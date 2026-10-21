"""Placeholder-only accounting, diagnostics and grammar gate boundaries."""
import json
from decimal import Decimal

import httpx2 as httpx
import pytest
from anthropic import BadRequestError

from ara.runtime.budget import Budget, BudgetStop
from ara.runtime.export import methodology
from ara.runtime.providers import Response
from ara.types import Proposition, TokenUsage
from test_calls import rig, response


def test_explicit_unknown_reconciliation(rig):
    calls, provider, log = rig
    with pytest.raises(BudgetStop):
        calls.formalise(Proposition('p', 'P'))
    originals = log.read()
    cost = calls.budget.used_cost
    config = {**calls.config, 'unknown_usage_policy': 'count-at-reservation'}
    resumed = Budget(config, log)
    assert resumed.used_cost == cost > 0
    assert log.read()[:len(originals)] == originals
    marker = json.loads(log.read()[-1]['payload_json'])
    assert marker['policy'] == 'count-at-reservation'
    assert Decimal(str(marker['upper_bound_usd'])) == cost
    assert len(marker['receipt_ids']) == 1
    report = json.loads(methodology(log.path).split('```json\n')[1].split('\n```')[0])
    assert report['measured_usage']['cost_usd'] == 0
    assert report['unknown_usage_reservations']['cost_usd'] == float(cost)
    assert 'unknown usage, counted at reservation' in report['accounting_note']
    assert report['accounting_complete'] is False
    config['cost_cap_usd'] = float(cost)
    with pytest.raises(BudgetStop, match='cost cap'):
        Budget(config, log).before(TokenUsage(1, 1), 'extract_paper')


def test_reconciliation_does_not_clear_unreceipted_dispatch(rig):
    calls, _, log = rig
    log.record('call_start')
    with pytest.raises(BudgetStop, match='interrupted provider call'):
        Budget({**calls.config, 'unknown_usage_policy': 'count-at-reservation'}, log)


def test_provider_error_evidence_sanitized(rig, monkeypatch):
    calls, provider, log = rig
    secret = 'sk-ant-placeholder-secret'
    monkeypatch.setenv('ANTHROPIC_API_KEY', secret)
    def fail(*args):
        raise BadRequestError('unsafe wrapper ' + secret,
            response=httpx.Response(400, request=httpx.Request('POST', 'https://example.invalid'),
                                    headers={'request-id': 'req_P'}),
            body={'error': {'type': 'invalid_request_error',
                'message': 'Schema grammar rejected. Authorization: Bearer ' + secret +
                           '\nrequest body: {"messages": ["P"]}'}})
    monkeypatch.setattr(provider, 'complete', fail)
    with pytest.raises(BudgetStop):
        calls.formalise(Proposition('p', 'P'))
    evidence = [json.loads(e['payload_json']) for e in log.read() if e['stage'] == 'provider_error']
    assert len(evidence) == 1
    assert evidence[0]['http_status'] == 400
    assert evidence[0]['error_type'] == 'invalid_request_error'
    assert evidence[0]['request_id'] == 'req_P'
    assert 'Schema grammar rejected.' in evidence[0]['message']
    assert secret not in log.path.read_text()
    assert '"messages"' not in evidence[0]['message']


def test_schema_gate_native_wires_and_cost(rig, monkeypatch):
    from ara.runtime.preflight import schema_preflight
    from ara.runtime.providers import structured_schema
    calls, provider, log = rig
    sent = []
    def complete(kind, prompt, schema, maximum):
        sent.append((kind, prompt, structured_schema(schema), maximum))
        return Response(response({}, stop_reason='max_tokens'))
    monkeypatch.setattr(provider, 'complete', complete)
    report = schema_preflight(calls)
    assert report['passed'] and report['distinct_schemas'] == 5
    assert len(sent) == 5
    assert all(kind == 'extract_paper' and maximum == 1 and len(prompt) < 200
               for kind, prompt, _, maximum in sent)
    assert len({json.dumps(wire, sort_keys=True) for _, _, wire, _ in sent}) == 5
    assert all(len((wire['anyOf'][0] if 'anyOf' in wire else wire)['properties']['items']['items']['anyOf']) == 3
               for _, _, wire, _ in sent)
    assert calls.budget.used_cost > 0
    assert len([e for e in log.read() if e['label'] == 'MODEL']) == 5
    assert not list(calls.cache.path.glob('*.json'))


def test_schema_gate_cap_refuses_dispatch(rig, monkeypatch):
    from ara.runtime.preflight import schema_preflight
    calls, provider, log = rig
    calls.config['cost_cap_usd'] = 0
    with pytest.raises(BudgetStop):
        schema_preflight(calls)
    assert provider.calls == 0


def test_native_preflight_cli_reimports_gate_charges(rig, tmp_path, monkeypatch):
    import yaml
    from ara.runtime.cli import main
    from ara.runtime.calls import ModelCalls
    from ara.runtime.cache import Cache
    calls, provider, log = rig
    monkeypatch.setattr(provider, 'complete', lambda *args: Response(response({}, stop_reason='max_tokens')))
    config = {**calls.config, 'extraction-full': {}}
    path = tmp_path / 'config.yaml'
    path.write_text(yaml.safe_dump(config))
    made = []
    def factory(config, log, topic):
        result = ModelCalls(config, provider, log, Cache(tmp_path / 'cache2'), calls.root, topic)
        made.append(result)
        return result
    first, second = tmp_path / 'gate1', tmp_path / 'gate2'
    common = ['schema-preflight', '--config', str(path)]
    assert main(common + ['--run-dir', str(first)], calls_factory=factory) == 0
    assert main(common + ['--run-dir', str(second), '--resume-from', str(first)], calls_factory=factory) == 0
    assert made[1].budget.used_cost == made[0].budget.used_cost * 2
    assert main(common + ['--run-dir', str(tmp_path / 'bad'), '--cost-cap-usd', '1.01'], calls_factory=factory) == 2
