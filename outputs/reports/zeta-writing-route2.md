# Zeta — fork 3, route 2 writing

**4,638-word draft produced; audit FAIL; blocked at `revise_essay`.** Three targeted-revision attempts added citation markers forbidden by the native validator. None was applied. The saved essay remains the original length-valid, audit-failed draft.

[Essay draft](/home/dev/ara-work/reports/essays/fork3-route2-draft.md) · [Machine-readable results](/home/dev/ara-scaffold/runs/codex-writing-route2-control/results.json) · [Revision diagnostics](/home/dev/ara-scaffold/runs/codex-writing-route2-control/revision-diagnostics.json)

## Route and execution scope

Executed clean detached writer head `89be37a1074e87b34fc2b79dca0e2208020c8cda` at `/home/dev/ara-work/run-89be37a-route2`. The native selection chose `edd5e3e69fbe:r0` on the verified independent copy `/home/dev/ara-scaffold/runs/codex-writing-route2`. The source `/home/dev/ara-scaffold/runs/codex-fork-3` was never modified.

The operator's prior selection, “Write C ... actually build all routes”, and the route-2 brief were logged as HUMAN authorization on the copy. The route targets order sensitivity as a diagnostic constraint on epistemic-modal semantics. Historically CLOSED-derived, it is **CLOSED-single-paper** under this writer head: two distinct endorsed commitments from GSV1996, one paper, and one licensed sign inference. Its source support omits `gsv1996:r18-35:inf1`; a new literature contribution remains unestablished. The earlier [fork-3 substantive review](/home/dev/ara-work/reports/zeta-fork3.md) still applies (F7).

Fresh native schema preflight passed **18/18** cases. Native `cli.main select` then ran the sectioned writer, audit and targeted-revision path with Codex only. A call-factory wrapper relocated only cache storage into the copy and logged the old/new paths; prompts, model settings, budgets, route, writing and audit logic were unchanged. The CLI's explicit `--route` selection handles the disclosed single-paper classification.

## Writing and audit results

The plan had four sections, each budgeted at 1,200 words, totaling 4,800. Their initial outputs were 634, 436, 726 and 557 words. With the nine-word title, the assembled initial text would have been 2,362 words. Seven accepted expansions across two rounds produced **4,638 words**, within 4,500–6,000 (F1).

Two expansion attempts failed `essay section node coverage mismatch`; both recovered on the next attempt (F2). The accepted expansions preserved each initial section body verbatim as a prefix. The final draft matches a reconstruction from the persisted accepted sections.

| Check | Result |
|---|---|
| Length / schema / route-node coverage | PASS: 4,638 words; all 3 nodes represented |
| First sentence audit | FAIL: 151/245 sentences flagged; all 3 nodes covered; 0 missing nodes |
| Accepted targeted-revision rounds | 0 |
| Re-audit after targeted revision | NOT REACHED |
| Evidence retrieval | NOT REACHED |
| Originality / citation verification | NOT REACHED / NOT REACHED |
| Final verification re-audit / final export | NOT REACHED / NOT REACHED |

The only complete audit returned `faithful=false` (F3). Word count is native whitespace token count in **title plus body**, including node/citation markers and section headings, excluding bibliography. The Markdown wrapper and bibliography in the copied file are not added to that reported count. The two bibliography entries identify two commitments from the same paper, not two independent papers.

## Audit interpretation

The first audit flags sentence 3, which contains the exact root conclusion:

> The claim is limited: [[node:n0]] Order sensitivity in epistemic-modal discourse is a diagnostic constraint on an adequate semantics of those modals.

Its label assigns `node_ids=["n0"]` while also setting `asserts_premise_or_inference_not_in_outline=true`. The labels do not give a rationale distinguishing the framing from the conclusion. This is a concrete reason not to treat all 151 flags as independently established defects; it is not grounds for silently changing the native FAIL verdict (F4). [Representative flagged sentences](/home/dev/ara-scaffold/runs/codex-writing-route2-control/first-audit-samples.json) are preserved.

## Targeted revision failure

The native revision call attempted replacements for exactly 151 flagged sentences. All three responses failed `revision changed citations` (F5). The checks prohibit adding, removing or reordering citation/node markers in retained replacement text.

| Attempt | Sentence citation inventories changed | Words if the rejected changes had been applied | Result |
|---|---:|---:|---|
| 1 | 6 | 4871 | REJECTED |
| 2 | 41 | 5024 | REJECTED |
| 3 | 2 | 4864 | REJECTED |

These candidate word counts describe rejected responses, not delivered drafts. All detected citation mismatches added markers to sentences whose original citation inventory was empty. The third attempt added two citation markers to each of sentences 154 and 186. The saved draft stayed byte-equivalent to its pre-audit content. Zero accepted revision rounds means the lifecycle never reached its second audit or the two-round revision limit: it stopped when the **first revision call's three validation attempts** were exhausted.

A progress update incorrectly anticipated a fourth revision attempt; the native receipts show three, and the final result uses that count.

## Verification status

`search_evidence` was **not exercised**. The pinned Codex transport rejects that stage as `stage_requires_api_provider`, but this run stopped earlier. No claim is made that web verification failed live, or that originality/citation checks could pass without it (F6). No API or Claude substitution, manual essay repair or additional retry was introduced. There is no native verified `draft.json` or final essay export from this selection.

## Time and usage

| Phase | Process seconds | MODEL receipts | Input | Output | Cache-read | Total tokens | New API USD |
|---|---:|---:|---:|---:|---:|---:|---:|
| Schema preflight | 86.51 | 20 | 90,494 | 3,766 | 0 | 94,260 | 0.0 |
| Selection / writing / audit / rejected revision | 1292.10 | 19 | 306,956 | 40,931 | 2,944 | 350,831 | 0.0 |

Total process time across preflight and selection: **1378.62 seconds (22.98 minutes)**, excluding setup and this reporting. Total new usage: **445,091 tokens across 39 MODEL receipts**. Selection alone used 350,831 tokens across 19 receipts: 1 canary, 1 outline, 13 writer calls, 1 audit and 3 revision attempts.

All new calls have actual accounting; 0 unknown-usage receipts, 0 unsettled call IDs, 0 ARA response-cache hits, 0 server tools, 0 Claude calls and USD 0 new API spend. Provider cache-read usage is separately included above. Requested transport/model is `codex_cli` / `gpt-6-luna`; actual serving identity is unverified. Subscription-dollar cost is unavailable (F8). Imported history is excluded from these new-usage totals; its existing count-at-reservation policy was retained.

Native select timing was 1256.95 seconds; full selection process time was 1292.10 seconds. The latter includes wrapper authorization logging and final export. Neither is a measurement of human labor (F9).

## Integrity and artifacts

All 89 source files still match their pre-copy SHA-256 values, and no source files were added or removed. The copy initially used independent inodes; its 8108-record source prefix remains byte-identical. Native chain/checkpoint verification passed after execution. The checkout remains clean.

The original absolute cache path was `/home/dev/ara-scaffold/runs/codex-fork-3/cache`; the recorded relocation uses `/home/dev/ara-scaffold/runs/codex-writing-route2/cache`. This prevents the native selection's cache writes from changing the original (F10).

- [Delivered unverified draft](/home/dev/ara-work/reports/essays/fork3-route2-draft.md)
- [Native unverified JSON](/home/dev/ara-scaffold/runs/codex-writing-route2/draft.unverified.json) — canonical draft SHA-256:`0b9ec226e540d18a3df080c9cac0169ef79df3d6adf996b0a335346b2cad7789`
- [Pre-audit draft](/home/dev/ara-scaffold/runs/codex-writing-route2-control/draft-before-audit.json)
- [Preservation checks](/home/dev/ara-scaffold/runs/codex-writing-route2-control/revision-integrity.json):all 4 initial section bodies preserved; 0 accepted audit edits; latest draft matches reconstruction
- [Source-copy manifest](/home/dev/ara-scaffold/runs/codex-writing-route2-control/source-manifest.json) and [copy verification](/home/dev/ara-scaffold/runs/codex-writing-route2-control/copy-verification.json)
- [Native methodology](/home/dev/ara-scaffold/runs/codex-writing-route2/export/methodology.md), retaining failed responses and usage; not certified anonymised or submission-ready
- [Control notes](/home/dev/ara-scaffold/runs/codex-writing-route2-control/work-notes.md)

## Findings placement

- F1 → Writing and audit results: Initial section output undershot the 4,800-word plan: 2,362 assembled words. Seven accepted section expansions over two rounds raised it to 4,638; the native length and node-coverage validation passed.
- F2 → Writing and audit results: Two expansion outputs failed essay section node coverage mismatch. Both recovered on the next native attempt; neither rejected candidate was applied.
- F3 → Writing and audit results: The only complete audit returned faithful=false:151 of 245 sentences flagged as extra steps, with all 3 nodes covered and 0 missing. No audit passed.
- F4 → Audit interpretation: Flagged sentence 3contains the exact root conclusion with framing; its label maps to n0 and simultaneously marks an extra step. The flags are model judgments, not151 independently confirmed errors. No native verdict was overridden.
- F5 → Targeted revision failure: The first targeted-revision call exhausted 3 validation attempts, all revision changed citations. They altered 6, 41 and 2 sentence citation inventories respectively by adding markers. No revision round was accepted, no unflagged prose was changed and no re-audit occurred.
- F6 → Verification status: search_evidence was not reached. Codex refusal at that stage remains a source-code expectation, not an observed failure in this run. Originality/citation verification, final re-audit and final export were not reached; the delivered essay is unverified and audit-failed.
- F7 → Route and execution scope: The historically CLOSED-derived selected route is CLOSED-single-paper at writer head:2 supports from 1 paper, 1 sign inference. Omitted support gsv1996:r18-35:inf1 and unestablished literature novelty remain; writing does not repair those limits.
- F8 → Time and usage: All live receipts request codex_cli/gpt-6-luna; serving-model identity is explicitly unverified. No Claude calls or API spend occurred. Subscription-dollar cost is unavailable, not measured zero.
- F9 → Time and usage: Selection process elapsed 1292.10s versus native select timing 1256.95s. The process includes wrapper authorization logging and final export; native timing alone is not full elapsed time or human labor.
- F10 → Integrity and artifacts: The copied effective config retained an absolute cache path into the original source. Only that cache destination was relocated through the native CLI calls_factory interface and logged. All 89 original files remain hash-identical and the copied 8108-record prefix is unchanged.

**10 findings, 10 placed.**

The authorized native writing test is complete. The draft meets the length bound but has not passed audit or verification. The next unresolved stage is citation-preserving targeted revision; evidence retrieval and originality/citation checks remain downstream. No further generation was started.
