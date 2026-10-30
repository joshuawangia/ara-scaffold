# Omicron3 documentation handoff after rebase

Branch `docs/deslop-organize` is rebased onto `f89cd373eb3e3953bcd4ee4ad56e212ac005bcef` and committed at `5b512de4ef37264fe3ac3fa8bbfe2a19e48606b8`. Worktree: `/home/dev/ara-work/omicron3`. The checkout is clean. All changes against the requested base are Markdown or instruction-symlink changes; executable code, tests, prompts, schemas, configuration and dependencies match the base. No tracked paths were deleted. No push or delegation occurred.

Xi's new README guidance is integrated into the concern guides. All 114 added upstream DECISIONS lines remain in order, with round indexes and supersession links. The authorized L1 placeholder remains. The original four documentation commits were replayed, followed by `5b512de docs: integrate current target gates and frozen-fork guidance`.

## Reconciliation and findings

| ID | Current finding and documentation placement | Evidence at f89cd37 |
| --- | --- | --- |
| R1 | Ten requested targets can yield fewer accepted targets or none. Vocabulary and contribution share one correction. Solver checks test both polarities without premises and with each commitment; isolated `classify_target` accepts only `own_thesis`. See `docs/search.md`, target proposal and triviality. | `ara/runtime/calls.py:916`, `ara/runtime/target_policy.py:42`, `ara/runtime/contribution.py:45` |
| R2 | Only `CLOSED-derived` is offered by default and selected by smoke. Other displayed routes require explicit `--route`; that override still obeys budgets, provider gates, audits and verification. Support checks do not prove novelty, minimal larger support sets or independent papers. See `docs/search.md`, route classification and selection. | `ara/runtime/route_policy.py`, `ara/runtime/contribution.py`; `test_contribution_gate.py`, `test_target_triviality.py` |
| R3 | Native `fork-from-freeze` verifies the complete source chain/anchor and one freeze, copies its prefix and frozen artifacts, uses a separate cache and proposes current targets. A completed essay is unnecessary. Overrides are limited to registered provider/preflight/unknown-usage flags and human time; there is no fork config/model/profile/cap override. See `docs/search.md`, reuse a verified freeze, plus construction/accounting links. | `ara/runtime/freeze_fork.py:25`, `ara/runtime/cli.py:45`; `test_freeze_fork.py` |
| R4 | Resume retains recorded targets/jobs and dispatches unfinished work. A fork resumes with its effective configuration; resume does not refresh proposals under current preflight. `--stop-before-dispatch` appends recovery receipts. See `docs/search.md`, resume a stopped search. | `ara/runtime/search_resume.py:265`, `ara/runtime/freeze_fork.py:16` |
| R5 | Reports retain event target/polarity/graph and top-level classification; the solver receipt is nested under `contribution`. Event `negation` and contribution `target` polarities can correctly coexist. See `docs/reporting.md`, route classification and contribution receipts. | `ara/runtime/report.py:286`, `ara/runtime/report_render.py:301`; `test_report_contribution.py` |
| R6 | Codex preflight now includes `classify_target`. Historical 15-case proofs require a fresh 16-case receipt before live use. See `docs/providers.md`, Codex CLI. | `ara/runtime/codex_preflight.py`; current schema/help inventory |
| G1 | The previous missing-shared-freeze finding is superseded: `fork-from-freeze` exists. `run --from-frozen` remains unsupported. This establishes xi's prefix-fork contract, not adoption of all policies on eta's separate branch or successful live synthesis. See PLAN and construction/search guides. | Registered CLI help and `ara/runtime/freeze_fork.py` |
| G2 | Codex serving identity remains unverified when events omit it. Request pins and schema acceptance do not establish serving identity. See PLAN and providers. | `ara/runtime/codex_cli.py:230` |
| G3 | OCR quality, source fidelity and formalization remain bounded. Default OCR tests use fakes; installed-weight checks are opt-in. See PLAN, extraction/OCR/construction guides. | Owning source/tests; no new live-quality claim |
| D13 | `prompts/README.md` retains obsolete future-tense template wording. Prompt-tree files remain outside this docs edit scope. SOURCE_MAP and PLAN identify the existing implementation; a prompt-owner follow-up can correct that historical wording. | `prompts/README.md:3` |

The README remains the command/profile front door. Deep extraction guidance stays in `docs/extraction.md`; construction and frozen-vocabulary detail in `docs/construction.md`; search, targets, classification, forks and resume in `docs/search.md`; transport and schema proof in `docs/providers.md`; inherited charges in `docs/accounting.md`; OCR in `docs/ocr.md`; report receipts in `docs/reporting.md`; proof scope in `docs/verification.md`. `docs/README.md` routes these concerns. SOURCE_MAP includes the new fork/contribution modules and owning tests.

## Earlier documentation corrections retained

The [archived handoff](omicron3-docs-before-rebase.md#contradictions-fixed-with-evidence) preserves the original exact source citations at base `6511ff6`. These are historical correction receipts; current behavior is qualified above where xi extended it. Original decision paragraphs remain intact.

| ID | Retained correction and current guide |
| --- | --- |
| DOC1 | Engine/runtime are implemented; PLAN and SOURCE_MAP replace obsolete scaffold claims. |
| DOC2 | Failed-paper allowance is eight; stopped extraction retains evidence and rosters. Extraction guide. |
| DOC3 | Reconciliation is one best-effort pass and may leave unresolved gaps. Extraction guide. |
| DOC4 | Range/review failures can retain accepted evidence; strict intake checks still refuse diagnosed unreadable/partial PDFs. Extraction guide. |
| DOC5 | pypdf has no OCR itself; optional local OCR is the native default, with text-only `--ocr off`. OCR/extraction guides. |
| DOC6 | Corrections can discard rejected items with reasons and normalize supported forms; accepted history stays immutable. Extraction guide. |
| DOC7 | Construction may depth-cut support with disclosure. Construction guide. |
| DOC8 | Both subscription providers are registered; provider switching is limited to rich construction stages. Providers guide. |
| DOC9 | Claude Code passes a reread credential through the call environment; Codex uses a read-only bind. Providers guide. |
| DOC10 | Frozen catalogue and joint slot formalization are implemented; current shared correction and target gates extend the earlier vocabulary correction. Construction/search guides and R1. |
| DOC11 | Inherited API charges count for API admission; subscription token admission uses local usage. Accounting guide and R3. |
| DOC12 | Bibliography text does not extract PDFs or establish source evidence; historical inventories need current grounding. Extraction and literature guides. |

## Before and after line counts

Counts compare the requested base `f89cd37` with the delivered commit. There are nine docs pages including the index. The earlier base `6511ff6` had a 988-line README; xi's merged README had 1,026 lines.

| Path | Base | Delivered |
| --- | ---: | ---: |
| `AGENTS.md` | 31 | symlink to CLAUDE.md |
| `CLAUDE.md` | symlink to AGENTS.md | 39 |
| `DECISIONS.md` | 3137 | 3519 |
| `PLAN.md` | 126 | 66 |
| `README.md` | 1026 | 118 |
| `SOURCE_MAP.md` | 0 | 54 |
| `docs/README.md` | 0 | 35 |
| `docs/accounting.md` | 0 | 93 |
| `docs/construction.md` | 0 | 175 |
| `docs/extraction.md` | 0 | 286 |
| `docs/ocr.md` | 0 | 98 |
| `docs/providers.md` | 0 | 253 |
| `docs/reporting.md` | 0 | 107 |
| `docs/search.md` | 0 | 258 |
| `docs/verification.md` | 0 | 69 |
| `literature/README.md` | 21 | 23 |

## Verification

| Check | Result and receipt |
| --- | --- |
| Locked environment | `uv sync --locked` succeeded; lockfile unchanged. |
| Full offline pytest | `uv run pytest -q`: **1,108 passed, 4 skipped**, 900.18 seconds, exit 0; 1,112 collected. [Full log](omicron3-rebased-pytest.txt), [result](omicron3-rebased-result.json). Executable tree equals the base and was unchanged throughout the run. |
| Commands and flags | All 13 registered commands returned help. Parsed 42 complete runnable examples covering 136 option occurrences; helper and uv help checked. Absent fork `--model` and run `--from-frozen` explicitly confirmed. [Current inventory](omicron3-rebased-help/summary.json). |
| Local links | 246 local links/anchors resolved, zero errors. Same inventory. |
| Decision history | Both upstream and pre-rebase documentation histories remain ordered subsequences, allowing only the authorized upstream L1 identifier replacement. Round 13–15 entries indexed; historical missing-fork/selection statements link to current policy. |
| Scope and clean checkout | `git diff --check f89cd37 HEAD` passed. Base is an ancestor; docs-only diff, no deletions; `AGENTS.md -> CLAUDE.md` intact. [Scope receipt](omicron3-rebased-scope.json). |
| Leak scan | Zero identified leaks in current tracked Markdown. L1 and L2 scope below. [Current scan](omicron3-rebased-help/summary.json). |

**V1 — Evidence limit.** Pytest verifies offline regressions on the rebased executable tree. No paid calls, new production mutations, installed-weight OCR checks or new live synthesis/serving-identity validation were performed. Xi's historical proof receipts remain historical; this documentation rebase does not claim to have repeated them. External URLs were checked in the original handoff, not rerun for this rebase. Non-author review remains pending.

## Hygiene and anonymization

**L1 — Resolved in current text.** DECISIONS B1 uses `<operator repo>`. The decision and its meaning remain; no historical identity purge was performed. The scan checks the known identifier/account plus credential-shaped values, identity candidates and paper-content candidates across tracked Markdown. Remaining candidate locations are public OCR project URLs, content rules/templates, a named bank reference and authorized software-engineering verification history. No operator identifier, credential value or real paper argument/premise was identified. Pattern search cannot prove semantic absence; Git objects are outside this current-text scan.

**L2 — Topic-specific prose removed; bibliography scope unchanged.** The literature guide remains neutral and uses placeholders. Bibliographic manifest/BibTeX metadata is unchanged and outside the tracked-Markdown scan; review it separately before distributing those files. `.gitignore` still covers cache, runs and egg-info; the earlier artifact inventory found no tracked runtime/generated artifacts, and this rebase adds only docs paths. No tracked file was deleted.

## Proposed code-layout plan

The [original mechanical move plan](omicron3-docs-before-rebase.md#proposed-code-layout-plan-not-executed) remains a proposal, not executed work. It groups extraction, construction, search orchestration, transports and reporting only when their responsibilities justify a move; shared logging/budgets/cache/provenance stay shared. Preserve public imports with temporary facades, enumerate resource paths and consumers, and prove each unit with owning native tests and matching negative controls before full pytest and CLI replay. Do not combine a source-layout or resource-loading migration with semantic changes.

Now that xi's fork/contribution/report work is merged, include `freeze_fork.py`, `target_policy.py`, `contribution.py` and `route_policy.py` in any future ownership review. Preserve the single freeze, effective fork configuration, separate cache, imported accounting, target policy and nested report receipt contracts. No Python, test, prompt or schema move was made here.

## Findings placement

DOC1–DOC12 are placed in Earlier documentation corrections retained (12). R1–R6 and G1–G3 plus D13 are placed in Reconciliation and findings (10). V1 is placed in Verification (1). L1–L2 are placed in Hygiene and anonymization (2). The archived G1 absence claim is explicitly superseded by current G1.

25 findings, 25 placed.

DONE omicron3 rebased head=5b512de4ef37264fe3ac3fa8bbfe2a19e48606b8 base=f89cd37 leaks=0 tests=1108/1112
