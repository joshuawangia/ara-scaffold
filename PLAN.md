# ARA implementation plan

## Intent and scope

ARA separates versioned move forms (L), a frozen commitment table (T), and
model-proposed cuts (H). This new repository has no existing implementation.
Alpha fixes the shared seam so deterministic engine and runtime authors can
work independently. Only placeholder propositions (P, Q, R, S, F(x), a, b)
may occur in committed examples or fixtures. No philosophical content is
permitted in code, prompts, tests, documentation, or commit messages.

## Architecture and module map

- `bank/*.yaml`: versioned deductive schemas and defeasible slot/CQ forms.
- `ara/bank.py`: strict loader and validator; bank entries are the only licenses.
- `ara/types.py`: immutable formula AST, commitments, proposals, proof scopes,
  bank entries, route graphs, decisions and events; deterministic JSON contracts.
- `ara/ports.py`: typed protocols consumed by the engine, supplied by runtime.
- `ara/engine/{licensing,terminus,search,routes,forward,conflicts}.py`: future
  bank matching/Z3, closure, bounded AND/OR search, status/independence, forward
  derivation and conflict handling. Alpha supplies docstrings only.
- `ara/runtime/{providers,calls,cache,budget,logging,render,export,cli}.py`:
  future SDK/mock transport, schema validation, content-addressed cache, caps,
  append-only events, route display, log-derived export and human CLI entrypoints.
- `schemas/*.json`: model response contracts, including recursive formula AST.
- `prompts/`: future topic-neutral templates, with content injected at runtime.
- `config.yaml`, `pyproject.toml`, `uv.lock`: defaults and reproducible environment.
- `tests/`: placeholder-only boundary tests, no network.

## Engine/runtime seam

The engine imports only shared types and ports, never provider implementations.
CutProposer proposes bank ids with every premise slot filled and a goal-matching
conclusion. Formaliser returns formula ASTs. LeafMapper returns a frozen T id or
`open`. CQAnswerer answers named CQ templates. Tier1Repairer returns a structured
repair request/result; EventSink receives full immutable events. Engine decisions
are explicitly licensed/discarded with reason codes. Runtime owns validation,
caching, model calls, budget accounting and logging before values cross the seam.

Formula AST JSON distinguishes constants and variables; canonical text is a
structural identity, not semantic equivalence. Negation removes double negation.
Deductive bank schemas refer to formula metavariables, with explicit substitution
for quantifier rules and scoped assumption discharge for conditional proof and
reductio. Assumptions are never silently converted into T leaves. Scoped proofs
must be checked by the later engine, including external dependency closure.

## Phases and commits

1. Commit this plan alone before other repository content.
2. Commit repository rules, B1–B8 plus implementation decisions, configuration,
   packaging/lockfile, and docstring-only engine/runtime placeholders.
3. Commit immutable types, ports and tests; settle shared serialization and scopes.
4. Commit versioned bank forms, strict validation and tests.
5. Commit model response schemas and schema/contract compatibility tests.
6. Commit README skeleton and final evidence notes; report outside repository at
   `/home/dev/wt/shared/ara/alpha-report.md` and hand off the exact revision.
7. Later engine/runtime lanes implement against this seam; integration owns real
   smoke, fresh-clone proof and private remote publication. Alpha never pushes.

## Verification contract

Alpha executes `uv run pytest`: malformed and duplicate bank entries rejected;
missing slots and undefined CQ references rejected; formula JSON round-trip,
canonical identity and negation checked; commitment table deeply frozen; route
graph JSON round-trip checked; all model schemas checked against representative
placeholder payloads and malformed variants. For every load-bearing behavior,
mutate its production wire, observe the relevant test fail, restore, rerun green.
Record mutation and result. Audit all tracked content using broad text search
and direct review of bank/tests/docs; explain why grep cannot prove semantic
absence. Installation is tested with the locked environment. CLI execution is
explicitly deferred because its module must contain only a docstring in alpha.

Full program DONE-WHEN proofs belong to integration:

| Requirement | Proof and owner |
| --- | --- |
| Reject unlicensed steps | Engine tests using unknown bank ids |
| Reject invalid deduction | Engine Z3 counterexample tests on P/Q/R |
| Closure requires every leaf in T | Engine route fixtures including absent ids |
| Negation search executes | Engine original/negated target graph assertions |
| Tier 1 and Tier 2 trigger | Engine constructed contradictory placeholder graphs |
| Real `ara run --smoke` completes | Runtime/integration real-provider execution, 2 targets, shallow search, short draft; inspect graphs, draft, JSONL, methodology, tokens and cost |
| Fresh clone reproduces tests and smoke | Integration follows README from isolated clone using env credentials |

## Risks and accepted boundaries

- Formalisation is model-generated; schema shape plus solver entailment do not
  prove a faithful text translation. Preserve both for inspection.
- Solver entailment alone cannot enforce a named rule's shape; engine must check
  schema matching, quantifier substitution and assumption scope before Z3.
- No philosophical examples may enter the source tree; run/cache outputs ignored.
- Scheme citations use known book attribution and explicitly unknown page/chapter
  locators rather than invented specificity; source review remains visible.
- Canonical structural identity is deliberately weaker than theorem equivalence;
  runtime/engine must not substitute string similarity.
- Caps, SDK behavior, independent routes, conflicts and essay fidelity require
  later executable proof; passing scaffold tests is not end-to-end completion.
- Originality/citation verification uses evidence acquisition then structured
  classification because citations and structured output cannot share one call.
- Console script registration precedes implementation; README must disclose this.

## Delta integration checkpoint

Both lanes are merged on main. Engine/runtime integration uses the engine's
AnalysisResult and immutable ports; mock CLI/e2e/export/cache replay is native.
Real provider testing has exercised build_t, targets, cuts and formalisation;
provider projection fixes and a USD 5 smoke cap are recorded in DECISIONS D1–D5.
Final run receipts, fresh-clone verification, audit and final revision belong in
`/home/dev/wt/shared/ara/delta-report.md`; historical lane gaps above are retained
for provenance and superseded by those executed integration receipts.
