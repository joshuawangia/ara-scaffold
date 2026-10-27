"""Verify and publish stopped search work before any provider can be constructed."""
from __future__ import annotations

from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import hashlib
import json
from pathlib import Path

from ara.engine.licensing import Licenser
from ara.engine.routes import independent_count
from ara.engine.search import EngineConfig, SearchResult
from ara.runtime.cache import canonical, digest
from ara.runtime.calls import require
from ara.runtime.codex_schema import normalize_output
from ara.runtime.logging import EventLog, now
from ara.runtime.providers import Response
from ara.runtime.report_traces import expand_proposal, new_trace, read_sidecar, validate_trace
from ara.types import CommitmentSet, Formula, Proposition, Proposal, RouteGraph, RunEvent, TokenUsage, negate_proposition


def payload(event):
    return json.loads(event['payload_json'])


@contextmanager
def search_resume_lock(directory):
    with (directory / 'search-resume.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError('search resume already running') from exc
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


class RecordedFormaliser:
    """Replay only accepted formula receipts to recheck licenses, never search."""
    def __init__(self, events, root):
        self.formulas = defaultdict(deque)
        self.slots = defaultdict(deque)
        schema = json.loads((root / 'schemas/formalise.json').read_text())
        for event in events:
            data = payload(event)
            if event['stage'] == 'formalise' and event['label'] == 'MODEL' and data.get('status') == 'accepted':
                inputs = json.loads(event['prompt'].split('\nINPUT_JSON\n')[1])
                result = json.loads(Response(json.loads(event['response'])).text())
                if data.get('provider') == 'codex_cli':
                    result = normalize_output(schema, result)
                self.formulas[canonical(inputs['proposition'])].append(Formula.from_dict(result['formula']))

            if event['stage'] == 'formalise_slots' and event['label'] == 'MODEL' and data.get('status') == 'accepted':
                inputs = json.loads(event['prompt'].split('\nINPUT_JSON\n')[1])
                result = json.loads(Response(json.loads(event['response'])).text())
                if data.get('provider') == 'codex_cli':
                    result = normalize_output(json.loads((root / 'schemas/formalise_slots.json').read_text()), result)
                key = canonical([inputs['proposal'], inputs['goal'], inputs['bank_entry']])
                self.slots[key].append((inputs, result))

    def formalise_slots(self, proposal, goal, entry, commitments):
        from ara.runtime.search_alignment import slot_bindings, validate_slots
        saved = self.slots[canonical([proposal.to_dict(), goal.to_dict(), entry.to_dict()])]
        require(bool(saved), 'search resume missing accepted joint formalisation receipt')
        inputs, result = saved.popleft()
        bindings = slot_bindings(proposal, commitments)
        require(inputs['slot_bindings'] == bindings and
                inputs['commitments_sha256'] == digest(canonical(commitments.to_dict())),
                'search resume joint binding mismatch')
        return validate_slots(result, proposal, entry, bindings, inputs['symbol_catalogue'])

    def formalise(self, proposition):
        saved = self.formulas[canonical(proposition.to_dict())]
        require(bool(saved), 'search resume missing accepted formalisation receipt')
        return saved.popleft()

    def emit(self, event):
        pass  # Deterministic rechecking does not create new historical decisions.


def restore_result(directory, events, goal, commitments, bank, config, root):
    starts = [i for i, e in enumerate(events) if e['stage'] == 'search_job_started']
    if not starts:
        return None
    attempt = events[starts[-1]:]
    seals = [payload(e) for e in attempt if e['stage'] == 'search_trace_receipt']
    if not seals:
        require(not any(e['stage'] == 'search_job_finished' for e in attempt),
                'search resume completed job missing seal')
        return None
    require(len(seals) == 1,
            'search resume completed job lacks one terminal seal')
    seal = seals[0]
    # Resume requires local artifacts; a copied run cannot silently borrow originals.
    rows, _ = read_sidecar(directory, {k: v for k, v in seal.items() if k != 'source_log'})
    require(bool(rows), 'search resume sealed trace missing')
    require(seal['version'] == 2 and rows[0].get('search_id') == seal['search_id'],
            'search resume seal identity mismatch')
    trace = new_trace(0, rows[0], source=seal)
    trace['receipts'] = [dict(payload=row) for row in rows]
    trace['states'] = [row for row in rows if row['action'] == 'state']
    validate_trace(trace)
    require(trace['complete'], 'search resume invalid sealed trace: ' + '; '.join(trace['issues']))
    definitions = {(r['kind'], r['ref']): r['value'] for r in rows if r['action'] == 'definition'}
    def reference(kind, ref):
        return definitions[kind, ref]
    target = rows[0]['target']
    restored_goal = Proposition(target['id'], reference('text', target['text_id']),
                                Formula.from_dict(reference('formula', target['formula_id'])))
    require(restored_goal == goal, 'search resume trace target mismatch')
    require(rows[0]['bank_version'] == bank.bank_version and
            rows[0]['config'] == EngineConfig.from_mapping(config).to_dict(),
            'search resume trace bank/config mismatch')
    routes = tuple(RouteGraph.from_dict(r['graph']) for r in trace['completed_routes'])
    end = rows[-1]
    require(end['routes'] == [r.id for r in routes], 'search resume terminal route mismatch')
    result = SearchResult(goal, routes, independent_count(routes, commitments), end['nodes_created'], end['truncated'])
    formaliser = RecordedFormaliser(attempt, root)
    licenser = Licenser(bank, formaliser, formaliser, config.get('solver_timeout_ms', 1000), commitments)
    nodes = {r['node_id']: r for r in rows if r['action'] == 'node'}
    prunes = {(r['state_id'], r['node_id'], r['proposal_index']): r['reason']
              for r in rows if r['action'] == 'prune'}
    licenses = []
    for row in rows:
        if row['action'] != 'proposal':
            continue
        reason = prunes.get((row['state_id'], row['node_id'], row['proposal_index']))
        if reason == 'DUPLICATE_PROPOSAL':
            continue
        node = nodes[row['node_id']]
        node_goal = Proposition(row['node_id'], reference('text', node['text_id']),
                                Formula.from_dict(reference('formula', node['formula_id'])))
        proposal = Proposal.from_dict(expand_proposal(row['proposal_id'], reference))
        license = licenser.check(proposal, node_goal, row['node_id'])
        require(license.licensed == (reason in (None, 'NODE_CAP')),
                'search resume license differs from sealed decision')
        if license.licensed:
            licenses.append((proposal, license))
    require(len(licenses) == sum((e.get('decision') or {}).get('reason_code') == 'BANK_LICENSED' for e in attempt),
            'search resume license inventory mismatch')
    return result, licenses


def unsettled_receipts(events):
    starts, received, finished = {}, {}, set()
    for event in events:
        data = payload(event)
        call_id = data.get('call_id')
        if event['stage'] == 'call_start':
            require(call_id and call_id not in starts, 'search resume duplicate or missing call identity')
            starts[call_id] = data
        elif event['stage'] == 'response_received':
            require(call_id in starts and call_id not in received, 'search resume unmatched measured receipt')
            start = starts[call_id]
            require(all(start[k] == data[k] for k in ('kind', 'cache_key')),
                    'search resume measured receipt identity mismatch')
            require(TokenUsage.from_dict(data['measured_usage']) == Response(data['raw_response']).usage,
                    'search resume measured usage differs from raw response')
            received[call_id] = data
        elif event['label'] == 'MODEL' and not data.get('cache_hit'):
            require(call_id in starts and call_id not in finished, 'search resume unmatched accounting receipt')
            require(event['stage'] == starts[call_id]['kind'] and data.get('cache_key') == starts[call_id]['cache_key'],
                    'search resume accounting identity mismatch')
            if call_id in received:
                require(event['usage'] == received[call_id]['measured_usage'] and
                        event['cost_usd'] == received[call_id]['measured_cost_usd'],
                        'search resume measured accounting mismatch')
            finished.add(call_id)
    pending = []
    for call_id in starts:
        if call_id in finished:
            continue
        require(call_id in received, 'search resume interrupted dispatch without measured receipt')
        start, receipt = starts[call_id], received[call_id]
        raw = receipt['raw_response']
        pending.append(RunEvent(now(), start['kind'], 'MODEL', start['model'], raw.get('model'),
            start['prompt'], canonical(raw), TokenUsage.from_dict(receipt['measured_usage']),
            receipt['measured_cost_usd'], payload_json=canonical(dict(
                call_id=call_id, cache_key=start['cache_key'], cache_hit=False, accounting='actual',
                status='incomplete', reason='interrupted validation; measured receipt recovered',
                recovery='resume-search', receipt_hash=digest(canonical(receipt))))))
    return pending


@dataclass
class SearchResume:
    run: dict
    commitments: CommitmentSet
    targets: tuple
    restored: dict
    publications: list
    settlements: list
    already_finished: bool

    def summary(self):
        return dict(completed_jobs=sorted(self.restored),
                    jobs_to_rerun=[i for i in range(2 * len(self.targets)) if i not in self.restored],
                    commitments_hash=digest(self.commitments.to_json()),
                    state='awaiting_selection' if self.already_finished else 'stopped_before_dispatch')


def publication_progress(main, batch_id, index, receipt, journal):
    """Verify every already copied prefix, including a halt inside publication."""
    offset, published, seen = 0, False, False
    for position, event in enumerate(main):
        data = payload(event)
        if data.get('batch_id') != batch_id or data.get('job_index') != index:
            continue
        if event['stage'] in ('search_job_publication', 'search_job_publication_continued'):
            require(not published, 'search resume duplicate publication')
            if event['stage'] == 'search_job_publication':
                require(not seen and data == receipt, 'search resume journal hash/anchor mismatch')
                seen = True
            else:
                require(seen and data['offset'] == offset, 'search resume publication offset mismatch')
            for copied in main[position + 1:]:
                if offset == len(journal):
                    break
                if copied != journal[offset]:
                    require(copied['stage'] in ('runtime_error', 'command_timing', 'STOP',
                            'resume-search', 'search_resume_plan', 'search_job_publication_continued'),
                            'search resume copied journal event mismatch')
                    break
                offset += 1
        elif event['stage'] == 'search_job_published':
            require(seen and not published and offset == len(journal), 'search resume incomplete publication marker')
            published = True
    return offset, published, seen


def current_search_finished(events, batch_id, restored):
    """Completion belongs to the latest publication and the results it saved."""
    start = max(i for i, event in enumerate(events)
                if event['stage'] == 'search_publication_started' and payload(event)['batch_id'] == batch_id)
    current = events[start + 1:]
    stages = ('search_publication_finished', 'search_phase_finished',
              'conflicts_and_robustness', 'awaiting_selection')
    positions = {event['stage']: i for i, event in enumerate(current) if event['stage'] in stages}
    if any(stage not in positions for stage in stages):
        return False
    order = [positions[stage] for stage in stages]
    if order != sorted(order):
        return False
    publication, phase, findings, selection = [payload(current[i]) for i in order]
    jobs = phase.get('jobs', [])
    if (publication.get('batch_id') != batch_id or phase.get('status') != 'complete' or
            [job.get('job_index') for job in jobs] != list(range(len(restored))) or
            any(job.get('status') != 'completed' or job.get('goal') != restored[i][0].target.to_dict()
                for i, job in enumerate(jobs))):
        return False
    analyses = findings.get('findings', {}).get('analyses', [])
    if len(analyses) != len(restored) // 2:
        return False
    for i, analysis in enumerate(analyses):
        if (analysis.get('target') != restored[2 * i][0].to_dict() or
                analysis.get('negated') != restored[2 * i + 1][0].to_dict()):
            return False
    route_ids = {route.id for result, _ in restored.values() for route in result.routes}
    return set(selection.get('route_ids', [])) == route_ids


def load_search_resume(log, bank, root):
    main = log.read()  # Includes the append-only tail anchor.
    def single(stage):
        rows = [payload(e) for e in main if e['stage'] == stage]
        require(len(rows) == 1, 'search resume requires one ' + stage)
        return rows[0]
    from ara.runtime.freeze_fork import effective_run
    run, frozen, candidates = effective_run(main), single('commitments_frozen'), single('candidates')
    require(run['bank_version'] == frozen['bank_version'] == bank.bank_version, 'search resume bank version mismatch')
    commitments = CommitmentSet.from_dict(frozen['commitments'])
    artifact = CommitmentSet.from_json((log.path.parent/'commitments.json').read_text())
    require(digest(artifact.to_json()) == digest(commitments.to_json()), 'search resume frozen T hash mismatch')
    # A corrupt optional catalogue must fail before resume can create a provider.
    from ara.runtime.search_alignment import catalogue_inputs
    catalogue_inputs(log.path.parent, commitments)
    targets = tuple(Proposition.from_dict(p) for p in candidates['candidates'])
    require(bool(targets) and len({p.id for p in targets}) == len(targets) and all(p.formula for p in targets),
            'search resume invalid targets')
    goals = [g for t in targets for g in (t, negate_proposition(t))]
    batches = [payload(e) for e in main if e['stage'] == 'search_publication_started']
    require(bool(batches) and len({b['batch_id'] for b in batches}) == len(batches), 'search resume invalid batch inventory')
    restored, publications, all_journal_events = {}, [], []
    directory = log.path.parent
    for batch in batches:
        bid = batch['batch_id']
        require(isinstance(bid, str) and len(bid) == 32 and all(c in '0123456789abcdef' for c in bid),
                'search resume invalid batch identity')
        require([j['job_index'] for j in batch['jobs']] == list(range(len(goals))) and
                [j['goal'] for j in batch['jobs']] == [g.to_dict() for g in goals],
                'search resume job target/order mismatch')
        for index, job in enumerate(batch['jobs']):
            expected = f'search-journals/{bid}/{index:04d}.jsonl'
            require(job['journal'] == expected, 'search resume journal path mismatch')
            path = directory/expected
            require(not any(p.is_symlink() for p in (path, path.with_suffix('.anchor'), path.parent, path.parent.parent)),
                    'search resume journal symlink refused')
            require(path.is_file() or any(e['stage'] == 'search_job_publication' and
                    payload(e).get('batch_id') == bid and payload(e).get('job_index') == index and
                    payload(e).get('event_count') == 0 for e in main),
                    'search resume missing journal; completion cannot be established')
            journal_log = EventLog(path)
            journal = journal_log.read()
            for e in journal:
                if e['stage'] in ('search_job_started', 'search_job_finished', 'search_job_failed', 'search_job_retry'):
                    require(payload(e)['job_index'] == index, 'search resume journal job identity mismatch')
            receipt = dict(batch_id=bid, job_index=index, journal=expected, event_count=len(journal),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest() if journal else None,
                anchor_sha256=hashlib.sha256(journal_log.anchor.read_bytes()).hexdigest() if journal else None)
            progress = publication_progress(main, bid, index, receipt, journal)
            recovered = restore_result(directory, journal, goals[index], commitments, bank, run['config'], root)
            if recovered is not None:
                require(index not in restored, 'search resume completed job was dispatched twice')
                restored[index] = recovered
            all_journal_events.extend(journal)
            publications.append((receipt, journal, progress))
    # Main settlement receipts live outside the immutable source journals.
    settlements = unsettled_receipts(all_journal_events + [e for e in main if payload(e).get('recovery') == 'resume-search'])
    finished = len(restored) == len(goals) and current_search_finished(main, batches[-1]['batch_id'], restored)
    return SearchResume(run, commitments, targets, restored, publications, settlements, finished)


def publish_search_resume(log, state):
    pending = []
    def record(stage, **data):
        pending.append(RunEvent(now(), stage, 'SYSTEM', payload_json=canonical(data)))
    for receipt, journal, (offset, published, seen) in state.publications:
        if published:
            continue
        if seen:
            record('search_job_publication_continued', batch_id=receipt['batch_id'],
                   job_index=receipt['job_index'], offset=offset)
        else:
            record('search_job_publication', **receipt)
        pending.extend(RunEvent.from_dict(e) for e in journal[offset:])
        record('search_job_published', batch_id=receipt['batch_id'], job_index=receipt['job_index'])
    finished = {payload(e)['batch_id'] for e in log.read() if e['stage'] == 'search_publication_finished'}
    for bid in dict.fromkeys(r['batch_id'] for r, _, _ in state.publications):
        if bid not in finished:
            record('search_publication_finished', batch_id=bid)
    pending.extend(state.settlements)
    if pending:
        log.emit_many(pending)
