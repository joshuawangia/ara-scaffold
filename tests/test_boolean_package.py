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


def test_boolean_z3_objects_are_released_under_the_solver_lock(monkeypatch):
    import weakref
    import ara.formal as formal
    released = []
    compiler, solver = formal.Compiler, formal.z3.Solver
    def tracked(factory, kind):
        def create(*args, **kwargs):
            value = factory(*args, **kwargs)
            weakref.finalize(value, lambda: released.append((kind, formal._SOLVER_LOCK._is_owned())))
            return value
        return create
    monkeypatch.setattr(formal, 'Compiler', tracked(compiler, 'compiler'))
    monkeypatch.setattr(formal.z3, 'Solver', tracked(solver, 'solver'))
    assert formal.boolean_combination_equivalence((P,), Q) == 'SOLVER_COUNTEREXAMPLE'
    assert sorted(kind for kind, held in released) == ['compiler', 'compiler', 'solver']
    assert all(held for kind, held in released), released
