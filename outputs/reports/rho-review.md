# Rho — non-author review of Mu rounds 5 and 6

**Source verdict: merge; zero blocking source findings and one should-fix verification finding (S1).** The prerequisite-context fix, metadata projection, and import optimization are supported by code inspection and independent checks. Exact admission of the original recorded pilot command remains unverified; its offline replay refused because the available counter receipts describe a different audience. This is not a reproduced production capacity failure. No live pilot completion is claimed.

Reviewed `/home/dev/ara-work/mu`, branch `fix/four-paper-acceptance`, head `1d832b24805536b46e6974ca97842cffe0458e3a`, against base `9d4ec86595f7c46d5ba6d6f9747d86d50533246a`. No delegation, source-branch edits, push, or paid calls. All independent evidence is under `/home/dev/ara-work/reports/rho-evidence/`; mutations run only in `/home/dev/ara-work/rho-verification` at the same head.

## S1 — Match the pilot audience before relying on the recount

**Should fix, validation/reporting; not a source-merge blocker.** The saved pilot command `/home/dev/ara-scaffold/runs/overnight2-control/pilot-command.json` omits `--audience`. [cli.py](/home/dev/ara-work/mu/ara/runtime/cli.py:40) defaults it to `runtime audience`. The author's `runs/mu-round6/recount.py` instead calls `construct(calls, text, '')`. The author correctly discloses an empty audience, but those numbers are not an exact count of the recorded pilot invocation. Audience appears both in plan metadata and the request; it also changes the plan identity.

The first independent native CLI probe used the actual default, completed provenance import, then refused at its first exact-prompt lookup: no matching token-count receipt. I did not silently substitute a different prompt's count. A fresh free-counter attempt could not authenticate in this worker; no successful count or generation resulted. Evidence: `actual-pilot-first-attempt.json`, `offline-console.txt`, `offline_plan.py`, and `actual-recount-console.txt`.

Before relying on the reported capacity figures, either explicitly configure the intended pilot with `--audience ''`, or recount the actual default audience. The separate empty-audience probe below is explicitly a variant. The terminal `offline_pilot_plan=refused` conservatively denotes the original recorded invocation, not the passing variant or a demonstrated native batching defect.

## Round 5 — Native prerequisite context

Pi B1 is fixed. [snapshot_union.py](/home/dev/ara-work/mu/ara/runtime/snapshot_union.py:28) obtains context from construction's actual `evidence_dependencies`, including incoming `applies_to` for every target kind and inference-to-conclusion prerequisites. It qualifies IDs when prerequisite inventories differ, and propagates qualification through both native prerequisites and explicit references until stable. Shared endpoints therefore cannot reconnect separated contexts. Existing source bodies, original acceptance pins and explicit ID/reference mappings remain intact.

The five tracked publication regressions compare every eligible original root's closure with its mapped union closure, cover all four target kinds plus inference-to-conclusion presence, both input orders and a second resume. Independent `real_unions.py` additionally rebuilt all **six real overnight2 unions** in both orders, reproduced their full graphs and item provenance exactly, and compared **2,146 original-root prerequisite closures** without a mismatch. Evidence: `real-unions.json`. This is structural context preservation, not a semantic audit of the literature.

## Round 6 — Window metadata and T preservation

[evidence_window](/home/dev/ara-work/mu/ara/runtime/construction.py:87) is shared by initial counting, selection and formalization grouping. It preserves selected item dictionaries and limits provenance/quarantine to selected IDs. Explicit item-linked gaps are filtered to their IDs; native page-linked gaps must overlap a selected item's pages and, where present, its snapshot provenance. Full manifests, source diagnostics and unscoped gaps remain in the immutable artifact and receipts. Full original papers remain hashed into the plan.

The independent real-window audit checked all **5,296 eligible items across 46 windows**. Item bodies, IDs, citations and attribution were unchanged; there was no foreign item metadata; all applicable page/snapshot gaps and partial flags were retained. Seven real source records are partial; their flags appear in 24 paper-window records. There are 157 applicable gap occurrences across windows, not 157 distinct gaps. Evidence: `window-audit.json` and `window_audit.py`.

All 26 original artifact records lack title/author fields. The projection preserves those fields when supplied, including record fallback, and returns null when absent. This is an inherited bibliography gap, not metadata discarded by this patch. Source IDs and item attribution/citations remain available.

The deterministic T-copy contract is unchanged: [construction.py](/home/dev/ara-work/mu/ara/runtime/construction.py:312) copies exact attributed source text and citations and enforces the fixed closure inventory. This does not establish identical future model root choices or formulas after changing the prompt metadata. No real T was generated or frozen in this review.

## Count honesty and the 381-token margin

For the explicitly empty-audience variant, the verified saved counter receipts report **46 windows, 69,619 maximum governing input tokens, 2,357,296 construction-input tokens and 2,363,003 selection-input tokens**. The sum of per-window maxima is **2,393,603**. These are final-window sums, not all 274 partition probes/recounts. Every eligible item occurs in exactly one final initial window.

**381 tokens is planning slack, not a guarantee that a later formalization request fits.** [construction.py](/home/dev/ara-work/mu/ara/runtime/construction.py:213) plans with empty symbols, batch index zero and the full working allowance. Runtime selection adds the plan ID, content hash, actual index, current allowance and accumulated symbols. Formalization adds the chosen closure, prior supporting evidence and symbol allowance. Selection is rechecked against the 200,000-token model context including output allowance; the 70,000 bound is not an invariant for selection plus its growing catalogue.

Before formalization, native code recounts the actual closure envelope without symbols against the 70,000 bound, checks catalogue growth and working-T capacity, then recounts the complete request against context capacity. `_execute_once` recounts again before dispatch, including corrections and cache hits. An overlarge closure stops before formalization; it is not silently sliced. The existing closure-size, catalogue, retry and cached-context tests/controls exercise these safeguards.

Thus the margin is safe against unchecked dispatch overflow under the current guards. It is **not** proof of uninterrupted pilot completion, nor evidence that every possible selection will fit. No cap increase or guaranteed tolerance for future counter changes is justified. Exact recorded-command counts remain the S1 gap.

## Round 6 — Import integrity and speed

[provenance.py](/home/dev/ara-work/mu/ara/runtime/provenance.py:23) checks the active path before memo lookup, fully verifies each uncached chain, checks the pinned prefix hash/count, verifies all transitive imports, and only then stores verified events. The memo is a fresh dictionary per top-level verification/import operation: no global or persistent cache. Deduplication still compares exact original event identities and verifies copied events against the pinned source.

The independent shared-ancestor probe observed one read per operation, another read on the next operation, refusal after changing the ancestor, and refusal for a corrupt suffix beyond the pinned prefix. Evidence: `cache-probe.json`. Reuse within one operation represents its already-verified immutable checkpoint; subsequent calls do not inherit stale file verification.

[logging.py](/home/dev/ara-work/mu/ara/runtime/logging.py:70) verifies the destination under its exclusive lock, appends the marker and exact events with individual sequence/hash/anchor entries, then flushes and fsyncs both files. Operational errors propagate. Partial import counts and log/anchor mismatches remain invalid; there is no success fallback. Single-event writes use the same verified path.

I reran the author's paired benchmark against the same 128 evenly sampled original receipts: **4.2598 seconds before, 0.09027 seconds after, 47.19×**. Exact copied events and import verification passed for both. This supports the reported 45.4× sample result. It is not a controlled comparison of two complete 26-paper imports. Evidence: `import-benchmark/summary.json`, `benchmark_import.py`.

## Real artifact and native offline planning

Artifact: `/home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt`.

SHA-256: `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`.

The native CLI successfully verified/imported the real pinned transitive provenance: **4,436 destination entries before HUMAN/run-started events**, consisting of the import marker and deduplicated original receipts. Original receipts and timestamps remain exact; source files were not rewritten. The artifact has 26 source records, 5,659 retained items, 363 quarantined and 5,296 eligible.

The explicitly empty-audience native CLI variant **reached the complete `build_t_plan`**, before selection or any provider request. Its persisted plan is exactly equal to the author's, and all **274** native count requests match the saved prompt hashes, kinds, counts and item inventories in order. It covers all 5,296 eligible items exactly once across 46 initial windows. Evidence: `offline-plan.json`, `offline-counts.json`, `offline-summary.json`, `offline-pilot-empty-audience/events.jsonl` and `final-verification.json`.

A review-harness assertion initially failed **after the completed native plan** because it compared in-memory tuples with JSON arrays. I retained that failure transcript, corrected the comparison to JSON-normalized equality, and independently recovered the summary from the verified durable log. Both persisted plans are exactly equal; all 274 receipts match. No native planning rerun or source fix was needed. Evidence: `offline-empty-console.txt`, `offline_empty_audience.original.py`, `recover_offline_summary.py`, and `recovered-offline-console.txt`.

The successful variant took **743.37 seconds from its import marker to the completed plan**, despite making no network requests. The bulk-import optimization does not eliminate repeated whole-log verification on later single-event planning writes; the import sample speedup must not be read as a proportional end-to-end planning speedup.

Both offline probes block socket connections and prohibit generation. Counting is explicitly exact-prompt replay of the author's saved free-counter receipts after verifying their log chain and anchor; it is not a new provider measurement or independent authentication of historical counter responses. The native source import itself is rerun, not mocked. The only separate free-counter attempt failed authentication before any successful request.

No paid dispatch, new generated response, commitment freeze, search, route selection or semantic-quality proof occurred. Historical extraction limitations, lexical-grounding limits, and earlier shared-frozen/merged-tree concerns remain outside this narrow review.

## Executed tests and inspected mutations

Full pytest in the isolated exact-head checkout: **616 passed, 2 skipped / 618 collected**, exit 0, **272.98 seconds** reported by pytest. The two skips are opt-in live-provider tests. The full control runner started only after pytest exited successfully.

Full production-wire controls: **270/270 red under mutation and 270/270 restored green**, runner exit 0, **800.21 seconds**. Every tracked-file hash matches before and after both runs; the verification checkout is clean at the reviewed head. These controls completed after the full pytest run, never concurrently with it.

I directly read all five new mutation definitions and their independently rerun red/restored transcripts:

| Mutation | Production change under test | Observed failure |
|---|---|---|
| `snapshot_native_prerequisites` | Replace native prerequisites with outgoing references | All five closure cases fail; all five pass after restoration |
| `construction_window_metadata` | Restore full-paper metadata copying | Window contains forbidden/foreign fields |
| `construction_window_gap_scope` | Retain every gap | Window includes unrelated gaps |
| `receipt_bulk_import` | Emit copied events one at a time | 42 destination reads exceed the maximum of three |
| `bulk_append_verifies_chain` | Skip destination prefix verification | Tampered log is not refused by append |

Evidence: `verification.json`, `pytest.txt`, `controls.txt`, `controls-results.json`, `source-before.json`, `source-after.json`, and `inspected-controls/`. `git diff --check` passed. The Mu branch and real source artifact remain unchanged. There is no configured separate lint/typecheck command for this Python repository.

## Finding placement

| Finding | Deliverable placement |
|---|---|
| 1. Exact recorded pilot audience differs from counted variant; authentication blocks fresh confirmation; required follow-up | S1 — Match the pilot audience before relying on the recount |
| 2. Pi B1 fixed; native closure and real union retention verified | Round 5 — Native prerequisite context |
| 3. Window item/metadata preservation; inherited missing bibliography; deterministic versus model T limits | Round 6 — Window metadata and T preservation |
| 4. Honest variant counts; narrow planning margin is not a completed-pilot guarantee; dispatch remains guarded | Count honesty and the 381-token margin |
| 5. Fully verified operation-local memo and durable bulk append; reproduced sample speedup and benchmark limits | Round 6 — Import integrity and speed |
| 6. Real native import and scoped plan evidence; corrected postprocessing assertion; remaining planning cost; no paid/live/semantic proof | Real artifact and native offline planning |
| 7. Independent sequential tests, five inspected controls, restored-source evidence and check scope | Executed tests and inspected mutations |

7 findings, 7 placed.

DONE rho review verdict=merge blocking=0 should_fix=1 tests=616/618 negctl=pass offline_pilot_plan=refused
