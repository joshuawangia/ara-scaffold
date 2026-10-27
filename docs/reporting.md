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
