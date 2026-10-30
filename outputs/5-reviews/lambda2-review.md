# Lambda2 credential-handling review

**Verdict: merge. Blocking defects: 0.** The credential-handling change and its integration satisfy the six requested checks within the documented retry budgets and environment-transport threat model.

## Scope

Reviewed Omega commit `9a8e51ad7f832964a8602cc831bf3fa704354e5a` against `6bd7679`, and the integrated tree at `50ddc056dd408e7990a177a59256e7cba2396afb` on `integrate-auth`. Its parents are main `f9c5a8fe24cfb73cf5dc47a9d2743a503f9c9179` and Omega `9a8e51ad7f832964a8602cc831bf3fa704354e5a`.

The review and checks were performed personally, without delegation or source fixes. Tests run in the separate clone `/home/dev/ara-work/lambda2-review-clone`, never in `/home/dev/ara-scaffold`. The control runner temporarily mutates and restores production files as requested. No live model/provider call, credential rotation, commit, or push was performed.

## Six requested checks

1. **Fresh credential reads: pass.** `ara/runtime/claude_code.py:127` retains only the selected source path. `_authentication()` at line 246 opens that path anew, and `_environment()` at line 265 calls it for each model attempt. No token-bearing provider attribute remains. Environment-only authentication reads the current process environment. A missing or malformed selected file fails with `subscription_login_unavailable`, without falling back to an older environment token. The atomic-replacement regression exercises two calls on the same provider; six supplementary offline probes also verified unchanged source bytes/permissions, absence of retained token state, malformed/missing source refusal, and fresh environment reads.

2. **Bounded 401 re-read/retry: pass, with the documented budget qualification.** `classify_failure()` makes authentication failures retryable. `ara/runtime/calls.py:306` tracks `auth_retries` locally and permits at most one auth retry per transport invocation. The next attempt re-enters `_environment()` and reopens the source. Recovery and persistent-401 tests require two model attempts; `retries: 0` requires one. Measured and unknown usage remain accounted. This is not an unconditional extra attempt: the total retry limit and admission remain authoritative. The integrated search lifecycle can separately retry a failed job once; it does not turn the transport cap into a whole-run cap. The event name `auth_refresh_retry` means re-read, not OAuth refresh.

3. **Credential retention boundaries: pass within the stated threat model.** Only the access token enters the child environment; no refresh token or credential file is handed to the child. The command does not contain the credential. Call-local secret values remain available to scan raw stdout/stderr/debug and recursively decoded response strings even if the host replaces the source during the call. Cache replay scans current credentials before acceptance and evicts rejected entries. Exceptions and provider diagnostics retain fixed labels and allowlisted metadata, rather than environment dumps or free-form CLI error text. Tests cover encoded credentials, response keys/routing/nested strings, cache rejection, diagnostic suppression, and replacement during an in-flight call. The token is intentionally present in the child environment: this is not a claim of invisibility to same-user process inspection. README and provider methodology disclose that boundary.

4. **No credential writes/refresh/rotation: pass for the reviewed ARA path.** The source is read with `Path.read_text()`; the former snapshot-writing path is removed. The child receives no refresh token, uses a separate config directory, and receives no host-credential link. Success, subprocess failure, and timeout tests verify unchanged source bytes. The replacement operations in the rotation tests are fake-executable simulations of host replacement, not ARA refresh behavior.

5. **Private temporary resources and cleanup: pass; credential copy/link no longer applicable.** There is no temporary credential copy or link to clean up. `complete()` at `ara/runtime/claude_code.py:355` encloses the empty cwd/config directories and subprocess lifecycle in `TemporaryDirectory`, whose outer directory is private (0700). The context manager covers normal returns and raised failures. Existing success/exit/timeout tests assert that the per-call config directories no longer exist afterward. The child-environment test also asserts that no `.credentials.json` was created there.

6. **Merge preservation: pass.** Inspected the diffs against both parents and `git show --remerge-diff HEAD`. Only README required manual conflict resolution; its final text preserves the new auth retry and the existing separate search-job retry. All seven files changed exclusively by main and all three changed exclusively by Omega are byte-identical to the respective parent. Shared files are README, DECISIONS, and the integration controls. Both decision sections remain. All 389 Omega control names remain, together with main's eight search controls, yielding 397. The two old private-copy controls were intentionally replaced by the access-token-only and fresh-read controls in Omega itself; they were not lost during integration. Both parent-to-merge diffs pass `git diff --check`.

## Executed evidence

Environment: fresh clone of the reviewed merge, CPython 3.15.0, dependencies installed with `uv sync --locked --offline` from the committed lockfile.

- `uv run --offline pytest -q`: **860 passed, 2 skipped**, exit 0, 612.32 seconds. The denominator is 862 collected cases; the two skips are explicit live-provider tests. Paid-test opt-in was not enabled. [Complete pytest output](lambda2-pytest.txt).
- Six supplementary, read-only authentication probes using disposable placeholder credentials: **6/6 passed**; no provider subprocess was invoked. These are separate from the pytest count. [Probe output](lambda2-offline-probes.txt).
- After pytest exited, ran `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline python tests/integration/negative_controls.py`: **397/397 mutations failed as intended, and 397/397 restored tests passed**, runner exit 0. This includes `cli_access_token_only`, `cli_live_credential_read`, `cli_auth_retry_enabled`, and `cli_auth_retry_once`. [Runner output](lambda2-negative-controls.txt); [per-control results](/home/dev/ara-work/lambda2-review-clone/runs/delta-controls/results.json).
- Final restoration verified: `git status --porcelain` was empty; both `git diff --exit-code` and `git diff --cached --exit-code` passed. HEAD remained `50ddc056dd408e7990a177a59256e7cba2396afb`. No tracked or untracked source changes remain.

## Coverage limits

This is an offline source and regression review. No real Claude Code canary, paid API call, subscription inference call, or live host-token replacement was executed. The offline executable proves the ARA subprocess contract and retry/accounting behavior, not a live recovery of pilot 3. As the pilot report states, stale credentials are consistent with the observed failure but were not established by comparing token values. Passing this review does not establish a successful full pilot.

## Finding placement

These are review observations and verification limits, not eight code defects. No blocking defect has been identified in the reviewed change.

| Finding | Placement |
|---|---|
| 1. Fresh source reads and explicit missing/malformed-source refusal | Six requested checks, item 1 |
| 2. One auth retry per transport invocation, budget limits, and separate job retry | Six requested checks, item 2 |
| 3. Retention guards and intentional child-environment visibility | Six requested checks, item 3 |
| 4. Read-only source access and absence of refresh credentials | Six requested checks, item 4 |
| 5. No credential copy/link; private temporary directory and failure cleanup | Six requested checks, item 5 |
| 6. Both-parent merge preservation and intentional control replacements | Six requested checks, item 6 |
| 7. Exact revision, pytest/skips, probes, controls, and restoration evidence | Scope; Executed evidence |
| 8. Offline-only proof and unproven historical cause/live pilot recovery | Coverage limits |

8 findings, 8 placed.

DONE lambda2 verdict=merge blocking=0 tests=860/862 negctl=pass
