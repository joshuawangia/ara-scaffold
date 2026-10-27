"""Writer retries preserve inputs, validation, and accounting."""
from decimal import Decimal
import json

import pytest
import yaml

from ara.runtime.cli import main
from ara.runtime.logging import EventLog
from ara.runtime.providers import Response
from ara.types import Proposition, RouteGraph, RouteNode
from test_calls import register, response, rig
from test_cli import cli_setup


def route():
    return RouteGraph('r', 'n0', (RouteNode('n0', Proposition('p', 'P'), 'leaf'),
                                 RouteNode('n1', Proposition('q', 'Q'), 'leaf')))


VALID = {'title': 'P', 'body': '[[node:n0]] P. [[node:n1]] Q.', 'bibliography': []}
MARKERS = 'essay writer: node marker coverage mismatch'
BODY = 'essay writer: body needs at least two text tokens'


def correction(provider, invalid, corrected, monkeypatch):
    replies = iter([invalid, corrected])
    requests = []
    def complete(kind, prompt, schema, maximum):
        provider.calls += 1
        requests.append((kind, prompt, schema, maximum))
        return Response(response(next(replies)))
    monkeypatch.setattr(provider, 'complete', complete)
    return requests


@pytest.mark.parametrize('body,error', [
    ('x', MARKERS),
    ('[[node:n0]] P. Q.', MARKERS),
    ('[[node:n0]] [[node:n1]] x', BODY),
    ('[[node:n0]] [[node:n1]] [cite:c1] x', BODY),
    ('[[node:n0]] [[node:n1]] . !', BODY),
    ('[[node:n0]] [[node:n1]]', BODY),
    ('[[node:n0]] P. [[node:n1]] Q. [[node:n2]]', MARKERS),
])
def test_invalid_writer_corrects_before_audit(rig, body, error, monkeypatch):
    calls, provider, log = rig
    calls.config['validation_attempts'] = 3
    invalid = {'title': 'x' if body == 'x' else 'P [[node:n1]]', 'body': body, 'bibliography': []}
    requests = correction(provider, invalid, VALID, monkeypatch)
    assert calls.write_essay(route()) == VALID
    assert provider.calls == 2
    assert requests[0] == requests[1]
    assert "validation_feedback" not in requests[1][1]
    events = log.read()
    models = [e for e in events if e['label'] == 'MODEL']
    assert [json.loads(e['payload_json'])['status'] for e in models] == ['rejected', 'accepted']
    assert json.loads(models[0]['payload_json'])['reason'] == error
    assert [json.loads(e['payload_json'])['attempt'] for e in models] == [1, 2]
    assert models[0]['prompt'].encode() == models[1]['prompt'].encode()
    assert json.loads(Response(json.loads(models[0]['response'])).text()) == invalid
    assert calls.budget.used_tokens == 16
    assert calls.budget.used_cost == sum((Decimal(str(e['cost_usd'])) for e in models), Decimal(0)) > 0
    assert [json.loads(e['payload_json'])['next_attempt'] for e in events if e['stage'] == 'validation_retry'] == [2]
    assert not any(e['stage'] in ('audit_essay', 'essay_audit') for e in events)
    saved = list(calls.cache.path.glob('*.json'))
    assert len(saved) == 1
    assert json.loads(Response(json.loads(saved[0].read_text())['raw']).text()) == VALID


@pytest.mark.parametrize('underlength', [False, True])
def test_writer_correction_exhaustion_clean_cli_stop(cli_setup, tmp_path, monkeypatch, underlength):
    config, provider, _, factory, engine_factory = cli_setup
    complete = provider.complete
    def reject_writer(kind, prompt, schema, maximum):
        if kind == 'write_essay':
            provider.calls += 1
            return Response(response({'title': 'P', 'body': '[[node:n:p]][[node:n:p:c]][[node:n:p:a]] P Q' if underlength else 'x', 'bibliography': []}))
        return complete(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'complete', reject_writer)
    run = tmp_path / 'exhausted'
    assert main(['run', '--smoke', '--config', str(config), '--run-dir', str(run)],
                calls_factory=factory, engine_factory=engine_factory) == 2
    events = EventLog(run / 'events.jsonl').read()
    writers = [e for e in events if e['label'] == 'MODEL' and e['stage'] == 'write_essay']
    assert len(writers) == 4
    assert all(json.loads(e['payload_json'])['status'] == 'rejected' for e in writers)
    assert all(e['cost_usd'] > 0 and e['usage']['input_tokens'] > 0 for e in writers)
    assert [json.loads(e['payload_json'])['next_attempt'] for e in events if e['stage'] == 'validation_retry'] == [2, 3, 4]
    assert not any(e['stage'] in ('audit_essay', 'essay_audit', 'final_draft') for e in events)
    error = next(json.loads(e['payload_json']) for e in events if e['stage'] == 'runtime_error')
    reason = 'essay writer: minimum words not reached' if underlength else MARKERS
    assert error == {'error_type': 'InvalidOutput', 'message': reason}
    assert len({e['prompt'] for e in writers}) == 1
    assert sum(sum(e['usage'].values()) for e in writers) == 32
    assert sum(Decimal(str(e['cost_usd'])) for e in writers) == Decimal('0.0004')
    calls = factory(yaml.safe_load(config.read_text()), EventLog(run / 'events.jsonl'), 'P Q')
    for event in writers:
        assert calls.cache.get(json.loads(event['payload_json'])['cache_key']) is None
    assert (run / 'export/methodology.md').is_file()
    assert list((run / 'routes').glob('*.json'))
    assert not (run / 'draft.json').exists()
    assert not (run / 'export/essay.txt').exists()


@pytest.mark.parametrize('succeeds', [False, True])
def test_underlength_four_attempts_accounted(rig, monkeypatch, succeeds):
    calls, provider, log = rig
    calls.config['essay_min_words'] = 10
    short = {**VALID, 'bibliography': [{'id': 'c1', 'text': 'P ' * 100, 'url': None}]}
    valid = {**VALID, 'body': VALID['body'] + ' P' * 5}
    outputs = iter([short] * 3 + [valid if succeeds else short])
    requests = []
    def complete(kind, prompt, schema, maximum):
        provider.calls += 1
        requests.append((kind, prompt, schema, maximum))
        return Response(response(next(outputs)))
    monkeypatch.setattr(provider, 'complete', complete)
    if succeeds:
        assert calls.write_essay(route()) == valid
    else:
        from ara.runtime.calls import InvalidOutput
        with pytest.raises(InvalidOutput, match='minimum words'):
            calls.write_essay(route())
    assert provider.calls == 4
    assert all(r == requests[0] for r in requests)
    assert 'validation_feedback' not in requests[0][1]
    writers = [e for e in log.read() if e['label'] == 'MODEL']
    assert len(writers) == 4
    assert [json.loads(e['payload_json'])['attempt'] for e in writers] == [1, 2, 3, 4]
    assert all(json.loads(e['payload_json'])['reason'] == 'essay writer: minimum words not reached'
               for e in writers[:3 if succeeds else 4])
    assert calls.budget.used_tokens == 32
    assert calls.budget.used_cost == sum((Decimal(str(e['cost_usd'])) for e in writers), Decimal(0)) > 0
    assert len(list(calls.cache.path.glob('*.json'))) == int(succeeds)


@pytest.mark.parametrize('stop_reason', ['refusal', 'max_tokens'])
def test_writer_provider_stops_are_final(rig, stop_reason):
    from ara.runtime.calls import Rejected
    calls, provider, log = rig
    register(calls, provider, 'write_essay', calls.essay_inputs(route()), VALID, stop_reason=stop_reason)
    with pytest.raises(Rejected, match=stop_reason):
        calls.write_essay(route())
    assert provider.calls == 1
    assert not any(e['stage'] == 'validation_retry' for e in log.read())


def test_writer_retry_requires_new_admission(rig, monkeypatch):
    from ara.runtime.budget import BudgetStop
    calls, provider, log = rig
    def complete(kind, prompt, schema, maximum):
        provider.calls += 1
        # First request has already been admitted. Its actual usage fits, but
        # the next request's conservative reservation cannot fit this cap.
        calls.config['token_cap'] = 8
        return Response(response({'title': 'P', 'body': 'P', 'bibliography': []}))
    monkeypatch.setattr(provider, 'complete', complete)
    with pytest.raises(BudgetStop, match='reservation exceeds'):
        calls.write_essay(route())
    assert provider.calls == 1 and calls.budget.used_tokens == 8
    assert log.read()[-1]['label'] == 'STOP'
    assert not list(calls.cache.path.glob('*.json'))
