"""Reference metadata joined through frozen T source IDs and logged PDF hashes."""
import json

from ara.runtime.cache import digest
from ara.runtime.calls import require
from ara.runtime.extraction import HEADER


def bibliography_records(log, evidence, source_ids=()):
    sources = evidence['supporting_commitments'] + evidence.get('alignment_source_evidence', []) + evidence.get('proposal_source_evidence', [])
    wanted = {s['provenance']['source_id'] for s in sources
              if s['provenance'] and s['provenance']['source_id'] is not None}
    wanted.update(source_ids)
    events = log.read()
    starts = [json.loads(e['payload_json']) for e in events if e['stage']=='run_started']
    literature = starts[0].get('literature', '') if starts else ''
    papers = json.loads(literature[len(HEADER):])['papers'] if literature.startswith(HEADER) else []
    hashes = {p['source_id']: p.get('pdf_sha256') for p in papers if p['source_id'] in wanted}
    found = {}
    for event in events:
        if event['stage'] != 'extract_paper' or '\nINPUT_JSON\n' not in (event['prompt'] or ''):
            continue
        data = json.loads(event['prompt'].split('\nINPUT_JSON\n',1)[1])
        source = data.get('source_id')
        if source not in wanted or not hashes.get(source) or data.get('pdf_sha256') != hashes[source]:
            continue
        record = data.get('record')
        if not isinstance(record,dict) or record.get('id') != source:
            continue
        fields = {k:record[k] for k in ('id','authors','year','title','venue','pages') if k in record}
        if not all(isinstance(fields.get(k),str) and fields[k].strip() for k in ('authors','title','venue')):
            continue
        require(source not in found or found[source]['record']==fields, 'conflicting bibliography metadata for source PDF')
        if source not in found:
            found[source] = dict(record=fields,pdf_sha256=hashes[source],
                origin_prompt_sha256=digest(event['prompt']),verification='not_independently_verified')
    for source in evidence.get('proposal_source_evidence', []):
        item = source.get('local_evidence')
        if item:
            found[item['source_id']] = dict(record=item['record'], pdf_sha256=item['pdf_sha256'], verification='retained_proposal_pdf_metadata')
    return found



def author_year(record):
    authors = record.get('authors', [])
    authors = authors.split(';') if isinstance(authors,str) else authors
    names = [name.strip().split(',')[0] if ',' in name else name.strip().split()[-1] for name in authors if name.strip()]
    label = (', '.join(names[:-1]) + ' & ' + names[-1]) if len(names)>1 else names[0] if names else 'Source metadata unavailable'
    return label + (' ' + str(record['year']) if record.get('year') else '')


def reading_copy(markdown, evidence, records, currency):
    import re
    from ara.runtime.publication_currency import LIT
    sources = evidence['supporting_commitments'] + evidence.get('alignment_source_evidence', []) + evidence.get('proposal_source_evidence', [])
    supports = {s['commitment']['id']:s for s in sources
                if not s['provenance'] or s['provenance'].get('stance') != 'model_alignment'}
    receipt = {}
    def source_citation(match):
        id = match[1]
        require(id in supports, 'reading citation lacks T provenance')
        support = supports[id]; p = support['provenance']
        require(p is not None, 'reading citation lacks page provenance')
        metadata = records.get(p['source_id'], {})
        start,end = p['page_start'],p['page_end']
        locator = 'PDF p. '+str(start) if start==end else f'PDF pp. {start}–{end}'
        label = author_year(metadata.get('record', {})) + ', ' + locator
        receipt[id] = dict(source_id=p['source_id'],display=label,locator=locator,
            raw_citation=support['commitment']['citation'],pdf_sha256=metadata.get('pdf_sha256'),
            bibliography=metadata.get('record',{}),basis='proposal literature physical PDF pages' if id.startswith('proposal:') else 'frozen T physical PDF pages')
        return '('+label+')'
    def literature_citation(match):
        id=match[1]
        require(currency is not None and id in currency['evidence'], 'reading literature citation lacks evidence')
        item=currency['evidence'][id];work=item['work']
        record=records.get(work,{}).get('record',{}) if work else {}
        label=author_year(record) if work else 'Literature-currency search 2026'
        display=label+', '+item['location']
        receipt['lit:'+id]=dict(source_id=work,display=display,locator=item['location'],
            raw_citation='[lit:'+id+']',bibliography=record,basis='logged literature-currency record',
            evidence=item,record_hashes=currency['records'])
        return '('+display+')'
    markdown=re.sub(r'\[\[node:[^\]]+\]\]', '', markdown)
    text=re.sub(r'\[cite:([^\]]+)\]',source_citation,markdown)
    text=LIT.sub(literature_citation,text)
    labels=sorted({r['display'] for r in receipt.values()})
    for label in labels:
        if len({r['source_id'] for r in receipt.values() if r['display']==label}) != 1:
            continue
        escaped=re.escape(label)
        text=re.sub(r'\('+escaped+r'\)(?:[ \t]+\('+escaped+r'\))+',lambda _: '('+label+')',text)
    if labels:
        citation=r'\((?:'+'|'.join(map(re.escape,labels))+r')\)'
        text=re.sub(r'([.!?])[ \t]+('+citation+r'(?:[ \t]+'+citation+r')*)',
                    lambda m: ' '+m[2]+m[1],text)
    return text,receipt


def render_references(draft, evidence, records, currency=None, receipt=None):
    if receipt is None:
        _,receipt=reading_copy(draft['body'],evidence,records,currency)
    sources={r['source_id'] for r in receipt.values() if r['source_id']}
    entries=[]
    for source in sorted(sources):
        record=records.get(source,{}).get('record',{})
        if record:
            authors=record.get('authors','Source metadata unavailable')
            if isinstance(authors,list):authors='; '.join(authors)
            year=f" ({record['year']})" if record.get('year') else ''
            venue=f". {record['venue']}" if record.get('venue') else ''
            pages=f". pp. {record['pages']}" if record.get('pages') else ''
            doi=f". {record['doi']}" if record.get('doi') else ''
            entries.append(f"{authors}{year}. {record.get('title','Title unavailable')}{venue}{pages}{doi}.")
        else:
            locators=sorted({r['locator'] for r in receipt.values() if r['source_id']==source})
            entries.append('Source bibliographic metadata unavailable. '+ '; '.join(locators)+'.')
    if currency and any(id.startswith('lit:') for id in receipt):
        entries.append('Literature-currency record (2026). Bounded 2018–2026 search; verified page/section references and access limits retained in the accompanying publication receipt.')
    return '\n\n## References\n\n'+'\n\n'.join(entries)+'\n'
