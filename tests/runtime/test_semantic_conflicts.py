"""Cross-paper semantic judgments remain separate from frozen formal claims."""
import json
import pytest
from ara.runtime.cache import canonical
from ara.runtime.commitment_provenance import make_commitment_provenance
from ara.types import Commitment, CommitmentSet, Formula, Proposition
from test_search_alignment import P, Q, R, ROOT, rig
from test_cross_paper import frozen_metadata


def freeze(tmp_path, t, papers, definitions, stances=None):
    artifact, provenance = frozen_metadata(t, papers, definitions)
    rows = provenance['commitments']
    for tid, stance in (stances or {}).items():
        rows[tid].update(stance=stance, attribution={'endorsed':'author_claim', 'reported':'reported_view', 'attacked':'attacked_view'}[stance], source_kind='premise' if stance=='endorsed' else stance+'_view')
    provenance = make_commitment_provenance(t, artifact['symbol_catalogue'], rows)
    for name, data in [('frozen-t.json', artifact), ('commitment-provenance.json', provenance), ('commitments.json', t.to_dict())]:
        (tmp_path/name).write_text(canonical(data))
    return artifact, provenance


def test_ranked_pairs_cross_paper_private_symbols_and_roles(tmp_path):
    from ara.runtime.semantic_conflicts import rank_pairs
    s = Formula('atom', name='S')
    t = CommitmentSet(tuple(Commitment(tid, f.name, paper+':1', f)
        for tid,paper,f in [('a','a',P),('b','b',Q),('c','a',R),('d','d',s)]))
    artifact, provenance = frozen_metadata(t, ('a','b','a','d'), {'P':'P Q', 'Q':'P Q', 'R':'P', 'S':'S'})
    provenance['commitments']['b']['stance']='attacked'
    provenance['commitments']['c']['stance']='reported'
    result=rank_pairs(t, artifact['symbol_catalogue']['symbols'], provenance, 1)
    assert result['eligible_pairs']==1
    assert result['pairs'][0]['commitment_ids']==['a','b']
    assert result==rank_pairs(CommitmentSet(tuple(reversed(t.commitments))),artifact['symbol_catalogue']['symbols'],provenance,1)
    assert rank_pairs(t,None,None,60)['status']=='unavailable_legacy'
    with pytest.raises(ValueError): rank_pairs(t,[],provenance,-1)


@pytest.mark.parametrize('classification, expected', [('contradicts',1),('in_tension',1),('compatible',0),('unrelated',0)])
def test_isolated_classification_cache_gap_and_immutable_freeze(tmp_path, classification, expected):
    def reply(kind, data):
        assert kind=='classify_conflict'
        assert len(data['pair'])==2 and 'commitments' not in data and data['topic']==''
        assert {c['stance'] for c in data['pair']}=={'endorsed','reported'}
        return dict(classification=classification, reason='P Q')
    calls, requests=rig(tmp_path,reply)
    t=CommitmentSet((Commitment('a','P','a:1',P),Commitment('b','Q','b:1',Q)))
    freeze(tmp_path,t,('a','b'),{'P':'P Q','Q':'P Q'}, {'b':'reported'})
    original={p.name:p.read_bytes() for p in tmp_path.glob('*.json')}
    result=calls.discover_gaps(t)
    semantic=[g for g in result['gaps'] if g.kind=='semantic_conflict']
    assert len(semantic)==expected
    if semantic:
        assert semantic[0].finding==classification+': P Q'
        assert semantic[0].support_groups==(('a',),())
    calls.discover_gaps(t)
    assert len(requests)==1
    assert {p.name:p.read_bytes() for p in tmp_path.glob('*.json')}==original
    events=calls.log.read()
    assert sum(e['stage']=='semantic_pair_classified' for e in events)==2
    assert any(e['stage']=='classify_conflict' and e['label']=='MODEL' for e in events)


def test_semantic_gap_drives_resolution_proposal(tmp_path):
    seen=[]
    def reply(kind, data):
        if kind=='classify_conflict':return dict(classification='in_tension',reason='P Q')
        if kind=='propose_targets':
            seen.append(data)
            return dict(targets=[Proposition('r','R',R).to_dict()])
        return dict(classification='own_thesis',novelty='new_assertion',fidelity='matches',resolves_gap=True,reason='R')
    calls,_=rig(tmp_path,reply)
    t=CommitmentSet((Commitment('a','P','a:1',P),Commitment('b','Q','b:1',Q)))
    freeze(tmp_path,t,('a','b'),{'P':'P Q','Q':'P Q'})
    targets=calls.propose_targets(t,1)
    assert targets[0].gap.kind=='semantic_conflict'
    assert seen[0]['resolution_gap']['finding']=='in_tension: P Q'
    assert targets[0].gap.support_groups==(('a',),('b',))


def test_native_tiers_report_and_resolution_proposal(tmp_path, monkeypatch):
    from ara.bank import load_bank
    from ara.runtime.orchestration import NativeEngine, search_all
    from ara.runtime.report import build_run, generate_report
    t=CommitmentSet((Commitment('a','P','a:1',P),Commitment('b','Q','b:1',Q)))
    resolution_requests=[]
    def reply(kind,data):
        if kind=='map_leaf':return dict(t_id='open')
        if kind=='propose_cuts':
            return dict(proposals=[dict(bank_id='sign',conclusion_text=data['goal']['text'],conclusion_ref='current_goal',
                premises=[dict(slot=slot,text=c.text,t_id=c.id,scope_id=None) for slot,c in zip(('sign_relation','observed_sign'),t.commitments)])])
        if kind=='formalise_slots':return dict(slots=[dict(slot=b['slot'],formula=b['formula']) for b in data['slot_bindings']])
        if kind=='answer_cq':return dict(cq_id=data['question']['id'],answer='P Q',answered=True,supporting_t_ids=['a','b'])
        if kind=='tier1_repair':return dict(action='unresolved',detail='P Q',proposals=[])
        if kind=='propose_targets':
            resolution_requests.append(data)
            return dict(targets=[Proposition('s','S',Formula('atom',name='S')).to_dict()])
        if kind=='classify_target':return dict(classification='own_thesis',novelty='new_assertion',fidelity='matches',resolves_gap=True,reason='S')
        raise AssertionError(kind)
    calls,_=rig(tmp_path,reply)
    calls.config.update(forward_pass_depth=0,node_cap=30)
    artifact,provenance=freeze(tmp_path,t,('a','b'),{'P':'P','Q':'Q'})
    bank=load_bank(ROOT/'bank')
    calls.log.record('symbol_catalogue_frozen',**artifact['symbol_catalogue'])
    calls.log.record('commitment_provenance_frozen',**provenance)
    calls.log.record('commitments_frozen',commitments=t.to_dict(),bank_version=bank.bank_version)
    routes=search_all(calls,NativeEngine(bank,calls),t,(Proposition('r','R',R),))
    assert len(routes)==2 and all(r.status=='CLOSED' for r in routes)
    assert resolution_requests[0]['resolution_gap']['kind']=='tier2_conflict'
    assert '"text":"R"' in resolution_requests[0]['resolution_gap']['finding']
    assert set(resolution_requests[0]['resolution_gap']['route_ids'])=={r.id for r in routes}
    result=build_run(tmp_path)['conflicts']
    assert result['counts']==dict(tier1=1,tier2=1)
    assert result['tier1'][0]['repair']['action']=='unresolved'
    assert len(result['resolution_candidates'])==1
    monkeypatch.setattr('ara.runtime.report_render.shutil.which',lambda _:None)
    report=tmp_path.parent/(tmp_path.name+'-report')
    generate_report([tmp_path],report)
    data=json.loads((report/'data.json').read_text())['runs'][0]
    assert data['conflicts']['counts']==dict(tier1=1,tier2=1)
    assert 'Tier 1 repairs and Tier 2 conflicts' in (report/'report.html').read_text()
    assert (report/data['conflicts']['file']).is_file()


def test_pair_limit_and_context_refusal_are_disclosed(tmp_path):
    from ara.runtime.semantic_conflicts import rank_pairs
    t=CommitmentSet(tuple(Commitment(n,n,n+':1',Formula('atom',name=n)) for n in ('P','Q','R','S')))
    artifact,provenance=frozen_metadata(t,('a','b','c','d'),{'P':'P','Q':'Q','R':'P Q R','S':'P Q R'})
    ranked=rank_pairs(t,artifact['symbol_catalogue']['symbols'],provenance,2)
    assert ranked['eligible_pairs']==5 and len(ranked['pairs'])==2
    assert [p['commitment_ids'] for p in ranked['pairs']]==[['R','S'],['P','R']]
    calls,requests=rig(tmp_path,lambda *args:pytest.fail('refused pair dispatched'))
    freeze(tmp_path,t,('a','b','c','d'),{n:'P Q' for n in ('P','Q','R','S')})
    calls.config.update(semantic_conflict_pair_limit=2,model_context_token_bound=1)
    assert not any(g.kind=='semantic_conflict' for g in calls.discover_gaps(t)['gaps'])
    failures=[json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='semantic_pair_failed']
    assert len(failures)==2 and not requests
    stops=[json.loads(e['payload_json']) for e in calls.log.read() if e['label']=='STOP']
    assert len(stops)==2 and all(s['scope']=='search' for s in stops)


def test_bad_classifier_output_never_becomes_a_gap(tmp_path):
    calls,_=rig(tmp_path,lambda *args:dict(classification='formal_contradiction',reason='P Q'))
    t=CommitmentSet((Commitment('a','P','a:1',P),Commitment('b','Q','b:1',Q)))
    freeze(tmp_path,t,('a','b'),{'P':'P Q','Q':'P Q'})
    assert not any(g.kind=='semantic_conflict' for g in calls.discover_gaps(t)['gaps'])
    assert any(e['stage']=='semantic_pair_failed' for e in calls.log.read())


def test_report_does_not_reuse_findings_from_prior_search_generation(tmp_path):
    from ara.runtime.conflict_feedback import conflict_report
    from ara.runtime.logging import EventLog
    from ara.runtime.cache import digest
    log=EventLog(tmp_path/'events.jsonl')
    analyses=[dict(target=dict(target=dict(id='r')), tier1=[dict(repair=dict(action='unresolved'))], tier2=[])]
    log.record('conflicts_and_robustness',findings=dict(analyses=analyses))
    log.record('tier2_resolution_candidates',analyses_sha256=digest(canonical(analyses)),candidates=[dict(id='s')],status='proposed_not_searched')
    assert conflict_report(log.read())['counts']['tier1']==1
    log.record('search_publication_started',batch_id='new')
    result=conflict_report(log.read())
    assert result['analysis_status']=='not_recorded' and result['counts']['tier1']==0
    assert result['resolution_candidates']==[]
    log.record('conflicts_and_robustness',findings=dict(analyses=analyses))
    assert conflict_report(log.read())['resolution_candidates']==[]


def test_tier2_keeps_each_routes_distinct_support_group(tmp_path):
    from ara.bank import load_bank
    from ara.runtime.orchestration import NativeEngine
    from ara.runtime.conflict_feedback import tier2_gaps
    def reply(kind,data):
        assert kind=='map_leaf'
        return dict(t_id='a' if data['leaf']['formula']==P.to_dict() else 'b')
    calls,_=rig(tmp_path,reply)
    calls.config.update(forward_pass_depth=0,node_cap=8)
    t=CommitmentSet((Commitment('a','P','a:1',P),Commitment('b','not P','b:1',P.negated())))
    _,provenance=freeze(tmp_path,t,('a','b'),{'P':'P'})
    analysis=NativeEngine(load_bank(ROOT/'bank'),calls).analyse(Proposition('p','P',P),t)
    assert len(analysis.tier2)==1
    gaps=tier2_gaps((analysis,),t,provenance)
    assert gaps[0].support_groups==(('a',),('b',))
