# Brain decisions for the ara program (2026-10-08)

This is an append-only decision history. Entries describe the revision and task
in which they were written, including failed trials and superseded policies.
Annotations link replacements without deleting the original text. For current
operation use [README](README.md), [guides](docs/README.md) and [PLAN](PLAN.md).
Source citations in the documentation correction entry refer to base `6511ff6`.

## Index by area

### Foundations and engine

- [Alpha decisions](#alpha-decisions)
- [Beta engine decisions](#beta-engine-decisions)

### Runtime and integration

- [Gamma runtime decisions](#gamma-runtime-decisions)
- [Runtime integration gap (no seam changes)](#runtime-integration-gap-no-seam-changes)
- [Gamma verification handoff](#gamma-verification-handoff)
- [Delta integration decisions](#delta-integration-decisions)

### Writing and verification

- [Round 2 eta: writer retries, pilot, Python (R1–R3, R5–R6)](#round-2-eta-writer-retries-pilot-python-r1r3-r5r6)
- [Round 2 theta — verification known cases](#round-2-theta-verification-known-cases)
- [Round 2 iota: prevent writer extrapolation beyond supplied links](#round-2-iota-prevent-writer-extrapolation-beyond-supplied-links)
- [Round 2 iota: distinguish malformed audit inventory from an adverse verdict](#round-2-iota-distinguish-malformed-audit-inventory-from-an-adverse-verdict)
- [Round 2 iota continuation: pilot output allowances](#round-2-iota-continuation-pilot-output-allowances)
- [Round 2 iota: leave counting margin below the writer ceiling](#round-2-iota-leave-counting-margin-below-the-writer-ceiling)

### Extraction and provenance

- [Round 3 gamma: logged per-paper extraction](#round-3-gamma-logged-per-paper-extraction)
- [Round 3 gamma fix 1: corpus capacity, lineage and PDF coverage](#round-3-gamma-fix-1-corpus-capacity-lineage-and-pdf-coverage)
- [Gamma round 2: rich evidence and working T](#gamma-round-2-rich-evidence-and-working-t)
- [GX25 — Kind-specific extraction and bounded targeted correction](#gx25-kind-specific-extraction-and-bounded-targeted-correction)
- [GX26 — Counted root-selection allowance and compact inventory decisions](#gx26-counted-root-selection-allowance-and-compact-inventory-decisions)
- [GX25 — Full extraction preflight and global construction capacity](#gx25-full-extraction-preflight-and-global-construction-capacity)
- [GX26 — Bounded windows over immutable global evidence](#gx26-bounded-windows-over-immutable-global-evidence)
- [GX27 — Unpaid planning shares execution's range admission](#gx27-unpaid-planning-shares-executions-range-admission)
- [GX28 — New gaps remain obligations throughout reconciliation](#gx28-new-gaps-remain-obligations-throughout-reconciliation)
- [GX29 — Finite paper allowances cover every extraction continuation](#gx29-finite-paper-allowances-cover-every-extraction-continuation)
- [GX30 — Mode-specific context requests and correction per response](#gx30-mode-specific-context-requests-and-correction-per-response)
- [GX31 — Disclosed paper failures and completed-paper reuse](#gx31-disclosed-paper-failures-and-completed-paper-reuse)
- [GX32 — Acceptance-bound reuse and a separate ancestry inventory](#gx32-acceptance-bound-reuse-and-a-separate-ancestry-inventory)
- [Kappa: extraction response acceptance and bounded correction](#kappa-extraction-response-acceptance-and-bounded-correction)
- [Kappa round 2: explicit conservative imports and grammar preflight](#kappa-round-2-explicit-conservative-imports-and-grammar-preflight)
- [Kappa round 2 live grammar rejection and correction](#kappa-round-2-live-grammar-rejection-and-correction)
- [Kappa round 3: conservative diagnostics and normalized recovery](#kappa-round-3-conservative-diagnostics-and-normalized-recovery)
- [M1 — Relaxed paper acceptance with preserved evidence](#m1-relaxed-paper-acceptance-with-preserved-evidence)
- [Mu addendum — accepted range union and bounded review](#mu-addendum-accepted-range-union-and-bounded-review)
- [Mu round 2: grounded evidence and retained quarantine](#mu-round-2-grounded-evidence-and-retained-quarantine)
- [M4 — Monotonic snapshot reuse and versioned gap publication](#m4-monotonic-snapshot-reuse-and-versioned-gap-publication)
- [M5 — Completed snapshot unions and stable ordinary reuse](#m5-completed-snapshot-unions-and-stable-ordinary-reuse)
- [M6 — Snapshot context follows native prerequisites](#m6-snapshot-context-follows-native-prerequisites)
- [M7 — Construction windows project metadata and imports append in batches](#m7-construction-windows-project-metadata-and-imports-append-in-batches)
- [Persistent extraction-lineage verification receipts](#persistent-extraction-lineage-verification-receipts)

### Construction

- [S1 — Budgeted prerequisite depth before the single freeze](#s1-budgeted-prerequisite-depth-before-the-single-freeze)
- [S2 — Soft construction shares and accounted window refusal](#s2-soft-construction-shares-and-accounted-window-refusal)
- [S3 — Terminal construction refusals and verified continuation](#s3-terminal-construction-refusals-and-verified-continuation)
- [S4 — Free counter refusals and non-mutating resume previews](#s4-free-counter-refusals-and-non-mutating-resume-previews)
- [S5 — Initial-share caps and construction dispatch configuration](#s5-initial-share-caps-and-construction-dispatch-configuration)
- [S6 — Native schema authority with bounded local validation](#s6-native-schema-authority-with-bounded-local-validation)
- [S8: Frozen construction catalogue interface](#s8-frozen-construction-catalogue-interface)
- [S9: Content definitions with hash-bound source stance](#s9-content-definitions-with-hash-bound-source-stance)
- [S10: Per-window correction and exact definition unframing](#s10-per-window-correction-and-exact-definition-unframing)
- [S8 structure gate and bounded correction](#s8-structure-gate-and-bounded-correction)

### Search and reports

- [Search trace receipts (version 1, superseded below)](#search-trace-receipts-version-1-superseded-below)
- [Offline full-run report projection](#offline-full-run-report-projection)
- [Search trace version 2 and report validation](#search-trace-version-2-and-report-validation)
- [Report overview and linked evidence (round 4)](#report-overview-and-linked-evidence-round-4)
- [Xi round 6 — Concurrent search with isolated accounting](#xi-round-6-concurrent-search-with-isolated-accounting)
- [Xi round 7 — Stable publication with durable worker journals](#xi-round-7-stable-publication-with-durable-worker-journals)
- [Xi round 8 — Job-local failure, one final retry and partial selection](#xi-round-8-job-local-failure-one-final-retry-and-partial-selection)
- [Round 9 — Xi: stopped search recovery](#round-9-xi-stopped-search-recovery)
- [Round 10 — Xi: bind resume completion to its results generation](#round-10-xi-bind-resume-completion-to-its-results-generation)
- [Round 12 — shared search vocabulary and explicit formula bindings](#round-12-shared-search-vocabulary-and-explicit-formula-bindings)
- [Round 13 — contribution targets, route selection, and frozen forks](#round-13-contribution-targets-route-selection-and-frozen-forks)
- [Round 14 — solver contribution and own-thesis gates](#round-14-solver-contribution-and-own-thesis-gates)
- [Round 15 — separate route metadata from contribution receipts](#round-15-separate-route-metadata-from-contribution-receipts)

### Providers

- [Omega — Isolated subscription CLI provider](#omega-isolated-subscription-cli-provider)
- [Round 7 integration — Stage providers share admission, not billing policy](#round-7-integration-stage-providers-share-admission-not-billing-policy)
- [Omega round 3 — Decoded output, construction retries and config authentication](#omega-round-3-decoded-output-construction-retries-and-config-authentication)
- [Omega round 4 — Context sizing and resolved construction dispatch](#omega-round-4-context-sizing-and-resolved-construction-dispatch)
- [Omega round 5 — Measured calibration and scarce-window allocation](#omega-round-5-measured-calibration-and-scarce-window-allocation)
- [Omega round 6 — Comparable usage and local subscription admission](#omega-round-6-comparable-usage-and-local-subscription-admission)
- [Omega round 7 — One unclassified retry and scrubbed exit diagnostics](#omega-round-7-one-unclassified-retry-and-scrubbed-exit-diagnostics)
- [Omega round 8 — Suppress free-text CLI diagnostics (kappa2 F1)](#omega-round-8-suppress-free-text-cli-diagnostics-kappa2-f1)
- [Omega round 9 — Read current host credentials and retry auth once](#omega-round-9-read-current-host-credentials-and-retry-auth-once)
- [Omega round 10 — Codex subscription transport](#omega-round-10-codex-subscription-transport)
- [Omega round 11 — Separate ChatGPT credential source](#omega-round-11-separate-chatgpt-credential-source)
- [Omega round 12 — Visible generic definitions are not tool use](#omega-round-12-visible-generic-definitions-are-not-tool-use)
- [Omega round 13 — Strict Codex schemas and pilot gate](#omega-round-13-strict-codex-schemas-and-pilot-gate)

### OCR

- [Rho2: local OCR fallback at PDF intake](#rho2-local-ocr-fallback-at-pdf-intake)
- [Rho2 Round 2: clean-token retention and local VL second tier](#rho2-round-2-clean-token-retention-and-local-vl-second-tier)
- [Rho2 Round 3: preserve the text layer and repair spans](#rho2-round-3-preserve-the-text-layer-and-repair-spans)
- [Rho2 Round 4: synthesized-character confidence (tau2-F1)](#rho2-round-4-synthesized-character-confidence-tau2-f1)

Early brain decisions B1–B8 follow this index. Provider policy evolves through
[B9](#decision-b9), [B11](#decision-b11) and the Omega entries; audit/writer
policy through [B10](#decision-b10), [B12](#decision-b12), [B13](#decision-b13)
and Round 2. [Documentation corrections](#documentation-corrections-2026-10-27)
list source-backed differences from the old operating guides.


Copy the relevant ones into the repo's DECISIONS.md with their reasons.

B1. Repo: `ara-scaffold`, built at `/home/dev/wt/ara/ara-scaffold`, default branch
    `main`. Target remote: private repo on the operator's personal github.com account
    (`<operator repo>`). This box is not yet authenticated to github.com;
    the brain handles remote creation and push. Workers never push.

B2. Real provider: Anthropic. Default model `claude-opus-5` (current Opus; exact
    string, no date suffix). Pricing for the cost cap lives in config.yaml as data:
    claude-opus-5 input $5.00 / output $25.00 per million tokens. Use the official
    `anthropic` Python SDK (never raw HTTP, never an OpenAI shim). Reference docs
    copied to /home/dev/wt/briefs/ara/ref/ — read them before writing provider code;
    do not guess SDK names.
    - Schema-validated JSON: use structured outputs (`output_config={"format": ...}`,
      or `client.messages.parse`) and ALSO validate locally against /schemas; reject
      and log on failure.
    - Adaptive thinking (`thinking={"type": "adaptive"}`), effort configurable.
    - Check `stop_reason` before reading content; `refusal` and `max_tokens` are
      rejections that get logged, never silently accepted.
    - Web search for originality and citation verification: server tool
      `{"type": "web_search_20260209", "name": "web_search", "max_uses": N}`.
      Server-tool errors arrive as result blocks, not exceptions — handle both shapes.
      Citations are incompatible with output_config.format, so the verification
      step is two calls: (1) search-enabled call returning evidence text + URLs,
      (2) a schema-validated call that classifies each item verified/unverified
      using only the evidence from call 1. Unverified items are removed.
    - Token/cost accounting from `response.usage` (include cache read/write and
      server-tool usage counts in the log). Caps checked BEFORE each call using a
      conservative estimate (count_tokens or max_tokens bound) and after each call
      with actuals; exceeding a cap stops cleanly: log a STOP record, write partial
      artifacts, exit non-zero with a clear message.

B3. Provider abstraction: `Provider` protocol with `MockProvider` (deterministic,
    reads canned responses keyed by call kind + input hash, no network) and
    `AnthropicProvider`. config.yaml names provider + model; key from env
    `ANTHROPIC_API_KEY` (or SDK default credential chain). Tests use Mock only.

B4. Cache: content-addressed by (call kind, prompt template hash, rendered input
    hash, model id, schema hash). Re-running with the same cache and seed must give
    byte-identical route graphs. Cache dir gitignored.

B5. Smoke run content: `ara run --smoke` must not put philosophical content in the
    repo. It ships a placeholder literature fixture (statements over P, Q, R with
    placeholder citations) and a placeholder topic, so a real provider exercises
    every call end to end on placeholders. Outputs go to gitignored runs/. A real
    topic + literature are supplied at run time via flags (`--topic`, `--literature`)
    and never committed. Record this in DECISIONS.md as the resolution of
    "smoke must run with a real provider" vs "no philosophical content in repo".

B6. Formalisation language: a small JSON formula AST (atoms, not, and, or,
    implies, iff, forall, exists, predicates with constant/variable args) with a
    JSON schema, compiled to Z3. Deductive licensing = Z3 proves
    premises ∧ ¬conclusion is UNSAT. Defeasible steps need no entailment proof but
    every critical question must be answered for the route to be CLOSED.

B7. Negation of a proposition = a canonical `not` wrapper at the AST level and a
    canonical text form; "T contains the leaf's negation" is checked on canonical
    forms, not on string similarity.

B8. Human input (select/feedback) is logged verbatim with label HUMAN and a
    timestamp; human time is measured as wall time between the prompt being shown
    and the input being accepted, plus any explicit `--human-minutes` the operator
    supplies, labelled as which.

<a id="alpha-decisions"></a>
## Alpha decisions

A1. Use jsonschema (Draft 2020-12) and stdlib frozen dataclasses. This separates
wire validation from immutable engine types without another model framework.
No extra runtime dependency is introduced. Setuptools is the build backend.

A2. Alpha runs natively as the assigned executing worker; no delegation, push,
provider calls or shipping workflow. The task contract overrides generic skill
shipping/branch advice. Main is explicitly authorized; this is a new repository.

A3. All collections crossing the seam are tuples of frozen values. Formula AST
has explicit variable/constant terms; canonical text is compact sorted JSON of
a normalized AST (commutative and/or sorted and flattened, double negation
removed, bound variable names retained). This is structural normalization, not
logical equivalence or alpha-equivalence. Negation uses the same canonical form.

A4. Deductive schemas use Formula AST atoms named in formula_variables as
metavariables. A quantified body metavariable may contain a free variable.
Substitution constraints explicitly connect a slot to a capture-avoiding
substitution of a metavariable body. Engine must implement this before licensing
UI/EG; they cannot be treated as unconstrained propositional atoms.

A5. Scoped discharge: bank AssumptionScope identifies an assumption slot and
result slots checked under it. Proposal PremiseFill.scope_id identifies the
scope; assumption fills use open, never a T id. RouteGraph ProofScope links an
assumption node and result node to the discharging inference node. Result proof
must depend only on the declared assumption and independently licensed external
premises; no scope-local assumption may escape to a T leaf or another scope.
Conditional proof exports P implies Q from a checked P-scoped Q proof. Reductio
exports not P from checked P-scoped Q and not Q proofs. Engine checks scope and
rule shape first, then proves the exported sequent with Z3, using discharged
subproof implications rather than treating assumptions as global premises.
Alpha defines the representation; engine lane owns validation and solving.

A6. Scheme forms cite Walton, Reed & Macagno (2008), Argumentation Schemes.
Page/chapter locators not verified here are explicitly unknown. Forms are
normalized slot interfaces for the requested core, not quotations or claims of
a complete transcription. The bank version is 1.0.0; amendments require version
review. Critical questions are slot-only templates; CQ ids are local to entries.

A7. Ports are synchronous Protocols. Runtime adapters own all model/network,
cache/schema/log/budget effects. Event payloads are stored as canonical JSON
strings to avoid mutable nested objects; EventSink emits immutable RunEvent.
Graph/proposition/proposal ids and ordering are owned by the engine. Graph
serialization sorts JSON keys but retains tuple order for deterministic replay.

A8. All model schemas are standalone Draft 2020-12 documents with closed object
shapes. Formula definitions are embedded where needed (no network resolution).
Originality/citation verification has one structured classification schema; B2's
preceding evidence acquisition is a provider tool response, not a JSON model
contract. Evidence references, verified state, quotation text and remove/retain
are explicit; runtime must reject unsupported verification and remove unverified
items. A schema is shape validation, not evidence of truth.

<a id="decision-a9"></a>
> Status: CLI placeholder status superseded by [D1](#decision-d1).

A9. CLI console registration targets ara.runtime.cli:main, but that module remains
a docstring-only placeholder as required by this phase. CLI commands, real smoke,
private remote and fresh-clone end-to-end proof belong to later integration.

<a id="decision-a10"></a>
> Status: Smoke bounds superseded by [D4](#decision-d4), [D9](#decision-d9) and [D13](#decision-d13).

A10. Budget defaults: 200000 tokens, USD 10, output maximum 8192 tokens per call;
smoke uses 2 targets, depth 2, node cap 24 and 300-word draft. Pricing is explicit
config data including cache and web tool assumptions requiring provider-lane
verification before monetary enforcement. No pricing is inferred as zero.

A11. Substitution.slot may be the reserved conclusion slot (UI) or a premise
slot (EG). The formula at that slot is an instance metavariable constrained to
the stated body substitution; it is not an independent free choice. Conclusion
slot id is fixed to `conclusion` for deductive forms. Conjunction elimination
and disjunctive syllogism use commutative matching; double negation is oriented
as elimination, with introduction available through canonical normalization.

A12. RouteGraph.dialectical_cost uses null for an infinite or not-yet-evaluated
cost; the engine should distinguish those cases through status/decision events,
never serialize nonstandard JSON Infinity. Type constructors validate shape,
not graph closure, CQ truth, membership, or proof correctness. Those remain
engine responsibilities. A CQ answer's answered flag alone is not evidence.

A13. Standalone local schemas use full Draft 2020-12, including conditionals for
verification. Runtime owns any provider-compatible structured-output projection
and must always revalidate the original schema locally. Provider acceptance of
these exact schema features is unexecuted, not assumed.

<a id="beta-engine-decisions"></a>
## Beta engine decisions

E1. Execute natively in the assigned lane, without delegation or publishing. The
brief governs the return-to-caller handoff and permits lane commits. Baseline:
`b8dd2d7`; real `uv sync`; 45 scaffold tests passed. New licensing tests first
failed at the missing Licenser import, then passed after implementation.

E2. Licensing checks bank identity, exact nonempty slots, canonical conclusion,
and scope annotations first. For deductions the solver runs before schema
matching so invalid sequents report SOLVER_COUNTEREXAMPLE, even if the named
rule also mismatches. An entailed sequent still fails if it does not instantiate
the named rule. Solver UNKNOWN and timeout are separate discard reasons.

E3. Formula symbols use disjoint atom, predicate/arity, constant and variable
namespaces. Quantifiers share one individual sort. Schema matching backtracks
across commutative partitions; quantifier instances use capture-avoiding
substitution. Scoped deductions prove the exported sequent using subproof
implications; closure must separately prove the scoped result children.

E4. Runtime entrypoint is `Engine(...).analyse(target)`; `search` is the single
polarity primitive. EngineConfig.from_mapping consumes the existing bounds and
optional solver_timeout_ms (1000 ms default). The scaffold config has no timeout
key; its semantics and the shared types/ports remain unchanged. API and reasoned
bounds are documented in ara/engine/README.md. No seam changes.

E5. The best-first queue contains partial AND trees and branches over alternative
licensed cuts. Cost is inference count plus unresolved external leaves; frozen
T leaves cost zero; opposition in T makes cost infinite (JSON null). Random ties
use a local seed. Depth, total allocated search nodes and cycles bound search.
Closure counts only canonical/id-matching T leaves and local discharged
assumptions. Missing CQ support leaves the inference itself on the frontier.
Nonempty CQ answers must cite existing frozen T ids; this checks evidence
presence, not semantic truth. Adapter exceptions propagate.

E6. Shared premises mean canonical formula identity, not T id or text identity.
Independent route count is the exact maximum disjoint set, including external
CQ evidence and excluding discharged assumptions. It counts routes discovered
within caps; a closed T terminus is not expanded to enumerate alternative proofs.

E7. Forward search applies deductive schemas over the finite observed formula
vocabulary, including quantifier substitution. Defeasible/scoped instances are
replayed from closed proof graphs because the bank contains no formal conclusion
schema for defeasible forms. One forward layer cannot consume its own new
consequences. Scoped exports account for their subproof height. Consequence and
instantiation-work caps are explicit with FORWARD_CAP and truncated=true.

E8. Tier 1 marks discovered canonical premise sets with opposite licensed
conclusions and requests a structured repair once per pair. Repairs are returned,
not automatically applied to frozen T. Tier 2 pairs opposing CLOSED routes and
runs forward from both; first flag is ordered by positive-route then negative-route
consequences, or null when no bounded consequence is flagged. No model text
creates a license or changes T through either path.

E9. Graph/analysis JSON contains no wall-clock data. EngineDecision events retain
real timestamps and reason codes through EventSink. Replays with the same seed
and port outputs are byte-identical; logs appropriately retain run timestamps.
Tests are scripted ports with placeholders, without network or provider imports.

E10. Final conflict review found that immediate slot sets alone omit a closed
route's CQ dependencies and exported scoped support. A new regression failed
with no Tier 1 conflict for equal external support. Tier 1 now also compares
closed routes by the same external canonical support used for independence;
repair fills for these sets are labelled support_0, support_1, etc., with frozen
T ids. Duplicate immediate/external witnesses request only one repair per pair.

E11. Final lane verification: `uv run pytest -q` passed 96/96 (51 engine,
45 scaffold). The executable negative-control runner produced 26 assertion
failures under deliberate production mutations and 26 green restorations,
including solver, bank, terminus, CQ, seeding, exported support, quantifiers,
and best-first priority. `git diff --check`, byte compilation and an AST import
audit passed. The external beta-report.md contains the test-by-test controls and
five placed integration findings. No provider smoke, publishing or fresh-clone
proof was performed in this engine lane; those remain integration obligations.
<a id="gamma-runtime-decisions"></a>
## Gamma runtime decisions

G1. Native execution in the assigned worker/worktree. No delegation or push.
Generic skill shipping steps are outside this worker contract. Shared types and
ports are unchanged. Runtime-owned EngineAPI describes the lifecycle required
from the engine factory; see the integration gap below.

G2. Calls use one fresh Messages request, topic-neutral templates, local full
Draft 2020-12 validation and typed seam decoding before success caching. Cache
identity includes the specified five B4 components plus provider, effort, output
bound, web-use bound and formula projection depth. Cache hits are revalidated and
logged with original response but zero incremental usage/cost. Engine licensing
remains authoritative; cached proposals do not constitute licenses.

<a id="decision-g3"></a>
> Status: Generation depth/projection superseded by [D3](#decision-d3); validation retries by [D8](#decision-d8); fallback policy by [B11](#decision-b11).

G3. Provider structured output projection removes unsupported validation keywords
and replaces recursive formula references with an acyclic depth-bounded family
(default six). At depth zero it permits atoms/predicates only. Local schemas and
Formula constructors still enforce full constraints. Real API acceptance of this
projection requires the explicitly opt-in live test; fake SDK proof is not API proof.
No SDK retries, fallback models or hidden conversation state are used. Refusal,
max_tokens, pause_turn, unexpected tool_use and server error blocks are rejected.

G4. JSONL and its .anchor tail-checkpoint file are both append-only, flushed and
fsynced under an advisory lock. Reopening verifies every record and checkpoint;
an interrupted append refuses recovery rather than guessing. This detects edits,
reordering and tail truncation when the checkpoint is retained. It is not a signed
remote audit: someone able to rewrite both files can forge a new chain. Log-only
export verifies the chain but cannot detect deletion of a valid suffix without
its checkpoint; retain the checkpoint for restart/integrity verification.

G5. Word count is every whitespace-delimited token in title plus body, including
route and citation markers. Bibliography is exclusively the separate schema array
and excluded from the count. The effective limit is min(6000, configured limit).
Over-limit output is rejected, never truncated. Draft nodes carry [[node:ID]];
exact marker coverage supplements, but cannot replace, the second model's semantic
audit. A model's faithful flag alone cannot override missing nodes or extra steps.

G6. Citation syntax is [cite:ID] with a matching bibliography entry; every quotation
uses straight or curly double quotes. Verification inventories all bibliography
entries and double-quoted spans, acquires web evidence, then classifies exactly
that inventory. Evidence URLs must occur in actual server search-result blocks,
not merely model prose. Unverified spans, markers and bibliography entries are
removed without replacement. The cleaned draft is audited again before export.
Web search/classification does not establish exhaustive originality or source
truth; reports preserve the evidence and uncertainty. Quotes/citations outside
the specified syntax remain a semantic model-audit responsibility.

G7. Anonymisation is an explicit bounded transformation: export only title/body/
bibliography (no run metadata or attribution), remove route markers, and replace
operator-supplied --redact strings literally with [REDACTED]. The schema has no
author field and prompts prohibit author/affiliation/acknowledgements. This is not
semantic identity detection; operators must supply identifiers that appear in prose.
Methodology intentionally preserves the complete human/model record and is not
represented as anonymised. It is reproducible solely from JSONL, without cache,
config, bank, graph or draft files. Report timestamps come only from logged events.

<a id="decision-g8"></a>
> Status: Smoke USD10 cap superseded by [D4](#decision-d4). Current subscription admission is scoped separately in [Omega round 6](#omega-round-6-comparable-usage-and-local-subscription-admission).

G8. Pricing uses explicit config data, Decimal arithmetic, separate cache TTLs and
server-tool counts; unknown rates never default to zero. Caps are checked before
and after every paid call; actual usage is logged before a post-call STOP. Search
admission reserves the configured model context ceiling for every possible search
iteration plus output bounds. The base 200k-token cap can refuse web verification
before spending. Smoke adds a 1,000,000-token cap and one search use, sufficient for
that conservative reservation; cost cap remains USD 10. Configured context/pricing
are operator assumptions, not an invoice guarantee. Input/output rates come from
B2; ancillary rates were supplied by alpha and still require current billing review.
Provider errors with no usage cannot prove zero spend; logs must disclose unknown
accounting rather than let a failed call become an uncounted retry.

> Status: Default first-CLOSED/OPEN selection is superseded by [Round 13](#round-13-contribution-targets-route-selection-and-frozen-forks) and [Round 14](#round-14-solver-contribution-and-own-thesis-gates): only `CLOSED-derived` is offered by default.

G9. Normal run builds/freezes T, generates targets, searches every target and its
canonical negation, invokes engine conflict/robustness analysis, then pauses for
`ara select`. Smoke selects the first CLOSED route (or first OPEN route), with an
explicit SYSTEM policy record. Human selection is separately HUMAN. Feedback is
logged verbatim and supplied to subsequent essay calls while the route remains
fixed and independently audited. Human CLI argv and supplied literature are
logged; interactive input measures prompt-to-accept elapsed time; explicit minutes
are labelled separately. Machine timing for model calls is observed wall time.

<a id="runtime-integration-gap-no-seam-changes"></a>
### Runtime integration gap (no seam changes)

> Status: Temporary adapter gap superseded by [D1](#decision-d1).

At base b8dd2d7 the engine exports no search API. Runtime currently imports
`ara.engine.create_engine(bank=..., proposer=..., formaliser=..., mapper=...,
cq_answerer=..., repairer=..., sink=..., config=...)` and expects `search(target,
commitments) -> tuple[RouteGraph, ...]` and `conflicts(routes, commitments) -> dict`.
This is a runtime-owned temporary adapter contract, not a claim that the parallel
engine lane has adopted it. Integration must align `native_engine` to that lane's
public API. Missing API is a loud nonzero error; production never uses the test
fake or duplicates engine search. Real-provider full smoke, final engine/runtime
integration and fresh-clone end-to-end proof remain integration-owned.

G10. Accounting failures after dispatch charge the conservative reservation with
`accounting=reservation_unknown_actual`, log STOP, and refuse resumption. A call
interrupted between call_start and its response also refuses resumption. The
methodology identifies reservations separately from measured cost. Cache writes
without TTL detail use the more expensive configured rate. Command wall time
excluding measured interactive input is recorded separately from model-call time.
Smoke topic/literature supplied by software are SYSTEM fixture data, not HUMAN
content; only argv and actually supplied content are attributed to the human.

<a id="gamma-verification-handoff"></a>
### Gamma verification handoff

> Status: Integration blocker superseded by [D1](#decision-d1) and [D14](#decision-d14); test counts remain historical.

Base: b8dd2d7c7d0b60a014ba9d9e3c43f1c21008105b. First runtime checkpoint:
9e05c74 (final revision recorded in the external gamma report). Executed local
suite: 77 passed, one live-provider test skipped because ANTHROPIC_API_KEY is
absent. Runtime negative controls: 22 intentional failures, every restored test
passed. The initial schema mutation survived because typed decoding also rejected
its fixture; the test was strengthened to isolate an unknown top-level schema
property before recording the successful negative control. Offline mock CLI
receipt: four route graphs, 70 input and 42 output tokens, USD 0.0014 simulated
ledger, zero provider spend. Native CLI with mock transport refuses the absent
engine factory with exit 2 and preserves the log and methodology. No real API or
fresh-clone integrated smoke result is claimed. Next unresolved step: connect the
native_engine adapter to the engine lane's actual public API, then execute the
credentialed smoke and fresh-clone instructions. Full evidence and six actionable
findings are placed in /home/dev/wt/shared/ara/gamma-report.md.

<a id="delta-integration-decisions"></a>
## Delta integration decisions

<a id="decision-d1"></a>
D1. Both requested lane tips are merged into main with merge commits. The only
merge conflict was appended DECISIONS sections; both are retained as historical
lane receipts. D1 onward supersede the historical integration gaps in A9, E11,
G1/G3/G8 and the gamma handoff. No shared type or port changes were needed.
NativeEngine binds frozen commitments and all runtime ports to Engine.analyse;
search_all persists both SearchResults and logs the complete AnalysisResult.
Identical duplicate graphs are persisted once; different graphs with one id fail
explicitly. Every target/polarity is
retained in the log. Test-only FakeEngine now returns AnalysisResult; all existing
lifecycle assertions are retained. There is no production fake or second search.

D2. Add --provider mock for the shipped offline fixture. Native canned responses
are keyed by the existing call-kind/rendered-input hash. They exercise the real
CLI, engine, forward licensing, route persistence, audits and exports, with
byte-identical cached graph replay. They are finite placeholder fixtures, not a
fallback for arbitrary inputs. Every missing response remains an explicit error.

<a id="decision-d3"></a>
D3. Live API execution found two SDK request failures hidden by fake-transport
proof: unsupported JSON Schema `not`, then an oversized compiled formula grammar.
The provider projection now strips unsupported `not`, uses two AST families
per depth (leaf/compound) instead of multiplying per-operator branches, and requires explicit default
fields in generated formulas. Original local schemas and typed codecs still
check operator arity, reserved ids and every acceptance constraint. The lane
projection test now uses the full valid atom codec rather than omitted defaults:
this tests its original valid-formula purpose against the new provider wire shape,
without relaxing local acceptance. New regressions preserve both actual failures.
The configured generation depth is two; deeper requested grammars can exceed the
service compiler's bounds. This is a generation bound, not a restriction added to
local solver/AST semantics. The original depth-six grammar was rejected live even
after branch compaction. No blind provider retry or fallback model was added.

<a id="decision-d4"></a>
D4. Smoke cost cap is USD 5, token cap 1,000,000, one possible web search; other
smoke bounds are unchanged. Failed HTTP calls retain separate logs, STOP and
conservative reservations labelled unknown actual spend. Those reservations are
not represented as measured charges. Configured pricing/context assumptions and
all G4–G7 semantic, verification, integrity and anonymisation boundaries remain.

D5. The engine mutation runner initially refused integration because it hardcoded
the old lane directory. It now verifies the running script's own Git root, like
the other runners, enabling the unchanged 26 engine controls on main or a clone.
The runtime negation control follows the new AnalysisResult persistence seam.
Integration controls disable graph writes and provider projections and require
assertion failures plus restored passes. No lane test was deleted or weakened.

<a id="decision-d6"></a>
> Status: Output allowance superseded by [D13](#decision-d13); local-validation retries by [D8](#decision-d8).

D6. The first accepted live search later rejected a max_tokens cut response at the
2048 output allowance. Smoke now reserves 4096 output tokens, preserving the
USD 5 cap. A low-effort trial returned an empty citation, correctly rejected by
the untouched local build_t schema. Final smoke retains the base high effort;
invalid output is never repaired by software or silently retried. Failed attempts
and their measured/unknown-spend ledgers are retained in ignored run directories.

<a id="decision-d7"></a>
> Status: No-local-retry policy superseded by [D8](#decision-d8).

D7. Repeated live empty-citation and empty-compound responses showed that schema
projection must communicate and preserve constraints, not just compile. Structured
prompts now include the complete original local response schema before input data;
that exact prompt reaches the provider, log and cache identity. build_t explicitly
copies nonempty supplied source identifiers. Existing canned response bodies are
unchanged; affected prompt hashes were regenerated. Installed SDK 1.12.1's
transform_schema confirms minItems 0/1 support. The compact projection therefore
uses separate leaf/compound families and preserves minItems=1 for compounds, while
local validation still requires exact operator arity. Full-schema transport/log
and nonempty-compound regressions each have a production-wire negative control.
All rejected outputs remain logged and uncached; no retry or repair fallback was
introduced. The external delta report retains every live attempt's ledger.

<a id="decision-d8"></a>
D8. A second clean-clone trial returned duplicate commitment ids and stopped,
correctly. Smoke now allows at most three explicitly logged stateless validation
attempts, each with the original inputs plus the rejected output and validation
feedback. Every attempt passes the same budget admission, response logging, local
schema/typed/reference checks and actual accounting. Only accepted outputs enter
cache. Refusal, max_tokens, server/transport errors and engine licensing are never
retried by this mechanism. This supersedes G3/D6/D7's no-retry statement only for
accounted local-validation failures; there is still no hidden SDK retry or license
fallback. Non-smoke defaults to one attempt unless explicitly configured (1–3).

<a id="decision-d9"></a>
D9. Live depth-two search incurred over 60 model records before finishing its
first target. Smoke now uses depth one and eight nodes per polarity to keep the
end-to-end proof small; two targets, the real engine, both polarities, conflict/
forward analysis, draft/audits/web/export and the USD 5 cap remain. Truncation and
OPEN frontiers are logged, never presented as completeness. Normal search bounds
remain depth six / 500 nodes. Integration tests do not weaken their artifact or
analysis assertions; the bounded search policy is explicit in README/config.

<a id="decision-d10"></a>
> Status: Blocked smoke status superseded by [D14](#decision-d14); current fallback configuration is [B11](#decision-b11). This failed receipt remains historical.

D10. Real-provider integration remains blocked at the required essay audit.
Opus 5 returned stop_reason=refusal, category=reasoning_extraction, on both the
original audit prompt and a clarification that compares supplied public artifacts.
Refusals remain logged rejections, without retry or fallback; essay export stays
unavailable. The README explicitly discloses the failed real smoke. The operator
must resolve this provider/model conflict before claiming program completion.
The full graph/draft/log/methodology receipts and accounting are in delta-report.md.

D11. A semantic negative audit is final even when validation correction attempts
are enabled. Only malformed audit responses can be corrected; a valid adverse
assessment must never be retried into approval. The original extra-step test now
enables three attempts and asserts one provider call and no retry event; a
production-wire mutation proves that guard. Writing instructions distinguish
proposition labels from sourced quotations to avoid inventing quotations during
verification. None of these changes bypass the live refusal in D10.

D12. The earlier depth-two diagnostic v8 and the later bounded v9 briefly shared
one cache; v8 refused a divergent concurrent response, preserving the existing
entry rather than overwriting it. This was an integration execution collision,
not a successful smoke. Its actual paid usage is retained in its methodology.
Use one paid writer per cache. Final offline lifecycle proof includes the shipped
placeholder feedback input and subsequent selection/draft/export.


<a id="decision-b9"></a>
> Status: Scalar default routing superseded by [B11](#decision-b11). Retained accounting requirements still apply.

B9 (brain decision, brief 2b). Continue requesting claude-opus-5; enable the
server-side default chain with beta.messages.create, the July 2026 header and
scalar fallbacks="default". Config accepts default/off, default on. Installed
Anthropic SDK 1.12.1 supports this natively; no extra-body workaround is used.
This supersedes D10's no-server-fallback disposition, not bank-only licensing.
Only the private-reasoning-disclosure clause was removed from audit_essay; all
other audit semantics and final-refusal/no-retry behavior remain unchanged.

Record actual response.model, fallback switch blocks and fallback_message usage
iterations. Interpret only content after the final switch; retain all raw content
in the event. Sum iteration tokens and price each named model separately, with
server-tool charges counted once. Ordinary single-model iterations without model
use response.model; missing model provenance in a fallback chain stops accounting.
Unknown model/cache pricing stops loudly with a labelled unknown-spend reservation.
All configured model rates must be finite and nonnegative. Cached calls validate
provenance but charge zero incremental usage. Cache identity includes fallback mode.

Opus 4.8 input/output rates are USD 5/25 per MTok, supplied by B9's reference-price
instruction. No cache rates were supplied for 4.8, so nonzero unpriced cache usage
is an error. Existing web service prices remain operator assumptions. Methodology
lists actual serving models by call kind and explicitly discloses fallback calls.
Admission retains the configured primary-model reservation; the server's default
chain can consume additional billable partial output. Actual whole-chain usage is
checked after each call; a post-call STOP cannot undo an oversized charge.

<a id="decision-d13"></a>
D13. The first clean B9 trial at 191d366 stopped before the audit when a cut
proposal exhausted 4096 output tokens. The partial output was rejected without
retry and its USD 0.835520 measured spend is retained. Smoke now uses the normal
8192 output allowance; the USD 5 and 1,000,000-token caps, requested model, default
fallbacks, audit prompt and all acceptance guards are unchanged. A new clean-clone
trial is required; this configuration change does not turn the failed trial into
a success or enable retries of output-limit stops.

<a id="decision-d14"></a>
D14. A fresh clone at a20e03c completed the real smoke with the unchanged B9
audit prompt, both audits and full export. Its log reports 155636 input tokens,
11211 output tokens and USD 1.058455, with no unknown-spend reservation. All
nine executed call kinds were served by claude-opus-5. Default server fallbacks
were enabled but no hop occurred; no live fallback hop is claimed. The evidence
request completed without a server web-search invocation on placeholder input,
so external-source retrieval remains unexercised. This executed receipt supersedes
D10's blocked status; B9 remains the authorized provider configuration. Failed
trial costs and the full per-kind model account remain in delta-report.md.

Z1. SDK 1.12.1 responses use to_dict(mode="json") at the provider boundary.
A real BetaMessage container expiry and search-result block pass through the
fake transport, ModelCalls, event log and cache. Python-mode mutation fails.

Z2. Post-dispatch serialization, JSON parsing and completion-log failures book the
admitted reservation, replace any unpersisted in-memory actual charge, emit an
incomplete MODEL record, enforce the post-call cap, and STOP without retries.
The raw payload is omitted when it cannot safely be persisted; the prompt and
reservation remain. Fully parsed schema/reference rejections retain their actual
usage and existing bounded correction policy. Unknown accounting refuses resume.
Methodology marks unknown reservations and outstanding dispatches INCOMPLETE.
A persistent storage outage cannot guarantee a new append: the durable call_start
and checkpoint still force refusal; restoring storage/reconciling is required.

<a id="decision-b10"></a>
> Status: Default routing superseded by [B11](#decision-b11); node-only audit input superseded by [B12](#decision-b12).

B10 (brain decision, brief 4). Audit by sentence labelling against outline entries.
The model receives numbered body sentences and node id/text pairs, without graph
internals or bibliography. Remove node markers, split on newline or whitespace
following '.', '!' or '?', trim and discard empty fragments, number from one.
This deliberately simple deterministic rule can split abbreviations; it is not a
linguistic sentence parser. Title and separate bibliography are excluded.
The closed schema permits only sentence number, node_ids and
asserts_unlisted_content per label. Code rejects unknown/duplicate/missing sentence
numbers and unknown ids; computes coverage, missing nodes, extra-content sentences
and faithful; retains exact marker inventory and logs the computed result.
An adverse valid audit or refusal is final, never corrected into approval.
Default server fallbacks remain enabled (B9).

Z3. Sentence labels remain a semantic model assessment. Code catches unknown ids,
missing coverage, flagged additions and missing markers. A false match to a valid
node with an otherwise valid inventory can pass: placeholders Q versus node P
prove this limit offline. Neither marker presence nor computed faithful proves
natural-language equivalence. No semantic guarantee or zero-refusal promise is
made; fresh-clone live outcomes are observed evidence only.


<a id="decision-b11"></a>
B11 (operator decision, brief 4b, 2026-10-10). Keep claude-opus-5 primary and
explicitly request claude-opus-4-8 on refusal. Observed B9 default-mode evidence
across the program: at least four refusals and zero fallback hops; this motivates
replacing default routing, not a claim about all provider behavior. The authorized
array API requires betas=["server-side-fallback-2026-06-01"] and
fallbacks=[{"model": "claude-opus-4-8"}]. Config defaults to
fallbacks: [claude-opus-4-8]; off omits both fields. The old scalar default value
is rejected to prevent silent retention of the non-routing policy. The June
header and list cannot be mixed with the July scalar form (HTTP 400).
Cache identity uses the same explicit/implicit list default. B9 serving-model
provenance, fallback blocks and iterations, per-model pricing, whole-chain cap
checks and methodology disclosure remain. Both models retain configured USD5/25
per million input/output tokens; missing prices still fail explicitly. The API
owns the fallback within one dispatched request; no client retry or alternate
model selection is added. A final chain refusal remains a logged rejection with
no retry. This supersedes B9 default mode and B10's default-routing statement;
it does not change bank-only licensing or computed sentence audit semantics.


<a id="decision-b12"></a>
B12 (brain decision, brief 4c). Writer and auditor receive the same deterministic
essay outline: node propositions (ids only for machine markers/references),
inference links with bank entry names, and answered critical questions with their
slot-filled question text and answers. Status, dialectical cost, frontier, CQ ids
and support bookkeeping, route ids, formulas and raw graph records are excluded.
Assumptions discharged by a link and its scoped results remain expressible logical
relationships, without scope ids. Unknown bank entries are rejected, never renamed
or invented. The writer is instructed not to describe software, the graph or its
bookkeeping and to present the argument conditionally on its premises; OPEN
status/frontier remain in route artifacts, not essay prose.

The audit receives numbered sentences and that same outline, replacing B10's
node-only input. Its boolean is asserts_premise_or_inference_not_in_outline,
replacing asserts_unlisted_content. Transitions asserting neither a premise nor
an inference are not extra steps. Code still validates sentence/node inventories,
computes missing nodes and flagged extra steps, checks machine marker coverage and
computes faithful; valid-id semantic classification remains model-assessed.
Adverse audits and final chain refusals remain final; B11 explicit Opus 4.8
fallback and all usage accounting stay unchanged. Template/schema/input hashes
invalidate previous writer/audit cache entries. Canned responses are regenerated
for this contract, without relaxing acceptance or altering the deterministic engine.


<a id="decision-b13"></a>
> Status: Writer correction attempts/feedback superseded by [R1–R3](#round-2-eta-writer-retries-pilot-python-r1r3-r5r6). Marker/content checks remain.

B13 (brain decision, brief 4d). Writer output is validated before caching or
composition proceeds to the audit. Its body must contain exactly the route's node
marker set (missing or unknown IDs reject); markers in the title or bibliography
do not count. After removing node and citation markers, the body must contain at
least two whitespace-separated tokens that each contain a Unicode letter or
number. Empty, single-token and punctuation-only bodies therefore reject even if
all markers are present. We do not require one sentence per node: one sentence
may express multiple propositions, and the audit still checks their meaning.
This is a structural minimum, not proof that two tokens constitute a useful essay.

Failures are local InvalidOutput results under the existing correction policy:
log/account every attempt, return feedback, admit each correction against budget,
make at most three attempts (or the configured smaller bound), and never cache a
failed writer response as success. Exhaustion follows the normal CLI error exit
with logs, route artifacts and methodology retained, without a final essay.
Accepted drafts still undergo the unchanged final adverse-audit policy. Final
provider refusals and B11 fallback semantics are unchanged. The writer prompt
states the minimum and changes its cache identity; placeholder mock fixtures are
updated to meet it. B13 proof is offline only; no paid calls are authorized and no
new live success is claimed. The historical B12 F9 failure remains in the report.


<a id="round-2-eta-writer-retries-pilot-python-r1r3-r5r6"></a>
## Round 2 eta: writer retries, pilot, Python (R1–R3, R5–R6)

R1. Superseding B13's writer correction policy: write_essay has one initial
attempt plus at most three retries (four total), independent of validation_attempts.
Every locally validated rejection retries the identical rendered inputs, schema,
model and output allowance; no validation_feedback is appended. Invalid responses
are never cached. Each admission and MODEL event carries its attempt number;
rejections retain the failing check and actual token/cost accounting. Each retry
must pass the normal per-call budget reservation. Exhaustion exits 2 through the
normal CLI path, retaining routes/logs/methodology without exporting an essay.

R2. Contentless means the existing B13 coverage/structure checks fail.
essay_min_words adds the lower bound: smoke 150 (target 300), pilot 4500
(target 6000). The ordinary default also uses 4500. Custom configurations must supply
essay_min_words; absence fails instead of silently disabling the minimum. The existing word_count
counts whitespace-delimited title and body tokens, including markers, excluding
bibliography; the same rule serves both bounds. B13 separately excludes markers
when checking substantive text. The writer receives minimum_words and word_limit.
The upper bound remains min(6000, configured essay_word_limit). Over-limit drafts
also retry identically, so all local writer validation failures share one policy.
Changing the minimum or prompt changes the request/cache identity. Offline smoke
fixtures now contain 150 placeholder P tokens, plus title/marker, to exercise the
real configured minimum without introducing substantive content.

R3. Other calls retain validation_attempts (1–3) and correction feedback. An
adverse audit remains final. Client retries do not cover final provider refusal,
transport failure, output-token stops, or incomplete accounting; B11 server
fallback stays unchanged. Accepted drafts still take the existing audit and
verification lifecycle. Originality/quotation validation code is unchanged.

R5. requires-python is >=3.13; uv.lock is regenerated for that supported range,
and installation/full-suite verification uses CPython 3.13.15. No dependency is
added. This supersedes the original >=3.11 repository hygiene statement.

> Status: The profile still requests ten candidates; [Round 13](#round-13-contribution-targets-route-selection-and-frozen-forks) and [Round 14](#round-14-solver-contribution-and-own-thesis-gates) can exclude candidates before search. Ten completed searches are no longer unconditional.

R6. --profile pilot overlays the pilot mapping in config.yaml before constructing
calls and the engine. --smoke remains available and is mutually exclusive. Pilot
uses all 10 targets, depth_cap 6, node_cap 500, forward_pass_depth 2, a 6000-word
limit and 4500-word minimum. There is no target truncation after preparation.
It retains human selection. The pilot's token_cap 10000000 and cost_cap_usd 100
are editable per-run ceilings, not a projected cost or a program-wide guard.
No hard-coded aggregate guard is introduced. A fixture profile with a USD1001
cap accepts simulated usage beyond the former ordinary USD10 default; USD20
stops after the same charge and USD0 refuses admission. Real spend is zero here.

Writer output sizing uses successful historical write_essay MODEL receipts at
/home/dev/wt/ara/wt-fix/runs/{zeta-b12-proof/clone-1,zeta-b11-proof/clone-1,
zeta-b11-proof/clone-2}/runs/real-smoke/events.jsonl. Output tokens / counted words:
654/295 = 2.216949 tokens/word; 629/281 = 2.238434; 594/290 = 2.048276.
These are observed total output tokens divided by the existing word_count,
including any billed thinking and serialization overhead, not a tokenizer
measurement of prose alone. Conservatively round the highest ratio to 2.25:
6000 * 2.25 = 13500; add 2000 tokens for additional JSON/bibliography overhead
and 4500 for length/thinking variability = 20000 output tokens. This is a sizing
assumption from short drafts, not evidence that a 6000-word live draft completed.
The writer-only write_essay_max_output_tokens is used in cache identity, admission,
and dispatch. Other calls retain max_output_tokens 8192. Writer allowances above
8192 use beta.messages.stream with get_final_message and JSON-mode serialization,
preserving fallback parameters and whole-message usage accounting. A stream
failure takes the existing incomplete-accounting STOP path. No live calls were
made for this brief; integrated live smoke receipts belong to the caller.
<a id="round-2-theta-verification-known-cases"></a>
## Round 2 theta — verification known cases

R4. Known-case verification uses recorded real Anthropic responses with requested
and served models, timestamps and SHA-256 request/prompt hashes. CI replays these
responses through ModelCalls, cleanup and export with no network. A separately
opt-in ARA_LIVE_TEST=1 test exercises the real provider and requires web search
usage for every case. The operator explicitly authorizes non-philosophical
software-engineering material for these fixtures; the placeholder rule still
applies to engine propositions and unrelated fixtures. Generated run logs and
exports remain ignored; only the authorized verification recordings are tracked.

R7. Theta's share of the round-2 USD25 ceiling is USD4, enforced over one shared
live event ledger including failed attempts. Test-local settings use one search
per case and a 4096-token output allowance. No profile or configured price changes.
The five cases are separate evidence calls so an item cannot silently lose its
search opportunity to another item. Web-result presence and billed search use
are both checked. The opt-in test can resume its ledger/cache using
ARA_VERIFICATION_RUN; reused evidence retains its original receipt and is marked.

TH1. A verified quotation must match an evidence excerpt exactly, with only
layout whitespace normalized and word boundaries preserved. Prefer the API's
URL-bound cited_text excerpts. The observed live service returns empty citation
arrays despite supplying source quotations and retrieved URLs. In that case,
the classifier returns source_excerpt copied from the search evidence, and code
checks both its presence in that evidence and exact inclusion of the quotation.
An absent, altered or invented excerpt downgrades the item to unverified/remove.
No replacement is generated. Source extraction and attribution remain model
assessments: echoed draft wording in a search narrative is not independent proof
of attribution, even though instructions forbid selecting it. This is not a
source-authenticity guarantee or an exhaustive originality test. The unquoted
Brooks claim must yield possible_overlap and identify its prior source.

TH2. Evidence admission uses the SDK's count_tokens for the initial request plus
model_context_token_bound for each allowed search iteration. Output and tool-use
reservations remain bounded for all iterations. Previously the initial count was
discarded in favor of another full context window, which stopped the fifth test
at USD2.063590 actual spend. Correcting that over-reservation retains the per-search
context bound and the same aggregate USD4 ceiling; actual post-call checks,
unknown-usage STOP and fallback accounting are unchanged. The original stopped
attempt remains in the ledger and report. This estimate still shares the existing
assumptions about context bounds and server iterations; actual usage is recorded.


<a id="round-2-iota-prevent-writer-extrapolation-beyond-supplied-links"></a>
## Round 2 iota: prevent writer extrapolation beyond supplied links

The first integrated five-run series at 07c859a2d428 stopped on run 5: the
writer covered every node and met length, but added a counterfactual inference
outside the selected outline. The audit correctly rejected it before export.
The writer instruction now explicitly excludes inversions, consequences of
denying premises, and unsupported claims about comparative certainty or
reasoning itself. Length must come from explaining/restating supplied content,
not adding inferences. This changes only the producer instruction and its
mock request keys. Audit verdicts remain final, and the four identical-input
writer attempts still apply only to local validation failures. No semantic
compliance guarantee follows from an instruction; a new five-run live series
is required on the repaired commit. Historical failure and all spend remain
in the external iota report.


<a id="round-2-iota-distinguish-malformed-audit-inventory-from-an-adverse-verdict"></a>
## Round 2 iota: distinguish malformed audit inventory from an adverse verdict

Series 2 at bad5af510d56 stopped on its third smoke after the auditor returned
one sentence label for fifteen supplied sentences. This was neither a refusal
nor a complete adverse audit. Inventory mismatches used Rejected, which the
audit boundary reserves for final semantic rejections, incorrectly bypassing
its existing schema-validation correction policy. Missing, duplicate or unknown
sentence numbers now raise ValidationError: the configured bounded attempts
carry validation feedback, reserve again, retain rejected usage and never cache
an incomplete inventory. Complete coverage/extra-step verdict failures, final
provider refusals and output stops remain final. No incomplete audit is accepted
or classified as faithful. Observed failed runs and spend remain in the external
iota report. Four targeted regression cases were red before the repair. A fifth red-first
case preserves finality even when an incomplete inventory flags an extra
inference: such a response stops immediately rather than entering correction.


<a id="round-2-iota-continuation-pilot-output-allowances"></a>
## Round 2 iota continuation: pilot output allowances

The per-kind `<kind>_max_output_tokens` setting generalizes the existing writer
setting. The resolved value reaches cache identity, admission and dispatch.
Every request above 8192 tokens uses the SDK stream/final-message path, retaining
server fallback parameters, JSON serialization and whole-message accounting.
Smoke settings and final rejection behavior are unchanged.

Sizing observations come from the two successful series-3 smoke logs at
278abbf91a56 under /home/dev/wt/ara/iota-live/series-3. These are short-draft
measurements, not pilot completion evidence. Mean draft length was 289.5 words.
Writer visible density was 2.1140 tokens/word plus 72.5 thinking tokens:
6000 * 2.1140 + 72.5 + 2000 serialization margin = 14756.5, fitting the existing
20000 allowance. Retain that larger allowance and its earlier variability margin.

Each audit emitted 0.05181 labels/word at 41 visible tokens/label, no observed
thinking: 6000 * 0.05181 * 41 = 12745.26. Allow 50% variation plus 4000 thinking
and serialization tokens: 23117.89, rounded up to 24000 per audit. This covers
both native audit calls separately, not a combined allowance.

Evidence output averaged 2143 tokens; scaling the entire response with draft
length gives 2143 * 6000 / 289.5 = 44414.51. Add 25% for more sources/items and
8000 for thinking/tool-call text: 63518.14, rounded up to 64000. This is deliberately
more conservative than scaling only with five searches. Admission separately
reserves six possible server iterations: 64000 * (5 + 1) = 384000 output tokens,
SDK-counted initial input plus 5 * 200000 context tokens, and five tool uses.
At configured prices that reserves USD14.65 plus the initial input charge.
The 64000 allowance is per iteration; 384000 is admission, not predicted output.

Classifier output averaged 889 tokens. Draft-proportional extrapolation is
889 * 6000 / 289.5 = 18424.87. Double for item inventory and copied source-excerpt
variation, then add 8000 for thinking/JSON: 44849.74, rounded up to 48000.
Citation/quotation density is not bounded by word count; neither short-draft
ratio guarantees arbitrary inventories fit. An output stop remains final.

Native call-graph inspection finds writer, both audits, evidence acquisition
and citation/originality classification consume the draft. Build-T, target
proposal, cuts, formalisation, leaf mapping, critical-question answers and
repair consume literature or route/search inputs, not draft-length-scaled output;
their existing limits remain. No live pilot is authorized or claimed. Recompute
cost and cap projections from the final five smoke receipts, outside tracked
content. More output headroom increases conservative admission; it is not a
promise that the token/cost caps permit full search-cap exhaustion.


<a id="round-2-iota-leave-counting-margin-below-the-writer-ceiling"></a>
## Round 2 iota: leave counting margin below the writer ceiling

Series 4 at 2e5704f02b84 failed on run 2 after all four identical-input writer
attempts counted 302, 308, 301 and 311 words against the 300-word hard maximum.
The instruction to aim at the exact maximum left no room for counting error,
and did not explicitly say that markers count as whitespace-delimited tokens.
The writer now receives the same counting definition used by validation and
is asked to aim at about 90% of the maximum while honoring the minimum, checking
the complete count before return. This is a topic-neutral production instruction;
no counter, cap, minimum, retry count or audit behavior changes. For the pilot,
that planning margin targets about 5400 words within the unchanged 4500–6000
acceptance interval. Required propositions and markers must remain present.
Fixture request hashes change, response bodies do not. Offline tests cannot
establish instruction compliance; the failed series and its cost remain recorded,
and a new five-run live series on this commit supplies the required evidence.

<a id="round-3-gamma-logged-per-paper-extraction"></a>
## Round 3 gamma: logged per-paper extraction

GX1. Add a native `ara extract` stage and `ModelCalls.extract_paper`, using the
same provider, schema projection/local validator, retry, cache, budget and MODEL
log boundary as other calls. Each selected paper is one request, with up to the
configured validation attempts (extract defaults to three). Refusal, output stop,
transport failure and budget STOP retain existing finality. No extraction failure
is converted into successful model output. Frozen Paper/PageText and
PaperExtraction/ExtractedItem contracts separate intake and accepted output.

<a id="decision-gx2"></a>
> Status: Blank-page/byte refusal policy superseded by [GX9](#decision-gx9); no-OCR intake superseded by [OCR1](#rho2-local-ocr-fallback-at-pdf-intake).

GX2. Choose local pypdf (locked dependency) instead of PDF document upload. This
keeps the existing text-only provider protocol and exact prompt/cache logging,
preserves physical page indices, and permits offline inspection and counting.
The tradeoff is no OCR, image interpretation or layout-faithfulness guarantee.
An encrypted, malformed, empty or partially textless PDF is explicitly unavailable;
even a blank page refuses extraction rather than silently losing source material.
Missing/unreadable PDFs default to a logged `record only, not extracted` outcome;
`--missing refuse` stops without publishing the assembled file. Oversize inputs
use the same explicit unavailable outcome (or strict refusal), never truncation.
Local UTF-8 request bytes plus schema bytes and the output allowance conservatively
bound context; this can refuse a paper that would fit under an exact tokenizer.
The provider token estimate checks context again on every dispatched attempt,
including correction feedback. The configured context bound remains 200000.

GX3. The topic-neutral prompt requests only claims/arguments as stated in one
paper, with author_claim/reported_view/attacked_view labels and inclusive physical
PDF page ranges. Strict schema and local source/page/whitespace checks precede
cache admission. Citation ids are generated as `<id>:pdf:<start>[-<end>]`, explicitly
not printed folios. Build-T accepts only supplied extracted citation ids; record-only
entries cannot license commitments and an entirely record-only input stops before
build-T dispatch. These checks establish structure and source references, not
semantic fidelity, completeness, correctness of attribution or actual support on
a valid page. The model still owns those assessments; no human summary is supplied.

GX4. The assembled `literature.extracted.txt` is SYSTEM/MODEL output. Its sidecar
pins a completed hash-chained extraction-log prefix; CLI intake checks the hash,
reconstructs the file from logged outcomes, and imports original events with
labels/timestamps/costs preserved. The source log must remain available. Later
appends do not invalidate the pinned prefix. AI text is excluded from HUMAN input
events; the operator's command/manifest selections remain HUMAN. Imported usage
counts against the downstream run budget. Methodology discloses receipt import,
extracted/fallback/failed papers, calls/cache replays, models, tokens and cost.
A receipt reused by two runs appears in each methodology; aggregate spend must
deduplicate upstream receipts rather than sum both exports. This extends the
existing log-only exporter without a separate unaccounted intake pipeline.

GX5. Extraction has an additional USD30 configurable cap, subordinate to existing
run cost/token caps (ordinary defaults remain USD10/200000). Both reservation
and actual usage enforce it, including rejected attempts. Planning output before
dispatch uses pages * 1500 tokens/page, prompt overhead and 8192 output tokens per
readable paper, priced from config. This is an assumption, excludes retries and
server fallbacks, and is not admission or a promise of completion. `--estimate-only`
never dispatches; use `--provider mock` for credential-free local estimates.
`--paper-id` restricts the selection. Full-batch execution remains operator-owned.
Generated PDFs, extraction JSON, assembled text, provenance, logs and cache are
ignored. Tests generate placeholder PDFs at runtime; no real source output enters
tracked content. Work is isolated from other live runs in its own checkout/cache.

<a id="round-3-gamma-fix-1-corpus-capacity-lineage-and-pdf-coverage"></a>
## Round 3 gamma fix 1: corpus capacity, lineage and PDF coverage

<a id="decision-gx6"></a>
> Status: Compact item/text limits superseded by [GX12](#decision-gx12). Historical sizing below is not the current contract.

GX6 (B1). A generated build-T literature entry now has at most four extracted
items, each at most 400 characters, enforced by the closed response schema and
prompt. Acceptance also bounds the canonical entry after JSON-string escaping to
2200 UTF-8 bytes. This includes ids, generated page citations, status, text and
partial-coverage notice. Exceeding it retries through normal validation, never
truncates or drops a paper. The prompt requests a concise selection of central
material, including stated argument support, and explicitly disclaims exhaustive
coverage. Full bibliography/checksum/page diagnostics remain in per-paper artifacts
and logs; build-T receives the compact source-id/items/status projection. All
selected papers retain an entry, including record-only and partial outcomes.

For 53 papers, 53 * 2200 = 116600 escaped bytes. UTF-8 bytes conservatively bound
text tokens even for Unicode and JSON escapes. The offline maximum-capacity CLI
fixture measures 124441 input byte-tokens including assembly/instruction/schema
wrappers, topic/audience, the provider's extra schema count, and 32 message-envelope
units: 7841 overhead. With a 64000 build-T output allowance, total is 188441 versus
200000, leaving 11559 (5.8%) headroom. Topic/audience or correction feedback can
exceed this fixture's overhead; the actual full provider count is authoritative on
every dispatch. Different encodings are bounded at acceptance, not assumed to use
four bytes per token. This byte contract bounds produced artifact size; it is not
the rejected byte heuristic for deciding whether an input PDF fits (GX9).

<a id="decision-gx7"></a>
> Status: The compact 212-item sizing scenario is historical; [GX12](#decision-gx12) and [bounded windows](#gx26-bounded-windows-over-immutable-global-evidence) replace its single-batch assumptions.

GX7 (B1). Up to 53 * 4 = 212 source items can each yield a commitment. Allocate
approximately 100 tokens for a 400-character statement, 100 for its bounded-depth
formula, and 50 for id/citation/JSON fields: 212 * 250 = 53000. Add 11000 for
thinking, serialization and formulation variance, giving 64000 output tokens.
`extracted_build_t_max_output_tokens` applies only to generated extraction
literature; ordinary build-T remains at its existing allowance. This is sizing,
not a guarantee that arbitrary formulas or a model's repetitions fit. Output stops
remain final. Both extraction and every build-T request now use provider.estimate
(count_tokens for Anthropic) on the complete prompt and schema, log the count,
and refuse before dispatch if input plus output allowance exceeds context.
No model reduction stage is necessary for the bounded 53-paper input.

GX8 (B2/N1). Choose the smaller fail-closed policy: a cache replay without an
original accepted paid-call receipt earlier in the same source log makes production
accounting incomplete and prevents artifact import with an explicit reason. The
operator must import the original extraction artifact directly; no transitive
origin lookup is invented from cached raw response usage. Replaying a cache still
costs zero new spend, but no longer claims complete production accounting. Same-log
cache replay remains usable when the original receipt is present. Import records
have stable content-derived receipt ids and are idempotent for that receipt in one
log. Methodology separates local and inherited tokens, cost, model calls and human
reported time; aggregate consumers can deduplicate by receipt id. Sum local costs
for new spend; do not sum inherited totals across downstream exports.

<a id="decision-gx9"></a>
GX9 (S1/S2/S3). PDF preflight retains physical numbering and records blank_page
with its page number. A blank page has no text and no image/form/drawing paint
operators. Sparse image or form pages (fewer than 200 non-whitespace text characters)
produce sparse_image_text; other painted textless pages produce
nontext_visual_content. These pages are excluded from model input/citations and
make the paper partial, with affected page numbers/diagnostics in outcomes, logs
and methodology. A fully visual paper remains partial with no items and no model
call. Readable pages still proceed; blank pages alone do not make coverage partial.
Encrypted, empty and all-blank papers have distinct reason codes. Tests exposed
that pypdf ContentStream can be false in a boolean context despite containing paint
operators: inspect presence with `is not None`, then inspect operations. This
preflight is a conservative heuristic, not OCR or a completeness/reading-order
proof; a sufficiently long bad OCR/header layer can evade it.

PDF input bytes now produce only a planning warning. Hard context admission uses
counted tokens, including full correction prompts and schema. A genuine oversize
request logs context refusal and STOP without dispatch, rather than publishing a
record-only artifact based on a byte guess. This supersedes GX2's byte refusal and
blank-page policy; GX4's artifact projection/import rules are superseded by GX6/GX8.
Existing v1 artifacts from before this fix whose projection differs fail closed;
regenerate with the bounded extraction contract rather than stripping provenance.

GX10 (N2). `ara extract --profile extraction` explicitly selects USD30 enclosing
and extraction caps with 6000000 total tokens and at most three validation
attempts. Ordinary USD10/200000 defaults are unchanged. The conditional 1819-page
planning scenario now costs about USD25.23 before retries/fallbacks: 1819 * 1500 +
53 * 2751 = 2874303 estimated input tokens, plus 434176 output tokens at USD5/25
per million. It fits this profile's 3308479 combined-token estimate and USD30 cap,
without guaranteeing retries fit. Preflight explicitly prints and logs
`planned batch exceeds enclosing caps` when either enclosing limit is insufficient.
Downstream pilot retains its existing larger caps and counts inherited extraction
charges; extraction-profile caps are not an authorization to run the batch.


<a id="gamma-round-2-rich-evidence-and-working-t"></a>
## Gamma round 2: rich evidence and working T

<a id="decision-gx12"></a>
GX12 supersedes GX6's compact summary. Rich v2 records preserve individually cited
premises, intermediate/final conclusions, stated inference links, qualifications,
distinctions and attributed reported/attacked views. Inference origin is always
paper_stated; this is source evidence, never a bank license. No per-item text or
item-count ceiling is imposed. 32000 output tokens per extraction call replaces
8192: at roughly 250 tokens per serialized node/link this permits approximately
100 entries plus 7000 tokens for thinking/variance. This is an allowance, not a
completeness proof. Actual live usage belongs in the external round-2 report.

<a id="decision-gx13"></a>
> Status: Complete-review refusal policy superseded by [accepted range union](#mu-addendum-accepted-range-union-and-bounded-review). Open obligations and review failures remain disclosed.

GX13. Count full page requests. Oversize context or exhausted output splits the
physical readable-page range; save each accepted graph unchanged. A counted,
logged reconciliation can add cross-range links referencing immutable ids. It
cannot rewrite/delete range evidence. Refuse a single-page overflow, incomplete
coverage or unresolvable/oversized reconciliation; preserve attempted receipts.
No silent truncation. Source fidelity is still model-assessed, not proved by JSON.

<a id="decision-gx14"></a>
> Status: Single-source refusal/packing assumptions superseded by [bounded windows](#gx26-bounded-windows-over-immutable-global-evidence) and [budgeted closure](#s1-budgeted-prerequisite-depth-before-the-single-freeze).

GX14. Counted deterministic packing uses sorted source IDs/content hashes, plan
version, topic, audience and all capacity inputs in cache identity. Default input
packing is 70000 tokens plus a 16000-symbol reserve and 64000 output within 200000.
Each batch is a ModelCalls request. Model-produced symbol reuse is explicit in
bindings against an accumulated shared catalogue: names/signatures/evidence are
validated, not inferred. Batch dispatch order is deterministic because the shared
catalogue grows; final merge order is independent of completion order. Repeated
formulas and contradictions retain separate evidence ids/citations. No formula
union or implicit aliasing. A single source exceeding the construction allowance
fails explicitly; increase its counted allowance rather than squeeze its evidence.

<a id="decision-gx15"></a>
> Status: Whole-component selection superseded by [GX22](#decision-gx22); hard whole-closure allocation by [S1](#s1-budgeted-prerequisite-depth-before-the-single-freeze), [S2](#s2-soft-construction-shares-and-accounted-window-refusal) and [S5](#s5-initial-share-caps-and-construction-dispatch-configuration).

GX15. The model selects a topic/audience-relevant working T. Every source item is
selected or explicitly omitted with a reason. Bidirectional graph closure prevents
losing a needed premise, stated link or qualification. Attributed source text is
copied exactly and engine formalisation remains model output. The 100000-token
working context budget reserves 8000 wrapper tokens and proportionally allocates
the remainder by evidence count; selection can vary by relevance inside these
explicit allocations. This conservative allocation may refuse a skewed corpus;
raising the counted budget is explicit, never an automatic source summary.
Every model request, cache replay and retry is counted; source context is never
implicitly fetched. Search uses only working T, with full graphs inspectable.
One construction lifecycle, one freeze replaces the one-provider-call reading of
built-once. prepare_commitments owns that freeze and rejects a second freeze.

<a id="decision-gx16"></a>
> Status: No-OCR policy superseded by [OCR1](#rho2-local-ocr-fallback-at-pdf-intake) and [span-confidence policy](#rho2-round-4-synthesized-character-confidence-tau2-f1).

GX16 (R1). Strict missing policy refuses every partial paper, including no-readable
and mixed-readable/visual cases. Default mode keeps explicit partial records.
Private-use glyphs are a visible encoding warning but do not erase otherwise
readable pages; strict mode refuses those too. No OCR or speculative glyph repair.
Legacy v1 artifacts are refused instead of being mislabelled as human literature.
Original log lineage and imported-cost accounting remain required.


GX17. The live provider rejected inference_origin's nullable enum despite its
valid local JSON Schema: the service grammar does not accept enum with a union
of primitive types. Use explicit string-enum and null branches, preserving exactly
the local accepted values. The raw provider request error and conservative unknown
usage reservations remain in ignored live receipts. Add a projection regression
and production schema mutation; do not weaken source validation or discard failed
accounting. Subsequent authorized checks subtract those reservations from the cap.


GX18. The live batch schema exceeded the provider's compiled-grammar limit even
with the existing bounded AST projection. For build_t_batch only, the service
format requests formula ASTs as JSON strings. Runtime decodes each formula and
then applies the unchanged complete local response schema, immutable types,
symbol/citation checks and engine contracts. This removes grammar expansion
without reducing formula depth or accepting unchecked formulas. Raw wire strings
remain in MODEL receipts; validated batch artifacts hold decoded ASTs. Malformed
encoded JSON is a paid validation rejection, not unknown provider accounting.
The live retry uses a 60000-token output ceiling within the remaining authorized
budget after conservatively holding both failed batch reservations.


GX19. Rich working-T formulas require locally bound variables. The solver treats
free variables as global constants, so allowing an unbound variable would bypass
the shared symbol catalogue and could alias unrelated values across batches.
Quantified variables retain lexical scope; global values must be declared constant
symbols with evidence bindings. The new boundary regression was red before the
check, while its quantified control passed. No engine semantics were changed.

GX20 (round-3 stage model). Extraction uses the separately scoped
`stages.extraction` configuration: claude-sonnet-5-5, no fallback, high/adaptive.
Other stages remain on the primary Opus configuration. Requested/served models,
effort and thinking are retained in receipts and cache identity; reservations use
the requested stage rate. Published pricing at
https://platform.claude.com/docs/en/about-claude/pricing was checked 2026-10-21:
Sonnet input/output USD2/10 per million, cache read/5m write/1h write USD0.10/2.50/4.
The prior sample had negligible extraction thinking cost, so this round does not
lower effort speculatively. The two-paper live gate measures acceptance/structure
before any decision to process the corpus. A stage override must not mutate the
primary model or inherit a more expensive fallback silently.

<a id="decision-gx21"></a>
> Status: Mandatory complete reconciliation superseded by [accepted range union](#mu-addendum-accepted-range-union-and-bounded-review).

GX21 (D2-B1). Pending extraction references become stable IDs with originating
range and pages. Reconciliation receives counted original readable pages when
obligations exist, adds only immutable evidence, and returns an exact resolution
inventory mapping each obligation to nonempty accepted evidence/link IDs. Missing
or unknown resolutions refuse complete extraction. The saved graph includes both
obligation and resolution ledgers. This proves explicit obligations cannot vanish;
semantic adequacy of a model's evidence mapping still requires source inspection.
Full-source reconciliation may exceed context and explicitly refuse; no hidden
retrieval, clipping or inferred resolution is introduced.

<a id="decision-gx22"></a>
GX22 (D2-B2/D2-S1, supersedes GX15 whole-component selection). Use the operator's
ALT protocol: model roots/relevance and grouped omission decisions; deterministic
versioned prerequisite closure; then model formalization of exactly that inventory.
The `directional-prerequisites-v1` rule follows a conclusion to every stated link
supporting it, links to premises/conclusion/qualifiers, and any item to applicable
distinctions/qualifications. It never follows premises to other consequences or a
shared qualifier to its other targets. Cycles terminate by visited-ID membership.
Choosing a conclusion with multiple supporting inferences conservatively retains
all its stated support. Root IDs, added IDs, graph hash, rule version and actual
omissions are logged and included in the formalization request/cache identity.
Code copies exact attributed text/citations and derives symbol occurrences;
formulas, definitions and semantic reuse reasons remain model-authored. The new
construction plan is v3; saved rich source remains v2. No previous rejected live
formalization is reused or silently accepted under this changed policy.

GX23 (D2-S2/D2-N1). Persist a response_received receipt with raw response, measured
usage and cost before fallible validation, and write the terminal MODEL accounting
receipt on failure as well as success. Operational post-response failures retain
measured billing and are never cached or frozen. Receipt payloads avoid duplicate
numeric charging. Methodology adds measured/reserved/accounted splits in aggregate,
local, inherited and extraction scopes; existing numeric totals remain explicitly
budget-accounted for compatibility. Campaign accounting still retains unknown
reservations from earlier sibling runs; a new successful log cannot reconcile them.

<a id="decision-gx24"></a>
> Status: Deferred construction patches were introduced in [GX26](#gx26-counted-root-selection-allowance-and-compact-inventory-decisions); whole-source packing changed in [bounded windows](#gx26-bounded-windows-over-immutable-global-evidence).

GX24 (round-3 cost scope). Extraction wire grammar separates inference from node
fields; code supplies only empty structural defaults on non-inference nodes.
The local rich schema remains authoritative. Fixed-inventory formalization removes
model re-emission of exact source text/citations and syntactic bindings. A generic
patch/reuse protocol for invalid formulas is deferred: retaining partly validated
formulas safely requires item-level semantic alignment and receipt/cache lineage,
which is not a cheap variant of generic retry. Live checks use one validation
attempt and stop on the first failed phase as required. No lower output quota or
semantic content pruning is used to fit cost. Whole-source packing and proportional
working allowances still refuse oversized/skewed inputs explicitly. Full extraction
is deferred to Delta's next review per the brain addendum, even if projections fit.


<a id="gx25-kind-specific-extraction-and-bounded-targeted-correction"></a>
## GX25 — Kind-specific extraction and bounded targeted correction

> Status: Per-paper correction policy superseded by [GX30](#gx30-mode-specific-context-requests-and-correction-per-response) and [Kappa acceptance](#kappa-extraction-response-acceptance-and-bounded-correction); paper-stated-only links by [M1](#m1-relaxed-paper-acceptance-with-preserved-evidence).

The extraction provider wire has three disjoint kind families: proposition nodes,
qualification/distinction nodes with applies_to, and inference links with explicit
premise/conclusion/qualification edges. Empty omitted structural fields are filled
before canonical local validation. Invalid supplied relations remain invalid; code
never interprets them as edges. The prompt requires paper-stated inference nodes.
A flat grammar size regression bounds the wire without weakening local guards.

For bounded extraction checks, extraction_targeted_corrections=0 or 1 disables the
generic full-response retry loop. One correction allowance belongs to the entire
paper, including all ranges and reconciliation. A correction returns only changed
or new items, retains every omitted item, rejects unchanged retransmissions, and
revalidates the whole merged graph. It uses the same counted, reserved, logged,
cache-keyed model boundary and extraction stage contract. Malformed or ambiguous
candidate inventories cannot use the patch path. The extraction_require_inference
acceptance setting refuses whole-paper or reconciled graphs with no stated links;
it does not invent a link to satisfy the check. Neither setting changes historical
artifact provenance. The bounded pilot enables both settings; all rejected charges
and raw responses remain in the receipt.

The round-3b live scope is two extraction retries and one construction lifecycle,
using accepted prior evidence if either retry fails. Remaining extraction and
construction allowances are independent; unknown prior usage remains reserved.
The full-corpus phase remains deferred for independent review. Live receipts and
source-model attribution are in the external report, never tracked fixtures.


<a id="gx26-counted-root-selection-allowance-and-compact-inventory-decisions"></a>
## GX26 — Counted root-selection allowance and compact inventory decisions

select_t_roots_max_output_tokens is 16384, independently of the general 8192
allowance. The measured root-selection failure spent 6176 of 8192 output tokens
on thinking. Doubling the allowance leaves 10208 tokens beyond that observed
thinking usage for a complete response and variation; it is a bounded allowance,
not a prediction or completeness guarantee. Existing stage-aware cache identity,
provider request, context admission and monetary reservation all use this value.
High/adaptive stays unchanged; extraction settings and behavior are outside scope.

Root selection v2 emits short root ids and omission decisions keyed by supplied
group ids. A deterministic catalogue maps every item to a short id and partitions
items by source, kind, attribution and speaker. These are metadata groups, not
inferred semantic equivalences. Full source items remain in the counted request;
code never selects relevance or infers an argument grouping. Each omission reason
is model-authored and applies to every non-root member of its group. Unknown or
duplicate groups, unknown roots, blank reasons and incomplete inventories fail.
The catalogue and its graph hash are logged, ids are expanded before the existing
directional closure, and final per-item omissions retain their group reason.
The plan version advances to rich-working-t-v4. Old source artifacts remain valid;
root-selection responses use the new schema and cannot replay under old keys.

construction_targeted_corrections=0 or 1 opts out of generic response regeneration.
One correction allowance per stage is shared across the construction lifecycle.
A parseable, unambiguous rejected candidate can receive keyed replacements or
additions: omission groups for selection, and commitments/symbols/alignments for
formalization. Selection returns its complete short root list and relevance.
All other unchanged entries must be omitted and are retained. No deletion,
truncation recovery, or invention of missing content is performed in code.
Every patch is counted, reserved, logged and keyed normally; the full merged
result must pass the original schema, inventory, symbol and capacity checks.
Malformed inventories and transport stops are not patchable. A remaining token
or dollar allowance is not permission to exceed the configured stage quota.

The bounded live invocation may lower the formalization output ceiling to fit
its independent remaining monetary cap; this is a per-run admission limit, not
a change to the ordinary 64000-token batch allowance. Refusal remains explicit
when the counted reservation cannot fit. The sole freeze still follows accepted
roots, exact-inventory formalization and merge. Full extraction and pilot execution
remain outside this round; live receipts stay in the external report.

<a id="gx25-full-extraction-preflight-and-global-construction-capacity"></a>
### GX25 — Full extraction preflight and global construction capacity

> Status: Correction and inference requirements superseded by [M1](#m1-relaxed-paper-acceptance-with-preserved-evidence) and [range union](#mu-addendum-accepted-range-union-and-bounded-review). Operator-set full-profile caps remain required.

`extraction-full` selects its extraction model in one stage line, disables fallback,
requires stated inference at aggregate acceptance and permits one targeted correction
per paper. All enclosing/extraction caps are unset until the operator supplies them;
profile preflight refuses generation before provider creation. Historical profiles
retain their semantics. Empty readable ranges require a complete, obligation-free,
model-authored disposition persisted with page IDs. Empty root selections must
account for every group and skip formalization; an entirely empty T still refuses.

Working capacity is cumulative and provider-counted, not proportional to input-node
counts. Before formalization the runtime counts exact copied evidence in a minimal
formula envelope and the existing catalogue, reserves configurable symbol growth,
and logs remaining global capacity. These are planning measurements, not a promise
about unknown formulas or symbol reuse. Accepted cumulative T and catalogue are
measured again. Full profile catalogue capacity is 32k, informed by the prior live
10,471-token catalogue; no semantic deduplication is performed to fit it. A preflight
refusal retains root/closure receipts for an explicit subsequent selection decision.

<a id="gx26-bounded-windows-over-immutable-global-evidence"></a>
### GX26 — Bounded windows over immutable global evidence

> Status: Construction windows remain; reconciliation traversal is superseded by [single-pass range union](#mu-addendum-accepted-range-union-and-bounded-review).

Construction plans lossless counted windows within sources. Root inventories cover
only their window, but prerequisite closure uses the complete immutable graph.
Previously formalized exact IDs are reused deterministically. Formalization receives
the remaining fixed inventory and full-closure/prior-ID receipt; a closure exceeding
its counted bound refuses before dispatch. Final global selected/omitted accounting
includes every source item, with preliminary omissions superseded by later closure.
Prior accepted formulas and their immutable source records accompany reused closure
IDs in later counted formalization. There is still one construction lifecycle,
one merge and one freeze.

Reconciliation shares the counted-window partitioner. No-obligation review traverses
every bounded graph window and turns newly discovered gaps into stable obligations.
Each obligation is processed separately against counted source/evidence windows;
every response accounts for it as resolved or explicitly pending. The model can
request a complete next page/evidence set, fetched by immutable IDs and counted
before dispatch. Unknown/unread requests, cycles, request-limit exhaustion or an
oversized required set refuse without silently dropping context or obligations.
Accepted range/window artifacts and the obligation ledger survive refusal. Model
resolution remains a semantic judgment, not a deterministic coverage certificate.

<a id="gx27-unpaid-planning-shares-executions-range-admission"></a>
### GX27 — Unpaid planning shares execution's range admission

`plan-extraction` reads selected PDFs and emits numeric per-paper ranges, input
counts, coverage counts, construction-window scenarios and costs. Its provider
has no generation implementation and its internal generation caps are zero;
operator cap placeholders remain visible in the report. Provider counting is an
explicit option after verifying its free status; local UTF-8 bytes/4 estimates are
labelled separately. Initial extraction and planning share the counted range
partitioner. Full profile output-density planning uses 1200 tokens/readable page
(the prior bounded sample produced approximately 1150 including thinking).

Cost scenarios use counted initial input plus that output density at configured
stage rates. Initial full-output reservations are reported separately. Neither
includes reconciliation, targeted corrections, retries or construction. Estimated
construction windows use 1270 graph tokens/readable page plus an 8000-token window
wrapper reservation; actual immutable graph, relevance closure and symbol growth
must still pass runtime admission. `fits` is a range-size verdict, never approval
of caps, semantic coverage, unread pages, or the complete downstream run.

The full profile is available to both `extract` and native `run`; both preflight
the same unset caps before provider creation. Construction therefore receives its
32k catalogue and targeted policy through the native entrypoint.

<a id="gx28-new-gaps-remain-obligations-throughout-reconciliation"></a>
### GX28 — New gaps remain obligations throughout reconciliation

The model protocol separates `pending_obligation_ids` from structured `new_gaps`.
Every supplied obligation is resolved with accepted evidence IDs or explicitly
pending. New gaps receive runtime-assigned source/window/turn/index identities;
no description matching, merging or fuzzy equivalence occurs, even for identical
text. Coverage cannot be complete while either field is nonempty.

Accepted discoveries and resolutions append to the hash-chained event history.
Immutable range and continuation snapshots retain their obligation inventories;
the final cumulative ledger is written only after the queue drains. Every accepted
continuation queues its new gaps, including responses resolving the current
obligation and responses to earlier discovered gaps. Exhausted windows or existing
context/budget limits refuse extraction with intermediate receipts preserved.
Every continuation uses the counted model boundary. These checks establish exact
inventory accounting, not semantic adequacy of model-selected evidence.

The ambiguous `unresolved_references` wire field is removed, not heuristically
translated. The changed prompt/schema invalidates old response cache keys; saved
v2 literature artifacts keep their existing format and provenance. No prior
artifacts are rewritten, and no paid completion or automatic resume is implied.

<a id="gx29-finite-paper-allowances-cover-every-extraction-continuation"></a>
### GX29 — Finite paper allowances cover every extraction continuation

A paper has one count allowance and one USD allowance at the shared model-call
boundary. Every request after its first counts as a continuation, including
additional initial ranges, subdivision recovery, graph review, ordinary evidence
windows, requested contexts, descendants, validation retries and targeted
corrections. Cache reads consume count allowance with zero new USD reservation.
Free planning/count calls do not consume attempts. Count and monetary admission
precede dispatch; USD admission reserves the full counted next request against
all paper charges, including the initial response, rejected attempts and held
unknown-usage reservations. Measured usage is checked again after its receipt.
Existing stage/run reservation and actual-usage checks remain enforced.

The extraction-full profile sets 24 continuations and USD15 per paper. Papers
with at least 300 physical pages receive 48 continuations and USD30. The saved
free plan's smaller sources require at most four initial ranges plus one estimated
review window: four continuations, leaving twenty under the ordinary count cap.
Their largest full-output scenario is USD5.048850. The 358-page source requires
16 initial ranges plus four estimated review windows: nineteen continuations,
leaving twenty-nine under the large-paper count cap. Its expected-output scenario
with review is USD15.570865; its full-output scenario is USD20.281665, which would
already exceed USD15. USD30 leaves USD9.718335 beyond that scenario. At the full
context bound, a 168k-input/32k-output request reserves about USD1.64 at the pinned
stage rates; dollars can therefore bind before the count ceiling. These are
finite experiment limits, not predictions of semantic completion or permission
to spend. The enclosing profile caps remain unset until supplied by the operator.
Profiles without explicit paper settings also use finite defaults of 24/USD15;
the large-paper override is explicit in extraction-full. Invalid or nonfinite
settings refuse before paper dispatch, including invalid unused overrides.

Paper attempt receipts and source-linked MODEL charges prevent a same-paper
re-entry from resetting its allowance. A different source has its own allowance;
its costs still accumulate in the shared run/stage budgets. A local STOP records
source ID, pending obligation IDs, attempt/continuation counts, measured/held paper
cost and both limits in the event log and partial receipt. Global budget STOPs
inside extraction receive the same paper inventory context. No gap is discarded,
merged by description or marked complete to meet a cap. Earlier immutable evidence
and all raw responses remain available; an unaccepted response is retained as a
receipt rather than retroactively incorporated into the accepted ledger. This
provides bounded refusal, not automatic collection resume or source fidelity.

<a id="gx30-mode-specific-context-requests-and-correction-per-response"></a>
### GX30 — Mode-specific context requests and correction per response

The extraction response schema is now specialized from request inputs at the
single model boundary, shared by rendering, counting, dispatch/cache identity and
local validation. Initial ranges and graph review without obligations cannot
express context_request, pending_obligation_ids or resolutions. Only reconciliation
with supplied obligations exposes those fields. Targeted correction inherits its
original mode. Reconciliation cannot express a no-argument empty_reason disposition.
This removes the observed mismatch where an initial response included an empty-array
context_request object that the prompt forbade and local validation rejected.

Initial ranges report missing cross-range context as new_gaps; runtime assigns
stable obligations and traverses counted source/evidence windows. This retains the
native obligation inventory and complete page-linked graph rather than adding a
second context-fetch lifecycle or discarding requests. A model may still violate
the wire; those responses remain charged, rejected and eligible for correction.
Continuation request emptiness, unread/unknown references, cycle and request-count
checks now run before acceptance, inside targeted recovery. Request keys sort both
sets so reordered lists cannot evade cycle detection. Requested context still goes
through counted admission, and capacity refusal retains obligations.

One configured targeted correction applies to each range/reconciliation response,
not once for the whole paper; this supersedes GX25's per-paper correction statement.
There is no recursive correction. The existing finite paper-wide continuation and
USD allowances still admit every attempt, including corrections, before dispatch.
The observed first-range correction must not consume the recovery opportunity of
a later range while paper allowance remains. Unchanged candidate items are retained,
and the whole merged graph is validated under the original mode's schema.

The corpus policy remains stop-on-paper-failure. A terminal exception records a
failed outcome and an explicit stop receipt listing completed and not-attempted
sources. Methodology exposes that receipt. No completed literature/sidecar is
published, so native pilot provenance import cannot treat the failed corpus as
complete. Bibliographic missing/partial-source policies remain separately explicit.

Automatic partial resume is deferred under the task's small-native-path exception.
There is no native range restore API: legacy range files have no pinned acceptance
hash, an accepted correction receipt holds a patch, reconciliation has no restored
queue/cursor, and provenance assembles every outcome event without attempt selection.
A safe implementation must reconstruct and bind legacy accepted graphs to original
receipts, preserve original and subsequent charges/allowances, restore obligations
and turns, and select final outcomes without erasing failed attempts. Skipping files
or replaying cross-run cache entries does not establish that provenance. Existing
run directories therefore refuse before provider construction with an explicit
resume limitation. Paid accepted evidence is preserved but not automatically reused;
a fresh run can repay that work. No live extraction completion is claimed.


<a id="gx31-disclosed-paper-failures-and-completed-paper-reuse"></a>
### GX31 — Disclosed paper failures and completed-paper reuse

> Status: Three-failure default and stopped-publication policy superseded by [Mu addendum](#mu-addendum-accepted-range-union-and-bounded-review).

Supersedes GX30's stop-on-first-paper-failure policy and its blanket resume
deferral. Range restoration and completed-paper reuse are different scopes.
Restoring a reconciliation queue is unnecessary when a completed, accepted graph
already has a receipt. Rejecting all reuse unnecessarily repays successful work.
The intended result is a usable pilot corpus within the aggregate extraction cap.

Terminal validation/provider-output failures and paper-local allowance/context
stops produce explicit failed outcomes with no evidence, a reason, detail and
original log checkpoint. Extraction continues to the next paper. The configurable
`extraction_max_failed_papers` defaults to 3 globally and in `extraction-full`;
only exceeding it stops publication. Global budget exhaustion, unknown spend and
unexpected operational/configuration errors stop immediately. Failed sources
appear in completed literature and methodology but cannot enter construction or
citations. All-failed literature still cannot construct a working commitment set.

Repeatable `extract --resume-from` imports receipts into a fresh run before budget
construction. Source PDF hash, bibliographic metadata, diagnostics and input hash
bind reusable completed outcomes; older outcomes without an input hash retain
PDF/metadata binding. An accepted merged-graph receipt is required. Completed
papers from stopped runs can be reused. Changed, failed and missing papers need
fresh extraction; conflicting matching completed outcomes refuse. A new batch
selects current outcomes and resets paper-local allowances without resetting
aggregate cost or token totals. Methodology preserves historical failures.

Imports pin the original log path, record count and last hash. New source pins
also verify the append checkpoint. Recursive origin validation detects missing,
modified or truncated ancestors; copied events must match the pinned prefix.
Original events retain timestamps, labels, usage and charges, with event identities
deduplicating overlapping/transitive imports. Native pilot imports use the same
origin-pinned path. Legacy prefix-only callers remain supported and validated.
All original costs are retained, including failed attempts and unrelated papers
in a supplied origin; use origins from the same extraction campaign. These local
hash chains are integrity receipts, not external signatures.

No partial-range restoration, in-place resume, live generation or paid verification
is added. A failed paper may repay its accepted ranges, while completed papers do
not incur another extraction dispatch. Preserve every origin log and checkpoint.
Offline tests and production-wire mutation controls cover native extraction/pilot,
threshold boundaries, evidence exclusion, receipt identity, changed inputs,
transitive tamper detection, allowance reset and inherited aggregate caps.

<a id="gx32-acceptance-bound-reuse-and-a-separate-ancestry-inventory"></a>
### GX32 — Acceptance-bound reuse and a separate ancestry inventory

Iota T-B1 demonstrated that identical source inputs could bypass a newly required
inference through resume. Each newly completed outcome now records a versioned
acceptance identity. Reuse compares the effective inference policy, extraction
model/effort/thinking/fallback settings, provider, prompt hash and schema hash.
The explicit interpretation version covers validation, normalization and schema
specialization changes. Changed or unknown identities return the paper to native
extraction/validation; original model/configuration receipts and charges remain
intact. No legacy policy is inferred from absent metadata. This narrows GX31's
legacy reuse eligibility without invalidating existing literature provenance.

Spending caps, token/output allowances, planning bounds, failure thresholds and
recovery allowances do not define the accepted graph and are excluded. Unrelated
stage changes and overridden global settings do not invalidate an unchanged
effective extraction stage. This prevents unnecessary re-extraction when only
campaign budget or recovery policy changes. The execution boundary rechecks the
identity in case configuration changes after the reuse index was prepared.
Strict source coverage (`--missing refuse`) is checked before the reuse branch,
so a formerly accepted partial paper cannot bypass a stricter source policy.

Iota T-S1 showed that latest-batch publication and reusable ancestry are different
inventories. Resume now indexes all retained verified outcome candidates, then
applies source/acceptance matching and merged-graph receipt validation. An ancestor
success remains available when an intermediate descendant stops before emitting
its reused outcome. Distinct compatible successes for the same source refuse
explicitly. Latest-batch selection remains unchanged for literature and current
failure disclosure; historical failures and inherited charges remain visible.

README documents the required config/root arguments on resume and the shared
pinned-import verifier and outcome selectors for downstream integration. T-N1's
limits remain: whole-paper reuse only, retain original logs, no semantic quality
or full-corpus budget guarantee. No prompt/schema or live provider change is made.


<a id="kappa-extraction-response-acceptance-and-bounded-correction"></a>
## Kappa: extraction response acceptance and bounded correction

> Status: No-discard candidate policy superseded by [v6 quarantine/discard rules](#mu-round-2-grounded-evidence-and-retained-quarantine); correction count by [M1](#m1-relaxed-paper-acceptance-with-preserved-evidence).

- **Native replay boundary.** Extract the existing per-response closure into
  `ModelCalls._extraction_response`, called by both range extraction and
  reconciliation. The offline replay tool uses that same boundary, the original
  source windows, and recorded rejected candidates for patches. It refuses
  tracked inputs, writes only under ignored runs, disables network, and
  deduplicates copied ancestor receipts by event identity. Replay evaluates
  response acceptance; it does not claim successful new corrections, full
  traversal of context requests, completed-paper coverage, or semantic fidelity.
- **Wire shape and normalization.** Keep kind-specific provider alternatives and
  mode-specific reconciliation fields. Add disjoint initial-range alternatives:
  nonempty items permit only absent/null disposition; empty ranges require a
  substantive disposition. Nonempty-candidate patches cannot carry a substantive
  empty disposition, even when their item delta is empty. Optional empty/null
  disposition is the only new normalization and is logged before validation,
  while the raw response stays immutable. Empty attribution is content-bearing
  missing evidence and is never filled, inferred, or normalized away.
- **Cumulative patches.** Repeating an unchanged item is harmless under ID-based
  patch semantics, so remove that rejection. Preserve all omitted items and
  retain additions/changes from a schema- or semantics-rejected patch for the
  next correction. Duplicate or unusable IDs are ambiguous and still refuse;
  no inventory is silently dropped. Each merged candidate undergoes the full
  schema, page, attribution, link, inference, coverage, and obligation checks.
- **Bounded recovery.** Full extraction defaults to two targeted corrections per
  response, configurable to zero or one. Generic retry counts do not multiply
  this allowance. Each correction is logged with its ordinal, candidate hash,
  exact failed constraint, paper bounds and supplied readable pages. Native
  context counting, paper continuation/cost admission and campaign accounting
  apply to every dispatch. Exhausted output retains native subdivision; no
  page locator, source text, attribution, or inference is repaired in code.
- **Reuse.** Bump the acceptance identity to v3 because envelope validation,
  normalization and patch acceptance changed. Old campaign costs remain
  importable, but old completed graphs cannot silently satisfy the new policy.
- **Proof.** Placeholder tests exercise two cumulative patches, repeated unchanged
  items, optional normalization with original receipt retention, wire envelope
  alternatives, semantic refusal, and paper-limit exhaustion. Production-wire
  controls remove each new load-bearing behavior and require a red test followed
  by a restored green test. Real-response and paid evidence belongs only in
  ignored runs and the external execution report. Non-author review follows
  local delivery; no push is authorized here.

- **Provider envelope portability follow-up.** The first live probe at the v2
  acceptance revision returned a provider bad-request exception before a model
  response. The native boundary retained its unknown-usage reservation and
  refused continuation; that accounting is not rewritten or reset. Offline SDK
  transformation then exposed typeless constraint-only envelope branches.
  Materialize those wire alternatives as complete typed, closed objects, retain
  the common root constraints, type the fixed schema-version field, and use an
  explicit nullable union compatible with SDK transformation. Count the expanded
  extraction wire schema during request admission; its larger envelope must not
  be hidden behind the shorter local constraint form. The
  root item constraint still excludes null items from the empty alternative.
  Add an SDK transformation regression and a production-wire mutation. This
  establishes offline schema compatibility, not live service acceptance; the
  provider's detailed error was not retained, and no second paid run is claimed.

<a id="kappa-round-2-explicit-conservative-imports-and-grammar-preflight"></a>
## Kappa round 2: explicit conservative imports and grammar preflight

> Status: Diagnostic text retention superseded by [Kappa round 3](#kappa-round-3-conservative-diagnostics-and-normalized-recovery).

- `extract --unknown-usage-policy count-at-reservation` permits importing
  incomplete receipts only with their full existing reservation counted. It
  appends a reconciliation event naming receipt hashes and the upper-bound sum;
  originals remain immutable and retain `reservation_unknown_actual`. Measured
  totals never include these receipts. Unreceipted dispatches still refuse.
  Methodology says "unknown usage, counted at reservation" and remains marked
  incomplete for actual usage. The default policy still refuses continuation.
- Provider error receipts retain only sanitized HTTP status, error type, message,
  and request ID. They omit exception representations, requests, URLs, credential
  values and structured body echoes. Native CLI counter errors receive the same
  treatment before export or console output.
- `ara schema-preflight --profile extraction-full --run-dir runs/P` enumerates
  all response-shaping modes and correction candidates, deduplicates projected
  wires, and sends each complete grammar through the extraction model/transport.
  Every kind alternative is present in each compiled grammar. The prompt uses
  only placeholders and output allowance is one token; `max_tokens` is acceptable
  here because this gate tests grammar compilation, not graph acceptance. Normal
  extraction validation, caching and stop handling are unchanged. Gate responses
  never populate the extraction cache. Requests retain reservations and receipts
  through the native model boundary; paid errors stop with unknown reservations.
- The gate caps its entire imported history plus new requests at USD1. Re-gates
  must use `--resume-from` for every prior gate attempt; unknown errors require
  the same explicit reconciliation policy. Probe campaign caps are inherited
  accounted charges plus the separately authorized new-spend allowance.

<a id="kappa-round-2-live-grammar-rejection-and-correction"></a>
### Kappa round 2 live grammar rejection and correction

- The first gate's HTTP 400 identified a service constraint absent from the
  local SDK transform: `anyOf` cannot have sibling object constraints. Preserve
  its unknown-usage receipt at the full reservation and import it into re-gates.
- Initial response alternatives now stand alone. The empty alternative uses
  `items: null`, since an empty-only array cannot be expressed with the service's
  supported array constraints. The native boundary logs conversion of that
  content-free null to `[]`, preserves the raw response, and then applies the
  unchanged complete local schema and semantic guards. A nonempty inventory
  still cannot share the empty-disposition wire. No content is inferred or lost.
  The reusable acceptance identity advances to v4 because normalization changed.
- Regression tests assert standalone alternatives, disjoint nonempty/empty wire
  values, and logged null normalization with immutable originals. Two additional
  production-wire controls break the new projection and normalization seams.

<a id="kappa-round-3-conservative-diagnostics-and-normalized-recovery"></a>
## Kappa round 3: conservative diagnostics and normalized recovery

> Status: Two-correction ceiling superseded by [M1](#m1-relaxed-paper-acceptance-with-preserved-evidence). The rejected-gap fidelity limitation remains a historical unresolved claim, not a quality guarantee.

- **F1 diagnostic boundary.** Supersede the round-two substring-scrubbing claim.
  Arbitrary provider prose can contain partial or escaped request echoes and is
  now suppressed, including native CLI token-counter failures. Keep only integer
  HTTP error statuses (400–599), enumerated provider error types, and bounded
  alphanumeric `req_` request IDs. Unknown metadata becomes null. Message text
  survives only the full-string parser for the recognized `anyOf` sibling-schema
  constraint diagnostic; every variable token is an allowlisted schema keyword
  and output is reconstructed canonically. Unknown compiler messages are also
  suppressed until explicitly supported. No prompt knowledge is needed.
- **F2 rejected-candidate recovery.** Re-decoded rejected responses pass through
  the same content-free normalization as validation before ID-based patch merge.
  Original MODEL receipts remain intact; a separate normalization event records
  the correction-candidate phase, attempt and transformations. Null inventory
  with an invalid disposition can reach a valid correction. Initial plus at most
  two corrections remains the limit, with paper/budget limits still enforced.
  Malformed or duplicate item IDs still refuse; normalization does not repair
  substantive content or ambiguous identities.
- **F3 scope decision.** The guarantee is item-inventory preservation across
  corrections and accepted-obligation accounting. It does not retain rejected
  candidates' declared gaps and does not establish semantic fidelity. A patch
  can replace coverage metadata and `new_gaps`, so a rejected gap may disappear
  without an explicit evidence-backed resolution. The requested stronger rule
  exceeds the round-three approximately two-hour scope: stable gap identities
  must exist before acceptance; resolution/dismissal evidence must be defined
  across correction, subdivision and failed ranges; prompts, schemas and
  acceptance identity/reuse need coordinated changes and controls. Leave that
  behavior unchanged under the brief's explicit deferral allowance. A union of
  descriptions alone would strand false discoveries without valid dismissal.
- **Acceptance and proof.** Keep v4: F1 changes diagnostics only; F2 applies the
  existing v4 normalization consistently on a recovery path without changing
  accepted graph validation, prompts, schemas or model policy. Existing accepted
  evidence remains immutable. Adversarial placeholder tests cover dotted paths,
  partial/escaped echoes, invalid metadata and native CLI counter errors;
  extraction regressions cover null recovery, exhaustion and unusable IDs.
  Production-wire controls exercise these boundaries. Wire schemas are unchanged,
  so this round requires offline comparison, not another paid schema gate.

<a id="m1-relaxed-paper-acceptance-with-preserved-evidence"></a>
## M1 — Relaxed paper acceptance with preserved evidence

> Status: Mandatory whole-paper inference review superseded by [accepted range union](#mu-addendum-accepted-range-union-and-bounded-review); evidence eligibility further restricted by [v6 grounding](#mu-round-2-grounded-evidence-and-retained-quarantine).

Acceptance v5 admits disclosed reconstructed inference links. Inference coverage
is a paper-level requirement: zero-link papers require an explicit source-based
no-inference disposition covering all readable pages. Ranges have no link quota;
a counted whole-paper review obtains missing links or the disposition when needed.
Full evidence must fit that review; context overflow refuses rather than truncates.
Dispositions and origins remain in the immutable graph supplied downstream.

Reversed physical page endpoints are ordered and logged before validation; bounds
and unread-page checks still apply. Correction patches may rename repeated IDs
stably without deleting items. Identical repeated definitions keep references to
the first occurrence. A reference to distinct repeated definitions is ambiguous
and refuses rather than guessing. Three targeted corrections are permitted; all
responses and normalizations retain native accounting and original receipts.

The exact reviewed v4 prompt/schema identity may migrate offline under the same
source and extraction profile. Schema, graph references, attribution, physical
citations and obligation closure are revalidated, original outcomes remain v4,
and a separate migration receipt records the v5 check. Unknown identities still
require extraction. This is structural validation, not proof of semantic fidelity.

The offline replay tool explicitly inventories imported grammar-only receipts
and missing provider bodies instead of crashing or treating them as paper graphs.
Production PDF extraction stays unchanged: the separately pinned comparison did
not demonstrate that a replacement improves the affected source passages.

<a id="mu-addendum-accepted-range-union-and-bounded-review"></a>
## Mu addendum — accepted range union and bounded review

Paper acceptance retains the union of validated accepted range graphs. One complete
counted reconciliation request may add evidence; it has no correction, context-fetch
or obligation queue. Admission refusal, invalid output and provider failure retain
accepted evidence and disclose the review failure. Open obligations remain in the
published artifact, methodology and construction inputs. Missing readable pages
make a paper partial; no evidence makes it not extracted. Neither acceptance nor
structural validation establishes semantic completeness or paraphrase fidelity.

A range of at least eight readable pages with at most one item per ten pages
(minimum one) is thin. It receives one re-extraction split into halves, preserving
its original accepted items. Remaining thinness, failed refinements and unavailable
pages are disclosed. Historical refinement receipts prevent repeating that attempt.
Completed legacy graphs remain reusable; a socket-free salvage mode rebuilds accepted
ranges from pinned original receipts and revalidates source text, graph references,
attribution and physical locators. Distinct attempts keep distinct evidence IDs.
No rejected response is promoted by salvage. Historical raw receipts stay unchanged.

The default failed-paper allowance is eight. Cost/token admission still bounds paid
work. A stopped batch publishes its accepted evidence and an explicit failed and
not-extracted roster before returning the original failure. Operators may explicitly
exclude available sources with ID=REASON; exclusions carry no evidence and flow into
construction and methodology. No absent source is represented as extracted.

Thinness is recomputed against all accepted evidence over the range, including
historical review additions, before paying for a retry. Conflicting retained
no-explicit-structure dispositions and overlapping paper-stated inference nodes
are both preserved and explicitly flagged; union acceptance does not adjudicate
the disagreement. Offline salvage never constructs a generation-capable provider.

<a id="mu-round-2-grounded-evidence-and-retained-quarantine"></a>
## Mu round 2: grounded evidence and retained quarantine

Rich-paper acceptance v6 separates the retained range inventory from evidence
eligible for construction. At publication, including offline reuse of pinned v4
and v5 graphs, assess each item's text against only its cited readable physical
pages. NFKC/case folding, alphabetic tokenization, line-end dehyphenation and a
versioned function-word exclusion set precede distinct-token comparison. Require
at least half the item's content tokens and at least three distinct matches (or
all its content tokens when fewer than three exist). This is a conservative
lexical support screen, not entailment or an attribution-truth proof. Real-data
calibration and intentionally selected false-positive checks remain in ignored
run evidence and the external task report; no source content belongs here.

Template prefixes, one/two-character text, text identical to attribution and
nonword text are quarantined independently of overlap. All reference dependents
are quarantined transitively, including inference links constrained by a
quarantined qualifier. Original item bodies and IDs remain unchanged in the
retained inventory; separate `quarantined` records disclose reasons, scores and
blocked IDs. Log every decision. Grounding metadata binds the policy, inventory,
source text and quarantine decisions. Native citation lookup and construction
refuse ungrounded/modified inventories and exclude quarantine. Resolutions using
quarantined evidence no longer close a disclosed gap. Methodology distinguishes
retained counts from grounded counts. Original receipts are never rewritten.

There was no positive filler example or universal nonempty-item quota in the
reviewed prompt/schema. However, rejected-candidate corrections were forbidden
to remove unsupported items, and the displayed local-schema requirements did
not clearly distinguish post-normalization fields from wire omissions. The prompt
also described an empty array where the initial wire grammar requires null; v6
now explicitly explains that null-to-empty normalization. V6 makes
that distinction explicit and permits `discard_items` with an ID and reason,
only for rejected candidates. Unknown/accepted IDs cannot be discarded, a patch
cannot both replace and discard an ID, and all remaining references must still
resolve. An all-discarded no-content candidate can return the empty disposition.
Accepted history is quarantined, never silently deleted. Changing the prompt
is a hypothesis about model behavior; the offline gate is the enforced boundary.

Offline `--salvage-only` can use a verified monotonic paper snapshot, including
thin/partial coverage, without paying for retries. It revalidates grounding on
every retained item. A historical ungated artifact must be republished offline
before it can supply T; schema validity alone is insufficient. No extra anchor
field is added: historical items have no verbatim anchors, and adding one would
not improve their offline check. The changed correction grammar requires the
bounded live schema preflight; it does not authorize new extraction.

<a id="m4-monotonic-snapshot-reuse-and-versioned-gap-publication"></a>
## M4 — Monotonic snapshot reuse and versioned gap publication

> Status: Differing-snapshot refusal superseded by [M5](#m5-completed-snapshot-unions-and-stable-ordinary-reuse). Original identity/receipt preservation remains.

The current acceptance identity remains v6: v5 relaxed structural admission;
v6 additionally restricts evidence eligibility through deterministic quarantine.
Reviewed v4/v5 identities and receipts remain unchanged on reuse. V6 is not a
strict relaxation of v4 evidence eligibility.

Offline salvage may replace a verified completed snapshot only when every
previously accepted item ID and body is retained exactly. A smaller, disjoint or
conflicting inventory refuses explicitly before any provenance import. Growing
snapshots remain reusable; input order cannot silently delete accepted evidence.
Ordinary resume retains its stricter differing-outcome refusal. Grounding and
publication metadata upgrades alone do not create evidence conflicts.

New publication records carry quarantine-aware-v1. Revalidated legacy outcomes
use this marker to disclose dispositions and all unresolved obligations, including
resolutions reopened by quarantined evidence. Methodology uses the same scope.
Unmarked historical outcomes retain their original serialization, so existing
artifact hashes and pinned provenance remain verifiable. Republishing and a
second resume preserve original identities, item bodies and receipts. Current
usage text permits paper-stated or reconstructed links; neither licenses an
engine step. No prompt/schema or grounding-threshold change is made this round.

<a id="search-trace-receipts-version-1-superseded-below"></a>
## Search trace receipts (version 1, superseded below)

> Status: Version-1 production format superseded by [version 2](#search-trace-version-2-and-report-validation). Old logs remain readable.

The engine now emits versioned `search_trace` SYSTEM events through its existing
EventSink: begin, queued state with parent and graph/depth snapshot, visit,
expansion, proposed alternative, rejected alternative, completed route, and end.
A begin receipt scopes search IDs; state IDs are unique within that search.
This preserves best-first order and alternatives without changing route IDs,
licensing, caps, provider behavior or the returned analysis. Missing end means
an interrupted trace, not a completed search. Older decision-only logs cannot
recover state ancestry or unambiguously attach prunes to both polarities.
The extra snapshot receipts increase log size; this is an additive logging patch
that can be cherry-picked independently of the offline report command.

<a id="offline-full-run-report-projection"></a>
## Offline full-run report projection

`ara report` extends the native CLI beside export and reads verified snapshots
without creating a model adapter, re-running the engine or modifying source runs.
It preserves original receipts and artifacts in self-contained HTML/Markdown and
JSON, with nested proof/state trees and local optional DOT-to-SVG rendering.
Missing legacy search ancestry, model summaries, recorded revisions and exact
source links are report gaps, never synthesized evidence. Failed or interrupted
batches retain historical outcomes separately from the current selected roster.

Combined spend deduplicates identical original event receipts across supplied
runs, while local/inherited and measured/reservation totals remain separate.
Current source files cannot establish a historic run's revision. Artifacts have
separate trust labels and cannot override chain records. Existing tail checkpoints
are checked read-only; missing anchors/origins are visible limits, not silent
verification passes. A mismatched available receipt refuses report generation.


<a id="search-trace-version-2-and-report-validation"></a>
## Search trace version 2 and report validation

Round-two review found full graph snapshots amplified the native event writer's
prefix verification cost. The engine now depends on a filesystem-free trace port;
native orchestration supplies append-only per-search JSONL sidecars. Content-addressed
formula, text and proposal definitions accompany node and state deltas. Only completed
routes contain full graphs in the trace. The existing non-trace route artifacts and
analysis contract remain unchanged. Each successful search writes one chained receipt
with relative path, count and SHA-256 after flushing and fsyncing its sidecar. Exceptions
leave unsealed partial files. Chain verification is unchanged.

The offline reader authenticates sidecars before interpreting them. Completeness also
requires supported versions, root/state/node inventories, acyclic recorded parents,
resolved references and terminal route coverage. Legacy receipts stay visible with
validation gaps. State history rendering is iterative and uses explicit links so proof
depth does not bound or overflow state-history rendering. Final proof trees retain their
nested presentation. Original engine decisions remain in the chained appendix; version-2
sidecars carry explicit branch reasons rather than inferred decision associations.

Every available direct origin is pinned and compared before walking its ancestry.
Unavailable transitive ancestors reduce only that scope of verification. Measured
charges require the explicit actual marker; missing/future markers stay unclassified
with their costs, tokens and timeline entries. Unfinalized measured response receipts
remain separate from finalized MODEL charges. Benchmark tooling uses the real EventLog,
all five placeholder cap-scale scenarios, and a read-only base-engine differential.

Completed trace graphs retain every node and edge, with proposition and proposal
payloads referenced through the same interned definitions as state deltas. The
report resolves those references only after authentication and preserves the raw
receipts alongside the expanded terminal graphs. This keeps long repeated premise
text from multiplying across alternative routes; it does not omit any route.

Round-three R1 requires agreement across the authenticated records: a terminal
inference must contain the full selected proposal, each selected child must name
that inference node as its parent at the next depth, and each recorded alternative
must have exactly one matching admission or explicit prune. A sealed but contradictory
or unresolved trace remains partial, with named gaps and all original receipts.
These checks compare recorded evidence without rerunning search or licensing.

<a id="m5-completed-snapshot-unions-and-stable-ordinary-reuse"></a>
## M5 — Completed snapshot unions and stable ordinary reuse

This supersedes M4's differing-snapshot refusal. Acceptance remains v6; the new
completed-snapshot-union-v1 representation separately versions union publication.
Prompts, response schemas and grounding thresholds are unchanged.

Ordinary resume previously skipped completed outcomes with thin-range or missing-
page dispositions. Rebuilding from accepted range receipts then receipt-qualified
native IDs, even when bounded retries were already exhausted and no generation
occurred. Reuse validated completed outcomes directly, including disclosed thin
and partial results. Their limitations persist; resume is not an implicit request
to regenerate accepted papers. Raw accepted ranges remain salvageable when there
is no compatible completed snapshot.

When original verified snapshots differ, retain their union. Deduplication never
uses text similarity or discards distinct original IDs. Nonconflicting IDs receive
a stable union namespace. Conflicting IDs and their dependent reference context,
including incoming inference qualifiers, receive snapshot-qualified namespaces.
Identical referring bodies remain separate when their endpoints or constraints
resolve differently. All citations and graph references map within each source
snapshot. Per-item provenance records the snapshot, original ID, original citation
and original body hash. The snapshot manifest preserves original acceptance
identities, graph hashes and verified origin checkpoints; complete original bodies
remain unchanged in the pinned ancestry.

Obligations and resolutions are snapshot-scoped: resolution in one version never
silently closes an obligation in another. Dispositions retain snapshot identity.
Grounding and dependency quarantine are recomputed over the union; methodology
and literature disclose the resulting gaps and provenance. A derived union is
not another original snapshot. Subsequent resume requires all named originals in
verified ancestry and checks that they reproduce its graph and item provenance.
All origin and graph checks precede destination import.

Best-effort reconciliation already catches counted context overflow, logs the
refusal, accepts the retained ranges and continues to the next paper. Keep one
bounded pass. Splitting would require a new cross-window obligation and evidence
contract and extra calls; it is not a cheap substitute for the complete review.
A native two-paper regression and production-wire control verify continuation.

<a id="m6-snapshot-context-follows-native-prerequisites"></a>
## M6 — Snapshot context follows native prerequisites

M5's inference-only incoming context was incomplete. Union identity now uses the
same prerequisite function as construction: incoming applies_to on every target
kind and inference-to-conclusion relationships count as context. Different
prerequisite inventories or item bodies require snapshot-qualified IDs. Propagate
that separation through both native prerequisites and explicit references until
stable; shared conclusions must not reconnect separated inference contexts.
Preserve all original bodies, pins and mapped references, and recompute grounding
with the existing policy. This changes no prompt, acceptance or grounding rule.

The v1 representation is unchanged. Previously published unions whose graphs and
provenance reproduce remain reusable. A union affected by the earlier defect
fails the existing reconstruction check before import; republish it from its
original snapshot runs. Never accept a stale derived graph as an original.
Native publication regressions compare every original root's exact prerequisite
closure after mapping, for four qualifier target kinds and an added inference,
in both source orders and after a second resume. The production-wire control
replaces native prerequisites with outgoing references and must fail.

<a id="m7-construction-windows-project-metadata-and-imports-append-in-batches"></a>
## M7 — Construction windows project metadata and imports append in batches

Construction plan v6 uses one model-facing projection for counting, selection
and fixed-closure formalization. Each paper window carries source ID, supplied
title/authors (null when absent), a partial-source flag, selected evidence with
unchanged IDs/citations, and only its own provenance and quarantine entries.
Gap entries with item references are filtered to those IDs; otherwise a gap must
overlap a selected item's physical pages and, when scoped, its snapshot. Unscoped
gaps and all full-paper diagnostics, snapshot manifests and grounding receipts
stay in the immutable artifact and imported receipts. The original paper hash
still pins the full source in the plan. The projection changes no selection,
closure, omission, formula or freeze rule; actual requests remain counted.

Receipt import previously re-read and verified the growing destination chain
for every copied event. Import now appends its marker and exact copied events
under one verified destination lock, retaining per-event sequence numbers,
hashes and anchor entries. Both files are flushed and fsynced before return.
An interrupted mismatched append is refused on the next verification; an
incomplete import is still rejected by its declared event count. Nothing is
silently repaired or discarded. Single-event writes use the same append path.
Transitive verification shares a checkpoint memo only within one operation;
there is no persistent cache that could hide later ancestor tampering.

<a id="s1-budgeted-prerequisite-depth-before-the-single-freeze"></a>
## S1 — Budgeted prerequisite depth before the single freeze

> Status: Hard per-window actual-output shares superseded by [S2](#s2-soft-construction-shares-and-accounted-window-refusal) and [S5](#s5-initial-share-caps-and-construction-dispatch-configuration). Depth-cut disclosure remains.

Construction v7 allocates a global selected T before root selection. Its per-window
commitment cap is the minimum of working copy plus formula-growth capacity,
catalogue capacity, and the formalization bound, divided across counted windows.
It measures the copied source envelope, reserves 20% working/catalogue headroom,
and uses at least ceil(10471/45)=233 symbol tokens per commitment from the recorded
paired catalogue count. A lower configured reservation cannot erase that observed
cost. This is a planning assumption, not a guarantee of future model growth.
Actual accepted copy/formula and symbol growth must also fit each window's share;
the prior global and exact-request guards remain authoritative.

Every candidate carries full directional closure item count and a conservative
UTF-8 byte token upper bound on its evidence payload (explicitly not an API count
of the full request). Whole selection and formalization requests retain provider
counts. The model chooses relevant roots against the allocation. Deterministic
breadth/depth expansion retains the deepest complete prerequisite layer that fits
item, payload and counted copy/formalization limits, always closing incoming qualifications/distinctions and
inference endpoints. A minimum root bundle that cannot fit contributes nothing;
code never chooses a different relevant root. Cycles terminate at a fixed point.

Frontier items carry assumed_premise/support_omitted and exact omitted direct
support IDs in their commitment text. Original attributed text and citations
remain intact; the immutable graph is never rewritten. Full omitted inventories,
uncut closure, cut depth and reasons stay in receipts, with compact fixed included
inventory passed to formalization. Methodology exposes the conditional-premise
policy and each omitted-support edge. A later overlap reuses the first accepted
commitment unchanged, including its conservative assumption disclosure; no silent
upgrade is made. Empty windows are logged, but an entirely empty T still refuses.
One construction lifecycle, one merge, one freeze; no engine license changes.

The no-generation plan-construction CLI shares native planning, accepts an explicit
empty audience, and offers local estimates or the provider's free token counter.
Zero spend/token caps and a provider that refuses generation enforce its boundary.
It reports an allocation, not invented relevance choices, formulas or search proof.
Formalization chunking is deferred: bounded inventories retain exact request guards,
and splitting would need dependency-cycle and correction/symbol receipt semantics.


<a id="s2-soft-construction-shares-and-accounted-window-refusal"></a>
## S2 — Soft construction shares and accounted window refusal

> Status: Initial-share growth is now capped by [S5](#s5-initial-share-caps-and-construction-dispatch-configuration).

Construction v8 supersedes S1's hard actual-output window shares. The initial
count-only allocation retains its arithmetic and headroom. Before each window,
count accepted working T and the catalogue again, subtract actual use, and divide
the remaining planned capacity across the remaining windows. Headroom is a soft
target: faithful output may borrow it within hard global working/catalogue and
context bounds. Log accepted borrowing only after validation and accounting.
The next window's allowance reflects that consumption, including unused capacity
released by empty or refused windows. Shares guide selection only: neither the
per-window commitment target nor the headroom-adjusted working share is an
admission bound. Closure admission and depth cuts use recounted remaining global
working and catalogue capacity, counting only newly materialized IDs for growth.
The working envelope includes prior accepted commitments; copied growth and the
formula/catalogue growth reservation must fit the remaining global capacity.
Mandatory qualifiers and inference endpoints remain indivisible; exact request
and context checks and accepted-output bounds remain authoritative. Crossing the
headroom target alone cannot prevent a later fitting closure from contributing.

Selection/formalization refusals and exhausted corrections omit the window with
roots, closure (when available), reason, and evidence IDs retained in receipts.
Invalid selection candidates remain in model-response logs; they do not become
trusted roots. An indivisible oversized input is retained as an oversized window
in the plan and omitted before dispatch. Context admission remains hard for each
initial/correction request, with construction-local refusal scoped to that window.
Campaign caps, unknown spend, provider/counter/logging errors remain fatal; the
skip path does not catch general operational exceptions. Correction allowances
retain their existing lifecycle scope, and no additional retry spending is added.
Refusal receipts have content-addressed names so a new refusal on recount cannot
overwrite a prior accepted artifact.

When measured global working or catalogue capacity reaches zero, omit remaining
windows without dispatch, disclose exhaustion, and return only previously
accepted commitments through the existing merge and single freeze. Recount final
working T, catalogue and downstream context before that freeze. Zero accepted
commitments still fail. An oversized candidate is a window refusal, not evidence
that every future candidate would exceed the remaining global capacity. Partial
construction completion does not guarantee downstream search capacity or success.


<a id="s3-terminal-construction-refusals-and-verified-continuation"></a>
## S3 — Terminal construction refusals and verified continuation

A structured SDK invalid_request_error or request_too_large on construction
selection/formalization (including a correction) is a terminal window refusal.
This includes an error event inside an HTTP-200 stream; it is not an unreceipted
interruption. Retain the full reservation as unknown actual usage, disclose the
count-at-reservation policy, enforce enclosing caps, then omit the window and
continue. Other provider/transport/accounting failures still stop. No unknown
reservation is relabelled measured usage, and no rejected response is cached.
Diagnostics retain only complete allowlisted size sentences and bounded numeric
token counts; arbitrary diagnostic text remains suppressed.

resume-construction operates in the existing stopped run directory under an
exclusive lock and requires explicit --unknown-usage-policy count-at-reservation.
It uses the stored run inputs/configuration and bank version, verifies the event
chain and plan artifact, requires a contiguous prefix of completed windows, and
verifies accepted artifacts against their logged hashes. Skipped artifacts match
their logged omission/closure receipts. It requires a finalized terminal provider
request-rejection receipt for the next window, retains its reservation, and skips
that failed window. Interrupted dispatches without a terminal receipt refuse.
The native planner must reproduce the same plan id before any generation; existing
correction use is restored rather than replenished. Accepted commitments and
symbols restore without model replay or added charges. Normal global recounts,
merge, one nonempty freeze, target/search and awaiting-selection then continue.
Already-frozen runs, artifact corruption and incompatible plans refuse. This is
bounded recovery from a terminal request rejection, not general crash recovery.


<a id="report-overview-and-linked-evidence-round-4"></a>
## Report overview and linked evidence (round 4)

A real multi-run lineage made the original monolithic HTML unusable. Reporting now
separates a bounded HTML overview from full evidence files. The HTML uses a 12 MB
working budget, at most 64 KB per section, and explicit overflow links; the delivery
ceiling is 15 decimal MB. The manifest retains links even when whole sections cannot
fit. Tree previews show three levels and at most 60 nodes, with full counts/depth and
outcomes. JSON traces, route details and DOT retain the complete graph/state history.

Report format v2 stores each canonical original event once by hash. Per-run chain
envelopes reference those bodies; the event index records every occurrence and its
original/imported-by runs. These identity hashes do not replace original chain hashes.
Paper histories/items and full projections are split by run/paper; compact receipt
views point to their shared event bodies. Artifacts are copied separately with their
existing trust labels. HTML/Markdown are bounded navigation views, not raw appendices.
Verification precedes publication and the reporter still makes no provider calls.


<a id="s4-free-counter-refusals-and-non-mutating-resume-previews"></a>
## S4 — Free counter refusals and non-mutating resume previews

A terminal request-specific SDK rejection from the free count endpoint is logged
with kind, request hash, sanitized diagnostic and zero cost. During partition
planning an aggregate refusal causes deterministic splitting. An indivisible or
final window that cannot be counted is represented by null input_tokens and
omitted explicitly; no synthetic token count is persisted as a measurement.
Copy-floor refusals also omit that window. Window-level admission/count refusals
continue to later windows, while global final-envelope checks remain mandatory.
A count refusal before generation produces no MODEL receipt or reservation.
Authentication, rate limits, transport and server failures remain operational
stops. An account-credit denial is also fatal: it is not evidence against any
source window, and skipping every source would conceal the actual blocker.
Only a canonical paraphrase of the recognized account condition is logged.

resume-construction --plan-only requires a separate empty --output-dir. Under the
source resume lock, it verifies the source chain, accepted artifacts and original
plan, then recounts and restores into a new log. Zero spending caps and the
CountingProvider independently forbid generation. The preview counts the next
eligible selection request and reports its index without dispatch, freeze or
source-ledger writes. Original correction use and the same-plan guard still apply;
a refusal that would change the recorded partition or plan cannot authorize an
incompatible resume. The preview is not live construction or downstream success.


<a id="s5-initial-share-caps-and-construction-dispatch-configuration"></a>
## S5 — Initial-share caps and construction dispatch configuration

The first pass caps new commitments from each window at
floor(initial_window_commitments * construction_window_cap_multiplier), default
multiplier 2. The initial share is fixed by the global plan; later empty windows
or changing soft targets never increase this cap. Previously materialized IDs
remain reusable and do not consume a new window's cap. Native prerequisite depth
cutting now also observes this cap, preserving mandatory qualifiers/endpoints and
support_omitted disclosure. A mandatory root bundle above the cap contributes
nothing; code does not invent a relevance ranking to discard roots. A zero initial
share gives a zero cap and explicitly omits the window without generation.

No second redistribution pass is implemented. Such a pass would require another
logged selection/formalization lifecycle across remaining windows; unused capacity
may remain. The cap limits concentration but cannot guarantee relevance, equal
actual contributions, or global token capacity for every later window. Planning
shares remain targets and all actual global/context bounds still apply.

Plan version rich-working-t-v9 includes the cap arithmetic and effective
construction stage configuration. Changing the multiplier or stage model/provider
changes plan identity. A fresh run has no construction resume state, imports only
its pinned extraction provenance, and does not restore another run's accepted
batches. Old plans cannot authorize a capped rebuild; use a new empty run directory.

Config keys stages.select_t_roots, stages.build_t_batch and
stages.construction_correction independently override provider/model and dispatch
settings. Corrections inherit their originating stage before correction overrides.
Profile application preserves other named stages. Scoped ModelCalls views share
the ledger, cache and enclosing Budget but do not mutate the run's active provider.
Counting, reservations, cache identity and requested/served receipts use the chosen
stage; provider changes invalidate cached responses even at the same model name.
The CLI make_provider factory is the registration seam for provider implementations.
The claude_code implementation and live provider proof remain owned by its provider
lane; this change does not implement or execute that backend or edit providers.py.
<a id="xi-round-6-concurrent-search-with-isolated-accounting"></a>
## Xi round 6 — Concurrent search with isolated accounting

> Status: Scheduler-order publication acceptance superseded by [durable ordered journals](#xi-round-7-stable-publication-with-durable-worker-journals).

Runtime schedules each target and its negation as separate native engine jobs,
bounded by positive-integer `search_concurrency` (default 4). Prepared formulas,
frozen T and bank forms are shared immutable inputs. Each job owns its queue,
RNG, licenses and trace. Polarity serials remain 0/1. Results and licenses join
in target/polarity order before native forward and conflict analysis. Target
proposal remains its existing single batch call. Custom EngineAPI adapters keep
their sequential analysis contract.

One acknowledged writer owns event-log reads/appends throughout search and result
publication, retaining the existing chain/checkpoint verification and fsyncs.
Workers own separate sidecars and submit their seals to that writer. On failure,
pending jobs are cancelled and running requests drain before writer shutdown.
Z3 default-context construction, solving and destruction share a solver-only lock;
provider waits are outside it.

ModelCalls uses per-request single flight and local dispatch/receipt state.
Atomic admission includes all outstanding token/cost reservations. Reconciliation
replaces only the corresponding request's provisional or measured charge, never
a snapshot of global totals. Pre-dispatch failures release reservations; unknown
spend retains its reservation charge. Run STOP prevents later paid admission;
already admitted work must finish accounting. Existing paper-scoped construction
recovery remains intact. The provider implementation is unchanged.

Equivalence means identical native results, conflict findings and raw sidecar
bytes for fixed port responses, inputs and engine seeds with sufficient budget.
Wall-clock timestamps, event interleaving and sidecar filenames differ. A live
model is not made deterministic by an engine seed, and near-cap admission may
stop at different requests. At concurrency 4, twenty equal searches need about
five waves instead of twenty: up to 4x on the independent search portion, less
for the complete run because proposal, forward analysis, solver checks, event
verification and provider throttling remain limiting factors. No paid benchmark
is implied by the placeholder equivalence and concurrency controls.

<a id="xi-round-7-stable-publication-with-durable-worker-journals"></a>
## Xi round 7 — Stable publication with durable worker journals

Psi F1 correctly distinguished serialized appends from deterministic publication.
Native searches now write every worker event (including model accounting, engine
decisions and sidecar seals) through the one writer into durable, independently
chained per-job journals. After the pool drains, publication copies complete job
events into the main run chain in input-target order, positive then negative,
retaining within-job order. Results use that same order. UUID filenames, timings,
and model/cache outcomes are not claimed to be identical event bytes.

A main-chain publication-start record identifies every journal before dispatch.
Publication binds each journal and checkpoint by hash and marks completion only
after all jobs publish. Failure paths drain and publish accounted failures in the
same order. A crash or publication error leaves a visible incomplete batch:
Budget refuses new paid admission on reopen and methodology labels main-chain
totals incomplete, directing inspection to the durable journals. This is a
fail-closed boundary, not automatic interrupted-search replay. The round-six
acceptance of scheduler-ordered worker events is superseded by this decision.

<a id="persistent-extraction-lineage-verification-receipts"></a>
## Persistent extraction-lineage verification receipts

Native run startup writes an immutable verification receipt under
cache_dir/lineage-verification after full artifact reconstruction and recursive
origin verification. The receipt records the verifier version and code hashes,
Python version, result, origin pin, event digest, and SHA-256 of the exact bytes
of the artifact, sidecar, and every visited source log and separate anchor.
Referenced paths retain symlink spelling so retargeting remains detectable.
Every source anchor must agree with its entire log, including unpinned suffixes.

Reuse requires matching verifier identity, artifact/origin binding, all input
hashes and the loaded event digest; hashes are checked again after event loading.
A stale, missing or corrupt receipt falls back to full verification. Invalid
lineage refuses before model setup or import. A known extracted artifact cannot
be relabelled as human input by changing its header. Public verification/import
APIs retain full validation; only the validated startup path uses the internal
append helper to avoid verifying the same lineage twice.

Each run chains the full receipt, receipt digest, receipt-log checkpoint and
reuse decision into its own log before importing unchanged original events.
Receipt integrity uses the existing local hash-chain and separate-anchor trust
model, not signatures: jointly rewriting a receipt chain and its anchor is not
cryptographic authentication. Source histories must remain stable during startup;
hash rechecks detect observed changes, not an adversarial change-and-restore
between reads. This cache covers lineage verification and import only, not
construction restoration, planning, generation or search.

<a id="omega-isolated-subscription-cli-provider"></a>
## Omega — Isolated subscription CLI provider

> Status: Temporary credential-copy policy superseded by [fresh host credential reads](#omega-round-9-read-current-host-credentials-and-retry-auth-once); calibration by [round 5](#omega-round-5-measured-calibration-and-scarce-window-allocation) and [round 6](#omega-round-6-comparable-usage-and-local-subscription-admission).

The opt-in `claude_code` provider extends the native ModelCalls seam, with one
fresh process/session and empty cwd/config per request. Native startup preflight
is live, uncached, token-budgeted and logged. User settings, skills, installed
plugins/hooks, MCP and memory are excluded. A canary and debug checks scan a
runtime inventory of forbidden operator names/paths; private configuration can
supplement it. Git identity is read at runtime and rejected in every output,
including cache replays, without echoing the matched value. A fresh config with
only the existing OAuth token in the environment suppressed the account reminder
on CLI 2.1.306. No credentials or operator terms enter committed artifacts.

Round 1's literal ban on all plugins/hooks could not be met by safe mode. The
revised contract accepts Anthropic built-ins, the SDK prefix, runtime environment
and StructuredOutput with disclosure. Full effective prompt equivalence to the
API path is not claimed. `--exclude-dynamic-system-prompt-sections` is ignored
with an explicit system prompt; isolation relies on the fresh configuration,
safe mode and evidence checks instead. Empty ancestor instruction files are
not trusted merely because the cwd itself is empty.

The observed CLI validator rejects the draft-2020-12 metaschema declaration.
Only that declaration is omitted from the CLI argument. Stage constraints and
recursive definitions remain intact; authoritative local validation uses the
original schema. Successful structured tool-use completion is accepted, but
missing structured output, model mismatch and non-success exits are rejected.

Accounting records subscription list-price equivalents separately from API USD.
Subscription dollar caps are inapplicable, while context/token admission remains
mandatory. Local estimation reserves byte-per-token input plus runtime headroom
and two output allowances plus one possible input replay for the two-turn bound. Unknown usage is reserved and
labelled incomplete. Concurrency defaults to four processes per provider;
concurrent token reservations and per-call recovery IDs prevent one request's
failure from charging another request's reservation. Rate/usage retries are
bounded, logged and admitted independently. Original extraction API receipts
remain inherited evidence; this provider does not run extraction or silently
substitute generated text for tool-based web evidence.

Offline fake-executable tests exercise the native process, preflight, receipt,
validation, retry, identity and concurrency boundaries. Production-wire controls
live in the existing sequential integration control runner. Placeholder live
construction, target proposal and formalization passed the local schemas and
native acceptance path; the external omega report records receipts and limits.

<a id="round-7-integration-stage-providers-share-admission-not-billing-policy"></a>
## Round 7 integration — Stage providers share admission, not billing policy

Sigma's construction-stage routing and Omega's subscription backend share Xi's
single reservation ledger. Every request reserves tokens atomically, with zero
API-dollar reservation for a subscription provider. API stage calls remain priced
and subject to USD caps even when the run's default provider is subscription;
subscription stage calls remain zero-USD even under an API default. Imported API
charges remain measured history. Durable response receipts precede settlement,
including validated CLI error receipts. Request-local recovery supersedes both
older log-tail recovery and subscription-only pending counters.

Each new scoped subscription provider must complete its uncached isolation canary
before generation, while count-only planning remains non-generative. Bounded
transport retries use the selected stage provider's settings. Sigma's stage
cache identities, Mu's byte-bound verification receipts and the existing local
schema validation/isolation gates are preserved. Offline mixed-provider tests
exercise both routing directions and the scoped retry/canary boundaries; they
are not a live-provider or full-pilot completion claim.

<a id="omega-round-3-decoded-output-construction-retries-and-config-authentication"></a>
## Omega round 3 — Decoded output, construction retries and config authentication

F6: scan raw CLI stdout/stderr/debug for credentials, then recursively scan every
JSON string value and key before any untrusted CLI field enters a receipt,
log or cache. Nested JSON strings and cache replay receive the same scan.
Reject and evict contaminated cache entries without logging their contents.
Rejected CLI results retain only validated numeric usage/cost and locally
created routing/session data; missing accounting remains explicitly unknown.

F7: both construction_call attempts use the shared transport retry boundary.
Ordinary validation and targeted correction budgets are unchanged; rate/usage
retries spend transport attempts, never additional validation corrections.
Exhausted transport retries surface through the normal Rejected boundary.

F8: prefer a private 0600 copy of only the existing OAuth authentication fields
in each temporary config directory. No token goes in the child environment on
this path. Exclude refresh tokens to prevent child login rotation, and remove
the directory on success, error or timeout. A copy avoids writes through a
symlink/hardlink to the original credential. This brief explicitly authorizes
this temporary authentication-file exception to the repository's general
no-secret-files rule. The receipt label config-link includes this copy mode.
If the credential file is absent and only an environment login exists, retain
the explicitly disclosed env mode. Malformed/unreadable credential files refuse.

The accepted threat model permits same-user access: that user already can read
the original Claude credential file. Credentials never enter argv, logs or
cache; private file permissions protect against other unprivileged users.
Environment-only authentication remains visible to same-user environment
inspection, including ps eww. There is no unconditional "never in ps" claim,
and no protection from root is asserted. Original login refresh remains the
operator's responsibility. Methodology exports the chosen auth mode and policy.

A live canary with the original scope metadata authenticated but was rejected
for operator identity before any stage ran. CLI 2.1.306 fetches profile identity
when profile scope is advertised. The private copy now advertises only the
existing user:inference scope, matching environment-token discovery behavior.
This suppresses profile discovery; it does not narrow the bearer token's actual
server-side permissions. The original credential bytes and scopes are unchanged.


<a id="omega-round-4-context-sizing-and-resolved-construction-dispatch"></a>
## Omega round 4 — Context sizing and resolved construction dispatch

RequestCount separates initial_input_tokens and context_output_tokens from the
aggregate TokenUsage reservation. Construction partitions, working envelopes,
closure copies, catalogue deltas and final acceptance use initial input size.
The call boundary explicitly admits and accounts with reservation, retaining the
CLI two-turn envelope and API web-tool iteration allowance. Count events record
both quantities. Extraction range partitioning also uses initial input size;
its returned usage remains the API reservation for planning/accounting. Free
context checks in reconciliation consume no usage. Downstream context acceptance
uses the count's provider-specific output allowance.

Construction dispatch resolves category, exact-kind and correction settings in
that order and clears nested stages on the scoped configuration. Providers then
receive the resolved model/effort/system/thinking/fallback settings, without
reapplying the original stage over correction settings. Default provider state,
independent stage providers, canaries, transport retries and shared budgets remain
on their native paths. The construction manifest uses the same resolution.

Regression proof uses fake subprocesses and a fake API client, never paid calls.
Real-literature planning remains a capacity projection, not executed relevance,
formalization or proof of all-window contribution. Conservative local byte counts
can produce more windows and lower shares than the historical API token counts;
configured bounds and the computed cap are not relaxed to match that old plan.

The offline real-source replay under unchanged pilot limits has 177 windows,
versus the historical API-count plan's 48. The local estimate budgets 491 copied
input units plus 233 growth units per commitment, with 56,535 working units
available after headroom and wrapper. Its capacity is 78 commitments; divided
among 177 windows, initial share and multiplier-2 cap are zero. Thus the corrected
unit contract does not establish pilot readiness. No bound, cap or estimator was
relaxed to claim contribution; a separate capacity-policy decision is required.


<a id="omega-round-5-measured-calibration-and-scarce-window-allocation"></a>
## Omega round 5 — Measured calibration and scarce-window allocation

The calibration artifact claude-code-input-v1 contains 928 deduplicated API
count pairs: 381 build_t_batch, 453 select_t_roots, 94 propose_targets. Factors
are nearest-rank p99 times 1.05, rounded upward to six decimals: 0.553224,
0.551583 and 0.486932 respectively. Other kinds use the largest factor. CLI
runtime overhead is 949 tokens: 1.05 times the maximum positive residual between
recorded CLI aggregate input (including cache) and calibrated prompt/system/schema
bytes. Eight retained real CLI receipts establish that overhead. Source log and
anchor hashes, event hashes/sequence numbers and content hashes are retained;
source text is excluded. tools/calibrate_claude_code.py verifies native chains
and anchors and rebuilds the table without network or generation.

Planning and admission use the same calibrated initial input. Aggregate two-turn
and output-replay reservations remain separate. This replaces the old byte-per-
token plus 16,384-token envelope, not actual accounting. The table is a measured
forecast, not a universal tokenizer bound; distribution shift and unseen kinds
can exceed it. The API samples are not live CLI measurements of the real corpus.

Every uncached, numerically accounted CLI response, including rejected responses,
records provider_estimate_observation. Compare aggregate CLI input against the
initial estimate as a conservative response to missing per-turn attribution.
Overshoots raise the model/kind factor with 5% margin under a lock; smaller calls
never loosen it. Scoped providers share run state; matching-table observations
restore when a run reopens. Cached output does not train the estimator or change
cache identity. In-flight calls retain their admitted reservations; actual usage
settles the ledger and normal over-budget stops still apply. Unmeasured failures
remain explicitly incomplete, with no fabricated training sample.

When total global slots are positive but below the window count, one-slot shares
go to the earliest windows up to capacity; the remainder receive zero. The plan
records a vector of initial shares and caps, funded-window count and the rule.
Live dispatch skips unfunded windows, divides soft shares among funded remaining
windows, and checks the appropriate fixed per-window cap. Existing global
recounts and closure/mandatory-bundle checks remain authoritative. Allocation
and the multiplier cap permit existing soft borrowing; they do not guarantee
all funded windows contribute.

<a id="xi-round-8-job-local-failure-one-final-retry-and-partial-selection"></a>
## Xi round 8 — Job-local failure, one final retry and partial selection

Native target/polarity jobs no longer cancel the entire queue on a ModelCalls
Rejected/CountRequestRefused result or a local-scope BudgetStop. These are job
failures after the existing transport/validation boundary. The initial queue
drains first; failed jobs are then re-queued once in original order with fresh
engines, preserving immutable inputs and polarity serials without carrying
partially accumulated licenses. Successful results are never rerun. Global
BudgetStop, context exhaustion and unexpected infrastructure exceptions halt
queued work; active requests still drain and publish their durable evidence.
Provider accounting that already requires a run-level stop remains authoritative.

Both attempts share the job's durable journal. Started/failed/finished events
carry attempt numbers; retry events state the bounded policy. Publication still
copies journals in original target/polarity order. The final phase receipt lists
each job as completed, failed or cancelled and retains its attempt count and
failure class. Unsealed failed trace prefixes are retained, never represented as
completed traces. Successful retry traces retain the original search identity.

Missing searches are represented as absent results, not fabricated empty
SearchResults. Completed sibling routes are saved independently. Paired conflict
analysis runs only when both searches completed; an exhausted analysis provider
failure preserves their routes and logs incomplete analysis. A fatal analysis
error stops further analysis but still saves completed search routes before
propagating the run-level error. Partial search does not assert absence of conflict.

The normal run and resume-construction paths reach awaiting_selection after
job-local failures, with partial status in the selection receipt, stderr and
log-derived methodology. The offline report already retains these failure events.
Select accepts the existing explicit unknown-usage policy; its default remains
refusal. Count-at-reservation records unknown spend as upper bounds and keeps
normal admission checks. An all-failed phase has no selectable routes and is
disclosed as partial; no route or completed analysis is invented.

Placeholder regressions exercise native ModelCalls/Engine/provider failure,
transport-before-job retry bounds, queue order, both concurrency settings,
failure recovery/exhaustion, global cancellation, durable accounting and the
native CLI run-to-select-to-compose path. The twenty-search equivalence and
forced-publication-schedule proofs remain required. No live speedup or completed
pilot claim follows from this offline change.

<a id="omega-round-6-comparable-usage-and-local-subscription-admission"></a>
## Omega round 6 — Comparable usage and local subscription admission

> Status: Unknown-exit retry/diagnostic policy superseded by [round 7](#omega-round-7-one-unclassified-retry-and-scrubbed-exit-diagnostics) and [round 8](#omega-round-8-suppress-free-text-cli-diagnostics-kappa2-f1).

Round 5 incorrectly compared aggregate CLI input against initial context. The
pilot's first build_t_batch receipt had 30,294 aggregate input, an initial
estimate of 12,922, and an aggregate reservation of 89,844. That is not an
aggregate underestimate. The correction raised the factor anyway, causing
context refusals. The old regression tested that inflation as desirable and
therefore failed to protect the actual counting contract.

Keep the measured claude-code-input-v1 table and separate 949-token runtime
constant. Version live observation semantics as like-for-like-v2. When the CLI
reports num_turns=1, aggregate input is the first-turn input and can be compared
with initial context. Otherwise compare aggregate input with the aggregate
reservation, including the output-replay allowance. Infer a factor increase
only from excess over the corresponding fixed overhead and replay. Single-turn
canaries can raise fixed runtime overhead separately; multi-turn canaries cannot
identify it and retain the existing measured constant. Both quantities remain
upward-only. Ignore old mismatched observations and imported observations on
restore; retain matching local observations for same-run recovery.

Replaying all 12 pilot formalization receipts under this contract leaves the
factor 0.553224 with zero aggregate overshoots. All 70 planned windows fit; all
54 windows with recorded post-plan formalization requests also fit when recounted.
The pilot actually recorded 42 context skips and 16 closure/selection skips.
This counterfactual does not rerun model choices, assert first-turn measurements
that were never retained, or guarantee successful contribution from every window.

The old provider discarded stderr and CLI failure subtypes. Its two measured
exit-1 receipts cannot distinguish turn exhaustion, schema rejection or an
execution failure. New failure receipts preserve safe enumerated categories and
numeric status/turn metadata. Retry identified transient server/connection errors,
timeouts, max-turn exhaustion and structured-output retry exhaustion on the native
bounded backoff path (default three attempts). Keep schema, request, authentication
and unclassified failures non-retryable. Never retain raw errors or stderr, which
may echo prompts or credentials. New tests distinguish deterministic failure from
transient failure and verify that each attempt is accounted before retry.

The subscription cap governs local run work. Retain used_tokens as total history
plus local usage; identify imported ranges from native provenance markers and
subtract only their token usage for subscription admission and actual-usage stops.
Pending and unknown reservations remain charged. Mixed-provider API calls retain
historical-inclusive admission. Existing methodology local/inherited totals and
new token_cap_policy metadata disclose the distinction; STOP events include total,
local and imported tokens. No log is rewritten, historical receipt discarded,
or API dollar cap changed.


<a id="omega-round-7-one-unclassified-retry-and-scrubbed-exit-diagnostics"></a>
## Omega round 7 — One unclassified retry and scrubbed exit diagnostics

> Status: Free-text diagnostic retention superseded by [round 8](#omega-round-8-suppress-free-text-cli-diagnostics-kappa2-f1).

The operator explicitly permits one retry of an unclassified CLI exit 1. This
supersedes round 6's blanket non-retryable classification for unknown exits.
Mark only exit 1 retryable and enforce a separate one-retry counter inside the
native transport loop, logging unclassified_exit_retry with attempt, delay and
reason. Keep the configured total retry budget and retries=0 authoritative.
Auth, permission, schema, request/context-size, budget and credential/identity
failures remain non-retryable. Other unknown exit statuses do not gain retries.
All attempt accounting and admission run before retry, including explicit unknown
usage reservations; one cheap retry is not evidence that a failure is transient.

Retain sanitized JSON subtype/error category and the first stderr line, bounded
to 200 characters after redaction. Decode two layers of JSON/percent escaping;
suppress remaining encoded text. Remove known credential values, case-insensitive
operator identities, bearer credentials and key/token/password assignments before
truncation. Explicit echo markers or shared prompt/system fragments suppress the
whole line. This conservative rule can hide benign text; it does not claim to
recognize arbitrary paraphrases or novel encodings. Useful non-echo diagnostics
such as a prompt-size error remain available. Subtype and category fields pass
through the same sanitizer. Raw CLI errors and subsequent stderr lines are not
retained. Security rejection retains measured usage and scrubbed metadata without
storing the rejected content, and its receipt states non-retryable.

Offline production-subprocess tests cover repeated failure and recovery after one
retry, disabled retries, other exit codes, malformed receipts with reservation
accounting, auth/request categories, first-line retention, JSON/percent credential
encoding, identity, partial prompt echoes, JSON diagnostic fields and redaction
across the truncation boundary. No live or paid calls are part of round 7. Existing
historical exit-1 causes remain unrecoverable; new metadata helps future diagnosis.


<a id="omega-round-8-suppress-free-text-cli-diagnostics-kappa2-f1"></a>
## Omega round 8 — Suppress free-text CLI diagnostics (kappa2 F1)

Kappa2 reproduced three leaks in the round-7 first-line sanitizer: quoted JSON
token and password assignments absent from the known-secret inventory, and a
short literal prompt echo. This supersedes round 7's diagnostic-retention design.
Delete the sanitizer and retain no stderr/stdout diagnostic text. Recognize
failure categories in memory with a fixed pattern table and numeric statuses;
only fixed enum labels leave that boundary. Preserve JSON subtype only on exact
membership in the known four-value failure-subtype allowlist. Unknown subtypes
are omitted. Receipt exit status and numeric usage/status/turn/byte/time metadata
remain available, along with the existing validated routing fields. Prompt
knowledge is unnecessary for diagnostic suppression. No diagnostic captures or
arbitrary JSON error values reach provider-error or MODEL event receipts.

Keep the round-7 unclassified exit-1 retry bound, deterministic auth/request
refusal, admission and measured/unknown accounting. Transport timeouts expose
only their timeout category and numeric timing; their captured streams are not
retained. Existing credential/identity output rejection remains authoritative.
The three kappa2 subprocess probes now check both native event surfaces, with
additional probes for arbitrary JSON diagnostic fields and recognized-category
projection. Replace controls for removed scrubbing/truncation code with controls
for wholesale text suppression, subtype allowlisting and category enumeration.
No historical log rewriting or live/paid calls are part of round 8.


<a id="omega-round-9-read-current-host-credentials-and-retry-auth-once"></a>
## Omega round 9 — Read current host credentials and retry auth once

Pilot 3 recorded three 401/cli_auth_error receipts after a host credential-file
replacement. Its token values were not compared, so the stale-snapshot cause
remains a supported hypothesis, not a historical proof. The provider did cache
its first authentication read for its lifetime. Remove that state: retain only
the selected credential path and reopen it read-only for each subprocess. Atomic
host replacements are visible without recreating the provider. A selected file
that disappears or becomes malformed fails explicitly instead of falling back
to an old environment token. Environment-only logins remain supported and are
read afresh from this process's environment.

The live reference is the source path, not a writable filesystem symlink to
host credentials. Token values are never cached in provider attributes or copied
to child files. Use the previously authorized environment transport, passing
only the access token for that call. Refresh tokens are never handed to the
child. This supersedes the old private-copy/no-environment preference: a normal
symlink would permit writes/refresh, and the requested no-token-persistence rule
rules out private token copies. Same-user environment visibility remains within
the round-3 threat model; methodology discloses it. The source is opened only for
reading; ARA never refreshes or rotates the credential.

Keep call-local secret values for raw and decoded output scanning so a host
replacement during an in-flight call does not disable its leakage guard. Cache
replay scans current credential values. No token values enter logs, argv, cache,
reports or provider state. Per-call environments and scanners are independent
under provider concurrency.

cli_auth_error is eligible for one bounded retry per transport call, logged as
auth_refresh_retry, after ordinary attempt accounting. The next subprocess reads
the credential source again. The event names re-reading, not credential refresh.
Configured total retries, retries=0, admission, unknown reservations, schema and
request refusal, and the separate one-unclassified-retry cap remain authoritative.
Tests simulate host replacements between calls and after 401, persistent auth
failure, disabled retries, unknown usage, and replacement during an in-flight
call. Controls protect fresh reads, access-token-only handoff and retry bounds.
The authorized live proof is a canary and one placeholder stage call; no API
spending, full pilot restart or credential rotation is authorized.

<a id="omega-round-10-codex-subscription-transport"></a>
## Omega round 10 — Codex subscription transport

> Status: Credential-source and visible-tool policy are specialized by [round 11](#omega-round-11-separate-chatgpt-credential-source) and [round 12](#omega-round-12-visible-generic-definitions-are-not-tool-use); schemas by [round 13](#omega-round-13-strict-codex-schemas-and-pilot-gate).

O10.1. `codex_cli` extends the native ModelCalls/provider seam alongside
`claude_code`. Extraction remains Opus 5 API work; construction/search may pin
an explicit `gpt-*` model per stage. `extract_paper` and web-evidence acquisition
refuse on the subscription transport. Provider errors reuse bounded retry and
reservation/actual accounting, including one credential re-read after auth
failure. Missing ChatGPT auth refuses; an API key is never a fallback.

O10.2. Each request starts Codex CLI 0.163.0 `exec` with `--ephemeral`,
`--ignore-user-config`, `--ignore-rules`, `--skip-git-repo-check`, `--json`,
`--output-schema`, pinned `-m`, read-only sandbox, never approval, disabled web,
MCP, shell, apps, plugins, hooks, memory, goals, multi-agent, images, and plan/input
helpers. Linux bubblewrap is mandatory and hides host home directories, /tmp,
/run and process state. The empty cwd and fresh HOME carry no operator context.
CODEX_HOME starts with only a symlink to a read-only bind of the current auth
file. Its runtime-generated state is isolated in tmpfs and discarded with the
process; making the entire home read-only prevents this CLI from starting.
The source is opened anew per call; scanning and the mount use the same inode,
so atomic host replacements cannot race the credential output scan. No token
copy is written. The CLI refresh URL is set to an unsupported `disabled://`
scheme, preventing credential rotation as well as denying source writes. These
controls are version-specific: another CLI version refuses pending revalidation.

O10.3. Event parsing accepts only known lifecycle, reasoning, final-message and
error events. Nonfatal CLI warning items accompanying a completed turn retain
only a numeric count; terminal errors still reject. Every tool/file/command/web event and unknown event rejects the
response before retention. Error text and reasoning never enter receipts or
cache. Diagnostics carry only fixed categories and validated numeric metadata.
Successful model JSON is scanned for current credentials and runtime git name/
email. The isolation canary additionally scans discovered forbidden names,
including global AGENTS and memory paths. Local schema validation remains
mandatory; the CLI schema is not the acceptance authority.

O10.4. Seed estimates reuse the measured API receipts table and conservatively
retain the prior two-request reservation and runtime overhead. Anthropic and
Codex tokenizers differ: this seed is not a proven Codex bound. Single-turn
Codex input (including cached input exactly once) updates the same run-local,
model/kind-scoped factors upward only. No free counter is claimed. Dollar caps
exclude subscription calls; reported subscription USD equivalent is unavailable,
not measured zero. Codex has no hard output-token flag; configured output sizes
are admission reservations, and actual overages can stop the run afterward.

O10.5. Model IDs from CLI events are checked against the requested pin. When
Codex omits the served model, it remains explicitly `unverified` in receipts and
methodology. The request pin is never fabricated as a serving receipt. Live
subscription isolation, the tool-invitation canary, stage acceptance and any
account-specific model availability require the external Round 10 report's
executed evidence; fake-binary tests alone do not establish them.

<a id="omega-round-11-separate-chatgpt-credential-source"></a>
## Omega round 11 — Separate ChatGPT credential source

> Status: Nonempty generic-tool-name blocker superseded by [round 12](#omega-round-12-visible-generic-definitions-are-not-tool-use). Operator-context and tool-event rejection remain.

O11.1. `codex_cli.auth_file` is mandatory and is configured to the operator's
separate ChatGPT login at `/home/dev/.config/ara/codex-home/auth.json`. A missing
path setting refuses before opening credentials; neither CODEX_HOME nor the
worker's default ~/.codex login is a fallback. Explicit missing/malformed/API-key
credentials continue to refuse. The source is still opened fresh per call and
mounted read-only from that descriptor. No copy, logging, refresh or rotation
is added. Existing fresh-read and bounded-auth-retry tests remain authoritative.

O11.2. Live checks exposed bundled CLI skills despite disabled host discovery.
Disable both bundled skills and their instruction block explicitly. Replace the
coding-agent model instructions with a minimal task-only file in the temporary
read-only mount, retaining stage developer instructions and the native prompt.
The Codex canary now explicitly requests an empty string for absent callable
tools, as it already does for absent operator context. No nonempty canary field
or tool event is waived: the original context and event rejection checks remain.
Live acceptance, account-specific model availability and any remaining blocker
are recorded in the external Round 11 report, not inferred from offline tests.

<a id="omega-round-12-visible-generic-definitions-are-not-tool-use"></a>
## Omega round 12 — Visible generic definitions are not tool use

O12.1. The operator clarified the Codex preflight rule: generic built-in tool
names may be visible, as Claude's StructuredOutput is. The canary still requires
empty skills, memory, AGENTS.md and CLAUDE.md fields, no forbidden-term matches,
no operator identity/credentials, and the unchanged fail-closed event parser.
Any tool event or unknown event rejects the response. The canary reports visible
tool names in its CLI receipt and isolation evidence, exported in methodology;
visibility never authorizes invocation. Task-only model instructions explicitly
forbid all tool use, including file reads, commands, web and delegation.

O12.2. Round 12 live checks pin gpt-6-luna. The CLI reports no trustworthy served
model, so receipts retain unverified rather than inferring it from the pin.
The live canary and two native placeholder stages (formalise and map_leaf)
passed with no tool events. Generic definitions were disclosed, all operator
context checks passed, and the separate 0600 ChatGPT credential file was
unchanged. This supersedes the prior nonempty-tools preflight blocker under
the operator's revised rule; it does not waive any operator-context check.
Full verification and precise live measurements are in the external report.

<a id="rho2-local-ocr-fallback-at-pdf-intake"></a>
## Rho2: local OCR fallback at PDF intake

> Status: Whole-page repair policy superseded by [round 2](#rho2-round-2-clean-token-retention-and-local-vl-second-tier), [span repair](#rho2-round-3-preserve-the-text-layer-and-repair-spans) and [synthesized-character confidence](#rho2-round-4-synthesized-character-confidence-tau2-f1).

OCR1. The normal `extract` and `plan-extraction` CLI paths now default to local
OCR for pages with native glyph, encoding, sparse-image, visual-only or empty
text diagnostics. Healthy text-layer pages remain byte-for-byte unchanged.
`--ocr off` explicitly retains the prior text-only intake, including for reuse
of older extraction artifacts. OCR runs before reuse validation, strict missing
policy, grounding, and model requests; it is not an alternative extraction
pipeline. Genuinely blank pages retain the existing blank-page classification
when OCR finds no usable text. A failed OCR attempt never clears a nonblank
coverage diagnostic. OCR setup/inference errors log their exception class and
abort; there is no implicit download or cloud fallback.

OCR2. Current official sources checked on 2026-10-25 identify PaddleOCR 3.7.0,
PP-OCRv6 (tiny/small/medium), PP-StructureV3, and PaddleOCR-VL-1.6 (0.9B).
Select Baidu's PP-OCRv6 tiny detector and recognizer, PaddleOCR 3.7.0,
PaddlePaddle 3.3.1, PaddleX 3.7.2, and PDFium via pypdfium2 5.14.0 on CPU.
This box has 16 AMD EPYC virtual cores and 62 GiB RAM, without an NVIDIA GPU.
The model cards license both selected weights Apache-2.0; PaddleOCR,
PaddlePaddle and PaddleX code are Apache-2.0. pypdfium2 is Apache-2.0/BSD-3-Clause
with bundled PDFium/dependency notices; retain distribution license files.
The official olmOCR README requires a recent NVIDIA GPU with at least 12 GiB
VRAM for local inference, so it is not an evidenced better fit on this box.
No cross-model accuracy benchmark or academic-formula completeness is claimed.
The upstream OCR metrics use different evaluation sets across generations;
release claims do not establish accuracy on this corpus.

Sources:
- https://github.com/PaddlePaddle/PaddleOCR
- https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/pipeline_usage/OCR.en.md
- https://huggingface.co/PaddlePaddle/PP-OCRv6_tiny_det/tree/d3177d4e5551463292a61e27cfca2b53e7c3fe9d
- https://huggingface.co/PaddlePaddle/PP-OCRv6_tiny_rec/tree/0736086f72f666350ebcdc0c3a504eeac89cdfad
- https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6
- https://github.com/allenai/olmocr#requirements
- https://pypdfium2.readthedocs.io/en/stable/readme.html#licensing

OCR3. Pin Python 3.13.7 and direct dependencies exactly; commit the uv lockfile
for transitive package versions and distribution hashes. PaddleX requires
PyYAML 6.0.2, replacing the former 6.0.3 lock; other existing package versions
are retained. Optional `ocr` dependencies keep ordinary tests lightweight.
`tools/fetch_ocr_models.py` downloads only fixed public model URLs, verifies
archive SHA-256 and every inference/configuration file against the committed
`ocr_models.json`, and stores them in ignored `cache/ocr/`. Intake verifies
those files again and supplies only local paths and rendered arrays to OCR.
It blocks Python socket connections during synchronous initialization/inference.
This guard is scoped to the single-threaded CLI; it is not a general sandbox
for arbitrary native code. The real audit additionally runs inside an isolated
Linux network namespace. No document is sent to an OCR service.

OCR4. Render physical pages at 200 DPI, cap detection at 4000 pixels on the
longest side, use four CPU threads and explicitly
disable MKL-DNN. The accelerated configuration failed the local synthetic probe
with Paddle's `ConvertPirAttribute2RuntimeAttribute` NotImplementedError;
acceleration is not silently retried. Keep every detected recognition line
(score filter zero). Policy `local-ocr-v1` replaces a page only with nonempty
output, character-weighted confidence >= 0.95, <= 5% characters on lines below
0.8 confidence, no private-use/replacement/control characters, >= 98% of the
usable original character count, >= 98% multiset recall of normalized Latin
word tokens, and no loss of original Unicode mathematical-symbol counts.
These are conservative structural admission checks, not calibrated semantic
confidence, reading-order proof, or a guarantee of complete formulas. Unmapped
glyph identities cannot be verified by text comparison. Do not call threshold
recovery a semantic completeness result.

OCR5. Each attempt logs physical page, original diagnostics, selected source,
engine/version, combined locked-model manifest hash, text hashes, metrics,
recognition output, line scores, and elapsed time. Published paper provenance
and hashed model inputs carry deterministic decisions and model identity;
elapsed timing stays only in logs so it cannot invalidate otherwise identical
reuse. Successful OCR text flows through existing citation/grounding contracts.
Strict `--missing refuse` still rejects remaining affected pages. Reuse rejects
changed OCR provenance; an old partial extraction is not relabelled recovered.
Offline tests use synthetic placeholder content and fakes; the local model test
is opt-in. Production-wire mutations must go red, restore, and return green.

CPU selection evidence: medium recognized a dense page in 66.55 seconds with
unscaled detection (47.57 seconds at a 1280-pixel detector cap). Tiny at 1280
pixels took 3.99 seconds but retained only 94.68% of known Latin word tokens;
that configuration is rejected. Tiny at a 4000-pixel cap took 6.16 seconds on
the same physical page, retaining all known Latin word tokens and 99.88% of
usable characters. Choose the tiny CPU variant and require 98% token/character
preservation. This is one-page configuration evidence, not a comparative
accuracy benchmark. The final corpus audit uses only that selected configuration.

<a id="rho2-round-2-clean-token-retention-and-local-vl-second-tier"></a>
## Rho2 Round 2: clean-token retention and local VL second tier

> Status: Whole-page clean-token gate superseded by [span repair](#rho2-round-3-preserve-the-text-layer-and-repair-spans).

OCR6. Policy `local-ocr-v2` compares whole Unicode alphanumeric tokens, including
single-letter tokens and digits, after NFKC normalization and case folding.
Exclude entire whitespace spans with private-use/replacement/control glyphs
before tokenization; never salvage trustworthy-looking fragments from them.
This is an explicit alphanumeric definition, not a dictionary quality claim:
corrupted printable words without detectable bad glyphs may still be references.
LaTeX command names and environment delimiters are markup, not recovered words.
Keep the 0.98 token-recall and character-ratio thresholds, 0.95 confidence floor,
and 0.05 low-confidence character-share ceiling. Keep the old usable-character
denominator even in excluded token spans: removing that floor can admit missing
content. Preserve mathematical symbols actually encoded by the original layer,
including symbols within tainted spans; do not guess private glyph identities.
Recognize an explicit finite set of standard LaTeX symbol spellings as equivalent
Unicode symbols, including Greek letters in clean-token comparisons. This does not certify arbitrary formulas or their structure.

OCR7. Add official PaddleOCR-VL-1.6 (0.9B) as a lazy second tier after rejection
by PP-OCRv6 tiny on affected nonblank pages. Both engines use OCR6's same gate;
healthy and tier-1-accepted pages do not invoke VL. Extraction and planning use
two tiers by default; `--ocr-tiers 1` explicitly retains a single tier and
`--ocr off` retains text-only intake. Each attempt retains its tier, engine,
version, weights hash, policy and deterministic metrics in provenance; timings,
outputs, token/line confidence units, EOS and generation lengths stay in logs.
A final rejection keeps original text and diagnostics. Operational errors abort
with a logged exception class; empty VL output is a logged rejection, not an
operational exception. Strict missing policy and reuse identity remain native.

OCR8. Pin official model revision c5630abae1d940eafe0697512a0325494b02ab42;
`ocr_vl_model.json` locks all tokenizer/configuration files and the 1,917,255,968-byte
safetensors file by SHA-256. Weight SHA-256:
85a479d506a11e724e7285d395c551be69f41dbc16b6342d3cacfb189aed71db.
Combined manifest SHA-256:
99033588ee048347de6cf29b67a9633c173abb92ef4f5ab41eb624f16140d71a.
Use Transformers 5.20.2, PyTorch 2.14.1+cpu, torchvision 0.29.1+cpu and PDFium
5.14.0; exact optional dependency versions and transitive distribution hashes
are in uv.lock. CPU wheels come from the explicit PyTorch CPU index. Download
once with `tools/fetch_ocr_models.py --vl`, verify every file before loading,
use local-only paths with `trust_remote_code=False`, and retain license files.
Model weights and PaddleOCR/Transformers code are Apache-2.0; PyTorch and
torchvision have BSD-3-Clause primary licenses. PyTorch wheels also declare
Apache-2.0, LLVM-exception, BSD-2-Clause, BSL-1.0 and MIT bundled components;
retain their distribution notices. PDFium licensing remains as in OCR2. No paid calls
or OCR document uploads are used. Full document inference is additionally
validated inside an isolated Linux network namespace.

OCR9. Use the model card's Transformers CPU path with BF16, SDPA, eight CPU
threads, 200 DPI rendering, maximum 1,003,520 image pixels, deterministic greedy
`OCR:` generation, KV cache and maximum 4096 new tokens. The official example
supports element recognition/text spotting, not the full layout pipeline.
Applying it to a complete physical page does not establish complete layout
recovery. A CPU probe took 64.91 seconds for one page; a four-thread probe took
81.07 seconds, so retain eight threads and audit all remaining pages. Timings
are workload measurements, not a dedicated-host throughput guarantee.
VL confidence is the actual generated-token softmax probability weighted by
non-special decoded token character count; it is not PP-OCR recognition-line
confidence or a calibrated probability of correctness. Enforce the same numeric
thresholds and reject output that ends at the generation cap without EOS.
High confidence, complete generation, and structural retention still cannot
prove semantics, reading order, or meaning of unencoded symbols.

Official source: https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6/tree/c5630abae1d940eafe0697512a0325494b02ab42


<a id="rho2-round-3-preserve-the-text-layer-and-repair-spans"></a>
## Rho2 Round 3: preserve the text layer and repair spans

> Status: Span-confidence denominator superseded by [round 4](#rho2-round-4-synthesized-character-confidence-tau2-f1).

OCR10. Policy `local-ocr-v3-spans` replaces only tainted whitespace runs, retaining
all surrounding text and whitespace exactly. Align one to three adjacent clean
alphanumeric tokens on both sides, longest first, using NFKC/casefold token
comparison and requiring a unique occurrence of each anchor in both sequences.
Never anchor to fragments inside a tainted run. Adjacent damaged runs share outer
anchors; accept an interior positional alignment only with equal run counts.
Otherwise keep each unresolved span flagged. Tier 2 uses original coordinates
and cannot overwrite a tier-1 accepted span. Nonempty clean text with visual-only
warnings remains unchanged; only textless pages retain whole-page OCR admission.

OCR11. Inserted-character confidence must be >=0.95 with <=5% below 0.8. Use
covering tier-1 line scores or actual VL token-to-character ranges, not a page
mean. Tokenizer byte fragments can rewrite prior characters; use prefix decoding
and the minimum contributing score then. Missing confidence coverage, truncated
generation, empty/bad-glyph output and lost originally encoded math symbols
refuse. Log each attempted span's engine, confidence, unique-anchor evidence,
source/OCR character ranges and before/after Unicode categories. Keep diagnostics
until every damaged span is repaired and no other page diagnostic remains.
Partial repairs remain available with their provenance and original physical page.

OCR12. Keep the pinned model/dependency set and 4096-token cap, but retry capped
VL pages in three nonoverlapping horizontal regions, selecting nearest low-ink
rows around thirds. Record the capped attempt and all region outputs, scores,
geometry and durations; require EOS for every tile. On the two prior capped
physical pages, tiled generation completed in 84.60s and 105.65s. This establishes
completion, not layout or formula correctness. All inference remains local.

OCR13. Round-2 excluded-span arithmetic subtracted a normalized clean-token count
from an unnormalized whitespace count. U+00B4 expands to a leading space under
NFKC, undercounting one affected page. Count literal tainted runs directly: the
82-page cohort has 678 damaged runs, not the prior reported 677. The external
Round 3 report preserves this correction and distinguishes the brief's historical
reference denominator from measured counts. No paper content is tracked.


OCR14. Terminal visual inspection found a confident candidate changing a clean
uppercase character attached to a damaged delimiter. Require each candidate to
match the exact literal clean fragments inside its tainted run, with nonempty
replacement text only where damaged glyph runs occurred. This preserves case
and punctuation inside spans as well as all surrounding clean intervals. Three
regressions failed before this fix. Reuse inference, replay the final policy,
and rerun the full suite and controls; the interrupted pre-fix suite/audit are
not final evidence. Confidence and EOS alone cannot certify exact transcription.


<a id="rho2-round-4-synthesized-character-confidence-tau2-f1"></a>
## Rho2 Round 4: synthesized-character confidence (tau2-F1)

OCR15. Policy `local-ocr-v4-spans` computes admission confidence and the share
below 0.8 only over newly synthesized non-whitespace characters corresponding
to damaged glyph groups. Preserved clean fragments are source text, not new
recognition evidence; they must not dilute uncertainty in a replacement.
The numeric mean threshold 0.95 and low-score-share ceiling 0.05 are unchanged.

OCR16. Count complete exact clean-fragment alignments with dynamic programming,
saturating at two. Literal clean groups consume themselves; damaged glyph groups
consume one or more OCR characters. Require exactly one full alignment before
scoring; zero refuses changed clean fragments, and multiple alignments refuse
ambiguous boundaries. Prefix sums avoid enumerating wildcard paths. Log the
alignment count, confidence scope and absolute synthesized-character ranges.
The external clean-token anchors, physical pages, partial diagnostics and
cross-tier preservation rules remain unchanged.

OCR17. Rebase the local OCR branch onto requested main 7e5219a, retaining both
Omega's and Rho2's appended DECISIONS sections. No provider or credential action
is authorized by this repair. Tests, existing local model checks and mutation
runners execute offline; all source is restored after controls. The low-score
replacement regressions (0.10 and 0.94), high-score acceptance with unscored clean
text, ambiguous internal alignment and two separated glyph groups failed before
the fix. Dedicated confidence-dilution and ambiguity mutation controls protect
this admission boundary. See the external Round 4 report for final evidence.

<a id="omega-round-13-strict-codex-schemas-and-pilot-gate"></a>
## Omega round 13 — Strict Codex schemas and pilot gate

O13.1. `ara-openai-strict-v1` projects the native stage schema to a conservative
OpenAI strict vocabulary. Every object is closed, every property required,
and optional fields permit a null sentinel. Local references and recursive
unions remain; const becomes a singleton enum, oneOf becomes anyOf. Constraints
outside the wire vocabulary (including uniqueness, bounds and conditionals)
remain in the original schema shown in the native prompt and enforced locally.
Only optional nulls disallowed by the native child schema are removed before
local validation. Required nulls, native nullable values and unknown fields
are preserved for that validation. Raw receipts/cache retain the wire response;
normalization happens after accounting, including on cache replay. Projection
version is in cache identity and methodology; native/wire hashes are in receipts.
Admission and calibration use the projected schema size.

O13.2. `ara codex-schema-preflight --config PATH --run-dir DIR` invokes every
Codex-routed stage schema with a locally checked placeholder witness, including
both construction correction routes. All 12 stage schemas / 14 routing cases
must return complete JSON that passes original-schema validation. The preflight
has no cache hits and retains native accounting and isolation checks. Extraction
is API-only; web retrieval has no JSON schema and remains refused by Codex.
No grammar preflight proves a complete pilot, semantic quality or web retrieval.

O13.3. Before run, construction resume or writing selection, the CLI requires
`codex_cli.schema_preflight_log` to name a successful native preflight event log.
The gate verifies the hash chain and tail checkpoint, exact current manifest
(schema hashes, projection/CLI versions, model, effort and system-prompt hash),
and one accepted, measured, uncached Codex receipt for every case. Missing,
partial or stale evidence refuses before provider creation. Regenerate proof
after changing those settings. The preflight itself is exempt from this gate;
it still runs the mandatory isolation canary before stage calls. Served model
identity remains unverified when the CLI does not report it.

O13.4. Existing runs may supply fresh proof using
`--codex-schema-preflight-log` on resume-construction or select. This overrides
only the proof location, is logged in the human command, and leaves historical
configuration intact. The same manifest and receipt checks still apply.

<a id="round-9-xi-stopped-search-recovery"></a>
## Round 9 — Xi: stopped search recovery

R9.1. `ara resume-search --run-dir DIR` recovers the existing native lifecycle.
Before canonical publication or provider construction it verifies the main
chain/tail anchor, exactly one run configuration/freeze/candidate inventory,
the immutable T artifact hash, bank/config identity, ordered job goals, journal
chains/anchors, and the hashes, identities and structural integrity of sealed
trace sidecars. Recovery uses local artifacts; it does not borrow a missing
trace from the original directory when operating on a copy. A nonblocking
per-run lock excludes concurrent recovery commands. Missing or conflicting
evidence refuses explicitly.

R9.2. Publication retains original event bodies in input/polarity order using
the existing publication markers. Verified copied prefixes and completed
publication markers are deduplicated. A continuation receipt identifies the
remaining offset after an interrupted publication. Failed jobs' historical
usage is published too. A measured response without a final MODEL event gets
one incomplete MODEL settlement, linked by call ID and receipt hash. Its
usage must match the raw provider receipt. Repeating recovery neither imports
the same events twice nor settles a call twice. A dispatch without a measured
receipt is refused; no spend estimate is silently presented as actual usage.

R9.3. Completed SearchResults come from sealed terminal graphs. Accepted
formula receipts recheck the recorded proposal licenses locally, including
licensed proposals pruned by node caps; recovery does not rerun a completed
search or call a provider to restore licenses. Restored jobs enter the native
scheduler as completed, while unfinished/failed jobs retain the normal bounded
retry and stop behavior. The ordinary paired-analysis, route persistence and
`awaiting_selection` paths remain the delivery mechanism. A sealed search is
also reusable if a halt interrupted its final job-finished marker.

R9.4. `--stop-before-dispatch` performs real publication and accounting recovery
and prints the remaining job indices, then exits before provider creation.
The offline proof uses a byte-preserving copy of the stopped pilot and a
provider factory that fails if invoked. The original run remains unchanged.
The copied run restores 19 completed jobs, schedules only index 7, and imports
20 journals including that unfinished job's historical usage. A repeated
recovery reports the same plan. Evidence is retained under ignored
`runs/xi-round9/`; no source material or run artifacts enter the commit.

R9.5. Remaining limits: the real-run proof stops before dispatch, so live
completion and the separately owned validation repair are not claimed. A
missing journal without a recorded empty publication cannot establish whether
paid work completed; recovery refuses rather than repaying it. These two
findings are placed here: 2 findings, 2 placed.

R9.6. Verification: placeholder tests cover publication/accounting idempotence,
partial publication, frozen-T/target/journal/trace mismatches, missing measured
receipts, license preservation, recovery locking, and native completion with
only the unfinished job dispatched. Six production-wire mutations exercise
frozen T verification, target identity, seal identity, measured settlement,
completed-job dispatch exclusion and restored license inventory. Final suite
and control counts are recorded below after the sequential checkpoint.

R9.7. Executed offline accounting audit: the copied pilot has 166 commitments
and 10 targets. Nineteen completed jobs are restored and only job 7 remains.
The imported search usage totals 2,452,008 tokens. One measured settlement adds
8,373 input and 828 output tokens, with recorded subscription cost USD 0;
this is measured usage, not a claim that subscription capacity is free. Exact
MODEL-event multiplicities match the original main log plus all journal receipts
and this one settlement. Two recoveries produce identical plans, with zero new
dispatches. The original artifact inventory remains byte-for-byte unchanged.

R9.8. Full `uv run pytest -q`: 1,018 passed, 4 skipped (1,022 collected), in
537.26 seconds. The skips are the two opt-in paid-provider checks and the two
opt-in local OCR/VL model checks. No paid calls were made.

R9.9. After the full suite completed, `uv run python
tests/integration/negative_controls.py` exercised all 426 production-wire
mutations sequentially: 426 expected failures, 426 restored passes. This
includes all six new search-resume controls. `git diff --check` is clean.
The final handoff is a local commit on `feat/run-report`; no push or paid
provider call was performed.


<a id="s6-native-schema-authority-with-bounded-local-validation"></a>
## S6 — Native schema authority with bounded local validation

Recursive formula alternatives have unique required `op` tags. Local validation
selects that single native branch and delegates every constraint in it to Draft
2020-12; overlapping or optional tags retain ordinary union semantics. Schemas,
provider projections and formula operators are unchanged. An iterative precheck
reads the native branch constraints for node kinds, required fields, arity and
symbol/term reference shape. It rejects malformed formulas before recursive
jsonschema evaluation. Names remain subject to the existing catalogue checks;
this does not introduce a new closed vocabulary or prohibit free variables.

All runtime jsonschema entrypoints, including Codex normalization, correction
merges, recorded extraction, migration and isolation canaries, use bounded local
validation. JSON values are limited by `local_validation_max_depth` (64, root at
0) and `local_validation_max_nodes` (100000). Each schema validation or Codex
normalization operation has `local_validation_timeout_seconds` (2 seconds), using
a killable child interpreter, including when called from parallel search threads.
Timeout children are killed and reaped. Native response refusals remain charged,
logged and eligible for the existing correction path, never accepted or cached.
Offline replay and canary refusals retain their existing caller failure policies.

These limits are operational admission bounds, not a relaxed schema or a proof
that all schema-valid trees are feasible. A valid oversized tree can be refused
with its specific bound named. Within those bounds, tag exclusivity proves the
same union verdict, and the unchanged full native constraints still apply.
The guarantee concerns local schema/normalization work; model calls, domain
callbacks, and solver work retain their separate existing budgets. No live pilot
completion is implied by the offline equivalence and deadline tests.

<a id="round-10-xi-bind-resume-completion-to-its-results-generation"></a>
## Round 10 — Xi: bind resume completion to its results generation

R10.1. Tau2 F2 is fixed. A historical partial `awaiting_selection` marker no
longer establishes completion after a later recovery has finished its missing
jobs but halted before saving refreshed analyses and routes. The next resume
uses those sealed results to finish native publication without dispatching a
completed search again. A genuinely completed current generation still returns
before provider construction.

R10.2. Completion evidence is scoped to the latest search-publication batch in
the verified main chain. Its publication-finished receipt, complete job phase,
saved paired analyses and selection marker must occur in that order. The job
inventory must match the restored goals; the saved positive/negative results
must equal the restored SearchResults; the selection's route inventory must
match those results. Old markers, partial analyses and earlier result inventories
cannot authorize the shortcut. Existing logs need no new event format: their
verified ordering and result contents provide the binding.

R10.3. The native placeholder regression first reproduces the reported failure:
a bounded failed job leaves a partial selection, recovery finishes that job,
and an injected halt prevents refreshed analysis/route persistence. Before the
fix, the next resume returns success but adds zero route events instead of two.
After the fix it publishes two route events and one paired analysis, with zero
search redispatches and no new MODEL receipts. Re-entry after that creates no
provider and no new publication generation. The production-wire control restores
the former any-historical-selection predicate: the regression fails under that
mutation and passes after restoration. All 18 owning recovery tests pass.

R10.4. The separate integration checkpoint is `c8194b5`, merging `c32d429` into
`1971c74`. Both documentation appendices are preserved. Before F2 implementation,
full pytest passed 1,032 tests with 4 opt-in skips (1,036 collected), followed by
433/433 mutation failures and restored passes. All 187 tracked-file hashes were
restored exactly. Evidence for that checkpoint is under `runs/xi-integrate2/`;
Round 10 evidence is under `runs/xi-round10/`. No push or paid call is authorized
or performed by this work.

Finding disposition: tau2 F2 is fixed and its executed regression/control proof
is placed in R10.1–R10.3. 1 finding, 1 placed.

R10.5. Final checkpoint: full `uv run --locked pytest -q` passed 1,033 tests,
with 4 existing opt-in skips (1,037 collected), in 800.36 seconds. After it
finished, the full integration control runner produced 434/434 expected
mutation failures and restored passes, including the new F2 control. All 187
tracked-file hashes matched the pre-gate manifest after both gates. The diff
check is clean. The fix remains a local commit; no push or paid call occurred.
<a id="s8-frozen-construction-catalogue-interface"></a>
## S8: Frozen construction catalogue interface

> Status: Search consumption is implemented by [Round 12](#round-12-shared-search-vocabulary-and-explicit-formula-bindings); persistence contract remains current.

`CommitmentSet` and `commitments.json` retain their strict legacy format. Rich
construction also writes immutable `frozen-t.json` with `schema_version` equal to
`frozen-t-v1`, `commitments` equal to `CommitmentSet.to_dict()`, and
`symbol_catalogue`. The catalogue has `schema_version: symbol-catalogue-v1`,
`commitments_sha256`, `symbols`, `sha256`, and `catalogue_id`. Symbol entries retain
`name`, `kind`, `arity`, `definition`, and `evidence_ids`; symbols are sorted by
name and evidence IDs sorted and unique. Definitions remain model judgments.

`commitments_sha256` hashes canonical `CommitmentSet.to_dict()`. Catalogue
`sha256` hashes the object containing only `schema_version`,
`commitments_sha256`, and `symbols`; `catalogue_id` is `sha256:` plus that hex
hash. All hashes are SHA256 over UTF-8 `ara.runtime.cache.canonical`: sorted
object keys, compact separators, unescaped Unicode, no NaN. Array order is
significant. No formula/text equivalence normalization is performed. Consumers
must verify identity, binding and signatures when metadata exists. Absence of
`frozen-t.json` means legacy semantic catalogue unavailable; it does not license
inventing definitions or ignoring corrupt metadata. Construction owns persistence;
search owns loading metadata and incorporating identity in model/cache inputs.

<a id="round-12-shared-search-vocabulary-and-explicit-formula-bindings"></a>
### Round 12 — shared search vocabulary and explicit formula bindings

> Status: [Rounds 13–14](#round-14-solver-contribution-and-own-thesis-gates) extend target preflight with contribution and own-thesis checks. Frozen catalogue and slot-binding contracts remain.

- Integrate Sigma's catalogue interface from `597b666`. `commitments.json` and
  the strict `CommitmentSet` codec remain unchanged. Search validates the optional
  `frozen-t.json` envelope, passes its symbols and catalogue/T hashes in cache
  inputs, and refuses corrupt present metadata. Missing metadata is explicitly
  `unavailable_legacy`; search does not fabricate semantic definitions.
- New proposals carry `conclusion_ref=current_goal` after exact text validation.
  Licensing binds that reference to the existing goal formula and still checks
  canonical equality. A changed conclusion text cannot use the reference.
  Historical proposals retain their previous canonical encoding and independent
  formalization behavior for log replay; no old evidence is rewritten.
- A single `formalise_slots` call interprets all slots together with the goal,
  frozen catalogue, exact T-reference bindings and up to eight candidate shared
  metavariable substitutions. The model cannot change a frozen slot formula.
  Bank shape, solver entailment, scope rules and leaf equality remain independent
  engine requirements. Deterministic forward checking explicitly converts its
  canonical formulas out of the runtime reference contract.
- Non-open proposal T IDs must exist and carry the exact frozen text, including
  attribution. Runtime validation corrections receive the concrete rejected
  output and reason; a reference does not silently authorize a paraphrase.
- Target vocabulary preflight records disconnected IDs and permits exactly one
  target-proposal correction with catalogue context. If still disconnected,
  search retains the target and the explicit second failure receipt; it does not
  assert reachability or silently replace a named target. Legacy runs without
  semantic metadata still compare exact signatures present in T.
- Select the brief's bounded-batch option: one search proposal batch per expanded
  leaf, with up to three distinct proposals. `proposal_limit=3` and
  `attempt_budget=1` describe search generation; the existing separately logged
  runtime validation-attempt limit still applies to invalid responses. Empty
  batches remain valid. Depth and node caps are unchanged.
- Sealed traces preserve the current-goal reference. Offline resume replays joint
  slot receipts and rechecks bindings/licenses without a provider. The new schema
  joins the existing automatically enumerated Codex preflight manifest; an old
  live schema proof will be stale. This round makes no live provider calls.
- Placeholder regression: T contains P and P -> Q; the native preparation,
  paired search, route publication and offline replay path closes Q, with both
  leaves in T. Other regressions cover disconnected correction, catalogue cache
  identity, corrupt/legacy metadata, joint open-slot entailment, changed frozen
  bindings, reference correction, and a valid third proposal alternative.
- Add production-wire negative controls for all five diagnosed causes, including
  reference guards, catalogue/preflight propagation, batch size, joint slot and
  metavariable propagation, T membership/text, and reference trace persistence.
  Static mock request hashes were migrated offline for changed prompts and inputs.

Round 12 verification: full pytest passed 1,056 tests with 4 existing opt-in
skips (1,060 collected) in 864.28 seconds. After pytest completed, the full
negative-control runner produced 446/446 expected mutation failures and restored
passes, including all 12 new controls. All 193 pinned source/test/documentation
hashes matched before and after both gates. Evidence is in `runs/xi-round12/`.
The native placeholder regression closes Q from P and P -> Q and restores its
licensed inference through offline resume. No live-model behavior or new
real-corpus closure is claimed. This work is committed locally without a push.

Finding disposition: all five diagnosed causes are addressed above: current-goal
identity, frozen vocabulary/preflight, bounded proposal breadth, shared slot
formalization, and validated T references. 5 findings, 5 placed.
<a id="s8-structure-gate-and-bounded-correction"></a>
## S8 structure gate and bounded correction

Rich construction plan v10 requires selected inferences to be conditionals using
selected endpoint formulas in a shared vocabulary. The model owns source meaning,
relational encoding, symbol definitions and qualification attachment. Code checks
signatures and exact conjunct endpoint inclusion, not semantic equivalence.
Qualifications remain separate unless the model finds source support for attaching
them. Attributed source conditionals do not create bank licenses.

Every completed formalization batch logs non-atomic fraction (atoms and predicates
are atomic), symbol reuse rate (commitment/symbol bindings whose symbol occurs in
another current or prior commitment, including constants), and conditional endpoint
connections. Inference endpoints absent because of a disclosed support cut are
not asserted to be connected. A failed gate gets one complete replacement request
with item-specific feedback; shared catalogue entries remain immutable. This
structure correction is separate from the configured validation-patch allowance
and still undergoes normal schema, symbol, provenance and capacity checks. A still
atomic batch with inference evidence is accepted with `flat_after_one_correction`,
its failed gate retained in the receipt and methodology. A structured but invalid
inference remains a refusal. Invalid provider output has no flatness exemption.

The placeholder proof derives F(a) from P(a), Q(a), their attributed conditional
to R(a), and the conditional from R(a) to F(a), without including R(a) or F(a) as
premises. This establishes the executable seam, not faithful real-source encoding.
Plan v10 intentionally prevents replaying old counted plans as this new policy;
old frozen artifacts remain readable under the legacy/search compatibility path.

<a id="documentation-corrections-2026-10-27"></a>
## Documentation corrections (2026-10-27)

> Status: This correction entry describes base `6511ff6`. Its missing-fork statement is superseded by [Round 13](#round-13-contribution-targets-route-selection-and-frozen-forks) at the rebased `f89cd37`. The [rebase entry](#documentation-rebase-f89cd37) identifies current guidance.

The documentation review used base `6511ff6`. The old README combined several
superseded policies with current guidance. The guides now reflect the following
source-backed behavior; original decision paragraphs above remain unchanged.

| ID | Corrected claim | Current evidence at this base |
| --- | --- | --- |
| DOC1 | PLAN's engine/runtime placeholders are implemented. | `ara/runtime/cli.py:28`, `ara/runtime/orchestration.py:113`, `ara/engine/search.py:59`; D1 superseded the original integration gap. |
| DOC2 | The failed-paper allowance is eight, not three. A threshold-stopped batch publishes retained evidence and failed/not-attempted rosters before raising. | `config.yaml:88`, `ara/runtime/extraction.py:419`, `ara/runtime/extraction.py:447`, `ara/runtime/extraction.py:495`; Mu addendum supersedes GX31. |
| DOC3 | Reconciliation is one best-effort pass, not an obligation traversal that must resolve every gap. | `ara/runtime/reconciliation.py:8`; Mu addendum supersedes GX13/GX21 and the reconciliation portion of GX26. |
| DOC4 | Range/review failures can retain accepted evidence; not every extraction validation/context failure aborts the whole batch. Strict intake checks still refuse diagnosed unreadable/partial PDFs. | `ara/runtime/calls.py:867`, `ara/runtime/extraction.py:372`, `ara/runtime/extraction.py:419`. |
| DOC5 | pypdf itself has no OCR; native intake now defaults to optional local OCR. Text-only behavior requires `--ocr off`. | `ara/runtime/cli.py:61`, `ara/runtime/cli.py:350`; OCR1 and later span decisions supersede no-OCR guidance. |
| DOC6 | Corrections can explicitly discard rejected candidate items with reasons. Normalization also handles null inventories and structural/page/ID forms; accepted history stays immutable. | `ara/runtime/calls.py:152`, `ara/runtime/calls.py:70`; M1 and Mu round 2 replace the narrower Kappa correction description. |
| DOC7 | Construction may depth-cut a closure and disclose omitted support instead of always refusing the whole argument. | `ara/runtime/closure_budget.py:70`, `ara/runtime/construction.py:172`; S1/S2/S5 supersede the earlier full-closure capacity claim. |
| DOC8 | Both subscription providers are registered. Independent provider dispatch is limited to rich construction stages; model-only search/writing overrides do not create an API adapter. | `ara/runtime/cli.py:123`, `ara/runtime/construction_stages.py:5`; Omega supersedes the pre-registration README note. |
| DOC9 | Claude Code rereads credentials and passes the access token through the call environment; it no longer writes a temporary OAuth copy. Codex uses a read-only bind. | `ara/runtime/claude_code.py:246`, `ara/runtime/codex_cli.py:96`; Omega round 9 and O10/O11 replace the old copy policy. |
| DOC10 | Search consumes the frozen catalogue, uses joint slot formalization and permits one target-vocabulary correction; those are no longer future work or an unconditional single target call. | `ara/runtime/search_alignment.py:20`, `ara/runtime/calls.py:913`, `ara/runtime/calls.py:970`; Round 12 extends S8 persistence. |
| DOC11 | Inherited API charges remain visible and count for API admission; subscription token admission uses local usage. | `ara/runtime/budget.py:148`; Omega round 6 supersedes the blanket inherited-budget description. |
| DOC12 | A bibliography passed as ordinary text does not extract its PDFs or establish source evidence. Historical extracted inventories also need current grounding before entering T. | `ara/runtime/cli.py:374`, `ara/runtime/grounding.py:95`; Mu round 2 adds grounding eligibility. |

`fork-from-freeze` and `run --from-frozen` are absent from this base's parser.
They remain a deferred shared-frozen integration concern in PLAN, not runnable
examples. A requested Codex pin remains distinct from verified serving identity
(`ara/runtime/codex_cli.py:230`). No code, test, prompt or schema changes accompany
this documentation work. Current offline results and remaining review findings
belong in the external documentation handoff; historical receipts above retain
their original proof scope.

<a id="round-13-contribution-targets-route-selection-and-frozen-forks"></a>
### Round 13 — contribution targets, route selection, and frozen forks

> Status: The inference-only derived criterion and `CLOSED-trivial` display are superseded by [Round 14](#round-14-solver-contribution-and-own-thesis-gates). The frozen-prefix contract remains; [Round 15](#round-15-separate-route-metadata-from-contribution-receipts) keeps contribution receipts separate from route metadata.

Target proposal inputs now include an own-thesis policy, explicit conditionals,
and shared signatures. The prompt requires support/refutation using at least two
distinct commitments, preferably across papers. A deterministic preflight excludes
canonical T copies, direct universal instances, and explicit reporting language.
Vocabulary and triviality share one correction request. Still-trivial candidates
are excluded and disclosed; still-disconnected nontrivial candidates retain the
previous warning policy. This is not a semantic originality or support oracle.

Display and default selection distinguish CLOSED-trivial from CLOSED-derived.
The latter requires a reachable inference node with its licensed proposal in a
closed engine graph. Historic CLOSED serialization remains intact. Trivial and
open routes are disclosed; selecting them requires an explicit route argument.
The native smoke fixture now derives P and Q from distinct placeholder premises
and conditionals, instead of copying frozen targets.

`fork-from-freeze` verifies the entire source chain and its required anchor,
requires one freeze and compatible bank, verifies commitments and optional
catalogue against the freeze receipts, then atomically installs the exact prefix
and artifacts in a separate empty directory. It reads the source without creating
locks or changing files. The fork appends a prefix-accounting receipt and current
configuration overrides; its own cache avoids writes into source-run caches.
Historical MODEL usage is retained once, classified as imported, and included in
normal accounting. No construction or original target/search receipts after the
freeze are copied. Current target proposal, native search, and selection follow.
A current live Codex preflight remains required for a real rerun.

Placeholder regressions and production-wire controls cover rejection/correction,
instances and attribution, display/default selection, native fork continuation,
source preservation, prefix accounting, and chain/anchor/artifact/bank refusals.
Only offline/fake providers are used. Verification results are recorded below.

Round 13 verification: full offline pytest passed 1,074 tests with 4 existing
opt-in skips (1,078 collected) in 836.09 seconds. After pytest exited, all 463
production-wire controls produced their expected mutation failures and restored
passes, including 13 new controls. All 200 pinned files were restored exactly.
The offline real-freeze demo copied 6,813 prefix events, rejected all ten copied
trivial targets after one correction, and left the source log, anchor and freeze
artifacts unchanged. No network or paid calls occurred. Evidence and the explicit
fake profile/counter are under `runs/xi-round13/`; no real thesis generation or
new real-corpus closure is claimed. The initial stale live preflight correctly
refused. An earlier disk-full test run was discarded; only this task's failed
demo copies were removed before the successful full rerun.

Finding placement: target/support limitations are in the first paragraph;
classification/novelty limits are in the second and README; fork preservation and
accounting are in the third; the live-preflight prerequisite and offline-demo
limits are above. 5 findings, 5 placed. No push occurred.

<a id="round-14-solver-contribution-and-own-thesis-gates"></a>
## Round 14 — solver contribution and own-thesis gates

Phi2 B1 is fixed at proposal and publication/selection boundaries. Preflight
uses the existing Z3 entailment function for the target and its negation,
against no premises and each frozen commitment separately. Each check has a
1,000 ms timeout; a bounded 8,192-entry cache keys premise/conclusion hashes
and timeout. Hashes distinguish free variables from bound indices and compare
bound variables up to renaming. Checks short-circuit on a decisive exclusion;
the maximum per candidate is twice one plus the commitment count. Unknown and
timeout results cannot authorize a candidate. One shared proposal correction
remains the limit. Receipts retain polarity, commitment, solver result, hash,
and timeout, including exclusions after correction.

Post-closure policy traverses reachable graph nodes, includes frozen CQ
evidence, excludes assumptions, and deduplicates repeated/alpha-equivalent
support formulas. `CLOSED-derived` requires a licensed inference, at least two
distinct supports, and a negative single-support/validity entailment check.
Other closures disclose `CLOSED-single-support` or
`CLOSED-contribution-unresolved`; explicit attribution is separately labelled.
Only derived routes are default-selectable. This does not change bank
licensing, engine CLOSED, graph codecs, or explicit operator selection. It
checks single-support sufficiency, not minimality of larger subsets or
independence of source papers. Native publication, CLI, and log-derived reports
use frozen T. Graph-only legacy rendering can recover leaf formulas; missing
CQ support fails closed.

Phi2 B2 is fixed with broader attitude/report phrases, a frozen-catalogue
check for top-level attribution predicates, and an isolated `classify_target`
request on the same provider for every candidate. The classifier sees the
target and vocabulary, not proposal history or rationale. Its schema requires
`own_thesis`, `attributed_report`, or `unclear` and a short reason. Only the
first passes; all dispositions and cache replays are logged. Missing legacy
catalogues remain unavailable. The new schema is included in Codex preflight;
existing 15-case receipts must be refreshed to cover all 16 cases before live
use. No live schema acceptance is claimed here.

Placeholder regressions reproduce duplicate conjunctions, tautology padding,
alpha-renamed quantifiers, attributed native closures, CQ/assumption/alias
support handling, and fail-closed solver outcomes. The original red run had
20 failures and three passes. Offline fake-provider fork evidence and final
sequential pytest/control receipts are retained in the Round 14 task report.
The real pilot source is immutable; its copied targets test rejection only.
Neither the fake demo nor these checks prove real-corpus originality, faithful
formalization, successful new synthesis, or general semantic attribution.

<a id="round-15-separate-route-metadata-from-contribution-receipts"></a>
## Round 15 — separate route metadata from contribution receipts

Phi2 R1 exposed a report crash when a redundant two-support closure's solver
receipt contained `polarity`, colliding with the route event's `polarity`.
Reports now keep the event's target, polarity, and graph authoritative, retain
`classification` for existing report consumers, and nest the full solver
receipt under `contribution`. Thus a negation-search route can preserve its
`negation` polarity while `contribution.polarity` records the local solver's
`target` check. No receipt fields are silently merged into event metadata.

The native CLI regression covers two redundant-support proofs and a necessary
two-support positive control. It verifies licensed CLOSED graphs, classification
and selection disclosure, both polarity values, complete nested receipts,
HTML/JSON output, source-file preservation, and no report-time provider or
engine calls. Mutation controls cover both reintroducing the flat merge and
silently replacing the event polarity. Full offline pytest and sequential
control receipts are retained in the Round 15 task report. No paid calls or
push are part of this repair; contribution and licensing policy are unchanged.

<a id="documentation-rebase-f89cd37"></a>
## Documentation rebase onto f89cd37 (2026-10-27)

The docs branch now includes xi rounds 13–15 from `f89cd37`. All new decision
paragraphs remain intact and indexed; the authorized B1 identifier redaction is
retained. Earlier documentation corrections still describe their stated base.
Current guides route the merged behavior as follows:

- `docs/search.md` owns target contribution/own-thesis preflight, derived-only
  default selection, verified frozen-prefix forks and search resume. A request
  for ten candidates can yield fewer accepted targets or none. Vocabulary and
  contribution checks share one correction; explicit selection does not bypass
  provider, budget, audit or verification requirements.
- `docs/construction.md` links the native fork operation; it no longer describes
  all shared-freeze reuse as absent. `fork-from-freeze` is the registered command.
  `run --from-frozen` remains unsupported. The source needs a verified freeze,
  not a completed essay; fork configuration overrides are limited to the flags
  actually registered at `ara/runtime/cli.py:45`.
- `docs/reporting.md` preserves the distinction between event `polarity` and
  `contribution.polarity`; `classification` stays available at the report's top
  level (`ara/runtime/report.py:286`). Reports may evaluate the bounded local
  contribution policy but do not dispatch providers or rerun engine search.
- `docs/accounting.md` describes the once-imported frozen prefix. Search resume
  and later selection use the fork's effective configuration rather than the
  original source configuration (`ara/runtime/search_resume.py:265`,
  `ara/runtime/freeze_fork.py:16`). Resume retains the recorded target/job set;
  it does not refresh proposals to pass a newer target policy.
- `docs/providers.md` identifies the new `classify_target` schema. Historical
  15-case Codex proofs must be refreshed for the 16-case contract before live use.

Source checks and offline regressions do not establish semantic originality,
faithful formalization, useful new synthesis, independent source papers or live
Codex serving identity. The external rebase handoff records the current CLI-help,
link, leak and full pytest results separately from xi's historical proof receipts.
No executable, prompt, schema, test or configuration change is made by this rebase.


## S9: Content definitions with hash-bound source stance

This supersedes S8's attributed commitment text for newly constructed T. Rich
build_t_batch v5 returns id, content definition and formula. New Commitment.text
and symbol definitions denote the proposition itself; runtime copies exact source
text and attribution into provenance, without mechanical semantic rewriting.
The shared target_policy.attributed_report lexicon screens both definition kinds;
failures use logged construction correction and remain refusals when uncorrected.
This heuristic is not a proof of translation fidelity and can conservatively
reject content that uses its lexicon literally.

Keep the four-field CommitmentSet codec, commitments.json, frozen-t.json and
symbol-catalogue-v1 unchanged. Add commitment-provenance.json with schema_version
commitment-provenance-v1, definition_semantics content, commitments_sha256,
catalogue_sha256, commitments mapping and sha256. The mapping retains source_id,
source_authors, attributed_to, page_start/end, evidence_id, attribution, stance,
source_kind, exact source_text and sorted omitted_support_ids. Hash the entire
sidecar except sha256 with runtime.cache.canonical/digest. Bind exact T and the
verified catalogue. Full metadata is logged before freeze. The construction guide
owns the operating contract; the external Sigma/Xi contract records the seam.

Map author_claim to endorsed, reported_view to reported and attacked_view to
attacked; contradictory reported/attacked source-kind tags refuse. No endorsement
is inferred when legacy metadata is absent. Hashes detect changes relative to the
retained records, not an adversary rewriting an entire history. Source provenance
is validated/copied by code, while content and equivalence remain model judgments.
Plan v11 prevents silently resuming old plans under these semantics. Source
citations and immutable evidence stay unchanged. Search-side stance admission,
fork/resume copying and route/report policy are owned by Xi; solver licensing
is not changed by this construction patch.
## Round 16 — asserted content and source stance in search

The own-thesis classifier now receives the target text and a structural rendering
of its formula through verified content definitions. Source text, attribution and
stance are provenance, not assertion operators; they are excluded from the
classifier payload. Exact T, catalogue and provenance hashes bind its cache
identity. Definitions without the verified content marker remain unavailable,
not mechanically rewritten. The deterministic target-text attribution lexicon
and bounded solver contribution gates remain unchanged.

Search shares sigma's hash-bound commitment-provenance-v1 sidecar and full
commitment_provenance_frozen receipt. CommitmentSet and frozen-t-v1 codecs stay
unchanged. The engine retains full frozen context for proposal/formalization,
but only source-endorsed commitments can terminate global premises or satisfy CQ
evidence when provenance is verified. Reported/attacked content can be used under
existing bank-licensed assumption scopes, with its source role disclosed; attacked
content is never converted into an asserted negation. Rejected global use emits
STANCE_CROSSING. Forward/conflict analysis receives the same eligible premises.
Legacy runs retain their behavior with stance explicitly unavailable, not endorsed.

Native publication, reports, export and selection retain stance receipts.
Historical closed routes crossing a known stance are labelled
CLOSED-stance-crossing and excluded from default selection. Explicit selection
retains the existing disclosed-route policy. Freeze forks copy and verify the
sidecar against its prefix receipt; native search and resume refuse deleted,
corrupt or mismatched recorded provenance. Recovery refuses closed routes that
cross a verified stance before reusing their analyses.

Placeholder regressions exercise own-voice synthesis, the existing attribution
probes, reported/attacked premise rejection, CQ rejection, scoped hypotheses,
cache identity, native resume and frozen forks. The full offline pytest and
mutation gates run sequentially; exact receipts belong to the Round 16 task
report. No paid calls or push are part of this change. Model content fidelity,
source stance tagging and originality remain semantic limitations, not solver
claims.

The shared writer/auditor outline carries source stance, attribution and scope
role for referenced commitments when provenance is verified. Explicit selection
does not erase these roles. The prompts require reported/attacked material to
remain reporting or conditional hypotheses, including in dependent conclusions;
the model audit treats endorsement promotion as an added inference. This is a
model-audited writing obligation, not a deterministic semantic guarantee.


## S10: Per-window correction and exact definition unframing

Supersede the construction-wide single-correction allowance with configurable
nonnegative construction_targeted_corrections (default 2), separately per window
and call type. Preserve accumulated patches, normal counted transport/admission,
and existing run budgets. No separate global correction counter is needed; the
finite plan bounds the number of eligible requests. Plan v12 binds this policy,
and resume never replenishes a completed or terminal refused window.

Supersede S9's blanket prohibition on mechanical rewriting only for an exact
leading source-known author/speaker argues|holds|claims that content frame. Record
definition_unframed, preserve original_definition and author in optional
hash-bound definition_unframes provenance, and validate the remainder again.
Do not alter exact source text, citations or stance. Old sidecars without history
remain valid; new history requires the updated validator. The construction guide
owns the full schema and limits. Keep the shared lexical screening rule unchanged,
aggregate every offending definition/phrase into correction feedback, and treat
successful restatement, coverage improvement and semantic fidelity as unproved
until observed. Offline planning and recorded-response census are not a live run.
## Round 17 — larger target pools and defeasible reachability

The proposer now sees the actual versioned bank, its slots and critical questions,
plus placeholder examples of deduction, defeasible support and the conditional
consequent trap. A new main proposition must not already be in T or follow from
one commitment. Existing solver validity/singleton gates, attribution checks,
stance restrictions and two-distinct-support contribution criteria are unchanged.
Corrections identify the candidate, checked polarity and full entailing commitment;
a conditional with a consequent in T gets an explicit explanation. A wording
change cannot fix a formula-level entailment witness.

Each ordinary attempt requests 20 candidates, keeping at most ten (or the smaller
configured target count) in stable attempt/response order. There are at most two
corrections, with accepted candidates retained rather than discarded. A named
position remains one exact-text candidate. Short pools are accepted but explicitly
logged as underfilled; empty or oversized responses are invalid. Every candidate,
including duplicates and surplus passing targets, receives a logged disposition.
Retained IDs and alpha-equivalent structural formulas do not fill two places.
New vocabulary is advisory rather than an exclusion: it can be necessary for a
nontrivial thesis supported by a defeasible scheme.

The native placeholder proof proposes a fresh R, passes contribution and
own-thesis preflight, and closes it via the sign scheme from distinct frozen P
and Q supports. All of that scheme's CQs have explicit answers supported by both
frozen IDs. Classical entailment of R from even the full pair returns a
counterexample, yet native publication classifies the route CLOSED-derived.
The same route with unanswered CQs is OPEN. No engine licensing rule was changed
for this result. It proves mechanical reachability through the existing bank,
not source truth, semantic scheme fit, originality or usefulness of live targets.

Round 17 regression and production-wire mutation receipts are retained in its
external task report. Full offline pytest and controls run sequentially. No paid
calls or push are authorized or claimed.

## Round 18 — formal novelty and substantive closure

Target preflight now checks Boolean dependence on the complete formulas of frozen
T, using two independent vocabulary interpretations with equal T truth vectors.
An UNSAT result rejects equivalent Boolean packaging, including vacuous fresh
atoms; unknown/timeout refuses. T is not asserted during this check, because
that would exclude substantive deductions from T. Implications additionally check
the main consequent, retaining quantifiers, so novelty only in antecedents cannot
qualify. Main atomic applications must not already be whole T commitments. In
particular Q remains a new assertion for T={P, P -> Q}; mere vocabulary occurrence
inside a commitment does not make Q an already asserted commitment. All prior
single-support, validity, stance and isolated own-thesis gates remain in force.
Correction feedback includes the concrete novelty reason and frozen basis IDs.

`CLOSED-derived` additionally needs a reachable inference using a known bank
scheme other than conjunction introduction/elimination, disjunction introduction
or double negation. An otherwise contributing route lacking such an inference
is `CLOSED-structural`, disclosed but excluded from default selection. Unreachable
inferences do not count. Existing single-support/stance/unresolved priorities and
engine closure/licensing remain unchanged. Proposer inputs identify both bank
groups alongside actual schemes, catalogue definitions and placeholder examples.

The native placeholder regression rejects P and Q as a proposed new thesis,
retains R, closes R through `sign` from two endorsed supports in two sources with
all CQs answered, and labels a historical conjunction route structural. Mutation
controls cover equivalence, correction wiring, main-claim checks, unknown refusal,
structural classification, reachability and proposer guidance. Canonical policy
and limitations are in docs/search.md; exact offline pilot-fork and full gate
receipts are in the external Round 18 handoff. No new paid call is authorized.
Formal assertion novelty and mechanical cross-source support do not establish
semantic originality, source/formula fidelity or CQ truth.

## Round 19 — semantic novelty and bound content (kappa4 F1/F2)

The Round 18 acceptance of Q from T={P,P -> Q} is superseded: a classical
consequence of all frozen T is not a novel target. Modus ponens and engine closure
remain valid, but such a route is not offered as a novel derived thesis. A cached,
bounded entailment query checks all of T. Every fresh atomic application is then
replaced by true and false, with equivalence under T tested for each substitution.
At least one must change truth; unknown/timeout refuses. This replaces syntactic
main-claim descent and catches nested implications, disjunction, double negation,
quantifier wrappers, vacuous atoms and explicit aliases in T.

A qualifying reachable nonstructural bank step must conclude an essential new
proposition of the root. Its conclusion is checked against all frozen T too.
Unused conditional-proof assumptions do not qualify, even when their wrapper
mentions a new symbol. Pure deductive closure or an absent qualifying step is
reported as CLOSED-structural; uncertain novelty is contribution-unresolved.
Existing contribution, stance, licensing and CQ requirements remain in force.

Propositions optionally carry typed new_symbols content definitions, omitted
from serialization when absent so historical codecs remain stable. CommitmentSet,
commitments.json and frozen-t/catalogue formats are unchanged. A single atomic
assertion can bind its complete text; compound targets require explicit fresh
symbol definitions. Missing, duplicate, unused and frozen-name overrides refuse.
Normalized text equality and conservative near-duplicate matching screen frozen
content reuse. The existing isolated classifier additionally returns required
novelty and fidelity judgments against the T content list and rendered bindings.
Only own_thesis/new_assertion/matches admits; restatement, mismatch or uncertainty
refuses. Inputs, judgments, corrections and cache identities retain these fields.
The classifier schema change invalidates old preflight proof for live use.

Kappa4's wrapper and rename probes, genuine new-atom sign closure, unused scopes,
relevant versus unrelated inference conclusions, whole-freeze checks, definition
bindings, lexical duplication, model judgment gates and timeout refusal have
regressions and production-wire mutation controls. Success fixtures now use new
defeasible conclusions rather than non-novel deductive consequences. Formal
novelty, lexical screening and fake-provider tests do not prove semantic
originality, faithful paraphrase, scheme fit or model judgment accuracy. No paid
calls or push. See the external Round 19 handoff for exact pinned gate receipts.

## Round 20 — non-logical scheme conclusions (kappa4 R1/R5)

A CLOSED-derived route requires a reachable non-logical bank scheme whose own
conclusion contains an essential new proposition of the target. The bank's
kind=defeasible entries supply these schemes; every kind=deductive entry is
structural for novelty. This includes propositional and first-order rules,
modus ponens/tollens, hypothetical syllogism and conditional proof. Logical
wrappers may surround a qualifying scheme but cannot supply the qualifying step.
This supersedes Round 19's assumption-reachability heuristic, which counted
decorative conjunction introduction/elimination paths as assumption use.

Whole-freeze novelty, essential-application matching on the scheme's own
conclusion, support, stance, license and CQ checks remain. Native regressions
cover the old-vocabulary sign conclusion, unadorned conditional, matching
conjunction core, padded assumption, syllogism wrapper and genuine R. The
licensed deduction {P, P -> Q} proves Q with engine CLOSED and novelty-structural
classification. Offline fake-provider proof does not establish semantic scheme
fit, model accuracy or real originality. Live preflight remains a prerequisite.

R5 uses one name-collision check for automatic and explicit proposed definitions.
Both reject reuse of a frozen name with a different signature; both accept a
fresh F(a) binding. No CommitmentSet or frozen catalogue codec changes. Exact
full-suite and control receipts belong to the external Round 20 report.

## Round 21 — advisory attribution and new-atom scheme guidance

Broad lexical attribution screening is advisory for search. Every text/definition
hit is logged and supplied to the isolated own-thesis classifier. Its verdict is
authoritative; exact leading name + argues/holds/believes that frames retain a
hard rejection. Route display uses the same narrow exception. Construction's
shared attributed_report helper remains unchanged. The classifier prompt treats
named report patterns as strong evidence and distinguishes own-voice uses of
"claims about" and "account". Fake classifier tests verify required judgments,
not live model accuracy. Novelty, fidelity, stance and source integrity gates stay.

Leaf mapping and cut proposal receive goal novelty, the actual non-logical bank
signatures and CQs alongside the frozen catalogue. New atoms map to open and
require a scheme's own conclusion, never an irrelevant hypothesis or nearby old
claim. The native engine permits three candidates in a batch and one correction
when none is licensed, with concrete engine/validation feedback. An empty batch
reports NO_PROPOSALS. Validation retries cannot multiply this correction budget;
operational errors still propagate. Licensed alternatives and all CQ/node/depth
checks remain. This replaces the single cut batch from Round 12.

Placeholder native closure and a separate offline fake-provider replay of the
real pilot leaf exercise reachability. The latter is retained only in ignored
run evidence; no real source content is committed. It does not establish semantic
scheme fitness, useful synthesis or truthful CQ answers. The external Round 21
report inventories arbitrary-conclusion schemes and their critical questions,
source preservation and exact sequential test/control results. No paid calls or
push; live use still requires current configuration and preflight evidence.


## Round 22 — cross-paper routes and bounded bridge guidance

CLOSED-derived now requires at least two distinct source_id values from verified
commitment provenance among reachable, formula-distinct leaf/CQ supports. A
qualifying single-paper route is CLOSED-single-paper; missing identity remains
CLOSED-contribution-unresolved. Neither is selected by default. Citation/page
strings are not paper identities. Engine closure, stance and novelty checks
remain unchanged. Explicit human route selection remains available and logged.

The target pool grows from 20 to 30 with the existing keep-at-most-ten policy and
bounded corrections. Frozen metadata yields deterministic candidate bridges: up
to 30 pairs and 30 triples from multiple papers sharing catalogue symbols or
lexical definition terms. Work is capped at 10,000 combinations per size and
truncation disclosed. Only endorsed supports enter bridge guidance. No catalogue
or CommitmentSet codec changes; no source definitions are invented.

Target, map and cut calls carry the candidates in logged/cache-bound inputs. Cut
guidance prefers cross-paper slots for a new-atom conclusion. Exact returned T
IDs cite the bridge; proposal_bridge receipts record matched bridge IDs and slot
to paper mappings without changing the proposal codec. Lexical connectivity is
not proof of topic equivalence, semantic scheme fit, relevance or necessity.

Native placeholder regression covers cross-paper acceptance and single-paper
disclosure through selection and reports. Legacy smoke now waits for explicit
selection because it has no verified paper identity. No paid calls or push; exact
full sequential pytest/control receipts are in the external Round 22 report.

## Round 23 — order-independent formula/paper matching

Reachable leaf and CQ evidence keeps every cited commitment in its formula-hash
group. Logic still checks each distinct formula once, using a deterministic
representative; choosing that representative no longer discards paper provenance.
Cross-paper admission requires a matching of two distinct support formulas to two
distinct verified source IDs. Either formula may use any of its cited commitments.
The paper receipt retains all formula/commitment/paper associations and a stable
two-edge witness. Counts alone cannot substitute for that matching.

Reordering CQ supporting IDs leaves contribution receipts, classifications and
default selection unchanged. Repeated P across papers can supply the second paper
when Q supplies a distinct formula; P alone across papers remains single-support,
and P/Q from one paper remains single-paper. Reachability, stance, licensing,
novelty and CQ checks are preserved. Native report regressions and production-wire
controls cover provenance loss and reuse of a paper or formula in the matching.
No paid calls or push; exact verification is in the external Round 23 report.

The Round 23 context repair bounds map_leaf and propose_cuts guidance before
dispatch. At most eight bridges rank by shared leaf formula symbols, with bridge
ID ties. Their commitments form the leaf slice; when no bridge is available, at
most 2*k formula-ranked seed commitments supply bounded fallback leads. An exact
frozen match is retained even at k=0. Only referenced
catalogue entries and projected source roles accompany it. Full frozen T,
catalogue and provenance hashes remain bound to the inputs; local validation and
licensing still use the complete immutable artifacts. Zero-overlap seeds are
disclosed bounded leads, not semantic matches. Full CQ wording stays in compact
scheme signatures; duplicated provenance source text and bank citations do not.

Native request counting includes the output allowance. Oversized guidance shrinks
k deterministically through 8,4,2,1,0 with a search_context_slice receipt at each
count. Validation/correction requests are rebuilt and recounted too. Irreducible
context refusals in search ports use search scope, leaving the shared run budget
and sibling jobs active; accounting, cost/token caps and infrastructure failures
retain their run-stop behavior. Existing bounded job retries and partial-result
disclosure remain. Frozen artifact codecs and configured context limits stay.

Offline replay reproduces all eight fork-4 map/cut admission counts exactly,
using saved calibration and native local counting without transport or credential
loading. Maximum total context falls from 215750 to 48606 tokens, including output
allowance, against the same 200000 bound. This proves request admission, not model
quality or successful live closure. Evidence and final gates are in the external
Round 23 report; no live pilot or paid call was made.

## Round 24 — retain all exact leaf evidence

Leaf slices retain every commitment whose formula exactly matches the leaf,
independently of bridge selection and every shrinking level, including k=0.
Exact matches appear first, with verified endorsed copies ordered before all
other copies; IDs break ties. Reported/attacked copies remain visible with their
original roles, never promoted to endorsed. Missing legacy stance stays unknown.
Each search_context_slice receipt and request lists exact_match_commitment_ids.

The full exact-match set is counted as indispensable leaf context. If it cannot
fit, the existing disclosed job-local refusal applies; shrinking cannot silently
drop the leaf's own evidence. Native regressions reproduce the Q-bridge/P-leaf
probe with earlier-ID reported and attacked copies and a later-ID endorsed copy,
at normal sizing and forced k=0. The same engine now closes P using the endorsed
commitment. Exact retention and endorsed-first order have production-wire controls.
No paid calls or push; scoped verification receipts are in the Round 24 report.


## nu4 — sectioned competition writer (2026-10-28)

Eight historical whole-essay attempts failed the 4,500-word minimum before any
audit. Identical-input validation retries did not communicate measured shortfalls.
Competition-length writing now uses a checked 4,800–5,600-word section plan,
individually logged section calls and deterministic assembly. Up to three targeted
revision rounds retain accepted sections and communicate measured section/total
length. The short smoke path stays small. This extends `ModelCalls.write_essay`
and `compose`, without changing the engine or freezing additional commitments.

Exact frozen support, attributed source text and page citations accompany each
section and the audit. Bounded neighboring grounded source items remain context,
not additional premises. Exact T citations are checked locally; semantic fidelity
remains model-assessed. Required evidence is never silently truncated. Section
and context bounds, missing-context disclosures, plan/section/revision receipts
and partial artifacts are described in docs/search.md. The normal final word,
coverage, audit, originality/citation and isolation checks remain in place.

Offline coverage includes order, retained sections, shortage/excess correction,
three-round exhaustion, plan budgets, source context and unsupported citations,
plus production-wire controls. Full-suite, control and live receipts belong in
`/home/dev/ara-work/reports/nu4-writer.md` with the exact tested revision. A live
length-valid draft with an audit result is not a verified essay or proof of
novelty. Codex's API-only evidence-retrieval restriction is outside this repair;
no API/Claude fallback is introduced. No push; non-author review follows.

The first nu4 live experiment still ended at 3,213 words after three rounds:
whole-section replacement often returned roughly the same length or shortened
accepted text. Expansion therefore returns additional paragraphs, which runtime
appends deterministically while preserving the original text verbatim. Measured
remaining section capacity bounds each addition; condensation still replaces one
section. The revised regression fails against replacement semantics. The failed
live attempt remains logged and is not presented as successful evidence.

## nu4 round 2 — audit citation ownership and targeted repair (2026-10-28)

Trailing citation markers previously became part of the next numbered sentence.
The deterministic splitter now retains them with the preceding terminal
punctuation. Original-text offsets are shared by audit input and revision, with
node markers transparent to splitting. The draft itself is not normalized.

A complete adverse audit retains its exact evidence and labels in a typed
rejection. Native composition can request up to two rounds of replacements for
only its flagged sentences, then audits the complete result again. Each accepted
patch preserves unflagged bytes and bibliography; retained sentences keep exact
citation/node markers. An empty replacement removes an unsupported sentence.
Schema, size, body, length and node-coverage checks remain binding. No missing-node
repair is invented when the auditor identifies no sentence to change. Malformed
inventories and transport failures do not authorize revisions. The post-citation
audit remains final, so repair cannot alter text after its citations were checked.

`select --draft` admits a saved unverified draft through the same checks, logging
the input and avoiding fresh outlining/writing. The new revision kind uses writing
stage routing and the standard logging/cache/budget/isolation boundary. Codex
schema proof now includes 18 cases. No API fallback or provider-switching change
is made. Live outcomes and the unexecuted API alternative's estimate belong in
the external nu4 report, with remaining claims and the exact tested revision.
