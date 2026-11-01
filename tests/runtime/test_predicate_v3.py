"""Feasible provisional catalogue authority and cross-source use; placeholders only."""
from copy import deepcopy
import json
import pytest
from ara.bank import load_bank
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.search_alignment import catalogue_inputs
from test_extraction import rig,ROOT
from test_shared_predicates import install,CATALOGUE

V3='shared-predicate-formalization-v3'


def setup(rig,monkeypatch,damage=None):
    calls,t,rows,seen=install(rig,monkeypatch,damage)
    calls.config['shared_predicates_version']=V3
    return calls,t,rows,seen


def oversized(field,count):
    data=deepcopy(CATALOGUE)
    if field=='sorts':data[field]=[dict(name='a',gloss='a')]+[dict(name=f'a{i}',gloss='P') for i in range(1,count)]
    else:data[field]=[{**deepcopy(CATALOGUE['predicates'][0]),'gloss':f'F{i}(x)'} for i in range(count)]
    return data


@pytest.mark.parametrize('field,count',[('sorts',25),('predicates',49)])
def test_legacy_over_capacity_cannot_create_protected_authority(field,count):
    from ara.runtime.predicate_coverage import merge_preserved
    assert merge_preserved(None,oversized(field,count))==dict(sorts=[],predicates=[])
    data=oversized(field,count);data[field][0]=deepcopy(CATALOGUE[field][0])
    assert merge_preserved(CATALOGUE,data)==CATALOGUE


@pytest.mark.parametrize('field,count',[('sorts',13),('predicates',25)])
def test_native_capacity_correction_recovers_before_protection(rig,monkeypatch,field,count):
    attempts=[]
    def damage(kind,data,inputs):
        if kind!='predicate_catalogue':return
        attempts.append(inputs)
        if len(attempts)==1:data.update(oversized(field,count))
    calls,t,rows,seen=setup(rig,monkeypatch,damage);calls.config['validation_attempts']=2
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert len(attempts)==2
    feedback=attempts[1]['validation_feedback']
    assert 'preserve_catalogue' not in feedback
    assert feedback['catalogue_capacity']['counts'][field]==count
    assert 'merge to <=' in feedback['catalogue_capacity']['message']
    r=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    assert r['after']['admitted']==3
    events=calls.log.read();protection=[i for i,e in enumerate(events) if e['stage']=='shared_predicate_catalogue_protected']
    assert len(protection)==1
    assert protection[0]>max(i for i,e in enumerate(events) if e['stage']=='predicate_coverage' and e['label']=='MODEL')
    from ara.runtime.predicate_receipts import verify_model_receipts
    with pytest.raises(ValueError,match='protection'):
        verify_model_receipts([e for e in events if e['stage']!='shared_predicate_catalogue_protected'],r)


def test_failed_shared_coverage_can_replace_unprotected_draft(rig,monkeypatch):
    drafts=[]
    def damage(kind,data,inputs):
        if kind=='predicate_catalogue':
            drafts.append(inputs)
            if len(drafts)==1:data['predicates'].append({**deepcopy(data['predicates'][0]),'gloss':'G(x)'})
    calls,t,rows,seen=setup(rig,monkeypatch,damage)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert len(drafts)==2 and 'preserve_catalogue' not in drafts[1]
    r=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    assert len(r['catalogue_history'])==2 and r['after']['admitted']==3


def test_diagnostic_stop_counts_rejections_and_prevents_freeze(rig,monkeypatch):
    def damage(kind,data,inputs):
        if kind=='predicate_fidelity':data['equivalent']=False
    calls,t,rows,seen=setup(rig,monkeypatch,damage);calls.config['shared_predicates_max_unresolved']=1
    with pytest.raises(ValueError,match='threshold'):
        prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    pauses=[json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='shared_predicate_diagnostic_pause']
    assert len(pauses)==1 and pauses[0]['unresolved']==2 and pauses[0]['selected']==3
    assert pauses[0]['processed']==2 and pauses[0]['unattempted']==1 and pauses[0]['admitted']==0
    assert sum(k=='predicate_formalize' for k,_,_ in seen)==2
    assert not (calls.log.path.parent/'commitments.json').exists()


def test_shared_coverage_counts_papers_and_all_dependencies():
    from ara.runtime.predicate_catalogue_policy import assess
    check=dict(coverage=[dict(covered=True,handles=['p0'],missing=[],reason='P') for _ in range(3)])
    assert not assess(CATALOGUE,check,[dict(source_id='a')]*3)['accepted']
    result=assess(CATALOGUE,check,[dict(source_id=x) for x in ('a','b','a')])
    assert result['accepted'] and result['source_use_by_handle']==dict(t0=['a','b'],p0=['a','b'])
    unused=deepcopy(CATALOGUE);unused['sorts'].append(dict(name='b',gloss='b'))
    assert not assess(unused,check,[dict(source_id=x) for x in ('a','b','c')])['accepted']
    missing=deepcopy(CATALOGUE);missing['predicates'][0]['roles'][0]['sort']='b'
    with pytest.raises(ValueError,match='unknown role sort'):assess(missing,check,[dict(source_id='a')]*3)


def test_metadata_order_and_cycle_cannot_reroll_provisional_coverage():
    from ara.runtime.predicate_catalogue_policy import draft,replay
    a=deepcopy(CATALOGUE);b=deepcopy(a);b['predicates'][0]['gloss']='G(x)'
    metadata=deepcopy(a);metadata['predicates'][0]['sharing_rationale']='R'
    for data in (a,metadata):
        with pytest.raises(ValueError,match='reroll'):draft(data,[a,b])
    enlarged=deepcopy(a);enlarged['predicates'].append(deepcopy(b['predicates'][0]))
    reordered=deepcopy(enlarged);reordered['predicates'].reverse()
    with pytest.raises(ValueError,match='reroll'):draft(reordered,[enlarged])
    missing=dict(coverage=[dict(covered=False,handles=['p0'],missing=['Q'],reason='P')]*2)
    good=dict(coverage=[dict(covered=True,handles=['p0'],missing=[],reason='P')]*2)
    with pytest.raises(ValueError,match='reroll'):
        replay([a,b,a],[missing,missing,good],[dict(source_id='a'),dict(source_id='b')])


def test_capacity_feedback_is_deterministic_and_not_merge_authority():
    from ara.runtime.predicate_catalogue_policy import capacity_feedback,draft
    data=oversized('sorts',13)
    feedback=capacity_feedback(data)
    assert feedback==capacity_feedback(data)
    assert feedback['limits']==dict(sorts=12,predicates=24)
    assert feedback['dependency_sort_count']==1
    assert feedback['overlap_candidates'] and 'lexical candidates only' in feedback['message']
    with pytest.raises(ValueError,match='merge to <=12'):draft(data)
    data['sorts']=data['sorts'][:12];draft(data)


def test_v3_effective_schema_and_preflight_bind_small_capacity(rig):
    from ara.runtime.codex_preflight import manifest
    calls=rig[0];calls.config.update(provider='codex_cli',construction_shared_predicates=True,shared_predicates_version=V3)
    schema=calls.response_schema('predicate_catalogue',dict(policy_version=V3))
    from ara.runtime.validation import LinearValidator
    assert not LinearValidator(schema).is_valid(oversized('sorts',13))
    from ara.runtime.cache import canonical,digest
    case=next(c for c in manifest(calls.config,ROOT)['cases'] if c['case']=='predicate_catalogue')
    assert case['native_schema_hash']==digest(canonical(schema))
    formal=calls.response_schema('predicate_formalize',dict(policy_version=V3))
    assert not LinearValidator(formal).is_valid(dict(mode='retain',formula=None,reason='P'))



def test_unshared_catalogue_never_protects_or_formalizes(rig,monkeypatch):
    def damage(kind,data,inputs):
        if kind=='predicate_catalogue':
            data['predicates'].append({**deepcopy(data['predicates'][0]),'gloss':'G(x)'})
    calls,t,rows,seen=setup(rig,monkeypatch,damage)
    with pytest.raises(ValueError,match='reroll'):
        prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert not any(k=='predicate_formalize' for k,_,_ in seen)
    assert not any(e['stage']=='shared_predicate_catalogue_protected' for e in calls.log.read())


def test_replay_refuses_unshared_or_oversized_final_catalogue():
    from ara.runtime.predicate_catalogue_policy import replay
    check=dict(coverage=[dict(covered=True,handles=['p0'],missing=[],reason='P')]*2)
    with pytest.raises(ValueError,match='protection/coverage'):
        replay([CATALOGUE],[check],[dict(source_id='a')]*2)
    with pytest.raises(ValueError,match='merge to <=12'):
        replay([oversized('sorts',13)],[check],[dict(source_id='a'),dict(source_id='b')])
