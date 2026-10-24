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

Z2. Post-dispatch serialization, JSON parsing and completion-log failures book the
admitted reservation, replace any unpersisted in-memory actual charge, emit an
incomplete MODEL record, enforce the post-call cap, and STOP without retries.
The raw payload is omitted when it cannot safely be persisted; the prompt and
reservation remain. Fully parsed schema/reference rejections retain their actual
usage and existing bounded correction policy. Unknown accounting refuses resume.
Methodology marks unknown reservations and outstanding dispatches INCOMPLETE.
A persistent storage outage cannot guarantee a new append: the durable call_start
and checkpoint still force refusal; restoring storage/reconciling is required.

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

## Round 3 gamma: logged per-paper extraction

GX1. Add a native `ara extract` stage and `ModelCalls.extract_paper`, using the
same provider, schema projection/local validator, retry, cache, budget and MODEL
log boundary as other calls. Each selected paper is one request, with up to the
configured validation attempts (extract defaults to three). Refusal, output stop,
transport failure and budget STOP retain existing finality. No extraction failure
is converted into successful model output. Frozen Paper/PageText and
PaperExtraction/ExtractedItem contracts separate intake and accepted output.

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

## Round 3 gamma fix 1: corpus capacity, lineage and PDF coverage

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


## Gamma round 2: rich evidence and working T

GX12 supersedes GX6's compact summary. Rich v2 records preserve individually cited
premises, intermediate/final conclusions, stated inference links, qualifications,
distinctions and attributed reported/attacked views. Inference origin is always
paper_stated; this is source evidence, never a bank license. No per-item text or
item-count ceiling is imposed. 32000 output tokens per extraction call replaces
8192: at roughly 250 tokens per serialized node/link this permits approximately
100 entries plus 7000 tokens for thinking/variance. This is an allowance, not a
completeness proof. Actual live usage belongs in the external round-2 report.

GX13. Count full page requests. Oversize context or exhausted output splits the
physical readable-page range; save each accepted graph unchanged. A counted,
logged reconciliation can add cross-range links referencing immutable ids. It
cannot rewrite/delete range evidence. Refuse a single-page overflow, incomplete
coverage or unresolvable/oversized reconciliation; preserve attempted receipts.
No silent truncation. Source fidelity is still model-assessed, not proved by JSON.

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

GX21 (D2-B1). Pending extraction references become stable IDs with originating
range and pages. Reconciliation receives counted original readable pages when
obligations exist, adds only immutable evidence, and returns an exact resolution
inventory mapping each obligation to nonempty accepted evidence/link IDs. Missing
or unknown resolutions refuse complete extraction. The saved graph includes both
obligation and resolution ledgers. This proves explicit obligations cannot vanish;
semantic adequacy of a model's evidence mapping still requires source inspection.
Full-source reconciliation may exceed context and explicitly refuse; no hidden
retrieval, clipping or inferred resolution is introduced.

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


## GX25 — Kind-specific extraction and bounded targeted correction

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

### GX25 — Full extraction preflight and global construction capacity

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

### GX26 — Bounded windows over immutable global evidence

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


### GX31 — Disclosed paper failures and completed-paper reuse

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


## Kappa: extraction response acceptance and bounded correction

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

## Kappa round 2: explicit conservative imports and grammar preflight

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

## Kappa round 3: conservative diagnostics and normalized recovery

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

## M1 — Relaxed paper acceptance with preserved evidence

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

## M4 — Monotonic snapshot reuse and versioned gap publication

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

## Search trace receipts (version 1, superseded below)

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

## S1 — Budgeted prerequisite depth before the single freeze

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


## S2 — Soft construction shares and accounted window refusal

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
## Xi round 6 — Concurrent search with isolated accounting

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

## Omega — Isolated subscription CLI provider

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

## Omega round 6 — Comparable usage and local subscription admission

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


## Omega round 7 — One unclassified retry and scrubbed exit diagnostics

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
