"""Recorded real-source verification, plus explicitly opt-in paid capture."""
from __future__ import annotations

from fixture_support import api_fixture_config

import json
import os
from pathlib import Path

import pytest
import yaml

from ara.runtime.cache import Cache, canonical, digest
from ara.runtime.calls import ModelCalls
from ara.runtime.export import export_run
from ara.runtime.logging import EventLog, now
from ara.runtime.providers import AnthropicProvider, MockProvider, Response, mock_key

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / 'tests/fixtures/verification'
CASES = json.loads((FIXTURES / 'cases.json').read_text())
TOPIC = 'Software engineering history'


def configuration() -> dict:
    config = api_fixture_config()
    config.update(web_search_max_uses=1, max_output_tokens=4096,
                  cost_cap_usd=4, token_cap=1000000, validation_attempts=1)
    return config


def assert_case(name: str, cleaned: dict, result: dict, log: EventLog, output: Path) -> None:
    case = CASES[name]
    draft = case['draft']
    if name == 'prior_statement':
        assert result['items'] == []
        assert result['originality']['assessment'] == 'possible_overlap'
        assert result['originality']['evidence_urls']
        assert 'brooks' in result['originality']['detail'].lower()
        assert cleaned == draft
    else:
        assert len(result['items']) == 1
        item = result['items'][0]
        assert item['status'] == case['status']
        assert item['action'] == ('retain' if case['status'] == 'verified' else 'remove')
        if case['status'] == 'verified':
            assert item['evidence_urls']
            assert cleaned == draft
        elif name == 'altered_quote':
            assert cleaned == {**draft, 'body': 'Knuth wrote: .'}
        else:
            assert cleaned == {**draft, 'body': 'Software modularity .', 'bibliography': []}
    # The export assertion reads the actual artifact; this is verification/export
    # coverage, not a claim to exercise the writer or route audits.
    log.record('final_draft', draft=cleaned)
    _, essay = export_run(log.path, output)
    expected = cleaned['title'] + '\n\n' + cleaned['body']
    if cleaned['bibliography']:
        expected += '\n\nBibliography\n' + '\n'.join(b['text'] for b in cleaned['bibliography'])
    assert essay.read_text() == expected + '\n'


def replay(tmp_path: Path, name: str, *, fuzzy_verdict: bool = False):
    recorded = json.loads((FIXTURES / 'responses.json').read_text())
    responses = {}
    for call in recorded['cases'][name]['calls']:
        assert digest(call['prompt']) == call['prompt_hash']
        assert digest(canonical(call['request'])) == call['request_hash']
        raw = call['response']
        if fuzzy_verdict and call['kind'] == 'verify_originality_citations':
            # Deliberately adverse classifier output: the production exact check
            # must reject similarity even if the model mistakenly accepts it.
            block = next(b for b in raw['content'] if b['type'] == 'text')
            payload = json.loads(block['text'])
            item = payload['items'][0]
            item.update(status='verified', action='retain',
                        evidence_urls=payload['originality']['evidence_urls'])
            block['text'] = canonical(payload)
        responses[mock_key(call['kind'], call['prompt'])] = raw
    config = recorded['config']
    provider = MockProvider(responses, model=recorded['model'])
    log = EventLog(tmp_path / 'events.jsonl')
    calls = ModelCalls(config, provider, log, Cache(tmp_path / 'cache'), ROOT, TOPIC)
    cleaned, result = calls.verify_originality_citations(CASES[name]['draft'])
    return cleaned, result, log, provider


@pytest.mark.parametrize('name', CASES)
def test_recorded_known_case(tmp_path, name):
    cleaned, result, log, provider = replay(tmp_path, name)
    assert_case(name, cleaned, result, log, tmp_path / 'export')
    assert provider.calls == 2
    searches = [e for e in log.read() if e['stage'] == 'search_evidence' and e['label'] == 'MODEL']
    assert len(searches) == 1 and searches[0]['usage']['server_tool_uses'] > 0


def test_altered_quote_rejects_fuzzy_classifier(tmp_path):
    cleaned, result, log, _ = replay(tmp_path, 'altered_quote', fuzzy_verdict=True)
    assert_case('altered_quote', cleaned, result, log, tmp_path / 'export')


@pytest.mark.skipif(os.environ.get('ARA_LIVE_TEST') != '1', reason='paid provider test requires ARA_LIVE_TEST=1')
def test_live_known_cases():
    config = configuration()
    run = Path(os.environ['ARA_VERIFICATION_RUN']) if os.environ.get('ARA_VERIFICATION_RUN') else (
        ROOT / 'runs' / ('theta-verification-' + now().replace(':', '-')))
    recording_path = run / ('responses-' + now().replace(':', '-') + '.json')
    provider = AnthropicProvider(config)
    log = EventLog(run / 'events.jsonl')
    calls = ModelCalls(config, provider, log, Cache(run / 'cache'), ROOT, TOPIC)
    recording = {'model': provider.model, 'date': now(), 'config': config, 'cases': {}}
    results = {}
    start_offset = len(log.read())
    try:
        for name in ['prior_statement', *(n for n in CASES if n != 'prior_statement')]:
            case = CASES[name]
            offset = len(log.read())
            try:
                results[name] = calls.verify_originality_citations(case['draft'])
            finally:
                entries = []
                for event in log.read()[offset:]:
                    if event['label'] != 'MODEL':
                        continue
                    cached = json.loads(event['payload_json'])['cache_hit']
                    if cached:
                        event = next(e for e in log.read() if e['label'] == 'MODEL' and
                                     e['prompt'] == event['prompt'] and e['response'] == event['response'] and
                                     not json.loads(e['payload_json'])['cache_hit'])
                    kind = event['stage']
                    schema = None if kind == 'search_evidence' else json.loads(
                        (ROOT / 'schemas' / f'{kind}.json').read_text())
                    request = provider.request(kind, event['prompt'], schema, config['max_output_tokens'])
                    if config['fallbacks'] != 'off':
                        request.update(betas=['server-side-fallback-2026-06-01'],
                                       fallbacks=[{'model': model} for model in config['fallbacks']])
                    entries.append({'kind': kind, 'date': event['timestamp'], 'reused_evidence': cached,
                                    'prompt': event['prompt'], 'prompt_hash': digest(event['prompt']),
                                    'request': request, 'request_hash': digest(canonical(request)),
                                    'served_model': event['model_version'],
                                    'response': json.loads(event['response']) if event['response'] else None,
                                    'usage': event['usage'], 'cost_usd': event['cost_usd']})
                recording['cases'][name] = {'calls': entries}
        for name, (cleaned, result) in results.items():
            assert_case(name, cleaned, result, log, run / name / 'export')
        searches = [e for e in log.read()[start_offset:] if e['stage'] == 'search_evidence' and e['label'] == 'MODEL']
        assert len(searches) == 5
        assert all(Response(json.loads(e['response'])).usage.server_tool_uses > 0 for e in searches)
        assert any(e['label'] == 'MODEL' and not json.loads(e['payload_json'])['cache_hit']
                   for e in log.read()[start_offset:]), 'live test must make a real provider call'
    finally:
        recording['ledger_totals'] = {'tokens': calls.budget.used_tokens, 'cost_usd': float(calls.budget.used_cost)}
        recording_path.write_text(json.dumps(recording, indent=2, ensure_ascii=False) + '\n')
        print(f'Live receipt: {run}; tokens={calls.budget.used_tokens}; cost_usd={calls.budget.used_cost}')
