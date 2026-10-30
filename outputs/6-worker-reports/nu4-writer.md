# nu4 — sectioned essay writer

Implementation, live length proof, full offline verification and the local commit are complete. The real draft reached **4,642 words**, then its native audit **failed** on four numbered sentences. It is an unverified draft, with no final export.

## Behavior and scope

Worktree: `/home/dev/ara-work/nu4`; branch: `fix/writer-length`; requested base: `9b9999730c32b4dd0f06ef80a075920633d1acc9`. Final commit: `c7ae7f53dae52afb607b2b5ae4f06fb6c7d50a5d`. The working tree is clean and all 235 committed source files match the tested snapshot. No push or delegation. Non-author review follows this handoff.

Competition-length requests (`essay_min_words >= 4500`) now produce a logged, schema-checked 4–10-section outline with budgets totalling 4,800–5,600 words. Each section goes through the existing logged, cached and budgeted model boundary. Inputs contain the content graph, exact frozen supporting commitments and attributed source text/page citations, CQ answers, disclosed omissions, bounded nearby source items and retained sections. Available paper gaps/resolutions are carried as context; no route framing is invented.

Assembly is deterministic. Short drafts receive at most three targeted expansion rounds, starting with the largest section deficits. Expansion returns additional paragraphs and appends them to the accepted body verbatim. Overlong drafts receive targeted condensation. Each section remains bounded at 1,800 words / 24,000 body characters; required evidence is bounded at 80,000 canonical characters and refuses explicitly if it cannot fit. Nearby items are limited to six / 12,000 characters per support and remain context, not additional T premises. Short smoke requests retain their small whole-essay path.

The final word/coverage/body checks, native audit, citation/originality verification, re-audit and transport isolation/output scans remain in place. Exact T citation IDs and bibliography entries are checked before accepting a section; semantic fidelity remains model-assessed. Partial sections and rejected drafts are never treated as a final essay.

An initial experiment using whole-section replacement still ended at 3,213 words after all three rounds. Its failed native execution is retained. That observation led to append-only expansion; the preservation regression was observed failing against replacement behavior before the change.

## Executed verification

- `uv sync --locked`: passed with Python 3.13.7 and the committed lockfile.
- Final focused sectioned-writer and native subprocess replay: **12 passed**. Other scoped checks included the existing writer/audit/CLI consumers and **50 Codex transport/preflight tests**.
- Final `uv run --locked pytest -q`: **1,292 passed, 4 skipped**, 1,296 collected, 1,467.58 seconds. The four skips are the existing opt-in provider/OCR tests.
- `UV_OFFLINE=1 uv run --locked python tests/integration/negative_controls.py`: **571/571 controls passed**, exit 0. Every mutation returned 1 and every restored check returned 0. It ran sequentially after pytest and live generation, with no concurrent checkout writer. The earlier 568-case estimate was corrected to the completed runner’s 571 unique cases.
- Fresh native Codex schema preflight: **17/17 cases passed**, including the new outline schema. Its 19 model receipts include two isolation canaries.
- Full-suite discovery exposed stale finite smoke prompt hashes and hardcoded 16-schema expectations. Both were repaired; canned response payloads stayed unchanged. Interrupted/discovery logs are retained separately from the final green full-suite result.

The fake-provider coverage exercises deterministic order/assembly, retained prose, largest-deficit expansion, condensation, three-round exhaustion, plan budgets, exact source context, citation rejection and adverse-audit stopping. Eight added production-wire controls cover plan budgets, assembly, expansion, append preservation, the round bound, source citations, source context and the audit gate.

Proof files: [full pytest](/home/dev/ara-work/nu4/runs/nu4-proof/pytest-full.txt), [focused tests](/home/dev/ara-work/nu4/runs/nu4-proof/append-final-focused.txt), [initial regression failures](/home/dev/ara-work/reports/nu4-red.txt), [append regression failure](/home/dev/ara-work/nu4/runs/nu4-proof/append-red.txt), [mutation log](/home/dev/ara-work/nu4/runs/nu4-proof/negative-controls.txt), [mutation results](/home/dev/ara-work/nu4/runs/nu4-proof/round2/round1-control-results.json), [tested source manifest](/home/dev/ara-work/nu4/runs/nu4-proof/source-tested.json).

## Live result and audit — F1

The authorized route was `9a35a6febc9d:r0`. Native `ara select` ran against an independent, hash-verified copy of `/home/dev/ara-scaffold/runs/codex-fork-3`, exposed at `/home/dev/ara-work/nu4/runs/nu4-live`. All **89 original file hashes remain unchanged**. The original log/anchor prefixes and all three frozen artifacts also match their original hashes ([receipt](/home/dev/ara-work/nu4/runs/nu4-proof/copied-prefix-integrity.json)). The copied chain and anchor verify through **8,333 events**, retaining the original 8,108-event prefix and both experimental/final attempts.

The final implementation used five 1,000-word section budgets, five initial section calls and six append calls across two rounds. All five initial section bodies remain exact prefixes of the final bodies. The final section counts are 905, 886, 940, 1,008 and 898; the title adds five words. The first expansion round reached 4,495 words; one further addition reached **4,642**.

| Count/check | Observed result |
| --- | --- |
| Native title + body, bibliography excluded | **4,642 words** |
| After removing node markers | 4,591 words |
| After removing node and citation markers | 4,506 words |
| Audit sentences | 292 |
| Covered nodes | n0, n1, n2 |
| Missing nodes | None |
| Extra-step flags | **8, 10, 251, 279** |
| Faithful verdict | **False** |
| Native select exit | 2, `essay audit failed` |
| Originality/citations, evidence retrieval, re-audit | Not reached |
| Final draft/export | None |

The audit schema returns boolean flags, not explanations. The raw prose places some citations after terminal punctuation; the existing splitter can attach those markers to the following numbered segment. This is visible around the flagged sentences and makes raw-text review necessary before adjudicating each flag. The adverse verdict remains binding; no audit bypass or citation-boundary repair was applied in this length task.

The writer and auditor received identical source evidence: **11,469 canonical characters**, two exact frozen supporting commitments, and six neighboring items per support. Exact provenance equality and retained prose were checked against the native artifacts.

Final-attempt accounting: 14 model receipts, including one cached outline; 158,760 input tokens, 17,664 provider cache-read tokens and 21,557 output tokens. Both live attempts together used 36 receipts, 430,403 input + 38,272 cache-read + 48,022 output tokens. Preflight accounting is separate in the linked detail file. All live calls used `codex_cli`, requested `gpt-6-luna`, with no Claude/API provider or server-tool use. Recorded API USD is zero; subscription price equivalence is unavailable. Served-model identity remains unverified (F4).

Review artifacts: [unverified essay text](/home/dev/ara-work/nu4/runs/nu4-proof/essay.unverified.txt), [exact draft JSON](/home/dev/ara-work/nu4/runs/nu4-proof/essay.unverified.json), [flagged sentences](/home/dev/ara-work/nu4/runs/nu4-proof/audit-flagged-sentences.json), [live result](/home/dev/ara-work/nu4/runs/nu4-proof/live-result.json), [accounting and preservation proof](/home/dev/ara-work/nu4/runs/nu4-proof/live-detail.json).

## Remaining limits — F2–F6

- **F2 — Downstream completion is unproved.** Citation/originality checks and re-audit did not run because the first audit failed. Codex still refuses API-only `search_evidence`; that restriction remains unchanged and was not exercised in this run. No paid API/Claude fallback was introduced.
- **F3 — Route quality is unchanged.** This route uses supports from one paper. The prior omitted-support, universal-necessity and novelty/cross-paper limitations remain; see [fork-3 review](/home/dev/ara-work/reports/zeta-fork3.md) and [prior writing report](/home/dev/ara-work/reports/zeta-writing-test.md). Length does not repair those limits or establish acceptable-pilot coverage.
- **F4 — Serving identity is unverified.** The requested model and Codex transport are recorded; the CLI receipts do not independently establish which model served the calls.
- **F5 — This is bounded, single-route evidence.** The final append implementation reached length on one real route. The earlier replacement experiment failed at 3,213 words. Three rounds and section/context caps remain hard stops; no universal length or semantic-quality guarantee is claimed.
- **F6 — Existing export reuse risk remains.** The earlier zeta report identifies a stale-export risk when a failed selection follows a successful one in the same run. This task does not change that behavior. It was not exercised here: neither source nor copy has a final draft, and the delivered essay is explicitly unverified.

## Artifacts and handoff

Generated essays, logs, cache and source material remain ignored and uncommitted. The working live copy is on tmpfs because disk was tight, but the completed run is retained durably in [live-run.tar.gz](/home/dev/ara-work/nu4/runs/nu4-proof/live-run.tar.gz): 170,927,025 bytes, 132 readable archive entries, SHA-256 `c331ca8ab9baedd4719ce3197474537a4fe72bc856d7f60dc90e9725999be01d`. [Copy manifest](/home/dev/ara-work/nu4/runs/nu4-proof/copy-manifest.json) and [archive receipt](/home/dev/ara-work/nu4/runs/nu4-proof/live-archive.json) preserve integrity details. [Full new-event slice](/home/dev/ara-work/nu4/runs/nu4-proof/live-events.json) is a convenience view; authenticate it against the full archived chain and anchor. The failed first experiment's section artifact and console are in [attempt1](/home/dev/ara-work/nu4/runs/nu4-proof/attempt1/).

No submission-ready essay or completed citation/originality verification is claimed. The 17 owned files are committed locally; the working tree is clean. All 235 source hashes match both the pre-control and tested manifests, and the committed blobs match the tested snapshot. `git diff --check` passed. See the [final verification receipt](/home/dev/ara-work/nu4/runs/nu4-proof/final-verification.json). Next: caller-owned non-author review of the implementation and raw draft/audit flags. No push.

Finding placement: F1 → “Live result and audit”; F2–F6 → “Remaining limits”, with F4 also in live accounting and F5's failed experiment in “Behavior and scope”. **6 findings, 6 placed.**

DONE nu4 head=c7ae7f53dae52afb607b2b5ae4f06fb6c7d50a5d tests=1292/1296 negctl=pass live_words=4642 audit=fail essay=/home/dev/ara-work/nu4/runs/nu4-proof/essay.unverified.txt

## Round 2

The saved essay passed the native audit after two targeted revision rounds: **4,604 words, zero flags, all three route nodes covered**. It then stopped at `search_evidence`, before reservation or dispatch, with `stage_requires_api_provider`. Citation/originality classification and the final post-verification audit remain unexecuted. No paid API or Claude model ran; there is no final export.

Round 2 base: `c7ae7f53dae52afb607b2b5ae4f06fb6c7d50a5d`; local commit: `89be37a1074e87b34fc2b79dca0e2208020c8cda`. Full offline verification and the local commit are complete; the working tree is clean. No push or delegation; non-author review remains caller-owned.

### Behavior and native integration

The deterministic splitter now associates citation markers immediately after terminal punctuation with the preceding sentence, including across transparent node markers. It preserves the original draft bytes and exposes their sentence spans for targeted replacement. The audit prompt and its semantic checks were not loosened.

A complete adverse audit retains its exact inputs and labels. Each repair call receives those inputs, the flagged labels, the original flagged spans and immutable bibliography. Runtime requires exactly those sentence IDs, preserves citation/node marker sequences for retained text, and applies replacements by original offsets. Empty text can cut a whole unsupported sentence. All unflagged bytes remain untouched. Each replacement is bounded at 8,000 characters and at the greater of 1,000 or twice its original length; schema, body, word-count and node-coverage checks still apply. At most two accepted repair rounds are followed by full audits. Malformed inventories, transport failures and missing-node failures without flagged sentences do not authorize repairs. The post-citation re-audit remains final.

`ara select --draft PATH` resumes an existing unverified draft through the native selection/composition path, logging and validating it without new outlining or whole-essay writing. The new `revise_essay` kind uses writing-stage routing and the existing logging, cache, budget and isolation boundary.

### Live evidence and F1 disposition

Native command:

```sh
uv run --locked ara select --run-dir runs/nu4-live --route 9a35a6febc9d:r0 \
  --draft runs/nu4-proof/essay.unverified.json \
  --codex-schema-preflight-log /home/dev/ara-work/nu4/runs/nu4-round2-preflight/events.jsonl \
  --unknown-usage-policy count-at-reservation
```

The initial input was byte-identical to the round 1 draft. No outline or writer call ran.

| Audit | Words | Numbered sentences | Extra-step flags | Missing nodes |
| --- | ---: | ---: | ---: | --- |
| Existing draft, corrected splitter | 4,642 | 244 | 121 | None |
| After repair round 1 | 4,605 | 245 | 1 | None |
| After repair round 2 | **4,604** | 245 | **0** | None |

**F8 — Counting margin:** removing node markers leaves **4,553 words**; removing both node and citation markers leaves **4,468**. The unchanged native counter includes markers. A stricter 4,500-word count that excludes both marker types is therefore not satisfied, and competition compliance under that counting rule is unproved. No post-audit padding or additional revision round was applied.

Round 1's repair required three model responses: candidates of 4,233 and 4,271 words were rejected by the unchanged minimum-length check; the normal bounded validation correction accepted the third at 4,605. Round 2 required one response. Thus there were two accepted repair rounds and four repair responses, with every rejected response retained and accounted. Reconstructing the accepted replacements from the logged flagged spans reproduces the final artifact exactly; all unflagged bytes, bibliography entries and auditor evidence were preserved.

The prior four-flag audit is superseded for this revised artifact. Fixing the splitter alone did not make the original essay pass: the next audit flagged 121 sentences. Audit judgments remain model-based; this run does not isolate the causal contribution of sentence boundaries versus model variation. A passed audit is not citation/originality verification or proof of the route's philosophical quality.

Eight actual subscription responses: one isolation canary, three audits and four revision responses. Recorded usage: 143,996 input tokens, 5,888 cache-read tokens, 35,228 output tokens, zero server-tool uses. All actual responses are `codex_cli`, requested `gpt-6-luna`; serving identity remains unverified. Preflight is separate and passed **18/18 cases**. Subscription dollar equivalence is unavailable; paid API calls in this round are zero.

Artifacts: [latest unverified essay](/home/dev/ara-work/nu4/runs/nu4-proof/round2/essay.unverified.txt), [exact JSON](/home/dev/ara-work/nu4/runs/nu4-proof/round2/essay.unverified.json), [live result, patch accounting and hashes](/home/dev/ara-work/nu4/runs/nu4-proof/round2/live-result.json), [56-event native suffix](/home/dev/ara-work/nu4/runs/nu4-proof/round2/events.suffix.jsonl), [suffix anchor](/home/dev/ara-work/nu4/runs/nu4-proof/round2/events.suffix.anchor), [native console](/home/dev/ara-work/nu4/runs/nu4-proof/round2/live-console.txt).

### Exact blocker and unexecuted API alternative — F2

The native exit was **2**. `ModelCalls.count_request` invokes the Codex estimator for `search_evidence`; its inherited subscription estimator refuses this API-only kind. This happened before reservation and dispatch: no `search_evidence` call-start or response receipt exists. The retrieval stage did not run, so `verify_originality_citations` and the subsequent re-audit were never reached. The failed retrieval has a rejection receipt, not a successful model response.

There is **no currently implemented API alternative that satisfies the no-Claude constraint**. The repository's only retrieval-capable API adapter is Anthropic/Claude, and provider switching is limited to construction stages. A per-kind `search_evidence.provider` setting cannot supply a different adapter here.

The smallest non-Claude alternative would add a retrieval adapter and route only `search_evidence` to it: **one API request**, then **two Codex calls** for citation/originality classification and re-audit. This adapter/routing work is not implemented or exercised. The existing native API completion path would require three remaining model calls through the Anthropic adapter and would violate the present no-Claude constraint; it was not run.

For the final draft's two citations and two quoted passages, the exact search prompt is 35,038 UTF-8 bytes. An offline planning estimate uses bytes/4, or **8,760 initial input tokens**. An illustrative one-search-cycle forecast is **33,520 API tokens**: two prompt presentations, 8,000 retrieved-context tokens and 8,000 generated-evidence tokens. This is not a provider token count or measured cost; reasoning, tool overhead, extra search cycles and unsuccessful evidence retrieval can change it. The two later Codex calls are additional subscription usage and excluded from that API estimate. One API request is a minimum call-count scenario, not a guarantee of adequate retrieval or successful verification.

The current configuration is much more conservative: five potential tool uses, 200,000 input tokens reserved per use and 64,000 output tokens per iteration yield an approximate **1,392,760-token reservation** using the same initial-input estimate. That is an admission reservation, not expected consumption or a hard tokenizer bound. No paid counter, generation or retrieval was invoked to obtain these figures. [Estimate inputs and assumptions](/home/dev/ara-work/nu4/runs/nu4-proof/round2/api-estimate.json).

### Verification and preservation

- Before implementation, the new regression run had **12 failures, 2 passes**: three failures reproduced citation misattachment, and nine exercised the then-absent revision module.
- Targeted verification passed: **34** splitter/revision/audit-outline tests, **68** native/writer/schema consumers, **83** transport/audit/revision tests, and two additional no-repair boundary cases. These overlap and are not summed as a suite total.
- `uv run --locked pytest -q --basetemp /dev/shm/ara-nu4-r2-pytest`: **1,312 passed, 4 existing opt-in skips; 1,316 collected; 1,290.42 seconds; exit 0**. Log: [pytest-full.txt](/home/dev/ara-work/nu4/runs/nu4-proof/round2/pytest-full.txt).
- `UV_OFFLINE=1 uv run --locked python tests/integration/negative_controls.py`: **581/581 passed, exit 0; every mutation returned 1 and every restored check returned 0**. Ten new controls cover citation ownership, the repair bound, flagged-only edits, exact citations/markers, surrounding bytes, auditor evidence, length, re-audit and native draft resume.
- Final restoration/commit check: **all 239 files match both pre-control and full-test snapshots, and every committed blob matches the tested snapshot; `git diff --check` passed**. The stable source manifest covers 239 files.

Receipts: [final source/commit verification](/home/dev/ara-work/nu4/runs/nu4-proof/round2/final-verification.json), [control results](/home/dev/ara-work/nu4/runs/nu4-proof/round2/control-results.json), [control console](/home/dev/ara-work/nu4/runs/nu4-proof/round2/negative-controls.txt), [complete archived control logs](/home/dev/ara-work/nu4/runs/nu4-proof/round2/controls.tar.gz).

All **89 original-run file hashes remain unchanged**. The round 1 copied-log prefix and anchor match the durable archive byte-for-byte; all three frozen artifacts are unchanged. The complete copied chain and anchor verify through **8,389 events**, including the 56-event round 2 suffix. [Integrity receipt](/home/dev/ara-work/nu4/runs/nu4-proof/round2/integrity.json). The durable round 1 archive plus the linked suffix and anchor preserve this round's complete history without another full run copy.

The obsolete temporary export copy was removed only after verifying its retained archive, reclaiming 390,866,265 bytes on tmpfs. Full-suite temporary files are on tmpfs to avoid additional disk pressure. The native failed selection regenerated its methodology export; the unverified essay remains distinct from final export. [Cleanup receipt](/home/dev/ara-work/nu4/runs/nu4-proof/round2/cleanup.json). Round 1 control evidence is preserved in [archived logs](/home/dev/ara-work/nu4/runs/nu4-proof/round2/round1-controls.tar.gz) and [571-case results](/home/dev/ara-work/nu4/runs/nu4-proof/round2/round1-control-results.json).

### Remaining findings and handoff — F3–F8

F3's single-paper, omitted-support, necessity and novelty limitations remain unchanged. F4's serving identity remains unverified. F5 remains bounded, single-route evidence; the audit-label variation is recorded above without attributing it solely to the splitter. F6's pre-existing stale-export risk remains unchanged and unexercised: this copy still has no final draft or essay export.

**F7 — Refusal diagnostic provider label is misleading.** The refusal's diagnostic says `claude_code` because `CodexCLIProvider.estimate` inherits `ClaudeCodeProvider.estimate`, which raises the generic subscription error. It does not indicate a Claude invocation. Every actual response receipt in this round says `codex_cli`; there are no Claude/API responses. This diagnostic-label defect was not changed as part of audit repair.

**F8 — Stricter word count remains below 4,500.** The passed audit and native 4,604-word count do not establish compliance when all machine markers are excluded: that count is 4,468. This is a review/action item before treating the draft as competition-ready.

Next: caller-owned non-author review of the implementation and revised essay, including the stricter word-count issue. Any API-backed completion requires separate implementation and authorization; none is implied or requested here.

Finding placement: F1 disposition → “Live evidence and F1 disposition”; F2 → “Exact blocker and unexecuted API alternative”; F3–F8 → “Remaining findings and handoff”, with F4/F5/F8 also in live evidence. **8 findings, 8 placed**; F1's old adverse verdict is superseded for the revised artifact.

DONE nu4 round2 head=89be37a1074e87b34fc2b79dca0e2208020c8cda audit=pass flags_left=0 words=4604 blocked_at=search_evidence api_estimate=1/33520

## Round 3 — default Codex web evidence and kappa4 W1

Local commit `9dfedc5e0ea1073ae42344ff3606d96b918434c3` on `fix/writer-length`; working tree clean.
All 241 working files and committed blobs match the final tested snapshot.
The requested live lifecycle is **blocked**, and there is **no final draft or essay export**.
Codex is the default evidence-retrieval path when the main provider is `codex_cli`;
there is no API fallback. The operator declined API credit. No paid API or Claude
model was called, no worker was spawned, and nothing was pushed.

### Imported-draft boundary — W1 fixed

**F1 (fixed, kappa4-W1).** Imported drafts now pass the effective provider's existing
identity/credential scanner before schema validation, resume logging, artifact
writes or audit dispatch. Identity rejection is `operator_identity_in_output`;
credential rejection retains `credential_in_cli_output`. Validation cannot echo
an unscanned malformed import. The reviewer’s content-sensitive disposable Codex
CLI reproduction is now a regression covering body, title, bibliography and
JSON-encoded content in an invalid extra field. Rejected imports leave the log,
anchor, existing draft artifact and cache unchanged; clean imports still reach
the native audit. The new scan-removal mutation is part of the full runner.

Red proof: eight failures and one clean-resume pass before the fix. After the fix,
the owning regression, audit/revision and native CLI checks passed 23/23. The
original and latest real drafts also pass the actual configured provider scan,
without any model dispatch (`W1-live-draft-scan.json`). Independent re-review of
this fix belongs to the caller; the prior kappa4 review was against round 2.

### Web-only transport and evidence

Only `search_evidence` gets `web_search="live"` and `tools.web_search=true`.
Commands, file tools, connectors, delegation and other tools remain disabled.
The event parser admits only web-search items with search/open-page/find-in-page
actions, plus the usual lifecycle/message items. Every non-web tool or unknown
event rejects. The normal content-free isolation canary, isolated filesystem,
read-only credential mount and output scans remain active.

Accepted evidence retains completed web events, queries, result URLs and quoted
snippets. It enters the existing citation/originality verifier as URL-bound source
records. Exact quotation matching, unverified-item removal and the final audit are
unchanged. Methodology derives its “Codex web search” disclosure from actual
receipts. Tests exercise a real disposable subprocess and native verification,
including retaining an exact quote and removing altered wording.

**F4.** Source URLs and passages in this wire are explicitly **model-reported from
Codex web search**, not independently authenticated raw search-result bodies.
Receipts and methodology preserve this provenance distinction. A plausible
structured answer without a completed web event is rejected.

The configuration follows the [official Codex configuration reference](https://developers.openai.com/codex/config-reference/).
The installed CLI remains pinned to 0.163.0. The evidence stage mounts the vendor companion `codex-code-mode-host` read-only
under `/run`, keeping its host directory hidden; a missing helper refuses. The
exact pending `other` action is allowed before completion, but a completed unknown
action still rejects. The existing 18-case stage-schema
preflight manifest is unchanged; the transport-specific evidence schema was
presented in live probes. The final content-free probe established accepted web
transport, but returned unrelated material and established no useful source evidence.

### Live results and blockers

**F2.** The first two content-free probes and original-draft diagnostic returned
no completed web event (`cli_web_search_missing`). A web-enabled isolation canary
reported `functions.web__run` visible, which alone did not prove execution.

A later isolated diagnostic mounted the installed companion executable and reached
completed search events. Repeating the old transport without that mount again
returned no web event. The helper-mounted stream exposed a real parser mismatch:
searches start with `action: other` before completing as `search`. The pending-event
regression failed before the fix; the missing-helper/mount regressions failed four
tests before their fix. The parser continues to reject unknown completed actions;
a helper confirmation containing such an action was rejected `cli_tool_event`.

The corrected production transport then accepted a content-free search and recorded
two source URLs. Those results were unrelated to the intended documentation and
prove transport execution, not useful evidence or citation verification. The final
original-draft retrieval diagnostic also succeeded, retaining two source URLs and
completed search events. Classification and post-verification audit were not
run outside composition; this result does not establish citation validity or
originality. Diagnostic calls do not authorize
publication or bypass the adverse composition audit. Source-result payloads were
also observed in the CLI stream; this adapter still uses the explicitly disclosed
model-reported final-answer excerpts, not those raw payloads.

**F3.** Native `ara select --draft` re-audited the original draft. Its first audit
prompt was byte-for-byte identical to the final accepted round-2 audit prompt
(SHA-256 `7eec8c77d1b7fe907e61de6566fbc9f8cc20bce092c90bcb077b09eecbbb0750`),
with `gpt-6-luna` requested in both, but this call flagged 101 sentences.
The normal bounded repair lifecycle then produced:

| Stage | Native words | Flags |
| --- | ---: | ---: |
| Imported round-2 draft | 4,604 | 101 |
| Accepted repair 1 | 5,150 | 107 |
| Accepted repair 2 | 5,405 | 126 |

All three audits covered n0/n1/n2 without missing nodes. The two-round bound then
stopped the run with `EssayAuditFailed`; no further repair was attempted. Native
composition never reached evidence retrieval, classification or the final
post-verification audit. The separately executed retrieval diagnostics are reported above; they do not
change this native composition result. The requested final `draft.json` and essay export do not exist.
The native composition attempt preceded the W1 guard and late transport fixes.
Both real drafts subsequently passed the guard, and the corrected transport was
exercised separately by the successful original-draft retrieval diagnostic.
Neither observation changes the adverse native audit or establishes a final export.

### Verification and integrity

Before the late live transport diagnosis, full pytest passed **1,336 tests with
four existing opt-in skips / 1,340 collected**, exit 0, 1,263.02 seconds. All
**592/592** sequential controls failed under mutation and passed after restoration,
with all 241 source hashes restored. These receipts are retained as `prediagnostic-*`.
After the helper and pending-event fixes, the refreshed full suite passed
**1,339 tests with four existing opt-in skips / 1,343 collected**, exit 0,
1,396.25 seconds. The final **594/594** sequential controls all failed under mutation and passed
after restoration, exit 0, 3,941.91 seconds. All 241 source hashes were restored;
`git diff --check` passed. The added helper and pending-action controls passed.
No separate lint/typecheck is configured.
The pre-W1 full run was intentionally interrupted when the blocking review arrived:
566 tests had passed, exit 2. It is not a full-suite verdict. Earlier focused
transport/verification checks passed 86 tests with one existing opt-in skip.
No standalone shipping review, PR or CI run was performed.

All 89 original-run file hashes are unchanged. The copied log prefix and frozen
artifacts are unchanged, and the full copied chain/anchor verifies through 8,431
events. The 42 new native events and final unverified draft are durably retained.
Full test and control transcripts, probe receipts, the audit-prompt comparison,
source manifest and integrity receipt live under
`/home/dev/ara-work/nu4/runs/nu4-proof/round3/`. The prior full archive plus the round
2 and round 3 suffixes preserve the complete native history. No philosophical
content enters the committed tree.

### Remaining limits and finding placement

- **F5 — Serving identity:** all 23 actual responses in this round are Codex
  subscription receipts requesting `gpt-6-luna`; serving identity remains
  unverified. Imported historical API receipts are not new API calls.
- **F6 — Admission limits:** configured search/output allowances reserve tokens;
  the CLI does not enforce a hard per-call search/output cap. Completed web
  events are counted when present, aggregate token receipts retained, and later
  admission can stop. These reservations are not measured API charges.
- **F7 — Word counts:** the original draft is 4,604 native / 4,553 without node
  markers / 4,468 without both node and citation markers. The latest unverified
  draft is 5,405 / 5,354 / 5,269 respectively. Extra length does not overcome its
  failed audit or make either draft submission-ready.
- **F8 — Route quality:** the inherited single-paper route, omitted-support and
  novelty limitations remain. This transport/guard change establishes no new
  synthesis, originality, source fidelity or route-quality improvement.
- **F9 — Existing exports:** stale-export behavior on a run that already has an
  older successful final draft remains unexercised. This copied run had no final
  draft or essay export before or after the attempt.

F1 is placed in “Imported-draft boundary”; F2–F3 in “Live results and blockers”;
F4 in “Web-only transport and evidence”; F5–F9 in “Remaining limits”.
**9 findings, 9 placed.** The unresolved work is resolving the adverse native audit and completing
classification and post-verification audit within the native lifecycle before a
verified export can be produced. An API route is not proposed as a fallback.

DONE nu4 round3 head=9dfedc5e0ea1073ae42344ff3606d96b918434c3 tests=1339/1343 negctl=pass verification=fail final_export=none fixed=kappa4-W1

## Round 4 — typed sentence audit and citation-preserving revision

Committed locally as `d15eb43ef56a01079d9ad453b95ee37be675fa77` on
`fix/writer-length`, from `9dfedc5`. Full tests and all 602 controls passed, and the
checkout is clean. Both essays passed their typed pre-verification audits after
revision, but both native runs and their single retries stopped at evidence
retrieval. **No verified essay export was produced.** All live calls used Codex;
there was no API/Claude fallback, delegation or push.

### Typed audit and root conclusion

The binary extra-inference flag is replaced by eight sentence roles: source claim,
argument step, framing, exposition, signpost, objection, reply and unsupported
claim. Three substantive failure rules apply: unsupported claims fail; source
claims require a positive semantic citation judgment, a real marker and an exact
frozen-T bibliography match; argument steps require a known route mapping.
Presentation roles do not satisfy route coverage. The audit receives the exact
root conclusion and instructions to map faithful restatements to its node.
Additional unsupported content in the same sentence still fails. Complete
sentence inventory, known ids and full route coverage remain mandatory.

Role classification, source fidelity, whether prose adds substance, and whether
an objection/reply is marked and CQ-consistent remain model judgments. The tests
prove deterministic enforcement given those labels, not semantic truth. The live
comparison below records the observed effect on the saved drafts.

### Revision feedback and preserved boundaries

Each flagged sentence carries its exact citation/node marker sequences and typed
failure reason. The reviser is explicitly told not to add even a valid T marker to
a retained sentence. A rejection identifies the sentence and observed/required
sequences; a regression demonstrates recovery after adding the wrong marker.
Three accepted repair rounds are allowed, each followed by a full audit. A whole
unsupported sentence may be deleted only if length and coverage still pass.
Unflagged bytes and bibliography remain unchanged. The W1 import scan still runs
before validation, logging, persistence or auditor dispatch. Final citation/
originality verification and the post-verification audit remain required.

### Live comparison and integrity

The first typed audit returned **75/245 flags on route 1** (all miscited source
claims) and **25/245 on route 2** (24 miscited source claims, one unsupported
claim). Route 1 had 75 source claims without sentence-local citation markers;
route 2 had 23. All exact root-conclusion restatements mapped to n0 and none was
flagged, including route 2 sentence 3 from the prior review. Both audits covered
all nodes.

| Route / stage | Native words | Flags | Outcome |
| --- | ---: | ---: | --- |
| Route 1 imported draft | 4,604 | 75/245 | Revision required |
| Route 1 accepted repair 1 | 4,714 | 0/245 | Audit passed |
| Route 2 imported draft | 4,638 | 25/245 | Revision required |
| Route 2 accepted repair 1 | 4,525 | 74/244 | Revision required |
| Route 2 accepted repair 2 | 4,619 | 0/244 | Audit passed |

Route 1's first repair response and route 2's first response in repair round 2
fell below the minimum and were rejected; the next validator-informed attempts
were accepted. No marker-rule rejection occurred in these live repair attempts.
The offline marker-feedback regression proves that specific repair path. Route
2's second audit had 74 miscited-source flags and no unsupported-claim flags.
No audit in this round flagged an unmapped argument step. Its classifications
shifted substantially between audits; fewer flags are not a
stability guarantee, and a successful model audit is not independent semantic proof.

Both native runs stopped at `search_evidence` with `cli_tool_event`. A diagnostic
on route 1's accepted draft, using the unchanged production parser and transport,
then accepted web-only events and recorded two result URLs. This proves that
retrieval can execute, not that the native publication lifecycle completed.
It did not justify changing the event guard. One native retry per route reused
its logged, accepted audit cache entry, after asserting the rendered audit prompt
was byte-for-byte identical. Both retries again failed at `search_evidence` with
`cli_tool_event`. The sanitized failure receipts do not identify the rejected
event type; they do not prove that any particular non-web tool executed. Isolation
canaries passed on every native invocation. No further retry or guard relaxation
was attempted.

Neither route produced accepted native retrieval evidence, citation/originality
classification, the final post-verification audit, `draft.json`, or an essay
export. **Both overall routes remain failed; exports=0.** Their retained
`draft.unverified.json` artifacts passed their pre-verification typed audits only.

Route 1 starts from the preserved 4,604-word round-2 draft; route 2 starts
from Zeta's preserved 4,638-word draft. Both are resumed without regeneration on
independent verified copies. Route 1 copied 128 files and 8,431 verified events;
route 2 copied 103 files and 8,228 verified events. Only cache locations are
relocated through the native CLI factory and logged, preserving original caches.
The route-1 binary audit had returned zero flags in round 2 and 101 on the same
draft in round 3; route 2's prior binary audit returned 151/245 flags. These are
historical model judgments, not fixed truth labels or a controlled semantic benchmark.

Final integrity checks confirm all **128 route-1 and 103 route-2 original files**
are unchanged. Both copied log prefixes and frozen artifacts are unchanged. The
complete log/anchor chains verify through **8,494 events for route 1** and
**8,303 for route 2**, retaining 63 and 75 new events respectively. Full run
archives were compared file-by-file with the completed copies. Each route has one
logged audit cache replay on retry; native invocations made eight and ten actual
model calls respectively, all requesting `gpt-6-luna` through `codex_cli`.

Durable evidence root: `/home/dev/ara-work/nu4/runs/nu4-proof/round4/`.
Each `route1/` and `route2/` directory contains the original input, audit-passed
retry input, final unverified draft, log suffix, full anchor, `result.json`, and
`run.tar.gz` (the complete native run, including its original prefix). Both full
archives remain on disk rather than only in temporary memory. `live-results.json`
and `audit-counts.json` summarize the outcomes; `web-diagnostic/` retains the
successful diagnostic and sanitized event shapes. The diagnostic is separate
from the native composition receipts and cannot establish publication success.

### Verification

Before implementation, the new typed/revision regression set failed 16 tests.
After implementation, 78 typed-audit/revision/schema checks passed. Native CLI
checks passed 7/7 after updating the two smoke audit payloads and request hashes;
all other canned responses are unchanged. Writer and imported-draft consumers
passed 21/21 after adapting the fake revision response to omit input-only marker
inventories. The initial broader consumer run's five failures were those four
smoke-fixture lookups and one fake response; those owning checks were rerun.
Fresh live Codex schema preflight passed 18/18. Full pytest passed **1,354 tests
with four existing opt-in skips / 1,358 collected**, exit 0, 1,229.40 seconds.
After pytest and both live retries completed, **602/602 sequential controls**
detected their mutations and passed after restoration, exit 0, 3,704.89 seconds.
All 242 source-file hashes were restored; `git diff --check` passed. The first control attempt
stopped at an ambiguous `shared_audit_outline` anchor after eight successful
mutation/restoration pairs. The source-restoration check passed. The control was
narrowed to the audit input, all 602 anchors were checked for uniqueness, and the
entire runner was restarted. Only that runner file changed after full pytest;
production code, prompts, schemas and test cases still match its tested manifest.
No separate lint/typecheck is configured.
Non-author review remains caller-owned.

### Remaining limits

Native word counts include machine markers. Initial route 1 counts are
4,604 native / 4,553 without node markers / 4,468 without both node and citation
markers; route 2 counts are 4,638 / 4,610 / 4,517. The final unverified drafts
are **4,714 / 4,663 / 4,578** for route 1 and **4,619 / 4,591 / 4,498** for route 2.
Thus route 2 falls two words below 4,500 under a count excluding both marker
types, despite passing the existing native counter. Neither draft is verified
or submission-ready. Role classification and semantic mapping remain model
judgments. Source routes remain single-paper with the
previously disclosed omitted-support and novelty limits. Serving-model identity
is unverified; requests retain `gpt-6-luna`. Codex source excerpts remain explicitly
model-reported, and admission limits are not hard execution caps. Existing-export
staleness is unexercised because neither copy began with a final essay export.

### Finding placement and next step

- F1 — Typed role rules and their semantic limits: “Typed audit and root conclusion”.
- F2 — Exact-marker repair feedback, three-round bound and preserved W1 scan: “Revision feedback and preserved boundaries”.
- F3 — Live flag counts, root-conclusion result, rejected short repairs and audit variability: “Live comparison and integrity”.
- F4 — Repeated native retrieval rejection, successful diagnostic's limits and absent verification/exports: “Live comparison and integrity”.
- F5 — Executed tests, initial control-anchor failure, corrected full control run and review boundary: “Verification”.
- F6 — Original-run preservation, chain verification, cached retry audits and durable evidence: “Live comparison and integrity”.
- F7 — Native versus marker-free counts, including route 2's 4,498-word repaired draft: “Remaining limits”.
- F8 — Unverified serving identity, model-reported excerpts and admission-only caps: “Remaining limits”.
- F9 — Inherited route-quality limits and unexercised stale-export behavior: “Remaining limits”.

**9 findings, 9 placed.** The unresolved step is diagnosing the rejected native
web event without broadening the allowed tool boundary, then completing native
citation/originality verification and the final audit. Any later revision to meet
a stricter word-count rule must also pass those checks. No API alternative or
additional retry is proposed as a completed result.

DONE nu4 round4 head=d15eb43ef56a01079d9ad453b95ee37be675fa77 tests=1354/1358 negctl=pass route1=fail route2=fail exports=0


## Round 5 — native web retrieval and two final exports

Both routes completed the native lifecycle and produced final drafts and essay
exports. The transport fix, full offline suite and all 608 sequential mutation
controls passed. Local commit: `0368a17992c7ef8339abb7913b08792b7d785786`; the working tree is clean. Work started from clean
`d15eb43ef56a01079d9ad453b95ee37be675fa77` on `fix/writer-length`. All new live calls
used Codex, with no API/Claude fallback, delegation or push.

### Refusal diagnosis and narrow fix

The new refusal receipt identified **`item.completed` → `web_search` →
`action.type=other`**. It records fixed, allowlisted event/item/action/tool-name
labels only. Unrecognized strings become `unknown`; arbitrary text, arguments,
URLs, identity and credential sentinels stay out of the diagnostic.

The adapter had accepted the exact object `{"type":"other"}` only while pending.
The installed `codex-cli 0.163.0` generated its JSON protocol schemas offline;
both WebSearchAction and ResponsesApiWebSearchAction enumerate Other as a named
web-search variant. The native reproduction established that completion emits
it too. The adapter now accepts only that exact object inside a `web_search`
event during `search_evidence`, and retains it as opaque in receipts. Unknown
action names, Other with additional payload fields, non-web tools, and web events
outside retrieval still refuse. No particular operation is inferred from Other.

The fixed native retrievals actually exercised the previously rejected variant.
Route 1 recorded two search actions plus one Other, 10 query strings and two
source URLs; route 2 recorded one search action plus one Other, five query strings
and two source URLs. Both passed before entering citation/originality verification.

The round-4 native and diagnostic receipts had equal isolation flags, requested
model, effort, system prompt and schema metadata. Their only input difference
was the diagnostic's substituted generic topic. No configuration difference was
established, and that comparison does not prove the topic caused the different
actions. All round-5 native resumes retained the original run topic.

The general event taxonomy is documented at
https://developers.openai.com/codex/noninteractive. The pinned executable's
locally generated schemas and the native refusal receipt establish this variant;
the documentation page alone does not establish Other's semantics. Evidence:
`codex-protocol/`, `round4-comparison.json`, and `route1/rejected-event.json` under
the round-5 evidence root below.

### Native lifecycle and audit disagreement

Both initial resumes used the unchanged, audit-passed round-4 drafts and their
logged accepted audit cache entries, after confirming byte-identical audit
prompts. Retrieval passed on both. Each verifier retained two citation items;
route 1 removed one unverified quotation (`quote:0`), and route 2 removed two
(`quote:0`, `quote:1`). Both originality assessments were **possible_overlap**.

Fresh final audits of that cleaned text then failed: route 1 had **44 flags**
(41 miscited source claims, three unsupported claims); route 2 had **eight**
(one miscited source claim, seven unsupported claims). Neither had missing nodes,
and neither attempt exported. Those failures remain in the append-only history.
The evidence does not establish that quotation deletion caused every new flag.

Each cleaned draft was screened with the effective provider before saving it as
an additional native `select --draft` input. The existing three-round targeted
revision bound and every downstream verification gate remained in force:

| Route | New audit of cleaned input | Targeted revision | Audit after revision | Final audit |
| --- | ---: | --- | ---: | ---: |
| 1 | 0 flags | None | — | 0 flags, cache replay |
| 2 | 6 flags | One accepted round, 4,613 native words | 0 flags, fresh call | 0 flags, cache replay |

The repeated cleaned-input audit prompts were **byte-identical** to the earlier
adverse final-audit prompts. Thus route 1 changed from 44 flags to zero with no
text edit, and route 2 changed from eight to six before its actual revision.
`route1/audit-comparison.json` and `route2/audit-comparison.json` retain the hashes.
Route 1's final content equals its cleaned resume input. These contradictory
judgments remain unresolved; native completion does not establish a stable
semantic verdict or show that route 1's 44 flagged claims were repaired.

The final verification calls retained both citations, removed nothing further,
and again assessed originality as **possible_overlap**. Because verification
left each already-audited text unchanged, the native final-audit calls used their
accepted cache entries and recomputed the local verdict. Both returned zero flags
and both commands exited 0. No regeneration, adverse-audit cache injection,
manual final-draft write, or guard override was used.

### Final artifacts and word counts

These are durable, byte-identical copies of the native outputs:

| Route | Native words | Without node markers | Without either marker type | Files |
| --- | ---: | ---: | ---: | --- |
| 1 | 4,710 | 4,659 | 4,574 | [Essay](/home/dev/ara-work/nu4/runs/nu4-proof/round5/route1/export/essay.txt) · [draft.json](/home/dev/ara-work/nu4/runs/nu4-proof/round5/route1/draft.json) |
| 2 | 4,613 | 4,585 | 4,492 | [Essay](/home/dev/ara-work/nu4/runs/nu4-proof/round5/route2/export/essay.txt) · [draft.json](/home/dev/ara-work/nu4/runs/nu4-proof/round5/route2/draft.json) |

The native counter includes machine markers. Route 2 is eight words below 4,500
when both marker types are excluded. Both exports retain the `possible_overlap`
assessment and the audit-disagreement limits above; this is no claim of novelty,
independence, or submission readiness.

Native run paths remain `/home/dev/ara-work/nu4/runs/nu4-round5-route1/` and
`/home/dev/ara-work/nu4/runs/nu4-round5-route2/` (links to the temporary-memory run
copies). Each durable evidence directory also contains its native methodology,
final unverified artifact, original and cleaned resume inputs, full `run.tar.gz`,
log suffix, full anchor, and `result.json`.

### Verification and integrity

The refusal-receipt regressions first failed 18 checks because rejected-event
identity was absent; three unaffected checks passed. All 21 focused checks passed
after adding the sanitized labels. Broader Codex transport/schema checks passed
76/76 before the acceptance change. The completed-Other regression failed with
`cli_tool_event` before the compatibility fix. Afterward, 30 focused web/boundary
checks passed. One intermediate fixture assertion expected completion while its
malicious payload was emitted at start; the fixture was corrected to inject that
payload on completion, with no accompanying production change.

Full offline pytest passed **1,358 tests, four existing opt-in skips / 1,362
collected**, exit 0, **1,485.41 seconds**. Command:
`env -u ARA_LIVE_TEST uv run --locked pytest -q --basetemp /dev/shm/ara-nu4-r5-pytest`.
The matching round-4 18-case live schema preflight was reused after native
manifest validation; schemas, model/effort and the pinned CLI version were unchanged.
All five new native isolation canaries passed.

**608/608 sequential mutation controls passed**, exit 0, in **4,593.57 seconds**.
Every mutation returned 1 and every restored check returned 0. All **242 source-file
hashes** matched the pre-control manifest after restoration; `git diff --check`
passed. Their anchors were checked for uniqueness before dispatch. Only the
mutation runner changed after full pytest,
to add one explicit credential-label sanitization control; production code,
prompts, schemas and tests retain the full-suite manifest. Controls cover the
exact Other variant, unexpected Other payloads, diagnostic presence/sanitization,
shell/file refusal and a fully formed web event outside retrieval. No source
mutation ran concurrently with a live invocation or the full suite. No separate
lint/typecheck is configured; non-author review remains caller-owned.

All **130 route-1 and 106 route-2 round-4 source files** are unchanged. Both copied
log prefixes and frozen artifacts are unchanged. The complete log/anchor chains
verify through **8,579 and 8,379 events**, retaining 85 and 76 new events. Both
full archives were verified file-by-file against the completed native runs.
Each route has ten actual new model-response receipts; route 1 additionally has
three audit cache replays and route 2 has two. Imported historical API receipts
are not new API calls.

Evidence root: `/home/dev/ara-work/nu4/runs/nu4-proof/round5/`. It contains full test
transcripts, `pytest-result.json`, the full-suite and control source manifests,
`live-results.json`, per-route audit/verification/retrieval comparisons, and the
native archives. `controls-verification.json`, `control-results.json` and
`controls.tar.gz` preserve the completed control verdicts and transcripts.
`precommit-verification.json` records the restored source and owned-file checks.
`final-verification.json` confirms all 242 tested source paths match the committed
content, with symlink targets verified separately. The first receipt attempt
compared the `AGENTS.md` link blob with its dereferenced manifest hash; the
receipt script was corrected and passed without changing production source.
`handoff.json` records the implementation handoff and its evidence links.

### Remaining limits

Serving identity remains unverified; every new model request retained
`gpt-6-luna`. Source excerpts remain model-reported from Codex web search, and
configured allowances reserve admission capacity rather than imposing hard
per-call execution caps. Semantic role classification and source fidelity remain
model judgments, with the concrete disagreement reported above. The inherited
single-paper, omitted-support and novelty limitations remain. Stale-export
behavior is unexercised: both copies began without final essay exports, and all
failed attempts preceded each copy's first successful export. Nothing was pushed
or externally submitted.

### Finding placement

- F1 — Exact completed Other refusal, sanitized diagnostics and narrow web-only acceptance: “Refusal diagnosis and narrow fix”.
- F2 — Diagnostic/native topic difference does not establish causation: “Refusal diagnosis and narrow fix”.
- F3 — Removed unverified quotations, retained citations and possible_overlap verdicts: “Native lifecycle and audit disagreement”.
- F4 — Contradictory audits on byte-identical prompts, route 1 accepted without repair, and final cache replays: “Native lifecycle and audit disagreement”.
- F5 — Two native exports, all three word counts and route 2's eight-word marker-free shortfall: “Final artifacts and word counts”.
- F6 — Regression history, corrected fixture, test/control evidence and caller-owned non-author review: “Verification and integrity”.
- F7 — Preserved source runs, verified log chains and archives, new calls distinguished from cache/history: “Verification and integrity”.
- F8 — Unverified serving identity, model-reported web excerpts, allowance and semantic-judgment limits: “Remaining limits”.
- F9 — Inherited single-paper/omitted-support/novelty limits and unexercised stale-export behavior: “Remaining limits”.

9 findings, 9 placed.

All 608 controls passed; all 242 source paths match the tested manifest and
committed content. `git diff --check` passed and the working tree is clean.
Local commit: `0368a17992c7ef8339abb7913b08792b7d785786`. Non-author review remains caller-owned. No push.

DONE nu4 round5 head=0368a17992c7ef8339abb7913b08792b7d785786 tests=1358/1362 negctl=pass exports=2/2 rejected_event=web_search.other


## Round 6 — conservative fresh final audit

Implemented locally from `0368a17992c7ef8339abb7913b08792b7d785786` on
`fix/writer-length`. Native results: **2/2 new essay exports**.
No delegation, paid API, Claude fallback, push or external submission occurred.
Verification removed both essays' bibliography entries and citation markers;
both retain `possible_overlap`. These native exports are not a submission-readiness
or source-fidelity verdict.

### Gate and repair policy

The final gate defaults to **k=3** fresh provider requests, configurable as an
integer at least three. Requests use the same base audit input, bypass response-cache
reads and writes, and retain admission, validation, identity/credential scanning
and accounting. Separate requests do not establish statistical independence.
Any substantive flag or missing-node failure blocks export. The verdict includes
the union across current samples and valid adverse history for the same prompt,
including historical computed verdicts. A favourable cache entry or three later
clean samples cannot erase earlier adverse evidence. No automatic majority
adjudication is implemented.

Receipts include flags per sample, per-sentence clean/dissent sample ids,
historical flags, binary agreement, prompt/draft hashes and incomplete batches.
Per-sentence agreement is the larger share of clean/adverse votes. The batch
agreement below is the fraction of sentences with unanimous binary votes;
unanimous adverse votes still reject. Malformed historical responses are disclosed
as unusable, never counted as clean. Current samples retain bounded schema
correction; an uncorrected incomplete batch refuses. Methodology and the existing
route-report audit collection expose these receipts.

Repairs target the union. Initial and final repairs share at most three rounds;
final replacements must change each flagged sentence. Every final edit goes back
through citation/originality verification before another fresh audit batch.
Imported resumes carry used repair rounds forward. New validated composition
invalidates previous `draft.json` and `export/essay.txt`; log-derived export ignores
final events preceding that composition marker. Old history remains immutable.

### Native audit batches and repairs

Both routes started from independently copied round-5 runs and their final drafts.
The existing verified schema preflight was reused after native validation;
schemas, requested model and CLI pin were unchanged. All final samples below used
fresh transport, not response-cache replay.

| Route | Batch | Flags per sample | Prior adverse flags | Union sentences | Unanimous sentences | Verdict |
| --- | ---: | --- | --- | ---: | --- | --- |
| 1 | 1 | 0, 0, 36 | 44 | 47 | 209/245 | reject |
| 1 | 2 | 41, 52, 42 | none | 53 | 234/246 | reject |
| 1 | 3 | 0, 0, 0 | none | 0 | 245/245 | accept |
| 2 | 1 | 30, 0, 0 | none | 30 | 214/244 | reject |
| 2 | 2 | 2, 0, 5 | none | 6 | 238/244 | reject |
| 2 | 3 | 1, 15, 1 | none | 15 | 230/244 | reject |
| 2 | 4 | 0, 0, 0 | none | 0 | 244/244 | accept |

Route 1 repairs: round 1: 47 sentences, 5,400 native words; round 2: 53 sentences, 5,387 native words. There were **10 actual fresh audit calls**, including any initial audit and bounded schema correction, and 9 valid final-batch samples. Native latest command exit: **0**.

Route 2 repairs: round 1: 30 sentences, 4,533 native words; round 2: 6 sentences, 4,512 native words; round 3: 15 sentences, 4,413 native words. There were **13 actual fresh audit calls**, including any initial audit and bounded schema correction, and 12 valid final-batch samples. Native latest command exit: **0**.

Route 1's first batch retained the earlier 44-flag adverse verdict despite two
clean current samples. It repaired the 47-sentence union, then another 53-sentence
union, before obtaining three clean final samples. One audit in the second batch
needed schema correction, making ten actual fresh audit calls for nine valid
final samples. The successful gate was not rerolled.

Route 2's first command stopped after its second repair: verification removed
both bibliography entries and their citation markers, shortening 4,512 native
words to 4,419. A new final-stage minimum check incorrectly reapplied the writer's
4,500-word target. The corrected path permits verification cleanup and final
repairs below that construction target, retaining the 6,000-word cap, schema,
nontrivial body and marker checks. The run configuration stays unchanged so full
source context remains available. Two regressions also exposed repair-budget
reset on resume and the same minimum restriction during final repair; all were
fixed and demonstrated with negative controls.

The corrected native resume used the same run's `draft.unverified.json`, not a
fresh copy or regeneration. Its full cache and adverse history were retained,
and its new composition marker carried **two used repair rounds**, leaving one.
`initial-exit.json` preserves the first exit 2, and `pre-resume.json` pins the log
prefix and resumed draft. `resume-integrity.json` verifies that the entire failed-attempt
log prefix is unchanged, the imported draft matches the saved partial byte-for-byte,
and the resumed run accepted only repair round three. No manual final-draft write
or gate override was used.

### Verification cleanup, exports and word counts

Route 1 verification: pass 1: removed 0 items, originality `possible_overlap`; pass 2: removed 2 items, originality `possible_overlap`; pass 3: removed 0 items, originality `possible_overlap`. Full item statuses and URLs remain in `result.json` and the methodology.

Route 2 non-audit response refusals: unsupported originality URL (1). These responses did not count as successful verification; any correction retained the ordinary bounded validation policy.

Route 2 verification: pass 1: removed 0 items, originality `possible_overlap`; pass 2: removed 0 items, originality `possible_overlap`; pass 3: removed 2 items, originality `possible_overlap`; pass 4: removed 2 items, originality `possible_overlap`; pass 5: removed 0 items, originality `possible_overlap`. Full item statuses and URLs remain in `result.json` and the methodology.

Route 1's final bibliography contains **0 entries** and its body contains **0 citation markers** after cleanup. A clean sampled audit does not restore the removed source citations or establish source fidelity.

Route 2's final bibliography contains **0 entries** and its body contains **0 citation markers** after cleanup. A clean sampled audit does not restore the removed source citations or establish source fidelity.

`possible_overlap` is the verifier's recorded assessment, not an automatic
export prohibition in existing semantics. Native export does not establish novelty
or competition readiness.

| Route | State | Native words | Without node markers | Without both marker types | Essay |
| --- | --- | ---: | ---: | ---: | --- |
| 1 | final export | 5387 | 5336 | 5336 | [Essay](/home/dev/ara-work/nu4/runs/nu4-proof/round6/route1/export/essay.txt) |
| 2 | final export | 4413 | 4385 | 4385 | [Essay](/home/dev/ara-work/nu4/runs/nu4-proof/round6/route2/export/essay.txt) |

Counts use the native counter with node markers removed and then both node/citation
markers removed for comparison; title and bibliography remain part of that counter.
Final artifacts are native outputs copied byte-for-byte. Run links remain
`runs/nu4-round6-route1` and `runs/nu4-round6-route2`. Each evidence directory
contains the full archived run, final unverified artifact, log suffix, anchor,
result receipt, and compressed methodology. Successful routes also contain the
final draft and essay.

### Source versions and integrity

Route 1 completed before the cleanup-length/resume-budget correction. Its exact
initial source hashes are retained in `first-source-tested.json`; the corrected
source hashes and archive are `source-tested.json` and `tested-source.tar.gz`.
The pre-correction `calls.py` and `orchestration.py` were recovered byte-for-byte
and matched against the initial manifest in `initial-runtime-source/`; the
initial audit-module bytes were not recovered, so this is not a complete archive
of the earlier source tree. Its original hash and native receipts remain.
The final consensus logic is unchanged between these snapshots. Route 1 stayed
above the construction target and did not resume within round 6, so neither
corrected condition occurred in its executed path. This is an explicit source
qualification, not a claim that route 1 was rerun at the committed head. Route 2's
corrected resume used the final tested source.

Route 1: all **137 original files**, the copied log prefix, and frozen artifacts remain unchanged. The full log/anchor chain verifies through **8697 events**, including **118 new events**. Its new suffix has 17 actual model-response receipts and 3 cache replays; all 1 new isolation canaries passed. The complete archive was checked file-by-file against the native run.

Route 2: all **114 original files**, the copied log prefix, and frozen artifacts remain unchanged. The full log/anchor chain verifies through **8557 events**, including **178 new events**. Its new suffix has 25 actual model-response receipts and 5 cache replays; all 2 new isolation canaries passed. The complete archive was checked file-by-file against the native run.

Inherited historical API records are not new API calls. Stale-export invalidation
is now exercised: each copy began with a prior successful final export; the new
composition removed it, and route 2's first failed command left no final essay.
Only a new successful final gate can create a current export.

### Tests and negative controls

Nine initial consensus regressions failed before implementation. Early affected
runs exposed obsolete expectations for a single cached final audit; these were
updated for three fresh calls. The first full suite finished with **1,372 passed,
four skipped and one failed / 1,377 collected**: the CLI smoke still expected 16
provider calls instead of 19. Its corrected owning file passed 6/6 and explicitly
checks three uncached final receipts. The first full transcript and source
manifest remain under `first-*`.

One attempted history fixture incorrectly assumed fenced JSON was accepted. The
production decoder rejects it; the fixture now verifies disclosure of malformed
history, with no parser relaxation. Three cleanup/resume/final-repair regressions
failed before the later correction. The corrected affected set passed **81 tests
in 86.69 seconds**, including **18 consensus tests**. All **15 scoped mutation
controls** passed, each red exit 1 and restored exit 0.

Final full offline pytest: **1376 passed, 4 skipped / 1380 collected**, exit 0,
in **1645.92 seconds**. Command:
`env -u ARA_LIVE_TEST uv run --locked pytest -q --basetemp /dev/shm/ara-nu4-r6-pytest`.

Complete sequential mutation runner: **621/621 passed**, each mutation exit 1
and each restored check exit 0, in **4697.85 seconds**. All 621
anchors were unique before dispatch. All **243 source hashes** matched after restoration.
No mutations overlapped full pytest or native calls. `git diff --check` passed.
No separate lint/typecheck is configured. Non-author review remains caller-owned.

Evidence root: `/home/dev/ara-work/nu4/runs/nu4-proof/round6/`. `pytest-result.json`, `controls-verification.json`,
`control-results.json`, `controls.tar.gz` and complete transcripts retain the
executed checks. `methodology-verification.json` confirms that both compressed
methodology copies match the native files and contain every recorded consensus
batch with its per-sentence agreement. `precommit-verification.json` and `final-verification.json`
verify owned files and tested-versus-committed source, including the `AGENTS.md`
symlink target and resolved content. `handoff.json` records the implementation
handoff and evidence links.

### Remaining limits

Serving identity remains unverified; every new native request retained
`gpt-6-luna`. Source excerpts remain model-reported from Codex web search.
Configured allowances reserve admission capacity rather than imposing hard
per-call execution caps. Repeated calls do not prove statistical independence;
three clean samples do not establish semantic truth or calibrated confidence.
Role classification, source fidelity and originality remain model judgments.
The inherited single-paper, omitted-support and novelty limits remain.

### Finding placement

- F1 — Fresh conservative gate, adverse-history union, agreement semantics and malformed/incomplete evidence: “Gate and repair policy”.
- F2 — Sample disagreement, binding history, targeted repairs and actual native outcomes: “Native audit batches and repairs”.
- F3 — Final-stage minimum failure, correction, carried repair allowance and preserved failed attempt: “Native audit batches and repairs”.
- F4 — Citation removals, originality assessments, word counts and export paths: “Verification cleanup, exports and word counts”.
- F5 — Route 1 source qualification and route 2 final-source resume: “Source versions and integrity”.
- F6 — Unchanged originals, verified chains/archives, fresh/cache distinction and exercised stale-export behavior: “Source versions and integrity”.
- F7 — Red regressions, obsolete-count failure, fixture correction, final tests/controls and caller-owned review: “Tests and negative controls”.
- F8 — Unverified serving identity, model-reported excerpts, allowance, statistical/semantic and inherited limits: “Remaining limits”.

8 findings, 8 placed.

Local commit: `d9ac619f6d95dfc588926044944d02d6181e5bdd`. No push or external submission.

DONE nu4 round6 head=d9ac619f6d95dfc588926044944d02d6181e5bdd tests=1376/1380 negctl=pass exports=2/2 k=3 agreement=1.000/1.000
