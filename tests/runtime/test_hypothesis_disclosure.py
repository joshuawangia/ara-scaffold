import json
from pathlib import Path
import pytest
from test_extraction import offline
from test_hypothesis_premises import freeze_h,route_reply,P,Q,R,configured
from ara.runtime.orchestration import NativeEngine,compose
from ara.runtime.route_policy import selectable_routes
from ara.runtime.writing import source_context
from ara.types import Proposition

STATEMENT="This paper's conclusion is conditional on H (hypothesis:h)."

@pytest.mark.parametrize('disclaimer',['Not Conditional on H.', 'The result is 𝐮𝐧𝐜𝐨𝐧𝐝𝐢𝐭𝐢𝐨𝐧𝐚𝐥.','The result is unconditional; the phrase Conditional on H is unnecessary.', '"Conditional on H."', '> Conditional on H.', '`Conditional on H.`', STATEMENT+'\n\nNot conditional on H.', 'Not:\n\n'+STATEMENT, 'The following statement is false:\n\n'+STATEMENT, STATEMENT+'\n\nThe result is 𝐮𝐧𝐜𝐨𝐧𝐝𝐢𝐭𝐢𝐨𝐧𝐚𝐥.', STATEMENT+'\n\nThe result is **unconditional**.', STATEMENT+'\n\nThe result is un&#99;onditional.', '"'+STATEMENT+'"', '> '+STATEMENT, '```\n'+STATEMENT+'\n```'])
def test_negated_conditional_phrase_native_export(tmp_path,monkeypatch,disclaimer):
    from test_search_alignment import rig,raw,ROOT
    from test_delivery_alignment_citations import aligned_sources
    from ara.runtime.providers import Response
    from ara.bank import load_bank
    calls,_=rig(tmp_path,lambda *_:None)
    (tmp_path/'frozen-t.json').unlink();calls.config['hypothesis_premises']=[configured()]
    _,t,_=aligned_sources(calls,calls.provider,calls.log,monkeypatch)
    meta=calls.search_vocabulary(t)['commitment_provenance']
    def dispatch(kind,prompt,*_):return Response(raw(route_reply(kind,json.loads(prompt.split('INPUT_JSON\n')[1]))))
    monkeypatch.setattr(calls.provider,'complete',dispatch)
    route=selectable_routes(NativeEngine(load_bank(ROOT/'bank'),calls)._engine(t).search(Proposition('r','R',R)).routes,t,meta)[0]
    calls.log.record('route',graph=route.to_dict());evidence=source_context(calls,route)
    body=[];labels=[]
    for i,node in enumerate(route.nodes,1):
        is_h=node.t_id=='hypothesis:h';text='This paper proposes (P and Q) implies R' if is_h else node.proposition.text+' P'
        cite=' [cite:'+node.t_id+']' if node.t_id in ('p','q') else ''
        body.append(f'[[node:{node.id}]] {text}.{cite}')
        labels.append(dict(sentence=i,node_ids=[node.id],role='proposed_principle' if is_h else 'argument_step',citation_supported=True))
    body.append('\n'+disclaimer)
    from ara.runtime.essay_audit import sentence_spans
    for _ in sentence_spans(disclaimer):
        labels.append(dict(sentence=len(labels)+1,node_ids=[],role='framing',citation_supported=True))
    draft=dict(title='P',body='\n'.join(body),bibliography=evidence['allowed_bibliography']);seen=[]
    def complete(kind,prompt,*_):
        seen.append(kind)
        if kind=='write_essay':value=draft
        elif kind=='audit_essay':value=dict(labels=labels)
        elif kind=='search_evidence':value='P'
        else:
            assert kind=='verify_originality_citations';value=dict(items=[],originality=dict(assessment='unverified',detail='P',evidence_urls=[]))
        return Response(raw(value))
    monkeypatch.setattr(calls.provider,'complete',complete)
    # Clean fake labels cannot authorize false or merely quoted disclosure.
    with pytest.raises(ValueError,match='hypothesis disclosure'):
        compose(calls,route)
    assert 'audit_essay' not in seen
    assert not (tmp_path/'export/essay.txt').exists()
    from ara.runtime.export import export_run
    calls.log.record('final_draft',route_id=route.id,draft=draft)
    with pytest.raises(ValueError,match='hypothesis disclosure'):
        export_run(calls.log.path,tmp_path/'export')
    from ara.runtime.publication import publish
    with pytest.raises(ValueError,match='hypothesis disclosure'):
        publish(calls.log,dict(route_id=route.id,markdown=draft['body'],draft=draft))
    assert not (tmp_path/'publication/latest.json').exists()
    # An authenticated legacy publication is still subject to current disclosure.
    import ara.runtime.hypotheses as hypotheses
    from ara.runtime.publication import load_publication
    with monkeypatch.context() as old_policy:
        old_policy.setattr(hypotheses,'validate_disclosure',lambda *_:None)
        old_policy.setattr(hypotheses,'validate_conditional_statement',lambda *_:None)
        publish(calls.log,dict(route_id=route.id,markdown='# P\n\n'+draft['body'],draft=draft,
            polished=True,audit={},local_citations=[],native_citations=[],words=40,bibliographic_records={},
            repair_rounds=0,accepted_repair_rounds=0,word_limits={},repair_validation_attempts=0))
    with pytest.raises(ValueError,match='hypothesis disclosure'):
        load_publication(tmp_path)


@pytest.mark.parametrize('reading_bad',[False,True])
def test_publication_reading_copy_retains_affirmative_disclosure(tmp_path,monkeypatch,reading_bad):
    from ara.runtime.publication import publish
    from ara.types import Proposition
    calls,bank,t,meta,_=freeze_h(tmp_path,monkeypatch,route_reply)
    route=selectable_routes(NativeEngine(bank,calls)._engine(t).search(Proposition('r','R',R)).routes,t,meta)[0]
    calls.log.record('route',graph=route.to_dict())
    lines=[f"[[node:{n.id}]] "+('This paper proposes (P and Q) implies R.' if n.t_id=='hypothesis:h' else 'P Q.')
           for n in route.nodes]
    from ara.runtime.hypotheses import insert_runtime_disclosure
    draft=insert_runtime_disclosure(calls,route,dict(title='P',body='\n'.join(lines),bibliography=[]))
    body='# P\n\n'+draft['body']
    result=dict(route_id=route.id,markdown=body,draft=dict(body=body,bibliography=[]),
        reading_markdown=body.replace(STATEMENT,'Not Conditional on H.') if reading_bad else body,
        polished=True,audit=dict(),local_citations=[],native_citations=[],words=40,bibliographic_records={},
        repair_rounds=0,accepted_repair_rounds=0,word_limits={},repair_validation_attempts=0)
    if reading_bad:
        with pytest.raises(ValueError,match='hypothesis disclosure'):
            publish(calls.log,result)
        assert not (tmp_path/'publication/latest.json').exists()
    else:
        _,directory=publish(calls.log,result)
        assert STATEMENT in (directory/'paper.md').read_text()
        from ara.runtime.publication import load_publication
        assert load_publication(tmp_path)[1] == directory


@pytest.mark.parametrize('corrupted_copy', ['audit', 'reading'])
def test_publication_reload_rechecks_hypothesis_disclosure(tmp_path,monkeypatch,corrupted_copy):
    from ara.runtime.publication import publish, load_publication
    import ara.runtime.hypotheses as hypotheses
    calls,bank,t,meta,_=freeze_h(tmp_path,monkeypatch,route_reply)
    route=selectable_routes(NativeEngine(bank,calls)._engine(t).search(Proposition('r','R',R)).routes,t,meta)[0]
    calls.log.record('route',graph=route.to_dict())
    lines=[f"[[node:{n.id}]] "+('This paper proposes (P and Q) implies R.' if n.t_id=='hypothesis:h' else 'P Q.')
           for n in route.nodes]
    from ara.runtime.hypotheses import insert_runtime_disclosure
    draft=insert_runtime_disclosure(calls,route,dict(title='P',body='\n'.join(lines),bibliography=[]))
    body='# P\n\n'+draft['body']
    invalid=body.replace(STATEMENT,'Not Conditional on H.')
    result=dict(route_id=route.id,markdown=invalid if corrupted_copy=='audit' else body,
        draft=dict(body=body,bibliography=[]),
        reading_markdown=invalid if corrupted_copy=='reading' else body,
        polished=True,audit=dict(),local_citations=[],native_citations=[],words=40,bibliographic_records={},
        repair_rounds=0,accepted_repair_rounds=0,word_limits={},repair_validation_attempts=0)
    # Model an authentic old-policy publication, with valid hashes and logged completion.
    with monkeypatch.context() as old_policy:
        old_policy.setattr(hypotheses,'validate_disclosure',lambda *_:None)
        old_policy.setattr(hypotheses,'validate_conditional_statement',lambda *_:None)
        publish(calls.log,result)
    with pytest.raises(ValueError,match='hypothesis disclosure'):
        load_publication(tmp_path)
