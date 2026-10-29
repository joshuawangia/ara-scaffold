"""Config-only dispatch contracts for independently selected construction stages."""
from ara.runtime.cache import canonical, digest
from ara.runtime.providers import stage_settings

KINDS = ('select_t_roots', 'build_t_batch')


def dispatch_settings(config, kind, *, correction=False):
    if kind == 'judge_symbol_alignment':
        return dispatch_settings(config, 'build_t_batch', correction=False)
    if kind not in (*KINDS, 'audit_publication'):
        return kind, {}, config
    stages = config.get('stages', {})
    overrides = {}
    keys = ((kind,) if kind == 'audit_publication' else
            ('construction', kind, 'construction_correction') if correction else ('construction', kind))
    for key in keys:
        values = stages.get(key, {})
        if not isinstance(values, dict):
            raise ValueError(f'construction stage {key} must be a mapping')
        overrides.update(values)
    stage = 'construction_correction' if correction else kind
    # Scoped providers must not resolve the original stage over this correction.
    resolved = {**stage_settings(config, kind), **overrides, 'stages': {}}
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
