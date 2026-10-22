"""Deterministic lexical grounding; quarantine is retained, never evidence."""
import re
import unicodedata

from ara.runtime.cache import canonical, digest

VERSION = 'page-token-grounding-v1'
STOP_WORDS = frozenset('a an the and or but if then of to in on at by for from with as is are was were be been being it its this that these those he she they them their we our you your not no do does did can could would should may might must will have has had which who whom what when where why how so than also only some all any each such both into about there here'.split())
POLICY = dict(version=VERSION, minimum_overlap=0.5, minimum_matches=3,
              normalization='NFKC-casefold-letter-tokens-line-dehyphenation',
              stop_words_sha256=digest(canonical(sorted(STOP_WORDS))))


def normalized(text):
    text = unicodedata.normalize('NFKC', text).casefold()
    return re.sub(r'(?<=\w)-\s*\n\s*(?=\w)', '', text)


def tokens(text):
    return set(re.findall(r'[^\W\d_]+', normalized(text))) - STOP_WORDS


def references(item):
    return set((*item['premise_ids'], *item['qualification_ids'], *item['applies_to'],
                *((item['conclusion_id'],) if item['conclusion_id'] else ())))


def assessment(item, page_tokens):
    text = normalized(item['text']).strip()
    reasons = []
    if text.startswith(('placeholder', 'dummy', 'superseded')):
        reasons.append('junk_placeholder_prefix')
    if len(text) <= 2:
        reasons.append('junk_short_text')
    if text == normalized(item['attributed_to']).strip():
        reasons.append('junk_text_equals_attribution')
    if not re.search(r'[^\W\d_]', text):
        reasons.append('junk_nonword')
    words = tokens(text)
    cited = range(item['page_start'], item['page_end'] + 1)
    available = set().union(*(page_tokens.get(n, set()) for n in cited))
    matched = len(words & available)
    overlap = matched / len(words) if words else 0.0
    if not reasons and (not words or overlap < POLICY['minimum_overlap'] or
                        matched < min(POLICY['minimum_matches'], len(words))):
        reasons.append('insufficient_page_overlap')
    return dict(item_id=item['id'], status='quarantined', reasons=reasons,
                matched_tokens=matched, text_tokens=len(words), overlap=overlap, blocked_by=[])


def receipt_hash(items, quarantined, source_text_sha256):
    return digest(canonical(dict(items=sorted(items, key=lambda i: i['id']), quarantined=sorted(quarantined, key=lambda q: q['item_id']),
                                 source_text_sha256=source_text_sha256, policy=POLICY)))


def ground_outcome(paper, outcome, log):
    """Assess the full original inventory, including historical quarantines."""
    pages = {p.page: p.text for p in paper.readable_pages}
    items = outcome['items']
    by_id = {i['id']: i for i in items}
    if len(by_id) != len(items):
        raise ValueError('grounding duplicate item id')
    page_tokens = {number: tokens(text) for number, text in pages.items()}
    assessed = {i['id']: assessment(i, page_tokens) for i in items}
    rejected = {id for id, a in assessed.items() if a['reasons']}
    deps = {id: references(i) for id, i in by_id.items()}
    # A qualification may constrain an inference without a reciprocal edge.
    for id, refs in tuple(deps.items()):
        for target in refs:
            if target in by_id and by_id[target]['kind'] == 'inference':
                deps[target] = deps[target] | {id}
    while True:
        added = set()
        for id in by_id.keys() - rejected:
            blocked = deps[id] & rejected
            if blocked or not deps[id] <= by_id.keys():
                assessed[id]['reasons'] = ['quarantined_dependency' if blocked else 'missing_dependency']
                assessed[id]['blocked_by'] = sorted(blocked or (deps[id] - by_id.keys()))
                added.add(id)
        if not added:
            break
        rejected |= added
    quarantined = [assessed[i['id']] for i in items if i['id'] in rejected]
    source_hash = digest(canonical(pages))
    grounding = dict(policy=POLICY, source_text_sha256=source_hash,
                     inventory_sha256=receipt_hash(items, quarantined, source_hash),
                     total_items=len(items), accepted_items=len(items)-len(quarantined))
    for entry in quarantined:
        log.record('extraction_item_quarantined', source_id=paper.source_id, **entry)
    log.record('extraction_grounding_revalidated', source_id=paper.source_id,
               **grounding, quarantined=len(quarantined))
    return {**outcome, 'grounding': grounding, 'quarantined': quarantined}


def evidence_items(paper):
    """Fail closed for old or modified inventories before citation selection/T."""
    items = paper['items']
    if not items:
        return []
    grounding = paper.get('grounding', {})
    quarantined = paper.get('quarantined', [])
    if (grounding.get('policy') != POLICY or
        grounding.get('inventory_sha256') != receipt_hash(items, quarantined, grounding.get('source_text_sha256'))):
        raise ValueError('literature requires offline grounding revalidation before use as evidence')
    blocked = {q['item_id'] for q in quarantined}
    return [item for item in items if item['id'] not in blocked]
