"""Explicit prose ownership ranges; metadata never licenses a substantive claim."""
import re

PROPOSAL_HEADINGS = {'proposal', 'the bridge principle', 'objections and replies'}


def sections(body):
    """Recognize standalone Markdown, numbered and ordinary prose headings."""
    headings = []
    for match in re.finditer(r'^([^\n]+)\n?', body, re.M):
        raw = match[1].strip()
        markdown = re.match(r'#{1,6}\s+(.+?)(?:\s+#+)?$', raw)
        text = markdown[1] if markdown else raw
        text = re.sub(r'^\d+[.)]\s+', '', text).strip()
        if not markdown and (not text or not text[0].isupper() or len(text.split()) > 12
                             or len(text) > 100 or re.search(r'[.!?;:,\[\]*]', text)):
            continue
        headings.append(dict(heading=text, start=match.start(), content_start=match.end()))
    return [{**h, 'end': headings[i+1]['start'] if i+1 < len(headings) else len(body)}
            for i, h in enumerate(headings)]


def sentence_scopes(body, spans):
    """Scope ends at the next heading or, for Proposal: paragraphs, blank line."""
    ranges = [dict(start=s['content_start'], end=s['end'], kind='section', heading=s['heading'])
              for s in sections(body) if s['heading'].casefold() in PROPOSAL_HEADINGS]
    for block in re.finditer(r'(?:\A|\n[ \t]*\n)([^\n]*(?:\n(?![ \t]*\n)[^\n]*)*)', body):
        text = block[1]
        if re.match(r'[ \t]*(?:Proposal:|\*\*Proposal:\*\*)[ \t]+', text):
            ranges.append(dict(start=block.start(1), end=block.end(1), kind='paragraph', heading='Proposal:'))
    return [next(({k:r[k] for k in ('kind','heading')} for r in ranges
                  if r['start'] <= start and end <= r['end']), None) for start,end in spans]


def misplaced_status(body):
    """Process-search qualifications belong in the final note, not the opening."""
    for section in sections(body):
        if section['heading'].casefold() not in ('abstract', 'introduction'):
            continue
        text = body[section['content_start']:section['end']]
        if re.search(r'\bexternal AI\b|\bdossier\b|\bnot_found\b|\bcurrency verdict\b|'
                     r'\b(?:bounded|incomplete)[^.!?\n]{0,60}\bsearch\b|\bsearch[- ]scope\b|'
                     r'\bnovelty (?:certificate|certification)\b|\[lit:', text, re.I):
            return True
    return False
