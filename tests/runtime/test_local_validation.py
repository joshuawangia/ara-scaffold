"""Native validation authority and bounded work on placeholder formula trees."""
import copy
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from ara.runtime.validation import LinearValidator, validate_local
from ara.runtime.providers import Response
from ara.types import Proposition
from test_calls import rig, response

ROOT = Path(__file__).resolve().parents[2]
P = {'op': 'atom', 'name': 'P'}


def schema(kind='formalise'):
    return json.loads((ROOT / 'schemas' / f'{kind}.json').read_text())


def stall_shape():
    # Exact recorded operator topology; every source symbol is replaced by P.
    atom = {'args': [], 'name': 'P', 'op': 'atom', 'terms': [], 'variable': None}
    def node(op, *args):
        return {'args': list(args), 'name': None, 'op': op, 'terms': [], 'variable': None}
    value = node('and', node('and', node('implies', copy.deepcopy(atom), copy.deepcopy(atom)),
                           copy.deepcopy(atom), node('not', copy.deepcopy(atom))),
                 node('not', copy.deepcopy(atom)))
    for _ in range(7):
        value = node('and', value)
    return {'formula': value}


def test_stall_shape_rejected_before_recursive_validation(monkeypatch):
    from ara.runtime import validation
    def forbidden(*args, **kwargs):
        raise AssertionError('invalid formula reached recursive schema worker')
    monkeypatch.setattr(validation.subprocess, 'Popen', forbidden)
    started = time.monotonic()
    with pytest.raises(ValidationError, match='minItems') as error:
        validate_local(schema(), stall_shape())
    assert list(error.value.absolute_path) == ['formula', 'args']
    assert time.monotonic() - started < .05


def test_native_stall_rejection_corrects_and_accounts(rig, monkeypatch):
    calls, provider, log = rig
    calls.config['validation_attempts'] = 2
    sent = []
    def complete(kind, prompt, schema, maximum):
        sent.append(json.loads(prompt.split('\nINPUT_JSON\n')[1]))
        return Response(response(stall_shape() if len(sent) == 1 else {'formula': P}))
    monkeypatch.setattr(provider, 'complete', complete)
    assert calls.formalise(Proposition('p', 'P')).name == 'P'
    assert 'minItems' in sent[1]['validation_feedback']['error']
    receipts = [e for e in log.read() if e['label'] == 'MODEL']
    assert [json.loads(e['payload_json'])['status'] for e in receipts] == ['rejected', 'accepted']
    assert 'formula/args' in json.loads(receipts[0]['payload_json'])['reason']
    assert calls.budget.used_tokens == 16
    assert len(list(calls.cache.path.glob('*.json'))) == 1


@pytest.mark.parametrize('limit,value', [('local_validation_max_depth', 8), ('local_validation_max_nodes', 8)])
def test_complexity_limit_is_explicit(limit, value):
    tree = copy.deepcopy(P)
    for _ in range(10):
        tree = {'op': 'not', 'args': [tree]}
    with pytest.raises(ValidationError, match=limit):
        validate_local(schema(), {'formula': tree}, {limit: value})


def test_hard_deadline_works_in_search_threads():
    slow = {'type': 'string', 'pattern': '^(P+)+$'}
    def reject():
        started = time.monotonic()
        with pytest.raises(ValidationError, match='local_validation_timeout_seconds'):
            validate_local(slow, 'P' * 40 + 'Q', {'local_validation_timeout_seconds': .5})
        assert time.monotonic() - started < 2
    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(reject)
        b = pool.submit(validate_local, schema(), {'formula': P})
        a.result(timeout=3)
        b.result(timeout=3)
    validate_local(schema(), {'formula': P})


def test_timeout_enters_native_correction(rig, monkeypatch):
    calls, provider, log = rig
    calls.config.update(validation_attempts=2, local_validation_timeout_seconds=.5)
    native = schema()
    native['$defs']['formula']['oneOf'][0]['properties']['name']['pattern'] = '^(P+)+$'
    monkeypatch.setattr(calls, 'response_schema', lambda *a: native)
    sent = []
    def complete(*args):
        sent.append(args)
        return Response(response({'formula': {'op': 'atom', 'name': 'P' * 40 + 'Q' if len(sent) == 1 else 'P'}}))
    monkeypatch.setattr(provider, 'complete', complete)
    assert calls.formalise(Proposition('p', 'P')).name == 'P'
    assert len(sent) == 2
    rejected = next(e for e in log.read() if e['label'] == 'MODEL')
    assert 'local_validation_timeout_seconds' in json.loads(rejected['payload_json'])['reason']


def random_trees():
    rng = random.Random(7)
    def tree(depth):
        op = rng.choice(['atom', 'predicate', 'not', 'and', 'or', 'implies', 'iff', 'forall', 'exists']) if depth else 'atom'
        node = {'op': op}
        if op in ('atom', 'predicate'):
            node['name'] = rng.choice(['P', 'Q', ''])
            if op == 'predicate':
                node['terms'] = [{'kind': rng.choice(['variable', 'constant', 'P']), 'name': 'a'}]
        else:
            node['args'] = [tree(depth - 1) for _ in range(rng.randrange(3))]
            if op in ('forall', 'exists'):
                node['variable'] = rng.choice(['a', '', None])
        if rng.random() < .2:
            node[rng.choice(['name', 'args', 'terms', 'variable', 'unknown'])] = rng.choice([None, 'P', 0, [], {}])
        return node
    invalid_mix = [tree(2) for _ in range(200)]
    def valid(depth):
        op = rng.choice(['atom', 'predicate', 'not', 'and', 'or', 'implies', 'iff', 'forall', 'exists']) if depth else 'atom'
        if op == 'atom':
            return {'op': op, 'name': rng.choice(['P', 'Q', 'R', 'S'])}
        if op == 'predicate':
            return {'op': op, 'name': 'F', 'terms': [{'kind': rng.choice(['constant', 'variable']), 'name': 'a'}]}
        count = 1 if op in ('not', 'forall', 'exists') else 2
        node = {'op': op, 'args': [valid(depth - 1) for _ in range(count)]}
        if op in ('forall', 'exists'):
            node['variable'] = 'a'
        return node
    return invalid_mix + [valid(3) for _ in range(80)]


def test_random_and_existing_formula_corpus_equivalence():
    import runpy
    PAYLOADS = runpy.run_path(str(ROOT / 'tests/test_schemas.py'))['PAYLOADS']
    from ara.types import Formula, Term
    p = Formula('atom', name='P')
    formulas = [p, Formula('not', (p,))] + [Formula(op, (p, p)) for op in ('and', 'or', 'implies', 'iff')]
    pred = Formula('predicate', name='F', terms=(Term('variable', 'a'), Term('constant', 'b')))
    formulas += [pred] + [Formula(op, (pred,), variable='a') for op in ('forall', 'exists')]
    corpus = [f.to_dict() for f in formulas] + random_trees()
    for tree in corpus:
        old = Draft202012Validator(schema()).is_valid({'formula': tree})
        from ara.runtime.validation import precheck
        try:
            precheck(schema(), {'formula': tree})
            new = LinearValidator(schema()).is_valid({'formula': tree})
        except ValidationError:
            new = False
        assert new == old, tree
    for kind, value in PAYLOADS.items():
        for candidate in (value, {}, {**value, 'unknown': 'P'}):
            assert LinearValidator(schema(kind)).is_valid(candidate) == Draft202012Validator(schema(kind)).is_valid(candidate)


def test_valid_deep_formula_and_native_constraints():
    value = copy.deepcopy(P)
    for _ in range(22):
        value = {'op': 'not', 'args': [value]}
    validate_local(schema(), {'formula': value})
    custom = schema()
    custom['$defs']['formula']['oneOf'][0]['properties']['name']['pattern'] = '^Q$'
    with pytest.raises(ValidationError):
        validate_local(custom, {'formula': P})


def test_codex_stall_normalization_and_native_rejection():
    from ara.runtime.codex_schema import normalize_output
    value = stall_shape()
    started = time.monotonic()
    normalized = normalize_output(schema(), value)
    with pytest.raises(ValidationError):
        validate_local(schema(), normalized)
    assert time.monotonic() - started < 2


@pytest.mark.parametrize('limit', ['local_validation_max_depth', 'local_validation_max_nodes'])
def test_complexity_rejection_enters_correction(rig, monkeypatch, limit):
    calls, provider, log = rig
    calls.config.update(validation_attempts=2, **{limit: 8})
    tree = copy.deepcopy(P)
    for _ in range(10):
        tree = {'op': 'not', 'args': [tree]}
    count = 0
    def complete(*args):
        nonlocal count
        count += 1
        return Response(response({'formula': tree if count == 1 else P}))
    monkeypatch.setattr(provider, 'complete', complete)
    assert calls.formalise(Proposition('p', 'P')).name == 'P'
    rejected = next(e for e in log.read() if e['label'] == 'MODEL')
    assert limit in json.loads(rejected['payload_json'])['reason']
    assert count == 2


def test_discriminator_requires_exclusive_required_tags():
    # Overlap and optional tags must retain normal oneOf semantics.
    for branches in ([{'type':'object'}, {'type':'object'}],
                     [{'type':'object', 'properties':{'op':{'const':'P'}}}] * 2):
        original = {'oneOf': branches}
        for value in ({}, {'op':'P'}, {'op':'Q'}, None):
            assert LinearValidator(original).is_valid(value) == Draft202012Validator(original).is_valid(value)


def test_each_formula_node_is_validated_once(monkeypatch):
    nodes = 0
    original = LinearValidator.VALIDATORS['oneOf']
    def counted(*args):
        nonlocal nodes
        nodes += 1
        yield from original(*args)
    monkeypatch.setitem(LinearValidator.VALIDATORS, 'oneOf', counted)
    value = copy.deepcopy(P)
    for _ in range(5):
        value = {'op': 'and', 'args': [value, copy.deepcopy(P)]}
    LinearValidator(schema()).validate({'formula': value})
    assert nodes == 11


def test_json_parser_depth_refusal_enters_correction(rig, monkeypatch):
    calls, provider, log = rig
    calls.config['validation_attempts'] = 2
    text = '{"formula":' + '{"op":"not","args":[' * 600 + '{"op":"atom","name":"P"}' + ']}' * 600 + '}'
    # C decoder depth limits vary by Python build; inject its documented failure.
    native_loads = json.loads
    def limited_loads(value, *args, **kwargs):
        if value == text:
            raise RecursionError('decoder depth limit')
        return native_loads(value, *args, **kwargs)
    monkeypatch.setattr(json, 'loads', limited_loads)
    count = 0
    def complete(*args):
        nonlocal count
        count += 1
        raw = response({'formula': P})
        if count == 1:
            raw['content'][0]['text'] = text
        return Response(raw)
    monkeypatch.setattr(provider, 'complete', complete)
    assert calls.formalise(Proposition('p', 'P')).name == 'P'
    assert count == 2
    rejected = next(e for e in log.read() if e['label'] == 'MODEL')
    assert 'local_validation_max_depth' in json.loads(rejected['payload_json'])['reason']
