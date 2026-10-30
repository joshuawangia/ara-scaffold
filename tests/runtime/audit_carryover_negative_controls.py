"""Break production carry-over decisions, require regression failures, then restore."""
from pathlib import Path
import json
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
CARRY='ara/runtime/audit_carryover.py'
TEST='tests/runtime/test_audit_carryover.py::'
BOUNDARY='tests/runtime/test_audit_carryover_boundaries.py::'
CASES=[
 ('effective_source_role',CARRY,"records.append((old,effective_labels(data['labels'],old)))","records.append((old,data['labels']))",BOUNDARY+'test_revised_verified_source_inherits_its_effective_clean_role'),
 ('prefix_inheritance',CARRY,'            rows.append(pair)','            pass',TEST+'test_prefix_only_inherits_verified_role_and_keeps_raw_dissent'),
 ('prefix_direction',CARRY,"==text and removal_or_unchanged(r)","==text",BOUNDARY+'test_added_ownership_prefix_requires_meaning_votes'),
 ('word_equality',CARRY,"normalized_sentence(r['text'])==text and removal_or_unchanged(r)","True and removal_or_unchanged(r)",TEST+'test_substantive_or_attribution_change_retains_dissent[P, Q and S.]'),
 ('source_k3',CARRY,'type(k) is int and k>=3','type(k) is int and k>=2',BOUNDARY+'test_source_gate_requires_three_samples'),
 ('bibliography_binding',CARRY,"if any(bibliography.get(m[6:-1])!=original.get(m[6:-1]) for m in markers if m.startswith('[cite:')):",'if False:',BOUNDARY+'test_changed_bibliography_cannot_claim_carried_verdict'),
 ('meaning_unanimity',CARRY,"all(v['verdict']=='equivalent' for v in votes) and not adverse[key]","any(v['verdict']=='equivalent' for v in votes)",TEST+'test_scope_broadening_requires_meaning_and_retains_dissent'),
 ('retry_adverse',CARRY," and not adverse[key]",'',TEST+'test_malformed_meaning_retry_retains_valid_adverse_vote'),
 ('no_reroll',CARRY,"decided={p['pair_sha256'] for p in receipt.get('meaning_checks',[])}",'decided=set()',TEST+'test_meaning_dissent_survives_resume_without_reroll'),
 ('selected_provider',CARRY,"scoped=calls._for_construction_stage(kind,inputs)",'scoped=calls',BOUNDARY+'test_meaning_dispatch_uses_selected_audit_provider'),
 ('audit_history','ara/runtime/essay_audit.py',"        current.pop('verified_sentence_carryover', None)\n        return",'        return',TEST+'test_prior_nonprefix_adverse_history_is_not_erased'),
 ('node_inventory','ara/runtime/essay_audit.py',"    require(referenced <= ids, 'essay audit: unknown node id')","    require(True, 'essay audit: unknown node id')",TEST+'test_carryover_does_not_validate_malformed_current_inventory[unknown_node]'),
]


def main():
    out=ROOT/'runs/audit-inline'/('controls-'+sys.argv[1] if len(sys.argv)>1 else 'controls')
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':'/dev/shm'}
    for name,filename,old,new,test in CASES:
        if len(sys.argv)>2 and name not in sys.argv[2:]:
            continue
        path=ROOT/filename
        original=path.read_bytes();text=original.decode()
        assert text.count(old)==1,name
        command=[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',test]
        try:
            path.write_text(text.replace(old,new))
            bad=subprocess.run(command+['--basetemp=/dev/shm/nu4-inline-control-'+name+'-bad'],cwd=ROOT,env=env,capture_output=True,text=True)
            (out/(name+'-mutated.txt')).write_text(bad.stdout+bad.stderr)
        finally:
            path.write_bytes(original)
        good=subprocess.run(command+['--basetemp=/dev/shm/nu4-inline-control-'+name+'-restored'],cwd=ROOT,env=env,capture_output=True,text=True)
        (out/(name+'-restored.txt')).write_text(good.stdout+good.stderr)
        diagnostic = name!='no_reroll' or 'assert 6 == 3' in bad.stdout
        row=dict(name=name,detected=bad.returncode==1 and '1 failed' in bad.stdout and diagnostic,restored=good.returncode==0)
        results.append(row)
        (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
        print(json.dumps(row),flush=True)
        assert row['detected'] and row['restored'],name


if __name__=='__main__':main()
