"""Integration production-wire controls; restore exactly after each mutation."""
from pathlib import Path
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CASES = [
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
    ('compact_formula_projection', 'ara/runtime/providers.py',
     'return project(original)', 'return schema',
     'tests/runtime/test_provider.py::test_compact_formula_projection_keeps_local_operator_checks'),
    ('full_schema_prompt', 'ara/runtime/calls.py',
     "if kind != 'search_evidence':", 'if False:',
     'tests/runtime/test_calls.py::test_full_local_schema_reaches_provider_and_log'),
    ('compound_arguments', 'ara/runtime/providers.py',
     "result['minItems'] = min(1, value['minItems'])", 'pass',
     'tests/runtime/test_provider.py::test_compound_generation_cannot_omit_all_arguments'),
    ('validation_retry', 'ara/runtime/calls.py',
     "attempts = self.config.get('validation_attempts', 1)", 'attempts = 1',
     'tests/runtime/test_calls.py::test_validation_retry_is_accounted_and_admitted[False]'),
    ('retry_admission', 'ara/runtime/budget.py',
     "if self.used_tokens + tokens(usage) > self.config['token_cap']:", 'if False:',
     'tests/runtime/test_calls.py::test_validation_retry_is_accounted_and_admitted[True]'),
    ('negative_audit_is_final', 'ara/runtime/calls.py',
     "if validating and not (kind == 'audit_essay' and isinstance(exc, Rejected)):", 'if validating:',
     'tests/runtime/test_calls.py::test_audit_rejects_extra_step'),
    ('route_artifacts', 'ara/runtime/orchestration.py',
     "save_route(calls.log.path.parent / 'routes', route)", 'pass',
     'tests/integration/test_cli_e2e.py'),
    ('provider_not_projection', 'ara/runtime/providers.py',
     "'allOf', 'not'", "'allOf'",
     'tests/runtime/test_provider.py::test_live_observed_not_constraint_projected_but_locally_enforced'),
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
