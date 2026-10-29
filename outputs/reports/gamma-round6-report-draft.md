## Round 6

**D5-B1 repaired; awaiting independent review.** Base: `4b94f8e4a1053661d6dc36e3ec6d8bbc2b8d6405`. Final revision: `ba3a004d422467a0aed8a77be9407587d265a514` on `feat/paper-extraction`. Scope is only the round-6 brief and Delta's D5-B1 continuation-bound finding. Solo execution, no push, no network requests or paid generation.

### D5-B1: paper-wide admission and retained queue

A `PaperAllowance` wraps the native `extract_paper` lifecycle and is enforced by the shared model-call boundary. It applies to every extraction attempt, so graph reviews, ordinary evidence windows, explicit requested contexts, descendant obligations, validation retries and targeted corrections cannot acquire fresh allowances. The count is deliberately conservative: every request after the first counts as a continuation, including additional initial ranges and subdivision recovery. Cached response attempts consume count allowance but reserve USD0; free token-planning calls are not model attempts. SDK generation retries remain disabled, and extraction-full still disables model fallbacks.

Before each dispatch, the existing enclosing/stage reservation checks and the paper count/USD checks must all pass. The monetary allowance includes the initial response, all later responses, rejected attempts, and held unknown-usage reservations. It uses the requested stage model for reservation and the existing measured/served-model accounting for actual charges. Actual paper cost is checked again after a durable response/usage receipt. Both count and USD limits are validated as finite and nonnegative before paper work, including unused large-paper override values; counts must be integers.

Each attempt has a paper-specific receipt, and MODEL events carry the trusted paper source ID from the runtime scope. Re-entering the same paper recovers its prior attempt count and charges from the log, so restarting that method does not reset its allowance. A different source receives a separate allowance while total costs remain charged to the shared extraction/run caps. The first paper's costs therefore cannot consume the second paper's local allowance, and moving between obligations cannot reset any allowance.

A local refusal emits `BudgetStop` before the next dispatch. Its STOP event and partial JSON name the source and every pending accepted obligation ID, as well as attempts, used continuations, paper cost, and both limits. Pending IDs are reconstructed in event order from append-only discoveries and resolutions. Global budget stops within extraction receive the same paper context. Existing range/window snapshots, full model responses, charged/held usage and accumulated discoveries/resolutions survive. No gap is merged by text, discarded, or declared complete at a limit; no literature artifact is published on refusal.

A response received immediately before an actual-cost STOP remains in raw/usage receipts; the budget refusal prevents incorporating it into a paper artifact. Pending IDs reflect the accepted obligation history rather than invented entries from a response whose paper processing did not complete. Actual-cost checking detects an underestimate after the charge has occurred; it cannot undo provider charges or establish the actual value of an unknown reservation. There is still no automatic collection resume or live semantic-coverage guarantee.

### Defaults and free-plan arithmetic

The defaults are explicit in `extraction-full` and justified in `DECISIONS.md` GX29. Ordinary configurations without explicit paper settings also receive finite 24/USD15 defaults. The larger allowance is an explicit full-profile override based on physical-page count, with no source-name special case.

Any external proposed run configuration copied before this commit must copy these new profile keys, including `extraction_large_paper_limits`, before using the intended larger allowance. In particular, `/home/dev/ara-work/reports/delta-rereview4-config.proposed.yaml` was checked read-only and lacks all three new paper-limit keys; it was not edited here. An old configuration without the keys receives the finite 24/USD15 fallback for every source, so the large source can refuse even within its saved baseline cost scenario. This is a configuration-composition prerequisite, not permission to increase enclosing caps.

| Paper group | Continuation ceiling | Per-paper USD ceiling | Saved-plan basis |
|---|---:|---:|---|
| Under 300 physical pages | 24 | 15 | At most 4 initial ranges + 1 estimated review window = 4 continuations; largest full-output scenario USD5.048850 |
| At least 300 physical pages | 48 | 30 | The 358-page source: 16 initial ranges + 4 estimated review windows = 19 continuations; expected-output-with-review USD15.570865; full-output scenario USD20.281665 |

The ordinary ceiling leaves twenty continuation attempts beyond that planned maximum. The large ceiling leaves twenty-nine beyond its baseline scenario; USD30 leaves USD9.718335 beyond its full-output scenario. At USD5/M input and USD25/M output, a near-context request with 168k input plus 32k output reserves USD1.64, so the dollar ceiling may bind before the count ceiling. The count ceilings do not promise that every allowed request can be funded. These are finite experiment limits, not a forecast or authorization to spend; all enclosing extraction-full caps remain null.

The round-5 free plan is unchanged: neither the extraction prompt/schema nor range planner changed. No new token-counter call was needed. Sizing receipt: `runs/gamma-round6/sizing.json`, pinning plan SHA256 `f8e8cd4211326fcf1f4f2723d5400583b47dabefbbaa842224fe53e0cb7a06be`. It covers 26 PDFs, 1,379 physical / 1,368 readable pages, 66 initial ranges and 1,607,572 counted initial input tokens. Initial expected-output cost remains USD49.077860; adding the estimated no-obligation review gives USD63.004860; the corresponding full-output scenario remains USD89.049660. The 24 review windows and their graph/output densities remain estimates, not generated evidence. Obligation traversal, descendants, contexts, retries/corrections, construction and pilot work remain outside these scenarios.

### Executed verification and its limits

The three requested regressions failed before implementation: the descendant chain and paper-dollar cases did not stop, and the multi-paper case had no paper attempt accounting. Receipt: `runs/gamma-round6/regressions-before.txt`. They then passed through native `extract` with retained receipts (`regressions-after.txt`, `core-proof/`). The count test stops after one initial plus three continuations while shared and paper money remains; the dollar test accepts two measured responses and refuses the next full reservation; the multi-paper positive case accepts three responses independently for each of two sources while preserving the shared total.

The expanded tests cover count and dollar consumption by retries/corrections, all continuation kinds, multiple pending IDs in STOP, same-paper re-entry count and cost persistence, independent source allowances, retained unknown-usage reservation, actual-usage overrun, invalid/nonfinite limits, and the 299/300/358-page profile threshold. The affected run passed **93 tests** in 32.29 seconds. A preliminary command named a nonexistent `test_budget.py` and collected no tests; its error receipt is retained as `targeted-first.txt`, not counted as verification. Subsequent correct commands/results are retained separately.

Full `uv run pytest --basetemp=runs/gamma-round6/pytest-proof`: **414 passed, 2 skipped / 416 collected**, exit 0, **263.27 seconds**. Receipt: `runs/gamma-round6/pytest-final.txt`. After pytest exited, `uv run python tests/integration/negative_controls.py`: **162/162 red, 162/162 restored green**, exit 0. Full runner receipt: `runs/gamma-round6/negative-controls-final.txt`; individual traces and results: `runs/gamma-round6/controls/`. All seven committed file hashes exactly match the pre-gate tested-tree snapshot in `runs/gamma-round6/verified-tree-inputs.json`; the working tree is clean and `git diff --check` passes. Final verification: `/home/dev/ara-work/reports/gamma-round6-verification.json` (also retained under `runs/gamma-round6/verification.json`).

Six new production mutations and their observed red behavior:

| Control | Mutation | Observed failure |
|---|---|---|
| paper_continuation_cap | Removes per-paper count admission | Expected BudgetStop does not occur |
| paper_reservation_cap | Removes paper USD reservation admission | Expected BudgetStop does not occur |
| paper_actual_cap | Removes measured paper-cost stop | Expected BudgetStop does not occur |
| paper_count_finite | Removes integer/finite count validation | The explicit paper configuration error disappears; invalid infinity reaches JSON serialization instead |
| paper_dollars_finite | Removes finite/nonnegative USD validation | The explicit paper configuration error disappears; invalid infinity reaches JSON serialization instead |
| paper_boundary_cost | Counts the prior paper's spend against the next paper | Multi-paper positive case incorrectly stops before the second source's first dispatch |

The finite-value mutation controls prove the explicit validation/error contract; they do not claim those mutations dispatched a paid request, since JSON serialization also rejects infinity. The other controls distinguish missing local admission/actual stops and improper cross-paper accounting. Every restored counterpart passed. No pytest suite was run concurrently with mutation controls. All offline providers are network-forbidden and their dollar receipts are synthetic.

Inline simplification/manual diff review reused the existing accounting, log and STOP paths; the separate allowance owns paper scope rather than duplicating provider pricing or changing reconciliation queue logic. No further simplification was justified, and proof tests were retained. There is no configured lint/typecheck command. **Code review: skipped (ce-code-review unavailable).** The skill requires an independent reader for this money-boundary change, which the solo restriction prevents. No independent review or live extraction/model fidelity is claimed; Delta review remains the next gate.

### Retained operating limits and accounting

D4-N1/D4-N2 remain applicable: explicit pilot-profile composition, imported extraction charges consuming the enclosing pilot cap, and partial-source handling. The inventory is still 26 available PDFs out of 53 records. Its 82 affected pages across seven sources include one unread page and 81 retained encoding warnings; ten blank pages explain the remaining physical/readable difference. The intended full run still requires the disclosed `missing record-only` policy. Counted fit does not establish correct glyph interpretation, text order, complete argument coverage or successful live continuation.

The new per-paper limits may stop one expensive source while aggregate corpus budget remains. That is an explicit refusal with receipts, not automatic skipping, semantic deduplication, budget escalation or a guarantee of corpus completion. Enclosing budgets and the prior full-run approval prerequisites remain unchanged. No paid generation, construction, freeze, search or writing was executed this round; no credentials were loaded or exposed.

This round adds USD0 paid usage and no network count calls. Prior accounting remains **USD5.461870 measured + USD3.934240 held unknown = USD9.396110 accounted**, with build campaign **USD5.433360 of USD6**. No earlier failed receipt or unknown reservation was released. The accepted 45-item freeze retains SHA256 `25a7ec8c35d393b230738e6008467d70926697db6bed1f91c72b5edcd39cb3a4`.

### Findings placement

| Finding | Deliverable placement |
|---|---|
| D5-B1 missing per-paper admission limits | D5-B1: paper-wide admission and retained queue |
| Count semantics, finite defaults, large-paper arithmetic and old external config migration | Defaults and free-plan arithmetic |
| STOP inventory, re-entry/cost persistence, actual and unknown usage limits | D5-B1: paper-wide admission and retained queue; Executed verification and its limits |
| Test/control evidence, failed command disposition and independent/live review limits | Executed verification and its limits |
| Reused free-plan counts, cost exclusions and retained D4-N1/D4-N2 prerequisites | Defaults and free-plan arithmetic; Retained operating limits and accounting |
| No spending/network calls, preserved campaign reservations and freeze | Retained operating limits and accounting |

**6 findings, 6 placed.**

DONE gamma round6 head=ba3a004d422467a0aed8a77be9407587d265a514 tests=414/416 negctl=pass fixed=D5-B1 status=awaiting-review
