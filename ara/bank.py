"""Load versioned forms and reject invalid bank contracts before search."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from string import Formatter

import yaml

from ara.types import BankEntry, Formula, FormulaSchema, JSON, Record


@dataclass(frozen=True)
class Bank(Record):
    bank_version: str
    entries: tuple[BankEntry, ...]

    def get(self, bank_id: str) -> BankEntry | None:
        return next((entry for entry in self.entries if entry.id == bank_id), None)


def _unique(values: list[str], label: str) -> None:
    if len(set(values)) != len(values):
        raise ValueError(f'duplicate {label}')
    if any(not value for value in values):
        raise ValueError(f'empty {label}')


def _template(template: str, slots: set[str]) -> None:
    if not template:
        raise ValueError('empty template')
    references = 0
    for _, field, spec, conversion in Formatter().parse(template):
        if field is not None:
            references += 1
            if field not in slots:
                raise ValueError(f'undefined template slot: {field}')
            if spec or conversion:
                raise ValueError('only simple slot references are allowed')
    if not references:
        raise ValueError('template must reference a slot')


def _schema(schema: FormulaSchema, slots: set[str]) -> None:
    _unique(list(schema.formula_variables), 'formula metavariable')
    _unique(list(schema.term_variables), 'term metavariable')
    if not schema.formula_variables:
        raise ValueError('missing formula metavariables')
    names = [p.slot for p in schema.premises]
    _unique(names, 'formula slot')
    if set(names) != slots:
        raise ValueError('formula schema must cover exactly the premise slots')

    def visit(formula: Formula) -> None:
        if formula.op == 'atom' and formula.name not in schema.formula_variables:
            raise ValueError('undeclared formula metavariable')
        for term in formula.terms:
            if term.name not in schema.term_variables:
                raise ValueError('undeclared term metavariable')
        if formula.variable and formula.variable not in schema.term_variables:
            raise ValueError('undeclared bound variable')
        for child in formula.args:
            visit(child)

    for premise in schema.premises:
        visit(premise.formula)
    visit(schema.conclusion)
    for sub in schema.substitutions:
        if sub.slot not in slots | {'conclusion'} or sub.body_variable not in schema.formula_variables:
            raise ValueError('invalid substitution slot or body')
        if sub.variable not in schema.term_variables or sub.term.name not in schema.term_variables:
            raise ValueError('undeclared substitution term')
    _unique([scope.id for scope in schema.scopes], 'scope id')
    for scope in schema.scopes:
        if scope.assumption_slot not in slots or not scope.result_slots:
            raise ValueError('invalid assumption scope')
        if not set(scope.result_slots) <= slots or scope.assumption_slot in scope.result_slots:
            raise ValueError('invalid scoped results')
        _unique(list(scope.result_slots), 'scope result slot')


def _entry(entry: BankEntry) -> None:
    if not entry.id or not entry.name or not entry.source.work or not entry.source.locator:
        raise ValueError('entry requires id, name and source')
    if not entry.premise_slots:
        raise ValueError('missing premise slots')
    all_slots = [p.id for p in entry.premise_slots] + [entry.conclusion_slot.id]
    _unique(all_slots, 'slot')
    slots = set(all_slots)
    for slot in (*entry.premise_slots, entry.conclusion_slot):
        _template(slot.template, slots)
    _unique([cq.id for cq in entry.critical_questions], 'CQ id')
    for cq in entry.critical_questions:
        _template(cq.template, slots)
    if entry.kind == 'deductive':
        if entry.conclusion_slot.id != 'conclusion':
            raise ValueError('deductive conclusion slot must be conclusion')
        if entry.formula_schema is None:
            raise ValueError('deductive entry requires formula schema')
        _schema(entry.formula_schema, {p.id for p in entry.premise_slots})
    elif entry.formula_schema is not None or not entry.critical_questions:
        raise ValueError('defeasible entry requires CQs and no deductive schema')


def validate_bank(document: dict[str, JSON]) -> Bank:
    """Validate a complete YAML document; duplicate ids fail within and across files."""
    try:
        bank = Bank.from_dict(document)
        if not bank.bank_version or not bank.entries:
            raise ValueError('missing bank version or entries')
        _unique([entry.id for entry in bank.entries], 'bank id')
        for entry in bank.entries:
            _entry(entry)
        return bank
    except (TypeError, KeyError, ValueError) as exc:
        raise ValueError(f'invalid bank: {exc}') from exc


class _StrictLoader(yaml.SafeLoader):
    """YAML mappings must not silently overwrite repeated keys."""


def _mapping(loader: _StrictLoader, node: yaml.MappingNode) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        if key in result:
            raise ValueError(f'duplicate YAML key: {key}')
        result[key] = loader.construct_object(value_node, deep=True)
    return result


_StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def load_bank(path: str | Path) -> Bank:
    path = Path(path)
    paths = sorted(path.glob('*.yaml')) if path.is_dir() else [path]
    if not paths:
        raise ValueError('no bank files found')
    documents = [validate_bank(yaml.load(p.read_text(), Loader=_StrictLoader)) for p in paths]
    versions = {bank.bank_version for bank in documents}
    if len(versions) != 1:
        raise ValueError('bank version mismatch')
    return validate_bank({
        'bank_version': documents[0].bank_version,
        'entries': [entry.to_dict() for bank in documents for entry in bank.entries],
    })
