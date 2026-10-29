# Xi Round 16 — asserted content and source stance

Working checkout: `/home/dev/ara-work/xi`, branch `feat/run-report`.
Started from main `5b512de`, then fast-forwarded sigma's helper-only commit
`1ff0f7fafd5f7c633be61525fee33be4a2c3c404`. Round 16 completed at
`c187128180aa71229c812a8900da66523886a3ef`. The worktree is clean and its committed tree matches all 218
verified source hashes, resolving committed symlinks.
No paid calls, push or new worker delegation. Existing sigma coordination used
the authorized worker context and the agreed contract in
`/home/dev/ara-work/reports/sigma-xi-stance-contract.md`.

## Assertion meaning and cache identity

The isolated classifier receives target text and a structural rendering of the
formula using verified content definitions. It does not receive source text,
author attribution or stance prose. Those distinguish the source's role, not
whether the target itself reports a position. Exact T/catalogue/provenance hashes
bind the classifier cache identity. Missing legacy content definitions are null
and labelled unavailable, never manufactured by stripping attribution.

The deterministic target-text attribution lexicon remains shared with sigma's
construction validator. Existing phi2 attribution probes still reject even when
the fake classifier says own_thesis. The new own-voice placeholder synthesis is
accepted while its provenance retains an attributed source sentence. Solver
validity, singleton-entailment, both-polarity target checking and two-distinct-
support route requirements remain unchanged.

## Stance enforcement and disclosure

The native engine keeps full frozen source context for proposal/formalization,
with an exact eligible subset for global premises, CQ evidence, closure,
opposition and forward analysis. With verified provenance this subset contains
only source-endorsed commitments. Reported/attacked content remains available
under existing bank-licensed assumption scopes. Attacked content never becomes
an asserted negation. A source endorsement is not independent truth validation.

Global misuse emits STANCE_CROSSING with node and commitment identity. Historical
closed routes using restricted evidence receive CLOSED-stance-crossing, retain
the full graph and receipt, and are excluded from default selection. Explicit
selection retains the existing disclosed-route behavior. The shared writer/auditor outline also retains source roles so explicit selection
does not discard them; its prompts require qualification of reported/attacked
content and dependent conclusions. This remains a model-audited writing obligation,
not a deterministic semantic guarantee. Reports/export retain
validated provenance and route crossings/scoped source roles; the Round 15
nested contribution/polarity contract remains intact.

Legacy runs without provenance retain legacy search behavior and explicitly say
stance unavailable; absence does not mean endorsed. A present malformed sidecar,
a missing recorded sidecar, or a receipt mismatch refuses. Freeze forks copy
exact sidecar bytes and verify the prefix receipt. Search resume validates before
provider creation, preserves completed open restricted routes, and refuses a
closed historical stance crossing before analysis reuse.

## Evidence and integration boundary

New tests first failed in all five initial cases before implementation
(`runs/xi-round16/red.txt`). Focused verification then passed 131 engine/search,
fork/resume and report tests, followed by 39 classifier/calls/CLI/native-stance
checks. Exact logs are in `runs/xi-round16/targeted2.txt` and `targeted3.txt`.
An additional writer-outline regression failed before its fix (`outline-red.txt`),
then all 25 focused stance/outline/native CLI cases passed (`outline-targeted.txt`).
The first full-suite attempt was stopped during pytest to close this downstream
boundary; it is retained as `pytest-interrupted-before-outline.txt` and is not a
full-suite receipt. The final pinned full-gate run restarts from the revised tree.

The final driver pins all tracked files plus the new regression file, runs full
pytest, checks hashes, then runs all mutation controls sequentially and verifies
exact restoration. Evidence is retained under `/home/dev/ara-work/xi/runs/xi-round16/`.
Full offline pytest passed: **1,142 passed, four skipped / 1,146 collected** in
793.00 seconds. All 218 pinned source hashes matched afterward. All **488 mutation controls passed**, sequentially after pytest. Each mutation
returned pytest exit 1, and every restored test returned exit 0. All 218 pinned
source hashes matched afterward, including the runner’s 47 mutable source files.
The final committed tree matches these hashes, and `git diff --check` passed.
Evidence: `pytest-full.txt`, `pytest-verification.json`, `controls-full.txt`,
`full-control-results.json`, `controls/`, `source-before.json`,
`source-after-controls.json`, `final-verification.json`, `commit-verification.json`
and `gates.txt`.

This branch includes sigma's validated helper-only commit. Sigma owns rich
construction definition output and native provenance persistence in its separate
worktree; this receipt does not claim its still-pending final integration suite.
Sigma also adds construction.commitment_provenance to export methodology; it is
additive to this branch’s route policy. Missing bibliographic author records stay
source_authors=[], while attributed_to remains exact; search does not infer authors.
All new search proofs use placeholder data and fake providers. No live classifier,
new real-corpus synthesis, or rerun of the twenty-attempt pilot is claimed.
Faithfulness of model content definitions and source stance labels remains a
semantic limitation; the deterministic engine enforces the supplied verified
roles rather than establishing them from source prose.

## Finding placement

| Finding affecting review or use | Placement |
| --- | --- |
| Asserted-content classifier, preserved attribution/solver gates, cache binding | Assertion meaning and cache identity |
| Global stance enforcement, scoped use, historical route disclosure and explicit selection | Stance enforcement and disclosure |
| Legacy unavailable semantics, fail-closed recorded metadata, fork/resume behavior | Stance enforcement and disclosure |
| Helper-only integration boundary, executed proof and semantic/live limitations | Evidence and integration boundary |

4 findings, 4 placed.

DONE xi round16 head=c187128180aa71229c812a8900da66523886a3ef tests=1142/1146 negctl=pass classifier=text_and_content stance_aware=yes
