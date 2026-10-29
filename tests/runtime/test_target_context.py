"""Target projection keeps complete frozen formulas and authoritative gates."""
import json
import pytest
from ara.bank import load_bank
from ara.runtime.cache import canonical
from ara.runtime.budget import BudgetStop
from ara.runtime.target_policy import target_context
from ara.types import Commitment, CommitmentSet, Formula, Proposition, TokenUsage
from test_cross_paper import frozen_metadata
from test_search_alignment import P, Q, R, ROOT, rig, own_thesis
from test_search_failures import payloads


def setup(tmp_path, reply=None):
    calls, requests = rig(tmp_path, reply or (lambda kind, data: {'targets': []}))
    t = CommitmentSet(tuple(Commitment('t'+str(i), f.name or 'P Q', 'a:1', f)
        for i, f in enumerate((P, Formula('implies', (P,Q)), Q, R))))
    artifact, provenance = frozen_metadata(t, ('a','b','c','d'))
    (tmp_path/'frozen-t.json').write_text(canonical(artifact))
    (tmp_path/'commitment-provenance.json').write_text(canonical(provenance))
    inputs = dict(commitments=t.to_dict(), **calls.search_vocabulary(t),
                  **target_context(t, load_bank(ROOT/'bank')),
                  resolution_gap=dict(id='g', commitment_ids=['t0'], support_groups=[['t2']]),
                  count=1, named_position=None)
    return calls, requests, t, inputs


def test_projection_preserves_inventory_formulas_roles_and_exact_full_evidence(tmp_path):
    from ara.runtime.search_context import target_slice
    calls, _, t, inputs = setup(tmp_path)
    before = canonical(inputs)
    data = target_slice(inputs, 1)
    assert data['commitments']['commitments'] == [c.to_dict() for c in t.commitments[:3]]
    assert [r['id'] for r in data['compact_commitments']] == ['t3']
    assert data['compact_commitments'][0] == dict(id='t3', formula=R.to_dict(), stance='endorsed',
        citation=dict(source_id='d', page_start=1, page_end=1))
    assert data['commitment_roles'] == {k:v for k,v in inputs['commitment_provenance']['commitments'].items() if k!='t3'}
    assert 'commitment_provenance' not in data
    assert canonical(inputs) == before
    assert data['resolution_gap'] == inputs['resolution_gap']
    assert {r['name'] for r in data['symbol_catalogue']} == {'P','Q','R'}
    assert data['target_slice']['omitted_commitment_ids'] == []
    assert target_slice(inputs, 0)['target_slice']['full_ids'] == ['t0','t2']


def test_required_target_pack_refuses_without_truncation_or_dispatch(tmp_path, monkeypatch):
    calls, requests, _, inputs = setup(tmp_path)
    def estimate(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        size = 200001 if len(data['commitments']['commitments']) >= 3 else 100
        return TokenUsage(input_tokens=size)
    monkeypatch.setattr(calls.provider, 'estimate', estimate)
    with pytest.raises(BudgetStop, match='no truncation'):
        calls.call('propose_targets', inputs)
    assert not requests
    receipts = payloads(calls.log, 'target_context_slice')
    assert len(receipts) == 1
    assert receipts[0]['decision'] == 'refused'
    assert receipts[0]['full_ids'] == ['t0','t1','t2']
    assert receipts[0]['field_bytes']['resolution_gap'] == len(canonical(inputs['resolution_gap']).encode())


def test_compacted_commitment_remains_visible_to_native_novelty_and_classifier(tmp_path, monkeypatch):
    def reply(kind, data):
        if kind == 'classify_target':
            assert len(data['frozen_content']) == 4
            return dict(novelty='new_assertion', fidelity='matches', classification='own_thesis', reason='P')
        assert [r['id'] for r in data['compact_commitments']] == ['t0','t1','t2','t3']
        return {'targets':[Proposition('r','R',R).to_dict()]}
    calls, requests, t, _ = setup(tmp_path, reply)
    monkeypatch.setattr('ara.runtime.synthesis.proposal_forward_candidates', lambda *args: [])
    assert calls._propose_target_pool(t,1) == ()
    assert len([d for k,d in requests if k=='classify_target']) == 1  # identical full-input classification is cached
    assert len(payloads(calls.log, 'target_context_slice')) == 3
    rejected = payloads(calls.log, 'target_contribution_preflight')
    assert rejected and all(r['status'] != 'candidate' for r in rejected)


def recorded_source(tmp_path):
    calls, _, t, inputs = setup(tmp_path)
    bank = load_bank(ROOT/'bank')
    calls.log.record('run_started', config=calls.config, topic='P', bank_version=bank.bank_version)
    artifact = json.loads((tmp_path/'frozen-t.json').read_text())
    provenance = json.loads((tmp_path/'commitment-provenance.json').read_text())
    calls.log.record('symbol_catalogue_frozen', **artifact['symbol_catalogue'])
    calls.log.record('commitment_provenance_frozen', **provenance)
    calls.log.record('commitments_frozen', commitments=t.to_dict(), bank_version=bank.bank_version)
    (tmp_path/'commitments.json').write_text(t.to_json())
    calls.count_request('propose_targets', inputs, admission=True)
    return calls, inputs


def test_free_recorded_plan_matches_native_pack_and_leaves_source_unchanged(tmp_path):
    from ara.runtime.planning import plan_recorded_target
    from ara.runtime.search_context import target_slice
    from ara.runtime.cache import digest
    source, output = tmp_path/'source', tmp_path/'output'
    calls, inputs = recorded_source(source)
    before = {p.name:digest(p.read_text()) for p in source.iterdir() if p.is_file()}
    report = plan_recorded_target(source, output, ROOT, gap_id='g', bound=300000, counter='local')
    assert report['generation_calls'] == 0
    assert report['bounds']['recorded'] == 200000
    assert report['bounds']['configured'] == 300000
    assert report['decision'] == 'fits'
    packed = json.loads((output/'target-request.json').read_text())
    assert packed == target_slice(inputs,1)
    assert report['inputs_sha256'] == digest(canonical(packed))
    assert before == {p.name:digest(p.read_text()) for p in source.iterdir() if p.is_file()}


def test_plan_refuses_artifact_without_matching_receipt(tmp_path):
    from ara.runtime.planning import plan_recorded_target
    source = tmp_path/'source'
    calls, _ = recorded_source(source)
    calls.log.record('commitments_frozen', commitments={'commitments':[]}, bank_version='1')
    with pytest.raises(ValueError, match='one freeze'):
        plan_recorded_target(source, tmp_path/'output', ROOT, counter='local')


def test_alignment_bridge_requires_all_evidence_even_at_zero_hops():
    from ara.runtime.search_context import target_slice
    from ara.runtime.symbol_alignment import apply_judgments
    from test_symbol_alignment import fixture, judgment
    t, catalogue, roles = fixture()
    t, catalogue, roles, mapping = apply_judgments(t,catalogue,roles,[judgment(relation='entails_left_right')])
    bridge = t.commitments[-1]
    data = target_slice(dict(commitments=t.to_dict(), symbol_catalogue=catalogue,
        commitment_provenance=dict(commitments=roles),
        resolution_gap=dict(commitment_ids=[bridge.id], support_groups=[])),0)
    assert set(data['target_slice']['full_ids']) == {bridge.id,'P','Q'}
    assert data['commitment_roles'][bridge.id] == roles[bridge.id]
    assert [r['id'] for r in data['compact_commitments']] == ['R']


def test_legacy_stance_is_unavailable_and_formulas_are_never_shortened(tmp_path):
    from ara.runtime.search_context import target_slice
    calls, _, t, inputs = setup(tmp_path)
    inputs.update(commitment_provenance=None, resolution_gap=None)
    data = target_slice(inputs,1)
    assert all(c['stance']=='unavailable_legacy' for c in data['compact_commitments'])
    assert [c['formula'] for c in data['compact_commitments']] == [c.formula.to_dict() for c in t.commitments]
    assert data['compact_commitments'][0]['citation'] == {'legacy_citation':'a:1'}


def test_validation_feedback_repacked_and_counted_without_shrinking_scope(tmp_path, monkeypatch):
    from ara.runtime.providers import Response
    from test_search_alignment import raw
    calls, _, _, inputs = setup(tmp_path)
    seen = []
    def complete(kind, prompt, *args):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1]);seen.append(data)
        return Response(raw({'targets': [Proposition('r','R',R).to_dict()]} if len(seen)>1 else {'bad':'P'}))
    monkeypatch.setattr(calls.provider,'complete',complete)
    calls.call('propose_targets',inputs)
    receipts=payloads(calls.log,'target_context_slice')
    assert len(receipts)==2
    assert receipts[0]['full_ids']==receipts[1]['full_ids']==['t0','t1','t2']
    assert receipts[0]['inputs_sha256']!=receipts[1]['inputs_sha256']
    assert receipts[1]['input_tokens']>receipts[0]['input_tokens']
