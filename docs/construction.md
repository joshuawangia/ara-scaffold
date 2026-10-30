# Construction and frozen commitments

[Documentation index](README.md) · [Project README](../README.md)

Generated literature uses one construction lifecycle, one freeze. Source IDs are
sorted, content hashes pinned, and batches packed using provider-counted requests,
not a fixed paper count. Defaults allow 70000 batch input tokens, 64000 output and
a 16000-token shared-symbol reserve. Plans and their inputs partition caches.
Evidence windows can divide one large source. Each window asks the model for
relevant roots and grouped omission reasons. Closure uses the full immutable
graph, including evidence outside that window. Already accepted IDs are reused
exactly; accounted zero-root windows skip formalization. Code computes
`directional-prerequisites-v1`: selected conclusions include their supporting
links and premises recursively, plus applicable qualifications and distinctions.
Shared premises or qualifiers do not select other consequences. Roots, added IDs,
graph hash and rule version are logged. A second model call formalizes exactly
that fixed inventory. Every omitted item has a model-authored reason; code removes
required prerequisites from preliminary omission groups. Exact source text survives in immutable evidence and commitment provenance,
while citations remain unchanged in T; identical or contradictory formulas are not
deduplicated. Shared symbol definitions and model-produced semantic reuse
decisions are logged and validated; code derives syntactic occurrence bindings and
copies provenance and citations. Code never invents equivalences. Faithful
formalisation and semantic alignment remain model judgments requiring source
inspection.

The working T has a 100000-token counted downstream-input limit. Each batch
receives remaining measured global capacity, including actual wrappers. Before
formalization, counted copied evidence in a minimal formula envelope and the
existing catalogue are checked. The full profile reserves 256 catalogue
tokens/selected item for planning and allows a 32000-token catalogue. This
reservation is configurable, not a prediction of symbol semantics; actual accepted
T and catalogue are rechecked. When a full closure cannot fit, the current policy
may cut at a complete prerequisite depth and disclose omitted support, as
described below. Oversized mandatory bundles may contribute nothing; actual
request admission can still refuse. Full rich records remain available for
inspection; current search uses only the selected working T. Every request,
including downstream requests, retries and cache replay, is counted with its full
prompt/schema before admission. Larger goals/banks/feedback can still produce an
explicit STOP. Searching beyond working T requires a new construction with revised
topic/audience/budget, not mutation after freeze. The 53-paper offline fixture
exercises rich graphs, multiple batches, native search, cache replay and one
freeze; its deterministic transport counter is a test proxy, not a real tokenizer
forecast.

## Capacity planning

Construction uses a global working/copy/catalogue allocation and 20% headroom.
Selection sees each root's full closure size and a conservative UTF-8 payload
token bound. If necessary, code cuts at a complete prerequisite depth while
retaining qualifiers and inference endpoints. Frontier commitments carry explicit `omitted_support_ids` in provenance; methodology
discloses that routes using these premises are conditional. An oversized mandatory
bundle or an irrelevant window may contribute nothing. Actual output and complete
requests are still counted and may refuse; no model quality guarantee is implied.

Before generation, use `ara plan-construction --literature <path> --topic <text>
--audience '' --profile pilot --config <path> --run-dir <empty-path>
--token-counter provider`. This shares the native allocation and free provider
counter with generation disabled. `--token-counter local` needs no network but
reports byte/4 estimates, not provider measurements. Neither command selects roots
or predicts the actual frozen T. The full source and every cut remain inspectable.

## Resume a stopped construction

For a stopped, unfrozen run ending in a receipted provider request rejection:

```sh
uv run ara resume-construction --run-dir runs/previous --unknown-usage-policy count-at-reservation
```

This uses the stored configuration, source, topic and audience. It verifies batch
artifacts and the original counted plan, restores accepted work without model
replay, skips the terminally refused window, and continues through the existing
single freeze and search to route selection. Earlier charges and unknown
reservations remain in the same ledger. The policy flag acknowledges unknown usage
counted at its reservation; it does not convert it to measured usage. Concurrent
resumes, an already-frozen run, corrupt/missing receipts, a changed plan, or a
dispatch without a terminal receipt refuse. This command can make new paid calls
after verification; it is not an offline diagnostic command.

To verify a resume using free token counts only, write its receipts into a
separate empty directory:

```sh
uv run ara resume-construction --run-dir runs/previous --unknown-usage-policy count-at-reservation --plan-only --output-dir runs/resume-plan
```

The preview verifies the same plan and accepted artifacts, restores the
provisional commitments in its own log, and stops after counting the next eligible
selection request, before generation. It has zero spending caps and a provider
that cannot generate; it does not append to the source run or freeze commitments.
The report records the next window, restored count, and any refused counter
requests. An account credit rejection still stops even though the count endpoint
is free; restore account access before trying again.

## Construction spread and stage configuration

`construction_window_cap_multiplier` defaults to 2. Each window can add at most
its initial planning share times that multiplier, rounded down: share 3 gives cap
6. The cap stays fixed even when earlier windows contribute nothing. Closures are
depth-cut within it, with mandatory context preserved and omitted support
disclosed. There is no second redistribution pass. A zero share gives a zero cap;
the plan and skipped-window receipts disclose it. Actual contributions depend on
relevance and global token limits, so the capacity targets are not a promise of
equal coverage.

Rebuild with `ara run` and a new empty `--run-dir`. Do not use
`resume-construction` for a capped rebuild of an older plan. Fresh runs retain
extraction provenance but never restore the previous construction's accepted
batches. The cap and construction dispatch settings are part of the plan identity.

Each construction stage can independently select a registered provider and model:

```yaml
stages:
  select_t_roots: {provider: anthropic, model: claude-opus-5}
  build_t_batch: {provider: anthropic, model: claude-opus-5}
  construction_correction: {provider: anthropic, model: claude-opus-5}
```

Empty overrides inherit the run configuration. Corrections inherit their original
stage before applying `construction_correction`; profiles preserve unrelated stage
entries. Receipts and methodology show the actual requested/served stage models
and providers. Model pricing and accounting must be configured for the selected
backend. Both `claude_code` and `codex_cli` are registered in
`ara.runtime.cli.make_provider` (`ara/runtime/cli.py:130`). Their isolation,
credentials and schema gates are described in [providers](providers.md). Native
`ara run --literature ...` caches extraction-lineage verification receipts under
`cache_dir/lineage-verification`. Cold startup fully verifies the artifact,
recursive logs and anchors. Later starts reuse the receipt only when the verifier
identity and every recorded file hash match; changed inputs trigger full
verification and invalid lineage refuses before model setup. Every run logs the
receipt and reuse decision without changing inherited model receipts or charges.
Deleting this cache safely forces full verification. Receipts use local hash
chains with separate anchors, not signed authentication. The optimization does not
skip construction restoration or any downstream work.

If global construction capacity is smaller than the window count, available
one-slot allocations go to the earliest windows in plan order. Per-window shares
and caps, unfunded windows, and the allocation rule are disclosed in the plan.
Actual closures, symbols and global limits are still checked; an allocation is not
a guarantee that a window contributes.

## Operator gap anchors and larger construction windows

A fresh rich-source construction can prepend extra, counted retrieval windows
with `construction_gap_anchors`. Each entry has a nonempty `gap_id`, `source_id`,
and `root_ids` and/or `page_ranges`. Root IDs are exact IDs from the grounded
extracted graph, not invented premises or target formulas. Page ranges are
inclusive, one-based physical PDF pages; matching extracted items are candidates
for ordinary relevance selection. Page matching does not read new PDFs or certify
complete extraction. Missing sources, unknown/quarantined roots, empty page hits,
invalid ranges and duplicate `(gap_id, source_id)` entries refuse before planning
counts. Combine multiple ranges/roots for the same pair in one entry.

```yaml
construction_gap_anchors:
  - gap_id: P
    source_id: p
    root_ids: ["p:r1-2:f"]
    page_ranges: [[1, 2]]
```

Explicit roots must be selected in their anchor window; omitting them enters the
normal bounded correction/refusal path. Page-only candidates may be omitted with
reasons. The window can still contribute nothing if its mandatory closure does
not fit or formalization fails. Anchors cannot change source text, stance,
provenance, qualifiers, formalization gates or solver policy. Closure still reads
the full immutable graph. Previously formalized IDs and symbols are reused exactly,
and the run freezes once. Ordinary corpus windows remain after the extra windows.
Overlapping omissions are reconciled once per evidence ID in the final inventory;
every window's original reasons remain logged.

The optional `construction_context_limits` mapping derives any of the three
existing token budgets from the effective **run-level** `model_context_token_bound`.
Values must be finite fractions strictly between zero and one; unspecified keys
retain their absolute configured values. The bound is normalized from the
configured Codex window before calculating `floor(bound * fraction)`.

```yaml
provider: codex_cli
model: gpt-6-luna
model_context_window: 600000
construction_context_limits:
  build_t_batch_input_tokens: 0.60
  working_t_token_budget: 0.65
  working_t_symbol_token_budget: 0.15
construction_window_cap_multiplier: 8
```

With the default target output allowance and margin, the example uses run bound
567232 and budgets 340339/368700/85084 respectively. The batch input allowance is
also limited by the run bound minus construction output and catalogue reserves.
Actual complete requests, including output allowances and effective stage windows,
are still admitted separately; a smaller stage override can refuse a request.
The existing finite window-cap multiplier is independently configurable. Larger
budgets or caps do not guarantee that every closure fits, every source contributes,
or the resulting formulas faithfully express the sources.

Both options default to disabled. They apply to rich extracted literature only.
Resolved anchors, physical ranges, matched evidence, effective budgets and operator
origin enter the counted plan and logs. `construction_gap_anchor_window` and
`operator_construction_limits` appear in methodology/report construction data.
`plan-construction --token-counter local` exercises the same planner without
generation; it is an estimate, not a provider admission or source-quality verdict.

Use a fresh empty run directory when changing anchors or limits. Disabled options
preserve existing plan inputs. Enabled or changed options partition plan/request
cache identities, including downstream catalogue context. Keeping the old cache
directory permits only exact-input hits; it does **not** import previously accepted
construction outcomes into a different plan. Reusing extraction is separate. Add
new PDFs to validated extraction before anchoring them. Construction/alignment
resume continues to require the recorded plan and source identities.

## Opt-in partial acceptance and split retry

For a fresh construction lifecycle, three independent run-level boolean flags default off (stage overrides refuse):

```yaml
construction_partial_acceptance: true
construction_split_retry: true
construction_precise_attribution: true
```

Partial acceptance runs only after ordinary validation/structure corrections fail.
Whole-candidate complexity guards run before and after formula decoding; filtering
never turns an over-budget response into an admitted one. Recovery projects the
last complete, accounted candidate onto validated commitments,
checks the normal schema, content definitions, source pages/stance/provenance,
formula signatures and bindings, and recounts cumulative capacities. Formulas
must be individually satisfiable and the endorsed union consistent; reported and
attacked formulas do not become global premises. Candidates are admitted in stable
ID order; conflicts preserve earlier accepted rows. This is not a relevance ranking
or a promise to find the largest consistent subset. Unknown solver results refuse.

Dropped dependencies propagate to dependants until stable, including inference
endpoints and qualifiers. Existing disclosed support cuts remain disclosed; partial
recovery never invents a new cut to retain an unsupported dependant. Surviving
inferences must pass the structure gate. Symbol evidence lists are projected onto
survivors without inventing bindings. The entire surviving batch is revalidated
before acceptance. No formulas, source text or stance are repaired by this process.
The terminal accepted receipt has `status: partial` and a
`construction_partial_acceptance` receipt records the candidate hash, retained IDs,
dropped IDs/reasons and discarded auxiliary inventories. It is not a skipped window.

Split retry declares two dormant children for each divisible primary window in the
counted plan. A failed/oversized primary activates its children once, in stable
halves of the original evidence inventory. Each child uses normal root selection,
full-graph closure, shared prior commitments/catalogue, formalization and admission.
Children never split recursively. Global exhaustion does not activate retries.
An indivisible item, large mandatory closure or still-invalid child can still be
omitted. Partial success is terminal and does not activate its dormant children.

The allocation reserves capacity for primary windows; children share that parent's
allocation index and still face recounted global limits. The plan and receipts
include `budget_index` and `retry_parent`. All entries have ordered outcomes:
`status: split` on a retried parent, `inactive_retry` on unused children, or the normal
accepted/partial/skipped outcome. This retains native stopped-construction and
alignment-resume verification. Count primary coverage separately from retry entries;
three plan entries do not mean three distinct original windows. Split decisions and
partial results also appear in export methodology.

The precise attribution flag allows ordinary uses of “holds”, “hold”, “states” and
“maintains” while continuing to reject explicit report frames such as `b argues
that P`, `b holds that P`, and `According to b, P`. Known-author exact unframing
remains disclosed as before; an attributed frame itself never becomes a content
definition. This optional construction screen does not change the search target
attribution policy and is not a semantic completeness check.

Opt-in source rows carry `definition_screen: attribution-frames-v1`, hash-bound in
`commitment-provenance-v3`. The existing validator/loader accepts v1/v2 unchanged
and validates v3 using its recorded screen, including after alignment or fork.
Old readers refuse v3; use the updated reader for these runs. The outer
commitments and frozen-catalogue formats are unchanged. All enabled options enter
the construction plan/cache identity; no changed-input cache replay is licensed.

Partial recovery adds no provider calls beyond existing corrections. Split retry
adds at most two attempts per divisible failed primary: with correction limit C,
each attempt makes at most `2 * (1 + C) + 1` generation calls (selection and
formalization with corrections, plus one structure correction). Thus at most
`2 * (2 * (1 + C) + 1)` extra calls per failed primary, or 14 at default C=2.
Counts, local validation and bounded consistency checks add CPU time. Wall time
and tokens remain response-dependent; neither larger bounds nor recovery guarantees
coverage. Use new lifecycle settings only after reviewing the counted plan.

## Structure and frozen vocabulary

Rich construction preserves selected inference nodes as content conditionals with source stance in provenance
using shared endpoint formulas. Predicates/constants are required where the source
supports relational structure. The model decides meaning, symbol reuse, and
whether qualifications belong in conditions; code never invents equivalence. Each
batch logs non-atomic fraction, symbol reuse rate and exact conjunct endpoint
connections. These syntactic measurements are not a translation-fidelity score. A
deficient batch receives one structure correction. If it remains atomic despite
inference evidence, construction accepts it with `flat_after_one_correction` in
the batch receipt and methodology. Other schema, provenance, signature and budget
checks still apply. Such flatness can prevent useful entailments and is not a
successful structure-gate verdict.

`commitments.json` keeps the legacy CommitmentSet format. Rich freezes also write
`frozen-t.json`, an immutable envelope containing the commitments and a hash-bound
`symbol_catalogue`. Its entries preserve model-authored definitions and evidence
IDs. The exact canonical SHA256 contract is documented in DECISIONS S8 and checked
by `ara.runtime.frozen_catalogue.validate_frozen_artifact`. Missing metadata means
the legacy catalogue is `unavailable_legacy`; corrupt present metadata refuses.
Search loads and validates the catalogue, includes its hashes in model/cache
inputs, and jointly formalizes slots against frozen bindings. See
`ara/runtime/search_alignment.py:20` and `ara/runtime/calls.py:990`.

## Reuse after freeze

`fork-from-freeze` is available at base `f89cd37`. It verifies and copies the
recorded prefix through one freeze, then proposes new targets without rebuilding
T. Follow [frozen-fork operation](search.md#reuse-a-verified-freeze) for source,
destination, accounting and provider requirements. A fresh `ara run` still
constructs and freezes its own T. `run --from-frozen` is not a supported alias.
Manual artifact copying does not replace the native verification path.


## Content definitions and source stance

Fresh rich construction asks for a content `definition` alongside each formula.
It stores that definition as `Commitment.text`; catalogue definitions also denote
content. Only the exact source-known leading frame described below is mechanically
unframed; other restatements remain model judgments. Both
kinds of definition are screened using the same attribution lexicon as target
policy. Invalid definitions enter the logged, bounded construction correction
path; they cannot bypass validation by remaining flat. Lexical screening can
reject legitimate uses of attribution vocabulary and cannot establish semantic
fidelity. The existing correction allowance and admission budgets still apply.

`commitment-provenance.json` preserves a commitment-id mapping to source ID,
source authors, attributed speaker, physical page range, evidence ID, exact source
text, source kind, attribution, stance and omitted support IDs. Bibliographic
authors are preserved when supplied in the literature input; current published
extraction entries omit those records, so source_authors is empty for them. The
attributed speaker remains available independently. Missing authors are not inferred. `author_claim`
maps to `endorsed`, `reported_view` to `reported`, and `attacked_view` to `attacked`.
Reported/attacked source-kind tags must agree with attribution. Endorsed describes
the source's stance; it is not a truth judgment by ARA. Omitted support is a
separate condition and remains disclosed even for endorsed source claims.

The sidecar uses `commitment-provenance-v1` and `definition_semantics: content`.
Its SHA256 covers all fields except `sha256`, using the same canonical UTF-8 JSON
as the frozen catalogue. It binds both `CommitmentSet.to_dict()` and the catalogue
SHA256. `validate_commitment_provenance` and `load_commitment_provenance` in
`ara.runtime.commitment_provenance` return the verified full sidecar. Absence
returns `None`: legacy stance/content semantics are unavailable, never implicitly
endorsed. A present invalid sidecar refuses. The full sidecar is logged as
`commitment_provenance_frozen` before the single `commitments_frozen` event.
The CommitmentSet codec and existing frozen catalogue formats stay unchanged.

Plan v12 binds the per-window correction policy and normalization semantics. Rebuild for this
policy; do not reinterpret an old frozen catalogue or resume an old counted plan
as content-level construction. Search, fork/resume preservation and stance-aware
route admission consume this interface in their owning integration lane.


## Window correction budgets and exact unframing

`construction_targeted_corrections` defaults to 2 in the base configuration and
full-extraction profile. It is a nonnegative integer, scoped independently to each
window and each call type (`select_t_roots`, `build_t_batch`); 0 disables targeted
correction. The second correction sees the accumulated full candidate, including
changes from a failed first patch. Every correction uses the same transport,
context admission, token/cost accounting and provider policy as other construction
calls. Transport retries do not spend extra correction slots. There is no separate
global correction counter: finite windows and their local limits, together with
the existing run token/cost caps, bound execution. At 74 windows the limit permits
up to 296 targeted correction requests across both call types, not a reservation
or forecast that all those calls will occur. Structural correction remains its
separate one-shot check.

The counted plan binds this policy. Resume restores completed windows, skips the
terminal refused window, and gives each later window its own allowance. Changing
the correction limit requires a new plan. Old counted plans are not reinterpreted.

Definition feedback names all offending commitment IDs and symbol names and lists
the matched attribution phrases. The shared attribution lexicon is unchanged: it
can reject legitimate uses of those words. More correction opportunities do not
establish faithful translation or guarantee better source coverage.

Before that check, runtime may remove exactly a leading `a argues that P`,
`a holds that P`, or `a claims that P` frame, where `a` exactly matches a supplied
source author or attributed speaker for that evidence. Multiword names are allowed.
It does not remove negated, conditional, quoted, unknown-speaker or nonleading
frames. Matching is case-sensitive and requires `that`; nested frames are not
recursively stripped. The remainder passes through definition validation again.
This is an explicit syntactic convention for constructing content with provenance,
not a semantic guarantee about arbitrary prose.

Each transformation logs `definition_unframed` with window/plan identity, kind,
name, evidence IDs, author, original_definition and definition. Accepted provenance
rows optionally carry `definition_unframes`, a nonempty list of records with
`kind`, `name`, `author`, `original_definition`, and `definition`. Source text,
citation, attributed speaker and stance are not overwritten. The sidecar hash
covers this history; validators check its exact frame and symbol/evidence bindings.
Existing v1 rows without the optional history remain valid. Reading new history
requires this validator version; older strict readers cannot consume it. Fork,
resume, search and reports preserve the full validated sidecar through their
existing interface. Rejected normalization events remain in the log even when no
commitment is eventually accepted.

## Cross-source symbol alignment

Before the single freeze, rich construction ranks compatible atom/predicate pairs
from disjoint source-paper sets by TF-IDF-weighted definition-token overlap
(preferred cosine score defaults to 0.10, configured by
`construction_alignment_min_score`). Deterministic backfill from lower-scoring
shared-term pairs uses the available allowance; zero-overlap pairs are not
invented. `construction_alignment_paper_diversity` (default true) replaces a
lowest-ranked candidate when this adds an uncovered paper without losing any
covered paper. The counts at signature, lexical and threshold filtering and final
paper coverage are recorded. These are retrieval heuristics, not semantic
judgments. `construction_alignment_candidates` bounds the top
pairs, default 150; zero explicitly disables judgments. Each pair is a two-symbol
cluster. This lexical ranking is a lead, not a semantic equivalence assertion.
Constants are never merged. The plan version and candidate limit bind resume.

`judge_symbol_alignment` uses the construction formalization provider/model and
its isolation, cache, logging and budget path, including retries. It sees only
the pair, original definitions, source provenance and frozen-input hashes, never
search goals. It returns one of `same_content`, `entails_left_right`,
`entails_right_left`, `contrary`, `unrelated`, with a short reason. The default
output allowance is 2048 tokens. Changed definitions and prompt/schema identities
partition the cache. Live schema preflight includes this call; the identity-free
response schema invalidates earlier preflight receipts. Replies contain only
`relation` and `reason`. Exact left/right identities come from the candidate
record; any returned identifier is rejected, never normalized or silently repaired.

After `validation_attempts` (1–3), an invalid reply becomes a typed
`alignment_unresolved` outcome with its exact pair, reason and attempt count.
It grants no bridge or rewrite and is never counted as `unrelated`. Construction
continues unless the absolute count exceeds `construction_alignment_max_unresolved`
(default 5; 0 requires every candidate to resolve). Exceeding the limit stops before
freeze with `symbol_alignment_incomplete`. Provider, accounting and budget stops
remain operational failures, not unresolved judgments. Report `data.json` exposes
`construction.alignment.unresolved`, its count and the declared limit.

Same-content components use their lexicographically first symbol; formulas are
rewritten and evidence IDs merged without changing original source text,
citations or stance. Other nontrivial relations create explicit commitments
with `kind: alignment`, `stance: model_alignment` in provenance. Predicate bridges
are universally quantified over the same ordered argument tuple. Each bridge
cites both original definitions and evidence citations. Neither equivalence nor
a bridge is inferred from lexical similarity alone.

The entire alignment set is checked for signature/arity, uniqueness and Z3
consistency. Solver-unsatisfiable or solver-unknown sets are refused together and logged;
original T is retained. In particular, an already inconsistent source T cannot
receive an accepted nontrivial alignment. This does not suppress or repair source
contradictions. Operational and budget failures still stop before freeze.
The final working-T input allowance is checked again after alignment.

Existing CommitmentSet, commitments.json and frozen-t-v1 formats stay unchanged.
`commitment-provenance-v2` adds an `alignment` receipt containing original T and
symbols, bounded candidates, all judgments, canonical mapping, status and refusal
reason. The sidecar hash binds the complete receipt and final T/catalogue hashes.
Its validator replays the judgments; old v1 metadata and legacy absence retain
their existing behavior. New readers are required for v2. Fork/resume preserve
and validate the full sidecar and `commitment_provenance_frozen` event.

Search may use bridges as disclosed alignment premises. They are not source CQ
evidence, belong to no single paper, and cannot replace the requirement for at
least two endorsed source supports. Existing distinct-formula, cross-paper and
novelty gates still apply. Route receipts, rendered routes, writer/auditor outlines
and methodology retain alignment disclosure, including canonical rewrites.
Offline fake judgments establish only persistence and search plumbing, never
faithfulness, semantic equivalence or improved real argument quality.

### Continue unfinished alignment

`resume-construction` still owns terminal window-provider refusals.
`resume-alignment` owns runs with all window outcomes recorded and one verified
merged working artifact, where alignment has not finished and no freeze artifact
or receipt exists. It checks the log chain/tail, bank, plan artifact, all accepted
and skipped windows, merged commitments/symbols/provenance, candidate inventory,
and the full input bindings of accepted judgments. It restores valid legacy
judgments without changing their replies; rejected legacy replies stay rejected
and those pairs are judged anew under the identity-free schema. Explicit unresolved
outcomes are retained only with their exhausted rejected-attempt receipts.

```sh
uv run ara resume-alignment --run-dir runs/previous --plan-only --output-dir runs/alignment-plan
uv run ara resume-alignment --run-dir runs/previous --codex-schema-preflight-log runs/current-preflight/events.jsonl
```

The free plan creates no provider or counter and appends no source-run events;
only lock files may be created in that directory. It reports completed windows,
restored commitments and accepted/unresolved/remaining candidate counts in
`alignment-resume-plan.json`. It does not certify live context, spend or semantic
acceptance. A live continuation uses the original run configuration and accounting,
with optional current preflight and unknown-usage-policy overrides. It records
HUMAN/resumption receipts, continues alignment, freezes exactly once, then uses
native target proposal (including bounded forward synthesis) and search.
Construction model calls are not replayed. Concurrent resume, incomplete or corrupt
construction, interrupted dispatches without terminal receipts, a completed alignment
and partial/already-completed freezes are refused. Existing search recovery owns
runs that have already reached search.

Persisted consistency refusals remain refusals if a later solver run would resolve
the query: their final T must still equal original T with an identity mapping and
no bridge rows. Accepted alignments are rechecked on load. A refused receipt is
never silently promoted into an accepted alignment during fork or resume.


Alignment policy v2 records the effective preferred threshold, diversity setting,
pre-filter counts, selected/backfilled counts and covered papers under `retrieval`
in the alignment receipt. The reader recomputes these fields. Previously frozen
policy-v1 receipts keep their original hard 0.15 cutoff on replay; they are not
silently expanded on resume. Policy v3 retains that retrieval and adds separate
`unresolved` and `unresolved_limit` receipt fields. The validator requires judgments
and unresolved outcomes to partition the exact candidate inventory. Legacy v1/v2
alignment receipts still load; new v3 receipts need this reader. Construction plan
v15 binds the retrieval, judgment policy and unresolved limit. Alignment recovery
verifies the original completed plan rather than rebuilding it with v15.
Alignment judgment requests explicitly set `topic=''`: the task topic and any
desired thesis do not enter the pair judgment prompt. Every selected pair still
requires the model's relation judgment; broader retrieval never asserts an
alignment by itself.

## Proposed hypothesis premises

`hypothesis_premises` is an optional run-config list, empty by default. Each entry
has `id` (prefixed `hypothesis:`), content `text`, `rationale`, `proposer`
(`ara-target`, `eps2`, or `operator`), and nullable `linked_gap`/`linked_target`
(at least one is required). Supply exactly one of a normal formula AST or a
`formalization_request` string. Optional `new_symbols` entries contain `name`,
`kind`, `arity`, and a content `definition`; every symbol must be used and cannot
replace an existing catalogue signature. Missing definitions refuse.

For example, with P and Q already defined, a placeholder hypothesis can declare
`(P and Q) implies R`, introduce R with an explicit definition, and link to a
placeholder target. A supplied formula passes the normal local formula schema;
a request passes through the logged `formalise` model boundary. Text/formula
fidelity remains a model/operator responsibility, not a consequence of Z3.

Admission follows source symbol alignment and precedes the single freeze and
capacity check. The full combined T and H must be satisfiable; conflicts and
solver uncertainty refuse before writing freeze artifacts. This conservative
admission also refuses a T that already contains unrelated contradictions.
Search still uses its existing consistent-support policy. Hypotheses cannot be
added to a completed freeze; construct a new run. Frozen-prefix forks preserve
existing hypotheses and their provenance bytes exactly.

The four-field CommitmentSet codec and frozen-t v1 catalogue envelope are
unchanged. Hypothesis-bearing provenance uses v4 with a replayable base snapshot,
exact declarations/resolved formulas and consistency receipt. Its canonical hash
binds the complete T and catalogue. A hypothesis row has `kind=hypothesis`,
`stance=proposed`, and `source_id=null`; it never supplies paper ownership,
bibliography entries, source-pair conflicts, or CQ source evidence.

A selected route still needs two distinct source formulas assignable to two
endorsed papers. Per-paper novelty includes used H as assumptions in both
whole-target and essential-atom checks: if H alone or H plus one paper supplies
the target or its claimed new atom, extra source leaves do not turn that
restatement into a contribution. A successful using route remains mechanically
CLOSED but its contribution receipt and human rendering say **conditional on H**.
This neither proves H nor turns an OPEN proposal paper into a derivation.

The writer must state each H in a node-marked sentence beginning “This paper
proposes” or “We propose”, with no source citation or author attribution. The
runtime owns the conclusion-status disclosure: after validating the authored
argument, compose inserts a fixed **Runtime conditional disclosure** section
first in the body, naming the exact H IDs. The insertion receipt binds the route,
block hash and unchanged authored-body hash. Model prose must not supply or
imitate this reserved section or its status statement.

Compose, export, publication and reload require the exact first-body block and
its matching route-bound receipt. Moving it under an authored negation, altering
H, removing it or duplicating it refuses. Publication checks both the audit and
reading copies after the title. Resuming a recorded draft verifies and preserves
the existing block. Writer/revision/publication instructions explain the runtime
boundary; an audit cannot authorize changes to it. The existing status-wording
screen uses NFKC only for checking, without rewriting accepted text.

The typed `proposed_principle` role is available only for verified hypothesis
nodes. Other source and argument roles, three-sample adverse-union audits,
citation verification and repair bounds stay in force. Construction receipts,
report data, methodology, route receipts and figures retain proposed status.
Selection summaries, CLI listings and tree headings disclose H beside the
classification; OPEN routes retain reachable H use and state that no completed
conclusion is established. Local assumptions and unreachable nodes do not become
global H use. Runtime status is a mechanical disclosure, not a semantic proof of
arbitrary authored prose.

## Shared vocabulary and wider alignment (opt-in)

A fresh lifecycle can set `construction_shared_vocabulary: true`. Construction
then replaces the source-prefixed naming preference with a shared-vocabulary
contract in the counted, cached and logged formalization prompt. The existing
run-level catalogue grows sequentially from accepted source-supported symbols.
The model is asked to reuse exact meanings/signatures and expose relational
structure with predicates, terms and connectives. No starter ontology, automatic
synonym rewrite, minimum reuse quota or invented equivalence is introduced.
Faithful atomic formulas remain possible; offline tests cannot establish source
faithfulness or guarantee that a provider follows this guidance.

`construction_alignment_top_k: 20` selects up to 20 neighbours per atom/predicate
from all signature-compatible cross-source pairs. Definition-weighted lexical
similarity ranks neighbours, including zero-overlap pairs; it is not an embedding
retriever or a semantic equivalence test. Neighbour rank rounds distribute the
existing `construction_alignment_candidates` global call cap across symbols.
For example, set that cap to 2000 for a wider pool. A top-k union may contain
fewer than the cap; very small caps can still leave symbols uncovered. Retrieval
receipts disclose the selected inventory, zero-overlap/backfill counts, coverage
and truncation. Only subsequent model judgments authorize same-content rewriting
or disclosed entailment bridges. The existing consistency/refusal gates apply.
All candidate pairs are considered for ranking; retained neighbour memory is
bounded by symbol count times the smaller of top-k and the global cap.

Both settings are run-level only and validated before planning. Defaults are
false/zero and preserve prior prompts, plan fields and retrieval receipts.
Enabled shared guidance is bound into the construction plan; enabled top-k is
bound into its alignment policy and persisted retrieval receipt. The alignment
receipt envelope remains v3; its retrieval payload is extended only when top-k
is enabled. Updated validators replay that inventory exactly; old readers refuse
new retrieval payloads rather than downgrade. CommitmentSet, commitments.json,
frozen-t and provenance codecs are unchanged in this round.

A previously planned lifecycle cannot widen alignment in place: its recorded
configuration and construction plan bind that inventory. Native resume reads the
recorded policy; frozen-prefix forks preserve the frozen result. Use a fresh
lifecycle for changed policies. Copying cache files does not authorize replay
under changed prompts, plans, catalogue or commitment hashes.

Construction and alignment emit opt-in vocabulary metrics, exposed in methodology:
atomic commitment count/fraction, actual source-use shared symbols/predicates,
shared symbols including model-alignment context, and cross-paper exact-antecedent
modus-ponens candidates among endorsed source rows. The last is a narrow structural
opportunity count, not a complete bank sweep, solver proof or licensed route.
Alignment bridges do not count as source endorsement. Inspect the source-use and
alignment-context counts separately; a bridge can raise only the latter.

Shared guidance adds prompt tokens but no new logical calls. Wider alignment can
add one logical judgment per selected pair, each with the existing validation
attempt allowance. Run/window/provider budgets still apply, and unresolved
judgment limits still refuse freezing. These options may increase latency and
are not a claim of useful cross-paper synthesis without a measured live run.


The precise attribution screen recognizes explicit report frames even when
emphasis, quotes, a colon or a dash separates the verb from its complement marker.
Sentence-ending punctuation remains a boundary. This same check runs when loading
persisted provenance; a previously admitted formatted report frame refuses rather
than being accepted under a recorded precise-screen marker. Source text is intact.

Precise screening checks raw text and a formatting-free view, using Markdown
tokens plus HTML text/entity parsing. Formatting inside report words, HTML tags,
character entities and line-break tags cannot hide the tested explicit frames.
The normalized view is never substituted into accepted definitions, catalogue
entries or provenance. The legacy screen remains unchanged.

Under the precise screen, content definitions must be textual: Markdown image
tokens and non-text HTML elements are refused, including nested/reference images,
`img`, image inputs and embedded content. Only the explicit text-formatting HTML
tag set is supported; other tags refuse even if they contain text. Empty
normalized text also refuses.
Alt text cannot serve as the definition. Correction feedback identifies this
unsupported markup explicitly. Source material remains intact and no image or
URL is fetched. Ordinary text formatting remains supported by the screening view.


The supported HTML subset is attribute-free emphasis, spans, paragraphs, line
breaks, code and lists. All HTML attributes refuse; hidden/style/directional
presentation is not interpreted. Tags with special rendering behavior, including
`details` and `bdo`, are unsupported. Invisible Unicode format controls, selectors
and fillers refuse rather than split a reporting word in the screening view.
Ordinary Markdown emphasis and links remain supported. This is a conservative
textual boundary, not a browser renderer or semantic attribution proof.


The decoded formatting-free screening view also uses Unicode NFKC compatibility
normalization, so bold/full-width typographic letters cannot conceal an explicit
report frame. Accepted definitions retain their exact original typography. The
raw guard remains independent: report text in an HTML comment still refuses even
though the display-oriented view omits that comment. This policy does not claim
to recognize arbitrary visual confusables or determine semantic authorship.
