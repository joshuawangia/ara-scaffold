"""Offline reporting fixtures contain placeholder content only."""
from dataclasses import replace
import json
from pathlib import Path

import pytest

from ara.runtime.cache import canonical
from ara.runtime.cli import main
from ara.runtime.logging import EventLog, LogTampered, read_log
from ara.runtime.provenance import checkpoint, import_receipts
from ara.runtime.report import build_run, generate_report
from ara.types import Commitment, CommitmentSet, Formula, Proposition, RouteGraph, RouteNode, RunEvent, TokenUsage


def call(log, cost, *, unknown=False, source='paper-p', timestamp='2026-01-01T00:00:01Z'):
    log.emit(RunEvent(timestamp, 'extract_paper', 'MODEL', 'model-p', 'version-p', 'P', 'P',
                      TokenUsage(input_tokens=7), cost, 2,
                      payload_json=canonical(dict(source_id=source, cache_hit=False,
                          accounting='reservation_unknown_actual' if unknown else 'actual'))))


def fixture(directory):
    log = EventLog(directory / 'events.jsonl')
    log.human('run', '<script>P</script>')
    log.record('run_started', config={'token_cap': 100, 'model': 'model-p'})
    log.record('extraction_batch_started', selected=['paper-p', 'paper-q'])
    log.record('extraction_outcome', source_id='paper-p', status='extracted', pages=2, affected_pages=[],
               items=[dict(id='p', source_id='paper-p', citation='paper-p:pdf:2#p', kind='claim',
                           text='P', page_start=2, page_end=2)])
    log.record('extraction_outcome', source_id='paper-q', status='failed', reason='placeholder failure', items=[])
    call(log, 1)
    call(log, 3, unknown=True, timestamp='2026-01-01T00:00:02Z')
    c = Commitment('p', 'P', 'paper-p:pdf:2#p', Formula('atom', name='P'))
    log.record('commitments_frozen', commitments=CommitmentSet((c,)).to_dict())
    graph = RouteGraph('route-p', 'n0', (RouteNode('n0', Proposition('p', 'P', c.formula), 'leaf', 'p'),), status='CLOSED')
    log.record('route', target='p', polarity='target', graph=graph.to_dict())
    return log


def test_report_native_readonly_accounting_and_citations(tmp_path, monkeypatch):
    import ara.runtime.report_render as rendering
    monkeypatch.setattr(rendering.shutil, 'which', lambda _: None)
    directory = tmp_path/'input'
    log = fixture(directory)
    before = {p.name: p.read_bytes() for p in directory.iterdir()}
    def forbidden(*args, **kwargs):
        raise AssertionError('report must not call a model or engine')
    out = tmp_path/'output'
    assert main(['report', '--run-dir', str(directory), '--out', str(out)],
                calls_factory=forbidden, engine_factory=forbidden) == 0
    assert before == {p.name: p.read_bytes() for p in directory.iterdir()}
    data = json.loads((out/'data.json').read_text())
    run = data['runs'][0]
    assert data['accounting']['measured']['cost_usd'] == 1
    assert data['accounting']['unknown_at_reservation']['cost_usd'] == 3
    assert data['accounting']['budget_accounted']['cost_usd'] == 4
    assert data['accounting']['measured']['tokens']['input_tokens'] == 7
    assert data['accounting']['unknown_at_reservation']['tokens']['input_tokens'] == 7
    route = json.loads((out/run['routes'][0]['file']).read_text())
    assert route['support_chain'][0]['commitment']['source_evidence'][0]['page_start'] == 2
    assert run['routes'][0]['model_summary'] is None
    assert run['construction']['by_kind'] == {'claim': 1}
    assert run['extraction']['exclusions'][0]['source_id'] == 'paper-q'
    html = (out/'report.html').read_text()
    assert '<script>' not in html and '&lt;script&gt;P&lt;/script&gt;' in html
    assert '<script src=' not in html and '<details' in html
    assert 'PARTIAL SEARCH TRACE' in html and 'Model-written route summaries' in html
    assert '[Full data]' in (out/'report.md').read_text()
    assert len(list((out/'trees').glob('*.dot'))) == 1
    assert not list((out/'trees').glob('*.svg'))
    envelopes = json.loads((out/'run-0-events.json').read_text())
    restored = [{**{k:v for k,v in row.items() if k != 'event_ref'},
                 'event': json.loads((out/row['event_ref']).read_text())} for row in envelopes]
    assert restored == read_log(log.path)


@pytest.mark.parametrize('tamper', ['event', 'truncate', 'anchor'])
def test_report_refuses_tampering_before_output(tmp_path, tamper):
    log = fixture(tmp_path/'input')
    if tamper == 'event':
        log.path.write_text(log.path.read_text().replace('placeholder failure', 'Q'))
    elif tamper == 'truncate':
        log.path.write_text(''.join(log.path.read_text().splitlines(keepends=True)[:-1]))
    else:
        log.anchor.write_text('0'*64+'\n')
    with pytest.raises(LogTampered):
        generate_report([log.path.parent], tmp_path/'output')
    assert not (tmp_path/'output').exists()


def test_imported_receipts_deduplicate_combined_accounting(tmp_path):
    first = EventLog(tmp_path/'first/events.jsonl')
    call(first, 1)
    second = EventLog(tmp_path/'second/events.jsonl')
    origin = checkpoint(first.path)
    import_receipts(second, tuple(r['event'] for r in read_log(first.path)), origin)
    call(second, 2, timestamp='2026-01-01T00:00:03Z')
    generate_report([first.path.parent, second.path.parent, second.path.parent], tmp_path/'output')
    data = json.loads((tmp_path/'output/data.json').read_text())
    assert len(data['runs']) == 2
    assert data['accounting']['measured']['cost_usd'] == 3
    assert data['runs'][1]['accounting']['local']['measured']['cost_usd'] == 2
    assert data['runs'][1]['accounting']['inherited']['measured']['cost_usd'] == 1
    first.path.write_text(first.path.read_text().replace('version-p', 'version-q'))
    with pytest.raises(LogTampered):
        build_run(second.path.parent)


def test_historical_success_is_not_current_success_and_pending_is_visible(tmp_path):
    log = EventLog(tmp_path/'input/events.jsonl')
    log.record('extraction_batch_started', selected=['paper-p'])
    log.record('extraction_outcome', source_id='paper-p', status='extracted', items=[])
    log.record('extraction_batch_started', selected=['paper-p'])
    log.record('extraction_stopped', not_attempted=['paper-p'], reason='P')
    log.record('call_start', cache_key='p', kind='extract_paper', reserved_usage={'input_tokens': 7})
    run = build_run(log.path.parent)
    assert run['extraction']['papers'][0]['status'] == 'not attempted'
    assert run['extraction']['corpus_totals']['papers'] == 0
    assert len(run['accounting']['unresolved_dispatches']) == 1
    assert run['accounting']['measured']['cost_usd'] == 0


def test_output_cannot_modify_inputs_or_existing_report(tmp_path):
    log = fixture(tmp_path/'input')
    with pytest.raises(ValueError, match='separate'):
        generate_report([log.path.parent], log.path.parent/'output')
    (tmp_path/'out').mkdir()
    (tmp_path/'out/keep').write_text('P')
    with pytest.raises(ValueError, match='empty'):
        generate_report([log.path.parent], tmp_path/'out')
    assert (tmp_path/'out/keep').read_text() == 'P'


def test_missing_checkpoint_and_origin_are_explicit_gaps(tmp_path):
    first = EventLog(tmp_path/'first/events.jsonl')
    call(first, 1)
    second = EventLog(tmp_path/'second/events.jsonl')
    import_receipts(second, tuple(r['event'] for r in read_log(first.path)), checkpoint(first.path))
    first.path.unlink()
    second.anchor.unlink()
    run = build_run(second.path.parent)
    assert any('Tail checkpoint absent' in gap for gap in run['gaps'])
    assert any('Origin unavailable' in gap for gap in run['gaps'])


def test_svg_render_failure_is_disclosed(tmp_path, monkeypatch):
    import ara.runtime.report_render as rendering
    from subprocess import CompletedProcess
    monkeypatch.setattr(rendering.shutil, 'which', lambda _: '/placeholder/dot')
    monkeypatch.setattr(rendering.subprocess, 'run', lambda *a, **kw: CompletedProcess(a, 1, '', 'P'))
    log = fixture(tmp_path/'input')
    generate_report([log.path.parent], tmp_path/'out')
    run = json.loads((tmp_path/'out/data.json').read_text())['runs'][0]
    assert any('SVG rendering failed' in g for g in run['gaps'])
    assert (tmp_path/'out/trees/run-0-route-0.dot').is_file()


def test_exclusion_roster_retains_selected_papers_without_any_outcome(tmp_path):
    log = EventLog(tmp_path/'input/events.jsonl')
    log.record('extraction_started', selected=['paper-p', 'paper-q'])
    log.record('extraction_batch_started', selected=['paper-p', 'paper-q'])
    log.record('extraction_batch_started', selected=['paper-p'])
    run = build_run(log.path.parent)
    papers = {p['source_id']: p for p in run['extraction']['papers']}
    assert set(papers) == {'paper-p', 'paper-q'}
    assert papers['paper-q']['status'] == 'historical only'
    assert run['extraction']['corpus_totals']['requested_across_lineage'] == 2
    assert next(p for p in run['extraction']['exclusions'] if p['source_id'] == 'paper-q')['reason'] == 'not selected in latest recorded batch'


def test_svg_success_is_linked_without_embedding(tmp_path, monkeypatch):
    import ara.runtime.report_render as rendering
    from subprocess import CompletedProcess
    monkeypatch.setattr(rendering.shutil, 'which', lambda _: '/placeholder/dot')
    monkeypatch.setattr(rendering.subprocess, 'run', lambda *a, **kw: CompletedProcess(a, 0, '<svg xmlns="http://www.w3.org/2000/svg"><text>P</text></svg>', ''))
    log = fixture(tmp_path/'input')
    generate_report([log.path.parent], tmp_path/'out')
    run = json.loads((tmp_path/'out/data.json').read_text())['runs'][0]
    assert run['tree_exports'][0]['svg'] == 'trees/run-0-route-0.svg'
    assert (tmp_path/'out/trees/run-0-route-0.svg').read_text().startswith('<svg')
    assert 'href="trees/run-0-route-0.svg"' in (tmp_path/'out/report.html').read_text()
    assert 'data:image/svg' not in (tmp_path/'out/report.html').read_text()


def test_unmatched_citation_never_invents_source_pages(tmp_path):
    log = fixture(tmp_path/'input')
    c = Commitment('p', 'P', 'paper-q:pdf:1#p', Formula('atom', name='P'))
    log.record('commitments_frozen', commitments=CommitmentSet((c,)).to_dict())
    run = build_run(log.path.parent)
    assert run['construction']['commitments'][0]['source_evidence'] == []
    assert any('source paper, kind and page linkage cannot be established' in g for g in run['gaps'])


def test_all_inputs_verified_before_any_output(tmp_path):
    first = fixture(tmp_path/'first')
    second = fixture(tmp_path/'second')
    second.path.write_text(second.path.read_text().replace('placeholder failure', 'Q'))
    with pytest.raises(LogTampered):
        generate_report([first.path.parent, second.path.parent], tmp_path/'out')
    assert not (tmp_path/'out').exists()


def test_received_usage_survives_interruption_without_becoming_a_final_charge(tmp_path):
    log = EventLog(tmp_path/'input/events.jsonl')
    log.record('call_start', kind='extract_paper', cache_key='p', reserved_usage={'input_tokens': 100})
    log.record('response_received', kind='extract_paper', cache_key='p', measured_cost_usd=2,
               measured_usage={'input_tokens': 7}, raw_response={'content': 'P'})
    run = build_run(log.path.parent)
    assert run['accounting']['unfinalized_measured_totals']['cost_usd'] == 2
    assert run['accounting']['unfinalized_measured_totals']['tokens']['input_tokens'] == 7
    assert run['accounting']['budget_accounted']['cost_usd'] == 0
    assert len(run['accounting']['unresolved_dispatches']) == 1
    log.emit(RunEvent('2026-01-01T00:00:01Z', 'extract_paper', 'MODEL', cost_usd=2,
                     payload_json=canonical(dict(cache_key='p', accounting='actual', cache_hit=False))))
    run = build_run(log.path.parent)
    assert run['accounting']['unfinalized_measured_totals']['cost_usd'] == 0
    assert run['accounting']['measured']['cost_usd'] == 2
    assert not run['accounting']['unresolved_dispatches']


def test_dot_preserves_unicode_and_quotes_labels():
    from ara.runtime.report_render import route_dot
    graph = RouteGraph('p', 'n0', (RouteNode('n0', Proposition('p', 'P ∧ Q\n"R"'), 'leaf'),))
    dot = route_dot(graph.to_dict())
    assert 'P ∧ Q' in dot and '\\n\\"R\\"' in dot
    assert 'depth 0' in dot


def test_imported_evidence_and_literature_projection_keep_source_counts(tmp_path):
    log = fixture(tmp_path/'input')
    item = dict(id='p', source_id='paper-p', citation='paper-p:pdf:2#p', kind='claim',
                text='P', page_start=2, page_end=2)
    log.record('extraction_outcome', source_id='paper-p', status='extracted', record={'id': 'paper-p'}, items=[item])
    log.record('run_started', literature='# ARA extracted literature v2\n' + canonical({'papers':[
        dict(source_id='paper-p', status='extracted', items=[item])]}))
    run = build_run(log.path.parent)
    assert len(run['construction']['commitments'][0]['source_evidence']) == 2
    assert run['construction']['by_source'] == {'paper-p': 1}
    assert run['construction']['by_kind'] == {'claim': 1}


def test_missing_ancestor_does_not_hide_available_origin_mismatch(tmp_path):
    a = EventLog(tmp_path/'a/events.jsonl')
    call(a, 1)
    b = EventLog(tmp_path/'b/events.jsonl')
    import_receipts(b, tuple(a.read()), checkpoint(a.path))
    call(b, 2)
    c = EventLog(tmp_path/'c/events.jsonl')
    import_receipts(c, tuple(b.read()), checkpoint(b.path))
    a.path.unlink()
    run = build_run(c.path.parent)
    assert run['accounting']['measured']['cost_usd'] == 3
    warnings = [g for g in run['gaps'] if 'Origin unavailable' in g]
    assert len(warnings) == 1 and str(a.path) in warnings[0] and str(b.path) not in warnings[0]
    events = c.read()
    c.path.unlink()
    c.anchor.unlink()
    for event in events:
        if event['cost_usd'] == 2:
            event['cost_usd'] = 102
        c.emit(RunEvent.from_dict(event))
    with pytest.raises(ValueError, match='import does not match pinned events'):
        build_run(c.path.parent)


@pytest.mark.parametrize('marker', [None, 'future'])
def test_unclassified_incomplete_receipts_are_not_measured(tmp_path, marker):
    log = EventLog(tmp_path/'run/events.jsonl')
    data = dict(status='incomplete', cache_hit=False)
    if marker is not None:
        data['accounting'] = marker
    log.emit(RunEvent('2026-01-01T00:00:01Z', 'extract_paper', 'MODEL', cost_usd=3,
                      usage=TokenUsage(input_tokens=7), payload_json=canonical(data)))
    run = build_run(log.path.parent)
    a = run['accounting']
    assert a['measured']['cost_usd'] == 0
    assert a['unclassified']['cost_usd'] == 3
    assert a['unclassified']['tokens']['input_tokens'] == 7
    assert a['timeline'][0]['classification'] == 'unclassified'
    assert a['timeline'][0]['unclassified_cumulative_usd'] == 3
    assert a['timeline'][0]['recorded_accounting'] == marker
    assert any('unclassified' in g.lower() for g in run['gaps'])


@pytest.mark.parametrize('fault', ['empty', 'version', 'orphan', 'cycle', 'duplicate', 'terminal', 'target', 'reason'])
def test_invalid_trace_is_partial_and_still_renders(tmp_path, fault, monkeypatch):
    import ara.runtime.report_render as rendering
    monkeypatch.setattr(rendering.shutil, 'which', lambda _: None)
    log = fixture(tmp_path/'run')
    rows = [dict(action='begin', target={'id': 'P'}),
            dict(action='state', state_id=0, parent_state_id=None, transition='root'),
            dict(action='state', state_id=1, parent_state_id=0, transition='block', reason='P'),
            dict(action='end', routes=['P'])]
    if fault == 'empty': rows = [rows[0], rows[-1]]
    if fault == 'orphan': rows[2]['parent_state_id'] = 99
    if fault == 'cycle': rows[2]['parent_state_id'] = 1
    if fault == 'duplicate': rows[2]['state_id'] = 0
    if fault == 'target': rows[0]['target'] = 'P'
    if fault == 'reason': rows.insert(-1, dict(action='prune', state_id=1))
    for row in rows:
        log.record('search_trace', version=99 if fault == 'version' else 1, search_id='P', **row)
    generate_report([log.path.parent], tmp_path/'out')
    run = json.loads((tmp_path/'out/data.json').read_text())['runs'][0]
    assert not run['search']['traces'][0]['complete']
    assert any('PARTIAL SEARCH TRACE' in g for g in run['gaps'])
    trace = json.loads((tmp_path/'out'/run['search']['traces'][0]['file']).read_text())
    assert len(trace['receipts']) == len(rows)
    expected = {'empty': 'root state inventory', 'version': 'unsupported trace version',
                'orphan': 'state parent absent', 'cycle': 'state parent absent',
                'duplicate': 'duplicate state ID', 'terminal': 'terminal state completion coverage',
                'target': 'invalid target inventory'}
    if fault in expected:
        assert any(expected[fault] in issue for issue in run['search']['traces'][0]['issues'])
