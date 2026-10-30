# Theta round 2: disclosed failures and completed-paper resume

Status: implementation and all required offline verification complete.
Revision: `b063433d56f83f058d4941c8c8a30b43ec0cf355` on `fix/context-request-without-obligation`.
Locally committed; working tree clean; no push.
Worktree: `/home/dev/ara-work/theta`; round-2 base `188784e6e11309bf7658bdce31dd70f933aea5d8`.
Brief: `/home/dev/ara-work/briefs/theta-round-2.md`.

## Resulting behavior

Extraction continues after terminal paper-local validation, output, context or
allowance failures. Each failed outcome has empty items, reason/detail and a
pinned failure receipt. A completed artifact labels itself
`complete_with_disclosed_failures`; native pilot import accepts it, construction
never includes its failed sources, and methodology lists failed papers and policy.
`extraction_max_failed_papers=3` is the default globally and in `extraction-full`.
Exactly three failures may complete; the fourth stops without publishing completed
literature. Earlier completed papers remain reusable even from that stopped run.
An entirely evidence-free corpus still cannot construct a working commitment set.

Global token/dollar exhaustion, unknown or interrupted provider spend, and
unexpected operational/configuration failures stop the run. They cannot be
relabeled as paper-local recoveries. All measured/rejected charges remain logged.

## Resume and accounting

Use a new empty destination and repeat `--resume-from` for prior run directories:

```sh
uv run ara extract --config /path/to/operator-config.yaml --profile extraction-full --manifest literature/manifest.yaml --fulltext-dir literature/fulltext --resume-from runs/extraction-old --run-dir runs/extraction-new
```

Before future generation, fill the profile's operator caps: both dollar caps
should reflect the intended USD125 aggregate ceiling, and the token cap must also
be explicit. This task made no paid call and did not start that future run.

Completed matching papers, including accepted empty dispositions, are reused
without extraction dispatch. Failed, missing or changed papers are extracted.
PDF hash, metadata, diagnostics and current input hash bind the reusable outcome;
legacy outcomes without an input hash retain PDF/metadata binding. Accepted
merged-graph receipts are required. Conflicting matching completed outcomes refuse.

All origin charges, including failed attempts and other papers in supplied origins,
are inherited before budget construction. Overlapping/transitive native imports
count original events once. Retried papers receive fresh paper-local allowances;
aggregate cost and token limits retain prior spend. Current-batch outcomes drive
the new corpus, while methodology retains historical failures. Supply origins from
the same campaign rather than treating unrelated histories as free evidence.

## Provenance and retention

Native resume and pilot imports pin original log path, record count and last hash.
New source pins verify the append checkpoint; imports recursively validate origin
prefixes and compare copied events. Missing, modified or truncated ancestors refuse.
Preserve origin logs/checkpoints and absolute path accessibility for later imports.
Local hash chains detect alteration against retained pins; they are not external
signatures against a party rewriting every local receipt.

The checkout had pinned extraction sidecars and full-prefix import primitives,
not a separate B2 module. `ara/runtime/provenance.py` extends those native seams.
Legacy direct `import_provenance(log, events)` callers retain full-prefix semantics;
use the origin-pinned native path for overlapping or transitive multiple origins.

## Partial-range boundary and original evidence

Round 1 incorrectly conflated reconciliation/range restoration with the smaller
completed-paper reuse feature. GX31 in DECISIONS.md supersedes its blanket no-resume
policy. This change does not restore partial ranges or resume into an occupied
run directory. A failed paper may repay accepted ranges; completed papers do not.

The original paid full26 run has zero completed paper outcomes. Its accepted
71-item range therefore is not automatically reusable by paper-level resume.
Its charges can still be imported. No content or logs in that original run were
changed. Verified against `theta-source-evidence.json`:

- accepted range SHA256: `03e2022e53138bdfdc535a0238fc6442a8774ce8aaf1dd92db6cce2eac6a06d3`;
- original event-log SHA256: `766257cd90c1baddef7411caf44e5ca1b9b1875c47a4660fc3f607a139b68bc6`.

## Verification evidence

Full pytest: **458 passed, 2 skipped / 460 collected**, 245.88 seconds, exit 0.
Receipt: `theta2-pytest-full-final.txt`. The two skipped tests require paid-provider
opt-in and were intentionally not run. Complete control runner: **181/181 mutations red, 181/181 restorations green**,
exit 0, run sequentially after pytest. This includes 13 new recovery/resume controls.
Receipts: `theta2-negative-controls-full.txt` and
`theta2-negative-controls-results.json`; individual outputs are in
`/home/dev/ara-work/theta/runs/delta-controls/`. All 123 tracked/new source, test and
document files matched their pre-control SHA256 snapshot after restoration.
`git diff --check` passed. Additional executed evidence:

- Initial test-first recovery run: 12 failures / 2 passes (`theta2-red.txt`).
- Finished extraction/recovery targeted run: 59 passed (`theta2-recovery-final.txt`).
- Empty-disposition regression failed before the fix and passed after it
  (`theta2-empty-reuse-red.txt`, targeted run above).
- New and affected production-wire controls were run individually in focused
  batches; every final focused mutation failed and restoration passed.
- Two controls initially survived weak assertions. The repaired tests use a deeper
  origin chain and a cap admitting the next request only if prior cost is lost.
  Both now detect the intended faults. The complete-run receipts above supersede
  those development batches.
- The first broad pytest run was stopped after an obsolete event-position assertion
  failed (159 passed, 1 failed at interruption). That test now selects the estimate
  by event type; it passes in the targeted run. The final full rerun passed as recorded above.

The native CLI regression extracts a corpus with a failed source, imports it into
pilot construction/search, checks citations and methodology, then resumes to reuse
the successful source and retry the failed one. Other tests cover exact threshold
boundaries, failed-evidence injection, changed PDF/input, inherited admission,
allowance resets, overlapping origins and transitive tamper/missing/pin checks.
All fixtures use placeholder content. This proves the native offline lifecycle,
not live model quality or completion of the 26-paper corpus within USD125.

No round-2 prompt/schema change occurred, so the free planner was not rerun. The
round-1 26-paper/66-range counted result remains the existing planning evidence.
Printed extraction preflight is still a conservative whole-selection estimate,
including reused papers; actual admission and the inherited ledger enforce caps.

## Workspace and delivery

Only this worktree/branch was edited. No delegation, paid provider calls, push,
main-checkout edits or eta-branch edits. README documents the new native path;
DECISIONS.md GX31 explains the policy correction, receipt mechanism and boundary.
The verified tree was committed locally, and the working tree is clean.
The full control summary is recorded above; non-author review remains
with the caller. No standalone shipping or PR workflow was run.

## Finding placement

| Finding affecting the next action | Deliverable section |
| --- | --- |
| Continue policy, threshold and failed-evidence exclusion | Resulting behavior |
| Global/unknown-spend and operational stop rules | Resulting behavior |
| Completed-paper reuse, retry identity and inherited costs | Resume and accounting |
| Origin retention, hash trust boundary and legacy import behavior | Provenance and retention |
| Partial ranges remain outside resume; original run has no completed paper | Partial-range boundary and original evidence |
| Live budget/completion unproven; planner and estimate limits | Verification evidence |
| Test/control evidence and development assertion repairs | Verification evidence |
| Original evidence preserved; local-only delivery and caller review | Partial-range boundary and original evidence; Workspace and delivery |

8 findings, 8 placed.


# Round 3

Brief: `/home/dev/ara-work/briefs/theta-round-3.md`. Review:
`/home/dev/ara-work/reports/iota-review.md`, T-B1, T-S1 and T-N1.
Base: `b063433d56f83f058d4941c8c8a30b43ec0cf355`; same branch/worktree, initially clean.
Status: T-B1 and T-S1 fixed; all required offline verification complete.
Revision: `be7468df12d4c0422d54f8ccd881d653cd92bdd4`. Locally committed on
`fix/context-request-without-obligation`; working tree clean; no push.

## T-B1 — acceptance policy

Confirmed: the previous reuse predicate did not receive configuration. Completed
outcomes now carry an explicit versioned acceptance identity (inference policy,
effective extraction model/effort/thinking/fallbacks, provider, prompt/schema
hashes). Changed or absent identities require native extraction/validation again;
original receipts and costs are imported intact. Cap/recovery changes and unrelated
stages preserve compatibility. Both index construction and extract's reuse branch
check the identity. Interpretation changes require a version bump. Strict source
coverage (`--missing refuse`) is also checked before reuse, so previously accepted
partial papers cannot bypass a newly strict coverage policy.

Legacy completed outcomes without the identity are not automatically reused. This
is a conservative compatibility refusal, not a claim that their old literature is
invalid; its original pinned verification/import remains supported. Existing
native cache replay may still avoid dispatch while applying current validation
with original receipts present. No old evidence is relabelled as current policy.

## T-S1 — stopped descendant ancestry

Confirmed: latest-batch outcome selection hid ancestor successes when an
intermediate run stopped before visiting them. A separate historical candidate
inventory feeds the verified reusable-success index across retained ancestry.
Source and acceptance compatibility and accepted merged-graph receipts remain
mandatory. Conflicting compatible outcomes refuse before import. Latest-batch
publication and current failed-paper disclosure are unchanged.

## API and T-N1 operating boundary

README documents the consumer API: `resume_papers(log, papers, sources, config,
root)` now requires effective configuration and contract root; use
`read_checkpoint`/`verify_imports` for pinned/transitive imports and
`extraction_outcomes` for final literature. `historical_extraction_outcomes` is
only a candidate inventory. Do not hash a deduplicated copied block as if it were
the full origin receipt. Retained attempts keep their original model/configuration
and prompt/schema receipts, including historical rejected attempts.

Eta's branch/integration fixes remain with eta; this task changes no eta files.
T-N1 is retained: preserve origin logs, whole-paper resume only. The original live
run completed no paper; its paid partial range is not reusable through this feature.
No paid generation, live token counting, semantic quality claim or USD125 completion
claim is made. Both original paid-evidence file hashes were rechecked against
`theta-source-evidence.json` and remain unchanged. No prompt/schema changed, so no
free planner rerun is required.

## Verification and delivery

The initial regression run recorded 12 failures / 1 pass (`theta3-red.txt`).
After fixes, the policy/recovery suites pass 42 tests (`theta3-targeted.txt`).
They cover fresh versus resumed inference policy through direct/native CLI paths,
model/stage/interpretation/prompt/schema drift, legacy identities, cap-only reuse,
an intermediate stop before visiting an ancestor success, current failure/history
selection, exact inherited charges, explicit conflict refusal and the execution
boundary's second compatibility check. A test closure initially pointed at its
output path rather than its contract path; that test-only mistake was corrected.

Final targeted verification: **44 passed**, 15.48s (`theta3-targeted-final.txt`).
All nine focused controls (seven new, two affected existing) failed under mutation
and passed after restoration (`theta3-focused-controls.txt`, `theta3-strict-control.txt`).
Final full pytest: **473 passed, 2 skipped / 475 collected**, exit 0, 249.81s
(`theta3-pytest-full-final.txt`). Paid-provider tests were disabled explicitly.
Complete control runner: **188/188 mutations red, 188/188 restorations green**,
exit 0, run sequentially after pytest. All 124 source/test/document files matched
the pre-control SHA256 snapshot exactly. Receipts: `theta3-negative-controls-full.txt`,
`theta3-negative-controls-results.json`, and per-case files under
`/home/dev/ara-work/theta/runs/delta-controls/`. `git diff --check` passed.
No push, delegation or paid calls. The eta integration remains for eta's rebase;
this task does not claim the merged frozen-T path is verified.

## Round 3 finding placement

| Finding | Placement |
| --- | --- |
| T-B1: acceptance-policy bypass and legacy compatibility restriction | T-B1 — acceptance policy |
| T-S1: stopped descendant loses reusable ancestry; conflict handling | T-S1 — stopped descendant ancestry |
| T-N1 and eta API/operating requirements | API and T-N1 operating boundary |

3 findings, 3 placed.


Round-3 verification note: the first broad pytest run was intentionally interrupted
(with no observed failures) to add the related strict-coverage reuse regression.
It failed before moving coverage validation ahead of reuse (`theta3-strict-red.txt`).
The final full rerun and complete control runner passed with that fix.
