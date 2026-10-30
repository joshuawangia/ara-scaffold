# Xi Round 28 — INTEG-F1

Work on `feat/run-report` in `/home/dev/ara-work/xi`, from integration head
`0a31afb92c319bd0ae38f71e51b3233050d32758`. Implementation commit `1dce56efbfc97cc3ef00ea1e0f0d123841ddae51`; all required offline gates passed; clean local checkout.
No paid calls, push, source-artifact edits or new worker contexts.

## Behavior

The shared per-paper novelty gate now checks atomic essentiality against the full
admissible frozen union. Endorsed source commitments and disclosed alignment
premises enter that union; reported and attacked content retain their existing
non-premise role. Alignment bridges still own no paper. The receipt records union
commitment IDs and the solver outcome for both true/false substitutions. Unknown
solver results leave novelty unresolved. Union-essentiality implies essentiality
under each individual paper, replacing the weaker substitution loop; target and
atomic non-entailment against each individual paper remain required.

With P from a and Q from b, `(P and Q) or R` and `R -> (P and Q)` no longer become
derived just because R varies under each paper considered separately. Native
bank proofs remain CLOSED, but their contribution classification is structural
and they are not selectable by default. Native proposal and external gap-file
proposal reject both, even with an affirmative fake content/gap classifier.
The same shared gate removes the reviewed `P and (Q or R)` forward candidate.

The union is not a prohibition on union-entailable targets. P from a plus P -> Q
from b still gives selectable Q through native modus ponens. Both positive and
negative deductive conclusions are tested, as is a genuine R conclusion from a
non-logical scheme. Existing reported-opposition and alignment-bridge positives
remain part of the affected suite.

## Verification

New native red proof: four padded-route cases failed before the fix, while four
positive cases passed. Initial runs also found and repaired a fake classifier
fixture that omitted `resolves_gap`; the corrected red run is retained separately.
Initial forward/timeout regressions failed on the old code. An overbroad assertion
that the entire forward inventory must be empty was removed: that is not implied
by the requested union-essentiality criterion. The regression instead checks the
reviewed padded formulas; other generated candidates are not certified as novel.

Five new controls cover union basis, unknown handling, both substitutions,
forward filtering and external-gap admission. Existing stance, atomic closure and
compound-package controls are also included in the focused run. The affected suite passed 124 tests, CLI replay passed 7 tests, and all 8 focused
mutation/restoration pairs passed with actual failing-test transcripts verified.
Full pytest passed on the committed tree: **1,371 passed, 4 skipped / 1,375
collected**, exit 0 in 2,036.76 seconds. All 253 pinned paths matched afterward.
The full **655/655 controls passed**, exit 0 in 5,419.82 seconds. Every mutation
produced actual failing tests, every restored run passed, and all 253 tracked
paths (including the AGENTS.md symlink) match the committed tree afterward.
The checkout is clean. `delivery.json`, `gates.json`, `source-before.json`,
`source-after.json` and all control transcripts are retained in the evidence
directory. `DECISIONS.md` includes Round 28; no push or paid calls. Evidence directory:
`/home/dev/ara-work/xi/runs/xi-round28/`.

## Limits and review

This is a bounded deterministic novelty repair. It does not establish faithful
formalization, philosophical originality, exhaustive rejection of all compound
restatements, or live-provider quality. Other forward candidates remain available;
no zero-false-positive census is claimed. No source/artifact contract changes.

Code review: skipped (ce-code-review unavailable). Its focused path requires an
independent review context; operator instructions prohibit launching new worker
or hidden-agent contexts without explicit authorization. Manual diff and caller
inspection were performed, with no independent-review claim. The attempt is
recorded in `review-attempt.json`. No separate lint/typecheck gate is configured.

## Findings placement

1. Union-relative check, premise roles and solver uncertainty → Behavior.
2. Native/forward/gap rejection and preserved positive cases → Behavior.
3. Executed gates, intentional red proof and repaired test expectations → Verification.
4. Bounded evidence and unavailable independent review → Limits and review.

**4 findings, 4 placed.**

DONE xi round28 head=1dce56efbfc97cc3ef00ea1e0f0d123841ddae51 tests=1371/1375 negctl=pass fixed=INTEG-F1
