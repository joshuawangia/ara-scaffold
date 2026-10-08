"""Formula compilation and timeout-bounded entailment; no runtime dependencies."""
from __future__ import annotations

import z3

from ara.types import Formula


class Compiler:
    """One vocabulary per sequent, with disjoint atom/predicate/term namespaces."""

    def __init__(self) -> None:
        self.sort = z3.DeclareSort('ara:individual')
        self.predicates: dict[tuple[str, int], z3.FuncDeclRef] = {}

    def compile(self, formula: Formula, bound: dict | None = None) -> z3.BoolRef:
        bound = {} if bound is None else bound
        op = formula.op
        if op == 'atom':
            return z3.Bool('atom:' + formula.name)
        if op == 'predicate':
            key = (formula.name, len(formula.terms))
            if key not in self.predicates:
                self.predicates[key] = z3.Function(
                    f'predicate:{key[0]}:{key[1]}', *([self.sort] * key[1]), z3.BoolSort())
            args = [bound[t.name] if t.kind == 'variable' and t.name in bound
                    else z3.Const(f'{t.kind}:{t.name}', self.sort) for t in formula.terms]
            return self.predicates[key](*args)
        if op in ('forall', 'exists'):
            variable = z3.Const(f'bound:{formula.variable}:{len(bound)}', self.sort)
            body = self.compile(formula.args[0], {**bound, formula.variable: variable})
            return (z3.ForAll if op == 'forall' else z3.Exists)([variable], body)
        args = [self.compile(f, bound) for f in formula.args]
        return {'not': lambda: z3.Not(args[0]), 'and': lambda: z3.And(*args),
                'or': lambda: z3.Or(*args), 'implies': lambda: z3.Implies(*args),
                'iff': lambda: args[0] == args[1]}[op]()


def entails(premises: tuple[Formula, ...], conclusion: Formula, timeout_ms: int) -> str:
    if timeout_ms <= 0:
        raise ValueError('solver timeout must be positive')
    compiler, solver = Compiler(), z3.Solver()
    solver.set(timeout=timeout_ms)
    solver.add(*(compiler.compile(f) for f in premises))
    solver.add(z3.Not(compiler.compile(conclusion)))
    result = solver.check()
    if result == z3.unsat:
        return 'SOLVER_UNSAT'
    if result == z3.sat:
        return 'SOLVER_COUNTEREXAMPLE'
    return 'SOLVER_TIMEOUT' if 'timeout' in solver.reason_unknown().lower() else 'SOLVER_UNKNOWN'
