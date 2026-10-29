# pi3 quality3 — typed audit passed after one repair

Route 1 now reaches and **passes the typed post-polish audit after one targeted repair round**. The accepted paper has **3,471 reading words** (3,541 in the Markdown including references; 3,120 in the annotated audit copy), nine PDF pages, and two deterministic figures. It uses author–year citations and a related-work section audited against both logged eps2 records. This is an audit pass, not an independent research-quality or submission verdict (F1).

- [PDF](/home/dev/ara-work/reports/papers/pi3-quality3.pdf)
- [Markdown](/home/dev/ara-work/reports/papers/pi3-quality3.md)
- [Citation IDs and provenance receipt](/home/dev/ara-work/reports/papers/pi3-quality3-citations.json)
- [Event-derived methodology](/home/dev/ara-work/reports/papers/pi3-quality3-methodology.md)

## Length policy and integration

The publication floor defaults to **3,000 words**, configurable by `publication_min_words` in the run configuration or `ara polish --min-words N`; the CLI override wins. The ceiling remains **6,000 words**. The minimum is explicitly an ARA profile setting, not a competition rule. The effective bounds, count basis, and preference for a tight supported paper over padding appear in the logged `publication_length_policy`, publication receipt and methodology. The writer's separate 4,500-word profile is unchanged. Publication audits receive full source evidence at every configured minimum (F2).

Local commit **61d5a8c** on `feat/publication` contains 13 owned files. Nu4's newest `fix/writer-length` head, **d15eb43**, is already an ancestor and supplies the typed audit. Related-work heading capitalization is stylistic, with case-insensitive scope validation. Up to three targeted repairs remain enabled, preserving the no-new-claims constraint, exact sentence/category feedback, unchanged unflagged paragraphs, literature positioning only in related work, and thesis statements only in abstract/introduction/conclusion.

## Live audit and evidence boundary

The initial whole-paper edit passed structure at 3,325 reading words. The first audit covered all three route nodes and rejected 17 sentences as `miscited_source_claim`. Repair 1 changed only the seven flagged paragraphs. The full second audit covered all three nodes, reported no missing nodes or flags, and accepted 201 sentence labels: 43 argument steps, 26 source claims, 48 exposition, six framing, five objections, 29 replies and 44 signposts. One repair was attempted and accepted; rounds two and three were unnecessary. [Audit history](/home/dev/ara-work/pi3/runs/pi3-quality3-proof/audit-history.json).

The related-work section confines its claims to the verified eps2 records, identifies partial anticipation, retains access/version limits, and makes no novelty claim. It does not apply the focused L3 search's different question to this route. The repair removed a substantive attribution based only on an unavailable work's abstract. This is a bounded reconstruction; it does not independently establish its premises, restore omitted source support, or establish a new result. Imported literature receipts are not a fresh independent search (F1).

**External citation/originality verification remains blocked** with `stage_requires_api_provider`. The isolated Claude Code provider cannot retrieve external evidence; no API fallback was invoked. `ara polish` consequently returned exit 2 while retaining the audited publication. Local exact citation membership passed. The audit assesses the annotated text against logged evidence; neither it nor bibliography display independently verifies those records (F3).

Three first-audit flags also exposed an existing sentence-tokenizer limitation: `PDF pp.` was split before its citation. Repair spelled out `PDF pages` in the annotated prose, and re-audit passed. The tokenizer itself is unchanged and can still flag this abbreviation in future drafts (F4).

## PDF and integrity checks

The nine-page PDF embeds four serif font subsets. Both figures and captions are present; automated HTML horizontal-overflow and PDF glyph-bound checks found none. Figures reproduce byte-for-byte from the retained route and provenance. Raw `[cite:...]`, `[lit:...]` and node markers are absent from the reading Markdown/PDF; seven evidence IDs remain mapped in the receipt. Pages 1, 4, 6, 7, 8 and 9 were inspected visually. The main pages and figures are legible. Remaining presentation limits are dense repeated source locators in related work and a sparse final page holding one bibliography entry; the audit pass does not remove these editorial limits (F5).

The original 38-file copy, frozen artifacts and source draft are unchanged; only append-only event/anchor files grew. The report copies exactly match the run outputs. Physical PDF page locators come from provenance, without guessed printed-page offsets. [Artifact checks](/home/dev/ara-work/pi3/runs/pi3-quality3-proof/artifact-integrity.json), [visual checks](/home/dev/ara-work/pi3/runs/pi3-quality3-proof/visual-checks.json).

## Executed verification and accounting

- New regressions were observed red: 16 failed, 28 passed.
- Focused publication, typed-audit, audit-label and export suite: **90 passed**.
- Full pytest: **1,400 passed, four skipped**, exit 0, in 1,591.82 seconds. The skips are existing opt-in provider/OCR cases.
- **627/627 sequential mutation controls passed**, exit 0: every mutation exited 1 and every restored check exited 0. They ran after full pytest in an isolated checkout with the same 254-file source snapshot. Both checkouts match the snapshot, all 13 owned committed blobs match it, and the primary working tree is clean. `git diff --check` passed (F6).

The live run made nine actual Opus dispatches: five section edits, one whole-paper edit, two audits and one repair. All receipts report `claude-opus-5-5`; the isolation canary passed. Provider-reported totals for those calls are 111,623 output tokens, 5,597 cache-read, 413,026 cache-write, 20 uncached input and zero server-tool uses. Subscription list-price equivalents are not measured API charges. The inherited writer's requested Codex identity remains unverified in historical receipts. [Accounting](/home/dev/ara-work/pi3/runs/pi3-quality3-proof/receipt-counts.json), [full pytest](/home/dev/ara-work/pi3/runs/pi3-quality3-proof/pytest-full.txt), [control progress](/home/dev/ara-work/pi3/runs/pi3-quality3-proof/checks-progress.json).

No push or delegation. Generated prose, evidence, figures and PDFs remain ignored and uncommitted. Non-author review remains caller-owned. Final verification confirms commit **61d5a8c7a240a591eada1bf6a23165e20991da7c**, nu4 ancestry, exact tested source, preserved input copy and report-artifact hashes. [Final verification](/home/dev/ara-work/pi3/runs/pi3-quality3-proof/final-verification.json), [control results](/home/dev/ara-work/pi3/runs/pi3-quality3-proof/delta-controls/results.json), [structured handoff](/home/dev/ara-work/pi3/runs/pi3-quality3-proof/return-to-caller.json). Implementation and the requested quality3 test/report cycle are complete; external retrieval and non-author review remain as disclosed above.

Finding placement: F1 → “Live audit and evidence boundary”; F2 → “Length policy and integration”; F3/F4 → “Live audit and evidence boundary”; F5 → “PDF and integrity checks”; F6 → “Executed verification and accounting”. **6 findings, 6 placed.**

DONE pi3 quality3 pdf=/home/dev/ara-work/reports/papers/pi3-quality3.pdf words=3471 audit_after_polish=pass repair_rounds=1

## Quality 4 — enforcement verified; live polish failed and original retained

Local commit **`a6a2f9b8de76fe4792da0dcc790d7b2ffff71a1d`** fixes NP-F1, NP-F2 and NP-F3 from [kappa4's review](/home/dev/ara-work/reports/kappa4-nu4pi3-review.md). Merge `6fc46a4` includes the requested nu4 round-5 head **`0368a17992c7ef8339abb7913b08792b7d785786`**; both appended decision histories and control inventories were retained. No push or delegation. This report claims implementation and verification of the enforcement fixes, not non-author approval or successful editorial polish.

**NP-F1 — import screening.** Imported drafts now use the shared writer-resume `ModelCalls.screen_imported_draft`. The complete object is scanned by both effective providers before budget initialization, validation diagnostics, isolation-canary dispatch, content-bearing logs or fallback writes. Direct `polish` also screens before its first effect. Native CLI regressions cover identity and credential sentinels in title, body, bibliography and unexpected fields, requiring no provider dispatch and no persisted sentinel.

**NP-F2 — current structural text.** Publication audit inputs include the current title, body sentences and headings. A title-only change invalidates the audit cache input. Unflagged title and heading blocks remain byte-identical during repairs; flagged structural blocks can be repaired, then must pass a fresh audit. Unsupported current titles still fail after all three repair rounds. This fixes publication's optional audit context; nu4's separate non-publication writer audit redesign remains outside this change.

**NP-F3 — occurrence-bound permission.** Each flagged sentence's original field offsets identify its unique owning block and paragraph index. Identical sentence text elsewhere grants no edit permission. Every unflagged block and every inter-block separator is compared byte-for-byte. A duplicate-sentence regression rejects edits to the unflagged second occurrence while accepting the targeted first-occurrence repair.

### Native run and failed polish

The native command selected `--audit-provider codex_cli`, retained Opus for section edits, whole-paper editing and repairs, and logged both eps2 currency records. Provider scopes share the budget, cache boundary and append-only event log; each passed its own isolation canary. The model defaults to the recorded writer model unless `--audit-model` is supplied. This run requested `gpt-6-luna` for auditing and `claude-opus-5-5` for editing. Codex's serving identity is **unverified** in its receipts; Opus receipts report the requested model. A separate logged native placeholder schema probe passed, establishing wire acceptance only.

The run used a fresh verified copy of nu4's round-5 route-1 final draft, SHA-256 `083600f45d088742f4a7bcd914f85873d1bb7950944f16d9150f2367c339160b`, with its original topic, route, frozen evidence and history. The whole-paper edit passed structural checks. The first Codex audit flagged **20 sentences**; repair 1 passed the exact edit-scope checks. The second audit flagged **38 sentences**, including 26 in blocks unchanged by repair 1. The prompts differed because other blocks were repaired: this is a judgment shift under changed context, not an identical-prompt nondeterminism experiment. The current title was included in the first audit as sentence 195. See [audit history](/home/dev/ara-work/pi3/runs/pi3-quality4-proof/audit-history.json) and [transition receipt](/home/dev/ara-work/pi3/runs/pi3-quality4-proof/audit-transition-1.json).

**Repair 2 was rejected at 2,765 reading words**, below the unchanged 3,000 floor. It never reached another audit. The existing pipeline ends on a structurally invalid repair, so it attempted two repairs and accepted one; it did not invoke repair 3. The up-to-three policy remains intact. No adverse judgment was retried without a content repair, no length limit was lowered, and no audit was softened. `ara polish` exited **2**, recorded `polished=false`, and retained the original draft. The post-polish result is **fail**; the last audit applies to the repaired candidate, not a new audit of the retained original. [Rejected repair receipt](/home/dev/ara-work/pi3/runs/pi3-quality4-proof/rejected-repair-2-summary.json).

The final fallback has **5,065 reading words**, **5,092 Markdown words including references**, and **4,670 annotated audit words**. **Native external citation/originality verification was not run in this attempt**, because polish failed; this differs from quality3's accepted polish followed by blocked external retrieval. No new related-work section survived into the retained original. Both eps2 records remain logged, but the fallback cites neither and makes no new literature-positioning claim. The requested editorial improvement and related-work section remain unmet in this run.

### Artifact checks and accounting

- [Fallback PDF](/home/dev/ara-work/reports/papers/pi3-quality4.pdf)
- [Fallback Markdown](/home/dev/ara-work/reports/papers/pi3-quality4.md)
- [Citation IDs and provenance receipt](/home/dev/ara-work/reports/papers/pi3-quality4-citations.json)
- [Event-derived methodology](/home/dev/ara-work/reports/papers/pi3-quality4-methodology.md)

Native `figures` and `render-pdf` succeeded. The **12-page** PDF contains two byte-reproducible route/source figures and three embedded serif-font subsets; automated HTML horizontal-overflow and PDF glyph-bound checks found none. Raw citation and node markers are absent from the reading Markdown/PDF; two evidence IDs remain mapped in the receipt. Locators preserve recorded physical PDF pages, without guessed printed-page offsets. Pages 1, 6, 10, 11 and 12 were visually inspected: text, figures, captions and references are legible. The fallback remains highly repetitive, lacks the polished abstract and related-work section, and appends figures with substantial page whitespace. Rendering success does not imply journal or submission readiness. [Visual checks](/home/dev/ara-work/pi3/runs/pi3-quality4-proof/visual-checks.json).

The 134-file original copy and frozen artifacts are unchanged; only append-only event/anchor files grew, with their original prefixes verified. The fallback draft equals the original `draft.json`; report copies match generated outputs by hash. [Artifact integrity](/home/dev/ara-work/pi3/runs/pi3-quality4-proof/artifact-integrity.json).

The run made **10 actual model dispatches**: eight Opus edits (five sections, one whole paper, two repairs) and two Codex audits. Both audit calls returned complete adverse labels and were rejected. Aggregate provider-reported usage: 76,618 input tokens, 148,728 output tokens, 40,518 cache-read tokens, 502,751 cache-write tokens and zero server-tool uses. These totals exclude the separate schema probe and isolation canaries, whose receipts are retained. Subscription list-price equivalents are not measured API charges. An ignored accounting script initially failed on Codex's null served-model field; it was corrected to preserve the unverified identity rather than substitute the requested model. Production code and model results were unchanged. [Accounting](/home/dev/ara-work/pi3/runs/pi3-quality4-proof/receipt-counts.json).

### Verification and the three review notes

Red-first evidence: **18 failures** before the fixes. Focused verification: **104 passed**, including native CLI selection of both audit providers. Full pytest: **1,425 passed, four skipped / 1,429 collected**, exit 0, in 1,620.63 seconds. The skips are existing opt-in provider/OCR checks. All **640 mutation anchors** resolve exactly once. **640/640 sequential mutation controls passed**, exit 0: every mutated test exited 1 and every restored check exited 0. Controls ran after full pytest in an isolated checkout. Both source trees match the tested snapshot, all 14 owned committed blobs match, and the primary working tree is clean. `git diff --check` passed. [Red tests](/home/dev/ara-work/pi3/runs/pi3-quality4-proof/red-final.txt), [focused tests](/home/dev/ara-work/pi3/runs/pi3-quality4-proof/focused-complete.txt), [full pytest](/home/dev/ara-work/pi3/runs/pi3-quality4-proof/pytest-full.txt), [control progress](/home/dev/ara-work/pi3/runs/pi3-quality4-proof/checks-progress.json).

**NP-N1 — audit instability remains unresolved.** The recorded round-5 disagreement and favorable cache replay are not solved by these enforcement fixes; nu4's round-6 redesign remains separately owned and is not included in this pinned round-5 merge. The changed-context judgment shift in this live run is additional bounded evidence, not a new identical-prompt experiment.

**NP-N2 — length policy.** The configurable 3,000-word publication floor is an ARA profile choice, with a fixed 6,000 ceiling. Count basis and effective bounds appear in methodology. The floor was enforced even though it prevented accepting repair 2. Writer and publication counts remain distinct; the reading count includes rendered inline citations, title and abstract when present, excludes references/node markers/figure placeholders, and still counts Markdown heading tokens.

**NP-N3 — proof and product limits.** Authored offline tests and mutation controls establish enforcement given labels. They do not establish truthful/stable semantic classification, independent literature verification or submission readiness. The live audit failed, the fallback preserves repetitive prose and lacks the attempted related-work section, and external citation verification was not run. Non-author re-review remains caller-owned. Generated prose, logs, evidence, figures and PDFs remain ignored and uncommitted.

Quality 4 finding placement: NP-F1/F2/F3 → the respective fix paragraphs; NP-N1/NP-N2/NP-N3 → the corresponding review-note paragraphs, with live/artifact evidence above. **6 findings, 6 placed.** Final verification confirms the pinned nu4 ancestry, exact tested source, restored control checkout and copied artifact hashes. [Final verification](/home/dev/ara-work/pi3/runs/pi3-quality4-proof/final-verification.json), [control results](/home/dev/ara-work/pi3/runs/pi3-quality4-proof/delta-controls/results.json), [structured handoff](/home/dev/ara-work/pi3/runs/pi3-quality4-proof/return-to-caller.json). The requested fix/verification/rerun/report cycle is complete; successful polish and non-author re-review remain unresolved as stated above.

DONE pi3 quality4 head=a6a2f9b8de76fe4792da0dcc790d7b2ffff71a1d tests=1425/1429 negctl=pass fixed=NP-F1,NP-F2,NP-F3 pdf=/home/dev/ara-work/reports/papers/pi3-quality4.pdf
