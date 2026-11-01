"""Occurrence-bound inline edits and a separate persistent pass budget."""
import pytest

from ara.runtime.calls import Rejected
from ara.runtime.cache import canonical, digest
from test_publication_resume import row, start, request, accepted
from test_calls import rig


def test_inline_resume_keeps_exhausted_whole_paper_budget():
    from ara.runtime.publication_resume import repair_state
    events = [start()]
    for n in (1, 2, 3):
        events.extend([request(n), accepted(n)])
    state = repair_state(events, 'r', 'a', inline=True)
    assert state['repair_rounds'] == 3 and state['inline_passes'] == 0
    for n in (1, 2, 3):
        events.append(row('publication_inline_started', dict(pass_number=n,
            candidate_sha256=digest(canonical(state['candidate'])))))
    state = repair_state(events, 'r', 'a', inline=True)
    assert state['inline_passes'] == 3 and state['repair_rounds'] == 3
    events.append(row('publication_inline_started', dict(pass_number=4,
        candidate_sha256=digest(canonical(state['candidate'])))))
    with pytest.raises(Rejected, match='inline pass'):
        repair_state(events, 'r', 'a', inline=True)


def test_unfinished_inline_pass_survives_resume_without_reset():
    from ara.runtime.publication_resume import repair_state
    candidate = dict(markdown='# P\n\nP.', figure_placements=[], change_log=[])
    events = [start(), row('publication_candidate', candidate),
        row('publication_inline_started', dict(pass_number=1, candidate_sha256=digest(canonical(candidate)))),
        start(resumed_repair_rounds=0, resumed_inline_passes=1)]
    state = repair_state(events, 'r', 'a', inline=True)
    assert state['inline_passes'] == 1 and state['candidate'] == candidate
    with pytest.raises(Rejected, match='inline resume counter'):
        repair_state(events + [start(resumed_inline_passes=0)], 'r', 'a', inline=True)


def test_inline_acceptance_requires_matching_started_pass():
    from ara.runtime.publication_resume import repair_state
    candidate = dict(markdown='# P\n\nP.', figure_placements=[], change_log=[])
    events = [start(), row('publication_candidate', candidate)]
    with pytest.raises(Rejected, match='bounded request'):
        repair_state(events + [row('publication_inline_repair', dict(pass_number=1, **candidate))], 'r', 'a', inline=True)
    with pytest.raises(Rejected, match='candidate mismatch'):
        repair_state(events + [row('publication_inline_started', dict(pass_number=1,candidate_sha256='other'))], 'r', 'a', inline=True)


def test_exact_occurrence_patch_preserves_unflagged_bytes_and_markers():
    from ara.runtime.publication_inline import replace_sentence
    md = '# P\n\nP.  P.\n\nQ.'
    sentence = dict(sentence=2, field='body', start=4, end=6, text='P.')
    assert replace_sentence(md, sentence, 'R.') == '# P\n\nP.  R.\n\nQ.'
    assert replace_sentence(md, sentence, '') == '# P\n\nP.  \n\nQ.'
    with pytest.raises(Rejected, match='offsets'):
        replace_sentence(md, dict(sentence, start=5), 'R.')
    with pytest.raises(Rejected, match='single sentence'):
        replace_sentence(md, sentence, 'R. S.')
    cited = '# P\n\n[[node:n]] P [cite:p].'
    span = dict(sentence=1, field='body', start=0, end=len(cited.split('\n\n')[1]), text='P [cite:p].')
    with pytest.raises(Rejected, match='marker'):
        replace_sentence(cited, span, 'R.')
    assert replace_sentence(cited, span, '[[node:n]] R [cite:p].').endswith('[[node:n]] R [cite:p].')


def test_inline_reversion_uses_only_bound_accepted_carryover():
    from ara.runtime.publication_inline import source_reversions
    md = '# P\n\n[[node:n]] P [cite:p].'
    sentence = dict(sentence=1,field='body',start=0,end=len(md.split('\n\n')[1]),text='P [cite:p].')
    pair = dict(sentence=1, text=sentence['text'], source_text='We argue that P [cite:p].',
                raw_source_text='We argue that P [cite:p].', method='prefix_only')
    inputs = dict(sentences=[sentence],verified_sentence_carryover=dict(sentences=[pair]))
    assert source_reversions(md, inputs) == {1:'[[node:n]] We argue that P [cite:p].'}
    pair['method']='meaning_check'
    assert source_reversions(md,inputs) == {}
    pair.update(method='meaning_preserved',votes=[dict(verdict='equivalent')]*2+[dict(verdict='uncertain')])
    assert source_reversions(md,inputs) == {}
    pair['votes']=[dict(verdict='equivalent')]*3
    assert 1 in source_reversions(md,inputs)
    pair['text']='Q [cite:p].'
    assert source_reversions(md,inputs) == {}


def test_inline_native_path_has_separate_cap_and_fresh_audits(rig, monkeypatch):
    import json
    from ara.runtime.providers import Response
    from test_calls import response
    from test_publication import install_publication, paper
    from ara.runtime.publication import polish
    calls, route, seen = install_publication(rig, monkeypatch, adverse=4)
    calls.config['publication_inline_repairs'] = True
    original = calls.provider.complete
    edits = []
    def complete(kind, prompt, schema, maximum):
        if kind == 'repair_publication_sentence':
            data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
            edits.append(data)
            return Response(response(dict(replacement=data['sentence_text'].replace('P', 'Q', 1))))
        return original(kind, prompt, schema, maximum)
    monkeypatch.setattr(calls.provider, 'complete', complete)
    result, _ = polish(calls, route, paper())
    assert result['inline_passes'] == 3
    assert result['repair_rounds'] == 0
    assert not result['polished']
    assert 'inline pass budget exhausted' in result['polish_failure']
    assert edits and len([1 for k, _ in seen if k == 'audit_publication']) == 12
    assert not [d for k, d in seen if k == 'polish_essay' and d['mode'] == 'repair']


@pytest.mark.parametrize('miscitation', [False, True])
def test_inline_acceptance_and_miscitation_routing(rig, monkeypatch, miscitation):
    import json
    from ara.runtime.providers import Response
    from test_calls import response
    from test_publication import install_publication, paper
    from ara.runtime.publication import polish
    calls, route, seen = install_publication(rig, monkeypatch, adverse=1)
    calls.config['publication_inline_repairs'] = True
    original = calls.provider.complete
    def complete(kind, prompt, schema, maximum):
        if kind == 'repair_publication_sentence':
            data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
            return Response(response(dict(replacement=data['sentence_text'].replace('P', 'Q', 1))))
        value = original(kind,prompt,schema,maximum)
        if miscitation and kind == 'audit_publication':
            labels = json.loads(value.text())
            for label in labels['labels']:
                if label['role'] == 'unsupported_claim':
                    label.update(role='source_claim',citation_supported=False)
            return Response(response(labels))
        return value
    monkeypatch.setattr(calls.provider,'complete',complete)
    monkeypatch.setattr(calls,'verify_originality_citations',lambda draft:(draft,dict(items=[dict(status='verified')])))
    result,_ = polish(calls,route,paper())
    assert result['polished'] and result['native_citations']['status'] == 'pass'
    assert result['inline_passes'] == (0 if miscitation else 1)
    assert result['repair_rounds'] == (1 if miscitation else 0)
    assert len([1 for k,_ in seen if k == 'audit_publication']) == 9
    from ara.runtime.publication_resume import repair_state
    state=repair_state(calls.log.read(),route.id,result['original_sha256'],inline=True)
    assert state['inline_passes'] == result['inline_passes']
    assert state['candidate']['markdown'].startswith('# '+result['draft']['title'])


def test_inline_length_retry_keeps_pass_and_reports_exact_failure(rig, monkeypatch):
    import json
    from ara.runtime.providers import Response
    from test_calls import response
    from test_publication_quality5 import editor
    from test_publication import paper
    from ara.runtime.publication import polish
    calls,route,_,_=editor(rig,monkeypatch)
    calls.config['publication_inline_repairs']=True
    original=calls.provider.complete
    requests=[]
    def complete(kind,prompt,schema,maximum):
        if kind=='repair_publication_sentence':
            data=json.loads(prompt.split('\nINPUT_JSON\n')[1]);requests.append(data)
            text=data['sentence_text']
            text=text.replace('P '*900,'P '*2,1) if len(requests)==1 else text.replace('P','Q',1)
            return Response(response(dict(replacement=text)))
        return original(kind,prompt,schema,maximum)
    monkeypatch.setattr(calls.provider,'complete',complete)
    result,_=polish(calls,route,paper())
    assert result['polished'] and result['inline_passes']==1 and result['repair_rounds']==0
    assert [r['inline_pass'] for r in requests]==[1,1]
    feedback=json.loads(requests[1]['validation_feedback']['error'])
    assert feedback['minimum_words']==4500 and feedback['words']<4500<=feedback['previous_words']
    assert feedback['shrunken_sections']==[dict(section='1. Introduction',before=909,after=11,delta=-898)]
    assert requests[0]['sentence']==requests[1]['sentence']
