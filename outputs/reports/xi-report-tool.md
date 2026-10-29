# xi: offline full-run report tool

Implemented, committed locally, and verified. Full pytest and the complete negative-control runner are green; all source hashes were restored and the worktree is clean.

## Delivery

- Checkout: `/home/dev/ara-work/xi`, branch `feat/run-report`, from requested base `0eb8592`.
- Head: `74aa4ca4bd998961333bd102667b47cd1eb8b8e6` — native report command, rendering, tests, controls and documentation.
- Separate logging patch: `132057fafa50fd5a4757c0823488690d614e97ca` — version-1 search state/alternative receipts and engine tests. It can be cherry-picked independently.
- No delegation, paid calls, source-run writes or push.

Run from this checkout:

```sh
uv run ara report --run-dir /path/to/run-p --run-dir /path/to/run-q --out runs/report-p
```

Output must be a fresh empty directory separate from all inputs. The command reads verified event snapshots and run artifacts, without constructing a provider or executing search. It writes self-contained `report.html`, a Markdown twin, `data.json`, complete per-run event/artifact JSON, and a DOT file for each recorded route/search tree. Inline CSS and optional embedded SVG require no external scripts or assets.

All eight requested sections are present: identity/configuration/models/lineage; extraction histories, current outcomes and exclusion roster; construction/freeze/source-kind counts; nested search trees; route support and available audit receipts; split accounting; every HUMAN event; original gaps/failure receipts. Full prompts, responses, source text and artifacts remain in generated ignored output, never committed fixtures.

The native extension belongs beside `export` in `ara/runtime/cli.py`. `report.py` verifies and projects receipts; `report_render.py` renders those projections. `engine/search.py` adds trace receipts through the existing EventSink without changing search decisions or returned routes. It records queued-state ancestry, graph/depth snapshots, proposed alternatives, rejected alternatives, visits, completions and search boundaries.

## Trace completeness — finding 1

The existing real search logs contain final route graphs but lack branch ancestry and unambiguous polarity/state context for discarded alternatives. They are **partial search traces**. The reporter preserves all final graphs and raw engine decisions, and explicitly refuses to reconstruct missing branches from reused node IDs.

The optional logging patch supplies that context for future runs. It does not repair historical logs and adds graph snapshots to log volume. An interrupted trace without an end receipt stays partial. Aggregate terminal engine decisions remain unassigned; explicit completion receipts identify terminal states.

A fresh native mock smoke exercised both polarities: four complete search traces, six queued states, four final routes and eight DOT exports. Tests also exercise rejected/duplicate proposals, caps, interrupted search, commitments, ancestry and completed graphs.

## Metadata and source limits — finding 2

Historical code revisions and model-written route summaries are not consistently recorded. The report leaves them unavailable and identifies the gaps; it never substitutes the reporter's revision or calls a model for a summary. Exact commitment-to-source links require matching recorded evidence IDs and citations; otherwise the citation stays verbatim and page/kind/source attribution is unknown. Multiple recorded copies of the same evidence do not incorrectly make matching source/kind counts ambiguous.

Audits lacking a route ID remain available as unassigned run-level receipts. They do not certify a selected route. All model IDs/versions, configuration and profiles that are actually logged remain inspectable.

## Real-run smoke evidence — finding 3

Final combined report:

- HTML: `/home/dev/ara-work/xi/runs/xi-report/report.html`
- Markdown: `/home/dev/ara-work/xi/runs/xi-report/report.md`
- Data: `/home/dev/ara-work/xi/runs/xi-report/data.json`
- Proof metadata: `/home/dev/ara-work/xi/runs/xi-smoke-proof.json`

Inputs were all five `/home/dev/ara-scaffold/runs/series-5/run-*` runs, `/home/dev/ara-scaffold/runs/full26-v4a2`, and `/home/dev/ara-work/kappa/runs/kappa-probe`. All seven rendered successfully on the committed reporter; the combined report contains 39 recorded final routes and 39 DOT exports. Snapshot tail hashes and event counts are in the proof JSON.

The supplied extraction inputs are stopped snapshots, not evidence that a new full 26-paper search finished. The full26 snapshot contains 1,077 events, 26 papers requested across lineage, 16 selected in its latest batch, six current outcomes and ten not-attempted papers. Earlier outcomes remain historical, and even a previously selected paper with no outcome remains in the exclusion roster. No search completion is claimed for extraction-only inputs.

Native mock smoke and report:

- Run: `/home/dev/ara-work/xi/runs/xi-native-smoke`
- Report: `/home/dev/ara-work/xi/runs/xi-report-native/report.html`

These are offline outputs. The mock's logged accounting values are not paid provider charges.

## Accounting — finding 4

The combined real-input snapshot reports USD **58.040395** in logged measured cost and USD **0.89791** in unknown-actual-usage reservations. These remain separate in totals, per-stage/paper/model groupings and time series. The explicitly named budget-accounted totals combine them only for cap accounting. Logged costs use configured pricing; this is not invoice verification. Time totals sum logged model-call wall times.

Identical inherited receipts are deduplicated across supplied runs. Each run also shows local versus inherited totals. Calls without a source ID remain unattributed. Pending dispatches and measured responses without a finalized MODEL receipt have separate inventories/totals; they are not silently converted into finalized charges.

## Rendering and proof limits — finding 5

`dot` is not installed locally, so this delivery has DOT-only graph exports. The report says so for each tree. Tests cover unavailable Graphviz, rendering failure, and SVG embedding with a simulated renderer; actual local Graphviz execution is not claimed.

The combined self-contained HTML is **98,656,623 bytes**, retaining full receipts including prompts and responses. It has 64 sections and 364 collapsible details. HTML parser checks found zero scripts and zero external dependencies. The native report also passed structural checks. Final artifacts were regenerated at the committed head and matched the structurally checked HTML hashes. No browser visual inspection is claimed.

## Verification semantics — finding 6

Every input chain is verified before output publication. Existing tail checkpoints must match; available imported origin receipts are checked transitively. Modified chains, truncated anchored logs and mismatched imports refuse reporting. The read-only path does not create or repair source locks/logs. Tests compare source files byte-for-byte before and after CLI reporting.

A missing tail checkpoint or unavailable origin is explicitly disclosed, not silently called fully verified. A chain without a checkpoint cannot prove absence of suffix truncation; rewriting both a chain and its checkpoint is outside this mechanism's authenticity guarantee. Run artifacts are separately labelled as unauthenticated and cannot override logged evidence.

## Executed checks

- Logging patch engine suite: **53 passed**.
- Final focused report/trace checks: **19 passed**.
- Full suite at `74aa4ca`, with `ARA_LIVE_TEST=0`: **534 passed, 2 paid-provider tests skipped**, in 279.93 seconds. Evidence: `runs/xi-pytest-final.txt`.
- Integration negative-control runner: **218/218 passed** (every mutation failed its targeted test, then passed after restoration), run sequentially after the full suite. This includes nine new report/trace controls. All 18 mutated source files match their pre-control hashes and the worktree is clean. Evidence: `runs/xi-negative-controls.txt`, `runs/delta-controls/results.json`, and `runs/xi-control-inputs.json`. Final verification receipt: `runs/xi-verification.json`.
- Real-input smoke renders and fresh native mock CLI smoke/report succeeded. Rendered artifacts and source content remain gitignored.
- Three exploratory full-suite attempts were interrupted for review fixes and are excluded from the pass tally. The definitive suite above ran on the committed revision. Regression checks cover historical exclusion retention, unfinalized response accounting, terminal decision context, and duplicate evidence projections.

## Finding placement audit

| Finding | Deliverable section |
| --- | --- |
| Legacy trace incompleteness, future-only patch and logging volume | Trace completeness |
| Missing revision/summary/source/audit associations | Metadata and source limits |
| Stopped extraction snapshots are not completed full-corpus search | Real-run smoke evidence |
| Reservations, deduplication and pricing/accounting limits | Accounting |
| DOT-only output, simulated SVG proof and report size/browser limit | Rendering and proof limits |
| Chain/origin/artifact trust and read-only guarantees | Verification semantics |

6 findings, 6 placed

DONE xi head=74aa4ca4bd998961333bd102667b47cd1eb8b8e6 tests=534/536 negctl=pass tree_trace=partial:legacy-state-ancestry logging_patch=132057fafa50fd5a4757c0823488690d614e97ca report=/home/dev/ara-work/reports/xi-report-tool.md

## Round 2 — work record

Starting from 74aa4ca on the same branch; no delegation, paid calls or push. Nu identified B1 repeated graph snapshots amplified by native EventLog prefix verification; B2 available immediate origins skipped when an ancestor is missing; B3 recursive state-history rendering; S1 incomplete semantic trace validation; S2 unclassified cost treated as measured.

Required change: native per-search append-only sidecars with interned formula/text references and state/node deltas, one completed graph per route in the trace, and one final chained path/count/hash receipt. Preserve existing engine results/decisions and native non-trace route consumers. Validate sidecar hashes before interpreting them; unclosed files remain unauthenticated partial evidence. Verify each available origin prefix and direct copy independently of missing ancestry; require explicit accounting classifications; render state links iteratively. Evidence still pending: Nu's five native cap-scale scenarios, differential N1/consumer checks, full pytest and controls sequentially. Targets: under 10% native wall-time increment and under 100 decimal MB of trace data for the 20-search pilot workload projection.

### Round 2 checkpoint — 37cb5a7

Implemented B1/B2/B3/S1/S2 and committed locally at 37cb5a7. The current focused proof is 43 passed (runs/xi-round2-targeted.txt); native CLI/replay also passed before the final validator hardening. No paid calls, delegation or push. Added seven mutation controls (225 total), all anchors checked exactly once, pre-mutation SHA-256 inventory at runs/xi-round2-control-before.json. Full pytest is running before controls; neither is yet claimed green. Five-scenario native benchmark is running at runs/xi-round2-benchmark, with results persisted per completed pair. First two pairs: 127 nodes, sidecars 359402/619942 bytes, overhead -3.819%/+0.664%, projected 20-search trace 7.206/12.4168 decimal MB. Remaining three pairs pending. Benchmark executes actual EventLog appends, unchanged full chain verification, and original-base SearchResult/goal/decision comparisons. Other offline checks run on separate CPU affinities on this shared 16-core host; timings are single paired samples, not isolated statistical estimates.

Next: finish full suite, run controls sequentially and verify file restoration, finish all five benchmark pairs, fresh native/real-input reports and named consumer checks, then append final findings/evidence and required DONE line. Existing route events/artifacts and analysis snapshots remain unchanged for compatibility; full graph once per route applies to the new tracing stream. Inline source review recorded at runs/xi-round2-review.md; independent review was not dispatched under the explicit no-delegation/no-model-call brief.

### Round 2 checkpoint — terminal interning

The first size preview found the padded three-alternative trace exceeded the target (6,845,170 bytes; 136.9034 MB for twenty, excluding seal), so those timing runs were terminated and superseded. Final encoding retains the entire completed graph topology but interns its proposition/proposal payloads. New preview: 2,212,419 sidecar bytes / 44.24838 MB for twenty padded searches; ternary 678,468 bytes / 13.56936 MB. Every decoded route matches the engine's returned graph, including all 167 alternatives in the padded case. Focused tests: 45 passed. Eight new controls total 226; the newest removes terminal interning and targets the cap-scale storage regression.

The earlier complete suite (558 passed, 2 skipped) predates terminal interning and is superseded by the final suite now running. Final native benchmark outputs use runs/xi-round2-final-bench-{small,binary,padded,ternary}; independent scenario pairs run on distinct CPUs, off then on within each pair. Old benchmark files are diagnostic only. No EventLog verification change. Full suite and mutation runner remain sequential. Final source hashes are in runs/xi-round2-final-control-before.json.

Real inputs regenerated read-only (all seven, 39 routes), methodology/provenance passed. Eta rejected the first cache-reused smoke for missing cache-origin receipts, then accepted a fresh-cache smoke (seven construction prefix records, four sealed traces). The format changed since those native reports, so regenerate final native reports before handoff. Latest commit and test/benchmark completion remain to be recorded in final evidence.

### Round 2 checkpoint — final revision 5603994

Final implementation head: 5603994 (full SHA to be recorded at delivery). Focused suite is 45 passed. Final full suite is running at this revision; controls must follow it. Final-native smoke and report completed, four validated traces and four routes; real-input regeneration retains all 39 routes and byte-identical inputs. Final methodology and provenance checks passed. Eta at 185a318 accepts the final fresh-cache native smoke with seven prefix records/four sealed traces; evidence runs/xi-round2-final-eta.txt. Outputs are runs/xi-round2-final-native-report, runs/xi-round2-final-real-report and runs/xi-round2-final-imported-report; proof metadata runs/xi-round2-final-smoke-proof.json.

All five final-format native timing scenarios are underway across four separate processes: small cases 0/1 complete (7.5658→7.0960 s; 7.0326→6.9685 s; 3.0327/3.2035 MB projected trace), binary alternative case 2, padded alternative case 3, and ternary case 4 pending. Each pair uses actual EventLog, base engine 0eb8592, and exact result/goals/decisions comparisons; final output names are xi-round2-final-bench-*. Stop only the older superseded runs (already terminated), never these final processes until their pairs complete. No source edits planned. Finish full suite, controls (226), native ternary full-report rendering, timing table, source restoration hashes, final placement audit and DONE line. Performance values remain single-pair shared-host measurements, not a universal bound or projected 20-search runtime.

## Round 2 — final delivery

B1, B2, B3, S1 and S2 are fixed and verified. This section supersedes earlier work checkpoints and draft measurements above. Revision: `56039948c34b104f15bab13b455fadcc050c9c2d`; local commits `37cb5a7` and `5603994`; no push, delegation, live provider or paid calls.

### B1 — bounded sidecar tracing

Native search writes one append-only JSONL sidecar per search, with node/state deltas and interned formula/text/proposal definitions. Every completed route records its full topology exactly once in the trace, referencing those payload definitions. The authenticated reader expands it to the original complete graph; the padded cap test checks all 167 returned routes for exact equality. Existing non-trace route events/artifacts and analysis contracts retain their payloads for native consumers. The once-per-route claim is for tracing, not global artifact persistence.

After flush/fsync, one SYSTEM event in the unchanged hash-chained writer seals path, line count and SHA-256. Interrupted sidecars receive no seal; reports expose partial metadata without interpreting their contents. Hash/count mismatch refuses publication. Missing sealed files remain explicit gaps. Copy search-traces with the log/checkpoint when relocating; imports can resolve the recorded source path.

All five native pairs completed. Worst observed increment: **1.786%**; largest projected twenty-search trace: **44.26658 decimal MB**. Both requested targets pass for these workloads.

| Scenario | Nodes | Routes | Baseline s | Traced s | Increment % | Sidecar bytes | Seal/checkpoint increment bytes | 20-search trace MB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| One binary alternative | 127 | 1 | 7.566 | 7.096 | -6.210 | 150729 | 906 | 3.03270 |
| One binary alternative; 1,000-byte padding | 127 | 1 | 7.033 | 6.968 | -0.912 | 159269 | 906 | 3.20350 |
| Three binary alternatives | 499 | 167 | 1545.223 | 1471.953 | -4.742 | 2169641 | 910 | 43.41102 |
| Three binary alternatives; 1,000-byte padding | 499 | 167 | 1535.062 | 1463.960 | -4.632 | 2212419 | 910 | 44.26658 |
| One ternary alternative | 499 | 1 | 162.252 | 165.150 | +1.786 | 678468 | 910 | 13.58756 |

Combined metrics and authenticated trace checks: `runs/xi-round2-final-benchmark.json`. Final evidence directory pattern: `runs/xi-round2-final-bench-*`. Each row uses depth 6/node cap 500 and actual EventLog appends for both base and traced searches. Sizes include sidecar plus incremental seal/checkpoint bytes; decimal MB for a projected twenty comparable searches. This excludes existing model/engine events, route artifacts, report copies and other run data. Independent pairs run on separate CPUs on this shared host; off then on within each pair. Negative pair differences are timing variation, not a claimed speedup. These are single paired samples, not confidence intervals, a universal workload bound, or measured twenty-search elapsed time. The original decision writer still verifies the entire prefix on each append; its absolute cost remains visible in the table.

### B2 — available origins remain authoritative

Each available immediate origin is read and pinned; copied-event equality and receipt digest are checked before walking ancestors. In the A→B→C regression with A missing, valid C reports only A's unavailable scope. A locally rechained C that changes B's cost from 2 to 102 is refused while B remains available. Missing ancestry cannot suppress contradictory direct evidence. Origin verification remains read-only.

### B3 — cap-scale full report

State history uses iterative, bounded collapsible blocks with explicit parent/child links. Native EventLog cap-scale report proof: 499 nodes, 500 states, one route, all 2,193 original decisions retained; complete trace, 14,320,644-byte HTML and one DOT export. Output: `runs/xi-round2-final-cap-report/report.html`; receipt: `runs/xi-round2-cap-report-proof.txt`. No recursion-limit change or omitted state.

### S1 — completeness requires semantic evidence

The reporter checks versions, root and state inventories, duplicate/orphan/cyclic state IDs, proof-node parent/depth and references, definition hashes, proposal references, terminal coverage, graph roots/children/cycles, declared route inventory, and terminal graphs against their state ancestry. Begin/end alone does not establish completeness. Invalid/unassigned receipts remain visible, with named partial-trace gaps. Shape-tolerant rendering retains malformed target/reason evidence without crashing; it does not present an invalid graph as validated ancestry.

### S2 — explicit accounting classifications

Only `accounting="actual"` enters measured totals. Missing/future markers retain their costs and tokens in an unclassified bucket and timeline, with an explicit gap. Known reservation receipts remain separate, and the explicitly labelled budget-accounted sum includes logged charges across all classifications. Unfinalized measured response receipts remain separate from finalized MODEL charges. Tests include incomplete receipts with missing and future accounting markers.

### N1 — search semantics and native consumers

Every completed benchmark pair compares exact SearchResult JSON, proposer goal order and original ENGINE decisions with base `0eb8592`. All five final pairs pass all three exact comparisons. Each resulting sidecar also passes the production report reader's hash and semantic validation, with node/route counts matching the benchmark result. Fresh native mock CLI/replay and final native report pass: four complete traces, six states, four routes. Methodology export differs only in record count and tail hash when seals are filtered out. Native provenance import verifies and retains all four seals; imported reports resolve complete traces. Eta's actual frozen-T verifier at `185a318a7fa5a46485a375ee1cb26244c2254403`, in eta's own environment, accepts the seven-record construction prefix. The first cache-reused smoke was correctly refused for missing cache-origin receipts; final evidence uses a fresh cache. The saved version-one native smoke also passes the final reader with all four traces complete (six states); receipt: `runs/xi-round2-legacy-proof.json`. This is scoped consumer compatibility, not a full eta+xi branch integration.

Final native outputs: `runs/xi-round2-final-native`, `runs/xi-round2-final-native-report`, `runs/xi-round2-final-imported-report`; consumer/eta evidence: `runs/xi-round2-final-smoke-proof.json`, `runs/xi-round2-final-eta.txt`.

### N2 — real-input reports and content boundaries

The final reporter regenerated all seven requested existing real-run inputs, retaining all 39 recorded routes and byte-identical inputs. Output: `runs/xi-round2-final-real-report/report.html`, its Markdown twin and data.json; source hashes/counts/tails are in `runs/xi-round2-final-smoke-proof.json`. Stopped extraction snapshots do not establish completed full-corpus searches. Legacy logs still disclose absent state ancestry. Real content and generated outputs stay under ignored runs directories; committed fixtures/tools use placeholder propositions. The CLI still relies on the operator to choose ignored output paths; it does not globally enforce that path convention.

### N3 — verification and limits

Final focused proof: 45 passed. Final full suite on `5603994`: **560 passed, 2 skipped**, 292.35 seconds, `ARA_LIVE_TEST=0 taskset -c 14 uv run --offline pytest -q`; transcript `runs/xi-round2-final-pytest.txt`. The two skips are paid-provider gates. The full mutation runner started only after this suite finished; **226/226 controls passed** (all targeted mutations failed and all restored runs passed). Pre-run hashes cover all 20 mutated production files in `runs/xi-round2-final-control-before.json`; all 20 hashes match after restoration, and the worktree is clean. Final controls ran with `ARA_LIVE_TEST=0 UV_OFFLINE=1 taskset -c 14 uv run --offline python tests/integration/negative_controls.py`. Transcript: `runs/xi-round2-final-controls.txt`; archived red/green transcripts and results: `runs/xi-round2-final-control-evidence/`; hash and reviewed failure receipts: `runs/xi-round2-final-control-proof.json`. The eight new controls fail on the intended observable boundaries: contradictory available origin accepted, unclassified cost measured, changed sidecar accepted, incomplete trace called complete, unresolved formula reference omitted, wrong line count accepted, terminal payload volume over 100 MB projected, and a missing 500th rendered state.

No paid replay, complete twenty-search native timing, browser visual inspection, actual Graphviz execution, invoice validation or full branch integration is claimed. Graphviz is absent locally: native reports retain DOT and disclose SVG unavailability; renderer success/failure paths have offline tests. Inline source review was performed; the multi-agent CE review was not dispatched under the explicit no-delegation/no-model-call brief. The earlier 558-test suite and superseded format timings do not verify this final revision. Consolidated final receipt: `runs/xi-round2-final-verification.json`. All five authenticated cap-scale traces are complete, all 20 mutated source files are restored, and the final worktree is clean. Whitespace validation passes. No push was performed.

### Round 2 finding placement audit

| Finding | Deliverable section |
| --- | --- |
| Trace cost, payload interning, performance scope and unchanged base-writer cost | B1 |
| Available direct origin versus missing ancestor verification | B2 |
| Deep state-history rendering and cap-scale full-report proof | B3 |
| Semantic completeness and malformed/unassigned receipt handling | S1 |
| Unclassified accounting and unfinalized usage boundaries | S2 |
| Differential search behavior and scoped consumer/cache-origin evidence | N1 |
| Read-only real reports, stopped snapshots and ignored-content constraint | N2 |
| Stable full suite/controls, source restoration and unexecuted proofs | N3 |

8 findings, 8 placed

DONE xi round2 head=56039948c34b104f15bab13b455fadcc050c9c2d tests=560/562 negctl=pass fixed=B1,B2,B3,S1,S2 trace_overhead=1.786% pilot_trace_mb=44.26658


## Round 3

### R1 — sealed trace consistency fixed before rebase

Local checkpoint: `773e262f64f7f51f1e0188020ca3f242675613b3` on `feat/run-report`, based on `56039948c34b104f15bab13b455fadcc050c9c2d`. The worktree is clean. Terminal inferences now compare the full decoded proposal with the selected alternative, including conclusion, premise slots/text, commitment IDs and scope IDs. Selected child edges must agree with recorded node parent/depth. Every recorded alternative must have exactly one matching admission or explicit prune; contradictory dual outcomes are partial too. Admission/prune node identity must match its proposal. No search or solver re-execution is used. Contradictory receipts remain intact in JSON and HTML with named partial-trace gaps.

### Executed verification and scope

Extended the existing native sealed-sidecar/report-generation regression with Nu's three R1 cases and an admitted-and-pruned case. Before the production fix, all four failed because the report marked the trace complete (`runs/xi-round3-r1-red.txt`). After the fix, the owning search-trace and report test files pass: **49 passed**, including the 500-state full report, padded cap-scale route preservation and clean native/imported traces (`runs/xi-round3-r1-focused.txt`). One initial assertion in the strengthened existing cycle case incorrectly required the diagnostic substring to start the gap; corrected that test assertion and reran both owning files successfully.

Three new production-wire controls disable full proposal comparison, selected child ancestry comparison, or alternative disposition coverage. Their actual red outputs show the corresponding trace incorrectly becoming complete; restored runs each pass all 13 semantic cases. **3/3 targeted controls pass**, and SHA-256 before/after proves exact restoration of `ara/runtime/report_traces.py`. Evidence: `runs/xi-round3-r1-controls.txt`, `runs/xi-round3-r1-control-proof.json`, and `runs/xi-round3-r1-control-evidence/`. The registry now contains 229 controls. Whitespace validation passes. Inline source review found no further R1 blocker; no delegated or model-based review, paid calls, push, new native timing benchmark, or full-suite/full-control verification is claimed at this checkpoint.

### Pending integration — explicit operator hold

The user directed R1 now and to wait for their message before rebasing. No rebase has occurred, and no mu base SHA has been selected. Next: on the operator's explicit signal and final mu SHA, rebase onto `fix/four-paper-acceptance` from `/home/dev/ara-work/mu`, preserve both native behaviours in any conflicts, check mutation anchors, then run full offline pytest and the entire control runner sequentially on the rebased head. Verify restoration and clean status, update this handoff, and only then emit the requested round-three DONE line. Round-two full-suite/control evidence does not establish a round-three integrated verdict.

### Round 3 checkpoint finding placement audit

| Finding | Deliverable section |
| --- | --- |
| R1 semantic contradictions, retained evidence and resulting partial status | R1 — sealed trace consistency fixed before rebase |
| Executed regressions, targeted mutations, restoration and proof limits | Executed verification and scope |
| Operator-held rebase and outstanding full integrated verification | Pending integration — explicit operator hold |

3 findings, 3 placed


### Round 3 integration in progress

The operator supplied mu's final `514bae3ade119ae03533a00a3b976a01086aa1cd` and authorized the rebase. `feat/run-report` is now `070efb7bc5ed83d7b5528a42813a57b388751eb2`. Backup ref: `backup/xi-round3-before-mu-514bae3` at `773e262f64f7f51f1e0188020ca3f242675613b3`. Rebase conflicts occurred only in DECISIONS.md and the negative-controls registry; both appended histories/control groups were retained. `calls.py` is byte-identical to mu; README and CLI merged additively. The range-diff records only context/whitespace changes to the replayed patches; R1's patch is unchanged. All 257 unique control definitions have exactly one production anchor, and all 237 mu controls are retained unchanged. No retargeting was needed for this mu+xi integration; eta is outside this rebase. Evidence: `runs/xi-round3-rebase-range-diff.txt`, `runs/xi-round3-rebase-anchor-audit.json`.

Full offline pytest is running on this head; the full control runner has not started. Before-control SHA-256 hashes cover 22 production files in `runs/xi-round3-control-before.json`. Next: inspect the suite result, repair any actual failures, then run all controls sequentially, verify restoration and finalize the handoff. This paragraph is an in-progress checkpoint, not final verification.


Integration verification update: full suite at `070efb7bc5ed83d7b5528a42813a57b388751eb2` completed with **603 passed, 2 paid-provider skips**, 338.65 seconds, exit 0 (`runs/xi-round3-final-pytest.txt`). Only after that process exited, the full 257-control runner started with `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline python tests/integration/negative_controls.py`; transcript `runs/xi-round3-final-controls.txt`. Source mutation/restoration is in progress; final status and hash comparison remain pending.


### Round 3 final — integrated result

This final section supersedes the pending-rebase and in-progress checkpoints above. `feat/run-report` is **`070efb7bc5ed83d7b5528a42813a57b388751eb2`**, rebased onto mu's exact final **`514bae3ade119ae03533a00a3b976a01086aa1cd`**. No push occurred. The worktree is clean, the base is an ancestor, and whitespace validation passes.

**R1 behaviour.** Terminal inferences must match the full selected proposal, selected child edges must agree with node parent/depth, and every alternative must have exactly one matching admission or explicit prune. All three review reproductions and the conflicting dual-disposition case remain partial, preserve original receipts and expose their named gaps in JSON/HTML. The R1 patch is unchanged by the rebase. The full suite retains clean native traces, imported traces, cap-scale route preservation and 500-state rendering coverage.

**Rebase preservation.** Resolved only DECISIONS.md and the negative-controls registry, retaining both histories and both control groups. Mu's `calls.py` is unchanged; README and CLI additions retain both behaviours. All **237 mu controls** survive unchanged, plus **20 xi controls**, for **257 unique controls**. Every mutation anchor occurs exactly once; no anchor retarget was required in this mu+xi tree. The anticipated `calls.py` helper move belongs to eta's separate integration and was not part of this rebase. Backup ref `backup/xi-round3-before-mu-514bae3` retains the original xi head. Evidence: `runs/xi-round3-rebase-range-diff.txt` and `runs/xi-round3-rebase-anchor-audit.json`.

**Verification and limits.** On the exact final head, `ARA_LIVE_TEST=0 uv run --offline pytest -q` passed **603 tests**, with **2 paid-provider skips**, in **338.65 s**. Only after pytest exited 0, `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline python tests/integration/negative_controls.py` passed **257/257** controls: all mutations caused the targeted tests to fail and all restored runs passed. All **22 production files** match their pre-run SHA-256 hashes. No source change followed these checks.

Read the actual new R1 red outputs: suppressing proposal identity or child ancestry allows `complete=True`; suppressing disposition coverage allows both dangling and admitted-and-pruned alternatives to be complete. Each restored semantic run passes all 13 cases. Also read mu's three latest controls: removing retention accepts smaller/conflicting/disjoint snapshots, removing legacy publication loses `open_gaps`, and removing methodology disclosure loses limitations; their restored runs pass. These controls establish the tested boundaries, not semantic fidelity of arbitrary source content.

Final transcripts: `runs/xi-round3-final-pytest.txt`, `runs/xi-round3-final-controls.txt`. Archived per-control red/green outputs and all results: `runs/xi-round3-final-control-evidence/`. Restoration and selected failure evidence: `runs/xi-round3-final-control-proof.json`. Consolidated machine-readable receipt: `runs/xi-round3-final-verification.json`.

No paid calls, delegation, push, eta merge, new real-corpus extraction/construction/search, performance rerun, browser inspection or external Graphviz execution was performed for this rebase. The passing suite/control result covers this exact mu+xi tree; it does not establish shared-frozen-T readiness or a full multi-branch release verdict. Earlier benchmark receipts remain historical evidence for their recorded revisions. Committed changes use placeholders; generated evidence remains under ignored `runs/`.

### Round 3 final finding placement audit

| Finding | Final deliverable section |
| --- | --- |
| R1 contradictions now remain partial with original evidence and named gaps | Round 3 final — R1 behaviour |
| Exact mu base, conflict resolutions, preserved behaviours/controls and eta scope | Round 3 final — Rebase preservation |
| Final-head sequential suite/controls, exact source restoration and proof limits | Round 3 final — Verification and limits |

3 findings, 3 placed

DONE xi round3 head=070efb7bc5ed83d7b5528a42813a57b388751eb2 base=514bae3ade119ae03533a00a3b976a01086aa1cd tests=603/605 negctl=pass fixed=R1


## Round 4

### Implementation checkpoint

Rebased `feat/run-report` onto requested main `1411e91c70a6537422dbfece6f6ed1301b90e748`; this was a fast-forward because main already contains xi round 3. Backup: `backup/xi-round4-before-main-1411e91`. Scope is bounded HTML with full linked evidence, event-body deduplication, bounded tree previews, real 27-directory rerender, browser proof if available, then sequential full suite/controls. No paid calls, delegation or push.

The new large-import and paper-budget regressions failed against the old renderer. Implementation now writes format-v2 manifests, shared hash-addressed events with original/imported-by references, per-run chain envelopes, per-paper histories/items, complete artifact copies, per-section JSON, and full trace/route JSON plus DOT. The overview reserves 12 MB, limits sections to at most 64 KB (lower for many runs), and links explicitly when truncated. Trees show first three levels and at most 60 nodes; full state history remains in files. Existing tests now follow manifest links; R1 semantic checks remain intact. Owning verification: 52 passed (`runs/xi-round4-final-focused.txt`). Six targeted new/retargeted controls are in progress. New tests and examples contain placeholders only.

Zeta's exact 27-input command is `/home/dev/ara-scaffold/runs/overnight6-control/report-command.json`; inputs were extracted to `runs/xi-round4-inputs.json`, all exist. Intended output `/home/dev/ara-scaffold/runs/overnight-report-v2/` does not yet exist. A real-render verification script is at `runs/xi-round4-render-real.py`; it checks source hashes before/after. Headless Chromium is available via `/home/dev/enrollment_hub/node_modules/playwright`. Next: finish targeted controls, commit implementation, render/audit real lineage, verify browser/links/files, run full pytest then complete controls on the final head, and replace this in-progress statement with final evidence.


### Round 4 first real render and layout repair

At `117b9df`, the native 27-run render produced 2,473,214-byte HTML in 344.21 seconds, with all 394 input files unchanged. It exported 6,643 unique original event bodies for 44,324 occurrences (37,681 imported references), 763 paper files and no trees: this lineage contains no completed search. The independent file audit matched every chain envelope/event identity, 313 artifact copy hashes, all 763 paper histories and every section file. Total output: 7,994 files, 1,052,031,350 bytes. Thus evidence files remain substantial, while the HTML is bounded. Chromium 143.0.7499.4 opened the complete page in 1.626 seconds, with all 2,317 links valid, 246 sections, no missing run anchors and no page errors.

Desktop screenshot inspection passed, but the mobile screenshot exposed 891px content width in a 390px viewport and repeated table headers reduced readability. Fixed at `3350ef1`: bounded eight-row table chunks, contained horizontal table scrolling, and a compact combined-accounting table. All 30 report/budget tests pass. The first artifact is preserved at `/home/dev/ara-scaffold/runs/overnight-report-v2-initial/`; first proof receipts are under `runs/xi-round4-initial-*`. The first full suite passed 649 with 2 skips, but is historical evidence for `117b9df`. Full pytest and the real render have restarted on final-layout head `3350ef1`; the full control runner has not begun. Next: verify new browser widths/files, then run all 298 controls after pytest/render finish, verify all 26 source hashes, and finalize.


### Round 4 final — readable overview

Final head **`3350ef1b41574566fe549d02cb5827fa591dc16f`**, based on requested main **`1411e91c70a6537422dbfece6f6ed1301b90e748`**, on `feat/run-report`. Worktree clean; no push. Final report: [report.html](/home/dev/ara-scaffold/runs/overnight-report-v2/report.html).

**HTML and navigation.** Main HTML is **2,453,319 bytes / 2.453319 decimal MB**, below the 15 MB ceiling, versus the previous 3,703,537,195-byte HTML. Run/paper tables, combined/per-run accounting, limits and search overviews remain in the main page. The working budget is 12 MB with at most 64 KB per section, reduced for large run counts. Oversized sections explicitly link to their complete files. Whole-section overflow still preserves all links in the root manifest. Table chunks have closed markup and mobile scrolling stays inside tables. The final native render took 351.87 seconds. Size limits do not apply to evidence files: the full output remains **7,994 files / 1,052,011,317 bytes**. Copy the entire directory to preserve linked evidence.

**Shared events and preserved data.** The same **27** real directories from Zeta's saved command were used. All **394 source files** match before/after hashes. Format-v2 `data.json` is a manifest; full evidence is split by run, paper and tree. `events/index.json` contains **6,643 unique canonical event bodies** covering **44,324 original chain occurrences**, with **37,681 imported run references**. Each entry records original/imported-by runs and occurrence sequence/chain hashes. Per-run envelopes plus `event_ref` bodies reconstruct the original verified logs exactly. Original chain hashes are retained separately from event identity hashes. Compact event projections link to shared originals instead of re-embedding them.

The independent final audit checked every original event identity and envelope, **313 artifact copy hashes**, **763 complete paper histories**, and every section file. Full paper outcome items, history and receipts remain available through the per-paper files; full event prompts/responses and binary/text artifacts remain in sibling files. Combined accounting computation was unchanged; it covers all supplied historical receipts, not only the latest overnight campaign.

**Tree scope.** Each recorded tree gets node/edge counts, maximum depth, outcome and a preview of the first three levels, capped at 60 nodes. Complete trace/route JSON and DOT remain linked. This real lineage has **zero completed trees/routes**, as Zeta reported; the final search section explicitly says none were recorded. No search was rerun or invented. Native placeholder tests prove all 500 states remain in the full trace file while the overview shows three states and discloses 497 omitted preview nodes. Existing R1 contradictory-trace regressions still mark traces partial and retain their receipts. SVG generation remains optional and linked, with failures disclosed; no real Graphviz execution is claimed in this tree-free lineage.

**Browser and file proof.** Headless Chromium **143.0.7499.4** opened the complete final page in **1.268 seconds**, with **246 sections**, all run anchors present, **2,314 valid links**, and zero page errors. Desktop content width is 1440/1440; mobile is 390/390, with horizontal scrolling contained inside tables. Screenshots were inspected at desktop and mobile widths. This is a complete-document load, unlike the earlier excerpt-only proof. The first iteration's mobile overflow and repeated table headers were fixed in `3350ef1`; its earlier output is retained separately under `overnight-report-v2-initial` and is not the final deliverable. Final screenshots: `runs/xi-round4-report-top.png`, `xi-round4-report-accounting.png`, `xi-round4-report-search.png`, `xi-round4-report-mobile.png`. Browser receipt: `runs/xi-round4-browser-proof.json`; data-file audit: `runs/xi-round4-file-audit.json`; real render/input preservation: `runs/xi-round4-real-proof.json` and `runs/xi-round4-source-before.json`.

**Final-head verification.** Full offline pytest: **649 passed, 2 skipped of 651**, **320.04 seconds**, exit 0. Only after pytest and real rendering exited, the complete mutation runner passed **298/298**: every targeted mutation failed and every restored run passed. All **26 production files** match their pre-run SHA-256 hashes, and no source changed after verification. The two skipped tests are opt-in paid-provider checks. Five new controls cover section budget, global budget, canonical event identity, bounded tree preview and full paper-file retention; the prior all-state control now proves the complete linked trace rather than requiring all states in HTML. Actual red outputs show a lost truncation disclosure, a 38,871-byte page exceeding its test's 25,000-byte budget, incorrect event identities, all 500 states entering a three-state preview, a lost paper outcome, or a missing 500th state. Restored tests pass. The three R1 controls also still fail on unsupported completeness claims and restore green.

Full transcripts: `runs/xi-round4-full-pytest.txt`, `runs/xi-round4-full-controls.txt`. Exact current-registry red/green transcripts and results are archived in `runs/xi-round4-final-control-evidence/` (597 files). Source restoration and reviewed failure excerpts: `runs/xi-round4-final-control-proof.json`. Consolidated final receipt: `runs/xi-round4-final-verification.json`. Whitespace and ancestry checks pass. No separate lint/typecheck command is configured. No paid calls, delegation, push, new real extraction/construction/search, semantic source audit or new performance benchmark was performed. These limits do not qualify the executed report-size, preservation, browser and offline-test proofs.

### Round 4 final finding placement audit

| Finding | Final deliverable section |
| --- | --- |
| Bounded readable HTML, explicit overflow links, format-v2 manifest and substantial sibling-file/copy requirement | HTML and navigation |
| Imported-event deduplication, exact envelope reconstruction, all source/artifact/item preservation and accounting scope | Shared events and preserved data |
| Full tree files versus bounded previews; no actual completed trees in this lineage; retained R1 validation | Tree scope |
| Complete Chromium render, link checks and resolved mobile layout defect | Browser and file proof |
| Final-head sequential pytest/controls, exact restoration and unexecuted-proof limits | Final-head verification |

5 findings, 5 placed

DONE xi round4 head=3350ef1b41574566fe549d02cb5827fa591dc16f tests=649/651 negctl=pass html_mb=2.453319 report=/home/dev/ara-scaffold/runs/overnight-report-v2/report.html


## Round 5

### Integration checkpoint

Read the round-five brief and Phi's independent review. Rebased `feat/run-report` from `3350ef1b41574566fe549d02cb5827fa591dc16f` onto requested main `e5e40cb99a5e827be8c054feb171d400346a700e`. Current head: `2d9aeb590df3b48958ad481dcfc424ada70e11d1`; backup ref: `backup/xi-round5-before-main-e5e40cb`. Resolved the two additive conflicts in DECISIONS.md and tests/integration/negative_controls.py by retaining both sections/control groups. All production and test files match Phi's reviewed combined tree `c5d04ee` byte-for-byte; only decision-log and registry placement/formatting differ. Control definitions match Phi exactly, with 305 unique controls and every anchor occurring once. The existing xi all-state control remains targeted at the full linked trace file. No production repair or anchor retargeting was needed.

Full offline pytest is running at this head. The full control runner has not started and will run only after pytest succeeds. Pre-control hashes cover all 27 production targets in `runs/xi-round5-control-before.json`. Integration/anchor audit: `runs/xi-round5-integration-audit.json`; replayed patch comparison: `runs/xi-round5-range-diff.txt`. Next: complete sequential suite/controls, inspect expected failures/restored passes, verify exact restoration/clean tree, then finalize. No paid calls, delegation, push, new real report render or live pilot continuation was performed for this integration step. Round-four report evidence remains tied to its original head.


Round-five verification update: `ARA_LIVE_TEST=0 uv run --offline pytest -q` exited 0 at `2d9aeb590df3b48958ad481dcfc424ada70e11d1`: **672 passed, 2 skipped**, 324.39 seconds. Transcript: `runs/xi-round5-pytest.txt`. After the pytest process exited, the full 305-control runner started with `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline python tests/integration/negative_controls.py`; transcript `runs/xi-round5-controls.txt`. Source restoration and final handoff remain pending.


### Round 5 final — integration preserved

Rebase complete at **`2d9aeb590df3b48958ad481dcfc424ada70e11d1`**, based on requested main **`e5e40cb99a5e827be8c054feb171d400346a700e`**. Both additive decision sections and both control groups are preserved. The only conflicts were DECISIONS.md and tests/integration/negative_controls.py. All production/test files match Phi's reviewed combined tree `c5d04ee347c8f24216b2aa1405e3df68d393f20a` byte-for-byte; differences are limited to decision-log and registry ordering/formatting. The 305 control definitions match Phi exactly, with unique names and one occurrence per mutation anchor. No production fix or new anchor retarget was needed. The old xi all-state control remains on the full linked trace file. Backup: `backup/xi-round5-before-main-e5e40cb`. Evidence: `runs/xi-round5-integration-audit.json`, `runs/xi-round5-range-diff.txt`.

### Round 5 final — sequential verification

On this exact head, full pytest exited 0 with **672 passed, 2 skipped of 674**, in **324.39 seconds**. After pytest exited, the full mutation runner exited 0 with **305/305 expected failures and 305/305 restored passes**. All **27 production targets** match their pre-control SHA-256 hashes exactly. The worktree is clean; whitespace and requested-base ancestry checks pass. No source changes followed verification. The two skips are opt-in paid-provider checks; no separate lint/typecheck command is configured.

Inspected actual failures/restored passes for all seven sigma additions and all five xi report-budget/evidence controls. Removing resume artifact/plan checks admits invalid state; disabling resume CLI wiring repeats the accepted batch; disabling the lock reaches the forbidden concurrent provider boundary. Provider scope/terminal-refusal and diagnostic mutations fail their corresponding behavioural expectations. Xi mutations lose overflow disclosure, exceed the bounded test page size, break event identity, expose all 500 states in the three-state preview, or lose the full paper outcome. Every restored target passes.

Transcripts: `runs/xi-round5-pytest.txt`, `runs/xi-round5-controls.txt`. All 610 red/green transcripts plus registry results are archived in `runs/xi-round5-control-evidence/`. Before hashes: `runs/xi-round5-control-before.json`; exact restoration and reviewed excerpts: `runs/xi-round5-control-proof.json`. Consolidated final receipt: `runs/xi-round5-final-verification.json`.

### Round 5 final — scope

This round verifies the integrated tree locally. No paid calls, delegation, push, new real-lineage render, real-pilot replay or live continuation occurred. Round-four report/browser evidence remains attached to `3350ef1` and its unchanged output; it is not represented as a new round-five execution. Phi's real stopped-pilot replay is the independent evidence described in Phi's report, not work rerun here. Construction recovery remains bounded by its existing verified-receipt and accounting contract; passing the integration checks does not claim a live pilot completion.

### Round 5 finding placement audit

| Finding | Final deliverable section |
| --- | --- |
| Both additive conflicts preserved; exact production/test and control-definition agreement with reviewed integration | Integration preserved |
| Exact-head sequential suite/controls, selected failure evidence, complete restoration and clean tree | Sequential verification |
| Local integration scope; prior real-report/replay evidence not rerun; no paid calls or push | Scope |

3 findings, 3 placed

DONE xi round5 head=2d9aeb590df3b48958ad481dcfc424ada70e11d1 base=e5e40cb tests=672/674 negctl=pass

## Round 6 — Concurrent search

Requested base: `0e0a7fcf8a167fa6a0973f92e322582c33d6e6e4`. Branch `feat/run-report`
in `/home/dev/ara-work/xi` fast-forwarded from round-five head; backup is
`backup/xi-round6-before-main-0e0a7fc`. Implementation head: `f61a10a`.
Native runtime now schedules 20 independent target/polarity searches with default
concurrency 4, separate engines and sidecars, stable result/license joins, and one
acknowledged event writer. ModelCalls uses request-local recovery, single-flight
cache access and locked in-flight reservations retained through durable receipts.
Run stops prevent new paid admission; queued search work cancels and active work
drains. Solver-only locking protects Z3's default context. Target proposal is
already one batch call, so it is unchanged. `providers.py` is untouched.

Executed targeted evidence: original writer and reservation tests failed before
implementation; corrected native equivalence fixture passes across original
sequential and two reordered parallel executions (20 sidecars, exact bytes,
routes, forward/Tier1/Tier2 findings, peak 1/4/4). Early equivalence fixture failures
were fixture errors and are not claimed as red-before-fix behavior evidence.
`runs/xi-round6-targeted-equivalence.txt`: 8 passed in 101.92s. Accounting and
construction consumers: 57 passed, 1 deselected in 48.69s, archived in
`runs/xi-round6-targeted-accounting.txt`. Further targeted writer/default-four,
invalid-config, run-stop and durable-receipt checks pass. Final full pytest is
running at `f61a10a`; full mutation runner must follow it sequentially. No paid
calls, delegation or push. Next: full pytest, controls, byte restoration audit,
final report with limits and finding placement.

### Round 6 implementation and equivalence boundary

Set top-level `search_concurrency` in the run configuration; its default is 4 and
positive integer validation rejects bools, zero, negative and nonintegral values.
One worker pool bounds individual searches, not target pairs. Each polarity has a
fresh engine with the original 0/1 trace serial; native conflict/forward analysis
joins licenses in positive/negative order. An independent fixture compares the
old per-target `analyse` path against two four-worker completion orders on ten
placeholder targets and their negations. It checks all 20 raw sidecars, routes,
full analysis dictionaries and peak concurrency. Every fixture analysis has
forward, Tier1 and Tier2 findings. Native default-four and dedicated-writer wiring
have a separate test with a four-worker rendezvous.

Search workers submit writes synchronously to one owned writer thread. The
existing full hash-chain/checkpoint verification remains active. Sidecars keep
independent streams and seal into that chain. Writer errors propagate; active
requests drain before shutdown, pending futures cancel, and original log bindings
restore. ModelCalls uses locked reservations for both tokens and cost, including
in-flight spend. Reservations remain held until durable measured receipts, then
reconcile to actual usage. Unknown spend retains the estimate, and recovery
adjusts only that request. Run STOP refuses new paid admission. Per-request locks
prevent duplicate same-key dispatch/cache publication. Z3 work alone is serialized
to protect its default context; model waits can overlap.

Target proposal was already one batch request, so no per-target proposal loop was
changed. The default remains ten target candidates; both polarities are searched.
EngineAPI test/custom adapters retain the sequential `analyse` contract.

### Round 6 expected wall time and limits

Twenty equal independent searches at concurrency four need about five waves
instead of twenty: up to **4x for the search portion**. If independent searches
consume 80% of baseline elapsed time, the ideal total speedup is
`1 / (0.2 + 0.8 / 4) = 2.5x`; at 90% it is about 3.08x. These are estimates,
not live measurements. Uneven search lengths, serialized solver work, full log
verification/fsync, provider limits and shared request cache keys reduce overlap.
Proposal/construction and post-search forward/conflict analysis remain serial.

Proven equivalence is conditional on fixed model responses and sufficient budget.
An engine seed cannot make live model generation deterministic. Near a cap,
concurrent reservations can refuse an admission that would fit after another
request finishes; request order on a stopped run can differ. The event stream's
timestamps/interleaving and UUID sidecar filenames differ by design; sidecar
contents and completed native results are the compared invariants. No paid pilot
or live speedup was run. No new real-run report render is claimed. `providers.py`
is unchanged from `0e0a7fc`, preserving omega's ownership.

### Round 6 verification checkpoint

At `f61a10a26ffaa786688a14700593c03fb06ab3da`,
`ARA_LIVE_TEST=0 uv run --offline pytest -q` exited 0: **697 passed, 2 skipped**
(699 collected), 432.98 seconds. Transcript: `runs/xi-round6-pytest.txt`.
After that process exited, the complete 323-control runner started with
`ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline python tests/integration/negative_controls.py`.
Transcript: `runs/xi-round6-controls.txt`; pre-control hashes:
`runs/xi-round6-control-before.json`. All 323 anchors were checked for unique
occurrence before launch. Final negative-control outcomes, exact restoration and
finding placement remain pending; no completion claim yet.

### Round 6 final verification and revision

**Complete at `f61a10a26ffaa786688a14700593c03fb06ab3da`**, based on requested
`0e0a7fcf8a167fa6a0973f92e322582c33d6e6e4`. The final result supersedes the
in-progress checkpoints above. The checkout is clean; no push was performed.

Full offline pytest exited 0: **697 passed, 2 skipped / 699 collected**, 432.98s.
The skips are the explicitly disabled paid-provider tests. Only after pytest
exited, the full control runner ran and exited 0: **323/323 mutations failed with
exit 1 and all 323 restored targets passed with exit 0**. All 28 mutation-target
source files match their pre-run SHA-256 hashes exactly. `providers.py` also
matches the requested base byte-for-byte. No paid calls or delegation occurred.

Reviewed the actual failures and restored passes for all nine new controls and
four retargeted accounting controls. Bypassing the writer produced four append
threads in the writer test and five through native orchestration. Disabling
reservations allowed the competing request to dispatch; disabling the lock let
both token- and cost-cap admissions pass. Changing the negative search serial
broke sidecar-byte equivalence; mispairing results broke route equivalence.
Overwriting global recovery totals lost the other request's eight tokens
(20 instead of 28). Early reservation release admitted a request before the
measured receipt was durable. Removing single flight dispatched four identical
calls instead of one. Each restored implementation passed. Existing retry,
extraction admission, per-stage pricing and measured-receipt failure controls also
failed at their intended behavioral assertions and passed after restoration.

Evidence in `/home/dev/ara-work/xi/`:

- `runs/xi-round6-pytest.txt` — complete suite transcript.
- `runs/xi-round6-controls.txt` — complete sequential control-run transcript.
- `runs/xi-round6-control-evidence/` — archived red/green receipts and registry results.
- `runs/xi-round6-control-before.json` — pre-mutation source hashes.
- `runs/xi-round6-final-verification.json` — head/base, counts, restoration hashes,
  clean-tree/provider-ownership checks and reviewed failure excerpts.

The delivered change has no remaining implementation or local-verification gap
within this brief. Live wall-time improvement remains an estimate, with the
fixed-response/sufficient-budget equivalence boundary stated above.

### Round 6 finding placement

| Action-changing finding | Deliverable section |
| --- | --- |
| Default-four configurable polarity jobs; proposal is already batched; custom adapters remain sequential | Round 6 implementation and equivalence boundary |
| Separate sealed sidecars, one acknowledged chain writer, solver-only serialization and failure draining | Round 6 implementation and equivalence boundary |
| Atomic in-flight accounting, request-isolated recovery, durable receipts, run stops and single flight | Round 6 implementation and equivalence boundary; Round 6 final verification and revision |
| Exact result/trace equivalence proof and its model-response, budget and event-order boundaries | Round 6 implementation and equivalence boundary; Round 6 expected wall time and limits |
| Ideal five-wave search effect, whole-run limits and absence of a live timing claim | Round 6 expected wall time and limits |
| Exact revision, sequential suite/control results, all-source restoration, unchanged provider ownership and no paid calls/delegation/push | Round 6 final verification and revision |

**6 findings, 6 placed.**

DONE xi round6 head=f61a10a26ffaa786688a14700593c03fb06ab3da tests=697/699 negctl=pass parallel_search=yes equivalence=proven

## Round 7 — F1 and integration (verification in progress)

Read Psi F1 and the committed integration resolutions. Reproduced the nondeterministic
receipt order with a forced reverse schedule, then fixed publication in `db9bfff`.
All worker events, including accounting and failures, remain durable in chained
per-job journals. Main-chain publication follows input-target/polarity order after
workers drain. Interrupted publication remains visibly incomplete and refuses
paid resume. Focused checks: 22 passed, 1 deselected; six publication/writer
controls all failed as intended and restored green. The existing twenty-search
equivalence test now also asserts receipt order.

Integrated sigma `2195a2d` in `1b5670f`, then mu `cdc9753` in `b35aa03`.
Reused committed Psi resolutions (`efacf00` and `f4a19b5`), including the
`_call_reserved` stage-dispatch control adaptation. Psi's scratch working tree
was already mid-Omega merge and was not edited. Backup:
`backup/xi-round7-before-integration` at the F1 fix.

Omega `0472749` is currently merging in `/home/dev/ara-work/xi`; its conflicts
are resolved locally but the merge is not yet committed. Both the original brief
and subsequent steering are active: check `/home/dev/ara-work/omega` for its new
review-fix commit and merge it when available. At last check, head was still
`0472749` with active uncommitted review fixes. No paid calls, delegation or push.

Integration uses one reservation ledger for API and CLI tokens, request-specific
USD treatment, stage-specific canaries and retry bounds, and durable receipts
before settlement. Added mixed-provider tests in both directions. Existing
provider/construction/search focused coverage passed (73 tests before the final
receipt-helper consolidation); subsequent focused mixed/accounting checks passed
23 tests. Selected integration mutation controls are running sequentially at
`runs/xi-round7-integration-controls.txt`. Full integrated pytest and full controls
have not run yet. Next: finish scoped controls, commit Omega merge, incorporate
Omega's review fix, retarget anchors, then run the full gates sequentially and
verify exact source restoration at the final head.

Round 7 checkpoint: initial Omega merge is committed as `81960a8` and the checkout
is clean. All 21 selected integration controls passed (each mutation exit 1,
restored exit 0). The original sequential versus two parallel twenty-search
comparison also passed, now including receipt publication order, in 85.73s.
Transcripts: `runs/xi-round7-integration-controls.txt` and
`runs/xi-round7-integrated-equivalence.txt`. All 360 current control anchors occur
exactly once. Omega's review-fix commit remains pending; its working tree is not
being edited. An interim full suite is running at `81960a8` in
`runs/xi-round7-interim-pytest.txt`; it is not the final-head gate if Omega changes.

Interim full-suite checkpoint: `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline
--locked pytest -q` exited 0 at `81960a8`: **763 passed, 2 skipped / 765**, 488.67s.
The checkout remains clean. Omega still has no commit after `0472749`; its
review-fix work is active and uncommitted. Waiting for that commit before the
final integrated-head pytest/control sequence. This interim pass does not claim
verification of Omega's pending fixes.

Round 7 final-gate checkpoint: Omega review fixes `1d54a534b6f099a21620509cfc69437993d2ea7c` are now integrated in merge `c5c2c3eb35d4f9b8ec1e84be42d67096e5b1c749`. Only DECISIONS.md conflicted; both sections were preserved. The 110 focused provider/construction tests passed in 77.54s, and all ten focused mutation controls failed as intended and restored green. Credential/cache guards, both construction retry sites, inference-only auth metadata, no-token config-auth environment, scoped canary/retry policy, API pricing, and Sigma stage dispatch were checked. All 366 current anchors occur exactly once. Final full pytest is running in `runs/xi-round7-pytest.txt`; the full controls must run afterward, sequentially. Input refs and pre-control source hashes are recorded in `runs/xi-round7-inputs.json` and `runs/xi-round7-control-before.json`. No paid calls, delegation or push by Xi.

Final-gate repair checkpoint: the first full suite at `c5c2c3e` exited 1 with 788 passed, 2 skipped, 1 failure. The twenty-search test's sleep-based scheduler produced identical completion orders despite changed delays; routes, analysis, trace bytes and receipt order still matched. Failure transcript: `runs/xi-round7-pytest-schedule-failure.txt`. Replaced the timing assumption with four-job start barriers and explicit completion gates, and assert the exact forward/reversed orders. No production code changed. Focused equivalence plus F1 checks passed 4/4 in 85.87s (`runs/xi-round7-schedule-targeted.txt`). Committed as `76fa0b5fb7b9b9ff173239d5610073afed87bae4`; final full pytest restarted at that clean head, followed by full controls only after it passes.

Final pytest checkpoint at `76fa0b5`: **789 passed, 2 skipped / 791**, exit 0 in 437.41s. The skips are the opt-in live-provider tests. Only after pytest completed, the full 366-control runner started (`runs/xi-round7-controls.txt`). Source remained clean before mutation. Final control/restoration audit remains pending.

### Round 7 final result and integrated revision

**Complete at `76fa0b5fb7b9b9ff173239d5610073afed87bae4` on `feat/run-report`.**
This final section supersedes the in-progress checkpoints above. The checkout is
clean. Ancestry checks confirm sigma `2195a2dc15e4b636a8f168a9fc7b6dc822335c1e`,
mu `cdc9753f75e1906fa753bb7af3f410184f453d04`, and omega's fixed head
`1d54a534b6f099a21620509cfc69437993d2ea7c` are all included.

Merge order was sigma (`1b5670f`), mu (`b35aa03`), initial omega `0472749`
(`81960a8`), then omega's review fixes (`c5c2c3e`). The fixed omega head was
checked again after the final gates. Psi's committed sigma/mu resolutions were
reused, including the `_call_reserved` stage-dispatch mutation adaptation.
The omega follow-up had only a DECISIONS.md conflict; both decision records were
preserved. Original source working trees were not edited. No push was performed.

### Round 7 F1 — Stable publication and interrupted-run accounting

F1 is fixed in `db9bfff`: native jobs retain durable, hash-chained per-job
journals, then publish all worker events into the main chain in input-target
order, positive then negative. This includes model receipts, engine decisions,
trace seals, results and failures. Main-chain publication binds journal and
anchor hashes. Running jobs drain before publication even when a worker fails.
The acknowledged single writer remains in use.

The main chain records the ordered journal roster before dispatch. An interrupted
publication leaves a visible incomplete batch: methodology marks accounting
incomplete and Budget refuses reopening it. Durable receipts remain available in
the named journals. This is fail-closed recovery, not automatic replay; incomplete
main-chain totals must not be treated as the whole bill.

The four-job native regression forces forward and reverse schedules and compares
receipt order plus the logical event-stage sequence. The twenty-search regression
compares routes, analysis/conflicts, sidecar bytes and receipt order against the
original sequential adapter. Stable publication order does not mean byte-identical
event hashes across runs: timestamps, UUID paths, timing and provider/cache outcomes
can differ. Equivalence remains scoped to fixed responses and sufficient budgets.
Near-cap concurrent reservations can conservatively stop work that might fit
sequentially; aggregate in-flight headroom remains necessary.

### Round 7 provider and accounting integration

API and subscription calls share one atomic reservation ledger. The actual stage
provider determines billing policy: API stage calls retain priced USD admission
and measured charges even under a CLI default; CLI stages remain zero API USD
under an API default. Imported API costs remain visible. Measured receipts become
durable before settlement, request-local recovery and single flight remain intact,
and scoped CLI providers perform their uncached canary before generation.
Count-only planning does not run a canary. Transport retries use the selected
stage's settings. Three native fake-executable mixed-provider cases cover these
routing directions and the scoped retry/canary boundaries.

Omega `1d54a53` supplies F6/F7/F8 fixes: recursive decoded credential screening,
cache replay screening and eviction, ordinary and correction construction calls
through bounded transport retries, and config-link authentication. Config-link
uses a private temporary OAuth snapshot with inference-only CLI discovery metadata,
no refresh credential and no token in the child environment. It cleans up on
success/error/timeout and leaves the original login unchanged. Environment-only
login remains explicitly supported when the credential file is absent. Same-user
credential-file access and environment inspection remain permitted by the stated
threat model; no unconditional “never in ps” or root-isolation claim is made.
These policies are retained in README, DECISIONS and log-derived methodology.

### Round 7 verification and schedule-test repair

The first final-suite attempt exposed a test scheduling assumption: different
sleep delays happened to yield the same completion order. Output, analysis,
sidecar and receipt comparisons passed; the distinct-schedule assertion failed.
The failed run is retained in `runs/xi-round7-pytest-schedule-failure.txt`
(788 passed, 2 skipped, 1 failed). Commit `76fa0b5` replaces sleeps with bounded
four-job start barriers and explicit completion gates, asserting exact forward
and reversed orders while retaining concurrent native search. The focused
schedule/F1 rerun passed 4/4. No production behavior was changed for this repair.

Executed on the final clean head, sequentially:

- `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked pytest -q`:
  **789 passed, 2 skipped / 791**, exit 0 in **437.41s**. Both skips are opt-in
  live-provider tests.
- Only after pytest completed, `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline
  --locked python tests/integration/negative_controls.py`:
  **366/366 mutations exited 1; all 366 restored targets exited 0**; runner exit 0.
- All **31 mutation-target source files** match their pre-run SHA-256 hashes.
  Every anchor occurred exactly once. Ancestry, branch, clean-tree and
  `git diff --check` checks passed.

Inspected the actual failures for F1, interrupted accounting, mixed-provider
billing/canaries/retries, measured receipts, stage pricing/routing, omega's guards,
and both twenty-search controls. Publication mutations fail on receipt order;
unpublished-resume/export mutations lose the required refusal/incomplete flag.
Stage dispatch fails on wrong provider/model, not a signature mismatch.
Equivalence mutations fail on trace bytes and result pairing on routes.
Decoded/cache credential mutations fail to reject; construction retry mutations
leak the transport exception. Auth mutations trigger the fake executable's
contract refusal. Every restored implementation passes.

Earlier focused evidence remains supporting evidence: 22 F1/writer tests,
six F1/writer controls, 21 initial integration controls, 110 omega-follow-up
provider/construction tests, and ten follow-up controls. The full final-head
results above are the delivery gates.

Evidence under `/home/dev/ara-work/xi/`:

- `runs/xi-round7-pytest.txt` and `runs/xi-round7-controls.txt`: final transcripts.
- `runs/xi-round7-control-evidence/`: all 732 red/green outputs and registry results.
- `runs/xi-round7-inputs.json`, `runs/xi-round7-control-before.json`, and
  `runs/xi-round7-final-verification.json`: exact revisions, counts, restoration
  hashes, ancestry/clean-tree checks and reviewed failure excerpts.
- `runs/xi-round7-return.json`: local implementation/verification handoff receipt.

### Round 7 evidence limits

Xi made no paid calls, delegated no work and performed no push. All provider
subprocess tests use disposable fake binaries and synthetic credentials. Omega's
separately reported live canary is not a live check executed by Xi. This round does
not establish live speedup, full-pilot/full-corpus completion, broad literature
coverage, live load/rate-limit behavior, or expired-login refresh. Mu's byte-bound
verification receipts are integrated and tested, but its real-lineage timing
benchmark was not rerun here; the existing local-chain/anchor trust boundary and
non-atomic snapshot limits remain. The subscription route remains tool-free and
requires an explicitly retrieval-capable route for external evidence acquisition.
No implementation or local-verification task in the Round 7 brief remains open.

### Round 7 finding placement

| Action-changing finding | Deliverable section |
| --- | --- |
| Stable event publication order, changed-schedule proof and byte/equivalence boundary | Round 7 F1 — Stable publication and interrupted-run accounting |
| Durable worker evidence, failure draining and incomplete-publication refusal | Round 7 F1 — Stable publication and interrupted-run accounting |
| Exact integrated revisions, merge order and preserved Psi resolutions | Round 7 final result and integrated revision |
| Shared reservations, stage-specific billing, durable settlement and scoped canaries/retries | Round 7 provider and accounting integration |
| Omega F6/F7/F8 safeguards and explicit authentication threat model | Round 7 provider and accounting integration |
| Failed timing-based test and deterministic schedule repair | Round 7 verification and schedule-test repair |
| Final sequential gates, actual mutation failures and exact restoration | Round 7 verification and schedule-test repair |
| No paid calls/delegation/push; live, timing, retrieval and trust limits | Round 7 evidence limits; Round 7 final result and integrated revision |

**8 findings, 8 placed.**

DONE xi round7 head=76fa0b5fb7b9b9ff173239d5610073afed87bae4 base=2195a2d includes=mu,omega tests=789/791 negctl=pass fixed=psi-F1

## Round 8 — Continue independent searches (verification in progress)

Started from the requested main `852b21796191111c916be944648e3a42cac359ec` via fast-forward on `feat/run-report`, with a clean baseline. No paid calls, delegation or push. Six new native failure/CLI regressions failed before the implementation (`runs/xi-round8-red.txt`). The new scheduler lets job-local provider/validation refusals drain independently and retries each failed job once after the initial queue, in input order with a fresh engine. Global BudgetStop/context and infrastructure failures still cancel queued work; active work drains and publishes. Completed routes survive missing siblings and unavailable paired analysis. Attempt/status receipts and methodology disclose missing work. Select now accepts an explicit count-at-reservation policy while retaining default refusal for unknown usage.

Focused checks passed 18/18 in 18.61s. The original failure-accounting test now checks publication completion followed by the new stopped-phase disclosure, instead of requiring publication to be the last event. The broader parallel-search/equivalence check is running. Eight production-wire controls were added, and the result-pairing control was retargeted to the new analysis call. All 383 current mutation anchors occur exactly once. Full final-head pytest then full controls and restoration audit remain pending.

Round 8 gate checkpoint: implementation is committed at `801ef7d` on `feat/run-report`. Focused runtime/equivalence tests passed **34/34** in 104.75s; all **13/13** selected controls failed as intended and restored green. The final partial-route receipt wording check passed **9/9** in 12.43s. The controls' failures were inspected: isolation propagated the refusal, removing retry lost a recovered route, reversed requeue changed dispatch order, global-stop mutation failed to raise, dropping partial results lost a sibling route, missing disclosure lost status fields, and removing select policy prevented authorized reconciliation. Full pytest then all 383 controls are running sequentially via `runs/xi-round8-gates.py`; gate timestamps, input refs and pre-control hashes are retained in runs/. No final gate verdict yet.

Round 8 final pytest checkpoint: **808 passed, 2 skipped / 810**, exit 0 in 501.92s at `801ef7d`. Both skips are opt-in live-provider tests. Only after pytest exited, the driver started all 383 controls. Timestamps are in `runs/xi-round8-gate-times.json`; the final control/restoration audit is still pending.

### Round 8 final revision and behavior

**Complete at `801ef7d5ad961dfdbbdf353efa2f391b443fafd2` on `feat/run-report`,
based on requested main `852b21796191111c916be944648e3a42cac359ec`.** This section
supersedes the Round 8 in-progress checkpoints. The branch is clean; no push was
performed. The commit changes ten owned files, including the dedicated native
search scheduler and placeholder failure regressions.

A native search job that exhausts ModelCalls transport/validation retries no
longer cancels its siblings. Rejected and CountRequestRefused outcomes, plus
local-scope BudgetStop, are job-local. The initial queue drains; failed jobs then
receive exactly one additional attempt in input order. Successful jobs are not
rerun. Retry engines are fresh, retaining the original immutable inputs and
polarity serial without failed-attempt license state. The provider's own retry
policy remains inside each job attempt. Omega's separate transport-classification
work is not merged by this round; this change uses the boundary at the requested
base and leaves provider implementation files untouched.

Global BudgetStop—including native search context admission—and unexpected
infrastructure exceptions still halt queued jobs. Running requests drain.
Unknown API accounting that already requires a run-level stop remains such a
stop. Completed search routes are saved before the fatal error propagates;
those artifacts do not authorize generation past an applicable cap or accounting
refusal. Cancelled jobs are explicitly distinguished from failed/completed jobs.

### Round 8 stable publication and durable evidence

Every attempt remains in its job's durable journal. Started/failed/finished
receipts carry attempt numbers, and the retry receipt states the one-retry policy.
Publication remains in original target/polarity order, including failed attempts.
The final phase receipt lists all jobs, attempts and outcomes. Failed unsealed
trace prefixes remain on disk; successful retries have separately sealed trace
files with the original search identity. Nothing fabricates a successful trace
for failed work. Interrupted publication still discloses incomplete accounting
and refuses reopening through the existing guard.

The forced forward/reverse publication regression and the twenty-search
sequential-versus-parallel comparison both pass. The latter still compares
routes, conflict analysis, sidecar bytes and receipt order. Equivalence is scoped
to fixed responses and sufficient budgets. Timestamps/UUID paths/model behavior
are not claimed byte-identical, and conservative in-flight caps can stop work
that might fit sequentially.

### Round 8 partial routes, selection and accounting

A missing polarity is represented as an absent result, not an invented empty
SearchResult. Its completed sibling routes remain available. Paired analysis
runs only when both searches completed; an exhausted analysis-provider failure
also retains completed routes and logs unavailable analysis. Missing or failed
analysis is not evidence of no conflicts. Route receipts explicitly distinguish
completed search from unavailable paired analysis.

Both normal run and resume-construction use the native search path and record
`awaiting_selection` with partial-search metadata after job-local failures.
The console warns about failed jobs/incomplete analyses, methodology exports the
job statuses and failures, and the offline report retains the failure receipts.
An all-failed phase has zero selectable routes and a partial status; no route or
completed analysis is invented.

The native CLI regression runs through prepare/search, reaches awaiting_selection
with three routes despite a permanently failed negative search, and successfully
selects and composes a retained route. Unknown CLI usage is still accounted at
reservation and remains disclosed as incomplete measured accounting. A later
select refuses by default. The explicit option
`--unknown-usage-policy count-at-reservation` enables the existing reconciled
reservation policy and records that choice; it does not turn reservations into
measured spend or bypass context/token/USD admission or unresolved dispatches.

### Round 8 executed verification

Six initial regressions failed before the implementation, reproducing aborted
search, missing completed routes and inability to reach selection. Evidence:
`runs/xi-round8-red.txt`. Focused runtime/equivalence checks passed **34/34** in
104.75s; **13/13** selected controls failed and restored green. After the final
partial-route receipt wording change, all **9/9** failure/selection cases passed
in 12.43s. The old durable-failure regression now checks publication followed by
the new stopped-phase disclosure rather than assuming publication is the last
event. The result-pairing mutation was retargeted to the new analysis call.

Final gates ran sequentially at the exact committed head:

- `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked pytest -q`:
  **808 passed, 2 skipped / 810**, exit 0 in **501.92s**. The skips are opt-in
  live-provider tests.
- Only after pytest completed, the full offline locked control runner:
  **383/383 mutations exited 1, all 383 restored targets exited 0**, runner exit 0.
  Recorded timestamps prove pytest finished before controls started.
- All **34 mutation-target source files** match their pre-run SHA-256 hashes.
  Every mutation anchor occurred exactly once. Base ancestry, branch, clean-tree
  and `git diff --check` checks pass.

Inspected final failure receipts for all eight new controls and the publication,
writer, reservation, single-flight, recovery and equivalence controls. Removing
job isolation propagates the provider refusal; removing retry loses the recovered
route; reversing retry order changes dispatch order; downgrading global stops
fails to raise; dropping partial results loses a completed sibling route.
Removing disclosure loses required status fields, and removing the select policy
prevents explicitly authorized reconciliation. Existing publication mutations
fail on receipt order; pairing and serial mutations fail on routes/trace bytes.
All restored implementations pass.

Final evidence under `/home/dev/ara-work/xi/`:

- `runs/xi-round8-pytest.txt`, `runs/xi-round8-controls.txt`: final transcripts.
- `runs/xi-round8-control-evidence/`: all 766 mutation/restoration outputs and results.
- `runs/xi-round8-inputs.json`, `runs/xi-round8-gate-times.json`,
  `runs/xi-round8-control-before.json`, `runs/xi-round8-final-verification.json`:
  revision, chronological gate receipts, source hashes and reviewed failure excerpts.
- `runs/xi-round8-return.json`: local implementation/verification handoff receipt.

### Round 8 scope and limits

No paid calls, delegation or push occurred. This is offline native-runtime proof
with synthetic provider failures, not a rerun or repair of the existing live
pilot artifacts. No live completion, speedup, full-corpus result or future CLI
classification behavior is claimed. The existing custom EngineAPI adapter remains
sequential; independent polarity-job scheduling belongs to NativeEngine. No task
in the Round 8 brief remains open within this implementation and local-proof scope.

### Round 8 finding placement

| Action-changing finding | Deliverable section |
| --- | --- |
| Independent job failure, bounded end-of-queue retry and authoritative global stops | Round 8 final revision and behavior |
| Stable publication, attempt/failure evidence and equivalence boundaries | Round 8 stable publication and durable evidence |
| Retained sibling routes, unavailable analysis and all-failed outcome | Round 8 partial routes, selection and accounting |
| Native awaiting_selection, partial disclosure and explicit unknown-usage selection policy | Round 8 partial routes, selection and accounting |
| Exact head/base, sequential gates, actual mutation failures and full restoration | Round 8 final revision and behavior; Round 8 executed verification |
| No paid calls/delegation/push; live, adapter and separate provider-work limits | Round 8 scope and limits; Round 8 final revision and behavior |

**6 findings, 6 placed.**

DONE xi round8 head=801ef7d5ad961dfdbbdf353efa2f391b443fafd2 tests=808/810 negctl=pass continue_on_job_failure=yes partial_selection=yes

## Integration — Omega final head 6bd7679 (verification in progress)

Merged `6bd76796a1a7a68faf839b0f47d1ddd94bb2e925` from omega's `fix/subagent-final` into Xi `801ef7d`, resulting in `f9c5a8f` on `feat/run-report`. Conflicts were confined to DECISIONS.md and tests/integration/negative_controls.py; both sides were preserved. Omega's token-admission mutation-anchor adaptations survive, as does Xi's result-pairing adaptation. All 395 controls are unique and their anchors occur exactly once. README now distinguishes transport retry limits from the separate final search-job attempt.

The provider/calibration/mixed-provider/partial-search focused suite passed **128/128** in 47.48s. Full offline pytest then all controls are running sequentially on the merged head via `runs/xi-integrate-6bd7679-gates.py`. Timestamps, ancestry inputs and source hashes are captured. No paid calls, delegation or push. Final gates/restoration audit remain pending.

Integration full-suite checkpoint: `f9c5a8f` passed **854 tests, 2 skipped / 856**, exit 0 in 490.19s. Both skips are opt-in live-provider tests. The driver started all 395 controls only after pytest exited. Final control/restoration evidence remains pending; timing receipts are in `runs/xi-integrate-6bd7679-gate-times.json`.

### Integration final revision and conflict resolution

**Complete at `f9c5a8fe24cfb73cf5dc47a9d2743a503f9c9179` on `feat/run-report`.**
Ancestry checks confirm both Xi `801ef7d5ad961dfdbbdf353efa2f391b443fafd2` and
omega `6bd76796a1a7a68faf839b0f47d1ddd94bb2e925`, with common requested base
`852b21796191111c916be944648e3a42cac359ec`. This final section supersedes the
integration checkpoints and the earlier Round 8 statement that omega's separate
provider work had not yet been merged.

The two conflicts matched kappa2's report: DECISIONS.md and
`tests/integration/negative_controls.py`. Both sides were retained. Omega's
`cap_tokens(subscription)` anchor adaptations for retry/concurrent admission
survive, alongside Xi's adapted result-pairing control and all eight job-failure
controls. All **395 controls** have unique names and exactly one matching anchor.
No production conflict required replacement of either behavior. README received
one integration clarification separating transport retry limits from the final
search-job attempt. Omega's working tree was not edited. Xi is clean; no push.

### Integration behavior and boundaries

Omega's final provider changes are now included: like-for-like calibration,
separate fixed overhead, exclusion of obsolete/imported calibration observations,
local subscription token admission with imported history retained in total
accounting, classified bounded transport retries, one bounded retry for unknown
exit 1, and diagnostic suppression with allowlisted subtype/category metadata.
API admission keeps its history-inclusive policy, and pending/unknown-usage
reservations remain charged. Free-form diagnostic text is not retained.

Xi's independent job continuation, one final job retry, stable journal publication,
partial routes and explicit unknown-usage selection policy remain intact.
Transport retries occur within a job attempt; the final job attempt is separate.
Consequently, a failure that is non-retryable at transport level can still receive
Xi's one final job attempt after the initial queue drains. Both layers retain
accounting and normal admission. Global BudgetStop/context and unrecoverable
run-level stops remain authoritative. Partial analysis is disclosed rather than
represented as absence of conflicts.

### Integration executed verification

The focused provider/calibration/mixed-provider/partial-search suite passed
**128/128** in 47.48s before the merge commit. Existing native regressions were
used unchanged; the only integration-specific prose edit clarified retry scope.
No new test was needed for the additive conflict resolution itself; combined
behavior was verified by the focused and full suites and production-wire controls.

Final gates executed sequentially at the exact merged head:

- `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked pytest -q`:
  **854 passed, 2 skipped / 856**, exit 0 in **490.19s**. The skips are opt-in live
  provider tests.
- Only after pytest completed, the full offline locked control runner:
  **395/395 mutations exited 1; all 395 restored targets exited 0**, runner exit 0.
  Recorded timestamps establish that the runs did not overlap.
- All **34 mutation-target source files** match their pre-run SHA-256 hashes.
  Branch, both requested ancestors, clean-tree and `git diff --check` checks pass.

Inspected the actual failures for all twelve new omega controls and both retargeted
admission controls, plus Xi's job isolation/partial selection policy. Calibration
mutations compare unlike quantities, lose learned overhead or restore obsolete
factors. Admission mutations lose required refusals or incorrectly charge imported
history to the local subscription cap. Retry mutations lose recovery, retry known
deterministic failures, misclassify auth/request errors or exceed the unknown-exit
retry bound. Diagnostic mutations retain forbidden text/fields rather than fixed
metadata. Xi mutations lose failure isolation or required partial-selection
metadata/policy. Each restored implementation passes. Full equivalence and stable
publication controls also passed on the merged head.

Evidence under `/home/dev/ara-work/xi/`:

- `runs/xi-integrate-6bd7679-targeted.txt`: focused suite.
- `runs/xi-integrate-6bd7679-pytest.txt` and `runs/xi-integrate-6bd7679-controls.txt`:
  final complete transcripts.
- `runs/xi-integrate-6bd7679-control-evidence/`: all 790 mutation/restoration
  outputs and the complete results registry.
- `runs/xi-integrate-6bd7679-inputs.json`, `runs/xi-integrate-6bd7679-gate-times.json`,
  `runs/xi-integrate-6bd7679-control-before.json`, and
  `runs/xi-integrate-6bd7679-final-verification.json`: exact revisions, chronology,
  restoration hashes and failure excerpts.
- `runs/xi-integrate-6bd7679-return.json`: local handoff receipt.

### Integration limits and finding placement

No paid calls, delegation or push occurred. This is offline integration proof;
it does not claim a new live canary, repaired live-pilot artifacts, live completion,
measured speedup or full-corpus coverage. Earlier round-specific live/trust limits
remain as documented. No requested merge or local verification step remains open.

| Action-changing finding | Deliverable section |
| --- | --- |
| Exact integrated revision, both preserved conflict sides and valid adapted anchors | Integration final revision and conflict resolution |
| Combined retry layers, calibration/local-cap policy, safe diagnostics and retained partial search | Integration behavior and boundaries |
| Final sequential suite/controls, intended mutation failures and exact restoration | Integration executed verification |
| Clean local handoff, no paid calls/delegation/push and offline evidence limits | Integration final revision and conflict resolution; Integration limits and finding placement |

**4 findings, 4 placed.**

DONE xi integrate head=f9c5a8fe24cfb73cf5dc47a9d2743a503f9c9179 includes=6bd7679 tests=854/856 negctl=pass
