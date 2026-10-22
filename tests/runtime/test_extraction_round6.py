"""Per-paper admission limits, using counted placeholder responses only."""
from collections import Counter
import json

import pytest

from ara.runtime.budget import BudgetStop
from ara.runtime.extraction import Paper, PageText, extract
from ara.runtime.providers import Response
from ara.types import TokenUsage
from rich_fixture import graph
from test_extraction import rig, offline, response


def chain(rig, monkeypatch, *, finish=7, **limits):
    calls, provider, papers, *_ = rig
    calls.config.update(calls.config['extraction-full'])
    calls.config.update(token_cap=12000000, cost_cap_usd=125, extraction_cost_cap_usd=125,
                        reconciliation_context_requests=0, extraction_max_failed_papers=0, **limits)
    sent = []
    counts = Counter()

    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        source = inputs['source_id']
        sent.append(inputs)
        counts[source] += 1
        value = graph(source)
        if inputs.get('mode') == 'reconcile_ranges':
            value['items'] = []
            value['resolutions'] = [dict(obligation_id=inputs['obligations'][0]['id'],
                evidence_ids=[inputs['ranges'][0]['items'][0]['id']])]
        if counts[source] < finish:
            value.update(coverage_complete=False, new_gaps=[{'description': 'Q'}])
        return Response(response(value))

    monkeypatch.setattr(provider, 'estimate', lambda kind, prompt, schema, maximum:
                        TokenUsage(input_tokens=100, output_tokens=maximum))
    monkeypatch.setattr(provider, 'complete', complete)
    paper = Paper('p', papers[0].record_json, 'P', (PageText(1, 'P'),))
    return calls, provider, paper, sent


def test_descendant_chain_stops_at_paper_count_with_budget_remaining(rig, monkeypatch):
    calls, _, paper, sent = chain(rig, monkeypatch,
        extraction_paper_continuation_limit=0, extraction_paper_cost_cap_usd=15)
    path = extract(calls, (paper,))
    assert len(sent) == 1 and float(calls.budget.used_cost) == .00175
    outcome = json.loads((path.parent/'p.extraction.json').read_text())
    assert len(outcome['items']) == 8 and len(outcome['obligations']) == 1
    assert any('paper continuation limit' in d['reason'] for d in outcome['dispositions'])


def test_paper_dollars_reserve_before_dispatch(rig, monkeypatch):
    calls, _, paper, sent = chain(rig, monkeypatch,
        extraction_paper_continuation_limit=24, extraction_paper_cost_cap_usd=.802)
    path = extract(calls, (paper,))
    assert len(sent) == 1 and float(calls.budget.used_cost) == .00175
    outcome = json.loads((path.parent/'p.extraction.json').read_text())
    assert len(outcome['items']) == 8
    assert any('paper cost cap' in d['reason'] for d in outcome['dispositions'])


def test_multi_paper_allowances_reset_at_paper_boundary(rig, monkeypatch):
    calls, _, first, sent = chain(rig, monkeypatch, finish=2,
        extraction_paper_continuation_limit=1, extraction_paper_cost_cap_usd=.8025)
    second = Paper('q', json.dumps({'id': 'q', 'title': 'Q'}), 'Q', (PageText(1, 'Q'),))
    path = extract(calls, (first, second))
    assert [i['source_id'] for i in sent] == ['p'] * 2 + ['q'] * 2
    assert float(calls.budget.used_cost) == .007
    admissions = [json.loads(e['payload_json']) for e in calls.log.read()
                  if e['stage'] == 'extraction_paper_attempt']
    assert [a['paper_continuations'] for a in admissions] == [0, 1, 0, 1]
    assert path.exists()


@pytest.mark.parametrize('strategy', ['retry', 'correction'])
@pytest.mark.parametrize('at', ['initial'])
def test_retries_and_corrections_consume_same_allowance(rig, monkeypatch, strategy, at):
    limit = 0 if at == 'initial' else 1
    calls, provider, paper, sent = chain(rig, monkeypatch,
        extraction_paper_continuation_limit=limit, extraction_paper_cost_cap_usd=15)
    calls.config['validation_attempts'] = 3
    if strategy == 'retry':
        del calls.config['extraction_targeted_corrections']
    original = provider.complete

    def invalid(kind, prompt, schema, maximum):
        result = original(kind, prompt, schema, maximum)
        if len(sent) == limit + 1:
            value = json.loads(result.text())
            value['source_id'] = 'q'
            return Response(response(value))
        return result

    monkeypatch.setattr(provider, 'complete', invalid)
    with pytest.raises(BudgetStop, match='paper continuation limit'):
        extract(calls, (paper,))
    assert len(sent) == limit + 1
    events = calls.log.read()
    models = [e for e in events if e['label'] == 'MODEL']
    assert len(models) == limit + 1
    assert json.loads(models[-1]['payload_json'])['status'] == 'rejected'
    assert float(calls.budget.used_cost) == .00175 * (limit + 1)
    retry_stage = 'validation_retry' if strategy == 'retry' else 'extraction_targeted_correction'
    assert any(e['stage'] == retry_stage for e in events)
    stop = json.loads((calls.log.path.parent/'partial.json').read_text())
    assert stop['source_id'] == 'p'
    assert len(stop['pending_obligation_ids']) == limit
    assert (calls.log.path.parent/'literature.extracted.txt').exists()


def test_paper_actual_cost_overrun_keeps_measured_response(rig, monkeypatch):
    calls, provider, paper, sent = chain(rig, monkeypatch, finish=1,
        extraction_paper_continuation_limit=24, extraction_paper_cost_cap_usd=.9)
    original = provider.complete

    def expensive(*args):
        result = original(*args)
        result.raw['usage'] = {'input_tokens': 100, 'output_tokens': 40000}
        return result

    monkeypatch.setattr(provider, 'complete', expensive)
    with pytest.raises(BudgetStop, match='paper cost cap exceeded by actual usage'):
        extract(calls, (paper,))
    assert len(sent) == 1
    events = calls.log.read()
    models = [e for e in events if e['label'] == 'MODEL']
    assert len(models) == 1 and models[0]['response']
    assert models[0]['cost_usd'] == 1.0005
    stop = json.loads((calls.log.path.parent/'partial.json').read_text())
    assert stop['source_id'] == 'p' and stop['paper_cost_usd'] == 1.0005
    assert (calls.log.path.parent/'literature.extracted.txt').exists()


def test_same_paper_reentry_does_not_reset_allowance(rig, monkeypatch):
    calls, _, paper, sent = chain(rig, monkeypatch, finish=1,
        extraction_paper_continuation_limit=0, extraction_paper_cost_cap_usd=15)
    calls.extract_paper(paper)
    with pytest.raises(BudgetStop, match='paper continuation limit'):
        calls.extract_paper(paper)
    assert len(sent) == 1
    assert float(calls.budget.used_cost) == .00175


@pytest.mark.parametrize('key,value', [
    ('extraction_paper_continuation_limit', -1),
    ('extraction_paper_continuation_limit', 1.5),
    ('extraction_paper_continuation_limit', float('inf')),
    ('extraction_paper_continuation_limit', True),
    ('extraction_paper_continuation_limit', None),
    ('extraction_paper_cost_cap_usd', -1),
    ('extraction_paper_cost_cap_usd', float('nan')),
    ('extraction_paper_cost_cap_usd', float('inf')),
    ('extraction_paper_cost_cap_usd', True),
    ('extraction_paper_cost_cap_usd', None),
    ('extraction_large_paper_limits', {'min_pages': 300, 'continuation_limit': 48, 'cost_cap_usd': float('inf')}),
    ('extraction_large_paper_limits', {'min_pages': 300}),
])
def test_invalid_paper_limits_refuse_before_dispatch(rig, monkeypatch, key, value):
    calls, _, paper, sent = chain(rig, monkeypatch, **{key: value})
    with pytest.raises(ValueError, match=r'^(extraction_paper_|extraction_large_paper_limits |large paper )'):
        calls.extract_paper(paper)
    assert not sent
    assert not any(e['stage'] == 'call_start' for e in calls.log.read())


@pytest.mark.parametrize('pages,count,dollars', [(299, 24, 15), (300, 48, 30), (358, 48, 30)])
def test_full_profile_selects_finite_large_paper_allowance(rig, monkeypatch, pages, count, dollars):
    calls, _, paper, sent = chain(rig, monkeypatch)
    calls.config['token_cap'] = 0
    paper = Paper('p', paper.record_json, 'P', tuple(PageText(n, 'P') for n in range(1, pages + 1)))
    with pytest.raises(BudgetStop, match='token cap'):
        calls.extract_paper(paper)
    assert not sent
    allowance = next(json.loads(e['payload_json']) for e in calls.log.read()
                     if e['stage'] == 'extraction_paper_allowance')
    assert allowance['paper_continuation_limit'] == count
    assert allowance['paper_cost_cap_usd'] == dollars


def test_stop_lists_all_pending_descendants(rig, monkeypatch):
    calls, provider, paper, sent = chain(rig, monkeypatch,
        extraction_paper_continuation_limit=1, extraction_paper_cost_cap_usd=15)
    original = provider.complete
    def extra_gap(*args):
        result = original(*args)
        value = json.loads(result.text())
        if len(sent) == 1: value['new_gaps'].append({'description': 'R'})
        elif len(sent) == 2: value['pending_obligation_ids'] = ['p:r1-1:turn:1:gap:1']
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', extra_gap)
    path = extract(calls, (paper,))
    assert len(sent) == 2
    outcome = json.loads((path.parent/'p.extraction.json').read_text())
    assert len(outcome['obligations']) == 3 and len(outcome['resolutions']) == 1
    assert len(outcome['items']) == 8


def test_same_paper_reentry_retains_prior_cost(rig, monkeypatch):
    calls, _, paper, sent = chain(rig, monkeypatch, finish=1,
        extraction_paper_continuation_limit=24, extraction_paper_cost_cap_usd=15)
    calls.extract_paper(paper)
    calls.config['extraction_paper_cost_cap_usd'] = .8006
    calls.config['stages']['extraction']['effort'] = 'low'
    with pytest.raises(BudgetStop, match='paper cost cap'):
        calls.extract_paper(paper)
    assert len(sent) == 1
    stop = json.loads((calls.log.path.parent/'partial.json').read_text())
    assert stop['paper_cost_usd'] == .00175


@pytest.mark.parametrize('strategy', ['retry', 'correction'])
def test_retry_reservation_uses_paper_dollars(rig, monkeypatch, strategy):
    calls, provider, paper, sent = chain(rig, monkeypatch,
        extraction_paper_continuation_limit=24, extraction_paper_cost_cap_usd=.8006)
    calls.config['validation_attempts'] = 3
    if strategy == 'retry':
        del calls.config['extraction_targeted_corrections']
    original = provider.complete

    def invalid(*args):
        result = original(*args)
        value = json.loads(result.text())
        value['source_id'] = 'q'
        return Response(response(value))

    monkeypatch.setattr(provider, 'complete', invalid)
    with pytest.raises(BudgetStop, match='paper cost cap'):
        extract(calls, (paper,))
    assert len(sent) == 1
    assert float(calls.budget.used_cost) == .00175
    assert json.loads((calls.log.path.parent/'partial.json').read_text())['source_id'] == 'p'


def test_unknown_usage_retains_paper_reservation(rig, monkeypatch):
    calls, provider, paper, _ = chain(rig, monkeypatch,
        extraction_paper_continuation_limit=24, extraction_paper_cost_cap_usd=15)

    def unavailable(*args):
        raise OSError('P')

    monkeypatch.setattr(provider, 'complete', unavailable)
    with pytest.raises(BudgetStop, match='actual spend unknown'):
        extract(calls, (paper,))
    model = next(e for e in calls.log.read() if e['label'] == 'MODEL')
    assert model['cost_usd'] == .8005
    assert json.loads(model['payload_json'])['accounting'] == 'reservation_unknown_actual'
    stop = json.loads((calls.log.path.parent/'partial.json').read_text())
    assert stop['source_id'] == 'p' and stop['paper_cost_usd'] == .8005
