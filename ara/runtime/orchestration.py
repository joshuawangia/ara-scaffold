"""Runtime lifecycle; all search, robustness and conflicts belong to engine API."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Protocol

from ara.bank import Bank
from ara.engine import AnalysisResult, Engine, EngineConfig
from ara.runtime.cache import canonical
from ara.runtime.calls import ModelCalls
from ara.runtime.export import export_run
from ara.runtime.extraction import save_immutable
from ara.runtime.render import save_route
from ara.types import CommitmentSet, Proposition, RouteGraph


class EngineAPI(Protocol):
    def analyse(self, target: Proposition, commitments: CommitmentSet) -> AnalysisResult: ...


class NativeEngine:
    """Bind runtime ports to the engine's complete, deterministic analysis API."""
    def __init__(self, bank: Bank, calls: ModelCalls):
        self.bank, self.calls = bank, calls

    def analyse(self, target: Proposition, commitments: CommitmentSet) -> AnalysisResult:
        calls = self.calls
        engine = Engine(bank=self.bank, commitments=commitments, proposer=calls,
                        formaliser=calls, leaf_mapper=calls, cq_answerer=calls,
                        repairer=calls, sink=calls.log,
                        config=EngineConfig.from_mapping(calls.config))
        return engine.analyse(target)


def native_engine(bank: Bank, calls: ModelCalls) -> EngineAPI:
    return NativeEngine(bank, calls)


def prepare_commitments(calls: ModelCalls, bank: Bank, literature: str, audience: str) -> CommitmentSet:
    """One construction lifecycle, one freeze. Search cannot observe provisional batches."""
    if any(e['stage'] == 'commitments_frozen' for e in calls.log.read()):
        raise ValueError('commitments already frozen for this run')
    commitments = calls.build_t(literature, audience)
    save_immutable(calls.log.path.parent / 'commitments.json', commitments.to_json())
    calls.log.record('commitments_frozen', commitments=commitments.to_dict(), bank_version=bank.bank_version)
    return commitments


def prepare(calls: ModelCalls, bank: Bank, literature: str, audience: str,
            named_position: str | None = None) -> tuple[CommitmentSet, tuple[Proposition, ...]]:
    commitments = prepare_commitments(calls, bank, literature, audience)
    targets = calls.propose_targets(commitments, calls.config['target_candidates'], named_position)
    targets = tuple(p if p.formula else replace(p, formula=calls.formalise(p)) for p in targets)
    calls.log.record('candidates', candidates=[p.to_dict() for p in targets])
    return commitments, targets


def search_all(calls: ModelCalls, engine: EngineAPI, commitments: CommitmentSet,
               targets: tuple[Proposition, ...]) -> tuple[RouteGraph, ...]:
    routes = []
    graphs_by_id = {}
    analyses = []
    for target in targets:
        calls.log.record('analysis_started', target=target.to_dict())
        analysis = engine.analyse(target, commitments)
        analyses.append(analysis.to_dict())
        for result, polarity in ((analysis.target, 'target'), (analysis.negated, 'negation')):
            calls.log.record('search_started', target=target.id, polarity=polarity,
                             goal=result.target.to_dict(), source='completed engine analysis')
            for route in result.routes:
                # Formula-identical targets can share deterministic graph ids.
                # Retain each search in the log, but persist/select a graph once.
                calls.log.record('route', target=target.id, polarity=polarity, graph=route.to_dict())
                previous = graphs_by_id.get(route.id)
                if previous is not None and previous != route:
                    raise ValueError('engine returned conflicting graphs for one route id')
                if previous is None:
                    graphs_by_id[route.id] = route
                    save_route(calls.log.path.parent / 'routes', route)
                    routes.append(route)
            calls.log.record('search_finished', target=target.id, polarity=polarity,
                             routes=[r.id for r in result.routes],
                             closed=[r.id for r in result.routes if r.status == 'CLOSED'],
                             truncated=result.truncated, nodes_created=result.nodes_created,
                             independent_closed_routes=result.independent_closed_routes)
    calls.log.record('conflicts_and_robustness', findings={'analyses': analyses})
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
