# Accounting and run records

[Documentation index](README.md) · [Project README](../README.md)

## Artifacts and logging

Each run writes `commitments.json`, `routes/*.json` and matching readable trees,
`events.jsonl` with `events.anchor`, an unverified draft and, after audit and
verification, `draft.json` and `export/{essay.txt,methodology.md}`. No essay is
exported before verification and the second audit pass. OPEN frontiers remain
explicit in route artifacts; essays present the argument conditionally on its
stated premises without narrating software metadata. Budget STOP returns exit 2,
preserves partial graphs, writes `partial.json` and exports methodology. A
provider failure without usage charges a labelled conservative reservation,
reports unknown actual spend and refuses paid continuation by default. Supported
commands can explicitly count finalized unknown receipts at their reservation;
this does not resolve an unreceipted dispatch or establish measured spend.
Post-dispatch serialization, parsing or completion-log failures likewise stop with
an incomplete record and reservation-based cap checks. Methodology explicitly
marks incomplete totals and outstanding dispatches. A persistent storage failure
may prevent new appends; preserve the log/checkpoint and reconcile before starting
another run.

The append-only JSONL records full prompts/responses, model id/version, token and
server-tool usage, cost, time, cache hits, rejections, engine decisions and every
HUMAN command/input verbatim. Methodology derives from this log alone. Preserve
its checkpoint to detect tail truncation during resume; rewriting both files can
forge the local chain. Interrupted appends refuse startup.

Essay export removes run metadata and node markers and replaces literal `--redact`
identifiers. It does not discover identities in prose. Methodology intentionally
retains the complete record and is not anonymised. Web evidence and model audits
are bounded assessments, not exhaustive originality or source truth proofs.
Sentence inventory and id validation cannot prove that a valid-id label is
semantically correct; the simple deterministic splitter also splits abbreviations
at punctuation followed by whitespace. Formal entailment does not establish
faithful text translation or CQ truth. Search and forward results are bounded by
configuration; independent route counts cover discovered routes. Scheme forms cite
Walton, Reed & Macagno (2008); unverified page/chapter locators remain explicitly
unknown.

Measured responses and usage are persisted before fallible validation/counting. A
later failure prevents caching/freezing but retains the known bill and response.
Methodology exposes `measured_usage`, `unknown_usage_reservations` and
`budget_accounted` for aggregate, local, inherited and extraction scopes. Legacy
numeric totals remain budget-accounted for compatibility; unknown usage is not a
measured invoice, and sibling-run campaign reservations require separate
accounting.

## Subscription estimates and budgets

There is no free CLI token counter. The versioned calibration table uses per-kind
p99 measured API tokens/UTF-8-byte ratios with 5% margin, plus runtime overhead
measured from retained CLI receipts. Source/event hashes and numeric pairs are in
`ara/runtime/claude_code_calibration.json`; no source text is copied into that
table. Unknown kinds use the largest calibrated factor. This is an estimate, not a
hard tokenizer bound. The aggregate reservation still covers two turns and one
output replay. Initial context and cumulative token caps remain enforced. After
each uncached response with valid measured usage, an observation compares like
quantities: a reported one-turn call's input against its initial estimate;
otherwise aggregate input (including cache) against its aggregate reservation.
Fixed runtime overhead is a separate measured constant. One-turn canaries can
raise that constant without inflating the text factor. Aggregate overshoots adjust
the text factor only after removing the reserved output replay and fixed overhead.
Stage providers share run state; reopening restores matching-version local
observations. Imported observations and the old aggregate/initial comparisons
never train a new run. Factors and overhead can only increase. In-flight
reservations are not retroactively enlarged. Actual usage remains the accounting
authority. Missing usage consumes the reservation and stays incomplete.

CLI reported cost equivalents appear under `subscription_usage`; they are not
measured API USD. Dollar caps do not govern subscription calls. Subscription token
caps apply to local run usage, including pending reservations and unknown-usage
reservations; imported history remains separately reported and included in total
accounting. API token admission retains its historical-inclusive policy. Original
imported API charges remain visible in methodology, and cached subscription
receipts do not add new usage. Each call records requested/served model, CLI
version, tokens, wall time, exit status and session id; unsafe error text is
suppressed.
