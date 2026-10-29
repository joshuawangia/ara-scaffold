# Zeta Codex pilot 3

**awaiting-selection.** 157 frozen commitments from 21/26 papers; 10.19% non-atomic. 10 targets, 20/20 completed searches, 21 routes, 10 CLOSED. No route selected.

[Full-lineage HTML report](/home/dev/ara-work/reports/overnight/codex3/report.html) · [Model-written route summaries](/home/dev/ara-work/reports/overnight/codex3/route-summaries.html) · [Structured audit](/home/dev/ara-work/reports/overnight/codex3/pilot-audit.json). The previous handoff remains unchanged at `/home/dev/ara-work/reports/zeta-codex-pilot-2-resumed.md`.


## Methodology and exact revision

This fresh pilot ran from clean detached `6511ff6cb2bb5d88c5abedc1f20b715a03324d0f` in `/home/dev/ara-work/run-6511ff6`. It includes Sigma r8 structured construction/catalogue, Xi r12 vocabulary-aware search and F2 recovery fix, the bounded validator, and Codex strict-schema transport. No repository code was edited. Upsilon2 reviewed the integrated head with zero blocking findings: 1,060 tests passed, four opt-in tests skipped, and all 450 mutation controls restored green. Those are reviewer receipts, not a test suite rerun by this operational pilot.

Extraction is imported Opus 5 output produced via Anthropic API; this pilot performed no new extraction. Construction, target proposal, search and the separately requested route summaries use isolated codex_cli calls requesting gpt-6-luna through the ChatGPT subscription. Serving model identity remains unverified. There were no new Claude or API calls and no essay composition. Native run metadata lists generic available tools; actual call receipts establish the provider used.

The same pilot-2 configuration, literature, empty audience, 100M local token cap, 60k catalogue reservation, cap multiplier 2 and concurrency 4 were retained. A new config copy changes only the schema-preflight-log binding; authentication uses the separate ChatGPT source. All 22 checked stages and construction/correction routes resolved to Codex without fallbacks. The requested fresh live schema preflight passed 15/15 cases, including formalise_slots, followed by the standalone isolation canary. The native run also performs its own isolation checks.

The live construction plan is provider-specific. Initial token estimates use historical API-receipt UTF-8 calibration seeds, then upward-only corrections from observed Codex usage; the seed is not a Codex tokenizer measurement or a new API call. The reviewer’s offline 31-window plan used a local byte/4 counter; it is not a promise of this run’s window count or token use. Admission, native schema checks, provenance, bank shape, scope checks, solver entailment and T-reference equality were retained. No increase in caps or forced closure was used.

Native resumes recorded: 0. Full resume receipts, if any, are in pilot-audit.json. The fresh run uses its own construction lifecycle and freeze; the previous 166-commitment T was not edited.


## Frozen T structure and catalogue

| Measure | Value |
|---|---|
| Frozen commitments | 157 |
| Papers covered | 21/26 |
| Non-atomic formulas | 16 |
| Non-atomic fraction | 10.1911% |
| Conditionals | 16 |
| Unique symbols | 140 |
| Commitment/symbol bindings | 182 |
| Reused bindings | 84 |
| Final-T symbol reuse | 46.1538% |
| Flat after correction batches | [] |
| All-atomic accepted batches | [1, 4, 5, 6, 7, 9, 11, 15, 16, 23, 25, 26, 27, 28, 31, 36, 38, 46, 50, 52, 54, 55, 56, 57, 58, 59, 62, 64, 67, 68, 69, 70, 73] |

Atoms and predicates count as atomic. Conditional counts include implications beneath leading quantifiers. Reuse counts a commitment/symbol binding when the exact symbol signature occurs in another frozen commitment; constants count too. These are syntactic measurements, not evidence of faithful formalization or semantic relevance. Per-batch receipts use the current and prior commitments at that point, so their rates may differ from final-T rates.

Freeze path: /home/dev/ara-scaffold/runs/codex-pilot-3/commitments.json. Freeze SHA-256: dd1145580f473db96524655c668c83eb33d927bbe743eb2229c36227ded34173. The separate frozen-t.json catalogue was verified against exact T, vocabulary signatures, definitions, evidence and its canonical hash. Catalogue SHA-256: 4966df8ce9d85544b3b78aaa2475c54cec0bfa5920acfdc7e69150754f125d61.

| Paper | Frozen commitments |
|---|---|
| vonfintelgillies2007 | 9 |
| eganweatherson2011 | 2 |
| vonfintelgillies2011 | 11 |
| wright2007 | 1 |
| schaffer2011 | 7 |
| braun2012 | 0 |
| eganhawthorneweatherson2005 | 5 |
| egan2007 | 9 |
| macfarlane2011 | 10 |
| yalcin2007 | 5 |
| yalcin2011 | 7 |
| rothschild2012 | 0 |
| moss2015 | 3 |
| hawkesteinertthrelkeld2021 | 5 |
| veltman1996 | 7 |
| gsv1996 | 2 |
| willer2013 | 6 |
| ninan2018 | 5 |
| beddorgoldstein2021 | 4 |
| hollidaymandelkern2024 | 14 |
| kolodnymacfarlane2010 | 0 |
| knobeyalcin2014 | 2 |
| klinedinstrothschild2012 | 0 |
| bledin2014 | 0 |
| yalcin2015 | 12 |
| macfarlane2014 | 31 |

| Evidence kind | Frozen commitments |
|---|---|
| conclusion | 36 |
| qualification | 20 |
| reported_view | 5 |
| distinction | 10 |
| intermediate_conclusion | 34 |
| attacked_view | 13 |
| premise | 23 |
| inference | 16 |

| Batch | Commitments | Inference items | Non-atomic | Conditionals | Connected conditionals | Reuse rate | Gate passed | Disclosure |
|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 4 | 4 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 5 | 4 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 6 | 4 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 7 | 2 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 9 | 2 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 11 | 2 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 14 | 4 | 1 | 1 | 1 | 1 | 1.0 | True | None |
| 15 | 4 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 16 | 3 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 18 | 4 | 1 | 1 | 1 | 1 | 0.8 | True | None |
| 19 | 4 | 1 | 1 | 1 | 1 | 0.8 | True | None |
| 23 | 2 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 24 | 4 | 1 | 1 | 1 | 1 | 1.0 | True | None |
| 25 | 4 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 26 | 2 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 27 | 3 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 28 | 1 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 29 | 4 | 1 | 1 | 1 | 1 | 0.8 | True | None |
| 31 | 1 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 36 | 2 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 38 | 4 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 39 | 4 | 1 | 1 | 1 | 1 | 0.8 | True | None |
| 40 | 4 | 1 | 1 | 1 | 1 | 1.0 | True | None |
| 41 | 4 | 1 | 1 | 1 | 1 | 1.0 | True | None |
| 42 | 4 | 1 | 1 | 1 | 1 | 0.8 | True | None |
| 46 | 2 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 48 | 4 | 1 | 1 | 1 | 1 | 0.8 | True | None |
| 50 | 2 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 52 | 1 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 54 | 4 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 55 | 3 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 56 | 4 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 57 | 1 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 58 | 2 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 59 | 4 | 0 | 0 | 0 | 0 | 0.25 | True | None |
| 60 | 4 | 1 | 1 | 1 | 1 | 1.0 | True | None |
| 61 | 4 | 1 | 1 | 1 | 1 | 1.0 | True | None |
| 62 | 1 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 63 | 4 | 1 | 1 | 1 | 1 | 0.8 | True | None |
| 64 | 4 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 65 | 4 | 1 | 1 | 1 | 1 | 1.0 | True | None |
| 67 | 4 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 68 | 1 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 69 | 4 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 70 | 4 | 0 | 0 | 0 | 0 | 0.0 | True | None |
| 71 | 4 | 1 | 1 | 1 | 1 | 1.0 | True | None |
| 72 | 4 | 1 | 1 | 1 | 1 | 1.0 | True | None |
| 73 | 4 | 0 | 0 | 0 | 0 | 0.0 | True | None |

| Structure-gate phase | Passed | Failed |
|---|---|---|
| initial | 49 | 1 |
| corrected | 0 | 1 |

A flat inference batch may be retained only with its failed structure gate and flat_after_one_correction disclosure. Nonflat endpoint mismatches are refused. All-atomic batches without a selected inference can pass the gate; the separate all-atomic inventory above keeps that distinction visible. Source conditionals do not themselves license engine moves.


## Construction windows, coverage and omitted support

The saved live plan has 74 windows, initially two commitments per window, a per-window cap of four, and a projected 148 commitments. The global 152-slot figure is allocation arithmetic, not a hard final-count cap; exact native output and context checks govern admission. Larger mandatory source bundles can be skipped or trimmed only under the logged native policy.

| Window | Papers | Accepted | Commitments | Roots | Uncut items | Retained items | Cut depth | Omitted | Reason |
|---|---|---|---|---|---|---|---|---|---|
| 0 | beddorgoldstein2021 | False | 0 | 2 | 2 | 2 | None | 82 | candidate cannot support targeted construction correction |
| 1 | beddorgoldstein2021, bledin2014 | True | 4 | 2 | 16 | 4 | 0 | 79 | None |
| 2 | bledin2014, braun2012 | False | 0 | 3 | 61 | 0 | -1 | 112 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 3 | braun2012 | False | 0 | 1 | 12 | 0 | -1 | 42 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 4 | braun2012, egan2007 | True | 4 | 2 | 4 | 4 | None | 38 | None |
| 5 | egan2007 | True | 4 | 1 | 9 | 4 | 0 | 78 | None |
| 6 | egan2007, eganhawthorneweatherson2005 | True | 4 | 4 | 118 | 4 | 0 | 165 | None |
| 7 | eganhawthorneweatherson2005 | True | 2 | 2 | 27 | 2 | 0 | 83 | None |
| 8 | eganhawthorneweatherson2005, eganweatherson2011 | False | 0 | 1 | 81 | 0 | -1 | 130 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 9 | eganweatherson2011 | True | 2 | 2 | 2 | 2 | None | 80 | None |
| 10 | eganweatherson2011, gsv1996 | False | 0 | 4 | 15 | 0 | -1 | 83 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 11 | gsv1996 | True | 2 | 2 | 2 | 2 | None | 81 | None |
| 12 | gsv1996 | False | 0 | 2 | 17 | 0 | -1 | 83 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 13 | gsv1996, hawkesteinertthrelkeld2021 | False | 0 | 3 | 18 | 0 | -1 | 82 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 14 | hawkesteinertthrelkeld2021 | True | 4 | 1 | 48 | 4 | 1 | 85 | None |
| 15 | hawkesteinertthrelkeld2021, hollidaymandelkern2024 | True | 4 | 2 | 47 | 4 | 0 | 91 | None |
| 16 | hollidaymandelkern2024 | True | 3 | 3 | 3 | 3 | None | 80 | None |
| 17 | hollidaymandelkern2024 | False | 0 | 3 | 20 | 0 | -1 | 82 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 18 | hollidaymandelkern2024 | True | 4 | 2 | 4 | 4 | None | 80 | None |
| 19 | hollidaymandelkern2024 | True | 4 | 2 | 4 | 4 | None | 80 | None |
| 20 | hollidaymandelkern2024, klinedinstrothschild2012 | False | 0 | 1 | 6 | 0 | -1 | 83 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 21 | klinedinstrothschild2012 | False | 0 | 2 | 18 | 0 | -1 | 89 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 22 | klinedinstrothschild2012, knobeyalcin2014 | False | 0 | 1 | 10 | 0 | -1 | 85 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 23 | knobeyalcin2014, kolodnymacfarlane2010 | True | 2 | 1 | 35 | 2 | 0 | 89 | None |
| 24 | kolodnymacfarlane2010, macfarlane2011 | True | 4 | 1 | 4 | 4 | None | 79 | None |
| 25 | macfarlane2011 | True | 4 | 2 | 41 | 4 | 0 | 95 | None |
| 26 | macfarlane2011, macfarlane2014 | True | 2 | 1 | 85 | 2 | 0 | 152 | None |
| 27 | macfarlane2014 | True | 3 | 2 | 3 | 3 | None | 80 | None |
| 28 | macfarlane2014 | True | 1 | 1 | 18 | 1 | 0 | 82 | None |
| 29 | macfarlane2014 | True | 4 | 1 | 4 | 4 | None | 78 | None |
| 30 | macfarlane2014 | False | 0 | 2 | 8 | 0 | -1 | 83 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 31 | macfarlane2014 | True | 1 | 1 | 13 | 1 | 0 | 87 | None |
| 32 | macfarlane2014 | False | 0 | 2 | 15 | 0 | -1 | 89 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 33 | macfarlane2014 | False | 0 | 0 | 0 | 0 | None | 82 | This window concerns MacFarlane’s treatment of taste predicates, disagreement, and related belief ascriptions; it contains no directly relevant argument about epistemic modals, so no roots are selected. |
| 34 | macfarlane2014 | False | 0 | 0 | 0 | 0 | None | 83 | This window addresses taste relativism and expressivism, plus contextualism and invariantism about knowledge ascriptions. Those topics do not directly bear on the semantics or logic of epistemic modals, so no roots are selected. |
| 35 | macfarlane2014 | False | 0 | 1 | 21 | 0 | -1 | 90 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 36 | macfarlane2014 | True | 2 | 1 | 23 | 2 | 0 | 81 | None |
| 37 | macfarlane2014 | False | 0 | 0 | 0 | 0 | None | 82 | This window discusses theories of future contingents, assessment sensitivity, and assertion rather than epistemic modals. Its arguments do not materially bear on the requested topic, so no roots are selected. |
| 38 | macfarlane2014 | True | 4 | 3 | 15 | 4 | 0 | 79 | None |
| 39 | macfarlane2014 | True | 4 | 1 | 4 | 4 | None | 79 | None |
| 40 | macfarlane2014 | True | 4 | 1 | 4 | 4 | None | 79 | None |
| 41 | macfarlane2014 | True | 4 | 1 | 4 | 4 | None | 78 | None |
| 42 | macfarlane2014 | True | 4 | 2 | 4 | 4 | None | 37 | None |
| 43 | macfarlane2014, moss2015 | False | 0 | 3 | 24 | 0 | -1 | 62 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 44 | moss2015 | False | 0 | 1 | 6 | 0 | -1 | 43 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 45 | moss2015 | False | 0 | 4 | 35 | 0 | -1 | 62 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 46 | moss2015 | True | 2 | 2 | 24 | 2 | 0 | 55 | None |
| 47 | moss2015 | False | 0 | 1 | 4 | 4 | None | 42 | non-flat inference structure contract failed after correction |
| 48 | moss2015, ninan2018 | True | 4 | 2 | 4 | 4 | None | 38 | None |
| 49 | ninan2018 | False | 0 | 4 | 21 | 0 | -1 | 47 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 50 | ninan2018 | True | 2 | 1 | 26 | 2 | 0 | 82 | None |
| 51 | ninan2018, rothschild2012 | False | 0 | 2 | 47 | 0 | -1 | 114 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 52 | rothschild2012, schaffer2011 | True | 1 | 1 | 59 | 1 | 0 | 90 | None |
| 53 | schaffer2011 | False | 0 | 1 | 8 | 0 | -1 | 48 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 54 | schaffer2011 | True | 4 | 4 | 4 | 4 | None | 37 | None |
| 55 | schaffer2011, veltman1996 | True | 3 | 2 | 15 | 3 | 0 | 81 | None |
| 56 | veltman1996 | True | 4 | 3 | 4 | 4 | None | 80 | None |
| 57 | veltman1996 | True | 1 | 1 | 8 | 1 | 0 | 82 | None |
| 58 | veltman1996, vonfintelgillies2007 | True | 2 | 2 | 6 | 2 | 0 | 41 | None |
| 59 | vonfintelgillies2007 | True | 4 | 4 | 4 | 4 | None | 37 | None |
| 60 | vonfintelgillies2007 | True | 4 | 1 | 4 | 4 | None | 38 | None |
| 61 | vonfintelgillies2011 | True | 4 | 1 | 4 | 4 | None | 38 | None |
| 62 | vonfintelgillies2011 | True | 1 | 1 | 36 | 1 | 0 | 71 | None |
| 63 | vonfintelgillies2011 | True | 4 | 2 | 4 | 4 | None | 38 | None |
| 64 | vonfintelgillies2011, willer2013 | True | 4 | 2 | 4 | 4 | None | 80 | None |
| 65 | willer2013 | True | 4 | 1 | 4 | 4 | None | 78 | None |
| 66 | willer2013, wright2007 | False | 0 | 2 | 65 | 0 | -1 | 132 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 67 | wright2007, yalcin2007 | True | 4 | 4 | 7 | 4 | 0 | 79 | None |
| 68 | yalcin2007 | True | 1 | 1 | 19 | 1 | 0 | 83 | None |
| 69 | yalcin2007, yalcin2011 | True | 4 | 4 | 4 | 4 | None | 78 | None |
| 70 | yalcin2011, yalcin2015 | True | 4 | 2 | 4 | 4 | None | 37 | None |
| 71 | yalcin2015 | True | 4 | 1 | 4 | 4 | None | 38 | None |
| 72 | yalcin2015 | True | 4 | 1 | 4 | 4 | None | 79 | None |
| 73 | yalcin2015 | True | 4 | 3 | 17 | 4 | 0 | 79 | None |

26 frozen commitments retain explicit support_omitted assumptions. They are not proven by construction. Exact cut disclosures, window budgets, skips and calibration observations are in pilot-audit.json. Paper coverage is not full extraction; all historical source, OCR, quarantine, text-fidelity and unknown-usage limitations remain in the lineage and prior handoffs.


## Vocabulary preflight per target

| Attempt | Status | Disconnected targets | Catalogue status |
|---|---|---|---|
| 1 | aligned | [] | verified |

| Target | Final preflight | Shared signatures | Target signatures | Overlap |
|---|---|---|---|---|
| candidate_01 | aligned | 1 | 1 | 100.00% |
| candidate_02 | aligned | 1 | 1 | 100.00% |
| candidate_03 | aligned | 1 | 1 | 100.00% |
| candidate_04 | aligned | 1 | 1 | 100.00% |
| candidate_05 | aligned | 1 | 1 | 100.00% |
| candidate_06 | aligned | 1 | 1 | 100.00% |
| candidate_07 | aligned | 1 | 1 | 100.00% |
| candidate_08 | aligned | 1 | 1 | 100.00% |
| candidate_09 | aligned | 1 | 1 | 100.00% |
| candidate_10 | aligned | 1 | 1 | 100.00% |

Overlap requires exact name/kind/arity identity, including constants. Nonzero overlap does not prove entailment or faithful alignment. The native preflight permits one bounded target correction; a second disconnected result remains disclosed and searchable.


## Search proposals, admissions and closures

| Target | Polarity | Nodes | Proof depth | Expansions | Proposals | Admitted | CLOSED routes | Outcomes | Complete/authenticated | Prune reasons |
|---|---|---|---|---|---|---|---|---|---|---|
| candidate_01 | target | 1 | 0 | 0 | 0 | 0 | 1 | {'CLOSED': 1} | True/True | {} |
| candidate_01 | negation | 1 | 0 | 1 | 1 | 0 | 0 | {'OPEN': 1} | True/True | {'INVALID_SCOPE': 1} |
| candidate_02 | target | 1 | 0 | 0 | 0 | 0 | 1 | {'CLOSED': 1} | True/True | {} |
| candidate_02 | negation | 1 | 0 | 1 | 1 | 0 | 0 | {'OPEN': 1} | True/True | {'INVALID_SCOPE': 1} |
| candidate_03 | target | 1 | 0 | 0 | 0 | 0 | 1 | {'CLOSED': 1} | True/True | {} |
| candidate_03 | negation | 16 | 6 | 9 | 9 | 7 | 0 | {'OPEN': 1} | True/True | {'INVALID_SCOPE': 1, 'SCHEMA_MISMATCH': 1} |
| candidate_04 | target | 1 | 0 | 0 | 0 | 0 | 1 | {'CLOSED': 1} | True/True | {} |
| candidate_04 | negation | 4 | 1 | 1 | 1 | 1 | 0 | {'OPEN': 1} | True/True | {} |
| candidate_05 | target | 1 | 0 | 0 | 0 | 0 | 1 | {'CLOSED': 1} | True/True | {} |
| candidate_05 | negation | 1 | 0 | 1 | 1 | 0 | 0 | {'OPEN': 1} | True/True | {'INVALID_SCOPE': 1} |
| candidate_06 | target | 1 | 0 | 0 | 0 | 0 | 1 | {'CLOSED': 1} | True/True | {} |
| candidate_06 | negation | 2 | 1 | 1 | 1 | 1 | 0 | {'OPEN': 1} | True/True | {} |
| candidate_07 | target | 1 | 0 | 0 | 0 | 0 | 1 | {'CLOSED': 1} | True/True | {} |
| candidate_07 | negation | 1 | 0 | 1 | 1 | 0 | 0 | {'OPEN': 1} | True/True | {'INVALID_SCOPE': 1} |
| candidate_08 | target | 1 | 0 | 0 | 0 | 0 | 1 | {'CLOSED': 1} | True/True | {} |
| candidate_08 | negation | 1 | 0 | 1 | 1 | 0 | 0 | {'OPEN': 1} | True/True | {'INVALID_SCOPE': 1} |
| candidate_09 | target | 1 | 0 | 0 | 0 | 0 | 1 | {'CLOSED': 1} | True/True | {} |
| candidate_09 | negation | 26 | 6 | 16 | 18 | 14 | 0 | {'OPEN': 2} | True/True | {'INVALID_SCOPE': 3, 'SCHEMA_MISMATCH': 1} |
| candidate_10 | target | 1 | 0 | 0 | 0 | 0 | 1 | {'CLOSED': 1} | True/True | {} |
| candidate_10 | negation | 1 | 0 | 1 | 1 | 0 | 0 | {'OPEN': 1} | True/True | {'INVALID_SCOPE': 1} |

Depth is proof-node depth, not report state ancestry. Proposal counts come from recorded engine proposal receipts; admitted proposals are inference transitions. Search completion does not mean closure. CLOSED means closed relative to formalized T, bank-licensed steps and the implemented checks; it does not establish true premises or faithful source interpretation. Unsealed historical/failed attempts are not completed searches.

Among CLOSED routes, 0 contain an inference and 10 close without an inference. 6 OPEN routes contain only a target leaf. This distinguishes direct closure against frozen T from a derived route.

Current route status counts: {"CLOSED": 10, "OPEN": 11}. Search phase: complete. Full failures, retries and partial traces remain in the audit.


## Model-written route summaries

Each route description is generated separately through isolated codex_cli, then locally validated and bound to its recorded graph hash. Requested model gpt-6-luna; serving identity unverified. The reporting-only schema is additional to the native 15-case schema preflight. These are model-written descriptions, not independent semantic verification, rankings or selections. Open premises, polarity and evidence fidelity require inspection.

| Route | Target | Polarity | Status | Model-written summary |
|---|---|---|---|---|
| 3a1a7becdcce:r0 | candidate_01 | target | CLOSED | Target polarity: support. The sole recorded step is a leaf asserting the attributed Andy Egan thesis; it matches the target directly. Its frozen commitment says there are good reasons to adopt a relativist semantics for epistemic-modal claims, with truth values determined relative to something finer-grained than a world or world-time pair. The route is CLOSED with no frontier or blockers, relative to the supplied commitment and licensed steps. No omitted-support assumption is stated. This closure does not establish the commitment’s truth or the fidelity of its formalization. |
| 4383fdce848a:r0 | candidate_01 | negation | OPEN | Targets the negation of candidate_01: it opposes the attributed claim that there are good reasons to adopt Egan’s relativist semantics for epistemic modals. The route records only an open leaf asserting that negation; there are no supporting steps or frozen commitments, and its frontier remains n0. Thus the route is OPEN, with no support established here for the negative target. |
| cc6290b3605e:r0 | candidate_02 | target | CLOSED | Target polarity: supports the attributed conclusion that epistemic modals are assessment-sensitive, and that assessment-sensitive truth-conditional semantics can meet objections to contextualism and undermine the case for expressivism. The graph contains only a leaf stating this conclusion; it records no inferential steps. Its sole frozen commitment is marked as an assumed premise and explicitly omits support `macfarlane2011:r1-22:inf_main`. The route is CLOSED relative to the supplied commitments and licensed steps, with no frontier shown; this does not establish the premise’s truth or faithful formalization, and the omitted support remains unrepresented. |
| f1720d70ed0b:r0 | candidate_02 | negation | OPEN | This OPEN route targets the negation of candidate_02’s attributed conclusion about assessment-sensitive epistemic modals and truth-conditional semantics. Its only recorded node is the open negated-target leaf n0; no steps support the target. No frozen commitments are supplied, and the target remains open. |
| 3071d8cb195f:r0 | candidate_03 | target | CLOSED | Target-polarity route for the attributed conclusion that relativism is Egan, Hawthorne, and Weatherson’s best option for epistemic modals. The graph contains only the target leaf, with no recorded inferential steps; a frozen author-claim commitment directly states it. That commitment is marked as an assumed premise with support omitted: inf_g42_final and n_inf_rel. The route is CLOSED only relative to the supplied commitments and licensed steps; the omitted support remains unshown, and closure establishes neither the claim’s truth nor faithful formalization. |
| 329b8f992046:r0 | candidate_03 | negation | OPEN | Targets the negation of candidate_03’s attributed conclusion that Egan, Hawthorne, and Weatherson’s best option is relativism about epistemic modals. The reductio assumes that conclusion and uses the frozen Egan 2007 commitment—that there are good reasons to adopt a relativist semantics for epistemic modal claims—as a positive result. It then tries to derive the negation of that commitment through modus tollens and further placeholder steps, but those require open conditionals and premises (including open_auxiliary, open_p, and P). The commitment supports relativism generally, not the attributed best-option claim, and its text does not state an omitted-support assumption. The route is OPEN: the required negative result is not established, and frontier leaves remain open. |
| 38a0e7186914:r0 | candidate_04 | target | CLOSED | Target polarity: support the attributed claim that Hawke and Steinert-Threlkeld’s semantic expressivism uses a partial interpretation from information states to truth-values, satisfies the stated constraints, and is logically conservative. The sole recorded step is a leaf matching the target, licensed by the frozen author-claim commitment: the interpretation is partial, permitting acceptance, rejection, or neutrality, and the authors say they prove the constraints are met conservatively, with non-classical behavior arising from connectives interacting with modals. The route is CLOSED relative to this commitment and licensed step; no omitted-support assumption is stated. This does not establish the commitment’s truth or faithful formalization. |
| a8e41ddc6cd1:r0 | candidate_04 | negation | OPEN | Targets the negation of candidate_04’s attributed claim that Hawke and Steinert-Threlkeld’s semantic expressivism uses a partial interpretation, satisfies the stated constraints, and is logically conservative. The recorded reductio-shaped inference cites an assumption of a novel semantic expressivism satisfying Sect. 3.5 and both the claim that the assumption holds and that it does not. These are open assumptions, not established results; the negative-result leaf n3 remains the frontier. No frozen commitments are used, and the route is OPEN: it establishes neither a contradiction nor the target negation. |
| f6a8a77d1114:r0 | candidate_05 | target | CLOSED | Target polarity: support. The route has one leaf directly matching the target, backed by the frozen author-claim commitment c_abstract_program: it attributes to Holliday and Mandelkern the claims about genuine epistemic contradictions, failures of distributivity and disjunctive syllogism, preservation of other classical laws, and equivalent algebraic and possibility-based formulations. No inferential steps or omitted-support assumptions are recorded. CLOSED relative to this supplied commitment and licensed steps only; it does not establish the claim’s truth or faithful formalization. |
| c0d316b8799b:r0 | candidate_05 | negation | OPEN | This open negation route opposes candidate_05: the attributed claim that Holliday and Mandelkern’s semantics treats epistemic contradictions as genuine contradictions, invalidates distributivity and disjunctive syllogism while preserving other classical laws, and has equivalent algebraic and possibility-based formulations. Its only recorded node is the negation of that target; there are no recorded steps or frozen supporting commitments. The route remains open and provides no support for its opposition. |
| 3b8e84f6819a:r0 | candidate_06 | target | CLOSED | Target-polarity route for candidate_06: its sole recorded leaf directly states the attributed Yalcin author claim, matching the target; no inferential steps are recorded. It uses the frozen commitment yalcin2011:union:item:yalcin2011:salvage:a4495e98c6f03052:yalcin2011:r1-19:n56, which characterizes epistemic possibility as expressing compatibility with one's state of mind to coordinate interlocutors, rather than asserting a fact about the world. The graph is CLOSED with no frontier or blocked steps, relative only to the supplied formalized commitment and licensed steps; this does not establish the claim's truth or faithful formalization. No omitted-support assumption is stated. |
| 7a56c05426f0:r0 | candidate_06 | negation | OPEN | Targets the negation of candidate_06: the attributed Yalcin claim that epistemic-possibility talk expresses compatibility with one’s state of mind and coordinates interlocutors, rather than asserting a fact about the world. Its sole recorded step applies double-negation reasoning from the open premise ¬¬¬claim to ¬claim. No frozen commitments are supplied or used. The route is OPEN: the triple-negated premise remains unresolved at frontier n1, so the negative target is not established. |
| 5a877cece423:r0 | candidate_07 | target | CLOSED | Target polarity: supports the attributed claim that Schaffer’s defended meaning-perspectivalism is contextualist, with epistemic-modal sentences expressing different propositions across contexts as perspectives vary. The sole recorded leaf directly matches the target and is backed by the frozen author-claim commitment; there are no intermediate steps or other commitments. The route is CLOSED relative to the supplied commitment and licensed steps, not proof of the commitment’s truth or faithful formalization. No omitted-support assumption is stated; nothing remains open or blocked within this route. |
| d4126b07a5e8:r0 | candidate_07 | negation | OPEN | This OPEN route targets the negation of candidate_07: that Schaffer’s defended meaning-perspectivalist view is not contextualist, or that epistemic-modal sentences do not express different propositions across varying perspectives. Its sole recorded node is an open leaf; no steps or frozen commitments support the negation. The target remains unargued and open. |
| bd7c84a0da2a:r0 | candidate_08 | target | CLOSED | Target polarity: supports candidate_08, the attributed intermediate conclusion that a bare epistemic modal quantifies over a group’s information, but it is indeterminate which group or aggregated information state. The route consists of a single leaf asserting that conclusion, matching the frozen author_claim commitment from von Fintel and Gillies (citation: vonfintelgillies2011:pdf:2#...). No further inferential steps are recorded. It is CLOSED relative to the supplied commitment and licensed steps; this does not establish the commitment’s truth or faithful formalization. No omitted-support assumption is stated. Nothing remains open or blocked within the graph. |
| 341c76e6bf75:r0 | candidate_08 | negation | OPEN | This negation-polarity route targets the claim that von Fintel and Gillies attribute indeterminacy about which group or aggregated information state bare epistemic modals quantify over, while holding that they quantify over a group’s information. Its sole recorded node is an open leaf containing the negated target; there are no supporting steps or frozen commitments. The route remains open and does not establish the negation. |
| 28ef48e1f386:r0 | candidate_09 | target | CLOSED | Target polarity: support. The route is CLOSED relative to the supplied formalized commitments and licensed steps: its sole leaf directly states the target claim, attributed to Seth Yalcin. The frozen commitment says quantifying into modal contexts is not to be feared, while epistemic modality interacts distinctively with quantifiers and descriptions; it says de re puzzles motivated dynamic compositional-semantic solutions. No omitted-support assumption is stated. Closure does not establish the claim’s truth or the faithfulness of its formalization. |
| e31c4cc240f1:r0 | candidate_09 | negation | OPEN | Targets the negation of candidate_09: that Yalcin’s attributed claim about epistemic modality, quantifiers/descriptions, and dynamic compositional semantics is false. The route attempts modus tollens from the target-to-Q conditional and not-Q; it derives not-Q by another modus tollens from Q→R and not-R, while conditional proof, modus ponens, hypothetical syllogism, and double negation are used in the subproof. But the needed conditionals and not-R/double-negation premise remain open, as do the P/Q/R placeholder steps. No frozen supporting commitments are supplied. The route is OPEN, so the negated target remains unsupported and blocked relative to the recorded steps. |
| e31c4cc240f1:r1 | candidate_09 | negation | OPEN | Targets the negation of candidate_09: the attributed claim that epistemic modality interacts distinctively with quantifiers and descriptions, with de re puzzles addressed through dynamic compositional semantics. The recorded route attempts modus tollens from claim → Q and ¬Q; it derives Q → R by hypothetical syllogism from Q → S and S → R, then purports to derive ¬Q from ¬R. The S → R conditional-proof branch further uses P → R and ¬¬P to reach R. The route is OPEN, not closed: all leaves are unresolved, and no frozen supporting commitments were supplied. Q, R, S and P are abstract propositions here; the recorded step from ¬¬R to ¬R does not follow from the displayed formula. No omitted-support assumptions are stated in supporting commitment text. |
| 5e790ba3299d:r0 | candidate_10 | target | CLOSED | Target-polarity route for candidate_10: its sole recorded leaf is the attributed intermediate conclusion that Willer’s dynamic framework adequately captures the intuition that epistemic might-statements are informative. It uses the frozen author-claim commitment on p. 22, which qualifies the claim: “Insofar as we have any intuition that might is informative.” There are no supporting steps or open frontier. CLOSED means only that the route is closed relative to the supplied commitments and licensed steps; it does not establish the commitment’s truth or faithful formalization. |
| 2218cc68bbf6:r0 | candidate_10 | negation | OPEN | This OPEN route has negation polarity toward candidate_10: it presents the negation of the attributed intermediate conclusion that Willer’s dynamic framework adequately captures the intuition that epistemic might-statements are informative. Its only recorded node is an open leaf (n0); there are no steps or supporting commitments. The target remains unsupported and unresolved. |

**Concrete text/formula mismatch found during summary review:** Review observation: route e31c4cc240f1:r1 (candidate_09 negation), premise n10 says “It is not the case that Proposition R is not true.” (double negation), but its stored AST is triple negation of R. The stored triple-negation formula licenses double-negation elimination to not-R at n4; the prose premise would not. The model summary’s claim that the step does not follow from the displayed formula conflates this prose/formula mismatch with formal validity. The route remains OPEN. This is a concrete formalization-fidelity issue, not a closed proof or evidence that the stored formal step is invalid. Raw route and model-written summary are preserved; this observation is not an exhaustive semantic audit.

Exact node formulas and original model wording are preserved in [summary-review.json](/home/dev/ara-work/reports/overnight/codex3/summary-review.json).


## Usage, refusals and timing

| Scope | MODEL receipts | Recorded tokens | API USD | Unknown-usage calls |
|---|---|---|---|---|
| Pilot including summaries | 274 | 8965989 | 0.0 | 1 |
| Standalone canary | 1 | 5495 | 0.0 | 0 |
| Fresh schema proof | 17 | 80914 | 0.0 | 0 |
| This task total | 292 | 9052398 | 0.0 | 1 |
| Imported extraction (historical) | 277 | 11348025 | 110.395145 | 2 |

Subscription USD equivalent is unavailable; zero new API USD is not a measured zero subscription cost. Cached tokens are counted once. Pending/unknown usage remains charged under native reservation policy. Imported extraction is reported separately from the local 100M subscription cap. The CLI has no hard output-token flag; native admission reserves output and checks actual receipts.

Subscription limit events: 0; active limit duration at final check: 0 seconds. The watchdog is configured to halt after two hours of a persistent limit. Unsettled calls: 0; reserved unsettled tokens: 0.

| Timestamp | Stage | Reason/status |
|---|---|---|
| 2026-10-26T19:06:05.506755+00:00 | provider_error | {'error_type': 'cli_timeout'} |
| 2026-10-26T19:06:08.992574+00:00 | build_t_batch | {'reason': 'CodexCLIError', 'status': 'incomplete'} |
| 2026-10-26T19:06:12.285294+00:00 | provider_retry | {'reason': 'cli_timeout'} |
| 2026-10-26T19:07:05.147635+00:00 | build_t_batch | {'reason': 'ValidationError at /commitments/2/formula/args: minItems constraint failed', 'status': 'rejected'} |
| 2026-10-26T20:13:02.959748+00:00 | select_t_roots | {'reason': 'working T evidence inventory mismatch', 'status': 'rejected'} |

| Interval | Seconds |
|---|---|
| startup_and_plan | 1556.577399 |
| construction_after_plan | 9446.202567 |
| construction_until_interruption | None |
| target_proposal | 43.220027 |
| search_publication | 712.196792 |
| search_through_saved_analyses | 3493.632602 |
| route_summaries | 823.30592 |

Native initial run exit/timing: {"phase": "pilot", "exit_code": 0, "started_epoch": 1793039541.568018, "ended_epoch": 1793054187.2910516, "wall_seconds": 14645.723034381866}. Summed call times and concurrent wall times are distinct.


## Report verification and preservation

Native report covers 43 lineage inputs. Copied 35,637 files / 3,864,345,495 bytes, including report.html, report.md, data.json and all linked sidecars, with matching SHA-256 hashes. Reconstructed 101,323 event occurrences / 32,597 unique bodies and verified 1,191 artifact copies. Source logs and anchors were unchanged during generation.

HTML: 1,134,797 bytes (1.134797 decimal MB). Opened the delivered path in Chromium 143.0.7499.4; 3,717 links/anchors checked, no missing anchors or page errors. Desktop viewport/document widths: 1440/1440; mobile: 390/409. Native mobile overflow is 19 pixels and remains disclosed.

Expanded tree browser evidence: {"passed": true, "scope": "Current Codex pilot 3 authenticated trace", "current_pilot_search_details": 31, "expanded_search": "Search e31c4cc240f1:1", "run_index": 42, "proof_nodes": 26, "state_depth": 13, "proof_depth": 6, "linked_files": [{"path": "trees/run-42-search-17.json", "bytes": 152755}, {"path": "trees/run-42-search-17.dot", "bytes": 2129}], "linked_json_opened": true, "dot_valid_header": true, "tree_keys": ["begin_seq", "version", "search_id", "target", "states", "receipts", "decisions", "complete", "authenticated", "source", "issues", "completed_routes", "nodes"], "screenshot": "/home/dev/ara-scaffold/runs/codex-pilot-3-control/report-expanded-current-tree.png", "svg_available": false}. Full search.json files retain data beyond bounded HTML previews.

The model-summary companion page passed browser checks at desktop and mobile widths; all 21 summary cards and their links are present, with no page errors or horizontal overflow. Original long identifiers are preserved and wrap on narrow screens. {"passed": true, "articles": 21, "errors": [], "missing": [], "desktop": {"width": 1440, "scrollWidth": 1440}, "mobile": {"width": 390, "scrollWidth": 390}, "browser": "143.0.7499.4"}

The previous pilot-2 artifacts and named handoffs match their pre-run hashes. Source remains clean at the pinned revision. To make disk space, four regenerable local report duplicates were removed only after every source/delivered file matched its recorded hash. All delivered reports and all original run evidence remain. Cleanup receipts are retained in the control folder.


## Finding placement and next step

| Finding | Placement |
|---|---|
| 1 | Opening: final state and no selection |
| 2 | Methodology: exact revision, review limits, provider/auth/config and fresh schema proof |
| 3 | Frozen T: non-atomic structure, conditionals, symbol reuse, catalogue and flatness |
| 4 | Construction windows: coverage, omissions, skips and source limits |
| 5 | Vocabulary preflight: per-target alignment and bounded correction limits |
| 6 | Searches: proposals, admissions, depth, closure and proof limits |
| 7 | Model-written summaries: graph-bound descriptions and semantic limits |
| 8 | Usage: tokens, unknowns, refusals, limits and timing |
| 9 | Report verification: lineage, hashes, browser/tree checks and rendering limits |
| 10 | Preservation: previous handoffs, original artifacts, duplicate cleanup and clean source |
| 11 | Model-written summaries: concrete candidate_09 n10 prose/formula mismatch and correction of the summary’s formal-validity claim |

11 findings, 11 placed.

Operator selection is a separate future action. No route was selected and no essay was composed.

DONE zeta codex-pilot-3 commitments=157 papers_in_T=21/26 nonatomic_pct=10.19 targets=10 searches_ok=20/20 routes=21 closed_routes=10 status=awaiting-selection report=/home/dev/ara-work/reports/overnight/codex3/report.html
