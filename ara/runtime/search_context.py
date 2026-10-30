"""Deterministic, counted leaf guidance; full frozen inputs stay authoritative."""
from contextlib import contextmanager
from contextvars import ContextVar
from ara.runtime.cache import canonical, digest
from ara.runtime.search_alignment import symbols
from ara.types import CommitmentSet, Formula


SEARCH_STAGES = frozenset(('map_leaf', 'propose_cuts', 'formalise_slots', 'answer_cq', 'tier1_repair', 'classify_conflict'))
_target = ContextVar('search_context_target', default=None)


@contextmanager
def target_scope(target):
    """Keep a job's declared basis on child leaves without crossing threads/retries."""
    token = _target.set(target.to_dict())
    try:
        yield
    finally:
        _target.reset(token)


def basis_neighbourhood(inputs, signatures, hops):
    from ara.runtime.closure_budget import depth_cut
    if type(hops) is not int or hops < 0:
        raise ValueError('target_context_hops must be a nonnegative integer')
    target = inputs.get('search_target') or inputs.get('goal') or inputs['leaf']
    basis = sorted(set(target.get('basis_commitment_ids', [])))
    if not set(basis) <= signatures.keys():
        raise ValueError('target basis contains unknown frozen commitment IDs')
    if not basis:
        return set(), None
    rows = (inputs.get('commitment_provenance') or {}).get('commitments', {})
    mandatory = {tid: set(rows.get(tid, {}).get('evidence_ids', [])) for tid in signatures}
    if any(not ids <= signatures.keys() for ids in mandatory.values()):
        raise ValueError('alignment basis contains unknown frozen commitment IDs')
    names = {tid: {name for name, _, _ in sigs} for tid, sigs in signatures.items()}
    alignment = inputs.get('alignment_disclosure', {})
    pairs = [(p['left'], p['right']) for p in alignment.get('judgments', [])
             if alignment.get('status') == 'accepted' and p['relation'] != 'unrelated']
    aligned_names = {tid: {other for left, right in pairs for name, other in ((left, right), (right, left))
                          if name in group} for tid, group in names.items()}
    dependencies = {tid: {other for other in signatures if other != tid and (
        signatures[tid] & signatures[other] or aligned_names[tid] & names[other])}
        for tid in signatures}
    full, boundary, depth = depth_cut(signatures, set(basis), dependencies, lambda ids: True,
                                    max_depth=hops, mandatory=mandatory)
    return full, dict(target_id=target['id'], basis_commitment_ids=basis,
        mandatory_commitment_ids=sorted(full), neighbourhood_commitment_ids=sorted(full-set(basis)),
        hops=hops, reached_depth=depth, unexpanded_neighbours=boundary,
        policy='Declared basis and complete formal/alignment hops are mandatory; retrieval is not endorsement.')


def leaf_slice(inputs, bridge_limit, *, hops=1):
    commitments = CommitmentSet.from_dict(inputs['commitments'])
    goal = inputs.get('goal') or inputs['leaf']
    formula = Formula.from_dict(goal['formula']) if goal.get('formula') else None
    leaf_symbols = set(symbols(formula)) if formula else set()
    signatures = {c.id: set(symbols(c.formula)) for c in commitments.commitments}
    mandatory_ids, basis = basis_neighbourhood(inputs, signatures, hops)
    relevant_symbols = leaf_symbols | set().union(*(signatures[tid] for tid in mandatory_ids))
    bridges = sorted(inputs.get('candidate_bridges', []), key=lambda b: (
        -len(relevant_symbols.intersection(set().union(*(signatures[tid] for tid in b['commitment_ids'])))),
        b['bridge_id']))[:bridge_limit]
    provenance = inputs.get('commitment_provenance')
    roles = provenance['commitments'] if provenance else {}
    exact = sorted([c for c in commitments.commitments if c.formula == formula],
                   key=lambda c: (roles.get(c.id, {}).get('stance') != 'endorsed', c.id))
    exact_ids = [c.id for c in exact]
    ranked = sorted(commitments.commitments, key=lambda c: (
        c.formula != formula, -len(relevant_symbols & signatures[c.id]), c.id))
    seed_limit = 0 if bridges else 2 * bridge_limit
    selected = {c.id for c in ranked[:seed_limit]}
    selected.update(tid for b in bridges for tid in b['commitment_ids'])
    selected.update(exact_ids)
    binding_ids = sorted({b['t_id'] for b in inputs.get('slot_bindings', []) if b['t_id'] != 'open'})
    selected.update(binding_ids)
    selected.update(mandatory_ids)
    if basis is not None:
        basis['basis_coverage'] = len(set(basis['basis_commitment_ids']) & selected) / len(basis['basis_commitment_ids'])
    selected.update(c.id for c in [c for c in ranked if roles.get(c.id, {}).get('stance') in ('model_alignment','proposed')][:bridge_limit])
    referenced = leaf_symbols | set().union(*(signatures[tid] for tid in selected))
    catalogue = inputs.get('symbol_catalogue')
    open_slots = [b['slot'] for b in inputs.get('slot_bindings', []) if b['t_id'] == 'open']
    if open_slots:
        # Open text has no complete symbolic dependency inventory. Preserve the
        # full definitions/signatures, count them, and refuse instead of guessing.
        referenced.update((s['name'], s['kind'], s['arity']) for s in catalogue or [])
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
            'source_kind', 'omitted_support_ids', 'kind', 'source_ids', 'evidence_ids', 'definitions', 'judgment', 'declaration') if key in row}
            for tid, row in sorted(provenance['commitments'].items()) if tid in selected} if provenance else None,
        provenance_scope='projected_roles_bound_to_full_provenance_sha256',
        symbol_catalogue=[s for s in catalogue if (s['name'], s['kind'], s['arity']) in referenced]
                         if catalogue is not None else None,
        search_slice=dict(version='leaf-context-v1', bridge_limit=bridge_limit,
                          exact_match_commitment_ids=exact_ids,
                          **({'basis_context': basis} if basis is not None else {}),
                          **({'mandatory_open_slots': open_slots, 'catalogue_scope': 'full_frozen_for_open_slots'} if open_slots else {}),
                          **({'mandatory_binding_ids': binding_ids} if 'slot_bindings' in inputs else {}),
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
    from ara.runtime.search_evidence import project_evidence
    evidence, receipt = project_evidence(inputs, referenced)
    data.update(evidence)
    if receipt is not None:
        data['search_slice']['evidence_projection'] = receipt
    if 'goal_novelty' in data:
        data['goal_novelty'] = {k: v for k, v in data['goal_novelty'].items() if k != 'basis_commitment_ids'}
        data['goal_novelty']['basis_commitments_sha256'] = inputs['commitments_sha256']
    return data


def fit_leaf_request(calls, kind, inputs):
    """Rebuild from the same full inputs at every level, including retry feedback."""
    from ara.runtime.search_evidence import full_evidence
    target = _target.get()
    if target and target.get('basis_commitment_ids'):
        inputs = {**inputs, 'search_target': target}
    evidence = full_evidence(inputs)
    if evidence:
        calls.log.record('search_context_evidence', kind=kind,
            goal_id=(inputs.get('goal') or inputs['leaf'])['id'],
            goal_sha256=digest(canonical(inputs.get('goal') or inputs['leaf'])),
            field_bytes={key: len(canonical(value).encode()) for key, value in evidence.items()},
            **evidence, **{key + '_sha256': digest(canonical(value)) for key, value in evidence.items()},
            commitments_sha256=inputs['commitments_sha256'],
            catalogue_sha256=inputs.get('catalogue_sha256'), provenance_sha256=inputs.get('provenance_sha256'))
    for bridge_limit in (8, 4, 2, 1, 0):
        data = leaf_slice(inputs, bridge_limit, hops=calls.config.get('target_context_hops', 1))
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
                         **{key: data['search_slice'][key] for key in ('basis_context', 'mandatory_open_slots', 'catalogue_scope')
                            if key in data['search_slice']},
                         **({'mandatory_binding_ids': data['search_slice']['mandatory_binding_ids']}
                            if 'mandatory_binding_ids' in data['search_slice'] else {}),
                         commitment_ids=[c['id'] for c in data['commitments']['commitments']],
                         catalogue_count=len(data['symbol_catalogue'] or []), inputs_sha256=digest(canonical(data)),
                         field_bytes={key: len(canonical(value).encode()) for key, value in data.items()},
                         **({'evidence_projection': data['search_slice']['evidence_projection']}
                            if 'evidence_projection' in data['search_slice'] else {}))
        if fits:
            return data
    calls.count_request(kind, data, admission=True)
    return data


def target_slice(inputs, hops):
    """Prompt projection only: required whole hops, plus a complete frozen index."""
    from ara.runtime.closure_budget import depth_cut
    if type(hops) is not int or hops < 0:
        raise ValueError('target_context_hops must be a nonnegative integer')
    commitments = CommitmentSet.from_dict(inputs['commitments'])
    items = {c.id: c for c in commitments.commitments}
    signatures = {c.id: set(symbols(c.formula)) for c in commitments.commitments}
    provenance = inputs.get('commitment_provenance')
    roles = provenance['commitments'] if provenance else {}
    mandatory = {tid: set(roles.get(tid, {}).get('evidence_ids', [])) for tid in items}
    dependencies = {tid: {other for other in items if other != tid and signatures[tid] & signatures[other]}
                    for tid in items}
    gap = inputs.get('resolution_gap')
    roots = (set(gap['commitment_ids']) | {tid for group in gap.get('support_groups', []) for tid in group}
             if gap else {tid for lead in inputs.get('forward_candidates', []) for tid in lead['support_ids']})
    if not roots <= items.keys() or any(not ids <= items.keys() for ids in mandatory.values()):
        raise ValueError('target scope contains unknown frozen commitment IDs')
    full, boundary, depth = depth_cut(items, roots, dependencies, lambda ids: True,
                                     max_depth=hops, mandatory=mandatory)
    compact = set(items) - full
    referenced = set().union(*signatures.values())
    full_names = {name for tid in full for name, _, _ in signatures[tid]}
    alignment = inputs.get('alignment_disclosure', {})
    mapping = ((provenance or {}).get('alignment') or {}).get('mapping', {})
    def relevant(pair):
        return any(mapping.get(pair[key], pair[key]) in full_names for key in ('left', 'right'))
    judgments = alignment.get('judgments', [])
    kept_judgments = [j for j in judgments if relevant(j)]
    unresolved = alignment.get('unresolved', [])
    kept_unresolved = [j for j in unresolved if relevant(j)]
    def citation(tid):
        row = roles.get(tid, {})
        if row.get('stance') == 'model_alignment':
            return dict(evidence=[dict(id=eid, citation=citation(eid)) for eid in row['evidence_ids']])
        if 'page_start' in row:
            return {key: row[key] for key in ('source_id', 'page_start', 'page_end')}
        return dict(legacy_citation=items[tid].citation)
    catalogue = inputs.get('symbol_catalogue')
    bridges = inputs.get('candidate_bridges', [])
    selected_bridges = [b for b in bridges if gap is None or set(b['commitment_ids']) <= full]
    data = {key: value for key, value in inputs.items() if key != 'commitment_provenance'}
    data.update(commitments=CommitmentSet(tuple(c for c in commitments.commitments if c.id in full)).to_dict(),
        compact_commitments=[dict(id=tid, formula=items[tid].formula.to_dict(),
            stance=roles.get(tid, {}).get('stance', 'unavailable_legacy'), citation=citation(tid)) for tid in sorted(compact)],
        commitments_scope='full_neighbourhood_plus_complete_compact_frozen_index',
        commitment_roles={tid: roles[tid] for tid in sorted(full) if tid in roles} if provenance else None,
        provenance_scope='projected_rows_bound_to_full_provenance_sha256',
        symbol_catalogue=[s for s in catalogue if (s['name'],s['kind'],s['arity']) in referenced] if catalogue is not None else None,
        candidate_bridges=selected_bridges,
        alignment_disclosure={**alignment, 'judgments': kept_judgments, 'unresolved': kept_unresolved,
            'unresolved_count': len(kept_unresolved), 'full_unresolved_count': len(unresolved),
            'mapping': {a:b for a,b in alignment.get('mapping', {}).items() if b in full_names},
            'scope': 'pairs_touching_full_neighbourhood'},
        conditionals=[dict(id=c['id'], formula=c['formula']) for c in inputs.get('conditionals', [])],
        target_slice=dict(version='target-context-v1', hops=hops, reached_depth=depth,
            root_ids=sorted(roots), full_ids=sorted(full), compact_ids=sorted(compact),
            omitted_commitment_ids=[], unexpanded_neighbours=boundary,
            full_inputs_sha256=digest(canonical(inputs)),
            full_alignment_sha256=digest(canonical(alignment)),
            projected_alignment_pair_ids=[[j['left'],j['right']] for j in judgments if not relevant(j)],
            projected_unresolved_pair_ids=[[j['left'],j['right']] for j in unresolved if not relevant(j)],
            projected_bridge_ids=[b['bridge_id'] for b in bridges if b not in selected_bridges],
            projected_symbol_names=[s['name'] for s in catalogue or [] if (s['name'],s['kind'],s['arity']) not in referenced],
            projected_fields=['commitment_provenance', 'commitments', 'conditionals', 'alignment_disclosure',
                              'candidate_bridges', 'symbol_catalogue'],
            policy='No commitment or formula omitted. Full rows retain exact text and provenance; compact rows omit text and quotes. Validation uses full frozen T.'))
    return data


def fit_target_request(calls, inputs):
    data = target_slice(inputs, calls.config.get('target_context_hops', 1))
    count = calls.count_request('propose_targets', data)
    total = count.initial_input_tokens + count.context_output_tokens
    fits = total <= calls.config['model_context_token_bound']
    calls.log.record('target_context_slice', **data['target_slice'],
        decision='fits' if fits else 'refused', input_tokens=count.initial_input_tokens,
        output_tokens=count.context_output_tokens, total_tokens=total,
        limit=calls.config['model_context_token_bound'], inputs_sha256=digest(canonical(data)),
        field_bytes={key: len(canonical(value).encode()) for key,value in data.items()},
        prompt_bytes=len(calls.render('propose_targets', data)[1].encode()),
        commitments_sha256=inputs.get('commitments_sha256'), catalogue_sha256=inputs.get('catalogue_sha256'),
        provenance_sha256=inputs.get('provenance_sha256'))
    if not fits:
        calls.count_request('propose_targets', data, admission=True)
    return data
