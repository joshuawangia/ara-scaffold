"""Accepted content stays immutable through opt-in cross-source re-formalization."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from ara.bank import load_bank
from ara.runtime.cache import Cache, canonical
from ara.runtime.calls import ModelCalls
from ara.runtime.cli import main
from ara.runtime.providers import Response
from ara.types import CommitmentSet
from test_extraction import rig, ROOT, response
from test_hypothesis_construction_fork import finish_source, snapshot


def options(**values):
    return dict(construction_consolidate_vocabulary=True, consolidation_batch_size=2,
                construction_alignment_top_k=2, construction_alignment_candidates=10, **values)


def provider(calls, monkeypatch, damage=None):
    requests=[]
    def complete(kind,prompt,schema,maximum):
        value=json.loads(prompt.split('\nINPUT_JSON\n')[1]);requests.append((kind,value))
        if kind=='judge_symbol_alignment':return Response(response(dict(relation='unrelated',reason='P Q')))
        assert kind=='consolidate_vocabulary' and value['mode']=='vocabulary_consolidation'
        fresh=not value['shared_symbols']
        handles=('n0','n1') if fresh else ('s0','s1')
        data=dict(formulas=[dict(op='predicate',name=handles[0],terms=[dict(kind='constant',name=handles[1])]) for c in value['accepted_commitments']['commitments']],
            new_symbols=[dict(kind='predicate',arity=1,definition='F(a)'),dict(kind='constant',arity=0,definition='a')] if fresh else [],
            reuse=[] if fresh else [dict(handle=n,reason='F(a)') for n in handles])
        if damage:damage(data,value)
        return Response(response(data))
    monkeypatch.setattr(calls.provider,'complete',complete)
    return requests


def test_free_plan_never_calls_or_copies_source(rig,monkeypatch,tmp_path):
    from ara.runtime.construction_fork import inspect_construction_fork
    calls=rig[0];finish_source(calls,monkeypatch);source=calls.log.path.parent;before=snapshot(source)
    plan=inspect_construction_fork(source,tmp_path/'next',load_bank(ROOT/'bank'),[],consolidation=options())
    summary=plan['receipt']['consolidation_plan']
    assert summary['before']['bare_atoms']==3 and summary['before']['shared_symbols']==0
    assert summary['after'] is None and summary['generation_calls']==0
    assert len(summary['batches'])==2
    assert len({plan['state']['provenance'][id]['source_id'] for id in summary['batches'][0]})==2
    assert not (tmp_path/'next').exists() and snapshot(source)==before
    assert plan['state']['judgments']==[] and plan['state']['expected_source'] is not None


def launch(rig,monkeypatch,tmp_path,damage=None):
    calls=rig[0];frozen=finish_source(calls,monkeypatch);source=calls.log.path.parent;before=snapshot(source)
    requests=provider(calls,monkeypatch,damage)
    config=tmp_path/'consolidate.json';config.write_text(canonical(options()))
    destination=tmp_path/'consolidated'
    def factory(settings,log,topic):
        result=ModelCalls(settings,calls.provider,log,Cache(destination/'cache'),ROOT,topic)
        monkeypatch.setattr(result,'build_t',lambda *_:pytest.fail('must reuse construction'))
        monkeypatch.setattr(result,'propose_targets',lambda *a:())
        return result
    rc=main(['resume-alignment','--source-run',str(source),'--run-dir',str(destination),
             '--consolidation-config',str(config)],calls_factory=factory)
    assert snapshot(source)==before
    return rc,destination,requests,frozen


def test_native_consolidation_then_alignment_then_one_freeze(rig,monkeypatch,tmp_path):
    rc,path,requests,original=launch(rig,monkeypatch,tmp_path)
    assert rc==0
    from ara.runtime.search_alignment import catalogue_inputs
    from ara.runtime.logging import EventLog
    t=CommitmentSet.from_json((path/'commitments.json').read_text());meta=catalogue_inputs(path,t)['commitment_provenance']
    assert [(c.id,c.text,c.citation) for c in t.commitments]==[(c.id,c.text,c.citation) for c in original.commitments]
    assert meta['schema_version']=='commitment-provenance-v5'
    receipt=meta['consolidation']
    assert receipt['original_commitments']==original.to_dict()
    assert receipt['before']['shared_symbols']==0 and receipt['after']['shared_symbols']==2
    assert receipt['after']['bare_atoms']==0
    assert {c.formula.name for c in t.commitments}=={'V0_0'}
    assert len([k for k,v in requests if k=='consolidate_vocabulary'])==2
    assert len(requests[1][1]['shared_symbols'])==2
    events=EventLog(path/'events.jsonl').read();stages=[e['stage'] for e in events]
    assert stages.count('commitments_frozen')==1
    assert stages.index('vocabulary_consolidated')<stages.index('symbol_alignment_candidates')<stages.index('commitments_frozen')
    assert receipt['provenance']=={id:meta['commitments'][id] for id in receipt['provenance']}


@pytest.mark.parametrize('damage',[
    lambda d,v:d.update(commitments=[dict(definition='Q')]),
    lambda d,v:d['formulas'].pop(),
    lambda d,v:d['formulas'].__setitem__(0,dict(op='not',args=[d['formulas'][0]])),
    lambda d,v:d['formulas'].append(deepcopy(d['formulas'][0])),
    lambda d,v:d['new_symbols'][0].update(definition='b holds that P') if d['new_symbols'] else None,
    lambda d,v:d.update(reuse=[]) if v['shared_symbols'] else None,
    lambda d,v:d['formulas'][0].update(name='missing'),
    lambda d,v:d['new_symbols'].append(dict(kind='atom',arity=0,definition='P')),
])
def test_invalid_consolidation_never_freezes(rig,monkeypatch,tmp_path,damage):
    rc,path,_,_=launch(rig,monkeypatch,tmp_path,damage)
    assert rc==2 and not (path/'commitments.json').exists()


def test_cli_plan_has_zero_generation_and_no_destination(rig,monkeypatch,tmp_path):
    calls=rig[0];finish_source(calls,monkeypatch);source=calls.log.path.parent;before=snapshot(source)
    settings=tmp_path/'consolidation.json';settings.write_text(canonical(options()))
    destination=tmp_path/'planned';out=tmp_path/'plan'
    assert main(['resume-alignment','--source-run',str(source),'--run-dir',str(destination),
        '--consolidation-config',str(settings),'--plan-only','--output-dir',str(out)],
        calls_factory=lambda *a:pytest.fail('plan must never construct provider'))==0
    plan=json.loads((out/'alignment-resume-plan.json').read_text())['construction_fork']['consolidation_plan']
    assert plan['generation_calls']==0 and plan['after'] is None
    assert not destination.exists() and snapshot(source)==before


@pytest.mark.parametrize('field,value',[('construction_consolidate_vocabulary',1),('consolidation_batch_size',True),
    ('consolidation_batch_size',0),('consolidation_batch_size',65)])
def test_invalid_policy_refuses(field,value):
    from ara.runtime.vocabulary_consolidation import policy
    config=options();config[field]=value
    with pytest.raises(ValueError):policy(config)


def test_stage_policy_refuses():
    from ara.runtime.vocabulary_consolidation import policy
    with pytest.raises(ValueError,match='run-level'):
        policy(dict(stages=dict(build_t_batch=dict(construction_consolidate_vocabulary=True))))


@pytest.mark.parametrize('damage',['text','citation','stance','formula','judgment','hash'])
def test_rehashed_receipt_tampering_refuses(rig,monkeypatch,tmp_path,damage):
    rc,path,_,_=launch(rig,monkeypatch,tmp_path);assert rc==0
    from ara.runtime.commitment_provenance import validate_commitment_provenance
    from ara.runtime.cache import digest
    from ara.runtime.frozen_catalogue import make_catalogue
    meta=json.loads((path/'commitment-provenance.json').read_text());t=CommitmentSet.from_json((path/'commitments.json').read_text())
    cat=make_catalogue(t,json.loads((path/'frozen-t.json').read_text())['symbol_catalogue']['symbols'])
    r=meta['consolidation']
    if damage=='text':r['original_commitments']['commitments'][0]['text']='Q'
    elif damage=='citation':r['original_commitments']['commitments'][0]['citation']='Q'
    elif damage=='stance':r['provenance']['P']['stance']='reported'
    elif damage=='formula':r['batches'][0]['response']['formulas'][0]={'op':'atom','name':'Q'}
    elif damage=='judgment':r['batches'][1]['response']['reuse']=[]
    if damage!='hash':r['sha256']=digest(canonical({k:v for k,v in r.items() if k!='sha256'}))
    else:r['sha256']='0'*64
    meta['sha256']=digest(canonical({k:v for k,v in meta.items() if k!='sha256'}))
    with pytest.raises(ValueError):validate_commitment_provenance(meta,t,cat)


def test_default_path_never_consolidates(rig,monkeypatch):
    calls=rig[0];finish_source(calls,monkeypatch)
    assert not any(e['stage'].startswith('vocabulary_') for e in calls.log.read())
    assert json.loads((calls.log.path.parent/'commitment-provenance.json').read_text())['schema_version']!='commitment-provenance-v5'


def test_frozen_fork_preserves_embedded_receipt_and_metrics(rig,monkeypatch,tmp_path):
    rc,path,_,_=launch(rig,monkeypatch,tmp_path);assert rc==0
    from ara.runtime.freeze_fork import fork_from_freeze
    from ara.runtime.search_alignment import catalogue_inputs
    from ara.runtime.export import methodology
    log,run,t=fork_from_freeze(path,tmp_path/'frozen-copy',load_bank(ROOT/'bank'))
    assert catalogue_inputs(log.path.parent,t)['commitment_provenance']['consolidation']['after']['shared_symbols']==2
    report=json.loads(methodology(log.path).split('```json\n')[1].split('\n```')[0])
    assert report['construction']['consolidation'][0]['before']['shared_symbols']==0


def test_completed_consolidation_resumes_alignment_without_reformalizing(rig,monkeypatch,tmp_path):
    calls=rig[0];finish_source(calls,monkeypatch);source=calls.log.path.parent
    from ara.runtime.construction_fork import inspect_construction_fork,write_construction_fork
    from ara.runtime.alignment_resume import load_alignment_resume
    from ara.runtime.orchestration import prepare_commitments
    from ara.runtime.vocabulary_consolidation import consolidate
    bank=load_bank(ROOT/'bank');plan=inspect_construction_fork(source,tmp_path/'resume',bank,[],consolidation=options())
    log=write_construction_fork(plan);state=load_alignment_resume(log,bank)
    new=ModelCalls(state['run']['config'],calls.provider,log,Cache(tmp_path/'cache-resume'),ROOT,'P')
    requests=provider(new,monkeypatch)
    result=consolidate(new,state['commitments'],state['symbols'],state['provenance'],state['run']['literature'])
    assert len(requests)==2
    new.alignment_resume=load_alignment_resume(log,bank)
    monkeypatch.setattr(new.provider,'complete',lambda *a:pytest.fail('must not repeat consolidation'))
    frozen=prepare_commitments(new,bank,state['run']['literature'],'P')
    assert frozen==result[0]
    assert sum(e['stage']=='vocabulary_consolidated' for e in log.read())==1


def test_reported_stance_and_historical_symbol_unframes_survive(rig,monkeypatch):
    from ara.runtime.vocabulary_consolidation import consolidate
    from ara.runtime.commitment_provenance import make_commitment_provenance
    from ara.runtime.frozen_catalogue import make_catalogue
    from test_symbol_alignment import fixture
    calls=rig[0];calls.config.update(options());t,symbols,rows=fixture()
    rows['P'].update(stance='reported',attribution='reported_view',source_kind='reported_view')
    rows['Q']['definition_unframes']=[dict(kind='symbol',name='Q',author='b',original_definition='b holds that P Q',definition='P Q')]
    before=deepcopy(rows);provider(calls,monkeypatch)
    result,symbols,after,receipt=consolidate(calls,t,symbols,rows,'P')
    meta=make_commitment_provenance(result,make_catalogue(result,symbols),after,consolidation=receipt)
    assert meta['commitments']==before
    assert meta['commitments']['P']['stance']=='reported'
    assert meta['commitments']['Q']['definition_unframes'][0]['name']=='Q'


@pytest.mark.parametrize('required,success',[(['V0_0','V0_1'],True),(['P'],False)])
def test_hypotheses_bind_resulting_catalogue_not_original(rig,monkeypatch,tmp_path,required,success):
    from ara.runtime.construction_fork import inspect_construction_fork,write_construction_fork
    from ara.runtime.alignment_resume import load_alignment_resume
    from ara.runtime.orchestration import prepare_commitments
    from ara.runtime.search_alignment import catalogue_inputs
    calls=rig[0];finish_source(calls,monkeypatch);bank=load_bank(ROOT/'bank')
    h=dict(id='hypothesis:h',text='F(a)',proposer='operator',rationale='P',linked_gap='P',linked_target=None,
           existing_symbols=required,formula=dict(op='predicate',name='V0_0',terms=[dict(kind='constant',name='V0_1')]))
    plan=inspect_construction_fork(calls.log.path.parent,tmp_path/'h-fork',bank,[h],consolidation=options())
    log=write_construction_fork(plan);state=load_alignment_resume(log,bank)
    new=ModelCalls(state['run']['config'],calls.provider,log,Cache(tmp_path/'h-cache'),ROOT,'P')
    new.alignment_resume=state;provider(new,monkeypatch)
    if not success:
        with pytest.raises(ValueError,match='existing symbol'):prepare_commitments(new,bank,'P','P')
        assert not (log.path.parent/'commitments.json').exists()
    else:
        t=prepare_commitments(new,bank,'P','P');meta=catalogue_inputs(log.path.parent,t)['commitment_provenance']
        assert meta['schema_version']=='commitment-provenance-v5'
        assert meta['commitments']['hypothesis:h']['stance']=='proposed'
        assert meta['hypotheses'] and meta['consolidation']


def test_interrupted_batches_resume_from_validated_cache(rig,monkeypatch,tmp_path):
    from ara.runtime.vocabulary_consolidation import consolidate
    from test_symbol_alignment import fixture
    calls=rig[0];calls.config.update(options());t,symbols,rows=fixture();requests=provider(calls,monkeypatch)
    call=calls.call
    def interrupted(kind,inputs,check):
        if inputs.get('batch_index')==1:raise RuntimeError('P')
        return call(kind,inputs,check)
    monkeypatch.setattr(calls,'call',interrupted)
    with pytest.raises(RuntimeError):consolidate(calls,t,symbols,rows,'P')
    assert not (calls.log.path.parent/'vocabulary-consolidation.json').exists()
    monkeypatch.setattr(calls,'call',call)
    result=consolidate(calls,t,symbols,rows,'P')
    assert len(requests)==2 and len(result[0].commitments)==3


@pytest.mark.parametrize('key', ['working_t_token_budget','working_t_symbol_token_budget','model_context_token_bound'])
def test_consolidation_capacity_refuses(rig,monkeypatch,key):
    from ara.runtime.vocabulary_consolidation import consolidate
    from test_symbol_alignment import fixture
    calls=rig[0];calls.config.update(options());calls.config[key]=1;provider(calls,monkeypatch)
    from ara.runtime.budget import BudgetStop
    reason={'working_t_token_budget':'working T capacity', 'working_t_symbol_token_budget':'catalogue capacity',
            'model_context_token_bound':'context bound'}[key]
    with pytest.raises((ValueError,BudgetStop),match=reason):consolidate(calls,*fixture(),'P')
    assert not any(e['stage']=='vocabulary_consolidated' for e in calls.log.read())


def test_topic_plan_preserves_inference_components():
    from ara.runtime.vocabulary_consolidation import make_plan
    from test_symbol_alignment import fixture
    t,symbols,rows=fixture()
    items={id:dict(id=id,kind='premise',premise_ids=[],conclusion_id=None,qualification_ids=[],applies_to=[]) for id in rows}
    items['R'].update(kind='inference',premise_ids=['P'],conclusion_id='Q')
    with pytest.raises(ValueError,match='component exceeds'):make_plan(t,symbols,rows,options(),items)
    config=options();config['consolidation_batch_size']=3
    plan=make_plan(t,symbols,rows,config,items)
    assert plan['batches']==[['P','Q','R']]


@pytest.mark.parametrize('relation', ['same_content', 'entails_left_right'])
def test_consolidation_alignment_and_hypothesis_refork(rig,monkeypatch,tmp_path,relation):
    calls=rig[0];finish_source(calls,monkeypatch)
    from ara.runtime.construction_fork import inspect_construction_fork,write_construction_fork
    from ara.runtime.alignment_resume import load_alignment_resume
    from ara.runtime.orchestration import prepare_commitments
    from ara.runtime.search_alignment import catalogue_inputs
    bank=load_bank(ROOT/'bank')
    plan=inspect_construction_fork(calls.log.path.parent,tmp_path/'aligned',bank,[],consolidation=options())
    log=write_construction_fork(plan);state=load_alignment_resume(log,bank)
    new=ModelCalls(state['run']['config'],calls.provider,log,Cache(tmp_path/'aligned-cache'),ROOT,'P')
    new.alignment_resume=state
    def separate_symbol(data,inputs):
        if inputs['batch_index']==1:
            for f in data['formulas']:f['name']='n0'
            data['new_symbols']=[dict(kind='predicate',arity=1,definition='F(a)')]
            data['reuse']=[dict(handle='s1',reason='a')]
    provider(new,monkeypatch,separate_symbol);complete=new.provider.complete
    def judge(kind,prompt,schema,maximum):
        if kind=='judge_symbol_alignment':return Response(response(dict(relation=relation,reason='F(a)')))
        return complete(kind,prompt,schema,maximum)
    monkeypatch.setattr(new.provider,'complete',judge)
    t=prepare_commitments(new,bank,'P','P')
    meta=catalogue_inputs(log.path.parent,t)['commitment_provenance']
    assert meta['alignment']['judgments'][0]['relation']==relation
    assert meta['consolidation']['after']['shared_symbols']==2
    h=dict(id='hypothesis:h',text='F(a)',proposer='operator',rationale='P',linked_gap='P',linked_target=None,
           existing_symbols=['V0_0','V0_1'],formula=dict(op='predicate',name='V0_0',terms=[dict(kind='constant',name='V0_1')]))
    fork=inspect_construction_fork(log.path.parent,tmp_path/'after-h',bank,[h])
    fork_log=write_construction_fork(fork);fork_state=load_alignment_resume(fork_log,bank)
    h_calls=ModelCalls(fork_state['run']['config'],calls.provider,fork_log,Cache(tmp_path/'after-h-cache'),ROOT,'P')
    h_calls.alignment_resume=fork_state
    monkeypatch.setattr(h_calls.provider,'complete',lambda *a:pytest.fail('validated consolidation and alignment must replay'))
    result=prepare_commitments(h_calls,bank,'P','P')
    h_meta=catalogue_inputs(fork_log.path.parent,result)['commitment_provenance']
    assert h_meta['consolidation']==meta['consolidation']
    assert h_meta['commitments']['hypothesis:h']['stance']=='proposed'


def test_native_consolidation_preserves_historical_unframes(rig,monkeypatch):
    from test_symbol_alignment import fixture
    from ara.runtime.orchestration import prepare_commitments
    from ara.runtime.search_alignment import catalogue_inputs
    calls=rig[0];calls.config.update(options());t,symbols,rows=fixture()
    rows['Q']['definition_unframes']=[dict(kind='symbol',name='Q',author='b',original_definition='b holds that P Q',definition='P Q')]
    monkeypatch.setattr(calls,'build_t',lambda *_:t)
    calls.log.record('build_t_merged',commitments=t.to_dict(),symbols=symbols,provenance=rows)
    provider(calls,monkeypatch)
    result=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    meta=catalogue_inputs(calls.log.path.parent,result)['commitment_provenance']
    assert meta['commitments']['Q']['definition_unframes']==rows['Q']['definition_unframes']


def test_consolidation_refuses_disconnected_conditional(rig,monkeypatch):
    from test_symbol_alignment import fixture
    from ara.runtime.vocabulary_consolidation import consolidate
    calls=rig[0];calls.config.update(options());calls.config['consolidation_batch_size']=3
    t,symbols,rows=fixture()
    items={id:dict(id=id,kind='premise',premise_ids=[],conclusion_id=None,qualification_ids=[],applies_to=[]) for id in rows}
    items['R'].update(kind='inference',premise_ids=['P'],conclusion_id='Q')
    def disconnected(data,inputs):
        i=next(i for i,c in enumerate(inputs['accepted_commitments']['commitments']) if c['id']=='R')
        f=data['formulas'][i]
        data['formulas'][i]=dict(op='implies',args=[f,dict(op='implies',args=[f,f])])
    provider(calls,monkeypatch,disconnected)
    with pytest.raises(ValueError,match='conditional endpoint mismatch'):
        consolidate(calls,t,symbols,rows,items)
    assert not any(e['stage']=='vocabulary_consolidated' for e in calls.log.read())


def test_h_only_refork_must_not_reinterpret_consolidated_source(rig,monkeypatch,tmp_path):
    relation="entails_left_right"
    calls=rig[0];finish_source(calls,monkeypatch)
    from ara.runtime.construction_fork import inspect_construction_fork,write_construction_fork
    from ara.runtime.alignment_resume import load_alignment_resume
    from ara.runtime.orchestration import prepare_commitments
    from ara.runtime.search_alignment import catalogue_inputs
    bank=load_bank(ROOT/'bank')
    plan=inspect_construction_fork(calls.log.path.parent,tmp_path/'aligned',bank,[],consolidation=options())
    log=write_construction_fork(plan);state=load_alignment_resume(log,bank)
    new=ModelCalls(state['run']['config'],calls.provider,log,Cache(tmp_path/'aligned-cache'),ROOT,'P')
    new.alignment_resume=state
    def separate_symbol(data,inputs):
        if inputs['batch_index']==1:
            for f in data['formulas']:f['name']='n0'
            data['new_symbols']=[dict(kind='predicate',arity=1,definition='F(a)')]
            data['reuse']=[dict(handle='s1',reason='a')]
    provider(new,monkeypatch,separate_symbol);complete=new.provider.complete
    def judge(kind,prompt,schema,maximum):
        if kind=='judge_symbol_alignment':return Response(response(dict(relation=relation,reason='F(a)')))
        return complete(kind,prompt,schema,maximum)
    monkeypatch.setattr(new.provider,'complete',judge)
    import ara.runtime.symbol_alignment as alignment
    apply=alignment.apply_judgments
    def unavailable(*args):raise ValueError(alignment.CONSISTENCY_REFUSAL)
    monkeypatch.setattr(alignment,'apply_judgments',unavailable)
    t=prepare_commitments(new,bank,'P','P')
    meta=catalogue_inputs(log.path.parent,t)['commitment_provenance']
    assert meta['alignment']['judgments'][0]['relation']==relation
    assert meta['alignment']['status']=='refused'
    monkeypatch.setattr(alignment,'apply_judgments',apply)
    assert meta['consolidation']['after']['shared_symbols']==2
    h=dict(id='hypothesis:h',text='F(a)',proposer='operator',rationale='P',linked_gap='P',linked_target=None,
           existing_symbols=['V0_0','V0_1'],formula=dict(op='predicate',name='V0_0',terms=[dict(kind='constant',name='V0_1')]))
    fork=inspect_construction_fork(log.path.parent,tmp_path/'after-h',bank,[h])
    fork_log=write_construction_fork(fork);fork_state=load_alignment_resume(fork_log,bank)
    h_calls=ModelCalls(fork_state['run']['config'],calls.provider,fork_log,Cache(tmp_path/'after-h-cache'),ROOT,'P')
    h_calls.alignment_resume=fork_state
    monkeypatch.setattr(h_calls.provider,'complete',lambda *a:pytest.fail('validated consolidation and alignment must replay'))
    with pytest.raises(ValueError,match='construction fork changed source'):
        prepare_commitments(h_calls,bank,'P','P')
    assert not (fork_log.path.parent/'commitments.json').exists()


def test_native_stop_at_freeze_excludes_targets_and_search(rig,monkeypatch,tmp_path):
    from ara.runtime import cli
    from ara.runtime.logging import EventLog
    from ara.runtime.freeze_fork import fork_from_freeze
    from ara.runtime.search_alignment import catalogue_inputs
    calls=rig[0];finish_source(calls,monkeypatch);source=calls.log.path.parent
    before=snapshot(source);provider(calls,monkeypatch)
    settings=tmp_path/'settings.json';settings.write_text(canonical(options()))
    destination=tmp_path/'freeze-only'
    def factory(config,log,topic):
        result=ModelCalls(config,calls.provider,log,Cache(destination/'cache'),ROOT,topic)
        monkeypatch.setattr(result,'propose_targets',lambda *a:pytest.fail('freeze stop must not propose targets'))
        return result
    monkeypatch.setattr(cli,'search_all',lambda *a:pytest.fail('freeze stop must not search'))
    assert main(['resume-alignment','--source-run',str(source),'--run-dir',str(destination),
                 '--consolidation-config',str(settings),'--stop-at','freeze'],calls_factory=factory)==0
    events=EventLog(destination/'events.jsonl').read();stages=[e['stage'] for e in events]
    assert stages.count('commitments_frozen')==1
    assert stages.index('vocabulary_consolidated')<stages.index('symbol_alignment_candidates')<stages.index('commitments_frozen')<stages.index('run_stopped_at_freeze')
    assert not {'candidates','search_started','awaiting_selection'} & set(stages)
    assert json.loads(next(e['payload_json'] for e in events if e['stage']=='run_stopped_at_freeze'))['controller']=='native_cli'
    assert 'run_stopped_at_freeze' in (destination/'export'/'methodology.md').read_text()
    fork=tmp_path/'fork-check';log,run,t=fork_from_freeze(destination,fork,load_bank(ROOT/'bank'))
    assert catalogue_inputs(fork,t)['commitment_provenance']['schema_version']=='commitment-provenance-v5'
    assert sum(e['stage']=='commitments_frozen' for e in log.read())==1
    assert snapshot(source)==before
