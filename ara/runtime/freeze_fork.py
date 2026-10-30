"""Copy an authenticated immutable freeze prefix without touching the source run."""
from contextlib import nullcontext
import fcntl
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import tempfile

from ara.runtime.logging import EventLog, read_log, LogTampered
from ara.runtime.frozen_catalogue import validate_frozen_artifact
from ara.types import CommitmentSet


def effective_run(events):
    starts = [json.loads(e['payload_json']) for e in events if e['stage']=='run_started']
    if len(starts)!=1:
        raise ValueError('requires one run configuration')
    run = starts[0]
    for event in events:
        if event['stage']=='construction_forked':
            payload=json.loads(event['payload_json'])
            run={**run,'config':{**run['config'],**payload.get('consolidation_config',{}),'hypothesis_premises':payload['hypotheses'],'cache_dir':payload['cache_dir']}}
        elif event['stage']=='freeze_fork_configuration':
            run={**run,'config':json.loads(event['payload_json'])['config']}
    return run


def fork_from_freeze(source, destination, bank):
    source, destination = Path(source).resolve(), Path(destination).absolute()
    if destination.resolve().is_relative_to(source) or source.is_relative_to(destination.resolve()):
        raise ValueError('fork destination must be separate from source')
    if destination.is_symlink() or (destination.exists() and (not destination.is_dir() or any(destination.iterdir()))):
        raise ValueError('fork destination must be empty')
    path = source/'events.jsonl'
    lock = source/'events.lock'
    with lock.open('rb') if lock.exists() else nullcontext() as stream:
        if stream is not None:
            fcntl.flock(stream,fcntl.LOCK_SH)
        rows = read_log(path)
        if (source/'events.anchor').read_text().splitlines() != [r['hash'] for r in rows]:
            raise LogTampered('fork source anchor mismatch')
        freezes = [r for r in rows if r['event']['stage']=='commitments_frozen']
        if len(freezes)!=1:
            raise ValueError('fork requires one freeze event')
        freeze = freezes[0]
        count = freeze['seq']+1
        events = [r['event'] for r in rows[:count]]
        run = effective_run(events)
        frozen = json.loads(freeze['event']['payload_json'])
        if run['bank_version'] != bank.bank_version or frozen['bank_version'] != bank.bank_version:
            raise ValueError('fork bank version mismatch')
        commitments = CommitmentSet.from_dict(frozen['commitments'])
        artifacts = {'commitments.json':(source/'commitments.json').read_bytes()}
        if CommitmentSet.from_json(artifacts['commitments.json'].decode()).to_dict()!=commitments.to_dict():
            raise ValueError('fork frozen commitments mismatch')
        catalogue = None
        if (source/'frozen-t.json').exists():
            artifacts['frozen-t.json']=(source/'frozen-t.json').read_bytes()
            catalogue = validate_frozen_artifact(json.loads(artifacts['frozen-t.json']),commitments)
            receipts=[json.loads(e['payload_json']) for e in events if e['stage']=='symbol_catalogue_frozen']
            if receipts != [catalogue]:
                raise ValueError('fork frozen catalogue receipt mismatch')
        elif any(e['stage']=='symbol_catalogue_frozen' for e in events):
            raise ValueError('fork frozen catalogue artifact missing')
        from ara.runtime.commitment_provenance import load_commitment_provenance
        provenance = load_commitment_provenance(source, commitments, catalogue)
        receipts = [json.loads(e['payload_json']) for e in events if e['stage']=='commitment_provenance_frozen']
        if receipts != ([provenance] if provenance is not None else []):
            raise ValueError('fork commitment provenance receipt mismatch')
        if provenance is not None:
            artifacts['commitment-provenance.json'] = (source/'commitment-provenance.json').read_bytes()
        lines = path.read_bytes().splitlines(keepends=True)
        prefix = b''.join(lines[:count])
        # Detect a source rewrite even if it did not cooperate with the lock.
        if len(lines) != len(rows) or any(json.loads(line) != row for line,row in zip(lines,rows)):
            raise LogTampered('fork source changed during verification')
    destination.parent.mkdir(parents=True,exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix='.freeze-fork-',dir=destination.parent))
    try:
        (temporary/'events.jsonl').write_bytes(prefix)
        (temporary/'events.anchor').write_text(''.join(r['hash']+'\n' for r in rows[:count]))
        for name,content in artifacts.items():
            (temporary/name).write_bytes(content)
        log = EventLog(temporary/'events.jsonl')
        log.record('freeze_forked', source_run=str(source), records=count, freeze_hash=freeze['hash'],
                   prefix_sha256=sha256(prefix).hexdigest(), artifacts={name:sha256(value).hexdigest() for name,value in artifacts.items()},
                   note='Exact source prefix through freeze, counted once as imported history; no targets or search receipts copied.')
        os.rename(temporary,destination)
    except BaseException:
        shutil.rmtree(temporary)
        raise
    return EventLog(destination/'events.jsonl'),run,commitments
