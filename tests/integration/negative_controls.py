"""Integration production-wire controls; restore exactly after each mutation."""
from pathlib import Path
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('compact_formula_projection', 'ara/runtime/providers.py',
     'return project(original)', 'return schema',
     'tests/runtime/test_provider.py::test_compact_formula_projection_keeps_local_operator_checks'),
    ('route_artifacts', 'ara/runtime/orchestration.py',
     "save_route(calls.log.path.parent / 'routes', route)", 'pass',
     'tests/integration/test_cli_e2e.py'),
    ('provider_not_projection', 'ara/runtime/providers.py',
     "'allOf', 'not'", "'allOf'",
     'tests/runtime/test_provider.py::test_live_observed_not_constraint_projected_but_locally_enforced'),
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
