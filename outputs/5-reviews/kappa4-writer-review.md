# Kappa4 — non-author review of nu4's writer

**Verdict: fix-first; one blocking finding.** Reviewed cumulative head `89be37a1074e87b34fc2b79dca0e2208020c8cda`, including sectioned-writer commit `c7ae7f53dae52afb607b2b5ae4f06fb6c7d50a5d`, against base `9b9999730c32b4dd0f06ef80a075920633d1acc9`. Scope follows `briefs/nu4-writer.md` and `briefs/nu4-round-2.md`. Work ran directly in `/home/dev/ara-work/kappa4-writer-checkout`, with no delegation, paid calls, source fixes or commits.

## W1 — Blocking: resumed drafts bypass the operator-identity boundary before logging and dispatch

The new `--draft` path enters [orchestration.py:205](/home/dev/ara-work/kappa4-writer-checkout/ara/runtime/orchestration.py:205), calls `validate_essay`, then immediately logs the complete document, saves `draft.unverified.json`, and sends it to the auditor. Validation checks schema, length and node coverage; it does not apply the provider's identity/output scan. The generated-output path does apply that scan.

An independent native reproduction uses the actual CodexCLIProvider with the repository's disposable fake CLI, fake credentials and synthetic configured operator identity. No real provider or operator data is involved. The imported draft contains the configured sentinel address:

- Directly passing the draft to the provider's `scan_output` rejects it with `operator_identity_in_output`.
- Passing the same document through `compose(..., draft=...)`, the function called by `select --draft`, accepts it, persists the identity in `essay_draft_resumed`, and includes it in the first dispatched audit prompt.
- A content-sensitive fake auditor flags that sentence; the targeted revision deletes it, and a second audit passes. All model response bodies are identity-free and pass the normal output scan. The final unverified document is also clean. Neither fact reverses the earlier disclosure to the auditor and log.
- The run later stops at the expected API-only `search_evidence` refusal. There is no final export in this reproduction, and no claim that an actual external provider received the sentinel.

A follow-up probe places the same configured identity only in the resumed title. Direct scanning rejects it, but resume persists it unchanged. The honest body-only audit passes without seeing the title, so targeted revision cannot remove it. The run again stops at the API-only retrieval boundary; the title remains in the unverified artifact (`identity-title.json`, `identity-title.log`).

Five positive boundary controls confirm that identity-bearing *generated responses* are rejected for outline, section, expansion, condensation and revision calls without leaking the sentinel into their logs. This isolates the regression to imported draft handling, rather than removal of the existing output guard.

Required repair: apply the effective writing provider's identity/credential checks to resumed draft content **before any log/file persistence or provider dispatch**. Reject with a sanitized diagnostic rather than echoing the document. Add a native `--draft`/compose regression proving that an identity-bearing draft reaches neither the auditor nor stored draft/event content, while a clean draft can still resume.

Evidence: `test_identity_probes.py`, `identity-resume.json`, `identity-events.jsonl`, `identity-probes.log`. The initial probe matrix passed 6/6 assertions; the follow-up title case passed separately after control restoration. An initial reviewer-observer failure while inspecting a null refusal response was corrected; its separate log is retained as `identity-probes-initial.log`.

## Writer preservation, outline budgets and source context

The expansion implementation concatenates the old accepted body and new paragraphs, then unions the exact permitted bibliography. It cannot replace the old body in expansion mode. An independent native run with real placeholder frozen metadata produced a 5,212-word assembled draft: all five initial section bodies remain exact prefixes, both required citations survive, and only the largest-deficit section s1 receives an expansion. The plan, prior sections and evidence go through the existing logged/cached call boundary. Evidence: `append-probe.json` and `test_behavior_probes.py`.

Eleven additional native outline probes accept the 4,800 and 5,600 budget endpoints and reject out-of-range sums, 3/11 sections, invalid individual budgets, duplicate IDs, and missing/unknown nodes before any section call (`outline-probes.py/json/log`). The owning tests additionally cover 4–10-section schema validation, unique section IDs, node coverage, aggregate 4,800–5,600-word budgets, deterministic section order, targeted condensation, and three-round exhaustion without regeneration or final export. Individual section and combined expansion limits are enforced after output; required source context is capped and refuses rather than silently truncating evidence. Exact source citation IDs/text and attributed source context are checked before accepting sections.

Condensation is explicitly a replacement of the selected overlong section; the append-only preservation guarantee applies to expansion. Content quality and useful elaboration remain model-dependent. The tests do not turn repeated placeholder prose into evidence of useful long-form argumentation.

## Splitter, targeted revisions and final-text audit

A deterministic 500-case splitter probe mixes punctuation, quotes, citations, node markers, spaces and newlines. Every non-marker, non-whitespace character appears in the audit inventory, and sentence spans never overlap. The owning regressions verify that trailing citations attach to the preceding sentence, including across transparent node markers. The audit prompt adds source-evidence requirements; its inventory, unknown-node, coverage and adverse-verdict checks are not relaxed.

Six independent revision scenarios confirm that valid flagged-span replacement or whole-sentence deletion preserves surrounding bytes and the bibliography. Retaining a claim while dropping or reordering its citations, or editing an unflagged span, is rejected. Deleting an entire unsupported sentence may legitimately remove that sentence's citations; this is distinct from stripping citations off retained text. Node coverage and word limits are revalidated.

A malicious repair that repeatedly substitutes unsupported R for flagged Q is detected by a content-sensitive fake auditor and stops after two revisions and three full audits. The correction cannot evade audit by adding another sentence: the updated document is split and audited again. Existing tests cover malformed inventories and missing-node failures that do not authorize repair.

An independent `compose` probe then lets citation verification remove a citation from an initially accepted draft. The final auditor sees that cleaned text, flags the resulting unsupported statement, and prevents `final_draft`, `draft.json` and export. This establishes that the post-verification audit is on the final text, not a cached audit of the original document.

Evidence: `splitter-probe.json`, `revision-*.json`, `final-audit-probe.json`, `behavior-probes.log` (9/9 assertions), and the owning audit/revision/verification tests. Semantic truth, faithful attribution and whether a claim is actually supported still depend on auditor judgment; a false-positive model judgment is not mechanically disproved by citation-string preservation.

## Verification, live-artifact limits and restoration

Fresh scoped pytest: **299 passed, 1 skipped / 300 collected**, exit 0, 290.99 seconds. The intentional skip is the existing paid-provider verification test (`ARA_LIVE_TEST` was disabled). The executed files cover writer sections, revisions, audit labels, word/body validation, source outlines, verification, model calls, Codex/Claude transport boundaries, schemas, stance, and native CLI replay. Exact command and output: `pytest-result.json`, `pytest.log`. The 15 independent pytest probe assertions and 11 native outline cases above are reported separately, not added to this suite count.

After pytest and the initial probes completed, the unchanged integration control runner executed **57/57 selected mutation/restoration pairs**, including all 18 controls introduced by these two writer commits. Each mutation caused the expected test failure and each restored test passed. The selection also covers existing audit, writer, verification and subscription isolation guards. These controls do not cover W1's imported-draft scan gap. Manifest, results and complete transcripts: `control-manifest.json`, `control-results.json`, `controls.log`, `controls/`.

All **239 tracked-file hashes**, including **eight temporarily mutated files**, match the pre-verification snapshot. The isolated clone is clean at the reviewed head and git diff --check passes. The author checkout had concurrent uncommitted changes at final observation; these were left untouched and are outside this pinned review. Its status is recorded in `final-verification.json`. No author source or live run was modified by this review. Evidence root: `/home/dev/ara-work/kappa4-writer-checkout/runs/kappa4-writer/`.

A read-only count of the author's saved round-2 document independently confirms **4,604 native words**, **4,553 without node markers**, and **4,468 without either node or citation markers**. The file hash is unchanged (`live-count-observation.json`). The native counter predates this change and includes machine markers; this result therefore does not prove a 4,500-word minimum under a stricter prose-only competition count.

No live generation, paid verification or live re-audit was rerun. The author's reported successful semantic audit and subscription `search_evidence` refusal remain historical receipts, not independently repeated live evidence. The native fake path above verifies later-stage ordering and failure enforcement. No submission-ready essay, successful real citation/originality verification, provider serving identity, or route-quality improvement is claimed. The author's disclosed pre-existing single-paper/omitted-support and stale-export limitations are outside this writer diff.

**4 findings, 4 placed:** identity-boundary regression in W1; expansion/budget/source preservation in “Writer preservation”; splitter/revision/final-audit behavior and semantic limits in “Splitter, targeted revisions and final-text audit”; executed verification, restoration, word-count and live-evidence limits in “Verification, live-artifact limits and restoration”. Only W1 blocks approval of this change.

DONE kappa4 writer verdict=fix-first blocking=1 tests=299/300 negctl=pass
