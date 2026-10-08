"""Closure and exact disjoint-premise counts for engine-constructed routes."""
from __future__ import annotations

from dataclasses import replace
from functools import lru_cache

from ara.bank import Bank
from ara.types import CommitmentSet, CQAnswer, RouteGraph, RouteNode
from ara.engine.terminus import is_terminus


def cq_supported(answer: CQAnswer, question_id: str, commitments: CommitmentSet) -> bool:
    return (answer.cq_id == question_id and answer.answered and bool(answer.answer.strip())
            and bool(answer.supporting_t_ids)
            and all(commitments.get(tid) is not None for tid in answer.supporting_t_ids))


def frontier(nodes: tuple[RouteNode, ...], commitments: CommitmentSet, bank: Bank) -> tuple[str, ...]:
    opened = []
    for node in nodes:
        if node.kind == 'leaf' and not is_terminus(node.proposition, node.t_id, commitments):
            opened.append(node.id)
        if node.kind == 'inference':
            entry = bank.get(node.proposal.bank_id)
            answers = {a.cq_id: a for a in node.cq_answers}
            if any(q.id not in answers or not cq_supported(answers[q.id], q.id, commitments)
                   for q in entry.critical_questions):
                opened.append(node.id)
    return tuple(opened)


def dialectical_cost(nodes: tuple[RouteNode, ...], commitments: CommitmentSet) -> float | None:
    if any(n.kind == 'leaf' and commitments.contains_formula(n.proposition.formula.negated()) for n in nodes):
        return None
    return float(sum(n.kind == 'inference' or (
        n.kind == 'leaf' and not is_terminus(n.proposition, n.t_id, commitments)) for n in nodes))


def finish(graph: RouteGraph, commitments: CommitmentSet, bank: Bank) -> RouteGraph:
    opened = frontier(graph.nodes, commitments, bank)
    return replace(graph, status='OPEN' if opened else 'CLOSED', frontier=opened,
                   dialectical_cost=dialectical_cost(graph.nodes, commitments))


def leaf_premises(graph: RouteGraph, commitments: CommitmentSet) -> frozenset[str]:
    # CQ evidence is also an external commitment dependency. Assumptions are not.
    formulas = {n.proposition.formula.canonical() for n in graph.nodes if n.kind == 'leaf'}
    formulas.update(commitments.get(tid).formula.canonical() for n in graph.nodes
                    for answer in n.cq_answers for tid in answer.supporting_t_ids
                    if commitments.get(tid) is not None)
    return frozenset(formulas)


def independent_count(routes: tuple[RouteGraph, ...], commitments: CommitmentSet) -> int:
    sets = tuple(leaf_premises(r, commitments) for r in routes if r.status == 'CLOSED')
    # Exact maximum independent set, not an order-dependent greedy count.
    conflicts = tuple(sum(1 << j for j, other in enumerate(sets)
                          if i == j or bool(s & other)) for i, s in enumerate(sets))

    @lru_cache(None)
    def solve(mask: int) -> int:
        if not mask:
            return 0
        indices = [i for i in range(len(sets)) if mask & (1 << i)]
        isolated = [i for i in indices if (conflicts[i] & mask) == (1 << i)]
        if isolated:
            return len(isolated) + solve(mask & ~sum(1 << i for i in isolated))
        i = max(indices, key=lambda i: (conflicts[i] & mask).bit_count())
        return max(solve(mask & ~(1 << i)), 1 + solve(mask & ~conflicts[i]))

    return solve((1 << len(sets)) - 1)
