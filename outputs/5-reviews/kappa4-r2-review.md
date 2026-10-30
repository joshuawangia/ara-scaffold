# Kappa4 re-review — Pi Quality 4 and Nu4 Round 6

**Verdict: fix-first; two blockers at Nu4 d9ac619. Pi a6a2f9b closes NP-F1/F2/F3 and is mergeable for those fixes.** Independent offline verification is complete: **429 passed / 430 collected (one paid-provider skip); 82/82 scoped mutation controls passed**.

## Scope and intent

Reviewed immutable local clones of Pi `a6a2f9b8de76fe4792da0dcc790d7b2ffff71a1d` and Nu4 `d9ac619f6d95dfc588926044944d02d6181e5bdd`. Pi's parent merge `6fc46a4` includes Nu4 `0368a17`; Nu4 Round 6 is a separate change over `0368a17`, not present in this Pi head. This review checks enforcement and failure handling, not the semantic truth of model labels. No paid/live provider calls, delegation, source fixes, commits or pushes. Author worktrees, including Nu4's in-progress Round 7, were not changed.

Intent: imported publication drafts must be screened before effects; current structural text must be audited; repair permissions must identify the flagged occurrence. A final writer audit must use fresh samples, retain unresolved adverse evidence, and carry the bounded repair allowance on resume. Source citations must survive when they are already grounded in frozen local evidence.

## Blockers

### R2-F1 — P1: a structurally invalid audit can lose valid adverse evidence on unchanged-draft resume

Location: [essay_audit.py:104](/home/dev/ara-work/kappa4-r2-nu4/ara/runtime/essay_audit.py:104), particularly the catch/continue at line 113; [audit_result:65](/home/dev/ara-work/kappa4-r2-nu4/ara/runtime/essay_audit.py:65).

A schema-valid response labels sentence 2 `unsupported_claim` but omits sentence 3. The current call correctly rejects it and logs an incomplete final batch. Reprocessing that same response raises `Rejected` again; because `Rejected` subclasses `ValueError`, the history loop puts the whole receipt in `unusable_history` and continues. The valid adverse label is absent from the union. Three subsequent clean responses approve the unchanged draft. A duplicate sentence inventory, or an unknown node on another sentence, has the same effect.

Independent execution through native `compose`, then a new `ModelCalls` object over the same log/cache and the same imported draft, reproduced successful export with **zero repairs and byte-identical draft content** after the partial adverse final audit. No log editing or fake precomputed verdict was used. Both repeated direct consensus rerolls passed for all three malformed/adverse variants. The receipt honestly discloses unusable history, but that disclosure does not preserve the blocking obligation.

Required correction: retain valid, in-range substantive flags from incomplete/invalid inventories, or retain an unresolved blocking audit obligation until repair or explicit adjudication. Do not treat inability to reconstruct a complete verdict as permission to discard adverse evidence. Add native resume regressions for partial, duplicate and unknown-node adverse responses.

Evidence: [probe script](/home/dev/ara-work/kappa4-r2-nu4/runs/kappa4-r2/audit-probes.py), [results](/home/dev/ara-work/kappa4-r2-nu4/runs/kappa4-r2/audit-probes.json), [native unchanged-resume log](/home/dev/ara-work/kappa4-r2-nu4/runs/kappa4-r2/native-partial-resume/run/events.jsonl). Positive contrast: complete adverse history remains binding through two clean rerolls; schema-corrected complete adverse history remains bound to the original prompt hash despite a different correction prompt ([receipt](/home/dev/ara-work/kappa4-r2-nu4/runs/kappa4-r2/corrected-history-probe.json)).

### R2-F2 — P1, known/inherited: verification cleanup removes exact frozen-T citations and still exports

Location: [calls.py:1205](/home/dev/ara-work/kappa4-r2-nu4/ara/runtime/calls.py:1205), [calls.py:1253](/home/dev/ara-work/kappa4-r2-nu4/ara/runtime/calls.py:1253).

All bibliography entries, including exact local frozen-source locators, become external citation verification items. An external `unverified` result deletes the bibliography entry and citation marker. The final audit can classify the remaining statements as mapped argument steps and permit export without restoring source references. Three clean samples do not cure this deterministic provenance loss.

Independent competition-profile reproduction seeded actual frozen artifacts and commitment provenance, used the exact allowed bibliography, and ran native `compose`. The fake external verifier marked both local entries unverified. Result: **bibliography 2 → 0, citation markers 2 → 0, successful final k=3 audit and export**. Frozen artifacts themselves remained byte-identical. This is an existing cleanup flaw exposed by the final workflow, not a claim that Round 6 introduced the deletion code.

Nu4's Round 6 report independently records bibliography/citation counts of zero for both real routes. That is author-reported live evidence, not a new live run by this reviewer. Route 1 predates the cleanup-length/resume-budget correction; Route 2's corrected resume used final source. The report preserves this qualification.

Required correction: distinguish exact frozen local references from externally retrieved citation/quotation claims, preserve their source linkage, and enforce final citation obligations independently of role relabeling. Round 7 is reportedly fixing this; its dirty/uncommitted implementation is outside this review and does not close this finding at `d9ac619`.

Evidence: `frozen_citations` in [probe results](/home/dev/ara-work/kappa4-r2-nu4/runs/kappa4-r2/audit-probes.json), [native log](/home/dev/ara-work/kappa4-r2-nu4/runs/kappa4-r2/frozen-citations/run/events.jsonl), [export](/home/dev/ara-work/kappa4-r2-nu4/runs/kappa4-r2/frozen-citations/run/export/essay.txt), [author report](/home/dev/ara-work/reports/nu4-writer.md:748).

## Closure of NP-F1/F2/F3 at Pi a6a2f9b

| Finding | Result and executed evidence |
| --- | --- |
| NP-F1: imported identity/credential leak | **Closed.** Re-ran the prior body-identity/title-credential cases through the native CLI/default factory and disposable offline executable. Both refuse with sanitized codes, no new canary/model dispatch, no sentinel persisted to run logs/output artifacts, and no publication artifact. Authored native boundary tests additionally cover bibliography/unexpected fields and screening by the effective audit provider. Screening occurs before budget/provider startup and before publication effects. |
| NP-F2: moving unsupported content into the title | **Closed for publication.** The previous repair moving R from body into title is rejected, retaining the original draft. Current title participates in audit input/cache identity. Authored tests check title-only cache invalidation, persistent adverse titles, successful repairs to flagged titles/headings, and re-audit of the repaired text. The independent unflagged-heading movement probe also rejects. |
| NP-F3: duplicate-text repair authorization | **Closed.** The previous duplicate-sentence probe is rejected; only paragraph 1 is authorized. Offsets bind the exact occurrence to one block, while all unflagged blocks and separators must remain unchanged. Authored positive control permits editing only the flagged occurrence. |

Independent Pi evidence: [publication probes](/home/dev/ara-work/kappa4-r2-pi3/runs/kappa4-r2/publication-probes.json), [import probes](/home/dev/ara-work/kappa4-r2-pi3/runs/kappa4-r2/import-probes.json). Source: [screening](/home/dev/ara-work/kappa4-r2-pi3/ara/runtime/calls.py:212), [current title](/home/dev/ara-work/kappa4-r2-pi3/ara/runtime/calls.py:1200), [occurrence binding and scope](/home/dev/ara-work/kappa4-r2-pi3/ara/runtime/publication_audit.py:60).

## Other requested enforcement checks

- Complete adverse history cannot be outvoted by three clean fresh responses or a favorable cached entry. Fresh calls bypass cache reads and writes. k≥3 and configured k=4, disagreement receipts, union repair, re-verification and final re-audit are covered by scoped tests and controls.
- Independent new-object resume probes with two and three already-used rounds, including an interleaved unrelated route, permit respectively only round 3 and no further repair. They end rejected with no export. Authored tests additionally exhaust the native initial/final shared allowance, resume its saved partial draft, and invalidate stale successful exports.
- Incomplete current batches refuse and record partial results. The failure is the subsequent handling of their adverse history, described in R2-F1; ordinary schema-corrected complete adverse results do remain binding.
- Publication still rejects an unsupported body claim after at most three repairs. The 3,000 reading-word floor and fixed 6,000 ceiling are unchanged; Nu4 permits final verification cleanup/repair below its construction target while retaining its ceiling and structural checks. Scoped tests cover those policies.

## R2-N1 — remaining evidence and product limits (non-blocking note)

Pi's pinned head contains Round 5, not Round 6 consensus. The earlier audit nondeterminism/cache limitation is not solved by its three enforcement fixes; per the assignment, this alone is not an additional blocker. These two branches were reviewed separately, with no claim about their combined integration. Pi's Quality 4 live polish failed at a below-floor second repair and retained the original; external citation verification was not run in that failed attempt. Closure of NP-F1/F2/F3 does not turn that run into a successful polish.

Fresh requests do not prove statistical independence, reliable semantic labels, source fidelity or originality. Offline fakes establish gate behavior given labels. No live pilot, PDF visual inspection, complete corpus evaluation, or non-publication title-audit redesign was performed here. Author full-suite and full-control receipts remain historical evidence, separate from the independent scoped receipts below.

## Verification

Independent offline scoped pytest: **429 passed, one skipped / 430 collected**, zero failures.

| Pinned checkout | Executed scope | Result |
| --- | --- | --- |
| Pi a6a2f9b | Publication/boundaries, typed audit, sentence labels/revision, verification export, schemas, construction stages and resumed-draft screening | 163 passed / 163, 144.37 seconds |
| Nu4 d9ac619 | Consensus, typed audit, labels/revision, calls, outline/sectioned writer/validation, resume screening, Codex transport/schema, known verification/export/receipts, schemas and CLI | 266 passed, one skipped / 267, 309.66 seconds |

Commands use `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked pytest -q` with exact file selections in each evidence root's `pytest-files.json`. These are independently rerun affected suites, not a claimed rerun of either author's full suite. [Pi pytest log](/home/dev/ara-work/kappa4-r2-pi3/runs/kappa4-r2/pytest.log); [Nu4 pytest log](/home/dev/ara-work/kappa4-r2-nu4/runs/kappa4-r2/pytest.log).

Independent probe scripts completed **15 cases** (nine Nu4, six Pi); defect reproductions intentionally assert the observed bad outcomes and are not counted as green product regressions. Fixtures use placeholders and offline executables; probe sockets explicitly refuse network connections.

The repository's native `tests/integration/negative_controls.py` runner executed **82/82 selected production-wire controls**, sequentially after all pytest/probes stopped: **32 Pi** (355.26 seconds), then **50 Nu4** (245.28 seconds). Exact selections are retained in each `control-manifest.json`. Every mutation exited 1 with actual failed tests, every restored run exited 0 with passed tests, and none relied on a collection error. This is a scoped control run, not the author's full 640/621-control run.

[Pi control results](/home/dev/ara-work/kappa4-r2-pi3/runs/kappa4-r2/control-results.json), [Pi transcript verification](/home/dev/ara-work/kappa4-r2-pi3/runs/kappa4-r2/control-transcript-verification.json); [Nu4 control results](/home/dev/ara-work/kappa4-r2-nu4/runs/kappa4-r2/control-results.json), [Nu4 transcript verification](/home/dev/ara-work/kappa4-r2-nu4/runs/kappa4-r2/control-transcript-verification.json).

Final integrity verification matched all **255 Pi and 243 Nu4 tracked paths** against both the original source snapshot and committed blobs, including symlink targets. Both review clones are clean, pinned to the requested commits, and pass `git diff --check`. [Pi final verification](/home/dev/ara-work/kappa4-r2-pi3/runs/kappa4-r2/final-verification.json); [Nu4 final verification](/home/dev/ara-work/kappa4-r2-nu4/runs/kappa4-r2/final-verification.json).

The one skipped test is the explicitly opt-in paid-provider known-case check (`ARA_LIVE_TEST=1` required). No test failed. This does not contradict fix-first: the independent probes expose two behaviors the existing passing regression suite does not prohibit. The next step is to fix R2-F1 and review the completed Round 7 citation fix against R2-F2, then rerun those reproductions and affected checks.

## Finding placement

R2-F1 and R2-F2 → “Blockers”; NP-F1, NP-F2 and NP-F3 → “Closure of NP-F1/F2/F3”; R2-N1 → “Remaining evidence and product limits”. **6 findings, 6 placed: two blockers, three closed findings, one non-blocking note.**

DONE kappa4 r2 verdict=fix-first blocking=2 tests=429/430 negctl=pass
