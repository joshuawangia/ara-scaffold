"""Deletion-only terminal repair, bounded by the original edge inventory."""
import copy
import json

import pytest

from ara.runtime.calls import Rejected
from ara.runtime.extraction import extract
from ara.runtime.export import methodology
from ara.runtime.salvage import accepted_ranges
from ara.runtime.logging import EventLog
from rich_fixture import graph
from test_extraction import rig, offline, ROOT
from test_extraction_acceptance import sequence
from test_extraction_repairs import payloads


def damaged(count=3):
    value = graph()
    # Nine valid edges plus three invalid edges: exactly 25% removed.
    for item in value['items'][:count]:
        item['applies_to'] = ['q']
    return value


def test_terminal_pruning_preserves_content_and_logs_original_values(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 3
    value = damaged()
    original = copy.deepcopy(value)
    sent = sequence(monkeypatch, provider, [value])
    result = calls.extract_paper(papers[0])
    assert len(sent) == 4
    assert len(result.items) == len(value['items'])
    for before, after in zip(value['items'], result.items):
        for key in ('text', 'kind', 'source_id', 'attribution', 'attributed_to', 'page_start', 'page_end', 'inference_origin'):
            assert getattr(after, key) == before[key]
    assert value == original
    assert all(not i.applies_to for i in result.items[:3])
    removals = payloads(calls, 'invalid_relation_dropped')
    assert [(p['item_id'], p['field'], p['original_value']) for p in removals] == [
        (id, 'applies_to', 'q') for id in ('p', 'q', 'r')]
    receipt = payloads(calls, 'extraction_structure_repaired')[0]
    assert receipt['removed'] == 3 and receipt['total'] == 12 and receipt['share'] == .25
    assert receipt['status'] == 'accepted'
    assert len([e for e in calls.log.read() if e['label']=='MODEL']) == 4
    assert all(json.loads(e['payload_json'])['status']=='rejected' for e in calls.log.read() if e['label']=='MODEL')
    report = json.loads(methodology(calls.log.path).split('```json\n')[1].split('\n```')[0])
    assert report['extraction']['structural_repairs_by_paper']['p']['removed'] == 3
    assert report['extraction']['structural_repairs_by_paper']['p']['total'] == 12


def test_pruning_over_quarter_fails_and_logs_disposition(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 1
    sequence(monkeypatch, provider, [damaged(4)])
    with pytest.raises(Rejected, match='repair share exceeds 25%'):
        calls.extract_paper(papers[0])
    receipt = payloads(calls, 'extraction_structure_repaired')[0]
    assert receipt['removed'] == 4 and receipt['total'] == 13
    assert receipt['status'] == 'rejected'


@pytest.mark.parametrize('field,ref,event', [
    ('premise_ids', 'missing', 'dangling_link_dropped'),
    ('qualification_ids', 'q', 'invalid_relation_dropped'),
    ('premise_ids', 'j', 'invalid_relation_dropped')])
def test_pruning_drops_only_bad_endpoint(rig, monkeypatch, field, ref, event):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 0
    value = graph(); value['items'][6][field].append(ref)
    sequence(monkeypatch, provider, [value])
    result = calls.extract_paper(papers[0])
    assert getattr(result.items[6], field) == tuple('p:r1-2:'+v for v in graph()['items'][6][field])
    assert payloads(calls, event)[0]['original_value'] == ref


@pytest.mark.parametrize('defect', ['conclusion', 'premises', 'page', 'text', 'no_inference', 'obligation'])
def test_pruning_cannot_bypass_other_acceptance_checks(rig, monkeypatch, defect):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 0
    value = damaged(1)
    if defect == 'conclusion': value['items'][6]['conclusion_id'] = 'missing'
    if defect == 'premises': value['items'][6]['premise_ids'] = ['missing']
    if defect == 'page': value['items'][0]['page_end'] = 99
    if defect == 'text': value['items'][0]['text'] = ' '
    if defect == 'no_inference':
        value['items'] = value['items'][:6]
        value['items'][4]['applies_to'] = ['p', 'q', 'r']
    if defect == 'obligation': value['coverage_complete'] = False
    sequence(monkeypatch, provider, [value])
    with pytest.raises(Rejected): calls.extract_paper(papers[0])
    assert not any(p['status']=='accepted' for p in payloads(calls, 'extraction_structure_repaired'))


def test_valid_correction_never_triggers_pruning(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 3
    sequence(monkeypatch, provider, [damaged(), graph()])
    calls.extract_paper(papers[0])
    assert payloads(calls, 'extraction_structure_repaired') == []


def test_terminal_pruning_replays_offline(rig, monkeypatch, tmp_path):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 1
    sequence(monkeypatch, provider, [damaged()])
    extract(calls, papers[:1])
    entries = accepted_ranges(calls.log.read(), papers[:1], calls.config, ROOT,
                              EventLog(tmp_path/'salvaged/events.jsonl'))
    assert len(entries['p']) == 1
    assert len(entries['p'][0]['result'].items) == 8
    assert all(not i.applies_to for i in entries['p'][0]['result'].items[:3])


def test_pruning_uses_final_cumulative_patch(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 1
    bad = damaged(1)
    patch = {**graph(), 'items': [dict(graph()['items'][1], text='Q Q Q Q', applies_to=['r'])]}
    sequence(monkeypatch, provider, [bad, patch])
    result = calls.extract_paper(papers[0])
    assert len(result.items) == 8 and result.items[1].text == 'Q Q Q Q'
    assert payloads(calls, 'extraction_structure_repaired')[0]['removed'] == 2


def test_pruning_preserves_existing_endpoints_and_is_deletion_only():
    from ara.runtime.calls import prune_extraction_relations
    from ara.runtime.extraction import ExtractedItem
    value = graph()
    value['items'][6]['premise_ids'].extend(['existing', 'missing'])
    original = copy.deepcopy(value)
    existing = (ExtractedItem(**dict(graph()['items'][0], id='existing')),)
    repaired, removals, total = prune_extraction_relations(value, existing)
    assert total == 11 and len(removals) == 1
    assert repaired['items'][6]['premise_ids'] == ['p', 'q', 'existing']
    expected = copy.deepcopy(value); expected['items'][6]['premise_ids'].remove('missing')
    assert repaired == expected and value == original


@pytest.mark.parametrize('tamper', ['text', 'count', 'candidate', 'policy'])
def test_pruned_receipts_cannot_change_content_or_counts_on_replay(rig, monkeypatch, tmp_path, tamper):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 1
    sequence(monkeypatch, provider, [damaged()])
    extract(calls, papers[:1])
    events = calls.log.read()
    event = next(e for e in events if e['stage']=='extraction_structure_repaired')
    data = json.loads(event['payload_json'])
    if tamper == 'text': data['repaired']['items'][0]['text'] = 'Q'
    if tamper == 'count': data['removed'] = 0
    if tamper == 'candidate': data['candidate']['items'][0]['text'] = 'Q'
    if tamper == 'policy': data['policy'] = 'P'
    event['payload_json'] = json.dumps(data)
    with pytest.raises(Rejected):
        accepted_ranges(events, papers[:1], calls.config, ROOT, EventLog(tmp_path/'salvage/events.jsonl'))
