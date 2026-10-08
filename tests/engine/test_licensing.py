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
