"""Publication repair feedback and conservative audits; placeholders only."""
import json

import pytest

from ara.runtime.calls import EssayAuditFailed
from ara.runtime.providers import Response
from test_calls import rig, response
from test_publication import install_publication, paper, polished


def editor(rig, monkeypatch, *, forever=False, invalid_forever=False):
    calls, route, _ = install_publication(rig, monkeypatch)
    calls.config.update(publication_min_words=4500, validation_attempts=1)
    original = calls.provider.complete
    seen, repairs = [], []
    counts = {}
    def complete(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1]); seen.append((kind, data))
        if kind == 'audit_publication':
            labels = []
            for s in data['sentences']:
                flag = s['section'] == 'Introduction' and (forever or s['text'].startswith('P '))
                labels.append(dict(sentence=s['sentence'], role='unsupported_claim' if flag else 'argument_step',
                                   node_ids=['n0','n1'], citation_supported=True, publication_issue='none'))
            return Response(response(dict(labels=labels)))
        if kind == 'polish_essay' and data['mode'] == 'repair':
            repairs.append(data); n=data['repair_round'];counts[n]=counts.get(n,0)+1
            md=data['markdown']
            if invalid_forever or counts[n]==1:
                md=md.replace('P '*900, 'P '*2, 1) if n==1 else md.replace('P '*899,'P '*2,1)
            else:
                md=md.replace('[[node:n0]] ', '[[node:n0]] '+('Q '*n), 1)
            return Response(response(dict(polished(paper()), markdown=md)))
        return original(kind,prompt,schema,maximum)
    monkeypatch.setattr(calls.provider,'complete',complete)
    return calls,route,seen,repairs


def test_invalid_repair_retries_same_round_with_exact_length_feedback(rig,monkeypatch):
    from ara.runtime.publication import polish
    calls,route,seen,repairs=editor(rig,monkeypatch)
    result,_=polish(calls,route,paper())
    assert result['polished'] and result['repair_rounds']==result['accepted_repair_rounds']==1
    assert [r['repair_round'] for r in repairs]==[1,1]
    feedback=json.loads(repairs[1]['validation_feedback']['error'])
    assert 'word count' in feedback['validator_failure']
    assert feedback['minimum_words']==4500 and feedback['maximum_words']==6000
    assert feedback['words'] < 4500 <= feedback['previous_words']
    assert feedback['previous_words']-feedback['words']==898
    assert feedback['shrunken_sections']==[dict(section='1. Introduction',before=909,after=11,delta=-898)]
    assert repairs[0]['markdown']==repairs[1]['markdown']
    assert repairs[0]['flagged_sentences']==repairs[1]['flagged_sentences']
    assert sum(k=='audit_publication' for k,_ in seen)==6
    assert result['draft']['bibliography']==paper()['bibliography']
    assert '[cite:p]' in result['draft']['body'] and '[cite:q]' in result['draft']['body']


def test_invalid_repair_retry_is_bounded_and_never_audits_invalid_draft(rig,monkeypatch):
    from ara.runtime.publication import polish
    calls,route,seen,repairs=editor(rig,monkeypatch,invalid_forever=True)
    result,_=polish(calls,route,paper())
    assert not result['polished'] and result['draft']==paper()
    assert [r['repair_round'] for r in repairs]==[1,1]
    assert result['repair_rounds']==1 and result['accepted_repair_rounds']==0
    assert sum(k=='audit_publication' for k,_ in seen)==3


def test_retry_generations_do_not_reset_three_round_limit(rig,monkeypatch):
    from ara.runtime.publication import polish
    calls,route,seen,repairs=editor(rig,monkeypatch,forever=True)
    result,_=polish(calls,route,paper())
    assert not result['polished'] and result['draft']==paper()
    assert [r['repair_round'] for r in repairs]==[1,1,2,2,3,3]
    assert result['repair_rounds']==result['accepted_repair_rounds']==3
    assert sum(k=='audit_publication' for k,_ in seen)==12


def test_publication_gate_keeps_adverse_history_despite_clean_cache(rig,monkeypatch):
    from ara.runtime.essay_audit import audit_consensus
    from ara.runtime.publication import as_draft
    calls,route,_=install_publication(rig,monkeypatch)
    current=as_draft(polished(paper())['markdown'],paper()['bibliography'])
    context=dict(original_draft=paper(),literature_currency=None)
    clean=calls.provider.complete;seen=[]
    def complete(kind,prompt,schema,maximum):
        value=clean(kind,prompt,schema,maximum)
        if kind=='audit_publication':
            seen.append(prompt)
            if len(seen)==1:
                out=json.loads(value.text());out['labels'][-1]['publication_issue']='unsupported_elaboration'
                return Response(response(out))
        return value
    monkeypatch.setattr(calls.provider,'complete',complete)
    with pytest.raises(EssayAuditFailed): calls.audit_essay(route,current,publication_context=context)
    calls.audit_essay(route,current,publication_context=context)
    with pytest.raises(EssayAuditFailed) as failure:
        audit_consensus(calls,route,current,publication_context=context)
    assert len(seen)==5
    assert failure.value.result['k']==3
    assert any(f['reason']=='unsupported_elaboration' for f in failure.value.result['flags'])
    assert len(failure.value.result['historical_adverse'])==1
    events=[json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='audit_publication']
    assert all(not e['cache_hit'] for e in events[-3:])


def test_publication_second_sample_dissent_reaches_repair(rig,monkeypatch):
    from ara.runtime.publication import polish
    calls,route,_=install_publication(rig,monkeypatch)
    original=calls.provider.complete;audits=0;repairs=[]
    def complete(kind,prompt,schema,maximum):
        nonlocal audits
        data=json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind=='polish_essay' and data['mode']=='repair':
            repairs.append(data)
            return Response(response(dict(polished(paper()),markdown=data['markdown'])))
        value=original(kind,prompt,schema,maximum)
        if kind=='audit_publication':
            audits+=1
            if audits==2:
                out=json.loads(value.text());out['labels'][-1]['publication_issue']='unsupported_elaboration'
                return Response(response(out))
        return value
    monkeypatch.setattr(calls.provider,'complete',complete)
    result,_=polish(calls,route,paper())
    assert not result['polished']  # An unchanged "repair" cannot erase the prior dissent.
    assert len(repairs)==3 and audits==12
    assert repairs[0]['flagged_sentences'][0]['field']=='title'


def test_repair_cannot_rewrite_unflagged_sentence_in_flagged_paragraph(rig,monkeypatch):
    from ara.runtime.publication import polish
    calls,route,_=install_publication(rig,monkeypatch)
    original=calls.provider.complete
    def complete(kind,prompt,schema,maximum):
        data=json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind=='polish_essay' and data['mode']=='whole':
            value=polished(paper());value['markdown']=value['markdown'].replace('[[node:n0]] ', '[[node:n0]] R. S. ',1)
            return Response(response(value))
        if kind=='polish_essay' and data['mode']=='repair':
            return Response(response(dict(polished(paper()),markdown=data['markdown'].replace('R. S.', 'Q. Q.',1))))
        if kind=='audit_publication':
            return Response(response(dict(labels=[dict(sentence=s['sentence'],role='unsupported_claim' if s['text']=='R.' else 'argument_step',node_ids=['n0','n1'],citation_supported=True,publication_issue='none') for s in data['sentences']])))
        return original(kind,prompt,schema,maximum)
    monkeypatch.setattr(calls.provider,'complete',complete)
    result,_=polish(calls,route,paper())
    assert not result['polished'] and result['accepted_repair_rounds']==0
    assert 'unflagged sentence' in result['polish_failure']


def test_post_verification_gate_also_requires_fresh_unanimous_samples(rig,monkeypatch):
    from ara.runtime.publication import polish
    calls,route,_=install_publication(rig,monkeypatch)
    monkeypatch.setattr(calls,'verify_originality_citations',lambda draft:(draft,dict(items=[dict(status='verified')])))
    original=calls.provider.complete;audits=0
    def complete(kind,prompt,schema,maximum):
        nonlocal audits
        value=original(kind,prompt,schema,maximum)
        if kind=='audit_publication':
            audits+=1
            if audits==5:
                out=json.loads(value.text());out['labels'][-1]['publication_issue']='unsupported_elaboration'
                return Response(response(out))
        return value
    monkeypatch.setattr(calls.provider,'complete',complete)
    with pytest.raises(EssayAuditFailed):polish(calls,route,paper())
    assert audits==6
    assert not (calls.log.path.parent/'publication/latest.json').exists()
