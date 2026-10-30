# pi3 quality2 — implementation complete; live quality failed

The three-round repair path and nu4 typed-audit integration are implemented. Full pytest passed **1,388 tests with four skips**. The live route-1 quality test **failed before semantic audit**: the new edit had **3,727 reading words**, below the required 4,500 minimum. It therefore used **0 repair rounds** and retained the original **4,959-word** draft. No accepted improved paper is claimed (F1). All **621 sequential mutation controls passed**. The change is committed locally at **a0dc5e3ddfe30ef43a4447ae4a1357459b6110eb**; the working tree is clean.

- [Delivered fallback PDF](/home/dev/ara-work/reports/papers/pi3-quality2.pdf)
- [Fallback Markdown](/home/dev/ara-work/reports/papers/pi3-quality2.md)
- [Citation receipt](/home/dev/ara-work/reports/papers/pi3-quality2-citations.json)
- [Rejected edit, visibly marked review-only PDF](/home/dev/ara-work/reports/papers/pi3-quality2-rejected-review.pdf)
- [Rejected edit Markdown](/home/dev/ara-work/reports/papers/pi3-quality2-rejected-review.md)
- [Publication result](/home/dev/ara-work/pi3/runs/pi3-quality2-live/publication/d7ea79985264f07b/publication.json)
- [Methodology](/home/dev/ara-work/pi3/runs/pi3-quality2-live/export/methodology.md)

## Integration and repair behavior

The branch is rebased onto nu4's `fix/writer-length` head **d15eb43ef56a01079d9ad453b95ee37be675fa77**. Earlier publication commits are now `beef818` and `a02f471`; the earlier reports retain their historical hashes. Nu4's latest round-four report still claims no final verified export. This comparison retains the same accepted round-two draft and frozen route used in the previous quality test, copied into `runs/pi3-quality2-live`, so the writer code changes without silently replacing the paper's input evidence (F5).

Publication permits up to three targeted repair rounds, auditing after each. Each repair receives exact flagged sentence numbers, text, typed roles and reason categories. Only flagged paragraphs may change. Attempted and accepted repair counts are recorded separately. Exhaustion retains the original draft; incomplete or malformed audits do not authorize a targeted repair.

The publication audit uses nu4's roles: `source_claim`, `argument_step`, `framing`, `exposition`, `signpost`, `objection`, `reply`, and `unsupported_claim`. Presentation alone neither fails nor establishes route coverage. Source citations and mapped inference steps remain required. Publication-specific categories cover misplaced literature positioning, misplaced thesis restatements, unsupported elaboration and material departure from the original draft.

Both editorial and repair prompts restrict literature positioning to related work, thesis statements to abstract/introduction/conclusion, and elaboration to route nodes and answered CQs. The no-new-claims rule remains. The separate publication audit receives the original draft and logged literature records; the ordinary writer audit retains its own schema.

## Live outcome and quality limits

Five section calls succeeded. The first whole-paper attempt returned a retryable CLI error without a structured paper. The native retry returned an edit that failed the reading-word minimum: **3,727 reading / 3,507 annotated words**, excluding references and node/figure markers. Its related-work heading also differs in capitalization from the exact required heading; that is an additional observed structural mismatch, not the gate's logged rejection reason.

The pipeline stopped at length validation. **No post-polish semantic audit, targeted repair, or external citation/originality verification ran.** `audit_after_polish=fail` means there is no accepted audited polish; it does not mean a typed semantic auditor judged this shorter edit adverse. The three-round live recovery path therefore remains unexercised, despite its offline coverage. The fallback is the exact original draft and was not freshly audited in this run (F1).

The shorter edit is retained with a visible rejection notice for review. Its more concise prose does not establish supported claims, strong journal quality or compliance with the requested length. The fallback retains its existing repetition and lacks the revised abstract and related-work section. The prose-quality goal remains unmet. No favorable-verdict rerun or length waiver was used.

## Evidence boundary

Both supplied eps2 files were logged verbatim again with SHA-256 hashes and their verification receipts. They remain separate from frozen T. Source-linked read passages may support literature positioning; metadata-only records cannot become substantive evidence. Route 1's record supports partial anticipation. The focused L3 absence concerns another thesis and cannot be transferred to this route. Any absence claim remains bounded to the stated 2018–2026 search; no new literature search or novelty certificate is claimed (F2).

The publication audit is configured and tested to check that section against the same record. This live edit failed before that audit, so its related-work section remains **unaudited review evidence**. Rendering it is not acceptance. The route still rests on two frozen items from one paper, and model-assigned roles are not proof of semantic equivalence or philosophical quality (F3).

Reading Markdown, PDF and figures show author–year/page citations. The frozen source locators identify physical PDF page 18; no printed-page offset was guessed. Raw IDs and exact provenance remain in the annotated result and citation receipts. The fallback bibliography contains only references actually used. The rejected review has a separate citation receipt.

## Artifact proof

The delivered fallback has **12 pages and two figures**. The rejected review has **nine pages and two figures**. Both have embedded Liberation Serif and DejaVu Serif fonts, captions present, and no detected HTML or PDF glyph overflow. Visual inspection covered fallback pages 1/11/12 and review pages 1/7/9: title/rejection notice, citation display, figures and references were readable with no visible clipping.

The original copied files, frozen evidence and input draft remain unchanged; the original event-log/anchor prefix is preserved. Real SVG regeneration is byte-identical. Copied paper files match checked artifacts, and raw citation/node IDs are absent from fallback reading Markdown/PDF. [Integrity receipt](/home/dev/ara-work/pi3/runs/pi3-quality2-proof/artifact-integrity.json), [artifact/visual checks](/home/dev/ara-work/pi3/runs/pi3-quality2-proof/artifacts-complete.json), [rejected review checks](/home/dev/ara-work/pi3/runs/pi3-quality2-proof/rejected-result.json).

Fallback PDF SHA-256: `08e315b92fe58bfbc09e9162857a6dca0cd662b43b6c1d93cb61a226d89dfbc2`. Rejected review PDF SHA-256: `5c654af6870f49a23e853cffa0d2fb07295215d134786b6b17777a7a95405cb7`.

## Executed verification

- Initial updated regressions: **16 failed, 16 passed**, before typed publication integration.
- Focused publication, typed-audit, targeted-revision, audit-label and schema checks: **107 passed**.
- Full `uv run --locked pytest -q --basetemp /dev/shm/ara-pi3-quality2-final-delivery`: **1,388 passed, four skipped / 1,392 collected**, exit 0, 1,367.63 seconds. The skips are existing opt-in provider/OCR checks.
- The tests exercise successful repairs on rounds one, two and three, original fallback after exhaustion, unchanged unflagged paragraphs, framing without false positives, publication issue propagation, and literature scope/support checks.
- **621/621 sequential mutation controls passed**, exit 0: every mutation exited 1 and every restored check exited 0. They ran after full pytest in `/home/dev/ara-work/pi3-quality2-controls`, whose 254 file contents matched the tested snapshot. This isolated the live publication process from source mutations. Both checkouts match the final snapshot, all 13 owned committed blobs match it, and the primary working tree is clean. `git diff --check` passed (F6).

[Focused log](/home/dev/ara-work/pi3/runs/pi3-quality2-proof/focused-first.txt), [full pytest](/home/dev/ara-work/pi3/runs/pi3-quality2-proof/pytest-full.txt), [tested snapshot](/home/dev/ara-work/pi3/runs/pi3-quality2-proof/tested-source.json), [control progress](/home/dev/ara-work/pi3/runs/pi3-quality2-proof/checks-progress.json).

## Accounting and handoff boundary

The live followup records **seven actual Opus dispatches**: five section calls and two whole-paper attempts. No semantic audit or repair call was made. All model receipts report `claude-opus-5-5` through Claude Code 2.1.306; the isolation canary passed. The inherited writer's requested Codex identity remains unverified in its historical receipts.

The first whole-paper call returned `cli_exit_error` after 868.646 CLI seconds, with measured usage and no structured paper. Earlier progress messages calling it a timeout/unknown usage were corrected. Its 98,304 reported output tokens span four CLI-reported turns; those tokens are not a usable draft. Across the seven calls, receipts report 150,158 output, 98,850 cache-read, 350,208 cache-write and 22 uncached input tokens, with zero server-tool uses. These are provider-reported usage figures; subscription list-price equivalents are not measured API charges (F4). [Receipts](/home/dev/ara-work/pi3/runs/pi3-quality2-proof/receipt-counts.json).

No push or delegation. Generated prose, evidence, figures and PDFs remain ignored and uncommitted. Non-author review remains caller-owned. Local commit: **a0dc5e3ddfe30ef43a4447ae4a1357459b6110eb**, containing 13 owned files. The control checkout is retained for inspection; its results are also archived under the primary proof directory. [Final verification](/home/dev/ara-work/pi3/runs/pi3-quality2-proof/final-verification.json), [control results](/home/dev/ara-work/pi3/runs/pi3-quality2-proof/delta-controls/results.json), [structured handoff](/home/dev/ara-work/pi3/runs/pi3-quality2-proof/return-to-caller.json).

Finding placement: F1 → “Live outcome and quality limits”; F2/F3 → “Evidence boundary”; F4 → “Accounting and handoff boundary”; F5 → “Integration and repair behavior”; F6 → “Executed verification”. **6 findings, 6 placed.**

Implementation and the requested test/report cycle are complete. The next unresolved product step is a structurally compliant edit that can reach the typed audit; the current paper-quality goal remains unmet. The 4,500-word requirement remains in force.

DONE pi3 quality2 pdf=/home/dev/ara-work/reports/papers/pi3-quality2.pdf words=4959 audit_after_polish=fail repair_rounds=0
