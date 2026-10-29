# Tau2 independent review

**Omega: merge. Rho2: fix-first. One blocking defect.** Reviewed Omega `7e5219a837de0ed126c50c2dbbe8dc49036f68e9` and Rho2 `cc705c7e37ac607c1546cd8218f46bf503c99f5b` against `50ddc05`. This is a non-author review performed directly, without delegation, paid calls, credential changes, author-branch edits, or push.

## Blocking finding — Rho2 confidence dilution

**F1 / P1: unchanged clean characters can make a low-confidence glyph replacement pass.** [ocr_spans.py:129](/home/dev/ara-work/rho2/ara/runtime/ocr_spans.py:129) calls `insertion_confidence` over the entire replacement whitespace run. That includes clean fragments retained verbatim, although only the damaged glyph replacement supplies new source text. The averaging at [ocr_spans.py:24](/home/dev/ara-work/rho2/ara/runtime/ocr_spans.py:24) allows those unchanged characters to conceal uncertainty in the actual repair.

Minimal placeholder reproducer: original `Q ` + `P` repeated 30 times + U+E000 + ` R`; OCR proposes the same text with `S` replacing U+E000. Give the preserved characters probability 0.999 and `S` probability **0.10**. Both anchors are unique, clean fragments match exactly, and production `repair_spans` **accepts**: mean confidence **0.97**, low-confidence share **1/31 = 3.23%**. A replacement scored 0.94 also passes. The same reproducer through native `recover_papers` makes tier 1 refuse, then tier 2 accept, publish `ocr_spans`, and clear the sole page diagnostic. This contradicts the required low-confidence refusal for newly inserted text.

Fix before merging Rho2: identify the candidate ranges corresponding to damaged glyph groups, calculate admission confidence on newly synthesized characters, and refuse ambiguous clean-fragment alignment conservatively. Preserve the clean fragments exactly. Add a regression and production-wire mutation control for a low-score replacement attached to a long high-score clean fragment, plus the corresponding high-score accepted case. Do not merely raise an aggregate threshold.

Evidence: [reproducer](/home/dev/ara-work/reports/tau2-evidence/ocr-confidence-probe.py), [results](/home/dev/ara-work/reports/tau2-evidence/ocr-confidence-probe.json), [native intake result](/home/dev/ara-work/reports/tau2-evidence/ocr-confidence-native.json). This defect is reproduced on synthetic input. An independent recalculation of all **11 accepted VL repairs** in the retained real-corpus receipts found **zero additional refusals** when scoring only inserted characters. Thus the review does not claim that this particular defect corrupted those saved repairs.

## Omega — credentials, isolation and diagnostics

No blocking defect found in the requested scope. `codex_cli.auth_file` is required, and the committed configuration selects `/home/dev/.config/ara/codex-home/auth.json`. There is no implicit `~/.codex` or inherited `CODEX_HOME` fallback. The source is opened fresh per call; validation/scanning and the read-only bind use the same open descriptor. The ephemeral `CODEX_HOME` begins with a symlink to that mount. The credential is not copied into a new file, and refresh is disabled. Fake-binary tests exercise replacement between calls, read-only writes, API-key refusal, missing selected auth, and bounded auth re-read.

Each call uses an empty cwd, isolated home/process mounts, the pinned CLI version, ephemeral sessions, ignored user configuration/rules, disabled bundled skills/memory, and task-only instructions prohibiting tools. The event parser allowlists lifecycle/message/reasoning/error events and rejects every tool or unknown event before admitting output. Diagnostic retention is limited to fixed categories and numeric metadata; credentials and runtime git identity are scanned before accepted output retention. Local schema validation remains authoritative. `extract_paper` and web-evidence retrieval refuse on this transport; new extraction still requires its API configuration, and imported extraction receipts retain their original provenance.

Applied the **Round 12** rule: empty skills/memory/AGENTS/CLAUDE fields and forbidden-content/identity scans remain mandatory; generic visible tool definitions are permitted and disclosed in receipts and methodology. Definitions do not authorize execution. The review does not substitute the superseded Round 11 empty-tools rule, nor claim event rejection alone prevents every possible side effect of attempted tool execution.

Independently verified the retained Round 12 EventLog chain and all **169 source-manifest files** against Omega's requested head. Those author-executed receipts show an accepted canary, `formalise`, and `map_leaf`, totaling **15,861 tokens**. No new live request was made in this review. Evidence: [receipt audit](/home/dev/ara-work/reports/tau2-evidence/omega-receipt-audit.json).

## Omega — accounting and limits

The requested model is pinned; omitted serving identity remains **`unverified`**, including in the retained live smoke. Calibration starts from the measured Anthropic API table, explicitly discloses the different tokenizer, and adjusts upward using like-for-like Codex usage with cached input counted once. It is not a proven Codex token bound. Subscription calls remain separate from measured API spend; Codex's USD equivalent is unavailable, rather than a measured zero equivalent. Retries/backoff are bounded and failed calls retain measured usage or explicit reservation accounting.

The CLI has no hard output-token cap. Configured output sizes are admission reservations, and excess actual usage can stop the run after a response. Pilot operation must retain these disclosures and must not treat this review or a plan as model-quality, full-run, or serving-identity proof.

## Rho2 — preservation, provenance and pins

Reviewed the native intake, two-tier recovery, span alignment, confidence mapping, provenance, strict-missing and reuse paths. Unchanged source intervals are copied literally; exact clean fragments inside tainted runs are checked; both token anchors must occur uniquely in original and OCR streams and in order. Missing/ambiguous anchors, unmapped confidence and incomplete generation refuse. Tier 2 cannot overwrite accepted tier-1 repairs. Partial repairs retain diagnostics and `ocr_spans` provenance; physical pages remain unchanged. Textless whole-page recovery is separately labelled `ocr`.

Independent reconstruction from the retained author receipts covered **7 papers / 633 physical pages**, with **588 unchanged pages**, **44 pages containing accepted span repairs**, and **one textless-page recovery**. All **131 accepted spans** preserve their surrounding clean intervals and internal clean fragments. This is receipt reconstruction, not new OCR inference or a new visual transcription judgment. Evidence: [corpus audit](/home/dev/ara-work/reports/tau2-evidence/corpus-audit.json).

The author-reported corpus remains **131/678 repaired spans**, **547 unresolved**, and **9/82 diagnostically cleared pages**. The historical denominator 677 was corrected in Round 3. The author's visual review records a wrong recognized relation symbol among accepted repairs and pre-existing ordering/encoding problems even on a cleared page. Confidence and diagnostic clearance therefore do not establish accurate or complete transcription. F1 is an additional admission defect, separate from these disclosed recognition limits.

Exact dependency versions and distribution hashes are in `pyproject.toml`/`uv.lock`; model manifests record hashes and the VL revision. Independently verified both cached tier-1 models and the VL files against those manifests without downloading or running inference. Licenses are recorded in `DECISIONS.md` OCR2/OCR8; the VL license is itself hash-pinned. Optional installed-model tests are outside this review's default environment. Evidence: [pin audit](/home/dev/ara-work/reports/tau2-evidence/model-pin-audit.json).

## Integration and verification

Scratch clone: `/home/dev/ara-work/tau2-integration`. Started at `50ddc05`, merged Omega first, then Rho2. **One conflict: `DECISIONS.md`**, where both branches append sections. Retained both sections in merge order. `ara/runtime/cli.py` auto-merged; no implementation resolution was needed. The reviewed merged revision is **`ed84ff671f177b6633c0958d28450cf37b19c431`**. The scratch merge is not a merge of either author branch into the production repository.

`UV_OFFLINE=1 uv sync --locked` succeeded. Full pytest, repository controls and OCR controls were scheduled sequentially in a network namespace (`unshare -Urn`) using the locked merged environment. No provider network request was authorized or possible from that namespace.

Merged full pytest: **980 passed, 4 skipped / 984 collected**, exit 0, **587.54 seconds**. The skips are two paid-provider opt-ins and two installed-local-model opt-ins. Tracked source hashes match the pre-suite manifest.

Repository mutation runner: **411/411** controls failed under mutation (exit 1) and passed after restoration (exit 0), runner exit 0, **2158.85 seconds**. The separate OCR runner then passed **30/30** mutation/restoration checks, runner exit 0, **50.58 seconds**. Total: **441/441 controls**. All **180 tracked files** match their pre-gate hashes after each stage, and the merged tree is clean. `git diff --check 50ddc05 HEAD` passes. Both author branches remain clean at their requested heads.

Evidence: [full pytest log](/home/dev/ara-work/reports/tau2-evidence/pytest.log), [repository controls](/home/dev/ara-work/reports/tau2-evidence/repo-control-results.json), [OCR controls](/home/dev/ara-work/reports/tau2-evidence/ocr-control-results.json), [gate receipts](/home/dev/ara-work/reports/tau2-evidence/gate-results.json), [final state audit](/home/dev/ara-work/reports/tau2-evidence/final-verification.json). Individual red/green transcripts remain in the scratch clone's `runs/delta-controls/` and `runs/ocr-round3-controls/`.

The existing suite's success does not cover F1; its independent reproducer does. 

## Offline pilot plan

Used the actual published 26-paper literature artifact, SHA-256 `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`, with the pilot-4 configuration copied into review evidence and its Claude provider/model selections explicitly converted to **`codex_cli` / `gpt-6-luna`**. This conversion is necessary for a Codex pilot; merely adding the provider implementation does not migrate an old pilot config. Real credentials were replaced with synthetic credentials and an inspectable fake executable.

Native `plan-construction --profile pilot --token-counter provider` exited **0**: **70/70 windows counted and funded**, **zero uncounted windows**, **zero generation calls**. Largest planned request: **68,507 tokens**; reserved context: **192,507 / 200,000**. The four construction/correction manifest entries select Codex; checked search settings also select Codex. A separate native fake canary and `formalise` call passed through bubblewrap and normal ModelCalls. Other search stages were checked for routing configuration, not executed as a complete search.

The planner did not launch the fake CLI: its calibration estimator is local. Fake execution was tested separately so this distinction is explicit. Nonbillable context receipts were batched through `emit_many` with their original payloads; estimator, planner and admission logic were unchanged. All work ran with OS network isolation plus subprocess/socket guards. This confirms offline routing and planning, not a live pilot, new extraction, or incorporation of the OCR repairs into the old literature artifact.

Evidence: [script](/home/dev/ara-work/reports/tau2-evidence/offline-plan.py), [summary](/home/dev/ara-work/reports/tau2-evidence/offline-plan/summary.json), [config](/home/dev/ara-work/reports/tau2-evidence/offline-plan/config.yaml), [fake transport receipts](/home/dev/ara-work/reports/tau2-evidence/offline-plan/smoke-routing.json).

## Finding placement

| Action-relevant finding | Placement |
|---|---|
| 1. Blocking confidence dilution, fix, reproduction and no observed saved-corpus incidence | Blocking finding |
| 2. Auth/isolation/diagnostics checks and revised canary rule; retained live evidence only | Omega — credentials, isolation and diagnostics |
| 3. Unverified serving identity, calibration, subscription accounting and output limits | Omega — accounting and limits |
| 4. Clean-text proof, corpus counts and recognition/completeness limitations | Rho2 — preservation, provenance and pins |
| 5. Dependency/model/license verification and optional installed-model coverage limit | Rho2 — preservation, provenance and pins; Integration and verification |
| 6. Merge conflict, resolution and exact scratch revision | Integration and verification |
| 7. Exact tests/controls/restoration and offline/nondelegated review scope | Integration and verification |
| 8. Required pilot config migration, successful plan and routing proof boundaries | Offline pilot plan |

8 findings, 8 placed.

DONE tau2 review omega=merge rho2=fix-first blocking=1 integration=conflicts:DECISIONS.md merged_tests=980/984 offline_plan=ok

## Re-review

**Rho2: merge. F1 is resolved; zero blocking findings remain in this re-review.** Reviewed `9aad0132d3f78a5e18dac4f00a5e51365accbfc0` on `feat/local-ocr`, based on `7e5219a837de0ed126c50c2dbbe8dc49036f68e9`. This supersedes the earlier F1/fix-first verdict above; the original review is retained as historical evidence. Work was performed directly, without delegation, paid calls, fresh model inference, author-branch edits or push.

### F1 resolution and exact preservation

[The admission call](/home/dev/ara-work/rho2/ara/runtime/ocr_spans.py:190) now passes only the absolute OCR ranges replacing damaged glyph groups to `insertion_confidence`. Preserved clean fragments contribute neither to the confidence mean nor to the low-score share. The thresholds remain 0.95 and 5% below 0.8. Policy `local-ocr-v4-spans` records the confidence scope, synthesized ranges and alignment count and changes reuse identity.

Independent native `recover_papers` probes reproduce the original 30-clean-character case: replacement scores **0.10** and **0.94** produce admission means exactly **0.10** and **0.94**, leave the source page unchanged, retain its diagnostic and select `text_layer`. A **0.99** replacement accepts with **no confidence coverage on the preserved clean fragment**, demonstrating that clean text is excluded rather than merely downweighted.

The new alignment routine requires an exact full match of every clean fragment and one unambiguous allocation of candidate characters to damaged groups. Zero matches refuse as `clean_fragment_changed`; multiple matches refuse as `ambiguous_clean_fragments`. An independent recursive oracle matched the production routine on **76,755 exhaustive small cases**, including exact synthesized ranges for **13,526 unique matches** and correct refusal counts for **4,976 ambiguous cases**. Separate native probes confirm a changed clean character and repeated ambiguous fragments leave the original text untouched. Surrounding source intervals still use the unchanged literal-copy path.

Evidence: [probe script](/home/dev/ara-work/reports/tau2-rereview-evidence/independent-probes.py), [results](/home/dev/ara-work/reports/tau2-rereview-evidence/independent-probes.json).

### Regression and mutation evidence

The new native regression `test_low_score_glyph_is_not_diluted_by_clean_fragment` covers both 0.10 and 0.94 replacements. The `synthesized-confidence` control restores the defective whole-span call, `insertion_confidence(result, ((a, b),))`. In this re-review, **both parameterized cases failed under that mutation (2 failed, exit 1)** and **both passed after exact source restoration (2 passed, exit 0)**. The retained red transcript shows test assertion failures, not a collection error. [Red evidence](/home/dev/ara-work/reports/tau2-rereview-evidence/synthesized-confidence-red.txt), [restored evidence](/home/dev/ara-work/reports/tau2-rereview-evidence/synthesized-confidence-green.txt).

The corresponding high-score regression verifies acceptance without clean-fragment confidence coverage. Additional tests and controls cover ambiguous internal alignment, exact clean-fragment preservation and multiple damaged groups separated by clean text. These checks exercise the production path.

### Rebase and conflict resolution

Verified `7e5219a` is an ancestor of `9aad013`. The **complete Omega `DECISIONS.md` file remains an exact prefix**, and the **complete original Rho2 appended sections remain present**. Both sides of the earlier conflict were retained. Comparing this tree with the previous reviewed scratch integration, `ed84ff6`, changes only the six F1 implementation/test/documentation files; no provider or unrelated integration code changed.

Evidence: [rebase audit](/home/dev/ara-work/reports/tau2-rereview-evidence/rebase-audit.json), [net scope](/home/dev/ara-work/reports/tau2-rereview-evidence/net-scope.json).

### Verification

A fresh scratch clone at `/home/dev/ara-work/tau2-rereview` uses the exact reviewed commit and a locked environment. Executed sequentially with `UV_OFFLINE=1` inside `unshare -Urn`: `uv run --locked pytest -q`, `uv run --locked python tests/integration/negative_controls.py`, then `uv run --locked python tools/ocr_negative_controls.py`.

Full pytest: **985 passed, 4 skipped / 989 collected**, exit 0, **541.31 seconds**. Repository controls: **411/411** expected mutation failures and restored passes, exit 0, **2105.91 seconds**. OCR controls: **32/32**, exit 0, **72.82 seconds**. Total: **443/443 controls**. All **180 tracked-file hashes** match the pre-gate manifest after every stage. The scratch and author trees are clean at the reviewed head; `git diff --check 7e5219a HEAD` passes.

Evidence: [pytest](/home/dev/ara-work/reports/tau2-rereview-evidence/pytest.log), [repository controls](/home/dev/ara-work/reports/tau2-rereview-evidence/repository-controls.json), [OCR controls](/home/dev/ara-work/reports/tau2-rereview-evidence/ocr-controls.json), [final source/gate audit](/home/dev/ara-work/reports/tau2-rereview-evidence/final-verification.json).

The four default-suite skips are the two paid-provider opt-ins and two installed-local-model opt-ins. No new live pilot, model-quality claim or fresh OCR inference is implied. The earlier offline pilot-routing proof remains scoped to the prior reviewed integration; this re-review's net changes are confined to F1.

### Saved-candidate impact and remaining limits

Independently rechecked all **131 previously accepted Round 3 candidates**, including **11 VL candidates**, against the new unique-alignment and synthesized-only confidence functions using the retained OCR text and actual confidence ranges. **All 131 still pass; seven confidence values change; zero additional refusals.** Evidence: [saved-candidate audit](/home/dev/ara-work/reports/tau2-rereview-evidence/saved-candidate-audit.json).

This rechecks previously accepted candidates only. It is not a new corpus extraction or a reassessment of earlier rejected candidates. The historical 131/678 repaired spans and 9/82 cleared-page counts, observed wrong symbol recognition, and remaining formula-order/encoding issues retain the limitations documented above. Closing F1 establishes the requested admission behavior, not complete or semantically correct transcription.

### Re-review finding placement

| Action-relevant finding | Placement |
|---|---|
| 1. F1 resolved, synthesized-only scoring and native low/high-score evidence | F1 resolution and exact preservation |
| 2. Exact clean fragments, unique alignment and independent exhaustive proof | F1 resolution and exact preservation |
| 3. Real regression failure under whole-span mutation and restored success | Regression and mutation evidence |
| 4. Requested ancestry, both decision sections retained and bounded net diff | Rebase and conflict resolution |
| 5. Full tests, both control runners, restoration and coverage limits | Verification |
| 6. Saved-candidate impact and unchanged transcription limitations | Saved-candidate impact and remaining limits |

6 findings, 6 placed.

DONE tau2 rereview rho2=merge blocking=0 tests=985/989 negctl=pass

## Follow-up: schema projection

**Omega: merge. Zero blocking findings in the reviewed scope.** Reviewed `8aa265fa32b97bdbae662108ba080950c5c73034`, whose parent is requested main `9aad0132d3f78a5e18dac4f00a5e51365accbfc0`. This follow-up was performed directly, without delegation, author-branch edits or push. The only live model requests were the explicitly authorized Codex subscription schema preflight and its required isolation canaries; no paid API calls or pilot generation were made.

### Projection and authoritative local validation

[`codex_schema.py`](/home/dev/ara-work/omega/ara/runtime/codex_schema.py) implements `ara-openai-strict-v1`. Repeated projection of each of the 12 native stage schemas produces the same result without mutating its input. Objects become closed with all properties required; optional properties gain a null sentinel; recursive local references remain; `const` becomes a singleton enum and `oneOf` becomes `anyOf`. The version enters provider metadata and cache identity. Native/wire schema hashes appear in call receipts, and admission/calibration use the projected schema.

The projection deliberately omits bounds, uniqueness and logical conditions. The full original schema remains in normal stage prompts and is passed to `Draft202012Validator` **after** normalization, before any caller check or accepted return. No original schema file changed. Native conditional/negation constraints and the exact-one-branch requirement therefore remain authoritative even where the wire grammar is weaker.

Normalization deletes only an optional property's null value when the native child schema disallows null. Required nulls, native nullable values, unknown fields and other malformed values survive for local rejection. Recursive branch selection uses the wire shape, but acceptance still depends on validation against the complete original schema. Raw wire responses remain unchanged in receipts and cache; replay repeats normalization and validation. Invalid responses retain accounting and do not enter the accepted cache.

Independent native `ModelCalls` probes exercised **24 cases**: **14 invalid outputs rejected**, including **nine valid under the weaker wire schema**, and **10 valid outputs accepted**. These cover empty required text, missing/nullable required fields, unknown null fields, bad discriminators, array bounds, duplicate values, numeric bounds, forbidden identifiers and both conditional branches. Accepted cases cover all nine formula variants, recursive references and preservation of native nullable data. The probes injected raw responses after a fake-binary canary; they are offline admission checks, not additional live provider requests.

Evidence: [probe script](/home/dev/ara-work/reports/tau2-projection-evidence/independent-probes.py), [results](/home/dev/ara-work/reports/tau2-projection-evidence/independent-probes.json), [constraint inventory](/home/dev/ara-work/reports/tau2-projection-evidence/constraint-inventory.json).

### Complete preflight coverage and pilot admission

Cross-checked the manifest against all native schema files, literal runtime call sites and dynamic construction dispatch. Its **12 stage schemas / 14 routing cases** cover `answer_cq`, `audit_essay`, `build_t`, `build_t_batch`, `formalise`, `map_leaf`, `propose_cuts`, `propose_targets`, `select_t_roots`, `tier1_repair`, `verify_originality_citations` and `write_essay`, plus separate correction cases for both construction stages. The recursive `formula` utility is embedded in stage schemas. Isolation canaries execute automatically. Extraction remains API-only, and schema-less web retrieval remains explicitly refused by Codex; neither is silently claimed as covered.

Before `run`, generation-capable `resume-construction` or `select` constructs its provider, the CLI requires a preflight log matching the current native/wire schema hashes, projection/CLI versions, model, effort and system-prompt hash. It verifies the event chain and tail checkpoint and requires a unique accepted, measured, uncached Codex receipt for every case. Missing, incomplete and stale proof refuses. Existing runs can supply a new proof path without rewriting their stored configuration. Offline planning remains exempt because it does not generate responses.

### Subscription live evidence and limits

The review's native preflight passed **14/14 cases**, with **two required isolation canaries**, for **16 accepted model calls**. The production gate then accepted the actual log. Requested model: **gpt-6-luna**, effort **high**, CLI **0.163.0**. Recorded usage: **75,498 tokens**; elapsed preflight/gate verification: **69.08 seconds**. The selected credential file's inode, size, modification time and permissions were unchanged. The canaries report no tool events and active tool-event rejection; generic visible tool definitions remain disclosed under the Round 12 rule.

Serving identity is still **unverified**. Subscription usage is distinct from measured API spend; the logged zero API cost is not a measured zero USD equivalent. This proves live grammar acceptance and local validation of placeholder responses, not semantic quality, a completed pilot, external retrieval or all possible model outputs. The existing lack of a hard CLI output-token cap remains unchanged.

Evidence: [live result and manifest](/home/dev/ara-work/reports/tau2-projection-evidence/live-results.json), [native log](/home/dev/ara-work/reports/tau2-projection-evidence/live-preflight/events.jsonl), [execution script](/home/dev/ara-work/reports/tau2-projection-evidence/live-preflight.py).

### Offline pilot plan

Reran `plan-construction --profile pilot --token-counter provider` at the reviewed revision against the same real 26-paper literature artifact, SHA-256 `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`, using synthetic credentials and a fake Codex binary inside network isolation. The migrated pilot configuration still routes construction, corrections and checked search stages to **codex_cli / gpt-6-luna**. The plan exits **0**, with **69/69 windows counted and funded**, zero uncounted windows and **zero generation calls**. Projected-schema accounting changes the earlier 70-window plan.

The planner uses local calibration and launches no Codex process. A separate native fake-binary canary and `formalise` call verify transport routing. Count receipts were batched with their original payloads; estimator, planner and admission behavior were unchanged. This verifies offline planning and routing, not live pilot execution.

Evidence: [summary](/home/dev/ara-work/reports/tau2-projection-evidence/offline-plan/summary.json), [script](/home/dev/ara-work/reports/tau2-projection-evidence/offline-plan.py), [fake transport receipts](/home/dev/ara-work/reports/tau2-projection-evidence/offline-plan/smoke-routing.json).

### Tests, mutation controls and source restoration

In the isolated scratch clone, ran `UV_OFFLINE=1 uv run --locked pytest -q` followed by `UV_OFFLINE=1 uv run --locked python tests/integration/negative_controls.py`, each inside `unshare -Urn`. Full pytest: **1,001 passed, 4 skipped / 1,005 collected**, exit 0, **556.16 seconds** (557.71 including startup). The four skips are two paid-provider opt-ins and two installed-local-model opt-ins.

Repository controls: **420/420 expected mutation failures and restored passes**, runner exit 0, **1,846.20 seconds**. All **nine new controls** failed under mutation and passed after restoration: strict projection, required optional properties, closed objects, normalization before validation, local schema authority, wire-hash receipt matching, complete case coverage, no cache receipts and mandatory pilot admission. Inspected their retained red transcripts: these are test-execution failures, not collection errors. In particular, bypassing local validation lets duplicate roots through and fails the regression; bypassing preflight permits provider construction and fails the admission regression.

All **183 tracked-file hashes** match the pre-gate manifest after each gate and at final audit. Both scratch trees and the author tree are clean at `8aa265f`; `git diff --check 9aad013 HEAD` passes. The complete base `DECISIONS.md` remains an exact prefix, preserving both previously reconciled sides before the new Round 13 decisions.

Evidence: [pytest log](/home/dev/ara-work/reports/tau2-projection-evidence/pytest.log), [control results](/home/dev/ara-work/reports/tau2-projection-evidence/control-results.json), [control log](/home/dev/ara-work/reports/tau2-projection-evidence/controls.log), [new control transcripts](/home/dev/ara-work/reports/tau2-projection-evidence/new-controls), [final source and gate audit](/home/dev/ara-work/reports/tau2-projection-evidence/final-verification.json).

### Follow-up finding placement

| Action-relevant finding | Placement |
|---|---|
| 1. Deterministic versioned projection and retained native constraints | Projection and authoritative local validation |
| 2. Safe null normalization, cache replay and direct invalid/valid probes | Projection and authoritative local validation |
| 3. Complete stage/correction coverage and mandatory proof gate | Complete preflight coverage and pilot admission |
| 4. Live 14/14 evidence, credential metadata, identity/accounting and proof limits | Subscription live evidence and limits |
| 5. Successful offline plan, current Codex routing and changed window count | Offline pilot plan |
| 6. Full tests, controls, source restoration and opt-in coverage limits | Tests, mutation controls and source restoration |

6 findings, 6 placed.

DONE tau2 projection omega=merge blocking=0 tests=1001/1005 negctl=pass

## Follow-up: resume

**Sigma: merge. Xi: fix-first. One blocking finding remains in Xi.** Reviewed Sigma `c32d429e77eedb09e0d4f48126b01355f998a119` and Xi `1971c74e77ca8732e029a766fbd687d2e24d1d56`, both based on `8aa265fa32b97bdbae662108ba080950c5c73034`. Work was performed directly, without delegation, paid calls, live provider generation, author-branch edits or push. The real stopped pilot was audited through a byte-preserving copy; its original files remain unchanged.

### Blocking finding F2 — stale completion marker skips resumed results

**F2 / P2: an older partial run's selection marker can make a later interrupted resume return success without publishing its new results.** At [search_resume.py:267](/home/dev/ara-work/xi/ara/runtime/search_resume.py:267), `already_finished` combines the current restored-job count with **any historical** `awaiting_selection` event. The CLI then returns before native analysis and route publication. The marker is not tied to the batch/results it completed.

Independent native reproduction on **both Xi alone and the merged tree**:

1. A placeholder search completes job 0, exhausts job 1's bounded failures and reaches the normal partial `awaiting_selection` state with one route and no paired analysis.
2. Resume completes and durably publishes job 1. An injected halt occurs before refreshed analyses/routes are saved.
3. The next `resume-search` exits **0** and reports **`awaiting_selection`**, because both jobs are now restored and the old marker exists. It retains the **one old route** and **empty paired-analysis inventory**, instead of publishing both results.

A runtime-only diagnostic that bypasses this stale shortcut allows the existing native continuation to publish **two route events and one paired analysis**, with **zero search redispatches and zero new MODEL receipts**. No source fix was applied. This isolates the defect to completion detection rather than missing results or an inability to reuse them.

Fix before merging Xi: bind completion evidence to the current search-publication/results generation, so a prior partial-run marker cannot authorize the early return. Preserve the fast path for a genuinely completed current generation. Add the partial-run -> successful missing-job recovery -> halt-before-analysis -> resume regression and a production-wire control. The requested original pilot has no such stale-completion situation in the executed proof; its offline recovery remains **ok**. The defect affects the general resume lifecycle and is not covered by the current passing suite.

Evidence: [merged reproducer](/home/dev/ara-work/reports/tau2-resume-evidence/stale-completion-probe.py), [merged result](/home/dev/ara-work/reports/tau2-resume-evidence/stale-completion.json), [Xi-only result](/home/dev/ara-work/reports/tau2-resume-evidence/xi-only-stale-completion.json), [diagnostic native continuation](/home/dev/ara-work/reports/tau2-resume-evidence/stale-completion-continuation.json).

### Sigma: schema equivalence and bounded work

[`validation.py`](/home/dev/ara-work/sigma/ara/runtime/validation.py) selects a recursive formula branch only when every branch requires a distinct string `op` tag. Those conditions prove that at most one branch can match; all constraints of that branch still run through the extended native Draft 2020-12 validator. Optional or overlapping tags retain ordinary union semantics. The structural precheck uses the existing branch definitions to reject malformed operators, fields, terms and arities before recursive validation. Native schema files are unchanged.

Independent comparison against the original `Draft202012Validator` covered **1,206 distinct formula cases**: **114 accepted, 1,092 rejected, zero mismatches and zero oracle timeouts**. Cases included repository fixtures, generated random trees and independently generated operator/field boundaries. Another **39 stage-payload comparisons** agreed. This supports the disjoint-tag equivalence argument; it is not a claim that finite testing alone proves every possible input.

The recursive-schema inventory covers `formalise`, `build_t`, `build_t_batch`, `propose_targets` and the `formula` utility. They use the same protected recursive formula structure. Cut/repair schemas reference nonrecursive proposal records; CQ answers do not contain recursive formula ASTs. The runtime schema-validation entrypoints, Codex normalization, correction merges, replayed extraction and canary checks use the bounded path.

Depth **64**, JSON-value count **100,000** and **two seconds per schema/normalization operation** are explicit operational admission limits. They can refuse an oversized schema-valid value; the unchanged-acceptance claim concerns schema semantics within those bounds. The time guard runs in a separate interpreter, including from search threads, and kills and reaps timed-out children. Response failures become logged, charged `InvalidOutput` rejections eligible for the existing correction path. They do not become accepted/cacheable output. Domain callbacks and solver work retain their separate budgets.

Evidence: [independent comparison](/home/dev/ara-work/reports/tau2-resume-evidence/equivalence.json), [probe](/home/dev/ara-work/reports/tau2-resume-evidence/equivalence-probe.py).

### Sigma: actual stalled response

Read the pending measured `formalise` receipt from real job 7 without generating a replacement. Its **1,306 characters, 17 formula nodes and root-zero JSON depth 22** match the reported stall shape. The new validator rejects it at **`minItems`, `/formula/args`**: **0.046 ms median, 0.173 ms maximum over 100 samples**, with the schema already loaded. The complete measured Codex normalization-plus-validation path took **88.90 ms**. These are separate timing scopes; the subprocess overhead is included only in the latter.

The native regressions exercise rejection followed by correction, accurate accounting, cache exclusion, node/depth limits and a pathological regex timeout from search threads. The decoder-RecursionError regression explicitly injects that documented decoder failure; it does not claim every Python build rejects JSON at the same nesting depth.

Evidence: [actual-response timing and recovery audit](/home/dev/ara-work/reports/tau2-resume-evidence/offline-resume.json), [execution script](/home/dev/ara-work/reports/tau2-resume-evidence/offline-resume.py).

### Xi: integrity, publication and selective continuation

[`search_resume.py`](/home/dev/ara-work/xi/ara/runtime/search_resume.py) verifies the main hash chain and tail checkpoint; exactly one run configuration, freeze and candidate inventory; the frozen T against `commitments.json`; bank identity; ordered target/polarity goals; journal paths, chains and checkpoints; and sealed trace hashes, identities and structure. Recovery requires local trace artifacts and rejects symlinked journal/trace paths. Recorded accepted formalisation receipts recheck proposal licenses locally. A sealed job remains recoverable if its final job-finished marker was interrupted.

Publication retains original event bodies in stable job order. Existing publication markers and copied prefixes are verified and deduplicated. An interrupted measured response gets one incomplete settlement tied to its call ID and receipt hash; an interrupted dispatch without a measured receipt refuses. Changed T, targets, journals, seals, accounting identities or measured usage likewise refuse before canonical publication or provider creation. A nonblocking per-run lock excludes concurrent recovery commands.

Completed results and their license inventories enter the existing scheduler as restored jobs. Only missing jobs are submitted, and native paired analysis, route persistence and `awaiting_selection` remain the completion path. The owning native regression resumes a placeholder run, observes only its unfinished polarity dispatched, completes the lifecycle, then repeats without another dispatch. The real-run proof below deliberately stops before dispatch.

### Real stopped pilot: offline recovery and accounting

Copied all **160 files** from `/home/dev/ara-scaffold/runs/codex-pilot-2`, verifying the complete SHA-256 inventory before execution. Ran native `ara resume-search --stop-before-dispatch` twice under OS network isolation with a provider factory that fails if invoked. Both runs exited **0**; they took **65.31 seconds** and **62.60 seconds**, including integrity checks and local reconstruction.

Both reported **166 frozen commitments**, **10 targets**, **19 completed jobs**, and **only job index 7 to rerun**. Publication covers indices **0–19 in order**: the 19 completed journals plus job 7's unfinished historical usage. No provider was constructed, no new call was dispatched and no generation occurred. The repeated plan and MODEL-event sequence are identical. The MODEL-event multiset matches the original main log plus the journal receipts and exactly one recovered settlement.

That settlement contains **8,373 input + 828 output tokens**. Total imported search usage is **2,452,008 tokens**. A separate native `Budget` restoration verifies **17,989,495 total recorded tokens**, including **11,348,025 imported tokens**, with unchanged MODEL receipts. The saved configuration already authorizes `count-at-reservation` for **two pre-existing finalized unknown-usage receipts**; budget startup adds the corresponding zero-usage reconciliation event. Those older reservations remain estimates. Job 7's new settlement retains its measured usage, and no new paid usage is claimed.

The original pilot inventory remains unchanged. This establishes safe offline publication and the exact remaining-job plan, not completion of the live pilot. Live continuation still uses the stored configuration and the mandatory Codex preflight gate. Missing evidence refuses rather than silently repeating potentially paid work.

Evidence: [offline recovery summary](/home/dev/ara-work/reports/tau2-resume-evidence/offline-resume.json), [execution log](/home/dev/ara-work/reports/tau2-resume-evidence/offline-resume.log), [budget restoration](/home/dev/ara-work/reports/tau2-resume-evidence/budget-restore.json), [original inventory](/home/dev/ara-work/reports/tau2-resume-evidence/original-inventory.json).

### Integration and verification

Scratch checkout: `/home/dev/ara-work/tau2-resume`. Merged Sigma then Xi onto `8aa265f`, producing **`27b83dcb8523856bbb3a291a6d49c83292417b01`**. Conflicts were confined to **`DECISIONS.md` and `README.md`**. The complete base and both branches' appended sections are retained. Implementation and control-runner changes auto-merged. All **433 controls** have unique names and exactly one mutation anchor. No native schema file changed.

Executed the full suite, then the repository control runner sequentially, with `UV_OFFLINE=1`, live/local-model opt-ins disabled and `unshare -Urn` network isolation. `uv run --locked pytest -q`: **1,032 passed, 4 skipped / 1,036 collected**, exit 0, **832.43 seconds** (834.05 including startup). The skips are two paid-provider opt-ins and two installed-local-model opt-ins.

`uv run --locked python tests/integration/negative_controls.py`: **433/433 expected mutation failures and restored passes**, runner exit 0, **2,251.15 seconds**. This includes all **seven new Sigma controls** and **six new Xi controls**. Inspected those 13 red/green transcripts plus the three adapted schema/decoding controls: failures exercise the intended behavior, not collection errors. Disabling tag dispatch visits 125 formula branches instead of 11; bypassing the deadline or native authority loses required refusals; removing completed-job exclusion dispatches both jobs; omitting settlement loses measured usage. The restored targets all pass. These controls do not cover F2's stale selection marker.

All **187 tracked-file hashes** match the pre-gate manifest after both gates and at final audit. Both scratch checkouts are clean at the reviewed merge; both author checkouts are clean at their requested heads. Ancestry and `git diff --check 8aa265f HEAD` pass. All **160 original pilot files** still match their initial hashes. No implementation fix was applied for F2; its passing existing tests do not override the independent native reproduction.

The selected mutation transcripts are retained in [new-controls](/home/dev/ara-work/reports/tau2-resume-evidence/new-controls).

Evidence: [integration audit](/home/dev/ara-work/reports/tau2-resume-evidence/integration.json), [pytest log](/home/dev/ara-work/reports/tau2-resume-evidence/pytest.log), [control results](/home/dev/ara-work/reports/tau2-resume-evidence/control-results.json), [final verification](/home/dev/ara-work/reports/tau2-resume-evidence/final-verification.json).

### Resume finding placement

| Action-relevant finding | Placement |
|---|---|
| F2. Blocking stale completion marker, native reproduction and required fix | Blocking finding F2 |
| 1. Native schema equivalence, recursive-schema inventory and operational bounds | Sigma: schema equivalence and bounded work |
| 2. Actual stalled-response rejection, measured timing scopes and correction coverage | Sigma: actual stalled response |
| 3. Chain/freeze/T/journal/seal verification and explicit refusals | Xi: integrity, publication and selective continuation |
| 4. Stable deduplicated publication, preserved licenses and unfinished-only dispatch | Xi: integrity, publication and selective continuation; Real stopped pilot |
| 5. Exact-once accounting, measured settlement and retained unknown-usage reservations | Real stopped pilot: offline recovery and accounting |
| 6. Successful real offline proof, original preservation and live-proof boundary | Real stopped pilot: offline recovery and accounting |
| 7. Exact merged revision, preserved conflicts, full gates and source restoration | Integration and verification |

8 findings, 8 placed.

DONE tau2 resume sigma=merge xi=fix-first blocking=1 integration=conflicts:DECISIONS.md,README.md merged_tests=1032/1036 offline_resume=ok

## Re-review F2

**Xi: merge. F2 is resolved; zero blocking findings remain in this re-review.** Reviewed `4c1c76fe34d00666d9fc2535b2f2d2eba380ab46` on parent `c8194b53fe238ec50960705ff43b8c574659ca5f`, containing Sigma `c32d429`. This supersedes the preceding Xi fix-first verdict; the original finding remains above as historical evidence. Review and execution were direct, without delegation, author-branch edits, paid calls, live pilot generation or push.

### Completion evidence follows the current results

[`current_search_finished`](/home/dev/ara-work/tau2-f2-probes/ara/runtime/search_resume.py:214) examines events after the latest search-publication start. It requires that batch's publication-finished receipt, a complete job phase, saved paired analyses and selection marker, in that order. Job indices, completion statuses and goals must match the restored inventory; each saved positive/negative result must equal its restored `SearchResult`; selected route IDs must match those results. An older selection marker cannot authorize completion of a newer generation.

The existing main-chain, freeze, T, journal, seal, license and accounting verification still runs before this check. The parent tree is implementation-identical to the prior reviewed scratch integration `27b83dc`; only the order of the preserved `DECISIONS.md` and `README.md` additions differs. The repair changes one production module, its regression/control and decisions documentation.

Independent predicate checks exercised **19 cases** against copies of authentic completed-run receipts. All **17 invalid/stale cases** were rejected, covering missing or reordered completion stages, wrong batch, partial/mismatched job inventories, absent or mismatched paired results, wrong route inventory and a newer generation following an old completion. The genuine current generation and audit-only appends both preserve the fast path.

Evidence: [scope audit](/home/dev/ara-work/reports/tau2-f2-evidence/scope-audit.json), [completion checks](/home/dev/ara-work/reports/tau2-f2-evidence/completion-evidence.json), [probe](/home/dev/ara-work/reports/tau2-f2-evidence/completion-evidence-probe.py).

### Original reproduction and completion fast path

Reran the original native F2 setup: job 0 completes, job 1 exhausts its bounded failures, and the partial run reaches selection. Recovery then completes job 1, followed by an injected halt before saving refreshed analyses/routes. At that point the repaired loader reports `stopped_before_dispatch`, with both jobs restored and no jobs to rerun, instead of incorrectly claiming selection readiness.

The next normal `resume-search` exits **0**, publishes **two route events and one paired analysis**, and selects both routes. It redispatches **zero completed searches** and creates **zero new MODEL receipts**. No completion shortcut was patched or bypassed in this re-review.

A subsequent resume of that genuinely completed generation exits **0 before provider creation**. It adds only the human resume command, plan and timing records: no new publication generation, analysis, route, dispatch or MODEL event. Thus the fix closes F2 while retaining idempotent completion behavior.

Evidence: [reproduction script](/home/dev/ara-work/reports/tau2-f2-evidence/stale-completion-probe.py), [executed results](/home/dev/ara-work/reports/tau2-f2-evidence/stale-completion.json).

### Regression, mutation and full verification

`uv run --locked pytest -q`: **1,033 passed, 4 skipped / 1,037**, exit 0, in 879.92 seconds (881.50 seconds including startup). `uv run --locked python tests/integration/negative_controls.py`: **434/434 controls**, exit 0, in 2,330.02 seconds. Every mutation returned 1 and every restored run returned 0. Both commands ran with network access disabled and offline dependency resolution.

The new `search_resume_current_generation` control restores the historical `any(awaiting_selection)` predicate. Its regression fails at the intended assertion: **zero newly published route events instead of two**, with no collection error. Restoring the production predicate makes that same test pass. This reproduces F2 directly and demonstrates that the regression detects its return.

Final verification confirmed all **187 tracked file hashes** unchanged in both isolated review copies, both clean and pinned to the requested `4c1c76f`. Ancestry and diff whitespace checks passed. Xi's author checkout acquired concurrent follow-on edits during the run; its state is recorded separately and was left untouched. Those edits are outside this review, whose execution and source evidence use the pinned copies.

All execution was offline with synthetic responses. This establishes the repaired resume behavior and regression coverage, not a newly completed live pilot. The earlier real stopped-run recovery proof remains scoped to its recorded revision; no new real-run mutation was required here.

Evidence: [pytest](/home/dev/ara-work/reports/tau2-f2-evidence/pytest.log), [control results](/home/dev/ara-work/reports/tau2-f2-evidence/control-results.json), [F2 mutation failure](/home/dev/ara-work/reports/tau2-f2-evidence/current-generation-red.txt), [restored pass](/home/dev/ara-work/reports/tau2-f2-evidence/current-generation-green.txt), [final verification](/home/dev/ara-work/reports/tau2-f2-evidence/final-verification.json).

### F2 re-review finding placement

| Action-relevant finding | Placement |
|---|---|
| 1. F2 resolved through current batch/result binding; exact review scope | Completion evidence follows the current results |
| 2. Original halted-recovery case now publishes both results without redispatch | Original reproduction and completion fast path |
| 3. Genuine completion fast path and adversarial completion-evidence checks | Completion evidence follows the current results; Original reproduction and completion fast path |
| 4. Effective regression/control, full gates, restoration and offline proof limits | Regression, mutation and full verification |

4 findings, 4 placed.

DONE tau2 f2 xi=merge blocking=0 tests=1033/1037 negctl=pass
