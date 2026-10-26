"""Stopped native search recovery, using placeholder-only provider responses."""
import json

import pytest
import yaml

from ara.bank import load_bank
from ara.engine import Engine
from ara.runtime.cache import Cache, canonical
from ara.runtime.calls import ModelCalls
from ara.runtime.cli import ROOT, main
from ara.runtime.logging import EventLog
from ara.runtime.orchestration import NativeEngine, search_all
from ara.runtime.providers import MockProvider, Response
from ara.runtime.search_publication import SearchPublication
from ara.types import Commitment, CommitmentSet, Formula, Proposition, TokenUsage
from test_calls import response


def stopped(tmp_path, monkeypatch, *, licensed=False):
    config = yaml.safe_load((ROOT / 'config.yaml').read_text())
    config.update(provider='mock', search_concurrency=1, cache_dir=str(tmp_path/'cache'))
    if licensed:
        config['node_cap'] = 2
    bank = load_bank(ROOT/'bank')
    log = EventLog(tmp_path/'events.jsonl')
    t = CommitmentSet(())
    targets = (Proposition('p', 'P', Formula('atom', name='P')),)
    log.record('run_started', config=config, topic='P', audience='', literature='', bank_version=bank.bank_version)
    (tmp_path/'commitments.json').write_text(t.to_json())
    log.record('commitments_frozen', commitments=t.to_dict(), bank_version=bank.bank_version)
    log.record('candidates', candidates=[p.to_dict() for p in targets])
    provider = MockProvider({})
    def complete(kind, prompt, *args):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'map_leaf':
            value = {'t_id': 'open'}
        elif kind == 'formalise':
            p, q = Formula('atom', name='P'), Formula('atom', name='Q')
            value = {'formula': {'P': p, 'Q': q, 'R': Formula('implies', (q, p))}[
                inputs['proposition']['text']].to_dict()}
        elif licensed:
            value = {'proposals': [dict(bank_id='modus_ponens', conclusion_text='P', premises=[
                dict(slot='conditional', text='R', t_id='open', scope_id=None),
                dict(slot='antecedent', text='Q', t_id='open', scope_id=None)])]}
        else:
            value = {'proposals': []}
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    calls = ModelCalls(config, provider, log, Cache(tmp_path/'cache'), ROOT, 'P')
    search = Engine.search
    def interrupted(engine, goal):
        if goal.formula.op == 'not':
            engine.sink.record('call_start', call_id='pending', kind='formalise', cache_key='P',
                               model=config['model'], prompt='P', reserved_usage=TokenUsage(9, 3).to_dict())
            engine.sink.record('response_received', call_id='pending', kind='formalise', cache_key='P',
                               requested_model=config['model'], raw_response=response({'formula': {'op': 'atom', 'name': 'P'}},
                                   usage={'input_tokens': 5, 'output_tokens': 2}),
                               measured_usage=TokenUsage(5, 2).to_dict(), measured_cost_usd=.001)
            raise KeyboardInterrupt()
        return search(engine, goal)
    with monkeypatch.context() as patch:
        patch.setattr(Engine, 'search', interrupted)
        patch.setattr(SearchPublication, 'publish', lambda self: None)
        with pytest.raises(KeyboardInterrupt):
            search_all(calls, NativeEngine(bank, calls), t, targets)
    return log, provider


def test_resume_offline_publishes_once_and_settles_measured_receipt(tmp_path, monkeypatch, capsys):
    log, provider = stopped(tmp_path, monkeypatch)
    def forbidden(*args):
        pytest.fail('offline recovery created a provider')
    args = ['resume-search', '--run-dir', str(tmp_path), '--stop-before-dispatch']
    assert main(args, calls_factory=forbidden) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan['jobs_to_rerun'] == [1]
    assert plan['completed_jobs'] == [0]
    first = [e for e in log.read() if e['label'] == 'MODEL']
    assert sum(e['usage']['input_tokens'] for e in first if json.loads(e['payload_json']).get('call_id') == 'pending') == 5
    assert main(args, calls_factory=forbidden) == 0
    assert [e for e in log.read() if e['label'] == 'MODEL'] == first
    assert len([e for e in log.read() if e['stage'] == 'search_job_published']) == 2


def test_resume_dispatches_only_missing_job_and_finishes_native_lifecycle(tmp_path, monkeypatch):
    log, provider = stopped(tmp_path, monkeypatch)
    searched = []
    search = Engine.search
    def track(engine, goal):
        searched.append(goal.formula.op)
        return search(engine, goal)
    monkeypatch.setattr(Engine, 'search', track)
    def factory(config, log, topic):
        return ModelCalls(config, provider, log, Cache(tmp_path/'cache'), ROOT, topic)
    assert main(['resume-search', '--run-dir', str(tmp_path)], calls_factory=factory) == 0
    assert searched == ['not']
    events = log.read()
    assert len([e for e in events if e['stage'] == 'commitments_frozen']) == 1
    analysis = [json.loads(e['payload_json']) for e in events if e['stage'] == 'conflicts_and_robustness'][-1]
    assert len(analysis['findings']['analyses']) == 1
    assert any(e['stage'] == 'awaiting_selection' for e in events)
    assert main(['resume-search', '--run-dir', str(tmp_path)], calls_factory=factory) == 0
    assert searched == ['not']


@pytest.mark.parametrize('damage', ['t', 'freeze', 'target', 'trace', 'anchor', 'unknown_usage', 'job_target', 'seal', 'missing_journal', 'usage'])
def test_resume_refuses_mismatch_before_publication(tmp_path, monkeypatch, damage):
    log, _ = stopped(tmp_path, monkeypatch)
    if damage == 't':
        (tmp_path/'commitments.json').write_text(CommitmentSet((
            Commitment('t1', 'P', 'P', Formula('atom', name='P')),)).to_json())
    elif damage == 'freeze':
        log.record('commitments_frozen', commitments={'commitments': []})
    elif damage == 'target':
        log.record('candidates', candidates=[])
    elif damage == 'trace':
        next((tmp_path/'search-traces').glob('*.jsonl')).write_text('{}\n')
    elif damage == 'anchor':
        next((tmp_path/'search-journals').glob('*/*.anchor')).write_text('P\n')
    elif damage == 'unknown_usage':
        journal = EventLog(sorted((tmp_path/'search-journals').glob('*/*.jsonl'))[1])
        journal.record('call_start', call_id='unknown', kind='formalise', cache_key='Q')
    elif damage == 'missing_journal':
        path = sorted((tmp_path/'search-journals').glob('*/*.jsonl'))[0]
        path.unlink()
        path.with_suffix('.anchor').unlink()
    else:
        from ara.types import RunEvent
        target = log if damage == 'job_target' else EventLog(sorted(
            (tmp_path/'search-journals').glob('*/*.jsonl'))[1 if damage == 'usage' else 0])
        events = target.read()
        stage = {'job_target': 'search_publication_started', 'seal': 'search_trace_receipt',
                 'usage': 'response_received'}[damage]
        event = next(e for e in events if e['stage'] == stage)
        data = json.loads(event['payload_json'])
        if damage == 'job_target':
            data['jobs'][0]['goal']['text'] = 'Q'
        elif damage == 'seal':
            data['search_id'] = 'Q'
        else:
            data['measured_usage']['input_tokens'] += 1
        event['payload_json'] = canonical(data)
        target.path.unlink()
        target.anchor.unlink()
        target.emit_many(RunEvent.from_dict(e) for e in events)
    before = log.path.read_bytes()
    assert main(['resume-search', '--run-dir', str(tmp_path), '--stop-before-dispatch']) == 2
    assert log.path.read_bytes() == before


def test_resume_continues_copied_prefix_without_duplicate_usage(tmp_path, monkeypatch):
    from ara.runtime.search_resume import load_search_resume
    from ara.types import RunEvent
    log, _ = stopped(tmp_path, monkeypatch)
    state = load_search_resume(log, load_bank(ROOT/'bank'), ROOT)
    receipt, journal, _ = state.publications[0]
    log.record('search_job_publication', **receipt)
    log.emit_many(RunEvent.from_dict(e) for e in journal[:8])
    log.record('runtime_error', error_type='InterruptedError')
    args = ['resume-search', '--run-dir', str(tmp_path), '--stop-before-dispatch']
    assert main(args) == 0
    after = log.read()
    for event in journal:
        assert after.count(event) == 1
    assert main(args) == 0
    assert len([e for e in log.read() if e['stage'] == 'search_job_publication_continued']) == 1


def test_resume_refuses_changed_published_journal(tmp_path, monkeypatch):
    from ara.runtime.search_resume import load_search_resume, publish_search_resume
    log, _ = stopped(tmp_path, monkeypatch)
    state = load_search_resume(log, load_bank(ROOT/'bank'), ROOT)
    publish_search_resume(log, state)
    journal = EventLog(sorted((tmp_path/'search-journals').glob('*/*.jsonl'))[0])
    journal.record('P')
    before = log.path.read_bytes()
    assert main(['resume-search', '--run-dir', str(tmp_path), '--stop-before-dispatch']) == 2
    assert log.path.read_bytes() == before


def test_resume_restores_seal_even_if_finished_marker_was_interrupted(tmp_path, monkeypatch):
    from ara.runtime.search_resume import load_search_resume
    log, _ = stopped(tmp_path, monkeypatch)
    path = sorted((tmp_path/'search-journals').glob('*/*.jsonl'))[0]
    # A halt immediately after the seal leaves an authentic shorter journal.
    for p in (path, path.with_suffix('.anchor')):
        p.write_bytes(b''.join(p.read_bytes().splitlines(keepends=True)[:-1]))
    state = load_search_resume(log, load_bank(ROOT/'bank'), ROOT)
    assert state.summary()['completed_jobs'] == [0]


def test_resume_lock_refuses_concurrent_recovery(tmp_path, monkeypatch):
    from ara.runtime.search_resume import search_resume_lock
    log, _ = stopped(tmp_path, monkeypatch)
    before = log.path.read_bytes()
    with search_resume_lock(tmp_path):
        assert main(['resume-search', '--run-dir', str(tmp_path), '--stop-before-dispatch']) == 2
    assert log.path.read_bytes() == before



def test_resume_restores_licenses_even_when_node_cap_discards_the_proposal(tmp_path, monkeypatch):
    from ara.runtime.search_resume import load_search_resume
    log, _ = stopped(tmp_path, monkeypatch, licensed=True)
    state = load_search_resume(log, load_bank(ROOT/'bank'), ROOT)
    result, licenses = state.restored[0]
    assert result.truncated
    assert all(node.proposal is None for route in result.routes for node in route.nodes)
    assert len(licenses) == 1
    assert licenses[0][0].bank_id == 'modus_ponens'
    assert licenses[0][1].conclusion.formula == Formula('atom', name='P')
    assert [p.id for p in licenses[0][1].premises] == ['conditional', 'antecedent']
