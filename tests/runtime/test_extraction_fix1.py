"""Review regressions: full corpus capacity, lineage, and physical page coverage."""
import copy
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
import json

import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject, DecodedStreamObject, DictionaryObject
import yaml

from test_extraction import rig, offline, pdf, register, accounting, response, ROOT, ITEM, VALUE
from ara.runtime.budget import BudgetStop
from ara.runtime.cache import Cache, canonical
from ara.runtime.calls import ModelCalls, Rejected
from ara.runtime.cli import main
from ara.runtime.extraction import (load_papers, extract, Paper, PageText, PaperExtraction, ExtractedItem,
    literature_entry, entry_size, ENTRY_BYTES, HEADER, literature_provenance, import_provenance,
    MissingExtractionLineage)
from ara.runtime.logging import EventLog
from ara.runtime.providers import AnthropicProvider, MockProvider, Response
from ara.types import TokenUsage


@pytest.mark.parametrize('case', ['items', 'text', 'serialized'])
def test_extraction_output_budget(rig, case):
    calls, provider, papers, *_ = rig
    value = copy.deepcopy(VALUE)
    if case == 'items': value['items'] *= 5
    if case == 'text': value['items'][0]['text'] = 'P' * 401
    if case == 'serialized': value['items'] = [{**ITEM, 'text': 'P' * 400} for _ in range(4)]
    register(calls, provider, papers[0], value)
    with pytest.raises(Rejected): calls.extract_paper(papers[0])
    assert not list(calls.cache.path.glob('*.json'))
    assert accounting(calls.log)['extraction']['cost_usd'] == .00175


def test_build_t_counted_context_refusal(rig, monkeypatch):
    calls, provider, *_ = rig
    calls.config.update(token_cap=1000000, cost_cap_usd=100)
    monkeypatch.setattr(provider, 'estimate', lambda *args: TokenUsage(input_tokens=200001))
    with pytest.raises(BudgetStop, match='build_t context bound'):
        calls.build_t('P', 'Q')
    assert provider.calls == 0
    admission = next(json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'context_admission')
    assert admission['decision'] == 'refused' and admission['input_tokens'] == 200001
    assert 'LOCAL_RESPONSE_SCHEMA' in admission['prompt'] and '"literature":"P"' in admission['prompt']
    assert not any(e['stage'] == 'call_start' for e in calls.log.read())


@pytest.mark.parametrize('unicode', [False, True])
def test_large_bytes_use_counted_tokens(rig, monkeypatch, unicode):
    calls, provider, papers, *_ = rig
    # No substantive content; exercise a text encoding and length well beyond the old byte cliff.
    text = ('\ufb01' if unicode else 'P Q ') * 100000
    paper = Paper('p', papers[0].record_json, 'P', (PageText(1, text),))
    register(calls, provider, paper)
    monkeypatch.setattr(provider, 'estimate', lambda *args: TokenUsage(input_tokens=90000, output_tokens=8192))
    path = extract(calls, (paper,))
    assert provider.calls == 1 and 'p:pdf:1' in path.read_text()
    assert any(e['stage'] == 'extraction_size_warning' for e in calls.log.read())


def test_blank_pages_retained_without_rejecting_paper(rig):
    calls, provider, _, manifest, fulltext, _ = rig
    pdf(fulltext / 'p.pdf', ('', 'P', ''))
    paper = load_papers(manifest, fulltext, ('p',))[0]
    assert paper.unavailable is None and not paper.affected_pages
    assert paper.inputs()['pages'] == [{'page': 2, 'text': 'P'}]
    assert [(d.page, d.reason) for d in paper.diagnostics] == [(1, 'blank_page'), (3, 'blank_page')]
    value = {'source_id': 'p', 'items': [{**ITEM, 'page_start': 2, 'page_end': 2}]}
    register(calls, provider, paper, value)
    path = extract(calls, (paper,))
    assert 'p:pdf:2' in path.read_text()
    report = accounting(calls.log)['extraction']
    assert report['extracted'] == ['p'] and not report['partial']
    assert [d['page'] for d in report['page_diagnostics'][0]['pages']] == [1, 3]


def add_image(path, page_index):
    reader = PdfReader(path)
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    page = writer.pages[page_index]
    image = DecodedStreamObject()
    image.set_data(b'\x00')
    image.update({NameObject('/Type'): NameObject('/XObject'), NameObject('/Subtype'): NameObject('/Image'),
                  NameObject('/Width'): NumberObject(1), NameObject('/Height'): NumberObject(1),
                  NameObject('/ColorSpace'): NameObject('/DeviceGray'), NameObject('/BitsPerComponent'): NumberObject(8)})
    resources = page['/Resources']
    resources[NameObject('/XObject')] = DictionaryObject({NameObject('/Im0'): writer._add_object(image)})
    content = DecodedStreamObject()
    content.set_data(page.get_contents().get_data() + b'\nq 250 0 0 250 0 0 cm /Im0 Do Q')
    page[NameObject('/Contents')] = writer._add_object(content)
    writer.write(path)


@pytest.mark.parametrize('header', ['P', ''])
def test_sparse_image_pages_are_partial(rig, header):
    calls, provider, _, manifest, fulltext, _ = rig
    path = fulltext / 'p.pdf'
    pdf(path, ('P', header))
    add_image(path, 1)
    paper = load_papers(manifest, fulltext, ('p',))[0]
    assert paper.unavailable is None and paper.affected_pages == (2,)
    assert paper.inputs()['pages'] == [{'page': 1, 'text': 'P'}]
    register(calls, provider, paper)
    result = extract(calls, (paper,))
    entry = json.loads(result.read_text()[len(HEADER):])['papers'][0]
    assert entry['status'] == 'partial' and 'partial' in entry['coverage']
    outcome = next(json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'extraction_outcome')
    assert outcome['affected_pages'] == [2]
    assert outcome['page_diagnostics'] == [{'page': 2, 'reason': 'sparse_image_text', 'text_chars': len(header)}]
    report = accounting(calls.log)['extraction']
    assert not report['extracted'] and report['partial'][0]['affected_pages'] == [2]


def test_extraction_cannot_cite_unread_image_page(rig):
    calls, provider, _, manifest, fulltext, _ = rig
    add_image(fulltext / 'p.pdf', 1)
    paper = load_papers(manifest, fulltext, ('p',))[0]
    register(calls, provider, paper, {'source_id': 'p', 'items': [{**ITEM, 'page_end': 2}]})
    with pytest.raises(Rejected, match='unread page'): calls.extract_paper(paper)


def test_image_only_paper_stays_partial_without_model(rig):
    calls, provider, _, manifest, fulltext, _ = rig
    pdf(fulltext / 'p.pdf', ('',))
    add_image(fulltext / 'p.pdf', 0)
    path = extract(calls, load_papers(manifest, fulltext, ('p',)))
    assert provider.calls == 0
    entry = json.loads(path.read_text()[len(HEADER):])['papers'][0]
    assert entry['status'] == 'partial' and entry['items'] == []
    assert accounting(calls.log)['extraction']['partial'][0]['affected_pages'] == [1]


def test_fresh_cache_artifact_refused_at_cli_import(rig, tmp_path):
    calls, provider, papers, _, _, config_path = rig
    calls.log.human('extract', 'P', reported_minutes=3)
    register(calls, provider, papers[0])
    original = extract(calls, (papers[0],))
    replay_log = EventLog(tmp_path / 'replay/events.jsonl')
    replay = ModelCalls(calls.config, provider, replay_log, calls.cache, ROOT, '')
    replay_path = extract(replay, (papers[0],))
    assert provider.calls == 1
    report = accounting(replay_log)
    assert not report['accounting_complete'] and not report['extraction']['production_lineage_complete']
    assert report['cost_usd'] == 0 and report['extraction']['cache_replays'] == 1
    with pytest.raises(MissingExtractionLineage, match='origin receipt'):
        literature_provenance(replay_path, replay_path.read_text())
    directory = tmp_path / 'refused'
    assert main(['run', '--config', str(config_path), '--topic', 'P', '--literature', str(replay_path),
                 '--run-dir', str(directory)]) == 2
    failed = EventLog(directory / 'events.jsonl')
    assert not accounting(failed)['accounting_complete']
    assert not any(e['stage'] == 'call_start' for e in failed.read())
    imported = EventLog(tmp_path / 'direct/events.jsonl')
    events = literature_provenance(original, original.read_text())
    import_provenance(imported, events)
    count = len(imported.read())
    import_provenance(imported, events)
    assert len(imported.read()) == count
    imported.human('run', 'Q', reported_minutes=1)
    summary = accounting(imported)
    assert summary['accounting_complete'] and summary['inherited_totals']['cost_usd'] == .00175
    assert summary['local_totals']['cost_usd'] == 0
    assert summary['inherited_totals']['human_reported_minutes'] == 3
    assert summary['local_totals']['human_reported_minutes'] == 1
    assert len(summary['inherited_receipt_ids']) == 1


def test_preflight_flags_caps_and_profile_is_explicit(rig, tmp_path, capsys):
    calls, provider, papers, manifest, fulltext, config_path = rig
    long = Paper('p', papers[0].record_json, 'P', tuple(PageText(i, 'P') for i in range(1, 1820)))
    extract(calls, (long,), estimate_only=True)
    assert 'planned batch exceeds enclosing caps' in capsys.readouterr().out
    selected = []
    def factory(config, log, topic):
        selected.append(config)
        return ModelCalls(config, provider, log, calls.cache, ROOT, topic)
    assert main(['extract', '--config', str(config_path), '--profile', 'extraction', '--manifest', str(manifest),
                 '--fulltext-dir', str(fulltext), '--estimate-only', '--run-dir', str(tmp_path / 'profile')],
                calls_factory=factory) == 0
    config = selected[0]
    assert config['cost_cap_usd'] == config['extraction_cost_cap_usd'] == 30
    assert config['token_cap'] == 6000000
    defaults = yaml.safe_load(config_path.read_text())
    assert defaults['cost_cap_usd'] == 10 and defaults['token_cap'] == 200000


def maximum_value(source_id):
    value = {'source_id': source_id, 'items': [{**ITEM, 'source_id': source_id} for _ in range(4)]}
    def size():
        result = PaperExtraction(source_id, tuple(ExtractedItem(**item) for item in value['items']))
        return entry_size(literature_entry({**result.to_dict(), 'status': 'extracted'}))
    for item in value['items']:
        while len(item['text']) < 400 and size() < ENTRY_BYTES:
            item['text'] += 'P'
    assert size() == ENTRY_BYTES
    return value


class CapacityServer:
    """Offline SDK surface: count the complete UTF-8 request conservatively, never tokenize remotely."""
    def __init__(self):
        self.messages = self
        self.beta = SimpleNamespace(messages=self)
        self.counted = []
        self.requests = []
        self.values = {}

    def count_tokens(self, **request):
        self.counted.append(request)
        return SimpleNamespace(input_tokens=len(request['messages'][0]['content'].encode()) + 32)

    def create(self, **request):
        self.requests.append(request)
        prompt = request['messages'][0]['content']
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if prompt.startswith('ROLE: extract_paper'):
            value = maximum_value(inputs['source_id'])
            self.values[inputs['source_id']] = value
        elif prompt.startswith('ROLE: build_t'):
            assert request['max_tokens'] == 64000
            entries = json.loads(inputs['literature'][len(HEADER):])['papers']
            assert len(entries) == 53 and all(entry_size(entry) == ENTRY_BYTES for entry in entries)
            value = {'commitments': [
                {'id': f't{n}_{i}', 'text': item['text'], 'citation': item['citation'], 'formula': {'op': 'atom', 'name': 'P'}}
                for n, entry in enumerate(entries) for i, item in enumerate(entry['items'])]}
        elif prompt.startswith('ROLE: propose_targets'):
            value = {'targets': [{'id': 'q', 'text': 'Q', 'formula': {'op': 'atom', 'name': 'Q'}}]}
        elif prompt.startswith('ROLE: propose_cuts'):
            value = {'proposals': []}
        elif prompt.startswith('ROLE: map_leaf'):
            value = {'t_id': 'open'}
        else: raise AssertionError(prompt[:40])
        return SimpleNamespace(to_dict=lambda **kwargs: response(value))

    @contextmanager
    def stream(self, **request):
        yield SimpleNamespace(get_final_message=lambda: self.create(**request))


def test_capacity53_maximum_through_cli(rig, tmp_path):
    calls, _, _, manifest, fulltext, config_path = rig
    records = [{'id': f'p{i:02}' + 'P' * 61, 'title': 'P', 'fulltext': f'fulltext/p{i:02}' + 'P' * 61 + '.pdf'}
               for i in range(53)]
    manifest.write_text(yaml.safe_dump(records))
    for record in records: pdf(fulltext / (record['id'] + '.pdf'), ('P',))
    server = CapacityServer()
    def factory(config, log, topic):
        return ModelCalls(config, AnthropicProvider(config, client=server), log, calls.cache, ROOT, topic)
    directory = tmp_path / 'capacity-extract'
    assert main(['extract', '--config', str(config_path), '--profile', 'extraction', '--manifest', str(manifest),
                 '--fulltext-dir', str(fulltext), '--run-dir', str(directory)], calls_factory=factory) == 0
    artifact = directory / 'literature.extracted.txt'
    downstream = tmp_path / 'capacity-t'
    config = yaml.safe_load(config_path.read_text())
    config.update(config['extraction'])
    config_path.write_text(yaml.safe_dump(config))
    assert main(['run', '--config', str(config_path), '--topic', 'P', '--literature', str(artifact),
                 '--run-dir', str(downstream)], calls_factory=factory) == 0
    commitments = json.loads((downstream / 'commitments.json').read_text())['commitments']
    assert len(commitments) == 212
    assert {c['citation'].split(':')[0] for c in commitments} == {r['id'] for r in records}
    log = EventLog(downstream / 'events.jsonl')
    admission = next(json.loads(e['payload_json']) for e in log.read()
                     if e['stage'] == 'context_admission' and json.loads(e['payload_json'])['kind'] == 'build_t')
    assert admission['decision'] == 'fits'
    assert admission['input_tokens'] + admission['output_tokens'] < 190000
    counted = next(r for r in server.counted if r['messages'][0]['content'].startswith('ROLE: build_t'))
    prompt = counted['messages'][0]['content']
    tail = prompt.split('\nINPUT_JSON\n')[1]
    inputs, end = json.JSONDecoder().raw_decode(tail)
    assert inputs['literature'] == artifact.read_text()
    assert json.loads(tail[end:]) == json.loads((ROOT / 'schemas/build_t.json').read_text())
    assert 'LOCAL_RESPONSE_SCHEMA' in prompt and all(record['id'] in prompt for record in records)
    report = accounting(log)
    assert report['extraction']['call_count'] == 53 and report['accounting_complete']
    assert report['inherited_totals']['model_calls'] == 53
    print('CAPACITY53 ' + canonical({k: admission[k] for k in ('input_tokens', 'output_tokens', 'limit', 'decision')}))


def test_build_t_retry_recounts_feedback(rig, monkeypatch):
    calls, provider, *_ = rig
    calls.config.update(validation_attempts=2, token_cap=1000000, cost_cap_usd=100)
    prompts = []
    def estimate(kind, prompt, schema, maximum):
        prompts.append(prompt)
        return TokenUsage(input_tokens=200001 if 'validation_feedback' in prompt else 10, output_tokens=maximum)
    def complete(*args):
        provider.calls += 1
        return Response(response({'commitments': []}))
    monkeypatch.setattr(provider, 'estimate', estimate)
    monkeypatch.setattr(provider, 'complete', complete)
    with pytest.raises(BudgetStop, match='build_t context bound'):
        calls.build_t('P', 'Q')
    assert provider.calls == 1 and len(prompts) == 2
    assert 'validation_feedback' in prompts[1]
    assert len([e for e in calls.log.read() if e['stage'] == 'call_start']) == 1


def test_nontext_vector_page_is_not_blank(rig):
    calls, provider, _, manifest, fulltext, _ = rig
    path = fulltext / 'p.pdf'
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=300)
    stream = DecodedStreamObject()
    stream.set_data(b'0 0 100 100 re f')
    page[NameObject('/Contents')] = writer._add_object(stream)
    writer.write(path)
    paper = load_papers(manifest, fulltext, ('p',))[0]
    assert paper.affected_pages == (1,)
    assert paper.diagnostics[0].reason == 'nontext_visual_content'
    path = extract(calls, (paper,))
    assert json.loads(path.read_text()[len(HEADER):])['papers'][0]['status'] == 'partial'
    assert provider.calls == 0
