"""Read-only verification and inherited receipts for a shared frozen T."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from ara.runtime.cache import canonical, digest
from ara.runtime.extraction import HEADER, assemble, missing_lineage, save_immutable
from ara.runtime.logging import EventLog, read_log
from ara.types import CommitmentSet


# Search/writer settings and local caps may differ. Construction semantics may not.
CONSTRUCTION_KEYS = ('provider', 'model', 'effort', 'thinking', 'fallbacks', 'stages',
                     'formula_output_depth', 'validation_attempts', 'max_output_tokens')


def construction_config(config: dict) -> dict:
    return {key: value for key, value in config.items() if key in CONSTRUCTION_KEYS or
            key.startswith(('build_t_', 'working_t_', 'construction_', 'extracted_build_t_',
                            'select_t_roots_', 'extract_paper_'))}


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
    origins = set()
    for i, event in enumerate(events):
        payload = json.loads(event['payload_json'])
        if event['stage'] == 'extraction_provenance_import':
            count = payload['records']
            block = events[i + 1:i + 1 + count]
            require(len(block) == count and digest(canonical(block)) == payload['receipt_id'],
                    'broken extraction provenance receipt')
        if event['label'] != 'MODEL':
            continue
        require(payload.get('accounting') != 'reservation_unknown_actual', 'unknown construction/extraction spend')
        kind = event['stage']
        schema = root / 'schemas' / f'{kind}.json'
        template = root / 'prompts' / f'{kind}.txt'
        require(schema.is_file() and template.is_file(), 'unsupported receipt schema version')
        prefix = template.read_text() + '\nLOCAL_RESPONSE_SCHEMA (all constraints are mandatory)\n' + canonical(json.loads(schema.read_text()))
        require(event['prompt'].startswith(prefix + '\nINPUT_JSON\n'), 'schema/prompt version drift: ' + kind)
        if payload['status'] == 'accepted':
            key = payload['cache_key']
            require(not payload['cache_hit'] or key in origins, 'missing construction/extraction cache origin')
            if not payload['cache_hit']:
                origins.add(key)
    require(not missing_lineage(events), 'broken extraction lineage')
    starts = sum(e['stage'] == 'call_start' for e in events)
    finishes = sum(e['label'] == 'MODEL' and not json.loads(e['payload_json']).get('cache_hit') for e in events)
    require(starts == finishes, 'incomplete construction/extraction dispatch receipts')


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
        outcomes = [json.loads(e['payload_json']) for e in prefix if e['stage'] == 'extraction_outcome']
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
