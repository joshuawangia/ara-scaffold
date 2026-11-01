"""V2 authority is limited to native authenticated catalogue definitions."""
from copy import deepcopy
import json
import pytest
from ara.bank import load_bank
from ara.runtime.cache import canonical,digest
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.search_alignment import catalogue_inputs
from ara.runtime.validation import LinearValidator
from test_extraction import rig,ROOT
from test_predicate_v2 import setup,V2
from test_shared_predicates import CATALOGUE


def test_catalogue_relation_gloss_survives_native_frozen_readers(rig,monkeypatch):
    def damage(kind,data,inputs):
        if kind=='predicate_catalogue':data['predicates'][0]['gloss']='a asserts P'
    calls,t,rows,seen=setup(rig,monkeypatch,damage)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    meta=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']
    assert meta['consolidation']['after']['admitted']==3
    from ara.runtime.export import methodology
    assert 'shared_predicates' in methodology(calls.log.path)
    from ara.types import RunEvent
    event=next(e for e in calls.log.read() if e['label']=='MODEL' and e['stage']=='predicate_coverage')
    calls.log.emit(RunEvent.from_dict(event))
    with pytest.raises(ValueError,match='duplicate predicate model receipt'):methodology(calls.log.path)


def test_shape_correction_preserves_valid_entries_and_authenticates_history(rig,monkeypatch):
    def damage(kind,data,inputs):
        if kind=='predicate_catalogue' and 'validation_feedback' not in inputs:data['extra']='Q'
        elif kind=='predicate_catalogue':
            assert inputs['validation_feedback']['preserve_catalogue']==CATALOGUE
    calls,t,rows,seen=setup(rig,monkeypatch,damage);calls.config['validation_attempts']=2
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    receipt=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    from ara.runtime.predicate_receipts import verify_model_receipts
    from ara.runtime.providers import Response
    from test_extraction import response
    events=deepcopy(calls.log.read())
    rejected=next(e for e in events if e['label']=='MODEL' and e['stage']=='predicate_catalogue' and json.loads(e['payload_json'])['status']=='rejected')
    raw=json.loads(Response(json.loads(rejected['response'])).text())
    raw['predicates'][0]['gloss']='G(x)'
    rejected['response']=canonical(response(raw))
    with pytest.raises(ValueError,match='preserve valid entries'):verify_model_receipts(events,receipt)


def test_coverage_reference_and_cardinality_are_runtime_gates():
    from ara.runtime.predicate_coverage import coverage
    from ara.runtime.shared_predicates import catalogue
    entries=catalogue(CATALOGUE,version=V2)
    good=dict(coverage=[dict(covered=True,handles=['p0'],missing=[],reason='P')])
    with pytest.raises(ValueError,match='slot count'):coverage(good,entries,2)
    bad=deepcopy(good);bad['coverage'][0]['missing']=['G(x)']
    with pytest.raises(ValueError,match='inconsistent missing'):coverage(bad,entries,1)
    bad=deepcopy(good);bad['coverage'][0]['handles']=['p1']
    with pytest.raises(ValueError,match='unknown or duplicate'):coverage(bad,entries,1)


def test_published_handles_cannot_reorder():
    from ara.runtime.predicate_coverage import check_extension
    old=deepcopy(CATALOGUE)
    old['predicates'].append(dict(gloss='G(x)',roles=[dict(role='x',sort='a')],sharing_rationale='Q',distinctions='P'))
    reordered=deepcopy(old);reordered['predicates'].reverse()
    with pytest.raises(ValueError,match='published order'):check_extension(reordered,old)


def test_preflight_binds_effective_mandatory_grammar(rig):
    from ara.runtime.codex_preflight import manifest
    from ara.runtime.codex_schema import strict_schema
    calls=rig[0];calls.config.update(provider='codex_cli',construction_shared_predicates=True,shared_predicates_version=V2)
    cases=manifest(calls.config,ROOT)['cases']
    for case in cases:
        if case['kind'] not in ('predicate_formalize','predicate_coverage'):continue
        schema=calls.response_schema(case['kind'],case['inputs'])
        assert case['native_schema_hash']==digest(canonical(schema))
        assert case['wire_schema_hash']==digest(canonical(strict_schema(schema)))
        if case['kind']=='predicate_formalize':
            assert not LinearValidator(schema).is_valid(dict(mode='retain',formula=None,reason='P'))
        else:assert schema['properties']['coverage']['minItems']==schema['properties']['coverage']['maxItems']==1


def test_semantic_candidate_guard_refuses_legacy_retain():
    from ara.runtime.shared_predicates import candidate,catalogue
    with pytest.raises(ValueError,match='structured proposal mandatory'):
        candidate(dict(mode='retain',formula=None,reason='P'),catalogue(CATALOGUE),version=V2)
