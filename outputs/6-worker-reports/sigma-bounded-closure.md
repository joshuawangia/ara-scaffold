# Sigma — bounded prerequisite closures

Worktree `/home/dev/ara-work/sigma`, branch `fix/bounded-closure`, based on `1d832b24805536b46e6974ca97842cffe0458e3a`. Implementation is local; no push, delegation or paid generation. Final local commit: `5009af1e053d11dac18405fe7402331134585fea`. The worktree is clean; independent non-author review is next.

## Result and causal account

At the base revision, native construction selected roots before knowing their closure costs or any per-window allocation. Zeta part 4 selected 182 items and reached 73,902 formalization input tokens against 70,000 before any formalization or freeze. Independent catalogue/cumulative-copy guards meant raising that one bound would only move the failure.

Construction v7 now allocates global working/copy/catalogue capacity before selection. The same native planner powers `ara plan-construction`; its count-only provider refuses generation and its token/spend caps are zero. Each model-facing root has its complete directional closure item count and a conservative counted UTF-8 payload token bound. The model still chooses relevance and roots. Code then retains the deepest complete prerequisite layer that fits the item, payload, exact copied-envelope and exact formalization-request limits. All incoming qualifiers/distinctions and every included inference's stated endpoints remain mandatory. A mandatory bundle that cannot fit contributes nothing, with a reason; an entirely empty T still refuses.

Cut frontier commitments retain their exact source citation and attributed text, prefixed with `assumed_premise; support_omitted` and omitted direct support IDs. Original rich source bodies are unchanged. Uncut inventories, every budget/relevance omission and cut depth remain in receipts; the formalizer receives compact included inventory, existing exact formulas/source context, and explicit omitted-support edges. The final ledger records budget-cut reasons rather than preliminary relevance reasons for cut items. Methodology discloses conditional premises and each omitted-support edge. Later overlap reuses an earlier commitment unchanged, preserving its conservative assumption marker even if supporting material is later included.

Actual accepted working output and catalogue growth must fit each window's share as well as existing global limits. This prevents one window consuming the later windows' allocations. One native construction lifecycle, one merge and one freeze remain; no source inference becomes an engine license.

Inspected owning paths: `construction.construct`, `evidence_dependencies`, `prerequisite_closure`, `evidence_window`, `ModelCalls.count_request`, `prepare_commitments`, `export.methodology`, `planning.CountingProvider`, CLI and owning tests. New deterministic arithmetic/depth-cut helpers live in `closure_budget.py`. This extends the native path; it does not introduce a parallel construction engine.

## Real literature plan and arithmetic

Artifact: `/home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt`, SHA-256 `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`. It contains 26 published papers and 5,296 eligible items. The plan uses Zeta part 4's ignored config, unchanged, with its pilot profile and explicit empty audience. Provider measurements use the free Anthropic count endpoint; this is no-generation verification, not a network-free tokenizer run.

Final count command (run from the task worktree with the repository-documented existing credential sourced only into the process environment):

```sh
uv run ara plan-construction --profile pilot \
  --config /home/dev/ara-scaffold/runs/inputs/overnight-pilot-4-config.yaml \
  --topic 'epistemic modals' \
  --literature /home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt \
  --audience '' --token-counter provider --run-dir runs/sigma-plan-final
```

Final provider-counted result: 48 windows, 3 commitments/window, upper allocation 144 commitments; copied-envelope mean rounded up to 204 tokens/commitment; minimum symbol/formula-growth reservation ceil(10,471 / 45) = 233, overriding the inherited 128 planning assumption; empty working envelope 3,232. Reserve 20% working/catalogue headroom. The arithmetic is min(floor((80,000−3,232)/(204+233)), floor(38,400/233)) = min(175,164) = 164 global slots; floor(164/48) = 3/window, or 144 allocated slots. Projected working envelope 3,232 + 144×437 = 66,160; projected catalogue 144×233 = 33,552. The batch allowance min(70,000,200,000−64,000−48,000) remains 70,000.

| Admission or projection | Tokens | Bound |
|---|---:|---:|
| Largest planned initial window input | 67,613 | 70,000 batch |
| Largest window + 64,000 output + 48,000 catalogue reservation | 179,613 | 200,000 context |
| Projected working T, including wrapper and formula-growth reserve | 66,160 | 80,000 after headroom; 100,000 configured |
| Projected catalogue | 33,552 | 38,400 after headroom; 48,000 configured |
| Per-window new working allocation | 1,599 | 76,768 available / 48 |
| Per-window new catalogue allocation | 800 | 38,400 available / 48 |

The new metadata/counting leaves 48 windows versus the old 46; quotas use the actual 48. The maximum above is an admitted planned window, not an oversized diagnostic packing probe. Final log/anchor verification covered 340 records, no MODEL events or call_start dispatches, and zero recorded cost. All seven artifact/admission/accounting checks passed. Evidence under `/home/dev/ara-work/sigma/`: `runs/sigma-plan-final/{construction-plan.json,events.jsonl,events.anchor}`, and `runs/sigma-evidence/real-plan-verification.json`. Final plan SHA-256: `4410649ff537d1b09e582dae78cb9ca1b91da0ca8b055dcdbdd9f71a53e404ef`. This is the final prompt count; the first diagnostic pass is not substituted for it.

The structural candidate census, using the native depth cut at three items and the payload bound, finds 3,593 candidates with full closures fitting, 844 requiring cuts, and 859 whose mandatory bundles are too large. Every paper has some structurally fitting candidate. This is before exact per-window copy/request checks and makes no relevance or semantic quality claim. Evidence: `runs/sigma-evidence/candidate-census.json`.

## Verification

Executed targeted final cut/ledger/window checks: 16 passed. Broader targeted run: 76 passed plus one legacy late-refusal test whose injection was moved after the new early cut check; its updated test and exact-bound cutting regression then passed. Two exploratory full-suite runs were interrupted for final fixes and are not counted as completed verification.

The first completed full run found one legacy 53-paper fixture that still selected all 424 items: 623 passed, one failed, two skipped. Its placeholder selection was updated to respect the real allocation while preserving full selected/omitted inventory, replay and native single-freeze proof; the targeted repair passed in 121.69 seconds. Final `uv run pytest -q`: **624 passed, 2 skipped in 264.30 seconds** (626 collected). The two skips are opt-in live tests. After pytest exited zero, `uv run python tests/integration/negative_controls.py` started alone; all **280/280 mutations failed their targeted tests and all 280 restorations passed**. The combined sequential command exited zero. The runner includes new mutations for empirical symbol reservation, global window division, required qualifiers, omitted support IDs, frozen-text assumption markers, methodology disclosure, working/symbol output shares, exact request cutting and zero-root windows. Source was restored after each mutation; no pytest suite ran alongside mutations. All 280 anchors were validated before running. `git diff --check` passed, and the committed worktree is clean.

Final proof copies are in `/home/dev/ara-work/reports/sigma-evidence/`: `pytest-final.txt`, `controls-console.txt`, `controls/results.json`, all 560 individual mutation/restoration outputs, `construction-plan.json`, `real-plan-verification.json`, `candidate-census.json`, and `final-verification.json`. `manifest.json` records SHA-256 and size for all 569 evidence files. Native full count prompts, chain and anchor remain in the task worktree. These are executed results; no live test is represented as passed.

## Scope and remaining gaps

- The allocation is an upper capacity projection, not a prediction that 144 commitments will be selected. Root relevance, model fidelity, semantic symbol alignment, actual formulas and actual downstream search remain unexecuted; non-author review follows this handoff.
- Candidate payload costs use explicit conservative UTF-8 byte token bounds, not exact provider tokenization of each of the 5,296 closures. Complete planning windows and actual cut/formalization requests use the provider counter. The local CLI option is explicitly byte/4 estimation and is not the real-plan evidence.
- Exact output and retry admission can still refuse unexpectedly large model output. The change prevents capacity theft and cuts oversized fixed inventories; it does not promise model compliance or silently retry/relax budgets. All global guards remain.
- Formalization chunking is deferred under the brief's optional/cheap condition. Bounded fixed inventories are counted before dispatch. Splitting arbitrary cyclic dependency graphs with correction/symbol receipts is additional scope.
- No real construction, freeze, search, route, live semantic-quality verdict, push or paid generation was performed. Placeholder tests exercise the native freeze and log-only methodology; the real artifact exercise stops at planning.

## Finding placement

| Finding affecting the next action | Placement |
|---|---|
| Root expansion caused successive independent capacity stops; native planner now bounds the lifecycle | Result and causal account |
| Three-item allocation, measured copy/symbol arithmetic, final maximum request and all bounds | Real literature plan and arithmetic |
| Deterministic cuts retain mandatory qualifiers/endpoints, preserve source, and disclose conditional premises | Result and causal account |
| Zero-contribution windows, final omission reasons and conservative reuse of prior assumed premises | Result and causal account |
| Actual per-window output quotas prevent consumption of later capacity; unexpected output may still refuse | Result and causal account; Scope and remaining gaps |
| Full-suite/control evidence and which partial runs are not final proof | Verification |
| Candidate costs are conservative payload bounds; provider counts are whole-request evidence, free but networked | Real literature plan and arithmetic; Scope and remaining gaps |
| All papers have structural candidates, without relevance/semantic assurance; actual T may be smaller | Real literature plan and arithmetic; Scope and remaining gaps |
| Optional chunking deferred; non-author review and actual model/search behavior remain unexecuted | Scope and remaining gaps |

9 findings, 9 placed.

Delivery checkpoint: clean `5009af1e053d11dac18405fe7402331134585fea` on `fix/bounded-closure`, all requested local verification complete. No push or paid generation. Next unresolved step is the explicitly following non-author review, then any separately authorized live pilot. Optional chunking and semantic/search proof remain the disclosed limits above.

DONE sigma head=5009af1e053d11dac18405fe7402331134585fea tests=624/626 negctl=pass per_window_budget=3 projected_t_commitments=144 max_request_tokens=67613 report=/home/dev/ara-work/reports/sigma-bounded-closure.md


## Round 2

### Intake and causal checkpoint

Resumed on fix/bounded-closure at 5009af1e053d11dac18405fe7402331134585fea with a clean tree. No round-two edits existed at intake. The pilot reproduced the 48-window / 144-slot plan, then rejected 927 catalogue tokens against an 800-token window share; correction yielded 802 and still failed. Global capacity remained. This hard local rejection is the demonstrated blocker (zeta-full26.md, part 5).

Implement soft shares and borrowing, actual remaining-capacity recounts, accounted window skips, and partial construction completion on genuine global capacity exhaustion. Preserve global working/catalogue/context bounds and campaign/accounting failures. Zero accepted commitments still fail. Validate with placeholder native-path tests and mutation controls, rerun the count-only real plan, then full pytest and controls sequentially. No paid generation, delegation, or push. Native inline execution; the user owns publication.

Checkpoint before implementation: 1 finding, 1 placed (Intake and causal checkpoint).


### Implemented behavior and local review

Soft working/catalogue shares are now recomputed before each window from counted
accepted capacity and remaining windows. Actual output may borrow beyond a share
while global budgets and context remain hard. Accepted borrowing is logged after
accounting succeeds. Empty earlier windows release capacity, so a later root may
retain more of its full support than under round one's static shares.

Window-level selection/formalization failures, exhausted corrections, oversized
initial/correction contexts, and indivisible oversized source windows are accounted
skips. Roots and closure are retained when valid, alongside omissions and reasons.
Invalid selection candidates remain in raw response receipts. Content-addressed
refusal artifacts cannot overwrite prior accepted artifacts during a recount.
Only accepted commitments/symbols update the accumulated state. Evidence accounting
still reconciles every source ID before the existing single freeze.

Global exhaustion ends dispatch and passes accepted work to the existing freeze,
with exhaustion and omitted windows exposed in methodology. An empty T still fails.
Final working, catalogue, and downstream context recounts remain mandatory.
Campaign caps, unknown usage and operational failures still abort. Partial
construction completion does not assert downstream search or semantic success.

Author review identified and reproduced a counter-error classification gap: a
post-response ValueError from token counting could become InvalidOutput and be
skipped. A regression first failed because construction silently completed; after
wrapping counter ValueError as an operational RuntimeError, it passes and proves
measured response usage remains logged, no window skip and no freeze occurs.
The preliminary full suite was stopped at this finding; the final full run starts
after this fix. The first real-plan attempt was superseded when prompt wording was
finalized; only sigma-plan-round2-final is used for the final planning receipt.

The ce-simplify-code rubrics were applied inline under the no-delegation instruction;
no additional refactor was justified. No lint/typecheck command is configured.
Code review: skipped (ce-code-review unavailable) — its required independent agent
review conflicts with the brief's explicit no-delegation instruction. An author
manual diff review covered refusals, admission/accounting exceptions, inventory,
replay receipts and the sole freeze; the brief's non-author review remains pending.
This is not an independent-review claim.


### Round 2 real-plan verification

Free provider token counting completed in `runs/sigma-plan-round2-final/` with zero
generation calls and an explicitly empty audience. The original artifact SHA-256
remains `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`.
All 48 window content hashes and the entire allocation object are identical to
`runs/sigma-plan-final/construction-plan.json`: 3 commitments/window, 144 projected
commitments; 204 copied tokens and 233 symbol-reservation tokens per commitment;
3,232 wrapper tokens; projected working T 66,160/100,000; projected catalogue
33,552/48,000. The largest input is 67,631/70,000, and the input plus reserved
catalogue and output is 179,631/200,000. Prompt clarification adds 18 input tokens
relative to round one; it changes neither allocation nor partitioning. This is a
count-only proof, not a successful live construction/search claim. Compact receipt:
`/home/dev/ara-work/reports/sigma-evidence/round2/real-plan-verification.json`.


### Round 2 execution checkpoint

Implementation is complete in the uncommitted tree on fix/bounded-closure atop
5009af1e053d11dac18405fe7402331134585fea. Focused construction tests and the new
counter-failure regression are green. Final full pytest is active with output at
`/tmp/sigma-round2-pytest-final.txt` (session 82445); no controls are running.
All 291 control anchors occur exactly once. After pytest completes, run
`uv run python tests/integration/negative_controls.py` sequentially, preserve its
red/restored receipts, commit only the task files, and add final verification and
finding-placement counts here. No source edits are planned. The final real plan
is complete and its comparison receipt is recorded above. Do not rerun the
superseded initial real-plan or preliminary full-suite attempts.


### Round 2 verification results

Final full pytest: **642 passed, 2 skipped** (644 collected), 299.33 seconds.
The two skips are opt-in live checks; no paid generation was performed. Evidence:
`/home/dev/ara-work/reports/sigma-evidence/round2/pytest.txt`.
The 291-control runner started only after this suite completed: **291 red under
mutation, 291 restored green**, exit 0. No independent pytest ran alongside it.
Receipts are preserved in `/home/dev/ara-work/reports/sigma-evidence/round2/controls/`
and the console summary in `sigma-evidence/round2/controls.txt`. All mutations were
restored; the final diff has no whitespace errors. New controls cover borrowing
for both resources, share recomputation, recounts, skippable refusal and correction
context, global exhaustion/one freeze, hard global working capacity, campaign
failure, exhaustion disclosure, indivisible-window skipping, final catalogue
recount and post-response counter failure. Existing hard catalogue and empty-T
controls also pass.

### Round 2 finding placement

| Finding affecting the next action | Report section carrying it |
| --- | --- |
| Hard window shares caused the reproduced pilot refusal despite global capacity. | Intake and causal checkpoint |
| Recomputed shares may retain more support after earlier empty windows; static-cut expectations no longer apply. | Implemented behavior and local review |
| Post-response counter ValueError could be mistaken for invalid model output; reproduced and fixed with accounting retained. | Implemented behavior and local review |
| Partial freeze is disclosed and bounded, but downstream search and semantic quality remain unverified without a live run. | Implemented behavior and local review; Round 2 real-plan verification |
| Independent non-author review remains pending; this task performed author review only under the no-delegation constraint. | Implemented behavior and local review |
| Allocation and partitioning are unchanged; prompt clarification adds 18 tokens while retaining all planned bounds. | Round 2 real-plan verification |

**6 findings, 6 placed.**


### Round 2 final handoff

Committed locally on `fix/bounded-closure`: `4a5fbc3bd0988ec38f8826f94d31a82a95527d28`. The worktree is clean.
Full pytest and all 291 controls completed sequentially; all control mutations
were restored. No push, paid generation, or delegated agents were used. The
count-only real plan retains the entire original allocation and all 48 window
content hashes. Non-author review and live construction/search remain pending.
The execution checkpoint above is superseded by these final results.

**6 findings, 6 placed** (mapping in Round 2 finding placement).

DONE sigma round2 head=4a5fbc3bd0988ec38f8826f94d31a82a95527d28 tests=642/644 negctl=pass soft_shares=yes window_skip=yes freeze_on_global_exhaustion=yes


## Round 3

### Intake and reproduced finding

Resumed clean on fix/bounded-closure at 4a5fbc3bd0988ec38f8826f94d31a82a95527d28.
Upsilon B1 is valid: actual-output borrowing was allowed, but closure admission
and depth cutting still enforced headroom-adjusted window shares. Later fitting
roots could be starved after the first output crossed the planning target. The
round-two interpretation recorded in S2 was wrong and is superseded here.

Added native-path regressions for an 82,000-token first output followed by fitting
windows, the review's 1,500-token budget with both headroom settings, and a five-item
mandatory inference bundle above its four-item local target. All four cases fail
on the unmodified round-two source. Evidence: /tmp/sigma-round3-red.txt.
The required fix uses recounted remaining global capacity for admission and depth
cuts, preserving mandatory qualifiers/endpoints, exact request/context checks,
accepted-output limits and omission accounting. No paid calls, delegation or push.


### Round 3 implementation and targeted proof

Closure admission and depth cutting no longer consult per-window commitment
slots or working shares. They count the candidate working envelope together with
prior accepted commitments, then compare its copied growth plus the existing
formula-growth reservation against recounted global working capacity. Catalogue
growth reserves only newly materialized IDs against remaining global catalogue
capacity. Mandatory closure rules, exact request/context admission, actual output
bounds, one nonempty freeze, and explicit omissions are retained. S2 and the
selection prompt now distinguish planning guidance from global admission.

All **40 focused tests passed**. The headroom regression accepts three commitments
at 84,000 tokens after the first uses 82,000; the later windows retain zero soft
shares. The 1,500-token-budget reproduction now accepts all three at 1,300 tokens
under both .2 and .01 headroom. The mandatory inference bundle keeps five items
against a four-item planning target, preserving both endpoints, the qualifier and
distinction, and disclosing the omitted support. Two production-wire controls
restore the former working-share and item-slot vetoes independently.

The implementation diff was reviewed locally against B1 and the unchanged hard
checks. No delegated or independent round-three review is claimed. Full pytest
is running at /tmp/sigma-round3-pytest.txt (session 32891); controls have not yet
started. All 293 control anchors are unique, and mutation-target hashes are saved
for the post-run restoration audit. Evidence: sigma-evidence/round3/.

No provider counting or generation was rerun in round three. The earlier real-plan
receipt is historical; the initial allocation arithmetic is unchanged, but no new
exact real-request token count or live construction/search success is claimed.


### Round 3 full verification checkpoint

`uv run --locked pytest -q`: **646 passed, 2 skipped, 648 collected**, exit 0,
304.50 seconds. The skips are opt-in live checks. Only after that process exited,
`uv run --locked python tests/integration/negative_controls.py` started with 293
controls. Its output is /tmp/sigma-round3-controls.txt (session 57640). No other tests run concurrently.
The source is fixed pending verification; local commit and final restoration audit
remain. Full-suite evidence: sigma-evidence/round3/pytest.txt.


### Round 3 finding placement

| Action-relevant finding | Placement |
| --- | --- |
| Upsilon B1: soft shares still acted as closure vetoes; the prior S2 interpretation was wrong. Fixed by global admission. | Intake and reproduced finding; implementation and targeted proof |
| The previous full suite and controls missed the admission gap; four new regression cases and two mutations now cover it, including mandatory endpoints/qualifiers and explicit support omissions. | Implementation and targeted proof; full verification checkpoint |
| Verification is offline; no new provider token counts, live construction/search success, or independent round-three review is claimed. | Implementation and targeted proof |

**3 findings, 3 placed.**


### Round 3 final verification

Full pytest completed first: **646 passed, 2 skipped (648 collected)**, exit 0.
The control runner then completed: **293 mutations failed their targeted tests,
293 restorations passed**, exit 0. Both new B1 controls passed: restoring the
working-share cutoff starves the post-headroom windows, and restoring the item
slot cutoff rejects the globally fitting mandatory bundle. No tests ran beside
the mutation runner. All mutation-target SHA-256 hashes match their pre-run values;
`git diff --check` passes. Saved receipts include all 586 individual control
outputs, results.json, console output and before/after hashes under
`/home/dev/ara-work/reports/sigma-evidence/round3/`.

Upsilon B1 is fixed. No paid calls, delegation, push, live construction/search,
or independent round-three review was performed. The earlier checkpoints are
superseded by these completed verification results. **3 findings, 3 placed.**


Round 3 committed locally on `fix/bounded-closure` at `1411e91c70a6537422dbfece6f6ed1301b90e748`. Worktree clean; no push.

DONE sigma round3 head=1411e91c70a6537422dbfece6f6ed1301b90e748 tests=646/648 negctl=pass fixed=upsilon-B1


## Round 4 — terminal provider refusal and verified construction resume

### Intake and offline diagnosis

Same branch `fix/bounded-closure`, clean intake at
`1411e91c70a6537422dbfece6f6ed1301b90e748`. No paid calls, delegation or push.
The stopped pilot accepted seven batches containing 140 provisional commitments.
Its measured spend was USD18.770560; the terminal request retained a separate
USD0.946910 reservation with unknown actual usage.

Reconstructed window 17's `select_t_roots` request from the recorded prompt,
schema, configuration and reservation. Its recorded input was 107,462 tokens and
output reservation 16,384: 123,846 total against the 200,000-token context limit.
The prompt was 245,285 bytes; provider argument JSON was 264,035 bytes and the
SDK mock-transport wire body 264,049 bytes. The 416-byte projected schema passes
JSON Schema validation and matches prior successful selections. The request has
one nonempty text block, no images, and no invalid control/surrogate characters.
Successful window 12 had a larger recorded input count of 114,095 tokens.
There is no evidence of a malformed or oversized application request.

The installed Anthropic SDK 1.12.1 raises `APIStatusError(status_code=200)` for an
SSE error received inside a successful HTTP stream. The existing safe diagnostic
filter suppresses non-error HTTP status codes, explaining a null logged status.
An offline `httpx2.MockTransport` reproduction using the reconstructed request
and a synthetic placeholder error reproduces that exact diagnostic shape without
network access. Likely cause: **opaque provider-side streamed validation
rejection**. The original suppressed message cannot be recovered; prompt-too-long
is not confirmed. Request ID: `req_011CgJkLXVWBuPojPU69m6qe`.

Evidence: `sigma-evidence/round4/terminal-request-audit.json`,
`selection-comparison.json`, `sdk-stream-reproduction.json`; reconstructed request,
inputs and SDK wire body remain external, outside tracked repository content.

### Resulting behavior and recovery boundary

A terminal SDK `invalid_request_error` or `request_too_large` on selection,
formalization or a correction now retains its full reservation, enforces caps,
logs `count-at-reservation`, skips the window and continues. HTTP-200 streamed
errors are included. Transport interruptions, authentication, rate limits and
server failures remain fatal. Unknown usage stays unknown and rejected responses
are never cached. Methodology includes provider refusals and resume receipts.
Safe diagnostics retain only whole allowlisted size sentences with bounded
numeric token counts; arbitrary text and appended request echoes remain suppressed.

`resume-construction` uses the existing run's stored configuration, literature,
topic, audience and bank version under an exclusive resume lock. It verifies the
event chain and anchor, plan hash and artifact, contiguous completed windows,
accepted-artifact hashes and evidence IDs, and skipped omission/closure receipts.
It requires a terminal provider-refusal receipt linked to its dispatch and exact
reserved usage, and explicit count-at-reservation acknowledgment. It restores
used correction allowances, recomputes the same counted plan ID, and restores
accepted commitments/symbols without generation or extra charges. Normal global
recounts, merge, one nonempty freeze and target/search lifecycle then apply.
Already-frozen runs, incompatible plans, corrupt artifacts and unreceipted
interruptions refuse. This is bounded recovery from a terminal request rejection;
it does not claim arbitrary crash recovery.

Read-only verification of the real pilot found completed windows 0–16, seven
accepted batches totaling 140 commitments, terminal window 17, next window 18,
and one selection plus one formalization correction already consumed. Plan ID:
`0c05ea4383c09b28bb865ce44c3eb2dbfb8efde6b49c16888989215a1efe2581`.
Receipt: `sigma-evidence/round4/pilot-resume-audit.json`.
A native offline replay on a copied run is in progress; it uses recorded token
counts and forbids generation. The original pilot has not been relaunched.

Operator command, **not executed live in this round** (can make new paid calls):

```sh
uv run ara resume-construction --run-dir /home/dev/ara-scaffold/runs/overnight6-pilot --unknown-usage-policy count-at-reservation
```

Run from the checkout containing this round's eventual commit. Future paid
continuation remains subject to the original budget caps and same-plan check.

### Verification checkpoint

Regression evidence before implementation: refusal/diagnostic tests had 10
failures and four passes; resume tests had three failures and one pass. Focused
green runs: 55 refusal/diagnostic tests, 63 combined targeted tests, then 12 resume
file tests after adding the lock. Full pytest is currently running; all 300
negative-control anchors are unique and the 26 mutation-target file hashes have
been saved. Controls will run only after pytest and the native replay exit.

Inline review covers the round-four diff, artifact/ledger linkage, accounting,
correction allowances, single-freeze lifecycle and concurrent resume refusal.
No independent or delegated review is claimed. No separate lint/typecheck is
configured in pyproject.toml. Implementation decisions are recorded in S3.


### Round 4 completed full-suite checkpoint and operational timing

`uv run --locked pytest -q` completed with **669 passed, 2 skipped, 671 collected**,
exit 0, in 338.44 seconds. The two skips are opt-in live checks. Receipt:
`sigma-evidence/round4/pytest.txt`. No production changes followed this run.

The native replay is slower than the small fixtures: the original append-only
log is approximately 267 MiB, and the existing EventLog re-verifies its chain for
each planning append. Several minutes of CPU-bound plan recounting are observable
before any generation. This is a real continuation latency limit, not evidence
of a hung provider call. No logging safeguard was bypassed or optimized here.

Simplification review made no changes; the local source review found no remaining
round-four defect. The independent/delegated review workflow was not used under
the task's no-delegation constraint. Scope and limits are recorded in
`sigma-evidence/round4/review.json`.

### Round 4 finding placement

| Action-relevant finding | Placement |
| --- | --- |
| The original failure is consistent with a provider streamed rejection; request size/schema/content checks do not establish an application defect, and the suppressed complaint is unrecoverable. | Intake and offline diagnosis |
| Safe size diagnostics now retain only complete allowlisted messages and bounded counts; arbitrary provider text remains suppressed. | Resulting behavior and recovery boundary |
| Terminal construction refusals now skip a window, retain unknown reservation accounting and disclose the policy; other operational failures remain fatal. | Resulting behavior and recovery boundary |
| The pilot has seven verified accepted batches / 140 reusable commitments, with window 18 next and earlier corrections already consumed. | Resulting behavior and recovery boundary; final verification |
| Resume is bounded by receipt integrity, the same plan, original caps and single freeze; it is not general crash recovery and can incur new paid calls. | Resulting behavior and recovery boundary, including operator command |
| All new verification is offline; neither live continuation/search success nor independent review is claimed. | Verification checkpoint; completed full-suite checkpoint; final verification |
| Large-log chain verification makes native recounting take several minutes before dispatch. | Completed full-suite checkpoint and operational timing |

**7 findings, 7 placed.**


### Round 4 native replay result

The native replay completed successfully on a copied real pilot. It reproduced
the exact plan ID, restored all 17 completed windows and 140 commitments, skipped
terminal window 17 and reached window 18. It made **zero new dispatches** and
added **USD0.00**. The original log's byte-for-byte prefix remains unchanged in
the copy; the destination event chain and anchor verify. Original log SHA-256:
`c44b443a82130252cebc15dcb2ac34058f9c3c6c2a1180dd53f1fa5780fad3b3`.
The replay stopped at the first request lacking a recorded count; live token
counting, generation, freeze and downstream search were not attempted on the
real source. Placeholder native-path tests cover completion through one freeze.
Receipts: `sigma-evidence/round4/pilot-native-replay.json` and the saved replay
transcript. The follow-up receipt verifier initially expected error text rather
than the native replay's successful JSON output; that harness-only expectation
was corrected, and the verification passed without rerunning construction.

Only after full pytest and native replay completed, all 300 mutation targets
were successfully collected and the full control runner started. No tests or
replay process run concurrently with its temporary production-file mutations.


### Round 4 final verification

Full pytest: **669 passed, 2 skipped, 671 collected**, exit 0. After pytest and
the offline native replay had exited, the complete negative-control runner
passed: **300 mutations failed their targeted tests; 300 restorations passed**,
exit 0. All seven new controls passed: terminal-provider window skip, safe size
diagnostics, accepted-artifact hash, same counted plan, native CLI resume wiring,
non-request provider failure scope, and exclusive resume lock.

All **26 mutation-target file SHA-256 hashes** match the pre-control manifest;
`git diff --check` passes. No source changed after the successful full suite
except temporary mutations that were restored exactly. Saved evidence under
`sigma-evidence/round4/` includes the full pytest transcript, control console,
results.json, all 600 individual red/green outputs, before/after source hashes,
collected control targets, native replay receipts, and verification-summary.json.
The complete native replay was offline and restored the actual pilot's 140
commitments under the same plan with zero dispatches or added cost. It does not
claim live continuation, freeze or downstream success on that real source.

The terminal provider complaint remains unknown; no application request defect
was established. Window refusal handling and bounded verified construction resume
are implemented. No paid calls, delegation, push, or independent review occurred.
Earlier in-progress checkpoints are superseded by these completed results.

**7 findings, 7 placed.**


Round 4 committed locally on `fix/bounded-closure` at `e5e40cb99a5e827be8c054feb171d400346a700e`. Worktree clean; no push.

DONE sigma round4 head=e5e40cb99a5e827be8c054feb171d400346a700e tests=669/671 negctl=pass cause=opaque-stream-rejection window_provider_skip=yes construction_resume=yes


## Round 5 — live counter diagnosis and count-only resume

### Intake and base

Started clean on `fix/bounded-closure` at `e5e40cb`. At the operator's instruction,
rebased the round-five work onto **2d9aeb5**, including Xi's report fixes, before
final verification. Only free count endpoint calls are authorized; no generation,
paid calls, delegation or push. Credentials were loaded only into the probe
process environment from the existing documented loader; no key was printed or
written. Raw provider diagnostic text was read only in the terminal, not written
to tracked files or events. The report below contains a paraphrase.

### Diagnosis: account credit, not a demonstrated request-construction fault

The first resume recount is the full-corpus `build_t_batch` probe used before
recursive partitioning. Rebuilding it with the native request path produced
exactly the same message content as the original successful count. That recorded
count was **2,018,079 input tokens**, with a 64,000 output reservation; it is a
partition probe, not a generation admission. The count message is **4,468,597
bytes**; canonical request JSON is **4,738,873 bytes**. It contains one nonempty
message, no images, no invalid control characters and no lone surrogates. Its API
fields are model, thinking and messages; schema content is appended as text, not
passed as a schema/tool definition to the count endpoint. The source/configuration
and request construction did not establish the presumed serialization difference.
Historical wire headers were not recorded, so full wire-level identity is not
claimed. Audit: `sigma-evidence/round5/first-count-audit.json`.

The exact rebuilt first request returned **HTTP 400 / invalid_request_error**.
Sanitized paraphrase: **the account lacks sufficient credit for API access,
including this free count call**. Field path: **none**. Request ID:
`req_011CgJvd3rjfPhuCeDadMp45`. A minimal placeholder-only request to the same free
endpoint returned the same account condition, request
`req_011CgJvfvZH8oUtchYdW6ZFW`. This isolates the current blocker from book text,
message size, schema and restored-state serialization. No text sanitization or
source alteration is justified by this evidence.

This reproduction explains the present recount refusal and is consistent with
the earlier opaque part-7 400. It does **not** recover the suppressed historical
message. Part 6's streamed window-17 rejection remains opaque; no new generation
call was permitted or made, and a common historical cause is not proven.

### Implementation and account-wide failure boundary

Request-specific terminal count rejections now log stage, request hash, safe
diagnostic and zero cost. Aggregate partition probes that are rejected are split
deterministically. Indivisible or final uncountable windows are explicitly omitted
with null input_tokens; no invented count is persisted as a measurement. Copy-floor
and window-admission refusals can also omit that window and proceed to later
windows. Global final-envelope checks remain mandatory. A pre-dispatch count
refusal creates neither a MODEL receipt nor a charge/reservation. Methodology
includes counter refusal/failure receipts.

Account-credit failures are deliberately **fatal**, including when carried by an
HTTP-200 stream. They are account-wide and must not cause every source window to
be skipped. Diagnostics emit only a canonical paraphrase; appended text is never
echoed. Resume also refuses to reinterpret an explicitly identified account-credit
terminal receipt as a window refusal. Authentication, rate limits, server errors
and interruptions remain operational stops. No client-side change can restore
the provider's account access. The operator has been asked to restore access or
identify another authorized credential loader; no billing action was taken.

### Count-only preview and executed restoration proof

New command (separate empty output directory required):

```sh
uv run ara resume-construction --run-dir /home/dev/ara-scaffold/runs/overnight6-pilot --unknown-usage-policy count-at-reservation --plan-only --output-dir runs/resume-plan-next
```

The preview holds the source resume lock, verifies the source ledger/artifacts,
requires the same counted plan, and restores into its own log. It has zero spending
caps and a CountingProvider that cannot generate. It stops after counting the next
eligible selection request, without generation or freeze. A refusal that changes
the partition or plan still fails the compatibility guard; the new skip policy
does not waive plan identity or rewrite accepted work.

The native CLI offline replay used **338 exact recorded counts**, restored all
**17 completed windows / 140 commitments**, and reached the first unrecorded count
for **window 18** under plan
`0c05ea4383c09b28bb865ce44c3eb2dbfb8efde6b49c16888989215a1efe2581`.
It made zero generation calls and added USD0.00. The original source log was
unchanged, SHA-256
`7b445640ba67fbdee9793d779733ad1b0e6e337554dcc719dc556c75c0fea255`.
Receipt: `sigma-evidence/round5/offline-resume.json`. This is a recorded-count
replay, not live confirmation of the window-18 count. Placeholder native CLI tests
exercise the completed preview and its source-preservation/dispatch boundaries.

The live guarded CLI preview was then executed. It exited **2 at the first count**,
with the account-credit condition, before restoration. It logged kind
`build_t_batch`, zero cost and safe diagnostics; request
`req_011CgJwWRtxewx9VpbXX62Xk`. No generation dispatch, MODEL receipt, freeze or new
charge occurred. The source log remains byte-identical. Receipt:
`sigma-evidence/round5/live-resume.json`. **Live count-only restoration is not yet
successful; no claim that every live count passes is made.**

### Verification checkpoint

Initial regression run: five new tests failed on the prior implementation.
Additional red checks exposed account-error classification, missing counter-stage
receipts, a spurious MODEL receipt before generation, and account-error resume
misclassification; each received a focused regression and fix. Focused suites
passed (latest combined checkpoint: 72 tests); final resume checks and the full
suite follow on the stable rebased source. The earlier interrupted full-suite run
is not counted as final verification. Full pytest and the mutation runner will
complete sequentially. No independent/delegated review is claimed.


### Round 5 finding placement

| Action-relevant finding | Placement |
| --- | --- |
| The first recount's message equals the original count content; no invalid text, empty block, or demonstrated schema/serialization fault justifies source edits. | Diagnosis |
| Both the exact request and a tiny placeholder receive account-credit denial; account access must be restored before free counting can complete. | Diagnosis; implementation and account-wide failure boundary |
| Historical part-6/part-7 raw messages remain unavailable; a shared historical cause is not established by today's reproduction. | Diagnosis |
| Request-specific count failures now split/omit honestly, while account-wide failures stop; counter receipts are free and pre-dispatch refusals create no MODEL receipt. | Implementation and account-wide failure boundary |
| The new preview is isolated from the source run, has zero caps/no generation provider, and does not waive plan identity or authorize omission of a known account failure. | Count-only preview; implementation and account-wide failure boundary |
| Offline restoration reached window 18 with 140 commitments; live preview failed before restoration. Neither every-live-count success nor downstream completion is claimed. | Count-only preview and executed restoration proof; final verification |
| Work is rebased on 2d9aeb5; final tests/controls are local and sequential, with no paid calls, push or independent review. | Intake and base; verification checkpoint; final verification |

**7 findings, 7 placed.**


### Round 5 full-suite result

On the stable source rebased onto `2d9aeb5`, `uv run --locked pytest -q` completed
with **681 passed, 2 skipped, 683 collected**, exit 0, in 327.90 seconds. The skips
are opt-in live checks. The final focused resume/account file run passed nine
tests. No production changes followed the successful full suite. All 314 control
anchors and target selections were checked, and mutation-target hashes were
saved. The full control runner started only after pytest completed; no replay,
provider probe or other test runs concurrently with it.


### Round 5 final verification and remaining live gap

Final full pytest: **681 passed, 2 skipped (683 collected)**, exit 0. After pytest
and both replay/probe processes had exited, the complete control runner passed:
**314 mutations failed their targeted tests; 314 restorations passed**, exit 0.
All nine new controls passed, covering counter classification, recursive splitting,
uncounted-window omission, absence of pre-dispatch MODEL receipts, preview dispatch
prevention, account-credit scope, source-log isolation, safe counter diagnostics,
and refusal to turn known account errors into resume omissions.

All **28 mutation-target SHA-256 hashes** match their pre-run values.
`git diff --check` passes. No production changes followed the final full suite;
temporary control mutations were restored exactly. Receipts under
`sigma-evidence/round5/` include pytest output, results.json, all 628 individual
red/green control outputs, console output, target selections and before/after
hashes. Inline review covered the round-five diff only; no independent review or
separate lint/typecheck is claimed. The repository has no separate configured
lint/typecheck command. The branch's base is
`2d9aeb590df3b48958ad481dcfc424ada70e11d1` as requested.

**Live count-only resume remains failed because account credit is insufficient.**
The exact first request, a minimal placeholder probe, and the guarded native
preview all encountered that condition. No account-access restoration was supplied
during this round. Repeating the operator command after restoring API access is
the next unresolved step; every-live-count success and live restoration through
window 18 remain unverified. No paid generation, billing change, push, or source
artifact rewrite occurred. The live attempt added **USD0.00** and left the original
pilot log unchanged. The offline replay restored 140 commitments under the same
plan and reached the window-18 count boundary; this does not close the live gap.

Earlier in-progress checkpoints are superseded by these completed verification
results. **7 findings, 7 placed.**


Round 5 committed locally on `fix/bounded-closure` at `0e0a7fcf8a167fa6a0973f92e322582c33d6e6e4`, directly on `2d9aeb590df3b48958ad481dcfc424ada70e11d1`. Worktree clean; no push.

DONE sigma round5 head=0e0a7fcf8a167fa6a0973f92e322582c33d6e6e4 tests=681/683 negctl=pass cause=insufficient-credit live_count_resume=fail


## Round 6 — Fixed spread cap and construction stage configuration

### Intake and implementation

Work continues on `fix/bounded-closure` from
`0e0a7fcf8a167fa6a0973f92e322582c33d6e6e4`, which includes requested base
`2d9aeb5`. Intake was clean. Work was performed inline; no delegation, paid calls,
network calls, push, or edits to `ara/runtime/providers.py` were made this round.
Real-source replay artifacts remain external or ignored; tracked additions use
placeholder content.

`construction_window_cap_multiplier` defaults to 2 and accepts finite numeric
values at least 1. The fixed cap is floor(initial planning share × multiplier):
share 3 gives cap 6. It counts new commitments; already materialized exact IDs
can be reused. Empty early windows do not increase later windows' caps.
Deterministic prerequisite depth cuts preserve mandatory qualifiers/endpoints and
record `support_omitted`. Acceptance also checks the returned inventory against
the cap. If the mandatory root bundle itself exceeds the cap, the window contributes
nothing; roots are not arbitrarily ranked or discarded by code. A zero initial
share gives a zero cap and a disclosed omission before generation.

**No redistribution pass is implemented.** A second selection/formalization pass
would add lifecycle and accounting work. Unused capacity may remain. The cap limits
concentration; it does not guarantee relevance, equal actual contributions, or
reserve global token capacity for later windows. Existing global/context bounds
still apply.

### Fresh rebuild and stage contract

Use `ara run` with a new empty run directory for a fresh rebuild. The native CLI
regression proves that it dispatches window 0 again and does not restore earlier
accepted construction artifacts. Extraction provenance remains pinned. Plan
version is `rich-working-t-v9`; cap arithmetic and effective stage settings are
part of identity, so old accepted plans cannot authorize the new capped rebuild.

Configuration nodes are `stages.select_t_roots`, `stages.build_t_batch`, and
`stages.construction_correction`. Each may override `provider`, `model`, and
provider dispatch settings. Corrections inherit their originating stage before
correction overrides. Profile application preserves unrelated stage entries.
Scoped calls share the ledger/cache/enclosing Budget and use the matching backend
for counting, dispatch, and receipts without mutating the main provider. Provider
changes at the same model name invalidate the response cache. Pricing for all
selected models belongs in the enclosing run configuration. Methodology exposes
requested/served stage models and provider identity.

`ara.runtime.cli.make_provider` is the registration seam for Omega. No coordination
messages were sent; these documented config keys are the contract. `claude_code`
is neither implemented nor executed by this change. Live dispatch/count behavior
for that backend remains an integration proof for its lane. Existing standalone
provider-count planning still uses the Anthropic counter; it does not certify
another backend's tokenization.

### Offline real-plan distribution and limits

The completed replay used the original 48-window evidence geometry and **335
historical count receipts**, mapping requests by removing only the new cap/stage
metadata and restoring the old version/prompt prefix. It did not obtain fresh
provider counts. New metadata/prompt overhead is measured separately: maximum
**1,164 added bytes**. The new provider may produce different token counts,
partitioning, and shares; this is not its capacity certificate.

Projected target distribution: **windows 0–47 each target 3 commitments**, total
**144**, fixed cap **6** each. Every window has at least one nonempty single-root
closure fitting the cap and conservative payload bound: **48/48 potentially
contributing windows**. This establishes candidate feasibility, not relevance,
actual formula sizes, or actual accepted contributions. Generation calls: **0**;
network calls: **0**. The earlier 7/48 actual-contribution result is not replaced
by an executed 48/48 construction run.

Recorded-budget projection: working copy cost 204 and symbol cost 233 per item;
working wrapper 3,232; projected working tokens **66,160** and symbol tokens
**33,552**, within available 76,768 and 38,400 respectively. Recorded batch counts
range **29,696–67,688**, under 70,000; added prompt bytes were not newly tokenized.
Old plan id `0c05ea4383c09b28bb865ce44c3eb2dbfb8efde6b49c16888989215a1efe2581`
changes to `4ab8d1d8d1b2f52c2f958b96857e081d5eb7e1507e8e0336484a336cfc1c2c63`.
All 48 window content hashes are unchanged.

The separate historical-root-bundle cap replay demonstrates why fresh selection
matters: window 5's former 76-item bundle contributes zero under the new cap
because its mandatory bundle cannot fit. This is not a prediction that fresh
selection will choose the same roots. Per-window targets, candidate counts, capped
closure maxima, and historical-bundle outcomes are in
`sigma-evidence/round6/distribution.json`; native plan and count mappings are in
`real-plan.json` and `count-mapping.json`, with reproducible `real_plan.py` alongside.

### Verification checkpoint

Before implementation, cap and dispatch/profile regressions failed as expected.
Focused verification passed 58 tests; the final cap/stage file run passed 15 tests
following the cache identity refinement. The obsolete zero-share borrowing test
now asserts a zero-cap omission. All **323** mutation anchors are unique; the
inherited extraction-profile control now removes `apply_profile` at its original
CLI branch, preserving its intended check. Mutation-source hashes are saved.
Full pytest is running on the final source; the full mutation runner will start
only after pytest exits. Neither an independent review nor a separate lint/typecheck
is claimed; this repository configures pytest and no separate lint/typecheck.
Inline diff inspection found no additional blocking defect or useful simplification.
The no-delegation brief takes precedence over the skills' review-agent workflow;
a non-author review remains the caller's next step.

### Findings placement

| Action-changing finding | Deliverable section |
| --- | --- |
| Fixed cap defaults to 6 for share 3; later empty windows cannot raise it. | Intake and implementation |
| Mandatory bundles above the cap and zero initial shares contribute nothing; omitted support stays explicit. | Intake and implementation; Offline real-plan distribution and limits |
| No second pass; the cap does not ensure equal relevance/coverage or reserve later global tokens. | Intake and implementation |
| A fresh empty run rebuilds construction, and cap/stage configuration changes plan identity. | Fresh rebuild and stage contract |
| Stage provider/model routing is configurable; the new backend and its live counting remain unexecuted. | Fresh rebuild and stage contract |
| The 48/48 projection means candidate feasibility using historical counts; added bytes and new tokenization remain a capacity caveat. | Offline real-plan distribution and limits |
| Full tests/controls must complete sequentially with exact restoration; review is inline and no independent review is claimed. | Verification checkpoint; Round 6 final verification |

**7 findings, 7 placed.**


### Round 6 diagnostic regression and repair

The first full suite completed with **688 passed, 1 failed, 2 skipped**. The new
zero-cap branch preceded the existing oversized-source branch and hid its explicit
diagnostic when the source batch bound was only one token. The existing
`test_counted_capacity_refuses_explicitly[batch]` caught this. The zero-cap branch
now follows count-refusal and oversized-source checks, preserving their original
reason while still preventing generation at zero capacity. The failing full-suite
output is retained as `pytest-before-diagnostic-fix.txt`. Affected tests and the
full suite must pass again before controls start; the earlier full run is not a
passing checkpoint.


### Round 6 full-suite checkpoint

After the diagnostic-order repair, affected files passed **84/84** tests. The
final full command `uv run --locked pytest -q` passed **689 tests, 2 skipped,
691 collected**, exit 0, in 373.11 seconds. The skips are opt-in live checks.
No production edits followed that run. All 323 mutation anchors are unique,
all control target selectors collect (including whole-file targets), and all
28 saved source hashes still match. The full control runner started after
pytest and collection completed; no tests or replay run concurrently in this
worktree. Final receipts will follow after mutation restoration is audited.


### Round 6 final verification

The final full suite passed **689/691 tests**, with **2 opt-in live tests skipped**,
exit 0. The complete mutation runner then passed **323/323 controls**: each mutation
returned pytest exit 1, and each exact restoration returned exit 0. All nine new
controls passed, covering multiplier configuration, cap depth cutting, fixed cap
after an empty window, fresh-run isolation, stage/correction dispatch, cache
identity, profile preservation, and stage plan identity. All **28 mutation-target
SHA-256 hashes** match their saved pre-run values; `git diff --check` passes.
No production edits followed the successful full pytest run.

Evidence is saved in `sigma-evidence/round6/`: `pytest-final.txt`,
`diagnostic-targeted.txt`, `collected.txt`, `controls-console.txt`, `controls/results.json`,
all 646 individual red/green control outputs, source hash manifests, the offline
plan/distribution/count mapping, and reproduction/audit scripts. Earlier failed
verification is retained and superseded by this final result. The diagnostic-order
regression was fixed in production, without weakening the existing refusal test.
No separate lint/typecheck is configured. Inline inspection is author review only;
the requested later non-author review remains outside this worker's scope.

The implementation is ready for integration of the provider lane. It does not
claim live `claude_code` execution, new-provider capacity counts, actual 48-window
contributions, or downstream completion. The remaining execution step is a fresh
pilot with the registered backend and explicit operator budgets. No redistribution
pass, paid call, or push occurred. The report's seven action-changing findings are
all carried in the sections named in the findings table: **7 findings, 7 placed.**


Round 6 committed locally at `2195a2dc15e4b636a8f168a9fc7b6dc822335c1e` on `fix/bounded-closure`, based on
`0e0a7fcf8a167fa6a0973f92e322582c33d6e6e4` and containing `2d9aeb5`.
Worktree is clean. `providers.py` is unchanged. No push.

DONE sigma round6 head=2195a2dc15e4b636a8f168a9fc7b6dc822335c1e tests=689/691 negctl=pass window_cap=6 projected_windows_contributing=48/48


## Round 7 — Bounded native formula validation

### Base, intent, and implementation

Started from clean round-six `2195a2d` and fast-forwarded `fix/bounded-closure`
to requested main `8aa265fa32b97bdbae662108ba080950c5c73034`, which already contains
that work. No delegation, paid calls, live provider execution, or push. Tracked
regressions use placeholders; external pilot evidence was read, not modified.

The native schema files and provider projections are unchanged. A local Draft
2020-12 extension selects a unique required `op` branch before descent instead
of exploring all recursive alternatives. All constraints of the selected native
branch are still evaluated. If tags are not required and disjoint, ordinary
oneOf/anyOf behavior remains. A schema-derived structural pass checks formula
node kinds, required fields, argument counts, symbol/term kinds and names before
recursive validation. Existing catalogue-reference checks remain in force; free
variables and vocabulary are not newly restricted.

Codex normalization uses the same discriminator and carries a successful subtree
check through its traversal, avoiding repeated validation and copying of that
subtree. Optional-null normalization retains its existing semantics. ModelCalls,
construction/extraction correction merges, recorded extraction validation, graph
migration, Codex preflight witnesses and both provider canaries all use bounded
native-schema evaluation. `providers.py` is unchanged.

### Operational bounds and correction behavior

Configurable defaults: `local_validation_max_depth: 64` (root depth 0),
`local_validation_max_nodes: 100000` (JSON values), and
`local_validation_timeout_seconds: 2.0` per schema/normalization operation.
The precheck uses an iterative traversal. Recursive schema work runs in a separate
interpreter; timeout kills and reaps it, including when invoked from concurrent
search threads. A single pathological regex cannot trap a search thread forever.

Native model-output bound failures retain the received response, usage/cost and
precise validation path/constraint in the ledger, are not cached, and enter the
existing correction path. Tests exercise structural, depth, node and hard-time
refusals followed by an accepted correction. Offline replay and isolation canaries
retain their existing caller failure policies. This bounds local schema and Codex
normalization work; provider calls, domain callbacks and solver work keep their
separate budgets. Child startup/IPC adds overhead; the configured time allowance
includes this work after the initial complexity traversal.

Schema equivalence is distinct from operational admission: an otherwise valid
object over a resource limit is explicitly refused. No arbitrary depth cap was
added to the native schema, and no invalid tree is accepted as a fallback.

### Equivalence, stall measurement, and schema audit

The old unmodified Draft202012Validator times out after two seconds on the
placeholder nested-unary-conjunction shape (`old-stall-red.json`). The recorded
pilot's longer 14-minute stall was not rerun. The placeholder regression has
**17 formula nodes and JSON depth 22** and must reject in under 50 ms, before
starting the recursive validator process. Across 100 real executions, median
**0.115 ms**, maximum **0.269 ms** (`equivalence.json`). No network or generation.

Offline corpus comparison passed **215/215 distinct cases**, zero mismatches,
zero old-validator timeouts: **84 accepted, 131 rejected**. Inputs combine existing
fixture formulas, all existing serialized operator/term forms, and 280 seeded
random valid/invalid generation attempts (duplicates removed for this replay).
The replay invokes the old validator and the complete new bounded entrypoint;
it does not compare the new implementation with itself. The test corpus also
checks every native response-schema example and malformed envelope against both.

The general equivalence argument is branch exclusivity: every optimized branch
requires a string `op` with a distinct constant (or singleton enum), so no other
branch can validate the same object. Selecting that branch preserves oneOf and
anyOf truth values; every remaining branch constraint is still delegated to the
native Draft implementation. Missing/unknown tags cannot satisfy any branch.
The structural precheck enforces constraints from those same native branches.
The depth/node/time bounds remain the explicitly separate operational refusal.

Audit of all 14 schema files: recursive formula definitions occur in `formula`,
`formalise`, `build_t`, `build_t_batch`, and `propose_targets`, with identical
native formula definitions. `propose_cuts` and `tier1_repair` have acyclic
proposal/premise references; `answer_cq` has no recursive references. Extraction's
unions are shallow scalar variants; citation verification has nonrecursive
conditions. All native runtime schema evaluations now share the deadline even
where no formula exists. `schema-audit.json` records this scope. No changed-schema
or live provider preflight is claimed or required: native/wire schema bytes did
not change.

### Verification in progress

Affected checks passed **130 tests with one opt-in live skip**, then **189
consumer tests**. The validation regression file passed **13 tests**, including
exactly one native union visit per formula node. The final Codex-normalization
focused run passed **68 tests**. After adding the JSON-decoder depth boundary,
the final validation file passed **14 tests**. Seven new controls bring the
integration inventory to **427**; all anchors are unique. Full pytest and the complete mutation runner
will run sequentially on the stable final source, then source hashes and evidence
will be audited before the local commit.

### Findings placement

| Action-changing finding | Deliverable section |
| --- | --- |
| Recursive branch search caused the local stall; native constraints now run through tag selection and an early structural guard. | Base, intent, and implementation; Equivalence, stall measurement, and schema audit |
| Codex normalization had the same exposure and now avoids repeated subtree work. | Base, intent, and implementation |
| Schema-valid objects may be refused by explicit configurable resource limits; this is operational admission, not schema relaxation. | Operational bounds and correction behavior |
| Timeouts work in search threads through kill/reap, and received output stays accounted, logged and correction eligible. | Operational bounds and correction behavior |
| Equivalence has a disjoint-branch argument and finite old/new corpus evidence; the pathological old run is bounded rather than awaited indefinitely. | Equivalence, stall measurement, and schema audit |
| All recursive schema owners were audited; cuts/CQ schemas do not contain the recursive formula union. | Equivalence, stall measurement, and schema audit |
| Full tests/controls, restoration hashes and author-review limits determine local readiness; no live pilot completion or push is claimed. | Verification in progress; Round 7 final verification |

**7 findings, 7 placed.**


### Round 7 stable-source checkpoint

An additional native regression proves that JSON decoder recursion exhaustion
also becomes a logged depth rejection and correction. Its control disables that
conversion. Existing extraction/Codex schema controls and the encoded-formula
decode control now target the replacement entrypoints, preserving their purposes.
All **427** mutation anchors are unique, and hashes for **38** mutation-target
source files are saved. The final full pytest run has started with live provider,
local OCR and local VL opt-ins disabled. No further code edits are planned.


### Round 7 feedback regression and repair

The first full suite was interrupted after **285 passed, 3 failed** because three
existing audit tests showed a feedback regression: a manually raised domain
ValidationError lost its sentence-inventory message when formatted as a schema
error with an unset validator. Production now retains domain error messages and
uses path/keyword formatting only for actual schema constraints. No assertions
were weakened. Audit, writer, call and validation consumers then passed **59/59**.
The interrupted output is retained as `pytest-interrupted-feedback-regression.txt`.
The full suite is being rerun on this correction, with refreshed source hashes.


### Exact recorded-shape alignment

The initial synthetic regression matched the reported node count and depth. A
read of the preserved receipt established its exact operator topology, including
inner implication and negation nodes. The committed fixture now reproduces that
whole topology and all optional fields, with every source symbol replaced by P.
Its generated value equals the redacted external receipt byte-for-JSON-value;
no real-source names or text are tracked. The native old validator still times
out after two seconds. The exact placeholder shape rejects at **0.083 ms median,
0.511 ms maximum over 100 runs**, including schema-file loading in this measurement.
The updated validation file passed **14/14**. A full run with no failures observed
was interrupted at **737 passed, 3 skipped** to ensure the final full run covers
this exact fixture revision; it is not reported as a completed full-suite result.


### Round 7 full-suite checkpoint

On the stable final source and exact recorded placeholder fixture, the full
command `ARA_LIVE_TEST=0 ARA_TEST_LOCAL_OCR=0 ARA_TEST_LOCAL_VL=0 uv run --locked pytest -q`
passed **1015 tests, 4 skipped, 1019 collected**, exit 0, in **777.33 seconds**.
The skips are opt-in live-provider/local-model tests. All 427 control anchors
are unique and every targeted test selector collects. All 38 pre-mutation source
hashes match. The complete mutation runner starts only after full pytest and
collection exit; no other tests/replay run alongside it in this worktree.


### Decoder control exposed a test gap

The first complete control attempt reached **425 successful mutations** and then
stopped at `local_json_decoder_depth`: mutated and restored tests both passed.
The current C decoder accepts the test's 600-level JSON; the real structural
depth guard had supplied the rejection, so this test did not prove the decoder
exception handler. No production defect or un-restored mutation was found; all
38 production-source hashes matched after the stop.

The test now explicitly injects the decoder's documented RecursionError only
for that response string. It proves the native accounting/correction path handles
that exception, rather than claiming this Python build rejects at that depth.
Actual depth/node-limit and recorded-stall tests continue using real unmodified
parsing. The revised validation file passes **14/14**. All seven new controls are
being rerun before another full-suite/control sequence. This test-only repair
leaves production source unchanged; prior final-suite evidence is retained but
the final delivery receipt will name the completed rerun on the revised tests.


### Round 7 final verification

The final stable-tree run passed **1015 tests, 4 skipped, 1019 collected**, exit 0,
in **770.49 seconds**. Live-provider and optional installed OCR/VL checks were
disabled. After pytest exited, the full integration mutation runner passed
**427/427 controls**: every mutation returned pytest exit 1 and every restoration
returned exit 0. All seven new validation controls passed, including the corrected
fault-injected decoder failure test. All **38 mutation-target SHA-256 hashes**
match the saved pre-run hashes; `git diff --check` passes. No production or test
edits followed this final full-suite run, apart from exactly restored mutations.

The pipeline archived `pytest-final.txt`, `controls-console.txt`,
`controls/results.json`, all **854** current red/green control outputs, target
collection, source hash manifests, corpus equivalence evidence, exact redacted
stall topology and timing samples under `sigma-evidence/round7/`. Historical
interrupted/failed checkpoints remain clearly labeled and are superseded by this
completed sequence. `phase.txt` records completion of tests, controls and hash
verification. Both the native schema directory and `providers.py` are unchanged
from `8aa265f`.

**Schema equivalence: proven by the required-disjoint-tag argument and supported
by 215/215 old/new corpus comparisons, zero mismatches.** Operational depth/node/time
limits remain separate explicit refusals; the claim does not erase those limits.
The exact recorded topology with placeholder names rejects in **0.511 ms worst
case across 100 samples**, well under 50 ms. Actual decoder-limit behavior varies
by Python build; its exception-to-correction path was fault-injected, while real
structural/depth/node/timeout and native correction paths were executed directly.

Author inspection covered validation entrypoints, normalization, correction,
accounting, cache rejection, subprocess termination, and unchanged schema authority.
No independent review or separate lint/typecheck is claimed; the repository has
no separately configured lint/typecheck command. No live pilot was resumed or
completed, no paid calls were made, and nothing was pushed. A non-author review
and then an operator-authorized pilot remain downstream steps, not completed
proofs from this round. All seven action-changing findings are carried in their
named deliverable sections: **7 findings, 7 placed.**


Round 7 committed locally at `c32d429e77eedb09e0d4f48126b01355f998a119` on `fix/bounded-closure`, directly on
`8aa265fa32b97bdbae662108ba080950c5c73034`. Worktree is clean. Native schemas
and `providers.py` remain unchanged. No push.

DONE sigma round7 head=c32d429e77eedb09e0d4f48126b01355f998a119 tests=1015/1019 negctl=pass stall_shape_ms=0.511 equivalence=proven

## Round 8 — source structure and frozen catalogue

### Interface and ownership

Base: `c32d429e77eedb09e0d4f48126b01355f998a119`. Catalogue interface commit:
`597b666ef73b4394a6828b2a72d7387d6a58236e`. Xi confirmed integration of that commit
with an additive DECISIONS resolution. Sigma owns construction, catalogue
persistence, and `prepare_commitments`; Xi owns search/calls/contracts/search tests,
`prepare`, and NativeEngine methods. Search integration verification belongs to Xi;
Sigma's branch does not claim his later search changes are present.

Strict CommitmentSet serialization and `commitments.json` remain unchanged. Rich
construction writes `frozen-t.json` with `{schema_version: frozen-t-v1,
commitments: CommitmentSet.to_dict(), symbol_catalogue: ...}`. Catalogue fields
are `schema_version: symbol-catalogue-v1`, `commitments_sha256`, `symbols`,
`sha256`, and `catalogue_id`. Symbols contain name/kind/arity/definition/evidence_ids,
sorted by name with sorted unique evidence IDs. Commitment hash uses canonical T;
catalogue hash uses only schema_version/commitments_sha256/symbols. SHA256 is over
UTF-8 sorted compact JSON with unescaped Unicode and no NaN. Identity is `sha256:`
plus lowercase hex. No semantic normalization occurs. The validator verifies
binding, definitions' hash identity, exact vocabulary coverage and signatures.

Missing envelope means legacy catalogue unavailable. A present corrupt envelope
must refuse, not silently downgrade. Xi reports that his accessor does this and
carries symbols/catalogue_sha256/commitments_sha256 into search inputs. The original
pilot artifacts remain untouched; plan v10 does not reinterpret old counted plans
as this new construction policy.

### Structure behavior and limits

Inference items are prompted as attributed conditionals using selected premise
and conclusion formulas in a shared vocabulary. Source-supported relational
encoding uses predicates/constants. Code checks exact endpoint conjunct inclusion,
never semantic equivalence. Model-authored definitions and supporting evidence
record within-batch reuse; existing-symbol reuse still requires alignment reasons.
Source-supported qualifiers may attach; unsupported attachment is not fabricated.
Source conditionals never confer ARA bank licenses.

Each batch records non-atomic fraction, symbol reuse rate, conditional endpoint
connections, and source inference fraction. Atoms and predicates count as atomic.
Reuse is the fraction of commitment/symbol bindings whose symbol appears in another
current or prior commitment; constants count too. Endpoint connectivity requires
exact conjunct matches, not merely shared constants. Missing budget-cut endpoints
are not certified as connected. These are syntactic measurements, not semantic
translation scores.

A deficient batch gets one item-specific structure correction, separate from the
validation-patch allowance. The response replaces the fixed batch so unused flat
symbols can be removed; prior catalogue symbols remain immutable. If still atomic,
the failed gate remains visible and the batch is accepted with
`flat_after_one_correction` in its receipt and log-derived methodology. This can
still prevent useful entailments. Structured but mismatched selected inference
endpoints remain a refusal. Malformed outputs, symbol/provenance mismatches and
capacity failures have no flatness exemption.

### Placeholder solver proof

The native rich-construction path produces P(a), Q(a), a conditional from their
conjunction to R(a), and a conditional from R(a) to F(a), with shared predicates
and constant. Existing `ara.formal.entails` derives F(a) from those four premises
(SOLVER_UNSAT); neither R(a) nor F(a) is assumed. Removing the conditional premises
produces SOLVER_COUNTEREXAMPLE. Unsupported qualification attachment remains
separate in this fixture. The proof checks an executable placeholder seam; it does
not establish faithful real-source formalization or live search success.

### Offline real-source census

The first attempt stopped before fake generation: API token cap zero means no
tokens allowed. It was rerun in a fresh directory with ample synthetic budgets.
The default-budget retry was stopped after confirming a two-item window cap:
no inference with distinct premise/conclusion can fit that mandatory bundle. The
census uses the existing full-profile 32,000-token catalogue reservation and
256-token symbol-growth allowance. These choices remain explicit fake-count inputs.
**Completed:** 28 of 131 selected items are inference nodes (**21.37%**),
from 5,296 source items (943 inference nodes). All 31 windows were processed;
28 batches were accepted and three oversized mandatory bundles were omitted.
All 28 accepted batches disclosed flatness after correction. There were 87 fake
dispatches, zero network calls, and zero paid calls. Source log SHA256
`7b445640ba67fbdee9793d779733ad1b0e6e337554dcc719dc556c75c0fea255`
is unchanged. Receipt: `sigma-evidence/round8/real-fake-census.json`; reproduction
script: `sigma-evidence/round8/real_fake.py`. This is a fresh
native construction run with the real imported literature, a deterministic
inference-first single-root selector per window, fake byte/4 token estimates and
flat placeholder formulas. It measures potential structure under this explicit
selection policy. It is not a real relevance judgment, tokenizer/capacity proof,
or successful semantic encoding. No network or paid calls are allowed.

### Verification and delivery

Catalogue checks: 7 passed. New structure checks: 4 passed. The first wider targeted
run yielded 90 passed/1 failed: a pre-existing variable-scope test replaced inference
items with quantified predicates. Its fixture now selects only premises, preserving
the variable-binding test's purpose under the structure contract. The subsequent
focused structure/catalogue/stage/scope run passed all 15 tests. Full pytest completed: **1,026 passed, 4 skipped / 1,030 collected**,
865.50 seconds. **All 431 mutation controls passed**: every mutation produced test exit 1 and
every restored run exit 0. All 40 mutation-source SHA256s match their saved values. All 431 mutation anchors are unique; their targets are present
in the 1,030 collected tests. Controls ran only after both full pytest and the real-source fake census exited;
no test or replay ran concurrently with the mutation runner. Restoration audit
passed for all 40 source files. All 862 individual control outputs, the full
pytest log, source hash manifests, and census reproduction script are preserved
in `sigma-evidence/round8/`. The four new controls passed separately before the
full checks and passed again in the complete run. `git diff --check` passed. No paid generation, push,
independent review, or real-source semantic success is claimed.

### Findings placement

| Action-changing finding | Section carrying it |
| --- | --- |
| Catalogue metadata is an optional hash-bound envelope; legacy codecs remain strict and present corruption refuses. | Interface and ownership |
| Xi owns search integration; its later search implementation is not in Sigma's branch. | Interface and ownership |
| Plan v10 does not resume old plans as the new policy; original pilot stays unchanged. | Interface and ownership |
| Metrics and endpoint matching are syntactic, not semantic fidelity or equivalence. | Structure behavior and limits |
| One correction can end in disclosed flatness; other validation failures retain refusal behavior. | Structure behavior and limits |
| Placeholder entailment succeeds without assuming the target but proves no real-source semantic success. | Placeholder solver proof |
| Real-source inference fraction is policy-dependent potential structure using fake counts/formulas. | Offline real-source census |
| Verification is author-run; no independent/live/search-integration verdict is claimed. | Verification and delivery |

8 findings, 8 placed.

### Final local receipt

Catalogue commit: `597b666ef73b4394a6828b2a72d7387d6a58236e`. Structure commit / final head:
`2452ecbabdc02ead31dd86bb4e23e90bc17ded5d`. Base ancestry verified against `c32d429`; worktree clean.
No push. Exact machine receipt: `sigma-evidence/round8/final-receipt.json`.

`DONE sigma round8 head=2452ecbabdc02ead31dd86bb4e23e90bc17ded5d tests=1026/1030 negctl=pass structure_gate=yes catalogue_exposed=yes`

## Round 9 — content definitions and source stance

### Interface, semantics, and integration boundary

Base: `5b512de4ef37264fe3ac3fa8bbfe2a19e48606b8`; clean round-8 worktree was
fast-forwarded to that requested base. Helper-only commit:
`1ff0f7fafd5f7c633be61525fee33be4a2c3c404`, already accepted and integrated by Xi.
The exact agreed contract is `/home/dev/ara-work/reports/sigma-xi-stance-contract.md`.
No delegation, paid calls or push.

Fresh rich construction (`rich-working-t-v11`, `build_t_batch_v5`) asks for id,
content definition, and formula. Commitment.text is the content definition, and
catalogue definitions also denote content. Runtime does not mechanically strip
attribution to invent a proposition. Exact source text remains unchanged in the
source evidence and is copied into provenance; citations remain unchanged. Old
frozen texts/catalogues are not rewritten, and old counted construction plans
cannot silently resume under the new semantics.

CommitmentSet's four-field codec, commitments.json, frozen-t.json and the
symbol-catalogue-v1 format/hash contract remain unchanged. New metadata lives in
immutable `commitment-provenance.json`. Its required fields are schema_version
(commitment-provenance-v1), definition_semantics (content), commitments_sha256,
catalogue_sha256, commitments (id -> provenance), and sha256. SHA256 covers all
fields except sha256 using runtime.cache.canonical/digest. It binds the exact T
and verified catalogue. The full sidecar is logged as `commitment_provenance_frozen`
before `commitments_frozen`. Batch receipts and working-T artifacts also retain
provenance, including restored construction batches.

The load/validation helpers return the verified full sidecar. Absence returns
None: legacy content/stance semantics are unavailable, never implicitly endorsed.
Present corruption, wrong bindings, unknown fields, mismatched inventory or
inconsistent stance refuse. Hashes detect changes relative to retained records;
they do not authenticate an attacker rewriting an entire history.

Xi owns classifier inputs, search/cache context, stance-aware premise/CQ/forward
admission, route/report/selection disclosure, and fork/resume preservation. His
later implementation is **not in this Sigma verification tree**. Integrate that
lane before a new pilot: the search/fork code at this branch's base does not by
itself consume the new sidecar or enforce its stance restrictions. Sigma changes
neither solver checks nor bank licensing.

### Provenance fidelity and stance

Each commitment's metadata preserves source_id, source_authors, attributed_to,
page_start/end, evidence_id, original attribution, stance, source_kind, exact
source_text and sorted omitted_support_ids. author_claim maps to endorsed,
reported_view to reported, and attacked_view to attacked. A reported/attacked
source-kind tag must agree with attribution. Endorsed describes the extraction's
source-stance label, not an independently established truth. Reported/attacked
content is retained for explicit scoped use, not relabelled as endorsed.

Bibliographic authors are preserved when the literature input supplies them.
An added source-author regression exposed an existing publication limitation:
native literature_entry omits bibliographic records, although extraction logs
retain them. For those inputs source_authors is empty; attributed_to is still
available separately. The final regression covers both absent author metadata
and explicitly supplied authors distinct from the reported speaker. No author is
inferred and no historical extraction artifact is rewritten.

Budget-cut support warnings now live in omitted_support_ids, separate from the
content definition. A source claim can be endorsed yet have omitted supporting
evidence; these are different properties. Existing closure receipts and methodology
still disclose the conditional frontier. The original support-marker mutation
control now mutates this provenance field, guarding the same observable warning.

### Definition validation and limits

Both commitment and symbol definitions reuse Xi's unchanged
`target_policy.attributed_report` lexicon. Attributed definitions enter the native
logged correction path; the configured correction allowance, admission and budget
rules remain binding. Uncorrected invalid definitions refuse and cannot use the
flatness exception. No new retry loop bypasses the construction budget.

The lexical rule is conservative: legitimate content using words in its lexicon
may be refused, and avoiding those words does not prove faithful translation.
Content definitions, formula fidelity and equivalence remain model judgments.
The existing structure gate and the placeholder conditional entailment proof
remain exercised; exact source metadata is copied by code, not authored by the model.

### Verification and delivery

Initial native proof: 8 failed/2 passed before the new contract/helper, with failures
at the intended missing-schema/API boundary. Helper tests: 15 passed. Native
content/provenance/catalogue/structure tests: 21 passed. Broader construction,
resume, attribution and capacity consumers: 161 passed. The stronger author
assertion initially failed because published literature omits records; the
corrected input-boundary regression covers both actual absence and supplied
metadata. Final focused content tests: 11 passed.

Seven new/updated mutation cases were verified red then restored green before
full gates: five new definition/stance/source-text/hash cases plus the existing
content-copy and omitted-support cases. Full pytest/control results follow below.
The first full control attempt exposed a weak boundary assertion: the new final
provenance inventory guard rejected omitted content even with the earlier fixed-
inventory guard disabled. The existing qualification test now requires rejection
before any batch acceptance. Its control fails under mutation and all 10 invalid-
batch tests pass after restoration. Production checks remain unchanged. The first
full-suite receipt and stopped control run are retained separately; final gates
restart on the strengthened test tree.

Author review and inline simplification consolidated an import and removed a
redundant comment; protected proof tests and trust-boundary checks were retained.
This is local/offline evidence, not independent review, live pilot completion or
proof of semantic faithfulness. Standalone shipping is skipped under the caller's
bounded implementation brief; no PR or push is authorized or performed.

Final delivery commit: `2d713e99743453f4746dd5324cd3832ccb241d64` on `fix/bounded-closure`; working tree clean.
The committed tree matches all 218 pinned file contents (including verification
of the AGENTS.md symlink and its CLAUDE.md target), and both requested base
`5b512de` and accepted helper `1ff0f7f` are ancestors. Final offline pytest:
**1134 passed, 4 skipped / 1138 collected**, 915.82 seconds. It was followed
sequentially by **483/483 controls**, each red exit 1 and restored exit 0.
All 48 mutation-target hashes were restored; the complete ordered result inventory
was audited. Evidence is under `/home/dev/ara-work/reports/sigma-evidence/round9/`:
`pytest-final.txt`, `controls-console.txt`, `controls/results.json`,
`verification-tree-sha256.json`, `verification-tree-after.json`,
`committed-blob-sha256.json`, and `commit.json`.
The earlier failed control attempt is retained in `controls-first-attempt/` and
`first-controls-console.txt`; it is not counted as a passing full control run.

Xi reports his separate completed commit as
`c187128180aa71229c812a8900da66523886a3ef` (helper included), with 1142 passed,
4 skipped and 488 controls. Those are Xi's reported results, not a combined-tree
verification receipt. Integrate Sigma's final commit with Xi's lane and verify
the combined tree before a pilot. No push, paid call or live run was made here.

### Findings placement

| Action-changing finding | Section carrying it |
| --- | --- |
| New content semantics require plan v11/schema v5; old frozen artifacts/plans are not reinterpreted. | Interface, semantics, and integration boundary |
| Sidecar identity binds exact T/catalogue; absent legacy metadata is unknown and present corruption refuses. | Interface, semantics, and integration boundary |
| Stance is a copied source label, not truth; reported/attacked content remains explicitly restricted. | Provenance fidelity and stance |
| Current literature publication omits bibliographic records; unknown authors remain empty, distinct from attributed speakers. | Provenance fidelity and stance |
| Omitted support remains a separate conditional warning in provenance. | Provenance fidelity and stance |
| Lexical screening can over-reject and cannot prove fidelity; correction and budget limits remain binding. | Definition validation and limits |
| Xi's metadata-aware search/fork/resume enforcement must be integrated before a pilot; it is outside this test tree. | Interface, semantics, and integration boundary |
| Executed tests/controls are offline author evidence, with no independent or live semantic verdict. | Verification and delivery |
| Final provenance validation also catches omitted inventory; the early-boundary regression must assert no batch acceptance to distinguish the two gates. | Verification and delivery |

9 findings, 9 placed.


## Round 10 — per-window corrections and exact definition unframing

### Behavior and configuration

Started from clean requested main `b48d56f97286199cbd144fc441b2d92837bfdda9`
on `fix/bounded-closure`. Construction now allocates a fresh configurable
`construction_targeted_corrections` allowance to each window and each call type.
The base configuration and full-extraction profile default to **2**; zero disables
correction. An existing explicit value of 1 remains 1, so a new pilot using an old
saved configuration must set this field to 2. This changes targeted correction,
not the separate one-shot structure correction.

The second correction receives the accumulated full candidate, retaining earlier
partial repairs. Every correction still uses native transport retries, context
admission, usage receipts and token/cost accounting. Transport retries do not
consume additional correction slots. There is no global correction counter; a
finite plan and its local limits bound requests, with existing run budgets as
backstops. At 74 windows, both stages together permit at most **296** targeted
correction requests. That is neither an upfront reservation nor a spend forecast.

Plan v12 includes the correction policy in its identity. Changing the allowance
requires a new plan. Old plans cannot resume under the new semantics; current
resume restores completed windows, skips the terminal refused window and gives
later windows their own budgets. A regression verifies that changing the limit
refuses before resumed generation.

### Feedback, rewriting and retained evidence

Definition validation now reports every offending commitment ID and symbol name,
with all matched phrases and an instruction to give a content-only restatement.
The active candidate validation reason remains visible alongside rejected-patch
and decoding errors; malformed corrections do not erase the specific repair request.
The shared attribution lexicon is unchanged. It can still reject ordinary content
that uses those words; extra retries do not establish semantic fidelity.

Runtime unframes only an exact leading source-known author or attributed speaker
followed by `argues that`, `holds that` or `claims that`. Matching is case-sensitive;
multiword source names are supported. Negated, conditional, quoted, nonleading,
unknown-speaker and missing-`that` wording remains for model correction. The
remainder is validated again. Normalization works on a copy of the model candidate:
repeated failed patches cannot silently peel nested frames one layer at a time.
This is a narrow syntactic convention for content-with-provenance, not a general
semantic transformation.

Each rewrite emits `definition_unframed` with plan/window identity, kind, name,
evidence IDs, author, original_definition and definition. Accepted provenance rows
optionally contain `definition_unframes` records with exactly kind, name, author,
original_definition and definition. The existing sidecar hash covers the history;
its validator checks the frame and symbol/evidence binding. Original source text,
citations, attributed speaker, source authors and stance are unchanged. Unknown
bibliographic authors remain unknown; the attributed speaker can still identify
a frame. Existing v1 sidecars without the optional field remain valid. Old strict
readers cannot accept new history: deploy the updated helper with construction.
CommitmentSet, commitments.json, frozen-t.json and helper signatures are unchanged.
Rejected rewrite events remain in the log even when their window contributes no T.

### Offline real plan and expected coverage

The read-only source was `/home/dev/ara-scaffold/runs/codex-pilot-4/events.jsonl`,
SHA256 `508f17d6a366a1dfec7f33171c4f0ff2a5c5682407b557f1e88f22ab23f353e5`.
Its hash is unchanged. The native planner used the same literature, audience,
profile and stage settings, changed the correction allowance to 2, and used a
counting-only adapter with native Codex estimates and pre-plan calibration. Network
and generation are forbidden in that harness. Missing adapter factory/metadata
methods were repaired before the completed planning run; no live provider was used.

The replan still has **74 windows**, all counted and within the 70,000-token batch bound (maximum
67,326 estimated input tokens), initial allocation **2 commitments/window**,
cap **4/window**, and **148 projected commitments**. Projected working tokens are
78,190 and projected symbol tokens 34,484. These are planning estimates and
allocation limits, not actual accepted coverage or a Codex tokenizer guarantee.

The historical pilot accepted 21 windows, freezing 64 commitments from 12/26 papers.
The response census reproduced **35 attribution-rejected responses across 34
windows**, with **zero exact frames eligible for deterministic unframing** and zero
responses automatically clearing the definition gate. Two correction events were
recorded across both call types. Under the new policy, those 34 windows can each
receive up to two formalization corrections, subject to current request and run
budgets; earlier windows no longer exhaust their allowance. Specific feedback
provides the missing IDs and phrases for each attempt. Improvement depends on the
model successfully restating content and passing the remaining checks. No new
commitment count, paper-coverage percentage or search success is claimed.

Evidence: `/home/dev/ara-work/reports/sigma-evidence/round10/real-plan-summary.json`,
`real-plan.json`, `definition-census.json`, `offline_plan.py` and its console log.
All real source material stays outside committed fixtures; repository tests use
placeholders only. No paid calls, live generation or push were made.

### Verification and delivery

Initial native regression run: 4 failed/17 passed before implementation. Focused
construction/provenance/root tests then passed 89 cases; resume/helper/profile/
transport consumers passed 78. An added nested-frame regression failed before
candidate-copy isolation and passed after it; the final focused group passed 40.
New controls cover per-window allowances, a second correction, accumulated patches,
complete feedback, exact matching, rewrite logging, retained provenance, plan
identity and single-layer normalization. The final receipts are recorded below. The first full run exposed six diagnostics regressions: unchanged or
undecodable correction patches hid the original validation reason. A new native
regression reproduced the lost model feedback; the fix retains the active
candidate reason alongside the patch error. Existing boundary assertions remain
unchanged. The first failed full run is retained separately. This is offline author
evidence, not independent review or a live coverage verdict.

Final delivery: `5fcd2b1a3dd76e15b565731f078aea7f2f74d536` on clean `fix/bounded-closure`, with requested base
`b48d56f` verified as an ancestor. Final offline pytest: **1174 passed, 4 skipped /
1178 collected**, 965.09 seconds. It was followed sequentially by **503/503 mutation
controls**, each red exit 1 and restored exit 0. All 219 pinned file contents match
after restoration and match the committed tree, with the AGENTS.md symlink and
its target checked separately. The 13 focused mutation checks also passed. No
source edits occurred during these final gates.

Final evidence lives in `/home/dev/ara-work/reports/sigma-evidence/round10/`:
`pytest-final.txt`, `controls-console.txt`, `controls/results.json`,
`verification-tree-sha256.json`, `verification-tree-after.json`,
`committed-blob-sha256.json`, `commit.json` and `delivery.json`. The failed first
full run is retained as `pytest-first-failed.txt`; it is not counted as a passing
receipt. The original pilot log hash was checked again after the gates and still
matches. The final feedback repair does not change the completed planning path
or its prompts/configuration. No push or paid call was made.

### Findings placement

| Action-changing finding | Section carrying it |
| --- | --- |
| Defaults are 2, but an old explicit configuration of 1 must be changed for a new pilot. | Behavior and configuration |
| Local correction budgets permit more requests; existing run admission and token/cost caps still apply. | Behavior and configuration |
| Plan v12 binds the correction limit; old plans cannot be silently resumed or reinterpreted. | Behavior and configuration |
| Partial repairs and active validation reasons survive invalid patches, while normalization cannot progressively remove nested attribution frames. | Feedback, rewriting and retained evidence |
| Exact unframing requires source-known names and narrow syntax; source text/citations/stance remain unchanged. | Feedback, rewriting and retained evidence |
| Optional provenance history remains hash-bound; old sidecars work, but old strict readers require the updated helper for new history. | Feedback, rewriting and retained evidence |
| None of the 35 historical rejected responses is automatically repaired; better coverage depends on model correction and remaining gates. | Offline real plan and expected coverage |
| 74-window allocation/counts are estimates; no regenerated corpus, live coverage or independent semantic verdict was produced. | Offline real plan and expected coverage; Verification and delivery |

8 findings, 8 placed.


## Round 11 — cross-paper symbol alignment before freeze

### Behavior and integration

From requested base `9b99997`, construction now ranks compatible atoms/predicates from disjoint paper sets by content-definition token overlap, with a default top-150 bound and a 0.15 weighted cosine threshold. Constants are excluded. One independently logged model judgment is requested per pair (two-symbol cluster), on the same provider/model as construction formalization. No search target is supplied. Valid relations are same_content, both directional entailments, contrary and unrelated. Code never promotes a candidate without a model judgment. A pair is a two-symbol cluster; larger semantic clustering is not claimed.

Same-content components rewrite formulas to the lexicographically first symbol and merge evidence IDs. Other nontrivial relations produce explicit bridge commitments, universally quantified for predicates, citing both original definitions and citations. Original source text, citation, attribution and stance remain unchanged. The full alignment set must pass signature/arity, uniqueness and bounded Z3 consistency checks; unsat/unknown sets are refused together and logged, retaining original T. An already inconsistent T cannot receive a nontrivial accepted alignment. No automatic subset salvage occurs. Recorded consistency refusals remain refused if a later solver would resolve; they can grant no bridge or mapping and must preserve original T.

`construction_alignment_candidates` defaults to 150; 0 disables the judgments explicitly. Each call has a default 2048 output allowance, with normal admission/cost accounting and configured validation retries. The new schema changes the Codex preflight manifest: older receipts become stale and live use needs a refreshed applicable preflight, whose calls are additional to the alignment judgments. No live preflight was run here. The final T input budget is checked after alignment. Construction plan v13 includes alignment policy/limit, invalidating older or differently configured plans for resume. The existing construction-resume entrypoint handles terminal window-provider refusals only; a later alignment-stage failure requires a new run with retained cache.

### Persistence and search contract

CommitmentSet, commitments.json and frozen-t-v1 stay unchanged. With candidates, commitment-provenance-v2 adds an alignment receipt (original T/symbols, candidate list, judgments, mapping, accepted/refused status and reason). Its hash binds final T/catalogue and the complete receipt. The validator replays the transformation and rejects tampering; v1 and legacy absence remain supported. New v2 records require updated readers. Full sidecar remains in commitment_provenance_frozen before commitments_frozen; native fork preserves/validates it. The reporter uses the final frozen catalogue.

Bridges have provenance kind=alignment,stance=model_alignment,source_id=null. They may be explicit alignment premises, never source CQ evidence or source endorsement. They do not count as a paper or replace the requirement for at least two endorsed source supports. Existing distinct-formula/cross-paper/novelty gates remain in force. Bounded leaf guidance includes bridge leads; route receipts, rendered routes, writer/auditor outlines and methodology disclose bridges and same-content judgments. Xi confirmed Sigma owns this seam; Xi owns further per-paper novelty and forward work. Exact interface: /home/dev/ara-work/reports/sigma-xi-alignment-contract.md.

### Offline pilot-5 result and limits

Read-only original input: /home/dev/ara-scaffold/runs/codex-pilot-5. Verified frozen artifacts contain 169 commitments, 151 symbols, 22 papers. Candidate ranking selects 23 eligible pairs (limit 150). One fake unrelated run made 23 calls and retained 169 commitments/151 symbols; one synthetic run made 23 calls and exercised one canonical rewrite plus one entailment bridge, yielding 170 commitments/150 symbols/one bridge. Both native freezes and persisted validators passed. The replay used mock token/accounting receipts and generous replay-only token, cost and final-T caps; it does not prove production context admission or spend budgets. All three source artifact hashes remained unchanged.

This is plumbing evidence only. The fake judge does not establish a valid alignment, improved cross-paper closure, philosophical fidelity or useful new arguments. Lexical ranking can miss paraphrases and can propose false friends. A live run would make 23 initial small judgment calls for this T/policy, plus any configured retries; no live/paid calls occurred. No semantic success claim is made.

### Verification and delivery

Final local commit: `bdeaeb8444113e5c0d6d62e5ac1b494a8f0b5fee` on clean `fix/bounded-closure`, with requested base `9b99997` verified as an ancestor. Final offline pytest: **1297 passed, 4 skipped / 1301 collected** (1444.60s (0:24:04)). It was followed sequentially by **583/583 controls**, each red exit 1 and restored exit 0. All 234 pinned file contents match both restored and committed trees; the AGENTS.md symlink was checked separately. The three pilot-5 source artifact hashes still match, and both fake-run artifacts and log receipts validate again on the final source (`pilot5-final-validation.json`). Final receipts: `pytest-final.txt`, `controls-console.txt`, `controls/results.json`, `verification-tree-sha256.json`, `verification-tree-after.json`, `committed-blob-sha256.json`, `commit.json`, and `delivery.json`. Before the final gate, 17 alignment regressions, 57 affected CLI/Codex tests, 90 construction tests, 68 search/fork/report tests and 22 focused mutation controls passed. The first interrupted suite exposed stale canned-request hashes and schema inventory counts; response values were unchanged when rekeyed. The next full suite passed 1,296 tests with four skips and one finite-fake fixture failure; that fake provider was extended for unrelated alignment judgments without weakening its assertions. Both unsuccessful suite receipts remain in the evidence directory. A focused signature mutation initially survived because a later catalogue guard still rejected the rewrite; the test was strengthened to use an unrelated judgment, isolating the early signature boundary, and then passed its red/restored control. That first failed control receipt is retained too. The solver-refusal reload correction has its own pre-fix red regression. Evidence directory: /home/dev/ara-work/reports/sigma-evidence/round11. Native inline author verification; no independent review or live provider proof claimed. No push.

### Findings placement

| Action-changing finding | Section carrying it |
| --- | --- |
| Ranking is a bounded lexical proxy and can miss paraphrases or suggest false friends. | Behavior and integration; Offline pilot-5 result and limits |
| Same-content judgments rewrite formulas while preserving original symbols/formulas, evidence and source stance. | Behavior and integration; Persistence and search contract |
| An unsat/unknown alignment set is refused in full; an already inconsistent T cannot accept nontrivial alignment. | Behavior and integration |
| Recorded refusals never become accepted during reload, even if solver timing changes. | Behavior and integration |
| Default cap150 and output allowance2048 affect initial call budgets; zero explicitly disables judgments. | Behavior and integration |
| The new judgment schema invalidates older Codex preflight receipts; live use requires refreshing the applicable manifest. | Behavior and integration |
| Plan v13 binds alignment policy/limit; earlier or changed plans cannot silently resume. | Behavior and integration |
| Alignment-stage failures have no dedicated construction-resume entrypoint. | Behavior and integration |
| Old v1/legacy metadata remains supported, but v2 artifacts require updated readers. | Persistence and search contract |
| Bridges have no single paper, are not CQ source evidence, and cannot replace two endorsed source supports. | Persistence and search contract |
| Pilot-5 has23 selected pairs; fake judgments prove plumbing, not semantic alignment or improved argument quality. | Offline pilot-5 result and limits |
| Xi's further per-paper novelty/forward work requires later integration; this branch stays on the requested base. | Behavior and integration; Persistence and search contract |
| The fake replay used mock accounting and generous replay-only caps; live context/cost admission is unproved. | Offline pilot-5 result and limits |
| Verification is offline author evidence; no independent review, live acceptance, paid call or push is claimed. | Verification and delivery |

14 findings, 14 placed.
