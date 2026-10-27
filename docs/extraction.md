# PDF extraction

[Documentation index](README.md) · [Project README](../README.md)

Place manifest-listed PDFs in `literature/fulltext/`. See [local OCR](ocr.md) for
the default intake requirements. This text-only estimate needs no OCR weights or
provider credential:

```sh
uv run ara extract --profile extraction --manifest literature/manifest.yaml --fulltext-dir literature/fulltext --provider mock --ocr off --estimate-only --run-dir runs/extraction-estimate
```

With credentials configured, extract the chosen sources through the normal logged
model boundary. `p` below is a placeholder to replace with a manifest id; omit
`--paper-id` only when ready to extract the entire manifest.

```sh
uv run ara extract --profile extraction --manifest literature/manifest.yaml --fulltext-dir literature/fulltext --paper-id p --run-dir runs/extraction
uv run ara run --profile pilot --topic 'P' --literature runs/extraction/literature.extracted.txt --run-dir runs/pilot-extracted
```

The explicit extraction profile sets both enclosing and extraction cost caps to
USD30 and the token cap to 6000000. Ordinary defaults remain USD10/200000 tokens.
Preflight prints `planned batch exceeds enclosing caps` if its pages × 1500
input-token estimate plus prompt overhead and output allowances exceed those
limits. Estimates exclude retries and server fallbacks; actual requests reserve
and account separately. Use an isolated cache for the planned extraction run.

For a full-run plan, use the separate `extraction-full` profile. It selects Opus
in `stages.extraction.model` and disables fallbacks. Accepted range unions
disclose inference coverage rather than imposing a link quota. Range corrections
use the configured limit (0 through 3), within shared paper-wide count and cost
limits. Reconciliation is one best-effort pass with no correction queue; a counted
context overflow is logged and skipped while accepted ranges survive. Its
enclosing token/cost caps and extraction cost cap are `null`: the operator must
set all three before generation. The same profile is accepted by `ara run
--profile extraction-full` so its 32k catalogue and construction correction policy
also reach construction. Use it with the original extracted literature and
operator-set caps. The ordinary `extraction` profile above retains its defaults.

```sh
uv run ara plan-extraction --profile extraction-full --manifest literature/manifest.yaml --fulltext-dir literature/fulltext --paper-id p --ocr off --token-counter local --run-dir runs/extraction-plan
```

The example disables OCR; omit `--ocr off` after installing its dependencies and
weights to plan with the default OCR intake. The planner reads PDFs and writes
numeric ranges, capacity admissions and cost scenarios to `extraction-plan.json`;
it cannot generate. `local` labels its UTF-8-bytes/4 estimate. `provider` uses the
provider's token-count endpoint; verify that endpoint remains free before using
it. Counts include the runtime's conservative schema overhead. Full-profile
initial ranges also reserve a scenario of 1200 output tokens/readable page,
informed by the bounded extraction sample; this reduces predictable output
exhaustion, but does not guarantee coverage. Execution uses the same range
planner. Output cost and construction-window counts remain estimates:
reconciliation, corrections, actual graphs, chosen closures and symbol reuse
cannot be known before extraction. `fits` concerns initial readable ranges only.
Inspect unread/glyph-warning counts separately.

Rich v2 extractions preserve page-linked premises, intermediate conclusions,
conclusions, paper-stated or reconstructed inference links, distinctions,
qualifications and reported/attacked views, with explicit attribution. There is no
four-item or character cap. Each call allows 32000 output tokens (including
thinking); actual output and coverage must be inspected. Context overflow or
output exhaustion subdivides readable physical page ranges.

Each accepted range is
saved immutably. Publication retains their union. When review is needed, one
counted reconciliation request can add evidence. It has no correction queue or
follow-up context fetch. Admission or review failures leave accepted ranges
available and disclose the failure. Unresolved references retain stable
range/page-linked obligation IDs; artifacts retain both obligation and resolution
ledgers, including open gaps. Additional requested context is recorded as
unfulfilled. Empty ranges need model-authored reasons.

A range of at least eight readable pages with at most one item per ten pages
(minimum one) receives one split re-extraction. Existing accepted evidence stays;
remaining thinness, failed refinements and missing readable pages are disclosed.
Historical refinement receipts prevent repeating the attempt. An indivisible page
that cannot fit can remain unextracted; this is disclosed, never treated as
covered. See `ara/runtime/reconciliation.py:8` and `ara/runtime/calls.py:867`.

Full graphs remain in `<id>.extraction.json`, range artifacts and log-backed v2
literature. Item-level citations such as `p:pdf:1-2#p:r1-2:p` disambiguate
separate items on the same pages. Folio labels are not physical page indices.

## Text intake and provenance

The pypdf text reader does not perform OCR. The following diagnostics describe
text-only intake (`--ocr off`) or pages still flagged after [local OCR](ocr.md).
Blank pages are recorded and preserve numbering while readable pages proceed.
Image/form pages with fewer than 200 text characters, and painted pages with no
text, are flagged and excluded from claim support. Their papers are explicitly
`partial`, with affected page numbers in outcomes, logs and methodology. An
entirely visual paper is partial with no items and no model call. Private-use
glyphs flag encoding warnings: their text is retained and the paper remains
partial. Text-only intake performs no glyph substitution. These heuristics cannot
prove text completeness or correct reading order. Missing/unreadable PDFs default
to `record only, not extracted`; `--missing refuse` stops for missing/unreadable
PDFs and diagnosed incomplete text coverage, including wholly visual, mixed
readable/visual and encoding-warning pages. It is not a semantic completeness
check. Later range/review failures can retain accepted evidence with disclosed
gaps; paper and run failures follow the policy below. Record-only entries supply
no commitments, and an all-record-only collection cannot build T. Partial entries
supply only their readable-page items.

Import the **original extraction artifact directly**. Keep its text, provenance
sidecar and original source log available at the recorded path. The loader
verifies and imports its receipts with SYSTEM/MODEL labels. Cross-run cached
re-extraction without original receipts is explicitly marked incomplete and
refused at import; zero new spend is not complete production accounting. Same-log
replay with its original receipt remains usable. Do not strip the provenance
header to bypass a refusal. Legacy v1 artifacts are refused and must be
regenerated as rich v2.

Methodology separates local and inherited usage/cost/human time and gives imported
receipts stable ids. Re-importing the same receipt within a log is idempotent;
aggregate reports should deduplicate inherited receipt ids. Imported API charges
count against API admission. Subscription token admission uses local usage;
[accounting](accounting.md) describes the separate scopes. PDF bytes partition the
cache even when text is identical. Generated artifacts and PDFs remain gitignored.
Structural page/citation checks do not establish semantic support or accurate
attribution.

## Failures and reuse

Extraction continues after terminal paper-local failures. Each failed source is
published with an empty evidence list, reason, and pinned failure receipt; the
artifact is labelled `complete_with_disclosed_failures`. Pilot import accepts it,
construction excludes failed sources, and methodology lists failures and the
policy. `extraction_max_failed_papers` defaults to 8, including `extraction-full`.
Eight paper-local failures may complete; the ninth stops further extraction. The
stopped batch publishes accepted evidence and failed/not-attempted rosters before
returning the failure. Global budget, unknown-spend and operational failures stop
further paid work; they do not erase earlier accepted evidence. See
`config.yaml:88`, `ara/runtime/extraction.py:419` and
`ara/runtime/extraction.py:447`.

Initial extraction and graph review report
missing context as `new_gaps`. Only a response to a supplied obligation can
request pages or evidence; the current single-pass reconciliation records such a
request without fetching it.

Reuse completed papers in a fresh destination with repeatable `--resume-from`:

```sh
uv run ara extract --config config.yaml --profile extraction-full --manifest literature/manifest.yaml --fulltext-dir literature/fulltext --resume-from runs/extraction-old --run-dir runs/extraction-new
```

Set the full profile's operator caps before generation. Resume checks source
identity and original log checkpoints, then reuses matching completed papers from
completed or stopped runs. Failed, missing or changed papers are extracted again.
Every original charge, including failed attempts, counts toward the new API
extraction run's aggregate caps; overlapping and transitive origins are charged
once. Retried papers get fresh paper-local allowances. Preserve all original logs
and checkpoints: missing or changed origins refuse, including during later pilot
import. Unknown or interrupted spend must be reconciled before reuse.

Verified accepted range receipts can be salvaged from failed or interrupted
papers. Accepted completed snapshots, including disclosed thin or partial results,
are reused without reconstructing their IDs or automatically repeating extraction.
The original run directory remains immutable; an occupied destination refuses
before provider construction. Cross-run cache entries without original receipts
remain invalid provenance.

Resume eligibility also binds the completed outcome's versioned
`acceptance_identity`: inference policy, effective extraction
model/effort/thinking/ fallback settings, provider, prompt hash and schema hash.
Changed or missing identities require the native extraction/validation path again;
old receipts and costs are still imported. Dollar/token caps, paper/recovery
allowances and unrelated stage settings can change without invalidating compatible
completed papers. `--missing refuse` also rejects reused partial sources before
publication. Ancestor successes remain reusable if an intermediate run stops
before reaching those papers. Multiple compatible completed snapshots publish an
explicit union. Identical original ID/body pairs can share an output item;
distinct IDs are never merged by text similarity. Conflicting IDs and their
dependent reference context are snapshot-qualified, with all links mapped within
the originating snapshot. The artifact carries per-item provenance and original
snapshot identities and checkpoints. Gaps and resolutions remain snapshot-scoped;
quarantine is recomputed over the union. A second resume rebuilds from verified
original snapshots rather than recursively unioning derived copies. The acceptance
identity remains v6; `completed-snapshot-union-v1` versions this publication
representation.

## Extraction and provenance API

| API | Contract |
| --- | --- |
| `extraction.extraction_acceptance_identity(config, root)` | Returns the active acceptance contract using the effective, profile-applied configuration. Bump `EXTRACTION_ACCEPTANCE_VERSION` when validation, normalization, mode-schema rules or graph interpretation change. |
| `extraction.resume_papers(log, papers, sources, config, root)` | Verifies all supplied origins before importing; indexes matching successful outcomes across retained ancestry. Config and contract root are required. Returns entries for `extract(..., reused=...)`, which rechecks compatibility. |
| `provenance.read_checkpoint(origin)` | Reads the pinned log prefix, validates its chain and recursive imports, and returns original events. Missing or altered origins refuse. |
| `provenance.verify_imports(events)` | Validates origin-pinned imported blocks against original prefixes, including deduplication. Does not replace verification of the containing log chain. A native import's `receipt_id` hashes the full original prefix, not just the copied block. |
| `extraction.import_provenance(log, events, origin)` | Copies verified original receipts with deduplication. Pass the pin for native/transitive imports. Original timestamps, configuration, model receipts and charges remain unchanged. |
| `provenance.extraction_outcomes(events)` | Selects only the latest batch for final literature/current failure disclosure. |
| `provenance.historical_extraction_outcomes(events)` | Returns all retained outcome candidates. It is not a verifier or compatibility check; resume validates source, acceptance identity and merged-graph receipt before indexing successes. |
| `extraction.literature_provenance(path, text)` | Verifies an existing literature artifact against pinned imports and current-batch reconstruction. It does not relabel historical extraction as accepted under today's policy. |

`ModelCalls.response_schema(kind, inputs)` remains the active mode-specific schema
entrypoint used by rendering, counting and validation. The acceptance identity
belongs to completed outcomes; retained historical attempts, including rejected
responses, keep their original contracts and must not be rewritten as today's
prompt/schema. Existing historical literature can still be verified and imported;
unknown acceptance identities disqualify automatic completed-paper reuse only.

## Corrections

Extraction corrections are ID-based patches. Unchanged items may be repeated, and
a second patch sees the cumulative candidate, including new items from a rejected
first patch. Omitted items remain unless `discard_items` explicitly removes a
rejected candidate item with its ID and reason. Unknown IDs, accepted history, and
simultaneous replacement/discard of one ID cannot use that exception. All
remaining references must resolve (`ara/runtime/calls.py:152`).
`extraction_targeted_corrections` accepts 0, 1, 2 or 3; every dispatch remains
subject to the paper and run allowances. Feedback includes physical paper bounds
and the readable pages of the current window. Blank attribution, invalid
references, unsupported inference structure, and substantive empty dispositions
alongside items remain errors. Content-free normalization removes empty/null
optional `empty_reason`, converts the wire's null empty inventory to `[]`, and
fills structural defaults. Page-order and repeated-ID normalization retain their
receipts. Original responses remain unchanged; none of these operations
establishes semantic support.

## Offline response replay

Historical-response replay uses the same native response boundary.

```sh
uv run python tools/replay_extraction.py --log runs/previous/events.jsonl \
  --output runs/replay --corrections 2
```

Inputs must be gitignored and output must be a fresh directory under `runs/`. The
harness forbids sockets, deduplicates copied receipts, and reports each response
as accepted, normalized, needing a new correction, requiring native subdivision,
or terminal. It tests each recorded candidate/patch against its original source
window; it does not generate corrections, replay the complete obligation
traversal, prove live admission, or certify completed-paper fidelity. Historical
spend is not a new charge; replay receipts are offline artifacts.

The provider projection expands range-envelope alternatives to typed, closed
objects; the SDK transformation contract is checked offline as well as ordinary
JSON Schema validity. These checks do not prove live service acceptance. A
provider exception with unknown usage retains the admission reservation and blocks
a resumed paid run until its accounting is reconciled.

## Extraction schema preflight

Before a paid extraction, compile all extraction response grammars with a
placeholder-only native gate:

```sh
uv run ara schema-preflight --profile extraction-full --config config.yaml --run-dir runs/schema-P
```

The gate allows at most USD1 including imported gate history. A repeated gate uses
a new directory and `--resume-from runs/schema-P`; preserve all prior attempts.
Both `schema-preflight` and `extract` accept the explicit `--unknown-usage-policy
count-at-reservation` option. This counts unknown usage at its full reservation
upper bound, preserves the original receipts, and never claims measured usage. It
does not reconcile an interrupted dispatch without a receipt. Schema compilation
does not establish source extraction quality.

## Grounding and offline salvage

Current v6 publication screens each item's text against its cited readable pages.
The screen normalizes NFKC/case, dehyphenates line endings and excludes versioned
function words. It requires at least half the distinct content tokens and three
matches (all tokens when fewer than three exist). Template text, one/two-character
text, text identical to attribution and nonword text are quarantined separately.
Quarantine propagates through dependent references. Original IDs and bodies stay
in the retained inventory; quarantined items cannot enter T or close a gap.
Lexical overlap does not prove entailment, accurate attribution or source
fidelity.

Historical artifacts without current grounding must be republished before use as
evidence. Offline salvage verifies original receipts, retains accepted evidence
and rechecks grounding without creating a generation-capable provider:

```sh
uv run ara extract --profile extraction --manifest literature/manifest.yaml --fulltext-dir literature/fulltext --ocr off --salvage-only --resume-from runs/extraction-old --run-dir runs/extraction-salvage
```

Match the original source intake and effective acceptance settings; `--ocr off` is
appropriate only for text-only inputs. Use `--exclude-paper p=REASON` to record an
explicit exclusion with no evidence. Keep source logs, anchors and sidecars. See
`ara/runtime/grounding.py:56`, `ara/runtime/grounding.py:95` and the [Mu
decisions](../DECISIONS.md#mu-round-2-grounded-evidence-and-retained-quarantine).
