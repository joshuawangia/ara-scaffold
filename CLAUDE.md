# ARA repository rules

No philosophical argument, premise, distinction, example, or view may appear in
committed code, prompts, tests, fixtures, docs, or commit messages. Use only
placeholder propositions (P, Q, R, S, F(x), a, b), except for the authorized
verification recordings described below. Bank entries are forms with
slots and critical-question templates, never filled real-world examples.

A step is licensed only by instantiating a versioned bank entry. There is no
fallback license. The deterministic engine imports shared types and ports, makes
no provider calls, and checks both rule shape and Z3 entailment for deductions.
T has one construction lifecycle, one freeze: cited working commitments are
frozen before search; rich source evidence remains immutable. Model output enters
only after schema validation through cached, logged runtime calls.

Every run has append-only JSONL: timestamp, stage, model id/version, full prompt,
full response, usage tokens (including cache and server tools), cost, wall time,
and every licensed/discarded engine decision with reason. Rejected outputs and
budget STOP events are logged. HUMAN inputs from run/select/feedback/export are
logged verbatim with timestamps and labelled HUMAN; elapsed and operator-reported
human time are distinguished. Export methodology derives from logs alone.
Never write secrets to files or logs. API keys come from the environment;
subscription adapters read existing host credentials through the isolated
transport described in [providers](docs/providers.md). Do not copy or rotate them.
Runs, cache, generated drafts and logs stay gitignored, never committed.

Python >=3.13; uv with committed lockfile; typed immutable shared contracts;
pytest with no network. Under round-2 R4 in DECISIONS.md,
`tests/fixtures/verification` holds the authorized non-philosophical
software-engineering known-case recordings. Every other fixture stays
placeholder-only. Keep engine/runtime imports separate. Record decisions in
DECISIONS.md. Test load-bearing behavior with production-wire negative controls,
restore and rerun. No silent operational fallbacks.

Read [PLAN.md](PLAN.md) for current gaps and [SOURCE_MAP.md](SOURCE_MAP.md) for
ownership, callers and tests. [docs/README.md](docs/README.md) routes operating
guides and defines context layers. Keep one canonical document per concern;
link to it instead of duplicating procedures. Historical receipts do not prove
current behavior. Handoffs name the tested revision and unresolved claims.
