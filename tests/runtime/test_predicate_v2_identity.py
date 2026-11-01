"""Rejected duplicate declarations cannot replace protected catalogue identities."""
from copy import deepcopy
import pytest
from test_extraction import rig,ROOT
from test_predicate_v2 import setup
from test_shared_predicates import CATALOGUE
from ara.bank import load_bank
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.search_alignment import catalogue_inputs


@pytest.mark.parametrize('field',['sorts','predicates'])
@pytest.mark.parametrize('first',[True,False])
def test_rejected_duplicate_keeps_protected_identity_recoverable(rig,monkeypatch,field,first):
    attempts=[]
    def damage(kind,data,inputs):
        if kind!='predicate_catalogue':return
        attempts.append(inputs)
        if len(attempts)==1:data['extra']='Q'
        elif len(attempts)==2:
            duplicate=deepcopy(data[field][0])
            duplicate['gloss' if field=='sorts' else 'sharing_rationale']='Q'
            data[field].insert(0 if first else len(data[field]),duplicate)
    calls,t,rows,seen=setup(rig,monkeypatch,damage);calls.config['validation_attempts']=3
    final=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert attempts[2]['validation_feedback']['preserve_catalogue']==CATALOGUE
    receipt=catalogue_inputs(calls.log.path.parent,final)['commitment_provenance']['consolidation']
    assert receipt['after']['admitted']==3


def test_ambiguous_initial_identity_protects_only_unambiguous_siblings():
    from ara.runtime.predicate_coverage import merge_preserved
    data=deepcopy(CATALOGUE)
    data['sorts'] += [dict(name='a',gloss='Q'),dict(name='b',gloss='b')]
    sibling=dict(gloss='G(x)',roles=[dict(role='x',sort='b')],sharing_rationale='Q',distinctions='R')
    data['predicates'].append(sibling)
    assert merge_preserved(None,data)==dict(sorts=[dict(name='b',gloss='b')],predicates=[sibling])


def test_prior_identity_wins_without_losing_nonconflicting_additions():
    from ara.runtime.predicate_coverage import merge_preserved
    data=deepcopy(CATALOGUE)
    data['sorts'].insert(0,dict(name='a',gloss='Q'))
    data['sorts'].append(dict(name='b',gloss='b'))
    sibling=dict(gloss='G(x)',roles=[dict(role='x',sort='b')],sharing_rationale='Q',distinctions='R')
    data['predicates'].append(sibling)
    expected=deepcopy(CATALOGUE);expected['sorts'].append(dict(name='b',gloss='b'));expected['predicates'].append(sibling)
    assert merge_preserved(CATALOGUE,data)==expected
