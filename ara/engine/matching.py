"""Backtracking schema unification and capture-avoiding quantifier substitution."""
from __future__ import annotations

from dataclasses import replace
from itertools import combinations
from typing import Iterator

from ara.types import Formula, FormulaSchema, Term

Bindings = tuple[dict[str, Formula], dict[str, Term]]


def terms(formula: Formula) -> set[Term]:
    return set(formula.terms).union(*(terms(a) for a in formula.args))


def substitute(body: Formula, variable: str, term: Term) -> Formula:
    if body.op in ('forall', 'exists'):
        if body.variable == variable:
            return body
        if term.kind == 'variable' and body.variable == term.name:
            names = {t.name for t in terms(body)} | {variable, term.name}
            fresh = body.variable + '_'
            while fresh in names:
                fresh += '_'
            body = replace(body, variable=fresh, args=(
                substitute(body.args[0], body.variable, Term('variable', fresh)),))
    return replace(body, terms=tuple(term if t == Term('variable', variable) else t for t in body.terms),
                   args=tuple(substitute(a, variable, term) for a in body.args))


def match(pattern: Formula, value: Formula, schema: FormulaSchema,
          bindings: Bindings = ({}, {})) -> Iterator[Bindings]:
    formulas, ts = bindings
    pattern, value = pattern.normalized(), value.normalized()
    if pattern.op == 'atom' and pattern.name in schema.formula_variables:
        old = formulas.get(pattern.name)
        if old is None or old.canonical() == value.canonical():
            yield ({**formulas, pattern.name: value}, ts)
        return
    if pattern.op != value.op or pattern.name != value.name or len(pattern.terms) != len(value.terms):
        return
    ts = dict(ts)
    if pattern.variable:
        v = Term('variable', value.variable)
        if pattern.variable in ts and ts[pattern.variable] != v:
            return
        ts[pattern.variable] = v
    for p, v in zip(pattern.terms, value.terms):
        if p.name in schema.term_variables:
            if p.kind != v.kind or (p.name in ts and ts[p.name] != v):
                return
            ts[p.name] = v
        elif p != v:
            return
    if pattern.op in ('and', 'or'):
        # Partition normalized n-ary expressions, retaining repeated operands.
        def parts(ps: tuple[Formula, ...], vs: tuple[Formula, ...], env: Bindings):
            if len(ps) == 1:
                grouped = vs[0] if len(vs) == 1 else Formula(pattern.op, vs)
                yield from match(ps[0], grouped, schema, env)
                return
            for size in range(1, len(vs) - len(ps) + 2):
                for indices in combinations(range(len(vs)), size):
                    group = tuple(vs[i] for i in indices)
                    rest = tuple(v for i, v in enumerate(vs) if i not in indices)
                    grouped = group[0] if size == 1 else Formula(pattern.op, group)
                    for next_env in match(ps[0], grouped, schema, env):
                        yield from parts(ps[1:], rest, next_env)
        if len(value.args) >= len(pattern.args):
            yield from parts(pattern.args, value.args, (formulas, ts))
        return
    if len(pattern.args) != len(value.args):
        return
    envs = [(formulas, ts)]
    for p, v in zip(pattern.args, value.args):
        envs = [e for env in envs for e in match(p, v, schema, env)]
    yield from envs


def instantiate(pattern: Formula, bindings: Bindings) -> Formula:
    fs, ts = bindings
    if pattern.op == 'atom' and pattern.name in fs:
        return fs[pattern.name]
    return replace(pattern, args=tuple(instantiate(a, bindings) for a in pattern.args),
                   terms=tuple(ts.get(t.name, t) for t in pattern.terms),
                   variable=ts[pattern.variable].name if pattern.variable in ts else pattern.variable)


def matches_schema(schema: FormulaSchema, fills: dict[str, Formula], conclusion: Formula) -> bool:
    envs: list[Bindings] = [({}, {})]
    for pattern, value in [(p.formula, fills[p.slot]) for p in schema.premises] + [(schema.conclusion, conclusion)]:
        envs = [e for env in envs for e in match(pattern, value, schema, env)]
    values = {**fills, 'conclusion': conclusion}
    for fs, ts in envs:
        valid = True
        for sub in schema.substitutions:
            body = fs[sub.body_variable]
            variable = ts.get(sub.variable, Term('variable', sub.variable)).name
            candidates = [ts[sub.term.name]] if sub.term.name in ts else sorted(
                {t for f in values.values() for t in terms(f) if t.kind == sub.term.kind},
                key=lambda t: t.to_json())
            # Vacuous binding still has a legitimate instance.
            candidates = candidates or [sub.term]
            if not any(substitute(body, variable, t).canonical() == values[sub.slot].canonical()
                       for t in candidates):
                valid = False
                break
        if valid:
            return True
    return False
