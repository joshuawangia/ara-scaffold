# pi3 quality5 — code and verification in progress; no live polish

The publication changes are committed locally at `b6fc454`, following merge `9fbf4d6` of nu4 round 6 `d9ac619f6d95dfc588926044944d02d6181e5bdd`. Nu4 round 7 remains uncommitted and is not claimed as merged. No push, delegation or live model run was performed.

## Structural repair retries

A repair gets two structural attempts inside the same numbered round: the initial response and one bounded retry. The three-round semantic repair limit remains fixed, so at most six repair proposals can be generated. Retry feedback contains the exact validator failure, rendered current/previous word counts, effective floor and ceiling, and each section that shrank. The retry retains the same accepted baseline, exact flagged occurrences and audit reasons. Invalid output is never adopted or audited. A second invalid response exhausts that round's structural allowance and retains the original fallback honestly. The configurable 3,000-word profile minimum and fixed 6,000 ceiling are unchanged (Q5-F1).

Only flagged sentence spans may change. The existing paragraph/block occurrence restriction now also protects unflagged sentences inside a flagged paragraph. The prompt instructs the editor to preserve supported content and length, rewrite only flagged occurrences, and avoid padding. Frozen citation and route-marker inventories remain required (Q5-F2).

## Conservative publication gate

Publication reuses nu4's `audit_consensus` with publication context and the effective audit provider. Every gate requires at least three fresh samples (`essay_audit_samples`, default/minimum 3); it unions all flags and unresolved adverse history for the same audit input and requires unanimous acceptance. It bypasses favourable cached responses. Publication-only reasons, current titles/headings, source evidence and logged literature-currency evidence remain part of the input. Both the initial post-polish audit and the post-verification audit use this gate. A changed candidate receives another complete gate; an unchanged repair cannot erase a recorded dissent. Receipts retain samples, historical flags, agreement and the derived result (Q5-F3).

## Integration and verification

Nu4 round 7's citation-preserving verification is still pending upstream. Only committed upstream changes will be merged; its in-progress checkout remains untouched. Final verification will run on the merged revision (Q5-N1).

Six new regressions were observed failing before their fixes: five retry/consensus cases plus the unflagged-sentence case. The first new-suite run passed five tests and exposed an incorrect expected fixture count in the sixth: rendered citations make the section 909 words, shrinking to 11, a decrease of 898. That expectation was corrected. The broader focused suite passed **138 tests**; the final seven-test suite, including a new post-verification gate check, passed **7/7**. All **660 mutation anchors** resolve exactly once. Preliminary full pytest on `b6fc4544c47f1ffb24079443dcb75ff9d71608f0` passed: **1,450 passed, four skipped / 1,454 collected**, exit 0, in 1,894.93 seconds; the source snapshot is unchanged. The 52 publication/consensus mutation controls are running sequentially afterward in an isolated checkout. These are pre-round-7 receipts; no final merged-suite/control verdict is claimed yet. [Proof directory](/home/dev/ara-work/pi3/runs/pi3-quality5-proof/).

The inline simplification pass applied no changes. The implementation reuses existing validation-feedback transport and the shared consensus gate. Proof tests were retained. No separate lint/typecheck command is configured. Non-author review remains caller-owned; authored offline tests establish enforcement given labels, not semantic truth or audit stability (Q5-N3).

## Live boundary

**No live polish was run for quality5.** The operator will start it later on nu4 round 7's exported route essays. Quality4's failed audit/fallback remains historical evidence; this code change does not retroactively improve it or establish a new accepted paper. No new PDF, word count or live semantic pass is claimed (Q5-N2).

Finding placement: Q5-F1/F2 → “Structural repair retries”; Q5-F3 → “Conservative publication gate”; Q5-N1/N3 → “Integration and verification”; Q5-N2 → “Live boundary”. **6 findings, 6 placed.**
