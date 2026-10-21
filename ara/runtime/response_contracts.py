"""Versioned local response contracts shared by live calls and receipt verification."""
import json
from pathlib import Path
from ara.runtime.cache import canonical, digest

RESPONSE_CONTRACT_VERSION = 2


def response_schema(root: Path, kind: str, inputs: dict) -> dict | None:
    if kind == 'search_evidence':
        return None
    schema = json.loads((root / 'schemas' / f'{kind}.json').read_text())
    if kind == 'extract_paper':
        mode = inputs.get('original_mode') if inputs.get('mode') == 'targeted_correction' else inputs.get('mode')
        reconciliation = mode == 'reconcile_ranges'
        if not reconciliation or not inputs.get('obligations'):
            for field in ('context_request', 'pending_obligation_ids', 'resolutions'):
                del schema['properties'][field]
        if reconciliation:
            del schema['properties']['empty_reason']
    return schema


def response_template(root: Path, kind: str, inputs: dict) -> str:
    template = (root / 'prompts' / f'{kind}.txt').read_text()
    if kind != 'search_evidence':
        template += '\nLOCAL_RESPONSE_SCHEMA (all constraints are mandatory)\n' + canonical(response_schema(root, kind, inputs))
    return template


def compatible_prompt(root: Path, kind: str, prompt: str, version=None) -> bool:
    try:
        template, raw = prompt.rsplit('\nINPUT_JSON\n', 1)
        inputs = json.loads(raw)
        if version in (None, RESPONSE_CONTRACT_VERSION) and template == response_template(root, kind, inputs):
            return True
        # The pre-mode-specific extraction contract is retained for original
        # accepted and rejected attempts, never used to dispatch a new call.
        historical = json.loads(Path(__file__).with_name('legacy_response_contracts.json').read_text())
        return version in (None, 1) and digest(template) in historical.get(kind, [])
    except (ValueError, KeyError, FileNotFoundError):
        return False
