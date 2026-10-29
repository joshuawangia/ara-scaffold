# Xi Round 19 — semantic novelty and content bindings

Base `2c4741d481e53bac6f32f644678eef86302028a7`, branch `feat/run-report`,
checkout `/home/dev/ara-work/xi`. Local implementation and verification only;
no paid calls, push or delegation. Evidence: `runs/xi-round19/`.

## F1 fixed: semantic admission and qualifying conclusions

Novelty now rejects classical consequences of all frozen T, using the existing
bounded cached Z3 path. Fresh atomic applications must be essential: replacing
all corresponding occurrences by true or false must change target truth under T.
Unknown/timeout refuses, including during essential-atom checks. Receipts include
basis IDs, every result and substitution, and essential application identities.
Free/constant identity and repeated/distinct bound-variable patterns are kept;
unused surrounding binders cannot manufacture a new application.

The root and qualifying bank-step conclusion are checked against the entire
freeze, including uncited commitments. A reachable nonstructural step must conclude
an essential new proposition of the root. Unused conditional-proof assumptions
cannot qualify. A genuine new sign conclusion can still qualify beneath an unused
conditional wrapper; the wrapper step itself does not count. Otherwise-contributing
closures without a qualifying step are CLOSED-structural and not default-selected.
Existing single-support, stance, license, CQ and unresolved-check gates remain.

Kappa4's nested implication conjunction, equivalent implication/disjunction,
double negation and quantified wrapper probes are rejected. Native closure of the
unused-assumption conjunction remains CLOSED but is structural and not selectable.
An unrelated new inference or an unreachable inference cannot upgrade a route.

## F2 fixed: definitions and independent content judgments

Typed optional `Proposition.new_symbols` entries bind name/kind/arity to content
text. The codec omits absent entries, preserving historical proposition encoding.
CommitmentSet, commitments.json and frozen catalogue v1 formats are unchanged.
For one atomic assertion its full target text is its default content binding;
compound targets require explicit otherwise-unbound fresh definitions. Missing,
duplicate, unused and frozen-name overrides refuse.

New definitions are compared with T text and verified catalogue definitions using
NFKC/casefolded word equality and a conservative near-duplicate threshold (0.90
character similarity, minimum 20 normalized characters). The existing logged
classifier receives the T content list, rendered formula and proposed definitions.
It must return own_thesis, novelty=new_assertion and fidelity=matches. Restatement,
renaming, definitional packaging, mismatch and uncertain judgments refuse.
Definition bindings and all judgments participate in cache inputs and receipts.

The native text-P/formula-R probe is rejected by deterministic reuse checking,
even with a positive fake classifier judgment. The R := (P and Q) probe is
rejected by the required restatement judgment. Separate mismatch, uncertain and
restatement controls demonstrate that own_thesis alone cannot admit a target.
A genuine new R via sign remains accepted, engine-closed and default-selectable
with two endorsed source supports and answered CQs.

## Consequence policy change

The brief explicitly excludes the deductive closure of T. Q from {P,P -> Q}
therefore remains a valid licensed modus-ponens conclusion but is not a novel
target or a default-selectable novel route. This supersedes Round 18's acceptance
policy. Native engine deduction regressions remain; success-path lifecycle
fixtures now use genuine new defeasible conclusions instead of weakening the gate.

## Limits and operational prerequisites

Lexical near-duplicate screening is conservative and may reject close wording.
The model's novelty/fidelity judgment is evidence, not a semantic proof; fake
providers cannot establish live judgment accuracy, source/formula fidelity,
semantic originality, scheme fitness or truthful CQ answers. No paid pilot or new
real-corpus synthesis is claimed. Round 19 does not rerun the historical real-T
fork; Round 18's separate mock proof and refused native CLI remain historical.

The classifier schema now requires two additional judgments. Old live schema
preflight receipts are stale and must be refreshed against the effective live
configuration before a paid/subscription run. No preflight was fabricated or bypassed.

## Verification

Before implementation, all 11 initial blocker regressions failed (`red.txt`).
The added unused-binder probe also failed before its identity fix (`binder-red.txt`).
Focused controls: 24/24 mutation/restoration pairs passed before the final binder
control was added; all touched source hashes restored (`focused-controls.txt`).
Final full-suite and full-control counts are recorded below once complete.

## Finding placement

5 findings, 5 placed: fixed F1 in “F1 fixed”; fixed F2 in “F2 fixed”; changed
classical-consequence admission in “Consequence policy change”; limits of lexical
and model judgments plus stale live preflight in “Limits and operational prerequisites”.

Final affected-test checkpoint: **207 passed** (`affected-final.txt`). The first
full run exposed a native CLI smoke fixture comparison that rendered CQ-bearing
graphs without frozen T; production rendering already supplied T. The known-failed
full run was stopped before controls, its logs preserved as `first-*`, and the
comparison was repaired to pass the same frozen T. The subprocess smoke/replay
regression then passed (`e2e-fixed.txt`, 1 passed). Full gates were restarted on a
fresh 225-file source snapshot. No production gate was relaxed for this repair.

Independent-gate verification: the old `closure_unknown` mutation was masked by
its fixture making every solver query unknown (`masked-control.txt`, mutated and
restored both passed). The fixture now makes only the contribution queries
unknown while whole-T novelty remains decidable. The own-thesis guard fixture
also uses a genuine new target so deductive closure cannot mask that guard.
A qualifying-step timeout now has an explicit receipt and unresolved label
(`step-unknown-red.txt` before the fix). The broader policy control run passed
**56/56** mutation/restoration pairs with every touched source hash restored
(`policy-controls.txt`, `policy-control-results.json`). The final focused tests
passed **76/76** (`focused-last.txt`). The second partial full run was deliberately
stopped for this coverage repair and is preserved as `second-*`; it is not a
full-suite pass. Final full verification uses **531 controls**.

The third full run completed with 1224 passed, 4 skipped and one fixture failure:
`test_two_rich_catalogues_share_global_capacity` asserted a historical 10,000-token
prompt footprint. Expanded policy input measured 10,679 tokens, within its configured
20,000-token working budget. The assertion now checks positive measured usage within
that configured bound; no production budget changed. Its targeted regression and
`root_measured_remaining_capacity` mutation/restoration control both pass
(`rich-fixed.txt`, `rich-controls.txt`). The complete diagnostic run remains in
`third-*`; final full gates are rerun after this test-only repair.

## Final gates — 2026-10-28

Full pytest: **1225 passed, 4 skipped / 1229 collected**, exit 0,
901.58 seconds. The full control runner began only after pytest succeeded:
**531/531 expected mutation failures and 531/531 restored passes**, exit 0.
All **225 pinned source files** match the original snapshot, including the
**51 files** touched by controls. `git diff --check` passed.

The command was `ARA_LIVE_TEST=0 TMPDIR=/dev/shm/xi-round19 UV_OFFLINE=1
uv run --offline --locked python runs/xi-round19/verify.py`. It runs pytest and
the integration control runner sequentially. Receipts are
`runs/xi-round19/final-verification.json`, `pytest-full.txt`,
`full-control-results.json`, `controls-full.txt`, `controls/`,
`source-before.json`, and `source-after-controls.json`. No paid calls or push.

## Committed revision

Local head `44cced12f901ce01722d639d1ce5010ab905ddc7` on `feat/run-report`. The working tree is clean.
All 225 committed file contents match the tested snapshot (tracked symlinks
checked through their canonical target). Proof: `runs/xi-round19/commit-verification.json`.
No push. **5 findings, 5 placed**, as mapped above.
