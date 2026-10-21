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
