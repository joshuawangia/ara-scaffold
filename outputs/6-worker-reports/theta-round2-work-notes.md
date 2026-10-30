# Theta round 2 — working record

Base 188784e6e11309bf7658bdce31dd70f933aea5d8, same clean branch/worktree.
Round-1 report is preserved as theta-context-fix-round1.md.

## Intent correction and causal plan
The first fix conflated range-level resume with completed-paper reuse, and selected
corpus refusal even though the intended result is a usable pilot corpus under the
USD125 aggregate extraction cap. Preserve paid successful papers; explicitly
exclude failed papers from evidence rather than refusing every usable source.
Apply the same distinction downstream: a disclosed failed record is permitted
metadata but never a construction/citation input.

At 188784e, extract catches every terminal exception and raises immediately;
assemble can carry status records, but construction selects any nonempty items
without checking status. literature_provenance reconstructs every outcome in history,
and import_provenance deduplicates only an entire event-prefix receipt. These are
the seams to extend for a final corpus with failures and transitive paper reuse.
The base checkout has pinned extraction sidecars and full-prefix receipt imports;
it does not contain a separate B2 import module. Extend those existing primitives
with origin checkpoint validation and event receipt deduplication.

Implement a disclosed failure threshold (default 3, stop only after exceeding it),
continue model/paper-local failures, and retain immediate refusal for global budget
exhaustion or unknown accounting. Explicit failure receipts pin the original log
prefix. Completed successful papers can be imported into a fresh run through
--resume-from, with source identity checked and all original costs retained once.
No partial-range replay. Re-extraction gets a fresh paper attempt allowance but
cannot reset inherited global charges. Scope final outcomes to the current batch
so historical failures remain inspectable without duplicating published papers.

Proof: placeholder native extraction/pilot, thresholds and global caps, completed
paper resume from both completed and stopped runs, tampered/missing origins,
transitive/overlapping imports and exact inherited charges; new mutation controls;
full pytest and complete control runner sequentially. No paid calls or delegation.


## Round-2 implementation checkpoint

Native implementation is present, pending full-suite/control completion and commit.
The first test-first run recorded 12 failures / 2 passes; implementation brought
that original recovery suite green. Expanded recovery coverage is 27 tests,
including actual CLI extract/resume/pilot, threshold boundaries, changed PDF/input,
run-scoped failures, inherited costs, missing/pinned/truncated origins and transitive
reuse. All new focused mutation controls have now failed under mutation and passed
after restoration; the complete runner remains the final gate.

Two focused controls initially survived because the tests had weak assertions:
one tested only a shallow import (another validation path still caught tampering),
and one set a cap too low even without inherited costs. The tests now use a deeper
origin chain and a cap that admits the next request only if prior costs are wrongly
lost. Both controls now detect their faults. No surviving mutation is accepted.

Original paid evidence hashes were rechecked and match theta-source-evidence.json.
Full pytest is running sequentially ahead of the complete control runner. Next:
inspect results, repair any regression with targeted checks, finish full controls,
update this report with final results and locally commit the owned files.
