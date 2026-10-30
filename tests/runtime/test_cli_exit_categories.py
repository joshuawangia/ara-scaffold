"""Sanitized transport diagnostics through the native isolated fake CLI."""
import json
from pathlib import Path

import pytest

from ara.runtime.calls import Rejected
from ara.runtime.cli import make_calls
from ara.runtime.logging import EventLog
from ara.types import Proposition
from test_codex_cli import codex


@pytest.mark.parametrize('channel', ['stderr', 'event', 'plain_stdout'])
@pytest.mark.parametrize('message,category,code', [
    ('Your input exceeds the context window of this model.', 'context_length', 'cli_invalid_request'),
    ('Maximum context length is 272000 tokens.', 'context_length', 'cli_invalid_request'),
    ('context_length_exceeded', 'context_length', 'cli_invalid_request'),
    ('The prompt is too long.', 'context_length', 'cli_invalid_request'),
    ('HTTP 429 Too Many Requests', 'rate_limit', 'cli_usage_limit'),
    ('Please log in again: session expired.', 'auth', 'cli_auth_error'),
    ('P Q', 'other', 'cli_exit_error'),
    ('Configured context window: 272000 tokens.', 'other', 'cli_exit_error'),
])
def test_exit_categories_are_sanitized_and_context_is_not_retried(codex, message, category, code, channel):
    config, _, _, tmp = codex
    config['codex_cli']['retries'] = 1
    binary = Path(config['codex_cli']['binary'])
    diagnostic = message + ' PRIVATE_CONTEXT_SENTINEL offline-access'
    action = ("emit({'type':'turn.failed','error':{'message':" + repr(diagnostic) + "}})"
              if channel == 'event' else 'print(' + repr(diagnostic) + ',file=sys.' + ('stderr' if channel == 'stderr' else 'stdout') + ')')
    injection = 'if not canary:\n ' + action + '\n sys.exit(1)\n'
    anchor = "emit({'type':'turn.started','model':arg('-m')})\n"
    source = binary.read_text(); assert source.count(anchor) == 1
    binary.write_text(source.replace(anchor, anchor + injection))
    log = EventLog(tmp/'events.jsonl')
    calls = make_calls(config, log, 'P')
    with pytest.raises(Rejected, match=code):
        calls.formalise(Proposition('p', 'P'))
    text = log.path.read_text()
    assert diagnostic not in text and 'PRIVATE_CONTEXT_SENTINEL' not in text and 'offline-access' not in text
    models = [json.loads(e['payload_json']) for e in log.read() if e['stage']=='formalise' and e['label']=='MODEL']
    assert len(models) == (1 if category == 'context_length' else 2)
    assert all(row['cli']['error_category'] == category for row in models)
    assert all(row['cli']['exit_status'] == 1 and row['cli']['failure_class'] == code for row in models)
    assert all(row['accounting'] == 'reservation_unknown_actual' for row in models)
    assert not list((tmp/'cache').rglob('*.json'))
    if category == 'context_length':
        assert not any('retry' in e['stage'] for e in log.read())
