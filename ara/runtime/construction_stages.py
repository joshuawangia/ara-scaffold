"""Config-only dispatch contracts for independently selected construction stages."""
from ara.runtime.cache import canonical, digest
from ara.runtime.providers import stage_settings

KINDS = ('select_t_roots', 'build_t_batch')


def dispatch_settings(config, kind, *, correction=False):
    if kind == 'judge_symbol_alignment':
        return dispatch_settings(config, 'build_t_batch', correction=False)
    if kind not in KINDS:
        return kind, {}, config
    stages = config.get('stages', {})
    overrides = {}
    inherited_window = config.get('model_context_window')
    keys = ('construction', kind, 'construction_correction') if correction else ('construction', kind)
    for key in keys:
        values = stages.get(key, {})
        if not isinstance(values, dict):
            raise ValueError(f'construction stage {key} must be a mapping')
        if values.get('model_context_window') is not None:
            inherited_window = values['model_context_window']
        overrides.update(values)
    stage = 'construction_correction' if correction else kind
    # Scoped providers must not resolve the original stage over this correction.
    resolved = {**stage_settings(config, kind), **overrides, 'stages': {}}
    # Normalize before provider-cache identity, including a repeated/cached lookup.
    # Provider construction must not be what determines the admission bound.
    from ara.runtime.codex_window import apply_context_window
    apply_context_window(resolved, inherited_window=inherited_window)
    return stage, overrides, resolved


def construction_stage_manifest(config):
    result = {}
    for kind in KINDS:
        for correction in (False, True):
            _, overrides, settings = dispatch_settings(config, kind, correction=correction)
            result[kind + ('_correction' if correction else '')] = {
                'provider': settings['provider'], 'model': settings['model'],
                'effort': settings['effort'], 'thinking': settings.get('thinking', 'adaptive'),
                'fallbacks': settings.get('fallbacks', ['claude-opus-4-8']),
                'overrides_hash': digest(canonical(overrides))}
    return result
