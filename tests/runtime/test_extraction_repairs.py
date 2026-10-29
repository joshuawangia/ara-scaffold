"""Content-free candidate repair and actionable structural feedback."""
import copy
import json

import pytest

from ara.runtime.calls import Rejected
from rich_fixture import graph
from test_extraction import rig, offline
from test_extraction_acceptance import sequence


def payloads(calls, stage):
    return [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == stage]


def test_initial_duplicate_ids_preserve_content_and_require_explicit_reference(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 3
    bad = graph()
    bad['items'].append(dict(bad['items'][0], text='Q'))
    bad['items'].append(dict(bad['items'][0], id='p__duplicate_2', text='R'))
    link = copy.deepcopy(next(i for i in bad['items'] if i['id'] == 'i'))
    link['premise_ids'] = ['p__duplicate_3']
    sent = sequence(monkeypatch, provider, [bad, {**graph(), 'items': [link]}])
    result = calls.extract_paper(papers[0])
    assert len(result.items) == len(bad['items'])
    candidate = sent[1]['candidate']
    assert candidate['items'][-2]['id'] == 'p__duplicate_3'
    for old, new in zip(bad['items'], candidate['items']):
        assert {k:v for k,v in old.items() if k != 'id'} == {k:v for k,v in new.items() if k != 'id'}
    assert sent[1]['required_reference_updates'] == ['i']
    assert sent[1]['duplicate_id_repairs'][0]['after'] == 'p__duplicate_3'
    changes = payloads(calls, 'extraction_normalized')
    assert any(c['operation'] == 'rename_duplicate_id' for p in changes for c in p['changes'])
    raw = next(e['response'] for e in calls.log.read() if e['stage'] == 'extract_paper' and e['label'] == 'MODEL')
    assert json.loads(json.loads(raw)['content'][0]['text']) == bad
    assert next(i for i in result.items if i.id.endswith(':i')).premise_ids == ('p:r1-2:p__duplicate_3',)


def test_renamed_ambiguous_references_cannot_pass_with_empty_patch(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 1
    bad = graph(); bad['items'].append(dict(bad['items'][0], text='Q'))
    sent = sequence(monkeypatch, provider, [bad, {**graph(), 'items': []}])
    with pytest.raises(Rejected, match='duplicate references require explicit correction'):
        calls.extract_paper(papers[0])
    assert len(sent) == 2
    assert len(sent[1]['candidate']['items']) == len(bad['items'])


@pytest.mark.parametrize('field,item_id', [('premise_ids','i'), ('conclusion_id','i'),
                                          ('qualification_ids','i'), ('applies_to','d')])
def test_unknown_endpoint_feedback_names_link_field_and_inventory(rig, monkeypatch, field, item_id):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 1
    bad = graph(); item = next(i for i in bad['items'] if i['id'] == item_id)
    item[field] = 'missing' if field == 'conclusion_id' else ['missing']
    sent = sequence(monkeypatch, provider, [bad, graph()])
    calls.extract_paper(papers[0])
    error = sent[1]['validation_error']
    assert 'unknown endpoint' in error
    details = json.loads(error.split(': ', 1)[1])
    assert details['link_id'] == item_id and details['field'] == field
    assert details['missing_ids'] == ['missing']
    assert details['valid_item_ids'] == sorted(i['id'] for i in bad['items'])


def test_relation_feedback_includes_allowed_kind_table(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 1
    bad = graph(); bad['items'][0]['applies_to'] = ['q']
    sent = sequence(monkeypatch, provider, [bad, graph()])
    calls.extract_paper(papers[0])
    rules = sent[1]['allowed_relations_by_kind']
    assert rules['premise'] == []
    assert rules['qualification'] == rules['distinction'] == ['applies_to']
    assert rules['inference'] == ['premise_ids', 'conclusion_id', 'qualification_ids']
    assert 'allowed_relations_by_kind' in sent[1]['validation_error']


def test_relation_feedback_lists_all_offending_items(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 1
    bad = graph()
    for item in bad['items']:
        if item['kind'] not in ('distinction', 'qualification'):
            item['applies_to'] = ['q']
    sent = sequence(monkeypatch, provider, [bad, graph()])
    calls.extract_paper(papers[0])
    violations = sent[1]['relation_violations']
    assert {v['item_id'] for v in violations} == {'p','q','r','f','i','j'}
    assert all(v['field']=='applies_to' and v['actual_ids']==['q'] for v in violations)
    assert all('applies_to' not in v['allowed_fields'] for v in violations)


@pytest.mark.parametrize('limit', [None, 0, 2, 3])
def test_codex_defaults_to_three_corrections_and_respects_override(rig, monkeypatch, limit):
    calls, provider, papers, *_ = rig
    calls.config['provider'] = 'codex_cli'
    calls.config.pop('extraction_targeted_corrections', None)
    if limit is not None: calls.config['extraction_targeted_corrections'] = limit
    bad = graph(); bad['items'][0]['page_end'] = 3
    sent = sequence(monkeypatch, provider, [bad, bad, bad, graph()])
    if limit in (0, 2):
        with pytest.raises(Rejected): calls.extract_paper(papers[0])
        assert len(sent) == limit + 1
    else:
        assert len(calls.extract_paper(papers[0]).items) == len(graph()['items'])
        assert len(sent) == 4
        assert [p['correction'] for p in payloads(calls, 'extraction_targeted_correction')] == [1, 2, 3]
