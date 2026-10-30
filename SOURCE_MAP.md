# Repository source map

Start here for ownership and entry points, then read bodies, callers and owning
tests. This is navigation, not proof that a path is complete or works.
[CLAUDE.md](CLAUDE.md) owns rules; [docs/README.md](docs/README.md) routes guides.

## Contracts and engine

| Owner | Responsibility and entry points | Tests |
| --- | --- | --- |
| Shared contracts | `ara/types.py` immutable values/codecs; `ara/ports.py` synchronous protocols; `ara/formal.py` formula utilities | `tests/test_types.py`, `tests/test_schemas.py` |
| Bank | `bank/*.yaml` licenses; `ara/bank.py` strict loading | `tests/test_bank.py` |
| Engine | `ara/engine/search.py` Engine/search/analysis; `licensing.py` and `matching.py` rule/Z3 checks; `terminus.py` closure; `routes.py` support/independence; `forward.py` consequences; `conflicts.py` conflicts; `tracing.py` state events | `tests/engine/`; [engine API guide](ara/engine/README.md) |

The engine consumes shared contracts and ports. Runtime implements model/effect
ports; engine modules do not import provider implementations. Runtime validation
does not replace bank licensing or solver checks.

## Runtime

All paths below are under `ara/runtime/` unless stated otherwise.

| Owner | Entry points and supporting modules | Owning tests under `tests/runtime/` |
| --- | --- | --- |
| CLI/lifecycle | `cli.py:main` registered by `pyproject.toml`; `orchestration.py` prepare/freeze/search/compose; `freeze_fork.py` verified frozen-prefix reuse | `test_cli.py`, `test_pilot.py`, `test_freeze_fork.py`; `tests/integration/test_cli_e2e.py` drives subprocess CLI |
| Model boundary | `calls.py:ModelCalls`; `validation.py`, `render.py`, `cache.py`; root `prompts/` and `schemas/` | `test_calls.py`, `test_local_validation.py`, `test_boundaries.py`; root schema tests |
| Extraction | `extraction.py` intake/publication/reuse; `calls.py:extract_paper`; `extraction_budget.py`, `reconciliation.py`, `snapshot_union.py`, `salvage.py`, `grounding.py`, `windows.py` | `test_extraction*.py`, `test_range_union.py`, `test_paper_recovery.py`, `test_grounding.py`, `test_root_selection.py`, `test_context_request_fix.py` |
| Construction/planning | `construction.py`, `construction_anchors.py`, `construction_stages.py`, `construction_structure.py`, `closure_budget.py`, `planning.py`, `construction_resume.py`, `alignment_resume.py`, `frozen_catalogue.py`, `commitment_provenance.py`, `symbol_alignment.py` | `test_construction*.py`, `test_gap_construction.py`, `test_bounded_closure.py`, `test_evidence_windows.py`, `test_extraction_plan.py`, `test_resume_policy.py`, `test_frozen_catalogue.py`, `test_commitment_provenance.py`, `test_content_provenance.py`, `test_symbol_alignment.py`, `test_alignment_retrieval.py`, `test_alignment_resume.py` |
| Search runtime | `search_jobs.py`, `search_publication.py`, `search_resume.py`, `search_alignment.py`, `search_context.py`, `cq_context.py`, `gaps.py`, `external_gaps.py`, `semantic_conflicts.py`, `conflict_feedback.py`, `bridges.py`, `search_traces.py`; `target_policy.py`, `target_content.py`, `novelty.py`, `novelty_basis.py`, `synthesis.py`, `contribution.py`, `route_policy.py` target/selection checks; engine remains licensing authority | `test_parallel_search.py`, `test_search*.py`, `test_target_triviality.py`, `test_target_context.py`, `test_novelty_policy.py`, `test_semantic_novelty.py`, `test_per_paper_synthesis.py`, `test_consistent_novelty.py`, `test_nonlogical_contribution.py`, `test_search_guidance.py`, `test_search_context.py`, `test_cq_retrieval.py`, `test_gaps.py`, `test_external_gaps.py`, `test_semantic_conflicts.py`, `test_cross_paper.py`, `test_contribution_gate.py`, `test_republication.py`, `tests/engine/test_search_trace.py` |
| API/mock transport | `providers.py`, stage resolution and configured prices; `preflight.py` extraction grammar probes | `test_provider.py`, `test_provider_integration.py`, `test_fallbacks.py`, `test_schema_preflight.py` |
| Subscription transport | `claude_code.py`, `codex_cli.py`, `codex_window.py`; `claude_estimation.py` and packaged calibration data; `codex_schema.py`, `codex_preflight.py`, `codex_web.py` | `test_claude*.py`, `test_codex*.py`, `test_subagent_counting.py` |
| OCR | `ocr.py`, `ocr_spans.py`, `ocr_vl.py`; packaged model manifests | `test_ocr.py`, `test_ocr_spans.py`; installed-weight cases are opt-in |
| Integrity/accounting | `logging.py`, `provenance.py`, `verification.py`, `budget.py`, `export.py` | `test_incomplete.py`, `test_verification_receipts.py`, `test_verification_export.py`, budget/provider/extraction tests |
| Writing/verification | `orchestration.py:compose`; `writing.py` section planning/context/assembly; `essay_audit.py` sentence spans/typed failures/fresh consensus/targeted revision; `citations.py` retained-page verification, restoration and export coverage; writer/audit/verification methods in `calls.py`; `export.py` | `test_writer_validation.py`, `test_sectioned_writer.py`, `test_audit_labels.py`, `test_typed_audit.py`, `test_audit_consensus.py`, `test_audit_revision.py`, `test_resumed_draft_scan.py`, `test_essay_outline.py`, `test_known_verification.py`, `test_local_citations.py`, `test_delivery_alignment_citations.py` |
| Publication | `publication.py`, `publication_audit.py`, `publication_figures.py`, `publication_pdf.py`, `publication_references.py`, `publication_currency.py`; `polish`, `figures`, `render-pdf` CLI commands | `test_publication.py`, `test_publication_boundaries.py`, `test_publication_quality5.py` |
| Reports | `report.py:generate_report`; `report_files.py`, `report_render.py`, `report_traces.py` | `test_report.py`, `test_report_size.py`, `test_report_contribution.py` |

## Fixtures, tools and generated data

| Path | Purpose |
| --- | --- |
| `tests/fixtures/runtime/` | Placeholder smoke text and finite canned responses |
| `tests/fixtures/verification/` | Authorized software-engineering recordings; [capture/replay rules](tests/fixtures/verification/README.md) |
| `tests/runtime/fixture_support.py`, `rich_fixture.py` | Offline runtime and rich-source fixtures |
| `tests/integration/negative_controls.py` | Integration mutation runner; also invokes owning engine/runtime controls |
| `tests/engine/negative_controls.py`, `tests/runtime/*negative_controls.py` | Scoped production-wire mutations; run sequentially and restore |
| `tools/negative_controls.py`, `tools/ocr_negative_controls.py` | Aggregate and OCR controls |
| `tools/replay_extraction.py` | Offline historical response replay |
| `tools/fetch_ocr_models.py`, `tools/ocr_audit.py` | Weight provisioning and local OCR audit |
| `tools/calibrate_claude_code.py`, `tools/benchmark_search_traces.py` | Token-estimate calibration and trace benchmarking |
| `literature/` | Bibliographic metadata and ignored local PDFs; [input guidance](literature/README.md) |
| `runs/`, `cache/`, `*.egg-info/` | Ignored runtime/build outputs; never source authority |

`pyproject.toml` owns pytest discovery (`tests/`), package data and the CLI entry
point. `uv.lock` pins dependencies. No source-layout moves accompany this map.
