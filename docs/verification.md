# Verification and evidence

[Documentation index](README.md) · [Project README](../README.md)

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/). Obtain a clone from
the operator and run every command below from its repository root. The operator
owns private remote publication; installation uses the committed lockfile and
local bank, schemas and prompts.

```sh
uv sync --locked
uv run pytest
uv run python tests/integration/negative_controls.py
```

The default suite is offline. Two live-provider tests and two installed-weight OCR
tests are opt-in; the default suite skips all four. The integration test starts
the actual CLI in subprocesses, checks persisted artifacts and engine analysis,
exports from logs, and proves cached graph replay. Negative controls disable
production behavior, require red tests, restore it and require green tests. Run
them without another checkout writer.

## Historical live smoke

A historical clean-clone real smoke at `a20e03c` completed with both audit passes,
route graphs, draft, log and essay/methodology export: 155,636 input tokens,
11,211 output tokens and USD 1.058455. Every call was served by `claude-opus-5`.
Default server fallbacks were enabled, but no fallback hop was reported. Mock
tests and production-wire controls verify fallback billing, provenance and
final-chain refusal handling. The placeholder evidence stage returned without
invoking a web search; this run does not prove live external-source retrieval.
Full receipts are in the external delta report. An independent later trial refused
the former audit request. The current writer and auditor share an outline
containing propositions, inference links with rule/scheme names, and answered
critical questions. Graph bookkeeping is excluded. Before the audit, writer
validation requires every node marker and at least two text tokens after markers
are removed. Invalid drafts use up to four identical-input writer attempts; an
adverse audit still ends the run. The audit labels additional premises or
inferences; transitions asserting neither are allowed. Code computes coverage and
the verdict. It does not request a reconstruction of text production. Later
historical fresh-clone outcomes were recorded in the external zeta report;
observed successes do not guarantee that a provider will never refuse. Earlier
failed runs and their costs remain recorded there.

## What a check establishes

Resolve current behavior from the registered CLI, runtime bodies and owning tests.
Requirements and operator decisions define what ARA owes; missing implementation
is a gap, not permission to narrow that requirement. Decision-log entries retain
their original revision and proof scope.

- Static checks establish file, schema or contract shape.
- Offline pytest checks deterministic behavior with placeholders, recorded responses
  or fake transports. The integration suite drives the CLI and inspects persisted
  graphs, logs and exports; it does not establish live provider behavior.
- A product claim needs the real entry point, a durable result, an expectation
  independent of the implementation, and a negative control that breaks the
  determining production behavior. Run mutation controls sequentially, restore
  the source and rerun the relevant tests. An undetected mutation is a proof gap.
- Live provider, installed OCR and source-quality checks need their own receipts,
  exact revision/configuration and retained failures. Model judgments are bounded
  assessments, not deterministic release gates.

Every handoff must separate checks executed now, historical receipts, proposed
checks and unresolved claims. Test counts alone do not prove extraction fidelity,
useful formalization, exhaustive search, live isolation or campaign completion.
[PLAN](../PLAN.md) lists the current gaps; the external documentation report
records this change's checks. No paid or installed-weight proof was run for this
rewrite.
