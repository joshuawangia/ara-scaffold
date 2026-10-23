"""Persistent lineage proofs retain native verification and exact receipts; P/Q only."""
import json
from pathlib import Path

import pytest

from ara.runtime.cache import Cache, canonical
from ara.runtime.calls import ModelCalls
from ara.runtime.extraction import extract, resume_papers
from ara.runtime.logging import EventLog
from test_extraction import ROOT, accounting, offline, register, rig


def chain(rig, tmp_path):
    calls, provider, papers, *_ = rig
    register(calls, provider, papers[0])
    original = extract(calls, papers[:1])
    log = EventLog(tmp_path/'derived/events.jsonl')
    reuse = resume_papers(log, papers[:1], [original.parent], calls.config, ROOT)
    follow = ModelCalls(calls.config, provider, log, Cache(tmp_path/'derived/cache'), ROOT, '')
    artifact = extract(follow, papers[:1], reused=reuse, salvage_only=True)
    return artifact, calls.log.path


def decision(log):
    return [json.loads(e['payload_json']) for e in log.read() if e['stage']=='lineage_verification'][-1]


def test_native_startup_reuses_chained_receipt_without_reverification(rig, tmp_path, monkeypatch):
    from ara.runtime import verification
    from ara.runtime.cli import main
    artifact, ancestor = chain(rig, tmp_path)
    calls, _, _, _, _, config = rig
    def ready(cfg, log, topic):
        assert accounting(log)['extraction']['extracted'] == ['p']
        raise Ready()
    class Ready(BaseException): pass
    for n in range(2):
        log = tmp_path/f'pilot{n}'
        if n:
            monkeypatch.setattr(verification, 'literature_provenance',
                                lambda *a, **kw: pytest.fail('unchanged lineage was fully reverified'))
        with pytest.raises(Ready):
            main(['run','--config',str(config),'--topic','P','--literature',str(artifact),
                  '--run-dir',str(log)],calls_factory=ready)
        receipt = decision(EventLog(log/'events.jsonl'))
        assert receipt['mode'] == ('full' if n==0 else 'reused')
        data=receipt['receipt']
        assert data['result']=='verified' and data['verifier']['version']
        expected={str(p.resolve()) for p in (artifact,artifact.with_suffix('.provenance.json'),ancestor,
                  ancestor.with_suffix('.anchor'), artifact.parent/'events.jsonl',artifact.parent/'events.anchor')}
        assert expected <= data['files'].keys()
        assert all(len(sha)==64 for sha in data['files'].values())
        assert receipt['receipt_log']['last_hash']
    assert (tmp_path/'pilot0/events.jsonl').read_bytes() != (tmp_path/'pilot1/events.jsonl').read_bytes()


@pytest.mark.parametrize('damage', ['ancestor', 'ancestor_anchor', 'source', 'source_anchor', 'sidecar', 'artifact', 'header', 'malformed_sidecar', 'missing_sidecar', 'missing', 'symlink'])
def test_changed_input_forces_full_verification_and_refuses(rig, tmp_path, monkeypatch, damage):
    from ara.runtime import verification
    artifact, ancestor = chain(rig,tmp_path)
    if damage=='symlink':
        saved=ancestor.with_name('saved.jsonl')
        ancestor.rename(saved)
        ancestor.symlink_to(saved)
    cache=tmp_path/'verification-cache'
    verification.import_literature(EventLog(tmp_path/'first/events.jsonl'),artifact,artifact.read_text(),cache)
    paths=dict(ancestor=ancestor,ancestor_anchor=ancestor.with_suffix('.anchor'),source=artifact.parent/'events.jsonl',
               source_anchor=artifact.parent/'events.anchor',sidecar=artifact.with_suffix('.provenance.json'),
               artifact=artifact,header=artifact,malformed_sidecar=artifact.with_suffix('.provenance.json'),
               missing_sidecar=artifact.with_suffix('.provenance.json'),missing=ancestor,symlink=ancestor)
    path=paths[damage]
    if damage=='symlink':
        bad=ancestor.with_name('bad.jsonl')
        bad.write_bytes(ancestor.read_bytes()+b'P')
        ancestor.unlink();ancestor.symlink_to(bad)
    elif damage in ('missing','missing_sidecar'):path.unlink()
    elif damage=='header':path.write_text(path.read_text().replace('# ARA extracted literature v2','P',1))
    elif damage=='malformed_sidecar':path.write_bytes(b'P')
    elif damage=='artifact':path.write_text(path.read_text().replace('P P P','Q Q Q'))
    elif damage=='sidecar':
        data=json.loads(path.read_text());data['last_hash']='0'*64;path.write_text(canonical(data))
    elif 'anchor' in damage:path.write_text('0'*64+'\n')
    else:path.write_text(path.read_text().replace('"stage":','"stageX":',1))
    full=verification.literature_provenance
    seen=[]
    def tracked(*args,**kwargs):
        seen.append(True);return full(*args,**kwargs)
    monkeypatch.setattr(verification,'literature_provenance',tracked)
    destination=EventLog(tmp_path/'refused/events.jsonl')
    with pytest.raises((ValueError,OSError)):
        verification.import_literature(destination,artifact,artifact.read_text(),cache)
    assert seen == [True]
    assert not any(e['stage']=='extraction_provenance_import' for e in destination.read())


@pytest.mark.parametrize('change',['receipt','receipt_anchor','version','valid_append'])
def test_invalid_cache_or_changed_valid_input_is_fully_reverified(rig,tmp_path,monkeypatch,change):
    from ara.runtime import verification
    artifact,ancestor=chain(rig,tmp_path)
    cache=tmp_path/'verification-cache'
    first=EventLog(tmp_path/'first/events.jsonl')
    verification.import_literature(first,artifact,artifact.read_text(),cache)
    pin=decision(first)['receipt_log']
    if change.startswith('receipt'):
        path=Path(pin['source_log'])
        if change=='receipt_anchor':path=path.with_suffix('.anchor')
        path.write_bytes(path.read_bytes()+b'P')
    elif change=='version':monkeypatch.setattr(verification,'VERSION','changed')
    else:EventLog(ancestor).record('P',text='Q')
    full=verification.literature_provenance;seen=[]
    def tracked(*args,**kwargs):seen.append(True);return full(*args,**kwargs)
    monkeypatch.setattr(verification,'literature_provenance',tracked)
    second=EventLog(tmp_path/'second/events.jsonl')
    verification.import_literature(second,artifact,artifact.read_text(),cache)
    assert seen==[True] and decision(second)['mode']=='full'
    assert accounting(first)['inherited_totals']==accounting(second)['inherited_totals']


@pytest.mark.parametrize('phase', ['full', 'warm'])
def test_input_changed_during_verification_is_refused(rig, tmp_path, monkeypatch, phase):
    from ara.runtime import verification
    artifact, ancestor = chain(rig, tmp_path)
    cache = tmp_path/'verification-cache'
    if phase == 'warm':
        verification.import_literature(EventLog(tmp_path/'first/events.jsonl'), artifact, artifact.read_text(), cache)
    name = 'literature_provenance' if phase == 'full' else 'pinned_events'
    original = getattr(verification, name)
    def changed(*args, **kwargs):
        result = original(*args, **kwargs)
        ancestor.write_bytes(ancestor.read_bytes() + b'P')
        return result
    monkeypatch.setattr(verification, name, changed)
    destination = EventLog(tmp_path/'refused/events.jsonl')
    with pytest.raises(ValueError):
        verification.import_literature(destination, artifact, artifact.read_text(), cache)
    assert not destination.read()
