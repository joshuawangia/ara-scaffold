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
from ara.runtime.provenance import (checkpoint, read_checkpoint, import_receipts,
                                    extraction_outcomes)

if TYPE_CHECKING:
    from ara.runtime.calls import ModelCalls

HEADER = '# ARA extracted literature v2\n'
EXTRACTION_VERSION = 2


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
    def unread_pages(self) -> tuple[int, ...]:
        return tuple(d.page for d in self.diagnostics if d.reason not in ('blank_page', 'private_use_glyphs'))

    @property
    def readable_pages(self) -> tuple[PageText, ...]:
        return tuple(p for p in self.pages if p.text.strip() and p.page not in self.unread_pages)

    def inputs(self) -> dict:
        return {'source_id': self.source_id, 'record': json.loads(self.record_json),
                'pdf_sha256': self.pdf_sha256, 'pages': [asdict(p) for p in self.readable_pages],
                'page_diagnostics': [asdict(d) for d in self.diagnostics]}


@dataclass(frozen=True)
class ExtractedItem:
    id: str
    source_id: str
    kind: Literal['premise', 'inference', 'intermediate_conclusion', 'conclusion',
                  'distinction', 'qualification', 'reported_view', 'attacked_view']
    attribution: Literal['author_claim', 'reported_view', 'attacked_view']
    attributed_to: str
    text: str
    page_start: int
    page_end: int
    premise_ids: tuple[str, ...]
    conclusion_id: str | None
    qualification_ids: tuple[str, ...]
    applies_to: tuple[str, ...]
    inference_origin: Literal['paper_stated'] | None

    def __post_init__(self):
        for key in ('premise_ids', 'qualification_ids', 'applies_to'):
            object.__setattr__(self, key, tuple(getattr(self, key)))

    @property
    def citation(self) -> str:
        end = f'-{self.page_end}' if self.page_end != self.page_start else ''
        return f'{self.source_id}:pdf:{self.page_start}{end}#{self.id}'


@dataclass(frozen=True)
class PaperExtraction:
    source_id: str
    items: tuple[ExtractedItem, ...]
    schema_version: int = EXTRACTION_VERSION
    obligations_json: str = '[]'
    resolutions_json: str = '[]'
    dispositions_json: str = '[]'

    def to_dict(self) -> dict:
        return {'schema_version': self.schema_version, 'source_id': self.source_id,
                'dispositions': json.loads(self.dispositions_json),
                'obligations': json.loads(self.obligations_json), 'resolutions': json.loads(self.resolutions_json),
                'items': [{**asdict(item), 'citation': item.citation} for item in self.items]}


def record_new_obligations(log, source_id, window, turn, pages, gaps):
    """Assign identities without comparing descriptions; retain discoveries on refusal."""
    obligations = [dict(id=f'{source_id}:{window}:turn:{turn}:gap:{index}',
                        source_id=source_id, range=window, turn=turn,
                        pages=list(pages), description=gap['description'])
                   for index, gap in enumerate(gaps)]
    for obligation in obligations:
        log.record('extraction_obligation_discovered', source_id=source_id, obligation=obligation)
    return obligations


def save_immutable(path: Path, value: str) -> None:
    if path.exists():
        if path.read_text() != value:
            raise ValueError(f'immutable artifact already exists: {path.name}')
    else:
        path.write_text(value)


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
                if any(0xE000 <= ord(c) <= 0xF8FF or 0xF0000 <= ord(c) <= 0xFFFFD or
                       0x100000 <= ord(c) <= 0x10FFFD for c in text):
                    diagnostics.append(PageDiagnostic(i, 'private_use_glyphs', chars))
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
    entry = {key: outcome[key] for key in ('source_id', 'status', 'items')}
    entry['schema_version'] = EXTRACTION_VERSION
    entry['pdf_sha256'] = outcome.get('pdf_sha256')
    if outcome.get('reason'):
        entry['reason'] = outcome['reason']
    if outcome['status'] == 'failed':
        if outcome['items']:
            raise ValueError('failed paper cannot supply evidence')
        entry['failure_receipt'] = outcome['failure_receipt']
        entry['failure_detail'] = outcome['failure_detail']
    if outcome.get('affected_pages'):
        entry['coverage'] = 'partial: unread visual pages excluded; retained encoding warnings require source inspection; see diagnostics'
    return entry


def assemble(outcomes: list[dict]) -> str:
    entries = [literature_entry(outcome) for outcome in outcomes]
    return HEADER + canonical({
        'origin': 'SYSTEM/MODEL', 'locator_convention': 'one-based physical PDF pages, not printed folios',
        'use': 'Use extracted items only. Record-only entries supply no claims. Partial entries cover only '
               'readable pages. Preserve attribution; reported or attacked views are not author endorsements. '
               'Copy evidence identifiers and citations verbatim. Inferences describe paper-stated links, not engine licenses.',
        **({'status': 'complete_with_disclosed_failures'} if any(e['status'] == 'failed' for e in entries) else {}),
        'papers': entries}) + '\n'


def extraction_range_plan(calls: ModelCalls, paper: Paper):
    """Count initial ranges exactly as execution does; output density is an explicit scenario."""
    from ara.runtime.windows import counted_windows
    maximum = calls.config['extract_paper_max_output_tokens']
    bound = calls.config['model_context_token_bound'] - maximum
    density = calls.config.get('extraction_planned_output_tokens_per_page', 0)
    if type(density) is not int or density < 0:
        raise ValueError('extraction planned output density must be a nonnegative integer')
    counts = {}
    def measure(pages):
        inputs = {**paper.inputs(), 'pages': [asdict(p) for p in pages]}
        usage = calls.count_request('extract_paper', inputs)
        counts[tuple(p.page for p in pages)] = usage
        if density * len(pages) > maximum:
            return bound + 1
        return usage.input_tokens
    windows = counted_windows(paper.readable_pages, measure, bound, lambda: calls.budget.stop(
        'extract_paper context bound or output planning bound: single page cannot fit; no truncation', 'extract_paper', scope='paper'))
    return [(pages, counts[tuple(p.page for p in pages)]) for pages in windows]


def extract(calls: ModelCalls, papers: tuple[Paper, ...], *, missing: str = 'record-only',
            estimate_only: bool = False, reused: dict | None = None) -> Path | None:
    from ara.types import TokenUsage
    from ara.runtime.calls import Rejected
    from ara.runtime.budget import BudgetStop

    maximum_failures = validate_failure_limit(calls.config)
    policy = dict(policy='continue-on-paper-failure', max_failed_papers=maximum_failures)
    calls.log.record('extraction_batch_started', **policy, selected=[p.source_id for p in papers])
    if not estimate_only:
        calls.budget.after('extract_paper')
    reused = reused or {}
    failures = 0

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
                'output_token_allowance': usage.output_tokens, 'estimated_usd': float(calls.budget.cost(usage, model=calls.requested_model('extract_paper'))),
                'extraction_cap_usd': calls.config['extraction_cost_cap_usd'],
                'run_cap_usd': calls.config['cost_cap_usd'],
                'note': 'Planning estimate: pages times tokens/page plus prompt overhead and full output allowance; '
                        'excludes retries/fallbacks. Admission counts each actual request separately.'}
    estimate['run_token_cap'] = calls.config['token_cap']
    estimate['planned_batch_exceeds_enclosing_caps'] = (
        usage.input_tokens + usage.output_tokens + calls.budget.used_tokens > calls.config['token_cap'] or
        calls.budget.cost(usage, model=calls.requested_model('extract_paper')) + calls.budget.used_cost > calls.config['cost_cap_usd'])
    calls.log.record('extraction_estimate', **estimate)
    print('Extraction estimate before dispatch: ' + canonical(estimate), flush=True)
    if estimate['planned_batch_exceeds_enclosing_caps']:
        print('planned batch exceeds enclosing caps', flush=True)
    outcomes = []
    for index, paper in enumerate(papers):
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
                'affected_pages': list(paper.affected_pages),
                'input_sha256': digest(canonical(paper.inputs()))}
        if paper.source_id in reused:
            previous = reused[paper.source_id]
            outcome = previous['outcome']
            validate_reused_paper(paper, outcome)
            calls.log.record('extraction_paper_reused', source_id=paper.source_id, origin=previous['origin'],
                             outcome_hash=digest(canonical(outcome)))
            calls.log.record('extraction_outcome', **outcome)
            outcomes.append(outcome)
            save_immutable(calls.log.path.parent / f'{paper.source_id}.extraction.json', canonical(outcome))
            continue
        if reason:
            outcome = {**base, 'status': 'record only, not extracted', 'reason': reason, 'items': []}
            calls.log.record('extraction_outcome', **outcome)
            outcomes.append(outcome)
            print(f'{paper.source_id}: record only, not extracted ({reason})', flush=True)
            if missing == 'refuse':
                raise ValueError(f'{paper.source_id}: extraction refused: {reason}')
            continue
        if paper.affected_pages and missing == 'refuse':
            calls.log.record('extraction_outcome', **base, status='partial', reason='strict_incomplete_coverage', items=[])
            raise ValueError(f'{paper.source_id}: extraction refused: partial text coverage')
        if not paper.readable_pages and paper.affected_pages:
            outcome = {**base, 'status': 'partial', 'reason': 'no_readable_pages', 'items': []}
            calls.log.record('extraction_outcome', **outcome)
            outcomes.append(outcome)
            continue
        calls.log.record('extraction_paper_started', **base)
        try:
            result = calls.extract_paper(paper)
        except Exception as exc:
            receipt = checkpoint(calls.log.path)
            outcome = {**base, 'status': 'failed', 'reason': type(exc).__name__, 'items': [],
                       'failure_detail': str(exc) if isinstance(exc, (Rejected, BudgetStop)) else type(exc).__name__,
                       'failure_receipt': receipt}
            calls.log.record('extraction_outcome', **outcome)
            outcomes.append(outcome)
            save_immutable(calls.log.path.parent / f'{paper.source_id}.extraction.json', canonical(outcome))
            failures += 1
            paper_failure = isinstance(exc, Rejected) or (isinstance(exc, BudgetStop) and exc.scope == 'paper')
            if not paper_failure or failures > maximum_failures:
                calls.log.record('extraction_stopped', **policy, failed_count=failures,
                                 failed_source_id=paper.source_id,
                                 completed=[o['source_id'] for o in outcomes if o['status'] != 'failed'],
                                 not_attempted=[p.source_id for p in papers[index + 1:]],
                                 reason='failed-paper threshold exceeded' if paper_failure else type(exc).__name__)
                raise  # Run budgets, unknown accounting and excess failures refuse publication.
            continue
        outcome = {**base, 'status': 'partial' if paper.affected_pages else 'extracted', **result.to_dict()}
        calls.log.record('extraction_outcome', **outcome)
        outcomes.append(outcome)
        save_immutable(calls.log.path.parent / f'{paper.source_id}.extraction.json', canonical(outcome))
    if estimate_only:
        return None
    lineage_missing = missing_lineage(calls.log.read())
    if lineage_missing:
        calls.log.record('extraction_lineage_missing', cache_keys=lineage_missing,
                         reason='cross-run extraction cache replay lacks origin receipt; import original extraction artifact')
    literature = assemble(outcomes)
    path = calls.log.path.parent / 'literature.extracted.txt'
    calls.log.record('extraction_completed', literature_sha256=digest(literature), papers=len(outcomes),
                     **policy, failed=[o['source_id'] for o in outcomes if o['status'] == 'failed'])
    # Pin the completed prefix. Later timing/export events may append without invalidating it.
    records = read_log(calls.log.path)
    path.with_suffix('.provenance.json').write_text(canonical({
        'source_log': str(calls.log.path.resolve()), 'records': len(records), 'last_hash': records[-1]['hash']}))
    save_immutable(path, literature)
    return path


def literature_provenance(path: Path, text: str) -> tuple[dict, ...]:
    """Validate the generated artifact against its pinned source-log prefix."""
    if text.startswith('# ARA extracted literature') and not text.startswith(HEADER):
        raise ValueError('unsupported extraction artifact version; regenerate rich v2 evidence')
    if not text.startswith(HEADER):
        return ()
    provenance = json.loads(path.with_suffix('.provenance.json').read_text())
    events = read_checkpoint(provenance)
    complete = json.loads(events[-1]['payload_json'])
    outcomes = extraction_outcomes(events)
    if events[-1]['stage'] != 'extraction_completed' or complete['literature_sha256'] != digest(text) or assemble(outcomes) != text:
        raise ValueError('extracted literature does not match logged output')
    if missing_lineage(events):
        raise MissingExtractionLineage('cross-run extraction cache replay lacks origin receipt; import original extraction artifact')
    return events


def import_provenance(log: EventLog, events: tuple[dict, ...], origin: dict | None = None) -> None:
    import_receipts(log, events, origin)


def validate_failure_limit(config):
    value = config.get('extraction_max_failed_papers', 3)
    if type(value) is not int or value < 0:
        raise ValueError('extraction_max_failed_papers must be a nonnegative integer')
    return value


def validate_reused_paper(paper, outcome):
    if outcome['status'] not in ('extracted', 'partial'):
        raise ValueError('resume requires completed paper outcome')
    expected = dict(source_id=paper.source_id, pdf_sha256=paper.pdf_sha256,
                    record=json.loads(paper.record_json), pages=len(paper.pages),
                    page_diagnostics=[asdict(d) for d in paper.diagnostics],
                    affected_pages=list(paper.affected_pages))
    if not paper.pdf_sha256 or any(outcome.get(k) != v for k, v in expected.items()):
        raise ValueError('resume paper identity mismatch')
    if outcome.get('input_sha256', digest(canonical(paper.inputs()))) != digest(canonical(paper.inputs())):
        raise ValueError('resume paper input mismatch')


def resume_papers(log, papers, sources):
    """Import whole origin receipts; reuse only completed, matching paper outcomes."""
    loaded = []
    reused = {}
    selected = {p.source_id: p for p in papers}
    for directory in sources:
        path = Path(directory) / 'events.jsonl'
        origin = checkpoint(path)
        events = read_checkpoint(origin)
        if missing_lineage(events):
            raise MissingExtractionLineage('resume origin lacks original extraction receipts')
        for outcome in extraction_outcomes(events):
            source = outcome['source_id']
            if source not in selected or outcome['status'] not in ('extracted', 'partial'):
                continue
            paper = selected[source]
            try:
                validate_reused_paper(paper, outcome)
            except ValueError:
                # Changed or previously unavailable sources need fresh extraction.
                continue
            if source in reused and reused[source]['outcome'] != outcome:
                raise ValueError(f'conflicting completed paper receipts: {source}')
            graph = {k: outcome[k] for k in ('schema_version', 'source_id', 'items',
                                            'obligations', 'resolutions', 'dispositions')}
            if not any(e['stage'] == 'extraction_graph_merged' and
                       json.loads(e['payload_json']).get('graph_hash') == digest(canonical(graph)) for e in events):
                raise ValueError('completed paper lacks accepted graph receipt')
            reused[source] = dict(outcome=outcome, origin=origin)
        loaded.append((events, origin))
    # Validate every origin before modifying the destination or constructing a provider.
    for events, origin in loaded:
        import_provenance(log, events, origin)
    return reused


def citation_ids(literature: str) -> set[str] | None:
    if not literature.startswith(HEADER):
        return None
    data = json.loads(literature[len(HEADER):])
    return {item['citation'] for paper in data['papers'] if paper['status'] in ('extracted', 'partial') for item in paper['items']}
