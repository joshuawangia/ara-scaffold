"""Placeholder search regressions through the native runtime boundary."""
from fixture_support import api_fixture_config
from dataclasses import replace
import json
from pathlib import Path

import pytest
import yaml

from ara.bank import load_bank
from ara.engine.licensing import Licenser
from ara.runtime.cache import Cache, canonical
from ara.runtime.calls import ModelCalls, Rejected
from ara.runtime.logging import EventLog
from ara.runtime.orchestration import NativeEngine
from ara.runtime.providers import MockProvider, Response
from ara.types import Commitment, CommitmentSet, Formula, PremiseFill, Proposal, Proposition

ROOT = Path(__file__).resolve().parents[2]
P, Q, R = (Formula('atom', name=s) for s in ('P', 'Q', 'R'))
PQ = Formula('implies', (P, Q))
T = CommitmentSet((Commitment('t1', 'P', 'placeholder:1', P),
                   Commitment('t2', 'P -> Q', 'placeholder:2', PQ)))
GOAL = Proposition('q', 'Q', Q)


def raw(value):
    return {'model': 'claude-opus-5', 'stop_reason': 'end_turn',
            'content': [{'type': 'text', 'text': canonical(value)}],
            'usage': {'input_tokens': 5, 'output_tokens': 3}}


def cut(**updates):
    return {**dict(bank_id='modus_ponens', conclusion_text='Q', conclusion_ref='current_goal',
        premises=[dict(slot='conditional', text='P -> Q', t_id='t2', scope_id=None),
                  dict(slot='antecedent', text='P', t_id='t1', scope_id=None)]), **updates}


def own_thesis(reply):
    def respond(kind, inputs):
        if kind == 'classify_target':
            return dict(novelty='new_assertion',fidelity='matches',classification='own_thesis', reason='P')
        return reply(kind, inputs)
    return respond


def rig(tmp_path, reply):
    config = api_fixture_config()
    config.update(validation_attempts=2, search_concurrency=1)
    provider = MockProvider({})
    requests = []
    def complete(kind, prompt, *args):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        requests.append((kind, inputs))
        return Response(raw(reply(kind, inputs)))
    provider.complete = complete
    log = EventLog(tmp_path/'events.jsonl')
    from ara.runtime.frozen_catalogue import frozen_artifact
    artifact = frozen_artifact(T, [dict(name=n, kind='atom', arity=0, definition=n,
        evidence_ids=['t1', 't2'] if n == 'P' else ['t2']) for n in ('P', 'Q')])
    (tmp_path/'frozen-t.json').write_text(canonical(artifact))
    calls = ModelCalls(config, provider, log, Cache(tmp_path/'cache'), ROOT, 'P')
    return calls, requests


def test_current_goal_reference_prevents_reformalization(tmp_path):
    def reply(kind, inputs):
        if kind == 'map_leaf': return {'t_id': 'open'}
        if kind == 'propose_cuts': return {'proposals': [cut()]}
        if kind == 'formalise_slots':
            return {'slots': [{'slot': 'conditional', 'formula': PQ.to_dict()},
                              {'slot': 'antecedent', 'formula': P.to_dict()}]}
        if kind == 'formalise': return {'formula': R.to_dict()}
        pytest.fail(kind)
    calls, requests = rig(tmp_path, reply)
    result = NativeEngine(load_bank(ROOT/'bank'), calls)._engine(T).search(GOAL)
    assert result.routes[0].status == 'CLOSED'
    assert len(result.routes[0].nodes) == 3
    assert not any(kind == 'formalise' for kind, _ in requests)
    joint = [data for kind, data in requests if kind == 'formalise_slots']
    assert len(joint) == 1
    assert joint[0]['goal']['formula'] == Q.to_dict()
    assert {b['slot'] for b in joint[0]['slot_bindings']} == {'conditional', 'antecedent'}
    assert {s['name'] for s in joint[0]['symbol_catalogue']} == {'P', 'Q'}
    assert joint[0]['shared_metavariables'] == [dict(formulas={'Q': Q.to_dict(), 'P': P.to_dict()}, terms={})]
    assert joint[0]['catalogue_sha256']


def test_target_preflight_retains_new_vocabulary_with_catalogue(tmp_path):
    targets = []
    def reply(kind, inputs):
        assert kind == 'propose_targets'
        targets.append(inputs)
        return {'targets': [Proposition('q', 'Q', R if len(targets) == 1 else Q).to_dict()]}
    calls, requests = rig(tmp_path, own_thesis(reply))
    assert calls.propose_targets(T, 1)[0].formula == R
    assert len(targets) == 1
    assert targets[0]['catalogue_sha256']
    assert {s['name'] for s in targets[0]['symbol_catalogue']} == {'P', 'Q'}
    events = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'target_vocabulary_preflight']
    assert [e['status'] for e in events] == ['disconnected']
    assert all(e['attempt_budget'] == 3 for e in events)


def test_disconnected_vocabulary_is_explicit(tmp_path):
    calls, requests = rig(tmp_path, own_thesis(lambda *_: {'targets': [Proposition('r', 'R', R).to_dict()]}))
    assert calls.propose_targets(T, 1)[0].formula == R
    assert len(requests) == 2
    events = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'target_vocabulary_preflight']
    assert len(events) == 1 and events[-1]['status'] == 'disconnected'


def test_catalogue_identity_changes_cache_and_legacy_is_explicit(tmp_path):
    calls, requests = rig(tmp_path, own_thesis(lambda *_: {'targets': [Proposition('r','R',R).to_dict()]}))
    calls.propose_targets(T, 1)
    calls.propose_targets(T, 1)
    assert len(requests) == 2
    artifact = json.loads((tmp_path/'frozen-t.json').read_text())
    symbols = artifact['symbol_catalogue']['symbols']
    symbols[0]['definition'] = 'P P'
    from ara.runtime.frozen_catalogue import frozen_artifact
    (tmp_path/'frozen-t.json').write_text(canonical(frozen_artifact(T, symbols)))
    calls.propose_targets(T, 1)
    assert len(requests) == 4
    assert requests[0][1]['catalogue_sha256'] != requests[2][1]['catalogue_sha256']
    (tmp_path/'frozen-t.json').unlink()
    calls.propose_targets(T, 1)
    assert requests[-2][1]['symbol_catalogue'] is None
    assert requests[-2][1]['catalogue_status'] == 'unavailable_legacy'
    assert requests[-1][1]['definition_semantics'] == 'unavailable_legacy'
    assert requests[-1][1]['rendered_content']['definition'] == 'R'


def test_corrupt_catalogue_refused_without_dispatch(tmp_path):
    calls, requests = rig(tmp_path, lambda *_: pytest.fail('dispatch'))
    artifact = json.loads((tmp_path/'frozen-t.json').read_text())
    artifact['symbol_catalogue']['sha256'] = '0' * 64
    (tmp_path/'frozen-t.json').write_text(canonical(artifact))
    with pytest.raises(ValueError, match='hash'):
        calls.propose_targets(T, 1)
    assert not requests


@pytest.mark.parametrize('defect', ['id', 'text', 'goal'])
def test_proposal_reference_correction(tmp_path, defect):
    seen = []
    def reply(kind, inputs):
        if kind=='map_leaf': return {'t_id':'open'}
        if kind=='formalise_slots': return {'slots':[dict(slot=b['slot'],formula=b['formula']) for b in inputs['slot_bindings']]}
        assert kind == 'propose_cuts'
        seen.append(inputs)
        proposal = cut()
        if len(seen) == 1:
            if defect == 'id': proposal['premises'][0]['t_id'] = 'absent'
            if defect == 'text': proposal['premises'][0]['text'] = 'R'
            if defect == 'goal': proposal['conclusion_text'] = 'R'
        return {'proposals': [proposal]}
    calls, _ = rig(tmp_path, reply)
    route = NativeEngine(load_bank(ROOT/'bank'), calls)._engine(T).search(GOAL).routes[0]
    assert route.status=='CLOSED'
    proposals = [route.nodes[0].proposal]
    assert len(seen) == 2 and seen[1]['rejection_feedback']
    assert proposals[0].conclusion_ref == 'current_goal'
    assert proposals[0].premises[0].t_id == 't2'
    assert proposals[0].premises[0].text == 'P -> Q'


def test_joint_slots_cannot_change_frozen_binding(tmp_path):
    def reply(kind, inputs):
        assert kind == 'formalise_slots'
        return {'slots': [{'slot': 'conditional', 'formula': Formula('implies', (R, Q)).to_dict()},
                          {'slot': 'antecedent', 'formula': R.to_dict()}]}
    calls, _ = rig(tmp_path, reply)
    with pytest.raises(Rejected, match='frozen slot binding'):
        calls.formalise_slots(Proposal.from_dict(cut()), GOAL, load_bank(ROOT/'bank').get('modus_ponens'), T)


def test_explicit_goal_reference_does_not_override_changed_text(tmp_path):
    calls, requests = rig(tmp_path, lambda *_: pytest.fail('dispatch'))
    proposal = Proposal.from_dict(cut(conclusion_text='R'))
    license = Licenser(load_bank(ROOT/'bank'), calls, calls.log, commitments=T).check(proposal, GOAL)
    assert not license.licensed and license.decision.reason_code == 'CONCLUSION_REFERENCE_MISMATCH'
    assert not requests


def test_three_proposal_batch_keeps_valid_alternative(tmp_path):
    def reply(kind, inputs):
        if kind == 'map_leaf': return {'t_id': 'open'}
        if kind == 'propose_cuts':
            assert inputs['proposal_limit'] == 3 and inputs['attempt_budget'] == 2
            return {'proposals': [cut(bank_id='P'), cut(bank_id='Q'), cut()]}
        if kind == 'formalise_slots':
            return {'slots': [{'slot': 'conditional', 'formula': PQ.to_dict()},
                              {'slot': 'antecedent', 'formula': P.to_dict()}]}
        pytest.fail(kind)
    calls, requests = rig(tmp_path, reply)
    result = NativeEngine(load_bank(ROOT/'bank'), calls)._engine(T).search(GOAL)
    assert result.routes[0].status == 'CLOSED'
    assert sum(kind == 'propose_cuts' for kind, _ in requests) == 1
    assert sum((e['decision'] or {}).get('reason_code') == 'UNKNOWN_BANK_ID' for e in calls.log.read()) == 2


def test_native_lifecycle_closure_and_offline_joint_replay(tmp_path):
    from ara.runtime.orchestration import prepare, search_all
    from ara.runtime.search_resume import load_search_resume
    from ara.runtime.report_traces import collect_traces
    def reply(kind, inputs):
        if kind == 'classify_target': return dict(novelty='new_assertion',fidelity='matches',classification='own_thesis',reason='P')
        if kind == 'build_t': return T.to_dict()
        if kind == 'propose_targets': return {'targets': [Proposition('r','R',R).to_dict()]}
        if kind == 'map_leaf': return {'t_id': 'open'}
        if kind == 'propose_cuts':
            return {'proposals': [] if inputs['goal']['formula']['op'] == 'not' else [cut(bank_id='sign',conclusion_text='R',premises=[dict(slot='sign_relation',text='P -> Q',t_id='t2',scope_id=None),dict(slot='observed_sign',text='P',t_id='t1',scope_id=None)])]}
        if kind == 'formalise_slots':
            return {'slots': [{'slot': 'sign_relation', 'formula': PQ.to_dict()},
                              {'slot': 'observed_sign', 'formula': P.to_dict()}]}
        if kind=='answer_cq': return dict(cq_id=inputs['question']['id'],answer='P',answered=True,supporting_t_ids=['t1','t2'])
        pytest.fail(kind)
    calls, requests = rig(tmp_path, reply)
    calls.config.update(target_candidates=1, forward_pass_depth=0)
    bank = load_bank(ROOT/'bank')
    calls.log.record('run_started', config=calls.config, topic='P', audience='', literature='P',
                     bank_version=bank.bank_version)
    commitments, targets = prepare(calls, bank, 'P', '')
    routes = search_all(calls, NativeEngine(bank, calls), commitments, targets)
    assert [r.status for r in routes] == ['CLOSED', 'OPEN']
    closed = routes[0]
    assert {n.t_id for n in closed.nodes if n.kind == 'leaf'} == {'t1', 't2'}
    assert closed.nodes[0].proposal.conclusion_ref == 'current_goal'
    count = len(requests)
    state = load_search_resume(calls.log, bank, ROOT)
    assert len(requests) == count
    assert sorted(state.restored) == [0, 1]
    restored, licenses = state.restored[0]
    assert restored.routes == (closed,) and len(licenses) == 1
    assert licenses[0][1].premises[0].formula == PQ


def test_joint_open_slots_share_goal_vocabulary_and_still_require_entailment(tmp_path):
    cuts = cut()
    for premise in cuts['premises']:
        premise['t_id'] = 'open'
    wrong = False
    def reply(kind, inputs):
        assert kind == 'formalise_slots'
        assert len(inputs['slot_bindings']) == 2
        assert inputs['shared_metavariables'] == [dict(formulas={'Q': Q.to_dict()}, terms={})]
        return {'slots': [{'slot': 'conditional', 'formula': PQ.to_dict()},
                          {'slot': 'antecedent', 'formula': (R if wrong else P).to_dict()}]}
    calls, _ = rig(tmp_path, reply)
    checker = Licenser(load_bank(ROOT/'bank'), calls, calls.log, commitments=T)
    proposal = Proposal.from_dict(cuts)
    assert checker.check(proposal, GOAL).licensed
    # A different premise text creates a different joint request, not a cache replay.
    wrong = True
    proposal = replace(proposal, premises=(proposal.premises[0], replace(proposal.premises[1], text='R')))
    assert checker.check(proposal, GOAL).decision.reason_code == 'SOLVER_COUNTEREXAMPLE'


def test_proposal_batch_bound_is_enforced(tmp_path):
    calls, _ = rig(tmp_path, lambda *_: {'proposals': [cut(bank_id=n) for n in ('P', 'Q', 'R', 'S')]})
    with pytest.raises(Rejected, match='three candidates'):
        calls.propose_cuts(GOAL, T, load_bank(ROOT/'bank').entries)


def test_joint_slots_preserve_scoped_result_reference(tmp_path):
    entry = load_bank(ROOT/'bank').get('conditional_proof')
    scope = entry.formula_schema.scopes[0].id
    proposal = Proposal('conditional_proof', (PremiseFill('assumption', 'Q', 'open', scope),
        PremiseFill('result', 'P', 't1', scope)), 'Q -> P', 'current_goal')
    goal = Proposition('q', 'Q -> P', Formula('implies', (Q, P)))
    def reply(kind, inputs):
        assert kind == 'formalise_slots'
        return {'slots': [{'slot': 'assumption', 'formula': Q.to_dict()},
                          {'slot': 'result', 'formula': P.to_dict()}]}
    calls, _ = rig(tmp_path, reply)
    assert Licenser(load_bank(ROOT/'bank'), calls, calls.log, commitments=T).check(proposal, goal).licensed
