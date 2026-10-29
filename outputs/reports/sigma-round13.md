# Sigma Round 13 — target context and explicit Codex window

**DONE** at `c99c6b32eba9259dbc5b00b2dbd3b83e11b7fdd6`. Base: `4cefe35f4a037725c1d5a97a1e401be46fe8fc83`; branch `fix/bounded-closure`. No push or live generation.

## Result and evidence scope

Target prompts now carry the gap's full evidence and a complete compact index of the rest of frozen T. `target_context_hops` defaults to one; gap commitment IDs and all support-group IDs seed the existing bounded-closure traversal. Shared canonical symbols give formal neighbours; explicit alignment bridges always bring their source evidence. Lexical leads are not treated as formal edges. Required hops never shrink to meet admission. Full rows preserve text/provenance; every compact row preserves its entire formula, stance and page citation. Legacy provenance remains explicitly unavailable.

Only the model prompt is projected. Novelty, classifier, formalization, CQ, route and solver gates retain full frozen T and metadata. CommitmentSet, commitments.json, frozen-t.json, provenance sidecar and v3 alignment reader contracts remain unchanged. General target proposals retain their existing bounded lexical bridge hints across the complete index; gap pools scope these hints to the full neighbourhood. No competing construction or search gate policy was introduced. Conditionals become ID/formula references; referenced catalogue definitions remain available for compact formulas too.

The copied L3 request has **3 full commitments, 157 compact commitments, zero omitted IDs/formulas**. The configured one-hop closure has no additional shared-symbol neighbours. It retains all **147** referenced catalogue symbols, **11/150** alignment judgments, and the complete bank/CQs, external gap framing and two recorded forward leads. The receipt lists the other **139** judgment pairs and **60** lexical leads as projected, not as unrelated or disproved. This preserves the original disputed model-alignment commitment in the compact index, labelled model_alignment.

## Admission comparisons

Free `plan-target-request` replay used the exact authenticated refused L3 payload from a copy of gap1r, including its gap record and recorded leads. It validates all frozen artifacts against chained receipts, restores the original upward-only calibration (runtime overhead 3,978), and runs the native packer/counter. CountingProvider prohibits generation and uses zero generation budgets. No semantic discovery or costly forward recomputation occurred.

| Request/configuration | Input estimate | Output allowance | Total | Native bound | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Original logged unpacked request | 311,785 | 16,384 | 328,169 | 200,000 | Refused (historical) |
| Packed, original bound | 105,724 | 16,384 | **122,108** | **200,000** | Fits |
| Packed, explicit 272,000 window | 105,724 | 16,384 | **122,108** | **239,232** | Fits |
| Unpacked current template, explicit 872,000 window | 312,084 | 16,384 | **328,468** | **839,232** | Fits |
| Packed, explicit 872,000 window | 105,724 | 16,384 | 122,108 | 839,232 | Fits |

The current unpacked count is 299 tokens above the historical count because the current target prompt explains the projection contract. Packed prompt size is **204,567 UTF-8 bytes**, compared with the historical 627,750. These are calibrated admission estimates, not exact serving-token usage. Each request includes its current prompt, response schema, system overhead, output reservation and retry feedback. Field byte breakdowns are logged; field token counts would not be additive.

Construction's commitments-only counts now explicitly say `commitments_only_capacity_not_target_readiness`. Passing that storage-capacity check does not assert target readiness. At the actual target boundary, `target_context_slice` records IDs, scope, projected fields/pairs, hashes, bytes and complete request counts. Oversized required packs refuse without truncation or generation.

Evidence: [200k plan](sigma-evidence/round13/l3-plan-200k/target-plan.json), [239232 plan](sigma-evidence/round13/l3-plan-239232/target-plan.json), [raised-window plan](sigma-evidence/round13/l3-plan-872k/target-plan.json). Each directory contains the exact projected request and chained events. All three contain **zero MODEL events**.

## Operator window decision

`model_context_window` is an explicit run-config setting and `--model-context-window` is accepted by `run`, `fork-from-freeze`, and `plan-target-request`. The adapter forwards `-c model_context_window=<integer>` to every isolated Codex invocation, including the canary. All existing isolation flags, read-only credentials, version check and tool-event rejection remain active.

The pin is `codex-cli 0.163.0`, model `gpt-6-luna`, default **272,000**, maximum **872,000**. The embedded-catalogue evidence is [zeta's extracted record](/home/dev/ara-scaffold/runs/codex-gap-1f-control/pinned-model-metadata.json), binary SHA-256 `399ff69c431c066e40de318fba45c2b07f45a76b19939d247ee4828fc70c4215`. The [official configuration reference](https://developers.openai.com/codex/config-reference) was fetched and confirms the model_context_window field. The OpenAI Docs skill was used for that narrow configuration check.

Invalid/non-integer windows, above-maximum overrides and models lacking a pinned maximum refuse. A missing setting preserves legacy behaviour. The optional positive `model_context_margin_tokens`/`--context-margin-tokens` defaults to 16,384. Native bound is **window − doubled target output allowance − margin**. With output configured at 8,192, the 872,000 setting derives 839,232. Admission also counts each request's output within that bound, conservatively reserving target output twice as requested.

`operator_context_window`, persisted fork/run config, CLI receipts, provider metadata, cache identity and methodology disclose the decision. Schema-preflight requirements are unchanged; fresh runtime canaries execute with the actual override. Offline executable tests prove argument delivery and canary preservation. **No live larger-window acceptance or serving identity is claimed.** The planned gap1f fork was not started by this task. Zeta owns its launch.

## Integrity and compatibility

The original `/home/dev/ara-scaffold/runs/codex-gap-1r` and the probe copy both retain **425/425 identical files, 711,079,736 bytes**, compared with pre-probe SHA-256 manifests. No source event, cache, artifact or anchor was rewritten. [Integrity receipt](sigma-evidence/round13/integrity.json), [original manifest](sigma-evidence/round13/source-before.json), [copy manifest](sigma-evidence/round13/copy-before.json).

New plan output lives outside the copied run. Probe paths and commands are preserved in the evidence directory. Two canned target-prompt keys were refreshed; all response values are identical to the base. The full frozen validation and model-alignment receipt formats are unchanged. A real configured-window override requires a supported pinned model, unlike legacy configurations without an override.

## Verification checkpoint

Tested committed tree: `c99c6b32eba9259dbc5b00b2dbd3b83e11b7fdd6`. **288/288 distinct scoped tests passed, 0 skipped**, across 21 test files, including native CLI smoke/replay, target packing/gates, frozen forks, Codex transport/canaries, alignment v3/resume, construction closure/shares, extraction planning, CQ context, counting and export. [Broad scoped run](sigma-evidence/round13/final-tests.txt), [affected-file rerun](sigma-evidence/round13/calls-recheck.txt), [latest-result summary](sigma-evidence/round13/verification-summary.json). The broad run had 287 passes and one stale named-position mock hash; only its fixture helper changed afterward. The entire affected test_calls.py file passed on rerun. The combined verdict uses the latest receipt for each test ID; it is not presented as a single all-green invocation.

**10/10 sequential production-wire controls** failed with their wire disabled and passed after exact restoration: full-T novelty; full-T classifier; complete compact formulas; mandatory bridge evidence; no hop shrinking; pinned window maximum; CLI argument forwarding; bound derivation; existing leaf output allowance; existing Codex canary-context rejection. Tests and controls were never run concurrently. All **668** control anchors validate; the other controls were not executed this round. [Control results](sigma-evidence/round13/controls/results.json).

All **257** pinned repository file hashes match their committed blobs, including the instruction symlink, and the final tree is clean. [Completion](sigma-evidence/round13/completion.json). This is a scoped regression verdict, not a full pytest/all-controls claim.

Evidence strategy: three target-context regressions failed before implementation; two free-plan tests failed before the helper existed; nine context-window regressions failed before implementation, then passed. Subsequent fixture failures were corrected: the retry fixture needed a schema-valid nonempty target list; the fork fixture needed the requested model in its source configuration; the stored target-prompt hashes and named-position fixture registration needed rekeying. The broader suite also exposed a production regression: general target pools had lost their lexical bridge hints. The fix preserves those hints for general pools while retaining gap-scoped packing. The existing cross-paper regression proves this native path. None of these fixes relaxes a production gate. Native CLI smoke/replay passed after rekeying (7/7), with response values unchanged.

No separate agent review or full-suite verdict is claimed. This task uses native inline ce-work, returns to the caller, and skips publishing. No workers were spawned.

## Remaining substantive limits

Packing and a configurable client window do not resolve L3. No new target, route, CLOSED-derived result, essay or human selection exists from this task. The gap1r/gap1f handoffs' inherited limitations remain: disputed legacy entailment bridge; source/formula and stance/citation limitations; incomplete gap rule anchors and coverage; two padded forward leads; nonexhaustive search and no demonstrated substantive contribution. They were neither repaired nor accepted as semantic proof here. See [gap1r handoff](overnight/gap1r/handoff.md) and [gap1f handoff](overnight/gap1f/handoff.md).

## Findings placement

1. Full evidence scope plus complete compact T index; full gates preserved — Result and evidence scope.
2. Prior readiness mismatch corrected by capacity labels and assembled target admission — Admission comparisons.
3. All three requested comparisons fit, with historical/current-template count distinction — Admission comparisons.
4. Pinned window forwarding, maximum, conservative derivation and legacy behaviour — Operator window decision.
5. Client-window configuration and offline tests do not prove live service capacity — Operator window decision.
6. Original/copy integrity and unchanged frozen persistence formats — Integrity and compatibility.
7. Verification scope, mutation controls, corrected fixtures, and no independent review — Verification checkpoint.
8. No semantic L3 resolution; inherited source/stance/padding limitations remain — Remaining substantive limits.
9. No live generation, spending, fork launch or publication by this task — Result and evidence scope; Operator window decision; Verification checkpoint.

**9 findings, 9 placed.**
