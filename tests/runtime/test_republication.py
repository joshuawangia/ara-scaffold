"""Verified snapshot reuse and historical publication compatibility; P/Q only."""
import json
from dataclasses import replace

import pytest

from ara.runtime.cache import Cache, canonical, digest
from ara.runtime.calls import ModelCalls
from ara.runtime.extraction import HEADER, extract, literature_provenance, resume_papers
from ara.runtime.logging import EventLog
from rich_fixture import graph
from test_extraction import ROOT, accounting, offline, register, rig


@pytest.mark.parametrize('change', ['smaller', 'larger', 'conflicting', 'disjoint'])
def test_offline_snapshot_replacement_preserves_accepted_inventory(rig, tmp_path, change):
    calls, provider, papers, *_ = rig
    first, second = graph(), graph()
    if change == 'larger':
        first['items'] = first['items'][:1]
    elif change == 'smaller':
        second['items'] = second['items'][:1]
    elif change == 'conflicting':
        second['items'][0]['text'] = 'Q Q Q'
    else:
        second['items'] = [dict(second['items'][0], id='s')]
    register(calls, provider, papers[0], first)
    original = extract(calls, papers[:1])
    newer = ModelCalls(calls.config, provider, EventLog(tmp_path/'newer/events.jsonl'),
                       Cache(tmp_path/'newer/cache'), ROOT, '')
    register(newer, provider, papers[0], second)
    other = extract(newer, papers[:1])
    for path in (original, other):
        literature_provenance(path, path.read_text())
    destination = EventLog(tmp_path/'follow/events.jsonl')
    sources = [calls.log.path.parent, newer.log.path.parent]
    if change != 'larger':
        with pytest.raises(ValueError, match='non-monotonic completed paper replacement: p'):
            resume_papers(destination, papers[:1], sources, calls.config, ROOT, revalidate_only=True)
        assert destination.read() == []
        assert not (destination.path.parent/'literature.extracted.txt').exists()
    else:
        reused = resume_papers(destination, papers[:1], sources, calls.config, ROOT, revalidate_only=True)
        follow = ModelCalls(calls.config, provider, destination, Cache(tmp_path/'follow/cache'), ROOT, '')
        path = extract(follow, papers[:1], reused=reused, salvage_only=True)
        items = json.loads(path.read_text()[len(HEADER):])['papers'][0]['items']
        assert len(items) == 8
        assert json.loads(original.read_text()[len(HEADER):])['papers'][0]['items'][0] in items
        assert accounting(destination)['local_totals']['model_calls'] == 0
        literature_provenance(path, path.read_text())


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
