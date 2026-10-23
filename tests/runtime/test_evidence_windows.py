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


def test_windows_keep_only_selected_metadata(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    data = json.loads(path.read_text()[len(HEADER):])
    paper = data['papers'][0]
    original = copy.deepcopy(paper['items'])
    for n, item in enumerate(paper['items']):
        item.update(page_start=n + 1, page_end=n + 1)
    paper.update(title='P', authors=['a'], status='partial', record={'title': 'Q', 'extra': 'R'},
                 snapshot_union={'snapshots': {'foreign': 'R' * 100000}},
                 dispositions=[{'reason': 'R' * 100000}], unknown_metadata='R' * 100000)
    paper['item_provenance'] = {i['id']: [dict(snapshot_id='a', original_id=i['id'])] for i in paper['items']}
    paper['open_gaps'] = [dict(id=i['id'] + ':gap', description='Q', pages=[i['page_start']], snapshot_id='a')
                          for i in paper['items']]
    paper['open_gaps'] += [dict(id='foreign', description='R', pages=[1], snapshot_id='b'),
                           dict(id='unscoped', description='R')]
    from ara.runtime.grounding import ground_outcome
    data['papers'][0] = paper = ground_outcome(
        Paper('p', '{}', 'P', tuple(PageText(n, 'P Q R F(x)') for n in range(1, 9))), paper, calls.log)
    # A valid quarantine receipt for unrelated inventory must not reach a window.
    from ara.runtime.grounding import receipt_hash
    paper['quarantined'] = [dict(item_id='foreign', reasons=['P'], blocked_by=[])]
    paper['grounding']['inventory_sha256'] = receipt_hash(paper['items'], paper['quarantined'],
                                                        paper['grounding']['source_text_sha256'])
    text = HEADER + json.dumps(data)
    original_estimate = provider.estimate
    observed = []
    def check(inputs):
        for window in inputs.get('papers', []):
            ids = {i['id'] for i in window['items']}
            assert set(window) == {'source_id', 'title', 'authors', 'partial_source', 'items',
                                   'item_provenance', 'quarantined', 'open_gaps'}
            assert (window['source_id'], window['title'], window['authors'], window['partial_source']) == ('p', 'P', ['a'], True)
            assert set(window['item_provenance']) == ids
            assert window['quarantined'] == []
            assert {g['id'] for g in window['open_gaps']} == {id + ':gap' for id in ids}
            assert all({k: v for k, v in i.items() if k != 'root_id'} in paper['items'] for i in window['items'])
    def estimate(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind in ('build_t_batch', 'select_t_roots'):
            check(inputs)
            if kind == 'select_t_roots' and sum(len(p['items']) for p in inputs['papers']) > 4:
                return TokenUsage(input_tokens=70001, output_tokens=maximum)
        return original_estimate(kind, prompt, schema, maximum)
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        check(inputs)
        observed.append(kind)
        return Response(response(batch_response(inputs)))
    monkeypatch.setattr(provider, 'estimate', estimate)
    monkeypatch.setattr(provider, 'complete', complete)
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), text, 'P')
    assert {c.id for c in result.commitments} == {i['id'] for i in original}
    assert {c.citation for c in result.commitments} == {i['citation'] for i in original}
    assert observed.count('select_t_roots') == 2 and 'build_t_batch' in observed
    assert json.loads(text[len(HEADER):]) == data




def test_large_single_graph_windows_close_against_full_evidence(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    calls.config.update(working_t_token_budget=200000, working_t_symbol_token_budget=32000)
    data = json.loads(path.read_text()[len(HEADER):])
    paper = data['papers'][0]
    original = copy.deepcopy(paper['items'])
    decoys = []
    for index in range(90):
        item = copy.deepcopy(original[0])
        item.update(id=f'p:r1-2:z{index}', citation=f'p:pdf:1#p:r1-2:z{index}', text='P ' * 1600)
        decoys.append(item)
    paper['items'] = original[:3] + decoys[:45] + original[3:6] + decoys[45:] + original[6:]
    from ara.runtime.grounding import ground_outcome
    data['papers'][0] = ground_outcome(Paper('p', '{}', 'P', (PageText(1, 'P Q R F(x)'),)), paper, calls.log)
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
    # Earlier empty windows release their unused shares to this root's full closure.
    expected = {i['id'] for i in original}
    assert {c.id for c in t.commitments} == expected
    assert sum(kind == 'select_t_roots' for kind, _ in seen) > 2
    assert sum(kind == 'build_t_batch' for kind, _ in seen) == 1
    events = calls.log.read()
    ledger = next(json.loads(e['payload_json']) for e in events if e['stage'] == 'build_t_evidence_accounted')
    assert set(ledger['selected_ids']) == expected
    assert {o['evidence_id'] for o in ledger['omitted']} == {i['id'] for i in paper['items']} - expected
    closure = next(json.loads(e['payload_json']) for e in events
                   if e['stage'] == 'build_t_closure' and json.loads(e['payload_json'])['roots'])
    assert set(closure['uncut_inventory']) == {i['id'] for i in original}
    assert closure['support_omitted'] == {}
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
                value.update(coverage_complete=False, new_gaps=[{'description': 'Q'}])
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
                value.update(coverage_complete=False, new_gaps=[], pending_obligation_ids=[obligation])
                if resolve: value['context_request'] = {'pages': [1,6], 'evidence_ids': []}
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    result = calls.extract_paper(paper).to_dict()
    assert len(result['items']) == 2
    assert len(result['obligations']) == 1 and not result['resolutions']
    assert any(d['kind'] == 'reconciliation_failed' for d in result['dispositions'])
    assert not any(len(i.get('pages', [])) == 6 for i in seen)
    assert len(list(calls.log.path.parent.glob('p.r*.rich.json'))) > 1


def test_oversized_selected_closure_refuses_before_formalization(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    original = provider.estimate
    sent = []
    def estimate(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'build_t_batch' and inputs.get('closure') and any(e['stage'] == 'build_t_closure' for e in calls.log.read()):
            return TokenUsage(input_tokens=70001, output_tokens=maximum)
        return original(kind, prompt, schema, maximum)
    def complete(kind, prompt, schema, maximum):
        sent.append(kind)
        return Response(response(batch_response(json.loads(prompt.split('\nINPUT_JSON\n')[1]))))
    monkeypatch.setattr(provider, 'estimate', estimate)
    monkeypatch.setattr(provider, 'complete', complete)
    from ara.runtime.calls import Rejected
    with pytest.raises(Rejected, match='empty working T.*selected closure'):
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
    assert reviewed == set()
    assert any(d['kind'] == 'reconciliation_failed' for d in json.loads(result.dispositions_json))
    windows = [e for e in calls.log.read() if e['stage'] == 'extraction_reconciliation_window']
    assert not windows
    assert result.obligations_json == result.resolutions_json == '[]'


def test_resolved_ledger_cannot_hide_remaining_reference(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    sent = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        sent.append(inputs)
        if len(sent) > 2:
            pytest.fail('complete coverage with a new gap was accepted')
        value = graph()
        value.update(coverage_complete=False, new_gaps=[{'description': 'Q'}])
        if inputs.get('mode') == 'reconcile_ranges':
            value['items'] = []
            value['coverage_complete'] = True
            known = inputs['ranges'][0]['items'][0]['id']
            value['resolutions'] = [dict(obligation_id=inputs['obligations'][0]['id'], evidence_ids=[known])]
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    result = calls.extract_paper(papers[0])
    assert len(result.items) == 8 and not json.loads(result.resolutions_json)
    assert any(d['kind'] == 'reconciliation_failed' for d in json.loads(result.dispositions_json))


def test_overlapping_closures_include_prior_formulas_and_source_evidence(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    data = json.loads(path.read_text()[len(HEADER):])
    by_id = {i['id'].rsplit(':',1)[-1]: i for i in data['papers'][0]['items']}
    data['papers'][0]['items'] = [by_id[key] for key in ('p','q','r','d','f','qual','i','j')]
    original = provider.estimate
    def estimate(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'select_t_roots' and sum(len(p['items']) for p in inputs['papers']) > 4:
            return TokenUsage(input_tokens=70001, output_tokens=maximum)
        return original(kind, prompt, schema, maximum)
    formalized = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'select_t_roots':
            roots = [i['root_id'] for p in inputs['papers'] for i in p['items'] if i['id'].endswith((':r',':f'))]
            value = dict(roots=roots, relevance='P', omissions=[dict(group_id=g['group_id'],reason='Q')
                for g in inputs['selection_groups'] if set(g['root_ids']) - set(roots)])
        else:
            if formalized:
                expected = {i['id'] for i in formalized[0]['commitments']}
                assert {i['id'] for i in inputs['existing_commitments']} == expected
                assert {i['id'] for i in inputs['supporting_evidence']} == expected
                from ara.types import Formula
                prior_formulas = {i['id']: Formula.from_dict(i['formula']) for i in formalized[0]['commitments']}
                assert {i['id']: Formula.from_dict(i['formula']) for i in inputs['existing_commitments']} == prior_formulas
            value = batch_response(inputs)
            formalized.append(value)
        return Response(response(value))
    monkeypatch.setattr(provider, 'estimate', estimate)
    monkeypatch.setattr(provider, 'complete', complete)
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), HEADER+json.dumps(data), 'P')
    assert len(formalized) == 2
    assert len(result.commitments) == len({c.id for c in result.commitments}) == 8
    assert sum(e['stage'] == 'commitments_frozen' for e in calls.log.read()) == 1
