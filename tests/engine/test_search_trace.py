"""Placeholder-only trace proofs against the native search queue."""
import json

from ara.types import Formula
from test_search import engine, table, mp, P, Q, prop, proposal


def traces(ports):
    return [json.loads(e.payload_json) for e in ports.events if e.stage == 'search_trace']


def test_trace_branches_rejections_and_completed_graphs():
    cut = mp()
    rejected = proposal('absent', Q, antecedent=P)
    e, ports = engine(table(P, Formula('implies', (P, Q))),
                      {Q.canonical(): (cut, cut, rejected)})
    result = e.analyse(prop(Q))
    rows = traces(ports)
    begins = [r for r in rows if r['action'] == 'begin']
    assert len(begins) == 2 and begins[0]['search_id'] != begins[1]['search_id']
    assert begins[1]['target']['formula'] == Q.negated().to_dict()
    positive = [r for r in rows if r['search_id'] == begins[0]['search_id']]
    states = {r['state_id']: r for r in positive if r['action'] == 'state'}
    assert states[0]['parent_state_id'] is None
    assert states[1]['parent_state_id'] == 0 and states[1]['bank_id'] == 'modus_ponens'
    assert states[1]['depths'] == {'n0': 0, 'n1': 1, 'n2': 1}
    assert {r['reason'] for r in positive if r['action'] == 'prune'} == {'DUPLICATE_PROPOSAL', 'UNKNOWN_BANK_ID'}
    terminal = next(r for r in positive if r['action'] == 'complete')
    assert terminal['graph'] == result.target.routes[0].to_dict()
    assert terminal['reason'] == 'ROUTE_CLOSED'
    assert {n['t_id'] for n in terminal['graph']['nodes'] if n['kind'] == 'leaf'} == {'t0', 't1'}


def test_trace_records_cap_and_interrupted_search():
    import pytest
    for bounds in ({'depth_cap': 0}, {'node_cap': 2}):
        e, ports = engine(table(), {Q.canonical(): (mp(),)}, **bounds)
        e.search(prop(Q))
        rows = traces(ports)
        assert any(r.get('reason') in ('DEPTH_CAP', 'NODE_CAP') for r in rows)
        assert rows[-1]['action'] == 'end' and rows[-1]['truncated']
    e, ports = engine(table())
    def stop(*args):
        raise RuntimeError('placeholder stop')
    ports.propose_cuts = stop
    with pytest.raises(RuntimeError):
        e.search(prop(Q))
    rows = traces(ports)
    assert rows[0]['action'] == 'begin'
    assert rows[-1]['action'] == 'expand'
    assert not any(r['action'] == 'end' for r in rows)


def test_native_trace_renders_both_polarities(tmp_path):
    from ara.runtime.logging import EventLog
    from ara.runtime.report import generate_report
    e, ports = engine(table(P, Formula('implies', (P, Q))), {Q.canonical(): (mp(),)})
    analysis = e.analyse(prop(Q))
    log = EventLog(tmp_path / 'run/events.jsonl')
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
    assert terminal_decisions and all(d['context'] == {} for d in terminal_decisions)
    assert {r['polarity'] for r in data['routes']} == {'target', 'negation'}
    assert not any('PARTIAL SEARCH TRACE' in gap for gap in data['gaps'])
    assert len([x for x in data['tree_exports'] if x['kind'] == 'search']) == 2
    html = (tmp_path/'out/report.html').read_text()
    assert 'NO_ADMITTED_PROPOSAL' in html and 'ROUTE_CLOSED' in html
