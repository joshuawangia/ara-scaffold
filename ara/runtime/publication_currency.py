"""Logged literature-currency inputs, separate from frozen argument support."""
import json
import re
from hashlib import sha256

from ara.runtime.calls import require

HEADING = 'Related work and scope of the novelty claim'
LIT = re.compile(r'\[lit:([^\]]+)\]')


def load_currency(paths, log):
    if not paths:
        return None
    result = dict(records=[], evidence={}, excluded_metadata=[], sources={}, assessments=[])
    for path in paths:
        raw = path.read_text()
        require(len(raw) <= 2_000_000, 'currency record exceeds input bound')
        data = json.loads(raw)
        name = data.get('task', '')
        require(re.fullmatch(r'[A-Za-z0-9_-]+', name) is not None, 'currency record needs a task id')
        require(name not in {r['id'] for r in result['records']}, 'duplicate currency record')
        if 'evidence_register' in data:
            verification = data.get('verification', {})
            require(verification.get('tracked_files_unchanged') is True and verification.get('existing_26_pdfs_unchanged') is True,
                    'currency verification receipt missing')
            entries = [dict(id=key, **value) for key, value in data['evidence_register'].items()]
            sources = data.get('records', [])
            scope = dict(coverage=data['coverage'], queries=[{k:q[k] for k in ('id','query') if k in q} for q in data.get('query_catalog', [])])
            result['assessments'].extend(data.get('thesis_currency', []))
        else:
            verification = data.get('handoff_verification', {})
            require(verification.get('verified_at') and verification.get('errors') == [], 'currency verification receipt missing')
            entries = data['evidence']
            sources = data.get('added_records', []) + data.get('new_unavailable_records', [])
            scope = {k: data[k] for k in ('search_window','search_scope','verdict','exact_link_found',
                     'confidence_scope','addressed_criterion','partial_basis','coverage')}
        log.human('publication_currency_input', raw, path=str(path), sha256=sha256(raw.encode()).hexdigest())
        result['records'].append(dict(id=name, sha256=sha256(raw.encode()).hexdigest(), verification=verification))
        result['evidence'][name+':search'] = dict(work=None, claim=scope,
            kind='bounded_search_record', location=data.get('search_window','2018–2026 search'), year=2026)
        for entry in entries:
            if entry['kind'] not in ('read_fulltext', 'read_fulltext_passages'):
                result['excluded_metadata'].append({k:entry[k] for k in ('work','kind','claim')})
                continue
            location = entry.get('location')
            if not location:
                pages = entry.get('pdf_pages')
                require(pages and all(type(p) is int and p > 0 for p in pages), 'currency page references missing')
                location = 'PDF pp. ' + ', '.join(map(str,pages)) + '; §' + entry['section']
            require(isinstance(location,str) and 'PDF' in location, 'currency verified PDF location missing')
            key = name+':'+entry['id']
            result['evidence'][key] = dict(work=entry['work'],claim=entry['claim'],location=location,
                kind=entry['kind'],year=entry.get('year'),version_note=entry.get('version_note'))
        for source in sources:
            result['sources'][source['id']] = {k:source[k] for k in ('id','title','authors','year','doi','version_details') if k in source}
    result['assessments'] = [{k:r[k] for k in ('id','thesis','status','assessment','evidence_ids') if k in r}
                             for r in result['assessments']]
    require(any(e['work'] for e in result['evidence'].values()), 'currency record has no read evidence')
    return result


def related_text(markdown):
    found = re.findall(r'^## \d+\. '+re.escape(HEADING)+r'\s*\n(.*?)(?=^## |\Z)', markdown, re.M|re.S)
    require(len(found) == 1, 'publication needs one related-work section')
    return found[0]


def check_currency(markdown, currency):
    used = set(LIT.findall(markdown))
    if currency is None:
        require(not used, 'literature citation without currency input')
        return
    related = related_text(markdown)
    require(used <= currency['evidence'].keys(), 'unrecorded literature citation')
    require(used and any(currency['evidence'][id]['kind']=='bounded_search_record' for id in used),
            'related-work section missing search-scope citation')
    require(any(currency['evidence'][id]['work'] for id in used), 'related-work section missing source citation')
    require(LIT.findall(markdown) == LIT.findall(related), 'literature evidence belongs only in related work')
    require('[[node:' not in related, 'literature currency must not enlarge the route')
