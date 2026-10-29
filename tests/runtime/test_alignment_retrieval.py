"""Broad bounded alignment retrieval and isolated native judgment requests."""
from copy import deepcopy
import json
import pytest
from ara.runtime.symbol_alignment import candidate_pairs, align_symbols
from ara.runtime.commitment_provenance import make_commitment_provenance
from ara.runtime.frozen_catalogue import make_catalogue
from test_symbol_alignment import fixture, configure_judge
from test_extraction import rig, ROOT


def inventory():
    specs=[('P','a','P Q'),('Q','a','P Q'),('R','a','P Q'),
           ('S','b','P Q'),('F','b','P Q'),('G','c','R S'),
           ('H','d','R S '+' '.join('P'+str(i) for i in range(30)))]
    symbols=[dict(name=n,kind='atom',arity=0,definition=d,evidence_ids=[n]) for n,p,d in specs]
    rows={n:dict(source_id=p) for n,p,d in specs}
    return symbols,rows


def test_retrieval_backfills_reports_prefilters_and_covers_papers():
    from ara.runtime.symbol_alignment import candidate_inventory
    symbols,rows=inventory()
    result=candidate_inventory(symbols,rows,limit=3,minimum_score=.95)
    assert len(result['candidates'])==3
    assert result['signature_compatible_pairs']==17
    assert result['lexical_overlap_pairs']==7 and result['above_threshold_pairs']==6
    assert result['backfilled_pairs']==1 and result['diversity_additions']==1
    assert result['covered_papers']==['a','b','c','d']
    plain=candidate_inventory(symbols,rows,limit=3,minimum_score=.95,paper_diversity=False)
    assert plain['covered_papers']==['a','b'] and plain['diversity_additions']==0
    assert result==candidate_inventory(list(reversed(symbols)),dict(reversed(list(rows.items()))),limit=3,minimum_score=.95)
    all_pairs=candidate_inventory(symbols,rows,limit=20,minimum_score=.95)
    assert len(all_pairs['candidates'])==7 and all_pairs['backfilled_pairs']==1
    assert candidate_inventory(symbols,rows,limit=20,minimum_score=0)['above_threshold_pairs']==7
    assert candidate_pairs(symbols,rows,limit=0)==[]
    for value in (-1,1.1,float('nan'),float('inf'),True,'0.1'):
        with pytest.raises(ValueError):candidate_inventory(symbols,rows,minimum_score=value)
    with pytest.raises(ValueError):candidate_inventory(symbols,rows,paper_diversity='yes')


def test_native_judge_neutral_topic_and_retrieval_replay(rig,monkeypatch):
    from ara.runtime.commitment_provenance import validate_commitment_provenance
    from ara.runtime.cache import canonical,digest
    calls,requests=configure_judge(rig,monkeypatch,'unrelated')
    calls.topic='S'
    calls.config.update(construction_alignment_min_score=.99,construction_alignment_paper_diversity=False)
    t,symbols,rows=fixture()
    result,final_symbols,final_rows,receipt=align_symbols(calls,t,symbols,rows)
    assert requests and all(r['topic']=='' for r in requests)
    assert all(r['candidate']['left']['definition']=='P Q' and r['sources'] for r in requests)
    assert receipt['retrieval']['minimum_score']==.99
    assert receipt['retrieval']['paper_diversity'] is False
    logged=next(json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='symbol_alignment_candidates')
    assert logged['retrieval']==receipt['retrieval'] and logged['retrieval']['signature_compatible_pairs']==3
    catalogue=make_catalogue(result,final_symbols)
    meta=make_commitment_provenance(result,catalogue,final_rows,alignment=receipt)
    bad=deepcopy(meta);bad['alignment']['retrieval']['lexical_overlap_pairs']=99
    bad['sha256']=digest(canonical({k:v for k,v in bad.items() if k!='sha256'}))
    with pytest.raises(ValueError,match='retrieval'):validate_commitment_provenance(bad,result,catalogue)
    assert t==result and symbols==final_symbols and rows==final_rows


def test_legacy_alignment_receipt_replays_original_policy(rig,monkeypatch):
    from ara.runtime.symbol_alignment import legacy_candidate_pairs
    t,symbols,rows=fixture()
    symbols[2]['definition']='P '+' '.join('P'+str(i) for i in range(200))
    pairs=[dict(left='P',right='Q',score=1.0)]
    assert legacy_candidate_pairs(symbols,rows)==pairs
    assert len(candidate_pairs(symbols,rows))==3
    receipt=dict(policy_version='cross-source-symbol-alignment-v1',candidate_limit=150,candidates=pairs,
        judgments=[dict(left=p['left'],right=p['right'],relation='unrelated',reason='P Q') for p in pairs],
        original_commitments=t.to_dict(),original_symbols=symbols,status='accepted',refusal_reason=None,
        mapping={s['name']:s['name'] for s in symbols})
    meta=make_commitment_provenance(t,make_catalogue(t,symbols),rows,alignment=receipt)
    assert meta['alignment']==receipt


def test_native_discovery_never_dispatches_alignment_as_source(rig,monkeypatch):
    from ara.bank import load_bank
    from ara.runtime.orchestration import prepare_commitments
    from ara.runtime.providers import Response
    from test_extraction import response
    calls,_=configure_judge(rig,monkeypatch)
    t,symbols,rows=fixture()
    monkeypatch.setattr(calls,'build_t',lambda *_:t)
    calls.log.record('build_t_merged',commitments=t.to_dict(),symbols=symbols,provenance=rows)
    aligned=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    requests=[]
    def complete(kind,prompt,*args):
        assert kind=='classify_conflict'
        data=json.loads(prompt.split('\nINPUT_JSON\n')[1]);requests.append(data)
        return Response(response(dict(classification='compatible',reason='P Q')))
    monkeypatch.setattr(calls.provider,'complete',complete)
    assert calls.discover_gaps(aligned)['gaps']==()
    assert len(requests)==3
    assert all(row['source_id'] and row['stance']!='model_alignment' and row['attributed_to']
               for request in requests for row in request['pair'])
