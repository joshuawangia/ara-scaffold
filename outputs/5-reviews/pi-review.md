# Pi — narrow non-author review of mu Round 4

**Verdict: fix-first; one blocking correctness finding, zero additional should-fix findings.** The current published corpus passes the structural retention checks. The blocking finding is a valid-input snapshot-context defect reproduced with placeholder sources; the corresponding prerequisite-context mismatch is absent from this artifact.

Reviewed `/home/dev/ara-work/mu`, branch `fix/four-paper-acceptance`, exact head `9d4ec86595f7c46d5ba6d6f9747d86d50533246a`, against base `070efb7bc5ed83d7b5528a42813a57b388751eb2`. This review executes `briefs/pi-review-mu4.md`; it does not edit the branch or delegate work. All evidence below is under `/home/dev/ara-work/reports/pi-evidence/` unless specified otherwise.

## B1 — Union isolation omits native prerequisite relationships

**Blocking, P2.** In [snapshot_union.py](/home/dev/ara-work/mu/ara/runtime/snapshot_union.py:31), incoming contexts are collected only for items whose kind is `inference`, and the reverse dependency is added only when the referenced target is an inference. Valid `applies_to` links can also target premises and conclusions. The actual pilot consumer, [construction.py](/home/dev/ara-work/mu/ara/runtime/construction.py:49), makes an incoming qualifier a prerequisite of **every** target kind. It also makes an inference a prerequisite of its conclusion; the union does not use that reverse relationship when deciding which contexts must stay separate.

Reproduction through native extraction and publication: snapshot A contains premise P; snapshot B has the identical premise ID/body plus a new eligible qualifier applying to P. Both original artifacts verify. `resume_papers → extract(..., salvage_only=True)` produces a provenance-valid union, but coalesces the two P contexts into one item with two original provenances. Native `prerequisite_closure` for A's mapped P now includes B's qualifier. A's original closure did not include it. The implementation therefore changes the constraints of one snapshot by attaching another snapshot's incoming qualifier. No text body needs to change for this defect to occur.

An inference target gets separate IDs, but its shared conclusion connects both inference variants through native prerequisites; the old inference still reaches the new snapshot's qualifier. Checking only separate inference IDs would miss this. The final parameterized regression checks actual closure and fails for all four target kinds: **0 passed, 4 failed**. This is separate from the committed suite's results. Evidence: `test_snapshot_context.py`, `context-probe.txt`, and `context-probe-{i,p,r,f}.json`. The test uses mock provider responses, blocks sockets, and invokes production publication/provenance and construction dependency functions.

Before merge, derive snapshot context from the relationships the native consumer actually treats as prerequisites, including incoming `applies_to` on non-inference items, and propagate distinct contexts through dependent references. Add native closure regressions for all four target kinds and a production-wire negative control; preserve the existing quarantine and inference-target tests. This review made no repair.

**Current-artifact impact:** an independent inventory checked all **741 coalesced items** across the six multi-snapshot papers and found **zero differing incoming native prerequisite contexts**, checking both `applies_to` and inference-to-conclusion relationships. This narrows the observed corpus impact; it does not make the valid-input failure correct. Evidence: `context_inventory.py`, `context-inventory.json`, `native_context_inventory.py`, `native-context-inventory.json`.

## Root cause and repair location

`resume-skip-id-remap` is supported by the code and original receipts. Base `resume_papers` skipped completed range-union outcomes carrying `thin_range` or `unextracted_pages`, then accepted-range salvage reconstructed their IDs. The four affected prior outcomes carry original **v5** acceptance identities with thin-range disclosures; they are not four newly generated v6 model outputs.

My independently derived suffix mapping reproduced all **532 original bodies and links**, allowing only ID/citation/reference renaming: 36 renamed in `vonfintelgillies2007`, 11 in `braun2012`, two in `yalcin2011`, two in `moss2015`; total **51**. The latest overnight batch contains zero MODEL calls for these four sources. The patch removes the skip at the selection cause, reuses compatible completed snapshots directly, and retains their limitations. The new completed-history test checks exact item equality; interrupted-history salvage remains separately covered.

Evidence: `independent_structure.py`, `independent-structure.json`; base/head diff and `test_historical_thin_retry_is_not_repeated`.

## Union retention, provenance, and recomputation

Apart from B1's incoming-context gap, the implementation and executed checks support lossless structural union:

- Every compatible original item maps to a published item with the same body, attribution, locators and mapped references. Every union output item has original provenance. No novel source text was added.
- Nonconflicting IDs use a deterministic source namespace; body collisions and their tracked dependent contexts use full snapshot hashes. Sorting makes IDs and item provenance independent of input order for the same snapshot set. Committed tests cover both source orders and a second resume. I also rebuilt all six real multi-snapshot graphs and their item provenance exactly in both input orders (`rebuild_unions.py`, `rebuild-unions.json`). This is not a promise that adding a new conflicting snapshot leaves previously shared IDs unchanged.
- Every coalesced real-artifact item has exactly one distinct original `(id, body hash)` pair. Identical text under distinct original IDs is retained separately. The 51 additional records preserve original and remapped identities; they are not newly extracted claims.
- Manifest graph hashes, original acceptance identities and per-item original IDs/hashes/citations reproduce. Original checkpoint pins verify and contain the named original snapshots. Derived unions are rebuilt from their originals on resume; the forged-derived-graph regression tests refusal before destination import.
- Fresh grounding from physical PDF page text reproduces **317 quarantined / 3,407 eligible** items. Eligible explicit references avoid quarantine. Snapshot-scoped resolutions and quarantine reproduce **46 open gaps**, and the published methodology agrees. The gaps are snapshot-scoped obligations, not 46 independently distinct semantic omissions.

The artifact audit was rerun from the author's reviewed `audit.py` with outputs redirected to this review's evidence directory; it was not merely an inspection of their success receipt. Independent scripts additionally checked the root-cause mapping, zeta counts, deduplication pairs, checkpoint membership and consumer-context discrepancy. Evidence: `replay_artifact_audit.py`, `artifact-audit.txt`, `audit-summary.json`, `manifest_pins.py`, `manifest-pins.json`, `independent-structure.json`. The prior Round 3 artifact also reverified unchanged.

## Reconciliation overflow

The production `reconcile` catches the counted request overflow, appends a failure disposition, logs `extraction_reconciliation_failed`, and returns accepted ranges. The overnight log confirms **382 retained items**, an `extracted` outcome for `hollidaymandelkern2024`, another completed outcome and a subsequent paper start after the failure. It contains no subsequent provider dispatch. The independently inspected admission record (`overflow-admission.json`) shows 220,721 input tokens plus 32,000 output allowance against a 200,000 context bound. The later operator stop was separate from this caught reconciliation failure.

The two-paper native regression proves that overflow preserves the first paper's 16 items, accepts the next paper's eight items, and never dispatches reconciliation completion. The production-wire mutation rethrows the exception. No windowed reconciliation was added; the brief makes splitting optional.

## Published artifact and zeta floor

Artifact: `/home/dev/ara-work/mu/runs/mu-round4-offline/literature.extracted.txt`.

SHA-256: `c6f5db583c22f8b3685c31e4af4c2199efcf6e71f7550c53022744c9b06deaf7`.

Pinned transitive provenance and exact logged serialization verify. There are **26 records, 22 nonempty graphs, 3,724 retained items, 317 quarantined, 3,407 eligible, 46 open gaps**, and four explicitly reasoned exclusions. Five nonempty graphs remain partial. Every paper meets or exceeds zeta's diagnostic inventory:

| Paper | Zeta items | Published items | Delta |
|---|---:|---:|---:|
| vonfintelgillies2007 | 100 | 136 | +36 |
| eganweatherson2011 | 125 | 125 | +0 |
| vonfintelgillies2011 | 147 | 147 | +0 |
| wright2007 | 105 | 105 | +0 |
| schaffer2011 | 194 | 194 | +0 |
| braun2012 | 108 | 119 | +11 |
| eganhawthorneweatherson2005 | 213 | 213 | +0 |
| egan2007 | 158 | 158 | +0 |
| macfarlane2011 | 169 | 169 | +0 |
| macfarlane2014 | 0 | 0 | +0 |
| yalcin2007 | 210 | 210 | +0 |
| yalcin2011 | 85 | 87 | +2 |
| rothschild2012 | 71 | 71 | +0 |
| moss2015 | 239 | 241 | +2 |
| hawkesteinertthrelkeld2021 | 227 | 227 | +0 |
| veltman1996 | 267 | 267 | +0 |
| gsv1996 | 259 | 259 | +0 |
| willer2013 | 169 | 169 | +0 |
| yalcin2015 | 0 | 0 | +0 |
| ninan2018 | 180 | 180 | +0 |
| beddorgoldstein2021 | 123 | 123 | +0 |
| hollidaymandelkern2024 | 382 | 382 | +0 |
| kolodnymacfarlane2010 | 84 | 84 | +0 |
| klinedinstrothschild2012 | 0 | 0 | +0 |
| bledin2014 | 0 | 0 | +0 |
| knobeyalcin2014 | 58 | 58 | +0 |

The exclusions are retained as roster records; they supply no evidence. Counts describe accepted inventory, not distinct or semantically verified claims.

## Native offline pilot import

**Pilot import: OK.** The native CLI verified and imported all 3,310 original receipts, reached construction with **3,407 eligible items across 22 sources and four excluded roster entries**, and stopped deliberately at its first token-count request, before any provider call. No network attempt occurred; exported methodology confirms zero local MODEL calls and USD0 local cost. Elapsed time was 2470.4 seconds. Evidence: `pilot_import.py`, `pilot-import.json`, `pilot-import/events.jsonl`, `pilot-import/export/methodology.md`, and `final-verification.json`. The probe uses the saved overnight `mu/runs/mu-round4/config.yaml` with `--profile pilot`, placeholder topic P, the actual published artifact, and an external empty destination. Sockets are blocked and a generation-incapable provider is supplied. It intercepts the first `ModelCalls.count_request`, before any provider estimate or completion, after native provenance import, `prepare_commitments`, `ModelCalls.build_t`, quarantine filtering and construction dependency setup.

The actual overnight profile retains `unknown_usage_policy: count-at-reservation`; this matters because ancestry contains held unknown-usage reservations. An initial probe using repository-default configuration was stopped during receipt copying and restarted with the correct saved configuration; both histories are retained (`import-attempt-note.txt`). No cap was raised and no policy was bypassed.

This check cannot prove provider token fit, successful model construction, freeze, search, or semantic faithfulness. Its scope is native offline import and pre-provider structural acceptance.

## Executed tests, controls, and limits

- Full suite in an isolated exact-head clone `/home/dev/ara-work/pi-verification`: **608 passed, 2 skipped / 610**, exit 0, 302.36 seconds reported by pytest. The two skips are opt-in provider checks.
- Full production-wire control runner started only after that suite exited successfully, on the same restored revision: **265/265 mutations red (exit 1), 265/265 restored targets green (exit 0); runner exit 0**, 803.04 seconds. Exact commands, sequence and exit receipts are in `verification.json`; all results are in `control-results.json`. The verification clone is clean at the reviewed head after restoration.
- Additional non-author snapshot-context regression: **0 passed, 4 failed / 4**, as B1 describes. It is outside the branch and outside the committed suite denominator.
- Real-artifact structural and historical provenance audits passed with network blocked. No source content was semantically read or reproduced in this report.

I directly read all eight new mutation definitions and their independently rerun red/restored transcripts (`inspected-controls/`):

| Mutation | Observed red behavior; restored target passes |
|---|---|
| `snapshot_collision_namespace` | Refuses conflicting mapped items when snapshot qualification is removed |
| `snapshot_incoming_qualifier` | Nine items instead of ten when the reverse inference-qualifier dependency is removed |
| `snapshot_incoming_presence` | Nine items instead of ten when presence-only incoming contexts are ignored |
| `snapshot_reference_mapping` | Original `applies_to` ID survives instead of its mapped union ID |
| `snapshot_gap_scope` | Zero open gaps instead of one because another snapshot's resolution closes it |
| `snapshot_derived_reconstruction` | Forged derived graph is accepted instead of raising |
| `completed_thin_snapshot_reuse` | Previously native IDs are reconstructed with salvage namespaces |
| `reconciliation_overflow_continues` | Overflow escapes and stops the paper/run path |

The namespace-removal mutation is caught by an additional conflict guard; its red result proves sensitivity/refusal, not silent corrupt output. The two qualifier controls assert the intended inference inventory and quarantine behavior, but do not exercise native prerequisite closure; B1 is the uncovered consumer behavior. Passing controls do not override that regression.

Final exact-head status checks are clean for both the reviewed source and restored verification clone (`final-verification.json`); the artifact hash is unchanged.

No paid calls, source-branch edits, delegation, push, completed real-corpus construction, freeze, search, or semantic-completeness verdict occurred. Lexical grounding is not semantic entailment. Earlier extraction/source-quality limitations remain. Deferred shared-frozen compatibility is outside this review. Buckeye's JavaScript gate does not apply to this separate Python repository.

## Finding placement

| Finding | Placement |
|---|---|
| 1 — Native prerequisite context crosses snapshots; absent from this artifact's shared-item inventory | B1 |
| 2 — Resume selection caused 51 exact namespace remaps; repair is at the selection cause | Root cause and repair location |
| 3 — Original bodies retained, stable deterministic mapping/deduplication and original provenance, subject to B1 | Union retention, provenance, and recomputation |
| 4 — Quarantine and snapshot-scoped gaps recompute; counts do not establish semantic completeness | Union retention, provenance, and recomputation; Published artifact and zeta floor |
| 5 — Reconciliation context overflow is logged and skipped, allowing continuation | Reconciliation overflow |
| 6 — Exact artifact provenance, inventory, exclusions and every zeta per-paper floor | Published artifact and zeta floor |
| 7 — Native pilot import result, actual configuration and pre-provider proof limit | Native offline pilot import |
| 8 — Exact-head tests, controls, independent regression, restoration and scope limits | Executed tests, controls, and limits |

8 findings, 8 placed.

DONE pi review verdict=fix-first blocking=1 should_fix=0 tests=608/610 negctl=pass pilot_import=ok
