# Providers and isolation

[Documentation index](README.md) · [Project README](../README.md)

## Anthropic API

Set `ANTHROPIC_API_KEY` in the environment. If the operator keeps it in a shell
file, source that file in the same shell as the command:

```sh
set -a; . ~/.config/ara/anthropic.env; set +a
uv run ara run --smoke --run-dir runs/real-smoke
```

Default provider/model: Anthropic / `claude-opus-5`, using the official SDK,
adaptive thinking and structured output with strict local schema checks.
Extraction alone uses `stages.extraction.model: claude-sonnet-5-5`, with
`fallbacks: []`, high effort and adaptive thinking. Other stages remain on Opus 5.
The stage model, effort, thinking and fallbacks partition caches; receipts and
methodology disclose requested/served models and versions. Sonnet rates were
verified on the provider pricing page on 2026-10-21: USD2/M input, USD10/M output,
USD0.10/M cache reads, USD2.50/M five-minute writes and USD4/M one-hour writes.


`fallbacks: [claude-opus-4-8]` explicitly enables the June 2026 refusal-fallback
API: the primary remains Opus 5 and the server can re-run a refused call on Opus
4.8. `fallbacks: off` or `[]` disables both the fallback parameter and beta
header. The old scalar `default` configuration is rejected; update existing
runtime configs to the list form. A final refusal from the whole chain is logged
and never retried.

Logs retain the requested and actual serving models, switch
blocks and fallback usage iterations. Each iteration is priced at its model's
configured rates; unknown model/cache prices stop with explicit unknown-spend
accounting. Methodology lists actual serving models by call kind and discloses
fallback use. Server-side fallback attempts may add billable usage beyond the
primary-model admission reservation; post-call accounting checks the whole chain.

Every structured prompt also contains the full local response schema. Generated
formula ASTs are bounded to depth two by config; local AST/solver semantics
support deeper formulas, but larger generation grammars can exceed the API
compiler limit.

Smoke uses placeholder literature, two targets, depth one, eight
search nodes per polarity, a 300-word draft with a 150-word minimum, an
8,192-token output allowance and at most one web search per evidence call. Its
caps are **USD 5 and 1,000,000 tokens**, including conservative admission
reservations. These are limits, not expected usage.

The writer instruction targets
about 90% of the hard word maximum to leave counting margin, while retaining the
minimum. Validation counts all title/body whitespace tokens, including markers.
The writer permits one initial attempt plus three retries for local validation
failures, including contentless, under-length and over-limit drafts. Each retry
sends identical inputs without validation feedback; every attempt records its
number, rejection reason, tokens and cost, and must fit the configured caps. Other
smoke call kinds retain up to three attempts with validation feedback. Invalid
responses are never cached. This local-validation retry policy does not retry
final refusals, transport failures, output-token stops, negative essay audits or
bank-license failures. CLI transport retries and final search-job attempts have
separate policies below and in [search](search.md).

A complete adverse first audit may start the separate, bounded sentence-revision
workflow described in [search](search.md). Each revision is a new logged call with
the auditor's exact evidence and flags; it does not retry or weaken that verdict.

Web admission reserves the
configured 200,000-token context bound for each potential server iteration. Prices
and that bound are explicit configuration assumptions; actual provider usage is
recorded. A reservation is checked before each call and actual usage after it. An
oversized actual charge cannot be undone; STOP prevents subsequent calls.

Use a new empty `--run-dir` when repeating a command. Omitting it generates a run
id automatically. Reusing the cache avoids paid calls only when all keyed inputs
match. Use one paid writer per cache; divergent concurrent outputs fail
explicitly. Delete neither failed logs nor their accounting to disguise a retry.

## Stage dispatch

See [construction stage
configuration](construction.md#construction-spread-and-stage-configuration).

## Claude Code CLI

Set `provider: claude_code` and a full pinned `model` such as `claude-opus-5-5` in
a local configuration file. `stages.construction`, `stages.search`, and
`stages.writing` may override `model`, `effort`, and `system_prompt`; an exact
call-kind override takes precedence. Existing extraction configuration and API
receipts are retained. This provider refuses extraction and `search_evidence`: it
has no external retrieval tools, so it cannot replace web verification. Provider
switching applies only to the rich construction stages. A run with `claude_code`
as its main provider cannot complete the web-verification stage through a per-kind
API provider setting. Native symbolic search, construction, and writing calls with
response schemas use fresh `claude -p` sessions through the usual `ModelCalls`
boundary.

The machine must have Claude Code, an existing subscription login (or
`CLAUDE_CODE_OAUTH_TOKEN` in the environment), and both `git config user.name` and
`git config user.email`. The provider keeps a live reference to the credential
file path and opens it read-only before every subprocess, including retries.
Atomic host-side replacements become visible on the next call. It never caches
credential values in provider state or creates a token file/link for the child.
Only the current access token is passed in the per-call environment; refresh
tokens, MCP credentials and operator settings are excluded. An environment-only
login is read fresh from the process environment when no file source was selected.
A missing or malformed selected file fails explicitly, without falling back to an
old environment token. Same-user processes can already read the original
credential file and may inspect the child environment; this is not a promise about
`ps` visibility. Credentials are excluded from argv, logs and caches.

It creates a
separate empty cwd for every process, checks ancestor instruction files, and uses
safe mode, no user setting sources, no MCP, no slash commands, no session
persistence, no browser, and an empty built-in tool list. It does not refresh or
rotate the original login. An expired token requires operator login maintenance
outside ARA.

Every newly opened run context performs an uncached, budgeted isolation canary.
The visible-context report must show no skills, memory, CLAUDE.md or AGENTS.md.
Debug markers must prove skipped skill discovery, disabled installed plugins and
MCP, and disabled project memory. Both visible context and debug output are
scanned for runtime-discovered user skill names, project names and memory paths.
Supplement that inventory with `claude_code.forbidden_terms` in private local
configuration for project names absent from Claude's registry. Inventory values
and git identity are never added to prompts or committed. Every response,
including cached output, is scanned for the git name/email; a hit is rejected
without echoing its value. The isolated config suppressed the account reminder in
the verified CLI version. Debug output is scanned in the temporary directory and
discarded; its digest and check results remain in the event log.

Anthropic built-in plugins, SDK identity/runtime instructions, environment info,
and the `StructuredOutput` schema tool remain. The effective prompt is **not
byte-identical** to the API path; methodology records these differences. The CLI
receives the stage schema without its unsupported draft-2020-12 declaration; ARA
still validates the full original schema locally. A successful structured
completion may have CLI `stop_reason: tool_use`.

`claude_code.concurrency` defaults to 4 processes per provider instance;
`timeout_seconds` defaults to 300. Rate/usage errors receive at most two fresh
process retries, with logged exponential backoff capped at 30 seconds. The same
bounded retry path handles CLI turn exhaustion, structured-output retry
exhaustion, timeouts and identified transient server/connection failures. Schema,
invalid request failures are not retried. A `cli_auth_error` gets at most one
retry, logged as `auth_refresh_retry`, with a fresh read of the host credential
source. This event means re-read only: ARA never refreshes or rotates credentials.
The configured retry limit still applies and `retries: 0` disables this retry.


Native search still permits its one final job attempt after the initial queue
drains; that is separate from the per-call transport retry budget. An unclassified
exit 1 gets at most one retry per transport call, logged as
`unclassified_exit_retry`, within the configured retry budget; `retries: 0`
disables it. Other unclassified exit statuses are not retried. Admission is
repeated for every attempt, including retries with unknown usage charged at
reservation. Concurrent requests reserve tokens atomically.

Exit diagnostics retain only the exit status, an explicitly allowlisted CLI JSON
failure subtype, a fixed recognized-category label and numeric metadata. The
subtype allowlist is `error_during_execution`, `error_max_turns`,
`error_max_structured_output_retries` and `error_max_budget_usd`; other subtype
values are omitted. A fixed pattern table and numeric statuses classify errors in
memory as schema, auth, request, rate/usage limit, timeout, transient, max-turn,
structured-output or budget-limit categories, or `unknown`. No stderr line, stdout
diagnostic, arbitrary error category or other diagnostic text is retained.

 The
former first-line sanitizer was removed after ordinary quoted credentials and
short prompt echoes bypassed it. Existing credential and identity rejection still
prevents unsafe content from being accepted.

## Codex CLI

Select `provider: codex_cli` with a pinned model such as `gpt-6-luna` in a private
configuration. Set `codex_cli.auth_file` to a separate ChatGPT login file. ARA
requires an explicit path and never falls back to the worker's `CODEX_HOME`,
default login, or an API key. It opens the file fresh for each call, mounts it
read-only, and disables refresh. It does not copy, log or rotate credentials.

This transport requires Linux, `bwrap`, Codex CLI 0.163.0 and Git name/email
configuration for output screening. A different CLI version refuses pending
revalidation. Each call uses a fresh process, empty working directory and
temporary HOME/CODEX_HOME. The mount and PID namespaces hide host homes, `/tmp`,
`/run` and process state. User settings, project instructions, skills, memory,
MCP and local tools are disabled. Web search is enabled only for `search_evidence`. Minimal task instructions replace
coding-agent defaults; stage instructions and ARA's prompt remain. This prompt
differs from the API path.

The budgeted isolation canary checks visible context. Generic built-in tool
definitions may be visible; outside evidence retrieval any actual tool event rejects
the response. During `search_evidence`, only `web_search` events (search, open page,
find in page) are accepted. Unknown events and every non-web tool event reject. Only validated output and typed receipts are retained;
reasoning and free-text diagnostics are discarded. Output and cache replay are
screened for credentials and Git identity.

Construction, symbolic search, writing and evidence retrieval can use Codex.
Extraction still requires the API. `search_evidence` enables `web_search="live"`
inside the same isolated filesystem and records queries, completed web actions,
source URLs and quoted snippets. The no-tool isolation canary still runs before
operator content is sent. A response without a completed web event refuses.
The installed CLI's sibling `codex-code-mode-host` executable is also required
for this stage and mounted read-only under `/run`, without exposing its host
directory. A pending `other` web action may precede a recognized completed
search/open-page/find-in-page action; an unknown completed action still refuses.

The evidence wire is locally schema-validated. URLs must be HTTP(S), without
embedded credentials. Source URLs and snippets are model-reported from web search,
not raw search-result payloads; receipts and methodology disclose that boundary.
The existing verifier receives URL-bound excerpts, checks exact quotation wording,
removes unverified items and re-audits the cleaned essay before publication.
Web-search usage counts completed web events. The configured search allowance
bounds token admission, but the CLI has no hard per-call search/output limit.
Actual aggregate tokens are retained and can stop later calls. Web results are
untrusted evidence, never operator instructions.

Provider switching remains implemented for rich construction stages only; setting
`stages.search_evidence.provider` does not create an API transport. A Codex main
provider routes evidence retrieval through Codex web search by default, without an API fallback. Claude Code's retrieval
refusal and the API path are unchanged.

A requested model pin is not a serving receipt. When the CLI omits serving model
identity, ARA records `unverified`; it does not infer identity from the request.
An event reporting a different model rejects. Live serving identity remains
unverified by this documentation work. See `ara/runtime/codex_cli.py:197` and
`ara/runtime/codex_cli.py:230`.

Codex reports tokens, not a USD cost equivalent. Subscription USD is unavailable,
not measured zero. Its initial token estimate uses Anthropic calibration data and
is not a proven Codex tokenizer bound. Run-local observations can raise it. There
is no free counter or hard output-token CLI flag; output allowances reserve
capacity, and measured overages can stop later calls. See
[accounting](accounting.md).

Codex pilots require a live schema preflight with the same resolved profile and
stage settings as the pilot:

```sh
uv run ara codex-schema-preflight --config /path/to/codex.yaml --profile pilot --run-dir runs/codex-schemas
```

Set `codex_cli.schema_preflight_log` in that config to the absolute path of
`runs/codex-schemas/events.jsonl`, then use that config/profile for the pilot.
Run, construction resume and writing selection refuse absent or stale proof. Rerun
preflight after changing a schema, model, effort, system prompt, projection
version or pinned CLI version. It tests construction, corrections, targets,
own-thesis classification, search and writing with placeholders, keeping local
constraints authoritative; it does
not prove pilot success. API-only extraction and web retrieval are not Codex
schema cases. Use the separate ChatGPT auth file; never the worker login.

The current contract includes `outline_essay` and `revise_essay`: older proofs must
be refreshed to cover all 18 cases. This is schema-acceptance evidence, not proof of
originality or successful new targets.

For an existing run, pass `--codex-schema-preflight-log PATH` to
`resume-construction`, `resume-search` or `select` to supply new proof without
editing its history. `fork-from-freeze` accepts the same override for its new run.

## Local schema validation

Local validation retains the full native schemas. Formula alternatives use their
existing `op` discriminator, so each formula node is validated once. A structural
precheck rejects invalid arity, node kinds and symbol/term fields immediately.
Corrections use the same validation path as first responses and cache replays.

Configure `local_validation_max_depth` (default 64, JSON root depth 0),
`local_validation_max_nodes` (100000 JSON values), and
`local_validation_timeout_seconds` (2 seconds per schema/normalization operation).
A bound exceeded by a model response produces a logged, correction-eligible
rejection. It never becomes an accepted response. The time limit runs in a
killable child interpreter and works inside parallel search jobs. Larger valid
objects may need explicitly larger limits; the limits do not change native schema
meaning. Existing catalogue-reference checks and solver budgets still apply.
