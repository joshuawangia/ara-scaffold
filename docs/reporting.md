# Offline reports

[Documentation index](README.md) · [Project README](../README.md)

```sh
uv run ara report --run-dir runs/run-p --run-dir runs/run-q --out runs/report-p
```

`report` reads receipts and artifacts without creating providers, running the
engine, appending HUMAN events, or modifying source runs. Output must be a fresh,
empty directory separate from every input run. Keep real output under ignored
`runs/`. It writes a bounded `report.html` overview (inline styles, no scripts), a
Markdown link index, and a version-2 `data.json` manifest. Copy the entire output
directory to retain its sibling evidence files. Local Graphviz `dot` optionally
produces linked SVG files; absence or render failure is disclosed and DOT
retained.

The HTML stays below 15 decimal MB, with a 12 MB working budget and at most 64 KB
per section (reduced for larger run counts). Oversized views explicitly link to
their full files. Run/paper rows, accounting and tree summaries stay in the
overview. Trees show counts, depth, outcome and the first three levels, capped at
60 preview nodes; full traces/routes and DOT are in `trees/`. No size limit
truncates evidence.

`data.json` lists every run's section files, paper files and trees. Full paper
item listings/history are split by run and paper. Full artifacts are copied
separately with trust metadata; full accounting timelines are linked JSON.
`events/index.json` lists each original event once by SHA-256 of its canonical
event body, with original and imported-by run references and every
sequence/chain-hash occurrence. Per-run `*-events.json` files retain chain
envelopes and `event_ref` links; replacing each reference with the linked JSON
event reconstructs the original verified records. Compact event projections
likewise reference the shared bodies. Chain hashes stay separate from event
identity hashes because import changes chain positions.

The eight sections cover identity/configuration/lineage, extraction and
exclusions, construction/freeze receipts, search, selectable routes and support
citations, accounting, HUMAN actions, and original failure/limit receipts. The
linked receipt files retain full prompts and responses; large extraction runs can
still produce large evidence files without enlarging the HTML view. JSON strings
and paper text are displayed as escaped text, never active HTML. Model-written
route summaries appear only when already logged. Reporting never calls a model to
fill a missing field.

The reader verifies every hash chain and any available tail checkpoint before
writing output. Missing checkpoints or inaccessible origin logs are explicit
verification gaps; modified chains, mismatched anchors or imports refuse. Imported
receipt provenance is verified transitively where available. An unanchored chain
cannot prove absence of suffix truncation, and hash chains cannot protect against
rewriting both the log and its checkpoint. Artifacts are separately labelled as
unauthenticated unless matched to logged evidence; no artifact overrides the log.

Combined accounting deduplicates identical original receipts across input runs.
Per-run local and inherited totals remain separate. Measured usage and unknown
actual usage charged at reservation are separate in every grouping and timeline.
Only `accounting="actual"` is measured; missing/future markers retain their cost
and tokens in an unclassified bucket with a gap. The explicitly named
budget-accounted column combines all recorded charges. Unresolved dispatches and
unattributed paper calls remain visible. Extraction history is not silently
substituted for an unattempted paper in the latest batch.

Old logs provide final proof graphs, not a faithful search-state tree. Reports
retain those graphs and unassigned engine decisions while declaring the missing
ancestry/prune context. Legacy version-1 traces remain readable. Native version-2
searches write append-only `search-traces/*.jsonl` sidecars containing state/node
deltas, interned formula/text/proposal references, and one full graph per
completed route. One final chained receipt seals each search with path, line count
and SHA-256. The report verifies the seal before interpreting content, then checks
versions, references, ancestry, root inventories and terminal coverage. A missing,
unsealed, unsupported or inconsistent trace is partial; a mismatched seal refuses
the report. The overview shows bounded tree previews. Full state ancestry, proof
graphs and original ENGINE decisions remain in linked files; the overview never
claims that its preview contains every state.

Copy `search-traces/` with `events.jsonl` and its checkpoint when relocating runs.
Imported seals can use their recorded origin path when the sidecar is not local;
an unavailable sidecar is an explicit gap. Available immediate origin prefixes and
copied receipts are checked even when a more distant ancestor is missing. Warnings
identify only the unavailable path and scope. Current non-trace route artifacts
and analysis persistence remain unchanged; the once-per-route rule applies to
tracing. Run code revisions, source-page mappings, route summaries and audit
associations are not guessed when absent.

Completed trace graphs retain every node and edge, with proposition and proposal
payloads referenced through the same interned definitions as state deltas. The
report resolves those references only after authentication and preserves the raw
receipts alongside the expanded terminal graphs. This keeps long repeated premise
text from multiplying across alternative routes; it does not omit any route.

## Route classification and contribution receipts

The overview and linked route records show [contribution classifications](search.md#route-classification-and-selection).
Only `CLOSED-derived` is `selectable_by_default`. The report computes this policy
from the recorded graph and available frozen commitments, without a provider or
new engine search. Bounded local solver checks can run during classification;
this does not add new inference licenses or source-run events.

Each route retains the event's `target`, `polarity` and `graph`. `classification`
remains a top-level report field for consumers; the full solver/support receipt
is nested under `contribution`. For a route from negation search, `polarity` can
be `negation` while `contribution.polarity` is `target`, meaning the solver tested
that route's root. These fields describe different scopes and are never merged.
See `ara/runtime/report.py:286` and `ara/runtime/report_render.py:301`.

Legacy records keep their original engine status and evidence. Missing support
or unresolved contribution checks remain disclosed; a contribution label does
not establish novelty, minimal support sets or independent source papers.


Round 16 route contribution receipts also include provenance availability, hash,
stance crossings and scoped source roles. `CLOSED-stance-crossing` identifies a
historical closed route using reported/attacked content as a global premise or CQ
evidence. Source stance is loaded from the validated frozen receipt; missing
legacy metadata remains unavailable. The construction detail retains the full
provenance receipt, including exact source text. See [source stance](search.md#source-stance-and-content-definitions).

The shared writer/auditor outline carries source stance, attribution and scope
role for referenced commitments when provenance is verified. Explicit selection
does not erase these roles. The prompts require reported/attacked material to
remain reporting or conditional hypotheses, including in dependent conclusions;
the model audit treats endorsement promotion as an added inference. This is a
model-audited writing obligation, not a deterministic semantic guarantee.

Round 18 discloses `CLOSED-structural` for otherwise contributing closures without
a reachable qualifying bank inference. Contribution receipts identify the
qualifying substantive node IDs and bank IDs; pure connective packaging is not
selectable by default. See [search policy](search.md#route-classification-and-selection).

Round 19 receipts additionally contain semantic novelty checks against the entire
frozen T. The qualifying inference list excludes unused conditional proofs and
steps whose conclusions do not establish an essential new proposition of the
root. Classical consequences remain engine-closed but are not novel derived
routes for default selection. Classifier novelty/fidelity judgments and proposed
definitions are logged during admission, not recomputed by report rendering.
Step receipts in `inference_novelty_checks` retain conclusion checks and unused
scope reasons. If no step qualifies and a step's novelty is unknown, the route
is contribution-unresolved rather than silently reported as structural.

Round 20 restricts qualifying steps to non-logical bank schemes (`kind=defeasible`).
A scheme's own conclusion must contain an essential new proposition of the target.
Deductive rules, including conditional proof and hypothetical syllogism, may wrap
a qualifying scheme but never supply one. Engine CLOSED still records valid
deductions such as Q from {P, P -> Q}; those routes remain structural for novelty.

Round 21 treats broad lexical attribution matches as advisory classifier evidence.
Only exact leading name + argues/holds/believes that report frames retain a
lexical hard veto, including on historical route display. Native target admission
requires the logged own-thesis classifier verdict. Offline fake judgments verify
the wire and policy, not real classifier accuracy.


Round 22 requires two verified paper IDs for CLOSED-derived. CLOSED-single-paper
is disclosed and not offered by default. Missing paper provenance is unresolved.
Each route contribution contains paper_support with IDs, counts, per-commitment
source mapping and missing identities; paper counts do not establish semantic
independence. See [cross-paper contribution](search.md#cross-paper-contribution-and-bridges).

Round 27 supersedes the whole-T deductive novelty exclusion above. Verified
per-paper closure allows cross-paper deductions as CLOSED-derived when no single
paper entails the root, an essential assertion remains, and source-support and
license checks pass. Receipts contain per_paper_novelty, support_union_entailment
and synthesis_inference_licenses; single-paper padding remains unselectable.
Native defeasible licensing, supported CQs and legacy-unavailable disclosure remain. See the current
[search policy](search.md#route-classification-and-selection).
