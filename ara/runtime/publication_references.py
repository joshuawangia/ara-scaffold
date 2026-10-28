"""Reference metadata joined through frozen T source IDs and logged PDF hashes."""
import json

from ara.runtime.cache import digest
from ara.runtime.calls import require
from ara.runtime.extraction import HEADER


def bibliography_records(log, evidence):
    wanted = {s['provenance']['source_id'] for s in evidence['supporting_commitments'] if s['provenance']}
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
    return found


def render_references(draft, evidence, records):
    sources = {s['commitment']['id']:s['provenance']['source_id'] for s in evidence['supporting_commitments'] if s['provenance']}
    groups = {}
    for item in draft['bibliography']:
        source = sources.get(item['id'],item['id'])
        groups.setdefault(source,[]).append(item)
    paragraphs = []
    for source,items in groups.items():
        if source in records:
            record = records[source]['record']
            year = f" ({record['year']})" if record.get('year') is not None else ''
            pages = f" pp. {record['pages']}." if record.get('pages') else ''
            paragraphs.append(f"{record['authors']}{year}. {record['title']}. {record['venue']}.{pages}")
        paragraphs.extend(f'[{item["id"]}] {item["text"]}' for item in items)
    return '\n\n## References\n\n' + '\n\n'.join(paragraphs) + '\n'
