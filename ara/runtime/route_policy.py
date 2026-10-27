"""Contribution display/selection policy; historical CLOSED and licenses are unchanged."""
from ara.runtime.contribution import contribution_check, formula_hash
from ara.runtime.target_policy import attributed_report
from ara.types import Commitment, CommitmentSet


def route_contribution(route, commitments=None):
    if route.status != 'CLOSED':
        return dict(classification=route.status, reason='not_closed')
    nodes = {n.id:n for n in route.nodes}
    pending, seen, supports = [route.root_id], set(), {}
    inferred = False
    while pending:
        id = pending.pop()
        if id in seen:
            continue
        seen.add(id)
        node = nodes[id]
        inferred |= node.kind == 'inference' and node.proposal is not None
        ids = ([node.t_id] if node.kind == 'leaf' else [])
        ids += [tid for answer in node.cq_answers for tid in answer.supporting_t_ids]
        for tid in ids:
            commitment = commitments.get(tid) if commitments is not None else None
            if commitments is None and node.kind == 'leaf' and tid == node.t_id and tid != 'open':
                commitment = Commitment(tid, node.proposition.text, 'graph', node.proposition.formula)
            if commitment is None:
                return dict(classification='CLOSED-contribution-unresolved', reason='missing_support')
            supports.setdefault(formula_hash(commitment.formula), commitment)
        pending.extend(node.children)
    support_ids = sorted(c.id for c in supports.values())
    if len(supports) < 2 or not inferred:
        return dict(classification='CLOSED-single-support', reason='fewer_than_two_distinct_supports',
                    support_ids=support_ids)
    root = nodes[route.root_id].proposition
    receipt = contribution_check(root.formula, CommitmentSet(tuple(supports.values())), both_polarities=False)
    classification = {'trivial':'CLOSED-single-support', 'unresolved':'CLOSED-contribution-unresolved',
                      'candidate':'CLOSED-derived'}[receipt['status']]
    if attributed_report(root.text):
        classification = 'CLOSED-attributed-report'
    return dict(classification=classification, support_ids=support_ids, **receipt)


def route_classification(route, commitments=None):
    return route_contribution(route, commitments)['classification']


def selectable_routes(routes, commitments=None):
    return tuple(r for r in routes if route_classification(r, commitments) == 'CLOSED-derived')


def frozen_from_events(events):
    """Frozen inputs from the verified log; absent historical inputs stay absent."""
    import json
    freezes = [json.loads(e['payload_json'])['commitments'] for e in events
               if e['stage'] == 'commitments_frozen']
    return CommitmentSet.from_dict(freezes[-1]) if freezes else None
