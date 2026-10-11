"""Pilot configuration reaches the native CLI lifecycle and provider boundary."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from ara.runtime.cache import Cache
from ara.runtime.calls import ModelCalls
from ara.runtime.cli import main
from ara.runtime.logging import EventLog
from ara.runtime.providers import AnthropicProvider, MockProvider, Response
from ara.types import Proposition, Formula
from fixture_support import ROOT, T, FakeEngine
from test_calls import response, rig, register, graph


@pytest.mark.parametrize('cap,expected', [(0, 2), (20, 2), (1001, 0)])
def test_pilot_config_and_caps(tmp_path, cap, expected):
    config = yaml.safe_load((ROOT / 'config.yaml').read_text())
    assert config['pilot']['cost_cap_usd'] == 100.0
    assert config['pilot']['token_cap'] == 10_000_000
    assert config['smoke']['essay_min_words'] == 150
    config['pilot']['cost_cap_usd'] = cap
    config['pilot']['token_cap'] = 100_000_000
    path = tmp_path / 'config.yaml'
    path.write_text(yaml.safe_dump(config))
    targets = [Proposition(f'p{i}', 'P', Formula('atom', name='P')) for i in range(10)]
    captured, engines, dispatched = [], [], []
    def factory(config, log, topic):
        captured.append(config)
        provider = MockProvider({})
        def complete(kind, prompt, schema, maximum):
            dispatched.append(kind)
            data = {'build_t': T.to_dict(), 'propose_targets': {'targets': [p.to_dict() for p in targets]},
                    'map_leaf': {'t_id': 'open'}, 'propose_cuts': {'proposals': []}}[kind]
            return Response(response(data, usage={'input_tokens': 5,
                                    'output_tokens': 1_000_000 if kind == 'build_t' else 3}))
        provider.complete = complete
        return ModelCalls(config, provider, log, Cache(tmp_path / 'cache'), ROOT, topic)
    def engine_factory(bank, calls):
        engine = FakeEngine(calls)
        engines.append(engine)
        return engine
    run = tmp_path / 'run'
    assert main(['run', '--profile', 'pilot', '--config', str(path), '--topic', 'P Q',
                 '--literature', str(ROOT / 'tests/fixtures/runtime/smoke-literature.txt'),
                 '--run-dir', str(run)], calls_factory=factory, engine_factory=engine_factory) == expected
    resolved = captured[0]
    assert {k: resolved[k] for k in ('target_candidates', 'depth_cap', 'node_cap',
            'essay_word_limit', 'essay_min_words', 'write_essay_max_output_tokens')} == {
                'target_candidates': 10, 'depth_cap': 6, 'node_cap': 500,
                'essay_word_limit': 6000, 'essay_min_words': 4500, 'write_essay_max_output_tokens': 20000}
    assert [resolved.get(f'{kind}_max_output_tokens', resolved['max_output_tokens'])
            for kind in ('audit_essay', 'search_evidence', 'verify_originality_citations')] == [24000, 64000, 48000]
    assert resolved['cost_cap_usd'] == cap and resolved['token_cap'] == 100_000_000
    events = EventLog(run / 'events.jsonl').read()
    if expected == 0:
        assert [p.id for p in engines[0].goals] == [name for p in targets for name in (p.id, 'not:' + p.id)]
        assert any(e['stage'] == 'awaiting_selection' for e in events)
        assert not any(e['label'] == 'STOP' for e in events)
    else:
        assert len(dispatched) == (0 if cap == 0 else 1)
        assert json.loads((run / 'partial.json').read_text())['reason'].startswith('cost cap')


def test_writer_output_limit_reserved_and_dispatched(rig, monkeypatch):
    calls, provider, log = rig
    calls.config['write_essay_max_output_tokens'] = 20000
    draft = {'title': 'P', 'body': '[[node:n1]] P P', 'bibliography': []}
    register(calls, provider, 'write_essay', calls.essay_inputs(graph()), draft)
    maximums = []
    complete = provider.complete
    def capture(kind, prompt, schema, maximum):
        maximums.append(maximum)
        return complete(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'complete', capture)
    assert calls.write_essay(graph()) == draft
    assert maximums == [20000]
    start = next(json.loads(e['payload_json']) for e in log.read() if e['stage'] == 'call_start')
    assert start['reserved_usage']['output_tokens'] == 20000


@pytest.mark.parametrize('kind,maximum', [('write_essay', 20000), ('audit_essay', 24000),
    ('search_evidence', 64000), ('verify_originality_citations', 48000)])
def test_large_writer_uses_sdk_stream(rig, kind, maximum):
    calls, _, _ = rig
    requests = []
    class Stream:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def get_final_message(self):
            return SimpleNamespace(to_dict=lambda **kw: response({'P': 'Q'}))
    class Messages:
        def stream(self, **kwargs):
            requests.append(kwargs)
            return Stream()
        def create(self, **kwargs):
            pytest.fail('large writer must stream')
    provider = AnthropicProvider(calls.config, SimpleNamespace(beta=SimpleNamespace(messages=Messages())))
    result = provider.complete(kind, 'P', None, maximum)
    assert result.raw == response({'P': 'Q'})
    assert requests[0]['max_tokens'] == maximum
    assert requests[0]['fallbacks'] == [{'model': 'claude-opus-4-8'}]


@pytest.mark.parametrize('profile', ['pilot', 'smoke'])
@pytest.mark.parametrize('kind,limit,data', [
    ('write_essay', 20000, {'title': 'P', 'body': 'P Q', 'bibliography': []}),
    ('audit_essay', 24000, {'labels': []}),
    ('search_evidence', 64000, {'P': 'Q'}),
    ('verify_originality_citations', 48000, {'originality': {
        'assessment': 'unverified', 'evidence_urls': [], 'detail': 'P'}, 'items': []}),
    ('formalise', 8192, {'formula': {'op': 'atom', 'name': 'P'}}),
])
def test_profile_kind_limits_reach_reservation_dispatch_and_cache(rig, monkeypatch, profile, kind, limit, data):
    calls, provider, log = rig
    calls.config.update(calls.config[profile])
    expected = limit if profile == 'pilot' else 8192
    register(calls, provider, kind, {}, data)
    maximums = []
    complete = provider.complete
    def capture(kind, prompt, schema, maximum):
        maximums.append(maximum)
        return complete(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'complete', capture)
    calls.call(kind, {})
    calls.call(kind, {})  # Same allowance reuses the accepted response.
    calls.config[f'{kind}_max_output_tokens'] = expected + 1
    calls.call(kind, {})  # Changed allowance must not reuse the prior cache entry.
    assert maximums == [expected, expected + 1]
    starts = [json.loads(e['payload_json']) for e in log.read() if e['stage'] == 'call_start']
    assert [s['reserved_usage']['output_tokens'] for s in starts] == [expected, expected + 1]
