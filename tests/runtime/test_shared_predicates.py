"""Catalogue-first relations through native admission and frozen replay; P/Q only."""
from copy import deepcopy
import json
import pytest
from ara.bank import load_bank
from ara.runtime.cache import canonical, digest
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.providers import Response
from ara.runtime.search_alignment import catalogue_inputs
from test_extraction import rig, ROOT, response
from test_symbol_alignment import fixture

CATALOGUE=dict(sorts=[dict(name='a',gloss='a')],predicates=[dict(gloss='F(x)',roles=[dict(role='x',sort='a')],sharing_rationale='P Q',distinctions='R')])
def formula(name='p0'):
    return dict(op='forall',variable='x',args=[dict(op='implies',args=[dict(op='predicate',name='t0',terms=[dict(kind='variable',name='x')]),dict(op='predicate',name=name,terms=[dict(kind='variable',name='x')])])])

def install(rig,monkeypatch,damage=None,*,record_setup=True):
    calls=rig[0];calls.config.update(construction_shared_predicates=True,shared_predicates_max_unresolved=3,shared_predicates_failure_streak=4)
    t,symbols,rows=fixture();monkeypatch.setattr(calls,'build_t',lambda *_:t)
    if record_setup:
        calls.log.record('run_started',config=calls.config,topic='P',literature='P',audience='P',bank_version=load_bank(ROOT/'bank').bank_version)
        calls.log.record('build_t_merged',commitments=t.to_dict(),symbols=symbols,provenance=rows)
    seen=[]
    def complete(kind,prompt,schema,maximum):
        inputs=json.loads(prompt.split('\nINPUT_JSON\n')[1]);seen.append((kind,inputs,schema))
        if kind=='judge_symbol_alignment':data=dict(relation='unrelated',reason='P Q')
        elif kind=='predicate_catalogue':data=deepcopy(CATALOGUE)
        elif kind=='predicate_formalize':data=dict(mode='decompose',formula=formula(),reason='P Q')
        elif kind=='predicate_backtranslate':
            assert 'source' not in inputs and 'evidence' not in inputs
            data=dict(text='F(x)')
        elif kind=='predicate_fidelity':data=dict(equivalent=True,preserves_scope=True,no_additions=True,reason='P Q')
        else:raise AssertionError(kind)
        if damage:damage(kind,data,inputs)
        return Response(response(data))
    monkeypatch.setattr(calls.provider,'complete',complete)
    return calls,t,rows,seen

def test_native_catalogue_first_shared_predicates(rig,monkeypatch):
    calls,t,rows,seen=install(rig,monkeypatch)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert all(c.formula.op=='forall' for c in final.commitments)
    meta=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']
    assert meta['commitments']==rows
    receipt=meta['consolidation'];assert receipt['schema_version']=='shared-predicate-formalization-v1'
    assert receipt['after']['shared_content_predicates']==1
    assert receipt['after']['faithful_fraction']==1
    assert [k for k,_,_ in seen].count('predicate_fidelity')==9
    assert not any(k=='judge_symbol_alignment' for k,_,_ in seen)


def test_one_adverse_sample_retains_exact_original_and_stance(rig,monkeypatch):
    def damage(kind,data,inputs):
        if kind=='predicate_fidelity' and inputs['sample_index']==1:data['equivalent']=False
    calls,t,rows,seen=install(rig,monkeypatch,damage)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert final==t
    receipt=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    assert receipt['after']['unresolved']==3 and receipt['after']['faithful_fraction']==0
    assert all(i['reason']=='adverse_fidelity' for i in receipt['items'])
    assert sum(e['stage']=='consolidation_unresolved' for e in calls.log.read())==3


@pytest.mark.parametrize('damage',[
    lambda f:f.update(op='atom',name='P',args=[],variable=None),
    lambda f:f['args'][0]['args'][1].update(name='missing'),
    lambda f:f['args'][0]['args'][1]['terms'][0].update(kind='constant'),
    lambda f:f['args'][0].update(op='and'),
])
def test_structural_failures_are_local_and_originals_survive(rig,monkeypatch,damage):
    def change(kind,data,inputs):
        if kind=='predicate_formalize':damage(data['formula'])
    calls,t,rows,seen=install(rig,monkeypatch,change)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert final==t
    receipt=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    assert receipt['after']['unresolved']==3
    assert not any(k=='predicate_fidelity' for k,_,_ in seen)


def test_failure_threshold_refuses_before_freeze(rig,monkeypatch):
    def damage(kind,data,inputs):
        if kind=='predicate_formalize':data.update(mode='retain',formula=None,reason='P')
    calls,t,rows,seen=install(rig,monkeypatch,damage);calls.config['shared_predicates_max_unresolved']=1
    with pytest.raises(ValueError,match='failure threshold'):prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert not (calls.log.path.parent/'commitments.json').exists()


def test_cumulative_feedback_keeps_prior_constraints(rig,monkeypatch):
    counts={}
    def damage(kind,data,inputs):
        if kind!='predicate_formalize':return
        key=inputs['item_key'];counts[key]=counts.get(key,0)+1
        if counts[key]==1:data['formula']['args'][0]['args'][1]['name']='missing'
        elif counts[key]==2:data['formula']['args'][0]['op']='and'
        else:
            assert len(inputs['validation_history'])==2
            assert 'enum' in str(inputs['validation_history'][0]) or 'unknown predicate handle' in str(inputs['validation_history'][0])
            assert 'sort guard' in str(inputs['validation_history'][1])
    calls,t,rows,seen=install(rig,monkeypatch,damage);calls.config['validation_attempts']=3
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert all(c.formula.op=='forall' for c in final.commitments)


def test_full_endorsed_consistency_cannot_be_avoided_by_item_order(rig,monkeypatch):
    def damage(kind,data,inputs):
        if kind=='predicate_formalize' and inputs['item_key']==digest('Q'):
            # An existing admitted universal must contradict this witness.
            data['formula']=dict(op='exists',variable='x',args=[dict(op='and',args=[
                dict(op='predicate',name='t0',terms=[dict(kind='variable',name='x')]),
                dict(op='not',args=[dict(op='predicate',name='p0',terms=[dict(kind='variable',name='x')])])])])
    calls,t,rows,seen=install(rig,monkeypatch,damage)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert final.get('Q')==t.get('Q')
    assert final.get('P').formula.op=='forall'
    receipt=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    assert receipt['items'][1]['reason']=='shared predicate consistency not established'


def test_receipt_fidelity_replay_refuses_rehashed_admission(rig,monkeypatch):
    from ara.runtime.shared_predicates import validate_receipt
    calls,t,rows,seen=install(rig,monkeypatch)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    receipt=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    receipt['items'][0]['judgments'][2]['no_additions']=False
    receipt['sha256']=digest(canonical({k:v for k,v in receipt.items() if k!='sha256'}))
    with pytest.raises(ValueError,match='adverse fidelity'):validate_receipt(receipt,final,receipt['symbols'],rows)


def test_native_frozen_fork_preserves_typed_receipt(rig,monkeypatch,tmp_path):
    from ara.runtime.freeze_fork import fork_from_freeze
    calls,t,rows,seen=install(rig,monkeypatch)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    dest=tmp_path/'frozen-copy'
    _,_,restored=fork_from_freeze(calls.log.path.parent,dest,load_bank(ROOT/'bank'))
    assert restored==final
    assert catalogue_inputs(dest,restored)==catalogue_inputs(calls.log.path.parent,final)


def test_type_conflict_and_sort_only_sharing_do_not_pass():
    from ara.runtime.shared_predicates import catalogue,typed_formula
    data=deepcopy(CATALOGUE);data['sorts'].append(dict(name='b',gloss='b'))
    data['predicates'][0]['roles'][0]['sort']='b'
    with pytest.raises(ValueError,match='sort mismatch'):typed_formula(formula(),catalogue(data))
    with pytest.raises(ValueError,match='content predicate'):typed_formula(formula('t0'),catalogue(CATALOGUE))


def test_native_selected_cli_freeze_and_report(rig,monkeypatch,tmp_path):
    from test_hypothesis_construction_fork import finish_source,snapshot
    from ara.runtime.cli import main
    from ara.runtime.calls import ModelCalls
    from ara.runtime.cache import Cache
    from ara.runtime.logging import EventLog
    from ara.runtime.export import methodology
    calls=rig[0];original=finish_source(calls,monkeypatch);source=calls.log.path.parent;before=snapshot(source)
    selection=tmp_path/'selection.json';selection.write_text(canonical(dict(commitment_ids=['P','Q','R'],max_unresolved=3,failure_streak=4)))
    # Reuse only the fake transport; destination goes through all native functions.
    install(rig,monkeypatch,record_setup=False)
    destination=tmp_path/'shared'
    def factory(config,log,topic):return ModelCalls(config,calls.provider,log,Cache(destination/'cache'),ROOT,topic)
    assert main(['shared-predicates','--source-run',str(source),'--run-dir',str(destination),'--selection-file',str(selection),'--stop-at','freeze'],calls_factory=factory)==0
    assert snapshot(source)==before
    events=EventLog(destination/'events.jsonl').read()
    assert sum(e['stage']=='commitments_frozen' for e in events)==1
    assert any(e['stage']=='run_stopped_at_freeze' for e in events)
    assert not any(e['label']=='MODEL' and e['stage'] in ('propose_targets','map_leaf') for e in events)
    assert any(e['stage']=='shared_predicate_bank_metrics' for e in events)
    data=methodology(destination/'events.jsonl')
    assert '"shared_predicates"' in data and '"shared_content_predicates": 1' in data
    from ara.runtime.freeze_fork import fork_from_freeze
    fork_from_freeze(destination,tmp_path/'verified-fork',load_bank(ROOT/'bank'))
    (source/'commitments.json').unlink()
    with pytest.raises((ValueError,FileNotFoundError)):
        fork_from_freeze(destination,tmp_path/'missing-source-fork',load_bank(ROOT/'bank'))


def test_native_wire_cannot_emit_r20_atom_lists(rig):
    from ara.runtime.codex_schema import strict_schema
    from ara.runtime.validation import LinearValidator
    calls=rig[0];schema=calls.response_schema('predicate_formalize',{})
    wire=strict_schema(schema)
    assert not LinearValidator(wire).is_valid(dict(formulas=[dict(op='atom',name='P')]*7))
    assert not LinearValidator(schema).is_valid(dict(mode='decompose',formula=dict(op='atom',name='P'),reason='P'))
    assert LinearValidator(schema).is_valid(dict(mode='retain',formula=None,reason='P'))


def test_bank_metric_counts_native_cross_source_instances_only():
    from ara.runtime.predicate_metrics import bank_instances
    from ara.types import Commitment,CommitmentSet,Formula
    class Sink:
        def emit(self,event):pass
    p,q=Formula('atom',name='P'),Formula('atom',name='Q')
    t=CommitmentSet((Commitment('a','P','a:1',Formula('implies',(p,q))),Commitment('b','P','b:1',p)))
    rows={id:dict(source_id=id,stance='endorsed') for id in ('a','b')}
    result=bank_instances(t,rows,load_bank(ROOT/'bank'),Sink())
    assert any(i['bank_id']=='modus_ponens' for i in result['instances'])
    rows['b']['stance']='reported'
    result=bank_instances(t,rows,load_bank(ROOT/'bank'),Sink())
    assert result['cross_paper_applicable_bank_instances']==0


def test_selected_origin_corruption_refuses(rig,monkeypatch,tmp_path):
    calls,t,rows,seen=install(rig,monkeypatch)
    prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    # An authenticated but mismatching origin cannot replace the original selection.
    origin=dict(commitments={'commitments':[]},symbols=[],provenance={},evidence={})
    calls.log.record('shared_predicate_source',**origin,sha256=digest(canonical(origin)))
    # The fake origin is after freeze and therefore deliberately outside fork prefix.
    # Direct native origin replay is the load-bearing check for this malformed receipt.
    from ara.runtime.predicate_fork import validate_selected_origin
    final=json.loads((calls.log.path.parent/'commitment-provenance.json').read_text())
    with pytest.raises(ValueError,match='selected-source binding'):validate_selected_origin(calls.log.read(),final)


def test_authenticated_dissent_cannot_be_replaced_in_receipt(rig,monkeypatch):
    from ara.runtime.predicate_receipts import verify_model_receipts
    def damage(kind,data,inputs):
        if kind=='predicate_fidelity' and inputs['sample_index']==2:data['equivalent']=False
    calls,t,rows,seen=install(rig,monkeypatch,damage)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    receipt=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    receipt['items'][0]['judgments'][2]['equivalent']=True
    with pytest.raises(ValueError,match='model response/receipt mismatch'):verify_model_receipts(calls.log.read(),receipt)


def test_negated_mixed_quantifiers_preserve_guards_and_reject_wrong_polarity():
    from ara.runtime.shared_predicates import catalogue,typed_formula
    entries=catalogue(CATALOGUE)
    inner=dict(op='exists',variable='y',args=[dict(op='and',args=[
        dict(op='predicate',name='t0',terms=[dict(kind='variable',name='y')]),
        dict(op='not',args=[dict(op='predicate',name='p0',terms=[dict(kind='variable',name='y')])])])])
    f=formula();f['args'][0]['args'][1]=inner
    good=dict(op='not',args=[f]);bound=typed_formula(good,entries)
    assert bound.op=='not' and bound.args[0].args[0].args[1].op=='exists'
    inner['args'][0]['op']='implies'
    with pytest.raises(ValueError,match='sort guard'):typed_formula(good,entries)


def test_loader_checks_model_receipts_after_rehash(rig,monkeypatch):
    calls,t,rows,seen=install(rig,monkeypatch)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    path=calls.log.path.parent/'commitment-provenance.json';meta=json.loads(path.read_text())
    receipt=meta['consolidation'];receipt['items'][0]['judgments'][0]['reason']='R'
    receipt['sha256']=digest(canonical({k:v for k,v in receipt.items() if k!='sha256'}))
    meta['sha256']=digest(canonical({k:v for k,v in meta.items() if k!='sha256'}))
    path.write_text(canonical(meta))
    with pytest.raises(ValueError,match='model response/receipt mismatch'):catalogue_inputs(calls.log.path.parent,final)


def test_reported_uses_cannot_earn_pilot_sharing_credit():
    from dataclasses import replace
    from ara.runtime.shared_predicates import catalogue,typed_formula,metrics,symbols_for
    t,syms,rows=fixture();entries=catalogue(CATALOGUE);f=typed_formula(formula(),entries)
    final=type(t)(tuple(replace(c,formula=f) for c in t.commitments));symbols=symbols_for(final,syms,entries)
    items=[dict(id=c.id,status='admitted') for c in t.commitments]
    rows['Q']['stance']='reported';rows['R']['stance']='attacked'
    result=metrics(final,symbols,rows,entries,items)
    assert result['shared_content_predicates']==0 and result['shared_content_predicates_all_stances']==1
    items[1]['status']='unresolved';items[2]['status']='unresolved'
    rows['Q']['stance']=rows['R']['stance']='endorsed'
    assert metrics(final,symbols,rows,entries,items)['shared_content_predicates']==0
