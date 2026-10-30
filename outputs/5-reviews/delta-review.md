# Delta independent review: per-paper extraction

**Verdict: FIX-FIRST for the intended 53-paper real run.** The native integration and tested guards work, but the assembled literature can exceed build-T's context without local admission protection, and cached re-extraction loses the original log lineage needed for the competition methodology. PDF intake also needs work before relying on it for a mixed real corpus.

Reviewed `/home/dev/ara-work/gamma`, branch `feat/paper-extraction`, head `893b3794bab3ebd349af2be54cb809ecd4d051d9`, base `5998c90b990b843ce4da111bbddfa04f7080ca6b`. Read the author brief before the author report; read AGENTS.md, PLAN.md, README.md, DECISIONS.md (including GX1–GX5), the changed files, and the native CLI → orchestration → ModelCalls → provider/cache/budget/log/export path. Review performed independently, without delegation or implementation edits. Only the requested negative-control runner temporarily mutated tracked files; it restored them. Final tracked/untracked status was clean and HEAD unchanged. No live or paid calls; real spend USD0.

## Ranked findings

### B1 — BLOCKING: the combined literature can exceed context, and build-T has no context admission guard

**Locations:** `ara/runtime/extraction.py:169`, `ara/runtime/calls.py:143`, `ara/runtime/calls.py:222`, `ara/runtime/orchestration.py:40`, `config.yaml:44`, `config.yaml:64`.

**Failure scenario:** With 53 accepted papers at the 8,192-token output allowance, the upstream allowance totals **53 × 8,192 = 434,176 tokens**. That is **2.17 times** the 200,000-token context, before assembly metadata, citation fields, build-T instructions/schema, JSON escaping and build-T output. Output allowance includes any model thinking and need not all become literature, so this is a capacity scenario, not a prediction of typical output length. Nonetheless, there is no enforced collection-size limit. Even ignoring all wrapper overhead, with 8,192 tokens reserved for build-T output, the collection must average less than **(200,000 − 8,192) / 53 = 3,619.02 tokens per paper**. The branch neither sizes nor reduces the assembled collection.

`prepare` passes the entire literature into one `build_t` call. The context guard in `_execute_once` applies only to `extract_paper`; monetary/token-run admission is not a per-request context check. With sufficient run caps, an over-context build-T estimate proceeds to dispatch. My offline boundary probe supplied an estimate of 434,176 input tokens and observed one build-T dispatch and accepted mock output despite the 200,000 context setting. This proves the missing guard, not real-provider acceptance.

**What happens now:** No application truncation or batching occurs. Default run caps can stop earlier; with raised caps, token counting or the provider can reject the oversized request. A failure after `call_start` enters existing incomplete/unknown-actual accounting and STOP handling; a counting failure occurs before dispatch and is reported as a runtime error. Neither path constructs T. The author discloses this gap, but disclosure does not make the planned full batch usable.

**Fix direction:** Count the complete build-T request and enforce the context limit before dispatch. Add a logged, provenance-preserving model reduction/batching strategy with a final single frozen T, or an explicit, measured extraction-output budget that guarantees the chosen corpus fits. Do not silently omit papers or ask a human to write substantive summaries. Verify the assembled 53-paper capacity path offline before scheduling paid extraction.

### B2 — BLOCKING: cache replay drops original extraction receipts and human provenance

**Locations:** `ara/runtime/calls.py:131`, `ara/runtime/calls.py:138`, `ara/runtime/calls.py:197`, `ara/runtime/cache.py:31`, `ara/runtime/extraction.py:174`, `ara/runtime/extraction.py:197`, `ara/runtime/export.py:35`.

**Failure scenario:** Extract paper P in run A, then follow the documented recovery/reuse workflow: start fresh run B using the same cache and use B's literature for the downstream run. Cache entries contain only `raw`, with no pinned origin log/receipt. Replay logs a new MODEL event with zero event usage/cost. B's provenance sidecar points only to B, so downstream import cannot recover A's original timestamp, prompt history/rejected attempts, pricing/configuration or human actions from its log.

**Executed evidence:** A mock original extraction recorded 100 input/50 output tokens, USD0.00175 simulated cost, and a three-minute HUMAN event. Re-extraction made zero additional provider dispatches. Importing the re-extraction artifact produced an extraction summary of one cache replay, zero dispatches, zero tokens, USD0, and zero human minutes; the cache file had only the `raw` key. The raw successful response still contains its usage, but there is no original log linkage and no original HUMAN receipt. Zero *new spend* is correct; treating that as a complete account of the artifact's production is not. The exporter nevertheless marks recorded accounting complete.

**Fix direction:** Preserve a stable origin receipt/log checkpoint in cached results, including original attempts and human provenance, and import verified origin receipts transitively with deduplication. Separately report new spend, inherited production spend, and cache access. Replaying a cache must not charge the provider again, but must retain the methodology of how the reused artifact was produced. Add a fresh-run cache → artifact → CLI import test; the current replay test stays in the original log and cannot catch this loss.

### S1 — SHOULD-FIX: a nonempty header can disguise a largely unread image page as usable source text

**Locations:** `ara/runtime/extraction.py:94`, `ara/runtime/extraction.py:96`, `ara/runtime/extraction.py:163`.

**Failure scenario:** A scanned page contains a raster body and a selectable page number/header, or a deficient OCR layer provides only a few characters. `extract_text()` returns nonempty text, so the whole paper is considered available. The model receives that text only; it never sees the omitted raster content. If it returns a structurally valid item, the paper becomes `extracted`. This is an input omission that the output schema/page bounds cannot detect.

**Executed evidence:** A generated placeholder PDF with a raster plus selectable `P` passed intake with `unavailable=None` and page text exactly `P`. The same raster without selectable text fell back. This establishes the predicate's blind spot; it does not estimate the prevalence of partial OCR in the real corpus.

**Fix direction:** Add an explicit text-quality/coverage preflight and diagnostics for image-dominant pages, sparse text, and suspect OCR. Route such pages to logged OCR/document processing or a clear unavailable/partial status that cannot be mistaken for a complete extraction. Preserve page positions and source hashes. No heuristic proves semantic completeness; retain that limitation and test representative scans when available.

### S2 — SHOULD-FIX: one harmless blank page rejects every substantive page in a paper

**Locations:** `ara/runtime/extraction.py:95`, `ara/runtime/extraction.py:103`.

**Failure scenario:** A perfectly readable paper has a blank verso, blank cover or separator. `any(not page.text.strip())` discards all page text and returns `record only, not extracted`; strict mode stops the batch. The reason is just `unreadable_pdf:ValueError`, which also describes encryption and empty-text failures, so the operator cannot distinguish the cause from the outcome alone.

**Executed evidence:** A generated two-page PDF containing `P` followed by a genuinely blank page returned `unreadable_pdf:ValueError`. The existing blank-page test and negative control deliberately enforce this behavior. GX2 documents it, but it is too strict for ordinary PDFs.

**Fix direction:** Distinguish an actually blank page from a page with unread visual content. Keep physical page numbering, record blank pages explicitly, and allow readable substantive pages through. Do not fix this merely by deleting the empty-text check: a scan would then be silently skipped. Emit a precise, content-safe reason code and affected page numbers.

### S3 — SHOULD-FIX: the byte-based preflight rejects many plausible 35–60-page papers before accurate token counting

**Locations:** `ara/runtime/extraction.py:139`, `ara/runtime/extraction.py:142`, `ara/runtime/providers.py:165`.

**Failure scenario:** UTF-8 bytes are treated as tokens in the hard context decision, even though the production provider subsequently has a token-counting path. At the configured planning density of 1,500 tokens/page and an illustrative four UTF-8 bytes/token, a 35-page paper is roughly 52,500 text tokens but 210,000 text bytes. It falls back before token counting despite being well below 200,000 actual tokens under that assumption. Sixty pages would be about 90,000 text tokens versus 360,000 bytes. The prompt already includes the local schema, and the preflight additionally appends schema bytes, making the check still more conservative.

**Executed evidence:** Placeholder inputs with 6,000 text bytes/page produced these exact local bounds, including output allowance and overhead:

| Pages | Bound used as tokens | Decision at 200,000 |
| --- | ---: | --- |
| 30 | 192,107 | Pass |
| 35 | 222,217 | Fallback/refuse |
| 60 | 372,767 | Fallback/refuse |

These are byte-bound measurements, not measured natural-language token counts. They show the effective size cliff. Ligatures with sound Unicode mappings can remain readable to pypdf; broken mappings/order are not checked, and multibyte characters further inflate the byte bound. Pure image scans always fall back without OCR. Born-digital 30-page sources may pass, while longer/dense sources can fail despite fitting a model context. There are no real PDFs in the inspected fulltext directories, so a corpus pass percentage is unknown; the implementation does not justify assuming most of the 53 will pass.

**Fix direction:** Use accurate counted tokens for the hard request decision, retaining bytes as a conservative planning warning or initial sizing heuristic. Keep explicit refusal or implement logged page-range splitting for genuinely oversized papers. Recheck correction prompts, schema and output allowance on every attempt. Add realistic length and Unicode/ligature fixtures without substantive philosophical content.

### N1 — NOTE: imported receipts are repeated in each downstream methodology, not aggregate-deduplicated

**Locations:** `ara/runtime/extraction.py:197`, `ara/runtime/export.py:37`, `ara/runtime/export.py:61`.

**Failure scenario:** Two downstream runs import the same original extraction artifact. Each gets the full upstream MODEL and HUMAN events and includes their costs, dispatch count and human minutes in totals. Summing the two methodologies counts the same original work twice. Within a normal single CLI import I found no extra duplication; this is the documented reuse policy, and the import event explicitly says these are reused receipts. The import helper itself is not idempotent, although the current CLI calls it once.

**Fix direction:** For competition-level accounting, retain stable origin IDs and expose local versus inherited totals so aggregation can deduplicate reliably from logs. Until then, preserve original logs and do not sum downstream totals as new spend. This is distinct from B2: importing A directly preserves its evidence, whereas importing a fresh cache replay of A loses the lineage.

### N2 — NOTE: the extraction cap does not make the documented full-batch planning scenario admissible

**Locations:** `config.yaml:6`, `config.yaml:7`, `config.yaml:63`, `ara/runtime/budget.py:111`, `ara/runtime/extraction.py:127`.

**Failure scenario:** The operator sees the USD30 extraction cap and an approximately USD24.99 batch estimate, but leaves the enclosing defaults at USD10 and 200,000 total tokens. The author's stated scenario is 2,826,285 input plus 434,176 output tokens, **3,260,461 combined**, at USD24.985825 before retries/fallbacks. The default enclosing caps will stop the batch. These are protective stops, not hidden overrun bugs; actual oversized charges are also checked after each response, and imported receipts consume downstream budget.

**Fix direction:** Use an explicit reviewed batch configuration with adequate enclosing token/cost caps and downstream headroom. Make the preflight show that the planned batch exceeds those caps rather than merely printing the separate numbers. Do not treat this conditional estimate as a quote: PDF availability, conservative refusal, actual output, retries and server fallbacks change it. Raising caps does not resolve B1.

## Verification and rule compliance

Executed the requested commands myself at the specified head:

| Check | Independent result | Receipt |
| --- | --- | --- |
| `uv run pytest` after all mutations were restored | **265 passed, 2 skipped, 267 collected**, exit 0, 37.81s | `/home/dev/ara-work/reports/delta-review-pytest.txt` |
| `uv run python tests/integration/negative_controls.py` | **63/63 red, 63/63 restored green**, exit 0 | `/home/dev/ara-work/reports/delta-review-controls/results.json` and individual `*-red.txt` / `*-green.txt` |
| Independent offline boundary probes | All assertions passed, exit 0; network explicitly forbidden | `/home/dev/ara-work/reports/delta-review-probes.py`, `.json`, `.txt` |
| Final revision/restoration | HEAD still `893b3794bab3ebd349af2be54cb809ecd4d051d9`; `git status --short` empty; `git diff --check` exit 0 | Executed after both requested commands |

The two skips are the existing opt-in live-provider tests. No live test was enabled. The new extraction suite blocks socket connections and generates placeholder PDFs. My extra probes use only P and synthetic raster data, run through the production boundaries with mock transport, and write outside the branch. They do not validate live model fidelity or API acceptance.

Test-run bookkeeping: I initially started pytest and the mutation runner concurrently. That pytest invocation saw the deliberately disabled writer-marker guard and reported four failures. It is discarded as contaminated evidence, not attributed to this head. I waited for the mutation runner to finish, verified restoration, and reran the complete suite alone; the authoritative result is the clean 265-pass receipt above. The mutation runner's own targets are isolated subprocesses and every restoration was green.

I read the production mutations and the resulting red failures for eight controls, exceeding the required five:

| Control / definition location | Actual mutation | Observed red failure |
| --- | --- | --- |
| `extraction_schema`, `tests/integration/negative_controls.py:68` | Skip the local validator only for extraction | Extra response field accepted; expected Rejected not raised |
| `extraction_source`, line 70 | Replace top-level source identity predicate with true | Wrong source accepted; expected Rejected not raised |
| `extraction_page_bounds`, line 72 | Replace page range predicate with true | Out-of-range page accepted; expected Rejected not raised |
| `extraction_fallback_marker`, line 75 | Mark unavailable paper as extracted | Status assertion sees `extracted` instead of record-only |
| `extraction_pdf_cache_identity`, line 85 | Remove PDF hash from request inputs | Changed PDF reuses cache; dispatch count is 1 rather than 2 |
| `extraction_provenance_integrity`, line 86 | Disable artifact/log reconstruction check | Modified text accepted; expected ValueError not raised |
| `extraction_ai_label`, line 88 | Put extracted literature in the HUMAN input event | Native CLI test detects AI literature under HUMAN |
| `extraction_t_citation`, line 89 | Disable allowed-citation membership | Fallback source citation accepted; expected Rejected not raised |

These are behavioral failures, not collection errors. Each selected control was restored green. Some other controls have narrower implications than their names might suggest: disabling the local oversize fallback can still hit the independent provider-context guard; the negative control proves the local fallback path, not removal of every size safeguard. None of these controls proves aggregate build-T sizing or original-log provenance on a fresh cache replay.

The diff adds no substantive philosophical propositions, examples or views. New prompts/schema/docs are topic-neutral; fixture content is placeholder-only. I reviewed changed source, prompt, schema, tests, documentation and the branch's single commit subject. The committed fulltext tree contains only `.gitkeep`; the new PDFs and output patterns are ignored. Existing bibliographic titles are not new philosophical arguments. This is direct review evidence, not a claim that text search proves semantic absence.

## Behavior that is working, and limits of the verdict

The feature uses the native provider/cache/budget/logging boundary. Schema validation, source/item identity, page bounds and nonblank item text precede cache admission. PDF bytes, extracted pages and record metadata enter cache identity. Output-token stops and provider refusals are rejected before content acceptance. Missing/unreadable/oversize input has an explicit record-only outcome, strict refusal publishes no literature, and model/validation/budget failure records a failed paper and stops. No source or output slicing was found; the partial-input risk is S1.

The sidecar pins the completed log prefix and validates exact reconstruction of the literature. The direct artifact → CLI path preserves SYSTEM/MODEL labels, retains operator commands/manifest as HUMAN, and excludes AI literature from HUMAN input. Build-T rejects fallback/invented citation IDs and an all-record-only collection before building T. Accepted page IDs and attribution enums do not establish semantic support, completeness, or correct attribution; real source/output inspection remains unexecuted. No real PDFs were present in either the review checkout or `/home/dev/ara-scaffold/literature/fulltext` at review inventory. Thus passing offline tests do not demonstrate that the operator's actual corpus can be extracted and assembled into a usable T.

The real-run merge verdict remains **fix-first**. Resolve B1 and B2, address the PDF intake limitations with evidence appropriate to the selected corpus, then repeat the affected native-path and accounting checks. Gamma should make the implementation changes; this review leaves the branch intact.

## Finding placement and handoff record

| Finding | Deliverable placement |
| --- | --- |
| B1: aggregate context/dispatch gap and no full-batch T proof | B1; real-run verdict |
| B2: cached re-extraction loses production provenance | B2; independent probe receipt |
| S1: partial image/text page can pass | S1; behavior limits |
| S2: blank page discards usable paper | S2 |
| S3: byte-bound size cliff, scan/ligature limitations and unmeasured real corpus | S3; behavior limits |
| N1: repeated imports require aggregate deduplication | N1 |
| N2: default caps cannot admit the planning scenario | N2 |

**7 findings, 7 placed.** Current revision, executed receipts and all action-changing findings are preserved here. Next unresolved step belongs to the author: fix the two blockers and demonstrate PDF/corpus suitability before the real run. Test totals in the completion line use collected cases as the denominator: 265 passed of 267, with two intentional skips and zero failures.

DONE delta review blocking=2 should_fix=3 notes=2 tests=265/267 negctl=pass verdict=fix-first report=/home/dev/ara-work/reports/delta-review.md


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

## Re-review round 5

Reviewed `feat/paper-extraction` at `4b94f8e4a1053661d6dc36e3ec6d8bbc2b8d6405`, against `be8c2c2ee2adaf491a8a31bb38640d40e287cebc`, in `/home/dev/ara-work/gamma`. Scope is the D4-B1 repair and the round-5 brief's explicit continuation-bound requirement. Solo, report-only review; no branch changes, implementation edits, delegation, network calls or paid generation. The negative-control runner temporarily mutates and restores production files as required. Historical review sections remain unchanged.

**Verdict: fix-first.** D4-B1's silent inventory loss is resolved, but the new expanding queue lacks the requested per-paper count and monetary bounds. Shared extraction/run budgets still protect total charged spending; they do not allocate a bounded continuation allowance to each paper. One blocking finding, no additional should-fix findings; full-run readiness remains **no**.

### Blocking finding D5-B1 — descendants bypass the only local continuation bound

**Priority: blocking for this brief and the full extraction run.** Locations: `ara/runtime/reconciliation.py:21`, `:44`, `:55`, `:69`, `:72`, `:87`; `ara/runtime/budget.py:98` and `:102`.

`reconciliation_context_requests` limits explicit context requests for one obligation. Its `requests` set resets for every queue entry. `turn` increments but is never compared with a ceiling. Every accepted response can resolve its supplied obligation and append a fresh `new_gaps` entry; the next obligation starts another traversal. Such a response does not need a context request. No total per-paper continuation count exists, and budget admission sums the whole extraction stage/run rather than a paper-specific allowance. Each descendant has a fresh identity and therefore a fresh prompt/cache key. Neither context fit nor cycle detection bounds this chain.

**Executed reproduction:** `uv run python /home/dev/ara-work/reports/delta-rereview5-probes.py` invokes production `extract` with the full extraction profile, a one-page placeholder paper, a network-forbidden mock provider, and synthetic counted usage. Initial extraction discovers Q. Each following response resolves its supplied ID using accepted evidence and discovers another Q under a distinct runtime identity. With `reconciliation_context_requests=0`, USD125 enclosing/extraction caps and a 12M token cap, **41 provider dispatches / 40 reconciliation calls** succeed; 40 discoveries and 40 resolutions are retained and literature is published. The probe stops inventing gaps after 40 solely to terminate the demonstration; production has no corresponding count check. Repeated equal descriptions are intentionally distinct, so deduplicating them would be the wrong repair.

A second run uses the same response generator and USD0.81 shared caps. It stops on the seventh attempted dispatch, after **6 dispatched responses, 6 discoveries and 5 resolutions**, with `BudgetStop: extraction cost cap: request reservation exceeds remaining cost`. Synthetic actual charges total USD0.0105; the next USD0.8005 reservation would exceed the cap. One pending ID remains auditable, a STOP/partial receipt is saved, and no literature is published. These are mock charges, not paid usage. This proves shared budget admission remains effective; it does **not** show unbounded dollar spending past a configured run cap. The defect is that a single paper can keep consuming the corpus allowance without an independent count or paper spending stop.

**Fix direction:** introduce validated finite per-paper continuation-count and monetary limits; enforce them before dispatch across graph review, ordinary evidence windows, explicit context requests and all descendant obligations. Count paid retry/correction attempts within the applicable allowance, retain the existing global reservation checks, and preserve accumulated discoveries/resolutions plus an explicit STOP identifying the paper and pending IDs when a local limit refuses. Do not discard gaps, merge descriptions, or mark coverage complete at the limit. Add a resolving-plus-new-gap chain regression that reaches the count limit while budget remains, a separate paper-budget refusal test, and a multi-paper test proving counters reset only at the paper boundary. Mutate each new guard and require red/restored-green receipts.

Own probe receipts: `delta-rereview5-probes.py`, `.json`, `.txt` in `/home/dev/ara-work/reports/`; the JSON links both complete event/cache/artifact directories.

### D4-B1 disposition — inventory loss resolved

The wire now separates `pending_obligation_ids` and structured `new_gaps`. `ara/runtime/calls.py:288` checks coverage consistency; `:338` requires every supplied ID to occur exactly once in the pending/resolved partition; `:344` requires nonempty resolution evidence drawn from accepted/current validated IDs. `ara/runtime/extraction.py:131` assigns source/window/turn/index IDs and appends discovery events without comparing description text.

`ara/runtime/reconciliation.py:55–60` appends every accepted continuation's new obligations to both cumulative inventory and the queue before processing the current resolution. This includes gaps returned while resolving an existing gap, and descendants of those gaps. At `:100–103`, exhausted windows refuse; successful publication requires the resolution-ID set to equal the entire accumulated inventory. Discovery/resolution events live in the existing hash-chained log; per-window snapshots preserve supplied/new obligations. The final cumulative obligations JSON is produced only after successful draining. A refusal's incomplete inventory is reconstructible from receipts even though no final ledger is published.

The eight direct parameterized regressions exercise discovery while pending or while resolving, equal or distinct descriptions, and either original-only refusal or both-resolved success. The ninth covers review-discovered gaps and multiple descendant generations. They assert counted admissions, four MODEL receipts in the direct cases, accepted evidence IDs, stable provenance IDs, immutable snapshots and absence of publication on refusal. The independent 40-generation probe also confirms distinct identities and complete retention for equal descriptions. Thus the original disappearing-R counterexample is repaired; it has not merely moved into a final merge check.

### Executed verification and mutation evidence

Full `uv run pytest`: **382 passed, 2 skipped / 384 collected**, exit 0, 247.91 seconds. The two skips are opt-in live checks. Receipt: `/home/dev/ara-work/reports/delta-rereview5-pytest.txt`. The new round-5 file contributed nine passing cases. Independent probe and saved-plan audits also exited 0 before mutation testing began.

Then `uv run python tests/integration/negative_controls.py`: **156/156 red, 156/156 restored green**, exit 0. No pytest/probe/plan audit ran concurrently with the mutation runner. Full receipt: `/home/dev/ara-work/reports/delta-rereview5-negative-controls.txt`; copied individual red/green traces and `results.json`: `/home/dev/ara-work/reports/delta-rereview5-controls/`. Both new controls failed with pytest exit 1 and restored with exit 0; their actual traces were read, not inferred from the summary.

After controls, `git status --short` was empty, `git diff --exit-code` passed, and HEAD remained `4b94f8e4a1053661d6dc36e3ec6d8bbc2b8d6405`. The previously accepted frozen T remained at SHA256 `25a7ec8c35d393b230738e6008467d70926697db6bed1f91c72b5edcd39cb3a4`; no new construction was performed.

Both new mutation definitions were read in `tests/integration/negative_controls.py:202–209`:

- `new_gap_inventory` changes the production ingestion argument from `ids, new_gaps)` to `ids, [])`, targeting the original-only refusal case `[False-2-R]`. Fresh red trace: `Failed: DID NOT RAISE Rejected` at `tests/runtime/test_extraction_round5.py:48` (0.42 seconds). Restored: 1 passed (0.52 seconds).
- `new_gap_queue` removes `queue.extend(new_obligations)`, targeting the both-resolved case `[True-2-R]`. Fresh red trace: `Rejected: unresolved obligation inventory at merge` from `ara/runtime/reconciliation.py:101`, reached by the positive test at line 45 (0.44 seconds). Restored: 1 passed (0.52 seconds).

These controls establish ingestion and processing independently. They do not cover a per-paper continuation limit; no such guard exists. Other than D5-B1, no regression was found in this narrow diff review and the executed checks. Passing offline tests certify structural accounting and refusal paths, not semantic sufficiency of the model-selected evidence.

### Free-plan confirmation and retained limits

Independently audited the saved round-5 free plan with `delta-rereview5-plan-audit.py` (network forbidden); receipt `.json` and full output `.txt` are alongside this report. Checked the log chain, actual PDF hashes, exact readable-page partitions, every range's saved count, context fit and arithmetic. No token-counter or generation service was called during this review.

- 26 PDFs; 1,379 physical / 1,368 readable pages; 66 initial ranges.
- 1,607,572 counted initial input tokens, 1,641,600 expected output tokens. Initial cost: `(1,607,572 × 5 + 1,641,600 × 25) / 1,000,000 = USD49.077860`.
- Saved graph-review scenario: 24 windows, 1,802,360 input and 196,608 output tokens. Cost: `(1,802,360 × 5 + 196,608 × 25) / 1,000,000 = USD13.927000`.
- Combined central scenario: **USD63.004860 ≈ USD63.00**. Full-output scenario: **USD89.049660**. Largest initial counted input plus output allowance: 67,030 / 200,000 tokens.
- 106 saved count events; zero generation starts, zero MODEL events, USD0 logged. Generation readiness is false; operator caps remain unset. Plan SHA256: `f8e8cd4211326fcf1f4f2723d5400583b47dabefbbaa842224fe53e0cb7a06be`.

Review-window density/output are estimates, not generated/count-verified graphs. Both scenarios exclude obligation traversal, descendant discovery, requested contexts, corrections, retries, construction and pilot search/writing. The newly retained gaps can add work precisely outside this central estimate. D4-N1/D4-N2 remain applicable: explicit profile composition, imported extraction charges consuming the pilot cap, 26 available PDFs out of 53 records, 82 affected pages, and unverified live fidelity/completion. No prior budget recommendation becomes authorization here. No paid usage was added or unknown reservation released; no live extraction, construction, pilot, or semantic-fidelity review was performed.

### Findings placement

| Finding/disposition | Placement in this section |
|---|---|
| D5-B1: missing per-paper continuation count/spend bounds | Blocking finding D5-B1; verdict |
| D4-B1: silent gap loss resolved, exact identities retained | D4-B1 disposition; mutation evidence |
| Updated USD63.00 plan and exclusions | Free-plan confirmation and retained limits |
| Offline proof limits and unchanged D4-N1/D4-N2 operational prerequisites | Executed verification; Free-plan confirmation and retained limits |

**4 findings, 4 placed.**

DONE delta rereview5 blocking=1 should_fix=0 tests=382/384 negctl=pass full_run_ready=no verdict=fix-first

## Re-review round 6

Reviewed `feat/paper-extraction` at `ba3a004d422467a0aed8a77be9407587d265a514`, against `4b94f8e4a1053661d6dc36e3ec6d8bbc2b8d6405`, in `/home/dev/ara-work/gamma`. Scope: D5-B1, the new per-paper defaults, regression/mutation evidence, and migration of the proposed run configuration. Solo, report-only review; no implementation edits, branch changes, delegation, network calls, or paid generation. The required control runner temporarily mutated production files and restored them. Earlier report sections and the round-4 proposed config remain unchanged.

**Verdict: merge. D5-B1 is resolved; no blocking or should-fix findings remain in this review scope.** Full-run readiness is **yes for the configured, budgeted experiment**, with the disclosed partial-source policy and operator authorization still required before spending. This does not certify that every paper will finish within its allowance or that model extraction is semantically complete.

### D5-B1 disposition — one allowance covers the paper lifecycle

The native caller (`ara/runtime/extraction.py:315`) enters `ModelCalls.extract_paper`; `ara/runtime/calls.py:285–296` installs one `PaperAllowance` for the whole operation and clears only the active scope on exit. All extraction attempts pass through `_execute_once`, where context admission, enclosing budget admission, and paper admission precede provider dispatch (`calls.py:168–180`). Reviews, evidence windows, explicit context requests, descendant obligations, retries, targeted corrections, additional initial ranges and subdivision recovery therefore share the same allowance. There is no queue-specific bypass or new allowance per obligation. SDK retries remain disabled; the full profile disables model fallbacks.

`ara/runtime/extraction_budget.py:74–83` admits at most one initial attempt plus the configured continuation limit. Cache reads consume an attempt with zero new dollar reservation; free token-count/planning calls consume neither. Monetary admission includes initial/rejected/held charges and reserves the complete next counted request at the stage model's rates. `_after` checks actual cost after a durable MODEL receipt (`calls.py:243–246`, `extraction_budget.py:85–87`). Existing global accounting and STOP behavior remain in force. As before, an underestimated response can exceed a cap before its actual usage is known; the post-response guard then stops, retains the charge, and prevents publication. It cannot undo provider charges or infer unknown actual usage.

At `extraction_budget.py:39–51`, prior attempts and source-linked MODEL charges are reconstructed from the existing log. A new source gets its own count/cost baseline; returning to an old source recovers its prior usage, even through a new `ModelCalls` instance. The source ID comes from the runtime paper scope rather than model output. Clearing `_paper_budget` does not erase the persisted allowance.

At `extraction_budget.py:59–72`, STOP reconstructs outstanding accepted obligation IDs from discovery/resolution events and records the source, sorted pending IDs, attempts, continuations, paper spending and both limits. Both the reason and structured partial receipt identify the paper and pending IDs. A global budget stop is also enriched with this paper context by the lifecycle wrapper. Raw responses, immutable snapshots and accumulated history remain intact; no gap is discarded or declared resolved to meet a limit. A post-response actual-cost STOP retains the raw response but does not incorporate its new discoveries into accepted artifacts; pending IDs describe the accepted ledger, not unincorporated response content.

**Independent offline probes:** reran the prior 40-generation counterexample using the new full-profile defaults. It now refuses before dispatch 26, after **25 responses / 24 continuations**, USD0.04375 synthetic charges, 25 discoveries and 24 resolutions. STOP names `p` and `p:joined24:turn:24:gap:0`; no literature is published. Shared USD125 and paper USD15 allowances still have money available, proving that the count guard independently binds.

A separate USD0.8025 paper-cap probe refuses before dispatch 3 after USD0.0035 synthetic charges; the next USD0.8005 reservation would exceed the paper cap, while shared USD125 remains available. The low-global-budget probe still stops after six responses and now retains paper/pending-ID context in its final STOP/partial receipt. A further probe executes `p`, replays `p` from cache, reconstructs `ModelCalls`, executes `q`, then retries `p`: only two provider dispatches occur, the cached attempt consumes count, `q` starts with its own allowance, and re-entry to `p` refuses with two prior attempts and USD0.00175 paper cost versus USD0.0035 total cost. No reset occurs at a cache, queue, or object boundary.

Receipts under `/home/dev/ara-work/reports/`: `delta-rereview6-probes.py/.json/.txt` and `delta-rereview6-reentry.py/.json/.txt`. Their JSON records link the complete event/cache/artifact directories. All probe usage/cost is synthetic; sockets were blocked.

### Default sizing and proposed configuration

**The defaults are sound as finite experimental limits.** Independently recomputed the sizing from the saved round-5 plan and cost scenarios:

| Group | Allowed continuations / paper USD | Baseline count arithmetic | Full-output cost scenario | Remaining scenario headroom |
|---|---|---|---|---|
| Under 300 physical pages | 24 / USD15 | At most 4 initial ranges + 1 review − 1 initial attempt = 4 continuations | At most USD5.048850 | 20 continuations; USD9.951150 |
| At least 300 physical pages; current large source has 358 | 48 / USD30 | 16 initial ranges + 4 reviews − 1 initial attempt = 19 continuations | USD20.281665 | 29 continuations; USD9.718335 |

The large source's central scenario is USD15.570865, already above the ordinary USD15 cap; an explicit larger allowance is necessary for the intended baseline. The 300-page threshold is a physical-size rule, not a source-name exception. Near context capacity, `(168,000 × 5 + 32,000 × 25) / 1,000,000 = USD1.64` reserved per request, so dollars can bind before count. The headroom does not fund all allowed continuations at maximum size. Aggregate extraction/run caps still apply and are not increased by summing paper limits. Invalid counts and nonfinite/negative dollars, including unused override values, refuse before dispatch.

Created `/home/dev/ara-work/reports/delta-rereview6-config.proposed.yaml` from `delta-rereview4-config.proposed.yaml`, adding the three keys below to both the `extraction-full` and composed `pilot` profiles. All other parsed configuration values were asserted unchanged:

```yaml
extraction_paper_continuation_limit: 24
extraction_paper_cost_cap_usd: 15.0
extraction_large_paper_limits:
  min_pages: 300
  continuation_limit: 48
  cost_cap_usd: 30.0
```

Offline check: invoked native CLI profile loading for `extract --profile extraction-full` and `run --profile pilot`, intercepting the injected calls factory before provider creation or generation. Verified the resulting caps, extraction model/fallback policy, construction settings and writing allowances. Instantiated the production allowance for 299, 300 and 358 physical pages in both composed profiles. This checks configuration wiring and threshold selection; it is not an extraction or pilot completion test.

The proposal preserves USD125 / 12M extraction caps, USD350 / 30M pilot caps including imported extraction charges, the 32k construction catalogue and 100k working-input budget, and writer/audit/evidence/verification output allowances of 20k/24k/64k/48k. The proposal remains a configuration artifact for an authorized run, not authorization itself. The old file is preserved at SHA256 `3d93d44597db15e07708bba7d7cb4a5bb2bbf86646c1c438e80d751c3f8fb14a`.

Config/sizing check receipts: `delta-rereview6-config-check.py/.json/.txt`. No extraction prompt, response schema or range-planning change occurred in this commit, so reuse of the saved free plan is appropriate. Its central estimate remains **USD63.004860 ≈ USD63.00**, with full-output scenario USD89.049660 and plan SHA256 `f8e8cd4211326fcf1f4f2723d5400583b47dabefbbaa842224fe53e0cb7a06be`. Review density/output remain assumptions; obligations, descendants, requested contexts, corrections/retries, construction and pilot work remain outside those scenarios. No new count-service call was made.

### Executed verification and mutation evidence

Full `uv run pytest`: **414 passed, 2 skipped / 416 collected**, exit 0, **239.40 seconds**. The two skips are opt-in live checks; `test_extraction_round6.py` contributes 32 passing cases. Own probe, re-entry and offline-config checks also exited 0 before mutation testing began. Full receipt: `/home/dev/ara-work/reports/delta-rereview6-pytest.txt`.

After pytest and all independent source-dependent probes exited, ran `uv run python tests/integration/negative_controls.py` sequentially: **162/162 red, 162/162 restored green**, exit 0. Full receipt: `/home/dev/ara-work/reports/delta-rereview6-negative-controls.txt`. Copied all individual traces and `results.json` to `/home/dev/ara-work/reports/delta-rereview6-controls/`. No suite, probe or config check ran concurrently with mutation controls.

Read all six new mutation definitions in `tests/integration/negative_controls.py:211–230` and their actual red traces. The fresh independent run produced these failures, each followed by restored green:

| Mutation | Observed red behavior | What it establishes |
|---|---|---|
| `paper_continuation_cap` removes count admission | Expected `BudgetStop` did not occur | Descendants cannot bypass the paper count |
| `paper_reservation_cap` removes paper reservation admission | Expected `BudgetStop` did not occur | Shared remaining money cannot bypass paper USD admission |
| `paper_actual_cap` removes actual-cost stop | Expected `BudgetStop` did not occur | Measured overruns stop after retaining the response/charge |
| `paper_count_finite` removes count validation | Expected paper error instead became JSON infinity serialization error | Explicit finite/integer validation contract |
| `paper_dollars_finite` removes dollar validation | Expected paper error instead became JSON infinity serialization error | Explicit finite/nonnegative USD validation contract |
| `paper_boundary_cost` includes earlier papers' spending | Second paper incorrectly refused before its first dispatch | Monetary allowances reset for a different source |

The finite-value controls prove the configuration error boundary; they do not show a paid dispatch under mutation, since JSON serialization also rejects infinity. The suite additionally exercises retry/correction count and dollars, review/evidence/context kinds, multiple pending IDs, same-source re-entry, independent sources, unknown reservations, actual overruns and threshold selection. The old gap-retention controls remain green after restoration. No additional regression was found in this narrow review.

Final restoration checks: `git status --short` empty, `git diff --exit-code` and `git diff --check` passed, HEAD remained `ba3a004d422467a0aed8a77be9407587d265a514`. The prior 45-item frozen T remains SHA256 `25a7ec8c35d393b230738e6008467d70926697db6bed1f91c72b5edcd39cb3a4`. No new construction/freeze was performed.

### Remaining operating limits and findings placement

D4-N1/D4-N2 remain disclosed operating conditions, not new defects: explicit profile composition, imported extraction charges consuming the enclosing pilot cap, 26 available PDFs out of 53 records, 82 affected pages, and the intended `missing record-only` policy. Finite local limits may refuse a source while corpus budget remains; they neither skip the source nor automatically resume the collection. Structural/reference validation does not independently certify the semantic adequacy of selected evidence. No live extraction, construction, search, writing, or semantic-fidelity proof was run this round. This review added USD0 paid usage, released no prior reservation, and granted no new spend authorization.

| Finding/disposition | Placement in this section |
|---|---|
| D5-B1 resolved: count/USD bounds, STOP inventory, lifecycle persistence | D5-B1 disposition; independent probes; mutation evidence |
| Default sizing and external config migration | Default sizing and proposed configuration |
| Verification limits and retained partial-source/accounting prerequisites | Executed verification; Remaining operating limits |

**3 findings, 3 placed.**

DONE delta rereview6 blocking=0 should_fix=0 tests=414/416 negctl=pass full_run_ready=yes verdict=merge
