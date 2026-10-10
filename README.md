# ARA

ARA is a Python CLI for bank-constrained symbolic search. The deterministic engine
checks bank instantiation, Z3 entailment, frozen commitments and route closure.
The model proposes cuts through validated, cached, logged calls. Both polarities,
route independence, bounded forward consequences and conflicts use one engine API.

## Install and test

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/). Obtain a clone from the
operator and run every command below from its repository root. The operator owns
private remote publication; installation uses the committed lockfile and local
bank, schemas and prompts.

```sh
uv sync --locked
uv run pytest
uv run python tests/integration/negative_controls.py
```

The default suite is offline. One separately gated live-provider test is skipped.
The integration test starts the actual CLI in subprocesses, checks persisted
artifacts and engine analysis, exports from logs, and proves cached graph replay.
Negative controls disable production behavior, require red tests, restore it and
require green tests. Run them without another checkout writer.

## Offline smoke

```sh
uv run ara run --smoke --provider mock --run-dir runs/mock-smoke
uv run ara export --run-dir runs/mock-smoke
```

This uses the real engine and finite canned responses keyed by call kind and
rendered-input hash. It needs no credential or network. Mock responses cover the
shipped placeholder smoke and the feedback example below; other inputs fail explicitly. Mock ledger costs
are simulated and incur no provider spend.

## Real smoke

A historical clean-clone real smoke completed with both audit passes, route graphs, draft,
log and essay/methodology export: 155,636 input tokens, 11,211 output tokens and
USD 1.058455. Every call was served by `claude-opus-5`. Default server fallbacks
were enabled, but no fallback hop was reported. Mock tests and production-wire
controls verify fallback billing, provenance and final-chain refusal handling.
The placeholder evidence stage returned without invoking a web search; this run
does not prove live external-source retrieval. Full receipts are in the external
delta report. An independent later trial refused the former audit request. The
current writer and auditor share an outline containing propositions, inference
links with rule/scheme names, and answered critical questions. Graph bookkeeping
is excluded. The audit labels additional premises or inferences; transitions
asserting neither are allowed. Code computes coverage and the verdict. It does not request a reconstruction of text production.
Fresh-clone outcomes for this revision are in the external zeta report; observed
successes do not guarantee that a provider will never refuse. Earlier failed runs and their costs remain recorded there.

Set `ANTHROPIC_API_KEY` in your environment, or source the operator's credential
file in the same shell as the command:

```sh
set -a; . ~/.config/ara/anthropic.env; set +a
uv run ara run --smoke --run-dir runs/real-smoke
```

Default provider/model: Anthropic / `claude-opus-5`, using the official SDK,
adaptive thinking and structured output with strict local schema checks.
`fallbacks: [claude-opus-4-8]` explicitly enables the June 2026 refusal-fallback
API: the primary remains Opus 5 and the server can re-run a refused call on Opus
4.8. `fallbacks: off` disables both the fallback parameter and beta header. The
old scalar `default` configuration is rejected; update existing runtime configs
to the list form. A final refusal from the whole chain is logged and never retried.
Logs retain the requested and actual serving models, switch blocks and fallback
usage iterations. Each iteration is priced at its model's configured rates;
unknown model/cache prices stop with explicit unknown-spend accounting.
Methodology lists actual serving models by call kind and discloses fallback use.
Server-side fallback attempts may add billable usage beyond the primary-model
admission reservation; post-call accounting checks the whole chain. Every
structured prompt also contains the full local response schema. Generated
formula ASTs are bounded to depth two by config; local AST/solver semantics support
deeper formulas, but larger generation grammars can exceed the API compiler limit.
Smoke uses placeholder literature, two targets, depth one, eight search nodes per
polarity, a 300-word draft, an 8,192-token output allowance and at most one web search per evidence call. Its caps
are **USD 5 and 1,000,000 tokens**, including conservative admission reservations.
These are limits, not expected usage. Smoke permits up to three explicitly
logged attempts for a response that fails local validation; every attempt reserves
and records its own usage. Invalid responses are never cached. Refusals, transport
failures, output-token stops, negative essay audits and bank-license failures are not retried. Web admission reserves the configured
200,000-token context bound for each potential server iteration. Prices and that
bound are explicit configuration assumptions; actual provider usage is recorded.
A reservation is checked before each call and actual usage after it. An oversized
actual charge cannot be undone; STOP prevents subsequent calls.

Use a new empty `--run-dir` when repeating a command. Omitting it generates a run
id automatically. Reusing the cache avoids paid calls only when all keyed inputs
match. Use one paid writer per cache; divergent concurrent outputs fail explicitly.
Delete neither failed logs nor their accounting to disguise a retry.

## Topic, literature, selection and feedback

The following reproducible example uses placeholders. Replace the topic and file
path with your own runtime inputs for substantive work. They are logged in full.
First write a bounded example configuration under the ignored runs directory:

```sh
uv run python - <<'PY'
from pathlib import Path
import yaml
config = yaml.safe_load(Path('config.yaml').read_text())
config.update(config['smoke'])
config['provider'] = 'mock'
Path('runs').mkdir(exist_ok=True)
Path('runs/example-config.yaml').write_text(yaml.safe_dump(config))
PY
uv run ara run --config runs/example-config.yaml --topic 'P Q' --literature tests/fixtures/runtime/smoke-literature.txt --run-dir runs/example
```

This reproducible example is offline. A normal run waits for human route selection. The unmodified configuration
requests ten targets, depth six and 500 nodes; its ordinary 200,000-token cap can
refuse conservative web admission. Review caps before a larger run.

```sh
uv run ara select --run-dir runs/example
uv run ara feedback --run-dir runs/example --text 'P'
uv run ara select --run-dir runs/example
uv run ara export --run-dir runs/example --redact 'operator-id'
```

For the real provider with topic/literature flags, the following command uses
the credential from the earlier shell step and pauses before selection/audit:

```sh
uv run ara run --config runs/example-config.yaml --provider anthropic --topic 'P Q' --literature tests/fixtures/runtime/smoke-literature.txt --run-dir runs/real-inputs
```

Selection prints the actual route ids and prompts for one. Enter an id from that
list. Feedback is passed to the next draft request; it does not mutate frozen T
or alter the licensed graph. `--route` supplies a selection without prompting;
`--named-position` on run accepts one exact position. Interactive elapsed human
time and explicit `--human-minutes` are logged separately. Smoke selects the first
CLOSED route (otherwise the first OPEN route) under a logged SYSTEM policy.

## Artifacts and logging

Each run writes `commitments.json`, `routes/*.json` and matching readable trees,
`events.jsonl` with `events.anchor`, an unverified draft and, after audit and
verification, `draft.json` and `export/{essay.txt,methodology.md}`. No essay is
exported before verification and the second audit pass. OPEN frontiers remain
explicit in route artifacts; essays present the argument conditionally on its
stated premises without narrating software metadata. Budget STOP returns exit 2, preserves partial graphs,
writes `partial.json` and exports methodology. A provider failure without usage
charges a labelled conservative reservation, reports unknown actual spend and
refuses resume. Post-dispatch serialization, parsing or completion-log failures
likewise stop with an incomplete record and reservation-based cap checks.
Methodology explicitly marks incomplete totals and outstanding dispatches. A
persistent storage failure may prevent new appends; preserve the log/checkpoint
and reconcile before starting another run.

The append-only JSONL records full prompts/responses, model id/version, token and
server-tool usage, cost, time, cache hits, rejections, engine decisions and every
HUMAN command/input verbatim. Methodology derives from this log alone. Preserve
its checkpoint to detect tail truncation during resume; rewriting both files can
forge the local chain. Interrupted appends refuse startup.

Essay export removes run metadata and node markers and replaces literal
`--redact` identifiers. It does not discover identities in prose. Methodology
intentionally retains the complete record and is not anonymised. Web evidence
and model audits are bounded assessments, not exhaustive originality or source
truth proofs. Sentence inventory and id validation cannot prove that a valid-id
label is semantically correct; the simple deterministic splitter also splits
abbreviations at punctuation followed by whitespace. Formal entailment does not establish faithful text translation or
CQ truth. Search and forward results are bounded by configuration; independent
route counts cover discovered routes. Scheme forms cite Walton, Reed & Macagno
(2008); unverified page/chapter locators remain explicitly unknown.

## Content rule

No philosophical argument, premise, distinction, example or view belongs anywhere
in tracked code, prompts, tests, fixtures, docs or commit messages. Bank entries
are forms with slots and critical questions. Fixtures contain placeholders only.
Supply substantive topic/literature at runtime. Runs, caches, generated drafts and
logs are gitignored and must never be committed. Credentials come only from the
environment and must never be written or logged. See AGENTS.md and DECISIONS.md.
