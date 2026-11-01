"""Equivalent declaration multiplicity and coverage dispatch boundaries."""
from copy import deepcopy
import json
import pytest
from test_extraction import rig, ROOT
from test_predicate_v3 import setup
from test_shared_predicates import CATALOGUE
from ara.bank import load_bank
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.search_alignment import catalogue_inputs


def duplicate(mode):
    data=deepcopy(CATALOGUE);predicate=deepcopy(data['predicates'][0])
    if mode=='alias':
        data['sorts'].append(dict(name='b',gloss='a'))
        predicate['roles'][0]['sort']='b'
    else:predicate['gloss']='**F(x)**'
    data['predicates'].append(predicate)
    return data


@pytest.mark.parametrize('mode',['alias','format'])
def test_duplicate_meanings_cannot_reroll_history(mode):
    from ara.runtime.predicate_catalogue_policy import draft,replay
    bad=dict(coverage=[dict(covered=False,handles=['p0'],missing=['Q'],reason='P')]*2)
    good=dict(coverage=[dict(covered=True,handles=['p0','p1'],missing=[],reason='P')]*2)
    with pytest.raises(ValueError,match='reroll'):draft(duplicate(mode),[CATALOGUE])
    with pytest.raises(ValueError,match='reroll'):
        replay([CATALOGUE,duplicate(mode)],[bad,good],[dict(source_id='a'),dict(source_id='b')])


def test_native_duplicate_cannot_buy_another_coverage_call(rig,monkeypatch):
    votes=[]
    def damage(kind,data,inputs):
        if kind=='predicate_catalogue' and inputs.get('revision')==1:data.update(duplicate('alias'))
        if kind=='predicate_coverage':
            votes.append(inputs['revision'])
            for row in data['coverage']:
                if len(votes)==1:row.update(covered=False,missing=['Q'])
                else:row['handles']=['p0','p1']
    calls,t,rows,seen=setup(rig,monkeypatch,damage)
    with pytest.raises(ValueError,match='reroll'):prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert votes==[0]
    assert not any(k=='predicate_formalize' for k,_,_ in seen)


@pytest.mark.parametrize('placement',['before_catalogue','after_response','cached'])
def test_coverage_dispatch_between_prerequisite_and_response(rig,monkeypatch,placement):
    from ara.runtime.predicate_receipts import verify_model_receipts
    calls,t,rows,seen=setup(rig,monkeypatch)
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    receipt=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    events=calls.log.read()
    start=next(e for e in events if e['stage']=='call_start' and json.loads(e['payload_json'])['kind']=='predicate_coverage')
    events.remove(start)
    if placement=='cached':
        # Cached responses legitimately have no provider dispatch event.
        verify_model_receipts(events,receipt)
        return
    kind='predicate_catalogue' if placement=='before_catalogue' else 'predicate_coverage'
    position=next(i for i,e in enumerate(events) if e['stage']==kind and e['label']=='MODEL')
    events.insert(position+(placement=='after_response'),start)
    with pytest.raises(ValueError,match='order'):verify_model_receipts(events,receipt)
