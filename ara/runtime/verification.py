"""Persist verified extraction lineage; reuse only byte-identical inputs."""
from hashlib import file_digest, sha256
import json
from pathlib import Path
import platform
import time
import uuid

from ara.runtime.cache import canonical, digest
from ara.runtime.extraction import HEADER, literature_provenance
from ara.runtime.logging import EventLog, read_log
from ara.runtime.provenance import _append_receipts, checkpoint

VERSION = 'extraction-lineage-verifier-v1'


def file_hash(path):
    with Path(path).open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


def verifier_identity():
    root = Path(__file__).resolve().parents[1]
    files = ('types.py', 'runtime/cache.py', 'runtime/logging.py', 'runtime/provenance.py',
             'runtime/extraction.py', 'runtime/verification.py')
    return dict(version=VERSION, python=platform.python_version(),
                code_sha256={name: file_hash(root/name) for name in files})


def matching_inputs(files):
    return all(file_hash(path) == checksum for path, checksum in files.items())


def load_receipt(path):
    rows = read_log(path)
    if (path.read_bytes() != ''.join(canonical(r) + '\n' for r in rows).encode() or
            path.with_suffix('.anchor').read_bytes() != ''.join(r['hash'] + '\n' for r in rows).encode()):
        raise ValueError('verification receipt anchor mismatch')
    if len(rows) != 1 or rows[0]['event']['stage'] != 'lineage_verified':
        raise ValueError('invalid verification receipt')
    return json.loads(rows[0]['event']['payload_json']), checkpoint(path, rows)


def pinned_events(origin, expected_hash):
    events = []
    hasher = sha256()
    with Path(origin['source_log']).open('rb') as stream:
        for n, line in enumerate(stream):
            hasher.update(line)
            if n < origin['records']:
                row = json.loads(line)
                events.append(row['event'])
                last = row['hash']
    if (hasher.hexdigest() != expected_hash or len(events) != origin['records'] or
            last != origin['last_hash']):
        raise ValueError('verified source changed while loading')
    return tuple(events)


def import_literature(log, path, text, cache_dir):
    """Verify and import before a pilot can construct its model boundary."""
    path = Path(path).resolve()
    sidecar = path.with_suffix('.provenance.json')
    verifier = verifier_identity()
    directory = Path(cache_dir) / digest(str(path))
    candidates = sorted(directory.glob('receipt-*.jsonl'))
    if not text.startswith(HEADER) and not sidecar.exists() and not candidates:
        return literature_provenance(path, text)
    receipt, pin, events = None, None, None
    reason = 'missing_receipt'
    try:
        origin = json.loads(sidecar.read_bytes())
    except (OSError, ValueError):
        origin = None
        reason = 'invalid_origin'
    if candidates:
        try:
            candidate, candidate_pin = load_receipt(candidates[-1])
            files = candidate['files']
            required = {str(path), str(sidecar), str(Path(origin['source_log']).absolute()),
                        str(Path(origin['source_log']).with_suffix('.anchor').absolute())}
            if (candidate['verifier'] != verifier or candidate['result'] != 'verified' or
                    candidate['artifact'] != str(path) or candidate['origin'] != origin or
                    not required <= files.keys() or files[str(path)] != digest(text)):
                reason = 'receipt_binding_changed'
            elif not matching_inputs(files):
                reason = 'input_hash_changed'
            else:
                events = pinned_events(origin, files[str(Path(origin['source_log']).absolute())])
                if digest(canonical(events)) != candidate['events_sha256'] or not matching_inputs(files):
                    raise ValueError('verified inputs changed while loading')
                receipt, pin = candidate, candidate_pin
        except (OSError, ValueError, KeyError, TypeError):
            reason = 'invalid_receipt_or_changed_input'
            events = None
    mode = 'reused' if receipt is not None else 'full'
    if receipt is None:
        files = {}
        events = literature_provenance(path, text, inputs=files)
        if not events:
            raise ValueError('extracted literature header was modified')
        if not matching_inputs(files) or json.loads(sidecar.read_bytes()) != origin:
            raise ValueError('lineage changed during verification')
        receipt = dict(verifier=verifier, result='verified', artifact=str(path), origin=origin,
                       files=files, events_sha256=digest(canonical(events)))
        proof = EventLog(directory / f'receipt-{time.time_ns()}-{uuid.uuid4().hex}.jsonl')
        proof.record('lineage_verified', **receipt)
        pin = checkpoint(proof.path)
    log.record('lineage_verification', mode=mode, reason=reason if mode == 'full' else 'all_hashes_match',
               receipt=receipt, receipt_sha256=digest(canonical(receipt)), receipt_log=pin)
    _append_receipts(log, events, origin)
    return events
