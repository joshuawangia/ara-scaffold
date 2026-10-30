"""Break admission trust boundaries and lossless evidence encoding, then restore."""
from pathlib import Path
import json
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
MODULE='ara/runtime/proposal_admission.py'
TEST='tests/runtime/test_proposal_admission.py::'
CASES=[
    ('freeze_binding',MODULE,"request['source_freeze_hash']==snapshot['freeze_hash']",'True',
     TEST+'test_admission_refuses_before_copy_or_model[freeze]','assert 0 != 0'),
    ('output_screen',MODULE,"    screen_request(snapshot['run']['config'],root,dict(request=request,proposal=prepared))",'    pass',
     TEST+'test_native_output_screen_runs_before_admission_records','assert 0 == 2'),
    ('admission_capacity',MODULE,"require(space['fits'], 'proposal admission held: projected disk reserve')","require(True, 'proposal admission held: projected disk reserve')",
     TEST+'test_admission_refuses_before_copy_or_model[floor]','assert 0 != 0'),
    ('root_reserve',MODULE,'fits=root_free >= ROOT_RESERVE and free-projected_bytes >= reserve','fits=free-projected_bytes >= reserve',
     TEST+'test_root_reserve_is_checked_even_when_code_and_run_are_in_shm','assert not True'),
    ('no_fake_formula',MODULE,"target=Proposition('paper:'+candidate,proposal['target_text'])","target=Proposition('paper:'+candidate,proposal['target_text'],__import__('ara.types',fromlist=['Formula']).Formula('atom',name='P'))",
     TEST+'test_native_admission_keeps_sources_and_adds_only_unformalized_open_target','is None'),
    ('queue_binding',MODULE,"admission['candidate_id']==entry['id'] and admission['source_run']", "admission['source_run']",
     TEST+'test_queue_promotion_requires_bound_native_admission','DID NOT RAISE'),
    ('lossless_context','ara/runtime/writing.py','refs.append(indexes[key])','refs.append(0)',
     'tests/runtime/test_sectioned_writer.py::test_large_repeated_source_context_is_lossless_without_raising_bound','assert restored==original'),
]


def main():
    out=ROOT/'runs/proposal-mode/admission-controls';out.mkdir(parents=True,exist_ok=True)
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':'/dev/shm'}
    results=[]
    for name,filename,old,new,test,diagnostic in CASES:
        path=ROOT/filename;original=path.read_bytes();assert original.decode().count(old)==1,name
        command=[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',test]
        try:
            path.write_text(original.decode().replace(old,new))
            bad=subprocess.run(command+[f'--basetemp=/dev/shm/nu4-admission-control-{os.getpid()}-{name}-bad'],cwd=ROOT,env=env,capture_output=True,text=True)
            (out/(name+'-bad.txt')).write_text(bad.stdout+bad.stderr)
        finally:path.write_bytes(original)
        good=subprocess.run(command+[f'--basetemp=/dev/shm/nu4-admission-control-{os.getpid()}-{name}-restored'],cwd=ROOT,env=env,capture_output=True,text=True)
        (out/(name+'-restored.txt')).write_text(good.stdout+good.stderr)
        row=dict(name=name,detected=bad.returncode==1 and diagnostic in bad.stdout,restored=good.returncode==0)
        results.append(row);(out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
        print(json.dumps(row),flush=True)
        assert row['detected'] and row['restored'],name


if __name__=='__main__':main()
