"""Explicit proposed premises: one freeze, no source authority, replayable metadata."""
from ara.runtime.commitment_provenance import content_definition
from ara.runtime.frozen_catalogue import make_catalogue
from ara.runtime.novelty_basis import support_consistency
from ara.runtime.search_alignment import symbols as formula_symbols
from ara.types import Commitment, CommitmentSet, Formula

_FIELDS = {'id', 'text', 'rationale', 'proposer', 'linked_gap', 'linked_target'}
_OPTIONAL = {'formula', 'formalization_request', 'new_symbols'}


def declaration(value):
    if not isinstance(value, dict) or not _FIELDS <= value.keys() or value.keys() - (_FIELDS | _OPTIONAL):
        raise ValueError('invalid hypothesis declaration fields')
    if (any(not isinstance(value[k], str) or not value[k].strip() for k in ('id','text','rationale','proposer')) or
            not value['id'].startswith('hypothesis:') or value['proposer'] not in ('ara-target','eps2','operator') or
            not content_definition(value['text']) or
            any(v is not None and (not isinstance(v,str) or not v.strip()) for v in
                (value['linked_gap'],value['linked_target'])) or not (value['linked_gap'] or value['linked_target'])):
        raise ValueError('invalid hypothesis identity, content, proposer or link')
    if (value.get('formula') is None) == (value.get('formalization_request') is None):
        raise ValueError('hypothesis requires exactly one formula or formalization request')
    if value.get('formalization_request') is not None and (
            not isinstance(value['formalization_request'],str) or not value['formalization_request'].strip()):
        raise ValueError('invalid hypothesis formalization request')
    fresh = value.get('new_symbols', [])
    if not isinstance(fresh,list) or any(not isinstance(s,dict) or
            set(s) != {'name','kind','arity','definition'} or not content_definition(s['definition']) for s in fresh):
        raise ValueError('invalid hypothesis symbol definitions')
    return value


def _append(commitments, symbols, rows, entries):
    inventory = {c.id for c in commitments.commitments}
    result, vocabulary, provenance = list(commitments.commitments), list(symbols), dict(rows)
    names = {s['name'] for s in vocabulary}
    for entry in entries:
        value = declaration({k:v for k,v in entry.items() if k != 'resolved_formula'})
        if value['id'] in inventory:
            raise ValueError('duplicate hypothesis id')
        inventory.add(value['id'])
        formula = Formula.from_dict(entry['resolved_formula'])
        if value.get('formula') is not None and Formula.from_dict(value['formula']) != formula:
            raise ValueError('hypothesis formula binding mismatch')
        used = set(formula_symbols(formula))
        for s in value.get('new_symbols', []):
            if s['name'] in names or (s['name'],s['kind'],s['arity']) not in used:
                raise ValueError('hypothesis symbol collision or unused definition')
            vocabulary.append(dict(**s,evidence_ids=[value['id']]))
            names.add(s['name'])
        result.append(Commitment(value['id'],value['text'],'Proposed hypothesis: '+value['id'],formula))
        provenance[value['id']] = dict(kind='hypothesis',stance='proposed',source_id=None,
            declaration=value,formula=formula.to_dict())
    frozen = CommitmentSet(tuple(result))
    make_catalogue(frozen,vocabulary)  # Exact vocabulary/signature/definition coverage.
    return frozen,vocabulary,provenance


def admit_hypotheses(calls, commitments, symbols, rows):
    configured = calls.config.get('hypothesis_premises', [])
    if not isinstance(configured,list):
        raise ValueError('hypothesis_premises must be a list')
    if not configured:
        return commitments,symbols,rows,None
    calls.log.record('hypotheses_requested', hypotheses=configured, authority='proposed_not_source')
    entries=[]
    for raw in configured:
        value=declaration(raw)
        def check(data):
            formula=Formula.from_dict(data['formula'])
            entry=dict(value,resolved_formula=formula.to_dict())
            _append(commitments,symbols,rows,[*entries,entry])
            return entry
        if value.get('formula') is not None:
            from ara.runtime.validation import validate_local
            data=dict(formula=value['formula'])
            validate_local(calls.response_schema('formalise',{}),data,calls.config)
            entry=check(data)
        else:
            entry=calls.call('formalise',dict(proposition=dict(id=value['id'],text=value['text']),
                symbol_catalogue=symbols,new_symbols=value.get('new_symbols',[]),
                formalization_request=value['formalization_request'],
                vocabulary_instruction='Formalize this proposed hypothesis, not a source assertion. Reuse exact supplied symbol definitions/signatures. No undeclared symbols.'),check)
        entries.append(entry)
    frozen,vocabulary,provenance=_append(commitments,symbols,rows,entries)
    consistency=support_consistency(frozen,[c.id for c in frozen.commitments])
    calls.log.record('hypotheses_consistency',**consistency)
    if consistency['status']!='consistent':
        raise ValueError('hypotheses inconsistent with T or consistency unresolved')
    receipt=dict(schema_version='hypothesis-premises-v1',base_commitments=commitments.to_dict(),
        base_symbols=symbols,entries=entries,consistency=consistency)
    calls.log.record('hypotheses_admitted',**receipt,
        note='Proposed premises, not source evidence. Any using route is conditional on H; two source papers remain required.')
    return frozen,vocabulary,provenance,receipt


def validate_hypotheses(receipt,commitments,symbols,rows):
    if (not isinstance(receipt,dict) or set(receipt)!=
            {'schema_version','base_commitments','base_symbols','entries','consistency'} or
            receipt['schema_version']!='hypothesis-premises-v1' or
            not isinstance(receipt['entries'],list) or not receipt['entries']):
        raise ValueError('invalid hypothesis receipt')
    base=CommitmentSet.from_dict(receipt['base_commitments'])
    base_rows={c.id:rows[c.id] for c in base.commitments}
    expected,expected_symbols,expected_rows=_append(base,receipt['base_symbols'],base_rows,receipt['entries'])
    if (expected!=commitments or make_catalogue(expected,expected_symbols)!=make_catalogue(commitments,symbols) or expected_rows!=rows or
            receipt['consistency'].get('status')!='consistent' or
            receipt['consistency'].get('commitment_ids')!=sorted(c.id for c in commitments.commitments) or
            support_consistency(commitments,[c.id for c in commitments.commitments])['status']!='consistent'):
        raise ValueError('hypothesis replay or consistency mismatch')
    return base,receipt['base_symbols'],base_rows


def hypothesis_ids(provenance):
    return sorted(tid for tid,row in (provenance or {}).get('commitments',{}).items()
                  if row.get('kind')=='hypothesis' and row.get('stance')=='proposed')


def hypothesis_disclosure(provenance, support_ids=None):
    ids=hypothesis_ids(provenance)
    if support_ids is not None:
        ids=[tid for tid in ids if tid in support_ids]
    return dict(conditional_on=ids,hypotheses=[dict(id=tid,**provenance['commitments'][tid]) for tid in ids],
        label='conditional on H' if ids else None,
        note='Hypotheses are the paper\'s proposals, never author-endorsed source claims. Derivation is conditional on these premises.' if ids else None)


def route_hypothesis_disclosure(route, provenance):
    """Actual reachable H use, independent of closure or novelty classification."""
    nodes = {node.id: node for node in route.nodes}
    pending, seen, used = [route.root_id], set(), set()
    while pending:
        node_id = pending.pop()
        if node_id in seen:
            continue
        seen.add(node_id)
        node = nodes[node_id]
        if node.kind == 'leaf':
            used.add(node.t_id)
        used.update(tid for answer in node.cq_answers for tid in answer.supporting_t_ids)
        pending.extend(node.children)
    disclosure = hypothesis_disclosure(provenance, used)
    if disclosure['conditional_on']:
        ids = ', '.join(disclosure['conditional_on'])
        closed = route.status == 'CLOSED'
        disclosure.update(conclusion_id=route.root_id,
            conclusion_text=nodes[route.root_id].proposition.text, route_status=route.status,
            conclusion_status='conditional on H' if closed else 'conditional on H; no completed conclusion',
            required_statement=(f"This paper's conclusion is conditional on H ({ids})." if closed else
                f'This unfinished argument is conditional on H ({ids}); no completed conclusion is established.'))
        if not closed:
            disclosure['note'] = 'Proposed premises are used in this unfinished route; no completed conclusion is established.'
    return disclosure


def route_disclosure(events, route):
    from ara.runtime.route_policy import frozen_from_events, provenance_from_events
    frozen = frozen_from_events(events)
    return route_hypothesis_disclosure(route, provenance_from_events(events, frozen))


def validate_conditional_statement(disclosure, body):
    """One runtime-specified affirmative paragraph, never a phrase occurrence."""
    import re
    from html.parser import HTMLParser
    from markdown_it import MarkdownIt
    if not disclosure['conditional_on']:
        return
    statement = disclosure['required_statement']
    markdown = MarkdownIt('commonmark')
    tokens = markdown.parse(body)
    affirmative = any(token.type == 'inline' and token.content == statement and
        i > 0 and tokens[i-1].type == 'paragraph_open' and tokens[i-1].level == 0 and
        all(child.type == 'text' for child in token.children or ())
        for i, token in enumerate(tokens))
    if not affirmative or body.count(statement) != 1:
        raise ValueError('hypothesis disclosure requires one standalone plain paragraph: ' + statement)

    class VisibleText(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts = []
        def handle_data(self, data):
            self.parts.append(data)
        def handle_starttag(self, tag, attrs):
            if tag == 'br':
                self.parts.append(' ')
            if tag == 'img':
                self.parts.append(dict(attrs).get('alt', '') or '')

    # Screening view only: preserve all authored bytes, including markup.
    text = VisibleText()
    text.feed(markdown.render(body.replace(statement, '', 1)))
    text.close()
    if re.search(r'\bconditional\s+on\s+h\b|\bunconditional(?:ly)?\b|'
                 r'\b(?:independent\s+of|(?:not|never)\s+(?:depend|rely)\s+on)\s+'
                 r'(?:h\b|(?:the\s+)?(?:proposed\s+)?hypothes)', ''.join(text.parts), re.I):
        raise ValueError('hypothesis disclosure has contradictory or ambiguous status wording')


def hypothesis_role_failure(role, text, authorized):
    import re
    if role!='proposed_principle':
        return 'hypothesis_requires_proposed_principle'
    if not authorized:
        return 'unauthorized_hypothesis_role'
    text=re.sub(r'\[\[node:[^\]]+\]\]','',text).strip()
    prefix=re.match(r'(?i)^(?:this paper proposes|we propose)\b[\s:]*',text)
    if prefix is None:
        return 'unmarked_hypothesis'
    remainder=text[prefix.end():]
    if re.search(r'\[(?:cite|lit):',text) or not content_definition(remainder):
        return 'source_attributed_hypothesis'
    return None


def validate_disclosure(events, route, draft):
    """A clean audit cannot substitute for explicit proposal/conditional disclosure."""
    import re
    from ara.runtime.essay_audit import sentence_spans
    disclosure=route_disclosure(events,route)
    if not disclosure['conditional_on']:
        return
    validate_conditional_statement(disclosure, draft['body'])
    for tid in disclosure['conditional_on']:
        nodes={n.id for n in route.nodes if n.kind=='leaf' and n.t_id==tid}
        marked=[draft['body'][a:b] for a,b in sentence_spans(draft['body'])
                if nodes & set(re.findall(r'\[\[node:([^\]]+)\]\]',draft['body'][a:b]))]
        if not marked or not any(hypothesis_role_failure('proposed_principle',text,True) is None for text in marked):
            raise ValueError('hypothesis disclosure missing paper-owned proposal: '+tid)


def validate_hypothesis_config(config):
    values=config.get('hypothesis_premises',[])
    if not isinstance(values,list):
        raise ValueError('hypothesis_premises must be a list')
    ids=[declaration(value)['id'] for value in values]
    if len(ids)!=len(set(ids)):
        raise ValueError('duplicate hypothesis id')
