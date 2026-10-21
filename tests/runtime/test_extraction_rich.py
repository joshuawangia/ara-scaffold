"""Rich argument graphs and counted construction, using placeholders only."""
import copy
import json
import pytest

from test_extraction import rig, offline, register, pdf, response, ROOT
from test_extraction_fix1 import add_image
from ara.runtime.cli import main
from ara.runtime.extraction import load_papers


from rich_fixture import graph


def test_rich_graph_preserves_structure(rig):
    calls, provider, papers, *_ = rig
    register(calls, provider, papers[0], graph())
    result = calls.extract_paper(papers[0])
    assert len(result.items) == 8
    ids = {x.id for x in result.items}
    links = [x for x in result.items if x.kind == 'inference']
    assert len(links) == 2 and len(links[0].premise_ids) == 2
    assert all(set(x.premise_ids) <= ids and x.conclusion_id in ids for x in links)
    assert all(x.inference_origin == 'paper_stated' for x in links)
    assert len({x.citation for x in result.items}) == 8


@pytest.mark.parametrize('mixed', [False, True])
def test_strict_partial_cli(rig, tmp_path, mixed):
    calls, provider, _, manifest, fulltext, config = rig
    pdf(fulltext / 'p.pdf', ('P', '') if mixed else ('',))
    add_image(fulltext / 'p.pdf', 1 if mixed else 0)
    directory = tmp_path / 'strict'
    def factory(config, log, topic):
        from ara.runtime.calls import ModelCalls
        return ModelCalls(config, provider, log, calls.cache, ROOT, topic)
    assert main(['extract', '--config', str(config), '--manifest', str(manifest),
                 '--fulltext-dir', str(fulltext), '--paper-id', 'p', '--missing', 'refuse',
                 '--run-dir', str(directory)], calls_factory=factory) == 2
    assert provider.calls == 0
    assert not (directory / 'literature.extracted.txt').exists()
    assert 'partial' in (directory / 'events.jsonl').read_text()


def rich_calls(rig, monkeypatch):
    from ara.runtime.extraction import extract
    from ara.runtime.providers import Response
    from rich_fixture import batch_response
    calls, provider, papers, *_ = rig
    register(calls, provider, papers[0], graph())
    path = extract(calls, (papers[0],))
    def complete(kind, prompt, schema, maximum):
        provider.calls += 1
        assert kind == 'build_t_batch'
        return Response(response(batch_response(json.loads(prompt.split('\nINPUT_JSON\n')[1]))))
    monkeypatch.setattr(provider, 'complete', complete)
    return calls, provider, path


@pytest.mark.parametrize('case', ['duplicate_id', 'duplicate_symbol', 'duplicate_citation', 'unknown_symbol',
    'symbol_arity', 'binding', 'qualification', 'inventory', 'attribution', 'omission_reason'])
def test_invalid_working_batch_refused_before_freeze(rig, monkeypatch, case):
    from ara.runtime.providers import Response
    from ara.runtime.calls import Rejected
    from ara.runtime.orchestration import prepare
    from ara.bank import load_bank
    from rich_fixture import batch_response
    calls, provider, path = rich_calls(rig, monkeypatch)
    def complete(kind, prompt, schema, maximum):
        value = batch_response(json.loads(prompt.split('\nINPUT_JSON\n')[1]))
        if case == 'duplicate_id': value['commitments'].append(value['commitments'][0])
        if case == 'duplicate_symbol': value['new_symbols'].append(value['new_symbols'][0])
        if case == 'duplicate_citation': value['commitments'][1]['citation'] = value['commitments'][0]['citation']
        if case == 'unknown_symbol': value['commitments'][0]['formula']['name'] = 'Q_Q'
        if case == 'symbol_arity': value['new_symbols'][0]['arity'] = 1
        if case == 'binding': value['bindings'][0]['evidence_ids'].pop()
        if case == 'qualification':
            item = value['commitments'].pop(5)
            value['omitted'].append({'evidence_id': item['id'], 'reason': 'P'})
            for symbol in value['new_symbols']:
                symbol['evidence_ids'] = [id for id in symbol['evidence_ids'] if id != item['id']]
            for binding in value['bindings']:
                binding['evidence_ids'] = [id for id in binding['evidence_ids'] if id != item['id']]
        if case == 'inventory': value['omitted'].append({'evidence_id': 'unknown', 'reason': 'P'})
        if case == 'attribution': value['commitments'][0]['text'] = 'P'
        if case == 'omission_reason':
            value['omitted'] = [{'evidence_id': c['id'], 'reason': ' '} for c in value['commitments']]
            value['commitments'] = []; value['bindings'] = []; value['new_symbols'] = []
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    with pytest.raises(Rejected):
        prepare(calls, load_bank(ROOT / 'bank'), path.read_text(), 'P')
    assert not any(e['stage'] == 'commitments_frozen' for e in calls.log.read())
    assert not (calls.log.path.parent / 'commitments.json').exists()


def test_merge_order_cache_replay_and_contradictions(rig, monkeypatch):
    from ara.runtime.construction import BatchResult, merge_batches
    from ara.types import CommitmentSet, Commitment, Formula
    calls, provider, path = rich_calls(rig, monkeypatch)
    first = calls.build_t(path.read_text(), 'P')
    before = provider.calls
    assert calls.build_t(path.read_text(), 'P') == first
    assert provider.calls == before
    from dataclasses import replace
    positive = replace(first.commitments[0], id='z')
    negative = Commitment('q', 'Q', 'q:pdf:1#q', positive.formula.negated())
    same_formula = Commitment('r', 'R', 'r:pdf:1#r', positive.formula)
    one = BatchResult(0, CommitmentSet((positive,)), '{}')
    two = BatchResult(1, CommitmentSet((negative, same_formula)), '{}')
    assert merge_batches((two, one), 2) == merge_batches((one, two), 2)
    assert [c.id for c in merge_batches((two, one), 2).commitments] == ['q', 'r', 'z']
    with pytest.raises(ValueError, match='batch id'): merge_batches((one, one), 2)
    with pytest.raises(ValueError, match='citation'):
        merge_batches((one, BatchResult(1, one.commitments, '{}')), 2)


@pytest.mark.parametrize('case', ['batch', 'downstream', 'working'])
def test_counted_capacity_refuses_explicitly(rig, monkeypatch, case):
    from ara.runtime.budget import BudgetStop
    from ara.types import TokenUsage
    calls, provider, path = rich_calls(rig, monkeypatch)
    if case == 'batch':
        calls.config['build_t_batch_input_tokens'] = 1
        with pytest.raises(BudgetStop, match='oversized source batch'):
            calls.build_t(path.read_text(), 'P')
        assert provider.calls == 1
    else:
        t = calls.build_t(path.read_text(), 'P')
        before = provider.calls
        if case == 'downstream':
            monkeypatch.setattr(provider, 'estimate', lambda *a: TokenUsage(input_tokens=200001))
            with pytest.raises(BudgetStop, match='propose_targets context bound'):
                calls.propose_targets(t)
            assert provider.calls == before
        else:
            calls.config['working_t_token_budget'] = 8001
            from ara.runtime.calls import Rejected
            with pytest.raises(Rejected, match='working T batch token allowance'):
                calls.build_t(path.read_text(), 'P')
    assert not any(e['stage'] == 'commitments_frozen' for e in calls.log.read())


def test_page_ranges_and_logged_reconciliation(rig, monkeypatch):
    from ara.runtime.extraction import Paper, PageText, extract, HEADER
    from ara.runtime.providers import Response
    from ara.types import TokenUsage
    calls, provider, papers, *_ = rig
    paper = Paper('p', papers[0].record_json, 'P', (PageText(1, 'P'), PageText(2, 'Q')))
    seen = []
    def estimate(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        return TokenUsage(input_tokens=200001 if len(data.get('pages', [])) > 1 else 100, output_tokens=maximum)
    def complete(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1]); seen.append(data)
        if data.get('mode') == 'reconcile_ranges':
            value = graph(); value['items'] = []
        else: value = graph(page=data['pages'][0]['page'])
        return Response(response(value))
    monkeypatch.setattr(provider, 'estimate', estimate)
    monkeypatch.setattr(provider, 'complete', complete)
    path = extract(calls, (paper,))
    items = json.loads(path.read_text()[len(HEADER):])['papers'][0]['items']
    assert len(items) == 16 and len({x['id'] for x in items}) == 16
    assert [x['pages'][0]['page'] for x in seen if 'pages' in x] == [1, 2]
    assert seen[-1]['mode'] == 'reconcile_ranges'
    assert len([e for e in calls.log.read() if e['label'] == 'MODEL']) == 3
    assert len(list(calls.log.path.parent.glob('p.r*.rich.json'))) == 2


@pytest.mark.parametrize('case', ['id', 'endpoint', 'origin', 'coverage'])
def test_rich_graph_rejects_invalid_links(rig, case):
    from ara.runtime.calls import Rejected
    calls, provider, papers, *_ = rig
    value = graph()
    if case == 'id': value['items'].append(copy.deepcopy(value['items'][0]))
    if case == 'endpoint': value['items'][-1]['premise_ids'] = ['unknown']
    if case == 'origin': value['items'][-1]['inference_origin'] = None
    if case == 'coverage': value['coverage_complete'] = False
    # Single readable page prevents subdivision from hiding the invalid graph.
    from ara.runtime.extraction import Paper
    paper = Paper('p', papers[0].record_json, 'P', papers[0].pages[:1])
    register(calls, provider, paper, value)
    with pytest.raises(Rejected): calls.extract_paper(paper)
    assert not list(calls.cache.path.glob('*.json'))
    assert all(json.loads(e['payload_json'])['status'] == 'rejected' for e in calls.log.read() if e['label'] == 'MODEL')


def test_no_compact_summary_limit(rig):
    calls, provider, papers, *_ = rig
    value = graph()
    value['items'][0]['text'] = 'P ' * 1000
    register(calls, provider, papers[0], value)
    result = calls.extract_paper(papers[0])
    assert len(result.items) == 8 and len(result.items[0].text) == 2000


def test_plan_identity_and_source_order(rig, monkeypatch):
    from ara.runtime.extraction import HEADER
    from ara.runtime.cache import canonical
    calls, provider, path = rich_calls(rig, monkeypatch)
    text = path.read_text()
    first = calls.build_t(text, 'P')
    plan = next(json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'build_t_plan')
    calls.config['build_t_batch_input_tokens'] -= 1
    assert calls.build_t(text, 'P') == first
    plans = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'build_t_plan']
    assert plans[-1]['plan_id'] != plan['plan_id']
    assert provider.calls == 3  # extraction plus two differently keyed constructions
    assert plans[-1]['plan']['sources'][0]['content_hash'] == plan['plan']['sources'][0]['content_hash']


def test_freeze_is_unique_and_immutable(rig, monkeypatch):
    from ara.bank import load_bank
    from ara.runtime.orchestration import prepare_commitments
    calls, provider, path = rich_calls(rig, monkeypatch)
    bank = load_bank(ROOT / 'bank')
    prepare_commitments(calls, bank, path.read_text(), 'P')
    snapshot = (calls.log.path.parent / 'commitments.json').read_bytes()
    with pytest.raises(ValueError, match='already frozen'):
        prepare_commitments(calls, bank, path.read_text(), 'P')
    assert (calls.log.path.parent / 'commitments.json').read_bytes() == snapshot
    assert sum(e['stage'] == 'commitments_frozen' for e in calls.log.read()) == 1


def test_encoding_warning_retains_text_and_rejects_strict(rig, monkeypatch):
    from ara.runtime.extraction import extract
    from pypdf._page import PageObject
    calls, provider, _, manifest, fulltext, _ = rig
    monkeypatch.setattr(PageObject, 'extract_text', lambda *a, **kw: 'P\uf700Q')
    paper = load_papers(manifest, fulltext, ('p',))[0]
    assert paper.affected_pages == (1, 2) and len(paper.readable_pages) == 2
    assert all(d.reason == 'private_use_glyphs' for d in paper.diagnostics)
    register(calls, provider, paper, graph())
    result = extract(calls, (paper,))
    assert 'partial' in result.read_text() and 'P' in result.read_text()
    with pytest.raises(ValueError, match='partial text coverage'):
        extract(calls, (paper,), missing='refuse')


def test_legacy_artifact_not_treated_as_human(rig, tmp_path):
    from ara.runtime.extraction import literature_provenance
    legacy = tmp_path / 'legacy.txt'
    legacy.write_text('# ARA extracted literature v1\nP')
    with pytest.raises(ValueError, match='unsupported extraction artifact version'):
        literature_provenance(legacy, legacy.read_text())


def test_output_exhaustion_splits_without_truncation(rig, monkeypatch):
    from ara.runtime.extraction import extract, HEADER
    from ara.runtime.providers import Response
    calls, provider, papers, *_ = rig
    def complete(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if len(data.get('pages', [])) == 2:
            raw = response({}); raw['stop_reason'] = 'max_tokens'
        elif data.get('mode') == 'reconcile_ranges':
            value = graph(); value['items'] = []; raw = response(value)
        else: raw = response(graph(page=data['pages'][0]['page']))
        return Response(raw)
    monkeypatch.setattr(provider, 'complete', complete)
    path = extract(calls, (papers[0],))
    assert len(json.loads(path.read_text()[len(HEADER):])['papers'][0]['items']) == 16
    model = [e for e in calls.log.read() if e['label'] == 'MODEL']
    assert len(model) == 4 and all(e['cost_usd'] > 0 for e in model)
    assert json.loads(model[0]['payload_json'])['status'] == 'rejected'
    assert sum(e['stage'] == 'extraction_range_split' for e in calls.log.read()) == 1


@pytest.mark.parametrize('case', ['final_budget', 'symbols'])
def test_construction_final_capacity_guard(rig, monkeypatch, case):
    from ara.runtime.orchestration import prepare_commitments
    from ara.runtime.budget import BudgetStop
    from ara.runtime.calls import Rejected
    from ara.bank import load_bank
    from ara.types import TokenUsage
    calls, provider, path = rich_calls(rig, monkeypatch)
    if case == 'final_budget':
        estimate = provider.estimate
        monkeypatch.setattr(provider, 'estimate', lambda kind, *args: TokenUsage(input_tokens=100001)
                            if kind == 'propose_targets' else estimate(kind, *args))
        error, message = BudgetStop, 'working T downstream token budget'
    else:
        calls.config['working_t_symbol_token_budget'] = 1
        error, message = Rejected, 'shared symbol token allowance'
    with pytest.raises(error, match=message):
        prepare_commitments(calls, load_bank(ROOT / 'bank'), path.read_text(), 'P')
    assert not any(e['stage'] == 'commitments_frozen' for e in calls.log.read())


def test_cached_context_is_recounted(rig, monkeypatch):
    from ara.runtime.providers import mock_key
    from ara.runtime.budget import BudgetStop
    from ara.types import Proposition, TokenUsage
    calls, provider, *_ = rig
    proposition = Proposition('p', 'P')
    prompt = calls.render('formalise', {'proposition': proposition.to_dict()})[1]
    provider.responses[mock_key('formalise', prompt)] = response({'formula': {'op': 'atom', 'name': 'P'}})
    calls.formalise(proposition)
    monkeypatch.setattr(provider, 'estimate', lambda *a: TokenUsage(input_tokens=200001))
    with pytest.raises(BudgetStop, match='formalise context bound'):
        calls.formalise(proposition)
    assert provider.calls == 1


@pytest.mark.parametrize('valid', [True, False])
def test_encoded_batch_formula_still_requires_local_validation(rig, monkeypatch, valid):
    from ara.runtime.calls import Rejected
    from ara.runtime.cache import canonical
    from ara.runtime.providers import Response
    from rich_fixture import batch_response
    calls, provider, path = rich_calls(rig, monkeypatch)
    def complete(kind, prompt, schema, maximum):
        value = batch_response(json.loads(prompt.split('\nINPUT_JSON\n')[1]))
        for c in value['commitments']:
            c['formula'] = canonical(c['formula']) if valid else 'P'
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    if valid:
        result = calls.build_t(path.read_text(), 'P')
        assert len(result.commitments) == 8
        assert sum(c.formula.op == 'implies' for c in result.commitments) == 2
    else:
        with pytest.raises(Rejected, match='encoded formula'):
            calls.build_t(path.read_text(), 'P')
        event = [e for e in calls.log.read() if e['label'] == 'MODEL'][-1]
        assert json.loads(event['payload_json'])['status'] == 'rejected'
        assert json.loads(event['payload_json'])['accounting'] == 'actual'


@pytest.mark.parametrize('locally_bound', [True, False])
def test_batch_variables_cannot_bypass_symbol_contract(rig, monkeypatch, locally_bound):
    from ara.runtime.calls import Rejected
    from ara.runtime.providers import Response
    from rich_fixture import batch_response
    calls, provider, path = rich_calls(rig, monkeypatch)
    def complete(kind, prompt, schema, maximum):
        value = batch_response(json.loads(prompt.split('\nINPUT_JSON\n')[1]))
        formula = {'op': 'predicate', 'name': 'F', 'terms': [{'kind': 'variable', 'name': 'x'}]}
        if locally_bound: formula = {'op': 'forall', 'variable': 'x', 'args': [formula]}
        for c in value['commitments']: c['formula'] = formula
        ids = [c['id'] for c in value['commitments']]
        value['new_symbols'] = [dict(name='F', kind='predicate', arity=1, definition='F(x)', evidence_ids=ids)]
        value['bindings'] = [dict(name='F', evidence_ids=ids)]
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    if locally_bound:
        assert all(c.formula.op == 'forall' for c in calls.build_t(path.read_text(), 'P').commitments)
    else:
        with pytest.raises(Rejected, match='locally bound'):
            calls.build_t(path.read_text(), 'P')
