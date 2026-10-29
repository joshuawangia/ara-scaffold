"""Deterministic exports whose sole source of run data is the event log."""
from __future__ import annotations

import json
import re
from pathlib import Path

from ara.runtime.cache import canonical
from ara.runtime.logging import read_log, pending_search_publications
from ara.runtime.search_publication import search_status
from ara.runtime.route_policy import route_contribution, frozen_from_events, provenance_from_events
from ara.types import RouteGraph
from ara.runtime.extraction import missing_lineage, publication_roster, literature_entry, PUBLICATION_POLICY
from ara.runtime.provenance import extraction_outcomes
from ara.runtime.grounding import evidence_items


def methodology(log_path: Path) -> str:
    records = read_log(log_path)
    events = [r['event'] for r in records]
    unpublished = pending_search_publications(events)
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
    unknown = [e for e, p in routing if p.get('accounting') == 'reservation_unknown_actual']
    pending = max(0, sum(e['stage'] == 'call_start' for e in events) -
                  sum(not p.get('cache_hit') for e, p in routing))
    extraction_calls = [e for e in calls if e['stage'] == 'extract_paper']
    outcomes = extraction_outcomes(events)
    lineage_missing = missing_lineage(events)
    lineage_incomplete = bool(lineage_missing) or any(e['stage'] == 'extraction_lineage_missing' for e in events)
    from ara.runtime.provenance import imported_event_indices
    inherited_indices = imported_event_indices(events)
    receipt_ids = []
    for i, event in enumerate(events):
        if event['stage'] == 'extraction_provenance_import':
            payload = json.loads(event['payload_json'])
            inherited_indices.update(range(i + 1, min(len(events), i + 1 + payload['records'])))
            receipt_ids.append(payload.get('receipt_id'))
    def raw_totals(selected):
        return {'cost_usd': round(sum(e['cost_usd'] for e in selected), 10),
                'tokens': {key: sum(e['usage'][key] for e in selected) for key in (
                    'input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_write_tokens', 'server_tool_uses')},
                'model_calls': sum(e['label'] == 'MODEL' for e in selected),
                'human_reported_minutes': sum(json.loads(e['payload_json']).get('reported_minutes', 0)
                                              for e in selected if e['label'] == 'HUMAN')}
    def split_totals(selected):
        measured = [e for e in selected if json.loads(e['payload_json']).get('accounting') != 'reservation_unknown_actual']
        reserved = [e for e in selected if json.loads(e['payload_json']).get('accounting') == 'reservation_unknown_actual']
        return {'measured_usage': raw_totals(measured), 'unknown_usage_reservations': raw_totals(reserved),
                'budget_accounted': raw_totals(selected)}
    def totals(selected):
        return {**raw_totals(selected), **split_totals(selected)}
    extraction_summary = {
        **split_totals(extraction_calls),
        'acceptance_note': 'Accepted range union; reconciliation is one best-effort pass. Open gaps and thin ranges are not completeness guarantees.',
        'publication_roster': publication_roster(outcomes),
        'snapshot_unions': [dict(source_id=p['source_id'], **p['snapshot_union']) for p in outcomes if 'snapshot_union' in p],
        'limitations': [dict(source_id=p['source_id'], open_gaps=literature_entry(p).get('open_gaps', []), dispositions=p.get('dispositions', [])) for p in outcomes if p.get('range_union_policy') or p.get('publication_policy') == PUBLICATION_POLICY],
        'grounding': [dict(source_id=p['source_id'], **p['grounding'], quarantined=len(p['quarantined'])) for p in outcomes if 'grounding' in p],
        'quarantined': [dict(source_id=p['source_id'], entries=p['quarantined']) for p in outcomes if p.get('quarantined')],
        'grounded_item_counts_by_kind': {kind: sum(item['kind'] == kind for p in outcomes if 'grounding' in p for item in evidence_items(p))
                                         for kind in sorted({item['kind'] for p in outcomes for item in p['items']})},
        'schema_versions': sorted({p.get('schema_version', 1) for p in outcomes if p.get('items')}),
        'item_counts_by_kind': {kind: sum(item['kind'] == kind for p in outcomes for item in p['items'])
                                for kind in sorted({item['kind'] for p in outcomes for item in p['items']})},
        'range_calls': sum(e['stage'] == 'extraction_range' for e in events),
        'production_lineage_complete': not lineage_incomplete,
        'missing_origin_cache_keys': lineage_missing,
        'partial': [{'source_id': p['source_id'], 'affected_pages': p['affected_pages'],
                     'page_diagnostics': p['page_diagnostics']} for p in outcomes if p['status'] == 'partial'],
        'page_diagnostics': [{'source_id': p['source_id'], 'pages': p['page_diagnostics']}
                             for p in outcomes if p.get('page_diagnostics')],
        'call_count': len(extraction_calls),
        'dispatch_count': sum(not json.loads(e['payload_json']).get('cache_hit') for e in extraction_calls),
        'cache_replays': sum(bool(json.loads(e['payload_json']).get('cache_hit')) for e in extraction_calls),
        'tokens': {k: sum(e['usage'][k] for e in extraction_calls) for k in (
            'input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_write_tokens', 'server_tool_uses')},
        'cost_usd': round(sum(e['cost_usd'] for e in extraction_calls), 10),
        'models': served_by_kind.get('extract_paper', []),
        'extracted': [p['source_id'] for p in outcomes if p['status'] == 'extracted'],
        'record_only': [{'source_id': p['source_id'], 'reason': p['reason']} for p in outcomes
                        if p['status'] == 'record only, not extracted'],
        'failed': [p['source_id'] for p in outcomes if p['status'] == 'failed'],
        'failed_papers': [p for p in outcomes if p['status'] == 'failed'],
        'failure_history': [json.loads(e['payload_json']) for e in events if e['stage'] == 'extraction_outcome'
                            and json.loads(e['payload_json'])['status'] == 'failed'],
        'failure_policy': next((json.loads(e['payload_json']) for e in reversed(events)
                                if e['stage'] == 'extraction_batch_started'), None),
        'stops': [json.loads(e['payload_json']) for e in events if e['stage'] == 'extraction_stopped'],
        'origin': 'SYSTEM/MODEL',
        'upstream_receipts_imported': any(e['stage'] == 'extraction_provenance_import' for e in events),
    }
    cli_calls = [(e, p) for e, p in routing if p.get('provider') in ('claude_code', 'codex_cli')]
    provider_methods = {
        'requested_models_by_stage': {kind: sorted({e['model_id'] for e in calls if e['stage'] == kind}) for kind in served_by_kind},
        'providers_by_stage': {kind: sorted({p.get('provider', 'anthropic_or_mock_legacy') for e, p in routing
                                             if e['stage'] == kind}) for kind in served_by_kind},
        'claude_code': [{key: p.get(key) for key in ('cli_version', 'isolation_flags', 'fresh_cwd_and_config',
                         'token_estimate_method', 'calibration', 'usd_cap_policy', 'token_cap_policy', 'effective_prompt_note',
                         'operator_identity_output_scan', 'web_retrieval', 'concurrency', 'max_cli_turns', 'schema_transport',
                         'auth_mode', 'auth_transport', 'auth_threat_model', 'credential_output_scan')}
                       for _, p in cli_calls if p.get('provider') == 'claude_code'][:1],
        'codex_cli': [{key:p.get(key) for key in ('cli_version', 'isolation_flags', 'fresh_cwd_and_config',
                         'token_estimate_method', 'calibration', 'usd_cap_policy', 'token_cap_policy', 'effective_prompt_note',
                         'operator_identity_output_scan', 'web_retrieval', 'concurrency', 'max_cli_turns', 'schema_transport',
                         'auth_mode', 'auth_transport', 'auth_threat_model', 'credential_output_scan', 'served_model_policy',
                         'tokenizer_note', 'subscription_cost_note', 'host_context_isolation', 'output_bound_note', 'visible_tool_policy', 'schema_transform')}
                       for _,p in cli_calls if p.get('provider') == 'codex_cli'][:1],
        'evidence_retrieval': [dict(provider='codex_cli', method='Codex web search',
                                    status=p.get('status'), cache_hit=p.get('cache_hit'),
                                    **p['cli']['web_search'])
                               for e,p in cli_calls if e['stage']=='search_evidence'
                               and p.get('cli', {}).get('web_search')],
        'token_cap_policies': sorted({p.get('token_cap_policy', 'legacy_history_inclusive') for _, p in cli_calls}),
        'estimate_observations': [json.loads(e['payload_json']) for e in events if e['stage']=='provider_estimate_observation'],
        'isolation_preflights': [p.get('isolation') for e, p in cli_calls if e['stage'] == 'isolation_canary'],
        'subscription_usage': {'cost_equivalent_usd': sum((p.get('subscription_usage', {}).get('cost_equivalent_usd') or 0)
                                  for e, p in cli_calls if not p.get('cache_hit')),
                               'cost_equivalent_unavailable_calls': sum(p.get('subscription_usage', {}).get('cost_equivalent_usd') is None for e,p in cli_calls if not p.get('cache_hit')),
                               'note': 'Codex does not report a cost equivalent; missing amounts are unknown. CLI-reported subscription list-price equivalent, not measured API USD; dollar caps do not apply. Token-cap policy is recorded per call; imported and local usage remain separately reported.'},
        'stage_transport_note': ('Extraction retains its imported API receipts when present. '
                                'Construction and search stages listed as claude_code or codex_cli use fresh headless subagent sessions. '
                                'Stages absent from the log are not claimed as executed.') if cli_calls else None,
    }
    commitments = frozen_from_events(events)
    summary = {
        **split_totals(events),
        'provider_methodology': provider_methods,
        'extraction': extraction_summary,
        'search': {**search_status(events),
                   'target_preflights': [json.loads(e['payload_json']) for e in events if e['stage'] in ('target_triviality_preflight','target_vocabulary_preflight','target_contribution_preflight','target_own_thesis_classification')],
                   'routes': [dict(id=p['graph']['id'], **route_contribution(RouteGraph.from_dict(p['graph']), commitments, provenance_from_events(events, commitments)))
                              for e in events if e['stage']=='route' for p in [json.loads(e['payload_json'])]]},
        'freeze_forks': [json.loads(e['payload_json']) for e in events if e['stage']=='freeze_forked'],
        'construction': {'structure_gates': [json.loads(e['payload_json']) for e in events if e['stage'] == 'build_t_structure_gate'],
                         'structure_outcomes': [json.loads(e['payload_json']) for e in events if e['stage'] == 'build_t_structure_outcome'],
                         'frozen_catalogues': [json.loads(e['payload_json']) for e in events if e['stage'] == 'symbol_catalogue_frozen'],
                         'commitment_provenance': [json.loads(e['payload_json']) for e in events if e['stage'] == 'commitment_provenance_frozen'],
                         'support_omitted': [dict(index=p['index'], evidence_id=id, omitted_support_ids=ids)
                         for e in events if e['stage'] == 'build_t_closure'
                         for p in [json.loads(e['payload_json'])] for id, ids in p.get('support_omitted', {}).items()],
                         'support_policy': 'Budget-cut frontier items are attributed assumed premises (support_omitted); routes using them are conditional on those premises. Immutable full sources retain omitted support.',
                         'plans': [json.loads(e['payload_json']) for e in events if e['stage'] == 'build_t_plan'],
                         'stage_dispatches': [dict(kind=e['stage'], stage=json.loads(e['payload_json']).get('dispatch_stage', e['stage']),
                                                  provider=json.loads(e['payload_json']).get('provider'),
                                                  requested_model=e['model_id'], served_model=e['model_version'])
                                              for e in calls if e['stage'] in ('select_t_roots', 'build_t_batch')],
                         'skipped_windows': [json.loads(e['payload_json']) for e in events if e['stage'] == 'build_t_batch_skipped'],
                         'provider_refusals': [json.loads(e['payload_json']) for e in events if e['stage'] == 'construction_provider_refusal'],
                         'counter_refusals': [json.loads(e['payload_json']) for e in events if e['stage'] == 'token_count_refused'],
                         'counter_failures': [json.loads(e['payload_json']) for e in events if e['stage'] == 'token_count_failed'],
                         'resumes': [json.loads(e['payload_json']) for e in events if e['stage'] == 'construction_resumed'],
                         'share_borrowing': [json.loads(e['payload_json']) for e in events if e['stage'] == 'build_t_share_borrowed'],
                         'global_exhaustion': [json.loads(e['payload_json']) for e in events if e['stage'] == 'build_t_global_exhaustion'],
                         'batches': sum(e['stage'] == 'build_t_batch_accepted' for e in events),
                         'freezes': sum(e['stage'] == 'commitments_frozen' for e in events),
                         'closure': [json.loads(e['payload_json']) for e in events if e['stage'] == 'build_t_closure']},
        'accounting_complete': not unknown and not pending and not lineage_incomplete and not unpublished,
        'unpublished_search_batches': unpublished,
        'local_totals': totals([e for i, e in enumerate(events) if i not in inherited_indices]),
        'inherited_totals': totals([e for i, e in enumerate(events) if i in inherited_indices]),
        'inherited_receipt_ids': receipt_ids,
        'incomplete_calls': len(unknown) + pending,
        'unresolved_dispatches': pending,
        'served_models_by_kind': served_by_kind,
        'fallback_calls': fallback_calls,
        'models': sorted({(e['model_id'], e['model_version']) for e in calls}, key=repr),
        'roles': sorted({e['stage'] for e in calls}),
        'tokens': {k: sum(e['usage'][k] for e in events) for k in (
            'input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_write_tokens', 'server_tool_uses')},
        'cost_usd': round(sum(e['cost_usd'] for e in events), 10),
        'accounting_note': ('INCOMPLETE search accounting: inspect durable per-job journals; publication did not finish.'
                            if unpublished else 'INCOMPLETE production accounting: extraction cache replay lacks original receipts.'
                            if lineage_incomplete else 'INCOMPLETE totals: unknown usage, counted at reservation (upper bound). Reservations are not measured charges.'
                            if unknown or pending else 'Complete recorded usage; prices are configuration assumptions.'),
        'reconciliation_policy': [json.loads(e['payload_json']) for e in events
                                  if e['stage'] == 'unknown_usage_reconciled'],
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
