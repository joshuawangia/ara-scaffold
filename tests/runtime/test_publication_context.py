"""Publication admission follows its pinned editor, not an inherited writer window."""
from copy import deepcopy
import json
from types import SimpleNamespace

import pytest

from test_calls import rig, graph
from test_publication import paper
from test_claude_code import cli


@pytest.mark.parametrize('writer_window', [None, 872000])
def test_publication_window_keeps_auditor_bound_separate(rig, writer_window):
    from ara.runtime.publication import publication_command
    from ara.runtime.construction_stages import dispatch_settings
    calls, _, log = rig
    config = deepcopy(calls.config)
    config.update(provider='codex_cli', model='gpt-6-luna', model_context_token_bound=200000)
    if writer_window:
        config.update(model_context_window=writer_window, model_context_margin_tokens=16384,
                      model_context_token_bound=839232)
    log.record('run_started', config=config, topic='P')
    route = graph()
    log.record('route', graph=route.to_dict())
    draft = log.path.parent/'draft.json'
    draft.write_text(json.dumps(paper()))
    args = SimpleNamespace(command='polish', run_dir=log.path.parent, route=route.id,
        draft=draft, min_words=3000, audit_provider='codex_cli', audit_model=None,
        unknown_usage_policy=None, literature_currency=[])
    class Captured(Exception): pass
    def factory(settings, *unused, **kwargs):
        assert settings['provider'] == 'claude_code'
        assert settings['model'] == 'claude-opus-5-5'
        assert 'model_context_window' not in settings
        assert settings['model_context_token_bound'] == 934464
        policy = settings['publication_context_policy']
        assert policy['window_tokens'] == 1000000
        assert policy['output_allowance_tokens'] == 49152
        assert policy['margin_tokens'] == 16384
        audit = dispatch_settings(settings, 'audit_publication')[2]
        assert audit['model_context_token_bound'] == (806464 if writer_window else 200000)
        assert audit.get('model_context_window') == writer_window
        raise Captured
    with pytest.raises(Captured):
        publication_command(args, log, calls.root, factory)
    assert json.loads(log.read()[0]['payload_json'])['config'] == config


@pytest.mark.parametrize('maximum,margin', [(24576,16384), (8192,32768)])
def test_context_policy_reserves_native_output_and_margin(maximum, margin):
    from ara.runtime.publication import publication_context_policy
    from ara.runtime.claude_code import ClaudeCodeProvider
    policy = publication_context_policy(maximum, margin)
    assert policy['output_allowance_tokens'] == ClaudeCodeProvider.context_output_tokens(None, maximum)
    assert policy['admission_bound_tokens'] == 1000000 - 2*maximum - margin


@pytest.mark.parametrize('maximum,margin', [(True,16384),(0,16384),(24576,True),(24576,0),(500000,1)])
def test_context_policy_refuses_invalid_or_exhausted_reservations(maximum, margin):
    from ara.runtime.publication import publication_context_policy
    from ara.runtime.calls import Rejected
    with pytest.raises(Rejected):
        publication_context_policy(maximum, margin)


def test_counted_repair_fits_new_bound_but_oversize_still_refuses(rig):
    from ara.runtime.publication import publication_context_policy
    from ara.runtime.claude_code import ClaudeCodeProvider
    from ara.types import TokenUsage
    from ara.runtime.budget import BudgetStop
    calls, _, _ = rig
    class Counter:
        model = calls.config['model']
        initial_context_tokens = ClaudeCodeProvider.initial_context_tokens
        context_output_tokens = ClaudeCodeProvider.context_output_tokens
        def estimate(self, *args):
            return TokenUsage(input_tokens=354182, output_tokens=49152)
        def complete(self, *args):
            raise AssertionError('counting must not dispatch')
    calls.provider = Counter()
    calls.config['model_context_token_bound'] = 200000
    before = calls.count_request('polish_essay', {'markdown':'P'}, maximum=24576)
    assert before.initial_input_tokens == 164803
    assert before.context_output_tokens == 49152
    assert before.initial_input_tokens + before.context_output_tokens > 200000
    calls.config['model_context_token_bound'] = publication_context_policy(24576)['admission_bound_tokens']
    after = calls.count_request('polish_essay', {'markdown':'P'}, maximum=24576, admission=True)
    assert after.initial_input_tokens + after.context_output_tokens <= calls.config['model_context_token_bound']
    assert after.initial_input_tokens == before.initial_input_tokens
    assert after.context_output_tokens == before.context_output_tokens
    calls.config['model_context_token_bound'] = 213954
    with pytest.raises(BudgetStop, match='context bound exceeded'):
        calls.count_request('polish_essay', {'markdown':'P'}, maximum=24576, admission=True)


def test_host_context_overrides_do_not_reach_isolated_editor(cli, monkeypatch, tmp_path):
    from ara.runtime.claude_code import ClaudeCodeProvider
    _, _, config, _ = cli
    monkeypatch.setenv('CLAUDE_CODE_DISABLE_1M_CONTEXT', '1')
    monkeypatch.setenv('CLAUDE_CODE_MAX_CONTEXT_TOKENS', '200000')
    provider = ClaudeCodeProvider(config)
    directory = tmp_path/'environment-probe'/'config'
    directory.mkdir(parents=True)
    environment, _ = provider._environment(directory, 24576)
    assert 'CLAUDE_CODE_DISABLE_1M_CONTEXT' not in environment
    assert 'CLAUDE_CODE_MAX_CONTEXT_TOKENS' not in environment
    assert environment['CLAUDE_CODE_MAX_OUTPUT_TOKENS'] == '24576'
