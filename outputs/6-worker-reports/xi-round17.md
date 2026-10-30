# Xi Round 17 — target pools and defeasible reachability

Checkout `/home/dev/ara-work/xi`, branch `feat/run-report`, fast-forwarded to
requested main `b48d56f` before changes. Completed at
`fffb7c3cd1526d048ffda302fc877559eba5a2a5`. The worktree is clean and all 220 committed source files
match the pinned verification hashes (resolving committed symlinks); see
`runs/xi-round17/commit-verification.json`.
No paid calls, push, or worker delegation.

## Proposer contract and correction evidence

The proposer receives the actual bank version and entries, including premise
slots, rule kinds, formula schemas and CQs. Placeholder examples distinguish
licensed deduction, defeasible support, and the conditional-consequent trap.
The main claim must be new: a consequent already in T cannot become a new claim
by attaching antecedents. Existing tautology/singleton/both-polarity gates,
attribution/own-thesis checks and stance restrictions remain unchanged.

Correction receipts identify each rejected target, reason and checked polarity,
include the full entailing commitment where present, and explain when that
commitment alone entails the target or its negation. A direct frozen conditional
consequent is identified explicitly. Corrections receive previous proposals and
retained targets, rather than generic advice to reword them.

## Pool and disposition behavior

Ordinary proposal attempts request 20 candidates and retain up to
min(target_candidates, 10). A named position remains one exact-text candidate.
An initial attempt plus at most two corrections can fill remaining places;
passing targets survive in stable attempt/response order. Retained IDs and
alpha-equivalent structural formulas cannot fill two places. Structural
canonicalization does not prove semantic diversity or general logical inequivalence.

Short responses are accepted but explicitly marked underfilled with requested
and received counts; empty or oversized responses remain invalid. Each candidate,
including rejected, duplicate and surplus passing candidates, has a full logged
disposition. The final pool receipt identifies the retained set. New vocabulary
is disclosed as advisory: a fresh thesis atom can be reached through a defeasible
scheme, so vocabulary disconnection must not force its rejection or replacement.

## Native defeasible proof and limits

**Mechanically yes: native nontrivial defeasible closure is possible.** The
placeholder reproduction proposes a fresh R against distinct frozen P and Q.
Contribution and own-thesis preflight accept it. Native search licenses a sign
step, closes both frozen supports, and obtains answers for every sign CQ with
both frozen IDs as evidence. Native publication labels the route CLOSED-derived.
Classical entailment of R from even the entire pair returns SOLVER_COUNTEREXAMPLE.
Leaving those same CQs unanswered keeps the route OPEN.

No engine licensing rule was changed to obtain this result. A mutation that
forces classical deduction checks onto defeasible steps must break the positive
reproduction. The proof does not establish that arbitrary source content fits a
sign scheme, that model CQ answers are true, or that a live target is useful or
original. Those semantic limitations are distinct from native mechanical
reachability. No new paid pilot or real-source synthesis is claimed.

Durable run: `/home/dev/ara-work/xi/runs/xi-round17/defeasible-e2e/` contains event
and trace receipts plus saved routes; `defeasible-e2e.json` summarizes the result.
The parametrized regression also runs the unanswered-CQ negative case.
An additional real native CLI lifecycle used a mock provider, froze T once,
received an exact 20-item pool, rejected 19 trivial candidates, retained R,
and published the same CLOSED-derived sign route with every CQ answered.
Its artifacts and receipt are in `runs/xi-round17/cli-e2e/`; execution output is
`cli-e2e.txt`, and the replay script is `cli_e2e.py`.

## Verification

Before implementation, three new pool tests failed and both defeasible engine
cases passed (`runs/xi-round17/red.txt`). After implementation all five new cases
passed (`pool.txt`). The broader focused run passed 108 tests and found one old
pilot fixture expecting ten identical formulas to survive deduplication; that
fixture now supplies distinct placeholders. The repaired pilot/new-pool run
passed all 23 cases (`focused-repair.txt`). All ten focused production-wire controls detected their injected defects and
restored green (`focused-controls.txt` and `focused-controls/`).

Full offline pytest passed **1,158 passed, four skipped / 1,162 collected** in
845.46 seconds. All 220 pinned source hashes matched afterward. The full
500-control runner started only after pytest completed. **All 500 controls
passed**: each mutation returned pytest exit 1 and every restored test returned
exit 0. All 220 source hashes matched afterward, including 48 mutable source
files. `git diff --check` passed. Evidence: `pytest-full.txt`, `pytest-verification.json`,
`source-before.json`, `gates.txt`, `controls-full.txt`, `full-control-results.json`,
`controls/`, `source-after-controls.json` and `final-verification.json` under
`runs/xi-round17/`.

## Finding placement

| Finding affecting review or use | Placement |
| --- | --- |
| Concrete main-claim guidance and entailment witnesses; existing gates unchanged | Proposer contract and correction evidence |
| Pool size, retention, duplicates, short responses and advisory vocabulary | Pool and disposition behavior |
| Native CLOSED-derived defeasible route, CQ negative case and semantic limits | Native defeasible proof and limits |
| Executed regressions, complete gates and local revision | Verification |

4 findings, 4 placed.

DONE xi round17 head=fffb7c3cd1526d048ffda302fc877559eba5a2a5 tests=1158/1162 negctl=pass defeasible_e2e=yes
