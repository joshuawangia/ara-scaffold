"""Content assertions and source stances at the native search boundary."""
import json
from dataclasses import replace
import pytest
from ara.bank import load_bank
from ara.runtime.cache import canonical, digest
from ara.runtime.orchestration import NativeEngine
from ara.runtime.search_alignment import catalogue_inputs
from ara.runtime.route_policy import route_contribution
from test_search_alignment import rig, T, P, Q, PQ, GOAL, ROOT, cut
from test_contribution_gate import closed_graph, payloads


def provenance(directory, stance='endorsed'):
    catalogue = json.loads((directory/'frozen-t.json').read_text())['symbol_catalogue']
    roles = {'endorsed':'author_claim','reported':'reported_view','attacked':'attacked_view'}
    entries = {c.id: dict(source_id='p',source_authors=['P'],attributed_to='P',
        page_start=1,page_end=1,evidence_id=c.id,attribution=roles[stance if c.id=='t1' else 'endorsed'],
        stance=stance if c.id=='t1' else 'endorsed',source_kind='premise',
        source_text='P holds Q',omitted_support_ids=[]) for c in T.commitments}
    data = dict(schema_version='commitment-provenance-v1',definition_semantics='content',
        commitments_sha256=digest(canonical(T.to_dict())),catalogue_sha256=catalogue['sha256'],commitments=entries)
    data['sha256'] = digest(canonical(data))
    (directory/'commitment-provenance.json').write_text(canonical(data))
    return data


def reply(kind, inputs):
    if kind=='map_leaf': return dict(t_id='t1' if inputs['leaf']['formula']==P.to_dict() else 'open')
    if kind=='propose_cuts': return dict(proposals=[cut()] if inputs['goal']['formula']==Q.to_dict() else [])
    if kind=='formalise_slots': return dict(slots=[dict(slot=b['slot'],formula=b['formula']) for b in inputs['slot_bindings']])
    if kind=='tier1_repair': return dict(action='unresolved',detail='P',proposals=[])
    raise AssertionError(kind)


def test_classifier_assertion_uses_content_not_source_voice(tmp_path):
    def respond(kind, inputs):
        if kind=='propose_targets': return dict(targets=[GOAL.to_dict()])
        assert kind=='classify_target'
        assert inputs['target']==GOAL.to_dict()
        assert inputs['rendered_content']==dict(op='atom',name='Q',definition='Q',terms=[])
        assert inputs['definition_semantics']=='content'
        assert 'P holds Q' not in canonical(inputs)
        return dict(classification='own_thesis',reason='Q')
    calls,_=rig(tmp_path,respond)
    provenance(tmp_path)
    assert calls.propose_targets(T,1)==(GOAL,)


@pytest.mark.parametrize('stance',['reported','attacked'])
def test_restricted_support_cannot_close_native_route(tmp_path,stance):
    calls,requests=rig(tmp_path,reply)
    data=provenance(tmp_path,stance)
    engine=NativeEngine(load_bank(ROOT/'bank'),calls)._engine(T)
    result=engine.analyse(GOAL)
    assert all(r.status=='OPEN' for r in result.target.routes)
    assert not result.forward
    assert engine.frozen_commitments==T
    assert [c.id for c in engine.commitments.commitments]==['t2']
    assert any(e['decision'] and e['decision']['reason_code']=='STANCE_CROSSING' for e in calls.log.read())
    inputs=next(i for k,i in requests if k=='propose_cuts')
    assert inputs['commitment_provenance']==data
    receipt=route_contribution(closed_graph(),T,data)
    assert receipt['classification']=='CLOSED-stance-crossing'
    assert receipt['stance_crossings']==[dict(commitment_id='t1',stance=stance,role='global_premise')]


def test_endorsed_support_closes_and_legacy_is_disclosed(tmp_path):
    calls,_=rig(tmp_path,reply)
    assert catalogue_inputs(tmp_path,T)['provenance_status']=='unavailable_legacy'
    provenance(tmp_path)
    engine=NativeEngine(load_bank(ROOT/'bank'),calls)._engine(T)
    assert engine.search(GOAL).routes[0].status=='CLOSED'


def test_provenance_tamper_refuses_and_changes_cache_context(tmp_path):
    calls,_=rig(tmp_path,reply)
    first=provenance(tmp_path)
    a=catalogue_inputs(tmp_path,T)
    second=provenance(tmp_path,'reported')
    b=catalogue_inputs(tmp_path,T)
    assert a['provenance_sha256']!=b['provenance_sha256']
    second['commitments']['t1']['stance']='endorsed'
    (tmp_path/'commitment-provenance.json').write_text(canonical(second))
    with pytest.raises(ValueError): NativeEngine(load_bank(ROOT/'bank'),calls)._engine(T)


def test_report_and_selection_disclose_historical_crossing(tmp_path):
    from ara.runtime.report import build_run
    from ara.runtime.route_policy import selectable_routes, provenance_from_events
    calls,_=rig(tmp_path,reply)
    data=provenance(tmp_path,'attacked')
    catalogue=json.loads((tmp_path/'frozen-t.json').read_text())['symbol_catalogue']
    calls.log.record('symbol_catalogue_frozen',**catalogue)
    calls.log.record('commitment_provenance_frozen',**data)
    calls.log.record('commitments_frozen',commitments=T.to_dict())
    calls.log.record('route',target='q',polarity='target',graph=closed_graph().to_dict())
    assert not selectable_routes((closed_graph(),),T,provenance_from_events(calls.log.read(),T))
    run=build_run(tmp_path)
    assert run['routes'][0]['classification']=='CLOSED-stance-crossing'
    assert run['routes'][0]['contribution']['stance_crossings'][0]['stance']=='attacked'


def test_restored_crossing_refused_before_analysis(tmp_path):
    from ara.engine.search import SearchResult
    calls,_=rig(tmp_path,reply)
    provenance(tmp_path,'reported')
    result=SearchResult(GOAL,(closed_graph(),),1,3,False)
    with pytest.raises(ValueError,match='restored search crosses'):
        list(NativeEngine(load_bank(ROOT/'bank'),calls).analyse_all((GOAL,),T,1,restored={0:(result,())}))


@pytest.mark.parametrize('stance',['reported','attacked'])
def test_restricted_content_allowed_as_scoped_hypothesis(tmp_path,stance):
    from ara.types import Formula, Proposition
    goal=Proposition('pp','P -> P',Formula('implies',(P,P)))
    def scoped(kind,inputs):
        if kind=='propose_cuts':
            return dict(proposals=[dict(bank_id='conditional_proof',conclusion_text=goal.text,
                conclusion_ref='current_goal',premises=[dict(slot=s,text='P',t_id='open',scope_id='conditional')
                for s in ('assumption','result')])])
        if kind=='formalise_slots': return dict(slots=[dict(slot=s,formula=P.to_dict()) for s in ('assumption','result')])
        return reply(kind,inputs)
    calls,_=rig(tmp_path,scoped)
    data=provenance(tmp_path,stance)
    route=NativeEngine(load_bank(ROOT/'bank'),calls)._engine(T).search(goal).routes[0]
    assert route.status=='CLOSED'
    assert all(n.kind=='assumption' for n in route.nodes if n.id!=route.root_id)
    assert route_contribution(route,T,data)['stance_crossings']==[]
    assert {r['stance'] for r in route_contribution(route,T,data)['scoped_source_roles']}=={stance}
    assert route_contribution(route,T,data)['classification']=='CLOSED-single-support'


def test_restricted_cq_evidence_keeps_native_route_open(tmp_path):
    def cq(kind,inputs):
        if kind=='propose_cuts':
            return dict(proposals=[dict(bank_id='sign',conclusion_text='Q',conclusion_ref='current_goal',premises=[
                dict(slot=s,text='P -> Q',t_id='t2',scope_id=None) for s in ('sign_relation','observed_sign')])])
        if kind=='answer_cq': return dict(cq_id=inputs['question']['id'],answer='P',answered=True,supporting_t_ids=['t1'])
        return reply(kind,inputs)
    calls,_=rig(tmp_path,cq)
    data=provenance(tmp_path,'reported')
    route=NativeEngine(load_bank(ROOT/'bank'),calls)._engine(T).search(GOAL).routes[0]
    assert route.status=='OPEN'
    assert any(n.cq_answers for n in route.nodes)
    decisions=[e['decision']['reason_code'] for e in calls.log.read() if e['decision']]
    assert 'CQ_UNSUPPORTED' in decisions and 'CQ_SUPPORTED' not in decisions
    assert route_contribution(route,T,data)['stance_crossings']==[dict(commitment_id='t1',stance='reported',role='cq_evidence')]


@pytest.mark.parametrize('defect',[None,'missing','tamper','receipt'])
def test_fork_preserves_provenance_or_refuses(tmp_path,defect):
    from ara.runtime.freeze_fork import fork_from_freeze
    from ara.runtime.logging import EventLog
    from test_freeze_fork import source
    # Rebuild the source event sequence so the stance receipt belongs to the freeze prefix.
    src,config,bank,_=source(tmp_path)
    data=provenance(src,'reported')
    events=EventLog(src/'events.jsonl').read()
    (src/'events.jsonl').unlink();(src/'events.anchor').unlink()
    log=EventLog(src/'events.jsonl')
    from ara.types import RunEvent
    for event in events:
        if event['stage']=='commitments_frozen':
            log.record('commitment_provenance_frozen',**(dict(data,sha256='0'*64) if defect=='receipt' else data))
        log.emit(RunEvent.from_dict(event))
    if defect=='missing': (src/'commitment-provenance.json').unlink()
    if defect=='tamper': (src/'commitment-provenance.json').write_text('{}')
    destination=tmp_path/'fork'
    if defect:
        with pytest.raises(ValueError): fork_from_freeze(src,destination,bank)
        assert not destination.exists()
    else:
        fork_from_freeze(src,destination,bank)
        assert (destination/'commitment-provenance.json').read_bytes()==(src/'commitment-provenance.json').read_bytes()
        assert catalogue_inputs(destination,T)['commitment_provenance']==data


@pytest.mark.parametrize('defect',[None,'missing','changed'])
def test_native_resume_preserves_stance_and_refuses_lost_metadata(tmp_path,defect):
    from ara.runtime.orchestration import search_all
    from ara.runtime.search_resume import load_search_resume
    calls,_=rig(tmp_path,reply)
    data=provenance(tmp_path,'reported')
    bank=load_bank(ROOT/'bank')
    catalogue=json.loads((tmp_path/'frozen-t.json').read_text())['symbol_catalogue']
    (tmp_path/'commitments.json').write_text(T.to_json())
    calls.log.record('run_started',config=calls.config,topic='P',literature='P',audience='P',bank_version=bank.bank_version)
    calls.log.record('symbol_catalogue_frozen',**catalogue)
    calls.log.record('commitment_provenance_frozen',**data)
    calls.log.record('commitments_frozen',commitments=T.to_dict(),bank_version=bank.bank_version)
    calls.log.record('candidates',candidates=[GOAL.to_dict()])
    routes=search_all(calls,NativeEngine(bank,calls),T,(GOAL,))
    assert routes and all(r.status=='OPEN' for r in routes)
    if defect=='missing': (tmp_path/'commitment-provenance.json').unlink()
    if defect=='changed': provenance(tmp_path,'endorsed')
    if defect:
        with pytest.raises(ValueError,match='provenance receipt mismatch'):
            load_search_resume(calls.log,bank,ROOT)
    else:
        state=load_search_resume(calls.log,bank,ROOT)
        assert len(state.restored)==2
        assert all(r.status=='OPEN' for result,_ in state.restored.values() for r in result.routes)


def test_native_engine_refuses_deleted_stance_receipt(tmp_path):
    calls,_=rig(tmp_path,reply)
    data=provenance(tmp_path,'attacked')
    calls.log.record('symbol_catalogue_frozen',**json.loads((tmp_path/'frozen-t.json').read_text())['symbol_catalogue'])
    calls.log.record('commitment_provenance_frozen',**data)
    calls.log.record('commitments_frozen',commitments=T.to_dict())
    (tmp_path/'commitment-provenance.json').unlink()
    with pytest.raises(ValueError,match='provenance receipt mismatch'):
        NativeEngine(load_bank(ROOT/'bank'),calls)._engine(T)


def test_writer_and_auditor_preserve_source_roles(tmp_path):
    calls,_=rig(tmp_path,reply)
    data=provenance(tmp_path,'attacked')
    calls.log.record('symbol_catalogue_frozen',**json.loads((tmp_path/'frozen-t.json').read_text())['symbol_catalogue'])
    calls.log.record('commitment_provenance_frozen',**data)
    calls.log.record('commitments_frozen',commitments=T.to_dict())
    route=closed_graph()
    outline=calls.essay_inputs(route)['outline']
    role=next(row for row in outline['source_roles'] if row['node_id']=='b')
    assert role==dict(node_id='b',evidence_id='t1',role='global_premise',stance='attacked',
                     attributed_to='P',source_id='p')
    assert calls.audit_inputs(route,dict(body='Q'))['outline']==outline
    assert 'classification' not in outline and 'provenance_sha256' not in outline
