"""Consistent support and equivalent-package gates through native search."""
import json
from dataclasses import replace

import pytest

from ara.bank import load_bank
from ara.runtime.cache import canonical
from ara.runtime.novelty import novelty_check
from ara.runtime.orchestration import NativeEngine, search_all
from ara.runtime.route_policy import route_contribution, selectable_routes
from ara.runtime.synthesis import forward_candidates
from ara.types import Commitment, CommitmentSet, Formula, Proposition, Term
from test_cross_paper import frozen_metadata
from test_per_paper_synthesis import freeze
from test_search_alignment import ROOT, P, Q, R, PQ, T, GOAL, cut, rig


QR = Formula('implies', (Q, R))
EX = Formula('exists', (QR,), variable='x')
WRAPPED = Formula('and', (P, EX))


@pytest.mark.parametrize('external', [False, True])
def test_native_quantified_package_is_not_selectable(tmp_path, external):
    t = CommitmentSet((Commitment('p', 'P', 'a:1', P), Commitment('qr', 'Q -> R', 'b:1', QR)))
    goal = Proposition('wrapped', 'P and exists x (Q -> R)', WRAPPED)
    def reply(kind, data):
        if kind == 'propose_targets': return dict(targets=[goal.to_dict()])
        if kind == 'classify_target':
            return dict(classification='own_thesis', novelty='new_assertion', fidelity='matches', reason='P Q R', resolves_gap=True)
        if kind == 'map_leaf':
            return dict(t_id=next((c['id'] for c in data['commitments']['commitments']
                if c['formula'] == data['leaf']['formula']), 'open'))
        if kind == 'propose_cuts':
            f = Formula.from_dict(data['goal']['formula'])
            if f == WRAPPED:
                bank, ps = 'conjunction_introduction', [('left', 'P', 'p'), ('right', 'exists x (Q -> R)', 'open')]
            elif f == EX:
                bank, ps = 'existential_generalisation', [('instance', 'Q -> R', 'qr')]
            else: return dict(proposals=[])
            return dict(proposals=[dict(bank_id=bank, conclusion_text=data['goal']['text'], conclusion_ref='current_goal',
                premises=[dict(slot=s, text=txt, t_id=tid, scope_id=None) for s, txt, tid in ps])])
        if kind == 'formalise_slots':
            return dict(slots=[dict(slot=b['slot'], formula=b['formula'] or EX.to_dict()) for b in data['slot_bindings']])
        raise AssertionError(kind)
    calls, _ = rig(tmp_path, reply)
    calls.config.update(node_cap=40, forward_pass_depth=0, semantic_conflict_pair_limit=0)
    meta = freeze(calls, t, ('a', 'b'))
    if external:
        gap = dict(id='wrapped', origin='AI-found', priority=0, finding='P Q R', paper_ids=['a', 'b'],
            commitment_ids=['p', 'qr'], support_groups=[['p'], ['qr']],
            evidence=[dict(source_id='a', location='1', finding='P')], currency_verdict='partial',
            search_scope='placeholder', claim_framing='P Q R')
        path = tmp_path/'gaps.json'; path.write_text(canonical(dict(schema_version='external-gaps-v1', gaps=[gap])))
        calls.config['gap_file'] = str(path)
    targets = calls.propose_targets(t, 1)
    routes = search_all(calls, NativeEngine(load_bank(ROOT/'bank'), calls), t, (goal,))
    closed = [r for r in routes if r.status == 'CLOSED']
    assert closed
    assert all(route_contribution(r, t, meta)['classification'] == 'CLOSED-structural' for r in closed)
    assert not selectable_routes(routes, t, meta)
    assert not targets
    if external:
        assert any(e['stage'] == 'external_gaps_loaded' for e in calls.log.read())


def test_native_unused_contradiction_preserves_modus_ponens(tmp_path):
    t = CommitmentSet(T.commitments + (Commitment('r', 'R', 'c:1', R), Commitment('nr', 'not R', 'd:1', R.negated())))
    def reply(kind, data):
        if kind == 'propose_targets': return dict(targets=[GOAL.to_dict()])
        if kind == 'classify_target':
            return dict(classification='own_thesis', novelty='new_assertion', fidelity='matches', reason='Q', resolves_gap=False)
        if kind == 'map_leaf':
            return dict(t_id=next((c['id'] for c in data['commitments']['commitments']
                if c['formula'] == data['leaf']['formula']), 'open'))
        if kind == 'propose_cuts': return dict(proposals=[cut()] if data['goal']['formula'] == Q.to_dict() else [])
        if kind == 'formalise_slots':
            return dict(slots=[dict(slot=b['slot'], formula=b['formula']) for b in data['slot_bindings']])
        raise AssertionError(kind)
    calls, requests = rig(tmp_path, reply)
    calls.config.update(node_cap=30, forward_pass_depth=1, forward_candidate_node_cap=30, semantic_conflict_pair_limit=0)
    meta = freeze(calls, t, ('a', 'b', 'c', 'd'))
    targets = calls.propose_targets(t, 1)
    routes = search_all(calls, NativeEngine(load_bank(ROOT/'bank'), calls), t, (GOAL,))
    selected = selectable_routes(routes, t, meta)
    assert selected and targets and targets[0].formula == Q
    receipt = route_contribution(selected[0], t, meta)
    assert receipt['support_consistency']['status'] == 'consistent'
    assert receipt['per_paper_novelty']['union_basis_commitment_ids'] == ['t1', 't2']
    assert any(c['formula'] == Q.to_dict() for k, d in requests if k == 'propose_targets' for c in d['forward_candidates'])
    gaps = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'gaps_detected']
    assert any(g['kind'] == 'contradiction' and set(g['commitment_ids']) == {'r', 'nr'} for p in gaps for g in p['gaps'])
    preflight = [json.loads(e['payload_json'])['novelty'] for e in calls.log.read() if e['stage'] == 'target_contribution_preflight']
    assert all(p['consistent_basis']['status'] == 'consistent' for p in preflight)
    assert all(set(p['consistent_basis']['omitted_commitment_ids']) in ({'r'}, {'nr'}) for p in preflight)


def test_maximal_consistent_basis_preserves_required_ids_deterministically():
    t = CommitmentSet(T.commitments + (Commitment('r', 'R', 'c:1', R), Commitment('nr', 'not R', 'd:1', R.negated())))
    _, meta = frozen_metadata(t, ('a', 'b', 'c', 'd'))
    receipt = novelty_check(Q, t, meta, basis_ids=('t1', 't2', 'r'))
    reverse = novelty_check(Q, CommitmentSet(tuple(reversed(t.commitments))), meta, basis_ids=('r', 't2', 't1'))
    assert receipt == reverse
    assert receipt['status'] == 'candidate'
    assert receipt['consistent_basis']['selected_commitment_ids'] == ['r', 't1', 't2']
    assert receipt['consistent_basis']['omitted_commitment_ids'] == ['nr']
    assert novelty_check(Q, t, meta, basis_ids=('r', 'nr'))['reason'] == 'inconsistent_basis'
    assert novelty_check(Q, t, meta, basis_ids=('missing',))['status'] == 'unresolved'


def test_equivalent_packages_without_vacuous_binders_are_rejected():
    t = CommitmentSet((Commitment('p', 'P', 'a:1', P), Commitment('qr', 'Q -> R', 'b:1', QR)))
    _, meta = frozen_metadata(t, ('a', 'b'))
    equivalent = Formula('and', (P, Formula('or', (Q.negated(), R))))
    receipt = novelty_check(equivalent, t, meta)
    assert receipt['status'] == 'rejected'
    assert receipt['boolean_package']['solver_result'] == 'SOLVER_UNSAT'
    assert novelty_check(R, t, meta)['status'] == 'candidate'


def test_real_quantifier_is_not_erased():
    x = Term('variable', 'x')
    body = Formula('predicate', name='F', terms=(x,))
    from ara.runtime.novelty_basis import drop_vacuous_quantifiers
    assert drop_vacuous_quantifiers(Formula('exists', (body,), variable='x')).op == 'exists'
    assert drop_vacuous_quantifiers(Formula('exists', (QR,), variable='x')) == QR


def test_native_inconsistent_cq_support_is_a_conflict(tmp_path):
    from ara.runtime.conflict_feedback import conflict_report
    t = CommitmentSet(T.commitments + (Commitment('nq', 'not Q', 'c:1', Q.negated()),))
    goal = Proposition('r', 'R', R)
    def reply(kind, data):
        if kind == 'map_leaf': return dict(t_id='open')
        if kind == 'propose_cuts':
            if data['goal']['formula'] != R.to_dict(): return dict(proposals=[])
            return dict(proposals=[dict(bank_id='sign', conclusion_text='R', conclusion_ref='current_goal',
                premises=[dict(slot='sign_relation', text='P -> Q', t_id='t2', scope_id=None),
                          dict(slot='observed_sign', text='P', t_id='t1', scope_id=None)])])
        if kind == 'formalise_slots':
            return dict(slots=[dict(slot=b['slot'], formula=b['formula']) for b in data['slot_bindings']])
        if kind == 'answer_cq':
            return dict(cq_id=data['question']['id'], answered=True, answer='P Q', supporting_t_ids=['t1', 't2', 'nq'])
        if kind == 'propose_targets': return dict(targets=[goal.to_dict()])
        if kind == 'classify_target':
            return dict(classification='own_thesis', novelty='new_assertion', fidelity='matches', reason='R', resolves_gap=True)
        raise AssertionError(kind)
    calls, _ = rig(tmp_path, reply)
    calls.config.update(node_cap=30, forward_pass_depth=0, semantic_conflict_pair_limit=0)
    meta = freeze(calls, t, ('a', 'b', 'c'))
    routes = search_all(calls, NativeEngine(load_bank(ROOT/'bank'), calls), t, (goal,))
    closed = [r for r in routes if r.status == 'CLOSED']
    assert closed
    assert all(route_contribution(r, t, meta)['classification'] == 'CLOSED-conflict' for r in closed)
    assert not selectable_routes(routes, t, meta)
    conflicts = conflict_report(calls.log.read())['support_conflicts']
    assert conflicts and set(conflicts[0]['commitment_ids']) == {'t1', 't2', 'nq'}
    assert any(g.route_ids for g in calls.discover_gaps(t)['gaps'])
    from ara.runtime.orchestration import compose
    with pytest.raises(ValueError, match='inconsistent'):
        compose(calls, closed[0])
    assert any(e['stage'] == 'composition_refused' for e in calls.log.read())


def test_forward_rejects_quantified_packages_and_keeps_alignment_lead(tmp_path, monkeypatch):
    from ara.runtime.orchestration import prepare_commitments
    t = CommitmentSet((Commitment('p', 'P', 'a:1', P), Commitment('qr', 'Q -> R', 'b:1', QR)))
    artifact, meta = frozen_metadata(t, ('a', 'b'), {'P': 'P Q', 'Q': 'P Q'})
    def reply(kind, data):
        if kind == 'judge_symbol_alignment':
            left, right = (data['candidate'][side]['name'] for side in ('left', 'right'))
            return dict(left=left, right=right, relation='entails_left_right' if (left, right) == ('P', 'Q') else 'unrelated', reason='P Q')
        if kind == 'propose_targets': return dict(targets=[Proposition('r', 'R', R).to_dict()])
        if kind == 'classify_target':
            return dict(classification='own_thesis', novelty='new_assertion', fidelity='matches', reason='R')
        raise AssertionError(kind)
    calls, requests = rig(tmp_path, reply)
    (tmp_path/'frozen-t.json').unlink()  # This regression starts before construction's only freeze.
    calls.config.update(forward_pass_depth=2, forward_candidate_node_cap=500, semantic_conflict_pair_limit=0)
    monkeypatch.setattr(calls, 'build_t', lambda *_: t)
    calls.log.record('build_t_merged', commitments=t.to_dict(), symbols=artifact['symbol_catalogue']['symbols'],
                     provenance=meta['commitments'])
    aligned = prepare_commitments(calls, load_bank(ROOT/'bank'), 'P', 'P')
    vocabulary = calls.search_vocabulary(aligned)
    assert vocabulary['commitment_provenance']['alignment']['status'] == 'accepted'
    before = {name: (tmp_path/name).read_bytes() for name in ('commitments.json', 'frozen-t.json', 'commitment-provenance.json')}
    targets = calls.propose_targets(aligned, 1)
    assert targets and targets[0].formula == R
    result = next(json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'forward_target_candidates')
    assert not any(c['formula'] == WRAPPED.to_dict() for c in result['candidates'])
    shown = next(d['forward_candidates'] for k, d in requests if k == 'propose_targets')
    assert any(c['formula'] == R.to_dict() for c in shown)
    receipts = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'target_contribution_preflight']
    assert receipts[0]['novelty']['consistent_basis']['required_commitment_ids'] == next(c['support_ids'] for c in shown if c['formula'] == R.to_dict())
    assert before == {name: (tmp_path/name).read_bytes() for name in before}


def test_declared_basis_survives_codec_and_rejects_joint_conflict(tmp_path):
    from ara.runtime.target_policy import trivial_targets
    from ara.runtime.validation import validate_local
    from ara.types import negate_proposition
    t = CommitmentSet(T.commitments + (Commitment('r', 'R', 'c:1', R), Commitment('nr', 'not R', 'd:1', R.negated())))
    _, meta = frozen_metadata(t, ('a', 'b', 'c', 'd'))
    goal = replace(GOAL, basis_commitment_ids=('t1', 't2', 'r'))
    assert Proposition.from_dict(goal.to_dict()) == goal
    assert negate_proposition(goal).basis_commitment_ids == goal.basis_commitment_ids
    assert 'basis_commitment_ids' not in GOAL.to_dict()
    schema = json.loads((ROOT/'schemas/propose_targets.json').read_text())
    validate_local(schema, {'targets': [goal.to_dict()]})
    receipts = []
    assert not trivial_targets((goal,), t, receipts=receipts, provenance=meta)
    assert receipts[0]['novelty']['consistent_basis']['required_commitment_ids'] == ['r', 't1', 't2']
    bad = replace(goal, basis_commitment_ids=('r', 'nr'))
    assert trivial_targets((bad,), t, provenance=meta)[0]['reason'] == 'inconsistent_basis'


def test_solver_uncertainty_never_certifies_a_consistent_basis_or_package(monkeypatch):
    import ara.runtime.novelty_basis as module
    _, meta = frozen_metadata(T, ('a', 'b'))
    monkeypatch.setattr(module, 'cached_entails', lambda *args: 'SOLVER_UNKNOWN')
    assert novelty_check(Q, T, meta)['status'] == 'unresolved'
    monkeypatch.undo()
    monkeypatch.setattr(module, '_package_equivalence', lambda *args: 'SOLVER_TIMEOUT')
    assert novelty_check(Q, T, meta)['status'] == 'unresolved'


def test_internal_paper_conflict_does_not_entail_an_unused_target():
    t = CommitmentSet(T.commitments + (Commitment('r', 'R', 'c:1', R), Commitment('nr', 'not R', 'c:2', R.negated())))
    _, meta = frozen_metadata(t, ('a', 'b', 'c', 'c'))
    receipt = novelty_check(Q, t, meta, support_ids=('t1', 't2'))
    assert receipt['status'] == 'candidate'
    assert len(receipt['paper_bases']['c']['omitted_commitment_ids']) == 1


def test_recorded_forward_conflicting_supports_are_disclosed(tmp_path):
    from ara.engine.forward import Consequence, ForwardResult
    t = CommitmentSet((Commitment('p', 'P', 'a:1', P), Commitment('np', 'not P', 'b:1', P.negated())))
    calls, _ = rig(tmp_path, lambda *args: pytest.fail('forward dispatched a model'))
    meta = freeze(calls, t, ('a', 'b'))
    conjunction = Formula('and', (P, P.negated()))
    observed = ForwardResult((Consequence(conjunction, 'conjunction_introduction', (P, P.negated()), 1, False),), False)
    result = forward_candidates(t, meta, load_bank(ROOT/'bank'), calls.log, depth=0, node_cap=10, observed=(observed,))
    assert not result['candidates']
    conflict = next(c for c in result['support_conflicts'] if c['formula'] == conjunction.to_dict())
    assert conflict['consistency']['status'] == 'conflict'
    assert conflict['support_ids'] == ['np', 'p']


def test_missing_route_support_inventory_remains_unresolved():
    from test_contribution_gate import closed_graph
    incomplete = CommitmentSet((T.commitments[0],))
    receipt = route_contribution(closed_graph(), incomplete)
    assert receipt['support_consistency']['status'] == 'unresolved'
    assert receipt['classification'] == 'CLOSED-contribution-unresolved'
