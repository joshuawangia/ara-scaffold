# Xi Round 26 — semantic pairs and conflict feedback

Base `68ca9654537286c98fbd11cffb20f5f32481508b`, branch `feat/run-report`, checkout `/home/dev/ara-work/xi`. Offline only, no push. Final revision `80a344892d9acd1933bf47c1b6fd8fd986bbee5b`. Full gates are complete and the checkout is clean.

## Result

Semantic discovery compares content across private formula vocabularies. It ranks cross-paper pairs by shared catalogue-definition terms and then content overlap, keeps the configured top N (default 60), and classifies each pair through the existing cached, schema-validated, counted and logged model boundary. Each request contains the pair, its definitions and verified source roles, and frozen hashes; it excludes the global task topic and full T. The same provider handles the call. Source roles include endorsed, reported and attacked, with at least one endorsed side. Restricted views remain ineligible as positive support.

`contradicts` and `in_tension` create `semantic_conflict` resolution obligations. `compatible` and `unrelated` do not. These are model judgments, never formal contradictions or edits to frozen T. Invalid outputs and local context refusals are logged as unclassified pairs; global accounting and infrastructure failures still propagate. Optional new Gap metadata preserves old encodings when absent. Frozen CommitmentSet, catalogue and provenance contracts are unchanged.

Native paired-search findings now feed a gated resolution proposal step. Tier 2 gaps retain the actual positive/negative conclusions, route IDs and support from each route. Existing novelty, own-thesis, fidelity, gap, stance and cross-paper gates remain. The report and methodology expose Tier 1 repairs, Tier 2 opposing routes and proposed resolution candidates with linked lossless evidence. Current findings are bound to the current search generation; stale findings and candidate receipts cannot stand in for a resumed analysis.

## Scope and limits

- Lexical/topic-word overlap and top-N retention are bounded retrieval, not an exhaustive semantic conflict census. Semantically related pairs with no shared words can be missed. Zero disables the stage explicitly; missing legacy metadata remains unavailable.
- Classification quality is not established by the fake provider. A reported view is not the reporting paper's endorsement; the prompt preserves that distinction. Neither a classified tension nor an engine conflict supplies missing resolution evidence.
- Tier 1 repair proposals do not mutate T. Tier 2 resolution candidates are explicitly `proposed_not_searched`. This round implements the brief's resolution-proposal requirement; it does not create another search batch. The optional clarification about automatic follow-up search received no answer, so the narrower explicit scope was retained. No closure or resolved conflict is claimed for these candidates.
- Whole-T classical novelty remains strict, including its limitation when T is inconsistent. All existing route admission gates remain.
- The new classifier schema changes the Codex preflight manifest. A live pilot requires refreshed live preflight; only fake transport/schema proof was run here.
- Reports expose only recorded bounded analyses. Missing or partial paired analysis is not evidence of no conflicts. Historical receipts remain in the original event inventory.

## Real pilot-5 offline census

Source: `/home/dev/ara-scaffold/runs/codex-fork-5`. Entry point: `tools/offline_semantic_conflicts.py --source <source> --out <fresh-directory>` with `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked python`.

Final executed census: **7,693 eligible pairs**, **60 selected pairs**, **60 fake classifier dispatches**. Synthetic labels cycle through all four outcomes: 15 each, yielding 30 synthetic semantic gaps. One representative semantic gap generated one mechanically accepted fake resolution candidate. No literature content or substantive conflict claim is copied into this report. Maximum classifier input-plus-output estimate was 6,656 tokens using the production Codex CLI offline calibration, not an actual live tokenizer measurement. All three source frozen artifacts match the Round 25 saved hashes and the final diagnostic copies byte-for-byte; hashes are in `runs/xi-round26/offline-freeze-hashes.json`.

Evidence: `runs/xi-round26/fork5-final/summary.json` contains pair IDs and ranks; adjacent events retain complete native fake-call receipts. These synthetic labels verify plumbing only and cannot establish how many real semantic conflicts exist. No paid or network call was made.

## Verification

Initial seven regressions failed before implementation on the expected missing behavior. The implemented seven passed in 43.58 s. Broader affected suite: 111 passed, one test assertion failed because it referenced a nonexistent Budget property; the assertion was repaired to inspect the actual STOP scope. Manual inspection then found stale report-generation reuse; the new regression failed before its repair. The repaired 74-test semantic/gap/report/schema suite passed in 24.94 s. All 15 initial production-wire controls passed. An additional native disjoint-support regression passed after fixing its leaf-mapping fixture; its control also passed. All 16 new controls are registered (597 total). The first full run was interrupted after 287 passing tests and a stale preflight inventory assertion (expected 16, actual 17). The new classifier schema was accepted; expected counts were updated and explicit classifier-preflight coverage added. Both repaired preflight tests passed (10.48 s and 9.82 s). The next full run stopped after 468 passing tests and four failures from two old fake-provider fixtures that did not recognize classify_conflict. Those fixtures now return explicit compatible judgments for their placeholder comparisons, preserving all paper-matching assertions. The repaired affected-consumer suite passed **103/103** in **191.00 s**. The third full run completed with **1,304 passed, 4 skipped and 1 failed** in **1,353.83 s**. Its sole failure was the capacity-53 offline SDK fixture missing classify_conflict; that fixture now supplies a compatible placeholder response. The repaired capacity-53 CLI regression passed in **290.20 s**. The final full suite passed **1,305 tests, 4 skipped / 1,309 collected**, exit 0, in **1,593.87 s**. The source hash check passed, and only then did the full **597-control** runner start. That control run was interrupted at the user-requested checkpoint; all 242 source hashes were restored. It is not a completed control receipt. Final gates are rerun after the blocker fixes below.

Simplification used the ce-simplify-code rubrics inline: reused the common gap-target proposal path, computed route support once per route, removed redundant JSON parsing and kept the proof tests. No project lint/typecheck command is configured; pytest and diff checks are the local gates.

Code review: skipped (ce-code-review unavailable). Its independent review path requires dispatching reviewer contexts; the standing operator instruction prohibits starting workers without approval. No independent review is claimed. Manual review covered frozen codecs, model isolation, cache inputs, source stance, native analysis feedback, report generation binding and negative-control anchors.

## Findings placement

1. Retrieval is bounded and can miss conflicts without lexical overlap — Scope and limits.
2. Synthetic labels and a fake resolution candidate prove plumbing only — Real pilot-5 offline census.
3. Source stance and unchanged formal/novelty gates limit admissible evidence — Result; Scope and limits.
4. Tier 2 candidates are proposed, not searched or resolved — Scope and limits.
5. Stale report-generation reuse was found and repaired with red-before-fix evidence — Result; Verification.
6. Offline token estimates and unavailable independent review limit verification claims — Real pilot-5 offline census; Verification.

7. A new live Codex preflight receipt is required before a live pilot — Scope and limits.

**7 findings, 7 placed.**

## Round-25 review blockers repaired in Round 26

R25-F1: the shared engine/runtime CQ predicate now compares Unicode-normalized words across whitespace, markdown, quotes and case. Named partial-answer and insufficient-evidence markers downgrade; original answer text and supporting IDs are retained. Native route tests stay OPEN and unselectable; direct engine CQ checks also refuse these answers. This lexical guard is conservative, not general semantic validation.

R25-F2: exact frozen content definitions participate in stance-conflict detection only under verified content semantics. AST substitution preserves connective structure, arguments, binders and polarity. A native distinct-symbol/distinct-text regression now proposes a gap target retaining both endorsed support obligations. Different definitions, polarity, arguments and structure do not match. Frozen artifacts remain byte-identical.

Red evidence: 10 failures/15 passes before the fixes; two additional underscore-markdown regressions failed before the delimiter repair. Final focused suite: 38 passed in 32.18 seconds. Three new production-wire controls and three affected controls are run before the full gates.

Both blockers are placed in this section; combined with the seven findings above: **9 findings, 9 placed.**

Affected controls: all six mutations failed with exit 1 and restored tests passed. Final offline census rerun after both fixes (`fork5-blockers`) retains 7,693 eligible / 60 selected pairs, 30 synthetic gaps, one accepted fake candidate and 6,656 estimated tokens. All three frozen artifacts are byte-identical to the source.

Final post-blocker full pytest: **1,319 passed, 4 skipped / 1,323 collected**, exit 0 in 1,626.79 seconds. The driver verified all pinned source hashes before starting the sequential 600-control runner. The resumed full control census passed all 600 controls.

The final tool session exited with signal 143 after 199 completed controls. No Xi test process remained; every pinned source hash matched. The 199 ordered red/restored receipts were preserved and validated against the control manifest. The remaining 401 controls are resumed sequentially in a detached local process; the driver will combine the receipts and verify all source hashes again. This is a resumed full control census, not an uninterrupted run.

## Final local receipt

All **600/600** controls exited 1 under mutation and 0 after restoration: 199 preserved ordered receipts plus 401 resumed receipts. The resumed runner exited 0. All **242** pinned source hashes match both the restored working tree and the committed tree (symlink targets verified). Full pytest preceded the controls: **1,319 passed, 4 skipped / 1,323 collected**. `git diff --check` and clean-tree checks pass. No paid/network call, worker dispatch or push occurred.

The three new blocker mutants fail at their intended assertions: formatting again closes a partial-answer route; removing definition matching loses the gap; dropping structure creates a false gap. Their restored tests all pass. Full evidence: `runs/xi-round26/pytest-full.txt`, `control-results.json`, `gates.json`, `controls-full.txt`, `controls-resume.txt`, `source-before.json`, `source-after.json`, plus native offline `fork5-blockers/summary.json`.

Code review: skipped (ce-code-review unavailable). The standing operator instruction prohibits dispatching its required independent reviewer contexts; manual source/diff review and the executed controls are recorded, with no independent-review claim.

**9 findings, 9 placed.**

DONE xi round26 head=80a344892d9acd1933bf47c1b6fd8fd986bbee5b tests=1319/1323 negctl=pass semantic_pairs=60 tier_findings_reported=yes fixed=kappa4-R25-F1,kappa4-R25-F2
