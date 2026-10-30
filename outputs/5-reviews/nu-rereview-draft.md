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
