# Search, selection and writing

[Documentation index](README.md) · [Project README](../README.md)

## Pilot profile

With the environment credential set, supply your runtime topic and literature:

```sh
uv run ara run --profile pilot --topic 'P Q' --literature /path/to/literature.txt --run-dir runs/pilot
uv run ara select --run-dir runs/pilot
```

The pilot requests 10 target candidates and searches those that pass preflight
at depth 6 and node cap 500, then waits for human route selection. Excluded
candidates remain disclosed; the accepted set can contain fewer than ten or none.

`search_concurrency` (top-level configuration, default 4)
bounds independent target/polarity searches; set it to 1 for sequential searches.
Each search retains a separate sealed trace, and one writer serializes the event
chain. Worker events are durably journaled and published in input-target order,
positive then negative. Interrupted publication leaves accounting explicitly
incomplete and refuses paid resume until reconciled. In-flight model reservations
count against the run caps.

Target proposal requests candidates in a batch. Vocabulary and contribution
checks share one correction request; each candidate also receives the own-thesis
classification described below. If all ten candidates pass, there are 20 polarity
searches. For 20 similarly sized searches, four workers can reduce that portion
from 20 waves to about five; proposal, forward/conflict analysis, solver checks,
logging and provider limits reduce the total speedup. This is an expected effect, not a
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

Selection prints every route with its classification. It prompts only when a
`CLOSED-derived` route is available; enter an offered route ID. Other displayed
routes require explicit `--route ID`. If no derived route is available, the
command reports that fact without creating a writer provider.

Feedback is passed to the next draft request; it does not mutate frozen T or
alter the licensed graph. `--route` supplies a selection without prompting;
`--named-position` on run accepts one exact position. Interactive elapsed human
time and explicit `--human-minutes` are logged separately. Smoke selects only the
first `CLOSED-derived` route under a logged SYSTEM policy. With no eligible route,
it waits at selection without writing an essay.

## Target proposal and triviality

Target proposals request own theses supported or refuted by at least two distinct
commitments, preferably from different papers. Inputs include frozen commitments,
explicit conditionals, shared signatures and available catalogue definitions.
The preferred paper count is a model instruction, not a deterministic guarantee.

Bounded solver checks test the target and its negation with no premises and with
each frozen commitment separately. A valid formula or a formula entailed by one
commitment is excluded, including direct universal instances and padded
restatements. Each check has a 1,000 ms timeout. The 8,192-entry cache keys premise
and conclusion hashes plus timeout; bound-variable renaming shares hashes while
free and bound variables stay distinct. Checks stop on a decisive exclusion;
at most `2 * (1 + len(T))` checks are needed per candidate. Unknowns and timeouts
cannot authorize a target.

Each candidate also receives an isolated `classify_target` request on the same
provider. It sees the target text and a structural formula rendering through verified
content definitions, without source attribution, proposal history or rationale.
Own-voice synthesis may draw on source claims; reporting what someone holds
remains an attributed report. Legacy content definitions stay unavailable.
Only `own_thesis` passes; `attributed_report` and `unclear` are disclosed and
excluded. Deterministic attitude/report phrases and top-level attribution
predicates identified by catalogue definitions also reject candidates. Missing
legacy catalogues remain unavailable; code does not invent their definitions.
All classification dispositions, cache replays and solver receipts are logged.

Vocabulary and triviality share one proposal correction. Remaining exclusions
and reasons are retained; a second disconnected-vocabulary result is disclosed
without automatically excluding an otherwise accepted target. `--named-position`
preserves the requested text and still undergoes these checks. Neither the model
classification nor the solver checks prove originality, source support or faithful
text/formula translation. See `ara/runtime/calls.py:916`,
`ara/runtime/target_policy.py:42` and `ara/runtime/contribution.py:45`.

The classifier schema is part of Codex preflight. Historical 15-case receipts
must be refreshed for the current 16-case contract before live use; a changed
manifest or model/configuration can also invalidate proof. See
[provider preflight](providers.md#codex-cli).

## Route classification and selection

Contribution labels supplement the engine's unchanged `CLOSED`/`OPEN` status,
bank licenses and graph format. `CLOSED-derived` requires a reachable licensed
inference, at least two distinct frozen supports and solver checks that rule out
validity without support and entailment of the root by any one support. The
route check tests the root polarity; target preflight tests both polarities.

CQ evidence counts as support. Assumptions and repeated or alpha-equivalent
support formulas do not inflate the count. The check traverses reachable nodes;
it does not establish minimality of larger support subsets, independence across
papers or semantic novelty.

| Display label | Meaning for selection |
| --- | --- |
| `CLOSED-derived` | Passes the contribution policy; offered by default |
| `CLOSED-single-support` | Lacks the required inference/distinct supports, is valid without support, or follows from one support; explicit `--route` required |
| `CLOSED-contribution-unresolved` | Required support or a solver verdict is unavailable; explicit `--route` required |
| `CLOSED-stance-crossing` | A recorded reported/attacked support is used as a global premise or CQ evidence; explicit `--route` required |
| `CLOSED-attributed-report` | Reporting language is detected during the closed-route contribution check; explicit `--route` required |
| `OPEN` or another non-closed status | Retains its engine status and disclosed frontier; explicit `--route` required |

An explicit route argument chooses a displayed route but does not bypass budgets,
provider gates, audits or verification. Graph-only legacy rendering can recover
leaf formulas; missing CQ evidence remains unresolved. Native publication,
selection and reports use frozen T when available. Reports keep the full
contribution receipt separate from search target/polarity metadata; see
[reporting](reporting.md#route-classification-and-contribution-receipts).

## Reuse a verified freeze

```sh
uv run ara fork-from-freeze --source-run runs/source --run-dir runs/fork
```

The command verifies the source's entire event chain and required anchor,
requires one freeze and matching bank versions, and compares commitments plus
any frozen catalogue with their receipts. It atomically installs the exact event
prefix through the freeze and the frozen artifacts in an empty separate directory.
The destination cannot be inside the source or contain it. Source files are read
without creating locks or changing their contents.

The fork retains source topic/configuration, appends its configuration and
prefix-accounting receipts, and uses its own cache. It copies no target/search
receipts after the freeze. Current target proposal and native paired search then
run, ending at `awaiting_selection`; construction and a second freeze do not run.
The source needs a verified freeze, not a completed essay.

`--provider`, `--codex-schema-preflight-log` and `--unknown-usage-policy` are the
explicit overrides; `--human-minutes` records operator-reported time. There is no
fork `--config`, `--model`, `--profile` or cap override. A provider override does
not automatically change stored model/stage settings. A live Codex rerun needs
current successful schema preflight, including `classify_target`.

This command can make paid calls. Historical MODEL usage is retained once as
imported history; ordinary API/subscription accounting rules still apply. Forking
is not a budget reset. Keep the source and inherited provenance for audit, and
use [combined reporting](reporting.md) to deduplicate original receipts across
runs. See `ara/runtime/freeze_fork.py:25` and `ara/runtime/cli.py:185`.

Use a fork to propose new targets from a retained freeze. Use `resume-search` to
continue the fork's already-recorded search jobs. A fork that stopped before it
recorded a valid target/job inventory is not eligible for search resume; preserve
its failed receipts rather than treating it as a completed rerun.

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

Live resume retains recorded targets and provider gates. For a fork, it uses the
latest `freeze_fork_configuration`, including the fork cache and recorded
overrides; it does not fall back to the original source-run configuration. It
does not repeat target proposal or apply current target preflight to replace the
stored candidate set. Resume requires a nonempty valid target inventory and
matching job/trace receipts (`ara/runtime/search_resume.py:265`). Use
`--codex-schema-preflight-log PATH` to supply current Codex proof and
`--unknown-usage-policy count-at-reservation` only for previously finalized
unknown-usage receipts. Neither option overrides missing measured evidence for an
interrupted search dispatch.

## Source stance and content definitions

New rich freezes bind `commitment-provenance.json` to exact T and catalogue hashes.
Its verified `definition_semantics=content` marker distinguishes content definitions
from source attribution. The source text and author/page/evidence linkage remain
in provenance. Search cache identities include the provenance hash.

With verified metadata, only `endorsed` source content can serve as a global
premise or CQ evidence. This means the source author's assertion, not independent
verification of its truth. `reported` and `attacked` content remains available
for bank-licensed scoped hypotheses. It cannot silently terminate an ordinary
premise, seed a closed-route forward pass, or become an asserted negation.
Rejected uses emit `STANCE_CROSSING`; route receipts disclose crossings and scoped
source roles. Historical crossing routes are excluded from default selection.

Missing legacy metadata means unavailable stance, and retains legacy behavior.
A present corrupt sidecar or a missing/mismatched recorded sidecar refuses search.
Forks preserve its exact bytes and prefix receipt; resume validates both before
provider creation and refuses closed results that cross a known stance.

The shared writer/auditor outline carries source stance, attribution and scope
role for referenced commitments when provenance is verified. Explicit selection
does not erase these roles. The prompts require reported/attacked material to
remain reporting or conditional hypotheses, including in dependent conclusions;
the model audit treats endorsement promotion as an added inference. This is a
model-audited writing obligation, not a deterministic semantic guarantee.
