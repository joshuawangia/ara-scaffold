# Kappa2 non-author review

**Omega: fix first. Xi: merge. One blocking finding: Omega's new diagnostic sanitizer still persists credential-shaped JSON values and short prompt echoes.** This is an offline review of the pinned revisions, not a successful pilot rerun.

## Scope and integration

Reviewed base `852b21796191111c916be944648e3a42cac359ec`, Omega `a85c0af3a275bad2c6ff23c223e44a1ced894df1` (`fix/subagent-final`, rounds 6–7), and Xi `801ef7d5ad961dfdbbdf353efa2f391b443fafd2` (`feat/run-report`, round 8). Read the requested briefs, author reports, pilot report, pilot work notes, ARA rules and architecture plan. Reviewed runtime changes with their native callers, accounting, trace/publication consumers and tests. Worked solo as required; no delegated or external-model review, live or paid provider calls, push, or author-branch edits.

Scratch clone: `/home/dev/ara-work/kappa2-integration`. Merged Omega first, then Xi. Xi's merge conflicted in `DECISIONS.md` and `tests/integration/negative_controls.py`. Both conflicts were additive: retained the Omega and Xi decision sections and all controls, removing only conflict markers. The resulting merge is `c524823d938443f5f7cb1a91998cb95cda036b5d`, with the two requested heads as parents. Other overlapping files, including `ara/runtime/export.py`, merged automatically. This is a conflict-resolved integration result, not a clean automatic merge. Neither source branch was changed.

## Blocking finding F1 — diagnostic text still crosses the sensitive-data boundary

**P1; Omega; [credential redaction](/home/dev/ara-work/omega/ara/runtime/claude_code.py:296) and [prompt-echo matching](/home/dev/ara-work/omega/ara/runtime/claude_code.py:307).** The sanitizer's credential-assignment regex requires a colon/equal sign immediately after the key and whitespace. A closing JSON quote prevents matching. Separately, when the full rendered prompt is longer than seven characters, prompt-echo detection only tests shared eight-character fragments; it never tests the short input values inside that prompt.

Three independent production-subprocess probes using the repository's disposable offline CLI fixture demonstrate persistence in the native receipt:

| Simulated stderr | Retained `stderr_first_line` | Defect |
| --- | --- | --- |
| `{"token":"new-secret-value"}` | Identical | Quoted JSON credential key bypasses assignment redaction |
| `{"password":"new-secret-value"}` | Identical | Same bypass for passwords |
| `invalid value: P` with proposition text `P` in the full rendered request | Identical | Short input echo bypasses eight-character matching |

The fake credential is deliberately absent from the provider's known-secret inventory, exercising the generic credential-pattern protection. Known OAuth values still receive exact-value scrubbing; this finding does not claim a real credential was exposed. These are ordinary quoted assignments and literal prompt fragments, not novel encodings or paraphrases. `provider_error_evidence` forwards `exc.receipt`, and ModelCalls persists it in provider-error and MODEL events, so this is a durable log leak rather than a helper-only failure. The same sanitizer also protects subtype/category strings.

Fix the retention boundary before the pilot: handle quoted credential fields and short input echoes, or suppress diagnostic text that cannot be established safe while retaining recognized categories and numeric metadata. Add these production-wire regressions and controls. Do not claim the current free-text sanitizer guarantees no credential/prompt echo.

Evidence: [probe source](/home/dev/ara-work/reports/kappa2-evidence/test_review_probes.py), [final probe transcript](/home/dev/ara-work/reports/kappa2-evidence/review-probes-final.txt), [retained diagnostic witnesses](/home/dev/ara-work/reports/kappa2-evidence/diagnostic-witnesses.json), all under `kappa2-evidence/` relative to the report directory. Final probes: **3 failed redaction assertions, 1 passing combined retry test**. The first version of the combined test compared against an incomplete formula serialization and did not inject a failure; that review-test mistake was corrected before the final run. No production code was modified to obtain these results.

## Omega calibration and accounting

Re-executed the author's derivation script after reading its calculations, redirecting its outputs into this review's evidence directory. It uses production `CalibrationState`, validates the original pilot chain and anchor, excludes imported observations, and verifies the source log remains unchanged. Source SHA-256: `678b4974d74f6380482f4f0797d84948fb81a56eab7c08dfecf59dc18bd73cab`; anchor SHA-256: `262cefdf7ba5012d3096150d8f1db54f399929d8fa58bd88eaaa8a90f27400f1`.

Results reproduced:

- Factor **0.553224**; **12/12** formalization receipts had no aggregate overshoot. The first is **30,294 actual aggregate input versus 89,844 reserved aggregate input**, not versus the **12,922 initial-context estimate**.
- **70/70 original planned windows fit** the plan's input bound. **54/54 windows with recorded post-plan requests fit** when those exact prompts are recounted with the corrected factor. Historical skips were **42 context refusals plus 16 closure/selection skips**, not 58 context refusals.
- The separate fixed overhead remains **949 tokens**. The old receipts do not expose first-turn input or turn counts, so these data cannot independently measure a new first-turn factor or per-turn overhead. The reported factor is the retained measured baseline under the corrected rule.

Code now compares a reported single-turn input with initial context, otherwise aggregate input with aggregate reservation. Overshoot correction removes corresponding fixed overhead/output replay; factor and overhead updates use upward-only maxima. Restore excludes imported and obsolete-version observations; cache replay does not train. The 70-window result is an admission counterfactual, not proof of 70 successful model contributions or full-corpus quality.

Pilot accounting independently reproduced **18,509,550 local + 11,348,025 imported = 29,857,575 total tokens**. `Budget.used_tokens` retains both; subscription admission and actual-overrun checks subtract only imported tokens. Reservations and unknown usage remain charged. API admission remains history-inclusive, including mixed-provider calls. STOP receipts expose local/imported/total, and methodology retains historical receipts and distinguishes token-cap policy. No imported history is discarded or rewritten. At a 30M local cap, measured local usage leaves **11,490,450** tokens before pending/new reservations; this is not permission to spend them or a guarantee of completion.

## Retry, partial selection and stable publication

Omega's unclassified exit-1 policy is one retry within the configured transport limit; retries=0 and other unknown exit codes remain authoritative. Deterministic auth/request/schema and credential/identity failures are non-retryable at that transport boundary. Each attempted call is admitted and accounted separately. The original two pilot exit-1 causes remain unknown because their stderr/subtype were discarded; the review does not relabel them transient.

Xi isolates exhausted job-local failures, drains the initial queue, then requeues failed jobs once in original order with fresh engines. Global budget/context and infrastructure failures retain their run-stop behavior. Search journals retain both attempts and publish in original target/polarity order. Failed unsealed trace files remain separate; retry traces use fresh files and seals.

Completed sibling routes survive missing searches. Paired analysis runs only when both results exist; unavailable analysis is disclosed rather than equated with no conflicts. CLI `awaiting_selection`, console output and methodology disclose partial search. Unknown prior spend still refuses later selection by default; the explicit `--unknown-usage-policy count-at-reservation` option retains upper-bound accounting and normal admission checks. All-failed search supplies no routes.

The review's combined offline CLI/NativeEngine probe passed with search concurrency two: one permanently failing negative search received **two transport attempts on each of two job attempts**, with exactly two `unclassified_exit_retry` events and one `search_job_retry`. Three healthy routes remained, the failed job was disclosed, and job publication was `[0,1,2,3]`. This exercises both branches together across the actual subprocess/provider/runtime boundary. Registered tests also cover partial run-to-selection-to-compose, run-stop cancellation, forced reverse publication, and twenty-search sequential/parallel equivalence with fixed responses and sufficient budgets. It does not establish equivalent live model outputs or live speedup.

## Executed integration gates

Full suite command: `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked pytest -q`. Result: **852 passed, 2 skipped / 854 collected**, exit 0, **483.43 seconds**. The two skips are opt-in live-provider tests. Transcript: `/home/dev/ara-work/reports/kappa2-evidence/pytest.txt`.

Only after the suite process exited, the supervisor started `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked python tests/integration/negative_controls.py` at **2026-10-24 01:02:59 UTC**. It completed at **01:29:09 UTC**, exit 0, in **1,569.48 seconds**: **397/397 mutations exited 1 and all 397 restorations exited 0**. The registry contains the 375 base controls plus all 14 Omega and 8 Xi additions; every anchor occurs exactly once.

Inspected the 22 new controls' red transcripts: failures concern comparison units, overhead propagation, old-factor restore, local cap, retry/classification bounds, redaction/truncation, queue isolation/order, retained routes, global stops, disclosure and explicit selection policy. None is a collection, import or syntax failure. The identity-scrub mutation still suppresses the whole line through the prompt matcher; its failed exact-string assertion proves the expected representation changed, not that an identity escaped. The parallel-equivalence mutation fails on differing trace bytes, and its restoration passes. These controls do not cover the three independently reproduced F1 cases.

All tracked-file SHA-256 values match the pre-control snapshot. `git diff --check` passes; the scratch merge and both original source branches are clean at their pinned heads. No production fix or tracked edit remains.

Evidence under `/home/dev/ara-work/reports/kappa2-evidence/`: `gates.json` records chronology and restoration, `controls.txt` and `control-results.json` record every result, `new-control-inspection.json` and `new-controls/` retain the 22 new red/green transcripts, `source-before-controls.json` holds source hashes, and `review-summary.json` records final heads and verdicts. All 794 full-run control transcripts remain in `/home/dev/ara-work/kappa2-integration/runs/delta-controls/`.

## Coverage and finding placement

The code-review skill's review discipline was applied manually under the brief's explicit solo/no-paid-call requirement. No multi-agent or cross-model review is claimed. The user-requested external report/evidence paths were used. Buckeye's pnpm delivery gate does not apply to this separate ARA Python repository; the requested ARA full pytest and control runner are the integration gates.

No live pilot, credential rotation, API fallback, real-corpus construction, real-run route selection, or repair of historical artifacts occurred. Selection/composition was exercised only by offline placeholder tests. The original pilot's limited paper coverage and unavailable failure diagnosis remain unchanged. Existing tests/controls passing cannot negate the separately reproduced redaction failures. No product fixes were made because the brief is review-only.

| Action-changing finding | Placement |
| --- | --- |
| Unsafe free-text diagnostic retention; Omega must be fixed first | Blocking finding F1 |
| Merge conflicts, resolution and exact integrated revision | Scope and integration |
| Corrected factor/window counts and counterfactual limits | Omega calibration and accounting |
| Local cap excludes imported history only; complete accounting remains | Omega calibration and accounting |
| Bounded combined retries, partial selection, stable publication and unknown-spend policy | Retry, partial selection and stable publication |
| Executed gates, adversarial failures and source restoration | Executed integration gates; Blocking finding F1 |
| Offline/solo/report-only scope and unchanged pilot limitations | Coverage and finding placement; Retry, partial selection and stable publication |

7 findings, 7 placed.

DONE kappa2 review omega=fix-first xi=merge blocking=1 integration=conflicts:DECISIONS.md,tests/integration/negative_controls.py merged_tests=852/854

# Re-review

**Omega `6bd7679`: merge. F1 is closed at this revision; zero blocking findings remain.** This supersedes the earlier fix-first verdict for the revised head, while retaining the original review and its evidence unchanged. Xi remains pinned to `801ef7d5ad961dfdbbdf353efa2f391b443fafd2`. No live or paid calls were made.

## R1 — F1 closed by removing free-text diagnostics

Reviewed the complete change from `a85c0af3a275bad2c6ff23c223e44a1ced894df1` to `6bd76796a1a7a68faf839b0f47d1ddd94bb2e925`, including its native receipt/log consumers. The former sanitizer is deleted. [`classify_failure`](/home/dev/ara-work/omega/ara/runtime/claude_code.py:58) examines diagnostic text in memory but returns only fixed failure/category labels, never matched text or regex captures. [`failure_receipt`](/home/dev/ara-work/omega/ara/runtime/claude_code.py:83) retains a subtype only if it exactly equals one of four known constants; unknown subtypes are omitted. Stderr survives only as its numeric byte count, and API status is type/range checked. Timeout metadata is also constant/numeric.

Traced valid error JSON, malformed/non-JSON receipts, credential/identity rejection, timeout and launch failure through `ClaudeCodeProvider.complete`, `_accounted_response`, `provider_error_evidence`, and ModelCalls' `response_received`/MODEL logging. Failure responses have empty content and explicit usage/routing metadata; arbitrary `result`, `error`, `errors`, `error_type`, subtype and stderr values are not copied into diagnostic receipts. Existing validated CLI version/model/session and usage fields remain. This closes the two original leak mechanisms without depending on credential discovery or prompt-fragment length. Retry bounds, non-retryable auth/request failures, and measured/unknown accounting remain intact.

Reran the same three production-subprocess inputs independently: `{"token":"new-secret-value"}`, `{"password":"new-secret-value"}`, and `invalid value: P`. **All three pass.** Since suppression deliberately removes `stderr_first_line`, the copied review probes now require that field to be absent and inspect all event payloads for the diagnostic/sentinel values. Their inputs and subprocess injection are unchanged; the original red evidence was preserved. The existing combined offline CLI/NativeEngine retry probe also passes: one transport retry per job attempt, one job requeue, retained healthy routes and stable publication. **4/4 probes passed in 2.73 seconds.** Source and transcript: `/home/dev/ara-work/reports/kappa2-rereview-evidence/test_review_probes.py` and `review-probes.txt`.

## R2 — Fresh integration and control replacement

Created `/home/dev/ara-work/kappa2-rereview-integration` from base `852b21796191111c916be944648e3a42cac359ec`, merged Omega `6bd7679`, then Xi `801ef7d`. The same two additive conflicts occurred in `DECISIONS.md` and `tests/integration/negative_controls.py`; retained both branches' entries without production behavior edits. Scratch merge: **`469c278cb34d67c80d4a033788d4bf5222fb373f`**. No source branch was edited.

The merged registry has **395 controls**, each with a unique mutation anchor. The reduction from 397 is explained: five controls for deleted scrubbing/truncation code were replaced with three controls for complete text suppression, exact subtype allowlisting and category enumeration. Xi's eight controls and the remaining Omega retry/calibration/accounting controls remain present.

## R3 — Executed gates and restoration

Ran `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked pytest -q` on the fresh merge: **854 passed, 2 skipped / 856 collected**, exit 0, **491.65 seconds**. The skips are the opt-in live-provider tests. No tracked source hashes changed.

Only after pytest exited successfully, ran `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked python tests/integration/negative_controls.py`. It ran from **2026-10-24 02:19:48 UTC to 02:46:23 UTC**, exit 0, **1,595.60 seconds**. **395/395 mutations exited 1; all 395 restorations exited 0.** The three replacement controls fail specifically on the original three retained stderr diagnostics, an arbitrary subtype, and an arbitrary error-category string. Their restored targets pass (3, 5 and 5 cases respectively); none of the red transcripts is a collection, import or syntax failure. Parallel equivalence, result pairing, publication and Xi's continuation/selection controls also pass their mutation/restoration checks.

All tracked-file SHA-256 values match the pre-gate snapshot. `git diff --check` passes. Omega and the scratch integration remain clean at their reviewed heads. Xi's checkout advanced independently; R5 states that scope distinction. The original report is preserved byte-for-byte as the prefix of this appended report.

Evidence: `/home/dev/ara-work/reports/kappa2-rereview-evidence/` contains `pytest.txt`, `controls.txt`, `gates.json`, `control-results.json`, `source-before-gates.json`, `review-summary.json`, `new-control-inspection.json` and the three replacement controls' red/green transcripts in `new-controls/`. All 790 full-run control transcripts remain under `/home/dev/ara-work/kappa2-rereview-integration/runs/delta-controls/`. The independent four-probe run is separate from the 856 collected repository tests.

## R4 — Scope and retained limitations

This remains a solo, offline, report-only review using the same adapted code-review discipline. No delegation, live-provider execution, credential changes, push, historical-log rewrite or pilot relaunch occurred. The reviewed suppression policy intentionally loses arbitrary diagnostic text; recognized categories and numeric receipts remain useful, but old pilot exit causes cannot be recovered. The prior calibration/accounting and 70-window counterfactual findings remain as qualified in the original report; no new live corpus-completion or output-quality claim follows from these gates. Existing historical logs are not retroactively sanitized by the code change.

## R5 — Verdict applies to the requested pinned integration

At delivery, Xi's working checkout is clean but has advanced to `f9c5a8fe24cfb73cf5dc47a9d2743a503f9c9179`. That commit was not the requested review target, and its tree differs from the tested scratch tree. No verdict on its additional merge resolution is claimed. The tested merge's parents were independently verified as exactly Omega `6bd7679` and Xi `801ef7d`; source hashes remained unchanged throughout both gates. These results and the zero-blocker verdict apply to that pinned integration, not automatically to the newer Xi head.

The original report's seven finding placements remain above. Five re-review conclusions are placed in R1 (F1 closure/design/probes), R2 (fresh integration/conflicts/control replacement), R3 (executed gates/restoration), R4 (scope and historical limits), and R5 (Xi checkout advancement and exact verdict scope).

12 findings, 12 placed.

DONE kappa2 rereview omega=merge blocking=0 merged_tests=854/856 negctl=pass
