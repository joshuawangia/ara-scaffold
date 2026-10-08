# ARA scaffold

ARA has a bank, immutable contracts, model runtime and CLI. At the runtime lane
base, engine modules are placeholders: the native engine factory must be connected
during integration. Runtime tests exercise the lifecycle with a test-only fake
engine and deterministic mock provider. No real-provider smoke is claimed here.
See PLAN.md and DECISIONS.md for ownership and limitations.

## Install

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/). From the repository root:

```sh
uv sync --locked
```

No remote is configured by alpha. The orchestrator owns private repository
creation/push; use its clone URL once available. Commands use repository-root
`bank/`, `schemas/`, `prompts/` and `config.yaml` resources.

## Test

```sh
uv run pytest
uv run python tools/negative_controls.py
uv run python tests/runtime/negative_controls.py
```

Tests use placeholder propositions only and make no network calls. Negative
controls temporarily modify owned source/schema files, verify tests go red,
restore them in `finally`, and rerun the same tests green. Run in a clean checkout,
without another writer. Evidence goes to gitignored `runs/alpha-proof/`.

## Runtime proof and smoke

Run the offline CLI lifecycle proof (two targets and their negations, route files,
short draft, audit, verification, export, deterministic cached replay):

```sh
uv run pytest tests/runtime/test_cli.py -q
```

The finite canned responses in `tests/fixtures/runtime/canned.json` are keyed by
call kind and full rendered-input hash. Missing entries fail loudly. The fake
engine in these tests proves orchestration only; it is never used by `ara run`.

After the engine integration adapter is connected, set `ANTHROPIC_API_KEY` in the
environment and run from the repository root:

```sh
uv run ara run --smoke
```

The default config uses Anthropic and `claude-opus-5`; SDK credentials are never
written to files or logs. Smoke uses a placeholder topic/literature, two candidates,
depth two, at most 24 nodes, a 300-word draft, one web search use and a 1,000,000-token
cap with USD 10 cost cap. These are caps, not expected consumption. Conservative
web-call admission reserves full model-context bounds; the ordinary 200k-token
cap can stop before verification. Change caps and pricing explicitly in config
for a real run. Ancillary rates/context assumptions still require billing review.

The real-provider path test is skipped unless both a key and an explicit network
opt-in are present; a skip is not a passing real-provider proof:

```sh
ARA_LIVE_TEST=1 uv run pytest tests/runtime/test_provider.py::test_real_provider_path -rs
```

This lane has no credential and has not executed that command against the service.
Full real-provider smoke and a fresh-clone end-to-end receipt remain integration
work. At this base `ara.engine.create_engine` is absent; native run exits nonzero
and writes the error plus methodology. See DECISIONS.md, “Runtime integration gap”.

## Run, select, feedback and export

```sh
uv run ara run --topic '<runtime topic>' --literature '<runtime literature path>' --audience '<audience>'
uv run ara select --run-dir runs/<run-id> --route '<route-id>' --human-minutes 2
uv run ara feedback --run-dir runs/<run-id> --text '<verbatim feedback>'
uv run ara export --run-dir runs/<run-id> --redact '<identifier>'
```

`run` freezes the commitment table, proposes ten targets by default, searches each
and its canonical negation, records conflicts/robustness, and waits for `select`.
Use `--named-position` to supply one exact position. `--run-dir` chooses a new empty
output directory; `--config` chooses runtime configuration. Selection without
`--route` and feedback without `--text` prompt interactively and measure elapsed
human time. Explicit `--human-minutes` is recorded separately. Smoke selects a
route automatically with a logged SYSTEM policy. Feedback is included in the next
draft request without changing the frozen commitments or selected graph.

Every command logs HUMAN argv and inputs verbatim, with timestamps. Every model
call records prompt, raw response, model/version, usage, cost, wall time and
accept/reject status. Budget exhaustion returns exit code 2, writes STOP and
`partial.json`, retains completed route files, and exports methodology. A transport
failure without usage records a reservation with unknown actual spend and blocks
resume; it is never reported as free. No output/cache file belongs in a commit.

Artifacts include `events.jsonl`, `events.anchor`, `commitments.json`, route JSON
and readable trees, `draft.unverified.json`, verified `draft.json`, and
`export/{essay.txt,methodology.md}`. No essay is exported until both audits and
verification succeed. Preserve the log and checkpoint together to detect edits
and truncation on resume. An interrupted append refuses startup. This is local
integrity detection, not a signed audit against someone who can rewrite both.

The essay export omits run metadata and node markers, and replaces explicit
`--redact` strings. It does not infer personal identities in prose. The methodology
preserves the full record and is not anonymised. To demonstrate log-only recovery
without recording a new human command or changing the report:

```sh
uv run python -c 'from pathlib import Path; from ara.runtime.export import export_run; export_run(Path("events.jsonl"), Path("recovered"))'
```

That function needs only the JSONL. Log-only export verifies the chain but cannot
prove that its tail was not deleted without the separate checkpoint. Full reports
include every prompt, response, engine decision, human action and accounting note.

## Shared contracts

- `ara.types`: frozen dataclasses and strict JSON codecs. Canonical formula text
  is normalized AST JSON, not a natural-language paraphrase or equivalence proof.
- `ara.ports`: synchronous proposer, formaliser, mapper, CQ answerer, repairer and
  event sink interfaces. Runtime effects sit behind these ports.
- `ara.bank.load_bank('bank')`: immutable versioned entries; validation rejects
  malformed schemas, undefined slots and duplicate ids across files.
- `schemas`: ten model response schemas and the standalone formula schema.
  JSON validation is local; no external references or remote resolution.

Bank schemes are normalized forms attributed to Walton, Reed & Macagno (2008).
Unverified page/chapter locators say unknown. They are not a verified transcription
of the complete book. Later engine licensing must check named-rule shape, scope,
substitution, entailment and T membership; scaffold validation proves none of those
search outcomes by itself. Graph status/frontier/edges are engine-owned claims,
not inferred by deserializing a graph.
