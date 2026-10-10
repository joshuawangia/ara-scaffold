import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from ara.types import CommitmentSet, CQAnswer, Formula, Proposal, Proposition, Tier1Repair

SCHEMAS = Path(__file__).resolve().parents[1] / 'schemas'
P = {'op': 'atom', 'name': 'P'}
PROPOSITION = {'id': 'p', 'text': 'P', 'formula': P}
PROPOSAL = {'bank_id': 'modus_ponens', 'premises': [
    {'slot': 'antecedent', 'text': 'P', 't_id': 't1', 'scope_id': None}], 'conclusion_text': 'Q'}
PAYLOADS = {
    'build_t': {'commitments': [{'id': 't1', 'text': 'P', 'citation': 'placeholder:1', 'formula': P}]},
    'propose_targets': {'targets': [PROPOSITION]},
    'propose_cuts': {'proposals': [PROPOSAL]},
    'formalise': {'formula': P},
    'map_leaf': {'t_id': 'open'},
    'answer_cq': {'cq_id': 'cq1', 'answer': 'P', 'answered': True, 'supporting_t_ids': ['t1']},
    'tier1_repair': {'action': 'unresolved', 'detail': 'P', 'proposals': []},
    'write_essay': {'title': 'P', 'body': 'P', 'bibliography': [
        {'id': 'c1', 'text': 'placeholder:1', 'url': None}]},
    'audit_essay': {'labels': [{'sentence': 1, 'node_ids': ['n1'], 'asserts_premise_or_inference_not_in_outline': False}]},
    'verify_originality_citations': {
        'originality': {'assessment': 'unverified', 'evidence_urls': [], 'detail': 'P'},
        'items': [{'id': 'c1', 'kind': 'citation', 'text': 'placeholder:1',
                   'status': 'unverified', 'evidence_urls': [], 'detail': 'P', 'action': 'remove'}]},
}


def validator(kind):
    schema = json.loads((SCHEMAS / f'{kind}.json').read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


@pytest.mark.parametrize('kind', PAYLOADS)
def test_model_response_schema(kind):
    v = validator(kind)
    v.validate(PAYLOADS[kind])
    with pytest.raises(ValidationError):
        v.validate({**PAYLOADS[kind], 'unknown': 'P'})
    with pytest.raises(ValidationError):
        v.validate({})


def test_schema_payloads_deserialize_into_seam():
    assert CommitmentSet.from_dict(PAYLOADS['build_t']).get('t1').formula == Formula('atom', name='P')
    assert Proposition.from_dict(PAYLOADS['propose_targets']['targets'][0]).id == 'p'
    assert Proposal.from_dict(PROPOSAL).premises[0].t_id == 't1'
    assert CQAnswer.from_dict(PAYLOADS['answer_cq']).answered
    assert Tier1Repair.from_dict(PAYLOADS['tier1_repair']).action == 'unresolved'
    for payload in PAYLOADS.values():
        assert json.loads(json.dumps(payload)) == payload


@pytest.mark.parametrize('op,args', [('not', []), ('and', [P]), ('implies', [P]), ('forall', [P])])
def test_formula_schema_rejects_bad_shapes(op, args):
    with pytest.raises(ValidationError):
        validator('formalise').validate({'formula': {'op': op, 'args': args}})


def test_verification_cannot_retain_unverified_item():
    payload = json.loads(json.dumps(PAYLOADS['verify_originality_citations']))
    payload['items'][0]['action'] = 'retain'
    with pytest.raises(ValidationError):
        validator('verify_originality_citations').validate(payload)


def test_verified_item_requires_evidence():
    payload = json.loads(json.dumps(PAYLOADS['verify_originality_citations']))
    payload['items'][0].update(status='verified', action='retain')
    with pytest.raises(ValidationError):
        validator('verify_originality_citations').validate(payload)


def test_formula_schema_accepts_serialized_ast():
    from ara.types import Term
    p, q = Formula('atom', name='P'), Formula('atom', name='Q')
    expressions = [p, Formula('not', (p,)), *[
        Formula(op, (p, q)) for op in ('and', 'or', 'implies', 'iff')],
        Formula('predicate', name='F', terms=(Term('variable', 'x'), Term('constant', 'a')))]
    expressions.extend([Formula(op, (expressions[-1],), variable='x') for op in ('forall', 'exists')])
    for formula in expressions:
        validator('formula').validate(formula.to_dict())
        validator('formalise').validate({'formula': formula.to_dict()})
