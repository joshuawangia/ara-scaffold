# Zeta subagent pilot

**Blocked during search.** The fresh pilot froze **34 commitments from 8/26 papers** and proposed **10 targets**. It did not reach `awaiting_selection`, publish selectable routes, or select a route. Native execution exited **2** after non-retryable `cli_exit_error` failures. No new API charge occurred.

[Open the full report](/home/dev/ara-work/reports/overnight/final/report.html). [Frozen T](/home/dev/ara-scaffold/runs/subagent-pilot/commitments.json). [Structured audit](/home/dev/ara-scaffold/runs/subagent-pilot-control/pilot-audit.json). The prior handoff is preserved byte-for-byte as [zeta-full26-part7.md](/home/dev/ara-work/reports/zeta-full26-part7.md); the interim report is also preserved.

## Execution and stop

Source was clean at `852b21796191111c916be944648e3a42cac359ec` before launch and at the delivery checkpoint. Read Omega’s five provider rounds and Psi’s Final/Final 2 review. The independently reviewed 799-passed/2-skipped tests and 375 restored negative controls are prior review evidence, not tests rerun in this execution. No tracked source edit, commit, push, credential rotation, API fallback, or extraction rerun occurred.

The native standalone canary passed in 8.677 seconds. The pilot’s startup and scoped-construction canaries also passed. All construction, target, search and writing configuration resolves to `claude_code` / `claude-opus-5-5`, no fallback; cap multiplier 2, search concurrency 4 and provider concurrency 4. The audience was explicitly empty, profile `pilot`, and the pilot/cache directories were fresh. No part-6 construction batches were restored. Historical extraction receipts were imported normally.

The unchanged literature is `/home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt`, SHA-256 `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`. Frozen artifact SHA-256: `ceb6628ad5b21ff796a670182f138c6fe305dd44bd4912e4ecc3150ff50e7077`.

The first failure was search job 9, the negative polarity of `t5_nonclassical_logic`, at 22:13:29 UTC. A `propose_cuts` process exited 1; native accounting retained measured usage and rejected the result. The provider records `cli_exit_error` and “CLI diagnostic suppressed.” The underlying complaint is unavailable. This is not evidence of a rate limit, account exhaustion, context overflow, or a specific CLI turn-limit cause. No retryable rate-limit classification or provider backoff was recorded.

Native failure handling canceled queued futures but waited for entire running searches, which continued making model calls. It did not stop dispatch within each active search after the first failure. The receipts below preserve every failed job; this drain behavior explains the additional wall time and subscription usage. No pilot was relaunched.

| Job | Timestamp UTC | Native failure |
|---|---|---|
| 9 | 2026-10-23T22:13:29.545541+00:00 | Rejected |
| 1 | 2026-10-23T22:22:59.903058+00:00 | Rejected |
| 7 | 2026-10-23T23:06:04.608260+00:00 | BudgetStop |
| 5 | 2026-10-23T23:06:30.840330+00:00 | BudgetStop |

The two remaining active searches then stopped on the unchanged token budget: job 7 at 23:06:04 UTC and job 5 at 23:06:30 UTC. The admission STOP at 23:06:03 UTC recorded 29,824,229 used tokens and refused a request because used tokens plus in-flight/new reservations exceeded 30,000,000. Final recorded pilot tokens were 18,509,550; adding 11,348,025 imported historical tokens gives 29,857,575. These are reservation-based stops below the measured cap, not a raised limit. Stable publication completed before the terminal `cli_exit_error`; no searches remain active.

After the first failed-job receipt, 1053 further model receipts recorded 101.5901996 USD-equivalent subscription usage and 9,784,541 tokens. This includes calls already in flight at failure and zero-new-usage cache replays. Separately, 575 new `call_start` receipts were recorded after that failure while native searches drained.

## Frozen T and coverage

Exactly one freeze was recorded. The 34 frozen IDs equal the union of accepted batch IDs; no skipped batch entered T. Paper and kind counts use exact evidence-ID/citation linkage. These checks establish structural provenance, not faithful formalization or the truth of the commitments. Coverage is 8/26 papers, not full-corpus representation.

| Paper ID | Commitments in T |
|---|---|
| vonfintelgillies2007 | 0 |
| eganweatherson2011 | 8 |
| vonfintelgillies2011 | 0 |
| wright2007 | 0 |
| schaffer2011 | 0 |
| braun2012 | 0 |
| eganhawthorneweatherson2005 | 3 |
| egan2007 | 9 |
| macfarlane2011 | 0 |
| yalcin2007 | 0 |
| yalcin2011 | 0 |
| rothschild2012 | 0 |
| moss2015 | 0 |
| hawkesteinertthrelkeld2021 | 3 |
| veltman1996 | 0 |
| gsv1996 | 2 |
| willer2013 | 0 |
| ninan2018 | 0 |
| beddorgoldstein2021 | 4 |
| hollidaymandelkern2024 | 4 |
| kolodnymacfarlane2010 | 0 |
| knobeyalcin2014 | 0 |
| klinedinstrothschild2012 | 1 |
| bledin2014 | 0 |
| yalcin2015 | 0 |
| macfarlane2014 | 0 |

| Kind | Commitments in T |
|---|---|
| attacked_view | 1 |
| conclusion | 10 |
| intermediate_conclusion | 6 |
| distinction | 4 |
| reported_view | 3 |
| qualification | 7 |
| inference | 1 |
| premise | 2 |

## Construction windows and every skip

The live plan had 70 funded windows, equal initial shares of 2, fixed caps of 4, 160 global slots and 140 projected commitments. Actual contribution was 12 accepted windows / 34 commitments, with 58 skipped windows. Planning allocations were not guarantees. The original limits remained: 70,000 batch input, 100,000 working T, 48,000 catalogue, 233 symbol-growth reservation, 200,000 model context and 30,000,000 total run tokens.

The first measured formalization raised the `build_t_batch` estimate factor from 0.553224 to 1.4237247019683947: 30,294 measured aggregate input tokens versus 12,922 estimated initial tokens, on 21,642 request bytes. The reviewed estimator compares aggregate two-turn input with initial input and only raises its factor. Subsequent catalogue and context estimates became substantially larger. Many later windows failed the final counted-context admission check even after closure selection. This is observed native behavior; no bound or estimator was weakened to force contributions.

Window indices are zero-based. “Uncut” and “retained” describe the attempted closure; only the “new in T” column counts accepted commitments. Full per-item omissions, relevance explanations, and attempted closures remain in the native linked construction receipts.

| Window | Paper IDs | Roots | Uncut | Retained | New in T | Outcome / complete skip reason |
|---|---|---|---|---|---|---|
| 0 | beddorgoldstein2021 | 4 | 4 | 4 | 4 | accepted |
| 1 | beddorgoldstein2021, bledin2014 | 2 | 64 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 2 | bledin2014, braun2012 | 2 | 40 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 3 | braun2012 | 1 | 12 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 4 | braun2012, egan2007 | 2 | 4 | 4 | 4 | accepted |
| 5 | egan2007 | 1 | 9 | 4 | 4 | accepted |
| 6 | egan2007, eganhawthorneweatherson2005 | 2 | 117 | 3 | 3 | accepted |
| 7 | eganhawthorneweatherson2005 | 1 | 27 | 1 | 1 | accepted |
| 8 | eganhawthorneweatherson2005, eganweatherson2011 | 2 | 89 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 9 | eganweatherson2011 | 4 | 7 | 4 | 4 | accepted |
| 10 | eganweatherson2011, gsv1996 | 1 | 4 | 4 | 4 | accepted |
| 11 | gsv1996 | 2 | 6 | 2 | 2 | accepted |
| 12 | gsv1996 | 2 | 7 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 13 | gsv1996, hawkesteinertthrelkeld2021 | 1 | 11 | 2 | 2 | accepted |
| 14 | hawkesteinertthrelkeld2021 | 1 | 48 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 15 | hawkesteinertthrelkeld2021, hollidaymandelkern2024 | 2 | 4 | 4 | 4 | accepted |
| 16 | hollidaymandelkern2024 | 3 | 3 | 3 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 17 | hollidaymandelkern2024 | 1 | 13 | 2 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 18 | hollidaymandelkern2024 | 1 | 5 | 1 | 1 | accepted |
| 19 | hollidaymandelkern2024 | 1 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 20 | hollidaymandelkern2024, klinedinstrothschild2012 | 3 | 17 | 3 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 21 | klinedinstrothschild2012 | 1 | 9 | 1 | 1 | accepted |
| 22 | klinedinstrothschild2012, knobeyalcin2014 | 2 | 13 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 23 | knobeyalcin2014, kolodnymacfarlane2010 | 2 | 41 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 24 | kolodnymacfarlane2010, macfarlane2011 | 1 | 16 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 25 | macfarlane2011 | 2 | 41 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 26 | macfarlane2011, macfarlane2014 | 1 | 85 | 2 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 27 | macfarlane2014 | 3 | 3 | 3 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 28 | macfarlane2014 | 2 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 29 | macfarlane2014 | 1 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 30 | macfarlane2014 | 2 | 2 | 2 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 31 | macfarlane2014 | 1 | 9 | 2 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 32 | macfarlane2014 | 3 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 33 | macfarlane2014 | 3 | 3 | 3 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 34 | macfarlane2014 | 0 | 0 | 0 | 0 | This window is from MacFarlane 2014 and covers two topics, neither of which is epistemic modals. The first is the end of the taste-predicate chapter: binding and tense with 'tasty', judge-in-index views, mind-dependence, and Gibbardian expressivism about 'tasty' compared with relativism. The second is the knowledge-attribution chapter: the Closure conundrum, contextualism, semantic blindness, and subject-sensitive invariantism. The debate between expressivism and relativism about disagreement and retraction (r28/r46) is similar in structure to the debate over epistemic modals. But here it is argued only for 'tasty', and the book's epistemic-modal material appears in other windows. The window adds no new symbols and its commitment allowance is small. Spending it on taste or 'knows' arguments would take capacity away from sources that address epistemic modals directly. So the whole window is left out and every group has an accounted omission. |
| 35 | macfarlane2014 | 1 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 36 | macfarlane2014 | 3 | 3 | 3 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 37 | macfarlane2014 | 0 | 0 | 0 | 0 | I selected no roots from this window. The whole window comes from MacFarlane 2014's chapter on future contingents (pp. 225–249). It compares the Peircean, Thin Red Line, three-valued, supervaluationist and relativist semantics for "will" and historical necessity (□ as settledness), and opens the credence and wondering problems about objective branching. The topic is epistemic modals, and none of these arguments is about epistemic "might", "must" or "probably". Assessment sensitivity is the framework MacFarlane also uses for epistemic modals, but here it is argued for only through retrospective accuracy judgments about predictions. Formalizing it would bring in future-tense and branching-time machinery that the epistemic-modal analysis does not use. The cheapest bridging root (r10, "we need assessment sensitivity") has an 11-item closure, well over the hard cap of 4. The soft per-window target is 0, and fewer than 3.3k symbol tokens remain, so it would be cut off at the frontier and contribute little. The budget is better kept for windows that deal with epistemic modals directly. |
| 38 | macfarlane2014 | 4 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 39 | macfarlane2014 | 1 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 40 | macfarlane2014 | 1 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 41 | macfarlane2014 | 3 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 42 | macfarlane2014, moss2015 | 2 | 5 | 2 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 43 | moss2015 | 1 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 44 | moss2015 | 2 | 13 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 45 | moss2015 | 2 | 12 | 2 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 46 | moss2015 | 1 | 13 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 47 | moss2015, ninan2018 | 2 | 14 | 2 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 48 | ninan2018 | 1 | 26 | 2 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 49 | ninan2018, rothschild2012 | 2 | 47 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 50 | rothschild2012, schaffer2011 | 2 | 61 | 3 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 51 | schaffer2011 | 2 | 9 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 52 | schaffer2011 | 3 | 11 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 53 | schaffer2011, veltman1996 | 2 | 9 | 3 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 54 | veltman1996 | 1 | 5 | 1 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 55 | veltman1996, vonfintelgillies2007 | 4 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 56 | vonfintelgillies2007 | 4 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 57 | vonfintelgillies2007 | 2 | 16 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 58 | vonfintelgillies2011 | 2 | 35 | 2 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 59 | vonfintelgillies2011 | 2 | 37 | 2 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 60 | vonfintelgillies2011 | 1 | 36 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 61 | vonfintelgillies2011, willer2013 | 3 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 62 | willer2013 | 1 | 7 | 1 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 63 | willer2013, wright2007 | 2 | 11 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 64 | wright2007, yalcin2007 | 4 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 65 | yalcin2007 | 1 | 19 | 1 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 66 | yalcin2007, yalcin2011 | 3 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 67 | yalcin2011, yalcin2015 | 2 | 4 | 4 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 68 | yalcin2015 | 1 | 7 | 3 | 0 | build_t_batch context bound exceeded by counted request; no truncation |
| 69 | yalcin2015 | 2 | 10 | 3 | 0 | build_t_batch context bound exceeded by counted request; no truncation |

## Omitted-support cuts

9 frozen commitments explicitly carry `support_omitted`. Accepted cuts are assumptions at the recorded frontier, not proofs of their omitted support. The table also retains attempted cuts from skipped windows; those never entered T.

| Window | Entered T? | Cut depth | Commitment → omitted support IDs |
|---|---|---|---|
| 5 | yes | 0 | `egan2007:salvage:dec68a6bbc12fd01:egan2007:r1-19:n_relativist_might` → `egan2007:salvage:dec68a6bbc12fd01:egan2007:r1-19:inf_relativist_might` |
| 6 | yes | 0 | `egan2007:salvage:65b686e45c7b24fd:egan2007:r20-39:c_final` → `egan2007:salvage:65b686e45c7b24fd:egan2007:r20-39:inf_final`<br>`eganhawthorneweatherson2005:r1-24:n_concl_rel` → `eganhawthorneweatherson2005:joined:inf_g42_final`, `eganhawthorneweatherson2005:r1-24:n_inf_rel` |
| 7 | yes | 0 | `eganhawthorneweatherson2005:joined:g29_ic_avoid_both` → `eganhawthorneweatherson2005:joined:inf_g29_avoid_both` |
| 9 | yes | 0 | `eganweatherson2011:r1-21:ic16` → `eganweatherson2011:r1-21:inf21` |
| 11 | yes | 0 | `gsv1996:r18-35:n_order` → `gsv1996:r18-35:inf1` |
| 13 | yes | 0 | `hawkesteinertthrelkeld2021:r1-9-refine:n7` → `hawkesteinertthrelkeld2021:r1-9-refine:inf1`, `hawkesteinertthrelkeld2021:r1-9-refine:inf10` |
| 14 | no | 1 | `hawkesteinertthrelkeld2021:r10-19-refine:n_pragmatic_fails` → `hawkesteinertthrelkeld2021:r10-19-refine:inf_pragmatic_fails`<br>`hawkesteinertthrelkeld2021:r10-19-refine:n_summary_constraints` → `hawkesteinertthrelkeld2021:r10-19-refine:inf_summary` |
| 17 | no | 0 | `hollidaymandelkern2024:r18-35:d12` → `hollidaymandelkern2024:r18-35:d_inf3` |
| 18 | yes | 0 | `hollidaymandelkern2024:r36-52:c18` → `hollidaymandelkern2024:r36-52:inf_c18` |
| 20 | no | 0 | `hollidaymandelkern2024:r53-70:c_possibility_framework` → `hollidaymandelkern2024:r53-70:inf_possibility_framework`<br>`klinedinstrothschild2012:r1-12-refine:c_peculiar` → `klinedinstrothschild2012:r1-12-refine:i_peculiar` |
| 21 | yes | 0 | `klinedinstrothschild2012:r1-12-refine:c_modaldyn` → `klinedinstrothschild2012:r1-12-refine:i_modaldyn` |
| 23 | no | 0 | `knobeyalcin2014:r1-21:cc1` → `knobeyalcin2014:r1-21:inf8`<br>`knobeyalcin2014:r1-21:cc2` → `knobeyalcin2014:r1-21:inf9` |
| 25 | no | 0 | `macfarlane2011:r1-22:main_concl` → `macfarlane2011:r1-22:inf_main` |
| 26 | no | 0 | `macfarlane2011:joined:r23-44:final` → `macfarlane2011:joined:r23-44:inf_final` |
| 31 | no | 0 | `macfarlane2014:r114-135:n30` → `macfarlane2014:r114-135:i7` |
| 42 | no | 0 | `moss2015:union:item:moss2015:salvage:8ada77f0a96c0388:moss2015:r61-81:ic13` → `moss2015:union:item:moss2015:salvage:8ada77f0a96c0388:moss2015:r61-81:inf13` |
| 45 | no | 0 | `moss2015:union:item:moss2015:salvage:b115aa1188404ab0:moss2015:r21-40:n32` → `moss2015:union:item:moss2015:salvage:b115aa1188404ab0:moss2015:r21-40:inf9` |
| 47 | no | 0 | `moss2015:union:item:moss2015:salvage:e986b46e97e98057:moss2015:r11-20:p16_pragmatic` → `moss2015:union:item:moss2015:salvage:e986b46e97e98057:moss2015:r11-20:inf8`<br>`ninan2018:r1-22:ic_problem_for_everyone` → `ninan2018:joined:rec_i14` |
| 48 | no | 0 | `ninan2018:r23-45:n58` → `ninan2018:r23-45:inf18` |
| 50 | no | 0 | `schaffer2011:union:item:schaffer2011:r26-49:c_final` → `schaffer2011:union:item:schaffer2011:r26-49:inf_final` |
| 52 | no | 0 | `schaffer2011:union:item:schaffer2011:salvage:666c341ba755e3a8:schaffer2011:r2-25:n4` → `schaffer2011:union:item:schaffer2011:salvage:666c341ba755e3a8:schaffer2011:r2-25:inf1` |
| 53 | no | 0 | `schaffer2011:union:item:schaffer2011:salvage:666c341ba755e3a8:schaffer2011:r2-25:n88` → `schaffer2011:union:item:schaffer2011:salvage:666c341ba755e3a8:schaffer2011:r2-25:inf20` |
| 54 | no | 0 | `veltman1996:r1-22:ic_LA1_not_additive` → `veltman1996:r1-22:inf_LA1_not_additive` |
| 58 | no | 0 | `vonfintelgillies2011:union:item:vonfintelgillies2011:salvage:102d49a275b6d08b:vonfintelgillies2011:r1-11:a_other_options` → `vonfintelgillies2011:union:item:vonfintelgillies2011:salvage:102d49a275b6d08b:vonfintelgillies2011:r1-11:link_other_options` |
| 59 | no | 0 | `vonfintelgillies2011:union:item:vonfintelgillies2011:salvage:eccdcb12d37ac9c1:vonfintelgillies2011:joined2:r12-23:c_overall` → `vonfintelgillies2011:union:item:vonfintelgillies2011:salvage:eccdcb12d37ac9c1:vonfintelgillies2011:joined2:r12-23:link_conclusion` |
| 62 | no | 0 | `willer2013:r21-40:c_both_problematic` → `willer2013:joined:willer2013:rec:inf_xr_naive_to_orthodoxy`, `willer2013:r21-40:inf_both_problematic` |
| 65 | no | 0 | `yalcin2007:r23-33:c_informational_favoured` → `yalcin2007:r23-33:i13` |
| 68 | no | 0 | `yalcin2015:r1-26:n49` → `yalcin2015:r1-26:inf16` |
| 69 | no | 0 | `yalcin2015:r40-53:ic_standard_needs_modification` → `yalcin2015:r40-53:inf_standard_fails` |

## Targets

These are the model-proposed targets, verbatim. Their formulas are in the linked native candidate receipt and [targets.json](/home/dev/ara-scaffold/runs/subagent-pilot-control/targets.json). Neither the prose/formula correspondence nor the philosophical claims have been independently validated.

| Target ID | Model-written target |
|---|---|
| t1_relativism_best | A relativist semantics for epistemic modals, on which the truth of an utterance of 'a might be F' varies with the context of assessment, captures the behaviour of epistemic modals better than contextualism or other rivals. |
| t2_transparency_fails | Knowledge Transparency is false: knowing that p might be the case is not equivalent to p's being compatible with what one knows, because modal beliefs can fail to be knowledge through falsity, lack of justification, or Gettierization. |
| t3_semantic_expressivism | Semantic expressivism about epistemic modals is correct: the semantic value of an epistemic modal declarative is (partly) the property of doxastic attitudes it canonically serves to express, not a truth-valued proposition about someone's knowledge. |
| t4_contextualism_indeterminacy | Contextualism about epistemic modals, supplemented with indeterminacy about which group's information is relevant, has enough resources to explain the disagreement and retraction data, so the motivation for relativism fades. |
| t5_nonclassical_logic | The logic of epistemic modals should be minimally non-classical: Wittgenstein sentences (p and might not-p) are contradictions, yet might not-p does not entail not-p, so classical reasoning is safe within but not across epistemic levels. |
| t6_dynamic_test | Epistemic 'might' is best analysed dynamically, as a test on an information state for consistency with the prejacent, which explains why discourse order matters (e.g. 'It isn't raining... It might be raining' is unacceptable). |
| t7_relation_not_content | Epistemic modality is best understood as a distinctive relation to content rather than as a distinctive kind of content, since ordinary thinkers and children grasp epistemic modals without second-order thought about their own epistemic states. |
| t8_info_sensitive_safety | Knowledge of epistemic modal claims is governed by an information-sensitive safety condition: one knows that p might (or probably) obtain only if, at all nearby worlds where one holds the modal belief, it is true relative to that world's worldly information (objective chance or evidential probability). |
| t9_relativism_survives_communication | Relativism about epistemic modals survives the communicative objection: the presupposition of relevant similarity between speaker and audience is typically in place when epistemic 'might' claims are asserted, so relativist assertion remains a sensible communicative practice. |
| t10_local_context_modals | Epistemic modals are interpreted relative to local contexts in the same way presuppositions are, so their interpretation inside disjunctions (and other connectives) is shifted by the preceding material rather than fixed by the global context. |

## Search outcomes by target and polarity

Twenty target/polarity jobs were scheduled. Completed, authenticated traces are distinguished from unsealed raw observations and jobs that never started. Node/depth figures for an unsealed artifact are only observations of its retained bytes; native reporting does not authenticate or reconstruct that artifact as a valid tree. An OPEN outcome is not a proof, and a CLOSED outcome is relative to formalized T and licensed steps.

Final job counts: 7 completed, 4 failed (2 CLI failures and 2 budget stops), and 9 canceled before starting. The seven sealed traces contain eight completed graphs, all OPEN. Four additional trace artifacts remain unsealed.

| Target | Polarity | Proof nodes | Max proof depth | State receipts | Outcomes | Evidence state |
|---|---|---|---|---|---|---|
| t1_relativism_best | target | 1 | 0 | 2 | {"OPEN": 1} | complete, sealed |
| t1_relativism_best | negation | 72 | 3 | 43 | no complete result | PARTIAL, unsealed raw observations |
| t2_transparency_fails | target | 1 | 0 | 2 | {"OPEN": 1} | complete, sealed |
| t2_transparency_fails | negation | 10 | 3 | 10 | {"OPEN": 2} | complete, sealed |
| t3_semantic_expressivism | target | 1 | 0 | 2 | {"OPEN": 1} | complete, sealed |
| t3_semantic_expressivism | negation | 211 | 6 | 127 | no complete result | PARTIAL, unsealed raw observations |
| t4_contextualism_indeterminacy | target | 1 | 0 | 2 | {"OPEN": 1} | complete, sealed |
| t4_contextualism_indeterminacy | negation | 183 | 5 | 124 | no complete result | PARTIAL, unsealed raw observations |
| t5_nonclassical_logic | target | 1 | 0 | 2 | {"OPEN": 1} | complete, sealed |
| t5_nonclassical_logic | negation | 16 | 3 | 13 | no complete result | PARTIAL, unsealed raw observations |
| t6_dynamic_test | target | 1 | 0 | 2 | {"OPEN": 1} | complete, sealed |
| t6_dynamic_test | negation | — | — | — | none | not started; canceled after failure |
| t7_relation_not_content | target | — | — | — | none | not started; canceled after failure |
| t7_relation_not_content | negation | — | — | — | none | not started; canceled after failure |
| t8_info_sensitive_safety | target | — | — | — | none | not started; canceled after failure |
| t8_info_sensitive_safety | negation | — | — | — | none | not started; canceled after failure |
| t9_relativism_survives_communication | target | — | — | — | none | not started; canceled after failure |
| t9_relativism_survives_communication | negation | — | — | — | none | not started; canceled after failure |
| t10_local_context_modals | target | — | — | — | none | not started; canceled after failure |
| t10_local_context_modals | negation | — | — | — | none | not started; canceled after failure |

The table counts proof-node receipts and their recorded search depth. The HTML separately counts state-ancestry nodes and depth: the completed negative `t2_transparency_fails` tree has 10 state nodes, 9 edges and state-ancestry depth 7, while its proof-node depth above is 3. Each other completed tree has 2 state nodes, 1 edge and state-ancestry depth 1. These are different metrics, not conflicting counts.

All recorded prune reasons and trace-validation issues are retained in `pilot-audit.json` and the native report’s search section. No completed analysis, conflict/robustness verdict, or all-target completion is inferred from a partial trace.

## Routes and requested model summaries

**No selectable route IDs were published.** The failure interrupted the batch before native route publication and `awaiting_selection`. The completed trace graphs below are retained evidence, not routes available to `ara select`. No route was selected. The prepared Claude Code summary step was not run after the unrecoverable provider failure, so native model-written route summaries remain unavailable. No summary receipt was fabricated.

| Completed trace target | Graph ID (not selectable) | Status | Recorded root text |
|---|---|---|---|
| t1_relativism_best | e8929e5744ee:r0 | OPEN | A relativist semantics for epistemic modals, on which the truth of an utterance of 'a might be F' varies with the context of assessment, captures the behaviour of epistemic modals better than contextualism or other rivals. |
| t2_transparency_fails | 237acaa9ffb8:r0 | OPEN | Knowledge Transparency is false: knowing that p might be the case is not equivalent to p's being compatible with what one knows, because modal beliefs can fail to be knowledge through falsity, lack of justification, or Gettierization. |
| not:t2_transparency_fails | 3701b2976b74:r0 | OPEN | {"args":[],"name":"bg2021_knowledge_transparency","op":"atom","terms":[],"variable":null} |
| not:t2_transparency_fails | 3701b2976b74:r1 | OPEN | {"args":[],"name":"bg2021_knowledge_transparency","op":"atom","terms":[],"variable":null} |
| t3_semantic_expressivism | b0d18d05f697:r0 | OPEN | Semantic expressivism about epistemic modals is correct: the semantic value of an epistemic modal declarative is (partly) the property of doxastic attitudes it canonically serves to express, not a truth-valued proposition about someone's knowledge. |
| t4_contextualism_indeterminacy | 3822bccd5f27:r0 | OPEN | Contextualism about epistemic modals, supplemented with indeterminacy about which group's information is relevant, has enough resources to explain the disagreement and retraction data, so the motivation for relativism fades. |
| t5_nonclassical_logic | a94b69388568:r0 | OPEN | The logic of epistemic modals should be minimally non-classical: Wittgenstein sentences (p and might not-p) are contradictions, yet might not-p does not entail not-p, so classical reasoning is safe within but not across epistemic levels. |
| t6_dynamic_test | 607470752a88:r0 | OPEN | Epistemic 'might' is best analysed dynamically, as a test on an information state for consistency with the prejacent, which explains why discourse order matters (e.g. 'It isn't raining... It might be raining' is unacceptable). |

## Wall time

| Native stage interval | Elapsed seconds |
|---|---|
| startup_and_plan | 1341.438 |
| construction_after_plan | 7139.768 |
| target_proposal | 44.165 |
| search_publication | 4065.229 |
| search_through_saved_analyses | not completed |
| route_summaries | not completed |

Native command wall time: **12729.559 seconds**. Startup/provenance before `run_started` and final export/publication overhead explain differences from the stage intervals. Search is concurrent; summed model-call seconds below are not elapsed search wall time. Extraction was reused and took no new extraction-stage calls.

## Subscription usage, tokens and refusals

Pilot plus standalone preflight: **176.5945932 USD-equivalent subscription usage**, **0.0 new API USD**, 18,511,594 tokens, 1553 model receipts and 0 unknown-usage receipts. Equivalents are the CLI’s list-price accounting, not API spend or a claim about remaining subscription quota. Cached replay follows native zero-new-usage accounting.

| Call kind | Receipts | Input | Cache read | Cache write | Output | Subscription USD equivalent | Summed call seconds |
|---|---|---|---|---|---|---|---|
| isolation_canary | 2 | 4 | 1578 | 660 | 1771 | 0.0410316 | 36.773 |
| select_t_roots | 70 | 140 | 44298 | 3561930 | 165855 | 31.8219596 | 2728.778 |
| build_t_batch | 12 | 48 | 249525 | 242807 | 62190 | 3.2363530 | 855.834 |
| propose_targets | 1 | 2 | 0 | 21538 | 2566 | 0.2236320 | 36.898 |
| map_leaf | 398 | 788 | 0 | 7446967 | 181246 | 63.8392880 | 3266.021 |
| propose_cuts | 179 | 268 | 534803 | 3726900 | 240511 | 51.7862790 | 2436.869 |
| formalise | 850 | 642 | 603753 | 696945 | 74273 | 18.8164586 | 2002.194 |
| answer_cq | 40 | 64 | 18073 | 595764 | 33641 | 6.8021834 | 444.459 |

The standalone preflight is additional to the call-kind table: {"calls": 1, "api_usd": "0.0", "subscription_equivalent_usd": "0.027408", "tokens": {"input_tokens": 2, "output_tokens": 922, "cache_read_tokens": 0, "cache_write_tokens": 1120, "server_tool_uses": 0}, "summed_call_wall_seconds": 8.650887452007737, "unknown_calls": 0}.

Full historical-lineage API accounting is unchanged: measured USD131.785270 plus USD1.844820 of unknown reservations, total USD133.630090. Those three old unknown reservations remain unknown. The pilot’s imported extraction accounting is only one component of that campaign total; per-run totals must not be added.

| Timestamp UTC | Stage | Refusal / failure | Scope |
|---|---|---|---|
| 2026-10-23T20:37:44.377468+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T20:41:59.026499+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T20:43:26.782857+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T20:47:12.373613+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T20:48:41.356866+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T20:53:26.557360+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T20:55:53.919228+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T20:57:29.827838+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T20:58:57.727861+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:00:31.500796+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:02:10.481073+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:03:44.491032+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:05:21.084579+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:07:02.775708+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:08:33.273192+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:11:18.667653+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:12:49.722430+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:15:33.339661+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:17:10.721557+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:18:51.562527+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:20:34.824498+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:22:10.942381+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:23:38.127955+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:26:14.548308+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:28:53.027814+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:30:30.376256+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:33:27.247115+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:36:01.257505+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:37:40.319972+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:39:11.757285+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:40:47.518395+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:42:15.115257+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:44:51.023461+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:46:21.644053+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:48:51.024917+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:50:29.874307+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:53:18.845157+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:55:02.275415+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:56:46.476999+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T21:58:31.123494+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T22:00:33.640309+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T22:02:12.725732+00:00 | build_t_batch | build_t_batch context bound exceeded by counted request; no truncation | window |
| 2026-10-23T22:22:58.518324+00:00 | provider_error | CLI diagnostic suppressed. | provider/runtime |
| 2026-10-23T22:22:59.379288+00:00 | propose_cuts | ClaudeCodeError | provider/runtime |
| 2026-10-23T23:06:03.849895+00:00 | map_leaf | token cap: request reservation exceeds remaining tokens | run |
| 2026-10-23T22:13:29.384301+00:00 | provider_error | CLI diagnostic suppressed. | provider/runtime |
| 2026-10-23T22:13:29.457433+00:00 | propose_cuts | ClaudeCodeError | provider/runtime |
| 2026-10-23T23:11:54.031739+00:00 | runtime_error | cli_exit_error | provider/runtime |

## Delivered report and verification

Native `ara report` completed over **29 input runs**: the full 27-run historical lineage, the separate canary, and this fresh pilot. It contains **11 search trace entries**, including explicitly partial/unsealed entries. The search section is populated, but full search completion is not claimed.

Copied the complete bundle from `/home/dev/ara-scaffold/runs/subagent-pilot-report/` to `/home/dev/ara-work/reports/overnight/final/`: **16,675 files / 1,549,719,095 bytes**, every file SHA-256 matched. HTML is **1,465,827 bytes (1.465827 decimal MB)**. The delivered HTML opened in Chromium 143.0.7499.4 at desktop and mobile sizes, with no page errors or missing anchors. Desktop width passed at 1440 pixels. **The mobile no-overflow check failed:** document width was 403 pixels in a 390-pixel viewport (13 pixels of horizontal overflow). The browser receipt retains `passed: false`; this is an unresolved native rendering limitation, not a failed open or missing evidence. Source and copied report bytes were preserved. All 2,496 local links/anchors passed. Keep the linked sidecar directories with the HTML.

The audit reconstructed 57,217 exact event occurrences from 15,101 unique bodies and verified 441 artifact copies. Input logs and anchors were unchanged during report generation/copy. Sealed traces have chained byte-hash receipts; unsealed prefixes do not. Hash chains do not protect against rewriting both a chain and its checkpoint.

Desktop, mobile, collapsed-search and expanded-tree screenshots were inspected. Expanding the negative `t2_transparency_fails` tree showed populated ancestry and its two OPEN outcomes. Native HTML deliberately bounds previews to three levels; its full linked JSON and DOT retain the remaining nodes. SVG was not generated because local `dot` was unavailable. This does not remove the JSON/DOT tree data. The construction HTML also announces its bounded preview and links the full construction data.

Controls, full per-window details, trace statistics, screenshots, copy hashes and final receipts are under `/home/dev/ara-scaffold/runs/subagent-pilot-control/`. No whole-repository release or semantic-success verdict is claimed.

## Limits and recovery

The fresh T represents only 8 papers. Earlier extraction limitations remain: published artifacts for 26 papers do not establish complete extraction; partial sources, quarantines, omitted/unread material, missing original metadata and unknown historical accounting are retained in the linked extraction sections and preserved part-7 handoff. The older 140-commitment provisional T was not reused. The readable final report supersedes the old monolithic HTML rendering problem, not the historical evidence limits.

The provider’s revised isolation contract permits Anthropic built-ins, SDK/runtime context and StructuredOutput. Its effective context is not byte-identical to the API path. Canary success is specific to this CLI/environment, and calibrated token estimates are empirical rather than hard tokenizer guarantees. No credential maintenance or hidden API fallback was used.

The next unresolved step is review of the non-retryable CLI failures and a native recovery path after freeze. `resume-construction` is not applicable to this already-frozen run, and this brief does not authorize weakening checks or reconstructing selectable routes from partial evidence. Preserve this run; do not repeat construction or select a route as if search completed. No additional pilot or summary-generation call was started after the failure; only already-running searches drained under the native runner.

## Finding placement

| Finding | Section carrying it |
|---|---|
| 1. Reviewed clean revision, fresh configuration, canaries and unchanged extraction | Execution and stop |
| 2. One freeze, 34 commitments, 8/26 paper coverage and kind counts | Frozen T and coverage |
| 3. 70-window allocation, upward calibration, 12 contributions and every skip | Construction windows and every skip |
| 4. Accepted and discarded omitted-support cuts | Omitted-support cuts |
| 5. Ten model targets and unverified prose/formula correspondence | Targets |
| 6. Per-target/polarity outcomes, canceled jobs and unsealed trace limits | Search outcomes by target and polarity |
| 7. Opaque CLI failures, continued native drain usage and eventual token-budget stops | Execution and stop; Subscription usage, tokens and refusals |
| 8. No selectable routes, no model summaries, no selection and recovery boundary | Routes and requested model summaries; Limits and recovery |
| 9. Subscription accounting, zero new API spend and retained old unknowns | Subscription usage, tokens and refusals |
| 10. Stage wall time and concurrent cumulative-call distinction | Wall time |
| 11. Full-lineage copy, opened HTML, populated/partial trees, mobile overflow and verification trust limits | Delivered report and verification |
| 12. Historical extraction limits, provider-context differences and empirical estimates | Limits and recovery |

12 findings, 12 placed.

DONE zeta subagent-pilot freeze=/home/dev/ara-scaffold/runs/subagent-pilot/commitments.json commitments=34 papers_in_T=8/26 targets=10 routes=0 status=blocked:cli-exit-error-search report=/home/dev/ara-work/reports/overnight/final/report.html
