"""Brief 4 regression wires; execute alone in a disposable worktree."""
from pathlib import Path
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CASES = [
 ('json_mode', 'ara/runtime/providers.py', 'raw.to_dict(mode="json")', 'raw.to_dict()', 'tests/runtime/test_provider.py::test_sdk_container_and_web_results_are_json_safe'),
]
for failure in ('serialization', 'logging', 'parse'):
    CASES.append((failure, 'ara/runtime/calls.py',
        'if not starts or completed:', 'if True:',
        f'tests/runtime/test_incomplete.py::test_dispatched_failure_is_incomplete[{failure}]'))
CASES += [
 ('unknown_charge', 'ara/runtime/calls.py', 'self.budget.charge(usage, cost)\n            self.log.emit', 'pass\n            self.log.emit', 'tests/runtime/test_incomplete.py::test_dispatched_failure_is_incomplete[parse]'),
 ('post_cap', 'ara/runtime/calls.py', 'if unknown_usage:\n                self.budget.after(kind)', 'if unknown_usage:\n                pass', 'tests/runtime/test_incomplete.py::test_unknown_reservation_runs_post_call_cap_check'),
 ('resume', 'ara/runtime/budget.py', "if any(json.loads(e['payload_json']).get('accounting') == 'reservation_unknown_actual' for e in log.read()):", 'if False:', 'tests/runtime/test_incomplete.py::test_dispatched_failure_is_incomplete[parse]'),
 ('incomplete_report', 'ara/runtime/export.py', "'accounting_complete': not unknown and not pending", "'accounting_complete': True", 'tests/runtime/test_incomplete.py'),
 ('splitter', 'ara/runtime/calls.py', "parts = [part.strip() for part in re.split(r'(?<=[.!?])\\s+|\\n+', body) if part.strip()]", 'parts = [body.strip()]', 'tests/runtime/test_audit_labels.py::test_sentence_splitter_excludes_bibliography'),
 ('missing_nodes', 'ara/runtime/calls.py', 'missing = ids - covered', 'missing = set()', 'tests/runtime/test_audit_labels.py::test_invalid_labels_cannot_approve[missing]'),
 ('trust_faithful', 'ara/runtime/calls.py', "'faithful': not missing and not extra and markers == ids", "'faithful': data.get('faithful', True)", 'tests/runtime/test_audit_labels.py::test_invalid_labels_cannot_approve[missing]'),
 ('sentence_inventory', 'ara/runtime/calls.py', 'len(numbers) != len(set(numbers)) or set(numbers) != expected', 'False', 'tests/runtime/test_audit_labels.py::test_invalid_labels_cannot_approve[unknown_sentence]'),
 ('node_inventory', 'ara/runtime/calls.py', "require(covered <= ids, 'essay audit: unknown node id')", 'pass', 'tests/runtime/test_audit_labels.py::test_invalid_labels_cannot_approve[unknown_node]'),
 ('marker_support', 'ara/runtime/calls.py', 'not missing and not extra and markers == ids', 'not missing and not extra', 'tests/runtime/test_audit_labels.py::test_invalid_labels_cannot_approve[unsupported_marker]'),
]


def main():
    assert Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()) == ROOT
    output = ROOT / 'runs/zeta-proof'
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for name, file, old, new, target in CASES:
        path = ROOT / file
        original = path.read_text()
        assert original.count(old) == 1, name
        for pyc in path.parent.glob('__pycache__/*.pyc'): pyc.unlink()
        env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
        try:
            path.write_text(original.replace(old, new))
            red = subprocess.run(['uv', 'run', 'pytest', '-q', target], env=env, capture_output=True, text=True)
        finally: path.write_text(original)
        green = subprocess.run(['uv', 'run', 'pytest', '-q', target], env=env, capture_output=True, text=True)
        (output / f'{name}-red.txt').write_text(red.stdout + red.stderr)
        (output / f'{name}-green.txt').write_text(green.stdout + green.stderr)
        results.append({'name': name, 'red': red.returncode, 'green': green.returncode})
        (output / 'controls.json').write_text(json.dumps(results, indent=2))
        assert red.returncode == 1 and green.returncode == 0, results[-1]
        assert 'AssertionError' in red.stdout or 'DID NOT RAISE' in red.stdout or 'BudgetStop' in red.stdout, red.stdout
        print(f'{name}: red=1 green=0', flush=True)

if __name__ == '__main__': main()
