"""Advisory attribution and bounded native scheme correction, using placeholders."""
import json
from dataclasses import replace
import pytest
from ara.runtime.orchestration import NativeEngine, search_all
from ara.runtime.route_policy import route_contribution, selectable_routes
from ara.runtime.providers import Response
from test_novelty_policy import setup, T, R
from test_search_alignment import raw


@pytest.mark.parametrize('text', ['Claims about P support R', 'The account of P supports R'])
def test_own_voice_lexical_hits_are_advisory_through_selection(tmp_path, text):
    calls, bank, goal, _, provenance = setup(tmp_path)
    goal = replace(goal, text=text)
    original = calls.provider.complete
    inputs_seen = []
    def complete(kind, prompt, *args):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'propose_targets': return Response(raw(dict(targets=[goal.to_dict()])))
        if kind == 'classify_target':
            inputs_seen.append(inputs)
            return Response(raw(dict(classification='own_thesis', novelty='new_assertion', fidelity='matches', reason='R')))
        return original(kind, prompt, *args)
    calls.provider.complete = complete
    assert calls.propose_targets(T, 1) == (goal,)
    assert inputs_seen[0]['lexical_attribution_hits']
    hits = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'target_lexical_attribution']
    assert hits[0]['hits'] == inputs_seen[0]['lexical_attribution_hits']
    routes = search_all(calls, NativeEngine(bank, calls), T, (goal,))
    assert selectable_routes(routes, T, provenance)


@pytest.mark.parametrize('defect', ['unknown_bank', 'bad_reference', 'empty'])
def test_native_new_atom_guidance_and_one_concrete_correction(tmp_path, defect):
    calls, bank, goal, _, provenance = setup(tmp_path)
    calls.config.update(validation_attempts=3, forward_pass_depth=0)
    original = calls.provider.complete
    attempts, guidance = [], []
    def complete(kind, prompt, *args):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind in ('map_leaf', 'propose_cuts') and (inputs.get('goal') or inputs['leaf'])['formula'] == R.to_dict():
            guidance.append(inputs)
        if kind == 'propose_cuts':
            attempts.append(inputs)
            if len(attempts) == 1:
                value = json.loads(original(kind, prompt, *args).text())
                if defect == 'empty': value['proposals'] = []
                elif defect == 'unknown_bank': value['proposals'][0]['bank_id'] = 'absent'
                else: value['proposals'][0]['premises'][0]['t_id'] = 'absent'
                return Response(raw(value))
        return original(kind, prompt, *args)
    calls.provider.complete = complete
    routes = NativeEngine(bank, calls)._engine(T).search(goal).routes
    assert routes[0].status == 'CLOSED'
    assert route_contribution(routes[0], T, provenance)['classification'] == 'CLOSED-derived'
    assert len(attempts) == 2
    assert attempts[0]['proposal_limit'] == 3 and attempts[0]['attempt_budget'] == 2
    reason = {'unknown_bank': 'UNKNOWN_BANK_ID', 'bad_reference': 'unknown proposal T id: absent', 'empty': 'NO_PROPOSALS'}[defect]
    assert reason in json.dumps(attempts[1]['rejection_feedback'])
    for inputs in guidance:
        assert inputs['goal_novelty']['essential_new_propositions'] == [R.to_dict()]
        sign = next(s for s in inputs['scheme_signatures'] if s['bank_id'] == 'sign')
        assert [s['id'] for s in sign['premise_slots']] == ['sign_relation', 'observed_sign']
        assert sign['critical_questions'] and inputs['symbol_catalogue']


@pytest.mark.parametrize('invalid', [False, True])
def test_empty_batches_exhaust_one_correction(tmp_path, invalid):
    calls, bank, goal, _, _ = setup(tmp_path)
    calls.config['validation_attempts'] = 3
    original = calls.provider.complete
    attempts = []
    def complete(kind, prompt, *args):
        if kind == 'propose_cuts':
            attempts.append(json.loads(prompt.split('\nINPUT_JSON\n')[1]))
            if invalid:
                value=json.loads(original(kind,prompt,*args).text())
                value['proposals'][0]['premises'][0]['t_id']='absent'
                return Response(raw(value))
            return Response(raw(dict(proposals=[])))
        return original(kind, prompt, *args)
    calls.provider.complete = complete
    assert NativeEngine(bank, calls)._engine(T).search(goal).routes[0].status == 'OPEN'
    assert len(attempts) == 2
    assert ('unknown proposal T id: absent' if invalid else 'NO_PROPOSALS') in attempts[1]['rejection_feedback'][0]['reason']
