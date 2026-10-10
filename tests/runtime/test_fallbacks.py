"""B11 routing and B9 accounting, provenance and final-refusal contracts, without network."""
import json
from types import SimpleNamespace

import pytest

from ara.runtime.budget import Budget, BudgetStop
from ara.runtime.calls import Rejected
from ara.runtime.export import methodology
from ara.runtime.providers import AnthropicProvider
from ara.types import Proposition
from test_calls import rig, register, response, graph


@pytest.mark.parametrize('mode', ['explicit', 'implicit', 'off'])
def test_fallback_request_shape(rig, mode):
    calls, _, _ = rig
    if mode == 'implicit':
        calls.config.pop('fallbacks', None)
    else:
        calls.config['fallbacks'] = ['claude-opus-4-8'] if mode == 'explicit' else mode
    requests = []
    def create(**kwargs):
        requests.append(kwargs)
        return SimpleNamespace(to_dict=lambda **kwargs: response({}))
    # Only the beta endpoint is exposed, so ordinary messages.create cannot pass.
    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(create=create)))
    AnthropicProvider(calls.config, client).complete('formalise', 'P', None, 32)
    request = requests[0]
    assert request['model'] == 'claude-opus-5'
    if mode != 'off':
        assert request['betas'] == ['server-side-fallback-2026-06-01']
        assert request['fallbacks'] == [{'model': 'claude-opus-4-8'}]
    else:
        assert 'betas' not in request and 'fallbacks' not in request


def fallback_response(*, iterations=True, boundary=True):
    raw = response({'formula': {'op': 'atom', 'name': 'P'}}, model='claude-opus-4-8')
    if boundary:
        raw['content'][:0] = [
            {'type': 'text', 'text': 'Q'},
            {'type': 'fallback', 'from': {'model': 'claude-opus-5'},
             'to': {'model': 'claude-opus-4-8'}},
        ]
    if iterations:
        raw['usage'] = {'input_tokens': 30, 'output_tokens': 7,
                        'server_tool_use': {'web_search_requests': 1},
                        'iterations': [
                            {'type': 'message', 'model': 'claude-opus-5',
                             'input_tokens': 10, 'output_tokens': 2},
                            {'type': 'fallback_message', 'model': 'claude-opus-4-8',
                             'input_tokens': 20, 'output_tokens': 5},
                        ]}
    return raw


@pytest.mark.parametrize('iterations,boundary', [(True, True), (True, False), (False, True)])
def test_fallback_billing_logging_and_methodology(rig, iterations, boundary):
    calls, provider, log = rig
    # Deliberately distinct fixture rates detect requested-model mispricing.
    calls.config['pricing']['claude-opus-4-8'].update(
        input_per_million_usd=2, output_per_million_usd=8)
    raw = fallback_response(iterations=iterations, boundary=boundary)
    p = Proposition('p', 'P')
    register(calls, provider, 'formalise', {'proposition': p.to_dict()}, {}, **raw)
    assert calls.formalise(p).name == 'P'
    event = log.read()[-1]
    payload = json.loads(event['payload_json'])
    assert event['model_id'] == 'claude-opus-5'
    assert event['model_version'] == payload['served_model'] == 'claude-opus-4-8'
    assert payload['requested_model'] == 'claude-opus-5'
    assert payload['fallback_used'] is True
    assert payload['fallback_blocks'] == ([raw['content'][1]] if boundary else [])
    assert payload['fallback_iterations'] == (raw['usage']['iterations'][1:] if iterations else [])
    assert event['usage']['input_tokens'] == (30 if iterations else 5)
    assert event['usage']['output_tokens'] == (7 if iterations else 3)
    assert event['usage']['server_tool_uses'] == (1 if iterations else 0)
    assert event['cost_usd'] == pytest.approx(.01018 if iterations else .000034)
    report = methodology(log.path)
    summary = json.loads(report.split('```json\n')[1].split('\n```')[0])
    assert summary['served_models_by_kind'] == {'formalise': ['claude-opus-4-8']}
    assert summary['fallback_calls'][0]['served_model'] == 'claude-opus-4-8'
    assert 'Server-side fallback served calls: formalise → claude-opus-4-8' in report
    provider.responses.clear()
    assert calls.formalise(p).name == 'P'
    assert provider.calls == 1
    assert log.read()[-1]['cost_usd'] == 0


@pytest.mark.parametrize('missing', ['served', 'iteration'])
def test_unpriced_model_stops_loudly(rig, missing):
    calls, provider, log = rig
    raw = fallback_response()
    if missing == 'served':
        raw['model'] = 'unpriced'
    else:
        raw['usage']['iterations'][0]['model'] = 'unpriced'
    p = Proposition('p', 'P')
    register(calls, provider, 'formalise', {'proposition': p.to_dict()}, {}, **raw)
    with pytest.raises(BudgetStop, match='unpriced served model: unpriced'):
        calls.formalise(p)
    event = next(e for e in log.read() if e['label'] == 'MODEL')
    assert event['cost_usd'] > 0
    assert json.loads(event['payload_json'])['accounting'] == 'reservation_unknown_actual'
    assert log.read()[-1]['label'] == 'STOP'
    assert not list(calls.cache.path.glob('*.json'))
    assert provider.calls == 1


def test_final_fallback_refusal_is_not_retried(rig):
    calls, provider, log = rig
    calls.config['validation_attempts'] = 3
    draft = {'title': 'P', 'body': '[[node:n1]] P', 'bibliography': []}
    raw = fallback_response()
    raw['stop_reason'] = 'refusal'
    # Valid audit content cannot override a whole-chain refusal.
    raw['content'][-1]['text'] = json.dumps({'labels': [{'sentence': 1, 'node_ids': ['n1'],
                                            'asserts_premise_or_inference_not_in_outline': False}]})
    register(calls, provider, 'audit_essay', calls.audit_inputs(graph(), draft), {}, **raw)
    with pytest.raises(Rejected, match='provider stop: refusal'):
        calls.audit_essay(graph(), draft)
    assert provider.calls == 1
    assert not any(e['stage'] == 'validation_retry' for e in log.read())
    event = next(e for e in log.read() if e['label'] == 'MODEL')
    assert json.loads(event['payload_json'])['status'] == 'rejected'
    assert event['cost_usd'] > 0
    assert not list(calls.cache.path.glob('*.json'))


@pytest.mark.parametrize('rate', [-1, float('nan')])
def test_fallback_rates_are_validated(rig, rate):
    calls, _, log = rig
    calls.config['pricing']['claude-opus-4-8']['input_per_million_usd'] = rate
    with pytest.raises(ValueError, match='pricing must be finite and nonnegative'):
        Budget(calls.config, log)


def test_ambiguous_iteration_model_stops(rig):
    calls, provider, _ = rig
    raw = fallback_response()
    del raw['usage']['iterations'][0]['model']
    p = Proposition('p', 'P')
    register(calls, provider, 'formalise', {'proposition': p.to_dict()}, {}, **raw)
    with pytest.raises(BudgetStop, match='missing model in fallback usage iteration'):
        calls.formalise(p)


@pytest.mark.parametrize('mode', ['default', [], [''], [1], None, True, 'claude-opus-4-8'])
def test_invalid_fallback_config_is_rejected(rig, mode):
    calls, _, _ = rig
    calls.config['fallbacks'] = mode
    with pytest.raises(ValueError, match='nonempty list of model ids or off'):
        AnthropicProvider(calls.config, SimpleNamespace())


def test_explicit_fallback_through_provider_and_calls(rig):
    calls, _, log = rig
    requests = []
    raw = fallback_response()
    calls.config['pricing']['claude-opus-4-8'].update(input_per_million_usd=2, output_per_million_usd=8)
    def create(**kwargs):
        requests.append(kwargs)
        return SimpleNamespace(to_dict=lambda **kwargs: raw)
    client = SimpleNamespace(messages=SimpleNamespace(count_tokens=lambda **kwargs: SimpleNamespace(input_tokens=10)),
        beta=SimpleNamespace(messages=SimpleNamespace(create=create)))
    calls.provider = AnthropicProvider(calls.config, client)
    assert calls.formalise(Proposition('p', 'P')).name == 'P'
    assert len(requests) == 1
    assert requests[0]['fallbacks'] == [{'model': 'claude-opus-4-8'}]
    event = next(e for e in log.read() if e['label'] == 'MODEL')
    payload = json.loads(event['payload_json'])
    assert payload['status'] == 'accepted' and payload['served_model'] == 'claude-opus-4-8'
    assert event['model_id'] == 'claude-opus-5' and event['model_version'] == 'claude-opus-4-8'
    assert payload['fallback_blocks'] == [raw['content'][1]]
    assert payload['fallback_iterations'] == raw['usage']['iterations'][1:]
    assert event['usage']['input_tokens'] == 30 and event['usage']['output_tokens'] == 7
    assert event['cost_usd'] == pytest.approx(.01018)
    summary = json.loads(methodology(log.path).split('```json\n')[1].split('\n```')[0])
    assert summary['served_models_by_kind'] == {'formalise': ['claude-opus-4-8']}
    assert summary['fallback_calls'][0]['served_model'] == 'claude-opus-4-8'


def test_fallback_mode_partitions_cache(rig):
    calls, provider, log = rig
    p = Proposition('p', 'P')
    register(calls, provider, 'formalise', {'proposition': p.to_dict()},
             {'formula': {'op': 'atom', 'name': 'P'}})
    calls.formalise(p)
    calls.config['fallbacks'] = 'off'
    calls.formalise(p)
    assert provider.calls == 2
    calls.config.pop('fallbacks')
    calls.formalise(p)
    assert provider.calls == 2  # implicit B11 list shares the explicit-list cache
    assert json.loads(log.read()[-1]['payload_json'])['cache_hit']
