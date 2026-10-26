"""Deterministic exact-token alignment around damaged text-layer spans."""
from collections import Counter
from itertools import groupby
import re
import unicodedata

from ara.runtime.ocr import OCRResult, bad_character, math_symbols, tainted_spans


def character_classes(text: str) -> dict:
    return dict(sorted(Counter(unicodedata.category(c) for c in text).items()))


def tokens(text: str) -> list[tuple[str, int, int]]:
    return [(unicodedata.normalize('NFKC', m[0]).casefold(), m.start(), m.end())
            for m in re.finditer(r'[^\W_]+', text)]


def occurrences(sequence, anchor):
    return [i for i in range(len(sequence) - len(anchor) + 1)
            if sequence[i:i + len(anchor)] == anchor]


def insertion_confidence(result: OCRResult, start: int, end: int):
    ranges = result.character_confidences
    text = result.text
    values = []
    for offset in range(start, end):
        if text[offset].isspace():
            continue
        scores = [p for a, b, p in ranges if a <= offset < b]
        if not scores:
            return None, None
        values.append(min(scores))
    if not values:
        return None, None
    return sum(values) / len(values), sum(p < 0.8 for p in values) / len(values)


def preserves_clean_fragments(before: str, insertion: str) -> bool:
    pattern = ''.join('.+?' if damaged else re.escape(''.join(chars))
                      for damaged, chars in groupby(before, key=bad_character))
    return re.fullmatch(pattern, insertion, flags=re.DOTALL) is not None


def repair_spans(original: str, result: OCRResult, *, accepted: dict | None = None):
    """Keep original coordinates across tiers; replace only accepted damaged runs.

    Align up to three adjacent clean alphanumeric tokens on each side, with
    exact normalized token-sequence matches unique in both streams. Never use
    another damaged run as an anchor or pick an arbitrary repeated match.
    """
    accepted = {} if accepted is None else accepted
    damaged = tainted_spans(original)
    source = tokens(original)
    target = tokens(result.text)
    source_values = [v if not any(a < end and start < b for start, end in damaged) else None
                     for v, a, b in source]
    target_values = [v for v, _, _ in target]
    groups = []
    for i, (a, b) in enumerate(damaged):
        if groups and not original[damaged[groups[-1][-1]][1]:a].strip():
            groups[-1].append(i)
        else:
            groups.append([i])
    records = []
    for index, (start, end) in enumerate(damaged):
        if index in accepted:
            continue
        before = original[start:end]
        record = dict(span=index, start=start, end=end, accepted=False, reason='missing_anchor',
                      confidence=None, low_confidence_char_share=None,
                      confidence_basis=result.confidence_basis, anchor_match={'unique': False},
                      before_classes=character_classes(before), after_classes=character_classes(before))
        records.append(record)
        group = next(g for g in groups if index in g)
        first, last = group[0], group[-1]
        group_start, group_end = damaged[first][0], damaged[last][1]
        lower = damaged[first - 1][1] if first else 0
        upper = damaged[last + 1][0] if last + 1 < len(damaged) else len(original)
        left = [i for i, (_, a, b) in enumerate(source) if lower <= a and b <= group_start][-3:]
        right = [i for i, (_, a, b) in enumerate(source) if group_end <= a and b <= upper][:3]
        if not left or not right:
            continue
        old_matches, new_matches, chosen = [], [], []
        for side, from_left in ((left, True), (right, False)):
            candidates = [side[-n:] if from_left else side[:n] for n in range(len(side), 0, -1)]
            for selection in candidates:
                anchor = [source_values[i] for i in selection]
                old = occurrences(source_values, anchor)
                new = occurrences(target_values, anchor)
                if len(old) == len(new) == 1:
                    break
            old_matches.append(old)
            new_matches.append(new)
            chosen.append(selection)
        left, right = chosen
        unique = all(len(matches) == 1 for matches in old_matches + new_matches)
        record['anchor_match'] = dict(unique=unique, source_matches=old_matches, ocr_matches=new_matches,
                                      token_counts=[len(left), len(right)], cluster_spans=group)
        if not unique:
            record['reason'] = 'anchor_not_unique'
            continue
        left_end = new_matches[0][0] + len(left) - 1
        right_start = new_matches[1][0]
        if left_end >= right_start:
            record['reason'] = 'anchor_order'
            continue
        a, b = target[left_end][2], target[right_start][1]
        prefix = original[source[left[-1]][2]:group_start].strip()
        suffix = original[group_end:source[right[0]][1]].strip()
        while a < b and result.text[a].isspace(): a += 1
        while b > a and result.text[b - 1].isspace(): b -= 1
        if not result.text[a:b].startswith(prefix) or not result.text[a:b].endswith(suffix):
            record['reason'] = 'clean_boundary_mismatch'
            continue
        a += len(prefix)
        b -= len(suffix)
        while a < b and result.text[a].isspace(): a += 1
        while b > a and result.text[b - 1].isspace(): b -= 1
        if len(group) > 1:
            candidates = list(re.finditer(r'\S+', result.text[a:b]))
            if len(candidates) != len(group):
                record['reason'] = 'cluster_alignment_ambiguous'
                continue
            candidate = candidates[group.index(index)]
            a, b = a + candidate.start(), a + candidate.end()
        insertion = result.text[a:b]
        confidence, low_share = insertion_confidence(result, a, b)
        record.update(confidence=confidence, low_confidence_char_share=low_share,
                      ocr_start=a, ocr_end=b, candidate_classes=character_classes(insertion))
        if not result.complete:
            record['reason'] = 'incomplete_generation'
        elif not insertion:
            record['reason'] = 'empty_insertion'
        elif any(bad_character(c) for c in insertion):
            record['reason'] = 'damaged_insertion'
        elif confidence is None:
            record['reason'] = 'unmapped_confidence'
        elif confidence < 0.95 or low_share > 0.05:
            record['reason'] = 'low_confidence'
        elif math_symbols(before) - math_symbols(insertion):
            record['reason'] = 'encoded_symbol_loss'
        elif not preserves_clean_fragments(before, insertion):
            record['reason'] = 'clean_fragment_changed'
        else:
            record.update(accepted=True, reason='accepted', after_classes=character_classes(insertion))
            accepted[index] = insertion
    pieces, position = [], 0
    for index, (start, end) in enumerate(damaged):
        pieces.extend((original[position:start], accepted.get(index, original[start:end])))
        position = end
    pieces.append(original[position:])
    return ''.join(pieces), records
