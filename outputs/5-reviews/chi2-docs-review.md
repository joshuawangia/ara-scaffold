# Chi2 non-author documentation review

**Verdict: fix-first. One blocking integration finding; zero executable changes in the reviewed branch.** The documentation cleanup passes the other seven requested checks. It cannot merge cleanly onto xi's current head.

Reviewed `docs/deslop-organize` at `0ebff970bc3e80da5b1924286196729bcbe7b72e` in `/home/dev/ara-work/omicron3`, against `6511ff6cb2bb5d88c5abedc1f20b715a03324d0f`. Xi was `feat/run-report` at `9f07ba0a50df2802d56302134f85e4a896a23dd6`, checked again before handoff. The omicron3 report's opening revision predates its final redaction; this review includes that redaction commit.

Intent: shorten and organize the operating documentation while preserving facts, qualifications, history and repository rules. Review requirements came from `briefs/chi2-docs-review.md` and `briefs/omicron3-docs.md`. I performed the review myself, without delegation, paid calls, branch edits, commits or pushes.

## Findings and required action

| ID | Severity / blocking | Location | Finding and resolution |
| --- | --- | --- | --- |
| F1 | P1 / yes | `README.md:50`, `DECISIONS.md:3325`; integration also affects `PLAN.md:35`, `docs/construction.md:168`, `docs/search.md:105`, `docs/reporting.md` | The scratch merge onto xi fails in **README.md and DECISIONS.md**. Xi adds `fork-from-freeze`, target-triviality rejection and derived-route default selection. Preserve xi's new decisions and the documentation correction entry; retain the short README and move xi's operating detail into the appropriate guides. Update the integrated status/command map and selection/reporting descriptions against xi's parser and runtime. Repeat command/link checks and the scratch merge on the resolved revision. |

F1 evidence: from a separate local clone at xi's pinned SHA, `git -c core.hooksPath=/dev/null merge --no-commit --no-ff 0ebff970bc3e80da5b1924286196729bcbe7b72e` exited **1**; `git diff --name-only --diff-filter=U` returned exactly `DECISIONS.md` and `README.md`. Scratch clone: `/tmp/chi2-docs-merge`; [merge receipt](chi2-docs-review/merge.json).

The merge conflict is also a content-integration task. The reviewed README says “`fork-from-freeze` is **not available** at base `6511ff6`,” which is accurate for this review base. Xi's README addition documents that command and its read-only source contract. Its Round 13 decision also changes automatic/interactive selection to derived routes, whereas `docs/search.md:109` retains the earlier first-CLOSED/otherwise-OPEN smoke policy. Keeping either side wholesale would discard useful documentation or leave the integrated guides describing the earlier runtime. These are one integration finding, not defects attributed to omicron3's unchanged base code.

Classification: confidence 100; owner `downstream-resolver`; fix class `manual`. No resolution was applied. The requested next step is a documentation merge resolution followed by verification at the resulting head.

## Check results

| Requested check | Result | Evidence |
| --- | --- | --- |
| Only documentation changed | PASS | `git diff --stat 6511ff6 HEAD`: 16 paths, 1,824 insertions, 1,154 deletions. Every changed path is Markdown or the AGENTS/CLAUDE symlink reversal. Zero Python, tests, prompts, schemas, configuration, lockfile or workflow changes; no deleted tracked paths. [Stat](chi2-docs-review/diff-stat.txt), [file inventory](chi2-docs-review/diff-files.txt). |
| Facts survived | PASS, sampled | 25 old-README facts traced below to the new guides, including numerical limits and evidence caveats. |
| Commands and flags exist | PASS for this head | All 12 ARA subcommands returned help; 47 parser-accepted command examples/mentions, plus helper/tool help and source checks. The sole absent documented long option is explicitly unavailable `--from-frozen`. Details below. |
| Decision history preserved | PASS with authorized redaction exception | All 3,023 original lines remain in order except the single L1 identity substitution. No decision was removed. The 43 new status annotations resolve to relevant replacement decisions. |
| No Markdown leaks found | PASS within stated scope | All 19 tracked Markdown paths inspected/scanned; no remaining L1 account identifier, credential-shaped value, email, non-generic home identity, or substantive paper topic/content found. Bibliographic metadata scope is stated below. |
| Links resolve | PASS | 232 relative path/anchor references resolve against tracked paths; all ten distinct external URLs returned HTTP 200. |
| Plain prose | PASS | README is 110 lines rather than 988; concern guides put commands next to prerequisites and explain limits directly. Technical contract names remain where needed. No consequential prose defect found. |
| Clean merge with xi | FAIL | Two conflicts, both documented in F1. No conflicts outside `README.md` and `DECISIONS.md`. |

`git diff --check 6511ff6 HEAD` passed. The reviewed worktree was clean before and after the checks. The committed-tree diff, rather than a working-directory inventory, establishes the documentation-only scope.

## Fact-retention sample

Old line numbers refer to `6511ff6:README.md`; new locations refer to the reviewed head. I checked the surrounding qualifications as well as the matched phrases. This is a spot check, not a claim that every old sentence was retained unchanged. [Machine-recorded mapping](chi2-docs-review/facts.json).

| Preserved fact | Old README line | New home |
| --- | ---: | --- |
| Historical live-smoke cost remains USD1.058455 and is historical evidence. | 43 | `docs/verification.md:27` |
| Smoke output allowance remains 8,192 tokens. | 90 | `docs/providers.md:45` |
| Pilot draft bounds remain 4,500–6,000 words. | 151 | `docs/search.md:45` |
| Pilot caps remain USD100 and 10,000,000 tokens, with no completion guarantee. | 163 | `docs/search.md:58` |
| Extraction profile caps remain USD30 and 6,000,000 tokens. | 189 | `docs/extraction.md:23` |
| Folio labels are distinct from physical page indices. | 240 | `docs/extraction.md:84` |
| Rich construction retains one lifecycle and one freeze. | 242 | `docs/construction.md:5` |
| Construction batch allowances retain 70k input, 64k output and 16k shared-symbol reserve. | 244 | `docs/construction.md:7` |
| Working T retains its 100k downstream-input limit. | 261 | `docs/construction.md:26` |
| The 53-paper test counter is a proxy rather than a real tokenizer forecast. | 272 | `docs/construction.md:40` |
| Sparse image/form-page diagnostic threshold remains 200 text characters. | 277 | `docs/extraction.md:91` |
| Legacy v1 extraction artifacts are refused; rich v2 regeneration is required. | 296 | `docs/extraction.md:112` |
| Re-importing a receipt in one log is idempotent. | 299 | `docs/extraction.md:116` |
| PDF bytes partition cache identity even for identical text. | 301 | `docs/extraction.md:119` |
| Append-only logs retain full prompts/responses and usage. | 365 | `docs/accounting.md:24` |
| Redaction is literal and methodology remains identifiable. | 372 | `docs/accounting.md:31` |
| Measured usage, unknown reservations and budget-accounted totals remain distinct. | 398 | `docs/accounting.md:44` |
| Report HTML retains a 15 MB cap, 12 MB working budget and 64 KB section limit. | 533 | `docs/reporting.md:18` |
| Reports retain eight evidence sections and links to full receipts. | 549 | `docs/reporting.md:36` |
| Reporting checks chains and available tail checkpoints before writing. | 557 | `docs/reporting.md:45` |
| Reports keep local/inherited and measured/reserved accounting separate. | 566 | `docs/reporting.md:54` |
| Construction allocation retains 20% headroom. | 602 | `docs/construction.md:47` |
| Subscription calibration retains p99 API token/byte ratios and a 5% margin; it is an estimate. | 773 | `docs/accounting.md:53` |
| OCR span admission retains confidence ≥0.95 and at most 5% low-score characters. | 849 | `docs/ocr.md:46` |
| Local schema validation keeps a 100,000-value node bound. | 960 | `docs/providers.md:241` |

The changed guidance also distinguishes deliberate corrections from lost facts: eight failed papers rather than three; single-pass reconciliation with retained accepted ranges; optional local OCR rather than an unconditional no-OCR claim; v6 grounding and rejected-candidate discards; and frozen-catalogue search consumption. Their replacements are explained in the guides and recorded under DOC1–DOC12, with source locations. The old policies remain in the decision log.

## Commands and flags

The public registration is `pyproject.toml`'s `ara = "ara.runtime.cli:main"`; `ara/runtime/cli.py:28` defines the parser. I executed top-level help and help for `run`, `resume-construction`, `resume-search`, `extract`, `schema-preflight`, `codex-schema-preflight`, `plan-extraction`, `plan-construction`, `report`, `select`, `feedback` and `export`. Each exited zero.

The documentation inventory contains 49 distinct long option names across tracked Markdown. Of those, 48 appear in the appropriate captured ARA/helper/tool help; `--from-frozen` is explicitly described as absent. `fork-from-freeze` is likewise correctly marked absent at this base. I checked example arguments against the actual parser, including choices and required options. All 47 accepted command snippets passed. Six additional snippets are prose command names or partial references, such as “`ara extract`,” rather than advertised runnable examples; their missing required arguments are not documentation errors. ARA's option definitions and helper-script parsers agree with their help output.

Help checks also covered `tools/replay_extraction.py`, `tools/fetch_ocr_models.py`, `tools/ocr_audit.py`, `uv sync`, `uv run`, pytest, Python, `unshare`, shell built-ins, Git, Claude and `codex exec`. Historical provider flags in DECISIONS exist in the corresponding transport code and installed CLI help. `unshare -Urn` corresponds to the documented user-namespace, root-map and network-namespace switches. Git's `-h` convention returned 129 while printing usage. Documented negative-control scripts exist with executable main entrypoints; they were inspected, not run, because they intentionally mutate source and this review must not edit the branch. This check establishes command syntax and availability, not successful paid execution or live isolation.

Receipts: [command inventory](chi2-docs-review/commands.json) and [help directory](chi2-docs-review/help/). `commands.py` retains raw parser classification so command-name mentions can be distinguished from full examples.

## Decision history, links and privacy

A sequence comparison of old and new DECISIONS found additions plus exactly one one-line replacement: the former operator remote identifier became `<operator repo>` in B1 (`DECISIONS.md:118`). That is the authorized L1 exception to literal append-only history. All other original lines, including blank lines, retain their order; no decision or failed historical receipt was deleted. Git history itself was not rewritten.

I checked all 43 status annotations and their targets. They follow the relevant changes: D1 integration; D4/D9/D13 smoke bounds; B11 fallback routing; B12 and R1–R3 writing policy; GX12/GX22/GX26 evidence/construction changes; Mu range union and v6 grounding; M5 snapshot union; S2/S5 allocation; ordered search journals; subscription credential/retry changes; Codex schema policy; successive OCR repairs; and Round 12 catalogue consumption. [Supersession inventory](chi2-docs-review/supersessions.json).

The local-link check covers Markdown links, explicit anchors and heading fragments in all tracked Markdown, including unchanged guides and the canonical instruction symlink. All 232 references resolve. All ten external URLs returned HTTP 200; HTTP status does not verify a remote fragment or historical pricing claim. [Local links](chi2-docs-review/links.json), [external results](chi2-docs-review/external-links.json).

The leak check covered current tracked Markdown, including DECISIONS and the literature guide. The exact former L1 account identifier and full remote have no matches. Broader credential, email, identity-path and topic searches produced only public dependency/documentation URL candidates, which were reviewed. Manual reading found no real paper argument, premise or topic in that Markdown. [Audit](chi2-docs-review/audit.json), [candidate locations without sensitive values](chi2-docs-review/leak-candidates.json).

This is not a repository-wide anonymity certification: unchanged `literature/manifest.yaml` and `literature/references.bib` deliberately retain bibliographic metadata, and historical Git objects retain the old redaction target. The original brief/report already identify bibliography as outside the Markdown cleanup. Pattern searches also cannot prove semantic absence. No credential files or substantive runtime inputs were opened for this review.

## Coverage and evidence limits

This was a single-reviewer, read-only application of the CE code-review skill, using the lite path for a zero-executable-change diff and the caller's explicit no-delegation requirement. The root canonical `CLAUDE.md` supplied repository criteria; no scoped standards or declared Compound Packs were present. No reviewer agents, cross-model calls, mutation controls, installed-weight OCR, live provider work, or new full pytest run were used. Learnings, deployment readiness and agent-native capability were not separate review lenses.

The author's retained pytest log ends with **1,060 passed, 4 skipped in 887.99 seconds**. I inspected that receipt and independently verified that executable files, tests and dependencies are unchanged against the requested base. The test result remains author-run evidence, not a suite rerun by chi2 and not proof of the eventual combined xi/docs revision. No Buckeye pnpm gate applies to this separate Python repository.

The current report completes all eight review checks and leaves the branch unchanged. The unresolved next step is F1: resolve documentation integration with xi and check the resulting committed head. No original-base documentation defect beyond that integration requirement was retained.

## Findings placement

| Finding | Section carrying the finding and action |
| --- | --- |
| F1: textual conflicts and corresponding xi documentation integration | Findings and required action; also reflected in Check results |

1 findings, 1 placed.

DONE chi2 verdict=fix-first blocking=1 code_changes=0 conflicts_with_xi=DECISIONS.md,README.md


## Re-review

**Verdict: merge. Zero blockers. F1 is resolved.** This verdict supersedes the initial review's `fix-first` result for the new revision only.

Reviewed `docs/deslop-organize` at **`5b512de4ef37264fe3ac3fa8bbfe2a19e48606b8`**, against requested main **`f89cd373eb3e3953bcd4ee4ad56e212ac005bcef`**, on 2026-10-27. I performed the re-review myself, without paid calls, delegation, edits to either branch, or publication. The previous review text is preserved above.

### Re-review scope and integration

`git diff --stat f89cd37 5b512de` reports **16 documentation paths, 2,044 insertions and 1,192 deletions**. All changed paths are Markdown or the AGENTS/CLAUDE canonical-file/symlink reversal. Python, tests, prompts, schemas, configuration and dependency files match `f89cd37` exactly. `git diff --check` passed, and the reviewed worktree remained clean. [Diff inventory](chi2-docs-review/rereview/diff-files.txt), [stat](chi2-docs-review/rereview/diff-stat.txt).

`git merge-base --is-ancestor f89cd37 5b512de` exited zero. In a fresh scratch clone checked out at the exact base SHA, `git -c core.hooksPath=/dev/null merge --ff-only 5b512de4ef37264fe3ac3fa8bbfe2a19e48606b8` exited zero, advanced HEAD to the reviewed SHA, and produced **no conflicts**. This was an executed fast-forward check, not an update of main. [Receipt](chi2-docs-review/rereview/fast-forward.json).

### Xi behavior checked against source

| Behavior | Current documentation | Source-backed result |
| --- | --- | --- |
| Catalogue-aware search | `docs/construction.md:144`; `docs/search.md:123` | Matches `search_alignment.py:20` and `calls.py:913`: optional frozen catalogue validation, explicit legacy-unavailable status, catalogue/commitment hashes in model inputs, exact frozen slot bindings and joint formalization. Corrupt present metadata refuses. |
| Triviality and contribution gates | `docs/search.md:123` | Matches `contribution.py:45`, `target_policy.py:42` and `calls.py:916`: both target polarities checked without premises and against each commitment; 1,000 ms checks, bounded 8,192-entry cache, alpha-aware identity, conservative unknown/timeout handling, and one shared vocabulary/contribution proposal correction. Remaining rejected candidates are excluded; fewer than ten, including zero, can survive. A second disconnected-vocabulary result alone does not exclude an otherwise accepted candidate. |
| Route labels and selection | `docs/search.md:160`; `README.md:51`; `DECISIONS.md:3369` | Matches `route_policy.py:7` and CLI selection: only `CLOSED-derived` is offered by default. It requires a reachable licensed inference, at least two distinct frozen supports and no zero/single-support entailment of the root. CQ supports count; repeated/alpha-equivalent formulas and assumptions do not inflate support. `CLOSED-single-support`, `CLOSED-contribution-unresolved`, `CLOSED-attributed-report` and non-closed statuses remain disclosed and require explicit selection. `CLOSED-trivial` is correctly retained only as superseded Round 13 history, not advertised as a current label. |
| Own-thesis classification | `docs/search.md:141`; `docs/providers.md:214` | Matches `calls.py:940`, `target_policy.py`, the `classify_target` prompt and schema: every candidate receives a separate same-provider request with target/vocabulary, without proposal history/rationale. Only `own_thesis` passes; attribution checks and `attributed_report`/`unclear` exclusions remain logged. A local manifest calculation confirms **16 cases including classify_target** for the full Codex configuration; this was not a live preflight. |
| Frozen forks | `docs/search.md:188`; `docs/construction.md:168`; `docs/accounting.md:81` | Matches `freeze_fork.py:25` and `cli.py:185`: verified chain/anchor, one freeze, matching bank and frozen artifacts, separate empty destination, exact prefix preservation, separate cache, inherited accounting and fresh targets/search without rebuilding T. Supported overrides and paid-call implications are stated. `run --from-frozen` remains explicitly unsupported. |
| Search resume | `docs/search.md:224` | Matches `search_resume.py:265`, `freeze_fork.py:16` and the CLI resume branch: recorded nonempty target/job inventory and verified artifacts/journals are required; completed jobs are restored; no fresh proposal replaces stored targets. Fork resumes use the latest recorded fork configuration. `--stop-before-dispatch` creates no provider but appends recovery receipts, as the guide states. |
| Reporting contribution receipts | `docs/reporting.md:90` | Matches `report.py:276` and `report_render.py:301`: event target/polarity/graph remain authoritative, `classification` remains available, and solver/support metadata stays nested under `contribution`. A negation-search route may have `contribution.polarity = target` without overwriting its event polarity. Reporting can perform bounded local classification checks without a provider or a new engine search. |

The guides retain the limits: these checks do not establish originality, faithful formalization, minimal larger support subsets, independent source papers, successful new synthesis, or live serving identity. Explicit route selection does not waive budget/provider/audit gates.

### Help and offline validation

All **13 ARA subcommands**, including `fork-from-freeze` and `resume-search`, returned help with exit zero. The fork help exposes exactly `--source-run`, `--run-dir`, `--provider`, `--codex-schema-preflight-log`, `--unknown-usage-policy`, `--human-minutes` and help; the guide accurately excludes fork config/model/profile/cap overrides. Resume help matches the documented recovery options. Across the docs, **49 command snippets parsed successfully**; six additional snippets are prose command-name/partial references rather than runnable examples. `--from-frozen` is the only documented long-option name absent from the collected help and is explicitly described as unsupported. Helper/tool help was also refreshed. [Command inventory](chi2-docs-review/rereview/commands.json), [fork help](chi2-docs-review/rereview/help/ara-fork-from-freeze.txt), [resume help](chi2-docs-review/rereview/help/ara-resume-search.txt), [schema-manifest check](chi2-docs-review/rereview/schema-manifest-check.json).

Executed focused offline verification at the reviewed head:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider   tests/runtime/test_search_alignment.py   tests/runtime/test_target_triviality.py   tests/runtime/test_contribution_gate.py   tests/runtime/test_freeze_fork.py   tests/runtime/test_report_contribution.py
```

**62 passed in 26.17 seconds**, exit zero. These tests exercise catalogue bindings, candidate rejection/classification, solver/support boundaries, native fork preservation/accounting, and the report polarity fix with placeholder/fake-provider inputs. [Test receipt](chi2-docs-review/rereview/pytest.txt). Resume behavior was checked against source and help; a separate resume test suite was not run. No full pytest rerun, mutation runner, installed-weight OCR, live schema gate or paid provider test was part of this re-review.

### Decision history, privacy and links

The decision-history comparison against `f89cd37` preserves all **3,137 original lines in order**, except the already-authorized one-line B1 identifier redaction. Xi's Round **12, 13, 14 and 15** sections retain their original bodies, including historical qualifications and verification receipts. Section comparisons remove only the newly inserted navigation anchors and status notes; no xi paragraph is rewritten or omitted. Round 13's former label and inference-only rule are explicitly marked superseded by Round 14, and the original missing-fork correction is clearly marked historical. [History audit](chi2-docs-review/rereview/audit.json), [xi section comparisons](chi2-docs-review/rereview/xi-decisions.json).

The refreshed scan and manual review found **no L1 operator identifier, credential-shaped value, email, non-generic personal home path, or substantive paper topic/content in the 19 tracked Markdown paths**. Broad candidates were public dependency/documentation URLs. As before, this check does not certify historical Git objects or the unchanged bibliographic YAML/BibTeX metadata as anonymous. No credentials or substantive run inputs were opened. [Candidate locations](chi2-docs-review/rereview/leak-candidates.json).

All **250 local Markdown path/anchor references resolve**, and all **ten external URLs returned HTTP 200**. External HTTP checks do not validate remote fragments or historical pricing claims. [Local link inventory](chi2-docs-review/rereview/links.json), [external results](chi2-docs-review/rereview/external-links.json).

### Re-review finding disposition

| Finding | Disposition and placement |
| --- | --- |
| F1: conflicting xi integration and stale operating guidance | **Resolved.** Re-review scope and integration records the successful fast-forward; Xi behavior checked against source records the corrected guides, historical-label treatment and preserved new behavior. |

No new findings. Zero unresolved blockers. **1 findings, 1 placed.** The retained finding is the resolved F1; the earlier verdict remains historical evidence for the old head.

DONE chi2 rereview verdict=merge blocking=0
