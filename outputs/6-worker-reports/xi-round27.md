# Xi Round 27 — per-paper novelty and forward synthesis

Base `80a344892d9acd1933bf47c1b6fd8fd986bbee5b`, branch `feat/run-report`, checkout `/home/dev/ara-work/xi`. Offline only; no push. Final local commit `5557e9a7da15413071b25932413d2f9fac30f797`; full sequential gates complete and checkout clean.

## Behavior and native proof

Verified provenance groups all endorsed commitments by paper. Targets are rejected if a single paper entails them, if they are tautologies, or if they merely package frozen assertions or already-known atomic consequences. Solver uncertainty stays unresolved. Union entailment is allowed. Legacy metadata remains unavailable and uses the conservative legacy gate.

The native placeholder regression carries P from paper a and P -> Q from paper b through proposal, engine search, default selection and report generation: Q is CLOSED-derived. The same premises from one paper yield CLOSED-single-paper. A fitting sign step followed by modus ponens also qualifies, retaining native licensing and supported CQs. Unreachable and unknown bank steps cannot supply the qualifying inference. Re-expressed single-paper padding regressions retain rejection through conjunction detours, conditional proof and hypothetical syllogism. Quantified per-paper closure is covered.

Own-thesis, frozen definition restatement, fidelity, source stance, distinct-formula/paper matching and gap-support checks remain independent gates. Engine CLOSED status and immutable frozen formats are unchanged.

## Forward proposal and generation binding

A bounded native forward pass produces ranked leads with support IDs, paper IDs, bank IDs and depth. Up to 30 enter proposal alongside gap candidates; the model must render them faithfully and ordinary target gates still apply. Current-generation recorded forward results are also mined, under their own node-cap scan bound, only when their freeze matches the current commitments. The proposal cache includes recorded results, preventing reuse across a new analysis boundary. Full lead and truncation receipts remain logged. These are candidate leads, not accepted theses or already searched routes.

## Real freeze census and limits

Command: `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked python tools/offline_forward_synthesis.py --source /home/dev/ara-scaffold/runs/codex-fork-5 --out runs/xi-round27/fork5-final`.

The final depth-2, 500-consequence pass used 169 commitments from 22 endorsed papers and found **0 qualifying candidates**. It reached the cap, so this is not an exhaustive absence claim. An earlier six-candidate result in `fork5/` preceded the compound-premise packaging repair; all six are rejected by the final novelty check as `no_essential_new_proposition`. Only `fork5-final/summary.json` is the final census. Source artifact SHA-256 hashes and byte comparisons establish that commitments, catalogue and provenance were unchanged. The command explicitly refuses socket connections; no model or paid call ran.

Sigma's separate symbol-alignment head `bdeaeb8444113e5c0d6d62e5ac1b494a8f0b5fee` is not merged here. No semantic originality, useful literature synthesis, live provider acceptance, exhaustive forward coverage or paid-pilot success is claimed. Alignment can change a future census; no such increase is asserted from this result.

## Verification and review coverage

The recovered affected suite passed 145/145 in 397.22 seconds. The additional compound-consequence padding assertion passed in 0.47 seconds. Earlier expected failures and repairs are retained under `runs/xi-round27/`, including `red.txt`, `boundary-red.txt`, `mixed-red.txt` and their green receipts. All 17 new controls passed with intended assertion failures and green restorations. Full pytest then exposed stale finite request keys; the two canned inventories were rekeyed against the previous prompts with every response payload preserved, and 25 CLI/fixture consumers passed. The next full run completed with 1326 passed, 4 skipped and three failures: a named-position request fixture and two report-label expectations. Their owning files passed all 19 tests after updating only the expected request field and per-paper labels; polarity, nested receipt, triviality witness and read-only report assertions remain.

Focused older policy controls exposed three mutations masked by the new per-paper gate. The uncertainty control now turns a solver UNKNOWN into a counterexample instead of mutating a redundant label. The two native padding controls now disable the per-paper closure gate; independent legacy non-logical bank-kind controls remain. No control was waived or deleted. Final full pytest passed **1329 tests, 4 skipped / 1333 collected**, exit 0 in **1730.04 seconds**. The pinned source hashes matched afterward. The complete **617-control** runner started only after pytest finished and passed, exit 0 in **4497.78 seconds**. All 617 mutations exited 1; all 617 restored tests exited 0. All **245 pinned/restored/committed file hashes**, including the instruction symlink and **59 mutation-target files**, match the exact tested tree. The 17 new and three retargeted controls were also checked for intended owning-test failures, without syntax or collection failures. The final commit is clean and local; no push or paid calls occurred.

Implementation/diff/consumer inspection and inline simplification checks completed. No test was removed or weakened as simplification. No separate lint/typecheck is configured in pyproject.toml. Code review: skipped (ce-code-review unavailable) — the required independent review dispatch conflicts with the operator restriction on spawning new worker/hidden-agent contexts; no independent review is claimed. The failed attempt is recorded in `runs/xi-round27/review-attempt.json`; manual source and requirements inspection remains separate from that unavailable review.

Exact receipts under `/home/dev/ara-work/xi/runs/xi-round27/`:

- `final-receipt.json`: final head/tree, counts, chronology, committed-tree hashes and limits.
- `pytest-full.txt`, `controls-full.txt`, `gates.json`: successful sequential gate transcripts and times.
- `control-evidence/`: all 1234 mutation/restoration outputs and complete results registry; `final-control-failures.json` records the 20 new/retargeted owning-test failures.
- `source-before.json`, `source-after.json`, `control-manifest.json`: exact tested/restored source pin and mutation inventory.
- `fork5-final/summary.json`, `offline-final.txt`: final zero-candidate bounded census with immutable source hashes.
- `pre-fixture-*`, `pre-expectations-*`, `fixtures-repaired.txt`, `expectations-repaired.txt`, `policy-control-evidence/`, `retargeted-control-evidence/`: retained failures, compatibility repairs, old masked mutations and their replacements.

## Finding placement

1. Per-paper policy, retained guards and native placeholder outcome: Behavior and native proof.
2. Forward leads, exact-freeze/generation binding and bounded scan: Forward proposal and generation binding.
3. Final zero census, superseded six-candidate result, source preservation and cap: Real freeze census and limits.
4. Sigma integration boundary and unproved semantic/live outcomes: Real freeze census and limits.
5. Executed verification, committed-tree identity and unavailable independent review: Verification and review coverage.

**5 findings, 5 placed.**

DONE xi round27 head=5557e9a7da15413071b25932413d2f9fac30f797 tests=1329/1333 negctl=pass per_paper_novelty=yes forward_candidates=0
