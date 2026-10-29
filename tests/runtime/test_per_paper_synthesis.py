"""Cross-paper deductive novelty through frozen proposal, search and reporting."""
import json
from dataclasses import replace
import pytest
from ara.bank import load_bank
from ara.runtime.cache import canonical
from ara.runtime.novelty import novelty_check
from ara.runtime.orchestration import NativeEngine, search_all
from ara.runtime.route_policy import route_contribution, selectable_routes
from ara.types import Commitment, CommitmentSet, Formula, Proposition
from test_search_alignment import rig,ROOT,P,Q,R,T,PQ,GOAL,cut
from test_cross_paper import frozen_metadata


def freeze(calls,t,papers,stances=None):
    from ara.runtime.commitment_provenance import make_commitment_provenance
    artifact,provenance=frozen_metadata(t,papers)
    for tid,stance in (stances or {}).items():
        provenance['commitments'][tid].update(stance=stance,attribution={'attacked':'attacked_view','reported':'reported_view'}[stance])
    provenance=make_commitment_provenance(t,artifact['symbol_catalogue'],provenance['commitments'])
    for name,value in [('commitments.json',t.to_dict()),('frozen-t.json',artifact),('commitment-provenance.json',provenance)]:
        (calls.log.path.parent/name).write_text(canonical(value))
    calls.log.record('symbol_catalogue_frozen',**artifact['symbol_catalogue'])
    calls.log.record('commitment_provenance_frozen',**provenance)
    calls.log.record('commitments_frozen',commitments=t.to_dict(),bank_version='1.0.0')
    return provenance


@pytest.mark.parametrize('papers,expected',[(('a','b'),'CLOSED-derived'),(('a','a'),'CLOSED-single-paper')])
def test_native_deductive_synthesis_proposal_selection_and_report(tmp_path,papers,expected):
    from ara.runtime.report import build_run
    requests=[]
    def reply(kind,data):
        requests.append((kind,data))
        if kind=='classify_conflict': return dict(classification='compatible',reason='P Q')
        if kind=='propose_targets': return dict(targets=[GOAL.to_dict()])
        if kind=='classify_target': return dict(classification='own_thesis',novelty='new_assertion',fidelity='matches',reason='Q')
        if kind=='map_leaf': return dict(t_id=next((c['id'] for c in data['commitments']['commitments'] if c['formula']==data['leaf']['formula']),'open'))
        if kind=='propose_cuts': return dict(proposals=[cut()] if data['goal']['formula']==Q.to_dict() else [])
        if kind=='formalise_slots': return dict(slots=[dict(slot=b['slot'],formula=b['formula']) for b in data['slot_bindings']])
        raise AssertionError(kind)
    calls,_=rig(tmp_path,reply)
    calls.config.update(node_cap=30,forward_candidate_node_cap=30)
    provenance=freeze(calls,T,papers)
    targets=calls.propose_targets(T,1)
    assert targets==((GOAL,) if expected=='CLOSED-derived' else ())
    proposed=next(d for k,d in requests if k=='propose_targets')
    assert bool(proposed['forward_candidates'])==(expected=='CLOSED-derived')
    if expected=='CLOSED-derived':
        assert proposed['forward_candidates'][0]['formula']==Q.to_dict()
        assert proposed['target_policy']['novelty_basis']=='per_paper_endorsed_closure'
    routes=search_all(calls,NativeEngine(load_bank(ROOT/'bank'),calls),T,(GOAL,))
    closed=next(r for r in routes if r.status=='CLOSED')
    receipt=route_contribution(closed,T,provenance)
    assert receipt['classification']==expected
    assert bool(selectable_routes(routes,T,provenance))==(expected=='CLOSED-derived')
    report=build_run(tmp_path)
    assert next(r for r in report['routes'] if r['graph']['id']==closed.id)['classification']==expected
    assert receipt['per_paper_novelty']['status']==('candidate' if expected=='CLOSED-derived' else 'rejected')


def test_per_paper_closure_groups_and_padding():
    _,cross=frozen_metadata(T,('a','b'))
    _,single=frozen_metadata(T,('a','a'))
    assert novelty_check(Q,T,cross)['status']=='candidate'
    assert novelty_check(Q,T,single)['reason']=='single_paper_closure'
    for formula in (Formula('implies',(R,Q)),Formula('or',(Q,Formula('and',(R,R.negated()))))):
        assert novelty_check(formula,T,single)['reason']=='single_paper_closure'
    tautology=Formula('or',(R,R.negated()))
    assert novelty_check(tautology,T,cross)['reason']=='valid_without_support'
    atoms=CommitmentSet((Commitment('p','P','a:1',P),Commitment('q','Q','b:1',Q)))
    _,metadata=frozen_metadata(atoms,('a','b'))
    assert novelty_check(Formula('and',(P,Q)),atoms,metadata)['reason']=='no_essential_new_proposition'
    assert novelty_check(R,atoms,metadata)['status']=='candidate'
    extra=CommitmentSet(T.commitments+(Commitment('r','R','b:1',R),))
    _,metadata=frozen_metadata(extra,('a','a','b'))
    assert novelty_check(Q,extra,metadata)['reason']=='single_paper_closure'
    # Separate consequences of compound premises still only package known atoms.
    s=Formula('atom',name='S')
    compounds=CommitmentSet((Commitment('pr','P and R','a:1',Formula('and',(P,R))),
        Commitment('qs','Q and S','b:1',Formula('and',(Q,s)))))
    _,metadata=frozen_metadata(compounds,('a','b'))
    assert novelty_check(Formula('and',(P,Q)),compounds,metadata)['reason']=='no_essential_new_proposition'


def test_per_paper_unknown_is_not_novel(monkeypatch):
    import ara.runtime.novelty as module
    _,metadata=frozen_metadata(T,('a','b'))
    original=module.cached_entails
    remaining=[True]
    def first_paper_timeout(premises,goal,timeout):
        if premises and remaining:
            remaining.pop()
            return 'SOLVER_TIMEOUT'
        return original(premises,goal,timeout)
    monkeypatch.setattr(module,'cached_entails',first_paper_timeout)
    assert novelty_check(Q,T,metadata)['status']=='unresolved'


def test_forward_uses_native_licenses_and_endorsed_dependencies(tmp_path):
    from ara.runtime.synthesis import forward_candidates
    calls,_=rig(tmp_path,lambda *args:pytest.fail('forward mining dispatched a model call'))
    provenance=freeze(calls,T,('a','b'))
    result=forward_candidates(T,provenance,load_bank(ROOT/'bank'),calls.log,depth=2,node_cap=30)
    q=next(c for c in result['candidates'] if c['formula']==Q.to_dict())
    assert q['support_ids']==['t1','t2'] and q['paper_ids']==['a','b']
    assert 'modus_ponens' in q['bank_ids']
    assert result['licensed_consequences']>0
    provenance['commitments']['t2']['stance']='reported'
    assert not forward_candidates(T,provenance,load_bank(ROOT/'bank'),calls.log,depth=2,node_cap=30)['candidates']
    assert not forward_candidates(T,None,load_bank(ROOT/'bank'),calls.log,depth=2,node_cap=30)['candidates']


def test_reported_opposition_does_not_remove_forward_synthesis(tmp_path):
    from ara.runtime.synthesis import forward_candidates
    calls,_=rig(tmp_path,lambda *args:pytest.fail('model dispatch'))
    t=CommitmentSet(T.commitments+(Commitment('r','not Q','c:1',Q.negated()),))
    provenance=freeze(calls,t,('a','b','c'),{'r':'reported'})
    assert novelty_check(Q,t,provenance)['status']=='candidate'
    result=forward_candidates(t,provenance,load_bank(ROOT/'bank'),calls.log,depth=2,node_cap=30)
    assert any(c['formula']==Q.to_dict() for c in result['candidates'])


def test_unlicensed_or_unreachable_step_cannot_supply_synthesis():
    from ara.types import RouteGraph,RouteNode,Proposal,PremiseFill
    _,provenance=frozen_metadata(T,('a','b'))
    leaves=tuple(RouteNode(c.id,Proposition(c.id,c.text,c.formula),'leaf',c.id) for c in T.commitments)
    invalid=RouteNode('root',GOAL,'inference',proposal=Proposal('unknown',(),'Q'),children=('t1','t2'))
    valid=RouteNode('elsewhere',GOAL,'inference',proposal=Proposal('modus_ponens',(
        PremiseFill('conditional','P -> Q','t2'),PremiseFill('antecedent','P','t1')),'Q'),children=('t2','t1'))
    graph=RouteGraph('invalid','root',(invalid,valid)+leaves,'CLOSED')
    assert route_contribution(graph,T,provenance)['classification']!='CLOSED-derived'
    invalid=replace(invalid,proposal=replace(valid.proposal,bank_id='conjunction_elimination'))
    assert route_contribution(replace(graph,nodes=(invalid,valid)+leaves),T,provenance)['classification']!='CLOSED-derived'


def test_conditional_premise_package_is_not_a_synthesis():
    _,provenance=frozen_metadata(T,('a','b'))
    assert novelty_check(Formula('and',(P,PQ)),T,provenance)['status']=='rejected'


def test_mixed_native_inference_and_recorded_forward_candidates(tmp_path):
    s=Formula('atom',name='S')
    rs=Formula('implies',(R,s))
    t=CommitmentSet((Commitment('p','P','a:1',P),Commitment('q','Q','b:1',Q),Commitment('rs','R -> S','b:2',rs)))
    seen=[]
    def reply(kind,d):
        if kind=='classify_conflict':return dict(classification='compatible',reason='P Q')
        if kind=='propose_targets':
            seen.append(d)
            return dict(targets=[Proposition('r','R',R).to_dict()])
        if kind=='classify_target':return dict(classification='own_thesis',novelty='new_assertion',fidelity='matches',reason='R')
        if kind=='map_leaf':return dict(t_id=next((c['id'] for c in d['commitments']['commitments'] if c['formula']==d['leaf']['formula']),'open'))
        if kind=='propose_cuts':
            f=Formula.from_dict(d['goal']['formula'])
            if f==s:
                bank,ps='modus_ponens',[('conditional','R -> S','rs'),('antecedent','R','open')]
            elif f==R:
                bank,ps='sign',[('sign_relation','P','p'),('observed_sign','Q','q')]
            else:return dict(proposals=[])
            return dict(proposals=[dict(bank_id=bank,conclusion_text=d['goal']['text'],conclusion_ref='current_goal',
                premises=[dict(slot=slot,text=text,t_id=tid,scope_id=None) for slot,text,tid in ps])])
        if kind=='formalise_slots':return dict(slots=[dict(slot=b['slot'],formula=b['formula'] or R.to_dict()) for b in d['slot_bindings']])
        if kind=='answer_cq':return dict(cq_id=d['question']['id'],answered=True,answer='P Q',supporting_t_ids=['p','q'])
        raise AssertionError(kind)
    calls,_=rig(tmp_path,reply)
    calls.config.update(node_cap=30,forward_candidate_node_cap=30,forward_pass_depth=2)
    provenance=freeze(calls,t,('a','b','b'))
    routes=search_all(calls,NativeEngine(load_bank(ROOT/'bank'),calls),t,(Proposition('s','S',s),))
    closed=next(r for r in routes if r.status=='CLOSED')
    assert route_contribution(closed,t,provenance)['classification']=='CLOSED-derived'
    targets=calls.propose_targets(t,1)
    assert targets and targets[0].formula==R
    assert any(c['formula']==R.to_dict() and c['origin']=='recorded_forward' for c in seen[0]['forward_candidates'])
    from ara.runtime.synthesis import recorded_forward
    assert recorded_forward(calls.log.read(),CommitmentSet(t.commitments[:2]))==()
    calls.log.record('analysis_started',target=Proposition('new','S',s).to_dict())
    calls.propose_targets(t,1)
    assert not any(c['origin']=='recorded_forward' for c in seen[-1]['forward_candidates'])


def test_quantified_cross_paper_closure():
    from ara.types import Term
    x,a=Term('variable','x'),Term('constant','a')
    pred=lambda n,t:Formula('predicate',name=n,terms=(t,))
    t=CommitmentSet((Commitment('a','F(a)','a:1',pred('F',a)),
        Commitment('b','F(x) -> Q(x)','b:1',Formula('forall',(Formula('implies',(pred('F',x),pred('Q',x))),),variable='x'))))
    _,provenance=frozen_metadata(t,('a','b'))
    assert novelty_check(pred('Q',a),t,provenance)['status']=='candidate'
    _,provenance=frozen_metadata(t,('a','a'))
    assert novelty_check(pred('Q',a),t,provenance)['reason']=='single_paper_closure'


def test_alignment_forward_uses_bridges_without_paper_ownership(tmp_path):
    from ara.runtime.synthesis import forward_candidates
    from ara.runtime.logging import EventLog
    from ara.runtime.novelty import endorsed_papers
    from ara.runtime.semantic_conflicts import rank_pairs
    from ara.runtime.symbol_alignment import apply_judgments
    t=CommitmentSet((Commitment('a','P','a:1',P),Commitment('b','Q -> R','b:1',Formula('implies',(Q,R)))))
    artifact,meta=frozen_metadata(t,('a','b'),{'P':'P Q','Q':'P Q'})
    aligned,symbols,rows,_=apply_judgments(t,artifact['symbol_catalogue']['symbols'],meta['commitments'],
        [dict(left='P',right='Q',relation='entails_left_right',reason='P Q')])
    # The complete v2 persistence path is covered by the native freeze tests.
    provenance={**meta,'commitments':rows}
    bridge=aligned.commitments[-1]
    assert endorsed_papers(aligned,provenance)==endorsed_papers(t,meta)
    assert novelty_check(R,aligned,provenance)['status']=='candidate'
    assert all(bridge.id not in c['commitment_ids'] for c in rank_pairs(aligned,symbols,provenance,60)['pairs'])
    result=forward_candidates(aligned,provenance,load_bank(ROOT/'bank'),EventLog(tmp_path/'events.jsonl'),depth=2,node_cap=500)
    candidate=next(c for c in result['candidates'] if c['formula']==R.to_dict())
    assert candidate['paper_ids']==['a','b'] and candidate['support_ids']==sorted(['a','b',bridge.id])
    assert candidate['alignment_support_ids']==[bridge.id]
    assert candidate['endorsed_support_ids']==['a','b']
    assert not any(c['formula']==Q.to_dict() for c in result['candidates'])
    # An alignment premise is not a paper even if its payload falsely supplies one.
    rows[bridge.id]['source_id']='c'
    assert set(endorsed_papers(aligned,provenance))=={'a','b'}
