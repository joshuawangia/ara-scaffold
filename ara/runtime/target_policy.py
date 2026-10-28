"""Solver contribution gates, advisory lexical evidence and exact report frames."""
import re
from collections import Counter
from ara.runtime.search_alignment import symbols


_ATTRIBUTION = re.compile(
    r"\b(argues?|claims?|holds?|maintains?|contends?|reports?|asserts?|suggests?|proposes?|"
    r"believes?|defends?|endorses?|says?|states?|thinks?|accounts?)\b|"
    r"\baccording\s+to\b|\bon\s+.+?[’']s\s+account\b|"
    r"[’']s\s+(view|position|thesis|claim|belief|account)\b", re.I)

_CATALOGUE_HINTS = re.compile(_ATTRIBUTION.pattern + r'|\b(attribution|attitude|reported|attributed)\b', re.I)


def attributed_report(text):
    return bool(_ATTRIBUTION.search(text))


def leading_report_frame(text):
    return bool(re.match(r"^\s*[A-Z][\w’'-]*(?:\s+[A-Z][\w’'-]*){0,3}\s+"
                         r"(?i:argues|holds|believes)\s+(?i:that)\b", text))


def attribution_hits(target, catalogue=None):
    sources = [('target_text', target.text)]
    sources += [('proposed_definition:' + s.name, s.definition) for s in target.new_symbols]
    used = set(symbols(target.formula))
    sources += [('catalogue', text) for s in catalogue or []
                if (s['name'], s['kind'], s['arity']) in used for text in (s['name'], s['definition'])]
    hits = []
    for source, text in sources:
        pattern = _CATALOGUE_HINTS if source == 'catalogue' else _ATTRIBUTION
        hits.extend(dict(source=source, text=text, match=m.group(), start=m.start(), end=m.end())
                    for m in pattern.finditer(text))
    return hits


def target_context(commitments, bank):
    signatures = Counter(s for c in commitments.commitments for s in set(symbols(c.formula)))
    def conditional(formula):
        while formula.op in ('forall','exists'):
            formula = formula.args[0]
        return formula.op == 'implies'
    return dict(bank_version=bank.bank_version, bank=[b.to_dict() for b in bank.entries],
                substantive_bank_ids=[b.id for b in bank.entries if b.kind == 'defeasible'],
                structural_bank_ids=sorted(b.id for b in bank.entries if b.kind == 'deductive'),
                support_examples=[dict(rejected_target='P and Q', commitments=['P','Q'],
                    reason='A bare conjunction only repackages T and its conjunction-introduction route is structural.'),
                    dict(rejected_target='Q', commitments=['P', 'P -> Q'],
                    reason='Modus ponens is licensed, but Q is already in the classical closure of T.'),
                    dict(bank_id='sign', commitments=['P', 'Q'], target='R',
                    slots=dict(sign_relation='P', observed_sign='Q'),
                    condition='The source content must fit the sign scheme. Answer every supplied CQ with frozen evidence; P and Q need not classically entail R.'),
                    dict(rejected_target='(P and Q) -> R', commitment='R',
                    reason='R alone entails this conditional. State a new main proposition instead of adding antecedents.')],
                target_policy=dict(stance='own_thesis', minimum_support_commitments=2,
                    minimum_support_papers=2, exclude_single_commitment_instances=True,
                    exclude_conditional_with_frozen_consequent=True, allow_defeasible_support=True,
                    require_new_main_proposition=True, exclude_boolean_recombination=True),
                conditionals=[c.to_dict() for c in commitments.commitments if conditional(c.formula)],
                shared_symbols=[dict(name=n,kind=k,arity=a,commitments=count)
                                for (n,k,a),count in sorted(signatures.items()) if count>=2])


def trivial_targets(targets, commitments, catalogue=None, receipts=None):
    from ara.runtime.contribution import contribution_check
    from ara.runtime.novelty import novelty_check
    rejected = []
    for target in targets:
        receipt = contribution_check(target.formula, commitments)
        novelty = novelty_check(target.formula, commitments)
        if receipts is not None:
            receipts.append(dict(target_id=target.id, novelty=novelty, **receipt))
        reason = receipt['reason'] if receipt['status'] != 'candidate' else None
        if reason is None and novelty['status'] != 'candidate':
            reason = novelty['reason']
        if leading_report_frame(target.text):
            reason = 'attributed_report'
        if reason:
            witness = commitments.get(receipt.get('commitment_id'))
            consequent_in_t = (target.formula.op == 'implies' and
                commitments.contains_formula(target.formula.args[1]))
            explanation = (f"Commitment {witness.id} alone entails the {receipt['polarity']}: {witness.text}."
                           if witness is not None else reason)
            if consequent_in_t:
                explanation += ' The conditional consequent is already in T; adding antecedents does not create a new claim.'
            rejected.append(dict(target_id=target.id, target=target.to_dict(), reason=reason,
                                 commitment_id=receipt.get('commitment_id'), polarity=receipt.get('polarity'),
                                 entailing_commitment=witness.to_dict() if witness else None,
                                 conditional_consequent_in_t=consequent_in_t, novelty=novelty,
                                 explanation=novelty['explanation'] if reason in ('deductive_closure','novelty_unresolved','no_essential_new_proposition') else explanation))
    return rejected


def classifier_inputs(target, vocabulary, commitments):
    """Render asserted logical structure; source attribution is not assertion content."""
    from ara.runtime.target_content import content_bindings
    content = content_bindings(target, vocabulary, commitments)
    definitions = {(s['name'],s['kind'],s['arity']):s['definition'] for s in content['definitions']}
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
                frozen_content=content['frozen_content'], proposed_definitions=content['proposed_definitions'],
                definition_issues=content['issues'],
                lexical_attribution_hits=attribution_hits(target, vocabulary['symbol_catalogue']),
                definition_semantics=vocabulary['definition_semantics'],
                commitments_sha256=vocabulary['commitments_sha256'],
                catalogue_sha256=vocabulary['catalogue_sha256'],
                provenance_sha256=vocabulary['provenance_sha256'])
