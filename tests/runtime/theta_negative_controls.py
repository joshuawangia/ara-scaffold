"""Run alone in this checkout: break each verification wire, restore, rerun."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
TESTS = 'tests/runtime/test_known_verification.py'
CONTROLS = [
    ('accept fuzzy quotation', 'ara/runtime/calls.py', 'if not exact:', 'if False:',
     TESTS + '::test_altered_quote_rejects_fuzzy_classifier'),
    ('skip originality-only search', 'ara/runtime/calls.py',
     '        evidence = self.search_evidence(draft, items)',
     "        if not items:\n"
     "            return draft, {'originality': {'assessment': 'unverified', 'evidence_urls': [], 'detail': 'Search omitted.'}, 'items': []}\n"
     '        evidence = self.search_evidence(draft, items)',
     TESTS + '::test_recorded_known_case[prior_statement]'),
    ('retain unverified citations', 'ara/runtime/calls.py',
     "if item['status'] == 'unverified':", "if item['status'] == 'unverified' and item['kind'] != 'citation':",
     TESTS + '::test_recorded_known_case[fabricated_citation]'),
    ('omit search input reservation', 'ara/runtime/providers.py',
     "count += self.config['model_context_token_bound'] * searches", 'count += 0',
     'tests/runtime/test_provider.py::test_web_admission_counts_initial_request_and_bounds_search_iterations[1]'),
    ('allow invented source excerpt', 'ara/runtime/calls.py',
     "if extracted and ' '.join(extracted.split()) in ' '.join(evidence['text'].split()):", 'if extracted:',
     'tests/runtime/test_verification_export.py::test_quote_excerpt_must_match_search_evidence[P Q S-P Q S-unverified]'),
]


def main() -> None:
    for name, filename, old, new, target in CONTROLS:
        source = ROOT / filename
        original = source.read_text()
        assert original.count(old) == 1, name
        try:
            source.write_text(original.replace(old, new))
            result = subprocess.run([sys.executable, '-m', 'pytest', '-q', '--tb=short', target], cwd=ROOT,
                                    capture_output=True, text=True)
            print(f'{name}: negative exit {result.returncode}\n{result.stdout}', flush=True)
            assert result.returncode == 1 and '1 failed' in result.stdout, name
        finally:
            source.write_text(original)
        subprocess.run([sys.executable, '-m', 'pytest', '-q', target], cwd=ROOT, check=True)
    print(f'{len(CONTROLS)} red / {len(CONTROLS)}, restored {len(CONTROLS)} green / {len(CONTROLS)}', flush=True)


if __name__ == '__main__':
    main()
