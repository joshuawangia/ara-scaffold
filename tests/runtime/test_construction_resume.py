"""Verified provisional artifacts resume one construction lifecycle."""
import json

import httpx2 as httpx
import pytest
from anthropic import APIStatusError

from ara.bank import load_bank
from ara.runtime.budget import BudgetStop
from ara.runtime.cache import Cache
from ara.runtime.calls import ModelCalls
from ara.runtime.orchestration import prepare_commitments
from test_construction_shares import windows, payloads
from test_extraction import rig, ROOT


def stopped(rig, monkeypatch, *, record_run=False, error_message='P'):
    from ara.runtime import providers
    calls, provider, literature, sent = windows(rig, monkeypatch)
    if record_run:
        calls.log.record('run_started', config=calls.config, topic=calls.topic, literature=literature,
                         audience='', bank_version=load_bank(ROOT/'bank').bank_version)
    complete = provider.complete
    def fail(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if inputs['batch_index'] == 1 and kind == 'select_t_roots':
            raise APIStatusError('P', response=httpx.Response(200, request=httpx.Request('POST', 'https://example.invalid'),
                headers={'request-id': 'req_P'}), body={'error': {'type': 'invalid_request_error', 'message': error_message}})
        return complete(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'complete', fail)
    # Reproduce the prior policy's terminal stop with the actual model boundary.
    with monkeypatch.context() as old:
        old.setattr(providers, 'terminal_request_refusal', lambda exc: False)
        with pytest.raises(BudgetStop, match='provider accounting unavailable'):
            prepare_commitments(calls, load_bank(ROOT/'bank'), literature, '')
    assert len(payloads(calls, 'build_t_batch_accepted')) == 1
    return calls, provider, literature, sent


def test_resume_restores_verified_batches_skips_terminal_window_and_freezes_once(rig, monkeypatch, tmp_path):
    calls, provider, literature, sent = stopped(rig, monkeypatch)
    previous_cost = calls.budget.used_cost
    config = {**calls.config, 'unknown_usage_policy': 'count-at-reservation'}
    resumed = ModelCalls(config, provider, calls.log, Cache(tmp_path/'fresh-cache'), ROOT, calls.topic)
    resumed.construction_resume = True
    result = prepare_commitments(resumed, load_bank(ROOT/'bank'), literature, '')
    assert {c.id.rsplit(':', 1)[1] for c in result.commitments} == {'p', 'r'}
    assert [(k, i['batch_index']) for k, i in sent] == [
        ('select_t_roots', 0), ('build_t_batch', 0), ('select_t_roots', 2), ('build_t_batch', 2)]
    assert len(payloads(calls, 'build_t_batch_restored')) == 1
    assert len(payloads(calls, 'build_t_plan')) == 1
    assert len(payloads(calls, 'commitments_frozen')) == 1
    assert payloads(calls, 'build_t_batch_skipped')[0]['index'] == 1
    assert resumed.budget.used_cost > previous_cost
    from decimal import Decimal
    assert resumed.budget.used_cost == sum(Decimal(str(e['cost_usd'])) for e in calls.log.read())
    assert payloads(calls, 'construction_resumed')[0]['next_window'] == 2


@pytest.mark.parametrize('damage', ['artifact', 'plan', 'interrupted'])
def test_resume_refuses_unverified_state_before_dispatch(rig, monkeypatch, tmp_path, damage):
    calls, provider, literature, sent = stopped(rig, monkeypatch)
    config = {**calls.config, 'unknown_usage_policy': 'count-at-reservation'}
    if damage == 'artifact':
        artifact = next(calls.log.path.parent.glob('build-t-*-0.json'))
        data = json.loads(artifact.read_text()); data['commitments'][0]['text'] = 'Q'
        artifact.write_text(json.dumps(data))
    elif damage == 'plan':
        config['working_t_token_budget'] += 1
    else:
        calls.log.record('call_start', kind='select_t_roots', cache_key='P')
    before = len(sent)
    with pytest.raises((ValueError, BudgetStop)):
        resumed = ModelCalls(config, provider, calls.log, Cache(tmp_path/'fresh-cache'), ROOT, calls.topic)
        resumed.construction_resume = True
        prepare_commitments(resumed, load_bank(ROOT/'bank'), literature, '')
    assert len(sent) == before
    assert not payloads(calls, 'commitments_frozen')


def test_resume_cli_reuses_stored_run_and_refuses_second_freeze(rig, monkeypatch, tmp_path):
    from ara.runtime.cli import main
    calls, provider, literature, sent = stopped(rig, monkeypatch, record_run=True)
    def factory(config, log, topic):
        result = ModelCalls(config, provider, log, Cache(tmp_path/'cli-cache'), ROOT, topic)
        monkeypatch.setattr(result, 'propose_targets', lambda *args: ())
        return result
    args = ['resume-construction', '--run-dir', str(calls.log.path.parent),
            '--unknown-usage-policy', 'count-at-reservation']
    assert main(args, calls_factory=factory) == 0
    assert len(payloads(calls, 'commitments_frozen')) == 1
    assert [i['batch_index'] for k, i in sent if k == 'build_t_batch'] == [0, 2]
    assert main(args, calls_factory=factory) == 2
    assert len(payloads(calls, 'commitments_frozen')) == 1


def test_resume_cli_prevents_concurrent_dispatch(rig, monkeypatch):
    from ara.runtime.cli import main
    from ara.runtime.construction_resume import construction_resume_lock
    calls, provider, literature, sent = stopped(rig, monkeypatch, record_run=True)
    before = len(sent)
    with construction_resume_lock(calls.log.path.parent):
        assert main(['resume-construction', '--run-dir', str(calls.log.path.parent),
                     '--unknown-usage-policy', 'count-at-reservation'],
                    calls_factory=lambda *args: pytest.fail('concurrent resume reached provider')) == 2
    assert len(sent) == before


def test_resume_plan_only_restores_in_separate_log_without_generation_or_source_edits(rig, monkeypatch, tmp_path):
    from ara.runtime.cli import main
    from ara.runtime import planning
    from ara.runtime.logging import EventLog
    calls, provider, literature, sent = stopped(rig, monkeypatch, record_run=True)
    source_log = calls.log.path.read_bytes()
    before = len(sent)
    monkeypatch.setattr(planning, 'AnthropicProvider', lambda config: provider)
    output = tmp_path/'preview'
    result = main(['resume-construction', '--run-dir', str(calls.log.path.parent),
                   '--unknown-usage-policy', 'count-at-reservation', '--plan-only', '--output-dir', str(output)],
                  calls_factory=lambda *args: pytest.fail('preview entered generating calls factory'))
    assert result == 0
    assert calls.log.path.read_bytes() == source_log
    assert len(sent) == before
    events = EventLog(output/'events.jsonl').read()
    assert not any(e['stage'] in ('call_start', 'commitments_frozen') for e in events)
    report = json.loads((output/'construction-resume-plan.json').read_text())
    assert report['restored_commitments'] == 1
    assert report['restored_windows'] == [0]
    assert report['next_window'] == 2
    assert report['generation_calls'] == 0 and report['new_cost_usd'] == 0
    assert report['all_counts_passed'] is True


def test_resume_does_not_turn_account_failure_into_window_omission(rig, monkeypatch, tmp_path):
    calls, provider, literature, sent = stopped(rig, monkeypatch, error_message='Your credit balance is too low P')
    before = len(sent)
    resumed = ModelCalls({**calls.config, 'unknown_usage_policy': 'count-at-reservation'}, provider,
                         calls.log, Cache(tmp_path/'resume-cache'), ROOT, calls.topic)
    resumed.construction_resume = True
    with pytest.raises(ValueError, match='finalized provider request refusal'):
        prepare_commitments(resumed, load_bank(ROOT/'bank'), literature, '')
    assert len(sent) == before
    assert not payloads(calls, 'build_t_batch_skipped')
