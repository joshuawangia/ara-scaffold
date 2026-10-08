"""Canonical conflict witnesses and repair requests; no automatic premise edits."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ara.engine.forward import Consequence, ForwardResult, forward_pass
from ara.engine.licensing import emit
from ara.engine.routes import leaf_premises
from ara.engine.search import SearchResult
from ara.types import Formula, Proposition, Record, Tier1Repair, negate_proposition

if TYPE_CHECKING:
    from ara.engine.search import Engine


@dataclass(frozen=True)
class Tier1Conflict(Record):
    premise_forms: tuple[str, ...]
    conclusions: tuple[Proposition, ...]
    repair: Tier1Repair


@dataclass(frozen=True)
class Tier2Conflict(Record):
    positive_route_id: str
    negative_route_id: str
    first_flagged: Consequence | None


@dataclass(frozen=True)
class AnalysisResult(Record):
    target: SearchResult
    negated: SearchResult
    forward: tuple[ForwardResult, ...]
    tier1: tuple[Tier1Conflict, ...]
    tier2: tuple[Tier2Conflict, ...]


def analyse(engine: Engine, target: Proposition) -> AnalysisResult:
    engine._licenses = []
    positive = engine.search(target)
    negative = engine.search(negate_proposition(positive.target))
    closed = tuple(r for result in (positive, negative) for r in result.routes if r.status == 'CLOSED')
    forward = tuple(forward_pass(tuple(Formula.from_json(f) for f in sorted(leaf_premises(r, engine.commitments))),
                                 engine.commitments, engine.licenser, engine.config.forward_pass_depth,
                                 engine.config.node_cap, closed, r.id,
                                 lambda p, license: engine._licenses.append((p, license))) for r in closed)
    groups, tier1, marked = {}, [], set()
    for proposal, license in engine._licenses:
        # A scoped assumption is not a global premise. Scoped conflicts are
        # discovered through their closed exported routes below.
        if license.entry.formula_schema and license.entry.formula_schema.scopes:
            continue
        key = tuple(sorted({p.formula.canonical() for p in license.premises}))
        group = groups.setdefault(key, {})
        conclusion = license.conclusion
        opposite = conclusion.formula.negated().canonical()
        pair = (key, tuple(sorted((conclusion.formula.canonical(), opposite))))
        if opposite in group and pair not in marked:
            conclusions = (group[opposite], conclusion)
            emit(engine.sink, 'discarded', 'TIER1_CONFLICT', detail=';'.join(key))
            repair = engine.repairer.repair_tier1(proposal.premises, conclusions, engine.commitments)
            tier1.append(Tier1Conflict(key, conclusions, repair))
            marked.add(pair)
        group[conclusion.formula.canonical()] = conclusion
    by_id = {f.route_id: f for f in forward}
    tier2 = []
    for p in positive.routes:
        for n in negative.routes:
            if p.status != 'CLOSED' or n.status != 'CLOSED':
                continue
            flagged = next((c for f in (by_id[p.id], by_id[n.id]) for c in f.consequences if c.flagged), None)
            tier2.append(Tier2Conflict(p.id, n.id, flagged))
            emit(engine.sink, 'discarded', 'TIER2_CONFLICT', detail=f'{p.id};{n.id}')
    return AnalysisResult(positive, negative, forward, tuple(tier1), tuple(tier2))
