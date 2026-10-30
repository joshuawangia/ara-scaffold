# Omicron: non-author review of mu and three-branch integration

**Recommendation: fix-first.** Mu's core range-union and quarantine design is useful under the operator's explicitly relaxed acceptance bar. I found two blocking mu defects: offline reuse can replace an accepted inventory with a smaller one, and legacy reuse omits gaps reopened by quarantine. The three-branch integration has a further shared-frozen-T compatibility blocker. There are also two should-fix items below. None requires increasing extraction strictness or making another paid call.

I performed this review myself, without delegation or paid calls. Mu, xi and eta source branches were not edited. Mutation tests and merge resolutions are confined to separate scratch clones.

## Blocking findings

### B1 — Offline snapshot selection can silently lose accepted items

**Mu `ara/runtime/extraction.py:578–585`, `resume_papers`.** `revalidate_only=True`, used by `--salvage-only`, disables the differing-outcome guard. Each later completed outcome overwrites `reused[source]`, without checking that its inventory contains the earlier accepted evidence. Selection follows receipt/input order, not an evidence-union or monotonic-superset rule.

I reproduced this through native extraction, provenance import, resume and publication using placeholder sources: an earlier eight-item accepted graph followed by an independently accepted one-item graph publishes only the latter item. Seven previously accepted IDs are absent. Both original runs are valid; this is not a malformed-artifact test. The current real 2,333-item artifact passes the retention comparison, so this probe establishes an exposed path, not seven missing items in that artifact.

Before merge, preserve the union of differing accepted snapshots with explicit identities/references, or refuse a non-monotonic replacement explicitly. A smaller or conflicting snapshot must not silently become the whole paper. Add a production-path regression covering multiple verified completed snapshots and their ordering.

Evidence: `omicron-evidence/test_review_probes.py::test_offline_latest_snapshot_drops_previously_accepted_items`; `review-probes.txt`. This probe passes by confirming the defect.

### B2 — Two real legacy gaps reopened by quarantine are not disclosed

**Mu `ara/runtime/extraction.py:249–253` and `ara/runtime/export.py:65`.** `literature_entry` computes `open_gaps` and publishes dispositions only for outcomes with `range_union_policy`. The reused v4 outcomes retain their old shape, without this marker. Methodology also filters its limitations inventory by that marker.

The current real `yalcin2007` outcome has five historical obligations. Two resolutions now depend on quarantined evidence. They therefore reopen under the implemented policy, but the published paper has no `open_gaps` field and the methodology limitations inventory omits that paper. The artifact discloses 16 gaps; projecting quarantine-aware resolutions over all retained outcomes gives 18. A separate placeholder probe confirms the legacy branch omission.

Before merge, give revalidated legacy outcomes the same quarantine-aware gap/disposition publication treatment. Preserve original acceptance identities and receipts, and preserve historical artifact verification: changing how every old outcome is assembled indiscriminately can invalidate old artifact hashes. Test actual legacy reuse, republication and a second resume, not only a new outcome already carrying `range_union_policy`.

Evidence: `legacy-gap-inventory.json`, `expected-gap-counts.json`, `corpus-audit.txt`, and `test_review_probes.py::test_legacy_resolved_gap_not_reopened_in_publication`.

### B3 — The integrated shared-frozen path does not accept this reused lineage

**Integrated `ara/runtime/response_contracts.py::compatible_prompt`, `ara/runtime/frozen.py:57–60,139–143`, and the legacy contract manifests.** Eta's retained prompt archive recognizes one pre-mode-specific extraction template. It does not cover the reviewed extraction contracts present in mu's real reused corpus. At the resolved integration head, 151 of its 154 inherited MODEL receipts fail prompt compatibility: 73 accepted, 76 rejected and two incomplete extraction receipts. Three pass. Calling the native `verify_receipts` on this verified lineage refuses with `frozen T: schema/prompt version drift: extract_paper`.

There is a second known prerequisite: the same lineage includes two `reservation_unknown_actual` receipts. Eta explicitly refuses those before shared-T import, whereas the extraction campaign carries their disclosed reservation accounting. Fixing the prompt archive alone will not make this corpus shareable. Resolve the supported inherited-accounting policy explicitly; do not relabel reservations as measured charges or remove receipts.

The merged suite also fails two compatibility tests:

- `tests/integration/test_shared_frozen.py::test_legacy_freeze_and_budget_campaign`: `config/schema-version drift`; the fallback frozen manifest pins the older extraction schema.
- `tests/runtime/test_shared_frozen_theta.py::test_retained_legacy_accepted_and_rejected_attempts[None]`: `schema/prompt version drift: extract_paper`.

These tests need faithful, pinned legacy fixtures: the second currently constructs a “legacy” prompt using today's schema, and the first removes contract metadata from a newly built table. Their failures alone do not prove that an arbitrary older T should be accepted. The independent real-receipt check establishes the operational incompatibility. Preserve the new live contract, archive and verify the specifically supported historical contracts, settle legacy frozen-table compatibility, and rerun both files plus the integrated suite.

This blocks the combined shared-frozen workflow. The initial pilot literature import works, as separately verified below. No real-corpus frozen builder was created here, so I do not claim an end-to-end `load_frozen` execution on that corpus.

Evidence: `shared-contract-audit.txt`, `merged-pytest.txt`, `merged-failing-files.txt`.

## Should-fix findings

**S1 — Retarget one merged mutation anchor.** The schema-helper conflict resolution moves mu's schema logic into eta's `response_contracts.py`. The combined registry still points `disposition_wire_separation` at `ara/runtime/calls.py`, where its anchor occurs zero times. Static enumeration finds 279 combined controls and exactly this one missing anchor. The merged runner would stop at its anchor assertion; it was not run. Move this control to the owning helper while preserving its behavioral target. Evidence: `merged-control-anchors.json`.

**S2 — Update conflicting usage wording.** Mu's `README.md:434` still says targeted corrections accept only 0, 1 or 2; the implementation supports 3. `assemble`'s general `use` text still describes inference links as paper-stated, while its new acceptance note correctly allows reconstructed links. Update both so consumers receive one consistent contract. These are wording defects, not reasons to reject reconstructed inference evidence.

## Range union, reconciliation and reuse

Within a fresh extraction, accepted ranges survive later range failures and the one bounded reconciliation attempt. Reconciliation appends accepted additions; it cannot redeclare immutable evidence. Admission refusal, invalid output, context requests and provider failure become disclosed limitations. Unresolved obligations remain open rather than triggering an unbounded queue. Thin ranges get the bounded split retry and retain their original items. The relevant owning tests passed. B1 is a separate completed-snapshot selection hole; B2 is a legacy publication hole.

The v5 relaxation is substantive: reconstructed origins are retained, range-level inference quotas are removed, and a zero-inference union is disclosed as unverified. That last behavior is broader than the original explicit-no-inference-disposition request but is consistent with the later approved range-union addendum. The current round-2 acceptance identity is **v6**, not v5: evidence eligibility became stricter through quarantine while the original structural inventory remains retained. It would be misleading to call v6 evidence eligibility a strict relaxation of v4.

V4/v5 reuse is real validation, not relabeling. The code pins reviewed prompt/schema hashes and effective profile/source identity, validates graph schema, references, locators, attribution presence, citation identity and resolution references, checks accepted graph receipts, then recomputes grounding from physical-page text. Migration receipts preserve original acceptance identities. The legacy test fixtures that merely substitute a v4 identity into a newly generated outcome do not exercise the missing legacy publication marker in B2. Unknown contracts are not admitted by a version string alone. My network-blocked corpus audit verified the artifact's pinned provenance and recomputed every quarantine inventory; all **2,333 original item bodies remain exactly equal by ID** to the pre-grounding artifacts, including all seven v4 completions.

Reversed physical endpoints are sorted and logged before bounds/readability checks. Duplicate correction IDs receive stable fresh IDs without deleting items. Identical duplicates leave references on the first definition; distinct referenced duplicates are refused as ambiguous. Replay stability, reference preservation, out-of-bounds refusal and third-correction handling are exercised by the owning tests. These repairs do not infer missing source content.

## Grounding, quarantine and false positives

The independent structural audit reproduced **245/2,333 quarantined**, leaving **2,088 eligible**. There are 200 direct flags and 45 dependent exclusions: 132 insufficient-overlap flags, 67 template-prefix flags and one short item also equal to its attribution. All 57 literal placeholder-prefix items are excluded. Every eligible item's explicit references avoid quarantined IDs. Inference links and dependent qualifiers propagate quarantine; resolutions relying on quarantined items reopen gaps, subject to B2's publication defect.

| Paper | Retained | Quarantined | Eligible |
|---|---:|---:|---:|
| vonfintelgillies2007 | 100 | 21 | 79 |
| eganweatherson2011 | 125 | 10 | 115 |
| vonfintelgillies2011 | 147 | 13 | 134 |
| wright2007 | 105 | 17 | 88 |
| schaffer2011 | 194 | 21 | 173 |
| braun2012 | 108 | 31 | 77 |
| eganhawthorneweatherson2005 | 213 | 14 | 199 |
| egan2007 | 158 | 12 | 146 |
| macfarlane2011 | 169 | 17 | 152 |
| yalcin2007 | 210 | 10 | 200 |
| yalcin2011 | 85 | 22 | 63 |
| rothschild2012 | 71 | 1 | 70 |
| moss2015 | 239 | 11 | 228 |
| veltman1996 | 267 | 31 | 236 |
| kolodnymacfarlane2010 | 84 | 13 | 71 |
| knobeyalcin2014 | 58 | 1 | 57 |
| **Total** | **2,333** | **245** | **2,088** |

The threshold is reasonable as a **provisional lexical screen** under the requested practical bar: at least 50% distinct normalized content-token overlap, with at least three matches or all tokens when fewer than three exist. I independently reproduced the direct-flag sensitivity curve: 35% → 116, 40% → 132, 50% → 200, 60% → 336, 70% → 590. There are 38 non-junk items at 45%–below 50%, and 32 exactly at 50%. Citation spans are 1,605 single-page, 690 two-to-five-page, and 38 longer spans; overlap across a broad citation is not a quotation match.

I read the eight anonymized boundary records. Mu classifies three of four below-threshold examples as supported paraphrases and one as contaminated; all four at exactly 50% are classified as supported. Those are the author's semantic judgments on a deliberately selected sample, not my independent semantic audit and not a population false-positive estimate. The structural scores reproduce. Do not report a 75% corpus false-positive rate, or treat 2,088 eligible items as 2,088 semantically verified claims. Unsupported text using the same vocabulary may pass, and supported paraphrase may fail. No threshold adjustment is required for this review's merge bar.

Evidence: `corpus-audit.txt`, `threshold-audit.json`, and mu's ignored `runs/mu-round2/anonymized-spot-check.json`. No philosophical source text is reproduced here. Earlier thinness, unread-page/encoding limitations and zero eligible inferences in `yalcin2011` remain limitations; quarantine does not repair extraction completeness.

## Publication roster and pilot import

The current artifact has **53 records**, 16 nonempty graphs and **37 explicit roster entries**: one excluded source, nine not extracted, and 27 record-only/not-extracted records. Each roster entry has a reason. Excluded entries supply no evidence. The native construction path passes the roster to selection/formalization and filters quarantined items before either stage; citation lookup also filters them and refuses ungrounded or altered inventories.

My additional placeholder probe executed the native CLI path **extract → run → freeze → methodology**, using only a mock provider. It verified that the excluded source and quarantined premise/dependent inference never enter T, that construction inputs carry the roster, and that downstream methodology retains both the roster and quarantine count. This adds actual pilot-import proof to the read-only real-artifact audit. It is not a paid or semantic real-corpus pilot.

## Integration execution

Pinned inputs, merged in the requested order from `0eb85924afeb01aac44e5bc0ca5f2714c6a99823`:

| Lane | Exact head |
|---|---|
| mu | `95be49ad754f1dd113191486e6946749d5f9a2c0` |
| xi | `56039948c34b104f15bab13b455fadcc050c9c2d` |
| eta | `185a318a7fa5a46485a375ee1cb26244c2254403` |

Scratch clone: `/home/dev/ara-work/omicron-integration`; tested resolved head **`88a09132da5f840b71550db9996bfc5263fbea9b`**. No source branch was merged or changed.

| Merge | Conflict file | Scratch resolution |
|---|---|---|
| mu | none | Fast-forward from the requested base |
| xi | `DECISIONS.md` | Retain both appended decision histories |
| xi | `tests/integration/negative_controls.py` | Retain both appended control sets |
| eta | `DECISIONS.md` | Retain both appended decision histories |
| eta | `README.md` | Retain both documentation additions |
| eta | `ara/runtime/calls.py` | Keep eta's shared response-helper entrypoints; transfer mu's complete schema and prompt behavior into `response_contracts.py` |
| eta | `tests/integration/negative_controls.py` | Retain both control sets; S1 records the remaining moved-anchor adjustment |

Thus the unique conflict files are **`DECISIONS.md`, `README.md`, `ara/runtime/calls.py`, `tests/integration/negative_controls.py`**. Automatic merges in construction, export, CLI and orchestration do not by themselves prove semantic compatibility; the suite and native probes supply the evidence above. Merge logs and the contract-resolution patch are in `omicron-evidence/`.

## Executed verification and limits

- Mu at the requested head: **548 passed, 2 skipped / 550**, `uv run --offline --frozen pytest -q`, 304.96 seconds. Skips are opt-in provider checks. Transcript: `mu-pytest.txt`.
- Mu control runner: **234/234 mutations returned exit 1; all restored tests returned exit 0; runner exited 0**. Started only after the full mu suite exited successfully, at the same commit in `/home/dev/ara-work/omicron-controls`. The runner's temporary mutations do not touch the reviewed checkout. Transcript: `mu-controls.txt`; results: `mu-control-results.json`. Final tracked checkout is clean.
- Three-branch resolved head: **631 passed, 2 failed, 2 skipped / 635**, full suite, 434.11 seconds. Both failures are listed in B3. Transcript: `merged-pytest.txt`.
- Failing integration files rerun on the unchanged resolved head: **30 passed, the same 2 failed / 32**, 92.89 seconds. Transcript: `merged-failing-files.txt`.
- Additional native probes: **3 passed**. Two confirm the identified defects; one verifies the pilot roster/quarantine path. This is not a claim that B1/B2 are fixed.
- Real-artifact provenance, exact retention, quarantine recomputation, dependency exclusion and threshold counts: passed with sockets blocked and no source-run writes. The separate integrated receipt audit refuses as described in B3.
- No paid calls, extraction, schema preflight or real-corpus construction/search were performed. This review provides no live-provider or semantic-completeness verdict. No unrelated Buckeye/JavaScript gate applies to this Python checkout.

I directly read more than five extraction mutation definitions, including reversed endpoints, duplicate-ID repair, v4 graph revalidation, range retention, open-gap projection, overlap threshold, quarantine propagation and construction filtering. I also read the actual red/restored transcripts for those controls. Disabling range retention removes all 16 expected items; disabling quarantine propagation leaves its dependent inference eligible; disabling the construction filter admits quarantined IDs into T; disabling gap reopening falsely closes the test gap. Each restored target passes. Selected transcripts are copied to `inspected-controls/`. Two additional controls (`extraction_page_bounds` and `extraction_no_record_only_t`) turn red because the refusal message changes while another safeguard still rejects the input; the aggregate control count is therefore test sensitivity, not 234 independent demonstrations of an unsafe outcome. Final revisions, exit statuses and clean-tree checks are recorded in `verification.json`.

All evidence paths above are relative to `/home/dev/ara-work/reports/omicron-evidence/` unless explicitly qualified. Continuation state is in `work-notes.md`.

## Finding placement

| Finding | Placement |
|---|---|
| 1 — Accepted completed-snapshot replacement can lose evidence | B1 |
| 2 — Legacy quarantine reopens two undisclosed real gaps | B2 |
| 3 — Shared-frozen historical contracts/accounting are incompatible; two merged tests fail | B3; Integration execution; Executed verification |
| 4 — One moved integration mutation anchor remains stale | S1 |
| 5 — Correction-count and inference-origin wording conflict with behavior | S2 |
| 6 — Bounded range union preserves accepted range/review additions but does not establish completeness | Range union, reconciliation and reuse |
| 7 — V4/v5 reuse performs actual validation; v6 narrows eligibility and preserves original inventories | Range union, reconciliation and reuse |
| 8 — Content-free repairs preserve references and reject ambiguity | Range union, reconciliation and reuse |
| 9 — Quarantine counts reproduce; threshold has disclosed false-positive/semantic limits | Grounding, quarantine and false positives |
| 10 — Roster and quarantine survive native initial pilot import | Publication roster and pilot import |
| 11 — Exact revisions, conflicts, executed checks and remaining proof limits | Integration execution; Executed verification and limits |

11 findings, 11 placed.

DONE omicron review mu=fix-first blocking=3 should_fix=2 integration=conflicts:DECISIONS.md,README.md,ara/runtime/calls.py,tests/integration/negative_controls.py merged_tests=631/635

## Re-review

**Recommendation: merge mu and rebased xi; 0 in-scope blockers.**

This section supersedes the original merge recommendation for **mu plus rebased xi only**. Eta/shared-frozen compatibility (B3) is explicitly deferred until after tonight's pilot by the re-review brief. It is not fixed or included in this verdict.

### Mu: B1, B2 and S2

Reviewed `514bae3ade119ae03533a00a3b976a01086aa1cd` against `95be49a`. No additional design blocker found in the six-file patch.

- **B1 fixed by explicit refusal.** Before importing provenance, an offline replacement must preserve every prior accepted item ID and exact body. Smaller, disjoint and changed-body snapshots refuse with a non-monotonic replacement error; growth preserving all earlier evidence remains usable. Ordering is deliberately strict, as disclosed. This meets the authorized refuse-or-union alternative; it is not a claim that arbitrary snapshots are automatically unioned. The native regression covers all four cases, including an empty destination after refusal.
- **B2 fixed by versioned republication.** New outcomes and revalidated legacy outcomes carry `publication_policy=quarantine-aware-v1`. Literature and methodology use the same marker to expose dispositions and gaps reopened by quarantine. Historical unmarked outcomes retain their original serialization; original acceptance identities and graph receipts remain intact. Native tests cover ungated and already-grounded historical shapes, republication and a second resume, no generation, and repeated original-artifact verification.
- **S2 fixed.** README permits 0–3 targeted corrections and paper-stated or reconstructed links. New publication usage text agrees. Old wording is retained only to reconstruct historical bytes. Current acceptance remains **v6**; the v5 relaxation is correctly described as historical. No prompt, schema or grounding-threshold change occurred.

### Independent real-artifact audit

The socket-blocked, read-only audit passed for `mu/runs/mu-round3-final-offline/literature.extracted.txt`: **2,333 retained, 245 quarantined, 2,088 eligible, 18 open gaps, 37 roster entries**. Every original item body is unchanged by ID. All 16 nonempty graphs pass current-contract reuse validation. Recomputed quarantine, eligible dependency references, gaps and dispositions agree with publication and methodology. The two formerly hidden `yalcin2007` gaps are present. The three historical artifacts (`mu-roster-proof`, `mu-eight-live`, `mu-round2-offline`) still pass exact provenance/hash verification. Local generation and cost are zero.

Use **`mu-round3-final-offline`**, not the diagnostic `mu-round3-offline`. Mu reports that the first diagnostic publication omitted the 84-item partial graph because its intermediate v6 prompt identity was incompatible. The final artifact recovers the original accepted ranges under the current validator. My independent audit confirms the recovered inventory and current reuse compatibility; it does not waive the prompt-identity check or claim a second full-corpus publication.

Evidence: `omicron-rereview-evidence/publication-audit.json`, `publication-audit.txt`, and `audit-publication.py`.

### Xi rebase and conflict resolution

Final head reviewed: `070efb7bc5ed83d7b5528a42813a57b388751eb2`, based on mu `514bae3`; pre-rebase xi was `773e262f64f7f51f1e0188020ca3f242675613b3`. Xi’s final `DONE xi round3` line names exactly this head and base, with 603/605 tests and controls passing. I checked that receipt after completion; it matches the independently tested clone.

The rebase conflicts are only append collisions in `DECISIONS.md` and `tests/integration/negative_controls.py`. Both histories/control groups survive. Mu's extraction, calls, grounding, reconciliation, salvage, export, prompt/schema and republication-test files are byte-identical to mu's head. Xi's reporting/tracing implementation and owning tests are byte-identical to its pre-rebase head, including the R1 trace-consistency fix. The range-diff shows only context/whitespace changes to earlier replayed commits and an unchanged R1 patch. CLI adds the offline report entrypoint; orchestration adds the native trace sink; README appends report documentation without reverting mu wording.

All **257 control names are unique**, every production anchor occurs exactly once, and all **237 mu control definitions remain unchanged**. The original S1 stale-helper anchor is absent in this mu+xi scope: eta's helper refactor is not included. This does not claim to repair the deferred three-branch merge.

Evidence: `xi-range-diff.txt`, `xi-rebase-audit.json`.

### Verification and verdict

All re-review evidence is under `/home/dev/ara-work/reports/omicron-rereview-evidence/`.

| Check | Result | Executor/evidence |
|---|---|---|
| Mu full pytest at `514bae3` | 554 passed, 2 skipped / 556; exit 0; 307.45 s | Independent rerun; `mu-pytest.txt` |
| Mu control runner, sequential after that pytest | 237/237 red under mutation and green restored; runner exit 0 | Independent rerun in isolated clone; `mu-controls.txt` |
| Xi full pytest at final rebased head | 603 passed, 2 skipped / 605; exit 0; 342.22 s | Independent isolated rerun; `xi-pytest.txt` |
| Xi full controls, sequential after its author pytest | 257/257 red under mutation and green restored; all 514 transcript summaries and 22 before/after file hashes verified | Author execution, independently verified against exact-head receipts, committed source hashes and restored results; `xi-control-receipt-audit.json` |
| Xi’s 20 added controls | 20/20 red under mutation and green restored; runner exit 0 | Independent isolated replay after xi pytest; `xi-added-controls.txt`, `xi-added-control-results.json` |
| Artifact audit and rebase/anchor comparison | Passed | Independent checks described above |

Paid-provider tests were skipped. No paid calls, source-branch edits, push, delegation, real-corpus construction/search or semantic audit occurred. The prior lexical false-positive/completeness limits remain. B3 is deferred, not counted as a current blocker or represented as fixed. Final head/restoration checks and exit receipts are in `verification.json`.

The new mu controls and the independently replayed xi R1 controls were also inspected directly: removing each boundary reproduces the reported loss/disclosure or false-completeness failure; restored tests pass. Selected transcripts are in `inspected-controls/`.

### Re-review finding placement

| Finding | Placement |
|---|---|
| R1 — Snapshot-loss finding B1 is closed by explicit non-monotonic refusal | Mu: B1, B2 and S2 |
| R2 — Legacy-gap finding B2 is closed without invalidating historical artifacts or second resume | Mu: B1, B2 and S2; Independent real-artifact audit |
| R3 — S2 wording and current v6 identity are correct | Mu: B1, B2 and S2 |
| R4 — Corrected final corpus retains 2,333 items/18 gaps; diagnostic artifact must not be used | Independent real-artifact audit |
| R5 — Rebase preserves both behaviors and all mutation anchors | Xi rebase and conflict resolution |
| R6 — Exact-head test/control results and executor distinction | Verification and verdict |
| R7 — Eta B3 remains explicitly deferred; old S1 does not occur in this integration scope | Opening; Xi rebase and conflict resolution; Verification and verdict |
| R8 — No paid/source edits and no semantic or real-pilot verdict | Verification and verdict |

8 findings, 8 placed (re-review; the original 11 findings remain above with their historical scope).

DONE omicron rereview mu=merge xi_rebase=merge blocking=0 tests=603/605 negctl=pass
