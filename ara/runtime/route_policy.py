"""Contribution display/selection policy; historical CLOSED and licenses are unchanged."""
from ara.runtime.contribution import contribution_check, formula_hash, cached_entails
from ara.runtime.target_policy import leading_report_frame
from ara.runtime.novelty import novelty_check
from ara.types import Commitment, CommitmentSet
from functools import lru_cache


@lru_cache(maxsize=1)
def substantive_scheme_ids():
    from pathlib import Path
    from ara.bank import load_bank
    bank = load_bank(Path(__file__).resolve().parents[2] / 'bank')
    return frozenset(b.id for b in bank.entries if b.kind == 'defeasible')


def _logical_contribution(route, commitments=None):
    if route.status != 'CLOSED':
        return dict(classification=route.status, reason='not_closed')
    nodes = {n.id:n for n in route.nodes}
    pending, seen, supports = [route.root_id], set(), {}
    inferred = False
    substantive = []
    substantive_ids = substantive_scheme_ids()
    while pending:
        id = pending.pop()
        if id in seen:
            continue
        seen.add(id)
        node = nodes[id]
        inferred |= node.kind == 'inference' and node.proposal is not None
        if node.kind == 'inference' and node.proposal is not None and node.proposal.bank_id in substantive_ids:
            substantive.append(dict(node_id=node.id, bank_id=node.proposal.bank_id))
        ids = ([node.t_id] if node.kind == 'leaf' else [])
        ids += [tid for answer in node.cq_answers for tid in answer.supporting_t_ids]
        for tid in ids:
            commitment = commitments.get(tid) if commitments is not None else None
            if commitments is None and node.kind == 'leaf' and tid == node.t_id and tid != 'open':
                commitment = Commitment(tid, node.proposition.text, 'graph', node.proposition.formula)
            if commitment is None:
                return dict(classification='CLOSED-contribution-unresolved', reason='missing_support')
            supports.setdefault(formula_hash(commitment.formula), {})[commitment.id] = commitment
        pending.extend(node.children)
    formula_supports = [dict(formula_hash=key, support_ids=sorted(group))
                        for key, group in sorted(supports.items())]
    support_ids = sorted(tid for group in formula_supports for tid in group['support_ids'])
    # One deterministic representative per formula for logic; retain every source above.
    supports = {key: group[min(group)] for key, group in sorted(supports.items())}
    if len(supports) < 2 or not inferred:
        return dict(classification='CLOSED-single-support', reason='fewer_than_two_distinct_supports',
                    support_ids=support_ids, formula_supports=formula_supports)
    root = nodes[route.root_id].proposition
    receipt = contribution_check(root.formula, CommitmentSet(tuple(supports.values())), both_polarities=False)
    classification = {'trivial':'CLOSED-single-support', 'unresolved':'CLOSED-contribution-unresolved',
                      'candidate':'CLOSED-derived'}[receipt['status']]
    basis = commitments or CommitmentSet(tuple(supports.values()))
    novelty = novelty_check(root.formula, basis)
    essential = set(novelty.get('essential_application_keys', ()))
    qualified, step_checks = [], []
    for inference in substantive:
        node = nodes[inference['node_id']]
        # A non-logical scheme must itself conclude the essential new assertion.
        # Deductive wrappers never supply the qualifying step.
        conclusion = novelty_check(node.proposition.formula, basis)
        step_checks.append(dict(**inference, novelty=conclusion))
        if essential.intersection(conclusion.get('essential_application_keys', ())):
            qualified.append(inference)
    substantive = qualified
    if classification == 'CLOSED-derived':
        if novelty['status'] == 'unresolved':
            classification = 'CLOSED-contribution-unresolved'
        elif not substantive:
            classification = ('CLOSED-contribution-unresolved'
                if any(s.get('novelty', {}).get('status') == 'unresolved' for s in step_checks)
                else 'CLOSED-structural')
    if leading_report_frame(root.text):
        classification = 'CLOSED-attributed-report'
    return dict(classification=classification, support_ids=support_ids, formula_supports=formula_supports,
                substantive_inferences=substantive, novelty=novelty, inference_novelty_checks=step_checks, **receipt)


def stance_crossings(route, provenance):
    if provenance is None:
        return []
    nodes = {n.id:n for n in route.nodes}
    pending, seen, crossings = [route.root_id], set(), set()
    while pending:
        id = pending.pop()
        if id in seen:
            continue
        seen.add(id)
        node = nodes[id]
        roles = [(node.t_id, 'global_premise')] if node.kind == 'leaf' and node.t_id != 'open' else []
        roles += [(tid, 'cq_evidence') for a in node.cq_answers for tid in a.supporting_t_ids]
        for tid,role in roles:
            stance = provenance['commitments'].get(tid, {}).get('stance', 'unavailable')
            if stance != 'endorsed' and not (stance in ('model_alignment','proposed') and role == 'global_premise'):
                crossings.add((tid,stance,role))
        pending.extend(node.children)
    return [dict(commitment_id=tid,stance=stance,role=role) for tid,stance,role in sorted(crossings)]


def route_contribution(route, commitments=None, provenance=None):
    receipt = _logical_contribution(route, commitments)
    from ara.runtime.novelty_basis import support_consistency
    consistency = (support_consistency(commitments, receipt.get('support_ids', ()))
        if route.status == 'CLOSED' and commitments is not None else None)
    if consistency is not None and 'support_ids' not in receipt:
        consistency = dict(status='unresolved', reason='missing_support_inventory', solver_result='NOT_CHECKED')
    receipt['support_consistency'] = consistency
    from ara.runtime.bridges import paper_support
    papers = paper_support(receipt.get('formula_supports', []), provenance)
    if route.status == 'CLOSED' and commitments is not None and provenance is not None:
        root = next(n for n in route.nodes if n.id == route.root_id)
        novelty = novelty_check(root.proposition.formula, commitments, provenance,
                                support_ids=receipt.get('support_ids', ()))
        receipt['per_paper_novelty'] = novelty
        supports = tuple(commitments.get(tid).formula for tid in receipt.get('support_ids', ()))
        union = cached_entails(supports, root.proposition.formula, 1000)
        receipt['support_union_entailment'] = union
        # CLOSED routes are engine-licensed. Deduction can supply the qualifying
        # inference when the contribution lies in combining distinct papers.
        from ara.runtime.synthesis import route_inference_licenses
        license_receipt = (route_inference_licenses(route)
            if novelty['status'] == 'candidate' and papers['cross_paper_supported']
            else dict(licensed=False,checks=[]))
        receipt['synthesis_inference_licenses'] = license_receipt
        if (novelty['status'] == 'candidate'
                and papers['cross_paper_supported'] and license_receipt['licensed']
                and receipt['classification'] in ('CLOSED-structural','CLOSED-contribution-unresolved')):
            receipt.update(classification='CLOSED-derived', contribution_kind=(
                'cross_paper_deduction' if union == 'SOLVER_UNSAT' else 'cross_paper_inference'))
        if novelty['reason'] == 'single_paper_closure':
            receipt.update(classification='CLOSED-single-paper', reason='single_paper_closure')
        elif novelty['status'] == 'unresolved' and receipt['classification'] == 'CLOSED-derived':
            receipt.update(classification='CLOSED-contribution-unresolved', reason='novelty_unresolved')
        elif novelty['status'] == 'rejected' and receipt['classification'] == 'CLOSED-derived':
            receipt.update(classification='CLOSED-structural', reason=novelty['reason'])
    if receipt['classification'] == 'CLOSED-derived':
        if papers['status'] != 'verified':
            receipt.update(classification='CLOSED-contribution-unresolved', reason='paper_identity_unavailable')
        elif not papers['cross_paper_supported']:
            receipt.update(classification='CLOSED-single-paper', reason='fewer_than_two_papers')
    gap = next(n.proposition.gap for n in route.nodes if n.id == route.root_id)
    if gap is not None:
        from ara.runtime.gaps import resolution_support
        resolution = resolution_support(gap, receipt.get('support_ids', []), provenance)
        receipt['gap_resolution'] = resolution
        if receipt['classification'] == 'CLOSED-derived' and not resolution['supported']:
            receipt.update(classification='CLOSED-gap-unresolved', reason='gap_side_support_missing')
    rows = provenance['commitments'] if provenance else {}
    alignment_ids = [tid for tid in receipt.get('support_ids', []) if rows.get(tid, {}).get('stance') == 'model_alignment']
    endorsed_ids = [tid for tid in receipt.get('support_ids', []) if rows.get(tid, {}).get('stance') == 'endorsed']
    if alignment_ids and len(endorsed_ids) < 2 and route.status == 'CLOSED':
        receipt.update(classification='CLOSED-single-support', reason='fewer_than_two_endorsed_source_supports')
    crossings = stance_crossings(route, provenance)
    if crossings:
        receipt.update(classification='CLOSED-stance-crossing' if route.status == 'CLOSED' else route.status,
                       reason='restricted_source_used_as_global_support')
    if consistency is not None and consistency['status'] != 'consistent':
        receipt.update(classification='CLOSED-conflict' if consistency['status'] == 'conflict' else 'CLOSED-contribution-unresolved',
                       reason='inconsistent_supports' if consistency['status'] == 'conflict' else 'support_consistency_unresolved')
    scoped = [dict(node_id=n.id, commitment_id=c.id, stance=provenance['commitments'][c.id]['stance'],
                   role='scoped_hypothesis')
              for n in route.nodes if n.kind == 'assumption'
              for c in (commitments.commitments if commitments is not None and provenance else ())
              if formula_hash(n.proposition.formula) == formula_hash(c.formula)]
    from ara.runtime.symbol_alignment import alignment_disclosure
    from ara.runtime.hypotheses import route_hypothesis_disclosure
    hypotheses = route_hypothesis_disclosure(route, provenance)
    if hypotheses['conditional_on']:
        receipt.update(hypothesis_disclosure=hypotheses, conditional_on=hypotheses['conditional_on'],
                       conclusion_status=hypotheses['conclusion_status'])
    return dict(**receipt, alignment_support_ids=alignment_ids, endorsed_support_ids=endorsed_ids,
                alignment_disclosure=alignment_disclosure(provenance), paper_support=papers, scoped_source_roles=scoped, provenance_status='verified' if provenance else 'unavailable_legacy',
                provenance_sha256=provenance['sha256'] if provenance else None,
                stance_crossings=crossings)


def route_classification(route, commitments=None, provenance=None):
    return route_contribution(route, commitments, provenance)['classification']


def route_display_status(route, commitments=None, provenance=None):
    receipt = route_contribution(route, commitments, provenance)
    return receipt['classification'] + ('; ' + receipt['conclusion_status'] if receipt.get('conditional_on') else '')


def selectable_routes(routes, commitments=None, provenance=None):
    return tuple(r for r in routes if route_classification(r, commitments, provenance) == 'CLOSED-derived')


def frozen_from_events(events):
    """Frozen inputs from the verified log; absent historical inputs stay absent."""
    import json
    freezes = [json.loads(e['payload_json'])['commitments'] for e in events
               if e['stage'] == 'commitments_frozen']
    return CommitmentSet.from_dict(freezes[-1]) if freezes else None


def provenance_from_events(events, commitments):
    """Validate provenance receipts against the logged freeze, without inventing legacy roles."""
    import json
    from ara.runtime.commitment_provenance import validate_commitment_provenance
    receipts = [json.loads(e['payload_json']) for e in events if e['stage'] == 'commitment_provenance_frozen']
    if not receipts:
        return None
    catalogues = [json.loads(e['payload_json']) for e in events if e['stage'] == 'symbol_catalogue_frozen']
    if len(receipts) != 1 or len(catalogues) != 1 or commitments is None:
        raise ValueError('invalid commitment provenance freeze receipts')
    return validate_commitment_provenance(receipts[0], commitments, catalogues[0])
