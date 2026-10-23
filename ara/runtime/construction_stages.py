"""Config-only dispatch contracts for independently selected construction stages."""
from ara.runtime.cache import canonical, digest

KINDS = ('select_t_roots', 'build_t_batch')


def dispatch_settings(config, kind, *, correction=False):
    if kind not in KINDS:
        return kind, {}, config
    stages = config.get('stages', {})
    overrides = {}
    keys = (kind, 'construction_correction') if correction else (kind,)
    for key in keys:
        values = stages.get(key, {})
        if not isinstance(values, dict):
            raise ValueError(f'construction stage {key} must be a mapping')
        overrides.update(values)
    stage = 'construction_correction' if correction else kind
    return stage, overrides, {**config, **overrides}


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
