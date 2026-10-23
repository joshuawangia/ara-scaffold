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


def test_native_cli_correction_matches_stage_manifest(cli, tmp_path):
    from ara.runtime.cli import make_calls
    from ara.runtime.construction import construction_call
    from ara.runtime.construction_stages import construction_stage_manifest
    _, set_mode, config, binary = cli
    config.update(cache_dir=str(tmp_path/'routing-cache'), stages={
        'construction': {'effort':'medium', 'system_prompt':'R'},
        'select_t_roots': {'provider':'claude_code', 'model':'claude-opus-4-8',
                          'effort':'low', 'system_prompt':'P'},
        'construction_correction': {'provider':'claude_code', 'model':'claude-opus-5-5',
                                    'effort':'high', 'system_prompt':'Q'}})
    log = EventLog(tmp_path/'routing/events.jsonl')
    calls = make_calls(config, log, 'P')
    set_mode('construction_correction_rate')
    def check(data):
        if data['relevance'] != 'Q': raise Rejected('P')
        return data
    with pytest.raises(Rejected, match='cli_usage_limit'):
        construction_call(calls, 'select_t_roots', {'papers':[]}, check, {'select_t_roots':1})
    manifest = construction_stage_manifest(config)
    events = [e for e in log.read() if e['label']=='MODEL' and e['stage']=='select_t_roots']
    traces = [json.loads(row) for row in binary.with_suffix('.trace').read_text().splitlines()]
    traces = [row for row in traces if 'ARA_ISOLATION_CANARY' not in row['prompt']]
    assert len(events) == len(traces) == 4
    for index, (event, trace) in enumerate(zip(events, traces)):
        settings = manifest['select_t_roots' + ('_correction' if index else '')]
        args = trace['args']
        assert args[args.index('--model')+1] == settings['model']
        assert args[args.index('--effort')+1] == settings['effort']
        assert args[args.index('--system-prompt')+1] == ('Q' if index else 'P')
        assert event['model_id'] == event['model_version'] == settings['model']
        assert json.loads(event['payload_json'])['attempt'] == (2 if index else 1)


def test_native_api_correction_matches_stage_manifest(cli, tmp_path):
    from types import SimpleNamespace
    from ara.runtime.providers import AnthropicProvider
    from ara.runtime.construction import construction_call
    from ara.runtime.construction_stages import construction_stage_manifest
    _, _, config, _ = cli
    config.update(provider='anthropic', model='claude-opus-5-5', cost_cap_usd=1,
                  select_t_roots_max_output_tokens=1024, stages={
        'construction': {'effort':'medium', 'thinking':'disabled', 'system_prompt':'R'},
        'select_t_roots': {'model':'claude-opus-4-8', 'effort':'low', 'system_prompt':'P'},
        'construction_correction': {'model':'claude-opus-5-5', 'effort':'high', 'system_prompt':'Q',
                                    'thinking':'adaptive', 'fallbacks':[]}})
    config['pricing']['claude-opus-5-5'] = config['pricing']['claude-opus-5']
    requests, counts = [], []
    def count(**kwargs):
        counts.append(kwargs)
        return SimpleNamespace(input_tokens=10)
    def create(**kwargs):
        requests.append(kwargs)
        value = {**ROOTS, 'relevance': 'Q' if len(requests)>1 else 'P'}
        raw = {'model':kwargs['model'], 'stop_reason':'end_turn',
               'usage':{'input_tokens':10,'output_tokens':5},
               'content':[{'type':'text','text':json.dumps(value)}]}
        return SimpleNamespace(to_dict=lambda **_: raw)
    client = SimpleNamespace(messages=SimpleNamespace(count_tokens=count),
                             beta=SimpleNamespace(messages=SimpleNamespace(create=create)))
    log = EventLog(tmp_path/'api-routing/events.jsonl')
    calls = ModelCalls(config, AnthropicProvider(config, client), log, Cache(tmp_path/'api-cache'), ROOT, 'P',
                       provider_factory=lambda settings: AnthropicProvider(settings, client))
    def check(data):
        if data['relevance']!='Q': raise Rejected('P')
        return data
    assert construction_call(calls, 'select_t_roots', {'papers':[]}, check, {'select_t_roots':1})['relevance']=='Q'
    manifest = construction_stage_manifest(config)
    events = [e for e in log.read() if e['label']=='MODEL']
    assert len(requests) == len(events) == 2
    for index, (request, event) in enumerate(zip(requests, events)):
        settings = manifest['select_t_roots' + ('_correction' if index else '')]
        assert request['model'] == event['model_id'] == event['model_version'] == settings['model']
        assert request['output_config']['effort'] == settings['effort']
        assert request['thinking']['type'] == settings['thinking']
        assert request['system'] == ('Q' if index else 'P')
        assert counts[index]['model'] == request['model']
    assert 'fallbacks' not in requests[1]
