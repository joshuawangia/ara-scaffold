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
                                    extraction_outcomes, historical_extraction_outcomes)

if TYPE_CHECKING:
    from ara.runtime.calls import ModelCalls

HEADER = '# ARA extracted literature v2\n'
EXTRACTION_VERSION = 2
PUBLICATION_POLICY = 'quarantine-aware-v1'
# Bump when validation, normalization, mode schemas or graph interpretation change.
EXTRACTION_ACCEPTANCE_VERSION = 'rich-paper-acceptance-v6'
V5_UNION_PROMPT_SHA256 = '7f653b3126df705c7fe2ccd8fb806f0c864146dfee63f12d4b907beb6492e537'
V5_SCHEMA_SHA256 = 'e5995f28b1d3c311c10de7894e5106634cec33ba70f13310a5dd23d1df323df9'
# The reviewed predecessors; unknown contracts never migrate by version alone.
V5_PRE_UNION_PROMPT_SHA256 = '96510d73f8288a587c78edf86b417725863a275487f795f9f3d75cdbb6ebbc72'
V4_PROMPT_SHA256 = '6fdc1d8a71ded072a99d9190245bd3380e8ae003ee7cdce7f614e611158bbe22'
V4_SCHEMA_SHA256 = '7d2778f90a78b5040dc3e9d7975f33b216d96652f3ca134e9d7ce568b72fd9cf'


def extraction_acceptance_identity(config: dict, root: Path) -> dict:
    """Effective reusable-paper contract; budgets and recovery allowances are excluded."""
    from ara.runtime.providers import stage_settings
    stage = stage_settings(config, 'extract_paper')
    fallbacks = stage.get('fallbacks', ['claude-opus-4-8'])
    return {
        'version': EXTRACTION_ACCEPTANCE_VERSION,
        'require_inference': bool(config.get('extraction_require_inference', False)),
        'provider': config['provider'],
        'stage': {'model': stage['model'], 'effort': stage['effort'],
                  'thinking': stage.get('thinking', 'adaptive'),
                  'fallbacks': [] if fallbacks == 'off' else list(fallbacks)},
        'prompt_sha256': digest((Path(root)/'prompts/extract_paper.txt').read_text()),
        'schema_sha256': digest(canonical(json.loads((Path(root)/'schemas/extract_paper.json').read_text()))),
    }



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
    inference_origin: Literal['paper_stated', 'reconstructed'] | None

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
    if outcome.get('range_union_policy') or outcome.get('publication_policy') == PUBLICATION_POLICY:
        blocked = {q['item_id'] for q in outcome.get('quarantined', [])}
        resolved = {r['obligation_id'] for r in outcome.get('resolutions', []) if not blocked.intersection(r['evidence_ids'])}
        entry['open_gaps'] = [o for o in outcome.get('obligations', []) if o['id'] not in resolved]
        entry['dispositions'] = outcome.get('dispositions', [])
    if 'snapshot_union' in outcome:
        entry['snapshot_union'] = outcome['snapshot_union']
        entry['item_provenance'] = outcome['item_provenance']
    if 'grounding' in outcome:
        entry['grounding'] = outcome['grounding']
        entry['quarantined'] = outcome['quarantined']
    if outcome.get('affected_pages'):
        entry['coverage'] = 'partial: unread visual pages excluded; retained encoding warnings require source inspection; see diagnostics'
    return entry


def publication_roster(outcomes):
    return [dict(source_id=o['source_id'], status=o['status'],
                 reason=o.get('failure_detail') or o.get('reason') or 'No accepted evidence.')
            for o in outcomes if o['status'] not in ('extracted', 'partial')]


def assemble(outcomes: list[dict]) -> str:
    entries = [literature_entry(outcome) for outcome in outcomes]
    # Unmarked outcomes retain their historical serialization for hash verification.
    current = any(o.get('publication_policy') == PUBLICATION_POLICY for o in outcomes)
    return HEADER + canonical({
        'origin': 'SYSTEM/MODEL', 'locator_convention': 'one-based physical PDF pages, not printed folios',
        'use': 'Use extracted items only. Record-only entries supply no claims. Partial entries cover only '
               'readable pages. Preserve attribution; reported or attacked views are not author endorsements. '
               'Copy evidence identifiers and citations verbatim. ' +
               ('Inferences describe paper-stated or reconstructed links, not engine licenses.' if current else
                'Inferences describe paper-stated links, not engine licenses.'),
        **({'status': 'complete_with_disclosed_failures'} if any(e['status'] == 'failed' for e in entries) else {}),
        'papers': entries,
        **({'grounding_note': 'Items retain the original inventory for audit. Entries listed in quarantined are not evidence and must never enter T. Only grounding-accepted items may be used; lexical overlap is not semantic entailment.'} if any('grounding' in o for o in outcomes) else {}),
        **({'acceptance_note': 'Accepted range union with best-effort reconciliation. Open gaps, missing pages and thin ranges remain disclosed. Inference origins may be paper_stated or reconstructed; neither is an engine license.', 'publication_roster': publication_roster(outcomes)} if any(o.get('range_union_policy') for o in outcomes) or any(o['status'] in ('excluded', 'not extracted') for o in outcomes) else {})}) + '\n'


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
            estimate_only: bool = False, reused: dict | None = None, salvage_only=False, excluded=None) -> Path | None:
    from ara.types import TokenUsage
    from ara.runtime.grounding import ground_outcome
    from ara.runtime.calls import Rejected
    from ara.runtime.budget import BudgetStop

    acceptance = extraction_acceptance_identity(calls.config, calls.root)
    maximum_failures = validate_failure_limit(calls.config)
    policy = dict(policy='continue-on-paper-failure', max_failed_papers=maximum_failures)
    calls.log.record('extraction_batch_started', **policy, config=calls.config, selected=[p.source_id for p in papers])
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
    stopped = None
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
        base = {'publication_policy': PUBLICATION_POLICY, 'range_union_policy': True, 'source_id': paper.source_id, 'record': json.loads(paper.record_json),
                'pdf_sha256': paper.pdf_sha256, 'pages': len(paper.pages),
                'page_diagnostics': [asdict(d) for d in paper.diagnostics],
                'affected_pages': list(paper.affected_pages),
                'input_sha256': digest(canonical(paper.inputs()))}
        if paper.affected_pages and missing == 'refuse':
            calls.log.record('extraction_outcome', **base, status='partial', reason='strict_incomplete_coverage', items=[])
            raise ValueError(f'{paper.source_id}: extraction refused: partial text coverage')
        if excluded and paper.source_id in excluded:
            outcome = {**base, 'status': 'excluded', 'reason': excluded[paper.source_id], 'items': [], 'range_union_policy': True}
            calls.log.record('extraction_outcome', **outcome)
            outcomes.append(outcome)
            continue
        if paper.source_id in reused and 'outcome' in reused[paper.source_id]:
            previous = reused[paper.source_id]
            outcome = previous['outcome']
            validate_reused_paper(paper, outcome, acceptance)
            calls.log.record('extraction_paper_reused', source_id=paper.source_id, origin=previous['origin'],
                             outcome_hash=digest(canonical(outcome)))
            outcome = ground_outcome(paper, outcome, calls.log)
            outcome = {**outcome, 'publication_policy': PUBLICATION_POLICY}
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
        if not paper.readable_pages and paper.affected_pages:
            outcome = {**base, 'status': 'partial', 'reason': 'no_readable_pages', 'items': []}
            calls.log.record('extraction_outcome', **outcome)
            outcomes.append(outcome)
            continue
        calls.log.record('extraction_paper_started', **base)
        try:
            result = calls.extract_paper(paper, salvaged=reused.get(paper.source_id, {}).get('ranges', ()), salvage_only=salvage_only)
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
                stopped = exc
                for remaining in papers[index + 1:]:
                    not_attempted = dict(source_id=remaining.source_id, status='not extracted', items=[],
                                         pdf_sha256=remaining.pdf_sha256, range_union_policy=True,
                                         reason='Batch stopped before extraction: ' + type(exc).__name__)
                    calls.log.record('extraction_outcome', **not_attempted)
                    outcomes.append(not_attempted)
                break
            continue
        outcome = {**base, 'status': 'partial' if paper.affected_pages else 'extracted',
                   'acceptance_identity': acceptance, 'range_union_policy': True, **result.to_dict()}
        if any(d.get('kind') == 'unextracted_pages' for d in json.loads(result.dispositions_json)):
            outcome['status'] = 'partial' if result.items else 'not extracted'
            outcome['reason'] = 'Readable pages remain unextracted; see dispositions.'
        outcome = ground_outcome(paper, outcome, calls.log)
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
    if stopped is not None:
        raise stopped
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
    value = config.get('extraction_max_failed_papers', 8)
    if type(value) is not int or value < 0:
        raise ValueError('extraction_max_failed_papers must be a nonnegative integer')
    return value


def validate_reused_paper(paper, outcome, acceptance):
    previous = outcome.get('acceptance_identity')
    compatible_v4 = bool(previous and acceptance and
        acceptance.get('version') == 'rich-paper-acceptance-v6' and
        previous.get('version') == 'rich-paper-acceptance-v4' and
        previous.get('prompt_sha256') == V4_PROMPT_SHA256 and
        previous.get('schema_sha256') == V4_SCHEMA_SHA256 and
        all(previous.get(k) == acceptance.get(k) for k in ('provider', 'stage', 'require_inference')))
    compatible_v5 = bool(previous and acceptance and acceptance.get('version') == 'rich-paper-acceptance-v6' and previous.get('version') == 'rich-paper-acceptance-v5' and
        previous.get('prompt_sha256') in (V5_PRE_UNION_PROMPT_SHA256, V5_UNION_PROMPT_SHA256) and
        previous.get('schema_sha256') == V5_SCHEMA_SHA256 and
        all(previous.get(k) == acceptance.get(k) for k in ('provider', 'stage', 'require_inference')))
    if not acceptance or (previous != acceptance and not compatible_v4 and not compatible_v5):
        raise ValueError('resume extraction acceptance identity mismatch')
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
    if compatible_v4 or compatible_v5:
        revalidate_v4_graph(paper, outcome, acceptance)


def revalidate_v4_graph(paper, outcome, acceptance):
    """Offline migration checks the actual graph, never relabels an old receipt."""
    from jsonschema import Draft202012Validator
    schema = json.loads((Path(__file__).resolve().parents[2] / 'schemas/extract_paper.json').read_text())
    items = [{k: v for k, v in item.items() if k != 'citation'} for item in outcome['items']]
    Draft202012Validator(schema).validate(dict(schema_version=2, source_id=paper.source_id,
        coverage_complete=True, new_gaps=[], items=items))
    by_id = {i['id']: i for i in items}
    if len(by_id) != len(items):
        raise ValueError('resume duplicate graph id')
    readable = {p.page for p in paper.readable_pages}
    for item, original in zip(items, outcome['items'], strict=True):
        if (item['source_id'] != paper.source_id or not item['text'].strip() or
                not item['attributed_to'].strip() or
                not 1 <= item['page_start'] <= item['page_end'] <= len(paper.pages) or
                item['page_start'] not in readable or item['page_end'] not in readable or
                any(item['page_start'] <= p <= item['page_end'] for p in paper.unread_pages)):
            raise ValueError('resume invalid graph source evidence')
        refs = (*item['premise_ids'], *item['qualification_ids'], *item['applies_to'],
                *((item['conclusion_id'],) if item['conclusion_id'] else ()))
        if not set(refs) <= by_id.keys():
            raise ValueError('resume unknown graph reference')
        if item['kind'] == 'inference':
            if (not item['premise_ids'] or not item['conclusion_id'] or
                    item['inference_origin'] not in ('paper_stated', 'reconstructed') or
                    any(by_id[r]['kind'] == 'inference' for r in (*item['premise_ids'], item['conclusion_id'])) or
                    any(by_id[r]['kind'] not in ('distinction', 'qualification') for r in item['qualification_ids'])):
                raise ValueError('resume invalid inference')
        elif item['premise_ids'] or item['conclusion_id'] or item['qualification_ids'] or item['inference_origin']:
            raise ValueError('resume node contains inference fields')
        if item['applies_to'] and item['kind'] not in ('distinction', 'qualification'):
            raise ValueError('resume invalid qualification relation')
        if original.get('citation') != ExtractedItem(**item).citation:
            raise ValueError('resume invalid citation')
    obligations = [o['id'] for o in outcome['obligations']]
    resolutions = [r['obligation_id'] for r in outcome['resolutions']]
    if (len(set(obligations)) != len(obligations) or len(set(resolutions)) != len(resolutions) or
            not set(resolutions) <= set(obligations) or any(not r['evidence_ids'] or
            not set(r['evidence_ids']) <= by_id.keys() for r in outcome['resolutions'])):
        raise ValueError('resume unresolved graph obligations')


def resume_papers(log, papers, sources, config: dict, root: Path, *, revalidate_only=False):
    """Verify all ancestry before import; index compatible successes across every batch.

    config must be the effective (profile-applied) configuration, root the contract
    directory. Missing or incompatible acceptance identities require extraction.
    Publication still uses extraction_outcomes(), which selects only the last batch.
    revalidate_only remains an accepted keyword; completed reuse now always retains
    every compatible snapshot, in both ordinary and salvage-only runs.
    """
    from ara.runtime.snapshot_union import VERSION, graph, snapshot_id, unite
    acceptance = extraction_acceptance_identity(config, root)
    loaded, derived = [], []
    snapshots = {}
    selected = {p.source_id: p for p in papers}
    for directory in sources:
        path = Path(directory) / 'events.jsonl'
        origin = checkpoint(path)
        events = read_checkpoint(origin)
        if missing_lineage(events):
            raise MissingExtractionLineage('resume origin lacks original extraction receipts')
        accepted_graphs = {json.loads(e['payload_json']).get('graph_hash') for e in events
                           if e['stage'] == 'extraction_graph_merged'}
        for outcome in historical_extraction_outcomes(events):
            source = outcome['source_id']
            if source not in selected or outcome['status'] not in ('extracted', 'partial'):
                continue
            try:
                validate_reused_paper(selected[source], outcome, acceptance)
            except ValueError:
                # Changed sources or incompatible/unknown acceptance policies need extraction.
                continue
            if digest(canonical(graph(outcome))) not in accepted_graphs:
                raise ValueError('completed paper lacks accepted graph receipt')
            if 'snapshot_union' in outcome:
                if outcome['snapshot_union'].get('version') != VERSION:
                    raise ValueError('unsupported completed snapshot union')
                derived.append(outcome)
                continue
            sid = snapshot_id(outcome)
            entry = snapshots.setdefault(source, {}).setdefault(sid, dict(outcome=outcome, origins=[]))
            if origin not in entry['origins']:
                entry['origins'].append(origin)
        loaded.append((events, origin))
    # A published union is derived, never a new independent source snapshot.
    # Require its original snapshots in the verified ancestry before rebuilding.
    for outcome in derived:
        if not set(outcome['snapshot_union']['snapshots']) <= snapshots.get(outcome['source_id'], {}).keys():
            raise ValueError('completed snapshot union lacks original snapshot receipts')
        originals = {id: snapshots[outcome['source_id']][id] for id in outcome['snapshot_union']['snapshots']}
        rebuilt = unite(originals, outcome['acceptance_identity'])
        if (graph(rebuilt) != graph(outcome) or
                rebuilt['item_provenance'] != outcome.get('item_provenance')):
            raise ValueError('completed snapshot union differs from original snapshot receipts')
    reused = {}
    for source, entries in snapshots.items():
        first = entries[sorted(entries)[0]]
        outcome = unite(entries, acceptance) if len(entries) > 1 else first['outcome']
        reused[source] = dict(outcome=outcome, origin=sorted(first['origins'], key=canonical)[0])
    # Validate and construct every union before modifying the destination.
    for events, origin in loaded:
        import_provenance(log, events, origin)
    for source, entries in snapshots.items():
        for entry in entries.values():
            outcome = entry['outcome']
            if outcome['acceptance_identity'] != acceptance:
                log.record('extraction_acceptance_revalidated', source_id=source,
                           from_identity=outcome['acceptance_identity'], to_identity=acceptance,
                           outcome_hash=digest(canonical(outcome)))
        outcome = reused[source]['outcome']
        if 'snapshot_union' in outcome:
            graph_hash = digest(canonical(graph(outcome)))
            log.record('extraction_snapshot_union', source_id=source, **outcome['snapshot_union'],
                       items=len(outcome['items']), graph_hash=graph_hash,
                       item_provenance_sha256=digest(canonical(outcome['item_provenance'])))
            log.record('extraction_graph_merged', source_id=source, graph_hash=graph_hash,
                       snapshots=len(entries), items=len(outcome['items']))
    from ara.runtime.salvage import accepted_ranges
    combined = []
    seen = set()
    for events, _ in loaded:
        for event in events:
            key = digest(canonical(event))
            if key not in seen:
                combined.append(event)
                seen.add(key)
    incompatible_completed = {o['source_id'] for events, _ in loaded for o in historical_extraction_outcomes(events)
                              if o['status'] in ('extracted', 'partial') and not (o.get('range_union_policy') and any(d.get('kind') in ('thin_range', 'unextracted_pages') for d in o.get('dispositions', [])))}
    candidates = tuple(p for p in papers if p.source_id not in reused and p.source_id not in incompatible_completed)
    ranges = accepted_ranges(combined, candidates, config, root, log)
    for source, entries in ranges.items():
        reused[source] = dict(ranges=entries)
    return reused


def citation_ids(literature: str) -> set[str] | None:
    if not literature.startswith(HEADER):
        return None
    data = json.loads(literature[len(HEADER):])
    from ara.runtime.grounding import evidence_items
    return {item['citation'] for paper in data['papers'] if paper['status'] in ('extracted', 'partial') for item in evidence_items(paper)}
