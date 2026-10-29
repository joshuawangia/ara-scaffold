
## Re-review round 5

Reviewed `feat/paper-extraction` at `4b94f8e4a1053661d6dc36e3ec6d8bbc2b8d6405`, against `be8c2c2ee2adaf491a8a31bb38640d40e287cebc`, in `/home/dev/ara-work/gamma`. Scope is the D4-B1 repair and the round-5 brief's explicit continuation-bound requirement. Solo, report-only review; no branch changes, implementation edits, delegation, network calls or paid generation. The negative-control runner temporarily mutates and restores production files as required. Historical review sections remain unchanged.

**Verdict: fix-first.** D4-B1's silent inventory loss is resolved, but the new expanding queue lacks the requested per-paper count and monetary bounds. Shared extraction/run budgets still protect total charged spending; they do not allocate a bounded continuation allowance to each paper. One blocking finding, no additional should-fix findings; full-run readiness remains **no**.

### Blocking finding D5-B1 — descendants bypass the only local continuation bound

**Priority: blocking for this brief and the full extraction run.** Locations: `ara/runtime/reconciliation.py:21`, `:44`, `:55`, `:69`, `:72`, `:87`; `ara/runtime/budget.py:98` and `:102`.

`reconciliation_context_requests` limits explicit context requests for one obligation. Its `requests` set resets for every queue entry. `turn` increments but is never compared with a ceiling. Every accepted response can resolve its supplied obligation and append a fresh `new_gaps` entry; the next obligation starts another traversal. Such a response does not need a context request. No total per-paper continuation count exists, and budget admission sums the whole extraction stage/run rather than a paper-specific allowance. Each descendant has a fresh identity and therefore a fresh prompt/cache key. Neither context fit nor cycle detection bounds this chain.

**Executed reproduction:** `uv run python /home/dev/ara-work/reports/delta-rereview5-probes.py` invokes production `extract` with the full extraction profile, a one-page placeholder paper, a network-forbidden mock provider, and synthetic counted usage. Initial extraction discovers Q. Each following response resolves its supplied ID using accepted evidence and discovers another Q under a distinct runtime identity. With `reconciliation_context_requests=0`, USD125 enclosing/extraction caps and a 12M token cap, **41 provider dispatches / 40 reconciliation calls** succeed; 40 discoveries and 40 resolutions are retained and literature is published. The probe stops inventing gaps after 40 solely to terminate the demonstration; production has no corresponding count check. Repeated equal descriptions are intentionally distinct, so deduplicating them would be the wrong repair.

A second run uses the same response generator and USD0.81 shared caps. It stops on the seventh attempted dispatch, after **6 dispatched responses, 6 discoveries and 5 resolutions**, with `BudgetStop: extraction cost cap: request reservation exceeds remaining cost`. Synthetic actual charges total USD0.0105; the next USD0.8005 reservation would exceed the cap. One pending ID remains auditable, a STOP/partial receipt is saved, and no literature is published. These are mock charges, not paid usage. This proves shared budget admission remains effective; it does **not** show unbounded dollar spending past a configured run cap. The defect is that a single paper can keep consuming the corpus allowance without an independent count or paper spending stop.

**Fix direction:** introduce validated finite per-paper continuation-count and monetary limits; enforce them before dispatch across graph review, ordinary evidence windows, explicit context requests and all descendant obligations. Count paid retry/correction attempts within the applicable allowance, retain the existing global reservation checks, and preserve accumulated discoveries/resolutions plus an explicit STOP identifying the paper and pending IDs when a local limit refuses. Do not discard gaps, merge descriptions, or mark coverage complete at the limit. Add a resolving-plus-new-gap chain regression that reaches the count limit while budget remains, a separate paper-budget refusal test, and a multi-paper test proving counters reset only at the paper boundary. Mutate each new guard and require red/restored-green receipts.

Own probe receipts: `delta-rereview5-probes.py`, `.json`, `.txt` in `/home/dev/ara-work/reports/`; the JSON links both complete event/cache/artifact directories.

### D4-B1 disposition — inventory loss resolved

The wire now separates `pending_obligation_ids` and structured `new_gaps`. `ara/runtime/calls.py:288` checks coverage consistency; `:338` requires every supplied ID to occur exactly once in the pending/resolved partition; `:344` requires nonempty resolution evidence drawn from accepted/current validated IDs. `ara/runtime/extraction.py:131` assigns source/window/turn/index IDs and appends discovery events without comparing description text.

`ara/runtime/reconciliation.py:55–60` appends every accepted continuation's new obligations to both cumulative inventory and the queue before processing the current resolution. This includes gaps returned while resolving an existing gap, and descendants of those gaps. At `:100–103`, exhausted windows refuse; successful publication requires the resolution-ID set to equal the entire accumulated inventory. Discovery/resolution events live in the existing hash-chained log; per-window snapshots preserve supplied/new obligations. The final cumulative obligations JSON is produced only after successful draining. A refusal's incomplete inventory is reconstructible from receipts even though no final ledger is published.

The eight direct parameterized regressions exercise discovery while pending or while resolving, equal or distinct descriptions, and either original-only refusal or both-resolved success. The ninth covers review-discovered gaps and multiple descendant generations. They assert counted admissions, four MODEL receipts in the direct cases, accepted evidence IDs, stable provenance IDs, immutable snapshots and absence of publication on refusal. The independent 40-generation probe also confirms distinct identities and complete retention for equal descriptions. Thus the original disappearing-R counterexample is repaired; it has not merely moved into a final merge check.

### Executed verification and mutation evidence

Full `uv run pytest`: **382 passed, 2 skipped / 384 collected**, exit 0, 247.91 seconds. The two skips are opt-in live checks. Receipt: `/home/dev/ara-work/reports/delta-rereview5-pytest.txt`. The new round-5 file contributed nine passing cases. Independent probe and saved-plan audits also exited 0 before mutation testing began.

Then `uv run python tests/integration/negative_controls.py`: **156/156 red, 156/156 restored green**, exit 0. No pytest/probe/plan audit ran concurrently with the mutation runner. Full receipt: `/home/dev/ara-work/reports/delta-rereview5-negative-controls.txt`; copied individual red/green traces and `results.json`: `/home/dev/ara-work/reports/delta-rereview5-controls/`. Both new controls failed with pytest exit 1 and restored with exit 0; their actual traces were read, not inferred from the summary.

After controls, `git status --short` was empty, `git diff --exit-code` passed, and HEAD remained `4b94f8e4a1053661d6dc36e3ec6d8bbc2b8d6405`. The previously accepted frozen T remained at SHA256 `25a7ec8c35d393b230738e6008467d70926697db6bed1f91c72b5edcd39cb3a4`; no new construction was performed.

Both new mutation definitions were read in `tests/integration/negative_controls.py:202–209`:

- `new_gap_inventory` changes the production ingestion argument from `ids, new_gaps)` to `ids, [])`, targeting the original-only refusal case `[False-2-R]`. Fresh red trace: `Failed: DID NOT RAISE Rejected` at `tests/runtime/test_extraction_round5.py:48` (0.42 seconds). Restored: 1 passed (0.52 seconds).
- `new_gap_queue` removes `queue.extend(new_obligations)`, targeting the both-resolved case `[True-2-R]`. Fresh red trace: `Rejected: unresolved obligation inventory at merge` from `ara/runtime/reconciliation.py:101`, reached by the positive test at line 45 (0.44 seconds). Restored: 1 passed (0.52 seconds).

These controls establish ingestion and processing independently. They do not cover a per-paper continuation limit; no such guard exists. Other than D5-B1, no regression was found in this narrow diff review and the executed checks. Passing offline tests certify structural accounting and refusal paths, not semantic sufficiency of the model-selected evidence.

### Free-plan confirmation and retained limits

Independently audited the saved round-5 free plan with `delta-rereview5-plan-audit.py` (network forbidden); receipt `.json` and full output `.txt` are alongside this report. Checked the log chain, actual PDF hashes, exact readable-page partitions, every range's saved count, context fit and arithmetic. No token-counter or generation service was called during this review.

- 26 PDFs; 1,379 physical / 1,368 readable pages; 66 initial ranges.
- 1,607,572 counted initial input tokens, 1,641,600 expected output tokens. Initial cost: `(1,607,572 × 5 + 1,641,600 × 25) / 1,000,000 = USD49.077860`.
- Saved graph-review scenario: 24 windows, 1,802,360 input and 196,608 output tokens. Cost: `(1,802,360 × 5 + 196,608 × 25) / 1,000,000 = USD13.927000`.
- Combined central scenario: **USD63.004860 ≈ USD63.00**. Full-output scenario: **USD89.049660**. Largest initial counted input plus output allowance: 67,030 / 200,000 tokens.
- 106 saved count events; zero generation starts, zero MODEL events, USD0 logged. Generation readiness is false; operator caps remain unset. Plan SHA256: `f8e8cd4211326fcf1f4f2723d5400583b47dabefbbaa842224fe53e0cb7a06be`.

Review-window density/output are estimates, not generated/count-verified graphs. Both scenarios exclude obligation traversal, descendant discovery, requested contexts, corrections, retries, construction and pilot search/writing. The newly retained gaps can add work precisely outside this central estimate. D4-N1/D4-N2 remain applicable: explicit profile composition, imported extraction charges consuming the pilot cap, 26 available PDFs out of 53 records, 82 affected pages, and unverified live fidelity/completion. No prior budget recommendation becomes authorization here. No paid usage was added or unknown reservation released; no live extraction, construction, pilot, or semantic-fidelity review was performed.

### Findings placement

| Finding/disposition | Placement in this section |
|---|---|
| D5-B1: missing per-paper continuation count/spend bounds | Blocking finding D5-B1; verdict |
| D4-B1: silent gap loss resolved, exact identities retained | D4-B1 disposition; mutation evidence |
| Updated USD63.00 plan and exclusions | Free-plan confirmation and retained limits |
| Offline proof limits and unchanged D4-N1/D4-N2 operational prerequisites | Executed verification; Free-plan confirmation and retained limits |

**4 findings, 4 placed.**

DONE delta rereview5 blocking=1 should_fix=0 tests=382/384 negctl=pass full_run_ready=no verdict=fix-first
