"""Search prompts project receipts without weakening native gate inputs."""
import json

import pytest

from ara.runtime.cache import canonical, digest
from ara.runtime.novelty import novelty_check
from ara.runtime.search_context import leaf_slice
from ara.types import Proposition, TokenUsage
from test_search_alignment import R, raw
from test_search_context import context_rig, invoke
from test_search_failures import payloads


@pytest.mark.parametrize('kind', ['map_leaf', 'propose_cuts'])
def test_native_search_packs_basis_traces_but_logs_full_evidence(tmp_path, kind):
    calls, requests, t, _ = context_rig(tmp_path)
    goal = Proposition('r', 'R', R)
    vocabulary = calls.search_vocabulary(t)
    full = novelty_check(R, t, vocabulary['commitment_provenance'])
    original = canonical(full)
    invoke(calls, kind, goal, t)
    data = requests[-1][1]
    packed = data['goal_novelty']
    assert 'checks' not in packed['consistent_basis']
    assert packed['checks'] == full['checks']
    assert packed['status'] == 'candidate'
    assert packed['essential_new_propositions'] == [R.to_dict()]
    table = packed['commitment_id_table']
    assert [table[i] for i in packed['consistent_basis']['selected_commitment_indices']] == full['consistent_basis']['selected_commitment_ids']
    assert all('checks' not in p for p in packed['paper_bases'].values())
    evidence = payloads(calls.log, 'search_context_evidence')
    assert len(evidence) == 1
    assert evidence[0]['goal_novelty'] == full
    assert evidence[0]['goal_novelty_sha256'] == digest(original)
    projection = data['search_slice']['evidence_projection']
    assert projection['goal_novelty_sha256'] == digest(original)
    assert canonical(novelty_check(R, t, vocabulary['commitment_provenance'])) == original
    assert payloads(calls.log, 'search_context_slice')[-1]['evidence_projection'] == projection


def alignment_inputs(tmp_path):
    calls, requests, t, goal = context_rig(tmp_path)
    data = dict(leaf=goal.to_dict(), commitments=t.to_dict(), **calls.search_vocabulary(t))
    # Receipt projection operates after native frozen validation; these isolated
    # rows exercise alias relevance and disclosure independent of model calls.
    data['alignment_disclosure'] = dict(status='accepted', refusal_reason=None,
        mapping={'F': 'P', 'G': 'Q'},
        judgments=[dict(left='F', right='P', relation='same_content', reason='P'),
                   dict(left='G', right='Q', relation='same_content', reason='Q')],
        unresolved=[dict(left='F', right='R', reason='P R'), dict(left='G',right='S',reason='Q S')],
        unresolved_count=2, note='Model alignment judgments are not source endorsements.')
    return calls, requests, t, data


def test_leaf_alignment_keeps_alias_related_rows_and_discloses_projection(tmp_path):
    _, _, _, inputs = alignment_inputs(tmp_path)
    original = canonical(inputs)
    data = leaf_slice(inputs, 0)
    disclosure = data['alignment_disclosure']
    full = inputs['alignment_disclosure']
    assert disclosure['judgments'] == full['judgments'][:1]
    assert disclosure['unresolved'] == full['unresolved'][:1]
    assert disclosure['mapping'] == {'F': 'P'}
    assert disclosure['unresolved_count'] == 1 and disclosure['full_unresolved_count'] == 2
    assert disclosure['full_judgment_count'] == 2
    assert disclosure['status'] == full['status'] and disclosure['note'] == full['note']
    assert data['search_slice']['evidence_projection']['alignment_disclosure_sha256'] == digest(canonical(full))
    assert canonical(inputs) == original
    expanded = leaf_slice(inputs, 60)['alignment_disclosure']
    assert expanded['judgments'] == full['judgments']
    assert expanded['unresolved'] == full['unresolved']


def test_retry_repacks_full_evidence_and_required_context_still_refuses(tmp_path, monkeypatch):
    from ara.runtime.budget import BudgetStop
    from ara.runtime.providers import Response
    calls, requests, t, inputs = alignment_inputs(tmp_path)
    inputs['goal_novelty'] = novelty_check(R, t, calls.search_vocabulary(t)['commitment_provenance'])
    inputs['leaf'] = Proposition('r', 'R', R).to_dict()
    before = canonical(inputs)
    seen = []
    calls.config['model_context_token_bound'] = 20000
    def estimate(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        assert 'checks' not in data['goal_novelty']['consistent_basis']
        return TokenUsage(input_tokens=500 + 1000 * data['search_slice']['bridge_limit']
                          + (10000 if 'validation_feedback' in data else 0), output_tokens=maximum)
    def complete(kind, prompt, *args):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1]); seen.append(data)
        return Response(raw({'t_id': 'absent' if len(seen) == 1 else 'open'}))
    monkeypatch.setattr(calls.provider, 'estimate', estimate)
    monkeypatch.setattr(calls.provider, 'complete', complete)
    def check(value):
        from ara.runtime.calls import require
        require(value['t_id'] == 'open', 'unknown T id')
        return value['t_id']
    assert calls.call('map_leaf', inputs, check) == 'open'
    assert [d['search_slice']['bridge_limit'] for d in seen] == [8, 1]
    evidence = payloads(calls.log, 'search_context_evidence')
    assert len(evidence) == 2
    assert all(e['goal_novelty'] == inputs['goal_novelty'] for e in evidence)
    assert all(e['alignment_disclosure'] == inputs['alignment_disclosure'] for e in evidence)
    assert canonical(inputs) == before
    monkeypatch.setattr(calls.provider, 'estimate', lambda *args: TokenUsage(input_tokens=20001))
    with pytest.raises(BudgetStop, match='no truncation') as caught:
        calls.call('map_leaf', inputs, check)
    assert caught.value.scope == 'search' and calls.budget._halted is None
    assert len(seen) == 2
    assert payloads(calls.log, 'search_context_slice')[-1]['decision'] == 'refused'


def test_projected_out_evidence_still_binds_cache_identity(tmp_path):
    calls, requests, t, inputs = alignment_inputs(tmp_path)
    inputs['goal_novelty'] = novelty_check(R, t, calls.search_vocabulary(t)['commitment_provenance'])
    inputs['leaf'] = Proposition('r', 'R', R).to_dict()
    calls.call('map_leaf', inputs)
    calls.call('map_leaf', inputs)
    assert len(requests) == 1
    inputs['goal_novelty']['consistent_basis']['checks'][0]['timeout_ms'] += 1
    calls.call('map_leaf', inputs)
    assert len(requests) == 2
    first, changed = (data for _, data in requests)
    assert first['goal_novelty']['status'] == changed['goal_novelty']['status']
    assert first['goal_novelty']['checks'] == changed['goal_novelty']['checks']
    assert first['search_slice']['evidence_projection']['goal_novelty_sha256'] != changed['search_slice']['evidence_projection']['goal_novelty_sha256']


@pytest.mark.parametrize('force_zero', [False, True])
def test_native_slot_formalization_projects_provenance_and_keeps_all_bindings(tmp_path, monkeypatch, force_zero):
    from ara.bank import load_bank
    from ara.types import Proposal
    from test_search_alignment import rig, T, GOAL, ROOT, cut
    from test_stance_search import provenance, reply
    calls, requests = rig(tmp_path, reply)
    full = provenance(tmp_path)
    if force_zero:
        calls.config['model_context_token_bound'] = 20000
        def estimate(kind, prompt, schema, maximum):
            data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
            return TokenUsage(input_tokens=20001 if data.get('search_slice',{}).get('bridge_limit',8) else 100,
                              output_tokens=maximum)
        monkeypatch.setattr(calls.provider, 'estimate', estimate)
    result = calls.formalise_slots(Proposal.from_dict(cut()), GOAL, load_bank(ROOT/'bank').get('modus_ponens'), T)
    assert {p.formula for p in result} == {c.formula for c in T.commitments}
    data = requests[-1][1]
    assert 'commitment_provenance' not in data
    assert data['provenance_sha256'] == full['sha256']
    assert {c['id'] for c in data['commitments']['commitments']} == {'t1','t2'}
    assert data['search_slice']['mandatory_binding_ids'] == ['t1','t2']
    assert {s['name'] for s in data['symbol_catalogue']} == {'P','Q'}
    if force_zero:
        assert data['search_slice']['bridge_limit'] == 0
    assert all(b['formula'] == T.get(b['t_id']).formula.to_dict() for b in data['slot_bindings'])


@pytest.mark.parametrize('force_zero',[False,True])
def test_open_slot_definition_is_mandatory(tmp_path,monkeypatch,force_zero):
    from ara.bank import load_bank
    from ara.types import Commitment, CommitmentSet, Formula, PremiseFill, Proposal
    from test_cross_paper import frozen_metadata
    from test_search_alignment import rig, ROOT, P, Q
    s=Formula('atom',name='S')
    t=CommitmentSet(tuple(Commitment(f't{i:02}','P','a:1',P) for i in range(20))+
        (Commitment('z','P -> R','a:1',Formula('implies',(P,s))),))
    artifact,metadata=frozen_metadata(t,('a',)*21,{'S':'R'})
    seen=[]
    def reply(kind,inputs):
        assert kind=='formalise_slots';seen.append(inputs)
        symbol=next((row['name'] for row in inputs['symbol_catalogue'] if row['definition']=='R'),'R')
        f=Formula('atom',name=symbol)
        return {'slots':[dict(slot='conditional',formula=Formula('implies',(f,Q)).to_dict()),dict(slot='antecedent',formula=f.to_dict())]}
    calls,_=rig(tmp_path,reply)
    (tmp_path/'frozen-t.json').write_text(canonical(artifact));(tmp_path/'commitment-provenance.json').write_text(canonical(metadata))
    if force_zero:
        calls.config['model_context_token_bound']=20000
        def estimate(kind,prompt,schema,maximum):
            inputs=json.loads(prompt.split('\nINPUT_JSON\n')[1])
            return TokenUsage(input_tokens=20001 if inputs.get('search_slice',{}).get('bridge_limit',0) else 100,output_tokens=maximum)
        monkeypatch.setattr(calls.provider,'estimate',estimate)
    proposal=Proposal('modus_ponens',(PremiseFill('conditional','R -> Q','open',None),PremiseFill('antecedent','R','open',None)),'Q','current_goal')
    actual=calls.formalise_slots(proposal,Proposition('q','Q',Q),load_bank(ROOT/'bank').get('modus_ponens'),t)
    assert any(row['name']=='S' and row['definition']=='R' for row in seen[-1]['symbol_catalogue'])
    assert actual[1].formula==s
