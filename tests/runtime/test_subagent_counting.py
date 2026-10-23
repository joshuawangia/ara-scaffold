"""Initial context and transport reservations have different units."""
import json
from pathlib import Path

from ara.runtime.cache import Cache, canonical
from ara.runtime.calls import ModelCalls
from ara.runtime.construction import construct
from ara.runtime.extraction import HEADER, Paper, PageText
from ara.runtime.grounding import ground_outcome
from ara.runtime.logging import EventLog
from ara.runtime.planning import CountingProvider
from test_claude_code import cli, ROOT
from rich_fixture import graph


def test_native_subscription_plan_uses_initial_context_at_pilot_limits(cli, tmp_path):
    _, _, config, binary = cli
    config.update(extracted_build_t_max_output_tokens=64000, build_t_batch_input_tokens=70000,
                  working_t_token_budget=100000, working_t_symbol_token_budget=48000,
                  working_t_symbol_growth_tokens_per_item=233, model_context_token_bound=200000,
                  construction_window_cap_multiplier=2)
    items = graph()['items']
    for item in items:
        item['citation'] = '[p:' + item['id'] + ']'
    log = EventLog(tmp_path/'plan/events.jsonl')
    paper = Paper('p', '{}', 'P', (PageText(1, 'P Q R F x'),))
    grounded = ground_outcome(paper, {'source_id':'p', 'status':'extracted', 'items':items}, log)
    literature = HEADER + canonical({'papers': [grounded]})
    calls = ModelCalls(config, CountingProvider(config, 'provider'), log,
                       Cache(tmp_path/'plan-cache'), ROOT, 'P')
    plan = construct(calls, literature, '', plan_only=True)
    assert len(plan['batches']) == 1
    assert plan['batches'][0]['input_tokens'] <= 70000
    assert plan['budget']['window_commitment_cap'] > 0
    assert plan['budget']['working_wrapper_tokens'] < 30000
    assert not binary.with_suffix('.trace').exists()


def test_count_contract_retains_aggregate_for_admission(cli):
    make, _, config, _ = cli
    calls, log = make()
    count = calls.count_request('build_t_batch', {'papers': []})
    assert count.reservation.input_tokens == 2 * count.initial_input_tokens + 64000
    assert count.reservation.output_tokens == 128000
    assert count.context_output_tokens == 128000
    assert count.initial_input_tokens < 70000 < count.reservation.input_tokens
    event = json.loads(log.read()[-1]['payload_json'])
    assert event['input_tokens'] == count.initial_input_tokens
    assert event['reserved_usage'] == count.reservation.to_dict()


def test_api_search_count_keeps_tool_reservation_separate(cli, tmp_path):
    from types import SimpleNamespace
    from ara.runtime.providers import AnthropicProvider
    _, _, config, _ = cli
    config.update(provider='anthropic', model='claude-opus-5', cost_cap_usd=1, web_search_max_uses=2)
    client = SimpleNamespace(messages=SimpleNamespace(count_tokens=lambda **kwargs: SimpleNamespace(input_tokens=10)))
    calls = ModelCalls(config, AnthropicProvider(config, client), EventLog(tmp_path/'api/events.jsonl'),
                       Cache(tmp_path/'api-cache'), ROOT, 'P')
    count = calls.count_request('search_evidence', {'draft':{}, 'items':[]}, maximum=32, admission=True)
    assert count.initial_input_tokens == 10
    assert count.context_output_tokens == 32
    assert count.reservation.input_tokens == 10 + 2 * config['model_context_token_bound']
    assert count.reservation.output_tokens == 96
    assert count.reservation.server_tool_uses == 2
