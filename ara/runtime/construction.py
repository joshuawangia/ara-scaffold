"""Counted rich-evidence selection; deterministic merge before the sole freeze.

No formula equivalence is inferred here. Symbol reuse is a logged model decision
against the shared catalogue, and every evidence decision remains inspectable.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import TYPE_CHECKING

from ara.runtime.cache import canonical, digest
from ara.runtime.extraction import HEADER, save_immutable
from ara.types import CommitmentSet

if TYPE_CHECKING:
    from ara.runtime.calls import ModelCalls

PLAN_VERSION = 'rich-working-t-v2'


@dataclass(frozen=True)
class Batch:
    index: int
    source_ids: tuple[str, ...]
    papers_json: str
    input_tokens: int
    allowance: int


@dataclass(frozen=True)
class BatchResult:
    index: int
    commitments: CommitmentSet
    receipt_json: str


def merge_batches(results: tuple[BatchResult, ...], expected: int) -> CommitmentSet:
    from ara.runtime.calls import require
    require(sorted(r.index for r in results) == list(range(expected)), 'duplicate or missing batch id')
    # Keep distinct evidence even when formulas agree or contradict.
    items = [c for r in sorted(results, key=lambda r: r.index) for c in r.commitments.commitments]
    require(len({c.citation for c in items}) == len(items), 'duplicate merged evidence citation')
    return CommitmentSet(tuple(sorted(items, key=lambda c: c.id)))


def evidence_dependencies(items: dict[str, dict]) -> dict[str, set[str]]:
    deps = {id: set() for id in items}
    for id, item in items.items():
        if item['kind'] == 'inference':
            group = {id, *item['premise_ids'], item['conclusion_id'], *item['qualification_ids']}
            for member in group:
                deps[member].update(group - {member})
        for target in item['applies_to']:
            deps[id].add(target)
            deps[target].add(id)
    return deps


def formula_symbols(formula):
    if formula.op in ('atom', 'predicate'):
        yield formula.name, formula.op, len(formula.terms)
    for term in formula.terms:
        if term.kind == 'constant':
            yield term.name, 'constant', 0
    for arg in formula.args:
        yield from formula_symbols(arg)


def construct(calls: ModelCalls, literature: str, audience: str) -> CommitmentSet:
    from ara.runtime.calls import require
    papers = sorted(json.loads(literature[len(HEADER):])['papers'], key=lambda p: p['source_id'])
    require(len({p['source_id'] for p in papers}) == len(papers), 'duplicate source id')
    usable = [p for p in papers if p['items']]
    all_items = [item for p in usable for item in p['items']]
    require(len({i['id'] for i in all_items}) == len(all_items), 'duplicate evidence id')
    require(len({i['citation'] for i in all_items}) == len(all_items), 'duplicate evidence citation')
    metadata = {'version': PLAN_VERSION, 'sources': [
        {'source_id': p['source_id'], 'content_hash': digest(canonical(p))} for p in papers],
        'topic': calls.topic, 'audience': audience,
        'batch_input_tokens': calls.config['build_t_batch_input_tokens'],
        'symbol_token_budget': calls.config['working_t_symbol_token_budget'],
        'working_t_token_budget': calls.config['working_t_token_budget']}
    symbol_budget = metadata['symbol_token_budget']
    input_bound = min(metadata['batch_input_tokens'], calls.config['model_context_token_bound'] -
                      calls.config['extracted_build_t_max_output_tokens'] - symbol_budget)
    require(input_bound > 0, 'no build-T batch input allowance')
    base_inputs = {'plan': metadata, 'audience': audience, 'shared_symbols': []}
    batches: list[Batch] = []
    pending = []
    pending_tokens = 0
    total_nodes = len(all_items)
    def inputs_for(group, index, allowance):
        return {**base_inputs, 'batch_index': index, 'papers': group, 'working_token_allowance': allowance}
    def allowance_for(group):
        return max(1, (metadata['working_t_token_budget'] - 8000) * sum(len(p['items']) for p in group) // total_nodes)
    def count(group):
        return calls.count_request('build_t_batch', inputs_for(group, len(batches), allowance_for(group))).input_tokens
    for paper in usable:
        candidate = pending + [paper]
        counted = count(candidate)
        if counted > input_bound and pending:
            batches.append(Batch(len(batches), tuple(p['source_id'] for p in pending), canonical(pending),
                                 pending_tokens, allowance_for(pending)))
            pending = []
            candidate = [paper]
            counted = count(candidate)
        if counted > input_bound:
            calls.budget.stop('build_t_batch oversized source batch; raise counted batch allowance; no truncation', 'build_t_batch')
        pending, pending_tokens = candidate, counted
    if pending:
        batches.append(Batch(len(batches), tuple(p['source_id'] for p in pending), canonical(pending),
                             pending_tokens, allowance_for(pending)))
    plan = {**metadata, 'batches': [dict(index=b.index, source_ids=b.source_ids, input_tokens=b.input_tokens,
                                       allowance=b.allowance, content_hash=digest(b.papers_json)) for b in batches]}
    plan_id = digest(canonical(plan))
    calls.log.record('build_t_plan', plan_id=plan_id, plan=plan)
    save_immutable(calls.log.path.parent / f'build-t-plan-{plan_id}.json', canonical(plan))
    symbols = []
    results = []
    for batch in batches:
        group = json.loads(batch.papers_json)
        items = {item['id']: item for paper in group for item in paper['items']}
        dependencies = evidence_dependencies(items)
        inputs = {**inputs_for(group, batch.index, batch.allowance), 'plan_id': plan_id,
                  'shared_symbols': symbols, 'batch_content_hash': digest(batch.papers_json)}
        # The actual growing catalogue and plan identity are counted again, including retries.
        def check(data):
            commitments = CommitmentSet.from_dict({'commitments': data['commitments']})
            selected = {c.id for c in commitments.commitments}
            omitted = data['omitted']
            require(len({o['evidence_id'] for o in omitted}) == len(omitted), 'duplicate omission id')
            excluded = {o['evidence_id'] for o in omitted}
            require(not selected & excluded and selected | excluded == set(items), 'working T evidence inventory mismatch')
            require(all(o['reason'].strip() for o in omitted), 'empty omission reason')
            require(all(dependencies[id] <= selected for id in selected), 'working T drops premise/link/qualification')
            for c in commitments.commitments:
                require(c.citation == items[c.id]['citation'], 'T citation not in extracted literature')
                # Text carries attribution and provenance from immutable evidence, not a lossy rewrite.
                require(c.text == evidence_text(items[c.id]), 'working T changed evidence or attribution')
            require(len({c.citation for c in commitments.commitments}) == len(commitments.commitments), 'duplicate batch citation')
            names = [s['name'] for s in symbols + data['new_symbols']]
            require(len(set(names)) == len(names), 'duplicate symbol definition')
            catalog = {s['name']: s for s in symbols + data['new_symbols']}
            bindings = data['bindings']
            require(len({b['name'] for b in bindings}) == len(bindings), 'duplicate symbol binding')
            bound = {b['name']: set(b['evidence_ids']) for b in bindings}
            used = {}
            for c in commitments.commitments:
                for name, kind, arity in formula_symbols(c.formula):
                    require(name in catalog, 'undeclared formula symbol')
                    require(catalog[name]['kind'] == kind and catalog[name]['arity'] == arity, 'symbol signature mismatch')
                    used.setdefault(name, set()).add(c.id)
            require(bound == used, 'symbol alignment evidence mismatch')
            for symbol in data['new_symbols']:
                require(bool(symbol['definition'].strip()) and set(symbol['evidence_ids']) <= selected and
                        bool(symbol['evidence_ids']), 'symbol definition lacks evidence')
                require(symbol['name'] in used, 'unused symbol definition')
            blank = calls.count_request('propose_targets', {'commitments': {'commitments': []}, 'count': 1, 'named_position': None})
            measured = calls.count_request('propose_targets', {'commitments': commitments.to_dict(), 'count': 1, 'named_position': None})
            require(measured.input_tokens - blank.input_tokens <= batch.allowance, 'working T batch token allowance exceeded')
            catalog_inputs = {**inputs, 'papers': [], 'shared_symbols': symbols + data['new_symbols']}
            without = calls.count_request('build_t_batch', {**catalog_inputs, 'shared_symbols': []})
            with_catalog = calls.count_request('build_t_batch', catalog_inputs)
            require(with_catalog.input_tokens - without.input_tokens <= symbol_budget, 'shared symbol token allowance exceeded')
            return BatchResult(batch.index, commitments, canonical(data))
        result = calls.call('build_t_batch', inputs, check)
        data = json.loads(result.receipt_json)
        symbols += data['new_symbols']
        results.append(result)
        calls.log.record('build_t_batch_accepted', plan_id=plan_id, index=batch.index,
                         source_ids=batch.source_ids, output_hash=digest(result.receipt_json),
                         evidence_ids=[c.id for c in result.commitments.commitments], omitted=data['omitted'])
        save_immutable(calls.log.path.parent / f'build-t-{plan_id}-{batch.index}.json', result.receipt_json)
    merged = merge_batches(tuple(results), len(batches))
    measured = calls.count_request('propose_targets', {'commitments': merged.to_dict(),
        'count': calls.config['target_candidates'], 'named_position': None}, admission=True)
    if measured.input_tokens > metadata['working_t_token_budget']:
        calls.budget.stop('working T downstream token budget exceeded before freeze', 'build_t_batch')
    calls.log.record('build_t_merged', plan_id=plan_id, commitments=merged.to_dict(), symbols=symbols,
                     input_tokens=measured.input_tokens, source_ids=[p['source_id'] for p in papers],
                     note='One construction lifecycle, one freeze; explicit model omissions retained in batch receipts.')
    save_immutable(calls.log.path.parent / f'working-t-{plan_id}.json', canonical({
        'plan_id': plan_id, 'symbols': symbols, 'commitments': merged.to_dict()}))
    return merged


def evidence_text(item: dict) -> str:
    return f"[{item['attribution']}; {item['attributed_to']}; {item['kind']}] {item['text']}"
