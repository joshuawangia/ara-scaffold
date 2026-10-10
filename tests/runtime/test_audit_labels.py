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
