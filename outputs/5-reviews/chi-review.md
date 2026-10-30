# Chi: sigma round-five review

**Verdict: merge. Blocking code findings: 0.** The requested refusal, preview, and accounting boundaries pass this narrow non-author review. Live count-only restoration remains unverified pending restored API credit; this verdict does not certify a successful live continuation.

## Scope

Reviewed `/home/dev/ara-work/sigma`, branch `fix/bounded-closure`, head `0e0a7fcf8a167fa6a0973f92e322582c33d6e6e4`, against `main` at `2d9aeb590df3b48958ad481dcfc424ada70e11d1`. Read the round-five brief and report, repository rules and plan, the complete changed runtime paths, their native callers, accounting/export paths, owning tests, and all nine new control definitions.

Performed the review myself, adapting the code-review skill to the explicit solo constraint. No delegation, provider calls, token-count endpoint calls, paid calls, credential loading, branch edits, or push. Verification used a detached local clone of the exact head at `/tmp/chi-review-sigma5`; temporary mutations never touched the subject checkout.

## Required checks

| Check | Review result |
| --- | --- |
| Credit refusal stops with an explicit reason | `providers.py:292` canonicalizes the observed insufficient-credit diagnostic, including HTTP-200 stream errors. `terminal_request_refusal` excludes it from window refusals. `calls.py:450` logs counter failure evidence and propagates the error. Construction does not turn it into a skip. The resume receipt guard also rejects known credit failures. Independent probes confirmed fatal behavior during partition counting, admission, output validation, and generation for HTTP 200 and 400, with no later-window dispatch or freeze. |
| Other request-specific count 4xx refusals skip with logging | `calls.py:445` records safe, zero-cost counter-refusal evidence. `construction.py:247` splits rejected aggregate probes; indivisible/final uncountable windows retain null counts and explicit omission receipts. Copy-floor and admission failures omit the affected window and preserve later windows. The owning four-case regression verifies retained P/R windows. Authentication, rate-limit, server, and transport failures remain fatal; mandatory global checks still cannot be bypassed. |
| Preview stops before generation | CLI requires a separate empty output directory and holds the source resume lock. `planning.py:126` verifies original receipts, uses zero caps and `CountingProvider`, and invokes native construction with `plan_only=True`. Construction verifies plan identity, restores completed work, then returns after counting the next eligible selection request, before generation or freeze. The native CLI regression checks source-log preservation, restored commitments/window index, and absence of dispatch. |
| Accounting remains intact | No pricing or Budget implementation changed. Request-specific pre-dispatch count refusal raises before MODEL receipt creation and adds no charge or reservation. Dispatched unknown usage retains its reservation; post-response validation failures retain measured usage. The independent probes verified ledger/budget equality and both accounting cases. Preview reports new cost separately in its own log. |

## Executed verification

Ran these sequentially, with `ANTHROPIC_API_KEY` removed, `ARA_LIVE_TEST=0`, and `UV_OFFLINE=1`:

1. `uv run --locked pytest -q`: **681 passed, 2 skipped, 683 collected**, exit 0, 332.08 seconds. The skips are the opt-in live tests. [Transcript](chi-evidence/pytest.txt).
2. Eight independent external offline probes: **8 passed**, exit 0, 6.17 seconds. These exercise the credit and accounting boundaries at four phases under HTTP 200/400. [Probe source](chi-evidence/test_chi_boundaries.py), [transcript](chi-evidence/boundary-probes.txt).
3. `uv run --locked python tests/integration/negative_controls.py`: **314 mutations failed their targeted tests; all 314 restorations passed**, exit 0. No pytest or replay process ran alongside the mutation runner. [Console](chi-evidence/controls.txt), [results](chi-evidence/controls/results.json).

Read all nine new mutation definitions and directly inspected six new mutations' red/green transcripts:

| Mutation | Observed failure with mutation; restoration |
| --- | --- |
| `construction_counter_classification` | Request-specific count error escaped as APIStatusError; restored test passed. |
| `construction_counter_split` | Aggregate refusal lost all usable windows and reached empty-working-T rejection; restored test passed. |
| `construction_counter_no_model_receipt` | Five dispatch receipts versus six MODEL receipts; restored test passed. |
| `construction_resume_preview_dispatch` | Preview entered generation admission and exited 2 at the zero-token-cap guard instead of completing the preview; restored test passed. The independent spending barrier remained effective. |
| `construction_account_credit_scope` | Both HTTP-200 and HTTP-400 credit errors incorrectly classified as window refusals; both restored cases passed. |
| `construction_resume_account_scope` | Known credit receipt was accepted for resume instead of raising; restored test passed. |

All **150 tracked files**, including all **28 mutation-target files**, match their saved pre-run SHA-256 hashes and the untouched subject checkout. Both checkouts are clean at the requested head; `git diff --check` passes. [Verification summary](chi-evidence/verification-summary.json). All 628 individual control transcripts are retained under [chi-evidence/controls](chi-evidence/controls/).

## Remaining operational gap and finding placement

The author's live count-only preview stopped at the first recount because of insufficient API credit. Restore authorized account access, then rerun the count-only preview to verify live restoration through window 18. The reported real-run restoration of 140 commitments and the live credit diagnosis are author evidence; this review independently reran offline placeholder tests only. It neither repeated those provider calls nor established that every live count succeeds.

There are no actionable code defects from this review. The one action-relevant operational finding—live restoration still requires account access and verification—is placed in this section and disclosed in the opening verdict.

**1 findings, 1 placed.**

DONE chi review verdict=merge blocking=0 tests=681/683 negctl=pass
