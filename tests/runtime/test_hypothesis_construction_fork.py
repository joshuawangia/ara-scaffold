"""New H lifecycle reuses verified construction and exact existing vocabulary."""
import json

import pytest

from ara.bank import load_bank
from ara.runtime.cache import Cache, canonical
from ara.runtime.calls import ModelCalls
from ara.runtime.cli import main
from ara.runtime.logging import EventLog
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.providers import Response
from ara.types import Formula
from test_alignment_resume import completed, legacy_stop
from test_extraction import rig, ROOT, response


def entry():
    return dict(id='hypothesis:h',text='P implies Q',rationale='P Q',proposer='operator',
                linked_gap='g',linked_target=None,formalization_request='P implies Q',
                existing_symbols=['P','Q'])


def snapshot(directory):
    return {str(p.relative_to(directory)):p.read_bytes() for p in directory.rglob('*') if p.is_file()}


def finish_source(calls,monkeypatch):
    t,_,_=completed(calls)
    monkeypatch.setattr(calls,'build_t',lambda *_:t)
    monkeypatch.setattr(calls.provider,'complete',lambda *a:Response(response(dict(relation='unrelated',reason='P Q'))))
    return prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')


def test_completed_fork_adds_bound_h_without_reconstruction(rig,monkeypatch,tmp_path):
    calls=rig[0];frozen=finish_source(calls,monkeypatch)
    directory=calls.log.path.parent;before=snapshot(directory)
    requested=[]
    def complete(kind,prompt,schema,maximum):
        assert kind=='formalise', 'construction and accepted alignment must not dispatch'
        value=json.loads(prompt.split('\nINPUT_JSON\n')[1]);requested.append(value)
        assert [s['name'] for s in value['required_existing_symbols']]==['P','Q']
        return Response(response(dict(formula=Formula('implies',(Formula('atom',name='P'),Formula('atom',name='Q'))).to_dict())))
    monkeypatch.setattr(calls.provider,'complete',complete)
    def factory(config,log,topic):
        result=ModelCalls(config,calls.provider,log,Cache(tmp_path/'new-cache'),ROOT,topic)
        monkeypatch.setattr(result,'build_t',lambda *_:pytest.fail('must not reconstruct'))
        monkeypatch.setattr(result,'propose_targets',lambda *a:())
        return result
    hypotheses=tmp_path/'hypotheses.json';hypotheses.write_text(canonical([entry()]))
    destination=tmp_path/'fork'
    args=['resume-alignment','--source-run',str(directory),'--run-dir',str(destination),'--hypotheses-file',str(hypotheses)]
    assert main(args,calls_factory=factory)==0
    assert snapshot(directory)==before
    assert len(requested)==1
    from ara.types import CommitmentSet
    from ara.runtime.search_alignment import catalogue_inputs
    t=CommitmentSet.from_json((destination/'commitments.json').read_text())
    assert tuple(c for c in t.commitments if c.id!='hypothesis:h')==frozen.commitments
    metadata=catalogue_inputs(destination,t)
    assert metadata['hypothesis_disclosure']['conditional_on']==['hypothesis:h']
    assert metadata['commitment_provenance']['commitments']['hypothesis:h']['stance']=='proposed'
    source_catalogue=json.loads(before['frozen-t.json'])['symbol_catalogue']
    new_catalogue=json.loads((destination/'frozen-t.json').read_text())['symbol_catalogue']
    assert new_catalogue['symbols']==source_catalogue['symbols']
    events=EventLog(destination/'events.jsonl').read()
    assert sum(e['stage']=='commitments_frozen' for e in events)==1
    assert sum(e['stage']=='build_t_merged' for e in events)==1
    assert any(e['stage']=='construction_forked' for e in events)
    assert any(e['stage']=='hypotheses_admitted' for e in events)
    from ara.runtime.freeze_fork import effective_run
    assert effective_run(events)['config']['hypothesis_premises']==[entry()]
    # Mandatory runtime disclosure continues to refuse an undisclosed essay.
    from ara.runtime.hypotheses import insert_runtime_disclosure, validate_disclosure, route_hypothesis_disclosure
    from ara.types import Proposition, RouteGraph, RouteNode
    h=t.get('hypothesis:h')
    route=RouteGraph('r','h',(RouteNode('h',Proposition('h',h.text,h.formula),'leaf',t_id=h.id),))
    disclosure=route_hypothesis_disclosure(route,metadata['commitment_provenance'])
    assert disclosure['conclusion_status']=='conditional on H; no completed conclusion'
    draft=dict(title='P',body='[[node:h]] This paper proposes P implies Q.',bibliography=[])
    with pytest.raises(ValueError,match='runtime block'):
        validate_disclosure(events,route,draft)
    resumed=factory(effective_run(events)['config'],EventLog(destination/'events.jsonl'),'P')
    disclosed=insert_runtime_disclosure(resumed,route,draft)
    validate_disclosure(resumed.log.read(),route,disclosed)
    assert 'conditional on H (hypothesis:h)' in disclosed['body']


def test_fork_plan_only_is_read_only_and_preserves_partial_alignment(rig,tmp_path):
    calls=rig[0];legacy_stop(calls);source=calls.log.path.parent;before=snapshot(source)
    hypotheses=tmp_path/'hypotheses.json';hypotheses.write_text(canonical([entry()]))
    destination=tmp_path/'planned-fork';output=tmp_path/'plan'
    assert main(['resume-alignment','--source-run',str(source),'--run-dir',str(destination),
                 '--hypotheses-file',str(hypotheses),'--plan-only','--output-dir',str(output)],
                calls_factory=lambda *a:pytest.fail('plan constructed a provider'))==0
    assert snapshot(source)==before and not destination.exists()
    plan=json.loads((output/'alignment-resume-plan.json').read_text())
    assert plan['accepted_judgments']==1 and plan['remaining_candidates']==2
    assert plan['hypothesis_ids']==['hypothesis:h'] and plan['generation_calls']==0


@pytest.mark.parametrize('damage',['batch','frozen','symbols'])
def test_fork_refuses_corruption_before_provider(rig,monkeypatch,tmp_path,damage):
    calls=rig[0];finish_source(calls,monkeypatch);source=calls.log.path.parent
    value=entry()
    if damage=='batch':next(source.glob('build-t-*-0.json')).write_text('{}')
    elif damage=='frozen':(source/'frozen-t.json').write_text('{}')
    else:value['existing_symbols']=['missing']
    hypotheses=tmp_path/'hypotheses.json';hypotheses.write_text(canonical([value]))
    before=snapshot(source);destination=tmp_path/'bad-fork'
    assert main(['resume-alignment','--source-run',str(source),'--run-dir',str(destination),'--hypotheses-file',str(hypotheses)],
                calls_factory=lambda *a:pytest.fail('invalid fork created provider'))==2
    assert snapshot(source)==before and not destination.exists()


def test_h_formalization_cannot_ignore_required_existing_symbol(rig,monkeypatch):
    from ara.runtime.hypotheses import admit_hypotheses
    from ara.runtime.calls import InvalidOutput
    from test_symbol_alignment import fixture
    calls=rig[0];calls.config['hypothesis_premises']=[entry()]
    monkeypatch.setattr(calls.provider,'complete',lambda *a:Response(response(dict(formula=Formula('atom',name='P').to_dict()))))
    with pytest.raises(InvalidOutput):
        admit_hypotheses(calls,*fixture())
    assert not any(e['stage']=='hypotheses_admitted' for e in calls.log.read())


def test_source_changed_on_replay_refuses_before_h(rig,monkeypatch,tmp_path):
    from dataclasses import replace
    from ara.runtime import symbol_alignment
    from ara.types import CommitmentSet
    calls=rig[0];finish_source(calls,monkeypatch);source=calls.log.path.parent
    original=symbol_alignment.align_symbols
    def altered(*args):
        t,symbols,rows,receipt=original(*args)
        return CommitmentSet((replace(t.commitments[0],text='Q P'),*t.commitments[1:])),symbols,rows,receipt
    monkeypatch.setattr(symbol_alignment,'align_symbols',altered)
    value=entry();value.pop('formalization_request');value['formula']=Formula('implies',(Formula('atom',name='P'),Formula('atom',name='Q'))).to_dict()
    hypotheses=tmp_path/'hypotheses.json';hypotheses.write_text(canonical([value]))
    destination=tmp_path/'changed-source'
    def factory(config,log,topic):
        result=ModelCalls(config,calls.provider,log,Cache(tmp_path/'new-cache'),ROOT,topic)
        monkeypatch.setattr(result,'propose_targets',lambda *a:())
        return result
    assert main(['resume-alignment','--source-run',str(source),'--run-dir',str(destination),
                 '--hypotheses-file',str(hypotheses)],calls_factory=factory)==2
    assert not (destination/'commitments.json').exists()
    assert not any(e['stage']=='hypotheses_admitted' for e in EventLog(destination/'events.jsonl').read())


@pytest.mark.parametrize('names',[['missing'],['P','P'],'P'])
def test_invalid_required_symbol_names_refuse(rig,names):
    from ara.runtime.hypotheses import admit_hypotheses
    from test_symbol_alignment import fixture
    value=entry();value['existing_symbols']=names
    rig[0].config['hypothesis_premises']=[value]
    with pytest.raises(ValueError,match='existing symbol'):
        admit_hypotheses(rig[0],*fixture())


@pytest.mark.parametrize('change',['append','rewrite'])
def test_fork_snapshot_tolerates_only_later_appends(rig,monkeypatch,tmp_path,change):
    from ara.runtime import construction_fork
    calls=rig[0];finish_source(calls,monkeypatch);source=calls.log.path.parent
    original=construction_fork._load_alignment_resume
    def after_snapshot(*args):
        state=original(*args)
        if change=='append':calls.log.record('later_search_progress',detail='P')
        else:
            text=calls.log.path.read_text()
            calls.log.path.write_text(text.replace('run_started','run_changed',1))
        return state
    monkeypatch.setattr(construction_fork,'_load_alignment_resume',after_snapshot)
    if change=='rewrite':
        with pytest.raises(ValueError,match='source changed'):
            construction_fork.inspect_construction_fork(source,tmp_path/'new',load_bank(ROOT/'bank'),[entry()])
    else:
        plan=construction_fork.inspect_construction_fork(source,tmp_path/'new',load_bank(ROOT/'bank'),[entry()])
        assert plan['state']['judgments'] and plan['state']['expected_source'] is not None
        assert all(r['event']['stage']!='later_search_progress' for r in plan['records'])
