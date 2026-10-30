# Gap pilot fork — provider-window check blocks launch

The requested fork was **not launched**. Step 1 of the brief says to use gap-scoped packing if the configured provider window is below the approximately 328k L3 request. That condition holds for the unmodified pinned adapter. No model call, preflight, new target, route, selection, or API spend occurred. This is a blocked attempt, not an acceptable pilot.

## Window evidence and supported configuration

Requested model: `gpt-6-luna`, effort high, through `codex-cli 0.163.0`. The exact installed binary's embedded model record has `context_window=272000` and a separate `max_context_window=872000`. The extracted record, binary SHA-256, byte offset, and generated protocol schemas are preserved in the control directory. These are configured client metadata, not a fresh serving-model identity receipt.

The [official model page](https://developers.openai.com/api/docs/models/gpt-6-luna) lists a 1,050,000-token API window. That does not establish this isolated subscription transport's effective window. The [official configuration reference](https://developers.openai.com/codex/config-reference) documents `model_context_window`; the pinned generated protocol also contains that configuration field.

At clean `4cefe35`, `ara/runtime/codex_cli.py:278` passes the model, instructions, reasoning effort, and isolation flags, but no `model_context_window` override. It ignores user configuration and uses a fresh isolated CODEX_HOME. ARA's `model_context_token_bound` changes native admission only; it does not configure the provider window. The fork CLI likewise has no general context/config override flag. Consequently the 872,000 metadata maximum cannot be treated as already enabled by simply raising ARA's bound. No adapter edits, monkey-patches, transport replacements, or user-config workarounds were introduced.

## Bound comparison for Sigma round13

The proposed safe ARA bound is **239,232 = 272,000 − 16,384 output allowance − 16,384 safety margin**. It is **evaluated, not applied**. Native admission independently includes the output allowance, so this proposal reserves that space conservatively twice, following the brief's requested bound formula.

| Bound | Saved L3 input estimate | Output allowance | Total | Result |
| --- | ---: | ---: | ---: | --- |
| Original 200,000 | 311,785 | 16,384 | 328,169 | REFUSED, exceeds by 128,169 |
| Proposed 239,232 | 311,785 | 16,384 | 328,169 | REFUSED, exceeds by 88,937 |
| CLI default 272,000, without deductions | 311,785 | 16,384 | 328,169 | REFUSED, exceeds by 56,169 |
| Metadata maximum 872,000, not enabled | 311,785 | 16,384 | 328,169 | Arithmetic fit only; unavailable as an established configured window |

These are arithmetic comparisons of the **saved gap1r calibrated estimate**, not newly counted packed prompts or actual dispatched token usage. Sigma should report fresh packed-request counts against both **200,000 and 239,232**, retaining native full validation and the disclosed evidence scope. No packed request was available or tested here.

Planned fork: `/home/dev/ara-scaffold/runs/codex-gap-1f` (not created). Source: `/home/dev/ara-scaffold/runs/codex-gap-1r`. Control evidence: `/home/dev/ara-scaffold/runs/codex-gap-1f-control`. The supported next path in this brief is Sigma r13 packing; a separately integrated provider override would need its own evidence and validation before using a larger window.

## Preserved freeze and substantive review

All three saved frozen artifacts match their prior SHA-256 receipts; source checkout remains clean at `4cefe35f4a037725c1d5a97a1e401be46fe8fc83`. Freeze ID: `7418a5cd6975379634e68a7c7d900e78c8da91f2d7644d0fdd2b68ca0e2ee5ed`. There are 159 source commitments across 22 papers and one model-alignment bridge, with zero unresolved alignments. No new freeze was made.

Targets: **0**; routes: **0**; CLOSED-derived: **0**; substantive contributions: **0**. Every-target/every-route padding review has an empty population. This does not clear R28-F1. Both prior gap1r forward leads were independently classified as Boolean repackaging/padding, not contributions; neither supplies the safety–retraction link. L3 remains **unresolved**, with partial anticipation and missing rule anchors already documented. The prior SAT result means R28-F2 did not bite in the saved freeze; it does not certify faithful formalization.

The [gap1r substantive handoff](/home/dev/ara-work/reports/zeta-gap1r.md) remains the source review: disputed legacy alignment, Bledin stance/citation problems, H&M/Yalcin stance reversal, historical gap limitations, construction omissions, and incomplete L3 anchors all remain applicable. No source/formula metadata was repaired. The [prior rendered native report](/home/dev/ara-work/reports/overnight/gap1r/report.html) is retained as prior evidence, not a new fork report.

## Acceptable pilot criteria

| Criterion | Verdict | Evidence |
| --- | --- | --- |
| 1. Clean run | **FAIL** | No fork launched; no awaiting_selection. New Codex calls 0, Claude calls 0, API spend $0. |
| 2. Coverage | **PASS, inherited and qualified** | Saved T has 22/26 papers and 159/159 source citation/stance metadata; 1 separately identified model bridge. Artifact hashes rechecked; source fidelity limitations persist. |
| 3. Real routes | **FAIL** | 0/3 required CLOSED-derived routes, 0 substantive contributions. |
| 4. Readable output | **FAIL, unexercised for this fork** | 0 routes and 0 summaries. This handoff exists, but no new native fork report was generated. Prior gap1r browser proof is not a fresh gap1f result. |

## Findings placement

1. API, default CLI, and maximum CLI windows differ; larger maximum is not configured — Window evidence and supported configuration.
2. Adapter does not forward the provider context override; native bound alone is insufficient — Window evidence and supported configuration.
3. Original and safe raised bounds both refuse the saved request; counts are inherited estimates — Bound comparison for Sigma round13.
4. Fork unstarted, zero new usage, next path is packing — Bound comparison; Acceptable pilot criteria.
5. Freeze retained with inherited coverage and source-quality qualifications — Preserved freeze and substantive review.
6. Padding remains unresolved, no L3 contribution or route — Preserved freeze and substantive review.
7. No new native rendering proof; pilot fails — Acceptable pilot criteria.

**7 findings, 7 placed.**
