"""Round-2 production-wire mutations with red/restored-green receipts."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
CASES = [('pilot_audit_override',
  'config.yaml',
  '  audit_essay_max_output_tokens: 24000\n',
  '',
  'tests/runtime/test_pilot.py'),
 ('per_kind_allowance',
  'ara/runtime/calls.py',
  "self.config.get(f'{kind}_max_output_tokens', self.config['max_output_tokens'])",
  "self.config['max_output_tokens']",
  'tests/runtime/test_pilot.py'),
 ('inventory_correction',
  'ara/runtime/calls.py',
  "raise ValidationError('essay audit: sentence inventory mismatch')",
  "raise Rejected('essay audit: sentence inventory mismatch')",
  'tests/runtime/test_audit_labels.py::test_malformed_audit_inventory_corrects_before_verdict'),
 ('partial_adverse_final',
  'ara/runtime/calls.py',
  "require(not flags,",
  'require(True,',
  'tests/runtime/test_audit_labels.py::test_incomplete_audit_with_extra_inference_is_still_final')]


def main():
    assert Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()) == ROOT
    output = ROOT / 'runs/iota-controls'
    output.mkdir(parents=True, exist_ok=True)
    results = []
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'ARA_LIVE_TEST': '0'}
    for name, filename, old, new, target in CASES:
        path = ROOT / filename
        original = path.read_bytes()
        assert old in original.decode(), name
        for pyc in (ROOT / 'ara/runtime/__pycache__').glob('*.pyc'):
            pyc.unlink()
        try:
            path.write_text(original.decode().replace(old, new))
            red = subprocess.run([sys.executable, '-m', 'pytest', '-q', target], cwd=ROOT,
                                 env=env, capture_output=True, text=True)
            (output / f'{name}-red.txt').write_text(red.stdout + red.stderr)
        finally:
            path.write_bytes(original)
        green = subprocess.run([sys.executable, '-m', 'pytest', '-q', target], cwd=ROOT,
                               env=env, capture_output=True, text=True)
        (output / f'{name}-green.txt').write_text(green.stdout + green.stderr)
        results.append({'name': name, 'red': red.returncode, 'restored': green.returncode})
        (output / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
        assert red.returncode == 1 and green.returncode == 0, results[-1]
        print(f'{name}: red=1 restored=0', flush=True)
    print(f'{len(results)} red/{len(results)}, all restored green')


if __name__ == '__main__':
    main()
