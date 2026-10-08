"""Bank-only licenses; solver truth and rule identity are independent checks."""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone

from ara.bank import Bank
from ara.formal import entails
from ara.ports import EventSink, Formaliser
from ara.types import BankEntry, EngineDecision, Formula, Proposal, Proposition, RunEvent
from ara.engine.matching import matches_schema


def emit(sink: EventSink, status: str, reason: str, detail: str = '',
         bank_id: str | None = None, node_id: str | None = None) -> EngineDecision:
    decision = EngineDecision(status, reason, detail, bank_id, node_id)
    sink.emit(RunEvent(datetime.now(timezone.utc).isoformat(), 'engine', 'ENGINE', decision=decision))
    return decision


@dataclass(frozen=True)
class License:
    decision: EngineDecision
    entry: BankEntry | None = None
    premises: tuple[Proposition, ...] = ()
    conclusion: Proposition | None = None

    @property
    def licensed(self) -> bool:
        return self.decision.status == 'licensed'


class Licenser:
    def __init__(self, bank: Bank, formaliser: Formaliser, sink: EventSink, timeout_ms: int = 1000):
        if timeout_ms <= 0:
            raise ValueError('solver timeout must be positive')
        self.bank, self.formaliser, self.sink, self.timeout_ms = bank, formaliser, sink, timeout_ms

    def formalise(self, p: Proposition) -> Proposition:
        return p if p.formula is not None else replace(p, formula=self.formaliser.formalise(p))

    def check(self, proposal: Proposal, goal: Proposition, node_id: str | None = None) -> License:
        entry = self.bank.get(proposal.bank_id)

        def result(reason: str, licensed: bool = False, premises=(), conclusion=None):
            return License(emit(self.sink, 'licensed' if licensed else 'discarded', reason,
                                bank_id=proposal.bank_id, node_id=node_id), entry, premises, conclusion)

        if entry is None:
            return result('UNKNOWN_BANK_ID')
        expected = {s.id for s in entry.premise_slots}
        if (len(proposal.premises) != len(expected) or {p.slot for p in proposal.premises} != expected
                or any(not p.text.strip() for p in proposal.premises) or not proposal.conclusion_text.strip()):
            return result('SLOT_MISMATCH')
        goal = self.formalise(goal)
        conclusion = self.formalise(Proposition('conclusion', proposal.conclusion_text))
        if conclusion.formula.canonical() != goal.formula.canonical():
            return result('CONCLUSION_MISMATCH')
        by_slot = {p.slot: p for p in proposal.premises}
        premises = tuple(self.formalise(Proposition(s.id, by_slot[s.id].text)) for s in entry.premise_slots)
        fills = {p.id: p.formula for p in premises}
        schema = entry.formula_schema
        allowed_scopes = {}
        if schema:
            for scope in schema.scopes:
                for slot in (scope.assumption_slot, *scope.result_slots):
                    allowed_scopes[slot] = scope.id
                if by_slot[scope.assumption_slot].t_id != 'open':
                    return result('INVALID_SCOPE')
        if any(p.scope_id != allowed_scopes.get(p.slot) for p in proposal.premises):
            return result('INVALID_SCOPE')
        if entry.kind == 'deductive':
            if schema is None:
                return result('SCHEMA_MISMATCH')
            sequent = dict(fills)
            for scope in schema.scopes:
                assumption = sequent.pop(scope.assumption_slot)
                for slot in scope.result_slots:
                    sequent[slot] = Formula('implies', (assumption, fills[slot]))
            verdict = entails(tuple(sequent.values()), conclusion.formula, self.timeout_ms)
            if verdict != 'SOLVER_UNSAT':
                return result(verdict)
            if not matches_schema(schema, fills, conclusion.formula):
                return result('SCHEMA_MISMATCH')
        return result('BANK_LICENSED', True, premises, conclusion)
