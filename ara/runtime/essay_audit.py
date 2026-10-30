"""Citation-aware sentence spans and bounded repair of complete adverse audits."""
import json
import re

from jsonschema import ValidationError

from ara.runtime.cache import canonical, digest
from ara.runtime.calls import EssayAuditFailed, require, word_count

NODE = re.compile(r'\[\[node:[^\]]+\]\]')
CITE = re.compile(r'\[cite:[^\]]+\]')
BOUNDARY = re.compile(r'''[.!?]["”’')]*(?:\s*\[cite:[^\]]+\])*(?=\s|$)|\n+''')


def sentence_spans(body, *, literature=False):
    """Keep original offsets; node markers are transparent to punctuation."""
    masked = NODE.sub(lambda match: ' ' * len(match.group()), body)
    spans, start = [], 0
    boundary = re.compile(BOUNDARY.pattern.replace(r'\[cite:', r'\[(?:cite|lit):')) if literature else BOUNDARY
    for match in boundary.finditer(masked):
        end = match.start() if match.group().startswith('\n') else match.end()
        if not NODE.sub('', body[start:end]).strip():
            continue
        while start < end and body[start].isspace():
            start += 1
        while end > start and body[end - 1].isspace():
            end -= 1
        spans.append((start, end))
        start = match.end()
    if NODE.sub('', body[start:]).strip():
        while start < len(body) and body[start].isspace():
            start += 1
        spans.append((start, len(body.rstrip())))
    return spans


def audit_flags(labels, inputs, draft):
    """Apply the three typed failure rules; semantic role/support comes from audit."""
    sentences = {s['sentence']: s['text'] for s in inputs['sentences']}
    allowed = {b['id']: b for b in inputs.get('source_evidence', {}).get('allowed_bibliography', [])}
    bibliography = {b['id']: b for b in draft.get('bibliography', [])}
    flags = []
    for item in labels:
        role, reason = item['role'], None
        cited = [marker[6:-1] for marker in CITE.findall(sentences.get(item['sentence'], ''))]
        premises = {r['evidence_id'] for r in inputs['outline'].get('source_roles', [])
                    if r['role'] == 'global_premise' and r['node_id'] in item['node_ids']}
        from ara.runtime.proposal import role_failure
        proposal_reason = role_failure(role, sentences.get(item['sentence'], ''), inputs.get('proposal'))
        if proposal_reason:
            reason = proposal_reason
        elif inputs.get('proposal') and role == 'argument_step' and inputs['root_conclusion']['node_id'] in item['node_ids']:
            reason = 'proposal_presented_as_derivation'
        elif role == 'unsupported_claim':
            reason = 'unsupported_claim'
        elif role == 'argument_step' and not item['node_ids']:
            reason = 'unmapped_argument_step'
        elif role == 'argument_step' and premises and not premises <= set(cited):
            reason = 'miscited_source_claim'
        elif role == 'source_claim' or (cited and 'source_evidence' in inputs):
            if (not item['citation_supported'] or not cited or
                    any(tid not in allowed or bibliography.get(tid) != allowed[tid] for tid in cited)):
                reason = 'miscited_source_claim'
        if reason:
            flags.append(dict(sentence=item['sentence'], role=role, reason=reason))
    if 'publication_context' in inputs:
        from ara.runtime.publication_audit import publication_flags
        flags = publication_flags(labels, inputs, flags)
    return flags


def audit_result(route, draft, inputs, data):
    from collections import Counter
    ids = {n.id for n in route.nodes}
    expected = {s['sentence'] for s in inputs['sentences']}
    labels = data['labels']
    flags = audit_flags(labels, inputs, draft)
    numbers = [item['sentence'] for item in labels]
    if len(numbers) != len(set(numbers)) or set(numbers) != expected:
        require(not flags,
                'essay audit failed')
        # An incomplete non-adverse inventory supplies no audit verdict.
        # Correct its shape through the normal bounded validation policy;
        # a complete adverse audit remains final below.
        raise ValidationError('essay audit: sentence inventory mismatch')
    referenced = {node for item in labels for node in item['node_ids']}
    require(referenced <= ids, 'essay audit: unknown node id')
    covered = {node for item in labels if item['role'] in (('argument_step', 'source_claim', 'proposed_principle', 'argument_for_proposal')
                                                     if inputs.get('proposal') else ('argument_step', 'source_claim'))
               for node in item['node_ids']}
    missing = ids - covered
    if inputs.get('proposal') and not any(item['role'] == 'proposed_principle' and route.root_id in item['node_ids'] for item in labels):
        missing.add(route.root_id)
    extra = list(dict.fromkeys(item['sentence'] for item in flags))
    markers = set(re.findall(r'\[\[node:([^\]]+)\]\]', draft['body']))
    result = {'covered_node_ids': sorted(covered), 'missing_node_ids': sorted(missing),
              'extra_steps': extra, 'flags': flags,
              'role_counts': dict(Counter(item['role'] for item in labels)),
              'faithful': not missing and not extra and markers == ids}
    return result


def _same_audit_request(previous_prompt, prompt):
    """Validation feedback changes transport bytes, not the audited draft/evidence."""
    if previous_prompt == prompt:
        return True
    try:
        previous_template, previous_input = previous_prompt.split('\nINPUT_JSON\n', 1)
        template, current_input = prompt.split('\nINPUT_JSON\n', 1)
        previous = json.loads(previous_input)
        previous.pop('validation_feedback', None)
        return previous_template == template and previous == json.loads(current_input)
    except (ValueError, TypeError, AttributeError):
        return False


def _partial_adverse_history(route, draft, inputs, data, schema, config):
    """Salvage adverse facts only; an invalid inventory supplies no clean verdict."""
    from collections import Counter
    from jsonschema import Draft202012Validator
    from ara.runtime.validation import guard_complexity
    guard_complexity(data, config)
    if not isinstance(data, dict) or not isinstance(data.get('labels'), list):
        return None
    expected = {s['sentence'] for s in inputs['sentences']}
    nodes = {n.id for n in route.nodes}
    # The repository's label schema is shallow and fixed. Validate labels in
    # isolation so an unrelated invalid label cannot erase a valid adverse one.
    validator = Draft202012Validator(schema['properties']['labels']['items'])
    labels = [label for label in data['labels'] if validator.is_valid(label)
              and label['sentence'] in expected and set(label['node_ids']) <= nodes]
    adverse = [label for label in labels if audit_flags([label], inputs, draft)]
    flags = {(flag['sentence'], flag['reason']): flag for flag in audit_flags(adverse, inputs, draft)}
    if not flags:
        return None
    result = dict(covered_node_ids=[], missing_node_ids=[],
        extra_steps=sorted({n for n, _ in flags}), flags=[flags[key] for key in sorted(flags)],
        role_counts=dict(Counter(label['role'] for label in adverse)), faithful=False,
        partial_adverse_only=True)
    return result, adverse


def audit_consensus(calls, route, draft, *, publication_context=None):
    """Fresh samples plus unresolved adverse history; a dissent never votes away."""
    from ara.runtime.providers import Response
    from ara.runtime.validation import decode_response, validate_local
    k = calls.config.get('essay_audit_samples', 3)
    require(type(k) is int and k >= 3, 'essay_audit_samples must be an integer >= 3')
    context = {} if publication_context is None else dict(publication_context=publication_context)
    kind = 'audit_publication' if publication_context is not None else 'audit_essay'
    inputs = calls.audit_inputs(route, draft, **context)
    scoped = calls._for_construction_stage(kind, inputs)
    prompt = scoped.render(kind, inputs)[1]
    prompt_hash = digest(prompt)
    historical, failures, ignored = [], [], []
    def collect_history(events, *, start=0, partial_only=False):
        for index, event in enumerate(events[start:], start + 1):
            if event['stage'] != kind or event['label'] != 'MODEL':
                continue
            previous = events[index - 2] if index > 1 else {}
            recorded = json.loads(previous['payload_json']) if previous.get('stage') == 'essay_audit' else None
            if not _same_audit_request(event['prompt'], prompt) and (recorded or {}).get('prompt_sha256') != prompt_hash:
                continue
            data = None
            schema = scoped.response_schema(kind, inputs)
            try:
                data = decode_response(Response(json.loads(event['response'])).text())
                if hasattr(scoped.provider, 'normalize_output'):
                    data = scoped.provider.normalize_output(schema, data)
                validate_local(schema, data, calls.config)
                result = audit_result(route, draft, inputs, data)
                if recorded is not None:
                    result = {key: recorded[key] for key in result}
            except (ValueError, TypeError, KeyError, ValidationError) as exc:
                ignored.append(dict(event=index, reason=type(exc).__name__))
                recovered = _partial_adverse_history(route, draft, inputs, data, schema, calls.config)
                if recovered is not None:
                    ignored[-1]['retained_adverse'] = True
                    result, labels = recovered
                    historical.append(dict(event=index, invalid_reason=type(exc).__name__, **result))
                    failures.append(EssayAuditFailed(result, inputs, labels))
                continue
            if not partial_only and not result['faithful']:
                historical.append(dict(event=index, **result))
                failures.append(EssayAuditFailed(result, inputs, data['labels']))

    events = calls.log.read()
    collect_history(events)
    samples = []
    for number in range(1, k + 1):
        try:
            result = calls.audit_essay(route, draft, fresh=True, **context)
        except EssayAuditFailed as failure:
            failures.append(failure)
            result = failure.result
        except Exception as exc:
            calls.log.record('essay_audit_consensus', route_id=route.id, audit_kind=kind, prompt_sha256=prompt_hash,
                draft_sha256=digest(canonical(draft)), k=k, policy='fresh-unanimous-with-adverse-history',
                status='incomplete', failed_sample=number, reason=type(exc).__name__,
                samples=samples, historical_adverse=historical, unusable_history=ignored, faithful=False)
            raise
        samples.append(dict(sample=number, **result))
    # Schema retries append rejected receipts during this gate. A clean retry
    # cannot erase a valid adverse label in one of those rejected responses.
    # Complete sample verdicts are already represented in samples/failures.
    collect_history(calls.log.read(), start=len(events), partial_only=True)
    all_results = historical + samples
    flags = { (flag['sentence'], flag['reason']): flag
              for result in all_results for flag in result['flags'] }
    flags = [flags[key] for key in sorted(flags)]
    sentences = []
    for item in inputs['sentences']:
        n = item['sentence']
        flagged = [s['sample'] for s in samples if n in s['extra_steps']]
        clean = [s['sample'] for s in samples if n not in s['extra_steps']]
        sentences.append(dict(sentence=n, flagged_samples=flagged, clean_samples=clean,
            historical_flags=sorted({f['reason'] for s in historical for f in s['flags'] if f['sentence']==n}),
            agreement=max(len(flagged), len(clean)) / k))
    result = dict(route_id=route.id, audit_kind=kind, prompt_sha256=prompt_hash, draft_sha256=digest(canonical(draft)),
        k=k, policy='fresh-unanimous-with-adverse-history', status='complete', samples=samples,
        historical_adverse=historical, unusable_history=ignored, sentences=sentences,
        unanimous_sentences=sum(s['agreement']==1 for s in sentences), sentence_count=len(sentences),
        covered_node_ids=sorted(set.intersection(*(set(s['covered_node_ids']) for s in all_results))),
        missing_node_ids=sorted({n for s in all_results for n in s['missing_node_ids']}),
        extra_steps=sorted({f['sentence'] for f in flags}), flags=flags,
        faithful=all(s['faithful'] for s in all_results))
    calls.log.record('essay_audit_consensus', **result)
    if not result['faithful']:
        labels = {}
        for failure in failures:
            for label in failure.labels:
                if label['sentence'] in failure.result['extra_steps']:
                    labels.setdefault(label['sentence'], label)
        raise EssayAuditFailed(result, inputs, list(labels.values()))
    return result


def repair_rounds(calls, route):
    current, used = None, 0
    for event in calls.log.read():
        if event['stage'] == 'essay_composition_started':
            data = json.loads(event['payload_json'])
            current = data['route_id']
            if current == route.id:
                used = data.get('repair_rounds', 0)
        elif event['stage'] == 'essay_audit_revision' and current == route.id:
            used = max(used, json.loads(event['payload_json'])['round'])
    return used


def audit_and_revise(calls, route, draft, *, final=False):
    used = repair_rounds(calls, route)
    for round_number in range(used, 4):
        try:
            if final:
                cleaned, verification = calls.verify_originality_citations(draft)
                calls.validate_essay(route, cleaned, minimum_words=0)
                audit_consensus(calls, route, cleaned)
                return cleaned, verification
            calls.audit_essay(route, draft)
            return draft
        except EssayAuditFailed as failure:
            if final:
                draft = cleaned
            flags = [label for label in failure.labels
                     if label['sentence'] in failure.result['extra_steps']]
            if round_number == 3 or not flags:
                calls.log.record('essay_audit_revision_exhausted', rounds=round_number,
                                 **failure.result)
                raise
            spans = sentence_spans(draft['body'])
            originals = {flag['sentence']: (draft['title'] if flag['sentence'] == len(spans)+1 and failure.inputs.get('proposal')
                                           else draft['body'][slice(*spans[flag['sentence'] - 1])])
                         for flag in flags}
            citation_repairs = {f['sentence'] for f in failure.result['flags'] if f['reason'] == 'miscited_source_claim'}
            allowed = {b['id']: b for b in failure.inputs.get('source_evidence', {}).get('allowed_bibliography', [])}
            inputs = dict(audit_inputs=failure.inputs, flags=flags, audit_failures=failure.result['flags'],
                          citation_additions={str(n): sorted(allowed) for n in citation_repairs},
                          flagged_sentences=[dict(sentence=n, text=text,
                              citation_markers=CITE.findall(text), node_markers=NODE.findall(text))
                              for n, text in originals.items()],
                          bibliography=draft['bibliography'], round=round_number + 1,
                          minimum_words=0 if final else calls.config['essay_min_words'],
                          word_limit=min(6000, calls.config['essay_word_limit']),
                          current_words=word_count(draft))

            def check(data):
                replacements = data['revisions']
                numbers = [r['sentence'] for r in replacements]
                require(len(numbers) == len(set(numbers)) and set(numbers) == set(originals),
                        'revision must cover exactly the flagged sentences')
                body, title = draft['body'], draft['title']
                for item in sorted(replacements, key=lambda r: r['sentence'], reverse=True):
                    old, text = originals[item['sentence']], item['text']
                    require(not final or text != old, 'revision left flagged sentence unchanged')
                    require(len(text) <= max(1000, 2 * len(old)), 'revision sentence size exceeded')
                    if text:
                        for pattern, name in ((CITE, 'citations'), (NODE, 'node markers')):
                            expected, actual = pattern.findall(old), pattern.findall(text)
                            addition = (pattern is CITE and item['sentence'] in citation_repairs and
                                        actual[:len(expected)] == expected and
                                        all(marker[6:-1] in allowed for marker in actual[len(expected):]))
                            require(actual == expected or addition,
                                    f'revision changed {name} in sentence {item["sentence"]}: '
                                    f'forbidden or misplaced markers {actual!r}; required exact sequence {expected!r}')
                    if item['sentence'] == len(spans)+1 and failure.inputs.get('proposal'):
                        title = text
                    else:
                        start, end = spans[item['sentence'] - 1]
                        body = body[:start] + text + body[end:]
                revised = {**draft, 'body': body, 'title': title}
                bibliography = {b['id']: b for b in draft['bibliography']}
                for marker in CITE.findall(body):
                    tid = marker[6:-1]
                    if tid in allowed and tid not in bibliography:
                        bibliography[tid] = allowed[tid]
                revised['bibliography'] = list(bibliography.values())
                return calls.validate_essay(route, revised, minimum_words=0 if final else None)

            revised = calls.call('revise_essay', inputs, check)
            calls.log.record('essay_audit_revision', round=round_number + 1,
                             flagged_sentence_ids=sorted(originals),
                             before_sha256=digest(canonical(draft)), draft=revised,
                             words=word_count(revised))
            (calls.log.path.parent / 'draft.unverified.json').write_text(canonical(revised))
            draft = revised
    raise AssertionError('unreachable')
