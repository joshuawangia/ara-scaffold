## Round 5

Scope: D4-B1 only, based on be8c2c2ee2adaf491a8a31bb38640d40e287cebc. Final commit 4b94f8e4a1053661d6dc36e3ec6d8bbc2b8d6405 on feat/paper-extraction; no push, delegation, paid generation, construction or pilot.

### D4-B1 behavior and protocol

Reconciliation now separates pending_obligation_ids from new_gaps objects. Every supplied obligation must be accounted for exactly once as pending or resolved with nonempty accepted evidence IDs. The runtime assigns each new gap a source/window/turn/index ID, preserving exact discovery provenance. Equal descriptions remain distinct; no fuzzy matching is used.

Every accepted response, including a response resolving the current obligation, appends its new gaps to the accumulated inventory and the work queue. The queue also processes gaps discovered while resolving earlier new gaps. It must drain, with an evidence-backed resolution for every accumulated ID, before merging the paper. Exhausted windows, invalid requests, cycles, context limits or normal budget limits explicitly refuse. A refusal retains earlier evidence, responses and obligation events.

Discoveries and resolutions append to the existing hash-chained event log. Immutable per-range/per-continuation rich snapshots retain their corresponding supplied and new obligations. The final cumulative obligations JSON is written only on successful queue completion; it is not a mutable ledger file. Pending status remains visible in full model response receipts. Each continuation still goes through counted admission, reserve/dispatch, raw response/usage logging and validation.

The ambiguous unresolved_references response field was removed. The changed prompt and schema give new cache identities; old responses are not guessed into the new protocol. Existing saved v2 literature and its provenance format remain readable and untouched. GX28 records this decision.

### Executed proof and review limits

The pre-fix placeholder regression demonstrated the actual bug: the original-only case did not refuse, and the positive case retained one obligation rather than two. Receipt: runs/gamma-round5/regression-before-page1.txt. Two preceding fixture-setup failures (identical cached context and a requested page without evidence) remain retained under regression-before*.txt; they are not counted as defect proofs.

Nine new test cases cover new-gap discovery during a pending response or the original resolution, original-only refusal, both-resolved success, distinct identity for equal descriptions, and graph review followed by multiple generations of discovered gaps. The direct cases check all four counted model calls, accepted raw responses, actual synthetic usage/cost records, exact provenance IDs, preserved snapshots, and absence of a merged/public artifact on refusal. Durable fixture receipts are under runs/gamma-round5/targeted-proof and runs/gamma-round5/pytest-proof.

Affected suite: 89 passed. Final `uv run pytest --basetemp=runs/gamma-round5/pytest-proof`: **382 passed, 2 skipped / 384 collected**, exit 0, 251.63 seconds. The two skips remain opt-in live checks. Receipt: `runs/gamma-round5/pytest-final.txt`.

Final `uv run python tests/integration/negative_controls.py`: **156/156 red, 156/156 restored green**, exit 0. Receipt: `runs/gamma-round5/negative-controls-final.txt`; complete individual traces and results: `runs/gamma-round5/controls/`. Every changed file in the commit matches its pre-verification SHA256. The source tree is clean. Machine-readable verification: `/home/dev/ara-work/reports/gamma-round5-verification.json`.

The new_gap_inventory control removes newly discovered gaps at their production ingestion point: the direct refusal regression then fails because extraction succeeds. The new_gap_queue control removes enqueueing while retaining inventory: the positive regression then fails at the final unresolved-inventory guard. Both restore green. Existing coverage and bounded-context controls were adapted to the explicit protocol, preserving their acceptance/refusal duties.

An early status-control trial was interrupted after its deliberately disabled guard allowed its unbounded fake provider to keep inventing gaps. Its red=2/restored=0 receipt is preserved in controls-before-bounded-fixture and is not a successful control. The test now fails immediately on a third provider request when the invalid second response was accepted. The final control runner uses this bounded fixture. No pytest suite ran concurrently with mutation controls.

Simplification and final diff inspection were performed inline under the solo restriction. No additional simplification was justified; the queue and accumulated immutable history have different duties, and proof tests were retained. No lint/typecheck command is configured. Code review: skipped (ce-code-review unavailable). The skill requires an independent reader for this silent inventory/data-boundary change; solo restrictions prevented that path. No independent review or live model fidelity is claimed; this handoff awaits Delta.

### Updated free 26-PDF plan

The prompt/schema change affects counts, so the native generation-disabled planner was rerun with the provider token counter. Official documentation was refreshed and again states “Token counting is **free to use**”; its text/hash/URL are retained in runs/gamma-round5/free-count-verification.json and token-counting-docs.txt. The initial urllib retrieval returned HTTP403; curl retrieved the official page successfully before counting.

The run made 106 free count requests, zero generation dispatches and zero MODEL events, with logged cost USD0. Internal generation caps were zero; operator caps remain unset and generation_ready=false. PDF hashes, physical-page partitions and every range's logged count were audited against the actual PDFs. No philosophical content entered tracked code, prompts, tests, docs or commits; source-bearing planning logs remain ignored in runs/.

| Quantity | Round-5 result |
|---|---:|
| Selected PDFs / physical pages / readable pages | 26 / 1,379 / 1,368 |
| Initial ranges; fit | 66; all fit |
| Counted initial input tokens | 1,607,572 (+14,652) |
| Largest initial input + output allowance | 35,030 + 32,000 = 67,030 / 200,000 |
| Initial expected-output scenario | USD49.077860 (+0.073260) |
| Initial full-output scenario | USD60.837860 |
| Initial plus estimated graph review | USD63.004860 |
| Initial plus review, full-output scenario | USD89.049660 |
| Estimated construction selection windows | 38, unchanged scenario |

The graph-review estimate retains round-4 assumptions (1,270 graph tokens/readable page, 8,000 overhead/window, 8,192 output/window). Its 24 windows are scenarios, not measured generated graphs. The USD63.004860 combined scenario excludes obligation traversal, requested contexts, corrections, retries, construction and pilot search/writing. New-gap queue work can increase actual traversal. These figures are not completion guarantees or spend authorization.

Receipts: runs/gamma-round5/plan26/extraction-plan.json, plan26-audit.json, plan26-cost-scenarios.json, plan26-stdout.txt, plan26-stderr.txt. The audit script and output are retained beside them. Plan SHA256: f8e8cd4211326fcf1f4f2723d5400583b47dabefbbaa842224fe53e0cb7a06be.

### Remaining full-run limits and preserved accounting

D4-N1 and D4-N2 were outside this repair and remain applicable. Pilot profile composition must remain explicit, and imported extraction charges consume the enclosing pilot cap. No caps or profiles were changed; Delta's proposed configuration/caps are still conditional operator inputs, not spending authorized or exercised here. Immutable receipts do not establish automatic collection resume.

This is still 26 available PDFs out of 53 manifest records. The 82 affected pages across seven sources include one unread page and 81 retained encoding-warning pages; ten blank pages explain the rest of the physical/readable difference. The intended run still needs the disclosed partial-source policy (missing record-only). Counted fit does not prove text order, glyph fidelity, semantic argument coverage, or successful live reconciliation. Model-selected evidence is schema/reference validated, not independently certified as resolving the source gap. Existing context/monetary limits can cause a late refusal after earlier paid work; no cap was increased and no automatic recovery was added.

This round adds USD0 paid usage. Earlier campaign accounting remains USD5.461870 measured + USD3.934240 held unknown = USD9.396110 accounted; build campaign USD5.433360 of USD6. No earlier failed receipts or reservations were released. The accepted 45-item freeze retains SHA256 25a7ec8c35d393b230738e6008467d70926697db6bed1f91c72b5edcd39cb3a4.

### Findings placement

| Finding | Deliverable placement |
|---|---|
| D4-B1 inventory loss and exact fix | D4-B1 behavior and protocol; Executed proof and review limits |
| Response protocol/cache compatibility and history format | D4-B1 behavior and protocol |
| Test/control evidence, failed trial disposition and independent/live-review limits | Executed proof and review limits |
| Changed free-plan counts, scenario costs and exclusions | Updated free 26-PDF plan |
| D4-N1/D4-N2 profile, budget, partial-source and completion limits | Remaining full-run limits and preserved accounting |
| No spending, retained unknown reservations and prior freeze | Remaining full-run limits and preserved accounting |

**6 findings, 6 placed.**

DONE gamma round5 head=4b94f8e4a1053661d6dc36e3ec6d8bbc2b8d6405 tests=382/384 negctl=pass fixed=D4-B1 status=awaiting-review
