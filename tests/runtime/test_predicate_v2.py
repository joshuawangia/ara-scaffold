"""Mandatory proposals and complete, preserved catalogue coverage; placeholders only."""
from copy import deepcopy
import json
import pytest
from ara.bank import load_bank
from ara.runtime.cache import canonical,digest
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.search_alignment import catalogue_inputs
from ara.runtime.validation import LinearValidator
from test_extraction import rig,ROOT
from test_shared_predicates import install,CATALOGUE,formula

V2='shared-predicate-formalization-v2'

def setup(rig,monkeypatch,damage=None):
    calls,t,rows,seen=install(rig,monkeypatch,damage)
    calls.config['shared_predicates_version']=V2
    return calls,t,rows,seen


def test_mandatory_local_and_wire_schema(rig):
    from ara.runtime.codex_schema import strict_schema
    calls=rig[0]
    schema=calls.response_schema('predicate_formalize',dict(policy_version=V2,catalogue=[]))
    for s in (schema,strict_schema(schema)):
        assert not LinearValidator(s).is_valid(dict(mode='retain',formula=None,reason='P'))
    assert LinearValidator(schema).is_valid(dict(mode='decompose',formula=formula(),reason='P'))


def test_catalogue_gloss_relation_verbs_allowed_exact_frames_refused():
    from ara.runtime.shared_predicates import catalogue
    data=deepcopy(CATALOGUE);data['predicates'][0]['gloss']='a asserts P'
    assert catalogue(data,version=V2)
    for gloss in ('b argues that P','B holds <em>that</em> P','b ![h**olds**](https://example.invalid/p.png) that P'):
        data['predicates'][0]['gloss']=gloss
        with pytest.raises(ValueError,match='report frame|formatting'):catalogue(data,version=V2)


def test_v2_native_coverage_then_proposals_and_all_judges(rig,monkeypatch):
    calls,t,rows,seen=setup(rig,monkeypatch)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    receipt=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    assert receipt['schema_version']==V2
    kinds=[k for k,_,_ in seen]
    assert kinds.index('predicate_coverage')<kinds.index('predicate_formalize')
    assert receipt['after']['proposed']==3 and receipt['after']['judged']==3
    assert receipt['after']['faithful_fraction']==1
    from ara.runtime.predicate_receipts import verify_model_receipts
    events=[e for e in calls.log.read() if e['stage']!='predicate_coverage']
    with pytest.raises(ValueError,match='missing authenticated'):verify_model_receipts(events,receipt)


def test_v2_retain_exhaustion_refuses_freeze(rig,monkeypatch):
    def damage(kind,data,inputs):
        if kind=='predicate_formalize':data.update(mode='retain',formula=None)
    calls,t,rows,seen=setup(rig,monkeypatch,damage)
    with pytest.raises(ValueError):prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert not (calls.log.path.parent/'commitments.json').exists()


def test_coverage_cannot_drop_slots_or_claim_missing_is_covered(rig,monkeypatch):
    def damage(kind,data,inputs):
        if kind=='predicate_coverage':data['coverage']=data['coverage'][:-1]
    calls,t,rows,seen=setup(rig,monkeypatch,damage)
    with pytest.raises(ValueError):prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert not any(k=='predicate_formalize' for k,_,_ in seen)


def test_patch_preserves_entries_and_coverage_replay(rig,monkeypatch):
    def damage(kind,data,inputs):
        if kind=='predicate_coverage' and len(inputs['catalogue'])==2:
            data['coverage'][0].update(covered=False,missing=['G(x)'])
        if kind=='predicate_catalogue' and inputs.get('mode')=='coverage_patch':
            data['predicates'].append(dict(gloss='G(x)',roles=[dict(role='x',sort='a')],sharing_rationale='P Q',distinctions='S'))
    calls,t,rows,seen=setup(rig,monkeypatch,damage)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    receipt=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    assert len(receipt['catalogue_history'])==2 and len(receipt['coverage_history'])==2
    assert receipt['catalogue_response']['predicates'][0]==CATALOGUE['predicates'][0]
    from ara.runtime.shared_predicates import validate_receipt
    receipt['coverage_history'][-1]['coverage'][0]['covered']=False
    receipt['sha256']=digest(canonical({k:v for k,v in receipt.items() if k!='sha256'}))
    with pytest.raises(ValueError,match='coverage'):validate_receipt(receipt,final,receipt['symbols'],rows)


def test_catalogue_correction_preserves_valid_rejected_entries(rig,monkeypatch):
    def damage(kind,data,inputs):
        if kind!='predicate_catalogue':return
        if 'validation_feedback' not in inputs:
            data['predicates'].append(dict(gloss='b argues that Q',roles=[dict(role='x',sort='a')],sharing_rationale='Q',distinctions='Q'))
        else:
            data['predicates'][0]['gloss']='G(x)'
    calls,t,rows,seen=setup(rig,monkeypatch,damage);calls.config['validation_attempts']=2
    with pytest.raises(ValueError,match='preserv'):prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert not any(k=='predicate_formalize' for k,_,_ in seen)


def test_v2_adverse_judgment_is_measured_retention(rig,monkeypatch):
    def damage(kind,data,inputs):
        if kind=='predicate_fidelity' and inputs['sample_index']==2:data['no_additions']=False
    calls,t,rows,seen=setup(rig,monkeypatch,damage)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    r=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    assert final==t and r['after']['proposed']==r['after']['judged']==3
    assert r['after']['faithful_fraction']==0
