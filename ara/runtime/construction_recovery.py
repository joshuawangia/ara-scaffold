"""Opt-in bounded construction recovery; no source or formula rewriting."""
from copy import deepcopy

from jsonschema import ValidationError

from ara.runtime.cache import canonical, digest
from ara.runtime.validation import decode_response, guard_complexity, validate_local
from ara.types import Formula

FLAGS = ('construction_partial_acceptance', 'construction_split_retry', 'construction_precise_attribution')


def recovery_policy(config):
    for name in FLAGS:
        if type(config.get(name, False)) is not bool:
            raise ValueError(name + ' must be boolean')
    if any(isinstance(stage, dict) and any(name in stage for name in FLAGS)
           for stage in config.get('stages', {}).values()):
        raise ValueError('construction recovery flags are run-level only')
    enabled = {name: True for name in FLAGS if config.get(name, False)}
    return dict(version='construction-recovery-v1', **enabled) if enabled else None


def consistent(commitments, prior, items):
    """Each formula must be satisfiable; only endorsed rows are global premises."""
    from ara.runtime.symbol_alignment import _consistent
    from ara.types import CommitmentSet
    return (all(_consistent(CommitmentSet((c,))) for c in commitments.commitments) and
            _consistent(CommitmentSet(tuple(c for c in (*prior.commitments, *commitments.commitments)
                if items[c.id]['attribution'] == 'author_claim'))))


def partial_candidate(candidate, expected, materialized, dependencies, support_omitted,
                      check, prior, items, schema, config):
    """Stable-ID admission then dependency pruning; recheck the entire survivor set.

    Candidate rows are never repaired. Only irrelevant symbol/binding inventories
    and their evidence lists are projected onto the retained IDs, then revalidated.
    Conflicts preserve already accepted rows; order is disclosed, not relevance.
    """
    from ara.runtime.calls import Rejected, require
    from ara.runtime.construction import formula_symbols
    from ara.runtime.construction_structure import structure_gate
    require(isinstance(candidate, dict) and set(candidate) == {'commitments', 'new_symbols', 'alignments'} and
            all(isinstance(v, list) for v in candidate.values()), 'partial recovery requires a complete candidate envelope')
    def check_complexity(value):
        try:
            guard_complexity(value, config)
        except ValidationError as exc:
            raise Rejected('partial candidate complexity refused: ' + str(exc)) from exc
    # Projection must never turn an over-budget response into an admitted one.
    check_complexity(candidate)
    original_hash = digest(canonical(candidate))
    candidate = deepcopy(candidate)
    rows, dropped = {}, {}
    for id in sorted(expected):
        matches = [c for c in candidate['commitments'] if isinstance(c, dict) and c.get('id') == id]
        if len(matches) != 1:
            dropped[id] = 'missing or duplicate candidate commitment'
            continue
        row = matches[0]
        try:
            if isinstance(row.get('formula'), str): row['formula'] = decode_response(row['formula'])
            guard_complexity(row['formula'], config)
            tuple(formula_symbols(Formula.from_dict(row['formula'])))
        except (ValueError, KeyError, TypeError, RecursionError, ValidationError) as exc:
            dropped[id] = 'invalid formula: ' + str(exc)
            continue
        rows[id] = row
    check_complexity(candidate)

    def project(ids, tentative=False):
        used = {name for id in ids for name, _, _ in formula_symbols(Formula.from_dict(rows[id]['formula']))}
        symbols = []
        for symbol in candidate['new_symbols']:
            if isinstance(symbol, dict) and isinstance(symbol.get('name'), str) and symbol['name'] in used:
                # Do not invent an evidence binding for a surviving use.
                evidence = symbol.get('evidence_ids')
                symbols.append({**symbol, **({'evidence_ids': [id for id in evidence if tentative or id in ids or id not in expected]}
                                            if isinstance(evidence, list) else {})})
        return dict(commitments=[rows[id] for id in sorted(ids)], new_symbols=symbols,
                    alignments=[a for a in candidate['alignments'] if isinstance(a, dict) and
                                isinstance(a.get('name'), str) and a['name'] in used])

    def validate(ids, tentative=False):
        value = project(ids, tentative)
        validate_local(schema, value, config)
        return check(value, ids, symbol_scope=expected if tentative else None)

    kept = set()
    for id in sorted(rows):
        try:
            validate(kept | {id}, tentative=True)
        except (Rejected, ValueError, TypeError, ValidationError) as exc:
            dropped[id] = 'item validation: ' + str(exc)
        else:
            kept.add(id)
    while kept:
        orphaned = {s['name'] for s in project(kept)['new_symbols'] if not s['evidence_ids']}
        orphan_users = {id for id in kept if orphaned.intersection(
            name for name, _, _ in formula_symbols(Formula.from_dict(rows[id]['formula'])))}
        for id in orphan_users:
            dropped[id] = 'symbol evidence dropped: ' + ', '.join(sorted(orphaned))
        if orphan_users:
            kept -= orphan_users
            continue
        missing = {id: dependencies[id] - set(support_omitted.get(id, [])) - kept - materialized for id in kept}
        invalid = {id for id, missing_ids in missing.items() if missing_ids}
        for id in sorted(invalid):
            dropped[id] = 'required dependency dropped: ' + ', '.join(sorted(missing[id]))
        if invalid:
            kept -= invalid
            continue
        result = validate(kept)
        metrics = structure_gate(result.commitments, prior, items)
        invalid = {issue['evidence_id'] for issue in metrics['issues']}
        if invalid:
            for id in invalid: dropped[id] = 'inference structure validation failed'
            kept -= invalid
            continue
        retained = project(kept)
        receipt = dict(policy='validated_subset_stable_id_order_v1', candidate_sha256=original_hash,
            retained_ids=sorted(kept), dropped=[dict(evidence_id=id, reason=dropped[id]) for id in sorted(dropped)],
            discarded_symbols=[s.get('name') if isinstance(s, dict) else None for s in candidate['new_symbols']
                               if s not in retained['new_symbols']],
            discarded_unknown_ids=[c.get('id') if isinstance(c, dict) else None for c in candidate['commitments']
                                   if not isinstance(c, dict) or not isinstance(c.get('id'), str) or c['id'] not in expected])
        return result, metrics, receipt
    raise Rejected('partial recovery has no dependency-safe validated commitments')
