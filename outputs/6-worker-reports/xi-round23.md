# Xi Round 23 — formula/paper provenance and bounded search context

Base: 25e076a01bc68dc0d717ab0e9949c7674f3bfc07, feat/run-report,
checkout /home/dev/ara-work/xi. Local work only; no paid calls, push or delegation.

## R22-F1 repair

Every reachable leaf/CQ commitment is retained in its formula-hash group. Logical
checks use one deterministic representative per formula, while paper matching uses
every cited commitment's verified source ID. The gate requires two distinct
formulas assignable to two distinct papers, with a stable two-edge witness. Each
receipt exposes all formula/commitment/paper associations. Sorting CQ supporting
IDs no longer changes the receipt, classification or default selection.

The native reversed-order regression freezes t1=P/a, t2=Q/a, t3=P/b, closes a sign
route to fresh R, and confirms both orders are CLOSED-derived and selectable.
Graphs agree after sorting CQ evidence lists; the native report reproduces the
same contribution receipt. Repeated P across papers can supply b while Q supplies
a. True same-paper P/Q remains CLOSED-single-paper; P alone across papers remains
CLOSED-single-support. Existing reachability, stance, licensing, novelty and CQ
checks remain on the production path.

## Executed verification

Before the production fix, four new test cases failed: the forward-order and
positive matching cases incorrectly classified as single-paper, and the two
negative cases lacked the new matching receipt. After the fix, all 58 focused
tests passed (cross-paper, contribution gate, report contribution, nonlogical
contribution; 93.13 seconds). Three new controls remove duplicate provenance or
allow paper/formula reuse; the existing cross-paper gate and alias-deduplication anchors were retargeted.
Preflight confirms all 555 control anchors occur exactly once.

A separate exhaustive probe checked all 400 nonempty-neighborhood bipartite
graphs with zero to three formula groups and up to three papers, comparing
the result against exhaustive partial injective assignments. All matched, all
witness edges referenced the correct source, and reversing group/provenance order
left receipts unchanged. Receipt: runs/xi-round23/matching-probe.json.

Full pytest passed **1,266 tests, four skipped / 1,270 collected**, in 1042.95
seconds. All production and collected-test hashes match the pinned tree.
The only hash change during pytest was the noncollected negative-control runner:
its old alias-deduplication anchor was retargeted during read-only preflight.
The gate receipt records that manifest-only change explicitly. No production
or test change was made to obtain the pass. A new snapshot pins the final
manifest before running all 555 controls, sequentially after pytest.
That first full suite predates the added context repair. At the user's scope
addition, the initial control run was interrupted cleanly (exit 130); all mutated
source hashes were restored. It is not a completed full-control receipt.
Final full gates will verify the combined change.

## Bounded leaf requests and job-local context failures

map_leaf and propose_cuts receive at most eight candidate bridges ranked by
shared leaf formula symbols, with stable bridge-ID ties. Bridge commitments
supply the slice and referenced catalogue entries. When no bridge is available,
a bounded 2*k pool ranked by exact match, symbol overlap and ID supplies fallback
leads, including when a fresh atom has no shared symbol. One exact formula match
is retained at k=0. Zero-overlap leads are explicitly disclosed as deterministic
candidates, not semantic matches.

The request carries projected source roles rather than the full provenance
sidecar or repeated exact source text. Full T/catalogue/provenance hashes bind
the projection; frozen files, local validation, stance rules and licensing retain
the full originals. Scheme signatures retain exact CQ wording while omitting
duplicated slot templates and bibliographic bank metadata.

Native counting includes initial context and the output allowance. Oversized
requests shrink k through 8,4,2,1,0, with counted search_context_slice receipts.
Validation feedback and cut corrections are recounted from the full inputs.
An irreducible context refusal uses search scope for search ports, does not set
the shared budget's halted flag, and does not cancel sibling jobs. Existing
bounded retries and partial-result disclosure remain. Actual token/cost caps,
unknown accounting and infrastructure failures remain run-wide stops.

All 67 affected search tests passed. The additional correction-feedback and
later-search-port tests passed in a 12/12 focused repair run. The broader
42-case CLI/calls check initially found one stale canned map request key;
updating the fixture to the sliced request restored its typed-reference test.
Native mock fixtures were regenerated offline. No provider dispatch occurred
in the real-source measurement below.

## Fork-4 offline size replay

The replay reads the eight saved native map/cut admission requests and restores
the calibration state at each recorded event. The native Codex counting functions
reproduce **all eight original input/output counts exactly**, then count the
new request using the same calibration and configured 200000-token limit.
No credential loader, transport, canary or model call runs.

| Polarity job | Old map total | New map total | Old cut total | New cut total |
| --- | ---: | ---: | ---: | ---: |
| 0 | 198593 | 37519 | 215578 | 48435 |
| 1 | 198603 | 37529 | 215588 | 48445 |
| 2 | 198744 | 37670 | 215730 | 48587 |
| 3 | 198764 | 37690 | 215750 | 48606 |

Each new request uses k=8, 9 selected commitments and 11 catalogue entries.
Totals include the unchanged **16384-token output allowance**. The maximum is
**ctx_max=48606**, compared with 215750 before. These are calibrated admission
estimates, not measured provider usage. All source-run top-level artifact hashes
are unchanged. Evidence: runs/xi-round23/fork4-context-final/results.json,
source-hashes.json, per-request counting logs, and fork4-context-final.txt. The
read-only harness is runs/xi-round23/fork4-context.py.

## Limits and finding placement

Matching verified source IDs does not establish semantic independence, truthful
CQ evidence, necessity of every support, faithful formalization or useful live
synthesis. The bounded slice can omit useful evidence; shared symbols and
zero-overlap seeds are heuristics. Context fit does not prove live completion.
The pre-existing concentration of the bridge pool around generic definition
terms is not repaired by ranking and bounding that pool. No live fork was
restarted, no paid calls were made, and nothing was pushed.

5 findings, 5 placed: ordering/provenance defect and repair in R22-F1 repair;
preserved same-paper and duplicate-only exclusions in R22-F1 repair; request
growth and counted shrink behavior in Bounded leaf requests and Fork-4 offline
size replay; local context failure versus global accounting stops in Bounded
leaf requests; heuristic and live-evidence limits in Limits and finding placement.

## Final verification checkpoint

The initial 11 targeted new/retargeted controls all detected their mutations and
passed after restoration. The final slice uses fallback seeds only when no bridge
is available. Final full pytest passed **1276 tests, four skipped / 1280 collected**, in
1093.44 seconds, with every pinned source hash unchanged. All **561/561 integration controls** then passed on this same tree: every
mutation caused its expected failure and every restored test passed. The runner
completed in 2895.16 seconds. All **231 pinned source hashes** match after both
stages; git diff --check passed. Earlier counts above are scoped or pre-context evidence.

## Final revision and receipts

Committed locally as **2ed9e21796bf55e1160bd6a22e1f0f459bb67436** on feat/run-report. The working tree
is clean, and all 231 committed source files match the exact final verification
snapshot. No push, delegation or paid calls occurred.

Final evidence is under /home/dev/ara-work/xi/runs/xi-round23/final-gates/:
pytest-full.txt, controls-full.txt, control-manifest.json, controls/results.json,
every control's red/green transcripts, source-before.json,
source-after-controls.json, verification.json, final-verification.json and
commit-verification.json. The final real-source context measurement is
runs/xi-round23/fork4-context-final/results.json; it is separate from, and
supersedes, the earlier wider-slice measurement.

**5 findings, 5 placed**, as inventoried above. Offline checks establish admission
and policy behavior; they do not claim a successful live fork or useful synthesis.

DONE xi round23 head=2ed9e21796bf55e1160bd6a22e1f0f459bb67436 tests=1276/1280 negctl=pass fixed=kappa4-R22-F1 ctx_max=48606
