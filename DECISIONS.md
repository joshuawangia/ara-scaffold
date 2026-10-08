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
