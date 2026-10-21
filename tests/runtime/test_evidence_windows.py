"""Full-corpus boundary proofs using placeholder evidence only."""
import copy
import json

import pytest
import yaml

from ara.bank import load_bank
from ara.runtime.calls import Rejected
from ara.runtime.cli import main
from ara.runtime.extraction import Paper, PageText, HEADER
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.providers import Response
from ara.types import TokenUsage
from rich_fixture import graph, batch_response
from test_extraction import rig, offline, response, ROOT
from test_extraction_rich import rich_calls




def test_large_single_graph_windows_close_against_full_evidence(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    data = json.loads(path.read_text()[len(HEADER):])
    paper = data['papers'][0]
    original = copy.deepcopy(paper['items'])
    decoys = []
    for index in range(90):
        item = copy.deepcopy(original[0])
        item.update(id=f'p:r1-2:z{index}', citation=f'p:pdf:1#p:r1-2:z{index}', text='P ' * 1600)
        decoys.append(item)
    paper['items'] = original[:3] + decoys[:45] + original[3:6] + decoys[45:] + original[6:]
    seen = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1]); seen.append((kind, inputs))
        assert len(prompt.encode()) + maximum <= calls.config['model_context_token_bound']
        if kind == 'select_t_roots':
            roots = [i['root_id'] for p in inputs['papers'] for i in p['items'] if i['id'].endswith(':f')]
            value = dict(roots=roots, relevance='P', omissions=[dict(group_id=g['group_id'], reason='Q')
                for g in inputs['selection_groups'] if set(g['root_ids']) - set(roots)])
        else: value = batch_response(inputs)
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    t = prepare_commitments(calls, load_bank(ROOT/'bank'), HEADER + json.dumps(data), 'P')
    assert {c.id for c in t.commitments} == {i['id'] for i in original}
    assert sum(kind == 'select_t_roots' for kind, _ in seen) > 2
    assert sum(kind == 'build_t_batch' for kind, _ in seen) == 1
    events = calls.log.read()
    ledger = next(json.loads(e['payload_json']) for e in events if e['stage'] == 'build_t_evidence_accounted')
    assert set(ledger['selected_ids']) == {i['id'] for i in original}
    assert {o['evidence_id'] for o in ledger['omitted']} == {i['id'] for i in decoys}
    assert sum(e['stage'] == 'commitments_frozen' for e in events) == 1


@pytest.mark.parametrize('resolve', [True, False])
def test_reconcile_over_context_with_requested_cross_window_evidence(rig, monkeypatch, resolve):
    calls, provider, papers, *_ = rig
    calls.config.update(token_cap=10000000, cost_cap_usd=100, extraction_cost_cap_usd=100)
    paper = Paper('p', papers[0].record_json, 'P', tuple(PageText(n, 'P ' * 30000) for n in range(1,7)))
    seen = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1]); seen.append(inputs)
        assert len(prompt.encode()) + maximum <= 200000
        value = graph(); value['items'] = []
        pages = {p['page'] for p in inputs.get('pages', [])}
        if inputs.get('mode') != 'reconcile_ranges':
            if 1 in pages:
                value['items'].append(graph(page=1)['items'][0])
                value.update(coverage_complete=False, unresolved_references=['Q'])
            if 6 in pages: value['items'].append(graph(page=6)['items'][1])
            if not value['items']: value['empty_reason'] = 'P'
        elif inputs['obligations']:
            obligation = inputs['obligations'][0]['id']
            if {1,6} <= pages and resolve:
                existing = [i for r in inputs['ranges'] for i in r['items']]
                p = next(i['id'] for i in existing if i['id'].endswith(':p'))
                q = next(i['id'] for i in existing if i['id'].endswith(':q'))
                link = graph(page=6)['items'][6]
                link.update(premise_ids=[p], conclusion_id=q, qualification_ids=[])
                value['items'] = [link]
                value['resolutions'] = [dict(obligation_id=obligation, evidence_ids=['i', p, q])]
            else:
                value.update(coverage_complete=False, unresolved_references=['Q'], pending_obligation_ids=[obligation])
                if resolve: value['context_request'] = {'pages': [1,6], 'evidence_ids': []}
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    if resolve:
        result = calls.extract_paper(paper).to_dict()
        assert len(result['items']) == 3
        assert len(result['obligations']) == len(result['resolutions']) == 1
        link = next(i for i in result['items'] if i['kind'] == 'inference')
        assert link['premise_ids'] == ('p:r1-1:p',) or link['premise_ids'] == ['p:r1-1:p']
        assert link['conclusion_id'].endswith(':q')
        assert any({p['page'] for p in i.get('pages', [])} == {1,6} for i in seen)
    else:
        with pytest.raises(Rejected, match='unresolved obligation'): calls.extract_paper(paper)
        assert not (calls.log.path.parent/'literature.extracted.txt').exists()
    assert not any(len(i.get('pages', [])) == 6 for i in seen)
    assert len(list(calls.log.path.parent.glob('p.r*.rich.json'))) > 1


def test_oversized_selected_closure_refuses_before_formalization(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    original = provider.estimate
    sent = []
    def estimate(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'build_t_batch' and inputs.get('closure'):
            return TokenUsage(input_tokens=70001, output_tokens=maximum)
        return original(kind, prompt, schema, maximum)
    def complete(kind, prompt, schema, maximum):
        sent.append(kind)
        return Response(response(batch_response(json.loads(prompt.split('\nINPUT_JSON\n')[1]))))
    monkeypatch.setattr(provider, 'estimate', estimate)
    monkeypatch.setattr(provider, 'complete', complete)
    from ara.runtime.budget import BudgetStop
    with pytest.raises(BudgetStop, match='selected closure'):
        prepare_commitments(calls, load_bank(ROOT/'bank'), path.read_text(), 'P')
    assert sent == ['select_t_roots']
    assert not any(e['stage'] == 'commitments_frozen' for e in calls.log.read())


def test_no_obligation_review_bounds_large_graph_union(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config.update(token_cap=10000000, cost_cap_usd=100, extraction_cost_cap_usd=100)
    paper = Paper('p', papers[0].record_json, 'P', tuple(PageText(n, 'P ' * 30000) for n in range(1,7)))
    reviewed = set()
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        assert len(prompt.encode()) + maximum <= 200000
        value = graph(); value['items'] = []
        if inputs.get('mode') == 'reconcile_ranges':
            reviewed.update(i['id'] for r in inputs['ranges'] for i in r['items'])
        else:
            for page in inputs['pages']:
                item = graph(page=page['page'])['items'][0]
                item.update(id=f'p{page["page"]}', text='P ' * 30000)
                value['items'].append(item)
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    result = calls.extract_paper(paper)
    assert len(result.items) == 6
    assert reviewed == {i.id for i in result.items}
    windows = [e for e in calls.log.read() if e['stage'] == 'extraction_reconciliation_window']
    assert len(windows) > 1
    assert result.obligations_json == result.resolutions_json == '[]'
