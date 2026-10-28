"""Committed defaults select the subscription without bypassing its gates."""
from pathlib import Path
import pytest
import yaml
from ara.runtime.cli import apply_profile
from ara.runtime.providers import stage_settings

ROOT=Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('profile',[None,'smoke','pilot','extraction','extraction-full'])
def test_committed_defaults_use_codex_for_every_stage(profile):
    config=yaml.safe_load((ROOT/'config.yaml').read_text())
    if profile:apply_profile(config,profile)
    for path in (ROOT/'schemas').glob('*.json'):
        if path.stem=='formula':continue
        settings=stage_settings(config,path.stem)
        assert settings['provider']=='codex_cli'
        assert settings['model']=='gpt-6-luna' and settings['fallbacks']==[]
    assert stage_settings(config,'search_evidence')['provider']=='codex_cli'
    assert config['codex_cli']['schema_preflight_log'] is None
    assert config['codex_cli']['auth_file']=='/home/dev/.config/ara/codex-home/auth.json'
    if profile=='extraction-full':
        assert all(config[key] is None for key in ('token_cap','cost_cap_usd','extraction_cost_cap_usd'))
    assert 'claude-opus-5' in config['pricing']  # Explicit API configuration remains available.
