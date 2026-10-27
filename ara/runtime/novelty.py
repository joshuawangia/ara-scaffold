"""Bounded Boolean dependence of a proposed assertion on frozen commitments."""
from dataclasses import replace

from ara.runtime.contribution import cached_entails, formula_hash
from ara.types import Formula


def _world(formula, side):
    """Independent interpretations, preserving sharing and binders within each world."""
    prefix = 'novelty:' + side + ':'
    return replace(formula, args=tuple(_world(a, side) for a in formula.args),
                   name=prefix + formula.name if formula.name is not None else None,
                   terms=tuple(replace(t, name=prefix + t.name) for t in formula.terms),
                   variable=prefix + formula.variable if formula.variable is not None else None)


def main_claim(formula):
    if formula.op == 'implies':
        return main_claim(formula.args[1])
    if formula.op in ('forall', 'exists'):
        return replace(formula, args=(main_claim(formula.args[0]),))
    return formula


def atomic_claims(formula):
    if formula.op in ('atom', 'predicate'):
        yield formula
    for child in formula.args:
        yield from atomic_claims(child)


def novelty_check(formula, commitments):
    """Equal T truth values must permit different target truth values to pass.

    No commitment is assumed true here: doing so would exclude deductions from
    multiple commitments. UNSAT proves Boolean definability over the finite T
    truth vector, including equivalent disguises and vacuous new atoms.
    """
    basis_ids = [c.id for c in commitments.commitments]
    constraints = tuple(Formula('iff', (_world(c.formula, 'left'), _world(c.formula, 'right')))
                        for c in commitments.commitments)
    main = main_claim(formula)
    scopes = [('target', formula)]
    if main != formula:
        scopes.append(('main_claim', main))
    checks = []
    for scope, claim in scopes:
        equality = Formula('iff', (_world(claim, 'left'), _world(claim, 'right')))
        result = cached_entails(constraints, equality, 1000)
        checks.append(dict(scope=scope, solver_result=result, timeout_ms=1000))
        if result != 'SOLVER_COUNTEREXAMPLE':
            return dict(status='rejected' if result == 'SOLVER_UNSAT' else 'unresolved',
                        reason='boolean_recombination' if result == 'SOLVER_UNSAT' else 'novelty_unresolved',
                        scope=scope, solver_result=result, checks=checks, basis_commitment_ids=basis_ids,
                        main_claim=main.to_dict(), explanation=(
                            'The ' + scope + ' is fully determined by Boolean combinations of existing T formulas; '
                            'rephrasing connectives or adding a vacuous atom does not add a new assertion.'
                            if result == 'SOLVER_UNSAT' else
                            'Bounded equivalence checking could not establish a new main assertion.'))
    existing = {formula_hash(c.formula) for c in commitments.commitments}
    new_claims = {formula_hash(a):a for a in atomic_claims(main) if formula_hash(a) not in existing}
    if not new_claims:
        return dict(status='rejected', reason='no_new_main_proposition', scope='main_claim', checks=checks,
                    basis_commitment_ids=basis_ids, main_claim=main.to_dict(),
                    explanation='The main claim has no atom or predicate application not already asserted in T; antecedent-only novelty does not count.')
    return dict(status='candidate', reason='new_main_assertion', checks=checks,
                basis_commitment_ids=basis_ids, main_claim=main.to_dict(),
                new_main_propositions=[a.to_dict() for a in new_claims.values()])
