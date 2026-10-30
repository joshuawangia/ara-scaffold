"""Declared target evidence stays model-visible through native counted search."""
from dataclasses import replace
import json

import pytest

from ara.runtime.cache import canonical
from ara.runtime.budget import BudgetStop
from ara.types import Commitment, CommitmentSet, Formula, Proposition, TokenUsage, negate_proposition
from test_cross_paper import frozen_metadata
from test_search_alignment import P, Q, R, rig
from test_search_context import invoke
from test_search_failures import payloads


def setup(tmp_path):
    calls, requests = rig(tmp_path, lambda kind, data:
        {'t_id': 'open'} if kind == 'map_leaf' else {'proposals': []})
    s = Formula('atom', name='S')
    formulas = (Q, R, s, Formula('implies', (Q, R)), Formula('implies', (R, s)), Formula('implies', (s, Q)))
    t = CommitmentSet(tuple(Commitment(f'a{i:02}', 'P', f'{i}:1', P) for i in range(20)) +
        tuple(Commitment(f'z{i}', f.canonical(), f'{i+20}:1', f) for i,f in enumerate(formulas)))
    artifact, provenance = frozen_metadata(t, tuple(str(i) for i in range(26)))
    (tmp_path/'frozen-t.json').write_text(canonical(artifact))
    (tmp_path/'commitment-provenance.json').write_text(canonical(provenance))
    goal = Proposition('f', 'F', Formula('atom', name='F'), basis_commitment_ids=tuple(f'z{i}' for i in range(6)))
    return calls, requests, t, goal


@pytest.mark.parametrize('kind', ['map_leaf', 'propose_cuts'])
@pytest.mark.parametrize('negative', [False, True])
@pytest.mark.parametrize('force_zero', [False, True])
def test_declared_six_support_basis_survives_native_leaf_packing(tmp_path, monkeypatch, kind, negative, force_zero):
    # Receipt-shaped reproduction: unrelated root atoms and six late source IDs.
    calls, requests, t, goal = setup(tmp_path)
    if negative: goal = negate_proposition(goal)
    if force_zero:
        calls.config['model_context_token_bound'] = 20000
        def count(stage, prompt, schema, maximum):
            data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
            return TokenUsage(input_tokens=20001 if data['search_slice']['bridge_limit'] else 100, output_tokens=maximum)
        monkeypatch.setattr(calls.provider, 'estimate', count)
    invoke(calls, kind, goal, t)
    data = requests[-1][1]
    selected = {c['id'] for c in data['commitments']['commitments']}
    assert set(goal.basis_commitment_ids) <= selected
    receipt = payloads(calls.log, 'search_context_slice')[-1]
    assert receipt['basis_context']['basis_commitment_ids'] == list(goal.basis_commitment_ids)
    assert set(goal.basis_commitment_ids) <= set(receipt['basis_context']['mandatory_commitment_ids'])
    assert receipt['basis_context']['basis_coverage'] == 1.0
    if force_zero: assert data['search_slice']['bridge_limit'] == 0


def test_distinct_targets_seed_distinct_formal_neighbourhoods(tmp_path):
    calls, requests, t, goal = setup(tmp_path)
    calls.config['target_context_hops'] = 1
    for tid in ('a00','z0'):
        invoke(calls, 'map_leaf', replace(goal, id=tid, basis_commitment_ids=(tid,)), t)
    contexts = [d['search_slice']['basis_context'] for _, d in requests]
    assert set(contexts[0]['mandatory_commitment_ids']) == {f'a{i:02}' for i in range(20)}
    assert set(contexts[1]['mandatory_commitment_ids']) == {'z0','z3','z5'}


def test_oversized_mandatory_basis_refuses_with_breakdown(tmp_path, monkeypatch):
    calls, requests, t, goal = setup(tmp_path)
    def count(stage, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        complete = set(goal.basis_commitment_ids) <= {c['id'] for c in data['commitments']['commitments']}
        return TokenUsage(input_tokens=200001 if complete else 1, output_tokens=maximum)
    monkeypatch.setattr(calls.provider, 'estimate', count)
    with pytest.raises(BudgetStop) as caught: invoke(calls, 'map_leaf', goal, t)
    assert caught.value.scope == 'search' and calls.budget._halted is None
    assert requests == []
    receipt = payloads(calls.log, 'search_context_slice')[-1]
    assert receipt['decision'] == 'refused' and receipt['bridge_limit'] == 0
    assert receipt['basis_context']['basis_coverage'] == 1.0
    assert receipt['field_bytes']['commitments'] > 0


def test_unknown_declared_basis_refuses_before_dispatch(tmp_path):
    calls, requests, t, goal = setup(tmp_path)
    with pytest.raises(ValueError, match='unknown frozen commitment'):
        invoke(calls, 'map_leaf', replace(goal, basis_commitment_ids=('absent',)), t)
    assert requests == []


def test_parallel_child_leaves_keep_their_own_target_basis(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from ara.runtime.logging import SerializedEventLog
    from ara.runtime.search_publication import SearchPublication
    calls, requests, t, goal = setup(tmp_path)
    goals = [replace(goal, id=tid, basis_commitment_ids=(tid,)) for tid in ('a00','z0')]
    barrier = Barrier(2)
    original = calls.log
    with SerializedEventLog(original) as writer:
        calls.log = writer
        publication = SearchPublication(writer, goals)
        def child_search(root):
            barrier.wait(timeout=10)
            calls.map_leaf(Proposition('child','F', goal.formula), t)
        with ThreadPoolExecutor(2) as pool:
            list(pool.map(lambda i: publication.run(i, child_search, goals[i]), range(2)))
        publication.publish()
    calls.log = original
    assert len(requests) == 2
    for _, data in requests:
        basis = data['search_slice']['basis_context']
        assert basis['basis_commitment_ids'] == [basis['target_id']]
        assert basis['target_id'] in {c['id'] for c in data['commitments']['commitments']}
    calls.map_leaf(Proposition('unscoped','F',goal.formula), t)
    assert 'basis_context' not in requests[-1][1]['search_slice']


def test_alignment_neighbourhood_keeps_source_evidence_and_disclosed_relations():
    from ara.runtime.search_context import basis_neighbourhood
    from ara.runtime.search_alignment import symbols
    from test_symbol_alignment import fixture, judgment
    from ara.runtime.symbol_alignment import apply_judgments
    t, catalogue, rows = fixture()
    t, catalogue, rows, _ = apply_judgments(t, catalogue, rows, [judgment(relation='entails_left_right')])
    bridge = t.commitments[-1].id
    inputs = dict(goal=Proposition('s','S',Formula('atom',name='S'),basis_commitment_ids=('P',)).to_dict(),
        commitment_provenance=dict(commitments=rows),
        alignment_disclosure=dict(status='accepted', judgments=[judgment(relation='entails_left_right')]))
    signatures = {c.id: set(symbols(c.formula)) for c in t.commitments}
    selected, receipt = basis_neighbourhood(inputs, signatures, 1)
    assert selected == {'P','Q',bridge}
    inputs['goal']['basis_commitment_ids'] = [bridge]
    selected, _ = basis_neighbourhood(inputs, signatures, 0)
    assert selected == {'P','Q',bridge}
