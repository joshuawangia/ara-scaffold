"""Bound target definitions and conservative lexical reuse checks; no model effects."""
from difflib import SequenceMatcher
import re
import unicodedata
from ara.runtime.novelty import atomic_applications


def normalized_text(text):
    return ' '.join(re.findall(r'\w+', unicodedata.normalize('NFKC', text).casefold()))


def near_duplicate(left, right):
    a, b = normalized_text(left), normalized_text(right)
    return bool(a and b) and (a == b or (min(len(a),len(b)) >= 20 and
        SequenceMatcher(None,a,b,autojunk=False).ratio() >= .90))


def content_bindings(target, vocabulary, commitments):
    frozen = {(a.name,a.op,len(a.terms)) for c in commitments.commitments for _,a in atomic_applications(c.formula)}
    catalogue = vocabulary['symbol_catalogue'] if vocabulary['definition_semantics'] == 'content' else None
    definitions = {(s['name'],s['kind'],s['arity']):s['definition'] for s in catalogue or []}
    used = {(a.name,a.op,len(a.terms)) for _,a in atomic_applications(target.formula)}
    proposed, issues = {}, []
    for symbol in target.new_symbols:
        key = (symbol.name,symbol.kind,symbol.arity)
        if any(key[0] == k[0] for k in frozen | definitions.keys() | proposed.keys()) or key not in used:
            issues.append(dict(reason='invalid_definition_binding', symbol=symbol.name))
        proposed[key] = symbol.definition
    # For one atomic assertion its complete asserted text is its content binding.
    # Compound targets must explicitly define each otherwise unbound fresh symbol.
    if target.formula.op in ('atom','predicate'):
        key = (target.formula.name,target.formula.op,len(target.formula.terms))
        if key not in frozen and key not in definitions and key not in proposed:
            proposed[key] = target.text
    for key in used - frozen - definitions.keys() - proposed.keys():
        issues.append(dict(reason='missing_definition_binding', symbol=key[0]))
    content = [dict(id=c.id,text=c.text,formula=c.formula.to_dict()) for c in commitments.commitments]
    comparisons = [(c.id,c.text) for c in commitments.commitments]
    comparisons += [('catalogue:'+s['name'],s['definition']) for s in catalogue or []]
    for key,definition in proposed.items():
        matches = [id for id,text in comparisons if near_duplicate(definition,text)]
        if matches:
            issues.append(dict(reason='definition_restates_frozen_content',symbol=key[0],matches=matches))
    definitions.update(proposed)
    bindings = [dict(name=n,kind=k,arity=a,definition=d) for (n,k,a),d in sorted(definitions.items())]
    return dict(definitions=bindings, proposed_definitions=[dict(name=n,kind=k,arity=a,definition=d)
                for (n,k,a),d in sorted(proposed.items())], frozen_content=content, issues=issues)
