"""Page-preserving intake and log-backed runtime literature artifacts."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
from typing import TYPE_CHECKING, Literal

from pypdf import PdfReader
import yaml

from ara.runtime.cache import canonical, digest
from ara.runtime.logging import EventLog, read_log
from ara.types import RunEvent

if TYPE_CHECKING:
    from ara.runtime.calls import ModelCalls

HEADER = '# ARA extracted literature v1\n'


@dataclass(frozen=True)
class PageText:
    page: int
    text: str


@dataclass(frozen=True)
class Paper:
    source_id: str
    record_json: str
    pdf_sha256: str | None
    pages: tuple[PageText, ...]
    unavailable: str | None = None

    def inputs(self) -> dict:
        return {'source_id': self.source_id, 'record': json.loads(self.record_json),
                'pdf_sha256': self.pdf_sha256, 'pages': [asdict(p) for p in self.pages]}


@dataclass(frozen=True)
class ExtractedItem:
    source_id: str
    kind: Literal['claim', 'argument']
    attribution: Literal['author_claim', 'reported_view', 'attacked_view']
    text: str
    page_start: int
    page_end: int

    @property
    def citation(self) -> str:
        end = f'-{self.page_end}' if self.page_end != self.page_start else ''
        return f'{self.source_id}:pdf:{self.page_start}{end}'


@dataclass(frozen=True)
class PaperExtraction:
    source_id: str
    items: tuple[ExtractedItem, ...]

    def to_dict(self) -> dict:
        return {'source_id': self.source_id,
                'items': [{**asdict(item), 'citation': item.citation} for item in self.items]}


def load_papers(manifest: Path, fulltext_dir: Path, selected: tuple[str, ...] = ()) -> tuple[Paper, ...]:
    records = yaml.safe_load(manifest.read_text())
    if not isinstance(records, list) or not records:
        raise ValueError('manifest must be a nonempty list')
    ids = []
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get('id'), str) or not re.fullmatch(r'[A-Za-z0-9_-]+', record['id']):
            raise ValueError('manifest requires safe, nonempty source ids')
        if record.get('fulltext') != f'fulltext/{record["id"]}.pdf':
            raise ValueError('manifest fulltext must be fulltext/<id>.pdf')
        ids.append(record['id'])
    if len(set(ids)) != len(ids) or not set(selected) <= set(ids):
        raise ValueError('duplicate or unknown source id')
    papers = []
    for record in records:
        if selected and record['id'] not in selected:
            continue
        path = fulltext_dir / f'{record["id"]}.pdf'
        checksum = None
        try:
            raw = path.read_bytes()
            checksum = sha256(raw).hexdigest()
            reader = PdfReader(BytesIO(raw), strict=True)
            if reader.is_encrypted:
                raise ValueError('encrypted PDF')
            pages = tuple(PageText(i, page.extract_text() or '') for i, page in enumerate(reader.pages, 1))
            # No OCR: a missing text layer on even one page cannot be silently omitted.
            if not pages or any(not page.text.strip() for page in pages):
                raise ValueError('empty page text')
            papers.append(Paper(record['id'], canonical(record), checksum, pages))
        except FileNotFoundError:
            papers.append(Paper(record['id'], canonical(record), checksum, (), 'missing_pdf'))
        except Exception as exc:
            # Parser messages can include source content. Keep the class, not an untrusted message.
            papers.append(Paper(record['id'], canonical(record), checksum, (), f'unreadable_pdf:{type(exc).__name__}'))
    return tuple(papers)


def assemble(outcomes: list[dict]) -> str:
    return HEADER + canonical({
        'origin': 'SYSTEM/MODEL', 'locator_convention': 'one-based physical PDF pages, not printed folios',
        'use': 'Use extracted items only. Record-only entries supply no claims. Preserve attribution; '
               'reported or attacked views are not author endorsements. Copy citation identifiers verbatim.',
        'papers': outcomes}) + '\n'


def extract(calls: ModelCalls, papers: tuple[Paper, ...], *, missing: str = 'record-only',
            estimate_only: bool = False) -> Path | None:
    from ara.types import TokenUsage

    maximum = calls.config['extract_paper_max_output_tokens']
    per_page = calls.config['extraction_estimated_tokens_per_page']
    if type(per_page) is not int or per_page <= 0 or type(maximum) is not int or maximum <= 0:
        raise ValueError('extraction token estimates and output allowance must be positive integers')
    pages = sum(len(p.pages) for p in papers)
    readable = sum(p.unavailable is None for p in papers)
    overhead = len(calls.render('extract_paper', {})[1].encode())
    usage = TokenUsage(input_tokens=pages * per_page + readable * overhead, output_tokens=readable * maximum)
    estimate = {'papers': len(papers), 'readable_papers': readable, 'pages': pages,
                'tokens_per_page': per_page, 'input_tokens': usage.input_tokens,
                'output_token_allowance': usage.output_tokens, 'estimated_usd': float(calls.budget.cost(usage)),
                'extraction_cap_usd': calls.config['extraction_cost_cap_usd'],
                'run_cap_usd': calls.config['cost_cap_usd'],
                'note': 'Planning estimate: pages times tokens/page plus prompt overhead and full output allowance; '
                        'excludes retries/fallbacks. Admission counts each actual request separately.'}
    calls.log.record('extraction_estimate', **estimate)
    print('Extraction estimate before dispatch: ' + canonical(estimate), flush=True)
    outcomes = []
    for paper in papers:
        reason = paper.unavailable
        # UTF-8 bytes conservatively bound text tokens, including JSON escaping and schema.
        prompt = calls.render('extract_paper', paper.inputs())[1]
        schema = (calls.root / 'schemas/extract_paper.json').read_text()
        if reason is None and len((prompt + schema).encode()) + maximum > calls.config['model_context_token_bound']:
            reason = 'context_bound: conservative UTF-8 byte bound exceeds model context; no truncation'
        if estimate_only:
            calls.log.record('extraction_preflight', source_id=paper.source_id, pages=len(paper.pages), reason=reason)
            continue
        base = {'source_id': paper.source_id, 'record': json.loads(paper.record_json),
                'pdf_sha256': paper.pdf_sha256, 'pages': len(paper.pages)}
        if reason:
            outcome = {**base, 'status': 'record only, not extracted', 'reason': reason, 'items': []}
            calls.log.record('extraction_outcome', **outcome)
            outcomes.append(outcome)
            print(f'{paper.source_id}: record only, not extracted ({reason})', flush=True)
            if missing == 'refuse':
                raise ValueError(f'{paper.source_id}: extraction refused: {reason}')
            continue
        calls.log.record('extraction_paper_started', **base)
        try:
            result = calls.extract_paper(paper)
        except Exception as exc:
            calls.log.record('extraction_outcome', **base, status='failed', reason=type(exc).__name__, items=[])
            raise  # Validation, provider and budget failures are never bibliographic success.
        outcome = {**base, 'status': 'extracted', **result.to_dict()}
        calls.log.record('extraction_outcome', **outcome)
        outcomes.append(outcome)
        (calls.log.path.parent / f'{paper.source_id}.extraction.json').write_text(canonical(outcome))
    if estimate_only:
        return None
    literature = assemble(outcomes)
    path = calls.log.path.parent / 'literature.extracted.txt'
    calls.log.record('extraction_completed', literature_sha256=digest(literature), papers=len(outcomes))
    # Pin the completed prefix. Later timing/export events may append without invalidating it.
    records = read_log(calls.log.path)
    path.with_suffix('.provenance.json').write_text(canonical({
        'source_log': str(calls.log.path.resolve()), 'records': len(records), 'last_hash': records[-1]['hash']}))
    path.write_text(literature)
    return path


def literature_provenance(path: Path, text: str) -> tuple[dict, ...]:
    """Validate the generated artifact against its pinned source-log prefix."""
    if not text.startswith(HEADER):
        return ()
    provenance = json.loads(path.with_suffix('.provenance.json').read_text())
    records = read_log(Path(provenance['source_log']))
    count = provenance['records']
    if type(count) is not int or count <= 0 or len(records) < count or records[count - 1]['hash'] != provenance['last_hash']:
        raise ValueError('extraction provenance checkpoint mismatch')
    events = tuple(row['event'] for row in records[:count])
    complete = json.loads(events[-1]['payload_json'])
    outcomes = [json.loads(e['payload_json']) for e in events if e['stage'] == 'extraction_outcome']
    if events[-1]['stage'] != 'extraction_completed' or complete['literature_sha256'] != digest(text) or assemble(outcomes) != text:
        raise ValueError('extracted literature does not match logged output')
    return events


def import_provenance(log: EventLog, events: tuple[dict, ...]) -> None:
    log.record('extraction_provenance_import', records=len(events),
               note='Original event labels, timestamps and charges retained; upstream costs count in this run budget. '
                    'These are reused receipts, not new provider dispatches.')
    for event in events:
        log.emit(RunEvent.from_dict(event))


def citation_ids(literature: str) -> set[str] | None:
    if not literature.startswith(HEADER):
        return None
    data = json.loads(literature[len(HEADER):])
    return {item['citation'] for paper in data['papers'] if paper['status'] == 'extracted' for item in paper['items']}
