"""Independent candidate runs over one frozen placeholder table."""
import json
from pathlib import Path

import pytest
import yaml

from ara.runtime.cli import main
from ara.runtime.logging import read_log

ROOT = Path(__file__).resolve().parents[2]


def events(directory):
    return [r['event'] for r in read_log(directory / 'events.jsonl')]


def summary(directory):
    text = (directory / 'export/methodology.md').read_text()
    return json.loads(text.split('```json\n')[1].split('\n```')[0])


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    import socket
    def forbidden(*args, **kwargs):
        pytest.fail('network is forbidden')
    monkeypatch.setattr(socket.socket, 'connect', forbidden)


@pytest.fixture
def source(tmp_path):
    config = yaml.safe_load((ROOT / 'config.yaml').read_text())
    config['cache_dir'] = str(tmp_path / 'cache')
    path = tmp_path / 'config.yaml'
    path.write_text(yaml.safe_dump(config))
    run = tmp_path / 'builder'
    assert main(['run', '--smoke', '--provider', 'mock', '--config', str(path), '--run-dir', str(run)]) == 0
    return run, path


def candidate(source, directory, *extra, **kwargs):
    run, config = source
    return main(['run', '--smoke', '--provider', 'mock', '--config', str(config),
                 '--run-dir', str(directory), '--from-frozen', str(run),
                 '--cost-cap-usd', '2', '--token-cap', '1000000', *extra], **kwargs)


def test_shared_candidates(source, tmp_path):
    run, _ = source
    before = {p.name: p.read_bytes() for p in run.iterdir() if p.is_file()}
    candidates = [tmp_path / 'first', tmp_path / 'second']
    seen_keys = {json.loads(e['payload_json'])['cache_key'] for e in events(run) if e['label'] == 'MODEL'}
    for directory in candidates:
        assert candidate(source, directory) == 0
        assert (directory / 'commitments.json').read_bytes() == (run / 'commitments.json').read_bytes()
        local = events(directory)
        assert not any(e['stage'] in ('build_t', 'commitments_frozen') for e in local)
        models = [e for e in local if e['label'] == 'MODEL']
        assert models[0]['stage'] == 'propose_targets'
        keys = {json.loads(e['payload_json'])['cache_key'] for e in models}
        assert not keys & seen_keys
        seen_keys.update(keys)
        assert not json.loads(models[0]['payload_json'])['cache_hit']
        report = summary(directory)
        assert report['shared_frozen_t']['builder_run'] == str(run.resolve())
        assert report['inherited_totals']['cost_usd'] > 0
        assert report['cost_usd'] == report['local_totals']['cost_usd']
        assert report['cost_usd'] == round(sum(e['cost_usd'] for e in models), 10)
    configs = [next(json.loads(e['payload_json'])['config'] for e in events(d)
                    if e['stage'] == 'run_started') for d in candidates]
    assert configs[0]['seed'] != configs[1]['seed']
    assert configs[0]['cache_identity'] != configs[1]['cache_identity']
    assert before == {p.name: p.read_bytes() for p in run.iterdir() if p.is_file()}


def rewrite(directory, transform):
    """Rebuild a fixture chain so refusal tests exercise semantics, not checksum failure."""
    from ara.runtime.logging import EventLog
    from ara.types import RunEvent
    original = events(directory)
    (directory / 'events.jsonl').unlink()
    (directory / 'events.anchor').unlink()
    log = EventLog(directory / 'events.jsonl')
    for event in original:
        result = transform(event)
        if result is not None:
            log.emit(RunEvent.from_dict(result))


@pytest.mark.parametrize('case,reason', [
    ('no_freeze', 'exactly one freeze'), ('hash', 'file hash mismatch'),
    ('chain', 'invalid or modified log'), ('anchor', 'checkpoint mismatch'),
    ('incomplete', 'not complete'), ('topic', 'different topic'),
    ('config', 'config drift'), ('schema', 'schema-version drift'),
    ('schema_empty', 'schema-version drift'), ('schema_null', 'schema-version drift'),
    ('bank', 'bank version drift'), ('provenance', 'missing construction receipts'),
    ('cache_origin', 'missing construction/extraction cache origin'),
    ('prompt', 'schema/prompt version drift'), ('response', 'does not match frozen T'),
])
def test_refusals(source, tmp_path, capsys, case, reason):
    run, config = source
    extra = []
    def transform(e):
        p = json.loads(e['payload_json'])
        if case == 'no_freeze' and e['stage'] == 'commitments_frozen': return None
        if case == 'incomplete' and e['stage'] == 'run_finished': return None
        if case == 'provenance' and (e['stage'] == 'build_t' or
                                    e['stage'] == 'call_start' and p['kind'] == 'build_t'): return None
        if case == 'cache_origin' and e['stage'] == 'call_start' and p['kind'] == 'build_t': return None
        if e['stage'] == 'commitments_frozen':
            if case == 'schema': p['contract']['version'] = 999
            if case == 'schema_empty': p['contract'] = {}
            if case == 'schema_null': p['contract'] = None
            if case == 'bank': p['bank_version'] = '999'
        if e['stage'] == 'build_t':
            if case == 'cache_origin': p['cache_hit'] = True
            if case == 'prompt': e['prompt'] = 'P'
            if case == 'response':
                raw = json.loads(e['response'])
                value = json.loads(raw['content'][0]['text'])
                value['commitments'][0]['text'] = 'R'
                raw['content'][0]['text'] = json.dumps(value)
                e['response'] = json.dumps(raw)
        e['payload_json'] = json.dumps(p)
        return e
    rewrite(run, transform)
    if case == 'hash': (run / 'commitments.json').write_text('{}')
    if case == 'chain':
        path = run / 'events.jsonl'
        path.write_text(path.read_text().replace('P Q', 'Q R', 1))
    if case == 'anchor': (run / 'events.anchor').write_text('')
    if case == 'topic': extra = ['--topic', 'Q']
    if case == 'config':
        data = yaml.safe_load(config.read_text())
        data['formula_output_depth'] = 3
        config.write_text(yaml.safe_dump(data))
    def no_provider(*args):
        pytest.fail('invalid source must refuse before provider creation')
    assert candidate(source, tmp_path / 'refused', *extra, calls_factory=no_provider) == 2
    assert reason in capsys.readouterr().err
    assert not (tmp_path / 'refused/commitments.json').exists()


def test_legacy_freeze_and_budget_campaign(source, tmp_path):
    from ara.runtime.frozen import campaign_totals
    from ara.runtime.budget import Budget
    from ara.runtime.logging import EventLog
    run, _ = source
    def legacy(e):
        p = json.loads(e['payload_json'])
        if e['stage'] == 'commitments_frozen':
            p.pop('contract')
            p.pop('commitments_sha256')
        if e['stage'] == 'build_t' and e['label'] == 'MODEL':
            e['cost_usd'] = 20
        e['payload_json'] = json.dumps(p)
        return e
    rewrite(run, legacy)
    paths = [run / 'events.jsonl']
    for name in ('first', 'second'):
        directory = tmp_path / name
        assert candidate(source, directory) == 0
        paths.append(directory / 'events.jsonl')
        report = summary(directory)
        assert report['inherited_totals']['cost_usd'] == 20
        assert report['shared_frozen_t']['contract_basis'].startswith('legacy')
        local = events(directory)
        config = next(json.loads(e['payload_json'])['config'] for e in local if e['stage'] == 'run_started')
        budget = Budget(config, EventLog(directory / 'events.jsonl'))
        assert float(budget.used_cost) == report['cost_usd'] < 2
    expected = round(sum(summary(p.parent)['cost_usd'] for p in paths[1:]) +
                     sum(e['cost_usd'] for e in events(run)), 10)
    assert campaign_totals(paths)['cost_usd'] == expected
    assert campaign_totals(paths + paths)['cost_usd'] == expected
    assert campaign_totals(paths[1:])['cost_usd'] == round(20 + sum(summary(p.parent)['cost_usd'] for p in paths[1:]), 10)


def test_explicit_caps_required(source, tmp_path, capsys):
    run, config = source
    assert main(['run', '--smoke', '--provider', 'mock', '--config', str(config),
                 '--from-frozen', str(run), '--run-dir', str(tmp_path / 'refused')]) == 2
    assert 'requires explicit' in capsys.readouterr().err


def test_inherited_run_cannot_refreeze(source, tmp_path):
    from ara.runtime.cli import make_calls
    from ara.runtime.logging import EventLog
    from ara.runtime.orchestration import prepare_commitments
    from ara.bank import load_bank
    directory = tmp_path / 'candidate'
    assert candidate(source, directory) == 0
    config = next(json.loads(e['payload_json'])['config'] for e in events(directory) if e['stage'] == 'run_started')
    calls = make_calls(config, EventLog(directory / 'events.jsonl'), 'P Q')
    with pytest.raises(ValueError, match='already frozen'):
        prepare_commitments(calls, load_bank(ROOT / 'bank'), 'P', 'P')


def test_completed_via_later_select(tmp_path):
    config = yaml.safe_load((ROOT / 'config.yaml').read_text())
    config.update(config['smoke'])
    config['cache_dir'] = str(tmp_path / 'cache')
    path = tmp_path / 'config.yaml'
    path.write_text(yaml.safe_dump(config))
    directory = tmp_path / 'builder'
    assert main(['run', '--provider', 'mock', '--config', str(path), '--topic', 'P Q',
                 '--literature', str(ROOT / 'tests/fixtures/runtime/smoke-literature.txt'),
                 '--run-dir', str(directory)]) == 0
    assert candidate((directory, path), tmp_path / 'too-early') == 2
    route = next(json.loads(e['payload_json'])['graph']['id'] for e in events(directory)
                 if e['stage'] == 'route' and json.loads(e['payload_json'])['graph']['status'] == 'CLOSED')
    assert main(['select', '--run-dir', str(directory), '--route', route]) == 0
    assert candidate((directory, path), tmp_path / 'candidate') == 0


def test_writer_stage_change_allowed(source, tmp_path):
    _, path = source
    config = yaml.safe_load(path.read_text())
    config.setdefault('stages', {})['write_essay'] = {'effort': 'low'}
    path.write_text(yaml.safe_dump(config))
    assert candidate(source, tmp_path / 'writer') == 0


def test_effective_extraction_settings():
    from ara.runtime.frozen import construction_config
    config = yaml.safe_load((ROOT / 'config.yaml').read_text())
    same = json.loads(json.dumps(config))
    same['stages']['extraction']['max_output_tokens'] = config['max_output_tokens']
    assert construction_config(config) == construction_config(same)
    same['stages']['extraction']['effort'] = 'low'
    assert construction_config(config) != construction_config(same)
