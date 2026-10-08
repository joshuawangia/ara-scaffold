"""Runtime lifecycle; all search, robustness and conflicts belong to engine API."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Protocol, Any

from ara.bank import Bank
from ara.runtime.cache import canonical
from ara.runtime.calls import ModelCalls, Rejected
from ara.runtime.export import export_run
from ara.runtime.render import save_route
from ara.types import CommitmentSet, Proposition, RouteGraph, negate_proposition


class EngineAPI(Protocol):
    """Temporary runtime-side interface until the engine lane publishes its API.

    The factory receives adapters implementing every ara.ports protocol. Search
    returns graphs only. Conflicts performs Tier 1, Tier 2, forward pass and route
    independence accounting and returns JSON-serializable findings. It emits every
    licensing/discard decision through the supplied EventSink.
    """
    def search(self, target: Proposition, commitments: CommitmentSet) -> tuple[RouteGraph, ...]: ...
    def conflicts(self, routes: tuple[RouteGraph, ...], commitments: CommitmentSet) -> dict: ...


def native_engine(bank: Bank, calls: ModelCalls) -> EngineAPI:
    try:
        from ara.engine import create_engine
    except ImportError as exc:
        raise RuntimeError('engine public API unavailable: ara.engine.create_engine; integration required') from exc
    return create_engine(bank=bank, proposer=calls, formaliser=calls, mapper=calls,
                         cq_answerer=calls, repairer=calls, sink=calls.log, config=calls.config)


def prepare(calls: ModelCalls, bank: Bank, literature: str, audience: str,
            named_position: str | None = None) -> tuple[CommitmentSet, tuple[Proposition, ...]]:
    commitments = calls.build_t(literature, audience)
    calls.log.record('commitments_frozen', commitments=commitments.to_dict(), bank_version=bank.bank_version)
    (calls.log.path.parent / 'commitments.json').write_text(commitments.to_json())
    targets = calls.propose_targets(commitments, calls.config['target_candidates'], named_position)
    targets = tuple(p if p.formula else replace(p, formula=calls.formalise(p)) for p in targets)
    calls.log.record('candidates', candidates=[p.to_dict() for p in targets])
    return commitments, targets


def search_all(calls: ModelCalls, engine: EngineAPI, commitments: CommitmentSet,
               targets: tuple[Proposition, ...]) -> tuple[RouteGraph, ...]:
    routes = []
    ids = set()
    for target in targets:
        for goal, polarity in ((target, 'target'), (negate_proposition(target), 'negation')):
            calls.log.record('search_started', target=target.id, polarity=polarity, goal=goal.to_dict())
            found = engine.search(goal, commitments)
            for route in found:
                if route.id in ids:
                    raise ValueError('engine returned duplicate route id')
                ids.add(route.id)
                calls.log.record('route', target=target.id, polarity=polarity, graph=route.to_dict())
                save_route(calls.log.path.parent / 'routes', route)
                routes.append(route)
            calls.log.record('search_finished', target=target.id, polarity=polarity,
                             routes=[r.id for r in found], closed=[r.id for r in found if r.status == 'CLOSED'])
    findings = engine.conflicts(tuple(routes), commitments)
    calls.log.record('conflicts_and_robustness', findings=findings)
    return tuple(routes)


def compose(calls: ModelCalls, route: RouteGraph) -> dict:
    draft = calls.write_essay(route)
    # Save the unverified draft as a clearly named partial artifact, never export it.
    (calls.log.path.parent / 'draft.unverified.json').write_text(canonical(draft))
    calls.audit_essay(route, draft)
    cleaned, verification = calls.verify_originality_citations(draft)
    # Removing unsupported items can change the route's coverage; audit again.
    calls.audit_essay(route, cleaned)
    calls.log.record('final_draft', draft=cleaned, route_id=route.id, verification=verification)
    (calls.log.path.parent / 'draft.json').write_text(canonical(cleaned))
    export_run(calls.log.path, calls.log.path.parent / 'export')
    return cleaned
