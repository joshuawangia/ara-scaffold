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
            if not inputs.get('proposal') and sentence.get('section', '').casefold() != HEADING.casefold():
                reasons.append('literature_scope')
            if not label['citation_supported'] or any(id not in evidence for id in cited):
                reasons.append('miscited_literature_claim')
            if label['node_ids']:
                reasons.append('literature_route_mapping')
            if not reasons and '[cite:' not in sentence.get('text', ''):
                flags = [f for f in flags if not (f['sentence'] == label['sentence']
                         and f['reason'] == 'miscited_source_claim')]
        advisory = inputs.get('proposal') and label['publication_issue'] in ('thesis_placement', 'literature_scope')
        if label['publication_issue'] != 'none' and not advisory:
            reasons.append(label['publication_issue'])
        for reason in reasons:
            flag = dict(sentence=label['sentence'], role=label['role'], reason=reason)
            if flag not in flags:
                flags.append(flag)
    return flags


def document_blocks(markdown):
    """Retain exact ranges, including non-prose blocks excluded by paragraphs()."""
    from ara.runtime.publication import FIGURE
    blocks = []
    paragraph_index = 0
    for match in re.finditer(r'\S[\s\S]*?(?=\n\s*\n|\Z)', markdown):
        text = match[0].rstrip()
        kind = ('title' if not blocks and text.startswith('# ') else
                'heading' if text.startswith('#') else
                'figure' if FIGURE.fullmatch(text) else 'paragraph')
        blocks.append(dict(kind=kind, start=match.start(), end=match.start()+len(text),
                           paragraph_index=paragraph_index if kind == 'paragraph' else None))
        paragraph_index += kind == 'paragraph'
    return blocks


def repair_locations(markdown, flagged):
    """Bind the auditor's field offsets to their unique original block occurrence."""
    from ara.runtime.calls import require
    from ara.runtime.essay_audit import NODE
    blocks = document_blocks(markdown)
    newline = markdown.index('\n')
    tail = markdown[newline+1:]
    body_start = newline + 1 + len(tail) - len(tail.lstrip())
    title_start = 2 + len(markdown[2:newline]) - len(markdown[2:newline].lstrip())
    result = []
    for sentence in flagged:
        origin = title_start if sentence['field'] == 'title' else body_start
        start, end = origin + sentence['start'], origin + sentence['end']
        require(NODE.sub('', markdown[start:end]).strip() == sentence['text'],
                'publication audit sentence offsets do not match current draft')
        owners = [(i, b) for i, b in enumerate(blocks) if b['start'] <= start < end <= b['end']]
        require(len(owners) == 1, 'publication audit sentence must have one owning block')
        index, block = owners[0]
        result.append(dict(**sentence, location=dict(block_index=index, kind=block['kind'],
            paragraph_index=block['paragraph_index'], start=start-block['start'], end=end-block['start'])))
    return result


def validate_repair_scope(before, after, allowed_blocks):
    """Every unflagged block and every separator remains byte-for-byte unchanged."""
    from ara.runtime.calls import require
    old, new = document_blocks(before), document_blocks(after)
    require(len(old) == len(new), 'publication repair changed block inventory')
    old_end = new_end = 0
    for index, (a, b) in enumerate(zip(old, new)):
        require(a['kind'] == b['kind'], 'publication repair changed block kind')
        require(before[old_end:a['start']] == after[new_end:b['start']],
                'publication repair changed an unflagged separator')
        if index not in allowed_blocks:
            require(before[a['start']:a['end']] == after[b['start']:b['end']],
                    'publication repair changed an unflagged block')
        old_end, new_end = a['end'], b['end']
    require(before[old_end:] == after[new_end:], 'publication repair changed an unflagged separator')


def validate_sentence_repair(before, after, flagged):
    """Keep the literal spans between flagged occurrences unchanged, even within a block."""
    from ara.runtime.calls import require
    old, new = document_blocks(before), document_blocks(after)
    for index in sorted({s['location']['block_index'] for s in flagged}):
        a, b = old[index], new[index]
        original = before[a['start']:a['end']]
        ranges = sorted((s['location']['start'], s['location']['end']) for s in flagged
                        if s['location']['block_index'] == index)
        parts, end = [], 0
        for start, stop in ranges:
            require(start >= end, 'publication repair sentence ranges overlap')
            parts.extend((re.escape(original[end:start]), r'[\s\S]*?'))
            end = stop
        parts.append(re.escape(original[end:]))
        require(re.fullmatch(''.join(parts), after[b['start']:b['end']]) is not None,
                'publication repair changed an unflagged sentence span')


def repair_length_feedback(before, after):
    """Use the same rendered reading-word basis as the publication length gate."""
    from ara.runtime.publication import NODE, FIGURE
    def words(text):
        return len(NODE.sub('', FIGURE.sub('', text)).split())
    def sections(text):
        headers = list(re.finditer(r'^## (.+)$', text, re.M))
        return [(m[1], words(text[m.start():headers[i+1].start() if i+1 < len(headers) else len(text)]))
                for i, m in enumerate(headers)]
    old, new = sections(before), sections(after)
    shrunken = []
    for i, (heading, count) in enumerate(old):
        current = new[i][1] if i < len(new) else 0
        if current < count:
            shrunken.append(dict(section=heading, before=count, after=current, delta=current-count))
    return dict(previous_words=words(before), words=words(after), shrunken_sections=shrunken)
