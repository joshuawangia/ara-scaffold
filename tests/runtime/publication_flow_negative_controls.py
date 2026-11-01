"""Mutate production flow safeguards, require diagnostic failures, then restore."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
FLOW = 'ara/runtime/publication_flow.py'
TEST = 'tests/runtime/test_publication_flow.py::'
CASES = [
    ('ordinary_preflight', [('ara/runtime/codex_preflight.py', "'polish_essay', 'polish_flow',", "'polish_essay',")],
     'test_native_preflight_can_complete_without_operator_flow_prompt'),
    ('instruction', [(FLOW, "return text, text + '\\nINPUT_JSON\\n'", "return text, text + 'R' + '\\nINPUT_JSON\\n'")],
     'test_flow_single_edit_exact_instruction_and_native_final_gate'),
    ('source', [(FLOW, 'require(verified_legacy_import(events, route, draft),', 'require(True,')],
     'test_flow_fails_closed_on_unverified_source_before_edit'),
    ('citation_occurrences', [(FLOW, 'Counter(CITATION.findall(value[\'markdown\'])) == Counter(CITATION.findall(markdown))',
                             'set(CITATION.findall(value[\'markdown\'])) == set(CITATION.findall(markdown))')],
     'test_flow_citation_occurrence_loss_is_not_accepted_or_rerolled'),
    ('reroll', [(FLOW, "require(not any(e['stage'] == 'publication_flow_edit_started' for e in events)", 'require(True'),
                (FLOW, "require(not any(e['stage'] == 'publication_flow_edit_started' for e in calls.log.read()),", 'require(True,')],
     'test_flow_citation_occurrence_loss_is_not_accepted_or_rerolled'),
    ('whole_repair', [('ara/runtime/publication.py', "if flow or repair_rounds == 3 or not audit.get('flags'):",
                       "if repair_rounds == 3 or not audit.get('flags'):")],
     'test_flow_never_falls_back_to_whole_paper_repairs'),
]


def main():
    output = Path(sys.argv[1])
    output.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, 'PYTHONPATH': str(ROOT), 'PYTHONDONTWRITEBYTECODE': '1', 'TMPDIR': '/dev/shm'}
    results = []
    for name, edits, test in CASES:
        originals = {file: (ROOT/file).read_bytes() for file, _, _ in edits}
        command = [sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', TEST+test]
        bad_temp = '/dev/shm/pi3-flow-control-'+name+'-bad'
        try:
            for file, old, new in edits:
                path = ROOT/file
                source = path.read_text()
                assert source.count(old) == 1, (name, old)
                path.write_text(source.replace(old, new))
            bad = subprocess.run(command+['--basetemp='+bad_temp], cwd=ROOT, env=env, capture_output=True, text=True)
            (output/(name+'-mutated.txt')).write_text(bad.stdout+bad.stderr)
        finally:
            for file, raw in originals.items():
                (ROOT/file).write_bytes(raw)
        good = subprocess.run(command+['--basetemp=/dev/shm/pi3-flow-control-'+name+'-good'],
                              cwd=ROOT, env=env, capture_output=True, text=True)
        (output/(name+'-restored.txt')).write_text(good.stdout+good.stderr)
        row = dict(name=name, detected=bad.returncode == 1 and '1 failed' in bad.stdout,
                   restored=good.returncode == 0)
        if name == 'reroll':
            counts = []
            for path in Path(bad_temp).rglob('events.jsonl'):
                counts.append(sum(json.loads(line)['event']['stage'] == 'polish_flow'
                                  for line in path.read_text().splitlines()))
            row['mutated_edit_calls'] = max(counts, default=0)
            row['detected'] = row['detected'] and row['mutated_edit_calls'] == 2
        results.append(row)
        (output/'results.json').write_text(json.dumps(results, indent=2)+'\n')
        print(json.dumps(row), flush=True)
        assert row['detected'] and row['restored'], row


if __name__ == '__main__':
    main()
