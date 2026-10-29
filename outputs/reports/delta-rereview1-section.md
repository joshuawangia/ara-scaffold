## Re-review round 1

**Verdict: FIX-FIRST.** At `7aacc81f06736ca9b424a95fdf4a3fb764acb563`, six original findings are resolved under the agreed fix brief: **B2, S1, S2, S3, N1, N2**. B1's missing admission guard and bounded-fixture capacity problem are technically fixed, but **B1 remains open against the operator's argument-structure goal**. The cap defeats that goal for the intended general 30–60-page corpus. I also found **R1**, a strict-refusal regression for entirely visual papers. Logged batched build-T construction is feasible here; it is a medium change, with important identity and downstream-context requirements detailed below.

This round read `/home/dev/ara-work/briefs/gamma-fix-round-1.md` and the author's “Fix round 1” record, then checked the diff and owning runtime/tests directly. The fix brief explicitly preferred a per-paper budget and permitted refusing cache-derived artifacts. Gamma followed those instructions; the B1 objection is to whether that chosen mechanism serves the now-explicit product intent, not to failure to follow the requested implementation. No delegation, live/paid calls, or implementation edits were made. The requested mutation runner was the only temporary tracked-file writer.

### Finding-by-finding disposition

| ID | Disposition | Code and executed evidence |
| --- | --- | --- |
| **B1** | **OPEN: technical guard fixed; intent not satisfied** | `calls.py:144` counts extraction and build-T requests and logs/refuses overflow before dispatch; correction feedback is recounted. Generated-literature build-T now reserves 64,000 output tokens at `calls.py:122`. `test_build_t_counted_context_refusal`, `test_build_t_retry_recounts_feedback`, and `test_capacity53_maximum_through_cli` passed in my full run. The cap and capacity evidence are assessed separately below. |
| **B2** | **RESOLVED by explicit refusal** | `extraction.py:38` identifies accepted cache replays lacking an earlier accepted dispatch for that cache key. `extraction.py:293` refuses their artifact import; `cli.py:127` records the failure; `export.py:75` marks accounting incomplete. `test_fresh_cache_artifact_refused_at_cli_import` passed: original → fresh cached extraction → real CLI import refuses before a model dispatch, while direct original-artifact import remains valid. This implements the smaller fix explicitly allowed by the brief; it does not reconstruct origins. |
| **S1** | **RESOLVED for the agreed coverage heuristic** | `extraction.py:141` inspects paint operations, flags image/form pages with fewer than 200 non-whitespace text characters, and flags painted textless pages. `Paper.readable_pages` excludes them; `calls.py:225` rejects citations crossing unread pages; `extraction.py:258` and `export.py:55` report partial coverage. Sparse-header/image-only/vector tests passed. This remains a heuristic: sufficiently long deficient OCR, layout errors, and other incomplete text are not proven safe. R1 below concerns the new path's strict policy, not failure of its partial label. |
| **S2** | **RESOLVED** | `extraction.py:150` distinguishes blank pages from unread visual content; physical indices are retained at line 154. `test_blank_pages_retained_without_rejecting_paper` passed for blank/P/blank, with citation `p:pdf:2` and diagnostics for pages 1 and 3. No renumbering or whole-paper rejection merely for a blank verso. |
| **S3** | **RESOLVED** | `extraction.py:229` now records only a byte-size warning; the provider estimate at `calls.py:144` decides admission. Large-byte and ligature stress cases with a fitting counted estimate passed; genuine counted overflow refused. The ligature test injects a counted-token estimate and text directly, so it proves admission behavior, not real PDF font/OCR fidelity. |
| **N1** | **RESOLVED** | `extraction.py:298` assigns content-derived receipt IDs and makes same-receipt import idempotent. `export.py:38` separates imported spans into local/inherited tokens, cost, call count and reported human minutes. The lineage test verifies one inherited three-minute event versus one local minute and no duplicate records on re-import. Cross-run aggregation still must deduplicate inherited receipt IDs, as documented. |
| **N2** | **RESOLVED** | `extraction.py:215` detects enclosing-cap insufficiency and prints the explicit warning. The optional extraction profile sets 6,000,000 tokens and USD30 for both cost caps; defaults stay USD10/200,000. `test_preflight_flags_caps_and_profile_is_explicit` passed. The revised conditional estimate is 3,308,479 total tokens and USD25.225915 before retries/fallbacks, within this profile. This remains a planning scenario, not a measured corpus bill. |

Paths in this table are relative to `ara/runtime/`, except config/tests. B2's deliberately restricted recovery policy is material: a failed batch may leave useful cache entries without a completed original artifact. A fresh cached rerun will be refused at import. Retain the original logs; do not strip the header, erase receipts, or describe cache reuse as supported recovery of that failed batch. A later resumable/batched workflow should carry origin receipts or resume the same accounted construction.

### B1: the numeric capacity proof passes, but the cap defeats the argument-structure intent

**Locations:** `schemas/extract_paper.json:54`, `schemas/extract_paper.json:66`, `prompts/extract_paper.txt:4`, `ara/runtime/calls.py:231`, `ara/runtime/extraction.py:261`, `tests/runtime/test_extraction_fix1.py:245`.

The capacity contract is real and locally enforced. The 53-paper test pads every entry to exactly 2,200 escaped bytes and passes through both CLI commands, real ModelCalls/AnthropicProvider request construction and the native engine with an offline SDK transport. Its arithmetic is **53 × 2,200 = 116,600**, plus **7,841** counting-request/wrapper units = **124,441** input units. Add **64,000** output = **188,441**, leaving **11,559** below 200,000. The fake counter uses UTF-8 length plus a message allowance; this is a conservative offline fixture measurement, not a live tokenizer receipt. The 64,000 output allowance is a reasonable engineering allowance for the author's assumed 212 × 250 = 53,000 commitment tokens plus 11,000 headroom, not proof of useful or complete T content.

**Explicit intent judgment: yes, the cap defeats the stated goal as a general extraction policy.** Four items of at most 400 characters allow at most 1,600 text characters before the tighter serialized budget. The prompt actually says to aim below **900 total text characters**, approximately 150 words or 225 ordinary-English tokens under illustrative six-characters/word and four-characters/token assumptions. One 400-character item is only about 65 words. Premises, intermediate conclusions, inference dependencies, qualifications, objections, and the paper's distinctions all compete for that space and the same four item slots. The schema can accept one `claim` and no `argument`; there is no required premise/link structure or coverage check.

My independent exact-size probe found that four placeholder items at the 2,200-byte limit carry **1,560 text characters for a one-character source ID**, but only **993 for a 64-character source ID**. The latter item lengths were 400/400/192/1. Those are serialization measurements, not a suggested allocation. At the existing planning density, a 30–60-page paper is 45,000–90,000 input tokens; a requested 225-token selection is roughly **0.25–0.5%** of that length. Compression ratio alone does not prove a lost argument, and a very simple argument could fit. It does show why this cannot be accepted as a generally adequate representation of the chosen papers' argument structures without substantially different evidence.

The important architectural fact is that this limit applies to **the saved source extraction itself**. `<id>.extraction.json` at line 261 stores the same capped `PaperExtraction`. There is no richer argument artifact behind the compact view. Logs preserve the PDF page text and rejected responses, but later runtime stages do not reconstruct a rich argument inventory from them. Keeping every source ID and avoiding literal string slicing does not preserve the omitted premises and distinctions: the prompt explicitly requests their reduction before any downstream model can use them. The capacity test returns repeated P text with atomic formulas and proves transport/size/citations, not argument preservation.

**Fix direction:** Preserve richer, schema-validated per-paper argument records, with page-linked premises, stated inference links, conclusions and distinctions/qualifications. Distinguish an author's inference from the deterministic engine's license for a newly constructed argument. Build a bounded, audience-relevant T from that evidence in logged batches; retain the rich records for source inspection and any logged source-context use. Increasing the cap somewhat without preserving structure merely moves the same risk.

### R1 — SHOULD-FIX regression: strict refusal is bypassed for an entirely visual paper

**Locations:** `ara/runtime/extraction.py:244`, `ara/runtime/extraction.py:247`, `README.md:185`.

**Failure scenario:** Invoke `ara extract --missing refuse` on an image-only PDF. The new coverage branch records `partial`, `reason=no_readable_pages`, `items=[]`, then continues without testing `missing`. The command exits 0 and publishes literature despite extracting nothing from that paper. An all-blank PDF still takes the unavailable branch and refuses. The previous head treated textless scans as unreadable and honored the strict flag; the README still says missing/unreadable PDFs stop under that option.

**Independent receipt:** A generated image-only placeholder PDF through the real `cli.main` returned **0**, published the artifact, and made zero provider dispatches. A wholly blank PDF in the same harness returned **2** and published no artifact. This is not disguised as a successful extracted paper—the partial marker is honest—but it bypasses the operator's requested refusal policy. Existing new image-only tests exercise only the default policy.

**Fix direction:** Apply strict refusal at least to `partial` papers with no readable pages, recording diagnostics before stopping and publishing no collection. Specify whether strict mode also refuses any incomplete paper, and test both wholly visual and mixed readable/visual inputs through the CLI. Preserve default partial reporting rather than reintroducing silent omission.

### Feasible alternative: rich artifacts, logged build-T batches, deterministic merge, one freeze

**Assessment: feasible, medium scope.** The needed runtime seams already exist. `ModelCalls.call` supplies schema validation, cache keys, retries, budget reservation/actuals, MODEL receipts and provider streaming. `ModelCalls.build_t` already validates the batch's citation set. `CommitmentSet` is immutable and enforces unique IDs (`ara/types.py:174`). `prepare` freezes/persists T and only then proposes targets (`orchestration.py:39`). Construction can make multiple logged calls internally, merge their provisional outputs, and reach that single existing freeze boundary. Search must never see a partially built T. Update the documented “T built once” rule to clarify one construction lifecycle and one final freeze, not one provider request.

One workable **capacity scenario, not an implemented design or measured forecast**, is:

| Quantity | Arithmetic |
| --- | ---: |
| Rich extraction material allowance across 53 papers | 53 × 8,192 = **434,176 tokens** |
| Six papers per nominal build-T batch | 6 × 8,192 = **49,152 input tokens** |
| Batch input with illustrative schema/topic/projection overhead | 49,152 + 8,000 = **57,152** |
| Input plus 64,000 output allowance | 57,152 + 64,000 = **121,152**, below 200,000 by **78,848** |
| Number of batch calls | ceil(53 / 6) = **9**: eight six-paper batches and one five-paper batch |
| Total batch input, counting overhead nine times | 434,176 + 9 × 8,000 = **506,176 tokens** |

The existing 8,192 extraction output allowance also includes thinking; the entire allowance will not necessarily become saved material. Using it as a material upper-bound scenario is conservative for assembly, not a promise of 8,192 useful tokens per paper. Actual JSON escaping, topic, symbol catalogue and correction feedback must be counted in each full request. Pack batches against counted tokens, not a fixed six-paper rule; page-range extraction/batch subdivision can handle genuinely larger sources without shrinking away required structure. If useful material requires raising extraction output allowances, revisit the USD30 extraction budget explicitly.

**Do not stop the design at the merge.** `propose_targets`, `propose_cuts`, `map_leaf` and `answer_cq` currently resend the entire T (`calls.py:248`, `260`, `270`, `277`), and the new context guard only covers extraction/build-T. If batch outputs average 20 commitments per paper at 250 serialized tokens each, the merged T is **53 × 20 × 250 = 265,000 tokens**, already too big for those later requests. Batched construction alone would move the failure downstream.

Two sound choices are available. For the smaller change, have the model select an audience/topic-relevant working T from the rich records with a counted total budget, while preserving all source argument structure in separate immutable artifacts. For an illustrative fit, **8 commitments per paper × 53 × 200 serialized tokens = 84,800 tokens**; plus 10,000 for goal/bank/wrappers and 8,192 output gives **102,992**. These are sizing assumptions, not a new hard per-paper evidence cap: source evidence stays rich, and T allocations can vary by relevance. The selected T must still express the needed premises/inferences/qualifications, and fuller source context must be explicitly passed or retrieved if search needs it—merely saving an unused artifact is not enough. If every extracted commitment must remain in T, keep the full frozen T in the engine and introduce counted, deterministic source/T-context selection for model requests, with IDs checked against the complete T. That option touches more search-call inputs.

For the illustrative 84,800-token working T, nine batches cost **506,176 × USD5/1M + 84,800 × USD25/1M = USD4.65088** for their input/output content, before thinking, retries, fallbacks, symbol alignment or later search. Reserving all nine 64,000-token output allowances gives **USD16.93088** at the same rates, excluding fallback excess and retries. These are incremental build-T numbers; extraction and repeated full-T search calls are additional. Both token accounting and rate assumptions come from the current config, not live measurements.

The implementation needs these specific pieces:

1. **Rich source contract and provenance.** Replace the four-item summary contract with structured, page-linked argument records; retain attribution and coverage diagnostics. Version the artifact/schema so the richer source and any compact working projection are distinguishable. Preserve the original extraction receipts or fail closed under the current B2 policy.
2. **Deterministic batch plan.** Stable source ordering and content hashes, counted request sizing, explicit per-batch source IDs, and call/cache identity including the plan version, topic/audience and any shared symbol catalogue. Each batch uses the existing ModelCalls path; failed construction publishes no frozen T. Log the plan and each accepted batch hash.
3. **Safe deterministic merge.** Assign globally stable commitment IDs, validate citations against the relevant source evidence, keep distinct provenance/attribution, and do not silently drop contradictions or merge semantically similar text. Prefixing IDs alone is insufficient: two independent calls can use the same formula atom name for different propositions. Define a shared symbol contract or source-scoped symbols with explicitly logged model-produced alignments. Deterministic code can validate/apply those mappings; it must not invent philosophical equivalences. Do not deduplicate solely by formula and lose a source citation.
4. **One freeze and downstream capacity.** Merge validated provisional results into one `CommitmentSet`, log the batch-to-final mapping, persist once at the current `prepare` boundary, then start target/search work. Count every model request that carries T/source context. Either bound the selected working T before freeze or select bounded views of a larger immutable T; never mutate T in response to a search result.
5. **Native proofs.** Extend the 53-paper CLI test to rich records and multiple build-T calls; assert one freeze, all intended source IDs, stable merge under reordered batch completion/cache replay, duplicate-ID/symbol/citation rejection, explicit failure of an oversized batch or downstream request, preserved HUMAN/MODEL receipts, and the strict partial-paper policy. Add matching production-wire negative controls. Include a placeholder argument graph with multiple premises/intermediate links/distinctions; repeated P paragraphs do not test structure preservation.

A bare loop plus ID-prefixed union is small, but it is not the complete change above. I estimate **roughly 3–5 engineer-days including local tests/review**, on the order of **500–1,000 production lines plus 400–800 test lines across about 8–12 files**, for richer contracts, batching, merge/identity rules, bounded downstream inputs and provenance/capacity proofs. This is a rough planning estimate, not a delivery commitment. A general retrieval subsystem or semantic ontology reconciliation would expand it; neither a new provider integration nor an engine licensing rewrite is inherently required. Real-PDF quality/provider acceptance remains a separate executed-validation step.

### Independent test receipts and regression coverage

- `uv run pytest`: **280 passed, 2 skipped, 282 collected**, exit 0, **72.27s**. Receipt: `/home/dev/ara-work/reports/delta-rereview1-pytest.txt`. The skips are the opt-in live tests. The maximum-size CLI capacity case is included.
- `uv run python tests/integration/negative_controls.py`: **82/82 red, 82/82 restored green**, exit 0. Receipt: `/home/dev/ara-work/reports/delta-rereview1-negative-controls.txt`; copied per-control logs and `results.json` are in `/home/dev/ara-work/reports/delta-rereview1-controls/`. This round ran the mutation command only after pytest and the independent probes finished; there was no overlapping full-suite run.
- Independent boundary probes: exit 0 with network connections forbidden. Receipts: `/home/dev/ara-work/reports/delta-rereview1-probes.py`, `.json`, `.txt`. These reproduce strict-image refusal bypass, verify its blank-page control, measure four-item text capacity, and calculate the alternative sizing/cost scenario. They do not execute the proposed batching design.
- Final head/restoration: HEAD remained `7aacc81f06736ca9b424a95fdf4a3fb764acb563`; `git status --short` was empty and `git diff --check` exited 0 after all 82 controls restored their changes.

I read nine fix-round mutations and their actual red receipts. These spot checks distinguish the property tested from broader claims:

| Control | Mutation and observed failure |
| --- | --- |
| `build_t_context` | Remove build-T from context guarding; the test reaches an uncanned provider request and gets an accounting STOP instead of the expected pre-dispatch context refusal. Restored code verifies zero dispatches. |
| `extraction_blank_pages` | Make any blank diagnostic render the paper unavailable; the blank/P/blank intake assertion fails. |
| `extraction_partial_status` | Label the mixed visual/text paper extracted; the explicit partial-status assertion fails. |
| `extraction_counted_not_bytes` | Reintroduce a hard byte STOP; both fitting-count Unicode/ASCII cases fail. |
| `extraction_cache_lineage_import` | Disable the missing-origin check; expected MissingExtractionLineage is not raised. |
| `extraction_local_inherited_totals` | Count imported events as local; local USD0 becomes USD0.00175. |
| `extraction_batch_profile` | Skip profile application; the expected USD30 cap remains USD10. |
| `extraction_import_idempotence` | Disable duplicate receipt suppression; the log doubles from 10 records to 20. |
| `extracted_t_output_capacity` | Revert extracted build-T to the ordinary allowance; the fake SDK explicitly requires `max_tokens == 64000` and the CLI fails. This proves forwarding the configured allowance, **not** that a real model needs 64,000 tokens or can deliver adequate T content in that allowance. |

All nine restored green; none failed from collection errors. The full suite and controls do not exercise strict refusal on visual-only partial papers, which is why R1 remains despite their green result.

Changed fixtures/prompt/docs remain topic-neutral and placeholder-only. The raster/glyph cases contain no philosophical content. No new paid/API tests were enabled. The capacity fake supplies accepted responses and conservative counts; neither that fake nor green mutations establishes real argument extraction quality. Inventory found no PDFs in the review checkout's fulltext directory or `/home/dev/ara-scaffold/literature/fulltext`. No real-paper or full-corpus success is claimed.

### Round-1 placement and next step

| Finding or action-changing conclusion | Placement in this section |
| --- | --- |
| B1 numeric safeguards pass, but cap defeats argument-structure intent | Disposition table; B1 intent assessment |
| B2 resolved by refusing missing lineage, with constrained failed-batch recovery | Disposition table and following recovery paragraph |
| S1 heuristic fix and remaining source-quality limits | Disposition table; evidence limits |
| S2 blank-page fix | Disposition table |
| S3 counted admission fix and limited Unicode proof | Disposition table |
| N1 inherited/local accounting and deduplication | Disposition table |
| N2 explicit profile/cap warning, conditional budget | Disposition table |
| R1 strict policy bypass | R1 regression subsection and independent probe receipt |

The batch feasibility, arithmetic, final-T size risk, symbol-identity requirement and implementation estimate are all carried in B1's “Feasible alternative” subsection. **8 findings, 8 placed.** Next step: revise B1 around preserved argument structure and a counted construction/search path, fix R1, then rerun affected tests and controls before the real run. This re-review does not authorize or perform that implementation.

DONE delta rereview1 resolved=B2,S1,S2,S3,N1,N2 open=B1,R1 cap_defeats_intent=yes batched_build_t=feasible:medium verdict=fix-first
