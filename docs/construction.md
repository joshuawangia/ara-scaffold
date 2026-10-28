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
(cosine score at least 0.15). `construction_alignment_candidates` bounds the top
pairs, default 150; zero explicitly disables judgments. Each pair is a two-symbol
cluster. This lexical ranking is a lead, not a semantic equivalence assertion.
Constants are never merged. The plan version and candidate limit bind resume.

`judge_symbol_alignment` uses the construction formalization provider/model and
its isolation, cache, logging and budget path, including retries. It sees only
the pair, original definitions, source provenance and frozen-input hashes, never
search goals. It returns one of `same_content`, `entails_left_right`,
`entails_right_left`, `contrary`, `unrelated`, with a short reason. The default
output allowance is 2048 tokens. Changed definitions and prompt/schema identities
partition the cache. Live schema preflight includes this call.

Same-content components use their lexicographically first symbol; formulas are
rewritten and evidence IDs merged without changing original source text,
citations or stance. Other nontrivial relations create explicit commitments
with `kind: alignment`, `stance: model_alignment` in provenance. Predicate bridges
are universally quantified over the same ordered argument tuple. Each bridge
cites both original definitions and evidence citations. Neither equivalence nor
a bridge is inferred from lexical similarity alone.

The entire alignment set is checked for signature/arity, uniqueness and Z3
consistency. Unsatisfiable or unresolved sets are refused together and logged;
original T is retained. In particular, an already inconsistent source T cannot
receive an accepted nontrivial alignment. This does not suppress or repair source
contradictions. Model-call validation and budget failures stop before freeze.
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

The existing construction-resume command still handles terminal window-provider
refusals only. A failure during the later alignment stage stops before freeze;
that stage has no dedicated resume entrypoint. Use a new run with the retained
cache rather than treating a partial alignment ledger as frozen T.

Persisted consistency refusals remain refusals if a later solver run would resolve
the query: their final T must still equal original T with an identity mapping and
no bridge rows. Accepted alignments are rechecked on load. A refused receipt is
never silently promoted into an accepted alignment during fork or resume.
