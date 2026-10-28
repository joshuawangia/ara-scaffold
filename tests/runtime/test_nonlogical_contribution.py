"""Native kappa4 probes: logical detours cannot supply a new scheme conclusion."""
import pytest
from ara.bank import load_bank
from ara.runtime.cache import canonical
from ara.runtime.commitment_provenance import make_commitment_provenance
from ara.runtime.frozen_catalogue import frozen_artifact
from ara.runtime.orchestration import NativeEngine, search_all
from ara.runtime.route_policy import route_contribution, selectable_routes
from ara.types import Commitment, CommitmentSet, Formula as F, Proposition, SymbolDefinition, Term
from test_search_alignment import rig, ROOT, P, Q, R

S = F('atom', name='S')
T = CommitmentSet((Commitment('t1', 'P or Q', 'placeholder:1', F('or', (P, Q))),
                   Commitment('t2', 'S', 'placeholder:2', S)))
RQ, RS, SQ = (F('implies', pair) for pair in ((R, Q), (R, S), (S, Q)))
QS = F('and', (Q, S))
QSR = F('and', (QS, R))
TEXTS = {'P or Q': T.commitments[0].formula, 'Q': Q, 'R': R, 'S': S,
         'R -> Q': RQ, 'R -> S': RS, 'S -> Q': SQ, 'Q and S': QS, 'Q and S and R': QSR}


def frozen_calls(tmp_path, reply):
    calls, _ = rig(tmp_path, reply)
    calls.config['forward_pass_depth'] = 0
    artifact = frozen_artifact(T, [dict(name=n, kind='atom', arity=0, definition=n,
        evidence_ids=['t1'] if n in ('P', 'Q') else ['t2']) for n in ('P', 'Q', 'S')])
    provenance = make_commitment_provenance(T, artifact['symbol_catalogue'], {
        c.id: dict(source_id=source, source_authors=[], attributed_to=source,
            page_start=1, page_end=1, evidence_id=c.id, attribution='author_claim', stance='endorsed',
            source_kind='premise', source_text=c.text, omitted_support_ids=[])
        for c, source in zip(T.commitments, ('a', 'b'))})
    (tmp_path/'frozen-t.json').write_text(canonical(artifact))
    (tmp_path/'commitment-provenance.json').write_text(canonical(provenance))
    (tmp_path/'commitments.json').write_text(T.to_json())
    calls.log.record('run_started', config=calls.config, topic='P Q R S', bank_version='1.0.0')
    calls.log.record('symbol_catalogue_frozen', **artifact['symbol_catalogue'])
    calls.log.record('commitment_provenance_frozen', **provenance)
    calls.log.record('commitments_frozen', commitments=T.to_dict(), bank_version='1.0.0')
    return calls, provenance


@pytest.mark.parametrize('proof', ['old_vocabulary', 'unadorned', 'matching_core', 'padded', 'syllogism', 'genuine'])
def test_native_only_new_scheme_conclusion_qualifies(tmp_path, proof):
    formula = Q if proof == 'old_vocabulary' else R if proof == 'genuine' else RQ
    goal = Proposition('target', next(t for t, f in TEXTS.items() if f == formula), formula,
                       () if formula == Q else (SymbolDefinition('R', 'atom', 0, 'R'),))
    def reply(kind, inputs):
        if kind == 'propose_targets': return dict(targets=[goal.to_dict()])
        if kind == 'classify_target':
            return dict(classification='own_thesis', novelty='new_assertion', fidelity='matches', reason='R')
        if kind == 'map_leaf': return dict(t_id='open')
        if kind == 'propose_cuts':
            f = F.from_dict(inputs['goal']['formula'])
            if f == RQ and proof == 'syllogism':
                scheme, ps = 'hypothetical_syllogism', [('first', 'R -> S', 'open', None), ('second', 'S -> Q', 'open', None)]
            elif f in (RQ, RS, SQ):
                a, b = ('R', 'Q') if f == RQ else ('R', 'S') if f == RS else ('S', 'Q')
                scheme, ps = 'conditional_proof', [('assumption', a, 'open', 'conditional'),
                    ('result', b, 't2' if f == RS else 'open', 'conditional')]
            elif f == Q and proof in ('padded', 'matching_core'):
                scheme, ps = 'conjunction_elimination', [('conjunction', 'Q and S and R' if proof == 'padded' else 'Q and S', 'open', None)]
            elif f == QSR:
                scheme, ps = 'conjunction_introduction', [('left', 'Q and S', 'open', None), ('right', 'R', 'open', None)]
            elif f in (Q, QS) or (f == R and proof == 'genuine'):
                scheme, ps = 'sign', [('sign_relation', 'P or Q', 't1', None), ('observed_sign', 'S', 't2', None)]
            else: return dict(proposals=[])
            return dict(proposals=[dict(bank_id=scheme, conclusion_text=inputs['goal']['text'], conclusion_ref='current_goal',
                premises=[dict(slot=s, text=t, t_id=i, scope_id=sc) for s, t, i, sc in ps])])
        if kind == 'formalise_slots':
            return dict(slots=[dict(slot=b['slot'], formula=b['formula'] or TEXTS[b['text']].to_dict()) for b in inputs['slot_bindings']])
        if kind == 'answer_cq':
            return dict(cq_id=inputs['question']['id'], answer='P Q S', answered=True, supporting_t_ids=['t1', 't2'])
        raise AssertionError(kind)
    calls, provenance = frozen_calls(tmp_path, reply)
    assert calls.propose_targets(T, 1) == (() if proof == 'old_vocabulary' else (goal,))
    # Explicit historical targets still run through native licensing and closure.
    routes = search_all(calls, NativeEngine(load_bank(ROOT/'bank'), calls), T, (goal,))
    closed = [r for r in routes if r.status == 'CLOSED']
    assert closed
    for route in closed:
        receipt = route_contribution(route, T, provenance)
        assert receipt['classification'] == ('CLOSED-derived' if proof == 'genuine' else 'CLOSED-structural')
        assert [s['bank_id'] for s in receipt['substantive_inferences']] == (['sign'] if proof == 'genuine' else [])
    assert bool(selectable_routes(routes, T, provenance)) == (proof == 'genuine')


def test_native_deduction_remains_closed_but_structural(tmp_path):
    from test_search_alignment import T as deductive, GOAL, cut, PQ
    def reply(kind, inputs):
        if kind == 'map_leaf': return dict(t_id='open')
        if kind == 'propose_cuts': return dict(proposals=[cut()] if inputs['goal']['formula'] == Q.to_dict() else [])
        if kind == 'formalise_slots':
            return dict(slots=[dict(slot='conditional', formula=PQ.to_dict()), dict(slot='antecedent', formula=P.to_dict())])
        raise AssertionError(kind)
    calls, _ = rig(tmp_path, reply)
    routes = NativeEngine(load_bank(ROOT/'bank'), calls)._engine(deductive).search(GOAL).routes
    assert routes[0].status == 'CLOSED'
    assert routes[0].nodes[0].proposal.bank_id == 'modus_ponens'
    assert route_contribution(routes[0], deductive)['classification'] == 'CLOSED-structural'


@pytest.mark.parametrize('name', ['P', 'F'])
@pytest.mark.parametrize('explicit', [False, True])
def test_automatic_and_explicit_bindings_share_collision_policy(tmp_path, name, explicit):
    goal = Proposition('target', 'R', F('predicate', name=name, terms=(Term('constant', 'a'),)),
        (SymbolDefinition(name, 'predicate', 1, 'R'),) if explicit else ())
    issues = []
    def reply(kind, inputs):
        if kind == 'propose_targets': return dict(targets=[goal.to_dict()])
        assert kind == 'classify_target'
        issues.append(inputs['definition_issues'])
        return dict(classification='own_thesis', novelty='new_assertion', fidelity='matches', reason='R')
    calls, _ = frozen_calls(tmp_path, reply)
    assert calls.propose_targets(T, 1) == (() if name == 'P' else (goal,))
    assert issues and all(bool(i) == (name == 'P') for i in issues)
