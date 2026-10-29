## Re-review round 2

**Verdict: FIX-FIRST. Recovery recommendation: ALT — model-chosen roots/components, deterministic graph closure, then model formalization of the fixed inventory.** The rich-v2 design fixes the old B1 summary-cap problem, and R1's strict-refusal bypass is fixed. The required real build-T construction still has no accepted batch or freeze. I also reproduced a reconciliation coverage gap and a loss of measured accounting after a token-counter failure.

Subject: `/home/dev/ara-work/gamma`, `feat/paper-extraction`, **`140a54b8620eed256901e099a1a861870e4f5e69`**, round base `7aacc81`. I read `gamma-round-2-rich.md` before the author's round-2 report, reviewed the changed implementation/contracts and native callers/tests, and inspected the existing live receipts read-only. I made **no live/paid calls, no implementation edits, and no delegation**. New probes and review receipts live outside the branch. The negative-control runner temporarily mutates and restores production files as requested.

### Ranked findings

#### D2-B1 — BLOCKING: unresolved extraction references can disappear through an empty reconciliation

**Locations:** `ara/runtime/calls.py:250`, `:290`, `:307`, `:320`; `prompts/extract_paper.txt:6`.

**Failure scenario:** A range returns `coverage_complete=false` and an unresolved reference. `allow_incomplete=True` accepts it. Reconciliation receives the accepted range graphs and the strings describing unresolved references, but no original page text. It may then return `items=[]`, `coverage_complete=true`, `unresolved_references=[]`. The checker accepts that response without a resolution map, adds nothing, and publishes the original incomplete graph as extracted. The pending obligations have vanished; no evidence ID or explicit resolution explains their disposition in the final rich artifact.

**Independent proof:** My placeholder source contained P/Q. The first response retained only P and declared unresolved `Q`; the second response was an empty, supposedly complete reconciliation. The real extraction path published **status `extracted`, one item, two accepted model calls**. The reconciliation request had no `pages`, and the final artifact had no resolution inventory. This is not merely the unavoidable possibility of a model paraphrasing badly: a previously explicit unresolved obligation is allowed to disappear without an auditable resolution. The existing reconciliation test uses two already-complete disconnected graphs and an empty reconciliation, so it cannot detect this failure.

**Fix direction:** Give unresolved obligations stable IDs, originating range/page information, and explicit resolution records. Each must map to existing or newly accepted evidence/link IDs, or remain unresolved and prevent a complete extraction. Supply the relevant counted boundary/source text when the range graphs do not contain enough evidence; do not ask the reconciler to recover omitted source content from memory. Keep additive immutable graphs, but require the union plus resolution ledger to account for every obligation. Add an incomplete-range/no-op-reconciliation rejection test and a genuine cross-range premise/inference/qualification resolution test. Page-range subdivision is useful, but does not yet establish complete reconciled source evidence by design.

#### D2-B2 — BLOCKING: the required live construction remains unproved; the production correction is still generic

**Locations:** `ara/runtime/construction.py:128`, `:140`, `:171`; `ara/runtime/calls.py:195`; existing receipt `runs/gamma-round2-live-attempt3/construction-final/events.jsonl`.

**Failure scenario:** The real batch selected 31 of 176 source items but violated the implemented closure invariant. It was correctly rejected under that invariant, and its correction could not fit the remaining authorized build budget. There are **zero accepted live batches, zero freezes and zero published live commitments**. This is a completion blocker specified by the brief, not a context overflow or a green-offline-test substitute for the missing proof.

I independently recomputed closure from the accepted artifacts and rejected response. The selected items touch components of **44 and 27 nodes**. Closure is **71 nodes**, requiring exactly **40 additions**. Iterative expansion adds **11, 17, 11, then 1** nodes. Thus a one-hop missing-ID list would be inadequate; gamma's diagnostic total of 40 is the transitive result. The recorded request counted 56,529 input plus 60,000 output tokens, well below 200,000. The failure was structural selection, not input capacity.

The code computes `dependencies` for validation but does not put the dependency/component map in `inputs`. Its error is only `working T drops premise/link/qualification`. The generic retry sends that message and the entire rejected response. It does not yet send the proposed connected-component IDs or explicit missing-dependency set. Those improvements are recommendations in the author report, not implemented production recovery.

**Fix direction:** Implement and prove a recovery protocol offline before another paid attempt. Gamma's proposed component IDs plus transitive missing-ID feedback are a sound improvement **for the current whole-component policy**, provided they are deterministic functions of the immutable model-extracted graph and are logged/counted. They do not guarantee the 71-node formalization fits output, symbol or working-T budgets. The cheaper alternative below avoids asking the model to perform reachability at all. Retain all rejected receipts, recompute admission after changing the request, and obtain an accepted merge/freeze proof within whatever separate build budget the operator authorizes. This review makes no paid attempt or budget amendment.

#### D2-S1 — SHOULD-FIX: closure means an entire undirected component, which is stronger than preserving a chosen argument's prerequisites

**Locations:** `ara/runtime/construction.py:47`, `:51`, `:54`, `:140`; `prompts/build_t_batch.txt:4`.

**Failure scenario:** In a placeholder graph, inference I uses P to conclude Q, while inference J uses the same P to conclude R. Choosing the complete P/I/Q argument forces J and R too: the implementation makes every inference's premises, link, conclusion and qualifiers a clique, and `applies_to` is bidirectional. Repeating the requirement over the selected set produces the whole connected component. A common premise or broadly applicable distinction can therefore pull most of a paper into T, even when only one argument is relevant. Under the proportional working allowance, an otherwise usable relevant argument can then be refused.

**Independent proof:** The dependency function expanded `{p,q,i}` to `{p,q,r,i,j}`. The extra branch was required because of graph connectivity, not because the selected inference depended on it. This does **not** mean the live model's 31 items were adequate, or that all 40 omitted live items were unnecessary; that would require source-level semantic review. It means the message “drops premise/link/qualification” describes a stronger policy than a minimal prerequisite check.

**Judgment:** The current implementation is correct for its expressly stated **whole connected component** contract. It is conservative but over-strict as a general implementation of **needed dependencies of a selected argument**. Do not simply disable closure. Decide the selection unit explicitly: retain whole components as a disclosed conservative policy, or let the model choose argument/inference roots and define directional prerequisite plus applicable-qualification closure. Shared-premise reuse must not automatically become a requirement to include every downstream consequence unless that is the intended selection policy. Version/test that rule, including shared-premise branches and shared qualifiers. Component IDs alone make the current policy easier to obey; they do not solve its potentially excessive scope.

#### D2-S2 — SHOULD-FIX: a post-response token-count failure discards known measured usage and the response

**Locations:** `ara/runtime/construction.py:163`, `:168`; `ara/runtime/calls.py:151`, `:177`, `:181`, `:97`.

**Failure scenario:** A build-T response arrives with valid raw usage, is charged in memory, and passes local graph/symbol validation. Its validator then calls the provider's token-count endpoint to measure working-T or catalogue size. If that transport raises, `_execute_once` re-raises before writing the MODEL receipt. `_call_once` sees a start without a completion, resets the measured charge and logs the original reservation as unknown actual usage, with the known response discarded. Introducing remote counting inside validation makes this an operationally reachable failure after a successful paid response.

**Independent proof:** A valid mocked batch returned **100 input/50 output tokens, USD0.00175**. An injected OSError during the later `propose_targets` sizing call produced a MODEL record with **100 input/64,000 output tokens, USD1.6005**, `accounting=reservation_unknown_actual`, and `response=None`. A safe stop occurred, but the accounting no longer reflects what was already known, and the paid response cannot be recovered from this log.

**Fix direction:** Persist the measured response/usage receipt before performing fallible follow-up counting, and log validation/count failure separately. An output that cannot complete validation remains rejected/provisional and must not enter T or cache; its measured bill and raw response should still survive. Reserve-unknown handling should apply only when actual provider usage is unavailable, not when a subsequent validation dependency fails. Add this exact transport-failure regression and a negative control.

#### D2-N1 — NOTE: uncertainty is disclosed, but numeric totals mix reservations with measured usage

**Locations:** `ara/runtime/export.py:45`, `:66`, `:92`, `:98`; `ara/runtime/calls.py:217`.

**Failure scenario:** An exporter consumer reads `tokens`, `cost_usd`, `local_totals` or extraction totals as measured usage. Those fields sum unknown-usage reservation events alongside actual events. The original failed extraction's methodology, for example, displays 15,838 input/32,000 output tokens and USD0.879190 in local totals, although the actual response usage is unknown. It does correctly set `accounting_complete=false`, provides `unknown_spend_reservations_usd`, and says reservations are not measured charges. The log labels permit separation; this is a presentation/aggregation hazard, not concealed known spend or a reported successful extraction.

**Fix direction:** Expose parallel `measured_usage`, `unknown_usage_reservations` and `budget_accounted` totals, for both tokens and USD and for local/inherited scopes. Do not fill unknown actual usage with zero or treat a held reservation as a measured invoice. Keep the original events unchanged. The final construction methodology's `accounting_complete=true` applies to its own imported/current receipts; it does not reconcile the four failed sibling runs. Campaign accounting must include those logs too.

The author report and its machine receipt make that campaign distinction correctly: **USD3.059635 measured**, **USD3.934240 held with unknown usage**, **USD6.993875 accounted against caps**. Extraction and build caps remain separate. I found no basis to relabel the four unknown reservations as either measured charges or free requests. D2-S2 is a separate bug where usage actually was known and then lost.

#### D2-N2 — NOTE: measured extraction cost is driven chiefly by structured output and retries; the default cap and large-source path remain planning constraints

**Locations:** `config.yaml:64`, `ara/runtime/providers.py:158`, `ara/runtime/calls.py:87`, `:309`, `ara/runtime/construction.py:100`, `:112`; existing raw MODEL receipts under `runs/gamma-round2-live-attempt3/`.

**Failure scenario:** Treat the USD30 extraction profile or an assumed reduction in thinking as sufficient to make a 26/53-paper run affordable, or treat extraction range splitting as proof that a large source can reach T. The measured scenarios are **USD52.095172 for 26 papers** and **USD94.934857 for 53**, both above that cap. They are page-scaled extrapolations from two papers/44 pages and one paid validation retry, not quotes or upper bounds. The 358-page source and real multi-range reconciliation remain unproved. Construction packs whole papers; a single rich source above the counted batch bound refuses before a batch call, and proportional node-count allowances can refuse a relevance-skewed batch even if other batches leave room.

**Evidence and fix direction:** Use the cost breakdown and structure-preserving reductions below, size actual artifacts before scheduling a full run, and explicitly review enclosing caps. If a single source is too large, pack validated argument components/subgraphs with required closure rather than truncate its graph. Reallocate working allowance using counted selected groups and remaining global budget where appropriate, rather than equating node count with relevance or token size. Preserve every source record and explicit omission/refusal. A successful combined extraction/build-T completion forecast is still unavailable because the only measured build-T response failed.

### Old findings and design checks

- **Old B1's cap defect is resolved by design.** Rich v2 has separate premise/inference/intermediate/final conclusion/distinction/qualification/reported/attacked records, explicit speaker/attribution, item-level citations, endpoint checks and `paper_stated` origin. No four-item or character quota remains. Per-range IDs are namespaced and immutable artifacts retained. Counted request overflow and `max_tokens` trigger subdivision; single-page and oversized reconciliation refuse. No source text slicing or formula-based evidence deduplication was found. D2-B1 limits the completeness claim for unresolved reconciliation, and D2-B2 keeps the end-to-end real-run verdict open.
- **Old R1 is resolved by design.** `extraction.py:268` refuses any partial paper under `--missing refuse` before either empty-partial continuation or model dispatch, including wholly visual, mixed visual/readable and encoding-warning cases. The strict CLI cases passed independently in the full suite.
- **Batch/symbol/merge mechanisms have coherent local invariants.** Stable source sorting/content hashes and plan ID enter requests/cache identity. The shared catalogue grows in dispatch order. Duplicate names, symbol signatures, unbound variables, occurrence bindings, evidence inventory, exact attributed text and citations are checked. Symbol reuse is a model choice against its stated meaning/signature; deterministic code validates it without inventing equivalence. Merge retains distinct agreeing/contradictory formulas and sorts stable evidence IDs. These are structural checks, not semantic verification that a model's symbol reuse or attribution is faithful.
- **One freeze and capacity safeguards are in the native path.** `prepare_commitments` checks prior freeze, builds/validates the full working T, saves immutable commitments, then emits the freeze before target/search work. All ModelCalls requests now pass counted admission, including cache replay and downstream T consumers. The 53-paper CLI test exercises four batches and nontrivial placeholder graphs. Its fake token counter proves the tested lifecycle, not real token density, output fidelity, successful cross-batch live alignment, or the 358-page source.

### Closure and recovery judgment

Gamma's proposed component IDs plus missing-dependency feedback is **sound as a constrained improvement to the present policy**, not sufficient evidence that another paid attempt will succeed. The component map must be computed from the accepted rich graphs, include all transitive members, be stable and versioned, and appear in the logged/countable request. Feedback must distinguish missing selected-group members from other validation failures. Recount symbol/working/output budgets too. Never accept the old rejected response merely by changing its status or omitting the check.

I recommend the **alternative** because reachability and exact source-field copying do not require new philosophical content:

1. **Model selects roots/groups and gives relevance decisions.** It receives rich evidence with stable IDs and any deterministic component map. Use a compact selection response; do not ask it to independently reproduce the closure set or formalize items whose selection is still unsettled.
2. **Code computes closure of those roots under the chosen, versioned graph policy.** For today's conservative rule this is connected-component union. Record root IDs, added IDs, graph hash and the rule version. This follows links already supplied by the extraction model; it creates no new premise, inference, attribution, equivalence or relevance judgment. If choosing directional argument closure instead, settle/test that policy explicitly rather than silently changing semantics.
3. **Model formalizes the fixed resulting inventory.** Request only evidence ID, formula and necessary new-symbol/alignment decisions. Code copies exact attributed text/citations from immutable evidence and can derive syntactic symbol-occurrence inventories from the returned formulas. Semantic symbol alignment remains model-authored and locally validated. Require exactly the requested evidence IDs; validate the catalogue and all measured budgets before the final deterministic merge/freeze.
4. **Preserve and account for omissions.** A model reason can cover an explicitly named unselected group; code can expand that group to its member IDs in logs. It must not invent why a source is irrelevant. Retain rejected/provisional receipts and freeze only after the completed construction passes.

This can avoid an expensive rejected full formalization followed by full regeneration. It is not a free way to finish the current 31-item response: the other 40 items have no accepted formalizations, and code cannot invent those. Existing provisional formulas could be reused only through a new verified production recovery path with their original receipt, catalogue and validation history; otherwise request a fresh, correctly scoped formalization. Component/root selection itself remains a logged model call unless an already logged selection is explicitly adopted.

The previous automatic correction counted **90,078 input + 60,000 output**, reserving **USD1.950390** against only **USD0.426715** remaining in the separate build allowance. That stop was correct. The proposed USD2 extension in gamma's report has not been granted here. A changed recovery request will have a different count and should not reuse that estimate as a quote.

### Cost drivers and reductions that preserve argument structure

I read `usage.output_tokens_details.thinking_tokens` in the existing raw receipts rather than inferring reasoning volume from text length:

| Work | Measured input / output tokens | Reported thinking tokens within output | Measured USD |
| --- | ---: | ---: | ---: |
| Extraction rejected attempt | 16,141 / 12,314 | 0 | 0.388555 |
| Extraction accepted correction | 31,660 / 13,019 | 465 | 0.483775 |
| Partial-paper accepted extraction | 31,636 / 25,268 | 0 | 0.789880 |
| Rejected build-T batch | 55,510 / 44,795 | 17,353 | 1.397425 |

At configured USD5/M input and USD25/M output, extraction input costs **USD0.397185** and output **USD1.265025**, so output accounts for **76.1%** of the USD1.662210 total. Only **465** extraction tokens are reported as thinking, costing **USD0.011625**, about **0.7%** of total extraction spend. Reducing reasoning alone is therefore not the main extraction saving in this sample. The partial paper's 25,268 output tokens with zero reported thinking support an output allowance above 8,192; lowering that limit would risk output-stop subdivision/rework rather than preserve the observed graph cheaply.

The rejected extraction cost **23.4%** of the measured extraction total. If the same sample had succeeded in one attempt per paper, its accepted calls alone would be USD1.273655; page-scaling that yields **USD39.917506 / USD72.743069** for 26/53 papers. These are counterfactual sensitivities, not achievable guarantees. The correction prompt repeated the rejected output; its input grew from 16,141 to 31,660 tokens. Schema mistakes and whole-response retries matter.

The failed build-T output accounts for **80.1%** of its USD1.397425 charge. Reported thinking alone is **17,353 tokens = USD0.433825**, about **31.0%** of that charge. Its 31 selected commitments were accompanied by 145 individual omissions, 52 new symbols and 52 bindings. Serialized response-field sizes were about **21,214 UTF-8 bytes of omissions**, **17,820 commitments**, **12,078 new symbols**, and **5,970 bindings**; exact source text/citation fields contributed about **9,870 bytes**. These are byte measurements, not token counts, but identify deterministic repetition and selection bookkeeping worth removing from generated output.

Priorities, with the same model:

- **Eliminate avoidable invalid shapes/retries.** Tighten the extraction wire contract for inference versus node fields where the provider grammar permits; add local fixture coverage of the observed error. Use targeted, accounted corrections where evidence can be retained safely, rather than making the model re-emit every accepted field. Do not erase failed attempts.
- **Use root selection and deterministic closure before formalization.** This targets build-T's observed failure and removes a graph-traversal/relevance/formalization combination from one large response. Keep every necessary premise/link/qualification.
- **Stop paying for exact copies and redundant bookkeeping.** Copy source IDs, text, citations and fixed metadata in code from selected evidence; derive purely syntactic symbol-occurrence bindings and expand explicit group omission decisions deterministically. Keep semantic formulas, symbol definitions/reuse judgments, source text paraphrases and relevance reasons model-produced. A compact wire representation can preserve the same rich artifact without a character quota.
- **Measure effort changes only where supported by the evidence.** The existing high/adaptive configuration may be costly for build-T, but extraction's measured thinking is already tiny. Any reduced-effort experiment needs the same structure/fidelity checks; no saving or acceptance is established here. I make no model-switch recommendation.
- **Preserve/reuse verified receipts and consider explicit provider prompt caching for stable repeated context.** Observed cache-read/write tokens were zero. This can reduce repeated input cost, but output is the larger cost center and origin-less local cache replay still must fail closed. Range splitting/reconciliation adds calls; it is a capacity mechanism, not automatically a cost optimization.

### Independent verification receipts

- `uv run pytest`: **315 passed, 2 skipped, 317 collected**, exit 0, **109.87 seconds**. `/home/dev/ara-work/reports/delta-rereview2-pytest.txt`. The skips are existing gated live tests; none was enabled. The full suite includes strict partial refusal, rich 53-paper CLI capacity and one-freeze tests.
- `uv run python tests/integration/negative_controls.py`: **110/110 red, 110/110 restored green**, exit 0. `/home/dev/ara-work/reports/delta-rereview2-negative-controls.txt`; copied results and individual red/green logs in `/home/dev/ara-work/reports/delta-rereview2-controls/`. They were started only after pytest and the independent probes completed; no full-suite run overlapped mutations.
- Independent probes: exit 0, network explicitly forbidden. `/home/dev/ara-work/reports/delta-rereview2-probes.py`, `.json`, `.txt` reproduce D2-B1, D2-S1 and D2-S2 and calculate cost sensitivities.
- Existing-live read-only analyses: `/home/dev/ara-work/reports/delta-rereview2-live-analysis.json` records component/closure counts; `/home/dev/ara-work/reports/delta-rereview2-token-breakdown.json` records usage/thinking figures. These are my analyses of existing paid receipts, not new paid runs.
- Final revision/restoration: HEAD remained `140a54b8620eed256901e099a1a861870e4f5e69`; `git status --short` was empty and `git diff --check` exited 0 after all controls restored the files.

I read the mutations and actual red receipts for nine new/changed controls, exceeding the required five:

| Control; definition in `tests/integration/negative_controls.py` | Mutation and observed red result |
| --- | --- |
| `rich_range_reconciliation`, line 93 | Remove the reconciliation branch. The test's last-call `mode` lookup raises KeyError because the last call is now ordinary extraction. This proves reconciliation dispatch, not successful resolution of incomplete ranges. |
| `strict_partial`, line 94 | Disable strict partial refusal. Visual-only CLI returns 0 rather than 2; mixed case dispatches a model call rather than refusing first. |
| `rich_dependency_closure`, line 96 | Disable the dependency predicate. The invalid batch advances through freeze into an unconfigured target request; that mock raises KeyError/unknown-usage STOP rather than the expected Rejected. |
| `rich_attribution`, line 97 | Disable exact evidence/attribution text checking. The changed-text batch likewise advances to the unconfigured target request. |
| `rich_symbol_alignment`, line 100 | Disable equality of returned bindings and formula occurrences. The bad-binding batch likewise advances to the target mock and fails there. |
| `rich_single_freeze`, line 107 | Disable prior-freeze refusal. The second preparation no longer raises the expected ValueError. |
| `rich_output_exhaustion`, line 112 | Remove `max_tokens` from the subdivision-trigger reasons. Extraction raises Rejected instead of completing split ranges. |
| `batch_wire_decode`, line 120 | Remove formula-string decoding. The formerly valid string response now fails the full local formula schema. |
| `batch_bound_variables`, line 122 | Disable the locally-bound-variable check. An unbound variable is accepted; expected Rejected is not raised. |

Every selected control restored green and none failed at test collection. The closure/attribution/binding mutations are genuine production changes, but their red evidence is indirect: the test transport only handles batch inputs, and the observed error is from a later unexpected target call. For the D2-B2 recovery proof, strengthen these tests around `construct`/`prepare_commitments` and explicit no-freeze assertions so the red result directly identifies acceptance of the invalid batch. Do not describe those existing red traces as direct missing-dependency or symbol-error assertions. The reconciliation control similarly does not cover D2-B1's no-op resolution gap.

New committed fixtures are placeholder-only graphs, formulas, raster/glyph stress data; changed prompt/schema/docs describe mechanisms without substantive philosophical content. I found no new tracked real-paper output. The formula-string wire workaround still decodes into the full local schema, and bound-variable checks preserve the symbol boundary. Those are legitimate transport/validation repairs, not relaxed semantic acceptance.

### Placement and handoff

| Finding / action-changing conclusion | Section carrying it |
| --- | --- |
| D2-B1: unresolved reconciliation can lose an obligation | D2-B1; independent probe receipts |
| D2-B2: no accepted live T/freeze; generic correction; verified 40-node deficit | D2-B2; closure/recovery judgment |
| D2-S1: whole-component closure is stricter than chosen-argument prerequisites | D2-S1; closure/recovery judgment |
| D2-S2: post-response count failure loses measured accounting | D2-S2; independent probe receipts |
| D2-N1: reservation/measured totals and campaign scope | D2-N1 |
| D2-N2: cost drivers, caps, large/skewed sources, structure-preserving savings | D2-N2; cost drivers and reductions |

Old B1/R1 dispositions and successful batch/symbol/freeze safeguards are in “Old findings and design checks.” The recovery alternative and its no-invented-content boundary are explicit above. **6 findings, 6 placed.** Next unresolved work is an offline reconciliation/accounting/recovery repair, followed by an authorized real construction proof; no such implementation or additional spend was performed by this reviewer.

DONE delta rereview2 blocking=2 should_fix=2 notes=2 tests=315/317 negctl=pass recovery=alt verdict=fix-first
