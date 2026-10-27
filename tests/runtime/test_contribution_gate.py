"""Phi2's placeholder probes at proposal, native closure and selection boundaries."""
import json
from dataclasses import replace
import pytest

from ara.bank import load_bank
from ara.runtime.orchestration import NativeEngine
from ara.runtime.route_policy import route_classification, selectable_routes
from ara.types import Formula, Proposition, Commitment, CommitmentSet, Term
from test_search_alignment import rig, P, Q, R, T, ROOT, GOAL, cut, PQ


def payloads(calls,stage):
    return [json.loads(e['payload_json']) for e in calls.log.read() if e['stage']==stage]


def provider_for(goal,classification='own_thesis'):
    def reply(kind,inputs):
        if kind=='propose_targets': return {'targets':[goal.to_dict()]}
        if kind=='classify_target':
            assert inputs['target']==goal.to_dict()
            assert 'previous_targets' not in inputs and 'proposals' not in inputs
            return dict(classification=classification,reason='P')
        raise AssertionError(kind)
    return reply


@pytest.mark.parametrize('formula',[
    Formula('and',(P,P)), Formula('and',(P,Formula('implies',(Q,Q)))),
    Formula('implies',(P,P)), P.negated(), Formula('implies',(Q,Q)).negated(),
])
def test_solver_preflight_rejects_single_support_and_both_polarities(tmp_path,formula):
    calls,requests=rig(tmp_path,provider_for(Proposition('p','P',formula)))
    assert calls.propose_targets(T,1)==()
    assert len(payloads(calls,'target_triviality_preflight'))==2
    checks=payloads(calls,'target_contribution_preflight')
    assert checks and all(row['status']=='trivial' for row in checks)
    assert any(row['reason'] in ('single_commitment_entailment','valid_without_support') for row in checks)


@pytest.mark.parametrize('text',[
    'P believes that Q','P defends Q',"Q is P's view",'According to P, Q',
    "On P's account, Q",'P holds Q','P maintains Q',"P's position is Q",
    'P endorses Q','P says Q','P’s view is Q',
])
def test_attributed_reports_rejected_even_when_model_says_own(tmp_path,text):
    calls,requests=rig(tmp_path,provider_for(Proposition('q',text,Q)))
    assert calls.propose_targets(T,1)==()
    assert any(r['reason']=='attributed_report' for e in payloads(calls,'target_triviality_preflight') for r in e['rejected'])


@pytest.mark.parametrize('classification',['attributed_report','unclear'])
def test_classifier_is_required_and_logged_on_same_provider(tmp_path,classification):
    calls,requests=rig(tmp_path,provider_for(GOAL,classification))
    assert calls.propose_targets(T,1)==()
    classified=payloads(calls,'target_own_thesis_classification')
    assert len(classified)==2 and all(e['classification']==classification for e in classified)
    models=[e for e in calls.log.read() if e['label']=='MODEL' and e['stage']=='classify_target']
    assert len(models)==2 and json.loads(models[-1]['payload_json'])['cache_hit']
    assert any(k=='classify_target' for k,_ in requests)


def test_own_thesis_with_two_needed_commitments_is_accepted(tmp_path):
    calls,requests=rig(tmp_path,provider_for(GOAL))
    assert calls.propose_targets(T,1)==(GOAL,)
    assert [k for k,_ in requests]==['propose_targets','classify_target']
    assert payloads(calls,'target_contribution_preflight')[0]['status']=='candidate'


@pytest.mark.parametrize('padded',[False,True])
def test_native_single_support_closure_is_licensed_but_not_selectable(tmp_path,padded):
    taut=Formula('implies',(Q,Q))
    formula=Formula('and',(P,taut if padded else P));goal=Proposition('p','P',formula)
    def reply(kind,inputs):
        if kind=='map_leaf': return {'t_id':'open'}
        if kind=='propose_cuts':
            if inputs['goal']['formula']==formula.to_dict():
                bank='conjunction_introduction'
                fills=[dict(slot='left',text='P',t_id='t1',scope_id=None),
                       dict(slot='right',text='Q -> Q' if padded else 'P',t_id='open' if padded else 't1',scope_id=None)]
            else:
                bank='conditional_proof'
                fills=[dict(slot=s,text='Q',t_id='open',scope_id='conditional') for s in ('assumption','result')]
            return {'proposals':[dict(bank_id=bank,premises=fills,conclusion_text=inputs['goal']['text'],conclusion_ref='current_goal')]}
        if kind=='formalise_slots':
            pairs=[('left',P),('right',taut if padded else P)] if inputs['goal']['formula']==formula.to_dict() else [('assumption',Q),('result',Q)]
            return {'slots':[dict(slot=s,formula=f.to_dict()) for s,f in pairs]}
        raise AssertionError(kind)
    calls,_=rig(tmp_path,reply)
    routes=NativeEngine(load_bank(ROOT/'bank'),calls)._engine(T).search(goal).routes
    assert routes[0].status=='CLOSED'
    assert any(e['decision'] and e['decision']['reason_code']=='BANK_LICENSED' for e in calls.log.read())
    assert route_classification(routes[0],T)=='CLOSED-single-support'
    assert not selectable_routes(routes,T)


def test_alpha_equivalent_instance_and_cache(tmp_path,monkeypatch):
    from ara.runtime.contribution import contribution_check, clear_entailment_cache
    import ara.runtime.contribution as contribution
    x,y,z=[Term('variable',n) for n in ('x','y','z')];a=Term('constant','a')
    pred=lambda *ts: Formula('predicate',name='F',terms=ts)
    universal=Formula('forall',(Formula('forall',(pred(x,y),),variable='y'),),variable='x')
    t=CommitmentSet((Commitment('t','P','placeholder:1',universal),))
    first=Formula('forall',(pred(a,y),),variable='y')
    second=Formula('forall',(pred(a,z),),variable='z')
    clear_entailment_cache();seen=[];original=contribution.entails
    def counted(premises,goal,timeout_ms):
        seen.append((premises,goal,timeout_ms));return original(premises,goal,timeout_ms)
    monkeypatch.setattr(contribution,'entails',counted)
    assert contribution_check(first,t)['status']=='trivial'
    count=len(seen)
    assert contribution_check(second,t)['status']=='trivial'
    assert len(seen)==count
    assert all(0<timeout<=1000 for _,_,timeout in seen)


def test_solver_unknown_fails_closed(tmp_path,monkeypatch):
    from ara.runtime import contribution
    contribution.clear_entailment_cache()
    monkeypatch.setattr(contribution,'entails',lambda *args:'SOLVER_TIMEOUT')
    calls,_=rig(tmp_path,provider_for(GOAL))
    assert calls.propose_targets(T,1)==()
    assert all(e['status']=='unresolved' for e in payloads(calls,'target_contribution_preflight'))
    contribution.clear_entailment_cache()


def closed_graph(goal=GOAL):
    from ara.types import RouteGraph, RouteNode, Proposal
    return RouteGraph('d','n',(
        RouteNode('n',goal,'inference',proposal=Proposal.from_dict(cut(conclusion_text=goal.text)),children=('a','b')),
        RouteNode('a',Proposition('a','P -> Q',PQ),'leaf','t2'),
        RouteNode('b',Proposition('b','P',P),'leaf','t1')),'CLOSED')


def test_two_supports_do_not_override_single_support_entailment(tmp_path):
    from ara.runtime.frozen_catalogue import frozen_artifact
    from ara.runtime.cache import canonical
    from ara.runtime.route_policy import route_contribution
    taut=Formula('implies',(Q,Q))
    t=CommitmentSet((Commitment('t1','P','placeholder:1',P),
                     Commitment('t2','Q -> Q','placeholder:2',taut)))
    goal=Proposition('p','P',Formula('and',(P,taut)))
    def reply(kind,inputs):
        if kind=='map_leaf': return dict(t_id='open')
        if kind=='propose_cuts':
            return dict(proposals=[dict(bank_id='conjunction_introduction',conclusion_text=goal.text,
                conclusion_ref='current_goal',premises=[dict(slot=s,text=c.text,t_id=c.id,scope_id=None)
                for s,c in zip(('left','right'),t.commitments)])])
        if kind=='formalise_slots':
            return dict(slots=[dict(slot=s,formula=c.formula.to_dict()) for s,c in zip(('left','right'),t.commitments)])
        raise AssertionError(kind)
    calls,_=rig(tmp_path,reply)
    (tmp_path/'frozen-t.json').write_text(canonical(frozen_artifact(t,[
        dict(name=n,kind='atom',arity=0,definition=n,evidence_ids=['t1' if n=='P' else 't2']) for n in ('P','Q')])))
    routes=NativeEngine(load_bank(ROOT/'bank'),calls)._engine(t).search(goal).routes
    assert routes[0].status=='CLOSED'
    assert route_contribution(routes[0],t)['support_ids']==['t1','t2']
    assert route_classification(routes[0],t)=='CLOSED-single-support'
    assert not selectable_routes(routes,t)
    assert any(e['decision'] and e['decision']['reason_code']=='BANK_LICENSED' for e in calls.log.read())


def test_supports_exclude_assumptions_and_deduplicate_aliases():
    from ara.types import RouteNode
    graph=closed_graph()
    alias=Commitment('alias','P','placeholder:3',P)
    t=CommitmentSet((T.commitments[0],alias,T.commitments[1]))
    assumption=RouteNode('c',Proposition('c','P -> Q',PQ),'assumption')
    a=replace(graph.nodes[1],t_id='alias',proposition=Proposition('a','P',P))
    graph=replace(graph,nodes=(replace(graph.nodes[0],children=('a','b','c')),a,graph.nodes[2],assumption))
    assert route_classification(graph,t)=='CLOSED-single-support'


def test_cq_dependencies_are_support_and_unknown_fails_closed(monkeypatch):
    from ara.types import CQAnswer
    from ara.runtime import contribution
    from ara.runtime.route_policy import route_contribution
    graph=closed_graph()
    graph=replace(graph,nodes=(replace(graph.nodes[0],children=('b',),
        cq_answers=(CQAnswer('cq','P',True,('t2',)),)),graph.nodes[2]))
    assert route_classification(graph,T)=='CLOSED-derived'
    assert route_contribution(graph,T)['support_ids']==['t1','t2']
    assert route_classification(graph)=='CLOSED-contribution-unresolved'
    contribution.clear_entailment_cache()
    monkeypatch.setattr(contribution,'entails',lambda *args:'SOLVER_UNKNOWN')
    assert route_classification(graph,T)=='CLOSED-contribution-unresolved'
    assert not selectable_routes((graph,),T)
    contribution.clear_entailment_cache()


def test_catalogue_top_level_attribution_is_rejected(tmp_path):
    from ara.runtime.frozen_catalogue import frozen_artifact
    from ara.runtime.cache import canonical
    calls,_=rig(tmp_path,provider_for(GOAL))
    symbols=[dict(name=n,kind='atom',arity=0,definition='P believes that Q' if n=='Q' else 'P',
                  evidence_ids=['t2']) for n in ('P','Q')]
    (tmp_path/'frozen-t.json').write_text(canonical(frozen_artifact(T,symbols)))
    assert calls.propose_targets(T,1)==()
    assert any(r['reason']=='attributed_report' for e in payloads(calls,'target_triviality_preflight') for r in e['rejected'])


def test_native_attributed_closure_not_default_selectable(tmp_path):
    goal=Proposition('q','P believes that Q',Q)
    def reply(kind,inputs):
        if kind=='map_leaf': return {'t_id':'open'}
        if kind=='propose_cuts': return {'proposals':[cut(conclusion_text=goal.text)]}
        if kind=='formalise_slots': return {'slots':[dict(slot='conditional',formula=PQ.to_dict()),dict(slot='antecedent',formula=P.to_dict())]}
        raise AssertionError(kind)
    calls,_=rig(tmp_path,reply)
    routes=NativeEngine(load_bank(ROOT/'bank'),calls)._engine(T).search(goal).routes
    assert routes[0].status=='CLOSED'
    assert route_classification(routes[0],T)=='CLOSED-attributed-report'
    assert not selectable_routes(routes,T)


def test_alpha_hash_does_not_capture_free_variables():
    from ara.runtime.contribution import formula_hash
    x,y=Term('variable','x'),Term('variable','y')
    pred=lambda *ts: Formula('predicate',name='F',terms=ts)
    a=Formula('forall',(pred(x,y),),variable='x')
    b=Formula('forall',(pred(y,y),),variable='y')
    assert formula_hash(a)!=formula_hash(b)


def test_validity_without_commitments():
    from ara.runtime.contribution import contribution_check
    result=contribution_check(Formula('implies',(P,P)),CommitmentSet(()))
    assert result['status']=='trivial' and result['reason']=='valid_without_support'
