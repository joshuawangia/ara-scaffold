"""Semantic novelty relative to all frozen T, with bounded cached solver receipts."""
from dataclasses import replace
from ara.runtime.cache import canonical
from ara.runtime.contribution import cached_entails
from ara.types import Formula


def application_key(formula, bound=()):
    # Local bound-variable identity ignores unused surrounding binders while
    # preserving repeated-versus-distinct variables and free/constant identity.
    variables = {}
    terms = []
    for term in formula.terms:
        if term.kind == 'variable' and term.name in bound:
            identity = ('bound', variables.setdefault(term.name, len(variables)))
        else:
            identity = ('free', term.name)
        terms.append((term.kind, identity))
    return canonical([formula.op, formula.name, terms])


def atomic_applications(formula, bound=()):
    if formula.op in ('atom', 'predicate'):
        yield application_key(formula, bound), formula
    nested = bound + (formula.variable,) if formula.op in ('forall', 'exists') else bound
    for child in formula.args:
        yield from atomic_applications(child, nested)


def cofactor(formula, key, truth, bound=()):
    if formula.op in ('atom', 'predicate') and application_key(formula, bound) == key:
        # The shared AST has no truth constants. These are exactly top/bottom.
        return Formula('or' if truth else 'and', (formula, formula.negated()))
    nested = bound + (formula.variable,) if formula.op in ('forall', 'exists') else bound
    return replace(formula, args=tuple(cofactor(a, key, truth, nested) for a in formula.args))


def novelty_check(formula, commitments):
    premises = tuple(c.formula for c in commitments.commitments)
    checks = []
    base = dict(basis_commitment_ids=[c.id for c in commitments.commitments], checks=checks)
    result = cached_entails(premises, formula, 1000)
    checks.append(dict(scope='deductive_closure', solver_result=result, timeout_ms=1000))
    if result == 'SOLVER_UNSAT':
        return dict(**base, status='rejected', reason='deductive_closure', solver_result=result,
                    explanation='All of frozen T classically entails this target. Connective or quantifier wrappers do not create a new assertion.')
    if result != 'SOLVER_COUNTEREXAMPLE':
        return dict(**base, status='unresolved', reason='novelty_unresolved',
                    explanation='Bounded deductive-closure checking did not establish novelty.')
    existing = {key for c in commitments.commitments for key, _ in atomic_applications(c.formula)}
    candidates = {key:atom for key, atom in atomic_applications(formula) if key not in existing}
    essential = []
    for key, atom in candidates.items():
        changed = False
        for truth in (True, False):
            result = cached_entails(premises, Formula('iff', (formula, cofactor(formula, key, truth))), 1000)
            checks.append(dict(scope='essential_atom', application_key=key, substituted_truth=truth,
                               solver_result=result, timeout_ms=1000))
            if result not in ('SOLVER_UNSAT', 'SOLVER_COUNTEREXAMPLE'):
                return dict(**base, status='unresolved', reason='novelty_unresolved',
                            explanation='Bounded essential-atom checking was unresolved; novelty cannot be admitted.')
            changed |= result == 'SOLVER_COUNTEREXAMPLE'
        if changed:
            essential.append((key, atom))
    if not essential:
        return dict(**base, status='rejected', reason='no_essential_new_proposition',
                    explanation='No new atomic application changes the target truth under T when replaced by true or false; vacuous or renamed bound variables do not count.')
    return dict(**base, status='candidate', reason='essential_new_assertion',
                essential_application_keys=[key for key, _ in essential],
                essential_new_propositions=[atom.to_dict() for _, atom in essential])
