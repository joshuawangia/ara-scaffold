"""Full extraction and construction lineage for inherited placeholder evidence."""
import json

import pytest

from test_extraction import rig, offline, register, response, ROOT
from rich_fixture import graph, batch_response
from ara.bank import load_bank
from ara.runtime.cache import Cache
from ara.runtime.calls import ModelCalls
from ara.runtime.extraction import extract, import_provenance, literature_provenance
from ara.runtime.frozen import load_frozen, import_frozen, campaign_totals
from ara.runtime.logging import EventLog
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.providers import Response
from ara.runtime.export import methodology


@pytest.fixture
def rich_builder(rig, tmp_path, monkeypatch, request):
    extraction, provider, papers, *_ = rig
    mode = getattr(request, 'param', 'plain')
    if mode == 'corrected':
        extraction.config['construction_targeted_corrections'] = 1
    register(extraction, provider, papers[0], graph())
    literature = extract(extraction, (papers[0],))
    directory = tmp_path / 'builder'
    log = EventLog(directory / 'events.jsonl')
    import_provenance(log, literature_provenance(literature, literature.read_text()))
    bank = load_bank(ROOT / 'bank')
    log.record('run_started', config=extraction.config, topic='P Q', literature=literature.read_text(),
               bank_version=bank.bank_version)
    calls = ModelCalls(extraction.config, provider, log, Cache(tmp_path / 'builder-cache'), ROOT, 'P Q')
    def complete(kind, prompt, schema, maximum):
        assert kind in ('select_t_roots', 'build_t_batch')
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        value = batch_response(inputs)
        if kind == 'build_t_batch':
            if mode == 'corrected':
                if inputs.get('mode') == 'targeted_correction':
                    value = dict(commitments=[], new_symbols=value['new_symbols'], alignments=[])
                else:
                    for symbol in value['new_symbols']:
                        symbol['definition'] = ''
            if mode in ('encoded', 'corrected'):
                for c in value['commitments']:
                    c['formula'] = json.dumps(c['formula'])
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    prepare_commitments(calls, bank, literature.read_text(), 'P')
    log.record('run_finished', state='complete')
    return directory, calls, extraction.log.path


def test_full_rich_history_and_campaign(rich_builder, tmp_path):
    directory, calls, extraction_log = rich_builder
    history = load_frozen(directory, 'P Q', calls.config, load_bank(ROOT / 'bank').bank_version, ROOT)
    log = EventLog(tmp_path / 'candidate/events.jsonl')
    import_frozen(log, history)
    inherited = [r['event'] for r in history['records']]
    assert any(e['label'] == 'MODEL' and e['stage'] == 'extract_paper' for e in inherited)
    assert any(e['label'] == 'MODEL' and e['stage'] == 'build_t_batch' for e in inherited)
    assert len(history['artifacts']) == 2
    summary = json.loads(methodology(log.path).split('```json\n')[1].split('\n```')[0])
    assert summary['inherited_totals']['cost_usd'] > 0
    assert summary['cost_usd'] == summary['local_totals']['cost_usd'] == 0
    inherited_cost = summary['inherited_totals']['cost_usd']
    assert campaign_totals([extraction_log, calls.log.path, log.path])['cost_usd'] == inherited_cost
    assert campaign_totals([log.path])['cost_usd'] == inherited_cost


@pytest.mark.parametrize('case', ['batch', 'plan', 'extraction'])
def test_broken_rich_provenance(rich_builder, case):
    directory, calls, _ = rich_builder
    if case == 'batch':
        path = next(directory.glob('build-t-*-0.json'))
        path.write_text('{}')
    elif case == 'plan':
        path = next(directory.glob('build-t-plan-*.json'))
        path.write_text('{}')
    else:
        # Valid outer hash chain but altered inner import digest.
        from ara.types import RunEvent
        events = calls.log.read()
        calls.log.path.unlink()
        calls.log.anchor.unlink()
        for e in events:
            if e['stage'] == 'extraction_provenance_import':
                payload = json.loads(e['payload_json'])
                payload['receipt_id'] = 'P'
                e['payload_json'] = json.dumps(payload)
            calls.log.emit(RunEvent.from_dict(e))
    with pytest.raises(ValueError, match='broken'):
        load_frozen(directory, 'P Q', calls.config, load_bank(ROOT / 'bank').bank_version, ROOT)


def test_rich_model_response_disagrees_with_artifact(rich_builder):
    from ara.types import RunEvent
    directory, calls, _ = rich_builder
    events = calls.log.read()
    calls.log.path.unlink()
    calls.log.anchor.unlink()
    for e in events:
        if e['label'] == 'MODEL' and e['stage'] == 'build_t_batch':
            raw = json.loads(e['response'])
            data = json.loads(raw['content'][0]['text'])
            data['commitments'][0]['formula'] = {'op': 'atom', 'name': 'S'}
            raw['content'][0]['text'] = json.dumps(data)
            e['response'] = json.dumps(raw)
        calls.log.emit(RunEvent.from_dict(e))
    with pytest.raises(ValueError, match='construction response does not match batch'):
        load_frozen(directory, 'P Q', calls.config, load_bank(ROOT / 'bank').bank_version, ROOT)


@pytest.mark.parametrize('rich_builder', ['encoded', 'corrected'], indirect=True)
def test_rich_encoded_and_corrected_receipts(rich_builder):
    directory, calls, _ = rich_builder
    history = load_frozen(directory, 'P Q', calls.config, load_bank(ROOT / 'bank').bank_version, ROOT)
    assert history['commitments']['commitments']


@pytest.mark.parametrize('rich_builder', ['corrected'], indirect=True)
def test_rich_correction_origin_disagreement(rich_builder):
    from ara.types import RunEvent
    directory, calls, _ = rich_builder
    events = calls.log.read()
    calls.log.path.unlink()
    calls.log.anchor.unlink()
    for e in events:
        if e['label'] == 'MODEL' and e['stage'] == 'build_t_batch' and json.loads(e['payload_json'])['status'] == 'rejected':
            raw = json.loads(e['response'])
            data = json.loads(raw['content'][0]['text'])
            data['commitments'][0]['formula'] = {'op': 'atom', 'name': 'S'}
            raw['content'][0]['text'] = json.dumps(data)
            e['response'] = json.dumps(raw)
        calls.log.emit(RunEvent.from_dict(e))
    with pytest.raises(ValueError, match='construction correction candidate mismatch'):
        load_frozen(directory, 'P Q', calls.config, load_bank(ROOT / 'bank').bank_version, ROOT)
