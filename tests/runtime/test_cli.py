import json
from pathlib import Path

import pytest
import yaml

from ara.runtime.cache import Cache
from ara.runtime.calls import ModelCalls
from ara.runtime.cli import main
from ara.runtime.logging import EventLog
from ara.runtime.providers import MockProvider
from ara.types import RouteGraph
from fixture_support import ROOT, FakeEngine, TARGETS


@pytest.fixture
def cli_setup(tmp_path):
    config = yaml.safe_load((ROOT / 'config.yaml').read_text())
    config.update(config['smoke'])
    config['cache_dir'] = str(tmp_path / 'cache')
    path = tmp_path / 'config.yaml'
    path.write_text(yaml.safe_dump(config))
    provider = MockProvider(ROOT / 'tests/fixtures/runtime/canned.json')
    engines = []
    def calls_factory(config, log, topic):
        return ModelCalls(config, provider, log, Cache(Path(config['cache_dir'])), ROOT, topic)
    def engine_factory(bank, calls):
        engine = FakeEngine(calls)
        engines.append(engine)
        return engine
    return path, provider, engines, calls_factory, engine_factory


def test_smoke_cli_runs_both_polarities_and_exports(cli_setup, tmp_path):
    config, provider, engines, factory, engine_factory = cli_setup
    run = tmp_path / 'run'
    argv = ['run', '--smoke', '--config', str(config), '--run-dir', str(run)]
    assert main(argv, engine_factory=engine_factory, calls_factory=factory) == 0
    assert [g.id for g in engines[0].goals] == ['p', 'not:p', 'q', 'not:q']
    graphs = sorted((run / 'routes').glob('*.json'))
    assert len(graphs) == 4
    parsed = [RouteGraph.from_json(p.read_text()) for p in graphs]
    assert sum(g.status == 'CLOSED' for g in parsed) == 2
    assert json.loads((run / 'draft.json').read_text())['body'] == '[[node:n:p]] P P'
    assert (run / 'export/essay.txt').read_text() == 'P\n\nP P\n'
    events = EventLog(run / 'events.jsonl').read()
    assert any(e['decision'] and e['decision']['status'] == 'discarded' for e in events)
    human = next(e for e in events if e['label'] == 'HUMAN')
    human_data = json.loads(human['payload_json'])
    assert human_data['argv'] == argv
    assert human_data['literature'] is None and human_data['topic'] is None
    assert json.loads(next(e['payload_json'] for e in events if e['stage'] == 'run_started'))['literature_source'] == 'smoke_fixture'
    assert provider.calls == 14  # second audit is a cache hit
    second = tmp_path / 'second'
    argv[-1] = str(second)
    assert main(argv, engine_factory=engine_factory, calls_factory=factory) == 0
    assert provider.calls == 14
    assert [p.read_bytes() for p in graphs] == [p.read_bytes() for p in sorted((second / 'routes').glob('*.json'))]


def test_every_cli_human_input_verbatim(cli_setup, tmp_path):
    config, provider, engines, factory, engine_factory = cli_setup
    run = tmp_path / 'run'
    assert main(['run', '--smoke', '--config', str(config), '--run-dir', str(run)],
                engine_factory=engine_factory, calls_factory=factory) == 0
    assert main(['select', '--run-dir', str(run), '--route', 'route:p', '--human-minutes', '1.5'],
                calls_factory=factory) == 0
    feedback = ' P\n Q  '
    assert main(['feedback', '--run-dir', str(run), '--text', feedback]) == 0
    assert main(['export', '--run-dir', str(run), '--redact', 'P']) == 0
    events = EventLog(run / 'events.jsonl').read()
    human = [e for e in events if e['label'] == 'HUMAN']
    assert all(e['timestamp'] for e in human)
    payloads = [json.loads(e['payload_json']) for e in human]
    assert any(p['text'] == feedback for p in payloads)
    assert any(p['text'] == 'route:p' for p in payloads)
    assert sum(p['reported_minutes'] for p in payloads) == 1.5
    assert (run / 'export/essay.txt').read_text() == '[REDACTED]\n\n[REDACTED] [REDACTED]\n'
    calls = factory(yaml.safe_load(config.read_text()), EventLog(run / 'events.jsonl'), 'P Q')
    assert calls.essay_inputs(RouteGraph.from_json(next((run / 'routes').glob('*.json')).read_text()))['feedback'] == [feedback]


@pytest.mark.parametrize('cap,value', [('token_cap', 1), ('cost_cap_usd', 0)])
def test_cli_cap_clean_stop_with_partial_artifacts(cli_setup, tmp_path, cap, value):
    config, provider, _, factory, engine_factory = cli_setup
    data = yaml.safe_load(config.read_text())
    data['smoke'][cap] = value
    config.write_text(yaml.safe_dump(data))
    run = tmp_path / 'run'
    assert main(['run', '--smoke', '--config', str(config), '--run-dir', str(run)],
                engine_factory=engine_factory, calls_factory=factory) == 2
    events = EventLog(run / 'events.jsonl').read()
    assert any(e['label'] == 'STOP' for e in events)
    assert (run / 'partial.json').is_file()
    assert (run / 'export/methodology.md').is_file()
    assert not (run / 'export/essay.txt').exists()
    assert provider.calls == 0


def test_normal_run_waits_for_human_selection(cli_setup, tmp_path):
    config, provider, engines, factory, engine_factory = cli_setup
    run = tmp_path / 'run'
    assert main(['run', '--config', str(config), '--topic', 'P Q', '--literature',
                 str(ROOT / 'tests/fixtures/runtime/smoke-literature.txt'), '--run-dir', str(run)],
                engine_factory=engine_factory, calls_factory=factory) == 0
    events = EventLog(run / 'events.jsonl').read()
    assert any(e['stage'] == 'awaiting_selection' for e in events)
    assert not any(e['stage'] == 'write_essay' for e in events)
    assert not (run / 'export/essay.txt').exists()
    assert main(['select', '--run-dir', str(run), '--route', 'route:p'], calls_factory=factory) == 0
    assert (run / 'export/essay.txt').exists()


def test_interactive_input_measures_prompt_to_accept(tmp_path, monkeypatch):
    import ara.runtime.cli as cli
    run = tmp_path / 'run'
    log = EventLog(run / 'events.jsonl')
    log.record('run_started', topic='P')
    values = iter([10.0, 20.0, 25.0, 30.0])
    monkeypatch.setattr(cli.time, 'monotonic', lambda: next(values))
    monkeypatch.setattr('builtins.input', lambda prompt: ' Q\nP ')
    assert main(['feedback', '--run-dir', str(run)]) == 0
    event = next(e for e in log.read() if e['stage'] == 'feedback')
    payload = json.loads(event['payload_json'])
    assert payload['text'] == ' Q\nP '
    assert payload['elapsed_seconds'] == 5.0
