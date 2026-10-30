"""Cross-paper novelty cannot be supplied by an irrelevant package wrapper."""
import pytest

from ara.bank import load_bank
from ara.runtime.cache import canonical
from ara.runtime.novelty import novelty_check
from ara.runtime.orchestration import NativeEngine, search_all
from ara.runtime.route_policy import route_contribution, selectable_routes
from ara.runtime.synthesis import forward_candidates
from ara.types import Commitment, CommitmentSet, Formula, Proposition, SymbolDefinition
from test_cross_paper import frozen_metadata
from test_per_paper_synthesis import freeze
from test_search_alignment import ROOT, P, Q, R, PQ, rig


PACKAGE = Formula('and', (P, Q))
PADDED_OR = Formula('or', (PACKAGE, R))
PADDED_IF = Formula('implies', (R, PACKAGE))


@pytest.mark.parametrize('external', [False, True])
@pytest.mark.parametrize('case', ['padded_or', 'padded_if', 'fresh_scheme', 'modus_ponens'])
def test_native_union_essentiality_proposal_selection_and_gap_file(tmp_path, case, external):
    formula = {'padded_or': PADDED_OR, 'padded_if': PADDED_IF,
               'fresh_scheme': R, 'modus_ponens': Q}[case]
    text = {'padded_or': '(P and Q) or R', 'padded_if': 'R -> (P and Q)',
            'fresh_scheme': 'R', 'modus_ponens': 'Q'}[case]
    goal = Proposition('target', text, formula,
        () if case == 'modus_ponens' else (SymbolDefinition('R', 'atom', 0, 'R'),))
    t = CommitmentSet((Commitment('p', 'P', 'a:1', P),
        Commitment('q', 'P -> Q' if case == 'modus_ponens' else 'Q', 'b:1',
                   PQ if case == 'modus_ponens' else Q)))
    texts = {'P': P, 'Q': Q, 'R': R, 'P and Q': PACKAGE, 'P -> Q': PQ}
    def reply(kind, data):
        if kind == 'classify_conflict':
            return dict(classification='compatible', reason='P Q')
        if kind == 'propose_targets':
            return dict(targets=[goal.to_dict()])
        if kind == 'classify_target':
            verdict = dict(classification='own_thesis', novelty='new_assertion', fidelity='matches', reason='P Q R')
            if external:
                verdict['resolves_gap'] = True
            return verdict
        if kind == 'map_leaf':
            return dict(t_id=next((c['id'] for c in data['commitments']['commitments']
                if c['formula'] == data['leaf']['formula']), 'open'))
        if kind == 'propose_cuts':
            f = Formula.from_dict(data['goal']['formula'])
            if f == PADDED_OR:
                bank, ps = 'disjunction_introduction', [('disjunct', 'P and Q', 'open', None)]
            elif f == PADDED_IF:
                bank, ps = 'conditional_proof', [('assumption', 'R', 'open', 'conditional'),
                    ('result', 'P and Q', 'open', 'conditional')]
            elif f == PACKAGE:
                bank, ps = 'conjunction_introduction', [('left', 'P', 'p', None), ('right', 'Q', 'q', None)]
            elif f == R:
                bank, ps = 'sign', [('sign_relation', 'P', 'p', None), ('observed_sign', 'Q', 'q', None)]
            elif f == Q and case == 'modus_ponens':
                bank, ps = 'modus_ponens', [('conditional', 'P -> Q', 'q', None), ('antecedent', 'P', 'p', None)]
            else:
                return dict(proposals=[])
            return dict(proposals=[dict(bank_id=bank, conclusion_text=data['goal']['text'], conclusion_ref='current_goal',
                premises=[dict(slot=s, text=txt, t_id=tid, scope_id=scope) for s, txt, tid, scope in ps])])
        if kind == 'formalise_slots':
            return dict(slots=[dict(slot=b['slot'], formula=b['formula'] or texts[b['text']].to_dict())
                for b in data['slot_bindings']])
        if kind == 'answer_cq':
            return dict(cq_id=data['question']['id'], answered=True, answer='P Q', supporting_t_ids=['p', 'q'])
        raise AssertionError(kind)
    calls, requests = rig(tmp_path, reply)
    calls.config.update(node_cap=50, forward_pass_depth=0)
    provenance = freeze(calls, t, ('a', 'b'))
    if external:
        gap = dict(id='pad', origin='AI-found', priority=0, finding='P Q', paper_ids=['a', 'b'],
            commitment_ids=['p', 'q'], support_groups=[['p'], ['q']],
            evidence=[dict(source_id='a', location='1', finding='P')], currency_verdict='partial',
            search_scope='2018–2026', claim_framing='not found within the stated scope; partially anticipated by P')
        path = tmp_path/'gaps.json'
        path.write_text(canonical(dict(schema_version='external-gaps-v1', gaps=[gap])))
        calls.config['gap_file'] = str(path)
    targets = calls.propose_targets(t, 1)
    # Explicit historical targets still get native bank licensing and route policy.
    routes = search_all(calls, NativeEngine(load_bank(ROOT/'bank'), calls), t, (goal,))
    closed = [r for r in routes if r.status == 'CLOSED']
    assert closed
    positive = case in ('fresh_scheme', 'modus_ponens')
    receipts = [route_contribution(r, t, provenance) for r in closed]
    assert all(r['classification'] == ('CLOSED-derived' if positive else 'CLOSED-structural') for r in receipts)
    assert bool(selectable_routes(routes, t, provenance)) == positive
    assert bool(targets) == positive
    if external:
        proposed = next(d for k, d in requests if k == 'propose_targets')
        assert proposed['resolution_gap']['id'] == 'external:pad'
        assert any(e['stage'] == 'external_gaps_loaded' for e in calls.log.read())
        if positive:
            assert targets[0].gap.id == 'external:pad'
    if not positive:
        for receipt in receipts:
            novelty = receipt['per_paper_novelty']
            assert novelty['reason'] == 'no_essential_new_proposition'
            union = [c for c in novelty['checks'] if c['scope'] == 'essential_atom_union']
            assert {c['substituted_truth'] for c in union} == {True, False}
            assert all(c['solver_result'] == 'SOLVER_UNSAT' for c in union)


def test_forward_union_essentiality_removes_padded_packages(tmp_path):
    s = Formula('atom', name='S')
    t = CommitmentSet((Commitment('p', 'P', 'a:1', P), Commitment('q', 'Q', 'b:1', Q),
        Commitment('rs', 'R -> S', 'c:1', Formula('implies', (R, s)))))
    calls, _ = rig(tmp_path, lambda *args: pytest.fail('forward dispatched a model'))
    provenance = freeze(calls, t, ('a', 'b', 'c'))
    from ara.engine.forward import Consequence, ForwardResult
    disjunction = Formula('or', (Q, R))
    padded = Formula('and', (P, disjunction))
    # Historical/route-witness packages still need the novelty gate even though
    # fresh enumeration no longer generates them as standalone discoveries.
    observed = ForwardResult((
        Consequence(disjunction, 'disjunction_introduction', (Q,), 1, False),
        Consequence(padded, 'conjunction_introduction', (P, disjunction), 2, False)), False)
    result = forward_candidates(t, provenance, load_bank(ROOT/'bank'), calls.log,
                                depth=2, node_cap=500, observed=(observed,))
    assert result['licensed_consequences'] == 0
    assert result['observed_scanned'] == 2
    assert not any(c['formula'] == padded.to_dict() for c in result['candidates'])
    assert not any(c['formula'] in (PADDED_OR.to_dict(), PADDED_IF.to_dict()) for c in result['candidates'])


@pytest.mark.parametrize('positive', [False, True])
def test_union_entailment_preserves_both_polarities(positive):
    goal = Q if positive else Q.negated()
    t = CommitmentSet((Commitment('p', 'P', 'a:1', P),
        Commitment('q', 'P -> Q' if positive else 'P -> not Q', 'b:1', Formula('implies', (P, goal)))))
    _, provenance = frozen_metadata(t, ('a', 'b'))
    receipt = novelty_check(goal, t, provenance)
    assert receipt['status'] == 'candidate'
    assert receipt['union_basis_commitment_ids'] == ['p', 'q']
    checks = [c for c in receipt['checks'] if c['scope'] == 'essential_atom_union']
    assert {c['substituted_truth'] for c in checks} == {True, False}
    assert any(c['substituted_truth'] != positive and c['solver_result'] == 'SOLVER_COUNTEREXAMPLE' for c in checks)


def test_union_essentiality_unknown_refuses(monkeypatch):
    import ara.runtime.novelty as module
    t = CommitmentSet((Commitment('p', 'P', 'a:1', P), Commitment('q', 'P -> Q', 'b:1', PQ)))
    _, provenance = frozen_metadata(t, ('a', 'b'))
    original = module.cached_entails
    def timeout_union(premises, goal, timeout):
        if len(premises) == 2 and goal.op == 'iff':
            return 'SOLVER_TIMEOUT'
        return original(premises, goal, timeout)
    monkeypatch.setattr(module, 'cached_entails', timeout_union)
    assert novelty_check(Q, t, provenance)['status'] == 'unresolved'
