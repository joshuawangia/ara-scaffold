"""Frozen construction vocabulary, content-addressed and bound to exact T.

The legacy commitments.json and CommitmentSet codec are unchanged. Search reads
this optional envelope; absence means no recorded semantic catalogue.
"""
from __future__ import annotations

from ara.runtime.cache import canonical, digest
from ara.types import CommitmentSet


def make_catalogue(commitments: CommitmentSet, symbols: list[dict]) -> dict:
    from ara.runtime.construction import formula_symbols

    normalized = []
    ids = {c.id for c in commitments.commitments}
    signatures = {}
    for symbol in symbols:
        if set(symbol) != {'name', 'kind', 'arity', 'definition', 'evidence_ids'}:
            raise ValueError('invalid catalogue symbol fields')
        name, kind, arity = symbol['name'], symbol['kind'], symbol['arity']
        evidence = symbol['evidence_ids']
        if (not isinstance(name, str) or not name or name in signatures or
                kind not in ('atom', 'predicate', 'constant') or type(arity) is not int or
                arity < 0 or (kind != 'predicate' and arity != 0) or
                not isinstance(symbol['definition'], str) or not symbol['definition'].strip() or
                not isinstance(evidence, list) or not evidence or
                any(not isinstance(id, str) or id not in ids for id in evidence)):
            raise ValueError('invalid catalogue symbol definition')
        signatures[name] = (kind, arity)
        normalized.append({**symbol, 'evidence_ids': sorted(set(evidence))})
    used = {}
    for commitment in commitments.commitments:
        for name, kind, arity in formula_symbols(commitment.formula):
            if name in used and used[name] != (kind, arity):
                raise ValueError('conflicting frozen symbol signature')
            used[name] = (kind, arity)
    if signatures != used:
        raise ValueError('catalogue does not cover exact frozen vocabulary')
    payload = dict(schema_version='symbol-catalogue-v1',
                   commitments_sha256=digest(canonical(commitments.to_dict())),
                   symbols=sorted(normalized, key=lambda s: s['name']))
    sha256 = digest(canonical(payload))
    return {**payload, 'catalogue_id': 'sha256:' + sha256, 'sha256': sha256}


def frozen_artifact(commitments: CommitmentSet, symbols: list[dict]) -> dict:
    return dict(schema_version='frozen-t-v1', commitments=commitments.to_dict(),
                symbol_catalogue=make_catalogue(commitments, symbols))


def validate_frozen_artifact(value: dict, commitments: CommitmentSet) -> dict:
    """Return verified catalogue; reject corrupt/mismatched metadata, never downgrade."""
    if (set(value) != {'schema_version', 'commitments', 'symbol_catalogue'} or
            value['schema_version'] != 'frozen-t-v1' or value['commitments'] != commitments.to_dict()):
        raise ValueError('frozen T artifact mismatch')
    catalogue = value['symbol_catalogue']
    if not isinstance(catalogue, dict) or not isinstance(catalogue.get('symbols'), list):
        raise ValueError('invalid frozen symbol catalogue')
    expected = make_catalogue(commitments, catalogue['symbols'])
    if catalogue != expected:
        raise ValueError('frozen catalogue hash or canonical payload mismatch')
    return expected
