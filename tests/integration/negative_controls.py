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
    ('extraction_schema', 'ara/runtime/calls.py', 'Draft202012Validator(schema).validate(data)', "None if kind == 'extract_paper' else Draft202012Validator(schema).validate(data)", 'tests/runtime/test_extraction.py::test_schema_and_reference_rejection[extra]'),
    ('extraction_attribution', 'schemas/extract_paper.json', '"author_claim",', '"P", "author_claim",', 'tests/runtime/test_extraction.py::test_schema_and_reference_rejection[attribution]'),
    ('extraction_source', 'ara/runtime/calls.py', "require(data['source_id'] == paper.source_id,", 'require(True,', 'tests/runtime/test_extraction.py::test_schema_and_reference_rejection[source]'),
    ('extraction_item_source', 'ara/runtime/calls.py', 'require(item.source_id == paper.source_id,', 'require(True,', 'tests/runtime/test_extraction.py::test_schema_and_reference_rejection[item_source]'),
    ('extraction_page_bounds', 'ara/runtime/calls.py', 'require(1 <= item.page_start <= item.page_end <= len(paper.pages),', 'require(True,', 'tests/runtime/test_extraction_v5.py::test_reversed_pages_repaired_logged_and_out_of_bounds_refused'),
    ('extraction_pdf_pages', 'ara/runtime/extraction.py', "page.extract_text() or ''", "'R'", 'tests/runtime/test_extraction.py::test_page_text_and_immutable_contract'),
    ('extraction_sparse_image_detection', 'ara/runtime/extraction.py', 'if image_or_form and chars < 200:', 'if False:', 'tests/runtime/test_extraction_fix1.py::test_sparse_image_pages_are_partial[P]'),
    ('extraction_fallback_marker', 'ara/runtime/extraction.py', "outcome = {**base, 'status': 'record only, not extracted'", "outcome = {**base, 'status': 'extracted'", 'tests/runtime/test_extraction.py::test_missing_fallback_and_methodology'),
    ('extraction_strict_refusal', 'ara/runtime/extraction.py', "if missing == 'refuse':", 'if False:', 'tests/runtime/test_extraction.py::test_refuse_missing_and_no_publication'),
    ('extraction_counted_oversize', 'ara/runtime/extraction.py', 'return usage.input_tokens', 'return 0', 'tests/runtime/test_extraction_rich.py::test_page_ranges_and_logged_reconciliation'),
    ('extraction_provider_context', 'ara/runtime/calls.py', 'if admission and not fits:', "if admission and not fits and kind != 'extract_paper':", 'tests/runtime/test_extraction.py::test_provider_context_bound_rechecked'),
    ('extraction_admission_cap', 'ara/runtime/budget.py', "if stage == 'extract_paper' and self.extraction_cost() + self.cost(usage, model=model) > Decimal(str(", 'if False and self.extraction_cost() + self.cost(usage, model=model) > Decimal(str(', 'tests/runtime/test_extraction.py::test_extraction_budget_admission[extraction_cost_cap_usd]'),
    ('extraction_actual_cap', 'ara/runtime/budget.py', "if stage == 'extract_paper' and self.extraction_cost() > Decimal(str(", 'if False and self.extraction_cost() > Decimal(str(', 'tests/runtime/test_extraction.py::test_extraction_actual_cost_cap'),
    ('extraction_retry', 'ara/runtime/calls.py', "attempts = self.config.get('validation_attempts', 1)", "attempts = 1 if kind == 'extract_paper' else self.config.get('validation_attempts', 1)", 'tests/runtime/test_extraction.py::test_extraction_retry_and_reservation'),
    ('extraction_model_logging', 'ara/runtime/calls.py', "self._event(kind, prompt, raw, usage, cost, start, cached, 'accepted', None, key, attempt=attempt)", "None if kind == 'extract_paper' else self._event(kind, prompt, raw, usage, cost, start, cached, 'accepted', None, key, attempt=attempt)", 'tests/runtime/test_extraction.py::test_missing_fallback_and_methodology'),
    ('extraction_export_accounting', 'ara/runtime/export.py', "'extraction': extraction_summary,", "'extraction': {},", 'tests/runtime/test_extraction.py::test_missing_fallback_and_methodology'),
    ('extraction_cache', 'ara/runtime/calls.py', 'saved = self.cache.get(key)', "saved = None if kind == 'extract_paper' else self.cache.get(key)", 'tests/runtime/test_extraction.py::test_cache_replay_and_pdf_identity'),
    ('extraction_pdf_cache_identity', 'ara/runtime/extraction.py', "'pdf_sha256': self.pdf_sha256, 'pages':", "'pdf_sha256': None, 'pages':", 'tests/runtime/test_extraction.py::test_cache_replay_and_pdf_identity'),
    ('extraction_provenance_integrity', 'ara/runtime/extraction.py', "if events[-1]['stage'] != 'extraction_completed' or complete['literature_sha256'] != digest(text) or assemble(outcomes) != text:", 'if False:', 'tests/runtime/test_extraction.py::test_provenance_integrity'),
    ('extraction_cli_import', 'ara/runtime/cli.py', "import_provenance(log, provenance, json.loads(args.literature.with_suffix('.provenance.json').read_text()))", 'pass' , 'tests/runtime/test_extraction.py::test_extract_cli_to_build_t_native_path'),
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
    ('extraction_cache_lineage_accounting', 'ara/runtime/export.py', "'accounting_complete': not unknown and not pending and not lineage_incomplete,", "'accounting_complete': not unknown and not pending,", 'tests/runtime/test_extraction_fix1.py::test_fresh_cache_artifact_refused_at_cli_import'),
    ('extraction_local_inherited_totals', 'ara/runtime/export.py', "'local_totals': totals([e for i, e in enumerate(events) if i not in inherited_indices]),", "'local_totals': totals(events),", 'tests/runtime/test_extraction_fix1.py::test_fresh_cache_artifact_refused_at_cli_import'),
    ('extraction_enclosing_cap_warning', 'ara/runtime/extraction.py', "print('planned batch exceeds enclosing caps', flush=True)", 'pass', 'tests/runtime/test_extraction_fix1.py::test_preflight_flags_caps_and_profile_is_explicit'),
    ('extraction_batch_profile', 'ara/runtime/cli.py', 'if args.profile:\n                config.update(config[args.profile])', 'if args.profile:\n                pass', 'tests/runtime/test_extraction_fix1.py::test_preflight_flags_caps_and_profile_is_explicit'),
    ('extracted_t_output_capacity', 'ara/runtime/calls.py', "maximum = self.config['extracted_build_t_max_output_tokens']\n        identity", "maximum = self.config['max_output_tokens']\n        identity", 'tests/runtime/test_extraction_fix1.py::test_capacity53_maximum_through_cli'),
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
    ('rich_attribution', 'ara/runtime/construction.py', 'require(c.text == evidence_text(items[c.id], support_omitted.get(c.id)),', 'require(True,', 'tests/runtime/test_extraction_round3.py::test_fixed_inventory_boundary_has_no_freeze[attribution]'),
    ('rich_symbol_unique', 'ara/runtime/construction.py', 'require(len(set(names)) == len(names),', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[duplicate_symbol]'),
    ('rich_symbol_signature', 'ara/runtime/construction.py', "require(catalog[name]['kind'] == kind and catalog[name]['arity'] == arity,", 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[symbol_arity]'),
    ('rich_symbol_alignment', 'ara/runtime/construction.py', 'require(valid_alignments,', 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[binding]'),
    ('rich_omission_reason', 'ara/runtime/construction.py', "require(all(g['reason'].strip() for g in data['omissions']),", 'require(True,', 'tests/runtime/test_extraction_rich.py::test_invalid_working_batch_refused_before_freeze[omission_reason]'),
    ('rich_working_allowance', 'ara/runtime/construction.py', "require(cumulative.input_tokens <= metadata['working_t_token_budget'],", 'require(True,', 'tests/runtime/test_extraction_rich.py::test_counted_capacity_refuses_explicitly[working]'),
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
    ('stage_reservation_price', 'ara/runtime/calls.py', 'self.budget.before(estimate, kind, model=self.requested_model(kind))', 'self.budget.before(estimate, kind)', 'tests/runtime/test_extraction_round3.py::test_stage_model_wire_cache_and_receipts'),
    ('known_terminal_log_failure', 'ara/runtime/calls.py', 'if received:', 'if False:', 'tests/runtime/test_extraction_round3.py::test_known_usage_survives_parsing_or_terminal_log_failure[logging]'),
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
    ('closure_preflight', 'ara/runtime/construction.py', "require(projected.input_tokens <= metadata['working_t_token_budget'],", 'require(True,', 'tests/runtime/test_extraction_round4.py::test_closure_preflight_before_formalization'),
    ('window_inventory', 'ara/runtime/windows.py', 'values[:middle]', 'values[1:middle]', 'tests/runtime/test_evidence_windows.py::test_large_single_graph_windows_close_against_full_evidence'),
    ('full_graph_closure', 'ara/runtime/construction.py', "prerequisite_closure(items, selection['roots'])", "prerequisite_closure(window_items, selection['roots'])", 'tests/runtime/test_evidence_windows.py::test_large_single_graph_windows_close_against_full_evidence'),
    ('closure_size_admission', 'ara/runtime/construction.py', 'if closure_count.input_tokens > input_bound:', 'if False:', 'tests/runtime/test_evidence_windows.py::test_oversized_selected_closure_refuses_before_formalization'),
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
     'verify_imports(events, active | {key}, memo)', 'pass',
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
     "trace('prune', state_id=state_id, node_id=node.id, proposal_index=proposal_index,\n                          reason=license.decision.reason_code)", 'pass',
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
     "for index, state in enumerate(trace['states']):", "for index, state in enumerate(trace['states'][:499]):",
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
    ('bounded_assumption_mark', 'ara/runtime/construction.py',
     'return prefix + f', 'return f',
     'tests/runtime/test_bounded_closure.py::test_native_cut_disclosed_in_frozen_text_receipt_and_methodology'),
    ('bounded_methodology', 'ara/runtime/export.py',
     "p.get('support_omitted', {}).items()", '{}.items()',
     'tests/runtime/test_bounded_closure.py::test_native_cut_disclosed_in_frozen_text_receipt_and_methodology'),
    ('soft_working_output', 'ara/runtime/construction.py',
     "require(cumulative.input_tokens <= metadata['working_t_token_budget'],",
     "require(cumulative.input_tokens - current.input_tokens <= working_share,",
     'tests/runtime/test_bounded_closure.py::test_actual_output_borrows_within_global_limits[working]'),
    ('soft_symbol_output', 'ara/runtime/construction.py',
     "require(with_catalog.input_tokens - without.input_tokens <= symbol_budget,",
     "require(with_catalog.input_tokens - without.input_tokens - catalog_tokens <= symbol_share,",
     'tests/runtime/test_bounded_closure.py::test_actual_output_borrows_within_global_limits[symbols]'),
    ('bounded_exact_request_cut', 'ara/runtime/construction.py',
     "return calls.count_request('build_t_batch', {**trial, 'shared_symbols': []}).input_tokens <= input_bound",
     'return True',
     'tests/runtime/test_bounded_closure.py::test_counted_formalization_bound_cuts_before_dispatch'),
    ('bounded_zero_window', 'ara/runtime/construction.py',
     'if not selected_ids:', 'if False:',
     'tests/runtime/test_bounded_closure.py::test_zero_root_window_can_precede_contributing_window'),
]



CASES += [
    ('soft_recompute', 'ara/runtime/construction.py',
     'windows_left = len(batches) - batch.index', 'windows_left = len(batches)',
     'tests/runtime/test_construction_shares.py::test_borrowing_recounts_and_recomputes_before_next_dispatch'),
    ('soft_recount', 'ara/runtime/construction.py',
     "current = calls.count_request('propose_targets', {**target_inputs, 'commitments': {'commitments': prior}})",
     "current = calls.count_request('propose_targets', {**target_inputs, 'commitments': {'commitments': []}})",
     'tests/runtime/test_construction_shares.py::test_borrowing_recounts_and_recomputes_before_next_dispatch'),
    ('soft_window_skip', 'ara/runtime/construction.py',
     'refusal_reasons.append(str(exc))', 'raise',
     'tests/runtime/test_construction_shares.py::test_window_refusal_is_accounted_and_later_window_succeeds[formalization]'),
    ('soft_context_skip', 'ara/runtime/calls.py',
     "'window' if kind in ('select_t_roots', 'build_t_batch') else 'run'", "'run'",
     'tests/runtime/test_construction_shares.py::test_window_refusal_is_accounted_and_later_window_succeeds[correction_context]'),
    ('soft_exhaustion', 'ara/runtime/construction.py',
     'if available <= 0 or symbol_available <= 0:', 'if False:',
     'tests/runtime/test_construction_shares.py::test_global_exhaustion_freezes_accepted_work_once'),
    ('soft_global_working', 'ara/runtime/construction.py',
     "require(cumulative.input_tokens <= metadata['working_t_token_budget'],", 'require(True,',
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
