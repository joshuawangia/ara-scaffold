"""Phi2's native closures remain reportable with distinct polarity namespaces."""
import hashlib
import json

import pytest

from ara.bank import load_bank
from ara.runtime.cache import canonical
from ara.runtime.cli import main
from ara.runtime.frozen_catalogue import frozen_artifact
from ara.runtime.orchestration import NativeEngine
from ara.runtime.route_policy import route_contribution, selectable_routes
from ara.types import Commitment, CommitmentSet, Formula, Proposition
from test_search_alignment import P, Q, R, T, ROOT, rig


@pytest.mark.parametrize('case', ['antecedent_in_t', 'two_support_padding', 'positive'])
def test_native_report_preserves_route_polarity_and_nested_contribution(tmp_path, monkeypatch, case):
    taut = Formula('implies', (Q, Q))
    if case == 'antecedent_in_t':
        t = CommitmentSet((Commitment('t1', 'Q -> Q', 'placeholder:1', taut),
            Commitment('t2', '(Q -> Q) -> P', 'placeholder:2', Formula('implies', (taut, P)))))
        goal, bank_id, bindings = Proposition('p', 'P', P), 'modus_ponens', [('conditional', 1), ('antecedent', 0)]
    elif case == 'two_support_padding':
        t = CommitmentSet((T.commitments[0], Commitment('t2', 'Q -> Q', 'placeholder:2', taut)))
        goal = Proposition('p', 'P and (Q -> Q)', Formula('and', (P, taut)))
        bank_id, bindings = 'conjunction_introduction', [('left', 0), ('right', 1)]
    else:
        t, goal = T, Proposition('r', 'R', R)
        bank_id, bindings = 'sign', [('sign_relation', 1), ('observed_sign', 0)]

    def reply(kind, inputs):
        if kind == 'map_leaf':
            return {'t_id': 'open'}
        if kind == 'propose_cuts':
            return {'proposals': [dict(bank_id=bank_id, conclusion_text=goal.text,
                conclusion_ref='current_goal', premises=[dict(slot=slot, text=t.commitments[i].text,
                t_id=t.commitments[i].id, scope_id=None) for slot, i in bindings])]}
        if kind == 'formalise_slots':
            return {'slots': [dict(slot=b['slot'], formula=b['formula']) for b in inputs['slot_bindings']]}
        if kind=='answer_cq': return dict(cq_id=inputs['question']['id'],answer='P',answered=True,supporting_t_ids=['t1','t2'])
        raise AssertionError(kind)

    directory, output = tmp_path/'source', tmp_path/'report'
    calls, _ = rig(directory, reply)
    from test_cross_paper import frozen_metadata
    artifact,provenance=frozen_metadata(t,('a','b'))
    (directory/'frozen-t.json').write_text(canonical(artifact))
    (directory/'commitment-provenance.json').write_text(canonical(provenance))
    calls.log.record('run_started', config=calls.config, topic='P')
    calls.log.record('symbol_catalogue_frozen', **artifact['symbol_catalogue'])
    calls.log.record('commitment_provenance_frozen', **provenance)
    calls.log.record('commitments_frozen', commitments=t.to_dict())
    routes = NativeEngine(load_bank(ROOT/'bank'), calls)._engine(t).search(goal).routes
    graph = routes[0]
    assert graph.status == 'CLOSED'
    assert any(e['decision'] and e['decision']['reason_code'] == 'BANK_LICENSED' for e in calls.log.read())
    receipt = route_contribution(graph, t, provenance)
    expected = 'CLOSED-derived' if case == 'positive' else 'CLOSED-single-paper'
    assert receipt['classification'] == expected and receipt['support_ids'] == ['t1', 't2']
    assert bool(selectable_routes(routes, t, provenance)) == (case == 'positive')
    if case != 'positive':
        assert receipt['polarity'] == 'target' and receipt['reason'] == 'single_paper_closure'
        assert receipt['status'] == 'trivial' and receipt['commitment_id'] in ('t1', 't2')
    calls.log.record('route', target=goal.id, polarity='negation', graph=graph.to_dict())

    def snapshot():
        return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in directory.rglob('*') if p.is_file()}
    before = snapshot()
    def forbidden(*args, **kwargs):
        raise AssertionError('report must not call a provider or engine')
    monkeypatch.setattr('ara.runtime.report_render.shutil.which', lambda _: None)
    assert main(['report', '--run-dir', str(directory), '--out', str(output)],
                calls_factory=forbidden, engine_factory=forbidden) == 0
    assert snapshot() == before
    assert expected in (output/'report.html').read_text()
    summary = json.loads((output/'data.json').read_text())['runs'][0]['routes'][0]
    assert summary['polarity'] == 'negation' and summary['target'] == goal.id
    assert summary['classification'] == expected
    assert summary['selectable_by_default'] == (case == 'positive')
    route = json.loads((output/summary['file']).read_text())
    assert route['polarity'] == 'negation' and route['target'] == goal.id
    assert route['classification'] == expected and route['graph'] == graph.to_dict()
    assert route['contribution'] == receipt
