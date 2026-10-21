"""Continuation obligation inventory proofs using placeholder responses."""
import json

import pytest

from ara.runtime.calls import Rejected
from ara.runtime.extraction import extract
from ara.runtime.providers import Response
from rich_fixture import graph
from test_extraction import rig, offline, response


@pytest.mark.parametrize('description', ['R', 'Q'])
@pytest.mark.parametrize('discover_turn', [2, 3])
@pytest.mark.parametrize('resolve_new', [False, True])
def test_new_gap_survives_original_resolution(rig, monkeypatch, resolve_new, discover_turn, description):
    calls, provider, papers, *_ = rig
    seen = []

    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        seen.append(inputs)
        value = graph()
        if len(seen) == 1:
            value.update(coverage_complete=False, new_gaps=[{'description': 'Q'}])
        else:
            value['items'] = []
            obligation = inputs['obligations'][0]
            if len(seen) == 2:
                value.update(coverage_complete=False, new_gaps=[],
                             pending_obligation_ids=[obligation['id']],
                             context_request={'pages': [1], 'evidence_ids': []})
            elif len(seen) == 3 or resolve_new:
                value['resolutions'] = [dict(obligation_id=obligation['id'],
                    evidence_ids=[inputs['ranges'][0]['items'][0]['id']])]
            else:
                value.update(coverage_complete=False, new_gaps=[],
                             pending_obligation_ids=[obligation['id']])
        if len(seen) == discover_turn:
            value.update(coverage_complete=False, new_gaps=[{'description': description}])
        return Response(response(value))

    monkeypatch.setattr(provider, 'complete', complete)
    if resolve_new:
        result = calls.extract_paper(papers[0]).to_dict()
        assert len(result['obligations']) == len(result['resolutions']) == 2
    else:
        with pytest.raises(Rejected, match='unresolved obligation inventory'):
            extract(calls, papers[:1])
        assert not (calls.log.path.parent / 'literature.extracted.txt').exists()
    assert len(seen) == 4
    events = calls.log.read()
    discoveries = [json.loads(e['payload_json'])['obligation'] for e in events
                   if e['stage'] == 'extraction_obligation_discovered']
    assert [o['description'] for o in discoveries] == ['Q', description]
    assert discoveries[0]['id'] == 'p:r1-2:turn:1:gap:0'
    window = 'joined' if discover_turn == 2 else 'joined2'
    assert discoveries[1]['id'] == f'p:{window}:turn:{discover_turn - 1}:gap:0'
    assert discoveries[1]['source_id'] == 'p'
    assert discoveries[1]['range'] == window
    assert discoveries[1]['turn'] == discover_turn - 1
    assert discoveries[1]['pages'] == ([1, 2] if discover_turn == 2 else [1])
    assert seen[3]['obligations'] == [discoveries[1]]
    resolutions = [r for e in events if e['stage'] == 'extraction_obligation_resolved'
                   for r in json.loads(e['payload_json'])['resolutions']]
    assert {r['obligation_id'] for r in resolutions} == {o['id'] for o in discoveries[:2 if resolve_new else 1]}
    models = [e for e in events if e['label'] == 'MODEL']
    assert len(models) == 4
    for event in models:
        assert event['usage']['input_tokens'] == 100 and event['usage']['output_tokens'] == 50
        assert event['cost_usd'] == .00175
        assert json.loads(event['payload_json'])['status'] == 'accepted'
        assert event['response']
        assert any(e['stage'] == 'context_admission' and
                   json.loads(e['payload_json'])['prompt'] == event['prompt']
                   for e in events[:events.index(event)])
    snapshots = [json.loads(path.read_text()) for path in calls.log.path.parent.glob('p.*.rich.json')]
    assert len(snapshots) == 4
    assert {o['id'] for snapshot in snapshots for o in snapshot['obligations']} == {o['id'] for o in discoveries}
    if resolve_new:
        assert result['obligations'] == discoveries
        assert result['resolutions'] == resolutions
        assert all(r['evidence_ids'] for r in result['resolutions'])
    else:
        assert not any(e['stage'] == 'extraction_graph_merged' for e in events)


def test_review_and_descendant_gaps_drain_queue(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_planned_output_tokens_per_page=calls.config['extract_paper_max_output_tokens'])
    seen = []

    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        seen.append(inputs)
        value = graph()
        if inputs.get('mode') != 'reconcile_ranges':
            value = graph(page=inputs['pages'][0]['page'])
        else:
            value['items'] = []
            if inputs['obligations']:
                value['resolutions'] = [dict(obligation_id=inputs['obligations'][0]['id'],
                    evidence_ids=[inputs['ranges'][0]['items'][0]['id']])]
            if len(seen) < 6:
                value.update(coverage_complete=False, new_gaps=[{'description': 'Q'}])
        return Response(response(value))

    monkeypatch.setattr(provider, 'complete', complete)
    result = calls.extract_paper(papers[0]).to_dict()
    assert len(seen) == 6
    assert not seen[2]['obligations']
    assert len(result['obligations']) == len(result['resolutions']) == 3
    assert len({o['id'] for o in result['obligations']}) == 3
    assert {o['description'] for o in result['obligations']} == {'Q'}
    assert {o['id'] for o in result['obligations']} == {r['obligation_id'] for r in result['resolutions']}
