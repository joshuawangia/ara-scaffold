"""Acceptance and bounded patch recovery; placeholder-only responses."""
import copy
import json

import pytest
from jsonschema import Draft202012Validator

from ara.runtime.budget import BudgetStop
from ara.runtime.calls import Rejected
from ara.runtime.providers import Response, structured_schema
from rich_fixture import graph
from test_extraction import rig, offline, response


def sequence(monkeypatch, provider, values):
    sent = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        sent.append(inputs)
        return Response(response(values[min(len(sent)-1, len(values)-1)]))
    monkeypatch.setattr(provider, 'complete', complete)
    return sent


def test_empty_optional_normalization_is_logged_without_content_change(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    value = graph(); value['empty_reason'] = ''
    sequence(monkeypatch, provider, [value])
    result = calls.extract_paper(papers[0])
    assert [i.text for i in result.items] == [i['text'] for i in value['items']]
    events = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'extraction_normalized']
    assert events and events[0]['changes'] == [{'path': '/empty_reason', 'operation': 'remove_empty_optional'}]
    raw = next(e['response'] for e in calls.log.read() if e['label'] == 'MODEL')
    assert json.loads(json.loads(raw)['content'][0]['text'])['empty_reason'] == ''


def test_two_patches_keep_all_items_and_specific_page_feedback(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_targeted_corrections=2, extraction_require_inference=True)
    bad = graph(); bad['items'][0]['page_end'] = 3
    first = {**graph(), 'items': [copy.deepcopy(graph()['items'][0]),
                                  dict(graph()['items'][1], id='s', page_end=4)]}
    second = {**graph(), 'items': [dict(graph()['items'][1], id='s')]}
    sent = sequence(monkeypatch, provider, [bad, first, second])
    result = calls.extract_paper(papers[0])
    assert len(sent) == 3 and len(result.items) == 9
    assert any(i.id.endswith(':s') for i in result.items)
    assert len(sent[2]['candidate']['items']) == 9
    assert sent[2]['candidate']['items'][0]['page_end'] == 1
    for request in sent[1:]:
        assert request['valid_page_bounds'] == {'paper_start': 1, 'paper_end': 2, 'readable_pages': [1, 2]}
        assert 'outside paper' in request['validation_error']
    events = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'extraction_targeted_correction']
    assert [e['correction'] for e in events] == [1, 2]
    assert len([e for e in calls.log.read() if e['stage'] == 'extraction_paper_attempt']) == 3


@pytest.mark.parametrize('defect', ['attribution', 'disposition', 'reference', 'inference'])
def test_semantic_errors_are_not_normalized_away(rig, monkeypatch, defect):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_targeted_corrections=2, extraction_require_inference=True)
    value = graph()
    if defect == 'attribution': value['items'][0]['attributed_to'] = ''
    if defect == 'disposition': value['empty_reason'] = 'P'
    if defect == 'reference': value['items'][-1]['premise_ids'] = ['unknown']
    if defect == 'inference': value['items'][-1]['inference_origin'] = None
    sent = sequence(monkeypatch, provider, [value])
    with pytest.raises(Rejected): calls.extract_paper(papers[0])
    assert len(sent) == 3
    assert not list(calls.cache.path.glob('*.json'))


def test_second_correction_respects_paper_allowance(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_targeted_corrections=2, extraction_paper_continuation_limit=1)
    bad = graph(); bad['items'][0]['page_end'] = 3
    sent = sequence(monkeypatch, provider, [bad])
    with pytest.raises(BudgetStop, match='paper continuation limit'):
        calls.extract_paper(papers[0])
    assert len(sent) == 2


@pytest.mark.parametrize('limit', [-1, True, 4, 1.5])
def test_invalid_correction_limit_refuses_before_dispatch(rig, monkeypatch, limit):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = limit
    sent = sequence(monkeypatch, provider, [graph()])
    with pytest.raises(ValueError, match='extraction_targeted_corrections'):
        calls.extract_paper(papers[0])
    assert sent == []


def test_provider_wire_cannot_mix_disposition_and_content(rig):
    calls, _, papers, *_ = rig
    schema = structured_schema(calls.response_schema('extract_paper', papers[0].inputs()))
    value = graph()
    for item in value['items']:
        if item['kind'] != 'inference':
            for name in ('premise_ids', 'conclusion_id', 'qualification_ids', 'inference_origin'):
                del item[name]
        if item['kind'] not in ('distinction', 'qualification'):
            del item['applies_to']
    validator = Draft202012Validator(schema)
    assert validator.is_valid(value)
    assert validator.is_valid({**value, 'empty_reason': None})
    assert not validator.is_valid({**value, 'empty_reason': 'P'})
    assert validator.is_valid({**value, 'items': None, 'empty_reason': 'P'})
    assert not validator.is_valid({**value, 'items': []})
    assert not validator.is_valid({**value, 'items': [None], 'empty_reason': 'P'})


def test_initial_wire_satisfies_provider_sdk_schema_contract(rig):
    from anthropic import transform_schema
    calls, _, papers, *_ = rig
    wire = structured_schema(calls.response_schema('extract_paper', papers[0].inputs()))
    # The SDK rejects typeless constraint-only branches before service dispatch.
    transformed = transform_schema(wire)
    assert transformed
    assert not {'type', 'properties', 'required', 'additionalProperties'} & wire.keys()
    for alternative in wire['anyOf']:
        assert alternative['type'] == 'object'
        assert alternative['additionalProperties'] is False
        assert alternative['properties']['items']['type'] in ('array', 'null')


def test_extraction_counter_includes_expanded_provider_envelope(rig):
    from types import SimpleNamespace
    from ara.runtime.cache import canonical
    from ara.runtime.providers import AnthropicProvider
    calls, _, papers, *_ = rig
    counted = []
    def count_tokens(**request):
        counted.append(request)
        return SimpleNamespace(input_tokens=100)
    provider = AnthropicProvider(calls.config, SimpleNamespace(messages=SimpleNamespace(count_tokens=count_tokens)))
    schema = calls.response_schema('extract_paper', papers[0].inputs())
    wire = provider.request('extract_paper', 'P', schema, 32000)['output_config']['format']['schema']
    provider.estimate('extract_paper', 'P', schema, 32000)
    assert counted[0]['messages'][0]['content'] == 'P' + canonical(wire)


def test_null_empty_inventory_normalized_with_original_preserved(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    value = {**graph(), 'items': None, 'empty_reason': 'P'}
    sequence(monkeypatch, provider, [value])
    result = calls.call('extract_paper', papers[0].inputs())
    assert result['items'] == [] and result['empty_reason'] == 'P'
    models = [e for e in calls.log.read() if e['label'] == 'MODEL']
    assert json.loads(json.loads(models[0]['response'])['content'][0]['text'])['items'] is None
    events = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'extraction_normalized']
    assert events[0]['changes'] == [{'path': '/items', 'operation': 'null_empty_inventory_to_array'}]


@pytest.mark.parametrize('failed_patches', [0, 1, 2])
def test_rejected_null_inventory_recovers_within_correction_limit(rig, monkeypatch, failed_patches):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_targeted_corrections=2, extraction_require_inference=True)
    empty = {**graph(), 'items': None, 'empty_reason': ''}
    bad = graph(); bad['items'][0]['page_end'] = 3
    sent = sequence(monkeypatch, provider, [empty] + [bad] * failed_patches + [graph()])
    if failed_patches == 2:
        with pytest.raises(Rejected):
            calls.extract_paper(papers[0])
        assert len(sent) == 3
    else:
        result = calls.extract_paper(papers[0])
        assert len(result.items) == len(graph()['items'])
        assert len(sent) == 2 + failed_patches
    assert sent[1]['candidate']['items'] == []
    assert 'empty_reason' not in sent[1]['candidate']
    models = [e for e in calls.log.read() if e['label'] == 'MODEL']
    assert json.loads(json.loads(models[0]['response'])['content'][0]['text']) == empty
    events = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'extraction_normalized']
    recovery = [e for e in events if e.get('phase') == 'correction_candidate']
    assert recovery[0]['changes'] == [
        {'path': '/items', 'operation': 'null_empty_inventory_to_array'},
        {'path': '/empty_reason', 'operation': 'remove_empty_optional'}]
    assert recovery[0]['attempt'] == 1


@pytest.mark.parametrize('identity', [None, '', 1])
def test_rejected_candidate_ambiguous_ids_still_refuse(rig, monkeypatch, identity):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_targeted_corrections=2)
    bad = graph()
    bad['items'][0]['id'] = identity
    sent = sequence(monkeypatch, provider, [bad, graph()])
    with pytest.raises(Rejected):
        calls.extract_paper(papers[0])
    assert len(sent) == 1
