"""Unconstrained Boolean dependence must not collapse into entailment."""
import pytest
from ara.formal import boolean_combination_equivalence
from ara.types import Formula, Term

P, Q, R = (Formula('atom', name=n) for n in ('P', 'Q', 'R'))


def test_equivalent_connective_package_and_cross_paper_deduction_differ():
    conditional = Formula('implies', (Q, R))
    equivalent = Formula('and', (P, Formula('or', (Q.negated(), R))))
    assert boolean_combination_equivalence((P, conditional), equivalent) == 'SOLVER_UNSAT'
    assert boolean_combination_equivalence((P, Formula('implies', (P, Q))), Q) == 'SOLVER_COUNTEREXAMPLE'


def test_independent_quantified_interpretations_keep_real_quantifiers():
    x = Term('variable', 'x')
    body = Formula('predicate', name='F', terms=(x,))
    universal, existential = (Formula(op, (body,), variable='x') for op in ('forall', 'exists'))
    assert boolean_combination_equivalence((universal,), existential) == 'SOLVER_COUNTEREXAMPLE'
    assert boolean_combination_equivalence((universal,), universal) == 'SOLVER_UNSAT'


def test_boolean_package_requires_a_positive_solver_bound():
    with pytest.raises(ValueError, match='positive'):
        boolean_combination_equivalence((P,), Q, 0)
