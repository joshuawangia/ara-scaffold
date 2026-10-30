## Re-review theta

**Verdict: merge theta; 0 blocking, 0 should-fix. T-B1 and T-S1 are resolved by design and independent verification.** Narrow re-review of `be7468df12d4c0422d54f8ccd881d653cd92bdd4` against `b063433d56f83f058d4941c8c8a30b43ec0cf355`, following `iota-rereview-theta.md` and `theta-round-3.md`. I inspected the actual diff and new mutations after reading the brief, then the author's Round 3 report. Verification runs in the detached `/home/dev/ara-work/iota-theta-rereview` checkout. No author-branch edits, delegation, live token counting, paid calls or push. Eta's rebase is outside this re-review; the earlier eta findings and integrated-run verdict are not superseded here.

### T-B1 resolved — reuse binds the current acceptance contract

**Locations:** `ara/runtime/extraction.py:25`, `:28`, `:283`, `:339`, `:381`, `:433`, `:449`; `ara/runtime/cli.py:135`.

Completed outcomes now record a versioned identity covering inference policy, provider, effective extraction model/effort/thinking/fallbacks, and prompt/schema hashes. CLI supplies the profile-applied configuration and contract root to the reusable-success index. Both index construction and the execution boundary compare the identity. Missing or incompatible identities return a source to native extraction/validation instead of treating the old graph as accepted under new rules. Strict coverage is checked before reuse, closing the related partial-source bypass.

This fixes the design, rather than only adding a special case for inference. An explicit interpretation version covers validation/normalization/mode-schema changes and must be bumped with such changes. Budget, recovery and unrelated-stage settings remain outside the identity; the tests confirm those changes preserve compatible reuse. Legacy outcomes without this identity cannot automatically supply completed-paper reuse, while their existing pinned literature and original receipts remain valid historical imports. A native cache hit may still avoid a new dispatch, but it undergoes current validation with original production receipts retained.

**Independent proof:** I reran the previous native CLI counterexample. Fresh and resumed extraction now both mark the premise-only placeholder paper failed when `extraction_require_inference` changes to true; neither publishes it as extracted. A separate same-cache probe rejects the old cached response under the new rule, records zero new charge and retains the original USD0.00175 simulated charge. The full suite also passes model/settings/version/prompt/schema/legacy drift, cap-only compatibility, execution-time recheck and strict-coverage cases.

### T-S1 resolved — verified ancestor successes remain reusable after an intermediate stop

**Locations:** `ara/runtime/provenance.py:99`, `:108`; `ara/runtime/extraction.py:449`, `:466`, `:477`.

Resume now uses a separate historical outcome inventory after verifying the pinned origin chain/imports. It filters candidates through current source and acceptance identity checks and the accepted merged-graph receipt. Conflicting compatible successes explicitly refuse before receipt import. Current-batch publication still uses `extraction_outcomes`, so adding ancestor candidates does not reintroduce old failures or duplicate papers into the published corpus.

**Independent proof:** A completes `p`; B imports A, fails on `q` before visiting `p`, and stops; C resumes only from B. C now reuses `p` with zero new calls. Its total simulated cost remains USD0.0035, retaining both original attempts exactly once. Its current corpus contains only successful `p`, while historical failed `q` remains disclosed. The completed artifact passes native literature provenance verification.

The documented API now clearly distinguishes `historical_extraction_outcomes` (candidates) from `extraction_outcomes` (current corpus), and requires effective config/root arguments for `resume_papers`. Eta can consume this contract in its own rebase; no eta repair or re-review is claimed here.

### Fresh extraction-full command and retained operating limits

**The command shape is verified offline at this head.** I ran the native CLI through profile/config validation and actual PDF intake, intercepting the injected calls factory before any provider could be constructed. Sockets were blocked. Both a fully isolated fresh command and a fresh destination importing only prior receipts reached the expected interception. Exit 2 with `PreflightCaptured` in these receipts is intentional, not a failed extraction or a generation attempt.

The inventory remains **26 PDFs / 1,379 physical pages / 82 affected pages**. The known PDF encoding/font warnings remain in the preflight log. Use the existing `--missing record-only` policy and retain partial-source disclosures. No OCR, semantic fidelity or completed 26-paper extraction is claimed.

The [reviewed config proposal](iota-theta-rereview-config.proposed.yaml) preserves the original full26 configuration, changing only the cache path to an unused location and making the full profile's default failure threshold explicit. Effective values checked at the native boundary:

| Setting | Verified value |
|---|---|
| Extraction provider/model | Anthropic / `claude-opus-5`, high effort, adaptive thinking |
| Fallbacks | Disabled |
| Enclosing and extraction USD caps | 125 / 125 |
| Token cap | 12,000,000 |
| Acceptance/recovery | Require inference; one targeted correction per response |
| Failed-paper limit | 3; exceeding it stops publication |
| Ordinary paper allowance | 24 continuations / USD15 |
| At least 300 physical pages | 48 continuations / USD30 |

For this continuing campaign, use a **new destination and cache** and carry the original stopped run's receipts so the USD125 cap includes its **USD0.818205** already spent. The native preflight confirmed **USD124.181795 remaining** after import. The original run has **zero completed papers**, so this does not reuse its partial range: all 26 papers still require extraction.

```bash
cd /home/dev/ara-work/theta
mapfile -t iota_paper_ids < /home/dev/ara-work/reports/delta-rereview4-paper-ids.txt
iota_paper_args=()
for iota_paper_id in "${iota_paper_ids[@]}"; do
  iota_paper_args+=(--paper-id "$iota_paper_id")
done
uv run ara extract \
  --config /home/dev/ara-work/reports/iota-theta-rereview-config.proposed.yaml \
  --profile extraction-full \
  --manifest /home/dev/ara-scaffold/literature/manifest.yaml \
  --fulltext-dir /home/dev/ara-scaffold/literature/fulltext \
  --missing record-only \
  --run-dir /home/dev/ara-work/theta/runs/full26-rerun-be7468d \
  --resume-from /home/dev/ara-scaffold/runs/full26-extraction \
  "${iota_paper_args[@]}"
```

[Command proposal](iota-theta-rereview-command.proposed.sh); syntax checked with `bash -n`, generation not executed. The proposed run/cache paths were absent during preflight and remain uncreated by this review. A fully isolated fresh run omits `--resume-from`; that form was also checked, but gives a USD125 new-run allowance without importing the old spend. Its campaign accounting must still include the original log. Preserve the origin log/checkpoint for the receipt-carry form.

The current head changes no extraction prompt, schema or planning inputs relative to `b063433`; no new provider token count was needed or performed. Existing cost scenarios remain scenarios. Finite caps, whole-paper-only reuse, original receipt retention and the lack of live semantic/completion proof remain T-N1 operating limits. The original paid partial range is not rescued by this change. This review checks theta's extraction readiness for the bounded experiment; it does not certify eta's shared-T path.

### Re-review verification and mutations

| Check | Result | Receipt |
|---|---|---|
| Full `uv run pytest` | 473 passed, 2 live-provider skips / 475 collected; exit 0; 294.04s | [Full output](iota-theta-rereview-pytest.txt) |
| Independent previous-counterexample/cache probes | 3 passed; 1.76s | [Source](iota-theta-rereview-probes.py), [output](iota-theta-rereview-probes.txt) |
| Native command preflights | Both reached the expected pre-provider interception; 0 provider creations/new calls | [Structured receipt](iota-theta-rereview-preflight.json), [fresh output](iota-theta-rereview-preflight.txt), [receipt-carry output](iota-theta-rereview-carry-preflight.txt) |
| Full control runner, after pytest | 188/188 mutations failed as expected; 188/188 restorations passed; exit 0 | [Full output](iota-theta-rereview-controls.txt), [results](iota-theta-rereview-controls/results.json) |

I read all seven new mutation definitions and their fresh red/green traces. Each red result was a behavioral assertion failure (pytest exit 1), followed by its corresponding restored pass (exit 0):

| Mutation | Observed failure under mutation | Trace pair |
|---|---|---|
| `resume_acceptance_policy` | Changed inference policy failed to reject the resumed paper | [red](iota-theta-rereview-controls/resume_acceptance_policy-red.txt), [green](iota-theta-rereview-controls/resume_acceptance_policy-green.txt) |
| `resume_acceptance_model` | Model drift reused the old paper with no new extraction | [red](iota-theta-rereview-controls/resume_acceptance_model-red.txt), [green](iota-theta-rereview-controls/resume_acceptance_model-green.txt) |
| `resume_acceptance_version` | Interpretation-version drift reused the old paper | [red](iota-theta-rereview-controls/resume_acceptance_version-red.txt), [green](iota-theta-rereview-controls/resume_acceptance_version-green.txt) |
| `resume_ancestor_inventory` | An interrupted descendant caused another call for the completed ancestor paper | [red](iota-theta-rereview-controls/resume_ancestor_inventory-red.txt), [green](iota-theta-rereview-controls/resume_ancestor_inventory-green.txt) |
| `resume_ancestor_conflict` | Conflicting compatible completed outcomes failed to refuse | [red](iota-theta-rereview-controls/resume_ancestor_conflict-red.txt), [green](iota-theta-rereview-controls/resume_ancestor_conflict-green.txt) |
| `resume_execution_policy` | A policy change after indexing bypassed the execution-boundary refusal | [red](iota-theta-rereview-controls/resume_execution_policy-red.txt), [green](iota-theta-rereview-controls/resume_execution_policy-green.txt) |
| `resume_strict_coverage` | Strict coverage failed to reject a reused partial paper | [red](iota-theta-rereview-controls/resume_strict_coverage-red.txt), [green](iota-theta-rereview-controls/resume_strict_coverage-green.txt) |

After the runner exited, both scratch and author checkouts remained clean at `be7468df12d4c0422d54f8ccd881d653cd92bdd4`. Unstaged and staged `git diff --exit-code`, `git diff --check`, and empty porcelain status confirmed restoration. The proposed paid run/cache paths remain absent. No live-provider result or eta integration result is implied by these offline checks.

### Re-review finding placement

| Finding/disposition affecting the next action | Placement |
|---|---|
| T-B1 resolved, identity/version duties, legacy restriction and cached revalidation | T-B1 resolved; Re-review verification and mutations |
| T-S1 resolved, ancestor inventory, conflict checks and current/history separation | T-S1 resolved; Re-review verification and mutations |
| Fresh command, original-spend carry, partial-source/whole-paper/live-proof limits and separate eta scope | Fresh extraction-full command and retained operating limits; opening scope |

3 findings, 3 placed.

DONE iota rereview theta=merge blocking=0 should_fix=0 tests=473/475 negctl=pass
