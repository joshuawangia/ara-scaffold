"""Deterministic exports whose sole source of run data is the event log."""
from __future__ import annotations

import json
import re
from pathlib import Path

from ara.runtime.cache import canonical
from ara.runtime.logging import read_log


def methodology(log_path: Path) -> str:
    records = read_log(log_path)
    events = [r['event'] for r in records]
    calls = [e for e in events if e['label'] == 'MODEL']
    human = [e for e in events if e['label'] == 'HUMAN']
    payloads = [json.loads(e['payload_json']) for e in human]
    routing = [(e, json.loads(e['payload_json'])) for e in calls]
    served_by_kind = {
        kind: sorted({p.get('served_model') or e['model_version'] for e, p in routing
                      if e['stage'] == kind and (p.get('served_model') or e['model_version'])})
        for kind in sorted({e['stage'] for e in calls})
    }
    fallback_calls = [
        {'kind': e['stage'], 'requested_model': e['model_id'], 'served_model': p['served_model'],
         'status': p['status'], 'cache_hit': p['cache_hit'],
         'blocks': p['fallback_blocks'], 'iterations': p['fallback_iterations']}
        for e, p in routing if p.get('fallback_used')
    ]
    summary = {
        'served_models_by_kind': served_by_kind,
        'fallback_calls': fallback_calls,
        'models': sorted({(e['model_id'], e['model_version']) for e in calls}, key=repr),
        'roles': sorted({e['stage'] for e in calls}),
        'tokens': {k: sum(e['usage'][k] for e in events) for k in (
            'input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_write_tokens', 'server_tool_uses')},
        'cost_usd': round(sum(e['cost_usd'] for e in events), 10),
        'accounting_note': 'Totals include conservative reservations for failed calls with unknown usage; these are not measured charges.',
        'unknown_spend_reservations_usd': sum(e['cost_usd'] for e in calls
            if json.loads(e['payload_json']).get('accounting') == 'reservation_unknown_actual'),
        'model_call_seconds': sum(e['wall_seconds'] for e in events),
        'machine_seconds': sum(json.loads(e['payload_json']).get('machine_elapsed_seconds', 0)
                               for e in events if e['stage'] == 'command_timing'),
        'human_elapsed_seconds': sum(p.get('elapsed_seconds', 0) for p in payloads),
        'human_reported_minutes': sum(p.get('reported_minutes', 0) for p in payloads),
        'human_time_note': 'Elapsed prompt time and operator-reported time are separate, not inferred from CLI startup.',
        'log_records': len(records),
        'last_record_hash': records[-1]['hash'] if records else None,
    }
    # Include every event verbatim. This is the evidence for architecture, bank,
    # candidates, searches, decisions, selections, prompts, tools and human input.
    return ('# Methodology\n\nGenerated only from the event log. Search and audit are model assessments; '
            'formal licensing belongs to the engine.\n\n## Accounting\n\n```json\n' +
            json.dumps(summary, indent=2, ensure_ascii=False) + '\n```\n\n' +
            ('Server-side fallback served calls: ' + '; '.join(
                f"{c['kind']} → {c['served_model']} ({c['status']})" for c in fallback_calls) + '.\n\n'
             if fallback_calls else 'No server-side fallback was reported.\n\n') +
            '## Complete evidence\n\n' +
            '\n'.join('```json\n' + canonical(e) + '\n```\n' for e in events))


def export_run(log_path: Path, output: Path, redactions: tuple[str, ...] = ()) -> tuple[Path, Path | None]:
    events = [r['event'] for r in read_log(log_path)]
    drafts = [json.loads(e['payload_json'])['draft'] for e in events if e['stage'] == 'final_draft']
    output.mkdir(parents=True, exist_ok=True)
    report = output / 'methodology.md'
    report.write_text(methodology(log_path))
    essay_path = None
    if drafts:
        draft = drafts[-1]
        body = re.sub(r'\[\[node:[^\]]+\]\]', '', draft['body'])
        text = draft['title'] + '\n\n' + body.strip()
        if draft['bibliography']:
            text += '\n\nBibliography\n' + '\n'.join(b['text'] for b in draft['bibliography'])
        for identifier in redactions:
            if identifier:
                text = text.replace(identifier, '[REDACTED]')
        essay_path = output / 'essay.txt'
        essay_path.write_text(text + '\n')
    elif (output / 'essay.txt').exists():
        # Never let an earlier complete export masquerade as the current result.
        raise ValueError('no final draft in log; output already contains essay.txt')
    return report, essay_path
