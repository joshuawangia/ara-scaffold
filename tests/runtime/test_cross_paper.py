"""Cross-paper admission and catalogue bridges, using only placeholder content."""
from dataclasses import replace
import json
import pytest

from ara.runtime.cache import canonical
from ara.runtime.commitment_provenance import make_commitment_provenance
from ara.runtime.frozen_catalogue import frozen_artifact
from ara.runtime.orchestration import NativeEngine, search_all
from ara.runtime.route_policy import route_contribution, selectable_routes
from ara.types import Commitment, CommitmentSet, Formula
from test_novelty_policy import setup, T, P, Q, R


def frozen_metadata(t, papers, definitions=None):
    from ara.runtime.search_alignment import symbols
    used = sorted(set(s for c in t.commitments for s in symbols(c.formula)))
    artifact = frozen_artifact(t, [dict(name=n, kind=k, arity=a,
        definition=(definitions or {}).get(n, n), evidence_ids=[c.id for c in t.commitments
            if (n,k,a) in set(symbols(c.formula))]) for n,k,a in used])
    provenance = make_commitment_provenance(t, artifact['symbol_catalogue'], {
        c.id: dict(source_id=paper, source_authors=[], attributed_to=paper,
            page_start=1, page_end=1, evidence_id=c.id, attribution='author_claim',
            stance='endorsed', source_kind='premise', source_text=c.text, omitted_support_ids=[])
        for c,paper in zip(t.commitments,papers)})
    return artifact, provenance


@pytest.mark.parametrize('papers,expected', [
    (('a','b'),'CLOSED-derived'), (('a','a'),'CLOSED-single-paper')])
def test_native_cross_paper_selection_and_report(tmp_path, papers, expected):
    from ara.runtime.cli import main
    source = tmp_path/'source'
    calls, bank, goal, _, provenance = setup(source, papers)
    routes = search_all(calls, NativeEngine(bank,calls), T, (goal,))
    closed = next(r for r in routes if r.status == 'CLOSED')
    receipt = route_contribution(closed,T,provenance)
    assert receipt['classification'] == expected
    assert receipt['paper_support']['paper_ids'] == sorted(set(papers))
    assert receipt['paper_support']['minimum_papers'] == 2
    assert bool(selectable_routes(routes,T,provenance)) == (len(set(papers)) == 2)
    output = tmp_path/'report'
    assert main(['report','--run-dir',str(source),'--out',str(output)]) == 0
    summary = json.loads((output/'data.json').read_text())['runs'][0]
    row = next(r for r in summary['routes'] if r['route_id'] == closed.id)
    assert row['classification'] == expected
    assert row['selectable_by_default'] == (len(set(papers)) == 2)
    assert json.loads((output/row['file']).read_text())['contribution']['paper_support'] == receipt['paper_support']
    assert expected in (output/'report.html').read_text()


def test_unknown_paper_identity_and_unreachable_support_do_not_upgrade(tmp_path):
    calls, bank, goal, _, provenance = setup(tmp_path, ('a','a'))
    route = NativeEngine(bank,calls)._engine(T).search(goal).routes[0]
    assert route_contribution(route,T)['classification'] == 'CLOSED-contribution-unresolved'
    assert route_contribution(route,T)['paper_support']['status'] == 'unavailable_legacy'
    extra = Commitment('t3','S','another:1',Formula('atom',name='S'))
    t = CommitmentSet(T.commitments+(extra,))
    _, metadata = frozen_metadata(t,('a','a','b'))
    from ara.types import RouteNode, Proposition
    unreachable = RouteNode('unreachable',Proposition('s','S',extra.formula),'leaf','t3')
    receipt = route_contribution(replace(route,nodes=route.nodes+(unreachable,)),t,metadata)
    assert receipt['classification'] == 'CLOSED-single-paper'
    assert receipt['paper_support']['paper_ids'] == ['a']


@pytest.mark.parametrize('shared', ['symbol','definition_term'])
def test_bridges_are_deterministic_cross_paper_pairs_and_triples(shared):
    from ara.runtime.bridges import bridge_context
    s = Formula('atom',name='S')
    formulas = (P,Formula('and',(P,Q)),Formula('and',(P,s)),R) if shared=='symbol' else (P,Q,s,R)
    t = CommitmentSet(tuple(Commitment('t'+str(i),f.canonical(),'placeholder:'+str(i),f)
        for i,f in enumerate(formulas)))
    artifact, provenance = frozen_metadata(t,('a','b','c','d'),dict(P='P',Q='P',S='P',R='R'))
    catalogue = artifact['symbol_catalogue']['symbols']
    context = bridge_context(t,catalogue,provenance)
    bridges = context['candidate_bridges']
    assert any(b['commitment_ids']==['t0','t1'] for b in bridges)
    assert any(b['commitment_ids']==['t0','t1','t2'] for b in bridges)
    assert all('t3' not in b['commitment_ids'] and len(b['paper_ids'])>=2 for b in bridges)
    assert all(any(link['kind']==shared for link in b['connections']) for b in bridges)
    assert context == bridge_context(CommitmentSet(tuple(reversed(t.commitments))),list(reversed(catalogue)),provenance)
    assert bridge_context(t,None,None)['candidate_bridges'] == []
    assert bridge_context(t,catalogue,None)['candidate_bridges'] == []
    _, same = frozen_metadata(t,('a','a','a','a'),dict(P='P',Q='P',S='P',R='R'))
    assert bridge_context(t,catalogue,same)['candidate_bridges'] == []


def test_bridge_bounds_and_restricted_stances():
    from ara.runtime.bridges import bridge_context, proposal_bridge
    from ara.types import Proposal, PremiseFill
    t = CommitmentSet(tuple(Commitment('t'+str(i),'P','placeholder:'+str(i),P) for i in range(40)))
    artifact, provenance = frozen_metadata(t,tuple('a' if i%2 else 'b' for i in range(40)))
    context = bridge_context(t,artifact['symbol_catalogue']['symbols'],provenance)
    assert len(context['candidate_bridges']) == 60 and context['bridges_truncated']
    assert sum(len(b['commitment_ids'])==2 for b in context['candidate_bridges']) == 30
    rows = {tid:{**row,'stance':'reported','attribution':'reported_view'} for tid,row in provenance['commitments'].items()}
    restricted = make_commitment_provenance(t,artifact['symbol_catalogue'],rows)
    assert bridge_context(t,artifact['symbol_catalogue']['symbols'],restricted)['candidate_bridges'] == []
    proposal = Proposal('sign',(PremiseFill('sign_relation','P','t0','conditional'),
        PremiseFill('observed_sign','P','t1')),'R')
    receipt = proposal_bridge(proposal,context)
    assert receipt['bridge_ids'] == [] and receipt['paper_ids'] == ['a']


def test_bridge_guidance_reaches_target_and_cut_with_slot_paper_receipt(tmp_path):
    calls, bank, goal, _, _ = setup(tmp_path)
    # Separate atoms have overlapping catalogue definition terms, not a logical relation.
    artifact, provenance = frozen_metadata(T,('a','b'),dict(P='P',Q='P Q'))
    (tmp_path/'frozen-t.json').write_text(canonical(artifact))
    (tmp_path/'commitment-provenance.json').write_text(canonical(provenance))
    # Use a fresh log matching the exact replacement freeze.
    from ara.runtime.logging import EventLog
    calls.log = EventLog(tmp_path/'bridge-events.jsonl')
    original = calls.provider.complete
    seen = []
    def complete(kind,prompt,*args):
        if kind in ('propose_targets','propose_cuts','map_leaf'):
            inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1]); seen.append((kind,inputs))
            assert inputs['candidate_bridges']
            assert inputs['commitment_papers'] == {'t1':'a','t2':'b'}
            if kind=='propose_targets':
                assert inputs['count']==30 and inputs['target_policy']['minimum_support_papers']==2
        return original(kind,prompt,*args)
    calls.provider.complete = complete
    assert calls.propose_targets(T,1)==(goal,)
    route=NativeEngine(bank,calls)._engine(T).search(goal).routes[0]
    assert route_contribution(route,T,provenance)['classification']=='CLOSED-derived'
    assert {k for k,_ in seen}=={'propose_targets','map_leaf','propose_cuts'}
    receipts=[json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='proposal_bridge']
    assert receipts[0]['bridge_ids']
    assert receipts[0]['paper_slots']==[
        dict(slot='sign_relation',commitment_id='t1',paper_id='a'),
        dict(slot='observed_sign',commitment_id='t2',paper_id='b')]


def alias_route(directory, cq_ids, formulas=(P,Q,P), papers=('a','a','b')):
    from ara.bank import load_bank
    from ara.types import Proposition
    from test_search_alignment import rig, ROOT
    t = CommitmentSet(tuple(Commitment('t'+str(i+1),f.name,paper+':1',f)
        for i,(f,paper) in enumerate(zip(formulas,papers))))
    artifact, provenance = frozen_metadata(t,papers)
    goal = Proposition('r','R',R)
    def reply(kind, inputs):
        if kind=='classify_conflict': return dict(classification='compatible',reason='P Q')
        if kind=='propose_targets': return dict(targets=[goal.to_dict()])
        if kind=='classify_target': return dict(classification='own_thesis',novelty='new_assertion',fidelity='matches',reason='R')
        if kind=='map_leaf': return dict(t_id='open')
        if kind=='propose_cuts':
            return dict(proposals=[dict(bank_id='sign',conclusion_text='R',conclusion_ref='current_goal',
                premises=[dict(slot=s,text=c.text,t_id=c.id,scope_id=None)
                    for s,c in zip(('sign_relation','observed_sign'),t.commitments[:2])])]
                if inputs['goal']['formula']==R.to_dict() else [])
        if kind=='formalise_slots': return dict(slots=[dict(slot=b['slot'],formula=b['formula']) for b in inputs['slot_bindings']])
        if kind=='answer_cq': return dict(cq_id=inputs['question']['id'],answer='P Q',answered=True,supporting_t_ids=list(cq_ids))
        raise AssertionError(kind)
    calls,_ = rig(directory,reply)
    calls.config['forward_pass_depth'] = 0
    (directory/'frozen-t.json').write_text(canonical(artifact))
    (directory/'commitment-provenance.json').write_text(canonical(provenance))
    calls.log.record('run_started',config=calls.config,topic='P Q')
    calls.log.record('symbol_catalogue_frozen',**artifact['symbol_catalogue'])
    calls.log.record('commitment_provenance_frozen',**provenance)
    calls.log.record('commitments_frozen',commitments=t.to_dict())
    assert calls.propose_targets(t,1)==(goal,)
    routes=search_all(calls,NativeEngine(load_bank(ROOT/'bank'),calls),t,(goal,))
    route=next(r for r in routes if r.status=='CLOSED')
    return route,t,provenance


def test_reversed_cq_order_preserves_all_formula_paper_provenance(tmp_path):
    from ara.runtime.report import build_run
    from ara.runtime.contribution import formula_hash
    receipts, graphs = [], []
    for name,ids in [('forward',('t1','t2','t3')),('reverse',('t3','t2','t1'))]:
        directory=tmp_path/name
        route,t,provenance=alias_route(directory,ids)
        receipt=route_contribution(route,t,provenance)
        assert receipt['classification']=='CLOSED-derived'
        assert selectable_routes((route,),t,provenance)==(route,)
        assert receipt['support_ids']==['t1','t2','t3']
        papers=receipt['paper_support']
        assert papers['commitment_papers']=={'t1':'a','t2':'a','t3':'b'}
        groups={g['formula_hash']:g['commitment_papers'] for g in papers['formula_supports']}
        assert groups=={formula_hash(P):{'t1':'a','t3':'b'},formula_hash(Q):{'t2':'a'}}
        assert len(papers['matching'])==2
        assert {m['paper_id'] for m in papers['matching']}=={'a','b'}
        assert len({m['formula_hash'] for m in papers['matching']})==2
        assert next(r for r in build_run(directory)['routes'] if r['graph']['id']==route.id)['contribution']==receipt
        receipts.append(receipt)
        graph=route.to_dict()
        for node in graph['nodes']:
            for answer in node['cq_answers']:
                answer['supporting_t_ids'].sort()
        graphs.append(graph)
    assert receipts[0]==receipts[1]
    assert graphs[0]==graphs[1]


@pytest.mark.parametrize('formulas,papers,expected,matched', [
    ((P,Q,P),('a','a','b'),'CLOSED-derived',True),
    ((P,Q,P),('a','a','a'),'CLOSED-single-paper',False),
    ((P,P,P),('a','a','b'),'CLOSED-single-support',False),
])
def test_distinct_formula_paper_matching(tmp_path,formulas,papers,expected,matched):
    route,t,provenance=alias_route(tmp_path,('t1','t2','t3'),formulas,papers)
    receipt=route_contribution(route,t,provenance)
    assert receipt['classification']==expected
    assert bool(selectable_routes((route,),t,provenance))==matched
    assert receipt['paper_support']['cross_paper_supported']==matched
    assert len(receipt['paper_support']['matching'])==(2 if matched else 0)
