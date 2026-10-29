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
    config['essay_min_words'] = 0  # Short boundary fixtures; profile minima have dedicated tests.
    provider = MockProvider({})
    log = EventLog(tmp_path / 'run' / 'events.jsonl')
    calls = ModelCalls(config, provider, log, Cache(tmp_path / 'cache'), ROOT, 'P')
    return calls, provider, log


def register(calls, provider, kind, inputs, value, **updates):
    if kind in ('map_leaf', 'propose_cuts'):
        from ara.runtime.search_context import leaf_slice
        inputs = leaf_slice(inputs, 8)
    provider.responses[mock_key(kind, calls.render(kind, inputs)[1])] = response(value, **updates)


def graph():
    return RouteGraph('r1', 'n1', (RouteNode('n1', Proposition('p', 'P', Formula('atom', name='P')), 'leaf', 't1'),), 'CLOSED')


def test_invalid_schema_rejected_logged_not_cached(rig):
    calls, provider, log = rig
    invalid = {'formula': {'op': 'atom', 'name': 'P'}, 'unknown': 'P'}
    register(calls, provider, 'formalise', {'proposition': {'id': 'p', 'text': 'P', 'formula': None}}, invalid)
    with pytest.raises(Rejected):
        calls.formalise(Proposition('p', 'P'))
    event = [e for e in log.read() if e['label'] == 'MODEL'][-1]
    assert json.loads(event['payload_json'])['status'] == 'rejected'
    assert event['prompt'] and json.loads(json.loads(event['response'])['content'][0]['text']) == invalid
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
    calls.config['validation_attempts'] = 3
    draft = {'title': 'P', 'body': '[[node:n1]] P Q', 'bibliography': []}
    register(calls, provider, 'audit_essay', calls.audit_inputs(graph(), draft),
             {'labels': [{'sentence': 1, 'node_ids': ['n1'], 'role': 'unsupported_claim', 'citation_supported': True}]})
    with pytest.raises(Rejected, match='audit'):
        calls.audit_essay(graph(), draft)
    assert provider.calls == 1
    assert not any(e['stage'] == 'validation_retry' for e in log.read())


@pytest.mark.parametrize('cap,value', [('token_cap', 15000), ('cost_cap_usd', .30)])
def test_actual_usage_cap_is_enforced_after_call(rig, cap, value):
    calls, provider, log = rig
    calls.config[cap] = value
    p = Proposition('p', 'P')
    register(calls, provider, 'formalise', {'proposition': p.to_dict()}, {'formula': {'op': 'atom', 'name': 'P'}},
             usage={'input_tokens': 50000, 'output_tokens': 50000})
    with pytest.raises(BudgetStop):
        calls.formalise(p)
    assert provider.calls == 1
    assert log.read()[-1]['label'] == 'STOP'
    assert calls.budget.used_tokens == 100000
    assert not list(calls.cache.path.glob('*.json'))


def test_transport_failure_charges_reservation_and_stops(rig):
    calls, provider, log = rig
    with pytest.raises(BudgetStop, match='actual spend unknown'):
        calls.formalise(Proposition('p', 'P'))
    event = next(e for e in log.read() if e['label'] == 'MODEL')
    assert json.loads(event['payload_json'])['accounting'] == 'reservation_unknown_actual'
    assert calls.budget.used_tokens > 0
    assert event['response'] is None
    with pytest.raises(BudgetStop, match='prior provider spend is unknown'):
        Budget(calls.config, log)


def test_ports_return_typed_values_and_enforce_references(rig):
    from ara.types import CommitmentSet, Commitment, CriticalQuestion, Proposal, CQAnswer, Tier1Repair
    calls, provider, log = rig
    commitments = CommitmentSet((Commitment('t1', 'P', 'placeholder:1', Formula('atom', name='P')),))
    question = CriticalQuestion('cq1', '{P}')
    proposal = Proposal('scheme', (), 'Q')
    inputs = {'question': question.to_dict(), 'proposal': proposal.to_dict(), 'commitments': commitments.to_dict(), **calls.search_vocabulary(commitments)}
    register(calls, provider, 'answer_cq', inputs,
             {'cq_id': 'cq1', 'answer': 'P', 'answered': True, 'supporting_t_ids': ['t1']})
    assert calls.answer_cq(question, proposal, commitments) == CQAnswer('cq1', 'P', True, ('t1',))
    repair_input = {'premises': [], 'conclusions': [], 'commitments': commitments.to_dict()}
    register(calls, provider, 'tier1_repair', repair_input, {'action': 'unresolved', 'detail': 'P', 'proposals': []})
    assert calls.repair_tier1((), (), commitments) == Tier1Repair('unresolved', 'P', ())
    leaf = Proposition('q', 'Q')
    from ara.runtime.search_alignment import search_guidance
    from ara.bank import load_bank
    register(calls, provider, 'map_leaf', {'leaf': leaf.to_dict(), 'commitments': commitments.to_dict(), **calls.search_vocabulary(commitments), **search_guidance(leaf,commitments,load_bank(calls.root/'bank').entries)}, {'t_id': 'missing'})
    with pytest.raises(Rejected, match='unknown T id'):
        calls.map_leaf(leaf, commitments)


def test_named_position_preserved(rig):
    from ara.types import Commitment, CommitmentSet
    calls, provider, log = rig
    formula = Formula('atom', name='P')
    from test_search_alignment import T as commitments
    formula = Formula('atom', name='R')
    from ara.bank import load_bank
    from ara.runtime.target_policy import target_context, classifier_inputs
    inputs = {'commitments': commitments.to_dict(), 'count': 1, 'keep_count': 1, 'attempt': 1, 'attempt_budget': 3, 'named_position': 'R',
              **calls.search_vocabulary(commitments), **target_context(commitments, load_bank(calls.root / 'bank'))}
    register(calls, provider, 'propose_targets', inputs, {'targets': [{'id': 'p', 'text': 'R', 'formula': None}]})
    register(calls, provider, 'formalise', {'proposition': Proposition('p', 'R').to_dict(),
             **calls.search_vocabulary(commitments),
             'vocabulary_instruction': 'Reuse catalogue definitions and signatures; preserve the proposition meaning.'},
             {'formula': formula.to_dict()})
    register(calls, provider, 'classify_target', classifier_inputs(Proposition('p', 'R', formula), calls.search_vocabulary(commitments), commitments), dict(novelty='new_assertion',fidelity='matches',classification='own_thesis', reason='P'))
    assert calls.propose_targets(commitments, named_position='R') == (Proposition('p', 'R', formula),)


def test_essay_bibliography_excluded_but_title_included(rig):
    calls, provider, _ = rig
    calls.config['essay_word_limit'] = 6000
    draft = {'title': 'P', 'body': '[[node:n1]] ' + ' '.join(['P'] * 5998),
             'bibliography': [{'id': 'c1', 'text': ' '.join(['Q'] * 7000), 'url': None}]}
    register(calls, provider, 'write_essay', calls.essay_inputs(graph()), draft)
    assert calls.write_essay(graph()) == draft


def test_unknown_cache_ttl_uses_expensive_rate(rig):
    from ara.types import TokenUsage
    calls, _, _ = rig
    assert float(calls.budget.cost(TokenUsage(cache_write_tokens=1000000))) == 10.0


def test_full_local_schema_reaches_provider_and_log(rig, monkeypatch):
    calls, provider, log = rig
    proposition = Proposition('p', 'P')
    register(calls, provider, 'formalise', {'proposition': proposition.to_dict()},
             {'formula': Formula('atom', name='P').to_dict()})
    prompts = []
    complete = provider.complete
    def capture(kind, prompt, schema, maximum):
        prompts.append(prompt)
        return complete(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'complete', capture)
    assert calls.formalise(proposition) == Formula('atom', name='P')
    assert len(prompts) == 1
    assert '\nLOCAL_RESPONSE_SCHEMA (all constraints are mandatory)\n' in prompts[0]
    schema_text = prompts[0].split('\nLOCAL_RESPONSE_SCHEMA (all constraints are mandatory)\n')[1].split('\nINPUT_JSON\n')[0]
    assert json.loads(schema_text) == json.loads((ROOT / 'schemas/formalise.json').read_text())
    event = next(e for e in log.read() if e['label'] == 'MODEL')
    assert event['prompt'] == prompts[0]


@pytest.mark.parametrize('limit_retry', [False, True])
def test_validation_retry_is_accounted_and_admitted(rig, limit_retry):
    calls, provider, log = rig
    calls.config['validation_attempts'] = 3
    entry = {'id': 'c1', 'text': 'P', 'citation': 'placeholder:1',
             'formula': Formula('atom', name='P').to_dict()}
    invalid, valid = {'commitments': [entry, entry]}, {'commitments': [entry]}
    inputs = {'literature': 'P', 'audience': 'P'}
    register(calls, provider, 'build_t', inputs, invalid)
    feedback = {'error': 'duplicate commitment id', 'rejected_response': canonical(invalid),
                'instruction': 'Return a new response satisfying every local schema and reference constraint.'}
    register(calls, provider, 'build_t', {**inputs, 'validation_feedback': feedback}, valid)
    if limit_retry:
        prompt = calls.render('build_t', inputs)[1]
        calls.config['token_cap'] = len(prompt.encode()) + calls.config['max_output_tokens']
        with pytest.raises(BudgetStop):
            calls.build_t('P', 'P')
        assert provider.calls == 1
        assert log.read()[-1]['label'] == 'STOP'
        assert not list(calls.cache.path.glob('*.json'))
    else:
        assert calls.build_t('P', 'P').get('c1').citation == 'placeholder:1'
        assert provider.calls == 2
        models = [e for e in log.read() if e['label'] == 'MODEL']
        assert [json.loads(e['payload_json'])['status'] for e in models] == ['rejected', 'accepted']
        assert all(e['cost_usd'] > 0 and e['usage']['input_tokens'] > 0 for e in models)
        assert calls.budget.used_tokens == 16
        assert len(list(calls.cache.path.glob('*.json'))) == 1
        assert any(e['stage'] == 'validation_retry' for e in log.read())
