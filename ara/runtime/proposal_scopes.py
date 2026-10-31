"""Explicit prose ownership ranges; metadata never licenses a substantive claim."""
import re

def is_proposal_heading(heading):
    """A named Proposal section may carry a subtitle, without matching mentions."""
    return re.fullmatch(r'proposal(?:\s*[:—–-]\s*\S.*)?', heading.strip(), re.I) is not None


def sections(body):
    """Recognize standalone Markdown, numbered and ordinary prose headings."""
    headings = []
    for match in re.finditer(r'^([^\n]+)\n?', body, re.M):
        raw = match[1].strip()
        markdown = re.match(r'#{1,6}\s+(.+?)(?:\s+#+)?$', raw)
        text = markdown[1] if markdown else raw
        text = re.sub(r'^\d+[.)]\s+', '', text).strip()
        if not markdown and (not text or not text[0].isupper() or len(text.split()) > 12
                             or len(text) > 100 or re.search(r'[.!?;,\[\]*]', text)
                             or (':' in text and not is_proposal_heading(text))):
            continue
        headings.append(dict(heading=text, start=match.start(), content_start=match.end(),
                             level=len(raw)-len(raw.lstrip('#')) if markdown else 2))
    return [{**h, 'end': next((n['start'] for n in headings[i+1:] if n['level'] <= h['level']), len(body))}
            for i, h in enumerate(headings)]


def sentence_scopes(body, spans):
    """The declared bridge belongs in Proposal, ending at the next heading."""
    ranges = [dict(start=s['content_start'], end=s['end'], kind='section', heading=s['heading'])
              for s in sections(body) if is_proposal_heading(s['heading'])]
    return [next(({k:r[k] for k in ('kind','heading')} for r in ranges
                  if r['start'] <= start and end <= r['end']), None) for start,end in spans]
