"""Partial native search, bounded retries, accounting and selection on placeholders."""
from collections import Counter
import json
from pathlib import Path

import pytest
import yaml

from ara.bank import Bank
from ara.runtime.budget import BudgetStop
from ara.runtime.cache import Cache
from ara.runtime.calls import ModelCalls
from ara.runtime.claude_code import ClaudeCodeError
from ara.runtime.cli import main
from ara.runtime.export import methodology
from ara.runtime.logging import EventLog
from ara.runtime.orchestration import NativeEngine, search_all
from ara.runtime.providers import MockProvider, Response
from ara.types import CommitmentSet, Formula, Proposition
from test_calls import ROOT, response


class SearchProvider(MockProvider):
    retries = 1
    backoff = 0

    def __init__(self, failures):
        super().__init__({})
        self.failures = failures
        self.attempts = Counter()
        self.order = []

    def complete(self, kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'map_leaf':
            value = {'t_id': 'open'}
        elif kind == 'propose_cuts':
            formula = Formula.from_dict(data['goal']['formula'])
            goal = ('not:' + formula.args[0].name.lower()) if formula.op == 'not' else formula.name.lower()
            self.attempts[goal] += 1
            self.order.append(goal)
            if self.attempts[goal] <= self.failures.get(goal, 0):
                raise ClaudeCodeError('cli_exit_error', retryable=True)
            value = {'proposals': []}
        else:
            raise AssertionError(kind)
        return Response(response(value))


def setup(tmp_path, failures, concurrency=1):
    config = yaml.safe_load((ROOT / 'config.yaml').read_text())
    config.update(search_concurrency=concurrency, token_cap=10**9, cost_cap_usd=1000)
    log = EventLog(tmp_path / 'events.jsonl')
    provider = SearchProvider(failures)
    calls = ModelCalls(config, provider, log, Cache(tmp_path / 'cache'), ROOT, 'P')
    targets = tuple(Proposition(n.lower(), n, Formula('atom', name=n)) for n in ('P', 'Q', 'R'))
    return calls, provider, log, targets


def payloads(log, stage):
    return [json.loads(e['payload_json']) for e in log.read() if e['stage'] == stage]


@pytest.mark.parametrize('concurrency', [1, 4])
def test_failed_job_retries_after_initial_queue_and_preserves_sibling(tmp_path, concurrency):
    calls, provider, log, targets = setup(tmp_path, {'not:p': 100, 'q': 2}, concurrency)
    routes = search_all(calls, NativeEngine(Bank('1', ()), calls), CommitmentSet(()), targets)
    assert len(routes) == 5  # Includes P even though its negative search never completed.
    assert provider.attempts == {'p': 1, 'not:p': 4, 'q': 3, 'not:q': 1, 'r': 1, 'not:r': 1}
    if concurrency == 1:
        assert provider.order == ['p', 'not:p', 'not:p', 'q', 'q', 'not:q', 'r', 'not:r',
                                  'not:p', 'not:p', 'q']
    started = payloads(log, 'search_job_started')
    assert [p['job_index'] for p in started] == [0, 1, 1, 2, 2, 3, 4, 5]
    assert [p['attempt'] for p in started] == [1, 1, 2, 1, 2, 1, 1, 1]
    assert len(payloads(log, 'search_job_retry')) == 2
    phase = payloads(log, 'search_phase_finished')[-1]
    assert phase['status'] == 'partial'
    assert [p['status'] for p in phase['jobs']] == ['completed', 'failed', 'completed', 'completed', 'completed', 'completed']
    assert len(payloads(log, 'search_analysis_failed')) == 1
    assert payloads(log, 'search_started')[0]['source'] == 'completed search; paired analysis unavailable'
    # Unknown CLI spend remains reserved and disclosed, even after a job recovers.
    summary = json.loads(methodology(log.path).split('```json\n')[1].split('\n```')[0])
    assert not summary['accounting_complete']
    assert summary['search']['status'] == 'partial'
    assert summary['search']['failed_job_indices'] == [1]
    assert len(list((tmp_path / 'routes').glob('*.json'))) == 5


@pytest.mark.parametrize('failure', ['budget', 'context', 'infrastructure'])
def test_global_stop_cancels_queue_without_retry_and_keeps_completed_routes(tmp_path, monkeypatch, failure):
    calls, provider, log, targets = setup(tmp_path, {})
    complete = provider.complete
    def stop(kind, prompt, *args):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'propose_cuts' and data['goal']['formula'] == Formula('not', (Formula('atom', name='P'),)).to_dict():
            if failure == 'infrastructure':
                raise OSError('P')
            calls.budget.stop('context bound' if failure == 'context' else 'token cap', kind)
        return complete(kind, prompt, *args)
    monkeypatch.setattr(provider, 'complete', stop)
    with pytest.raises(BudgetStop):
        search_all(calls, NativeEngine(Bank('1', ()), calls), CommitmentSet(()), targets)
    assert set(provider.attempts) == {'p'}
    assert not payloads(log, 'search_job_retry')
    phase = payloads(log, 'search_phase_finished')[-1]
    assert phase['status'] == 'stopped'
    assert [p['status'] for p in phase['jobs']] == ['completed', 'failed'] + ['cancelled'] * 4
    assert len(list((tmp_path / 'routes').glob('*.json'))) == 1


def test_cli_partial_search_reaches_selection_and_composes(tmp_path, capsys):
    from fixture_support import T, TARGETS
    provider = SearchProvider({'not:p': 100})
    complete = provider.complete
    def native(kind, prompt, schema, maximum):
        if kind == 'build_t':
            value = T.to_dict()
        elif kind == 'propose_targets':
            value = {'targets': [t.to_dict() for t in TARGETS]}
        elif kind == 'write_essay':
            value = {'title': 'P', 'body': '[[node:n0]] P Q', 'bibliography': []}
        elif kind == 'audit_essay':
            value = {'labels': [{'sentence': 1, 'node_ids': ['n0'],
                                'asserts_premise_or_inference_not_in_outline': False}]}
        elif kind == 'search_evidence':
            return Response(response(None, content=[{'type': 'text', 'text': 'P'}]))
        elif kind == 'verify_originality_citations':
            value = {'items': [], 'originality': {'assessment': 'unverified', 'evidence_urls': [], 'detail': 'P'}}
        else:
            return complete(kind, prompt, schema, maximum)
        return Response(response(value))
    provider.complete = native
    config = yaml.safe_load((ROOT / 'config.yaml').read_text())
    config.update(provider='mock', search_concurrency=1, essay_min_words=0, target_candidates=2,
                  token_cap=10**9, cost_cap_usd=1000, cache_dir=str(tmp_path / 'cache'))
    path = tmp_path / 'config.yaml'
    path.write_text(yaml.safe_dump(config))
    def factory(config, log, topic):
        return ModelCalls(config, provider, log, Cache(Path(config['cache_dir'])), ROOT, topic)
    run = tmp_path / 'run'
    assert main(['run', '--config', str(path), '--topic', 'P Q', '--literature',
                 str(ROOT / 'tests/fixtures/runtime/smoke-literature.txt'), '--run-dir', str(run)],
                calls_factory=factory) == 0
    assert 'Partial search:' in capsys.readouterr().err
    log = EventLog(run / 'events.jsonl')
    awaiting = payloads(log, 'awaiting_selection')[-1]
    assert len(awaiting['route_ids']) == 3
    assert awaiting['search']['status'] == 'partial'
    assert awaiting['search']['failed_job_indices'] == [1]
    route = awaiting['route_ids'][0]
    # Prior unknown spend cannot silently become measured spend on selection.
    assert main(['select', '--run-dir', str(run), '--route', route], calls_factory=factory) == 2
    assert main(['select', '--run-dir', str(run), '--route', route,
                 '--unknown-usage-policy', 'count-at-reservation'], calls_factory=factory) == 0
    assert (run / 'export/essay.txt').exists()
    assert payloads(log, 'unknown_usage_reconciled')
    assert 'partial' in (run / 'export/methodology.md').read_text()


@pytest.mark.parametrize('all_fail', [False, True])
def test_final_failure_is_disclosed_without_fabricating_search_results(tmp_path, all_fail):
    failures = {name: 100 for name in ('p', 'not:p', 'q', 'not:q', 'r', 'not:r')} if all_fail else {'p': 2}
    calls, provider, log, targets = setup(tmp_path, failures)
    routes = search_all(calls, NativeEngine(Bank('1', ()), calls), CommitmentSet(()), targets)
    phase = payloads(log, 'search_phase_finished')[-1]
    assert len(routes) == (0 if all_fail else 6)
    assert phase['status'] == ('partial' if all_fail else 'complete')
    assert all(p['status'] == ('failed' if all_fail else 'completed') for p in phase['jobs'])
    assert len(payloads(log, 'search_job_retry')) == (6 if all_fail else 1)
    assert len(payloads(log, 'search_finished')) == len(routes)
    assert len(payloads(log, 'search_job_failed')) == (12 if all_fail else 1)


def test_analysis_provider_failure_preserves_completed_search_routes(tmp_path, monkeypatch):
    from ara.runtime.calls import Rejected
    import ara.runtime.orchestration as orchestration
    calls, provider, log, targets = setup(tmp_path, {})
    analyse = orchestration.analyse_searches
    def fail_one(engine, positive, negative):
        if positive.target.id == 'p':
            raise Rejected('P')
        return analyse(engine, positive, negative)
    monkeypatch.setattr(orchestration, 'analyse_searches', fail_one)
    routes = search_all(calls, NativeEngine(Bank('1', ()), calls), CommitmentSet(()), targets)
    assert len(routes) == 6
    assert [p['target'] for p in payloads(log, 'search_analysis_failed')] == ['p']
    assert len(payloads(log, 'conflicts_and_robustness')[-1]['findings']['analyses']) == 2
    summary = json.loads(methodology(log.path).split('```json\n')[1].split('\n```')[0])
    assert summary['search']['status'] == 'partial'
