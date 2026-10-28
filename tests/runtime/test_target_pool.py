"""Larger target pools and native defeasible reachability on placeholders."""
from dataclasses import replace
import json
import pytest
from ara.bank import load_bank
from ara.formal import entails
from ara.runtime.cache import canonical
from ara.runtime.orchestration import NativeEngine, search_all
from ara.runtime.route_policy import route_contribution
from ara.types import Commitment, CommitmentSet, Formula, Proposition, SymbolDefinition
from test_search_alignment import rig, ROOT, P, Q, R, T
from test_contribution_gate import payloads


def candidate(i):
    # Distinct placeholder formulas, none implied by either P or P -> Q.
    f=Formula('predicate',name='F',terms=())
    for _ in range(i): f=Formula('implies',(R,f))
    return Proposition('p'+str(i),'R -> '*i+'F',f,
        (SymbolDefinition('F','predicate',0,'F'),) + ((SymbolDefinition('R','atom',0,'R'),) if i else ()))


def test_pool_keeps_thirty_in_stable_order(tmp_path):
    pool=[candidate(i) for i in range(30)]
    def reply(kind,inputs):
        if kind=='propose_targets':
            assert inputs['count']==30 and inputs['keep_count']==30
            assert inputs['attempt_budget']==3
            assert any(b['id']=='sign' and b['critical_questions'] for b in inputs['bank'])
            assert inputs['support_examples']
            return dict(targets=[p.to_dict() for p in pool])
        return dict(novelty='new_assertion',fidelity='matches',classification='own_thesis',reason='P')
    calls,_=rig(tmp_path,reply)
    assert calls.propose_targets(T)==tuple(pool)
    events=payloads(calls,'target_pool_candidate')
    assert len(events)==30
    assert [e['disposition'] for e in events]==['kept']*30
    assert [e['target'] for e in events]==[p.to_dict() for p in pool]


def test_two_corrections_preserve_survivors_and_give_witnesses(tmp_path):
    bad=Proposition('bad','R -> P',Formula('implies',(R,P)))
    pools=[[candidate(0),bad],[candidate(0),candidate(1),bad],[candidate(2)]]
    attempts=[]
    def reply(kind,inputs):
        if kind=='propose_targets':
            attempts.append(inputs)
            if len(attempts)>1:
                witness=next(r for r in inputs['triviality_feedback']['rejected'] if r['target_id']=='bad')
                assert witness['entailing_commitment']==T.commitments[0].to_dict()
                assert witness['polarity']=='target'
                assert witness['conditional_consequent_in_t'] is True
                assert 'alone entails' in witness['explanation']
            return dict(targets=[p.to_dict() for p in pools[len(attempts)-1]])
        return dict(novelty='new_assertion',fidelity='matches',classification='own_thesis',reason='P')
    calls,_=rig(tmp_path,reply)
    assert calls.propose_targets(T,3)==tuple(candidate(i) for i in range(3))
    assert len(attempts)==3
    assert any(e['disposition']=='duplicate' for e in payloads(calls,'target_pool_candidate'))
    assert payloads(calls,'target_pool_finished')[0]['attempts']==3


def test_all_invalid_exhausts_three_attempts(tmp_path):
    def reply(kind,inputs):
        if kind=='propose_targets': return dict(targets=[Proposition('p','P',P).to_dict()])
        return dict(novelty='new_assertion',fidelity='matches',classification='own_thesis',reason='P')
    calls,_=rig(tmp_path,reply)
    assert calls.propose_targets(T)==()
    assert len(payloads(calls,'target_triviality_preflight'))==3
    assert payloads(calls,'target_pool_finished')[0]['kept']==[]


@pytest.mark.parametrize('answered',[True,False])
def test_native_new_atom_defeasible_closure(tmp_path,answered):
    t=CommitmentSet((Commitment('t1','P','placeholder:1',P),Commitment('t2','Q','placeholder:2',Q)))
    goal=Proposition('r','R',R)
    def reply(kind,inputs):
        if kind=='propose_targets': return dict(targets=[goal.to_dict()])
        if kind=='classify_target': return dict(novelty='new_assertion',fidelity='matches',classification='own_thesis',reason='R')
        if kind=='map_leaf': return dict(t_id='open')
        if kind=='propose_cuts':
            return dict(proposals=[dict(bank_id='sign',conclusion_text='R',conclusion_ref='current_goal',
                premises=[dict(slot=s,text=c.text,t_id=c.id,scope_id=None)
                          for s,c in zip(('sign_relation','observed_sign'),t.commitments)])]
                if inputs['goal']['formula']==R.to_dict() else [])
        if kind=='formalise_slots': return dict(slots=[dict(slot=b['slot'],formula=b['formula']) for b in inputs['slot_bindings']])
        if kind=='answer_cq': return dict(cq_id=inputs['question']['id'],answer='P Q',answered=answered,supporting_t_ids=['t1','t2'])
        raise AssertionError(kind)
    calls,_=rig(tmp_path,reply)
    from test_cross_paper import frozen_metadata
    artifact,provenance=frozen_metadata(t,('a','b'))
    (tmp_path/'frozen-t.json').write_text(canonical(artifact))
    (tmp_path/'commitment-provenance.json').write_text(canonical(provenance))
    # Establish no classical entailment, even from the complete support pair.
    assert entails((P,Q),R,1000)=='SOLVER_COUNTEREXAMPLE'
    targets=calls.propose_targets(t,1)
    assert targets==(goal,)
    bank=load_bank(ROOT/'bank')
    routes=search_all(calls,NativeEngine(bank,calls),t,targets)
    route=next(r for r in routes if r.nodes[0].proposition.formula==R)
    assert route.status==('CLOSED' if answered else 'OPEN')
    receipt=route_contribution(route,t,provenance)
    assert receipt['classification']==('CLOSED-derived' if answered else 'OPEN')
    if answered: assert receipt['support_ids']==['t1','t2']
    root=next(n for n in route.nodes if n.id==route.root_id)
    assert root.proposal.bank_id=='sign'
    assert {a.cq_id for a in root.cq_answers}=={q.id for q in bank.get('sign').critical_questions}
    assert all(a.answered==answered and a.supporting_t_ids==('t1','t2') for a in root.cq_answers)
    assert any(e['decision'] and e['decision']['reason_code']=='BANK_LICENSED' for e in calls.log.read())
