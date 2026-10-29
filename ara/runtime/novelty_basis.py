"""Consistent novelty bases and bounded, interpretation-independent packaging checks."""
from dataclasses import replace
from functools import lru_cache

from ara.formal import boolean_combination_equivalence
from ara.runtime.contribution import cached_entails
from ara.types import Formula

_P = Formula('atom', name='P')
_FALSE = Formula('and', (_P, _P.negated()))


def admissible_commitments(commitments, provenance):
    rows = provenance['commitments'] if provenance else None
    return tuple(sorted((c for c in commitments.commitments if rows is None or
        rows.get(c.id, {}).get('stance') in ('endorsed', 'model_alignment')), key=lambda c: c.id))


def support_consistency(commitments, support_ids):
    ids = sorted(set(support_ids))
    members = tuple(commitments.get(tid) for tid in ids)
    if any(c is None for c in members):
        return dict(status='unresolved', reason='missing_support', commitment_ids=ids, solver_result='NOT_CHECKED')
    verdict = cached_entails(tuple(c.formula for c in members), _FALSE, 1000)
    return dict(status={'SOLVER_COUNTEREXAMPLE': 'consistent', 'SOLVER_UNSAT': 'conflict'}.get(verdict, 'unresolved'),
                commitment_ids=ids, solver_result=verdict, timeout_ms=1000)


def consistent_basis(commitments, provenance, required_ids=(), *, exact=False):
    """ID-ordered greedy maximal consistent extension, never maximum or unique."""
    inventory = admissible_commitments(commitments, provenance)
    required = sorted(set(required_ids))
    selected = [c for c in inventory if c.id in required]
    checks, omitted = [], []
    receipt = dict(mode='exact_support' if exact else 'deterministic_maximal_consistent_subset',
        required_commitment_ids=required, selected_commitment_ids=[c.id for c in selected],
        omitted_commitment_ids=omitted, checks=checks, order='commitment_id', maximal=False)
    if len(selected) != len(required):
        return dict(**receipt, status='unresolved', reason='invalid_basis_commitments')
    def check(members):
        value = support_consistency(commitments, [c.id for c in members])
        checks.append(value)
        return value['status']
    verdict = check(selected)
    if verdict != 'consistent':
        return dict(**receipt, status=verdict, reason='inconsistent_basis' if verdict == 'conflict' else 'novelty_unresolved')
    if not exact:
        for c in inventory:
            if c.id in required:
                continue
            verdict = check((*selected, c))
            if verdict == 'consistent':
                selected.append(c)
            elif verdict == 'conflict':
                omitted.append(c.id)
            else:
                receipt['selected_commitment_ids'] = sorted(c.id for c in selected)
                return dict(**receipt, status='unresolved', reason='novelty_unresolved')
        receipt['maximal'] = True
    receipt['selected_commitment_ids'] = sorted(c.id for c in selected)
    return dict(**receipt, status='consistent', reason='satisfiable_basis')


def free_variables(formula):
    names = {t.name for t in formula.terms if t.kind == 'variable'}
    names.update(v for child in formula.args for v in free_variables(child))
    if formula.op in ('forall', 'exists'):
        names.discard(formula.variable)
    return names


def drop_vacuous_quantifiers(formula):
    formula = replace(formula, args=tuple(drop_vacuous_quantifiers(a) for a in formula.args))
    if formula.op in ('forall', 'exists') and formula.variable not in free_variables(formula.args[0]):
        return formula.args[0]
    return formula


@lru_cache(maxsize=8192)
def _package_equivalence(basis, target):
    return boolean_combination_equivalence(basis, target, 1000)


def boolean_package(formula, basis):
    target = drop_vacuous_quantifiers(formula)
    normalized = tuple(drop_vacuous_quantifiers(c.formula) for c in basis)
    verdict = _package_equivalence(normalized, target)
    return dict(method='two_independent_interpretations', basis_commitment_ids=[c.id for c in basis],
                normalized_target=target.to_dict(), solver_result=verdict, timeout_ms=1000)
