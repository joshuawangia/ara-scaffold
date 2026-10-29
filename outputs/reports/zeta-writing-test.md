# Zeta writing-stage test

**Blocked at writer validation: 0/2 routes written, 0 audits passed.** Both native selections exhausted four attempts below 4,500 words and exited 2. No attempt reached audit, evidence retrieval, originality/citation verification, or re-audit. No accepted draft or final essay exists. All eight rejected responses are preserved, clearly labelled, in gitignored `runs/`.

## Authorization and execution

Operator instruction **“Write C ... actually build all routes”** was recorded verbatim as native HUMAN `writing_authorization`, seq 8041, with the full writing brief and both route IDs. Each native selection also recorded its command and selected ID. The source run is `/home/dev/ara-scaffold/runs/codex-fork-3`.

Native `ara select` supports repeated selections from the same run. Both authorized historical CLOSED-derived routes were selected explicitly; current policy calls them CLOSED-single-paper. No fork or replay mechanism was invented. The commands were `ara select --run-dir /home/dev/ara-scaffold/runs/codex-fork-3 --route <ID> --codex-schema-preflight-log /home/dev/ara-scaffold/runs/codex-fork-5-schema-preflight/events.jsonl`.

Execution used clean detached revision `2ed9e21796bf55e1160bd6a22e1f0f459bb67436` in `/home/dev/ara-work/run-2ed9e21`. Its writing, audit, provider, CLI and export code matches main `9b9999730c32b4dd0f06ef80a075920633d1acc9`; the intervening change concerns search context. Both checkouts remained clean. No source edits, commits, construction, search, new schema proof calls, or new worker contexts were introduced.

Effective run settings: `codex_cli` / requested `gpt-6-luna`, high effort, no fallbacks, 4,500 minimum / 6,000 maximum words. The existing fork-5 schema proof passed native offline revalidation against the effective config and execution checkout. That proof binds the schema/transport manifest, not a Git revision. Child environments excluded Claude/API credential variables; the configured isolated Codex subscription transport ran its native canary for each selection. Both canaries passed. Serving-model identity remains unverified in all ten model receipts (F7); requested identity is not proof of serving identity.

## Route results

Counts use native `word_count`: every whitespace-separated token in title plus body, including markers, excluding bibliography. These are **rejected-attempt counts**, not counts of completed essays.

| Route | Rejected words, attempts 1–4 | First audit | Evidence | Originality / citations | Re-audit | Exit |
|---|---|---|---|---|---|---|
| `9a35a6febc9d:r0` | 3,179, 1,857, 2,892, 2,792 | NOT REACHED | NOT REACHED | NOT REACHED / NOT REACHED | NOT REACHED | 2 |
| `edd5e3e69fbe:r0` | 4,376, 1,590, 3,209, 3,617 | NOT REACHED | NOT REACHED | NOT REACHED / NOT REACHED | NOT REACHED | 2 |

Every rejection was `essay writer: minimum words not reached` (F1). Both commands emitted `runtime_error` with that message. There were zero `essay_audit`, `verification_cleanup`, or `final_draft` events in the writing intervals. No `draft.unverified.json`, `draft.json`, or `export/essay.txt` was created. The longest output, route 2 attempt 1, was 124 words short. No extra retry or hand repair was applied.

| Route | Process elapsed seconds | Native command seconds | Input tokens including canary | Output tokens including canary | Total tokens | Writer-only tokens | API USD |
|---|---:|---:|---:|---:|---:|---:|---:|
| `9a35a6febc9d:r0` | 615.57 | 587.60 | 25,919 | 18,781 | 44,700 | 39,432 | 0 |
| `edd5e3e69fbe:r0` | 618.65 | 587.42 | 25,911 | 21,642 | 47,553 | 41,509 | 0 |

Total new usage: **51,830 input + 40,423 output = 92,253 tokens** across 8 writer calls and 2 canaries. All ten actual receipts reconcile one-to-one with call IDs; zero cache hits, cache tokens, server tools, unsettled calls, unknown-usage receipts, Claude calls, or API spend in these intervals. Historical imported unknown usage was reconciled under the pre-existing count-at-reservation policy; it is not new writing usage. Summed process elapsed time was 1,234.22 seconds (20.57 minutes), excluding operator investigation and the gap between commands.

### Individual attempts and essay paths

No verified essay path is available. The links below are rejected JSON responses containing title/body/bibliography, not native successful exports. MODEL wall seconds are receipt measurements and include native accounting work; they are not isolated model latency.

| Route | Attempt | Words | Input | Output | MODEL wall seconds | Rejected response |
|---|---:|---:|---:|---:|---:|---|
| 1 | 1 | 3,179 | 5,400 | 5,107 | 80.17 | [attempt-1.rejected.json](/home/dev/ara-scaffold/runs/codex-writing-test-control/route1/attempt-1.rejected.json) |
| 1 | 2 | 1,857 | 5,398 | 3,120 | 56.17 | [attempt-2.rejected.json](/home/dev/ara-scaffold/runs/codex-writing-test-control/route1/attempt-2.rejected.json) |
| 1 | 3 | 2,892 | 5,398 | 5,096 | 80.32 | [attempt-3.rejected.json](/home/dev/ara-scaffold/runs/codex-writing-test-control/route1/attempt-3.rejected.json) |
| 1 | 4 | 2,792 | 5,396 | 4,517 | 73.42 | [attempt-4.rejected.json](/home/dev/ara-scaffold/runs/codex-writing-test-control/route1/attempt-4.rejected.json) |
| 2 | 1 | 4,376 | 5,397 | 6,534 | 81.27 | [attempt-1.rejected.json](/home/dev/ara-scaffold/runs/codex-writing-test-control/route2/attempt-1.rejected.json) |
| 2 | 2 | 1,590 | 5,395 | 2,649 | 58.54 | [attempt-2.rejected.json](/home/dev/ara-scaffold/runs/codex-writing-test-control/route2/attempt-2.rejected.json) |
| 2 | 3 | 3,209 | 5,397 | 4,871 | 77.63 | [attempt-3.rejected.json](/home/dev/ara-scaffold/runs/codex-writing-test-control/route2/attempt-3.rejected.json) |
| 2 | 4 | 3,617 | 5,397 | 5,869 | 80.14 | [attempt-4.rejected.json](/home/dev/ara-scaffold/runs/codex-writing-test-control/route2/attempt-4.rejected.json) |

## Defects and limitations

**F1 — All eight writer attempts failed length.** See Route results and Individual attempts. None satisfies the requested 4,500–6,000 words; no successful-entry essay exists.

**F2 — Writer retries repeat the prompt without validation feedback.** All four prompt hashes within each route are identical. Native `calls.py:294–311` explicitly excludes `write_essay` from adding validation feedback. Route 1 hash: `3c49748217f9833dfc4077f223e0558d71c3c5d4b02d5e16e2c37327f613e078`; route 2: `58849170b36df0a372c28c33d3ba3af3602902c4ba469425c3f9a1c9adb9a148`. Four native attempts were consumed on each route without communicating the measured shortfall. This behavior is observed; no repair was attempted.

**F3 — Codex evidence retrieval cannot complete this lifecycle, but the refusal was not exercised.** `CodexCLI.complete` rejects `search_evidence` with `stage_requires_api_provider` before launching a subprocess. `verify_originality_citations` calls that stage unconditionally, even with no bibliography or quotations. Both selections stopped earlier at writer validation. Therefore this test provides **no evidence that the first audit can pass**, and no evidence of completed originality/citation checks or re-audit. The lifecycle runs first audit before evidence, but reaches re-audit only after verification. No API or Claude substitution was made.

**F4 — The selected routes retain substantive limits.** Each uses two distinct supports from **one** paper and one licensed sign inference, below the acceptable-pilot requirement of at least two papers per route and at least three qualifying routes overall. Prior review found omitted support `gsv1996:r18-35:inf1`; the universal necessity claimed by route 1 and literature novelty/cross-paper contribution were not established. Route 2 likewise reuses the source’s explanatory example without independent novelty comparison. Writing authorization does not repair these limitations. The [fork-3 review](/home/dev/ara-work/reports/zeta-fork3.md) remains authoritative and is not provisional.

**F5 — Startup overhead and incomplete command timing.** First writer call_start was logged **227.47 s** and **219.53 s** after process launch. Native setup repeatedly reads/verifies the approximately 382 MB log and reconciles historical usage. Native command timings of 587.60 s and 587.42 s are recorded before the final methodology export, while complete subprocess times are 615.57 s and 618.65 s. Report both measurements; the native timing alone understates elapsed command time. This is measured overhead, not a profiled claim that every second came from log verification.

**F6 — Repeated selections reuse output paths, with a latent stale-export risk.** `compose` reuses draft filenames; `export_run` chooses the last `final_draft` anywhere in the log, without matching the latest selected route. A later failed selection following a successful one could therefore expose the earlier route’s essay. That scenario was **not exercised**: this run has zero final drafts and no exported essay. Per-route command byte intervals and rejected-response copies preserve attribution. Native per-route `ara export --output` was unnecessary because neither route yielded a final draft; the CLI refreshed its standard methodology on each failure.

**F7 — Served model identity is unverified.** All ten receipts request `gpt-6-luna` through Codex and report serving identity unverified. The transport and requested model are evidenced; the actual serving identity is not independently proven. See Authorization and execution.

## Artifacts, integrity, and handoff

- [Machine-readable results](/home/dev/ara-scaffold/runs/codex-writing-test-control/results.json): per-route totals, attempts, paths, timings, call reconciliation, original-file checks, and chain verdict.
- [Control notes](/home/dev/ara-scaffold/runs/codex-writing-test-control/notes.md): authorization, decisions, progress and final state. Adjacent files contain effective config, process IDs/exit codes, command arguments, and console logs.
- [Route 1 command interval](/home/dev/ara-scaffold/runs/codex-writing-test-control/route1/events.interval.jsonl): native sequences 8042–8074. [Route 2 interval](/home/dev/ara-scaffold/runs/codex-writing-test-control/route2/events.interval.jsonl): sequences 8075–8107. These are extracted evidence slices, not standalone authenticated run logs; authenticate against the original log/anchor.
- [Native methodology](/home/dev/ara-scaffold/runs/codex-fork-3/export/methodology.md): refreshed by native CLI through the final command timing event. It retains full history, model prompts/responses and HUMAN actions. It has not been certified anonymised or submission-ready.
- [Native event log](/home/dev/ara-scaffold/runs/codex-fork-3/events.jsonl) and adjacent anchor: native verification passed after both commands. Event count rose from 8,041 to 8,108. All 17 pre-writing file/prefix hashes match, including frozen artifacts, route artifacts, original log prefix and original anchor prefix. The original evidence was appended to, not rewritten.

All essay response bodies remain in gitignored `runs/`. Both checkouts are clean, both supervisors exited, and no ARA select/Codex child remains. No source-code tests were needed or run for this operational test; verification used actual native executions, native word counts, chain validation, hash checks, and call accounting. Approximately 1.1 GiB disk remains.

The successful-entry criteria are not met: no length-valid essay, no passed audits or originality/citation checks, no certified anonymised submission package, and no submission. Next unresolved steps are writer length/retry repair and a Codex-compatible evidence path; neither is silently bypassed or started by this brief.

Finding placement: F1 → Route results and Individual attempts; F2, F3, F5, F6 → Defects and limitations; F4 → Defects and limitations plus linked historical review; F7 → Authorization and execution and Defects and limitations. **7 findings, 7 placed.**
