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

G10. Accounting failures after dispatch charge the conservative reservation with
`accounting=reservation_unknown_actual`, log STOP, and refuse resumption. A call
interrupted between call_start and its response also refuses resumption. The
methodology identifies reservations separately from measured cost. Cache writes
without TTL detail use the more expensive configured rate. Command wall time
excluding measured interactive input is recorded separately from model-call time.
Smoke topic/literature supplied by software are SYSTEM fixture data, not HUMAN
content; only argv and actually supplied content are attributed to the human.

### Gamma verification handoff

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

## Delta integration decisions

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

D6. The first accepted live search later rejected a max_tokens cut response at the
2048 output allowance. Smoke now reserves 4096 output tokens, preserving the
USD 5 cap. A low-effort trial returned an empty citation, correctly rejected by
the untouched local build_t schema. Final smoke retains the base high effort;
invalid output is never repaired by software or silently retried. Failed attempts
and their measured/unknown-spend ledgers are retained in ignored run directories.

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

D8. A second clean-clone trial returned duplicate commitment ids and stopped,
correctly. Smoke now allows at most three explicitly logged stateless validation
attempts, each with the original inputs plus the rejected output and validation
feedback. Every attempt passes the same budget admission, response logging, local
schema/typed/reference checks and actual accounting. Only accepted outputs enter
cache. Refusal, max_tokens, server/transport errors and engine licensing are never
retried by this mechanism. This supersedes G3/D6/D7's no-retry statement only for
accounted local-validation failures; there is still no hidden SDK retry or license
fallback. Non-smoke defaults to one attempt unless explicitly configured (1–3).

D9. Live depth-two search incurred over 60 model records before finishing its
first target. Smoke now uses depth one and eight nodes per polarity to keep the
end-to-end proof small; two targets, the real engine, both polarities, conflict/
forward analysis, draft/audits/web/export and the USD 5 cap remain. Truncation and
OPEN frontiers are logged, never presented as completeness. Normal search bounds
remain depth six / 500 nodes. Integration tests do not weaken their artifact or
analysis assertions; the bounded search policy is explicit in README/config.

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

D13. The first clean B9 trial at 191d366 stopped before the audit when a cut
proposal exhausted 4096 output tokens. The partial output was rejected without
retry and its USD 0.835520 measured spend is retained. Smoke now uses the normal
8192 output allowance; the USD 5 and 1,000,000-token caps, requested model, default
fallbacks, audit prompt and all acceptance guards are unchanged. A new clean-clone
trial is required; this configuration change does not turn the failed trial into
a success or enable retries of output-limit stops.

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
