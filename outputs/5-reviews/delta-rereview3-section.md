

## Re-review round 3

**Verdict: FIX-FIRST for the full corpus.** ALT recovery now works on the two accepted Opus source graphs: the live 45-item T is structurally consistent with its sources, and the old obligation-loss, undirected-closure and measured-accounting defects are resolved. That success does not establish fitness for all 26 PDFs. Long-source reconciliation still reconstructs an oversized request, construction still requires each whole paper to fit one batch, and the measured symbol catalogue leaves little room for additional batches.

Subject: `/home/dev/ara-work/gamma`, `feat/paper-extraction`, **`1b152d9c78c9c30851b48d106359cb796bcedc61`**, base `140a54b`. I read the round-3/3b/3c author briefs, their report sections, repository rules and ownership plan; inspected the changed production paths, callers, schemas, prompts and tests; and independently audited existing live artifacts. This was a solo review with no delegation, implementation changes, live calls, paid token counting, pilot execution or push. The code-review skill was adapted to the explicit solo/report-only brief; its multi-agent workflow was not executed. Tests and probes ran before the separate mutation runner. Probe scripts and receipts are outside the branch.

### D2 disposition

| Finding | Round-3 disposition and evidence |
| --- | --- |
| D2-B1: disappearing unresolved obligations | **Resolved by design.** `calls.py:331` requires an exact, unique obligation inventory and nonempty accepted evidence IDs. `:396` creates stable source/range-linked obligations; `:407` supplies source pages; artifacts retain both ledgers. Missing resolutions and unknown evidence are rejected; the positive test adds a cross-range link and qualifier. The semantic adequacy of a model's resolution remains a source-review question. New D3-B1 concerns capacity, not silent clearing. |
| D2-B2: no accepted live construction / generic closure recovery | **Resolved for the required bounded proof.** Model roots → logged deterministic closure → exact-inventory formalization → copied source text/citations and derived bindings → deterministic merge → one freeze. I independently verified the existing live freeze and its receipts. No earlier rejected formalization was relabelled as accepted. |
| D2-S1: undirected component expansion | **Resolved.** `construction.py:48` follows supporting links, their premises/conclusions/qualifiers, and qualifiers applying to selected items. Shared premises and shared qualifiers do not pull in their other consequences. It conservatively keeps every supporting link for a selected conclusion; this is disclosed and matches the chosen policy. |
| D2-S2: actual usage lost after follow-up counting failure | **Resolved.** `calls.py:181` persists the measured raw receipt before parsing/counting; terminal failures retain actual usage. Regressions cover the exact 100-input/50-output, USD0.00175 failure, parse failure and transient terminal-log failure, without cache/freeze. |
| D2-N1: numeric actual/reservation ambiguity | **Resolved additively.** Export now separates measured, unknown-reserved and budget-accounted tokens/USD in local, inherited and aggregate scopes. I recomputed the live local and inherited totals below. Historical sibling-run reservations still require the campaign ledger; the author preserves that distinction. |
| D2-N2: cost and large-source fitness | **Still open.** Sonnet accepted neither sample, so it supplies no successful cheaper extraction projection. Opus extraction projection remains above USD30. Whole-source packing, oversized reconciliation and proportional working allocation remain; the new live catalogue measurement makes the cross-batch limit concrete. See D3-B1/B2/S3/N2. |

### Ranked findings

#### D3-B1 — BLOCKING: range subdivision is undone by a single full-paper reconciliation

**Locations:** `ara/runtime/calls.py:374`, `:406`, `:410`; `DECISIONS.md` GX21.

When any range has an unresolved reference, reconciliation sends **all readable original pages plus all accepted range graphs and obligations in one request**. It has no partition/retrieval continuation. If original pages already exceeded the context limit, this larger request cannot solve the reason for subdivision. Even without obligations, the union of all rich range graphs can overflow. Admission safely stops, but the complete extraction fails after paying for its ranges. This is an expressly disclosed refusal, not hidden truncation; it is nevertheless a blocker for promising the full long-source run.

**Executed independent probe:** a counted 180,000-input whole source with a 32,000-output allowance splits into two accepted ranges. Each declares an obligation. Reconciliation restores the whole source, fails the 200,000-token guard, and dispatches no reconciliation call. Two immutable range artifacts remain, with no completed extraction. Receipt: `delta-rereview3-probes.json`, `reconciliation_overflow`.

The actual largest PDF has **358 pages, 807,287 extracted characters / 823,122 UTF-8 bytes**. A rough four-characters/token estimate is already 201,822 tokens before prompt and graph overhead, against 168,000 available input tokens. This estimate is **not a provider token count**; the deterministic failure scenario is proved by the injected counter. The real long-source range/reconciliation path has not been demonstrated.

**Fix direction:** reconcile logged bounded obligation sets against counted source windows and relevant immutable evidence, retaining stable global IDs and one complete resolution ledger. Permit explicit model requests for additional page context; unresolved obligations must remain unresolved. Also bound the no-obligation cross-range pass rather than concatenating the whole graph. Prove a multi-range source whose total evidence exceeds one context, including cross-window references and no silent omissions. This is a **medium change**, not a larger token limit or shorter extraction. Cheap immediate protection is a preflight that explains/refuses the unsupported long-source path before paying for ranges; that does not complete the 26-paper objective.

#### D3-B2 — BLOCKING: rich evidence from one large paper cannot reach root selection

**Locations:** `ara/runtime/construction.py:164`, `:178`, `:187`.

Packing divides the corpus only **between papers**. A single source whose rich graph exceeds the 70,000-input batch bound stops before root selection, regardless of how small its relevant argument might be. Splitting extraction into page ranges does not change this construction boundary. Raising the batch setting cannot solve a graph larger than the model context after output/catalogue reservations.

**Executed independent probe:** one paper counted at 70,001 input tokens raises `build_t_batch oversized source batch`; zero model calls occur. This is the existing explicit behavior, now a full-run blocker rather than a speculative limitation in the two-paper exercise. The live two-paper/44-page source batch counted 55,962 tokens. Pure page scaling to 358 pages gives roughly **455,327 source-batch tokens**; that is a stress scenario, not a measured book graph or a prediction of uniform density.

**Fix direction:** plan source windows or model-selected root inventories over bounded evidence, preserving globally identified source graphs. Compute closure against the full immutable graph, then formalize bounded fixed inventories with shared symbols and deterministic duplicate handling, followed by the sole freeze. A closure that itself exceeds capacity must be explicitly handled/refused, never cut arbitrarily. Small-paper multi-batch tests do not prove this path. This is another **medium extension**, potentially shared with D3-B1's evidence-window machinery; configuration alone is insufficient for the general case.

#### D3-S1 — SHOULD-FIX: the full-run configuration does not activate the reviewed extraction acceptance/correction policy

**Locations:** `config.yaml:18`, `:85`; `ara/runtime/calls.py:276`, `:315`; `ara/runtime/cli.py:87`.

The checked-in extraction profile leaves `extraction_require_inference` and `extraction_targeted_corrections` unset. Its normal behavior therefore accepts a coverage-complete proposition list with zero inferences and uses generic full-response retries. Only the bounded live script/config enabled the new policy. The configured extraction model also remains Sonnet despite its 0/2 accepted outcome; changing the top-level model to Opus does not override `stages.extraction.model`.

**Executed independent probe:** with checked-in configuration plus the `extraction` profile, a one-premise, zero-inference response was accepted. Both policy keys were absent. This is intentional backward compatibility in the implementation, but is an unsafe handoff assumption for the next corpus run.

**Fix direction:** prepare a concrete, logged full-run configuration with the operator-selected **stage** model, explicit fallback policy, nonzero-inference acceptance, targeted-correction policy, and both enclosing/extraction caps. Add a profile/preflight regression using that configuration. Do not silently change historical artifact semantics. Enabling nonzero inference is a cheap safety gate for these argumentative papers, not a test of full coverage: one link among hundreds of propositions still passes. For a legitimately nonargumentative source, record/review an explicit disposition rather than invent a link to meet the count.

#### D3-S2 — SHOULD-FIX: legitimate empty ranges and all-omitted batches have no successful representation

**Locations:** `ara/runtime/calls.py:287`, `:389`; `schemas/select_t_roots.json:14`; `ara/runtime/construction.py:216`.

A readable page range containing only front matter, bibliography or other nonargument material cannot return a faithful empty graph: `empty extraction` is rejected and is not a split/recovery reason. This matters when a long book is divided into small ranges. Separately, root selection requires at least one root **in every batch**, so a model cannot explicitly omit an entirely irrelevant batch even when it supplies every omission reason. It must choose irrelevant material or fail the construction.

**Executed independent probes:** a one-page readable range with `coverage_complete=true`, no obligations and `items=[]` is rejected; a root response with no roots and complete group omissions is also rejected. These are refusal/selection constraints, not evidence that a real source should have been empty.

**Fix direction:** allow an auditable model-authored no-argument range disposition, while enforcing appropriate nonzero structure on the aggregate argumentative paper; allow a fully accounted zero-root batch to skip formalization and participate in the merge. Keep the overall empty-T refusal where appropriate. Both changes are **small**, with tests proving that empty stages cannot erase obligations, inventory, attribution or required source coverage.

#### D3-S3 — SHOULD-FIX: catalogue and working allowances are not sized for the measured multi-batch workload

**Locations:** `ara/runtime/construction.py:174`, `:230`, `:272`, `:275`; `config.yaml:93`.

The live build introduced **89 symbols**. Its logged catalogue-only counting difference was **31,034 − 20,563 = 10,471 tokens**, already **65.4%** of the fixed 16,000-token catalogue limit. Only **5,529** tokens remain. Another similarly sized batch with different meanings would bring this to roughly **20,942**, and fail **after** its paid formalization. The one-batch live proof never exercised reuse or growth across real batches. Code correctly refuses undeclared/conflicting symbols and requires model-authored reuse reasons; it must not force equivalence to fit the catalogue.

Working allowances also remain proportional to raw source-node counts, not selected relevance or measured closure cost. At the sample density, 1,379 pages imply roughly 5,516 source items. A 176-item batch then receives only `92,000 * 176 / 5,516 = 2,935` working tokens. The accepted sample's actual T increment is **19,115 − 3,304 = 15,811** tokens, **5.39×** that allowance. Thus rerunning the same root choices in a larger corpus can fail despite unused capacity in other batches. Fixed-inventory patch correction cannot reduce the chosen closure to repair such an overflow.

**Fix direction:** preflight counted selected closure/source-copy size and catalogue growth before expensive formalization, and expose these numbers to a logged root-reselection step when necessary. Carry unused working allowance forward or allocate against a global selection plan. Size/compact the shared catalogue from measurements, preserving meanings and full evidence in artifacts; do not deduplicate meanings in code. The immediate budget/configuration and diagnostic fixes are small; robust reallocation/reselection is **small-to-medium**. Prove at least two distinct-rich-symbol batches near the configured limit. The arithmetic above is conditional scaling, not a claim that every future symbol must be new or that the same 45 commitments must be chosen for every 44 pages.

#### D3-N1 — NOTE: the new wire and targeted corrections are sound but deliberately incomplete recovery mechanisms

**Locations:** `ara/runtime/providers.py:94`; `ara/runtime/calls.py:344`; `ara/runtime/construction.py:100`.

The three disjoint wire families remove the observed illegal `applies_to` shape without converting relations into inferences. The local relation/page/reference guards still apply after empty structural defaults. Formula strings are decoded and locally validated. Grammar acceptance was exercised by the author's existing live calls; those calls did not establish Sonnet extraction suitability.

Targeted corrections preserve omitted candidate entries and revalidate the full merged response. They are counted, charged and cache-keyed, with one allowance per paper or per construction stage across all batches when enabled. **Deletion is unsupported:** an extra unknown commitment, unknown omission group, or unused/new symbol cannot simply disappear in a patch. Malformed/ambiguous inventories and `max_tokens` responses are not patchable. This limitation is documented and safely refuses; it is not a weakening of validation. If such failures recur, add explicit deletion of rejected-candidate entries with inventory proof, not deletion of accepted source evidence. Neither live round-3c stage required correction, so live construction-patch success remains unproved.

#### D3-N2 — NOTE: the small frozen T has context headroom, but pilot handoff and full-run cost remain separate gates

**Locations:** `ara/runtime/construction.py:290`; `ara/runtime/calls.py:431`, `:443`, `:453`, `:469`; `ara/runtime/cli.py:125`, `:147`; `config.yaml:65`, `:85`.

The existing frozen T is **35,168 canonical UTF-8 bytes**. The author's provider-counted target request was **19,115 input + 8,192 output = 27,307 tokens**, leaving **172,693** of the 200,000-token context. Search consumers send T plus their goal/bank/proposal data and each uses counted admission. There is no evidence that this small T alone exhausts pilot context. The 100,000-input final working limit also leaves 91,808 tokens for extra search input at the ordinary 8,192 output allowance, but it only measures `propose_targets`; it is not a guarantee for arbitrarily large goals, proposals, repairs or later essay/audit data. No downstream live pilot calls were made here. An additional offline render used the actual frozen T, the complete bank for cuts, and placeholder goal/repair data: prompt sizes were 38,954 bytes (`propose_targets`), 64,206 (`propose_cuts`), 35,862 (`map_leaf`) and 36,748 (`tier1_repair`). Including projected-schema bytes, 8,192 output allowance and a 1,000-unit margin, the largest byte-based sizing total was 74,100. This corroborates headroom for these envelopes; it is not a provider token measurement or a proof for future variable-sized data. Receipt: `delta-rereview3-downstream.json`.

The native `ara run --literature` path reconstructs T and expects literature/provenance, not a frozen `commitments.json`; it has no direct frozen-T resume argument. Alpha must use a verified import/continuation path preserving the original freeze, catalogue, bank version and receipts. Passing this JSON file as literature would ask for a new construction. The available artifact is valid for structural review, not proof of a completed native handoff.

Cost permission also remains external to this review. The accepted Opus extraction sample still gives `1.662210 * 1379 / 44 = USD52.095173`, above the USD30 extraction profile. Naively scaling the successful ALT build gives `1.391215 * 1379 / 44 = USD43.601943`; 1.5× is USD65.402914, above the prior USD15 build ceiling. These are **two-paper scenario calculations, not estimates with reliable error bounds**: selection, shared symbols, range retries and batch overhead are nonlinear. They supply no authority to raise caps. Obtain an explicit run configuration/budget and a capacity-informed projection before the corpus run.

### Independent live artifact and accounting audit

I compared `runs/gamma-round3c/construction/commitments.json` with the two original accepted Opus source graphs and the live log/batch receipt, structurally only. No philosophical content was copied into tracked files or this report.

- Frozen SHA-256: `25a7ec8c35d393b230738e6008467d70926697db6bed1f91c72b5edcd39cb3a4`.
- **176 source items = 45 selected + 131 explicitly omitted**, with disjoint inventories. **2 model roots + 43 closure additions = 45**. The logged graph hash matches the source map; independently recomputed prerequisite closure matches the fixed inventory and frozen IDs.
- All 45 exact attributed texts and citations match their source records. Every selected inference's endpoints/qualifiers and every applicable qualification/distinction are present. Per-source counts are 23 and 22. Kind counts: 18 premises, 8 inferences, 7 intermediate conclusions, 1 conclusion, 3 distinctions, 5 qualifications, 2 reported views, 1 attacked view.
- All 89 symbol declarations match formula signatures; syntactic bindings match actual occurrences; definition evidence IDs belong to the selected set. This proves syntactic/provenance consistency, **not semantic correctness of formulas, symbol meanings, attribution or relevance**. Code follows source edges and copies fields; I found no code-invented argument or equivalence.
- Exactly one `commitments_frozen` event matches the file. There are no target/search/pilot dispatches. The partial source's eight glyph-warning pages remain disclosed; successful construction did not clear source-quality limitations.
- New local measured usage: **91,278 input / 37,393 output, USD1.391215**, two calls. Imported historical extraction: **79,437 input / 50,601 output, USD1.662210**, three calls. The log's USD3.053425 total is local plus inherited, not new spend. Both local and inherited unknown-reservation totals are zero.
- The campaign arithmetic remains **USD5.461870 measured + USD3.934240 held unknown = USD9.396110 accounted**. The build campaign is USD5.433360 of USD6, leaving USD0.566640. Current-log `accounting_complete=true` does not reconcile sibling failures or release their reservations. The author's separation is honest.

Receipts: `/home/dev/ara-work/reports/delta-rereview3-live-audit.json` and its `-audit.py` script. Corpus read-only inventory: `delta-rereview3-corpus.json` and `.txt`; actual PDFs were under `/home/dev/ara-scaffold/literature/fulltext/`, while the review checkout's fulltext directory was empty. The PDF reader also emitted fontTools/encoding warnings; character counts do not certify fidelity. Existing partial diagnostics and operator source inspection remain relevant.

### Executed verification and mutation inspection

- `uv run pytest`: **354 passed, 2 skipped / 356 collected**, exit 0, **158.92 seconds**. Receipt: `/home/dev/ara-work/reports/delta-rereview3-pytest.txt`. The skips are opt-in live checks; no network tests were enabled.
- Independent offline probes: default-profile zero-inference acceptance, faithful empty-range refusal, reconciliation overflow after successful subdivision, oversized-single-source refusal, and fully omitted batch refusal. Script/result: `delta-rereview3-probes.py` / `.json`. These probes use injected counters and placeholder graphs, not live model counts.
- `uv run python tests/integration/negative_controls.py`: **139/139 red, 139/139 restored green**, exit 0. Started only after pytest, corpus/probe processes finished. Receipt: `/home/dev/ara-work/reports/delta-rereview3-negative-controls.txt`; copied results and actual red/green outputs: `/home/dev/ara-work/reports/delta-rereview3-controls/`.

I read the new production mutation definitions and their actual red traces, including these nine controls:

| Mutation | Changed production behavior | Observed red result |
| --- | --- | --- |
| `directional_shared_branch` | Adds reverse premise → inference dependencies | Exact closure assertion gains unrelated `j` and `r`. |
| `directional_shared_qualifier` | Makes qualification links bidirectional | Exact closure assertion gains unrelated `j` and `r`. |
| `reconciliation_obligation_inventory` | Removes exact resolution-inventory requirement | Expected obligation rejection does not occur (`DID NOT RAISE`). |
| `reconciliation_source_pages` | Removes original pages from reconciliation | Provider fake's explicit `[] != ['P', 'Q']` assertion fails; runtime wraps it as accounting-unavailable `BudgetStop`. This proves source transmission, not semantic resolution quality. |
| `measured_count_failure` | Replaces measured response/usage with missing response and reservation | Assertion fails because the `build_t_batch` response is `None`. |
| `nonzero_inference_acceptance` | Disables the inference-count guard | Expected zero-inference rejection does not occur. This control enables the flag explicitly; D3-S1 concerns the normal profile. |
| `root_complete_groups` | Removes complete source-inventory coverage check | Missing omission group reaches construction without the expected rejection. |
| `root_stage_allowance` | Reduces root allowance from 16,384 to 8,192 | Expected context refusal no longer occurs for 190,000 counted input. |
| `construction_patch_retention` | Keeps only patch entries, discarding unchanged candidate entries | The valid-correction test fails with `formalization inventory differs from fixed closure`. |

I also inspected `targeted_inventory_retained` (unknown endpoint after retained nodes disappear) and the strengthened closure/attribution/alignment controls (direct `DID NOT RAISE` at construction, with no uncanned target call involved). All listed restored runs passed.

Direct review of the changed prompts, schemas, source, decision notes and new fixtures found topic-neutral contracts and placeholder-only tests; no new philosophical argument content was found in the tracked diff. This is a review observation, not a claim that keyword search proves semantic absence.

The full suite includes native 53-paper placeholder construction, multiple batches, shared-symbol reuse, deterministic merge/replay, and freeze protections. It does not establish rich real-corpus density, meaningful real cross-batch symbol alignment, semantic fidelity, or the 358-page path. New closure/attribution/citation controls now call the construction boundary and check no freeze, fixing round 2's downstream uncanned-target ambiguity. No lint/typecheck command is configured.

### Placement and readiness

All retained new findings are placed in the seven ranked subsections: **D3-B1** long-source reconciliation; **D3-B2** whole-source construction packing; **D3-S1** full-run policy/configuration; **D3-S2** legitimate empty stages; **D3-S3** catalogue/working-budget planning; **D3-N1** correction limits; **D3-N2** pilot handoff/context and cost. All six D2 dispositions are in the disposition table; structural/provenance and accounting conclusions are in the independent live audit; verification limitations and mutation evidence are in executed verification.

**7 findings, 7 placed.** The two-paper ALT structural proof is accepted. The full 26-PDF extraction/build/pilot chain is **not ready**. Preserve the valid live artifacts; fix or explicitly resolve the full-run blockers and cheap configuration/empty-stage/capacity issues before authorizing expensive corpus work. No branch fixes or paid actions were performed by this review.

Final restoration check: `git status --short` empty; HEAD remains `1b152d9c78c9c30851b48d106359cb796bcedc61`; `git diff --check` passes. No running verification process remains.

DONE delta rereview3 blocking=2 should_fix=3 notes=2 tests=354/356 negctl=pass full_run_ready=no verdict=fix-first
