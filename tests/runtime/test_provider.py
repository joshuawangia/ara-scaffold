import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from jsonschema import Draft202012Validator

from ara.runtime.calls import Rejected
from ara.runtime.providers import AnthropicProvider, structured_schema
from ara.types import Formula, Proposition, TokenUsage
from test_calls import ROOT, rig, register, response


@pytest.mark.parametrize('reason', ['refusal', 'max_tokens', 'pause_turn', 'tool_use'])
def test_stop_reasons_logged_rejected(rig, reason):
    calls, provider, log = rig
    p = Proposition('p', 'P')
    register(calls, provider, 'formalise', {'proposition': p.to_dict()}, {}, stop_reason=reason,
             content=[{'type': 'text', 'text': 'not JSON'}])
    with pytest.raises(Rejected, match=reason):
        calls.formalise(p)
    assert json.loads(log.read()[-1]['response'])['stop_reason'] == reason
    assert not list(calls.cache.path.glob('*.json'))


@pytest.mark.parametrize('error', [{'type': 'web_search_tool_result_error', 'error_code': 'unavailable'},
                                   [{'type': 'web_search_tool_result_error', 'error_code': 'unavailable'}]])
def test_server_error_blocks_rejected(rig, error):
    calls, provider, log = rig
    register(calls, provider, 'search_evidence', {'draft': {}, 'items': []}, {},
             content=[{'type': 'web_search_tool_result', 'content': error}])
    with pytest.raises(Rejected, match='server tool error'):
        calls.search_evidence({}, [])


def test_anthropic_sdk_request_shapes_and_accounting(rig):
    calls, _, _ = rig
    requests = []
    counts = []
    class Messages:
        def create(self, **kwargs):
            requests.append(kwargs)
            return SimpleNamespace(to_dict=lambda **kwargs: response({'formula': {'op': 'atom', 'name': 'P'}}))
        def count_tokens(self, **kwargs):
            counts.append(kwargs)
            return SimpleNamespace(input_tokens=10)
    provider = AnthropicProvider(calls.config, SimpleNamespace(messages=Messages(), beta=SimpleNamespace(messages=Messages())))
    schema = json.loads((ROOT / 'schemas/formalise.json').read_text())
    estimate = provider.estimate('formalise', 'P', schema, 32)
    assert estimate == TokenUsage(10, 32)
    provider.complete('formalise', 'P', schema, 32)
    request = requests[-1]
    assert request['thinking'] == {'type': 'adaptive'}
    assert request['messages'] == [{'role': 'user', 'content': 'P'}]
    assert request['output_config']['format']['type'] == 'json_schema'
    provider.complete('search_evidence', 'Q', None, 32)
    request = requests[-1]
    assert 'format' not in request['output_config']
    assert request['tools'] == [{'type': 'web_search_20260209', 'name': 'web_search', 'max_uses': 5}]
    assert request['messages'] == [{'role': 'user', 'content': 'Q'}]
    usage = TokenUsage(10, 20, 30, 40, 2)
    assert float(calls.budget.cost(usage, {'cache_creation': {'ephemeral_5m_input_tokens': 10,
                                                            'ephemeral_1h_input_tokens': 30}})) == pytest.approx(.0209275)


def test_projected_schema_is_acyclic_and_local_validation_is_stricter():
    schema = json.loads((ROOT / 'schemas/formalise.json').read_text())
    projected = structured_schema(schema, 2)
    Draft202012Validator.check_schema(projected)
    defs = projected['$defs']
    def visit(value, chain=()):
        if isinstance(value, dict):
            if '$ref' in value:
                key = value['$ref'].split('/')[-1]
                assert key not in chain
                visit(defs[key], (*chain, key))
            for key, item in value.items():
                if key != '$defs':
                    visit(item, chain)
        elif isinstance(value, list):
            for item in value:
                visit(item, chain)
    visit(projected)
    Draft202012Validator(projected).validate({'formula': Formula('atom', name='P').to_dict()})


@pytest.mark.skipif(not os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('ARA_LIVE_TEST') != '1',
                    reason=('ANTHROPIC_API_KEY absent: real-provider path unexecuted'
                            if not os.environ.get('ANTHROPIC_API_KEY') else
                            'live network opt-in ARA_LIVE_TEST=1 required; offline suite only'))
def test_real_provider_path(tmp_path):
    from ara.runtime.cache import Cache
    from ara.runtime.calls import ModelCalls
    from ara.runtime.logging import EventLog
    config = yaml.safe_load((ROOT / 'config.yaml').read_text())
    calls = ModelCalls(config, AnthropicProvider(config), EventLog(tmp_path / 'events.jsonl'),
                       Cache(tmp_path / 'cache'), ROOT, 'P')
    formula = calls.formalise(Proposition('p', 'P'))
    assert formula.op == 'atom' and formula.name == 'P'


def test_live_observed_not_constraint_projected_but_locally_enforced():
    # Live HTTP 400: output_config.format.schema: keyword not is unsupported.
    schema = json.loads((ROOT / 'schemas/build_t.json').read_text())
    projected = structured_schema(schema)
    def assert_supported(node):
        if isinstance(node, dict):
            assert 'not' not in node
            for value in node.values():
                assert_supported(value)
        elif isinstance(node, list):
            for value in node:
                assert_supported(value)
    assert_supported(projected)
    Draft202012Validator.check_schema(projected)
    invalid = {'commitments': [{'id': 'open', 'text': 'P', 'citation': 'placeholder:1',
                               'formula': Formula('atom', name='P').to_dict()}]}
    # Projection accepts the omitted provider constraint; local schema refuses.
    Draft202012Validator(projected).validate(invalid)
    from jsonschema import ValidationError
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(invalid)


def test_compact_formula_projection_keeps_local_operator_checks():
    schema = json.loads((ROOT / 'schemas/formalise.json').read_text())
    projected = structured_schema(schema)
    invalid = {'formula': {'op': 'implies', 'args': [Formula('atom', name='P').to_dict()],
                           'name': None, 'terms': [], 'variable': None}}
    Draft202012Validator(projected).validate(invalid)
    from jsonschema import ValidationError
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate(invalid)
    # The server-rejected shape branches over every operator at every level.
    for level in range(3):
        assert len(projected['$defs'][f'formula_{level}'].get('anyOf', [])) <= 2


def test_compound_generation_cannot_omit_all_arguments():
    schema = structured_schema(json.loads((ROOT / 'schemas/formalise.json').read_text()))
    from jsonschema import ValidationError
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate({'formula': {'op': 'and', 'args': [],
                                                          'name': None, 'terms': [], 'variable': None}})
    compound = Formula('and', (Formula('atom', name='P'), Formula('atom', name='Q')))
    Draft202012Validator(schema).validate({'formula': compound.to_dict()})


def test_sdk_container_and_web_results_are_json_safe(rig):
    from anthropic.types.beta import BetaMessage
    from datetime import datetime
    calls, _, log = rig
    calls.config.update(token_cap=1000000, web_search_max_uses=1)
    message = BetaMessage.model_validate({
        'id': 'msg_P', 'type': 'message', 'role': 'assistant', 'model': calls.config['model'],
        'stop_reason': 'end_turn', 'stop_sequence': None,
        'container': {'id': 'P', 'expires_at': '2026-10-08T22:00:00Z'},
        'content': [{'type': 'text', 'text': 'P'},
                    {'type': 'web_search_tool_result', 'tool_use_id': 'P', 'content': [
                        {'type': 'web_search_result', 'title': 'P', 'url': 'https://example.org/P',
                         'encrypted_content': 'P', 'page_age': None}]}],
        'usage': {'input_tokens': 10, 'output_tokens': 5,
                  'server_tool_use': {'web_search_requests': 1, 'web_fetch_requests': 0}}})
    assert isinstance(message.to_dict()['container']['expires_at'], datetime)
    client = SimpleNamespace(messages=SimpleNamespace(count_tokens=lambda **kw: SimpleNamespace(input_tokens=1)),
        beta=SimpleNamespace(messages=SimpleNamespace(create=lambda **kw: message)))
    calls.provider = AnthropicProvider(calls.config, client)
    evidence = calls.search_evidence({}, [])
    assert evidence['urls'] == ['https://example.org/P']
    event = next(e for e in log.read() if e['label'] == 'MODEL')
    raw = json.loads(event['response'])
    assert isinstance(raw['container']['expires_at'], str)
    assert raw['content'][1]['content'][0]['url'] == evidence['urls'][0]
    assert event['usage']['server_tool_uses'] == 1
    assert event['cost_usd'] == pytest.approx(.010175)
    assert list(calls.cache.path.glob('*.json'))


@pytest.mark.parametrize('searches', [0, 1, 5])
def test_web_admission_counts_initial_request_and_bounds_search_iterations(rig, searches):
    calls, _, log = rig
    calls.config['web_search_max_uses'] = searches
    client = SimpleNamespace(messages=SimpleNamespace(
        count_tokens=lambda **kw: SimpleNamespace(input_tokens=123)))
    provider = AnthropicProvider(calls.config, client)
    estimate = provider.estimate('search_evidence', 'P', None, 32)
    assert estimate == TokenUsage(123 + searches * calls.config['model_context_token_bound'],
                                  32 * (searches + 1), server_tool_uses=searches)
