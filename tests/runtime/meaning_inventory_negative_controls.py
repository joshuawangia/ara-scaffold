"""Mutate the native meaning shape retry, preserve logs, restore every mutation."""
from pathlib import Path
import json
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
TARGET=ROOT/'ara/runtime/audit_carryover.py'
TEST='tests/runtime/test_audit_carryover.py::'
CASES=[
    ('parent_attempts', ',validation_attempts=2)', ')',
     'test_malformed_meaning_retry_retains_valid_adverse_vote', 'InvalidOutput: meaning check pair inventory mismatch'),
    ('adverse_union', ' and not adverse[key]', '',
     'test_missing_meaning_inventory_keeps_all_51_adverse_votes[False]', 'DID NOT RAISE'),
    ('bounded_attempts', ',validation_attempts=2)', ',validation_attempts=3)',
     'test_meaning_shape_retry_stops_after_one_correction', 'assert 3 == 2'),
    ('duplicate_inventory', 'if len(keys)!=len(counts) or set(keys)!=expected:', 'if set(keys)!=expected:',
     'test_malformed_meaning_retry_retains_valid_adverse_vote', 'assert 3 == 4'),
]


def main():
    out=ROOT/'runs/audit-inline/inventory-controls'
    out.mkdir(parents=True,exist_ok=True)
    original=TARGET.read_bytes()
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':'/dev/shm'}
    results=[]
    for name,old,new,test,diagnostic in CASES:
        assert original.decode().count(old)==1,name
        command=[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',TEST+test]
        try:
            TARGET.write_text(original.decode().replace(old,new))
            bad=subprocess.run(command+[f'--basetemp=/dev/shm/nu4-inventory-{os.getpid()}-{name}-bad'],cwd=ROOT,env=env,capture_output=True,text=True)
            (out/(name+'-mutated.txt')).write_text(bad.stdout+bad.stderr)
        finally:
            TARGET.write_bytes(original)
        good=subprocess.run(command+[f'--basetemp=/dev/shm/nu4-inventory-{os.getpid()}-{name}-restored'],cwd=ROOT,env=env,capture_output=True,text=True)
        (out/(name+'-restored.txt')).write_text(good.stdout+good.stderr)
        row=dict(name=name,detected=bad.returncode==1 and diagnostic in bad.stdout,restored=good.returncode==0)
        results.append(row)
        (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
        print(json.dumps(row),flush=True)
        assert row['detected'] and row['restored'],name


if __name__=='__main__':main()
