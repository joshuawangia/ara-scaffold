"""Source graph structure through the production construction boundary."""
import json

import pytest

from ara.bank import load_bank
from ara.formal import entails
from ara.runtime.calls import Rejected
from ara.runtime.export import methodology
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.providers import Response
from rich_fixture import batch_response
from test_extraction import rig, response, ROOT
from test_extraction_rich import rich_calls


def relational(inputs, flat=False):
    if 'closure' not in inputs:
        return batch_response(inputs)
    items = {i['id']: i for p in inputs['papers'] for i in p['items']}
    names = dict(p='P', q='Q', r='R', f='F', d='D', qual='S')
    base = {id: {'op': 'predicate', 'name': names[id.rsplit(':', 1)[1]],
                 'terms': [{'kind': 'constant', 'name': 'a'}]}
            for id, item in items.items() if item['kind'] != 'inference'}
    formulas = dict(base)
    for id, item in items.items():
        if flat:
            formulas[id] = {'op': 'atom', 'name': 'P' + str(list(items).index(id))}
        elif item['kind'] == 'inference':
            premises = [base[p] for p in item['premise_ids']]
            formulas[id] = {'op': 'implies', 'args': [premises[0] if len(premises) == 1 else
                {'op': 'and', 'args': premises}, base[item['conclusion_id']]]}
    from ara.runtime.construction import formula_symbols
    from ara.types import Formula
    symbols = {}
    for id, f in formulas.items():
        for name, kind, arity in set(formula_symbols(Formula.from_dict(f))):
            symbol = symbols.setdefault(name, dict(name=name, kind=kind, arity=arity, definition=name, evidence_ids=[]))
            symbol['evidence_ids'].append(id)
    return dict(commitments=[dict(id=id, definition=items[id]['text'], formula=f) for id, f in formulas.items()],
                new_symbols=list(symbols.values()), alignments=[])


def install(rig, monkeypatch, mode='structured'):
    calls, provider, path = rich_calls(rig, monkeypatch)
    sent = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        sent.append((kind, inputs))
        value = relational(inputs, flat=(mode == 'flat' or mode == 'repair' and inputs.get('mode') != 'structure_correction'))
        if kind == 'build_t_batch' and mode == 'disconnected':
            inference = next(c for c in value['commitments'] if c['formula']['op'] == 'implies')
            inference['formula']['args'][1] = {'op': 'predicate', 'name': 'Q', 'terms': [{'kind': 'constant', 'name': 'a'}]}
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    return calls, path, sent


def payloads(calls, stage):
    return [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == stage]


def test_relational_inferences_derive_target_without_assuming_conclusion(rig, monkeypatch):
    calls, path, sent = install(rig, monkeypatch)
    frozen = prepare_commitments(calls, load_bank(ROOT / 'bank'), path.read_text(), 'P')
    by_id = {c.id.rsplit(':', 1)[1]: c for c in frozen.commitments}
    premises = tuple(by_id[id].formula for id in ('p', 'q', 'i', 'j'))
    assert entails(premises, by_id['f'].formula, 2000) == 'SOLVER_UNSAT'
    assert entails(premises[:2], by_id['f'].formula, 2000) == 'SOLVER_COUNTEREXAMPLE'
    provenance = json.loads((calls.log.path.parent / 'commitment-provenance.json').read_text())['commitments']
    assert all(provenance[by_id[id].id]['source_kind'] == 'inference' and by_id[id].citation for id in ('i', 'j'))
    outcome = payloads(calls, 'build_t_structure_outcome')[0]
    assert outcome['passed'] and outcome['non_atomic_fraction'] == 2 / 8
    assert outcome['inference_fraction'] == 2 / 8
    assert outcome['connected_conditionals'] == 2 and outcome['symbol_reuse_rate'] > 0
    # Unsupported qualification attachment is not fabricated by code.
    assert by_id['qual'].formula.op == 'predicate'
    assert not payloads(calls, 'construction_structure_correction')


@pytest.mark.parametrize('mode', ['flat', 'repair'])
def test_flat_batch_fails_gate_and_gets_exactly_one_correction(rig, monkeypatch, mode):
    calls, path, sent = install(rig, monkeypatch, mode)
    frozen = prepare_commitments(calls, load_bank(ROOT / 'bank'), path.read_text(), 'P')
    gates = payloads(calls, 'build_t_structure_gate')
    assert len(gates) == 2 and not gates[0]['passed'] and gates[0]['flat']
    assert gates[0]['non_atomic_fraction'] == 0 and gates[0]['symbol_reuse_rate'] == 0
    correction = [i for k, i in sent if i.get('mode') == 'structure_correction']
    assert len(correction) == 1 and correction[0]['structure_feedback']['issues']
    assert len([k for k, _ in sent if k == 'build_t_batch']) == 2
    outcome = payloads(calls, 'build_t_structure_outcome')[0]
    assert outcome['disclosure'] == ('flat_after_one_correction' if mode == 'flat' else None)
    assert outcome['passed'] == (mode == 'repair')
    assert len(frozen.commitments) == 8
    report = json.loads(methodology(calls.log.path).split('```json\n')[1].split('\n```')[0])
    assert report['construction']['structure_outcomes'] == [outcome]
    assert len(payloads(calls, 'commitments_frozen')) == 1


def test_nonflat_disconnected_inference_not_silently_accepted(rig, monkeypatch):
    calls, path, sent = install(rig, monkeypatch, 'disconnected')
    with pytest.raises(Rejected, match='structure contract failed'):
        prepare_commitments(calls, load_bank(ROOT / 'bank'), path.read_text(), 'P')
    assert not payloads(calls, 'commitments_frozen')
    gates = payloads(calls, 'build_t_structure_gate')
    assert len(gates) == 2 and all(not g['passed'] for g in gates)
    assert any(i['reason'] == 'conditional_must_reuse_selected_endpoint_formula' for i in gates[-1]['issues'])
