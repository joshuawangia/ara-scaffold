# Psi independent review

Review scope: base `0e0a7fcf8a167fa6a0973f92e322582c33d6e6e4`; Sigma `2195a2dc15e4b636a8f168a9fc7b6dc822335c1e`, Xi `f61a10a26ffaa786688a14700593c03fb06ab3da`, Mu `cdc9753f75e1906fa753bb7af3f410184f453d04`. No source-branch changes, delegation, paid calls, push, or Omega review. This is a non-author, single-reviewer review; no cross-model review was run, as the brief requires doing the work alone. Branch diffs, native callers, tests, control mutations, and authors' reports were inspected. ARA's own pytest/control gates apply; this is a separate Python repository, not the enrollment_hub pnpm project.

**Verdict: Sigma merge; Xi fix-first; Mu merge. One blocking finding.**

## F1 — Xi: hashed event order remains nondeterministic (blocking)

`ara/runtime/logging.py:109–113` queues events on its single executor as workers submit them. `ara/runtime/orchestration.py:51–63` joins results in target/polarity order only after searches finish; engine/model events and sidecar seals have already entered the hash chain in scheduler order. Serializing appends protects chain integrity; it does not establish deterministic event ordering.

Independently ran Xi's native ten-target/two-polarity equivalence test with its original sequential schedule and both four-worker schedules. Its assertions passed: routes, conflict/forward analyses, and all 20 raw sidecar contents match. Each event chain verifies. Nevertheless the stable `search_id` order of `search_trace_receipt` events differs:

- Sequential begins `11aa490cbe07:0`, `76cf3df1dbfe:1`, `0ade1cf88f56:0`, `59709fec9f35:1`.
- Four workers, first schedule: `76cf3df1dbfe:1`, `0ade1cf88f56:0`, `11aa490cbe07:0`, `59709fec9f35:1`.
- Four workers, reversed delay schedule: `59709fec9f35:1`, `11aa490cbe07:0`, `0ade1cf88f56:0`, `76cf3df1dbfe:1`.

This comparison excludes timestamps, UUID paths and raw hash values: logical event ordering itself changes. The equivalence test (`tests/runtime/test_parallel_search.py:135–143`) compares only routes, analyses and sorted sidecar bytes. The author's report explicitly accepts variable event interleaving, contrary to the Psi brief's requirement to check that there is no event-order nondeterminism in hashed logs.

Required before merge: define and enforce a stable job/event publication order, preserving durable request accounting and failure evidence, and add an order assertion under changed completion schedules. A valid single-writer chain alone does not meet this requirement. Evidence: `psi-evidence/check_event_order.py`, `psi-evidence/xi-event-order.txt`, and `psi-evidence/xi-equivalence/summary.json`; the three complete native logs and sidecars are retained alongside the summary. No claim of chain corruption or failed route equivalence is made.

## F2 — Sigma: the requested cap works; broad coverage remains conditional

The fixed cap is computed once from the initial share, configurable with `construction_window_cap_multiplier`, and disclosed in the plan. `construct.fits` rejects closures with too many **new** IDs before formalization; deterministic depth cutting preserves mandatory bundles and discloses omitted support. Acceptance independently checks the cap and exact inventory. Empty earlier windows do not enlarge it. Oversized mandatory bundles produce explicit zero-contribution windows rather than arbitrary root deletion. No second redistribution pass is implemented, as permitted by the brief.

This prevents the former 76-new-commitment window when share=3/cap=6. It does not reserve global tokens for all later windows, guarantee all papers contribute, or rescue an all-empty selection. Global token exhaustion and mandatory bundles can still omit windows; an entirely empty T correctly refuses. Do not present the cap as proof of representative literature coverage.

The author's offline historical-count replay projects 3 commitments per window, 144 total, cap 6, and at least one feasible root in each of 48 windows. That is feasibility, not an executed 48-window build. It reuses 335 old count receipts; up to 1,164 added prompt bytes were not newly tokenized. Its historical 76-item root bundle becomes empty under the cap. These limitations are accurately disclosed in Round 6 and `sigma-evidence/round6/distribution.json`, which I inspected; I did not rerun the real-plan projection.

Fresh native `run` starts without construction-resume state; tests prove it dispatches again rather than importing earlier accepted construction batches. Plan v9 binds the cap and stage choices. Root selection, formalization and correction use separate configurable provider/model settings, with a shared budget and stage-aware cache identity. `cli.make_provider` is the integration seam. The future `claude_code` backend and its token counts remain unverified here; Omega is outside scope. These are rollout limits, not additional defects in the requested cap change.

## F3 — Xi: reservation safety and equivalence boundaries

Admission checks and reservation insertion share an `RLock`; pending reservations count toward both token and cost limits. Reservations remain until a durable measured receipt exists. Settlement adjusts only the relevant request, exception recovery preserves other charges, and a run STOP blocks later admission. Per-key single flight avoids concurrent duplicate dispatch. Search workers own their engine state and sidecar; the solver's shared Z3 context is serialized. Target proposal is already a single batch call, so there is no independent per-target proposal loop to parallelize.

The route/sidecar equivalence proof is credible for fixed provider responses, equal inputs/seeds, and sufficient budgets. It does not prove live-model determinism or identical near-cap execution: outstanding reservations can cause an immediate conservative STOP even when sequential requests would eventually fit. This is disclosed and preserves the spending bound. Operators should account for aggregate in-flight headroom. The ideal fourfold search-phase speedup is an estimate, not a measured pilot improvement. F1 remains the blocking distinction between output equivalence and event-order equivalence.

## F4 — Mu: tamper detection retained; timing claim is narrower than 24 minutes

Cold verification captures exact artifact/sidecar bytes plus every transitive log and anchor, checks the original lineage, and stores verifier version/code/Python identity and result. Reuse validates the receipt chain/anchor, bindings and every recorded file hash, checks pinned-event bytes/digest, then hashes inputs again before import. Any mismatch falls back to full verification; invalid lineage refuses before model setup. Public full-verification entrypoints retain checks. The complete receipt and its checkpoint are chained into the new run before copied original receipts.

The placeholder regressions exercise ancestor/root log and anchor damage, artifact/header/sidecar damage and deletion, symlink retargeting, receipt corruption, verifier change, valid append invalidation, and mutation during cold/warm verification. No weakened verification was found within the repository's existing local-chain/separate-anchor trust model. Coordinated replacement of both a receipt chain and its anchor is not authenticated; adversarial change-and-restore between reads is not an atomic snapshot guarantee. These are disclosed trust limits, not signatures supplied by this change.

Independent real-lineage replay on this host: **33.226655s cold, 5.994966s warm**, 42 hashed files / 744,729,028 bytes, all 4,454 source events identical. Cold performed one full verification; warm performed none. Imported event digest matched the author's original base-run evidence, and the source artifact hash remained unchanged. No model/network call was used. The author's base measurement was 64.214626s and warm measurement 5.692084s; I reran cold/warm, not the old base timing. Evidence: `psi-evidence/check_mu_startup.py`, `psi-evidence/mu-startup.txt`, `psi-evidence/mu-benchmark/summary.json`.

This speeds lineage verification/import. It does not demonstrate elimination of the reported roughly 24-minute interval, which also includes construction restoration.

## F5 — Integration, conflict resolution and executed gates

Scratch clone: `/home/dev/ara-work/psi-integration`. Merge order: base → Sigma fast-forward → Xi (`efacf00`) → Mu (`f4a19b582b6eb96ed48cf00002560514fe08108c`).

| Merge | Conflicting files |
| --- | --- |
| Xi after Sigma | `DECISIONS.md`, `ara/runtime/calls.py`, `config.yaml`, `tests/integration/negative_controls.py` |
| Mu after both | `DECISIONS.md`, `README.md`, `tests/integration/negative_controls.py` |

Five unique files conflict. Both documentation/config/control additions are preserved. In `calls.py`, both initialization additions survive; stage routing precedes Xi's single-flight wrapper and request-local reservation state replaces the old log-offset/global-accounting recovery. Mu's CLI/logging changes auto-merged. Sigma's stage-dispatch control replacement now calls `_call_reserved`, because Xi added a required `state` parameter to `_execute_once`; leaving the old replacement would create a signature-error red instead of testing dispatch behavior. This adaptation is confined to the scratch merge. The full resolution is inspectable in the two local merge commits.

Executed on the final merged tree, sequentially:

- `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked pytest -q`: exit 0, **723 passed, 2 skipped / 725 collected**, 458.24 seconds. The skips are opt-in live-provider tests.
- `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked python tests/integration/negative_controls.py`: exit 0, **341/341 controls**, each red exit 1 and restored exit 0. All anchors occurred exactly once. Reviewed the failure causes for all 27 new controls, including the adapted stage-dispatch mutation: it fails on wrong provider/model routing, not a call-signature error. Reservation-removal/early-release controls time out at the deliberately held provider instead of receiving the required admission refusal; lock removal permits both competing admissions.
- All **29 mutation-target source files** match their pre-control SHA-256 hashes exactly; scratch `git status --porcelain` is empty and `git diff --check` passes. All three original source branches remain clean at their requested heads. `providers.py` matches the base byte-for-byte.

Evidence: `psi-evidence/merged-pytest.txt`, `merged-controls.txt`, `control-preflight.json`, `final-verification.json`, and `controls/` (all 682 individual red/green outputs plus `results.json`). No additional lint/typecheck is configured. No live provider tests or pilot completion are claimed. These passing integration gates do not supersede F1 or supply its missing event-order assertion.

## Finding placement

| Finding | Section carrying it |
| --- | --- |
| 1. Blocking hashed event-order nondeterminism and missing assertion | F1 |
| 2. Fixed cap/fresh rebuild/stage behavior and limits on coverage/provider proof | F2 |
| 3. Concurrent reservation safety, conservative near-cap stops and equivalence/speedup limits | F3 |
| 4. Cache integrity/trust boundary and measured startup scope | F4 |
| 5. Merge conflicts, resolution, executed integration gates and remaining validation scope | F5 |

5 findings, 5 placed.

DONE psi review sigma=merge xi=fix-first mu=merge blocking=1 integration=conflicts:DECISIONS.md,ara/runtime/calls.py,config.yaml,tests/integration/negative_controls.py,README.md merged_tests=723/725

## Follow-up: omega

Reviewed Omega `047274986b0099c8122d8250e0214089d4a5b781` against `0e0a7fc`, including both provider briefs and the revised Round 2 isolation contract. **Omega: fix-first. Three blocking findings below: two implementation defects and one explicit process-visibility contract mismatch.** Together with original finding F1, four blockers remain across the reviewed branches. No source-branch edits, real credential inspection, paid calls, or delegation occurred.

The user's later instruction supersedes separate four-branch integration: Xi owns the combined branch and its head will be supplied for a final check. No verdict on that future integrated head is implied.

### F6 — JSON-escaped credentials bypass the output guard (P1, blocking)

`ara/runtime/claude_code.py:263` searches the raw stdout/stderr/debug strings for the literal OAuth token. JSON decoding follows at line 266; the decoded object is subsequently scanned only for operator name/email at lines 296–299. The decoded structured output then enters the native event log and cache.

Independent reproduction used only the fixture's synthetic token and fake executable. The executable returned that token as a formula name using JSON Unicode escapes. The native call accepted it, and the decoded token appeared in **both the event log and response cache**. This is not an observed leak of the machine's real credential; it proves the guard fails for a valid JSON representation of the same secret. The existing encoded-identity regression covers identity, not credentials.

Before merge, scan decoded JSON string values for the credential before copying any untrusted field into a persistable receipt or response. Apply the corresponding guard on cache replay and add an encoded-credential regression that checks every retained artifact. Preserve only sanitized numeric/accounting evidence on rejection. Evidence: `psi-evidence/omega/check_encoded_credential.py` and `encoded-credential.txt` (boolean outcomes only; synthetic fixture content is removed with its temporary directory).

### F7 — Targeted construction bypasses provider backoff (P1, blocking)

The new retry logic lives in `ara/runtime/calls.py:253–265`, reached through `ModelCalls.call`. Native targeted construction instead invokes `_call_once` directly at `ara/runtime/construction.py:132` and `:169` when `construction_targeted_corrections` is 0 or 1. The supplied `extraction-full` profile enables that path with value 1. A retryable `ClaudeCodeError` consequently escapes the construction wrapper rather than using bounded retries and the normal `Rejected` boundary.

Independent fake-executable runs through `construction_call` confirmed both rate-limit and usage-limit cases: **configured retries=2, actual stage subprocesses=1, retry events=0, escaped exception=ClaudeCodeError**. This leaves the intended rich-source rebuild vulnerable to the first transient limit even though the direct formalization retry test passes.

Route ordinary and correction construction attempts through the shared transport retry boundary while keeping validation-correction budgets separate. Add coverage through this native construction caller. Evidence: `psi-evidence/omega/check_construction_retry.py` and `construction-retry.txt`.

### F8 — Environment handoff does not satisfy “never exposed in ps” (contract blocker)

`ara/runtime/claude_code.py:159–175` passes the OAuth token in the child environment, as requested. It is absent from the command arguments. However, a child under the same Unix identity has an inspectable environment on this host.

An independent test observed the actual fake-provider subprocess while it ran, with only a synthetic token. Ordinary `ps -o args` did **not** contain the token; **same-user `ps eww -o args` did**. The test captured this in memory and emitted booleans only; it did not print or retain a real process environment. Evidence: `psi-evidence/omega/check_process_environment.py` and `process-environment.txt`.

The unconditional follow-up requirement that the token never be exposed through `ps` is therefore unmet. This is distinct from placing the token in argv or logs, and it is not evidence of exposure to another Unix user. Before claiming that requirement satisfied, either establish a process-isolation boundary that prevents the relevant inspection or explicitly revise the threat model to permit same-user environment access. Merely redacting event logs cannot change this result. The requested environment handoff and a blanket no-`ps` promise cannot both be claimed for the current same-user launch.

### F9 — Isolation, schema and accounting evidence and limits

The implementation creates a fresh temporary cwd/config directory and UUID session per process, checks ancestor instruction files, disables user settings/slash commands, uses safe mode and empty strict MCP configuration, disables memory/session persistence, and supplies an empty tool list. The revised contract permits Anthropic built-ins and StructuredOutput. The canary checks empty instruction/memory/skill fields, forbidden names/paths in visible context and debug output, required debug markers, and operator identity in decoded output. It runs uncached when a native ModelCalls context opens. Discovery uses a bounded registry inventory plus private configured supplements; absent project names require that supplement. A canary is evidence for the tested version/environment, not a proof about every future CLI release.

I inspected the final author canary summary: CLI 2.1.306, 49 forbidden terms, passing checks. I did **not** repeat the live canary or stage smoke because this review prohibits paid calls. The author's reported 3/3 native stage smoke and 715 passed/2 skipped plus 326 controls remain author evidence, distinct from my checks. The author's disclosed unrecorded direct diagnostic means its successful-run subscription total is not a complete whole-task spend total.

StructuredOutput `tool_use` is accepted only with a successful receipt, pinned served model, structured output and no permission denials/server tool use; ModelCalls still validates the original complete schema locally. The transport drops only `$schema` for CLI compatibility. Effective CLI context differences and built-in defaults are disclosed.

Valid CLI cost equivalents remain under `subscription_usage`, while new API `cost_usd` is zero. Imported extraction charges remain visible. Token/context admission remains active; missing receipts consume a disclosed reservation rather than claiming measured usage. Direct-call bounded retries, timeout/error sanitization, per-instance process concurrency, local schema rejection, fresh canaries, and encoded identity rejection passed the existing offline tests. That evidence does not cover the F6/F7 paths. The tool-free provider intentionally refuses extraction and `search_evidence`; a complete composition workflow needing external retrieval still requires an explicit retrieval-capable route.

### F10 — Executed follow-up checks and deferred integration

Independent checks on unchanged Omega head:

- `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked pytest -q tests/runtime/test_claude_code.py`: **34 passed**, exit 0, 9.75 seconds. Transcript: `psi-evidence/omega/provider-tests.txt`.
- Three additional offline reproduction scripts completed exit 0, confirming F6, F7 and F8. They use disposable fixture homes, a fake executable and a synthetic credential. They make no network/model calls. Their exit 0 means the reported defect/constraint mismatch was reproduced, not that the behavior is acceptable.
- Omega remains clean at `0472749`; `git diff --check` passes. No fixes were applied.

Before the user's scope update, an initial scratch Omega merge encountered conflicts in `DECISIONS.md`, `README.md`, `ara/runtime/budget.py`, `ara/runtime/calls.py`, `config.yaml`, and `tests/integration/negative_controls.py`. After the update I aborted it without resolution edits. The scratch clone is clean at the previously verified three-branch head `f4a19b5`; its 723/725 suite and 341 controls remain valid for that tree only.

**Four-branch integration, full merged suite and merged control runner are deferred to Xi's forthcoming integrated head.** No four-branch test count or clean-merge claim is made. Final checking must inspect the shared budget/reservation reconciliation and stage-provider/preflight/retry wiring as well as the reported blockers. The trailer uses `integration4=deferred-to-xi` rather than a false clean/conflict verdict on an unprovided integrated head, honoring the later user instruction; `merged4_tests=0/0` means unexecuted.

### Follow-up finding placement

| Finding | Section carrying it |
| --- | --- |
| 6. Encoded credential reaches native log/cache | F6 |
| 7. Targeted construction bypasses transport retries | F7 |
| 8. Same-user process-environment visibility conflicts with blanket ps requirement | F8 |
| 9. Accepted isolation/schema/accounting behavior and live/whole-task/retrieval limits | F9 |
| 10. Independent checks, clean source state and explicitly deferred integrated verification | F10 |

10 findings, 10 placed (five original findings plus five follow-up findings).

DONE psi omega=fix-first blocking=3 integration4=deferred-to-xi merged4_tests=0/0

## Final

Reviewed integrated Xi head `76fa0b5fb7b9b9ff173239d5610073afed87bae4` against `main` / Sigma `2195a2dc15e4b636a8f168a9fc7b6dc822335c1e`. Mu `cdc9753` and Omega `1d54a53` (including `0472749`) are ancestors. Read the requested Round 7/Round 3 briefs and reports. Independent verification uses a detached, exact-head clone at `/home/dev/ara-work/psi-final-check`; no source-branch edits, delegation, paid calls or push.

**Verdict: fix-first, two blocking findings. F1, F6, F7 and F8 are resolved on this head, but the requested subagent pilot is not ready: its real-literature plan has 5,296 singleton windows and a zero commitment cap, and distinct correction-stage model settings are overridden.** This verdict supersedes the earlier branch verdicts for this integrated head only.

### F11 — Aggregate subscription reservation is mistaken for request size (P1, blocking)

`ara/runtime/claude_code.py:144–150` deliberately reserves two CLI turns: with initial input size `S` and maximum output `M`, the returned input reservation is `2*S + M`, with output reservation `2*M`. This is a campaign-accounting allowance, not the initial request size. `ModelCalls.count_request` computes the initial context correctly for its admission event, but returns the aggregate estimate (`calls.py:575–591`). Construction then uses that aggregate `.input_tokens` to partition source windows (`construction.py:246–247`) and to size its working envelope and closure copies.

With the approved pilot's 64,000 construction-output allowance, even an empty encoded payload has an input reservation above `2*16,384 + 64,000 = 96,768`, before prompt/schema bytes. It cannot fit the 70,000 batch-input bound. The real-literature plan therefore splits all **5,296 evidence items into singleton windows**. Their recorded input reservations range from **128,836 to 153,808**, all above the bound. The initial share and fixed window cap both become **0**, despite the requested multiplier 2 that previously gave cap 6. Execution checks oversized batches and zero caps before generation (`construction.py:346–352`), so this plan cannot build a nonempty T. A planner exit of 0 is not a usable pilot plan.

Separate initial-context size and cumulative transport usage at the counting contract, retain conservative reservations for billing/admission, and audit construction's downstream working/catalogue calculations for the same unit mismatch. Add native subagent construction-plan coverage under the real pilot limits before attempting the pilot. Do not solve this by simply relaxing the 70,000 bound or declaring a cap of 6 independent of the computed plan. Even after separating the quantities, the conservative byte-based estimator may produce a different window count from the historical API plan; that must be measured again.

Evidence: `psi-evidence/final/offline-plan-batched/summary.json`, `offline-fresh-run/summary.json`, their complete plan artifacts and `count-observations.json`; the unchanged production estimator and planner were used. The offline execution boundary and logging instrumentation are disclosed in F15.

### F12 — Correction-stage model override is undone at provider resolution (P1, blocking)

`construction_stages.dispatch_settings` correctly merges `construction_correction` over the original stage and `_for_construction_stage` constructs the scoped provider from those settings. However, the scoped configuration retains the original nested `stages` mapping. `ClaudeCodeProvider.model_for` (`claude_code.py:135–136`) calls `stage_settings(config, kind)` again, which reapplies `stages[kind]` after the already resolved correction settings (`providers.py:186–192`). The original stage's model wins. The stage manifest still advertises the correction model.

Independent native `construction_call` reproduction configured selection as `claude-opus-4-8` and correction as `claude-opus-5-5`. The fake executable and native MODEL receipts show **4-8 for the initial call and all three correction transport attempts**. The latter receipts say `dispatch_stage=construction_correction`, so the label alone falsely suggests that the intended routing took effect. This also means current passing stage-dispatch tests do not prove native correction-model selection. The shared `stage_settings` consumer warrants checking both API and CLI routes; the executed reproduction here uses CLI.

Resolve stage settings once, or make correction precedence explicit through the provider's model/effort/system resolution. Preserve independently selected providers, canaries and retry policy. Add a native regression with distinct original and correction model settings, comparing actual subprocess arguments/receipts with the manifest. Evidence: `psi-evidence/final/check_stage_routing.py` and `stage-routing.txt`. The all-5-5 pilot manifest does not expose this defect by itself.

### F13 — Prior blockers resolved, with their actual boundaries

**F1:** `SearchPublication` journals each job durably and publishes journal events in input-target / positive-negative order after workers drain, including failure paths. The main chain records the journal roster before dispatch and binds journal/anchor hashes at publication. The native four-job regression checks the complete logical stage sequence and receipt order under forward/reverse schedules; the twenty-search regression forces distinct completion orders and compares routes, analyses, sidecar bytes and receipt order. Both passed in the independent full suite. Interrupted publication is visible: methodology marks accounting incomplete and Budget refuses reopening; it does not silently treat main-chain totals as a complete bill. This is fail-closed recovery, not automatic replay. Stable logical publication does not imply identical timestamp/UUID/hash bytes or identical outcomes under tight concurrent budgets.

**F6:** Raw scanning remains, followed by recursive decoded string/key scanning before retaining CLI fields. Nested JSON strings and replayed cache responses are checked; contaminated cache entries are evicted. Only sanitized numeric accounting and locally generated routing data survive rejection. The Unicode-escape, nested/key/routing-field, special-character credential and cache-replay regressions passed with synthetic credentials.

**F7:** Both ordinary and targeted construction attempts now traverse `_transport_call`. Native construction tests cover both stage kinds, correction settings None/0/1, rate/usage limits, and targeted correction retries. Exhaustion produces `Rejected`; retries do not consume additional validation corrections. F12 is a distinct settings-precedence defect, not a recurrence of the missing transport boundary.

**F8:** The requested `config-link` receipt vocabulary describes a **private copy, not a symlink or hardlink**. A fresh temporary tree holds a 0600 OAuth snapshot containing inference-only discovery metadata, no refresh credential and no MCP credential/settings. The config-file path sends no OAuth token in the child environment. The fake executable enforces those properties; tests verify same-user `ps eww` contains neither synthetic access nor refresh token, the original credential bytes are unchanged, and the temporary config is removed after success, error and timeout. `TemporaryDirectory` supplies cleanup and a private parent; abrupt process/host termination is not a proven cleanup guarantee.

The operator's revised threat model explicitly permits same-user access to the original credential and environment-only fallback when no credential file exists. Root is outside the boundary; inference-only metadata does not reduce server-side token permissions. These are documented limits, not a blanket “never in ps” promise. No real credential was inspected for this review, and Omega's live canary/stage evidence was not independently repeated.

### F14 — Integration preservation and independent gates

Compared the integrated tree with Psi's prior scratch resolutions and the source branch revisions. Sigma's closure-budget/stage modules and owning tests, and Mu's verification/extraction/provenance modules and receipt tests, remain byte-identical. The recorded Sigma/Xi and Mu merge resolutions are preserved; the `_call_reserved` stage-dispatch control adaptation remains. Omega's provider, credential/retry fixes and tests survive, alongside Xi's stable publication and shared reservation changes. Both documentation histories are retained. Evidence: `psi-evidence/final/integration-comparison.json` and the integrated commit graph/diff. No lost branch change was identified; that does not negate the integration defects in F11/F12.

API and subscription calls share the atomic ledger; billing follows the actual stage provider. Mixed-provider tests cover CLI stages under API defaults and API stages under CLI defaults, scoped canaries/retries and retained API pricing. Subscription usage remains separate from API USD, and imported extraction charges remain visible. Mu's verification tests passed; its real-lineage timing benchmark was not repeated, and the earlier local-chain/anchor and non-atomic snapshot limits still apply.

Executed on that exact head, sequentially:

- `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked pytest -q`: exit 0, **789 passed, 2 skipped / 791 collected**, 489.65 seconds. Both skips are opt-in live-provider checks.
- Only after pytest completed, `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked python tests/integration/negative_controls.py`: exit 0 in 1,577.19 seconds, **366/366 mutations exited 1 and all 366 restorations exited 0**.
- All 366 anchors occur exactly once; none of the prior 341 controls was removed. All tracked files, including all 31 mutation-target files, match their pre-gate SHA-256 hashes. The verification clone and Xi source checkout are clean at the requested head; `git diff --check` passes.

Inspected the actual failures for all 25 added controls and six relevant existing controls. Publication mutations fail on receipt order; interrupted-accounting mutations lose refusal/incomplete reporting. Decoded/cache credential mutations fail to reject, and construction retry mutations let `ClaudeCodeError` escape. Auth mutations trigger the fake executable's unsafe-configuration refusal. The retry-loop mutations reach the explicit `unreachable` assertion after eliminating required attempts; this is a broken retry path, not a syntax/signature failure. The two long equivalence mutations fail on trace bytes and routes respectively. The preserved stage-dispatch mutation fails on the wrong provider/model, not an argument-signature error.

Evidence: `psi-evidence/final/{pytest.txt,controls.txt,gate-status.json,source-before.json,control-preflight.json,control-review.json}`. All 732 individual red/green transcripts and `results.json` are retained in `/home/dev/ara-work/psi-final-check/runs/delta-controls/`. These passing gates do not cover the F11/F12 combinations exposed by the additional native probes. No separate lint/typecheck gate is configured for this ARA checkout.

### F15 — Offline pilot execution and refusal

Used Zeta's authoritative `/home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt`, SHA-256 `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`, and the approved `overnight6-control/config.yaml` pilot basis: 48,000 catalogue, 233 growth reservation, 100,000 working budget and 200,000 context. Set `--audience ''`, `search_concurrency=4`, window-cap multiplier 2, provider `claude_code`, pinned model `claude-opus-5-5`, and matching construction-stage overrides. Every executable invocation used the fixture's fake `claude`, disposable synthetic credentials and fake HOME; network connections were forbidden by the probe. No real provider call occurred.

Completed both a count-only `plan-construction` and a **fresh native `run` stopped immediately after `build_t_budget_plan`, before construction generation**. No part-6 construction state or batches were imported/restored. The normal extraction-provenance lineage remains verified/imported, as required for the source artifact; “fresh” does not erase those extraction receipts. Count-only planning launched no fake model process; the native run launched one fake isolation canary. Both produced plan ID `8a1f510d8eee7d8f8f7f614f0e3914d6b8afc327a54b7664320c6d5324c352f9`, **5,296 windows / initial share 0 / cap 0 / 5,296 oversized windows**.

The manifest routes selection, formalization and both correction entries to `claude_code` / `claude-opus-5-5`, high effort and adaptive thinking. Parallel search is configured at 4; search was not reached because this proof stops at planning. Distinct correction routing fails the separate F12 probe. No 48-window/cap-six plan, useful frozen T, live speedup, full pilot, literature coverage or completed search is claimed. The tool-free provider still needs an explicit retrieval-capable route for external evidence acquisition during composition.

**Instrumentation limit:** the first fully logged plan was interrupted after 334 context events because repeated full-chain verification made the thousands-of-windows diagnostic slow. For both completed probes, non-billable context-count events were collected outside the chain with prompt hashes instead of appending every full prompt to the native log. The estimator, partitioner, budgets and generated plan were unmodified; the fresh native run retained its canary and plan events and was deliberately intercepted at the plan boundary. This proves the planning result, not completion of an uninstrumented native run. Scripts and transcripts: `psi-evidence/final/offline_plan.py`, `offline_plan_batched.py`, `offline_fresh_run.py`, the matching console files and output directories.

**Offline verdict: refused.** This is the review's refusal to authorize a pilot from an unusable plan, not a claim that the CLI itself returned a refusal exit code. Fix F11/F12 and repeat the offline plan and native routing proof before any real pilot call.

### Final finding placement

| Finding | Section carrying the current outcome |
| --- | --- |
| F1: event ordering, now resolved | F13 |
| F2: cap/fresh rebuild/stage claims and current failure | F11, F12, F15 |
| F3: concurrent reservation/equivalence limits | F13, F14 |
| F4: verification cache/trust/timing limits | F14; original F4 retains measured timing |
| F5: earlier integration and current preservation/gates | F14; original F5 retains historical conflicts |
| F6: decoded credential rejection, now resolved | F13 |
| F7: construction retries, now resolved | F13 |
| F8: authentication lifecycle and revised threat model | F13 |
| F9: isolation/schema/accounting/live/retrieval boundaries | F13–F15; original F9 retains earlier evidence |
| F10: formerly deferred integrated verification | F14 |
| F11: aggregate reservation makes the pilot plan unusable | F11 |
| F12: correction-model routing disagrees with configuration | F12 |
| F13: prior fixes and remaining recovery/auth boundaries | F13 |
| F14: integration preservation and executed gate scope | F14 |
| F15: real-source offline result, instrumentation and pilot refusal | F15 |

15 findings, 15 placed. Two active blockers; four earlier blockers resolved.

DONE psi final verdict=fix-first blocking=2 tests=789/791 negctl=pass offline_plan=refused

## Final 2

Reviewed Omega `fix/subagent-final` at `852b21796191111c916be944648e3a42cac359ec`, against integrated base `76fa0b5fb7b9b9ff173239d5610073afed87bae4`. Read the Round 4/5 briefs, decisions and report sections. Independent gates ran in `/home/dev/ara-work/psi-final2-check`; offline probes used the unchanged subject checkout and separate evidence directories. No source-branch edits, delegation, real credential inspection, paid calls or push.

**Verdict: merge, zero blocking findings. F11 and F12 are resolved. The independent offline plan is usable as a capacity projection: 70 windows, cap 4, all 70 funded. Actual contributions and exact token/context guarantees are not established by this empirical estimator or offline run.** This supersedes the prior fix-first verdict for the reviewed head.

### F16 — F11 and F12 resolved at their native boundaries

**F11:** `RequestCount` explicitly separates `initial_input_tokens`, provider-specific `context_output_tokens`, and cumulative `reservation`. Construction partitioning, working-envelope calculations, closure copies, catalogue deltas and final acceptance consume initial input size. Downstream context acceptance adds the provider's output allowance. The model boundary and paper/campaign accounting retain the aggregate reservation; extraction range partitioning uses initial input while its returned usage remains the reservation. Reconciliation consumes the admission side effect only. I inspected all production `count_request` callers; no remaining use of aggregate input as construction context size was found.

For CLI calls the reservation still has input `2*initial + maximum_output` and output `2*maximum_output`. API search retains future tool-iteration reservations separately from initial context. The independent native plan below confirms that the former 5,296-singleton/zero-cap failure is gone; the new count-contract tests also exercise the real pilot limits without generation.

**F12:** construction dispatch resolves category, exact kind, then correction overrides, and clears nested `stages` on the scoped configuration. The native provider cannot reapply the original kind over correction settings. The manifest uses the same resolution. Re-running Psi's original reproduction now records selection on **4-8**, followed by **5-5 for all three correction transport attempts**, with attempt numbers 1,2,2,2. Evidence: `psi-evidence/final2/check_stage_routing.py` and `stage-routing.txt`.

The owning CLI regression compares actual fake-executable model/effort/system arguments and requested/served receipts with the manifest. The API regression uses the real provider with a fake SDK, comparing counted and generated request settings, receipts, thinking and fallback removal. These are included in the independent full gate. Shared budgets, per-stage canaries and bounded retries remain on the native path. Earlier F1/F6/F7/F8 safeguards are retained; their prior trust and recovery limitations remain in F13.

### F17 — Calibration provenance, upward correction and context limits

Independently rebuilt the table from its seven recorded API/CLI source logs, verifying chains and separate anchors, source hashes, and the selected event/prompt/schema identities. The rebuilt object matches the committed table exactly. File SHA-256: `73fbae14a14907710300e25d3db6b3fd2baa79ac8b031edb9a1f68c1022ec76e`; canonical table hash used in runtime receipts: `7474c9e793c07eb37cc7dd59885b71ba6ab247845b91efdef6509449fe1100ea`. These two hashes intentionally cover different byte representations.

| Request kind | Deduplicated real API samples | Nearest-rank p99 | Upward-rounded p99 × 1.05 |
| --- | ---: | ---: | ---: |
| build_t_batch | 381 | 0.5268793948670172 | 0.553224 |
| select_t_roots | 453 | 0.5253168432008817 | 0.551583 |
| propose_targets | 94 | 0.4637438800797856 | 0.486932 |

The fallback is 0.553224. Eight retained, measured CLI receipts supply additive overhead **949 tokens**, calculated from the largest positive residual with a 5% margin. The factors alone cover every retained API sample; the overhead covers the retained CLI samples. Numeric pairs and provenance hashes are committed, not source content. Evidence: `psi-evidence/final2/check_calibration.py`, `calibration-console.txt` and `calibration-verification.json`. This is actual receipt reconstruction, not just a recalculation from the table's own numbers.

Runtime correction is model/kind-specific and upward-only under a lock. Measured aggregate CLI input includes cache reads/writes; an overshoot raises the factor with margin, while smaller later or concurrent observations cannot lower it. Scoped providers share the state, and reopening restores matching-table observations. Measured rejected responses can train it; cache replays and failures without measured usage do not. Existing reservations are not enlarged retroactively, and actual usage still settles the ledger. These behaviors have native fake-CLI regressions and production-wire controls in the full gate.

**Context-bound qualification:** a statistical estimate cannot guarantee that every oversized request is stopped before dispatch. Local admission enforces the configured bound against the estimate; the CLI/service enforces its own actual context limit. Those are different claims. The code and decisions correctly describe this calibration as a forecast, not a tokenizer bound. The sample is API-derived with only eight CLI overhead observations, so unfamiliar inputs and future CLI behavior can exceed it. Comparing aggregate two-turn usage to an initial-context estimate is deliberately conservative and may also raise future estimates substantially, reducing later capacity.

Independently injected both a structured CLI context-error receipt and a plain nonzero-exit context error through native construction. In both cases the local estimate fit, the fake CLI was called once, native execution raised `Rejected(cli_exit_error)`, no transport retry occurred, and no response was cached. The structured response retained measured accounting; the plain error remained `reservation_unknown_actual` / incomplete. Evidence: `check_context_refusal.py`, `context-refusal.json` and its console transcript under `psi-evidence/final2/`. Thus a reported CLI context failure is not accepted as successful construction. This offline check does **not** establish a literal never-dispatch guarantee or live enforcement of a configured limit by the service. No live context-limit or rate-limit probe was authorized or run.

### F18 — Allocation policy and independently reproduced real plan

The minimum-allocation guard is disclosed in README, DECISIONS and the plan. If positive global capacity is below the number of windows, and one item can fit the input allowance, it funds one initial slot in each earliest window until capacity is exhausted. The plan records the share/cap vectors, funded count, global capacity and allocation rule; unfunded windows are skipped. A zero-capacity plan still refuses an empty T. Native placeholder coverage verifies two funded windows dispatch/freeze and the third skips; arithmetic coverage verifies `[1,1,1,0,0]` for three slots over five windows. Fixed caps and actual closure/global recounts remain active. Soft borrowing can still exhaust capacity before a later funded window, so funding is not guaranteed contribution.

Independently executed both count-only planning and a fresh native `run`, using the authoritative real artifact `/home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt`, unchanged SHA-256 `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`. Used the approved pilot limits, `--audience ''`, multiplier 2, parallel search configuration 4, and CLI/5-5 stage routing. Both plans match exactly:

- **70 windows, initial share 2, fixed cap 4, 70/70 funded and potentially contributing.**
- **160 global slots; 140 projected commitments.** Wrapper 4,397, copy cost 239, growth reservation 233, working allowance 75,603 after headroom/wrapper.
- Initial input estimates **32,309–68,523**; no window exceeds the 70,000 input allowance.
- Plan ID `17c3e1a07f9dc3130bd467e5ee10332928bc8bb7f2b8d779ac22f2a0f6833f66`, matching the author's final plan.

The historical API plan remains **48 windows / cap 6**, not a new API token count executed here. The approved calibrated estimator yields 22 more windows and cap 4; no bound was raised or cap forced to recover the historical result. The scarce-slot fallback is not needed by this 70-window plan, because all windows receive positive equal initial shares.

Count-only planning launched no model process. The fresh native run launched **one fake canary**, then was deliberately stopped immediately after its budget-plan event, before construction generation. It restored no construction batches and imported no part-6 construction-resume state; normal extraction-provenance verification/import remains intact. Both native chains and anchors verified. Full non-billable count events were batched using native `emit_many` to avoid repeated whole-chain verification; prompts/events remain in the chain, and the estimator, partitioner and allocation were unmodified. The fake executable, synthetic home/credentials, subprocess allowlist and network-denying hook prevented real provider use.

Evidence: `psi-evidence/final2/offline_plan.py`, `offline_fresh_run.py`, their output directories/transcripts and `offline-verification.json`. **Offline plan: ok**, as a feasible allocation under the disclosed estimator. “70/70 contributing” means potentially contributing; no real window was selected/formalized, no T was frozen, and search was not reached. Useful coverage, live speedup and completion remain unproven. The tool-free provider still requires an explicit retrieval-capable route for external evidence during composition.

### F19 — Independent gates and final scope

Executed on the exact subject head, sequentially:

- `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked pytest -q`: exit 0, **799 passed, 2 skipped / 801 collected**, 508.51 seconds. The two skips require live providers.
- Only after pytest completed, `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked python tests/integration/negative_controls.py`: exit 0 in 1,596.80 seconds, **375/375 mutations exited 1; all 375 restored tests exited 0**.
- All 375 mutation anchors occur exactly once. No prior control was removed; nine were added and thirteen existing controls were retargeted. All tracked files, including all 33 mutation-target files, match the pre-gate SHA-256 snapshot. Both the source checkout and verification clone remain clean at `852b217`; `git diff --check` passes.

Inspected all nine new red transcripts: the context-unit mutation produces eight windows instead of one; reservation mutation loses the two-turn input allowance; both native CLI and API correction mutations select 4-8 instead of 5-5; the uncalibrated estimate differs from the measured table; learning/sharing/reopening mutations lose the expected raised factor; and removing the scarce-slot guard leaves an empty working T. These are behavioral failures, not syntax or broken-signature failures. Also inspected the thirteen retargeted existing controls and both long parallel-equivalence failures, for 24 retained failure excerpts.

Evidence: `psi-evidence/final2/{pytest.txt,controls.txt,gate-status.json,source-before.json,control-preflight.json,control-review.json,final-verification.json}`. All 750 individual red/green transcripts and `results.json` remain in `/home/dev/ara-work/psi-final2-check/runs/delta-controls/`. There is no separate configured lint/typecheck gate. The calibration table is declared as package data; the author's wheel-build check was read, not independently repeated.

One retained control has an existing proof limitation: removing the working-T acceptance guard in `rich_working_allowance` reaches an immutable-artifact collision, rather than the intended allowance rejection. I checked its red transcript on both this head and the previously reviewed `76fa0b5`; the same failure mechanism occurs on both. The mutation is detected and restoration passes, but that red alone is not clean proof of the intended boundary. Other retained controls can fail at a later global guard. This is not a newly introduced production defect, and no stronger claim is inferred from their exit codes.

This is a source-review and offline-plan verdict on `852b217`, not a merge, push or authorization of paid execution. Source inspection, recorded calibration reconstruction and fake-provider behavior support the conclusions. No additional live evidence is claimed.

### Final 2 finding placement

The fifteen earlier findings remain in their original named sections. Their current dispositions are: F1/F6/F7/F8 resolved with the F13 boundaries; F11/F12 resolved in F16; F2's current cap/coverage outcome and F15's former offline refusal are superseded by F18; F3/F4/F9 trust, concurrency, provider and live-evidence limits remain applicable; F5/F10/F14's current verification status is in F19. New findings are placed as follows:

| Finding | Deliverable section |
| --- | --- |
| F16: explicit counting contract and native correction routing resolve F11/F12 | F16 |
| F17: real calibration provenance, upward-only learning and context-error/estimate limits | F17 |
| F18: disclosed minimum allocation, 70-window plan and potential-contribution boundary | F18 |
| F19: exact-head sequential gates, restoration and review scope | F19 |

19 findings, 19 placed.

DONE psi final2 verdict=merge blocking=0 tests=799/801 negctl=pass offline_plan=ok
