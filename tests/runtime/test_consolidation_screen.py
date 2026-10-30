"""Fresh definitions use their own precise policy, never retag source provenance."""
from copy import deepcopy
import json

import pytest

from ara.bank import load_bank
from ara.runtime.cache import canonical, digest
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.search_alignment import catalogue_inputs
from ara.runtime.vocabulary_consolidation import consolidate, validate_receipt
from ara.types import CommitmentSet
from test_extraction import rig, ROOT
from test_vocabulary_consolidation import options, provider
from test_symbol_alignment import fixture


@pytest.mark.parametrize('definition',['state a: P','P holds at a','a maintains P'])
def test_fresh_definitions_do_not_inherit_legacy_lexicon(rig,monkeypatch,definition):
    calls=rig[0];calls.config.update(options());t,symbols,rows=fixture();before=deepcopy(rows)
    assert all('definition_screen' not in r for r in rows.values())
    monkeypatch.setattr(calls,'build_t',lambda *_:t)
    calls.log.record('build_t_merged',commitments=t.to_dict(),symbols=symbols,provenance=rows)
    def change(data,inputs):
        if data['new_symbols']:data['new_symbols'][0]['definition']=definition
    provider(calls,monkeypatch,change)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    meta=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']
    assert meta['commitments']==before
    assert meta['consolidation']['symbols'][0]['definition']==definition
    assert meta['consolidation']['schema_version']=='vocabulary-consolidation-v3'
    assert meta['consolidation']['plan']['policy']['definition_screen']=='attribution-frames-v1'
    assert all('definition_screen' not in r for r in meta['commitments'].values())


@pytest.mark.parametrize('definition,frame',[
    ('b argues that P','argues'),
    ('b holds that P','holds that'),
    ('b h**olds** th**at** P','holds that'),
    ('b states <strong>that</strong> P','states that'),
])
def test_exact_definition_feedback_allows_bounded_correction(rig,monkeypatch,definition,frame):
    calls=rig[0];calls.config.update(options());calls.config['validation_attempts']=2
    seen=[]
    def change(data,inputs):
        seen.append(deepcopy(inputs))
        if len(seen)==1:data['new_symbols'][0]['definition']=definition
    provider(calls,monkeypatch,change)
    t,symbols,rows,receipt=consolidate(calls,*fixture(),'P')
    feedback=seen[1]['validation_feedback']['reference_constraints']['definition_issues']
    assert len(feedback)==1
    issue=feedback[0]
    assert issue['declaration_slot']==0 and issue['handle']=='n0'
    assert issue['definition']==definition and issue['screen']=='attribution-frames-v1'
    assert frame in [m['match'] for m in issue['matched_frames']]
    assert issue['reason']=='attribution_frame'
    assert len(t.commitments)==3
    assert receipt['symbols'][0]['definition']=='F(a)'


@pytest.mark.parametrize('definition',['b argues that P','b holds <em>that</em> P',
    'b maintains &quot;that&quot; P','![b h**olds** th**at** P](https://example.invalid/p.png)'])
def test_attribution_and_unsupported_markup_never_freeze(rig,monkeypatch,definition):
    calls=rig[0];calls.config.update(options());t,symbols,rows=fixture()
    monkeypatch.setattr(calls,'build_t',lambda *_:t)
    calls.log.record('build_t_merged',commitments=t.to_dict(),symbols=symbols,provenance=rows)
    def change(data,inputs):
        if data['new_symbols']:data['new_symbols'][0]['definition']=definition
    provider(calls,monkeypatch,change)
    with pytest.raises(ValueError,match='consolidation symbol is not content'):
        prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert not (calls.log.path.parent/'commitments.json').exists()


def test_v2_completed_receipt_retains_legacy_definition_policy():
    receipt=json.loads((ROOT/'tests/fixtures/runtime/consolidation-v2.json').read_text())
    t=CommitmentSet.from_dict(receipt['commitments'])
    validate_receipt(receipt,t,receipt['symbols'],receipt['provenance'])
    receipt['batches'][0]['response']['new_symbols'][0]['definition']='state a: P'
    receipt['sha256']=digest(canonical({k:v for k,v in receipt.items() if k!='sha256'}))
    with pytest.raises(ValueError,match='consolidation symbol is not content'):
        validate_receipt(receipt,t,receipt['symbols'],receipt['provenance'])


def test_rehashed_attribution_receipt_refuses(rig,monkeypatch):
    from ara.runtime.commitment_provenance import validate_commitment_provenance
    from ara.runtime.frozen_catalogue import make_catalogue
    calls=rig[0];calls.config.update(options());t,symbols,rows=fixture()
    monkeypatch.setattr(calls,'build_t',lambda *_:t)
    calls.log.record('build_t_merged',commitments=t.to_dict(),symbols=symbols,provenance=rows)
    provider(calls,monkeypatch)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    context=catalogue_inputs(calls.log.path.parent,final);meta=context['commitment_provenance']
    receipt=meta['consolidation'];receipt['batches'][0]['response']['new_symbols'][0]['definition']='b holds <em>that</em> P'
    receipt['sha256']=digest(canonical({k:v for k,v in receipt.items() if k!='sha256'}))
    meta['sha256']=digest(canonical({k:v for k,v in meta.items() if k!='sha256'}))
    with pytest.raises(ValueError,match='consolidation symbol is not content'):
        validate_commitment_provenance(meta,final,make_catalogue(final,context['symbol_catalogue']))


def test_precise_definitions_survive_alignment_and_frozen_fork(rig,monkeypatch,tmp_path):
    from ara.runtime.providers import Response
    from ara.runtime.freeze_fork import fork_from_freeze
    from test_extraction import response
    calls=rig[0];calls.config.update(options());t,symbols,rows=fixture();before=deepcopy(rows)
    calls.log.record('run_started',config=calls.config,topic='P',literature='P',audience='P',bank_version=load_bank(ROOT/'bank').bank_version)
    monkeypatch.setattr(calls,'build_t',lambda *_:t)
    calls.log.record('build_t_merged',commitments=t.to_dict(),symbols=symbols,provenance=rows)
    def change(data,inputs):
        if inputs['batch_index']==0:data['new_symbols'][0]['definition']='state a: P'
        else:
            for f in data['formulas']:f['name']='n0'
            data['new_symbols']=[dict(kind='predicate',arity=1,definition='P holds at a')]
            data['reuse']=[dict(handle='s1',reason='a')]
    provider(calls,monkeypatch,change);complete=calls.provider.complete
    def routed(kind,*args):
        if kind=='judge_symbol_alignment':return Response(response(dict(relation='entails_left_right',reason='P Q')))
        return complete(kind,*args)
    monkeypatch.setattr(calls.provider,'complete',routed)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    meta=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']
    assert meta['alignment']['status']=='accepted'
    assert len(final.commitments)==4
    assert {id:meta['commitments'][id] for id in before}==before
    destination=tmp_path/'fork';_,_,copy=fork_from_freeze(calls.log.path.parent,destination,load_bank(ROOT/'bank'))
    assert catalogue_inputs(destination,copy)['commitment_provenance']==meta


def test_rehashed_policy_change_refuses(rig,monkeypatch):
    calls=rig[0];calls.config.update(options());provider(calls,monkeypatch)
    t,symbols,rows,receipt=consolidate(calls,*fixture(),'P')
    receipt['plan']['policy']['definition_screen']=None
    receipt['sha256']=digest(canonical({k:v for k,v in receipt.items() if k!='sha256'}))
    with pytest.raises(ValueError,match='consolidation plan mismatch'):
        validate_receipt(receipt,t,symbols,rows)
