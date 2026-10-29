"""Publication-only scope checks around the native typed sentence audit."""
import re

from ara.runtime.publication_currency import HEADING, LIT


def sentence_sections(body, spans):
    headings = list(re.finditer(r'^##\s+(?:\d+\.\s+)?(.+)$', body, re.M))
    return [next((h[1] for h in reversed(headings) if h.start() <= start), '')
            for start, _ in spans]


def publication_flags(labels, inputs, native_flags):
    sentences = {s['sentence']: s for s in inputs['sentences']}
    currency = inputs['publication_context'].get('literature_currency') or {}
    evidence = currency.get('evidence', {})
    flags = list(native_flags)
    for label in labels:
        sentence = sentences.get(label['sentence'], {})
        cited = LIT.findall(sentence.get('text', ''))
        reasons = []
        if cited:
            if sentence.get('section') != HEADING:
                reasons.append('literature_scope')
            if not label['citation_supported'] or any(id not in evidence for id in cited):
                reasons.append('miscited_literature_claim')
            if label['node_ids']:
                reasons.append('literature_route_mapping')
            if not reasons and '[cite:' not in sentence.get('text', ''):
                flags = [f for f in flags if not (f['sentence'] == label['sentence']
                         and f['reason'] == 'miscited_source_claim')]
        if label['publication_issue'] != 'none':
            reasons.append(label['publication_issue'])
        for reason in reasons:
            flag = dict(sentence=label['sentence'], role=label['role'], reason=reason)
            if flag not in flags:
                flags.append(flag)
    return flags
