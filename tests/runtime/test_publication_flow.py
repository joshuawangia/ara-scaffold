"""Exact operator editing instructions, one edit, and unchanged native gates."""
import json

import pytest

from ara.runtime.cache import digest
from ara.runtime.calls import Rejected
from ara.runtime.providers import Response
from test_calls import rig, response
from test_publication import install_publication, paper, polished


def setup_flow(rig, monkeypatch, adverse=0):
    from ara.runtime import publication
    calls, route, seen = install_publication(rig, monkeypatch, adverse=adverse)
    text = 'P\n\nQ\n'
    calls.config['publication_flow_prompt'] = dict(text=text, sha256=digest(text), path='P.txt')
    calls.config['publication_inline_repairs'] = True
    monkeypatch.setattr(publication, 'verified_legacy_import', lambda *args: True)
    monkeypatch.setattr(calls, 'verify_originality_citations', lambda draft: (draft, dict(items=[dict(status='verified')])))
    complete = calls.provider.complete
    edits = []
    def dispatch(kind, prompt, schema, maximum):
        if kind == 'polish_flow':
            edits.append((prompt, schema))
            return Response(response(dict(markdown=polished(paper())['markdown'].split('\n\n{{fig:')[0])))
        return complete(kind, prompt, schema, maximum)
    monkeypatch.setattr(calls.provider, 'complete', dispatch)
    return calls, route, seen, edits


def test_flow_single_edit_exact_instruction_and_native_final_gate(rig, monkeypatch):
    from ara.runtime.publication import polish
    calls, route, seen, edits = setup_flow(rig, monkeypatch)
    result, _ = polish(calls, route, paper())
    assert result['polished'] and result['native_citations']['status'] == 'pass'
    assert len(edits) == 1
    instruction, payload = edits[0][0].split('\nINPUT_JSON\n')
    assert instruction == calls.config['publication_flow_prompt']['text']
    assert json.loads(payload) == {'markdown': '# P\n\n' + paper()['body']}
    assert set(edits[0][1]['properties']) == {'markdown'}
    assert not [k for k, _ in seen if k == 'polish_essay']
    assert len([k for k, _ in seen if k == 'audit_publication']) == 6
    record = next(json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'publication_flow_prompt')
    assert record['sha256'] == digest('P\n\nQ\n')
    assert record['text'] == 'P\n\nQ\n'


def test_flow_fails_closed_on_unverified_source_before_edit(rig, monkeypatch):
    from ara.runtime import publication
    calls, route, _, edits = setup_flow(rig, monkeypatch)
    monkeypatch.setattr(publication, 'verified_legacy_import', lambda *args: False)
    with pytest.raises(Rejected, match='verified original'):
        publication.polish(calls, route, paper())
    assert not edits


def test_flow_prompt_hash_mismatch_refuses_before_dispatch(rig, monkeypatch):
    calls, _, _, edits = setup_flow(rig, monkeypatch)
    calls.config['publication_flow_prompt']['text'] += 'R'
    with pytest.raises(Rejected, match='prompt hash'):
        calls.call('polish_flow', {'markdown': 'P'})
    assert not edits


def test_flow_citation_occurrence_loss_is_not_accepted_or_rerolled(rig, monkeypatch):
    from ara.runtime.publication import polish
    calls, route, _, edits = setup_flow(rig, monkeypatch)
    complete = calls.provider.complete
    def dispatch(kind, prompt, schema, maximum):
        value = complete(kind, prompt, schema, maximum)
        if kind == 'polish_flow':
            data = json.loads(value.text())
            data['markdown'] = data['markdown'].replace('[cite:p]', '', 1)
            return Response(response(data))
        return value
    monkeypatch.setattr(calls.provider, 'complete', dispatch)
    result, _ = polish(calls, route, paper())
    assert not result['polished'] and 'citation occurrence' in result['polish_failure']
    assert len(edits) == 1
    with pytest.raises(Rejected, match='already attempted'):
        polish(calls, route, paper())
    assert len(edits) == 1


def test_flow_never_falls_back_to_whole_paper_repairs(rig, monkeypatch):
    from ara.runtime.publication import polish
    calls, route, seen, edits = setup_flow(rig, monkeypatch, adverse=1)
    complete = calls.provider.complete
    def dispatch(kind, prompt, schema, maximum):
        value = complete(kind, prompt, schema, maximum)
        if kind == 'audit_publication':
            data = json.loads(value.text())
            for label in data['labels']:
                if label['role'] == 'unsupported_claim':
                    label.update(role='source_claim', citation_supported=False)
            return Response(response(data))
        return value
    monkeypatch.setattr(calls.provider, 'complete', dispatch)
    result, _ = polish(calls, route, paper())
    assert not result['polished'] and result['repair_rounds'] == 0
    assert len(edits) == 1 and not [k for k, _ in seen if k == 'polish_essay']


def test_prompt_file_hash_preserves_newline_bytes(tmp_path):
    from ara.runtime.publication_flow import prompt_record
    path = tmp_path / 'P.txt'
    path.write_bytes(b'P\r\nQ\r\n')
    record = prompt_record(path)
    assert record['text'].encode() == path.read_bytes()
    assert record['sha256'] == digest('P\r\nQ\r\n')


def test_flow_cannot_relabel_an_existing_publication(rig, monkeypatch):
    from ara.runtime.publication import polish
    calls, route, _, edits = setup_flow(rig, monkeypatch)
    calls.log.record('publication_started', route_id=route.id)
    with pytest.raises(Rejected, match='dedicated verified-source run'):
        polish(calls, route, paper())
    assert not edits


def test_flow_resume_cannot_change_or_omit_instruction(rig, monkeypatch):
    from ara.runtime.publication import polish
    calls, route, _, edits = setup_flow(rig, monkeypatch)
    polish(calls, route, paper())
    calls.config['publication_flow_prompt'] = dict(text='R', sha256=digest('R'), path='R.txt')
    with pytest.raises(Rejected, match='binding changed'):
        polish(calls, route, paper())
    del calls.config['publication_flow_prompt']
    with pytest.raises(Rejected, match='original prompt'):
        polish(calls, route, paper())
    assert len(edits) == 1
