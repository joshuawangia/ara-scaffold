import json
from pathlib import Path
from dataclasses import replace
import pytest
from ara.types import Formula,Commitment,CommitmentSet,Proposition
from ara.runtime.novelty import novelty_check
from ara.runtime.route_policy import route_contribution,selectable_routes
from ara.runtime.orchestration import NativeEngine,prepare_commitments
from test_hypothesis_premises import P,Q,R,configured
from test_cross_paper import frozen_metadata
from test_search_alignment import rig,ROOT
from ara.bank import load_bank

S=Formula('atom',name='S')
AND=lambda a,b:Formula('and',(a,b))
BASE=CommitmentSet((Commitment('p','P','a:1',P),Commitment('qs','Q and S','b:1',AND(Q,S))))
GOAL=AND(R,AND(P,Q))

@pytest.mark.parametrize('h',[R,AND(R,S),Formula('forall',(R,),variable='x'),Formula('implies',(P,R))],ids=['atomic_h','compound_h','quantified_h','single_paper_plus_h'])
def test_h_restatement_padding_native(tmp_path,monkeypatch,h):
    catalogue,meta=frozen_metadata(BASE,('a','b'))
    formulas={'H':h,'R':R,'P':P,'Q':Q,'Q and S':AND(Q,S),'P and Q':AND(P,Q),'R and (P and Q)':GOAL}
    def reply(kind,data):
        if kind=='map_leaf':return dict(t_id=next((c['id'] for c in data['commitments']['commitments'] if c['formula']==data['leaf']['formula']),'open'))
        if kind=='propose_cuts':
            f=data['goal']['formula']
            if f==GOAL.to_dict():bank,slots='conjunction_introduction',[('left','R','open'),('right','P and Q','open')]
            elif f==AND(P,Q).to_dict():bank,slots='conjunction_introduction',[('left','P','p'),('right','Q','open')]
            elif f==R.to_dict() and h==AND(R,S):bank,slots='conjunction_elimination',[('conjunction','H','hypothesis:h')]
            elif f==R.to_dict() and h.op=='forall':bank,slots='universal_instantiation',[('universal','H','hypothesis:h')]
            elif f==R.to_dict() and h.op=='implies':bank,slots='modus_ponens',[('conditional','H','hypothesis:h'),('antecedent','P','p')]
            elif f==Q.to_dict():bank,slots='conjunction_elimination',[('conjunction','Q and S','qs')]
            else:return dict(proposals=[])
            return dict(proposals=[dict(bank_id=bank,conclusion_text=data['goal']['text'],conclusion_ref='current_goal',premises=[dict(slot=s,text=entry['text'] if i=='hypothesis:h' else t,t_id=i,scope_id=None) for s,t,i in slots])])
        if kind=='formalise_slots':return dict(slots=[dict(slot=b['slot'],formula=b['formula'] or formulas[b['text']].to_dict()) for b in data['slot_bindings']])
        pytest.fail(kind)
    calls,_=rig(tmp_path,reply);(tmp_path/'frozen-t.json').unlink()
    entry=configured(h);entry['text']='R' if h==R else 'R and S' if h==AND(R,S) else 'For all x R' if h.op=='forall' else 'P implies R'
    calls.config.update(hypothesis_premises=[entry],construction_alignment_candidates=0,node_cap=80,forward_pass_depth=0,semantic_conflict_pair_limit=0)
    calls.log.record('build_t_merged',commitments=BASE.to_dict(),symbols=catalogue['symbol_catalogue']['symbols'],provenance=meta['commitments'])
    monkeypatch.setattr(calls,'build_t',lambda *_:BASE)
    bank=load_bank(ROOT/'bank');t=prepare_commitments(calls,bank,'P','P')
    provenance=calls.search_vocabulary(t)['commitment_provenance']
    novelty=novelty_check(GOAL,t,provenance,support_ids=['p','qs','hypothesis:h'])
    from ara.runtime.target_policy import trivial_targets
    preflight=trivial_targets((Proposition('r','R and (P and Q)',GOAL),),t,calls.search_vocabulary(t)['symbol_catalogue'],provenance=provenance)
    result=NativeEngine(bank,calls)._engine(t).search(Proposition('r','R and (P and Q)',GOAL))
    rows=[dict(route=r.to_dict(),receipt=route_contribution(r,t,provenance)) for r in result.routes]
    closed=next(r for r in result.routes if r.status=='CLOSED')
    from ara.engine.forward import forward_pass
    from ara.engine.licensing import Licenser
    from ara.runtime.synthesis import forward_candidates
    witnessed=forward_pass(tuple(c.formula for c in t.commitments),t,Licenser(bank,None,calls.log),
                           4,100,witnesses=(closed,))
    mined=forward_candidates(t,provenance,bank,calls.log,depth=4,node_cap=100,observed=(witnessed,))
    assert novelty['status']=='rejected'
    assert preflight
    assert all(row['receipt']['classification']!='CLOSED-derived' for row in rows)
    assert not selectable_routes(result.routes,t,provenance)
    assert not any(Formula.from_dict(c['formula']).canonical()==GOAL.canonical() for c in mined['candidates'])
