"""Placeholder concurrency proofs through the native runtime boundaries."""
from fixture_support import api_fixture_config
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event, Lock, get_ident
import json
import time

import pytest

from ara.runtime.budget import BudgetStop
from ara.runtime.calls import RequestCount
from ara.runtime.logging import EventLog, read_log
from ara.types import Proposition, TokenUsage
from test_calls import rig, response


def test_single_writer(tmp_path, monkeypatch):
    from ara.runtime.logging import SerializedEventLog
    log = EventLog(tmp_path / 'events.jsonl')
    writers = set()
    emit = log.emit_many
    def observed(events):
        writers.add(get_ident())
        emit(events)
    monkeypatch.setattr(log, 'emit_many', observed)
    with SerializedEventLog(log) as writer:
        with ThreadPoolExecutor(4) as pool:
            list(pool.map(lambda i: writer.record('P', index=i), range(24)))
        assert len(writer.read()) == 24
    assert len(writers) == 1 and get_ident() not in writers
    assert len(read_log(log.path)) == 24


def test_concurrent_admission_reserves_inflight(rig, monkeypatch):
    calls, provider, log = rig
    calls.config['token_cap'] = 15
    monkeypatch.setattr(calls, 'count_request', lambda *a, **k: RequestCount(5, 5, TokenUsage(5, 5)))
    entered, release = Event(), Event()
    dispatched = []
    def complete(*args):
        dispatched.append(args)
        entered.set()
        assert release.wait(5)
        return __import__('ara.runtime.providers', fromlist=['Response']).Response(
            response({'formula': {'op': 'atom', 'name': 'P'}}))
    monkeypatch.setattr(provider, 'complete', complete)
    with ThreadPoolExecutor(2) as pool:
        first = pool.submit(calls.formalise, Proposition('p', 'P'))
        assert entered.wait(5)
        second = pool.submit(calls.formalise, Proposition('q', 'Q'))
        try:
            with pytest.raises(BudgetStop, match='reservation'):
                second.result(timeout=2)
        finally:
            release.set()
        first.result()
    assert len(dispatched) == 1
    assert calls.budget.used_tokens == 8


def test_parallel_native_equivalence(tmp_path, monkeypatch):
    from ara.bank import Bank, load_bank
    from ara.engine import Engine
    from ara.runtime.cache import Cache
    from ara.runtime.calls import ModelCalls
    from ara.runtime.orchestration import NativeEngine, search_all
    from ara.runtime.providers import MockProvider, Response
    from ara.types import Commitment, CommitmentSet, Formula, PremiseFill, Proposal
    from test_calls import ROOT
    import yaml
    from itertools import combinations
    atoms = [Formula('atom', name=n) for n in ('P', 'Q', 'R', 'S')]
    forms = atoms + [Formula('iff', pair) for pair in combinations(atoms, 2)]
    targets = tuple(Proposition(f'p{i}', f.canonical(), f) for i, f in enumerate(forms))
    both = {f.canonical(): Formula('and', (f, f.negated())) for f in forms}
    table = CommitmentSet(tuple(Commitment(f't{i}', f.canonical(), f'placeholder:{i}', f)
                                for i, f in enumerate(both.values())))
    active = peak = 0
    orders = []
    completion_order = []
    schedule = {f.canonical(): i for i, f in enumerate(
        f for t in targets for f in (t.formula, t.formula.negated()))}
    lock = Lock()
    original_search = Engine.search
    def observed_search(engine, target):
        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
        try:
            index = schedule[target.formula.canonical()]
            if concurrency > 1:
                started.wait(timeout=60)
            result = original_search(engine, target)
            # Force a distinct finish order within each four-job window without
            # relying on host load or serializing the native search work.
            rank = index // 4 * 4 + (3 - index % 4 if reverse else index % 4)
            assert completed[rank].wait(60)
            with lock:
                completion_order.append(target.id)
            completed[rank + 1].set()
            return result
        finally:
            with lock:
                active -= 1
    monkeypatch.setattr(Engine, 'search', observed_search)
    results = []
    receipt_orders = []
    for concurrency, reverse in ((1, False), (4, False), (4, True)):
        peak = 0
        completion_order = []
        started = Barrier(concurrency)
        completed = [Event() for _ in range(21)]
        completed[0].set()
        directory = tmp_path / f'{concurrency}-{reverse}'
        config = api_fixture_config()
        config.update(search_concurrency=concurrency, forward_pass_depth=1, node_cap=100)
        log = EventLog(directory / 'events.jsonl')
        provider = MockProvider({})
        def complete(kind, prompt, schema, maximum):
            data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
            time.sleep(0.002 if reverse else 0.004)
            if kind == 'map_leaf':
                f = Formula.from_dict(data['leaf']['formula'])
                value = {'t_id': next((c.id for c in table.commitments if c.formula == f), 'open')}
            elif kind == 'propose_cuts':
                f = Formula.from_dict(data['goal']['formula'])
                positive = f.args[0] if f.op == 'not' else f
                premise = both[positive.canonical()]
                cut = Proposal('conjunction_elimination', (PremiseFill('conjunction', premise.canonical()),), f.canonical())
                value = {'proposals': [cut.to_dict()]}
            elif kind == 'formalise_slots':
                value = {'slots': [dict(slot=p['slot'], formula=json.loads(p['text']))
                                   for p in data['proposal']['premises']]}
            elif kind == 'formalise':
                value = {'formula': json.loads(data['proposition']['text'])}
            elif kind == 'tier1_repair':
                value = {'action': 'unresolved', 'detail': 'P', 'proposals': []}
            else:
                raise AssertionError(kind)
            return Response(response(value))
        monkeypatch.setattr(provider, 'complete', complete)
        calls = ModelCalls(config, provider, log, Cache(directory / 'cache'), ROOT, 'P')
        bank = load_bank(ROOT / 'bank')
        native = NativeEngine(Bank(bank.bank_version, (bank.get('conjunction_elimination'),)), calls)
        class Sequential:
            analyse = native.analyse
        routes = search_all(calls, Sequential() if concurrency == 1 else native, table, targets)
        events = log.read()
        analysis = json.loads(next(e['payload_json'] for e in events if e['stage'] == 'conflicts_and_robustness'))
        receipt_orders.append([json.loads(e['payload_json'])['search_id'] for e in events
                               if e['stage'] == 'search_trace_receipt'])
        traces = sorted(p.read_bytes() for p in (directory / 'search-traces').glob('*.jsonl'))
        assert len(traces) == 20
        assert all(a['tier1'] and a['tier2'] and a['forward'] for a in analysis['findings']['analyses'])
        assert peak == concurrency
        results.append((routes, analysis, traces))
        orders.append(completion_order)
    assert results[0] == results[1] == results[2]
    expected = [id for t in targets for id in (t.id, f'not:{t.id}')]
    assert orders[0] == orders[1] == expected
    assert orders[2] == [id for i in range(0, len(expected), 4)
                         for id in reversed(expected[i:i + 4])]
    assert receipt_orders[0] == receipt_orders[1] == receipt_orders[2]


@pytest.mark.parametrize('cap', ['token_cap', 'cost_cap_usd'])
def test_reservation_check_and_claim_are_atomic(rig, monkeypatch, cap):
    calls, _, _ = rig
    budget = calls.budget
    usage = TokenUsage(5, 5)
    calls.config[cap] = 15 if cap == 'token_cap' else float(budget.cost(usage) * 3 / 2)
    checked, release, second_started = Event(), Event(), Event()
    before = budget.before
    def pause_after_check(*args, **kwargs):
        before(*args, **kwargs)
        checked.set()
        assert release.wait(5)
    monkeypatch.setattr(budget, 'before', pause_after_check)
    def second():
        second_started.set()
        return budget.reserve(usage, 'formalise')
    with ThreadPoolExecutor(2) as pool:
        first = pool.submit(budget.reserve, usage, 'formalise')
        assert checked.wait(5)
        other = pool.submit(second)
        assert second_started.wait(5)
        # With the lock, the second check cannot run until the first claim lands.
        time.sleep(0.05)
        release.set()
        reservation = first.result()
        with pytest.raises(BudgetStop):
            other.result()
        budget.release(reservation)


def test_recovery_does_not_erase_other_request(rig, monkeypatch):
    from datetime import datetime, timezone
    from ara.runtime.providers import Response
    calls, provider, log = rig
    waiting, release = Event(), Event()
    monkeypatch.setattr(calls, 'count_request', lambda *a, **k: RequestCount(10, 10, TokenUsage(10, 10)))
    def complete(kind, prompt, *args):
        raw = response({'formula': {'op': 'atom', 'name': 'P'}})
        if json.loads(prompt.split('\nINPUT_JSON\n')[1])['proposition']['id'] == 'p':
            waiting.set()
            assert release.wait(5)
            raw['container'] = {'expires_at': datetime.now(timezone.utc)}
        return Response(raw)
    monkeypatch.setattr(provider, 'complete', complete)
    with ThreadPoolExecutor(2) as pool:
        failed = pool.submit(calls.formalise, Proposition('p', 'P'))
        assert waiting.wait(5)
        calls.formalise(Proposition('q', 'Q'))
        release.set()
        with pytest.raises(BudgetStop, match='actual spend unknown'):
            failed.result()
    events = [e for e in log.read() if e['label'] == 'MODEL']
    assert len(events) == 2
    assert calls.budget.used_tokens == 28
    assert calls.budget.used_cost == calls.budget.cost(TokenUsage(15, 13))
    assert sorted(json.loads(e['payload_json'])['status'] for e in events) == ['accepted', 'incomplete']


def test_same_request_single_flight(rig, monkeypatch):
    from ara.runtime.providers import Response
    calls, provider, log = rig
    dispatches = []
    def complete(*args):
        dispatches.append(args)
        time.sleep(0.03)
        return Response(response({'formula': {'op': 'atom', 'name': 'P'}}))
    monkeypatch.setattr(provider, 'complete', complete)
    barrier = Barrier(4)
    def request(_):
        barrier.wait()
        return calls.formalise(Proposition('p', 'P'))
    with ThreadPoolExecutor(4) as pool:
        results = list(pool.map(request, range(4)))
    assert len(dispatches) == 1
    assert results.count(results[0]) == 4
    assert calls.budget.used_tokens == 8
    assert sum(json.loads(e['payload_json']).get('cache_hit', False) for e in log.read()) == 3


def test_writer_propagates_failure_and_drains(tmp_path, monkeypatch):
    from ara.runtime.logging import SerializedEventLog
    log = EventLog(tmp_path / 'events.jsonl')
    original = log.emit
    def fail(event):
        if event.stage == 'Q':
            raise OSError('Q')
        original(event)
    monkeypatch.setattr(log, 'emit', fail)
    with SerializedEventLog(log) as writer:
        writer.record('P')
        with pytest.raises(OSError, match='Q'):
            writer.record('Q')
        writer.record('R')
    assert [e['stage'] for e in log.read()] == ['P', 'R']


@pytest.mark.parametrize('value', [0, -1, True, 1.5, '4'])
def test_invalid_concurrency_refuses_before_search(rig, value):
    from ara.runtime.orchestration import search_all
    from ara.types import CommitmentSet
    calls, _, log = rig
    calls.config['search_concurrency'] = value
    with pytest.raises(ValueError, match='search_concurrency'):
        search_all(calls, None, CommitmentSet(()), ())
    assert log.read() == []


def test_run_stop_refuses_later_admission(rig):
    calls, _, _ = rig
    with pytest.raises(BudgetStop):
        calls.budget.stop('P', 'formalise')
    with pytest.raises(BudgetStop, match='P'):
        calls.budget.reserve(TokenUsage(1, 1), 'formalise')


def test_native_search_uses_writer_and_default_limit(rig, monkeypatch):
    from ara.bank import Bank
    from ara.runtime.orchestration import NativeEngine, search_all
    from ara.runtime.providers import Response
    from ara.types import CommitmentSet, Formula
    calls, provider, log = rig
    calls.config.pop('search_concurrency', None)
    writer_threads = set()
    emit_many = log.emit_many
    def observed(events):
        writer_threads.add(get_ident())
        emit_many(events)
    monkeypatch.setattr(log, 'emit_many', observed)
    def complete(kind, *args):
        return Response(response({'t_id': 'open'} if kind == 'map_leaf' else {'proposals': []}))
    monkeypatch.setattr(provider, 'complete', complete)
    from ara.engine import Engine
    search = Engine.search
    barrier = Barrier(4)
    def overlapping(engine, target):
        barrier.wait(timeout=5)
        return search(engine, target)
    monkeypatch.setattr(Engine, 'search', overlapping)
    targets = tuple(Proposition(n.lower(), n, Formula('atom', name=n)) for n in ('P', 'Q'))
    routes = search_all(calls, NativeEngine(Bank('1', ()), calls), CommitmentSet(()), targets)
    assert len(routes) == 4
    assert len(writer_threads) == 1 and get_ident() not in writer_threads
    assert calls.log is calls.budget.log is log
    assert len(list((log.path.parent / 'search-traces').glob('*.jsonl'))) == 4


def test_reservation_is_held_until_receipt_is_durable(rig, monkeypatch):
    from ara.runtime.providers import Response
    calls, provider, log = rig
    calls.config['token_cap'] = 19
    monkeypatch.setattr(calls, 'count_request', lambda *a, **k: RequestCount(5, 5, TokenUsage(5, 5)))
    monkeypatch.setattr(provider, 'complete', lambda *a: Response(response(
        {'formula': {'op': 'atom', 'name': 'P'}})))
    waiting, release = Event(), Event()
    record = log.record
    def hold_receipt(stage, *args, **kwargs):
        if stage == 'response_received':
            waiting.set()
            assert release.wait(5)
        record(stage, *args, **kwargs)
    monkeypatch.setattr(log, 'record', hold_receipt)
    with ThreadPoolExecutor(2) as pool:
        first = pool.submit(calls.formalise, Proposition('p', 'P'))
        assert waiting.wait(5)
        second = pool.submit(calls.formalise, Proposition('q', 'Q'))
        try:
            with pytest.raises(BudgetStop):
                second.result(timeout=2)
        finally:
            release.set()
        first.result()
    assert calls.budget.used_tokens == 8
