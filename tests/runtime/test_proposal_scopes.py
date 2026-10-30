"""Scoped ownership permits prose, never source attribution or unmarked claims."""
import json
import pytest
from ara.runtime.calls import EssayAuditFailed, Rejected
from ara.runtime.providers import Response
from test_calls import rig, register, response
from test_proposal_mode import setup, DISCLOSURE
from test_typed_audit import label


def paper(content):
    return dict(title='P', body='Abstract\n\nDisclosure: '+DISCLOSURE+'.\n\n'+content+'\n\nStatus and method\n\nDisclosure: '+DISCLOSURE+'.', bibliography=[])


def labels_for(inputs, target='P.', other_role='argument_for_proposal'):
    return [label(s['sentence'], 'proposed_principle' if s['text']==target else
                  other_role if s['text']=='Q.' else 'framing',
                  ('n0','n1') if s['text']==target else ()) for s in inputs['sentences']]


@pytest.mark.parametrize('heading', ['Proposal', '## The bridge principle', '2. Proposal'])
def test_native_scoped_proposal_accepts_natural_prose_and_bounds_heading(rig, heading):
    calls,provider,log=rig; route,_=setup(calls,log)
    d=paper(heading+'\n\n[[node:n0]] [[node:n1]] P. Q.\n\nConclusion\n\nR.')
    inputs=calls.audit_inputs(route,d)
    assert all(s['proposal_scope']['kind']=='section' for s in inputs['sentences'] if s['text'] in ('P.','Q.'))
    assert not next(s for s in inputs['sentences'] if s['text']=='R.').get('proposal_scope')
    register(calls,provider,'audit_essay',inputs,dict(labels=labels_for(inputs)))
    assert calls.audit_essay(route,d)['faithful']


@pytest.mark.parametrize('marker', ['Proposal:', '**Proposal:**'])
def test_marked_paragraph_ends_at_blank_line(rig, marker):
    calls,provider,log=rig;route,_=setup(calls,log)
    d=paper('Introduction\n\n'+marker+' [[node:n0]] [[node:n1]] P. Q.\n\nR.')
    inputs=calls.audit_inputs(route,d)
    assert next(s for s in inputs['sentences'] if s['text']=='Q.')['proposal_scope']['kind']=='paragraph'
    assert not next(s for s in inputs['sentences'] if s['text']=='R.').get('proposal_scope')
    target=next(s['text'] for s in inputs['sentences'] if marker in s['text'])
    register(calls,provider,'audit_essay',inputs,dict(labels=labels_for(inputs,target)))
    assert calls.audit_essay(route,d)['faithful']


@pytest.mark.parametrize('role', ['proposed_principle','argument_for_proposal','source_claim','framing'])
def test_in_scope_attribution_fails_regardless_of_role(rig, role):
    calls,provider,log=rig;route,_=setup(calls,log)
    d=paper('Proposal\n\n[[node:n0]] [[node:n1]] P. According to a, Q.')
    inputs=calls.audit_inputs(route,d);labels=labels_for(inputs)
    for item,s in zip(labels,inputs['sentences']):
        if s['text']=='According to a, Q.':item['role']=role
    register(calls,provider,'audit_essay',inputs,dict(labels=labels))
    with pytest.raises(EssayAuditFailed) as failure:calls.audit_essay(route,d)
    assert any(f['reason']=='source_attributed_proposal' for f in failure.value.result['flags'])


def test_outside_scope_unmarked_claim_fails(rig):
    calls,provider,log=rig;route,_=setup(calls,log)
    d=paper('Proposal\n\n[[node:n0]] [[node:n1]] P.\n\nConclusion\n\nQ.')
    inputs=calls.audit_inputs(route,d)
    register(calls,provider,'audit_essay',inputs,dict(labels=labels_for(inputs)))
    with pytest.raises(EssayAuditFailed) as failure:calls.audit_essay(route,d)
    assert failure.value.result['flags'][0]['reason']=='unmarked_proposal'


def test_outside_scope_uncited_source_claim_fails(rig):
    calls,provider,log=rig;route,_=setup(calls,log)
    d=paper('Proposal\n\n[[node:n0]] [[node:n1]] P.\n\nIntroduction\n\nQ.')
    inputs=calls.audit_inputs(route,d)
    labels=labels_for(inputs,other_role='source_claim')
    register(calls,provider,'audit_essay',inputs,dict(labels=labels))
    with pytest.raises(EssayAuditFailed) as failure:calls.audit_essay(route,d)
    assert failure.value.result['flags'][0]['reason']=='miscited_source_claim'


def test_scopes_do_not_authorize_other_modes():
    from ara.runtime.proposal import role_failure
    scope=dict(kind='section',heading='Proposal')
    assert role_failure('proposed_principle','P.',None,proposal_scope=scope)=='proposal_mode_required'
    h=dict(kind='hypothesis',stance='proposed',source_id=None,declaration=dict(text='P'),formula=dict(op='atom',name='P'))
    assert role_failure('proposed_principle','P.',None,frozen_hypothesis=h,proposal_scope=scope)


def test_disclosure_normalizes_legacy_once_and_keeps_import_compatibility():
    from ara.runtime.proposal import insert_disclosure,validate_disclosure
    proposal=dict(disclosure=DISCLOSURE)
    old=dict(title='P — '+DISCLOSURE,body='Abstract\n\n'+DISCLOSURE+'. '+DISCLOSURE+'. P.\n\nMethodology\n\n'+DISCLOSURE+'. Q.',bibliography=[])
    validate_disclosure(proposal,old,allow_legacy=True)
    new=insert_disclosure(proposal,old)
    assert new['title']=='P'
    assert new['body'].count('Disclosure: '+DISCLOSURE+'.')==2
    assert new['body'].endswith('Q.') and 'Status and method\n' in new['body']
    assert insert_disclosure(proposal,new)==new
    validate_disclosure(proposal,new)
    with pytest.raises(Rejected):validate_disclosure(proposal,old)


@pytest.mark.parametrize('bad', ['External AI findings are P.', 'The bounded, incomplete search is P.'])
def test_search_disclaimers_cannot_return_to_abstract(rig,bad):
    from ara.runtime.proposal import validate_disclosure
    d=paper('Proposal\n\nP.');d['body']=d['body'].replace('\n\nProposal',' '+bad+'\n\nProposal')
    with pytest.raises(Rejected,match='Status and method'):validate_disclosure(dict(disclosure=DISCLOSURE),d)


def test_status_note_has_one_disclosure():
    from ara.runtime.proposal import validate_disclosure
    d=paper('Proposal\n\nP.');d['body']+=' '+DISCLOSURE+'.'
    with pytest.raises(Rejected):validate_disclosure(dict(disclosure=DISCLOSURE),d)
