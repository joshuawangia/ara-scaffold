"""Pinned origin prefixes and verified, transitive receipt imports."""
from pathlib import Path
import json

from ara.runtime.cache import canonical, digest
from ara.runtime.logging import read_log
from ara.types import RunEvent

IMPORT_STAGE = 'extraction_provenance_import'


def checkpoint(path, records=None):
    if records is None:
        records = read_log(path)
        anchor = Path(path).with_suffix('.anchor')
        if anchor.read_text().splitlines() != [r['hash'] for r in records]:
            raise ValueError('origin log/checkpoint mismatch')
    if not records:
        raise ValueError('origin receipt requires a nonempty log')
    return dict(source_log=str(Path(path).resolve()), records=len(records), last_hash=records[-1]['hash'])


def read_checkpoint(origin, active=frozenset(), memo=None):
    memo = {} if memo is None else memo
    key = canonical(origin)
    if key in active:
        raise ValueError('cyclic origin receipt')
    if key in memo:
        return memo[key]
    count = origin['records']
    rows = read_log(Path(origin['source_log']))
    if type(count) is not int or count <= 0 or len(rows) < count or rows[count-1]['hash'] != origin['last_hash']:
        raise ValueError('extraction provenance checkpoint mismatch')
    events = tuple(row['event'] for row in rows[:count])
    verify_imports(events, active | {key}, memo)
    memo[key] = events
    return events


def unique_events(events, seen):
    """Copied original events retain timestamp, provider response ID and charge."""
    result = []
    seen = set(seen)
    for event in events:
        if event['stage'] == IMPORT_STAGE:
            continue
        identity = digest(canonical(event))
        if identity not in seen:
            seen.add(identity)
            result.append(event)
    return result


def verify_imports(events, active=frozenset(), memo=None):
    seen = set()
    for index, event in enumerate(events):
        if event['stage'] == IMPORT_STAGE:
            data = json.loads(event['payload_json'])
            count = data['records']
            if type(count) is not int or count < 0 or index + count >= len(events):
                raise ValueError('incomplete origin receipt import')
            copied = tuple(events[index+1:index+1+count])
            if 'origin' in data:
                original = read_checkpoint(data['origin'], active, memo)
                if data['receipt_id'] != digest(canonical(original)) or list(copied) != unique_events(original, seen):
                    raise ValueError('origin receipt import does not match pinned events')
            elif data.get('receipt_id') != digest(canonical(copied)):
                raise ValueError('legacy origin receipt import mismatch')
        else:
            seen.add(digest(canonical(event)))


def import_receipts(log, events, origin=None):
    verify_imports(events)
    receipt_id = digest(canonical(events))
    existing = log.read()
    if origin is not None and tuple(events) != read_checkpoint(origin):
        raise ValueError('origin receipt events mismatch')
    if any(e['stage'] == IMPORT_STAGE and json.loads(e['payload_json']).get('receipt_id') == receipt_id
           for e in existing):
        return
    # Legacy callers supply a validated artifact prefix without its sidecar. Keep
    # that complete prefix intact; native resume/import supplies the origin pin.
    copied = list(events) if origin is None else unique_events(events, {
        digest(canonical(e)) for e in existing if e['stage'] != IMPORT_STAGE})
    log.record(IMPORT_STAGE, records=len(copied), receipt_id=receipt_id,
               **({'origin': origin} if origin is not None else {}),
               note='Original receipts, not new dispatches; inherited charges count in this run.')
    for event in copied:
        log.emit(RunEvent.from_dict(event))


def batch_events(events):
    start = next((i for i in range(len(events)-1, -1, -1)
                  if events[i]['stage'] == 'extraction_batch_started'), 0)
    return events[start:]


def historical_extraction_outcomes(events):
    """All retained outcomes, including ancestors; caller must verify imports first.

    This is a candidate inventory, not proof of compatibility or completion.
    resume_papers applies source/policy checks and accepted-graph receipts.
    """
    return [json.loads(e['payload_json']) for e in events if e['stage'] == 'extraction_outcome']


def extraction_outcomes(events):
    """Current published corpus only; never use this as the reusable-success index."""
    return historical_extraction_outcomes(batch_events(events))
