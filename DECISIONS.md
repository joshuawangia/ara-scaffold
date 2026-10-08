# Brain decisions for the ara program (2026-10-08)

Copy the relevant ones into the repo's DECISIONS.md with their reasons.

B1. Repo: `ara-scaffold`, built at `/home/dev/wt/ara/ara-scaffold`, default branch
    `main`. Target remote: private repo on the operator's personal github.com account
    (`joshuawangia/ara-scaffold`). This box is not yet authenticated to github.com;
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

A9. CLI console registration targets ara.runtime.cli:main, but that module remains
a docstring-only placeholder as required by this phase. CLI commands, real smoke,
private remote and fresh-clone end-to-end proof belong to later integration.

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

G9. Normal run builds/freezes T, generates targets, searches every target and its
canonical negation, invokes engine conflict/robustness analysis, then pauses for
`ara select`. Smoke selects the first CLOSED route (or first OPEN route), with an
explicit SYSTEM policy record. Human selection is separately HUMAN. Feedback is
logged verbatim and supplied to subsequent essay calls while the route remains
fixed and independently audited. Human CLI argv and supplied literature are
logged; interactive input measures prompt-to-accept elapsed time; explicit minutes
are labelled separately. Machine timing for model calls is observed wall time.

### Runtime integration gap (no seam changes)

At base b8dd2d7 the engine exports no search API. Runtime currently imports
`ara.engine.create_engine(bank=..., proposer=..., formaliser=..., mapper=...,
cq_answerer=..., repairer=..., sink=..., config=...)` and expects `search(target,
commitments) -> tuple[RouteGraph, ...]` and `conflicts(routes, commitments) -> dict`.
This is a runtime-owned temporary adapter contract, not a claim that the parallel
engine lane has adopted it. Integration must align `native_engine` to that lane's
public API. Missing API is a loud nonzero error; production never uses the test
fake or duplicates engine search. Real-provider full smoke, final engine/runtime
integration and fresh-clone end-to-end proof remain integration-owned.
