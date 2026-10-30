# Zeta fork pilot 4 — blocked, provisional

The native run exited 2 at `propose_cuts` context admission. Two targets were retained, but all four polarity searches failed before cut-proposal dispatch. It did not reach `awaiting_selection`; no route was selected. Results remain **provisional** pending the operator's confirmation of kappa4's review of xi r22 (`25e076a`). The approval of r21 applies to fork pilot 3, not this revision.

[Native full-lineage report](/home/dev/ara-work/reports/overnight/fork4/report.html). Detailed receipts are in `/home/dev/ara-scaffold/runs/codex-fork-4-control/`; delivered evidence is linked from the report and copied alongside this handoff.

## Acceptable pilot — criteria 1–4

Overall: **FAIL**.

| Criterion | Verdict | Evidence |
|---|---|---|
| 1. Clean run | FAIL | `awaiting_selection` false; 0/4 completed searches, 4/4 failed; 30 new MODEL receipts, 0 unsettled calls and 0 unknown-usage calls; 0 Claude calls, $0 new API spend. Three native HUMAN command receipts are preserved; continuation/reporting decisions are in control work notes. |
| 2. Coverage | PASS | 22/26 papers, exceeding the minimum 20; 169/169 commitments page-cited and stance-labelled: 150 endorsed, 13 attacked, 6 reported. |
| 3. Real routes | FAIL | 0 CLOSED-derived, against at least 3 required; 0 mechanically or substantively qualifying cross-paper routes. There is no CLOSED-derived graph to review for a new thesis, licensed substantive scheme, support independence, or stance fidelity. |
| 4. Readable output | PASS | HTML opens: 1.315421 MB, 0 page errors, 0 missing anchors; 0 routes, 0 model-written summaries, 0 missing summaries (0/0 coverage). This is a literal coverage/rendering PASS, not evidence of route-summary quality. The mobile layout check fails with 19 px overflow; see below. |

## Execution, configuration and preservation

Executed revision: `25e076a01bc68dc0d717ab0e9949c7674f3bfc07`, clean detached checkout `/home/dev/ara-work/run-25e076a`. The fresh live schema preflight passed 16/16 cases at this head, followed by the standalone canary and the native fork. The fork reused pilot 5's single frozen T and immediately continued through targets and search. No source changes, new construction, second freeze, route selection, essay writing or additional worker context were introduced.

The effective configuration matches pilot 5 apart from the separate fork cache and fresh schema-proof log: `codex_cli`, requested `gpt-6-luna`, 100M local-token cap, search concurrency 4, no fallbacks, empty audience, 200,000 context limit, and 16,384 cut-proposal output allowance. Serving model identity remains unverified; a requested model pin is not proof of serving identity.

The source prefix, all four frozen artifacts, every pilot 5 source file and the prior handoffs passed their saved hash checks. The previous handoff remains `/home/dev/ara-work/reports/zeta-fork3.md`. No pilot was restarted after resumption. The only remaining background process was a status monitor, which was stopped; it made no provider calls.

## Context blocker and search state

| Job | Goal | Counted input | Output allowance | Total | Limit | Excess |
|---|---|---:|---:|---:|---:|---:|
| 0 | target1 | 199,194 | 16,384 | 215,578 | 200,000 | 15,578 |
| 1 | not:target1 | 199,204 | 16,384 | 215,588 | 200,000 | 15,588 |
| 2 | target2 | 199,346 | 16,384 | 215,730 | 200,000 | 15,730 |
| 3 | not:target2 | 199,366 | 16,384 | 215,750 | 200,000 | 15,750 |

All four context decisions were `refused`; all four jobs recorded `BudgetStop` and the native command exited 2. These are admission-counter values, not measured provider input usage: their method is the calibrated UTF-8 estimate with upward-only correction and runtime overhead. No truncation or bound change was made. The four native `map_leaf` calls did complete before admission stopped the subsequent cut requests. There were **zero native search `propose_cuts` calls**; the one preflight call with that stage name is a schema test.

The four trace sidecars are incomplete and unsealed. The report explicitly refuses to interpret their content as authenticated search trees. Four chained `NOT_IN_COMMITMENTS` engine decisions and four job-failure receipts survive; they do not establish completed search, exhausted alternatives or absence of conflicts. Both paired analyses failed. There are no published route categories to infer from these failed jobs.

The saved `needs-native-recovery.json` recommends inspecting resume applicability; it is not an authorization or proof that repeating the same oversized request can succeed. Continuing requires a separately reviewed resolution of request size/configuration compatibility. This pass preserves the exact configured bounds and does not retry deterministic refusals.

## Target gates and summaries

Three proposal attempts each returned 1 candidate against a requested pool of 30. Two were retained against a keep limit of 10; the third was rejected after the allowed corrections. All three vocabulary checks were `disconnected`, an advisory result for fresh thesis atoms. For each candidate, all 340 target/negation single-support and tautology checks returned `SOLVER_COUNTEREXAMPLE`. Whole-T closure and essential-new-atom checks also passed candidate admission, with 1 essential fresh atom each. These are formal admission results, not proof of philosophical originality or a usable inference.

| Candidate | Own-thesis classifier | Fidelity | Semantic novelty classifier | Deterministic novelty | Final gate |
|---|---|---|---|---|---|
| target1 | own_thesis | matches | new_assertion | candidate, essential_new_assertion; no single support | KEPT |
| target2 | own_thesis | matches | new_assertion | candidate, essential_new_assertion; no single support | KEPT |
| candidate1 (attempt 3) | own_thesis | matches | restatement | candidate, essential_new_assertion; no single support | REJECTED: target_content_not_established |

**target1:** “A semantics of knowledge involving epistemic modals should represent worldly information and context of assessment as independent parameters: worldly information bears on whether the belief is safe, while assessment sensitivity is orthogonal to the choice of truth parameters.” The model classifier accepted this as a new recommendation combining frozen claims. Independence and a substantive inference to that recommendation were not demonstrated because search stopped.

**target2:** “A theory of epistemic modals should distinguish the conditions under which a modal belief qualifies as knowledge from the constraints governing whether modal sentences are assertible; these are separate evaluative standards, not one condition.” The classifier accepted the separation recommendation as a new assertion, rather than a restatement of the source claims. No licensed cross-paper derivation was produced.

**candidate1, rejected:** “Epistemic-modal semantics should represent information states as able to accept, reject, or remain neutral about sentences, and should restrict nonclassical inference to reasoning that crosses epistemic levels.” The classifier judged this a repackaging of two frozen commitments despite its fresh atom and own-voice recommendation. This illustrates why atomic formal novelty alone is insufficient. The two lexical `states` matches were advisory; there were zero lexical-only exclusions and zero exact leading report-frame rejections.

These are target descriptions and review notes, not model-written route summaries. The brief's requested substantive review of each CLOSED-derived route has zero applicable graphs.

## Catalogue bridge evidence

All three exact native target prompts match the prepared bridge candidates and commitment-to-paper map. The truncated bridge set has 60 entries (30 pairs, 30 triples), spanning 21 commitments from 7 of the 22 frozen papers. All 60 include Beddor–Goldstein 2021 and the definition term `about`; 0 connect shared catalogue symbols. This concentrates supplied guidance around a generic term and one paper, limiting the diversity of the bridge pool. It does not prove that the concentration caused the failed searches or underfilled target pool.

There are 0 `proposal_bridge` receipts: no cut proposal was dispatched. Cross-paper bank-scheme guidance was therefore supplied but not exercised through a live cut proposal in this pilot.

## Route categories and summaries

| Category | Count | Summary |
|---|---:|---|
| CLOSED-derived | 0 | No published route; substantive scheme and cross-paper support untested. |
| CLOSED-structural | 0 | No published route. |
| CLOSED-single-paper | 0 | No published route; r22's new classification was not exercised by a closed route. |
| OPEN | 0 | Failed search jobs are not published OPEN routes. |
| Other route classifications | 0 | No published routes in any category. |

Model-written route summaries: 0, because there are 0 routes. No summary-generation call was made during recovery.

## Usage and human actions

| Scope | Calls | Input tokens | Output tokens | Total tokens | New API USD |
|---|---:|---:|---:|---:|---:|
| Fresh schema preflight + standalone canary | 19 | 86,306 | 5,536 | 91,842 | 0 |
| Native fork | 11 | 766,678 | 5,616 | 772,294 | 0 |
| Total new work | 30 | 852,984 | 11,152 | 864,136 | 0 |

All new calls have actual accounting; unsettled calls 0, unknown usage 0, fallbacks 0, Claude/non-Codex calls 0. Subscription dollar equivalent is unavailable. Summed call wall time was 346.608 seconds; the native fork command elapsed 596.199 seconds. These measure different scopes and are not human labor time. Native HUMAN commands are schema preflight at 09:20:21 UTC, standalone canary at 09:22:10 UTC, and fork-from-freeze at 09:22:52 UTC on 2026-10-28. Each reports 0 operator minutes; no unmeasured labor estimate is supplied.

The partial run checkpoint includes 16,204,728 imported tokens and $110.395145 inherited accounting. Those figures are historical lineage, not new API spend. The combined report also includes prior Claude/API activity; the zero-call/zero-spend claim above is scoped to fork pilot 4 and its fresh preflights.

## Report verification

`ara report` completed successfully in 1,173.694 seconds over 61 input runs. Delivered native HTML is **1,315,421 bytes (1.315421 decimal MB)**. The independent copy contains **45,710 native report files / 4,751,528,429 bytes**, including `report.html`, `report.md`, `data.json`, all per-run sections, events, artifacts and tree sidecars. Every file matched its source SHA-256 before generated staging files were reclaimed to stay within available disk space. Only this newly generated staging output was reclaimed; native inputs, delivered reports and prior handoffs were retained.

The audit reconstructed **147,307 event occurrences from 41,622 unique bodies**, verified **1,637 artifact copies**, and checked **4,386 HTML links** with **0 broken links / 0 missing anchors**. All 61 input logs and anchors stayed unchanged. The full-lineage accounting remains $131.785270 measured plus $1.844820 unknown/reserved = $133.630090 budget-accounted; these historical totals are not new pilot spend.

Chromium 143.0.7499.4 opened the delivered local HTML. Desktop width/scroll width are both 1,440 px; page errors 0, missing anchors 0. The strict browser layout test is **FAIL solely for mobile overflow**: viewport 390 px, document 409 px (19 px overflow). Rendering and literal summary coverage pass criterion 4, but a fully responsive layout is not claimed. The native HTML was preserved unchanged. Expanded current-run search panels visibly show all four results as `partial`, with unsealed-sidecar warnings and no authenticated proof tree.

The native event index still treats **10,349 copied freeze-prefix occurrences** as `original_in` instead of `imported_by`. `import-origin-overlay.json` supplies the correction without rewriting the native report. Deduplicated accounting is unaffected; use the overlay when attributing event origin.

Evidence copied beside the report includes `fork-audit.json`, `context-refusals.json`, `target-gate-review.json`, `bridge-review.json`, `success-criteria-assessment.json`, `report-audit.json`, `copy-verification.json`, browser receipts/screenshots and the import-origin overlay. These reporting receipts are external control evidence, not fabricated native MODEL or HUMAN events.


## Findings placement

1. R22 review remains provisional — **Opening status**.
2. Four deterministic context refusals prevent native completion — **Context blocker and search state**.
3. Four incomplete unsealed traces and failed paired analyses do not establish search exhaustion or conflict absence — **Context blocker and search state**.
4. Target proposal pool underfilled: one candidate per attempt, two retained — **Target gates and summaries**.
5. Formal fresh-atom novelty admitted a semantic restatement that the classifier rejected — **Target gates and summaries**.
6. Bridge guidance concentrates on a generic term and one paper — **Catalogue bridge evidence**.
7. Zero routes; CLOSED-derived and cross-paper closure unexercised — **Route categories and summaries**.
8. Serving identity unverified despite requested model pin — **Execution, configuration and preservation**.
9. Historical API/Claude usage must be distinguished from zero new pilot4 usage — **Usage and human actions**.
10. Zero-route summary coverage cannot establish summary quality — **Acceptable pilot — criteria 1–4**.
11. Native report index mislabels 10,349 copied freeze-prefix occurrences; deduplicated accounting is unaffected — **Report verification**.
12. Mobile layout check fails with 19 px horizontal overflow despite successful rendering — **Report verification**.

**12 findings, 12 placed.**

## Continuation boundary

No further model calls, native resumes, route selections or configuration changes were made during recovery. The remaining operational blocker is the oversized cut-proposal request under the required configuration. A subsequent task must resolve that incompatibility before retrying. The successful-entry essay, audits and submission remain unattempted.

DONE zeta fork4 targets=2 derived_closed=0 structural_closed=0 open=0 criteria=F,P,F,P status=blocked:propose_cuts-context-bound report=/home/dev/ara-work/reports/overnight/fork4/report.html
