"""Resolve operator retrieval anchors against grounded evidence, never add claims."""


def resolve_anchors(config, papers):
    anchors = config.get('construction_gap_anchors', [])
    if not isinstance(anchors, list):
        raise ValueError('construction gap anchors must be a list')
    sources = {p['source_id']: {i['id']: i for i in p['items']} for p in papers}
    resolved, identities = [], set()
    for anchor in anchors:
        if (not isinstance(anchor, dict) or
                not {'gap_id', 'source_id'} <= anchor.keys() or
                not anchor.keys() <= {'gap_id', 'source_id', 'root_ids', 'page_ranges'} or
                any(not isinstance(anchor[k], str) or not anchor[k].strip() for k in ('gap_id', 'source_id'))):
            raise ValueError('invalid construction gap anchor fields')
        identity = (anchor['gap_id'], anchor['source_id'])
        if identity in identities:
            raise ValueError('duplicate construction gap anchor identity; combine its selectors')
        identities.add(identity)
        if anchor['source_id'] not in sources:
            raise ValueError('construction gap anchor source has no grounded evidence')
        items = sources[anchor['source_id']]
        roots, ranges = anchor.get('root_ids', []), anchor.get('page_ranges', [])
        if (not isinstance(roots, list) or any(not isinstance(r, str) for r in roots) or
                len(set(roots)) != len(roots) or not set(roots) <= items.keys()):
            raise ValueError('construction gap anchor roots must be unique grounded IDs in its source')
        if not isinstance(ranges, list) or (not roots and not ranges):
            raise ValueError('construction gap anchor requires root_ids or page_ranges')
        selected = set(roots)
        for span in ranges:
            if (not isinstance(span, list) or len(span) != 2 or
                    any(type(n) is not int for n in span) or not 0 < span[0] <= span[1]):
                raise ValueError('construction gap anchor page range must be [positive start, end]')
            hits = {id for id, item in items.items()
                    if item['page_start'] <= span[1] and item['page_end'] >= span[0]}
            if not hits:
                raise ValueError('construction gap anchor page range has no grounded evidence')
            selected.update(hits)
        resolved.append(dict(gap_id=anchor['gap_id'], source_id=anchor['source_id'],
            root_ids=sorted(roots), page_ranges=sorted(ranges), evidence_ids=sorted(selected),
            origin='operator_run_config', policy='grounded_evidence_priority_windows_v1'))
    return resolved


def window_anchor(anchor, ids):
    if anchor is None:
        return {}
    selected = set(ids)
    return {'gap_anchor': {**anchor, 'evidence_ids': sorted(selected),
        'root_ids': sorted(selected.intersection(anchor['root_ids'])),
        'instruction': 'Select required_root_ids when supplied. Page matches are retrieval candidates; '
                       'account for other omissions normally. This operator retrieval request supplies no '
                       'new source claim, endorsement or formalization. Preserve source stance and evidence.'}}
