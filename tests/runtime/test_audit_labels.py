"""Sentence inventory and computed audit verdicts over placeholders."""
import json

import pytest

from ara.runtime.calls import Rejected
from test_calls import graph, register, rig


def test_sentence_splitter_excludes_bibliography(rig):
    calls, _, _ = rig
    inputs = calls.audit_inputs(graph(), {'body': '[[node:n1]] P. Q!\nR? S',
        'bibliography': [{'id': 'c1', 'text': 'Q.'}]})
    assert inputs == {'sentences': [{'sentence': 1, 'text': 'P.'}, {'sentence': 2, 'text': 'Q!'},
                                   {'sentence': 3, 'text': 'R?'}, {'sentence': 4, 'text': 'S'}],
                      'outline': {'nodes': [{'id': 'n1', 'text': 'P'}], 'links': []}}


@pytest.mark.parametrize('variant', ['missing', 'unknown_node', 'unknown_sentence', 'duplicate', 'absent', 'faithful', 'unsupported_marker'])
def test_invalid_labels_cannot_approve(rig, variant):
    calls, provider, log = rig
    draft = {'title': 'P', 'body': '[[node:n1]] P', 'bibliography': []}
    value = {'labels': [{'sentence': 1, 'node_ids': ['n1'], 'asserts_premise_or_inference_not_in_outline': False}]}
    if variant == 'missing': value['labels'][0]['node_ids'] = []
    if variant == 'unknown_node': value['labels'][0]['node_ids'] = ['n1', 'n2']
    if variant == 'unknown_sentence': value['labels'][0]['sentence'] = 2
    if variant == 'duplicate': value['labels'] *= 2
    if variant == 'absent': value['labels'] = []
    if variant == 'faithful':
        value['faithful'] = True
        value['labels'][0]['node_ids'] = []
    if variant == 'unsupported_marker': draft['body'] = 'Q'
    register(calls, provider, 'audit_essay', calls.audit_inputs(graph(), draft), value)
    with pytest.raises(Rejected): calls.audit_essay(graph(), draft)
    assert provider.calls == 1
    assert not list(calls.cache.path.glob('*.json'))
    if variant == 'missing':
        event = next(e for e in log.read() if e['stage'] == 'essay_audit')
        assert json.loads(event['payload_json']) == {
            'covered_node_ids': [], 'missing_node_ids': ['n1'], 'extra_steps': [], 'faithful': False}


def test_valid_labels_compute_verdict_and_record_it(rig):
    calls, provider, log = rig
    draft = {'title': 'P', 'body': '[[node:n1]] P', 'bibliography': []}
    value = {'labels': [{'sentence': 1, 'node_ids': ['n1'], 'asserts_premise_or_inference_not_in_outline': False}]}
    register(calls, provider, 'audit_essay', calls.audit_inputs(graph(), draft), value)
    assert calls.audit_essay(graph(), draft) == {
        'covered_node_ids': ['n1'], 'missing_node_ids': [], 'extra_steps': [], 'faithful': True}


def test_valid_id_semantic_mislabel_is_model_boundary(rig):
    # Code cannot prove that natural-language text expresses an existing node.
    # This pins the disclosed boundary; ids/markers alone are not a semantic proof.
    calls, provider, _ = rig
    draft = {'title': 'Q', 'body': '[[node:n1]] Q', 'bibliography': []}
    register(calls, provider, 'audit_essay', calls.audit_inputs(graph(), draft),
        {'labels': [{'sentence': 1, 'node_ids': ['n1'], 'asserts_premise_or_inference_not_in_outline': False}]})
    assert calls.audit_essay(graph(), draft)['faithful'] is True


@pytest.mark.parametrize('malformed', ['partial', 'duplicate', 'unknown'])
def test_malformed_audit_inventory_corrects_before_verdict(rig, monkeypatch, malformed):
    """Observed live shape: one returned label for a fifteen-sentence input."""
    from ara.runtime.providers import Response
    from test_calls import response
    calls, provider, log = rig
    calls.config['validation_attempts'] = 3
    draft = {'title': 'P', 'body': '[[node:n1]] ' + ' '.join(['P.'] * 15), 'bibliography': []}
    good = {'labels': [{'sentence': i, 'node_ids': ['n1'],
                       'asserts_premise_or_inference_not_in_outline': False}
                      for i in range(1, 16)]}
    bad = {'labels': [dict(good['labels'][0])]}
    if malformed == 'duplicate': bad['labels'] *= 15
    if malformed == 'unknown': bad['labels'][0]['sentence'] = 16
    replies = iter([bad, good])
    prompts = []
    def complete(kind, prompt, schema, maximum):
        provider.calls += 1
        prompts.append(prompt)
        return Response(response(next(replies)))
    monkeypatch.setattr(provider, 'complete', complete)
    assert calls.audit_essay(graph(), draft)['faithful']
    assert provider.calls == 2
    corrected = json.loads(prompts[1].split('\nINPUT_JSON\n')[1])
    assert corrected['validation_feedback']['error'] == 'essay audit: sentence inventory mismatch'
    assert json.loads(corrected['validation_feedback']['rejected_response']) == bad
    events = log.read()
    models = [e for e in events if e['label'] == 'MODEL']
    assert [json.loads(e['payload_json'])['status'] for e in models] == ['rejected', 'accepted']
    assert calls.budget.used_tokens == 16 and all(e['cost_usd'] > 0 for e in models)
    assert len([e for e in events if e['stage'] == 'essay_audit']) == 1
    saved = list(calls.cache.path.glob('*.json'))
    assert len(saved) == 1
    assert json.loads(Response(json.loads(saved[0].read_text())['raw']).text()) == good


def test_malformed_audit_retry_requires_new_admission(rig):
    from ara.runtime.budget import BudgetStop, tokens
    calls, provider, log = rig
    calls.config['validation_attempts'] = 3
    draft = {'title': 'P', 'body': '[[node:n1]] P. Q.', 'bibliography': []}
    inputs = calls.audit_inputs(graph(), draft)
    prompt = calls.render('audit_essay', inputs)[1]
    schema = json.loads((calls.root / 'schemas/audit_essay.json').read_text())
    calls.config['token_cap'] = tokens(provider.estimate('audit_essay', prompt, schema, calls.config['max_output_tokens']))
    register(calls, provider, 'audit_essay', inputs, {'labels': []})
    with pytest.raises(BudgetStop, match='reservation'):
        calls.audit_essay(graph(), draft)
    assert provider.calls == 1
    assert not list(calls.cache.path.glob('*.json'))
    assert any(e['stage'] == 'validation_retry' for e in log.read())


def test_incomplete_audit_with_extra_inference_is_still_final(rig, monkeypatch):
    from ara.runtime.providers import Response
    from test_calls import response
    calls, provider, log = rig
    calls.config['validation_attempts'] = 3
    draft = {'title': 'P', 'body': '[[node:n1]] P. Q.', 'bibliography': []}
    partial_adverse = {'labels': [{'sentence': 1, 'node_ids': ['n1'],
                                  'asserts_premise_or_inference_not_in_outline': True}]}
    def complete(kind, prompt, schema, maximum):
        provider.calls += 1
        return Response(response(partial_adverse))
    monkeypatch.setattr(provider, 'complete', complete)
    with pytest.raises(Rejected):
        calls.audit_essay(graph(), draft)
    assert provider.calls == 1
    assert not any(e['stage'] == 'validation_retry' for e in log.read())
    assert not list(calls.cache.path.glob('*.json'))
