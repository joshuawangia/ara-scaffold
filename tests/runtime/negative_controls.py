"""Reversible production-wire mutations. Run without another checkout writer."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('projection', 'providers.py', 'return project(original)', 'return schema',
     'test_provider.py::test_projected_schema_is_acyclic_and_local_validation_is_stricter'),
    ('redaction', 'export.py', "text = text.replace(identifier, '[REDACTED]')", 'pass',
     'test_cli.py::test_every_cli_human_input_verbatim'),
    ('leaf_reference', 'calls.py', "require(data['t_id'] == 'open' or commitments.get(data['t_id']) is not None, 'unknown T id')", 'pass',
     'test_calls.py::test_ports_return_typed_values_and_enforce_references'),
    ('cache_ttl', 'budget.py', "(hour + unknown, 'cache_write_1h_per_million_usd')", "(hour, 'cache_write_1h_per_million_usd')",
     'test_calls.py::test_unknown_cache_ttl_uses_expensive_rate'),
    ('interactive_time', 'cli.py', "log.human('feedback', text, elapsed_seconds=elapsed)", "log.human('feedback', text, elapsed_seconds=0)",
     'test_cli.py::test_interactive_input_measures_prompt_to_accept'),
    ('schema', 'calls.py', 'validate_local(schema, data, self.config)', 'pass # disabled validation',
     'test_calls.py::test_invalid_schema_rejected_logged_not_cached'),
    ('cache', 'calls.py', 'saved = self.cache.get(key)', 'saved = None',
     'test_calls.py::test_cache_hit_identical_no_provider_call'),
    ('token_admission', 'budget.py', "if self.used_tokens + tokens(usage) > self.config['token_cap']:", 'if False:',
     'test_calls.py::test_caps_stop_with_partial_artifact[token_cap-1]'),
    ('cost_admission', 'budget.py', "if self.used_cost + self.cost(usage) > Decimal(str(self.config['cost_cap_usd'])):", 'if False:',
     'test_calls.py::test_caps_stop_with_partial_artifact[cost_cap_usd-0]'),
    ('token_actual', 'budget.py', "if self.used_tokens > self.config['token_cap']:", 'if False:',
     'test_calls.py::test_actual_usage_cap_is_enforced_after_call[token_cap-15000]'),
    ('cost_actual', 'budget.py', "if self.used_cost > Decimal(str(self.config['cost_cap_usd'])):", 'if False:',
     'test_calls.py::test_actual_usage_cap_is_enforced_after_call[cost_cap_usd-0.3]'),
    ('human_verbatim', 'logging.py', "self.record(stage, 'HUMAN', text=text,", "self.record(stage, 'HUMAN', text=text.strip(),",
     'test_cli.py::test_every_cli_human_input_verbatim'),
    ('log_only_export', 'export.py', "events = [r['event'] for r in records]", 'events = []',
     'test_verification_export.py::test_methodology_regenerates_from_log_alone'),
    ('essay_cap', 'calls.py', "require(word_count(data) <= min(6000, self.config['essay_word_limit']), 'essay word limit exceeded')", 'pass',
     'test_calls.py::test_essay_word_cap'),
    ('audit_steps', 'calls.py', "not missing and not extra and markers == ids", "not missing and markers == ids",
     'test_calls.py::test_audit_rejects_extra_step'),
    ('unverified_removal', 'calls.py', "if item['status'] == 'unverified':", 'if False:',
     'test_verification_export.py::test_unverified_items_removed_never_replaced'),
    ('evidence_provenance', 'calls.py', "require(set(item['evidence_urls']) <= set(evidence['urls']), 'unsupported verification URL')", 'pass',
     'test_verification_export.py::test_verification_rejects_invented_evidence'),
    ('log_hash', 'logging.py', 'or digest(canonical(row)) != checksum', 'or False',
     'test_boundaries.py::test_log_tamper_and_truncation'),
    ('log_tail', 'logging.py', "if checkpoints != expected or (self.path.exists() != self.anchor.exists()):", 'if False:',
     'test_boundaries.py::test_log_tamper_and_truncation'),
    ('engine_decisions', 'logging.py', 'def emit(self, event: RunEvent) -> None:',
     "def emit(self, event: RunEvent) -> None:\n        if event.label == 'ENGINE':\n            return",
     'test_verification_export.py::test_methodology_regenerates_from_log_alone'),
    ('negation_orchestration', 'orchestration.py', "((analysis.target, 'target'), (analysis.negated, 'negation'))", "((analysis.target, 'target'),)",
     'test_cli.py::test_smoke_cli_runs_both_polarities_and_exports'),
    ('unknown_spend', 'calls.py', 'if unknown_usage:\n                self.budget.after(kind)', 'if False:\n                self.budget.after(kind)',
     'test_calls.py::test_transport_failure_charges_reservation_and_stops'),
]


def run() -> None:
    if Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=ROOT, text=True).strip()) != ROOT:
        raise SystemExit('wrong checkout')
    output = ROOT / 'runs/gamma-proof'
    output.mkdir(parents=True, exist_ok=True)
    results = []
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    for name, file, old, new, target in CASES:
        path = ROOT / 'ara/runtime' / file
        original = path.read_bytes()
        text = original.decode()
        if text.count(old) != 1:
            raise RuntimeError(f'{name}: expected one production wire, got {text.count(old)}')
        # CPython bytecode timestamp granularity must not hide a restored wire.
        for cache in (ROOT / 'ara/runtime/__pycache__').glob('*.pyc'):
            cache.unlink()
        try:
            path.write_text(text.replace(old, new))
            red = subprocess.run(['uv', 'run', 'pytest', '-q', 'tests/runtime/' + target],
                                 cwd=ROOT, env=env, capture_output=True, text=True)
            (output / f'{name}-red.txt').write_text(red.stdout + red.stderr)
        finally:
            path.write_bytes(original)
        green = subprocess.run(['uv', 'run', 'pytest', '-q', 'tests/runtime/' + target],
                               cwd=ROOT, env=env, capture_output=True, text=True)
        (output / f'{name}-green.txt').write_text(green.stdout + green.stderr)
        results.append({'name': name, 'target': target, 'red_exit': red.returncode, 'green_exit': green.returncode})
        (output / 'negative-controls.json').write_text(json.dumps(results, indent=2))
        print(f'{name}: red={red.returncode} restored={green.returncode}', flush=True)
        if red.returncode != 1 or green.returncode != 0:
            raise SystemExit(f'invalid negative-control result: {name}')
    print(f'{len(results)} red/{len(results)}, all restored green')


if __name__ == '__main__':
    run()
