"""Sidecar codec/bindings without changing the legacy CommitmentSet codec."""
import copy
import json

import pytest

from ara.runtime.cache import canonical, digest
from ara.runtime.commitment_provenance import (content_definition, load_commitment_provenance,
    make_commitment_provenance, validate_commitment_provenance)
from ara.runtime.frozen_catalogue import make_catalogue
from ara.types import Commitment, CommitmentSet, Formula


def fixture():
    t = CommitmentSet((Commitment('p', 'P', 'p:pdf:1', Formula('atom', name='P')),))
    cat = make_catalogue(t, [dict(name='P',kind='atom',arity=0,definition='P',evidence_ids=['p'])])
    rows = {'p':dict(source_id='p',source_authors=['a'],attributed_to='b',page_start=1,page_end=1,
                    evidence_id='p',attribution='reported_view',stance='reported',source_kind='premise',
                    source_text='b argues P',omitted_support_ids=[])}
    return t,cat,make_commitment_provenance(t,cat,rows)


def test_sidecar_roundtrip_and_legacy_absence(tmp_path):
    t,cat,value=fixture()
    assert load_commitment_provenance(tmp_path,t,None) is None
    (tmp_path/'commitment-provenance.json').write_text(canonical(value))
    assert load_commitment_provenance(tmp_path,t,cat)==value
    assert value['commitments']['p']['stance']=='reported'
    assert value['commitments']['p']['source_text']=='b argues P'
    assert set(t.to_dict()['commitments'][0])=={'id','text','citation','formula'}
    with pytest.raises(ValueError):load_commitment_provenance(tmp_path,t,None)


@pytest.mark.parametrize('change',['hash','t_binding','catalogue_binding','inventory','stance','source_kind','fields','page','semantics'])
def test_sidecar_refuses_tampering_even_with_recomputed_hash(change):
    t,cat,value=fixture()
    row=value['commitments']['p']
    if change=='hash':value['sha256']='0'*64
    if change=='t_binding':value['commitments_sha256']='0'*64
    if change=='catalogue_binding':value['catalogue_sha256']='0'*64
    if change=='inventory':value['commitments']={}
    if change=='stance':row['stance']='endorsed'
    if change=='source_kind':row['source_kind']='attacked_view'
    if change=='fields':row['extra']='P'
    if change=='page':row['page_start']=True
    if change=='semantics':value['definition_semantics']='P'
    if change!='hash':value['sha256']=digest(canonical({k:v for k,v in value.items() if k!='sha256'}))
    with pytest.raises(ValueError):validate_commitment_provenance(value,t,cat)


@pytest.mark.parametrize('text',['a argues P','According to a, P',"a’s view is P",'a holds P','a maintains P'])
def test_shared_lexicon_rejects_attribution(text):
    assert not content_definition(text)
    assert content_definition('P')


@pytest.mark.parametrize('verb', ['argues', 'holds', 'claims'])
def test_exact_unframing_preserves_author_and_original(verb):
    from ara.runtime.commitment_provenance import exact_unframe
    original = f'a b {verb} that P'
    assert exact_unframe(original, ['a', 'a b']) == dict(author='a b', original_definition=original, definition='P')
    assert exact_unframe('Not ' + original, ['a b']) is None


@pytest.mark.parametrize('field', ['author', 'original_definition', 'definition', 'name'])
def test_unframing_provenance_rejects_tampered_history(field):
    t, cat, value = fixture()
    row = value['commitments']['p']
    row['definition_unframes'] = [dict(kind='commitment', name='p', author='b',
                                       original_definition='b claims that P', definition='P')]
    valid = make_commitment_provenance(t, cat, value['commitments'])
    assert valid['commitments']['p']['source_text'] == 'b argues P'
    valid['commitments']['p']['definition_unframes'][0][field] = 'Q'
    valid['sha256'] = digest(canonical({k:v for k,v in valid.items() if k != 'sha256'}))
    with pytest.raises(ValueError): validate_commitment_provenance(valid, t, cat)
