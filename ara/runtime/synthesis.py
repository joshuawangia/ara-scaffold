"""Bounded native forward candidates with source dependencies and per-paper novelty."""
import json
from ara.engine.forward import forward_pass, ForwardResult
from ara.engine.licensing import Licenser
from ara.runtime.bridges import paper_support
from ara.runtime.cache import canonical, digest
from ara.runtime.contribution import formula_hash
from ara.runtime.novelty import novelty_check, atomic_applications
from ara.types import CommitmentSet


def _rank_result(commitments, eligible, provenance, result, origin):
    dependencies, licenses = {}, {}
    for c in eligible.commitments:
        dependencies.setdefault(c.formula.canonical(), set()).add(c.id)
    direct_atoms = {key for c in eligible.commitments
                    if c.formula.op in ('atom','predicate') or (c.formula.op == 'not' and c.formula.args[0].op in ('atom','predicate'))
                    for key,_ in atomic_applications(c.formula)}
    candidates = []
    for consequence in result.consequences:
        key = consequence.formula.canonical()
        premise_keys = [p.canonical() for p in consequence.premises]
        if any(p not in dependencies for p in premise_keys):
            continue
        ids = set().union(*(dependencies.get(p,set()) for p in premise_keys))
        dependencies[key] = ids
        bank_ids = {consequence.bank_id}.union(*(licenses.get(p,set()) for p in premise_keys))
        licenses[key] = bank_ids
        if consequence.flagged or not ids:
            continue
        groups = {}
        for tid in sorted(ids):
            groups.setdefault(formula_hash(commitments.get(tid).formula), []).append(tid)
        papers = paper_support([dict(formula_hash=h,support_ids=tids) for h,tids in groups.items()],provenance)
        if not papers['cross_paper_supported']:
            continue
        if all(key in direct_atoms for key,_ in atomic_applications(consequence.formula)):
            continue
        novelty = novelty_check(consequence.formula, commitments, provenance)
        if novelty['status'] != 'candidate':
            continue
        candidates.append(dict(formula=consequence.formula.to_dict(),support_ids=sorted(ids),
            paper_ids=papers['paper_ids'],bank_ids=sorted(bank_ids),depth=consequence.depth,
            alignment_support_ids=sorted(tid for tid in ids if provenance['commitments'][tid]['stance']=='model_alignment'),
            endorsed_support_ids=sorted(tid for tid in ids if provenance['commitments'][tid]['stance']=='endorsed'),
            candidate_id='forward:'+digest(key),origin=origin))
    return candidates


def forward_candidates(commitments, provenance, bank, sink, *, depth=2, node_cap=500, observed=()):
    if provenance is None:
        return dict(status='unavailable_legacy', candidates=[], licensed_consequences=0, truncated=False)
    rows = provenance['commitments']
    eligible = CommitmentSet(tuple(c for c in commitments.commitments if rows[c.id]['stance'] in ('endorsed','model_alignment')))
    # The forward engine uses its canonical AST adapter; no model port is invoked.
    result = forward_pass(tuple(c.formula for c in eligible.commitments), eligible,
                          Licenser(bank, None, sink), depth, node_cap)
    candidates = _rank_result(commitments,eligible,provenance,result,'fresh_forward')
    remaining = node_cap
    for prior in observed:
        selected = ForwardResult(prior.consequences[:remaining],prior.truncated,prior.route_id)
        candidates.extend(_rank_result(commitments,eligible,provenance,selected,'recorded_forward'))
        remaining -= len(selected.consequences)
        if not remaining:
            break
    candidates.sort(key=lambda c:(c['depth'],len(c['support_ids']),c['candidate_id'],c['origin']))
    unique = {}
    for candidate in candidates:
        unique.setdefault(candidate['candidate_id'],candidate)
    available = sum(len(prior.consequences) for prior in observed)
    return dict(status='bounded_native_forward',candidates=list(unique.values()),
                licensed_consequences=len(result.consequences),truncated=result.truncated,
                observed_consequences=available,observed_scanned=node_cap-remaining,
                observed_truncated=available>node_cap or any(p.truncated for p in observed),
                depth=depth,node_cap=node_cap)


def recorded_forward(events, commitments):
    freezes = [(i,json.loads(e['payload_json'])) for i,e in enumerate(events) if e['stage']=='commitments_frozen']
    if not freezes or freezes[-1][1]['commitments']!=commitments.to_dict():
        return ()
    boundary = max([freezes[-1][0]]+[i for i,e in enumerate(events)
        if e['stage'] in ('analysis_started','search_publication_started')])
    findings = [json.loads(e['payload_json']) for i,e in enumerate(events)
                if i > boundary and e['stage']=='conflicts_and_robustness']
    if not findings:
        return ()
    return tuple(ForwardResult.from_dict(f) for a in findings[-1]['findings']['analyses'] for f in a['forward'])


def proposal_forward_candidates(calls, commitments, vocabulary):
    from ara.bank import load_bank
    bank = load_bank(calls.root/'bank')
    depth = calls.config['forward_pass_depth']
    cap = calls.config.get('forward_candidate_node_cap',calls.config['node_cap'])
    observed = recorded_forward(calls.log.read(),commitments)
    key = digest(canonical([vocabulary['commitments_sha256'],vocabulary['provenance_sha256'],
                            bank.to_dict(),depth,cap,[p.to_dict() for p in observed]]))
    cache = getattr(calls,'_forward_candidates',{})
    if key not in cache:
        cache[key] = forward_candidates(commitments,vocabulary['commitment_provenance'],bank,calls.log,
                                        depth=depth,node_cap=cap,observed=observed)
        calls._forward_candidates = cache
    result = cache[key]
    calls.log.record('forward_target_candidates',**result,commitments_sha256=vocabulary['commitments_sha256'],
                     provenance_sha256=vocabulary['provenance_sha256'],proposed_limit=30,
                     note='Licensed forward candidates, not accepted theses or searched routes; bounded, not exhaustive.')
    return result['candidates'][:30]


class _CanonicalFormula:
    def formalise(self, proposition):
        from ara.types import Formula
        return Formula.from_json(proposition.text)


class _LicenseReceipt:
    def emit(self, event):
        # These read-only rechecks return receipts below; native search logs
        # remain the authority for original licensing events.
        pass


def route_inference_licenses(route):
    """Recheck reachable inferences through the native bank licenser, without models."""
    from dataclasses import replace
    from pathlib import Path
    from ara.bank import load_bank
    nodes = {n.id:n for n in route.nodes}
    checker = Licenser(load_bank(Path(__file__).resolve().parents[2]/'bank'),_CanonicalFormula(),_LicenseReceipt())
    pending, seen, checks = [route.root_id], set(), []
    while pending:
        id = pending.pop()
        if id in seen:
            continue
        seen.add(id)
        node = nodes[id]
        pending.extend(node.children)
        if node.kind != 'inference':
            continue
        entry = checker.bank.get(node.proposal.bank_id) if node.proposal else None
        fills = {p.slot:p for p in node.proposal.premises} if node.proposal else {}
        if entry is None or len(node.children)!=len(entry.premise_slots) or set(fills)!={s.id for s in entry.premise_slots}:
            checks.append(dict(node_id=id,licensed=False,reason='INVALID_INFERENCE_BINDING'))
            continue
        proposal = replace(node.proposal, conclusion_ref=None, conclusion_text=node.proposition.formula.canonical(),
            premises=tuple(replace(fills[slot.id],text=nodes[child].proposition.formula.canonical())
                           for slot,child in zip(entry.premise_slots,node.children,strict=True)))
        verdict = checker.check(proposal,node.proposition)
        checks.append(dict(node_id=id,bank_id=entry.id,licensed=verdict.licensed,reason=verdict.decision.reason_code))
    return dict(licensed=bool(checks) and all(c['licensed'] for c in checks),checks=checks)
