# Kappa4 delivery review — round 30 and round 30b

**Verdict: merge round30b `6c6cf84`, including Pi3 `3c9c8a4`; zero open blockers.** Independent final-head verification: **253 passed / 254 collected** (one paid-provider skip), **170/170 mutation controls**, and **33 probe scenarios**. This verdict explicitly covers round30b. It does **not** approve the older `d24288b` alone: that head remains **fix-first, one blocker**, because it retains the fresh schema-retry defect described below.

## Scope and intent

Reviewed pinned, independent local checkouts of delivery `d24288be09769ac8768cd75b7d95d68f680925b4`, Pi3 `3c9c8a41e6eb3b4f57f6cda83eee76d1893953c6`, and round30b `6c6cf84d76201faccb6ab1399e5bce52b6b51750`. Round30b has the first two heads as its parents. Nu4 `72c11e7`, Pi3 `1bd07d5`, Xi `0c4d472`, and Sigma `7d19ccc` are verified ancestors. The additional Pi diff over `1bd07d5` has six files; its only production change is in `essay_audit.py`. The merged audit module matches Pi3's final module exactly. No paid/live calls, delegation, author-tree edits, source fixes, commits, or pushes.

Intent: preserve adverse audit obligations and frozen-source references throughout writing, verification, resume and publication; permit bounded corrections without widening repair authority; preserve earlier reviewed search, provider and integration gates.

## R2-F1 — closed: partial adverse history remains binding

Replayed the original incomplete-inventory, duplicate-inventory, and unrelated-unknown-node variants. Each initial call refuses; two subsequent batches of clean samples still refuse. Complete adverse history also remains binding. A native `compose` failure followed by a fresh `ModelCalls` object, the original cache/log, and unchanged imported text cannot export; the retained adverse sentence triggers repair instead. Schema correction can change the wire prompt without losing the original audit obligation.

The recovery admits only individually schema-valid, in-range adverse labels with valid node references. Invalid responses provide no clean verdict. Their retained adverse flags and unusable-history reasons appear in the consensus receipt. This is conservative union of validated labels, not an assertion that every malformed response can be interpreted.

Independent resume probes with two and three rounds already used permit, respectively, only round three and no further semantic repair. An interleaved unrelated route does not reset the allowance. Both persistent-adverse cases refuse export.

Evidence: [audit probes](../kappa4-dlv30b-checkout/runs/kappa4-dlv/audit-probes.json), [corrected history](../kappa4-dlv30b-checkout/runs/kappa4-dlv/corrected-history-probe.json). Source: [partial recovery](../kappa4-dlv30b-checkout/ara/runtime/essay_audit.py:104), [resume allowance](../kappa4-dlv30b-checkout/ara/runtime/essay_audit.py:235).

## R2-F2 — closed: local source citations survive web absence

The native competition-length reproduction now exports with **2 → 2 bibliography entries**, unchanged body/citation markers, and unchanged frozen artifacts. Exact locally verified references are removed from the external verifier's item list; an empty web result cannot classify them as unverified or delete them. The old fixture without retained pages now explicitly refuses before web dispatch, retaining its input unchanged. This is an explicit refusal where local evidence is unavailable, not a fabricated local verification.

Nine independent citation/budget/export cases verify that:

- The citation-only pass appends approved markers to the original sentence bytes. New prose and changed node markers refuse. Even a whitespace-only model response yields byte-identical original prose after markers are removed.
- The pass leaves an exhausted semantic allowance at three. A subsequent adverse audit refuses; it cannot acquire a fresh repair budget.
- Empty support coverage, one missing support citation, and a wrong bibliography each refuse export and remove a stale essay.

Production checks distinguish unavailable evidence from positive mismatch. Page identity, retained-text hashes, grounding, bibliography and exact quotations are checked locally. A proven mismatch can be removed with a recorded reason; missing local evidence cannot be converted into proof of mismatch. Verification is followed by the final audit and independent export support-coverage check.

Evidence: [citation probes](../kappa4-dlv30b-checkout/runs/kappa4-dlv/citation-probes.json), `frozen_citations` in the audit probes above. Source: [local verification and restoration](../kappa4-dlv30b-checkout/ara/runtime/citations.py), [native composition](../kappa4-dlv30b-checkout/ara/runtime/orchestration.py:225).

## DLV-F1 — P1 on d24288b; closed by Pi3 3c9c8a4 and round30b

The older head can discard a valid adverse label generated during a schema retry inside the *current* fresh audit batch. A malformed response flags sentence 2 but has a separate invalid label. Its clean corrected response and the other two clean samples permit unchanged export. The same hole exists after publication verification: the final gate can publish despite that rejected response's valid adverse label.

Independently reproduced on `d24288b`; then replayed on Pi3's final head and on the actual round30b merge. The fix scans the newly appended model receipts after collecting the batch and unions their valid partial adverse labels before deciding. Malformed/adverse responses at sample positions one and three now refuse; malformed non-adverse counterparts can still be corrected. Native composition cannot export the unchanged draft. The post-verification publication reproduction makes seven audit dispatches and refuses publication.

This is why the verdict must distinguish the two delivery heads. The Pi3 delta is required, not merely an additional passing-test receipt.

Evidence: [old-head reproduction](../kappa4-dlv-checkout/runs/kappa4-dlv/fresh-retry.json), [round30b replay](../kappa4-dlv30b-checkout/runs/kappa4-dlv/fresh-retry.json), [post-verification publication replay](../kappa4-dlv30b-checkout/runs/kappa4-dlv/publication-retry.json). Source: [new-receipt collection](../kappa4-dlv30b-checkout/ara/runtime/essay_audit.py:196).

## Publication repair bounds and preserved integration

Three independent retry scenarios exercise the native publication loop. A structurally invalid repair followed by a valid correction uses round sequence `[1, 1]` and succeeds after re-audit. Persistent adverse content uses `[1, 1, 2, 2, 3, 3]`, then retains the original as an explicitly failed polish. Persistent structurally invalid output uses `[1, 1]`, accepts zero repairs, and stops. Retry feedback reports the actual reading-word count, floor, fixed 6,000 ceiling and shrunken sections; it retains the same candidate baseline and flagged spans. Invalid drafts never become audit candidates.

The prior title-movement, unflagged-heading, duplicate-occurrence and persistent unsupported-body probes still refuse the attempted polish. Unflagged blocks, separators and sentence spans remain protected. All accepted repairs face the complete typed audit again; publication uses k≥3 conservative consensus both before and after verification. This prevents bypassing adverse labels; it does not mechanically prove the semantic truth of a clean model judgment.

Imported body identity and title credential probes still refuse before provider dispatch, with sanitized reasons and no sentinel persisted. Alignment bridge citations resolve to their underlying source evidence; the bridge remains a model judgment and cannot become a bibliography entry or source endorsement. Native merged tests exercise composition, section writing, reading references and figures.

Inventory comparison finds **all 808 round30 controls unchanged** in round30b, plus the two Pi3 controls: **810 unique names, each mutation anchor present exactly once**. No control names from the reviewed parent inventories are missing. All **24** earlier adapted control names are included in the scoped execution. Inventory preservation alone is not claimed as execution of all 810 controls.

Evidence: [retry probes](../kappa4-dlv30b-checkout/runs/kappa4-dlv/repair-budget-probes.json), [publication probes](../kappa4-dlv30b-checkout/runs/kappa4-dlv/publication-probes.json), [import probes](../kappa4-dlv30b-checkout/runs/kappa4-dlv/import-probes.json), [ancestry and merge](../kappa4-dlv30b-checkout/runs/kappa4-dlv/integration.json), [control inventory comparison](../kappa4-dlv30b-checkout/runs/kappa4-dlv/control-preservation.json).

## Verification

Independent offline pytest results:

| Pinned head | Scope | Result |
| --- | --- | --- |
| Round30b `6c6cf84` | Audit, citations, writer, publication, verification, delivery alignment integration and native CLI | **253 passed / 254 collected**, one paid-provider skip; 549.08 seconds |
| Original delivery `d24288b` | Same delivery areas plus Codex isolation/context, construction stages, full target context, consistent novelty and Boolean-package gates | **363 passed / 364 collected**, one paid-provider skip; 762.55 seconds |
| Pi3 final `3c9c8a4` | Consensus, quality5 publication, local citations and audit revision | **76 passed / 76 collected**; 192.68 seconds |

Commands use `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked pytest -q` with exact file selections saved in `pytest-files.json`. These are scoped independent reruns, not a claim to have rerun the authors' full suites. The final completion line uses the round30b count, not the aggregate across comparison heads.

**Final-head mutation controls: 170/170 passed.** Every mutated test exited 1 with an actual failed-test transcript; every restored test exited 0 with passing tests. All 340 transcripts were checked for the expected outcomes, collection failures, fatal interpreter errors and local-validation timeout signatures. Pi3's two new controls also passed separately on `3c9c8a4`, with all 259 tracked paths restored.

The actual repository mutation runner ran only after pytest completed. The first 21 controls completed sequentially in the final-head review checkout. To reduce elapsed time, that coordinator was interrupted, all 466 source paths were verified restored, and the remaining 149 cases ran in four independent exact-head clones with separate environments. Each clone executed its assigned mutations sequentially; no source tree had concurrent mutations. The interrupted, uncompleted case was included in the remaining inventory. No interrupted transcript was counted as a passing control. The combined inventory contains each of the 170 selected controls exactly once. All 466 tracked paths were verified restored in the review checkout and all four control clones, with clean Git status and the pinned head unchanged.

Evidence directories are `runs/kappa4-dlv/` under the three pinned review checkouts. Exact pytest selections, logs, source manifests, probe scripts/results and control tuples are retained there. Final evidence: [verified review receipt](../kappa4-dlv30b-checkout/runs/kappa4-dlv/review-verification.json), [pytest log](../kappa4-dlv30b-checkout/runs/kappa4-dlv/pytest.log), [control results](../kappa4-dlv30b-checkout/runs/kappa4-dlv/control-results.json), [transcript verification](../kappa4-dlv30b-checkout/runs/kappa4-dlv/control-transcript-verification.json), [restored source manifest](../kappa4-dlv30b-checkout/runs/kappa4-dlv/source-after-controls.json). These are scoped controls, not an independent execution of all 810 registered cases.

The final round30b independent probe suite contains **33 scenarios**; the old delivery and Pi3-only probe suites are comparison evidence, not additional final-head test counts. Source manifests cover all 466 tracked round30b paths, including the instruction symlink.

## Evidence limits and findings placement

This is an offline code/gate review. No live serving identity, semantic reliability, statistical independence of fresh samples, faithful source interpretation, originality, useful synthesis, visual PDF quality, or successful current essay is established. Nu4's Round 7 report explicitly records **0/2 successful native exports** after substantive audit/repair refusal. Closing the citation defect does not turn those historical runs into successful exports. Legacy runs without source provenance retain their documented limitations and cannot claim local source verification.

Five material observations are placed: R2-F1 closure in its named section; R2-F2 closure in its named section; the old-head DLV-F1 blocker and exact closure boundary in its named section; bounded repairs/control preservation in “Publication repair bounds and preserved integration”; offline/product limits and executed-evidence scope in “Verification” and this section. **5 findings, 5 placed.**

DONE kappa4 dlv verdict=merge blocking=0 tests=253/254 negctl=pass
