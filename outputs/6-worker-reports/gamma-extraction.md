# Gamma: native per-paper literature extraction

## Delivery

Branch: `feat/paper-extraction`.
Head: `893b3794bab3ebd349af2be54cb809ecd4d051d9`.
Base: `5998c90b990b843ce4da111bbddfa04f7080ca6b`.
Checkout: `/home/dev/ara-work/gamma`.
The branch is locally committed, not pushed. `/home/dev/ara-scaffold` remains on `main` at the requested base; alpha's run directories and caches were not touched. No workers were delegated to. Python 3.13.16; pypdf 6.21.1 is locked.

## Design and rationale

At the base, `cli.main` read `--literature` as plain text, labelled its contents HUMAN, and passed it through `prepare` to `ModelCalls.build_t`. There was no PDF intake. Existing `ModelCalls` already owned prompt rendering, strict local response validation, cached provider dispatch, reservation, retry, actual accounting and append-only MODEL events. That is the extended native boundary; the deterministic engine is unchanged.

`ara extract` reads the manifest and selected PDFs, estimates cost before dispatch, and invokes `ModelCalls.extract_paper` once per available paper, with the normal bounded validation retries. `--paper-id` restricts selection; omission selects the manifest. The new prompt and closed schema require claims or arguments, source id, author/reported/attacked attribution and inclusive page ranges. Accepted results cross the boundary as frozen dataclasses with tuple collections. Source ids, page ranges, whitespace-only text and schema shape are checked before caching. The prompt supplies no human summary, evaluation or cross-paper synthesis.

Local pypdf text extraction preserves one-based physical PDF pages and leaves the provider's existing text request protocol unchanged. Input text, PDF checksum and metadata enter prompt/cache identity; changing PDF bytes invalidates cache even when text is identical. Citation identifiers are generated as `<id>:pdf:<page>` or `<id>:pdf:<start>-<end>`. Build-T checks citations against accepted extracted identifiers. Entirely record-only literature stops before build-T dispatch.

Missing, unreadable, encrypted or partially textless PDFs produce a logged **record only, not extracted** outcome with no claim items. `--missing refuse` stops without publishing an assembled file. A conservative UTF-8 request-byte bound plus schema bytes and output allowance refuses oversized papers without truncation; provider token admission rechecks the context limit on every attempted dispatch, including retries. Oversize preflight refusals use the marked fallback unless strict refusal is selected. Model/provider/schema/budget failures always stop; they do not become bibliographic success.

Each accepted paper writes `<id>.extraction.json`. The assembled `literature.extracted.txt` has a provenance sidecar pinning the completed source-log prefix. The real `--literature` loader verifies the checkpoint and reconstructs the exact artifact from logged outcomes before importing source events. Original labels, timestamps, model receipts and charges survive. AI text stays SYSTEM/MODEL rather than HUMAN; human commands and manifest selections remain HUMAN. Methodology is derived from logs alone and summarizes extracted/fallback/failed papers, call count, cache replay, models, tokens and cost.

The extraction cap defaults to USD30 and is enforced before dispatch and after actual usage, including rejected attempts. Existing per-run caps also apply. A planning estimate uses pages × 1500 tokens/page, prompt overhead and the full 8192 output-token allowance per readable paper. It excludes retries and server fallbacks. DECISIONS.md GX1–GX5 records these choices and limits; README documents the ordinary command flow.

## Files changed

- `ara/runtime/extraction.py`: immutable intake/result contracts, manifest/PDF loading, estimates, outcomes, assembly and provenance validation/import.
- `ara/runtime/calls.py`: native extraction call, context admission and build-T citation checks.
- `ara/runtime/cli.py`: extract command and provenance-aware literature intake.
- `ara/runtime/budget.py`: extraction admission/actual cap within the existing ledger.
- `ara/runtime/export.py`: log-derived extraction accounting and receipt-import disclosure.
- `prompts/extract_paper.txt`, `schemas/extract_paper.json`: topic-neutral instruction and strict response contract.
- `config.yaml`: extraction cap, output allowance and page-token assumption.
- `pyproject.toml`, `uv.lock`: locked pypdf dependency; no unrelated dependency upgrades.
- `.gitignore`: PDFs and generated extraction/provenance/assembled artifacts.
- `tests/runtime/test_extraction.py`, `tests/test_schemas.py`, `tests/integration/negative_controls.py`: placeholder-only tests and production mutations.
- `README.md`, `DECISIONS.md`: usage and decisions.

New tracked content is topic-neutral; generated fixtures contain only P/Q/R. Real PDFs, model output, logs and caches are not committed. Reviewed the changed source/prompt/schema/docs and generated fixture construction; text search alone would not prove semantic absence.

## Executed verification

First complete-tree run: `uv run pytest` — **265 passed, 2 skipped, 267 collected**, in 38.83 seconds. The skipped cases are the pre-existing opt-in live-provider tests. No paid calls occurred in tests.

Extraction-specific coverage: **32 cases**, plus the new generic response-schema case. Tests generate tiny PDFs at runtime and block socket connections. They exercise actual pypdf page text, immutable accepted values, invalid schemas/attributions/source ids/page ranges, missing and unreadable fallback, strict refusal, oversize refusal, provider context admission, extraction and enclosing caps, actual overspend, retries and retry admission, cache replay/PDF identity, log-derived methodology, provenance integrity, imported costs, manifest safety, and estimate-only behavior.

`test_extract_cli_to_build_t_native_path` executes `cli.main` for extraction and then normal run intake, using the real ModelCalls and native engine with an offline provider transport. It verifies exact assembled input in build-T, persisted commitments with page citations, extraction accounting in downstream methodology and absence of AI literature text in HUMAN events. This exercises preparation and native search to awaiting selection; it is not a live essay/pilot completion claim.

Installed-console proof: `uv run ara extract` against one generated two-page P/Q PDF completed through the default CLI factory and MockProvider. Its estimate was USD0.229025; its **simulated** response receipt was 100 input/50 output tokens, USD0.00175. Real spend was zero. Artifacts: `/home/dev/ara-work/gamma/runs/gamma-console-proof/` and generated inputs in `runs/gamma-console-inputs/`.

Actual-manifest estimate-only command completed with 53 records, zero PDFs/readable papers and zero model dispatches. It did not execute a 53-paper extraction. Its current-input estimate is USD0 because no paper is available, distinct from the future full-text scenario below. Receipt: `/home/dev/ara-work/gamma/runs/gamma-estimate/`.

`uv run python tests/integration/negative_controls.py` — **63/63 observed red, 63/63 restored green** (39 existing controls plus 24 extraction controls). Every mutation disabled a production wire and required pytest exit 1; each restoration required exit 0. New controls cover schema, attribution, source/item identity, page bounds, actual PDF text, no partial-page omission, fallback marker, strict refusal, local/provider context bounds, admission/actual caps, retries, MODEL logging, methodology, cache replay and PDF identity, artifact provenance, CLI import, AI/HUMAN labels, T citation grounding, record-only refusal and cost estimation.

Per-control red/green stdout: `/home/dev/ara-work/gamma/runs/delta-controls/<name>-{red,green}.txt`.
Machine receipt: `/home/dev/ara-work/gamma/runs/delta-controls/results.json`.
Console receipt: `/home/dev/ara-work/gamma/runs/gamma-negative-controls.txt`.
Final committed-revision reruns at `893b3794bab3ebd349af2be54cb809ecd4d051d9` completed successfully:

- `uv run pytest`: **265 passed, 2 skipped, 267 collected in 34.71s**; receipt `runs/gamma-final-pytest.txt`.
- `uv run python tests/integration/negative_controls.py`: **63/63 red, 63/63 restored green**, exit 0; receipt `runs/gamma-final-negative-controls.txt` and the per-control files above.
- `git diff --check` and final clean-tree check passed; mutations were restored exactly. Committed tree contains only `.gitkeep` under `literature/fulltext`, with no generated outputs staged or committed.

## Live single-paper receipt

**not run: no PDF present**.
The source directory `/home/dev/ara-scaffold/literature/fulltext/` had zero PDFs at the input inventory and estimate-only checks. No live extraction call or full batch was run. Real spend: USD0. The approved USD3 single-paper allowance was unused. Final directory recheck at 2026-10-21T00:26:05.989366+00:00 also found zero PDFs. No claim is made about real provider acceptance, source fidelity or extracted output quality; the offline output shape is `source_id` plus an item array containing kind, attribution, text and page range, with generated citation ids in the assembled artifact.

## Projected cost for 53 papers

**USD24.99 (unmeasured planning scenario; exact arithmetic USD24.985825).**

The 40 available bibliographic page ranges total 1,364 pages. Thirteen records lack usable ranges. Imputing their lengths at the observed median of 35 pages gives 1,819 pages. At 1,500 input tokens/page plus 1,845 prompt-overhead byte-tokens per paper, this yields 2,826,285 estimated input tokens. Reserving all 8,192 output tokens for each of 53 papers yields 434,176 output tokens. Configured USD5/25 per million input/output tokens gives USD14.131425 + USD10.854400 = USD24.985825.

This assumes one accepted attempt for every paper and excludes correction feedback, retries, fallback iterations and source-metadata overhead. Bibliographic extents are unverified, missing lengths may be much larger, and some papers may be refused by the conservative context/text-layer checks. Three attempts could roughly triple cost before accounting for larger correction prompts or server fallbacks. It is neither a quote nor evidence that every individual paper fits one call. Re-estimate actual PDFs before scheduling the batch.

The ordinary USD10/200000-token run limits are insufficient for this scenario (~3.26 million combined estimated tokens); the extraction USD30 cap alone does not override them. The operator must supply a reviewed extraction config with suitable enclosing caps, and preserve room for downstream build-T/search if imported into the same run budget. Machine calculation: `/home/dev/ara-work/reports/gamma-cost-projection.json`.

## Known gaps and operational limits

1. No PDFs were available, so live single-paper acceptance and real extraction quality remain unexercised. No full-batch or live pilot completion is claimed.
2. pypdf provides text extraction, not OCR or guaranteed layout recovery. Even an otherwise harmless blank page causes explicit fallback. Nonempty but badly ordered/incomplete text can still pass intake; images, equations and visual content are not interpreted.
3. UTF-8 bytes are a conservative context bound, so a paper that could fit a tokenizer may fall back. Oversize splitting is intentionally not implemented. Provider/output stops remain final and cannot yield silently partial accepted extraction.
4. Schema, attribution enums and page/citation bounds do not prove semantic support, correct attribution or exhaustive coverage. Real papers and AI extraction outputs still require inspection under the competition's methodology rules; no human-authored philosophical summary was introduced.
5. The generated artifact depends on its sidecar and the recorded source-log path. Copying only its text is insufficient. Importing preserves upstream cost in each downstream run; aggregate spending across multiple downstream exports must deduplicate reused upstream receipts. Cached re-extraction records zero new spend and retains raw cached response provenance under the existing cache semantics.
6. The USD24.99 projection relies on missing-length imputation and excludes retries/fallbacks. Default enclosing caps stop a full-size scenario early. Full-batch scheduling and cap selection remain with the operator.
7. Individual-paper context checks do not ensure the combined 53-paper extraction fits build-T. At the maximum output allowance, the collection could exceed a 200000-token context. This task adds no cross-paper reduction or build-T batching; those would require additional logged model work/design. The ordinary build-T/provider failure path remains, and no aggregate full-text size or successful full-batch T construction is claimed. Check the assembled input size before starting the pilot.

## Finding placement audit

| Finding affecting the next action | Deliverable section |
| --- | --- |
| F1: Native extract→literature→build-T/search path is proven offline; no live completion claim | Design and rationale; Executed verification |
| F2: No PDF available, no live call, USD0 real spend | Live single-paper receipt |
| F3: Missing/unreadable/textless/oversize sources explicitly fall back or refuse; no OCR or split support | Design and rationale; Known gaps 2–3 |
| F4: Structural citation/schema checks do not establish semantic fidelity or coverage | Design and rationale; Known gaps 4 |
| F5: Provenance sidecar/source log required; upstream receipts count in each run and need aggregate deduplication | Design and rationale; Known gaps 5 |
| F6: USD24.99 is a conditional projection; ordinary caps are insufficient | Projected cost; Known gaps 6 |
| F7: Combined extraction size may exceed build-T context; full-batch T construction is untested | Known gaps 7 |

**7 findings, 7 placed.**

Next operator step: review/merge the local branch, supply PDFs, inspect their preflight estimate and choose batch caps. The full extraction batch remains unscheduled by this worker.

## Fix round 1 — work record

Continuing from 893b3794bab3ebd349af2be54cb809ecd4d051d9 after reading the complete independent delta review and the brain's fix brief. The review reproduces an unguarded aggregate build-T request, missing cross-run cache lineage, silent sparse-image input, rejected blank pages and a byte-based size cliff. Responsible native paths are ModelCalls._execute_once, extraction.load_papers/assemble/literature_provenance, CLI profile selection and log-derived methodology.

Plan: cap compact per-paper literature entries with closed-schema item/text bounds and an escaped serialized size check; count complete build-T and extraction requests before dispatch; size extracted-literature T output separately. Refuse imports whose cross-run cache replay lacks original receipts. Record blank pages and partial image/text coverage without renumbering. Replace byte-based context refusal with counted admission. Add extraction profile/preflight cap diagnosis and local/inherited accounting. Verification and commits pending; no new live call made.

### Fix round 1 implementation and capacity

Commit: `7aacc81f06736ca9b424a95fdf4a3fb764acb563` (`Bound corpus extraction and enforce context, coverage, and receipt integrity`), on the same local branch. The changes below supersede the earlier byte/blank-page policy, unbounded aggregate input, and permissive cache-import accounting. The earlier receipts remain historical.

B1 is resolved with bounded extraction rather than an additional model reduction stage. A closed schema permits at most four items per paper and 400 characters per item. Local validation additionally limits each compact entry to **2,200 UTF-8 bytes after JSON-string escaping**, including source ids, generated citations, status and partial-coverage notice. The prompt states these limits and asks the model for a central selection; oversized output retries through the existing logged/reserved validation path. Code never truncates text or silently drops a paper. Full bibliography, checksum and page diagnostics remain in per-paper artifacts and logs rather than consuming build-T context.

The maximum-capacity fixture uses 53 distinct 64-character source ids, four items each, and pads **every** entry exactly to the 2,200-byte allowed size. It executes `ara extract` and `ara run --literature` through the actual CLI, ModelCalls, AnthropicProvider request/count/stream path and native engine with an offline SDK transport. The transport uses the full request's UTF-8 length plus 32 envelope units as a conservative token upper bound; this is not a live tokenizer measurement. It verifies both copies of the schema in the counting request, the complete assembled literature, all 53 source ids and 212 persisted commitments.

Capacity arithmetic recorded in DECISIONS GX6/GX7:

- Entries: `53 × 2,200 = 116,600` escaped bytes.
- Full counting request: `124,441` conservative input token units; measured overhead is `7,841`.
- Build-T output: `53 × 4 = 212` potential commitments; approximately 100 statement tokens + 100 formula tokens + 50 id/citation/JSON tokens each gives `212 × 250 = 53,000`; add 11,000 for thinking/serialization/formulation variance → **64,000 output tokens**.
- Combined maximum fixture: `124,441 + 64,000 = 188,441 < 200,000`, leaving **11,559 tokens (5.8%)** of headroom.

`extracted_build_t_max_output_tokens: 64000` applies to generated extraction literature; ordinary build-T output remains unchanged. This is output sizing, not a guarantee about arbitrary model formula complexity or repetition. Actual build-T and extraction calls now use `provider.estimate` (Anthropic `count_tokens`) on the full rendered request plus schema, record a `context_admission` event, and refuse before `call_start`/dispatch if input plus output allowance exceeds context. Correction attempts are counted again with their feedback. Long custom topic/audience fields can still trigger explicit refusal; the capacity fixture does not assert unlimited wrapper size.

B2 uses the expressly permitted smaller policy: **refuse import rather than invent missing lineage**. A cached extraction without its original accepted dispatch receipt earlier in the source log is marked as incomplete production accounting. Its artifact cannot enter the run CLI; the error says to import the original extraction artifact. Zero new cache spend remains reported as zero, but it is no longer labelled complete production accounting. Direct original-artifact import preserves original MODEL/HUMAN events. Same-log cache replay remains valid when the original receipt is present. No transitive cache-origin reconstruction is claimed.

S1/S2: the PDF preflight inspects actual paint operations, counts non-whitespace text, records `blank_page`, `sparse_image_text` or `nontext_visual_content` with physical page numbers, and excludes flagged unread visual pages from model input and citation support. Readable pages proceed and the paper becomes explicitly `partial`, with affected pages in outcomes, logs and methodology. An image-only paper remains partial with no items and no model dispatch. Blank pages preserve their positions and do not reject a readable paper. Encrypted, empty and all-blank PDFs have distinct reason codes. A focused failing probe found that pypdf ContentStream is false in a boolean test despite containing `Do` paint operations; presence is now tested with `is not None`, and a negative control protects that exact regression.

S3: PDF byte length is now a planning warning only. Both a >200,000-byte placeholder input and a multibyte glyph input with a fitting counted-token estimate proceed; a genuinely oversized counted request refuses without dispatch. The fixed production counter receives the complete prompt and schema on every attempt.

N1: methodology now exposes `local_totals`, `inherited_totals` and stable `inherited_receipt_ids`, including tokens, cost, model calls and reported human minutes. Import of the same receipt into one log is idempotent. Aggregate consumers must still deduplicate inherited receipt ids across downstream logs; imported charges remain in each run's budget.

N2: `ara extract --profile extraction` explicitly selects **USD30** for both cost caps and **6,000,000** total tokens; ordinary USD10/200000 defaults are unchanged. Preflight prints and logs **planned batch exceeds enclosing caps** if either enclosing limit is insufficient. With the existing unverified 1,819-page scenario, current prompt overhead is 2,751 per paper: input `1,819 × 1,500 + 53 × 2,751 = 2,874,303`; output `53 × 8,192 = 434,176`; combined `3,308,479` estimated tokens and **USD25.225915 (~USD25.23)** at configured prices. This fits the explicit profile for one attempt per paper, excluding source-metadata overhead/retries/fallbacks. It is not a quote or evidence that the unavailable actual corpus fits those spending caps. Downstream pilot retains its larger existing caps and inherited charges.

### Fix round 1 finding-to-commit/test map

All seven reviewed findings are implemented in `7aacc81f06736ca9b424a95fdf4a3fb764acb563`:

| Finding | Production change | Test / evidence carrying the finding |
| --- | --- | --- |
| B1 | Schema/prompt/serialized output budgets, compact literature projection, counted build-T admission, 64000 output allowance | `test_extraction_output_budget`; `test_build_t_counted_context_refusal`; `test_build_t_retry_recounts_feedback`; `test_capacity53_maximum_through_cli`; capacity arithmetic above |
| B2 | Missing-origin detection, incomplete accounting, explicit CLI import refusal | `test_fresh_cache_artifact_refused_at_cli_import` (fresh run A → cached run B → real CLI import refusal; A remains importable) |
| S1 | Sparse image/form and textless painted-page diagnostics; partial status; citation exclusion | `test_sparse_image_pages_are_partial`; `test_extraction_cannot_cite_unread_image_page`; `test_image_only_paper_stays_partial_without_model`; `test_nontext_vector_page_is_not_blank` |
| S2 | Blank-page diagnostics with original page indices, readable-page continuation | `test_blank_pages_retained_without_rejecting_paper` |
| S3 | Counted-token refusal, byte warning only | `test_large_bytes_use_counted_tokens`; `test_oversize_refusal_no_dispatch`; `test_provider_context_bound_rechecked` |
| N1 | Local/inherited totals, stable receipt ids, idempotent import | `test_fresh_cache_artifact_refused_at_cli_import` verifies original three-minute HUMAN receipt as inherited, new one-minute event as local, and duplicate import adds no records |
| N2 | Explicit extraction profile and enclosing-cap preflight warning | `test_preflight_flags_caps_and_profile_is_explicit`; GX10 arithmetic; unchanged ordinary defaults assertion |

### Fix round 1 verification receipts

- Focused regression run: **93 passed, one gated live test skipped, one capacity test deselected**; separate new retry/vector tests: **2 passed**.
- Standalone maximum-size capacity test: **1 passed in 27.39s**. Receipt `/home/dev/ara-work/gamma/runs/gamma-fix1-capacity.txt`; `CAPACITY53` reports input 124441, output 64000, limit 200000, decision fits.
- Fresh full suite, exact tree committed above: `uv run pytest` — **280 passed, 2 skipped, 282 collected in 66.87s**. Receipt `/home/dev/ara-work/gamma/runs/gamma-fix1-pytest.txt`. Skips are the existing opt-in live-provider tests; no live tests were enabled.
- Expanded required production-wire negative controls at commit `7aacc81f06736ca9b424a95fdf4a3fb764acb563`: **82/82 observed red, 82/82 restored green**, exit 0. Receipt `/home/dev/ara-work/gamma/runs/gamma-fix1-negative-controls.txt`; per-control logs and `results.json` in `runs/delta-controls/`. The suite includes 19 additional controls plus updated controls for superseded blank/byte behavior. No mutation tests ran concurrently with the full suite. The final worktree was restored exactly and is clean.

New fixtures remain non-substantive: P/Q placeholder text, blank pages, synthetic raster/vector marks and a Unicode glyph stress input. No new dependencies, philosophical summaries, real PDFs or model-produced source content are committed. Tests prohibit network access; fake SDK usage is simulated, not incurred cost.

### Fix round 1 compatibility and remaining limits

The original extraction artifact and its source log are the supported production route. Cross-run cache artifacts without origin receipts intentionally cannot be imported. Older artifacts using the prior unbounded projection fail closed and must be regenerated under the new contract; do not remove their provenance header. Custom older configs need the new extracted-build-T allowance, or should use the updated config.

The four-item/serialized-size budget is a deliberate central selection, not exhaustive source coverage. Structural checks do not prove semantic support, accurate attribution or satisfactory philosophical breadth. The PDF coverage heuristic flags image/form pages with fewer than 200 text characters and textless painted pages; it does not perform OCR or prove reading order/completeness. A sufficiently long deficient OCR/header layer can evade it, and a sparse harmless form can be conservatively flagged. Those limitations need inspection of the real corpus rather than claims from placeholder tests.

No PDF has been present at checks during this round, so live acceptance and source fidelity remain unexercised; the authorized USD3 single-paper allowance is still unused. Real spend is USD0. No full real-paper extraction batch was started. The final inventory/live disposition will be recorded below.


### Fix round 1 final disposition

All B1, B2, S1, S2, S3, N1 and N2 changes are locally committed at
`7aacc81f06736ca9b424a95fdf4a3fb764acb563`; the full tested tree matches that commit.
Capacity53: **fits** under the documented bounded contract. Tests: **280/282**,
with two intentional live-test skips and zero failures. Negative controls:
**82/82 red, 82/82 restored green**. No push or main-branch change by this worker.

Live receipt: **not run: no PDF present**. Final directory inventory at 2026-10-21T00:51:54.975428+00:00 found zero PDFs. Real spend USD0; the authorized USD3 allowance remains unused. This is a live-evidence limit, not a passing real-paper extraction claim.

Placement audit: B1, B2, S1, S2, S3, N1 and N2 are each carried in the finding-to-commit/test map, implementation/capacity section and compatibility/remaining-limits section above. L1 (no PDF/live evidence, zero spend) is carried in this final disposition. **8 findings, 8 placed.**

Next operator step: review the fixed branch; when PDFs arrive, run the single shortest-paper check under the authorized cap before scheduling the one original full extraction run. Retain its original artifact/log for direct pilot import. No full real-paper extraction batch has been run by this worker.

## Round 2: rich extraction

### Intent and implementation record (in progress)

Worktree `/home/dev/ara-work/gamma`, branch `feat/paper-extraction`, starting head
`7aacc81f06736ca9b424a95fdf4a3fb764acb563`. Work alone; no push. The rich-design brief
and Delta's full re-review/feasible alternative govern this round. The full PDF
inventory was read; selected live candidates are the shortest placed file
(`rothschild2012`, 13 physical pages) and `kolodnymacfarlane2010` (31 pages, partial
text encoding). No live generation has run at this checkpoint.

Implemented v2 rich nodes/links, item-level page citations, 32000 output allowance,
counted range subdivision and additive range reconciliation, immutable graph files,
deterministic token-packed T plan, shared symbol catalogue/model bindings, exact
attributed source text, explicit omissions, connected-argument selection, one native
freeze, universal request admission including cache and retries, strict partial
refusal, and visible private-use glyph diagnostics. Source text is never byte-sliced.
The full graph is retained independently of the 100000-token working context.
Methodology includes item counts, range counts, plan and freeze evidence.

Executed evidence so far: initial rich/strict tests were red (3 failures); updated
extraction/CLI suite then passed 47 cases in 55.74s; added graph/batch guard suite
passed 27 cases in 4.11s. Full suite and 101 production mutation controls are now
being verified sequentially. Final counts and paid receipts will supersede this
checkpoint below. Tests use placeholders only. Real content remains in ignored runs.

### Design constraints to retain in final findings

- Semantic coverage, attribution/formalisation and symbol equivalence are model
  judgments. JSON/reference validation does not prove fidelity. Explicit reuse is
  logged, never invented by deterministic code.
- Default graph-connected selection keeps needed dependencies and qualifications.
  Proportional per-batch working allowances can refuse relevance-skewed corpora;
  they never trim the saved graph. Large single source batches or reconciliation
  contexts refuse explicitly. Full rich source is inspectable; current search sees
  working T only and requires a new lifecycle for expanded evidence.
- Sequential symbol-catalogue growth fixes dispatch order; merge order is stable.
  All request contexts, including growing catalogue and validation feedback, count.
- Encoding-warning text is retained but marked partial. Strict mode refuses any
  partial paper, including mixed visual/text and private-use glyph warnings. OCR,
  reading-order correction and speculative glyph repair remain unsupported.
- Original extraction lineage remains mandatory. A fresh cross-run cache artifact
  without origin receipts is refused; legacy v1 is refused rather than human-labelled.

### Local quality review

The ce-work implementation workflow was used within the local-only brief. The
ce-simplify-code pass removed the obsolete serialized-size helper and unused
imports; it retained all proof tests and boundary checks. No lint/typecheck command
is configured in pyproject.toml. The full test suite and diff whitespace check are
the configured local verification.

Code review: skipped (ce-code-review unavailable). Its full workflow requires
delegated review/merge/report contexts, which conflict with this task's solo-work
constraint. A manual diff scan covered graph references, counted admission,
immutable evidence, freeze ordering, shared-symbol bindings and receipt accounting;
it is not an independent review. Receipt: `runs/gamma-round2-review.json`.

### Live admission issue and correction

At committed head `47fe17b3384f60a216519dd3dcdef51680e53809`, after 309 tests
passed (2 intentional skips) and all 105 controls passed red/restored-green, the
first extraction attempt returned BadRequestError. The runtime stopped and held
USD0.87919 as a reservation with actual spend unknown. A diagnostic retry under a
reduced USD5.12081 remaining cap returned an explicit HTTP400 invalid-request error:
the provider grammar rejects an enum combined with a union-valued `type` for
`inference_origin`. Its second unknown-usage reservation was also USD0.87919.
Neither attempt accepted source evidence; no build-T call had run.

The source schema now expresses the same accepted values as separate string-enum
and null branches. The new offline projection regression failed before this
correction, and the complete verification is being rerun before a new local commit.
Further extraction checks have a USD4.24162 cap: the original USD6 less both held
reservations (USD1.75838). These reservations must not be represented as measured
provider usage. Diagnostics and both original logs remain in ignored
`runs/gamma-round2-live/` and `runs/gamma-round2-live-attempt2/`.

### Batch service grammar correction

The first real build-T request at `eaa29526e97d7776ec004ac5989c4705931ec9b5`
was also rejected before usable output. Its 56306-input/64000-output reservation
was USD1.88153 with actual usage unavailable. A diagnostic request limited to 512
output tokens established HTTP400 `compiled grammar is too large`; its reservation
was USD0.29433. Both original receipts remain in
`runs/gamma-round2-live-attempt3/construction/` and `construction-diagnostic/`.
There was no accepted batch or freeze in either directory.

The batch-only wire now represents formula ASTs as JSON strings, decoded before
unchanged local schema/type/symbol/citation validation. This avoids expansion of
the provider grammar without reducing formula expressiveness. Malformed JSON is
an accounted validation rejection. New wire tests were red before the fix; the
53-paper CLI transport now sends actual encoded formula strings. The final live
retry will use a 60000-token output ceiling and USD1.82414 remaining local budget
(USD4 minus USD2.17586 held reservations). No failed request is erased or presented
as zero-cost success. The new live topic selects one principal connected argument
from each source, with all its prerequisites and qualifications, while retaining
and explicitly accounting for the remaining rich evidence.

### Symbol-boundary review correction

The final solo review traced variables into `ara/formal.py`: an unbound variable
compiles to a global constant. The rich batch catalogue previously enumerated only
atoms, predicates and explicit constants, so a free variable could bypass its
alignment contract. Working-T validation now requires local quantifier binding;
global values must use declared constant symbols. The free-variable regression
failed before the fix and the bound-variable control passed. This leaves engine
semantics unchanged and closes the rich-construction boundary before the last
paid check. Full tests and controls are being rerun on this final source tree.

### Execution checkpoint before final batch attempt

Current HEAD: `eaa29526e97d7776ec004ac5989c4705931ec9b5`. Pending local changes are
GX18/GX19 (formula wire encoding and bound-variable validation), with 315 passed,
2 skipped, 317 collected in 116.53s. The full 110-control runner is active alone;
no pytest is running concurrently with it. After its successful restoration, commit
DECISIONS.md, ara/runtime/{calls,providers,construction}.py,
prompts/build_t_batch.txt, tests/integration/negative_controls.py, and
 tests/runtime/{test_extraction_fix1,test_extraction_rich,test_provider}.py.

Then source the existing operator credential only into the process environment and
run `uv run python runs/gamma-round2-live/check-build-final.py build`. It uses the
accepted artifacts in `runs/gamma-round2-live-attempt3/extraction/`, a fresh
`construction-final/`, 60000 output tokens, and USD1.82414 remaining local budget.
Do not rerun extraction: both accepted rich papers already exist. Earlier failed
batch reservations total USD2.17586; earlier failed extraction reservations total
USD1.75838. Measured extraction cost including its paid local-validation retry is
USD1.66221. Thus pre-final accounting is USD5.59645 including USD3.93424 unknown-
usage reservations. Keep measured charges and held reservations distinct.

Final remaining work: inspect the final batch's actual receipt/merge/freeze and
schema acceptance, compute projections using 1379 known pages and 2513 projected
pages (27 missing × 42 median + 1379), append final cost/capacity/verification and
findings-placement sections, update gamma-round2-verification.json to final head,
verify clean Git state, and emit the requested exact DONE line. The model's full
real outputs remain only under ignored runs paths. No full real corpus run.

### Final round-2 disposition — live construction blocked

This section supersedes the execution checkpoints above. Final committed HEAD is
`140a54b8620eed256901e099a1a861870e4f5e69` on `feat/paper-extraction`.
The checkout is clean; nothing was pushed. The implementation and offline proofs
are complete, and both requested rich extractions were accepted. **The required
live build-T merge/freeze proof is incomplete:** the only wire-valid live response
omitted required dependencies and was correctly refused before freeze. No usable
live T or successful combined extraction/construction cost forecast is claimed.

Commits in this round:

- `47fe17b`: rich source graphs and counted working commitments.
- `eaa2952`: provider-compatible nullable extraction fields.
- `140a54b`: batch formula wire encoding and bound-variable validation.

The final live attempt ran at the final HEAD after offline verification. Accepted
extractions were produced at `eaa2952`; the later commit leaves extraction code and
its schema unchanged. Reusing those immutable artifacts avoids paying to repeat
accepted evidence. No real philosophical content was added to tracked files.

### Final design and capacity evidence

V2 source artifacts replace the four-item/400-character representation. They
retain premises, stated inference edges, intermediate/final conclusions,
distinctions, qualifications, reported views and attacked views with explicit
attribution and physical-page citations. `paper_stated` marks reported inference
origin; it grants no engine license. There is no item-count or character quota.
The 32,000-token extraction output allowance is justified by the partial paper's
25,268 accepted output tokens; the former 8,192 allowance would not accommodate
that observed response. Output tokens can include provider reasoning overhead.

Counted overflow or exhausted output triggers logged page-range subdivision and
additive reconciliation, with immutable range artifacts. Single-page overflow and
oversized reconciliation refuse explicitly. This path is proved offline, not on a
large real paper. All requests, including retries, cache hits and downstream T
consumers, are counted before admission.

Construction sorts sources, hashes their content and persists a versioned plan;
plan inputs participate in cache identity. It packs against counted tokens rather
than a fixed paper count. Each logged batch selects topic/audience-relevant working
commitments, explicitly accounts for omitted evidence, and must preserve the full
connected dependency structure of each selection. Source texts/citations remain
exact. Shared symbols and model-produced bindings are checked for uniqueness,
signatures and evidence; deterministic code neither invents equivalence nor
deduplicates formulas. Free variables are rejected because the engine would treat
them as global constants; locally quantified variables remain valid. Stable merge
feeds the existing native preparation lifecycle and exactly one freeze.

Default arithmetic: batch input ceiling 70,000; output allowance 64,000; symbol
catalogue reserve 16,000. Their sum is 150,000 against a 200,000 context bound,
leaving 50,000 nominal headroom; the actual assembled request is recounted. Working
T is capped at 100,000 input tokens, with 8,000 reserved when assigning per-batch
working allowances. These are admission limits, not promises of semantic coverage.

The native 53-paper CLI capacity receipt uses nontrivial placeholder graphs:
**4 batches, 424 commitments, maximum counted batch input 28,660, merged working-T
input 51,847**. Its offline counter is `ceil(UTF8 bytes / 2) + 32`, not real-provider
tokenization. Tests verify all 53 source IDs, one freeze, HUMAN/MODEL receipts,
stable merge under completion reordering/cache replay, and duplicate IDs,
citations/symbols and over-capacity refusal. The real request independently counted
56,529 input plus 60,000 output = 116,529, leaving 83,471 context tokens. It failed
semantic structure validation, not context admission.

Receipts: `runs/gamma-round2-capacity.txt`,
`runs/gamma-round2-capacity-events.json`, and the tests in
`tests/runtime/test_extraction_rich.py` and `test_extraction_fix1.py`.
No real 26/53-paper run was performed.

### Final verification receipts

- `uv run pytest`: **315 passed, 2 skipped, 317 collected**, 116.53 seconds.
  The skips are opt-in live tests. Receipt: `runs/gamma-round2-pytest.txt`.
- `uv run python tests/integration/negative_controls.py`: **110/110 red and
  110/110 restored green**. Receipt: `runs/gamma-round2-negative-controls.txt`;
  individual mutation results/logs: `runs/delta-controls/`.
- The two commands ran sequentially. All mutations were restored; `git diff
  --check` passed and the final Git status was clean. No further tracked source
  changes followed those checks, so they were not rerun during report completion.
- Machine-readable verification:
  `/home/dev/ara-work/reports/gamma-round2-verification.json`, identifying HEAD
  and tree `5312b44a05ecede8855453c9719db4adc3d1e9e7`.

Controls cover graph identity/endpoints/origin, coverage and absence of summary
caps, ranges/reconciliation, strict partial handling, selection inventory and
closure, attribution, symbol identity/signature/alignment/budget, omissions,
working/downstream limits, merge/citations, plan identity, one freeze, encoding
warnings, legacy refusal, exhausted output, cache admission, nullable provider
projection, batch wire decoding and bound variables. Offline success establishes
these enforced boundaries; it does not establish real-model fidelity or completion.

Code review: skipped (ce-code-review unavailable). The dedicated workflow's
required delegated contexts conflict with the solo-work restriction. The recorded
manual scan is not independent; see `runs/gamma-round2-review.json` and the earlier
Local quality review subsection. This limitation remains open.

### Final live extraction receipts

All measured calls used `claude-opus-5`, with fallbacks disabled. Input/output
figures below are actual usage, not reservations. Cache read/write and server-tool
usage were zero. Full prompts/responses remain in ignored run logs.

| Paper / attempt | Result | Input tokens | Output tokens | USD | Provider seconds |
| --- | --- | ---: | ---: | ---: | ---: |
| rothschild2012, first | Schema/domain rejection: inference fields on a non-inference node | 16,141 | 12,314 | 0.388555 | 119.09 |
| rothschild2012, correction | Accepted | 31,660 | 13,019 | 0.483775 | 114.73 |
| kolodnymacfarlane2010 | Accepted, partial coverage | 31,636 | 25,268 | 0.789880 | 244.49 |

Shortest paper: 13 physical pages, **68 items**, measured total USD0.872330
including its rejection/retry. Partial paper: 31 readable physical pages,
**108 items**, USD0.789880. Private-use glyph warnings affect physical pages
1, 4, 5, 6, 8, 9, 30 and 31; readable text is preserved and coverage remains partial.
No speculative glyph repair or OCR was performed. Strict `--missing refuse`
rejects any partial source, including this warning case and wholly/mixed visual
papers; default partial mode produced the requested live artifact.

| Accepted item kind | Shortest paper | Partial paper |
| --- | ---: | ---: |
| premise | 23 | 50 |
| inference | 12 | 14 |
| intermediate_conclusion | 11 | 12 |
| conclusion | 3 | 3 |
| distinction | 1 | 3 |
| qualification | 8 | 14 |
| reported_view | 5 | 4 |
| attacked_view | 5 | 8 |
| Total | 68 | 108 |

Measured extraction: **79,437 input, 50,601 output, USD1.662210**, command elapsed
481.36 seconds. Receipt: `runs/gamma-round2-live-attempt3/extract-receipt.json`;
accepted immutable artifacts: `runs/gamma-round2-live-attempt3/extraction/`.
The two preceding provider grammar errors each retain USD0.879190 as an
unknown-usage reservation, not measured cost. Their receipts remain in
`runs/gamma-round2-live/` and `runs/gamma-round2-live-attempt2/`.

### Final live construction failure and budget boundary

The final provider response passed wire decoding/schema shape but failed local
argument closure: `working T drops premise/link/qualification`. It selected 31
items and explicitly omitted 145; closure requires **40 additional items**:
16 premises, 6 inferences, 6 qualifications, 5 intermediate conclusions,
3 distinctions, 2 conclusions, 1 reported view and 1 attacked view. A read-only
diagnostic found no changed source texts/citations, symbol-signature or
free-variable errors, binding mismatches, or new-symbol evidence errors. The
working-T and symbol-size guards were not independently checked in that diagnostic;
production validation stopped at closure. No claim is made that closure is the
only possible remaining failure.

Actual usage: **55,510 input, 44,795 output, USD1.397425**; provider time
426.79 seconds, command elapsed 429.19 seconds. **Zero accepted batches, zero
freezes, zero commitments published.** The automatic correction was counted at
90,078 input plus 60,000 output, which fits context but reserves USD1.950390.
Budget admission stopped it before dispatch; only USD0.426715 remained.

Receipts: `runs/gamma-round2-live-attempt3/build-final-receipt.json`,
`construction-final/events.jsonl`, and `closure-diagnostic.json`. The two earlier
construction HTTP400 failures retain unknown-usage reservations of USD1.881530
and USD0.294330. Their grammar issue was fixed in the final commit; those failed
attempts are neither erased nor treated as zero-cost usage.

| Accounting category | Extraction | Build T | Combined |
| --- | ---: | ---: | ---: |
| Measured usage USD | 1.662210 | 1.397425 | 3.059635 |
| Unknown-usage reservations USD | 1.758380 | 2.175860 | 3.934240 |
| Accounted against caps USD | 3.420590 | 3.573285 | 6.993875 |
| Separate authorized caps USD | 6.000000 | 4.000000 | 10.000000 |
| Remaining allowance USD | 2.579410 | 0.426715 | 3.006125 |

The caps are separate: unused extraction allowance is not transferable. Actual
provider accounting is incomplete for the four failed requests. The combined
USD6.993875 figure is measured usage plus held reservations, not an invoice total.
Machine-readable summary: `/home/dev/ara-work/reports/gamma-round2-live-receipts.json`.
No further paid call was made after the final rejection.

### Cost projections and their limits

The inventory has **26 placed PDFs, 1,379 physical pages**, median 42, minimum 13,
maximum 358. For 53 papers, the explicit central assumption is
`1379 + 27 * 42 = 2513 pages`. The two-paper sample has 44 pages. At the measured
sample extraction workload, including its paid validation retry:

- 26-paper extraction: `1.662210 * 1379 / 44 = USD52.095172`.
- 53-paper extraction: `1.662210 * 2513 / 44 = USD94.934857`.

These are page-scaled workload-equivalent scenarios, not upper bounds or validated
corpus forecasts. Both exceed the default USD30 extraction profile. Density,
encoding, output size, range/reconciliation calls, cache, retries and sample bias
can change the actual totals substantially. Unknown-usage reservations from setup
failures are excluded from future-work projections and retained above as current
accounting.

**Successful build-T cost and successful extraction-plus-build-T totals are
unmeasured for both corpus sizes.** Treating the rejected response as successful
construction would conceal the required missing evidence. For expenditure
sensitivity only, repeating the observed *failed* construction workload gives:

| Page-scaled scenario | 26 papers | 53 papers |
| --- | ---: | ---: |
| Extraction USD | 52.095172 | 94.934857 |
| Rejected build-T attempt USD | 43.796570 | 79.812023 |
| Extraction plus rejected attempt USD | 95.891742 | 174.746881 |

The last row purchases no accepted T in the observed case and is **not a completion
forecast**. Future packing, omission output, shared-symbol catalogue growth and
bounded working-T selection do not scale linearly with pages. Later search,
writing and export model calls are additional. A successful live construction
receipt is needed before replacing the unmeasured combined projections.

### Remaining gaps and concrete recovery

The live merge/freeze requirement remains blocking. The brief explicitly permits
“cap USD 4” for build T and “nothing beyond this”; the remaining USD0.426715 cannot
cover the already-counted USD1.950390 correction. Do not spend more, weaken closure,
trim source graphs, relabel rejected output as accepted, or discard reservations.

Recommended next authorized scope: raise the separate build-T cap from USD4 to
USD6 (USD2 additional), retain all existing reservations, and permit one further
counted attempt over the existing accepted extractions. Before that paid attempt,
provide explicit connected-component IDs and missing-dependency feedback through
the production request path, with placeholder regression/control proof. Those
improvements are proposed, **not implemented**, and the present report does not
claim that another model response will pass. Recount the actual request after
changes; any amount above the amended cap still refuses. The current counted
correction needs at least USD1.523675 additional allowance; USD2 adds some room
without authorizing a full corpus run. No additional budget has been granted.

Other limits remain: semantic fidelity/attribution/equivalence are model judgments;
search sees only working T, with rich graphs available for inspection rather than
implicit retrieval; proportional batch allowances may refuse skewed corpora;
single-source/page/reconciliation/downstream overflow refuses; the 358-page book
has not been shown to fit; real cross-batch alignment and range reconciliation
remain unproved; OCR and glyph repair are absent; origin-less cross-run cache
artifacts and legacy v1 artifacts refuse. There is no independent review receipt.

### Final findings placement and handoff state

| Action-changing finding | Deliverable section carrying it |
| --- | --- |
| Rich v2 structure replaces compact summaries; 32,000 output allowance has measured support | Final design and capacity evidence; Final live extraction receipts |
| Token-packed construction, symbol contract and one freeze have offline proof | Final design and capacity evidence; Final verification receipts |
| Universal counted admission and explicit overflow refusal bound downstream work | Final design and capacity evidence; Remaining gaps and concrete recovery |
| Strict refusal now covers partial sources; private-use warnings remain unresolved source-quality limits | Final live extraction receipts |
| Nullable enum and formula grammar incompatibilities were fixed; failed receipts remain charge-uncertain | Live admission issue and correction; Batch service grammar correction; Final live construction failure and budget boundary |
| Unbound variables could bypass symbol alignment; final validation closes that boundary | Symbol-boundary review correction; Final design and capacity evidence |
| Real build T omitted 40 required dependencies; no merge/freeze completion proof exists | Final live construction failure and budget boundary |
| Separate build cap prevents correction; paid continuation requires an amended cap | Final live construction failure and budget boundary; Remaining gaps and concrete recovery |
| Extraction projections exceed USD30; successful combined costs remain unmeasured | Cost projections and their limits |
| Fidelity, selected working context, large/skewed inputs and real multi-batch/range behavior remain limited | Final design and capacity evidence; Remaining gaps and concrete recovery |
| Origin lineage and v2-only import rules constrain recovery | Design constraints to retain in final findings; Remaining gaps and concrete recovery |
| Solo manual scan does not provide independent review | Final verification receipts; Remaining gaps and concrete recovery |

**12 findings, 12 placed.** Status is blocked on the live construction proof and
its budget, not complete. The next unresolved step is an operator decision on the
specific amended build-T cap above; no background job or API request is active.
The final task-line fields use `live_usd` for measured usage (USD3.059635), and
`unmeasured` for successful combined corpus projections. The prescribed `DONE`
marker is a handoff-format token and must not be read as overriding this blocked
status.

## Round 3

### Active work record

Brief: `/home/dev/ara-work/briefs/gamma-round-3-to-pilot.md`, including its brain
addendum. Base `140a54b8620eed256901e099a1a861870e4f5e69`; same local branch and solo
checkout, no push. D2-B1/B2/S1/S2 are being fixed with the requested ALT protocol;
D2-N1 numeric splits are included. Stage Sonnet pricing verified on the provider's
published pricing page (raw receipt: `runs/gamma-round3/pricing.html`). Extraction
keeps high/adaptive effort because the prior sample's thinking was a minor cost.

Six new regression tests were observed red before changes. They now pass; affected
suites passed 114 tests with one gated live skip. Full suite is running before the
121-control sequential mutation run. Latest source changes implement directional
closure, fixed-inventory formalization, obligation resolution, measured receipt
preservation and stage-specific extraction configuration. Artifact-only docs were
updated while tests ran; production code is stable during verification.

Paid authorization: new two-paper Sonnet extraction cap USD3; build-T campaign cap
USD6 less prior accounted USD3.573285 = USD2.426715 for one new construction
lifecycle, including root selection. No new live call yet. Stop at first failed
phase; if both pass, report and await Delta review, without step 3c. Prior Opus
artifacts and all failed receipts remain untouched. New real data will stay under
ignored `runs/gamma-round3/`. Targeted patch/reuse of invalid formulas is not cheap
under the provenance/alignment contract; it remains explicitly deferred in GX24.

### Round-3 implementation and review dispositions

- **D2-B1 fixed:** unresolved strings receive stable obligation IDs with originating
  range/page metadata. Reconciliation receives the original counted readable pages
  and an exact obligation inventory. Every resolution names accepted existing/new
  evidence IDs; missing, duplicate or unknown resolutions refuse publication.
  Immutable per-paper artifacts retain both obligation and resolution ledgers.
  Tests exercise no-op rejection, unknown evidence rejection, and genuine
  cross-range premise/link/qualification resolution. This validates the ledger,
  not the semantic truth of a model's resolution mapping.
- **D2-B2 implemented; live proof pending below:** the logged `select_t_roots` call
  returns roots/relevance and grouped omissions. Code computes closure and records
  roots, added IDs, graph hash and rule version. `build_t_batch` then formalizes
  exactly that fixed inventory. Code copies exact attributed source text/citations
  and derives syntactic occurrence bindings; new-symbol definitions and reuse
  alignment reasons remain model-authored. Selection and formalization each use
  ModelCalls, counting, reservations, cache identity and receipts. Previous rejected
  formulas are not reused or relabelled.
- **D2-S1 fixed:** `directional-prerequisites-v1` follows a selected conclusion to
  its supporting inference links, then their premises and qualifiers, recursively;
  applicable qualifications/distinctions are prerequisites too. It never follows a
  shared premise to other consequences or a qualifier to its other targets. It
  conservatively includes all stated supporting links for a chosen conclusion.
  Shared-premise and shared-qualifier tests have direct production mutations.
  Plan version is `rich-working-t-v3`; methodology discloses each closure receipt.
- **D2-S2 fixed:** the raw paid response and measured usage/cost are durably logged
  before parsing or fallible follow-up counting. Operational validation/count
  failures keep actual billing and response data, prevent cache/freeze, and record
  rejection. A transient terminal-log failure recovers the durable measured
  receipt. The exact 100-input/50-output, USD0.00175 follow-up-counter failure is
  covered. Malformed JSON with known usage is now an accounted rejection rather
  than an unknown reservation. Unusable nonserializable provider objects retain
  the pre-existing conservative unknown-result handling.
- **D2-N1 fixed additively:** methodology now supplies `measured_usage`,
  `unknown_usage_reservations` and `budget_accounted` totals for aggregate, local,
  inherited and extraction scopes, with both tokens and USD. Legacy numeric totals
  remain budget-accounted. Sibling-run campaign reservations still need the
  separate campaign ledger; successful current-log accounting cannot erase them.
- **D2-N2 addressed within this round's scope:** Sonnet extraction, unambiguous
  inference/node wire shapes and removal of generated exact text/citations/bindings
  target measured cost drivers without lowering rich output limits. Generic
  partial-formula patch/reuse remains deferred (GX24): a correct implementation
  needs item-level validation/alignment and provenance/cache handling; it is not a
  cheap safe retry. This live round uses one validation attempt and stops on the
  first failed phase. Large-source/subgraph packing and redistribution of unused
  working allowances remain limits, not silently claimed fixes.

The stage configuration is `stages.extraction`, not the similarly named budget
profile. It selects `claude-sonnet-5-5`, `fallbacks: []`, high effort and adaptive
thinking. Build T, search and writing retain Opus 5. Model/effort/thinking/fallback
settings enter cache identity and receipts; admission and preflight use the stage's
requested-model price. The provider's Sonnet overview confirms adaptive thinking,
high default effort and 128K maximum output; the runtime retains its counted 32K
extraction allowance and 200K context guard.

Published Sonnet pricing checked on 2026-10-21:
https://platform.claude.com/docs/en/about-claude/pricing — USD2/M input, USD10/M
output, USD0.10/M cache reads, USD2.50/M five-minute writes and USD4/M one-hour
writes. Receipt: `runs/gamma-round3/pricing-receipt.json`; raw page and model overview
are saved alongside it. These token/cache rates are verified, not guessed. No
lower-effort saving is claimed; only 465 of the prior sample's extraction output
tokens were reported as thinking, so high/adaptive was retained.

### Round-3 verification and review scope

The final full suite passed **327 tests, with 2 opt-in live skips, 329 collected**
in **139.10 seconds**. Receipt: `runs/gamma-round3/pytest-final.txt`. The new targeted
set passed 49 tests; 18 new/strengthened mutation checks each failed red and restored
green. A full control run was intentionally interrupted and restored before
strengthening a fixture: the missing-inventory case now removes unrelated symbol
references so the inventory control cannot pass through a different guard. The
final complete 124-control result is recorded below; no pytest process overlaps
its mutation runner.

Closure, attribution, citation and alignment cases now call `prepare_commitments`
directly and assert no freeze/file on rejection. They no longer rely on a later
uncanned target request failing. The 53-paper native CLI test still exercises
multiple batches, 424 commitments, all source IDs, cache replay, reversed merge,
HUMAN/MODEL receipts and one freeze, using placeholder graphs only. Its SDK fake
now reports the actual requested stage model in each response.

Code review: skipped (ce-code-review unavailable). The full workflow requires
separate review/finish agents, conflicting with solo work. A manual diff scan
covered stage pricing/routing, obligations, directional closure, fixed inventory,
source copying, semantic alignment, measured receipts and freeze order. It is not
independent. The ce-simplify-code lenses were applied inline under that constraint;
no further behavior-preserving rewrite or test deletion was justified. No lint or
typecheck command is configured. Receipt: `runs/gamma-round3/review.json`.
Delta's independent re-review remains the explicit gate before any full extraction.

### Round-3 final verification and committed state

Final HEAD: **`e97f9efbafbc16c83fcf44d84877b065efe6078f`** —
`Build fixed prerequisite inventories with stage-priced extraction`.
The complete runner finished **124/124 red, 124/124 restored green**, exit 0.
The full suite was **327 passed / 329 collected, 2 skipped**, exit 0, 139.10s.
No tests ran concurrently with mutations. `git diff --check` passed; all temporary
mutations were restored. Source is committed locally, with no push.

Receipts:

- `runs/gamma-round3/pytest-final.txt`
- `runs/gamma-round3/negative-controls-final.txt`
- `runs/gamma-round3/controls/results.json` and the copied red/green logs
- `/home/dev/ara-work/reports/gamma-round3-verification.json`

The paid call below ran at this committed head after both gates passed. No source
change or paid retry followed its failure.

### Round-3 live phase 3a — rejected; stop rule applied

**Status: BLOCKED — Sonnet extraction produced an invalid graph.** The first call,
for `rothschild2012` (13 physical pages), returned provider/schema-readable JSON
but failed local graph validation with `invalid qualification relation`.
Six nodes used `applies_to` where only distinction/qualification nodes may use it:
three premises and three intermediate conclusions. The candidate also had **zero
inference nodes**, versus 12 in the accepted Opus extraction. All candidate
reference endpoints existed, but that does not make these relations valid.

The candidate claimed complete coverage and no unresolved references. Those claims
were not accepted. Validation stopped at the invalid qualification relation;
remaining validation and semantic fidelity are not established. No range graph,
per-paper extraction artifact or literature collection was published. The raw paid
response remains in the append-only ignored log with its actual measured usage.
The wire repair eliminated non-inference *inference fields*, but `applies_to`
remains available in the wire node shape and locally constrained by kind; this
attempt exposed that remaining shape risk. It must not be silently converted into
inference edges by code.

| Receipt | Result |
| --- | --- |
| Requested / served model | `claude-sonnet-5-5` / `claude-sonnet-5-5` |
| Settings | high effort, adaptive thinking, no fallback |
| Actual input / output tokens | 16,990 / 11,889 |
| Thinking tokens included in output | 3,884 |
| Cache read / write tokens; server-tool uses | 0 / 0; 0 |
| Measured cost | **USD0.152870** |
| Provider / command seconds | 74.31 / 77.12 |
| Acceptance | Rejected by graph validation; no accepted extraction |
| Candidate / accepted item count | 54 / 0 |

Per the brief's **“Stop at the first failure and report”**, `kolodnymacfarlane2010`
was **not attempted** with Sonnet. Phase 3b was **not attempted**. There were no
root-selection or formalization calls, no merge, and no freeze. Phase 3c was not
run, and no successful round-3 corpus cost projection is inferred from this failed
single-paper response. Unused budget does not override the stop instruction.

Counts below compare the prior **accepted Opus artifacts** with this round's
**rejected Sonnet candidate**, not two accepted extractions. A dash means not
attempted, not zero evidence in the source.

| Kind | Shortest: Opus accepted | Shortest: Sonnet rejected | Partial: Opus accepted | Partial: Sonnet |
| --- | ---: | ---: | ---: | ---: |
| premise | 23 | 25 | 50 | — |
| inference | 12 | 0 | 14 | — |
| intermediate_conclusion | 11 | 10 | 12 | — |
| conclusion | 3 | 3 | 3 | — |
| distinction | 1 | 0 | 3 | — |
| qualification | 8 | 6 | 14 | — |
| reported_view | 5 | 5 | 4 | — |
| attacked_view | 5 | 5 | 8 | — |
| Total | 68 | 54 | 108 | — |

Prior Opus cost remains USD0.872330 for the shortest paper including its rejected
attempt/correction, and USD0.789880 for the partial paper. Sonnet's lower price and
this lower failed-call bill do **not** establish equal quality or successful
extraction savings. One rejection does not establish that Sonnet is incapable of
the task; the configured choice remains unvalidated for the requested rich graph.
No model switch or effort reduction was made after this result.

New receipts/artifacts:

- `runs/gamma-round3/extract-receipt.json`
- `runs/gamma-round3/extraction/events.jsonl`
- `runs/gamma-round3/extraction/export/methodology.md`
- `runs/gamma-round3/rejected-extraction-diagnostic.json`
- `/home/dev/ara-work/reports/gamma-round3-live-receipts.json`

Both accepted Opus artifacts remain untouched under
`runs/gamma-round2-live-attempt3/extraction/`. All new raw real content remains
under ignored `runs/gamma-round3/`; no real source content entered the commit.

### Round-3 budgets, pilot handoff and remaining gate

| Scope | Measured USD | Unknown reservations USD | Accounted USD |
| --- | ---: | ---: | ---: |
| This round | 0.152870 | 0.000000 | 0.152870 |
| Previous rounds retained | 3.059635 | 3.934240 | 6.993875 |
| Combined campaign | 3.212505 | 3.934240 | 7.146745 |

The new USD3 extraction allowance has USD2.847130 unused. The separate build-T
campaign remains **USD3.573285 accounted against USD6**, leaving **USD2.426715**;
no new build spend occurred. Prior unknown reservations are still held, not
reclassified as actual charges or free requests. The task-line `live_usd` means
this round's measured USD0.152870, not the combined campaign figure.

**Frozen T path: none. Commitment count: 0. Papers successfully extracted this
round: 0. Exact artifact for alpha's pilot: none available from round 3.** The
intended path `/home/dev/ara-work/gamma/runs/gamma-round3/extraction/literature.extracted.txt`
does not exist and must not be passed to a pilot. A rejected response is not a
literature artifact. The earlier Opus artifacts remain inspectable, but this round
does not label them a completed substitute for the required Sonnet/build-T gate.

Next unresolved work is operator-directed recovery of phase 3a: review the wire
representation of `applies_to` and the missing inference structure, repair/prove
any change offline, then authorize the next bounded live check. Do not weaken the
relation guard or invent inference links from these invalid relations. This round
stops without another paid call. After a future successful 3a/3b, Delta's independent
review still precedes any full extraction under the brain addendum. The 358-page
source, real range reconciliation/cross-batch alignment, proportional allowances,
semantic fidelity and general targeted formula correction remain the previously
disclosed limits.

### Round-3 findings placement

| Action-changing finding | Deliverable section carrying it |
| --- | --- |
| Explicit unresolved obligations now require auditable accepted evidence; semantic adequacy is still model-assessed | Round-3 implementation and review dispositions: D2-B1 |
| Directional closure replaces whole-component expansion and retains all stated support | Round-3 implementation and review dispositions: D2-S1 |
| ALT fixed-inventory construction is implemented offline; its new live merge/freeze remains unproved | Round-3 implementation and review dispositions: D2-B2; live phase 3a; budgets and pilot handoff |
| Measured responses survive parsing, counting and transient terminal-log failures | Round-3 implementation and review dispositions: D2-S2; verification and review scope |
| Methodology separates measured/reserved/accounted scopes; prior campaign reservations remain held | Round-3 implementation and review dispositions: D2-N1; budgets and pilot handoff |
| Sonnet pricing is verified and stage-scoped; high/adaptive remains unchanged and model suitability is unvalidated | Round-3 implementation and review dispositions; live phase 3a |
| Sonnet candidate had invalid qualification relations and no inference nodes; stop rule prevented remaining live checks | Round-3 live phase 3a |
| No round-3 accepted paper, frozen T, pilot input or successful cost projection exists; review gate remains before full extraction | Round-3 budgets, pilot handoff and remaining gate |
| Targeted partial-formula repair and large/skewed corpus capacity remain deferred limits | Round-3 implementation and review dispositions: D2-N2; budgets and pilot handoff |
| Offline suite/124 controls pass at local committed head; solo scan is not independent review | Round-3 verification and review scope; final verification and committed state |

**10 findings, 10 placed.** Final status is
`blocked:sonnet-extraction-invalid-graph`. There is no active API call, test process
or background worker. All authorized work up to the brief's mandatory first-failure
stop has been performed and reported; no full extraction or push occurred.


## Round 3b

**Outcome: blocked at ALT root selection; no frozen T.** Sonnet accepted **0/2**
papers. The required build attempt ran using the accepted **Opus** artifacts and
stopped when root selection exhausted its output allowance. New measured spend was
**USD0.858150**, with no new unknown reservation. No full extraction, pilot, or
push ran. All authorized live attempts are complete; Delta review is next.

Local committed head: `afdc0321299d18ccfa34c40114a7ebf9e73337a9` on `feat/paper-extraction`.
The checkout is clean. Implementation, verification and live receipts refer to this
same revision.

### Round-3b implementation and limits

GX25 implements three disjoint provider-wire kind families. Only distinction and
qualification nodes carry `applies_to`; inference nodes carry premise/conclusion
and qualification edges. The prompt explicitly requires paper-stated inference
nodes. Runtime supplies only omitted empty structural defaults, then applies the
unchanged local relation guards. It never converts invalid relations into edges.

The live config sets `extraction_targeted_corrections=1` and
`extraction_require_inference=true`. The former replaces generic full-response
retries with at most one counted correction across the entire paper, including
ranges and reconciliation. Corrections return only changed/new items, retain
omitted items, reject unchanged retransmissions, and revalidate the merged graph.
They use the normal admission, budget, log and cache boundary. Malformed or
ambiguous inventories cannot use this path. The latter requires nonzero inference
counts at whole-paper/reconciliation acceptance. These are explicit runtime
settings for the bounded check; generic callers without them retain their prior
policy. No new accepted extraction artifact or accepted cache response was created.

This implements targeted **extraction** repair. General targeted formula repair
remains deferred. Structural validity and nonzero counts do not establish semantic
faithfulness or completeness; neither the prompt's coverage flag nor a count is
independent evidence of either.

### Round-3b verification and review scope

- Full pytest: **337 passed, 2 skipped, 339 collected**, 169.33 seconds.
- Full controls: **131/131 mutations failed, 131/131 restorations passed**. Seven
  new controls cover wire relations, grammar size, nonzero inference acceptance,
  retained inventory, unchanged-item rejection, the paper-wide correction limit,
  and the unchanged local relation guard.
- Proof-first: nine new/strengthened checks failed before implementation. Focused
  tests subsequently passed, including correction admission before dispatch.
- Grammar: **2,724 bytes, three flat alternatives, 29 properties**, with unique
  kind assignments and no recursive references. Both live Sonnet requests and
  their corrections reached the provider and returned responses, so the service
  accepted the projected grammar. This does not establish extraction quality.
- The first control attempt stopped after a mutation anchor became ambiguous
  between two uniqueness guards. Its receipts were preserved; the anchor was
  narrowed to the original extraction guard's exact reason. The complete runner
  then passed. Production code was unchanged from the full-suite revision.
- `git diff --check` passed. No separate lint/typecheck is configured in this
  Python repository. The simplification pass and manual diff scan were solo.

**Code review: skipped (ce-code-review unavailable).** Its independent reviewer
workflow requires delegation, prohibited by this task's solo constraint. This is
not an independent review receipt; Delta's review remains required.

Evidence: `runs/gamma-round3b/pytest-final.txt`, `pytest-proof-first.txt`,
`negative-controls-final.txt`, `controls/`, `grammar-size.json`, `verification.json`;
failed-run evidence is in `negative-controls-attempt1.txt` and `controls-attempt1/`.
The external verification receipt is
`/home/dev/ara-work/reports/gamma-round3b-verification.json`.

### Round-3b Sonnet retry outcomes and Opus comparison

All four extraction calls requested and were served by `claude-sonnet-5-5`,
high effort/adaptive thinking, no fallback or cache hit. Each paper received
exactly one targeted correction. The per-paper total costs were USD0.186628 and
USD0.202662, respectively; the extraction command took 131.19 seconds overall.

- `rothschild2012` (13 physical pages): initial response had one inference with
  page bounds of zero, failing canonical schema validation. Its correction
  produced a 55-item candidate with 12 inference nodes, but one item used
  `rothschild2012,` (extra comma) as its source ID. The source-identity guard
  rejected the graph. No ID was silently repaired, and no second correction ran.
  Other validation after the first failing guard is not claimed to have passed.
- `kolodnymacfarlane2010` (31 readable physical pages): initial candidate had seven
  items and zero inference nodes. Its correction emitted three intermediate
  conclusions, resulting in a nine-item merged candidate, still with zero
  inferences. The new acceptance guard rejected both. Existing private-use-glyph
  warnings on pages **1, 4, 5, 6, 8, 9, 30, 31** remain disclosed. Partial-source
  processing was allowed; those pages were retained as readable, not omitted.

Accepted Sonnet counts are zero for every kind on both papers. For diagnostic
comparison, the following columns show **final rejected merged candidates**, not
accepted evidence, beside the untouched accepted Opus graphs:

| Kind | First paper Opus accepted | First paper Sonnet rejected | Second paper Opus accepted | Second paper Sonnet rejected |
| --- | ---: | ---: | ---: | ---: |
| premise | 23 | 20 | 50 | 4 |
| inference | 12 | 12 | 14 | 0 |
| intermediate_conclusion | 11 | 10 | 12 | 4 |
| conclusion | 3 | 2 | 3 | 0 |
| distinction | 1 | 1 | 3 | 0 |
| qualification | 8 | 5 | 14 | 0 |
| reported_view | 5 | 2 | 4 | 0 |
| attacked_view | 5 | 3 | 8 | 1 |
| **Total** | **68** | **55** | **108** | **9** |

No invalid `applies_to` relation appeared in any of this round's four responses.
The wire repair therefore removed that observed failure in these calls, but Sonnet
still failed the complete acceptance contract. These results do not establish that
another model/configuration would pass. Do not use the rejected candidates as
literature artifacts.

### Round-3b ALT build result and pilot handoff

The build used the production provenance importer with the original accepted Opus
collection at:
`/home/dev/ara-work/gamma/runs/gamma-round2-live-attempt3/extraction/literature.extracted.txt`.
The receipt explicitly labels `source_model=opus`; imported extraction charges of
**USD1.662210** are historical receipts, not new build spend. Original provenance
was revalidated and the prior artifacts were retained untouched.

The one ALT lifecycle dispatched `select_t_roots` to `claude-opus-5`, high/adaptive,
no fallback. It used **52,812 input tokens and 8,192 output tokens**, including
**6,176 thinking tokens**, and returned `stop_reason=max_tokens`. The response was
rejected before parsing or accepting roots. Provider time was **99.25 seconds**;
command time was **101.55 seconds**; measured cost was **USD0.468860**.

The root-selection stage still uses the general **8,192-token output allowance**;
the separate larger batch-formalization allowance does not apply to it. This is
the concrete next recovery point for review. A future repair must preserve the
complete root/omission inventory and counted budget admission. This report does
not authorize another paid attempt merely because funds remain.

**Accepted batches: 0. Merges: 0. Freezes: 0. Commitments: 0. Frozen T path: none.**
Only the construction plan, rejected raw response, logs and exports exist under
`runs/gamma-round3b/construction/`. `build_t_batch` never dispatched. There is no
completed artifact for alpha's pilot from this round. The source-literature path
above is valid input for a future reviewed build, not a frozen-T substitute.

No 3c/full-corpus extraction or pilot ran. Previously disclosed large-source,
real range-reconciliation, cross-batch semantic-alignment, proportional-capacity,
and semantic-fidelity limits remain unproved by this failed two-paper lifecycle.

### Round-3b usage, budgets and receipts

Thinking is included in output tokens and is not charged twice. All five new
requests have measured actual usage; none has unknown usage, a fallback, or a
cache hit.

| Call | Input | Output | Thinking (included) | USD | Provider seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| rothschild2012 / initial | 17,531 | 162 | 0 | 0.036682 | 5.89 |
| rothschild2012 / targeted_correction | 17,818 | 11,431 | 3,741 | 0.149946 | 67.31 |
| kolodnymacfarlane2010 / initial | 33,026 | 4,837 | 3,865 | 0.114422 | 37.29 |
| kolodnymacfarlane2010 / targeted_correction | 34,035 | 2,017 | 1,614 | 0.088240 | 16.97 |
| ALT root selection / initial | 52,812 | 8,192 | 6,176 | 0.468860 | 99.25 |

| Scope | Measured USD | Unknown reservations USD | Accounted USD |
| --- | ---: | ---: | ---: |
| New Sonnet extraction | 0.389290 | 0.000000 | 0.389290 |
| New Opus build attempt | 0.468860 | 0.000000 | 0.468860 |
| **Round 3b total** | **0.858150** | **0.000000** | **0.858150** |
| Previous rounds retained | 3.212505 | 3.934240 | 7.146745 |
| **Campaign total** | **4.070655** | **3.934240** | **8.004895** |

The extraction allowance has **USD2.457840** remaining from its opening
USD2.847130. The independent build allowance has **USD1.957855** remaining from
USD2.426715; build-campaign accounted cost is now USD4.042145 against USD6.
No extraction remainder was transferred to build, and every prior unknown
reservation remains held. The native enclosing build cap included inherited
extraction receipts plus the authorized local build remainder; only USD0.468860
is new build spending. `live_usd` in the final task line means this round's measured
USD0.858150, excluding reused receipts and prior rounds.

Primary receipts are `runs/gamma-round3b/extract-receipt.json`,
`build-receipt.json`, `live-summary.json`, `rejected-candidate-diagnostics.json`,
the per-paper `extraction/<source>/events.jsonl` and `export/methodology.md`, and
`construction/events.jsonl` with `construction/export/methodology.md`.
The consolidated external receipt is
`/home/dev/ara-work/reports/gamma-round3b-live-receipts.json`.
All new real responses remain in ignored `runs/`; tracked code, tests, prompts,
decisions and the commit contain no real source arguments.

### Round-3b findings placement

| Action-changing finding | Deliverable section carrying it |
| --- | --- |
| Kind-discriminated wire excludes illegal relations; guards remain intact and live grammar acceptance is distinct from quality | Implementation and limits; verification and review scope; Sonnet outcomes |
| One targeted correction preserves omitted evidence and remains counted; formula repair is still deferred | Implementation and limits; verification and review scope |
| Nonzero inference is an explicit acceptance setting and does not prove semantic fidelity or coverage | Implementation and limits; Sonnet outcomes |
| Both Sonnet papers remain rejected; per-kind candidate counts must not be mistaken for accepted evidence | Sonnet retry outcomes and Opus comparison |
| Required Opus fallback build ran but root selection exhausted 8,192 output tokens, leaving no batch, merge or freeze | ALT build result and pilot handoff |
| Partial-source glyph warnings remain on eight pages | Sonnet retry outcomes and Opus comparison |
| Actual spend, independent remaining caps and historical unknown reservations remain separated | Usage, budgets and receipts |
| Full suite and 131 controls pass; first control-run anchor failure was repaired and retained | Verification and review scope |
| Solo scan is not independent CE review; Delta's review is outstanding | Verification and review scope |
| No pilot/frozen T or full extraction exists; large-source and semantic integration limits remain unresolved | ALT build result and pilot handoff |

**10 findings, 10 placed.** Final status:
`blocked:build-root-selection-max-tokens`. No additional paid request is authorized
by this completed round. The next unresolved step is Delta's review of these
receipts and the root-selection output allowance. No push occurred.


## Round 3c

**Outcome: awaiting review.** The authorized ALT lifecycle succeeded on the
accepted Opus collection: **accepted roots, accepted formalization, one merge,
and exactly one freeze containing 45 commitments**. Neither stage required a
correction. New measured spend was **USD1.391215**, leaving **USD0.566640** of the
remaining build allowance. No extraction, full-corpus run, pilot, or push occurred.
Sonnet extractions remain rejected; their model and budget decision remains with
the operator.

Local committed head: `1b152d9c78c9c30851b48d106359cb796bcedc61` on `feat/paper-extraction`, clean.
Frozen T: **`/home/dev/ara-work/gamma/runs/gamma-round3c/construction/commitments.json`**.
Frozen-file SHA-256: `25a7ec8c35d393b230738e6008467d70926697db6bed1f91c72b5edcd39cb3a4`.

### Round-3c root allowance and compact inventory

GX26 adds `select_t_roots_max_output_tokens: 16384`. The prior 8192-token response
exhausted its allowance, with 6176 tokens spent on thinking. Doubling the allowance
leaves 10208 tokens beyond that observed thinking usage for the response and
variation. This is a bounded allowance, not a guarantee about future thinking.
The existing stage-specific request, token/context admission, monetary reservation
and cache identity all use it. High/adaptive is unchanged.

Selection schema v2 returns short root IDs and omission decisions keyed by supplied
group IDs. A deterministic catalogue assigns every original item a short ID and
partitions items by source, kind, attribution and speaker. These are metadata
partitions, **not inferred semantic equivalences or argument groupings**. The
model supplies the roots and group-specific reasons. Each reason covers all
non-root members of that group; code validates the complete inventory, expands
the aliases, then computes the existing directional prerequisite closure. Needed
prerequisites leave the omission list automatically and visibly in the closure log.
Unknown/duplicate groups, unknown roots, missing coverage and blank reasons fail.
Full source items stay in the counted request and immutable source artifacts.

The plan version is now `rich-working-t-v4`. New prompt/schema/cache identities
prevent old selection responses from replaying as the new wire. The placeholder
176-item, one-group example reduced the response from **2719 bytes to 85 bytes**
while preserving all item mappings. This is a shape regression, not a projection
for real papers: the live 176-item collection produced **46 metadata groups** and
46 omission decisions. The catalogue adds input overhead, disclosed below.

### Round-3c bounded correction and run configuration

`construction_targeted_corrections=1` permits at most one counted correction per
stage across the lifecycle, including all batches. A parseable, unambiguous
candidate may receive keyed additions/replacements of omission groups or
commitments/symbols/alignments. Selection supplies its complete short root list and
relevance; unchanged collection entries must be omitted and are retained by code.
The merged response must pass the original schema, inventory, symbol and capacity
checks. Each patch uses normal counted admission, reservation, logging and caching.
Malformed/ambiguous inventories, transport truncation and entry deletion are not
supported by this patch protocol. No full-response regeneration is used under this
setting. Offline tests exercise both stages; **no live correction was needed**, so
live correction behavior is not claimed as newly demonstrated.

The bounded live invocation used root output allowance **16384** and a per-run
formalization ceiling of **32000** so its reservation could fit after root selection
within the remaining **USD1.957855**. The ordinary formalization default remains
64000. Counted admission, the 200000-token context guard, shared-symbol checks,
exact fixed-inventory validation and final working-context admission stayed active.
Global fallback was off. The native enclosing cost cap was **USD3.620065**:
USD1.662210 in imported extraction receipts plus USD1.957855 of authorized new
build allowance. Historical import costs are not new spending.

Extraction source, call boundary, provider, prompt, schema and extraction settings
were verified unchanged from `afdc032`. No extraction request was dispatched.

### Round-3c verification and review scope

- Full pytest: **354 passed, 2 skipped, 356 collected**, 142.68 seconds.
- Full negative-control runner: **139/139 mutations failed and 139/139 restored
  versions passed**. The 11 affected controls also passed before the full run.
- Proof-first checks exposed seven selection/allowance failures and six correction
  failures before implementation. The final new focused file has 17 passing cases,
  covering complete group expansion, mixed selected/omitted groups, invalid
  inventories, context and money admission, stage cache identity, compact response
  size, correction retention/revalidation and correction admission.
- The code and tests were manually scanned using the simplification/review rubrics;
  no blocker remained. `git diff --check` passed. No separate lint/typecheck is
  configured. Tests and the mutation runner ran sequentially, and all mutated
  production files were restored before commit.

**Code review: skipped (ce-code-review unavailable).** Its required independent
reviewer dispatch conflicts with the solo-task constraint. The manual scan is not
an independent review receipt; Delta's review is still outstanding.

Evidence under `runs/gamma-round3c/`: `pytest-final.txt`, `pytest-targeted.txt`,
`pytest-proof-first.txt`, `pytest-correction-proof-first.txt`,
`negative-controls-final.txt`, `controls/`, `controls-focused/`,
`compact-shape.json`, `verification.json` and `artifact-audit.json`.
External verification receipt:
`/home/dev/ara-work/reports/gamma-round3c-verification.json`.

### Round-3c live result and frozen artifact

Source collection:
`/home/dev/ara-work/gamma/runs/gamma-round2-live-attempt3/extraction/literature.extracted.txt`.
Its original Opus provenance was revalidated and imported through the production
path. The two source graphs retain all **176** items. Their originals and every
prior failed receipt remain intact. The receipt labels `source_model=opus`.

Root selection accepted two roots, one from each paper. Directional closure added
43 prerequisite items, yielding **45 fixed items**; **131** remaining items have
explicit omission reasons. Formalization returned exactly that fixed inventory,
then the native lifecycle merged and froze once. There were two new model calls,
both requested and served by `claude-opus-5`, high effort/adaptive thinking,
without fallback, cache hit, rejection, correction, or unknown usage.

| Stage | Output allowance | Input tokens | Output tokens | Thinking included in output | USD | Provider seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Root selection | 16384 | 58510 | 7561 | 4401 | 0.481575 | 102.52 |
| Fixed-inventory formalization | 32000 | 32768 | 29832 | 11390 | 0.909640 | 281.91 |

Total command time: **387.21 seconds**. Thinking is included in output tokens and
is not charged twice. Root selection completed below even the former 8192-token
allowance on this run; the compact representation and larger allowance changed
together, so this receipt does not isolate their causal effects. Compared with the
previous rejected root call, input increased from 52812 to 58510, output decreased
from 8192 to 7561, and cost rose from USD0.468860 to USD0.481575. The result is a
complete accepted inventory, not a demonstrated per-call cost reduction.

Frozen commitment counts:

| Source | Commitments |
| --- | ---: |
| rothschild2012 | 23 |
| kolodnymacfarlane2010 | 22 |
| **Total** | **45** |

| Evidence kind | Commitments |
| --- | ---: |
| premise | 18 |
| inference | 8 |
| intermediate_conclusion | 7 |
| conclusion | 1 |
| distinction | 3 |
| qualification | 5 |
| reported_view | 2 |
| attacked_view | 1 |

The local artifact audit checked the frozen file against its log,
its selected IDs against the fixed inventory, exact attributed text/citation
copies against the immutable source items, every inference endpoint/qualifier,
applicable distinctions/qualifications, and the disjoint 45+131 inventory partition.
It confirmed one freeze and no target-generation, search or pilot model dispatch.
These checks establish structural/provenance consistency; they do not independently
establish semantic fidelity of extraction, relevance decisions or formulas.

The second paper remains **partial**, with retained private-use-glyph warnings on
physical pages **1, 4, 5, 6, 8, 9, 30, 31** in its original diagnostics. That
limitation carries into this T and still requires source inspection. No source
quality warning was cleared by successful formalization. Large-source capacity,
real range reconciliation and cross-batch semantic alignment are not newly proved
by this one-batch, two-paper build.

The exact frozen T for review is:
`/home/dev/ara-work/gamma/runs/gamma-round3c/construction/commitments.json`.
Its supporting catalogue, closure, batch receipt, merged working T and provenance
are in that directory and its `events.jsonl`. No pilot was run; no command to start
one is implied by availability of the artifact.

### Round-3c accounting and receipts

| Scope | Measured USD | Unknown reservations USD | Accounted USD |
| --- | ---: | ---: | ---: |
| **New round-3c build** | **1.391215** | **0.000000** | **1.391215** |
| Previous rounds retained | 4.070655 | 3.934240 | 8.004895 |
| **Combined campaign** | **5.461870** | **3.934240** | **9.396110** |

The build campaign is now **USD5.433360 accounted against USD6**, leaving
**USD0.566640**. Its historical unknown-reservation component remains
USD2.175860; all campaign unknown reservations remain USD3.934240. None were
released, reclassified or reallocated. The prior extraction allowance balance of
USD2.457840 is unchanged and is not permission for another extraction; its model
and budget remain the operator's decision. `live_usd` means this round's new
measured USD1.391215, excluding imported receipts and previous rounds.

Primary receipts: `runs/gamma-round3c/build-receipt.json`,
`construction/events.jsonl`, `construction/export/methodology.md`,
`live-config.yaml` and `artifact-audit.json`. Consolidated external receipt:
`/home/dev/ara-work/reports/gamma-round3c-live-receipts.json`.
All real responses and generated artifacts remain under ignored `runs/`; the
tracked change and commit contain only topic-neutral contracts and placeholder
proofs. No push occurred.

### Round-3c findings placement

| Action-changing finding | Deliverable section carrying it |
| --- | --- |
| Root selection has a measured, stage-specific 16384-token allowance with counted context/cost admission and cache identity | Root allowance and compact inventory; verification and review scope |
| Short IDs and metadata omission groups preserve the full inventory but add input overhead; this is not a proven cost reduction | Root allowance and compact inventory; live result and frozen artifact |
| One targeted correction per stage is bounded and revalidated; deletion/truncation repair is unsupported and no live correction was needed | Bounded correction and run configuration |
| Accepted roots and exact formalization produced 45 commitments, one merge and exactly one auditable freeze | Live result and frozen artifact |
| Partial-source glyph warnings and semantic/cross-batch limits survive successful structural validation | Live result and frozen artifact |
| New measured spend fits the separate remaining build cap; prior reservations and extraction funds remain intact | Accounting and receipts; bounded correction and run configuration |
| Full suite and all 139 controls pass at the local committed head | Verification and review scope |
| Solo scan does not replace independent review; Delta's review is pending | Verification and review scope |
| Sonnet remains rejected; no full extraction, pilot or push ran | Outcome; bounded correction and run configuration; live result and frozen artifact |

**9 findings, 9 placed.** Final status is `awaiting-review`. The authorized
construction lifecycle is complete, no live call or test process remains active,
and the next step is review of the frozen T and these receipts.

## Round 4

Subject: `feat/paper-extraction`, final HEAD **be8c2c2ee2adaf491a8a31bb38640d40e287cebc**. Starting revision
`1b152d9c78c9c30851b48d106359cb796bcedc61`. Read Delta's entire Re-review round 3.
Implemented D3-S1/S2/S3, then D3-B2/B1, then the unpaid 26-PDF plan. No paid
generation, push, pilot, worker or subagent. Status: **awaiting-review**.

Local commits: `851022f` (policy, empty stages and global capacity), `783e8b4`
(bounded graph/obligation windows), and `be8c2c2ee2adaf491a8a31bb38640d40e287cebc` (unpaid planner and final
native-profile, prior-context and remaining-allowance refinements).

### Policy and capacity changes

- **D3-S1:** `extraction-full` explicitly selects `claude-opus-5` at the extraction
  stage, with no fallback, aggregate nonzero-inference acceptance, and one targeted
  correction per paper. The model remains editable in one stage line. Enclosing
  token/cost caps and extraction cost cap are `null`; generation refuses before
  provider creation until the operator fills all three. Historical profiles retain
  their earlier defaults, including their extraction model and optional policies.
  Native `ara run --profile extraction-full` accepts the same profile and preflights
  its caps, so catalogue size and construction corrections reach the actual build.
- **D3-S2:** an empty readable range needs a complete, obligation-free model-authored
  reason, persisted with physical page IDs. This cannot erase pending references or
  bypass aggregate inference acceptance. A zero-root window must account for every
  omission group, skips formalization and participates in the lifecycle. Overall
  empty T still refuses; a large source can have empty windows and a successful T.
- **D3-S3:** working capacity is cumulative and measured against actual accepted T;
  unused capacity carries forward and each root-selection request receives that
  same measured remaining allowance. Before formalization the runtime counts the exact
  source-copy payload in a minimal formula envelope, the catalogue and the remaining
  global capacity. Full profile uses a configurable 256-token/selected-item catalogue
  growth reservation and a 32k catalogue limit. Historical profiles use zero growth
  reservation; actual catalogue growth remains checked. These are planning bounds,
  not predictions of formulas or semantic reuse. The two-rich-batch proof accepts
  16 distinct named symbols near a 19k catalogue limit and 16 commitments under a
  10k working limit. Capacity refusals retain logged roots/closures for explicit
  revised selection; there is no automatic budget-driven root reselection.
- **D3-B2:** a shared counted partitioner windows within a large source. Selection
  sees bounded evidence; closure uses the full immutable graph. Exact IDs already
  formalized are reused, with prior formulas and supporting source evidence supplied
  to later formalization. Every counted formalization inventory is fixed, and an
  oversized required closure refuses before dispatch rather than losing support.
  Final selected/omitted accounting covers the whole graph; one merge and freeze.
- **D3-B1:** reconciliation never reconstructs one unbounded whole-paper request.
  No-obligation review traverses bounded graph windows; discovered gaps receive
  stable IDs. Each obligation traverses counted original-page/evidence windows,
  accounting for itself as resolved or pending on every turn. Models can request
  complete next page/evidence sets; unknown/unread IDs, oversized required sets,
  request cycles or the 16-request default limit refuse without discarding context.
  Pending ledgers and accepted range/window artifacts survive refusal. A resolved
  ledger cannot coexist with an unexplained remaining reference. Runtime validates
  inventory and provenance; semantic adequacy remains a source-review judgment.

### Executed proof and review limits

- Final `uv run pytest -q`: **373 passed, 2 skipped, 375 collected (257.15s)**, log `runs/gamma-round4/pytest-final.txt`.
- Final complete control runner: **154/154 red, all 154 restored green, exit 0**, run only after pytest ended;
  results and actual red/restored traces are in `runs/gamma-round4/controls/`.
- New tests first failed against the old paths. Offline proof includes a 98-item
  single source larger than one context, 8 selected items plus 90 accounted
  omissions, cross-window prerequisites and one freeze; overlapping closures reuse
  prior formulas/support without duplicate evidence. A six-page source exceeding
  one context resolves a cross-window obligation after explicitly requesting pages
  1 and 6. Its unresolved variant refuses. A graph-only union larger than context
  traverses bounded review windows without omission. Oversized selected closures
  and catalogue growth refuse before formalization. Fixtures contain placeholders.
- Initial full-suite attempts exposed the historical low-density growth-reservation
  mismatch and a refusal-message regression; targeted repairs passed. Manual source
  inspection found the missing prior-context payload, added before the final suite.
  The final diff audit also corrected root selection to receive the measured
  remaining budget; its two-rich-batch regression first failed on the stale full
  allowance, then passed. Earlier failed test receipts remain in `runs/gamma-round4/`. Mutation-anchor
  audit caught a control-script quoting error and relocated anchors before execution.
- Inline simplification removed duplicated selection rendering and obsolete
  proportional/all-paper packing. No lint/typecheck command is configured.
  **Code review: skipped (ce-code-review unavailable)** — its independent delegated
  review workflow conflicts with the explicit solo restriction. No completed CE
  independent-review receipt is claimed; this handoff is for Delta's next review.
  [ce-code-review SKILL.md](/home/dev/.codex/plugins/cache/compound-engineering-plugin/compound-engineering/3.31.0/skills/ce-code-review/SKILL.md)
  requires “Dispatch the selected local reviewers as one concurrent batch”; that
  delegated workflow was not available under the solo constraint.
  Manual diff inspection covered runtime callers, prompts, schemas, immutable
  artifacts and the source/citation boundary, not real-model semantic fidelity.

### 26-paper unpaid plan

Read the 26 available PDFs under `/home/dev/ara-scaffold/literature/fulltext/`, using
its manifest. The manifest has 53 records; the other 27 missing files were not part
of this requested 26-PDF size check. Native command: `ara plan-extraction --profile
extraction-full --token-counter provider`, with those 26 explicit `--paper-id` values,
the manifest/fulltext paths above, and `--run-dir runs/gamma-round4/plan26`.
The exact argv, PDF hashes, configuration and full counted prompts are retained in
that ignored run directory; the report below contains identifiers and numbers only.

Verified free counting from the official token-counting documentation before API
use: “Token counting is **free to use**”. Receipt:
`runs/gamma-round4/free-count-verification.json`; source document:
`runs/gamma-round4/token-counting-docs.txt`. The numeric plan audit records **106
count requests, zero generation dispatches, zero MODEL events and USD0.000000**.
The planning provider cannot generate and its internal generation caps are zero.

**26/26 initial readable-range plans fit**: 1,379 physical pages, 1,368 readable
pages, 66 ranges, **1,592,920 provider-counted initial input tokens**. Maximum
initial range: **34,808 input + 32,000 output = 66,808**, below 200,000 context.
Execution and planning share the range planner; full profile also splits using a
1,200-output-token/readable-page scenario (prior bounded sample: about 1,150,
including thinking). Actual exhaustion can still require a smaller range.

The table's input counts are provider counts including the runtime's conservative
schema overhead. Selection windows are estimates from 1,270 graph tokens/readable
page, a 70k source batch and 8k wrapper allowance. Actual graphs, root inventories,
closures and catalogues do not exist for this corpus yet, so construction admission
remains conditional; these 38 estimated selection windows are not measured batches.
`fits` means initial readable extraction ranges fit, not full semantic coverage,
spend authorization, or an accepted extraction/build/pilot chain.

Costs use Opus **USD5/M input, USD25/M output**. “Initial” uses counted input plus
1,200 estimated output tokens/readable page. “With review” adds an explicitly
estimated no-obligation graph-review pass: binary windows with 160k graph capacity,
8k wrapper input and 8,192 output/window. This is the final-line cost scenario;
actual obligation scans, context requests, retries, targeted corrections and all
construction/pilot costs are additional and unmeasured.

| Source ID | Pages/readable | Initial ranges | Counted input | Est. selection windows | Admission | Initial USD | With review USD |
|---|---:|---:|---:|---:|---|---:|---:|
| vonfintelgillies2007 | 32/32 | 2 | 37,075 | 1 | fits | 1.145375 | 1.593375 |
| eganweatherson2011 | 21/21 | 1 | 24,309 | 1 | fits | 0.751545 | 0.751545 |
| vonfintelgillies2011 | 23/23 | 1 | 31,204 | 1 | fits | 0.846020 | 0.846020 |
| wright2007 | 22/22 | 1 | 25,987 | 1 | fits | 0.789935 | 0.789935 |
| schaffer2011 | 49/48 | 2 | 59,170 | 1 | fits | 1.735850 | 2.285450 |
| braun2012 | 52/52 | 2 | 45,408 | 2 | fits | 1.787040 | 2.362040 |
| eganhawthorneweatherson2005 | 48/48 | 2 | 48,903 | 1 | fits | 1.684515 | 2.234115 |
| egan2007 | 39/39 | 2 | 34,223 | 1 | fits | 1.341115 | 1.833565 |
| macfarlane2011 | 44/44 | 2 | 46,825 | 1 | fits | 1.554125 | 2.078325 |
| macfarlane2014 | 358/349 | 16 | 377,551 | 8 | fits | 12.357755 | 15.553105 |
| yalcin2007 | 44/44 | 2 | 56,914 | 1 | fits | 1.604570 | 2.128770 |
| yalcin2011 | 38/38 | 2 | 52,170 | 1 | fits | 1.400850 | 1.886950 |
| rothschild2012 | 13/13 | 1 | 17,337 | 1 | fits | 0.476685 | 0.476685 |
| moss2015 | 81/81 | 4 | 85,761 | 2 | fits | 2.858805 | 3.617955 |
| hawkesteinertthrelkeld2021 | 38/38 | 2 | 63,759 | 1 | fits | 1.458795 | 1.944895 |
| veltman1996 | 44/44 | 2 | 46,036 | 1 | fits | 1.550180 | 2.074380 |
| gsv1996 | 35/35 | 2 | 43,974 | 1 | fits | 1.269870 | 1.736920 |
| willer2013 | 40/40 | 2 | 51,914 | 1 | fits | 1.459570 | 1.958370 |
| yalcin2015 | 54/53 | 3 | 68,135 | 2 | fits | 1.930675 | 2.512025 |
| ninan2018 | 45/45 | 2 | 57,472 | 1 | fits | 1.637360 | 2.167910 |
| beddorgoldstein2021 | 47/47 | 2 | 49,346 | 1 | fits | 1.656730 | 2.199980 |
| hollidaymandelkern2024 | 70/70 | 4 | 111,982 | 2 | fits | 2.659910 | 3.349210 |
| kolodnymacfarlane2010 | 31/31 | 2 | 36,836 | 1 | fits | 1.114180 | 1.555830 |
| klinedinstrothschild2012 | 50/50 | 2 | 47,878 | 2 | fits | 1.739390 | 2.301690 |
| bledin2014 | 40/40 | 2 | 50,312 | 1 | fits | 1.451560 | 1.950360 |
| knobeyalcin2014 | 21/21 | 1 | 22,439 | 1 | fits | 0.742195 | 0.742195 |
| **Total** | **1379/1368** | **66** | **1,592,920** | **38 estimated** | **26 fit** | **49.004600** | **62.931600** |

Physical page ranges follow. Commas within one range identify gaps in readable page
numbers; semicolons separate model requests. Exact page arrays and per-range input
counts are in `runs/gamma-round4/plan26/extraction-plan.json`.

| Source ID | Planned physical page ranges |
|---|---|
| vonfintelgillies2007 | 1-16; 17-32 |
| eganweatherson2011 | 1-21 |
| vonfintelgillies2011 | 1-23 |
| wright2007 | 1-22 |
| schaffer2011 | 2-25; 26-49 |
| braun2012 | 1-26; 27-52 |
| eganhawthorneweatherson2005 | 1-24; 25-48 |
| egan2007 | 1-19; 20-39 |
| macfarlane2011 | 1-22; 23-44 |
| macfarlane2014 | 1,3-7,9-13,15-24; 25-39,41,43-48; 49-70; 71-92; 93-113; 114-135; 136-151,153,155-159; 160-181; 182-202; 203-224; 225-246; 247-268; 269-290; 291-312; 313-333,335; 336-349,351-358 |
| yalcin2007 | 1-22; 23-44 |
| yalcin2011 | 1-19; 20-38 |
| rothschild2012 | 1-13 |
| moss2015 | 1-20; 21-40; 41-60; 61-81 |
| hawkesteinertthrelkeld2021 | 1-19; 20-38 |
| veltman1996 | 1-22; 23-44 |
| gsv1996 | 1-17; 18-35 |
| willer2013 | 1-20; 21-40 |
| yalcin2015 | 1-26; 27-39; 40-53 |
| ninan2018 | 1-22; 23-45 |
| beddorgoldstein2021 | 1-23; 24-47 |
| hollidaymandelkern2024 | 1-17; 18-35; 36-52; 53-70 |
| kolodnymacfarlane2010 | 1-15; 16-31 |
| klinedinstrothschild2012 | 1-25; 26-50 |
| bledin2014 | 1-20; 21-40 |
| knobeyalcin2014 | 1-21 |

### Cost, coverage and remaining gates

The primary **USD62.931600** extraction scenario includes 24 estimated graph-review
windows, with no unresolved-obligation work. Initial calls alone reserve 2,112,000
output tokens at 32k/range: **USD60.764600**, compared with their expected-output
scenario USD49.004600. Reserving full output also for the estimated review windows
would give **USD88.976400**. These are scenarios, not upper bounds: real obligations,
context retrieval, corrections and retries can add calls. Even the initial scenario
exceeds the historical USD30 profile. Including the review scenario gives
5,233,488 input-plus-output tokens; its full-output reservation scenario gives
6,275,280, also above the historical 6M token cap. Review tokens are estimates,
not provider counts. The operator must set the null caps; none
were raised here. Numeric derivation: `runs/gamma-round4/plan26-cost-scenarios.json`.

Seven sources have **82 affected physical pages**: `schaffer2011` 1 (unread),
`braun2012` 5, `macfarlane2014` 15, `yalcin2007` 42, `yalcin2015` 3,
`ninan2018` 8 and `kolodnymacfarlane2010` 8. The other 81 affected pages have retained
encoding warnings. Ten blank pages plus the one unread page explain the 11-page
difference between physical and readable totals. Strict missing/coverage policy
still refuses partial sources; planning fit does not override it. pypdf warnings
are retained under `runs/gamma-round4/plan26-stderr.txt`; this is not OCR or proof of
correct text order/glyph interpretation. No source argument content is reproduced.

**D3-N1 remains a disclosed limit:** targeted patches cannot delete rejected entries,
repair truncated/malformed inventories, or guarantee successful recovery. Live
construction patch success and the new window protocol's live wire acceptance and semantic
quality remain unproved this unpaid round. **D3-N2 remains separate:** no native
frozen-T resume path or downstream live pilot was added/executed. Passing a frozen
commitments file as literature is still not an authorized continuation path.

The accepted round-3c 45-item freeze is untouched; SHA256 remains
`25a7ec8c35d393b230738e6008467d70926697db6bed1f91c72b5edcd39cb3a4`.
No earlier failed receipts or unknown reservations were released. Campaign totals
remain **USD5.461870 measured + USD3.934240 held unknown = USD9.396110 accounted**;
build campaign remains **USD5.433360 of USD6**. This round adds USD0.000000 paid
usage. No full corpus extraction, construction or pilot success is claimed.

### Findings placement

| Finding | Deliverable placement |
|---|---|
| D3-S1: full-run stage/policy and unset caps | Policy and capacity changes; Cost, coverage and remaining gates |
| D3-S2: legitimate empty ranges/windows | Policy and capacity changes; Executed proof and review limits |
| D3-S3: global working/catalogue capacity and prediction limits | Policy and capacity changes; 26-paper unpaid plan |
| D3-B2: single-source windows/full closure/prior context/oversized closure | Policy and capacity changes; Executed proof and review limits |
| D3-B1: bounded review/obligations/context requests and safe refusals | Policy and capacity changes; Executed proof and review limits |
| D3-N1: patch deletion/truncation/live semantic limits | Cost, coverage and remaining gates |
| D3-N2: frozen-T continuation/pilot gate | Cost, coverage and remaining gates |
| Corpus scope, missing 27 files, unread/glyph-warning coverage | 26-paper unpaid plan; Cost, coverage and remaining gates |
| Cost scenarios, omitted work, no cap authority, retained campaign reservations | 26-paper unpaid plan; Cost, coverage and remaining gates |
| Free endpoint verification and zero generation/spend | 26-paper unpaid plan; Cost, coverage and remaining gates |
| Executed verification, repaired regressions and independent-review gap | Executed proof and review limits |

**11 findings, 11 placed.**

DONE gamma round4 head=be8c2c2ee2adaf491a8a31bb38640d40e287cebc tests=373/375 negctl=pass fixed=D3-S1,D3-S2,D3-S3,D3-B2,D3-B1 plan26=fits est26_opus_usd=62.931600 status=awaiting-review

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

## Round 6

**D5-B1 repaired; awaiting independent review.** Base: `4b94f8e4a1053661d6dc36e3ec6d8bbc2b8d6405`. Final revision: `ba3a004d422467a0aed8a77be9407587d265a514` on `feat/paper-extraction`. Scope is only the round-6 brief and Delta's D5-B1 continuation-bound finding. Solo execution, no push, no network requests or paid generation.

### D5-B1: paper-wide admission and retained queue

A `PaperAllowance` wraps the native `extract_paper` lifecycle and is enforced by the shared model-call boundary. It applies to every extraction attempt, so graph reviews, ordinary evidence windows, explicit requested contexts, descendant obligations, validation retries and targeted corrections cannot acquire fresh allowances. The count is deliberately conservative: every request after the first counts as a continuation, including additional initial ranges and subdivision recovery. Cached response attempts consume count allowance but reserve USD0; free token-planning calls are not model attempts. SDK generation retries remain disabled, and extraction-full still disables model fallbacks.

Before each dispatch, the existing enclosing/stage reservation checks and the paper count/USD checks must all pass. The monetary allowance includes the initial response, all later responses, rejected attempts, and held unknown-usage reservations. It uses the requested stage model for reservation and the existing measured/served-model accounting for actual charges. Actual paper cost is checked again after a durable response/usage receipt. Both count and USD limits are validated as finite and nonnegative before paper work, including unused large-paper override values; counts must be integers.

Each attempt has a paper-specific receipt, and MODEL events carry the trusted paper source ID from the runtime scope. Re-entering the same paper recovers its prior attempt count and charges from the log, so restarting that method does not reset its allowance. A different source receives a separate allowance while total costs remain charged to the shared extraction/run caps. The first paper's costs therefore cannot consume the second paper's local allowance, and moving between obligations cannot reset any allowance.

A local refusal emits `BudgetStop` before the next dispatch. Its STOP event and partial JSON name the source and every pending accepted obligation ID, as well as attempts, used continuations, paper cost, and both limits. Pending IDs are reconstructed in event order from append-only discoveries and resolutions. Global budget stops within extraction receive the same paper context. Existing range/window snapshots, full model responses, charged/held usage and accumulated discoveries/resolutions survive. No gap is merged by text, discarded, or declared complete at a limit; no literature artifact is published on refusal.

A response received immediately before an actual-cost STOP remains in raw/usage receipts; the budget refusal prevents incorporating it into a paper artifact. Pending IDs reflect the accepted obligation history rather than invented entries from a response whose paper processing did not complete. Actual-cost checking detects an underestimate after the charge has occurred; it cannot undo provider charges or establish the actual value of an unknown reservation. There is still no automatic collection resume or live semantic-coverage guarantee.

### Defaults and free-plan arithmetic

The defaults are explicit in `extraction-full` and justified in `DECISIONS.md` GX29. Ordinary configurations without explicit paper settings also receive finite 24/USD15 defaults. The larger allowance is an explicit full-profile override based on physical-page count, with no source-name special case.

Any external proposed run configuration copied before this commit must copy these new profile keys, including `extraction_large_paper_limits`, before using the intended larger allowance. In particular, `/home/dev/ara-work/reports/delta-rereview4-config.proposed.yaml` was checked read-only and lacks all three new paper-limit keys; it was not edited here. An old configuration without the keys receives the finite 24/USD15 fallback for every source, so the large source can refuse even within its saved baseline cost scenario. This is a configuration-composition prerequisite, not permission to increase enclosing caps.

| Paper group | Continuation ceiling | Per-paper USD ceiling | Saved-plan basis |
|---|---:|---:|---|
| Under 300 physical pages | 24 | 15 | At most 4 initial ranges + 1 estimated review window = 4 continuations; largest full-output scenario USD5.048850 |
| At least 300 physical pages | 48 | 30 | The 358-page source: 16 initial ranges + 4 estimated review windows = 19 continuations; expected-output-with-review USD15.570865; full-output scenario USD20.281665 |

The ordinary ceiling leaves twenty continuation attempts beyond that planned maximum. The large ceiling leaves twenty-nine beyond its baseline scenario; USD30 leaves USD9.718335 beyond its full-output scenario. At USD5/M input and USD25/M output, a near-context request with 168k input plus 32k output reserves USD1.64, so the dollar ceiling may bind before the count ceiling. The count ceilings do not promise that every allowed request can be funded. These are finite experiment limits, not a forecast or authorization to spend; all enclosing extraction-full caps remain null.

The round-5 free plan is unchanged: neither the extraction prompt/schema nor range planner changed. No new token-counter call was needed. Sizing receipt: `runs/gamma-round6/sizing.json`, pinning plan SHA256 `f8e8cd4211326fcf1f4f2723d5400583b47dabefbbaa842224fe53e0cb7a06be`. It covers 26 PDFs, 1,379 physical / 1,368 readable pages, 66 initial ranges and 1,607,572 counted initial input tokens. Initial expected-output cost remains USD49.077860; adding the estimated no-obligation review gives USD63.004860; the corresponding full-output scenario remains USD89.049660. The 24 review windows and their graph/output densities remain estimates, not generated evidence. Obligation traversal, descendants, contexts, retries/corrections, construction and pilot work remain outside these scenarios.

### Executed verification and its limits

The three requested regressions failed before implementation: the descendant chain and paper-dollar cases did not stop, and the multi-paper case had no paper attempt accounting. Receipt: `runs/gamma-round6/regressions-before.txt`. They then passed through native `extract` with retained receipts (`regressions-after.txt`, `core-proof/`). The count test stops after one initial plus three continuations while shared and paper money remains; the dollar test accepts two measured responses and refuses the next full reservation; the multi-paper positive case accepts three responses independently for each of two sources while preserving the shared total.

The expanded tests cover count and dollar consumption by retries/corrections, all continuation kinds, multiple pending IDs in STOP, same-paper re-entry count and cost persistence, independent source allowances, retained unknown-usage reservation, actual-usage overrun, invalid/nonfinite limits, and the 299/300/358-page profile threshold. The affected run passed **93 tests** in 32.29 seconds. A preliminary command named a nonexistent `test_budget.py` and collected no tests; its error receipt is retained as `targeted-first.txt`, not counted as verification. Subsequent correct commands/results are retained separately.

Full `uv run pytest --basetemp=runs/gamma-round6/pytest-proof`: **414 passed, 2 skipped / 416 collected**, exit 0, **263.27 seconds**. Receipt: `runs/gamma-round6/pytest-final.txt`. After pytest exited, `uv run python tests/integration/negative_controls.py`: **162/162 red, 162/162 restored green**, exit 0. Full runner receipt: `runs/gamma-round6/negative-controls-final.txt`; individual traces and results: `runs/gamma-round6/controls/`. All seven committed file hashes exactly match the pre-gate tested-tree snapshot in `runs/gamma-round6/verified-tree-inputs.json`; the working tree is clean and `git diff --check` passes. Final verification: `/home/dev/ara-work/reports/gamma-round6-verification.json` (also retained under `runs/gamma-round6/verification.json`).

Six new production mutations and their observed red behavior:

| Control | Mutation | Observed failure |
|---|---|---|
| paper_continuation_cap | Removes per-paper count admission | Expected BudgetStop does not occur |
| paper_reservation_cap | Removes paper USD reservation admission | Expected BudgetStop does not occur |
| paper_actual_cap | Removes measured paper-cost stop | Expected BudgetStop does not occur |
| paper_count_finite | Removes integer/finite count validation | The explicit paper configuration error disappears; invalid infinity reaches JSON serialization instead |
| paper_dollars_finite | Removes finite/nonnegative USD validation | The explicit paper configuration error disappears; invalid infinity reaches JSON serialization instead |
| paper_boundary_cost | Counts the prior paper's spend against the next paper | Multi-paper positive case incorrectly stops before the second source's first dispatch |

The finite-value mutation controls prove the explicit validation/error contract; they do not claim those mutations dispatched a paid request, since JSON serialization also rejects infinity. The other controls distinguish missing local admission/actual stops and improper cross-paper accounting. Every restored counterpart passed. No pytest suite was run concurrently with mutation controls. All offline providers are network-forbidden and their dollar receipts are synthetic.

Inline simplification/manual diff review reused the existing accounting, log and STOP paths; the separate allowance owns paper scope rather than duplicating provider pricing or changing reconciliation queue logic. No further simplification was justified, and proof tests were retained. There is no configured lint/typecheck command. **Code review: skipped (ce-code-review unavailable).** The skill requires an independent reader for this money-boundary change, which the solo restriction prevents. No independent review or live extraction/model fidelity is claimed; Delta review remains the next gate.

### Retained operating limits and accounting

D4-N1/D4-N2 remain applicable: explicit pilot-profile composition, imported extraction charges consuming the enclosing pilot cap, and partial-source handling. The inventory is still 26 available PDFs out of 53 records. Its 82 affected pages across seven sources include one unread page and 81 retained encoding warnings; ten blank pages explain the remaining physical/readable difference. The intended full run still requires the disclosed `missing record-only` policy. Counted fit does not establish correct glyph interpretation, text order, complete argument coverage or successful live continuation.

The new per-paper limits may stop one expensive source while aggregate corpus budget remains. That is an explicit refusal with receipts, not automatic skipping, semantic deduplication, budget escalation or a guarantee of corpus completion. Enclosing budgets and the prior full-run approval prerequisites remain unchanged. No paid generation, construction, freeze, search or writing was executed this round; no credentials were loaded or exposed.

This round adds USD0 paid usage and no network count calls. Prior accounting remains **USD5.461870 measured + USD3.934240 held unknown = USD9.396110 accounted**, with build campaign **USD5.433360 of USD6**. No earlier failed receipt or unknown reservation was released. The accepted 45-item freeze retains SHA256 `25a7ec8c35d393b230738e6008467d70926697db6bed1f91c72b5edcd39cb3a4`.

### Findings placement

| Finding | Deliverable placement |
|---|---|
| D5-B1 missing per-paper admission limits | D5-B1: paper-wide admission and retained queue |
| Count semantics, finite defaults, large-paper arithmetic and old external config migration | Defaults and free-plan arithmetic |
| STOP inventory, re-entry/cost persistence, actual and unknown usage limits | D5-B1: paper-wide admission and retained queue; Executed verification and its limits |
| Test/control evidence, failed command disposition and independent/live review limits | Executed verification and its limits |
| Reused free-plan counts, cost exclusions and retained D4-N1/D4-N2 prerequisites | Defaults and free-plan arithmetic; Retained operating limits and accounting |
| No spending/network calls, preserved campaign reservations and freeze | Retained operating limits and accounting |

**6 findings, 6 placed.**

DONE gamma round6 head=ba3a004d422467a0aed8a77be9407587d265a514 tests=414/416 negctl=pass fixed=D5-B1 status=awaiting-review
