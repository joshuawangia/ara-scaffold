# Theta context request fix

## Result

Implemented in `/home/dev/ara-work/theta` on
`fix/context-request-without-obligation`, based on
`ba3a004d422467a0aed8a77be9407587d265a514`. Committed locally as `188784e6e11309bf7658bdce31dd70f933aea5d8`. Working tree clean.
No push, delegation, paid generation, extraction rerun, or pilot run.

Mode-specific response schemas and targeted recovery fix the observed blocker.
Policy: **stop-on-paper-failure** and refuse completed literature.
**Resume: no**; deferred under the brief's small-native-path exception. The
original 71-item range is preserved but this patch cannot reuse it automatically.
Non-author review remains outstanding as requested.

## Diagnosis and contract

The original 30-event log validates. Range 1 used a targeted correction. The
second initial range returned one item, `coverage_complete=true`, `new_gaps=[]`,
and `context_request={"pages":[],"evidence_ids":[]}`. It was rejected with
`InvalidOutput: context request requires a pending obligation`.

At the base revision, `ModelCalls.render`, `_execute_once` and `count_request`
loaded one schema exposing reconciliation fields in every mode. Provider schema
projection preserved them, although the prompt prohibited them outside
reconciliation. `_extract_paper.run.check` treated the dictionary containing two
empty arrays as a request. The single correction counter belonged to the whole
paper and had been consumed by range 1, so the second rejection killed extraction.
These causes were traced through actual request/response field inventories,
validation, correction, accounting, corpus publication and pilot import; no source
content was copied into tests or this report.

`ModelCalls.response_schema` now specializes the schema once by request mode and
supplied obligations. Rendering, provider counting, dispatch, cache identity and
local validation use that contract. Initial ranges and graph review cannot express
context requests, pending IDs or resolutions. Obligation continuation can. A
correction inherits its original mode. Reconciliation cannot express an
`empty_reason` disposition.

Initial missing context is recorded as `new_gaps`, assigned stable obligation IDs,
and handled through the existing counted reconciliation queue. This preserves
page-linked source evidence and cross-range obligations without inventing another
fetch lifecycle or dropping fields. Malformed model output is still logged,
charged, rejected and eligible for correction; no request is silently discarded.

The mode scan also found empty/unread/unknown/cyclic/over-limit requests could be
rejected after acceptance, outside correction recovery. Those checks now occur
inside response validation. Cycle keys sort both lists so order cannot evade a
repeat check. Capacity admission remains counted, with oversized context refused
and obligations retained. Existing positive requested-context, graph review, new-gap
queue and cross-window reconciliation tests remain part of verification.

Decision and tradeoffs: `DECISIONS.md`, GX30 (superseding GX25's correction scope).

## Recovery, failure policy and downstream provenance

Each range/reconciliation response gets its configured zero or one targeted
correction. Corrections do not recurse and do not invoke extra generic retries.
Every attempt still consumes the existing paper-wide continuation allowance and
is admitted against paper/run cost caps. The patch preserves omitted candidate
items and validates the entire merged graph under the original mode.

Terminal failure records `extraction_outcome(status=failed)` plus an
`extraction_stopped` receipt naming the policy, failed source, previously completed
sources and sources not attempted. Methodology exposes the stop receipt. The
exception stops the corpus and no completed literature or sidecar is published.
Missing-PDF/partial-readable-source policies remain separately explicit.

The pilot requires a complete, hash-pinned extraction-log prefix, exact literature
reconstruction and original accepted MODEL lineage; it imports upstream charges
before admitting downstream calls. The fix retains those requirements. Failed
partial extraction cannot supply the native completed literature handoff. Existing
native extract-to-build-T and imported-cost tests are exercised by the full suite.

## Resume limitation and next action

There is no small native restore path. CLI refuses nonempty extraction directories;
legacy range files lack a pinned acceptance hash, accepted correction MODEL receipts
contain patches rather than full graphs, and reconciliation has no restored cursor,
queue or turn state. Appending outcomes after a failure would also break the
current verifier, which reconstructs literature from every outcome event.
Cross-run cache replay without original receipts fails provenance, and the changed
prompt/schema invalidate prior cache keys.

A sound resume needs legacy graph reconstruction and receipt binding, restored
obligation/cursor state, charge/allowance preservation, and explicit outcome-attempt
selection. Simply skipping files is insufficient. This work documents that boundary
as authorized by the brief rather than presenting unsafe reuse as resume. CLI now
states the limitation instead of recommending a new directory/cache replay as if
that supplied production provenance. A regression verifies refusal before provider
construction and byte-for-byte preservation of the existing directory.

**Do not launch a fresh paid extraction expecting the 71 accepted items to be
reused.** A fresh run can repay that work. Preserve the original run for a separately
implemented and reviewed resume path, or explicitly accept re-extraction cost.
No additional authorization for paid work is implied by this report.

## Verification

- Initial offline regression at base: **12 failed, 1 passed** (`theta-red.txt`).
  The same empty-array request shape failed after a first-range correction.
- Affected suites: **71 passed** (`theta-targeted.txt`); focused coverage:
  **26 passed** (`theta-final-targeted.txt`); final affected tests **48 passed**
  (`theta-final-focused.txt`). All content is placeholder-only.
  Coverage includes initial/review/obligation and correction schema contracts,
  candidate preservation, empty/unread/unknown request recovery, request limits and
  cycles, paper cap admission, stop-on-failure, provenance and resume refusal.
- Final `uv run pytest`: **430 passed, 2 skipped / 432 collected**, 232.54 seconds,
  exit 0 (`theta-pytest.txt`). The first green run is retained separately in
  `theta-pytest-first-green.txt`. The skips are opt-in live tests. An earlier run was interrupted
  at 159 passed/1 failing new test because the cycle fixture reused identical
  context and hit the cache; the fixture was corrected. That interrupted run is
  retained as `theta-pytest-interrupted.txt` and is not passing evidence.
- Initial integration controls stopped at `paper_count_finite` after 159 controls
  killed their mutations and restored green. Disabling the finite guard still
  passed its test because Python 3.15's incidental JSON serialization error
  contained “paper,” matching the broad exception assertion. The test now requires
  the intended configuration-error prefix. No production budget guard changed.
  The cycle test also now counts MODEL receipts, so a cached accepted turn cannot
  hide behind an unchanged provider-call count.
- All nine remaining/new controls then passed red/restored-green
  (`theta-focused-controls.txt`), including finite guards, reordered cycles,
  pre-acceptance request recovery, correction admission and terminal failure.
  Final full `uv run pytest` was followed sequentially by the complete
  `uv run python tests/integration/negative_controls.py`: **168/168 red and 168/168
  restored green**, exit 0 (`theta-negctl.txt`, `theta-final-controls.json`, and
  individual traces under `theta/runs/delta-controls/`). No source-dependent checks
  ran concurrently with mutations. `git diff --check` passed after restoration.
- No live generation/semantic fidelity or completed 26-paper extraction is claimed.

## Free counted plan

The rendered schema changed, so the native provider-count planner ran over the same
26 selected PDFs, using the original config/manifest/PDFs read-only. New outputs are
under `theta/runs/theta-free-plan/`. Provider documentation at
https://platform.claude.com/docs/en/build-with-claude/token-counting.md was checked:
“Token counting is free to use.” The planner cannot generate and uses zero generation
caps. Its 136-event chain validates with no MODEL/call_start and zero generation calls.

| Measure | Result |
|---|---:|
| Papers / physical pages | 26 / 1,379 |
| Initial ranges fitting context | 66 / 66 |
| Readable pages / affected pages | 1,368 / 82 |
| Counted initial input tokens | 1,569,754 |
| Initial output-density cost scenario | USD48.888770 |
| Initial full-output reservations | USD60.648770 |

These are **initial extraction only**; they exclude reconciliation, corrections,
retries, construction and pilot work. They are not comparable to the older
USD63.004860 scenario including estimated review without restoring its assumptions.
Reader encoding/xref warnings remain; counted fit is not proof of source coverage.

Plan SHA256:
`120b91b276f4867b3541586b35c3af4328e7cecd69b719c86f5cd53e86cff2c6`.
Receipts: `theta-planner-command.json`, `theta-planner-console.txt`,
`theta-planner-receipt.json`; numeric artifact:
`/home/dev/ara-work/theta/runs/theta-free-plan/extraction-plan.json`.

## Evidence preservation and execution record

Original source evidence hashes are in `theta-source-evidence.json`: 30 valid log
records; 71 immutable range items, range SHA256
`03e2022e53138bdfdc535a0238fc6442a8774ce8aaf1dd92db6cce2eac6a06d3`.
Main tracked tree and eta branch were not edited. All task code is isolated in theta.

Work execution was native Codex, inline, no external engine binding or fallback,
no worker run ID. The brief governed implementation/verification/local commit;
standalone shipping/review/PR steps were skipped because the brief assigns later
non-author review and prohibits push. Current revision is `188784e6e11309bf7658bdce31dd70f933aea5d8`; the working tree is clean.
Main remains clean at the requested base. Both original evidence hashes were
rechecked unchanged after verification. All eight findings below have a deliverable
section. The next external step is non-author review; any paid rerun needs the
resume/cost decision described above. Structured execution receipt:
`theta-work-execution.json`.

## Finding placement

| Finding that changes action | Placement |
|---|---|
| F1: Initial wire/prompt mismatch permits the observed empty request | Diagnosis and contract |
| F2: A first-range correction must not consume later recovery; global caps still apply | Recovery, failure policy and downstream provenance |
| F3: Review/continuation checks must run before acceptance for recovery; cycles use sets | Diagnosis and contract |
| F4: Terminal failure stops the corpus and prevents completed pilot handoff | Recovery, failure policy and downstream provenance |
| F5: Partial resume remains unsupported; a fresh run can repay the saved range | Result; Resume limitation and next action |
| F6: New free counts fit, but exclude later work and retain 82 affected pages | Free counted plan |
| F7: Offline structural proof does not establish live semantic completion; independent review remains | Result; Verification |
| F8: An old budget negative control accepted an unrelated serializer error; strengthened assertion and rerun required | Verification |

8 findings, 8 placed

DONE theta fix head=188784e6e11309bf7658bdce31dd70f933aea5d8 tests=430/432 negctl=pass policy=stop-on-paper-failure resume=no report=/home/dev/ara-work/reports/theta-context-fix.md
