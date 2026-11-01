"""Repair ledger controls use placeholder content only."""
import json
import pytest
from ara.runtime.calls import Rejected
from ara.runtime.publication_resume import repair_state


def row(stage, data, *, prompt=None, label='SYSTEM'):
    return dict(stage=stage, payload_json=json.dumps(data), prompt=prompt, label=label)


def start(**extra):
    return row('publication_started', dict(route_id='r', original_sha256='a', **extra))


def request(number):
    return row('polish_essay', dict(status='accepted'), label='MODEL',
               prompt='P\nINPUT_JSON\n'+json.dumps(dict(mode='repair',repair_round=number)))


def accepted(number):
    return row('publication_repair', dict(round=number, markdown='# P\n\nP',
               figure_placements=[], change_log=[]))


def test_state_preserves_accepted_candidate_and_structural_attempts():
    events=[start(),request(1),request(1),accepted(1),start(resumed_repair_rounds=1)]
    state=repair_state(events,'r','a')
    assert state['repair_rounds']==state['accepted_repair_rounds']==1
    assert state['candidate']['markdown']=='# P\n\nP'
    assert repair_state(events,'r','b')['candidate'] is None
    assert repair_state(events,'other','a')['repair_rounds']==0


@pytest.mark.parametrize('tail,reason', [
    ([start(),request(1)], 'restarts a consumed round'),
    ([request(2)], 'unfinished or structurally refused'),
    ([start(resumed_repair_rounds=0)], 'counter does not match'),
    ([request(3)], 'restarts a consumed round'),
])
def test_state_refuses_reset_skip_or_unfinished_round(tail,reason):
    with pytest.raises(Rejected,match=reason):
        repair_state([start(),request(1),accepted(1),*tail],'r','a')


def test_structural_retry_cannot_be_replenished():
    with pytest.raises(Rejected,match='structural retry budget exhausted'):
        repair_state([start(),request(1),request(1),request(1)],'r','a')


@pytest.mark.parametrize('number',[0,4,True,'1'])
def test_round_number_is_strict(number):
    with pytest.raises(Rejected,match='invalid round'):
        repair_state([start(),request(number)],'r','a')


def test_unlogged_acceptance_cannot_supply_resume_candidate():
    with pytest.raises(Rejected,match='lacks its bounded model request'):
        repair_state([start(),accepted(1)],'r','a')


def test_third_round_refusal_cannot_be_restarted():
    events=[start()]
    for n in (1,2,3):events.extend([request(n),accepted(n)])
    with pytest.raises(Rejected,match='repair budget exhausted'):
        repair_state(events,'r','a')
