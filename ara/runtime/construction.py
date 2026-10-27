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
from ara.runtime.windows import counted_windows
from ara.types import CommitmentSet

if TYPE_CHECKING:
    from ara.runtime.calls import ModelCalls

PLAN_VERSION = 'rich-working-t-v11'
CLOSURE_VERSION = 'bounded-directional-prerequisites-v2'


@dataclass(frozen=True)
class Batch:
    index: int
    source_ids: tuple[str, ...]
    papers_json: str
    input_tokens: int | None
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


def evidence_window(paper: dict, selected: set[str]) -> dict:
    """Model-facing evidence only; full source metadata remains in the artifact."""
    items = [i for i in paper['items'] if i['id'] in selected]
    ids = {i['id'] for i in items}
    provenance = {id: origins for id, origins in paper.get('item_provenance', {}).items() if id in ids}
    def relevant(gap):
        if 'evidence_ids' in gap:
            return bool(ids.intersection(gap['evidence_ids']))
        if 'item_id' in gap:
            return gap['item_id'] in ids
        return any(any(i['page_start'] <= page <= i['page_end'] for page in gap.get('pages', [])) and
                   ('snapshot_id' not in gap or any(o['snapshot_id'] == gap['snapshot_id']
                                                    for o in provenance.get(i['id'], [])))
                   for i in items)
    gaps = [{**g, **({'evidence_ids': [id for id in g['evidence_ids'] if id in ids]}
                    if 'evidence_ids' in g else {})}
            for g in paper.get('open_gaps', []) if relevant(g)]
    record = paper.get('record', {})
    return dict(source_id=paper['source_id'], title=paper.get('title', record.get('title')),
                authors=paper.get('authors', record.get('authors')),
                partial_source=paper['status'] == 'partial' or bool(paper.get('coverage')),
                items=items, item_provenance=provenance,
                quarantined=[q for q in paper.get('quarantined', []) if q['item_id'] in ids],
                open_gaps=gaps)


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
        return calls._transport_call(kind, inputs, check, attempt=1)
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
            from ara.runtime.validation import validate_local
            schema = json.loads((calls.root / 'schemas' / f'{kind}.json').read_text())
            validate_local(schema, merged, calls.config)
            return check(merged)
        return calls._transport_call(kind, request, corrected, attempt=2)


def construct(calls: ModelCalls, literature: str, audience: str, *, plan_only: bool = False,
              resume_state: dict | None = None):
    from ara.runtime.calls import CountRequestRefused, Rejected, require
    from ara.runtime.budget import BudgetStop
    corrections = calls.config.get('construction_targeted_corrections')
    if corrections is not None and (type(corrections) is not int or corrections not in (0, 1)):
        raise ValueError('construction_targeted_corrections must be 0 or 1')
    remaining = dict(select_t_roots=corrections, build_t_batch=corrections)
    resumption = resume_state
    if getattr(calls, 'construction_resume', False):
        from ara.runtime.construction_resume import load_construction_resume
        resumption = load_construction_resume(calls)
    if resumption:
        for kind, used in resumption['corrections'].items():
            if remaining[kind] is not None:
                require(used <= remaining[kind], 'construction resume correction budget mismatch')
                remaining[kind] -= used
    papers = sorted(json.loads(literature[len(HEADER):])['papers'], key=lambda p: p['source_id'])
    require(len({p['source_id'] for p in papers}) == len(papers), 'duplicate source id')
    require(all(not p['items'] for p in papers if p['status'] == 'failed'),
            'failed paper cannot supply evidence')
    from ara.runtime.grounding import evidence_items
    usable = [{**p, 'items': evidence_items(p)} for p in papers if p['status'] in ('extracted', 'partial')]
    usable = [p for p in usable if p['items']]
    all_items = [item for p in usable for item in p['items']]
    require(len({i['id'] for i in all_items}) == len(all_items), 'duplicate evidence id')
    require(len({i['citation'] for i in all_items}) == len(all_items), 'duplicate evidence citation')
    from ara.runtime.construction_stages import construction_stage_manifest
    metadata = {'version': PLAN_VERSION, 'closure_version': CLOSURE_VERSION, 'sources': [
        {'source_id': p['source_id'], 'content_hash': digest(canonical(p))} for p in papers],
        'topic': calls.topic, 'audience': audience,
        'construction_stages': construction_stage_manifest(calls.config),
        'batch_input_tokens': calls.config['build_t_batch_input_tokens'],
        'symbol_token_budget': calls.config['working_t_symbol_token_budget'],
        'working_t_token_budget': calls.config['working_t_token_budget']}
    symbol_budget = metadata['symbol_token_budget']
    input_bound = min(metadata['batch_input_tokens'], calls.config['model_context_token_bound'] -
                      calls.config['extracted_build_t_max_output_tokens'] - symbol_budget)
    require(input_bound > 0, 'no build-T batch input allowance')
    base_inputs = {'publication_roster': json.loads(literature[len(HEADER):]).get('publication_roster', []), 'plan': metadata, 'audience': audience, 'shared_symbols': []}
    items = {item['id']: item for item in all_items}
    authors = {}
    for paper in usable:
        supplied = paper.get('authors', paper.get('record', {}).get('authors', []))
        supplied = [] if supplied is None else supplied
        require(isinstance(supplied, (str, list)), 'invalid source authors metadata')
        authors[paper['source_id']] = [supplied] if isinstance(supplied, str) else supplied

    dependencies = evidence_dependencies(items)
    from ara.runtime.closure_budget import budget_plan, depth_cut, payload_token_bound
    # Compute each distinct closure once. Payload bounds are local, deterministic
    # byte counts; provider counts still govern every complete request.
    full_closures = {id: prerequisite_closure(items, [id]) for id in items}
    costs = {id: dict(items=len(ids), evidence_payload_token_bound=payload_token_bound(items, ids))
             for id, ids in full_closures.items()}
    allocation = None
    def grouped(ids):
        selected = set(ids)
        return [evidence_window(p, selected)
                for p in usable if any(i['id'] in selected for i in p['items'])]
    def inputs_for(group, index, allowance):
        return {**base_inputs, 'batch_index': index, 'papers': group, 'working_token_allowance': allowance}
    def selection_request(inputs, window_items):
        root_ids, groups = selection_inventory(window_items)
        aliases = {id: alias for alias, id in root_ids.items()}
        return {**inputs, 'selection_groups': groups,
                'closure_costs': {alias: costs[id] for alias, id in root_ids.items()},
                'closure_cost_counter': 'conservative UTF-8 byte bound on evidence payload; not a full request count',
                'window_budget': allocation, 'papers': [
            {**p, 'items': [{**i, 'root_id': aliases[i['id']]} for i in p['items']]}
            for p in inputs['papers']]}
    count_cache = {}
    refused_windows = set()
    def count(ids):
        key = tuple(ids)
        if key in refused_windows:
            return None
        if key in count_cache:
            return count_cache[key]
        inputs = inputs_for(grouped(ids), 0, metadata['working_t_token_budget'])
        try:
            formal = calls.count_request('build_t_batch', inputs).initial_input_tokens
            roots = calls.count_request('select_t_roots', selection_request(inputs, {id: items[id] for id in ids})).initial_input_tokens
        except CountRequestRefused:
            calls.log.record('build_t_partition_refused', evidence_ids=list(ids),
                             action='split' if allocation is None and len(ids) > 1 else 'omit',
                             input_tokens=None)
            count_cache[key] = None
            if allocation is not None or len(ids) == 1:
                refused_windows.add(key)
            return None
        count_cache[key] = max(formal, roots)
        return count_cache[key]
    partition_bound = max(1, input_bound - 2048)
    def partition_count(ids):
        measured = count(ids)
        if measured is None:
            return partition_bound + 1 if len(ids) > 1 else partition_bound
        # Keep an indivisible oversized record as its own window. The plan records
        # its real count and execution omits it before dispatch, without truncation.
        return min(measured, partition_bound) if len(ids) == 1 else measured
    windows = counted_windows(list(items), partition_count, partition_bound, lambda: None)
    target_inputs = {'count': calls.config['target_candidates'], 'named_position': None}
    wrapper = calls.count_request('propose_targets', {**target_inputs, 'commitments': {'commitments': []}}).initial_input_tokens
    copy_total = 0
    copy_items = 0
    for ids in windows:
        if tuple(ids) in refused_windows:
            continue
        floor = [dict(id=id, text=evidence_text(items[id]), citation=items[id]['citation'],
                      formula={'op': 'atom', 'name': 'P'}) for id in ids]
        try:
            copy_total += max(0, calls.count_request('propose_targets', {**target_inputs,
                'commitments': {'commitments': floor}}).initial_input_tokens - wrapper)
            copy_items += len(ids)
        except CountRequestRefused:
            refused_windows.add(tuple(ids))
            calls.log.record('build_t_partition_refused', evidence_ids=list(ids), action='omit', input_tokens=None)
    allocation = budget_plan(calls.config, len(windows), copy_total / max(1, copy_items), wrapper, input_bound)
    count_cache.clear()
    batches = [Batch(index, tuple(p['source_id'] for p in grouped(ids)), canonical(grouped(ids)),
                     count(ids), metadata['working_t_token_budget']) for index, ids in enumerate(windows)]
    plan = {**metadata, 'budget': allocation, 'batches': [dict(index=b.index, source_ids=b.source_ids, input_tokens=b.input_tokens,
                                       allowance=b.allowance, content_hash=digest(b.papers_json)) for b in batches]}
    plan_id = digest(canonical(plan))
    if resumption:
        require(plan_id == resumption['plan_id'], 'construction resume requires the same counted plan id')
        calls.log.record('construction_resumed', plan_id=plan_id,
                         next_window=resumption['terminal_index'] + 1,
                         restored_windows=sorted(resumption['completed']),
                         terminal_receipt=resumption['terminal_receipt'], policy='count-at-reservation')
    else:
        calls.log.record('build_t_plan', plan_id=plan_id, plan=plan)
    save_immutable(calls.log.path.parent / f'build-t-plan-{plan_id}.json', canonical(plan))
    calls.log.record('build_t_budget_plan', plan_id=plan_id, **allocation)
    if plan_only and not resumption:
        return plan
    symbols = []
    results = []
    window_omissions = []
    materialized = set()
    exhausted = None
    refusal_reasons = []
    def preview(next_window):
        return dict(plan=plan, plan_id=plan_id, next_window=next_window,
                    restored_windows=sorted(resumption['completed']),
                    restored_commitments=sum(len(r.commitments.commitments) for r in results))
    def skip(batch, window_items, reason, selection, closure):
        omitted = [dict(evidence_id=id, reason=reason) for id in sorted(window_items)]
        window_omissions.extend(omitted)
        receipt = dict(omitted=omitted, roots=selection.get('roots', []), closure=closure, reason=reason)
        result = BatchResult(batch.index, CommitmentSet(()), canonical(receipt))
        results.append(result)
        calls.log.record('build_t_batch_skipped', plan_id=plan_id, index=batch.index, **receipt)
        save_immutable(calls.log.path.parent / f'build-t-{plan_id}-{batch.index}-skipped-{digest(result.receipt_json)}.json', result.receipt_json)

    for batch in batches:
        group = json.loads(batch.papers_json)
        window_items = {item['id']: item for paper in group for item in paper['items']}
        selection, closure = {}, None
        if resumption and batch.index in resumption['completed']:
            data = resumption['completed'][batch.index]
            commitments = CommitmentSet.from_dict({'commitments': data.get('commitments', [])})
            results.append(BatchResult(batch.index, commitments, canonical(data)))
            symbols += data.get('new_symbols', [])
            materialized.update(c.id for c in commitments.commitments)
            window_omissions.extend(o for o in data['omitted'] if o['evidence_id'] in window_items)
            calls.log.record('build_t_batch_restored', plan_id=plan_id, index=batch.index,
                             evidence_ids=[c.id for c in commitments.commitments])
            continue
        if resumption and batch.index == resumption['terminal_index']:
            closure = resumption['terminal_closure']
            selection = {'roots': closure['roots']} if closure else {}
            skip(batch, window_items, 'terminal provider request refusal; unknown usage counted at reservation', selection, closure)
            continue
        if exhausted:
            skip(batch, window_items, exhausted, selection, closure)
            continue
        if batch.input_tokens is None:
            skip(batch, window_items, 'terminal token-count request refusal; uncounted window omitted', selection, closure)
            continue
        if batch.input_tokens > input_bound:
            reason = 'oversized source batch: counted selection window exceeds input bound; no truncation'
            refusal_reasons.append(reason)
            skip(batch, window_items, reason, selection, closure)
            continue
        window_cap = allocation['window_commitment_caps'][batch.index]
        if window_cap == 0:
            skip(batch, window_items, 'zero initial window share; commitment cap is zero', selection, closure)
            continue
        try:
            prior = [c.to_dict() for r in results for c in r.commitments.commitments]
            target_inputs = {'count': calls.config['target_candidates'], 'named_position': None}
            current = calls.count_request('propose_targets', {**target_inputs, 'commitments': {'commitments': prior}})
            available = metadata['working_t_token_budget'] - current.initial_input_tokens
            catalog_probe = {**base_inputs, 'papers': [], 'shared_symbols': symbols}
            catalog_tokens = (calls.count_request('build_t_batch', catalog_probe).initial_input_tokens -
                              calls.count_request('build_t_batch', {**catalog_probe, 'shared_symbols': []}).initial_input_tokens)
            if catalog_tokens > symbol_budget:
                calls.budget.stop('accepted catalogue exceeds global budget on recount', 'build_t_batch')
            symbol_available = symbol_budget - catalog_tokens
            windows_left = sum(n > 0 for n in allocation['window_initial_commitments'][batch.index:])
            # Reserve the original headroom as a soft target; accepted output may borrow it.
            working_share = max(0, int(metadata['working_t_token_budget'] * (1 - allocation['headroom_fraction'])) - current.initial_input_tokens) // windows_left
            symbol_share = max(0, int(symbol_budget * (1 - allocation['headroom_fraction'])) - catalog_tokens) // windows_left
            window_budget = {**allocation, 'initial_window_commitments': allocation['window_initial_commitments'][batch.index],
                             'window_commitment_cap': window_cap, 'window_copy_token_budget': working_share,
                             'symbol_available_tokens': max(0, symbol_available),
                             'window_symbol_token_budget': symbol_share,
                             'per_window_commitments': min(
                                 working_share // (allocation['copy_tokens_per_commitment'] + allocation['symbol_tokens_per_commitment']),
                                 symbol_share // allocation['symbol_tokens_per_commitment'])}
            calls.log.record('build_t_window_budget', plan_id=plan_id, index=batch.index,
                             working_input_tokens=current.initial_input_tokens, catalogue_tokens=catalog_tokens,
                             working_remaining=available, symbol_remaining=symbol_available,
                             remaining_windows=windows_left, budget=window_budget)
            if available <= 0 or symbol_available <= 0:
                exhausted = 'global working T capacity exhausted' if available <= 0 else 'global catalogue capacity exhausted'
                calls.log.record('build_t_global_exhaustion', plan_id=plan_id, index=batch.index,
                                 reason=exhausted, accepted_ids=sorted(materialized),
                                 note='Freeze only previously accepted work; remaining windows are omitted.')
                skip(batch, window_items, exhausted, selection, closure)
                continue
            inputs = {**inputs_for(group, batch.index, max(0, available)), 'plan_id': plan_id,
                      'shared_symbols': symbols, 'batch_content_hash': digest(batch.papers_json)}
            root_ids, selection_groups = selection_inventory(window_items)
            groups_by_id = {g['group_id']: g for g in selection_groups}
            selection_inputs = {**selection_request(inputs, window_items), 'window_budget': window_budget}
            calls.log.record('build_t_selection_inventory', plan_id=plan_id, index=batch.index,
                             root_ids=root_ids, groups=selection_groups, graph_hash=digest(canonical(items)))
            def select(data):
                short_roots = data['roots']
                require(len(set(short_roots)) == len(short_roots) and
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
                require(not set(roots) & excluded and set(roots) | excluded == set(window_items), 'working T evidence inventory mismatch')
                return {**data, 'roots': roots}, omitted
            if plan_only:
                calls.count_request('select_t_roots', selection_inputs, admission=True)
                return preview(batch.index)
            selection, omitted = construction_call(calls, 'select_t_roots', selection_inputs, select, remaining)
            selected_ids = prerequisite_closure(items, selection['roots'])
            require(all(dependencies[id] <= selected_ids for id in selected_ids), 'working T drops premise/link/qualification')
            full_ids = set(selected_ids)
            def closure_record(ids, support, depth, omissions):
                return {'rule_version': CLOSURE_VERSION, 'graph_hash': digest(canonical(items)),
                        'roots': selection['roots'], 'added_ids': sorted(ids - set(selection['roots'])),
                        'full_inventory': sorted(ids), 'uncut_inventory': sorted(full_ids),
                        'support_omitted': support, 'cut_depth': depth, 'window_budget': window_budget,
                        'empty_reason': ('mandatory root context exceeds window commitment cap, remaining global capacity or request bound' if selection['roots'] and not ids
                                         else selection['relevance'] if not ids else None),
                        'already_formalized': sorted(ids & materialized), 'inventory': sorted(ids - materialized),
                        'relevance': selection['relevance'], 'omitted': omissions}
            def formalization_inputs(closure):
                # Full omission inventories stay logged; the formalizer needs only the
                # fixed included IDs, exact prior context and the omitted frontier.
                formal_closure = {key: value for key, value in closure.items()
                                  if key not in ('uncut_inventory', 'omitted')}
                formal_closure['uncut_items'] = len(full_ids)
                existing = {c['id']: c for c in prior if c['id'] in closure['already_formalized']}
                return {**inputs, 'closure': formal_closure, 'papers': grouped(closure['inventory']),
                        'existing_commitments': [existing[id] for id in closure['already_formalized']],
                        'supporting_evidence': [items[id] for id in closure['already_formalized']],
                        'new_symbol_token_allowance': symbol_budget,
                        'window_working_token_allowance': working_share,
                        'window_new_symbol_token_allowance': symbol_share}
            def fits(ids):
                if not ids:
                    return True
                if len(ids - materialized) > window_cap:
                    return False
                if payload_token_bound(items, ids) > input_bound - 8192:
                    return False
                support = {id: sorted(dependencies[id] - ids) for id in ids if dependencies[id] - ids}
                floor = [dict(id=id, text=evidence_text(items[id], support.get(id)), citation=items[id]['citation'],
                              formula={'op': 'atom', 'name': 'P'}) for id in sorted(ids - materialized)]
                copied = calls.count_request('propose_targets', {**target_inputs,
                    'commitments': {'commitments': prior + floor}}).initial_input_tokens - current.initial_input_tokens
                growth = len(floor) * allocation['symbol_tokens_per_commitment']
                if copied + growth > available or growth > symbol_available:
                    return False
                trial = formalization_inputs(closure_record(ids, support, len(items), []))
                return calls.count_request('build_t_batch', {**trial, 'shared_symbols': []}).initial_input_tokens <= input_bound
            support_omitted = {}
            cut_depth = None
            if not fits(selected_ids):
                selected_ids, support_omitted, cut_depth = depth_cut(items, selection['roots'], dependencies, fits)
            # All roots are a single model-selected bundle. No relevance ranking in code.
            # If mandatory context cannot fit, the window contributes nothing.
            cut_omissions = [dict(evidence_id=id, reason='budget depth cut: support omitted')
                             for id in sorted(full_ids - selected_ids)]
            omitted = [o for o in omitted if o['evidence_id'] not in full_ids] + cut_omissions

            omitted = [o for o in omitted if o['evidence_id'] not in selected_ids]
            closure = closure_record(selected_ids, support_omitted, cut_depth, omitted)
            calls.log.record('build_t_closure', plan_id=plan_id, index=batch.index, **closure)
            selected_ids -= materialized
            inputs = formalization_inputs(closure)
            if not selected_ids:
                window_omissions.extend(o for o in omitted if o['evidence_id'] in window_items)
                result = BatchResult(batch.index, CommitmentSet(()), canonical({'omitted': omitted, 'closure': closure}))
                results.append(result)
                calls.log.record('build_t_batch_skipped', plan_id=plan_id, index=batch.index, omitted=omitted)
                save_immutable(calls.log.path.parent / f'build-t-{plan_id}-{batch.index}.json', result.receipt_json)
                continue
            # Count exact copied evidence with a minimal formula envelope. Actual formulas
            # remain model-authored; the cumulative accepted result is checked separately.
            floor = [dict(id=id, text=evidence_text(items[id], support_omitted.get(id)), citation=items[id]['citation'],
                          formula={'op': 'atom', 'name': 'P'}) for id in sorted(selected_ids)]
            projected = calls.count_request('propose_targets', {**target_inputs,
                'commitments': {'commitments': prior + floor}})
            catalog_inputs = {**inputs, 'papers': []}
            empty_catalog = calls.count_request('build_t_batch', {**catalog_inputs, 'shared_symbols': []})
            current_catalog = calls.count_request('build_t_batch', catalog_inputs)
            catalog_tokens = current_catalog.initial_input_tokens - empty_catalog.initial_input_tokens
            growth = len(selected_ids) * allocation['symbol_tokens_per_commitment']
            calls.log.record('build_t_capacity_preflight', plan_id=plan_id, index=batch.index,
                             working_input_tokens=current.initial_input_tokens, working_available=available,
                             closure_copy_input_tokens=projected.initial_input_tokens, catalogue_tokens=catalog_tokens,
                             catalogue_growth_reservation=growth, catalogue_limit=symbol_budget,
                             note='Minimal formula envelope and configurable growth reservation; actual output rechecked.')
            require(projected.initial_input_tokens <= metadata['working_t_token_budget'], 'working T closure preflight exceeded')
            require(catalog_tokens + growth <= symbol_budget, 'shared symbol token allowance preflight exceeded')
            inputs = {**inputs, 'working_token_allowance': available,
                      'new_symbol_token_allowance': symbol_budget - catalog_tokens}
            closure_count = calls.count_request('build_t_batch', {**inputs, 'shared_symbols': []})
            if closure_count.initial_input_tokens > input_bound:
                raise Rejected('selected closure exceeds bounded formalization; no truncation; reselect roots')
            calls.count_request('build_t_batch', inputs, admission=True)
            # The actual growing catalogue and plan identity are counted again, including retries.
            def check(data):
                ids = [c['id'] for c in data['commitments']]
                require(len(ids) <= window_cap, 'construction window commitment cap exceeded')
                require(len(set(ids)) == len(ids) and set(ids) == selected_ids, 'formalization inventory differs from fixed closure')
                from ara.runtime.commitment_provenance import content_definition, source_provenance, _validate_source
                definitions = {c['id']: c['definition'] for c in data['commitments']}
                for id, definition in definitions.items():
                    require(content_definition(definition), 'content definition must not contain attribution: commitment ' + id)
                for symbol in data['new_symbols']:
                    require(content_definition(symbol['definition']), 'content definition must not contain attribution: symbol ' + symbol['name'])
                provenance = {id: source_provenance(items[id], authors[items[id]['source_id']], support_omitted.get(id, []))
                              for id in definitions}
                for id, row in provenance.items():
                    try:
                        _validate_source(id, row)
                    except ValueError as exc:
                        raise Rejected(str(exc)) from exc
                commitments = CommitmentSet.from_dict({'commitments': [
                    dict(id=c['id'], text=c['definition'], formula=c['formula'], citation=items[c['id']]['citation'])
                    for c in data['commitments']]})
                selected = {c.id for c in commitments.commitments}
                for c in commitments.commitments:
                    require(c.citation == items[c.id]['citation'], 'T citation not in extracted literature')
                    require(c.text == definitions[c.id], 'working T changed content definition')
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
                cumulative = calls.count_request('propose_targets', {**target_inputs,
                    'commitments': {'commitments': prior + commitments.to_dict()['commitments']}})
                require(cumulative.initial_input_tokens <= metadata['working_t_token_budget'], 'working T global token allowance exceeded')
                require(cumulative.initial_input_tokens + cumulative.context_output_tokens <=
                        calls.config['model_context_token_bound'], 'working T downstream context allowance exceeded')
                catalog_inputs = {**inputs, 'papers': [], 'shared_symbols': symbols + data['new_symbols']}
                without = calls.count_request('build_t_batch', {**catalog_inputs, 'shared_symbols': []})
                with_catalog = calls.count_request('build_t_batch', catalog_inputs)
                require(with_catalog.initial_input_tokens - without.initial_input_tokens <= symbol_budget, 'shared symbol token allowance exceeded')
                borrowing = dict(
                    working_borrowed_tokens=max(0, cumulative.initial_input_tokens - current.initial_input_tokens - working_share),
                    symbols_borrowed_tokens=max(0, with_catalog.initial_input_tokens - without.initial_input_tokens - catalog_tokens - symbol_share))
                return BatchResult(batch.index, commitments, canonical({**data, 'commitments': commitments.to_dict()['commitments'],
                    'bindings': bindings, 'provenance': provenance, 'omitted': omitted, 'closure': closure, 'borrowing': borrowing}))
            result = construction_call(calls, 'build_t_batch', inputs, check, remaining)
            from ara.runtime.construction_structure import structure_gate
            prior_set = CommitmentSet.from_dict({'commitments': prior})
            metrics = structure_gate(result.commitments, prior_set, items)
            calls.log.record('build_t_structure_gate', plan_id=plan_id, index=batch.index,
                             phase='initial', **metrics)
            if not metrics['passed']:
                # One structure-specific correction per batch, independent of the
                # validation-repair allowance. Full replacement permits removing
                # the unused atom symbols of a flattened candidate.
                candidate = json.loads(result.receipt_json)
                candidate = {key: candidate[key] for key in ('commitments', 'new_symbols', 'alignments')}
                candidate['commitments'] = [dict(id=c['id'], definition=c['text'], formula=c['formula']) for c in candidate['commitments']]
                feedback = dict(issues=metrics['issues'],
                    instruction='Encode each selected inference as premises -> conclusion, reusing selected endpoint formulas. '
                                'Use shared predicates/constants where source-supported. Keep unsupported qualifications separate. '
                                'Do not invent structure: if source-faithful structure cannot be supplied, retain flat formulas for disclosure.')
                calls.log.record('construction_structure_correction', plan_id=plan_id, index=batch.index,
                                 candidate_hash=digest(canonical(candidate)), feedback=feedback)
                result = calls._transport_call('build_t_batch', {**inputs, 'mode': 'structure_correction',
                    'candidate': candidate, 'structure_feedback': feedback}, check, attempt=2)
                metrics = structure_gate(result.commitments, prior_set, items)
                calls.log.record('build_t_structure_gate', plan_id=plan_id, index=batch.index,
                                 phase='corrected', **metrics)
                require(metrics['passed'] or metrics['flat'], 'non-flat inference structure contract failed after correction')
            disclosure = 'flat_after_one_correction' if metrics['flat'] else None
            calls.log.record('build_t_structure_outcome', plan_id=plan_id, index=batch.index,
                             disclosure=disclosure, **metrics)
            data = {**json.loads(result.receipt_json), 'structure': metrics, 'structure_disclosure': disclosure}
            result = BatchResult(result.index, result.commitments, canonical(data))
            if any(data['borrowing'].values()):
                calls.log.record('build_t_share_borrowed', plan_id=plan_id, index=batch.index, **data['borrowing'])
            window_omissions.extend(o for o in omitted if o['evidence_id'] in window_items)
            symbols += data['new_symbols']
            materialized.update(selected_ids)
            results.append(result)
            calls.log.record('build_t_batch_accepted', plan_id=plan_id, index=batch.index,
                             source_ids=batch.source_ids, output_hash=digest(result.receipt_json),
                             evidence_ids=[c.id for c in result.commitments.commitments], omitted=data['omitted'])
            save_immutable(calls.log.path.parent / f'build-t-{plan_id}-{batch.index}.json', result.receipt_json)
        except (Rejected, BudgetStop, CountRequestRefused) as exc:
            if isinstance(exc, BudgetStop) and exc.scope != 'window':
                raise
            refusal_reasons.append(str(exc))
            skip(batch, window_items, str(exc), selection, closure)
    if plan_only:
        return preview(None)
    merged = merge_batches(tuple(results), len(batches))
    require(bool(merged.commitments), 'empty working T after accounted omissions' + (': ' + '; '.join(refusal_reasons) if refusal_reasons else ''))
    final_omissions = [o for o in window_omissions if o['evidence_id'] not in materialized]
    omitted_ids = [o['evidence_id'] for o in final_omissions]
    require(len(omitted_ids) == len(set(omitted_ids)) and
            set(omitted_ids) | materialized == set(items), 'final evidence inventory mismatch')
    calls.log.record('build_t_evidence_accounted', plan_id=plan_id,
                     graph_hash=digest(canonical(items)), selected_ids=sorted(materialized), omitted=final_omissions)
    measured = calls.count_request('propose_targets', {'commitments': merged.to_dict(),
        'count': calls.config['target_candidates'], 'named_position': None}, admission=True)
    if measured.initial_input_tokens > metadata['working_t_token_budget']:
        calls.budget.stop('working T downstream token budget exceeded before freeze', 'build_t_batch')
    catalog_probe = {**base_inputs, 'papers': [], 'shared_symbols': symbols}
    final_catalog = (calls.count_request('build_t_batch', catalog_probe).initial_input_tokens -
                     calls.count_request('build_t_batch', {**catalog_probe, 'shared_symbols': []}).initial_input_tokens)
    if final_catalog > symbol_budget:
        calls.budget.stop('accepted catalogue exceeds global budget before freeze', 'build_t_batch')
    provenance = {id: row for result in results for id, row in json.loads(result.receipt_json).get('provenance', {}).items()}
    require(set(provenance) == materialized, 'merged commitment provenance inventory mismatch')
    calls.log.record('build_t_merged', plan_id=plan_id, commitments=merged.to_dict(), symbols=symbols, provenance=provenance,
                     input_tokens=measured.initial_input_tokens, source_ids=[p['source_id'] for p in papers],
                     note='One construction lifecycle, one freeze; explicit model omissions retained in batch receipts.')
    save_immutable(calls.log.path.parent / f'working-t-{plan_id}.json', canonical({
        'plan_id': plan_id, 'symbols': symbols, 'commitments': merged.to_dict(), 'provenance': provenance}))
    return merged


def evidence_text(item: dict, omitted_support: list[str] | None = None) -> str:
    prefix = ('[assumed_premise; support_omitted; omitted_support_ids=' + canonical(omitted_support) + '] ' if omitted_support else '')
    return prefix + f"[{item['attribution']}; {item['attributed_to']}; {item['kind']}] {item['text']}"
