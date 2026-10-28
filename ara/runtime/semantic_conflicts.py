"""Rank cross-paper content pairs; model judgments never alter formal frozen T."""
from heapq import nsmallest
from itertools import combinations
import re

from ara.runtime.bridges import _STOP_WORDS
from ara.runtime.cache import canonical, digest
from ara.runtime.search_alignment import symbols
from ara.types import Gap


def words(text):
    return set(re.findall(r"\b[^\W\d_][\w'-]*\b", text.casefold())) - _STOP_WORDS


def rank_pairs(commitments, catalogue, provenance, limit):
    if type(limit) is not int or limit < 0:
        raise ValueError('semantic_conflict_pair_limit must be a nonnegative integer')
    policy = dict(limit=limit, ranking='topic_definition_overlap_then_content_overlap_then_ids',
                  topic_method='shared_terms_in_catalogue_definitions',
                  roles='at_least_one_endorsed; other_endorsed_reported_or_attacked')
    if catalogue is None or provenance is None:
        return dict(**policy, status='unavailable_legacy', eligible_pairs=0, pairs=[])
    rows = provenance['commitments']
    definitions = {(s['name'], s['kind'], s['arity']): s['definition'] for s in catalogue}
    features = {}
    for c in commitments.commitments:
        topic = words(' '.join(definitions[s] for s in symbols(c.formula) if s in definitions))
        features[c.id] = (topic, words(c.text) | topic)
    eligible = 0
    def candidates():
        nonlocal eligible
        for a, b in combinations(sorted(commitments.commitments, key=lambda c: c.id), 2):
            if rows[a.id]['source_id'] == rows[b.id]['source_id']:
                continue
            if 'endorsed' not in (rows[a.id]['stance'], rows[b.id]['stance']):
                continue
            topic = len(features[a.id][0] & features[b.id][0])
            lexical = len(features[a.id][1] & features[b.id][1])
            if not lexical:
                continue
            eligible += 1
            yield dict(commitment_ids=[a.id, b.id], topic_overlap=topic, lexical_overlap=lexical)
    pairs = nsmallest(limit, candidates(), key=lambda p: (-p['topic_overlap'], -p['lexical_overlap'], p['commitment_ids'])) if limit else []
    return dict(**policy, status='ranked' if limit else 'disabled', eligible_pairs=eligible, pairs=pairs)


def classify_pairs(calls, commitments, vocabulary):
    catalogue, provenance = vocabulary['symbol_catalogue'], vocabulary['commitment_provenance']
    ranking = rank_pairs(commitments, catalogue, provenance, calls.config.get('semantic_conflict_pair_limit', 60))
    calls.log.record('semantic_pairs_ranked', **ranking, commitments_sha256=vocabulary['commitments_sha256'],
                     catalogue_sha256=vocabulary['catalogue_sha256'], provenance_sha256=vocabulary['provenance_sha256'])
    gaps = []
    rows = provenance['commitments'] if provenance else {}
    for candidate in ranking['pairs']:
        pair = []
        for tid in candidate['commitment_ids']:
            c = commitments.get(tid)
            used = set(symbols(c.formula))
            pair.append(dict(commitment_id=tid, content=c.text, formula=c.formula.to_dict(),
                source_id=rows[tid]['source_id'], stance=rows[tid]['stance'], attributed_to=rows[tid]['attributed_to'],
                definitions=[s for s in catalogue if (s['name'],s['kind'],s['arity']) in used]))
        inputs = dict(topic='', pair=pair, commitments_sha256=vocabulary['commitments_sha256'],
            catalogue_sha256=vocabulary['catalogue_sha256'], provenance_sha256=vocabulary['provenance_sha256'])
        try:
            result = calls.call('classify_conflict', inputs)
        except Exception as exc:
            from ara.runtime.search_jobs import job_failure
            if not job_failure(exc):
                raise
            calls.log.record('semantic_pair_failed', **candidate, reason=type(exc).__name__, status='unclassified')
            continue
        calls.log.record('semantic_pair_classified', **candidate, **result, formal_contradiction=False,
                         inputs_sha256=digest(canonical(inputs)))
        if result['classification'] not in ('contradicts', 'in_tension'):
            continue
        papers = tuple(sorted({rows[tid]['source_id'] for tid in candidate['commitment_ids']}))
        groups = []
        for paper in papers:
            restricted_side = any(rows[tid]['source_id'] == paper and rows[tid]['stance'] != 'endorsed'
                                  for tid in candidate['commitment_ids'])
            groups.append(tuple(sorted(c.id for c in commitments.commitments
                if rows[c.id]['source_id'] == paper and rows[c.id]['stance'] == 'endorsed'
                and (c.id in candidate['commitment_ids'] or restricted_side))))
        value = dict(kind='semantic_conflict', commitment_ids=tuple(candidate['commitment_ids']), paper_ids=papers,
                     support_groups=tuple(groups), finding=result['classification'] + ': ' + result['reason'])
        gap = Gap('gap:' + digest(canonical(value)), **value)
        gaps.append(gap)
        calls.log.record('semantic_gap_detected', gap=gap.to_dict(), formal_contradiction=False)
    return tuple(gaps)
