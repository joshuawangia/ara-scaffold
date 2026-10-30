# Zeta Codex pilot 2

**blocked:local-validation-stall.** 166 frozen commitments from 24/26 papers; 10 targets; 19/20 completed searches; 0 published routes. Native exit -15. No route selected.

[Open the full-lineage report](/home/dev/ara-work/reports/overnight/codex2/report.html). [Structured run audit](/home/dev/ara-scaffold/runs/codex-pilot-2-control/pilot-audit.json). Prior Codex handoff preserved as [zeta-codex-pilot-1.md](/home/dev/ara-work/reports/zeta-codex-pilot-1.md).

The pilot did not reach awaiting_selection. Zeta halted it as an operational safeguard after the final search became CPU-bound in local JSON Schema validation. This was an agent-initiated halt, not an operator-requested halt or a subscription limit. The supervisor forwarded SIGINT, then SIGTERM after its one-second grace period; native exit was -15. Nineteen searches completed in verified journals, but their publication into the canonical main log had not finished. No route or route summary was published, and no route was selected.

## Methodology and configuration

Extraction: imported Opus 5 results produced via the Anthropic API. Construction and search are configured to request gpt-6-luna through isolated Codex CLI calls using the ChatGPT subscription. Serving model identity is unverified; the requested model flag is not a serving receipt. No new extraction, Claude subscription call, API call, route selection or essay composition was authorized or performed by this pilot.

Clean requested revision: `8aa265fa32b97bdbae662108ba080950c5c73034`. Tau2 approved the strict-schema projection and mandatory native stage preflight with zero blocking findings. The merged local OCR implementation is unused because the literature is unchanged. Omega Round 13 and Tau2’s projection follow-up were read. Their tests are reviewer evidence, not tests rerun by this pilot. The existing literature artifact remains SHA-256 `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`. New OCR repairs were not incorporated.

Config: `runs/inputs/codex-pilot-config.yaml`, the same file used for Codex pilot 1. The only added setting is `codex_cli.schema_preflight_log`, binding this run’s successful live stage proof. Provider/model remain `codex_cli` / `gpt-6-luna`, with no fallback. All schema/stage routing was checked before canary execution. Auth source is exclusively `/home/dev/.config/ara/codex-home/auth.json`; no worker-home auth fallback. Local cap 100,000,000 tokens; catalogue 60,000 tokens; 233 symbol-growth tokens per item; window cap multiplier 2; search/provider concurrency 4; empty audience.

The standalone native canary passed before the pilot; native startup canaries remain logged. Generic built-in tool definitions may be visible and are disclosed; any executed tool or unknown event rejects. Skills, memory and operator instruction content must be absent. Credentials are mounted read-only per call; refresh is disabled. These checks do not establish byte-identical API context or model quality.

The mandatory native Codex stage preflight ran first and passed 14/14 cases. Its 16 measured, uncached calls include 2 required isolation canaries; usage was 74,846 tokens. The production admission gate verified the actual event chain, checkpoint and matching manifest. A separate standalone canary followed, then the fresh pilot.

The versioned ARA→OpenAI-strict projection changes only the wire grammar. Original schema constraints and caller checks remain authoritative after normalization. This preflight proves placeholder grammar/local-validation acceptance for 12 native schemas and 14 stage/correction cases; it does not prove semantic quality, a full pilot, or web retrieval. API-only extraction and schema-less web retrieval are excluded; neither is invoked here.

Visible definitions in the executed standalone canary: collaboration.followup_task, collaboration.interrupt_agent, collaboration.list_agents, collaboration.send_message, collaboration.spawn_agent, collaboration.wait_agent, functions.apply_patch, functions.clock__curr_time, functions.exec, functions.list_mcp_resource_templates, functions.list_mcp_resources, functions.read_mcp_resource, functions.wait. Recorded tool events: 0; forbidden-term checks: 51.

The live plan contains 74 funded windows, compared with 69 in Tau2's Round-13 offline review. Native allocation: 152 global slots, 148 projected commitments, 4 maximum commitments per window. This is an initial allocation, not a hard total-commitment cap or a prediction of accepted output. Native admission recalculates remaining working-context and catalogue token headroom for each window while preserving the four-commitment window cap. Accepted totals can exceed the initial slot estimate.

The first live canary measured 4327 input tokens against an initial-context estimate of 1488; native runtime overhead rose from 949 to 3978 tokens. Native planning used this updated live estimate. Requested caps were retained; no offline plan was substituted for live admission.

## Frozen T and construction

Freeze count 1; path `/home/dev/ara-scaffold/runs/codex-pilot-2/commitments.json`; SHA-256 `0f643d95f26a7847654fd29ea095e2fc3af5a1750b165b9fd758c30f9599ba4b`.
All 74 windows were processed: 53 accepted, 18 skipped for mandatory-context/capacity bounds and three skipped by model relevance decisions. The frozen T contains no commitments from rothschild2012 or kolodnymacfarlane2010. The per-paper table below records the exact coverage.

| Paper | Frozen commitments |
|---|---|
| vonfintelgillies2007 | 7 |
| eganweatherson2011 | 5 |
| vonfintelgillies2011 | 5 |
| wright2007 | 5 |
| schaffer2011 | 6 |
| braun2012 | 6 |
| eganhawthorneweatherson2005 | 4 |
| egan2007 | 5 |
| macfarlane2011 | 4 |
| yalcin2007 | 9 |
| yalcin2011 | 5 |
| rothschild2012 | 0 |
| moss2015 | 17 |
| hawkesteinertthrelkeld2021 | 5 |
| veltman1996 | 4 |
| gsv1996 | 1 |
| willer2013 | 7 |
| ninan2018 | 12 |
| beddorgoldstein2021 | 7 |
| hollidaymandelkern2024 | 16 |
| kolodnymacfarlane2010 | 0 |
| knobeyalcin2014 | 2 |
| klinedinstrothschild2012 | 1 |
| bledin2014 | 1 |
| yalcin2015 | 1 |
| macfarlane2014 | 31 |

| Kind | Frozen commitments |
|---|---|
| conclusion | 42 |
| attacked_view | 9 |
| qualification | 25 |
| intermediate_conclusion | 35 |
| distinction | 8 |
| inference | 18 |
| premise | 24 |
| reported_view | 5 |

Window indices are zero-based. Retained closure items in a skipped window did not enter T.

| Window | Papers | Roots | Uncut | Retained | Accepted commitments | Outcome/reason |
|---|---|---|---|---|---|---|
| 0 | beddorgoldstein2021 | 4 | 4 | 4 | 4 | accepted |
| 1 | beddorgoldstein2021, bledin2014 | 1 | 15 | 3 | 3 | accepted |
| 2 | bledin2014, braun2012 | 3 | 39 | 3 | 3 | accepted |
| 3 | braun2012 | 2 | 4 | 4 | 4 | accepted |
| 4 | braun2012, egan2007 | 3 | 6 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 5 | egan2007 | 1 | 9 | 4 | 4 | accepted |
| 6 | egan2007, eganhawthorneweatherson2005 | 2 | 117 | 3 | 3 | accepted |
| 7 | eganhawthorneweatherson2005 | 2 | 27 | 2 | 2 | accepted |
| 8 | eganhawthorneweatherson2005, eganweatherson2011 | 1 | 81 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 9 | eganweatherson2011 | 1 | 1 | 1 | 1 | accepted |
| 10 | eganweatherson2011, gsv1996 | 1 | 4 | 4 | 4 | accepted |
| 11 | gsv1996 | 1 | 5 | 1 | 1 | accepted |
| 12 | gsv1996 | 2 | 17 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 13 | gsv1996, hawkesteinertthrelkeld2021 | 1 | 4 | 4 | 4 | accepted |
| 14 | hawkesteinertthrelkeld2021 | 2 | 48 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 15 | hawkesteinertthrelkeld2021, hollidaymandelkern2024 | 2 | 4 | 4 | 4 | accepted |
| 16 | hollidaymandelkern2024 | 4 | 4 | 4 | 4 | accepted |
| 17 | hollidaymandelkern2024 | 1 | 13 | 2 | 2 | accepted |
| 18 | hollidaymandelkern2024 | 4 | 20 | 4 | 4 | accepted |
| 19 | hollidaymandelkern2024 | 1 | 3 | 3 | 3 | accepted |
| 20 | hollidaymandelkern2024, klinedinstrothschild2012 | 1 | 6 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 21 | klinedinstrothschild2012 | 1 | 9 | 1 | 1 | accepted |
| 22 | klinedinstrothschild2012, knobeyalcin2014 | 2 | 12 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 23 | knobeyalcin2014, kolodnymacfarlane2010 | 1 | 35 | 2 | 2 | accepted |
| 24 | kolodnymacfarlane2010, macfarlane2011 | 1 | 16 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 25 | macfarlane2011 | 1 | 40 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 26 | macfarlane2011, macfarlane2014 | 2 | 4 | 4 | 4 | accepted |
| 27 | macfarlane2014 | 1 | 1 | 1 | 1 | accepted |
| 28 | macfarlane2014 | 1 | 18 | 1 | 1 | accepted |
| 29 | macfarlane2014 | 1 | 6 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 30 | macfarlane2014 | 1 | 4 | 4 | 4 | accepted |
| 31 | macfarlane2014 | 2 | 14 | 2 | 2 | accepted |
| 32 | macfarlane2014 | 1 | 5 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 33 | macfarlane2014 | 0 | 0 | 0 | 0 | The supplied window concerns faultless disagreement, taste-predicate semantics, belief reports, and expressivism. It contains no relevant argument root about epistemic modals, so all items are omitted as outside the topic. |
| 34 | macfarlane2014 | 1 | 5 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 35 | macfarlane2014 | 1 | 4 | 4 | 4 | accepted |
| 36 | macfarlane2014 | 1 | 23 | 2 | 2 | accepted |
| 37 | macfarlane2014 | 0 | 0 | 0 | 0 | The supplied window discusses future contingents, branching time, supervaluationism, relativism, and retrospective accuracy; it does not materially address epistemic modals, so no roots are selected. |
| 38 | macfarlane2014 | 2 | 2 | 2 | 2 | accepted |
| 39 | macfarlane2014 | 1 | 4 | 4 | 4 | accepted |
| 40 | macfarlane2014 | 3 | 14 | 3 | 3 | accepted |
| 41 | macfarlane2014 | 1 | 4 | 4 | 4 | accepted |
| 42 | macfarlane2014 | 3 | 4 | 4 | 4 | accepted |
| 43 | macfarlane2014, moss2015 | 2 | 49 | 4 | 4 | accepted |
| 44 | moss2015 | 1 | 4 | 4 | 4 | accepted |
| 45 | moss2015 | 4 | 24 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 46 | moss2015 | 1 | 4 | 4 | 4 | accepted |
| 47 | moss2015 | 1 | 4 | 4 | 4 | accepted |
| 48 | moss2015, ninan2018 | 2 | 4 | 4 | 4 | accepted |
| 49 | ninan2018 | 1 | 6 | 1 | 1 | accepted |
| 50 | ninan2018 | 1 | 4 | 4 | 4 | accepted |
| 51 | ninan2018, rothschild2012 | 1 | 34 | 4 | 4 | accepted |
| 52 | rothschild2012, schaffer2011 | 1 | 4 | 4 | 4 | accepted |
| 53 | schaffer2011 | 4 | 11 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 54 | schaffer2011 | 4 | 12 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 55 | schaffer2011, veltman1996 | 2 | 15 | 3 | 3 | accepted |
| 56 | veltman1996 | 2 | 3 | 3 | 3 | accepted |
| 57 | veltman1996 | 0 | 0 | 0 | 0 | This window develops Veltman's theory of default reasoning and its formal consequences. Although it uses update semantics and notions of possibility, its arguments do not substantively address epistemic modals, so no roots are selected. |
| 58 | veltman1996, vonfintelgillies2007 | 4 | 4 | 4 | 4 | accepted |
| 59 | vonfintelgillies2007 | 2 | 10 | 3 | 3 | accepted |
| 60 | vonfintelgillies2007 | 4 | 11 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 61 | vonfintelgillies2011 | 1 | 26 | 1 | 1 | accepted |
| 62 | vonfintelgillies2011 | 4 | 37 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 63 | vonfintelgillies2011 | 2 | 4 | 4 | 4 | accepted |
| 64 | vonfintelgillies2011, willer2013 | 3 | 12 | 3 | 3 | accepted |
| 65 | willer2013 | 1 | 4 | 4 | 4 | accepted |
| 66 | willer2013, wright2007 | 1 | 4 | 4 | 4 | accepted |
| 67 | wright2007, yalcin2007 | 3 | 9 | 4 | 4 | accepted |
| 68 | yalcin2007 | 2 | 4 | 4 | 4 | accepted |
| 69 | yalcin2007, yalcin2011 | 4 | 4 | 4 | 4 | accepted |
| 70 | yalcin2011, yalcin2015 | 1 | 3 | 3 | 3 | accepted |
| 71 | yalcin2015 | 2 | 12 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 72 | yalcin2015 | 4 | 30 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 73 | yalcin2015 | 1 | 14 | 1 | 1 | accepted |

31 frozen commitments explicitly carry support_omitted; these are assumptions at recorded frontiers, not proofs of omitted support.

| Window | Accepted | Cut depth | Commitment → omitted support |
|---|---|---|---|
| 1 | True | 0 | beddorgoldstein2021:r36-47-refine:c_raTwoDifficulties → beddorgoldstein2021:r36-47-refine:link_raTwoDifficulties |
| 2 | True | 0 | bledin2014:r21-40:general → bledin2014:r21-40:inf9<br>braun2012:union:item:braun2012:salvage:47d76f588ef2072f:braun2012:r27-52:ic_advantage → braun2012:union:item:braun2012:salvage:47d76f588ef2072f:braun2012:r27-52:inf_advantage |
| 5 | True | 0 | egan2007:salvage:dec68a6bbc12fd01:egan2007:r1-19:n_relativist_might → egan2007:salvage:dec68a6bbc12fd01:egan2007:r1-19:inf_relativist_might |
| 6 | True | 0 | egan2007:salvage:65b686e45c7b24fd:egan2007:r20-39:c_final → egan2007:salvage:65b686e45c7b24fd:egan2007:r20-39:inf_final<br>eganhawthorneweatherson2005:r1-24:n_concl_rel → eganhawthorneweatherson2005:joined:inf_g42_final, eganhawthorneweatherson2005:r1-24:n_inf_rel |
| 7 | True | 0 | eganhawthorneweatherson2005:joined:g29_ic_avoid_both → eganhawthorneweatherson2005:joined:inf_g29_avoid_both |
| 11 | True | 0 | gsv1996:r18-35:n_order → gsv1996:r18-35:inf1 |
| 17 | True | 0 | hollidaymandelkern2024:r18-35:d12 → hollidaymandelkern2024:r18-35:d_inf3 |
| 18 | True | 0 | hollidaymandelkern2024:r36-52:c18 → hollidaymandelkern2024:r36-52:inf_c18<br>hollidaymandelkern2024:r36-52:c20 → hollidaymandelkern2024:r36-52:inf_c20<br>hollidaymandelkern2024:r36-52:c3 → hollidaymandelkern2024:r36-52:inf_c3<br>hollidaymandelkern2024:r36-52:c6 → hollidaymandelkern2024:r36-52:inf_c6 |
| 21 | True | 0 | klinedinstrothschild2012:r26-37:p35_sum → klinedinstrothschild2012:r26-37:inf_p35_1 |
| 23 | True | 0 | knobeyalcin2014:r1-21:cc1 → knobeyalcin2014:r1-21:inf8 |
| 28 | True | 0 | macfarlane2014:r49-70:n_assessment_sensitivity → macfarlane2014:r49-70:inf_as |
| 31 | True | 0 | macfarlane2014:r114-135:n56 → macfarlane2014:r114-135:i13 |
| 36 | True | 0 | macfarlane2014:r214-224-refine:c_dilemma_false → macfarlane2014:r214-224-refine:inf_to_assessment_sensitivity |
| 40 | True | 0 | macfarlane2014:r280-290-refine:c1 → macfarlane2014:r280-290-refine:inf21<br>macfarlane2014:r280-290-refine:ic18 → macfarlane2014:r280-290-refine:inf16<br>macfarlane2014:r280-290-refine:ic21 → macfarlane2014:r280-290-refine:inf19 |
| 43 | True | 0 | moss2015:union:item:moss2015:salvage:8ada77f0a96c0388:moss2015:r61-81:c1 → moss2015:union:item:moss2015:salvage:8ada77f0a96c0388:moss2015:r61-81:infC |
| 49 | True | 0 | ninan2018:r1-22:ic_problem_for_everyone → ninan2018:joined:rec_i14 |
| 51 | True | 0 | ninan2018:r1-22:ic_problem_for_everyone → ninan2018:joined:rec_i14<br>ninan2018:r23-45:n58 → ninan2018:r23-45:inf18 |
| 55 | True | 0 | schaffer2011:union:item:schaffer2011:salvage:666c341ba755e3a8:schaffer2011:r2-25:n88 → schaffer2011:union:item:schaffer2011:salvage:666c341ba755e3a8:schaffer2011:r2-25:inf20<br>veltman1996:r1-22:ic_testing_nonpersistence → veltman1996:r1-22:inf_testing |
| 59 | True | 0 | vonfintelgillies2007:union:item:vonfintelgillies2007:salvage:edb09070485ace2c:vonfintelgillies2007:r1-16:ic5 → vonfintelgillies2007:union:item:vonfintelgillies2007:salvage:edb09070485ace2c:vonfintelgillies2007:r1-16:inf5 |
| 61 | True | 0 | vonfintelgillies2011:union:item:vonfintelgillies2011:salvage:102d49a275b6d08b:vonfintelgillies2011:r1-11:a_both_readings → vonfintelgillies2011:union:item:vonfintelgillies2011:salvage:102d49a275b6d08b:vonfintelgillies2011:r1-11:link_both_readings |
| 64 | True | 0 | willer2013:r1-20:c_content_not_truth_conditional → willer2013:r1-20:inf_to_dynamic |
| 67 | True | 0 | yalcin2007:r1-22:ic16 → yalcin2007:r1-22:inf17 |
| 73 | True | 0 | yalcin2015:r27-39:n46 → yalcin2015:r27-39:inf17, yalcin2015:r27-39:inf18 |

## Targets, searches and routes

Target prose and route summaries below are model-written. Prose/formula correspondence has not been independently validated.

| Target ID | Model-written target |
|---|---|
| target1 | The semantics of epistemic modals must account for how claims relate to information, evidence, or epistemic states. |
| target2 | Whether epistemic modal claims are assessment-sensitive is distinct from whether their propositions are relativized to parameters beyond worlds. |
| target3 | A probabilistic knowledge account should require that nearby worlds where the subject has high credence in a claim also make that claim sufficiently probable relative to worldly information. |
| target4 | An adequate logic for epistemic modals should explain why epistemic contradictions remain contradictions in embedded contexts. |
| target5 | Classical inference may be reliable within a single epistemic level while failing when reasoning crosses epistemic levels. |
| target6 | Dynamic semantics can explain how epistemic modal utterances affect inquiry by changing which possibilities are treated as live. |
| target7 | The behavior of epistemic modal assertions may require pragmatic or expressive effects beyond their truth-conditional content. |
| target8 | Assigning sets of probability measures rather than sets of worlds may provide a unified account of epistemic modals and related vocabulary. |
| target9 | De re epistemic modal claims can depend on a way of thinking of an object, rather than on a possibility it has independently of such a perspective. |
| target10 | Context may leave the relevant group or information source for an epistemic modal underspecified rather than fixing it uniquely. |

Native search phase: {"status": "not_recorded", "jobs": [], "failed_job_indices": [], "cancelled_job_indices": [], "retried_job_indices": [], "incomplete_analyses": [], "note": "Only completed searches supply routes. Missing polarity or failed analysis is not evidence of no conflicts."}

**Unpublished journal evidence:** 19/20 jobs have completion receipts and 19 traces pass the native seal and structural trace checks when read against their verified journal chains. The completion count in this handoff and DONE line uses those journals. Canonical publication and paired analysis remain unfinished. The native HTML therefore marks these sidecars unsealed relative to the main log; it retains the journals as artifacts. The independent journal audit below does not merge or rewrite native history. Native report accounting excludes these unpublished model receipts; this handoff adds their deduplicated usage.

[Open the readable journal companion](/home/dev/ara-work/reports/overnight/codex2/journal-searches.html). All 19 completed journal graphs are OPEN. None is a closed proof; zero routes were published to the main log. The unfinished job is 0007.

| Target | Polarity | Nodes | Proof depth | Outcomes | Journal authenticated/complete |
|---|---|---|---|---|---|
| target1 | target | 1 | 0 | {"OPEN": 1} | True/True |
| target1 | negation | 1 | 0 | {"OPEN": 1} | True/True |
| target2 | target | 1 | 0 | {"OPEN": 1} | True/True |
| target2 | negation | 1 | 0 | {"OPEN": 1} | True/True |
| target3 | target | 1 | 0 | {"OPEN": 1} | True/True |
| target3 | negation | 1 | 0 | {"OPEN": 1} | True/True |
| target4 | target | 1 | 0 | {"OPEN": 1} | True/True |
| target5 | target | 1 | 0 | {"OPEN": 1} | True/True |
| target5 | negation | 1 | 0 | {"OPEN": 1} | True/True |
| target6 | target | 1 | 0 | {"OPEN": 1} | True/True |
| target6 | negation | 1 | 0 | {"OPEN": 1} | True/True |
| target7 | target | 1 | 0 | {"OPEN": 1} | True/True |
| target7 | negation | 4 | 1 | {"OPEN": 1} | True/True |
| target8 | target | 1 | 0 | {"OPEN": 1} | True/True |
| target8 | negation | 4 | 1 | {"OPEN": 1} | True/True |
| target9 | target | 1 | 0 | {"OPEN": 1} | True/True |
| target9 | negation | 3 | 1 | {"OPEN": 1} | True/True |
| target10 | target | 1 | 0 | {"OPEN": 1} | True/True |
| target10 | negation | 1 | 0 | {"OPEN": 1} | True/True |

Journal evidence and diagnostic traces: [unpublished-search-audit.json](/home/dev/ara-work/reports/overnight/codex2/unpublished-search-audit.json). No model-written route summaries were requested because awaiting_selection was not reached.

| Target | Polarity | Node receipts | Proof depth | State receipts | Outcomes | Authenticated/complete |
|---|---|---|---|---|---|---|
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |
| (unknown) | target | 0 | 0 | 0 | {} | False/False |

Unsealed raw observations are not authenticated completed trees: [{"path": "search-traces/1bae783f0b15f3a0-d8db54cdf2b649e29956167b778bc710.jsonl", "declared_target": "target10", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/23ccf6f53f43084a-71dfefa6ae8e469892db886c8b639022.jsonl", "declared_target": "not:target6", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/249f02098b15f5a7-6c2285508dc942c4bed111367611de7f.jsonl", "declared_target": "not:target7", "nodes": 4, "states": 4, "max_depth": 1, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/262e8b86cbc7e10a-1bee6b7854f848e582ac6e90eb05d9e1.jsonl", "declared_target": "not:target8", "nodes": 4, "states": 5, "max_depth": 1, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/2bb8f911d96472ac-aac320e78f764aafb2af4d945ee4266b.jsonl", "declared_target": "target1", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/2d307806d720e1af-3832e7496dce4510bc1c6bed65ab0885.jsonl", "declared_target": "target9", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/30aeda82f32fe560-8886544af72944049722ffa7040e6e62.jsonl", "declared_target": "target5", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/30cee138624887df-7efaf26584424f29af5785f8da967b3b.jsonl", "declared_target": "target3", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/35d205732e502c20-7e438b6637674f38b5cbd7d466d8d790.jsonl", "declared_target": "target6", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/3a18fc0909b8dfb0-f7a1c59b37e7475aa7cdc78d6d371530.jsonl", "declared_target": "not:target1", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/3a791a1ef7794df1-9f0f87fe3a51460ab887ddde120228d7.jsonl", "declared_target": "not:target9", "nodes": 3, "states": 4, "max_depth": 1, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/3d19cad821e652fa-c6614c36cab14c04946cf18d7c1b98bf.jsonl", "declared_target": "target7", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/62b956b249ac993e-e2cfb337bf754d13ac3aff5d360ef90f.jsonl", "declared_target": "not:target5", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/64ac6b5d2500cfed-0e9b4b3a284d4ca8b296dd4744d961be.jsonl", "declared_target": "not:target2", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/9c7c78800a20ee62-c4a35396414f49d5b105ae3c4444da39.jsonl", "declared_target": "target8", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/bddb840605beac68-1522dcbad1324dbdb19d1fdd1b5c5856.jsonl", "declared_target": "not:target10", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/cb4e942b20af1df3-beb7629c798146f892dc2009e8f16949.jsonl", "declared_target": "target4", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/e88a636269631a3e-8480d8205041464a802f7c0b9060ad06.jsonl", "declared_target": "target2", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/f835b15eb63cdb0b-d820cd4f8f824247912c49989873eaab.jsonl", "declared_target": "not:target3", "nodes": 1, "states": 2, "max_depth": 0, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}, {"path": "search-traces/fe5e67f76419f1b7-a459b6beb3f54be4b900e81f2bc2e92d.jsonl", "declared_target": "not:target4", "nodes": 3, "states": 3, "max_depth": 1, "trust": "Unsealed raw artifact observations only; not authenticated or interpreted as a valid tree by native reporter"}]

OPEN is not a proof. CLOSED is relative to formalized T and licensed steps. Missing polarity/paired analysis is not evidence of no conflicts. Proof depth differs from the state-ancestry depth in the native tree view.

None recorded.

## Usage, limits, refusals and timing

6,712,693 local recorded/reserved tokens including stage preflight, standalone canary and summaries when present; 227 pilot dispatches;
243 model receipts including cache replays; 0.0 new API USD. Codex USD equivalent is **unavailable**, not measured zero.
0 unknown-usage receipts reserve 0 tokens already included above; their actual usage remains unknown.

Measured usage is 6,712,693 tokens. Standalone canary adds 1 dispatches and native schema preflight adds 16 dispatches to the 227 native pilot dispatches.

A received response still awaiting validation has 9,201 measured tokens, already charged by native budget settlement but absent from MODEL receipts. Including it gives 6,721,894 measured tokens across this pilot and its preflights. This usage is known, not an unknown reservation.

Unfinished validation receipt: [{"call_id": "73fc13c9-797d-4441-a9e4-4207d1e619cd", "kind": "formalise", "reserved_usage": {"cache_read_tokens": 0, "cache_write_tokens": 0, "input_tokens": 37182, "output_tokens": 16384, "server_tool_uses": 0}, "measured_usage": {"cache_read_tokens": 0, "cache_write_tokens": 0, "input_tokens": 8373, "output_tokens": 828, "server_tool_uses": 0}, "measured_api_usd": 0.0, "status": "response received; validation unfinished; no MODEL settlement"}]

Pilot-only local tokens: 6,632,269; imported historical tokens: 11,348,025. Imported history is reported separately from the local subscription cap.

| Stage | Receipts | Input | Output | Cache read | Cache write | Summed call seconds |
|---|---|---|---|---|---|---|
| answer_cq | 6 | 198623 | 1806 | 0 | 0 | 238.655 |
| build_t_batch | 53 | 1050222 | 46080 | 55552 | 0 | 1822.016 |
| formalise | 36 | 179877 | 12237 | 34560 | 0 | 1735.789 |
| isolation_canary | 2 | 8652 | 2277 | 0 | 0 | 44.318 |
| map_leaf | 25 | 815700 | 4272 | 5888 | 0 | 744.89 |
| propose_cuts | 29 | 1152251 | 19161 | 18432 | 0 | 1330.992 |
| propose_targets | 1 | 34550 | 959 | 0 | 0 | 32.381 |
| select_t_roots | 74 | 2819887 | 112403 | 58880 | 0 | 2433.3 |

Standalone canary accounting: {"calls": 1, "api_usd": "0.0", "subscription_equivalent_usd": null, "subscription_equivalent_unavailable_calls": 1, "tokens": {"input_tokens": 4323, "output_tokens": 1255, "cache_read_tokens": 0, "cache_write_tokens": 0, "server_tool_uses": 0}, "summed_call_wall_seconds": 12.807146689970978, "unknown_calls": 0, "unknown_usage_reserved_tokens": 0}

Native schema preflight accounting: {"calls": 16, "api_usd": "0.0", "subscription_equivalent_usd": null, "subscription_equivalent_unavailable_calls": 16, "tokens": {"input_tokens": 72425, "output_tokens": 2421, "cache_read_tokens": 0, "cache_write_tokens": 0, "server_tool_uses": 0}, "summed_call_wall_seconds": 69.32655287603848, "unknown_calls": 0, "unknown_usage_reserved_tokens": 0}

Subscription-limit/watch receipts: {"subscription_equivalent_usd": null, "subscription_usd_equivalent_unavailable_calls": 226, "subscription_limit_occurrences": [], "subscription_waits": [], "subscription_wait_seconds": 0, "subscription_limit_active_since": null, "subscription_limit_elapsed_seconds": 0}

Admission begins with Anthropic-tokenizer calibration and adjusts upward from Codex usage; it is not a proven Codex token bound. Configured output allowances are admission reservations: the CLI has no hard output-token cap, so measured excess can stop the run after a response. The nominal 70k input + 64k output + 60k catalogue arithmetic does not override live admission.

None recorded.

| Timestamp | Stage | Refusal/retry/stop payload |
|---|---|---|
| 2026-10-26T09:18:28.269437+00:00 | formalise | {"accounting": "actual", "attempt": 1, "auth_mode": "chatgpt", "auth_threat_model": "Linux mount/PID namespace hides operator homes; auth writes denied; refresh endpoint disabled; no credential rotation.", "auth_transport": "Per-call read-only bind of current host auth file, linked from temporary in-memory CODEX_HOME; no credential copy.", "cache_hit": false, "cache_key": "1e88102101bc7382ce81f6858e1313b01bd737906e52750dfe94eac609eb1872", "calibration": {"correction": "like-for-like; single-turn input versus initial, otherwise aggregate versus aggregate; run-local upward only; old observations excluded", "factors": {"build_t_batch": 0.553224, "propose_targets": 0.486932, "select_t_roots": 0.551583}, "fallback_factor": 0.553224, "observation_version": "like-for-like-v2", "runtime_overhead_current": 3978, "runtime_overhead_tokens": 949, "sha256": "7474c9e793c07eb37cc7dd59885b71ba6ab247845b91efdef6509449fe1100ea", "version": "claude-code-input-v1"}, "call_id": "8afd0545-0373-44e6-9557-335842660187", "cli": {"exit_status": 0, "native_schema_hash": "7ae0fe0443d6be6136950620a7ca6c3014ff20726c0b4f281a552a40e3f31fc7", "num_turns": 1, "requested_model": "gpt-6-luna", "schema_transform": "ara-openai-strict-v1", "served_model": null, "served_model_verified": false, "session_id": "01a17780-1df7-7812-92b2-3f9a736294b8", "version": "codex-cli 0.163.0", "wall_seconds": 59.22747552499641, "warning_events": 1, "wire_schema_hash": "e3504bbc817e171939b81b8757d86b848ac85b818873cbade5d656ff8a804ce6"}, "cli_version": "codex-cli 0.163.0", "concurrency": 4, "credential_output_scan": "raw and recursive decoded strings, including cache replay", "dispatch_stage": "formalise", "effective_prompt_note": "Minimal task-only model instructions replace coding-agent defaults; stage developer instructions and native stage prompt retained; not API byte-identical.", "effort": "high", "fallback_blocks": [], "fallback_iterations": [], "fallback_used": false, "fresh_cwd_and_config": true, "host_context_isolation": "Home directories and host /tmp /run hidden; fresh HOME and CODEX_HOME; project docs disabled; user config ignored.", "isolation_flags": ["--ephemeral", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check", "--json", "-s", "read-only", "-c", "approval_policy=\"never\"", "-c", "suppress_unstable_features_warning=true", "-c", "project_doc_max_bytes=0", "-c", "web_search=\"disabled\"", "-c", "mcp_servers={}", "-c", "memories.use_memories=false", "-c", "memories.generate_memories=false", "-c", "skills.bundled.enabled=false", "-c", "skills.include_instructions=false", "-c", "features.skip_host_skill_discovery=true", "-c", "tools.update_plan.enabled=false", "-c", "tools.experimental_request_user_input.enabled=false", "-c", "analytics.enabled=false", "-c", "feedback.enabled=false", "-c", "history.persistence=\"none\"", "-c", "cli_auth_credentials_store=\"file\"", "-c", "features.shell_tool=false", "-c", "features.unified_exec=false", "-c", "features.shell_snapshot=false", "-c", "features.apps=false", "-c", "features.plugins=false", "-c", "features.hooks=false", "-c", "features.memories=false", "-c", "features.goals=false", "-c", "features.multi_agent=false", "-c", "features.multi_agent_v2=false", "-c", "features.browser_use=false", "-c", "features.computer_use=false", "-c", "features.image_generation=false", "-c", "features.view_image=false", "-c", "features.skill_search=false", "-c", "features.sleep_tool=false", "-c", "features.workspace_dependencies=false"], "max_cli_turns": 1, "operator_identity_output_scan": true, "output_bound_note": "Admission reserves the configured output allowance twice; CLI has no hard output-token flag. Actual usage can stop the run after receipt.", "provider": "codex_cli", "reason": "ValidationError", "requested_model": "gpt-6-luna", "schema_transform": "ara-openai-strict-v1", "schema_transport": "Versioned OpenAI-strict projection passed to --output-schema; optional nulls normalized before authoritative local Draft202012Validator.", "served_model": "unverified", "served_model_policy": "CLI model event when reported; otherwise explicitly unverified, never inferred from -m.", "status": "rejected", "subscription_cost_note": "Codex JSON reports tokens, not list-price USD; cost equivalent unavailable, never treated as measured zero.", "subscription_usage": {"basis": "unavailable; Codex reports tokens only; not measured API USD", "cost_equivalent_usd": null}, "system_prompt": "", "thinking": "adaptive", "token_cap_policy": "local_run_usage; imported history retained separately", "token_estimate_method": "API-receipt UTF-8 calibration seed; different Codex tokenizer; upward-only like-for-like correction; no free counter", "tokenizer_note": "Seed table measured Anthropic API tokens, not the Codex tokenizer. Codex usage corrects estimates upward only.", "usd_cap_policy": "not_applicable_subscription", "visible_tool_policy": "Generic built-in definitions may be visible; visible definitions do not authorize use; any tool event rejects the response.", "web_retrieval": "disabled; search_evidence refuses"} |
| 2026-10-26T09:18:28.323749+00:00 | validation_retry | {"kind": "formalise", "next_attempt": 2, "reason": "ValidationError"} |

| Stage interval | Seconds |
|---|---|
| startup_and_plan | 1341.129348 |
| construction_after_plan | 7931.068899 |
| construction_until_interruption | None |
| target_proposal | 40.851396 |
| search_publication | None |
| search_through_saved_analyses | None |
| route_summaries | None |

Native command wall time: 11088.980 seconds. Summed call time is distinct from elapsed concurrent wall time.

## Local validation blocker

Search job 0007 rejected its first formalise response with ValidationError at 09:18:28 UTC. Its correction response arrived at 09:19:28 and remained in local validation until the halt at 09:33:21. The received response is 1,306 characters, with 17 formula nodes and JSON depth 22; it contains a chain of nested conjunctions, including unary conjunctions that violate the native minimum arity. The exact-schema offline replay normalized it in 0.45 seconds, then timed out after 45 seconds in Draft202012Validator.validate. Captured Python stacks show recursive oneOf, properties, items and reference validation. A second replay using the equivalent logged schema also timed out. Neither replay invoked a model.

A placeholder-only scaling probe measured unary-conjunction depths 1–6 at 0.0012, 0.0080, 0.0494, 0.3707, 2.6326 and 22.0993 seconds. The live process grew from 548,312 KiB during planning to 2,460,020 KiB RSS before halt. These observations support a pathological recursive-validation cost; they do not establish a fix or an exact finish time. No native code, schema, configuration, accepted output, journal or validation rule was changed.

Evidence: [stop receipt](/home/dev/ara-work/reports/overnight/codex2/local-validation-stop.json), [exact replay stack](/home/dev/ara-work/reports/overnight/codex2/probe-native-validation.txt), [scaling timings](/home/dev/ara-work/reports/overnight/codex2/validation-scaling.txt). The full evidence directory is `/home/dev/ara-scaffold/runs/codex-pilot-2-control/`.

## Report verification and preserved history

Native ara report covers 40 inputs. Copied 30,183 files / 3,485,550,029 bytes with matching SHA-256 hashes, including all linked sidecars.
HTML: 1,031,101 bytes (1.031101 decimal MB). Opened the delivered file in Chromium 143.0.7499.4;
3,310 links/anchors checked; 0 broken links. Desktop/mobile overflow check: False.

Desktop viewport/document widths are 1440/1440 pixels; mobile widths are 390/410 pixels. The mobile document overflows by 20 pixels. Native HTML bytes were preserved; horizontal overflow remains unresolved. No page errors or missing anchors were recorded.

Expanded-tree browser receipt: {"passed": true, "scope": "Current pilot main-log view is unsealed; verified journal traces are in journal-searches.html", "current_pilot_search_details": 20, "expanded_search": "Search 1bae783f0b15f3a0-d8db54cdf2b649e29956167b778bc710", "run_index": 39, "proof_nodes": 0, "state_depth": 0, "proof_depth": 0, "linked_files": [{"path": "trees/run-39-search-0.json", "bytes": 706}, {"path": "trees/run-39-search-0.dot", "bytes": 49}], "linked_json_opened": true, "dot_valid_header": true, "tree_keys": ["begin_seq", "version", "search_id", "target", "states", "receipts", "decisions", "complete", "authenticated", "source", "issues", "completed_routes"], "screenshot": "/home/dev/ara-scaffold/runs/codex-pilot-2-control/report-expanded-current-tree.png", "svg_available": false}

The journal companion displayed all 19 expandable trace records, checked 41 links with no missing files or page errors, and opened an authenticated complete trace with 4 proof nodes. Desktop and mobile width checks passed: True. These are journal views, not published routes.

Verified 91,905 reconstructed event occurrences, 27,614 unique bodies and 927 artifact copies; input logs/anchors unchanged.

All 9 prior Codex-pilot files matched their pre-run hashes; pilot-3 and pilot-4 handoffs and preserved prior handoffs matched their hashes. The current config changed only by its required proof-log binding; its pre-change bytes were retained. Source tree remains clean at 8aa265fa32b97bdbae662108ba080950c5c73034.

The halted pilot 4 remains preserved. Its native publication was interrupted; unpublished search journals are retained as artifacts, not silently merged into canonical history. Its halt-state accounting includes 1,231 Claude dispatches and 59,590,188 recorded/reserved tokens, including two calls dispatched during shutdown. Those are historical usage, not new Claude calls by this pilot. Earlier extraction gaps, quarantines, omitted material and unknown actual usage remain in prior handoffs and lineage.

## Remaining limits and next step

The validation owner needs to reproduce the nested invalid response and address recursive diagnostic cost while preserving full native schema authority. A reviewed fix and fresh authorization are needed before another pilot or recovery attempt. This report does not claim 20 completed searches, a published route set, or selection readiness.

Formal schema acceptance and licensed/Z3-checked steps do not establish faithful formalization or true commitments. Paper coverage is not complete extraction. Failed searches, missing summaries and unavailable paired analysis above remain unresolved. No route was selected; operator selection is a separate future instruction. The single frozen T is not rebuilt by a construction resume. No source checks or budgets were weakened to force completion.

## Finding placement

| Finding | Section |
|---|---|
| 1. Outcome, freeze and coverage | Opening; Frozen T and construction |
| 2. Revision, auth, routing, live plan/calibration difference, canary and unverified serving identity | Methodology and configuration |
| 3. Every window, skipped material and omitted support | Frozen T and construction |
| 4. Target/polarity results, route summaries and missing work | Targets, searches and routes |
| 5. Usage, unknowns, output/calibration limits, refusals and timing | Usage, limits, refusals and timing |
| 6. Full-lineage copy, browser/tree proof and rendering limitations | Report verification and preserved history |
| 7. Halted pilot 4 and historical completeness/accounting limits | Report verification and preserved history |
| 8. Semantic limits and no route selection | Remaining limits and next step |

9. Recursive validation cost, operational halt, unpublished completion and measured pending usage: Local validation blocker; Targets, searches and routes; Usage, limits, refusals and timing.

9 findings, 9 placed.

DONE zeta codex-pilot-2 freeze=/home/dev/ara-scaffold/runs/codex-pilot-2/commitments.json commitments=166 papers_in_T=24/26 targets=10 searches_ok=19/20 routes=0 status=blocked:local-validation-stall report=/home/dev/ara-work/reports/overnight/codex2/report.html
