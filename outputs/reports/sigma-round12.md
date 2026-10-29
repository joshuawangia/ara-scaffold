# Sigma Round 12 — resume alignment without rebuilding construction

## Delivered behavior

Requested base: `1dce56e`. Final local commit: `4cefe35f4a037725c1d5a97a1e401be46fe8fc83`, clean `fix/bounded-closure`. Full offline pytest: **1387 passed, 4 skipped / 1391 collected**. All **36 scoped controls** passed sequentially after the suite; the full 660-control inventory was anchor-checked, not fully rerun.

Alignment model replies now contain only `{relation, reason}`. Runtime binds exact candidate identities. Extra identifiers, including a mutated echo, fail validation; no model response text is repaired. A fully accounted invalid response receives the configured bounded retries. Exhaustion records `alignment_unresolved` with the pair, reason and attempt count, then continues. This outcome is neither `unrelated` nor an alignment and grants no formula rewrite or bridge. `construction_alignment_max_unresolved` is an absolute count, default 5; zero requires all candidates to resolve. Exceeding it records `symbol_alignment_incomplete` and refuses freeze. Provider, accounting and budget failures retain their existing explicit stops.

The remaining accepted judgments still pass the transactional type/arity, uniqueness and Z3 consistency gate. Source stance, source-support counting, CQ evidence restrictions and mandatory model-alignment disclosure remain intact. Native `report` exposes unresolved entries, their count and threshold in `data.json` under `construction.alignment`, and in the construction section. Persisted sidecar/disclosure retains unresolved outcomes after freeze.

## Native recovery interface

```
uv run ara resume-alignment --run-dir <copy-or-existing-run> --plan-only --output-dir <separate-empty-directory>
uv run ara resume-alignment --run-dir <existing-run> --codex-schema-preflight-log <current-preflight-events>
```

`ara/runtime/alignment_resume.py:load_alignment_resume(log, bank)` verifies the log chain/tail, run configuration and bank, original plan hash/artifact, every completed accepted/skipped window, merged working artifact and exact source provenance, candidate retrieval inventory and input-bound accepted judgment receipts. Explicit unresolved receipts require matching exhausted rejected attempts. It creates neither a provider nor a token counter. The CLI validates before provider creation, shares the construction-resume lock, records HUMAN/resumption receipts, restores accepted decisions and unresolved outcomes, and uses the native alignment → one freeze → forward candidates/targets → search path. It does not replay construction calls or fabricate a frozen set. Failed legacy responses stay rejected; their pairs are judged under the new schema. Reused accepted responses remain byte-for-byte original.

`--plan-only` writes `alignment-resume-plan.json` and separate logged receipts. It appends no source-run events; lock files may be created. Live continuation retains the original run configuration/accounting, with optional preflight and unknown-usage-policy overrides. Normal model admission and budget checks still apply. This entrypoint refuses incomplete or damaged construction, unfinalized dispatches, completed alignment, and partial/already-existing freezes. Existing construction and search recovery entrypoints keep their responsibilities. Explicit unresolved outcomes are preserved on resume rather than silently retried or erased.

CommitmentSet, commitments.json and frozen-t-v1 are unchanged. Alignment receipt policy v3 adds `unresolved` and `unresolved_limit` inside commitment-provenance-v2. Validation requires accepted and unresolved rows to partition the exact candidate inventory. Legacy alignment policies v1/v2 remain readable; v3 requires this reader. Construction plan v15 binds the new policy/limit. Alignment recovery verifies the original completed plan instead of reconstructing it under the new version. The changed judgment schema makes old Codex preflight manifests stale; a live continuation requires a refreshed applicable receipt.

## Real-copy free plan evidence

Source: `/home/dev/ara-scaffold/runs/codex-gap-1`. Probe copy: `/home/dev/ara-work/reports/sigma-evidence/round12/gap1-copy`. Native plan-only succeeded with 74 terminal windows, 159 working commitments, 150 candidates, 35 reusable accepted judgments and 115 remaining candidates. The old failed candidate has no accepted judgment and is included among those 115; its three invalid replies are retained. The plan reports zero generation calls and constructs no provider/counter. All 246 original files and all existing files in the copy matched their pre-probe SHA-256 values.

The 35 accepted legacy judgments remain model decisions, not source-established equivalences or entailments. The overnight handoff specifically disputes the substantive adequacy of one accepted relation; this recovery change preserves it for disclosure and review, not semantic endorsement. The existing omissions and source coverage are unchanged. No real freeze, target, forward result, route or useful synthesis was generated by this task. A live continuation would need up to 115 initial remaining judgment calls plus configured retries, applicable refreshed preflight calls and subsequent target/search calls. The free plan does not prove live context admission, budget sufficiency, solver consistency or semantic quality.

## Verification and limits

Evidence directory: `/home/dev/ara-work/reports/sigma-evidence/round12`.

The initial nine regressions failed before implementation (`red.txt`). An orphan unresolved receipt was separately shown resumable before its receipt check was added (`unresolved-receipt-red.txt`). Focused tests cover altered identity refusal, unresolved continuation/threshold/reporting, corruption and interruption refusal before provider creation, accepted legacy reuse, explicit unresolved reuse, native construction without replay, one freeze, actual native forward/target/search continuation and policy-v2 loading. The first targeted run exposed a synthetic fixture with no requested model identity; it was corrected to a realistic identity without changing production export behavior or weakening assertions. A new working-artifact mutation initially survived because the CLI caught a test factory exception and returned the same refusal code; the test was strengthened to assert zero factory calls separately. All five new mutations then produced red exit 1 and restored exit 0. Earlier failed receipts remain available.

Final full pytest: `1387 passed, 4 skipped in 2317.65s (0:38:37)`. All 36 scoped controls produced red exit 1 and restored exit 0. All 254 pinned regular-file hashes match restored and committed trees; the AGENTS symlink was checked separately. The final-source native free resume plan exactly matches the earlier successful plan, and all 246 original/copy file hashes still match. Receipts: `pytest-final.txt`, `controls/results.json`, `verification-tree-sha256.json`, `verification-tree-after.json`, `committed-blob-sha256.json`, `gap1-plan-final/alignment-resume-plan.json`, `commit.json`, `delivery.json`. The full control inventory is anchor-checked; the scoped run covers alignment/retrieval/construction-resume controls plus the new exact candidate binding, unresolved threshold, working-artifact binding, rejected-attempt receipt and report-count controls. This is scoped negative-control evidence, not a claim that the entire repository control inventory was rerun.

Native inline author verification only; no independent review, live provider acceptance or paid calls. No push. Xi was notified of the interface and will integrate separately with parallel search work.

## Findings placement

| Finding | Section |
| --- | --- |
| Unresolved is distinct from unrelated/aligned, with default absolute limit 5; operational failures still stop. | Delivered behavior |
| Live use needs a refreshed Codex preflight and normal admission/budget checks. | Native recovery interface; Real-copy free plan evidence |
| The free plan proves 74 windows/159 commitments/35 accepted reuse and 115 remaining pairs, not live continuation. | Real-copy free plan evidence |
| Legacy accepted judgments include an externally disputed relation; reuse preserves model decisions, not semantic endorsement. | Real-copy free plan evidence |
| Existing source omissions/coverage are unchanged; no real synthesis result was produced. | Real-copy free plan evidence |
| Policy v3 requires updated readers; v1/v2 remain supported, and original completed plans are verified rather than rebuilt. | Native recovery interface |
| Completed alignment, partial freezes and unfinalized dispatches refuse this recovery path; explicit unresolved outcomes remain preserved. | Native recovery interface |
| Verification is offline author evidence with scoped controls and no independent review/live calls/push. | Verification and limits |

8 findings, 8 placed.
