"""Bounded audit repair through the logged boundary, using placeholders only."""
import json

import pytest

from ara.runtime.calls import Rejected
from ara.runtime.providers import Response
from test_calls import graph, response, rig


def draft():
    return {'title': 'P', 'body': '[[node:n1]] P. [cite:t1]\n\nQ. [cite:t1]\nS.',
            'bibliography': [{'id': 't1', 'text': 'P:1', 'url': None}]}


def replies(provider, monkeypatch, *, always_adverse=False, replacement='R. [cite:t1]', number=2):
    seen = []
    def complete(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        seen.append((kind, data))
        if kind == 'audit_essay':
            result = {'labels': [dict(sentence=s['sentence'], node_ids=['n1'],
                role='unsupported_claim' if (s['sentence'] == 2 and
                    (always_adverse or s['text'].startswith('Q.'))) else 'argument_step', citation_supported=True) for s in data['sentences']]}
        elif kind == 'revise_essay':
            result = {'revisions': [{'sentence': number, 'text': replacement}]}
        else:
            raise AssertionError('unexpected call: ' + kind)
        return Response(response(result))
    monkeypatch.setattr(provider, 'complete', complete)
    return seen


def test_audit_revision_preserves_unflagged_text_and_evidence(rig, monkeypatch):
    from ara.runtime.essay_audit import audit_and_revise
    calls, provider, log = rig
    before = draft()
    expected_inputs = calls.audit_inputs(graph(), before)
    seen = replies(provider, monkeypatch)
    result = audit_and_revise(calls, graph(), before)
    assert result == {**before, 'body': before['body'].replace('Q. [cite:t1]', 'R. [cite:t1]')}
    assert before == draft()
    assert [kind for kind, _ in seen] == ['audit_essay', 'revise_essay', 'audit_essay']
    repair = seen[1][1]
    assert repair['audit_inputs'] == expected_inputs
    assert repair['flags'] == [{'sentence': 2, 'node_ids': ['n1'],
                              'role': 'unsupported_claim', 'citation_supported': True}]
    assert repair['flagged_sentences'] == [{'sentence': 2, 'text': 'Q. [cite:t1]', 'citation_markers': ['[cite:t1]'], 'node_markers': []}]
    assert repair['bibliography'] == before['bibliography']
    assert len([e for e in log.read() if e['stage'] == 'essay_audit_revision']) == 1
    assert json.loads((log.path.parent / 'draft.unverified.json').read_text()) == result


def test_audit_revision_stops_after_three_rounds(rig, monkeypatch):
    from ara.runtime.essay_audit import audit_and_revise
    calls, provider, log = rig
    seen = replies(provider, monkeypatch, always_adverse=True)
    with pytest.raises(Rejected, match='essay audit failed'):
        audit_and_revise(calls, graph(), draft())
    assert [k for k, _ in seen].count('revise_essay') == 3
    assert [k for k, _ in seen].count('audit_essay') == 4
    assert not (log.path.parent / 'draft.json').exists()
    stop = json.loads(next(e['payload_json'] for e in log.read() if e['stage'] == 'essay_audit_revision_exhausted'))
    assert stop['extra_steps'] == [2] and stop['rounds'] == 3


def test_revision_feedback_names_forbidden_marker_and_recovers(rig, monkeypatch):
    from ara.runtime.essay_audit import audit_and_revise
    calls, provider, _ = rig
    calls.config['validation_attempts'] = 2
    seen = replies(provider, monkeypatch)
    original = provider.complete
    repairs = []
    def complete(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'revise_essay':
            repairs.append(data)
            if len(repairs) == 1:
                return Response(response({'revisions': [{'sentence': 2, 'text': 'R. [cite:t2]'}]}))
            assert '[cite:t2]' in data['validation_feedback']['error']
            assert '[cite:t1]' in data['validation_feedback']['error']
        return original(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'complete', complete)
    result = audit_and_revise(calls, graph(), draft())
    assert 'Q.' not in result['body'] and '[cite:t2]' not in result['body']
    assert repairs[0]['flagged_sentences'][0]['citation_markers'] == ['[cite:t1]']
    assert len(repairs) == 2


@pytest.mark.parametrize('number,replacement,reason', [
    (1, 'R. [cite:t1]', 'flagged sentence'),
    (2, 'R. [cite:t2]', 'citations'),
    (2, 'R.', 'citations'),
    (2, '[[node:n1]] R. [cite:t1]', 'node markers'),
    (2, 'P ' * 1000 + '[cite:t1]', 'size'),
], ids=['unflagged', 'invented_citation', 'dropped_citation', 'added_node', 'oversize'])
def test_revision_rejects_changes_outside_authorized_span(rig, monkeypatch, number, replacement, reason):
    from ara.runtime.essay_audit import audit_and_revise
    calls, provider, log = rig
    replies(provider, monkeypatch, number=number, replacement=replacement)
    with pytest.raises(Rejected, match=reason):
        audit_and_revise(calls, graph(), draft())
    assert not any(e['stage'] == 'essay_audit_revision' for e in log.read())


def test_revision_can_cut_unsupported_sentence(rig, monkeypatch):
    from ara.runtime.essay_audit import audit_and_revise
    calls, provider, _ = rig
    replies(provider, monkeypatch, replacement='')
    before = draft()
    result = audit_and_revise(calls, graph(), before)
    assert result['body'] == '[[node:n1]] P. [cite:t1]\n\n\nS.'
    assert result['bibliography'] == before['bibliography']


def test_revision_rechecks_minimum_words(rig, monkeypatch):
    from ara.runtime.essay_audit import audit_and_revise
    calls, provider, log = rig
    from ara.runtime.calls import word_count
    calls.config['essay_min_words'] = word_count(draft())
    replies(provider, monkeypatch, replacement='')
    with pytest.raises(Rejected, match='minimum words'):
        audit_and_revise(calls, graph(), draft())
    assert not any(e['stage'] == 'essay_audit_revision' for e in log.read())


def test_native_compose_resumes_and_preserves_later_verification(rig, monkeypatch):
    from ara.runtime.orchestration import compose
    calls, provider, log = rig
    seen = replies(provider, monkeypatch)
    complete = provider.complete
    later = []
    def verify(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'search_evidence':
            later.append(kind)
            return Response(response('P'))
        if kind == 'verify_originality_citations':
            later.append(kind)
            return Response(response({'items': [{**item, 'status': 'unverified', 'action': 'remove',
                'detail': 'P', 'evidence_urls': []} for item in data['items']],
                'originality': {'assessment': 'unverified', 'detail': 'P', 'evidence_urls': []}}))
        return complete(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'complete', verify)
    result = compose(calls, graph(), draft())
    assert later == ['search_evidence', 'verify_originality_citations']
    assert [k for k, _ in seen] == ['audit_essay', 'revise_essay', 'audit_essay', 'audit_essay']
    assert 'Q.' not in result['body'] and result['bibliography'] == []
    assert json.loads((log.path.parent / 'draft.json').read_text()) == result


def test_revision_receives_exact_frozen_source_context(rig, monkeypatch):
    from ara.runtime.essay_audit import audit_and_revise
    from test_sectioned_writer import seed_sources
    calls, provider, log = rig
    route = seed_sources(calls, log)
    calls.config['essay_min_words'] = 4500
    calls.config['token_cap'] = 10_000_000
    before = {'title': 'P', 'body': '[[node:n0]] [[node:n1]] ' + 'P ' * 4500 + '. [cite:p] [cite:q]\nQ. [cite:p]',
              'bibliography': [dict(id=tid, text='p:pdf:1#' + tid, url=None) for tid in ['p', 'q']]}
    seen = []
    def complete(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        seen.append((kind, data))
        if kind == 'revise_essay':
            result = {'revisions': [{'sentence': 2, 'text': 'R. [cite:p]'}]}
        else:
            result = {'labels': [dict(sentence=s['sentence'], node_ids=['n0', 'n1'],
                role='unsupported_claim' if s['text'].startswith('Q.') else 'argument_step', citation_supported=True) for s in data['sentences']]}
        return Response(response(result))
    monkeypatch.setattr(provider, 'complete', complete)
    result = audit_and_revise(calls, route, before)
    assert result['body'] == before['body'].replace('Q. [cite:p]', 'R. [cite:p]')
    assert seen[1][1]['audit_inputs'] == {k: v for k, v in seen[0][1].items() if k != 'topic'}
    evidence = seen[1][1]['audit_inputs']['source_evidence']
    assert len(evidence['supporting_commitments']) == 2
    assert evidence == seen[2][1]['source_evidence']


@pytest.mark.parametrize('incomplete', [False, True])
def test_audit_without_complete_flagged_inventory_does_not_revise(rig, monkeypatch, incomplete):
    from ara.runtime.essay_audit import audit_and_revise
    calls, provider, log = rig
    seen = []
    def complete(kind, prompt, schema, maximum):
        seen.append(kind)
        assert kind == 'audit_essay'
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        sentences = data['sentences'][:1] if incomplete else data['sentences']
        return Response(response({'labels': [dict(sentence=s['sentence'], node_ids=[],
            role='unsupported_claim' if incomplete else 'signpost', citation_supported=True) for s in sentences]}))
    monkeypatch.setattr(provider, 'complete', complete)
    with pytest.raises(Rejected, match='essay audit failed'):
        audit_and_revise(calls, graph(), draft())
    assert seen == ['audit_essay']
    assert not any(e['stage'] == 'essay_audit_revision' for e in log.read())
