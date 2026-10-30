"""Content-definition provenance bound to exact frozen commitments and vocabulary."""
from __future__ import annotations

import json
import re
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


PRECISE_SCREEN = 'attribution-frames-v1'
# Ambiguous verbs require an explicit report frame. Other attribution markers
# remain conservative; this screen is not a semantic authorship judgment.
_PRECISE_ATTRIBUTION = re.compile(
    r"\b(argues?|claims?|contends?|reports?|asserts?|suggests?|proposes?|believes?|"
    r"defends?|endorses?|says?|thinks?)\b|\b(?:holds?|maintains?|states?)\s+that\b|"
    r"\baccording\s+to\b|\bon\s+.+?[’']s\s+account\b|"
    r"[’']s\s+(view|position|thesis|claim|belief|account)\b", re.I)


def content_definition(text: str, *, screen: str | None = None) -> bool:
    # One lexicon shared with search; lexical screening is not semantic proof.
    from ara.runtime.target_policy import attributed_report
    if screen not in (None, PRECISE_SCREEN):
        raise ValueError('unknown content definition screen')
    attributed = _PRECISE_ATTRIBUTION.search if screen == PRECISE_SCREEN else attributed_report
    return isinstance(text, str) and bool(text.strip()) and not attributed(text)


def definition_issues(data: dict, *, screen: str | None = None) -> list[dict]:
    from ara.runtime.target_policy import _ATTRIBUTION
    issues = []
    for field, kind, key in (('commitments', 'commitment', 'id'), ('new_symbols', 'symbol', 'name')):
        for entry in data[field]:
            text = entry['definition']
            if not content_definition(text, screen=screen):
                issues.append(dict(kind=kind, name=entry[key],
                                   phrases=[m.group() for m in _ATTRIBUTION.finditer(text)]))
    return issues


def exact_unframe(text: str, authors: list[str]) -> dict | None:
    for author in sorted(set(authors), key=lambda a: (-len(a), a)):
        match = re.fullmatch(re.escape(author) + r'\s+(?:argues|holds|claims)\s+that\s+(\S[\s\S]*)', text)
        if match:
            return dict(author=author, original_definition=text, definition=match[1].strip())
    return None


def unframe_definitions(data: dict, items: dict, authors: dict) -> list[dict]:
    changes = []
    for field, kind, key in (('commitments', 'commitment', 'id'), ('new_symbols', 'symbol', 'name')):
        for entry in data[field]:
            ids = [entry['id']] if kind == 'commitment' else entry['evidence_ids']
            known = [name for id in ids if id in items
                     for name in [items[id]['attributed_to'], *authors[items[id]['source_id']]]]
            change = exact_unframe(entry['definition'], known)
            if change:
                entry['definition'] = change['definition']
                changes.append(dict(kind=kind, name=entry[key], evidence_ids=sorted(set(ids)), **change))
    return changes


def source_provenance(item: dict, authors: list[str], omitted_support_ids=()) -> dict:
    return dict(source_id=item['source_id'], source_authors=list(authors),
                attributed_to=item['attributed_to'], page_start=item['page_start'], page_end=item['page_end'],
                evidence_id=item['id'], attribution=item['attribution'], stance=STANCES[item['attribution']],
                source_kind=item['kind'], source_text=item['text'],
                omitted_support_ids=sorted(set(omitted_support_ids)))


def _validate_source(id, row):
    if not isinstance(row, dict) or not SOURCE_FIELDS <= row.keys() or not row.keys() <= SOURCE_FIELDS | {'definition_unframes', 'definition_screen'}:
        raise ValueError('invalid commitment provenance fields')
    if 'definition_screen' in row and row['definition_screen'] != PRECISE_SCREEN:
        raise ValueError('invalid commitment definition screen')
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
    if 'definition_unframes' in row:
        history = row['definition_unframes']
        if not isinstance(history, list) or not history:
            raise ValueError('invalid definition unframing history')
        for change in history:
            if (not isinstance(change, dict) or set(change) !=
                    {'kind', 'name', 'author', 'original_definition', 'definition'} or
                    any(not isinstance(v, str) or not v.strip() for v in change.values()) or
                    change['kind'] not in ('commitment', 'symbol') or
                    (change['kind'] == 'commitment' and change['name'] != id) or
                    exact_unframe(change['original_definition'], [change['author']]) !=
                    {k: change[k] for k in ('author', 'original_definition', 'definition')}):
                raise ValueError('invalid definition unframing record')


def validate_commitment_provenance(value: dict, commitments: CommitmentSet, catalogue: dict) -> dict:
    """Verify the full sidecar; absence is handled only by the loader."""
    if (not isinstance(value, dict) or
            (value.get('schema_version'), frozenset(value)) not in (
                ('commitment-provenance-v1', frozenset(FIELDS)),
                ('commitment-provenance-v2', frozenset(FIELDS | {'alignment'})),
                ('commitment-provenance-v3', frozenset(FIELDS)),
                ('commitment-provenance-v3', frozenset(FIELDS | {'alignment'}))) or
            value['definition_semantics'] != 'content'):
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
    source_commitments, source_symbols = commitments, catalogue['symbols']
    if 'alignment' in value:
        from ara.runtime.symbol_alignment import validate_alignment
        source_commitments, source_symbols = validate_alignment(value['alignment'], commitments,
                                                               catalogue['symbols'], value['commitments'])
    for source in source_commitments.commitments:
        id, row = source.id, value['commitments'][source.id]
        _validate_source(id, row)
        for change in row.get('definition_unframes', []):
            if change['kind'] == 'symbol' and not any(
                    s['name'] == change['name'] and id in s['evidence_ids'] for s in source_symbols):
                raise ValueError('unframed symbol lacks evidence binding')
    policies = {row.get('definition_screen') for row in value['commitments'].values() if 'source_text' in row}
    if (PRECISE_SCREEN in policies) != (value['schema_version'] == 'commitment-provenance-v3'):
        raise ValueError('commitment definition screen version mismatch')
    def definition_ok(text, ids):
        source_ids = {source for id in ids for source in
                      (value['commitments'][id].get('evidence_ids', [id]))}
        screens = {value['commitments'][id].get('definition_screen') for id in source_ids}
        screen = PRECISE_SCREEN if screens == {PRECISE_SCREEN} else None
        return content_definition(text, screen=screen)
    if (not all(definition_ok(c.text, [c.id]) for c in source_commitments.commitments) or
            not all(definition_ok(s['definition'], s['evidence_ids']) for s in source_symbols) or
            not all(definition_ok(c.text, [c.id]) for c in commitments.commitments) or
            not all(definition_ok(s['definition'], s['evidence_ids']) for s in catalogue['symbols'])):
        raise ValueError('attribution in content definition')
    return value


def make_commitment_provenance(commitments: CommitmentSet, catalogue: dict, provenance: dict, *, alignment: dict | None = None) -> dict:
    payload = dict(schema_version='commitment-provenance-v1', definition_semantics='content',
                   commitments_sha256=digest(canonical(commitments.to_dict())),
                   catalogue_sha256=catalogue['sha256'], commitments=provenance)
    if alignment is not None:
        payload.update(schema_version='commitment-provenance-v2', alignment=alignment)
    if any('definition_screen' in row for row in provenance.values()):
        payload['schema_version'] = 'commitment-provenance-v3'
    return validate_commitment_provenance({**payload, 'sha256': digest(canonical(payload))}, commitments, catalogue)


def load_commitment_provenance(directory: Path, commitments: CommitmentSet, catalogue: dict | None) -> dict | None:
    path = directory / 'commitment-provenance.json'
    if not path.exists():
        return None
    return validate_commitment_provenance(json.loads(path.read_text()), commitments, catalogue)
