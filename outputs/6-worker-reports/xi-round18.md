# Xi Round 18 — novelty and substantive closure

Base: main `412a457`, branch `feat/run-report`, checkout `/home/dev/ara-work/xi`.
No paid calls, network provider calls, push, or worker delegation.

## Behavior and interpretation

Pre-search Boolean dependence is checked deterministically using two independently
interpreted formula copies. Equal truth values for every complete T formula must
permit unequal target truth values. UNSAT excludes Boolean recombination, including
equivalent disguises and vacuous atoms. Main implication consequents are checked
separately, retaining outer quantifiers. Unknown/timeout refuses. Existing validity,
single-support, attribution, stance and own-thesis gates remain active, with
concrete correction feedback and frozen basis IDs.

Finding 1: “new proposition” is implemented as a new asserted atom/application,
not a vocabulary symbol absent everywhere inside T. Q is eligible for T={P,P→Q}
(subject to all other gates). The optional clarification received no answer; this
interpretation was disclosed during work and preserves substantive deductive
linking. The canonical policy and regression explicitly pin it.

A reachable known nonstructural bank inference is additionally required for
`CLOSED-derived`. Conjunction introduction/elimination, disjunction introduction
and double negation do not qualify. Otherwise contributing closures become
`CLOSED-structural` and are excluded from default selection. Unreachable nodes
cannot qualify. The actual bank, structural/substantive groups, catalogue and
placeholder examples are supplied to proposal.

Finding 2: this proves formal assertion novelty and native mechanical closure,
not semantic originality, faithful formalization, source fit or truthful CQ
answers. No new live pilot is claimed.

## Executed evidence

Initial Round 18 regressions were red: 10 failed before implementation. Focused
final regression: 16 passed. Affected legacy tests: 101 passed; the single new
correction test initially used the wrong frozen fixture, then passed after its
fixture was bound to its own T. Canned mock recordings were re-keyed to current
prompt/input hashes by the existing native fixture builder.

The native placeholder regression retains R and rejects P∧Q before search, closes
R through `sign` using two endorsed commitments from two source IDs and answers
all CQs, and reports a historical conjunction route as `CLOSED-structural`.
Default selection admits only the substantive route. It also verifies that an
unreachable sign inference cannot inflate a structural route.

Final pinned full-suite/control counts and commit receipt follow below when
complete. Evidence directory: `/home/dev/ara-work/xi/runs/xi-round18`.

## Real-T offline fork

Finding 3: the native `fork-from-freeze --provider mock` command verifies and
copies pilot 5's frozen prefix but refuses stale inherited Codex preflight.
Its stage overrides remain Codex even with the top-level mock option. No live
preflight was executed or bypassed. This CLI outcome is reported as `refused`.
An explicit all-mock configuration is logged on the already verified copied
freeze for the separate native target-gate exercise. The source is read only;
source hashes and fake-provider dispatches are retained in the fork receipt.

## Finding placement

3 findings, 3 placed: interpretation and semantic limits in “Behavior and
interpretation”; native CLI refusal in “Real-T offline fork”.

Offline harness settings and diagnostics: the fake provider uses the existing
priced mock model and an explicit 2,000,000-token context bound because its byte
counter exceeded the inherited 200,000 bound. This is an offline fixture allowance,
not a claim about live model capacity; inputs are not truncated. A harness-only
hash-helper type error produced a failed mock receipt; the retry retains it and
uses logged count-at-reservation reconciliation. These setup failures and the
stale preflight refusal remain in the append-only fork log. The final gate receipt
will distinguish this harness from an accepted native CLI run.

Completed real-T gate receipt: `runs/xi-round18/fork-verification.json`.
The fake proposer ran three attempts against all 169 commitments, verified the
canonical commitments hash `0d750f19b3812887cadfed90a850afb274d17476491678880060c9d35aa64520`,
and received Boolean-recombination feedback. No targets survived; no search
provider request was made. The independently cached own-thesis classification
was reused after its first fake call. All five source file hashes stayed unchanged
(events, anchor, commitments, frozen envelope and provenance). The raw
commitments.json byte hash remains `390163f35a3b8d4604750ddd18813e938d449030006b1be0f41a20c0490944eb`;
this differs from canonical CommitmentSet hashing by serialization, as expected.
Result: native CLI `refused`; verified-copy native target-gate harness `ok`.

## Final verification and local handoff

Committed `2c4741d481e53bac6f32f644678eef86302028a7` on `feat/run-report`; clean working tree, no push.
Full offline pytest: **1195 passed, 4 skipped / 1199 collected**, 876.41 seconds.
Full control runner, after pytest: **517/517** mutations failed as expected and
all restored runs passed. All **223 pinned source hashes** restored, covering
**49 mutated files**. Committed blobs match the pinned source (symlinks resolved).
Receipts: `runs/xi-round18/final-verification.json`, `commit-verification.json`,
`pytest-full.txt`, `controls-full.txt`, `full-control-results.json` and `controls/`.
The verification process continued through the server restart; it was inspected
and allowed to finish without re-running or interrupting the active mutation.
Caller-owned integration/review remains external to this local implementation;
standalone shipping skipped. Implementation ran natively, with no external agent
engine binding or delegation. No further implementation work is pending.
Final status: novelty gate yes; structural label yes; native CLI offline fork
refused for stale inherited preflight, separate real-T fake-provider gate proof ok.
