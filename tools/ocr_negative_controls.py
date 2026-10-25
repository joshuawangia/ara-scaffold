"""Mutate OCR production wires sequentially, require red, restore and require green."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CASES = [
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
    output = ROOT / 'runs/ocr-controls'
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
