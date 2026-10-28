"""Boolean repackaging is not a new main assertion; structural closure is disclosed."""
from dataclasses import replace
import json
import pytest
from ara.bank import load_bank
from ara.runtime.cache import canonical
from ara.runtime.orchestration import NativeEngine, search_all
from ara.runtime.route_policy import route_contribution, selectable_routes
from ara.types import Commitment, CommitmentSet, Formula, Proposition, Term, RouteNode, Proposal
from test_search_alignment import rig, ROOT, P, Q, R

T=CommitmentSet((Commitment('t1','P','placeholder:1',P),Commitment('t2','Q','placeholder:2',Q)))
AND=Formula('and',(P,Q))


@pytest.mark.parametrize('formula',[AND,Formula('or',(P,Q)),
    Formula('not',(Formula('or',(P.negated(),Q.negated())),)),
    Formula('not',(Formula('implies',(P,Q.negated())),)),
    Formula('and',(AND,Formula('or',(R,R.negated())))),
    Formula('or',(Formula('and',(AND,R)),Formula('and',(AND,R.negated()))))])
def test_equivalent_boolean_packages_rejected(formula):
    from ara.runtime.novelty import novelty_check
    receipt=novelty_check(formula,T)
    assert receipt['status']=='rejected'
    assert receipt['reason'] in ('deductive_closure','no_essential_new_proposition')
    assert any(c['solver_result']=='SOLVER_UNSAT' for c in receipt['checks'])
    assert receipt['basis_commitment_ids']==['t1','t2']


def test_new_main_claim_not_vacuous_or_only_antecedent():
    from ara.runtime.novelty import novelty_check
    s=Formula('atom',name='S')
    for conclusion in (AND,Formula('and',(AND,Formula('or',(R,R.negated()))))):
        receipt=novelty_check(Formula('implies',(s,conclusion)),T)
        assert receipt['status']=='rejected' and receipt['reason']=='deductive_closure'
    assert novelty_check(R,T)['status']=='candidate'
    deductive=CommitmentSet((T.commitments[0],Commitment('t2','P -> Q','placeholder:2',Formula('implies',(P,Q)))))
    assert novelty_check(Q,deductive)['reason']=='deductive_closure'


def test_predicate_application_and_quantified_equivalence():
    from ara.runtime.novelty import novelty_check
    def pred(kind,name):return Formula('predicate',name='F',terms=(Term(kind,name),))
    a,b=pred('constant','a'),pred('constant','b')
    t=CommitmentSet((Commitment('t1','F(a)','placeholder:1',a),))
    assert novelty_check(b,t)['status']=='candidate'
    x,y=pred('variable','x'),pred('variable','y')
    t=CommitmentSet((Commitment('t1','F(x)','placeholder:1',Formula('forall',(x,),variable='x')),))
    assert novelty_check(Formula('forall',(y,),variable='y'),t)['status']=='rejected'


def test_novelty_unknown_refuses(monkeypatch):
    import ara.runtime.novelty as novelty
    answers=iter(['SOLVER_TIMEOUT','SOLVER_COUNTEREXAMPLE','SOLVER_COUNTEREXAMPLE'])
    monkeypatch.setattr(novelty,'cached_entails',lambda *args,**kwargs:next(answers))
    assert novelty.novelty_check(R,T)['status']=='unresolved'


def setup(tmp_path):
    goal=Proposition('r','R',R);package=Proposition('pq','P and Q',AND)
    def reply(kind,inputs):
        if kind=='propose_targets':return dict(targets=[package.to_dict(),goal.to_dict()])
        if kind=='classify_target':return dict(novelty='new_assertion',fidelity='matches',classification='own_thesis',reason='R')
        if kind=='map_leaf':return dict(t_id='open')
        if kind=='propose_cuts':
            formula=Formula.from_dict(inputs['goal']['formula'])
            if formula not in (R,AND):return dict(proposals=[])
            scheme,slots=('sign',('sign_relation','observed_sign')) if formula==R else ('conjunction_introduction',('left','right'))
            return dict(proposals=[dict(bank_id=scheme,conclusion_text=inputs['goal']['text'],conclusion_ref='current_goal',
                premises=[dict(slot=s,text=c.text,t_id=c.id,scope_id=None) for s,c in zip(slots,T.commitments)])])
        if kind=='formalise_slots':return dict(slots=[dict(slot=b['slot'],formula=b['formula']) for b in inputs['slot_bindings']])
        if kind=='answer_cq':return dict(cq_id=inputs['question']['id'],answer='P Q',answered=True,supporting_t_ids=['t1','t2'])
        raise AssertionError(kind)
    calls,_=rig(tmp_path,reply)
    from ara.runtime.frozen_catalogue import frozen_artifact
    from ara.runtime.commitment_provenance import make_commitment_provenance
    artifact=frozen_artifact(T,[dict(name=n,kind='atom',arity=0,definition=n,evidence_ids=['t1','t2']) for n in ('P','Q')])
    (tmp_path/'frozen-t.json').write_text(canonical(artifact))
    provenance=make_commitment_provenance(T,artifact['symbol_catalogue'],{c.id:dict(source_id=source,
        source_authors=[],attributed_to=source,page_start=1,page_end=1,evidence_id=c.id,
        attribution='author_claim',stance='endorsed',source_kind='premise',source_text=c.text,
        omitted_support_ids=[]) for c,source in zip(T.commitments,('a','b'))})
    (tmp_path/'commitment-provenance.json').write_text(canonical(provenance))
    (tmp_path/'commitments.json').write_text(T.to_json())
    bank=load_bank(ROOT/'bank')
    calls.log.record('run_started',config=calls.config,topic='P Q',bank_version=bank.bank_version)
    calls.log.record('symbol_catalogue_frozen',**artifact['symbol_catalogue'])
    calls.log.record('commitment_provenance_frozen',**provenance)
    calls.log.record('commitments_frozen',commitments=T.to_dict(),bank_version=bank.bank_version)
    return calls,bank,goal,package,provenance


def test_native_two_source_thesis_and_structural_route(tmp_path):
    calls,bank,goal,package,provenance=setup(tmp_path)
    assert calls.propose_targets(T,1)==(goal,)
    rejected=[json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='target_pool_candidate']
    assert next(r for r in rejected if r['target']['id']=='pq')['disposition']=='rejected'
    # Historical or explicitly requested packages are still disclosed after native closure.
    routes=search_all(calls,NativeEngine(bank,calls),T,(goal,package))
    positive={r.nodes[0].proposition.formula:r for r in routes if r.status=='CLOSED'}
    substantive,structural=positive[R],positive[AND]
    assert route_contribution(substantive,T,provenance)['classification']=='CLOSED-derived'
    receipt=route_contribution(structural,T,provenance)
    assert receipt['classification']=='CLOSED-structural'
    assert receipt['substantive_inferences']==[]
    assert receipt['support_ids']==['t1','t2']
    assert {provenance['commitments'][tid]['source_id'] for tid in receipt['support_ids']}=={'a','b'}
    assert selectable_routes(routes,T,provenance)==(substantive,)
    root=next(n for n in substantive.nodes if n.id==substantive.root_id)
    assert root.proposal.bank_id=='sign' and all(a.answered for a in root.cq_answers)
    # An unreachable inference cannot make a purely structural route substantive.
    extra=replace(root,id='unreachable')
    assert route_contribution(replace(structural,nodes=structural.nodes+(extra,)),T,provenance)['classification']=='CLOSED-structural'
    from ara.runtime.report import build_run
    report=build_run(tmp_path)
    assert {r['classification'] for r in report['routes']} >= {'CLOSED-derived','CLOSED-structural'}


def test_boolean_feedback_and_bank_guidance_reach_correction(tmp_path):
    attempts=[]
    package=Proposition('pq','P and Q',AND)
    def reply(kind,inputs):
        if kind=='propose_targets':
            attempts.append(inputs)
            assert 'sign' in inputs['substantive_bank_ids']
            assert 'conjunction_introduction' not in inputs['substantive_bank_ids']
            assert set(inputs['structural_bank_ids'])=={b.id for b in load_bank(ROOT/'bank').entries if b.kind=='deductive'}
            assert set(inputs['substantive_bank_ids'])=={b.id for b in load_bank(ROOT/'bank').entries if b.kind=='defeasible'}
            assert inputs['target_policy']['exclude_boolean_recombination']
            if len(attempts)>1:
                rejection=inputs['triviality_feedback']['rejected'][0]
                assert rejection['reason']=='deductive_closure'
                assert 'classically entails' in rejection['explanation']
                assert rejection['novelty']['basis_commitment_ids']==['t1','t2']
            return dict(targets=[package.to_dict()])
        return dict(novelty='new_assertion',fidelity='matches',classification='own_thesis',reason='P Q')
    calls,_=rig(tmp_path,reply)
    from ara.runtime.frozen_catalogue import frozen_artifact
    (tmp_path/'frozen-t.json').write_text(canonical(frozen_artifact(T,
        [dict(name=n,kind='atom',arity=0,definition=n,evidence_ids=['t1','t2']) for n in ('P','Q')])))
    assert calls.propose_targets(T)==()
    assert len(attempts)==3


@pytest.mark.parametrize('scheme',[b.id for b in load_bank(ROOT/'bank').entries if b.kind=='deductive']+['unknown'])
def test_only_known_nonstructural_scheme_counts(scheme):
    from ara.types import RouteGraph
    nodes=(RouteNode('root',Proposition('r','R',R),'inference',
        proposal=Proposal(scheme,(),'R'),children=('p','q')),
        RouteNode('p',Proposition('p','P',P),'leaf',t_id='t1'),
        RouteNode('q',Proposition('q','Q',Q),'leaf',t_id='t2'))
    route=RouteGraph('route','root',nodes,'CLOSED')
    assert route_contribution(route,T)['classification']=='CLOSED-structural'
