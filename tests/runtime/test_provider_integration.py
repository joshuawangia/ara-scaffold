"""Stage dispatch and shared budgets across API and subscription backends."""
import json

import pytest

from ara.runtime.budget import BudgetStop
from ara.runtime.cache import Cache
from ara.runtime.calls import ModelCalls, Rejected
from ara.runtime.claude_code import ClaudeCodeProvider
from ara.runtime.logging import EventLog
from ara.runtime.providers import MockProvider
from ara.types import Proposition
from test_calls import ROOT, register
from test_claude_code import cli

ROOTS = {'roots': [], 'relevance': 'P', 'omissions': []}


def stage_binary(binary):
    binary.write_text(binary.read_text().replace(
        " value={'formula':{'op':'atom','name':'P'}}",
        " value={'roots': [], 'relevance': 'P', 'omissions': []} if 'roots' in schema['properties'] else {'formula':{'op':'atom','name':'P'}}"))


@pytest.mark.parametrize('retry', [False, True])
def test_api_run_subscription_stage_canary_accounting_and_retries(cli, tmp_path, retry):
    _, set_mode, config, binary = cli
    stage_binary(binary)
    config.update(provider='mock', model='claude-opus-5', stages={
        'select_t_roots': {'provider': 'claude_code', 'model': 'claude-opus-5-5'}})
    log = EventLog(tmp_path / 'mixed' / 'events.jsonl')
    api = MockProvider({})
    calls = ModelCalls(config, api, log, Cache(tmp_path / 'mixed-cache'), ROOT, 'P',
                       provider_factory=ClaudeCodeProvider)
    calls.count_request('select_t_roots', {})
    assert not [e for e in log.read() if e['label'] == 'MODEL']
    if retry:
        set_mode('rate')
        with pytest.raises(Rejected, match='cli_.*limit'):
            calls.call('select_t_roots', {})
    else:
        assert calls.call('select_t_roots', {}) == ROOTS
        assert calls.call('select_t_roots', {}) == ROOTS
    models = [e for e in log.read() if e['label'] == 'MODEL']
    assert sum(e['stage'] == 'isolation_canary' for e in models) == 1
    assert len([e for e in models if e['stage'] == 'select_t_roots' and not json.loads(e['payload_json'])['cache_hit']]) == (3 if retry else 1)
    assert calls.budget.used_cost == 0 and calls.budget._pending_tokens == 0
    assert all(json.loads(e['payload_json'])['provider'] == 'claude_code' for e in models)
    assert api.calls == 0
    with pytest.raises(BudgetStop, match='cost cap'):
        calls.formalise(Proposition('p', 'P'))
    assert api.calls == 0


def test_subscription_run_api_stage_retains_prices_and_cap(cli, tmp_path):
    _, _, config, _ = cli
    config.update(cost_cap_usd=1, stages={'select_t_roots': {'provider': 'mock', 'model': 'claude-opus-5'}})
    log = EventLog(tmp_path / 'mixed' / 'events.jsonl')
    api = MockProvider({})
    calls = ModelCalls(config, ClaudeCodeProvider(config), log, Cache(tmp_path / 'mixed-cache'), ROOT, 'P',
                       provider_factory=lambda settings: api)
    scoped = calls._for_construction_stage('select_t_roots', {})
    register(scoped, api, 'select_t_roots', {}, ROOTS)
    assert calls.call('select_t_roots', {}) == ROOTS
    assert calls.budget.used_cost > 0
    assert api.calls == 1
    register(scoped, api, 'select_t_roots', {'P': 'Q'}, ROOTS)
    config['cost_cap_usd'] = 0
    with pytest.raises(BudgetStop, match='cost cap'):
        calls.call('select_t_roots', {'P': 'Q'})
    assert api.calls == 1
