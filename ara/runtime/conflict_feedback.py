"""Resolution feedback and report projections for engine-owned paired analyses."""
import json
from ara.runtime.cache import canonical, digest
from ara.types import Gap


def route_support_gap(route_id, support_ids, provenance):
    rows = provenance['commitments'] if provenance else {}
    ids = tuple(sorted(set(support_ids)))
    papers = tuple(sorted({rows[tid]['source_id'] for tid in ids
        if rows.get(tid, {}).get('stance') == 'endorsed' and rows[tid].get('source_id')}))
    groups = tuple(tuple(tid for tid in ids if rows.get(tid, {}).get('stance') == 'endorsed'
        and rows[tid].get('source_id') == paper) for paper in papers)
    value = dict(kind='contradiction', commitment_ids=ids, paper_ids=papers, support_groups=groups,
                 route_ids=(route_id,), finding='Jointly inconsistent route supports; not an admissible derivation basis.')
    return Gap('gap:' + digest(canonical(value)), **value)


def _support_conflict_receipt(events):
    boundary = max((i for i, e in enumerate(events)
        if e['stage'] in ('commitments_frozen', 'analysis_started', 'search_publication_started')), default=-1)
    receipts = [json.loads(e['payload_json']) for i, e in enumerate(events)
                if i > boundary and e['stage'] == 'route_support_conflicts']
    return receipts[-1] if receipts else None


def support_conflict_gaps(events, commitments, provenance):
    receipt = _support_conflict_receipt(events)
    if provenance is None or receipt is None:
        return ()
    if (receipt['commitments_sha256'] != digest(canonical(commitments.to_dict()))
            or receipt['provenance_sha256'] != provenance['sha256']):
        return ()
    return tuple(Gap.from_dict(g) for g in receipt['gaps'])


def tier2_gaps(analyses, commitments, provenance):
    if provenance is None:
        return ()
    from ara.runtime.route_policy import route_contribution
    rows = provenance['commitments']
    gaps = {}
    for analysis in analyses:
        routes = {r.id:r for search in (analysis.target, analysis.negated) for r in search.routes}
        supports = {rid:tuple(tid for tid in route_contribution(route, commitments, provenance).get('support_ids', ())
                              if rows[tid]['stance'] == 'endorsed')
                    for rid,route in routes.items() if route.status == 'CLOSED'}
        for conflict in analysis.tier2:
            route_ids = (conflict.positive_route_id, conflict.negative_route_id)
            groups = tuple(supports[rid] for rid in route_ids)
            ids = tuple(sorted({tid for group in groups for tid in group}))
            value = dict(kind='tier2_conflict', commitment_ids=ids,
                paper_ids=tuple(sorted({rows[tid]['source_id'] for tid in ids})), support_groups=groups,
                route_ids=route_ids, finding='Opposing CLOSED routes from paired engine analysis; resolve these supported conclusions: ' +
                    canonical(dict(positive=analysis.target.target.to_dict(), negative=analysis.negated.target.to_dict(),
                                   first_flagged=conflict.first_flagged.to_dict() if conflict.first_flagged else None)))
            gap = Gap('gap:' + digest(canonical(value)), **value)
            gaps[gap.id] = gap
    return tuple(gaps[k] for k in sorted(gaps))


def propose_tier2_resolutions(calls, analyses, commitments, provenance):
    gaps = tier2_gaps(analyses, commitments, provenance)
    identity = digest(canonical([a.to_dict() for a in analyses]))
    calls.log.record('tier2_resolution_gaps', analyses_sha256=identity, gaps=[g.to_dict() for g in gaps],
        status='verified' if provenance is not None else 'unavailable_legacy',
        note='Engine findings remain authoritative; gaps are resolution obligations, not edits to T.')
    candidates = calls.propose_gap_targets(commitments, gaps, calls.config['target_candidates']) if gaps else ()
    calls.log.record('tier2_resolution_candidates', analyses_sha256=identity,
                     candidates=[p.to_dict() for p in candidates], status='proposed_not_searched',
                     note='These candidates passed target gates. No route, closure, or resolved conflict is claimed.')


def conflict_report(events):
    boundary = max((i for i,e in enumerate(events)
                    if e['stage'] in ('analysis_started','search_publication_started')), default=-1)
    findings = [(i,json.loads(e['payload_json'])) for i,e in enumerate(events)
                if i > boundary and e['stage']=='conflicts_and_robustness']
    finding_index, latest = findings[-1] if findings else (len(events), {})
    analyses = latest.get('findings', {}).get('analyses', [])
    tiers = {tier:[dict(target_id=a['target']['target']['id'], **finding)
                   for a in analyses for finding in a.get(tier, [])] for tier in ('tier1','tier2')}
    identity = digest(canonical(analyses))
    resolutions = [json.loads(e['payload_json']) for i,e in enumerate(events)
                   if i > finding_index and e['stage']=='tier2_resolution_candidates']
    resolutions = [p for p in resolutions if p.get('analyses_sha256')==identity]
    semantic = [json.loads(e['payload_json']) for e in events if e['stage']=='semantic_pair_classified']
    support_conflicts = _support_conflict_receipt(events)
    return dict(**tiers, counts={tier:len(values) for tier,values in tiers.items()},
        support_conflicts=support_conflicts['gaps'] if support_conflicts else [],
        analysis_status='recorded_bounded_analyses' if findings else 'not_recorded',
        analyses_count=len(analyses),
        resolution_candidates=resolutions[-1]['candidates'] if resolutions else [],
        resolution_status=resolutions[-1]['status'] if resolutions else 'not_recorded',
        semantic_classifications=semantic,
        note='Tier 1 repairs are proposals, not edits to frozen T. Tier 2 records opposing CLOSED routes. '
             'Missing or partial analyses are not evidence of no conflicts. Semantic judgments are not formal contradictions.')
