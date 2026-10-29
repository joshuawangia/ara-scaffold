"""Formula compilation and timeout-bounded entailment; no runtime dependencies."""
from __future__ import annotations

import z3
from threading import RLock

_SOLVER_LOCK = RLock()

from ara.types import Formula


class Compiler:
    """One vocabulary per sequent, with disjoint atom/predicate/term namespaces."""

    def __init__(self, namespace: str = '') -> None:
        self.namespace = namespace
        self.sort = z3.DeclareSort(namespace + 'ara:individual')
        self.predicates: dict[tuple[str, int], z3.FuncDeclRef] = {}

    def compile(self, formula: Formula, bound: dict | None = None) -> z3.BoolRef:
        bound = {} if bound is None else bound
        op = formula.op
        if op == 'atom':
            return z3.Bool(self.namespace + 'atom:' + formula.name)
        if op == 'predicate':
            key = (formula.name, len(formula.terms))
            if key not in self.predicates:
                self.predicates[key] = z3.Function(
                    self.namespace + f'predicate:{key[0]}:{key[1]}', *([self.sort] * key[1]), z3.BoolSort())
            args = [bound[t.name] if t.kind == 'variable' and t.name in bound
                    else z3.Const(self.namespace + f'{t.kind}:{t.name}', self.sort) for t in formula.terms]
            return self.predicates[key](*args)
        if op in ('forall', 'exists'):
            variable = z3.Const(self.namespace + f'bound:{formula.variable}:{len(bound)}', self.sort)
            body = self.compile(formula.args[0], {**bound, formula.variable: variable})
            return (z3.ForAll if op == 'forall' else z3.Exists)([variable], body)
        args = [self.compile(f, bound) for f in formula.args]
        return {'not': lambda: z3.Not(args[0]), 'and': lambda: z3.And(*args),
                'or': lambda: z3.Or(*args), 'implies': lambda: z3.Implies(*args),
                'iff': lambda: args[0] == args[1]}[op]()


def entails(premises: tuple[Formula, ...], conclusion: Formula, timeout_ms: int) -> str:
    if timeout_ms <= 0:
        raise ValueError('solver timeout must be positive')
    # Z3 objects in the default context must stay inside this critical section.
    with _SOLVER_LOCK:
        return _entails(premises, conclusion, timeout_ms)


def _entails(premises, conclusion, timeout_ms):
    compiler, solver = Compiler(), z3.Solver()
    solver.set(timeout=timeout_ms)
    solver.add(*(compiler.compile(f) for f in premises))
    solver.add(z3.Not(compiler.compile(conclusion)))
    return _solver_result(solver)


def boolean_combination_equivalence(basis: tuple[Formula, ...], target: Formula, timeout_ms: int = 1000) -> str:
    """UNSAT iff target is a Boolean function of the basis's truth values.

    Two independent interpretations may agree on every basis formula while
    disagreeing on the target exactly when no such Boolean combination exists.
    Basis formulas are not asserted as premises: that would reject deductions.
    """
    if timeout_ms <= 0:
        raise ValueError('solver timeout must be positive')
    with _SOLVER_LOCK:
        left, right, solver = Compiler('left:'), Compiler('right:'), z3.Solver()
        solver.set(timeout=timeout_ms)
        solver.add(*(left.compile(f) == right.compile(f) for f in basis))
        solver.add(left.compile(target) != right.compile(target))
        return _solver_result(solver)


def _solver_result(solver):
    result = solver.check()
    if result == z3.unsat:
        return 'SOLVER_UNSAT'
    if result == z3.sat:
        return 'SOLVER_COUNTEREXAMPLE'
    return 'SOLVER_TIMEOUT' if 'timeout' in solver.reason_unknown().lower() else 'SOLVER_UNKNOWN'
