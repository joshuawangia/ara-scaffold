"""Runtime bindings remove identifier echoing without changing semantic gates."""
import json

from ara.bank import load_bank
from ara.runtime.cache import canonical
from ara.runtime.logging import EventLog
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.providers import Response
from ara.runtime.search_alignment import catalogue_inputs
from ara.runtime.vocabulary_consolidation import validate_receipt
from ara.types import CommitmentSet
from test_extraction import rig, ROOT, response
from test_alignment_resume import completed
from test_vocabulary_consolidation import options


import pytest
from copy import deepcopy
from ara.runtime.cache import digest
from ara.runtime.vocabulary_consolidation import consolidate
from test_symbol_alignment import fixture
from test_vocabulary_consolidation import provider


def test_legacy_consolidation_receipt_still_replays():
    receipt=json.loads((ROOT/'tests/fixtures/runtime/consolidation-v1.json').read_text())
    final=CommitmentSet.from_dict(receipt['commitments'])
    original,symbols=validate_receipt(receipt,final,receipt['symbols'],receipt['provenance'])
    assert original.to_dict()==receipt['original_commitments']
    assert symbols==receipt['original_symbols']


def test_native_consolidation_derives_ids_and_all_symbol_uses(rig,monkeypatch):
    calls=rig[0];t,_,_=completed(calls);calls.config.update(options())
    monkeypatch.setattr(calls,'build_t',lambda *args:t)
    seen=[];schemas=[]
    def complete(kind,prompt,schema,maximum):
        value=json.loads(prompt.split('\nINPUT_JSON\n')[1]);seen.append((kind,value))
        if kind=='judge_symbol_alignment':return Response(response(dict(relation='unrelated',reason='P Q')))
        schemas.append(schema)
        count=len(value['accepted_commitments']['commitments'])
        fresh=not value['shared_symbols']
        handles=('n0','n1') if fresh else ('s0','s1')
        payload=dict(formulas=[dict(op='predicate',name=handles[0],terms=[dict(kind='constant',name=handles[1])]) for _ in range(count)],
            new_symbols=[dict(kind='predicate',arity=1,definition='F(a)'),dict(kind='constant',arity=0,definition='a')] if fresh else [],
            reuse=[] if fresh else [dict(handle=h,reason='F(a)') for h in handles])
        return Response(response(payload))
    monkeypatch.setattr(calls.provider,'complete',complete)
    frozen=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    directory=calls.log.path.parent;context=catalogue_inputs(directory,frozen)
    meta=context['commitment_provenance'];receipt=meta['consolidation']
    assert set(schemas[0]['properties'])=={'formulas','new_symbols','reuse'}
    assert 'evidence_ids' not in schemas[0]['properties']['new_symbols']['items']['properties']
    assert receipt['schema_version']=='vocabulary-consolidation-v3'
    assert [(c.id,c.text,c.citation) for c in frozen.commitments]==[(c.id,c.text,c.citation) for c in t.commitments]
    expected=sorted(c.id for c in t.commitments)
    assert all(s['evidence_ids']==expected for s in receipt['symbols'])
    assert receipt['after']['shared_symbols']==2
    assert all(set(b['response'])=={'formulas','new_symbols','reuse'} for b in receipt['batches'])
    assert sum(e['stage']=='commitments_frozen' for e in EventLog(directory/'events.jsonl').read())==1
    assert sum(kind=='consolidate_vocabulary' for kind,_ in seen)==2


@pytest.mark.parametrize('fault,field,expected', [
    ('count','expected_formula_count',2),
    ('unknown','unknown_formula_handles',['missing']),
    ('signature','signature_mismatches',[dict(slot=0,handle='n0',expected_kind='atom',expected_arity=0,received_kind='predicate',received_arity=1),dict(slot=1,handle='n0',expected_kind='atom',expected_arity=0,received_kind='predicate',received_arity=1)]),
    ('unused','unused_new_handles',['n2']),
    ('reuse','missing_reuse_handles',['s0','s1']),
    ('duplicate','duplicate_reuse_handles',['s0']),
])
def test_native_exact_feedback_corrects_same_slots(rig,monkeypatch,fault,field,expected):
    calls=rig[0];calls.config.update(options());calls.config['validation_attempts']=2
    seen=[];damaged=False
    def damage(data,value):
        nonlocal damaged
        seen.append(deepcopy(value))
        at=1 if fault in ('reuse','duplicate') else 0
        if value['batch_index']!=at or damaged:return
        damaged=True
        if fault=='count':data['formulas'].pop()
        elif fault=='unknown':data['formulas'][0]['name']='missing'
        elif fault=='signature':data['new_symbols'][0].update(kind='atom',arity=0)
        elif fault=='unused':data['new_symbols'].append(dict(kind='atom',arity=0,definition='P'))
        elif fault=='reuse':data['reuse']=[]
        elif fault=='duplicate':data['reuse'].append(deepcopy(data['reuse'][0]))
    provider(calls,monkeypatch,damage)
    result=consolidate(calls,*fixture(),'P')
    corrected=next(v for v in seen if 'validation_feedback' in v)
    assert corrected['validation_feedback']['reference_constraints'][field]==expected
    original=next(v for v in seen if v['batch_index']==corrected['batch_index'])
    assert {k:v for k,v in corrected.items() if k!='validation_feedback'}==original
    assert len(result[0].commitments)==3
    receipts=[json.loads(e['payload_json']) for e in calls.log.read() if e['label']=='MODEL']
    assert sum(r['status']=='rejected' for r in receipts)==1


@pytest.mark.parametrize('field',['slots','catalogue','introduced','evidence_ids','reuse'])
def test_rehashed_runtime_binding_tampering_refuses(rig,monkeypatch,field):
    calls=rig[0];calls.config.update(options());provider(calls,monkeypatch)
    t,symbols,rows,r=consolidate(calls,*fixture(),'P')
    bindings=r['batches'][1 if field in ('catalogue','reuse') else 0]['bindings']
    bindings[field]=[] if isinstance(bindings[field],list) else {}
    r['sha256']=digest(canonical({k:v for k,v in r.items() if k!='sha256'}))
    with pytest.raises(ValueError,match='runtime binding mismatch'):validate_receipt(r,t,symbols,rows)


@pytest.mark.parametrize('damage,reason',[('text','changed accepted text'),('reuse','reuse judgment mismatch')])
def test_legacy_semantic_gates_remain_enforced(damage,reason):
    r=json.loads((ROOT/'tests/fixtures/runtime/consolidation-v1.json').read_text())
    if damage=='text':r['batches'][0]['response']['commitments'][0]['definition']='S'
    else:r['batches'][1]['response']['alignments']=[]
    r['sha256']=digest(canonical({k:v for k,v in r.items() if k!='sha256'}))
    with pytest.raises(ValueError,match=reason):
        validate_receipt(r,CommitmentSet.from_dict(r['commitments']),r['symbols'],r['provenance'])


def test_small_batches_are_versioned_and_keep_components():
    from dataclasses import replace
    from ara.runtime.vocabulary_consolidation import make_plan
    t,symbols,rows=fixture()
    source=t.commitments[0];row=rows[source.id]
    t=CommitmentSet(tuple(replace(source,id=f'P{i}') for i in range(20)))
    rows={c.id:deepcopy(row) for c in t.commitments}
    symbols=[{**symbols[0],'evidence_ids':sorted(rows)}]
    config=dict(construction_consolidate_vocabulary=True,consolidation_batch_size=11)
    plan=make_plan(t,symbols,rows,config,'P')
    assert sorted(map(len,plan['batches']))==[4,8,8]
    legacy=make_plan(t,symbols,rows,config,'P',version='vocabulary-consolidation-v1')
    assert sorted(map(len,legacy['batches']))==[9,11]
    assert plan['plan_id']!=legacy['plan_id']


def test_stage_routing_and_preflight_include_handle_correction(rig,monkeypatch):
    from ara.runtime.codex_preflight import manifest
    from ara.runtime.providers import stage_settings
    calls=rig[0];calls.config.update(options());calls.config['validation_attempts']=2
    calls.config['stages']={'build_t_batch':dict(model='R'),'construction_correction':dict(model='S')}
    calls.config['pricing'].update({m:calls.config['pricing'][calls.config['model']] for m in ('R','S')})
    damaged=False
    def damage(data,inputs):
        nonlocal damaged
        if not damaged:data['formulas'].pop();damaged=True
    provider(calls,monkeypatch,damage)
    backend=calls.provider;generated=[]
    class Scoped:
        def __init__(self,config):self.model=config['model']
        def estimate(self,*args):return backend.estimate(*args)
        def complete(self,*args):generated.append(self.model);return backend.complete(*args)
    calls.provider_factory=Scoped
    consolidate(calls,*fixture(),'P')
    assert generated==['R','S','R']
    assert len(calls._stage_providers)==2
    config={**calls.config,'stages':{'build_t_batch':dict(provider='codex_cli',model='gpt-6-luna',effort='high'),
        'construction_correction':dict(provider='codex_cli',model='gpt-6-luna',effort='low')}}
    cases={c['case']:c for c in manifest(config,ROOT)['cases']}
    assert cases['consolidate_vocabulary']['effort']=='high'
    assert cases['consolidate_vocabulary_correction']['effort']=='low'
    assert stage_settings(config,'consolidate_vocabulary')['model']=='gpt-6-luna'
    assert not any(c['kind']=='consolidate_vocabulary' for c in manifest({**config,'construction_consolidate_vocabulary':False},ROOT)['cases'])


def test_corrupt_cached_handles_refuse_before_freeze(rig,monkeypatch):
    calls=rig[0];calls.config.update(options());provider(calls,monkeypatch)
    call=calls.call
    def interrupted(kind,inputs,check):
        if inputs.get('batch_index')==1:raise RuntimeError('P')
        return call(kind,inputs,check)
    monkeypatch.setattr(calls,'call',interrupted)
    with pytest.raises(RuntimeError,match='P'):consolidate(calls,*fixture(),'P')
    files=list(calls.cache.path.glob('*.json'));assert len(files)==1
    cached=json.loads(files[0].read_text())
    data=json.loads(cached['raw']['content'][0]['text']);data['formulas'][0]['name']='missing'
    cached['raw']['content'][0]['text']=canonical(data);files[0].write_text(canonical(cached))
    monkeypatch.setattr(calls,'call',call)
    monkeypatch.setattr(calls.provider,'complete',lambda *a:pytest.fail('cached output must be locally refused'))
    with pytest.raises(ValueError,match='formula handle mismatch'):consolidate(calls,*fixture(),'P')
    assert not any(e['stage']=='commitments_frozen' for e in calls.log.read())


def test_handle_binding_preserves_local_variables_and_nested_uses(rig,monkeypatch):
    calls=rig[0];calls.config.update(options())
    def quantified(data,inputs):
        # A quantified occurrence has no constant use; the sibling retains it.
        f=deepcopy(data['formulas'][0]);f['terms']=[dict(kind='variable',name='x')]
        data['formulas'][0]=dict(op='forall',variable='x',args=[dict(op='implies',args=[f,f])])
        if len(data['formulas'])==1:
            data['reuse']=[dict(handle='s0',reason='F(x)')]
    provider(calls,monkeypatch,quantified)
    t,symbols,rows,r=consolidate(calls,*fixture(),'P')
    assert t.commitments[0].formula.variable=='x'
    assert t.commitments[0].formula.args[0].args[0].terms[0].name=='x'
    assert symbols[0]['evidence_ids']==['P','Q','R']
    assert len(symbols[1]['evidence_ids'])==1
    validate_receipt(r,t,symbols,rows)
