from dataclasses import replace

import pytest

from ara.bank import load_bank
from ara.engine.licensing import Licenser
from ara.formal import entails
from ara.types import Commitment, CommitmentSet, Formula, PremiseFill, Proposal, Proposition, Term

P, Q, R = (Formula('atom', name=n) for n in ('P', 'Q', 'R'))


def prop(f):
    return Proposition(f.canonical(), f.canonical(), f)


def proposal(bank_id, conclusion, **slots):
    return Proposal(bank_id, tuple(PremiseFill(k, f.canonical()) for k, f in slots.items()), conclusion.canonical())


class Ports:
    def __init__(self):
        self.events = []

    def formalise(self, p):
        return p.formula or Formula.from_json(p.text)

    def emit(self, e):
        self.events.append(e)


@pytest.fixture
def licenser():
    ports = Ports()
    return Licenser(load_bank('bank'), ports, ports, 1000)


def test_solver_rejects_affirming_consequent(licenser):
    cut = proposal('modus_ponens', P, conditional=Formula('implies', (P, Q)), antecedent=Q)
    result = licenser.check(cut, prop(P))
    assert not result.licensed
    assert result.decision.reason_code == 'SOLVER_COUNTEREXAMPLE'
    assert licenser.sink.events[-1].decision == result.decision


@pytest.mark.parametrize('case,reason', [('bank', 'UNKNOWN_BANK_ID'), ('slot', 'SLOT_MISMATCH'), ('goal', 'CONCLUSION_MISMATCH')])
def test_unlicensed_rejected(licenser, case, reason):
    cut = proposal('modus_ponens', Q, conditional=Formula('implies', (P, Q)), antecedent=P)
    if case == 'bank': cut = replace(cut, bank_id='absent')
    if case == 'slot': cut = replace(cut, premises=cut.premises[:1])
    if case == 'goal': cut = replace(cut, conclusion_text=R.canonical())
    result = licenser.check(cut, prop(Q))
    assert not result.licensed
    assert result.decision.reason_code == reason


def test_shape_required_even_when_entailment_holds(licenser):
    cut = proposal('modus_ponens', Q, conditional=Q, antecedent=P)
    assert licenser.check(cut, prop(Q)).decision.reason_code == 'SCHEMA_MISMATCH'


def test_valid_deduction(licenser):
    cut = proposal('modus_ponens', Q, conditional=Formula('implies', (P, Q)), antecedent=P)
    assert licenser.check(cut, prop(Q)).licensed


def test_quantifier_compilation_and_substitution(licenser):
    fx = Formula('predicate', name='P', terms=(Term('variable', 'x'),))
    fa = Formula('predicate', name='P', terms=(Term('constant', 'a'),))
    universal = Formula('forall', (fx,), variable='x')
    existential = Formula('exists', (fx,), variable='x')
    assert entails((universal,), fa, 1000) == 'SOLVER_UNSAT'
    assert licenser.check(proposal('universal_instantiation', fa, universal=universal), prop(fa)).licensed
    assert licenser.check(proposal('existential_generalisation', existential, instance=fa), prop(existential)).licensed


def test_compiler_symbol_namespaces():
    atom = Formula('atom', name='P')
    pred = Formula('predicate', name='P')
    assert entails((atom,), pred, 1000) == 'SOLVER_COUNTEREXAMPLE'
    assert entails((Formula('iff', (P, Q)), P), Q, 1000) == 'SOLVER_UNSAT'


@pytest.mark.parametrize('status,reason', [('unknown', 'SOLVER_UNKNOWN'), ('timeout', 'SOLVER_TIMEOUT')])
def test_solver_unknown_and_timeout_are_discards(licenser, monkeypatch, status, reason):
    import z3
    from ara import formal
    class UnknownSolver:
        def set(self, **kwargs):
            assert kwargs['timeout'] == 1000
        def add(self, *args):
            pass
        def check(self):
            return z3.unknown
        def reason_unknown(self):
            return status
    monkeypatch.setattr(formal.z3, 'Solver', UnknownSolver)
    cut = proposal('modus_ponens', Q, conditional=Formula('implies', (P, Q)), antecedent=P)
    result = licenser.check(cut, prop(Q))
    assert not result.licensed
    assert result.decision.reason_code == reason


@pytest.mark.parametrize('bank_id,conclusion,fills', [
    ('modus_tollens', P.negated(), {'conditional': Formula('implies', (P, Q)), 'negated_consequent': Q.negated()}),
    ('hypothetical_syllogism', Formula('implies', (P, R)), {'first': Formula('implies', (P, Q)), 'second': Formula('implies', (Q, R))}),
    ('disjunctive_syllogism', P, {'disjunction': Formula('or', (P, Q)), 'negated_disjunct': Q.negated()}),
    ('conjunction_introduction', Formula('and', (P, Q)), {'left': Q, 'right': P}),
    ('conjunction_elimination', R, {'conjunction': Formula('and', (P, Q, R))}),
    ('disjunction_introduction', Formula('or', (P, Q)), {'disjunct': Q}),
    ('double_negation', P, {'double_negated': Formula('not', (Formula('not', (P,)),))}),
    ('constructive_dilemma', Formula('or', (Q, R)), {'first': Formula('implies', (P, Q)), 'second': Formula('implies', (Q, R)), 'disjunction': Formula('or', (P, Q))}),
])
def test_other_deductive_bank_forms(licenser, bank_id, conclusion, fills):
    assert licenser.check(proposal(bank_id, conclusion, **fills), prop(conclusion)).licensed


def test_schema_rejects_noninstance_even_if_quantifier_entails(licenser):
    fx = Formula('predicate', name='P', terms=(Term('variable', 'x'),))
    fa = Formula('predicate', name='P', terms=(Term('constant', 'a'),))
    fb = Formula('predicate', name='P', terms=(Term('constant', 'b'),))
    universal = Formula('forall', (fx,), variable='x')
    conclusion = Formula('and', (fa, fb))
    result = licenser.check(proposal('universal_instantiation', conclusion, universal=universal), prop(conclusion))
    assert result.decision.reason_code == 'SCHEMA_MISMATCH'


def test_substitution_avoids_capture():
    from ara.engine.matching import substitute
    body = Formula('forall', (Formula('predicate', name='P', terms=(Term('variable', 'x'), Term('variable', 'y'))),), variable='y')
    result = substitute(body, 'x', Term('variable', 'y'))
    assert result.variable != 'y'
    assert result.args[0].terms == (Term('variable', 'y'), Term('variable', result.variable))


def test_scope_annotations_cannot_escape(licenser):
    cut = proposal('modus_ponens', Q, conditional=Formula('implies', (P, Q)), antecedent=P)
    cut = replace(cut, premises=tuple(replace(p, scope_id='conditional') for p in cut.premises))
    assert licenser.check(cut, prop(Q)).decision.reason_code == 'INVALID_SCOPE'


def test_assumption_cannot_be_a_t_leaf(licenser):
    pp = Formula('implies', (P, P))
    cut = Proposal('conditional_proof', (PremiseFill('assumption', P.canonical(), 't0', 'conditional'),
                    PremiseFill('result', P.canonical(), scope_id='conditional')), pp.canonical())
    assert licenser.check(cut, prop(pp)).decision.reason_code == 'INVALID_SCOPE'
