"""Bounded native leaf requests and local context failures; placeholder-only."""
import json

import pytest

from ara.bank import load_bank
from ara.runtime.cache import canonical
from ara.runtime.orchestration import NativeEngine, search_all
from ara.types import Commitment, CommitmentSet, Proposition, TokenUsage
from test_cross_paper import frozen_metadata
from test_search_alignment import P, Q, ROOT, rig
from test_search_failures import setup as failure_setup, payloads


def context_rig(directory):
    calls, requests = rig(directory, lambda kind, inputs:
                          {'t_id': 'open'} if kind == 'map_leaf' else {'proposals': []})
    t = CommitmentSet(tuple(Commitment(f't{i:02}', f.name, f'{i}:1', f)
                            for i, f in enumerate((P,) * 6 + (Q,) * 6)))
    artifact, provenance = frozen_metadata(t, tuple(str(i) for i in range(12)))
    (directory/'frozen-t.json').write_text(canonical(artifact))
    (directory/'commitment-provenance.json').write_text(canonical(provenance))
    return calls, requests, t, Proposition('p', 'P', P)


def invoke(calls, kind, goal, t):
    if kind == 'map_leaf':
        return calls.map_leaf(goal, t)
    return calls.propose_cuts(goal, t, load_bank(ROOT/'bank').entries)


@pytest.mark.parametrize('kind', ['map_leaf', 'propose_cuts'])
def test_leaf_context_selects_ranked_bridges_and_referenced_catalogue(tmp_path, kind):
    calls, requests, t, goal = context_rig(tmp_path)
    full = calls.search_vocabulary(t)
    assert len(full['candidate_bridges']) > 8
    invoke(calls, kind, goal, t)
    data = requests[-1][1]
    bridges = data['candidate_bridges']
    assert len(bridges) == 8
    assert all(all(t.get(tid).formula == P for tid in b['commitment_ids']) for b in bridges)
    assert data['search_slice']['bridge_limit'] == 8
    assert 'commitment_provenance' not in data
    assert data['provenance_sha256'] == full['provenance_sha256']
    assert all('source_text' not in row for row in data['commitment_roles'].values())
    assert set(data['commitment_roles']) == {c['id'] for c in data['commitments']['commitments']}
    assert {s['name'] for s in data['symbol_catalogue']} == {
        c['formula']['name'] for c in data['commitments']['commitments']} | {'P'}
    assert all('source' not in entry for entry in data.get('bank', []))
    assert next(s for s in data['scheme_signatures'] if s['bank_id'] == 'sign')['critical_questions']
    slices = payloads(calls.log, 'search_context_slice')
    assert slices[-1]['decision'] == 'fits' and slices[-1]['bridge_limit'] == 8


@pytest.mark.parametrize('kind', ['map_leaf', 'propose_cuts'])
def test_leaf_context_recounts_and_shrinks_before_dispatch(tmp_path, monkeypatch, kind):
    calls, requests, t, goal = context_rig(tmp_path)
    calls.config['model_context_token_bound'] = calls.config['max_output_tokens'] + 2500
    def count(stage, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        return TokenUsage(input_tokens=100 + 1000 * data.get('search_slice', {}).get('bridge_limit', 100),
                          output_tokens=maximum)
    monkeypatch.setattr(calls.provider, 'estimate', count)
    invoke(calls, kind, goal, t)
    data = requests[-1][1]
    assert data['search_slice']['bridge_limit'] == 2
    assert len(data['candidate_bridges']) == 2
    assert len(data['commitments']['commitments']) <= 10
    assert {s['name'] for s in data['symbol_catalogue']} == {'P'}
    assert len(requests) == 1
    assert [p['bridge_limit'] for p in payloads(calls.log, 'search_context_slice')] == [8, 4, 2]
    assert not any(e['label'] == 'STOP' for e in calls.log.read())


@pytest.mark.parametrize('kind', ['map_leaf', 'propose_cuts'])
def test_context_refusal_is_job_local_and_preserves_other_searches(tmp_path, monkeypatch, kind):
    from ara.bank import Bank
    calls, provider, log, targets = failure_setup(tmp_path, {}, concurrency=1)
    estimate = provider.estimate
    def oversized(stage, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        goal = data.get('goal') or data.get('leaf')
        if stage == kind and goal and goal['formula'] == P.negated().to_dict():
            return TokenUsage(input_tokens=calls.config['model_context_token_bound'] + 1,
                              output_tokens=maximum)
        return estimate(stage, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'estimate', oversized)
    routes = search_all(calls, NativeEngine(Bank('1', ()), calls), CommitmentSet(()), targets)
    assert len(routes) == 5
    phase = payloads(log, 'search_phase_finished')[-1]
    assert phase['status'] == 'partial'
    assert [j['status'] for j in phase['jobs']] == ['completed', 'failed'] + ['completed'] * 4
    assert calls.budget._halted is None
    stops = [json.loads(e['payload_json']) for e in log.read() if e['label'] == 'STOP']
    assert stops and all(s['scope'] == 'search' for s in stops)
    assert any(p['bridge_limit'] == 0 and p['decision'] == 'refused'
               for p in payloads(log, 'search_context_slice'))


@pytest.mark.parametrize('kind', ['formalise', 'formalise_slots', 'answer_cq', 'tier1_repair'])
def test_other_search_context_refusals_do_not_halt_shared_budget(tmp_path, monkeypatch, kind):
    from ara.runtime.budget import BudgetStop
    from ara.runtime.search_jobs import job_failure
    calls, _, _, _ = context_rig(tmp_path)
    monkeypatch.setattr(calls.provider, 'estimate', lambda *args: TokenUsage(input_tokens=200001))
    with pytest.raises(BudgetStop) as caught:
        calls.count_request(kind, {'commitments_sha256': 'frozen'}, admission=True)
    assert caught.value.scope == 'search' and job_failure(caught.value)
    assert calls.budget._halted is None


def test_mapping_validation_feedback_is_recounted_and_shrunk(tmp_path, monkeypatch):
    from ara.runtime.providers import Response
    from test_search_alignment import raw
    calls, _, t, goal = context_rig(tmp_path)
    calls.config['model_context_token_bound'] = 20000
    seen = []
    def complete(kind, prompt, *args):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        seen.append(data)
        return Response(raw({'t_id': 'absent' if len(seen) == 1 else 'open'}))
    def estimate(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        return TokenUsage(input_tokens=500 + 1000 * data['search_slice']['bridge_limit']
                          + (10000 if 'validation_feedback' in data else 0), output_tokens=maximum)
    monkeypatch.setattr(calls.provider, 'complete', complete)
    monkeypatch.setattr(calls.provider, 'estimate', estimate)
    assert calls.map_leaf(goal, t) == 'open'
    assert [d['search_slice']['bridge_limit'] for d in seen] == [8, 1]
    assert seen[-1]['validation_feedback']
    assert [p['bridge_limit'] for p in payloads(calls.log, 'search_context_slice')] == [8, 8, 4, 2, 1]


@pytest.mark.parametrize('stance', ['reported', 'attacked'])
@pytest.mark.parametrize('force_zero', [False, True])
def test_all_exact_leaf_evidence_survives_bridges_and_shrinking(tmp_path, monkeypatch, stance, force_zero):
    from ara.runtime.commitment_provenance import make_commitment_provenance
    t = CommitmentSet((
        Commitment('a-restricted', 'P', 'a:1', P),
        Commitment('b-q', 'Q', 'b:1', Q),
        Commitment('c-q', 'Q', 'c:1', Q),
        Commitment('z-endorsed', 'P', 'z:1', P)))
    artifact, provenance = frozen_metadata(t, ('a', 'b', 'c', 'z'))
    rows = provenance['commitments']
    rows['a-restricted'].update(stance=stance, attribution=stance + '_view')
    provenance = make_commitment_provenance(t, artifact['symbol_catalogue'], rows)

    def reply(kind, inputs):
        if kind == 'map_leaf':
            return {'t_id': next((c['id'] for c in inputs['commitments']['commitments']
                if c['formula'] == inputs['leaf']['formula']
                and inputs['commitment_roles'][c['id']]['stance'] == 'endorsed'), 'open')}
        if kind == 'propose_cuts':
            return {'proposals': []}
        raise AssertionError(kind)

    calls, requests = rig(tmp_path, reply)
    calls.config['forward_pass_depth'] = 0
    (tmp_path/'frozen-t.json').write_text(canonical(artifact))
    (tmp_path/'commitment-provenance.json').write_text(canonical(provenance))
    if force_zero:
        calls.config['model_context_token_bound'] = 10000
        def count(kind, prompt, schema, maximum):
            inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
            return TokenUsage(input_tokens=20000 if inputs['search_slice']['bridge_limit'] else 100,
                              output_tokens=maximum)
        monkeypatch.setattr(calls.provider, 'estimate', count)

    route = NativeEngine(load_bank(ROOT/'bank'), calls)._engine(t).search(Proposition('p', 'P', P)).routes[0]
    assert route.status == 'CLOSED'
    assert route.nodes[0].t_id == 'z-endorsed'
    data = next(inputs for kind, inputs in requests if kind == 'map_leaf')
    exact_ids = ['z-endorsed', 'a-restricted']
    assert [c['id'] for c in data['commitments']['commitments']][:2] == exact_ids
    assert data['commitment_roles']['a-restricted']['stance'] == stance
    assert data['commitment_roles']['z-endorsed']['stance'] == 'endorsed'
    assert data['search_slice']['exact_match_commitment_ids'] == exact_ids
    slices = payloads(calls.log, 'search_context_slice')
    assert [s['bridge_limit'] for s in slices] == ([8, 4, 2, 1, 0] if force_zero else [8])
    assert all(s['exact_match_commitment_ids'] == exact_ids for s in slices)
    if force_zero:
        assert [c['id'] for c in data['commitments']['commitments']] == exact_ids
    else:
        assert data['candidate_bridges'] and all(
            set(b['commitment_ids']) == {'b-q', 'c-q'} for b in data['candidate_bridges'])
