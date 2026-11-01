"""Catalogue correction must recover and must address uncovered content."""
from copy import deepcopy
import pytest
from test_extraction import rig,ROOT
from test_predicate_v2 import setup
from ara.bank import load_bank
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.search_alignment import catalogue_inputs


def test_rejected_overwrite_keeps_prior_authority_recoverable(rig,monkeypatch):
    attempts=[]
    def damage(kind,data,inputs):
        if kind!='predicate_catalogue':return
        attempts.append(deepcopy(inputs))
        if len(attempts)==1:data['extra']='Q'
        elif len(attempts)==2:
            data['sorts'][0]['gloss']='Q'
            data['sorts'].append(dict(name='b',gloss='b'))
            data['predicates'].append(dict(gloss='G(x)',roles=[dict(role='x',sort='b')],
                                          sharing_rationale='P Q',distinctions='R'))
    calls,t,rows,seen=setup(rig,monkeypatch,damage);calls.config['validation_attempts']=3
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert len(attempts)==3
    assert attempts[-1]['validation_feedback']['preserve_catalogue']['sorts']==[dict(name='a',gloss='a')]
    receipt=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    assert receipt['after']['admitted']==3


def test_noop_extension_refuses_before_fresh_coverage(rig,monkeypatch):
    coverage_calls=[]
    def damage(kind,data,inputs):
        if kind=='predicate_coverage':
            coverage_calls.append(inputs)
            if len(coverage_calls)==1:data['coverage'][0].update(covered=False,missing=['G(x)'])
    calls,t,rows,seen=setup(rig,monkeypatch,damage)
    with pytest.raises(ValueError,match='strictly grow'):
        prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert len(coverage_calls)==1
    assert not any(k=='predicate_formalize' for k,_,_ in seen)


def test_replay_rejects_unchanged_catalogue_after_uncovered_judgment():
    from ara.runtime.predicate_coverage import replay
    from test_shared_predicates import CATALOGUE
    missing=dict(coverage=[dict(covered=False,handles=['p0'],missing=['G(x)'],reason='P')])
    covered=dict(coverage=[dict(covered=True,handles=['p0'],missing=[],reason='P')])
    with pytest.raises(ValueError,match='strictly grow'):
        replay([CATALOGUE,CATALOGUE],[missing,covered],1)


def test_partial_shape_correction_preserves_new_valid_sort():
    from ara.runtime.predicate_coverage import merge_preserved
    a=dict(name='a',gloss='a');b=dict(name='b',gloss='b')
    protected=dict(sorts=[a],predicates=[])
    assert merge_preserved(protected,dict(sorts=[a,b]))==dict(sorts=[a,b],predicates=[])
