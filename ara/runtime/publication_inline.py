"""Bounded, occurrence-only repairs; all surrounding bytes are constructed locally."""
import re

from ara.runtime.cache import canonical, digest
from ara.runtime.calls import require

REASONS = frozenset(('unsupported_claim', 'unsupported_elaboration'))
LIMIT = 3
MARKERS = re.compile(r'\[(?:cite|lit):[^\]]+\]|\[\[node:[^\]]+\]\]|\{\{fig:[^}]+\}\}')


def sentence_range(markdown, sentence):
    from ara.runtime.publication_audit import repair_locations, document_blocks
    located = repair_locations(markdown, [sentence])[0]['location']
    block = document_blocks(markdown)[located['block_index']]
    require(located['kind'] == 'paragraph', 'inline repair requires a prose sentence')
    return block['start'] + located['start'], block['start'] + located['end']


def replace_sentence(markdown, sentence, replacement):
    from ara.runtime.essay_audit import sentence_spans
    start, end = sentence_range(markdown, sentence)
    require(isinstance(replacement, str) and '\n' not in replacement
            and len(sentence_spans(replacement, literature=True)) <= 1,
            'inline replacement must be a single sentence or empty')
    require(MARKERS.findall(markdown[start:end]) == MARKERS.findall(replacement),
            'inline replacement changed sentence marker inventory')
    return markdown[:start] + replacement + markdown[end:]


def eligible_sentences(markdown, rejection):
    from ara.runtime.publication_audit import repair_locations
    flags = rejection.result.get('flags', [])
    numbers = {f['sentence'] for f in flags if f['reason'] in REASONS}
    numbers -= {f['sentence'] for f in flags if f['reason'] not in REASONS}
    rows = [s for s in rejection.inputs['sentences'] if s['sentence'] in numbers]
    return [row for row, located in zip(rows, repair_locations(markdown, rows))
            if located['location']['kind'] == 'paragraph']


def with_markdown(candidate, markdown, reason):
    from ara.runtime.publication import FIGURE, paragraphs
    return dict(candidate, markdown=markdown,
        figure_placements=[dict(id=m[1], after_paragraph=len(paragraphs(markdown[:m.start()]))-1)
                           for m in FIGURE.finditer(markdown)],
        change_log=[dict(paragraph=i, improvement=reason) for i, _ in enumerate(paragraphs(markdown))])


def source_reversions(markdown, inputs):
    """Consume only native accepted, occurrence-bound source mappings."""
    from ara.runtime.essay_audit import NODE
    rows = {s['sentence']: s for s in inputs['sentences']}
    result = {}
    for pair in inputs.get('verified_sentence_carryover', {}).get('sentences', []):
        row = rows.get(pair.get('sentence'))
        method = pair.get('method')
        if row is None or pair.get('text') != row['text']:
            continue
        if method == 'meaning_preserved':
            votes = pair.get('votes', [])
            if len(votes) != 3 or any(v.get('verdict') != 'equivalent' for v in votes):
                continue
        elif method != 'prefix_only':
            continue
        raw = pair.get('raw_source_text', pair.get('source_text'))
        if not isinstance(raw, str):
            continue
        start, end = sentence_range(markdown, row)
        current = markdown[start:end]
        nodes = NODE.findall(current)
        replacement = (' '.join(nodes) + ' ' if nodes else '') + NODE.sub('', raw).strip()
        if MARKERS.findall(current) == MARKERS.findall(replacement):
            result[row['sentence']] = replacement
    return result


def repair(calls, candidate, rejection, base, check_whole, pass_number):
    require(type(pass_number) is int and 1 <= pass_number <= LIMIT,
            'publication inline pass budget exhausted')
    flags = rejection.result['flags']
    rows = eligible_sentences(candidate['markdown'], rejection)
    require(bool(rows), 'publication inline repair has no eligible sentences')
    for row in rows:
        sentence_range(candidate['markdown'], row)
    calls.log.record('publication_inline_started', pass_number=pass_number,
        candidate_sha256=digest(canonical(candidate)), flagged_sentences=rows,
        audit_failures=flags, whole_paper_rounds_unchanged=True)
    before = candidate
    reversions = source_reversions(candidate['markdown'], {**rejection.inputs, 'sentences': rows})
    edits = []
    for row in sorted(rows, key=lambda s: sentence_range(before['markdown'], s)[0], reverse=True):
        start, end = sentence_range(before['markdown'], row)
        sentence_text = before['markdown'][start:end]
        def validate(value):
            replacement = value['replacement']
            updated = with_markdown(candidate, replace_sentence(candidate['markdown'], row, replacement),
                                    'Occurrence-bound inline repair; surrounding text retained.')
            check_whole(updated)
            return updated, replacement
        source = reversions.get(row['sentence'])
        if source is not None:
            updated, replacement = validate(dict(replacement=source))
            origin = 'verified_source_reversion'
        else:
            updated, replacement = calls.call('repair_publication_sentence',
                dict(**base, sentence=row, sentence_text=sentence_text,
                     reasons=[f['reason'] for f in flags if f['sentence'] == row['sentence']],
                     inline_pass=pass_number), validate, fresh=True, validation_attempts=2)
            origin = 'isolated_model_sentence_edit'
        edits.append(dict(sentence=row['sentence'], start=start, end=end,
                          before=sentence_text, after=replacement, origin=origin))
        candidate = updated
    require(candidate['markdown'] != before['markdown'], 'publication inline repair made no change')
    calls.log.record('publication_inline_repair', pass_number=pass_number,
        before_sha256=digest(canonical(before)), edits=edits, **candidate)
    return candidate
