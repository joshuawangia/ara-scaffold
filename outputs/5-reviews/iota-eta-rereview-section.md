## Re-review eta

**Verdict: merge eta; 0 blocking, 0 should-fix. E-B1, E-S1, E-S2 and E-S3 are resolved by design and independent verification.** Narrow re-review of eta `185a318a7fa5a46485a375ee1cb26244c2254403`, based on reviewed theta `be7468df12d4c0422d54f8ccd881d653cd92bdd4`, following `iota-rereview-eta.md` and `eta-round-2.md`. I read the repair diff, native callers and owning tests, all eight new mutation definitions and retargeted controls, then checked the author's Round 2 claims against independent evidence. Verification uses an independent detached clone at `/home/dev/ara-work/iota-eta-rereview`. No author edits, delegation, paid calls, provider token counting or push; no operations in the active paid extraction checkout or its run directories.

### E-B1 resolved — shared native contracts, pinned origins and current outcomes

**Locations:** `ara/runtime/frozen.py:46`, `:158`; `ara/runtime/response_contracts.py:9`, `:31`; `ara/runtime/calls.py:81`.

The frozen verifier now delegates imported-history verification to theta's `verify_imports`, which checks actual pinned origin prefixes and transitive imports. It reconstructs literature using theta's `extraction_outcomes`, so historical attempts remain evidence without becoming duplicate current papers. This closes both later resume failures identified in the original review.

Live prompt rendering and receipt verification share `response_contracts.py`, including mode-specific extraction schemas. New MODEL receipts record response-contract version 2. Historical accepted and rejected extraction attempts can match a pinned legacy template hash; unknown versions or changed templates refuse. I independently recomputed that hash from the original `ba3a004` prompt and schema in the review clone and checked the fixture against that historical prompt: `bfba951c2b48fc237eb2d5cf841ad9b0de8161f7f1a4f30ade2684bf1aa8c730`. Historical compatibility neither rewrites old receipts nor dispatches old schemas.

**Proof:** All four native cases pass through extraction, builder run, later builder selection, candidate `--from-frozen`, and later candidate selection/export. The full suite includes missing/changed pinned-ancestor refusals before provider creation. I reran the exact three previously failing merged-suite cases separately: `test_full_rich_history_and_campaign`, `test_broken_rich_provenance[batch]`, and `[plan]`; all pass. The independent resumed/disclosed-failure candidate also completes, with no local extraction, construction or freeze and byte-identical T.

### E-S1 resolved — accepted responses bind rich batch artifacts

**Locations:** `ara/runtime/frozen.py:72`, `:176`; `ara/runtime/construction.py:101`, `:114`, `:120`; `ara/runtime/calls.py:201`.

For each `(plan_id, batch_index)`, verification decodes the accepted MODEL response using the live decoder, applies the live correction merger when appropriate, and normalizes immutable evidence text/citations using the same helper as construction. A targeted correction must identify the actual preceding rejected candidate. The reconstructed commitments, symbols and alignments must match the saved batch. Existing artifact hashes, merge checks and frozen-table checks remain in force.

This directly closes the original internally contradictory MODEL-response/artifact counterexample. It also covers encoded formula ASTs and corrected responses, instead of comparing only the unnormalized provider text.

**Proof:** The original response/artifact contradiction now raises `construction response does not match batch`. An independent native CLI probe rebuilds a valid outer fixture chain with an inconsistent rich MODEL formula and confirms the same refusal before provider creation or destination log creation. A changed commitments file also refuses at that boundary. The full suite passes encoded and corrected receipt cases plus correction-origin disagreement refusal. All examples use placeholders.

### E-S2 resolved — compatibility excludes unrelated stage entries

**Locations:** `ara/runtime/frozen.py:18`, `:24`; `ara/runtime/providers.py:167`.

Compatibility compares relevant effective construction/extraction provider settings with runtime defaults supplied, plus the existing construction-specific configuration fields. It no longer hashes the entire `stages` map. A writer-only entry therefore does not invalidate T; effective extraction model/effort changes and construction interpretation changes still do.

This changes compatibility checking only. The current provider's stage-override implementation remains extraction-specific; accepting a `stages.write_essay` entry does not newly make that entry an operative writer override. The builder's original configuration remains verbatim in inherited history.

**Proof:** The original writer-only counterexample now succeeds through native `--from-frozen`. The full suite verifies that explicitly supplying an effective extraction default preserves compatibility, changing extraction effort changes the compatibility identity, and meaningful construction drift refuses.

### E-S3 resolved — inherited extraction disclosure without local charging

**Locations:** `ara/runtime/export.py:35`, `:63`, `:87`, `:107`.

The exporter derives extraction outcomes, partial coverage, models/usage, current failures, historical failures, stops and the failure policy from the inherited builder prefix plus local extraction evidence. The summary explicitly labels that scope. Imported history stays nested for lifecycle and budget purposes; the candidate's local charges remain its own MODEL work.

**Proof:** The independent native resumed/disclosed-failure candidate publishes successful `p`, reports current failed `q` and both historical failed attempts, and retains the maximum-three-failures policy. Simulated extraction spend is USD0.00525, inherited prefix spend USD0.00875, and local candidate spend USD0.01575. The full supplied campaign totals USD0.04025 and remains identical when the input log list is duplicated. Candidate-only aggregation is smaller because it excludes post-freeze builder work. The full suite also passes inherited partial-page diagnostics, model identity and production-lineage disclosure. The source builder files remain unchanged.

### Re-review verification and mutations

| Check | Result | Receipt |
|---|---|---|
| Full `uv run pytest` | 513 passed, 2 live-provider skips / 515 collected; exit 0; 335.20s | [Full output](iota-eta-rereview-pytest.txt) |
| Original three merged-suite failures plus independent probes | 8 passed; exit 0; 23.08s | [Probe source](iota-eta-rereview-probes.py), [output](iota-eta-rereview-probes.txt) |
| Full control runner, sequentially after pytest | 216/216 expected mutation failures; 216/216 restored passes; exit 0 | [Full output](iota-eta-rereview-controls.txt), [results](iota-eta-rereview-controls/results.json) |

I inspected all eight new mutation definitions and their fresh failure/pass traces. Each mutant exited 1, and its restored target exited 0. These are behavior checks, including valid-path regressions and the explicitly narrower correction-origin diagnostic check:

| Mutation | Observed failure under mutation | Trace pair |
|---|---|---|
| `shared_rich_response` | Removing response/artifact comparison permits the original contradictory MODEL formula. | [red](iota-eta-rereview-controls/shared_rich_response-red.txt), [green](iota-eta-rereview-controls/shared_rich_response-green.txt) |
| `shared_correction_origin` | Removing the origin check changes the expected refusal to a later batch-response mismatch; the downstream comparison still rejects this fixture. | [red](iota-eta-rereview-controls/shared_correction_origin-red.txt), [green](iota-eta-rereview-controls/shared_correction_origin-green.txt) |
| `shared_current_outcomes` | Using every historical outcome incorrectly refuses the valid resumed/disclosed-failure candidate. | [red](iota-eta-rereview-controls/shared_current_outcomes-red.txt), [green](iota-eta-rereview-controls/shared_current_outcomes-green.txt) |
| `shared_transitive_origin` | Skipping pinned-import verification lets missing and changed ancestors reach the forbidden provider-creation boundary. | [red](iota-eta-rereview-controls/shared_transitive_origin-red.txt), [green](iota-eta-rereview-controls/shared_transitive_origin-green.txt) |
| `shared_writer_settings` | Including the entire stage map again incorrectly refuses the writer-only configuration. | [red](iota-eta-rereview-controls/shared_writer_settings-red.txt), [green](iota-eta-rereview-controls/shared_writer_settings-green.txt) |
| `shared_extraction_settings` | Ignoring effective stage settings fails to distinguish changed extraction effort. | [red](iota-eta-rereview-controls/shared_extraction_settings-red.txt), [green](iota-eta-rereview-controls/shared_extraction_settings-green.txt) |
| `shared_failure_disclosure` | Ignoring inherited extraction makes the candidate report no current failed paper instead of failed `q`. | [red](iota-eta-rereview-controls/shared_failure_disclosure-red.txt), [green](iota-eta-rereview-controls/shared_failure_disclosure-green.txt) |
| `shared_legacy_attempts` | Removing the pinned legacy allowance rejects supported historical accepted/rejected attempts. | [red](iota-eta-rereview-controls/shared_legacy_attempts-red.txt), [green](iota-eta-rereview-controls/shared_legacy_attempts-green.txt) |

All control traces are archived alongside the results. The relocated full-schema control also still fails at its intended assertion and passes after restoration.

After the control runner exited, all **132 tracked files** in both review and author checkouts matched the [input fingerprints](iota-eta-rereview-files.json). Both remained clean at `185a318a7fa5a46485a375ee1cb26244c2254403`, with theta `be7468d` as their base. Staged/unstaged `git diff --exit-code`, `git diff --check` and empty porcelain status passed: [scratch receipt](iota-eta-rereview-scratch-restoration.json), [author receipt](iota-eta-rereview-author-restoration.json).

### Retained limits and next action

This re-review covers eta integrated on theta `be7468d`, including the formerly failing merged path. It does not certify any later revision or the active real-corpus extraction. No live semantic quality, statistical independence, campaign completion or budget-sufficiency claim follows from offline tests.

Keep the original completed builder and every pinned ancestor log. A native builder awaiting selection becomes eligible only after later `ara select` produces the final draft. Candidates preserve byte-identical T, reference its original freeze, start at target proposal and must not re-freeze it. Fresh cache identities and engine seeds separate candidate work; they are not provider sampling seeds.

Retain the complete campaign log set, including the builder's work after freeze. Candidates inherit only the prefix through freeze, so candidate-only totals omit the builder's later search/writing/selection. Hash chains and receipt comparisons detect changed or internally inconsistent evidence; they do not authenticate a completely coherent rewritten history or establish semantic fidelity.

### Re-review finding placement

| Finding/disposition affecting the next action | Placement |
|---|---|
| E-B1 resolved; exact historical compatibility, retained pinned ancestors and repaired theta integration | E-B1 resolved; Re-review verification and mutations; Retained limits and next action |
| E-S1 resolved; rich accepted-response/correction binding and integrity limits | E-S1 resolved; Re-review verification and mutations; Retained limits and next action |
| E-S2 resolved; effective compatibility and unchanged writer-override support | E-S2 resolved; Re-review verification and mutations |
| E-S3 resolved; inherited failure/coverage/policy disclosure and separate charges | E-S3 resolved; Re-review verification and mutations |
| Original-builder lifecycle, campaign-log completeness, cache/seed limits and offline scope | Retained limits and next action |

5 findings, 5 placed.

DONE iota rereview eta=merge blocking=0 should_fix=0 tests=513/515 negctl=pass
