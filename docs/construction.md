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
required prerequisites from preliminary omission groups. Exact attributed evidence
text and citations survive into T; identical or contradictory formulas are not
deduplicated. Shared symbol definitions and model-produced semantic reuse
decisions are logged and validated; code derives syntactic occurrence bindings and
copies source text/citations. Code never invents equivalences. Faithful
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
retaining qualifiers and inference endpoints. Frontier commitments are explicitly
marked `assumed_premise; support_omitted` with omitted support IDs; methodology
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
`ara.runtime.cli.make_provider` (`ara/runtime/cli.py:123`). Their isolation,
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

Rich construction preserves selected inference nodes as attributed conditionals
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
`ara/runtime/search_alignment.py:20` and `ara/runtime/calls.py:970`.

## Shared-frozen candidates are deferred

`fork-from-freeze` is not a command at base `6511ff6`. `ara run --from-frozen` is
also absent. The separate eta work is not integrated here; see [PLAN](../PLAN.md).
Do not copy `commitments.json` into a new run to simulate provenance import. A
fresh `ara run` constructs and freezes its own T.
