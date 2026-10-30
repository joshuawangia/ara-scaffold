
## Re-review round 6

Reviewed `feat/paper-extraction` at `ba3a004d422467a0aed8a77be9407587d265a514`, against `4b94f8e4a1053661d6dc36e3ec6d8bbc2b8d6405`, in `/home/dev/ara-work/gamma`. Scope: D5-B1, the new per-paper defaults, regression/mutation evidence, and migration of the proposed run configuration. Solo, report-only review; no implementation edits, branch changes, delegation, network calls, or paid generation. The required control runner temporarily mutated production files and restored them. Earlier report sections and the round-4 proposed config remain unchanged.

**Verdict: merge. D5-B1 is resolved; no blocking or should-fix findings remain in this review scope.** Full-run readiness is **yes for the configured, budgeted experiment**, with the disclosed partial-source policy and operator authorization still required before spending. This does not certify that every paper will finish within its allowance or that model extraction is semantically complete.

### D5-B1 disposition — one allowance covers the paper lifecycle

The native caller (`ara/runtime/extraction.py:315`) enters `ModelCalls.extract_paper`; `ara/runtime/calls.py:285–296` installs one `PaperAllowance` for the whole operation and clears only the active scope on exit. All extraction attempts pass through `_execute_once`, where context admission, enclosing budget admission, and paper admission precede provider dispatch (`calls.py:168–180`). Reviews, evidence windows, explicit context requests, descendant obligations, retries, targeted corrections, additional initial ranges and subdivision recovery therefore share the same allowance. There is no queue-specific bypass or new allowance per obligation. SDK retries remain disabled; the full profile disables model fallbacks.

`ara/runtime/extraction_budget.py:74–83` admits at most one initial attempt plus the configured continuation limit. Cache reads consume an attempt with zero new dollar reservation; free token-count/planning calls consume neither. Monetary admission includes initial/rejected/held charges and reserves the complete next counted request at the stage model's rates. `_after` checks actual cost after a durable MODEL receipt (`calls.py:243–246`, `extraction_budget.py:85–87`). Existing global accounting and STOP behavior remain in force. As before, an underestimated response can exceed a cap before its actual usage is known; the post-response guard then stops, retains the charge, and prevents publication. It cannot undo provider charges or infer unknown actual usage.

At `extraction_budget.py:39–51`, prior attempts and source-linked MODEL charges are reconstructed from the existing log. A new source gets its own count/cost baseline; returning to an old source recovers its prior usage, even through a new `ModelCalls` instance. The source ID comes from the runtime paper scope rather than model output. Clearing `_paper_budget` does not erase the persisted allowance.

At `extraction_budget.py:59–72`, STOP reconstructs outstanding accepted obligation IDs from discovery/resolution events and records the source, sorted pending IDs, attempts, continuations, paper spending and both limits. Both the reason and structured partial receipt identify the paper and pending IDs. A global budget stop is also enriched with this paper context by the lifecycle wrapper. Raw responses, immutable snapshots and accumulated history remain intact; no gap is discarded or declared resolved to meet a limit. A post-response actual-cost STOP retains the raw response but does not incorporate its new discoveries into accepted artifacts; pending IDs describe the accepted ledger, not unincorporated response content.

**Independent offline probes:** reran the prior 40-generation counterexample using the new full-profile defaults. It now refuses before dispatch 26, after **25 responses / 24 continuations**, USD0.04375 synthetic charges, 25 discoveries and 24 resolutions. STOP names `p` and `p:joined24:turn:24:gap:0`; no literature is published. Shared USD125 and paper USD15 allowances still have money available, proving that the count guard independently binds.

A separate USD0.8025 paper-cap probe refuses before dispatch 3 after USD0.0035 synthetic charges; the next USD0.8005 reservation would exceed the paper cap, while shared USD125 remains available. The low-global-budget probe still stops after six responses and now retains paper/pending-ID context in its final STOP/partial receipt. A further probe executes `p`, replays `p` from cache, reconstructs `ModelCalls`, executes `q`, then retries `p`: only two provider dispatches occur, the cached attempt consumes count, `q` starts with its own allowance, and re-entry to `p` refuses with two prior attempts and USD0.00175 paper cost versus USD0.0035 total cost. No reset occurs at a cache, queue, or object boundary.

Receipts under `/home/dev/ara-work/reports/`: `delta-rereview6-probes.py/.json/.txt` and `delta-rereview6-reentry.py/.json/.txt`. Their JSON records link the complete event/cache/artifact directories. All probe usage/cost is synthetic; sockets were blocked.

### Default sizing and proposed configuration

**The defaults are sound as finite experimental limits.** Independently recomputed the sizing from the saved round-5 plan and cost scenarios:

| Group | Allowed continuations / paper USD | Baseline count arithmetic | Full-output cost scenario | Remaining scenario headroom |
|---|---|---|---|---|
| Under 300 physical pages | 24 / USD15 | At most 4 initial ranges + 1 review − 1 initial attempt = 4 continuations | At most USD5.048850 | 20 continuations; USD9.951150 |
| At least 300 physical pages; current large source has 358 | 48 / USD30 | 16 initial ranges + 4 reviews − 1 initial attempt = 19 continuations | USD20.281665 | 29 continuations; USD9.718335 |

The large source's central scenario is USD15.570865, already above the ordinary USD15 cap; an explicit larger allowance is necessary for the intended baseline. The 300-page threshold is a physical-size rule, not a source-name exception. Near context capacity, `(168,000 × 5 + 32,000 × 25) / 1,000,000 = USD1.64` reserved per request, so dollars can bind before count. The headroom does not fund all allowed continuations at maximum size. Aggregate extraction/run caps still apply and are not increased by summing paper limits. Invalid counts and nonfinite/negative dollars, including unused override values, refuse before dispatch.

Created `/home/dev/ara-work/reports/delta-rereview6-config.proposed.yaml` from `delta-rereview4-config.proposed.yaml`, adding the three keys below to both the `extraction-full` and composed `pilot` profiles. All other parsed configuration values were asserted unchanged:

```yaml
extraction_paper_continuation_limit: 24
extraction_paper_cost_cap_usd: 15.0
extraction_large_paper_limits:
  min_pages: 300
  continuation_limit: 48
  cost_cap_usd: 30.0
```

Offline check: invoked native CLI profile loading for `extract --profile extraction-full` and `run --profile pilot`, intercepting the injected calls factory before provider creation or generation. Verified the resulting caps, extraction model/fallback policy, construction settings and writing allowances. Instantiated the production allowance for 299, 300 and 358 physical pages in both composed profiles. This checks configuration wiring and threshold selection; it is not an extraction or pilot completion test.

The proposal preserves USD125 / 12M extraction caps, USD350 / 30M pilot caps including imported extraction charges, the 32k construction catalogue and 100k working-input budget, and writer/audit/evidence/verification output allowances of 20k/24k/64k/48k. The proposal remains a configuration artifact for an authorized run, not authorization itself. The old file is preserved at SHA256 `3d93d44597db15e07708bba7d7cb4a5bb2bbf86646c1c438e80d751c3f8fb14a`.

Config/sizing check receipts: `delta-rereview6-config-check.py/.json/.txt`. No extraction prompt, response schema or range-planning change occurred in this commit, so reuse of the saved free plan is appropriate. Its central estimate remains **USD63.004860 ≈ USD63.00**, with full-output scenario USD89.049660 and plan SHA256 `f8e8cd4211326fcf1f4f2723d5400583b47dabefbbaa842224fe53e0cb7a06be`. Review density/output remain assumptions; obligations, descendants, requested contexts, corrections/retries, construction and pilot work remain outside those scenarios. No new count-service call was made.

### Executed verification and mutation evidence

Full `uv run pytest`: **414 passed, 2 skipped / 416 collected**, exit 0, **239.40 seconds**. The two skips are opt-in live checks; `test_extraction_round6.py` contributes 32 passing cases. Own probe, re-entry and offline-config checks also exited 0 before mutation testing began. Full receipt: `/home/dev/ara-work/reports/delta-rereview6-pytest.txt`.

After pytest and all independent source-dependent probes exited, ran `uv run python tests/integration/negative_controls.py` sequentially: **162/162 red, 162/162 restored green**, exit 0. Full receipt: `/home/dev/ara-work/reports/delta-rereview6-negative-controls.txt`. Copied all individual traces and `results.json` to `/home/dev/ara-work/reports/delta-rereview6-controls/`. No suite, probe or config check ran concurrently with mutation controls.

Read all six new mutation definitions in `tests/integration/negative_controls.py:211–230` and their actual red traces. The fresh independent run produced these failures, each followed by restored green:

| Mutation | Observed red behavior | What it establishes |
|---|---|---|
| `paper_continuation_cap` removes count admission | Expected `BudgetStop` did not occur | Descendants cannot bypass the paper count |
| `paper_reservation_cap` removes paper reservation admission | Expected `BudgetStop` did not occur | Shared remaining money cannot bypass paper USD admission |
| `paper_actual_cap` removes actual-cost stop | Expected `BudgetStop` did not occur | Measured overruns stop after retaining the response/charge |
| `paper_count_finite` removes count validation | Expected paper error instead became JSON infinity serialization error | Explicit finite/integer validation contract |
| `paper_dollars_finite` removes dollar validation | Expected paper error instead became JSON infinity serialization error | Explicit finite/nonnegative USD validation contract |
| `paper_boundary_cost` includes earlier papers' spending | Second paper incorrectly refused before its first dispatch | Monetary allowances reset for a different source |

The finite-value controls prove the configuration error boundary; they do not show a paid dispatch under mutation, since JSON serialization also rejects infinity. The suite additionally exercises retry/correction count and dollars, review/evidence/context kinds, multiple pending IDs, same-source re-entry, independent sources, unknown reservations, actual overruns and threshold selection. The old gap-retention controls remain green after restoration. No additional regression was found in this narrow review.

Final restoration checks: `git status --short` empty, `git diff --exit-code` and `git diff --check` passed, HEAD remained `ba3a004d422467a0aed8a77be9407587d265a514`. The prior 45-item frozen T remains SHA256 `25a7ec8c35d393b230738e6008467d70926697db6bed1f91c72b5edcd39cb3a4`. No new construction/freeze was performed.

### Remaining operating limits and findings placement

D4-N1/D4-N2 remain disclosed operating conditions, not new defects: explicit profile composition, imported extraction charges consuming the enclosing pilot cap, 26 available PDFs out of 53 records, 82 affected pages, and the intended `missing record-only` policy. Finite local limits may refuse a source while corpus budget remains; they neither skip the source nor automatically resume the collection. Structural/reference validation does not independently certify the semantic adequacy of selected evidence. No live extraction, construction, search, writing, or semantic-fidelity proof was run this round. This review added USD0 paid usage, released no prior reservation, and granted no new spend authorization.

| Finding/disposition | Placement in this section |
|---|---|
| D5-B1 resolved: count/USD bounds, STOP inventory, lifecycle persistence | D5-B1 disposition; independent probes; mutation evidence |
| Default sizing and external config migration | Default sizing and proposed configuration |
| Verification limits and retained partial-source/accounting prerequisites | Executed verification; Remaining operating limits |

**3 findings, 3 placed.**

DONE delta rereview6 blocking=0 should_fix=0 tests=414/416 negctl=pass full_run_ready=yes verdict=merge
