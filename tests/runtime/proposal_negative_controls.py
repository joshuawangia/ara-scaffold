"""Proposal authorization controls mutate the production audit, then restore it."""
from pathlib import Path
import os
import subprocess

ROOT=Path(__file__).resolve().parents[2]
CASES=[
 ('scope_adverse_history','ara/runtime/essay_audit.py',
  "            remap = None if same else _proposal_metadata_request(event['prompt'], prompt)", '            remap = None',
  'tests/runtime/test_proposal_policy.py::test_moving_proposal_heading_preserves_substantive_adverse_history[True]'),
 ('policy_adverse_history','ara/runtime/essay_audit.py',
  '            if not same and remap is None:', '            if True:',
  'tests/runtime/test_proposal_policy.py::test_prompt_policy_update_keeps_valid_adverse_labels'),
 ('bridge_attribution','ara/runtime/proposal.py',
  "    if role == 'proposed_principle' and source_attribution(text, source_authors):", '    if False:',
  'tests/runtime/test_proposal_policy.py::test_attributed_bridge_and_unsupported_established_claim_fail'),
 ('outside_unsupported_claim','ara/runtime/essay_audit.py',
  "        elif role == 'unsupported_claim':", '        elif False:',
  'tests/runtime/test_proposal_policy.py::test_outside_proposal_unsupported_established_claim_fails'),
 ('bridge_section','ara/runtime/essay_audit.py',
  "and scopes.get(item['sentence'], {}).get('heading', '').casefold() == 'proposal' for item in labels):", 'and True for item in labels):',
  'tests/runtime/test_proposal_scopes.py::test_bridge_principle_outside_proposal_section_fails'),
 ('source_fidelity','ara/runtime/essay_audit.py',
  "if (not item['citation_supported'] or not cited or", 'if (False or not cited or',
  'tests/runtime/test_proposal_policy.py::test_source_claim_must_be_cited_and_faithful_even_inside_proposal[True]'),
 ('metadata_adverse_history','ara/runtime/essay_audit.py',
  "            remap = None if same else _proposal_metadata_request(event['prompt'], prompt)", '            remap = None',
  'tests/runtime/test_proposal_mode.py::test_metadata_insertion_does_not_erase_unchanged_adverse_history[None]'),
 ('deterministic_disclosure','ara/runtime/proposal.py',
  '    result = insert_disclosure(proposal, draft)','    result = draft',
  'tests/runtime/test_proposal_mode.py::test_resume_inserts_disclosure_and_restores_cleanup_without_spending_repair'),
 ('disclosure','ara/runtime/proposal.py',
  "require(abstract.count(label) == 1 and 'Disclosure: ' + label + '.' in abstract,",'require(True,',
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
