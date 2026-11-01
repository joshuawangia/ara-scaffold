import json
from test_extraction import rig, ROOT
from test_shared_predicates import install
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.search_alignment import catalogue_inputs
from ara.bank import load_bank


def test_schema_retry_retains_valid_adverse_fidelity(rig,monkeypatch):
    def damage(kind,data,inputs):
        if kind=='predicate_fidelity' and inputs['sample_index']==0 and 'validation_feedback' not in inputs:
            data['equivalent']=False
            data.pop('reason')  # The adverse boolean is valid; only another field is missing.
    calls,original,rows,seen=install(rig,monkeypatch,damage)
    calls.config['validation_attempts']=2
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    events=calls.log.read()
    rejected=[e for e in events if e['stage']=='predicate_fidelity' and e['label']=='MODEL' and json.loads(e['payload_json']).get('status')!='accepted']
    assert len(rejected)==3
    assert all('false' in e['response'] for e in rejected)
    receipt=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    assert receipt['after']['admitted']==0, 'valid adverse fidelity was discarded by schema correction'
    assert final==original


def test_event_reader_authenticates_predicate_model_receipts(rig,monkeypatch):
    import pytest
    from ara.runtime.route_policy import provenance_from_events
    calls,original,rows,seen=install(rig,monkeypatch)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    events=calls.log.read()
    missing=[e for e in events if not (e['label']=='MODEL' and e['stage']=='predicate_fidelity')]
    assert len(missing)<len(events)
    with pytest.raises(ValueError,match='missing authenticated predicate model response'):
        provenance_from_events(missing,final)


def test_freeze_only_methodology_authenticates_predicate_history(rig,monkeypatch):
    import pytest
    from ara.runtime.export import methodology
    from ara.types import RunEvent
    calls,original,rows,seen=install(rig,monkeypatch)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    events=calls.log.read()
    assert not any(e['stage']=='route' for e in events)
    prior=next(e for e in events if e['label']=='MODEL' and e['stage']=='predicate_fidelity')
    calls.log.emit(RunEvent.from_dict(prior))
    # Authentic append-only log, but duplicate sample history is invalid.
    with pytest.raises(ValueError,match='duplicate predicate model receipt'):
        catalogue_inputs(calls.log.path.parent,final)
    with pytest.raises(ValueError,match='duplicate predicate model receipt'):
        methodology(calls.log.path)


def test_shape_only_fidelity_correction_still_admits(rig,monkeypatch):
    def damage(kind,data,inputs):
        if kind=='predicate_fidelity' and inputs['sample_index']==0 and 'validation_feedback' not in inputs:
            data.pop('reason')
    calls,original,rows,seen=install(rig,monkeypatch,damage)
    calls.config['validation_attempts']=2
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    receipt=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    assert receipt['after']['admitted']==3


def test_replay_rejects_valid_adverse_fields_in_shape_rejected_history(rig,monkeypatch):
    from copy import deepcopy
    import pytest
    from ara.runtime.cache import canonical
    from ara.runtime.providers import Response
    from ara.types import RunEvent
    from test_extraction import response
    calls,original,rows,seen=install(rig,monkeypatch)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    prior=deepcopy(next(e for e in calls.log.read() if e['label']=='MODEL' and e['stage']=='predicate_fidelity'))
    raw=json.loads(Response(json.loads(prior['response'])).text())
    raw['no_additions']=False;raw.pop('reason')
    prior['response']=canonical(response(raw))
    payload=json.loads(prior['payload_json']);payload['status']='rejected'
    prior['payload_json']=canonical(payload)
    calls.log.emit(RunEvent.from_dict(prior))
    with pytest.raises(ValueError,match='adverse fidelity history'):
        catalogue_inputs(calls.log.path.parent,final)
