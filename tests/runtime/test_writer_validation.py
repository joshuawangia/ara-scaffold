"""B13 writer structure validation uses the existing bounded correction path."""
from decimal import Decimal
import json

import pytest
import yaml

from ara.runtime.cache import canonical
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


def correction(calls, provider, graph, invalid, error, corrected):
    inputs = calls.essay_inputs(graph)
    register(calls, provider, 'write_essay', inputs, invalid)
    register(calls, provider, 'write_essay', {**inputs, 'validation_feedback': {
        'error': error, 'rejected_response': canonical(invalid),
        'instruction': 'Return a new response satisfying every local schema and reference constraint.'}}, corrected)


@pytest.mark.parametrize('body,error', [
    ('x', MARKERS),
    ('[[node:n0]] P. Q.', MARKERS),
    ('[[node:n0]] [[node:n1]] x', BODY),
    ('[[node:n0]] [[node:n1]] [cite:c1] x', BODY),
    ('[[node:n0]] [[node:n1]] . !', BODY),
    ('[[node:n0]] [[node:n1]]', BODY),
    ('[[node:n0]] P. [[node:n1]] Q. [[node:n2]]', MARKERS),
])
def test_invalid_writer_corrects_before_audit(rig, body, error):
    calls, provider, log = rig
    calls.config['validation_attempts'] = 3
    invalid = {'title': 'x' if body == 'x' else 'P [[node:n1]]', 'body': body, 'bibliography': []}
    correction(calls, provider, route(), invalid, error, VALID)
    assert calls.write_essay(route()) == VALID
    assert provider.calls == 2
    events = log.read()
    models = [e for e in events if e['label'] == 'MODEL']
    assert [json.loads(e['payload_json'])['status'] for e in models] == ['rejected', 'accepted']
    assert json.loads(models[0]['payload_json'])['reason'] == error
    assert json.loads(Response(json.loads(models[0]['response'])).text()) == invalid
    assert calls.budget.used_tokens == 16
    assert calls.budget.used_cost == sum((Decimal(str(e['cost_usd'])) for e in models), Decimal(0)) > 0
    assert [json.loads(e['payload_json'])['next_attempt'] for e in events if e['stage'] == 'validation_retry'] == [2]
    assert not any(e['stage'] in ('audit_essay', 'essay_audit') for e in events)
    saved = list(calls.cache.path.glob('*.json'))
    assert len(saved) == 1
    assert json.loads(Response(json.loads(saved[0].read_text())['raw']).text()) == VALID


def test_writer_correction_exhaustion_clean_cli_stop(cli_setup, tmp_path, monkeypatch):
    config, provider, _, factory, engine_factory = cli_setup
    complete = provider.complete
    def reject_writer(kind, prompt, schema, maximum):
        if kind == 'write_essay':
            provider.calls += 1
            return Response(response({'title': 'x', 'body': 'x', 'bibliography': []}))
        return complete(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'complete', reject_writer)
    run = tmp_path / 'exhausted'
    assert main(['run', '--smoke', '--config', str(config), '--run-dir', str(run)],
                calls_factory=factory, engine_factory=engine_factory) == 2
    events = EventLog(run / 'events.jsonl').read()
    writers = [e for e in events if e['label'] == 'MODEL' and e['stage'] == 'write_essay']
    assert len(writers) == 3
    assert all(json.loads(e['payload_json'])['status'] == 'rejected' for e in writers)
    assert all(e['cost_usd'] > 0 and e['usage']['input_tokens'] > 0 for e in writers)
    assert [json.loads(e['payload_json'])['next_attempt'] for e in events if e['stage'] == 'validation_retry'] == [2, 3]
    assert not any(e['stage'] in ('audit_essay', 'essay_audit', 'final_draft') for e in events)
    error = next(json.loads(e['payload_json']) for e in events if e['stage'] == 'runtime_error')
    assert error == {'error_type': 'InvalidOutput', 'message': MARKERS}
    calls = factory(yaml.safe_load(config.read_text()), EventLog(run / 'events.jsonl'), 'P Q')
    for event in writers:
        assert calls.cache.get(json.loads(event['payload_json'])['cache_key']) is None
    assert (run / 'export/methodology.md').is_file()
    assert list((run / 'routes').glob('*.json'))
    assert not (run / 'draft.json').exists()
    assert not (run / 'export/essay.txt').exists()
