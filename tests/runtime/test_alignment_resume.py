"""Exact candidate identity, bounded unresolved outcomes and native continuation."""
from copy import deepcopy
import json

import pytest

from ara.bank import load_bank
from ara.runtime.cache import canonical, digest, Cache
from ara.runtime.calls import ModelCalls, Rejected
from ara.runtime.commitment_provenance import make_commitment_provenance
from ara.runtime.frozen_catalogue import make_catalogue
from ara.runtime.providers import Response
from test_extraction import rig, ROOT, response
from test_symbol_alignment import fixture, judgment


def judge(calls, monkeypatch, invalid_first=False):
    sent=[]
    def complete(kind,prompt,schema,maximum):
        assert kind=='judge_symbol_alignment'
        value=json.loads(prompt.split('\nINPUT_JSON\n')[1]);sent.append(value)
        pair=value['candidate']
        data=dict(relation='entails_left_right',reason='P Q')
        if invalid_first and pair['left']['name']=='P' and pair['right']['name']=='Q':
            data.update(left='P',right='R')
        return Response(response(data))
    monkeypatch.setattr(calls.provider,'complete',complete)
    return sent


def test_mutated_id_is_unresolved_and_never_changes_candidate(rig,monkeypatch,tmp_path):
    from ara.runtime.symbol_alignment import align_symbols
    from ara.runtime.report import generate_report
    calls=rig[0];calls.config.update(validation_attempts=2,construction_alignment_max_unresolved=1)
    sent=judge(calls,monkeypatch,True)
    t,symbols,rows=fixture()
    result,final_symbols,final_rows,receipt=align_symbols(calls,t,symbols,rows)
    assert len(sent)==4
    assert [(j['left'],j['right']) for j in receipt['judgments']]==[('P','R'),('Q','R')]
    assert len(result.commitments)==5
    assert receipt['unresolved']==[dict(left='P',right='Q',status='alignment_unresolved',
        reason=receipt['unresolved'][0]['reason'],attempts=2)]
    assert receipt['unresolved'][0]['reason']
    meta=make_commitment_provenance(result,make_catalogue(result,final_symbols),final_rows,alignment=receipt)
    altered=deepcopy(receipt);altered['unresolved'][0]['right']='R'
    with pytest.raises(ValueError):
        make_commitment_provenance(result,make_catalogue(result,final_symbols),final_rows,alignment=altered)
    assert meta['alignment']['unresolved_limit']==1
    events=calls.log.read()
    assert sum(e['stage']=='alignment_unresolved' for e in events)==1
    invalid=[e for e in events if e['stage']=='judge_symbol_alignment' and json.loads(e['payload_json'])['status']=='rejected']
    assert len(invalid)==2 and all(json.loads(Response(json.loads(e['response'])).text())['right']=='R' for e in invalid)
    generate_report([calls.log.path.parent],tmp_path/'report')
    report=json.loads((tmp_path/'report/data.json').read_text())['runs'][0]['construction']['alignment']
    assert report['unresolved_count']==1 and report['unresolved'][0]['status']=='alignment_unresolved'


def test_unresolved_threshold_refuses_before_freeze(rig,monkeypatch):
    from ara.runtime.orchestration import prepare_commitments
    calls=rig[0];calls.config['construction_alignment_max_unresolved']=0
    judge(calls,monkeypatch,True)
    t,symbols,rows=fixture()
    monkeypatch.setattr(calls,'build_t',lambda *_:t)
    calls.log.record('build_t_merged',commitments=t.to_dict(),symbols=symbols,provenance=rows)
    with pytest.raises(Rejected,match='unresolved limit'):
        prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert not (calls.log.path.parent/'commitments.json').exists()
    assert any(e['stage']=='symbol_alignment_incomplete' for e in calls.log.read())


def completed(calls):
    """Recorded terminal windows and immutable artifact, all placeholder content."""
    t,symbols,rows=fixture()
    plan=dict(version='rich-working-t-v14',batches=[dict(index=i) for i in range(3)])
    plan_id=digest(canonical(plan));directory=calls.log.path.parent
    calls.log.record('run_started',config=calls.config,topic='P',literature='P',audience='P',bank_version=load_bank(ROOT/'bank').bank_version)
    calls.log.record('build_t_plan',plan_id=plan_id,plan=plan)
    (directory/f'build-t-plan-{plan_id}.json').write_text(canonical(plan))
    for i,c in enumerate(t.commitments):
        data=dict(commitments=[c.to_dict()],new_symbols=[symbols[i]],provenance={c.id:rows[c.id]},omitted=[])
        (directory/f'build-t-{plan_id}-{i}.json').write_text(canonical(data))
        calls.log.record('build_t_batch_accepted',plan_id=plan_id,index=i,output_hash=digest(canonical(data)),evidence_ids=[c.id],omitted=[])
    merged=dict(plan_id=plan_id,commitments=t.to_dict(),symbols=symbols,provenance=rows)
    calls.log.record('build_t_merged',**merged)
    (directory/f'working-t-{plan_id}.json').write_text(canonical(merged))
    return t,symbols,rows


def legacy_stop(calls):
    from ara.runtime.symbol_alignment import candidate_inventory
    from ara.types import RunEvent, TokenUsage
    from ara.runtime.logging import now
    t,symbols,rows=completed(calls)
    catalogue=make_catalogue(t,symbols);inventory=candidate_inventory(symbols,rows)
    candidates=inventory.pop('candidates')
    calls.log.record('symbol_alignment_candidates',policy_version='cross-source-symbol-alignment-v2',limit=150,
        candidates=candidates,retrieval=inventory,commitments_sha256=catalogue['commitments_sha256'],catalogue_sha256=catalogue['sha256'])
    for pair,status in [(candidates[0],'accepted'),(candidates[1],'rejected')]:
        names={s['name']:s for s in symbols}
        inputs=dict(topic='',policy_version='cross-source-symbol-alignment-v2',candidate=dict(left=names[pair['left']],right=names[pair['right']],score=pair['score']),
            sources={id:rows[id] for id in sorted(set(names[pair['left']]['evidence_ids']+names[pair['right']]['evidence_ids']))},
            commitments_sha256=catalogue['commitments_sha256'],catalogue_sha256=catalogue['sha256'])
        value=judgment(pair['left'],pair['right'],'entails_left_right')
        if status=='rejected':value['right']='Q'
        calls.log.emit(RunEvent(now(),'judge_symbol_alignment','MODEL',model_id='claude-opus-5',model_version='claude-opus-5',prompt='P\nINPUT_JSON\n'+canonical(inputs),
            response=canonical(response(value)),usage=TokenUsage(),payload_json=canonical(dict(status=status,cache_hit=True,attempt=1))))
    return t,symbols,rows


def test_resume_plan_has_no_factory_or_calls_and_preserves_source(rig,monkeypatch,tmp_path,capsys):
    from ara.runtime.cli import main
    calls=rig[0];legacy_stop(calls)
    directory=calls.log.path.parent
    before={p.name:p.read_bytes() for p in directory.iterdir() if p.is_file()}
    def forbidden(*a):raise AssertionError('plan must not construct a provider')
    out=tmp_path/'plan'
    assert main(['resume-alignment','--run-dir',str(directory),'--plan-only','--output-dir',str(out)],calls_factory=forbidden)==0
    plan=json.loads((out/'alignment-resume-plan.json').read_text())
    assert plan['completed_windows']==3 and plan['restored_commitments']==3
    assert plan['accepted_judgments']==1 and plan['remaining_candidates']==2
    assert plan['generation_calls']==0
    assert all((directory/name).read_bytes()==data for name,data in before.items())


def test_resume_reuses_accepted_judgments_and_freezes_once(rig,monkeypatch,tmp_path):
    from ara.runtime.cli import main
    calls=rig[0];legacy_stop(calls)
    sent=judge(calls,monkeypatch)
    def factory(config,log,topic):
        resumed=ModelCalls(config,calls.provider,log,Cache(tmp_path/'resume-cache'),ROOT,topic)
        monkeypatch.setattr(resumed,'build_t',lambda *_:pytest.fail('construction must not replay'))
        monkeypatch.setattr(resumed,'propose_targets',lambda *a:())
        return resumed
    args=['resume-alignment','--run-dir',str(calls.log.path.parent)]
    assert main(args,calls_factory=factory)==0
    assert [(i['candidate']['left']['name'],i['candidate']['right']['name']) for i in sent]==[('P','R'),('Q','R')]
    stages=[e['stage'] for e in calls.log.read()]
    assert stages.count('build_t_merged')==1 and stages.count('commitments_frozen')==1
    assert 'candidates' in stages and 'run_finished' in stages
    assert main(args,calls_factory=factory)==2
    assert len(sent)==2


@pytest.mark.parametrize('damage',['batch','working','incomplete','interrupted','frozen'])
def test_resume_refuses_damaged_or_incomplete_state_before_provider(rig,monkeypatch,tmp_path,damage):
    from ara.runtime.cli import main
    calls=rig[0];completed(calls);directory=calls.log.path.parent
    if damage=='batch':next(directory.glob('build-t-*-0.json')).write_text('{}')
    elif damage=='working':next(directory.glob('working-t-*.json')).write_text('{}')
    elif damage=='incomplete':next(directory.glob('build-t-*-2.json')).unlink()
    elif damage=='interrupted':calls.log.record('call_start',kind='judge_symbol_alignment',cache_key='P')
    else:(directory/'commitments.json').write_text('{}')
    created=[]
    def forbidden(*a):
        created.append(True)
        raise AssertionError('unverified state must not construct provider')
    assert main(['resume-alignment','--run-dir',str(directory)],calls_factory=forbidden)==2
    assert created==[]


def test_binding_rejects_even_an_echoed_mutated_identity():
    from ara.runtime.symbol_alignment import bind_judgment
    candidate=dict(left='P',right='Q',score=1.0)
    assert bind_judgment(dict(relation='same_content',reason='P Q'),candidate)==judgment()
    with pytest.raises(Rejected,match='only relation and reason'):
        bind_judgment(judgment('P','R'),candidate)


def test_native_completed_construction_is_not_replayed(rig,monkeypatch,tmp_path):
    from ara.runtime.cli import main
    from test_construction_shares import windows
    calls,provider,literature,sent=windows(rig,monkeypatch)
    calls.log.record('run_started',config=calls.config,topic='P',literature=literature,audience='',bank_version=load_bank(ROOT/'bank').bank_version)
    original=calls.build_t(literature,'')
    prior=list(sent)
    def factory(config,log,topic):
        resumed=ModelCalls(config,provider,log,Cache(tmp_path/'resume-cache'),ROOT,topic)
        monkeypatch.setattr(resumed,'propose_targets',lambda *a:())
        return resumed
    assert main(['resume-alignment','--run-dir',str(calls.log.path.parent)],calls_factory=factory)==0
    assert sent==prior
    assert json.loads((calls.log.path.parent/'commitments.json').read_text())==original.to_dict()


def test_unresolved_receipt_without_rejected_attempts_cannot_resume(rig):
    from ara.runtime.alignment_resume import load_alignment_resume
    from ara.runtime.symbol_alignment import candidate_inventory, POLICY_VERSION
    calls=rig[0];t,symbols,rows=completed(calls)
    catalogue=make_catalogue(t,symbols);inventory=candidate_inventory(symbols,rows)
    candidates=inventory.pop('candidates')
    calls.log.record('symbol_alignment_candidates',policy_version=POLICY_VERSION,limit=150,
        candidates=candidates,retrieval=inventory,commitments_sha256=catalogue['commitments_sha256'],catalogue_sha256=catalogue['sha256'])
    calls.log.record('alignment_unresolved',left='P',right='Q',status='alignment_unresolved',reason='P',attempts=1)
    with pytest.raises(Rejected,match='rejected attempts'):
        load_alignment_resume(calls.log,load_bank(ROOT/'bank'))


def test_provider_failure_is_not_an_unresolved_judgment(rig,monkeypatch):
    from ara.runtime.symbol_alignment import align_symbols
    from ara.runtime.budget import BudgetStop
    calls=rig[0]
    def failed(*args):raise RuntimeError('P')
    monkeypatch.setattr(calls.provider,'complete',failed)
    with pytest.raises(BudgetStop):align_symbols(calls,*fixture())
    assert not any(e['stage']=='alignment_unresolved' for e in calls.log.read())


def test_resume_continues_native_forward_targets_and_search(rig,monkeypatch,tmp_path):
    from ara.runtime.cli import main
    calls=rig[0]
    calls.config.update(depth_cap=1,node_cap=12,forward_pass_depth=1,semantic_conflict_pair_limit=0)
    legacy_stop(calls)
    sent=[]
    def complete(kind,prompt,schema,maximum):
        sent.append(kind)
        if kind=='judge_symbol_alignment':data=dict(relation='unrelated',reason='P Q')
        elif kind=='classify_conflict':data=dict(classification='compatible',reason='P Q')
        elif kind=='propose_targets':data=dict(targets=[dict(id='s',text='S',formula=dict(op='atom',name='S'))])
        elif kind=='classify_target':data=dict(classification='own_thesis',novelty='new_assertion',fidelity='matches',reason='S')
        elif kind=='map_leaf':data=dict(t_id='open')
        elif kind=='propose_cuts':data=dict(proposals=[])
        elif kind=='tier1_repair':data=dict(action='unresolved',detail='P',proposals=[])
        else:raise AssertionError(kind)
        return Response(response(data))
    monkeypatch.setattr(calls.provider,'complete',complete)
    def factory(config,log,topic):return ModelCalls(config,calls.provider,log,Cache(tmp_path/'fresh'),ROOT,topic)
    assert main(['resume-alignment','--run-dir',str(calls.log.path.parent)],calls_factory=factory)==0
    stages=[e['stage'] for e in calls.log.read()]
    assert stages.index('commitments_frozen')<stages.index('forward_target_candidates')<stages.index('candidates')<stages.index('analysis_started')
    assert 'propose_targets' in sent and 'map_leaf' in sent
    assert 'build_t_batch' not in sent and 'select_t_roots' not in sent
    assert stages.count('commitments_frozen')==1


def test_policy_v2_frozen_receipt_still_loads(rig,monkeypatch):
    from ara.runtime.symbol_alignment import align_symbols
    from test_symbol_alignment import configure_judge
    calls,_=configure_judge(rig,monkeypatch,'unrelated')
    result,symbols,rows,receipt=align_symbols(calls,*fixture())
    receipt['policy_version']='cross-source-symbol-alignment-v2'
    del receipt['unresolved'];del receipt['unresolved_limit']
    assert make_commitment_provenance(result,make_catalogue(result,symbols),rows,alignment=receipt)['alignment']==receipt


def test_resume_retains_explicit_unresolved_without_retrying_it(rig,monkeypatch,tmp_path):
    from ara.runtime.symbol_alignment import align_symbols
    from ara.runtime.cli import main
    calls=rig[0];calls.config.update(validation_attempts=2,construction_alignment_max_unresolved=1)
    t,symbols,rows=completed(calls)
    sent=judge(calls,monkeypatch,True)
    real_call=calls.call
    def interrupted(kind,inputs,check=None):
        if inputs['candidate']['right']['name']=='R':raise Rejected('P')
        return real_call(kind,inputs,check)
    monkeypatch.setattr(calls,'call',interrupted)
    with pytest.raises(Rejected,match='P'):align_symbols(calls,t,symbols,rows)
    assert len(sent)==2
    def factory(config,log,topic):
        resumed=ModelCalls(config,calls.provider,log,Cache(tmp_path/'fresh'),ROOT,topic)
        monkeypatch.setattr(resumed,'propose_targets',lambda *a:())
        return resumed
    assert main(['resume-alignment','--run-dir',str(calls.log.path.parent)],calls_factory=factory)==0
    assert len(sent)==4
    meta=json.loads((calls.log.path.parent/'commitment-provenance.json').read_text())
    assert len(meta['alignment']['unresolved'])==1
    assert len(meta['alignment']['judgments'])==2
    assert sum(e['stage']=='alignment_unresolved' for e in calls.log.read())==1
