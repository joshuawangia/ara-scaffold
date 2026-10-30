> Historical handoff before the rebase onto f89cd37. Current results and superseding findings are in [omicron3-docs.md](omicron3-docs.md).

# Omicron3 documentation handoff

Completed on `docs/deslop-organize` at `c12409a2590415520ab4a8d1b474f11a57787d6f`, based on requested `main` revision `6511ff6`. Worktree: `/home/dev/ara-work/omicron3`. Three local commits; no push, delegation, paid calls or source-layout changes. Non-author review remains with the caller.

The README is now a short command/configuration entry point. Nine pages under `docs/` contain the index and eight concern guides. Decision history is indexed and annotated; the follow-up redacts one personal identifier while preserving its decision entry. The full offline suite passed **1,060 tests with 4 opt-in skips**.

## Commits

- `7af5985 docs: split operating guides from the README`
- `4c8aaf8 docs: map ownership and refresh implementation status`
- `c12409a docs: index decision history and link superseded policies`

## Before and after line counts

Counts are physical text lines. Symlinks are described by their target rather than counted as independent rule text. `docs_pages=9` includes the index and verification guide.

| File | Before | After |
| --- | ---: | ---: |
| `AGENTS.md` | 31 | symlink to CLAUDE.md (39 lines) |
| `CLAUDE.md` | symlink to AGENTS.md (31 lines) | 39 |
| `DECISIONS.md` | 3023 | 3353 |
| `PLAN.md` | 126 | 64 |
| `README.md` | 988 | 110 |
| `SOURCE_MAP.md` | 0 | 54 |
| `docs/README.md` | 0 | 35 |
| `docs/accounting.md` | 0 | 79 |
| `docs/construction.md` | 0 | 173 |
| `docs/extraction.md` | 0 | 286 |
| `docs/ocr.md` | 0 | 98 |
| `docs/providers.md` | 0 | 247 |
| `docs/reporting.md` | 0 | 88 |
| `docs/search.md` | 0 | 141 |
| `docs/verification.md` | 0 | 69 |
| `literature/README.md` | 21 | 23 |

## What moved where

| Original README area | Current home |
| --- | --- |
| Setup, smoke, commands, profiles | `README.md`; check policy and historical receipts in `docs/verification.md` |
| PDF intake, extraction profile/planner, failures, corrections, provenance and reuse | `docs/extraction.md`; added current grounding/salvage guidance |
| Rich working T, capacity, depth cuts, construction resume, stages and frozen vocabulary | `docs/construction.md` |
| Pilot search, concurrency, partial failure, route selection, feedback, writing and stopped-search resume | `docs/search.md` |
| API configuration/fallbacks, subscription isolation and local schemas | `docs/providers.md`; added Codex setup, serving-identity limit and actual provider-routing scope |
| Logs, artifact lifecycle, export/redaction, measured/reserved/inherited totals and CLI calibration | `docs/accounting.md` |
| Local OCR install, spans, confidence, offline audit and limitations | `docs/ocr.md` |
| Offline report format, linked receipts, accounting and sealed traces | `docs/reporting.md` |
| Root content rule | Canonical `CLAUDE.md`, with `AGENTS.md -> CLAUDE.md`; README routes to it |

`SOURCE_MAP.md` maps actual modules, entry points, test ownership and tools. `PLAN.md` replaces the obsolete scaffold plan with current implementation and named gaps. `docs/README.md` defines cascading context and one canonical owner per concern. The literature guide retains record counts, date range, metadata caveats and selection intent while removing topic-specific prose and the misleading bibliography-only extraction example.

Buckeye methodology was applied at Python-repository scale: canonical instructions and scoped navigation, source-backed correction of stale guidance, and separate claims for static checks, offline behavior, live evidence and unproved quality. The bobvi example was `45b554c83d`. No Buckeye pnpm/CI procedure was imported into ARA.

## Contradictions fixed with evidence

Twelve groups are recorded as DOC1–DOC12 in DECISIONS. Source citations refer to `6511ff6`; all cited executable files are unchanged at the delivered head. Older policy paragraphs remain historical, with links to their replacements.

| ID | Corrected claim | Current evidence at this base |
| --- | --- | --- |
| DOC1 | PLAN's engine/runtime placeholders are implemented. | `ara/runtime/cli.py:28`, `ara/runtime/orchestration.py:113`, `ara/engine/search.py:59`; D1 superseded the original integration gap. |
| DOC2 | The failed-paper allowance is eight, not three. A threshold-stopped batch publishes retained evidence and failed/not-attempted rosters before raising. | `config.yaml:88`, `ara/runtime/extraction.py:419`, `ara/runtime/extraction.py:447`, `ara/runtime/extraction.py:495`; Mu addendum supersedes GX31. |
| DOC3 | Reconciliation is one best-effort pass, not an obligation traversal that must resolve every gap. | `ara/runtime/reconciliation.py:8`; Mu addendum supersedes GX13/GX21 and the reconciliation portion of GX26. |
| DOC4 | Range/review failures can retain accepted evidence; not every extraction validation/context failure aborts the whole batch. Strict intake checks still refuse diagnosed unreadable/partial PDFs. | `ara/runtime/calls.py:867`, `ara/runtime/extraction.py:372`, `ara/runtime/extraction.py:419`. |
| DOC5 | pypdf itself has no OCR; native intake now defaults to optional local OCR. Text-only behavior requires `--ocr off`. | `ara/runtime/cli.py:61`, `ara/runtime/cli.py:350`; OCR1 and later span decisions supersede no-OCR guidance. |
| DOC6 | Corrections can explicitly discard rejected candidate items with reasons. Normalization also handles null inventories and structural/page/ID forms; accepted history stays immutable. | `ara/runtime/calls.py:152`, `ara/runtime/calls.py:70`; M1 and Mu round 2 replace the narrower Kappa correction description. |
| DOC7 | Construction may depth-cut a closure and disclose omitted support instead of always refusing the whole argument. | `ara/runtime/closure_budget.py:70`, `ara/runtime/construction.py:172`; S1/S2/S5 supersede the earlier full-closure capacity claim. |
| DOC8 | Both subscription providers are registered. Independent provider dispatch is limited to rich construction stages; model-only search/writing overrides do not create an API adapter. | `ara/runtime/cli.py:123`, `ara/runtime/construction_stages.py:5`; Omega supersedes the pre-registration README note. |
| DOC9 | Claude Code rereads credentials and passes the access token through the call environment; it no longer writes a temporary OAuth copy. Codex uses a read-only bind. | `ara/runtime/claude_code.py:246`, `ara/runtime/codex_cli.py:96`; Omega round 9 and O10/O11 replace the old copy policy. |
| DOC10 | Search consumes the frozen catalogue, uses joint slot formalization and permits one target-vocabulary correction; those are no longer future work or an unconditional single target call. | `ara/runtime/search_alignment.py:20`, `ara/runtime/calls.py:913`, `ara/runtime/calls.py:970`; Round 12 extends S8 persistence. |
| DOC11 | Inherited API charges remain visible and count for API admission; subscription token admission uses local usage. | `ara/runtime/budget.py:148`; Omega round 6 supersedes the blanket inherited-budget description. |
| DOC12 | A bibliography passed as ordinary text does not extract its PDFs or establish source evidence. Historical extracted inventories also need current grounding before entering T. | `ara/runtime/cli.py:374`, `ara/runtime/grounding.py:95`; Mu round 2 adds grounding eligibility. |

Before the authorized redaction, the history check verified all original 3,023 lines remained in order, including blank lines. The follow-up changes only the identifier in B1. Additions are an area index, stable anchors, supersession/status notes and the correction entry. Source-backed current guidance does not silently rewrite historical tests, costs, failures or model judgments.

## Verification

| Check | Executed result | Receipt |
| --- | --- | --- |
| Locked environment | `uv sync --locked` succeeded with Python 3.13.7; lockfile unchanged | Tool output; `pyproject.toml` and `uv.lock` unchanged |
| Full offline suite | `uv run pytest -q`: **1,060 passed, 4 skipped**, 887.99 seconds, exit 0 | [pytest log](omicron3-pytest.txt) |
| CLI commands and examples | All 12 registered commands returned help; 38 complete runnable examples parsed, covering 123 option occurrences | [help inventory](omicron3-help/summary.json), [doc check](omicron3-doc-check.txt) |
| Remaining option names | Current guide flags match ARA/helper help or uv help; `--from-frozen` is explicitly identified as unavailable | Helper help in `omicron3-help/` |
| Local links | 226 relative/anchor references resolved; no errors | [doc check](omicron3-doc-check.txt) |
| External references | All ten URLs returned HTTP 200. Three rejected HEAD with 403 but succeeded with GET; historical pricing/source claims were not re-evaluated | [HTTP results](omicron3-external-links.json) |
| History/scope | Original decision lines retained in order; diff contains only Markdown and symlink changes; no deleted tracked paths | [audit](omicron3-audit.json) and Git tree comparison |
| Whitespace/checkout | `git diff --check 6511ff6 HEAD` passed; worktree clean | Final Git checks |

The suite ran while prose was edited. All executable code, tests, prompts, schemas, configuration and dependency files are byte-identical to the requested base at the delivered head. No code change after testing requires another suite run.

**V1 — Evidence limit.** No paid provider calls, installed-weight OCR checks, fresh-clone live smoke or new production mutations were executed. The brief forbids editing Python/test files, so mutation runners were documented rather than run. Offline pytest is supporting regression evidence, not a new quality or live-isolation verdict. Non-author review is still pending.

## Hygiene and leak review

`.gitignore` already covers `cache/`, `runs/` and `*.egg-info/`, including `ara.egg-info/`. `git check-ignore` confirmed all three. A committed-tree inventory found **no tracked runtime/cache/egg-info artifacts, PDFs, bytecode or generated extraction/provenance outputs**. No tracked file was deleted. The two instruction paths remain present; only the canonical-file/symlink direction changed.

**L1 — Identity disclosure redacted.** The personal GitHub account/repository
identifier in DECISIONS B1 was replaced with `<operator repo>` under the explicit
follow-up instruction. The entry and its meaning remain; Git history is untouched.
The competition submission's current tracked Markdown has no remaining identified
operator disclosure or credential value. The new scan is scoped to current files,
not historical Git objects. See [redaction scan](omicron3-redact-scan.json).

**L2 — Topic-specific guide text removed.** The old `literature/README.md` heading, group prose and example run path exposed the substantive corpus topic. The guide now uses neutral input instructions and placeholder examples. Bibliographic manifest/BibTeX files remain unchanged; their metadata is outside the tracked-doc leak scan and should be reviewed separately before public distribution.

Credential-shaped pattern searches found **no credential values in tracked Markdown**. Remaining identity-pattern hits were public OCR project URLs or generic local checkout paths, not operator identities. Content-pattern hits in rules, template descriptions, the named bank reference and authorized software-engineering verification history were reviewed; no real paper argument/premise content was found in the reviewed docs. Pattern search cannot prove semantic absence. [Final candidate locations](omicron3-audit.json) omit matched values.

## Remaining product/documentation gaps

**G1 — Shared-frozen B3 is not integrated.** The requested base rejects `fork-from-freeze`; it also has no `run --from-frozen`. The separate eta report describes an older branch contract, not this main revision. README and PLAN explicitly mark the capability absent. Integrate and verify it before publishing a runnable command; copying a frozen artifact is not provenance import.

**G2 — Codex serving identity remains conditional.** When CLI events omit model identity, receipts say `unverified`. Request pins do not establish serving identity. Provider/schema help and offline tests do not close that gap; providers and PLAN disclose it.

**G3 — OCR quality remains bounded.** Default tests use fakes and skip the two installed-weight checks. Optional dependencies/weights are required for diagnosed pages. The guides retain confidence, formula, typography, reading-order and completeness limits. API/CLI routing limits, partial extraction and flat formalization are also explicitly documented under DOC3–DOC12 and PLAN.

**D13 — Prompt-tree historical wording remains.** `prompts/README.md:3` still says the runtime lane adds templates in the future. Prompt-tree files were kept untouched under the brief. It is not current implementation guidance; SOURCE_MAP and PLAN point to the existing runtime and templates. A later prompt-owner documentation edit can retire that wording.

## Proposed code-layout plan (not executed)

Wait until xi reporting work and any accepted eta integration are stable. Use the owning tests and public CLI behavior to define each move; do not combine it with semantic changes. Keep the current flat layout if a move has no demonstrated ownership benefit.

| Proposed unit | Candidate organization | Required compatibility/proof |
| --- | --- | --- |
| Extraction | Group intake/publication/reuse from `extraction.py` with reconciliation, grounding, salvage and snapshot-union helpers under `ara/runtime/extraction/` | Preserve a package facade for current imports; native extract/resume/salvage, source identity, provenance and rejection behavior must stay the same |
| Construction | Group construction, stage dispatch, structure checks, closure budgeting, resume and frozen-catalogue helpers under `ara/runtime/construction/` | Preserve one-freeze lifecycle, stored-plan compatibility, catalogue hashes, support-cut disclosure and resume refusal cases |
| Search orchestration | Group search jobs, ordered publication, resume, alignment and trace persistence under `ara/runtime/search/`; leave deterministic algorithms in `ara/engine/` | Preserve engine/runtime boundary, per-job accounting, completed-job reuse, replay, licensing and sealed trace formats |
| Providers | Keep protocol/stage resolution stable; group API, mock and subscription implementations plus projection/calibration helpers under `ara/runtime/transports/` | Preserve provider identity/cache keys, credential isolation, model receipts, schema gates, retry budgets and packaged calibration/model data |
| Reporting | After xi settles, group `report.py`, `report_files.py`, `report_render.py` and `report_traces.py` under `ara/runtime/reporting/` | Keep public `generate_report` compatibility until callers migrate; prove no source-run writes, verified trace consumption, linked evidence and size bounds |
| Shared effects/model coordination | Keep logging, budgets, cache, provenance and export shared; split `calls.py` only where existing validation, retry/accounting and stage-call responsibilities justify it | Avoid a second acceptance or accounting path; preserve durable response-before-validation ordering and independent schema/engine checks |

For each unit: enumerate imports, callers, package data, root-relative resource lookups and owning tests; make one mechanical move with temporary compatibility exports; run focused native tests and matching production-wire controls; remove compatibility exports only after all consumers migrate. Finish with locked installation, full pytest and CLI replay/exports from a clean checkout. Move tests only when their new owner is established and pytest discovery remains unchanged.

Do not introduce a `src/` layout, move the top-level bank/prompts/schemas, or relocate packaged data in the same change. Current `ROOT` calculations, CLI defaults, fixture paths and installed data would need an explicit resource-loading migration. These are proposed steps; no move or corresponding proof was performed here.

## Findings placement

| Finding | Deliverable section carrying it |
| --- | --- |
| DOC1 | Contradictions fixed with evidence, row DOC1 |
| DOC2 | Contradictions fixed with evidence, row DOC2 |
| DOC3 | Contradictions fixed with evidence, row DOC3 |
| DOC4 | Contradictions fixed with evidence, row DOC4 |
| DOC5 | Contradictions fixed with evidence, row DOC5 |
| DOC6 | Contradictions fixed with evidence, row DOC6 |
| DOC7 | Contradictions fixed with evidence, row DOC7 |
| DOC8 | Contradictions fixed with evidence, row DOC8 |
| DOC9 | Contradictions fixed with evidence, row DOC9 |
| DOC10 | Contradictions fixed with evidence, row DOC10 |
| DOC11 | Contradictions fixed with evidence, row DOC11 |
| DOC12 | Contradictions fixed with evidence, row DOC12 |
| G1: missing shared-frozen command | Remaining product/documentation gaps |
| G2: unverified Codex serving identity | Remaining product/documentation gaps |
| G3: OCR proof/quality limits | Remaining product/documentation gaps |
| L1: historical identity redacted in current text | Hygiene and leak review |
| L2: corpus-topic prose removed; bibliography unchanged | Hygiene and leak review |
| V1: offline-only evidence and pending non-author review | Verification |
| D13: untouched prompt-tree stale wording | Remaining product/documentation gaps |

19 findings, 19 placed.

## Anonymization follow-up

Committed `0ebff970bc3e80da5b1924286196729bcbe7b72e` locally after the initial three-commit documentation handoff.
Only one line in `DECISIONS.md` changed. The tracked-Markdown leak scan found zero
remaining operator identifiers or credential values. Broad remaining matches are
public OCR URLs, repository rules and the previously reviewed authorized references.
`git diff --check` passed and the worktree is clean. No push. Pytest was not repeated
for this prose-only redaction; the original full-suite result above is unchanged.

DONE omicron3 redact head=0ebff970bc3e80da5b1924286196729bcbe7b72e leaks=0
