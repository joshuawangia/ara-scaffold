"""Lossless unions of verified completed snapshots; no source-content inference."""
from ara.runtime.cache import canonical, digest
from ara.runtime.grounding import references

VERSION = 'completed-snapshot-union-v1'
GRAPH_FIELDS = ('schema_version', 'source_id', 'items', 'obligations', 'resolutions', 'dispositions')


def graph(outcome):
    return {key: outcome[key] for key in GRAPH_FIELDS}


def snapshot_id(outcome):
    # Re-grounding and publication upgrades do not create new source snapshots.
    return digest(canonical({k: v for k, v in outcome.items()
                             if k not in ('grounding', 'quarantined', 'publication_policy')}))


def unite(entries, acceptance):
    """Input entries are unique original snapshots with verified origin pins.

    Conflicting IDs and their reverse-reference closure stay snapshot-qualified.
    Identical text with distinct original IDs is never deduplicated. An identical
    referring item must also remain separate when its endpoints differ by snapshot.
    """
    from ara.runtime.extraction import ExtractedItem
    snapshots = sorted(entries)
    source = entries[snapshots[0]]['outcome']['source_id']
    variants, dependencies, incoming_contexts = {}, {}, {}
    for entry in entries.values():
        by_id = {i['id']: i for i in entry['outcome']['items']}
        incoming = {id: set() for id, item in by_id.items() if item['kind'] == 'inference'}
        for item in by_id.values():
            refs = references(item)
            if not refs <= by_id.keys():
                raise ValueError('snapshot union unknown item reference')
            dependencies.setdefault(item['id'], set()).update(refs)
            # Incoming qualifiers constrain an inference even without a reciprocal edge.
            for target in refs:
                if by_id[target]['kind'] == 'inference':
                    dependencies.setdefault(target, set()).add(item['id'])
                    incoming[target].add(item['id'])
            variants.setdefault(item['id'], set()).add(canonical(item))
        for id, refs in incoming.items():
            incoming_contexts.setdefault(id, set()).add(frozenset(refs))
    qualified = {id for id, bodies in variants.items() if len(bodies) > 1}
    # A qualifier present in only one snapshot must not constrain shared evidence.
    qualified.update(id for id, contexts in incoming_contexts.items() if len(contexts) > 1)
    while True:
        added = {id for id, refs in dependencies.items() if refs & qualified} - qualified
        if not added:
            break
        qualified |= added
    items, provenance, manifests = {}, {}, {}
    obligations, resolutions, dispositions = [], [], []
    for sid in snapshots:
        entry = entries[sid]
        outcome = entry['outcome']
        mapping = {i['id']: (f'{source}:union:snapshot:{sid}:{i["id"]}' if i['id'] in qualified
                             else f'{source}:union:item:{i["id"]}') for i in outcome['items']}
        for original in outcome['items']:
            item = {k: v for k, v in original.items() if k != 'citation'}
            item['id'] = mapping[original['id']]
            for field in ('premise_ids', 'qualification_ids', 'applies_to'):
                item[field] = [mapping[id] for id in original[field]]
            item['conclusion_id'] = mapping[original['conclusion_id']] if original['conclusion_id'] else None
            item['citation'] = ExtractedItem(**item).citation
            if item['id'] in items and items[item['id']] != item:
                raise ValueError('snapshot union conflicting mapped item')
            items[item['id']] = item
            provenance.setdefault(item['id'], []).append(dict(snapshot_id=sid, original_id=original['id'],
                item_sha256=digest(canonical(original)), original_citation=original['citation']))
        gap_ids = {o['id']: f'{source}:union:snapshot:{sid}:gap:{o["id"]}' for o in outcome['obligations']}
        obligations.extend({**o, 'id': gap_ids[o['id']], 'snapshot_id': sid, 'original_id': o['id']}
                           for o in outcome['obligations'])
        resolutions.extend({**r, 'obligation_id': gap_ids[r['obligation_id']],
                            'evidence_ids': [mapping[id] for id in r['evidence_ids']]}
                           for r in outcome['resolutions'])
        dispositions.extend({**d, 'snapshot_id': sid} for d in outcome['dispositions'])
        manifests[sid] = dict(graph_sha256=digest(canonical(graph(outcome))),
                              acceptance_identity=outcome['acceptance_identity'],
                              origins=sorted(entry['origins'], key=canonical))
    base = {k: v for k, v in entries[snapshots[0]]['outcome'].items()
            if k not in (*GRAPH_FIELDS, 'grounding', 'quarantined', 'reason', 'publication_policy')}
    partial = any(entry['outcome']['status'] == 'partial' for entry in entries.values())
    return {**base, 'schema_version': 2, 'source_id': source, 'status': 'partial' if partial else 'extracted',
            'acceptance_identity': acceptance, 'range_union_policy': True,
            'items': [items[id] for id in sorted(items)], 'obligations': obligations,
            'resolutions': resolutions, 'dispositions': dispositions,
            'item_provenance': {id: provenance[id] for id in sorted(provenance)},
            'snapshot_union': dict(version=VERSION, snapshots=manifests,
                note='Union of verified accepted snapshots. Original bodies remain in pinned ancestry; IDs, citations and references are mapped explicitly. Gaps and dispositions remain snapshot-scoped.')}
