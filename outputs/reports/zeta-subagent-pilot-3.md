# Zeta subagent pilot 3

**blocked:authentication.** No frozen T exists. There are **8 provisional commitments from 2/26 papers**, with no targets, searches or routes. No route was selected. Native pilot exit: -2. New API spend is zero.

Target proposal, all 20 planned polarity searches, and paired analyses were never reached. No route summaries were applicable.

No frozen T exists. The two accepted windows retain 8 provisional commitments; these are preserved in their hash-checked batch artifacts, not counted as frozen commitments. Construction stopped before the remaining windows, target proposal, search or route summaries.

Three `select_t_roots` calls, for windows 6–8, returned HTTP 401 classified `cli_auth_error`, non-retryable, with no served model recorded. Native construction skipped those windows. The execution supervisor paused before another dispatch, inspected only allowlisted diagnostics and credential expiry metadata, then sent SIGINT/SIGCONT to stop the process. Exit -2 is the supervisor intervention, not a native global-budget stop. The hash chain and anchor remained valid; all dispatched calls had terminal receipts. The external control action is explicitly labeled in the run log.

The credential source file was modified at 07:06:41 UTC during this run and its recorded expiry was 15:06:41 UTC, still in the future. This provider reads authentication once into an in-memory snapshot and disables child refresh. A stale snapshot is consistent with the timing, but token values were not compared or disclosed, so that cause is not proven. No credentials were changed by this execution. `resume-construction` at this revision accepts finalized API request-refusal receipts, not these Claude Code authentication failures; no supported config-only continuation was found. No new pilot was launched to discard or hide the partial run.

[Open the full-lineage report](/home/dev/ara-work/reports/overnight/final3/report.html). [Structured audit](/home/dev/ara-scaffold/runs/subagent-pilot-3-control/pilot-audit.json). The previous handoff is preserved byte-for-byte as [zeta-subagent-pilot-2.md](/home/dev/ara-work/reports/zeta-subagent-pilot-2.md). The prior pilot, final report, interim report and part-7 backup remain preserved.

## Revision, configuration and review boundary

Ran requested main `f9c5a8fe24cfb73cf5dc47a9d2743a503f9c9179` from a clean tree, with fresh run/cache directories and an empty audience. All construction, target, search and writing stages resolve to `claude_code` / `claude-opus-5-5`, no fallback. Window cap multiplier is 2; search and provider concurrency are both 4. The native standalone canary ran first and passed; native startup canaries remain in the linked receipts. No API fallback, extraction rerun, credential change, tracked source edit, commit or push was performed.

Read kappa2’s review and re-review, Omega Rounds 6–8, and Xi Round 8 plus its final integration. Kappa2’s zero-blocker verdict and 854-passed/2-skipped suite apply to scratch merge `469c278`, not automatically to the requested merge resolution. Xi separately verified exact head `f9c5a8f`: 854 passed, 2 skipped, then 395 mutations failed as intended and all 395 restorations passed. The recorded source hashes were checked against this checkout before launch. These are prior review/integration results, not suites rerun by this execution.

The literature is unchanged: `/home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt`, SHA-256 `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`. No old construction batches were restored. Historical extraction provenance was imported normally.

## Corrected calibration, budgets and retries

Pilot 2 froze 95 commitments from 15/26 papers, completed 8/20 searches, and retained 15 OPEN routes before its 30M local-token guard stopped search. Its 48k catalogue budget limited later construction. Pilot 3 changes only the two requested budgets plus the isolated cache path. The retained calibration factor is 0.553224 with separate fixed overhead of 949 tokens; like-for-like observations may raise estimates. An admission fit does not guarantee accepted contributions or complete paper coverage.

The first live formalization recorded 29,803 aggregate input tokens against 89,846 reserved input tokens, using `aggregate_input_vs_aggregate_reservation`. Its initial-context estimate was 12,923; the factor changed from 0.553224 to 0.553224. All local observations remain in the structured audit.

The requested 100,000,000-token cap applies to local subscription usage, including reservations and unknown usage. Imported tokens remain visible in accounting but do not consume this subscription cap. API admission remains history-inclusive. Other retained limits include 70,000 batch-input tokens, 100,000 working-T tokens, 60,000 catalogue tokens, 233 symbol-growth tokens per item, and 200,000 model-context tokens.

At the start of the last attempted window (8), catalogue usage was 4,538/60,000, remaining symbol allowance 55,462, and working-T input 11,256. All native per-window budget receipts are retained in the structured audit; acceptance and refusal counts below describe the observed result.

Native transport allows one retry for an unclassified exit 1 within configured retry limits. Exhausted job-local failures do not cancel sibling searches; each failed job may receive one final attempt after the initial queue drains. Global budget/context and infrastructure stops remain authoritative. Only allowlisted categories/subtypes and numeric diagnostic metadata survive; unavailable free-text diagnostics are not inferred. A retry policy is not a diagnosis of an error’s cause.

| Local tokens | Imported historical tokens | Combined recorded tokens | Local cap |
|---|---|---|---|
| 797568 | 11348025 | 12145593 | 100000000 |

Configuration: `runs/inputs/subagent-pilot-3-config.yaml`, copied from pilot 2; `pilot.token_cap=100000000`, `pilot.working_t_symbol_token_budget=60000`. Configured context arithmetic is 70,000 + 64,000 + 60,000 = 194,000 under the 200,000 bound; the native source-input calculation retains 70,000. Native planning admitted all 70 windows without reducing the catalogue budget: largest counted input 68,523, 160 global commitment slots, initial share 2 and cap 4 per window. Exact live admission remains authoritative. No configurable structured-call max-turns key exists in this revision: the provider hard-codes `--max-turns 2` and metadata `max_cli_turns=2`. The prior error receipt reported three turns; that was not a configurable setting of three. The code was left unchanged.

Subscription monitoring recorded 0 usage/rate-limit occurrences and 0 seconds of logged native backoff. The monitor's two-hour persistence cutoff was not triggered. No manual retry loop was used. All occurrences and wait receipts are retained in `subscription-watch.json`; absence of a recorded limit is not a claim about remaining weekly quota.

## Frozen T and paper coverage

Freeze count: 0. Freeze path: `none`. SHA-256: `none`. Accepted batch IDs were checked against hash-verified native batch artifacts; frozen commitments were checked only when a freeze exists. Paper/kind linkage uses recorded evidence IDs and citations; these checks do not establish faithful formalization or the truth of commitments.

| Paper ID | Commitments provisional only |
|---|---|
| vonfintelgillies2007 | 0 |
| eganweatherson2011 | 0 |
| vonfintelgillies2011 | 0 |
| wright2007 | 0 |
| schaffer2011 | 0 |
| braun2012 | 0 |
| eganhawthorneweatherson2005 | 0 |
| egan2007 | 4 |
| macfarlane2011 | 0 |
| yalcin2007 | 0 |
| yalcin2011 | 0 |
| rothschild2012 | 0 |
| moss2015 | 0 |
| hawkesteinertthrelkeld2021 | 0 |
| veltman1996 | 0 |
| gsv1996 | 0 |
| willer2013 | 0 |
| ninan2018 | 0 |
| beddorgoldstein2021 | 4 |
| hollidaymandelkern2024 | 0 |
| kolodnymacfarlane2010 | 0 |
| knobeyalcin2014 | 0 |
| klinedinstrothschild2012 | 0 |
| bledin2014 | 0 |
| yalcin2015 | 0 |
| macfarlane2014 | 0 |

| Kind | Provisional count |
|---|---|
| attacked_view | 1 |
| conclusion | 3 |
| intermediate_conclusion | 1 |
| qualification | 2 |
| distinction | 1 |

## Every construction window and skip

70 planned windows; 2 contributed. Window indices are zero-based. Retained closure items in a skipped window did not enter T. Full per-item omissions and relevance explanations remain in the linked native construction data.

| Window | Papers | Roots | Uncut | Retained | Accepted commitments | Outcome / reason |
|---|---|---|---|---|---|---|
| 0 | beddorgoldstein2021 | 4 | 4 | 4 | 4 | accepted |
| 1 | beddorgoldstein2021, bledin2014 | 3 | 65 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 2 | bledin2014, braun2012 | 2 | 40 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 3 | braun2012 | 1 | 12 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 4 | braun2012, egan2007 | 1 | 16 | 0 | 0 | mandatory root context exceeds window commitment cap, remaining global capacity or request bound |
| 5 | egan2007 | 1 | 9 | 4 | 4 | accepted |
| 6 | egan2007, eganhawthorneweatherson2005 | 0 | 0 | 0 | 0 | cli_auth_error |
| 7 | eganhawthorneweatherson2005 | 0 | 0 | 0 | 0 | cli_auth_error |
| 8 | eganhawthorneweatherson2005, eganweatherson2011 | 0 | 0 | 0 | 0 | cli_auth_error |
| 9 | eganweatherson2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 10 | eganweatherson2011, gsv1996 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 11 | gsv1996 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 12 | gsv1996 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 13 | gsv1996, hawkesteinertthrelkeld2021 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 14 | hawkesteinertthrelkeld2021 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 15 | hawkesteinertthrelkeld2021, hollidaymandelkern2024 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 16 | hollidaymandelkern2024 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 17 | hollidaymandelkern2024 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 18 | hollidaymandelkern2024 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 19 | hollidaymandelkern2024 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 20 | hollidaymandelkern2024, klinedinstrothschild2012 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 21 | klinedinstrothschild2012 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 22 | klinedinstrothschild2012, knobeyalcin2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 23 | knobeyalcin2014, kolodnymacfarlane2010 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 24 | kolodnymacfarlane2010, macfarlane2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 25 | macfarlane2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 26 | macfarlane2011, macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 27 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 28 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 29 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 30 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 31 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 32 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 33 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 34 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 35 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 36 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 37 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 38 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 39 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 40 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 41 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 42 | macfarlane2014, moss2015 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 43 | moss2015 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 44 | moss2015 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 45 | moss2015 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 46 | moss2015 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 47 | moss2015, ninan2018 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 48 | ninan2018 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 49 | ninan2018, rothschild2012 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 50 | rothschild2012, schaffer2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 51 | schaffer2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 52 | schaffer2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 53 | schaffer2011, veltman1996 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 54 | veltman1996 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 55 | veltman1996, vonfintelgillies2007 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 56 | vonfintelgillies2007 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 57 | vonfintelgillies2007 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 58 | vonfintelgillies2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 59 | vonfintelgillies2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 60 | vonfintelgillies2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 61 | vonfintelgillies2011, willer2013 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 62 | willer2013 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 63 | willer2013, wright2007 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 64 | wright2007, yalcin2007 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 65 | yalcin2007 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 66 | yalcin2007, yalcin2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 67 | yalcin2011, yalcin2015 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 68 | yalcin2015 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 69 | yalcin2015 | 0 | 0 | 0 | 0 | not processed before run stopped |

## Omitted-support cuts

0 frozen commitments explicitly carry `support_omitted`. These are assumptions at a recorded frontier, not proofs of omitted support. The table records attempted cuts, including any from skipped windows. In an unfrozen run, accepted means accepted into a provisional batch only; no cut has entered frozen T.

| Window | Accepted? | Cut depth | Commitment → omitted support IDs |
|---|---|---|---|
| 5 | True | 0 | egan2007:salvage:dec68a6bbc12fd01:egan2007:r1-19:n_relativist_might → egan2007:salvage:dec68a6bbc12fd01:egan2007:r1-19:inf_relativist_might |

## Targets

Target generation was not reached before the stop.

None recorded.

## Search outcomes and partial evidence

Native search phase: **not_recorded**. 0/20 jobs completed; failed indices []; canceled indices []; retried indices []. Missing polarity or unavailable paired analysis is not evidence of no conflicts. OPEN is not a proof; CLOSED is relative to formalized T and licensed steps.

None recorded.

None recorded.

Proof depth above is distinct from state-ancestry depth shown by the native HTML/JSON tree view. All prune reasons, trace-validation issues and failed attempts remain in the structured audit and native report.

## Routes and model-written handoff summaries

No selectable route IDs were published; no route-summary calls were made. Completed trace graphs, if present, remain evidence and are not relabeled as selectable routes.

Summary-step result: {"status": "not_applicable", "reason": "Run stopped before freeze, targets, search, or awaiting_selection; no routes exist.", "routes": 0, "generated": 0, "new_calls": 0, "wall_seconds": 0}

## Wall time and usage

| Native stage interval | Seconds |
|---|---|
| startup_and_plan | 1263.096 |
| construction_after_plan | not completed |
| construction_until_interruption | 890.313 |
| target_proposal | not completed |
| search_publication | not completed |
| search_through_saved_analyses | not completed |
| route_summaries | not completed |

Native pilot command wall time: 2201.246 seconds. Startup/provenance and final export overhead are outside some stage intervals. Summed call time excludes planning, logging and interruption intervals; it is not command elapsed time. No search ran in this pilot. Extraction was reused without new extraction calls.

Pilot, summary step if present, and standalone preflight: **3.0683828 USD-equivalent subscription usage**, **0.0 new API USD**, **799,656 local tokens**, 14 model receipts, and 3 unknown-usage receipts. CLI list-price equivalent is not API spending or remaining subscription quota. Cache replays carry zero new usage.

| Kind | Receipts | Input | Cache read | Cache write | Output | Subscription equivalent USD | Summed seconds |
|---|---|---|---|---|---|---|---|
| isolation_canary | 2 | 4 | 1578 | 663 | 1978 | 0.0451956 | 38.912 |
| select_t_roots | 9 | 345238 | 3210 | 247784 | 113360 | 2.2840820 | 265.889 |
| build_t_batch | 2 | 8 | 26586 | 36477 | 20682 | 0.7108052 | 255.166 |

The standalone preflight is additional to the per-kind table: {"calls": 1, "api_usd": "0.0", "subscription_equivalent_usd": "0.0283", "tokens": {"input_tokens": 2, "output_tokens": 967, "cache_read_tokens": 0, "cache_write_tokens": 1119, "server_tool_uses": 0}, "summed_call_wall_seconds": 9.290531694015954, "unknown_calls": 0}.

The three authentication failures have unknown actual subscription usage; their 443,530 reserved input/output tokens are included in the token totals above. The recorded USD-equivalent is known usage only and does not establish the missing actual usage. New API charges remain zero.

Full-lineage historical API accounting remains measured USD131.785270 plus USD1.844820 unknown reservations, total USD133.630090. Historical unknown actual usage remains unknown. Per-run totals include imported history and must not be added together.

## Every refusal, retry and stop

| Timestamp UTC | Stage | Reason / diagnostic | Scope |
|---|---|---|---|
| 2026-10-24T07:07:38.522287+00:00 | provider_error | CLI diagnostic suppressed. | provider/runtime |
| 2026-10-24T07:07:41.385817+00:00 | select_t_roots | ClaudeCodeError | provider/runtime |
| 2026-10-24T07:08:09.169479+00:00 | provider_error | CLI diagnostic suppressed. | provider/runtime |
| 2026-10-24T07:08:11.999804+00:00 | select_t_roots | ClaudeCodeError | provider/runtime |
| 2026-10-24T07:08:40.620533+00:00 | provider_error | CLI diagnostic suppressed. | provider/runtime |
| 2026-10-24T07:08:43.440473+00:00 | select_t_roots | ClaudeCodeError | provider/runtime |
| 2026-10-24T07:11:16.435786+00:00 | execution_control_stop | Repeated non-retryable claude_code HTTP 401 authentication failures | run |

None recorded.

Full refusal payloads and allowlisted diagnostic metadata are preserved in `pilot-audit.json` and the native event sidecars. Job failure, retry and final outcome are distinct; a failed attempt is not counted as a permanently failed job after successful recovery.

## Delivered report and verification

Native `ara report` covered **33 inputs**, including the original full lineage, pilots 1–3 and all three standalone preflights. The entire linked bundle was copied to `/home/dev/ara-work/reports/overnight/final3`: **24,376 files / 2,340,331,926 bytes**, every SHA-256 matched. HTML is **1,184,298 bytes (1.184298 decimal MB)** and opened in Chromium 143.0.7499.4. All 2,794 links/anchors passed; no page errors or missing anchors were recorded. Keep all sidecars with the HTML.

Browser no-overflow check: **False**. Desktop viewport/document width: 1440/1440; mobile: 390/403. Any overflow is retained as a rendering limitation; native report bytes are not silently altered.

The audit reconstructed 73,418 event occurrences from 22,432 unique bodies and verified 611 native artifact copies. Inputs and anchors were unchanged. The new pilot contributes 0 trace entries. Sealed trees and unsealed prefixes remain distinct. HTML previews are bounded; complete linked JSON/DOT and construction data retain omitted preview material. SVG availability is recorded in the tree exports.

Expanded-tree browser check: {"passed": true, "scope": "Historical pilot 2 evidence in full lineage; pilot 3 never reached search", "current_pilot_search_details": 0, "current_pilot_search_text": "4. Search-tree tracing\n\nFull data: see file run-32/search.json\n\nNo recorded search trees or routes.", "expanded_search": "c94a9b5ddffe:1", "historical_run_index": 30, "proof_nodes": 25, "state_depth": 11, "proof_depth": 5, "linked_files": [{"path": "trees/run-30-search-2.json", "bytes": 258629}, {"path": "trees/run-30-search-2.dot", "bytes": 2805}], "linked_json_opened": true, "dot_valid_header": true, "tree_keys": ["begin_seq", "version", "search_id", "target", "states", "receipts", "decisions", "complete", "authenticated", "source", "issues", "completed_routes", "nodes"], "screenshot": "/home/dev/ara-scaffold/runs/subagent-pilot-3-control/report-expanded-historical-tree.png", "svg_available": false}

Screenshots and browser receipts are in the control directory. Hash chains detect changes relative to checkpoints; they do not protect against rewriting both chain and checkpoint. This is a run/report verification, not a semantic-success or whole-product release verdict.

## Remaining limits and recovery

Frozen coverage is 0/26 papers. Published extraction artifacts do not establish complete extraction: earlier partial sources, quarantines, omitted/unread material, missing metadata and unknown historical accounting remain in the full lineage and preserved handoffs. The provider permits Anthropic built-ins, SDK/runtime context and StructuredOutput; effective context is not byte-identical to the API path. Canary results are specific to this CLI/environment, and calibrated estimates remain empirical.

Any failed searches, unavailable analysis or missing summaries above remain unresolved. Retained routes do not erase those gaps. Preserve this run and its accounting; do not select a route without an operator instruction. `resume-construction` is applicable only before the single freeze, never as a way to rebuild an already frozen T. No checks or budgets were weakened to force completion.

## Finding placement

| Finding | Section |
|---|---|
| 1. Requested revision, exact review boundary, configuration and canaries | Revision, configuration and review boundary |
| 2. Corrected calibration and historical skip interpretation | Corrected calibration, budgets and retries |
| 3. Requested budgets, max-turns limitation, authentication stop/recovery boundary, subscription limits/waits, and retained history | Opening result; Corrected calibration, budgets and retries |
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

DONE zeta subagent-pilot-3 freeze=none commitments=0 papers_in_T=0/26 targets=0 searches_ok=0/20 routes=0 status=blocked:authentication report=/home/dev/ara-work/reports/overnight/final3/report.html
