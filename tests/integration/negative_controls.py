"""Integration production-wire controls; restore exactly after each mutation."""
from pathlib import Path
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('writer_marker_coverage', 'ara/runtime/calls.py', 'require(markers == {node.id for node in route.nodes},', 'require(True,', 'tests/runtime/test_writer_validation.py::test_invalid_writer_corrects_before_audit'),
    ('writer_nontrivial_body', 'ara/runtime/calls.py', 'require(len(text_tokens) >= 2,', 'require(True,', 'tests/runtime/test_writer_validation.py::test_invalid_writer_corrects_before_audit'),
    ('writer_citation_padding', 'ara/runtime/calls.py', '\\]\\]|\\[cite:[^\\]]+\\]', '\\]\\]', 'tests/runtime/test_writer_validation.py::test_invalid_writer_corrects_before_audit'),
    ('writer_punctuation_padding', 'ara/runtime/calls.py', 'if any(char.isalnum() for char in token)', 'if True', 'tests/runtime/test_writer_validation.py::test_invalid_writer_corrects_before_audit'),
    ('writer_correction_path', 'ara/runtime/calls.py', "if validating and not (kind == 'audit_essay' and isinstance(exc, Rejected)):", "if validating and kind != 'write_essay' and not (kind == 'audit_essay' and isinstance(exc, Rejected)):", 'tests/runtime/test_writer_validation.py::test_invalid_writer_corrects_before_audit'),
    ('writer_exhaustion_bound', 'ara/runtime/calls.py', 'for attempt in range(attempts):', 'for attempt in range(attempts - 1):', 'tests/runtime/test_writer_validation.py::test_writer_correction_exhaustion_clean_cli_stop'),
    ('writer_failure_not_cached', 'ara/runtime/calls.py', '            if validating and not', "            if kind == 'write_essay': self.cache.put(key, {'raw': raw})\n            if validating and not", 'tests/runtime/test_writer_validation.py::test_writer_correction_exhaustion_clean_cli_stop'),
    ('writer_projection', 'ara/runtime/calls.py', "return {'outline': self.essay_outline(route), 'word_limit':", "return {'outline': route.to_dict(), 'word_limit':", 'tests/runtime/test_essay_outline.py::test_route_status_and_cost_never_reach_writer'),
    ('shared_audit_outline', 'ara/runtime/calls.py', "'outline': self.essay_outline(route)}", "'outline': {'nodes': [], 'links': []}}", 'tests/runtime/test_essay_outline.py::test_writer_and_auditor_receive_same_content_only_outline'),
    ('scheme_name', 'ara/runtime/calls.py', "'scheme': entry.name", "'scheme': entry.id", 'tests/runtime/test_essay_outline.py::test_writer_and_auditor_receive_same_content_only_outline'),
    ('inference_links', 'ara/runtime/calls.py', "'premises': list(node.children)", "'premises': []", 'tests/runtime/test_essay_outline.py::test_writer_and_auditor_receive_same_content_only_outline'),
    ('answered_cq_content', 'ara/runtime/calls.py', "'answered_questions': answered}", "'answered_questions': []}", 'tests/runtime/test_essay_outline.py::test_writer_and_auditor_receive_same_content_only_outline'),
    ('only_answered_cqs', 'ara/runtime/calls.py', 'if answer.answered and answer.answer.strip():', 'if answer.answer.strip():', 'tests/runtime/test_essay_outline.py::test_writer_and_auditor_receive_same_content_only_outline'),
    ('assumption_discharge', 'ara/runtime/calls.py', 'if scopes:', 'if False:', 'tests/runtime/test_essay_outline.py::test_outline_preserves_assumption_discharge'),
    ('new_premise_rejected', 'ara/runtime/calls.py', "if item['asserts_premise_or_inference_not_in_outline']", 'if False', 'tests/runtime/test_calls.py::test_audit_rejects_extra_step'),
    ('transition_allowed', 'ara/runtime/calls.py', "if item['asserts_premise_or_inference_not_in_outline']", "if item['asserts_premise_or_inference_not_in_outline'] or not item['node_ids']", 'tests/runtime/test_essay_outline.py::test_transition_without_new_premise_is_not_extra'),
    ('unknown_scheme_rejected', 'ara/runtime/calls.py', "require(entry is not None, 'outline inference has unknown bank entry')", 'entry = entry or bank.entries[0]', 'tests/runtime/test_essay_outline.py::test_unknown_scheme_name_is_not_invented'),
    ('compact_formula_projection', 'ara/runtime/providers.py', 'return project(original)', 'return schema', 'tests/runtime/test_provider.py::test_compact_formula_projection_keeps_local_operator_checks'),
    ('full_schema_prompt', 'ara/runtime/calls.py', "if kind != 'search_evidence':", 'if False:', 'tests/runtime/test_calls.py::test_full_local_schema_reaches_provider_and_log'),
    ('compound_arguments', 'ara/runtime/providers.py', "result['minItems'] = min(1, value['minItems'])", 'pass', 'tests/runtime/test_provider.py::test_compound_generation_cannot_omit_all_arguments'),
    ('validation_retry', 'ara/runtime/calls.py', "attempts = self.config.get('validation_attempts', 1)", 'attempts = 1', 'tests/runtime/test_calls.py::test_validation_retry_is_accounted_and_admitted[False]'),
    ('retry_admission', 'ara/runtime/budget.py', "if self.cap_tokens(subscription) + sum(tokens(r.usage) for r in self._reservations) + tokens(usage) > self.config['token_cap']:", 'if False:', 'tests/runtime/test_calls.py::test_validation_retry_is_accounted_and_admitted[True]'),
    ('negative_audit_is_final', 'ara/runtime/calls.py', "if validating and not (kind == 'audit_essay' and isinstance(exc, Rejected)):", 'if validating:', 'tests/runtime/test_calls.py::test_audit_rejects_extra_step'),
    ('route_artifacts', 'ara/runtime/orchestration.py', "save_route(calls.log.path.parent / 'routes', route, commitments, provenance)", 'pass', 'tests/integration/test_cli_e2e.py'),
    ('provider_not_projection', 'ara/runtime/providers.py', "'allOf', 'not'", "'allOf'", 'tests/runtime/test_provider.py::test_live_observed_not_constraint_projected_but_locally_enforced'),
    ('fallback_header', 'ara/runtime/providers.py', "betas=['server-side-fallback-2026-06-01']", "betas=['server-side-fallback-2026-07-01']", 'tests/runtime/test_fallbacks.py::test_fallback_request_shape'),
    ('fallback_config_validation', 'ara/runtime/providers.py', "if fallbacks != 'off' and not (", 'if False and not (', 'tests/runtime/test_fallbacks.py::test_invalid_fallback_config_is_rejected'),
    ('fallback_cache', 'ara/runtime/calls.py', "'fallbacks': stage_settings(self.config, kind).get('fallbacks', ['claude-opus-4-8'])", "'fallbacks': 'off'", 'tests/runtime/test_fallbacks.py::test_fallback_mode_partitions_cache'),
    ('fallback_array', 'ara/runtime/providers.py', "fallbacks=[{'model': model} for model in fallbacks]", "fallbacks='default'", 'tests/runtime/test_fallbacks.py::test_fallback_request_shape[explicit]'),
    ('served_model_price', 'ara/runtime/budget.py', "served_model = raw['model']", "served_model = self.config['model']", 'tests/runtime/test_fallbacks.py::test_fallback_billing_logging_and_methodology[False-True]'),
    ('fallback_iterations_price', 'ara/runtime/budget.py', "model = iteration.get('model') or served_model", "model = self.config['model']", 'tests/runtime/test_fallbacks.py::test_fallback_billing_logging_and_methodology[True-True]'),
    ('fallback_logging', 'ara/runtime/providers.py', "'served_model': self.raw['model']", "'served_model': 'claude-opus-5'", 'tests/runtime/test_fallbacks.py::test_fallback_billing_logging_and_methodology'),
    ('unpriced_model', 'ara/runtime/budget.py', "r = self.config['pricing'].get(model)", "r = self.config['pricing'].get(model, self.rates)", 'tests/runtime/test_fallbacks.py::test_unpriced_model_stops_loudly'),
    ('fallback_refusal', 'ara/runtime/calls.py', 'require(raw[\'stop_reason\'] == \'end_turn\', f\'provider stop: {raw["stop_reason"]}\')', 'pass', 'tests/runtime/test_fallbacks.py::test_final_fallback_refusal_is_not_retried'),
    ('fallback_boundary', 'ara/runtime/providers.py', 'return content[boundary + 1:]', 'return content', 'tests/runtime/test_fallbacks.py::test_fallback_billing_logging_and_methodology[True-True]'),
    ('fallback_disclosure', 'ara/runtime/export.py', "for e, p in routing if p.get('fallback_used')", 'for e, p in routing if False', 'tests/runtime/test_fallbacks.py::test_fallback_billing_logging_and_methodology'),
    ('fallback_rate_validation', 'ara/runtime/budget.py', "for rates in config['pricing'].values():", 'for rates in [self.rates]:', 'tests/runtime/test_fallbacks.py::test_fallback_rates_are_validated'),
    ('ambiguous_iteration', 'ara/runtime/budget.py', "if fallback and not iteration.get('model'):", 'if False:', 'tests/runtime/test_fallbacks.py::test_ambiguous_iteration_model_stops'),
    ('fallback_off', 'ara/runtime/providers.py', "if fallbacks and fallbacks != 'off':", 'if True:', 'tests/runtime/test_fallbacks.py::test_fallback_request_shape[off]'),
    ('extraction_schema', 'ara/runtime/calls.py', 'validate_local(schema, data, self.config)', "None if kind == 'extract_paper' else validate_local(schema, data, self.config)", 'tests/runtime/test_extraction.py::test_schema_and_reference_rejection[extra]'),
    ('extraction_attribution', 'schemas/extract_paper.json', '"author_claim",', '"P", "author_claim",', 'tests/runtime/test_extraction.py::test_schema_and_reference_rejection[attribution]'),
    ('extraction_source', 'ara/runtime/calls.py', "require(data['source_id'] == paper.source_id,", 'require(True,', 'tests/runtime/test_extraction.py::test_schema_and_reference_rejection[source]'),
    ('extraction_item_source', 'ara/runtime/calls.py', 'require(item.source_id == paper.source_id,', 'require(True,', 'tests/runtime/test_extraction.py::test_schema_and_reference_rejection[item_source]'),
    ('extraction_page_bounds', 'ara/runtime/calls.py', 'require(1 <= item.page_start <= item.page_end <= len(paper.pages),', 'require(True,', 'tests/runtime/test_extraction_v5.py::test_reversed_pages_repaired_logged_and_out_of_bounds_refused'),
    ('extraction_pdf_pages', 'ara/runtime/extraction.py', "page.extract_text() or ''", "'R'", 'tests/runtime/test_extraction.py::test_page_text_and_immutable_contract'),
    ('extraction_sparse_image_detection', 'ara/runtime/extraction.py', 'if image_or_form and chars < 200:', 'if False:', 'tests/runtime/test_extraction_fix1.py::test_sparse_image_pages_are_partial[P]'),
    ('extraction_fallback_marker', 'ara/runtime/extraction.py', "outcome = {**base, 'status': 'record only, not extracted'", "outcome = {**base, 'status': 'extracted'", 'tests/runtime/test_extraction.py::test_missing_fallback_and_methodology'),
    ('extraction_strict_refusal', 'ara/runtime/extraction.py', "if missing == 'refuse':", 'if False:', 'tests/runtime/test_extraction.py::test_refuse_missing_and_no_publication'),
    ('extraction_counted_oversize', 'ara/runtime/extraction.py', 'return usage.initial_input_tokens', 'return 0', 'tests/runtime/test_extraction_rich.py::test_page_ranges_and_logged_reconciliation'),
    ('extraction_provider_context', 'ara/runtime/calls.py', 'if admission and not fits:', "if admission and not fits and kind != 'extract_paper':", 'tests/runtime/test_extraction.py::test_provider_context_bound_rechecked'),
    ('extraction_admission_cap', 'ara/runtime/budget.py', "if not subscription and stage == 'extract_paper' and self.extraction_cost() + sum(r.cost for r in self._reservations if r.stage == stage) + self.cost(usage, model=model, subscription=subscription) > Decimal(str(", 'if False and self.extraction_cost() + self.cost(usage, model=model) > Decimal(str(', 'tests/runtime/test_extraction.py::test_extraction_budget_admission[extraction_cost_cap_usd]'),
    ('extraction_actual_cap', 'ara/runtime/budget.py', "if not subscription and stage == 'extract_paper' and self.extraction_cost() > Decimal(str(", 'if False and self.extraction_cost() > Decimal(str(', 'tests/runtime/test_extraction.py::test_extraction_actual_cost_cap'),
    ('extraction_retry', 'ara/runtime/calls.py', "attempts = self.config.get('validation_attempts', 1)", "attempts = 1 if kind == 'extract_paper' else self.config.get('validation_attempts', 1)", 'tests/runtime/test_extraction.py::test_extraction_retry_and_reservation'),
    ('extraction_model_logging', 'ara/runtime/calls.py', "self._event(kind, prompt, raw, usage, cost, start, cached, 'accepted', None, key, attempt=attempt)", "None if kind == 'extract_paper' else self._event(kind, prompt, raw, usage, cost, start, cached, 'accepted', None, key, attempt=attempt)", 'tests/runtime/test_extraction.py::test_missing_fallback_and_methodology'),
    ('extraction_export_accounting', 'ara/runtime/export.py', "'extraction': extraction_summary,", "'extraction': {},", 'tests/runtime/test_extraction.py::test_missing_fallback_and_methodology'),
    ('extraction_cache', 'ara/runtime/calls.py', 'saved = self.cache.get(key)', "saved = None if kind == 'extract_paper' else self.cache.get(key)", 'tests/runtime/test_extraction.py::test_cache_replay_and_pdf_identity'),
    ('extraction_pdf_cache_identity', 'ara/runtime/extraction.py', "'pdf_sha256': self.pdf_sha256, 'pages':", "'pdf_sha256': None, 'pages':", 'tests/runtime/test_extraction.py::test_cache_replay_and_pdf_identity'),
    ('extraction_provenance_integrity', 'ara/runtime/extraction.py', "if events[-1]['stage'] != 'extraction_completed' or complete['literature_sha256'] != digest(text) or assemble(outcomes) != text:", 'if False:', 'tests/runtime/test_extraction.py::test_provenance_integrity'),
    ('extraction_cli_import', 'ara/runtime/verification.py', '_append_receipts(log, events, origin)', 'pass' , 'tests/runtime/test_extraction.py::test_extract_cli_to_build_t_native_path'),
    ('extraction_ai_label', 'ara/runtime/cli.py', 'literature=literature if args.literature is not None and not provenance else None,', 'literature=literature if args.literature is not None else None,', 'tests/runtime/test_extraction.py::test_extract_cli_to_build_t_native_path'),
    ('extraction_t_citation', 'ara/runtime/construction.py', "require(c.citation == items[c.id]['citation'],", 'require(True,', 'tests/runtime/test_extraction_round3.py::test_fixed_inventory_boundary_has_no_freeze[citation]'),
    ('extraction_no_record_only_t', 'ara/runtime/calls.py', "require(bool(allowed), 'no extracted claims available to build T')", 'pass', 'tests/runtime/test_extraction.py::test_record_only_cannot_build_t'),
    ('extraction_estimate', 'ara/runtime/extraction.py', 'input_tokens=pages * per_page + readable * overhead', 'input_tokens=readable * overhead', 'tests/runtime/test_extraction.py::test_estimate_only_never_dispatches'),
    ('build_t_context', 'ara/runtime/calls.py', 'if admission and not fits:', "if admission and not fits and kind != 'build_t':", 'tests/runtime/test_extraction_fix1.py::test_build_t_counted_context_refusal'),
    ('extraction_blank_pages', 'ara/runtime/extraction.py', "unavailable = 'empty_pdf' if not pages else None", "unavailable = 'empty_pdf' if not pages or any(d.reason == 'blank_page' for d in diagnostics) else None", 'tests/runtime/test_extraction_fix1.py::test_blank_pages_retained_without_rejecting_paper'),
    ('extraction_page_numbers', 'ara/runtime/extraction.py', 'pages.append(PageText(i, text))', 'pages.append(PageText(len([p for p in pages if p.text.strip()]) + 1, text))', 'tests/runtime/test_extraction_fix1.py::test_blank_pages_retained_without_rejecting_paper'),
    ('extraction_partial_status', 'ara/runtime/extraction.py', "'status': 'partial' if paper.affected_pages else 'extracted',", "'status': 'extracted',", 'tests/runtime/test_extraction_fix1.py::test_sparse_image_pages_are_partial[P]'),
    ('extraction_unread_page_citation', 'ara/runtime/calls.py', 'require(item.page_start in readable and item.page_end in readable and', 'require(True or item.page_start in readable and item.page_end in readable and', 'tests/runtime/test_extraction_fix1.py::test_extraction_cannot_cite_unread_image_page'),
    ('extraction_blank_stream_detection', 'ara/runtime/extraction.py', 'contents.operations if contents is not None else []', 'contents.operations if contents else []', 'tests/runtime/test_extraction_fix1.py::test_sparse_image_pages_are_partial[P]'),
    ('extraction_counted_not_bytes', 'ara/runtime/extraction.py', "if prompt_bytes + maximum > calls.config['model_context_token_bound']:", "if prompt_bytes + maximum > calls.config['model_context_token_bound']:\n            calls.budget.stop('byte bound', 'extract_paper')", 'tests/runtime/test_extraction_fix1.py::test_large_bytes_use_counted_tokens'),
    ('extraction_cache_lineage_import', 'ara/runtime/extraction.py', '    if missing_lineage(events):\n        raise', '    if False:\n        raise', 'tests/runtime/test_extraction_fix1.py::test_fresh_cache_artifact_refused_at_cli_import'),
    ('extraction_cache_lineage_accounting', 'ara/runtime/export.py', "'accounting_complete': not unknown and not pending and not lineage_incomplete and not unpublished,", "'accounting_complete': not unknown and not pending,", 'tests/runtime/test_extraction_fix1.py::test_fresh_cache_artifact_refused_at_cli_import'),
    ('extraction_local_inherited_totals', 'ara/runtime/export.py', "'local_totals': totals([e for i, e in enumerate(events) if i not in inherited_indices]),", "'local_totals': totals(events),", 'tests/runtime/test_extraction_fix1.py::test_fresh_cache_artifact_refused_at_cli_import'),
    ('extraction_enclosing_cap_warning', 'ara/runtime/extraction.py', "print('planned batch exceeds enclosing caps', flush=True)", 'pass', 'tests/runtime/test_extraction_fix1.py::test_preflight_flags_caps_and_profile_is_explicit'),
    ('extraction_batch_profile', 'ara/runtime/cli.py', 'if args.profile:\n                apply_profile(config, args.profile)\n            validate_profile_caps(config, args.profile)', 'if args.profile:\n                pass\n            validate_profile_caps(config, args.profile)', 'tests/runtime/test_extraction_fix1.py::test_preflight_flags_caps_and_profile_is_explicit'),
    ('extracted_t_output_capacity', 'ara/runtime/calls.py', "maximum = self.config['extracted_build_t_max_output_tokens']\n        if kind == 'isolation_canary':\n            maximum = 4096\n        identity", "maximum = self.config['max_output_tokens']\n        if kind == 'isolation_canary':\n            maximum = 4096\n        identity", 'tests/runtime/test_extraction_fix1.py::test_capacity53_maximum_through_cli'),
    ('build_t_retry_context', 'ara/runtime/calls.py', 'estimate = self.count_request(kind, inputs, maximum=maximum, admission=True)', "estimate = self.count_request(kind, inputs, maximum=maximum, admission='validation_feedback' not in inputs)", 'tests/runtime/test_extraction_fix1.py::test_build_t_retry_recounts_feedback'),
    ('extraction_import_idempotence', 'ara/runtime/provenance.py', "if any(e['stage'] == IMPORT_STAGE and", "if False and any(e['stage'] == IMPORT_STAGE and", 'tests/runtime/test_extraction_fix1.py::test_fresh_cache_artifact_refused_at_cli_import'),
    ('extraction_partial_methodology', 'ara/runtime/export.py', "for p in outcomes if p['status'] == 'partial'", "for p in outcomes if p['status'] == 'extracted'", 'tests/runtime/test_extraction_fix1.py::test_sparse_image_pages_are_partial[P]'),
    ('rich_id_unique', 'ara/runtime/calls.py', "require(len(ids) == len(set(ids)), 'duplicate extraction id')", "require(True, 'duplicate extraction id')", 'tests/runtime/test_extraction_rich.py::test_rich_graph_rejects_invalid_links[id]'),
    ('rich_endpoint', 'ara/runtime/calls.py', 'require(set(refs) <= available,', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_rich_graph_rejects_invalid_links[endpoint]'),
    ('rich_inference_origin', 'ara/runtime/calls.py', "item.inference_origin in ('paper_stated', 'reconstructed')", 'True', 'tests/runtime/test_extraction_rich.py::test_rich_graph_rejects_invalid_links[origin]'),
    ('rich_coverage', 'ara/runtime/calls.py', "require(data['coverage_complete'] or (allow_incomplete and incomplete),", 'require(True,', 'tests/runtime/test_extraction_rich.py::test_rich_graph_rejects_invalid_links[coverage]'),
    ('rich_no_summary_cap', 'schemas/extract_paper.json', '"text": {\n            "type": "string",', '"text": {\n            "maxLength": 400,\n            "type": "string",', 'tests/runtime/test_extraction_rich.py::test_no_compact_summary_limit'),
    ('rich_range_reconciliation', 'ara/runtime/reconciliation.py', 'if len(ranges) == 1 and not obligations:', 'if not obligations:', 'tests/runtime/test_extraction_rich.py::test_page_ranges_and_logged_reconciliation'),
    ('strict_partial', 'ara/runtime/extraction.py', "if paper.affected_pages and missing == 'refuse':", 'if False:', 'tests/runtime/test_extraction_rich.py::test_strict_partial_cli'),
    ('rich_inventory', 'ara/runtime/construction.py', 'require(not set(roots) & excluded and set(roots) | excluded == set(window_items),', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[inventory]'),
    ('rich_dependency_closure', 'ara/runtime/construction.py', 'require(all(dependencies[id] <= selected_ids for id in selected_ids),', 'require(True,', 'tests/runtime/test_extraction_round3.py::test_fixed_inventory_boundary_has_no_freeze[closure]'),
    ('rich_attribution', 'ara/runtime/construction.py', 'require(c.text == definitions[c.id],', 'require(True,', 'tests/runtime/test_extraction_round3.py::test_fixed_inventory_boundary_has_no_freeze[attribution]'),
    ('rich_symbol_unique', 'ara/runtime/construction.py', 'require(len(set(names)) == len(names),', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[duplicate_symbol]'),
    ('rich_symbol_signature', 'ara/runtime/construction.py', "require(catalog[name]['kind'] == kind and catalog[name]['arity'] == arity,", 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[symbol_arity]'),
    ('rich_symbol_alignment', 'ara/runtime/construction.py', 'require(valid_alignments,', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[binding]'),
    ('rich_omission_reason', 'ara/runtime/construction.py', "require(all(g['reason'].strip() for g in data['omissions']),", 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[omission_reason]'),
    ('rich_working_allowance', 'ara/runtime/construction.py', "require(cumulative.initial_input_tokens <= metadata['working_t_token_budget'],", 'require(True,', 'tests/runtime/test_extraction_rich.py::test_counted_capacity_refuses_explicitly[working]'),
    ('rich_downstream_admission', 'ara/runtime/calls.py', 'if admission and not fits:', "if admission and not fits and kind != 'propose_targets':", 'tests/runtime/test_extraction_rich.py::test_counted_capacity_refuses_explicitly[downstream]'),
    ('rich_stable_merge', 'ara/runtime/construction.py', 'tuple(sorted(items, key=lambda c: c.id))', 'tuple(items)', 'tests/runtime/test_extraction_rich.py::test_merge_order_cache_replay_and_contradictions'),
    ('rich_merge_citations', 'ara/runtime/construction.py', 'require(len({c.citation for c in items}) == len(items),', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_merge_order_cache_replay_and_contradictions'),
    ('rich_plan_identity', 'ara/runtime/construction.py', 'plan_id = digest(canonical(plan))', "plan_id = 'P'", 'tests/runtime/test_extraction_rich.py::test_plan_identity_and_source_order'),
    ('rich_single_freeze', 'ara/runtime/orchestration.py', "if any(e['stage'] == 'commitments_frozen' for e in calls.log.read()):", 'if False:', 'tests/runtime/test_extraction_rich.py::test_freeze_is_unique_and_immutable'),
    ('rich_encoding_warning', 'ara/runtime/extraction.py', "diagnostics.append(PageDiagnostic(i, 'private_use_glyphs', chars))", 'pass', 'tests/runtime/test_extraction_rich.py::test_encoding_warning_retains_text_and_rejects_strict'),
    ('rich_legacy_refusal', 'ara/runtime/extraction.py', "if text.startswith('# ARA extracted literature') and not text.startswith(HEADER):", 'if False:', 'tests/runtime/test_extraction_rich.py::test_legacy_artifact_not_treated_as_human'),
]
CASES += [
    ('rich_output_exhaustion', 'ara/runtime/calls.py', "('provider stop: max_tokens', 'extraction coverage incomplete')", "('extraction coverage incomplete',)", 'tests/runtime/test_extraction_rich.py::test_output_exhaustion_splits_without_truncation'),
    ('rich_final_working_budget', 'ara/runtime/construction.py', "if measured.initial_input_tokens > metadata['working_t_token_budget']:", 'if False:', 'tests/runtime/test_extraction_rich.py::test_construction_final_capacity_guard[final_budget]'),
    ('rich_symbol_budget', 'ara/runtime/construction.py', 'require(with_catalog.initial_input_tokens - without.initial_input_tokens <= symbol_budget,', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_construction_final_capacity_guard[symbols]'),
    ('rich_cached_context', 'ara/runtime/calls.py', 'estimate = self.count_request(kind, inputs, maximum=maximum, admission=True)', 'estimate = self.count_request(kind, inputs, maximum=maximum, admission=not cached)', 'tests/runtime/test_extraction_rich.py::test_cached_context_is_recounted'),
]

CASES.append(('rich_nullable_provider_schema', 'schemas/extract_paper.json', '"type": "string",\n                "enum": [\n                  "paper_stated"', '"type": ["string", "null"],\n                "enum": [\n                  "paper_stated"', 'tests/runtime/test_provider.py::test_rich_nullable_enum_matches_provider_grammar'))

CASES += [('batch_wire_grammar', 'ara/runtime/providers.py', "encoded_formulas=kind == 'build_t_batch'", 'encoded_formulas=False', 'tests/runtime/test_provider.py::test_batch_formula_wire_avoids_grammar_expansion'), ('batch_wire_decode', 'ara/runtime/calls.py', "item['formula'] = decode_response(item['formula'])", 'pass', 'tests/runtime/test_extraction_rich.py::test_encoded_batch_formula_still_requires_local_validation[True]'), ('batch_wire_invalid_json', 'ara/runtime/calls.py', "raise Rejected('invalid encoded formula JSON') from exc", 'raise', 'tests/runtime/test_extraction_rich.py::test_encoded_batch_formula_still_requires_local_validation[False]')]

CASES.append(('batch_bound_variables', 'ara/runtime/construction.py', "require(term.kind != 'variable' or term.name in bound,", 'require(True,', 'tests/runtime/test_extraction_rich.py::test_batch_variables_cannot_bypass_symbol_contract[False]'))

CASES += [
    ('directional_shared_branch', 'ara/runtime/construction.py', "deps[item['conclusion_id']].add(id)", "deps[item['conclusion_id']].add(id)\n            for premise in item['premise_ids']: deps[premise].add(id)", 'tests/runtime/test_extraction_round3.py::test_directional_closure_shared_premise_and_qualifier'),
    ('directional_shared_qualifier', 'ara/runtime/construction.py', 'deps[target].add(id)', 'deps[target].add(id); deps[id].add(target)', 'tests/runtime/test_extraction_round3.py::test_directional_closure_shared_premise_and_qualifier'),
    ('reconciliation_obligation_inventory', 'ara/runtime/calls.py', "set(resolved_ids) | set(pending_ids) == {o['id'] for o in obligations}", 'True', 'tests/runtime/test_extraction_round3.py::test_unresolved_obligations_require_evidence[False]'),
    ('reconciliation_source_pages', 'ara/runtime/reconciliation.py', '[asdict(p) for p in paper.readable_pages]', '[]', 'tests/runtime/test_extraction_round3.py::test_unresolved_obligations_require_evidence[True]'),
    ('measured_before_validation', 'ara/runtime/calls.py', "self.log.record('response_received', kind=kind, cache_key=key,", "self.log.record('unrecorded_response', kind=kind, cache_key=key,", 'tests/runtime/test_extraction_round3.py::test_measured_response_survives_followup_count_failure'),
    ('measured_count_failure', 'ara/runtime/calls.py', "self._event(kind, prompt, raw, usage, cost, start, cached, 'incomplete'", "self._event(kind, prompt, None, estimate, self.budget.cost(estimate), start, cached, 'incomplete'", 'tests/runtime/test_extraction_round3.py::test_build_count_failure_preserves_measured_raw_receipt'),
    ('extraction_stage_model', 'ara/runtime/providers.py', "return stage_settings(self.config, kind)['model']", "return self.model", 'tests/runtime/test_extraction_round3.py::test_stage_model_wire_cache_and_receipts'),
    ('extraction_stage_cache', 'ara/runtime/calls.py', 'identity, self.requested_model(kind), schema or {}', 'identity, self.provider.model, schema or {}', 'tests/runtime/test_extraction_round3.py::test_stage_model_wire_cache_and_receipts'),
    ('accounting_split', 'ara/runtime/export.py', "'measured_usage': raw_totals(measured)", "'measured_usage': raw_totals(selected)", 'tests/runtime/test_extraction_round3.py::test_accounting_separates_reservations'),
    ('node_wire_shape', 'ara/runtime/providers.py', "if original.get('title') == 'extract_paper_v2':", 'if False:', 'tests/runtime/test_extraction_round3.py::test_extraction_wire_has_unambiguous_nodes'),
    ('fixed_formalization_inventory', 'ara/runtime/construction.py', "require(len(set(ids)) == len(ids) and set(ids) == selected_ids,", 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[qualification]'),
]

CASES += [
    ('stage_reservation_price', 'ara/runtime/calls.py', 'self.budget.reserve(estimate, kind, model=self.requested_model(kind), subscription=self._subscription())', 'self.budget.reserve(estimate, kind, subscription=self._subscription())', 'tests/runtime/test_extraction_round3.py::test_stage_model_wire_cache_and_receipts'),
    ('known_terminal_log_failure', 'ara/runtime/calls.py', 'if receipt:', 'if False:', 'tests/runtime/test_extraction_round3.py::test_known_usage_survives_parsing_or_terminal_log_failure[logging]'),
]

CASES.append(('reconciliation_resolution_evidence', 'ara/runtime/calls.py', "require(all(r['evidence_ids'] and set(r['evidence_ids']) <= available for r in resolutions),", 'require(True,', 'tests/runtime/test_extraction_round3.py::test_unresolved_obligations_require_evidence[unknown]'))

CASES += [
    ('kind_relation_wire', 'ara/runtime/providers.py', "edge_fields - set(fields)", "edge_fields - set(fields) - {'applies_to'}", 'tests/runtime/test_extraction_round3.py::test_extraction_wire_has_unambiguous_nodes'),
    ('extraction_grammar_size', 'ara/runtime/providers.py', 'branches.append(branch)', 'branches.extend([branch] * 4)', 'tests/runtime/test_extraction_round3b.py::test_extraction_grammar_size'),
    ('zero_inference_disclosure', 'ara/runtime/calls.py', "if self.config.get('extraction_require_inference', False) and not any(i.kind == 'inference' for i in items):", 'if False:', 'tests/runtime/test_extraction_round3b.py::test_zero_inference_disclosed_without_correction'),
    ('targeted_inventory_retained', 'ara/runtime/calls.py', "[updates.pop(id, item) for id, item in old.items() if id not in ids]", '[]', 'tests/runtime/test_extraction_round3b.py::test_targeted_correction_preserves_inventory_and_is_bounded[valid-inferences]'),
    ('targeted_unchanged_allowed', 'ara/runtime/calls.py', "old, updates = inventory(candidate), inventory(patch)", "old, updates = inventory(candidate), inventory(patch)\n    require(all(item != old.get(item['id']) for item in patch['items']), 'unchanged')", 'tests/runtime/test_extraction_round3b.py::test_targeted_correction_preserves_inventory_and_is_bounded[unchanged-inferences]'),
    ('targeted_per_response_recovery', 'ara/runtime/calls.py', '                if correction == corrections:', "                if correction == corrections or any(e['stage'] == 'extraction_targeted_correction' for e in self.log.read()):", 'tests/runtime/test_context_request_fix.py::test_second_range_gets_correction_after_first_used_one'),
    ('qualification_local_guard', 'ara/runtime/calls.py', "require(not item.applies_to or item.kind in ('distinction', 'qualification'),", 'require(True,', 'tests/runtime/test_extraction_round3b.py::test_targeted_correction_preserves_inventory_and_is_bounded[valid-relation]'),
]

CASES += [
    ('root_stage_allowance', 'config.yaml', 'select_t_roots_max_output_tokens: 16384', 'select_t_roots_max_output_tokens: 8192', 'tests/runtime/test_root_selection.py::test_root_allowance_is_counted_before_dispatch_and_cache'),
    ('root_stage_reservation', 'config.yaml', 'select_t_roots_max_output_tokens: 16384', 'select_t_roots_max_output_tokens: 8192', 'tests/runtime/test_root_selection.py::test_root_reservation_uses_own_output_allowance'),
    ('root_complete_groups', 'ara/runtime/construction.py', 'require(not set(roots) & excluded and set(roots) | excluded == set(window_items),', 'require(True,', 'tests/runtime/test_root_selection.py::test_bad_selection_never_freezes[missing_group]'),
    ('root_group_identity', 'ara/runtime/construction.py', 'set(omitted_groups) <= set(groups_by_id)', 'True', 'tests/runtime/test_root_selection.py::test_bad_selection_never_freezes[unknown_group]'),
    ('root_group_expansion', 'ara/runtime/construction.py', "if id not in short_roots]", 'if True]', 'tests/runtime/test_root_selection.py::test_group_omission_excludes_selected_member'),
    ('root_compact_groups', 'ara/runtime/construction.py', "key = tuple(items[id][field] for field in fields)", "key = tuple(items[id][field] for field in fields) + (id,)", 'tests/runtime/test_root_selection.py::test_grouped_omissions_bound_response_without_losing_items'),
    ('construction_patch_retention', 'ara/runtime/construction.py', 'list({**baseline[field], **updates}.values())', 'list(updates.values())', 'tests/runtime/test_root_selection.py::test_targeted_stage_correction_preserves_inventory[valid-build_t_batch]'),
    ('construction_patch_unchanged', 'ara/runtime/construction.py', 'require(all(item != baseline[field].get(id) for id, item in updates.items()),', 'require(True,', 'tests/runtime/test_root_selection.py::test_targeted_stage_correction_preserves_inventory[unchanged-build_t_batch]'),
]

CASES += [
    ('full_profile_caps', 'ara/runtime/cli.py', 'if missing_caps:', 'if False:', 'tests/runtime/test_extraction_round4.py::test_full_profile_refuses_unset_caps_before_provider'),
    ('empty_range_disposition', 'ara/runtime/calls.py', "bool(data.get('empty_reason', '').strip())", 'True', 'tests/runtime/test_extraction_round4.py::test_empty_range_requires_disposition_and_preserves_aggregate[ ]'),
    ('empty_root_accounting', 'ara/runtime/construction.py', "require(bool(merged.commitments),", 'require(True,', 'tests/runtime/test_extraction_round4.py::test_zero_roots_accounted_without_formalization'),
    ('closure_preflight', 'ara/runtime/construction.py', "require(projected.initial_input_tokens <= metadata['working_t_token_budget'],", 'require(True,', 'tests/runtime/test_extraction_round4.py::test_closure_preflight_before_formalization'),
    ('window_inventory', 'ara/runtime/windows.py', 'values[:middle]', 'values[1:middle]', 'tests/runtime/test_evidence_windows.py::test_large_single_graph_windows_close_against_full_evidence'),
    ('full_graph_closure', 'ara/runtime/construction.py', "prerequisite_closure(items, selection['roots'])", "prerequisite_closure(window_items, selection['roots'])", 'tests/runtime/test_evidence_windows.py::test_large_single_graph_windows_close_against_full_evidence'),
    ('closure_size_admission', 'ara/runtime/construction.py', 'if closure_count.initial_input_tokens > input_bound:', 'if False:', 'tests/runtime/test_evidence_windows.py::test_oversized_selected_closure_refuses_before_formalization'),
    ('review_context_validation', 'ara/runtime/reconciliation.py', "require(set(request['pages']) <= set(inputs['evidence_page_ids']),", 'require(True,', 'tests/runtime/test_context_request_fix.py::test_obligation_request_errors_correct_before_acceptance[bad_request1]'),
    ('bounded_graph_review', 'ara/runtime/reconciliation.py', "        calls.count_request('extract_paper', inputs, admission=True)", '        pass', 'tests/runtime/test_evidence_windows.py::test_no_obligation_review_bounds_large_graph_union'),
]

CASES += [
    ('output_density_plan', 'ara/runtime/extraction.py', 'if density * len(pages) > maximum:', 'if False:', 'tests/runtime/test_extraction_plan.py::test_planned_ranges_use_output_density_and_keep_every_page'),
]

CASES += [
    ('resolved_pending_status', 'ara/runtime/calls.py', "require(not data['coverage_complete'] or not incomplete,", 'require(True,', 'tests/runtime/test_evidence_windows.py::test_resolved_ledger_cannot_hide_remaining_reference'),
]

CASES += [
    ('catalogue_preflight', 'ara/runtime/construction.py', "require(catalog_tokens + growth <= symbol_budget,", 'require(True,', 'tests/runtime/test_extraction_round4.py::test_catalogue_growth_preflight_precedes_formalization'),
]

CASES += [
    ('prior_closure_context', 'ara/runtime/construction.py', "'supporting_evidence': [items[id] for id in closure['already_formalized']]", "'supporting_evidence': []", 'tests/runtime/test_evidence_windows.py::test_overlapping_closures_include_prior_formulas_and_source_evidence'),
]

CASES += [
    ('native_full_profile', 'ara/runtime/cli.py', "profile.add_argument('--profile', choices=('pilot', 'extraction-full'))", "profile.add_argument('--profile', choices=('pilot',))", 'tests/runtime/test_extraction_round4.py::test_full_profile_reaches_native_construction'),
]

CASES += [
    ('root_measured_remaining_capacity', 'ara/runtime/construction.py', 'inputs_for(group, batch.index, max(0, available))', 'inputs_for(group, batch.index, batch.allowance)', 'tests/runtime/test_extraction_round4.py::test_two_rich_catalogues_share_global_capacity'),
]

CASES += [
    ('new_gap_inventory', 'ara/runtime/reconciliation.py', "inputs['evidence_page_ids'], gaps)", "inputs['evidence_page_ids'], [])", 'tests/runtime/test_extraction_round5.py::test_new_gap_survives_original_resolution[False-R]'),
    ('review_resolution_retained', 'ara/runtime/reconciliation.py', 'resolutions.extend(json.loads(result.resolutions_json))', 'pass', 'tests/runtime/test_extraction_round5.py::test_new_gap_survives_original_resolution[True-R]'),
]

CASES += [
    ('paper_continuation_cap', 'ara/runtime/extraction_budget.py',
     'if self.attempts > self.continuation_limit:', 'if False:',
     'tests/runtime/test_extraction_round6.py::test_descendant_chain_stops_at_paper_count_with_budget_remaining'),
    ('paper_reservation_cap', 'ara/runtime/extraction_budget.py',
     'if self.spent + reserve > self.cost_cap:', 'if False:',
     'tests/runtime/test_extraction_round6.py::test_paper_dollars_reserve_before_dispatch'),
    ('paper_actual_cap', 'ara/runtime/extraction_budget.py',
     'if self.spent > self.cost_cap:', 'if False:',
     'tests/runtime/test_extraction_round6.py::test_paper_actual_cost_overrun_keeps_measured_response'),
    ('paper_count_finite', 'ara/runtime/extraction_budget.py',
     'if type(value) is not int or value < 0:', 'if False:',
     'tests/runtime/test_extraction_round6.py::test_invalid_paper_limits_refuse_before_dispatch[extraction_paper_continuation_limit-inf]'),
    ('paper_dollars_finite', 'ara/runtime/extraction_budget.py',
     'if not result.is_finite() or result < 0:', 'if False:',
     'tests/runtime/test_extraction_round6.py::test_invalid_paper_limits_refuse_before_dispatch[extraction_paper_cost_cap_usd-inf]'),
    ('paper_boundary_cost', 'ara/runtime/extraction_budget.py',
     'self.start_cost = calls.budget.used_cost', 'self.start_cost = Decimal(0)',
     'tests/runtime/test_extraction_round6.py::test_multi_paper_allowances_reset_at_paper_boundary'),
]

CASES += [
    ('mode_specific_context_wire', 'ara/runtime/calls.py',
     "            if not reconciliation or not inputs.get('obligations'):", '            if False:',
     'tests/runtime/test_context_request_fix.py::test_mode_contract_reaches_counter_prompt_and_wire'),
    ('context_validation_before_acceptance', 'ara/runtime/reconciliation.py', "require(set(request['evidence_ids']) <= {i.id for i in items},", 'require(True,', 'tests/runtime/test_context_request_fix.py::test_obligation_request_errors_correct_before_acceptance[bad_request2]'),
    ('correction_paper_limit', 'ara/runtime/extraction_budget.py', 'if self.attempts > self.continuation_limit:', 'if False:', 'tests/runtime/test_context_request_fix.py::test_correction_still_obeys_paper_allowance'),
    ('single_review_no_corrections', 'ara/runtime/calls.py', '        if single_pass:', '        if False:', 'tests/runtime/test_range_union.py::test_failed_review_preserves_ranges_and_discloses_gap'),
    ('context_empty_recovery', 'ara/runtime/calls.py', "require(bool(request['pages'] or request['evidence_ids']), 'unresolved obligation empty context request')", 'pass', 'tests/runtime/test_context_request_fix.py::test_obligation_request_errors_correct_before_acceptance[bad_request0]'),
    ('terminal_paper_policy', 'ara/runtime/extraction.py', '                stopped = exc', '                stopped = None', 'tests/runtime/test_context_request_fix.py::test_terminal_failure_stops_corpus_and_pilot_import'),
]

CASES += [
    ('paper_failure_continue', 'ara/runtime/extraction.py',
     'if not paper_failure or failures > maximum_failures:', 'if True:',
     'tests/runtime/test_paper_recovery.py::test_failed_paper_disclosed_and_excluded_from_construction'),
    ('paper_failure_threshold', 'ara/runtime/extraction.py',
     'failures > maximum_failures', 'False',
     'tests/runtime/test_paper_recovery.py::test_failure_threshold_stops_only_after_exceeded'),
    ('paper_failure_boundary', 'ara/runtime/extraction.py',
     'failures > maximum_failures', 'failures >= maximum_failures',
     'tests/runtime/test_paper_recovery.py::test_exact_failure_threshold_completes'),
    ('failed_evidence_exclusion', 'ara/runtime/construction.py',
     "require(all(not p['items'] for p in papers if p['status'] == 'failed'),", 'require(True,',
     'tests/runtime/test_paper_recovery.py::test_failed_status_cannot_supply_items_even_without_provenance'),
    ('completed_empty_paper_reuse', 'ara/runtime/extraction.py',
     "if source not in selected or outcome['status'] not in ('extracted', 'partial'):",
     "if source not in selected or outcome['status'] not in ('extracted', 'partial') or not outcome['items']:",
     'tests/runtime/test_paper_recovery.py::test_completed_empty_disposition_is_reused'),
    ('completed_paper_reuse', 'ara/runtime/extraction.py', "if paper.source_id in reused and 'outcome' in reused[paper.source_id]:", 'if False:', 'tests/runtime/test_paper_recovery.py::test_resume_reuses_completed_papers_and_retries_failed[False]'),
    ('resume_input_binding', 'ara/runtime/extraction.py',
     "if outcome.get('input_sha256', digest(canonical(paper.inputs()))) != digest(canonical(paper.inputs())):", 'if False:',
     'tests/runtime/test_paper_recovery.py::test_changed_source_is_extracted_again[input]'),
    ('resume_transitive_validation', 'ara/runtime/provenance.py',
     'verify_imports(events, active | {key}, memo, inputs=inputs)', 'pass',
     'tests/runtime/test_paper_recovery.py::test_resume_origin_tamper_is_detected_transitively'),
    ('resume_receipt_dedup', 'ara/runtime/provenance.py',
     'if identity not in seen:', 'if True:',
     'tests/runtime/test_paper_recovery.py::test_transitive_overlapping_import_does_not_double_charge'),
    ('resume_inherited_cost', 'ara/runtime/extraction.py',
     'import_provenance(log, events, origin)', 'pass',
     'tests/runtime/test_paper_recovery.py::test_inherited_cost_prevents_new_dispatch'),
    ('resume_paper_allowance_reset', 'ara/runtime/extraction_budget.py',
     'events = batch_events(calls.log.read())', 'events = calls.log.read()',
     'tests/runtime/test_paper_recovery.py::test_resume_reuses_completed_papers_and_retries_failed[False]'),
    ('resume_origin_checkpoint', 'ara/runtime/provenance.py',
     "if anchor.read_text().splitlines() != [r['hash'] for r in records]:", 'if False:',
     'tests/runtime/test_paper_recovery.py::test_fresh_origin_checkpoint_refuses_truncated_log'),
    ('resume_cli_wiring', 'ara/runtime/cli.py',
     'reused = resume_papers(log, papers, args.resume_from, config, ROOT, revalidate_only=args.salvage_only) if args.resume_from and not args.estimate_only else {}', 'reused = {}',
     'tests/runtime/test_paper_recovery.py::test_native_cli_resume_and_pilot_import'),
]

CASES += [
    ('resume_acceptance_policy', 'ara/runtime/extraction.py', 'if not acceptance or (previous != acceptance and not compatible_v4 and not compatible_v5):', 'if False:', 'tests/runtime/test_resume_policy.py::test_changed_acceptance_matches_fresh_extraction'),
    ('resume_acceptance_model', 'ara/runtime/extraction.py',
     "'stage': {'model': stage['model'], 'effort': stage['effort'],", "'stage': {'model': None, 'effort': stage['effort'],",
     'tests/runtime/test_resume_policy.py::test_acceptance_contract_drift_reextracts[model]'),
    ('resume_acceptance_version', 'ara/runtime/extraction.py',
     "'version': EXTRACTION_ACCEPTANCE_VERSION,", "'version': None,",
     'tests/runtime/test_resume_policy.py::test_acceptance_contract_drift_reextracts[version]'),
    ('resume_ancestor_inventory', 'ara/runtime/extraction.py',
     'for outcome in historical_extraction_outcomes(events):', 'for outcome in extraction_outcomes(events):',
     'tests/runtime/test_resume_policy.py::test_stopped_descendant_reuses_unreached_ancestor_success'),
    ('resume_ancestor_union', 'ara/runtime/extraction.py',
     "outcome = unite(entries, acceptance) if len(entries) > 1 else first['outcome']", "outcome = first['outcome']",
     'tests/runtime/test_resume_policy.py::test_conflicting_compatible_ancestor_successes_union'),
    ('resume_execution_policy', 'ara/runtime/extraction.py',
     '            validate_reused_paper(paper, outcome, acceptance)\n            calls.log.record', '            calls.log.record',
     'tests/runtime/test_resume_policy.py::test_execution_rechecks_reuse_policy'),
]

CASES += [
    ('resume_strict_coverage', 'ara/runtime/extraction.py',
     "if paper.affected_pages and missing == 'refuse':", 'if False:',
     'tests/runtime/test_resume_policy.py::test_strict_coverage_refuses_reused_partial_paper'),
]

CASES += [
    ('expanded_extraction_schema_count', 'ara/runtime/providers.py',
     "request['output_config']['format']['schema'] if kind == 'extract_paper' else (schema or {})", 'schema or {}',
     'tests/runtime/test_extraction_acceptance.py::test_extraction_counter_includes_expanded_provider_envelope'),
    ('typed_extraction_envelope_wire', 'ara/runtime/providers.py',
     "if original.get('oneOf'):", 'if False:',
     'tests/runtime/test_extraction_acceptance.py::test_initial_wire_satisfies_provider_sdk_schema_contract'),
    ('empty_optional_normalization', 'ara/runtime/calls.py',
     "if 'empty_reason' in data and data['empty_reason'] in ('', None):", 'if False:',
     'tests/runtime/test_extraction_acceptance.py::test_empty_optional_normalization_is_logged_without_content_change'),
    ('correction_second_attempt', 'ara/runtime/calls.py',
     'for correction in range(corrections + 1):', 'for correction in range(min(corrections, 1) + 1):',
     'tests/runtime/test_extraction_acceptance.py::test_two_patches_keep_all_items_and_specific_page_feedback'),
    ('correction_accumulated_inventory', 'ara/runtime/calls.py',
     'candidate = merge_extraction_patch(candidate or rejected, rejected)', 'candidate = rejected',
     'tests/runtime/test_extraction_acceptance.py::test_two_patches_keep_all_items_and_specific_page_feedback'),
    ('disposition_wire_separation', 'ara/runtime/calls.py',
     "schema['oneOf'] = [", "schema['ignored_alternatives'] = [",
     'tests/runtime/test_extraction_acceptance.py::test_provider_wire_cannot_mix_disposition_and_content'),
]

CASES += [
    ('standalone_envelope_alternatives', 'ara/runtime/providers.py',
     "original = {'oneOf': envelopes}", "original['oneOf'] = envelopes",
     'tests/runtime/test_extraction_acceptance.py::test_initial_wire_satisfies_provider_sdk_schema_contract'),
    ('null_inventory_normalization', 'ara/runtime/calls.py',
     "if 'items' in data and data['items'] is None:", 'if False:',
     'tests/runtime/test_extraction_acceptance.py::test_null_empty_inventory_normalized_with_original_preserved'),
    ('unknown_reconciliation_policy', 'ara/runtime/budget.py',
     "config.get('unknown_usage_policy', 'refuse') != 'count-at-reservation'", 'True',
     'tests/runtime/test_schema_preflight.py::test_explicit_unknown_reconciliation'),
    ('reconciled_reservation_charge', 'ara/runtime/budget.py',
     "self.used_cost = sum((Decimal(str(e['cost_usd'])) for e in log.read()), Decimal(0))",
     'self.used_cost = Decimal(0)',
     'tests/runtime/test_schema_preflight.py::test_explicit_unknown_reconciliation'),
    ('provider_error_receipt', 'ara/runtime/calls.py',
     "self.log.record('provider_error', kind=kind, **provider_error_evidence(exc, prompt))", 'pass',
     'tests/runtime/test_schema_preflight.py::test_provider_error_evidence_sanitized'),
    ('schema_gate_inventory', 'ara/runtime/preflight.py',
     'for identity, inputs, _ in wires:', 'for identity, inputs, _ in wires[:1]:',
     'tests/runtime/test_schema_preflight.py::test_schema_gate_native_wires_and_cost'),
]

CASES += [
    ('diagnostic_suppression', 'ara/runtime/providers.py',
     "message = 'Provider diagnostic suppressed.'", "message = error.get('message')",
     'tests/runtime/test_schema_preflight.py::test_provider_diagnostic_suppresses_unrecognized_text'),
    ('diagnostic_status_validation', 'ara/runtime/providers.py',
     'type(status) is int and 400 <= status <= 599', 'True',
     'tests/runtime/test_schema_preflight.py::test_provider_diagnostic_validates_metadata'),
    ('diagnostic_type_validation', 'ara/runtime/providers.py',
     'isinstance(error_type, str) and error_type in allowed_types', 'True',
     'tests/runtime/test_schema_preflight.py::test_provider_diagnostic_validates_metadata'),
    ('diagnostic_request_id_validation', 'ara/runtime/providers.py',
     "re.fullmatch(r'req_[A-Za-z0-9]{1,128}', request_id)", 'True',
     'tests/runtime/test_schema_preflight.py::test_provider_diagnostic_validates_metadata'),
    ('diagnostic_schema_recognition', 'ara/runtime/providers.py',
     'if match:', 'if False:',
     'tests/runtime/test_schema_preflight.py::test_provider_diagnostic_retains_recognized_schema_compiler_error'),
    ('diagnostic_cli_counter_boundary', 'ara/runtime/cli.py',
     'evidence = provider_error_evidence(exc)', "evidence = {'message': str(exc)}",
     'tests/runtime/test_schema_preflight.py::test_cli_token_counter_suppresses_request_echo'),
    ('diagnostic_compiler_keywords', 'ara/runtime/providers.py',
     'all(k in allowed_keywords for k in keywords)', 'True',
     'tests/runtime/test_schema_preflight.py::test_provider_diagnostic_suppresses_unrecognized_text'),
    ('diagnostic_compiler_full_sentence', 'ara/runtime/providers.py',
     'match = re.fullmatch(', 'match = re.match(',
     'tests/runtime/test_schema_preflight.py::test_provider_diagnostic_suppresses_unrecognized_text'),
    ('rejected_candidate_normalization', 'ara/runtime/calls.py',
     'changes = normalize_extraction(rejected)', 'changes = []',
     'tests/runtime/test_extraction_acceptance.py::test_rejected_null_inventory_recovers_within_correction_limit'),
]

CASES += [
    ('v5_reversed_pages', 'ara/runtime/calls.py',
     "if type(start) is int and type(end) is int and start > end:", 'if False:',
     'tests/runtime/test_extraction_v5.py::test_reversed_pages_repaired_logged_and_out_of_bounds_refused'),
    ('v5_duplicate_patch', 'ara/runtime/calls.py',
     "changes += normalize_patch_ids(data, inputs['candidate'])", 'pass',
     'tests/runtime/test_extraction_v5.py::test_duplicate_patch_retains_items_and_references'),
    ('v5_third_correction', 'ara/runtime/calls.py',
     'for correction in range(corrections + 1):', 'for correction in range(min(corrections, 2) + 1):',
     'tests/runtime/test_extraction_v5.py::test_third_correction_preserves_inventory'),
    ('v5_reuse_revalidation', 'ara/runtime/extraction.py',
     '        revalidate_v4_graph(paper, outcome, acceptance)', '        pass',
     'tests/runtime/test_extraction_v5.py::test_v4_graph_revalidated_offline[page]'),
    ('v5_disposition_required', 'ara/runtime/calls.py', "require(bool(data['no_inference_reason'].strip()),", 'require(True,', 'tests/runtime/test_extraction_v5.py::test_no_inference_requires_explicit_disposition'),
]

CASES += [
    ('v5_duplicate_stability', 'ara/runtime/calls.py',
     'if fresh not in patch_ids and fresh in previous and previous[fresh] == normalized:', 'if False:',
     'tests/runtime/test_extraction_v5.py::test_duplicate_repair_is_stable_after_failed_patch'),
    ('v5_duplicate_ambiguity', 'ara/runtime/calls.py',
     'require(old not in referenced or item == first[old],', 'require(True,',
     'tests/runtime/test_extraction_v5.py::test_ambiguous_duplicate_reference_is_not_guessed'),
]

CASES += [
    ('union_later_range_failure_retained', 'ara/runtime/calls.py',
     'if not ranges:', 'if True:',
     'tests/runtime/test_range_union.py::test_offline_salvage_keeps_failed_paper_ranges_and_provenance'),
    ('union_items_retained', 'ara/runtime/reconciliation.py',
     'items = tuple(item for result in ranges for item in result.items)', 'items = ()',
     'tests/runtime/test_range_union.py::test_failed_review_preserves_ranges_and_discloses_gap'),
    ('union_salvage_avoids_redundant_retry', 'ara/runtime/calls.py',
     'if not is_thin(pages, supported):', 'if False:',
     'tests/runtime/test_range_union.py::test_accepted_review_fills_thin_range_before_paid_retry'),
    ('union_inference_conflict_disclosure', 'ara/runtime/calls.py',
     "if any(d.get('kind') == 'no_explicit_inferential_structure' and any(", 'if any(False and any(',
     'tests/runtime/test_range_union.py::test_refinement_discloses_conflicting_inference_disposition'),
    ('union_thin_retry_once', 'ara/runtime/calls.py',
     "if entry.get('refined'):", 'if False:',
     'tests/runtime/test_range_union.py::test_historical_thin_retry_is_not_repeated[interrupted]'),
    ('union_thin_retry', 'ara/runtime/salvage.py',
     'return len(pages) >= 8 and len(items) <= max(1, len(pages) // 10)', 'return False',
     'tests/runtime/test_range_union.py::test_thin_range_retried_once_without_dropping_original'),
    ('union_salvage_revalidation', 'ara/runtime/salvage.py',
     "if any(source_text.get(p['page']) != p['text'] for p in request.get('pages', [])):", 'if False:',
     'tests/runtime/test_range_union.py::test_salvage_source_mismatch_refuses_without_dispatch'),
    ('union_roster_disclosure', 'ara/runtime/extraction.py',
     "'publication_roster': publication_roster(outcomes)", "'publication_roster': []",
     'tests/runtime/test_range_union.py::test_native_exclusion_roster_is_disclosed'),
    ('union_open_gaps', 'ara/runtime/extraction.py',
     "entry['open_gaps'] = [o for o in outcome.get('obligations', [])", "entry['open_gaps'] = [o for o in []",
     'tests/runtime/test_range_union.py::test_failed_review_preserves_ranges_and_discloses_gap'),
]

CASES += [
    ('grounding_overlap', 'ara/runtime/grounding.py',
     "overlap < POLICY['minimum_overlap']", 'overlap < 0',
     'tests/runtime/test_grounding.py::test_junk_and_page_grounding'),
    ('grounding_receipt', 'ara/runtime/grounding.py',
     "if (grounding.get('policy') != POLICY or", "if False and (grounding.get('policy') != POLICY or",
     'tests/runtime/test_grounding.py::test_ungated_and_tampered_inventory_cannot_supply_citations'),
    ('grounding_construction_filter', 'ara/runtime/construction.py',
     "'items': evidence_items(p)", "'items': p['items']",
     'tests/runtime/test_grounding.py::test_publication_quarantine_propagates_and_excludes_t'),
    ('grounding_quarantine_filter', 'ara/runtime/grounding.py',
     "if item['id'] not in blocked", 'if True',
     'tests/runtime/test_grounding.py::test_publication_quarantine_propagates_and_excludes_t'),
    ('grounding_cascade', 'ara/runtime/grounding.py',
     'blocked = deps[id] & rejected', 'blocked = set()',
     'tests/runtime/test_grounding.py::test_publication_quarantine_propagates_and_excludes_t'),
    ('grounding_publication', 'ara/runtime/extraction.py',
     '        outcome = ground_outcome(paper, outcome, calls.log)\n        calls.log.record',
     '        calls.log.record',
     'tests/runtime/test_grounding.py::test_publication_quarantine_propagates_and_excludes_t'),
    ('grounding_reuse', 'ara/runtime/extraction.py',
     '            outcome = ground_outcome(paper, outcome, calls.log)', '            outcome = {k:v for k,v in outcome.items() if k not in ("grounding", "quarantined")}',
     'tests/runtime/test_grounding.py::test_v4_and_thin_history_revalidated_without_dispatch'),
    ('grounding_resolution', 'ara/runtime/extraction.py',
     "if not blocked.intersection(r['evidence_ids'])", 'if True',
     'tests/runtime/test_grounding.py::test_quarantined_resolution_reopens_gap'),
    ('rejected_candidate_discard', 'ara/runtime/calls.py',
     "if id not in ids]", 'if True]',
     'tests/runtime/test_grounding.py::test_correction_can_discard_unsupported_rejected_items'),
]

CASES += [
    ('offline_snapshot_retention', 'ara/runtime/snapshot_union.py',
     "for original in outcome['items']:", "for original in outcome['items'][:1]:",
     'tests/runtime/test_republication.py::test_offline_snapshot_replacement_preserves_accepted_inventory'),
    ('legacy_gap_publication', 'ara/runtime/extraction.py',
     "if outcome.get('range_union_policy') or outcome.get('publication_policy') == PUBLICATION_POLICY:",
     "if outcome.get('range_union_policy'):",
     'tests/runtime/test_republication.py::test_legacy_republication_reopens_gaps_and_resumes_again'),
    ('legacy_gap_methodology', 'ara/runtime/export.py',
     "for p in outcomes if p.get('range_union_policy') or p.get('publication_policy') == PUBLICATION_POLICY]",
     "for p in outcomes if p.get('range_union_policy')]",
     'tests/runtime/test_republication.py::test_legacy_republication_reopens_gaps_and_resumes_again'),
]


CASES += [
    ('report_anchor', 'ara/runtime/report.py',
     "if anchor.read_text().splitlines() != [r['hash'] for r in records]:", 'if False:',
     'tests/runtime/test_report.py::test_report_refuses_tampering_before_output[truncate]'),
    ('report_reservations', 'ara/runtime/report.py',
     "unknown = [e for e in events if payload(e).get('accounting') == 'reservation_unknown_actual']", 'unknown = []',
     'tests/runtime/test_report.py::test_report_native_readonly_accounting_and_citations'),
    ('report_deduplication', 'ara/runtime/report.py',
     'unique.setdefault(digest(canonical(event)), event)', 'unique[len(unique)] = event',
     'tests/runtime/test_report.py::test_imported_receipts_deduplicate_combined_accounting'),
    ('report_source_links', 'ara/runtime/report.py',
     "matches = [v for v in evidence.get(c['id'], []) if v.get('citation') == c['citation']]", 'matches = []',
     'tests/runtime/test_report.py::test_report_native_readonly_accounting_and_citations'),
    ('report_html_escape', 'ara/runtime/report_render.py',
     "return '<pre>' + escape(pretty(value)) + '</pre>'", "return '<pre>' + pretty(value) + '</pre>'",
     'tests/runtime/test_report.py::test_report_native_readonly_accounting_and_citations'),
    ('report_historical_roster', 'ara/runtime/report.py',
     'set(histories) | set(related) | requested_history | set(selected) | unattempted',
     'set(histories) | set(related) | set(selected) | unattempted',
     'tests/runtime/test_report.py::test_exclusion_roster_retains_selected_papers_without_any_outcome'),
    ('report_unfinalized_usage', 'ara/runtime/report.py',
     'received[id(pending[key][-1])] = data', 'pass',
     'tests/runtime/test_report.py::test_received_usage_survives_interruption_without_becoming_a_final_charge'),
    ('report_current_outcomes', 'ara/runtime/report.py',
     'current = events[start:]', 'current = events',
     'tests/runtime/test_report.py::test_historical_success_is_not_current_success_and_pending_is_visible'),
    ('search_trace_prunes', 'ara/engine/search.py',
     "trace('prune', state_id=state_id, node_id=node.id,\n                          proposal_index=proposal_index, reason=reason)", 'pass',
     'tests/engine/test_search_trace.py::test_trace_branches_rejections_and_completed_graphs'),
]

CASES += [
    ('report_available_origin', 'ara/runtime/report.py',
     "if digest(canonical(original)) != data['receipt_id'] or list(copied) != unique_events(original, seen):", 'if False:',
     'tests/runtime/test_report.py::test_missing_ancestor_does_not_hide_available_origin_mismatch'),
    ('report_explicit_actual', 'ara/runtime/report.py',
     "measured = [e for e in events if payload(e).get('accounting') == 'actual']",
     "measured = [e for e in events if payload(e).get('accounting') != 'reservation_unknown_actual']",
     'tests/runtime/test_report.py::test_unclassified_incomplete_receipts_are_not_measured'),
    ('trace_seal_hash', 'ara/runtime/report_traces.py',
     "if hashlib.sha256(raw).hexdigest() != receipt['sha256']:", 'if False:',
     'tests/engine/test_search_trace.py::test_sidecar_seal_is_required_and_checked_before_use'),
    ('trace_semantic_completeness', 'ara/runtime/report_traces.py',
     "trace['complete'] = not issues", "trace['complete'] = True",
     'tests/runtime/test_report.py::test_invalid_trace_is_partial_and_still_renders[empty]'),
    ('trace_formula_reference', 'ara/runtime/report_traces.py',
     "issue('unresolved ' + kind + ' reference')", 'pass',
     'tests/engine/test_search_trace.py::test_invalid_sealed_references_and_line_counts'),
    ('trace_line_count', 'ara/runtime/report_traces.py',
     "if len(lines) != receipt['line_count'] or any(not line.endswith(b'\\n') for line in lines):", 'if False:',
     'tests/engine/test_search_trace.py::test_invalid_sealed_references_and_line_counts'),
    ('trace_terminal_payload_interning', 'ara/engine/tracing.py',
     "data['graph'] = self.graph(data['graph'])", "data['graph'] = data['graph'].to_dict()",
     'tests/engine/test_search_trace.py::test_padded_cap_trace_stays_below_pilot_limit_and_preserves_every_route'),
    ('trace_all_state_rendering', 'ara/runtime/report_render.py',
     "write_json(destination / trace_file, trace)", "write_json(destination / trace_file, {**trace, 'states': trace['states'][:499]})",
     'tests/engine/test_search_trace.py::test_native_500_state_trace_full_report'),
    ('trace_selected_proposal_identity', 'ara/runtime/report_traces.py',
     "if node.get('proposal') != expand_proposal(candidate.get('proposal_id'), reference):", 'if False:',
     'tests/engine/test_search_trace.py::test_sealed_trace_semantics_are_checked_before_rendering'),
    ('trace_selected_child_ancestry', 'ara/runtime/report_traces.py',
     "if (child.get('parent_node_id') != state.get('node_id') or\n                            type(parent.get('depth')) is not int or child.get('depth') != parent['depth'] + 1):", 'if False:',
     'tests/engine/test_search_trace.py::test_sealed_trace_semantics_are_checked_before_rendering'),
    ('trace_alternative_disposition', 'ara/runtime/report_traces.py',
     'if any(dispositions[key] != 1 for key in proposals):', 'if False:',
     'tests/engine/test_search_trace.py::test_sealed_trace_semantics_are_checked_before_rendering'),
]


CASES += [
    ('snapshot_collision_namespace', 'ara/runtime/snapshot_union.py',
     "if i['id'] in qualified", 'if False',
     'tests/runtime/test_republication.py::test_offline_snapshot_replacement_preserves_accepted_inventory[conflicting]'),
    ('snapshot_incoming_qualifier', 'ara/runtime/snapshot_union.py',
     'dependencies[id].update(refs)', 'pass',
     'tests/runtime/test_republication.py::test_offline_snapshot_replacement_preserves_accepted_inventory[qualifier]'),
    ('snapshot_incoming_presence', 'ara/runtime/snapshot_union.py',
     'qualified.update(id for id, values in contexts.items() if len(values) > 1)', 'pass',
     'tests/runtime/test_republication.py::test_offline_snapshot_replacement_preserves_accepted_inventory[new_qualifier]'),
    ('snapshot_native_prerequisites', 'ara/runtime/snapshot_union.py',
     'evidence_dependencies(by_id).items()',
     '{id: references(item) for id, item in by_id.items()}.items()',
     'tests/runtime/test_republication.py::test_native_closure_retains_snapshot_context'),
    ('snapshot_reference_mapping', 'ara/runtime/snapshot_union.py',
     "item[field] = [mapping[id] for id in original[field]]", "item[field] = original[field]",
     'tests/runtime/test_republication.py::test_offline_snapshot_replacement_preserves_accepted_inventory[conflicting]'),
    ('snapshot_gap_scope', 'ara/runtime/snapshot_union.py',
     ':snapshot:{sid}:gap:', ':gap:',
     'tests/runtime/test_republication.py::test_union_keeps_gap_resolution_with_its_snapshot'),
    ('snapshot_derived_reconstruction', 'ara/runtime/extraction.py',
     'graph(rebuilt) != graph(outcome) or', 'False or',
     'tests/runtime/test_republication.py::test_union_keeps_gap_resolution_with_its_snapshot'),
    ('completed_thin_snapshot_reuse', 'ara/runtime/extraction.py',
     "            try:\n                validate_reused_paper(selected[source], outcome, acceptance)",
     "            if any(d.get('kind') == 'thin_range' for d in outcome.get('dispositions', [])):\n                continue\n            try:\n                validate_reused_paper(selected[source], outcome, acceptance)",
     'tests/runtime/test_range_union.py::test_historical_thin_retry_is_not_repeated[completed]'),
    ('reconciliation_overflow_continues', 'ara/runtime/reconciliation.py',
     '    except Exception as exc:', '    except Exception as exc:\n        raise',
     'tests/runtime/test_range_union.py::test_reconciliation_context_overflow_preserves_paper_and_continues'),
]


CASES += [
    ('construction_window_metadata', 'ara/runtime/construction.py',
     'evidence_window(p, selected)', "{**p, 'items': [i for i in p['items'] if i['id'] in selected]}",
     'tests/runtime/test_evidence_windows.py::test_windows_keep_only_selected_metadata'),
    ('construction_window_gap_scope', 'ara/runtime/construction.py',
     'if relevant(g)', 'if True',
     'tests/runtime/test_evidence_windows.py::test_windows_keep_only_selected_metadata'),
    ('receipt_bulk_import', 'ara/runtime/provenance.py',
     'log.emit_many([marker, *(RunEvent.from_dict(event) for event in copied)])',
     'for event in [marker, *(RunEvent.from_dict(event) for event in copied)]:\n        log.emit(event)',
     'tests/runtime/test_boundaries.py::test_receipt_import_verification_does_not_grow_per_event'),
    ('bulk_append_verifies_chain', 'ara/runtime/logging.py',
     'records = self._verify()', 'records = []',
     'tests/runtime/test_boundaries.py::test_bulk_log_append_refuses_tamper_and_interrupted_write'),
]


CASES += [
    ('bounded_symbol_measurement', 'ara/runtime/closure_budget.py',
     'MEASURED_SYMBOL_TOKENS = ceil(10471 / 45)', 'MEASURED_SYMBOL_TOKENS = 128',
     'tests/runtime/test_bounded_closure.py::test_global_budget_reserves_copy_symbols_and_headroom'),
    ('bounded_global_window_division', 'ara/runtime/closure_budget.py',
     'total // count', 'total',
     'tests/runtime/test_bounded_closure.py::test_global_budget_reserves_copy_symbols_and_headroom'),
    ('bounded_cut_qualification', 'ara/runtime/closure_budget.py',
     'mandatory[target].add(id)', 'pass',
     'tests/runtime/test_bounded_closure.py::test_depth_cut_retains_qualifiers_endpoints_and_omitted_support'),
    ('bounded_cut_omission_ids', 'ara/runtime/closure_budget.py',
     'return selected, omitted, depth', 'return selected, {}, depth',
     'tests/runtime/test_bounded_closure.py::test_depth_cut_retains_qualifiers_endpoints_and_omitted_support'),
    ('bounded_assumption_mark', 'ara/runtime/commitment_provenance.py',
     'omitted_support_ids=sorted(set(omitted_support_ids))', 'omitted_support_ids=[]',
     'tests/runtime/test_bounded_closure.py::test_native_cut_disclosed_in_frozen_text_receipt_and_methodology'),
    ('bounded_methodology', 'ara/runtime/export.py',
     "p.get('support_omitted', {}).items()", '{}.items()',
     'tests/runtime/test_bounded_closure.py::test_native_cut_disclosed_in_frozen_text_receipt_and_methodology'),
    ('soft_working_output', 'ara/runtime/construction.py',
     "require(cumulative.initial_input_tokens <= metadata['working_t_token_budget'],",
     "require(cumulative.initial_input_tokens - current.initial_input_tokens <= working_share,",
     'tests/runtime/test_bounded_closure.py::test_actual_output_borrows_within_global_limits[working]'),
    ('soft_symbol_output', 'ara/runtime/construction.py',
     "require(with_catalog.initial_input_tokens - without.initial_input_tokens <= symbol_budget,",
     "require(with_catalog.initial_input_tokens - without.initial_input_tokens - catalog_tokens <= symbol_share,",
     'tests/runtime/test_bounded_closure.py::test_actual_output_borrows_within_global_limits[symbols]'),
    ('bounded_exact_request_cut', 'ara/runtime/construction.py',
     "return calls.count_request('build_t_batch', {**trial, 'shared_symbols': []}).initial_input_tokens <= input_bound",
     'return True',
     'tests/runtime/test_bounded_closure.py::test_counted_formalization_bound_cuts_before_dispatch'),
    ('bounded_zero_window', 'ara/runtime/construction.py',
     'if not selected_ids:', 'if False:',
     'tests/runtime/test_bounded_closure.py::test_zero_root_window_can_precede_contributing_window'),
]



CASES += [
    ('soft_recompute', 'ara/runtime/construction.py',
     "windows_left = sum(n > 0 for n in allocation['window_initial_commitments'][batch.index:])", 'windows_left = len(batches)',
     'tests/runtime/test_construction_shares.py::test_borrowing_recounts_and_recomputes_before_next_dispatch'),
    ('soft_recount', 'ara/runtime/construction.py',
     "current = calls.count_request('propose_targets', {**target_inputs, 'commitments': {'commitments': prior}})",
     "current = calls.count_request('propose_targets', {**target_inputs, 'commitments': {'commitments': []}})",
     'tests/runtime/test_construction_shares.py::test_borrowing_recounts_and_recomputes_before_next_dispatch'),
    ('soft_window_skip', 'ara/runtime/construction.py',
     'refusal_reasons.append(str(exc))', 'raise',
     'tests/runtime/test_construction_shares.py::test_window_refusal_is_accounted_and_later_window_succeeds[formalization]'),
    ('soft_context_skip', 'ara/runtime/calls.py',
     "'window' if kind in ('select_t_roots', 'build_t_batch')", "'run' if kind in ('select_t_roots', 'build_t_batch')",
     'tests/runtime/test_construction_shares.py::test_window_refusal_is_accounted_and_later_window_succeeds[correction_context]'),
    ('soft_exhaustion', 'ara/runtime/construction.py',
     'if available <= 0 or symbol_available <= 0:', 'if False:',
     'tests/runtime/test_construction_shares.py::test_global_exhaustion_freezes_accepted_work_once'),
    ('soft_global_working', 'ara/runtime/construction.py',
     "require(cumulative.initial_input_tokens <= metadata['working_t_token_budget'],", 'require(True,',
     'tests/runtime/test_construction_shares.py::test_window_refusal_is_accounted_and_later_window_succeeds[working]'),
    ('soft_campaign_stop', 'ara/runtime/construction.py',
     "if isinstance(exc, BudgetStop) and exc.scope != 'window':", 'if False:',
     'tests/runtime/test_construction_shares.py::test_operational_and_campaign_failures_do_not_freeze[campaign]'),
    ('soft_exhaustion_disclosure', 'ara/runtime/export.py',
     "if e['stage'] == 'build_t_global_exhaustion'", 'if False',
     'tests/runtime/test_construction_shares.py::test_global_exhaustion_freezes_accepted_work_once'),
]

CASES += [
    ('soft_indivisible_window', 'ara/runtime/construction.py',
     'return min(measured, partition_bound) if len(ids) == 1 else measured', 'return measured',
     'tests/runtime/test_construction_shares.py::test_indivisible_oversized_window_is_skipped_without_losing_later_work'),
    ('soft_final_catalogue', 'ara/runtime/construction.py',
     'if final_catalog > symbol_budget:', 'if False:',
     'tests/runtime/test_construction_shares.py::test_catalogue_recount_cannot_freeze_over_global_bound[3]'),
]


CASES += [
    ('soft_counter_failure', 'ara/runtime/calls.py',
     "raise RuntimeError('token counting failed') from exc", 'raise',
     'tests/runtime/test_construction_shares.py::test_post_response_counter_error_is_not_a_window_refusal'),
]


CASES += [
    ('global_closure_admission_after_headroom', 'ara/runtime/construction.py',
     'if copied + growth > available or growth > symbol_available:',
     'if copied + growth > working_share or growth > symbol_available:',
     'tests/runtime/test_construction_shares.py::test_admission_continues_after_borrowing_crosses_headroom'),
    ('global_mandatory_bundle_above_share', 'ara/runtime/construction.py',
     'if copied + growth > available or growth > symbol_available:',
     "if len(ids) > window_budget['per_window_commitments'] or copied + growth > available or growth > symbol_available:",
     'tests/runtime/test_construction_shares.py::test_mandatory_bundle_borrows_global_capacity_and_preserves_endpoints'),
]


CASES += [
    ('construction_terminal_provider_skip', 'ara/runtime/calls.py',
     "if kind in ('select_t_roots', 'build_t_batch') and terminal_request_refusal(exc):", 'if False:',
     'tests/runtime/test_construction_shares.py::test_terminal_provider_request_refusal_skips_window_at_reservation[200-select_t_roots]'),
    ('provider_size_diagnostic', 'ara/runtime/providers.py',
     'if size:', 'if False:',
     'tests/runtime/test_schema_preflight.py::test_provider_size_diagnostic_accepts_only_complete_safe_messages'),
    ('construction_resume_artifact_hash', 'ara/runtime/construction_resume.py',
     "require(digest(content) == data['output_hash'],", 'require(True,',
     'tests/runtime/test_construction_resume.py::test_resume_refuses_unverified_state_before_dispatch[artifact]'),
    ('construction_resume_same_plan', 'ara/runtime/construction.py',
     "require(plan_id == resumption['plan_id'],", 'require(True,',
     'tests/runtime/test_construction_resume.py::test_resume_refuses_unverified_state_before_dispatch[plan]'),
    ('construction_resume_cli_wire', 'ara/runtime/cli.py',
     'calls.construction_resume = True', 'calls.construction_resume = False',
     'tests/runtime/test_construction_resume.py::test_resume_cli_reuses_stored_run_and_refuses_second_freeze'),
]


CASES += [
    ('construction_provider_scope', 'ara/runtime/calls.py',
     'and terminal_request_refusal(exc):', 'and True:',
     'tests/runtime/test_construction_shares.py::test_non_request_provider_failures_remain_fatal[500-invalid_request_error]'),
    ('construction_resume_lock', 'ara/runtime/construction_resume.py',
     'fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)', 'pass',
     'tests/runtime/test_construction_resume.py::test_resume_cli_prevents_concurrent_dispatch'),
]

CASES += [
    ('report_section_budget', 'ara/runtime/report_render.py',
     'if used + size > allowance:', 'if False:',
     'tests/runtime/test_report_size.py::test_section_budget_keeps_paper_items_and_explicit_links'),
    ('report_global_budget', 'ara/runtime/report_render.py',
     'allowance = min(self.budget, HTML_BYTES - self.size - 1000)', 'allowance = self.budget',
     'tests/runtime/test_report_size.py::test_global_budget_keeps_all_run_files'),
    ('report_event_identity', 'ara/runtime/report_files.py',
     'event_hash = digest(canonical(event))', 'event_hash = digest(canonical(row))',
     'tests/runtime/test_report_size.py::test_large_imported_history_is_external_and_unique'),
    ('report_tree_preview', 'ara/runtime/report_render.py',
     "visible = [r for r in rows if r[2] is not None and r[2] < TREE_LEVELS][:TREE_NODES]", 'visible = rows',
     'tests/engine/test_search_trace.py::test_native_500_state_trace_full_report'),
    ('report_paper_file', 'ara/runtime/report_render.py',
     'files.projection(paper, run)', "{**files.projection(paper, run), 'outcome': None}",
     'tests/runtime/test_report_size.py::test_section_budget_keeps_paper_items_and_explicit_links'),
]


CASES += [
    ('construction_counter_classification', 'ara/runtime/calls.py',
     'if terminal_request_refusal(exc):', 'if False:',
     'tests/runtime/test_construction_shares.py::test_counter_request_refusal_splits_or_skips_without_losing_later_windows[partition]'),
    ('construction_counter_split', 'ara/runtime/construction.py',
     'return partition_bound + 1 if len(ids) > 1 else partition_bound', 'return partition_bound',
     'tests/runtime/test_construction_shares.py::test_counter_request_refusal_splits_or_skips_without_losing_later_windows[partition]'),
    ('construction_uncounted_omit', 'ara/runtime/construction.py',
     'if batch.input_tokens is None:', 'if False:',
     'tests/runtime/test_construction_shares.py::test_counter_request_refusal_splits_or_skips_without_losing_later_windows[singleton]'),
    ('construction_counter_no_model_receipt', 'ara/runtime/calls.py',
     'if isinstance(exc, CountRequestRefused) and not dispatched:', 'if False:',
     'tests/runtime/test_construction_shares.py::test_counter_request_refusal_splits_or_skips_without_losing_later_windows[admission]'),
    ('construction_resume_preview_dispatch', 'ara/runtime/planning.py',
     'plan_only=True, resume_state=state', 'plan_only=False, resume_state=state',
     'tests/runtime/test_construction_resume.py::test_resume_plan_only_restores_in_separate_log_without_generation_or_source_edits'),
    ('construction_account_credit_scope', 'ara/runtime/providers.py',
     "evidence['message'] != 'Provider account credit is insufficient.'", 'True',
     'tests/runtime/test_schema_preflight.py::test_account_credit_diagnostic_is_sanitized_and_not_a_window_refusal'),
    ('construction_resume_preview_source', 'ara/runtime/cli.py',
     "log = EventLog(args.output_dir / 'events.jsonl')", 'log = source_log',
     'tests/runtime/test_construction_resume.py::test_resume_plan_only_restores_in_separate_log_without_generation_or_source_edits'),
    ('construction_counter_safe_diagnostic', 'ara/runtime/calls.py',
     "cost_usd=0, evidence=provider_error_evidence(exc))\n                raise CountRequestRefused", "cost_usd=0, evidence=str(exc))\n                raise CountRequestRefused",
     'tests/runtime/test_construction_shares.py::test_counter_request_refusal_splits_or_skips_without_losing_later_windows[singleton]'),
]


CASES += [
    ('construction_resume_account_scope', 'ara/runtime/construction_resume.py',
     "diagnostic.get('message') != 'Provider account credit is insufficient.' and", 'True and',
     'tests/runtime/test_construction_resume.py::test_resume_does_not_turn_account_failure_into_window_omission'),
]


CASES += [
    ('construction_initial_cap_multiplier', 'ara/runtime/closure_budget.py',
     "config.get('construction_window_cap_multiplier', 2)", '2',
     'tests/runtime/test_bounded_closure.py::test_initial_window_cap_is_configurable_and_disclosed'),
    ('construction_cap_depth_cut', 'ara/runtime/construction.py',
     "if len(ids - materialized) > window_cap:", 'if False:',
     'tests/runtime/test_bounded_closure.py::test_native_closure_is_depth_cut_to_initial_window_cap'),
    ('construction_cap_stays_initial', 'ara/runtime/construction.py',
     "if len(ids - materialized) > window_cap:",
     "if len(ids - materialized) > window_budget['per_window_commitments'] * allocation['window_cap_multiplier']:",
     'tests/runtime/test_bounded_closure.py::test_later_window_keeps_initial_cap_after_an_empty_window'),
    ('construction_fresh_run_mode', 'ara/runtime/cli.py',
     "calls = calls_factory(config, log, topic)\n            engine = engine_factory(bank, calls)",
     "calls = calls_factory(config, log, topic)\n            calls.construction_resume = True\n            engine = engine_factory(bank, calls)",
     'tests/runtime/test_construction_resume.py::test_fresh_run_does_not_restore_prior_batches_and_cap_changes_plan'),
    ('construction_stage_dispatch', 'ara/runtime/calls.py',
     'return scoped._call_once(kind, inputs, check, attempt=attempt, schema_smoke=schema_smoke)',
     'return self._call_reserved(kind, inputs, check, attempt=attempt, schema_smoke=schema_smoke)',
     'tests/runtime/test_construction_stages.py::test_native_construction_routes_selection_formalization_and_correction[False]'),
    ('construction_correction_dispatch', 'ara/runtime/calls.py',
     "correction=attempt > 1 or inputs.get('mode') == 'targeted_correction'", 'correction=False',
     'tests/runtime/test_construction_stages.py::test_native_construction_routes_selection_formalization_and_correction[False]'),
    ('construction_stage_cache_identity', 'ara/runtime/calls.py',
     "'dispatch_settings': self._dispatch_identity", "'dispatch_settings': None",
     'tests/runtime/test_construction_stages.py::test_native_construction_routes_selection_formalization_and_correction[False]'),
    ('construction_profile_preserves_stages', 'ara/runtime/cli.py',
     "stages = {**config.get('stages', {}), **profile.get('stages', {})}", "stages = profile.get('stages', {})",
     'tests/runtime/test_construction_stages.py::test_native_construction_routes_selection_formalization_and_correction[True]'),
    ('construction_stage_plan_identity', 'ara/runtime/construction.py',
     "'construction_stages': construction_stage_manifest(calls.config)", "'construction_stages': {}",
     'tests/runtime/test_construction_stages.py::test_native_construction_routes_selection_formalization_and_correction[False]'),
    ('parallel_writer', 'ara/runtime/logging.py',
     'self._writer.submit(self._destination.get().emit, event).result()', 'self._destination.get().emit(event)',
     'tests/runtime/test_parallel_search.py::test_single_writer'),
    ('parallel_writer_wiring', 'ara/runtime/logging.py',
     'self._writer.submit(self._destination.get().emit_many, tuple(events)).result()',
     'self._destination.get().emit_many(tuple(events))',
     'tests/runtime/test_parallel_search.py::test_native_search_uses_writer_and_default_limit'),
    ('parallel_reservation', 'ara/runtime/budget.py',
     'self._reservations.add(reservation)', 'pass',
     'tests/runtime/test_parallel_search.py::test_concurrent_admission_reserves_inflight'),
    ('parallel_reservation_lock', 'ara/runtime/budget.py',
     'with self._lock:\n            if self._halted is not None:',
     'if True:\n            if self._halted is not None:',
     'tests/runtime/test_parallel_search.py::test_reservation_check_and_claim_are_atomic'),
    ('parallel_equivalence', 'ara/runtime/orchestration.py',
     'engine._search_serial = serial', 'engine._search_serial = 0',
     'tests/runtime/test_parallel_search.py::test_parallel_native_equivalence'),
    ('parallel_result_pairing', 'ara/runtime/orchestration.py',
     'analysis = analyse_searches(positive, results[i], results[i + 1])',
     'analysis = analyse_searches(positive, results[i], results[i])',
     'tests/runtime/test_parallel_search.py::test_parallel_native_equivalence'),
    ('parallel_recovery_isolation', 'ara/runtime/budget.py',
     'self.used_tokens += tokens(usage) - reservation.charged_tokens',
     'self.used_tokens = tokens(usage)',
     'tests/runtime/test_parallel_search.py::test_recovery_does_not_erase_other_request'),
    ('parallel_durable_reservation', 'ara/runtime/calls.py',
     '# Keep the reservation until the measured receipt is durable.',
     "self.budget.settle(state['reservation'], usage, cost)  # release before receipt",
     'tests/runtime/test_parallel_search.py::test_reservation_is_held_until_receipt_is_durable'),
    ('parallel_single_flight', 'ara/runtime/calls.py',
     'with lock:\n            return self._call_reserved',
     'if True:\n            return self._call_reserved',
     'tests/runtime/test_parallel_search.py::test_same_request_single_flight'),
    ('lineage_hash_recheck', 'ara/runtime/verification.py',
     "return all(file_hash(path) == checksum for path, checksum in files.items())", 'return True',
     'tests/runtime/test_verification_receipts.py::test_changed_input_forces_full_verification_and_refuses[ancestor]'),
    ('lineage_anchor_verification', 'ara/runtime/provenance.py',
     "if content.decode().splitlines() != [r['hash'] for r in rows]:", 'if False:',
     'tests/runtime/test_verification_receipts.py::test_changed_input_forces_full_verification_and_refuses[ancestor_anchor]'),
    ('lineage_verifier_version', 'ara/runtime/verification.py',
     "candidate['verifier'] != verifier", 'False',
     'tests/runtime/test_verification_receipts.py::test_invalid_cache_or_changed_valid_input_is_fully_reverified[version]'),
    ('lineage_receipt_anchor', 'ara/runtime/verification.py',
     "path.with_suffix('.anchor').read_bytes() != ''.join(r['hash'] + '\\n' for r in rows).encode()", 'False',
     'tests/runtime/test_verification_receipts.py::test_invalid_cache_or_changed_valid_input_is_fully_reverified[receipt_anchor]'),
    ('lineage_symlink_hash_binding', 'ara/runtime/logging.py',
     'key = str(Path(path).absolute())', 'key = str(Path(path).resolve())',
     'tests/runtime/test_verification_receipts.py::test_changed_input_forces_full_verification_and_refuses[symlink]'),
    ('lineage_receipt_logged', 'ara/runtime/verification.py',
     "log.record('lineage_verification',", "dict(stage='lineage_verification',",
     'tests/runtime/test_verification_receipts.py::test_native_startup_reuses_chained_receipt_without_reverification'),
]


CASES += [
    ('lineage_header_binding', 'ara/runtime/verification.py',
     'if not text.startswith(HEADER) and not sidecar.exists() and not candidates:',
     'if not text.startswith(HEADER):',
     'tests/runtime/test_verification_receipts.py::test_changed_input_forces_full_verification_and_refuses[header]'),
    ('lineage_full_stable_inputs', 'ara/runtime/verification.py',
     'if not matching_inputs(files) or json.loads(sidecar.read_bytes()) != origin:',
     'if json.loads(sidecar.read_bytes()) != origin:',
     'tests/runtime/test_verification_receipts.py::test_input_changed_during_verification_is_refused[full]'),
    ('lineage_warm_stable_inputs', 'ara/runtime/verification.py',
     "if digest(canonical(events)) != candidate['events_sha256'] or not matching_inputs(files):",
     "if digest(canonical(events)) != candidate['events_sha256']:",
     'tests/runtime/test_verification_receipts.py::test_input_changed_during_verification_is_refused[warm]'),
]


CASES += [
    ('search_publication_order', 'ara/runtime/search_publication.py',
     'for index, journal in enumerate(self.journals):',
     'for index, journal in reversed(list(enumerate(self.journals))):',
     'tests/runtime/test_search_publication.py::test_native_publication_order_under_reversed_schedule'),
    ('search_publication_destination', 'ara/runtime/search_publication.py',
     'with self.log.destination(self.journals[index]):',
     "with __import__('contextlib').nullcontext():",
     'tests/runtime/test_search_publication.py::test_native_publication_order_under_reversed_schedule'),
    ('search_unpublished_resume', 'ara/runtime/budget.py',
     'if pending_search_publications(log.read()):', 'if False:',
     'tests/runtime/test_search_publication.py::test_unpublished_accounting_is_durable_and_refuses_resume'),
    ('search_unpublished_export', 'ara/runtime/export.py',
     'and not lineage_incomplete and not unpublished,', 'and not lineage_incomplete,',
     'tests/runtime/test_search_publication.py::test_unpublished_accounting_is_durable_and_refuses_resume'),
]

CASES += [
    ('cli_safe_mode', 'ara/runtime/claude_code.py', "['--safe-mode', '--exclude", "['--exclude",
     'tests/runtime/test_claude_code.py::test_native_preflight_receipts_schema_cache_and_export'),
    ('cli_schema_transport', 'ara/runtime/claude_code.py', "'--json-schema', canonical({k: v for k, v in schema.items() if k != '$schema'})", "'--json-schema', '{}'",
     'tests/runtime/test_claude_code.py::test_stage_model_system_and_input_are_preserved'),
    ('cli_identity_scan', 'ara/runtime/claude_code.py', 'if any(term.casefold() in folded for term in self.identity):', 'if False:',
     'tests/runtime/test_claude_code.py::test_provider_errors_never_echo_output[identity]'),
    ('cli_forbidden_scan', 'ara/runtime/claude_code.py', 'if any(term.casefold() in combined for term in self.forbidden):', 'if False:',
     'tests/runtime/test_claude_code.py::test_preflight_fails_closed[forbidden_debug]'),
    ('cli_debug_proof', 'ara/runtime/claude_code.py', 'if not all(marker in debug for marker in required):', 'if False:',
     'tests/runtime/test_claude_code.py::test_preflight_fails_closed[missing_debug]'),
    ('cli_preflight_each_run', 'ara/runtime/calls.py', "self.call('isolation_canary', {})", 'pass',
     'tests/runtime/test_claude_code.py::test_native_preflight_receipts_schema_cache_and_export'),
    ('cli_no_stderr_echo', 'ara/runtime/claude_code.py', 'receipt.update(exit_status=result.returncode, wall_seconds=time.monotonic()-started)',
     "receipt.update(exit_status=result.returncode, wall_seconds=time.monotonic()-started, stderr=result.stderr)",
     'tests/runtime/test_claude_code.py::test_provider_errors_never_echo_output[exit]'),
    ('cli_retry_bound', 'ara/runtime/calls.py', "range(getattr(provider, 'retries', 0) + 1)", "range(1)",
     'tests/runtime/test_claude_code.py::test_bounded_logged_retry[rate]'),
    ('cli_concurrency', 'ara/runtime/claude_code.py', 'threading.BoundedSemaphore(self.concurrency)', 'threading.BoundedSemaphore(64)',
     'tests/runtime/test_claude_code.py::test_configurable_concurrency_and_fresh_sessions[2]'),
    ('cli_concurrent_admission', 'ara/runtime/budget.py', "if self.cap_tokens(subscription) + sum(tokens(r.usage) for r in self._reservations) + tokens(usage) > self.config['token_cap']:", 'if False:',
     'tests/runtime/test_claude_code.py::test_concurrent_budget_admission_cannot_oversubscribe'),
]


CASES += [
    ('cli_system_cache', 'ara/runtime/calls.py', "if stage_settings(self.config, kind).get('system_prompt') else {}", 'if False else {}', 'tests/runtime/test_claude_code.py::test_configured_system_prompt_partitions_existing_cache'),
    ('cli_stop_artifact', 'ara/runtime/budget.py', "def stop(self, reason: str, stage: str, *, scope='run', **details) -> None:\n        with self._lock:", "def stop(self, reason: str, stage: str, *, scope='run', **details) -> None:\n        with RLock():", 'tests/runtime/test_claude_code.py::test_concurrent_stop_artifacts_are_serialized'),
]


CASES += [
    ('mixed_stage_canary', 'ara/runtime/calls.py',
     "if kind != 'isolation_canary':\n            self._ensure_provider_ready()",
     "if False:\n            self._ensure_provider_ready()",
     'tests/runtime/test_provider_integration.py::test_api_run_subscription_stage_canary_accounting_and_retries[False]'),
    ('mixed_stage_retries', 'ara/runtime/calls.py',
     "range(getattr(provider, 'retries', 0) + 1)", "range(getattr(self.provider, 'retries', 0) + 1)",
     'tests/runtime/test_provider_integration.py::test_api_run_subscription_stage_canary_accounting_and_retries[True]'),
    ('mixed_served_api_price', 'ara/runtime/budget.py',
     "if raw.get('provider') in ('claude_code', 'codex_cli'):", 'if self.subscription:',
     'tests/runtime/test_provider_integration.py::test_subscription_run_api_stage_retains_prices_and_cap'),
]


CASES += [
    ('cli_decoded_credentials', 'ara/runtime/claude_code.py', 'self.scan_output(data, secrets=secrets)', 'pass',
     'tests/runtime/test_claude_code.py::test_json_escaped_credential_rejected_before_retention'),
    ('cli_cached_credentials', 'ara/runtime/calls.py', "self.provider.scan_output(saved['raw'])", 'pass',
     'tests/runtime/test_claude_code.py::test_cached_credential_rejected_without_logging_and_evicted'),
    ('cli_construction_transport', 'ara/runtime/construction.py',
     'calls._transport_call(kind, inputs, check, attempt=1)', 'calls._call_once(kind, inputs, check, attempt=1)',
     'tests/runtime/test_claude_code.py::test_native_construction_transport_retries'),
    ('cli_correction_transport', 'ara/runtime/construction.py',
     'calls._transport_call(kind, request, corrected, attempt=correction + 2)', 'calls._call_once(kind, request, corrected, attempt=correction + 2)',
     'tests/runtime/test_claude_code.py::test_targeted_construction_retry_does_not_spend_more_corrections'),
    ('cli_access_token_only', 'ara/runtime/claude_code.py',
     "return oauth['accessToken'], frozenset(secrets)",
     "return oauth['refreshToken'], frozenset(secrets)",
     'tests/runtime/test_claude_code.py::test_only_access_token_reaches_child_environment'),
    ('cli_live_credential_read', 'ara/runtime/claude_code.py',
     "oauth = json.loads(self._credential_source.read_text())['claudeAiOauth']",
     "oauth = self.__dict__.setdefault('_cached_oauth', json.loads(self._credential_source.read_text())['claudeAiOauth'])",
     'tests/runtime/test_claude_code.py::test_credential_file_replaced_between_calls_is_read_fresh'),
]


CASES += [
    ('cli_initial_context_partition', 'ara/runtime/construction.py',
     "formal = calls.count_request('build_t_batch', inputs).initial_input_tokens",
     "formal = calls.count_request('build_t_batch', inputs).reservation.input_tokens",
     'tests/runtime/test_subagent_counting.py::test_native_subscription_plan_uses_initial_context_at_pilot_limits'),
    ('cli_transport_reservation_contract', 'ara/runtime/calls.py',
     'return RequestCount(initial, context_output, estimate)',
     'return RequestCount(initial, context_output, TokenUsage(input_tokens=initial, output_tokens=context_output))',
     'tests/runtime/test_subagent_counting.py::test_count_contract_retains_aggregate_for_admission'),
    ('cli_resolved_correction_settings', 'ara/runtime/construction_stages.py',
     "**overrides, 'stages': {}", "**overrides, 'stages': config.get('stages', {})",
     'tests/runtime/test_provider_integration.py::test_native_cli_correction_matches_stage_manifest'),
    ('api_resolved_correction_settings', 'ara/runtime/construction_stages.py',
     "**overrides, 'stages': {}", "**overrides, 'stages': config.get('stages', {})",
     'tests/runtime/test_provider_integration.py::test_native_api_correction_matches_stage_manifest'),
]


CASES += [
    ('cli_calibrated_count', 'ara/runtime/claude_code.py',
     'initial = self.calibration_state.initial(self.model_for(kind), kind, size)', 'initial = size + 16384',
     'tests/runtime/test_claude_calibration.py::test_provider_uses_calibration_and_keeps_two_turn_reservation'),
    ('cli_calibration_learning', 'ara/runtime/claude_estimation.py',
     'underestimated = actual > estimated', 'underestimated = False',
     'tests/runtime/test_claude_calibration.py::test_live_usage_tightens_later_calls_without_invalidating_cache'),
    ('cli_calibration_shared', 'ara/runtime/calls.py',
     'stage_provider.calibration_state = self._calibration_state', 'pass',
     'tests/runtime/test_claude_calibration.py::test_correction_provider_reuses_run_calibration'),
    ('cli_calibration_restore', 'ara/runtime/claude_estimation.py',
     'self._factors[key] = max(self.factor(*key), factor)', 'pass',
     'tests/runtime/test_claude_calibration.py::test_live_usage_tightens_later_calls_without_invalidating_cache'),
    ('construction_scarce_slots', 'ara/runtime/closure_budget.py', 'if scarce:', 'if False:',
     'tests/runtime/test_construction_shares.py::test_zero_initial_share_discloses_zero_cap_without_dispatch[0.01]'),
]


CASES += [
    ('search_job_isolation', 'ara/runtime/search_jobs.py',
     'return isinstance(exc, (Rejected, CountRequestRefused)) or (', 'return False and (',
     'tests/runtime/test_search_failures.py::test_failed_job_retries_after_initial_queue_and_preserves_sibling[1]'),
    ('search_job_retry_once', 'ara/runtime/search_jobs.py', 'for attempt in (1, 2):', 'for attempt in (1,):',
     'tests/runtime/test_search_failures.py::test_failed_job_retries_after_initial_queue_and_preserves_sibling[1]'),
    ('search_job_retry_order', 'ara/runtime/search_jobs.py', 'pending = sorted(retry)', 'pending = sorted(retry, reverse=True)',
     'tests/runtime/test_search_failures.py::test_failed_job_retries_after_initial_queue_and_preserves_sibling[1]'),
    ('search_global_stop', 'ara/runtime/search_jobs.py', "exc.scope != 'run'", 'True',
     'tests/runtime/test_search_failures.py::test_global_stop_cancels_queue_without_retry_and_keeps_completed_routes[budget]'),
    ('search_partial_routes', 'ara/runtime/orchestration.py', 'yield PartialSearch(results[i], results[i + 1])',
     'yield PartialSearch(None, None)',
     'tests/runtime/test_search_failures.py::test_failed_job_retries_after_initial_queue_and_preserves_sibling[1]'),
    ('search_partial_methodology', 'ara/runtime/export.py', "'search': {**search_status(events),", "'search': {**{},",
     'tests/runtime/test_search_failures.py::test_failed_job_retries_after_initial_queue_and_preserves_sibling[1]'),
    ('search_partial_selection', 'ara/runtime/cli.py', 'search=search_info)', 'search={})',
     'tests/runtime/test_search_failures.py::test_cli_partial_search_reaches_selection_and_composes'),
    ('search_selection_unknown_policy', 'ara/runtime/cli.py',
     "selection_config['unknown_usage_policy'] = args.unknown_usage_policy", 'pass',
     'tests/runtime/test_search_failures.py::test_cli_partial_search_reaches_selection_and_composes'),
    ('cli_like_for_like', 'ara/runtime/claude_estimation.py',
     'estimated = initial if first_turn else aggregate', 'estimated = initial',
     'tests/runtime/test_claude_calibration.py::test_two_turn_pilot_usage_does_not_inflate_initial_context'),
    ('cli_fixed_overhead', 'ara/runtime/claude_estimation.py',
     'self._overheads[model] = overhead_after', 'pass',
     'tests/runtime/test_claude_calibration.py::test_canary_learns_fixed_overhead_without_changing_text_factor'),
    ('cli_observation_version', 'ara/runtime/claude_estimation.py',
     "or row.get('observation_version') != OBSERVATION_VERSION", '',
     'tests/runtime/test_claude_calibration.py::test_old_mismatched_observations_are_not_restored'),
    ('cli_local_token_cap', 'ara/runtime/budget.py',
     'self.used_tokens - (self.imported_tokens if subscription else 0)', 'self.used_tokens',
     'tests/runtime/test_claude_code.py::test_subscription_token_cap_excludes_only_imported_history'),
    ('cli_transient_exit_retry', 'ara/runtime/claude_code.py',
     "('cli_max_turns', True, 'max_turns')",
     "('cli_max_turns', False, 'max_turns')",
     'tests/runtime/test_claude_code.py::test_transient_exit_retries_to_success_without_losing_usage'),
    ('cli_deterministic_schema_exit', 'ara/runtime/claude_code.py',
     "return 'cli_invalid_schema', False", "return 'cli_invalid_schema', True",
     'tests/runtime/test_claude_code.py::test_exit_one_classification_preserves_usage_and_bounds_retries'),
]


CASES += [
    ('cli_subtype_auth_request_classification', 'ara/runtime/claude_code.py',
     "('subtype', 'errors', 'error', 'error_type', 'result')",
     "('errors', 'error', 'error_type', 'result')",
     'tests/runtime/test_claude_code.py::test_json_error_categories_follow_retry_policy'),
    ('cli_unclassified_retry_enabled', 'ara/runtime/claude_code.py',
     "if code == 'cli_exit_error' and receipt.get('exit_status') == 1:", 'if False:',
     'tests/runtime/test_claude_code.py::test_unclassified_exit_retries_once_with_named_event'),
    ('cli_unclassified_retry_once', 'ara/runtime/calls.py',
     'unclassified_retries >= 1', 'False',
     'tests/runtime/test_claude_code.py::test_unclassified_exit_retries_once_with_named_event'),
    ('cli_diagnostic_text_suppressed', 'ara/runtime/claude_code.py',
     'error_category=category, stderr_bytes=len(stderr.encode())',
     'stderr_first_line=stderr, error_category=category, stderr_bytes=len(stderr.encode())',
     'tests/runtime/test_claude_code.py::test_kappa2_diagnostics_never_retain_free_text'),
    ('cli_diagnostic_subtype_allowlist', 'ara/runtime/claude_code.py',
     'if subtype in FAILURE_SUBTYPES:', 'if True:',
     'tests/runtime/test_claude_code.py::test_json_diagnostics_are_suppressed'),
    ('cli_diagnostic_category_enum', 'ara/runtime/claude_code.py',
     'error_category=category, stderr_bytes=len(stderr.encode())',
     "error_category=data.get('error_type', category), stderr_bytes=len(stderr.encode())",
     'tests/runtime/test_claude_code.py::test_json_diagnostics_are_suppressed'),
]


CASES += [
    ('cli_auth_retry_enabled', 'ara/runtime/claude_code.py',
     "return 'cli_auth_error', True, 'auth'", "return 'cli_auth_error', False, 'auth'",
     'tests/runtime/test_claude_code.py::test_auth_reread_retry_is_once_and_accounted'),
    ('cli_auth_retry_once', 'ara/runtime/calls.py',
     'auth_retries >= 1', 'False',
     'tests/runtime/test_claude_code.py::test_auth_reread_retry_is_once_and_accounted'),
]



CASES += [
    ('codex_goal_tools_disabled', 'ara/runtime/codex_cli.py',
     "'hooks', 'memories', 'goals', 'multi_agent'", "'hooks', 'memories', 'multi_agent'",
     'tests/runtime/test_codex_cli.py::test_native_calls_and_receipts'),
    ('codex_tool_event_gate', 'ara/runtime/codex_cli.py',
     'if rejection: reject(rejection)', 'if False: reject(rejection)',
     'tests/runtime/test_codex_cli.py::test_tool_event_rejected_without_echo'),
    ('codex_unknown_event_gate', 'ara/runtime/codex_cli.py',
     'elif kind not in SAFE_EVENTS:', 'elif False:',
     'tests/runtime/test_codex_cli.py::test_suppressed_failures'),
    ('codex_readonly_auth', 'ara/runtime/codex_cli.py',
     "'--ro-bind',f'/proc/self/fd/{credential.fileno()}'", "'--bind',f'/proc/self/fd/{credential.fileno()}'",
     'tests/runtime/test_codex_cli.py::test_fresh_credential_and_read_only_link'),
    ('codex_no_api_key', 'ara/runtime/codex_cli.py',
     "or document.get('OPENAI_API_KEY')", 'or False',
     'tests/runtime/test_codex_cli.py::test_api_key_refused'),
    ('codex_stage_model_pin', 'ara/runtime/codex_cli.py',
     "'-m',model", "'-m','gpt-5.4'",
     'tests/runtime/test_codex_cli.py::test_stage_model_pin'),
    ('codex_context_gate', 'ara/runtime/codex_cli.py',
     "if any(value[field] != '' for field in ('skills', 'memory', 'claude_md', 'agents_md')):",
     'if False:', 'tests/runtime/test_codex_cli.py::test_isolation_canary_rejects_context'),
    ('codex_diagnostics_suppressed', 'ara/runtime/codex_cli.py',
     'events = []', "receipt['stderr'] = stderr; events = []",
     'tests/runtime/test_codex_cli.py::test_suppressed_failures'),
    ('codex_refresh_endpoint_disabled', 'ara/runtime/codex_cli.py',
     "'CODEX_REFRESH_TOKEN_URL_OVERRIDE':'disabled://refresh'", "'CODEX_REFRESH_TOKEN_URL_OVERRIDE':'https://example.invalid'",
     'tests/runtime/test_codex_cli.py::test_fresh_credential_and_read_only_link'),
]

CASES += [
    ('codex_model_instructions_isolated', 'ara/runtime/codex_cli.py',
     "'model_instructions_file='+canonical(str(instructions_path))", "'developer_instructions='+canonical(str(instructions_path))",
     'tests/runtime/test_codex_cli.py::test_native_calls_and_receipts'),
    ('codex_bundled_skills_disabled', 'ara/runtime/codex_cli.py',
     "'skills.bundled.enabled=false'", "'skills.bundled.enabled=true'",
     'tests/runtime/test_codex_cli.py::test_native_calls_and_receipts'),
    ('codex_no_worker_auth_fallback', 'ara/runtime/codex_cli.py',
     "auth_file = options.get('auth_file')",
     "auth_file = options.get('auth_file', str(Path(os.environ['CODEX_HOME'])/'auth.json'))",
     'tests/runtime/test_codex_cli.py::test_auth_source_required_without_worker_home_fallback'),
]


CASES += [
    ('codex_visible_tool_receipt', 'ara/runtime/codex_cli.py',
     "receipt['visible_tool_names'] = tool_names", "receipt['visible_tool_names'] = []",
     'tests/runtime/test_codex_cli.py::test_generic_visible_tools_disclosed_but_events_rejected'),
    ('codex_task_only_no_tools', 'ara/runtime/codex_cli.py',
     'Do not use tools for any purpose', 'Tools may be used',
     'tests/runtime/test_codex_cli.py::test_native_calls_and_receipts'),
]



CASES += [
    ('codex_strict_projection', 'ara/runtime/codex_cli.py',
     'wire = strict_schema(schema)', 'wire = schema',
     'tests/runtime/test_codex_cli.py::test_strict_wire_preflight_and_local_authority'),
    ('codex_required_optional', 'ara/runtime/codex_schema.py',
     "result['required'] = list(properties)", "result['required'] = list(required)",
     'tests/runtime/test_codex_schema.py::test_optional_null_roundtrip_and_local_constraints'),
    ('codex_closed_objects', 'ara/runtime/codex_schema.py',
     "result['additionalProperties'] = False", "result['additionalProperties'] = True",
     'tests/runtime/test_codex_schema.py::test_all_native_schemas_recursive_and_closed'),
    ('codex_normalize_before_validation', 'ara/runtime/calls.py',
     "data = self.provider.normalize_output(schema, data)", 'data = data',
     'tests/runtime/test_codex_cli.py::test_strict_wire_preflight_and_local_authority'),
    ('codex_local_authority', 'ara/runtime/calls.py',
     'validate_local(schema, data, self.config)', 'pass # bypass native validation',
     'tests/runtime/test_codex_cli.py::test_strict_wire_preflight_and_local_authority'),
    ('codex_preflight_live_receipt', 'ara/runtime/codex_preflight.py',
     "or cli.get('wire_schema_hash')!=case['wire_schema_hash']", 'or False',
     'tests/runtime/test_codex_cli.py::test_codex_preflight_gate_rejects_incomplete_receipts[wrong_wire]'),
    ('codex_preflight_coverage', 'ara/runtime/codex_preflight.py',
     'if sorted(accepted) != sorted(cases):', 'if False:',
     'tests/runtime/test_codex_cli.py::test_codex_preflight_gate_rejects_incomplete_receipts[missing_case]'),
    ('codex_preflight_no_cache', 'ara/runtime/codex_preflight.py',
     "or receipt.get('cache_hit') is not False", 'or False',
     'tests/runtime/test_codex_cli.py::test_codex_preflight_gate_rejects_incomplete_receipts[cached]'),
    ('codex_pilot_schema_gate', 'ara/runtime/cli.py',
     'require_codex_preflight(config, ROOT)\n            directory =', 'pass\n            directory =',
     'tests/runtime/test_codex_cli.py::test_codex_pilot_requires_preflight_before_provider'),
    ('search_resume_frozen_hash', 'ara/runtime/search_resume.py',
     "require(digest(artifact.to_json()) == digest(commitments.to_json()),", 'require(True,',
     'tests/runtime/test_search_resume.py::test_resume_refuses_mismatch_before_publication[t]'),
    ('search_resume_targets', 'ara/runtime/search_resume.py',
     "[j['goal'] for j in batch['jobs']] == [g.to_dict() for g in goals]", 'True',
     'tests/runtime/test_search_resume.py::test_resume_refuses_mismatch_before_publication[job_target]'),
    ('search_resume_seal', 'ara/runtime/search_resume.py',
     "rows[0].get('search_id') == seal['search_id']", 'True',
     'tests/runtime/test_search_resume.py::test_resume_refuses_mismatch_before_publication[seal]'),
    ('search_resume_measured_settlement', 'ara/runtime/search_resume.py',
     'pending.extend(state.settlements)', 'pass',
     'tests/runtime/test_search_resume.py::test_resume_offline_publishes_once_and_settles_measured_receipt'),
    ('search_resume_completed_dispatch', 'ara/runtime/search_jobs.py',
     'pending = [i for i in range(len(jobs)) if i not in restored]', 'pending = list(range(len(jobs)))',
     'tests/runtime/test_search_resume.py::test_resume_dispatches_only_missing_job_and_finishes_native_lifecycle'),
    ('search_resume_current_generation', 'ara/runtime/search_resume.py',
     "current_search_finished(main, batches[-1]['batch_id'], restored)",
     "any(e['stage'] == 'awaiting_selection' for e in main)",
     'tests/runtime/test_search_resume.py::test_resume_after_partial_recovery_halt_publishes_current_results'),
    ('search_resume_license_inventory', 'ara/runtime/search_resume.py',
     'return result, licenses', 'return result, []',
     'tests/runtime/test_search_resume.py::test_resume_restores_licenses_even_when_node_cap_discards_the_proposal'),

]


CASES += [
    ('local_formula_fast_rejection', 'ara/runtime/validation.py',
     "            _fields(item, branch, path)", "            pass # omit structural formula guard",
     'tests/runtime/test_local_validation.py::test_stall_shape_rejected_before_recursive_validation'),
    ('local_discriminated_recursion', 'ara/runtime/validation.py',
     '        choices = tagged_branches(branches)', '        choices = None',
     'tests/runtime/test_local_validation.py::test_each_formula_node_is_validated_once'),
    ('local_depth_guard', 'ara/runtime/validation.py',
     "        if depth > limits['local_validation_max_depth']:", '        if False:',
     'tests/runtime/test_local_validation.py::test_complexity_rejection_enters_correction[local_validation_max_depth]'),
    ('local_node_guard', 'ara/runtime/validation.py',
     "    limits = guard_complexity(value, config, deadline=deadline)", "    limits = _limits(config)",
     'tests/runtime/test_local_validation.py::test_complexity_limit_is_explicit[local_validation_max_nodes-8]'),
    ('local_deadline_rejection', 'ara/runtime/validation.py',
     "        process.communicate()\n        _reject('local_validation_timeout_seconds exceeded', validator='local_validation_timeout_seconds')",
     "        process.communicate()\n        return None",
     'tests/runtime/test_local_validation.py::test_hard_deadline_works_in_search_threads'),
    ('local_json_decoder_depth', 'ara/runtime/validation.py',
     '    except RecursionError:', '    except KeyError:',
     'tests/runtime/test_local_validation.py::test_json_parser_depth_refusal_enters_correction'),
    ('local_native_authority', 'ara/runtime/validation.py',
     "            LinearValidator(request['schema']).validate(request['value'])", '            pass',
     'tests/runtime/test_local_validation.py::test_valid_deep_formula_and_native_constraints'),
]


CASES += [
    ('search_goal_reference', 'ara/engine/licensing.py', '            conclusion = goal', "            conclusion = self.formalise(Proposition('conclusion', proposal.conclusion_text))", 'tests/runtime/test_search_alignment.py::test_current_goal_reference_prevents_reformalization'),
    ('search_goal_reference_text', 'ara/engine/licensing.py', '            if proposal.conclusion_text != goal.text:', '            if False:', 'tests/runtime/test_search_alignment.py::test_explicit_goal_reference_does_not_override_changed_text'),
    ('search_catalogue_inputs', 'ara/runtime/calls.py', 'vocabulary = catalogue_inputs(self.log.path.parent, commitments)', "vocabulary = dict(symbol_catalogue=None, catalogue_sha256=None, catalogue_status='unavailable_legacy', commitments_sha256=digest(canonical(commitments.to_dict())), commitment_provenance=None, provenance_status='unavailable_legacy', provenance_sha256=None, definition_semantics='unavailable_legacy')", 'tests/runtime/test_search_alignment.py::test_current_goal_reference_prevents_reformalization'),
    ('search_target_preflight', 'ara/runtime/calls.py', '            if len(kept) >= keep_count:', '            if True:', 'tests/runtime/test_target_pool.py::test_two_corrections_preserve_survivors_and_give_witnesses'),
    ('search_proposal_batch', 'ara/runtime/calls.py', 'proposal_limit=3, attempt_budget=2,', 'proposal_limit=1, attempt_budget=2,', 'tests/runtime/test_search_alignment.py::test_three_proposal_batch_keeps_valid_alternative'),
    ('search_proposal_batch_bound', 'ara/runtime/calls.py', "require(len(proposals) <= 3, 'proposal batch exceeds three candidates')", "require(True, 'proposal batch exceeds three candidates')", 'tests/runtime/test_search_alignment.py::test_proposal_batch_bound_is_enforced'),
    ('search_joint_slots', 'ara/engine/licensing.py', 'premises = self.formaliser.formalise_slots(proposal, goal, entry, self.commitments)', 'premises = tuple(self.formalise(Proposition(s.id, by_slot[s.id].text)) for s in entry.premise_slots)', 'tests/runtime/test_search_alignment.py::test_current_goal_reference_prevents_reformalization'),
    ('search_shared_metavariables', 'ara/runtime/calls.py', 'shared_metavariables=metavariable_bindings(entry, goal, bindings),', 'shared_metavariables=[],', 'tests/runtime/test_search_alignment.py::test_joint_open_slots_share_goal_vocabulary_and_still_require_entailment'),
    ('search_t_membership', 'ara/runtime/calls.py', '                slot_bindings(proposal, commitments)', '                pass', 'tests/runtime/test_search_alignment.py::test_proposal_reference_correction[id]'),
    ('search_t_reference_text', 'ara/runtime/search_alignment.py', "require(fill.text == commitment.text, 'proposal T reference text mismatch: ' + fill.t_id)", "require(True, 'proposal T reference text mismatch: ' + fill.t_id)", 'tests/runtime/test_search_alignment.py::test_proposal_reference_correction[text]'),
    ('search_frozen_slot_identity', 'ara/runtime/search_alignment.py', 'require(bound is None or formula.canonical() == Formula.from_dict(bound).canonical(),', 'require(True,', 'tests/runtime/test_search_alignment.py::test_joint_slots_cannot_change_frozen_binding'),
    ('search_reference_trace', 'ara/engine/tracing.py', '        if proposal.conclusion_ref is not None:', '        if False:', 'tests/runtime/test_search_alignment.py::test_native_lifecycle_closure_and_offline_joint_replay'),
    ('construction_structure_correction', 'ara/runtime/construction.py',
     "            if not metrics['passed']:", "            if False:",
     'tests/runtime/test_construction_structure.py::test_flat_batch_fails_gate_and_gets_exactly_one_correction[flat]'),
    ('construction_endpoint_reuse', 'ara/runtime/construction_structure.py',
     "if id in formulas and not conjuncts(formulas[id]) <= side:", "if False:",
     'tests/runtime/test_construction_structure.py::test_nonflat_disconnected_inference_not_silently_accepted'),
    ('frozen_catalogue_hash', 'ara/runtime/frozen_catalogue.py',
     '    if catalogue != expected:', '    if False:',
     'tests/runtime/test_frozen_catalogue.py::test_catalogue_refuses_tampering[definition]'),
    ('frozen_catalogue_binding', 'ara/runtime/frozen_catalogue.py',
     "or value['commitments'] != commitments.to_dict()", 'or False',
     'tests/runtime/test_frozen_catalogue.py::test_catalogue_refuses_tampering[commitment]'),
]


CASES += [
    ('target_triviality_guard', 'ara/runtime/contribution.py',
     "            if result == 'SOLVER_UNSAT':", '            if False:',
     'tests/runtime/test_target_triviality.py::test_trivial_target_correction_and_exhaustion'),
    ('target_instance_guard', 'ara/runtime/contribution.py',
     '        for commitment in (None, *commitments.commitments):', '        for commitment in (None,):',
     'tests/runtime/test_target_triviality.py::test_single_commitment_instance_and_attribution'),
    ('target_rejection_filter', 'ara/runtime/calls.py',
     '                if reasons:', '                if False:',
     'tests/runtime/test_target_triviality.py::test_trivial_target_correction_and_exhaustion'),
    ('derived_selection_default', 'ara/runtime/route_policy.py',
     "return tuple(r for r in routes if route_classification(r, commitments, provenance) == 'CLOSED-derived')", 'return tuple(routes)',
     'tests/runtime/test_target_triviality.py::test_default_cli_lists_but_does_not_offer_trivial'),
    ('route_derivation_classification', 'ara/runtime/route_policy.py',
     "if len(supports) < 2 or not inferred:", "if True:",
     'tests/runtime/test_target_triviality.py::test_derived_classification_and_default_selection'),
    ('freeze_fork_anchor', 'ara/runtime/freeze_fork.py',
     "if (source/'events.anchor').read_text().splitlines() != [r['hash'] for r in rows]:", 'if False:',
     'tests/runtime/test_freeze_fork.py::test_fork_refuses_before_destination_or_provider[anchor]'),
    ('freeze_fork_artifact', 'ara/runtime/freeze_fork.py',
     "if CommitmentSet.from_json(artifacts['commitments.json'].decode()).to_dict()!=commitments.to_dict():", 'if False:',
     'tests/runtime/test_freeze_fork.py::test_fork_refuses_before_destination_or_provider[artifact]'),
    ('freeze_fork_accounting', 'ara/runtime/provenance.py',
     '            inherited.update(range(count))', '            pass',
     'tests/runtime/test_freeze_fork.py::test_fork_exact_prefix_and_single_accounting'),
]


CASES += [
    ('target_attribution_exclusion', 'ara/runtime/target_policy.py',
     "            reason = 'attributed_report'", '            pass',
     'tests/runtime/test_contribution_gate.py::test_exact_leading_report_stays_hard_rejection'),
    ('target_two_corrections', 'ara/runtime/calls.py',
     '        for attempt in range(3):', '        for attempt in range(2):',
     'tests/runtime/test_target_triviality.py::test_trivial_target_correction_and_exhaustion'),
    ('freeze_fork_chain', 'ara/runtime/logging.py',
     'digest(canonical(row)) != checksum', 'False',
     'tests/runtime/test_freeze_fork.py::test_fork_refuses_before_destination_or_provider[chain]'),
    ('freeze_fork_single_freeze', 'ara/runtime/freeze_fork.py',
     '        if len(freezes)!=1:', '        if False:',
     'tests/runtime/test_freeze_fork.py::test_fork_refuses_before_destination_or_provider[duplicate]'),
]


CASES += [
    ('target_instance_canonical', 'ara/runtime/contribution.py',
     "nested = bound + (f.variable,) if f.op in ('forall', 'exists') else bound", 'nested = bound',
     'tests/runtime/test_contribution_gate.py::test_alpha_equivalent_instance_and_cache'),
]


CASES += [
    ('contribution_both_polarities', 'ara/runtime/contribution.py',
     '    if both_polarities:', '    if False:',
     'tests/runtime/test_contribution_gate.py::test_solver_preflight_rejects_single_support_and_both_polarities'),
    ('contribution_validity', 'ara/runtime/contribution.py',
     'for commitment in (None, *commitments.commitments):', 'for commitment in commitments.commitments:',
     'tests/runtime/test_contribution_gate.py::test_validity_without_commitments'),
    ('contribution_unknown', 'ara/runtime/contribution.py',
     "unresolved = any(c['result'] != 'SOLVER_COUNTEREXAMPLE' for c in checks)", 'unresolved = False',
     'tests/runtime/test_contribution_gate.py::test_solver_unknown_fails_closed'),
    ('distinct_support_count', 'ara/runtime/route_policy.py',
     'if len(supports) < 2 or not inferred:', 'if not inferred:',
     'tests/runtime/test_contribution_gate.py::test_supports_exclude_assumptions_and_deduplicate_aliases'),
    ('support_aliases', 'ara/runtime/route_policy.py',
     'supports.setdefault(formula_hash(commitment.formula), {})[commitment.id] = commitment',
     'supports.setdefault(commitment.id, {})[commitment.id] = commitment',
     'tests/runtime/test_contribution_gate.py::test_supports_exclude_assumptions_and_deduplicate_aliases'),
    ('support_assumptions', 'ara/runtime/route_policy.py',
     "ids = ([node.t_id] if node.kind == 'leaf' else [])",
     "ids = ([node.t_id] if node.kind in ('leaf','assumption') else [])",
     'tests/runtime/test_contribution_gate.py::test_supports_exclude_assumptions_and_deduplicate_aliases'),
    ('closure_minimality', 'ara/runtime/route_policy.py',
     "'trivial':'CLOSED-single-support'", "'trivial':'CLOSED-derived'",
     'tests/runtime/test_contribution_gate.py::test_two_supports_do_not_override_single_support_entailment'),
    ('closure_unknown', 'ara/runtime/contribution.py', 'result = entails(premises, conclusion, timeout_ms)', "result = entails(premises, conclusion, timeout_ms)\n        if result not in ('SOLVER_UNSAT', 'SOLVER_COUNTEREXAMPLE'):\n            result = 'SOLVER_COUNTEREXAMPLE'", 'tests/runtime/test_contribution_gate.py::test_cq_dependencies_are_support_and_unknown_fails_closed'),
    ('closure_cq_support', 'ara/runtime/route_policy.py',
     'ids += [tid for answer in node.cq_answers for tid in answer.supporting_t_ids]', 'ids += []',
     'tests/runtime/test_contribution_gate.py::test_cq_dependencies_are_support_and_unknown_fails_closed'),
    ('own_thesis_required', 'ara/runtime/calls.py',
     "if classification['classification'] != 'own_thesis':", 'if False:',
     'tests/runtime/test_contribution_gate.py::test_classifier_is_required_and_logged_on_same_provider'),
    ('broader_attribution_lexicon', 'ara/runtime/target_policy.py',
     'believes?|defends?|endorses?|says?|states?|thinks?|accounts?',
     'says?|states?|thinks?|accounts?',
     'tests/runtime/test_contribution_gate.py::test_attributed_reports_rejected_by_classifier'),
    ('catalogue_attribution', 'ara/runtime/target_policy.py',
     "if (s['name'], s['kind'], s['arity']) in used for text", 'if False for text',
     'tests/runtime/test_contribution_gate.py::test_catalogue_attribution_is_classifier_evidence'),
    ('closure_attribution', 'ara/runtime/route_policy.py',
     'if leading_report_frame(root.text):', 'if False:',
     'tests/runtime/test_contribution_gate.py::test_native_attributed_closure_not_default_selectable'),
]


CASES += [
    ('report_contribution_namespace', 'ara/runtime/report.py',
     "classification=contribution['classification'], contribution=contribution,", '**contribution,',
     'tests/runtime/test_report_contribution.py'),
    ('report_event_polarity_authority', 'ara/runtime/report.py',
     "polarity=data.get('polarity'), graph=graph,",
     "polarity=contribution.get('polarity', data.get('polarity')), graph=graph,",
     'tests/runtime/test_report_contribution.py'),
]


CASES += [
    ('content_commitment_correction', 'ara/runtime/construction.py',
     "require(not issues, 'content definition", "require(True, 'content definition",
     'tests/runtime/test_content_provenance.py::test_attributed_definition_gets_logged_targeted_correction[commitment]'),
    ('content_symbol_correction', 'ara/runtime/construction.py',
     "require(not issues, 'content definition", "require(True, 'content definition",
     'tests/runtime/test_content_provenance.py::test_attributed_definition_gets_logged_targeted_correction[symbol]'),
    ('content_source_stance', 'ara/runtime/commitment_provenance.py',
     "'reported_view': 'reported'", "'reported_view': 'endorsed'",
     'tests/runtime/test_content_provenance.py::test_content_stance_and_exact_evidence_survive_freeze'),
    ('content_source_text', 'ara/runtime/commitment_provenance.py',
     "source_text=item['text']", "source_text='P'",
     'tests/runtime/test_content_provenance.py::test_content_stance_and_exact_evidence_survive_freeze'),
    ('content_provenance_hash', 'ara/runtime/commitment_provenance.py',
     "if value['sha256'] != digest(canonical(payload)):", 'if False:',
     'tests/runtime/test_commitment_provenance.py::test_sidecar_refuses_tampering_even_with_recomputed_hash[hash]'),
    ('classifier_content_rendering', 'ara/runtime/target_policy.py',
     "rendered_content=render(target.formula)", "rendered_content=None",
     'tests/runtime/test_stance_search.py::test_classifier_assertion_uses_content_not_source_voice'),
    ('stance_native_admission', 'ara/runtime/orchestration.py',
     "provenance is None or provenance['commitments'][c.id]['stance'] in ('endorsed', 'model_alignment')", 'True',
     'tests/runtime/test_stance_search.py::test_restricted_support_cannot_close_native_route'),
    ('stance_cq_admission', 'ara/engine/search.py',
     'supported = cq_supported(answer, q.id, self.commitments)',
     'supported = cq_supported(answer, q.id, self.frozen_commitments)',
     'tests/runtime/test_stance_search.py::test_restricted_cq_evidence_keeps_native_route_open'),
    ('stance_route_disclosure', 'ara/runtime/route_policy.py',
     "if stance != 'endorsed' and not (stance == 'model_alignment' and role == 'global_premise'):", 'if False:',
     'tests/runtime/test_stance_search.py::test_report_and_selection_disclose_historical_crossing'),
    ('stance_fork_receipt', 'ara/runtime/freeze_fork.py',
     "if receipts != ([provenance] if provenance is not None else []):", 'if False:',
     'tests/runtime/test_stance_search.py::test_fork_preserves_provenance_or_refuses'),
    ('stance_restore_admission', 'ara/runtime/orchestration.py',
     "if any(route.status == 'CLOSED' and stance_crossings(route, provenance) for result, _ in restored.values() for route in result.routes):",
     'if False:',
     'tests/runtime/test_stance_search.py::test_restored_crossing_refused_before_analysis'),
    ('stance_cache_context', 'ara/runtime/search_alignment.py',
     "provenance_sha256=provenance['sha256'] if provenance else None", 'provenance_sha256=None',
     'tests/runtime/test_stance_search.py::test_provenance_tamper_refuses_and_changes_cache_context'),
]


CASES += [
    ('stance_resume_receipt', 'ara/runtime/search_resume.py',
     "require(vocabulary['commitment_provenance'] == provenance_from_events(main, commitments),",
     'require(True,',
     'tests/runtime/test_stance_search.py::test_native_resume_preserves_stance_and_refuses_lost_metadata'),
    ('stance_live_receipt', 'ara/runtime/calls.py',
     "require(vocabulary['commitment_provenance'] == provenance_from_events(events, commitments),",
     'require(True,',
     'tests/runtime/test_stance_search.py::test_native_engine_refuses_deleted_stance_receipt'),
]


CASES += [
    ('stance_writer_outline', 'ara/runtime/calls.py',
     "outline['source_roles'] = roles", 'pass',
     'tests/runtime/test_stance_search.py::test_writer_and_auditor_preserve_source_roles'),
]


CASES += [
    ('construction_window_corrections', 'ara/runtime/construction.py',
     'remaining = dict(select_t_roots=corrections, build_t_batch=corrections)',
     'remaining = dict(select_t_roots=corrections if batch.index == 0 else 0, build_t_batch=corrections if batch.index == 0 else 0)',
     'tests/runtime/test_construction_shares.py::test_corrections_are_per_window_and_per_call_type[2-3]'),
    ('construction_second_correction', 'ara/runtime/construction.py',
     'for correction in range(limit):', 'for correction in range(min(limit, 1)):',
     'tests/runtime/test_content_provenance.py::test_second_correction_keeps_first_patch_and_supplies_specific_feedback'),
    ('construction_accumulated_patch', 'ara/runtime/construction.py',
     'candidate = latest', 'pass',
     'tests/runtime/test_content_provenance.py::test_second_correction_keeps_first_patch_and_supplies_specific_feedback'),
    ('construction_all_definition_feedback', 'ara/runtime/commitment_provenance.py',
     'return issues', 'return issues[:1]',
     'tests/runtime/test_content_provenance.py::test_feedback_names_all_offenders_and_unframed_remainder_is_rechecked'),
    ('construction_exact_unframe', 'ara/runtime/commitment_provenance.py',
     'match = re.fullmatch(', 'match = re.search(',
     'tests/runtime/test_content_provenance.py::test_nonexact_frames_require_model_correction[Not a argues that P]'),
    ('construction_unframe_receipt', 'ara/runtime/construction.py',
     "calls.log.record('definition_unframed',", "calls.log.record('definition_frame_removed',",
     'tests/runtime/test_content_provenance.py::test_exact_frames_unframed_without_model_correction'),
    ('construction_unframe_provenance', 'ara/runtime/construction.py',
     "provenance[id]['definition_unframes'] = retained", 'pass',
     'tests/runtime/test_content_provenance.py::test_exact_frames_unframed_without_model_correction'),
    ('construction_correction_plan_identity', 'ara/runtime/construction.py',
     "'correction_policy': {'scope': 'window_call_type', 'limit': corrections},",
     "'correction_policy': {'scope': 'window_call_type', 'limit': 0},",
     'tests/runtime/test_construction_resume.py::test_resume_refuses_unverified_state_before_dispatch[correction_policy]'),
]


CASES += [
    ('construction_unframe_single_layer', 'ara/runtime/construction.py',
     'data = deepcopy(data)', 'data = data',
     'tests/runtime/test_content_provenance.py::test_unframing_does_not_peel_nested_frames_across_corrections'),
]


CASES += [
    ('construction_active_feedback', 'ara/runtime/construction.py',
     "candidate_error + '; correction rejected: '", "'' + '; correction rejected: '",
     'tests/runtime/test_content_provenance.py::test_invalid_patch_keeps_active_definition_feedback'),
    ('target_pool_size', 'ara/runtime/calls.py',
     "pool_count = 1 if named_position is not None else 30", "pool_count = 1 if named_position is not None else 10",
     'tests/runtime/test_target_pool.py::test_pool_keeps_thirty_in_stable_order'),
    ('target_pool_limit', 'ara/runtime/calls.py',
     "keep_count = 1 if named_position is not None else min(count, 30)", "keep_count = 1 if named_position is not None else 20",
     'tests/runtime/test_target_pool.py::test_pool_keeps_thirty_in_stable_order'),
    ('target_pool_survivors', 'ara/runtime/calls.py',
     "        return tuple(kept)\n\n    def propose_cuts", "        return tuple(kept[-1:])\n\n    def propose_cuts",
     'tests/runtime/test_target_pool.py::test_two_corrections_preserve_survivors_and_give_witnesses'),
    ('target_concrete_witness', 'ara/runtime/target_policy.py',
     "entailing_commitment=witness.to_dict() if witness else None", "entailing_commitment=None",
     'tests/runtime/test_target_pool.py::test_two_corrections_preserve_survivors_and_give_witnesses'),
    ('target_bank_guidance', 'ara/runtime/target_policy.py',
     "bank=[b.to_dict() for b in bank.entries]", "bank=[]",
     'tests/runtime/test_target_pool.py::test_pool_keeps_thirty_in_stable_order'),
    ('target_new_vocabulary', 'ara/runtime/calls.py',
     "                if reasons:", "                if reasons or target.id in disconnected:",
     'tests/runtime/test_target_pool.py::test_native_new_atom_defeasible_closure'),
    ('target_defeasible_reachability', 'ara/engine/licensing.py',
     "if entry.kind == 'deductive':", "if True:",
     'tests/runtime/test_target_pool.py::test_native_new_atom_defeasible_closure'),
]



CASES += [
    ('novelty_target_wiring', 'ara/runtime/target_policy.py',
     "if reason is None and novelty['status'] != 'candidate':", "if False:",
     'tests/runtime/test_novelty_policy.py::test_boolean_feedback_and_bank_guidance_reach_correction'),
    ('novelty_essential_relevance', 'ara/runtime/novelty.py',
     "changed |= result == 'SOLVER_COUNTEREXAMPLE'", "changed = True",
     'tests/runtime/test_semantic_novelty.py::test_new_atom_must_change_truth_under_t'),
    ('novelty_deductive_closure', 'ara/runtime/novelty.py',
     "if result == 'SOLVER_UNSAT':", "if False:",
     'tests/runtime/test_semantic_novelty.py::test_quantified_deductive_consequence_is_not_novel'),
    ('novelty_unknown_refusal', 'ara/runtime/novelty.py',
     "if result != 'SOLVER_COUNTEREXAMPLE':", "if result == 'SOLVER_UNSAT':",
     'tests/runtime/test_novelty_policy.py::test_novelty_unknown_refuses'),
    ('novelty_structural_label', 'ara/runtime/route_policy.py',
     "elif not substantive:", "elif False:",
     'tests/runtime/test_novelty_policy.py::test_only_known_nonstructural_scheme_counts'),
    ('novelty_reachable_substantive', 'ara/runtime/route_policy.py',
     "substantive = []", "substantive = [dict(node_id=n.id, bank_id=n.proposal.bank_id) for n in route.nodes if n.proposal and n.proposal.bank_id == 'sign']",
     'tests/runtime/test_semantic_novelty.py::test_only_reachable_step_with_root_essential_proposition_qualifies'),
    ('novelty_bank_guidance', 'ara/runtime/target_policy.py',
     "substantive_bank_ids=[b.id for b in bank.entries if b.kind == 'defeasible']", "substantive_bank_ids=[]",
     'tests/runtime/test_novelty_policy.py::test_boolean_feedback_and_bank_guidance_reach_correction'),
]


CASES += [
    ('semantic_essential_timeout', 'ara/runtime/novelty.py',
     "if result not in ('SOLVER_UNSAT', 'SOLVER_COUNTEREXAMPLE'):", 'if False:',
     'tests/runtime/test_semantic_novelty.py::test_unknown_essential_check_refuses'),
    ('semantic_root_proposition', 'ara/runtime/route_policy.py',
     "if essential.intersection(conclusion.get('essential_application_keys', ())):", "if conclusion['status'] == 'candidate':",
     'tests/runtime/test_semantic_novelty.py::test_only_reachable_step_with_root_essential_proposition_qualifies'),
    ('semantic_whole_freeze', 'ara/runtime/route_policy.py',
     'basis = commitments or CommitmentSet(tuple(supports.values()))', 'basis = CommitmentSet(tuple(supports.values()))',
     'tests/runtime/test_semantic_novelty.py::test_only_reachable_step_with_root_essential_proposition_qualifies'),
    ('semantic_unused_assumption', 'ara/runtime/route_policy.py',
     "b.kind == 'defeasible'", "b.kind == 'defeasible' or b.id == 'conditional_proof'",
     'tests/runtime/test_semantic_novelty.py::test_unused_conditional_proof_not_counted_but_new_sign_result_qualifies'),
    ('content_definition_wiring', 'ara/runtime/calls.py',
     "for issue in content['definition_issues']:", 'for issue in ():',
     'tests/runtime/test_semantic_novelty.py::test_definition_equality_and_near_duplicate_rejected'),
    ('content_normalized_equality', 'ara/runtime/target_content.py',
     '(a == b or (min(len(a),len(b)) >= 20 and', '(False or (min(len(a),len(b)) >= 20 and',
     'tests/runtime/test_semantic_novelty.py::test_definition_equality_and_near_duplicate_rejected'),
    ('content_near_duplicate', 'ara/runtime/target_content.py',
     'min(len(a),len(b)) >= 20 and', 'False and',
     'tests/runtime/test_semantic_novelty.py::test_definition_equality_and_near_duplicate_rejected'),
    ('content_model_novelty', 'ara/runtime/calls.py',
     "classification['novelty'] != 'new_assertion' or", 'False or',
     'tests/runtime/test_semantic_novelty.py::test_logged_content_judgment_is_required'),
    ('content_model_fidelity', 'ara/runtime/calls.py',
     "or classification['fidelity'] != 'matches':", 'or False:',
     'tests/runtime/test_semantic_novelty.py::test_logged_content_judgment_is_required'),
    ('content_frozen_list', 'ara/runtime/target_policy.py',
     "frozen_content=content['frozen_content']", 'frozen_content=[]',
     'tests/runtime/test_semantic_novelty.py::test_logged_content_judgment_is_required'),
    ('content_binding_codec', 'ara/types.py',
     'if not self.new_symbols:', 'if True:',
     'tests/runtime/test_semantic_novelty.py::test_explicit_definition_binding_survives_codec_and_cache'),
    ('content_missing_binding', 'ara/runtime/target_content.py',
     'for key in used - frozen - definitions.keys() - proposed.keys():', 'for key in ():',
     'tests/runtime/test_semantic_novelty.py::test_compound_definition_bindings_refuse_missing_or_changed_meanings'),
]

CASES += [
    ('semantic_unused_binder_identity', 'ara/runtime/novelty.py',
     "variables.setdefault(term.name, len(variables))", "bound[::-1].index(term.name)",
     'tests/runtime/test_semantic_novelty.py::test_unused_binder_does_not_make_bound_application_new'),
]

CASES += [
    ('semantic_step_unknown_display', 'ara/runtime/route_policy.py',
     "if any(s.get('novelty', {}).get('status') == 'unresolved' for s in step_checks)", 'if False',
     'tests/runtime/test_semantic_novelty.py::test_uncertain_step_novelty_is_disclosed_and_not_derived'),
]


CASES += [
    ('nonlogical_padded_conclusion', 'ara/runtime/novelty.py', "if verdict == 'SOLVER_UNSAT':\n            return result('rejected','single_paper_closure'", "if False:\n            return result('rejected','single_paper_closure'", 'tests/runtime/test_nonlogical_contribution.py::test_native_only_new_scheme_conclusion_qualifies[padded]'),
    ('nonlogical_syllogism_conclusion', 'ara/runtime/novelty.py', "if verdict == 'SOLVER_UNSAT':\n            return result('rejected','single_paper_closure'", "if False:\n            return result('rejected','single_paper_closure'", 'tests/runtime/test_nonlogical_contribution.py::test_native_only_new_scheme_conclusion_qualifies[syllogism]'),
    ('nonlogical_bank_kinds', 'ara/runtime/route_policy.py',
     "b.kind == 'defeasible'", 'True',
     'tests/runtime/test_novelty_policy.py::test_only_known_nonstructural_scheme_counts'),
    ('automatic_binding_collision', 'ara/runtime/target_content.py',
     'bind(key, target.text)', 'proposed[key] = target.text',
     'tests/runtime/test_nonlogical_contribution.py::test_automatic_and_explicit_bindings_share_collision_policy'),
]

CASES += [
    ('lexical_hit_receipt', 'ara/runtime/calls.py',
     "hits=content['lexical_attribution_hits']", 'hits=[]',
     'tests/runtime/test_search_guidance.py::test_own_voice_lexical_hits_are_advisory_through_selection'),
    ('lexical_classifier_evidence', 'ara/runtime/target_policy.py',
     "lexical_attribution_hits=attribution_hits(target, vocabulary['symbol_catalogue'])", 'lexical_attribution_hits=[]',
     'tests/runtime/test_search_guidance.py::test_own_voice_lexical_hits_are_advisory_through_selection'),
    ('lexical_advisory_selection', 'ara/runtime/route_policy.py',
     'if leading_report_frame(root.text):', "if leading_report_frame(root.text) or 'account' in root.text:",
     'tests/runtime/test_search_guidance.py::test_own_voice_lexical_hits_are_advisory_through_selection'),
    ('cut_correction_budget', 'ara/engine/search.py',
     'for attempt in range(2):', 'for attempt in range(1):',
     'tests/runtime/test_search_guidance.py::test_native_new_atom_guidance_and_one_concrete_correction'),
    ('cut_validation_budget', 'ara/runtime/calls.py',
     "self._transport_call('propose_cuts', inputs, check, attempt=inputs['attempt'])", "self.call('propose_cuts', inputs, check)",
     'tests/runtime/test_search_guidance.py::test_empty_batches_exhaust_one_correction[True]'),
    ('cut_correction_feedback', 'ara/runtime/calls.py',
     'rejection_feedback=list(feedback)', 'rejection_feedback=[]',
     'tests/runtime/test_search_guidance.py::test_native_new_atom_guidance_and_one_concrete_correction'),
    ('leaf_scheme_guidance', 'ara/runtime/search_alignment.py',
     "for b in bank if b.kind == 'defeasible'", "for b in bank if False",
     'tests/runtime/test_search_guidance.py::test_native_new_atom_guidance_and_one_concrete_correction'),
]


CASES += [
    ('cross_paper_classification', 'ara/runtime/route_policy.py',
     "elif not papers['cross_paper_supported']:", 'elif False:',
     'tests/runtime/test_cross_paper.py::test_native_cross_paper_selection_and_report'),
    ('cross_paper_missing_identity', 'ara/runtime/route_policy.py',
     "if papers['status'] != 'verified':", 'if False:',
     'tests/runtime/test_cross_paper.py::test_unknown_paper_identity_and_unreachable_support_do_not_upgrade'),
    ('cross_paper_source_identity', 'ara/runtime/bridges.py',
     "sources = {tid: rows.get(tid, {}).get('source_id') for tid in support_ids}",
     "sources = {tid: rows.get(tid, {}).get('evidence_id') for tid in support_ids}",
     'tests/runtime/test_cross_paper.py::test_native_cross_paper_selection_and_report'),
    ('bridge_distinct_papers', 'ara/runtime/bridges.py',
     'by_paper[papers[tid]].append(tid)', 'by_paper[tid].append(tid)',
     'tests/runtime/test_cross_paper.py::test_bridges_are_deterministic_cross_paper_pairs_and_triples'),
    ('bridge_catalogue_connection', 'ara/runtime/bridges.py',
     "features[c.id] = {('symbol',*s) for s in used} | {('definition_term',t) for t in terms}",
     "features[c.id] = {('symbol','P','atom',0)}",
     'tests/runtime/test_cross_paper.py::test_bridges_are_deterministic_cross_paper_pairs_and_triples'),
    ('bridge_stance_filter', 'ara/runtime/bridges.py',
     "rows.get(c.id, {}).get('stance') == 'endorsed'", 'True',
     'tests/runtime/test_cross_paper.py::test_bridge_bounds_and_restricted_stances'),
    ('bridge_candidate_bounds', 'ara/runtime/bridges.py',
     'pairs_limit=30, triples_limit=30', 'pairs_limit=31, triples_limit=31',
     'tests/runtime/test_cross_paper.py::test_bridge_bounds_and_restricted_stances'),
    ('bridge_scoped_premise', 'ara/runtime/bridges.py',
     "p.t_id != 'open' and p.scope_id is None", "p.t_id != 'open'",
     'tests/runtime/test_cross_paper.py::test_bridge_bounds_and_restricted_stances'),
    ('bridge_slot_paper_receipt', 'ara/runtime/bridges.py',
     'paper_id=papers.get(p.t_id)', 'paper_id=None',
     'tests/runtime/test_cross_paper.py::test_bridge_guidance_reaches_target_and_cut_with_slot_paper_receipt'),
    ('target_paper_requirement', 'ara/runtime/target_policy.py',
     'minimum_support_papers=2', 'minimum_support_papers=1',
     'tests/runtime/test_cross_paper.py::test_bridge_guidance_reaches_target_and_cut_with_slot_paper_receipt'),
]


CASES += [
    ('cross_paper_all_formula_provenance', 'ara/runtime/route_policy.py',
     'supports.setdefault(formula_hash(commitment.formula), {})[commitment.id] = commitment',
     'supports.setdefault(formula_hash(commitment.formula), {commitment.id: commitment})',
     'tests/runtime/test_cross_paper.py::test_reversed_cq_order_preserves_all_formula_paper_provenance'),
    ('cross_paper_matching_distinct_papers', 'ara/runtime/bridges.py',
     'if a != b), None)', 'if True), None)',
     'tests/runtime/test_cross_paper.py::test_distinct_formula_paper_matching'),
    ('cross_paper_matching_distinct_formulas', 'ara/runtime/bridges.py',
     'for left, right in combinations(groups, 2):', 'for left, right in product(groups, repeat=2):',
     'tests/runtime/test_cross_paper.py::test_distinct_formula_paper_matching'),
]


CASES += [
    ('leaf_bridge_relevance', 'ara/runtime/search_context.py',
     '-len(leaf_symbols.intersection', 'len(leaf_symbols.intersection',
     'tests/runtime/test_search_context.py::test_leaf_context_selects_ranked_bridges_and_referenced_catalogue'),
    ('leaf_bridge_bound', 'ara/runtime/search_context.py',
     "b['bridge_id']))[:bridge_limit]", "b['bridge_id']))[:]",
     'tests/runtime/test_search_context.py::test_leaf_context_selects_ranked_bridges_and_referenced_catalogue'),
    ('leaf_catalogue_slice', 'ara/runtime/search_context.py',
     "if (s['name'], s['kind'], s['arity']) in referenced", 'if True',
     'tests/runtime/test_search_context.py::test_leaf_context_recounts_and_shrinks_before_dispatch'),
    ('leaf_context_shrink', 'ara/runtime/search_context.py',
     'for bridge_limit in (8, 4, 2, 1, 0):', 'for bridge_limit in (8,):',
     'tests/runtime/test_search_context.py::test_leaf_context_recounts_and_shrinks_before_dispatch'),
    ('leaf_context_output_allowance', 'ara/runtime/search_context.py',
     'total = count.initial_input_tokens + count.context_output_tokens', 'total = count.initial_input_tokens',
     'tests/runtime/test_search_context.py::test_leaf_context_recounts_and_shrinks_before_dispatch'),
    ('search_context_local_scope', 'ara/runtime/calls.py',
     "'search' if kind in SEARCH_STAGES or", "'run' if kind in SEARCH_STAGES or",
     'tests/runtime/test_search_context.py::test_context_refusal_is_job_local_and_preserves_other_searches'),
]


CASES += [
    ('leaf_all_exact_matches', 'ara/runtime/search_context.py',
     '[c for c in commitments.commitments if c.formula == formula]',
     '[c for c in commitments.commitments if c.formula == formula][:1]',
     'tests/runtime/test_search_context.py::test_all_exact_leaf_evidence_survives_bridges_and_shrinking'),
    ('leaf_endorsed_exact_first', 'ara/runtime/search_context.py',
     "roles.get(c.id, {}).get('stance') != 'endorsed'", 'False',
     'tests/runtime/test_search_context.py::test_all_exact_leaf_evidence_survives_bridges_and_shrinking'),
]


CASES += [
    ('cq_rank_symbols', 'ara/runtime/cq_context.py', "-r['shared_symbols']", "r['shared_symbols']", 'tests/runtime/test_cq_retrieval.py::test_cq_retrieves_outside_premises_ranks_and_shrinks'),
    ('cq_endorsed_retrieval', 'ara/runtime/cq_context.py', "if provenance is not None and rows[c.id]['stance'] != 'endorsed':", 'if False:', 'tests/runtime/test_cq_retrieval.py::test_retrieval_excludes_restricted_evidence_but_full_T_ids_remain_valid'),
    ('cq_bound_retrieval', 'ara/runtime/cq_context.py', 'candidates = ranked[:limit]', 'candidates = ranked', 'tests/runtime/test_cq_retrieval.py::test_cq_retrieves_outside_premises_ranks_and_shrinks'),
    ('cq_output_allowance', 'ara/runtime/cq_context.py', 'total = count.initial_input_tokens + count.context_output_tokens', 'total = count.initial_input_tokens', 'tests/runtime/test_cq_retrieval.py::test_cq_retrieves_outside_premises_ranks_and_shrinks'),
    ('cq_lexical_retrieval', 'ara/runtime/cq_context.py', 'if shared or lexical:', 'if shared:', 'tests/runtime/test_cq_retrieval.py::test_cq_lexical_overlap_retrieves_definitions_without_shared_symbols'),
    ('cq_partial_downgrade', 'ara/runtime/calls.py', 'if answer.answered and partial_cq(answer.answer):', 'if False:', 'tests/runtime/test_cq_retrieval.py::test_partial_cq_is_disclosed_and_not_supported'),
    ('cq_partial_engine', 'ara/engine/routes.py', 'and not partial_cq(answer.answer)', 'and True', 'tests/runtime/test_cq_retrieval.py::test_retrieval_excludes_restricted_evidence_but_full_T_ids_remain_valid'),
    ('cq_scheme_retry', 'ara/engine/search.py', 'if not feedback:\n            return', 'if True:\n            return', 'tests/runtime/test_cq_retrieval.py::test_unsupported_cq_gets_one_different_scheme_correction'),
    ('cq_different_scheme', 'ara/engine/search.py', 'if proposal.bank_id not in {b.id for b in remaining}:', 'if False:', 'tests/runtime/test_cq_retrieval.py::test_unsupported_cq_gets_one_different_scheme_correction'),
    ('gap_contradictions', 'ara/runtime/gaps.py', "return verdict=='SOLVER_UNSAT'", 'return False', 'tests/runtime/test_gaps.py::test_gap_set_witness_and_same_paper_negative'),
    ('gap_stance_conflict', 'ara/runtime/gaps.py', "if (a.formula.canonical()==b.formula.canonical() or a.text==b.text\n                        or (provenance.get('definition_semantics') == 'content' and content[a.id]==content[b.id])):", 'if False:', 'tests/runtime/test_gaps.py::test_gap_kinds_and_stance_are_deterministic'),
    ('gap_open_problem', 'ara/runtime/gaps.py', 'if any(_OPEN.search(text) for text in (a.text,*definitions)):', 'if False:', 'tests/runtime/test_gaps.py::test_gap_kinds_and_stance_are_deterministic'),
    ('gap_side_support', 'ara/runtime/gaps.py', 'supported=bool(witnesses) and all(witnesses)', 'supported=True', 'tests/runtime/test_gaps.py::test_gap_targets_first_persist_and_require_both_sides'),
    ('gap_target_binding', 'ara/types.py', 'if self.gap is None:', 'if True:', 'tests/runtime/test_gaps.py::test_gap_targets_first_persist_and_require_both_sides'),
    ('gap_resolving_thesis', 'ara/runtime/calls.py', "if target.gap is not None and classification.get('resolves_gap') is not True:", 'if False:', 'tests/runtime/test_gaps.py::test_unrelated_thesis_is_not_retained_as_resolution'),
    ('alignment_candidate_limit', 'ara/runtime/symbol_alignment.py',
     'selected=nsmallest(max(1,limit),scored(),key=_rank)[:limit]', 'selected=nsmallest(1000000,scored(),key=_rank)',
     'tests/runtime/test_symbol_alignment.py::test_candidates_are_bounded_cross_source_content_pairs'),
    ('alignment_cross_source', 'ara/runtime/symbol_alignment.py',
     ' or papers[a] & papers[b]', '',
     'tests/runtime/test_symbol_alignment.py::test_candidates_are_bounded_cross_source_content_pairs'),
    ('alignment_signature', 'ara/runtime/symbol_alignment.py',
     "(left['kind'],left['arity']) != (right['kind'],right['arity'])):", 'False):',
     'tests/runtime/test_symbol_alignment.py::test_predicate_arity_and_symbol_type_are_not_interchangeable'),
    ('alignment_canonical_rewrite', 'ara/runtime/symbol_alignment.py',
     'formula=_rewrite(c.formula,mapping)', 'formula=c.formula',
     'tests/runtime/test_symbol_alignment.py::test_same_content_rewrites_transitively_and_keeps_originals'),
    ('alignment_no_invention', 'ara/runtime/symbol_alignment.py',
     "if j['relation']=='same_content':", 'if True:',
     'tests/runtime/test_symbol_alignment.py::test_unrelated_and_zero_limit_never_invent_alignment'),
    ('alignment_consistency', 'ara/runtime/symbol_alignment.py',
     "if any(j['relation']!='unrelated' for j in judgments) and not _consistent(result):", 'if False:',
     'tests/runtime/test_symbol_alignment.py::test_refused_alignment_is_logged_and_preserves_original_T'),
    ('alignment_unknown', 'ara/runtime/symbol_alignment.py',
     "=='SOLVER_COUNTEREXAMPLE'", "!='SOLVER_UNSAT'",
     'tests/runtime/test_symbol_alignment.py::test_solver_unknown_refuses_alignment'),
    ('alignment_stance', 'ara/runtime/symbol_alignment.py',
     "kind='alignment',stance='model_alignment'", "kind='alignment',stance='endorsed'",
     'tests/runtime/test_symbol_alignment.py::test_bridges_are_explicit_quantified_model_alignment'),
    ('alignment_quantifier', 'ara/runtime/symbol_alignment.py',
     'for variable in reversed(variables):', 'for variable in []:',
     'tests/runtime/test_symbol_alignment.py::test_bridges_are_explicit_quantified_model_alignment'),
    ('alignment_replay_mapping', 'ara/runtime/symbol_alignment.py',
     " or receipt['mapping']!=mapping", '',
     'tests/runtime/test_symbol_alignment.py::test_native_freeze_persists_alignment_receipt_and_validates_replay'),
    ('alignment_native_pipeline', 'ara/runtime/orchestration.py',
     "align_symbols(calls, commitments, latest['symbols'], latest['provenance'])", "(commitments, latest['symbols'], latest['provenance'], None)",
     'tests/runtime/test_symbol_alignment.py::test_native_freeze_persists_alignment_receipt_and_validates_replay'),
    ('alignment_stage_identity', 'ara/runtime/construction_stages.py',
     "return dispatch_settings(config, 'build_t_batch', correction=False)", "return dispatch_settings(config, 'build_t_batch', correction=correction)",
     'tests/runtime/test_symbol_alignment.py::test_alignment_uses_construction_provider_even_on_retry'),
    ('alignment_native_admission', 'ara/runtime/orchestration.py',
     "in ('endorsed', 'model_alignment')", "in ('endorsed',)",
     'tests/runtime/test_symbol_alignment.py::test_native_search_alignment_is_disclosed_and_needs_two_endorsed_sources'),
    ('alignment_endorsed_supports', 'ara/runtime/route_policy.py',
     "if alignment_ids and len(endorsed_ids) < 2 and route.status == 'CLOSED':", 'if False:',
     'tests/runtime/test_symbol_alignment.py::test_native_search_alignment_is_disclosed_and_needs_two_endorsed_sources'),
    ('alignment_no_paper', 'ara/runtime/bridges.py',
     "if rows.get(tid, {}).get('stance') != 'model_alignment'", 'if True',
     'tests/runtime/test_symbol_alignment.py::test_native_search_alignment_is_disclosed_and_needs_two_endorsed_sources'),
    ('alignment_leaf_leads', 'ara/runtime/search_context.py',
     "selected.update(c.id for c in [c for c in ranked if roles.get(c.id, {}).get('stance') == 'model_alignment'][:bridge_limit])", 'selected.update([])',
     'tests/runtime/test_symbol_alignment.py::test_native_search_alignment_is_disclosed_and_needs_two_endorsed_sources'),
    ('alignment_cq_evidence', 'ara/runtime/calls.py',
     "require(provenance is None or all(provenance['commitments'][t]['stance'] != 'model_alignment'", 'require(provenance is None or all(True',
     'tests/runtime/test_symbol_alignment.py::test_alignment_bridge_cannot_be_source_cq_evidence'),
    ('alignment_final_catalogue', 'ara/runtime/report.py',
     "catalogues[-1]['symbols'] if catalogues else merged[-1].get('symbols') if merged else None", "merged[-1].get('symbols') if merged else None",
     'tests/runtime/test_symbol_alignment.py::test_canonical_freeze_report_uses_final_catalogue_and_retains_unframe_history'),
    ('alignment_outline_disclosure', 'ara/runtime/calls.py',
     "outline['alignment_disclosure'] = alignment_disclosure(provenance)", "outline['alignment_disclosure'] = {}",
     'tests/runtime/test_symbol_alignment.py::test_native_search_alignment_is_disclosed_and_needs_two_endorsed_sources'),
]


CASES += [
    ('cq_trace_retry_indices', 'ara/engine/search.py', "last_index = payload['proposal_index']", 'last_index = -1', 'tests/runtime/test_cq_retrieval.py::test_unsupported_cq_gets_one_different_scheme_correction'),
    ('gap_trace_metadata', 'ara/engine/tracing.py', "encoded_node['proposition'] = dict(**proposition_metadata(node.proposition),", "encoded_node['proposition'] = dict(id=node.proposition.id,", 'tests/runtime/test_gaps.py::test_gap_targets_first_persist_and_require_both_sides'),
]


CASES += [('gap_open_marker_coverage', 'ara/runtime/gaps.py', '|is open|problem remains|jury is out', '', 'tests/runtime/test_gaps.py::test_explicit_open_markers_beyond_unresolved')]


CASES += [
    ('semantic_cross_paper', 'ara/runtime/semantic_conflicts.py', "if rows[a.id]['source_id'] == rows[b.id]['source_id']:", 'if False:', 'tests/runtime/test_semantic_conflicts.py::test_ranked_pairs_cross_paper_private_symbols_and_roles'),
    ('semantic_endorsed_side', 'ara/runtime/semantic_conflicts.py', "if 'endorsed' not in (rows[a.id]['stance'], rows[b.id]['stance']):", 'if False:', 'tests/runtime/test_semantic_conflicts.py::test_ranked_pairs_cross_paper_private_symbols_and_roles'),
    ('semantic_pair_limit', 'ara/runtime/semantic_conflicts.py', 'nsmallest(limit, candidates(),', 'nsmallest(limit + 1, candidates(),', 'tests/runtime/test_semantic_conflicts.py::test_pair_limit_and_context_refusal_are_disclosed'),
    ('semantic_labels', 'ara/runtime/semantic_conflicts.py', "if result['classification'] not in ('contradicts', 'in_tension'):", 'if False:', 'tests/runtime/test_semantic_conflicts.py::test_isolated_classification_cache_gap_and_immutable_freeze'),
    ('semantic_resolution_stance', 'ara/runtime/semantic_conflicts.py', "and rows[c.id]['stance'] == 'endorsed'", 'and True', 'tests/runtime/test_semantic_conflicts.py::test_isolated_classification_cache_gap_and_immutable_freeze'),
    ('semantic_isolated_topic', 'ara/runtime/semantic_conflicts.py', "inputs = dict(topic='', pair=pair,", 'inputs = dict(pair=pair,', 'tests/runtime/test_semantic_conflicts.py::test_isolated_classification_cache_gap_and_immutable_freeze'),
    ('semantic_target_wiring', 'ara/runtime/calls.py', "detection['gaps'] + support_gaps + classify_pairs(self, commitments, vocabulary)", "detection['gaps']", 'tests/runtime/test_semantic_conflicts.py::test_semantic_gap_drives_resolution_proposal'),
    ('semantic_context_local', 'ara/runtime/search_context.py', ", 'classify_conflict'", '', 'tests/runtime/test_semantic_conflicts.py::test_pair_limit_and_context_refusal_are_disclosed'),
    ('tier2_resolution_wiring', 'ara/runtime/orchestration.py', '        propose_tier2_resolutions(calls, paired, commitments, provenance)', '        pass', 'tests/runtime/test_semantic_conflicts.py::test_native_tiers_report_and_resolution_proposal'),
    ('tier2_route_evidence', 'ara/runtime/conflict_feedback.py', 'route_ids=route_ids, finding=', 'route_ids=(), finding=', 'tests/runtime/test_semantic_conflicts.py::test_native_tiers_report_and_resolution_proposal'),
    ('tier_report_findings', 'ara/runtime/conflict_feedback.py', 'for a in analyses for finding in a.get(tier, [])', 'for a in [] for finding in a.get(tier, [])', 'tests/runtime/test_semantic_conflicts.py::test_native_tiers_report_and_resolution_proposal'),
    ('tier_report_section', 'ara/runtime/report_render.py', "'Tier 1 repairs and Tier 2 conflicts'", "'Findings'", 'tests/runtime/test_semantic_conflicts.py::test_native_tiers_report_and_resolution_proposal'),
]


CASES += [
    ('semantic_pair_ranking', 'ara/runtime/semantic_conflicts.py', "-p['topic_overlap']", "p['topic_overlap']", 'tests/runtime/test_semantic_conflicts.py::test_pair_limit_and_context_refusal_are_disclosed'),
    ('tier_report_generation', 'ara/runtime/conflict_feedback.py', "if i > boundary and e['stage']=='conflicts_and_robustness'", "if e['stage']=='conflicts_and_robustness'", 'tests/runtime/test_semantic_conflicts.py::test_report_does_not_reuse_findings_from_prior_search_generation'),
    ('tier_resolution_generation', 'ara/runtime/conflict_feedback.py', "if i > finding_index and e['stage']=='tier2_resolution_candidates'", "if e['stage']=='tier2_resolution_candidates'", 'tests/runtime/test_semantic_conflicts.py::test_report_does_not_reuse_findings_from_prior_search_generation'),
]


CASES += [('tier2_distinct_support_groups', 'ara/runtime/conflict_feedback.py', 'groups = tuple(supports[rid] for rid in route_ids)', 'groups = tuple(supports[route_ids[0]] for rid in route_ids)', 'tests/runtime/test_semantic_conflicts.py::test_tier2_keeps_each_routes_distinct_support_group')]


CASES += [('cq_formatted_hedge_native', 'ara/engine/routes.py', "words = ' '.join(re.findall(r'[^\\W_]+', unicodedata.normalize('NFKC', text).casefold()))", 'words = text', 'tests/runtime/test_cq_retrieval.py::test_formatted_hedge_cannot_close_native_route'), ('gap_frozen_content_identity', 'ara/runtime/gaps.py', 'and content[a.id]==content[b.id]', 'and False', 'tests/runtime/test_gaps.py::test_frozen_definition_stance_conflict_reaches_native_proposal'), ('gap_content_structure', 'ara/runtime/gaps.py', "value['args'] = [frozen_content_key(child, definitions) for child in formula.args]", 'value = frozen_content_key(formula.args[0], definitions)', 'tests/runtime/test_gaps.py::test_definition_conflict_preserves_structure_arguments_and_polarity')]


CASES += [('per_paper_target_wiring', 'ara/runtime/target_policy.py', 'novelty_check(target.formula, commitments, provenance, basis_ids=required)', 'novelty_check(target.formula, commitments)', 'tests/runtime/test_per_paper_synthesis.py::test_native_deductive_synthesis_proposal_selection_and_report'), ('per_paper_closure', 'ara/runtime/novelty.py', "if verdict == 'SOLVER_UNSAT':\n            return result('rejected','single_paper_closure'", "if False:\n            return result('rejected','single_paper_closure'", 'tests/runtime/test_per_paper_synthesis.py::test_per_paper_closure_groups_and_padding'), ('per_paper_stance', 'ara/runtime/novelty.py', "if row.get('stance') == 'endorsed' and row.get('source_id'):", "if row.get('source_id'):", 'tests/runtime/test_per_paper_synthesis.py::test_reported_opposition_does_not_remove_forward_synthesis'), ('per_paper_essential', 'ara/runtime/novelty.py', '        if known:\n            continue', '        if False:\n            continue', 'tests/runtime/test_per_paper_synthesis.py::test_per_paper_closure_groups_and_padding'), ('per_paper_unknown', 'ara/runtime/novelty.py', "if verdict != 'SOLVER_COUNTEREXAMPLE':\n            return result('unresolved'", "if False:\n            return result('unresolved'", 'tests/runtime/test_per_paper_synthesis.py::test_per_paper_unknown_is_not_novel'), ('synthesis_deductive_upgrade', 'ara/runtime/route_policy.py', "classification='CLOSED-derived', contribution_kind=(", "classification='CLOSED-structural', contribution_kind=(", 'tests/runtime/test_per_paper_synthesis.py::test_native_deductive_synthesis_proposal_selection_and_report'), ('synthesis_reachable_license', 'ara/runtime/route_policy.py', "and papers['cross_paper_supported'] and license_receipt['licensed']", "and papers['cross_paper_supported'] and True", 'tests/runtime/test_per_paper_synthesis.py::test_unlicensed_or_unreachable_step_cannot_supply_synthesis'), ('forward_target_wiring', 'ara/runtime/calls.py', "inputs['forward_candidates'] = proposal_forward_candidates(self, commitments, vocabulary)", "inputs['forward_candidates'] = []", 'tests/runtime/test_per_paper_synthesis.py::test_native_deductive_synthesis_proposal_selection_and_report'), ('forward_endorsed_evidence', 'ara/runtime/synthesis.py', "if rows[c.id]['stance'] in ('endorsed','model_alignment')", 'if True', 'tests/runtime/test_per_paper_synthesis.py::test_forward_uses_native_licenses_and_endorsed_dependencies'), ('forward_endorsed_opposition', 'ara/runtime/synthesis.py', 'tuple(c.formula for c in eligible.commitments), eligible,', 'tuple(c.formula for c in eligible.commitments), commitments,', 'tests/runtime/test_per_paper_synthesis.py::test_reported_opposition_does_not_remove_forward_synthesis'), ('forward_dependency_provenance', 'ara/runtime/synthesis.py', 'ids = set().union(*(dependencies.get(p,set()) for p in premise_keys))', 'ids = set(dependencies.get(premise_keys[0],set()))', 'tests/runtime/test_per_paper_synthesis.py::test_native_deductive_synthesis_proposal_selection_and_report')]


CASES += [('per_paper_compound_package', 'ara/runtime/novelty_basis.py', 'return boolean_combination_equivalence(basis, target, 1000)', "return 'SOLVER_COUNTEREXAMPLE'", 'tests/runtime/test_per_paper_synthesis.py::test_conditional_premise_package_is_not_a_synthesis'), ('synthesis_mixed_inference', 'ara/runtime/route_policy.py', "if (novelty['status'] == 'candidate'\n                and papers", "if (novelty['status'] == 'candidate' and union == 'SOLVER_UNSAT'\n                and papers", 'tests/runtime/test_per_paper_synthesis.py::test_mixed_native_inference_and_recorded_forward_candidates'), ('forward_recorded_results', 'ara/runtime/synthesis.py', "candidates.extend(recorded)", 'pass', 'tests/runtime/test_per_paper_synthesis.py::test_mixed_native_inference_and_recorded_forward_candidates'), ('forward_recorded_generation', 'ara/runtime/synthesis.py', "if i > boundary and e['stage']=='conflicts_and_robustness'", "if e['stage']=='conflicts_and_robustness'", 'tests/runtime/test_per_paper_synthesis.py::test_mixed_native_inference_and_recorded_forward_candidates'), ('forward_recorded_source', 'ara/runtime/synthesis.py', "or freezes[-1][1]['commitments']!=commitments.to_dict()", '', 'tests/runtime/test_per_paper_synthesis.py::test_mixed_native_inference_and_recorded_forward_candidates'), ('forward_recorded_cache', 'ara/runtime/synthesis.py', '[p.to_dict() for p in observed]', '[]', 'tests/runtime/test_per_paper_synthesis.py::test_mixed_native_inference_and_recorded_forward_candidates')]


CASES += [
    ('alignment_durable_refusal', 'ara/runtime/symbol_alignment.py',
     "if receipt['status']=='refused' and receipt['refusal_reason']==CONSISTENCY_REFUSAL:", 'if False:',
     'tests/runtime/test_symbol_alignment.py::test_recorded_solver_refusal_remains_loadable_when_solver_later_resolves'),
]



CASES += [
    ('alignment_forward_premises', 'ara/runtime/synthesis.py',
     "if rows[c.id]['stance'] in ('endorsed','model_alignment')", "if rows[c.id]['stance']=='endorsed'",
     'tests/runtime/test_per_paper_synthesis.py::test_alignment_forward_uses_bridges_without_paper_ownership'),
    ('alignment_not_source_conflict', 'ara/runtime/semantic_conflicts.py',
     "if rows[c.id]['stance'] != 'model_alignment'", 'if True',
     'tests/runtime/test_per_paper_synthesis.py::test_alignment_forward_uses_bridges_without_paper_ownership'),
    ('external_gap_priority', 'ara/runtime/calls.py',
     "external + detection['gaps']", "detection['gaps'] + external",
     'tests/runtime/test_external_gaps.py::test_external_gap_is_logged_first_bound_and_roundtrips'),
    ('external_gap_endorsed_binding', 'ara/runtime/external_gaps.py',
     "if not group or any(tid not in rows or rows[tid]['stance'] != 'endorsed'\n                                or rows[tid]['source_id'] != paper for tid in group):", "if False:",
     'tests/runtime/test_external_gaps.py::test_external_gap_refuses_invalid_evidence'),
]

CASES += [
    ('external_gap_outline', 'ara/runtime/calls.py',
     "outline['gap_resolution'] = root_gap.to_dict()", "outline['gap_resolution'] = {}",
     'tests/runtime/test_external_gaps.py::test_external_gap_is_logged_first_bound_and_roundtrips'),
    ('external_gap_cli_fork', 'ara/runtime/cli.py',
     "            if args.gap_file is not None:\n                config['gap_file'] = str(args.gap_file.resolve())\n            if args.provider is not None:\n                config['provider'] = args.provider\n            if args.unknown_usage_policy",
     "            if args.provider is not None:\n                config['provider'] = args.provider\n            if args.unknown_usage_policy",
     'tests/runtime/test_external_gaps.py::test_fork_cli_uses_external_gap_file_without_editing_freeze'),
]


CASES += [
    ('s11_source_pair_eligibility', 'ara/runtime/semantic_conflicts.py',
     "if rows[c.id]['stance'] != 'model_alignment'", 'if True',
     'tests/runtime/test_alignment_retrieval.py::test_native_discovery_never_dispatches_alignment_as_source'),
    ('s11_retrieval_backfill', 'ara/runtime/symbol_alignment.py',
     '            yield pair\n', '            if score>=minimum_score: yield pair\n',
     'tests/runtime/test_alignment_retrieval.py::test_retrieval_backfills_reports_prefilters_and_covers_papers'),
    ('s11_paper_diversity', 'ara/runtime/symbol_alignment.py',
     '    if paper_diversity:', '    if False:',
     'tests/runtime/test_alignment_retrieval.py::test_retrieval_backfills_reports_prefilters_and_covers_papers'),
    ('s11_threshold_counts', 'ara/runtime/symbol_alignment.py',
     "stats['above_threshold_pairs'] += int(score>=minimum_score)", "stats['above_threshold_pairs'] += 0",
     'tests/runtime/test_alignment_retrieval.py::test_retrieval_backfills_reports_prefilters_and_covers_papers'),
    ('s11_retrieval_receipt', 'ara/runtime/symbol_alignment.py',
     '        if retrieval!=inventory:', '        if False:',
     'tests/runtime/test_alignment_retrieval.py::test_native_judge_neutral_topic_and_retrieval_replay'),
    ('s11_neutral_alignment_topic', 'ara/runtime/symbol_alignment.py',
     "dict(topic='',policy_version=POLICY_VERSION", 'dict(policy_version=POLICY_VERSION',
     'tests/runtime/test_alignment_retrieval.py::test_native_judge_neutral_topic_and_retrieval_replay'),
]


CASES += [
    ('s11_legacy_replay_policy', 'ara/runtime/symbol_alignment.py',
     "candidates=legacy_candidate_pairs(original_symbols,source_rows,receipt['candidate_limit'])",
     "candidates=candidate_pairs(original_symbols,source_rows,receipt['candidate_limit'])",
     'tests/runtime/test_alignment_retrieval.py::test_legacy_alignment_receipt_replays_original_policy'),
]


CASES += [
    ('union_essentiality_basis', 'ara/runtime/novelty.py',
     "check(union_premises, Formula('iff'", "check((), Formula('iff'",
     'tests/runtime/test_union_essentiality.py::test_native_union_essentiality_proposal_selection_and_gap_file'),
    ('union_essentiality_unknown', 'ara/runtime/novelty.py',
     "if verdict not in ('SOLVER_UNSAT','SOLVER_COUNTEREXAMPLE'):\n                return result('unresolved','novelty_unresolved','A union essential-atom check was unresolved.')",
     'if False:\n                pass',
     'tests/runtime/test_union_essentiality.py::test_union_essentiality_unknown_refuses'),
    ('union_essentiality_forward', 'ara/runtime/synthesis.py',
     "if novelty['status'] != 'candidate':", 'if False:',
     'tests/runtime/test_union_essentiality.py::test_forward_union_essentiality_removes_padded_packages'),
    ('union_essentiality_gap_targets', 'ara/runtime/target_policy.py',
     "if reason is None and novelty['status'] != 'candidate':", 'if False:',
     'tests/runtime/test_union_essentiality.py::test_native_union_essentiality_proposal_selection_and_gap_file[padded_or-True]'),
    ('union_essentiality_both_polarities', 'ara/runtime/novelty.py',
     "for truth in (True, False):\n            verdict = check(union_premises", "for truth in (True,):\n            verdict = check(union_premises",
     'tests/runtime/test_union_essentiality.py::test_union_entailment_preserves_both_polarities'),
]


CASES += [
    ('r29_independent_interpretations', 'ara/formal.py',
     "Compiler('left:'), Compiler('right:')", "Compiler('left:'), Compiler('left:')",
     'tests/test_boolean_package.py::test_equivalent_connective_package_and_cross_paper_deduction_differ'),
    ('r29_equivalent_package', 'ara/runtime/novelty.py',
     'package_check = boolean_package(formula, union)', "package_check = dict(boolean_package(formula, union), solver_result='SOLVER_COUNTEREXAMPLE')",
     'tests/runtime/test_consistent_novelty.py::test_native_quantified_package_is_not_selectable'),
    ('r29_required_basis', 'ara/runtime/novelty_basis.py',
     'required = sorted(set(required_ids))', 'required = []',
     'tests/runtime/test_consistent_novelty.py::test_maximal_consistent_basis_preserves_required_ids_deterministically'),
    ('r29_basis_unknown', 'ara/runtime/novelty_basis.py',
     ".get(verdict, 'unresolved')", ".get(verdict, 'consistent')",
     'tests/runtime/test_consistent_novelty.py::test_solver_uncertainty_never_certifies_a_consistent_basis_or_package'),
    ('r29_route_exact_basis', 'ara/runtime/route_policy.py',
     "support_ids=receipt.get('support_ids', ())", 'support_ids=tuple(c.id for c in commitments.commitments)',
     'tests/runtime/test_consistent_novelty.py::test_native_unused_contradiction_preserves_modus_ponens'),
    ('r29_conflict_classification', 'ara/runtime/route_policy.py',
     "if consistency is not None and consistency['status'] != 'consistent':", 'if False:',
     'tests/runtime/test_consistent_novelty.py::test_native_inconsistent_cq_support_is_a_conflict'),
    ('r29_conflict_report', 'ara/runtime/conflict_feedback.py',
     "support_conflicts=support_conflicts['gaps'] if support_conflicts else []", 'support_conflicts=[]',
     'tests/runtime/test_consistent_novelty.py::test_native_inconsistent_cq_support_is_a_conflict'),
    ('r29_conflict_gap', 'ara/runtime/calls.py',
     "external + detection['gaps'] + support_gaps + classify_pairs", "external + detection['gaps'] + classify_pairs",
     'tests/runtime/test_consistent_novelty.py::test_native_inconsistent_cq_support_is_a_conflict'),
    ('r29_compose_consistency', 'ara/runtime/orchestration.py',
     "if consistency['status'] != 'consistent':", 'if False:',
     'tests/runtime/test_consistent_novelty.py::test_native_inconsistent_cq_support_is_a_conflict'),
    ('r29_forward_basis', 'ara/runtime/synthesis.py',
     'support_ids=tuple(sorted(ids))', 'support_ids=tuple(c.id for c in commitments.commitments)',
     'tests/runtime/test_consistent_novelty.py::test_native_unused_contradiction_preserves_modus_ponens'),
    ('r29_forward_conflict_disclosure', 'ara/runtime/synthesis.py',
     "if consistency['status'] != 'consistent':", 'if False:',
     'tests/runtime/test_consistent_novelty.py::test_recorded_forward_conflicting_supports_are_disclosed'),
    ('r29_missing_support_inventory', 'ara/runtime/route_policy.py',
     "if consistency is not None and 'support_ids' not in receipt:", 'if False:',
     'tests/runtime/test_consistent_novelty.py::test_missing_route_support_inventory_remains_unresolved'),
    ('alignment_bound_candidate_identity', 'ara/runtime/symbol_alignment.py',
     "return dict(left=candidate['left'],right=candidate['right'],**value)",
     "return dict(left=candidate['left'],right='R',**value)",
     'tests/runtime/test_alignment_resume.py::test_binding_rejects_even_an_echoed_mutated_identity'),
    ('alignment_unresolved_threshold', 'ara/runtime/symbol_alignment.py',
     'if len(unresolved)>max_unresolved:', 'if False:',
     'tests/runtime/test_alignment_resume.py::test_unresolved_threshold_refuses_before_freeze'),
    ('alignment_resume_working_binding', 'ara/runtime/alignment_resume.py',
     "require(json.loads((directory/f\"working-t-{state['plan_id']}.json\").read_text())==expected,",
     'require(True,',
     'tests/runtime/test_alignment_resume.py::test_resume_refuses_damaged_or_incomplete_state_before_provider[working]'),
    ('alignment_resume_rejection_receipts', 'ara/runtime/alignment_resume.py',
     "require(data['attempts']==config.get('validation_attempts',1) and\n                [r.get('attempt') for r in rejected]==list(range(1,data['attempts']+1)) and\n                rejected[-1].get('reason')==data['reason'],",
     'require(True,',
     'tests/runtime/test_alignment_resume.py::test_unresolved_receipt_without_rejected_attempts_cannot_resume'),
    ('alignment_unresolved_report', 'ara/runtime/report.py',
     'unresolved_count=len(unresolved),unresolved=unresolved,', 'unresolved_count=0,unresolved=unresolved,',
     'tests/runtime/test_alignment_resume.py::test_mutated_id_is_unresolved_and_never_changes_candidate'),
]


CASES += [
    ('boolean_solver_lifetime_lock', 'ara/formal.py',
     'with _SOLVER_LOCK:\n        return _boolean_combination_equivalence(basis, target, timeout_ms)',
     'with _SOLVER_LOCK:\n        pass\n    return _boolean_combination_equivalence(basis, target, timeout_ms)',
     'tests/test_boolean_package.py::test_boolean_z3_objects_are_released_under_the_solver_lock'),
]


def main():
    assert Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=ROOT, text=True).strip()) == ROOT
    output = ROOT / 'runs/delta-controls'
    output.mkdir(parents=True, exist_ok=True)
    results = []
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    for name, filename, old, new, target in CASES:
        path = ROOT / filename
        original = path.read_bytes()
        assert original.decode().count(old) == 1, (name, 'mutation anchor must occur exactly once')
        for pyc in (ROOT / 'ara/runtime/__pycache__').glob('*.pyc'):
            pyc.unlink()
        try:
            path.write_text(original.decode().replace(old, new))
            red = subprocess.run(['uv', 'run', 'pytest', '-q', target], cwd=ROOT,
                                 env=env, capture_output=True, text=True)
            (output / f'{name}-red.txt').write_text(red.stdout + red.stderr)
        finally:
            path.write_bytes(original)
        green = subprocess.run(['uv', 'run', 'pytest', '-q', target], cwd=ROOT,
                               env=env, capture_output=True, text=True)
        (output / f'{name}-green.txt').write_text(green.stdout + green.stderr)
        results.append({'name': name, 'red': red.returncode, 'restored': green.returncode})
        (output / 'results.json').write_text(json.dumps(results, indent=2))
        assert red.returncode == 1 and green.returncode == 0, results[-1]
        print(f'{name}: red=1 restored=0', flush=True)
    print(f'{len(results)} red/{len(results)}, all restored green')


if __name__ == '__main__':
    main()
