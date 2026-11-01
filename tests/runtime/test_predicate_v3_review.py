"""Revision identity, exact diagnostics and causal catalogue/protection order."""
from copy import deepcopy
import json
import pytest
from test_extraction import rig,ROOT
from test_predicate_v3 import setup
from test_shared_predicates import CATALOGUE
from ara.bank import load_bank
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.search_alignment import catalogue_inputs


def renamed():
    data=deepcopy(CATALOGUE);data['sorts'][0]['name']='b';data['predicates'][0]['roles'][0]['sort']='b'
    return data


def test_sort_aliases_cannot_reroll_any_prior_vocabulary():
    from ara.runtime.predicate_catalogue_policy import draft,replay
    other=deepcopy(CATALOGUE);other['predicates'][0]['gloss']='G(x)'
    with pytest.raises(ValueError,match='reroll'):draft(renamed(),[CATALOGUE,other])
    missing=dict(coverage=[dict(covered=False,handles=['p0'],missing=['Q'],reason='R')]*2)
    good=dict(coverage=[dict(covered=True,handles=['p0'],missing=[],reason='P')]*2)
    with pytest.raises(ValueError,match='reroll'):
        replay([CATALOGUE,renamed()],[missing,good],[dict(source_id='a'),dict(source_id='b')])


def test_native_alias_revision_refuses_before_second_coverage(rig,monkeypatch):
    votes=[]
    def damage(kind,data,inputs):
        if kind=='predicate_coverage':
            votes.append(inputs)
            if len(votes)==1:data['coverage'][0].update(covered=False,missing=['Q'])
        if kind=='predicate_catalogue' and inputs.get('mode')=='provisional_revision':data.update(renamed())
    calls,t,rows,seen=setup(rig,monkeypatch,damage)
    with pytest.raises(ValueError,match='reroll'):
        prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert len(votes)==1 and not any(k=='predicate_formalize' for k,_,_ in seen)


def test_revision_keeps_exact_missing_components_and_reasons():
    from ara.runtime.predicate_catalogue_policy import catalogue_inputs
    check=dict(coverage=[dict(covered=False,handles=['p0'],missing=['Q','R'],reason='S'),
                         dict(covered=True,handles=['p0'],missing=[],reason='P')])
    base=dict(lifecycle_key='P',sources=[dict(source_id='a'),dict(source_id='b')],policy={})
    result=catalogue_inputs(base,[CATALOGUE],[check])
    assert result['coverage_feedback']['coverage']==check
    result['coverage_feedback']['coverage']['coverage'][0]['missing'].append('S')
    assert check['coverage'][0]['missing']==['Q','R']


@pytest.mark.parametrize('after',['predicate_coverage','shared_predicate_catalogue_protected'])
def test_reader_refuses_catalogue_response_after_coverage_or_protection(rig,monkeypatch,after):
    calls,t,rows,seen=setup(rig,monkeypatch)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    receipt=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    events=calls.log.read();i=next(i for i,e in enumerate(events) if e['stage']=='predicate_catalogue' and e['label']=='MODEL')
    catalogue=events.pop(i);j=next(i for i,e in enumerate(events) if e['stage']==after)
    events.insert(j+1,catalogue)
    from ara.runtime.predicate_receipts import verify_model_receipts
    with pytest.raises(ValueError,match='order'):verify_model_receipts(events,receipt)
