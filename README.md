# ARA

ARA is a Python CLI for bank-constrained symbolic search. The deterministic engine
checks bank instantiation, Z3 entailment, frozen commitments and route closure.
The model proposes cuts through validated, cached, logged calls. Both polarities,
route independence, bounded forward consequences and conflicts use one engine API.

## Install and test

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/). Obtain a clone from the
operator and run every command below from its repository root. The operator owns
private remote publication; installation uses the committed lockfile and local
bank, schemas and prompts.

```sh
uv sync --locked
uv run pytest
uv run python tests/integration/negative_controls.py
```

The default suite is offline. Two separately gated live-provider tests are skipped.
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
is excluded. Before the audit, writer validation requires every node marker and
at least two text tokens after markers are removed. Invalid drafts use up to four
identical-input writer attempts; an adverse audit still ends the run. The audit
labels additional premises or inferences; transitions
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
polarity, a 300-word draft with a 150-word minimum, an 8,192-token output allowance
and at most one web search per evidence call. Its caps
are **USD 5 and 1,000,000 tokens**, including conservative admission reservations.
These are limits, not expected usage. The writer instruction targets about 90% of the hard word maximum to leave
counting margin, while retaining the minimum. Validation counts all title/body
whitespace tokens, including markers. The writer permits one initial attempt plus
three retries for local validation
failures, including contentless, under-length and over-limit drafts. Each retry
sends identical inputs without validation feedback; every attempt records its
number, rejection reason, tokens and cost, and must fit the configured caps.
Other smoke call kinds retain up to three attempts with validation feedback.
Invalid responses are never cached. Refusals, transport
failures, output-token stops, negative essay audits and bank-license failures are not retried. Web admission reserves the configured
200,000-token context bound for each potential server iteration. Prices and that
bound are explicit configuration assumptions; actual provider usage is recorded.
A reservation is checked before each call and actual usage after it. An oversized
actual charge cannot be undone; STOP prevents subsequent calls.

Use a new empty `--run-dir` when repeating a command. Omitting it generates a run
id automatically. Reusing the cache avoids paid calls only when all keyed inputs
match. Use one paid writer per cache; divergent concurrent outputs fail explicitly.
Delete neither failed logs nor their accounting to disguise a retry.

## Pilot profile

With the environment credential set, supply your runtime topic and literature:

```sh
uv run ara run --profile pilot --topic 'P Q' --literature /path/to/literature.txt --run-dir runs/pilot
uv run ara select --run-dir runs/pilot
```

The pilot searches all 10 targets at depth 6 and node cap 500, then waits for
human route selection. It sets a 6,000-word hard maximum and rejects drafts below
4,500 words, using the existing title-and-body whitespace count (bibliography
excluded). The writer targets about 5,400 words to leave counting margin. Pilot output allowances are 20,000 tokens for the writer, 24,000 for each
audit, 64,000 for evidence search and 48,000 for citation/originality
classification. These calls stream through the SDK. Other calls retain 8,192
tokens. Per-kind `<kind>_max_output_tokens` settings override the global limit
in reservation, dispatch and cache identity. DECISIONS.md records
the observed token ratios and sizing arithmetic.

Edit `pilot.cost_cap_usd` and `pilot.token_cap` in `config.yaml`, or supply your
own file with `--config`. Older custom configurations must add `essay_min_words`
(and a `pilot` mapping to use that profile); a missing minimum is not treated as
zero. Shipped per-run caps are USD 100 and 10,000,000 tokens;
these are operator-adjustable ceilings, not predicted usage or guaranteed
completion budgets. No separate aggregate spend guard exists in code. Retry
reservations and actual usage use the resolved profile caps. `--smoke` remains
the short automatic-selection profile and cannot be combined with `--profile`.
The pilot path and streaming request are tested offline; no live pilot completion
is claimed.

## Extract literature from PDFs

Place manifest-listed PDFs in `literature/fulltext/`, then inspect a local estimate:

```sh
uv run ara extract --profile extraction --manifest literature/manifest.yaml --fulltext-dir literature/fulltext --provider mock --estimate-only --run-dir runs/extraction-estimate
```

With credentials configured, extract the chosen sources through the normal logged
model boundary. `p` below is a placeholder to replace with a manifest id; omit
`--paper-id` only when ready to extract the entire manifest.

```sh
uv run ara extract --profile extraction --manifest literature/manifest.yaml --fulltext-dir literature/fulltext --paper-id p --run-dir runs/extraction
uv run ara run --profile pilot --topic 'P' --literature runs/extraction/literature.extracted.txt --run-dir runs/pilot-extracted
```

The explicit extraction profile sets both enclosing and extraction cost caps to
USD30 and the token cap to 6000000. Ordinary defaults remain USD10/200000 tokens.
Preflight prints `planned batch exceeds enclosing caps` if its pages × 1500
input-token estimate plus prompt overhead and output allowances exceed those
limits. Estimates exclude retries and server fallbacks; actual requests reserve
and account separately. Use an isolated cache for the planned extraction run.

Each paper supplies at most four central claim/argument items, each at most 400
characters, with author/reported/attacked attribution. The escaped assembled entry
is additionally limited to 2200 UTF-8 bytes. Validation retries shorten model
output; code never slices text or silently drops a paper. This is a bounded central
selection, not an exhaustive inventory. Full bibliography and page diagnostics
remain in `<id>.extraction.json` and the log; the literature file carries compact
source-id/items/status entries. Citation ids such as `p:pdf:1-2` use physical PDF
pages, not printed page labels.

A 53-paper maximum-size offline CLI fixture uses 124441 conservative input
byte-tokens including instructions and schemas. The generated-literature build-T
output allowance is 64000 tokens, sized for up to 212 commitments; total 188441
fits the 200000 context with margin. `extracted_build_t_max_output_tokens` controls
this allowance; it does not change ordinary build-T. Every actual build-T and
extraction dispatch counts the full request via the provider and refuses a context
overflow with a logged STOP. Long custom topic/audience text or validation feedback
can still exceed context. PDF input bytes are warnings only, never a hard refusal.

pypdf does not perform OCR. Blank pages are recorded and preserve numbering while
readable pages proceed. Image/form pages with fewer than 200 text characters, and
painted pages with no text, are flagged and excluded from claim support. Their
papers are explicitly `partial`, with affected page numbers in outcomes, logs and
methodology. An entirely visual paper is partial with no items and no model call.
This heuristic cannot prove text completeness or correct reading order.
Missing/unreadable PDFs default to `record only, not extracted`; `--missing refuse`
stops instead. Model/validation/budget/context failures always stop and preserve
methodology. Record-only entries supply no commitments, and an all-record-only
collection cannot build T. Partial entries supply only their readable-page items.

Import the **original extraction artifact directly**. Keep its text, provenance
sidecar and original source log available at the recorded path. The loader verifies
and imports its receipts with SYSTEM/MODEL labels. Cross-run cached re-extraction
without original receipts is explicitly marked incomplete and refused at import;
zero new spend is not complete production accounting. Same-log replay with its
original receipt remains usable. Do not strip the provenance header to bypass a
refusal. Artifacts predating this bounded projection must be regenerated.

Methodology separates local and inherited usage/cost/human time and gives imported
receipts stable ids. Re-importing the same receipt within a log is idempotent;
aggregate reports should deduplicate inherited receipt ids. Imported charges still
count against the downstream run budget. PDF bytes partition the cache even when
text is identical. Generated artifacts and PDFs remain gitignored. Structural
page/citation checks do not establish semantic support or accurate attribution.

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
are forms with slots and critical questions. Under round-2 R4 in DECISIONS.md,
`tests/fixtures/verification` holds the authorized non-philosophical
software-engineering known-case recordings. Every other fixture stays
placeholder-only.
Supply substantive topic/literature at runtime. Runs, caches, generated drafts and
logs are gitignored and must never be committed. Credentials come only from the
environment and must never be written or logged. See AGENTS.md and DECISIONS.md.
