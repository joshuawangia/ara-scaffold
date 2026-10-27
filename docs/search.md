# Search, selection and writing

[Documentation index](README.md) · [Project README](../README.md)

## Pilot profile

With the environment credential set, supply your runtime topic and literature:

```sh
uv run ara run --profile pilot --topic 'P Q' --literature /path/to/literature.txt --run-dir runs/pilot
uv run ara select --run-dir runs/pilot
```

The pilot searches all 10 targets at depth 6 and node cap 500, then waits for
human route selection. `search_concurrency` (top-level configuration, default 4)
bounds independent target/polarity searches; set it to 1 for sequential searches.
Each search retains a separate sealed trace, and one writer serializes the event
chain. Worker events are durably journaled and published in input-target order,
positive then negative. Interrupted publication leaves accounting explicitly
incomplete and refuses paid resume until reconciled. In-flight model reservations
count against the run caps. Target proposal requests all targets in a batch. Vocabulary preflight may request
one correction if target symbols are disconnected from frozen T. For 20
similarly sized searches, four workers can reduce the search portion from 20 waves
to about five; proposal, forward/conflict analysis, solver checks, logging and
provider limits reduce the total speedup. This is an expected effect, not a
measured live-provider result.

A job whose provider/validation retries are exhausted does not cancel its
siblings. After the initial queue drains, failed jobs receive one more attempt in
input order, each with a fresh search engine and a logged retry. Both attempts
retain their accounting and trace evidence; publication remains in target/polarity
order. Global budget/context exhaustion, unknown API accounting and infrastructure
failures still stop the queue. Completed routes survive these stops, but
generation cannot proceed past the applicable budget/accounting refusal.

If a job still fails, its completed sibling routes remain available at
`awaiting_selection`. The console and methodology disclose partial search and
unavailable paired conflict analysis; missing work is not evidence of no
conflicts. An exhausted conflict-analysis call also retains the completed search
routes. If failed CLI calls left unknown usage, selection refuses by default. To
explicitly retain those reservations as upper bounds (not measured spend), use `uv
run ara select --run-dir runs/pilot --unknown-usage-policy count-at-reservation`.
This does not bypass context/token/USD admission or unresolved dispatched calls.

The pilot sets a 6,000-word hard maximum and rejects drafts below 4,500 words,
using the existing title-and-body whitespace count (bibliography excluded). The
writer targets about 5,400 words to leave counting margin. Pilot output allowances
are 20,000 tokens for the writer, 24,000 for each audit, 64,000 for evidence
search and 48,000 for citation/originality classification. These calls stream
through the SDK. Other calls retain 8,192 tokens. Per-kind
`<kind>_max_output_tokens` settings override the global limit in reservation,
dispatch and cache identity. DECISIONS.md records the observed token ratios and
sizing arithmetic.

Edit `pilot.cost_cap_usd` and `pilot.token_cap` in `config.yaml`, or supply your
own file with `--config`. Older custom configurations must add `essay_min_words`
(and a `pilot` mapping to use that profile); a missing minimum is not treated as
zero. Shipped per-run caps are USD 100 and 10,000,000 tokens; these are
operator-adjustable ceilings, not predicted usage or guaranteed completion
budgets. No separate aggregate spend guard exists in code. Retry reservations and
actual usage use the resolved profile caps. `--smoke` remains the short
automatic-selection profile and cannot be combined with `--profile`. The pilot
path and streaming request are tested offline; no live pilot completion is
claimed.

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

This reproducible example is offline. A normal run waits for human route
selection. The unmodified configuration requests ten targets, depth six and 500
nodes; its ordinary 200,000-token cap can refuse conservative web admission.
Review caps before a larger run.

```sh
uv run ara select --run-dir runs/example
uv run ara feedback --run-dir runs/example --text 'P'
uv run ara select --run-dir runs/example
uv run ara export --run-dir runs/example --redact 'operator-id'
```

For the real provider with topic/literature flags, the following command uses the
credential configured in [providers](providers.md#anthropic-api) and pauses before
selection/audit:

```sh
uv run ara run --config runs/example-config.yaml --provider anthropic --topic 'P Q' --literature tests/fixtures/runtime/smoke-literature.txt --run-dir runs/real-inputs
```

Selection prints the actual route ids and prompts for one. Enter an id from that
list. Feedback is passed to the next draft request; it does not mutate frozen T or
alter the licensed graph. `--route` supplies a selection without prompting;
`--named-position` on run accepts one exact position. Interactive elapsed human
time and explicit `--human-minutes` are logged separately. Smoke selects the first
CLOSED route (otherwise the first OPEN route) under a logged SYSTEM policy.

## Resume a stopped search

`uv run ara resume-search --run-dir runs/previous` verifies the stored run, frozen
commitments, targets, job journals and sealed search traces before creating a
provider. It publishes journal events in target/polarity order, restores completed
results and licenses, dispatches only unfinished jobs, and continues paired
analysis and route persistence to `awaiting_selection`. Completed searches are
never dispatched again. A repeated command on a fully completed search reports its
state without generation.

To recover publication and accounting while stopping before dispatch:

```sh
uv run ara resume-search --run-dir runs/previous --stop-before-dispatch
```

This command **appends recovery receipts to the supplied run**. Use a copy when
preserving a stopped run for an offline audit. The JSON result lists
`completed_jobs` and `jobs_to_rerun` using zero-based job indices. No provider is
created in this mode. A measured response interrupted during validation is
accounted once as incomplete; recovery does not mark its output accepted. Missing
evidence, changed hashes, incompatible targets, or an interrupted request without
a measured response refuse explicitly. Unsealed partial traces remain retained but
cannot establish a completed search.

Live resume retains the recorded configuration and provider gates. Use
`--codex-schema-preflight-log PATH` to supply current Codex proof and
`--unknown-usage-policy count-at-reservation` only for previously finalized
unknown-usage receipts. Neither option overrides missing measured evidence for an
interrupted search dispatch.

## Reuse a verified freeze

`ara fork-from-freeze --source-run runs/source --run-dir runs/fork` copies the
verified event-chain prefix through its single freeze and the exact frozen
artifacts. The source is read-only. The new run gets its own cache, proposes
fresh targets with current code, performs native paired search, and waits for
selection. It preserves historical accounting once and refuses changed chains,
anchors, commitments, catalogues, or bank versions. The destination must be
empty and separate from the source. `--codex-schema-preflight-log`, `--provider`,
and `--unknown-usage-policy` are explicit overrides; a real Codex rerun still
requires a current successful schema preflight.

Target proposals request own theses supported or refuted by at least two
commitments, preferably from different papers. Bounded solver checks reject
valid targets and targets whose positive or negative form follows from any
single frozen commitment, including padded restatements. Each check allows
1,000 ms; alpha-equivalent formula hashes share a bounded cache. Solver unknowns
and timeouts remain unresolved and are excluded. One shared proposal correction
is allowed; remaining exclusions and their reasons are logged.

Each target also receives an isolated own-thesis classification on the same
provider. Only `own_thesis` passes; `attributed_report` and `unclear` are disclosed
and excluded. Deterministic attitude/report phrases and top-level attribution
predicates identified by frozen catalogue definitions also cause rejection.
These checks do not prove originality or faithful text/formula translation.
A second disconnected-vocabulary result stays disclosed.

Route lists and reports offer `CLOSED-derived` by default only when a licensed
inference has at least two distinct reachable frozen supports and no single
support entails the root. CQ evidence counts; assumptions and duplicate or
alpha-equivalent supports do not inflate the count. Other closed routes are
labelled `CLOSED-single-support`, `CLOSED-contribution-unresolved`, or
`CLOSED-attributed-report`, and require an explicit `--route`. Engine licenses,
statuses, and graph codecs are unchanged. This contribution check does not
prove novelty, minimality among larger support subsets, or independence across
papers. Legacy graphs without frozen inputs can use their leaf formulas for
display; unavailable CQ evidence remains unresolved.
