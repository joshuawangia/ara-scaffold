"""Observed envelope replay with placeholder content and no provider network."""
import json

import pytest
from jsonschema import Draft202012Validator, ValidationError

from ara.runtime.calls import Rejected
from ara.runtime.budget import BudgetStop
from ara.runtime.cli import main
from ara.runtime.extraction import Paper, PageText, extract, literature_provenance
from ara.runtime.providers import Response, structured_schema
from ara.types import TokenUsage
from rich_fixture import graph
from test_extraction import rig, offline, response, accounting


def split_replay(rig, monkeypatch, *, limit=24, terminal=False, review_defect=False):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_targeted_corrections=1, extraction_require_inference=True,
                        extraction_paper_continuation_limit=limit)
    paper = Paper('p', papers[0].record_json, 'P', (PageText(1, 'P'), PageText(2, 'Q')))
    sent = []

    def estimate(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        return TokenUsage(input_tokens=200001 if 'mode' not in data and len(data['pages']) == 2 else 100,
                          output_tokens=maximum)

    def complete(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        sent.append(data)
        assert 'context_request' not in schema['properties']
        page = data['pages'][0]['page'] if data['pages'] else 1
        value = graph(page=page)
        if data.get('mode') == 'targeted_correction':
            value['items'] = []  # Envelope-only fix preserves the entire candidate.
            if terminal:
                value['source_id'] = 'q'
        elif data.get('mode') == 'reconcile_ranges':
            value['items'] = []
            if review_defect:
                value['context_request'] = {'pages': [], 'evidence_ids': []}
        elif page == 1:
            value['source_id'] = 'q'  # First range also needs a correction.
        else:
            # Same observed envelope defect: complete, no gaps, empty-array request.
            value['items'] = value['items'][:1]
            value['context_request'] = {'pages': [], 'evidence_ids': []}
        return Response(response(value))

    monkeypatch.setattr(provider, 'estimate', estimate)
    monkeypatch.setattr(provider, 'complete', complete)
    return calls, paper, sent


def test_second_range_gets_correction_after_first_used_one(rig, monkeypatch):
    calls, paper, sent = split_replay(rig, monkeypatch)
    path = extract(calls, (paper,))
    assert [i.get('mode', 'initial') for i in sent] == [
        'initial', 'targeted_correction', 'initial', 'targeted_correction', 'reconcile_ranges']
    assert len(json.loads((path.parent/'p.r1-1.rich.json').read_text())['items']) == 8
    assert len(json.loads((path.parent/'p.r2-2.rich.json').read_text())['items']) == 1
    events = literature_provenance(path, path.read_text())
    models = [e for e in events if e['label'] == 'MODEL']
    assert [json.loads(e['payload_json'])['status'] for e in models] == [
        'rejected', 'accepted', 'rejected', 'accepted', 'accepted']
    assert calls.budget.used_tokens == 750
    assert accounting(calls.log)['extraction']['failed'] == []


def test_correction_still_obeys_paper_allowance(rig, monkeypatch):
    calls, paper, sent = split_replay(rig, monkeypatch, limit=2)
    path = extract(calls, (paper,))
    value = json.loads((path.parent/'p.extraction.json').read_text())
    assert value['status'] == 'partial' and len(value['items']) == 8
    assert len(sent) == 3
    assert (calls.log.path.parent/'p.r1-1.rich.json').exists()
    assert (calls.log.path.parent/'literature.extracted.txt').exists()


@pytest.mark.parametrize('mode', ['initial', 'review', 'obligation'])
@pytest.mark.parametrize('correction', [False, True])
def test_mode_contract_reaches_counter_prompt_and_wire(rig, monkeypatch, mode, correction):
    calls, provider, papers, *_ = rig
    inputs = papers[0].inputs()
    if mode != 'initial':
        inputs.update(mode='reconcile_ranges', obligations=[] if mode == 'review' else [{'id': 'P'}])
    if correction:
        inputs.update(original_mode=inputs.get('mode'), mode='targeted_correction')
    seen = []
    monkeypatch.setattr(provider, 'estimate', lambda kind, prompt, schema, maximum:
                        (seen.append((prompt, schema)) or TokenUsage(input_tokens=1)))
    calls.count_request('extract_paper', inputs)
    prompt, schema = seen[0]
    embedded = json.loads(prompt.split('LOCAL_RESPONSE_SCHEMA (all constraints are mandatory)\n')[1].split('\nINPUT_JSON\n')[0])
    assert schema == embedded
    wire = structured_schema(schema)
    for candidate in [schema, *wire.get('anyOf', [wire])]:
        props = candidate['properties']
        assert ('context_request' in props) == (mode == 'obligation')
        assert ('pending_obligation_ids' in props) == (mode == 'obligation')
        assert ('resolutions' in props) == (mode == 'obligation')
        assert ('empty_reason' in props) == (mode == 'initial')
    if mode != 'obligation':
        with pytest.raises(ValidationError):
            Draft202012Validator(schema).validate({**graph(), 'context_request': {'pages': [], 'evidence_ids': []}})


@pytest.mark.parametrize('bad_request', [
    {'pages': [], 'evidence_ids': []},
    {'pages': [3], 'evidence_ids': []},
    {'pages': [], 'evidence_ids': ['unknown']},
])
def test_obligation_request_errors_correct_before_acceptance(rig, monkeypatch, bad_request):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 1
    sent = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        sent.append(inputs)
        value = graph()
        if not inputs.get('mode'):
            value.update(coverage_complete=False, new_gaps=[{'description': 'Q'}])
        else:
            value['items'] = []
            oid = inputs['obligations'][0]['id']
            if inputs['mode'] == 'targeted_correction':
                value['resolutions'] = [{'obligation_id': oid, 'evidence_ids': ['p:r1-2:p']}]
            else:
                value.update(coverage_complete=False, pending_obligation_ids=[oid], context_request=bad_request)
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    result = calls.extract_paper(papers[0])
    assert not json.loads(result.resolutions_json)
    assert len(result.items) == 8
    assert any(d['kind'] == 'reconciliation_failed' for d in json.loads(result.dispositions_json))
    assert [i.get('mode') for i in sent] == [None, 'reconcile_ranges']
    assert not [e for e in calls.log.read() if e['stage'] == 'extraction_targeted_correction']


def test_terminal_failure_stops_corpus_and_pilot_import(rig, monkeypatch):
    calls, paper, sent = split_replay(rig, monkeypatch, terminal=True)
    second = Paper('q', '{"id":"q"}', 'Q', (PageText(1, 'Q'),))
    with pytest.raises(Rejected):
        extract(calls, (paper, second))
    assert [i['source_id'] for i in sent] == ['p', 'p']
    outcomes = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'extraction_outcome']
    assert outcomes[0]['status'] == 'failed'
    assert outcomes[1]['status'] == 'not extracted'
    stopped = next(json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'extraction_stopped')
    assert stopped['policy'] == 'continue-on-paper-failure' and stopped['max_failed_papers'] == 0 and stopped['not_attempted'] == ['q']
    assert accounting(calls.log)['extraction']['stops'] == [stopped]
    assert (calls.log.path.parent/'literature.extracted.txt').exists()
    path = calls.log.path.parent/'literature.extracted.txt'
    literature_provenance(path, path.read_text())


def test_existing_run_refused_before_provider_and_left_untouched(rig):
    calls, _, _, manifest, fulltext, config_path = rig
    artifact = calls.log.path.parent/'p.r1-1.rich.json'
    artifact.write_text('P')
    before = {p.name: p.read_bytes() for p in artifact.parent.iterdir()}
    def forbidden(*args):
        pytest.fail('provider constructed for an unsupported resume')
    assert main(['extract', '--config', str(config_path), '--manifest', str(manifest),
                 '--fulltext-dir', str(fulltext), '--run-dir', str(artifact.parent)], calls_factory=forbidden) == 2
    assert {p.name: p.read_bytes() for p in artifact.parent.iterdir()} == before


def test_graph_review_can_correct_request_without_dropping_evidence(rig, monkeypatch):
    calls, paper, sent = split_replay(rig, monkeypatch, review_defect=True)
    path = extract(calls, (paper,))
    assert len(sent) == 5
    assert sent[-1]['mode'] == 'reconcile_ranges'
    assert len(json.loads((path.parent/'p.extraction.json').read_text())['items']) == 9
    literature_provenance(path, path.read_text())


@pytest.mark.parametrize('limit', [0, 16])
def test_context_limit_and_reordered_cycle_can_correct(rig, monkeypatch, limit):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_targeted_corrections=1, reconciliation_context_requests=limit)
    paper = Paper('p', papers[0].record_json, 'P', (*papers[0].pages, PageText(3, 'R')))
    sent = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        sent.append(inputs)
        value = graph()
        if not inputs.get('mode'):
            value.update(coverage_complete=False, new_gaps=[{'description': 'Q'}])
        else:
            value['items'] = []
            oid = inputs['obligations'][0]['id']
            if inputs['mode'] == 'targeted_correction':
                value['resolutions'] = [{'obligation_id': oid, 'evidence_ids': ['p:r1-3:p']}]
            else:
                value.update(coverage_complete=False, pending_obligation_ids=[oid],
                    context_request={'pages': [1, 2] if len(sent) == 2 else [2, 1], 'evidence_ids': []})
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    result = calls.extract_paper(paper)
    assert len(sent) == 2
    models = [e for e in calls.log.read() if e['label'] == 'MODEL']
    assert len(models) == len(sent)  # A reordered cycle must not add a cached accepted turn.
    assert not json.loads(result.resolutions_json)
    assert any(d['kind'] == 'context_request_unfulfilled' for d in json.loads(result.dispositions_json))
    rejected = [json.loads(e['payload_json']) for e in calls.log.read()
                if e['label'] == 'MODEL' and json.loads(e['payload_json'])['status'] == 'rejected']
    assert rejected == []
