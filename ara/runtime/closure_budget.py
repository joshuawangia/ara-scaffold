"""Deterministic budget arithmetic and depth cuts; never chooses relevance."""
from math import ceil

from ara.runtime.cache import canonical

# Historical paired token counts: 10,471 catalogue tokens / 45 commitments.
MEASURED_SYMBOL_TOKENS = ceil(10471 / 45)


def budget_plan(config, windows, copy_tokens, wrapper_tokens, input_bound):
    from ara.runtime.calls import require
    headroom = config.get('working_t_headroom_fraction', .2)
    require(0 < headroom < 1, 'working T headroom must be between zero and one')
    symbol_cost = max(MEASURED_SYMBOL_TOKENS,
                      config.get('working_t_symbol_growth_tokens_per_item', 256))
    copy_cost = max(1, ceil(copy_tokens))
    count = max(1, windows)
    working = max(0, int(config['working_t_token_budget'] * (1 - headroom)) - wrapper_tokens)
    symbols = int(config['working_t_symbol_token_budget'] * (1 - headroom))
    # Reserve formula growth at the measured symbol rate as well as copied text.
    total = min(working // (copy_cost + symbol_cost), symbols // symbol_cost)
    per_window = min(total // count, max(0, input_bound - wrapper_tokens) // (copy_cost + symbol_cost))
    return dict(window_count=windows, per_window_commitments=per_window,
                projected_t_commitments=per_window * windows, copy_tokens_per_commitment=copy_cost,
                symbol_tokens_per_commitment=symbol_cost, headroom_fraction=headroom,
                working_wrapper_tokens=wrapper_tokens, working_available_tokens=working,
                symbol_available_tokens=symbols, batch_input_bound=input_bound,
                projected_working_tokens=wrapper_tokens + per_window * windows * (copy_cost + symbol_cost),
                projected_symbol_tokens=per_window * windows * symbol_cost,
                window_copy_token_budget=working // count,
                measured_symbol_basis='ceil(10471 / 45); configurable reservation may only raise this',
                note='Allocation, not a prediction of model formulas. Exact requests and accepted outputs are rechecked.')


def mandatory_dependencies(items):
    """Qualifiers always travel with their targets; links retain their endpoints."""
    mandatory = {id: set() for id in items}
    for id, item in items.items():
        for target in item['applies_to']:
            mandatory[target].add(id)
        if item['kind'] == 'inference':
            mandatory[id].update([*item['premise_ids'], item['conclusion_id'], *item['qualification_ids']])
    return mandatory


def close_mandatory(selected, mandatory):
    selected = set(selected)
    pending = list(selected)
    while pending:
        for id in mandatory[pending.pop()] - selected:
            selected.add(id)
            pending.append(id)
    return selected


def depth_cut(items, roots, dependencies, fits):
    """Largest complete prerequisite depth that fits, including mandatory bundles.

    Cycles terminate at a fixed point. A too-large root/qualifier bundle yields
    no contribution; it is never partially included. IDs are never invented.
    """
    mandatory = mandatory_dependencies(items)
    selected = close_mandatory(roots, mandatory)
    if not fits(selected):
        return set(), {}, -1
    depth = 0
    while True:
        expanded = close_mandatory(selected | set().union(*(dependencies[id] for id in selected)), mandatory)
        if expanded == selected or not fits(expanded):
            break
        selected = expanded
        depth += 1
    omitted = {id: sorted(dependencies[id] - selected) for id in sorted(selected)
               if dependencies[id] - selected}
    return selected, omitted, depth


def payload_token_bound(items, ids):
    # A byte-level tokenizer cannot emit more ordinary tokens than UTF-8 bytes.
    # This is an explicit conservative payload bound, not an API request count.
    return len(canonical([items[id] for id in sorted(ids)]).encode())
