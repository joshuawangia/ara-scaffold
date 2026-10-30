# Xi Round 22 — cross-paper admission and bridge guidance

Base `a272ebe7df8615a7a9a4a0215068f963171a5c3d`, branch `feat/run-report`,
checkout `/home/dev/ara-work/xi`. Offline only, no paid calls, push or delegation.
Evidence directory: `runs/xi-round22/`. Final revision and full gates follow.

## Resulting policy

CLOSED-derived needs at least two verified paper source IDs among reachable,
formula-distinct frozen leaf/CQ supports. Otherwise an eligible one-paper route
is CLOSED-single-paper and excluded from default selection. Missing paper identity
is CLOSED-contribution-unresolved. The identity comes from the verified provenance
sidecar, not from citation/page text or inferred authors. Existing stance, novelty,
minimality and licensing checks remain. Engine CLOSED is preserved. The report
contains the classification and paper_support receipt, including IDs and missing
identity disclosure. Explicit human --route selection remains available and logged.

Legacy smoke inputs lack verified paper metadata and therefore wait for explicit
selection before writing. The CLI replay still exercises writing/export after
that explicit selection; it does not claim cross-paper qualification.

## Target and cut guidance

The target pool requests 30 candidates and keeps up to ten, preserving the existing
correction budget, gates, stable order and survivor retention. Native target, map
and cut calls receive candidate_bridges and commitment_papers. Each bridge is a
pair or triple of endorsed frozen commitments from at least two source IDs, with
a common catalogue symbol or an exact case-folded definition term. Common function
words are removed. Symbol connections take priority; candidates and IDs are
deterministic. At most 30 pairs and 30 triples are returned, with 10,000 examined
combinations per size and explicit truncation. A triple needs a common connection
across all three members. Missing catalogue/provenance yields no invented bridges.

For a new atom, cut guidance prefers cross-paper premises. Returned T IDs cite
the bridge through named premise slots. The proposal_bridge event records matched
bridge IDs and slot/commitment/paper mappings, excluding open/scoped hypotheses.
The provider sees the full logged/cache-bound context. CommitmentSet, frozen
catalogue, provenance and proposal codecs remain unchanged.

## Evidence and limits

Six initial new regressions failed before implementation (`red.txt`). The first
focused run passed 6/6. The affected policy run passed 145 tests (`affected.txt`),
and CLI/schema verification passed 97 tests (`cli-final.txt`), including the new
bounds/stance regression. Canned fixtures were regenerated offline using
`rekey.py`; no provider/network calls were used.

Native placeholder end-to-end verification closes a sign route, accepts the
two-paper version for selection and reports the one-paper version as
CLOSED-single-paper. Missing identity and an unreachable third-paper support
cannot upgrade the classification. Guidance tests verify deterministic pairs and
triples, no disconnected candidates, stance filtering, bounded output and a
logged slot-to-paper bridge receipt.

Lexical links are candidate leads, not proof of equivalent topics, relevance or
semantic scheme suitability. Counting source IDs is not proof of independent
evidence, necessity of every cited support, or bibliographic deduplication.
This offline change does not demonstrate three useful cross-paper philosophical
routes or satisfy the live go/no-go criteria. A new authorized pilot and
substantive review are still needed to establish that outcome.

## Finding placement

5 findings, 5 placed: single-paper exclusion and missing-identity behavior in
Resulting policy; changed legacy smoke selection in Resulting policy; bounded
lexical bridge limits in Target and cut guidance; semantic independence and
live-pilot limitations in Evidence and limits.

## Stored pilot-3 check

Offline inspection of the existing pilot-3 frozen artifacts found 169 commitments,
151 catalogue symbols and 22 papers with eligible endorsed commitments. Bridge
generation returned its bounded 30 pairs and 30 triples in approximately 0.145
seconds, with truncation disclosed. This is candidate availability, not semantic
review of those connections. Both stored CLOSED graphs now classify as
CLOSED-single-paper; the four OPEN graphs remain OPEN. No new search or model
call was made. All 11 inspected source artifact hashes match.
Receipts: `real-corpus-receipt.json`, `real-corpus-context.json`, `real-corpus.txt`;
harness: `census.py`. Zero network or paid calls.

## Focused mutation verification

All **23/23** focused controls passed (mutation red, restored green), with all
five touched production hashes restored. This includes the ten new paper/bridge
controls and affected existing pool, contribution and search controls. Evidence:
`focused-controls.txt`, `focused-control-results.json`. `git diff --check` passed.

## First full-suite repair

The first full run passed 1,260 tests, skipped four, and exposed two writer
exhaustion variants that still depended on legacy smoke auto-selection. Controls
did not start. Both now select the existing route explicitly with --route route:p,
so the writer-validation, accounting, retry and cache assertions still execute
unchanged. No production behavior changed in this repair. All 229 pinned files
were unchanged during the failed run; receipts are retained in `first-gates/`.

The repaired writer suite passed **14/14** tests (`writer-fixed.txt`). Both owning
controls passed mutation/restoration, with the source hash restored
(`writer-controls.txt`, `writer-control-results.json`). Final full gates are
repeating sequentially on this corrected test tree.

Final full pytest passed **1,262 tests, four skipped / 1,266 collected**, in
999.57 seconds (`pytest-full.txt`). All 229 pinned source hashes matched after
pytest. The full 552-control run started only after that pass.

## Final sequential verification

**1,262 passed, four skipped / 1,266 collected; 552/552 controls passed.**
The full control runner completed after full pytest on the same pinned tree.
Every mutation was red, every restoration green, and all **229 pinned file
hashes** match, including all **52 mutated production files**. `git diff --check`
passed. Receipts: `final-verification.json`, `source-before.json`,
`source-after-controls.json`, `full-control-results.json`, `pytest-full.txt`,
`controls-full.txt`, and individual red/green logs in `controls/`.
Zero paid calls; no push.

Committed locally as **`25e076a01bc68dc0d717ab0e9949c7674f3bfc07`** on `feat/run-report`.
The tree is clean and all 229 committed file contents match the exact snapshot
used for final sequential verification (AGENTS.md resolves to committed
CLAUDE.md). Receipt: `commit-verification.json`.

**5 findings, 5 placed**, with their sections listed above. The offline evidence
establishes the implemented gate and available lexical bridge candidates; a
new live pilot and substantive review are still needed to establish the
operator's three-route success criterion.
