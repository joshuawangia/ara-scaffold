# Xi Round 14 — phi2 B1 and B2

Checkout: `/home/dev/ara-work/xi`, branch `feat/run-report`, base
`9f07ba0a50df2802d56302134f85e4a896a23dd6`. Completed at `e7e12b42e3a76dfbbb6a71dbcfee2eac9f171b1d`. No paid calls, network calls, push, or delegation.

## B1: solver contribution

Preflight checks both target polarities against no premises and each frozen
commitment separately. Each entailment query has a 1,000 ms bound. A bounded
8,192-entry cache uses alpha-invariant formula hashes and timeout; bound and
free variables cannot collide. Valid targets, singly entailed targets, and
unresolved solver outcomes are excluded after at most one shared proposal
correction. Compact rejection feedback is separate from the full logged
solver receipts. The former structural `direct_instance` helper was removed;
`contribution_check` is the replacement preflight boundary.

Publication and selection traverse reachable graph support, including CQ
references, excluding assumptions, and deduplicating repeated or
alpha-equivalent formulas. A derived closure needs a licensed inference, at
least two distinct supports, and no singly sufficient support. Other results
are disclosed and excluded from default selection. Explicit operator route
selection and bank licensing retain their existing behavior.

The native regressions reproduce duplicated conjunctions and tautology
padding. A further native conjunction proof has two reachable frozen
supports but only one necessary support: it remains bank-licensed and CLOSED,
is classified `CLOSED-single-support`, and is not offered by default. Its
standalone receipt is `runs/xi-round14/two-support-demo.json`.

## B2: own-thesis classification

Broader deterministic attitude/report phrases reject phi2's text variants.
Frozen catalogue definitions also identify top-level attribution predicates.
Each target receives a separate, schema-validated `classify_target` call on
the same provider, with target/vocabulary inputs and no proposal history or
rationale. Only `own_thesis` passes; `attributed_report` and `unclear` are logged
and excluded. Identical repeated calls retain normal logged cache receipts.
Native attributed closures remain licensed but are not default-selectable.

## Compatibility and operational consequences

Frozen catalogue and commitment codecs are unchanged; missing legacy
catalogues still mean unavailable metadata. Native publication, selection,
and reports use frozen T. Legacy graph-only rendering can recover leaf
formulas, but missing CQ evidence stays unresolved.

The new response schema expands the Codex schema preflight from 15 to 16
cases. Existing 15-case receipts are stale and must be refreshed before a
live Codex run. No live acceptance of the new schema was attempted.

## Offline pilot proof and limits

The fake-provider pilot-3 fork passed. It inherited exactly 6,813 records /
331,834,295 bytes, rejected ten copied targets after one correction, and logged
20 own-thesis classifications and 20 contribution receipts. There were twelve
fake provider dispatches: two proposals and ten classifications; ten repeated
classifications were cache replays. Four original source artifacts retained
their SHA-256 hashes. No network or paid provider was used.
The real-data demo uses `fork_from_freeze`, `ModelCalls`, and native `search_all`
with an explicit fake-only profile: local caps above inherited historical
usage and a byte/4 test estimator. It does not exercise live CLI preflight,
production allowances, or real tokenizer accounting. Placeholder CLI lifecycle
coverage is separate in pytest.

Evidence: `runs/xi-round14/fork-demo.py`, `fork-demo.json`, `fork-suffix.jsonl`,
and `fork-suffix.anchor`; the full scratch fork is
`/dev/shm/xi-round14-pilot-fork`. The saved suffix can be appended to the first
6,813 source records and anchors for reconstruction. The source remains
`/home/dev/ara-scaffold/runs/codex-pilot-3`.

This proves rejection behavior on real frozen inputs with fake answers. It
does not demonstrate new real-corpus synthesis, faithful formalization,
semantic originality, general attribution accuracy, independence across
papers, or minimality among larger support subsets. Solver timeout/unknown
results fail closed. The one-second bound is per check, not a whole-target
latency guarantee.

## Verification and disposition

The initial focused red run had 20 failures and three passes. The first full
run found three outdated fake-provider inventories and a resume-test hook
that needed the frozen-commitments argument: 1,101 passed, four failed, four
skipped. Those fixtures were updated without weakening their owning
assertions. The four repairs plus all contribution regressions passed:
34 tests in `runs/xi-round14/repair.txt`. All 22 focused mutation controls
produced red regressions and restored green; their source hashes were restored
(`focused-controls-results.json` and `focused-control-restoration.json`).

Final full pytest passed: **1,105 passed, four skipped / 1,109 collected** in
788.80 seconds (`runs/xi-round14/pytest-full.txt`). All 204 pinned source hashes
matched afterward (`source-before.json`, `pytest-verification.json`). The four
skips are the live known-case test, real-provider test, and two optional local
OCR tests. All **476 mutation controls passed**, sequentially after pytest: every mutation
returned pytest exit 1 and every restored test returned exit 0. All 204 pinned
source hashes matched after the runner, including its 47 mutable source files.
Evidence: `controls-full.txt`, `full-control-results.json`, `controls/`,
`source-after-controls.json`, and `final-verification.json` under
`runs/xi-round14/`. `git diff --check` passed. Committed locally as `e7e12b42e3a76dfbbb6a71dbcfee2eac9f171b1d`. The worktree is clean; the committed tree
matches all 204 verified source hashes (resolving committed symlinks). Nothing was pushed.

| Finding affecting use or review | Placement |
| --- | --- |
| Phi2 B1, alpha-equivalence, and route/default-selection policy | B1: solver contribution |
| Phi2 B2, isolated classifier, deterministic/catalogue screens | B2: own-thesis classification |
| Frozen-contract compatibility and stale Codex schema receipts | Compatibility and operational consequences |
| Offline-only pilot scope and remaining semantic/live limits | Offline pilot proof and limits |
| Test repair, full gates, restoration, and local commit state | Verification and disposition |

5 findings, 5 placed.

DONE xi round14 head=e7e12b42e3a76dfbbb6a71dbcfee2eac9f171b1d tests=1105/1109 negctl=pass fixed=phi2-B1,phi2-B2
