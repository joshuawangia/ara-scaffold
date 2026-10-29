"""Operator-prioritized external AI findings remain logged hypotheses."""
import json
from pathlib import Path
import pytest
from ara.runtime.cache import canonical,digest
from ara.types import Commitment,CommitmentSet,Proposition
from test_cross_paper import frozen_metadata
from test_search_alignment import P,Q,R,rig


def setup(tmp_path):
    t=CommitmentSet((Commitment('a','P','a:1',P),Commitment('b','Q','b:1',Q)))
    artifact,meta=frozen_metadata(t,('a','b'),{'P':'P remains open'})
    seen=[]
    def reply(kind,d):
        if kind=='map_leaf':return dict(t_id='open')
        if kind=='propose_cuts':return dict(proposals=[])
        if kind=='classify_conflict':return dict(classification='compatible',reason='P Q')
        if kind=='propose_targets':
            seen.append(d)
            return dict(targets=[Proposition('r','R',R).to_dict()])
        return dict(novelty='new_assertion',fidelity='matches',classification='own_thesis',reason='R',resolves_gap=True)
    calls,_=rig(tmp_path,reply)
    for name,value in [('frozen-t.json',artifact),('commitment-provenance.json',meta)]:
        (tmp_path/name).write_text(canonical(value))
    document=dict(schema_version='external-gaps-v1',gaps=[dict(id='lead',origin='AI-found',priority=0,
        finding='P Q',paper_ids=['a','b'],commitment_ids=['a','b'],support_groups=[['a'],['b']],
        evidence=[dict(source_id='a',location='1',finding='P')],currency_verdict='partial',
        search_scope='2018–2026',claim_framing='not found within the stated 2018–2026 search scope; partially anticipated by P')])
    path=tmp_path/'input-gaps.json';path.write_text(canonical(document))
    calls.config['gap_file']=str(path)
    return calls,t,document,path,seen


def test_external_gap_is_logged_first_bound_and_roundtrips(tmp_path):
    calls,t,document,path,seen=setup(tmp_path)
    targets=calls.propose_targets(t,count=1)
    assert seen[0]['resolution_gap']['id']=='external:lead'
    gap=targets[0].gap
    assert gap.kind=='external_gap' and gap.support_groups==(('a',),('b',))
    assert json.loads(gap.external_evidence_json)['record']==document['gaps'][0]
    assert Proposition.from_dict(targets[0].to_dict())==targets[0]
    from ara.types import RouteGraph, RouteNode
    route=RouteGraph('route','r',(RouteNode('r',targets[0],'leaf','open'),),'OPEN')
    assert calls.essay_outline(route)['gap_resolution']==gap.to_dict()
    from ara.runtime.gaps import resolution_support
    assert not resolution_support(gap,['a'],calls.search_vocabulary(t)['commitment_provenance'])['supported']
    receipt=next(json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='external_gaps_loaded')
    assert receipt['document']==document and receipt['file_sha256']==digest(path.read_text())
    assert receipt['commitments_sha256']==digest(canonical(t.to_dict()))
    # Changed evidence enters the next prompt and cache identity, with a fresh receipt.
    document['gaps'][0]['currency_verdict']='unresolved'
    path.write_text(canonical(document))
    calls.propose_targets(t,count=1)
    assert 'unresolved' in seen[-1]['resolution_gap']['external_evidence_json']


@pytest.mark.parametrize('invalid',['unknown','alignment','empty_group','missing_evidence','bad_origin','missing_file'])
def test_external_gap_refuses_invalid_evidence(tmp_path,invalid):
    calls,t,document,path,seen=setup(tmp_path)
    record=document['gaps'][0]
    if invalid=='unknown':record['commitment_ids']=['missing']
    if invalid=='alignment':record['support_groups']=[['missing'],['b']]
    if invalid=='empty_group':record['support_groups']=[[],['b']]
    if invalid=='missing_evidence':record['evidence']=[]
    if invalid=='bad_origin':record['origin']='source-endorsed'
    path.write_text(canonical(document))
    if invalid=='missing_file':path.unlink()
    with pytest.raises((ValueError,FileNotFoundError)):
        calls.propose_targets(t)
    assert not seen


def test_fork_cli_uses_external_gap_file_without_editing_freeze(tmp_path):
    from ara.runtime.cli import main
    from ara.runtime.calls import ModelCalls
    from ara.runtime.cache import Cache
    from ara.runtime.logging import EventLog
    from ara.bank import load_bank
    from test_search_alignment import ROOT
    source=tmp_path/'source';source.mkdir()
    calls,t,document,path,seen=setup(source)
    config={**calls.config,'provider':'mock','target_candidates':1,'forward_pass_depth':0,'depth_cap':1}
    config.pop('gap_file')
    (source/'commitments.json').write_text(t.to_json())
    artifact=json.loads((source/'frozen-t.json').read_text())
    meta=json.loads((source/'commitment-provenance.json').read_text())
    bank=load_bank(ROOT/'bank')
    calls.log.record('run_started',config=config,topic='P',audience='P',literature='P',bank_version=bank.bank_version)
    calls.log.record('symbol_catalogue_frozen',**artifact['symbol_catalogue'])
    calls.log.record('commitment_provenance_frozen',**meta)
    calls.log.record('commitments_frozen',commitments=t.to_dict(),bank_version=bank.bank_version)
    before={p.name:p.read_bytes() for p in source.iterdir() if p.is_file()}
    def factory(config,log,topic):
        return ModelCalls(config,calls.provider,log,Cache(tmp_path/'cache'),ROOT,topic)
    destination=tmp_path/'fork'
    assert main(['fork-from-freeze','--source-run',str(source),'--run-dir',str(destination),
        '--gap-file',str(path)],calls_factory=factory)==0
    events=EventLog(destination/'events.jsonl').read()
    selected=next(json.loads(e['payload_json'])['candidates'] for e in events if e['stage']=='candidates')
    assert selected[0]['gap']['id']=='external:lead'
    assert seen[0]['resolution_gap']['id']=='external:lead'
    assert any(e['stage']=='external_gaps_loaded' for e in events)
    assert {p.name:p.read_bytes() for p in source.iterdir() if p.is_file()}==before
