"""Deterministic gap discovery and persisted resolution obligations."""
from dataclasses import replace
from ara.types import Commitment, CommitmentSet, Formula, Proposition
from ara.runtime.cache import canonical
from test_cross_paper import frozen_metadata
from test_search_alignment import P,Q,R,rig


def test_gap_kinds_and_stance_are_deterministic():
    from ara.runtime.gaps import detect_gaps
    t=CommitmentSet((Commitment('a','P','a:1',P),Commitment('b','not P','b:1',P.negated()),
        Commitment('c','Q','c:1',Q),Commitment('d','Q','d:1',Q),Commitment('e','R','e:1',R)))
    artifact,provenance=frozen_metadata(t,('a','b','c','d','e'),{'R':'R is unresolved'})
    provenance['commitments']['d']['stance']='attacked'
    result=detect_gaps(t,artifact['symbol_catalogue']['symbols'],provenance)
    assert {g.kind for g in result['gaps']}=={'contradiction','stance_conflict','open_problem'}
    assert next(g for g in result['gaps'] if g.kind=='contradiction').commitment_ids==('a','b')
    assert next(g for g in result['gaps'] if g.kind=='stance_conflict').commitment_ids==('c','d')
    assert next(g for g in result['gaps'] if g.kind=='open_problem').commitment_ids==('e',)
    assert result==detect_gaps(CommitmentSet(tuple(reversed(t.commitments))),artifact['symbol_catalogue']['symbols'],provenance)
    assert detect_gaps(t,None,None)['gaps']==()


def test_gap_set_witness_and_same_paper_negative():
    from ara.runtime.gaps import detect_gaps
    t=CommitmentSet((Commitment('a','P','a:1',P),Commitment('b','P -> Q','a:2',Formula('implies',(P,Q))),
                     Commitment('c','not Q','b:1',Q.negated())))
    artifact,provenance=frozen_metadata(t,('a','a','b'))
    gaps=detect_gaps(t,artifact['symbol_catalogue']['symbols'],provenance)['gaps']
    assert len(gaps)==1 and gaps[0].commitment_ids==('a','b','c')
    for row in provenance['commitments'].values(): row['source_id']='a'
    assert detect_gaps(t,artifact['symbol_catalogue']['symbols'],provenance)['gaps']==()


def test_gap_targets_first_persist_and_require_both_sides(tmp_path):
    from ara.runtime.gaps import detect_gaps
    from ara.runtime.route_policy import route_contribution
    from ara.types import RouteGraph, RouteNode, Proposal, PremiseFill, CQAnswer
    t=CommitmentSet((Commitment('a','P','a:1',P),Commitment('b','Q','b:1',Q)))
    artifact,provenance=frozen_metadata(t,('a','b'),{'P':'P remains an open problem'})
    seen=[]
    def reply(kind,d):
        if kind=='propose_targets':
            seen.append(d)
            return dict(targets=[Proposition('r' if d.get('resolution_gap') else 's',
                'R' if d.get('resolution_gap') else 'S',R if d.get('resolution_gap') else Formula('atom',name='S')).to_dict()])
        if kind=='map_leaf':
            return dict(t_id=next((c.id for c in t.commitments if c.formula.to_dict()==d['leaf']['formula']),'open'))
        if kind=='propose_cuts':
            return dict(proposals=[dict(bank_id='sign',conclusion_text='R',conclusion_ref='current_goal',
                premises=[dict(slot=slot,text=c.text,t_id=c.id,scope_id=None)
                          for slot,c in zip(('sign_relation','observed_sign'),t.commitments)])])
        if kind=='formalise_slots': return dict(slots=[dict(slot=b['slot'],formula=b['formula']) for b in d['slot_bindings']])
        if kind=='answer_cq': return dict(cq_id=d['question']['id'],answer='P Q',answered=True,supporting_t_ids=['a','b'])
        return dict(novelty='new_assertion',fidelity='matches',classification='own_thesis',reason='R',resolves_gap=True)
    calls,_=rig(tmp_path,reply)
    (tmp_path/'frozen-t.json').write_text(canonical(artifact))
    (tmp_path/'commitment-provenance.json').write_text(canonical(provenance))
    targets=calls.propose_targets(t)
    assert targets[0].gap is not None and targets[1].gap is None
    assert seen[0]['resolution_gap']['kind']=='open_problem'
    assert Proposition.from_dict(targets[0].to_dict())==targets[0]
    # Same gap origin must survive engine node-id replacement and graph round-trip.
    from ara.runtime.orchestration import NativeEngine
    from ara.bank import load_bank
    from test_search_alignment import ROOT
    graph=NativeEngine(load_bank(ROOT/'bank'),calls)._engine(t).search(targets[0]).routes[0]
    assert graph.status=='CLOSED'
    import json
    from ara.runtime.report_traces import new_trace,validate_trace
    rows=[json.loads(line) for path in (tmp_path/'search-traces').glob('*.jsonl') for line in path.read_text().splitlines()]
    trace=new_trace(0,rows[0])
    trace.update(states=[r for r in rows if r['action']=='state'],receipts=[dict(payload=r) for r in rows])
    validate_trace(trace)
    assert trace['complete'],trace['issues']
    assert trace['completed_routes'][0]['graph']==graph.to_dict()

    root=next(n for n in graph.nodes if n.id==graph.root_id)
    receipt=route_contribution(RouteGraph.from_dict(graph.to_dict()),t,provenance)
    assert receipt['gap_resolution']['supported']
    missing=replace(targets[0].gap,support_groups=(('absent',),))
    bad=replace(graph,nodes=(replace(root,proposition=replace(root.proposition,gap=missing)),)+graph.nodes[1:])
    assert route_contribution(bad,t,provenance)['classification']=='CLOSED-gap-unresolved'


def test_unrelated_thesis_is_not_retained_as_resolution(tmp_path):
    t=CommitmentSet((Commitment('a','P','a:1',P),Commitment('b','Q','b:1',Q)))
    artifact,provenance=frozen_metadata(t,('a','b'),{'P':'P is unresolved'})
    def reply(kind,d):
        if kind=='propose_targets': return dict(targets=[Proposition('r','R',R).to_dict()])
        return dict(novelty='new_assertion',fidelity='matches',classification='own_thesis',reason='R',resolves_gap=False)
    calls,_=rig(tmp_path,reply)
    (tmp_path/'frozen-t.json').write_text(canonical(artifact))
    (tmp_path/'commitment-provenance.json').write_text(canonical(provenance))
    targets=calls.propose_targets(t)
    assert targets and all(t.gap is None for t in targets)
    import json
    assert any('gap_resolution_not_established' in e['payload_json'] for e in calls.log.read())


def test_explicit_open_markers_beyond_unresolved():
    from ara.runtime.gaps import detect_gaps
    for definition in ('P is open', 'The problem remains of P', 'The jury is out on P', 'P remains open'):
        t=CommitmentSet((Commitment('a','P','a:1',P),))
        artifact,provenance=frozen_metadata(t,('a',),{'P':definition})
        gaps=detect_gaps(t,artifact['symbol_catalogue']['symbols'],provenance)['gaps']
        assert len(gaps)==1 and gaps[0].kind=='open_problem'


def test_frozen_definition_stance_conflict_reaches_native_proposal(tmp_path):
    from ara.runtime.commitment_provenance import make_commitment_provenance
    t=CommitmentSet((Commitment('a','P','a:1',P),Commitment('b','Q','b:1',Q),Commitment('c','R','b:2',R)))
    artifact,provenance=frozen_metadata(t,('a','b','b'),{'P':'S','Q':'S'})
    provenance['commitments']['b'].update(stance='attacked',attribution='attacked_view')
    provenance=make_commitment_provenance(t,artifact['symbol_catalogue'],provenance['commitments'])
    seen=[]
    target=Proposition('f','F(a)',Formula.from_dict({'op':'predicate','name':'F','terms':[{'kind':'constant','name':'a'}]}))
    def reply(kind,d):
        if kind=='classify_conflict': return dict(classification='compatible',reason='P')
        if kind=='propose_targets':
            seen.append(d)
            return dict(targets=[target.to_dict()])
        return dict(novelty='new_assertion',fidelity='matches',classification='own_thesis',reason='F(a)',resolves_gap=True)
    calls,_=rig(tmp_path,reply)
    for name,value in [('frozen-t.json',artifact),('commitment-provenance.json',provenance)]:
        (tmp_path/name).write_text(canonical(value))
    before={name:(tmp_path/name).read_bytes() for name in ('frozen-t.json','commitment-provenance.json')}
    targets=calls.propose_targets(t)
    resolutions=[v for v in targets if v.gap is not None]
    assert len(resolutions)==1
    gap=resolutions[0].gap
    assert gap.kind=='stance_conflict' and gap.commitment_ids==('a','b')
    assert gap.support_groups==(('a',),('c',))
    assert seen[0]['resolution_gap']==gap.to_dict()
    assert all((tmp_path/name).read_bytes()==value for name,value in before.items())


def test_definition_conflict_preserves_structure_arguments_and_polarity():
    from ara.runtime.gaps import detect_gaps
    from ara.types import Term
    fa=Formula('predicate',name='F',terms=(Term('constant','a'),))
    ga=Formula('predicate',name='G',terms=(Term('constant','a'),))
    gb=Formula('predicate',name='G',terms=(Term('constant','b'),))
    for left,right,expected in [(P,Q,True),(P,Q.negated(),False),
            (Formula('and',(P,R)),Formula('or',(Q,R)),False),
            (Formula('and',(P,R)),Q,False),(fa,ga,True),(fa,gb,False)]:
        t=CommitmentSet((Commitment('a','P','a:1',left),Commitment('b','Q','b:1',right)))
        artifact,provenance=frozen_metadata(t,('a','b'),{'P':'S','Q':'S','F':'S','G':'S'})
        provenance['commitments']['b']['stance']='attacked'
        result=detect_gaps(t,artifact['symbol_catalogue']['symbols'],provenance)
        assert bool([g for g in result['gaps'] if g.kind=='stance_conflict'])==expected
    artifact,provenance=frozen_metadata(t,('a','b'),{'F':'S','G':'R'})
    provenance['commitments']['b']['stance']='attacked'
    assert not detect_gaps(t,artifact['symbol_catalogue']['symbols'],provenance)['gaps']
