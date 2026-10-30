"""Verified pre-freeze copies for a new hypothesis lifecycle, never reconstruction."""
from pathlib import Path
from contextlib import nullcontext
import fcntl
import json
import os
import tempfile

from ara.runtime.alignment_resume import _load_alignment_resume
from ara.runtime.cache import digest
from ara.runtime.calls import require
from ara.runtime.hypotheses import required_symbols, validate_hypothesis_config
from ara.runtime.logging import EventLog, read_log
from ara.types import CommitmentSet


def separate_destination(source, destination):
    source, destination = Path(source).resolve(), Path(destination).absolute()
    require(not destination.resolve().is_relative_to(source) and not source.is_relative_to(destination.resolve()),
            'construction fork destination must be separate from source')
    require(not destination.is_symlink() and (not destination.exists() or
            (destination.is_dir() and not any(destination.iterdir()))), 'construction fork destination must be empty')
    return source, destination


def inspect_construction_fork(source, destination, bank, hypotheses):
    """Read-only plan: validate retained construction, accepted judgments and freeze."""
    source,destination=separate_destination(source,destination)
    validate_hypothesis_config(dict(hypothesis_premises=hypotheses))
    require(bool(hypotheses),'construction fork requires proposed hypotheses')
    path=source/'events.jsonl'
    lock=source/'events.lock'
    with lock.open('rb') if lock.exists() else nullcontext() as stream:
        if stream is not None:fcntl.flock(stream,fcntl.LOCK_SH)
        raw=path.read_bytes();records=read_log(path)
        anchor=(source/'events.anchor').read_bytes()
    require(anchor.decode().splitlines()==[r['hash'] for r in records], 'construction fork anchor mismatch')
    lines=raw.splitlines(keepends=True)
    require(len(lines)==len(records) and all(json.loads(line)==row for line,row in zip(lines,records)),
            'construction fork source changed during verification')
    events=[r['event'] for r in records]
    boundary={'symbol_alignment_applied','symbol_alignment_refused','hypotheses_requested',
              'symbol_catalogue_frozen','commitment_provenance_frozen','commitments_frozen',
              'search_started','run_finished'}
    count=next((i for i,e in enumerate(events) if e['stage'] in boundary),len(events))
    state=_load_alignment_resume(source,events[:count],bank)
    plan_id=state['plan_id']
    artifacts={name:p.read_bytes() for p in source.iterdir() if p.is_file() and
        ((name:=p.name)==f'build-t-plan-{plan_id}.json' or name==f'working-t-{plan_id}.json' or
         (name.startswith(f'build-t-{plan_id}-') and name.endswith('.json')))}
    expected=None
    freezes=[json.loads(e['payload_json']) for e in events if e['stage']=='commitments_frozen']
    if freezes:
        require(len(freezes)==1 and freezes[0]['bank_version']==bank.bank_version,'construction fork freeze mismatch')
        from ara.runtime.frozen_catalogue import validate_frozen_artifact
        from ara.runtime.commitment_provenance import load_commitment_provenance
        t=CommitmentSet.from_json((source/'commitments.json').read_text())
        require(t.to_dict()==freezes[0]['commitments'],'construction fork commitments mismatch')
        catalogue=validate_frozen_artifact(json.loads((source/'frozen-t.json').read_text()),t)
        meta=load_commitment_provenance(source,t,catalogue)
        require(meta is not None,'construction fork requires verified source provenance')
        for stage,value in [('symbol_catalogue_frozen',catalogue),('commitment_provenance_frozen',meta)]:
            require([json.loads(e['payload_json']) for e in events if e['stage']==stage]==[value],
                    'construction fork frozen metadata receipt mismatch')
        symbols,rows=catalogue['symbols'],meta['commitments']
        if meta.get('hypotheses') is not None:
            from ara.runtime.hypotheses import validate_hypotheses
            t,symbols,rows=validate_hypotheses(meta['hypotheses'],t,symbols,rows)
        alignment=meta.get('alignment')
        if alignment is not None:
            require(alignment['original_commitments']==state['commitments'].to_dict() and
                    alignment['original_symbols']==state['symbols'] and
                    alignment['judgments']==state['judgments'] and
                    alignment.get('unresolved',[])==state['unresolved'],
                    'construction fork alignment does not match completed construction receipts')
        else:
            validate_restored_source(dict(commitments=t.to_dict(),symbols=symbols,provenance=rows),
                                     state['commitments'],state['symbols'],state['provenance'])
        expected=dict(commitments=t.to_dict(),symbols=symbols,provenance=rows)
        for value in hypotheses:required_symbols(value,symbols)
    elif any((source/name).exists() for name in ('commitments.json','frozen-t.json','commitment-provenance.json')):
        raise ValueError('construction fork refuses partial freeze artifacts')
    else:
        for value in hypotheses:required_symbols(value,state['symbols'])
    prefix=b''.join(lines[:count])
    receipt=dict(source_run=str(source),source_tail=records[-1]['hash'],records=count,
        prefix_sha256=digest(prefix.decode()),
        artifacts={name:digest(data.decode()) for name,data in artifacts.items()},
        hypotheses=hypotheses,expected_source=expected,cache_dir=str(destination.resolve()/'cache'),
        note='New lifecycle imports completed construction and accepted alignment only; hypotheses precede its single freeze.')
    with path.open('rb') as stream:
        unchanged_prefix=stream.read(len(prefix))==prefix
    prefix_anchor=''.join(r['hash']+'\n' for r in records[:count]).encode()
    with (source/'events.anchor').open('rb') as stream:
        unchanged_anchor=stream.read(len(prefix_anchor))==prefix_anchor
    require(unchanged_prefix and unchanged_anchor and
            all((source/name).read_bytes()==data for name,data in artifacts.items()),
            'construction fork source changed during verification')
    state['run']={**state['run'],'config':{**state['run']['config'],'hypothesis_premises':hypotheses,'cache_dir':receipt['cache_dir']}}
    state['expected_source']=expected
    return dict(state=state,receipt=receipt,artifacts=artifacts,records=records[:count],
                prefix=prefix,destination=destination)


def write_construction_fork(plan):
    """Publish an already verified prefix; incomplete attempts remain inspectable."""
    destination=plan['destination']
    separate_destination(plan['receipt']['source_run'],destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    temporary=Path(tempfile.mkdtemp(prefix='.construction-fork-',dir=destination.parent))
    (temporary/'events.jsonl').write_bytes(plan['prefix'])
    (temporary/'events.anchor').write_text(''.join(r['hash']+'\n' for r in plan['records']))
    for name,data in plan['artifacts'].items():(temporary/name).write_bytes(data)
    log=EventLog(temporary/'events.jsonl')
    log.record('construction_forked',**plan['receipt'])
    os.rename(temporary,destination)
    return EventLog(destination/'events.jsonl')


def validate_restored_source(expected, commitments, symbols, rows):
    """H admission may append a premise but never rewrite the imported source T."""
    from ara.runtime.frozen_catalogue import make_catalogue
    original=CommitmentSet.from_dict(expected['commitments'])
    require(commitments==original and rows==expected['provenance'] and
            make_catalogue(commitments,symbols)==make_catalogue(original,expected['symbols']),
            'construction fork changed source commitments, provenance or catalogue')
