"""Kappa4 W1: imported content must be screened before persistence or dispatch."""
import json

import pytest

from ara.runtime.cli import make_calls
from ara.runtime.budget import BudgetStop
from ara.runtime.claude_code import ClaudeCodeError
from ara.runtime.logging import EventLog
from ara.runtime.orchestration import compose
from test_calls import graph
from test_codex_cli import codex


def content_sensitive_auditor(tmp):
    binary = tmp/'fake-codex'
    source = binary.read_text()
    old = "value={k:'' for k in schema['properties']} if canary else {'formula':{'op':'atom','name':'P'}}"
    new = """value={k:'' for k in schema['properties']}
if not canary:
 data=json.loads(prompt.split('\\nINPUT_JSON\\n')[1])
 if 'sentences' in data:
  value={'labels':[{'sentence':s['sentence'],'node_ids':['n1'],'asserts_premise_or_inference_not_in_outline':'sentinel@example.invalid' in s['text']} for s in data['sentences']]}
 elif 'flagged_sentences' in data:
  value={'revisions':[{'sentence':s['sentence'],'text':''} for s in data['flagged_sentences']]}
 else: raise AssertionError('unexpected kind')
"""
    assert old in source
    binary.write_text(source.replace(old, new))


@pytest.mark.parametrize('field', ['body', 'title', 'bibliography', 'invalid'])
@pytest.mark.parametrize('sensitive,code', [
    ('sentinel@example.invalid', 'operator_identity_in_output'),
    ('offline-access', 'credential_in_cli_output'),
])
def test_resumed_draft_scan_before_any_effect(codex, field, sensitive, code):
    config, auth, write, tmp = codex
    config['essay_min_words'] = 0
    log = EventLog(tmp/'events.jsonl'); calls = make_calls(config, log, 'P')
    content_sensitive_auditor(tmp)
    draft = {'title':'P', 'body':'[[node:n1]] P P.', 'bibliography':[]}
    if field == 'body': draft['body'] += ' ' + sensitive + '.'
    elif field == 'title': draft['title'] = sensitive
    elif field == 'bibliography': draft['bibliography'] = [{'id':'p','text':sensitive,'url':None}]
    else: draft['unexpected'] = json.dumps({'P': sensitive})
    with pytest.raises(ClaudeCodeError, match=code): calls.provider.scan_output(draft)
    before_log = log.path.read_bytes()
    before_anchor = log.path.with_suffix('.anchor').read_bytes()
    # Existing artifacts must not be replaced even transiently by rejected input.
    artifact = tmp/'draft.unverified.json'; artifact.write_text('P')
    with pytest.raises(ClaudeCodeError, match=code): compose(calls, graph(), draft)
    assert log.path.read_bytes() == before_log
    assert log.path.with_suffix('.anchor').read_bytes() == before_anchor
    assert artifact.read_text() == 'P'
    assert not (tmp/'draft.json').exists() and not (tmp/'export').exists()
    assert not list((tmp/'cache').rglob('*.json'))
    assert sensitive not in log.path.read_text()


def test_clean_resumed_draft_reaches_native_audit(codex):
    config, auth, write, tmp = codex
    config['essay_min_words'] = 0
    log = EventLog(tmp/'events.jsonl'); calls = make_calls(config, log, 'P')
    content_sensitive_auditor(tmp)
    draft = {'title':'P', 'body':'[[node:n1]] P P.', 'bibliography':[]}
    # The fake supports the real audit; the later search response is intentionally absent.
    with pytest.raises(BudgetStop, match='token cap'): compose(calls, graph(), draft)
    events = log.read()
    assert any(e['stage']=='essay_draft_resumed' for e in events)
    audits = [e for e in events if e['stage']=='audit_essay' and e['label']=='MODEL']
    assert len(audits)==1 and json.loads(audits[0]['payload_json'])['status']=='accepted'
    assert json.loads((tmp/'draft.unverified.json').read_text()) == draft
