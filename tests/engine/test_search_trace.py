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
