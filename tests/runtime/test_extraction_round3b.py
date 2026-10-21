"""Targeted extraction corrections and compact discriminated wire, P/Q only."""
import copy
import json

import pytest
from jsonschema import Draft202012Validator
from test_extraction import rig, offline, response, ROOT
from rich_fixture import graph
from ara.runtime.providers import Response, structured_schema
from ara.runtime.calls import Rejected
from ara.runtime.extraction import extract


def test_extraction_grammar_size():
    schema = structured_schema(json.loads((ROOT / 'schemas/extract_paper.json').read_text()))
    Draft202012Validator.check_schema(schema)
    branches = schema['properties']['items']['items']['anyOf']
    assert len(branches) == 3
    # Bounded flat alternatives, no recursion or combinatorial formula grammar.
    assert len(json.dumps(schema).encode()) < 6000
    assert sum(len(b['properties']) for b in branches) <= 34
    assert '$ref' not in json.dumps(schema)
    kinds = [k for b in branches for k in b['properties']['kind']['enum']]
    assert len(kinds) == len(set(kinds)) == 8


@pytest.mark.parametrize('failure', ['relation', 'inferences'])
@pytest.mark.parametrize('patch', ['valid', 'unchanged', 'invalid'])
def test_targeted_correction_preserves_inventory_and_is_bounded(rig, monkeypatch, failure, patch):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_targeted_corrections=1, extraction_require_inference=True, validation_attempts=3)
    candidate = graph()
    if failure == 'relation':
        candidate['items'][0]['applies_to'] = ['q']
        changes = [graph()['items'][0]]
    else:
        changes = [i for i in candidate['items'] if i['kind'] == 'inference']
        candidate['items'] = [i for i in candidate['items'] if i['kind'] != 'inference']
    correction = {**graph(), 'items': copy.deepcopy(changes)}
    if patch == 'unchanged': correction['items'].append(copy.deepcopy(candidate['items'][1]))
    if patch == 'invalid': correction['items'][0]['source_id'] = 'q'
    sent = []
    def complete(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1]); sent.append(data)
        if len(sent) == 1: return Response(response(candidate))
        assert data['mode'] == 'targeted_correction'
        assert data['candidate']['items'] == candidate['items']
        assert data['pages'] and data['validation_error']
        return Response(response(correction))
    monkeypatch.setattr(provider, 'complete', complete)
    if patch == 'valid':
        result = calls.extract_paper(papers[0])
        assert len(result.items) == len(graph()['items'])
        assert sum(i.kind == 'inference' for i in result.items) == 2
        assert [i.text for i in result.items] == [i['text'] for i in graph()['items']]
        assert len(list(calls.cache.path.glob('*.json'))) == 1
    else:
        with pytest.raises(Rejected): extract(calls, (papers[0],))
        assert not list(calls.cache.path.glob('*.json'))
        assert not (calls.log.path.parent / 'literature.extracted.txt').exists()
    assert len(sent) == 2  # Generic validation_attempts must not add more corrections.
    models = [e for e in calls.log.read() if e['label'] == 'MODEL']
    assert len(models) == 2 and all(e['cost_usd'] > 0 for e in models)
    assert len([e for e in calls.log.read() if e['stage'] == 'context_admission']) == 2
    assert json.loads(models[0]['payload_json'])['status'] == 'rejected'


def test_zero_inference_refused_without_correction(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_require_inference=True, extraction_targeted_corrections=0, validation_attempts=3)
    value = graph(); value['items'] = [i for i in value['items'] if i['kind'] != 'inference']
    monkeypatch.setattr(provider, 'complete', lambda *a: Response(response(value)))
    with pytest.raises(Rejected, match='no stated inference'): extract(calls, (papers[0],))
    assert len([e for e in calls.log.read() if e['label'] == 'MODEL']) == 1
    assert not list(calls.cache.path.glob('*.json'))
    assert not (calls.log.path.parent / 'literature.extracted.txt').exists()


def test_each_range_has_one_correction_inside_paper_allowance(rig, monkeypatch):
    from ara.types import TokenUsage
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_targeted_corrections=1, validation_attempts=3)
    sent = []
    def estimate(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        return TokenUsage(input_tokens=200001 if len(data['pages']) > 1 else 100, output_tokens=maximum)
    def complete(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1]); sent.append(data)
        if data.get('mode') == 'reconcile_ranges':
            return Response(response({**graph(), 'items': []}))
        value = graph(page=data['pages'][0]['page'])
        if data.get('mode') == 'targeted_correction': value['items'] = value['items'][:1]
        else: value['items'][0]['applies_to'] = ['q']
        return Response(response(value))
    monkeypatch.setattr(provider, 'estimate', estimate)
    monkeypatch.setattr(provider, 'complete', complete)
    path = extract(calls, (papers[0],))
    assert len(sent) == 5
    assert sum(d.get('mode') == 'targeted_correction' for d in sent) == 2
    assert path.exists()


def test_correction_is_readmitted_before_dispatch(rig, monkeypatch):
    from ara.runtime.budget import BudgetStop
    from ara.types import TokenUsage
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_targeted_corrections=1, extraction_require_inference=True, cost_cap_usd=.01)
    sent = []
    def estimate(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        return TokenUsage(input_tokens=10000 if data.get('mode') == 'targeted_correction' else 100, output_tokens=50)
    def complete(*args):
        sent.append(args)
        value = graph(); value['items'][0]['applies_to'] = ['q']
        return Response(response(value))
    monkeypatch.setattr(provider, 'estimate', estimate)
    monkeypatch.setattr(provider, 'complete', complete)
    with pytest.raises(BudgetStop): extract(calls, (papers[0],))
    assert len(sent) == 1
    assert not list(calls.cache.path.glob('*.json'))
