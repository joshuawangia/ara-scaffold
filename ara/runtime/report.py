"""Offline projections of verified run receipts. No provider or engine execution."""
from __future__ import annotations

from collections import Counter, defaultdict
from contextlib import nullcontext
import fcntl
import hashlib
import json
from pathlib import Path

from ara.runtime.cache import canonical, digest
from ara.runtime.logging import LogTampered, read_log
from ara.runtime.provenance import unique_events

TOKENS = ('input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_write_tokens', 'server_tool_uses')


def payload(event):
    return json.loads(event['payload_json'])


def compact(row):
    e = row['event']
    return dict(seq=row['seq'], timestamp=e['timestamp'], stage=e['stage'], label=e['label'],
                payload=payload(e), **({'decision': e['decision']} if e.get('decision') else {}))


def verified_snapshot(directory: Path):
    """Use an existing writer lock read-only; never create a lock or repair a log."""
    path = directory / 'events.jsonl'
    lock = path.with_suffix('.lock')
    gaps = []
    with lock.open('rb') if lock.exists() else nullcontext() as stream:
        if stream is not None:
            fcntl.flock(stream, fcntl.LOCK_SH)
        records = read_log(path)
        anchor = path.with_suffix('.anchor')
        if anchor.exists():
            if anchor.read_text().splitlines() != [r['hash'] for r in records]:
                raise LogTampered('log/checkpoint mismatch: ' + str(path))
        else:
            gaps.append('Tail checkpoint absent: chain verified, suffix truncation cannot be detected.')
    if not records:
        raise ValueError('empty run log: ' + str(path))
    events = [r['event'] for r in records]
    inherited = verify_available_imports(events, gaps)
    return records, inherited, gaps


def verify_available_imports(events, gaps, active=frozenset(), memo=None):
    """Check each available pinned prefix before inspecting its own ancestry."""
    memo = {} if memo is None else memo
    from ara.runtime.provenance import imported_event_indices
    seen, inherited = set(), imported_event_indices(events)
    for i, event in enumerate(events):
        data = payload(event)
        if event['stage'] != 'extraction_provenance_import':
            seen.add(digest(canonical(event)))
            continue
        count = data['records']
        if type(count) is not int or count < 0 or i + count >= len(events):
            raise ValueError('incomplete origin receipt import')
        copied = events[i + 1:i + 1 + count]
        inherited.update(range(i + 1, i + 1 + count))
        if 'origin' not in data:
            if digest(canonical(copied)) != data['receipt_id']:
                raise ValueError('legacy origin receipt import mismatch')
            continue
        origin = data['origin']
        key = canonical(origin)
        if key in active:
            raise ValueError('cyclic origin receipt')
        if key in memo:
            original = memo[key]
        else:
            try:
                rows = read_log(Path(origin['source_log']))
            except FileNotFoundError:
                gap = ('Origin unavailable at ' + origin['source_log'] +
                       '; only this missing prefix and its ancestry are unverified. Available direct origins remain checked.')
                if gap not in gaps:
                    gaps.append(gap)
                continue
            size = origin['records']
            if type(size) is not int or size <= 0 or len(rows) < size or rows[size - 1]['hash'] != origin['last_hash']:
                raise ValueError('extraction provenance checkpoint mismatch')
            original = tuple(row['event'] for row in rows[:size])
        if digest(canonical(original)) != data['receipt_id'] or list(copied) != unique_events(original, seen):
            raise ValueError('origin receipt import does not match pinned events')
        if key not in memo:
            verify_available_imports(original, gaps, active | {key}, memo)
            memo[key] = original
    return inherited


def totals(events):
    return dict(cost_usd=round(sum(e['cost_usd'] for e in events), 10),
                tokens={k: sum(e['usage'].get(k, 0) for e in events) for k in TOKENS},
                model_calls=len(events), wall_seconds=sum(e['wall_seconds'] for e in events))


def split_totals(events):
    events = [e for e in events if e['label'] == 'MODEL']
    unknown = [e for e in events if payload(e).get('accounting') == 'reservation_unknown_actual']
    measured = [e for e in events if payload(e).get('accounting') == 'actual']
    unclassified = [e for e in events if payload(e).get('accounting') not in ('actual', 'reservation_unknown_actual')]
    return dict(measured=totals(measured), unknown_at_reservation=totals(unknown),
                unclassified=totals(unclassified), budget_accounted=totals(events))


def accounting(events):
    calls = [e for e in events if e['label'] == 'MODEL']
    groups = {}
    for name, key in [('stage', lambda e: e['stage']),
                      ('paper', lambda e: payload(e).get('source_id') or '(unattributed)'),
                      ('model', lambda e: canonical([e['model_id'], e['model_version'], payload(e).get('served_model')]))]:
        buckets = defaultdict(list)
        for event in calls:
            buckets[key(event)].append(event)
        groups['by_' + name] = {k: split_totals(v) for k, v in buckets.items()}
    pending = defaultdict(list)
    received = {}
    for event in events:
        data = payload(event)
        key = (data.get('cache_key'), data.get('kind', event['stage']))
        if event['stage'] == 'call_start':
            pending[key].append(event)
        elif event['stage'] == 'response_received' and pending[key]:
            received[id(pending[key][-1])] = data
        elif event['label'] == 'MODEL' and not data.get('cache_hit') and pending[key]:
            received.pop(id(pending[key].pop(0)), None)
    unfinalized = list(received.values())
    timeline, measured, unknown, unclassified = [], 0.0, 0.0, 0.0
    for event in sorted(calls, key=lambda e: e['timestamp']):
        data = payload(event)
        is_unknown = data.get('accounting') == 'reservation_unknown_actual'
        if is_unknown:
            unknown += event['cost_usd']
        elif data.get('accounting') == 'actual':
            measured += event['cost_usd']
        else:
            unclassified += event['cost_usd']
        timeline.append(dict(timestamp=event['timestamp'], stage=event['stage'], source_id=data.get('source_id'),
                             model_id=event['model_id'], model_version=event['model_version'],
                             classification=('unknown_at_reservation' if is_unknown else 'measured' if data.get('accounting') == 'actual' else 'unclassified'),
                             recorded_accounting=data.get('accounting'),
                             cost_usd=event['cost_usd'], usage=event['usage'], wall_seconds=event['wall_seconds'],
                             cache_hit=data.get('cache_hit'), measured_cumulative_usd=round(measured, 10),
                             unknown_reservation_cumulative_usd=round(unknown, 10),
                             unclassified_cumulative_usd=round(unclassified, 10)))
    return dict(**split_totals(calls), **groups, timeline=timeline,
                unfinalized_measured_responses=unfinalized,
                unfinalized_measured_totals=dict(cost_usd=round(sum(p['measured_cost_usd'] for p in unfinalized), 10),
                    tokens={k: sum(p['measured_usage'].get(k, 0) for p in unfinalized) for k in TOKENS}),
                unresolved_dispatches=[dict(timestamp=e['timestamp'], **payload(e))
                                       for values in pending.values() for e in values],
                note='Missing or unrecognized accounting markers remain unclassified, including in the logged budget-accounted sum. Reservations are bounds, not measured charges. Budget-accounted totals combine them only for cap accounting. '
                     'Unattributed calls remain unattributed; cached replays use logged zero-charge usage. '
                     'Unresolved dispatch reservations are shown separately and are not finalized charges. '
                     'Measured response receipts without a final MODEL receipt are retained in unfinalized_measured_totals, separate from finalized totals.')


def artifacts(directory):
    result = []
    for path in sorted(directory.rglob('*')):
        if not path.is_file() or path.name in ('events.jsonl', 'events.anchor', 'events.lock'):
            continue
        relative = path.relative_to(directory)
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != directory):
            result.append(dict(path=str(relative), status='symlink not followed'))
            continue
        # Existing exports duplicate receipts and can be arbitrarily large.
        if relative.parts[0] == 'export':
            continue
        raw = path.read_bytes()
        entry = dict(path=str(relative), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                     trust='artifact, not authenticated by event chain unless matched to a receipt')
        if relative.parts[0] == 'search-traces':
            entry['trust'] = 'search sidecar; only a matching chained seal authenticates its trace projection'
            result.append(entry)
            continue
        try:
            entry['content'] = json.loads(raw) if path.suffix == '.json' else raw.decode('utf-8')
        except (UnicodeDecodeError, json.JSONDecodeError):
            entry['status'] = 'binary or invalid JSON; metadata only'
        result.append(entry)
    return result


def evidence_index(events):
    """Only exact recorded evidence identifiers; no guessed citation parsing."""
    evidence = defaultdict(list)
    for event in events:
        data = payload(event)
        papers = [data] if event['stage'] == 'extraction_outcome' else []
        if event['stage'] == 'run_started' and isinstance(data.get('literature'), str):
            text = data['literature']
            if text.startswith('# ARA extracted literature v') and '\n' in text:
                try:
                    papers += json.loads(text.split('\n', 1)[1]).get('papers', [])
                except (ValueError, AttributeError):
                    pass  # Raw literature remains in the verified event appendix.
        for paper in papers:
            for item in paper.get('items', []):
                value = {'source_id': paper.get('source_id'), 'record': paper.get('record'), **item}
                if value not in evidence[item['id']]:
                    evidence[item['id']].append(value)
    return evidence


def extraction(records, events):
    start = max((i for i, e in enumerate(events) if e['stage'] == 'extraction_batch_started'), default=0)
    current = events[start:]
    selected = next((payload(e).get('selected', []) for e in reversed(current)
                     if e['stage'] == 'extraction_batch_started'), [])
    requested_history = {sid for e in events if e['stage'] in ('extraction_batch_started', 'extraction_started')
                         for sid in payload(e).get('selected', [])}
    histories, related = defaultdict(list), defaultdict(list)
    for row in records:
        e, data = row['event'], payload(row['event'])
        if data.get('source_id'):
            if e['label'] != 'MODEL':
                related[data['source_id']].append(compact(row))
            if e['stage'] == 'extraction_outcome':
                histories[data['source_id']].append(data)
    latest = {payload(e)['source_id']: payload(e) for e in current if e['stage'] == 'extraction_outcome'}
    stopped = [payload(e) for e in current if e['stage'] == 'extraction_stopped']
    unattempted = {sid for p in stopped for sid in p.get('not_attempted', [])}
    papers = []
    for sid in sorted(set(histories) | set(related) | requested_history | set(selected) | unattempted):
        outcome = latest.get(sid)
        status = outcome['status'] if outcome else ('not attempted' if sid in unattempted else
                 'no current outcome' if sid in selected else 'historical only')
        calls = [e for e in events if e['label'] == 'MODEL' and payload(e).get('source_id') == sid]
        discoveries = [r['payload']['obligation'] for r in related[sid] if r['stage'] == 'extraction_obligation_discovered']
        resolved = {r['obligation_id'] for row in related[sid]
                    for r in row['payload'].get('resolutions', [])}
        papers.append(dict(source_id=sid, status=status, outcome=outcome, history=histories[sid],
                           item_counts_by_kind=dict(Counter(i['kind'] for i in (outcome or {}).get('items', []))),
                           open_obligations=[o for o in discoveries if o['id'] not in resolved],
                           accounting=split_totals(calls), receipts=related[sid]))
    return dict(papers=papers, corpus_totals=dict(papers=len(latest), selected=len(selected), requested_across_lineage=len(requested_history),
                status_counts=dict(Counter(p['status'] for p in papers)),
                item_counts_by_kind=dict(Counter(i['kind'] for p in latest.values() for i in p.get('items', [])))),
                exclusions=[dict(source_id=p['source_id'], status=p['status'],
                                 reason=(p['outcome'] or {}).get('reason') or ('not selected in latest recorded batch' if p['status'] == 'historical only' else p['status'])) for p in papers if p['status'] != 'extracted'],
                stops=stopped,
                note='Current outcomes come from the last extraction batch. Histories and per-paper accounting include imported receipts. '
                     'Historical successes are not silently substituted for an unattempted current paper.')


def construction(records, evidence):
    freezes = [r for r in records if r['event']['stage'] == 'commitments_frozen']
    commitments = payload(freezes[-1]['event'])['commitments']['commitments'] if freezes else []
    enriched = []
    for c in commitments:
        matches = [v for v in evidence.get(c['id'], []) if v.get('citation') == c['citation']]
        enriched.append(dict(**c, source_evidence=matches,
                             provenance='exact evidence id and citation match' if matches else 'citation only; structured source link unavailable'))
    merged = [payload(r['event']) for r in records if r['event']['stage'] == 'build_t_merged']
    symbols = merged[-1].get('symbols') if merged else None
    def classification(commitment, field):
        values = {item.get(field) for item in commitment['source_evidence']}
        return next(iter(values)) if len(values) == 1 and None not in values else '(unknown or ambiguous)'
    return dict(commitments=enriched,
                by_source=dict(Counter(classification(c, 'source_id') for c in enriched)),
                by_kind=dict(Counter(classification(c, 'kind') for c in enriched)),
                symbol_catalogue=symbols, symbol_count=len(symbols) if symbols is not None else None,
                freezes=[dict(seq=r['seq'], event_hash=r['hash'],
                              commitments_sha256=digest(canonical(payload(r['event'])['commitments'])),
                              hash_note='SHA-256 of canonical logged commitments, computed by reporter; event_hash is the chain freeze receipt.',
                              payload=payload(r['event'])) for r in freezes],
                receipts=[compact(r) for r in records if r['event']['stage'].startswith(('build_t_', 'construction_'))])


def route_details(row, commitments):
    data = payload(row['event'])
    graph = data['graph']
    support = []
    for node in graph['nodes']:
        ids = ([node['t_id']] if node.get('t_id') not in (None, 'open') else [])
        ids += [tid for answer in node.get('cq_answers', []) for tid in answer.get('supporting_t_ids', [])]
        for tid in dict.fromkeys(ids):
            support.append(dict(node_id=node['id'], commitment_id=tid, commitment=commitments.get(tid),
                                missing=tid not in commitments))
    from ara.runtime.route_policy import route_classification
    from ara.types import RouteGraph
    return dict(seq=row['seq'], target=data.get('target'), polarity=data.get('polarity'), graph=graph,
                classification=route_classification(RouteGraph.from_dict(graph)),
                support_chain=support, model_summary=None, audit_results=[])


def searches(records, directory):
    from ara.runtime.report_traces import collect_traces
    return collect_traces(records, directory, compact)


def build_run(directory):
    directory = Path(directory).resolve()
    records, inherited, gaps = verified_snapshot(directory)
    events = [r['event'] for r in records]
    evidence = evidence_index(events)
    built = construction(records, evidence)
    frozen = {c['id']: c for c in built['commitments']}
    routes = [route_details(r, frozen) for r in records if r['event']['stage'] == 'route']
    search = searches(records, directory)
    for trace in search['traces']:
        gaps.extend("PARTIAL SEARCH TRACE: " + text for text in trace['issues'])
    if search['unassigned_trace_receipts']:
        gaps.append("PARTIAL SEARCH TRACE: unassigned trace receipts are retained.")
    for route in routes:
        rid = route['graph']['id']
        summaries = [payload(e) for e in events if e['stage'] == 'route_summary' and payload(e).get('route_id') == rid]
        route['model_summary'] = summaries[-1] if summaries else None
        route['audit_results'] = [compact(r) for r in records if payload(r['event']).get('route_id') == rid
                                 and ('audit' in r['event']['stage'] or r['event']['stage'] == 'final_draft')]
    if not any(e['stage'].startswith('extraction_') for e in events):
        gaps.append('Extraction receipts are absent; corpus extraction counts and exclusions cannot be established from this run.')
    if not built['freezes']:
        gaps.append('No commitments_frozen receipt: construction may be absent or interrupted; no completed freeze is claimed.')
    if any(e['label'] == 'MODEL' and e['stage'] == 'extract_paper' and not payload(e).get('source_id') for e in events):
        gaps.append('Some extraction calls lack a source_id; their usage remains in the unattributed paper bucket.')
    if routes and not search['traces']:
        gaps.append('PARTIAL SEARCH TRACE: final route graphs are recorded, but search-state ancestry, discarded alternatives and polarity-specific prune context are absent. No search tree is reconstructed from legacy node IDs.')
    elif (any(not t['complete'] for t in search['traces']) or
          sum(r['stage'] == 'search_started' for r in search['logged_searches']) > len(search['traces'])):
        gaps.append('PARTIAL SEARCH TRACE: an interrupted or legacy search lacks complete begin/end trace receipts.')
    elif not routes and not search['traces']:
        gaps.append('Search-state trace and final routes not recorded in this run; raw calls and decisions are retained, but no target or negation completion is claimed.')
    if routes and any(r['model_summary'] is None for r in routes):
        gaps.append('Model-written route summaries are not recorded for some routes. No model was called and no summary was fabricated.')
    if any(c['provenance'].startswith('citation only') for c in built['commitments']):
        gaps.append('Some commitments have only a verbatim citation: source paper, kind and page linkage cannot be established by exact recorded evidence ID and citation.')
    identity_receipts = [dict(**compact(r), inherited=r['seq'] in inherited) for r in records if r['event']['stage'] in
                         ('run_started', 'extraction_started', 'schema_preflight_config', 'extraction_planning_started', 'run_identity')]
    revisions = [p[k] for r in records for p in [payload(r['event'])]
                 for k in ('code_revision', 'git_revision', 'git_sha', 'revision') if k in p]
    if not revisions:
        gaps.append('Run code revision not recorded; the reporter checkout revision is not substituted.')
    account = accounting(events)
    if account['unclassified']['model_calls']:
        gaps.append('Accounting unclassified: missing or unrecognized accounting markers cannot establish measured usage; see unclassified totals and timeline.')
    if account['unknown_at_reservation']['model_calls'] or account['unresolved_dispatches']:
        gaps.append('Accounting incomplete: unknown actual usage or unresolved dispatched calls remain. Reservations are not measured spend.')
    failures = [compact(r) for r in records if r['event']['label'] == 'STOP' or
                any(word in r['event']['stage'] for word in ('error', 'failed', 'stopped', 'gap', 'missing')) or
                payload(r['event']).get('status') in ('failed', 'rejected', 'incomplete', 'partial')]
    # Include original failure/limit receipts verbatim, never reduce them to an error count.
    limits = [compact(r) for r in records if r['event']['label'] != 'MODEL' and
              (any(word in r['event']['stage'] for word in ('obligation', 'reconciliation', 'correction', 'omitted')) or
               any(payload(r['event']).get(k) for k in ('gaps', 'limitations', 'reason', 'affected_pages')))]
    return dict(directory=str(directory), identity=dict(code_revisions=revisions or None,
                first_timestamp=min(e['timestamp'] for e in events), last_timestamp=max(e['timestamp'] for e in events),
                local_first_timestamp=min((e['timestamp'] for i, e in enumerate(events) if i not in inherited), default=None),
                local_last_timestamp=max((e['timestamp'] for i, e in enumerate(events) if i not in inherited), default=None),
                snapshot=dict(records=len(records), last_hash=records[-1]['hash'], anchor_present=(directory/'events.anchor').exists()),
                configuration_receipts=identity_receipts,
                models=sorted({canonical([e['model_id'], e['model_version'], payload(e).get('served_model')])
                               for e in events if e['label'] == 'MODEL'}),
                lineage=[compact(r) for r in records if r['event']['stage'] in
                         ('extraction_provenance_import', 'extraction_paper_reused', 'unknown_usage_reconciled')]),
                extraction=extraction(records, events), construction=built, search=search, routes=routes,
                accounting=dict(**account, local=split_totals([e for i, e in enumerate(events) if i not in inherited]),
                                inherited=split_totals([e for i, e in enumerate(events) if i in inherited])),
                human_actions=[compact(r) for r in records if r['event']['label'] == 'HUMAN'],
                gaps=gaps, failure_receipts=failures, limit_receipts=limits,
                unassigned_audits=[compact(r) for r in records if 'audit' in r['event']['stage'] and not payload(r['event']).get('route_id')],
                artifacts=artifacts(directory), records=records)


def generate_report(run_dirs, out):
    from ara.runtime.report_render import render
    directories = list(dict.fromkeys(Path(p).resolve() for p in run_dirs))
    destination = Path(out).resolve()
    if any(destination == d or destination in d.parents or d in destination.parents for d in directories):
        raise ValueError('report output must be separate from every input run directory')
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('report output must be empty; choose a fresh snapshot directory')
    runs = [build_run(d) for d in directories]  # Verify every input before publishing anything.
    unique = {}
    for run in runs:
        for row in run['records']:
            event = row['event']
            unique.setdefault(digest(canonical(event)), event)
    report = dict(format_version=2, runs=runs, accounting=accounting(list(unique.values())),
                  aggregation_note='Combined accounting deduplicates identical event receipts across supplied runs and imported lineage. '
                                   'Per-run totals include inherited receipts; do not add them. Hash chains detect changes relative to checkpoints, not malicious rewriting of both log and checkpoint.')
    destination.mkdir(parents=True, exist_ok=True)
    render(report, destination)
    return destination / 'report.html'
