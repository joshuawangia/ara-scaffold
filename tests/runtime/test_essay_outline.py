"""B12: the writer and auditor consume the same expressible material."""
import json
from dataclasses import replace

import pytest

from ara.runtime.calls import Rejected
from ara.types import CQAnswer, PremiseFill, Proposal, Proposition, ProofScope, RouteGraph, RouteNode
from test_calls import graph, register, rig


def scheme_route():
    proposal = Proposal('cause_to_effect', (PremiseFill('causal_rule', 'P'),
        PremiseFill('cause', 'Q'), PremiseFill('conditions', 'S')), 'R')
    return RouteGraph('r', 'n0', (
        RouteNode('n0', Proposition('r', 'R'), 'inference', proposal=proposal,
            children=('n1', 'n2', 'n3'), cq_answers=(CQAnswer('cq1', 'S', True, ('t3',)),
                                                  CQAnswer('cq2', 'P', False))),
        RouteNode('n1', Proposition('p', 'P'), 'leaf', 't1'),
        RouteNode('n2', Proposition('q', 'Q'), 'leaf', 't2'),
        RouteNode('n3', Proposition('s', 'S'), 'leaf', 't3')),
        'OPEN', ('n0',), dialectical_cost=1.0)


def test_writer_and_auditor_receive_same_content_only_outline(rig, monkeypatch):
    calls, provider, log = rig
    route = scheme_route()
    expected = {'nodes': [{'id': 'n0', 'text': 'R'}, {'id': 'n1', 'text': 'P'},
                          {'id': 'n2', 'text': 'Q'}, {'id': 'n3', 'text': 'S'}],
                'links': [{'premises': ['n1', 'n2', 'n3'], 'conclusion': 'n0',
                           'scheme': 'Cause to effect',
                           'answered_questions': [{'question': 'Are S satisfied?', 'answer': 'S'}]}]}
    draft = {'title': 'R', 'body': '[[node:n0]] R [[node:n1]] P [[node:n2]] Q [[node:n3]] S', 'bibliography': []}
    register(calls, provider, 'write_essay', calls.essay_inputs(route), draft)
    register(calls, provider, 'audit_essay', calls.audit_inputs(route, draft),
        {'labels': [{'sentence': 1, 'node_ids': ['n0', 'n1', 'n2', 'n3'],
                     'asserts_premise_or_inference_not_in_outline': False}]})
    requests = []
    complete = provider.complete
    def capture(kind, prompt, schema, maximum):
        requests.append((kind, json.loads(prompt.split('\nINPUT_JSON\n')[1])))
        return complete(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'complete', capture)
    calls.write_essay(route)
    assert calls.audit_essay(route, draft)['faithful'] is True
    assert requests[0] == ('write_essay', {'topic': 'P', 'outline': expected,
        'word_limit': calls.config['essay_word_limit'], 'minimum_words': 0, 'feedback': []})
    assert requests[1][0] == 'audit_essay' and requests[1][1]['outline'] == expected
    assert set(requests[1][1]) == {'topic', 'outline', 'sentences'}
    model_events = [e for e in log.read() if e['label'] == 'MODEL']
    assert [json.loads(e['prompt'].split('\nINPUT_JSON\n')[1]) for e in model_events] == [r[1] for r in requests]


def test_route_status_and_cost_never_reach_writer(rig):
    calls, _, _ = rig
    route = scheme_route()
    other = replace(route, status='CLOSED', frontier=(), dialectical_cost=999.0, id='other')
    # These were the metadata narrated in F7. Neither version is expressible input.
    first, second = calls.essay_inputs(route), calls.essay_inputs(other)
    assert first == second
    assert set(first) == {'outline', 'word_limit', 'minimum_words', 'feedback'}
    assert set(first['outline']) == {'nodes', 'links'}
    assert all(set(n) == {'id', 'text'} for n in first['outline']['nodes'])


def test_outline_preserves_assumption_discharge(rig):
    calls, _, _ = rig
    route = RouteGraph('r', 'n0', (
        RouteNode('n0', Proposition('r', 'P implies Q'), 'inference',
            proposal=Proposal('conditional_proof', (PremiseFill('assumption', 'P'), PremiseFill('result', 'Q')), 'P implies Q'),
            children=('n1', 'n2')),
        RouteNode('n1', Proposition('p', 'P'), 'assumption', scope_id='local'),
        RouteNode('n2', Proposition('q', 'Q'), 'leaf', scope_id='local')),
        scopes=(ProofScope('local', 'n1', ('n2',), 'n0'),))
    assert calls.essay_outline(route)['links'] == [{
        'premises': ['n1', 'n2'], 'conclusion': 'n0', 'scheme': 'Conditional proof',
        'answered_questions': [], 'assumptions': ['n1'], 'scoped_results': ['n2']}]


def test_transition_without_new_premise_is_not_extra(rig):
    calls, provider, _ = rig
    draft = {'title': 'P', 'body': '[[node:n1]] P. Next.', 'bibliography': []}
    register(calls, provider, 'audit_essay', calls.audit_inputs(graph(), draft), {'labels': [
        {'sentence': 1, 'node_ids': ['n1'], 'asserts_premise_or_inference_not_in_outline': False},
        {'sentence': 2, 'node_ids': [], 'asserts_premise_or_inference_not_in_outline': False}]})
    assert calls.audit_essay(graph(), draft) == {'covered_node_ids': ['n1'], 'missing_node_ids': [],
                                               'extra_steps': [], 'faithful': True}


def test_unknown_scheme_name_is_not_invented(rig):
    calls, provider, _ = rig
    route = scheme_route()
    root = replace(route.nodes[0], proposal=replace(route.nodes[0].proposal, bank_id='unknown'))
    with pytest.raises(Rejected, match='unknown bank entry'):
        calls.essay_outline(replace(route, nodes=(root, *route.nodes[1:])))
    assert provider.calls == 0
