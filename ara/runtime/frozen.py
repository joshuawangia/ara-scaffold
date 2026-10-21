"""Read-only verification and inherited receipts for a shared frozen T."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from ara.runtime.cache import canonical, digest
from ara.runtime.extraction import HEADER, assemble, missing_lineage, save_immutable
from ara.runtime.logging import EventLog, read_log
from ara.types import CommitmentSet
from ara.runtime.provenance import verify_imports, extraction_outcomes
from ara.runtime.response_contracts import compatible_prompt
from ara.runtime.providers import stage_settings


# Search/writer settings and local caps may differ. Construction semantics may not.
CONSTRUCTION_STAGES = ('build_t', 'build_t_batch', 'select_t_roots', 'extract_paper')
STAGE_DEFAULTS = {'provider': 'anthropic', 'thinking': 'adaptive',
                  'fallbacks': ['claude-opus-4-8'], 'formula_output_depth': 2,
                  'validation_attempts': 1, 'max_output_tokens': 8192}


def construction_config(config: dict) -> dict:
    stages = {kind: {key: settings.get(key, default) for key, default in
                    {**STAGE_DEFAULTS, 'model': None, 'effort': None}.items()}
              for kind in CONSTRUCTION_STAGES for settings in [stage_settings(config, kind)]}
    return {'stages': stages, **{key: value for key, value in config.items()
            if key.startswith(('build_t_', 'working_t_', 'construction_', 'extracted_build_t_',
                               'select_t_roots_', 'extract_paper_'))}}


def contract(root: Path) -> dict:
    """Pin interpretation of stored T, independent of model/search settings."""
    paths = [root / 'ara/types.py', *sorted((root / 'bank').glob('*.yaml')),
             *[root / 'schemas' / f'{kind}.json' for kind in
               ('build_t', 'build_t_batch', 'select_t_roots', 'extract_paper')]]
    return {'version': 1, 'files': {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest() for p in paths}}


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError('frozen T: ' + reason)


def verify_receipts(events: list[dict], root: Path) -> None:
    """Verify imported extraction blocks and all construction/extraction call origins."""
    try:
        verify_imports(events)
    except (ValueError, OSError) as exc:
        raise ValueError('frozen T: broken extraction provenance receipt: ' + str(exc)) from exc
    origins = set()
    for event in events:
        payload = json.loads(event['payload_json'])
        if event['label'] != 'MODEL':
            continue
        require(payload.get('accounting') != 'reservation_unknown_actual', 'unknown construction/extraction spend')
        kind = event['stage']
        require(compatible_prompt(root, kind, event['prompt'], payload.get('response_contract_version')),
                'schema/prompt version drift: ' + kind)
        if payload['status'] == 'accepted':
            key = payload['cache_key']
            require(not payload['cache_hit'] or key in origins, 'missing construction/extraction cache origin')
            if not payload['cache_hit']:
                origins.add(key)
    require(not missing_lineage(events), 'broken extraction lineage')
    starts = sum(e['stage'] == 'call_start' for e in events)
    finishes = sum(e['label'] == 'MODEL' and not json.loads(e['payload_json']).get('cache_hit') for e in events)
    require(starts == finishes, 'incomplete construction/extraction dispatch receipts')


def verify_batch_responses(events, batches, artifacts, literature):
    """Bind saved formulas to accepted calls, including their original correction candidate."""
    from ara.runtime.construction import decode_batch_formulas, merge_correction, normalize_commitments
    from ara.runtime.providers import Response
    items = {i['id']: i for p in json.loads(literature[len(HEADER):])['papers'] for i in p['items']}
    accepted = {}
    previous = {}
    for event in events:
        if event['label'] != 'MODEL' or event['stage'] != 'build_t_batch':
            continue
        payload = json.loads(event['payload_json'])
        inputs = json.loads(event['prompt'].rsplit('\nINPUT_JSON\n', 1)[1])
        identity = (inputs['plan_id'], inputs['batch_index'])
        if payload['status'] != 'accepted':
            previous[identity] = event
            continue
        data = decode_batch_formulas(json.loads(Response(json.loads(event['response'])).text()))
        if inputs.get('mode') == 'targeted_correction':
            rejected = previous.get(identity)
            require(rejected is not None, 'missing construction correction origin')
            candidate = decode_batch_formulas(json.loads(Response(json.loads(rejected['response'])).text()))
            require(candidate == inputs['candidate'], 'construction correction candidate mismatch')
            data = merge_correction(candidate, data, {'commitments': 'id', 'new_symbols': 'name', 'alignments': 'name'})
        require(identity not in accepted, 'duplicate accepted construction batch response')
        accepted[identity] = {**data, 'commitments': normalize_commitments(data, items).to_dict()['commitments']}
    require(set(accepted) == {(b['plan_id'], b['index']) for b in batches}, 'construction response inventory mismatch')
    for batch in batches:
        saved = json.loads(artifacts[f"build-t-{batch['plan_id']}-{batch['index']}.json"])
        require(all(accepted[(batch['plan_id'], batch['index'])][key] == saved[key]
                    for key in ('commitments', 'new_symbols', 'alignments')),
                'construction response does not match batch')


def load_frozen(directory: Path, topic: str, config: dict, bank_version: str, root: Path) -> dict:
    """No EventLog instance here: source verification must never create lock/files."""
    directory = directory.resolve()
    path = directory / 'events.jsonl'
    records = read_log(path)
    require(path.with_suffix('.anchor').read_text().splitlines() == [r['hash'] for r in records],
            'source checkpoint mismatch')
    events = [r['event'] for r in records]
    freezes = [i for i, e in enumerate(events) if e['stage'] == 'commitments_frozen']
    require(len(freezes) == 1, 'source must have exactly one freeze; use the original builder run')
    freeze_index = freezes[0]
    completed = any(e['stage'] == 'run_finished' and (
        json.loads(e['payload_json']).get('state') == 'complete' or
        json.loads(e['payload_json']).get('state') == 'awaiting_selection' and
        any(later['stage'] == 'final_draft' for later in events[i + 1:]))
        for i, e in enumerate(events) if i > freeze_index)
    require(completed, 'source run is not complete')
    prefix = events[:freeze_index + 1]
    runs = [json.loads(e['payload_json']) for e in prefix if e['stage'] == 'run_started']
    require(len(runs) == 1, 'missing or ambiguous builder run provenance')
    run = runs[0]
    require(run['topic'] == topic, 'different topic')
    require(run['bank_version'] == bank_version, 'bank version drift')
    require(construction_config(run['config']) == construction_config(config), 'construction config drift')
    frozen = json.loads(prefix[-1]['payload_json'])
    require(frozen['bank_version'] == bank_version, 'freeze bank version drift')
    # Older native freezes (including the running pilot) embed the exact canonical
    # table but no file hash. Its canonical bytes are the original hash commitment.
    commitments = CommitmentSet.from_dict(frozen['commitments'])
    expected = digest(commitments.to_json())
    content = (directory / 'commitments.json').read_bytes()
    require(sha256(content).hexdigest() == expected, 'commitments file hash mismatch')
    require(frozen.get('commitments_sha256', expected) == expected, 'freeze hash mismatch')
    expected_contract = frozen['contract'] if 'contract' in frozen else json.loads(
        (Path(__file__).with_name('legacy_frozen_contract.json')).read_text())
    require(expected_contract == contract(root), 'config/schema-version drift')
    verify_receipts(prefix, root)
    builds = [e for e in prefix if e['label'] == 'MODEL' and e['stage'] in ('build_t', 'build_t_batch')
              and json.loads(e['payload_json'])['status'] == 'accepted']
    require(bool(builds), 'missing construction receipts')
    literature = run['literature']
    artifacts = {}
    if literature.startswith(HEADER):
        from ara.runtime.construction import PLAN_VERSION, CLOSURE_VERSION
        plans = [json.loads(e['payload_json']) for e in prefix if e['stage'] == 'build_t_plan']
        require(len(plans) == 1, 'missing construction plan')
        plan = plans[0]
        require(plan['plan']['version'] == PLAN_VERSION and
                plan['plan']['closure_version'] == CLOSURE_VERSION, 'construction schema-version drift')
        require(digest(canonical(plan['plan'])) == plan['plan_id'], 'broken construction plan hash')
        plan_path = directory / f"build-t-plan-{plan['plan_id']}.json"
        require(plan_path.read_text() == canonical(plan['plan']), 'broken construction plan artifact')
        artifacts[plan_path.name] = plan_path.read_text()
        outcomes = extraction_outcomes(prefix)
        completed = [json.loads(e['payload_json']) for e in prefix if e['stage'] == 'extraction_completed']
        require(bool(completed) and completed[-1]['literature_sha256'] == digest(literature)
                and assemble(outcomes) == literature, 'broken extraction provenance')
        require(any(e['stage'] == 'extraction_provenance_import' for e in prefix), 'missing extraction import')
        merged = [json.loads(e['payload_json']) for e in prefix if e['stage'] == 'build_t_merged']
        require(len(merged) == 1 and merged[0]['commitments'] == frozen['commitments'], 'broken construction merge')
        batches = [json.loads(e['payload_json']) for e in prefix if e['stage'] == 'build_t_batch_accepted']
        reconstructed = []
        for batch in batches:
            require(batch['plan_id'] == plan['plan_id'] and type(batch['index']) is int and
                    batch['index'] in {b['index'] for b in plan['plan']['batches']},
                    'broken construction batch identity')
            receipt = directory / f"build-t-{batch['plan_id']}-{batch['index']}.json"
            text = receipt.read_text()
            require(digest(text) == batch['output_hash'], 'broken construction batch receipt')
            artifacts[receipt.name] = text
            reconstructed.extend(json.loads(text)['commitments'])
        verify_batch_responses(prefix, batches, artifacts, literature)
        require(canonical(sorted(reconstructed, key=lambda c: c['id'])) ==
                canonical(sorted(frozen['commitments']['commitments'], key=lambda c: c['id'])),
                'construction receipts do not cover frozen T')
    else:
        from ara.runtime.providers import Response
        raw = Response(json.loads(builds[-1]['response']))
        data = json.loads(''.join(b['text'] for b in raw.served_content if b['type'] == 'text'))
        require(CommitmentSet.from_dict(data) == commitments, 'construction response does not match frozen T')
    return {'builder_run': str(directory), 'commitments_sha256': expected,
            'freeze_hash': records[freeze_index]['hash'], 'records': records[:freeze_index + 1],
            'contract_basis': 'recorded' if 'contract' in frozen else 'legacy embedded T and logged schemas',
            'commitments': commitments.to_dict(), 'artifacts': artifacts}


def import_frozen(log: EventLog, history: dict) -> CommitmentSet:
    # Nest original chain rows. Flattening would replay old lifecycle/route events
    # and cause budgets to charge prior spend. Original labels remain untouched.
    log.record('frozen_history_import', **history,
               note='Shared commitments; independent searches. Inherited history is not local spend or model memory.')
    commitments = CommitmentSet.from_dict(history['commitments'])
    save_immutable(log.path.parent / 'commitments.json', commitments.to_json())
    return commitments


def campaign_totals(log_paths: list[Path]) -> dict:
    """Deduplicate original MODEL receipts across builders, extraction and candidates."""
    charges = {}
    for path in log_paths:
        for row in read_log(path):
            event = row['event']
            inherited = (json.loads(event['payload_json'])['records']
                         if event['stage'] == 'frozen_history_import' else [])
            for e in [event, *[r['event'] for r in inherited]]:
                if e['label'] == 'MODEL':
                    charges[digest(canonical(e))] = e
    return {'cost_usd': round(sum(e['cost_usd'] for e in charges.values()), 10),
            'model_receipts': len(charges), 'receipt_ids': sorted(charges)}
