"""Only the bridge principle needs section-level ownership."""
import pytest
from ara.runtime.calls import EssayAuditFailed
from test_calls import rig,register
from test_proposal_mode import setup
from test_proposal_policy import paper
from test_typed_audit import label


@pytest.mark.parametrize('heading',['Proposal','## Proposal','2. Proposal'])
def test_proposal_section_bounds_bridge_ownership(rig,heading):
    calls,provider,log=rig;route,_=setup(calls,log);d=paper();d['body']=d['body'].replace('\nProposal\n','\n'+heading+'\n');inputs=calls.audit_inputs(route,d)
    assert next(s for s in inputs['sentences'] if s['text']=='P.')['proposal_scope']['kind']=='section'
    assert not next(s for s in inputs['sentences'] if s['text']=='R.').get('proposal_scope')
    labels=[label(s['sentence'],'proposed_principle' if s['text']=='P.' else 'framing',('n0','n1') if s['text']=='P.' else ()) for s in inputs['sentences']]
    register(calls,provider,'audit_essay',inputs,dict(labels=labels));assert calls.audit_essay(route,d)['faithful']


def test_bridge_principle_outside_proposal_section_fails(rig):
    calls,provider,log=rig;route,_=setup(calls,log);d=paper();d['body']=d['body'].replace('[[node:n0]] [[node:n1]] P.','R.').replace('Introduction\n\nQ.','Introduction\n\n[[node:n0]] [[node:n1]] P.');inputs=calls.audit_inputs(route,d)
    labels=[label(s['sentence'],'proposed_principle' if s['text']=='P.' else 'framing',('n0','n1') if s['text']=='P.' else ()) for s in inputs['sentences']]
    register(calls,provider,'audit_essay',inputs,dict(labels=labels))
    with pytest.raises(EssayAuditFailed) as failure:calls.audit_essay(route,d)
    assert failure.value.result['flags'][0]['reason']=='proposal_section_required'


def test_open_scope_does_not_authorize_frozen_hypotheses():
    from ara.runtime.proposal import role_failure
    scope=dict(kind='section',heading='Proposal')
    assert role_failure('proposed_principle','P.',None,proposal_scope=scope)=='proposal_mode_required'
    h=dict(kind='hypothesis',stance='proposed',source_id=None,declaration=dict(text='P'),formula=dict(op='atom',name='P'))
    assert role_failure('proposed_principle','P.',None,frozen_hypothesis=h,proposal_scope=scope)
