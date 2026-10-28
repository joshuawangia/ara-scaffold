"""Citation-aware sentence spans and bounded repair of complete adverse audits."""
import re

from ara.runtime.cache import canonical, digest
from ara.runtime.calls import EssayAuditFailed, require, word_count

NODE = re.compile(r'\[\[node:[^\]]+\]\]')
CITE = re.compile(r'\[cite:[^\]]+\]')
BOUNDARY = re.compile(r'''[.!?]["”’')]*(?:\s*\[cite:[^\]]+\])*(?=\s|$)|\n+''')


def sentence_spans(body):
    """Keep original offsets; node markers are transparent to punctuation."""
    masked = NODE.sub(lambda match: ' ' * len(match.group()), body)
    spans, start = [], 0
    for match in BOUNDARY.finditer(masked):
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


def audit_and_revise(calls, route, draft):
    for round_number in range(3):
        try:
            calls.audit_essay(route, draft)
            return draft
        except EssayAuditFailed as failure:
            flags = [label for label in failure.labels
                     if label['asserts_premise_or_inference_not_in_outline']]
            if round_number == 2 or not flags:
                calls.log.record('essay_audit_revision_exhausted', rounds=round_number,
                                 **failure.result)
                raise
            spans = sentence_spans(draft['body'])
            originals = {flag['sentence']: draft['body'][slice(*spans[flag['sentence'] - 1])]
                         for flag in flags}
            inputs = dict(audit_inputs=failure.inputs, flags=flags,
                          flagged_sentences=[dict(sentence=n, text=text) for n, text in originals.items()],
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
                        require(CITE.findall(text) == CITE.findall(old), 'revision changed citations')
                        require(NODE.findall(text) == NODE.findall(old), 'revision changed node markers')
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
