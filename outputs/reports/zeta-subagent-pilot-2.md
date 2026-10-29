# Zeta subagent pilot 2

**blocked:token-cap.** Frozen T contains **95 commitments from 15/26 papers**; 10 targets, **8/20 completed polarity searches**, and **15 published routes**. No route was selected. Native pilot exit: 2. New API spend is zero.

The next search request exceeded the remaining token reservation at the 30,000,000 local-token cap. Four active jobs stopped with `BudgetStop`, eight jobs were canceled before starting, and all ten paired analyses are unavailable. All 15 retained routes are **OPEN**, not completed proofs. Requested model-written route summaries are blocked by the terminal run stop; no summary calls were made. The native run did not reach `awaiting_selection`.

[Open the full-lineage report](/home/dev/ara-work/reports/overnight/final2/report.html). [Structured audit](/home/dev/ara-scaffold/runs/subagent-pilot-2-control/pilot-audit.json). The previous handoff is preserved byte-for-byte as [zeta-subagent-pilot-1.md](/home/dev/ara-work/reports/zeta-subagent-pilot-1.md). The prior pilot, final report, interim report and part-7 backup remain preserved.

## Revision, configuration and review boundary

Ran requested main `f9c5a8fe24cfb73cf5dc47a9d2743a503f9c9179` from a clean tree, with fresh run/cache directories and an empty audience. All construction, target, search and writing stages resolve to `claude_code` / `claude-opus-5-5`, no fallback. Window cap multiplier is 2; search and provider concurrency are both 4. The native standalone canary ran first and passed; native startup canaries remain in the linked receipts. No API fallback, extraction rerun, credential change, tracked source edit, commit or push was performed.

Read kappa2’s review and re-review, Omega Rounds 6–8, and Xi Round 8 plus its final integration. Kappa2’s zero-blocker verdict and 854-passed/2-skipped suite apply to scratch merge `469c278`, not automatically to the requested merge resolution. Xi separately verified exact head `f9c5a8f`: 854 passed, 2 skipped, then 395 mutations failed as intended and all 395 restorations passed. The recorded source hashes were checked against this checkout before launch. These are prior review/integration results, not suites rerun by this execution.

The literature is unchanged: `/home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt`, SHA-256 `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`. No old construction batches were restored. Historical extraction provenance was imported normally.

## Corrected calibration, budgets and retries

Omega corrected the prior aggregate-input/initial-context comparison. The retained baseline factor is 0.553224 with separate fixed overhead of 949 tokens; like-for-like observations may raise estimates. The offline 70/70-window fit is an admission counterfactual, not a promise of 70 accepted contributions. The previous pilot’s 58 skips comprised 42 context refusals and 16 other closure/selection skips. Its historical receipts and handoff were not rewritten.

The first live formalization recorded 30,171 aggregate input tokens against 89,856 reserved input tokens, using `aggregate_input_vs_aggregate_reservation`. Its initial-context estimate was 12,928; the factor changed from 0.553224 to 0.553224. All local observations remain in the structured audit.

The unchanged 30,000,000-token cap now applies to local subscription usage, including reservations and unknown usage. Imported tokens remain visible in accounting but do not consume this subscription cap. API admission remains history-inclusive. Other retained limits include 70,000 batch-input tokens, 100,000 working-T tokens, 48,000 catalogue tokens, 233 symbol-growth tokens per item, and 200,000 model-context tokens.

Live catalogue growth became a limiting factor. Before window 38, the native catalogue was 45,519/48,000 tokens, leaving 2,481. That window's first output exceeded the shared symbol allowance; its targeted correction repeated an unchanged item, so the window was skipped. Window 39 subsequently contributed within the remaining allowance. Before window 53, catalogue usage was 47,538/48,000, with 462 tokens left across 17 windows; the native allocation assigned that window zero commitments and zero symbol tokens. At the start of the last attempted window (69), catalogue usage was 47,897, remaining symbol allowance 103, and working-T input 58,194. These are observed runtime capacities, separate from the initial 70-window fit counterfactual. All per-window budget receipts are retained in the structured audit.

Native transport allows one retry for an unclassified exit 1 within configured retry limits. Exhausted job-local failures do not cancel sibling searches; each failed job may receive one final attempt after the initial queue drains. Global budget/context and infrastructure stops remain authoritative. Only allowlisted categories/subtypes and numeric diagnostic metadata survive; unavailable free-text diagnostics are not inferred. A retry policy is not a diagnosis of an error’s cause.

| Local tokens | Imported historical tokens | Combined recorded tokens | Local cap |
|---|---|---|---|
| 29662860 | 11348025 | 41010885 | 30000000 |

Observed retry: `propose_cuts` reported `cli_max_turns` (exit 1, three turns), then retried after one second. No unclassified-exit retry or search-job requeue occurred. Critical-question outputs referencing unknown T IDs were rejected. These validation refusals are distinct from the terminal global token stop.

## Frozen T and paper coverage

Freeze count: 1. Freeze path: `/home/dev/ara-scaffold/runs/subagent-pilot-2/commitments.json`. SHA-256: `64460f4ea1ff389545c3cbf91af45be9b9d5b8e80bdeca04a0f47e79fcea1afc`. Accepted batch IDs were checked against the native commitment inventory. Paper/kind linkage uses recorded evidence IDs and citations; these checks do not establish faithful formalization or the truth of commitments.

| Paper ID | Commitments in T |
|---|---|
| vonfintelgillies2007 | 0 |
| eganweatherson2011 | 8 |
| vonfintelgillies2011 | 0 |
| wright2007 | 0 |
| schaffer2011 | 0 |
| braun2012 | 1 |
| eganhawthorneweatherson2005 | 3 |
| egan2007 | 5 |
| macfarlane2011 | 8 |
| yalcin2007 | 0 |
| yalcin2011 | 0 |
| rothschild2012 | 0 |
| moss2015 | 1 |
| hawkesteinertthrelkeld2021 | 5 |
| veltman1996 | 0 |
| gsv1996 | 2 |
| willer2013 | 1 |
| ninan2018 | 0 |
| beddorgoldstein2021 | 4 |
| hollidaymandelkern2024 | 10 |
| kolodnymacfarlane2010 | 0 |
| knobeyalcin2014 | 8 |
| klinedinstrothschild2012 | 3 |
| bledin2014 | 2 |
| yalcin2015 | 0 |
| macfarlane2014 | 34 |

| Kind | Count |
|---|---|
| attacked_view | 4 |
| conclusion | 23 |
| intermediate_conclusion | 23 |
| distinction | 14 |
| reported_view | 6 |
| qualification | 10 |
| inference | 7 |
| premise | 8 |

## Every construction window and skip

70 planned windows; 32 contributed. Window indices are zero-based. Retained closure items in a skipped window did not enter T. Full per-item omissions and relevance explanations remain in the linked native construction data.

| Window | Papers | Roots | Uncut | Retained | Accepted commitments | Outcome / reason |
|---|---|---|---|---|---|---|
| 0 | beddorgoldstein2021 | 4 | 4 | 4 | 4 | accepted |
| 1 | beddorgoldstein2021, bledin2014 | 2 | 64 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 2 | bledin2014, braun2012 | 2 | 29 | 3 | 3 | accepted |
| 3 | braun2012 | 1 | 12 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 4 | braun2012, egan2007 | 2 | 4 | 4 | 4 | accepted |
| 5 | egan2007 | 2 | 10 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 6 | egan2007, eganhawthorneweatherson2005 | 2 | 117 | 3 | 3 | accepted |
| 7 | eganhawthorneweatherson2005 | 1 | 27 | 1 | 1 | accepted |
| 8 | eganhawthorneweatherson2005, eganweatherson2011 | 2 | 89 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 9 | eganweatherson2011 | 4 | 4 | 4 | 4 | accepted |
| 10 | eganweatherson2011, gsv1996 | 1 | 4 | 4 | 4 | accepted |
| 11 | gsv1996 | 2 | 10 | 2 | 2 | accepted |
| 12 | gsv1996 | 2 | 9 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 13 | gsv1996, hawkesteinertthrelkeld2021 | 1 | 11 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 14 | hawkesteinertthrelkeld2021 | 1 | 48 | 4 | 4 | accepted |
| 15 | hawkesteinertthrelkeld2021, hollidaymandelkern2024 | 2 | 4 | 4 | 4 | accepted |
| 16 | hollidaymandelkern2024 | 4 | 4 | 4 | 4 | accepted |
| 17 | hollidaymandelkern2024 | 1 | 13 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 18 | hollidaymandelkern2024 | 2 | 9 | 2 | 2 | accepted |
| 19 | hollidaymandelkern2024 | 3 | 12 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 20 | hollidaymandelkern2024, klinedinstrothschild2012 | 2 | 16 | 2 | 2 | accepted |
| 21 | klinedinstrothschild2012 | 2 | 18 | 2 | 2 | accepted |
| 22 | klinedinstrothschild2012, knobeyalcin2014 | 2 | 4 | 4 | 4 | accepted |
| 23 | knobeyalcin2014, kolodnymacfarlane2010 | 1 | 41 | 4 | 4 | accepted |
| 24 | kolodnymacfarlane2010, macfarlane2011 | 1 | 16 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 25 | macfarlane2011 | 2 | 41 | 4 | 4 | accepted |
| 26 | macfarlane2011, macfarlane2014 | 2 | 4 | 4 | 4 | accepted |
| 27 | macfarlane2014 | 4 | 4 | 4 | 4 | accepted |
| 28 | macfarlane2014 | 2 | 3 | 3 | 3 | accepted |
| 29 | macfarlane2014 | 1 | 6 | 1 | 1 | accepted |
| 30 | macfarlane2014 | 2 | 4 | 4 | 4 | accepted |
| 31 | macfarlane2014 | 1 | 9 | 2 | 2 | accepted |
| 32 | macfarlane2014 | 3 | 4 | 4 | 4 | accepted |
| 33 | macfarlane2014 | 3 | 3 | 3 | 3 | accepted |
| 34 | macfarlane2014 | 1 | 5 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 35 | macfarlane2014 | 1 | 4 | 4 | 4 | accepted |
| 36 | macfarlane2014 | 2 | 2 | 2 | 2 | accepted |
| 37 | macfarlane2014 | 1 | 11 | 4 | 4 | accepted |
| 38 | macfarlane2014 | 4 | 4 | 4 | 0 | construction correction repeats unchanged item |
| 39 | macfarlane2014 | 2 | 11 | 2 | 2 | accepted |
| 40 | macfarlane2014 | 1 | 5 | 1 | 1 | accepted |
| 41 | macfarlane2014 | 2 | 6 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 42 | macfarlane2014, moss2015 | 4 | 4 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 43 | moss2015 | 1 | 48 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 44 | moss2015 | 1 | 4 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 45 | moss2015 | 1 | 8 | 1 | 1 | accepted |
| 46 | moss2015 | 2 | 19 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 47 | moss2015, ninan2018 | 2 | 14 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 48 | ninan2018 | 1 | 26 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 49 | ninan2018, rothschild2012 | 2 | 47 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 50 | rothschild2012, schaffer2011 | 2 | 24 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 51 | schaffer2011 | 2 | 9 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 52 | schaffer2011 | 2 | 11 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 53 | schaffer2011, veltman1996 | 2 | 9 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 54 | veltman1996 | 1 | 5 | 1 | 0 | shared symbol token allowance exceeded |
| 55 | veltman1996, vonfintelgillies2007 | 4 | 4 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 56 | vonfintelgillies2007 | 4 | 4 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 57 | vonfintelgillies2007 | 2 | 16 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 58 | vonfintelgillies2011 | 2 | 35 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 59 | vonfintelgillies2011 | 2 | 37 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 60 | vonfintelgillies2011 | 1 | 36 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 61 | vonfintelgillies2011, willer2013 | 2 | 4 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 62 | willer2013 | 1 | 7 | 1 | 1 | accepted |
| 63 | willer2013, wright2007 | 2 | 11 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 64 | wright2007, yalcin2007 | 4 | 4 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 65 | yalcin2007 | 2 | 32 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 66 | yalcin2007, yalcin2011 | 3 | 4 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 67 | yalcin2011, yalcin2015 | 2 | 4 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 68 | yalcin2015 | 1 | 7 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 69 | yalcin2015 | 3 | 4 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |

## Omitted-support cuts

26 frozen commitments explicitly carry `support_omitted`. These are assumptions at a recorded frontier, not proofs of omitted support. Attempted cuts from skipped windows are retained below and were not accepted into T.

| Window | Accepted? | Cut depth | Commitment → omitted support IDs |
|---|---|---|---|
| 2 | True | 0 | bledin2014:r21-40:lesson6 → bledin2014:r21-40:inf4<br>braun2012:union:item:braun2012:salvage:47d76f588ef2072f:braun2012:r27-52:ic_advantage → braun2012:union:item:braun2012:salvage:47d76f588ef2072f:braun2012:r27-52:inf_advantage |
| 6 | True | 0 | egan2007:salvage:65b686e45c7b24fd:egan2007:r20-39:c_final → egan2007:salvage:65b686e45c7b24fd:egan2007:r20-39:inf_final<br>eganhawthorneweatherson2005:r1-24:n_concl_rel → eganhawthorneweatherson2005:joined:inf_g42_final, eganhawthorneweatherson2005:r1-24:n_inf_rel |
| 7 | True | 0 | eganhawthorneweatherson2005:joined:g29_ic_avoid_both → eganhawthorneweatherson2005:joined:inf_g29_avoid_both |
| 11 | True | 0 | gsv1996:r18-35:n_order → gsv1996:r18-35:inf1<br>gsv1996:r9-17-refine:c_discourse_not_single_state → gsv1996:r9-17-refine:inf_discourse |
| 14 | True | 1 | hawkesteinertthrelkeld2021:r10-19-refine:n_pragmatic_fails → hawkesteinertthrelkeld2021:r10-19-refine:inf_pragmatic_fails<br>hawkesteinertthrelkeld2021:r10-19-refine:n_summary_constraints → hawkesteinertthrelkeld2021:r10-19-refine:inf_summary |
| 18 | True | 0 | hollidaymandelkern2024:r36-52:c18 → hollidaymandelkern2024:r36-52:inf_c18<br>hollidaymandelkern2024:r36-52:c20 → hollidaymandelkern2024:r36-52:inf_c20 |
| 20 | True | 0 | hollidaymandelkern2024:r53-70:c_possibility_framework → hollidaymandelkern2024:r53-70:inf_possibility_framework<br>klinedinstrothschild2012:r1-12-refine:c_peculiar → klinedinstrothschild2012:r1-12-refine:i_peculiar |
| 21 | True | 0 | klinedinstrothschild2012:r1-12-refine:c_modaldyn → klinedinstrothschild2012:r1-12-refine:i_modaldyn<br>klinedinstrothschild2012:r26-37:p35_sum → klinedinstrothschild2012:r26-37:inf_p35_1 |
| 23 | True | 1 | knobeyalcin2014:r1-21:cc1 → knobeyalcin2014:r1-21:inf8 |
| 25 | True | 0 | macfarlane2011:r1-22:main_concl → macfarlane2011:r1-22:inf_main |
| 29 | True | 0 | macfarlane2014:r71-92:n28 → macfarlane2014:r71-92:i5 |
| 31 | True | 0 | macfarlane2014:r114-135:n30 → macfarlane2014:r114-135:i7 |
| 37 | True | 1 | macfarlane2014:r225-246:c_puzzle → macfarlane2014:r225-246:inf_puzzle<br>macfarlane2014:r225-246:c_sv_requires_retraction → macfarlane2014:r225-246:inf_sv_retraction |
| 39 | True | 0 | macfarlane2014:r269-279-refine:n39 → macfarlane2014:r269-279-refine:inf11<br>macfarlane2014:r269-279-refine:n49 → macfarlane2014:r269-279-refine:inf15 |
| 40 | True | 0 | macfarlane2014:r280-290-refine:c1 → macfarlane2014:r280-290-refine:inf21 |
| 45 | True | 0 | moss2015:union:item:moss2015:salvage:b115aa1188404ab0:moss2015:r21-40:n30 → moss2015:union:item:moss2015:salvage:b115aa1188404ab0:moss2015:r21-40:inf8 |
| 54 | False | 0 | veltman1996:r1-22:ic_LA1_not_additive → veltman1996:r1-22:inf_LA1_not_additive |
| 62 | True | 0 | willer2013:r21-40:c_both_problematic → willer2013:joined:willer2013:rec:inf_xr_naive_to_orthodoxy, willer2013:r21-40:inf_both_problematic |

## Targets

Model-written target prose follows verbatim. Formulas remain in the native candidate receipts; prose/formula correspondence and philosophical claims have not been independently validated.

| Target ID | Model-written target |
|---|---|
| t1_assessment_sensitivity | Epistemic modals are assessment-sensitive: the best truth-conditional semantics for them makes truth vary with the context of assessment as well as the context of use. |
| t2_contextualism_fails_data | Contextualist accounts of epistemic modals cannot explain retrospective assessments, retractions, and disagreement, however much contextual flexibility they allow. |
| t3_cloud_contextualism_undercuts_relativism | Once contextualism lets an epistemic modal bring several group-relative propositions into play instead of one fixed group, the motivation for relativism about epistemic modals fades. |
| t4_equally_problematic | Contextualism and relativism about epistemic modals are equally problematic views. |
| t5_transparency_false | The transparency theory of modal knowledge is false: knowing that A might be the case is not equivalent to A being compatible with what one knows. |
| t6_genuine_contradictions | Epistemic contradictions (p and might-not-p) are genuine contradictions, and the logic of epistemic modals should give up distributivity and disjunctive syllogism while keeping the other classical laws. |
| t7_relation_to_content | Epistemic modality is better treated as a distinct relation to content than as a distinct kind of content. |
| t8_semantic_over_pragmatic_expressivism | Merely pragmatic expressivist frameworks for epistemic modals, such as domain semantics and update semantics, miss the right constraints on assertibility. A semantic expressivism that maps information states to truth-values meets those constraints. |
| t9_J_based_relativism_undermined | Ordinary speakers do not generally judge a bare 'might' claim false when its prejacent conflicts with their own information. This undermines arguments for relativism that rest on such assessor-relative truth judgments. |
| t10_asymmetric_perspectivality | If epistemic possibility is perspectival, it is only asymmetrically so: an assessor's knowledge affects the truth of an epistemic modal claim only when the assessor knows more than the original speaker. |

## Search outcomes and partial evidence

Native search phase: **stopped**. 8/20 jobs completed; failed indices [1, 5, 7, 11]; canceled indices [12, 13, 14, 15, 16, 17, 18, 19]; retried indices []. Missing polarity or unavailable paired analysis is not evidence of no conflicts. OPEN is not a proof; CLOSED is relative to formalized T and licensed steps.

| Job | Goal ID | Attempts | Final status | Recorded failure |
|---|---|---|---|---|
| 0 | t1_assessment_sensitivity | 1 | completed | None |
| 1 | not:t1_assessment_sensitivity | 1 | failed | BudgetStop |
| 2 | t2_contextualism_fails_data | 1 | completed | None |
| 3 | not:t2_contextualism_fails_data | 1 | completed | None |
| 4 | t3_cloud_contextualism_undercuts_relativism | 1 | completed | None |
| 5 | not:t3_cloud_contextualism_undercuts_relativism | 1 | failed | BudgetStop |
| 6 | t4_equally_problematic | 1 | completed | None |
| 7 | not:t4_equally_problematic | 1 | failed | BudgetStop |
| 8 | t5_transparency_false | 1 | completed | None |
| 9 | not:t5_transparency_false | 1 | completed | None |
| 10 | t6_genuine_contradictions | 1 | completed | None |
| 11 | not:t6_genuine_contradictions | 1 | failed | BudgetStop |
| 12 | t7_relation_to_content | 0 | cancelled | None |
| 13 | not:t7_relation_to_content | 0 | cancelled | None |
| 14 | t8_semantic_over_pragmatic_expressivism | 0 | cancelled | None |
| 15 | not:t8_semantic_over_pragmatic_expressivism | 0 | cancelled | None |
| 16 | t9_J_based_relativism_undermined | 0 | cancelled | None |
| 17 | not:t9_J_based_relativism_undermined | 0 | cancelled | None |
| 18 | t10_asymmetric_perspectivality | 0 | cancelled | None |
| 19 | not:t10_asymmetric_perspectivality | 0 | cancelled | None |

| Target | Polarity | Proof nodes | Max proof depth | State receipts | Outcomes | Sealed / complete |
|---|---|---|---|---|---|---|
| t1_assessment_sensitivity | target | 1 | 0 | 2 | {"OPEN": 1} | True / True |
| t2_contextualism_fails_data | target | 1 | 0 | 2 | {"OPEN": 1} | True / True |
| t2_contextualism_fails_data | negation | 25 | 5 | 25 | {"OPEN": 5} | True / True |
| t3_cloud_contextualism_undercuts_relativism | target | 1 | 0 | 2 | {"OPEN": 1} | True / True |
| t4_equally_problematic | target | 1 | 0 | 2 | {"OPEN": 1} | True / True |
| t5_transparency_false | target | 1 | 0 | 2 | {"OPEN": 1} | True / True |
| t5_transparency_false | negation | 21 | 4 | 21 | {"OPEN": 4} | True / True |
| t6_genuine_contradictions | target | 1 | 0 | 2 | {"OPEN": 1} | True / True |

The following are raw observations of unsealed files, not authenticated trees. Native reporting preserves their bytes without interpreting them as valid completed searches.

| Declared goal | Raw proof nodes | Raw max proof depth | Raw state receipts | Artifact |
|---|---|---|---|---|
| not:t3_cloud_contextualism_undercuts_relativism | 80 | 5 | 64 | search-traces/39f4c683072dee2a-46094c5ba0954aaca63676e15211dfe4.jsonl |
| not:t6_genuine_contradictions | 31 | 3 | 16 | search-traces/65b7da605a1812da-e75409017a334f01b412980f4a270a04.jsonl |
| not:t1_assessment_sensitivity | 66 | 3 | 42 | search-traces/76bcf3fae3265bb0-58e0850c43504c0288fabd0521561a8c.jsonl |
| not:t4_equally_problematic | 78 | 5 | 40 | search-traces/d39a442d22425886-550bd861dac1415bbfe0c94f0db32ab4.jsonl |

Proof depth above is distinct from state-ancestry depth shown by the native HTML/JSON tree view. All prune reasons, trace-validation issues and failed attempts remain in the structured audit and native report.

Unavailable paired analyses: [{"note": "Completed routes retained; paired conflict analysis unavailable.", "reason": "run_stopped", "status": "partial", "target": "t1_assessment_sensitivity"}, {"note": "Completed routes retained; paired conflict analysis unavailable.", "reason": "run_stopped", "status": "partial", "target": "t2_contextualism_fails_data"}, {"note": "Completed routes retained; paired conflict analysis unavailable.", "reason": "run_stopped", "status": "partial", "target": "t3_cloud_contextualism_undercuts_relativism"}, {"note": "Completed routes retained; paired conflict analysis unavailable.", "reason": "run_stopped", "status": "partial", "target": "t4_equally_problematic"}, {"note": "Completed routes retained; paired conflict analysis unavailable.", "reason": "run_stopped", "status": "partial", "target": "t5_transparency_false"}, {"note": "Completed routes retained; paired conflict analysis unavailable.", "reason": "run_stopped", "status": "partial", "target": "t6_genuine_contradictions"}, {"note": "Completed routes retained; paired conflict analysis unavailable.", "reason": "run_stopped", "status": "partial", "target": "t7_relation_to_content"}, {"note": "Completed routes retained; paired conflict analysis unavailable.", "reason": "run_stopped", "status": "partial", "target": "t8_semantic_over_pragmatic_expressivism"}, {"note": "Completed routes retained; paired conflict analysis unavailable.", "reason": "run_stopped", "status": "partial", "target": "t9_J_based_relativism_undermined"}, {"note": "Completed routes retained; paired conflict analysis unavailable.", "reason": "run_stopped", "status": "partial", "target": "t10_asymmetric_perspectivality"}]

## Routes and model-written handoff summaries

The route IDs below were published by the native run. The requested **model-written handoff summaries** are unavailable: the native pilot ended at a global token-cap stop before `awaiting_selection`, so no summary calls were dispatched. The prepared summary step requires native completion and preserves the original caps. Route graphs remain available for inspection; no model-written summaries are claimed. No route was selected or composed.

| Route ID | Target | Polarity | Status | Model-written handoff summary |
|---|---|---|---|---|
| ec733c1f7895:r0 | t1_assessment_sensitivity | target | OPEN | UNAVAILABLE; see summary-step receipt |
| 8d3412df032e:r0 | t2_contextualism_fails_data | target | OPEN | UNAVAILABLE; see summary-step receipt |
| c94a9b5ddffe:r0 | t2_contextualism_fails_data | negation | OPEN | UNAVAILABLE; see summary-step receipt |
| c94a9b5ddffe:r1 | t2_contextualism_fails_data | negation | OPEN | UNAVAILABLE; see summary-step receipt |
| c94a9b5ddffe:r2 | t2_contextualism_fails_data | negation | OPEN | UNAVAILABLE; see summary-step receipt |
| c94a9b5ddffe:r3 | t2_contextualism_fails_data | negation | OPEN | UNAVAILABLE; see summary-step receipt |
| c94a9b5ddffe:r4 | t2_contextualism_fails_data | negation | OPEN | UNAVAILABLE; see summary-step receipt |
| 406a93ed7772:r0 | t3_cloud_contextualism_undercuts_relativism | target | OPEN | UNAVAILABLE; see summary-step receipt |
| 2a17c0f54e67:r0 | t4_equally_problematic | target | OPEN | UNAVAILABLE; see summary-step receipt |
| fc20bd5ec65f:r0 | t5_transparency_false | target | OPEN | UNAVAILABLE; see summary-step receipt |
| c3b81358d7a7:r0 | t5_transparency_false | negation | OPEN | UNAVAILABLE; see summary-step receipt |
| c3b81358d7a7:r1 | t5_transparency_false | negation | OPEN | UNAVAILABLE; see summary-step receipt |
| c3b81358d7a7:r2 | t5_transparency_false | negation | OPEN | UNAVAILABLE; see summary-step receipt |
| c3b81358d7a7:r3 | t5_transparency_false | negation | OPEN | UNAVAILABLE; see summary-step receipt |
| 9206c56e910e:r0 | t6_genuine_contradictions | target | OPEN | UNAVAILABLE; see summary-step receipt |

Summary-step result: {"status": "blocked", "reason": "Native run exited 2 after global token-cap STOP; awaiting_selection was not reached. The terminal global stop is authoritative, so the summary step dispatched no model calls.", "routes": 15, "already_summarized": 0, "generated": 0, "new_calls": 0, "wall_seconds": 0, "native_exit_code": 2, "budget_unchanged": true}

## Wall time and usage

| Native stage interval | Seconds |
|---|---|
| startup_and_plan | 1255.994 |
| construction_after_plan | 8443.350 |
| target_proposal | 45.820 |
| search_publication | 2291.459 |
| search_through_saved_analyses | not completed |
| route_summaries | not completed |

Native pilot command wall time: 12416.918 seconds. Startup/provenance and final export overhead are outside some stage intervals. Summed call time is not elapsed wall time because search is concurrent. Extraction was reused without new extraction calls.

Pilot, summary step if present, and standalone preflight: **240.5466362 USD-equivalent subscription usage**, **0.0 new API USD**, **29,664,890 local tokens**, 1045 model receipts, and 0 unknown-usage receipts. CLI list-price equivalent is not API spending or remaining subscription quota. Cache replays carry zero new usage.

| Kind | Receipts | Input | Cache read | Cache write | Output | Subscription equivalent USD | Summed seconds |
|---|---|---|---|---|---|---|---|
| isolation_canary | 2 | 4 | 1578 | 661 | 1992 | 0.0454596 | 37.486 |
| select_t_roots | 70 | 140 | 44298 | 4526314 | 164660 | 39.5131316 | 2763.478 |
| build_t_batch | 35 | 138 | 1170138 | 1190113 | 182674 | 13.4089636 | 2640.121 |
| propose_targets | 1 | 2 | 0 | 52070 | 2650 | 0.4695680 | 38.663 |
| map_leaf | 238 | 476 | 0 | 11743152 | 124799 | 96.4431000 | 2263.951 |
| propose_cuts | 118 | 222 | 820139 | 6083307 | 157975 | 61.1390522 | 1825.417 |
| formalise | 537 | 648 | 605360 | 682909 | 65810 | 11.4659440 | 2224.242 |
| answer_cq | 43 | 80 | 22737 | 1966551 | 51263 | 18.0342892 | 690.482 |

The standalone preflight is additional to the per-kind table: {"calls": 1, "api_usd": "0.0", "subscription_equivalent_usd": "0.027128", "tokens": {"input_tokens": 2, "output_tokens": 908, "cache_read_tokens": 0, "cache_write_tokens": 1120, "server_tool_uses": 0}, "summed_call_wall_seconds": 8.967394808016252, "unknown_calls": 0}.

Full-lineage historical API accounting remains measured USD131.785270 plus USD1.844820 unknown reservations, total USD133.630090. Historical unknown actual usage remains unknown. Per-run totals include imported history and must not be added together.

## Every refusal, retry and stop

| Timestamp UTC | Stage | Reason / diagnostic | Scope |
|---|---|---|---|
| 2026-10-24T04:48:59.505415+00:00 | build_t_batch | shared symbol token allowance exceeded | provider/runtime |
| 2026-10-24T04:49:43.345636+00:00 | build_t_batch | construction correction repeats unchanged item | provider/runtime |
| 2026-10-24T05:13:58.336365+00:00 | build_t_batch | shared symbol token allowance exceeded | provider/runtime |
| 2026-10-24T05:43:09.061994+00:00 | answer_cq | unknown CQ T id | provider/runtime |
| 2026-10-24T05:45:50.174223+00:00 | provider_error | CLI diagnostic suppressed. | provider/runtime |
| 2026-10-24T05:45:50.598449+00:00 | propose_cuts | ClaudeCodeError | provider/runtime |
| 2026-10-24T05:45:51.047726+00:00 | provider_retry | cli_max_turns | provider/runtime |
| 2026-10-24T05:48:33.789866+00:00 | answer_cq | unknown CQ T id | provider/runtime |
| 2026-10-24T05:49:17.407601+00:00 | answer_cq | unknown CQ T id | provider/runtime |
| 2026-10-24T06:07:58.162939+00:00 | map_leaf | token cap: request reservation exceeds remaining tokens | run |
| 2026-10-24T06:13:51.280985+00:00 | search_analysis_failed | run_stopped | provider/runtime |
| 2026-10-24T06:14:14.788391+00:00 | search_analysis_failed | run_stopped | provider/runtime |
| 2026-10-24T06:15:19.201050+00:00 | search_analysis_failed | run_stopped | provider/runtime |
| 2026-10-24T06:15:43.384644+00:00 | search_analysis_failed | run_stopped | provider/runtime |
| 2026-10-24T06:16:06.452875+00:00 | search_analysis_failed | run_stopped | provider/runtime |
| 2026-10-24T06:17:05.584484+00:00 | search_analysis_failed | run_stopped | provider/runtime |
| 2026-10-24T06:17:29.353104+00:00 | search_analysis_failed | run_stopped | provider/runtime |
| 2026-10-24T06:17:35.347496+00:00 | search_analysis_failed | run_stopped | provider/runtime |
| 2026-10-24T06:17:41.331996+00:00 | search_analysis_failed | run_stopped | provider/runtime |
| 2026-10-24T06:17:47.239402+00:00 | search_analysis_failed | run_stopped | provider/runtime |

| Search failure timestamp | Job | Attempt | Failure |
|---|---|---|---|
| 2026-10-24T06:07:59.952070+00:00 | 7 | 1 | BudgetStop |
| 2026-10-24T06:08:09.753152+00:00 | 11 | 1 | BudgetStop |
| 2026-10-24T06:08:10.379012+00:00 | 1 | 1 | BudgetStop |
| 2026-10-24T06:08:16.320230+00:00 | 5 | 1 | BudgetStop |

Full refusal payloads and allowlisted diagnostic metadata are preserved in `pilot-audit.json` and the native event sidecars. Job failure, retry and final outcome are distinct; a failed attempt is not counted as a permanently failed job after successful recovery.

## Delivered report and verification

Native `ara report` covered **31 inputs**, including the original full lineage, pilot 1, both standalone preflights and pilot 2. The entire linked bundle was copied to `/home/dev/ara-work/reports/overnight/final2`: **23,640 files / 2,194,463,000 bytes**, every SHA-256 matched. HTML is **1,317,993 bytes (1.317993 decimal MB)** and opened in Chromium 143.0.7499.4. All 2,752 links/anchors passed; no page errors or missing anchors were recorded. Keep all sidecars with the HTML.

Browser no-overflow check: **False**. Desktop viewport/document width: 1440/1440; mobile: 390/403. Any overflow is retained as a rendering limitation; native report bytes are not silently altered.

The audit reconstructed 68,330 event occurrences from 21,779 unique bodies and verified 601 native artifact copies. Inputs and anchors were unchanged. The new pilot contributes 12 trace entries. Sealed trees and unsealed prefixes remain distinct. HTML previews are bounded; complete linked JSON/DOT and construction data retain omitted preview material. SVG availability is recorded in the tree exports.

Browser inspection expanded search `c94a9b5ddffe:1`: 25 proof nodes, proof depth 5, and state-ancestry depth 11. Its full JSON link opened in Chromium; its DOT file was verified. No SVG was emitted for this tree; complete JSON and DOT remain available. Desktop and mobile screenshots were inspected. The mobile document is 403 pixels wide at a 390-pixel viewport, a retained 13-pixel overflow.

Screenshots and browser receipts are in the control directory. Hash chains detect changes relative to checkpoints; they do not protect against rewriting both chain and checkpoint. This is a run/report verification, not a semantic-success or whole-product release verdict.

## Remaining limits and recovery

Frozen coverage is 15/26 papers. Published extraction artifacts do not establish complete extraction: earlier partial sources, quarantines, omitted/unread material, missing metadata and unknown historical accounting remain in the full lineage and preserved handoffs. The provider permits Anthropic built-ins, SDK/runtime context and StructuredOutput; effective context is not byte-identical to the API path. Canary results are specific to this CLI/environment, and calibrated estimates remain empirical.

Any failed searches, unavailable analysis or missing summaries above remain unresolved. Retained routes do not erase those gaps. Preserve this run and its accounting; do not select a route without an operator instruction. `resume-construction` is applicable only before the single freeze, never as a way to rebuild an already frozen T. No checks or budgets were weakened to force completion.

## Finding placement

| Finding | Section |
|---|---|
| 1. Requested revision, exact review boundary, configuration and canaries | Revision, configuration and review boundary |
| 2. Corrected calibration and historical skip interpretation | Corrected calibration, budgets and retries |
| 3. Local cap, retained history, live catalogue limits and bounded retry policy | Corrected calibration, budgets and retries |
| 4. Freeze, per-paper coverage and kind counts | Frozen T and paper coverage |
| 5. Every window contribution and skip | Every construction window and skip |
| 6. Accepted and discarded omitted-support cuts | Omitted-support cuts |
| 7. Targets and unverified prose/formula correspondence | Targets |
| 8. Job attempts, polarity outcomes, partial traces and unavailable analysis | Search outcomes and partial evidence |
| 9. Route IDs, attributed summaries, any missing summaries and no selection | Routes and model-written handoff summaries |
| 10. Timing, tokens, subscription/API distinction, unknowns and every refusal | Wall time and usage; Every refusal, retry and stop |
| 11. Full-lineage copy, browser limitations, tree data and verification trust limits | Delivered report and verification |
| 12. Historical extraction, provider-context and recovery limits | Remaining limits and recovery |

12 findings, 12 placed.

DONE zeta subagent-pilot-2 freeze=/home/dev/ara-scaffold/runs/subagent-pilot-2/commitments.json commitments=95 papers_in_T=15/26 targets=10 searches_ok=8/20 routes=15 status=blocked:token-cap report=/home/dev/ara-work/reports/overnight/final2/report.html
