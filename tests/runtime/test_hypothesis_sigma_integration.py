"""Native v3 source policy and wide alignment remain valid beneath v4 H."""
from dataclasses import replace
import json

from ara.bank import load_bank
from ara.runtime.commitment_provenance import load_commitment_provenance, PRECISE_SCREEN
from ara.runtime.extraction import extract
from ara.runtime.freeze_fork import fork_from_freeze
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.providers import Response
from rich_fixture import graph, batch_response
from test_extraction import rig, register, response, ROOT
from test_hypothesis_premises import configured


def test_precise_wide_alignment_and_hypotheses_freeze_and_fork(rig,monkeypatch,tmp_path):
    calls,provider,papers,*_=rig
    second=replace(papers[0],source_id='q',record_json=json.dumps(dict(id='q',title='Q')))
    for index,paper in enumerate((papers[0],second)):
        value=graph(paper.source_id);value['items']=value['items'][index:index+1]
        register(calls,provider,paper,value)
    literature=extract(calls,(papers[0],second)).read_text()
    calls.config.update(construction_precise_attribution=True,construction_shared_vocabulary=True,
        construction_alignment_top_k=2,construction_alignment_candidates=4,hypothesis_premises=[configured()])
    bank=load_bank(ROOT/'bank')
    calls.log.record('run_started',config=calls.config,topic='P',literature=literature,audience='P',bank_version=bank.bank_version)
    seen=[]
    def complete(kind,prompt,*_):
        data=json.loads(prompt.split('INPUT_JSON\n')[1]);seen.append(kind)
        if kind=='judge_symbol_alignment':return Response(response(dict(relation='entails_left_right',reason='P Q')))
        value=batch_response(data)
        if kind=='build_t_batch':
            for row in value['commitments']:row['definition']='P holds' if row['formula']['name']=='P' else 'Q'
        return Response(response(value))
    monkeypatch.setattr(provider,'complete',complete)
    frozen=prepare_commitments(calls,bank,literature,'P')
    catalogue=json.loads((calls.log.path.parent/'frozen-t.json').read_text())['symbol_catalogue']
    meta=load_commitment_provenance(calls.log.path.parent,frozen,catalogue)
    assert meta['schema_version']=='commitment-provenance-v4'
    sources=[row for row in meta['commitments'].values() if 'source_text' in row]
    assert len(sources)==2 and all(row['definition_screen']==PRECISE_SCREEN for row in sources)
    assert any(c.text=='P holds' for c in frozen.commitments)
    assert meta['alignment']['retrieval']['per_symbol_top_k']==2
    assert seen.count('judge_symbol_alignment')==1
    assert any(row.get('kind')=='alignment' for row in meta['commitments'].values())
    assert meta['commitments']['hypothesis:h']['stance']=='proposed'
    assert sum(e['stage']=='commitments_frozen' for e in calls.log.read())==1
    artifacts={name:(calls.log.path.parent/name).read_bytes() for name in
               ('commitments.json','frozen-t.json','commitment-provenance.json')}
    _,_,forked=fork_from_freeze(calls.log.path.parent,tmp_path/'fork',bank)
    assert forked==frozen
    assert {name:(tmp_path/'fork'/name).read_bytes() for name in artifacts}==artifacts
    assert load_commitment_provenance(tmp_path/'fork',forked,catalogue)==meta
