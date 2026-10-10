import json
import shutil

import pytest

from ara.runtime.calls import Rejected
from ara.runtime.export import export_run, methodology
from ara.runtime.logging import EventLog
from ara.types import EngineDecision, RunEvent
from test_calls import rig, register, graph


def verification(draft, status='unverified', urls=None):
    return {'originality': {'assessment': 'unverified', 'evidence_urls': [], 'detail': 'P'},
            'items': [{'id': i['id'], 'kind': i['kind'], 'text': i['text'], 'status': status,
                       'evidence_urls': urls or [], 'detail': 'P',
                       'action': 'retain' if status == 'verified' else 'remove'}
                      for i in __import__('ara.runtime.calls', fromlist=['ModelCalls']).ModelCalls.verification_items(draft)]}


def setup_verification(rig, status='unverified', urls=None):
    calls, provider, log = rig
    draft = {'title': 'P', 'body': '[[node:n1]] P [cite:c1] "Q"',
             'bibliography': [{'id': 'c1', 'text': 'placeholder:1', 'url': None}]}
    items = calls.verification_items(draft)
    content = [{'type': 'text', 'text': 'P'}, {'type': 'web_search_tool_result', 'content': [
        {'type': 'web_search_result', 'url': 'https://example.invalid/1', 'title': 'P'}]}]
    evidence = {'text': 'P', 'urls': ['https://example.invalid/1'], 'content': content}
    register(calls, provider, 'search_evidence', {'draft': draft, 'items': items}, {}, content=content)
    payload = verification(draft, status, urls)
    register(calls, provider, 'verify_originality_citations', {'draft': draft, 'items': items, 'evidence': evidence}, payload)
    return draft


def test_unverified_items_removed_never_replaced(rig):
    calls, _, log = rig
    draft = setup_verification(rig)
    cleaned, result = calls.verify_originality_citations(draft)
    assert cleaned == {'title': 'P', 'body': '[[node:n1]] P  ', 'bibliography': []}
    assert draft['bibliography'] and '"Q"' in draft['body']
    assert json.loads(log.read()[-1]['payload_json'])['removed_ids'] == ['c1', 'quote:0']


def test_verification_rejects_invented_evidence(rig):
    calls, _, log = rig
    draft = setup_verification(rig, 'verified', ['https://example.invalid/invented'])
    with pytest.raises(Rejected, match='unsupported verification URL'):
        calls.verify_originality_citations(draft)


def test_methodology_regenerates_from_log_alone(rig, tmp_path):
    calls, provider, log = rig
    log.record('run_started', architecture='L T H', bank_version='1.0.0')
    log.human('feedback', ' P\nQ ', reported_minutes=3)
    log.record('candidates', candidates=[{'id': 'p', 'text': 'P'}])
    log.record('route', graph=graph().to_dict())
    log.emit(RunEvent('2026-10-08T00:00:00+00:00', 'license', 'ENGINE',
                      decision=EngineDecision('discarded', 'unknown_bank', 'P', bank_id='missing')))
    log.record('final_draft', draft={'title': 'P', 'body': '[[node:n1]] P', 'bibliography': []})
    report, essay = export_run(log.path, log.path.parent / 'export')
    before, essay_before = report.read_bytes(), essay.read_bytes()
    copied_log = tmp_path / 'only.jsonl'
    shutil.copyfile(log.path, copied_log)
    shutil.rmtree(log.path.parent)
    shutil.rmtree(calls.cache.path)
    new_report, new_essay = export_run(copied_log, tmp_path / 'regenerated')
    assert new_report.read_bytes() == before
    assert new_essay.read_bytes() == essay_before == b'P\n\nP\n'
    report_events = [json.loads(block.split('\n```')[0]) for block in
                     new_report.read_text().split('```json\n')[2:]]
    assert any(e['decision'] and e['decision']['status'] == 'discarded' for e in report_events)
    assert any(e['label'] == 'HUMAN' and json.loads(e['payload_json'])['text'] == ' P\nQ ' for e in report_events)


@pytest.mark.parametrize('quote,excerpt,source_url,expected_status', [
    ('P Q R', 'P Q R', 'https://example.invalid/1', 'verified'),
    ('P Q R', 'P\n Q  R', 'https://example.invalid/1', 'verified'),
    ('P Q S', 'P Q R', 'https://example.invalid/1', 'unverified'),
    ('P Q R', 'P Q RS', 'https://example.invalid/1', 'unverified'),
    ('P Q R', 'P Q R', 'https://example.invalid/2', 'unverified'),
    ('P Q R', '', 'https://example.invalid/1', 'unverified'),
])
def test_quote_requires_exact_source_excerpt(rig, quote, excerpt, source_url, expected_status):
    calls, provider, log = rig
    draft = {'title': 'P', 'body': f'"{quote}"', 'bibliography': []}
    items = calls.verification_items(draft)
    url = 'https://example.invalid/1'
    content = [
        {'type': 'web_search_tool_result', 'content': [
            {'type': 'web_search_result', 'url': url, 'title': 'P'}]},
        {'type': 'text', 'text': 'P Q R', 'citations': [
            {'type': 'web_search_result_location', 'url': source_url, 'cited_text': excerpt}]},
    ]
    evidence = {'text': 'P Q R', 'urls': [url], 'content': content}
    register(calls, provider, 'search_evidence', {'draft': draft, 'items': items}, {}, content=content)
    register(calls, provider, 'verify_originality_citations',
             {'draft': draft, 'items': items, 'evidence': evidence}, verification(draft, 'verified', [url]))
    cleaned, result = calls.verify_originality_citations(draft)
    assert result['items'][0]['status'] == expected_status
    assert cleaned['body'] == (draft['body'] if expected_status == 'verified' else '')


@pytest.mark.parametrize('quote,excerpt,expected_status', [
    ('P Q R', 'P Q R', 'verified'),
    ('P Q S', 'P Q R', 'unverified'),
    ('P Q S', 'P Q S', 'unverified'),
])
def test_quote_excerpt_must_match_search_evidence(rig, quote, excerpt, expected_status):
    calls, provider, log = rig
    draft = {'title': 'P', 'body': f'"{quote}"', 'bibliography': []}
    items = calls.verification_items(draft)
    url = 'https://example.invalid/1'
    content = [{'type': 'text', 'text': 'P Q R'},
               {'type': 'web_search_tool_result', 'content': [
                   {'type': 'web_search_result', 'url': url, 'title': 'P'}]}]
    evidence = {'text': 'P Q R', 'urls': [url], 'content': content}
    register(calls, provider, 'search_evidence', {'draft': draft, 'items': items}, {}, content=content)
    payload = verification(draft, 'verified', [url])
    payload['items'][0]['source_excerpt'] = excerpt
    register(calls, provider, 'verify_originality_citations',
             {'draft': draft, 'items': items, 'evidence': evidence}, payload)
    cleaned, result = calls.verify_originality_citations(draft)
    assert result['items'][0]['status'] == expected_status
    assert cleaned['body'] == (draft['body'] if expected_status == 'verified' else '')
