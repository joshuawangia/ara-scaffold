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
# Bound the representation actually embedded in build-T INPUT_JSON, including escaping.
ENTRY_BYTES = 2200


@dataclass(frozen=True)
class PageDiagnostic:
    page: int
    reason: str
    text_chars: int


class MissingExtractionLineage(ValueError):
    pass


def missing_lineage(events: tuple[dict, ...] | list[dict]) -> list[str]:
    origins: set[str] = set()
    missing: set[str] = set()
    for event in events:
        if event['stage'] != 'extract_paper' or event['label'] != 'MODEL':
            continue
        payload = json.loads(event['payload_json'])
        if payload['status'] != 'accepted':
            continue
        key = payload['cache_key']
        if payload['cache_hit'] and key not in origins:
            missing.add(key)
        elif not payload['cache_hit']:
            origins.add(key)
    return sorted(missing)



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
    diagnostics: tuple[PageDiagnostic, ...] = ()

    @property
    def affected_pages(self) -> tuple[int, ...]:
        return tuple(d.page for d in self.diagnostics if d.reason != 'blank_page')

    @property
    def readable_pages(self) -> tuple[PageText, ...]:
        return tuple(p for p in self.pages if p.text.strip() and p.page not in self.affected_pages)

    def inputs(self) -> dict:
        return {'source_id': self.source_id, 'record': json.loads(self.record_json),
                'pdf_sha256': self.pdf_sha256, 'pages': [asdict(p) for p in self.readable_pages],
                'page_diagnostics': [asdict(d) for d in self.diagnostics]}


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
        if not isinstance(record, dict) or not isinstance(record.get('id'), str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', record['id']):
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
                papers.append(Paper(record['id'], canonical(record), checksum, (), 'encrypted_pdf'))
                continue
            pages = []
            diagnostics = []
            for i, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ''
                chars = len(''.join(text.split()))
                contents = page.get_contents()
                operations = contents.operations if contents is not None else []
                # Do includes images and form XObjects; flag sparse forms conservatively too.
                image_or_form = any(op in (b'Do', b'INLINE IMAGE') for _, op in operations)
                painted = image_or_form or any(op in (b'S', b's', b'f', b'F', b'f*', b'B', b'B*', b'b', b'b*', b'sh')
                                               for _, op in operations)
                reason = None
                if image_or_form and chars < 200:
                    reason = 'sparse_image_text'
                elif not chars:
                    reason = 'nontext_visual_content' if painted else 'blank_page'
                if reason:
                    diagnostics.append(PageDiagnostic(i, reason, chars))
                pages.append(PageText(i, text))
            unavailable = 'empty_pdf' if not pages else None
            paper = Paper(record['id'], canonical(record), checksum, tuple(pages), unavailable, tuple(diagnostics))
            if not paper.readable_pages and not paper.affected_pages and pages:
                paper = Paper(record['id'], canonical(record), checksum, tuple(pages), 'no_readable_text', tuple(diagnostics))
            papers.append(paper)
        except FileNotFoundError:
            papers.append(Paper(record['id'], canonical(record), checksum, (), 'missing_pdf'))
        except Exception as exc:
            # Parser messages can include source content. Keep the class, not an untrusted message.
            papers.append(Paper(record['id'], canonical(record), checksum, (), f'unreadable_pdf:{type(exc).__name__}'))
    return tuple(papers)


def literature_entry(outcome: dict) -> dict:
    # Full bibliography, PDF hashes and page diagnostics remain in per-paper artifacts/logs.
    # Only material needed for build-T enters its bounded context.
    entry = {key: outcome[key] for key in ('source_id', 'status', 'items')}
    if outcome.get('reason'):
        entry['reason'] = outcome['reason']
    if outcome.get('affected_pages'):
        entry['coverage'] = 'partial: unread visual pages excluded; see extraction log for page diagnostics'
    return entry


def entry_size(entry: dict) -> int:
    return len(canonical(canonical(entry)).encode())


def assemble(outcomes: list[dict]) -> str:
    entries = [literature_entry(outcome) for outcome in outcomes]
    if any(entry_size(entry) > ENTRY_BYTES for entry in entries):
        raise ValueError('extracted literature entry exceeds serialized budget')
    return HEADER + canonical({
        'origin': 'SYSTEM/MODEL', 'locator_convention': 'one-based physical PDF pages, not printed folios',
        'use': 'Use extracted items only. Record-only entries supply no claims. Partial entries cover only '
               'readable pages. Preserve attribution; reported or attacked views are not author endorsements. '
               'Copy citation identifiers verbatim. This is a bounded selection of central material, not exhaustive extraction.',
        'papers': entries}) + '\n'


def extract(calls: ModelCalls, papers: tuple[Paper, ...], *, missing: str = 'record-only',
            estimate_only: bool = False) -> Path | None:
    from ara.types import TokenUsage

    maximum = calls.config['extract_paper_max_output_tokens']
    per_page = calls.config['extraction_estimated_tokens_per_page']
    if type(per_page) is not int or per_page <= 0 or type(maximum) is not int or maximum <= 0:
        raise ValueError('extraction token estimates and output allowance must be positive integers')
    pages = sum(len(p.pages) for p in papers)
    readable = sum(bool(p.readable_pages) and p.unavailable is None for p in papers)
    overhead = len(calls.render('extract_paper', {})[1].encode())
    usage = TokenUsage(input_tokens=pages * per_page + readable * overhead, output_tokens=readable * maximum)
    estimate = {'papers': len(papers), 'readable_papers': readable, 'pages': pages,
                'tokens_per_page': per_page, 'input_tokens': usage.input_tokens,
                'output_token_allowance': usage.output_tokens, 'estimated_usd': float(calls.budget.cost(usage)),
                'extraction_cap_usd': calls.config['extraction_cost_cap_usd'],
                'run_cap_usd': calls.config['cost_cap_usd'],
                'note': 'Planning estimate: pages times tokens/page plus prompt overhead and full output allowance; '
                        'excludes retries/fallbacks. Admission counts each actual request separately.'}
    estimate['run_token_cap'] = calls.config['token_cap']
    estimate['planned_batch_exceeds_enclosing_caps'] = (
        usage.input_tokens + usage.output_tokens + calls.budget.used_tokens > calls.config['token_cap'] or
        calls.budget.cost(usage) + calls.budget.used_cost > calls.config['cost_cap_usd'])
    calls.log.record('extraction_estimate', **estimate)
    print('Extraction estimate before dispatch: ' + canonical(estimate), flush=True)
    if estimate['planned_batch_exceeds_enclosing_caps']:
        print('planned batch exceeds enclosing caps', flush=True)
    outcomes = []
    for paper in papers:
        reason = paper.unavailable
        prompt_bytes = len(calls.render('extract_paper', paper.inputs())[1].encode())
        calls.log.record('extraction_text_coverage', source_id=paper.source_id,
                         diagnostics=[asdict(d) for d in paper.diagnostics],
                         affected_pages=list(paper.affected_pages), readable_pages=[p.page for p in paper.readable_pages])
        if prompt_bytes + maximum > calls.config['model_context_token_bound']:
            calls.log.record('extraction_size_warning', source_id=paper.source_id, prompt_bytes=prompt_bytes,
                             note='Bytes are a planning warning only; provider-counted tokens decide admission.')
        if estimate_only:
            calls.log.record('extraction_preflight', source_id=paper.source_id, pages=len(paper.pages), reason=reason)
            continue
        base = {'source_id': paper.source_id, 'record': json.loads(paper.record_json),
                'pdf_sha256': paper.pdf_sha256, 'pages': len(paper.pages),
                'page_diagnostics': [asdict(d) for d in paper.diagnostics],
                'affected_pages': list(paper.affected_pages)}
        if reason:
            outcome = {**base, 'status': 'record only, not extracted', 'reason': reason, 'items': []}
            calls.log.record('extraction_outcome', **outcome)
            outcomes.append(outcome)
            print(f'{paper.source_id}: record only, not extracted ({reason})', flush=True)
            if missing == 'refuse':
                raise ValueError(f'{paper.source_id}: extraction refused: {reason}')
            continue
        if not paper.readable_pages and paper.affected_pages:
            outcome = {**base, 'status': 'partial', 'reason': 'no_readable_pages', 'items': []}
            calls.log.record('extraction_outcome', **outcome)
            outcomes.append(outcome)
            continue
        calls.log.record('extraction_paper_started', **base)
        try:
            result = calls.extract_paper(paper)
        except Exception as exc:
            calls.log.record('extraction_outcome', **base, status='failed', reason=type(exc).__name__, items=[])
            raise  # Validation, provider and budget failures are never bibliographic success.
        outcome = {**base, 'status': 'partial' if paper.affected_pages else 'extracted', **result.to_dict()}
        calls.log.record('extraction_outcome', **outcome)
        outcomes.append(outcome)
        (calls.log.path.parent / f'{paper.source_id}.extraction.json').write_text(canonical(outcome))
    if estimate_only:
        return None
    lineage_missing = missing_lineage(calls.log.read())
    if lineage_missing:
        calls.log.record('extraction_lineage_missing', cache_keys=lineage_missing,
                         reason='cross-run extraction cache replay lacks origin receipt; import original extraction artifact')
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
    if missing_lineage(events):
        raise MissingExtractionLineage('cross-run extraction cache replay lacks origin receipt; import original extraction artifact')
    return events


def import_provenance(log: EventLog, events: tuple[dict, ...]) -> None:
    receipt_id = digest(canonical(events))
    if any(e['stage'] == 'extraction_provenance_import' and
           json.loads(e['payload_json']).get('receipt_id') == receipt_id for e in log.read()):
        return
    log.record('extraction_provenance_import', records=len(events), receipt_id=receipt_id,
               note='Original event labels, timestamps and charges retained; upstream costs count in this run budget. '
                    'These are reused receipts, not new provider dispatches.')
    for event in events:
        log.emit(RunEvent.from_dict(event))


def citation_ids(literature: str) -> set[str] | None:
    if not literature.startswith(HEADER):
        return None
    data = json.loads(literature[len(HEADER):])
    return {item['citation'] for paper in data['papers'] if paper['status'] in ('extracted', 'partial') for item in paper['items']}
