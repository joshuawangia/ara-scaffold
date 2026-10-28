"""Deterministic, counted leaf guidance; full frozen inputs stay authoritative."""
from ara.runtime.cache import canonical, digest
from ara.runtime.search_alignment import symbols
from ara.types import CommitmentSet, Formula


SEARCH_STAGES = frozenset(('map_leaf', 'propose_cuts', 'formalise_slots', 'answer_cq', 'tier1_repair'))


def leaf_slice(inputs, bridge_limit):
    commitments = CommitmentSet.from_dict(inputs['commitments'])
    goal = inputs.get('goal') or inputs['leaf']
    formula = Formula.from_dict(goal['formula']) if goal.get('formula') else None
    leaf_symbols = set(symbols(formula)) if formula else set()
    signatures = {c.id: set(symbols(c.formula)) for c in commitments.commitments}
    bridges = sorted(inputs.get('candidate_bridges', []), key=lambda b: (
        -len(leaf_symbols.intersection(set().union(*(signatures[tid] for tid in b['commitment_ids'])))),
        b['bridge_id']))[:bridge_limit]
    provenance = inputs.get('commitment_provenance')
    roles = provenance['commitments'] if provenance else {}
    exact = sorted([c for c in commitments.commitments if c.formula == formula],
                   key=lambda c: (roles.get(c.id, {}).get('stance') != 'endorsed', c.id))
    exact_ids = [c.id for c in exact]
    ranked = sorted(commitments.commitments, key=lambda c: (
        c.formula != formula, -len(leaf_symbols & signatures[c.id]), c.id))
    seed_limit = 0 if bridges else 2 * bridge_limit
    selected = {c.id for c in ranked[:seed_limit]}
    selected.update(tid for b in bridges for tid in b['commitment_ids'])
    selected.update(exact_ids)
    referenced = leaf_symbols | set().union(*(signatures[tid] for tid in selected))
    catalogue = inputs.get('symbol_catalogue')
    data = {k: v for k, v in inputs.items() if k != 'commitment_provenance'}
    data.update(
        commitments=CommitmentSet(tuple(exact) + tuple(c for c in commitments.commitments
            if c.id in selected and c.formula != formula)).to_dict(),
        commitments_scope='leaf_slice_of_frozen_T',
        candidate_bridges=bridges,
        commitment_papers={tid: paper for tid, paper in sorted(inputs.get('commitment_papers', {}).items())
                           if tid in selected},
        commitment_roles={tid: {key: row[key] for key in (
            'source_id', 'source_authors', 'attributed_to', 'attribution', 'stance',
            'source_kind', 'omitted_support_ids') if key in row}
            for tid, row in sorted(provenance['commitments'].items()) if tid in selected} if provenance else None,
        provenance_scope='projected_roles_bound_to_full_provenance_sha256',
        symbol_catalogue=[s for s in catalogue if (s['name'], s['kind'], s['arity']) in referenced]
                         if catalogue is not None else None,
        search_slice=dict(version='leaf-context-v1', bridge_limit=bridge_limit,
                          exact_match_commitment_ids=exact_ids,
                          ranking='shared_leaf_symbols_then_bridge_id',
                          seed_limit=seed_limit, total_commitments=len(commitments.commitments),
                          total_bridges=len(inputs.get('candidate_bridges', [])),
                          zero_overlap_policy='bounded_deterministic_leads_not_semantic_matches'))
    if 'bank' in data:
        data['bank'] = [{key: entry[key] for key in ('id', 'kind', 'premise_slots', 'conclusion_slot', 'formula_schema')}
                        for entry in data['bank']]
    data['scheme_signatures'] = [
        dict(bank_id=s['bank_id'], premise_slots=[dict(id=p['id']) for p in s['premise_slots']],
             conclusion_slot=dict(id=s['conclusion_slot']['id']), critical_questions=s['critical_questions'])
        for s in inputs.get('scheme_signatures', [])]
    if 'goal_novelty' in data:
        data['goal_novelty'] = {k: v for k, v in data['goal_novelty'].items() if k != 'basis_commitment_ids'}
        data['goal_novelty']['basis_commitments_sha256'] = inputs['commitments_sha256']
    return data


def fit_leaf_request(calls, kind, inputs):
    """Rebuild from the same full inputs at every level, including retry feedback."""
    for bridge_limit in (8, 4, 2, 1, 0):
        data = leaf_slice(inputs, bridge_limit)
        count = calls.count_request(kind, data)
        total = count.initial_input_tokens + count.context_output_tokens
        fits = total <= calls.config['model_context_token_bound']
        calls.log.record('search_context_slice', kind=kind,
                         goal_id=(inputs.get('goal') or inputs['leaf'])['id'],
                         bridge_limit=bridge_limit, decision='fits' if fits else 'shrink' if bridge_limit else 'refused',
                         input_tokens=count.initial_input_tokens, output_tokens=count.context_output_tokens,
                         total_tokens=total, limit=calls.config['model_context_token_bound'],
                         exact_match_commitment_ids=data['search_slice']['exact_match_commitment_ids'],
                         bridge_ids=[b['bridge_id'] for b in data['candidate_bridges']],
                         commitment_ids=[c['id'] for c in data['commitments']['commitments']],
                         catalogue_count=len(data['symbol_catalogue'] or []), inputs_sha256=digest(canonical(data)))
        if fits:
            return data
    calls.count_request(kind, data, admission=True)
    return data
