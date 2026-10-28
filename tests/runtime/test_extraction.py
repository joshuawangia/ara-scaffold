"""Offline PDF intake through the production CLI and model boundary; P/Q/R only."""
from fixture_support import api_fixture_config
import copy
from dataclasses import FrozenInstanceError
import json
from pathlib import Path
import socket

import pytest
from pypdf import PdfWriter
from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
import yaml

from ara.runtime.budget import BudgetStop
from ara.runtime.cache import Cache, canonical
from ara.runtime.calls import ModelCalls, Rejected
from ara.runtime.cli import main
from ara.runtime.export import methodology
from ara.runtime.extraction import (Paper, PageText, extract, load_papers, literature_provenance,
                                    import_provenance, HEADER)
from ara.runtime.logging import EventLog
from ara.runtime.providers import MockProvider, Response, mock_key

ROOT = Path(__file__).resolve().parents[2]
ITEM = {'id': 'p', 'source_id': 'p', 'kind': 'premise', 'attribution': 'author_claim', 'attributed_to': 'a', 'text': 'P P P',
        'page_start': 1, 'page_end': 1, 'premise_ids': [], 'conclusion_id': None, 'qualification_ids': [],
        'applies_to': [], 'inference_origin': None}
VALUE = {'schema_version': 2, 'source_id': 'p', 'coverage_complete': True, 'new_gaps': [], 'items': [ITEM]}


def pdf(path, texts=('P', 'Q')):
    writer = PdfWriter()
    for text in texts:
        page = writer.add_blank_page(width=300, height=300)
        font = DictionaryObject({NameObject('/Type'): NameObject('/Font'),
                                 NameObject('/Subtype'): NameObject('/Type1'),
                                 NameObject('/BaseFont'): NameObject('/Helvetica')})
        page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'): DictionaryObject({NameObject('/F1'): font})})
        stream = DecodedStreamObject()
        stream.set_data(f'BT /F1 12 Tf 30 100 Td ({text}) Tj ET'.encode())
        page[NameObject('/Contents')] = writer._add_object(stream)
    writer.write(path)


def response(value, usage=None):
    return {'model': 'claude-opus-5', 'stop_reason': 'end_turn',
            'content': [{'type': 'text', 'text': canonical(value)}],
            'usage': usage or {'input_tokens': 100, 'output_tokens': 50}}


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('network is forbidden')
    monkeypatch.setattr(socket.socket, 'connect', forbidden)


@pytest.fixture
def rig(tmp_path):
    config = api_fixture_config()
    config.update(provider='mock', validation_attempts=1, extraction_max_failed_papers=0, cache_dir=str(tmp_path / 'cache'), target_candidates=1)
    config_path = tmp_path / 'config.yaml'
    config_path.write_text(yaml.safe_dump(config))
    manifest = tmp_path / 'manifest.yaml'
    manifest.write_text(yaml.safe_dump([{'id': 'p', 'title': 'P', 'fulltext': 'fulltext/p.pdf'},
                                        {'id': 'q', 'title': 'Q', 'fulltext': 'fulltext/q.pdf'}]))
    fulltext = tmp_path / 'fulltext'
    fulltext.mkdir()
    pdf(fulltext / 'p.pdf', ('P Q R F(x)', 'Q P R F(x)'))
    provider = MockProvider({})
    log = EventLog(tmp_path / 'run/events.jsonl')
    calls = ModelCalls(config, provider, log, Cache(Path(config['cache_dir'])), ROOT, '')
    papers = load_papers(manifest, fulltext)
    return calls, provider, papers, manifest, fulltext, config_path


def register(calls, provider, paper, value=VALUE, usage=None):
    provider.responses[mock_key('extract_paper', calls.render('extract_paper', paper.inputs())[1])] = response(value, usage)


def accounting(log):
    return json.loads(methodology(log.path).split('```json\n')[1].split('\n```')[0])


def test_page_text_and_immutable_contract(rig):
    calls, provider, papers, *_ = rig
    assert [p.text for p in papers[0].pages] == ['P Q R F(x)', 'Q P R F(x)']
    register(calls, provider, papers[0])
    result = calls.extract_paper(papers[0])
    assert result.items[0].citation == 'p:pdf:1#p:r1-2:p'
    with pytest.raises(FrozenInstanceError):
        result.items[0].text = 'Q'


@pytest.mark.parametrize('change', ['extra', 'empty', 'attribution', 'source', 'item_source', 'page', 'blank'])
def test_schema_and_reference_rejection(rig, change):
    calls, provider, papers, *_ = rig
    invalid = copy.deepcopy(VALUE)
    if change == 'extra': invalid['extra'] = 'P'
    if change == 'empty': invalid['items'] = []
    if change == 'attribution': invalid['items'][0]['attribution'] = 'P'
    if change == 'source': invalid['source_id'] = 'q'
    if change == 'item_source': invalid['items'][0]['source_id'] = 'q'
    if change == 'page': invalid['items'][0]['page_end'] = 3
    if change == 'blank': invalid['items'][0]['text'] = ' '
    register(calls, provider, papers[0], invalid)
    with pytest.raises(Rejected): calls.extract_paper(papers[0])
    event = next(e for e in calls.log.read() if e['label'] == 'MODEL')
    assert json.loads(event['payload_json'])['status'] == 'rejected'
    assert event['usage']['input_tokens'] == 100 and event['cost_usd'] > 0
    assert not list(calls.cache.path.glob('*.json'))


def test_extraction_retry_and_reservation(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config['validation_attempts'] = 2
    responses = iter([response({**VALUE, 'source_id': 'q'}), response(VALUE)])
    def complete(*args):
        provider.calls += 1
        return Response(next(responses))
    monkeypatch.setattr(provider, 'complete', complete)
    result = calls.extract_paper(papers[0])
    assert result.source_id == 'p' and provider.calls == 2
    events = calls.log.read()
    assert len([e for e in events if e['stage'] == 'call_start']) == 2
    assert [json.loads(e['payload_json'])['status'] for e in events if e['label'] == 'MODEL'] == ['rejected', 'accepted']
    assert calls.budget.used_tokens == 300


def test_missing_fallback_and_methodology(rig, capsys):
    calls, provider, papers, *_ = rig
    register(calls, provider, papers[0])
    path = extract(calls, papers)
    data = json.loads(path.read_text()[len(HEADER):])
    assert data['papers'][1]['status'] == 'record only, not extracted'
    assert data['papers'][1]['reason'] == 'missing_pdf' and data['papers'][1]['items'] == []
    assert data['papers'][0]['items'][0]['citation'] == 'p:pdf:1#p:r1-2:p'
    output = capsys.readouterr().out
    assert 'before dispatch' in output and 'record only, not extracted' in output
    report = accounting(calls.log)
    assert report['extraction']['call_count'] == 1
    assert report['extraction']['extracted'] == ['p']
    assert report['extraction']['record_only'] == [{'source_id': 'q', 'reason': 'missing_pdf'}]
    assert report['extraction']['models'] == ['claude-opus-5']
    assert report['extraction']['tokens']['input_tokens'] == 100
    assert report['extraction']['cost_usd'] == report['cost_usd'] == .00175
    assert all(e['label'] != 'HUMAN' for e in calls.log.read())


@pytest.mark.parametrize('mode', ['invalid', 'encrypted'])
def test_unreadable_pdf_explicit_fallback(rig, mode):
    calls, provider, _, manifest, fulltext, _ = rig
    path = fulltext / 'p.pdf'
    if mode == 'invalid': path.write_bytes(b'P')
    else:
        writer = PdfWriter()
        writer.add_blank_page(width=300, height=300)
        writer.encrypt('P')
        writer.write(path)
    papers = load_papers(manifest, fulltext)
    result = extract(calls, papers)
    assert ('unreadable_pdf:' if mode == 'invalid' else 'encrypted_pdf') in result.read_text()
    assert provider.calls == 0


def test_refuse_missing_and_no_publication(rig):
    calls, provider, papers, *_ = rig
    with pytest.raises(ValueError, match='extraction refused'):
        extract(calls, (papers[1],), missing='refuse')
    assert provider.calls == 0
    assert not (calls.log.path.parent / 'literature.extracted.txt').exists()
    assert accounting(calls.log)['extraction']['record_only'][0]['source_id'] == 'q'


def test_oversize_refusal_no_dispatch(rig):
    calls, provider, papers, *_ = rig
    paper = Paper('p', papers[0].record_json, 'P', (PageText(1, 'P' * 210000),))
    with pytest.raises(BudgetStop, match='context bound'):
        extract(calls, (paper,))
    assert provider.calls == 0
    assert accounting(calls.log)['extraction']['failed'] == ['p']


def test_provider_context_bound_rechecked(rig, monkeypatch):
    from ara.types import TokenUsage
    calls, provider, papers, *_ = rig
    monkeypatch.setattr(provider, 'estimate', lambda *args: TokenUsage(input_tokens=200001))
    with pytest.raises(BudgetStop, match='context bound'):
        calls.call('extract_paper', papers[0].inputs())
    assert provider.calls == 0


@pytest.mark.parametrize('cap', ['extraction_cost_cap_usd', 'cost_cap_usd', 'token_cap'])
def test_extraction_budget_admission(rig, cap):
    calls, provider, papers, *_ = rig
    calls.config[cap] = 0
    with pytest.raises(BudgetStop): extract(calls, (papers[0],))
    assert provider.calls == 0
    assert accounting(calls.log)['extraction']['failed'] == ['p']
    assert any(e['label'] == 'STOP' for e in calls.log.read())


def test_extraction_actual_cost_cap(rig):
    calls, provider, papers, *_ = rig
    calls.config['extraction_cost_cap_usd'] = 1.0
    register(calls, provider, papers[0], usage={'input_tokens': 200000, 'output_tokens': 20000})
    with pytest.raises(BudgetStop, match='extraction cost cap exceeded'):
        extract(calls, (papers[0],))
    assert provider.calls == 1
    assert accounting(calls.log)['extraction']['cost_usd'] == 1.5
    assert not list(calls.cache.path.glob('*.json'))


def test_cache_replay_and_pdf_identity(rig, tmp_path):
    calls, provider, papers, *_ = rig
    register(calls, provider, papers[0])
    first = calls.extract_paper(papers[0])
    provider.responses.clear()
    assert calls.extract_paper(papers[0]) == first
    assert provider.calls == 1
    report = accounting(calls.log)['extraction']
    assert report['cache_replays'] == 1 and report['dispatch_count'] == 1
    assert report['cost_usd'] == .00175
    changed = Paper('p', papers[0].record_json, 'Q', papers[0].pages)
    register(calls, provider, changed)
    calls.extract_paper(changed)
    assert provider.calls == 2


def test_provenance_integrity(rig, tmp_path):
    calls, provider, papers, *_ = rig
    register(calls, provider, papers[0])
    path = extract(calls, papers)
    events = literature_provenance(path, path.read_text())
    log = EventLog(tmp_path / 'import/events.jsonl')
    import_provenance(log, events)
    assert accounting(log)['extraction']['cost_usd'] == .00175
    assert accounting(log)['extraction']['upstream_receipts_imported']
    with pytest.raises(ValueError, match='does not match'):
        literature_provenance(path, path.read_text().replace('"text":"P P P"', '"text":"R R R"'))
    path.with_suffix('.provenance.json').unlink()
    with pytest.raises(FileNotFoundError): literature_provenance(path, path.read_text())


def test_extract_cli_to_build_t_native_path(rig, tmp_path, monkeypatch):
    calls, provider, papers, manifest, fulltext, config_path = rig
    def factory(config, log, topic):
        return ModelCalls(config, provider, log, calls.cache, ROOT, topic)
    observed = []
    def complete(kind, prompt, schema, maximum):
        provider.calls += 1
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        observed.append((kind, inputs))
        if kind == 'extract_paper':
            assert inputs['pages'] == [{'page': 1, 'text': 'P Q R F(x)'}, {'page': 2, 'text': 'Q P R F(x)'}]
            value = VALUE
        elif kind in ('select_t_roots', 'build_t_batch'):
            from rich_fixture import batch_response
            assert inputs['papers'][0]['source_id'] == 'p'
            value = batch_response(inputs)
        elif kind == 'classify_target': value = dict(novelty='new_assertion',fidelity='matches',classification='own_thesis',reason='P')
        elif kind == 'propose_targets':
            value = {'targets': [{'id': 'p', 'text': 'P', 'formula': {'op': 'atom', 'name': 'P'}}]}
        elif kind == 'propose_cuts': value = {'proposals': []}
        elif kind == 'map_leaf': value = {'t_id': 'open'}
        else: raise AssertionError(kind)
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    extraction_dir = tmp_path / 'extracted'
    assert main(['extract', '--config', str(config_path), '--manifest', str(manifest),
                 '--fulltext-dir', str(fulltext), '--run-dir', str(extraction_dir)], calls_factory=factory) == 0
    artifact = extraction_dir / 'literature.extracted.txt'
    run = tmp_path / 'native'
    assert main(['run', '--config', str(config_path), '--topic', 'P', '--literature', str(artifact),
                 '--run-dir', str(run)], calls_factory=factory) == 0
    assert any(kind == 'build_t_batch' for kind, _ in observed)
    assert json.loads((run / 'commitments.json').read_text())['commitments'][0]['citation'] == 'p:pdf:1#p:r1-2:p'
    log = EventLog(run / 'events.jsonl')
    assert accounting(log)['extraction']['extracted'] == ['p']
    assert accounting(log)['extraction']['cost_usd'] == .00175
    assert all(json.loads(e['payload_json']).get('literature') is None for e in log.read() if e['label'] == 'HUMAN')
    start = next(e for e in log.read() if e['stage'] == 'run_started')
    assert json.loads(start['payload_json'])['literature_source'] == 'model_extraction'


def test_build_t_cannot_cite_fallback_or_invented_page(rig, monkeypatch):
    from rich_fixture import batch_response
    calls, provider, papers, *_ = rig
    register(calls, provider, papers[0])
    path = extract(calls, papers)
    def complete(kind, prompt, schema, maximum):
        value = batch_response(json.loads(prompt.split('\nINPUT_JSON\n')[1]))
        if kind == 'build_t_batch': value['commitments'][0]['citation'] = 'q:pdf:1'
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    with pytest.raises(Rejected, match='ValidationError'):
        calls.build_t(path.read_text(), 'P')


def test_record_only_cannot_build_t(rig):
    calls, provider, papers, *_ = rig
    path = extract(calls, (papers[1],))
    with pytest.raises(Rejected, match='no extracted claims'):
        calls.build_t(path.read_text(), 'P')
    assert provider.calls == 0


def test_estimate_only_never_dispatches(rig):
    calls, provider, papers, *_ = rig
    assert extract(calls, papers, estimate_only=True) is None
    assert provider.calls == 0
    estimate = next(json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'extraction_estimate')
    assert estimate['pages'] == 2
    assert estimate['input_tokens'] - len(calls.render('extract_paper', {})[1].encode()) >= 3000
    assert estimate['output_token_allowance'] == 32000
    assert estimate['estimated_usd'] > .2


def test_retry_requires_remaining_extraction_budget(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config['validation_attempts'] = 2
    schema = json.loads((ROOT / 'schemas/extract_paper.json').read_text())
    estimate = provider.estimate('extract_paper', calls.render('extract_paper', papers[0].inputs())[1], schema, calls.config['extract_paper_max_output_tokens'])
    calls.config['extraction_cost_cap_usd'] = float(calls.budget.cost(estimate)) + .00001
    register(calls, provider, papers[0], {**VALUE, 'source_id': 'q'})
    with pytest.raises(BudgetStop, match='extraction cost cap'):
        calls.extract_paper(papers[0])
    assert provider.calls == 1
    assert accounting(calls.log)['extraction']['call_count'] == 1


def test_imported_extraction_cost_reduces_run_budget(rig, tmp_path):
    calls, provider, papers, *_ = rig
    register(calls, provider, papers[0])
    path = extract(calls, papers)
    log = EventLog(tmp_path / 'downstream/events.jsonl')
    import_provenance(log, literature_provenance(path, path.read_text()))
    config = {**calls.config, 'cost_cap_usd': .001}
    downstream = ModelCalls(config, provider, log, calls.cache, ROOT, 'P')
    with pytest.raises(BudgetStop, match='cost cap'):
        downstream.build_t(path.read_text(), 'P')
    assert provider.calls == 1


@pytest.mark.parametrize('mutation', ['duplicate', 'path', 'unknown_selection'])
def test_manifest_rejects_ambiguous_or_unsafe_records(rig, mutation):
    _, _, _, manifest, fulltext, _ = rig
    records = yaml.safe_load(manifest.read_text())
    if mutation == 'duplicate': records.append(records[0])
    if mutation == 'path': records[0]['fulltext'] = '../p.pdf'
    manifest.write_text(yaml.safe_dump(records))
    with pytest.raises(ValueError):
        load_papers(manifest, fulltext, ('r',) if mutation == 'unknown_selection' else ())
