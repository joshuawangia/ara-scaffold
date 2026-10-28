"""Search publication order and durable failure accounting on placeholders."""
from fixture_support import api_fixture_config
from threading import Event
import hashlib
import json

import pytest
import yaml

from ara.bank import Bank
from ara.engine import Engine
from ara.runtime.budget import Budget, BudgetStop
from ara.runtime.cache import Cache
from ara.runtime.calls import ModelCalls
from ara.runtime.export import methodology
from ara.runtime.logging import EventLog
from ara.runtime.orchestration import NativeEngine, search_all
from ara.runtime.providers import MockProvider, Response
from ara.types import CommitmentSet, Formula, Proposition, negate_proposition
from test_calls import ROOT, response


def test_native_publication_order_under_reversed_schedule(tmp_path, monkeypatch):
    targets = tuple(Proposition(n.lower(), n, Formula('atom', name=n)) for n in ('P', 'Q'))
    goals = [g for t in targets for g in (t, negate_proposition(t))]
    expected = [hashlib.sha256(g.formula.canonical().encode()).hexdigest()[:12] + f':{i % 2}'
                for i, g in enumerate(goals)]
    native_search = Engine.search
    signatures = []
    for concurrency, reverse in ((1, False), (4, False), (4, True)):
        config = api_fixture_config()
        config['search_concurrency'] = concurrency
        log = EventLog(tmp_path / f'{concurrency}-{reverse}' / 'events.jsonl')
        provider = MockProvider({})
        monkeypatch.setattr(provider, 'complete', lambda kind, *a: Response(response(
            {'t_id': 'open'} if kind == 'map_leaf' else {'proposals': []})))
        gates = [Event() for _ in range(5)]
        gates[0].set()
        completed = []
        def scheduled(engine, goal):
            index = goals.index(goal)
            rank = 3 - index if reverse else index
            assert gates[rank].wait(10)
            try:
                result = native_search(engine, goal)
                completed.append(index)
                return result
            finally:
                gates[rank + 1].set()
        monkeypatch.setattr(Engine, 'search', scheduled)
        calls = ModelCalls(config, provider, log, Cache(log.path.parent / 'cache'), ROOT, 'P')
        search_all(calls, NativeEngine(Bank('1', ()), calls), CommitmentSet(()), targets)
        assert completed == (list(reversed(range(4))) if reverse else list(range(4)))
        events = log.read()
        receipts = [json.loads(e['payload_json'])['search_id'] for e in events if e['stage'] == 'search_trace_receipt']
        assert receipts == expected
        # Covers engine/model events as well as sidecar/result receipts, excluding
        # timestamps, generated filenames and response timings from the order key.
        signatures.append([(e['stage'], e['label'], (e['decision'] or {}).get('reason_code'),
                            json.loads(e['payload_json']).get('job_index')) for e in events])
    assert signatures[0] == signatures[1] == signatures[2]


def test_unpublished_accounting_is_durable_and_refuses_resume(tmp_path):
    from ara.runtime.logging import SerializedEventLog
    from ara.runtime.search_publication import SearchPublication
    from ara.types import RunEvent, TokenUsage
    config = api_fixture_config()
    log = EventLog(tmp_path / 'events.jsonl')
    goal = Proposition('p', 'P', Formula('atom', name='P'))
    with SerializedEventLog(log) as writer:
        publication = SearchPublication(writer, [goal])
        def work(_):
            writer.record('call_start', reserved_usage=TokenUsage(5, 3).to_dict())
            writer.emit(RunEvent('2026-10-23T00:00:00+00:00', 'formalise', 'MODEL',
                                usage=TokenUsage(5, 3), cost_usd=.001,
                                payload_json='{"cache_hit":false,"accounting":"actual"}'))
        publication.run(0, work, goal)
        assert not any(e['label'] == 'MODEL' for e in log.read())
        journal = EventLog(publication.journals[0].path).read()
        assert sum(e['usage']['input_tokens'] for e in journal) == 5
        summary = json.loads(methodology(log.path).split('```json\n')[1].split('\n```')[0])
        assert not summary['accounting_complete'] and summary['unpublished_search_batches']
        with pytest.raises(BudgetStop, match='unpublished search accounting'):
            Budget(config, log)
        publication.publish()
    restored = Budget(config, log)
    assert restored.used_tokens == 8
    assert float(restored.used_cost) == .001
    assert len([e for e in log.read() if e['label'] == 'MODEL']) == 1


def test_search_failure_publishes_durable_accounting(tmp_path, monkeypatch):
    config = api_fixture_config()
    config['search_concurrency'] = 1
    log = EventLog(tmp_path / 'events.jsonl')
    provider = MockProvider({})
    def fail(*args):
        raise OSError('P')
    monkeypatch.setattr(provider, 'complete', fail)
    calls = ModelCalls(config, provider, log, Cache(tmp_path / 'cache'), ROOT, 'P')
    target = Proposition('p', 'P', Formula('atom', name='P'))
    with pytest.raises(BudgetStop):
        search_all(calls, NativeEngine(Bank('1', ()), calls), CommitmentSet(()), (target,))
    events = log.read()
    assert any(e['stage'] == 'search_job_failed' for e in events)
    models = [e for e in events if e['label'] == 'MODEL']
    assert len(models) == 1
    assert json.loads(models[0]['payload_json'])['accounting'] == 'reservation_unknown_actual'
    assert calls.budget.used_tokens == sum(sum(e['usage'][k] for k in ('input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_write_tokens')) for e in models)
    assert any(e['stage'] == 'search_publication_finished' for e in events)
    phase = next(json.loads(e['payload_json']) for e in events if e['stage'] == 'search_phase_finished')
    assert phase['status'] == 'stopped'
    assert calls.log is calls.budget.log is log
