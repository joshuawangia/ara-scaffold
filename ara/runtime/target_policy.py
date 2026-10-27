"""Contribution preflight: structural exclusions, not a semantic originality oracle."""
import re
from collections import Counter
from ara.runtime.search_alignment import symbols
from ara.engine.terminus import is_terminus


def direct_instance(pattern, value):
    """Match removal of leading universal quantifiers with consistent term bindings."""
    pattern, value = pattern.normalized(), value.normalized()
    variables = set()
    def matches(body):
        bindings = {}
        def match(p, v, bound=frozenset()):
            if (p.op, p.name, p.variable, len(p.args), len(p.terms)) != (v.op, v.name, v.variable, len(v.args), len(v.terms)):
                return False
            for a, b in zip(p.terms, v.terms):
                if a.kind == 'variable' and a.name in variables and a.name not in bound:
                    if b.kind == 'variable' and b.name in bound:
                        return False
                    if a.name in bindings and bindings[a.name] != b:
                        return False
                    bindings[a.name] = b
                elif a != b:
                    return False
            nested = bound | {p.variable} if p.op in ('forall','exists') else bound
            return all(match(a,b,nested) for a,b in zip(p.args,v.args))
        return match(body,value)
    while pattern.op == 'forall':
        variables.add(pattern.variable)
        pattern = pattern.args[0]
        if matches(pattern):
            return True
    return False


def target_context(commitments):
    signatures = Counter(s for c in commitments.commitments for s in set(symbols(c.formula)))
    def conditional(formula):
        while formula.op in ('forall','exists'):
            formula = formula.args[0]
        return formula.op == 'implies'
    return dict(target_policy=dict(stance='own_thesis', minimum_support_commitments=2,
                    preferred_support_papers=2, exclude_single_commitment_instances=True),
                conditionals=[c.to_dict() for c in commitments.commitments if conditional(c.formula)],
                shared_symbols=[dict(name=n,kind=k,arity=a,commitments=count)
                                for (n,k,a),count in sorted(signatures.items()) if count>=2])


def trivial_targets(targets, commitments):
    rejected = []
    for target in targets:
        reason, t_id = None, None
        for commitment in commitments.commitments:
            if is_terminus(target, commitment.id, commitments):
                reason, t_id = 'depth_zero_terminus', commitment.id
                break
            if direct_instance(commitment.formula, target.formula):
                reason, t_id = 'single_commitment_instance', commitment.id
                break
        # This catches explicit reporting language; broader semantic attribution
        # and whether multiple sources really support a thesis remain model judgments.
        if re.search(r'\b(argues?|claims?|holds?|maintains?|contends?|reports?|asserts?|suggests?|proposes?)\s+(that\s+)?|\baccording to\b', target.text, re.I):
            reason = 'attributed_report'
        if reason:
            rejected.append(dict(target_id=target.id,reason=reason,commitment_id=t_id))
    return rejected
