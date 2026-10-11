"""Round-2 production-wire mutations with red/restored-green receipts."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
WRITER = 'tests/runtime/test_writer_validation.py::'
PILOT = 'tests/runtime/test_pilot.py::'
CASES = [
    ('writer_feedback', 'ara/runtime/calls.py', "if kind != 'write_essay':", 'if True:', WRITER + 'test_invalid_writer_corrects_before_audit'),
    ('writer_three_attempts', 'ara/runtime/calls.py', 'attempts = 4', 'attempts = 3', WRITER + 'test_underlength_four_attempts_accounted'),
    ('writer_minimum', 'ara/runtime/calls.py', "require(word_count(data) >= self.config['essay_min_words'],", 'require(True,', WRITER + 'test_underlength_four_attempts_accounted'),
    ('writer_attempt_record', 'ara/runtime/calls.py', "'reason': reason, 'attempt': attempt,", "'reason': reason, 'attempt': 1,", WRITER + 'test_invalid_writer_corrects_before_audit'),
    ('writer_retry_admission', 'ara/runtime/budget.py', "if self.used_tokens + tokens(usage) > self.config['token_cap']:", 'if False:', WRITER + 'test_writer_retry_requires_new_admission'),
    ('pilot_overlay', 'ara/runtime/cli.py', 'config.update(config[selected_profile])', 'pass', PILOT + 'test_pilot_config_and_caps'),
    ('pilot_config_cost_cap', 'ara/runtime/budget.py', "Decimal(str(self.config['cost_cap_usd']))", "Decimal('10')", PILOT + 'test_pilot_config_and_caps[1001-0]'),
    ('writer_output_allowance', 'ara/runtime/calls.py', "self.config.get(f'{kind}_max_output_tokens', self.config['max_output_tokens'])", "self.config['max_output_tokens']", PILOT + 'test_writer_output_limit_reserved_and_dispatched'),
    ('writer_stream', 'ara/runtime/providers.py', "if maximum > 8192:", 'if False:', PILOT + 'test_large_writer_uses_sdk_stream'),
]


def main():
    assert Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()) == ROOT
    output = ROOT / 'runs/eta-controls'
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
