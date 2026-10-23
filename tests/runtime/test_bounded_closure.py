"""Budgeted native construction, using only placeholder source graphs."""
import copy
import json

import pytest

from ara.bank import load_bank
from ara.runtime.closure_budget import budget_plan, depth_cut
from ara.runtime.construction import evidence_dependencies, prerequisite_closure
from ara.runtime.export import methodology
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.providers import Response
from rich_fixture import graph, batch_response
from test_extraction import rig, offline, response, ROOT
from test_extraction_rich import rich_calls
from test_root_selection import choose


def test_global_budget_reserves_copy_symbols_and_headroom(rig):
    calls, *_ = rig
    config = {**calls.config, 'working_t_symbol_token_budget': 48000,
              'working_t_symbol_growth_tokens_per_item': 128}
    plan = budget_plan(config, 46, 220, 3200, 70000)
    assert plan['symbol_tokens_per_commitment'] == 233
    assert plan['per_window_commitments'] == 3
    assert plan['projected_t_commitments'] == 138
    assert plan['projected_working_tokens'] == 65714
    assert plan['projected_symbol_tokens'] == 32154
    assert plan['projected_working_tokens'] <= 80000
    assert budget_plan(config, 10000, 220, 3200, 70000)['per_window_commitments'] == 0
    assert budget_plan(config, 46, 220, 3200, 3300)['per_window_commitments'] == 0


def test_depth_cut_retains_qualifiers_endpoints_and_omitted_support():
    items = {i['id']: i for i in graph()['items']}
    original = copy.deepcopy(items)
    deps = evidence_dependencies(items)
    selected, omitted, depth = depth_cut(items, ['f'], deps, lambda ids: len(ids) <= 5)
    assert selected == {'f', 'qual', 'j', 'r', 'd'}
    assert omitted == {'r': ['i']} and depth == 1
    assert items == original
    assert depth_cut(items, ['f'], deps, lambda ids: len(ids) <= 1) == (set(), {}, -1)
    complete, omitted, _ = depth_cut(items, ['f'], deps, lambda ids: len(ids) <= 8)
    assert complete == prerequisite_closure(items, ['f']) and omitted == {}
    # Incoming qualification cycles reach a deterministic fixed point.
    items['qual']['applies_to'].append('d')
    items['d']['applies_to'].append('qual')
    selected, _, _ = depth_cut(items, ['f'], evidence_dependencies(items), lambda ids: len(ids) <= 3)
    assert selected == {'f', 'qual', 'd'}


def test_native_cut_disclosed_in_frozen_text_receipt_and_methodology(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    calls.config['working_t_symbol_token_budget'] = 1000  # 3 commitments after headroom.
    sent = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1]); sent.append((kind, inputs))
        if kind == 'select_t_roots':
            value = choose(inputs)
            assert inputs['window_budget']['per_window_commitments'] == 3
            root = value['roots'][0]
            assert inputs['closure_costs'][root]['items'] == 8
            assert inputs['closure_costs'][root]['evidence_payload_token_bound'] > 0
        else:
            assert len(inputs['closure']['inventory']) == 2
            value = batch_response(inputs)
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    t = prepare_commitments(calls, load_bank(ROOT/'bank'), path.read_text(), '')
    assert len(t.commitments) == 2
    conclusion = next(c for c in t.commitments if c.id.endswith(':f'))
    assert '[assumed_premise; support_omitted;' in conclusion.text
    assert 'p:r1-2:j' in conclusion.text
    assert conclusion.text.endswith('[author_claim; a; conclusion] F(x)')
    assert conclusion.citation == 'p:pdf:1#p:r1-2:f'
    events = calls.log.read()
    assert sum(e['stage'] == 'commitments_frozen' for e in events) == 1
    closure = next(json.loads(e['payload_json']) for e in events if e['stage'] == 'build_t_closure')
    assert closure['support_omitted'] == {'p:r1-2:f': ['p:r1-2:j']}
    accounted = next(json.loads(e['payload_json']) for e in events if e['stage'] == 'build_t_evidence_accounted')
    assert len(accounted['selected_ids']) == 2 and len(accounted['omitted']) == 6
    assert all(o['reason'] == 'budget depth cut: support omitted' for o in accounted['omitted'])
    summary = json.loads(methodology(calls.log.path).split('```json\n')[1].split('\n```')[0])
    assert summary['construction']['support_omitted'] == [dict(index=0, evidence_id=conclusion.id,
                                                             omitted_support_ids=['p:r1-2:j'])]
    assert 'conditional' in summary['construction']['support_policy']


def test_zero_root_window_can_precede_contributing_window(rig, monkeypatch):
    from ara.types import TokenUsage
    calls, provider, path = rich_calls(rig, monkeypatch)
    estimate = provider.estimate
    def count(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'select_t_roots' and sum(len(p['items']) for p in data['papers']) > 4:
            return TokenUsage(input_tokens=70001, output_tokens=maximum)
        return estimate(kind, prompt, schema, maximum)
    def complete(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        value = batch_response(data)
        if kind == 'select_t_roots' and data['batch_index'] == 0:
            value = dict(roots=[], relevance='P', omissions=[dict(group_id=g['group_id'], reason='Q')
                         for g in data['selection_groups']])
        return Response(response(value))
    monkeypatch.setattr(provider, 'estimate', count)
    monkeypatch.setattr(provider, 'complete', complete)
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), path.read_text(), '')
    assert result.commitments
    events = calls.log.read()
    assert sum(e['stage'] == 'build_t_batch_skipped' for e in events) == 1
    assert sum(e['stage'] == 'commitments_frozen' for e in events) == 1
    empty = next(json.loads(e['payload_json']) for e in events if e['stage'] == 'build_t_closure')
    assert empty['empty_reason'] == 'P'


def test_plan_cli_cannot_generate(rig, monkeypatch, tmp_path, capsys):
    from ara.runtime.cli import main
    from ara.runtime.planning import CountingProvider
    calls, provider, path = rich_calls(rig, monkeypatch)
    def forbidden(*args, **kwargs):
        pytest.fail('planning dispatched generation')
    monkeypatch.setattr(CountingProvider, 'complete', forbidden)
    destination = tmp_path/'plan'
    assert main(['plan-construction', '--literature', str(path), '--topic', 'P', '--audience', '',
                 '--config', str(rig[-1]), '--run-dir', str(destination)]) == 0
    plan = json.loads((destination/'construction-plan.json').read_text())
    assert plan['generation_calls'] == 0 and plan['audience'] == ''
    assert plan['plan']['budget']['per_window_commitments'] >= 8
    assert plan['max_request_tokens'] < plan['limits']['batch']
    assert 'provider_count_tokens' not in plan['counter']


@pytest.mark.parametrize('kind', ['working', 'symbols'])
def test_actual_output_cannot_consume_later_allocations(rig, monkeypatch, kind):
    from ara.runtime.calls import Rejected
    from ara.types import TokenUsage
    calls, provider, path = rich_calls(rig, monkeypatch)
    estimate = provider.estimate
    def oversized(stage, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        measured = estimate(stage, prompt, schema, maximum)
        if kind == 'working' and stage == 'propose_targets' and any(
                c['formula']['op'] == 'implies' for c in data.get('commitments', {}).get('commitments', [])):
            return TokenUsage(input_tokens=90000, output_tokens=maximum)
        if kind == 'symbols' and stage == 'build_t_batch' and data.get('shared_symbols'):
            return TokenUsage(input_tokens=measured.input_tokens + 13000, output_tokens=maximum)
        return measured
    monkeypatch.setattr(provider, 'estimate', oversized)
    with pytest.raises(Rejected, match='window token allowance exceeded'):
        prepare_commitments(calls, load_bank(ROOT/'bank'), path.read_text(), '')
    assert not any(e['stage'] == 'commitments_frozen' for e in calls.log.read())


def test_counted_formalization_bound_cuts_before_dispatch(rig, monkeypatch):
    from ara.types import TokenUsage
    calls, provider, path = rich_calls(rig, monkeypatch)
    estimate = provider.estimate
    def count(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'build_t_batch' and len(inputs.get('closure', {}).get('inventory', [])) > 2:
            return TokenUsage(input_tokens=70001, output_tokens=maximum)
        return estimate(kind, prompt, schema, maximum)
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'select_t_roots':
            assert inputs['window_budget']['per_window_commitments'] >= 8
            return Response(response(choose(inputs)))
        assert len(inputs['closure']['inventory']) == 2
        return Response(response(batch_response(inputs)))
    monkeypatch.setattr(provider, 'estimate', count)
    monkeypatch.setattr(provider, 'complete', complete)
    t = prepare_commitments(calls, load_bank(ROOT/'bank'), path.read_text(), '')
    assert len(t.commitments) == 2
    assert any('support_omitted' in c.text for c in t.commitments)
