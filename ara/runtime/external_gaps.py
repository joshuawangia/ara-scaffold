"""Logged external AI gap hypotheses, bound to current frozen source evidence."""
import json
from pathlib import Path

from ara.runtime.cache import canonical, digest
from ara.types import Gap


def load_external_gaps(calls, commitments, vocabulary):
    filename = calls.config.get('gap_file')
    if filename is None:
        return ()
    path = Path(filename).expanduser().resolve()
    raw = path.read_text(encoding='utf-8')
    document = json.loads(raw)
    if (not isinstance(document, dict) or set(document) != {'schema_version','gaps'}
            or document['schema_version'] != 'external-gaps-v1' or not isinstance(document['gaps'],list)):
        raise ValueError('invalid external gap file envelope')
    provenance = vocabulary['commitment_provenance']
    if provenance is None:
        raise ValueError('external gaps require verified source provenance')
    rows = provenance['commitments']
    gaps, seen = [], set()
    required = {'id','origin','priority','finding','paper_ids','commitment_ids','support_groups',
                'evidence','currency_verdict','search_scope','claim_framing'}
    for record in document['gaps']:
        if not isinstance(record,dict) or set(record) != required:
            raise ValueError('invalid external gap record fields')
        if (any(not isinstance(record[k],str) or not record[k].strip() for k in
                ('id','finding','currency_verdict','search_scope','claim_framing'))
                or record['origin'] != 'AI-found' or type(record['priority']) is not int
                or record['priority'] < 0 or record['id'] in seen
                or not isinstance(record['evidence'],list) or not record['evidence']):
            raise ValueError('invalid external gap evidence or priority')
        seen.add(record['id'])
        gap = Gap('external:'+record['id'], 'external_gap', record['commitment_ids'],
                  record['paper_ids'], record['support_groups'], finding=record['finding'],
                  external_evidence_json=canonical(dict(record=record,source_path=str(path),file_sha256=digest(raw))))
        if (not gap.commitment_ids or not gap.paper_ids or len(set(gap.paper_ids)) != len(gap.paper_ids)
                or any(commitments.get(tid) is None for tid in gap.commitment_ids)
                or set(gap.paper_ids) != {rows[tid]['source_id'] for tid in gap.commitment_ids}
                or len(gap.support_groups) != len(gap.paper_ids)):
            raise ValueError('external gap source binding mismatch')
        for paper,group in zip(gap.paper_ids,gap.support_groups,strict=True):
            if not group or any(tid not in rows or rows[tid]['stance'] != 'endorsed'
                                or rows[tid]['source_id'] != paper for tid in group):
                raise ValueError('external gap requires endorsed support from each paper')
        if any(not isinstance(e,dict) or set(e) != {'source_id','location','finding'}
               or any(not isinstance(v,str) or not v.strip() for v in e.values()) for e in record['evidence']):
            raise ValueError('invalid external gap evidence references')
        gaps.append((record['priority'],gap))
    gaps.sort(key=lambda item:(item[0],item[1].id))
    calls.log.record('external_gaps_loaded',source_path=str(path),file_sha256=digest(raw),document=document,
        commitments_sha256=vocabulary['commitments_sha256'],provenance_sha256=vocabulary['provenance_sha256'],
        ordered_gap_ids=[gap.id for _,gap in gaps],
        note='AI-found hypotheses prioritized by the operator; evidence and currency verdict are supplied claims, not source endorsement or proof of novelty.')
    return tuple(gap for _,gap in gaps)
