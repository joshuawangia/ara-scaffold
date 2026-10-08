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
