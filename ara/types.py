"""Immutable engine/runtime contracts; no providers or solver effects.

JSON uses snake_case field names. Optional/default fields may be omitted on input;
output always includes defaults. Unknown fields and wrong primitive types fail.
"""
from __future__ import annotations

import json
import types
from dataclasses import dataclass, fields
from functools import cache
from typing import Any, Iterable, Literal, Self, TypeAlias, Union, get_args, get_origin, get_type_hints

JSON: TypeAlias = Union[None, bool, int, float, str, list['JSON'], dict[str, 'JSON']]


@cache
def _hints(cls: type) -> dict[str, Any]:
    return get_type_hints(cls)


def _convert(annotation: Any, value: Any) -> Any:
    origin, args = get_origin(annotation), get_args(annotation)
    if origin in (Union, types.UnionType):
        for candidate in args:
            try:
                return _convert(candidate, value)
            except (TypeError, ValueError):
                pass
        raise TypeError(f'value does not match {annotation}')
    if origin is Literal:
        if value not in args or type(value) not in {type(a) for a in args}:
            raise ValueError(f'expected one of {args}')
        return value
    if origin is tuple:
        if not isinstance(value, (tuple, list)):
            raise TypeError('expected an array')
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(_convert(args[0], item) for item in value)
        if len(value) != len(args):
            raise ValueError('wrong tuple size')
        return tuple(_convert(t, v) for t, v in zip(args, value))
    if isinstance(annotation, type) and issubclass(annotation, Record):
        return value if isinstance(value, annotation) else annotation.from_dict(value)
    if annotation is float and type(value) in (float, int):
        return float(value)
    if type(value) is not annotation:
        raise TypeError(f'expected {annotation}')
    return value


def _encode(value: Any) -> JSON:
    if isinstance(value, Record):
        return value.to_dict()
    if isinstance(value, tuple):
        return [_encode(item) for item in value]
    return value


class Record:
    """Strict JSON codec for frozen dataclasses, including nested tuple coercion."""

    def __post_init__(self) -> None:
        for name, annotation in _hints(type(self)).items():
            object.__setattr__(self, name, _convert(annotation, getattr(self, name)))

    def to_dict(self) -> dict[str, JSON]:
        return {f.name: _encode(getattr(self, f.name)) for f in fields(self)}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(',', ':'), allow_nan=False)

    @classmethod
    def from_dict(cls, value: dict[str, JSON]) -> Self:
        if not isinstance(value, dict):
            raise TypeError('expected an object')
        if value.keys() - {f.name for f in fields(cls)}:
            raise ValueError(f'unknown fields for {cls.__name__}')
        return cls(**value)

    @classmethod
    def from_json(cls, value: str) -> Self:
        return cls.from_dict(json.loads(value))


@dataclass(frozen=True)
class Term(Record):
    kind: Literal['constant', 'variable']
    name: str

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.name:
            raise ValueError('term name is required')


FormulaOp = Literal['atom', 'not', 'and', 'or', 'implies', 'iff', 'forall', 'exists', 'predicate']


@dataclass(frozen=True)
class Formula(Record):
    op: FormulaOp
    args: tuple[Formula, ...] = ()
    name: str | None = None
    terms: tuple[Term, ...] = ()
    variable: str | None = None

    def __post_init__(self) -> None:
        super().__post_init__()
        arity = len(self.args)
        valid = (
            (self.op in ('atom', 'predicate') and arity == 0 and bool(self.name))
            or (self.op == 'not' and arity == 1)
            or (self.op in ('and', 'or') and arity >= 2)
            or (self.op in ('implies', 'iff') and arity == 2)
            or (self.op in ('forall', 'exists') and arity == 1 and bool(self.variable))
        )
        if not valid:
            raise ValueError('malformed formula shape')
        if self.op not in ('atom', 'predicate') and self.name is not None:
            raise ValueError('unexpected formula name')
        if self.op != 'predicate' and self.terms:
            raise ValueError('unexpected terms')
        if self.op not in ('forall', 'exists') and self.variable is not None:
            raise ValueError('unexpected bound variable')

    def normalized(self) -> Formula:
        children = tuple(child.normalized() for child in self.args)
        if self.op == 'not' and children[0].op == 'not':
            return children[0].args[0]
        if self.op in ('and', 'or'):
            children = tuple(sorted(
                (item for child in children for item in (child.args if child.op == self.op else (child,))),
                key=lambda item: item.to_json(),
            ))
        return Formula(self.op, children, self.name, self.terms, self.variable)

    def canonical(self) -> str:
        return self.normalized().to_json()

    def negated(self) -> Formula:
        return Formula('not', (self,)).normalized()


@dataclass(frozen=True)
class SymbolDefinition(Record):
    name: str
    kind: Literal['atom', 'predicate']
    arity: int
    definition: str

    def __post_init__(self):
        super().__post_init__()
        if not self.name or not self.definition.strip() or self.arity < 0 or (self.kind == 'atom' and self.arity):
            raise ValueError('invalid proposed symbol definition')


@dataclass(frozen=True)
class Proposition(Record):
    id: str
    text: str
    formula: Formula | None = None
    new_symbols: tuple[SymbolDefinition, ...] = ()

    def to_dict(self):
        value = super().to_dict()
        if not self.new_symbols:
            del value['new_symbols']
        return value


def negate_proposition(proposition: Proposition) -> Proposition:
    """Unformalised text cannot establish canonical negation."""
    if proposition.formula is None:
        raise ValueError('negation requires a formula')
    formula = proposition.formula.negated()
    return Proposition(f'not:{proposition.id}', formula.canonical(), formula, proposition.new_symbols)


@dataclass(frozen=True)
class Commitment(Record):
    id: str
    text: str
    citation: str
    formula: Formula

    def __post_init__(self) -> None:
        super().__post_init__()
        if not self.id or self.id == 'open' or not self.text or not self.citation:
            raise ValueError('commitment requires id, text and citation; open is reserved')


@dataclass(frozen=True)
class CommitmentSet(Record):
    commitments: tuple[Commitment, ...]

    def __post_init__(self) -> None:
        super().__post_init__()
        ids = [c.id for c in self.commitments]
        if len(set(ids)) != len(ids):
            raise ValueError('duplicate commitment id')

    @classmethod
    def build(cls, commitments: Iterable[Commitment]) -> CommitmentSet:
        return cls(tuple(commitments))

    def get(self, commitment_id: str) -> Commitment | None:
        return next((c for c in self.commitments if c.id == commitment_id), None)

    def contains_formula(self, formula: Formula) -> bool:
        return any(c.formula.canonical() == formula.canonical() for c in self.commitments)


@dataclass(frozen=True)
class Slot(Record):
    id: str
    template: str


@dataclass(frozen=True)
class CriticalQuestion(Record):
    id: str
    template: str


@dataclass(frozen=True)
class SourceCitation(Record):
    work: str
    locator: str


@dataclass(frozen=True)
class SlotFormula(Record):
    slot: str
    formula: Formula


@dataclass(frozen=True)
class Substitution(Record):
    slot: str
    body_variable: str
    variable: str
    term: Term


@dataclass(frozen=True)
class AssumptionScope(Record):
    id: str
    assumption_slot: str
    result_slots: tuple[str, ...]


@dataclass(frozen=True)
class FormulaSchema(Record):
    formula_variables: tuple[str, ...]
    term_variables: tuple[str, ...]
    premises: tuple[SlotFormula, ...]
    conclusion: Formula
    substitutions: tuple[Substitution, ...] = ()
    scopes: tuple[AssumptionScope, ...] = ()


@dataclass(frozen=True)
class BankEntry(Record):
    id: str
    name: str
    kind: Literal['deductive', 'defeasible']
    premise_slots: tuple[Slot, ...]
    conclusion_slot: Slot
    source: SourceCitation
    critical_questions: tuple[CriticalQuestion, ...] = ()
    formula_schema: FormulaSchema | None = None


@dataclass(frozen=True)
class PremiseFill(Record):
    slot: str
    text: str
    t_id: str = 'open'
    scope_id: str | None = None


@dataclass(frozen=True)
class Proposal(Record):
    bank_id: str
    premises: tuple[PremiseFill, ...]
    conclusion_text: str
    conclusion_ref: Literal['current_goal'] | None = None

    def to_dict(self):
        value = super().to_dict()
        # Preserve the canonical encoding of historical proposals without references.
        if self.conclusion_ref is None:
            del value['conclusion_ref']
        return value


@dataclass(frozen=True)
class CQAnswer(Record):
    cq_id: str
    answer: str
    answered: bool
    supporting_t_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProofScope(Record):
    id: str
    assumption_node_id: str
    result_node_ids: tuple[str, ...]
    discharged_by: str


@dataclass(frozen=True)
class RouteNode(Record):
    id: str
    proposition: Proposition
    kind: Literal['leaf', 'inference', 'assumption']
    t_id: str = 'open'
    proposal: Proposal | None = None
    children: tuple[str, ...] = ()
    cq_answers: tuple[CQAnswer, ...] = ()
    scope_id: str | None = None


@dataclass(frozen=True)
class RouteGraph(Record):
    id: str
    root_id: str
    nodes: tuple[RouteNode, ...]
    status: Literal['OPEN', 'CLOSED'] = 'OPEN'
    frontier: tuple[str, ...] = ()
    scopes: tuple[ProofScope, ...] = ()
    dialectical_cost: float | None = None


@dataclass(frozen=True)
class EngineDecision(Record):
    status: Literal['licensed', 'discarded']
    reason_code: str
    detail: str
    bank_id: str | None = None
    node_id: str | None = None


@dataclass(frozen=True)
class TokenUsage(Record):
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    server_tool_uses: int = 0


@dataclass(frozen=True)
class RunEvent(Record):
    timestamp: str
    stage: str
    label: Literal['MODEL', 'ENGINE', 'HUMAN', 'STOP', 'SYSTEM']
    model_id: str | None = None
    model_version: str | None = None
    prompt: str | None = None
    response: str | None = None
    usage: TokenUsage = TokenUsage()
    cost_usd: float = 0.0
    wall_seconds: float = 0.0
    decision: EngineDecision | None = None
    payload_json: str = '{}'

    def __post_init__(self) -> None:
        super().__post_init__()
        object.__setattr__(self, 'payload_json', json.dumps(
            json.loads(self.payload_json), sort_keys=True, separators=(',', ':'), allow_nan=False,
        ))


@dataclass(frozen=True)
class Tier1Repair(Record):
    action: Literal['disambiguate', 'add_premise', 'revise', 'unresolved']
    detail: str
    proposals: tuple[Proposal, ...] = ()
