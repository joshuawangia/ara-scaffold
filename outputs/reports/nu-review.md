# nu: independent review of xi

**Recommendation: logging fix-first; report tool fix-first.** Three BLOCKING findings and two SHOULD-FIX findings. No changes to xi's branch, no delegation, no live or paid provider calls, and no push.

Reviewed `/home/dev/ara-work/xi`, `feat/run-report`, head `74aa4ca4bd998961333bd102667b47cd1eb8b8e6`, against `0eb8592`. The separate logging commit is `132057fafa50fd5a4757c0823488690d614e97ca`. Read repository rules, PLAN, the original brief and delivery report, changed production code and owning tests, logging/provenance/export consumers, and eta's frozen-T verifier at `185a318a7fa5a46485a375ee1cb26244c2254403`.

## BLOCKING B1 — Full graph snapshots make pilot-scale logging operationally excessive

Location: [search.py:102](/home/dev/ara-work/xi/ara/engine/search.py:102) (every pushed state), line 116 (completed graph), interacting with [logging.py:59](/home/dev/ara-work/xi/ara/runtime/logging.py:59) (full-chain verification for every append).

Every inference and every blocked leaf writes the entire current graph again. Search depth bounds proof depth, not the number of successive queued-state snapshots. The node cap does not cap trace count or serialized bytes. The existing native EventLog rereads, JSON-decodes, hashes and validates the entire growing prefix on **each** event append. The added snapshots therefore amplify both storage and quadratic verification work. This is a blocker for merging this logging design before tonight's paid pilot, even though search choices themselves are unchanged.

I executed native, offline placeholder searches with the actual versioned bank, engine and immutable ports at depth 6/node cap 500. Results below are serialized JSONL byte counts, including event/chain envelopes; MB/GB/TB are decimal. One-proposal cases expand the same placeholder form through a binary or ternary tree. Three-alternative cases use three distinct placeholder forms. Padding adds 1,000 spaces to each premise text to measure sensitivity to payload size without changing formulas.

| Scenario | Nodes created | Trace events / all events, one search | Added trace MB, one search | Added trace GB, 10 targets × 2 polarities | Prefix bytes parsed, projected single 20-search log |
| --- | ---: | ---: | ---: | ---: | ---: |
| One 2-premise proposal; no padding | 127 | 385 / 766 | 32.650 | 0.653 | 4.91 TB |
| Same; 1,000-byte premise padding | 127 | 385 / 766 | 57.220 | 1.144 | 8.58 TB |
| Three 2-premise alternatives; no padding | 499 | 9,677 / 16,874 | 34.872 | 0.697 | 132.13 TB |
| Same; 1,000-byte premise padding | 499 | 9,677 / 16,874 | 67.146 | 1.343 | 241.08 TB |
| One 3-premise proposal; no padding | 499 | 1,929 / 4,122 | 539.478 | 10.790 | 435.26 TB |

The ternary case generates 500 state snapshots and only one final route. Its full one-search log is 540,804,124 bytes. These are demonstrated workload scenarios, **not** a prediction of the real papers, a universal upper bound, or measured completion times for a 20-search pilot. Text/formula sizes and proposal counts are not bounded by the three supplied pilot parameters. Extra model-call receipts, extraction history, analysis summaries, checkpoints and report copies are excluded from the projected trace increment. Twenty-search estimates assume comparable workloads share one log; they use `20 × one_search_scan + 190 × events_per_search × one_search_bytes`. Sequence/search-ID digit growth is negligible but not included. Prefix bytes are repeated input parsing, not physical disk traffic; OS caching does not eliminate JSON/hash/type-validation work.

A small actual EventLog timing sample of the first 150 patched events took 1.605 s versus 0.402 s for the same chronological prefix with its trace events removed (81 legacy events). This is an early-prefix illustration, not a full-pilot time extrapolation. Memory-sink timings are not native-writer timings.

Required before merge: replace repeated complete snapshots with versioned state transitions/references or another bounded representation that preserves faithful ancestry; retain explicit proposals, rejects and completions. Demonstrate native EventLog cost on representative cap-scale traces, including blocked states and long payloads. Do not resolve this by silently dropping trace events or weakening chain verification.

Evidence: `nu-probe.py`, `nu-volume.txt`, `nu-volume.json`, `nu-pilot-volume.json`, `nu-deep-volume.py`, `nu-deep-volume.txt`, all beside this report. An explicit shallow/flat-formula rerun (`nu-flat-probe.py`, `nu-flat-volume.txt`, `nu-flat-trace.py`, `nu-flat-trace.txt`) reproduced identical byte/event counts and the renderer failure. The original probes already parse canonical normalized formulas, which flatten conjunctions; the result does not require deep formula syntax.

## BLOCKING B2 — A missing ancestor suppresses verification against an available immediate origin

Location: [report.py:56](/home/dev/ara-work/xi/ara/runtime/report.py:56); recursive source loading in [provenance.py:29](/home/dev/ara-work/xi/ara/runtime/provenance.py:29).

`verified_snapshot` catches any `FileNotFoundError` from recursive `read_checkpoint` and treats the immediate origin as unavailable. If that origin exists but one of its ancestors is missing, the comparison of the copied events against the available origin never runs.

Executed reproduction: create valid chained imports A → B → C, with measured charges 1 in A and 2 in B. Remove A's log only. Change C's copied B charge from 2 to 102, rebuilding C's local chain/checkpoint but retaining its original import digest and B pin. B remains available and proves that C's copied event disagrees. `build_run(C)` nevertheless accepts the report and reports measured spend **103**, with a misleading warning naming available B as unavailable. Restoring A makes the exact same changed C refuse with `origin receipt import does not match pinned events`.

This is stronger than the documented limitation about rewriting a log and its own checkpoint: an independent, available, pinned origin still contains the contradictory evidence. Missing remote ancestry should not disable checks against evidence that is available.

Required before merge: distinguish an unavailable immediate origin from unavailable transitive ancestry; verify its pinned prefix and direct copied-event/digest equality before downgrading only the missing ancestor's verification. Keep the exact missing path and verification scope visible. Add a regression for available B/missing A/mismatched C.

Evidence: `nu-report-probe.py` and `nu-report-probe.txt`.

## BLOCKING B3 — A legal cap-scale trace crashes HTML rendering

Location: [report_render.py:103](/home/dev/ara-work/xi/ara/runtime/report_render.py:103), especially recursive state traversal at line 112; invoked by `render` for each search.

Executed a native search with one legal `expert_opinion` alternative, three placeholder premises per expansion, depth 6 and node cap 500. It returned 499 nodes, one route and **500 successive state snapshots**. Passing those native state graphs into production `trace_html` at the normal recursion limit of 1,000 raised **`RecursionError: maximum recursion depth exceeded`**. Receipts and decision lists were omitted from this focused renderer probe; they do not control the recursive parent/child traversal. The state graphs and ancestry came directly from the engine.

A depth-6 proof is not a depth-6 state-history tree. This can prevent the requested morning HTML/Markdown/JSON report from being published on a valid pilot run. The CLI catches the exception and returns failure; there is no iterative rendering fallback or completed report. This behavior follows the production call path; the executed probe exercised the renderer directly.

Required before merge: render state ancestry iteratively or with bounded nesting that retains all recorded states and explicit links. Cover the actual 500-state native case. Raising the recursion limit alone leaves large nested-string copying and memory amplification unresolved.

Evidence: `nu-deep-trace.py`, `nu-deep-trace.txt`; native results and default recursion limit are recorded there. This was a focused production-renderer proof, not a completed full report of that large log.

## SHOULD-FIX S1 — Begin/end alone is treated as a complete trace

Location: [report.py:256](/home/dev/ara-work/xi/ara/runtime/report.py:256), gap classification at line 309; [report_render.py:100](/home/dev/ara-work/xi/ara/runtime/report_render.py:100).

The reporter marks a trace complete on any matching `end` event. It does not validate the declared trace version, root inventory, unique state IDs, parent references, terminal route coverage or state ancestry. The HTML traversal only starts from parent `None`, so orphaned states can disappear from the visual tree without a gap.

Executed reproduction: an internally valid, anchored chain contains a final route and version-1 begin/end receipts declaring that route, but no states or completion receipt. The projection says `complete=True`, has zero states and emits **no PARTIAL SEARCH TRACE gap**. The current native writer normally emits the missing records; this is a semantic-validation defect for incomplete/custom/future receipts, not evidence that its ordinary completed traces lose records.

Validate trace invariants before calling a trace complete. Preserve malformed/unassigned receipts and disclose why branches cannot be traced. Existing legacy-log behavior is good: it retains final graphs and explicitly declines to reconstruct absent ancestry.

Evidence: `nu-report-probe.py` and `nu-report-probe.txt`.

## SHOULD-FIX S2 — Missing or unrecognized accounting classifications default to measured

Location: [report.py:77](/home/dev/ara-work/xi/ara/runtime/report.py:77), timeline classification at line 109.

Only the exact string `reservation_unknown_actual` is classified unknown; everything else becomes measured. An anchored MODEL event with `status=incomplete`, no response, cost 3 and no accounting marker is accepted as **measured 3 / unknown 0**. The same default applies to an unrecognized future classification.

Current native MODEL producers explicitly write `actual` or `reservation_unknown_actual`; I found no current-producer path omitting that marker. Known reservation receipts, pending dispatches and unfinalized measured responses are separated correctly by existing tests. The defect is the report's fail-open interpretation of an unclassified receipt, which the public RunEvent schema permits and chain verification alone cannot establish as measured.

Use explicit measured classifications and preserve missing/unrecognized classifications as unknown/unclassified with a gap (or refuse), including totals and timelines. Add a regression using an incomplete unclassified receipt. Do not relabel unfinalized measured response receipts as finalized charges.

Evidence: `nu-report-probe.py` and `nu-report-probe.txt`.

## NOTE N1 — Search semantics and named consumers passed the scoped checks

The logging diff leaves priorities, RNG calls, serial increments, cap comparisons, proposal ordering, licensing and returned graph construction unchanged. `_search_serial` affects trace identity only. Four differential searches compared the base engine loaded directly from `git show 0eb8592:ara/engine/search.py` against the patched engine with identical ports/configuration. Returned SearchResult JSON, proposer-goal order and original ENGINE decisions matched exactly in all four cases. Existing deterministic replay tests also passed. Thus I found **no search-result or determinism regression**, subject to successful logging; added I/O, serialization failures and resource exhaustion remain operational effects under B1.

Executed consumer checks against the existing placeholder `xi-native-smoke` with 26 trace receipts:

- Methodology export with/without trace receipts had identical summary fields except the expected record count and last hash.
- Native provenance import preserved all 26 trace events and `verify_imports` passed.
- Eta's actual `load_frozen` implementation at `185a318`, run in eta's own offline environment, accepted xi's traced native smoke. Its seven-record construction prefix precedes search; the new SYSTEM events do not masquerade as MODEL receipts or change the frozen contract.

The first attempt to import eta's verifier inside xi's package environment failed because xi lacks eta's `response_contracts` module. The successful check used eta's native environment. This is a scoped compatibility probe, not a claim that an entire merge of both feature branches was built/tested. Evidence: `nu-consumers.py` / `nu-consumers.txt` and `nu-eta-probe.py` / `nu-eta-probe.txt`.

## NOTE N2 — No committed-content leak found; ignored output remains an operator constraint

Direct review of the changed source, tests, documentation and commit diff found placeholder examples and generic implementation only. `git diff --check 0eb8592..74aa4ca` passed. The report path is offline, is reached before provider construction, reads event chains before publication, labels arbitrary artifacts unauthenticated, and escapes content in HTML. Tests cover refusal of changed/truncated anchored chains, verification of all inputs before output, HTML escaping, and unchanged source bytes. Missing checkpoints are explicitly disclosed as unable to prove suffix completeness. B2 is the identified exception to the claimed available-origin verification.

No tracked xi files were changed by this review. There is **no automatic git write or commit**, and existing nonempty output directories are refused. However, `--out` accepts any fresh separate directory; it does not enforce gitignored `runs/`. A mistaken output path can create trackable copies of full prompts, responses and artifacts. The README's instruction to keep real output in ignored `runs/` is an operator requirement, not a coded guard. Use that path for the pilot; enforcing it would strengthen the original brief's content constraint. A text scan/direct review cannot prove semantic absence across all possible future content.

## NOTE N3 — Verification record and remaining proof limits

The full suite and control runner were executed **sequentially**. Full suite in xi: `ARA_LIVE_TEST=0 uv run --offline pytest` → **534 passed, 2 skipped**, 266.53 seconds. The skipped cases are the paid-provider gates. Evidence: `nu-pytest.txt`.

Full control runner: `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline python tests/integration/negative_controls.py` → **218/218 mutations failed their targeted tests, and all 218 restored runs passed**. All **18** mutated production files match their pre-run SHA-256 hashes. The detached control checkout and original xi checkout are clean at the reviewed head. Final machine-readable receipt: `nu-verification.json`.

The control runner mutates production files, so it ran in `/home/dev/ara-work/nu-control-checkout`, a detached local clone of the exact reviewed head, with an offline locked environment. This preserved the instruction not to edit xi's branch. Evidence: `nu-controls.txt`, the clone's `runs/delta-controls/results.json` and per-control red/green transcripts, and `nu-control-hashes-before.json`.

Read all nine added mutation definitions: anchor removal, reservation bucket removal, combined accounting deduplication removal, source-link removal, HTML escape removal, historical roster removal, unfinalized response removal, current-outcome boundary removal, and rejected-proposal trace removal. Also read older writer/route mutations and their actual assertion failures/restored passes. Read the actual red assertion failures and restored passes for all nine new controls, in addition to five older controls (`writer_marker_coverage`, `writer_nontrivial_body`, `writer_citation_padding`, `shared_audit_outline`, `route_artifacts`). Selected new-control evidence:

| Mutation | Observed red result | Restored result |
| --- | --- | --- |
| `report_anchor` | Truncated anchored input no longer raised LogTampered | 1 passed |
| `report_reservations` | Unknown reservation total became 0 instead of 3 | 1 passed |
| `report_deduplication` | Combined charge became 4 instead of 3 | 1 passed |
| `report_html_escape` | Literal script markup appeared in HTML | 1 passed |
| `search_trace_prunes` | UNKNOWN_BANK_ID disappeared from rejection receipts | 1 passed |

The four remaining new controls failed on absent source links, a lost historical paper, lost unfinalized measured usage, and an incorrect current extraction outcome; each restored run passed. Exact targets, failure excerpts and result summaries are in `nu-verification.json`.

Passing existing tests/controls does not invalidate B1–B3 or S1–S2: their reproduction cases are outside that coverage. No real-paper/paid replay, complete 20-search native-writer timing, browser visual inspection, actual Graphviz execution, or full eta+xi branch integration is claimed. All additional probes used placeholder data. No source fix was authorized by this read-only brief; the review leaves the requested changes to the author.

## Finding placement audit

| Finding | Deliverable section |
| --- | --- |
| Logging volume and full-prefix verification amplification | BLOCKING B1 |
| Available origin verification suppressed by missing ancestry | BLOCKING B2 |
| Native cap-scale HTML recursion failure | BLOCKING B3 |
| Unsupported complete-trace claims | SHOULD-FIX S1 |
| Unclassified spend defaults to measured | SHOULD-FIX S2 |
| Search semantics, consumer compatibility and integration scope | NOTE N1 |
| Tracked content and ignored-output enforcement limits | NOTE N2 |
| Executed suite/controls, mutation review and remaining proof limits | NOTE N3 |

8 findings, 8 placed

DONE nu review logging=fix-first report_tool=fix-first blocking=3 should_fix=2 tests=534/536 negctl=pass

## Re-review

Reviewed revision `56039948c34b104f15bab13b455fadcc050c9c2d` against `74aa4ca`, under the same read-only/no-paid-calls brief. This section supersedes the earlier merge dispositions; the original findings above remain as the historical record.

**Disposition: logging merge; report tool fix-first. Zero BLOCKING findings; one remaining SHOULD-FIX (R1/S1).** B1, B2, B3 and S2 are fixed and independently verified. S1 fixes the original empty-trace case but still accepts contradictory or unresolved branch evidence. No current native search-result regression was found. The split verdict applies to components; the combined branch still carries R1.

### SHOULD-FIX R1 — S1 still calls internally inconsistent traces complete

Location: [report_traces.py:214](/home/dev/ara-work/xi/ara/runtime/report_traces.py:214) and [report_traces.py:231](/home/dev/ara-work/xi/ara/runtime/report_traces.py:231).

The new validator resolves definitions and checks inventories, references, terminal coverage and much of the state path. It does not finish comparing the selected proposal and node ancestry with the completed graph, or require a disposition for every recorded proposal.

I created a normal sealed modus-ponens trace, made each of the following changes separately, and rebuilt the local sidecar digest/seal so these tests exercise semantic consistency rather than ordinary hash tampering:

| Case | Contradictory or unresolved recorded evidence | Actual result |
| --- | --- | --- |
| Terminal proposal | Change the terminal inference's proposal reference to a valid, content-addressed proposal with the same bank ID but premise text R; leave the selected proposal and recorded proof nodes unchanged | complete=true, issues=[] |
| Node parent | Change node n2's recorded parent/depth to n1/2; the completed graph still has the edge n0→n2 | complete=true, issues=[] |
| Alternative disposition | Add recorded proposal index 7 with no inference successor or prune receipt | complete=true, issues=[] |

The README promises that inconsistent traces are partial; these cases contradict that promise. The clean control also remains complete. All payloads use placeholders. These are synthetic, internally inconsistent receipts; I did **not** observe the current native producer emitting them. Rehashing is intentional here: the new S1 contract promises semantic checks after authentication, and its own tests use the same approach.

The present comparison checks the proposal's bank ID but not its full identity; node definitions are checked for an internally plausible parent/depth, not agreement with the selected graph edges. A hash proves which bytes were sealed, not that these statements agree. The reporter consequently presents an unsupported complete-trace claim.

Before closing S1: compare each terminal inference with its selected proposal reference/full decoded proposal; compare its selected child edges with recorded node parent/depth; and require each recorded alternative to be admitted or explicitly pruned. Preserve inconsistent receipts, name the mismatch, and mark that trace partial. These checks need no search or solver re-execution. Add the three regression cases above.

Evidence: `nu-round2-probes.py`, `nu-round2-probes.txt`. The terminal-proposal case also renders as “complete” in the full HTML report; `nu-round2-r1-render.json` records that output. This is one remaining SHOULD-FIX finding, continuing S1; it does not reopen B2 or claim altered search results.

### B1 — Delta sidecar design and native performance

The engine now depends on a trace port; native orchestration supplies SearchTraceFiles. Search choices, queue costs/RNG draws, licensing and original ENGINE events remain intact. Sidecars contain state/node deltas and content-addressed formula, text and proposal definitions. Completed route topology occurs once per route in the trace and references those definitions. Existing non-trace route persistence is unchanged. There is no graph snapshot on every queued state.

On successful search completion, the sidecar is flushed/fsynced and one ordinary chained receipt records its path, line count and SHA-256. Interrupted searches retain an unsealed file, which reporting treats as partial and does not interpret. The reader checks raw bytes and count before using the content; missing sealed files remain explicit gaps. EventLog's existing prefix-verification algorithm was not weakened.

I inspected and reran the native benchmark runner rather than relying on xi's timing receipts. Each pair uses the actual EventLog writer, baseline engine loaded from `0eb8592`, depth 6/node cap 500, and exact comparisons of returned SearchResult JSON, proposer-goal sequence and original ENGINE decisions. Independent pairs use distinct CPUs on this shared host; within each pair the baseline runs before the traced variant.

| Scenario | Nodes / routes | Baseline s | Traced s | Increment % | Sidecar bytes | Seal/checkpoint increment bytes | 20-search trace MB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| One binary alternative | 127 / 1 | 7.449 | 7.734 | +3.827 | 150,729 | 900 | 3.03258 |
| One binary alternative; 1,000-byte padding | 127 / 1 | 7.406 | 7.477 | +0.967 | 159,269 | 900 | 3.20338 |
| Three binary alternatives | 499 / 167 | 1550.476 | 1496.688 | -3.469 | 2,169,641 | 904 | 43.41090 |
| Three binary alternatives; 1,000-byte padding | 499 / 167 | 1554.541 | 1493.673 | -3.916 | 2,212,419 | 904 | 44.26646 |
| One ternary alternative | 499 / 1 | 172.288 | 173.357 | +0.620 | 678,468 | 904 | 13.58744 |

**Both requested performance targets pass in these independent workloads.** Worst observed increment: **3.827%**; largest projected pilot trace: **44.26646 MB**. All five sidecars authenticate and pass the production reader; every decoded terminal graph also exactly matches an independent deterministic engine rerun. B1 is closed.

Pilot size is twenty comparable searches (ten targets × two polarities), decimal MB, including sidecars and the measured incremental seal/checkpoint bytes. It excludes the pre-existing engine/model log, route artifacts and report copies. It is a workload projection, not a hard bound on arbitrary content or a measured whole-pilot duration. Single-pair timing differences include host variability; negative increments are not claimed speedups. The unchanged baseline writer remains expensive in the branching cases.

Evidence: `nu-round2-bench-{small,binary,padded,ternary}.txt`; native logs/sidecars and results under xi's ignored `runs/nu-round2-bench-*`; consolidated `nu-round2-benchmark.json`.

### B2 — Available immediate origins are checked before missing ancestry

The implementation now reads and pins each available immediate origin, compares its copied events and receipt digest, and only then walks its ancestors. Missing-ancestor warnings identify the missing path without disabling direct comparisons.

Reran the independent A→B→C reproduction: changing C's copied B charge from 2 to 102 is now refused while A is missing and B is available. It remains refused after A is restored. The regression suite additionally checks that an unchanged C reports the valid total and identifies only missing A. B2 is closed.

### B3 — Native 500-state report now succeeds

Reran the native ternary depth-6/node-500 case through the actual EventLog writer, then ran the native report CLI against that newly generated log. It produces a complete trace with 499 proof nodes, 500 state blocks, one completed route, all 2,193 original ENGINE decisions and one DOT export. The HTML is 14,320,626 bytes; state 499 and all 500 state anchors are present. No recursion-limit adjustment was used.

The renderer iterates state history and supplies explicit parent/child links; route traversal is also iterative. B3 is closed. This is executed full-report evidence, not only the earlier direct-renderer probe. Output: [cap-scale report](/home/dev/ara-work/xi/runs/nu-round2-cap-report/report.html). Receipt: `nu-round2-cap-proof.json`.

### S1 original case and S2 accounting

The original begin/end-only trace now has complete=false and an explicit partial-trace gap. New version/root/parent/reference/terminal checks address substantial portions of S1; R1 above explains why it is not fully closed.

Only an explicit actual accounting marker now enters measured totals. Missing and future markers retain cost/tokens in unclassified totals and timelines with an explicit gap; reservation and unfinalized measured-response buckets remain distinct. The original incomplete receipt now contributes zero measured dollars. The new parametrized tests cover both missing and future markers. S2 is closed.

### N1/N2 — Consumers, semantics and content boundaries

The fresh round-2 native smoke has four sealed traces. Methodology summaries with and without seals differ only in record count and tail hash. Native provenance import verifies, retains all four seals, and the report resolves all four traces through their recorded source paths. I generated a combined native/imported report and verified that source file hashes were unchanged. The saved version-1 native smoke also remains readable: four complete traces, six states and four routes (`nu-round2-legacy.json`).

Eta's actual frozen-T verifier at `185a318`, run in eta's own environment, accepts the seven-record construction prefix of the fresh-cache round-2 smoke. This remains a scoped compatibility check, not a full merge/integration build of both branches. All five completed native benchmark pairs preserve exact results, proposer order and original decisions.

Changed code/tests/tools remain placeholder-only by direct diff review. The review did not alter xi's tracked files, run a live/paid provider, delegate, or push. The previously disclosed output-path constraint remains: the operator must choose ignored storage for real reports. The new benchmark tool enforces ignored runs output for its own artifacts; the general report CLI still accepts any fresh separate directory.

Evidence: `nu-round2-consumers.py/.txt`, `nu-round2-eta.py/.txt`; the consumer transcript gives the regenerated report path.

### N3 — Independent verification and limits

Full suite at the reviewed head: **560 passed, 2 paid-provider tests skipped**, 313.37 s. Command: `ARA_LIVE_TEST=0 UV_OFFLINE=1 taskset -c 4 uv run --offline pytest`. Transcript: `nu-round2-pytest.txt`.

Full control runner: **226/226 mutations failed their targeted tests, and all 226 restored runs passed**. Command: `ARA_LIVE_TEST=0 UV_OFFLINE=1 taskset -c 4 uv run --offline python tests/integration/negative_controls.py`. All **20** mutated production files match their pre-run SHA-256 hashes, and the detached control checkout is clean at the reviewed head. Transcript: `nu-round2-controls.txt`; before hashes: `nu-round2-control-before.json`; full red/green transcripts remain in the clone's `runs/delta-controls/`.

Read the actual failure and restoration outputs for all eight new controls. They fail when direct-origin comparison is disabled, unclassified spend becomes measured, sidecar hash/count checks are removed, empty traces are declared complete, unresolved-reference diagnostics disappear, terminal payload interning is removed (projected trace exceeds 100 MB), or the 500th rendered state is dropped. Each restored run passed. The unresolved-reference mutation specifically proves the missing-reference diagnostic; other validation still kept that malformed trace partial.

To preserve the no-branch-edits requirement, controls ran in a detached local clone at the identical head, `/home/dev/ara-work/nu-round2-control-checkout`, after the full suite finished. The eight new mutation definitions were read; actual failure/restoration evidence and final hashes are recorded in `nu-round2-verification.json`. Passing these controls does not cover the three additional R1 cases.

No real-paper/paid replay, full twenty-search elapsed-time benchmark, browser visual inspection, actual Graphviz run, invoice reconciliation or full eta+xi integration is claimed. Missing sidecars are disclosed, not reconstructed. The remaining report recommendation concerns semantic completeness claims, not a failure of ordinary sidecar hash verification.

### Re-review finding placement audit

| Reviewed finding | Current disposition and section |
| --- | --- |
| B1 trace volume and native overhead | B1 design/performance section |
| B2 available origin verification | B2, closed |
| B3 cap-scale rendering | B3, closed |
| S1 semantic completeness | Original case fixed; remaining SHOULD-FIX R1 |
| S2 unclassified spend | S1/S2 accounting section, S2 closed |
| N1 semantics and consumer compatibility | N1/N2 |
| N2 content/output constraint | N1/N2 |
| N3 independent tests, controls and unexecuted proofs | N3 |

8 findings, 8 placed

DONE nu rereview logging=merge report_tool=fix-first blocking=0 should_fix=1 trace_mb_pilot=44.26646
