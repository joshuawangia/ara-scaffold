# Upsilon — independent review of Sigma round 2

Review subject: `/home/dev/ara-work/sigma`, branch `fix/bounded-closure`, head `4a5fbc3bd0988ec38f8826f94d31a82a95527d28`, base `5009af1e053d11dac18405fe7402331134585fea` (`main` at intake). Read the round-two brief, author report, Zeta part 5 and repository rules/plan. No delegation, branch edits, push or paid calls. Verification runs in an independent local clone at `/home/dev/ara-work/upsilon-review-check` so mutation controls cannot modify the subject checkout.

**Verdict: fix-first. One blocking finding; zero additional should-fix findings.** Full pytest and all 291 mutation controls passed their expected checks sequentially. The reproduced admission defect below is not covered by those tests. Resolve it before the paid pilot.

## Blocking finding B1 — soft shares still veto closure admission

`ara/runtime/construction.py:301–308,369–387` computes shares from the headroom-adjusted capacity and then uses them as mandatory bounds in `fits`: both `per_window_commitments` and copied-envelope-plus-growth versus `working_share` can reject a selected bundle. `depth_cut` uses this same predicate for mandatory roots. Thus borrowing is allowed only after a closure passes hard window-share admission. This contradicts the round-two requirement that shares guide planning only and only global budgets/context remain hard.

The consequence is especially clear after legitimate output borrowing consumes the planned 80% allocation: later shares become zero even when actual global capacity remains. Every later nonempty root bundle then fails `fits`; selection calls can still spend money, but no formalization is attempted. The code logs ordinary budget cuts and can freeze an unnecessarily small T without a global-exhaustion event.

Two independent, network-disabled probes reproduce the behavior on unmodified production source:

* With the normal 100,000 working budget, a mocked first accepted batch measures 82,000. The next two windows each have 18,000 remaining but zero shares and zero commitment slots. Both selected single-premise roots are discarded. Only the first commitment freezes. The same deterministic counter would measure all three outputs at 84,000; the reused symbol catalogue also fits. Dispatches are selection/formalization for window 0, then selection only for windows 1 and 2.
* With a 1,500 global budget and a 1,000-token wrapper, each single-premise output adds 100 measured tokens. Shares are 66, 100 and 200, each below the 233-token planning reservation. All windows are discarded while 500 global tokens remain, ending in `empty working T after accounted omissions`, with no freeze. Changing only the soft headroom setting from .2 to .01 admits the final two windows and freezes them within the same hard budgets. This comparison diagnoses the hard planning cutoff; it is not a proposed configuration workaround.

Evidence: `upsilon-evidence/probes.py`, `probes.json`, `headroom-probe/run/events.jsonl`, `empty-probe.py`, `empty-probe.json`, and the two `empty-*` receipt directories. All model responses/counts in these probes are deterministic placeholders; no real-provider output or charge is claimed.

Required before the pilot: retain shares as selection/planning guidance, but let closure admission borrow against recounted remaining global capacity. Preserve mandatory qualifiers/endpoints, exact request/context checks, accepted-output bounds and explicit omissions. Add a regression that crosses the headroom target and still accepts later fitting windows, plus a mandatory bundle that exceeds its local share but fits globally. Do not simply increase the configured hard bounds. `DECISIONS.md` S2 explicitly says closure depth still follows planning targets; that explains the implementation but does not resolve the conflict with the task's soft-share requirement.

## Other requested checks

* **Accepted-output borrowing and hard bounds:** actual working/catalogue share checks were removed. Accepted outputs still face global working, global catalogue and downstream context validation (`construction.py:462–470`). Borrowing is logged after `construction_call` returns. The remaining problem is the earlier admission cutoff described in B1.
* **Refusals and no partial-state leakage:** selection/formalization validation failures and construction-scoped context refusals are caught per window. The skip receipt carries reason, omitted IDs, valid roots and closure when available; invalid raw responses stay in MODEL receipts. Symbols, materialized IDs and results are updated only after the full checked and accounted call returns (`construction.py:476–492`). The independent rejection probe accepted only P and R after rejecting Q twice; the merged catalogue contained only the accepted F symbol.
* **One bounded, nonempty freeze:** global exhaustion marks the remaining windows omitted and reaches the existing merge/freeze path. The merge verifies batch inventory, nonempty T and full evidence accounting. Final working/catalogue/context recounts precede the sole freeze; `prepare_commitments` rejects an existing freeze. Campaign/unknown-usage/operational failures propagate. No empty or partially rejected T freeze was found in the inspected paths. Logical inconsistency is not a rejection criterion: the existing merge intentionally retains distinct evidence even when formulas contradict; this review's consistency claim concerns construction state and inventories.
* **Recount and spend:** each dispatched window recounts accepted working T and catalogue, recomputes shares using remaining windows, and counts each initial/correction request again before dispatch. The independent rejection probe retained both rejected attempts: 300 tokens and mock USD0.0035. Total mock usage was 1,200 tokens/USD0.01400 and exactly reconciled to the event log and in-memory budget. The rejected window contributed no commitment or symbol and the remaining accepted work froze once.

## Verification results

Full `uv run --locked pytest -q` completed with **642 passed, 2 skipped (644 collected), 303.51 seconds**, exit 0, against the exact review head. The two skips are opt-in live-provider checks. Only after that process exited, `uv run --locked python tests/integration/negative_controls.py` ran: **291/291 mutations failed their targeted tests and 291/291 restorations passed**, runner exit 0. All 291 mutation anchors were independently checked to occur exactly once before execution. Independent probes finished before mutations started; no other tests ran alongside the control runner.

Preserved evidence: `upsilon-evidence/pytest.txt`, `controls.txt`, `controls/results.json`, all 582 individual mutation/restoration outputs, `final-verification.json`, and a SHA-256 manifest. Inspected the final failure/pass summaries for all 13 soft-share controls as well as their mutation definitions. After the runner exited, every mutation-target file matched its pre-run SHA-256. Both the subject checkout and verification clone remained clean at the requested head. `git diff --check 5009af1..4a5fbc3` passed. No source edits or commits were made.

Read all 13 soft-share mutations and their owning tests: `soft_working_output`, `soft_symbol_output`, `soft_recompute`, `soft_recount`, `soft_window_skip`, `soft_context_skip`, `soft_exhaustion`, `soft_global_working`, `soft_campaign_stop`, `soft_exhaustion_disclosure`, `soft_indivisible_window`, `soft_final_catalogue`, and `soft_counter_failure`. Definitions and original source hashes are preserved in `upsilon-evidence/mutation-review.json`. They exercise actual-output borrowing, recomputation, skip continuation, hard boundaries and exhaustion; none tests continued admission after borrowing consumes the headroom-adjusted allocation.

Specifically, `test_actual_output_borrows_within_global_limits` has only one window. The multi-window recomputation test reaches 31,000, 61,000 and 91,000 working tokens, crossing the 80,000 planned target only on its final window. Neither can expose starvation of a subsequent window.

## Scope and next step

No live construction, semantic fidelity, downstream search or pilot outcome is verified. The author’s existing real-plan receipt reports unchanged 48-window/144-slot allocation and 67,631 maximum input tokens; this review has not independently called the provider token counter. Fix B1, rerun the affected native-path proofs and complete the required delivery checks before a paid pilot.

## Finding placement

| Action-relevant finding | Placement |
| --- | --- |
| Soft targets remain hard closure limits, including zero-share starvation and empty-T failure. | Blocking finding B1 |
| Rejected output does not leak; its spend remains counted; freeze retains its inventory/nonempty/budget checks. | Other requested checks |
| Full suite and all controls pass, but existing new mutations do not cover the reproduced pre-formalization borrowing gap. | Verification results |
| No live semantic/search/pilot success or independent provider-counting claim. | Scope and next step |

4 findings, 4 placed.

DONE upsilon review verdict=fix-first blocking=1 should_fix=0 tests=642/644 negctl=pass

## Re-review

### Scope and verdict

Re-reviewing only B1 at `1411e91c70a6537422dbfece6f6ed1301b90e748`, against `4a5fbc3bd0988ec38f8826f94d31a82a95527d28`, per `briefs/upsilon-rereview.md` and `briefs/sigma-round-3.md`. The original review above remains the historical verdict on round two. Read the round-three author report and complete five-file diff. Verification runs in a fresh independent clone, `/home/dev/ara-work/upsilon-rereview-check`. No edits to the subject branch, delegation, push or paid calls.

**Verdict: merge. B1 is fixed; zero blocking findings remain in this narrow re-review.** Independent probes, full pytest and all 293 mutation/restoration controls passed. Evidence is in `upsilon-evidence/rereview/`; controls started only after pytest exited zero. This verdict supersedes the round-two fix-first verdict for the reviewed repair.

### B1 repair and independent reproduction

`construction.py:369–383` no longer rejects closures by per-window item slots or working shares. It counts the candidate together with previously accepted commitments, subtracts the current accepted envelope, reserves growth only for newly materialized IDs, and checks recounted global working/catalogue capacity. The same predicate governs depth cuts. Mandatory qualifier/endpoint closure logic is unchanged. The updated selection prompt and S2 now describe this actual behavior.

Reran the prior independent probe inputs and mocked counts unchanged, updating only output destinations and assertions to require the repaired behavior:

| Probe | Re-review result |
| --- | --- |
| First window consumes 82,000 of 100,000 working tokens | All three commitments accepted; remaining capacity before windows is 99,000 / 18,000 / 17,000; later shares remain zero; final T is 84,000 tokens, one freeze, no skipped windows. |
| Global budget 1,500, wrapper 1,000, each output adds 100 | All three accepted under both .2 and .01 headroom; remaining capacity is 500 / 400 / 300; one freeze in each case. Default shares are 66 / 50 / 0 and no longer veto admission. |
| Rejected middle formalization and correction | Both attempts remain charged; only P and R survive; no rejected commitment/symbol leaks into T; one freeze. |

Evidence: `rereview/probes.py`, `probes.json`, `empty-probe.py`, `empty-probe.json`, and their native event/artifact directories. The original round-two reproductions and receipts are preserved separately.

### Hard bounds remain enforced

Ran five additional network-disabled native-path probes after an 82,000-token first accepted window. Each preserves P, skips the offending Q window, accepts later R, and freezes exactly once at 83,000 tokens:

* Candidate working T of 100,001 exceeds the 100,000 global budget.
* Candidate catalogue of 16,001 exceeds the 16,000 global catalogue budget.
* Initial selection context of 200,001 exceeds the 200,000 model context before dispatch.
* Correction context of 200,001 exceeds the same hard bound before correction dispatch.
* Candidate working T of 91,000 is below its 100,000 working budget, but plus 110,000 reserved downstream output exceeds the 200,000 context bound; the candidate is rejected. The retained 83,000-token result plus that reservation fits.

Checked the actual MODEL rejection reasons for the working, catalogue and downstream cases. Their unchanged mock correction subsequently fails the repeated-item check; that terminal reason does not replace the original hard-bound rejection receipt. Evidence: `rereview/hard-bounds.py`, `hard-bounds.json`, `hard-bound-reasons.json`, and all five `hard-*` native receipt directories. Counts and usage are deterministic mock evidence; no provider success or real spend is claimed.

### Verification results

Full `uv run --locked pytest -q`: **646 passed, 2 skipped (648 collected), 305.57 seconds**, exit 0. After that process exited, `uv run --locked python tests/integration/negative_controls.py` completed: **293/293 mutations failed their targeted tests, 293/293 restorations passed**, exit 0. All 293 control anchors were checked for uniqueness and original mutation-target SHA-256 hashes were saved before controls. No independent test or probe ran beside the mutation runner.

Read both new controls and inspected their executed failures/restorations. `global_closure_admission_after_headroom` restores the old working-share cutoff and fails with one commitment instead of three. `global_mandatory_bundle_above_share` restores the old item-slot cutoff and fails with empty T. Both pass after restoration. Their owning tests cover the 82,000-token first window and a five-item mandatory inference bundle above a four-item planning target, including endpoints, qualifiers, distinctions and explicit omitted support.

Every mutation-target file matched its pre-run SHA-256 after completion. The subject checkout and verification clone are both clean at `1411e91c70a6537422dbfece6f6ed1301b90e748`; `git diff --check 4a5fbc3..1411e91` passed. Saved evidence includes `pytest.txt`, `controls.txt`, `controls/results.json`, all 586 mutation/restoration outputs, original target hashes, independent probe scripts/receipts, `final-verification.json`, and a SHA-256 manifest under `upsilon-evidence/rereview/`.

### Limits and finding placement

No new real-provider token count, live construction, semantic-fidelity or downstream-search result is claimed. The selection prompt changed, so earlier exact real-request counts remain historical evidence. This merge verdict addresses the narrow B1 repair and retained hard boundaries. No merge, push or paid pilot was performed.

| Action-relevant finding | Re-review placement |
| --- | --- |
| B1 no longer blocks later fitting closures; both original reproductions now accept all three commitments. | B1 repair and independent reproduction |
| Global working/catalogue and initial/correction/downstream context bounds remain enforced; rejected output stays out of T. | Hard bounds remain enforced |
| Full suite and all 293 controls pass, including regressions and mutations that cover the prior admission gap; all source hashes restored. | Verification results |
| No fresh provider counts or live semantic/search/pilot proof. | Limits and finding placement |

4 findings, 4 placed.

DONE upsilon rereview verdict=merge blocking=0 tests=646/648 negctl=pass
