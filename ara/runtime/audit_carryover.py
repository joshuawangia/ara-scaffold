"""Carry verified sentence verdicts across ownership edits and audited rewording."""
import json
import re
from difflib import SequenceMatcher
from collections import Counter

from jsonschema import ValidationError

from ara.runtime.cache import canonical, digest

PREFIX = re.compile(r'^(?:This paper (?:argues|proposes|suggests|holds|contends|maintains|claims)|We (?:argue|propose|suggest|hold|contend|maintain|claim))\s+(?:that\s+)?', re.I)
CITATIONS = re.compile(r'\[(?:cite|lit):[^\]]+\]')


def normalized_sentence(text):
    """No word deletion except a leading ownership cue; preserve logical symbols."""
    text = ' '.join(text.split()).translate(str.maketrans({'“':'"','”':'"','’':"'",'‘':"'"}))
    text = PREFIX.sub('', text, count=1)
    # Serial-comma and punctuation-spacing changes do not change word inventory.
    text = re.sub(r',\s+(and|or)\b', r' \1', text)
    text = re.sub(r'\s+([,.;:!?])', r'\1', text)
    text = re.sub(r'([,;:])\s*', r'\1 ', text)
    return text.strip()


def _payload(event):
    return json.loads(event['payload_json'])


def verified_source_rows(calls, route, draft, inputs, *, events=None):
    """Recover source roles from the current final draft's complete clean k>=3 gate."""
    from ara.runtime.essay_audit import NODE, sentence_spans
    from ara.runtime.providers import Response
    from ara.runtime.validation import decode_response, validate_local
    events = calls.log.read() if events is None else events
    start = max((i for i,e in enumerate(events) if e['stage']=='essay_composition_started'), default=0)
    finals = [(i,_payload(e)) for i,e in enumerate(events[start:], start) if e['stage']=='final_draft']
    if not finals:
        return None
    final_index, final = finals[-1]
    source = inputs.get('publication_context', {}).get('original_draft', final.get('draft'))
    if final.get('route_id') != route.id or final.get('draft') != source:
        return None
    gates = [(i,_payload(e)) for i,e in enumerate(events[start:final_index], start) if e['stage']=='essay_audit_consensus']
    if not gates:
        return None
    gate_index, gate = gates[-1]
    source_hash = digest(canonical(source))
    k = gate.get('k')
    if not (gate.get('audit_kind')=='audit_essay' and gate.get('status')=='complete'
            and gate.get('route_id')==route.id and gate.get('draft_sha256')==source_hash
            and gate.get('faithful') is True and gate.get('flags')==[]
            and type(k) is int and k>=3 and len(gate.get('samples', []))==k
            and all(s.get('faithful') is True and s.get('flags')==[] for s in gate['samples'])):
        return None
    spans = sentence_spans(source['body'])
    expected = [NODE.sub('',source['body'][a:b]).strip() for a,b in spans]
    if inputs.get('proposal'):
        expected.append(source['title'])
    records = []
    for index in range(gate_index-1,start-1,-1):
        event=events[index]
        if event['stage']!='audit_essay' or event['label']!='MODEL':
            continue
        try:
            template, raw_inputs = event['prompt'].split('\nINPUT_JSON\n',1)
            old = json.loads(raw_inputs)
            old.pop('validation_feedback',None)
            if digest(template+'\nINPUT_JSON\n'+canonical(old)) != gate['prompt_sha256']:
                continue
            if _payload(event).get('status')!='accepted':
                return None
            if any(old.get(key)!=inputs.get(key) for key in ('outline','root_conclusion','source_evidence','proposal')):
                return None
            if [(s['sentence'],s['text']) for s in old['sentences']] != list(enumerate(expected,1)):
                return None
            data = decode_response(Response(json.loads(event['response'])).text())
            schema = calls.response_schema('audit_essay',old)
            if hasattr(calls.provider,'normalize_output'):
                data = calls.provider.normalize_output(schema,data)
            validate_local(schema,data,calls.config)
            numbers=[label['sentence'] for label in data['labels']]
            if len(numbers)!=len(expected) or set(numbers)!=set(range(1,len(expected)+1)):
                return None
            if not {node for label in data['labels'] for node in label['node_ids']} <= {node.id for node in route.nodes}:
                return None
            previous=events[index-1] if index>0 else {}
            verdict=_payload(previous) if previous.get('stage')=='essay_audit' else {}
            if not (verdict.get('route_id')==route.id and verdict.get('prompt_sha256')==gate['prompt_sha256']
                    and verdict.get('faithful') is True and verdict.get('flags')==[]
                    and verdict.get('extra_steps')==[] and verdict.get('missing_node_ids')==[]):
                return None
            records.append((old,effective_labels(data['labels'],old)))
        except (ValueError,TypeError,KeyError,ValidationError):
            return None
        if len(records)==k:
            break
    if len(records)!=k:
        return None
    rows=[]
    labels_by_sentence={label['sentence']:label for label in records[0][1]}
    for row in records[0][0]['sentences']:
        if row['text'].startswith('#'):
            continue
        if row['sentence'] > len(spans):
            continue  # Title changes keep their document-level audit.
        a,b=spans[row['sentence']-1]
        rows.append(dict(source_sentence=row['sentence'], text=row['text'], label=labels_by_sentence[row['sentence']],
                         source_start=a,source_end=b,raw_source_text=source['body'][a:b],
                         citation_markers=CITATIONS.findall(row['text']), proposal_scope=row.get('proposal_scope')))
    return dict(source_sha256=source_hash, gate_event=gate_index+1, gate_sha256=digest(canonical(gate)),
                source_bibliography=source['bibliography'], rows=rows)


def aligned_pairs(source, inputs, draft):
    """Similarity proposes a pair only; it never licenses a clean verdict."""
    from ara.runtime.essay_audit import sentence_spans
    body_count=len(sentence_spans(draft['body'],literature='publication_context' in inputs))
    bibliography={b['id']:b for b in draft.get('bibliography',[])}
    original={b['id']:b for b in source['source_bibliography']}
    pairs=[]
    for sentence in inputs['sentences']:
        if sentence['sentence']>body_count or sentence.get('field')=='title' or sentence['text'].startswith('#'):
            continue
        markers=CITATIONS.findall(sentence['text'])
        if any(bibliography.get(m[6:-1])!=original.get(m[6:-1]) for m in markers if m.startswith('[cite:')):
            continue
        text=normalized_sentence(sentence['text'])
        candidates=[r for r in source['rows'] if r['citation_markers']==markers]
        target_prefix=PREFIX.match(' '.join(sentence['text'].split()))
        def removal_or_unchanged(row):
            source_prefix=PREFIX.match(' '.join(row['text'].split()))
            return target_prefix is None or (source_prefix is not None and source_prefix[0].casefold()==target_prefix[0].casefold())
        exact=[r for r in candidates if normalized_sentence(r['text'])==text and removal_or_unchanged(r)]
        if exact:
            # Identical duplicate text with incompatible roles is ambiguous.
            if len({canonical({k:v for k,v in r['label'].items() if k!='sentence'}) for r in exact})!=1:
                continue
            row=exact[0];method='prefix_only'
        else:
            scores=sorted([(SequenceMatcher(None,normalized_sentence(r['text']),text,autojunk=False).ratio(),i,r)
                           for i,r in enumerate(candidates)],key=lambda t:t[0],reverse=True)
            if not scores or scores[0][0]<0.45 or (len(scores)>1 and scores[0][0]==scores[1][0]):
                continue
            row=scores[0][2];method='meaning_check'
        pair=dict(sentence=sentence['sentence'],source_sentence=row['source_sentence'],
                  source_text=row['text'],raw_source_text=row['raw_source_text'],
                  source_start=row['source_start'],source_end=row['source_end'],text=sentence['text'],label={**row['label'],'sentence':sentence['sentence']},
                  citation_markers=markers,method=method,
                  source_scope=row.get('proposal_scope'),scope=sentence.get('proposal_scope'),section=sentence.get('section'))
        identity={k:v for k,v in pair.items() if k!='sentence'}
        identity['label']={k:v for k,v in pair['label'].items() if k!='sentence'}
        pair['pair_sha256']=digest(canonical(dict(source_sha256=source['source_sha256'],gate_sha256=source['gate_sha256'],pair=identity)))
        pairs.append(pair)
    return pairs


def carryover_receipt(calls, route, draft, inputs):
    events=calls.log.read()
    source=verified_source_rows(calls,route,draft,inputs,events=events)
    if source is None:
        return None
    decisions={}
    for event in events:
        if event['stage']=='sentence_meaning_consensus':
            for pair in _payload(event)['pairs']:
                # A recorded dissent is never replaced with a later clean reroll.
                key=pair['pair_sha256']
                if key not in decisions or not pair['inherited']:
                    decisions[key]=pair
    rows=[];checks=[]
    for pair in aligned_pairs(source,inputs,draft):
        if pair['method']=='prefix_only':
            rows.append(pair)
        elif pair['pair_sha256'] in decisions:
            decision=decisions[pair['pair_sha256']]
            checks.append(decision)
            if decision['inherited']:
                rows.append({**pair,'method':'meaning_preserved','votes':decision['votes']})
    return dict(source_sha256=source['source_sha256'],gate_event=source['gate_event'],gate_sha256=source['gate_sha256'],
                sentences=rows,meaning_checks=checks)


def effective_labels(labels, inputs):
    carried={p['sentence']:p for p in inputs.get('verified_sentence_carryover',{}).get('sentences',[])}
    return [{**label,**carried[label['sentence']]['label'],
             **({'publication_issue':'none'} if 'publication_issue' in label else {})}
            if label['sentence'] in carried else label for label in labels]


def prepare_meaning_checks(calls, route, draft, inputs):
    """Three fresh votes once per bound pair, with adverse retry/history retention."""
    from jsonschema import Draft202012Validator
    from ara.runtime.providers import Response
    from ara.runtime.validation import decode_response
    source=verified_source_rows(calls,route,draft,inputs)
    if source is None:
        return False
    receipt=inputs.get('verified_sentence_carryover',{})
    decided={p['pair_sha256'] for p in receipt.get('meaning_checks',[])}
    pairs=[p for p in aligned_pairs(source,inputs,draft) if p['method']=='meaning_check' and p['pair_sha256'] not in decided]
    if not pairs:
        return False
    kind='audit_publication' if 'publication_context' in inputs else 'audit_essay'
    scoped=calls._for_construction_stage(kind,inputs)
    request=dict(source_sha256=source['source_sha256'],gate_sha256=source['gate_sha256'],pairs=pairs,
                 outline=inputs['outline'],proposal=inputs.get('proposal'))
    samples=[]
    expected={(p['sentence'],p['source_sentence']) for p in pairs}
    def check(data):
        keys=[(p['sentence'],p['source_sentence']) for p in data['pairs']]
        counts=Counter(keys)
        if len(keys)!=len(counts) or set(keys)!=expected:
            inventory=dict(expected=len(expected),returned=len(keys),
                           missing=sorted(expected-set(keys)),extra=sorted(set(keys)-expected),
                           duplicates=sorted(key for key,count in counts.items() if count>1))
            detail='; '.join(f'{name}={json.dumps(value)}' for name,value in inventory.items())
            raise ValidationError('meaning check pair inventory mismatch: '+detail)
        return data
    for sample in range(1,4):
        # One shape correction even when the parent publication permits no retries.
        # Valid adverse votes from either attempt remain binding below.
        value=scoped.call('audit_meaning',request,check,fresh=True,validation_attempts=2)
        samples.append(dict(sample=sample,pairs=value['pairs']))
    # Include valid adverse votes in malformed responses/retries or interrupted gates.
    adverse={key:[] for key in expected}
    current_pairs={p['pair_sha256']:(p['sentence'],p['source_sentence']) for p in pairs}
    row_validator=Draft202012Validator(scoped.response_schema('audit_meaning',request)['properties']['pairs']['items'])
    for index,event in enumerate(calls.log.read(),1):
        if event['stage']!='audit_meaning' or event['label']!='MODEL':
            continue
        try:
            old=json.loads(event['prompt'].split('\nINPUT_JSON\n',1)[1]);old.pop('topic',None);old.pop('validation_feedback',None)
            if any(old.get(k)!=request[k] for k in ('source_sha256','gate_sha256','outline','proposal')):
                continue
            old_pairs={(p['sentence'],p['source_sentence']):p['pair_sha256'] for p in old['pairs']}
            data=decode_response(Response(json.loads(event['response'])).text())
            for row in data.get('pairs',[]):
                if not row_validator.is_valid(row):
                    continue
                key=current_pairs.get(old_pairs.get((row['sentence'],row['source_sentence'])))
                if key in adverse and row.get('verdict') in ('different','uncertain'):
                    adverse[key].append(dict(event=index,**row))
        except (ValueError,TypeError,KeyError,AttributeError):
            continue
    decisions=[]
    for pair in pairs:
        key=(pair['sentence'],pair['source_sentence'])
        votes=[dict(sample=s['sample'],**next(r for r in s['pairs'] if (r['sentence'],r['source_sentence'])==key)) for s in samples]
        inherited=all(v['verdict']=='equivalent' for v in votes) and not adverse[key]
        decisions.append(dict(**pair,votes=votes,historical_adverse=adverse[key],inherited=inherited,
                              outcome='inherit_source_verdict' if inherited else 'normal_audit'))
    calls.log.record('sentence_meaning_consensus',route_id=route.id,source_sha256=source['source_sha256'],
                     draft_sha256=digest(canonical(draft)),k=3,pairs=decisions)
    return True
