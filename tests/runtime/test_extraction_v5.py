"""Relaxed structure, retained evidence and explicit dispositions; P/Q only."""
import copy
import json
from dataclasses import replace

import pytest
from jsonschema import Draft202012Validator

from ara.runtime.calls import Rejected, normalize_patch_ids
from ara.runtime.cache import canonical
from ara.runtime.extraction import (extract, resume_papers, extraction_acceptance_identity,
                                    V4_PROMPT_SHA256, V4_SCHEMA_SHA256)
from ara.runtime.logging import EventLog
from ara.runtime.providers import structured_schema
from rich_fixture import graph
from test_extraction import rig, offline, ROOT
from test_extraction_acceptance import sequence


def test_reconstructed_inference_is_disclosed_and_wire_accepts_it(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_require_inference=True)
    value = graph()
    for i in value['items']:
        if i['kind'] == 'inference': i['inference_origin'] = 'reconstructed'
    wire = copy.deepcopy(value)
    for i in wire['items']:
        if i['kind'] != 'inference':
            for key in ('premise_ids', 'conclusion_id', 'qualification_ids', 'inference_origin'): i.pop(key)
        if i['kind'] not in ('distinction', 'qualification'): i.pop('applies_to')
    Draft202012Validator(structured_schema(calls.response_schema('extract_paper', papers[0].inputs()))).validate(wire)
    sequence(monkeypatch, provider, [value])
    result = calls.extract_paper(papers[0])
    assert [i.inference_origin for i in result.items if i.kind == 'inference'] == ['reconstructed'] * 2


@pytest.mark.parametrize('reason', [None, '', ' ', 'P'])
def test_no_inference_requires_explicit_disposition(rig, monkeypatch, reason):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_require_inference=True, extraction_targeted_corrections=0)
    value = graph(); value['items'] = value['items'][:2]
    if reason is not None: value['no_inference_reason'] = reason
    sent = sequence(monkeypatch, provider, [value])
    if reason in ('', ' '):
        with pytest.raises(Rejected): calls.extract_paper(papers[0])
        assert len(sent) == 1
    else:
        result = calls.extract_paper(papers[0])
        assert len(result.items) == 2
        dispositions = json.loads(result.dispositions_json)
        assert any(d['kind'] == 'inference_coverage_unverified' for d in dispositions)
        if reason == 'P':
            assert dict(pages=[1, 2], kind='no_explicit_inferential_structure', reason='P') in dispositions


def test_inference_is_paper_level_across_ranges(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_require_inference=True)
    monkeypatch.setattr('ara.runtime.calls.extraction_range_plan', lambda *a: [((p,), 1) for p in papers[0].pages])
    first = graph(); first['items'] = first['items'][:1]
    second = graph(page=2)
    review = {**graph(), 'items': []}
    sent = sequence(monkeypatch, provider, [first, second, review])
    result = calls.extract_paper(papers[0])
    assert len(result.items) == 9 and len(sent) == 3


def test_zero_inference_multi_range_gets_paper_review(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_require_inference=True, extraction_targeted_corrections=3)
    monkeypatch.setattr('ara.runtime.calls.extraction_range_plan', lambda *a: [((p,), 1) for p in papers[0].pages])
    first = graph(); first['items'] = first['items'][:1]
    second = graph(page=2); second['items'] = second['items'][:1]
    review = {**graph(), 'items': []}
    final = {**review, 'no_inference_reason': 'P'}
    sent = sequence(monkeypatch, provider, [first, second, review, review, final])
    result = calls.extract_paper(papers[0])
    assert len(sent) == 3 and sent[-1]['mode'] == 'reconcile_ranges'
    assert len(result.items) == 2
    assert any(d['kind'] == 'inference_coverage_unverified' for d in json.loads(result.dispositions_json))


def test_reversed_pages_repaired_logged_and_out_of_bounds_refused(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    value = graph(); value['items'][0].update(page_start=2, page_end=1)
    sequence(monkeypatch, provider, [value])
    result = calls.extract_paper(papers[0])
    assert (result.items[0].page_start, result.items[0].page_end) == (1, 2)
    changes = [json.loads(e['payload_json'])['changes'] for e in calls.log.read() if e['stage']=='extraction_normalized']
    assert changes[0][0]['operation'] == 'order_page_range'
    value['items'][0]['page_start'] = 3
    calls.cache.path = calls.cache.path / 'fresh'
    calls.cache.path.mkdir()
    sequence(monkeypatch, provider, [value])
    with pytest.raises(Rejected, match='outside paper'): calls.extract_paper(papers[0])


def test_duplicate_patch_retains_items_and_references(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_targeted_corrections=3)
    bad = graph(); bad['items'][4]['kind'] = 'premise'; bad['items'][4]['applies_to'] = []
    patch = {**graph(), 'items': [copy.deepcopy(graph()['items'][4]) for _ in range(2)]}
    sequence(monkeypatch, provider, [bad, patch])
    result = calls.extract_paper(papers[0])
    assert len(result.items) == 9
    assert any(i.id.endswith(':d__duplicate_2') for i in result.items)
    assert next(i for i in result.items if i.id.endswith(':i')).qualification_ids == ('p:r1-2:d',)
    changes = [json.loads(e['payload_json'])['changes'] for e in calls.log.read() if e['stage']=='extraction_normalized']
    assert any(c['operation']=='rename_duplicate_id' for cs in changes for c in cs)


def test_ambiguous_duplicate_reference_is_not_guessed():
    patch = graph(); patch['items'].append(dict(patch['items'][0], text='Q'))
    with pytest.raises(Rejected, match='ambiguous duplicate'): normalize_patch_ids(patch, {'items': []})


def test_third_correction_preserves_inventory(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config.update(extraction_targeted_corrections=3)
    bad = graph(); bad['items'][0]['page_end'] = 3
    patch = {**graph(), 'items': [copy.deepcopy(graph()['items'][0])]}
    sent = sequence(monkeypatch, provider, [bad, bad, bad, patch])
    result = calls.extract_paper(papers[0])
    assert len(sent) == 4 and len(result.items) == 8
    assert [json.loads(e['payload_json'])['correction'] for e in calls.log.read() if e['stage']=='extraction_targeted_correction'] == [1, 2, 3]


@pytest.mark.parametrize('defect', [None, 'page', 'reference', 'identity'])
def test_v4_graph_revalidated_offline(rig, monkeypatch, tmp_path, defect):
    import ara.runtime.extraction as module
    calls, provider, papers, *_ = rig
    identity = extraction_acceptance_identity(calls.config, ROOT)
    previous = {**identity, 'version':'rich-paper-acceptance-v4', 'prompt_sha256':V4_PROMPT_SHA256, 'schema_sha256':V4_SCHEMA_SHA256}
    if defect == 'identity': previous['schema_sha256'] = 'P'
    monkeypatch.setattr(module, 'extraction_acceptance_identity', lambda *a: previous)
    value = graph(); sequence(monkeypatch, provider, [value])
    if defect in ('page', 'reference'):
        # A hash-consistent old graph still has to pass the new validation boundary.
        original = calls.extract_paper
        def corrupted(paper, **kwargs):
            result = original(paper)
            item = replace(result.items[0], page_end=99) if defect == 'page' else replace(result.items[-1], premise_ids=('unknown',))
            changed = replace(result, items=((item,) + result.items[1:] if defect=='page' else result.items[:-1]+(item,)))
            from ara.runtime.cache import digest
            calls.log.record('extraction_graph_merged', graph_hash=digest(canonical(changed.to_dict())))
            return changed
        monkeypatch.setattr(calls, 'extract_paper', corrupted)
    extract(calls, papers[:1])
    monkeypatch.setattr(module, 'extraction_acceptance_identity', lambda *a: identity)
    log = EventLog(tmp_path/'resume/events.jsonl')
    reused = resume_papers(log, papers[:1], [calls.log.path.parent], calls.config, ROOT)
    assert bool(reused) == (defect is None)
    if defect is None:
        assert reused['p']['outcome']['acceptance_identity'] == previous
        assert any(e['stage']=='extraction_acceptance_revalidated' for e in log.read())


@pytest.mark.parametrize('count', [2, 3])
def test_duplicate_repair_is_stable_after_failed_patch(count):
    from ara.runtime.calls import extraction_defaults
    value = {**graph(), 'items': [copy.deepcopy(graph()['items'][0]) for _ in range(count)]}
    first = copy.deepcopy(value)
    normalize_patch_ids(first, {'items': []})
    extraction_defaults(first)
    second = copy.deepcopy(value)
    normalize_patch_ids(second, first)
    assert first == second
    assert len({i['id'] for i in second['items']}) == count


def test_duplicate_repair_leaves_malformed_fields_for_schema():
    value = {**graph(), 'items': [dict(graph()['items'][0], premise_ids=None) for _ in range(2)]}
    normalize_patch_ids(value, {'items': []})
    assert value['items'][1]['id'] == 'p__duplicate_2'
    assert value['items'][0]['premise_ids'] is None
