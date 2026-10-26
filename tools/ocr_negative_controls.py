"""Mutate OCR production wires sequentially, require red, restore and require green."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ('greek-equivalence', 'ara/runtime/ocr.py', "text = unicodedata.normalize('NFKC', normalize_latex_symbols(text))", 'text = text',
     'test_standard_latex_greek_preserves_clean_alphanumeric_symbols'),
    ('span-before-markup', 'ara/runtime/ocr.py', "text = ' '.join(clean_spans(text))", 'text = text',
     'test_latex_markup_does_not_hide_a_damaged_original_span'),
    ('alphanumeric-tokens', 'ara/runtime/ocr.py', "re.findall(r'[^\\W_]+', text)", "re.findall(r'[A-Za-z]{2,}', text)",
     'test_clean_alphanumeric_tokens_are_not_reduced_to_latin_fragments'),
    ('latex-prose', 'ara/runtime/ocr.py', "text = re.sub(r'\\\\[A-Za-z]+', ' ', text)", 'text = text',
     'test_latex_control_words_cannot_replace_missing_prose_tokens'),
    ('clean-spans', 'ara/runtime/ocr.py', 'if not any(bad_character(c) for c in span)', 'if True',
     'test_damaged_spans_do_not_create_trusted_word_fragments'),
    ('latex-symbols', 'ara/runtime/ocr.py', 'LATEX_SYMBOLS.get(m[1], m[0])', 'm[0]',
     'test_standard_latex_is_an_encoding_of_the_same_math_symbol'),
    ('cascade-after-rejection', 'ara/runtime/ocr.py', "if record['recovered'] or not use_vl", 'if True or not use_vl',
     'test_second_tier_recovers_only_rejected_physical_page'),
    ('keep-tier1-acceptance', 'ara/runtime/ocr.py', "if record['recovered'] or not use_vl", 'if not use_vl',
     'test_second_tier_is_skipped_after_tier1_acceptance'),
    ('vl-confidence', 'ara/runtime/ocr_vl.py', 'confidence_units=units', 'confidence_units=tuple((n, 1.0) for n, p in units)',
     'test_vl_generation_records_actual_probabilities_and_eos'),
    ('vl-completion', 'ara/runtime/ocr_vl.py', 'complete=ids[-1] in eos_ids', 'complete=True',
     'test_vl_truncation_is_not_recovery_even_with_high_confidence'),
    ('vl-weight-hash', 'ara/runtime/ocr_vl.py', "if actual != expected['sha256']:", 'if False:',
     'test_vl_weight_hash_rejects_tampering'),
    ('fallback-only', 'ara/runtime/ocr.py', 'if page.page not in candidates:', 'if False:',
     'test_recovery_preserves_healthy_page_and_physical_citations'),
    ('confidence', 'ara/runtime/ocr.py', 'result.confidence >= 0.95', 'result.confidence >= 0.0',
     'test_rejects_uncertain_or_lossy_ocr'),
    ('readable-retention', 'ara/runtime/ocr.py', 'length_ratio >= 0.98 and recall >= 0.98', 'length_ratio >= 0.9 and recall >= 0.9',
     'test_high_confidence_cannot_hide_small_readable_text_loss'),
    ('symbol-preservation', 'ara/runtime/ocr.py', 'missing_symbols == 0', 'True',
     'test_rejects_uncertain_or_lossy_ocr'),
    ('provenance', 'ara/runtime/ocr.py', 'ocr_provenance_json=canonical(records)', "ocr_provenance_json='[]'",
     'test_recovery_preserves_healthy_page_and_physical_citations'),
    ('physical-page', 'ara/runtime/ocr.py', 'PageText(page.page, result.text)', 'PageText(1, result.text)',
     'test_recovery_preserves_healthy_page_and_physical_citations'),
    ('weight-hash', 'ara/runtime/ocr.py', "sha256(path.read_bytes()).hexdigest() != expected", 'False',
     'test_hash_verification_rejects_missing_and_tampered_weights'),
    ('pdf-identity', 'ara/runtime/ocr.py', 'sha256(raw).hexdigest() != paper.pdf_sha256', 'False',
     'test_pdf_changed_after_intake_refused'),
    ('strict-policy', 'ara/runtime/extraction.py', "if paper.affected_pages and missing == 'refuse':", 'if False:',
     'test_low_confidence_stays_partial_and_strict_refuses'),
    ('native-cli', 'ara/runtime/cli.py', "if args.ocr == 'local':", 'if False:',
     'test_cli_defaults_to_local_before_provider_and_strict_policy'),
]


def main():
    if Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=ROOT, text=True).strip()) != ROOT:
        raise RuntimeError('wrong checkout')
    output = ROOT / 'runs/ocr-round2-controls'
    output.mkdir(parents=True, exist_ok=True)
    results = []
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    for name, file, old, new, test in CASES:
        path = ROOT / file
        original = path.read_text()
        if old not in original:
            raise RuntimeError(f'missing mutation anchor: {name}')
        for pyc in path.parent.glob('__pycache__/*.pyc'):
            pyc.unlink()
        command = [sys.executable, '-m', 'pytest', '-q', f'tests/runtime/test_ocr.py::{test}']
        try:
            path.write_text(original.replace(old, new))
            red = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
        finally:
            path.write_text(original)
        green = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
        (output / f'{name}-red.txt').write_text(red.stdout + red.stderr)
        (output / f'{name}-green.txt').write_text(green.stdout + green.stderr)
        results.append(dict(name=name, red_exit=red.returncode, restored_exit=green.returncode))
        (output / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
        print(f'{name}: red={red.returncode} restored={green.returncode}', flush=True)
        if red.returncode != 1 or green.returncode != 0:
            raise RuntimeError(f'control failed: {name}')


if __name__ == '__main__':
    main()
