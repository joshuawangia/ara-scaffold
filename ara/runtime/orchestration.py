"""Runtime lifecycle; all search, robustness and conflicts belong to engine API."""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Protocol

from ara.bank import Bank
from ara.engine import AnalysisResult, Engine, EngineConfig
from ara.engine.conflicts import analyse_searches
from ara.runtime.logging import SerializedEventLog
from ara.runtime.search_jobs import job_failure, run_search_jobs
from ara.engine.search import SearchResult
from ara.runtime.cache import canonical
from ara.runtime.calls import ModelCalls
from ara.runtime.export import export_run
from ara.runtime.extraction import save_immutable
from ara.runtime.render import save_route
from ara.runtime.search_traces import SearchTraceFiles
from ara.types import CommitmentSet, Proposition, RouteGraph, negate_proposition


class EngineAPI(Protocol):
    def analyse(self, target: Proposition, commitments: CommitmentSet) -> AnalysisResult: ...


@dataclass(frozen=True)
class PartialSearch:
    target: SearchResult | None
    negated: SearchResult | None


class NativeEngine:
    """Bind runtime ports to the engine's complete, deterministic analysis API."""
    def __init__(self, bank: Bank, calls: ModelCalls):
        self.bank, self.calls = bank, calls

    def _engine(self, commitments: CommitmentSet) -> Engine:
        calls = self.calls
        vocabulary = calls.search_vocabulary(commitments)
        provenance = vocabulary['commitment_provenance']
        premises = CommitmentSet(tuple(c for c in commitments.commitments
            if provenance is None or provenance['commitments'][c.id]['stance'] == 'endorsed'))
        calls.log.record('search_stance_policy', provenance_status=vocabulary['provenance_status'],
                         provenance_sha256=vocabulary['provenance_sha256'],
                         eligible_commitment_ids=[c.id for c in premises.commitments],
                         note='Legacy stance is unavailable. Verified reported/attacked content is usable only as a scoped hypothesis, never a global premise.')
        return Engine(bank=self.bank, commitments=commitments, proposer=calls,
                        formaliser=calls, leaf_mapper=calls, cq_answerer=calls,
                        repairer=calls, sink=calls.log,
                        config=EngineConfig.from_mapping(calls.config), traces=SearchTraceFiles(calls.log),
                        premise_commitments=premises)

    def analyse(self, target: Proposition, commitments: CommitmentSet) -> AnalysisResult:
        if target.formula is None:
            target = replace(target, formula=self.calls.formalise(target, commitments=commitments))
        return self._engine(commitments).analyse(target)

    def analyse_all(self, targets, commitments, concurrency, *, restored=None):
        restored = restored or {}
        from ara.runtime.route_policy import stance_crossings
        provenance = self.calls.search_vocabulary(commitments)['commitment_provenance']
        if any(route.status == 'CLOSED' and stance_crossings(route, provenance) for result, _ in restored.values() for route in result.routes):
            raise ValueError('restored search crosses frozen source stance')
        # A missing formula must be resolved once before constructing its negation.
        targets = tuple(t if t.formula else replace(t, formula=self.calls.formalise(t, commitments=commitments)) for t in targets)
        jobs = []
        for target in targets:
            self.calls.log.record('analysis_started', target=target.to_dict())
            for serial, goal in enumerate((target, negate_proposition(target))):
                engine = self._engine(commitments)
                engine._search_serial = serial
                if len(jobs) in restored:
                    engine._licenses.extend(restored[len(jobs)][1])
                jobs.append((engine, goal))
        results, fatal = run_search_jobs(self.calls.log, jobs, concurrency,
                                         lambda: self._engine(commitments),
                                         restored={i: item[0] for i, item in restored.items()})
        for i in range(0, len(jobs), 2):
            positive, negative = jobs[i][0], jobs[i + 1][0]
            reason = 'run_stopped' if fatal else 'missing_search'
            if fatal is None and results[i] is not None and results[i + 1] is not None:
                positive._licenses.extend(negative._licenses)
                try:
                    analysis = analyse_searches(positive, results[i], results[i + 1])
                except Exception as exc:
                    reason = type(exc).__name__
                    if not job_failure(exc):
                        fatal = exc
                else:
                    yield analysis
                    continue
            self.calls.log.record('search_analysis_failed', target=targets[i // 2].id,
                                  status='partial', reason=reason,
                                  note='Completed routes retained; paired conflict analysis unavailable.')
            yield PartialSearch(results[i], results[i + 1])
        if fatal is not None:
            raise fatal


def native_engine(bank: Bank, calls: ModelCalls) -> EngineAPI:
    return NativeEngine(bank, calls)


def prepare_commitments(calls: ModelCalls, bank: Bank, literature: str, audience: str) -> CommitmentSet:
    """One construction lifecycle, one freeze. Search cannot observe provisional batches."""
    if any(e['stage'] == 'commitments_frozen' for e in calls.log.read()):
        raise ValueError('commitments already frozen for this run')
    commitments = calls.build_t(literature, audience)
    # Rich construction exposes semantic metadata without changing the strict
    # CommitmentSet codec or the legacy commitments.json artifact.
    from ara.runtime.frozen_catalogue import frozen_artifact
    import json
    merged = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'build_t_merged']
    if merged:
        latest = merged[-1]
        if latest['commitments'] != commitments.to_dict():
            raise ValueError('frozen catalogue construction mismatch')
        artifact = frozen_artifact(commitments, latest['symbols'])
        save_immutable(calls.log.path.parent / 'frozen-t.json', canonical(artifact))
        calls.log.record('symbol_catalogue_frozen', **artifact['symbol_catalogue'])
        from ara.runtime.commitment_provenance import make_commitment_provenance
        provenance = make_commitment_provenance(commitments, artifact['symbol_catalogue'], latest['provenance'])
        save_immutable(calls.log.path.parent / 'commitment-provenance.json', canonical(provenance))
        calls.log.record('commitment_provenance_frozen', **provenance)
    save_immutable(calls.log.path.parent / 'commitments.json', commitments.to_json())
    calls.log.record('commitments_frozen', commitments=commitments.to_dict(), bank_version=bank.bank_version)
    return commitments


def prepare(calls: ModelCalls, bank: Bank, literature: str, audience: str,
            named_position: str | None = None) -> tuple[CommitmentSet, tuple[Proposition, ...]]:
    commitments = prepare_commitments(calls, bank, literature, audience)
    targets = calls.propose_targets(commitments, calls.config['target_candidates'], named_position)
    targets = tuple(p if p.formula else replace(p, formula=calls.formalise(p, commitments=commitments)) for p in targets)
    calls.log.record('candidates', candidates=[p.to_dict() for p in targets])
    return commitments, targets


def search_all(calls: ModelCalls, engine: EngineAPI, commitments: CommitmentSet,
               targets: tuple[Proposition, ...], *, restored=None) -> tuple[RouteGraph, ...]:
    concurrency = calls.config.get('search_concurrency', 4)
    if type(concurrency) is not int or concurrency < 1:
        raise ValueError('search_concurrency must be a positive integer')
    original_log, budget_log = calls.log, calls.budget.log
    with SerializedEventLog(original_log) as writer:
        calls.log = calls.budget.log = writer
        try:
            if isinstance(engine, NativeEngine):
                analyses = engine.analyse_all(targets, commitments, concurrency, restored=restored)
            else:
                def sequential():
                    for target in targets:
                        calls.log.record('analysis_started', target=target.to_dict())
                        yield engine.analyse(target, commitments)
                analyses = sequential()
            return _save_analyses(calls, targets, analyses, commitments)
        finally:
            calls.log, calls.budget.log = original_log, budget_log


def _save_analyses(calls, targets, results, commitments=None):
    provenance = calls.search_vocabulary(commitments)['commitment_provenance'] if commitments is not None else None
    routes = []
    graphs_by_id = {}
    analyses = []
    for target, analysis in zip(targets, results, strict=True):
        if isinstance(analysis, AnalysisResult):
            analyses.append(analysis.to_dict())
        for result, polarity in ((analysis.target, 'target'), (analysis.negated, 'negation')):
            if result is None:
                continue
            calls.log.record('search_started', target=target.id, polarity=polarity,
                             goal=result.target.to_dict(), source=('completed search; paired analysis unavailable'
                                 if isinstance(analysis, PartialSearch) else 'completed engine analysis'))
            for route in result.routes:
                # Formula-identical targets can share deterministic graph ids.
                # Retain each search in the log, but persist/select a graph once.
                from ara.runtime.route_policy import route_contribution
                contribution = route_contribution(route, commitments, provenance)
                calls.log.record('route', target=target.id, polarity=polarity, graph=route.to_dict(),
                                 contribution=contribution,
                                 classification=contribution['classification'])
                previous = graphs_by_id.get(route.id)
                if previous is not None and previous != route:
                    raise ValueError('engine returned conflicting graphs for one route id')
                if previous is None:
                    graphs_by_id[route.id] = route
                    save_route(calls.log.path.parent / 'routes', route, commitments, provenance)
                    routes.append(route)
            calls.log.record('search_finished', target=target.id, polarity=polarity,
                             routes=[r.id for r in result.routes],
                             closed=[r.id for r in result.routes if r.status == 'CLOSED'],
                             truncated=result.truncated, nodes_created=result.nodes_created,
                             independent_closed_routes=result.independent_closed_routes)
    calls.log.record('conflicts_and_robustness', findings={'analyses': analyses})
    return tuple(routes)


def compose(calls: ModelCalls, route: RouteGraph, draft: dict | None = None) -> dict:
    from ara.runtime.essay_audit import audit_and_revise
    if draft is None:
        draft = calls.write_essay(route)
    else:
        calls.validate_essay(route, draft)
        calls.log.record('essay_draft_resumed', route_id=route.id, draft=draft)
    # Save the unverified draft as a clearly named partial artifact, never export it.
    (calls.log.path.parent / 'draft.unverified.json').write_text(canonical(draft))
    draft = audit_and_revise(calls, route, draft)
    cleaned, verification = calls.verify_originality_citations(draft)
    # Removing unsupported items can change the route's coverage; audit again.
    calls.audit_essay(route, cleaned)
    calls.log.record('final_draft', draft=cleaned, route_id=route.id, verification=verification)
    (calls.log.path.parent / 'draft.json').write_text(canonical(cleaned))
    export_run(calls.log.path, calls.log.path.parent / 'export')
    return cleaned
