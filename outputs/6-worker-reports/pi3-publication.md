> Latest follow-up: [pi3 quality3](/home/dev/ara-work/reports/pi3-quality3.md) supersedes the earlier route-1 quality verdict and publication minimum. The configurable floor is now 3,000 words; the 3,471-word paper passes the typed post-polish audit after one repair. Full pytest and all 627 sequential controls pass; the follow-up report records verification limits.

# pi3 — publication

Implemented `ara polish`, `ara figures` and `ara render-pdf`, committed locally at **0aa6a29cef26bcbac30e7eb3b1e53cc93414b2b6**. The final paper is **4,743 words**, with **two deterministic figures** in a **12-page PDF**. Its native audit passes: all three route nodes are covered, with zero missing nodes or extra-step flags. Exact T citation checks pass. **External citation/originality verification remains blocked** by the isolated subscription provider; this is not a submission-ready verification verdict (F1).

- [Final PDF](/home/dev/ara-work/reports/papers/pi3-publication.pdf)
- [Final Markdown](/home/dev/ara-work/reports/papers/pi3-publication.md)
- [Publication result](/home/dev/ara-work/pi3/runs/pi3-live/publication/522c43ae6bc6de33/publication.json)
- [PDF checks](/home/dev/ara-work/pi3/runs/pi3-live/publication/522c43ae6bc6de33/pdf-checks.json)
- [Methodology](/home/dev/ara-work/pi3/runs/pi3-live/export/methodology.md)

## Behavior and native integration

Publication extends the native CLI and ModelCalls boundary after an existing draft. Each invocation makes one logical section call per section and one whole-paper call, pinned to isolated `claude_code` / `claude-opus-5-5`. The existing canary, forbidden-context checks, identity/credential scans, schema validation, cache, token budget and append-only receipts remain in force. Pilot routing stays unchanged; the publication-only schema is excluded from Codex pilot preflight.

Structured responses provide Markdown, validated figure placements and a paragraph change log. The whole paper requires 4,500–6,000 words, a 150–200-word abstract, numbered sections and preserved paragraph citation/node-marker sequences. Native audit assesses source support and route fidelity. One targeted repair is permitted after a complete adverse audit; remaining failure retains the original draft and records fallback. Offline tests prove both repair outcomes; the accepted live paper needed no semantic repair.

References preserve exact T locators and join full bibliographic records from logged extraction inputs through matching source IDs and PDF hashes. Conflicting metadata refuses. No mutable checkout bibliography supplies missing facts. These recorded bibliographic details remain independently unverified (F2, resolved formatting issue; verification limit is F1).

Figures use deterministic Python SVG layout: route nodes, inference schemes, premise edges, CQ status and source papers; then source/page support, attribution and stance. A gap panel uses an actual open route frontier. Source extraction defects are not argument gaps; the delivered closed route therefore has two figures (F6). Required figures cannot be silently omitted (F9).

Publication artifacts have content digests and route bindings. A later incomplete attempt blocks reuse of an older publication (F7). The reading Markdown removes internal node markers; annotated Markdown and the native audit draft remain in the result JSON (F8). No publication stage emits `final_draft` merely because formatting succeeded. Native essay export remains distinct.

HTML escapes embedded Markdown HTML, restricts SVG elements and blocks browser network requests. Chromium prints serif typography, numbered headings, captions, page numbers and margins. Checks cover page count, embedded fonts, figure inventory/captions, HTML horizontal overflow and PDF glyph bounds.

## Live result and artifact proof

Input: nu4's newest saved round-two draft, `/home/dev/ara-work/nu4/runs/nu4-proof/round2/essay.unverified.json`, on route `9a35a6febc9d:r0`. Canonical source-draft SHA-256: `36983be30b9b8c4c6ddde08b61f26104b2d062606bbc8325913687ba8458dd65`.

The source run was copied and hash-verified before work. Final integrity checks retain its original log/anchor prefixes, all frozen artifacts and the original draft. The upstream source run advanced during this task: its draft, event log/anchor and methodology now differ from the copy manifest. This work used its isolated copy; the selected round-two draft still matches the publication input digest. The integrity receipt therefore proves our retained input and prefix, not that the concurrently active upstream run stayed unchanged (F10). Real SVG bytes reproduce across the earlier and final artifact directories. See [integrity receipt](/home/dev/ara-work/pi3/runs/pi3-proof/integrity.json).

The delivered paper has 57 paragraph change entries, a title/abstract, numbered introduction/argument/objection/reply/limits/conclusion sections, exact citations and full recorded references. The native audit reports `faithful: true`, coverage `n0/n1/n2`, and no extra steps. Native citation retrieval refuses before API dispatch with `stage_requires_api_provider`; local membership in exact T provenance is separately reported as passed. No API adapter or paid retrieval fallback was invoked (F1).

An exploratory fresh pass passed audit but selected a source-extraction-gap figure; it is retained and not delivered. The corrected fresh pass supplied the accepted prose. Subsequent ordinary CLI cache replays exercised final validation and publication, including clean Markdown and the logged bibliography, without regenerating that prose. The final native `polish` command exits 2 for blocked external verification; native `figures` and `render-pdf` exit 0 for their artifact checks. Detailed receipts: [live result](/home/dev/ara-work/pi3/runs/pi3-proof/live-result.json), [final CLI](/home/dev/ara-work/pi3/runs/pi3-proof/live-polish-final-code.txt), [figures](/home/dev/ara-work/pi3/runs/pi3-proof/live-figures-final.txt), [render](/home/dev/ara-work/pi3/runs/pi3-proof/live-render-pdf-final.txt).

Final PDF: 12 pages, two embedded figures, embedded Liberation Serif and DejaVu Serif fonts, no detected HTML or glyph overflow. Visual inspection covered the title/abstract, both figure pages and conclusion/references. [Page images and inventory](/home/dev/ara-work/pi3/runs/pi3-proof/final-pages/page-inventory.json). Final PDF SHA-256: `5786390d5427756e98424d89f40b2bfa6e6b007763b7ed748a2e56dd57356856`. The copied Markdown and PDF are byte-identical to the checked run artifacts.

## Executed verification

- `uv sync --locked`: passed with Python 3.13.7 and the committed lockfile.
- Final focused publication/schema checks: **37 passed**. They exercise the real ModelCalls boundary with fakes and the real local Chromium renderer. Initial missing-module failures and later observed gap, stale-artifact, required-figure, marker-display and logged-metadata regressions are retained under `runs/pi3-proof/` and `/home/dev/ara-work/reports/pi3-red.txt`.
- Final `uv run --locked pytest -q --basetemp /dev/shm/ara-pi3-with-references`: **1305 passed, 4 skipped, 1309 collected**, exit 0. The skips are the four existing opt-in provider/OCR tests. [Full log](/home/dev/ara-work/pi3/runs/pi3-proof/pytest-full.txt).
- Sequential `UV_OFFLINE=1 uv run --locked python tests/integration/negative_controls.py`: **583/583 controls**, every mutation red with exit 1, every restored check green with exit 0. Twelve controls cover publication behavior. No concurrent checkout writer ran during controls. [Control log](/home/dev/ara-work/pi3/runs/pi3-proof/negative-controls.txt), [results](/home/dev/ara-work/pi3/runs/pi3-proof/delta-controls/results.json).
- Final source restoration, committed-blob comparison and `git diff --check`: passed. [Final verification receipt](/home/dev/ara-work/pi3/runs/pi3-proof/final-verification.json).

An earlier completed full run (1,304 passed, four skips) predates the bibliography module; interrupted discovery runs are retained separately. Only the final run above is the delivery verdict. No project lint/typecheck command is configured. Non-author review remains caller-owned.

## Accounting and limits

The final receipt inventory records 37 model receipts, 19 actual dispatches, 18 responses with measured receipts, and 14 cache replays. All receipted publication responses report `claude-opus-5-5`, through Claude Code 2.1.306. Writer model/provider versions remain in the inherited methodology; nu4 requested Codex `gpt-6-luna`, whose served identity remains unverified in that history.

One whole-paper attempt timed out at 300 seconds; the bounded retry succeeded. Its usage is unknown and counted at the reservation. Aggregate recorded tokens therefore mix measured usage with that reservation, and are not wholly measured (F5). No server tools or API adapter were used for publication. Subscription list-price equivalents are not measured API charges; the timed-out attempt has no measured equivalent. Full accounting is in the event-derived methodology and [live receipt](/home/dev/ara-work/pi3/runs/pi3-proof/live-result.json).

This is one route supported by one paper. Polishing does not establish novelty, independent cross-paper support or competition acceptance, and it does not repair the underlying source/support limitations documented by nu4. Native audit is a model assessment, not proof of semantic equivalence or philosophical quality. External citation/originality verification and non-author review remain necessary before a stronger research-quality claim (F3).

## Revision and handoff

Workspace: `/home/dev/ara-work/pi3`; branch: `feat/publication`; final commit: `0aa6a29cef26bcbac30e7eb3b1e53cc93414b2b6`. The requested `wip/nu4-writer` ref was absent, so the explicitly named `c7ae7f53dae52afb607b2b5ae4f06fb6c7d50a5d` was fetched from nu4 and used as the base. Nu4 advanced beyond this base during the work; its later round-three report records an adverse audit, so the previously accepted round-two draft remains the publication input. No instruction to rebase arrived; this branch retains the requested fetched base (F4).

Eighteen owned files are committed: publication/figure/PDF/reference modules, CLI registration, Codex preflight exclusion, methodology summary, prompt/schema, locked dependencies, tests/controls and documentation. Generated prose, PDFs, SVGs, source material and logs remain ignored and uncommitted. The working tree is clean. No push or delegation. [Structured implementation handoff](/home/dev/ara-work/pi3/runs/pi3-proof/return-to-caller.json). Standalone shipping skipped as requested. Next: caller-owned non-author review and any directed rebase; external retrieval requires separately authorized implementation/provider work.

Finding placement: F1 → “Live result and artifact proof”; F2 and F6–F9 → “Behavior and native integration”; F3/F5 → “Accounting and limits”; F4 → “Revision and handoff”; F10 → “Live result and artifact proof”. **10 findings, 10 placed.**

DONE pi3 head=0aa6a29cef26bcbac30e7eb3b1e53cc93414b2b6 tests=1305/1309 negctl=pass polished_words=4743 audit_after_polish=pass figures=2 pdf=/home/dev/ara-work/reports/papers/pi3-publication.pdf

## Latest quality3 completion

Local head `61d5a8c7a240a591eada1bf6a23165e20991da7c`; 1,400 tests passed, four skipped; 627/627 sequential controls passed. [Full quality3 report](/home/dev/ara-work/reports/pi3-quality3.md). External citation/originality retrieval remains blocked through the isolated provider. Six findings are placed in that report.

DONE pi3 quality3 pdf=/home/dev/ara-work/reports/papers/pi3-quality3.pdf words=3471 audit_after_polish=pass repair_rounds=1

## Quality 4 result

See the [Quality 4 appendix](/home/dev/ara-work/reports/pi3-quality3.md#quality-4--enforcement-verified-live-polish-failed-and-original-retained). NP-F1/F2/F3 are implemented at `a6a2f9b8de76fe4792da0dcc790d7b2ffff71a1d`, including nu4 `0368a17`; full pytest 1425 passed / 1429 collected and 640/640 mutation controls passed. The native Opus-edit/Codex-audit attempt failed and retained the original: 5065 reading words, two repairs attempted/one accepted, 12-page fallback PDF. External verification was not run; successful editorial polish and non-author re-review remain outstanding.
