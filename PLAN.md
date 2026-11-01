# ARA status and remaining work

Reconciled for the 2026-11-01 integration cleanup. This is a capability map;
exact revision, test and review receipts belong to the delivery report.
[DECISIONS.md](DECISIONS.md) retains the original alpha plan decisions and later
changes. [SOURCE_MAP.md](SOURCE_MAP.md) owns the module inventory.

## Intent and implemented path

ARA separates versioned move forms (L), frozen commitments (T), and model-proposed
cuts (H). Runtime owns provider calls, validation, caching, budgets and logs.
The engine imports shared types/ports, checks bank shape and deduction entailment,
and searches without importing provider implementations.

| Area | Present at this base | Evidence entry point |
| --- | --- | --- |
| Shared contracts and bank | Immutable ASTs, constants/variables, canonical structural identity, scoped proofs and versioned licenses | `ara/types.py`, `ara/ports.py`, `ara/bank.py`; root tests |
| Engine | Both polarities, licensing/Z3, closed-route independence, bounded forward search, Tier 1 repair requests and Tier 2 conflicts | `ara/engine/search.py`; `tests/engine/` |
| CLI lifecycle | Construction/freeze, targets, search, human selection, writing/audits, verification and export | `ara/runtime/cli.py`, `ara/runtime/orchestration.py`; integration tests |
| Extraction | Rich v2 page-linked graphs, immutable ranges, accepted unions, disclosed failures, grounding/quarantine and verified reuse | `ara/runtime/extraction.py`, `ara/runtime/grounding.py`; extraction tests |
| Construction | Counted windows, shared symbols, disclosed support cuts, one freeze, structure correction and frozen catalogue | `ara/runtime/construction.py`, `ara/runtime/orchestration.py`; construction tests |
| Frozen-prefix forks | Verified prefix/artifact copy, separate cache, imported accounting and current target proposal/search | `ara/runtime/freeze_fork.py`, `ara/runtime/cli.py`; `test_freeze_fork.py` |
| Target/route contribution | Bounded semantic novelty, bound target definitions and isolated own-thesis/content judgments, 30-candidate pools, two corrections with retained survivors, nonstructural derived-only default selection | `ara/runtime/target_policy.py`, `ara/runtime/contribution.py`, `ara/runtime/route_policy.py`; target/contribution/report tests |
| Search recovery | Durable journals, ordered publication, zero-inference diagnostic pause and verified unfinished-job resume | `ara/runtime/search_resume.py`; recovery/publication tests |
| Proposed premises and OPEN papers | Pre-freeze H retains conditional status; separately, paper-owned OPEN admission has no inferred edges, formula or H authority | `ara/runtime/hypotheses.py`, `ara/runtime/proposal_admission.py`; H and proposal tests |
| Publication recovery | Verified sentence carry-over, bounded occurrence repairs, persistent adverse history and final audit | `ara/runtime/audit_carryover.py`, `ara/runtime/publication_inline.py`; publication and audit tests |
| Frozen search vocabulary | Catalogue loading, current-goal references, joint slot formalization and bounded proposal batches | `ara/runtime/search_alignment.py`, `ara/runtime/calls.py`; alignment tests |
| Providers | Anthropic API, mock, isolated Claude Code and Codex CLI; stage selection and preflight gates | `ara/runtime/cli.py`; provider/isolation tests |
| OCR | Optional two-tier local recovery with span preservation and confidence gates | `ara/runtime/ocr.py`, `ara/runtime/ocr_spans.py`; OCR tests |
| Accounting/reporting | Append-only receipts, measured/reserved/local/inherited totals, export and offline reports with sealed traces | `ara/runtime/logging.py`, `ara/runtime/report.py`; report/accounting tests |

The CLI and engine are implemented. Earlier statements that they were docstring
placeholders describe alpha's historical phase and no longer describe this tree.
The native command set is defined at `ara/runtime/cli.py:30`.

## Deferred integration and known gaps

| Gap | Required next work or limit |
| --- | --- |
| Shared-frozen scope | Native `fork-from-freeze` now reuses a verified freeze and proposes current targets. This is xi's prefix-fork contract, not adoption of every policy on the separate eta branch. `run --from-frozen` remains absent. No live synthesis or statistical independence is established by the offline fork tests. |
| Codex serving identity | `ara/runtime/codex_cli.py` marks identity unverified when CLI events omit it. A request pin does not prove which model served a call. Live evidence must establish any stronger claim. |
| Source extraction quality | Accepted ranges can remain thin, partial or have open obligations. Lexical grounding and page checks cannot establish semantic completeness, attribution truth or faithful paraphrase. Retain and inspect source-linked evidence. |
| OCR limits | Default tests use fakes. Installed-weight checks are opt-in. Span confidence is not calibrated correctness; exact typography, formulas, reading order and semantic completeness remain unproved. Optional dependencies and weights are required on diagnosed pages. |
| Formalization quality | Structural checks, symbol reuse and Z3 entailment do not prove faithful translation. A still-atomic batch may be accepted with `flat_after_one_correction`; inspect its receipt before interpreting failed closure. |
| Search bounds | Target gates may exclude all candidates. `CLOSED-derived` requires the contribution policy, but does not establish semantic novelty, minimality of larger support subsets or independence across papers. Search/forward results remain bounded; partial paired analysis is not evidence of no conflicts. |
| Provider routing | Provider switching is implemented for rich construction stages only (`ara/runtime/construction_stages.py`). Both subscription providers refuse extraction; Claude Code also refuses web retrieval, while Codex allows web-only `search_evidence`; a `search_evidence.provider` setting does not create an API adapter. Use the main API provider or Codex web search for verification. |
| Provider acceptance and budgets | Fake transports and schema preflights do not prove live pilot completion. Output allowances and reservations are assumptions, not forecasts; actual charges can exceed a reservation before STOP prevents later calls. No separate aggregate spend guard exists. |
| Integrity and privacy limits | Hash chains require retained anchors/origins and do not authenticate a completely rewritten history. Export redaction is literal; methodology retains the full record. See [accounting](docs/accounting.md). |
| Evidence scope | Historical smoke and known-case recordings prove only their recorded conditions. No fresh paid pilot, full-corpus quality, installed-weight OCR or live serving identity is claimed by this documentation change. |

## Verification and next integration checkpoint

Run `uv sync --locked` and `uv run pytest` from the repository root. The
[verification guide](docs/verification.md) owns negative-control commands and the
rules for distinguishing regression checks from product evidence. The current
full-suite result belongs in the external handoff with its exact revision.

Current delivery requires an exact-head review and executed tests for the integrated
contracts. Historical branch receipts retain their original scope; they do not
establish a full-suite or full-control pass on a later merge. The cleanup report
also records retained unapproved branches and archive tags. No live calls are
required by repository cleanup, and offline success is not a new campaign result.

Keep `cli.py` as the public registration point. Extend existing owner lifecycles
with their callers, packaging, data and tests accounted for; avoid parallel
construction, search or publication paths without an explicit responsibility.
