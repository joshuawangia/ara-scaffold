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

PLAN_VERSION = 'rich-working-t-v4'
CLOSURE_VERSION = 'directional-prerequisites-v1'


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
            deps[id].update([*item['premise_ids'], item['conclusion_id'], *item['qualification_ids']])
            deps[item['conclusion_id']].add(id)
        # Applicable qualifiers are prerequisites; they never drag in other targets.
        for target in item['applies_to']:
            deps[target].add(id)
    return deps


def prerequisite_closure(items: dict[str, dict], roots: list[str]) -> set[str]:
    from ara.runtime.calls import require
    require(set(roots) <= set(items), 'unknown selection root')
    dependencies = evidence_dependencies(items)
    selected = set(roots)
    pending = list(roots)
    while pending:
        for id in dependencies[pending.pop()] - selected:
            selected.add(id)
            pending.append(id)
    return selected


def selection_inventory(items: dict[str, dict]) -> tuple[dict[str, str], list[dict]]:
    """Short IDs and metadata partitions; no semantic equivalence or relevance inference."""
    aliases = {f'r{index}': id for index, id in enumerate(sorted(items), 1)}
    partitions = {}
    fields = ('source_id', 'kind', 'attribution', 'attributed_to')
    for alias, id in aliases.items():
        key = tuple(items[id][field] for field in fields)
        partitions.setdefault(key, []).append(alias)
    groups = [dict(group_id=f'g{index}', root_ids=partitions[key], **dict(zip(fields, key)))
              for index, key in enumerate(sorted(partitions), 1)]
    return aliases, groups


def formula_symbols(formula, bound: frozenset[str] = frozenset()):
    from ara.runtime.calls import require
    if formula.op in ('forall', 'exists'):
        bound = bound | {formula.variable}
    if formula.op in ('atom', 'predicate'):
        yield formula.name, formula.op, len(formula.terms)
    for term in formula.terms:
        require(term.kind != 'variable' or term.name in bound, 'working T variables must be locally bound')
        if term.kind == 'constant':
            yield term.name, 'constant', 0
    for arg in formula.args:
        yield from formula_symbols(arg, bound)


def construction_call(calls: ModelCalls, kind: str, inputs: dict, check, remaining: dict):
    from ara.runtime.calls import InvalidOutput, Rejected, require
    if remaining[kind] is None:
        return calls.call(kind, inputs, check)
    try:
        return calls._call_once(kind, inputs, check)
    except InvalidOutput as exc:
        if not remaining[kind]:
            raise
        fields = {'omissions': 'group_id'} if kind == 'select_t_roots' else {
            'commitments': 'id', 'new_symbols': 'name', 'alignments': 'name'}
        try:
            candidate = json.loads(exc.feedback['rejected_response'])
            if kind == 'build_t_batch':
                for item in candidate['commitments']:
                    if isinstance(item['formula'], str):
                        item['formula'] = json.loads(item['formula'])
            baseline = {field: {item[key]: item for item in candidate[field]} for field, key in fields.items()}
            require(all(len(baseline[field]) == len(candidate[field]) for field in fields),
                    'ambiguous construction correction inventory')
        except (ValueError, KeyError, TypeError) as error:
            raise Rejected('candidate cannot support targeted construction correction') from error
        remaining[kind] -= 1
        request = {**inputs, 'mode': 'targeted_correction', 'candidate': candidate,
                   'validation_error': exc.feedback['error']}
        calls.log.record('construction_targeted_correction', kind=kind,
                         candidate_hash=digest(canonical(candidate)), reason=str(exc))
        def corrected(patch):
            merged = {**candidate, **patch}
            changed = any(patch[k] != candidate.get(k) for k in patch if k not in fields)
            for field, key in fields.items():
                updates = {item[key]: item for item in patch[field]}
                require(len(updates) == len(patch[field]), 'duplicate construction correction id')
                require(all(item != baseline[field].get(id) for id, item in updates.items()),
                        'construction correction repeats unchanged item')
                changed = changed or bool(updates)
                merged[field] = list({**baseline[field], **updates}.values())
            require(changed, 'empty construction correction')
            from jsonschema import Draft202012Validator
            schema = json.loads((calls.root / 'schemas' / f'{kind}.json').read_text())
            Draft202012Validator(schema).validate(merged)
            return check(merged)
        return calls._call_once(kind, request, corrected, attempt=2)


def construct(calls: ModelCalls, literature: str, audience: str) -> CommitmentSet:
    from ara.runtime.calls import require
    corrections = calls.config.get('construction_targeted_corrections')
    if corrections is not None and (type(corrections) is not int or corrections not in (0, 1)):
        raise ValueError('construction_targeted_corrections must be 0 or 1')
    remaining = dict(select_t_roots=corrections, build_t_batch=corrections)
    papers = sorted(json.loads(literature[len(HEADER):])['papers'], key=lambda p: p['source_id'])
    require(len({p['source_id'] for p in papers}) == len(papers), 'duplicate source id')
    usable = [p for p in papers if p['items']]
    all_items = [item for p in usable for item in p['items']]
    require(len({i['id'] for i in all_items}) == len(all_items), 'duplicate evidence id')
    require(len({i['citation'] for i in all_items}) == len(all_items), 'duplicate evidence citation')
    metadata = {'version': PLAN_VERSION, 'closure_version': CLOSURE_VERSION, 'sources': [
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
        root_ids, selection_groups = selection_inventory(items)
        aliases = {id: alias for alias, id in root_ids.items()}
        groups_by_id = {g['group_id']: g for g in selection_groups}
        selection_inputs = {**inputs, 'selection_groups': selection_groups, 'papers': [
            {**paper, 'items': [{**item, 'root_id': aliases[item['id']]} for item in paper['items']]}
            for paper in group]}
        calls.log.record('build_t_selection_inventory', plan_id=plan_id, index=batch.index,
                         root_ids=root_ids, groups=selection_groups, graph_hash=digest(canonical(items)))
        def select(data):
            short_roots = data['roots']
            require(bool(short_roots) and len(set(short_roots)) == len(short_roots) and
                    set(short_roots) <= set(root_ids), 'invalid selection roots')
            roots = [root_ids[id] for id in short_roots]
            require(bool(data['relevance'].strip()), 'empty selection reason')
            omitted_groups = [g['group_id'] for g in data['omissions']]
            require(len(omitted_groups) == len(set(omitted_groups)) and
                    set(omitted_groups) <= set(groups_by_id), 'invalid omission group inventory')
            require(all(g['reason'].strip() for g in data['omissions']), 'empty omission reason')
            omitted = [dict(evidence_id=root_ids[id], reason=g['reason']) for g in data['omissions']
                       for id in groups_by_id[g['group_id']]['root_ids'] if id not in short_roots]
            excluded = {o['evidence_id'] for o in omitted}
            require(len(omitted) == len(excluded), 'duplicate omission id')
            require(not set(roots) & excluded and set(roots) | excluded == set(items), 'working T evidence inventory mismatch')
            return {**data, 'roots': roots}, omitted
        selection, omitted = construction_call(calls, 'select_t_roots', selection_inputs, select, remaining)
        selected_ids = prerequisite_closure(items, selection['roots'])
        require(all(dependencies[id] <= selected_ids for id in selected_ids), 'working T drops premise/link/qualification')
        omitted = [o for o in omitted if o['evidence_id'] not in selected_ids]
        closure = {'rule_version': CLOSURE_VERSION, 'graph_hash': digest(canonical(items)),
                   'roots': selection['roots'], 'added_ids': sorted(selected_ids - set(selection['roots'])),
                   'inventory': sorted(selected_ids), 'relevance': selection['relevance'], 'omitted': omitted}
        calls.log.record('build_t_closure', plan_id=plan_id, index=batch.index, **closure)
        inputs = {**inputs, 'closure': closure, 'papers': [
            {**paper, 'items': [i for i in paper['items'] if i['id'] in selected_ids]} for paper in group]}
        # The actual growing catalogue and plan identity are counted again, including retries.
        def check(data):
            ids = [c['id'] for c in data['commitments']]
            require(len(set(ids)) == len(ids) and set(ids) == selected_ids, 'formalization inventory differs from fixed closure')
            commitments = CommitmentSet.from_dict({'commitments': [
                {**c, 'text': evidence_text(items[c['id']]), 'citation': items[c['id']]['citation']}
                for c in data['commitments']]})
            selected = {c.id for c in commitments.commitments}
            for c in commitments.commitments:
                require(c.citation == items[c.id]['citation'], 'T citation not in extracted literature')
                # Text carries attribution and provenance from immutable evidence, not a lossy rewrite.
                require(c.text == evidence_text(items[c.id]), 'working T changed evidence or attribution')
            require(len({c.citation for c in commitments.commitments}) == len(commitments.commitments), 'duplicate batch citation')
            names = [s['name'] for s in symbols + data['new_symbols']]
            require(len(set(names)) == len(names), 'duplicate symbol definition')
            catalog = {s['name']: s for s in symbols + data['new_symbols']}
            used = {}
            for c in commitments.commitments:
                for name, kind, arity in formula_symbols(c.formula):
                    require(name in catalog, 'undeclared formula symbol')
                    require(catalog[name]['kind'] == kind and catalog[name]['arity'] == arity, 'symbol signature mismatch')
                    used.setdefault(name, set()).add(c.id)
            alignments = data['alignments']
            aligned = [a['name'] for a in alignments]
            valid_alignments = (len(set(aligned)) == len(aligned) and
                set(aligned) == set(used) & {s['name'] for s in symbols} and all(a['reason'].strip() for a in alignments))
            require(valid_alignments, 'symbol alignment evidence mismatch')
            bindings = [dict(name=name, evidence_ids=sorted(ids)) for name, ids in sorted(used.items())]
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
            return BatchResult(batch.index, commitments, canonical({**data, 'commitments': commitments.to_dict()['commitments'],
                'bindings': bindings, 'omitted': omitted, 'closure': closure}))
        result = construction_call(calls, 'build_t_batch', inputs, check, remaining)
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
