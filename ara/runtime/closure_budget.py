"""Deterministic budget arithmetic and depth cuts; never chooses relevance."""
from math import ceil, floor, isfinite

from ara.runtime.cache import canonical

# Historical paired token counts: 10,471 catalogue tokens / 45 commitments.
MEASURED_SYMBOL_TOKENS = ceil(10471 / 45)


def apply_context_limits(config):
    """Opt-in fractions of the effective run bound; explicit absolute defaults stay intact."""
    fractions = config.get('construction_context_limits', {})
    keys = {'build_t_batch_input_tokens', 'working_t_token_budget', 'working_t_symbol_token_budget'}
    if (not isinstance(fractions, dict) or not fractions.keys() <= keys or
            any(type(v) not in (int, float) or not isfinite(v) or not 0 < v < 1 for v in fractions.values())):
        raise ValueError('construction context limits must map token-budget keys to fractions between zero and one')
    if not fractions:
        return None
    from ara.runtime.codex_window import apply_context_window
    effective = dict(config)
    apply_context_window(effective)
    bound = effective['model_context_token_bound']
    if type(bound) is not int or bound <= 0:
        raise ValueError('construction context limits require a positive integer run context bound')
    limits = {key: floor(bound * fractions[key]) if key in fractions else config[key] for key in keys}
    if any(type(v) is not int or v <= 0 for v in limits.values()):
        raise ValueError('construction context limits leave no usable token budget')
    if bound - config['extracted_build_t_max_output_tokens'] - limits['working_t_symbol_token_budget'] <= 0:
        raise ValueError('construction context limits leave no formalization input allowance')
    config.update(limits, model_context_token_bound=bound)
    return dict(origin='operator_run_config', rule='floor(effective run context bound * configured fraction)',
                context_bound=bound, model_context_window=config.get('model_context_window'),
                fractions=dict(fractions), effective=limits)


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
    multiplier = config.get('construction_window_cap_multiplier', 2)
    require(type(multiplier) in (int, float) and isfinite(multiplier) and multiplier >= 1,
            'construction window cap multiplier must be finite and at least one')
    shares = [per_window] * windows
    scarce = 0 < total < windows and input_bound - wrapper_tokens >= copy_cost + symbol_cost
    if scarce:
        shares = [1 if index < total else 0 for index in range(windows)]
    caps = [floor(share * multiplier) for share in shares]
    projected = sum(shares)
    return dict(window_initial_commitments=shares, window_commitment_caps=caps,
                global_commitment_slots=total, funded_windows=sum(share > 0 for share in shares),
                allocation_rule=('one_slot_in_plan_order_when_capacity_below_window_count' if scarce else 'equal_initial_shares'),
                window_count=windows, per_window_commitments=per_window,
                initial_window_commitments=max(shares, default=0), window_cap_multiplier=multiplier,
                window_commitment_cap=max(caps, default=0), redistribution_pass=False,
                projected_t_commitments=projected, copy_tokens_per_commitment=copy_cost,
                symbol_tokens_per_commitment=symbol_cost, headroom_fraction=headroom,
                working_wrapper_tokens=wrapper_tokens, working_available_tokens=working,
                symbol_available_tokens=symbols, batch_input_bound=input_bound,
                projected_working_tokens=wrapper_tokens + projected * (copy_cost + symbol_cost),
                projected_symbol_tokens=projected * symbol_cost,
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


def depth_cut(items, roots, dependencies, fits, *, max_depth=None, mandatory=None):
    """Largest complete prerequisite depth that fits, including mandatory bundles.

    Cycles terminate at a fixed point. A too-large root/qualifier bundle yields
    no contribution; it is never partially included. IDs are never invented.
    """
    mandatory = mandatory_dependencies(items) if mandatory is None else mandatory
    selected = close_mandatory(roots, mandatory)
    if not fits(selected):
        return set(), {}, -1
    depth = 0
    while max_depth is None or depth < max_depth:
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
