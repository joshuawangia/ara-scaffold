"""Syntactic structure receipts; never infer semantic equivalence from text."""
from __future__ import annotations

from ara.runtime.construction import formula_symbols
from ara.types import CommitmentSet, Formula


def conditional(formula: Formula) -> Formula | None:
    while formula.op in ('forall', 'exists'):
        formula = formula.args[0]
    return formula if formula.op == 'implies' else None


def conjuncts(formula: Formula) -> set[str]:
    if formula.op == 'and':
        return set().union(*(conjuncts(arg) for arg in formula.args))
    return {formula.canonical()}


def structure_gate(commitments: CommitmentSet, prior: CommitmentSet, items: dict) -> dict:
    """Exact endpoint reuse is observable; semantic faithfulness is not certified."""
    current = commitments.commitments
    formulas = {c.id: c.formula for c in (*prior.commitments, *current)}
    uses = {}
    for id, formula in formulas.items():
        for signature in set(formula_symbols(formula)):
            uses.setdefault(signature, set()).add(id)
    bindings = [(c.id, s) for c in current for s in set(formula_symbols(c.formula))]
    reused = sum(len(uses[s]) > 1 for _, s in bindings)
    non_atomic = sum(c.formula.op not in ('atom', 'predicate') for c in current)
    inference_ids = [c.id for c in current if items[c.id]['kind'] == 'inference']
    links, issues = [], []
    for c in current:
        implication = conditional(c.formula)
        if implication is None:
            if c.id in inference_ids:
                issues.append(dict(evidence_id=c.id, reason='inference_requires_conditional'))
            continue
        antecedent, consequent = map(conjuncts, implication.args)
        sides = [sorted(id for id, f in formulas.items() if id != c.id and conjuncts(f) <= side)
                 for side in (antecedent, consequent)]
        links.append(dict(evidence_id=c.id, antecedent_ids=sides[0], consequent_ids=sides[1],
                          connected=bool(sides[0] and sides[1])))
        if c.id in inference_ids:
            item = items[c.id]
            for side, ids in ((antecedent, item['premise_ids']), (consequent, [item['conclusion_id']])):
                for id in ids:
                    if id in formulas and not conjuncts(formulas[id]) <= side:
                        issues.append(dict(evidence_id=c.id, endpoint_id=id,
                                           reason='conditional_must_reuse_selected_endpoint_formula'))
    flat = bool(inference_ids) and non_atomic == 0
    return dict(commitments=len(current), inference_items=len(inference_ids),
                inference_fraction=len(inference_ids) / len(current) if current else 0,
                non_atomic_formulas=non_atomic, non_atomic_fraction=non_atomic / len(current) if current else 0,
                symbol_bindings=len(bindings), reused_symbol_bindings=reused,
                symbol_reuse_rate=reused / len(bindings) if bindings else 0,
                conditionals=links, connected_conditionals=sum(link['connected'] for link in links),
                flat=flat, passed=not issues, issues=issues,
                note='Syntactic counts and exact conjunct endpoints only; model-authored reuse is not semantic proof.')
