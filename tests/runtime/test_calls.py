import copy
import json
from pathlib import Path

import pytest
import yaml

from ara.runtime.budget import Budget, BudgetStop
from ara.runtime.cache import Cache, canonical
from ara.runtime.calls import ModelCalls, Rejected
from ara.runtime.logging import EventLog
from ara.runtime.providers import MockProvider, mock_key
from ara.types import Formula, Proposition, RouteGraph, RouteNode

ROOT = Path(__file__).resolve().parents[2]


def response(value, **updates):
    raw = {'model': 'claude-opus-5', 'stop_reason': 'end_turn',
           'content': [{'type': 'text', 'text': canonical(value)}],
           'usage': {'input_tokens': 5, 'output_tokens': 3}}
    raw.update(updates)
    return raw


@pytest.fixture
def rig(tmp_path):
    config = yaml.safe_load((ROOT / 'config.yaml').read_text())
    provider = MockProvider({})
    log = EventLog(tmp_path / 'run' / 'events.jsonl')
    calls = ModelCalls(config, provider, log, Cache(tmp_path / 'cache'), ROOT, 'P')
    return calls, provider, log


def register(calls, provider, kind, inputs, value, **updates):
    provider.responses[mock_key(kind, calls.render(kind, inputs)[1])] = response(value, **updates)


def graph():
    return RouteGraph('r1', 'n1', (RouteNode('n1', Proposition('p', 'P', Formula('atom', name='P')), 'leaf', 't1'),), 'CLOSED')


def test_invalid_schema_rejected_logged_not_cached(rig):
    calls, provider, log = rig
    register(calls, provider, 'formalise', {'proposition': {'id': 'p', 'text': 'P', 'formula': None}}, {})
    with pytest.raises(Rejected):
        calls.formalise(Proposition('p', 'P'))
    event = [e for e in log.read() if e['label'] == 'MODEL'][-1]
    assert json.loads(event['payload_json'])['status'] == 'rejected'
    assert event['prompt'] and json.loads(event['response'])['content'][0]['text'] == '{}'
    assert not list(calls.cache.path.glob('*.json'))


def test_cache_hit_identical_no_provider_call(rig):
    calls, provider, log = rig
    p = Proposition('p', 'P')
    register(calls, provider, 'formalise', {'proposition': p.to_dict()}, {'formula': {'op': 'atom', 'name': 'P'}})
    first = calls.formalise(p)
    provider.responses.clear()
    assert calls.formalise(p) == first
    assert provider.calls == 1
    last = log.read()[-1]
    assert json.loads(last['payload_json'])['cache_hit']
    assert sum(last['usage'].values()) == 0


@pytest.mark.parametrize('cap,value', [('token_cap', 1), ('cost_cap_usd', 0)])
def test_caps_stop_with_partial_artifact(rig, cap, value):
    calls, provider, log = rig
    calls.config[cap] = value
    with pytest.raises(BudgetStop):
        calls.formalise(Proposition('p', 'P'))
    assert provider.calls == 0
    assert log.read()[-1]['label'] == 'STOP'
    partial = json.loads((log.path.parent / 'partial.json').read_text())
    assert partial['status'] == 'STOPPED' and partial['reason'].startswith(cap.split('_')[0])


def test_essay_word_cap(rig):
    calls, provider, log = rig
    draft = {'title': 'P', 'body': ' '.join(['P'] * 6000), 'bibliography': []}
    register(calls, provider, 'write_essay', calls.essay_inputs(graph()), draft)
    with pytest.raises(Rejected, match='word limit'):
        calls.write_essay(graph())
    assert json.loads(log.read()[-1]['payload_json'])['status'] == 'rejected'


def test_audit_rejects_extra_step(rig):
    calls, provider, log = rig
    draft = {'title': 'P', 'body': '[[node:n1]] P Q', 'bibliography': []}
    register(calls, provider, 'audit_essay', {'route': graph().to_dict(), 'draft': draft},
             {'faithful': True, 'covered_node_ids': ['n1'], 'missing_node_ids': [], 'extra_steps': ['Q']})
    with pytest.raises(Rejected, match='audit'):
        calls.audit_essay(graph(), draft)
