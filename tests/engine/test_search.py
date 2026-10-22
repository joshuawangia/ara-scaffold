from dataclasses import replace

from ara.bank import load_bank
from ara.engine.search import Engine, EngineConfig
from ara.types import Commitment, CommitmentSet, CQAnswer, Formula, PremiseFill, Proposal, Tier1Repair
from test_licensing import P, Q, R, Ports, prop, proposal


class Scripted(Ports):
    def __init__(self, cuts=None, answered=True):
        super().__init__()
        self.cuts, self.answered, self.goals, self.repairs = cuts or {}, answered, [], []

    def propose_cuts(self, goal, commitments, bank):
        self.goals.append(goal.formula.canonical())
        return self.cuts.get(goal.formula.canonical(), ())

    def map_leaf(self, leaf, commitments):
        return next((c.id for c in commitments.commitments if c.formula.canonical() == leaf.formula.canonical()), 'open')

    def answer_cq(self, question, proposal, commitments):
        return CQAnswer(question.id, 'P', self.answered, tuple(c.id for c in commitments.commitments[:1]))

    def repair_tier1(self, premises, conclusions, commitments):
        self.repairs.append((premises, conclusions))
        return Tier1Repair('unresolved', 'P')


def table(*formulas):
    return CommitmentSet(tuple(Commitment(f't{i}', f.canonical(), f'placeholder:{i}', f) for i, f in enumerate(formulas)))


def engine(t, cuts=None, seed=0, answered=True, **config):
    ports = Scripted(cuts, answered)
    return Engine(load_bank('bank'), t, ports, ports, ports, ports, ports, ports,
                  EngineConfig(seed=seed, **config)), ports


def mp():
    return proposal('modus_ponens', Q, conditional=Formula('implies', (P, Q)), antecedent=P)


def test_all_leaves_required():
    pq = Formula('implies', (P, Q))
    closed, _ = engine(table(P, pq), {Q.canonical(): (mp(),)})
    route = closed.search(prop(Q)).routes[0]
    assert route.status == 'CLOSED'
    assert not route.frontier
    assert all(closed.commitments.get(n.t_id) for n in route.nodes if n.kind == 'leaf')
    opened, _ = engine(table(pq), {Q.canonical(): (mp(),)})
    route = opened.search(prop(Q)).routes[0]
    assert route.status == 'OPEN'
    assert [n.proposition.formula for n in route.nodes if n.id in route.frontier] == [P]


def test_terminus_rejects_forged_id_and_formula():
    cut = mp()
    cut = replace(cut, premises=tuple(replace(p, t_id='absent') for p in cut.premises))
    e, _ = engine(table(P, Formula('implies', (P, Q))), {Q.canonical(): (cut,)})
    assert e.search(prop(Q)).routes[0].status == 'OPEN'
    cut = replace(cut, premises=tuple(replace(p, t_id='t0') for p in cut.premises))
    e, _ = engine(table(P), {Q.canonical(): (cut,)})
    assert e.search(prop(Q)).routes[0].status == 'OPEN'


def test_unanswered_cq_keeps_route_open():
    cut = proposal('sign', Q, sign_relation=P, observed_sign=R)
    for answered, status in [(False, 'OPEN'), (True, 'CLOSED')]:
        e, _ = engine(table(P, R), {Q.canonical(): (cut,)}, answered=answered)
        route = e.search(prop(Q)).routes[0]
        assert route.status == status
        assert bool(route.frontier) == (not answered)


def test_cq_support_must_exist():
    cut = proposal('sign', Q, sign_relation=P, observed_sign=R)
    e, ports = engine(table(P, R), {Q.canonical(): (cut,)})
    ports.answer_cq = lambda q, p, t: CQAnswer(q.id, 'P', True, ('absent',))
    assert e.search(prop(Q)).routes[0].status == 'OPEN'


def test_negation_search_and_replay():
    cuts = {Q.canonical(): (mp(),)}
    first, ports = engine(table(P, Formula('implies', (P, Q))), cuts)
    second, _ = engine(first.commitments, cuts)
    a, b = first.analyse(prop(Q)), second.analyse(prop(Q))
    assert Q.negated().canonical() in ports.goals
    assert a.negated.target.formula == Q.negated()
    assert a.target.routes[0].status == 'CLOSED'
    assert a.negated.routes[0].status == 'OPEN'
    assert a.to_json() == b.to_json()


def test_seed_changes_equal_cost_order_and_replays():
    cuts = {Q.canonical(): (proposal('sign', Q, sign_relation=P, observed_sign=P),
                            proposal('sign', Q, sign_relation=R, observed_sign=R))}
    outputs = []
    for seed in (0, 0, 4):
        e, _ = engine(table(P, R), cuts, seed=seed)
        outputs.append(e.search(prop(Q)).to_json())
    assert outputs[0] == outputs[1]
    assert outputs[0] != outputs[2]


def test_negated_leaf_has_infinite_cost():
    e, _ = engine(table(P.negated()))
    result = e.search(prop(P))
    assert result.routes[0].dialectical_cost is None
    assert result.routes[0].status == 'OPEN'
    assert any(ev.decision and ev.decision.reason_code == 'OPPOSED_COMMITMENT' for ev in e.sink.events)


def test_caps_bound_cyclic_search():
    cut = proposal('sign', P, sign_relation=P, observed_sign=Q)
    e, ports = engine(table(Q), {P.canonical(): (cut,)}, node_cap=4, depth_cap=2)
    result = e.search(prop(P))
    assert all(r.status == 'OPEN' for r in result.routes)
    assert result.nodes_created <= 4
    assert len(ports.goals) <= 2


def test_independent_routes_use_canonical_leaves():
    cuts = {Q.canonical(): (proposal('sign', Q, sign_relation=P, observed_sign=P),
                            proposal('sign', Q, sign_relation=R, observed_sign=R),
                            proposal('sign', Q, sign_relation=P, observed_sign=R))}
    e, _ = engine(table(P, R), cuts)
    # CQ support is counted as a premise too; give each route its own leaf support.
    e.cq_answerer.answer_cq = lambda q, p, t: CQAnswer(q.id, 'P', True, (
        't0' if p.premises[0].text == P.canonical() else 't1',))
    result = e.search(prop(Q))
    assert len(result.routes) == 3
    assert result.independent_closed_routes == 2


def test_conditional_scope_closes_without_turning_assumption_into_commitment():
    pp = Formula('implies', (P, P))
    cut = Proposal('conditional_proof', (PremiseFill('assumption', P.canonical(), scope_id='conditional'),
                    PremiseFill('result', P.canonical(), scope_id='conditional')), pp.canonical())
    e, _ = engine(table(), {pp.canonical(): (cut,)})
    route = e.search(prop(pp)).routes[0]
    assert route.status == 'CLOSED'
    assert len(route.scopes) == 1
    assert all(n.t_id == 'open' for n in route.nodes)
    assert any(n.kind == 'assumption' for n in route.nodes)


def test_conditional_unproved_result_stays_open():
    pq = Formula('implies', (P, Q))
    cut = Proposal('conditional_proof', (PremiseFill('assumption', P.canonical(), scope_id='conditional'),
                    PremiseFill('result', Q.canonical(), scope_id='conditional')), pq.canonical())
    e, _ = engine(table(), {pq.canonical(): (cut,)})
    route = e.search(prop(pq)).routes[0]
    assert route.status == 'OPEN'
    assert [n.proposition.formula for n in route.nodes if n.id in route.frontier] == [Q]


def test_best_first_prefers_closed_cheaper_alternative():
    cut1 = proposal('sign', Q, sign_relation=P, observed_sign=R)
    cut2 = proposal('sign', Q, sign_relation=P, observed_sign=P)
    e, ports = engine(table(P), {Q.canonical(): (cut1, cut2)})
    routes = e.search(prop(Q)).routes
    assert [r.status for r in routes] == ['CLOSED', 'OPEN']
    assert [r.dialectical_cost for r in routes] == [1.0, 2.0]


def test_node_and_depth_caps_report_truncation():
    for config in ({'node_cap': 2}, {'depth_cap': 0}):
        e, _ = engine(table(P, Formula('implies', (P, Q))), {Q.canonical(): (mp(),)}, **config)
        result = e.search(prop(Q))
        assert result.truncated
        assert result.routes[0].status == 'OPEN'
        assert result.nodes_created == 1


def test_reductio_scoped_results_and_external_dependencies():
    pp = Formula('implies', (P, Q))
    cut = Proposal('reductio_ad_absurdum', (
        PremiseFill('assumption', P.canonical(), scope_id='reductio'),
        PremiseFill('positive_result', Q.canonical(), scope_id='reductio'),
        PremiseFill('negative_result', Q.negated().canonical(), scope_id='reductio'),
    ), P.negated().canonical())
    cuts = {P.negated().canonical(): (cut,), Q.canonical(): (mp(),)}
    e, _ = engine(table(pp, Q.negated()), cuts)
    route = e.search(prop(P.negated())).routes[0]
    assert route.status == 'CLOSED'
    assert len(route.scopes) == 1
    assert all(e.commitments.get(n.t_id) for n in route.nodes if n.kind == 'leaf')
    assert {n.proposition.formula.canonical() for n in route.nodes if n.kind == 'assumption'} == {P.canonical()}


def test_sibling_cannot_use_discharged_assumption():
    pp = Formula('implies', (P, P))
    root = Formula('and', (P, pp))
    cp = Proposal('conditional_proof', (PremiseFill('assumption', P.canonical(), scope_id='conditional'),
                    PremiseFill('result', P.canonical(), scope_id='conditional')), pp.canonical())
    cut = proposal('conjunction_introduction', root, left=pp, right=P)
    e, _ = engine(table(), {root.canonical(): (cut,), pp.canonical(): (cp,)})
    route = e.search(prop(root)).routes[0]
    assert route.status == 'OPEN'
    assert [n.proposition.formula for n in route.nodes if n.id in route.frontier] == [P]


def test_port_rejection_propagates():
    import pytest
    e, ports = engine(table())
    def reject(*args):
        raise RuntimeError('rejected')
    ports.propose_cuts = reject
    with pytest.raises(RuntimeError, match='rejected'):
        e.search(prop(Q))


def test_config_uses_solver_timeout_from_runtime_mapping():
    config = EngineConfig.from_mapping({'solver_timeout_ms': 17, 'seed': 4, 'provider': 'mock'})
    e, _ = engine(table(), solver_timeout_ms=config.solver_timeout_ms)
    assert e.licenser.timeout_ms == 17
