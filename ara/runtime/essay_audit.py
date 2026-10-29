"""Citation-aware sentence spans and bounded repair of complete adverse audits."""
import re

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
        if role == 'unsupported_claim':
            reason = 'unsupported_claim'
        elif role == 'argument_step' and not item['node_ids']:
            reason = 'unmapped_argument_step'
        elif role == 'source_claim':
            cited = [marker[6:-1] for marker in CITE.findall(sentences.get(item['sentence'], ''))]
            if (not item['citation_supported'] or not cited or
                    any(tid not in allowed or bibliography.get(tid) != allowed[tid] for tid in cited)):
                reason = 'miscited_source_claim'
        if reason:
            flags.append(dict(sentence=item['sentence'], role=role, reason=reason))
    return flags


def audit_and_revise(calls, route, draft):
    for round_number in range(4):
        try:
            calls.audit_essay(route, draft)
            return draft
        except EssayAuditFailed as failure:
            flags = [label for label in failure.labels
                     if label['sentence'] in failure.result['extra_steps']]
            if round_number == 3 or not flags:
                calls.log.record('essay_audit_revision_exhausted', rounds=round_number,
                                 **failure.result)
                raise
            spans = sentence_spans(draft['body'])
            originals = {flag['sentence']: draft['body'][slice(*spans[flag['sentence'] - 1])]
                         for flag in flags}
            inputs = dict(audit_inputs=failure.inputs, flags=flags, audit_failures=failure.result['flags'],
                          flagged_sentences=[dict(sentence=n, text=text,
                              citation_markers=CITE.findall(text), node_markers=NODE.findall(text))
                              for n, text in originals.items()],
                          bibliography=draft['bibliography'], round=round_number + 1,
                          minimum_words=calls.config['essay_min_words'],
                          word_limit=min(6000, calls.config['essay_word_limit']),
                          current_words=word_count(draft))

            def check(data):
                replacements = data['revisions']
                numbers = [r['sentence'] for r in replacements]
                require(len(numbers) == len(set(numbers)) and set(numbers) == set(originals),
                        'revision must cover exactly the flagged sentences')
                body = draft['body']
                for item in sorted(replacements, key=lambda r: r['sentence'], reverse=True):
                    old, text = originals[item['sentence']], item['text']
                    require(len(text) <= max(1000, 2 * len(old)), 'revision sentence size exceeded')
                    if text:
                        for pattern, name in ((CITE, 'citations'), (NODE, 'node markers')):
                            expected, actual = pattern.findall(old), pattern.findall(text)
                            require(actual == expected,
                                    f'revision changed {name} in sentence {item["sentence"]}: '
                                    f'forbidden or misplaced markers {actual!r}; required exact sequence {expected!r}')
                    start, end = spans[item['sentence'] - 1]
                    body = body[:start] + text + body[end:]
                revised = {**draft, 'body': body}
                return calls.validate_essay(route, revised)

            revised = calls.call('revise_essay', inputs, check)
            calls.log.record('essay_audit_revision', round=round_number + 1,
                             flagged_sentence_ids=sorted(originals),
                             before_sha256=digest(canonical(draft)), draft=revised,
                             words=word_count(revised))
            (calls.log.path.parent / 'draft.unverified.json').write_text(canonical(revised))
            draft = revised
    raise AssertionError('unreachable')
