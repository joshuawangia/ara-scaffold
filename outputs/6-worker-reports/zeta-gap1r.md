# Gap pilot 1 recovery — frozen, then stopped at target admission

**Provisional**, as requested in the recovery brief. Code: clean detached `4cefe35f4a037725c1d5a97a1e401be46fe8fc83`. Run: `/home/dev/ara-scaffold/runs/codex-gap-1r`. [Native report](/home/dev/ara-work/reports/overnight/gap1r/report.html) · [data manifest](/home/dev/ara-work/reports/overnight/gap1r/data.json) · [freeze summary](/home/dev/ara-work/reports/overnight/gap1r/freeze-summary.json) · [integrity](/home/dev/ara-work/reports/overnight/gap1r/final-integrity.json).

The recovery restored completed construction, resolved all 150 alignment pairs, froze T once, loaded the six external gaps, and completed bounded gap/forward discovery. It then **stopped before the first target model call** because the full L3 target request exceeded the configured context bound. Native exit code: 2. No targets, search routes, or selection were produced. L3 is not resolved. This is not an acceptable pilot.

## Target admission blocker

The first request addressed `external:eps2-L3`. Its calibrated native count was **311,785 initial-input tokens plus 16,384 output allowance**, versus a **200,000-token context bound**: 328,169 total, exceeding the bound by 128,169. These are admission estimates, not measured tokens from a dispatched request. Runtime refused with `propose_targets context bound exceeded by counted request; no truncation`; no target `call_start` occurred. The larger reservation figure is not actual usage and was not spent.

The actual rendered prompt is 627,750 UTF-8 bytes. The largest compact-JSON fields are commitment provenance (332,316 bytes), commitments (87,242), symbol catalogue (56,689), alignment disclosure (54,845), and bank (27,596). The external L3 record is 5,524 bytes; the two forward leads are 2,301. The pre-freeze readiness request had counted only **51,998 input tokens** and passed. It did not establish admission of the later fully assembled target request. [Admission comparison](/home/dev/ara-work/reports/overnight/gap1r/target-admission-comparison.json) and [field-size breakdown](/home/dev/ara-work/reports/overnight/gap1r/target-admission-breakdown.json) make this mismatch reviewable. The native linked event retains the full refused prompt.

No cap was raised, evidence silently dropped, prompt manually truncated, or source code changed. Continuing target/search work needs a supported change to target-context construction/admission on an appropriate reader; the saved freeze is the recovery asset. This turn did not start a new fork.

## Recovery and frozen T

The free native resume plan verified all **74 terminal construction windows**, **159 working commitments**, and **35 accepted legacy judgments**; it identified **115 pending pairs**, without creating a provider or counter. The fresh schema preflight passed **18/18 cases**, plus its two isolation canaries. The live recovery passed two further canaries and made no construction/root-selection replay calls. [Verified plan](/home/dev/ara-work/reports/overnight/gap1r/alignment-resume-plan.json).

All **150/150** candidate pairs now have accepted judgments; **0 unresolved**, against an absolute limit of 5. The 115 new judgments are all unrelated. Final relation counts: **149 unrelated, 1 entails_right_left, 0 same_content, 0 entails_left_right, 0 contrary**. The transaction applied **one model-alignment bridge**, made **zero canonical rewrites**, and recorded **zero consistency refusals**.

The frozen set contains **160 commitments: 159 source commitments from 22/26 papers plus 1 explicitly labelled model_alignment bridge**. Source stances: 134 endorsed, 10 reported, 15 attacked. All 159 source entries have page citations and stance metadata. The bridge has source-linked citation text but is not a paper's endorsement and is not counted as an extra source paper.

Freeze identifier:
`7418a5cd6975379634e68a7c7d900e78c8da91f2d7644d0fdd2b68ca0e2ee5ed`

Provenance identifier:
`2db36f17cf76ddee53a6318879ebfa14395d9ce13c04eb8f833ec5c330e924aa`

[Artifact hashes and independent solver checks](/home/dev/ara-work/reports/overnight/gap1r/freeze-audit.json) identify the exact files to preserve for any later fork.

The original construction limitations remain: 53 accepted windows, 21 skipped; 16 skipped closures exceeded a bound, one selected no topical roots, and four failed formalization (ordinary “holds/hold” and “states” falsely treated as attribution in two windows; provenance/correction failure and formula-schema/correction failure in two more). Recovery did not rebuild or repair these omissions. [Window outcomes](/home/dev/ara-work/reports/overnight/gap1r/window-outcomes.json), [source inventory](/home/dev/ara-work/reports/overnight/gap1r/prealignment-accepted-inventory.json).

### The retained entailment remains disputed

The sole bridge runs from Schaffer's description of truth perspectivalism to MacFarlane's assessment-sensitivity framework. Schaffer's source row is **attacked**, not endorsed. Schaffer PDF3 distinguishes his defended meaning perspectivalism from that rival; MacFarlane PDF66 explicitly says nonstandard truth parameters alone are insufficient for relativism. The model's identification of perspective-dependent evaluation with the full assessment-sensitivity claim is disputable and supplies no safety–retraction rule. Recovery preserved the accepted receipt; it did not establish its semantic adequacy. [Exact legacy judgment](/home/dev/ara-work/reports/overnight/gap1r/entailment-judgment-source-review.json); direct page checks are in `source-pages/`.

### R28-F2

**R28-F2 did not bite here.** Independent Z3 checks on the actual freeze returned SAT for all 160 commitments, the admissible 135-member endorsed/alignment union, and the 134 endorsed source commitments. Each check had a 5,000 ms bound. Thus the inconsistent-union condition that suppresses valid synthesis is absent. This is a formal result about these frozen formulas, not a guarantee of faithful source formalization.

## Gaps and L3

Six external hypotheses passed native frozen-source binding: L3 first, then qualified conflicts 14, 17, 20, 49, and 58. The loader was invoked once for explicit validation and once by native discovery; this is **six inputs, not twelve distinct gaps**. Four other partial comparisons (30, 34, 42, 46) remain unbound because no Willer2013 commitment survived. Pair46 overlaps42. Item35 was unknown rather than partial/still_open and was excluded under the original brief. [Binding plan](/home/dev/ara-work/reports/overnight/gap1r/gap-binding-plan.json), [exact external file](/home/dev/ara-work/reports/overnight/gap1r/external-gaps.json).

L3's supplied verdict remains **“partially anticipated by Beddor–Goldstein and Dinges 2021; no read source derives the link.”** This is a bounded reading verdict, not exhaustive novelty certification. Beddor–Goldstein already discusses assessor rejection and cites MacFarlane; Dinges offers a rival asymmetric-loss explanation of changes in estimates, including safety/reliability, without requiring relativism. Missing citation-index links are not absence evidence.

The desired link is from safety relative to worldly information to an obligation to retract with use context fixed and assessment context changed. Safety, permission to reject, and retraction obligation are different claims. The bound anchors are Beddor–Goldstein's safety/worldly-information commitments and MacFarlane n35. Original `ic_derive_safety`, MacFarlane n30, and q6 are absent; n35 is not the full retraction rule. These limits are explicit in the external input. The alignment inventory contains only one Beddor–Goldstein/MacFarlane2014 pair (rank45), comparing safety to n10's assertion norm; it was judged unrelated and is not a direct safety/retraction equivalence. [Alignment coverage](/home/dev/ara-work/reports/overnight/gap1r/l3-alignment-coverage.json), [earlier source review](/home/dev/ara-work/reports/overnight/gap1r/source-review-notes.md).

**L3 resolution theses: 0; L3 routes: 0; L3 CLOSED-derived resolutions: 0. L3_resolved=no.** The blocked request was L3's first target proposal. No output can be evaluated as a partial derivation merely because the prompt contained the intended question.

### Native gap review

All 60 ranked semantic pairs were classified: 35 compatible, 22 unrelated, 3 in tension, 0 contradicts, 0 unclassified failures. Together with three deterministic open_problem records and six external records, native discovery produced **12 gap hypotheses**. None is a formal contradiction witness. [Complete inventory](/home/dev/ara-work/reports/overnight/gap1r/detected-gaps.json), [classifications](/home/dev/ara-work/reports/overnight/gap1r/semantic-classifications.json).

Direct source checks found material limits:

- Egan–Weatherson PDF12 describes a historically open question in 2011; it does not certify currency in 2026.
- The two Moss open_problem records are successive steps of the same nested-modality argument on PDF11–12. A local challenge motivating the paper's alternative theory is not two independent current-open problems.
- The H&M/Yalcin tension contains a stance error: H&M PDF1 endorses the criticism that certain theories underpredict embedded contradictions. The classifier instead says H&M attacks that criticism. The frozen item mixes a criticized theory with the authors' assessment under one attacked label. Yalcin PDF11–12 also criticizes relational predictions; the stated opposition is not established by these passages.
- Moss PDF74–75 proves conditional modus tollens quasi-valid under positive-probability conditions; Yalcin PDF16 discusses universal Modus Tollens with quantifiers across epistemic modals. Different forms and consequence notions need comparison, not conflation.
- K&R PDF35 concerns information-parameter shifting/quantificational domains; Moss PDF11–12 concerns the type of sentential content for nested probability constructions. Those are distinct semantic questions, so the passages do not establish a contradiction.

These are reviewer findings; native labels and frozen stances remain unchanged. [Detailed review](/home/dev/ara-work/reports/overnight/gap1r/native-gap-source-review.md) and the saved physical-PDF page text support each qualification.

## Forward candidates: both are padding

The depth-2, node-cap-500 forward pass produced **500 licensed consequences** and reported **truncated=true**. Its 1,002 engine decisions include 500 conjunction-introduction licenses and 500 corresponding derived consequences; the bounded pass is not an exhaustive synthesis search. It ran from roughly 17:01 to 18:50 UTC. No provider calls occurred during that deterministic stage.

It emitted two ranked leads:

| Candidate | Actual supports | Substantive verdict |
|---|---|---|
| `forward:29e9b88b67e20d7888c6d8129c08a74f6faaddc75aeef4e3ba32cf36756ab2ac` | Beddor–Goldstein safety + Bledin q_cd_persistent | **Padding / Boolean repackaging, not a contribution.** |
| `forward:2cd7d2ddbe703e5dcdff84b12b7208f4741d45ad250313371ff1e0d9aae1740f` | Beddor–Goldstein worldly information + the same Bledin qualification | **Padding / Boolean repackaging, not a contribution.** |

Both use conjunction introduction alone. Independent Z3 checks **with no premises** prove each equivalent to the conjunction of its own two already frozen supports. Neither introduces a new atomic application. Normalizing/reordering/flattening the conjunction is not a new assertion. Both still return `candidate / per_paper_new_assertion` from this head's native novelty helper. [Forward receipts](/home/dev/ara-work/reports/overnight/gap1r/forward-target-candidates.json), [padding proofs](/home/dev/ara-work/reports/overnight/gap1r/forward-padding-review.json), [native novelty rechecks](/home/dev/ara-work/reports/overnight/gap1r/forward-novelty-recheck.json).

This is an observed forward-candidate false positive in the padding family. **It is not an executed target-admission or selectable-route reproduction:** the target call was refused before dispatch. Neither lead uses MacFarlane or a retraction premise, so neither addresses L3.

Bledin's source adds a second limit. PDF26 footnote52 starts a warning against unrestricted constructive dilemma; its office-example continuation is on **PDF27**, beyond the frozen citation's PDF26-only span. The frozen formula conjoins a badness assertion with the problematic implication as positive content. That warning should not be used as an endorsement that the implication is a sound inference. Both physical pages are saved; no citation/formula was silently repaired.

## Target and route review

Proposed model targets: **0**. Retained targets: **0**. All routes: **0**. CLOSED-derived routes: **0**. Thus every-target and every-CLOSED-derived padding reviews have empty populations (0/0); they do not clear INTEG-F1/R28-F1. The two actual forward leads were individually reviewed and excluded as contributions above. Substantive contribution count: **0**.

The operational collector preserved from the original pilot would retain all distinct native-gated passing candidates, including cap-only overflow, in gap/forward/general order. Target collection never completed, so it neither admitted nor discarded a target here. There was no search, route selection, essay, or audit stage. Model-written route summaries: **0/0**, because there are no routes; no summary calls were made.

## Approved acceptable-pilot criteria

| Criterion | Verdict | Numbers and limits |
|---|---|---|
| 1. Clean run | **FAIL** | Native context STOP/exit 2; `awaiting_selection` absent. Complete new receipts: 177 main-run call starts, responses, and MODEL receipts, plus 20 preflight calls. 0 Claude-subscription calls and $0 new API spend. |
| 2. Coverage | **PASS, with source-quality limits** | Frozen source T covers **22/26 papers**, above 20. **159/159** source commitments carry page citations and endorsed/reported/attacked labels. The additional bridge is separately model_alignment. This metadata pass does not certify source fidelity or the completeness of every cited span; the Bledin problem is disclosed. |
| 3. Real routes | **FAIL** | **0/3** required CLOSED-derived routes; **0** substantive contributions. Both forward leads are padding, and neither is a route. |
| 4. Readable output | **PASS, empty route population** | Delivered HTML opens in Chromium at desktop/mobile widths, with 0 page errors and 0 overflow. Summary coverage is **0/0**, not evidence of prose quality on a generated route. |

Overall: **FAIL / PASS / FAIL / PASS**, not an acceptable pilot. Successful-entry essay/submission criteria were not attempted.

## Review status and future fork compatibility

The run remains provisional under the brief. Kappa4's subsequently available Sigma12 review found no production resume bypass on this exact head and passed 233 scoped tests plus 44 scoped controls. It nevertheless reported an integration blocker: Xi r29's fake alignment response still includes old-schema IDs; the combined tree had 52/53 passing tests, with three additive merge conflicts. This is not an unconditional integrated-head approval. [Preserved review](/home/dev/ara-work/reports/overnight/gap1r/kappa4-sigma12-review-snapshot.md).

The freeze uses **alignment policy v3**. Static inspection of bare Xi r29 `ddda14f` shows its reader accepts only v1/v2; therefore a later fork requires the Sigma-integrated/v3-capable reader as well as the intended target-policy fixes. No bare-r29 fork was attempted, and this handoff does not claim it would load successfully. Retain the freeze ID and all three frozen artifacts plus their chained receipts.

## Accounting and integrity

This recovery added **197 Codex calls**: 20 fresh preflight calls (18 schema cases +2 canaries), then 177 main-run calls (2 canaries +115 alignment +60 semantic classifications). New measured token fields: **724,135 input +36,474 output +279,680 cache-read =1,040,289**; cache writes/server tools:0. All 197 receipts are actual, all providers codex_cli, requested model gpt-6-luna/high; serving identity is unverified in every receipt. New API spend:$0; subscription dollar equivalent is unavailable, not measured zero. [Accounting](/home/dev/ara-work/reports/overnight/gap1r/final-local-accounting.json).

Including the failed attempt's 242 calls and its preflights, the gap experiment has **439 Codex calls and 6,312,289 measured token-field units**. The native report also retains older extraction history: $109.497235 measured API cost +$0.897910 unknown actual charged at reservation =$110.395145 budget-accounted. That inherited API history is not new recovery spend. Native report combined receipt count 716 includes 439 Codex plus 277 historical extraction receipts; it is not a count of new calls. Other independent pilots are not inputs to this report.

All **246 original failed-run files** still match their pre-copy SHA-256 values. The original **344,106,370-byte event prefix** is byte-for-byte unchanged in the recovered log; the full recovered hash chain/tail verifies across 9,344 events. Code remains clean at 4cefe35. Cache/gap-file locations were explicitly relocated into recovery-owned paths and logged, to avoid writing to the original. No source rewrite or manual freeze occurred. [Integrity receipt](/home/dev/ara-work/reports/overnight/gap1r/final-integrity.json).

During low disk space, only the previous gap1 duplicate staging report was removed, after all 7,850 files matched the preserved delivered report. The failed source run and delivered gap1 report were untouched. [Reclamation receipt](/home/dev/ara-work/reports/overnight/gap1r/duplicate-report-reclamation.json).

## Report verification

The native offline report includes the recovered run, its fresh schema preflight, its free resume plan, and the original gap schema/canary runs; imported extraction lineage remains visible. Copied **10,134 native files /404,095,697 bytes**, including report.html, report.md, data.json and every linked sidecar, with SHA-256 equality. Companion reviews are separate from the native report output.

HTML size: **390,993 bytes /0.390993 decimal MB**. Chromium opened the delivered file at 1440×1000 and 390×844; both had 0 overflow pixels and 0 page errors. Checked1,116 native HTML links with 0 missing local files. [Browser receipt](/home/dev/ara-work/reports/overnight/gap1r/browser-check.json), [copy manifest](/home/dev/ara-work/reports/overnight/gap1r/copy-verification.json), [verification](/home/dev/ara-work/reports/overnight/gap1r/verification.json).

## Findings placement

- F1: Full target request refused after smaller readiness check passed — Target admission blocker.
- F2: Recovered alignments include a substantively disputed legacy bridge — Recovery and frozen T; The retained entailment remains disputed.
- F3: Coverage metadata passes but inherited construction omissions remain — Recovery and frozen T.
- F4: R28-F2 inconsistent-union condition is absent in the actual freeze — R28-F2.
- F5: L3 partial anticipation, absent rule anchors, and zero resolution — Gaps and L3.
- F6: Only six external gaps bind; four Willer comparisons remain excluded — Gaps and L3.
- F7: Historical/duplicated open-problem signals do not certify current gaps — Native gap review.
- F8: H&M/Yalcin conflict rationale reverses source criticism/stance — Native gap review.
- F9: Other semantic tensions compare different forms or representational levels — Native gap review.
- F10: Bounded forward pass is truncated and not exhaustive — Forward candidates: both are padding.
- F11: Both forward leads are Boolean repackaging despite native novelty acceptance — Forward candidates: both are padding.
- F12: Bledin counterexample-warning formalization and citation-span limitations — Forward candidates: both are padding.
- F13: Empty target/route inventories; collector unexercised and no selection — Target and route review.
- F14: Criteria fail overall; rendering pass has empty summary coverage — Approved acceptable-pilot criteria.
- F15: Provisional integration status and v3 incompatibility with bare Xi r29 — Review status and future fork compatibility.
- F16: New versus inherited usage, unverified serving identity and unavailable subscription USD — Accounting and integrity.
- F17: Original preservation, copied-prefix integrity and disclosed operational relocations — Accounting and integrity.
- F18: Native report copied, links checked and browser-opened — Report verification.

18 findings, 18 placed.
