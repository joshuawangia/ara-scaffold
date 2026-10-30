# pi3 publication quality pass

The publication stage now renders author–year/page citations, retains raw IDs and provenance in a receipt, imports both verified eps2 currency records, and sends Opus stronger editorial instructions. The route-1 quality test **failed the post-polish native audit after its one permitted repair**. The delivered PDF therefore retains the original draft with improved citation formatting. The revised prose and related-work section are review evidence, not an accepted publication (F1).

- [Delivered fallback PDF](/home/dev/ara-work/reports/papers/pi3-quality.pdf)
- [Delivered fallback Markdown](/home/dev/ara-work/reports/papers/pi3-quality.md)
- [Citation receipt](/home/dev/ara-work/reports/papers/pi3-quality-citations.json)
- [Rejected polish, visibly marked review-only PDF](/home/dev/ara-work/reports/papers/pi3-quality-rejected-review.pdf)
- [Rejected polish Markdown](/home/dev/ara-work/reports/papers/pi3-quality-rejected-review.md)
- [Rejected polish citation receipt](/home/dev/ara-work/reports/papers/pi3-quality-rejected-citations.json)
- [Publication result](/home/dev/ara-work/pi3/runs/pi3-quality-live/publication/91bd6f7166b586a1/publication.json)
- [Methodology](/home/dev/ara-work/pi3/runs/pi3-quality-live/export/methodology.md)

## Test outcome and editorial limits

Five fresh section edits and one whole-paper pass used the existing isolated `claude_code` provider pinned to `claude-opus-5-5`. Section edits reduced fragmentation. The whole-paper native audit flagged 11 sentences. Opus then made the single targeted repair, preserving all unflagged paragraphs byte-for-byte and retaining the 29-paragraph inventory, distinct citations, route nodes and figure placements.

That real logged repair was initially rejected before audit because the implementation counted a 4,500-word minimum on internal raw citation IDs as well as author–year reading text. The repair was 4,464 annotated words but **4,658 reading words**, within the original bound. The corrected validator enforces 4,500–6,000 on the actual reading text, excluding references and internal markers; it still reports the annotated count. A logged one-time recovery revalidated the existing response's schema, inventories, paragraph mapping and reading length. No new prose was generated and the initial adverse audit was not reset (F8).

The fresh post-repair audit covered all three route nodes but flagged **nine sentences: 9, 32, 97, 117, 135, 170, 171, 233 and 248**. Four restate literature positioning outside the allowed related-work section; five elaborate on consistency, order and explanation beyond the allowed support. The related-work section itself received no extra-step flags. These are native model verdicts, not an independent philosophical review. [Exact flagged text and verdict](/home/dev/ara-work/pi3/runs/pi3-quality-proof/repair-audit-findings.json), [audit input](/home/dev/ara-work/pi3/runs/pi3-quality-proof/repair-audit-input.json), [audit response](/home/dev/ara-work/pi3/runs/pi3-quality-proof/repair-audit-response.json).

No second repair or favorable-verdict retry followed. The original draft remains the fallback; it was not freshly audited for acceptance in this followup. It consequently lacks the new abstract, revised section structure and related-work section; its deterministic figures follow the original text. Its reading copy has **4,959 words**, excluding references and figure/internal markers. The rejected review artifact includes a visible rejection notice; its underlying article remains the exact 4,658-word repaired text, apart from deterministic citation display and marker removal.

Editorial inspection also finds repeated thesis restatements and qualifications in the repaired argument, limits and conclusion. Paragraph count fell from the prior polished paper's 57 to 29, but that does not establish strong journal prose. The 4,500-word minimum remains in force; no response authorized shortening below it. **The quality test did not meet the desired prose standard**, independently of the audit failure (F2).

## Citation display and literature scope

Reading Markdown, PDF and figures now use author–year/page labels. Raw `[cite:...]` and `[lit:...]` IDs remain in the annotated publication result and citation receipts. Adjacent references to the same work/page collapse visually while both evidence IDs remain traceable; citations move before sentence-ending punctuation.

Both frozen route citations point to **physical PDF page 18**, so the display is `(Groenendijk, Stokhof & Veltman 1996, PDF p. 18)`. The user's page-20 example was illustrative; no printed-page offset was invented (F4).

Both supplied files were logged verbatim as HUMAN inputs with hashes: `/home/dev/ara-work/reports/eps2-bridge-literature.json` and `/home/dev/ara-work/reports/eps2-L3.json`. The importer retains read evidence, page/section locators, search scope, route-specific assessments, access limits and verification receipts. Metadata-only records cannot become substantive source support. These inputs never enlarge frozen T or the route.

Route 1's assessment is partial anticipation. The focused L3 absence concerns a different relation and cannot be transferred to this thesis. The rejected related-work section accordingly uses the partial-anticipation assessment and does not claim that this thesis was absent from the search. Future absence claims are limited to “not found within the stated 2018–2026 search” for the precise recorded question. Importing the records is not a new literature search or a novelty certificate (F3).

The publication audit receives the original draft plus the exact normalized currency evidence, and checks every sentence against the appropriate source. New literature claims are restricted to the related-work section. Ordinary writer/audit calls and pilot provider routing remain unchanged. The polisher may consolidate redundant paragraphs while preserving distinct support and node inventories; a paragraph change log alone is not proof of claim preservation.

## Artifact proof

Native `ara figures` and `ara render-pdf` both exit 0 for the delivered fallback. It has **12 pages and two figures**, embedded Liberation Serif and DejaVu Serif fonts, and no detected HTML or PDF glyph overflow. Raw citation/node markers are absent. Final PDF SHA-256: `dd0caa28ed38cc9b4f2cb8fd3a9555ae840f9f59d755b1c7c2d648dec8100b40`.

The rejected review copy has **11 pages and two figures**, a visible rejection notice, six citation receipt entries and the same successful font/overflow checks. It uses the same deterministic renderer and never becomes the accepted publication pointer. Its PDF SHA-256 is `8e0a633d0d08fcb1f8dc95c4c41fb7fe3c380e59a3a43d0654a521802c67bbd9`.

Visual inspection covered title pages, figure pages and references. The final reading conversion removes node markers before punctuation/deduplication and excludes unused currency references from the fallback bibliography. Free-form operational version notes remain in provenance receipts; supported version/access qualifications remain in the related-work prose. The source article text and audit verdict were unchanged by these display corrections.

[Artifact checks and copied hashes](/home/dev/ara-work/pi3/runs/pi3-quality-proof/artifacts-complete.json), [fallback page images](/home/dev/ara-work/pi3/runs/pi3-quality-proof/fallback-final-pages/page-inventory.json), [rejected page images](/home/dev/ara-work/pi3/runs/pi3-quality-proof/rejected-clean-pages/page-inventory.json). Copied files are byte-identical to their checked artifacts. The original 8,590-event log/anchor prefix and all 35 other retained files match the copy manifest; the original draft and frozen evidence are unchanged. SVG regeneration is byte-identical. [Integrity receipt](/home/dev/ara-work/pi3/runs/pi3-quality-proof/artifact-integrity.json).

Original report and paper artifacts remain available as historical evidence. The prior 583-control receipts were copied to `runs/pi3-proof/delta-controls/`; the prior report's results link now points to that preserved archive.

## Verification

- Initial quality regressions: 7 failed, 9 passed; focused implementation checks subsequently passed.
- Citation punctuation/deduplication regression observed red before correction.
- Marker-interrupted citation punctuation and unused currency bibliography regressions both observed red, then fixed.
- Reading-word boundary regression: 1 failed, 2 passed before correction; **38 publication/audit checks passed** afterward.
- Earlier completed full suite: 1,314 passed, four skips, before the reading-count correction. This is historical, not the final source verdict.
- Final full pytest: **1,317 passed, four skipped (1,321 collected)** in 1282.51 seconds, exit 0, on `runs/pi3-quality-proof/tested-source.json`. The four skips are existing opt-in provider/OCR tests.
- Sequential `UV_OFFLINE=1 uv run --locked python tests/integration/negative_controls.py`: **587/587 controls passed**, every mutation red with exit 1 and every restored check green with exit 0. The runner finished after full pytest, with no concurrent source writer.

[Focused checks](/home/dev/ara-work/pi3/runs/pi3-quality-proof/focused-final.txt), [final pytest log](/home/dev/ara-work/pi3/runs/pi3-quality-proof/pytest-full.txt). All 215 pinned source files were restored exactly, and their committed blobs match the tested snapshot. `git diff --check` passed and the working tree is clean. [Final verification](/home/dev/ara-work/pi3/runs/pi3-quality-proof/final-verification.json), [control log](/home/dev/ara-work/pi3/runs/pi3-quality-proof/negative-controls.txt), [archived control results](/home/dev/ara-work/pi3/runs/pi3-quality-proof/delta-controls/results.json). No project lint/typecheck command exists. Non-author review is caller-owned.

## Accounting, evidence and revision limits

The local followup records 20 model receipts: 15 actual dispatches, 12 new measured responses, five cache replays and three unknown-usage timeouts. All receipted responses report `claude-opus-5-5` through Claude Code 2.1.306; all three isolation canaries passed. The inherited writer requested Codex `gpt-6-luna`, whose serving identity remains unverified in that history. [Receipt counts](/home/dev/ara-work/pi3/runs/pi3-quality-proof/receipt-counts.json).

Three fresh whole-paper attempts exhausted 300-second timeouts. Publication now defaults to 900 seconds unless explicitly configured otherwise; pilot defaults and transport retry bounds are unchanged. The longer call produced the whole draft. Timed-out usage is unknown and counted at reservation, distinct from measured response usage and imported historical accounting. List-price equivalents are not measured API charges (F7).

The isolated provider cannot perform external citation/originality retrieval. This failed-polish fallback records that step as `not_run`; the earlier accepted publication independently recorded `stage_requires_api_provider`. Imported eps2 records do not make external verification pass (F5).

The route remains supported by two frozen items from one paper. The literature record supports positioning only. Native audit is a model assessment, not proof of semantic equivalence, novelty or philosophical quality; polishing cannot repair the underlying route's evidential limits (F6).

Workspace `/home/dev/ara-work/pi3`, branch `feat/publication`, parent `0aa6a29cef26bcbac30e7eb3b1e53cc93414b2b6`, retaining the requested fetched nu4 base `c7ae7f5`. Input remains the accepted nu4 round-two draft, copied into this isolated run. No rebase instruction arrived; later upstream work is not silently adopted (F9). Local commit: **97139e79da1451f5e58731a1b3fd97e8e91d4cf5**. Seventeen owned source, prompt, schema, test and documentation files are committed; the working tree is clean. No push or delegation. Actual source material, prose and artifacts remain ignored and uncommitted.

Finding placement: F1/F2/F8 → “Test outcome and editorial limits”; F3/F4 → “Citation display and literature scope”; F5/F6/F7/F9 → “Accounting, evidence and revision limits”. **9 findings, 9 placed.**

Implementation and prescribed verification are complete. The prose-quality goal remains unmet; no accepted revised paper is claimed. Next is caller-owned non-author review. The structured handoff is [here](/home/dev/ara-work/pi3/runs/pi3-quality-proof/return-to-caller.json).

DONE pi3 quality pdf=/home/dev/ara-work/reports/papers/pi3-quality.pdf words=4959 audit_after_polish=fail
