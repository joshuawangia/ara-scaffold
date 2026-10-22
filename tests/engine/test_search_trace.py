"""Placeholder-only trace proofs against the native search queue."""
import json
import pytest
from contextlib import contextmanager

from ara.runtime.logging import EventLog, read_log
from ara.runtime.search_traces import SearchTraceFiles

from ara.types import Formula
from test_search import engine, table, mp, P, Q, prop, proposal


class MemoryTraces:
    def __init__(self):
        self.rows = []

    @contextmanager
    def open_search(self, search_id):
        yield self

    def record(self, action, **payload):
        self.rows.append(dict(action=action, **payload))


def traced_engine(*args, **kwargs):
    e, ports = engine(*args, **kwargs)
    e.traces = MemoryTraces()
    return e, ports


def traces(e):
    return e.traces.rows


def test_trace_branches_rejections_and_completed_graphs():
    cut = mp()
    rejected = proposal('absent', Q, antecedent=P)
    e, ports = traced_engine(table(P, Formula('implies', (P, Q))),
                      {Q.canonical(): (cut, cut, rejected)})
    result = e.analyse(prop(Q))
    rows = traces(e)
    begins = [r for r in rows if r['action'] == 'begin']
    assert len(begins) == 2 and begins[0]['search_id'] != begins[1]['search_id']
    assert any(r.get('kind') == 'formula' and r.get('value') == Q.negated().to_dict() for r in rows)
    positive = rows[:rows.index(begins[1])]
    states = {r['state_id']: r for r in positive if r['action'] == 'state'}
    assert states[0]['parent_state_id'] is None
    assert states[1]['parent_state_id'] == 0 and states[1]['bank_id'] == 'modus_ponens'
    assert {r['node_id']: r['depth'] for r in positive if r['action'] == 'node'} == {'n0': 0, 'n1': 1, 'n2': 1}
    assert all('graph' not in r for r in positive if r['action'] != 'complete')
    assert {r['reason'] for r in positive if r['action'] == 'prune'} == {'DUPLICATE_PROPOSAL', 'UNKNOWN_BANK_ID'}
    terminal = next(r for r in positive if r['action'] == 'complete')
    assert terminal['graph'] == result.target.routes[0].to_dict()
    assert terminal['reason'] == 'ROUTE_CLOSED'
    assert {n['t_id'] for n in terminal['graph']['nodes'] if n['kind'] == 'leaf'} == {'t0', 't1'}


def test_trace_records_cap_and_interrupted_search():
    import pytest
    for bounds in ({'depth_cap': 0}, {'node_cap': 2}):
        e, ports = traced_engine(table(), {Q.canonical(): (mp(),)}, **bounds)
        e.search(prop(Q))
        rows = traces(e)
        assert any(r.get('reason') in ('DEPTH_CAP', 'NODE_CAP') for r in rows)
        assert rows[-1]['action'] == 'end' and rows[-1]['truncated']
    e, ports = traced_engine(table())
    def stop(*args):
        raise RuntimeError('placeholder stop')
    ports.propose_cuts = stop
    with pytest.raises(RuntimeError):
        e.search(prop(Q))
    rows = traces(e)
    assert rows[0]['action'] == 'begin'
    assert rows[-1]['action'] == 'expand'
    assert not any(r['action'] == 'end' for r in rows)


def test_native_trace_renders_both_polarities(tmp_path):
    from ara.runtime.logging import EventLog
    from ara.runtime.report import generate_report
    e, ports = traced_engine(table(P, Formula('implies', (P, Q))), {Q.canonical(): (mp(),)})
    log = EventLog(tmp_path / 'run/events.jsonl')
    e.traces = SearchTraceFiles(log)
    analysis = e.analyse(prop(Q))
    log.record('commitments_frozen', commitments=e.commitments.to_dict())
    for event in ports.events:
        log.emit(event)
    for result, polarity in ((analysis.target, 'target'), (analysis.negated, 'negation')):
        for graph in result.routes:
            log.record('route', target='Q', polarity=polarity, graph=graph.to_dict())
    generate_report([log.path.parent], tmp_path / 'out')
    data = json.loads((tmp_path/'out/data.json').read_text())['runs'][0]
    assert len(data['search']['traces']) == 2
    assert all(t['complete'] for t in data['search']['traces'])
    terminal_decisions = [d for t in data['search']['traces'] for d in t['decisions']
                          if d['decision']['reason_code'].startswith('ROUTE_')]
    assert not terminal_decisions  # v2 keeps original decisions in their chained appendix
    assert any(d['decision']['reason_code'].startswith('ROUTE_') for d in data['search']['engine_decisions'])
    assert len([r for r in read_log(log.path) if r['event']['stage'] == 'search_trace_receipt']) == 2
    assert {r['polarity'] for r in data['routes']} == {'target', 'negation'}
    assert not any('PARTIAL SEARCH TRACE' in gap for gap in data['gaps'])
    assert len([x for x in data['tree_exports'] if x['kind'] == 'search']) == 2
    html = (tmp_path/'out/report.html').read_text()
    assert 'NO_ADMITTED_PROPOSAL' in html and 'ROUTE_CLOSED' in html


def sealed_search(tmp_path):
    e, ports = engine(table(P, Formula('implies', (P, Q))), {Q.canonical(): (mp(),)})
    log = EventLog(tmp_path/'run/events.jsonl')
    e.traces = SearchTraceFiles(log)
    e.search(prop(Q))
    seal = json.loads(read_log(log.path)[0]['event']['payload_json'])
    return log, log.path.parent / seal['path']


def test_sidecar_seal_is_required_and_checked_before_use(tmp_path):
    import pytest
    from ara.runtime.logging import LogTampered
    from ara.runtime.report import build_run
    log, path = sealed_search(tmp_path)
    run = build_run(log.path.parent)
    assert run['search']['traces'][0]['complete']
    original = path.read_bytes()
    path.write_bytes(original.replace(b'ROUTE_CLOSED', b'ROUTE_OPEN'))
    with pytest.raises(LogTampered, match='sidecar hash mismatch'):
        build_run(log.path.parent)
    path.unlink()
    run = build_run(log.path.parent)
    assert not run['search']['traces'][0]['complete']
    assert any('unavailable' in i for i in run['search']['traces'][0]['issues'])
    path.with_name('unsealed.jsonl').write_bytes(b'not trusted json\n')
    run = build_run(log.path.parent)
    unsealed = run['search']['traces'][-1]
    assert not unsealed['complete'] and not unsealed['authenticated'] and not unsealed['receipts']


def test_interrupted_native_sidecar_is_unsealed(tmp_path):
    import pytest
    from ara.runtime.report import build_run
    e, ports = engine(table())
    log = EventLog(tmp_path/'run/events.jsonl')
    log.record('run_started')
    e.traces = SearchTraceFiles(log)
    def stop(*args):
        raise RuntimeError('P')
    ports.propose_cuts = stop
    with pytest.raises(RuntimeError):
        e.search(prop(Q))
    assert not any(r['event']['stage'] == 'search_trace_receipt' for r in read_log(log.path))
    trace = build_run(log.path.parent)['search']['traces'][0]
    assert not trace['complete'] and not trace['authenticated']


def test_imported_and_relocated_sidecar(tmp_path):
    import shutil
    from ara.runtime.provenance import import_receipts, checkpoint
    from ara.runtime.report import build_run
    log, path = sealed_search(tmp_path)
    imported = EventLog(tmp_path/'import/events.jsonl')
    import_receipts(imported, tuple(log.read()), checkpoint(log.path))
    assert build_run(imported.path.parent)['search']['traces'][0]['complete']
    shutil.copytree(path.parent, imported.path.parent/'search-traces')
    path.unlink()
    assert build_run(imported.path.parent)['search']['traces'][0]['complete']


def test_invalid_sealed_references_and_line_counts(tmp_path):
    import hashlib
    import pytest
    from ara.runtime.logging import LogTampered
    from ara.runtime.cache import canonical
    from ara.runtime.report import build_run
    log, path = sealed_search(tmp_path)
    events = log.read()
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    next(r for r in rows if r['action'] == 'node')['formula_id'] = 'absent'
    raw = ''.join(canonical(r) + '\n' for r in rows).encode()
    path.write_bytes(raw)
    seal = json.loads(events[0]['payload_json'])
    seal['sha256'] = hashlib.sha256(raw).hexdigest()
    def reseal():
        log.path.unlink()
        log.anchor.unlink()
        log.record('search_trace_receipt', **seal)
    reseal()
    trace = build_run(log.path.parent)['search']['traces'][0]
    assert not trace['complete'] and 'unresolved formula reference' in trace['issues']
    seal['line_count'] += 1
    reseal()
    with pytest.raises(LogTampered, match='line count'):
        build_run(log.path.parent)


def test_native_500_state_trace_full_report(tmp_path, monkeypatch):
    from test_search import Scripted
    from ara.runtime.report import generate_report
    import ara.runtime.report_render as rendering
    monkeypatch.setattr(rendering.shutil, 'which', lambda _: None)
    e, ports = engine(table(), depth_cap=6, node_cap=500)
    entry = e.bank.get('expert_opinion')
    def propose(goal, commitments, entries):
        child = Formula('and', (goal.formula, P))
        return (proposal(entry.id, goal.formula, **{s.id: child for s in entry.premise_slots}),)
    ports.propose_cuts = propose
    log = EventLog(tmp_path/'run/events.jsonl')
    e.traces = SearchTraceFiles(log)
    result = e.search(prop(P))
    assert result.nodes_created == 499 and len(result.routes) == 1
    generate_report([log.path.parent], tmp_path/'out')
    trace = json.loads((tmp_path/'out/data.json').read_text())['runs'][0]['search']['traces'][0]
    assert trace['complete'], trace['issues']
    assert len(trace['states']) == 500
    html = (tmp_path/'out/report.html').read_text()
    assert html.count('<div id="run-0-search-0-state-') == 500
    assert 'state-499' in html and 'State 499' in html


@pytest.mark.parametrize('fault, expected', [
    ('version', 'unsupported trace version'),
    ('duplicate', 'duplicate state ID'),
    ('orphan', 'state parent absent'),
    ('terminal', 'terminal state completion coverage'),
    ('definition', 'unresolved formula reference'),
    ('cycle', 'cyclic ancestry'),
    ('fields', 'invalid terminal graph fields'),
    ('action', 'unsupported trace action'),
])
def test_sealed_trace_semantics_are_checked_before_rendering(tmp_path, monkeypatch, fault, expected):
    import hashlib
    from ara.runtime.cache import canonical
    from ara.runtime.report import generate_report
    import ara.runtime.report_render as rendering
    monkeypatch.setattr(rendering.shutil, 'which', lambda _: None)
    log, path = sealed_search(tmp_path)
    seal = json.loads(log.read()[0]['payload_json'])
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    state = next(r for r in rows if r['action'] == 'state' and r['state_id'] == 1)
    terminal = next(r for r in rows if r['action'] == 'complete')
    if fault == 'version': rows[0]['version'] = 99
    if fault == 'duplicate': state['state_id'] = 0
    if fault == 'orphan': state['parent_state_id'] = 99
    if fault == 'terminal': rows.remove(terminal)
    if fault == 'definition':
        rows = [r for r in rows if not (r['action'] == 'definition' and r.get('kind') == 'formula')]
    if fault == 'cycle': terminal['graph']['nodes'][0]['children'].append('n0')
    if fault == 'fields': terminal['graph']['nodes'][0]['proposition'] = None
    if fault == 'action': rows.insert(-1, dict(action='future'))
    for index, row in enumerate(rows): row['seq'] = index
    raw = ''.join(canonical(row) + '\n' for row in rows).encode()
    path.write_bytes(raw)
    seal.update(sha256=hashlib.sha256(raw).hexdigest(), line_count=len(rows))
    log.path.unlink()
    log.anchor.unlink()
    log.record('search_trace_receipt', **seal)
    generate_report([log.path.parent], tmp_path/'out')
    trace = json.loads((tmp_path/'out/data.json').read_text())['runs'][0]['search']['traces'][0]
    assert not trace['complete']
    assert any(expected in issue for issue in trace['issues']), trace['issues']
    assert len(trace['receipts']) == len(rows)
