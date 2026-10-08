import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml
from jsonschema import Draft202012Validator

from ara.runtime.calls import Rejected
from ara.runtime.providers import AnthropicProvider, structured_schema
from ara.types import Proposition, TokenUsage
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
            return SimpleNamespace(to_dict=lambda: response({'formula': {'op': 'atom', 'name': 'P'}}))
        def count_tokens(self, **kwargs):
            counts.append(kwargs)
            return SimpleNamespace(input_tokens=10)
    provider = AnthropicProvider(calls.config, SimpleNamespace(messages=Messages()))
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
    Draft202012Validator(projected).validate({'formula': {'op': 'atom', 'name': 'P'}})


@pytest.mark.skipif(not os.environ.get('ANTHROPIC_API_KEY'), reason='ANTHROPIC_API_KEY absent: real-provider path unexecuted')
@pytest.mark.skipif(os.environ.get('ARA_LIVE_TEST') != '1', reason='live network opt-in ARA_LIVE_TEST=1 required; offline suite only')
def test_real_provider_path(tmp_path):
    from ara.runtime.cache import Cache
    from ara.runtime.calls import ModelCalls
    from ara.runtime.logging import EventLog
    config = yaml.safe_load((ROOT / 'config.yaml').read_text())
    calls = ModelCalls(config, AnthropicProvider(config), EventLog(tmp_path / 'events.jsonl'),
                       Cache(tmp_path / 'cache'), ROOT, 'P')
    formula = calls.formalise(Proposition('p', 'P'))
    assert formula.op == 'atom' and formula.name == 'P'
