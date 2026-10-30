"""Native zero-inference stopping and evidence on placeholder inputs."""
import json

import pytest

from ara.bank import Bank
from ara.runtime.orchestration import NativeEngine, search_all
from ara.runtime.search_publication import search_status
from ara.types import CommitmentSet, Formula, Proposition
from test_search_failures import setup, payloads


@pytest.mark.parametrize('concurrency', [1, 4])
def test_zero_inference_pause_preserves_exact_completed_prefix(tmp_path, concurrency):
    calls, provider, log, targets = setup(tmp_path, {}, concurrency)
    calls.config['search_zero_inference_pause_after'] = 2
    with pytest.raises(RuntimeError, match='zero accepted inferences'):
        search_all(calls, NativeEngine(Bank('1', ()), calls), CommitmentSet(()), targets)
    phase = payloads(log, 'search_phase_finished')[-1]
    assert phase['status'] == 'paused'
    assert [p['status'] for p in phase['jobs']] == ['completed'] * 2 + ['cancelled'] * 4
    assert set(provider.attempts) == {'p', 'not:p'}
    assert len(list((tmp_path / 'routes').glob('*.json'))) == 2
    assert search_status(log.read())['status'] == 'paused'
    receipt = payloads(log, 'search_zero_inference_pause')[-1]
    assert receipt['completed_jobs'] == 2 and receipt['accepted_inferences'] == 0
    assert json.loads((tmp_path / receipt['receipt_path']).read_text())['jobs'] == receipt['jobs']
    assert [j['status'] for j in receipt['jobs']] == ['completed'] * 2 + ['cancelled'] * 4
    assert receipt['jobs'][0]['requests'][0]['basis_present'] is None
    assert any(r['outcome'] == 'accepted_empty_proposals' for r in receipt['jobs'][0]['requests'])


def test_default_ten_and_disabled(tmp_path):
    for disabled in (False, True):
        calls, provider, log, _ = setup(tmp_path / str(disabled), {})
        targets = tuple(Proposition(f'p{i}', 'P', Formula('atom', name=f'P{i}')) for i in range(6))
        if disabled:
            calls.config['search_zero_inference_pause_after'] = 0
            search_all(calls, NativeEngine(Bank('1', ()), calls), CommitmentSet(()), targets)
            assert not payloads(log, 'search_zero_inference_pause')
        else:
            with pytest.raises(RuntimeError, match='zero accepted inferences'):
                search_all(calls, NativeEngine(Bank('1', ()), calls), CommitmentSet(()), targets)
            assert payloads(log, 'search_zero_inference_pause')[-1]['completed_jobs'] == 10
        assert len(payloads(log, 'search_job_finished')) == (12 if disabled else 10)


def test_pause_diagnoses_actual_packed_basis_and_cross_paper_symbols(tmp_path):
    from test_search_basis import setup as basis_setup
    calls, requests, commitments, target = basis_setup(tmp_path)
    calls.config.update(search_zero_inference_pause_after=1, search_concurrency=1)
    with pytest.raises(RuntimeError, match='zero accepted inferences'):
        search_all(calls, NativeEngine(Bank('1', ()), calls), commitments, (target,))
    receipt = payloads(calls.log, 'search_zero_inference_pause')[-1]
    row = receipt['jobs'][0]
    assert row['accepted_inferences'] == 0
    for request in row['requests']:
        assert request['basis_present'] is True
        assert request['missing_basis_ids'] == []
        assert set(request['basis_ids']) == set(target.basis_commitment_ids)
        shared = request['cross_paper_shared_symbols']
        assert {s['name'] for s in shared} == {'Q', 'R', 'S'}
        assert all(len(s['paper_ids']) >= 2 for s in shared)
    assert 'prompt' not in row and 'response' not in row


@pytest.mark.parametrize('value', [-1, True, 1.5, '10', None])
def test_invalid_pause_setting_refuses_before_search(tmp_path, value):
    calls, provider, log, targets = setup(tmp_path, {})
    calls.config['search_zero_inference_pause_after'] = value
    with pytest.raises(ValueError, match='search_zero_inference_pause_after'):
        search_all(calls, NativeEngine(Bank('1', ()), calls), CommitmentSet(()), targets)
    assert not provider.order


def test_native_accepted_inference_prevents_pause(tmp_path):
    from ara.bank import load_bank
    from test_search_alignment import rig, cut, T, GOAL, P, Q, PQ, ROOT
    def reply(kind, inputs):
        if kind == 'map_leaf':
            return {'t_id': next((c.id for c in T.commitments if c.formula.to_dict() == inputs['leaf']['formula']), 'open')}
        if kind == 'propose_cuts':
            return {'proposals': [cut()] if inputs['goal']['formula'] == Q.to_dict() else []}
        if kind == 'formalise_slots':
            return {'slots': [dict(slot='conditional', formula=PQ.to_dict()), dict(slot='antecedent', formula=P.to_dict())]}
        pytest.fail(kind)
    calls, _ = rig(tmp_path, reply)
    calls.config['search_zero_inference_pause_after'] = 1
    routes = search_all(calls, NativeEngine(load_bank(ROOT/'bank'), calls), T, (GOAL,))
    assert any(r.status == 'CLOSED' and len(r.nodes) == 3 for r in routes)
    assert not payloads(calls.log, 'search_zero_inference_pause')
    assert payloads(calls.log, 'search_phase_finished')[-1]['status'] == 'complete'


def test_failures_do_not_count_as_completed(tmp_path):
    calls, provider, log, targets = setup(tmp_path, {'p': 2, 'not:p': 100})
    calls.config['search_zero_inference_pause_after'] = 2
    with pytest.raises(RuntimeError, match='zero accepted inferences'):
        search_all(calls, NativeEngine(Bank('1', ()), calls), CommitmentSet(()), (targets[0], targets[1]))
    # Two failed initial jobs do not consume the allowance: the next pair completes.
    receipt = payloads(log, 'search_zero_inference_pause')[-1]
    assert receipt['completed_jobs'] == 2
    assert [j['status'] for j in receipt['jobs']] == ['failed', 'failed', 'completed', 'completed']
    assert not payloads(log, 'search_job_retry')
    assert receipt['jobs'][0]['rejection_reasons']['JOB_FAILED'] == 1


def test_retry_completion_counts_once(tmp_path):
    calls, _, log, targets = setup(tmp_path, {'p': 2})
    calls.config['search_zero_inference_pause_after'] = 2
    with pytest.raises(RuntimeError, match='zero accepted inferences'):
        search_all(calls, NativeEngine(Bank('1', ()), calls), CommitmentSet(()), (targets[0],))
    receipt = payloads(log, 'search_zero_inference_pause')[-1]
    assert receipt['completed_jobs'] == 2
    assert [j['status'] for j in receipt['jobs']] == ['completed', 'completed']
    assert len(payloads(log, 'search_job_retry')) == 1


def test_pause_cli_resume_keeps_sealed_jobs_and_fresh_window(tmp_path, capsys):
    from ara.bank import load_bank
    from ara.runtime.cache import Cache
    from ara.runtime.calls import ModelCalls
    from ara.runtime.cli import main
    from test_calls import ROOT
    calls, provider, log, targets = setup(tmp_path, {})
    calls.config.update(provider='mock', search_zero_inference_pause_after=2)
    bank = load_bank(ROOT/'bank')
    table = CommitmentSet(())
    log.record('run_started', config=calls.config, topic='P', audience='', literature='', bank_version=bank.bank_version)
    (tmp_path/'commitments.json').write_text(table.to_json())
    log.record('commitments_frozen', commitments=table.to_dict(), bank_version=bank.bank_version)
    log.record('candidates', candidates=[t.to_dict() for t in targets])
    with pytest.raises(RuntimeError, match='zero accepted inferences'):
        search_all(calls, NativeEngine(bank, calls), table, targets)
    def factory(config, log, topic):
        return ModelCalls(config, provider, log, Cache(tmp_path/'cache'), ROOT, topic)
    args = ['resume-search', '--run-dir', str(tmp_path)]
    assert main(args, calls_factory=factory) == 2
    assert 'zero accepted inferences' in capsys.readouterr().err
    assert len(payloads(log, 'search_job_finished')) == 4
    assert main(args, calls_factory=factory) == 2
    assert len(payloads(log, 'search_job_finished')) == 6
    assert main(args, calls_factory=factory) == 0
    assert len(payloads(log, 'search_job_finished')) == 6
    assert not payloads(log, 'runtime_error')
    assert payloads(log, 'awaiting_selection')[-1]['search']['status'] == 'complete'


def test_diagnostic_missing_basis_and_sanitized_rejections(tmp_path):
    from ara.runtime.search_diagnostics import job_diagnostic
    from ara.runtime.logging import EventLog
    from ara.runtime.cache import canonical
    from ara.types import RunEvent, EngineDecision
    from test_calls import response
    log = EventLog(tmp_path/'job.jsonl')
    goal = Proposition('p', 'P', Formula('atom', name='P'), basis_commitment_ids=('t1', 't2'))
    log.emit(RunEvent('P', 'propose_cuts', 'MODEL', prompt='P\nINPUT_JSON\n' + canonical(dict(
        commitments={'commitments': [dict(id='t1', formula=goal.formula.to_dict())]},
        commitment_papers={'t1': 'p1'})), response=canonical(response({'proposals': []})),
        payload_json=canonical(dict(status='rejected', reason='secret-marker-123'))))
    log.emit(RunEvent('P', 'engine', 'ENGINE', decision=EngineDecision('discarded', 'UNKNOWN_BANK_ID', 'secret-marker-123')))
    log.emit(RunEvent('P', 'engine', 'ENGINE', decision=EngineDecision('discarded', 'secret-marker-456', '')))
    row = job_diagnostic(log, goal, 0, 'completed')
    request = row['requests'][0]
    assert request['basis_present'] is False and request['missing_basis_ids'] == ['t2']
    assert request['cross_paper_shared_symbols'] == []
    assert request['rejection_reason'] == 'model_output_rejected'
    assert row['rejection_reasons'] == {'UNKNOWN_BANK_ID': 1, 'OTHER_ENGINE_REJECTION': 1}
    assert 'secret-marker' not in canonical(row)
