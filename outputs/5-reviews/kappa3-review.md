**Kappa3 non-author review — merge both changes together; no blocking defect established.** Reviewed Sigma `2d713e99743453f4746dd5324cd3832ccb241d64` and Xi `c187128180aa71229c812a8900da66523886a3ef`, each against `5b512de4ef37264fe3ac3fa8bbfe2a19e48606b8`. This was a direct review without delegation, paid calls, or edits to either author branch. The conclusion covers the pinned implementation and offline behavior, not a successful real-corpus pilot.

**Sigma — content definitions and exact provenance.** The new construction response requires a content `definition` for each commitment. Both commitment text and symbol definitions are screened with the shared attribution lexicon. Attribution, source identity, speaker, pages, evidence ID, stance, exact source text, and omitted-support IDs are retained separately in the hash-bound provenance sidecar. Citations are copied from the immutable evidence. `author_claim`, `reported_view`, and `attacked_view` map to endorsed, reported, and attacked; contradictory reported/attacked kind tags refuse. The sidecar binds the exact frozen T and catalogue and is logged before the freeze.

I traced the real correction and freeze paths in [construction.py](/home/dev/ara-work/sigma/ara/runtime/construction.py:515), [commitment_provenance.py](/home/dev/ara-work/sigma/ara/runtime/commitment_provenance.py:20), and [orchestration.py](/home/dev/ara-work/sigma/ara/runtime/orchestration.py:106). The independent end-to-end probe deliberately supplied `According to a, P` as a definition. Native validation rejected it, logged one targeted correction, accepted the corrected content, and preserved the original source sentence and citation. The merged suite also exercises symbol-definition correction, exhausted correction refusing freeze, source/stance preservation, and metadata tampering.

**Xi — asserted content, source stance, and unchanged logical gates.** The classifier receives target text and a structural formula rendering through verified content definitions, with T/catalogue/provenance hashes binding cache identity. Source prose and attribution are excluded from that assertion payload. The deterministic attribution screen remains on the target text. All eleven named Phi2 attribution probes still reject even when the fake classifier returns `own_thesis`; the own-voice placeholder target is accepted.

Native search retains the complete frozen context for proposals and formalization, but only endorsed commitments can close global premises or support critical-question answers. The same eligible subset governs forward/conflict analysis. Reported and attacked content can remain scoped hypotheses under bank-licensed assumption rules; attacked P is never automatically asserted as not-P. Historical stance-crossing routes are disclosed as `CLOSED-stance-crossing` and excluded from default selection. Explicit historical route selection remains possible, with source roles in the writer/auditor outline and prompts requiring qualification; faithful prose is still a model-audited obligation.

I inspected these paths through proposal, engine closure, CQ checks, report/export, selection, fork, and resume. The bounded contribution solver, formal entailment, bank licensing, and terminus modules are byte-unchanged against the base; the route's two-distinct-support requirement remains in place. Five independent duplicated-premise, tautology, and opposite-polarity probes also reject. Source and comparison receipts: [scope-and-preservation.json](/home/dev/ara-work/reports/kappa3-evidence/scope-and-preservation.json).

**Integration — two additive conflicts resolved in scratch.** Sigma was merged first, then Xi, onto the requested base in `/home/dev/ara-work/kappa3-integration`. The merge conflicted in `DECISIONS.md` and `tests/integration/negative_controls.py`. I retained both appended decision sections and every control case. No production resolution edit or implementation fix was needed. The resulting tested merge is `b48d56f97286199cbd144fc441b2d92837bfdda9`. The final status deliberately reports conflicts rather than calling the original merge clean. Both author checkouts retain their pinned heads and clean status.

**Executed verification — native offline path, full suite, then controls.** In the independent probe, fake PDF extraction produced two sources: P and P -> Q. The real rich construction, correction, freeze, target proposal/classification, solver preflight, bank-licensed search, analysis, route publication, and default-selection filter ran. Q requires both commitments; the recorded solver checks rule out zero/single support in either polarity.

| Required premise P's source stance | Target preflight | Search outcome for Q | Default-selectable routes |
| --- | --- | --- | --- |
| Endorsed | Accepted | `CLOSED-derived`; two supports from two sources | One route |
| Reported | Accepted | `OPEN`, with `STANCE_CROSSING` | None |
| Attacked | Accepted | `OPEN`, with `STANCE_CROSSING` | None |

The opposite polarity remained open in all three cases. Report generation and methodology export preserve the classifications and provenance; native search resume restores both jobs in every case. The probe forbids socket connections and uses only fake provider responses. [Probe script](/home/dev/ara-work/reports/kappa3-evidence/e2e_probe.py), [successful summary](/home/dev/ara-work/reports/kappa3-evidence/e2e-v3/summary.json), [endorsed receipt](/home/dev/ara-work/reports/kappa3-evidence/e2e-v3/endorsed/receipt.json), [reported receipt](/home/dev/ara-work/reports/kappa3-evidence/e2e-v3/reported/receipt.json), [attacked receipt](/home/dev/ara-work/reports/kappa3-evidence/e2e-v3/attacked/receipt.json), and [report/resume receipts](/home/dev/ara-work/reports/kappa3-evidence/e2e-v3/consumers.json).

At the committed merge, `uv sync --locked --offline` succeeded. `uv run --offline pytest -q` exited 0: **1,153 passed, four skipped / 1,157 collected**, in **947.72 seconds**. The four skips are two opt-in paid-provider tests and two installed OCR/VL-weight tests.

Only after pytest exited, `ARA_LIVE_TEST=0 UV_OFFLINE=1 TMPDIR=/dev/shm/kappa3-controls uv run --offline python tests/integration/negative_controls.py` ran to completion, exit 0: **493/493 mutations produced pytest exit 1, and all 493 restored checks exited 0**. The controls took approximately 34 minutes. All **219 tracked files** match their pre-control hashes, and `git status --short` and `git diff --check` are clean. No production repair was applied or needed.

Evidence: [pytest receipt](/home/dev/ara-work/reports/kappa3-evidence/pytest-receipt.json), [full pytest log](/home/dev/ara-work/reports/kappa3-evidence/pytest.log), [control receipt](/home/dev/ara-work/reports/kappa3-evidence/controls-receipt.json), [control log](/home/dev/ara-work/reports/kappa3-evidence/controls.log), [all red/restored results](/home/dev/ara-work/reports/kappa3-evidence/controls/results.json), and [final preservation check](/home/dev/ara-work/reports/kappa3-evidence/final-verification.json).

The reviewer probe required two harness corrections: using `Paper.source_id`, and separating caches when intentionally changing fake responses for independent scenarios. Earlier failed transcripts remain in the evidence directory; the complete successful run is `e2e-v3`. Neither issue required a production change.

**Next pilot and limits.** These changes must be integrated together. Reconstruct and freeze T from the retained rich extraction: an old frozen-prefix fork preserves the old attributed definitions and does not acquire content semantics merely by running this code. An own-thesis verdict with legacy null definitions does not establish that the frozen atom meanings have been repaired. Refresh the Codex schema preflight for the changed `build_t_batch_v5` schema before a live run. No live preflight, corpus reconstruction, real-model classification, essay, or useful real-corpus synthesis was performed in this review.

The shared lexical validator is a bounded heuristic. Independent checks show it accepts `P accepts Q` and `In P's opinion, Q`, while rejecting content containing `accounts`. Thus it neither proves attribution-free content nor general target-classifier accuracy. Review actual generated definitions, stance labels, and classification reasons in the pilot; the fake responses here prove the integration contract. [Lexicon boundary receipt](/home/dev/ara-work/reports/kappa3-evidence/lexicon-boundary.json).

Native literature publication can omit bibliographic author records, leaving `source_authors=[]`; `source_id`, `attributed_to`, source text, and citations remain exact, and supplied author metadata is preserved. This pre-existing publication limitation is disclosed by both authors and exercised by Sigma's absent/supplied-author regression. Do not interpret an empty author list as proof that a source has no authors. Legacy runs without the new sidecar retain legacy premise eligibility with stance explicitly unavailable; recorded missing or corrupt provenance refuses rather than silently downgrading. Content fidelity and extraction stance accuracy remain semantic judgments. A two-source formal witness establishes neither originality nor independence of the source claims.

**Finding placement.** No blocking implementation findings; the six action-relevant review observations are placed as follows.

| Observation | Placement |
| --- | --- |
| 1. Content definitions, correction, exact source text/citations, and provenance binding | Sigma |
| 2. Asserted-content classification, stance enforcement, solver gates, historical selection qualification | Xi |
| 3. Merge conflicts, resolution, tested revision, author-branch preservation | Integration |
| 4. Independent native end-to-end proof, report/resume consumers, full suite and controls, harness corrections | Executed verification |
| 5. Fresh construction/freeze and current schema preflight required for the next pilot | Next pilot and limits |
| 6. Lexicon/model limits, absent author metadata, legacy behavior, and meaning of the formal witness | Next pilot and limits |

6 findings, 6 placed.

DONE kappa3 sigma=merge xi=merge blocking=0 integration=conflicts:DECISIONS.md,tests/integration/negative_controls.py merged_tests=1153/1157 e2e_derived=yes
