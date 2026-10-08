"""Post-dispatch failures retain conservative, visibly incomplete accounting."""
import json
from datetime import datetime, timezone

import pytest

from ara.runtime.budget import Budget, BudgetStop, tokens
from ara.runtime.export import methodology
from ara.runtime.providers import Response
from ara.types import Proposition, TokenUsage
from test_calls import rig, response


@pytest.mark.parametrize('failure', ['serialization', 'logging', 'parse'])
def test_dispatched_failure_is_incomplete(rig, monkeypatch, failure):
    calls, provider, log = rig
    calls.config['validation_attempts'] = 3
    raw = response({'formula': {'op': 'atom', 'name': 'P'}})
    if failure == 'serialization':
        raw['container'] = {'expires_at': datetime.now(timezone.utc)}
    elif failure == 'parse':
        raw['content'][0]['text'] = '{'
    else:
        emit = log.emit
        def fail_once(event):
            if event.label == 'MODEL':
                monkeypatch.setattr(log, 'emit', emit)
                raise OSError('P')
            emit(event)
        monkeypatch.setattr(log, 'emit', fail_once)
    def complete(*args):
        provider.calls += 1
        return Response(raw)
    monkeypatch.setattr(provider, 'complete', complete)
    with pytest.raises(BudgetStop, match='actual spend unknown'):
        calls.formalise(Proposition('p', 'P'))
    events = log.read()
    admission = json.loads(next(e['payload_json'] for e in events if e['stage'] == 'call_start'))
    reservation = TokenUsage.from_dict(admission['reserved_usage'])
    models = [e for e in events if e['label'] == 'MODEL']
    assert len(models) == 1 and provider.calls == 1
    event = models[0]
    payload = json.loads(event['payload_json'])
    assert payload['status'] == 'incomplete'
    assert payload['accounting'] == 'reservation_unknown_actual'
    assert event['usage'] == reservation.to_dict()
    assert event['cost_usd'] == float(calls.budget.cost(reservation))
    assert calls.budget.used_tokens == tokens(reservation)
    assert calls.budget.used_cost == calls.budget.cost(reservation)
    assert events[-1]['label'] == 'STOP'
    assert not list(calls.cache.path.glob('*.json'))
    summary = json.loads(methodology(log.path).split('```json\n')[1].split('\n```')[0])
    assert summary['accounting_complete'] is False and summary['incomplete_calls'] == 1
    assert summary['unknown_spend_reservations_usd'] == event['cost_usd']
    assert 'INCOMPLETE' in summary['accounting_note']
    with pytest.raises(BudgetStop, match='prior provider spend is unknown'):
        Budget(calls.config, log)


def test_unknown_reservation_runs_post_call_cap_check(rig, monkeypatch):
    calls, provider, log = rig
    def complete(*args):
        calls.config['cost_cap_usd'] = 0
        raise OSError('P')
    monkeypatch.setattr(provider, 'complete', complete)
    with pytest.raises(BudgetStop, match='cost cap exceeded'):
        calls.formalise(Proposition('p', 'P'))
    assert calls.budget.used_cost > 0
    assert json.loads(log.read()[-1]['payload_json'])['cost_usd'] == float(calls.budget.used_cost)


def test_outstanding_dispatch_export_never_looks_complete(rig):
    calls, _, log = rig
    log.record('call_start', reserved_usage=TokenUsage(1, 2).to_dict())
    summary = json.loads(methodology(log.path).split('```json\n')[1].split('\n```')[0])
    assert summary['accounting_complete'] is False
    assert summary['unresolved_dispatches'] == summary['incomplete_calls'] == 1
    with pytest.raises(BudgetStop, match='interrupted provider call'):
        Budget(calls.config, log)
