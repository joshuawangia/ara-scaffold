from dataclasses import FrozenInstanceError

import pytest

from ara.types import (
    Commitment, CommitmentSet, Formula, PremiseFill, Proposition, Proposal,
    RouteGraph, RouteNode, Term, negate_proposition,
)


def atom(name):
    return Formula('atom', name=name)


def test_formula_roundtrip():
    p, q = atom('P'), atom('Q')
    formulas = [p, Formula('not', (p,)), Formula('and', (p, q)),
                Formula('or', (p, q)), Formula('implies', (p, q)),
                Formula('iff', (p, q)),
                Formula('predicate', name='F', terms=(Term('variable', 'x'), Term('constant', 'a')))]
    formulas.extend(Formula(op, (formulas[-1],), variable='x') for op in ('forall', 'exists'))
    for formula in formulas:
        assert Formula.from_json(formula.to_json()) == formula


def test_canonical_negation():
    p, q, r = atom('P'), atom('Q'), atom('R')
    left = Formula('and', (p, Formula('and', (q, r))))
    right = Formula('and', (r, q, p))
    assert left.canonical() == right.canonical()
    assert left.negated().negated().canonical() == left.canonical()
    assert p.negated().canonical() != p.canonical()
    assert Formula('not', (Formula('not', (p,)),)).canonical() == p.canonical()
    negated = negate_proposition(Proposition('p', 'P', p))
    assert negated.formula == p.negated()
    assert negated.text == p.negated().canonical()


@pytest.mark.parametrize('payload', [
    {'op': 'not', 'args': []}, {'op': 'atom', 'name': ''},
    {'op': 'forall', 'args': [{'op': 'atom', 'name': 'P'}]},
    {'op': 'unknown'}, {'op': 'atom', 'name': 'P', 'extra': 'Q'},
    {'op': 'atom', 'name': 'P', 'terms': [{'kind': 'constant', 'name': 'a'}]},
])
def test_malformed_formula_rejected(payload):
    with pytest.raises((ValueError, TypeError)):
        Formula.from_dict(payload)


def test_commitment_set_frozen():
    source = [Commitment('t1', 'P', 'placeholder:1', atom('P'))]
    table = CommitmentSet(source)
    source.clear()
    assert table.get('t1').text == 'P'
    assert table.get('missing') is None
    assert len(table.commitments) == 1
    with pytest.raises(FrozenInstanceError):
        table.commitments = ()
    with pytest.raises(FrozenInstanceError):
        table.commitments[0].text = 'Q'
    with pytest.raises(AttributeError):
        table.commitments.append(Commitment('t2', 'Q', 'placeholder:2', atom('Q')))
    assert table.contains_formula(atom('P'))
    assert not table.contains_formula(atom('P').negated())


def test_duplicate_commitment_rejected():
    c = Commitment('t1', 'P', 'placeholder:1', atom('P'))
    with pytest.raises(ValueError, match='duplicate'):
        CommitmentSet.build([c, c])


def test_route_graph_roundtrip():
    p = Proposition('p', 'P', atom('P'))
    proposal = Proposal('conjunction_elimination', (PremiseFill('conjunction', 'P', 't1'),), 'P')
    graph = RouteGraph('g1', 'n1', (
        RouteNode('n1', p, 'inference', proposal=proposal, children=('n2',)),
        RouteNode('n2', p, 'leaf', t_id='t1'),
    ), 'CLOSED')
    decoded = RouteGraph.from_json(graph.to_json())
    assert decoded == graph
    assert decoded.nodes[1].t_id == 't1'
    assert decoded.nodes[0].children == ('n2',)
    assert decoded.to_json() == graph.to_json()


def test_scoped_graph_and_event_roundtrip():
    from ara.types import CQAnswer, EngineDecision, ProofScope, RunEvent, TokenUsage
    p, q = Proposition('p', 'P', atom('P')), Proposition('q', 'Q', atom('Q'))
    graph = RouteGraph('g2', 'n3', (
        RouteNode('n1', p, 'assumption', scope_id='conditional'),
        RouteNode('n2', q, 'inference', children=('n1',), scope_id='conditional',
                  cq_answers=(CQAnswer('cq1', 'P', True, ('t1',)),)),
        RouteNode('n3', Proposition('pq', 'P -> Q', Formula('implies', (p.formula, q.formula))),
                  'inference', children=('n2',)),
    ), scopes=(ProofScope('conditional', 'n1', ('n2',), 'n3'),), frontier=('n2',))
    restored = RouteGraph.from_json(graph.to_json())
    assert restored == graph
    assert restored.scopes[0].result_node_ids == ('n2',)
    event = RunEvent('2026-10-08T00:00:00Z', 'licensing', 'ENGINE',
                     usage=TokenUsage(2, 3, 4, 5, 1),
                     decision=EngineDecision('discarded', 'UNKNOWN_BANK_ID', 'P'),
                     payload_json='{"b":2, "a":1}')
    assert RunEvent.from_json(event.to_json()) == event
    assert event.payload_json == '{"a":1,"b":2}'
    with pytest.raises(FrozenInstanceError):
        restored.scopes[0].result_node_ids = ()


def test_unformalised_negation_rejected():
    with pytest.raises(ValueError, match='formula'):
        negate_proposition(Proposition('p', 'P'))
