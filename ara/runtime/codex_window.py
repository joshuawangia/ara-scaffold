"""Operator context decisions for the pinned isolated subscription transport."""
from ara.runtime.providers import stage_settings

# Embedded model catalogue in codex-cli 0.163.0, binary SHA256
# 399ff69c431c066e40de318fba45c2b07f45a76b19939d247ee4828fc70c4215.
# This is a client limit, not a serving-model identity or tokenizer guarantee.
PINNED_WINDOWS = {'gpt-6-luna': dict(context_window=272000, max_context_window=872000)}
CLI_VERSION = 'codex-cli 0.163.0'


def context_window_decision(config, model=None):
    window = config.get('model_context_window')
    if window is None:
        return None
    if config.get('provider') != 'codex_cli':
        raise ValueError('model_context_window requires codex_cli')
    model = model or config['model']
    if model not in PINNED_WINDOWS:
        raise ValueError('context window has no pinned maximum for model: ' + str(model))
    pinned = PINNED_WINDOWS[model]
    if type(window) is not int or not 0 < window <= pinned['max_context_window']:
        raise ValueError('model_context_window must be a positive integer within pinned max_context_window')
    margin = config.get('model_context_margin_tokens', 16384)
    maximum = config.get('propose_targets_max_output_tokens', config['max_output_tokens'])
    if type(margin) is not int or margin <= 0 or type(maximum) is not int or maximum <= 0:
        raise ValueError('context margin and target output allowance must be positive integers')
    # Same doubled output reservation as CodexCLIProvider.context_output_tokens.
    output = 2 * maximum
    bound = window - output - margin
    if bound <= output:
        raise ValueError('context window leaves no usable request allowance')
    return dict(origin='operator_run_config', model=model, cli_version=CLI_VERSION,
        model_context_window=window, pinned_default_context_window=pinned['context_window'],
        pinned_max_context_window=pinned['max_context_window'], output_allowance=output,
        margin_tokens=margin, model_context_token_bound=bound,
        rule='window minus target output allowance minus margin; native admission also includes request output',
        evidence='pinned CLI embedded model catalogue; configured client window, serving capacity unverified')


def apply_context_window(config):
    decision = context_window_decision(config)
    if decision is not None:
        # Stage changes must not silently opt into an unknown larger window.
        for kind in config.get('stages', {}):
            settings = stage_settings(config, kind)
            if kind != 'extraction' and settings['provider'] == 'codex_cli':
                context_window_decision(settings, settings['model'])
        config['model_context_token_bound'] = decision['model_context_token_bound']
    return decision
