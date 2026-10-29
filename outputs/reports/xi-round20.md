# Xi Round 20 — non-logical scheme conclusions

Base `44cced12f901ce01722d639d1ce5010ab905ddc7`, branch `feat/run-report`,
checkout `/home/dev/ara-work/xi`. Offline only; no paid calls, push or delegation.

## R1 fixed

Only bank entries with kind=defeasible can supply a qualifying inference. Every
deductive bank rule is structural for novelty, including conditional proof and
hypothetical syllogism. A reachable non-logical scheme's own conclusion must
contain an essential new proposition of the target; whole-freeze novelty,
stance, distinct support, licensing and CQ requirements remain. Logic rules may
wrap a qualifying scheme but cannot supply it. The assumption-reachability
heuristic was removed. Proposer guidance uses the same bank-kind distinction.

Native regressions cover Q by sign, the unadorned R -> Q conditional, the matching
conjunction core, the padded conjunction detour, the syllogism wrapper, and
genuine R. Only genuine R qualifies in that matrix. The existing native
new-scheme-conclusion-under-conditional test remains derived. Licensed
{P, P -> Q} proves Q with engine CLOSED and novelty-structural classification.
Policy coverage enumerates every deductive entry and rejects unknown schemes.

## R5 fixed

Explicit and automatic definitions now use one frozen-name collision policy.
Both reject P(a) where P is a frozen atom; both accept fresh F(a). The compiler's
separate namespaces and all frozen/CommitmentSet codecs remain unchanged.

## Limits and prerequisites

Fake-provider reachability does not prove scheme fitness, real originality,
faithful content or model judgment accuracy. The Round 19 definitional-alias
false-positive dependency remains. A live run still requires current effective
Codex preflight; no new real-T fork or live run was requested or executed.

## Verification

Before production edits, the padded and syllogism regressions failed as
CLOSED-derived; 8 native checks passed (`red.txt`). The automatic binding was
confirmed separately to survive proposal incorrectly (`binding-red.txt`: 1
failed, 3 passed). Strengthened bank-kind/guidance coverage failed 9 checks
(`kinds-red.txt`: 9 failed, 6 passed). After the fix, focused tests passed
66/66 (`focused.txt`). Full sequential gates and exact committed hashes follow.

## Finding placement

4 findings, 4 placed: route blocker in R1 fixed; binding inconsistency in R5
fixed; residual model/semantic accuracy and stale live preflight in Limits
and prerequisites. Evidence root: `runs/xi-round20/`.

Focused production-wire controls passed **32/32** mutation/restoration pairs,
including both native wrapper adversaries and automatic binding collision.
All three touched source hashes were restored (`focused-controls.txt`,
`focused-control-results.json`). Offline canned/native recordings were
regenerated using `runs/xi-round19/rekey.py` (`rekey.txt`).

## Final gates — 2026-10-28

Full pytest: **1245 passed, 4 skipped / 1249 collected**, exit 0,
920.57 seconds. Full controls ran sequentially after pytest: **535/535 expected
mutation failures and 535/535 restored passes**, exit 0. All **226 pinned files**
match their pre-test hashes, including **51 files** temporarily mutated by
controls. `git diff --check` passed.

Command: `ARA_LIVE_TEST=0 UV_OFFLINE=1 TMPDIR=/dev/shm/xi-round20 uv run
--offline --locked python runs/xi-round20/verify.py`. Receipts:
`runs/xi-round20/final-verification.json`, `pytest-full.txt`,
`full-control-results.json`, `controls-full.txt`, `controls/`,
`source-before.json`, and `source-after-controls.json`.

## Committed revision

Local head `cb9d2c0ff2b40e511258a97eb99eb94926aa37f7` on `feat/run-report`; clean working tree.
All 226 committed file contents match the tested snapshot, with tracked
symlinks checked through their canonical targets. Proof:
`runs/xi-round20/commit-verification.json`. No push.
**4 findings, 4 placed**, as mapped above.
