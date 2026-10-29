

## Re-review round 4

**Verdict: FIX-FIRST; full_run_ready=no.** The long-source windowing, global working allowance, empty-stage handling and full extraction profile are substantial improvements. I verified the 26-PDF plan's range coverage and arithmetic against the actual PDFs and saved count receipts. However, reconciliation can discard a **new unresolved reference discovered while processing an existing obligation**, then publish the paper as extracted. Fix D4-B1 before the paid run.

Subject: `/home/dev/ara-work/gamma`, `feat/paper-extraction`, **`be8c2c2ee2adaf491a8a31bb38640d40e287cebc`**, base `1b152d9`. I read the round-4 implementation brief and report, inspected the changed runtime, schema, prompt and test paths, and performed this review myself. No branch implementation edits, delegation, live/provider-count calls, paid generation, pilot execution or push. The negative-control runner temporarily mutates/restores source as explicitly required. Review receipts and proposed configuration are outside the branch. The previously read code-review skill remains adapted to the solo/report-only task; no multi-agent review is claimed.

### D3 dispositions

| Finding | Disposition at this head |
| --- | --- |
| D3-B1: unbounded full-paper reconciliation | **Original capacity defect resolved; completeness still blocked by D4-B1.** `reconciliation.py` counts graph/source windows instead of rebuilding one whole-paper request. Explicit page/evidence requests are admitted in full or refused; unresolved obligations cannot be cleared merely by an empty same-turn response. The new multi-turn ledger gap is separate. |
| D3-B2: whole-paper construction packing | **Resolved for bounded selected closures.** `construction.py:188` partitions evidence IDs within sources, computes prerequisites against the complete immutable graph, reuses already formalized IDs with their formulas/source evidence, and accounts for all final selected/omitted items. An oversized selected closure still refuses before formalization; arbitrary large closures are not themselves split into multiple formalizations. This explicit limit remains disclosed. |
| D3-S1: full-run policy disabled | **Resolved.** `extraction-full` pins the extraction stage to Opus, disables fallback, enables aggregate nonzero inference and one targeted correction, and refuses unset enclosing/extraction/token caps before provider creation. The model remains one editable stage setting. |
| D3-S2: empty ranges/batches impossible | **Resolved.** Argument-free ranges require an auditable complete disposition; empty-root windows require complete omissions and skip formalization. Overall empty T refuses. Aggregate inference acceptance remains active for argumentative papers. |
| D3-S3: proportional working allocation and catalogue cliffs | **Resolved as requested, with planning limitations.** Each selection receives measured remaining global working capacity. Exact source-copy/minimal-formula and catalogue-growth preflights precede formalization; accepted output is counted again. The full profile raises catalogue capacity to 32k and reserves 256 tokens per newly selected item. This is conservative planning, not a guarantee of actual symbol density or a global relevance optimizer. There is still no automatic root reselection after a capacity refusal. |
| D3-N1: targeted patch limitations | **Still disclosed, not a new defect.** Patches retain candidate entries; deletion, malformed/truncated-response recovery and live proof of the new protocol are not supplied. One correction per paper spans all its ranges/reconciliation; one per construction stage spans all windows. |
| D3-N2: pilot handoff and cost | **Native extraction-artifact handoff is available; cost must be reconfigured.** Use extracted literature with its provenance, not the old frozen T. The pilot constructs/freezes once before search. Full construction and pilot writing settings need composition, described below. No frozen-T resume was added or needed for this fresh full-corpus lifecycle. |

### Ranked findings

#### D4-B1 — BLOCKING: newly reported missing references disappear during obligation continuation

**Locations:** `ara/runtime/reconciliation.py:62`, `:74`, `:97`; `ara/runtime/calls.py:335`, `:341`.

The no-obligation review converts every returned unresolved description into a stable obligation. The active-obligation path instead assigns `result, _, request = execute(...)`: it discards the returned unresolved-reference list. Validation checks only that some unresolved text exists when a supplied obligation remains pending. It does not distinguish descriptions of that obligation from newly discovered independent gaps, and no new obligations are added during this traversal.

**Executed production-path reproduction:** initial extraction declares unresolved `Q`. The first reconciliation response accounts for that obligation as pending, reports **`['Q', 'R']`** as unresolved, and requests another page. The next response resolves only the supplied `Q` obligation. `extract(...)` then publishes **status `extracted`**, with one obligation (`Q`), one resolution and a nonzero inference count. The explicit `R` reference appears in the raw response history but never acquires a retained obligation or resolution in the final artifact. All three model-boundary responses were accepted in this offline placeholder probe. This is a multi-turn inventory loss; the new same-turn `resolved_pending_status` test does not cover it.

**Fix direction:** make pending existing obligations and newly discovered gaps separate structured fields. Give every new gap a stable source/window/turn-linked ID, append it to the immutable obligation history, and drain a work queue until every accumulated obligation has an evidence-backed resolution. Alternatively, explicitly refuse unsupported new-gap responses; never silently discard them. Do not use fuzzy string equivalence to decide that a new reference restates an old obligation. Include a direct regression where a pending response introduces an independent gap and a later response resolves only the original one, plus a negative control and a positive case resolving both. Preserve all intermediate receipts and count every continuation. This is a small-to-medium ledger/protocol correction, not a reason to abandon bounded windows.

Evidence: `/home/dev/ara-work/reports/delta-rereview4-probes.py`, `.json`, `.txt`. The companion probe confirms unknown requested evidence is correctly refused before another dispatch. These probes use placeholder responses and an injected counter; no semantic fidelity claim or live call is involved.

#### D4-N1 — NOTE: pilot profile composition and inherited charges matter to the run command and cap

**Locations:** `ara/runtime/cli.py:140`, `:163`, `:176`, `:178`, `:226`; `ara/runtime/extraction.py:350`; `ara/runtime/budget.py:37`; `config.yaml:63`, `:98`.

CLI profile application is a single shallow update. `--profile extraction-full` carries the new construction settings but does **not** inherit the pilot's 20k writer, 24k audit, 64k evidence-search and 48k verification allowances. Conversely, unchanged `--profile pilot` retains the old 16k catalogue and lacks the new construction correction/growth settings. The profile names are mutually exclusive, so two flags do not compose them.

Use the proposed composed configuration below with `--profile pilot`. It preserves the pilot's search/essay parameters and three generic validation attempts, while copying the full profile's Opus stage/no-fallback, 32k catalogue, 256-token growth reservation and targeted construction correction. Extraction itself still uses `--profile extraction-full` with its explicit one-correction policy.

`literature_provenance` checks the completed extraction artifact against its pinned source-log prefix. `import_provenance` retains original event labels, receipts and charges **before Budget is constructed**. Thus an enclosing USD100 pilot cap is not USD100 of new pilot spending: with the central extraction scenario it has only **100 − 62.9316 = USD37.0684** left for construction, all target/negation search and writing/verification. The previous live build's page-scaled scenario alone is **USD43.601943**; extraction plus that is **USD106.533543 before search/writing**. That build extrapolation is not a reliable forecast, but it disproves treating USD100 as a comfortable plan. A very sparse/lucky run could cost less; successful completion under USD100 is not established.

**Action:** use explicit composed settings and the conditional cap recommendation below. Do not suppress imported costs or pass `commitments.json` as literature. This review does not authorize generation or raise the actual branch configuration's caps.

#### D4-N2 — NOTE: bounded requests prevent overflow, but expensive refusal and incomplete source coverage remain possible

**Locations:** `ara/runtime/reconciliation.py:36`, `:68`, `:83`; `ara/runtime/construction.py:254`, `:270`, `:275`; `ara/runtime/extraction.py:218`; `config.yaml:109`.

The 358-page book's **16 initial ranges are not 16 total calls**. The graph-only review is estimated at another four windows. Each unresolved obligation may separately scan source/evidence windows and request up to 16 additional contexts by default. A near-full 168k-input/32k-output extraction call reserves roughly **USD1.64**; 16 extra requests alone can reserve/use up to roughly **USD26.24**, in addition to traversal and initial extraction. Actual counts may be much lower. The whole-run monetary cap is enforced, but there is no per-paper dollar cap or automatic budget-driven recovery. One late invalid range, unresolved obligation, oversized source window or selected closure can stop after earlier paid work. Immutable artifacts/receipts survive; they are not a demonstrated automatic resume of the complete collection.

Construction's preflights are correctly before formalization, but after paid root selection and any preceding successful windows. A minimal-formula floor and 256-token catalogue reservation cannot predict formal formulas/reuse; actual output can still fail its post-response limits. Overlarge closures refuse intact rather than lose support. Selection is sequential under remaining capacity, not a global comparison/reallocation of all proposed roots. These are explicit operational limits, not hidden truncation or code-invented equivalence.

The source inventory also remains **partial**: 82 affected pages across seven papers, including one unread page and 81 retained encoding-warning pages; ten blank pages explain the rest of the physical/readable difference. Planning fit does not certify text order, glyph fidelity or argument coverage. The known full run needs `--missing record-only`, with partial-source disclosures preserved. Do not call it strict full-text coverage. No OCR or real-model window/reconciliation success was proved in this unpaid round.

**Action:** retain the finite caps, inspect per-paper/obligation receipts as the run progresses, and stop/reassess unexpected traversal growth rather than automatically increasing limits. After extraction, replace the estimated construction window count with actual counted graphs before treating the remaining pilot budget as adequate. This remains a bounded experiment after D4-B1 is repaired, not guaranteed corpus completion.

### Independent plan audit and size arithmetic

I used the existing provider-count receipts read-only; I did not call even the free endpoint. I reloaded the actual 26 selected PDFs, matched every PDF hash, checked that each paper's range arrays partition exactly its readable physical pages without duplication, matched every range count to the logged request, and recomputed the costs. I also verified the plan file hash referenced by the supplemental cost scenario.

Plan SHA-256: `eae50186fe27abe3a085ae33b7b645bd99021e254eaefaa2c05770381c910072`. Independent receipt: `/home/dev/ara-work/reports/delta-rereview4-plan-audit.json`; script and PDF-reader warnings are beside it.

| Quantity | Independently checked result |
| --- | ---: |
| Selected PDFs / physical pages / readable pages | 26 / 1,379 / 1,368 |
| Count-request log events / generation starts / MODEL events / logged USD | 106 / 0 / 0 / 0 |
| Initial extraction ranges | 66 |
| Counted initial input tokens | 1,592,920 |
| Largest initial request | 34,808 input + 32,000 output = 66,808, below 200,000 |
| Largest book | 358 physical / 349 readable pages; 16 ranges; 377,551 counted initial input tokens |
| Estimated source graph size / selection windows | 1,737,360 tokens / 38 windows |
| Estimated graph-review input / output / windows | 1,802,360 / 196,608 / 24 |

The first three token-count/range measurements are based on saved provider counts, including conservative schema overhead. The graph densities, output densities and construction/review window numbers are **scenarios**, not measured corpus artifacts or accepted batches. In particular, 38 comes from per-paper ceiling arithmetic; production construction partitions the combined evidence by counted binary windows. It need not produce exactly 38 windows. Gamma labels that distinction correctly.

At USD5/M input and USD25/M output:

- Initial expected output: `1,368 * 1,200 = 1,641,600` tokens. Cost: `1,592,920 * 5/M + 1,641,600 * 25/M = USD49.004600`.
- Initial full-output scenario: `66 * 32,000 = 2,112,000` output tokens; cost **USD60.764600**.
- Estimated graph review: `1,802,360 * 5/M + 24 * 8,192 * 25/M = USD13.927000`.
- Initial plus estimated review: **USD62.931600**, **5,233,488** input-plus-output tokens.
- Initial plus review with full 32k output/window: **USD88.976400**, **6,275,280** tokens.
- The book's corresponding initial / with-review / full-output costs are **USD12.357755 / USD15.553105 / USD20.263905**.

These figures agree with Gamma's numeric tables. The lower USD49 figure is not a complete extraction estimate; the USD63 figure includes only the stated no-obligation review scenario. Neither includes obligation traversal, context requests, corrections, retries, construction, search or writing. The summed full-output scenario is also not an amount reserved all at once: runtime reserves each next call against actual spend to date. The planner's `generation_ready=false` and null operator caps correctly avoid claiming authorization.

### Recommended caps and concrete configuration

**Conditional recommendation after D4-B1 is fixed: extraction USD125; enclosing pilot USD350.** These are finite stop limits, not a quote or a promise to finish. No caps were changed in the subject checkout and no paid action was taken.

| Stage/profile | Cost settings | Token cap | Basis |
| --- | --- | ---: | --- |
| Extraction, `extraction-full` | `cost_cap_usd: 125`, `extraction_cost_cap_usd: 125` | 12,000,000 | `88.9764 * 1.4 = 124.56696`; covers the disclosed full-output scenario plus about 40% dollar room. The 12M token limit avoids the historical 6M cliff and is about 1.91× the 6.275M full-output scenario. |
| Enclosing `pilot` | `cost_cap_usd: 350`, `extraction_cost_cap_usd: 125` | 30,000,000 | Includes imported extraction plus new construction/search/writing. See construction stress calculation below. |

For a **conditional 38-window stress scenario**, use 70k source input + 32k catalogue per stage, 16,384 root output and 64,000 formalization output. Per-window root/formalization costs are approximately `102,000*5/M + 16,384*25/M = USD0.9196` and `102,000*5/M + 64,000*25/M = USD2.11`; 38 pairs total **USD115.1248**. This assumes every estimated window needs both stages near their allowances; sparse/overlapping selections can cost much less. Actual window counts and correction prompts can differ, so it is not a global upper bound.

A practical envelope is therefore **125 extraction + 115.1248 construction + 100 search/writing = USD340.1248**, rounded to a **USD350 aggregate cap**. The USD100 downstream allowance is a bounded operating budget, not a measured forecast: ten targets and their negations, depth/node settings, CQ/repair calls, long essay attempts and evidence/verification can still exhaust it. The code enforces the aggregate cap, not these internal suballocations. Review actual construction spend before continuing into expensive search; do not silently borrow from an assumed guaranteed writing reserve.

At the USD62.9316 central extraction scenario, the USD350 pilot starts with **USD287.0684** for new work. If extraction uses its entire USD125 cap, USD225 remains. Because imported extraction charges count again only as inherited accounting, the combined fresh extraction-plus-pilot spend is bounded by the enclosing cap for this one lifecycle; this is **not USD125 plus USD350 of new-spend permission**. Failed sibling runs and earlier campaign reservations remain separately accounted. No prior reservation is released by this proposal.

Reviewable configuration: `/home/dev/ara-work/reports/delta-rereview4-config.proposed.yaml`. It starts from the pinned branch configuration, fills the extraction caps, composes the full construction settings into `pilot`, retains pilot output/search settings, and selects an isolated cache path. It contains no credentials or source content. The exact 26 IDs audited are in `/home/dev/ara-work/reports/delta-rereview4-paper-ids.txt`. These are proposed inputs for the brain to approve/use after repair, not evidence of an executed run.

### Native extraction-to-pilot command shape

After the fix and the operator's budget decision, from `/home/dev/ara-work/gamma`, using fresh empty run/cache locations and operator-supplied `ARA_TOPIC` and `ARA_AUDIENCE`:

```bash
mapfile -t paper_ids < /home/dev/ara-work/reports/delta-rereview4-paper-ids.txt
paper_args=()
for paper_id in "${paper_ids[@]}"; do
  paper_args+=(--paper-id "$paper_id")
done

uv run ara extract \
  --config /home/dev/ara-work/reports/delta-rereview4-config.proposed.yaml \
  --profile extraction-full \
  --manifest /home/dev/ara-scaffold/literature/manifest.yaml \
  --fulltext-dir /home/dev/ara-scaffold/literature/fulltext \
  --missing record-only \
  --run-dir /home/dev/ara-work/gamma/runs/full26-extraction \
  "${paper_args[@]}"

uv run ara run \
  --config /home/dev/ara-work/reports/delta-rereview4-config.proposed.yaml \
  --profile pilot \
  --topic "$ARA_TOPIC" \
  --audience "$ARA_AUDIENCE" \
  --literature /home/dev/ara-work/gamma/runs/full26-extraction/literature.extracted.txt \
  --run-dir /home/dev/ara-work/gamma/runs/full26-pilot
```

Run the pilot command **only after extraction exits successfully and its artifact/provenance is complete**. Keep the original source log and sidecar accessible; copying only the text file is insufficient. The CLI imports extraction provenance as SYSTEM/MODEL history, constructs the bounded T, merges/freezes exactly once, then proposes targets and searches both polarities. It does not consume the old round-3c `commitments.json` or repeat PDF extraction.

Without a known route ID, `run` stops at `awaiting_selection`; writing is a separate native continuation using the stored run configuration and the same cumulative budget:

```bash
uv run ara select \
  --run-dir /home/dev/ara-work/gamma/runs/full26-pilot \
  --route "$ROUTE_ID"
```

The selected route must be one actually emitted by that pilot. This command performs writing, audit, evidence/verification and re-audit through the normal runtime. No such commands were executed during this review.

### Verification and mutation evidence

- `uv run pytest`: **373 passed, 2 skipped / 375 collected**, exit 0, **271.02 seconds**. Receipt: `/home/dev/ara-work/reports/delta-rereview4-pytest.txt`.
- Independent probes and actual-PDF/plan audit completed before starting the mutation runner. No network generation or live opt-in tests were enabled. The two pytest skips remain opt-in live checks.
- `uv run python tests/integration/negative_controls.py`: **154/154 red, 154/154 restored green**, exit 0; it ran after pytest and the independent probes/PDF audit ended. Receipt: `/home/dev/ara-work/reports/delta-rereview4-negative-controls.txt`; copied actual red/green traces and results: `/home/dev/ara-work/reports/delta-rereview4-controls/`.
- The proposed configuration was parsed and checked offline after mutation restoration: extraction/pilot caps, native pilot parser arguments, Opus/no-fallback settings, catalogue/growth/correction settings and pilot writer/audit allowances match the recommendation. No generation factory was invoked. Receipt: `delta-rereview4-config-check.json`.

I read the new mutation definitions and actual red outputs, including these ten:

| Mutation | Production change | Observed red result |
| --- | --- | --- |
| `full_profile_caps` | Removes unset-cap rejection | Explicit fake-provider failure: provider created before profile preflight. |
| `empty_range_disposition` | Accepts an empty range without a reason | Expected rejection does not occur. |
| `empty_root_accounting` | Removes overall empty-T refusal | Expected `empty working T` rejection does not occur. |
| `closure_preflight` | Removes the copied-source capacity preflight | Refusal occurs later as `working T global token allowance exceeded`, failing the expected preflight check; this control distinguishes early from post-formalization refusal. |
| `window_inventory` | Drops the first ID during partitioning | The expected successful build fails with `final evidence inventory mismatch`. The final guard catches the loss. |
| `full_graph_closure` | Closes against only the current window | Successful full-graph fixture instead fails with `working T drops premise/link/qualification`. |
| `closure_size_admission` | Disables selected-closure size stop | Expected budget refusal does not occur. |
| `requested_context` | Drops the model-requested pages | Positive cross-window resolution fails with `unresolved obligation empty context request`. |
| `bounded_graph_review` | Replaces review windows with the full page union | Positive review fails at counted context admission. |
| `root_measured_remaining_capacity` | Sends the original full allowance to every window | Measured-decreasing-allowance assertion fails (`10000 < 10000`). |

I also inspected `resolved_pending_status`, which fails directly when a same-turn resolved ledger retains unresolved text, and `prior_closure_context`, whose fake-provider assertion detects an empty supporting-evidence set before runtime wraps it as a `BudgetStop`. The latter proves payload transmission, not semantic reuse quality. All restored counterparts passed. None of these controls tests the new-reference/multi-turn loss in D4-B1.

The suite covers large placeholder graph windows, cross-window prerequisite closure, overlapping prior formulas/source context, a requested cross-page reconciliation, empty-stage behavior and cumulative capacity. Passing tests do not establish live semantic fidelity or complete obligation accounting beyond their exercised cases; D4-B1 is an independent counterexample. Changed tracked prompts, source, tests and decisions remain topic-neutral/placeholder-only by direct review. Real source text was not quoted into tracked files or this report. No lint/typecheck command is configured.

### Placement and final state

**3 findings, 3 placed:** D4-B1 is in the blocking subsection; D4-N1 is in its note plus the caps/configuration/native-handoff sections; D4-N2 is in its note plus the size arithmetic and cap limitations. All seven D3 dispositions are in the disposition table. Executed results and their limits are in verification; numeric planning and coverage evidence are in the independent audit. The valid earlier 45-item freeze and historical campaign receipts are not superseded by this review.

Final restoration check: `git status --short` empty; HEAD remains `be8c2c2ee2adaf491a8a31bb38640d40e287cebc`; `git diff --check` passes. The prior frozen-T SHA-256 remains `25a7ec8c35d393b230738e6008467d70926697db6bed1f91c72b5edcd39cb3a4`. No verification process remains active. Fix D4-B1, rerun its affected tests/control and required final gates, then apply the operator-approved configuration for the paid run.

DONE delta rereview4 blocking=1 should_fix=0 notes=2 tests=373/375 negctl=pass full_run_ready=no extraction_cap_usd=125 pilot_cap_usd=350 verdict=fix-first
