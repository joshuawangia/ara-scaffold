# Paper-owned target admission

`admit-proposal` starts a proposal paper from an authenticated existing frozen T
when no search route exists. It never formalizes a claim, admits H, creates an
inference, runs search, or freezes T again. Its one-node OPEN graph is an explicit
paper-owned target envelope, with a null formula and no supports/edges. It cannot
be classified as CLOSED-derived. The immutable proposal packet supplies separately
cited frozen evidence and the disclosed missing premise/nonclosure point.

The command takes `--source-run`, a separate `--run-dir`, and `--packet`. The
request has exactly `candidate_id`, `source_freeze_hash`, `proposal`, and
`grounding_files`. `proposal` has the ordinary proposal packet fields except
`route_id`; admission assigns a content-bound target ID. `grounding_files` is a
list of `{path, sha256}` bindings for retained handoff evidence. Ordinary proposal
origin labels, source citation checks, three-sample union audit, meaning checks,
and repair limits remain unchanged. A prose target is never represented by an
arbitrary formula or an implication between source atoms.

`--plan-only` verifies the original hash chain/anchor, frozen artifacts, source
pages, request bindings, provider output screen, and capacity without creating a
run or making model/counter calls. Identity/credential screening still uses the
selected providers. A positive plan is not review approval or model validation.
Actual admission rechecks those inputs, then copies the exact original prefix
through freeze, with its imported accounting. The original is unchanged. Native
`select --run-dir RUN --route ID` uses the logged proposal packet; it rechecks
capacity before any append, provider call, or automatic export. Keep one run per
candidate and resume its existing draft and repair history.

Capacity planning reserves three times the frozen import size plus one GB for
new writer receipts, separately retaining 6 GB on root and 2 GB for a destination
under `/dev/shm` (6 GB elsewhere). Subsequent selection reserves two current log
sizes plus one GB. These are disclosed projections, not a guarantee about other
processes or unlimited output. A shared-memory run is volatile: retain its evidence
until copied to durable storage with sufficient headroom; do not claim a durable
paper/export from its existence alone. No cleanup or compression is performed.

The pending queue state is `OPEN-proposal-pending`, `route_id: null`, and
`dispatch_hold: awaiting_native_grounding_admission`. It must not be sent to the
ordinary candidate runner. After reviewed admission, `promote-proposal --entry
ENTRY --run-dir RUN` verifies the admitted candidate, source, grounding hash,
graph and packet, then prints an `OPEN-proposal` row with `reuse_admitted_run:
true`. It neither edits the shared queue nor dispatches. The orchestrator consumes
this row using the existing run, never copying it again; a legacy supervisor that
does not support reuse must remain held. The queue's held state is not evidence
of a search result. Admission and promotion receipts are the native authorization
for the new proposal consumer path.

If repeated neighboring source items push writer context over its existing size
limit, `source_context` stores identical items once in `context_items`, with each
anchor's ordered `paper_context.item_refs` indexing that table. This encoding is
lossless: source rows, bibliography, omitted-item counts and per-anchor item order
are unchanged. The same size limit still refuses a context that cannot fit; no
required evidence is truncated and no source claim becomes a route premise.
