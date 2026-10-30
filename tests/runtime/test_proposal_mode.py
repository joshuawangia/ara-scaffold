"""Paper-owned proposals remain separate from source claims and engine licenses."""
from dataclasses import replace
import json

import pytest

from ara.runtime.calls import EssayAuditFailed, Rejected
from ara.runtime.providers import Response
from test_calls import register, response, rig
from test_sectioned_writer import seed_sources
from test_typed_audit import label

DISCLOSURE = 'ARA-proposed thesis; bridge principle argued, not mechanically derived'


def setup(calls, log):
    from ara.runtime.proposal import activate
    r = seed_sources(calls, log, local_pages='P P P Q Q Q R R R')
    r = replace(r, status='OPEN', nodes=tuple(replace(n, t_id='open') for n in r.nodes))
    packet = dict(route_id=r.id, target_text=r.nodes[0].proposition.text,
                  thesis_origin='ara', dossier_mapping='P', missing_premise='Q',
                  frozen_evidence_ids=['p', 'q'], local_sources=[], minimum_words=3000)
    activate(calls, r, packet)
    return r, packet


def draft():
    return dict(title='P',
                body='Abstract\nDisclosure: '+DISCLOSURE+'.\n[[node:n0]] [[node:n1]] This paper proposes P.\nStatus and method\nDisclosure: '+DISCLOSURE+'.',
                bibliography=[])


def test_native_proposal_roles_cover_open_target_and_keep_frozen_sources(rig):
    from ara.runtime.writing import source_context
    calls, provider, log = rig
    r, packet = setup(calls, log)
    d = draft()
    inputs = calls.audit_inputs(r, d)
    assert inputs['proposal']['packet']['missing_premise'] == 'Q'
    evidence = source_context(calls, r)
    assert not evidence['supporting_commitments']
    assert {b['id'] for b in evidence['allowed_bibliography']} == {'p', 'q'}
    assert len(evidence['proposal_source_evidence']) == 2
    labels = [label(s['sentence'], 'proposed_principle' if 'This paper proposes' in s['text'] else 'framing',
                    ('n0', 'n1') if 'This paper proposes' in s['text'] else ()) for s in inputs['sentences']]
    register(calls, provider, 'audit_essay', inputs, dict(labels=labels))
    assert calls.audit_essay(r, d)['faithful']


@pytest.mark.parametrize('text,role', [
    ('P.', 'proposed_principle'),
    ('According to a, P.', 'proposed_principle'),
    ('This paper proposes that a establishes P. [cite:p]', 'proposed_principle'),
    ('This paper argues that according to a, P.', 'argument_for_proposal'),
    ('P.', 'unsupported_claim'),
])
def test_unmarked_or_source_attributed_proposal_still_fails(rig, text, role):
    calls, provider, log = rig
    r, _ = setup(calls, log)
    d = draft(); d['body'] = d['body'].replace('This paper proposes P.', text)
    inputs = calls.audit_inputs(r, d)
    labels = [label(s['sentence'], role if '[[node:' not in s['text'] and s['sentence']==3 else 'framing',
                    ('n0','n1') if s['sentence']==3 else ()) for s in inputs['sentences']]
    register(calls, provider, 'audit_essay', inputs, dict(labels=labels))
    with pytest.raises(EssayAuditFailed):
        calls.audit_essay(r, d)


def test_proposal_mode_cannot_erase_citations_or_disclosure_on_export(rig):
    from ara.runtime.citations import check_coverage
    calls, _, log = rig
    r, _ = setup(calls, log)
    with pytest.raises(ValueError, match='citation coverage'):
        check_coverage(log.read(), r, draft())
    with pytest.raises(Rejected, match='disclosure'):
        calls.validate_essay(r, {**draft(), 'body':draft()['body'].replace(DISCLOSURE, '', 1)}, minimum_words=0)


def test_proposal_packet_is_bound_to_route_and_immutable(rig):
    from ara.runtime.proposal import activate
    calls, _, log = rig
    r, packet = setup(calls, log)
    with pytest.raises(Rejected, match='immutable'):
        activate(calls, r, {**packet, 'missing_premise':'R'})
    with pytest.raises(Rejected, match='route'):
        activate(calls, replace(r, id='different'), packet)


def test_proposal_writer_uses_native_proportional_sections(rig, monkeypatch):
    calls, provider, log = rig
    r, _ = setup(calls, log)
    calls.config['token_cap'] = 10_000_000
    seen=[]
    def complete(kind,prompt,schema,maximum):
        inputs=json.loads(prompt.split('INPUT_JSON\n')[1]);seen.append((kind,inputs))
        if kind=='outline_essay':
            assert 3000 <= inputs['budget_min'] < inputs['budget_max'] <= 4500
            value=dict(title='P', sections=[dict(id=f's{i}',heading=h,purpose='P',word_budget=w,node_ids=['n0','n1'])
                for i,(h,w) in enumerate([('Abstract',200),('Introduction',800),('Proposal',1000),('Objections and replies',700),('Conclusion',400),('Status and method',100)])])
        else:
            assert inputs['mode']=='section'
            value=dict(title=inputs['section']['heading'],body='[[node:n0]] [[node:n1]] '+('P '*inputs['section']['word_budget']),bibliography=[])
        return Response(response(value))
    monkeypatch.setattr(provider,'complete',complete)
    result=calls.write_essay(r)
    assert result['title']=='P'
    assert [k for k,_ in seen]==['outline_essay']+['write_essay']*6


def test_source_attribution_without_citation_cannot_hide_in_proposal_role(rig):
    calls, provider, log = rig
    r, _ = setup(calls, log)
    d = draft(); d['body'] = d['body'].replace('This paper proposes P.', 'This paper proposes that a establishes P.')
    inputs = calls.audit_inputs(r, d)
    labels = [label(s['sentence'], 'proposed_principle' if s['sentence']==3 else 'framing',
                    ('n0','n1') if s['sentence']==3 else ()) for s in inputs['sentences']]
    register(calls, provider, 'audit_essay', inputs, dict(labels=labels))
    with pytest.raises(EssayAuditFailed) as failure:
        calls.audit_essay(r, d)
    assert failure.value.result['flags'][0]['reason'] == 'source_attributed_proposal'


def test_proposal_adverse_sample_remains_binding_in_fresh_union(rig, monkeypatch):
    from ara.runtime.essay_audit import audit_consensus
    calls, provider, log = rig
    r, _ = setup(calls, log)
    d = draft(); count=0
    def complete(kind,prompt,schema,maximum):
        nonlocal count
        count += 1
        inputs = json.loads(prompt.split('INPUT_JSON\n')[1])
        labels = [label(s['sentence'], ('unsupported_claim' if count==2 else 'proposed_principle') if s['sentence']==3 else 'framing',
                        ('n0','n1') if s['sentence']==3 else ()) for s in inputs['sentences']]
        return Response(response(dict(labels=labels)))
    monkeypatch.setattr(provider,'complete',complete)
    with pytest.raises(EssayAuditFailed) as failure:
        audit_consensus(calls, r, d)
    assert count==3 and failure.value.result['extra_steps']==[3]


def test_regular_route_cannot_use_proposal_role(rig):
    from test_calls import graph
    calls, provider, _ = rig
    d = dict(title='P',body='[[node:n1]] This paper proposes P.',bibliography=[])
    inputs=calls.audit_inputs(graph(),d)
    register(calls, provider,'audit_essay',inputs,dict(labels=[label(1,'proposed_principle')]))
    with pytest.raises(EssayAuditFailed) as failure:
        calls.audit_essay(graph(),d)
    assert failure.value.result['flags'][0]['reason']=='proposal_mode_required'


def test_local_proposal_pdf_citations_survive_web_absence_and_publication(rig, monkeypatch, tmp_path):
    from hashlib import sha256
    from pypdf import PdfWriter
    from pypdf.generic import NameObject, DictionaryObject, DecodedStreamObject
    from ara.runtime.proposal import activate
    from ara.runtime.citations import check_coverage
    from ara.runtime.writing import source_context
    from ara.runtime.publication_references import bibliography_records, reading_copy
    from test_local_citations import web_absent
    calls, provider, log = rig
    r=seed_sources(calls,log,local_pages='P P P Q Q Q R R R')
    r=replace(r,status='OPEN',nodes=tuple(replace(n,t_id='open') for n in r.nodes))
    writer=PdfWriter(); page=writer.add_blank_page(width=200,height=200)
    font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
    page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):font})})
    stream=DecodedStreamObject();stream.set_data(b'BT /F1 12 Tf 10 100 Td (P P P) Tj ET')
    page[NameObject('/Contents')]=writer._add_object(stream)
    pdf=tmp_path/'p.pdf';writer.write(pdf)
    source=dict(id='proposal:p',pdf_path=str(pdf),pdf_sha256=sha256(pdf.read_bytes()).hexdigest(),
                page_start=1,page_end=1,record=dict(id='s',authors='b',year=2000,title='Q',venue='R'),excerpt='P P P')
    packet=dict(route_id=r.id,target_text=r.nodes[0].proposition.text,thesis_origin='eps2',
                dossier_mapping='P',missing_premise='Q',frozen_evidence_ids=['p','q'],local_sources=[source],minimum_words=3000)
    before=pdf.read_bytes()
    activate(calls,r,packet)
    evidence=source_context(calls,r)
    d=draft();d['title']=d['title'].replace(DISCLOSURE,'eps2-proposed thesis (tested in ARA); bridge principle argued, not mechanically derived')
    d['body']=d['body'].replace(DISCLOSURE,'eps2-proposed thesis (tested in ARA); bridge principle argued, not mechanically derived')+'\nP P P. [cite:p] Q Q Q. [cite:q] P P P. [cite:proposal:p]'
    d['bibliography']=evidence['allowed_bibliography']
    assert check_coverage(log.read(),r,d)['required_ids']==['p','proposal:p','q']
    seen=web_absent(provider,monkeypatch)
    cleaned,verification=calls.verify_originality_citations(d)
    assert cleaned==d and all(not data['items'] for _,data in seen)
    local=next(i for i in verification['items'] if i['id']=='proposal:p')
    assert local['verification_basis']=='local_proposal_pdf'
    records=bibliography_records(log,evidence)
    reading,receipt=reading_copy(d['body'],evidence,records,None)
    assert '[cite:' not in reading and receipt['proposal:p']['basis']=='proposal literature physical PDF pages'
    assert pdf.read_bytes()==before
    other=replace(r,id='r2')
    packet.update(route_id='r2',local_sources=[{**source,'pdf_sha256':'0'*64}])
    with pytest.raises(Rejected,match='PDF hash'):
        activate(calls,other,packet)


def test_frozen_hypothesis_authorization_is_explicit_and_separate():
    from ara.runtime.proposal import role_failure
    h=dict(kind='hypothesis',stance='proposed',source_id=None,declaration=dict(text='P'),formula=dict(op='atom',name='P'))
    assert role_failure('proposed_principle','This paper proposes P.',None,frozen_hypothesis=h) is None
    assert role_failure('proposed_principle','This paper proposes P.',None)=='proposal_mode_required'
    assert role_failure('proposed_principle','This paper proposes P.',{},frozen_hypothesis=h)=='invalid_frozen_hypothesis_authorization'
    assert role_failure('argument_for_proposal','This paper argues P.',None,frozen_hypothesis=h)=='invalid_frozen_hypothesis_authorization'
    assert role_failure('proposed_principle','According to a, P.',None,frozen_hypothesis=h)=='unmarked_proposal'


def test_proposal_title_repair_uses_title_field_and_shared_round_budget(rig, monkeypatch):
    from ara.runtime.essay_audit import audit_and_revise
    calls, provider, log = rig
    r,_=setup(calls,log)
    d=draft(); d['body']=d['body'].replace('\nStatus and method', '\nIntroduction\n'+'P '*3000+'\nStatus and method')
    d['title']='Q'
    seen=[]
    def complete(kind,prompt,schema,maximum):
        inputs=json.loads(prompt.split('INPUT_JSON\n')[1]);seen.append(kind)
        if kind=='revise_essay':
            return Response(response(dict(revisions=[dict(sentence=inputs['flags'][0]['sentence'],text='P')])))
        labels=[label(s['sentence'], 'proposed_principle' if s['sentence']==3 else
                      'unsupported_claim' if s['text']==d['title'] else 'framing',
                      ('n0','n1') if s['sentence']==3 else ()) for s in inputs['sentences']]
        return Response(response(dict(labels=labels)))
    monkeypatch.setattr(provider,'complete',complete)
    fixed=audit_and_revise(calls,r,d)
    assert fixed['body']==d['body'] and fixed['title']=='P'
    assert seen==['audit_essay','revise_essay','audit_essay']
    assert [json.loads(e['payload_json'])['round'] for e in log.read() if e['stage']=='essay_audit_revision']==[1]


def test_plural_claims_in_owned_reasoning_is_not_author_attribution(rig):
    calls, provider, log = rig
    r,_=setup(calls,log)
    d=draft();d['body']+='\nThis paper argues that the cited claims require Q if P.'
    inputs=calls.audit_inputs(r,d)
    labels=[label(s['sentence'], 'proposed_principle' if s['sentence']==3 else
                  'argument_for_proposal' if s['text'].startswith('This paper argues') else 'framing',
                  ('n0','n1') if s['sentence']==3 else ()) for s in inputs['sentences']]
    register(calls,provider,'audit_essay',inputs,dict(labels=labels))
    assert calls.audit_essay(r,d)['faithful']


def test_resume_inserts_disclosure_and_restores_cleanup_without_spending_repair(rig, monkeypatch):
    from ara.runtime.orchestration import compose
    from ara.runtime.essay_audit import repair_rounds
    from ara.runtime.writing import source_context
    calls,provider,log=rig
    r,_=setup(calls,log)
    body='Abstract\n\nP.\n\nMethodology\n\nQ.\n\n[[node:n0]] [[node:n1]] This paper proposes P.\nP P P. [cite:p]\nQ Q Q. [cite:q]'
    original=dict(title='P',body=body,bibliography=source_context(calls,r)['allowed_bibliography'])
    log.record('route',graph=r.to_dict())
    log.record('essay_composition_started',route_id=r.id,repair_rounds=3)
    log.record('essay_audit_revision',round=3,draft=original)
    seen=[]
    def complete(kind,prompt,schema,maximum):
        assert kind=='audit_essay';seen.append(kind)
        inputs=json.loads(prompt.split('INPUT_JSON\n')[1])
        assert any('Disclosure: '+DISCLOSURE+'.' in s['text'] for s in inputs['sentences'])
        labels=[label(s['sentence'], 'proposed_principle' if 'This paper proposes P.' in s['text'] else
                      'source_claim' if '[cite:' in s['text'] else 'framing',
                      ('n0','n1') if 'This paper proposes P.' in s['text'] else ()) for s in inputs['sentences']]
        return Response(response(dict(labels=labels)))
    monkeypatch.setattr(provider,'complete',complete)
    def cleanup(value):
        return {**value,'body':value['body'].replace('Disclosure: '+DISCLOSURE+'. ',''),'title':'P'},dict(items=[],originality=dict(assessment='unverified',detail='P',evidence_urls=[]))
    monkeypatch.setattr(calls,'verify_originality_citations',cleanup)
    result=compose(calls,r,original)
    assert result['title']=='P'
    assert result['body'].count('Disclosure: '+DISCLOSURE+'.')==2
    assert 'This paper proposes P.' in result['body'] and 'Status and method' in result['body']
    assert seen==['audit_essay']*4 and repair_rounds(calls,r)==3
    assert (log.path.parent/'export/essay.txt').exists()
    corrections=[json.loads(e['payload_json']) for e in log.read() if e['stage']=='essay_proposal_disclosure_inserted']
    assert len(corrections)==2 and all(c['semantic_repair_rounds_unchanged'] for c in corrections)


def test_disclosure_metadata_is_idempotent_and_never_a_source_quotation():
    from ara.runtime.proposal import insert_disclosure, validate_disclosure
    from ara.runtime.calls import ModelCalls
    proposal=dict(disclosure=DISCLOSURE)
    old=dict(title='P — "'+DISCLOSURE+'"',body='## Abstract\n\n"'+DISCLOSURE+'". P.\n\n## 1. Methodology\n\nQ.',bibliography=[])
    result=insert_disclosure(proposal,old)
    assert insert_disclosure(proposal,result)==result
    assert result['body'].count('Disclosure: '+DISCLOSURE+'.')==2
    assert not ModelCalls.verification_items(result)
    validate_disclosure(proposal,result)


@pytest.mark.parametrize('malformed', [None, 'missing', 'duplicate', 'unknown_node'])
def test_metadata_insertion_does_not_erase_unchanged_adverse_history(rig, monkeypatch, malformed):
    from ara.runtime.proposal import retain_disclosure
    from ara.runtime.essay_audit import audit_consensus
    calls,provider,log=rig
    r,_=setup(calls,log)
    old=dict(title='P — '+DISCLOSURE, body='Abstract\n'+DISCLOSURE+'.\n[[node:n0]] [[node:n1]] This paper proposes P.\nMethodology\n'+DISCLOSURE+'.\nThis paper argues Q.', bibliography=[])
    import ara.runtime.proposal as proposal_module
    validate=proposal_module.validate_disclosure
    monkeypatch.setattr(proposal_module,'validate_disclosure',lambda p,d:validate(p,d,allow_legacy=True))
    inputs=calls.audit_inputs(r,old)
    labels=[label(s['sentence'], 'proposed_principle' if s['sentence']==3 else
                  'unsupported_claim' if s['text']=='This paper argues Q.' else 'framing',
                  ('n0','n1') if s['sentence']==3 else ()) for s in inputs['sentences']]
    if malformed is None:
        register(calls,provider,'audit_essay',inputs,dict(labels=labels))
        with pytest.raises(EssayAuditFailed):calls.audit_essay(r,old)
    else:
        from ara.types import RunEvent
        from ara.runtime.logging import now
        from ara.runtime.cache import canonical
        if malformed == 'missing': labels = labels[1:]
        elif malformed == 'duplicate': labels.append(labels[0])
        else: labels[0] = {**labels[0], 'node_ids':['unknown']}
        log.emit(RunEvent(now(), 'audit_essay', 'MODEL', prompt=calls.render('audit_essay',inputs)[1],
                          response=canonical(response(dict(labels=labels)))))
    monkeypatch.setattr(proposal_module,'validate_disclosure',validate)
    current=retain_disclosure(calls,r,old,phase='resume')
    def complete(kind,prompt,schema,maximum):
        data=json.loads(prompt.split('INPUT_JSON\n')[1])
        return Response(response(dict(labels=[label(s['sentence'],
            'proposed_principle' if 'This paper proposes P.' in s['text'] else
            'argument_for_proposal' if s['text']=='This paper argues Q.' else 'framing',
            ('n0','n1') if 'This paper proposes P.' in s['text'] else ()) for s in data['sentences']])))
    monkeypatch.setattr(provider,'complete',complete)
    with pytest.raises(EssayAuditFailed) as failure:audit_consensus(calls,r,current)
    assert failure.value.result['historical_adverse']
    assert any(f['reason']=='unsupported_claim' for f in failure.value.result['flags'])
