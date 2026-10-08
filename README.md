# ARA scaffold

Alpha establishes the bank and shared contracts for a Python CLI. Engine search,
provider calls and CLI commands are **not implemented yet**. No real provider run
has been performed by this phase. See PLAN.md for the implementation/proof owners
and DECISIONS.md for fixed interfaces and limitations.

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
```

Tests use placeholder propositions only and make no network calls. Negative
controls temporarily modify owned source/schema files, verify tests go red,
restore them in `finally`, and rerun the same tests green. Run in a clean checkout,
without another writer. Evidence goes to gitignored `runs/alpha-proof/`.

## Smoke (next integration phase)

The console entrypoint is registered, but `ara.runtime.cli:main` is intentionally
absent until the runtime lane implements it. This command is a future interface,
not an alpha proof:

```sh
uv run ara run --smoke
```

Set `ANTHROPIC_API_KEY` in the environment; never place it in a tracked file or
log. Smoke will use placeholder topic/literature, 2 candidates, depth 2 and a
300-word draft. Inspect route graphs, draft, full JSONL and log-derived methodology
under gitignored `runs/`; record actual tokens and cost. Provider and model are
configured in `config.yaml`. Ancillary tool/cache pricing awaits provider review.

## Real run (next integration phase)

```sh
uv run ara run --topic '<runtime topic>' --literature '<runtime literature path>'
uv run ara select --help
uv run ara feedback --help
uv run ara export --help
```

Exact selection, feedback and export flags belong to the runtime lane. Human
inputs must be timestamped and logged verbatim as HUMAN. Generated content,
drafts, logs and cache are never committed. Final documentation must include an
executed fresh-clone test and a real-provider smoke receipt.

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
