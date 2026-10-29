# Search, selection and writing

[Documentation index](README.md) · [Project README](../README.md)

## Pilot profile

With the environment credential set, supply your runtime topic and literature:

```sh
uv run ara run --profile pilot --topic 'P Q' --literature /path/to/literature.txt --run-dir runs/pilot
uv run ara select --run-dir runs/pilot
```

The pilot requests a pool of 20 target candidates per attempt, retains up to 10
that pass preflight, and searches them at depth 6 and node cap 500 before human
route selection. Excluded
candidates remain disclosed; the accepted set can contain fewer than ten or none.

`search_concurrency` (top-level configuration, default 4)
bounds independent target/polarity searches; set it to 1 for sequential searches.
Each search retains a separate sealed trace, and one writer serializes the event
chain. Worker events are durably journaled and published in input-target order,
positive then negative. Interrupted publication leaves accounting explicitly
incomplete and refuses paid resume until reconciled. In-flight model reservations
count against the run caps.

Target proposal permits an initial batch and at most two corrections. Passing
candidates remain retained in stable attempt/response order; later batches fill
remaining places. Each candidate receives the own-thesis classification below. If all ten candidates pass, there are 20 polarity
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
commitments from at least two distinct papers. Inputs include frozen commitments,
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

A bounded semantic novelty check rejects any classical consequence of the whole
frozen T, regardless of connective or quantifier wrappers. Thus Q from
T={P, P -> Q} remains a valid modus-ponens deduction but is not a novel target.
At least one atom/application absent from T's formulas must also be essential:
replacing its occurrences by true or false must change target truth under T.
Both substitutions are checked with cached Z3 queries bounded to 1,000 ms each;
unknown/timeout refuses. Bound-variable keys preserve scope and alpha identity.
Receipts disclose the full basis, each substitution and essential applications.
No syntactic main-consequent shortcut grants novelty.

Each candidate also receives an isolated `classify_target` request on the same
provider. It sees the target text and a structural formula rendering through verified
content definitions, without source attribution, proposal history or rationale.
Own-voice synthesis may draw on source claims; reporting what someone holds
remains an attributed report. Legacy content definitions stay unavailable.
Acceptance additionally requires `novelty=new_assertion` and `fidelity=matches`.
The same logged classifier sees the entire T content list and rendered target
content. It rejects restatement, renaming, definitional packaging, text/formula
mismatch and uncertain judgments. These model judgments are not semantic proofs.
Only `own_thesis` passes; `attributed_report` and `unclear` are disclosed and
excluded. Lexical attitude/report matches in text and used catalogue definitions are
advisory: every hit is logged and passed to the classifier as evidence. Its
verdict is authoritative except for exact leading name + argues/holds/believes
that report frames, which still hard-reject. Words such as "claims about" or
"account" alone no longer veto own-voice assertions. Missing
legacy catalogues remain unavailable; code does not invent their definitions.
All classification dispositions, cache replays and solver receipts are logged.

Proposal asks for 30 candidates per attempt and retains at most
`min(target_candidates, 10)`. An explicit named position uses a one-item pool and
preserves its exact text. A response may supply fewer candidates when it cannot
fill the pool; received/requested counts and `underfilled` are logged. At most
three proposal attempts run, with passing candidates retained across corrections
in first-seen order. Retained IDs and alpha-equivalent structural formulas are
not counted twice. Every candidate, including surplus passing candidates, gets a
`target_pool_candidate` disposition; `target_pool_finished` records the retained
set. Processing stops once the requested retained count is reached.

Targets may carry `new_symbols` entries with name, kind, arity and content
definition. They are preserved in the proposition codec and cache inputs; absent
entries retain the historical encoding. A single atomic assertion binds its
entire target text as its definition when no explicit definition was supplied.
Compound targets must supply every otherwise unbound fresh symbol. Frozen-name
overrides, duplicate or unused definitions and missing bindings refuse.
Unicode-NFKC/casefolded word equality and a character similarity ratio of at
least 0.90 (minimum 20 normalized characters) screen new definitions against T
content and verified catalogue definitions. This conservative lexical screen
can reject close wording; it is not an equivalence solver. The classifier
separately judges whether definitions merely rename or package existing content.
Unverified legacy catalogue definitions remain unavailable.

The proposer receives the actual versioned bank, premise slots, CQs and
placeholder support examples. A new main proposition must not be in T or follow
from one paper's endorsed commitments. In particular, if R is in T, `(P and Q) -> R` is already
entailed by R alone. Correction feedback includes each rejected target, reason,
checked polarity, the full entailing commitment when present, and an explanation
of this conditional trap. Feedback identifies the entailing paper when a multi-commitment paper closure supplies the witness.

A new thesis may introduce new vocabulary; disconnection is disclosed as an
advisory, not a gate or a reason to replace an otherwise passing candidate.
Native search still needs a bank-licensed route. Defeasible schemes can license a
new-atom thesis without classical entailment of that thesis: the placeholder
regression closes R from P and Q through `sign`, with every CQ answered using
frozen evidence IDs. Leaving CQs unanswered keeps the route open. This establishes
native mechanical reachability, not the truth of CQ answers or semantic fitness
of arbitrary material to a scheme. Neither model classification nor solver
checks prove originality or faithful text/formula translation.

The classifier schema is part of Codex preflight. Historical preflight receipts
must match the current schema manifest before live use; a changed
manifest or model/configuration can also invalidate proof. See
[provider preflight](providers.md#codex-cli).

## Route classification and selection

Contribution labels supplement the engine's unchanged `CLOSED`/`OPEN` status,
bank licenses and graph format. With verified provenance, novelty is checked
against each paper's endorsed commitments. No individual paper may entail the
root, and the root must not be a tautology. Entailment by the union is allowed.
For P from paper a and P -> Q from paper b, Q can be a cross-paper deductive
synthesis; both premises from paper a make Q single-paper. Paper identity is never
inferred from citation strings when provenance is missing.

An essential atomic assertion must lie outside every individual paper's closure
and affect target truth under the route's jointly satisfiable supports. Replacing
it in the target with true or false must change the target in at least one model
of that support set. Supports include endorsed commitments and disclosed alignment
premises; reported and attacked content remains excluded. Both substitutions and
the union's commitment IDs are logged, and solver uncertainty stays unresolved.
It can occur inside a frozen conditional already; it
need not have a fresh symbol name. Bare Boolean packages of separately established
facts and irrelevant wrappers around cross-paper packages still fail. Vacuous
quantifiers are removed for this check. A bounded Z3 query rejects targets
equivalent to Boolean combinations of basis formulas, comparing two independent
interpretations without assuming the basis assertions true. This same
check governs native, forward-mined and external-gap targets. Own-thesis, content
fidelity, definition-restatement, source stance and CQ checks remain required.

Before search, optional target `basis_commitment_ids`, or dependencies of an
exactly matching forward lead, seed a deterministic maximal consistent subset.
Runtime adds admissible commitments in ID order when consistency is preserved,
logging selected/omitted IDs and every solver outcome. This is not a maximum
or unique subset. Required IDs are never discarded; invalid, inconsistent or
unresolved required bases refuse. An internally inconsistent paper receives a
logged consistent projection preserving required supports. Frozen T stays intact.

A deductive synthesis needs distinct endorsed support formulas assignable to at
least two distinct papers and a reachable licensed inference. Native bank
rechecks of reachable inference bindings accompany its contribution receipt;
unknown rules or disconnected inferences cannot upgrade it. Deductive rules
count when combination supplies the contribution. Defeasible and mixed scheme/deduction routes retain native licensing and CQ
requirements. Logical detours do not repair a target already entailed by one paper. Solver uncertainty remains unresolved.

Target proposal also receives up to 30 ranked native forward candidates, with
exact source dependency IDs, paper IDs, bank IDs and depth. The fresh pass uses the configured forward depth/node bounds. Recorded forward
results from the current search generation and exact freeze are also mined,
with a separate scan bound equal to the node cap. Both disclose truncation and
never call a model. Proposal cache inputs include the recorded result payloads;
a newly started generation cannot reuse old findings.
The proposer renders these candidates as theses alongside gap targets; all
admission gates still apply. A candidate is not a searched route or a substantive
novelty claim. Legacy freezes without source metadata have no forward synthesis
census and retain conservative legacy novelty checks.

CQ evidence counts as support. Assumptions and repeated or alpha-equivalent
support formulas do not inflate the count. The check traverses reachable nodes;
it does not establish minimality of larger support subsets, independence across
papers or semantic novelty.

| Display label | Meaning for selection |
| --- | --- |
| `CLOSED-conflict` | Jointly inconsistent supports; excluded from selection and composition, disclosed in conflict/gap records |
| `CLOSED-derived` | Passes the contribution policy; offered by default |
| `CLOSED-structural` | Otherwise passes contribution checks but has no qualifying step concluding an essential new proposition; explicit `--route` required |
| `CLOSED-single-support` | Lacks the required inference/distinct supports, is valid without support, or follows from one support; explicit `--route` required |
| `CLOSED-contribution-unresolved` | Required support or a solver verdict is unavailable; explicit `--route` required |
| `CLOSED-stance-crossing` | A recorded reported/attacked support is used as a global premise or CQ evidence; explicit `--route` required |
| `CLOSED-attributed-report` | Reporting language is detected during the closed-route contribution check; explicit `--route` required |
| `OPEN` or another non-closed status | Retains its engine status and disclosed frontier; explicit `--route` required |

An explicit route argument cannot compose inconsistent or unresolved supports.
It chooses a displayed route but does not bypass budgets,
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


## New-atom leaf guidance and correction

Both leaf mapping and cut proposal receive bounded goal-novelty evidence,
non-logical scheme signatures (premise/conclusion slots and critical questions),
and the frozen catalogue. A new atom should map to open unless its formula
actually matches T. Cut proposal then supplies scheme instances whose own
conclusion is the new atom, with fitting premises from T. Mapping never invents
a scheme or asserts closure. A signature fit is not proof of semantic suitability.

Each leaf has a batch of at most three cut proposals and one correction when no
proposal is licensed. The engine supplies concrete rejection codes and rejected
instances, or NO_PROPOSALS for an empty batch. Accounted local validation failure
also consumes a batch and supplies its reason. The correction is not multiplied
by validation_attempts. A licensed alternative is retained without another batch;
normal premise/CQ expansion and node/depth bounds still apply. Unanswered CQs
keep the route OPEN. Operational/provider failures still propagate.


## Cross-paper contribution and bridges

A CLOSED-derived route needs at least two distinct paper IDs among its reachable,
formula-distinct frozen supports, including cited CQ evidence. Paper identity is
the exact source_id in verified commitment provenance; differing citation strings,
pages, authors or T IDs do not establish different papers. An otherwise derived
route with one paper is CLOSED-single-paper. Missing paper identity yields
CLOSED-contribution-unresolved. Both remain disclosed and require explicit
--route selection. Engine CLOSED and its licenses are unchanged. Stance, novelty
and single-support checks still apply. This counts recorded sources, not semantic
independence or necessity of every support.

Target, leaf and cut inputs include candidate_bridges and commitment_papers.
Bridges are pairs or triples of endorsed T commitments from at least two papers,
linked by a common catalogue symbol or exact case-folded definition term (common
function words removed). Symbol links take priority; IDs and connections are
sorted deterministically. At most 30 pairs and 30 triples are returned, with
10,000 examined combinations per size and explicit truncation. A triple needs a
connection shared by all three members. Missing catalogue/provenance produces
no invented candidates. These are lexical leads, not verified topic equivalence
or semantic scheme fit. Catalogue/CommitmentSet formats and hashes are unchanged.

For a new-atom leaf, cut guidance prefers two-paper premises. A proposal cites a
bridge by placing its exact T IDs in named premise slots. Runtime logs the matched
bridge IDs and each slot's verified paper as proposal_bridge; open or scoped
hypotheses do not supply paper support. The schema stays unchanged. Guidance does
not force irrelevant premises, license a step, or promise three successful routes.

## External gap hypotheses

Set `gap_file` in the run configuration to an external JSON file, or pass
`--gap-file /path/to/gaps.json` to `run` or `fork-from-freeze`. Its envelope
is `{"schema_version":"external-gaps-v1","gaps":[...]}`. Each record requires
`id`, `origin` (exactly `AI-found`), nonnegative integer `priority` (lower first),
`finding`, `paper_ids`, `commitment_ids`, `support_groups`, `evidence`,
`currency_verdict`, `search_scope`, and `claim_framing`. Evidence is a nonempty
array of `{source_id, location, finding}` objects. Paper IDs and commitment IDs
must bind to the current verified freeze; each support group must contain
endorsed commitments from its corresponding paper. Alignment bridges cannot
supply source support. Evidence may discuss external literature, but this does
not admit that literature as frozen premises.

External gaps precede native gaps. The complete input and its SHA-256 are logged
as `external_gaps_loaded`; its evidence and file hash accompany the target,
classifier, route and writer/auditor outline. A changed file generates a new
receipt and proposal cache identity. Invalid or missing configured files refuse
explicitly; `gap_file: null` retains native-only discovery. On resume the configured
file is read again, so retain it at the recorded path for reproducibility.

For placeholder data, a record can bind papers `a` and `b` to commitments `p` and
`q`, use support groups `[["p"],["q"]]`, and describe a proposed link from P to Q.
The currency verdict and claim framing are supplied research qualifications,
not proof of an open problem. Normal target novelty, stance, licensing and
both-side support gates remain authoritative.
