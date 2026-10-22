"""Range union acceptance and disclosed limitations, using placeholder evidence."""
import json
from dataclasses import replace

import pytest

from ara.runtime.extraction import HEADER, PageText, extract
from test_extraction import accounting
from rich_fixture import graph
from test_extraction import rig, offline
from test_extraction_acceptance import sequence


def test_failed_review_preserves_ranges_and_discloses_gap(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 3
    monkeypatch.setattr('ara.runtime.calls.extraction_range_plan', lambda *a: [((p,), 1) for p in papers[0].pages])
    first = graph(); first.update(coverage_complete=False, new_gaps=[{'description': 'Q'}])
    bad = graph(); bad['source_id'] = 'q'
    sent = sequence(monkeypatch, provider, [first, graph(page=2), bad])
    path = extract(calls, papers[:1])
    paper = json.loads(path.read_text()[len(HEADER):])['papers'][0]
    assert len(sent) == 3 and len(paper['items']) == 16
    assert len(paper['open_gaps']) == 1
    assert any(d['kind'] == 'reconciliation_failed' for d in paper['dispositions'])
    assert accounting(calls.log)['extraction']['limitations'][0]['open_gaps'] == paper['open_gaps']


def test_thin_range_retried_once_without_dropping_original(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    paper = replace(papers[0], pages=tuple(PageText(n, 'P') for n in range(1, 21)))
    first = graph(); first['items'] = first['items'][:1]
    second = graph(page=11); second['items'] = second['items'][:1]
    sent = sequence(monkeypatch, provider, [first, first, second, {**graph(), 'items': []}])
    result = calls.extract_paper(paper)
    assert len(sent) == 4 and [len(s['pages']) for s in sent[:3]] == [20, 10, 10]
    assert len(result.items) == 3
    assert any(d['kind'] == 'thin_range' for d in json.loads(result.dispositions_json))


def test_offline_salvage_keeps_failed_paper_ranges_and_provenance(rig, monkeypatch, tmp_path):
    from ara.runtime.calls import ModelCalls, Rejected
    from ara.runtime.cache import Cache
    from ara.runtime.extraction import resume_papers, literature_provenance
    from ara.runtime.logging import EventLog
    from test_extraction import ROOT
    calls, provider, papers, *_ = rig
    monkeypatch.setattr('ara.runtime.calls.extraction_range_plan', lambda *a: [((p,), 1) for p in papers[0].pages])
    bad = graph(page=2); bad['source_id'] = 'q'
    sequence(monkeypatch, provider, [graph(), bad])
    calls.config['extraction_targeted_corrections'] = 0
    # First range survives a subsequent range failure as partial evidence.
    first = extract(calls, papers[:1])
    assert len(json.loads(first.read_text()[len(HEADER):])['papers'][0]['items']) == 8
    log = EventLog(tmp_path/'follow/events.jsonl')
    reused = resume_papers(log, papers[:1], [calls.log.path.parent], calls.config, ROOT)
    def forbidden(*args, **kwargs): raise AssertionError('offline salvage dispatched')
    monkeypatch.setattr(provider, 'complete', forbidden)
    follow = ModelCalls(calls.config, provider, log, Cache(tmp_path/'follow/cache'), ROOT, '')
    path = extract(follow, papers[:1], reused=reused, salvage_only=True)
    value = json.loads(path.read_text()[len(HEADER):])['papers'][0]
    assert len(value['items']) == 8
    assert value['status'] == 'partial'
    assert next(d for d in value['dispositions'] if d['kind'] == 'unextracted_pages')['pages'] == [2]
    literature_provenance(path, path.read_text())


def test_native_exclusion_roster_is_disclosed(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    sequence(monkeypatch, provider, [graph()])
    path = extract(calls, papers[:1], excluded={'p': 'P'})
    value = json.loads(path.read_text()[len(HEADER):])
    assert value['publication_roster'] == [dict(source_id='p', status='excluded', reason='P')]
    assert value['papers'][0]['items'] == []
    assert accounting(calls.log)['extraction']['publication_roster'] == value['publication_roster']


def test_salvage_source_mismatch_refuses_without_dispatch(rig, monkeypatch, tmp_path):
    from ara.runtime.extraction import resume_papers
    from ara.runtime.logging import EventLog
    from test_extraction import ROOT
    calls, provider, papers, *_ = rig
    monkeypatch.setattr('ara.runtime.calls.extraction_range_plan', lambda *a: [((p,), 1) for p in papers[0].pages])
    bad = graph(page=2); bad['source_id'] = 'q'
    sequence(monkeypatch, provider, [graph(), bad])
    calls.config['extraction_targeted_corrections'] = 0
    extract(calls, papers[:1])
    changed = replace(papers[0], pages=(PageText(1, 'Q'), papers[0].pages[1]))
    with pytest.raises(ValueError, match='source page text mismatch'):
        resume_papers(EventLog(tmp_path/'follow/events.jsonl'), (changed,), [calls.log.path.parent], calls.config, ROOT)


def test_salvage_preserves_review_additions_and_resolutions(rig, monkeypatch, tmp_path):
    from ara.runtime.extraction import resume_papers
    from ara.runtime.logging import EventLog
    from test_extraction import ROOT
    from ara.runtime.salvage import accepted_ranges
    calls, provider, papers, *_ = rig
    first = graph(); first.update(coverage_complete=False, new_gaps=[dict(description='Q')])
    review = {**graph(), 'items': [dict(graph()['items'][0], id='s')]}
    review['resolutions'] = [dict(obligation_id='p:r1-2:turn:1:gap:0', evidence_ids=['p:r1-2:p', 's'])]
    sequence(monkeypatch, provider, [first, review])
    path = extract(calls, papers[:1])
    log = EventLog(tmp_path/'follow/events.jsonl')
    ranges = accepted_ranges(calls.log.read(), papers[:1], calls.config, ROOT, log)['p']
    assert sum(len(r['result'].items) for r in ranges) == 9
    obligations = [o for r in ranges for o in json.loads(r['result'].obligations_json)]
    resolutions = [o for r in ranges for o in json.loads(r['result'].resolutions_json)]
    assert resolutions[0]['obligation_id'] == obligations[0]['id']
    assert set(resolutions[0]['evidence_ids']) <= {i.id for r in ranges for i in r['result'].items}


def test_native_salvage_only_never_constructs_provider(rig, monkeypatch, tmp_path):
    from ara.runtime.cli import main
    calls, provider, papers, manifest, fulltext, config = rig
    def forbidden(*args, **kwargs): raise AssertionError('provider constructed')
    run = tmp_path/'native-salvage'
    assert main(['extract', '--config', str(config), '--manifest', str(manifest),
                 '--fulltext-dir', str(fulltext), '--run-dir', str(run), '--paper-id', 'p',
                 '--salvage-only'], calls_factory=forbidden) == 0
    value = json.loads((run/'literature.extracted.txt').read_text()[len(HEADER):])
    assert value['papers'][0]['status'] == 'not extracted'
    assert value['publication_roster'][0]['reason']


def test_historical_thin_retry_is_not_repeated(rig, monkeypatch, tmp_path):
    from ara.runtime.calls import ModelCalls
    from ara.runtime.cache import Cache
    from ara.runtime.extraction import resume_papers
    from ara.runtime.logging import EventLog
    from test_extraction import ROOT
    calls, provider, papers, *_ = rig
    paper = replace(papers[0], pages=tuple(PageText(n, 'P') for n in range(1, 21)))
    first = graph(); first['items'] = first['items'][:1]
    second = graph(page=11); second['items'] = second['items'][:1]
    sent = sequence(monkeypatch, provider, [first, first, second, {**graph(), 'items': []}])
    extract(calls, (paper,))
    assert len(sent) == 4
    log = EventLog(tmp_path/'follow/events.jsonl')
    reused = resume_papers(log, (paper,), [calls.log.path.parent], calls.config, ROOT)
    sent.clear()
    follow = ModelCalls(calls.config, provider, log, Cache(tmp_path/'follow/cache'), ROOT, '')
    path = extract(follow, (paper,), reused=reused)
    assert sent == []
    value = json.loads(path.read_text()[len(HEADER):])['papers'][0]
    assert len(value['items']) == 3
    assert any(d['kind'] == 'thin_range' for d in value['dispositions'])


def test_refinement_discloses_conflicting_inference_disposition(rig, monkeypatch):
    calls, provider, papers, *_ = rig
    paper = replace(papers[0], pages=tuple(PageText(n, 'P') for n in range(1, 21)))
    first = graph(); first['items'] = first['items'][:1]; first['no_inference_reason'] = 'P'
    sequence(monkeypatch, provider, [first, graph(), graph(page=11), {**graph(), 'items': []}])
    result = calls.extract_paper(paper)
    assert len(result.items) == 17
    kinds = {d['kind'] for d in json.loads(result.dispositions_json)}
    assert {'no_explicit_inferential_structure', 'inference_disposition_conflict'} <= kinds


def test_accepted_review_fills_thin_range_before_paid_retry(rig, monkeypatch, tmp_path):
    from ara.runtime.calls import ModelCalls
    from ara.runtime.cache import Cache
    from ara.runtime.logging import EventLog
    from ara.runtime.salvage import accepted_ranges, is_thin
    from test_extraction import ROOT
    calls, provider, papers, *_ = rig
    paper = replace(papers[0], pages=tuple(PageText(n, 'P') for n in range(1, 21)))
    monkeypatch.setattr('ara.runtime.calls.extraction_range_plan', lambda *a: [(paper.pages[:10], 1), (paper.pages[10:], 1)])
    # Capture the old accepted-range/review pattern through native receipts.
    monkeypatch.setattr('ara.runtime.salvage.is_thin', lambda *a: False)
    first = graph(); first['items'] = first['items'][:1]
    sent = sequence(monkeypatch, provider, [first, graph(page=11), graph()])
    extract(calls, (paper,))
    log = EventLog(tmp_path/'follow/events.jsonl')
    entries = accepted_ranges(calls.log.read(), (paper,), calls.config, ROOT, log)['p']
    monkeypatch.setattr('ara.runtime.salvage.is_thin', is_thin)
    sent.clear()
    follow = ModelCalls(calls.config, provider, log, Cache(tmp_path/'follow/cache'), ROOT, '')
    result = follow.extract_paper(paper, salvaged=entries)
    assert not sent and len(result.items) == 17
    kinds = {d['kind'] for d in json.loads(result.dispositions_json)}
    assert 'thin_range_filled_by_accepted_evidence' in kinds and 'thin_range' not in kinds
