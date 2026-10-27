"""Search vocabulary and explicit frozen-reference bindings, without provider effects."""
from __future__ import annotations

import json
from ara.runtime.cache import canonical, digest
from ara.runtime.frozen_catalogue import validate_frozen_artifact
from ara.types import Formula, Proposition


def symbols(formula):
    if formula.op in ('atom', 'predicate'):
        yield formula.name, formula.op, len(formula.terms)
    for term in formula.terms:
        if term.kind == 'constant':
            yield term.name, 'constant', 0
    for arg in formula.args:
        yield from symbols(arg)


def catalogue_inputs(directory, commitments):
    from ara.runtime.commitment_provenance import load_commitment_provenance
    path = directory / 'frozen-t.json'
    catalogue = validate_frozen_artifact(json.loads(path.read_text()), commitments) if path.exists() else None
    provenance = load_commitment_provenance(directory, commitments, catalogue)
    return dict(symbol_catalogue=catalogue['symbols'] if catalogue else None,
                catalogue_sha256=catalogue['sha256'] if catalogue else None,
                catalogue_status='verified' if catalogue else 'unavailable_legacy',
                commitments_sha256=digest(canonical(commitments.to_dict())),
                commitment_provenance=provenance,
                provenance_sha256=provenance['sha256'] if provenance else None,
                provenance_status='verified' if provenance else 'unavailable_legacy',
                definition_semantics='content' if provenance else 'unavailable_legacy')


def slot_bindings(proposal, commitments):
    from ara.runtime.calls import require
    result = []
    for fill in proposal.premises:
        formula = None
        if fill.t_id != 'open':
            commitment = commitments.get(fill.t_id)
            require(commitment is not None, 'unknown proposal T id: ' + fill.t_id)
            require(fill.text == commitment.text, 'proposal T reference text mismatch: ' + fill.t_id)
            formula = commitment.formula.to_dict()
        result.append(dict(slot=fill.slot, text=fill.text, t_id=fill.t_id,
                           scope_id=fill.scope_id, formula=formula))
    return result


def validate_slots(data, proposal, entry, bindings, catalogue):
    from ara.runtime.calls import require
    slots = data['slots']
    expected = [s.id for s in entry.premise_slots]
    require(len(slots) == len(expected) and {s['slot'] for s in slots} == set(expected),
            'joint formalization slot inventory mismatch')
    formulas = {s['slot']: Formula.from_dict(s['formula']) for s in slots}
    by_slot = {b['slot']: b for b in bindings}
    signatures = {s['name']: (s['kind'], s['arity']) for s in catalogue or []}
    for slot, formula in formulas.items():
        bound = by_slot[slot]['formula']
        require(bound is None or formula.canonical() == Formula.from_dict(bound).canonical(),
                'joint formalization changed frozen slot binding: ' + slot)
        for name, kind, arity in symbols(formula):
            require(name not in signatures or signatures[name] == (kind, arity),
                    'joint formalization symbol signature mismatch: ' + name)
    return tuple(Proposition(slot, by_slot[slot]['text'], formulas[slot]) for slot in expected)


def metavariable_bindings(entry, goal, bindings):
    """Bounded candidate substitutions for one sequent; licensing remains authoritative."""
    from itertools import islice
    from ara.engine.matching import match
    schema = entry.formula_schema
    if schema is None:
        return []
    envs = list(islice(match(schema.conclusion, goal.formula, schema), 8))
    fixed = {b['slot']: Formula.from_dict(b['formula']) for b in bindings if b['formula'] is not None}
    for premise in schema.premises:
        if premise.slot in fixed:
            envs = list(islice((candidate for env in envs for candidate in
                match(premise.formula, fixed[premise.slot], schema, env)), 8))
    return [dict(formulas={k: v.to_dict() for k, v in fs.items()},
                 terms={k: v.to_dict() for k, v in ts.items()}) for fs, ts in envs]
