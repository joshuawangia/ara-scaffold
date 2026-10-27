"""Solver contribution gates and conservative attribution screening."""
import re
from collections import Counter
from ara.runtime.search_alignment import symbols


_ATTRIBUTION = re.compile(
    r"\b(argues?|claims?|holds?|maintains?|contends?|reports?|asserts?|suggests?|proposes?|"
    r"believes?|defends?|endorses?|says?|states?|thinks?|accounts?)\b|"
    r"\baccording\s+to\b|\bon\s+.+?[’']s\s+account\b|"
    r"[’']s\s+(view|position|thesis|claim|belief|account)\b", re.I)


def attributed_report(text):
    return bool(_ATTRIBUTION.search(text))


def top_level_attribution(formula, catalogue):
    while formula.op in ('forall', 'exists', 'not'):
        formula = formula.args[0]
    if formula.op not in ('atom', 'predicate'):
        return False
    return any(s['name'] == formula.name and s['kind'] == formula.op and
               s['arity'] == len(formula.terms) and
               (attributed_report(s['definition']) or attributed_report(s['name']) or
                re.search(r'\b(attribution|attitude|reported|attributed)\b', s['definition'], re.I))
               for s in catalogue or [])


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


def trivial_targets(targets, commitments, catalogue=None, receipts=None):
    from ara.runtime.contribution import contribution_check
    rejected = []
    for target in targets:
        receipt = contribution_check(target.formula, commitments)
        if receipts is not None:
            receipts.append(dict(target_id=target.id, **receipt))
        reason = receipt['reason'] if receipt['status'] != 'candidate' else None
        if attributed_report(target.text) or top_level_attribution(target.formula, catalogue):
            reason = 'attributed_report'
        if reason:
            rejected.append(dict(target_id=target.id, reason=reason,
                                 commitment_id=receipt.get('commitment_id')))
    return rejected


def classifier_inputs(target, vocabulary):
    """Render asserted logical structure; source attribution is not assertion content."""
    catalogue = vocabulary['symbol_catalogue'] if vocabulary['definition_semantics'] == 'content' else None
    definitions = {(s['name'],s['kind'],s['arity']):s['definition'] for s in catalogue or []}
    def render(formula):
        if formula.op in ('atom','predicate'):
            return dict(op=formula.op, name=formula.name,
                        definition=definitions.get((formula.name,formula.op,len(formula.terms))),
                        terms=[dict(**t.to_dict(), definition=definitions.get((t.name,'constant',0)))
                               if t.kind == 'constant' else t.to_dict() for t in formula.terms])
        result = dict(op=formula.op, args=[render(a) for a in formula.args])
        if formula.variable is not None:
            result['variable'] = formula.variable
        return result
    return dict(target=target.to_dict(), rendered_content=render(target.formula),
                definition_semantics=vocabulary['definition_semantics'],
                commitments_sha256=vocabulary['commitments_sha256'],
                catalogue_sha256=vocabulary['catalogue_sha256'],
                provenance_sha256=vocabulary['provenance_sha256'])
