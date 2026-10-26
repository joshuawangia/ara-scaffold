"""Depth-bounded forward instantiation over a finite observed formula vocabulary."""
from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product
from typing import Callable, Iterator

from ara.engine.licensing import License, Licenser, emit
from ara.engine.matching import Bindings, instantiate, match, substitute, terms
from ara.engine.routes import cq_supported
from ara.types import CommitmentSet, Formula, FormulaSchema, PremiseFill, Proposal, Proposition, Record, RouteGraph, Term


@dataclass(frozen=True)
class Consequence(Record):
    formula: Formula
    bank_id: str
    premises: tuple[Formula, ...]
    depth: int
    flagged: bool


@dataclass(frozen=True)
class ForwardResult(Record):
    consequences: tuple[Consequence, ...]
    truncated: bool
    route_id: str | None = None


class _CanonicalFormaliser:
    def formalise(self, proposition: Proposition) -> Formula:
        return Formula.from_json(proposition.text)


class _WorkLimit(Exception):
    pass


@dataclass
class _Budget:
    remaining: int

    def use(self):
        self.remaining -= 1
        if self.remaining < 0:
            raise _WorkLimit


def _subformulas(f: Formula) -> set[Formula]:
    return {f}.union(*(_subformulas(a) for a in f.args))


def _abstract(f: Formula, term: Term, variable: str) -> Formula:
    return replace(f, terms=tuple(Term('variable', variable) if t == term else t for t in f.terms),
                   args=tuple(_abstract(a, term, variable) for a in f.args))


def _instances(schema: FormulaSchema, known: tuple[Formula, ...], budget: _Budget
               ) -> Iterator[tuple[dict[str, Formula], Formula]]:
    def premises(index: int, env: Bindings, fills: dict[str, Formula]):
        if index == len(schema.premises):
            yield env, fills
            return
        pattern = schema.premises[index]
        for value in known:
            budget.use()
            for next_env in match(pattern.formula, value, schema, env):
                yield from premises(index + 1, next_env, {**fills, pattern.slot: value})

    # Unbound metavariables range over observed subformulas, never free text.
    domain = sorted(set().union(*(_subformulas(f) for f in known)), key=lambda f: f.canonical())
    constants = sorted({t for f in known for t in terms(f) if t.kind == 'constant'}, key=lambda t: t.to_json())
    for (fs, ts), fills in premises(0, ({}, {}), {}):
        envs = [(fs, ts)]
        for sub in schema.substitutions:
            expanded = []
            for fs, ts in envs:
                variable = ts.get(sub.variable, Term('variable', sub.variable)).name
                if sub.slot == 'conclusion' and sub.body_variable in fs:
                    # UI's conclusion instance is explicitly constrained by the body.
                    for term in constants or [sub.term]:
                        value = substitute(fs[sub.body_variable], variable, term)
                        expanded.append(({**fs, schema.conclusion.name: value}, {**ts, sub.term.name: term}))
                elif sub.slot in fills:
                    for term in constants or [sub.term]:
                        body = _abstract(fills[sub.slot], term, variable)
                        expanded.append(({**fs, sub.body_variable: body}, {**ts, sub.term.name: term}))
            envs = expanded
        for fs, ts in envs:
            missing = [v for v in schema.formula_variables if v not in fs]
            for values in product(domain, repeat=len(missing)):
                budget.use()
                bindings = ({**fs, **dict(zip(missing, values))}, ts)
                yield fills, instantiate(schema.conclusion, bindings).normalized()


def forward_pass(leaves: tuple[Formula, ...], commitments: CommitmentSet, licenser: Licenser,
                 depth: int, node_cap: int = 500, witnesses: tuple[RouteGraph, ...] = (),
                 route_id: str | None = None,
                 on_license: Callable[[Proposal, License], None] | None = None) -> ForwardResult:
    if depth < 0 or node_cap < 1:
        raise ValueError('invalid forward bounds')
    checker = Licenser(licenser.bank, _CanonicalFormaliser(), licenser.sink, licenser.timeout_ms)
    known = {f.canonical(): f.normalized() for f in leaves}
    known_depth = {key: 0 for key in known}
    consequences, attempted = [], set()
    budget = _Budget(node_cap * max(1, len(licenser.bank.entries)) * 10)

    def add(formula: Formula, bank_id: str, premises: tuple[Formula, ...], level: int):
        key = formula.canonical()
        if key in known:
            return
        if len(consequences) >= node_cap:
            raise _WorkLimit
        known[key] = formula.normalized()
        known_depth[key] = level
        flagged = commitments.contains_formula(formula.negated())
        consequences.append(Consequence(formula.normalized(), bank_id, premises, level, flagged))
        emit(licenser.sink, 'discarded' if flagged else 'licensed',
             'FORWARD_OPPOSED' if flagged else 'FORWARD_DERIVED', bank_id=bank_id)

    try:
        for level in range(1, depth + 1):
            snapshot = tuple(known.values())
            snapshot_keys = set(known)
            before = len(known)
            # Replay individual observed inferences, never a multi-step root as
            # one forward step. Scoped exports carry their subproof height.
            for graph in witnesses:
                if graph.status != 'CLOSED':
                    continue
                nodes = {n.id: n for n in graph.nodes}

                def dependencies(node):
                    if node.kind == 'leaf':
                        return {node.proposition.formula.canonical()}, 0
                    if node.kind == 'assumption':
                        return set(), 0
                    children = [dependencies(nodes[c]) for c in node.children]
                    support = {commitments.get(tid).formula.canonical()
                               for a in node.cq_answers for tid in a.supporting_t_ids
                               if commitments.get(tid) is not None}
                    return support.union(*(s for s, _ in children)), 1 + max((h for _, h in children), default=0)

                for node in graph.nodes:
                    if node.kind != 'inference' or node.scope_id is not None:
                        continue
                    entry = checker.bank.get(node.proposal.bank_id)
                    children = tuple(nodes[c] for c in node.children)
                    if entry.formula_schema and entry.formula_schema.scopes:
                        required, height = dependencies(node)
                        if max((known_depth.get(f, level) for f in required), default=0) + height > level:
                            continue
                    else:
                        required = {c.proposition.formula.canonical() for c in children}
                        required.update(commitments.get(tid).formula.canonical()
                                        for a in node.cq_answers for tid in a.supporting_t_ids
                                        if commitments.get(tid) is not None)
                    if not required <= snapshot_keys:
                        continue
                    fills = {p.slot: p for p in node.proposal.premises}
                    canonical_proposal = replace(node.proposal,
                        premises=tuple(replace(fills[s.id], text=c.proposition.formula.canonical())
                                       for s, c in zip(entry.premise_slots, children)),
                        conclusion_text=node.proposition.formula.canonical(), conclusion_ref=None)
                    license = checker.check(canonical_proposal, node.proposition)
                    if license.licensed and all(any(cq_supported(a, q.id, commitments) for a in node.cq_answers)
                                               for q in license.entry.critical_questions):
                        if on_license:
                            on_license(canonical_proposal, license)
                        support = tuple(Formula.from_json(f) for f in sorted(required))
                        add(node.proposition.formula, node.proposal.bank_id, support, level)
            for entry in licenser.bank.entries:
                schema = entry.formula_schema
                if schema is None or schema.scopes:
                    continue
                for fills, conclusion in _instances(schema, snapshot, budget):
                    key = (entry.id, tuple(f.canonical() for f in fills.values()), conclusion.canonical())
                    if key in attempted or conclusion.canonical() in known:
                        continue
                    attempted.add(key)
                    proposal = Proposal(entry.id, tuple(PremiseFill(s.id, fills[s.id].canonical())
                                                        for s in entry.premise_slots), conclusion.canonical())
                    result = checker.check(proposal, Proposition('forward', conclusion.canonical(), conclusion))
                    if result.licensed:
                        if on_license:
                            on_license(proposal, result)
                        add(conclusion, entry.id, tuple(fills.values()), level)
            if len(known) == before:
                break
    except _WorkLimit:
        emit(licenser.sink, 'discarded', 'FORWARD_CAP', 'Forward node or instantiation work cap reached')
        return ForwardResult(tuple(consequences), True, route_id)
    return ForwardResult(tuple(consequences), False, route_id)
