"""Typed sentence roles preserve substantive audit failures, using placeholders."""
import pytest

from ara.runtime.calls import EssayAuditFailed
from test_calls import graph, register, rig


def label(number, role='argument_step', nodes=('n1',), supported=True):
    return dict(sentence=number, role=role, node_ids=list(nodes), citation_supported=supported)


@pytest.mark.parametrize('role', ['framing', 'exposition', 'signpost', 'objection', 'reply'])
def test_typed_nonsubstantive_roles_do_not_require_node_mapping(rig, role):
    calls, provider, _ = rig
    draft = dict(title='P', body='[[node:n1]] P. Q.', bibliography=[])
    register(calls, provider, 'audit_essay', calls.audit_inputs(graph(), draft),
             {'labels': [label(1), label(2, role, ())]})
    result = calls.audit_essay(graph(), draft)
    assert result['faithful'] and result['role_counts'][role] == 1


def test_root_conclusion_is_explicit_and_a_mapped_argument_step(rig):
    calls, provider, _ = rig
    draft = dict(title='P', body='[[node:n1]] P.', bibliography=[])
    inputs = calls.audit_inputs(graph(), draft)
    assert inputs['root_conclusion'] == {'node_id': 'n1', 'text': 'P'}
    register(calls, provider, 'audit_essay', inputs, {'labels': [label(1)]})
    assert calls.audit_essay(graph(), draft)['faithful']


@pytest.mark.parametrize('role,nodes,reason', [
    ('unsupported_claim', ('n1',), 'unsupported_claim'),
    ('argument_step', (), 'unmapped_argument_step'),
])
def test_typed_substantive_failures_reject(rig, role, nodes, reason):
    calls, provider, log = rig
    draft = dict(title='P', body='[[node:n1]] P. Q.', bibliography=[])
    register(calls, provider, 'audit_essay', calls.audit_inputs(graph(), draft),
             {'labels': [label(1), label(2, role, nodes)]})
    with pytest.raises(EssayAuditFailed) as error:
        calls.audit_essay(graph(), draft)
    assert error.value.result['extra_steps'] == [2]
    assert error.value.result['flags'] == [dict(sentence=2, role=role, reason=reason)]
    assert not list(calls.cache.path.glob('*.json'))


@pytest.mark.parametrize('variant', ['correct', 'missing', 'unknown', 'miscited', 'bibliography'])
def test_source_claim_requires_correct_frozen_citation(rig, variant):
    from test_sectioned_writer import seed_sources
    calls, provider, log = rig
    route = seed_sources(calls, log)
    calls.config.update(essay_min_words=4500, token_cap=10_000_000)
    marker = '' if variant == 'missing' else '[cite:x]' if variant == 'unknown' else '[cite:p]'
    draft = dict(title='P', body='[[node:n0]] [[node:n1]] Q. [cite:q] P. '+marker,
                 bibliography=[dict(id=tid, text='Q' if tid == 'p' and variant == 'bibliography'
                                    else 'p:pdf:1#'+tid, url=None) for tid in ('p', 'q')])
    register(calls, provider, 'audit_essay', calls.audit_inputs(route, draft), {'labels': [
        label(1, nodes=('n1',)), label(2, 'source_claim', ('n0',), variant != 'miscited')]})
    if variant == 'correct':
        assert calls.audit_essay(route, draft)['faithful']
    else:
        with pytest.raises(EssayAuditFailed) as error:
            calls.audit_essay(route, draft)
        assert error.value.result['flags'] == [dict(sentence=2, role='source_claim', reason='miscited_source_claim')]


def test_presentation_mapping_does_not_fake_route_coverage(rig):
    calls, provider, _ = rig
    draft = dict(title='P', body='[[node:n1]] P.', bibliography=[])
    register(calls, provider, 'audit_essay', calls.audit_inputs(graph(), draft),
             {'labels': [label(1, 'signpost')]})
    with pytest.raises(EssayAuditFailed) as error:
        calls.audit_essay(graph(), draft)
    assert error.value.result['missing_node_ids'] == ['n1']
