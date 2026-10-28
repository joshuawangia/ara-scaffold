"""Bounded cross-paper candidates from verified frozen metadata, not semantic proof."""
from collections import defaultdict
from itertools import combinations, islice, product
import re

from ara.runtime.cache import canonical, digest

_STOP_WORDS = frozenset('a an the and or not of to in on for from with by as at is are be that this it its'.split())


def paper_support(formula_supports, provenance):
    rows = provenance['commitments'] if provenance else {}
    formula_supports = [{**group, 'support_ids': [tid for tid in group['support_ids']
        if rows.get(tid, {}).get('stance') != 'model_alignment']} for group in formula_supports]
    formula_supports = [group for group in formula_supports if group['support_ids']]
    support_ids = sorted({tid for group in formula_supports for tid in group['support_ids']})
    sources = {tid: rows.get(tid, {}).get('source_id') for tid in support_ids}
    missing = sorted(tid for tid,source in sources.items() if not source)
    papers = sorted({source for source in sources.values() if source})
    groups = [dict(formula_hash=group['formula_hash'],
                   commitment_papers={tid: sources[tid] for tid in sorted(group['support_ids'])},
                   paper_ids=sorted({sources[tid] for tid in group['support_ids'] if sources[tid]}))
              for group in sorted(formula_supports, key=lambda group: group['formula_hash'])]
    matching = []
    # A size-two matching suffices: each formula chooses any cited paper, but
    # neither formula nor paper may be reused. Sorted candidates give a stable witness.
    if provenance is not None and not missing:
        for left, right in combinations(groups, 2):
            pair = next(((a, b) for a, b in product(left['paper_ids'], right['paper_ids']) if a != b), None)
            if pair is not None:
                matching = [dict(formula_hash=group['formula_hash'], paper_id=paper,
                                 commitment_id=next(tid for tid, source in group['commitment_papers'].items()
                                                    if source == paper))
                            for group, paper in zip((left, right), pair)]
                break
    return dict(status='unavailable_legacy' if provenance is None else 'unresolved' if missing else 'verified',
                paper_ids=papers, paper_count=len(papers), minimum_papers=2,
                commitment_papers=sources, missing_support_ids=missing, formula_supports=groups,
                matching=matching, cross_paper_supported=len(matching) == 2)


def bridge_context(commitments, catalogue, provenance):
    from ara.runtime.search_alignment import symbols
    policy = dict(minimum_papers=2, pairs_limit=30, triples_limit=30, scan_limit=10000,
                  topic_method='exact_casefolded_catalogue_definition_terms', semantic_fit='unproved')
    result = dict(candidate_bridges=[], commitment_papers={}, bridge_policy=policy,
                  bridge_status='unavailable_legacy', bridges_truncated=False)
    if catalogue is None or provenance is None:
        return result
    rows = provenance['commitments']
    eligible = sorted((c for c in commitments.commitments
        if rows.get(c.id, {}).get('stance') == 'endorsed' and rows[c.id].get('source_id')), key=lambda c:c.id)
    papers = {c.id: rows[c.id]['source_id'] for c in eligible}
    definitions = {(s['name'],s['kind'],s['arity']):s['definition'] for s in catalogue}
    features, groups = {}, defaultdict(list)
    for c in eligible:
        used = set(symbols(c.formula)) & definitions.keys()
        terms = {term.casefold() for signature in used
                 for term in re.findall(r"\b[^\W\d_][\w'-]*\b",definitions[signature])} - _STOP_WORDS
        features[c.id] = {('symbol',*s) for s in used} | {('definition_term',t) for t in terms}
        for feature in features[c.id]:
            groups[feature].append(c.id)
    bridges, seen, truncated = [], set(), False
    for size in (2,3):
        limit = policy['pairs_limit' if size == 2 else 'triples_limit']
        accepted = scanned = 0
        for feature in sorted(groups, key=lambda f:(f[0]!='symbol',f)):
            by_paper = defaultdict(list)
            for tid in groups[feature]:
                by_paper[papers[tid]].append(tid)
            pairs = (pair for a,b in combinations(sorted(by_paper),2)
                     for pair in product(by_paper[a],by_paper[b]))
            candidates = pairs if size==2 else (tuple(sorted((*pair,third)))
                for pair in pairs for third in groups[feature] if third not in pair)
            for ids in islice(candidates,policy['scan_limit']-scanned):
                scanned += 1
                ids = tuple(sorted(ids))
                if ids in seen:
                    continue
                seen.add(ids)
                common = set.intersection(*(features[tid] for tid in ids))
                connections = [dict(kind=f[0],name=f[1],symbol_kind=f[2],arity=f[3]) if f[0]=='symbol'
                               else dict(kind=f[0],term=f[1]) for f in sorted(common)]
                payload = dict(commitment_ids=list(ids),paper_ids=sorted({papers[tid] for tid in ids}),
                               connections=connections)
                bridges.append(dict(bridge_id='bridge:'+digest(canonical(payload)),**payload))
                accepted += 1
                if accepted == limit:
                    break
            if accepted == limit or scanned == policy['scan_limit']:
                truncated = True
                break
    return dict(result,candidate_bridges=bridges,commitment_papers=papers,
                bridge_status='available' if bridges else 'no_shared_catalogue_features',bridges_truncated=truncated)


def proposal_bridge(proposal, context):
    papers = context['commitment_papers']
    slots = [dict(slot=p.slot,commitment_id=p.t_id,paper_id=papers.get(p.t_id))
             for p in proposal.premises if p.t_id != 'open' and p.scope_id is None]
    ids = {s['commitment_id'] for s in slots}
    return dict(bank_id=proposal.bank_id, bridge_ids=[b['bridge_id'] for b in context['candidate_bridges']
                if set(b['commitment_ids']) <= ids], paper_slots=slots,
                paper_ids=sorted({s['paper_id'] for s in slots if s['paper_id']}))
