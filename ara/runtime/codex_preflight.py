"""Live placeholder schema proof required before Codex pilot entrypoints."""
import json
from pathlib import Path

from ara.runtime.cache import canonical, digest
from ara.runtime.codex_schema import VERSION, strict_schema
from ara.runtime.codex_cli import CLI_VERSION
from ara.runtime.construction_stages import KINDS, dispatch_settings
from ara.runtime.logging import EventLog
from ara.runtime.providers import stage_settings


def manifest(config, root):
    cases = []
    for path in sorted((root / 'schemas').glob('*.json')):
        if path.stem in ('formula', 'extract_paper', 'polish_essay', 'audit_publication'):
            continue  # Utility schema and API-only extraction; web retrieval has no JSON schema.
        kind = path.stem
        if kind == 'consolidate_vocabulary' and not config.get('construction_consolidate_vocabulary'):
            continue
        for correction in ((False, True) if kind in (*KINDS, 'consolidate_vocabulary') else (False,)):
            _, overrides, scoped = dispatch_settings(config, kind, correction=correction)
            actual = scoped if overrides else config
            settings = stage_settings(actual, kind)
            if actual['provider'] != 'codex_cli':
                continue
            schema = json.loads(path.read_text())
            cases.append(dict(case=kind + ('_correction' if correction else ''), kind=kind,
                inputs={'mode':'targeted_correction'} if correction else {},
                native_schema_hash=digest(canonical(schema)), wire_schema_hash=digest(canonical(strict_schema(schema))),
                model=settings['model'], effort=settings['effort'],
                system_prompt_hash=digest(settings.get('system_prompt', ''))))
    return dict(version=VERSION, cli_version=CLI_VERSION, cases=cases)


def codex_schema_preflight(calls):
    proof = manifest(calls.config, calls.root)
    if not proof['cases']:
        raise ValueError('Codex schema preflight requires Codex stage routing')
    calls.log.record('codex_schema_preflight_started', manifest=proof)
    passed = 0
    for case in proof['cases']:
        calls.log.record('codex_schema_preflight_case', case=case['case'])
        try:
            calls._call_once(case['kind'], case['inputs'], schema_smoke=True)
        except Exception as exc:
            # Native calls already retain the sanitized category and accounting.
            # Never copy arbitrary exception/provider text into the gate receipt.
            calls.log.record('codex_schema_preflight_failed', case=case['case'], error_type=type(exc).__name__)
        else:
            passed += 1
            calls.log.record('codex_schema_preflight_accepted', case=case['case'])
    result = dict(passed=passed == len(proof['cases']), accepted=passed, total=len(proof['cases']), manifest=proof)
    calls.log.record('codex_schema_preflight_finished', **result)
    return result


def require_codex_preflight(config, root):
    expected = manifest(config, root)
    if not expected['cases']:
        return
    source = config.get('codex_cli', {}).get('schema_preflight_log')
    if not source or not Path(source).is_file():
        raise ValueError('Codex pilot requires a successful codex-schema-preflight; set codex_cli.schema_preflight_log')
    events = EventLog(Path(source)).read()  # Verify chain AND append-only tail checkpoint.
    starts = [json.loads(e['payload_json']) for e in events if e['stage']=='codex_schema_preflight_started']
    finishes = [json.loads(e['payload_json']) for e in events if e['stage']=='codex_schema_preflight_finished']
    if (starts != [{'manifest':expected}] or len(finishes)!=1 or not finishes[0].get('passed')
            or finishes[0].get('manifest') != expected or finishes[0].get('accepted') != len(expected['cases'])):
        raise ValueError('Codex schema preflight is missing, incomplete or stale')
    pending = None
    receipts = []
    accepted = []
    cases = {c['case']:c for c in expected['cases']}
    for event in events:
        payload = json.loads(event['payload_json'])
        if event['stage']=='codex_schema_preflight_case':
            pending = payload['case']
            receipts = []
        elif event['label']=='MODEL' and event['stage']!='isolation_canary':
            receipts.append((event, payload))
        elif event['stage']=='codex_schema_preflight_accepted':
            if pending not in cases or payload['case']!=pending or len(receipts)!=1:
                raise ValueError('Codex schema preflight lacks a unique live receipt')
            case = cases[pending]
            event, receipt = receipts[0]
            cli = receipt.get('cli', {})
            if (event['stage'] != case['kind'] or receipt.get('status')!='accepted'
                    or receipt.get('cache_hit') is not False or receipt.get('accounting')!='actual'
                    or receipt.get('provider')!='codex_cli' or receipt.get('requested_model')!=case['model']
                    or receipt.get('effort')!=case['effort'] or cli.get('version')!=CLI_VERSION
                    or cli.get('schema_transform')!=VERSION
                    or cli.get('native_schema_hash')!=case['native_schema_hash']
                    or cli.get('wire_schema_hash')!=case['wire_schema_hash']):
                raise ValueError('Codex schema preflight live receipt mismatch')
            accepted.append(pending)
            pending = None
    if sorted(accepted) != sorted(cases):
        raise ValueError('Codex schema preflight does not cover every stage and correction')
