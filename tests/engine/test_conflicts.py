from ara.engine.forward import forward_pass
from ara.types import Formula
from test_licensing import P, Q, R, prop, proposal
from test_search import engine, table


def test_forward_depth_and_flag():
    pq, qr = Formula('implies', (P, Q)), Formula('implies', (Q, R))
    e, _ = engine(table(P, pq, qr, R.negated()))
    first = forward_pass((P, pq, qr), e.commitments, e.licenser, depth=1, node_cap=100)
    second = forward_pass((P, pq, qr), e.commitments, e.licenser, depth=2, node_cap=100)
    assert Q.canonical() in {c.formula.canonical() for c in first.consequences}
    assert R.canonical() not in {c.formula.canonical() for c in first.consequences}
    assert any(c.formula == R and c.flagged and c.depth == 2 for c in second.consequences)


def test_tier1_marks_same_premises_and_requests_repair():
    cuts = {Q.canonical(): (proposal('sign', Q, sign_relation=P, observed_sign=R),),
            Q.negated().canonical(): (proposal('sign', Q.negated(), sign_relation=P, observed_sign=R),)}
    e, ports = engine(table(P, R), cuts, forward_pass_depth=1)
    result = e.analyse(prop(Q))
    assert len(result.tier1) == 1
    conflict = result.tier1[0]
    assert set(conflict.premise_forms) == {P.canonical(), R.canonical()}
    assert {p.formula.canonical() for p in conflict.conclusions} == {Q.canonical(), Q.negated().canonical()}
    assert conflict.repair.action == 'unresolved'
    assert len(ports.repairs) == 1
    assert any(ev.decision.reason_code == 'TIER1_CONFLICT' for ev in ports.events)


def test_tier2_records_first_flagged_consequence():
    pq = Formula('implies', (P, Q))
    cuts = {Q.canonical(): (proposal('modus_ponens', Q, conditional=pq, antecedent=P),)}
    e, _ = engine(table(P, pq, Q.negated()), cuts, forward_pass_depth=1)
    result = e.analyse(prop(Q))
    assert result.target.routes[0].status == result.negated.routes[0].status == 'CLOSED'
    assert len(result.tier2) == 1
    conflict = result.tier2[0]
    assert conflict.first_flagged.formula == Q
    assert conflict.first_flagged.flagged
    assert len(result.forward) == 2
    assert {f.route_id for f in result.forward} == {conflict.positive_route_id, conflict.negative_route_id}


def test_invalid_proposals_never_trigger_conflicts():
    cuts = {Q.canonical(): (proposal('absent', Q, sign_relation=P, observed_sign=R),),
            Q.negated().canonical(): (proposal('sign', Q.negated(), sign_relation=P, observed_sign=R),)}
    e, ports = engine(table(P, R), cuts, forward_pass_depth=0)
    result = e.analyse(prop(Q))
    assert result.tier1 == result.tier2 == ()
    assert ports.repairs == []


def test_forward_replays_textual_steps_at_their_actual_depth():
    from dataclasses import replace
    from ara.types import PremiseFill, Proposal
    cuts = {Q.canonical(): (Proposal('sign', (PremiseFill('sign_relation', 'P'), PremiseFill('observed_sign', 'P')), 'Q'),),
            R.canonical(): (Proposal('sign', (PremiseFill('sign_relation', 'Q'), PremiseFill('observed_sign', 'P')), 'R'),)}
    e, ports = engine(table(P), cuts, forward_pass_depth=1)
    ports.formalise = lambda p: p.formula or {'P': P, 'Q': Q, 'R': R}[p.text]
    result = e.analyse(prop(R))
    route = result.target.routes[0]
    assert route.status == 'CLOSED'
    derived = {c.formula.canonical() for c in result.forward[0].consequences}
    assert Q.canonical() in derived
    assert R.canonical() not in derived
    deeper = forward_pass((P,), e.commitments, e.licenser, 2, witnesses=(route,))
    assert any(c.formula == R and c.depth == 2 for c in deeper.consequences)


def test_forward_cap_is_explicit():
    e, ports = engine(table(P, Q))
    result = forward_pass((P, Q), e.commitments, e.licenser, 2, node_cap=1)
    assert result.truncated
    assert len(result.consequences) == 1
    assert any(ev.decision.reason_code == 'FORWARD_CAP' for ev in ports.events)


def test_forward_quantifier_instances():
    from ara.types import Term
    fx = Formula('predicate', name='P', terms=(Term('variable', 'x'),))
    fa = Formula('predicate', name='P', terms=(Term('constant', 'a'),))
    universal = Formula('forall', (fx,), variable='x')
    e, _ = engine(table(universal))
    result = forward_pass((universal,), e.commitments, e.licenser, 1, node_cap=100)
    assert any(c.formula == fa and c.bank_id == 'universal_instantiation' for c in result.consequences)


def test_analysis_roundtrip():
    from ara.engine.conflicts import AnalysisResult
    e, _ = engine(table(P), forward_pass_depth=0)
    result = e.analyse(prop(P))
    assert AnalysisResult.from_json(result.to_json()) == result


def test_tier1_deductive_premise_set():
    both = Formula('and', (P, P.negated()))
    cuts = {f.canonical(): (proposal('conjunction_elimination', f, conjunction=both),)
            for f in (P, P.negated())}
    e, ports = engine(table(both), cuts, forward_pass_depth=0)
    result = e.analyse(prop(P))
    assert len(result.tier1) == 1
    assert result.tier1[0].premise_forms == (both.canonical(),)
    assert len(ports.repairs) == 1


def test_forward_does_not_leak_scoped_assumptions():
    from ara.types import PremiseFill, Proposal
    pp = Formula('implies', (P, P))
    cut = Proposal('conditional_proof', (PremiseFill('assumption', P.canonical(), scope_id='conditional'),
                    PremiseFill('result', P.canonical(), scope_id='conditional')), pp.canonical())
    e, _ = engine(table(), {pp.canonical(): (cut,)}, forward_pass_depth=1)
    result = e.analyse(prop(pp))
    consequences = result.forward[0].consequences
    assert any(c.formula == pp for c in consequences)
    assert not any(c.formula == P for c in consequences)


def test_tier1_includes_forward_licenses():
    both = Formula('and', (P, P.negated()))
    e, ports = engine(table(both), forward_pass_depth=1)
    result = e.analyse(prop(both))
    assert any(c.premise_forms == (both.canonical(),) and
               {p.formula.canonical() for p in c.conclusions} == {P.canonical(), P.negated().canonical()}
               for c in result.tier1)
    assert ports.repairs
