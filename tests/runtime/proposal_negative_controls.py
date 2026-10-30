"""Proposal authorization controls mutate the production audit, then restore it."""
from pathlib import Path
import os
import subprocess

ROOT=Path(__file__).resolve().parents[2]
CASES=[
 ('scope_attribution','ara/runtime/proposal.py',
  "    if scoped and (role == 'source_claim' or source_attribution(text, source_authors)):",
  '    if False:',
  'tests/runtime/test_proposal_scopes.py::test_in_scope_attribution_fails_regardless_of_role[framing]'),
 ('outside_scope_claim','ara/runtime/proposal.py',
  "    if not scoped and not re.match(prefix+r'\\b', text, re.I):",
  '    if False:',
  'tests/runtime/test_proposal_scopes.py::test_outside_scope_unmarked_claim_fails'),
 ('metadata_adverse_history','ara/runtime/essay_audit.py',
  "            remap = None if same else _proposal_metadata_request(event['prompt'], prompt)",
  '            remap = None',
  'tests/runtime/test_proposal_mode.py::test_metadata_insertion_does_not_erase_unchanged_adverse_history[None]'),
 ('deterministic_disclosure','ara/runtime/proposal.py','    result = insert_disclosure(proposal, draft)','    result = draft',
  'tests/runtime/test_proposal_mode.py::test_resume_inserts_disclosure_and_restores_cleanup_without_spending_repair'),
 ('unmarked','ara/runtime/proposal.py',"return 'unmarked_proposal'",'return None',
  'tests/runtime/test_proposal_mode.py::test_unmarked_or_source_attributed_proposal_still_fails[P.-proposed_principle]'),
 ('source_attribution','ara/runtime/proposal.py',"    if source_attribution(remainder, source_authors):",'    if False:',
  'tests/runtime/test_proposal_mode.py::test_source_attribution_without_citation_cannot_hide_in_proposal_role'),
 ('disclosure','ara/runtime/proposal.py',"require(abstract.count(label) == 1 and 'Disclosure: ' + label + '.' in abstract,",'require(True,',
  'tests/runtime/test_proposal_mode.py::test_proposal_mode_cannot_erase_citations_or_disclosure_on_export'),
]

def main():
 for name,filename,old,new,test in CASES:
  path=ROOT/filename;original=path.read_text()
  assert original.count(old)==1,name
  env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
  try:
   path.write_text(original.replace(old,new))
   result=subprocess.run(['uv','run','pytest','-q',test],cwd=ROOT,env=env,capture_output=True,text=True)
   assert result.returncode==1 and '1 failed' in result.stdout,(name,result.stdout,result.stderr)
  finally:path.write_text(original)
  subprocess.run(['uv','run','pytest','-q',test],cwd=ROOT,env=env,check=True)
  print(name+': detected and restored',flush=True)

if __name__=='__main__':main()
