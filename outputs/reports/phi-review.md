# Phi — sigma round 4, xi round 4, and integration

**Recommendation: merge sigma and merge xi; 0 blocking findings.** The combined tree passed the full offline suite and all 305 controls. The real stopped pilot was accepted through the native resume CLI offline. The two additive merge conflicts are resolved in scratch and must be preserved when integrating. This is a solo, non-author review; neither author branch was edited. No paid calls, delegation, push, or live pilot continuation.

## Reviewed revisions and integration

Base: `1411e91c70a6537422dbfece6f6ed1301b90e748`.
Sigma: `e5e40cb99a5e827be8c054feb171d400346a700e` (`fix/bounded-closure`).
Xi: `3350ef1b41574566fe549d02cb5827fa591dc16f` (`feat/run-report`).

Scratch clone: `/home/dev/ara-work/phi-integration`; merged revision: `c5d04ee347c8f24216b2aa1405e3df68d393f20a`.

Sigma fast-forwarded onto the requested base. Merging xi then conflicted in `DECISIONS.md` and `tests/integration/negative_controls.py`. Both conflicts were independent additions at the same insertion point. I retained both decision sections and all controls; production code merged without conflicts. The combined registry contains 305 uniquely named controls across 27 production files, with every mutation anchor occurring exactly once. Integration is therefore reported as **conflicts**, even though they are resolved in the scratch merge. Reproduce this additive resolution when integrating; do not choose just one branch's registry.

## Sigma — receipt restoration and accounting

Source review traced the CLI into the existing construction/prepare/search lifecycle, `load_construction_resume`, `ModelCalls`, `Budget`, and methodology export. The resume loader verifies the event chain and anchor, the single plan and its artifact, contiguous window outcomes, accepted artifact hashes and evidence IDs, skipped omission/closure receipts, and a terminal refusal linked to its dispatched window and reservation. The native planner must reproduce the same plan ID. Previously consumed correction allowances are subtracted. Restored commitments and symbols enter the normal merge/recount/freeze path without replaying accepted model calls. The CLI uses stored run inputs/configuration and an exclusive resume lock.

The provider-skip path retains one unknown-at-reservation MODEL receipt, enforces caps, emits `construction_provider_refusal` with `policy=count-at-reservation`, and lets construction record the window omission and continue. Methodology preserves that policy and incomplete-accounting status; it does not relabel the reservation as measured spend. Selection, formalization, and targeted correction all use this boundary. Authentication, rate-limit, server and unreceipted transport failures remain fatal. Exact-size diagnostics are allowlisted; the original suppressed provider complaint remains unknown.

This is bounded recovery from the recorded terminal rejection, not general crash recovery. Live provider counts must reproduce the plan, and later interruptions or budget stops can still refuse continuation. No claim is made that the real pilot will finish construction, freeze, or search successfully.

**Native real-pilot CLI replay passed.** On a scratch copy of `/home/dev/ara-scaffold/runs/overnight6-pilot`, the CLI restored all 17 completed windows, including **7 accepted batches / 140 commitments**, reproduced plan ID `0c05ea4383c09b28bb865ce44c3eb2dbfb8efde6b49c16888989215a1efe2581`, skipped terminal window 17, and reached the selection request for window 18. It made **zero dispatches and added USD0.00**. The original log is an exact byte prefix of the replay log, both chains/anchors verify, all 18 original construction artifacts match, and the total ledger cost is unchanged. Original log SHA-256: `c44b443a82130252cebc15dcb2ac34058f9c3c6c2a1180dd53f1fa5780fad3b3`.

The provider supplied only previously recorded counts; sockets and generation were forbidden. CLI exit **2** is intentional: the first unrecorded window-18 selection count triggers the offline stop, before any `call_start`. The runtime emits a zero-charge, zero-token rejected MODEL receipt for that pre-dispatch failure. My initial final assertion incorrectly prohibited every MODEL-labelled event, so the harness reported an assertion failure after the native path had completed correctly. I corrected the assertion and independently verified the saved log without replaying construction. See [resume-offline.json](phi-evidence/resume-offline.json), [resume_offline.py](phi-evidence/resume_offline.py), [verify_resume.py](phi-evidence/verify_resume.py), and the retained initial/verification transcripts.

**Operational latency:** the native CLI recorded **1,447.03 seconds (24.1 minutes)** before its final timing receipt. Recounting repeatedly verifies the large append-only chain; this is substantial CPU-bound startup time before any dispatch. No logging check was bypassed. This proves offline acceptance and reuse, not live completion or a short startup time.

## Xi — preserved evidence and readable overview

Independent audit of `/home/dev/ara-scaffold/runs/overnight-report-v2/` passed:

- 27 input runs; HTML **2,453,319 bytes (2.453319 decimal MB)**, below 15 MB.
- **6,643** canonical event bodies cover **44,324** original chain occurrences and **37,681** imported run references. Every exported envelope reconstructed its source row exactly, including sequence and original chain hash; all source chains/anchors, event hashes, occurrence lists, and original/imported-by classifications matched.
- **313** copied artifacts matched both their recorded SHA-256 and original bytes; **763** complete paper histories matched source extraction receipts. All per-run section files existed.
- **2,314** HTML links and local anchors were valid.

The code hashes the complete original event body, rather than the run-specific envelope. Thus imported copies share one body while occurrence identity and provenance remain explicit. The HTML limits only previews; complete section/paper files are written before section truncation, complete events/artifacts are externalized, and whole-section overflow remains reachable through `data.json`. Independent recomputation from the unique MODEL event bodies matched combined accounting exactly: **USD131.785270 measured** (316 receipts), **USD1.844820 unknown at reservation** (3 receipts), and **USD133.630090 budget-accounted** (319 receipts). See [accounting-audit.json](phi-evidence/accounting-audit.json). These are totals across all 27 supplied historical runs, not just part 6. Combined accounting deduplicates identical receipts; per-run totals include inherited history and must not be added together.

Headless Chromium **143.0.7499.4** opened the complete page with **246 sections**, zero page errors, and matching document/viewport widths at desktop **1440/1440** and mobile **390/390**. Desktop and mobile screenshots were inspected. Tables scroll within the mobile layout. Evidence: [report-audit.json](phi-evidence/report-audit.json), [browser.json](phi-evidence/browser.json), and the adjacent audit/browser scripts and screenshots.

The complete output is **7,994 files / 1,052,011,317 bytes**. The entire sibling-file directory must travel with the HTML; the HTML alone is not a complete report. The real lineage contains no completed search trees, so it cannot prove tree rendering. Native placeholder tests cover complete trace sidecars with bounded previews, including the 500-state case. This review audited xi's existing real output and exercised rendering through merged tests; it did not rerender the entire real lineage.

## Merged verification and limits

Full pytest exited 0: **672 passed, 2 skipped, 674 collected**, in **334.70 seconds**. The skips are opt-in live-provider checks. **Complete control runner passed: 305/305 mutations failed their targeted tests, and all 305 restored runs passed**, exit 0. It started after pytest passed in `/home/dev/ara-work/phi-controls`, a second independent clone of the exact same merge, so its temporary source mutations could not affect the native replay in `phi-integration`. All **27 mutation-target files** match their pre-control SHA-256 hashes exactly. Both scratch clones are clean at the merged revision; whitespace checks pass. Both author branches remain clean at the requested heads. Evidence directory: `/home/dev/ara-work/reports/phi-evidence/`. The [consolidated receipt](phi-evidence/verification.json) links the facts; [pytest transcript](phi-evidence/pytest.txt), [control transcript](phi-evidence/controls.txt), [all control results](phi-evidence/control-details/results.json), 610 red/green transcripts, and before/after hash manifests are retained.

The relevant project is ARA, which uses locked uv/pytest and its native mutation runner; the unrelated Buckeye workspace's pnpm delivery gate is not applicable. No separate lint/typecheck is configured. Review scope is the two round-four diffs and their integration, not a semantic audit of the underlying source literature or a new paid execution.

## Finding placement

| Action-relevant observation | Placement |
| --- | --- |
| Two additive integration conflicts; preserve both decisions/control sets | Reviewed revisions and integration |
| Resume integrity, no repayment/double count, refusal policy, corrected harness assertion, 24-minute startup, and bounded recovery limits | Sigma — receipt restoration and accounting |
| Lossless imported history and artifact/paper retention; carry sibling files and do not sum inherited run totals | Xi — preserved evidence and readable overview |
| Real HTML/browser proof and the absence of real completed-tree proof | Xi — preserved evidence and readable overview |
| Exact merged tests/controls, mutation restoration, and unexecuted live scope | Merged verification and limits |

5 findings, 5 placed

DONE phi review sigma=merge xi=merge blocking=0 integration=conflicts:DECISIONS.md,tests/integration/negative_controls.py merged_tests=672/674 resume_offline=ok
