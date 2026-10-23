"""Restore only logged, hash-verified construction outcomes from a terminal stop."""
from __future__ import annotations

import json
import fcntl
from contextlib import contextmanager

from ara.runtime.cache import canonical, digest
from ara.runtime.calls import require
from ara.types import CommitmentSet


def load_construction_resume(calls):
    events = calls.log.read()  # Verifies the append-only chain and tail anchor.
    require(not any(e['stage'] in ('commitments_frozen', 'search_started', 'run_finished') for e in events),
            'construction resume requires an unfrozen stopped run')
    plans = [(n, json.loads(e['payload_json'])) for n, e in enumerate(events) if e['stage'] == 'build_t_plan']
    require(len(plans) == 1, 'construction resume requires one recorded plan')
    offset, recorded = plans[0]
    plan, plan_id = recorded['plan'], recorded['plan_id']
    require(digest(canonical(plan)) == plan_id, 'construction resume plan hash mismatch')
    directory = calls.log.path.parent
    require(json.loads((directory / f'build-t-plan-{plan_id}.json').read_text()) == plan,
            'construction resume plan artifact mismatch')
    completed, closures, corrections = {}, {}, dict(select_t_roots=0, build_t_batch=0)
    pending = None
    terminal = None
    for event in events[offset + 1:]:
        stage, data = event['stage'], json.loads(event['payload_json'])
        if stage == 'construction_targeted_correction':
            corrections[data['kind']] += 1
        if stage == 'build_t_closure':
            require(data['plan_id'] == plan_id, 'construction resume closure plan mismatch')
            closures[data['index']] = {k: v for k, v in data.items() if k not in ('plan_id', 'index')}
        if stage == 'call_start':
            require(pending is None, 'construction resume has overlapping dispatches')
            pending = dict(start=data, diagnostic=None)
        elif stage == 'provider_error' and pending is not None:
            pending['diagnostic'] = data
        elif event['label'] == 'MODEL' and not data.get('cache_hit'):
            require(pending is not None and pending['start']['cache_key'] == data.get('cache_key') and
                    pending['start']['kind'] == stage, 'construction resume unmatched model receipt')
            terminal = dict(**pending, event=event, receipt=data)
            pending = None
        if stage not in ('build_t_batch_accepted', 'build_t_batch_skipped'):
            continue
        index = data['index']
        require(data['plan_id'] == plan_id and index not in completed, 'construction resume duplicate or foreign batch')
        if 'reason' in data:
            expected = {k: v for k, v in data.items() if k not in ('plan_id', 'index')}
            name = f'build-t-{plan_id}-{index}-skipped-{digest(canonical(expected))}.json'
        else:
            name = f'build-t-{plan_id}-{index}.json'
            expected = None
        content = (directory / name).read_text()
        receipt = json.loads(content)
        require(receipt['omitted'] == data['omitted'], 'construction resume omission mismatch')
        if stage == 'build_t_batch_accepted':
            require(digest(content) == data['output_hash'], 'construction resume batch hash mismatch')
            commitments = CommitmentSet.from_dict({'commitments': receipt['commitments']})
            require([c.id for c in commitments.commitments] == data['evidence_ids'], 'construction resume evidence mismatch')
        else:
            require(receipt == (expected if expected is not None else dict(omitted=data['omitted'], closure=closures[index])),
                    'construction resume skipped receipt mismatch')
        completed[index] = receipt
    require(pending is None, 'construction resume refuses interrupted dispatch without terminal receipt')
    require(sorted(completed) == list(range(len(completed))), 'construction resume has missing batch outcomes')
    index = len(completed)
    require(index < len(plan['batches']) and terminal is not None, 'construction resume requires a terminal window refusal')
    start, receipt, diagnostic = terminal['start'], terminal['receipt'], terminal['diagnostic'] or {}
    inputs = json.loads(start['prompt'].split('\nINPUT_JSON\n')[1])
    require(start['kind'] in ('select_t_roots', 'build_t_batch') and
            inputs.get('plan_id') == plan_id and inputs.get('batch_index') == index,
            'construction resume terminal window mismatch')
    require(receipt.get('accounting') == 'reservation_unknown_actual' and
            receipt.get('reason') in ('APIStatusError', 'BadRequestError', 'RequestTooLargeError') and
            diagnostic.get('kind') == start['kind'] and
            diagnostic.get('error_type') in ('invalid_request_error', 'request_too_large') and
            (diagnostic.get('http_status') is None or 400 <= diagnostic['http_status'] < 500) and
            bool(diagnostic.get('request_id')) and terminal['event']['response'] is None and
            terminal['event']['usage'] == start['reserved_usage'],
            'construction resume requires a finalized provider request refusal counted at reservation')
    require(calls.config.get('unknown_usage_policy') == 'count-at-reservation',
            'construction resume requires count-at-reservation policy')
    return dict(plan_id=plan_id, plan=plan, completed=completed, terminal_index=index,
                terminal_closure=closures.get(index), terminal_receipt=digest(canonical(terminal['event'])),
                corrections=corrections)


@contextmanager
def construction_resume_lock(directory):
    with (directory / 'construction-resume.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError('construction resume already running') from exc
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)
