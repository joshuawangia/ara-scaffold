import json
from pathlib import Path

import pytest

from ara.runtime.logging import EventLog, LogTampered
from ara.runtime.providers import MockProvider, MissingResponse
from ara.runtime.cache import canonical


def test_log_tamper_and_truncation(tmp_path):
    path = tmp_path / 'events.jsonl'
    log = EventLog(path)
    log.human('feedback', ' P\nQ ', reported_minutes=2)
    log.human('select', 'p')
    original = path.read_text()
    row = log.read()[0]
    assert row['label'] == 'HUMAN'
    assert json.loads(row['payload_json'])['text'] == ' P\nQ '
    assert row['timestamp']
    path.write_text(original.replace('feedback', 'feedbacX'))
    with pytest.raises(LogTampered):
        EventLog(path)
    path.write_text(original.splitlines(keepends=True)[0])
    with pytest.raises(LogTampered):
        EventLog(path)
    path.write_text(original)
    assert len(EventLog(path).read()) == 2


def test_missing_mock_is_loud():
    provider = MockProvider({})
    with pytest.raises(MissingResponse):
        provider.complete('formalise', 'P', None, 10)


def test_receipt_import_verification_does_not_grow_per_event(tmp_path, monkeypatch):
    from ara.runtime.provenance import checkpoint, import_receipts, verify_imports
    import ara.runtime.logging as logging
    source = EventLog(tmp_path/'source.jsonl')
    for n in range(40):
        source.record('P', index=n, text='Q' * 2000)
    events, origin = tuple(source.read()), checkpoint(source.path)
    target = EventLog(tmp_path/'target.jsonl')
    target.human('feedback', 'P')
    prefix = target.path.read_bytes()
    read_log = logging.read_log
    reads = []
    def counted(path):
        if Path(path) == target.path:
            reads.append(path)
        return read_log(path)
    monkeypatch.setattr(logging, 'read_log', counted)
    import_receipts(target, events, origin)
    assert len(reads) <= 3
    assert target.path.read_bytes().startswith(prefix)
    imported = target.read()
    assert imported[2:] == list(events)
    verify_imports(imported)
    saved = target.path.read_bytes()
    import_receipts(target, events, origin)
    assert target.path.read_bytes() == saved


def test_bulk_log_append_refuses_tamper_and_interrupted_write(tmp_path, monkeypatch):
    from ara.types import RunEvent
    log = EventLog(tmp_path/'events.jsonl')
    log.record('P')
    original = log.path.read_text()
    log.path.write_text(original.replace('"stage":"P"', '"stage":"Q"'))
    with pytest.raises(LogTampered):
        log.emit_many([RunEvent('a', 'R', 'SYSTEM')])
    log.path.write_text(original)
    open_path = Path.open
    class InterruptedAnchor:
        def __init__(self, stream):
            self.stream = stream
        def __enter__(self):
            return self
        def __exit__(self, *args):
            self.stream.close()
        def write(self, text):
            raise OSError('P')
    def interrupted(path, *args, **kwargs):
        stream = open_path(path, *args, **kwargs)
        if path == log.anchor and args and args[0] == 'a':
            return InterruptedAnchor(stream)
        return stream
    with monkeypatch.context() as patch:
        patch.setattr(Path, 'open', interrupted)
        with pytest.raises(OSError, match='P'):
            log.emit_many([RunEvent('a', 'R', 'SYSTEM')])
    # A failed append is never silently repaired or reported as success.
    assert log.path.read_text() != original
    with pytest.raises(LogTampered):
        log.read()
