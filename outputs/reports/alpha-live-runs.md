# Alpha live runs

Repository: `/home/dev/ara-scaffold`, branch `main`, revision `5998c90b990b843ce4da111bbddfa04f7080ca6b`. Tracked tree clean at start and delivery; no tracked edits made. Read AGENTS.md, README.md, PLAN.md and DECISIONS.md, including series-4 failure and the 90%-of-maximum writer fix.

Authorization: five live smoke runs (USD 5 cap each). The original one-pilot authorization (USD 100 cap) is now ON HOLD under the brain’s updated instruction. Stop series above USD 3 for any run or at two failures; stop on an exposed defect. No extra paid runs, philosophical contributions, named position, audience override, or human route selection supplied.

## Smoke table

Words use ARA `word_count`: whitespace tokens in title and body, including markers, excluding bibliography. Accepted final draft counts must be 150–300. Both audit verdicts are code-computed `faithful`; acceptance does not prove semantic equivalence.

| Run | Exit | Final words / 150–300 | Writer attempts (counts) | Audit 1 / 2 | Essay / methodology export | USD | Wall seconds | Serving models | Fallback / refusal |
|---|---:|---|---|---|---|---:|---:|---|---|
| [1](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl) | 0 | 258 | 1 (258) | PASS (live) / PASS (live) | yes / yes | 1.604035 | 290.809 | claude-opus-5 | 0 / none |
| [2](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl) | 0 | 279 | 1 (279) | PASS (live) / PASS (cached) | yes / yes | 1.483260 | 254.541 | claude-opus-5 | 0 / none |
| [3](/home/dev/ara-scaffold/runs/series-5/run-3/events.jsonl) | 0 | 269 | 1 (269) | PASS (live) / PASS (cached) | yes / yes | 1.171805 | 190.790 | claude-opus-5 | 0 / none |
| [4](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl) | 0 | 248 | 1 (248) | PASS (live) / PASS (cached) | yes / yes | 1.372725 | 236.453 | claude-opus-5 | 0 / none |
| [5](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl) | 0 | 245 | 2 (1, 245) | PASS (live) / PASS (live) | yes / yes | 1.427505 | 244.504 | claude-opus-5 | 0 / none |

### Cache isolation and native event references

Each run gets an initially absent cache `runs/series-5/cache-<i>` through its own `config-<i>.yaml`; only `cache_dir` differs from shipped config. [revision.json](/home/dev/ara-scaffold/runs/series-5/revision.json) records the starting revision and empty-cache check. All artifacts remain gitignored. Every cache hit is checked against a preceding accepted live MODEL event with the identical cache key in that same run; `cache_origin_proof` records both line numbers. No earlier-run cache is available. Native event chains and anchors are verified by ARA `EventLog.read`. MODEL line numbers below are one-based file lines (event `seq` is one less).

| Run | MODEL records | Live (`cache_hit=false`) | Same-run hits (`true`) | Cache-hit lines | Writer / audit / final / timing lines |
|---|---:|---:|---:|---|---|
| 1 | 55 | 46 | 9 | [L46](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:46), [L100](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:100), [L124](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:124), [L132](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:132), [L135](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:135), [L136](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:136), [L142](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:142), [L144](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:144), [L154](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:154) | [writer 1](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:177); [audit 1](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:182); [audit 2](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:190); [final](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:192); [timing](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:194) |
| 2 | 66 | 53 | 13 | [L27](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:27), [L40](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:40), [L53](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:53), [L57](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:57), [L90](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:90), [L102](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:102), [L160](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:160), [L176](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:176), [L184](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:184), [L187](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:187), [L188](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:188), [L194](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:194), [L230](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:230) | [writer 1](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:220); [audit 1](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:222); [audit 2](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:229); [final](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:231); [timing](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:233) |
| 3 | 48 | 40 | 8 | [L46](/home/dev/ara-scaffold/runs/series-5/run-3/events.jsonl:46), [L102](/home/dev/ara-scaffold/runs/series-5/run-3/events.jsonl:102), [L127](/home/dev/ara-scaffold/runs/series-5/run-3/events.jsonl:127), [L135](/home/dev/ara-scaffold/runs/series-5/run-3/events.jsonl:135), [L138](/home/dev/ara-scaffold/runs/series-5/run-3/events.jsonl:138), [L139](/home/dev/ara-scaffold/runs/series-5/run-3/events.jsonl:139), [L145](/home/dev/ara-scaffold/runs/series-5/run-3/events.jsonl:145), [L182](/home/dev/ara-scaffold/runs/series-5/run-3/events.jsonl:182) | [writer 1](/home/dev/ara-scaffold/runs/series-5/run-3/events.jsonl:172); [audit 1](/home/dev/ara-scaffold/runs/series-5/run-3/events.jsonl:174); [audit 2](/home/dev/ara-scaffold/runs/series-5/run-3/events.jsonl:181); [final](/home/dev/ara-scaffold/runs/series-5/run-3/events.jsonl:183); [timing](/home/dev/ara-scaffold/runs/series-5/run-3/events.jsonl:185) |
| 4 | 57 | 44 | 13 | [L24](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:24), [L55](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:55), [L115](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:115), [L140](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:140), [L145](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:145), [L147](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:147), [L150](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:150), [L151](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:151), [L154](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:154), [L156](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:156), [L158](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:158), [L162](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:162), [L207](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:207) | [writer 1](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:197); [audit 1](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:199); [audit 2](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:206); [final](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:208); [timing](/home/dev/ara-scaffold/runs/series-5/run-4/events.jsonl:210) |
| 5 | 57 | 48 | 9 | [L49](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:49), [L61](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:61), [L67](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:67), [L117](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:117), [L142](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:142), [L150](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:150), [L153](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:153), [L154](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:154), [L160](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:160) | [writer 1](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:187); [writer 2](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:190); [audit 1](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:195); [audit 2](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:203); [final](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:205); [timing](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:207) |

Every MODEL record is enumerated in each `run-<i>.summary.json` (`model_lines`, `by_kind`, `cache_origin_proof`), alongside the untouched native JSONL. Exit status, UTC start/end and external wall time are in `run-<i>.execution.json`; console output is in `run-<i>.console.log`. These receipt files are under /home/dev/ara-scaffold/runs/series-5.

## Pilot up to selection

**ON HOLD — not started.** The brain's updated instruction is to finish Task 1, send its smoke DONE line, then wait. The operator requires per-paper extraction now being built by gamma. Beta's file arrived, but its presence no longer authorizes starting the pilot. No pilot cost, calls, routes, selection, or retrieval occurred. Pilot cost/time are zero because no pilot command was run.

Original requested input: `runs/inputs/epistemic-modals-literature.txt`. Observed beta file: 13,435 bytes, SHA-256 `c5d822011ffa24d2aeb687d8f3cff567a3f25c7ee80aed3a979045163182c872`. This is provenance only, not approval to use it for a pilot. Await the brain's revised input/instructions.


## Cost and time

USD below sums native MODEL `cost_usd` including rejected responses; native command time comes from `command_timing`. External wall time includes CLI startup. Configured-price accounting is not invoice reconciliation.

| Run | Recorded USD | Native command seconds | Model-call seconds | External wall seconds |
|---|---:|---:|---:|---:|
| smoke 1 | 1.604035 | 290.070 | 284.621 | 290.809 |
| smoke 2 | 1.483260 | 253.619 | 246.577 | 254.541 |
| smoke 3 | 1.171805 | 189.834 | 184.139 | 190.790 |
| smoke 4 | 1.372725 | 235.473 | 228.571 | 236.453 |
| smoke 5 | 1.427505 | 243.584 | 237.407 | 244.504 |
| smoke total (5 completed) | 7.059330 | 1212.580 | 1181.315 | 1217.098 |

## Anomalies and findings

- Smoke 1 `formalise` attempt 1: ValidationError ([L146](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:146)). Status `rejected`; retained in total cost.
- Smoke 1 `audit_essay` attempt 1: ValidationError ([L179](/home/dev/ara-scaffold/runs/series-5/run-1/events.jsonl:179)). Status `rejected`; retained in total cost.
- Smoke 2 `build_t` attempt 1: ValidationError ([L4](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:4)). Status `rejected`; retained in total cost.
- Smoke 2 `formalise` attempt 1: ValidationError ([L29](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:29)). Status `rejected`; retained in total cost.
- Smoke 2 `formalise` attempt 1: ValidationError ([L42](/home/dev/ara-scaffold/runs/series-5/run-2/events.jsonl:42)). Status `rejected`; retained in total cost.
- Smoke 5 `formalise` attempt 1: ValidationError ([L16](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:16)). Status `rejected`; retained in total cost.
- Smoke 5 `write_essay` attempt 1: ValidationError ([L187](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:187)). Status `rejected`; retained in total cost.
- Smoke 5 `audit_essay` attempt 1: ValidationError ([L192](/home/dev/ara-scaffold/runs/series-5/run-5/events.jsonl:192)). Status `rejected`; retained in total cost.

Run 1 and run 5 audit retries corrected sentence-inventory mismatches, not adverse semantic verdicts. Formalisation rejections were empty atom names (run 1 also nested under double negation); run 2 build-T rejected an empty citation. Run 5 writer rejected an empty body before the length checker; its one counted word belongs to the title. The successful retry sent an identical prompt and cache key. These details are derived from the rejected native responses and subsequent validation-feedback call inputs.

Same-run cache hits are disclosed above; all five caches are isolated from earlier runs. The smoke uses placeholder literature and is not evidence of successful substantive pilot composition. The pilot has not been started.

## Work notes

Completed smoke receipts: 5/5. Current revision remains the requested revision. Next unresolved step: wait for the brain; do not start the pilot (Task 1 complete). Preserve every native log, anchor, console log and accounting receipt; do not repair defects or select routes.




## Delivery verification and finding placement

[Final verification receipt](/home/dev/ara-scaffold/runs/series-5/final-verification.json) confirms the requested revision, clean tracked tree, all five native hash chains and anchors, matching configurations, balanced dispatch/completion accounting, and no pilot directory. Verification made no provider calls.

| Finding | Result and placement |
|---|---|
| 1. Smoke outcome and length | **5/5 passed**; final counts 258, 279, 269, 248, 245; writer attempt counts were 1, 1, 1, 1, 2; both audit stages and exports passed. See **Smoke table**. This is short placeholder-run evidence, not pilot completion. |
| 2. Live-call/cache scope | 231 paid live model responses and 52 same-run cache hits; each hit has a prior accepted live origin. Second audit used cache in runs 2, 3, 4; these are validated cached verdicts, not additional independent provider assessments. See **Cache isolation and native event references**, **Smoke table**, and per-run `audit_receipts`/`cache_origin_proof`. |
| 3. Validation retries | 8 malformed responses were rejected and corrected by native bounded retries, all retained and charged. Every individual rejection is listed in **Anomalies and findings**. Run 5 writer attempt 1 had an empty body (one counted title word) and failed the body minLength schema constraint; its identical-input retry passed at 245 words. No terminal rejection occurred. |
| 4. Serving and refusal evidence | All responses served by `claude-opus-5`; no fallback hop or refusal. Live fallback behavior remains unexercised. See **Smoke table** and per-run `served_models`/`fallback_calls`/`rejections`. |
| 5. Spend and stop thresholds | USD **7.059330** total; 20.285 minutes summed external run time. Every run below USD 3; no failures or unknown-accounting reservations. See **Cost and time**. |
| 6. Pilot hold | No pilot run, cost, route selection, or retrieval. Await the brain’s revised per-paper extraction/input instructions. See **Pilot up to selection**. |
| 7. Source and evidence preservation | Requested commit unchanged; tracked tree clean; all logs/anchors/exports/failed attempts kept in ignored runs. See opening provenance, **Cache isolation and native event references**, and this section’s final receipt. |

7 findings, 7 placed.
