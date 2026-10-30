"""Page-bound citation retention and native export coverage, using placeholders."""
import json

import pytest

from ara.runtime.calls import Rejected
from ara.runtime.providers import Response
from test_calls import rig, response
from test_sectioned_writer import seed_sources


def source_draft(calls, log):
    from ara.runtime.writing import source_context
    route = seed_sources(calls, log, local_pages='P P P Q Q Q R R R')
    entries = source_context(calls, route)['allowed_bibliography']
    return route, dict(title='P', body='[[node:n0]] P P P. [cite:p] [[node:n1]] Q Q Q. [cite:q]',
                       bibliography=entries)


def web_absent(provider, monkeypatch):
    seen=[]
    def complete(kind,prompt,schema,maximum):
        data=json.loads(prompt.split('INPUT_JSON\n')[1]);seen.append((kind,data))
        if kind=='search_evidence':value='P'
        else:
            assert kind=='verify_originality_citations'
            value=dict(items=[{**item,'status':'unverified','action':'remove','detail':'P','evidence_urls':[]}
                              for item in data['items']],
                       originality=dict(assessment='unverified',detail='P',evidence_urls=[]))
        return Response(response(value))
    monkeypatch.setattr(provider,'complete',complete)
    return seen


def test_web_absence_cannot_delete_frozen_citations(rig,monkeypatch):
    calls,provider,log=rig;route,draft=source_draft(calls,log)
    seen=web_absent(provider,monkeypatch)
    cleaned,result=calls.verify_originality_citations(draft)
    assert cleaned==draft
    assert {i['id'] for i in result['items'] if i['status']=='verified'}=={'p','q'}
    assert all(not data['items'] for _,data in seen)
    assert all('PDF p. 1' in b['text'] and 'a (2000)' in b['text'] for b in draft['bibliography'])
    assert any(e['stage']=='local_citation_verification' for e in log.read())


def test_positive_bibliography_mismatch_is_logged_removal(rig,monkeypatch):
    from ara.runtime.export import methodology
    calls,provider,log=rig;route,draft=source_draft(calls,log)
    draft['bibliography'][0]['text']='S'
    web_absent(provider,monkeypatch)
    cleaned,result=calls.verify_originality_citations(draft)
    assert [b['id'] for b in cleaned['bibliography']]==['q']
    item=next(i for i in result['items'] if i['id']=='p')
    assert item['status']=='unverified' and item['removal_reason']=='bibliography_mismatch'
    assert 'bibliography_mismatch' in methodology(log.path)


@pytest.mark.parametrize('bibliography_text', [None, 'S'])
def test_missing_local_pages_refuses_without_deleting_or_web_dispatch(rig,monkeypatch,bibliography_text):
    from ara.runtime.writing import source_context
    calls,provider,log=rig;route=seed_sources(calls,log)
    draft=dict(title='P',body='P. [cite:p]',bibliography=source_context(calls,route)['allowed_bibliography'][:1])
    if bibliography_text is not None:
        draft['bibliography'][0]['text'] = bibliography_text
    seen=web_absent(provider,monkeypatch)
    with pytest.raises(Rejected,match='local citation evidence unresolved'):
        calls.verify_originality_citations(draft)
    assert seen==[] and draft['bibliography']


@pytest.mark.parametrize('quote,retained',[('P P P',True),('P S P',False)])
def test_local_quotation_uses_cited_pages_not_web_absence(rig,monkeypatch,quote,retained):
    calls,provider,log=rig;route,draft=source_draft(calls,log)
    draft['body']=f'"{quote}" [cite:p]'
    web_absent(provider,monkeypatch)
    cleaned,result=calls.verify_originality_citations(draft)
    assert (quote in cleaned['body']) is retained
    assert len(cleaned['bibliography'])==2
    item=next(i for i in result['items'] if i['kind']=='quotation')
    assert item['status']==('verified' if retained else 'unverified')
    if not retained:assert item['removal_reason']=='quotation_mismatch'


def test_cli_zero_citation_export_is_explicit_nonzero(rig,capsys):
    from ara.runtime.cli import main
    calls,provider,log=rig;route,draft=source_draft(calls,log)
    draft.update(body='P.',bibliography=[])
    log.record('route',graph=route.to_dict());log.record('final_draft',route_id=route.id,draft=draft)
    assert main(['export','--run-dir',str(log.path.parent)])==2
    assert 'citation coverage' in capsys.readouterr().err
    assert not (log.path.parent/'export/essay.txt').exists()


@pytest.mark.parametrize('missing',['all','one'])
def test_export_refuses_missing_route_source_coverage(rig,tmp_path,missing):
    from ara.runtime.export import export_run
    calls,provider,log=rig;route,draft=source_draft(calls,log)
    log.record('route',graph=route.to_dict())
    if missing=='all':draft.update(body='[[node:n0]] P P P. [[node:n1]] Q Q Q.',bibliography=[])
    else:
        draft['body']=draft['body'].replace('[cite:q]','')
        draft['bibliography']=draft['bibliography'][:1]
    log.record('final_draft',route_id=route.id,draft=draft)
    output=tmp_path/'export';output.mkdir();(output/'essay.txt').write_text('old')
    with pytest.raises(ValueError,match='citation coverage'):
        export_run(log.path,output)
    assert not (output/'essay.txt').exists()


def test_export_accepts_locally_verified_source_coverage(rig,tmp_path):
    from ara.runtime.export import export_run
    calls,provider,log=rig;route,draft=source_draft(calls,log)
    log.record('route',graph=route.to_dict());log.record('final_draft',route_id=route.id,draft=draft)
    _,essay=export_run(log.path,tmp_path/'export')
    assert 'a (2000)' in essay.read_text() and 'PDF p. 1' in essay.read_text()


def test_citation_restoration_preserves_prose_and_repair_budget(rig,monkeypatch):
    from ara.runtime.orchestration import compose
    from ara.runtime.essay_audit import CITE
    calls,provider,log=rig;route,draft=source_draft(calls,log)
    calls.config['essay_min_words']=4500
    before={**draft,'body':draft['body'].replace('[cite:p]','').replace('[cite:q]',''),'bibliography':[]}
    log.record('route',graph=route.to_dict());log.record('final_draft',route_id=route.id,draft=before)
    log.record('essay_composition_started',route_id=route.id,repair_rounds=3)
    seen=[]
    def complete(kind,prompt,schema,maximum):
        data=json.loads(prompt.split('INPUT_JSON\n')[1]);seen.append((kind,data))
        if kind=='revise_essay':
            assert data['mode']=='citations'
            value={'revisions':[dict(sentence=s['sentence'],text=s['text']+'[cite:'+tid+']')
                                for s,tid in zip(data['flagged_sentences'],['p','q'])]}
        elif kind=='audit_essay':
            value={'labels':[dict(sentence=s['sentence'],role='source_claim',node_ids=['n0','n1'],citation_supported=True)
                             for s in data['sentences']]}
        elif kind=='search_evidence':value='P'
        else:
            assert kind=='verify_originality_citations' and data['items']==[]
            value=dict(items=[],originality=dict(assessment='unverified',detail='P',evidence_urls=[]))
        return Response(response(value))
    monkeypatch.setattr(provider,'complete',complete)
    result=compose(calls,route,before)
    assert CITE.sub('',result['body'])==before['body']
    assert {b['id'] for b in result['bibliography']}=={'p','q'}
    assert len([k for k,_ in seen if k=='audit_essay'])==4
    assert not any(e['stage']=='essay_audit_revision' for e in log.read())
    assert json.loads([e['payload_json'] for e in log.read() if e['stage']=='essay_composition_started'][-1])['repair_rounds']==3


def test_citation_only_restoration_rejects_prose_changes(rig,monkeypatch):
    from ara.runtime.orchestration import compose
    calls,provider,log=rig;route,draft=source_draft(calls,log)
    draft.update(body='[[node:n0]] P P P. [[node:n1]] Q Q Q.',bibliography=[])
    def complete(kind,prompt,schema,maximum):
        assert kind=='revise_essay'
        return Response(response({'revisions':[dict(sentence=1,text='R. [cite:p] [cite:q]')]}))
    monkeypatch.setattr(provider,'complete',complete)
    with pytest.raises(Rejected,match='citation restoration changed prose'):
        compose(calls,route,draft)
    assert not (log.path.parent/'draft.json').exists()


@pytest.mark.parametrize('pages,page_hash',[('S S S',None),('P P P Q Q Q','b'*64)])
def test_local_page_content_and_identity_must_support_citation(rig,monkeypatch,pages,page_hash):
    from ara.runtime.writing import source_context
    calls,provider,log=rig
    route=seed_sources(calls,log,local_pages=pages,local_hash=page_hash)
    draft=dict(title='P',body='P. [cite:p]',bibliography=source_context(calls,route)['allowed_bibliography'][:1])
    seen=web_absent(provider,monkeypatch)
    with pytest.raises(Rejected,match='local citation evidence unresolved'):
        calls.verify_originality_citations(draft)
    assert seen==[]


def test_miscited_sentence_can_add_only_approved_frozen_markers(rig,monkeypatch):
    from ara.runtime.essay_audit import audit_and_revise
    calls,provider,log=rig;route,draft=source_draft(calls,log)
    draft['body']=draft['body'].replace('[cite:q]','')
    seen=[]
    def complete(kind,prompt,schema,maximum):
        data=json.loads(prompt.split('INPUT_JSON\n')[1]);seen.append((kind,data))
        if kind=='audit_essay':
            value={'labels':[dict(sentence=s['sentence'],role='source_claim',node_ids=['n0','n1'],citation_supported=True)
                             for s in data['sentences']]}
        else:
            assert kind=='revise_essay'
            value={'revisions':[dict(sentence=2,text=data['flagged_sentences'][0]['text']+'[cite:q]')]}
        return Response(response(value))
    monkeypatch.setattr(provider,'complete',complete)
    result=audit_and_revise(calls,route,draft)
    assert '[cite:q]' in result['body']
    assert [k for k,_ in seen]==['audit_essay','revise_essay','audit_essay']


def test_cited_argument_step_cannot_hide_mismatched_source(rig,monkeypatch):
    from ara.runtime.calls import EssayAuditFailed
    calls,provider,log=rig;route,draft=source_draft(calls,log)
    def complete(kind,prompt,schema,maximum):
        data=json.loads(prompt.split('INPUT_JSON\n')[1])
        return Response(response({'labels':[dict(sentence=s['sentence'],role='argument_step',node_ids=['n0'] if s['sentence'] == 1 else ['n1'],citation_supported=False)
                                             for s in data['sentences']]}))
    monkeypatch.setattr(provider,'complete',complete)
    with pytest.raises(EssayAuditFailed):calls.audit_essay(route,draft)


def test_uncited_source_premise_cannot_hide_as_argument_step(rig,monkeypatch):
    from ara.runtime.calls import EssayAuditFailed
    calls,provider,log=rig;route,draft=source_draft(calls,log)
    draft['body']=draft['body'].replace('[cite:q]','')
    def complete(kind,prompt,schema,maximum):
        return Response(response({'labels':[dict(sentence=n,role='argument_step',node_ids=[node],citation_supported=True)
                                             for n,node in ((1,'n0'),(2,'n1'))]}))
    monkeypatch.setattr(provider,'complete',complete)
    with pytest.raises(EssayAuditFailed) as failure:calls.audit_essay(route,draft)
    assert failure.value.result['extra_steps']==[2]


@pytest.mark.parametrize('available', [True, False])
def test_native_competition_compose_cannot_strip_frozen_citations_and_export(rig, monkeypatch, available):
    from ara.runtime.orchestration import compose
    from ara.runtime.writing import source_context
    calls, provider, log = rig
    calls.config.update(essay_min_words=4500, token_cap=10_000_000)
    route = seed_sources(calls, log, local_pages='P P P Q Q Q R R R' if available else None)
    before = dict(title='P', body='[[node:n0]] [[node:n1]] ' + 'P ' * 4500 + '[cite:p] [cite:q]',
                  bibliography=source_context(calls, route)['allowed_bibliography'])
    log.record('route', graph=route.to_dict())
    frozen = {name: (log.path.parent / name).read_bytes() for name in
              ('frozen-t.json', 'commitment-provenance.json')}
    def complete(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'audit_essay':
            value = {'labels': [dict(sentence=s['sentence'], node_ids=['n0', 'n1'],
                role='source_claim' if '[cite:' in s['text'] else 'argument_step', citation_supported=True)
                for s in data['sentences']]}
        elif kind == 'search_evidence':
            value = 'P'
        elif kind == 'verify_originality_citations':
            value = dict(items=[{**item, 'status': 'unverified', 'action': 'remove',
                                 'detail': 'P', 'evidence_urls': []} for item in data['items']],
                         originality=dict(assessment='unverified', detail='P', evidence_urls=[]))
        else:
            raise AssertionError(kind)
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    if available:
        after = compose(calls, route, before)
        assert after == before
        assert (log.path.parent / 'export/essay.txt').exists()
        gate = json.loads([e['payload_json'] for e in log.read() if e['stage'] == 'essay_audit_consensus'][-1])
        assert len(gate['samples']) == 3 and gate['faithful']
    else:
        with pytest.raises(Rejected, match='local citation evidence unresolved'):
            compose(calls, route, before)
        assert not (log.path.parent / 'export/essay.txt').exists()
    assert frozen == {name: (log.path.parent / name).read_bytes() for name in frozen}


def test_frozen_reference_without_provenance_refuses_instead_of_web_removal(rig, monkeypatch):
    from ara.types import Commitment, CommitmentSet, Formula
    calls, provider, log = rig
    frozen = CommitmentSet((Commitment('p', 'P', 'P', Formula('atom', name='P')),))
    log.record('commitments_frozen', commitments=frozen.to_dict())
    before = dict(title='P', body='P. [cite:p]', bibliography=[dict(id='p', text='P', url=None)])
    seen = web_absent(provider, monkeypatch)
    with pytest.raises(Rejected, match='local citation evidence unresolved'):
        calls.verify_originality_citations(before)
    assert seen == [] and before['bibliography']
