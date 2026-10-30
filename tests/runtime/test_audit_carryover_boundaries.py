"""Ownership and provider boundaries for verified sentence carry-over."""
import json

import pytest

from ara.runtime.calls import EssayAuditFailed
from ara.runtime.providers import MockProvider
from test_calls import rig
from test_audit_carryover import setup_source, revised, run


def test_added_ownership_prefix_requires_meaning_votes(rig,monkeypatch):
    calls,route,source,_,seen=setup_source(rig,monkeypatch,first='P, Q, and R.',votes=('different',)*3)
    with pytest.raises(EssayAuditFailed) as exc:
        run(calls,route,source,revised(source,'We argue that P, Q and R.'))
    assert exc.value.result['extra_steps']==[1]
    assert [k for k,_ in seen].count('audit_meaning')==3


def test_meaning_dispatch_uses_selected_audit_provider(rig,monkeypatch):
    calls,route,source,_,seen=setup_source(rig,monkeypatch)
    selected=MockProvider({})
    monkeypatch.setattr(selected,'complete',calls.provider.complete)
    def forbidden(*args,**kwargs):raise AssertionError('meaning fell through to parent provider')
    monkeypatch.setattr(calls.provider,'complete',forbidden)
    calls.provider_factory=lambda settings:selected
    calls.config['stages']={'audit_publication':dict(provider='mock',model='claude-opus-5',effort='high')}
    assert run(calls,route,source,revised(source,'P together with Q and R.'))['faithful']
    assert [k for k,_ in seen].count('audit_meaning')==3


def test_source_gate_requires_three_samples(rig,monkeypatch):
    calls,route,source,_,_=setup_source(rig,monkeypatch)
    gate=json.loads([e['payload_json'] for e in calls.log.read() if e['stage']=='essay_audit_consensus'][-1])
    gate['k']=2;gate['samples']=gate['samples'][:2]
    calls.log.record('essay_audit_consensus',**gate)
    calls.log.record('final_draft',route_id=route.id,draft=source)
    with pytest.raises(EssayAuditFailed):run(calls,route,source,revised(source))


def test_clean_source_role_variation_keeps_verified_verdict(rig,monkeypatch):
    calls,route,source,_,_=setup_source(rig,monkeypatch,vary_source_roles=True)
    assert run(calls,route,source,revised(source))['faithful']


def test_changed_bibliography_cannot_claim_carried_verdict(rig,monkeypatch):
    calls,route,source,_,_=setup_source(rig,monkeypatch)
    draft=revised(source);draft['bibliography']=[{**b,'text':'R'} for b in source['bibliography']]
    inputs=calls.audit_inputs(route,draft,publication_context=dict(original_draft=source))
    assert inputs['verified_sentence_carryover']['sentences']==[]


def test_revised_verified_source_inherits_its_effective_clean_role(rig,monkeypatch):
    from ara.runtime.essay_audit import audit_consensus
    calls,route,source,_,_=setup_source(rig,monkeypatch)
    middle=revised(source)
    assert audit_consensus(calls,route,middle)['faithful']
    calls.log.record('final_draft',route_id=route.id,draft=middle)
    assert run(calls,route,middle,revised(middle))['faithful']


def test_legacy_clean_source_without_new_scope_metadata_can_inherit(rig,monkeypatch):
    from ara.runtime.cache import canonical,digest
    from ara.runtime.essay_audit import audit_consensus
    from ara.runtime.providers import Response
    from test_calls import response
    from test_proposal_mode import setup,draft
    calls,provider,log=rig
    route,_=setup(calls,log);source=draft()
    def complete(kind,prompt,schema,maximum):
        inputs=json.loads(prompt.split('\nINPUT_JSON\n')[1])
        return Response(response(dict(labels=[dict(sentence=s['sentence'],
            node_ids=['n0','n1'] if 'This paper proposes P.' in s['text'] else [],
            role='proposed_principle' if 'This paper proposes P.' in s['text'] else 'framing',
            citation_supported=True) for s in inputs['sentences']])))
    monkeypatch.setattr(provider,'complete',complete)
    gate=audit_consensus(calls,route,source)
    legacy=calls.audit_inputs(route,source)
    for sentence in legacy['sentences']:sentence.pop('proposal_scope',None)
    prompt_hash=digest(calls.render('audit_essay',legacy)[1])
    verdict={k:v for k,v in gate['samples'][0].items() if k!='sample'}
    # Replay the older accepted wire contract: same audited text/verdict, before scope metadata existed.
    def accepted_before_scopes(data):
        log.record('essay_audit',route_id=route.id,prompt_sha256=prompt_hash,**verdict)
        return verdict
    for _ in range(3):calls.call('audit_essay',legacy,accepted_before_scopes,fresh=True)
    log.record('essay_audit_consensus',**{**gate,'prompt_sha256':prompt_hash})
    log.record('final_draft',route_id=route.id,draft=source)
    current={**source,'body':source['body'].replace('This paper proposes P.','P.')}
    inputs=calls.audit_inputs(route,current,publication_context=dict(original_draft=source))
    assert any(row['label']['role']=='proposed_principle' and row['text']=='P.'
               for row in inputs['verified_sentence_carryover']['sentences'])
