"""Kappa4's semantic wrappers, definitions and native closure regressions."""
import json
from dataclasses import replace
import pytest
from ara.types import Formula as F, Proposition, Commitment, CommitmentSet
from ara.runtime.novelty import novelty_check
from ara.runtime.orchestration import NativeEngine, search_all
from ara.runtime.route_policy import route_contribution, selectable_routes
from ara.runtime.providers import Response
from test_search_alignment import raw
from test_novelty_policy import setup,T,P,Q,R,AND

S=F('atom',name='S')
I=F('implies',(R,AND));J=F('implies',(S,AND));WRAPPED=F('and',(I,J))
WRAPPERS=[I,WRAPPED,F('implies',(F('or',(R,S)),AND)),
    F('or',(R.negated(),AND)),F('not',(F('not',(I,)),)),
    F('not',(F('forall',(I.negated(),),variable='x'),))]


@pytest.mark.parametrize('formula',WRAPPERS)
def test_deductive_closure_rejects_every_wrapper(formula):
    from test_cross_paper import frozen_metadata
    _,provenance=frozen_metadata(T,('a','a'))
    result=novelty_check(formula,T,provenance)
    assert result['status']=='rejected'
    assert result['reason']=='single_paper_closure'


def test_deduction_stays_valid_but_is_not_novel():
    from ara.formal import entails
    t=CommitmentSet((T.commitments[0],Commitment('t2','P -> Q','placeholder:2',F('implies',(P,Q)))))
    assert entails(tuple(c.formula for c in t.commitments),Q,1000)=='SOLVER_UNSAT'
    assert novelty_check(Q,t)['reason']=='deductive_closure'
    assert novelty_check(R,t)['status']=='candidate'


def test_new_atom_must_change_truth_under_t():
    # R is only syntactically present; under P, this is equivalent to not Q.
    t=CommitmentSet((T.commitments[0],))
    vacuous=F('and',(F('or',(P,R)),Q.negated()))
    result=novelty_check(vacuous,t)
    assert result['status']=='candidate'
    assert [a['name'] for a in result['essential_new_propositions']]==['Q']
    # With Q also in T, every occurrence is vacuous or frozen.
    assert novelty_check(F('or',(R,AND)),T)['reason']=='deductive_closure'


def test_native_unused_assumptions_are_not_substantive(tmp_path):
    # Padding a consequence already available within one paper stays single-paper.
    calls,bank,_,_,provenance=setup(tmp_path, ('a','a'))
    calls.config['forward_pass_depth']=0
    texts={'P':P,'Q':Q,'R':R,'S':S,'P and Q':AND,'R -> (P and Q)':I,'S -> (P and Q)':J}
    goal=Proposition('wrapped','(R -> (P and Q)) and (S -> (P and Q))',WRAPPED)
    def reply(kind,inputs):
        if kind=='map_leaf':return dict(t_id='open')
        if kind=='propose_cuts':
            f=F.from_dict(inputs['goal']['formula'])
            if f==WRAPPED:scheme,ps='conjunction_introduction',[('left','R -> (P and Q)','open',None),('right','S -> (P and Q)','open',None)]
            elif f in (I,J):scheme,ps='conditional_proof',[('assumption','R' if f==I else 'S','open','conditional'),('result','P and Q','open','conditional')]
            elif f==AND:scheme,ps='conjunction_introduction',[('left','P','t1',None),('right','Q','t2',None)]
            else:return dict(proposals=[])
            return dict(proposals=[dict(bank_id=scheme,conclusion_text=inputs['goal']['text'],conclusion_ref='current_goal',
                premises=[dict(slot=s,text=t,t_id=i,scope_id=sc) for s,t,i,sc in ps])])
        if kind=='formalise_slots':return dict(slots=[dict(slot=b['slot'],formula=b['formula'] or texts[b['text']].to_dict()) for b in inputs['slot_bindings']])
        raise AssertionError(kind)
    calls.provider.complete=lambda kind,prompt,*args:Response(raw(reply(kind,json.loads(prompt.split('\nINPUT_JSON\n')[1]))))
    routes=search_all(calls,NativeEngine(bank,calls),T,(goal,))
    closed=[r for r in routes if r.status=='CLOSED']
    assert closed
    assert all(route_contribution(r,T,provenance)['classification']=='CLOSED-single-paper' for r in closed)
    assert not selectable_routes(routes,T,provenance)


@pytest.mark.parametrize('text',['P','R := (P and Q)'])
def test_native_renaming_probes_rejected(tmp_path,text):
    calls,_,_,_,_=setup(tmp_path)
    goal=Proposition('rename',text,R)
    def reply(kind,inputs):
        if kind=='propose_targets':return dict(targets=[goal.to_dict()])
        assert inputs['frozen_content']==[dict(id=c.id,text=c.text,formula=c.formula.to_dict()) for c in T.commitments]
        return dict(novelty='restatement' if ':=' in text else 'new_assertion',fidelity='matches',classification='own_thesis',reason='P')
    calls.provider.complete=lambda kind,prompt,*args:Response(raw(reply(kind,json.loads(prompt.split('\nINPUT_JSON\n')[1]))))
    assert calls.propose_targets(T,1)==()


@pytest.mark.parametrize('definition',[' P. ','p','P Q R S P Q R S P Q R R'])
def test_definition_equality_and_near_duplicate_rejected(tmp_path,definition):
    from ara.types import SymbolDefinition
    from ara.runtime.cache import canonical
    from ara.runtime.frozen_catalogue import frozen_artifact
    from test_search_alignment import rig
    calls,_=rig(tmp_path,lambda *_:{})
    t=CommitmentSet((replace(T.commitments[0],text='P' if len(definition)<8 else 'P Q R S P Q R S P Q R S'),T.commitments[1]))
    (tmp_path/'frozen-t.json').write_text(canonical(frozen_artifact(t,
        [dict(name=n,kind='atom',arity=0,definition=n,evidence_ids=['t1','t2']) for n in ('P','Q')])))
    goal=Proposition('r','R',R,(SymbolDefinition('R','atom',0,definition),))
    def reply(kind,inputs):
        if kind=='propose_targets':return dict(targets=[goal.to_dict()])
        return dict(classification='own_thesis',novelty='new_assertion',fidelity='matches',reason='R')
    calls.provider.complete=lambda kind,prompt,*args:Response(raw(reply(kind,json.loads(prompt.split('\nINPUT_JSON\n')[1]))))
    assert calls.propose_targets(t,1)==()
    receipts=[json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='target_triviality_preflight']
    assert all(any(r['reason']=='definition_restates_frozen_content' for r in p['rejected']) for p in receipts)


@pytest.mark.parametrize('novelty,fidelity',[('restatement','matches'),('new_assertion','mismatch'),('unclear','matches'),('new_assertion','unclear')])
def test_logged_content_judgment_is_required(tmp_path,novelty,fidelity):
    calls,_,goal,_,_=setup(tmp_path)
    def reply(kind,inputs):
        if kind=='propose_targets':return dict(targets=[goal.to_dict()])
        assert inputs['rendered_content']['definition']=='R'
        assert inputs['proposed_definitions']==[dict(name='R',kind='atom',arity=0,definition='R')]
        assert [c['text'] for c in inputs['frozen_content']]==['P','Q']
        return dict(classification='own_thesis',novelty=novelty,fidelity=fidelity,reason='R')
    calls.provider.complete=lambda kind,prompt,*args:Response(raw(reply(kind,json.loads(prompt.split('\nINPUT_JSON\n')[1]))))
    assert calls.propose_targets(T,1)==()
    logged=[json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='target_own_thesis_classification']
    assert logged and all(p['novelty']==novelty and p['fidelity']==fidelity for p in logged)


def test_unknown_essential_check_refuses(monkeypatch):
    import ara.runtime.novelty as novelty
    answers=iter(['SOLVER_COUNTEREXAMPLE','SOLVER_TIMEOUT','SOLVER_COUNTEREXAMPLE'])
    monkeypatch.setattr(novelty,'cached_entails',lambda *args:next(answers))
    result=novelty.novelty_check(R,T)
    assert result['status']=='unresolved' and result['checks'][-1]['scope']=='essential_atom'


def test_formal_alias_and_genuine_thesis():
    alias=Commitment('t3','R iff (P and Q)','placeholder:3',F('iff',(R,AND)))
    assert novelty_check(R,CommitmentSet(T.commitments+(alias,)))['reason']=='deductive_closure'
    assert novelty_check(R,T)['essential_new_propositions']==[R.to_dict()]


def test_explicit_definition_binding_survives_codec_and_cache(tmp_path):
    from ara.types import SymbolDefinition
    calls,_,_,_,_=setup(tmp_path)
    goal=Proposition('r','R',R,(SymbolDefinition('R','atom',0,'R'),))
    requests=[]
    def reply(kind,inputs):
        requests.append((kind,inputs))
        if kind=='propose_targets':return dict(targets=[goal.to_dict()])
        assert inputs['target']['new_symbols']==[dict(name='R',kind='atom',arity=0,definition='R')]
        return dict(classification='own_thesis',novelty='new_assertion',fidelity='matches',reason='R')
    calls.provider.complete=lambda kind,prompt,*args:Response(raw(reply(kind,json.loads(prompt.split('\nINPUT_JSON\n')[1]))))
    assert calls.propose_targets(T,1)==(goal,)
    assert calls.propose_targets(T,1)==(goal,)
    assert len(requests)==2
    assert Proposition.from_json(goal.to_json())==goal


@pytest.mark.parametrize('defect',['missing','override','extra','duplicate'])
def test_compound_definition_bindings_refuse_missing_or_changed_meanings(tmp_path,defect):
    from ara.types import SymbolDefinition
    calls,_,_,_,_=setup(tmp_path)
    defs=(SymbolDefinition('R','atom',0,'R'),SymbolDefinition('S','atom',0,'S'))
    definitions={'missing':defs[:1], 'override':defs+(SymbolDefinition('P','atom',0,'S'),),
                 'extra':defs+(SymbolDefinition('F','predicate',0,'F'),), 'duplicate':defs+defs[:1]}[defect]
    goal=Proposition('rs','R and S',F('and',(R,S)),definitions)
    def reply(kind,inputs):
        if kind=='propose_targets':return dict(targets=[goal.to_dict()])
        return dict(classification='own_thesis',novelty='new_assertion',fidelity='matches',reason='R S')
    calls.provider.complete=lambda kind,prompt,*args:Response(raw(reply(kind,json.loads(prompt.split('\nINPUT_JSON\n')[1]))))
    assert calls.propose_targets(T,1)==()


def test_quantified_deductive_consequence_is_not_novel():
    from ara.types import Term
    pred=lambda n,t:F('predicate',name=n,terms=(t,))
    x,a=Term('variable','x'),Term('constant','a')
    t=CommitmentSet((Commitment('t1','F(a)','placeholder:1',pred('F',a)),
        Commitment('t2','F(x) -> P(x)','placeholder:2',F('forall',(F('implies',(pred('F',x),pred('P',x))),),variable='x'))))
    assert novelty_check(pred('P',a),t)['status']=='rejected'


def test_only_reachable_step_with_root_essential_proposition_qualifies():
    from ara.types import RouteGraph, RouteNode, Proposal
    leaves=(RouteNode('p',Proposition('p','P',P),'leaf','t1'),RouteNode('q',Proposition('q','Q',Q),'leaf','t2'))
    sign=RouteNode('sign',Proposition('r','R',R),'inference',proposal=Proposal('sign',(),'R'),children=('p','q'))
    root=RouteNode('root',Proposition('s','S',S),'inference',proposal=Proposal('conjunction_elimination',(),'S'),children=('sign',))
    route=RouteGraph('different','root',(root,sign)+leaves,'CLOSED')
    assert route_contribution(route,T)['classification']=='CLOSED-structural'
    # A disconnected sign concluding R must not upgrade a structural R root.
    root=replace(root,proposition=Proposition('r','R',R),children=('p','q'))
    route=replace(route,nodes=(root,sign)+leaves)
    assert route_contribution(route,T)['classification']=='CLOSED-structural'
    # The whole freeze remains authoritative even when the route doesn't cite R.
    root=replace(sign,id='root')
    route=replace(route,nodes=(root,)+leaves)
    from test_cross_paper import frozen_metadata
    _,provenance=frozen_metadata(T,('a','b'))
    assert route_contribution(route,T,provenance)['classification']=='CLOSED-derived'
    full=CommitmentSet(T.commitments+(Commitment('t3','R','placeholder:3',R),))
    assert route_contribution(route,full)['classification']=='CLOSED-structural'


def test_unused_conditional_proof_not_counted_but_new_sign_result_qualifies(tmp_path):
    calls,bank,_,_,provenance=setup(tmp_path)
    calls.config['forward_pass_depth']=0
    goal=Proposition('rs','R -> S',F('implies',(R,S)))
    def reply(kind,inputs):
        if kind=='map_leaf':return dict(t_id='open')
        if kind=='propose_cuts':
            f=F.from_dict(inputs['goal']['formula'])
            if f==goal.formula:scheme,ps='conditional_proof',[('assumption','R','open','conditional'),('result','S','open','conditional')]
            elif f==S:scheme,ps='sign',[('sign_relation','P','t1',None),('observed_sign','Q','t2',None)]
            else:return dict(proposals=[])
            return dict(proposals=[dict(bank_id=scheme,conclusion_text=inputs['goal']['text'],conclusion_ref='current_goal',
                premises=[dict(slot=s,text=t,t_id=i,scope_id=sc) for s,t,i,sc in ps])])
        if kind=='formalise_slots':return dict(slots=[dict(slot=b['slot'],formula=b['formula'] or {'R':R,'S':S}[b['text']].to_dict()) for b in inputs['slot_bindings']])
        if kind=='answer_cq':return dict(cq_id=inputs['question']['id'],answer='P Q',answered=True,supporting_t_ids=['t1','t2'])
        raise AssertionError(kind)
    calls.provider.complete=lambda kind,prompt,*args:Response(raw(reply(kind,json.loads(prompt.split('\nINPUT_JSON\n')[1]))))
    routes=NativeEngine(bank,calls)._engine(T).search(goal).routes
    assert routes[0].status=='CLOSED'
    receipt=route_contribution(routes[0],T,provenance)
    assert receipt['classification']=='CLOSED-derived'
    assert [i['bank_id'] for i in receipt['substantive_inferences']]==['sign']


def test_unused_binder_does_not_make_bound_application_new():
    from ara.types import Term
    px=F('predicate',name='P',terms=(Term('variable','x'),))
    t=CommitmentSet((Commitment('t','P(x)','placeholder:1',F('exists',(px,),variable='x')),))
    target=F('forall',(F('forall',(px,),variable='y'),),variable='x')
    assert novelty_check(target,t)['reason']=='no_essential_new_proposition'


def test_uncertain_step_novelty_is_disclosed_and_not_derived(monkeypatch):
    from ara.types import RouteGraph,RouteNode,Proposal
    import ara.runtime.novelty as novelty
    original=novelty.cached_entails
    monkeypatch.setattr(novelty,'cached_entails',lambda premises,goal,timeout:
        'SOLVER_TIMEOUT' if goal==R else original(premises,goal,timeout))
    root=RouteNode('root',Proposition('rs','R and S',F('and',(R,S))),'inference',
        proposal=Proposal('conjunction_introduction',(),'R and S'),children=('sign',))
    sign=RouteNode('sign',Proposition('r','R',R),'inference',proposal=Proposal('sign',(),'R'),children=('p','q'))
    leaves=(RouteNode('p',Proposition('p','P',P),'leaf','t1'),RouteNode('q',Proposition('q','Q',Q),'leaf','t2'))
    receipt=route_contribution(RouteGraph('uncertain','root',(root,sign)+leaves,'CLOSED'),T)
    assert receipt['classification']=='CLOSED-contribution-unresolved'
    assert receipt['inference_novelty_checks'][0]['novelty']['reason']=='novelty_unresolved'
