"""Soft allocation and accounted refusal proofs on the native construction path."""
import json

import pytest

from ara.bank import load_bank
from ara.runtime.budget import BudgetStop
from ara.runtime.calls import Rejected
from ara.runtime.extraction import extract
from ara.runtime.export import methodology
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.providers import Response
from ara.types import TokenUsage
from rich_fixture import batch_response, graph
from test_extraction import rig, response, register, ROOT


def windows(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config['construction_targeted_corrections'] = 1
    value = graph()
    value['items'] = [i for i in value['items'] if i['id'] in ('p', 'q', 'r')]
    for item in value['items']:
        item.update(kind='premise', premise_ids=[], conclusion_id=None, qualification_ids=[], applies_to=[])
    register(calls, provider, papers[0], value)
    path = extract(calls, (papers[0],))
    estimate = provider.estimate
    dispatched = []
    def count(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'select_t_roots' and sum(len(p['items']) for p in inputs['papers']) > 1:
            return TokenUsage(input_tokens=70001, output_tokens=maximum)
        if kind == 'propose_targets':
            actual = sum(c['formula'].get('name') == 'F' for c in inputs['commitments']['commitments'])
            return TokenUsage(input_tokens=1000 + actual * 30000, output_tokens=maximum)
        return estimate(kind, prompt, schema, maximum)
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        dispatched.append((kind, inputs))
        data = batch_response(inputs)
        if kind == 'build_t_batch':
            for c in data['commitments']:
                c['formula'] = {'op': 'atom', 'name': 'F'}
            data['new_symbols'] = ([] if inputs['shared_symbols'] else [dict(
                name='F', kind='atom', arity=0, definition='F', evidence_ids=[c['id'] for c in data['commitments']])])
            data['alignments'] = [dict(name='F', reason='P')] if inputs['shared_symbols'] else []
        return Response(response(data))
    monkeypatch.setattr(provider, 'estimate', count)
    monkeypatch.setattr(provider, 'complete', complete)
    return calls, provider, path.read_text(), dispatched


def payloads(calls, stage):
    return [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == stage]


def test_borrowing_recounts_and_recomputes_before_next_dispatch(rig, monkeypatch):
    calls, provider, literature, sent = windows(rig, monkeypatch)
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), literature, '')
    assert len(result.commitments) == 3
    selections = [i for k, i in sent if k == 'select_t_roots']
    assert [i['window_budget']['window_copy_token_budget'] for i in selections] == [26333, 24500, 19000]
    assert [i['working_token_allowance'] for i in selections] == [99000, 69000, 39000]
    budgets = payloads(calls, 'build_t_window_budget')
    assert [b['working_input_tokens'] for b in budgets] == [1000, 31000, 61000]
    assert [b['remaining_windows'] for b in budgets] == [3, 2, 1]
    assert budgets[1]['catalogue_tokens'] > 0
    assert selections[1]['window_budget']['window_symbol_token_budget'] == (
        int(calls.config['working_t_symbol_token_budget'] * .8) - budgets[1]['catalogue_tokens']) // 2
    assert len(payloads(calls, 'build_t_share_borrowed')) == 3
    events = calls.log.read()
    for index in (1, 2):
        dispatch = next(n for n, e in enumerate(events) if e['stage'] == 'call_start' and
                        json.loads(e['payload_json'])['kind'] == 'select_t_roots' and
                        json.loads(json.loads(e['payload_json'])['prompt'].split('\nINPUT_JSON\n')[1])['batch_index'] == index)
        assert any(e['stage'] == 'build_t_window_budget' and json.loads(e['payload_json'])['index'] == index
                   for e in events[:dispatch])


@pytest.mark.parametrize('failure', ['selection', 'formalization', 'working', 'symbols', 'context', 'correction_context', 'batch_bound'])
def test_window_refusal_is_accounted_and_later_window_succeeds(rig, monkeypatch, failure):
    calls, provider, literature, sent = windows(rig, monkeypatch)
    complete, estimate = provider.complete, provider.estimate
    def respond(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        out = complete(kind, prompt, schema, maximum)
        if inputs['batch_index'] == 1:
            if kind == 'select_t_roots' and failure == 'selection':
                return Response(response(dict(roots=['r0'], relevance='P', omissions=[])))
            if kind == 'build_t_batch' and failure in ('formalization', 'correction_context'):
                value = json.loads(out.text()); value['commitments'][0]['formula']['name'] = 'Q'
                return Response(response(value))
        return out
    def count(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        measured = estimate(kind, prompt, schema, maximum)
        if inputs.get('batch_index') == 1:
            if failure == 'context' and kind == 'select_t_roots' and 'plan_id' in inputs:
                return TokenUsage(input_tokens=200001, output_tokens=maximum)
            if failure == 'correction_context' and inputs.get('mode') == 'targeted_correction':
                return TokenUsage(input_tokens=200001, output_tokens=maximum)
            if failure == 'batch_bound' and kind == 'build_t_batch' and any(p['index'] == 1 for p in payloads(calls, 'build_t_closure')):
                return TokenUsage(input_tokens=70001, output_tokens=maximum)
            if failure == 'symbols' and kind == 'build_t_batch' and inputs.get('shared_symbols') and any(p['index'] == 1 for p in payloads(calls, 'build_t_closure')):
                return TokenUsage(input_tokens=measured.input_tokens + 20000, output_tokens=maximum)
        if failure == 'working' and kind == 'propose_targets' and any(
                c['id'].endswith(':q') and c['formula'].get('name') == 'F' for c in inputs['commitments']['commitments']):
            return TokenUsage(input_tokens=100001, output_tokens=maximum)
        return measured
    monkeypatch.setattr(provider, 'complete', respond)
    monkeypatch.setattr(provider, 'estimate', count)
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), literature, '')
    assert len(result.commitments) == 2
    assert {c.id.rsplit(':', 1)[1] for c in result.commitments} == {'p', 'r'}
    skipped = payloads(calls, 'build_t_batch_skipped')
    assert len(skipped) == 1 and skipped[0]['index'] == 1 and skipped[0]['reason']
    if failure not in ('selection', 'context'):
        assert skipped[0]['roots'] and skipped[0]['closure']['inventory']
    accounted = payloads(calls, 'build_t_evidence_accounted')[0]
    assert len(accounted['omitted']) == 1 and accounted['omitted'][0]['evidence_id'].endswith(':q')
    assert len(payloads(calls, 'commitments_frozen')) == 1
    if failure == 'formalization':
        assert len(payloads(calls, 'construction_targeted_correction')) == 1
    summary = json.loads(methodology(calls.log.path).split('```json\n')[1].split('\n```')[0])
    assert summary['construction']['skipped_windows'] == skipped


@pytest.mark.parametrize('capacity', ['working', 'symbols'])
def test_global_exhaustion_freezes_accepted_work_once(rig, monkeypatch, capacity):
    calls, provider, literature, sent = windows(rig, monkeypatch)
    estimate = provider.estimate
    def count(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        measured = estimate(kind, prompt, schema, maximum)
        if capacity == 'working' and kind == 'propose_targets' and any(
                c['formula'].get('name') == 'F' for c in inputs['commitments']['commitments']):
            return TokenUsage(input_tokens=100000, output_tokens=maximum)
        if capacity == 'symbols' and kind == 'build_t_batch':
            empty = estimate(kind, calls.render(kind, {**inputs, 'shared_symbols': []})[1], schema, maximum)
            return TokenUsage(input_tokens=empty.input_tokens + (16000 if inputs.get('shared_symbols') else 0), output_tokens=maximum)
        return measured
    monkeypatch.setattr(provider, 'estimate', count)
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), literature, '')
    assert len(result.commitments) == 1
    assert [(k, i['batch_index']) for k, i in sent] == [('select_t_roots', 0), ('build_t_batch', 0)]
    assert len(payloads(calls, 'commitments_frozen')) == 1
    assert len(payloads(calls, 'build_t_global_exhaustion')) == 1
    assert len(payloads(calls, 'build_t_evidence_accounted')[0]['omitted']) == 2
    summary = json.loads(methodology(calls.log.path).split('```json\n')[1].split('\n```')[0])
    assert summary['construction']['global_exhaustion'][0]['accepted_ids'] == [result.commitments[0].id]


@pytest.mark.parametrize('failure', ['campaign', 'counter', 'provider'])
def test_operational_and_campaign_failures_do_not_freeze(rig, monkeypatch, failure):
    calls, provider, literature, sent = windows(rig, monkeypatch)
    if failure == 'campaign':
        calls.config['token_cap'] = 0
    else:
        original = getattr(provider, 'estimate' if failure == 'counter' else 'complete')
        def fail(kind, prompt, schema, maximum):
            inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
            if inputs.get('batch_index') == 1 and 'plan_id' in inputs:
                raise RuntimeError('P')
            return original(kind, prompt, schema, maximum)
        monkeypatch.setattr(provider, 'estimate' if failure == 'counter' else 'complete', fail)
    with pytest.raises(RuntimeError if failure == 'counter' else BudgetStop):
        prepare_commitments(calls, load_bank(ROOT/'bank'), literature, '')
    assert not payloads(calls, 'commitments_frozen')


def test_zero_success_after_window_refusals_still_fails(rig, monkeypatch):
    calls, provider, literature, sent = windows(rig, monkeypatch)
    monkeypatch.setattr(provider, 'complete', lambda *args: Response(response({})))
    with pytest.raises(Rejected, match='empty working T'):
        prepare_commitments(calls, load_bank(ROOT/'bank'), literature, '')
    assert len(payloads(calls, 'build_t_batch_skipped')) == 3
    assert not payloads(calls, 'commitments_frozen')


def test_indivisible_oversized_window_is_skipped_without_losing_later_work(rig, monkeypatch):
    calls, provider, literature, sent = windows(rig, monkeypatch)
    estimate = provider.estimate
    def count(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'select_t_roots' and any(i['id'].endswith(':q') for p in inputs['papers'] for i in p['items']):
            return TokenUsage(input_tokens=200001, output_tokens=maximum)
        return estimate(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'estimate', count)
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), literature, '')
    assert {c.id.rsplit(':', 1)[1] for c in result.commitments} == {'p', 'r'}
    assert all(i['batch_index'] != 1 for _, i in sent)
    skipped = payloads(calls, 'build_t_batch_skipped')
    assert len(skipped) == 1 and 'oversized source batch' in skipped[0]['reason']
    assert payloads(calls, 'build_t_plan')[0]['plan']['batches'][1]['input_tokens'] == 200001


@pytest.mark.parametrize('after_accepted', [1, 3])
def test_catalogue_recount_cannot_freeze_over_global_bound(rig, monkeypatch, after_accepted):
    calls, provider, literature, sent = windows(rig, monkeypatch)
    estimate = provider.estimate
    def count(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        measured = estimate(kind, prompt, schema, maximum)
        if kind == 'build_t_batch' and inputs.get('shared_symbols') and len(payloads(calls, 'build_t_batch_accepted')) >= after_accepted:
            return TokenUsage(input_tokens=measured.input_tokens + 16001, output_tokens=maximum)
        return measured
    monkeypatch.setattr(provider, 'estimate', count)
    with pytest.raises(BudgetStop, match='accepted catalogue exceeds global budget'):
        prepare_commitments(calls, load_bank(ROOT/'bank'), literature, '')
    assert not payloads(calls, 'commitments_frozen')


def test_post_response_counter_error_is_not_a_window_refusal(rig, monkeypatch):
    calls, provider, literature, sent = windows(rig, monkeypatch)
    estimate = provider.estimate
    def count(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'propose_targets' and any(c['id'].endswith(':q') and c['formula'].get('name') == 'F'
                                           for c in inputs['commitments']['commitments']):
            raise ValueError('P')
        return estimate(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'estimate', count)
    with pytest.raises(RuntimeError, match='token counting failed'):
        prepare_commitments(calls, load_bank(ROOT/'bank'), literature, '')
    assert not payloads(calls, 'commitments_frozen')
    assert not payloads(calls, 'build_t_batch_skipped')
    assert len(payloads(calls, 'build_t_batch_accepted')) == 1
    rejected = [e for e in calls.log.read() if e['stage'] == 'build_t_batch' and e['label'] == 'MODEL'
                and json.loads(e['payload_json'])['status'] == 'rejected']
    assert len(rejected) == 1 and rejected[0]['usage']['output_tokens'] > 0


def test_admission_continues_after_borrowing_crosses_headroom(rig, monkeypatch):
    calls, provider, literature, sent = windows(rig, monkeypatch)
    estimate = provider.estimate
    def count(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'propose_targets':
            actual = sum(c['formula'].get('name') == 'F' for c in inputs['commitments']['commitments'])
            return TokenUsage(input_tokens=1000 if not actual else 82000 + (actual - 1) * 1000,
                              output_tokens=maximum)
        return estimate(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'estimate', count)
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), literature, '')
    assert len(result.commitments) == 3
    budgets = payloads(calls, 'build_t_window_budget')
    assert [b['working_remaining'] for b in budgets] == [99000, 18000, 17000]
    assert [b['budget']['per_window_commitments'] for b in budgets][1:] == [0, 0]
    assert [b['budget']['window_copy_token_budget'] for b in budgets][1:] == [0, 0]
    assert [i['batch_index'] for k, i in sent if k == 'build_t_batch'] == [0, 1, 2]
    assert payloads(calls, 'build_t_merged')[0]['input_tokens'] == 84000
    assert not payloads(calls, 'build_t_batch_skipped')
    assert len(payloads(calls, 'commitments_frozen')) == 1


@pytest.mark.parametrize('headroom', [.2, .01])
def test_small_global_capacity_admits_roots_above_planning_share(rig, monkeypatch, headroom):
    calls, provider, literature, sent = windows(rig, monkeypatch)
    calls.config.update(working_t_token_budget=1500, working_t_headroom_fraction=headroom)
    estimate = provider.estimate
    def count(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'propose_targets':
            actual = sum(c['formula'].get('name') == 'F' for c in inputs['commitments']['commitments'])
            return TokenUsage(input_tokens=1000 + actual * 100, output_tokens=maximum)
        return estimate(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'estimate', count)
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), literature, '')
    assert len(result.commitments) == 3
    assert payloads(calls, 'build_t_merged')[0]['input_tokens'] == 1300
    assert [b['working_remaining'] for b in payloads(calls, 'build_t_window_budget')] == [500, 400, 300]
    assert [i['batch_index'] for k, i in sent if k == 'build_t_batch'] == [0, 1, 2]
    assert not payloads(calls, 'build_t_batch_skipped')
    assert len(payloads(calls, 'commitments_frozen')) == 1


def test_mandatory_bundle_borrows_global_capacity_and_preserves_endpoints(rig, monkeypatch):
    from test_extraction_rich import rich_calls
    calls, provider, path = rich_calls(rig, monkeypatch)
    calls.config['working_t_symbol_token_budget'] = 1400
    sent = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        sent.append((kind, inputs))
        if kind == 'select_t_roots':
            root = next(i['root_id'] for p in inputs['papers'] for i in p['items'] if i['id'].endswith(':j'))
            value = dict(roots=[root], relevance='P', omissions=[dict(group_id=g['group_id'], reason='Q')
                         for g in inputs['selection_groups'] if set(g['root_ids']) - {root}])
        else:
            value = batch_response(inputs)
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), path.read_text(), '')
    assert {c.id.rsplit(':', 1)[1] for c in result.commitments} == {'j', 'r', 'f', 'qual', 'd'}
    selection = next(i for k, i in sent if k == 'select_t_roots')
    assert selection['window_budget']['per_window_commitments'] == 4
    closure = payloads(calls, 'build_t_closure')[0]
    assert closure['cut_depth'] == 0
    assert closure['support_omitted'] == {'p:r1-2:r': ['p:r1-2:i']}
    accounted = payloads(calls, 'build_t_evidence_accounted')[0]
    assert {o['evidence_id'].rsplit(':', 1)[1] for o in accounted['omitted']} == {'p', 'q', 'i'}
    assert len(payloads(calls, 'commitments_frozen')) == 1


@pytest.mark.parametrize('stage', ['select_t_roots', 'build_t_batch', 'correction'])
@pytest.mark.parametrize('status', [400, 200])
def test_terminal_provider_request_refusal_skips_window_at_reservation(rig, monkeypatch, stage, status):
    from anthropic import APIStatusError
    import httpx2 as httpx
    calls, provider, literature, sent = windows(rig, monkeypatch)
    complete = provider.complete
    def respond(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if inputs['batch_index'] == 1:
            if kind == stage or (stage == 'correction' and inputs.get('mode') == 'targeted_correction'):
                raise APIStatusError('P', response=httpx.Response(status, request=httpx.Request('POST', 'https://example.invalid'),
                    headers={'request-id': 'req_P'}), body={'error': {'type': 'invalid_request_error', 'message': 'P'}})
            if stage == 'correction' and kind == 'build_t_batch':
                value = json.loads(complete(kind, prompt, schema, maximum).text())
                value['commitments'][0]['formula']['name'] = 'Q'
                return Response(response(value))
        return complete(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'complete', respond)
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), literature, '')
    assert {c.id.rsplit(':', 1)[1] for c in result.commitments} == {'p', 'r'}
    refusal = payloads(calls, 'construction_provider_refusal')
    assert len(refusal) == 1 and refusal[0]['policy'] == 'count-at-reservation'
    summary = json.loads(methodology(calls.log.path).split('```json\n')[1].split('\n```')[0])
    assert summary['construction']['provider_refusals'] == refusal
    assert summary['accounting_complete'] is False
    unknown = [e for e in calls.log.read() if json.loads(e['payload_json']).get('accounting') == 'reservation_unknown_actual']
    assert len(unknown) == 1 and unknown[0]['cost_usd'] > 0
    start = next(p for p in payloads(calls, 'call_start') if p['cache_key'] == json.loads(unknown[0]['payload_json'])['cache_key'])
    assert unknown[0]['usage'] == start['reserved_usage']
    assert len(payloads(calls, 'build_t_batch_skipped')) == 1
    assert len(payloads(calls, 'commitments_frozen')) == 1


@pytest.mark.parametrize('status,error_type', [(500, 'invalid_request_error'), (401, 'authentication_error'), (429, 'rate_limit_error')])
def test_non_request_provider_failures_remain_fatal(rig, monkeypatch, status, error_type):
    from anthropic import APIStatusError
    import httpx2 as httpx
    calls, provider, literature, sent = windows(rig, monkeypatch)
    def fail(*args):
        raise APIStatusError('P', response=httpx.Response(status, request=httpx.Request('POST', 'https://example.invalid')),
                             body={'error': {'type': error_type, 'message': 'P'}})
    monkeypatch.setattr(provider, 'complete', fail)
    with pytest.raises(BudgetStop, match='provider accounting unavailable'):
        prepare_commitments(calls, load_bank(ROOT/'bank'), literature, '')
    assert not payloads(calls, 'construction_provider_refusal')
    assert not payloads(calls, 'commitments_frozen')
