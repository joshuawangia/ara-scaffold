"""The operator four-rule contract, without sentence-level ownership rituals."""
import pytest
from ara.runtime.calls import EssayAuditFailed, Rejected
from test_calls import rig,register
from test_proposal_mode import setup,DISCLOSURE
from test_typed_audit import label


def paper():
    return dict(title='P — '+DISCLOSURE,body='Abstract\n\nDisclosure: '+DISCLOSURE+'.\n\nIntroduction\n\nQ.\n\nProposal\n\n[[node:n0]] [[node:n1]] P.\n\nObjections and replies\n\nR.\n\nConclusion\n\nS.',bibliography=[])


def test_natural_reasoning_needs_no_sentence_or_paragraph_marker(rig):
    calls,provider,log=rig;route,_=setup(calls,log);d=paper()
    inputs=calls.audit_inputs(route,d)
    labels=[label(s['sentence'],'proposed_principle' if s['text']=='P.' else 'argument_for_proposal' if s['text'] in ('Q.','R.','S.') else 'framing',('n0','n1') if s['text']=='P.' else ()) for s in inputs['sentences']]
    register(calls,provider,'audit_essay',inputs,dict(labels=labels))
    assert calls.audit_essay(route,d)['faithful']


def test_cited_faithful_source_discussion_allowed_in_proposal(rig):
    from ara.runtime.writing import source_context
    calls,provider,log=rig;route,_=setup(calls,log);d=paper();d['body']=d['body'].replace('P.\n\nObjections','P. According to a, Q. [cite:q]\n\nObjections');d['bibliography']=source_context(calls,route)['allowed_bibliography']
    inputs=calls.audit_inputs(route,d)
    labels=[label(s['sentence'],'proposed_principle' if s['text']=='P.' else 'source_claim' if '[cite:' in s['text'] else 'framing',('n0','n1') if s['text']=='P.' else ()) for s in inputs['sentences']]
    register(calls,provider,'audit_essay',inputs,dict(labels=labels))
    assert calls.audit_essay(route,d)['faithful']


@pytest.mark.parametrize('text,role,expected',[('According to a, P. [cite:p]','proposed_principle','source_attributed_proposal'),('Q.','unsupported_claim','unsupported_claim')])
def test_attributed_bridge_and_unsupported_established_claim_fail(rig,text,role,expected):
    calls,provider,log=rig;route,_=setup(calls,log);d=paper();
    from ara.runtime.writing import source_context
    d['bibliography']=source_context(calls,route)['allowed_bibliography']
    d['body']=d['body'].replace('P.\n\nObjections',text+'\n\nObjections');inputs=calls.audit_inputs(route,d)
    rows=[s for s in inputs['sentences'] if s.get('proposal_scope')]
    target=next(s['sentence'] for s in rows if s['text']==text)
    labels=[label(s['sentence'],role if s['sentence']==target else 'framing',('n0','n1') if s['sentence']==target else ()) for s in inputs['sentences']]
    register(calls,provider,'audit_essay',inputs,dict(labels=labels))
    with pytest.raises(EssayAuditFailed) as failure:calls.audit_essay(route,d)
    assert any(f['reason']==expected for f in failure.value.result['flags'])


def test_status_note_optional_and_title_label_required():
    from ara.runtime.proposal import validate_disclosure,insert_disclosure
    proposal=dict(disclosure=DISCLOSURE);d=paper();validate_disclosure(proposal,d)
    assert insert_disclosure(proposal,d)==d
    with pytest.raises(Rejected):validate_disclosure(proposal,{**d,'title':'P'})
    d['body']+='\n\nStatus and method\n\n'+'Q '*300
    validate_disclosure(proposal,d)


def test_outside_proposal_unsupported_established_claim_fails(rig):
    calls,provider,log=rig;route,_=setup(calls,log);d=paper();inputs=calls.audit_inputs(route,d)
    labels=[label(s['sentence'],'proposed_principle' if s['text']=='P.' else 'unsupported_claim' if s['text']=='Q.' else 'framing',('n0','n1') if s['text']=='P.' else ()) for s in inputs['sentences']]
    register(calls,provider,'audit_essay',inputs,dict(labels=labels))
    with pytest.raises(EssayAuditFailed) as failure:calls.audit_essay(route,d)
    assert [f['reason'] for f in failure.value.result['flags']]==['unsupported_claim']


@pytest.mark.parametrize('cited',[True,False])
def test_source_claim_must_be_cited_and_faithful_even_inside_proposal(rig,cited):
    from ara.runtime.writing import source_context
    calls,provider,log=rig;route,_=setup(calls,log);d=paper();text='According to a, Q.'+(' [cite:q]' if cited else '')
    d['body']=d['body'].replace('P.\n\nObjections','P. '+text+'\n\nObjections');d['bibliography']=source_context(calls,route)['allowed_bibliography'];inputs=calls.audit_inputs(route,d)
    labels=[label(s['sentence'],'proposed_principle' if s['text']=='P.' else 'source_claim' if s['text']==text else 'framing',('n0','n1') if s['text']=='P.' else ()) for s in inputs['sentences']]
    for item,sentence in zip(labels,inputs['sentences']):
        if sentence['text']==text:item['citation_supported']=False
    register(calls,provider,'audit_essay',inputs,dict(labels=labels))
    with pytest.raises(EssayAuditFailed) as failure:calls.audit_essay(route,d)
    assert [f['reason'] for f in failure.value.result['flags']]==['miscited_source_claim']


def test_title_page_label_may_precede_abstract_without_lengthening_title():
    from ara.runtime.proposal import validate_disclosure,insert_disclosure
    d=paper();d['title']='P';d['body']='Proposal status: '+DISCLOSURE+'.\n\n'+d['body']
    validate_disclosure(dict(disclosure=DISCLOSURE),d)
    assert insert_disclosure(dict(disclosure=DISCLOSURE),d)==d


def test_prompt_policy_update_keeps_valid_adverse_labels(rig,monkeypatch):
    import json
    from ara.runtime.essay_audit import audit_consensus
    from ara.runtime.cache import canonical
    from ara.runtime.logging import now
    from ara.runtime.providers import Response
    from ara.types import RunEvent
    from test_calls import response
    calls,provider,log=rig;route,_=setup(calls,log);d=paper();inputs=calls.audit_inputs(route,d)
    def labels(adverse):
        return [label(s['sentence'],'proposed_principle' if s['text']=='P.' else ('unsupported_claim' if adverse else 'argument_for_proposal') if s['text']=='Q.' else 'framing',('n0','n1') if s['text']=='P.' else ()) for s in inputs['sentences']]
    prior=calls.render('audit_essay',inputs)[1].replace('ROLE: audit_essay','ROLE: audit_essay\nPrevious policy wording.',1)
    log.emit(RunEvent(now(),'audit_essay','MODEL',prompt=prior,response=canonical(response(dict(labels=labels(True))))))
    monkeypatch.setattr(provider,'complete',lambda *args:Response(response(dict(labels=labels(False)))))
    with pytest.raises(EssayAuditFailed) as failure:audit_consensus(calls,route,d)
    assert failure.value.result['historical_adverse']
    assert failure.value.result['flags'][0]['reason']=='unsupported_claim'


@pytest.mark.parametrize('publication',[False,True])
def test_moving_proposal_heading_preserves_substantive_adverse_history(rig,monkeypatch,publication):
    from ara.runtime.essay_audit import audit_consensus
    from ara.runtime.providers import Response
    from test_calls import response
    calls,provider,log=rig;route,_=setup(calls,log)
    old=paper();old['body']=old['body'].replace('Introduction\n\nQ.\n\nProposal\n\n[[node:n0]] [[node:n1]] P.', 'Introduction\n\n[[node:n0]] [[node:n1]] P.\n\nProposal\n\nQ.')
    new={**old,'body':old['body'].replace('\n\nProposal\n\nQ.','\n\nQ.').replace('Introduction\n\n','Introduction\n\nProposal\n\n')}
    context={'publication_context':{}} if publication else {}
    if publication:
        import re
        for value in (old,new):
            value['body']=re.sub(r'^(Abstract|Introduction|Proposal|Objections and replies|Conclusion)$',r'## \1',value['body'],flags=re.M)
    inputs=calls.audit_inputs(route,old,**context)
    def classify(data,adverse):
        result=[label(s['sentence'],'proposed_principle' if s['text']=='P.' else ('unsupported_claim' if adverse else 'argument_for_proposal') if s['text']=='Q.' else 'framing',('n0','n1') if s['text']=='P.' else ()) for s in data['sentences']]
        return [{**item,'publication_issue':'none'} for item in result] if publication else result
    register(calls,provider,'audit_publication' if publication else 'audit_essay',inputs,dict(labels=classify(inputs,True)))
    with pytest.raises(EssayAuditFailed):calls.audit_essay(route,old,**context)
    def complete(kind,prompt,schema,maximum):
        import json
        data=json.loads(prompt.split('INPUT_JSON\n')[1])
        return Response(response(dict(labels=classify(data,False))))
    monkeypatch.setattr(provider,'complete',complete)
    with pytest.raises(EssayAuditFailed) as failure:audit_consensus(calls,route,new,**context)
    assert [f['reason'] for f in failure.value.result['flags']]==['unsupported_claim']
    assert failure.value.result['historical_adverse']


def test_abstract_can_restate_bridge_when_proposal_section_declares_it(rig):
    calls,provider,log=rig;route,_=setup(calls,log);d=paper();d['body']=d['body'].replace('\n\nIntroduction',' P.\n\nIntroduction');inputs=calls.audit_inputs(route,d)
    labels=[label(s['sentence'],'proposed_principle' if s['text']=='P.' else 'framing',('n0','n1') if s['text']=='P.' else ()) for s in inputs['sentences']]
    register(calls,provider,'audit_essay',inputs,dict(labels=labels))
    assert calls.audit_essay(route,d)['faithful']
