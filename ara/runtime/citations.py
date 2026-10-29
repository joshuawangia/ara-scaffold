"""Frozen-route citations, checked against retained local extraction evidence."""
from __future__ import annotations

import json
import re

from ara.runtime.cache import canonical, digest
from ara.runtime.extraction import HEADER
from ara.runtime.grounding import evidence_items, assessment, tokens
from ara.runtime.route_policy import frozen_from_events, provenance_from_events

CITATION = re.compile(r'\[cite:([^\]]+)\]')


def support_ids(route, frozen):
    ids = {n.t_id for n in route.nodes if n.kind == 'leaf' and n.t_id != 'open'}
    ids.update(tid for n in route.nodes for a in n.cq_answers for tid in a.supporting_t_ids)
    if frozen is not None:
        ids.update(c.id for n in route.nodes if n.kind == 'assumption' and n.proposition.formula is not None
                   for c in frozen.commitments if c.formula.canonical() == n.proposition.formula.canonical())
    return ids


def bibliography_entry(tid, commitment, source, record):
    if not record or any(not record.get(k) for k in ('authors', 'year', 'title')):
        return dict(id=tid, text=commitment.citation, url=None)
    pages = str(source['page_start'])
    if source['page_end'] != source['page_start']:
        pages += '-' + str(source['page_end'])
    text = f"{record['authors']} ({record['year']}). {record['title']}."
    if record.get('venue'):
        text += ' ' + str(record['venue']) + '.'
    text += ' PDF p. ' + pages + '.'
    return dict(id=tid, text=text, url=record.get('open_access_url'))


def catalogue(events, ids):
    """Use hash-bound page text already held in the log, never web absence."""
    frozen = frozen_from_events(events)
    provenance = provenance_from_events(events, frozen)
    if provenance is None:
        return {}
    wanted = {tid: provenance['commitments'][tid] for tid in ids if tid in provenance['commitments']}
    source_ids = {s['source_id'] for s in wanted.values()}
    papers = {}
    for event in events:
        if event['stage'] != 'run_started':
            continue
        literature = json.loads(event['payload_json']).get('literature')
        if isinstance(literature, str) and literature.startswith(HEADER):
            papers = {p['source_id']: p for p in json.loads(literature[len(HEADER):])['papers']
                      if p['source_id'] in source_ids}
            break
    retained = {sid: dict(pages={}, record=None, conflict=False) for sid in source_ids}
    for event in events:
        if event['stage'] != 'extract_paper' or event['label'] != 'MODEL':
            continue
        receipt = json.loads(event['payload_json'])
        sid = receipt.get('source_id')
        if sid not in papers or receipt.get('status') != 'accepted':
            continue
        try:
            inputs = json.loads(event['prompt'].rsplit('INPUT_JSON\n', 1)[1])
        except (ValueError, IndexError):
            continue  # Missing local evidence remains unresolved below.
        if (inputs.get('source_id') != sid or not papers[sid].get('pdf_sha256') or
                inputs.get('pdf_sha256') != papers[sid]['pdf_sha256']):
            continue
        local = retained[sid]
        record = inputs.get('record')
        if not isinstance(record, dict) or record.get('id') != sid:
            continue
        local['conflict'] |= local['record'] not in (None, record)
        local['record'] = record
        for page in inputs.get('pages', []):
            number, text = page.get('page'), page.get('text')
            if type(number) is not int or number < 1 or not isinstance(text, str):
                continue
            local['conflict'] |= number in local['pages'] and local['pages'][number] != text
            local['pages'][number] = text
    result = {}
    for tid, source in sorted(wanted.items()):
        commitment = frozen.get(tid)
        paper = papers.get(source['source_id'])
        local = retained[source['source_id']]
        pages = local['pages']
        entry = bibliography_entry(tid, commitment, source, local['record'])
        status, reason = 'unresolved', 'local_pages_or_metadata_unavailable'
        item = next((i for i in evidence_items(paper) if i['id'] == tid), None) if paper else None
        page_hash = digest(canonical(pages))
        page_grounding = assessment(item, {n: tokens(text) for n,text in pages.items()}) if item else None
        if item is not None:
            if (item['citation'] != commitment.citation or item['text'] != source['source_text'] or
                    any(item[k] != source[k] for k in ('source_id', 'page_start', 'page_end', 'attributed_to'))):
                status, reason = 'mismatch', 'frozen_source_mismatch'
            elif (not local['conflict'] and local['record'] and
                  all(local['record'].get(k) for k in ('authors', 'year', 'title')) and
                  page_hash == paper['grounding']['source_text_sha256'] and
                  not page_grounding['reasons'] and
                  all(pages.get(n, '').strip() for n in range(source['page_start'], source['page_end'] + 1))):
                status, reason = 'verified', 'frozen_item_and_page_evidence_match'
        result[tid] = dict(id=tid, bibliography=entry, legacy_citation=commitment.citation,
            status=status, reason=reason, source_id=source['source_id'],
            pdf_sha256=paper.get('pdf_sha256') if paper else None,
            page_text_sha256=page_hash, page_grounding=page_grounding,
            page_start=source['page_start'], page_end=source['page_end'],
            source_text=source['source_text'],
            pages=[dict(page=n, text=pages[n]) for n in range(source['page_start'], source['page_end'] + 1) if n in pages])
    return result


def local_verdicts(calls, draft, items):
    from ara.runtime.calls import require
    events = calls.log.read()
    frozen = frozen_from_events(events)
    entries = catalogue(events, {b['id'] for b in draft['bibliography']})
    result = {}
    for item in items:
        if item['kind'] != 'citation':
            continue
        if item['id'] not in entries:
            if frozen is not None and frozen.get(item['id']) is not None:
                calls.log.record('local_citation_verification', item_id=item['id'],
                                 status='unresolved', reason='frozen_provenance_unavailable')
                require(False, 'local citation evidence unresolved: ' + item['id'])
            continue
        entry = entries[item['id']]
        mismatch = entry['status'] != 'unresolved' and item['text'] not in (entry['bibliography']['text'], entry['legacy_citation'])
        status = 'mismatch' if mismatch else entry['status']
        reason = 'bibliography_mismatch' if mismatch else entry['reason']
        calls.log.record('local_citation_verification', item_id=item['id'], status=status, reason=reason, evidence=entry)
        require(status != 'unresolved', 'local citation evidence unresolved: ' + item['id'])
        result[item['id']] = dict(**item, status='verified' if status == 'verified' else 'unverified',
            action='retain' if status == 'verified' else 'remove', evidence_urls=[], detail=reason,
            verification_basis='local_frozen_T', local_evidence=entry,
            **({'removal_reason': reason} if status == 'mismatch' else {}))
    from ara.runtime.essay_audit import sentence_spans
    spans = [draft['body'][a:b] for a,b in sentence_spans(draft['body'])]
    for item in items:
        if item['kind'] != 'quotation':
            continue
        cited = {tid for text in spans if item['text'] in text for tid in CITATION.findall(text)}
        bound = [entries[tid] for tid in sorted(cited) if tid in entries and entries[tid]['status'] == 'verified']
        if not bound:
            continue
        quote = ' '.join(item['text'].split())
        exact = any(re.search(r'(?<!\w)' + re.escape(quote) + r'(?!\w)', ' '.join(p['text'].split()))
                    for entry in bound for p in entry['pages'])
        reason = 'exact_quotation_in_cited_pages' if exact else 'quotation_mismatch'
        result[item['id']] = dict(**item, status='verified' if exact else 'unverified',
            action='retain' if exact else 'remove', evidence_urls=[], detail=reason,
            verification_basis='local_frozen_T', local_evidence=bound,
            **({} if exact else {'removal_reason': reason}))
        calls.log.record('local_citation_verification', item_id=item['id'], status=result[item['id']]['status'],
                         reason=reason, evidence=bound)
    return result


def check_coverage(events, route, draft):
    frozen = frozen_from_events(events)
    if provenance_from_events(events, frozen) is None:
        return  # Legacy runs without source provenance cannot claim local verification.
    required = support_ids(route, frozen)
    entries = catalogue(events, required)
    cited = set(CITATION.findall(draft['body']))
    bibliography = {b['id']: b for b in draft['bibliography']}
    if not required <= cited or not required <= bibliography.keys() or not cited <= bibliography.keys():
        raise ValueError('citation coverage: missing route support or bibliography marker')
    if any(tid not in entries or entries[tid]['status'] != 'verified' or
           bibliography[tid] != entries[tid]['bibliography'] for tid in required):
        raise ValueError('citation coverage: route sources lack matching local evidence')
    return dict(required_ids=sorted(required), cited_ids=sorted(cited), bibliography_count=len(bibliography))


def restore_citations(calls, route, draft):
    """One citation-only pass; no prose edits and no reset of semantic repair rounds."""
    from ara.runtime.calls import require
    from ara.runtime.essay_audit import CITE, NODE, sentence_spans
    events = calls.log.read()
    entries = catalogue(events, support_ids(route, frozen_from_events(events)))
    if not entries:
        return draft
    allowed = {tid: e['bibliography'] for tid,e in entries.items()}
    bibliography = [allowed[b['id']] if b['id'] in entries and b['text'] == entries[b['id']]['legacy_citation']
                    else b for b in draft['bibliography']]
    candidate = {**draft, 'bibliography': bibliography}
    required = set(entries)
    present = set(CITATION.findall(candidate['body']))
    if required <= present and required <= {b['id'] for b in bibliography}:
        return candidate
    for tid, entry in entries.items():
        require(entry['status'] == 'verified', 'local citation evidence unresolved: ' + tid)
    spans = sentence_spans(draft['body'])
    originals = {i: draft['body'][a:b] for i,(a,b) in enumerate(spans, 1)}
    inputs = dict(mode='citations', audit_inputs=calls.audit_inputs(route,draft), flags=[],
        required_citation_ids=sorted(required), allowed_bibliography=list(allowed.values()),
        local_source_evidence=list(entries.values()), bibliography=bibliography,
        flagged_sentences=[dict(sentence=n,text=text,citation_markers=CITE.findall(text),node_markers=NODE.findall(text))
                           for n,text in originals.items()])
    def check(data):
        numbers = [r['sentence'] for r in data['revisions']]
        require(len(numbers) == len(set(numbers)) and set(numbers) <= originals.keys(), 'invalid citation restoration sentences')
        body = draft['body']
        for revision in sorted(data['revisions'],key=lambda r:r['sentence'],reverse=True):
            n,text = revision['sentence'],revision['text'];old=originals[n]
            require(' '.join(CITE.sub('', text).split()) == ' '.join(CITE.sub('', old).split()),
                    'citation restoration changed prose')
            existing, actual = CITATION.findall(old), CITATION.findall(text)
            require(actual[:len(existing)] == existing and set(actual[len(existing):]) <= allowed.keys(),
                    'citation restoration changed or invented a marker')
            # Reuse the original bytes; the response chooses citations, never prose or whitespace.
            replacement = old + ''.join('[cite:' + tid + ']' for tid in actual[len(existing):])
            a,b=spans[n-1];body=body[:a]+replacement+body[b:]
        used=set(CITATION.findall(body))
        bib={b['id']:b for b in bibliography}
        bib.update({tid:allowed[tid] for tid in used & allowed.keys()})
        restored={**draft,'body':body,'bibliography':[bib[k] for k in sorted(bib)]}
        check_coverage(events,route,restored)
        return calls.validate_essay(route,restored,minimum_words=0)
    restored=calls.call('revise_essay',inputs,check)
    calls.log.record('essay_citations_restored',route_id=route.id,before_sha256=digest(canonical(draft)),
                     required_ids=sorted(required),draft=restored,prose_preserved=True)
    return restored
