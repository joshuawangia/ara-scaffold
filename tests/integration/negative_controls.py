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
    ('retry_admission', 'ara/runtime/budget.py', "if self.used_tokens + tokens(usage) > self.config['token_cap']:", 'if False:', 'tests/runtime/test_calls.py::test_validation_retry_is_accounted_and_admitted[True]'),
    ('negative_audit_is_final', 'ara/runtime/calls.py', "if validating and not (kind == 'audit_essay' and isinstance(exc, Rejected)):", 'if validating:', 'tests/runtime/test_calls.py::test_audit_rejects_extra_step'),
    ('route_artifacts', 'ara/runtime/orchestration.py', "save_route(calls.log.path.parent / 'routes', route)", 'pass', 'tests/integration/test_cli_e2e.py'),
    ('provider_not_projection', 'ara/runtime/providers.py', "'allOf', 'not'", "'allOf'", 'tests/runtime/test_provider.py::test_live_observed_not_constraint_projected_but_locally_enforced'),
    ('fallback_header', 'ara/runtime/providers.py', "betas=['server-side-fallback-2026-06-01']", "betas=['server-side-fallback-2026-07-01']", 'tests/runtime/test_fallbacks.py::test_fallback_request_shape'),
    ('fallback_config_validation', 'ara/runtime/providers.py', "if fallbacks != 'off' and not (", 'if False and not (', 'tests/runtime/test_fallbacks.py::test_invalid_fallback_config_is_rejected'),
    ('fallback_cache', 'ara/runtime/calls.py', "'fallbacks': self.config.get('fallbacks', ['claude-opus-4-8'])", "'fallbacks': 'off'", 'tests/runtime/test_fallbacks.py::test_fallback_mode_partitions_cache'),
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
    ('fallback_off', 'ara/runtime/providers.py', "if fallbacks != 'off':", 'if True:', 'tests/runtime/test_fallbacks.py::test_fallback_request_shape[off]'),
    ('extraction_schema', 'ara/runtime/calls.py', 'Draft202012Validator(schema).validate(data)', "None if kind == 'extract_paper' else Draft202012Validator(schema).validate(data)", 'tests/runtime/test_extraction.py::test_schema_and_reference_rejection[extra]'),
    ('extraction_attribution', 'schemas/extract_paper.json', '"author_claim",', '"P", "author_claim",', 'tests/runtime/test_extraction.py::test_schema_and_reference_rejection[attribution]'),
    ('extraction_source', 'ara/runtime/calls.py', "require(data['source_id'] == paper.source_id,", 'require(True,', 'tests/runtime/test_extraction.py::test_schema_and_reference_rejection[source]'),
    ('extraction_item_source', 'ara/runtime/calls.py', 'require(item.source_id == paper.source_id,', 'require(True,', 'tests/runtime/test_extraction.py::test_schema_and_reference_rejection[item_source]'),
    ('extraction_page_bounds', 'ara/runtime/calls.py', 'require(1 <= item.page_start <= item.page_end <= len(paper.pages),', 'require(True,', 'tests/runtime/test_extraction.py::test_schema_and_reference_rejection[reversed]'),
    ('extraction_pdf_pages', 'ara/runtime/extraction.py', "page.extract_text() or ''", "'R'", 'tests/runtime/test_extraction.py::test_page_text_and_immutable_contract'),
    ('extraction_sparse_image_detection', 'ara/runtime/extraction.py', 'if image_or_form and chars < 200:', 'if False:', 'tests/runtime/test_extraction_fix1.py::test_sparse_image_pages_are_partial[P]'),
    ('extraction_fallback_marker', 'ara/runtime/extraction.py', "outcome = {**base, 'status': 'record only, not extracted'", "outcome = {**base, 'status': 'extracted'", 'tests/runtime/test_extraction.py::test_missing_fallback_and_methodology'),
    ('extraction_strict_refusal', 'ara/runtime/extraction.py', "if missing == 'refuse':", 'if False:', 'tests/runtime/test_extraction.py::test_refuse_missing_and_no_publication'),
    ('extraction_counted_oversize', 'ara/runtime/calls.py', 'if estimate.input_tokens + maximum > limit:', 'if False:', 'tests/runtime/test_extraction_rich.py::test_page_ranges_and_logged_reconciliation'),
    ('extraction_provider_context', 'ara/runtime/calls.py', 'if admission and not fits:', "if admission and not fits and kind != 'extract_paper':", 'tests/runtime/test_extraction.py::test_provider_context_bound_rechecked'),
    ('extraction_admission_cap', 'ara/runtime/budget.py', "if stage == 'extract_paper' and self.extraction_cost() + self.cost(usage) > Decimal(str(", 'if False and self.extraction_cost() + self.cost(usage) > Decimal(str(', 'tests/runtime/test_extraction.py::test_extraction_budget_admission[extraction_cost_cap_usd]'),
    ('extraction_actual_cap', 'ara/runtime/budget.py', "if stage == 'extract_paper' and self.extraction_cost() > Decimal(str(", 'if False and self.extraction_cost() > Decimal(str(', 'tests/runtime/test_extraction.py::test_extraction_actual_cost_cap'),
    ('extraction_retry', 'ara/runtime/calls.py', "attempts = self.config.get('validation_attempts', 1)", "attempts = 1 if kind == 'extract_paper' else self.config.get('validation_attempts', 1)", 'tests/runtime/test_extraction.py::test_extraction_retry_and_reservation'),
    ('extraction_model_logging', 'ara/runtime/calls.py', "self._event(kind, prompt, raw, usage, cost, start, cached, 'accepted', None, key, attempt=attempt)", "None if kind == 'extract_paper' else self._event(kind, prompt, raw, usage, cost, start, cached, 'accepted', None, key, attempt=attempt)", 'tests/runtime/test_extraction.py::test_missing_fallback_and_methodology'),
    ('extraction_export_accounting', 'ara/runtime/export.py', "'extraction': extraction_summary,", "'extraction': {},", 'tests/runtime/test_extraction.py::test_missing_fallback_and_methodology'),
    ('extraction_cache', 'ara/runtime/calls.py', 'saved = self.cache.get(key)', "saved = None if kind == 'extract_paper' else self.cache.get(key)", 'tests/runtime/test_extraction.py::test_cache_replay_and_pdf_identity'),
    ('extraction_pdf_cache_identity', 'ara/runtime/extraction.py', "'pdf_sha256': self.pdf_sha256, 'pages':", "'pdf_sha256': None, 'pages':", 'tests/runtime/test_extraction.py::test_cache_replay_and_pdf_identity'),
    ('extraction_provenance_integrity', 'ara/runtime/extraction.py', "if events[-1]['stage'] != 'extraction_completed' or complete['literature_sha256'] != digest(text) or assemble(outcomes) != text:", 'if False:', 'tests/runtime/test_extraction.py::test_provenance_integrity'),
    ('extraction_cli_import', 'ara/runtime/cli.py', 'import_provenance(log, provenance)', 'pass', 'tests/runtime/test_extraction.py::test_extract_cli_to_build_t_native_path'),
    ('extraction_ai_label', 'ara/runtime/cli.py', 'literature=literature if args.literature is not None and not provenance else None,', 'literature=literature if args.literature is not None else None,', 'tests/runtime/test_extraction.py::test_extract_cli_to_build_t_native_path'),
    ('extraction_t_citation', 'ara/runtime/construction.py', "require(c.citation == items[c.id]['citation'],", 'require(True,', 'tests/runtime/test_extraction.py::test_build_t_cannot_cite_fallback_or_invented_page'),
    ('extraction_no_record_only_t', 'ara/runtime/calls.py', "require(bool(allowed), 'no extracted claims available to build T')", 'pass', 'tests/runtime/test_extraction.py::test_record_only_cannot_build_t'),
    ('extraction_estimate', 'ara/runtime/extraction.py', 'input_tokens=pages * per_page + readable * overhead', 'input_tokens=readable * overhead', 'tests/runtime/test_extraction.py::test_estimate_only_never_dispatches'),
    ('build_t_context', 'ara/runtime/calls.py', 'if admission and not fits:', "if admission and not fits and kind != 'build_t':", 'tests/runtime/test_extraction_fix1.py::test_build_t_counted_context_refusal'),
    ('extraction_blank_pages', 'ara/runtime/extraction.py', "unavailable = 'empty_pdf' if not pages else None", "unavailable = 'empty_pdf' if not pages or any(d.reason == 'blank_page' for d in diagnostics) else None", 'tests/runtime/test_extraction_fix1.py::test_blank_pages_retained_without_rejecting_paper'),
    ('extraction_page_numbers', 'ara/runtime/extraction.py', 'pages.append(PageText(i, text))', 'pages.append(PageText(len([p for p in pages if p.text.strip()]) + 1, text))', 'tests/runtime/test_extraction_fix1.py::test_blank_pages_retained_without_rejecting_paper'),
    ('extraction_partial_status', 'ara/runtime/extraction.py', "outcome = {**base, 'status': 'partial' if paper.affected_pages else 'extracted', **result.to_dict()}", "outcome = {**base, 'status': 'extracted', **result.to_dict()}", 'tests/runtime/test_extraction_fix1.py::test_sparse_image_pages_are_partial[P]'),
    ('extraction_unread_page_citation', 'ara/runtime/calls.py', 'require(item.page_start in readable and item.page_end in readable and', 'require(True or item.page_start in readable and item.page_end in readable and', 'tests/runtime/test_extraction_fix1.py::test_extraction_cannot_cite_unread_image_page'),
    ('extraction_blank_stream_detection', 'ara/runtime/extraction.py', 'contents.operations if contents is not None else []', 'contents.operations if contents else []', 'tests/runtime/test_extraction_fix1.py::test_sparse_image_pages_are_partial[P]'),
    ('extraction_counted_not_bytes', 'ara/runtime/extraction.py', "if prompt_bytes + maximum > calls.config['model_context_token_bound']:", "if prompt_bytes + maximum > calls.config['model_context_token_bound']:\n            calls.budget.stop('byte bound', 'extract_paper')", 'tests/runtime/test_extraction_fix1.py::test_large_bytes_use_counted_tokens'),
    ('extraction_cache_lineage_import', 'ara/runtime/extraction.py', 'if missing_lineage(events):', 'if False:', 'tests/runtime/test_extraction_fix1.py::test_fresh_cache_artifact_refused_at_cli_import'),
    ('extraction_cache_lineage_accounting', 'ara/runtime/export.py', "'accounting_complete': not unknown and not pending and not lineage_incomplete,", "'accounting_complete': not unknown and not pending,", 'tests/runtime/test_extraction_fix1.py::test_fresh_cache_artifact_refused_at_cli_import'),
    ('extraction_local_inherited_totals', 'ara/runtime/export.py', "'local_totals': totals([e for i, e in enumerate(events) if i not in inherited_indices]),", "'local_totals': totals(events),", 'tests/runtime/test_extraction_fix1.py::test_fresh_cache_artifact_refused_at_cli_import'),
    ('extraction_enclosing_cap_warning', 'ara/runtime/extraction.py', "print('planned batch exceeds enclosing caps', flush=True)", 'pass', 'tests/runtime/test_extraction_fix1.py::test_preflight_flags_caps_and_profile_is_explicit'),
    ('extraction_batch_profile', 'ara/runtime/cli.py', 'config.update(config[args.profile])', 'pass', 'tests/runtime/test_extraction_fix1.py::test_preflight_flags_caps_and_profile_is_explicit'),
    ('extracted_t_output_capacity', 'ara/runtime/calls.py', "maximum = self.config['extracted_build_t_max_output_tokens']\n        identity", "maximum = self.config['max_output_tokens']\n        identity", 'tests/runtime/test_extraction_fix1.py::test_capacity53_maximum_through_cli'),
    ('build_t_retry_context', 'ara/runtime/calls.py', 'estimate = self.count_request(kind, inputs, maximum=maximum, admission=True)', "estimate = self.count_request(kind, inputs, maximum=maximum, admission='validation_feedback' not in inputs)", 'tests/runtime/test_extraction_fix1.py::test_build_t_retry_recounts_feedback'),
    ('extraction_import_idempotence', 'ara/runtime/extraction.py', "if any(e['stage'] == 'extraction_provenance_import' and", "if False and any(e['stage'] == 'extraction_provenance_import' and", 'tests/runtime/test_extraction_fix1.py::test_fresh_cache_artifact_refused_at_cli_import'),
    ('extraction_partial_methodology', 'ara/runtime/export.py', "for p in outcomes if p['status'] == 'partial'", "for p in outcomes if p['status'] == 'extracted'", 'tests/runtime/test_extraction_fix1.py::test_sparse_image_pages_are_partial[P]'),
    ('rich_id_unique', 'ara/runtime/calls.py', 'require(len(ids) == len(set(ids)),', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_rich_graph_rejects_invalid_links[id]'),
    ('rich_endpoint', 'ara/runtime/calls.py', 'require(set(refs) <= available,', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_rich_graph_rejects_invalid_links[endpoint]'),
    ('rich_inference_origin', 'ara/runtime/calls.py', "item.inference_origin == 'paper_stated'", 'True', 'tests/runtime/test_extraction_rich.py::test_rich_graph_rejects_invalid_links[origin]'),
    ('rich_coverage', 'ara/runtime/calls.py', "require(data['coverage_complete'] or (allow_incomplete and bool(data['unresolved_references'])),", 'require(True,', 'tests/runtime/test_extraction_rich.py::test_rich_graph_rejects_invalid_links[coverage]'),
    ('rich_no_summary_cap', 'schemas/extract_paper.json', '"text": {\n            "type": "string",', '"text": {\n            "maxLength": 400,\n            "type": "string",', 'tests/runtime/test_extraction_rich.py::test_no_compact_summary_limit'),
    ('rich_range_reconciliation', 'ara/runtime/calls.py', 'if len(ranges) > 1 or unresolved:', 'if False:', 'tests/runtime/test_extraction_rich.py::test_page_ranges_and_logged_reconciliation'),
    ('strict_partial', 'ara/runtime/extraction.py', "if paper.affected_pages and missing == 'refuse':", 'if False:', 'tests/runtime/test_extraction_rich.py::test_strict_partial_cli'),
    ('rich_inventory', 'ara/runtime/construction.py', 'require(not selected & excluded and selected | excluded == set(items),', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[inventory]'),
    ('rich_dependency_closure', 'ara/runtime/construction.py', 'require(all(dependencies[id] <= selected for id in selected),', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[qualification]'),
    ('rich_attribution', 'ara/runtime/construction.py', 'require(c.text == evidence_text(items[c.id]),', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[attribution]'),
    ('rich_symbol_unique', 'ara/runtime/construction.py', 'require(len(set(names)) == len(names),', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[duplicate_symbol]'),
    ('rich_symbol_signature', 'ara/runtime/construction.py', "require(catalog[name]['kind'] == kind and catalog[name]['arity'] == arity,", 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[symbol_arity]'),
    ('rich_symbol_alignment', 'ara/runtime/construction.py', 'require(bound == used,', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[binding]'),
    ('rich_omission_reason', 'ara/runtime/construction.py', "require(all(o['reason'].strip() for o in omitted),", 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[omission_reason]'),
    ('rich_working_allowance', 'ara/runtime/construction.py', 'require(measured.input_tokens - blank.input_tokens <= batch.allowance,', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_counted_capacity_refuses_explicitly[working]'),
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
    ('rich_final_working_budget', 'ara/runtime/construction.py', "if measured.input_tokens > metadata['working_t_token_budget']:", 'if False:', 'tests/runtime/test_extraction_rich.py::test_construction_final_capacity_guard[final_budget]'),
    ('rich_symbol_budget', 'ara/runtime/construction.py', 'require(with_catalog.input_tokens - without.input_tokens <= symbol_budget,', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_construction_final_capacity_guard[symbols]'),
    ('rich_cached_context', 'ara/runtime/calls.py', 'estimate = self.count_request(kind, inputs, maximum=maximum, admission=True)', 'estimate = self.count_request(kind, inputs, maximum=maximum, admission=not cached)', 'tests/runtime/test_extraction_rich.py::test_cached_context_is_recounted'),
]

CASES.append(('rich_nullable_provider_schema', 'schemas/extract_paper.json', '"type": "string",\n                "enum": [\n                  "paper_stated"', '"type": ["string", "null"],\n                "enum": [\n                  "paper_stated"', 'tests/runtime/test_provider.py::test_rich_nullable_enum_matches_provider_grammar'))

CASES += [('batch_wire_grammar', 'ara/runtime/providers.py', "encoded_formulas=kind == 'build_t_batch'", 'encoded_formulas=False', 'tests/runtime/test_provider.py::test_batch_formula_wire_avoids_grammar_expansion'), ('batch_wire_decode', 'ara/runtime/calls.py', "item['formula'] = json.loads(item['formula'])", 'pass', 'tests/runtime/test_extraction_rich.py::test_encoded_batch_formula_still_requires_local_validation[True]'), ('batch_wire_invalid_json', 'ara/runtime/calls.py', "raise Rejected('invalid encoded formula JSON') from exc", 'raise', 'tests/runtime/test_extraction_rich.py::test_encoded_batch_formula_still_requires_local_validation[False]')]

CASES.append(('batch_bound_variables', 'ara/runtime/construction.py', "require(term.kind != 'variable' or term.name in bound,", 'require(True,', 'tests/runtime/test_extraction_rich.py::test_batch_variables_cannot_bypass_symbol_contract[False]'))

def main():
    assert Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=ROOT, text=True).strip()) == ROOT
    output = ROOT / 'runs/delta-controls'
    output.mkdir(parents=True, exist_ok=True)
    results = []
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    for name, filename, old, new, target in CASES:
        path = ROOT / filename
        original = path.read_bytes()
        assert original.decode().count(old) == 1
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
