"""Content-definition provenance bound to exact frozen commitments and vocabulary."""
from __future__ import annotations

import json
from pathlib import Path

from ara.runtime.cache import canonical, digest
from ara.runtime.frozen_catalogue import make_catalogue
from ara.types import CommitmentSet

STANCES = {'author_claim': 'endorsed', 'reported_view': 'reported', 'attacked_view': 'attacked'}
SOURCE_KINDS = {'premise', 'intermediate_conclusion', 'conclusion', 'inference',
                'distinction', 'qualification', 'reported_view', 'attacked_view'}
SOURCE_FIELDS = {'source_id', 'source_authors', 'attributed_to', 'page_start', 'page_end',
                 'evidence_id', 'attribution', 'stance', 'source_kind', 'source_text', 'omitted_support_ids'}
FIELDS = {'schema_version', 'definition_semantics', 'commitments_sha256', 'catalogue_sha256',
          'commitments', 'sha256'}


def content_definition(text: str) -> bool:
    # One lexicon shared with search; lexical screening is not semantic proof.
    from ara.runtime.target_policy import attributed_report
    return isinstance(text, str) and bool(text.strip()) and not attributed_report(text)


def source_provenance(item: dict, authors: list[str], omitted_support_ids=()) -> dict:
    return dict(source_id=item['source_id'], source_authors=list(authors),
                attributed_to=item['attributed_to'], page_start=item['page_start'], page_end=item['page_end'],
                evidence_id=item['id'], attribution=item['attribution'], stance=STANCES[item['attribution']],
                source_kind=item['kind'], source_text=item['text'],
                omitted_support_ids=sorted(set(omitted_support_ids)))


def _validate_source(id, row):
    if not isinstance(row, dict) or set(row) != SOURCE_FIELDS:
        raise ValueError('invalid commitment provenance fields')
    if (any(not isinstance(row[k], str) or not row[k].strip() for k in
            ('source_id', 'attributed_to', 'evidence_id', 'attribution', 'stance', 'source_kind', 'source_text')) or
            row['evidence_id'] != id or row['source_kind'] not in SOURCE_KINDS or
            row['attribution'] not in STANCES or row['stance'] != STANCES[row['attribution']] or
            (row['source_kind'] in ('reported_view', 'attacked_view') and row['source_kind'] != row['attribution'])):
        raise ValueError('invalid commitment provenance stance or evidence')
    if (type(row['page_start']) is not int or type(row['page_end']) is not int or
            not 1 <= row['page_start'] <= row['page_end']):
        raise ValueError('invalid commitment provenance pages')
    for key in ('source_authors', 'omitted_support_ids'):
        if not isinstance(row[key], list) or any(not isinstance(s, str) or not s.strip() for s in row[key]):
            raise ValueError('invalid commitment provenance source list')
    if row['omitted_support_ids'] != sorted(set(row['omitted_support_ids'])):
        raise ValueError('noncanonical omitted support ids')


def validate_commitment_provenance(value: dict, commitments: CommitmentSet, catalogue: dict) -> dict:
    """Verify the full sidecar; absence is handled only by the loader."""
    if (not isinstance(value, dict) or set(value) != FIELDS or
            value['schema_version'] != 'commitment-provenance-v1' or value['definition_semantics'] != 'content'):
        raise ValueError('invalid commitment provenance schema')
    if (not isinstance(catalogue, dict) or not isinstance(catalogue.get('symbols'), list) or
            catalogue != make_catalogue(commitments, catalogue['symbols'])):
        raise ValueError('commitment provenance requires verified catalogue')
    if (value['commitments_sha256'] != digest(canonical(commitments.to_dict())) or
            value['catalogue_sha256'] != catalogue['sha256']):
        raise ValueError('commitment provenance binding mismatch')
    payload = {k: v for k, v in value.items() if k != 'sha256'}
    if value['sha256'] != digest(canonical(payload)):
        raise ValueError('commitment provenance hash mismatch')
    if not isinstance(value['commitments'], dict) or set(value['commitments']) != {c.id for c in commitments.commitments}:
        raise ValueError('commitment provenance inventory mismatch')
    for id, row in value['commitments'].items():
        _validate_source(id, row)
    if (not all(content_definition(c.text) for c in commitments.commitments) or
            not all(content_definition(s['definition']) for s in catalogue['symbols'])):
        raise ValueError('attribution in content definition')
    return value


def make_commitment_provenance(commitments: CommitmentSet, catalogue: dict, provenance: dict) -> dict:
    payload = dict(schema_version='commitment-provenance-v1', definition_semantics='content',
                   commitments_sha256=digest(canonical(commitments.to_dict())),
                   catalogue_sha256=catalogue['sha256'], commitments=provenance)
    return validate_commitment_provenance({**payload, 'sha256': digest(canonical(payload))}, commitments, catalogue)


def load_commitment_provenance(directory: Path, commitments: CommitmentSet, catalogue: dict | None) -> dict | None:
    path = directory / 'commitment-provenance.json'
    if not path.exists():
        return None
    return validate_commitment_provenance(json.loads(path.read_text()), commitments, catalogue)
