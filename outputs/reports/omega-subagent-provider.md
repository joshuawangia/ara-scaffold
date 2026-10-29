# Omega provider: round 1 evidence and round 2 implementation

Current result: **Round 2 implemented and committed locally at `047274986b0099c8122d8250e0214089d4a5b781`.** Full pytest and all 326 controls passed; the final native isolation canary passed. No push. Read the numbered Round 2 findings for scope limits and the diagnostic-accounting gap.

Round 1 status (superseded by the revised contract below): **BLOCKED — isolation failed the brief's strict contract.** No native provider was implemented or enabled, and no real ARA stage call was made. The instruction in `/home/dev/ara-work/briefs/omega-subagent-provider.md` is explicit: “If isolation can't be proven, stop and report it. Do not run real calls.” This report follows that stop condition; the required DONE trailer is a receipt format, not a claim of feature completion.

## Workspace and scope

Created `/home/dev/ara-work/omega`, branch `feat/subagent-provider`, from the requested `main` revision `0e0a7fcf8a167fa6a0973f92e322582c33d6e6e4`. HEAD remains that revision and the working tree is clean. No implementation commit or push occurred. No workers were delegated, credentials rotated, or harness installations changed.

Read ARA's repository rules, PLAN, relevant provider/accounting decisions, the native `ModelCalls` request/admission/validation/event/cache path, both existing provider implementations, budget accounting, CLI construction, methodology export, and provider tests. The native seam is `make_calls` → provider `estimate`/`complete` → `ModelCalls`; implementing a separate runner would bypass required accounting and validation. Implementation was deliberately held behind the live isolation prerequisite.

## Canary invocation and receipt

CLI: **2.1.306 (Claude Code)**. One fresh `claude -p` process used an empty temporary directory under `/tmp`, with no resume or session reuse. Inherited `ANTHROPIC_*`, `CLAUDE_*`, and `CLAUDECODE*` variables were removed from its subprocess environment; `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` was then set. The existing login was used without copying credentials. Exact reproducible invocation is in `omega-evidence/canary.py`.

Flags:

```text
-p
--model claude-opus-5-5
--output-format json
--json-schema <object schema with six required string fields and no additional properties>
--safe-mode
--system-prompt <the exact canary system text below>
--exclude-dynamic-system-prompt-sections
--disable-slash-commands
--strict-mcp-config
--mcp-config {"mcpServers":{}}
--tools ""
--setting-sources ""
--settings {"disableAllHooks":true,"autoMemoryEnabled":false,"enabledPlugins":{}}
--no-session-persistence
--no-chrome
--debug-file /home/dev/ara-work/reports/omega-evidence/canary.debug
```

Supplied system text:

```text
ARA isolation canary OMEGA_20261023. Report only context visible in this session. Do not infer hidden context.
```

Stdin asked the model to report verbatim visible skills, tools, memory, CLAUDE.md, other context, and its system prompt; absent categories were to be empty strings. No operator project content was placed in the prompt.

| Receipt | Observed value |
| --- | --- |
| Requested model | claude-opus-5-5 |
| Served model, CLI `modelUsage` | claude-opus-5-5 |
| Exit status | 0 |
| CLI subtype / terminal reason | success / completed |
| Session id | fa2ad31d-1f3e-4a20-b206-b7edff536942 |
| Wall time | 9.493908477 seconds |
| CLI duration | 8581 ms |
| Input tokens | 2 |
| Cache creation input tokens | 1235 |
| Cache read input tokens | 0 |
| Output tokens | 997, including 123 thinking tokens |
| CLI cost equivalent | **subscription_usage: 0.029828 USD equivalent**, list-price basis; not measured API USD |
| Real ARA stage smoke | 0/3; not attempted after isolation failure |
| Median real stage-call latency | N/A |

## Finding 1 — Built-in plugins and hook modules still execute

The help explicitly says safe mode leaves built-in plugins active. Debug evidence confirms that `disableAllHooks` does not establish the requested absence of all plugin hook modules:

- `canary.debug:34`: “Safe mode: installed plugins are disabled, none of their hooks or hooks modules load; built-in plugins load regardless”.
- Lines 46–48: native hook modules loaded for `cc-plugin-agents-md`, `cc-plugin-telemetry`, and `cc-plugin-plugin-authoring`.
- Lines 51–53: all three registered and admitted.
- Line 113: `cc-plugin-agents-md@builtin session.start` executed.
- Line 137: `cc-plugin-agents-md@builtin prompt.context` executed.
- Lines 143–144: its `turn.start` and `prompt.submit` handlers executed.

This is a concrete failure of the literal “no ... plugins or hooks” requirement, not evidence that the operator's project content was leaked. No such content was observed. The absence of a reported leak cannot substitute for the stronger isolation rule.

## Finding 2 — Replacement does not produce an identical effective prompt

The canary repeated the supplied system text, but also reported an SDK identity prefix and additional tool-execution instructions. Its other-context field exposed an account email reminder (value intentionally omitted here), temporary working directory, OS/shell information, model identity, date, and additional runtime instructions.

The CLI help states that `--exclude-dynamic-system-prompt-sections` is ignored with `--system-prompt`; with the default prompt it moves sections into the first user message rather than excluding them from model context. Consequently, these flags do not prove the strict API-equivalent system/prompt contract. The current API provider sends the rendered user message and no explicit custom system field.

Account identity is not a credential, but it is operator-specific injected context. This report does not repeat that identity. Raw canary evidence is local, outside git, with mode 0600.

## Finding 3 — Schema output adds a tool despite the empty built-in tool list

The canary reported a `StructuredOutput` tool and returned `structured_output`. The CLI receipt has `stop_reason: tool_use`, two turns, and a successful terminal result. The returned object has exactly the six required fields, all strings, so this particular schema was satisfied.

This single success is not proof that the CLI always enforces schema constraints. No adversarial schema probe or real ARA schema call followed the failed isolation gate. A future implementation must retain local schema validation and distinguish the CLI's structured-output tool completion from an ordinary unexpected tool-use stop. Under a literal all-tools-disallowed rule, the schema mechanism itself also needs resolution.

## Finding 4 — Limited clean-context evidence does not prove complete isolation

The canary reported empty skills, memory, and CLAUDE.md fields. Neither of the two direct user skill directory names appeared in its visible-context output. This name scan does not cover every bundled/plugin skill or prove that absent context was never loaded.

Debug lines 25–26 show user skill discovery was skipped; line 40 reports zero skill-directory commands and zero plugin skills, alongside bundled/built-in skill inventories. Lines 130–131 state project memory is off. Line 108 states claude.ai MCP connectors are disabled in safe mode. These support suppression of user customizations, but do not overcome the observed built-in hook execution and injected context.

## Verification and remaining work

The canary completed successfully as a process, but **failed isolation acceptance**. The failure checks identified loaded built-in hook modules, executed prompt-context hooks, non-identical effective system context, and a nonempty tool inventory. This is why the trailer says `negctl=fail`; it does not claim completion of the requested fake-binary production-wire negative-control suite.

Repository pytest and the control runner were **not run** after the mandatory stop; `tests=0/0` means unexecuted, not green. No fake-binary tests, provider implementation, budget policy changes, concurrency/retry implementation, or methodology changes were made. There is no new feature commit to integrate. Existing extraction behavior is untouched. No evidence claims construction/search ran on this provider.

Recovery: retain this clean worktree and the evidence. Before implementation resumes, establish a supported subscription-authenticated invocation that satisfies the required plugin/hook/context isolation, or obtain an explicit revision to those constraints. Do not silently treat safe mode as proven isolation, switch to `--bare` API-key auth, or run real ARA calls with these tested flags. This is a limit of the tested invocation and documented controls, not a claim that every possible future CLI version or configuration is incapable of isolation.

## Evidence and handoff

All evidence is under `/home/dev/ara-work/reports/omega-evidence/`:

- `canary.py`: exact reproduction, system text, stdin, schema, environment filtering, and flags.
- `canary.stdout.json`: full original CLI result and structured canary response (contains account identity; local-only).
- `canary.debug`: original debug evidence; local-only.
- `canary.stderr`: captured stderr.
- `summary.json`: token/cost/timing receipt, failure checks, and SHA-256 hashes of the script, response, and debug log.

Four action-changing findings are placed in the four explicitly named Finding sections above. Verification gaps, unchanged HEAD, and the next unresolved step are placed in “Verification and remaining work.”

4 findings, 4 placed

Historical round 1 receipt: DONE omega head=0e0a7fcf8a167fa6a0973f92e322582c33d6e6e4 tests=0/0 negctl=fail isolation=failed live_smoke=0/3 median_call_s=n/a report=/home/dev/ara-work/reports/omega-subagent-provider.md


# Round 2

Current state: **implemented, verified, and committed locally** as `047274986b0099c8122d8250e0214089d4a5b781` (`feat(runtime): add isolated Claude Code subscription calls`). Branch `feat/subagent-provider` in `/home/dev/ara-work/omega` is based on `0e0a7fc`. The working tree is clean. Nothing was pushed.

## R2 finding 1 — Revised isolation contract is enforced at native startup

Round 2 explicitly permits Anthropic built-in plugins, SDK instructions, environment information and the StructuredOutput tool. The provider creates separate empty cwd and Claude config directories for every process and passes only the existing OAuth login token into a filtered child environment. It neither copies credentials nor rotates/refreshes the machine login. No operator identity is introduced by this change. Git name/email are read at runtime, and every response, including cached responses, is checked before output persistence.

A new ModelCalls context performs a live, uncached, budgeted canary before stage calls. Empty skills, memory, CLAUDE.md and AGENTS.md, allowed-only schema tooling, absent ancestor instruction files, debug markers, and a forbidden-content scan must all pass. The scan covers runtime-discovered skill names, configured project names, memory paths and any private `claude_code.forbidden_terms` supplement. Terms and identity are not inserted in the canary prompt or persisted in the receipts. The inventory is a bounded registry-based check; project names absent from machine registries must be supplied in private configuration.

The fresh config suppressed the account-email reminder on CLI 2.1.306. The earlier native canary passed 48 forbidden-term checks. The final implementation additionally inventories frontmatter skill names and the global memory path; its final live startup canary passed all 49 terms. Full accepted canary output and hashes/check results are in the native event log. Runtime debug is scanned in the temporary directory, hashed, and discarded. The earlier independent round-2 canary's full debug remains in `omega-evidence/canary-round2.debug`.

## R2 finding 2 — Schema and effective prompt differences are disclosed

The first native construction call failed before generation because CLI 2.1.306 rejects the draft-2020-12 metaschema declaration. The CLI argument now omits only `$schema`; all stage constraints and recursive definitions remain. ModelCalls continues validating the original complete schema locally. Successful StructuredOutput may finish with `stop_reason: tool_use`. Failed exits, missing structured output, model mismatch, malformed receipts and local schema violations do not enter the cache.

User prompt text and configured system text are sent unchanged. The effective CLI context still contains accepted Anthropic defaults and is not byte-identical to the API path. The methodology export records this, the CLI version, models by stage, isolation flags and the schema transport difference.

## R2 finding 3 — Subscription accounting is distinct from API USD

CLI cost equivalents are labelled `subscription_usage`, not measured API charges. Subscription calls have zero new `cost_usd`; USD caps do not apply to them. Imported historical extraction API charges remain visible. Token admission and context limits still apply.

The CLI has no free token counter. The local reservation uses one token per UTF-8 byte of prompt/system/schema plus 16,384 tokens of runtime headroom, twice for the two-turn ceiling, plus one output allowance for possible replay as second-turn input; output generation is reserved twice. This is a conservative local estimate, not a measured tokenizer result or a guarantee about arbitrary future CLI defaults. Receipts identify the estimation method. Missing usage consumes the reservation and remains incomplete. Cached receipts do not add new subscription usage.

## R2 finding 4 — Native integration preserves existing caches and concurrent admission

`--provider claude_code` reaches the existing CLI → ModelCalls → provider → validation/event/cache path. Stage model settings and exact kind overrides are supported. Default concurrency is four processes per provider instance, with a configurable timeout and at most two logged fresh-process rate/usage retries (configurable up to three). Each retry is admitted separately. The CLI remains an opaque process; receipts describe CLI aggregates, not every internal SDK request.

Concurrent token reservations are atomic. Per-call receipt IDs prevent one failed request from charging another in-flight request's reservation. A regression test proved that failure mode before the fix. Existing API/mock cache keys are preserved; only the new provider includes CLI metadata in its cache identity. Count-only construction planning uses the local CLI estimate and makes no preflight/generation call.

Integration touches `ara/runtime/{claude_code,providers,calls,budget,cli,planning,export}.py`, configuration/docs, a new fake-executable test module, and the existing integration control runner. Other parallel workers touching calls/budget/planning should integrate these shared-file edits explicitly; the provider branch contains no construction spread or search algorithm changes.

## R2 finding 5 — Explicit scope limits remain

Extraction remains on its existing API workflow. The tool-free CLI provider also refuses `search_evidence` rather than inventing retrieved evidence. It supports native symbolic search and schema-bearing construction/writing calls, but an eventual complete composition/export workflow that requires external web verification still needs a retrieval-capable path. No API fallback or credential change is hidden in this provider.

No full-corpus rebuild, full ARA workflow, real provider concurrency/load test, expired-login refresh, or production rate-limit event is claimed. Concurrency, retries, limits and failures were tested offline with a real fake-executable subprocess boundary. Canary proof is version/environment-specific and is rerun at native startup.

## R2 finding 6 — Live smoke and diagnostic accounting

Native smoke on placeholder content accepted the canary plus construction, target proposal and formalization, all requested and served by `claude-opus-5-5`. Each used a fresh recorded session and passed local validation. Receipts are in `/home/dev/ara-work/omega/runs/omega-live2/events.jsonl`, `summary.json`, and `methodology.md`.

| Stage | Wall seconds | Input | Cache read | Cache creation | Output | Subscription USD equivalent |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| isolation_canary | 8.712 | 2 | 789 | 330 | 875 | 0.0203058 |
| build_t | 3.329 | 2 | 0 | 4252 | 140 | 0.0368240 |
| propose_targets | 4.744 | 2 | 0 | 4262 | 310 | 0.0403040 |
| formalise | 2.163 | 2 | 0 | 3847 | 75 | 0.0322840 |

Native stage acceptance: **3/3**. Median stage call: **3.329 seconds**. Native successful-run subscription equivalent including its canary: **0.1297178**. These are not whole-task totals.

Earlier evidence is retained: the isolated-config standalone canary; the first native run with a passing canary and the pre-generation schema failure (`runs/omega-live`); and direct transport diagnosis of that schema error. One direct diagnostic was inadvertently repeated after the fix and completed outside ModelCalls; its result was discarded, so its token/cost receipt is unavailable. It is excluded from measured totals and is an explicit verification-accounting gap, not a claimed zero-cost call. All three accepted native smoke stage calls have complete receipts.

## R2 verification and next step

The first new test run failed because the provider did not yet exist (13 errors). The final focused provider/runtime batch passed 70 tests. Two earlier full-suite attempts were interrupted to fix issues found during review, without observed failures; they are not counted as full passes. A preliminary full suite passed 713 tests with two live API tests skipped. **Final verification ran sequentially on the exact committed source: `uv run pytest -q` passed 715 tests with 2 opt-in live API tests skipped (717 collected), then `uv run python tests/integration/negative_controls.py` passed all 326 mutation controls, each red when disabled and green after restoration.** Twelve controls were added for safe mode, schema transport, identity/forbidden scans, debug evidence, preflight freshness, diagnostic suppression, retries, concurrency admission, configured-system cache separation and serialized STOP artifacts. Three existing anchors were adjusted to follow changed code without changing their target behavior.

In-context review was performed by the implementing worker, without delegated or independent review, as the brief requires. Resolved review findings include schema compatibility, concurrent receipt attribution, output-replay admission, legacy cache compatibility, configured system-prompt cache partitioning and serialized STOP-artifact writes.

The first control run was intentionally interrupted for the final cache correction; its active source mutation was restored and every owned file matched the pre-control SHA-256 manifest. The final sequential verification chain completed successfully (tool session 18943). Its stdout files are `omega-evidence/pytest-round2.txt` and `controls-round2.txt`. `verification-final.json` records both exit statuses as zero and exact source restoration. Source hashes are in `source-before-controls.json`; they matched the committed worktree after verification and commit.

The final live startup canary ran after the full suite and controls on the same source that was committed. Its receipt is `runs/omega-final-preflight/summary.json`: CLI 2.1.306, requested/served `claude-opus-5-5`, exit 0, session `9d66e356-9d04-4f7b-87db-aa0af8fed375`, 8.870 seconds, input 2, cache-read 789, cache-creation 329, output 874; subscription equivalent 0.0202778. It passed 49 forbidden terms and all empty-context/debug checks. The three stage-call smoke receipts precede the final accounting/cache refinements; their transport flags and schemas are unchanged, and those refinements have final offline coverage. No additional real stage execution is implied by the final preflight.

A final whole-file git-identity audit flagged one occurrence in historical DECISIONS.md. Artifact comparison showed the same single occurrence at base and HEAD, with no identity introduced in any added commit line. That pre-existing document text was preserved. The audit emitted no identity value.

Remaining handoff actions belong to integration: combine the shared runtime-file changes with parallel worker branches, configure private forbidden project terms absent from machine registries, and choose a retrieval-capable path before attempting a workflow requiring web evidence. These limits are placed in R2 findings 1, 4 and 5. The single unrecorded direct diagnostic is placed in R2 finding 6. No required local implementation or verification step remains.

10 findings, 10 placed — four historical findings in the numbered Round 1 sections and six current findings in the numbered Round 2 sections. Final verification and the unchanged historical identity occurrence are recorded here.

DONE omega head=047274986b0099c8122d8250e0214089d4a5b781 tests=715/717 negctl=pass isolation=proven live_smoke=3/3 median_call_s=3.329 report=/home/dev/ara-work/reports/omega-subagent-provider.md


# Round 3

Status: **F6, F7 and F8 fixed and verified** on `feat/subagent-provider` from
`047274986b0099c8122d8250e0214089d4a5b781`. Committed locally as `1d54a534b6f099a21620509cfc69437993d2ea7c`; working tree clean. Nothing was pushed.
Native inline execution, no delegation and no push. The caller owns cross-branch
integration. This is ARA's Python checkout, not the enrollment_hub pnpm project.

## R3 finding 1 — F6 decoded credential rejection precedes retention

Raw stdout/stderr/debug scanning remains in place. A recursive scan checks every
decoded JSON string value and key, including nested JSON text, before CLI-provided
model/session/content fields enter any persistable response. The same guard runs
on cache replay; contaminated entries are rejected and evicted without echoing
their content. Active access/refresh credentials and any environment login token
are checked. Rejection preserves only validated numeric accounting plus locally
generated routing/session data; incomplete accounting remains labelled unknown.

The fake executable reproduces psi's Unicode-escaped credential attack through
native formalization. Tests assert rejection, no retained token in logs/cache,
and measured usage preservation. Additional cases cover keys, routing fields,
nested JSON result text, JSON-special credential characters and cache replay.
The initial regression run recorded 12 failed / 4 passed (the cache and encoded
credential tests plus construction failures) before implementation; see
`omega-evidence/round3-red.txt`. This is synthetic-credential evidence, not a
claim that a real machine credential leaked.

## R3 finding 2 — F7 native construction uses transport retries

Both direct construction attempts now call the shared transport retry boundary.
The ordinary ModelCalls validation path already used it. Tests drive native
construction_call for select_t_roots and build_t_batch, with correction settings
None, 0 and 1, and both rate and usage limits. Two configured retries produce
three fresh stage processes and two retry events. Targeted correction tests
prove one validation correction followed by three transport attempts still uses
only one correction. Exhaustion raises normal Rejected, not ClaudeCodeError.
The attempt numbers remain 1, 2, 2, 2 and correction budgets remain separate.

## R3 finding 3 — F8 uses a temporary config copy; profile discovery is suppressed

Auth is `config-link` in the requested receipt vocabulary, implemented as a
private 0600 copy, not a filesystem link. Each temporary configuration contains
only required OAuth authentication fields, excludes refresh/MCP credentials and
operator settings, and is removed on success, error or timeout. It cannot write
through to the original credential file. On this path the child has no OAuth
token environment variable. Fake-process tests inspect same-user ps eww output
in memory, emit no credential values, and verify cleanup and unchanged original
credential bytes. The initial non-generation auth-status probe also succeeded
with no token in the environment (`round3-auth-probe.json`).

The first live file-auth canary authenticated but returned operator identity.
The guard rejected it before any real stage; its response text was discarded
and sanitized measured usage retained in `runs/omega-round3`. Investigation of
CLI 2.1.306 showed that advertised profile scope permits account discovery and
identity injection. The temporary copy now advertises only the original
user:inference scope, matching environment-token mode. This limits CLI discovery;
it does not reduce the token's actual server-side permissions. Original scopes
and credential bytes remain unchanged. Three auth-cleanup tests failed before
this metadata correction (`round3-scope-red.txt`) and passed afterward.

The successful rerun proves the tested file-auth invocation suppresses operator
identity and passes the revised isolation contract. Env-only installations retain
an explicit, logged env mode when no credential file exists. Same-user processes
already can read the original credential file and can inspect an environment
handoff. Private file permissions protect against other unprivileged users;
root is outside this boundary. No blanket “never in ps” claim is made. Expired
login maintenance stays outside ARA; child credential refresh is disabled.
DECISIONS.md, README.md and log-derived methodology disclose this policy.

## R3 finding 4 — Executed evidence and remaining scope

Final focused provider tests: **60 passed** in 17.78 seconds. The earlier
resumed-work evidence records 50 provider tests and 121 affected runtime tests;
those are intermediate results, not the final full gate.

Live receipts (CLI 2.1.306; requested model claude-opus-5-5 throughout):

| Call | Result | Wall seconds | Input | Cache read | Cache creation | Output | Subscription USD equivalent |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| First file-auth canary | Rejected: operator identity | 11.897 | 2 | 607 | 688 | 1284 | 0.0313134 |
| Final canary | Accepted | 9.844 | 2 | 789 | 332 | 1127 | 0.0253618 |
| Final formalise | Accepted | 3.263 | 2 | 0 | 3849 | 75 | 0.0323000 |

All three calls recorded **0 API USD**. Round 3's total measured subscription
equivalent is **0.0889752**, including the rejected canary; it is not a paid API
charge. The successful canary and one real stage both served the pinned model,
used separate recorded sessions, and passed local validation. The canary passed
49 forbidden terms, empty skills/memory/CLAUDE.md/AGENTS.md, debug markers and
identity suppression. Evidence: `runs/omega-round3-final/{events.jsonl,summary.json,methodology.md}`
and `omega-evidence/live-round3-final.txt`. No unrecorded generation calls were
made in this round. The auth-status probe did not generate model output.

A post-live audit checked all 11 retained round-3 artifacts and the added source
diff against current credentials and git identity: pass, with no values emitted
(`omega-evidence/round3-artifact-audit.json`).

Six production-wire controls are added: decoded credential scanning, cache replay
scanning, both construction retry sites, inference-only scope metadata, and absence
of token environment handoff. Full pytest completed under `ARA_LIVE_TEST=0 UV_OFFLINE=1`: **741 passed,
2 skipped / 743 collected**, exit 0 in 399.94 seconds. The skips are opt-in
live API tests. All tracked files matched their pre-test hashes. The sequential
control runner then passed **332/332 controls**, exit 0: every mutation red
(exit 1), every restored test green (exit 0). Every tracked file matched its
pre-check SHA-256 hash after the controls. The six new red transcripts were
inspected: they fail on missing credential rejection, escaped transport errors,
or unsafe auth configuration, not invalid mutation syntax. Evidence is in
`omega-evidence/{pytest-round3.txt,controls-round3.txt,verification-round3.json}`
and `runs/delta-controls/{results.json,*-red.txt,*-green.txt}`. A final README-only
clarification distinguishes API credential rules from the authorized temporary
OAuth copy; implementation and tests are unchanged after these gates. The verification driver
is `omega-evidence/verify-round3.py` and hashes every tracked file before/after.

This fixes the provider branch only. Cross-branch integration, full-corpus
execution, live rate-limit/load behavior and expired-login refresh are unproven.
The prior tool-free retrieval limitation and version/environment-specific nature
of canary evidence remain. No independent reviewer was delegated; the implementing
worker inspected the native callers and diff as required by the no-delegation brief.

Finding placement: F6 is in R3 finding 1; F7 in R3 finding 2; F8 including the
rejected canary and actual threat model in R3 finding 3; verification/accounting
and integration limits in R3 finding 4. The ten historical findings remain in
their original Round 1 and Round 2 sections.

14 findings, 14 placed.

Final evidence record: `omega-evidence/round3-final-verification.json`.
The committed implementation and tests match the verified source byte-for-byte.
All three findings are fixed; no required local step remains. The caller's next
step is integration and independent review of this local head.

DONE omega round3 head=1d54a534b6f099a21620509cfc69437993d2ea7c tests=741/743 negctl=pass fixed=F6,F7,F8 auth=config-link


# Round 4

Status: F11/F12 implemented on `fix/subagent-final` in `/home/dev/ara-work/omega`,
from integrated head `76fa0b5fb7b9b9ff173239d5610073afed87bae4`, fetched from Xi.
Both sequential gates passed on the final source. No paid calls, delegation or push.
**The corrected real-source pilot plan remains unusable under the unchanged
limits: 177 windows, initial share 0, cap 0, projected contribution 0/177.**
This capacity result must not be presented as pilot readiness.

## R4 finding 1 — F11 counting contract and consumer audit

The immutable RequestCount separates `initial_input_tokens`, the provider's
`context_output_tokens`, and the aggregate TokenUsage `reservation`. Count events
retain both context quantities and `reserved_usage`. CLI estimates still reserve
two turns, output replay and runtime headroom; API search still reserves future
server-tool iterations. Neither estimator nor spending limits were weakened.

Every production count_request consumer was audited:

| Consumer | Quantity used after the fix |
| --- | --- |
| Construction partition selection/formalization counts | Initial input size |
| Working wrapper, copied commitments, current/cumulative/final T envelope | Initial input size |
| Closure fit, preflight and actual-output acceptance | Initial input size; downstream context adds provider output allowance |
| Catalogue empty/current/projected/final differences and borrowing | Differences of initial input sizes |
| ModelCalls dispatch, paper allowance, token/dollar admission, unknown-usage accounting | Aggregate reservation |
| Extraction range partitioning | Initial input size; returned TokenUsage remains the API reservation for planning/accounting |
| Reconciliation context check | Admission side effect only; no usage result consumed |
| Extraction planner and extraction execution's range iterator | Existing range contract retained; no generation in planning |
| Test budget helpers and three concurrency stubs | Explicit aggregate reservation / RequestCount |

Batch.input_tokens remains the persisted initial count. No ambiguous TokenUsage
compatibility property was added to RequestCount. Native placeholder planning
uses the real 64,000 output, 70,000 batch, 100,000 working, 48,000 catalogue,
233 growth and 200,000 context limits, with multiplier 2. It fits a combined
window with a positive cap and launches no process. Separate contract tests
check CLI aggregate preservation and API search iteration reservations.

## R4 finding 2 — F12 correction settings match native transport and manifest

Construction dispatch now resolves generic construction, exact-kind and correction
overrides in that order and passes a configuration with no nested stages to the
scoped provider. The original stage therefore cannot overwrite the correction
model, effort, system text, thinking or fallbacks. The manifest uses that same
resolution. The parent configuration and independent provider instances remain
on the native factory/canary/retry/shared-budget path.

The native CLI regression selects 4-8 initially and 5-5 for all three correction
transport attempts. Actual fake-executable argv and native requested/served-model
receipts are compared with the manifest; effort and system text are checked too.
The API regression uses the real AnthropicProvider with a fake SDK client,
checks count/create request models and receipts, inherited thinking, effort,
system replacement and correction fallback removal. No live API calls occur.
The existing mixed-provider and native full-construction routing tests remain.

## R4 finding 3 — Real-source result and remaining capacity blocker

Used the authoritative extraction artifact at
`/home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt`, SHA-256
`1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`, the
`overnight6-control/config.yaml` pilot basis, an explicitly empty audience,
multiplier 2 and fresh output directories. All stage models/providers were
claude-opus-5-5 / claude_code. The fake CLI, synthetic home/credentials,
subprocess allowlist and network-denying audit hook prevent real provider use.

| Plan | Windows | Initial share | Fixed cap | Projected contributing | Projected commitments |
| --- | ---: | ---: | ---: | ---: | ---: |
| Psi's integrated-head reproduction before F11 | 5,296 | 0 | 0 | 0/5,296 | 0 |
| Corrected CLI conservative byte estimate | 177 | 0 | 0 | 0/177 | 0 |
| Historical API-count replay (Sigma round 6) | 48 | 3 | 6 | 48/48 potentially | 144 |

The corrected initial input range is **40,162–67,061**, with **zero oversized
windows** against the unchanged 70,000 bound. The wrapper is 23,465 and the
working allowance after 20% headroom is 56,535. Copy cost is 491 per commitment,
plus the unchanged 233 growth reservation: total capacity floor(56535/724)=78,
below 177 windows. Equal initial allocation therefore gives zero, and multiplying
that by two still gives zero. The contribution projection follows the native
zero-cap skip before generation; no relevance or formalization was simulated.

The historical API comparison is supplied evidence, not a newly executed token
counter or paid call. Its 48/48 means candidate feasibility under historical
counts; new metadata was not freshly tokenized and actual contributions were
never guaranteed. Its limitations remain in the copied comparison within
`omega-evidence/round4/distribution.json`.

Both count-only plan-construction and a fresh native run reach identical plan ID
`e6b19a80479c0592074c24015b150e34b9a9478e5009212302159febea0389ef`.
The fresh run is deliberately intercepted after build_t_budget_plan, before
construction generation. It starts one fake canary, imports normal extraction
provenance, restores zero construction batches and imports no construction-resume
state. Count-only planning starts no process. No frozen T, search, real usage or
complete workflow is claimed. Existing imported extraction charges are historical,
not new API spending. The source artifact's hash is unchanged.

The offline scripts batch non-billable context events with the native emit_many
method to avoid repeatedly validating an increasingly large log. Unlike the
prior diagnostic, every full count event and prompt remains in the verified
native chain. The estimator, partitioner, allocation and generated plan are
unmodified; batching affects append timing only. Evidence and exact reproduction
scripts are under `omega-evidence/round4/`: `offline_plan.py`,
`offline_fresh_run.py`, both output directories, `offline-verification.json` and
`distribution.json`.

**Next pilot decision:** a separate justified estimation, partition/allocation or
capacity policy is required before a useful real rebuild. No bound was relaxed,
cap forced, zero-contribution plan described as useful, or paid probe attempted.

## R4 finding 4 — Verification and handoff scope

Intermediate focused checks passed 71 tests with one fixture-grounding setup
failure; after supplying native grounding, the construction/provider/closure/
recovery batch passed **50 tests**. The final focused count/routing batch passed
**8 tests**. The first full-suite attempt exposed an old TokenUsage-returning
concurrency stub and was stopped before controls; it is not a full pass. Three
count_request stubs were migrated to RequestCount with unchanged reservation
amounts, and the targeted concurrency batch passed **15 tests, 1 long equivalence
test deselected**. The long test remains in the restarted full suite. Initial red evidence includes the missing explicit count contract
and CLI correction routing; the API red also exposed category/manifest thinking
precedence. The initial planning fixture was invalid before it reached counting,
so it is not claimed as red proof of the partition defect. Production-wire
mutation controls supply direct red/restored proof for the corrected test.

Four controls were added for initial-context partitioning, aggregate preservation,
and CLI/API correction resolution. Existing construction/extraction control
anchors were updated for the explicit field names without removing their
behavior checks. All **370 anchors** occur exactly once. The final full pytest run passed **794 tests, 2 skipped / 796 collected**,
exit 0 in **464.51 seconds**, under `ARA_LIVE_TEST=0 UV_OFFLINE=1`. The skipped
tests are opt-in live-provider checks. All tracked source hashes matched after
pytest. Only then did the control runner execute: **370/370 mutations exited 1 and
all 370 restorations exited 0**. Every tracked file, including all mutation
targets, matches its pre-gate SHA-256 hash. The four new red transcripts were
inspected: they fail on aggregate-driven partitioning, lost aggregate reservation,
and incorrect CLI/API stage settings; none is a syntax or call-signature failure.
`omega-evidence/round4/{pytest-round4.txt,controls-round4.txt,verification-round4.json,
source-before-controls-round4.json,new-control-review.json}` retains the evidence;
individual red/green transcripts and results remain in `runs/delta-controls/`. No separate lint/typecheck gate is configured.

The worker inspected native caller bodies and the diff in context; no independent
reviewer was delegated. Integrated source ordering, reservation ledger and
verification-cache changes are retained. Integration/review and a usable-pilot
capacity decision belong to the caller; successful source gates alone do not
establish a useful pilot plan.

Finding placement: F11 and the complete consumer audit are in R4 finding 1;
F12 and transport evidence are in R4 finding 2; the zero-cap outcome, historical
comparison, instrumentation and pilot decision are in R4 finding 3; verification
and integration scope are in R4 finding 4. Fourteen historical findings remain
in their original sections.

18 findings, 18 placed.

Final local commit: `46eab6593a260eef6a64e8b1ce003f078cec6d2e` on `fix/subagent-final`, directly atop
`76fa0b5fb7b9b9ff173239d5610073afed87bae4`. Working tree clean; every committed file matches the final
verified source. No push. Final receipt: `omega-evidence/round4/final-verification.json`.

F11/F12 repairs and the requested offline verification are complete. The next
unresolved step is the caller's capacity-policy decision: the measured plan
still cannot produce a useful T under the unchanged limits (R4 finding 3).

DONE omega round4 head=46eab6593a260eef6a64e8b1ce003f078cec6d2e base=76fa0b5 tests=794/796 negctl=pass fixed=F11,F12 windows=177 window_cap=0 contributing=0/177


# Round 5

Status: complete and locally committed as `852b21796191111c916be944648e3a42cac359ec` on
`fix/subagent-final`, directly atop `46eab6593a260eef6a64e8b1ce003f078cec6d2e`.
Both sequential gates passed, the worktree is clean, and committed source matches
the verified snapshot byte-for-byte. Same-task work resumed from the existing
round-5 implementation. No delegation, paid calls or push.

## R5 finding 1 — Versioned measured calibration

`ara/runtime/claude_code_calibration.json` is version `claude-code-input-v1`.
It contains numeric count/byte pairs and source, anchor, event, prompt and schema
hashes, with no source text. API source logs are `overnight5-pilot`,
`overnight5-plan-part3` and `overnight6-pilot`; CLI sources are `omega-live2`,
`omega-final-preflight`, `omega-round3` and `omega-round3-final`. Exact absolute
paths and SHA-256 values are in the table and
`omega-evidence/round5/calibration-verification.json`. The rebuild independently
verified native log chains and anchors and reproduced the table exactly.

| Kind | Deduplicated API pairs | Nearest-rank p99 | Factor (p99 × 1.05, rounded upward) |
| --- | ---: | ---: | ---: |
| build_t_batch | 381 | 0.5268793948670172 | 0.553224 |
| select_t_roots | 453 | 0.5253168432008817 | 0.551583 |
| propose_targets | 94 | 0.4637438800797856 | 0.486932 |

Unknown kinds use 0.553224. The byte basis is UTF-8 of prompt + separate system
text + canonical full response schema. Eight retained CLI receipts supply 949
runtime-overhead tokens: the maximum positive aggregate-input residual over the
calibrated text estimate, multiplied by 1.05 and rounded upward. The table file
SHA-256 is `73fbae14a14907710300e25d3db6b3fd2baa79ac8b031edb9a1f68c1022ec76e`.
`tools/calibrate_claude_code.py` reproduces it offline; setuptools includes the
JSON in the wheel, confirmed by the recorded successful wheel build.

This is an empirical estimate, not a hard tokenizer bound. The real-source
pairs measure API counts; the small CLI overhead sample is not a live CLI count
of the real corpus. Unknown kinds and distribution changes can exceed the
forecast. The factors are intentionally conservative rather than fitted to
reproduce the historical API plan exactly.

## R5 finding 2 — Admission, accounting and upward correction

Planning and admission share the calibrated initial input estimate. The
reservation remains two initial contexts plus one output replay, with two
output allowances. Actual CLI usage remains authoritative for settlement.

Every uncached response with measured usage, including rejected responses,
records `provider_estimate_observation` with estimate, actual aggregate input
including cache, underestimation flag, factor before/after and table identity.
Because CLI receipts do not attribute input by turn, aggregate input is compared
conservatively with the initial estimate. An overshoot raises the model/kind
factor with 5% margin under a lock; subsequent smaller observations never lower
it. Scoped providers share run state, and reopening the same run restores
observations for the matching table. Cache replays do not train the estimator
or alter cache identity. In-flight admissions retain their original reservations;
actual settlement and normal budget stops still apply. Failures without measured
usage remain incomplete and do not fabricate calibration observations.

Native fake-CLI tests cover overshoot, later counts, cache replay, reopen,
concurrent smaller observations and correction providers. They are offline
behavior proof, not a new live-provider test. Methodology exports include the
table identity and observation receipts.

## R5 finding 3 — Scarce slots reach windows in plan order

When positive global capacity is below the window count and one item can fit
the input envelope, one initial slot goes to each earliest window until capacity
is exhausted. Plans disclose per-window initial shares and caps, global slots,
funded-window count and the allocation rule. Unfunded windows are skipped;
remaining soft shares divide among funded windows. Fixed per-window caps and
all existing actual closure, mandatory-bundle, catalogue and global recounts
remain enforced. No allocation guarantees relevance or successful formalization,
and existing borrowing can consume capacity before later windows.

Native placeholder construction verifies two funded windows dispatch and freeze
two commitments while a third window is skipped. A truly zero-capacity plan
still refuses an empty working T. Separate arithmetic coverage verifies three
slots across five windows allocate `[1, 1, 1, 0, 0]`.

## R5 finding 4 — Offline real-literature plan

The completed count-only plan uses the same real extraction artifact, SHA-256
`1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`,
empty audience, multiplier 2, pilot limits and fresh output directory as round 4.
The result is 70 windows, initial share 2, cap 4, 160 global slots and 140
projected commitments. All 70 windows are funded and potentially contributing.
The working wrapper is 4,397, copy cost 239, symbol-growth reservation 233 and
working availability 75,603 after headroom and wrapper.

| Plan | Windows | Initial share | Cap | Potentially contributing |
| --- | ---: | ---: | ---: | ---: |
| Round 4 byte estimate | 177 | 0 | 0 | 0/177 |
| Round 5 calibrated estimate | 70 | 2 | 4 | 70/70 |
| Historical API count plan | 48 | 3 | 6 | 48/48 |

The API comparison is historical evidence, not a newly executed API counter.
The calibrated plan has 22 more windows and a cap two lower than that comparison;
it removes the zero-allocation blocker without relaxing bounds. Actual model
contributions are unproven. Count-only planning spawned no process or generation.
The fresh native run reached its budget-plan event and was deliberately stopped
before construction generation. Its plan matches the count-only plan exactly: ID
`17c3e1a07f9dc3130bd467e5ee10332928bc8bb7f2b8d779ac22f2a0f6833f66`.
Initial window input estimates range from 32,309 to 68,523, with zero windows
over the 70,000 limit. The native run starts one fake isolation canary, restores
zero construction batches and imports no construction-resume state. Both native
log chains and anchors verify. `omega-evidence/round5/offline-verification.json`
records the comparison and file hashes. Scripts deny network
connections and permit only the fake Claude executable and Git. Non-billable
count events are batched with native `emit_many`, preserving full events in the
chain without changing the estimator, partitioner or allocation.

## R5 finding 5 — Verification and handoff

Recorded proof-first run: four failures before implementation, comprising two
missing-module failures, failure to raise a later estimate after measured usage,
and missing scarce-allocation metadata. This is not claimed as four independent
production-wire behavioral failures. The final focused run passed 49 tests in
46.38 seconds. Exact calibration regeneration passed. Full pytest passed **799 tests, 2 skipped / 801 collected** in **437.94 seconds**,
exit 0, with `ARA_LIVE_TEST=0 UV_OFFLINE=1`. The two skipped checks require
live providers. Every source hash matched the pre-gate snapshot afterward.
Only then did the full control runner execute: **375/375 mutations exited 1,
and all 375 restorations exited 0**. Every tracked and new source file matched
the pre-gate SHA-256 snapshot after restoration. The five new red transcripts
were inspected: they fail on the uncalibrated count, missing upward correction,
unshared correction-provider state, missing restore, and zero-allocation empty T.
None fails because of syntax or a broken call signature. The final source also
passes `git diff --check`; there is no separate configured lint/typecheck gate.

Evidence is under `omega-evidence/round5/`: `pytest-round5.txt`,
`controls-round5.txt`, `control-results.json`, `verification-round5.json`,
`source-before-gates.json` and the copied five new red/green transcripts. Full
individual control transcripts also remain in `runs/delta-controls/`.

Final local revision: `852b21796191111c916be944648e3a42cac359ec`. No required implementation or
local verification step remains. Native caller paths and the diff were inspected
by the implementing worker; no independent reviewer was delegated under the
brief's no-delegation instruction. Integration and independent review belong to
the caller. A paid rebuild or actual all-window contribution is not claimed.
The final receipt is `omega-evidence/round5/final-verification.json`.
The single `calib_factor` in the completion line denotes the maximum/fallback
factor 0.553224; the three per-kind factors and additive overhead are in R5
finding 1.

Finding placement: calibration/provenance and statistical limits are in R5
finding 1; correction/accounting and concurrency limits in R5 finding 2;
allocation behavior and contribution limits in R5 finding 3; offline comparison
and instrumentation in R5 finding 4; verification status and recovery in R5
finding 5. The eighteen historical findings remain in their original sections.

23 findings, 23 placed.

DONE omega round5 head=852b21796191111c916be944648e3a42cac359ec tests=799/801 negctl=pass windows=70 window_cap=4 contributing=70/70 calib_factor=0.553224


# Round 6

Status: implemented, verified and locally committed as `e623021b4e79a5060137effaec3e81d5f2cbb416`
on `fix/subagent-final`, directly atop `852b21796191111c916be944648e3a42cac359ec`.
Both sequential gates passed; the worktree is clean and all committed source
bytes match the verified snapshot.
No push or delegation. Only isolated subscription checks were live; no API
calls or API charges. **The historical two exit-1 causes cannot be recovered
from the retained receipts: the old provider discarded their subtype and stderr.**
This remains an evidence limitation, not a diagnosed crash or schema failure.

## R6 finding 1 — Correct comparison units and separate fixed overhead

Round 5's comparison was wrong: the first pilot formalization's 30,294 aggregate
input was compared with 12,922 initial context, raising the factor from 0.553224
to 1.4237247019683947. The aggregate reservation was 89,844; that receipt did not
underestimate aggregate input. Prior tests asserted the inflation and therefore
missed the product failure. This section supersedes R5 finding 2's comparison rule.

`like-for-like-v2` observations compare a reported one-turn call's input with its
initial estimate. JSON receipts reporting multiple turns, or no turn count, use
aggregate input versus aggregate reservation. Aggregate factor correction removes
the reserved output replay and fixed overhead for both turns before computing
the text factor. Fixed overhead remains a separate measured 949-token constant
from the versioned table's CLI receipts. A one-turn canary can raise that constant
without raising the text factor. Multi-turn canaries do not identify per-turn
fixed overhead; they retain the measured constant. No first-turn usage is invented.
Factors and overhead remain upward-only and shared between scoped providers.

The byte/token table is unchanged. Restoration accepts only matching-table,
matching-observation-version local receipts. Old aggregate/initial corrections
and imported observations are excluded; same-run current observations restore.
Cache replay does not train. Actual accounting and aggregate two-turn reservations
remain authoritative. This still is an empirical estimate, not a hard tokenizer
bound. A small live sample cannot prove full-corpus context accuracy.

## R6 finding 2 — Pilot counterfactual and corrected skip count

Verified the native chain and anchor for
`/home/dev/ara-scaffold/runs/subagent-pilot/events.jsonl`, SHA-256
`678b4974d74f6380482f4f0797d84948fb81a56eab7c08dfecf59dc18bd73cab`.
The anchor SHA-256 is
`262cefdf7ba5012d3096150d8f1db54f399929d8fa58bd88eaaa8a90f27400f1`.
No source log was changed. The offline derivation replays local observations in
order using production CalibrationState and excludes imported history.

All 12 formalization receipts fit the recomputed aggregate reservations;
**the corrected factor remains 0.553224**. All **70/70 planned windows fit** their
original input bound. All **54/54 windows with recorded post-plan formalization
requests** fit after recounting those exact prompts with the corrected factor,
including the 42 previously rejected for context. Initial partition probes were
excluded from this latter check: oversized trial batches are not dispatched
windows. The other 16 windows were skipped for selection/closure reasons.
Thus the pilot had 42 context skips and 16 other skips, not 58 context skips.

The pilot's canary aggregate inputs were 1,120 and 1,122. Historical receipts
lack first-turn input and turn counts, so they do not identify a new independent
text ratio or overhead; they do establish no aggregate overshoot requiring the
incorrect factor increase. The rederived factor is the measured baseline retained
under the corrected rule, not an asserted measured first-turn ratio.

Evidence: `omega-evidence/round6/rederive-pilot.py`, `pilot-rederivation.json`,
`pilot-rederived-observations.json`, `pilot-rederived-windows.json` and transcript.
These are offline counterfactual estimates. They do not rerun selection, closure,
formalization, freeze, search or the failed pilot, and do not promise 70 actual
contributions. The historical 34-commitment result remains unchanged.

## R6 finding 3 — Exit-1 diagnostics and bounded retries

The two failed propose_cuts sessions were
`97418a74-4ab7-471b-8ad8-c734aeb7c181` (12.662 seconds) and
`1bd48340-d633-49a3-86b6-13f870e700f9` (15.862 seconds).
Both report exit 1 and measured usage, but their retained error text is only
`CLI diagnostic suppressed.` The old provider normalized their raw response to
an empty content array and end_turn, discarded failure subtype/error fields and
deleted its temporary directory. No separate sanitized stderr was found in the
pilot controls or the named session debug paths. No separately saved stderr was supplied in response to the optional artifact
query. Historical cause remains unverified.
The records do not establish schema, timeout, limit or crash as the cause. The
short wall times alone are not a cause. The live placeholder checks did not
reproduce these historical failures.

The provider now classifies before discarding diagnostic text. Enumerated failure
class/subtype, valid numeric API status, turn count and stderr byte count survive
in receipts; raw errors, stdout diagnostics and stderr never enter logs. Known
turn-limit/structured-output exhaustion, transient server/connection failures,
rate/usage limits and timeouts use native bounded exponential backoff, default
three total attempts and delays capped at 30 seconds. Invalid schema, invalid
request, authentication and unclassified exit errors remain non-retryable.
Every attempt retains measured accounting, or an explicit unknown reservation,
before another admission. Cached output and isolation checks retain their guards.

Regression tests exercise max-turn and 503 failures with three attempts,
deterministic schema/401 failures with one attempt, unknown failures with one
attempt, and a transient failure followed by success without lost usage.
Existing plain stderr rate-limit handling is retained. Self-review found and
fixed an intermediate regression for plain stdout rate-limit messages, with a
red/green test. None of these fixtures claims the original two failures were
proved transient. Future unclassified errors still fail closed with better metadata.

## R6 finding 4 — Local subscription cap with historical accounting retained

The pilot's final retained receipts contain **18,509,550 local tokens** and
**11,348,025 imported tokens**, totaling **29,857,575**. Under a 30M cap, a local
subscription policy leaves 11,490,450 tokens before pending/new reservations,
while the former history-inclusive policy left 142,425. These are accounting
comparisons, not new spending or a restarted run.

Native provenance ranges identify imported events. Budget.used_tokens still
includes all history and local usage. Subscription admission and actual-usage
stops subtract imported tokens only; reservations and unknown usage still count.
API calls retain history-inclusive admission, including in mixed-provider runs.
Reopening the log reconstructs both totals. STOP events expose total, local and
imported tokens. Existing methodology local/inherited totals remain; per-call
policy metadata and the exported policy list distinguish new local policy from
legacy history-inclusive calls rather than relabeling old receipts.

The native CLI imports provenance before ModelCalls/Budget initialization, so
this change reaches the actual run path. No imported receipt or charge is deleted,
no historical log is rewritten, and API dollar admission is unchanged. Regression
coverage checks import, local admission, reservation limits, actual overrun,
reopen, STOP totals, and retained API history-inclusive refusal.

## R6 finding 5 — Live subscription evidence and its limits

`runs/omega-round6-live/events.jsonl` contains two accepted isolation canaries,
one accepted placeholder formalise and one accepted placeholder propose_cuts.
All four were served by the pinned claude-opus-5-5 on Claude Code 2.1.306; all
reported two turns. Both canaries proved the existing context/tool isolation.
No API charge was incurred. The four calls report a combined subscription
list-price equivalent of **0.0891326 USD**, which is not API spending. Full
usage/latency receipts are in the run summary and
`omega-evidence/round6/live-verification.json`.

The first probe script mistakenly sliced the Bank object instead of Bank.entries
and failed before propose_cuts dispatch. Its accepted canary and formalise receipts
were preserved. The corrected continuation reopened the same log, performed the
required fresh canary, then dispatched only the missing cuts check. No formalise
call was repeated. Both scripts/transcripts are retained; no failed provider call
or unknown accounting arose from that script error. Live retry/limit recovery and
full-corpus generation were not exercised; retry behavior is proved offline.

## R6 finding 6 — Verification checkpoint and handoff scope

Before implementation, four of five new calibration/budget cases failed and the
unchanged API-policy case passed. Five exit-classification cases then failed on
the old behavior. After fixes, 75 provider/calibration tests passed, followed by
98 affected provider/call/integration tests. Four final restore/import/budget
regressions passed, and the stdout rate-limit regression passed after its red
failure. All 381 control anchors occur exactly once.

Full pytest passed **813 tests, 2 skipped / 815 collected** in **508.43 seconds**,
exit 0, under `ARA_LIVE_TEST=0 UV_OFFLINE=1`. All source hashes matched afterward.
Only then did the full control runner execute, driven sequentially by
`omega-evidence/round6/run-gates.py`: **381/381 mutations exited 1 and all 381
restorations exited 0**, in 1,692.45 seconds. All source hashes matched again
after the runner. `git diff --check` also passed.

The six new red transcripts were inspected. They fail on mismatched comparison
units, missing fixed-overhead propagation, restoration of the obsolete factor,
history-inclusive subscription admission, missing transient retry, and retrying
a deterministic schema failure. None is a syntax or call-signature failure.
`omega-evidence/round6/{gate-results.json,control-results.json,pytest-round6.txt,
controls-round6.txt,source-before-gates.json}` and copied new red/green transcripts
retain the evidence. Individual full-suite control transcripts remain under
`runs/delta-controls/`. No separate lint/typecheck gate is configured.

Final local revision: `e623021b4e79a5060137effaec3e81d5f2cbb416`. The ten changed files were reviewed
in native caller context and by a manual diff scan under the no-delegation brief;
no independent reviewer was used. Existing isolation, local output validation,
cache, reservation, correction routing and API admission paths passed the full
suite and controls. No source changed after verification. No push.

No implementation or required local verification remains. The retained-diagnostic
limitation prevents identifying the two original exit-1 causes; this deliverable
explicitly does not claim those old failures were schema, timeout, limit or crash.
Integration, independent review and any real-corpus rerun belong to the caller.
Do not repeat the live checks or alter the historical pilot to complete this task.
Final evidence receipt: `omega-evidence/round6/final-verification.json`.

Finding placement: corrected units, overhead and restore limits are in R6 finding
1; pilot replay and skip correction in R6 finding 2; historical diagnosis limits
and retry behavior in R6 finding 3; local cap and provenance in R6 finding 4;
live evidence and script recovery in R6 finding 5; verification, review scope and
handoff in R6 finding 6. The prior 23 findings remain in their original sections,
with the erroneous R5 comparison explicitly superseded above.

29 findings, 29 placed.

DONE omega round6 head=e623021b4e79a5060137effaec3e81d5f2cbb416 tests=813/815 negctl=pass rederived_factor=0.553224 windows_fitting=70/70 exit1_cause=diagnostics_discarded


# Round 7

## R7 finding 1 — One retry for an unclassified exit 1

The native transport grants at most one unclassified exit-1 retry, within the
configured total retry limit; retries=0 disables it. The event is named
unclassified_exit_retry and records attempt, reason and bounded delay. Every
attempt repeats admission and records measured usage or an unknown reservation.
Other unknown exit codes, auth, permission, invalid schema/request, budget and
credential/identity failures remain non-retryable. One retry is an operator
policy, not a claim that an unclassified failure is transient.

## R7 finding 2 — Sanitized diagnostics and limits

Failure receipts retain sanitized subtype/error category and the first stderr
line, capped at 200 characters after scrubbing known credentials, operator
identities, credential assignment patterns and prompt echoes. Two JSON/percent
decoding layers are supported; unresolved encoded material is suppressed.
Prompt/system fragment matching is conservative and can suppress benign text;
arbitrary paraphrases or novel encodings are not claimed. Later stderr lines
and raw diagnostic bodies are discarded. Historical exit causes remain unknown.

## R7 finding 3 — Verification, review and handoff

Resumed at e623021b4e79a5060137effaec3e81d5f2cbb416 on fix/subagent-final.
All six dirty files belonged to this round's resumed implementation. Earlier
focused evidence reports 108 passed, then 24 passed/70 deselected. Resume review
found subtype-only auth/request categories were not classified, allowing the
new unclassified retry. Five subtype cases failed while five nested-error cases
passed; adding subtype to classification fixed the five failures. A production
mutation control protects that path.

Full pytest passed **843 tests, 2 skipped / 845 collected** in **484.90 seconds**,
exit 0, under ARA_LIVE_TEST=0 UV_OFFLINE=1. All tracked source hashes matched
afterward. The full control runner then executed sequentially: **389/389
mutations exited 1 and all 389 restorations exited 0**, in **1,525.33 seconds**.
All source hashes matched again. git diff --check passed. No separate lint or
typecheck gate is configured. No source changed after these gates.

The eight new control transcripts were inspected: subtype-only auth/request
classification, enabling the unclassified retry, enforcing the one-retry cap,
credential scrubbing, identity scrubbing, prompt-echo scrubbing, truncation, and
JSON diagnostic scrubbing. They failed for the intended behavioral assertions,
not syntax or signature failures. Evidence is retained in
omega-evidence/round7, including gate-results.json, control-results.json, full
pytest/control output, new red/green transcripts, source-before-gates.json and
final-verification.json.

The six-file diff and native caller/accounting paths were reviewed manually.
Code review: skipped (ce-code-review unavailable) — its required independent
agent path conflicts with the explicit no-delegation brief. No independent
review is claimed. Manual review and simplification coverage are recorded in
omega-evidence/round7/manual-review.md; the subtype finding is fixed.

Final local revision: **a85c0af3a275bad2c6ff23c223e44a1ced894df1**. The committed tree matches
the exact source used for both gates, and the working tree is clean. The
CLAUDE.md symlink was verified as a link to its tracked target, separately from
regular-file content hashes. No live, API or paid model calls were made for
round 7. No push. No implementation or required local verification remains;
integration and any live reproduction belong to the caller.

Finding placement: retry bounds, configuration and accounting in R7 finding 1;
diagnostic retention, scrubbing limits and unrecoverable historical causes in
R7 finding 2; subtype-only fix, tests, controls, review limits and final revision
in R7 finding 3. The prior 29 findings remain in their original sections.

32 findings, 32 placed.

DONE omega round7 head=a85c0af3a275bad2c6ff23c223e44a1ced894df1 tests=843/845 negctl=pass


# Round 8

## R8 finding 1 — kappa2 F1 fixed by suppression

Kappa2 correctly found that the round-7 sanitizer retained ordinary quoted JSON
token/password values and short literal prompt echoes. Those are not exotic
encodings or paraphrases; the earlier caveat did not cover the observed defects.
Round 8 supersedes R7 finding 2's retention design. The sanitizer is deleted.
No free-text stderr or stdout diagnostic fields are persisted. Only exact known
CLI failure subtypes, fixed recognized-category labels and numeric diagnostic
metadata remain. Unknown subtypes are omitted, unrecognized errors become
unknown, and no regex capture is retained. Existing validated routing and usage
fields remain in the native receipts. The one-retry transport bound, auth/request
refusal and accounting remain intact. Historical logs have not been rewritten;
the original pilot's failure causes still cannot be reconstructed.

## R8 finding 2 — Verification and handoff

Work began from a85c0af3a275bad2c6ff23c223e44a1ced894df1 on fix/subagent-final,
with a clean tree. The three kappa2 production-subprocess probes failed against
the old implementation, alongside 13 new diagnostic/category assertions:
16 failed, 85 deselected. After the suppression change, 117 provider/call tests
passed. Tests inspect provider_error and MODEL payloads and cover arbitrary
JSON subtype/category/error/result fields as well as recognized category labels.

Full pytest passed **845 tests, 2 skipped / 847 collected** in **455.69 seconds**,
exit 0, under ARA_LIVE_TEST=0 UV_OFFLINE=1. All tracked source hashes matched
afterward. The full control runner then executed sequentially: **387/387
mutations exited 1 and all 387 restorations exited 0**, in **1,555.81 seconds**.
All source hashes matched again. git diff --check passed. No separate lint or
typecheck gate is configured. No source changed after verification.

Five controls for removed scrubbing/truncation code were replaced with three
controls for text suppression, subtype allowlisting and category enumeration,
leaving 387 total. Retry and auth/request controls remain. All mutation anchors
occur exactly once. The three new controls were run both before and during the
full control gate. Their red transcripts fail on the three kappa2 retention
probes, unknown-subtype retention and arbitrary-category retention respectively;
none is an import, syntax or signature failure. All restored tests passed.

Evidence is retained in omega-evidence/round8: red.txt, focused.txt,
gate-results.json, control-results.json, pytest-round8.txt, controls-round8.txt,
source-before-gates.json, copied red/green transcripts and final-verification.json.
Full per-control transcripts remain in runs/delta-controls in the omega checkout.

Manual review traced classification, accepted/rejected receipt construction,
malformed JSON, security rejection and both native event consumers. The
sanitizer and decoding import are gone; the fixed pattern table returns only
constant labels. Review scope and limitations are in manual-review.md.
Code review: skipped (ce-code-review unavailable) — the required independent
agent path conflicts with the same-task explicit no-delegation brief. No
independent review or live pilot success is claimed.

Final local revision: **6bd76796a1a7a68faf839b0f47d1ddd94bb2e925**. The committed tree matches
the exact source used for both gates; symlink targets were checked separately
from regular-file hashes. The working tree is clean. No live or paid calls,
credential changes, historical-log rewriting or push occurred. No requested
implementation or local verification remains. Integration and any live
reproduction belong to the caller.

Finding placement: kappa2 F1, the superseded round-7 claim, suppression policy
and historical-diagnosis limits are in R8 finding 1; tests, control replacement,
review limits, exact revision and delivery scope are in R8 finding 2. The prior
32 findings remain in their original sections, with R7 finding 2 superseded.

34 findings, 34 placed.

DONE omega round8 head=6bd76796a1a7a68faf839b0f47d1ddd94bb2e925 tests=845/847 negctl=pass fixed=kappa2-F1


# Round 9

## R9 finding 1 — Current credential source and bounded auth retry

Pilot 3's host-file replacement and subsequent 401 receipts support the stale-auth
hypothesis but do not prove the old token's value. The provider did cache its
first credential read. Round 9 removes token-valued provider state and keeps only
a live source-path reference, opened read-only for every subprocess. Atomic host
replacements are visible without restarting the provider. A missing/malformed
selected file refuses explicitly instead of using an old environment token.

The link is a read-only source reference, not a writable filesystem symlink.
The current access token uses the previously authorized per-call environment
transport; no token file is written and no refresh token is handed to the child.
Same-user environment visibility is disclosed. Call-local secret scanning covers
in-flight calls even if the source changes; cached output scans current values.
ARA never refreshes or rotates credentials. Existing historical logs are unchanged.

cli_auth_error now gets at most one auth_refresh_retry per transport call, within
the configured total retry budget; retries=0 disables it. This covers recognized
auth errors including 401 and permission-class errors. The event means re-read,
not refresh. Each retry repeats admission and measured/unknown accounting. The
unclassified retry cap remains separate; schema/request failures stay non-retryable.

## R9 finding 2 — Live smoke, verification and handoff

Work began clean at 6bd76796a1a7a68faf839b0f47d1ddd94bb2e925. Five assertions
failed against the stale implementation and two baseline/bound cases passed.
After implementation, 123 provider/call tests passed, followed by seven final
focused cases. Tests cover host replacement between calls and after 401,
persistent failure, retries=0, measured/unknown accounting, access-token-only
transport, unchanged source and scanning during an in-flight replacement.

The authorized live smoke in runs/omega-round9-live accepted its isolation canary
and exactly one formalise stage call, both on claude-opus-5-5 / CLI 2.1.306.
Wall times were 9.90 and 3.25 seconds. Combined usage was 6,102 tokens and
0.0561938 USD-equivalent subscription usage, with 0 API USD. The source credential
file's inode, size and mtime were unchanged. No real credential refresh was
induced; host replacement and 401 recovery are proved offline. No pilot restart
or further live call was performed. Live summary, receipts and script are
retained under runs/omega-round9-live and omega-evidence/round9.

Full pytest passed **851 tests, 2 skipped / 853 collected** in **455.12 seconds**,
exit 0, under ARA_LIVE_TEST=0 UV_OFFLINE=1. All tracked source hashes matched
afterward. The full control runner then executed sequentially: **389/389
mutations exited 1 and all 389 restorations exited 0**, in **1,539.07 seconds**.
All source hashes matched again. git diff --check passed. No separate lint or
typecheck gate is configured. No source changed after verification.

Two obsolete private-copy controls were replaced with fresh-read and access-token
controls, and two auth-retry controls were added. All 389 anchors occur exactly
once. Four new/replacement control transcripts were inspected: they fail on
wrong access-token transport, stale token reuse after source replacement, missing
retry and excess retry respectively. The access-token assertion is subsequently
wrapped by the normal unknown-accounting BudgetStop; the initial failure clearly
shows refresh-token handoff instead of access-token handoff. None is an import,
syntax or call-signature failure. All four also passed their focused restoration
checks before the full gates.

Evidence is retained in omega-evidence/round9: red.txt, focused.txt,
final-focused.txt, gate-results.json, control-results.json, pytest-round9.txt,
controls-round9.txt, source-before-gates.json, copied red/green transcripts,
live-check.py, live-check.txt, live-verification.json and final-verification.json.
Full per-control transcripts remain in runs/delta-controls in the omega checkout.
Manual review scope and limitations are in manual-review.md. The six-file diff
and native callers were reviewed; no further implementation blocker was found.
Code review: skipped (ce-code-review unavailable) — its required independent-agent
path conflicts with the same-task explicit no-delegation brief. No independent
review, live refresh recovery or completed-pilot success is claimed.

Final local revision: **9a8e51ad7f832964a8602cc831bf3fa704354e5a**. The committed tree matches
the exact source used for both gates; symlink targets were checked separately
from regular-file hashes. The working tree is clean. No API spend, credential
refresh/rotation, historical-log rewriting or push occurred. No requested
implementation or local verification remains. Integration and any pilot
continuation belong to the caller.

Finding placement: current-file semantics, environment visibility, bounded auth
retry, unchanged accounting and the historical-cause limitation are in R9
finding 1; live scope, tests, control replacement, review limits, exact revision
and handoff are in R9 finding 2. These supersede the earlier private-copy
transport and non-retryable-auth policy. The prior 34 findings remain in their
original sections.

36 findings, 36 placed.

DONE omega round9 head=9a8e51ad7f832964a8602cc831bf3fa704354e5a tests=851/853 negctl=pass fixed=stale-auth


# Round 10

## R10 finding 1 — Native Codex provider and current completion status

Added `codex_cli` beside `claude_code` through the existing provider factory,
ModelCalls, budget, construction-stage dispatch, counting, receipts, cache,
retry, concurrency and methodology seams. Each request starts one fresh Codex
process, with an explicit per-stage model pin and local schema validation.
Extraction and web evidence acquisition refuse on this transport; existing API
extraction receipts remain authoritative for their serving model. The intended
pilot methodology is imported Opus 5 API extraction and Codex construction/search;
this change does not claim that either a new extraction or a pilot ran.

The implementation and offline verification can be committed locally, but the
round's live acceptance remains BLOCKED. `/home/dev/.codex/auth.json` contains
an API-key login, not ChatGPT subscription credentials. The live preflight
refused with `subscription_login_required` before any model process. A request
for the existing ChatGPT auth-file path was left pending. No login, credential
refresh/rotation, API-key fallback, paid call, pilot restart or push was performed.

## R10 finding 2 — Context and credential isolation

Supported environment: Linux with bubblewrap and exactly Codex CLI 0.163.0.
Unknown CLI versions refuse until their controls are revalidated. Each call
uses `exec --ephemeral --ignore-user-config --ignore-rules
--skip-git-repo-check --json -s read-only`, never approval, an empty temporary
`-C` directory, a fresh HOME, no project instructions, and disabled shell,
unified execution, goal tools, web, images, MCP, apps, plugins, hooks, memory,
subagents and plan/input helpers. Full flags are in source and methodology.

A mount/PID namespace hides operator homes, host /tmp and /run, and host process
state. The current auth path is opened read-only per call and bind-mounted by
that file descriptor; the output scan uses credentials from the same inode.
This sees host atomic replacement on the next call without a scan/mount race.
CODEX_HOME is seeded with only a link to that read-only mount. Important CLI
constraint: it must generate runtime state, so CODEX_HOME is a disposable tmpfs,
not a permanently single-entry read-only directory. No generated state or raw
CLI stream is copied back to the host. Host credential writes are denied;
`CODEX_REFRESH_TOKEN_URL_OVERRIDE=disabled://refresh` disables the refresh route.
No credential values enter argv, retained output, receipts or cache.

Offline tests replace the auth file between calls and after a 401, exercise the
single bounded `auth_refresh_retry`, and verify that source writes fail. They
also place AGENTS and memory sentinels in the operator home and show that the
child cannot see that home. Runtime git name/email and forbidden-name scans
remain mandatory. These checks are evidence of the enforced local boundary;
they are not a live model's context report.

## R10 finding 3 — Tool rejection, diagnostics and serving identity

Only enumerated lifecycle, reasoning, final-message and error events are
accepted. Command execution, file reads/changes, web/MCP/tool/function calls,
and unknown event types reject before response retention. Final JSON is
retained only after credential and identity scans and normal local validation.
Reasoning, raw event streams and stderr are never persisted. Error diagnostics
contain only fixed categories and validated numeric fields. Nonfatal warning
items on an otherwise completed turn retain only a count; top-level/terminal
errors still reject. Rate/usage limits use the existing bounded backoff.

The actual installed CLI was exercised against a local synthetic Responses
endpoint. The final request advertised **zero tools**, contained the native
canary prompt, and had no discovered operator-context or identity matches.
The synthetic structured response was accepted. This caught and fixed two
issues missed by the fake binary: goal tools needed an additional disable flag,
and normal warnings arrive as error items. This was an offline protocol check,
not a ChatGPT call or a substitute for the requested live tool-invitation test.
A local synthetic 401 was classified without diagnostic text retention.

That same check confirmed a receipt limitation: CLI JSON omits the served model
even when the service response supplies it. If events do report a model it must
match the pin; otherwise serving identity is explicitly `unverified`, including
in normal model-version logs. It is never inferred from `-m`. The requested
smoke model is `gpt-5.4`; no live availability or served identity is claimed.

## R10 finding 4 — Accounting and calibration limits

Admission reuses the measured API-receipt calibration table with the conservative
prior runtime overhead and two-request reservation. Its seed uses the Anthropic
tokenizer; it is not a Codex tokenizer bound. Single-turn Codex input, including
cached input once, is compared with estimated initial input. Run-local factors
and overhead only increase, scoped by model/kind and restored through existing
observations. There is no free counter. Subscription calls consume token caps
and bypass API-dollar caps without claiming API charges.

Codex reports tokens but no USD equivalent. Receipts use null for the equivalent;
methodology counts calls with unavailable equivalents rather than asserting
measured zero. CLI output has no hard token-limit flag: the configured allowance
is a reservation, and measured overruns can stop the run after the response.

## R10 finding 5 — Verification, revision and remaining work

Full pytest: **890 passed, 2 skipped / 892 collected**, exit 0, in **572.91
seconds** (574.42 seconds including runner startup). The full control runner
then ran sequentially: **406/406 mutations exited 1 and all 406 restorations
exited 0**, exit 0, in **1,887.23 seconds**. Both ran with ARA_LIVE_TEST=0 and
UV_OFFLINE=1. Source hashes matched after each gate and again against the exact
committed tree. git diff --check passed. No source changed after the gates.

Final local revision: **9a01385dad43e39a6d9e7f5573e3222cf4d3ed0f**, branch `fix/subagent-final`, based on the
requested `50ddc05` (rebase confirmed already up to date). The working tree is
clean. The final live preflight again exited 2 with subscription_login_required;
zero live stage calls were made. No push occurred.

Thirty Codex fake-binary cases exercise the actual subprocess/mount boundary,
plus the existing Claude-provider/calibration regression suite. Nine new
production-wire mutations were killed and restored in focused checks. Controls
cover tool/unknown event rejection, read-only credentials, API-key refusal,
per-stage model pinning, context rejection, suppressed diagnostics, refresh
endpoint disabling and goal-tool disabling. Control failure transcripts were
inspected; none depends on import/syntax failures. Full-run results supersede
focused counts below.

The first full pytest run was intentionally interrupted when the local actual-CLI
probe found the two startup issues. Both full gates were restarted on the fixed
source; the interrupted run is not counted as a pass. Manual inline review and
CE Simplify Code review were performed under the explicit no-delegation brief;
no independent-agent review is claimed. No separate lint/typecheck gate exists.

Evidence: `/home/dev/ara-work/reports/omega-evidence/round10/`, including the
pre-change red run, focused runs, mutation transcripts, local CLI probe scripts
and typed summaries, live-preflight refusal, gate results and source hashes.
Full control transcripts remain in `runs/delta-controls`. Official references:
https://developers.openai.com/codex/cli/reference/ and
https://developers.openai.com/codex/config-schema.json (fetched 2026-10-24).

Remaining work: supply an existing ChatGPT credential file, run the live isolation
and tool-invitation canaries, then two placeholder stage calls using the retained
`live-check.py`. Resolve any account/model-specific failures before pilot use.
Live isolation/tool blocking are therefore reported `failed` (unproven), and
live stage smoke is `0/2`. The final model field names the requested pin only.

Finding placement: native integration and blocked-live status are in R10 finding 1;
OS/CLI boundaries and writable tmpfs qualification in finding 2; protocol checks,
error handling, tool proof scope and missing serving identity in finding 3;
calibration/usage bounds in finding 4; executed gates, exact revision and recovery
steps in finding 5. The prior 36 findings remain in their original sections.

41 findings, 41 placed.

DONE omega round10 head=9a01385dad43e39a6d9e7f5573e3222cf4d3ed0f tests=890/892 negctl=pass isolation=failed tools_blocked=failed live_smoke=0/2 model=gpt-5.4


# Round 11

## R11 finding 1 — Separate ChatGPT login, no worker-auth fallback

`codex_cli.auth_file` is now required and config.yaml points it to
`/home/dev/.config/ara/codex-home/auth.json`. This existing nested config key
already selects a source; round 11 removes its implicit CODEX_HOME/default-home
fallback. Missing or blank configuration refuses with
`subscription_auth_file_required`. A missing, malformed or API-key source
continues to refuse rather than switching logins. Neither the worker's default
~/.codex/auth.json nor its inherited CODEX_HOME is opened as a fallback.

Each call still opens the selected path fresh, scans and mounts that same inode,
and exposes it only through the read-only per-call link. No credential copy,
logging, refresh or rotation was added. The selected source is 0600, and all live
attempts left its inode/size/mtime unchanged. A scan of 94 retained evidence/run
files found no current token or account values. Regression tests cover required
configuration, no worker-file access, and missing selected-file refusal; prior
replacement-between-calls and 401 re-read tests remain green.

## R11 finding 2 — Live isolation blocker; tool invitation exercised

The credential blocker from Round 10 is resolved. Live model availability differs
from the earlier requested pin: gpt-5.4 and gpt-6.1 received invalid-request
responses. A read-only account catalog request listed gpt-reserve, gpt-6-luna,
gpt-5.6-terra and gpt-5.6-luna. Subsequent checks pinned gpt-6-luna; one strict
canary also tried gpt-5.6-terra. Serving identity remains `unverified`: CLI
0.163.0 does not expose it in its JSON receipts. The final model field is the
requested pin, not a fabricated serving receipt.

The live canaries exposed bundled skills despite the prior host-discovery
skip. Explicitly disabling `skills.bundled.enabled` and
`skills.include_instructions` cleared the skills field. A minimal task-only
model instruction file also replaces the coding-agent defaults; native stage
prompts and developer instructions remain. Codex canary wording now requests
empty absent tools and actual callable tools, not inferred capabilities. The
original empty-context and tool-event rejection conditions were not weakened.

After these changes the diagnostic canary reported empty skills, memory,
AGENTS.md and CLAUDE.md fields and no discovered forbidden-term matches, but
still reported generic tools. Recognized names included apply_patch,
spawn_agent and generic MCP resource functions. This is not evidence that those
tools actually executed; it does mean the strict isolation preflight did not
pass. Both tested available models failed that preflight. No production stage
was allowed past it. Isolation is therefore **failed/unproven**, and requested
stage smoke is **0/2**. This round is not a completed live-verification result.

The separate live tool-invitation canary explicitly asked for `ls ~` and reads of
global AGENTS.md and memory. It completed one CLI turn with **no tool events**, then
was rejected by the unchanged context check. This proves the requested
no-tool-event condition for that invitation run; it does not turn the failed
context canary into success. It reported 4,327 input and 787 output tokens, no
cache/tool usage, and 9.60 seconds CLI wall time. Thus `tools_blocked=proven`
refers to this executed invitation and the production event-rejection controls.

There were 12 canary attempts in total: three request failures with unknown
actual usage and nine measured responses rejected by the context gate. Measured
usage totaled 77,130 tokens and 138.47 seconds of ModelCalls wall time; unknown
attempts retain reservation accounting, not invented actuals. All receipts are
subscription usage with zero measured API spend; Codex USD equivalent remains
unavailable. Diagnostics retained only fixed categories/pattern labels, lengths,
counts and numeric metadata. No rejected raw context or stderr was retained.

## R11 finding 3 — Gates, revision and handoff

Full pytest passed **892 tests, 2 skipped / 894 collected**, exit 0, in
**549.85 seconds** (551.01 including runner startup). The full control runner
then ran sequentially: **409/409 mutations exited 1, all 409 restorations exited
0**, exit 0, in **2,050.68 seconds**. Both ran with ARA_LIVE_TEST=0 and
UV_OFFLINE=1. Source hashes matched after each gate and against the exact
committed tree. git diff --check passed. No source changed after verification.

Final local revision: **2e76caca6b4e37f901c6091071e6e2f9475eada6**, branch `fix/subagent-final`, clean working
tree. No push. The credential fix and offline verification are complete; live
isolation and the requested stage smoke remain blocked as described above.

The initial new-test run failed on worker-home fallback and passed explicit-source
selection (1 failed/1 passed), then all 32 Codex tests passed. The final focused
provider/calibration suite passed 149 tests in 42.57 seconds. Three new controls
were killed and restored for worker fallback, bundled skills and model
instructions. Their failure transcripts were inspected; none is an import or
syntax failure. Full gates supersede focused counts.

Inline review covered the auth selection path, new isolation flags/instruction
file, provider-specific canary render and unchanged rejection/accounting seams.
No independent-agent review is claimed under the original no-delegation brief.
No separate lint/typecheck gate is configured. No push, pilot restart, credential
rotation or historical-log rewrite occurred.

Evidence is in `/home/dev/ara-work/reports/omega-evidence/round11/`; individual
append-only live runs are `runs/omega-round11-*`. It includes the red test,
focused results, new-control transcripts, model catalog (IDs only), typed canary
classification, `live-verification.json`, source hashes and full gate results.
The retained `live-check.py` records the strict canaries and two planned stage
calls; it must use a new run directory for any future attempt.

Remaining work: determine why the live models report generic tools despite the
CLI disable controls, establish a passing isolation canary without waiving it,
then run two placeholder stages. The credential-path change and offline gates
are complete; live isolation and stage acceptance remain blocked. Do not start
an ARA pilot on the basis of these results.

Finding placement: credential selection and noninterference evidence are in
R11 finding 1; account/model availability, bundled-context fix, strict live
blocker, serving-ID limit and measured/unknown usage are in finding 2; exact
revision, full gates, review limits and recovery work are in finding 3. Earlier
41 findings remain in their original sections; the Round 10 missing-ChatGPT-auth
blocker is superseded by the live context blocker described here.

44 findings, 44 placed.

DONE omega round11 head=2e76caca6b4e37f901c6091071e6e2f9475eada6 tests=892/894 negctl=pass isolation=failed tools_blocked=proven live_smoke=0/2 model=gpt-6-luna


# Round 12

## R12 finding 1 — Operator-approved preflight rule

The operator clarified that the competition boundary excludes operator content
and customizations, while generic built-in tool definitions may be visible with
disclosure, like Claude's StructuredOutput. The Codex canary now requires empty
skills, memory, AGENTS.md and CLAUDE.md fields, zero forbidden-term and operator
identity matches, and the unchanged tool-event rejection path. Any tool or
unknown event still rejects the response. Credential scans, fresh sessions,
read-only sandbox/mounts, separate required auth source and disabled refresh
remain unchanged.

Visible tool names are recorded in the canary's CLI receipt and isolation
evidence, and exported through log-derived methodology. The policy explicitly
states that visible definitions do not authorize use. Task-only model
instructions additionally prohibit tools for any purpose, including commands,
file reads, web and delegation. This is the operator's authorized change to
the pass rule; it does not waive an operator-context or execution check.

## R12 finding 2 — Live isolation and stage smoke passed

The live run `runs/omega-round12-live` accepted its isolation canary and exactly
two native placeholder stage calls: formalise(P) and map_leaf(Q, empty frozen T).
All three ran fresh CLI sessions with `-m gpt-6-luna` on Codex CLI 0.163.0 and
passed normal local schema/seam validation. The canary reported empty skills,
memory, AGENTS.md and CLAUDE.md; all 51 forbidden-term checks and runtime git
name/email scans passed. No tool event occurred. The separate 0600 ChatGPT auth
file's inode, size and mtime remained unchanged. An initial scan of 13 retained
run/evidence files found no current credential token or account values.

The nine visible generic names were clock.clock__curr_time,
collaboration.followup_task, collaboration.interrupt_agent,
collaboration.list_agents, collaboration.send_message, collaboration.spawn_agent,
collaboration.wait_agent, functions.exec and functions.wait. They are disclosed
as definitions, not executed tools. Their names occur in both receipts and
methodology. The prior tool-invitation canary already produced zero tool events;
this round did not repeat that invitation. Production-wire tool-event rejection
was reverified offline.

Requested model: **gpt-6-luna**. Served identity: **unverified**, because the CLI
JSON still omits a trustworthy serving model. No serving claim is inferred from
the request pin. CLI wall times were **16.3436 s**, **2.6365 s**, and **2.7549 s**
for the canary, formalise and map_leaf respectively. Median across all three:
**2.75 s** (the final-line metric); median for the two stage calls alone: **2.70 s**.
Usage totaled **15,861 tokens**: 5,839 canary, 5,665 formalise and 4,357 map_leaf,
with no cache or server-tool usage. This is subscription usage with no measured
API spend; Codex does not report a USD equivalent. These checks prove the
requested smoke, not a completed pilot or generic model-quality result.

## R12 finding 3 — Verification and local handoff

Full pytest passed **899 tests, 2 skipped / 901 collected**, exit 0, in
**485.51 seconds** (486.99 including runner startup). The full control runner
then ran sequentially: **411/411 mutations exited 1, all 411 restorations exited
0**, exit 0, in **1,639.38 seconds**. Both ran with ARA_LIVE_TEST=0 and
UV_OFFLINE=1. Source hashes matched after each gate and against the exact
committed tree. git diff --check passed. No source changed after verification.

Final local revision: **7e5219a837de0ed126c50c2dbbe8dc49036f68e9**, branch `fix/subagent-final`, clean working
tree. No push. Isolation is proven under the operator-approved rule and live
stage smoke passed **2/2**.

The new visible-tools regression first failed under the prior strict rule while
six operator-content regression cases passed. All 39 Codex tests then passed;
the final focused provider/calibration suite passed 156 tests in 43.35 seconds.
The visible-tools test proves receipt and methodology disclosure, accepts a
normal stage, and still rejects an injected command event. The six context
cases cover skills, memory, AGENTS/CLAUDE content, forbidden names in tool text
and operator identity in tool text. Existing credential/retry/isolation tests
remain unchanged and green.

Four focused controls were killed and restored: tool-event rejection, required
empty context, visible-name receipt retention and the explicit no-tools
instruction. Two are new to this round. Failure transcripts were inspected;
none depends on import/syntax failures. Inline review found no remaining
implementation or verification blocker under the revised rule. No independent
review is claimed under the original no-delegation brief. No separate lint or
typecheck gate is configured.

Evidence is retained in `/home/dev/ara-work/reports/omega-evidence/round12/`:
red/focused results, focused mutation transcripts, live script and typed
verification, manual review, source hashes and full gate results. Native
append-only receipts and methodology remain under `runs/omega-round12-live`.
A stale tools_blocked=false placeholder inherited by the smoke summary script
was replaced with tool_invitation_executed=false; no event log was rewritten.
No credential refresh/rotation, API-key fallback, pilot restart or push occurred.
No requested Round 12 work remains. Integration and pilot continuation belong
to the caller.

Finding placement: the approved context/visible-tools rule and unchanged hard
checks are in R12 finding 1; executed live scope, names, model-identity limit,
measurements and credential evidence are in finding 2; exact revision, gates,
review limits and handoff are in finding 3. Earlier 44 findings remain in their
original sections; the prior tools-visible isolation blocker is superseded by
the operator's revised rule and this passing live proof.

47 findings, 47 placed.

DONE omega round12 head=7e5219a837de0ed126c50c2dbbe8dc49036f68e9 tests=899/901 negctl=pass isolation=proven live_smoke=2/2 model=gpt-6-luna median_call_s=2.75

# Round 13

## R13 finding 1 — Pilot failure reproduced across the complete schema inventory

Rebased the round-13 work onto main **9aad0132d3f78a5e18dac4f00a5e51365accbfc0**
(including rho2's local OCR changes) before implementation. The initial
untransformed Codex transport was exercised with placeholders across all **12
native stage schemas / 14 stage and correction routing cases**, after its
isolation canary. This covers construction, both targeted corrections, targets,
all structured search stages and writing. Formula is an embedded utility schema;
API-only extraction and schema-less web retrieval are explicitly excluded.

The baseline produced **7 accepted, 6 schema refusals, 1 incomplete/output-limit
failure**. Both select_t_roots cases rejected `roots.uniqueItems`; both
build_t_batch cases rejected `new_symbols.items.evidence_ids.uniqueItems`;
audit_essay rejected `labels.items.node_ids.uniqueItems`; and
verify_originality_citations rejected `items.items.allOf`. The CLI reported
HTTP 400 / invalid_json_schema, classified as non-retryable cli_invalid_schema.
build_t returned an incomplete/max_output_tokens error and was not counted as
schema acceptance. The raw compiler message was printed in the terminal only;
normal logs/evidence retain sanitized categories and numeric metadata, not raw
stderr/error text. Baseline native logs remain in runs/omega-round13-baseline.

## R13 finding 2 — Versioned strict wire schema with local authority

`ara-openai-strict-v1` is a deterministic, non-mutating projection with an
explicit wire vocabulary. Every object is closed and every property required;
optional properties permit null sentinels. Recursive local references remain,
const becomes a singleton enum, and oneOf becomes anyOf. Unsupported constraints
are omitted only from the wire, retained in the native prompt/schema and
validated locally. Unknown output fields are not discarded. Normalization
removes only optional nulls that the native child schema disallows; required
nulls and natively nullable fields remain subject to original validation.

Accounting precedes normalization and validation. Raw responses/cache retain
wire JSON, and cache replay performs the same normalization. Receipts include
native/wire schema hashes and the transform version. Cache identity and
methodology disclose the version. Admission/calibration use the projected
schema size. Native schemas, isolation policy, tools rejection, auth handling
and original Anthropic schema preflight behavior are unchanged.

Regression coverage includes every current schema, recursive formulas and
unions, optional/null handling, uniqueness and other local-only constraints,
malformed/unknown fields, raw-wire retention, cache replay, accounting before
rejection, stage/correction inventory, stale config/local schema changes,
missing/cached/mismatched/tampered proof, and refusal before provider creation.
The missing-module test was red before implementation. Nine new production
mutation controls were killed and restored; failure transcripts were inspected
and did not depend on import/syntax failures. An existing extraction profile
control anchor was narrowed because the new CLI branch duplicated its text.

## R13 finding 3 — Live proof and mandatory pilot admission

`uv run ara codex-schema-preflight --config PATH --run-dir DIR` now invokes
all Codex-routed schemas with locally checked placeholder JSON. Use the same
profile and stage settings as the intended pilot. Every call must complete and
pass original-schema validation; no cache acceptance counts. A successful
manifest and individual measured native MODEL receipts are mandatory.

Run, construction resume and writing selection verify the preflight log's
hash chain and tail checkpoint, complete case coverage, and exact schema,
transform/CLI version, model, effort and system-prompt identities before creating
a provider. Set `codex_cli.schema_preflight_log` to the successful log. For an
existing run, `--codex-schema-preflight-log PATH` supplies new proof on
resume-construction or select without modifying historical configuration.
Missing, failed, incomplete or stale evidence refuses; rerun the preflight when
these inputs change. The successful evidence is not a portable claim for a
different model/profile or changed schema.

The live command passed **14/14** cases on requested **gpt-6-luna**, effort high,
Codex CLI **0.163.0**. The production gate subsequently verified the actual native
log at `/home/dev/ara-work/omega/runs/omega-round13-strict/events.jsonl`.
The isolation canary passed: empty operator customizations, zero forbidden or
identity matches, zero tool events, active tool-event rejection. Generic visible
tool names are disclosed in the receipt/methodology, as authorized in Round 12.
Served identity remains explicitly **unverified**; it is not inferred from the
requested model.

The canary plus stage cases used **70,014 tokens** and **53.14 seconds** summed
native call time; median stage-call time was **2.56 seconds**. The configured
per-stage preflight output reservation is 4,096 tokens (with the provider's
existing doubled reservation policy); Codex still has no hard output-token
flag. This is subscription usage, not measured API dollars; USD equivalent is
unavailable. Auth came exclusively from the separate configured ChatGPT file,
with per-call read-only fresh access. No credential refresh, rotation, copy or
worker API-key fallback occurred. No pilot was started. This proves grammar
and local placeholder acceptance, not pilot completion, semantic quality, or
web-retrieval capability. Extraction and web retrieval remain API-only/refused
by Codex.

## R13 finding 4 — Verification and local handoff

The full control runner ran **after** full pytest: **420/420 mutations exited 1,
all 420 restorations exited 0**, runner exit 0, in **1,637.88 seconds**. Both
full gates verified unchanged source hashes. All committed source contents match
the tested snapshot, with symlink targets separately verified; git diff --check
passed. No source changed after verification.

Final local revision: **8aa265fa32b97bdbae662108ba080950c5c73034**, branch
`fix/subagent-final`, clean working tree. Its parent is the requested main
9aad013. The changes are committed locally; no push occurred. The complete
schema preflight passed, and no requested Round 13 work remains. Pilot startup
and integration remain with the caller.

Full pytest passed **1,001 tests, 4 skipped / 1,005 collected** in **563.73 seconds**
(564.79 including startup), exit 0, with source hashes unchanged. The skipped
tests are two opt-in paid-provider checks and two opt-in local OCR/VL weight
checks; ARA_LIVE_TEST=0 and UV_OFFLINE=1 were set.

Focused verification passed **109 tests**. Inline review found no unresolved
implementation blocker; no independent review is claimed under the original
no-delegation brief. No separate lint/typecheck gate is configured. README and
DECISIONS record the projection, proof workflow, preserved local validation,
and existing-run override. Evidence, source hashes and full gate logs are in
`/home/dev/ara-work/reports/omega-evidence/round13/`. Native baseline/live receipts
and methodology remain in their run directories. No push or pilot restart.

Finding placement: baseline inventory and exact compiler blockers are in R13
finding 1; transform/local authority and regression controls are in finding 2;
live result, gate operation, model-identity limit, accounting, credentials and
scope limits are in finding 3; exact revision, test/control gates, review limits
and handoff are in finding 4. Earlier 47 findings remain in their original
sections. The Round-12 smoke's lack of construction-schema coverage is resolved
by this complete schema preflight, without upgrading it to a full-pilot claim.

51 findings, 51 placed.

DONE omega round13 head=8aa265fa32b97bdbae662108ba080950c5c73034 tests=1001/1005 negctl=pass codex_schemas=14/14 passed


# Round 14 — Codex extraction and subscription defaults

## R14 finding 1 — Native extraction and authoritative local checks

Codex CLI now supports `extract_paper` through the existing ModelCalls lifecycle,
including initial extraction, targeted correction and range reconciliation.
Claude Code still refuses extraction; both subscription transports continue to
refuse external web retrieval. No isolation or credential policy was relaxed.

The deterministic projection is now `ara-openai-strict-v2`. Object-level branch
refinements stay local instead of creating invalid partial strict objects at the
root. Structural unions remain projected. Optional-null reverse mapping visits
declared root fields before local validation. Native schema and graph checks
remain authoritative; invalid graphs are rejected, not silently repaired or
accepted. The version partitions caches and completed Codex paper reuse.

Page-range planning subtracts the transport's full output reservation, including
Codex's doubled allowance. Existing lossless range subdivision, per-call
admission, continuation limits, corrections, immutable range receipts,
reconciliation, grounding and quarantine stay in the native path. An indivisible
oversized page refuses before dispatch. Offline accepted-range salvage now
normalizes Codex optional-null responses and candidates before patch merge and
local validation; this fixes the reproduced null `discard_items` crash without
creating a provider or making recovery calls.

The initial regression suite was red (4 failed, 8 passed). Sixteen new extraction
cases cover all nine schema variants, local rejection, native correction,
multi-range reconciliation, doubled output reservation, single-page refusal,
preflight wire identity, reuse identity and offline salvage. The focused
provider/schema/native regression suite passed 226 tests; extraction plus salvage
passed 28. Six new extraction production mutations each failed their regression
and passed after restoration; failures were inspected for behavioral causes.

## R14 finding 2 — Live schema compatibility, isolation and bounds

The native extraction `schema-preflight` now uses the effective Codex projection
and requires complete locally valid responses, reserving 4,096 output tokens.
The API grammar probe retains its one-token behavior. All nine extraction input
variants deduplicated to **six distinct wire schemas, all six accepted live**.
The canary plus six schema calls used **33,039 tokens** and **27.70 seconds**
summed native call time.

The live paper run made five calls: one isolation canary and four extraction
attempts, using **90,905 tokens** and **156.79 seconds** summed native call time.
All recorded context admissions fit the configured 200,000-token bound; extraction
reserved 24,000 output tokens with the existing 48,000-token context allowance.
All receipts used `codex_cli`, requested `gpt-6-luna`, high effort, CLI 0.163.0.
Served identity remains **unverified**, not inferred from the request. Local
estimates are not a proven Codex tokenizer bound; CLI output limits remain soft.

Both isolation canaries passed with zero tool events and active tool-event
rejection. Generic visible tool names are recorded in native receipts under the
authorized Round-12 policy. Host customizations remained hidden. Authentication
used only the configured separate ChatGPT credential, freshly linked read-only
per call, without copying, logging, refreshing or rotating its value. The live
harness refused API provider construction. No API or Claude calls occurred.

A first paper-run launch refused before provider dispatch because its destination
already held the preflight cache. That refusal is retained; the actual run used
a fresh directory. Native logs are `runs/omega-round14-preflight/events.jsonl`
and `runs/omega-round14-extract/events.jsonl`. The evidence directory retains the
configuration, launch transcripts, numeric receipts and comparison script.

## R14 finding 3 — Two-paper quality is weak: zero accepted

**Codex accepted 0/2 papers. Quality is weak and does not meet the extraction
bar.** The batch process exited 0 under its existing policy of continuing with
disclosed paper failures; neither paper was accepted. No validator was relaxed
and no extra live retry was used to chase acceptance.

For `wright2007` (22 pages), the planner selected pages 1–11 for the first range.
Its initial response had 54 items and 12 inferences but an unknown link endpoint.
The first correction (9 patch items) still had an unknown endpoint; the second
(1 patch item) failed an invalid qualification relation. No range was accepted,
and the second range was not attempted. For `rothschild2012` (13 pages), the
initial full-range response had 63 items and 12 inferences but duplicate IDs;
that invalid candidate could not enter the correction merge. It also failed.

The accepted Opus baseline is the pinned artifact and logged outcomes from
`/home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt`.
Artifact lineage and PDF hashes were checked. Re-grounding those graphs against
the current PDF text reproduced their retained grounding results. They used the
older v4 acceptance contract and prompt, so this is a comparison with accepted
historical artifacts, not a controlled same-prompt model experiment.

| Paper / accepted provider | Items | Inferences | Grounded items | Grounded inferences | Quarantined | Acceptance |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| rothschild2012 / Opus | 71 | 13 | 70 (98.59%) | 12 | 1 (1.41%) | extracted |
| rothschild2012 / Codex | 0 | 0 | N/A | N/A | N/A | failed |
| wright2007 / Opus | 105 | 21 | 88 (83.81%) | 11 | 17 (16.19%) | extracted |
| wright2007 / Codex | 0 | 0 | N/A | N/A | N/A | failed |

Codex grounding was never reached. Its rates are **N/A**, not successful zero
quarantine rates. The following inventories distinguish rejected initial
responses from accepted Opus graphs; correction patch sizes are not cumulative
graph counts. Every accepted Codex kind count is zero.

| Item kind | Rothschild Opus accepted | Rothschild Codex rejected initial | Wright Opus accepted | Wright Codex rejected initial |
| --- | ---: | ---: | ---: | ---: |
| premise | 28 | 26 | 38 | 15 |
| intermediate_conclusion | 10 | 3 | 21 | 7 |
| inference | 13 | 12 | 21 | 12 |
| reported_view | 6 | 5 | 12 | 10 |
| attacked_view | 6 | 2 | 2 | 0 |
| qualification | 6 | 8 | 8 | 5 |
| conclusion | 2 | 4 | 2 | 3 |
| distinction | 0 | 3 | 1 | 2 |

Lexical grounding alone does not establish source fidelity. Schema compatibility
and placeholder acceptance do not establish graph quality or pilot completion.
No full pilot was started. Improving extraction quality remains future work.

## R14 finding 4 — Operator-selected default and retained gates

Per the operator's same-task instruction, committed `config.yaml` now defaults to
**`codex_cli` / `gpt-6-luna` for every stage and profile**, including extraction,
pilot and extraction-full, with **no fallback**. API adapters and prices remain
available through explicit private provider/model configuration. This is the
operator's no-API-credit routing choice, not an endorsement of the weak quality
result above. The ordinary and full extraction model overrides are both pinned.

The isolation canary, tool-event rejection and matching pilot schema-preflight
requirements remain. The v2 projection changes proof identity: older v1 pilot
receipts are stale and must be regenerated before a pilot. Full extraction still
requires explicit finite caps; it does not become an uncapped default. External
web retrieval remains unsupported on Codex and there is no automatic API escape.

Dedicated tests check every schema-backed stage and all five effective profiles.
Three default-config mutation controls independently revert the main provider,
ordinary extraction model and full-extraction model; each fails and restores
green. Existing offline/API fixtures now explicitly select their historical
model/transport contract. README offline commands generate an ignored mock
configuration; API instructions explicitly require an API configuration.
Affected consumer tests passed 79 tests, with one opt-in skip. A transient test
import syntax error from the fixture edit was corrected; its failed consumer
was rerun successfully before final gates.

## R14 finding 5 — Verification and local handoff

Full pytest passed **1,301 tests, 4 skipped / 1,305 collected** in
**1,458.72 seconds** (1,459.97 including startup), exit 0. The skipped checks are
two opt-in paid-provider tests and two opt-in local OCR/VL weight tests.
`ARA_LIVE_TEST=0` and `UV_OFFLINE=1` were set. Source hashes matched after pytest.

The full control inventory passed **572/572 mutations**, each exiting 1 with its
restoration exiting 0. Verification was sequential: full pytest, then controls.
The first control process received SIGTERM after 327 completed cases. No cause
was established. All source hashes already matched the frozen snapshot; the
completed receipts were preserved and verified against the inventory. The
interrupted case was repeated in full, and the original runner completed the
remaining **245/245** cases in **2250.04 seconds**.
The resumed harness checked the combined ordered 572-case inventory and verified
all source hashes again, then exited 0. This is complete control coverage across
two sequential slices, not a claim of an uninterrupted single process. The
nine new controls' final failure transcripts were inspected; none relied on
syntax or import failure. No source edits or other tests ran during mutations.

Final local revision: **c774e94a277703556d95f2722c5fa7a4055e090a**, branch
`feat/codex-extraction`, direct parent **9b9999730c32b4dd0f06ef80a075920633d1acc9** (requested main 9b99997).
The working tree is clean. All 233 committed file contents match the tested
snapshot, with symlink targets checked separately; git diff --check passed.
Changes were committed locally; **no push** occurred.

Inline inspection covered native extraction, projection, validation, ranges,
salvage, cache/reuse identity, all default profiles, unchanged isolation and
preserved gates. No independent review is claimed under the original
no-delegation instruction. No separate lint/typecheck gate is configured.
README, provider/extraction guides and DECISIONS document the resulting behavior.
The implementation and requested quality evaluation are complete; the disclosed
weak extraction quality and unsupported web retrieval remain operational limits.

All gate logs, pre/post source verification, resumed control receipts, live
configuration and numeric quality comparison are retained under
`/home/dev/ara-work/reports/omega-evidence/round14/`. Real paper inputs and graph
artifacts remain outside committed source or in ignored run directories.


Finding placement: native extraction, projection, bounds and salvage are in R14
finding 1; schema compatibility, isolation, usage and identity limits are in
finding 2; both failures, item inventories, historical comparison and quality
limits are in finding 3; defaults, API opt-in and retained gates are in finding 4;
final revision, full test/control evidence and delivery limits are in finding 5.
Earlier 51 findings remain in their original sections.

56 findings, 56 placed.

DONE omega round14 head=c774e94a277703556d95f2722c5fa7a4055e090a tests=1301/1305 negctl=pass codex_extract=0/2 quality=weak default=codex_cli


# Round 15 — Structural extraction repair and gated retest

## R15 finding 1 — Preserve rejected candidates without inventing links

Starting from c774e94, rejected initial duplicate IDs now use the existing stable
patch-ID renamer. Collision-free `__duplicate_N` IDs retain every item, its order
and every non-ID field. Each rename is logged separately from the unchanged raw
response. No source content, attribution, relation or item is silently removed.

For distinct duplicates referenced by other items, renaming does not establish
which item a link meant. The correction request lists each referring item in
`required_reference_updates`; a patch must explicitly address those items or
explicitly discard unsupported rejected items with source-based reasons. An
empty/unrelated patch cannot silently select the first duplicate. Existing
ambiguous correction-patch duplicates still refuse. This is a model correction
boundary, not deterministic semantic repair.

Rejected Codex responses and failed patches receive the same optional-null wire
normalization before recovery merge as at the normal response boundary. This
preserves the cumulative candidate when a failed patch includes null optional
fields. Accepted results replay through offline range salvage without a model.
The acceptance identity advances to `rich-paper-acceptance-v7`: v6 paper outcomes
are not automatically reusable. Previously reviewed v4/v5 migrations retain full
source/graph revalidation. The strict wire projection remains v2.

Proof-first structural tests produced **8 failed, 3 passed** before the fix.
The first focused suite passed 66 tests; broader extraction, Codex, salvage and
reuse coverage passed 129. Two disposable-Codex wire/replay cases passed, including
a failed correction patch followed by recovery. These tests preserve inventories,
raw receipts, exact reference decisions and offline replay. Initial-duplicate
repair is established offline; the final live run did not exercise an initial
candidate duplicate and is not claimed as live proof of that path.

## R15 finding 2 — Actionable diagnostics and bounded corrections

Unknown-endpoint feedback names the link, relation field, missing IDs, valid
candidate IDs and existing immutable IDs. Relation failures include the allowed
relation-by-kind table and endpoint-kind restrictions. The correction request
also lists **every** candidate item carrying a field forbidden for its kind,
including the item ID, actual references and permitted fields. The runtime still
rejects invalid relations; it never guesses an endpoint or changes source text.

The first live retest showed that a table without the complete offending-ID list
was insufficient: many non-qualification nodes retained `applies_to`. A new test
reproduced the missing diagnostic list before that addition. The final focused
suite passed **30 tests**. The final live retest used the complete list; it still
failed, as detailed below. Both attempts remain retained; neither is erased or
relabelled as success.

Codex defaults to **three targeted corrections per range**, configurable through
`extraction_targeted_corrections` from 0 through 3; extraction-full already pins
three. Paper-wide continuation, context and token limits remain active. A
candidate that cannot safely merge may stop before using all three attempts.
Reconciliation keeps its existing single best-effort pass. Model-call accounting,
isolation, tool rejection, API opt-in and the committed Codex defaults are
unchanged. Diagnostic work on a valid link avoids repeatedly serializing the
whole inventory. No dedicated lint/typecheck gate is configured.

Seven new production mutation controls cover initial repair, unresolved-reference
refusal, endpoint inventory, full relation inventory, relation table, the Codex
three-correction default and failed wire-patch normalization. Two existing control
anchors were updated for the equivalent endpoint and patch-ambiguity guards.
All nine focused mutations failed behaviorally and passed after restoration.

## R15 finding 3 — Live compatibility, isolation and accounting

Both native extraction preflights accepted **6/6 distinct wire schemas**, with
an isolation canary each. The final preflight is in
`runs/omega-round15-preflight-final`; the earlier one remains in
`runs/omega-round15-preflight`. The first paper retest is in
`runs/omega-round15-extract`; the final fresh retest is in
`runs/omega-round15-retest`. Neither retest resumed old evidence.

Across both preflights and both paper attempts, **34 Codex calls** used
**517,422 tokens** and **783.44 seconds** summed native call time. This includes
four canaries. The first paper attempt used 13 calls / 289,894 tokens; the final
paper attempt used 7 calls / 160,767 tokens. The final preflight used 7 calls /
33,201 tokens. API spend was zero; subscription usage is disclosed as tokens,
not an invented API-dollar equivalent.

Requested model: **gpt-6-luna**, high effort, pinned CLI **0.163.0**. Served identity
remains **unverified** on every receipt. The canaries retained enforced isolation
and tool-event rejection; generic visible definitions remain disclosed under the
Round-12 rule. Credentials came from the separate configured ChatGPT file through
fresh read-only per-call access. No credential copy, log, refresh or rotation
occurred. The live harness refused API and Claude provider construction.

The live configuration retained the 200,000-token context bound, 24,000 requested
output reservation (48,000 context allowance), 1,200 planned output tokens/page,
4,000,000 run-token cap and 24 paper continuations. Each range allows at most
three corrections. Local token estimates and CLI output reservations remain
soft assumptions; no hard output-token limit or verified serving identity is
claimed. OCR was off for the same source PDFs used in Round 14.

## R15 finding 4 — Retest failed; bridge batch not started

**Final retest: 0/2 accepted. The quality gate failed, so 0/20 bridge papers were
extracted and no bridge run was created.** The native batch's exit 0 means it
completed with disclosed paper failures; it does not mean either graph passed.

For `wright2007`, pages 1–11 produced a rejected initial graph with 59 items and
12 inferences. Fifty-four items carried forbidden `applies_to` relations. The
first correction repeated all 54 invalid items despite receiving the exact
54-entry diagnostic list; later patches did not resolve those retained items.
All three corrections failed. No range was accepted and the remaining pages
were not attempted.

For `rothschild2012`, pages 1–13 produced a rejected initial graph with 54 items
and 16 inferences. The correction received a 31-entry forbidden-field list, then
returned 64 patch items with an ambiguous referenced duplicate ID. The existing
patch-ambiguity guard refused to guess the intended referent. No range or paper
was accepted. Patch counts are not cumulative accepted graph inventories.

The comparison uses the same pinned accepted Opus artifact as Round 14:
`/home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt`.
Lineage, outcomes and PDF hashes were verified, and current grounding reproduced
the retained rates. The brief mentions 68 Opus items; this verified Rothschild
artifact contains **71**, disclosed rather than silently substituted. Neither
baseline would change the failed acceptance gate. The historical Opus prompt and
v4 acceptance contract differ from the current run, so this is an operational
comparison with accepted artifacts, not a controlled same-prompt model study.

| Paper/provider | Accepted items | Inferences | Grounded | Grounded inferences | Quarantine | Outcome |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| rothschild2012 / Opus | 71 | 13 | 70 (98.59%) | 12 | 1 (1.41%) | extracted |
| rothschild2012 / Codex | 0 | 0 | N/A | N/A | N/A | failed |
| wright2007 / Opus | 105 | 21 | 88 (83.81%) | 11 | 17 (16.19%) | extracted |
| wright2007 / Codex | 0 | 0 | N/A | N/A | N/A | failed |

Codex never reached grounding; N/A is not a successful zero quarantine rate.
The following rejected-initial inventories are diagnostic only. Wright covers
only its first range, while the Opus inventory covers the paper. Every accepted
Codex item-kind count is zero.

| Kind | Rothschild Opus | Rothschild Codex rejected | Wright Opus | Wright Codex rejected |
| --- | ---: | ---: | ---: | ---: |
| premise | 28 | 26 | 38 | 20 |
| intermediate_conclusion | 10 | 3 | 21 | 0 |
| inference | 13 | 16 | 21 | 12 |
| reported_view | 6 | 4 | 12 | 8 |
| attacked_view | 6 | 3 | 2 | 0 |
| qualification | 6 | 2 | 8 | 2 |
| conclusion | 2 | 0 | 2 | 14 |
| distinction | 0 | 0 | 1 | 3 |

The operational gate was declared before the final retest: both papers extracted,
item and inference counts within ±25% of the verified Opus baseline, grounding
no more than five percentage points lower and quarantine no more than five
points higher. All checks fail with no accepted graph. No validation, counting
threshold or source text was changed to obtain acceptance. No further live retry
was run after the final gate failure.

The bridge manifest has since grown from 20 to 28 downloaded records. Its
`initial_eps2_counts` and selection groups identify the requested original 20:
17 `ranked_bridge` and three `original_missing`; the eight `l3_followup` records
are later additions. `bridge-disposition.json` retains a manifest hash and a
per-paper `not_run_quality_gate_failed` status for all original 20. There is no
`runs/codex-extract-bridge/` from this work. Improving live model compliance remains
future work; deterministic structural repair does not establish semantic fidelity.

## R15 finding 5 — Verification and local handoff

Full pytest passed **1,314 tests, 4 skipped / 1,318 collected** in
**1,561.50 seconds** (1,562.76 including startup), exit 0. The four skips are
two opt-in paid-provider checks and two opt-in installed OCR/VL-weight checks;
`ARA_LIVE_TEST=0` and `UV_OFFLINE=1` were set.

The full original control runner then completed **579/579 mutations**, each
exiting 1 and each restoration exiting 0, in **3,709.51 seconds**, runner exit 0.
This was one uninterrupted control run, after full pytest and after all live
work had finished. The seven new controls and two adjusted guards were inspected
for behavioral failures, with no syntax/import-error substitutes. All 579 ordered
receipts and their unique names were verified. No source edits or other tests
ran during mutations. Source hashes matched after both gates.

Final local revision: **ece4c07fc1a14e4064e56d7116472297ff010863**, branch
`feat/codex-extraction`, direct parent **c774e94a277703556d95f2722c5fa7a4055e090a** as requested.
The tree is clean. All **234 committed file contents** match the frozen tested
snapshot; symlink targets were checked separately. `git diff --check` passed.
Changes were committed locally; **no push** occurred.

Inline inspection covered duplicate preservation/ambiguity, cumulative correction
merge, precise diagnostics, correction bounds, Codex null recovery, offline
salvage and acceptance identity. No independent review is claimed under the
original no-delegation instruction. No separate lint/typecheck gate is configured.
The requested structural changes and gated quality evaluation are complete;
the conditional bridge batch was not authorized by its failed quality gate.
The unresolved operational limit is inadequate live extraction compliance,
not a claimed successful paper extraction.

Evidence is retained in
`/home/dev/ara-work/reports/omega-evidence/round15/`: source snapshots, full gate
logs, final mutation transcripts, live configurations/statuses, both comparisons,
quality-gate results, per-paper bridge dispositions and numeric usage. Real paper
content remains outside committed source or in ignored native run directories.


Finding placement: content-preserving repairs, ambiguity and version/replay limits
are in R15 finding 1; complete diagnostics, bounded corrections and regressions in
finding 2; live accounting, isolation and model/context limits in finding 3;
failed acceptance, quality comparison, baseline discrepancy and conditional bridge
scope in finding 4; exact revision, full verification and handoff in finding 5.
Earlier 56 findings remain in their original sections.

61 findings, 61 placed.

DONE omega round15 head=ece4c07fc1a14e4064e56d7116472297ff010863 tests=1314/1318 negctl=pass retest=0/2 bridge_extracted=0/20 run=none


# Round 16 — Bounded deletion after correction exhaustion

## R16 finding 1 — Deletion-only terminal repair

From ece4c07, targeted range correction now considers the final cumulative
candidate after the configured correction budget is exhausted, including a zero
budget. It removes only invalid relation endpoints: fields forbidden for the
source node's kind, absent endpoints, and inference endpoints with an invalid
target kind. `applies_to` remains valid on distinction/qualification nodes.
No item is added, removed or rewritten by this operation. Text, attribution,
page citations and inference origins remain unchanged. Existing initial-ID and
wire normalizations remain separate and logged; unresolved duplicate meanings
still refuse. Model corrections retain their existing explicit patch semantics.
Reconciliation remains its existing single best-effort pass.

One populated endpoint is one edge, including each array entry and a scalar
conclusion. The denominator is the final candidate before pruning; empty fields
do not inflate it, and an edge with multiple defects counts only once. The limit
is inclusive: exactly 25% may pass, more than 25% refuses. Missing the sole
premise or conclusion still invalidates an inference; its item is never dropped
or supplied with invented endpoints. The repaired range must retain at least one
valid inference and pass the full local schema and graph checks. Native citation,
grounding, quarantine and publication paths remain in effect. This does not prove
semantic fidelity or completeness.

## R16 finding 2 — Durable disclosure and offline verification

Every deletion records `invalid_relation_dropped` or `dangling_link_dropped`
with item ID, field and original endpoint. `extraction_structure_repaired`
records range, counts, share, correction budget, policy and accepted/rejected
status. An accepted repair retains before/after candidates. Original MODEL
responses remain rejected and fully accounted; no synthetic accepted MODEL event
or additional usage is created.

Methodology exposes per-paper totals and per-range counts/status, including
rejected repair attempts. These are attempt counts, not deduplicated published
edges across resumed histories. Offline salvage recomputes deletions and verifies
candidate hash, before/after equality, counts, policy, the 25% bound and inference
presence before running the native validator. Acceptance advances to v8 and the
repair policy is `terminal-edge-pruning-v1`; v6/v7 outcomes are not automatically
reused. Previously reviewed v4/v5 migration retains its full validation path.

## R16 finding 3 — Live gate failed; bridge batch not dispatched

**Retest: 0/2 papers accepted. Bridge extraction: 0/28, run=none.**
The Round-16 gate was both native paper outcomes `extracted`; no extra Round-15
comparison threshold was imposed. The native retest command completed with exit
0, which discloses completed partial/failed outcomes and does not mean success.

| Paper | Native outcome | Retained items / inferences | Grounded items / inferences | Terminal removals |
| --- | --- | ---: | ---: | --- |
| wright2007 | partial | 65 / 15 | 62 / 14 | 47/108, 43.52%; rejected |
| rothschild2012 | failed | 0 / 0 | N/A | 62/143, 43.36%; rejected |

Wright's pages 1–11 passed after three model corrections without pruning. Its
pages 12–22 reached terminal pruning after three corrections and exceeded 25%,
so they remain unextracted. Grounding retained 62 of the 65 first-range items
(95.38%) and quarantined three (4.62%); one inference is quarantined. These are
partial-paper counts, not a full accepted paper. Rothschild's pages 1–13 exceeded
the repair limit after three corrections; it never reached grounding. Its zero
accepted inventory is not a successful zero-quarantine rate.

Both live removal attempts were rejected. The <=25% acceptance path is proven
by offline regressions, not claimed as a successful live repair. No extra retry
or threshold relaxation followed the failed gate. All 28 placed PDFs in the
current bridge manifest were verified and hashed; their per-paper dispositions
are `not_run_retest_gate_failed`. No bridge run or bridge literature artifact was
created. The native retest retains its partial literature artifact and full
methodology in `runs/omega-round16-retest/`.

Live extraction preflight passed 6/6 schemas in `runs/omega-round16-preflight`.
Across preflight and retest: 20 Codex calls, 376,966 tokens (292,097 input,
81,541 output, 3,328 cache-read), 622.39 seconds summed call time, and zero API
USD. The two canaries proved enforced isolation, zero tool events and active
tool-event rejection; visible generic tool definitions remain disclosed under
Round 12. Requested model gpt-6-luna, pinned CLI 0.163.0; served identity remains
unverified. Codex remains the committed default. No API/Claude calls, credential
copy/log/refresh/rotation, delegation, or push occurred.

## R16 finding 4 — Verification and local handoff

Proof-first regressions: six failed and seven passed before implementation.
The first focused suite passed 46 tests, and broader coverage passed 138.
Nineteen new regressions cover the inclusive boundary, selective deletion,
content/citation preservation, final cumulative patches, unchanged acceptance
checks, per-paper methodology and offline replay/tamper refusal. Eight new
production mutation controls cover dispatch, share, inference presence, dangling
links, input preservation, removal receipts, methodology and replay. One existing
recovery-control anchor was narrowed after the terminal branch changed. All nine
focused mutations failed behaviorally and passed after restoration.

The initial full pytest found one obsolete assertion: a model patch that
explicitly discards a rejected item previously had to fail when its remaining
inference referenced that ID. Round 16 now permits removing that dangling edge
when a valid premise remains (1/9 edges removed). The updated regression retains
the immutable-item discard refusal and asserts the exact remaining graph and
repair receipt. The grounding file then passed 16/16. No production code changed
in response. The final full pytest rerun uses the updated test snapshot.

Final full pytest: **1,333 passed, 4 skipped / 1,337 collected**, zero failures
or errors. The final rerun used four disjoint whole-file shards in isolated
checkouts, **661.07 seconds** elapsed; every shard's source
hashes matched the final snapshot. Skips were the two opt-in paid-provider cases
and two installed local OCR/VL-weight cases. ARA_LIVE_TEST=0 and UV_OFFLINE=1.

Full controls: **587/587 unique mutations detected, every restoration green**.
The unchanged runner main function executed four disjoint CASES slices on
isolated source copies in **1948.63 seconds** elapsed.
Coverage was reconciled against every ordered committed control name; none was
omitted or duplicated in the aggregate. The earlier single-runner attempt was
intentionally interrupted when switching to parallel scheduling (exit 130), with
source restoration verified; that superseded receipt is retained separately.

The control snapshots share identical production code with the final revision.
The only subsequent source difference was the updated non-control grounding
regression above. AST comparison confirmed the nine control-target functions in
that module were unchanged; all nine controls nevertheless reran on the final
snapshot, red and restored green, in **52.94 seconds**.
All 587 final red/green transcripts are retained, and the eight new plus one
adjusted control failures were inspected for behavioral failures rather than
syntax/import-error substitutes. No mutation touched the canonical live/pytest
checkout. Gates used local processes, not delegated agent contexts.

Final revision: **f7067a150abfbe39b606cb95e4a21a5a2e2e602d**, branch `feat/codex-extraction`, direct parent
**ece4c07fc1a14e4064e56d7116472297ff010863** as requested. All **235 committed
file contents** match the final tested snapshot; the AGENTS.md symlink object
and target were checked separately. The canonical tree is clean and
`git diff --check HEAD^ HEAD` passed. Changes are committed locally; **no push**.


Inline inspection covered native correction, accounting, salvage, publication
and methodology paths. No independent review is claimed. No separate lint/typecheck
gate is configured. No new successful whole-paper extraction, semantic-fidelity
claim or verified serving identity follows from this change.

Evidence: `/home/dev/ara-work/reports/omega-evidence/round16/`, including source
snapshots, red/green regressions, mutation receipts, full pytest, live usage,
per-paper outcomes, pinned bridge inventory and skipped-paper dispositions.
Real source content remains in ignored native run directories and external
receipts; committed fixtures remain placeholders.

Finding placement: deletion semantics and denominator in R16 finding 1;
acceptance version, replay and disclosure in finding 2; failed live acceptance,
partial inventories, skipped batch, model/isolation/accounting limits in finding
3; exact revision and verification scope in finding 4. Earlier 61 findings remain
in their original sections.

65 findings, 65 placed.

DONE omega round16 head=f7067a150abfbe39b606cb95e4a21a5a2e2e602d tests=1333/1337 negctl=pass retest=0/2 bridge_extracted=0/28 run=none
