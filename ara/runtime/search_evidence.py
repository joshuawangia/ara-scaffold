"""Prompt-only projections of full, logged search evidence; no gate decisions."""
from ara.runtime.cache import canonical, digest


def full_evidence(inputs):
    """Legacy requests without nested evidence retain their existing cache shape."""
    result = {}
    novelty = inputs.get('goal_novelty', {})
    if 'consistent_basis' in novelty:
        result['goal_novelty'] = novelty
    alignment = inputs.get('alignment_disclosure', {})
    if any(alignment.get(key) for key in ('judgments', 'unresolved', 'mapping')):
        result['alignment_disclosure'] = alignment
    return result


def _novelty_projection(value, commitments):
    ids = sorted(c['id'] for c in commitments['commitments'])
    positions = {tid: i for i, tid in enumerate(ids)}

    def compact(value):
        if isinstance(value, list):
            return [compact(row) for row in value]
        if not isinstance(value, dict):
            return value
        result = {}
        for key, row in value.items():
            if key == 'commitment_ids' or key.endswith('_commitment_ids'):
                result[key.removesuffix('_ids') + '_indices'] = [positions[tid] for tid in row]
            else:
                result[key] = compact(row)
        return result

    def basis(value):
        # Intermediate greedy-extension checks are an audit trace. Final exact
        # membership and all verdicts remain, with an explicit full-trace link.
        checks = value['checks']
        return compact({**{k: v for k, v in value.items() if k != 'checks'},
            'consistency_trace': dict(count=len(checks), sha256=digest(canonical(checks)),
                scope='full_trace_in_search_context_evidence')})

    result = compact({k: v for k, v in value.items() if k not in ('consistent_basis', 'paper_bases')})
    result['consistent_basis'] = basis(value['consistent_basis'])
    if 'paper_bases' in value:
        result['paper_bases'] = {paper: basis(row) for paper, row in value['paper_bases'].items()}
    result['commitment_id_table'] = ids
    result['id_encoding'] = 'Every *_commitment_indices list indexes commitment_id_table; order and membership are exact.'
    return result


def project_evidence(inputs, referenced):
    evidence = full_evidence(inputs)
    if not evidence:
        return {}, None
    data = {}
    if 'goal_novelty' in evidence:
        data['goal_novelty'] = _novelty_projection(evidence['goal_novelty'], inputs['commitments'])
    if 'alignment_disclosure' in evidence:
        alignment = evidence['alignment_disclosure']
        mapping = alignment.get('mapping', {})
        names = {name for name, _, _ in referenced}
        def relevant(pair):
            return any(pair[key] in names or mapping.get(pair[key], pair[key]) in names
                       for key in ('left', 'right'))
        judgments = alignment.get('judgments', [])
        unresolved = alignment.get('unresolved', [])
        kept_unresolved = [row for row in unresolved if relevant(row)]
        data['alignment_disclosure'] = {**alignment,
            'judgments': [row for row in judgments if relevant(row)],
            'unresolved': kept_unresolved, 'unresolved_count': len(kept_unresolved),
            'full_unresolved_count': len(unresolved), 'full_judgment_count': len(judgments),
            'full_mapping_count': len(mapping),
            'mapping': {a: b for a, b in mapping.items() if a in names or b in names},
            'scope': 'pairs_touching_leaf_or_selected_support_symbols_including_canonical_aliases'}
    receipt = dict(version='search-evidence-v1',
        **{key + '_sha256': digest(canonical(value)) for key, value in evidence.items()},
        policy='Prompt projection only. Full receipts in search_context_evidence; gates use full frozen inputs. '
               'Target closure checks and final basis memberships are retained; consistency traces are linked by hash. '
               'Alignment rows outside the leaf and selected supports are scoped out, not judged unrelated.')
    return data, receipt
