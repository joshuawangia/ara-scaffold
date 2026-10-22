"""Verified snapshot reuse and historical publication compatibility; P/Q only."""
import json
from dataclasses import replace

import pytest

from ara.runtime.cache import Cache, canonical, digest
from ara.runtime.calls import ModelCalls
from ara.runtime.construction import prerequisite_closure
from ara.runtime.extraction import HEADER, extract, literature_provenance, resume_papers
from ara.runtime.grounding import evidence_items
from ara.runtime.logging import EventLog
from ara.runtime.snapshot_union import snapshot_id
from rich_fixture import graph
from test_extraction import ROOT, accounting, offline, register, rig


def assert_snapshot_retention(paper, originals):
    by_hash = {digest(canonical(i)): i for original in originals for i in original}
    provenance = paper['item_provenance']
    items = {i['id']: i for i in paper['items']}
    assert set(provenance) == set(items)
    observed = {(p['original_id'], p['item_sha256']) for origins in provenance.values() for p in origins}
    assert observed == {(i['id'], digest(canonical(i))) for original in originals for i in original}
    maps = {}
    for id, origins in provenance.items():
        for p in origins:
            mapping = maps.setdefault(p['snapshot_id'], {})
            assert mapping.setdefault(p['original_id'], id) == id
    for id, origins in provenance.items():
        for p in origins:
            original = by_hash[p['item_sha256']]
            mapping = maps[p['snapshot_id']]
            assert p['original_citation'] == original['citation']
            expected = {**original, 'id': id, 'citation': items[id]['citation']}
            for field in ('premise_ids', 'qualification_ids', 'applies_to'):
                expected[field] = [mapping[x] for x in original[field]]
            expected['conclusion_id'] = mapping[original['conclusion_id']] if original['conclusion_id'] else None
            assert items[id] == expected


@pytest.mark.parametrize('change', ['smaller', 'larger', 'conflicting', 'qualifier', 'new_qualifier', 'disjoint'])
def test_offline_snapshot_replacement_preserves_accepted_inventory(rig, tmp_path, monkeypatch, change):
    calls, provider, papers, *_ = rig
    first, second = graph(), graph()
    if change == 'larger':
        first['items'] = first['items'][:1]
    elif change == 'smaller':
        second['items'] = second['items'][:1]
    elif change == 'conflicting':
        second['items'][0]['text'] = 'placeholder'
    elif change == 'qualifier':
        for value in (first, second):
            value['items'][4]['applies_to'] = ['i']
            value['items'][6]['qualification_ids'] = []
        second['items'][4]['text'] = 'placeholder'
    elif change == 'new_qualifier':
        second['items'].append(dict(second['items'][4], id='new', text='placeholder', applies_to=['i']))
    else:
        second['items'] = [dict(second['items'][0], id='s')]
    register(calls, provider, papers[0], first)
    original = extract(calls, papers[:1])
    newer = ModelCalls(calls.config, provider, EventLog(tmp_path/'newer/events.jsonl'),
                       Cache(tmp_path/'newer/cache'), ROOT, '')
    register(newer, provider, papers[0], second)
    other = extract(newer, papers[:1])
    originals = [json.loads(path.read_text()[len(HEADER):])['papers'][0]['items'] for path in (original, other)]
    for path in (original, other):
        literature_provenance(path, path.read_text())
    def forbidden(*args, **kwargs):
        raise AssertionError('completed snapshots must not dispatch')
    monkeypatch.setattr(provider, 'complete', forbidden)
    previous = None
    for n, sources in enumerate(([calls.log.path.parent, newer.log.path.parent],
                                  [newer.log.path.parent, calls.log.path.parent])):
        destination = EventLog(tmp_path/f'follow{n}/events.jsonl')
        reused = resume_papers(destination, papers[:1], sources, calls.config, ROOT, revalidate_only=True)
        follow = ModelCalls(calls.config, provider, destination, Cache(tmp_path/f'follow{n}/cache'), ROOT, '')
        path = extract(follow, papers[:1], reused=reused, salvage_only=True)
        paper = json.loads(path.read_text()[len(HEADER):])['papers'][0]
        assert_snapshot_retention(paper, originals)
        assert len(paper['items']) == {'smaller': 8, 'larger': 8, 'conflicting': 15, 'qualifier': 14, 'new_qualifier': 15, 'disjoint': 9}[change]
        if change in ('conflicting', 'qualifier', 'new_qualifier'):
            assert len(paper['quarantined']) == 2  # only this snapshot's premise and dependent inference
        projection = {k: paper[k] for k in ('items', 'item_provenance', 'open_gaps', 'quarantined')}
        if previous is not None:
            assert projection == previous
        previous = projection
        assert accounting(destination)['local_totals']['model_calls'] == 0
        literature_provenance(path, path.read_text())
    destination = EventLog(tmp_path/'again/events.jsonl')
    reused = resume_papers(destination, papers[:1], [path.parent], calls.config, ROOT)
    follow = ModelCalls(calls.config, provider, destination, Cache(tmp_path/'again/cache'), ROOT, '')
    path = extract(follow, papers[:1], reused=reused)
    paper = json.loads(path.read_text()[len(HEADER):])['papers'][0]
    assert {k: paper[k] for k in previous} == previous
    assert_snapshot_retention(paper, originals)
    literature_provenance(path, path.read_text())


@pytest.mark.parametrize('target', ['i', 'p', 'r', 'f', 'inference_conclusion'])
def test_native_closure_retains_snapshot_context(rig, tmp_path, monkeypatch, target):
    calls, provider, papers, *_ = rig
    first, second = graph(), graph()
    if target == 'inference_conclusion':
        first['items'] = [i for i in first['items'] if i['id'] != 'j']
    else:
        second['items'].append(dict(second['items'][4], id='new', text='P Q', applies_to=[target]))
    originals, paths = [], []
    for n, value in enumerate((first, second)):
        current = ModelCalls(calls.config, provider, EventLog(tmp_path/f'original{n}/events.jsonl'),
                             Cache(tmp_path/f'original{n}/cache'), ROOT, '')
        register(current, provider, papers[0], value)
        paths.append(extract(current, papers[:1]))
        originals.append(json.loads((paths[-1].parent/'p.extraction.json').read_text()))
        literature_provenance(paths[-1], paths[-1].read_text())

    def forbidden(*args, **kwargs):
        raise AssertionError('completed snapshots must not dispatch')
    monkeypatch.setattr(provider, 'complete', forbidden)
    previous = None
    for n in range(3):
        sources = [p.parent for p in (paths if n == 0 else reversed(paths))] if n < 2 else [path.parent]
        log = EventLog(tmp_path/f'union{n}/events.jsonl')
        reuse = resume_papers(log, papers[:1], sources, calls.config, ROOT)
        follow = ModelCalls(calls.config, provider, log, Cache(tmp_path/f'union{n}/cache'), ROOT, '')
        path = extract(follow, papers[:1], reused=reuse, salvage_only=True)
        literature_provenance(path, path.read_text())
        union = json.loads(path.read_text()[len(HEADER):])['papers'][0]
        assert_snapshot_retention(union, [o['items'] for o in originals])
        items = {i['id']: i for i in evidence_items(union)}
        for original in originals:
            sid = snapshot_id(original)
            mapping = {origin['original_id']: published
                       for published, origins in union['item_provenance'].items()
                       for origin in origins if origin['snapshot_id'] == sid}
            old_items = {i['id']: i for i in evidence_items(original)}
            assert len(old_items) == len(original['items'])  # exercise eligible constraints
            for root in old_items:
                expected = {mapping[id] for id in prerequisite_closure(old_items, [root])}
                assert prerequisite_closure(items, [mapping[root]]) == expected
        projection = {k: union[k] for k in ('items', 'item_provenance', 'open_gaps', 'quarantined')}
        if previous is not None:
            assert projection == previous
        previous = projection
        assert accounting(log)['local_totals']['model_calls'] == 0


@pytest.mark.parametrize('grounded_history', [False, True])
def test_legacy_republication_reopens_gaps_and_resumes_again(rig, monkeypatch, tmp_path, grounded_history):
    import ara.runtime.extraction as module
    import ara.runtime.grounding as grounding
    calls, provider, papers, *_ = rig
    identity = module.extraction_acceptance_identity(calls.config, ROOT)
    previous = {**identity, 'version': 'rich-paper-acceptance-v4',
                'prompt_sha256': module.V4_PROMPT_SHA256, 'schema_sha256': module.V4_SCHEMA_SHA256}
    value = graph(); value['items'][0]['text'] = 'placeholder'
    register(calls, provider, papers[0], value)
    original_extract, original_ground = calls.extract_paper, grounding.ground_outcome
    obligations = [dict(id='g', description='P'), dict(id='h', description='Q')]
    dispositions = [dict(kind='no_explicit_inferential_structure', reason='P', pages=[1, 2])]

    def legacy_graph(paper, **kwargs):
        result = original_extract(paper, **kwargs)
        result = replace(result, obligations_json=canonical(obligations),
                         resolutions_json=canonical([dict(obligation_id='g', evidence_ids=[result.items[0].id]),
                                                     dict(obligation_id='h', evidence_ids=[result.items[1].id])]),
                         dispositions_json=canonical(dispositions))
        calls.log.record('extraction_graph_merged', graph_hash=digest(canonical(result.to_dict())))
        return result

    def legacy_outcome(paper, outcome, log):
        if grounded_history:
            outcome = original_ground(paper, outcome, log)
        return {k: v for k, v in outcome.items() if k not in ('range_union_policy', 'publication_policy')}

    with monkeypatch.context() as old:
        old.setattr(module, 'extraction_acceptance_identity', lambda *a: previous)
        old.setattr(calls, 'extract_paper', legacy_graph)
        old.setattr(grounding, 'ground_outcome', legacy_outcome)
        original = extract(calls, papers[:1])
    original_text = original.read_text()
    original_paper = json.loads(original_text[len(HEADER):])['papers'][0]
    assert 'open_gaps' not in original_paper
    assert 'paper-stated links' in original_text
    literature_provenance(original, original_text)

    def forbidden(*a, **kw):
        raise AssertionError('offline reuse dispatched')
    monkeypatch.setattr(provider, 'complete', forbidden)
    for n in range(2):
        destination = EventLog(tmp_path/f'resume{n}/events.jsonl')
        reused = resume_papers(destination, papers[:1], [calls.log.path.parent], calls.config, ROOT)
        calls = ModelCalls(calls.config, provider, destination, Cache(tmp_path/f'cache{n}'), ROOT, '')
        path = extract(calls, papers[:1], reused=reused, salvage_only=True)
        data = json.loads(path.read_text()[len(HEADER):])
        paper = data['papers'][0]
        assert paper['open_gaps'] == obligations[:1]
        assert paper['dispositions'] == dispositions
        assert paper['items'] == original_paper['items']
        assert len(paper['quarantined']) == 2
        assert 'paper-stated or reconstructed links' in data['use']
        saved = json.loads((path.parent/'p.extraction.json').read_text())
        assert saved['acceptance_identity'] == previous
        summary = accounting(destination)
        assert summary['extraction']['limitations'] == [dict(source_id='p', open_gaps=obligations[:1], dispositions=dispositions)]
        assert summary['local_totals']['model_calls'] == 0
        literature_provenance(path, path.read_text())
        assert original.read_text() == original_text
        literature_provenance(original, original_text)


def test_union_keeps_gap_resolution_with_its_snapshot(rig, monkeypatch, tmp_path):
    calls, provider, papers, *_ = rig
    originals = []
    for n, text in enumerate(('P P P', 'placeholder')):
        current = ModelCalls(calls.config, provider, EventLog(tmp_path/f'gap{n}/events.jsonl'),
                             Cache(tmp_path/f'gap{n}/cache'), ROOT, '')
        value = graph(); value['items'] = [dict(value['items'][0], text=text)]
        register(current, provider, papers[0], value)
        original_extract = current.extract_paper
        def with_gap(paper, **kwargs):
            result = original_extract(paper, **kwargs)
            result = replace(result, obligations_json=canonical([dict(id='g', description='Q')]),
                             resolutions_json=canonical([dict(obligation_id='g', evidence_ids=[result.items[0].id])]))
            current.log.record('extraction_graph_merged', graph_hash=digest(canonical(result.to_dict())))
            return result
        monkeypatch.setattr(current, 'extract_paper', with_gap)
        originals.append(extract(current, papers[:1]))
    destination = EventLog(tmp_path/'gap-union/events.jsonl')
    reused = resume_papers(destination, papers[:1], [p.parent for p in originals], calls.config, ROOT)
    follow = ModelCalls(calls.config, provider, destination, Cache(tmp_path/'gap-union/cache'), ROOT, '')
    path = extract(follow, papers[:1], reused=reused, salvage_only=True)
    paper = json.loads(path.read_text()[len(HEADER):])['papers'][0]
    assert len(paper['items']) == 2 and len(paper['quarantined']) == 1
    assert len(paper['open_gaps']) == 1 and paper['open_gaps'][0]['original_id'] == 'g'
    blocked = paper['quarantined'][0]['item_id']
    assert paper['open_gaps'][0]['snapshot_id'] == paper['item_provenance'][blocked][0]['snapshot_id']
    assert accounting(destination)['extraction']['limitations'][0]['open_gaps'] == paper['open_gaps']

    # A self-consistent log receipt cannot turn a modified derived union into a source.
    bad = json.loads((path.parent/'p.extraction.json').read_text())
    bad['items'][0]['text'] = 'Q Q Q'
    from ara.runtime.snapshot_union import graph as snapshot_graph
    destination.record('extraction_graph_merged', graph_hash=digest(canonical(snapshot_graph(bad))))
    destination.record('extraction_outcome', **bad)
    rejected = EventLog(tmp_path/'bad-union/events.jsonl')
    with pytest.raises(ValueError, match='differs from original snapshot receipts'):
        resume_papers(rejected, papers[:1], [path.parent], calls.config, ROOT)
    assert rejected.read() == []
