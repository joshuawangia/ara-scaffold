"""Runtime lifecycle; all search, robustness and conflicts belong to engine API."""
from __future__ import annotations

import json

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Protocol

from ara.bank import Bank
from ara.engine import AnalysisResult, Engine, EngineConfig
from ara.engine.conflicts import analyse_searches
from ara.runtime.logging import SerializedEventLog
from ara.runtime.search_jobs import job_failure, run_search_jobs
from ara.engine.search import SearchResult
from ara.runtime.cache import canonical, digest
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
            if provenance is None or provenance['commitments'][c.id]['stance'] in ('endorsed', 'model_alignment', 'proposed')))
        calls.log.record('search_stance_policy', provenance_status=vocabulary['provenance_status'],
                         provenance_sha256=vocabulary['provenance_sha256'],
                         eligible_commitment_ids=[c.id for c in premises.commitments],
                         note='Legacy stance is unavailable. Model alignments are disclosed premises, never source endorsements. Verified reported/attacked content is usable only as a scoped hypothesis, never a global premise.')
        return Engine(bank=self.bank, commitments=commitments, proposer=calls,
                        formaliser=calls, leaf_mapper=calls, cq_answerer=calls,
                        repairer=calls, sink=calls.log,
                        config=EngineConfig.from_mapping(calls.config), traces=SearchTraceFiles(calls.log),
                        premise_commitments=premises)

    def analyse(self, target: Proposition, commitments: CommitmentSet) -> AnalysisResult:
        if target.formula is None:
            target = replace(target, formula=self.calls.formalise(target, commitments=commitments))
        from ara.runtime.search_context import target_scope
        with target_scope(target):
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
    from ara.runtime.hypotheses import validate_hypothesis_config
    validate_hypothesis_config(calls.config)
    from ara.runtime.vocabulary_consolidation import policy, consolidate
    policy(calls.config)
    state = getattr(calls, 'alignment_resume', None)
    if state is not None:
        from ara.runtime.closure_budget import apply_context_limits
        decision = apply_context_limits(calls.config)
        if decision is not None:
            calls.log.record('operator_construction_limits', **decision)
    commitments = (state.get('consolidation_original',state['commitments']) if state is not None
                   else calls.build_t(literature, audience))
    # Rich construction exposes semantic metadata without changing the strict
    # CommitmentSet codec or the legacy commitments.json artifact.
    from ara.runtime.frozen_catalogue import frozen_artifact
    import json
    merged = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'build_t_merged']
    if merged:
        latest = merged[-1]
        if latest['commitments'] != commitments.to_dict():
            raise ValueError('frozen catalogue construction mismatch')
        from ara.runtime.symbol_alignment import align_symbols
        commitments,symbols,rows,consolidation = consolidate(calls,commitments,latest['symbols'],latest['provenance'],literature)
        if consolidation is not None and state is not None and state.get('consolidation') is None:
            # Prior alignment judgments bind the original formulas/catalogue and cannot be replayed.
            calls.alignment_resume = None
        commitments, symbols, rows, alignment = align_symbols(calls, commitments, symbols, rows, consolidation=consolidation)
        if state is not None and state.get('expected_source') is not None:
            from ara.runtime.construction_fork import validate_restored_source
            if consolidation is None or not state.get('reformalizing_source', False):
                validate_restored_source(state['expected_source'], commitments, symbols, rows)
            else:
                from ara.runtime.vocabulary_consolidation import validate_receipt
                from ara.runtime.symbol_alignment import validate_alignment
                before_alignment,before_symbols=(validate_alignment(alignment,commitments,symbols,rows)
                    if alignment is not None else (commitments,symbols))
                original,_=validate_receipt(consolidation,before_alignment,before_symbols,rows)
                expected=state['expected_source']
                source_ids=set(consolidation['provenance'])
                if ([(c.id,c.text,c.citation) for c in original.commitments] !=
                    [(c['id'],c['text'],c['citation']) for c in expected['commitments']['commitments'] if c['id'] in source_ids]
                    or any(expected['provenance'][id]!=rows[id] for id in source_ids)):
                    raise ValueError('consolidation changed frozen source content or provenance')
        from ara.runtime.hypotheses import admit_hypotheses
        commitments, symbols, rows, hypotheses = admit_hypotheses(calls, commitments, symbols, rows)
        measured = calls.count_request('propose_targets', {'commitments': commitments.to_dict(),
            'count': calls.config['target_candidates'], 'named_position': None},
            purpose='commitments_only_capacity_not_target_readiness')
        if measured.initial_input_tokens > calls.config['working_t_token_budget']:
            calls.budget.stop('aligned T downstream token budget exceeded before freeze', 'judge_symbol_alignment')
        artifact = frozen_artifact(commitments, symbols)
        save_immutable(calls.log.path.parent / 'frozen-t.json', canonical(artifact))
        calls.log.record('symbol_catalogue_frozen', **artifact['symbol_catalogue'])
        from ara.runtime.commitment_provenance import make_commitment_provenance
        provenance = make_commitment_provenance(commitments, artifact['symbol_catalogue'], rows, alignment=alignment, hypotheses=hypotheses, consolidation=consolidation)
        save_immutable(calls.log.path.parent / 'commitment-provenance.json', canonical(provenance))
        calls.log.record('commitment_provenance_frozen', **provenance)
    elif calls.config.get('construction_consolidate_vocabulary'):
        raise ValueError('vocabulary consolidation requires rich construction and verified provenance')
    elif calls.config.get('hypothesis_premises'):
        raise ValueError('hypothesis premises require rich construction and verified provenance')
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
    paired = []
    support_gaps = {}
    for target, analysis in zip(targets, results, strict=True):
        if isinstance(analysis, AnalysisResult):
            analyses.append(analysis.to_dict())
            paired.append(analysis)
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
                if (contribution.get('support_consistency') or {}).get('status') == 'conflict':
                    from ara.runtime.conflict_feedback import route_support_gap
                    gap = route_support_gap(route.id, contribution['support_ids'], provenance)
                    support_gaps[gap.id] = gap
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
    if commitments is not None:
        calls.log.record('route_support_conflicts', gaps=[support_gaps[k].to_dict() for k in sorted(support_gaps)],
            commitments_sha256=digest(canonical(commitments.to_dict())),
            provenance_sha256=provenance['sha256'] if provenance else None,
            note='Inconsistent support is a conflict, never ex-falso evidence for selection.')
    calls.log.record('conflicts_and_robustness', findings={'analyses': analyses})
    if commitments is not None:
        from ara.runtime.conflict_feedback import propose_tier2_resolutions
        propose_tier2_resolutions(calls, paired, commitments, provenance)
    return tuple(routes)


def compose(calls: ModelCalls, route: RouteGraph, draft: dict | None = None) -> dict:
    from ara.runtime.essay_audit import audit_and_revise, repair_rounds
    from ara.runtime.route_policy import frozen_from_events, provenance_from_events, route_contribution
    events = calls.log.read()
    commitments = frozen_from_events(events)
    if commitments is not None and route.status == 'CLOSED':
        receipt = route_contribution(route, commitments, provenance_from_events(events, commitments))
        consistency = receipt['support_consistency']
        if consistency['status'] != 'consistent':
            calls.log.record('composition_refused', route_id=route.id, support_consistency=consistency)
            raise ValueError('inconsistent or unresolved route supports cannot supply an essay')

    from ara.runtime.citations import restore_citations, check_coverage
    from ara.runtime.hypotheses import insert_runtime_disclosure, validate_disclosure
    if draft is None:
        draft = insert_runtime_disclosure(calls, route, calls.write_essay(route))
        prior_rounds = 0
    else:
        calls.screen_imported_draft(draft)
        recorded = any(e['stage'] in ('final_draft', 'verification_cleanup', 'essay_audit_revision', 'hypothesis_disclosure_inserted') and
                       json.loads(e['payload_json']).get('draft') == draft for e in calls.log.read())
        calls.validate_essay(route, draft, minimum_words=0 if recorded else None, authored=not recorded)
        if not recorded:
            draft = insert_runtime_disclosure(calls, route, draft)
        calls.log.record('essay_draft_resumed', route_id=route.id, draft=draft)
        prior_rounds = repair_rounds(calls, route)
    validate_disclosure(calls.log.read(), route, draft)
    calls.log.record('essay_composition_started', route_id=route.id,
                     policy='fresh-unanimous-with-adverse-history', repair_rounds=prior_rounds)
    for path in (calls.log.path.parent / 'draft.json', calls.log.path.parent / 'export/essay.txt'):
        path.unlink(missing_ok=True)
    # Save the unverified draft as a clearly named partial artifact, never export it.
    (calls.log.path.parent / 'draft.unverified.json').write_text(canonical(draft))
    draft = restore_citations(calls, route, draft)
    (calls.log.path.parent / 'draft.unverified.json').write_text(canonical(draft))
    draft = audit_and_revise(calls, route, draft)
    cleaned, verification = audit_and_revise(calls, route, draft, final=True)
    coverage = check_coverage(calls.log.read(), route, cleaned)
    if coverage is not None:
        calls.log.record('essay_citation_coverage', route_id=route.id, **coverage)
    calls.log.record('final_draft', draft=cleaned, route_id=route.id, verification=verification)
    (calls.log.path.parent / 'draft.json').write_text(canonical(cleaned))
    export_run(calls.log.path, calls.log.path.parent / 'export')
    return cleaned
