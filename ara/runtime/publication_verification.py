"""Address native quotation failures without authorizing substantive rewrites."""
import re
from ara.runtime.calls import require


def _failed_quotes(draft, failed):
    # Preserve the native verifier's quote:index inventory, including duplicates.
    quotes = list(re.finditer(r'"([^"\n]+)"|“([^”]+)”', draft['body']))
    selected = []
    for item in failed:
        match = re.fullmatch(r'quote:(\d+)', item['id'])
        require(item.get('kind') == 'quotation' and match is not None,
                'publication verification failure is not an addressable quotation')
        index = int(match[1])
        require(index < len(quotes), 'publication quotation occurrence is missing')
        quote = quotes[index]
        require((quote[1] or quote[2]) == item['text'],
                'publication quotation occurrence text differs from verification')
        selected.append(quote)
    return selected


def quotation_flags(draft, inputs, failed):
    numbers = set()
    for quote in _failed_quotes(draft, failed):
        covered = [s for s in inputs['sentences'] if s.get('field') == 'body'
                   and s['start'] < quote.end() and quote.start() < s['end']]
        require(bool(covered) and min(s['start'] for s in covered) <= quote.start()
                and max(s['end'] for s in covered) >= quote.end(),
                'publication quotation occurrence cannot be located in sentences')
        numbers.update(s['sentence'] for s in covered)
    return [dict(sentence=n, role='source_claim', reason='unverified_quotation')
            for n in sorted(numbers)]


def title_format_body(draft, failed, titles):
    require(all(item['text'] in titles for item in failed),
            'unverified quotation is not an exact logged work title; substantive verification refusal')
    body = draft['body']
    for quote in sorted(_failed_quotes(draft, failed), key=lambda q:q.start(), reverse=True):
        body = body[:quote.start()] + '*' + (quote[1] or quote[2]) + '*' + body[quote.end():]
    return body
