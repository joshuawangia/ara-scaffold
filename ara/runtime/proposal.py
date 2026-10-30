"""Logged paper proposals and local evidence; never engine premises or licenses."""
from __future__ import annotations

import json
import re
from pathlib import Path
from hashlib import sha256

from ara.runtime.cache import canonical, digest

LABELS = {
    'ara': 'ARA-proposed thesis; bridge principle argued, not mechanically derived',
    'eps2': 'eps2-proposed thesis (tested in ARA); bridge principle argued, not mechanically derived',
}
ROLES = ('proposed_principle', 'argument_for_proposal')


def from_events(events, route_id):
    records = [json.loads(e['payload_json']) for e in events if e['stage'] == 'essay_proposal_mode'
               and json.loads(e['payload_json'])['route_id'] == route_id]
    if not records:
        return None
    from ara.runtime.calls import require
    require(all(r == records[0] for r in records), 'proposal packet is immutable')
    return records[0]


def required_ids(events, route):
    proposal = from_events(events, route.id)
    return set(proposal['packet']['frozen_evidence_ids']) | set(proposal['local_evidence']) if proposal else set()


def local_catalogue(events, ids):
    from ara.runtime.calls import require
    found = {}
    for event in events:
        if event['stage'] != 'essay_proposal_mode':
            continue
        for tid, item in json.loads(event['payload_json'])['local_evidence'].items():
            if tid not in ids:
                continue
            require(item['page_text_sha256'] == digest(canonical(item['pages'])), 'proposal page evidence changed')
            require(tid not in found or found[tid] == item, 'conflicting proposal evidence')
            found[tid] = item
    return found


def activate(calls, route, packet=None):
    """Validate and retain one immutable packet before any writer or resumed draft."""
    from ara.runtime.calls import require
    from ara.runtime.citations import catalogue
    from ara.runtime.route_policy import frozen_from_events
    events = calls.log.read()
    prior = from_events(events, route.id)
    if packet is not None:
        calls.screen_imported_draft(packet)
        require(isinstance(packet, dict) and set(packet) == {
            'route_id', 'target_text', 'thesis_origin', 'dossier_mapping', 'missing_premise',
            'frozen_evidence_ids', 'local_sources', 'minimum_words'}, 'invalid proposal packet fields')
        require(route.status == 'OPEN' and packet['route_id'] == route.id, 'proposal requires matching OPEN route')
        target = next(n.proposition.text for n in route.nodes if n.id == route.root_id)
        require(packet['target_text'] == target, 'proposal target differs from route')
        require(packet['thesis_origin'] in LABELS, 'unknown proposal thesis origin')
        require(all(isinstance(packet[k], str) and packet[k].strip() for k in
                    ('dossier_mapping', 'missing_premise')), 'proposal needs dossier and missing premise')
        require(type(packet['minimum_words']) is int and 3000 <= packet['minimum_words'] <= 4500,
                'proposal minimum must be 3000–4500')
        require(len(canonical(packet)) <= 120000, 'proposal packet exceeds bound')
        if prior:
            require(prior['packet'] == packet, 'proposal packet is immutable; use an independent run')
        else:
            ids = packet['frozen_evidence_ids']
            require(isinstance(ids, list) and ids and all(isinstance(i,str) for i in ids)
                    and len(set(ids)) == len(ids), 'proposal needs unique frozen evidence ids')
            frozen = frozen_from_events(events)
            require(frozen is not None and all(frozen.get(i) is not None for i in ids), 'proposal evidence missing from frozen T')
            entries = catalogue(events, set(ids))
            require(entries and all(e['status'] == 'verified' for e in entries.values()), 'proposal frozen evidence lacks verified local pages')
            local = {}
            require(isinstance(packet['local_sources'], list), 'proposal local sources must be a list')
            for source in packet['local_sources']:
                item = _read_source(source)
                tid = item['id']
                require(tid not in local and frozen.get(tid) is None, 'proposal evidence id collision')
                local[tid] = item
            prior = dict(route_id=route.id, route_sha256=digest(route.to_json()), packet=packet,
                         disclosure=LABELS[packet['thesis_origin']], local_evidence=local,
                         authority='paper_owned_proposal_not_frozen_T_or_engine_license',
                         length_basis='orchestrator decision: route-proportional length; operator instruction: draft all candidates')
            calls.screen_imported_draft(prior)
            calls.log.record('essay_proposal_mode', **prior)
    if prior:
        require(prior['route_sha256'] == digest(route.to_json()), 'proposal route changed')
        calls.config['essay_min_words'] = prior['packet']['minimum_words']
        calls.config['essay_word_limit'] = min(6000, calls.config['essay_word_limit'])
    return prior


def _read_source(source):
    from ara.runtime.calls import require
    from pypdf import PdfReader
    from io import BytesIO
    require(set(source) == {'id', 'pdf_path', 'pdf_sha256', 'page_start', 'page_end', 'record', 'excerpt'},
            'invalid proposal local source fields')
    require(isinstance(source['id'], str) and re.fullmatch(r'proposal:[A-Za-z0-9_.:-]+', source['id']), 'invalid proposal evidence id')
    raw = Path(source['pdf_path']).read_bytes()
    require(sha256(raw).hexdigest() == source['pdf_sha256'], 'proposal PDF hash mismatch')
    reader = PdfReader(BytesIO(raw))
    start, end = source['page_start'], source['page_end']
    require(type(start) is int and type(end) is int and 1 <= start <= end <= len(reader.pages)
            and end-start < 6, 'proposal page range invalid')
    pages = [dict(page=n, text=reader.pages[n-1].extract_text() or '') for n in range(start,end+1)]
    require(all(p['text'].strip() for p in pages), 'proposal local page text unavailable')
    excerpt = source['excerpt']
    require(isinstance(excerpt,str) and len(excerpt.split()) >= 3 and
            ' '.join(excerpt.split()) in ' '.join(' '.join(p['text'] for p in pages).split()),
            'proposal excerpt absent from retained PDF pages')
    record = source['record']
    require(isinstance(record,dict) and all(record.get(k) for k in ('id','authors','year','title','venue')),
            'proposal source metadata incomplete')
    locator = str(start) if start == end else f'{start}-{end}'
    bibliography = dict(id=source['id'], text=f"{record['authors']} ({record['year']}). {record['title']}. {record['venue']}. PDF p. {locator}.",
                        url=record.get('open_access_url'))
    return dict(id=source['id'], bibliography=bibliography, legacy_citation=bibliography['text'],
                status='verified', reason='proposal_retained_pdf_pages', source_id=record['id'], record=record,
                pdf_sha256=source['pdf_sha256'], page_text_sha256=digest(canonical(pages)),
                page_start=start, page_end=end, source_text=excerpt, pages=pages,
                authority='related_literature_not_frozen_T')


def validate_disclosure(proposal, draft, *, allow_legacy=False):
    from ara.runtime.calls import require
    from ara.runtime.proposal_scopes import sections, misplaced_status
    if proposal is None:
        return
    label = proposal['disclosure']
    blocks = sections(draft['body'])
    by_name = {s['heading'].casefold(): draft['body'][s['content_start']:s['end']] for s in blocks}
    if allow_legacy and label in draft['title'] and all(label in by_name.get(h, '') for h in ('abstract','methodology')):
        return
    require(not any(value in draft['title'] for value in LABELS.values()), 'proposal title must be ordinary prose; disclosure belongs in abstract and Status and method')
    require(sum(s['heading'].casefold() == 'abstract' for s in blocks) == 1,
            'proposal needs one Abstract section')
    abstract = by_name.get('abstract', '')
    require(abstract.count(label) == 1 and 'Disclosure: ' + label + '.' in abstract,
            'proposal needs exactly one abstract disclosure')
    note = by_name.get('status and method', '')
    require(blocks and blocks[-1]['heading'].casefold() == 'status and method' and note.count(label) == 1,
            'proposal disclosure missing from final Status and method note')
    require(sum(s['heading'].casefold() == 'status and method' for s in blocks) == 1 and len(note.split()) <= 250,
            'proposal Status and method note must be unique and short')
    require(not misplaced_status(draft['body']), 'proposal search qualifications belong in Status and method')


def role_failure(role, text, proposal, *, frozen_hypothesis=None, source_authors=(), proposal_scope=None):
    """Caller binds frozen_hypothesis to a validated H node; never infer it from OPEN mode."""
    scoped = proposal is not None and proposal_scope is not None
    if scoped and (role == 'source_claim' or source_attribution(text, source_authors)):
        return 'source_attributed_proposal'
    if role not in ROLES:
        return None
    if frozen_hypothesis is not None:
        if (proposal is not None or proposal_scope is not None or role != 'proposed_principle' or
                frozen_hypothesis.get('kind') != 'hypothesis' or
                frozen_hypothesis.get('stance') != 'proposed' or
                frozen_hypothesis.get('source_id') is not None or
                not frozen_hypothesis.get('declaration') or not frozen_hypothesis.get('formula')):
            return 'invalid_frozen_hypothesis_authorization'
    elif proposal is None:
        return 'proposal_mode_required'
    prefix = r'(?:This paper|We) (?:proposes?|propose)' if role == 'proposed_principle' else r'(?:This paper|We) (?:argues?|argue|reasons?|reason|objects?|object|replies|reply)'
    if not scoped and not re.match(prefix+r'\b', text, re.I):
        return 'unmarked_proposal'
    # Source reports belong in their own cited sentence. The semantic auditor also
    # rejects indirect attribution and unargued substantive claims under these roles.
    remainder = re.sub(prefix+r'\b', '', text, count=1, flags=re.I)
    if source_attribution(remainder, source_authors):
        return 'source_attributed_proposal'
    return None


def source_attribution(text, source_authors):
    if re.search(r'\[(?:cite|lit):|\baccording to\b|\battributed to\b', text, re.I):
        return True
    return any(re.search(r'\b'+re.escape(author)+r'\s+(?:argues?|claims?|proposes?|establishes?|maintains?|writes?|endorses?|says?|holds?)\b', text, re.I)
               for author in source_authors)


def author_names(evidence):
    """Known source author names, not arbitrary nouns before the word 'claims'."""
    names = set()
    for key in ('supporting_commitments', 'alignment_source_evidence', 'proposal_source_evidence'):
        for item in evidence.get(key, []):
            source = item.get('provenance') or {}
            authors = source.get('source_authors', [])
            if isinstance(authors, str):
                authors = authors.split(';')
            for author in authors:
                if isinstance(author, str) and author.strip():
                    names.add(author.split(',')[0].strip() if ',' in author else author.split()[-1])
            attributed = source.get('attributed_to')
            if isinstance(attributed, str) and attributed.strip():
                names.add(attributed.strip())
    return tuple(sorted(names))


def insert_disclosure(proposal, draft):
    """Normalize exact metadata only; substantive qualifications require author editing."""
    if proposal is None:
        return draft
    from ara.runtime.proposal_scopes import sections
    label = proposal['disclosure']
    sentence = 'Disclosure: ' + label + '.'
    title = draft['title'].replace(label, '').strip(' \t\n—-:."“”')
    body = draft['body']
    blocks = sections(body)
    edits, note = [], None
    for block in blocks:
        heading = block['heading'].casefold()
        if heading not in ('abstract', 'methodology', 'status and method'):
            continue
        content = body[block['content_start']:block['end']]
        content = re.sub(r'(?:Disclosure:[ \t]*)?["“]?' + re.escape(label) + r'["”]?[.]?', '', content)
        content = content.replace('Disclosure: .', '').strip()
        replacement = sentence + (' ' + content if content else '')
        if heading == 'abstract':
            edits.append((block['start'], block['end'], 'Abstract\n\n'+replacement+'\n\n'))
        else:
            note = replacement if note is None else note + '\n\n' + content
            edits.append((block['start'], block['end'], ''))
    for start,end,text in reversed(edits):
        body = body[:start] + text + body[end:]
    if not any(b['heading'].casefold() == 'abstract' for b in blocks):
        body = 'Abstract\n\n' + sentence + '\n\n' + body
    body = body.rstrip() + '\n\nStatus and method\n\n' + (note or sentence)
    return {**draft, 'title': title, 'body': body}


def retain_disclosure(calls, route, draft, *, phase):
    proposal = from_events(calls.log.read(), route.id)
    result = insert_disclosure(proposal, draft)
    if result != draft:
        calls.log.record('essay_proposal_disclosure_inserted', route_id=route.id, phase=phase,
                         disclosure=proposal['disclosure'], before_sha256=digest(canonical(draft)),
                         after_sha256=digest(canonical(result)), draft=result,
                         semantic_repair_rounds_unchanged=True)
    return result
