"""Synchronous ports: engine consumes them; runtime supplies validated adapters.

Adapters raise on rejected/schema-invalid model output. They must log failures,
cache valid responses and enforce budgets before returning. The engine validates
licensing, commitment membership, CQ support and proof scope independently.
"""
from typing import Protocol

from ara.types import (
    BankEntry, CommitmentSet, CQAnswer, CriticalQuestion, Formula, PremiseFill,
    Proposal, Proposition, RunEvent, Tier1Repair,
)


class CutProposer(Protocol):
    def propose_cuts(self, goal: Proposition, commitments: CommitmentSet,
                     bank: tuple[BankEntry, ...]) -> tuple[Proposal, ...]: ...


class Formaliser(Protocol):
    def formalise(self, proposition: Proposition) -> Formula: ...


class LeafMapper(Protocol):
    def map_leaf(self, leaf: Proposition, commitments: CommitmentSet) -> str:
        """Return a T id or the reserved string 'open'; never assert closure."""
        ...


class CQAnswerer(Protocol):
    def answer_cq(self, question: CriticalQuestion, proposal: Proposal,
                  commitments: CommitmentSet) -> CQAnswer: ...


class Tier1Repairer(Protocol):
    def repair_tier1(self, premises: tuple[PremiseFill, ...],
                     conclusions: tuple[Proposition, ...],
                     commitments: CommitmentSet) -> Tier1Repair: ...


class EventSink(Protocol):
    def emit(self, event: RunEvent) -> None: ...
