# Phi2 review — fix-first

Review target: `/home/dev/ara-work/xi`, branch `feat/run-report`, head `9f07ba0a50df2802d56302134f85e4a896a23dd6`, base `main` at `6511ff6cb2bb5d88c5abedc1f20b715a03324d0f`. **Verdict: fix-first, two blocking findings.** This non-author review reproduced ways for one-premise restatements and explicit attributed reports to pass the new gates and become default selections. Full pytest and all mutation controls pass; the real-run offline fork also passes. The original branch was not edited. Work was performed by this reviewer without delegation or paid calls.


**B1 — Blocking: one-commitment restatements pass preflight and become default selections.** [target_policy.py:54](/home/dev/ara-work/xi/ara/runtime/target_policy.py:54) checks canonical equality and a limited direct-instance matcher; `minimum_support_commitments=2` is only a prompt input. With frozen `P` and `P -> Q`, the real `ModelCalls.propose_targets` accepts `P and P`. Native search licenses conjunction introduction using `t1` twice, returns `CLOSED-derived`, and `selectable_routes` offers it. More directly matching the brief's adversarial case, `P and (Q -> Q)` passes and closes through licensed conjunction introduction plus conditional proof; its only external support is still `t1`. Neither candidate needs two distinct commitments. An inference-count label therefore does not prevent the fork pilot from becoming trivial again. Add a bounded single-commitment entailment/equivalence or contribution gate, cover tautologies and duplicated premises, and enforce/disclose the support requirement before default selection. Preserve bank licensing; do not solve this by relabeling a valid inference as unlicensed.

There is also a concrete direct-instance coverage hole in the same preflight: `forall x forall y F(x,y)` matches `forall y F(a,y)` but fails to match `forall z F(a,z)`. [target_policy.py:15](/home/dev/ara-work/xi/ara/runtime/target_policy.py:15) compares bound variable names literally. Renaming a bound variable preserves meaning. Cover alpha-equivalence in the structural matcher or the bounded logical check. This particular case was tested at the matcher boundary; a closed native route for it is not claimed.

Evidence: [probes.json](/home/dev/ara-work/reports/phi2-evidence/probes.json), [duplicate-conjunct graph](/home/dev/ara-work/reports/phi2-evidence/duplicate_conjunct-routes.json), and [tautology.json](/home/dev/ara-work/reports/phi2-evidence/tautology.json). The latter records the two `BANK_LICENSED` rules and the single support ID. Reproduction scripts are [probes.py](/home/dev/ara-work/reports/phi2-evidence/probes.py) and [tautology_probe.py](/home/dev/ara-work/reports/phi2-evidence/tautology_probe.py); run with `PYTHONPATH=/home/dev/ara-work/xi:/home/dev/ara-work/xi/tests/runtime /home/dev/ara-work/xi/.venv/bin/python <script>` using fresh scratch directories.

**B2 — Blocking: common explicit attributed reports are admitted as own theses.** [target_policy.py:63](/home/dev/ara-work/xi/ara/runtime/target_policy.py:63) rejects a small verb list but accepts `P believes that Q`, `P defends Q`, and `Q is P's view`. The first was run through real proposal validation and native search: modus ponens licenses its stored `Q` formula from `P` and `P -> Q`, and the attributed text is offered as `CLOSED-derived`. This reproduces the prohibited report-of-a-source experience even when there are two premises and a valid formal inference. Exact formula-copy rejection cannot protect targets whose formula is otherwise derivable. Strengthen attribution validation and retain an explicit unresolved/rejected disposition when own-thesis status is not established; add these production-path regressions. A regex pass must not serve as approval that the target is the system's own thesis.

Evidence: [probes.json](/home/dev/ara-work/reports/phi2-evidence/probes.json), [attributed graph](/home/dev/ara-work/reports/phi2-evidence/missed_believes-routes.json). The test provider deliberately supplies the text/formula pair; this demonstrates acceptance, not fidelity of that pair or a frequency claim about real model outputs.

**Context and renamed symbols.** Canonical-equal and double-negated copies are rejected, as is `P argues that Q`. Proposal input includes the full frozen commitments, conditionals, shared signatures and validated symbol catalogue. The prompt explicitly asks for own theses and two distinct commitments. The separate `F(a)` to `F(b)` probe is accepted. That alone is not a logical-equivalence defect: distinct constants can denote different objects, and the probe supplies no alias relation. Semantic renaming and genuine originality remain unproved; the positive guard tests do not establish either.

**Classification and selection.** On the native path, [search.py:149](/home/dev/ara-work/xi/ara/engine/search.py:149) rejects unlicensed proposals before it creates inference nodes. `route_classification` checks a reachable inference with a proposal in a CLOSED engine graph; default smoke and interactive selection restrict choices to `CLOSED-derived`, while trivial/open routes remain disclosed and need explicit `--route`. The label's licensed-step meaning is sound on this reviewed native path. It is not a contribution or multiple-source guarantee, as B1 proves. The classifier itself does not independently authenticate arbitrary externally supplied graph objects.

**Fork evidence — passed offline.** The actual `/home/dev/ara-scaffold/runs/codex-pilot-3` source forked into `/dev/shm/phi2-review/real-fork`. The copied prefix is exactly **6,813 events / 331,834,295 bytes**, ending at its single freeze; both `commitments.json` and `frozen-t.json` match byte-for-byte. No original post-freeze candidates/routes were copied. All **204 source files** retained their hashes and the source inventory was unchanged. Reusing the destination refuses with `fork destination must be empty`.

The preserved accounting is **15,645,797 tokens and USD 110.395145 of historical cost**, imported once. Reconstructing `Budget` twice keeps imported totals fixed and adds only the two fake 8-token responses (16 local tokens total). No new paid calls occurred. The fake provider proposed ten direct copies; both attempts rejected all ten, including the one allowed correction. It received **16 conditionals, 42 shared signatures and 140 catalogue entries** on each call. Native search publication then completed with zero accepted targets. This proves freeze reuse and rejection, not successful new thesis generation.

Execution used production `fork_from_freeze`, real `ModelCalls.propose_targets` and native `search_all` with socket connections forbidden. It used a disclosed fake profile: cleared stage overrides, a local byte/4 counter, raised local test allowances and the explicit `count-at-reservation` policy for historical unknown usage. It did not run a live Codex preflight or claim that the unmodified pilot configuration can dispatch offline. The CLI continuation and mismatch paths are covered separately by the repository's fake-source tests. The first review-script run had a wrong expected fake charge; the reviewer harness was corrected and the complete probe reran successfully. Production code was unchanged.

Evidence: [fork receipt](/home/dev/ara-work/reports/phi2-evidence/fork.json), [source hash manifest](/home/dev/ara-work/reports/phi2-evidence/source-before.json), [fork probe](/home/dev/ara-work/reports/phi2-evidence/fork_probe.py), [successful transcript](/home/dev/ara-work/reports/phi2-evidence/fork.txt). The large scratch fork is in volatile `/dev/shm`; these receipts and scripts are persistent.

**Tests and coverage — passed.** In an isolated clone at the exact reviewed head, `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline pytest -q` finished with **1,074 passed, 4 skipped / 1,078 collected** in **866.06 seconds**, exit 0. The skips are two opt-in paid-provider tests and two opt-in installed OCR/VL-weight tests. Only after that process exited, `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline python tests/integration/negative_controls.py` ran sequentially: **463/463 mutations caused the expected test failure, and all 463 restored runs passed**. The runner used `/dev/shm/phi2-review` for temporary test data. All **200 tracked files** in the control clone match their pre-run hashes, and both the control clone and reviewed checkout are clean. The reviewed checkout remains at `9f07ba0`.

The six fork-refusal cases cover chain tampering, anchor mismatch, commitments mismatch, catalogue corruption, duplicate freeze and bank mismatch, with destination/provider creation refused. Native CLI continuation is tested with fake source data. The green suite/controls do not cover the B1/B2 adversarial cases; those are supported by this review's separate native-path probes. No live schema preflight, real model target generation, essay or new real-corpus closure is claimed. The code-review skill's source/evidence approach was used; multi-agent and external-model review were omitted under the explicit single-worker instruction.

Evidence: [pytest transcript](/home/dev/ara-work/reports/phi2-evidence/pytest.txt), [pytest receipt](/home/dev/ara-work/reports/phi2-evidence/pytest-receipt.json), [control transcript](/home/dev/ara-work/reports/phi2-evidence/controls.txt), [control/restoration receipt](/home/dev/ara-work/reports/phi2-evidence/controls-receipt.json), [all red/green results](/home/dev/ara-work/reports/phi2-evidence/controls/results.json), [final preservation check](/home/dev/ara-work/reports/phi2-evidence/final-preservation.json). The control clone is `/tmp/phi2-review-NIELunXz/repo`; all review output is outside the reviewed branch.

**Finding placement.** Rows 1–2 are blocking defects. Rows 3–6 record the verification results and limits that affect the pilot decision.

| Finding | Placement |
|---|---|
| 1. One-commitment copies, tautology padding and renamed-bound-variable instance gap | B1 |
| 2. Explicit attributed-report bypass | B2 |
| 3. Supplied proposer context; renamed-constant and semantic-originality limits | Context and renamed symbols |
| 4. Native licensing/classification/default-selection guarantee and its limits | Classification and selection |
| 5. Exact real-prefix fork, immutable source, single accounting, fake-profile and CLI-proof limits | Fork evidence |
| 6. Full pytest, sequential controls, skips, restoration and remaining live-proof gaps | Tests and coverage |

6 findings, 6 placed.

DONE phi2 verdict=fix-first blocking=2 tests=1074/1078 negctl=pass fork_offline=ok

## Re-review

Reviewed `e7e12b42e3a76dfbbb6a71dbcfee2eac9f171b1d` against `9f07ba0a50df2802d56302134f85e4a896a23dd6`. **Verdict: fix-first, one new blocking finding.** The original named B1/B2 regressions are blocked at this head. A new report-generation failure prevents completion of the new single-support disclosure path. This section supersedes the earlier review's disposition for this revision; the earlier record is preserved. No branch edits, delegation or paid calls occurred.

**R1 — Blocking: reporting a redundant two-support closure crashes.** [report.py:290](/home/dev/ara-work/xi/ara/runtime/report.py:290) passes the route event's `polarity` explicitly to `dict()`, then expands `route_contribution`. For a route with two distinct supports where one alone entails the root, [route_policy.py:35](/home/dev/ara-work/xi/ara/runtime/route_policy.py:35) returns a triviality receipt containing another `polarity`. The result is `TypeError: dict() got multiple values for keyword argument 'polarity'`.

Two valid, natively licensed examples reproduce this through the actual `ara report` CLI: (1) derive `P` by modus ponens from `Q -> Q` and `(Q -> Q) -> P`; (2) derive `P and (Q -> Q)` by conjunction introduction from those two conjuncts as separate commitments. Their new classification is correctly `CLOSED-single-support`, and default selection excludes them, but reporting exits **2** and produces no `report.html`. A proper two-support `P, P -> Q |- Q` report exits **0**. All three report source logs remain unchanged. The fresh preflight blocks the two redundant targets; this regression affects reporting native-produced/previously saved routes that require the new disclosure, rather than proving a fresh guarded run will generate them.

Keep the contribution check's polarity in a distinct/nested field and preserve the route's original polarity. Simply changing to dictionary unpacking could silently replace a negation-polarity route with the check's local `target` polarity; the reproduction deliberately uses `polarity='negation'`. Add a report/CLI regression for both redundant-support examples. Evidence: [CLI results](/home/dev/ara-work/reports/phi2-rereview-evidence/report-cli.json), [reproduction](/home/dev/ara-work/reports/phi2-rereview-evidence/report_cli_probe.py), [consumer results](/home/dev/ara-work/reports/phi2-rereview-evidence/consumers.json).

**Prior B1 — the requested mathematical probes are blocked.** Independent fake-provider probes rejected all **18** adversarial target variants after the bounded correction, with contribution and own-thesis receipts logged. The classifier deliberately returned `own_thesis` for these tests, so deterministic exclusions had to do the work. I separately bypassed proposal admission to test the closure gate with valid native proofs:

| Probe | Preflight | Forced native closure / default selection |
|---|---|---|
| `P and P` | Rejected | `CLOSED-single-support`; excluded |
| `P and (Q -> Q)` with scoped tautology | Rejected | `CLOSED-single-support`; excluded |
| `P or (Q and not Q)` (`P ∨ ⊥`) | Rejected | `CLOSED-single-support`; excluded |
| Double negation inside `not not P and P` | Rejected | `CLOSED-single-support`; excluded |
| `(Q -> Q) -> P` from frozen `P` | Rejected | `CLOSED-single-support`; excluded |
| True antecedent explicitly in T: `Q -> Q`, `(Q -> Q) -> P`, target `P` | Rejected | `CLOSED-single-support`; excluded despite two distinct support IDs |
| `P and (Q -> Q)` using two frozen conjuncts | Rejected | `CLOSED-single-support`; excluded despite two distinct support IDs |
| `forall x forall y F(x,y)` to `forall y F(a,y)` or `forall z F(a,z)` | Both rejected; alpha hashes equal | Not dispatched after rejection |
| Canonical copy, outer double negation, zero-support tautology, and one-premise refutation | Rejected | Not dispatched after rejection |

The native positive control `Q` from `P` and `P -> Q` remains `CLOSED-derived` and default-selectable. The original renamed-constant diagnostic `F(a)` to `F(b)` remains admissible as a different formula but native search stays **OPEN**, with no default selection. No alias relation is supplied. Evidence: [probe results](/home/dev/ara-work/reports/phi2-rereview-evidence/probes.json), [probe script](/home/dev/ara-work/reports/phi2-rereview-evidence/probes.py), [CLI/render/report checks](/home/dev/ara-work/reports/phi2-rereview-evidence/consumers.json). Ten forced adversarial native closures in total (seven mathematical and three attributed) were excluded by the actual `select` CLI, without prompting or creating a provider.

**Prior B2 — named regressions fixed; semantic coverage remains model-dependent.** `believes that`, `defends`, `is P's view`, curly-apostrophe `P’s view`, and the original `argues` case are rejected even when the fake classifier says `own_thesis`. Forced native proofs for the first three receive `CLOSED-attributed-report` and are excluded from default selection. Classifier replies `attributed_report` and `unclear` reject an otherwise valid candidate; `own_thesis` permits the positive control. These dispositions, including cache replays, are logged.

Two additional sensitivity probes expose the remaining boundary: `P accepts Q` and `In P's opinion, Q` fall outside the lexical screen. Both reject when the classifier reports attribution. If the fake classifier deliberately returns the **incorrect** `own_thesis` judgment, both proceed through real proposal validation and licensed native modus ponens to `CLOSED-derived`, and become default-selectable. Thus there is no unconditional guarantee that every attributed report is excluded. This is a disclosed semantic-model dependency, not a failure to require or log the classifier enum; no live classifier accuracy was measured. Inspect actual candidate wording/definitions and classification reasons in the pilot. Evidence: [full native sensitivity results](/home/dev/ara-work/reports/phi2-rereview-evidence/classifier-dependency.json), [reproduction](/home/dev/ara-work/reports/phi2-rereview-evidence/classifier_dependency_probe.py). The original named regressions are fixed; general attribution is not proved.

**Offline fork — passed.** Reran the production freeze fork, real `ModelCalls` and native search publication on `/home/dev/ara-scaffold/runs/codex-pilot-3`, with a fake provider and socket connections forbidden. The copied prefix again contains **6,813 events / 331,834,295 bytes**, with exactly one freeze and byte-identical frozen artifacts. All **204 source files** retained their hashes and inventory. Imported accounting remains **15,645,797 tokens / USD 110.395145 historical cost**, counted once across two budget reconstructions. Reusing the destination refuses.

The new classifier was exercised: **12 actual fake calls** (two proposals plus ten classifier calls), **22 MODEL receipts** including ten classification cache replays, **20 classification dispositions**, and **96 local fake tokens**. Ten copied targets were rejected on both attempts even though the fake classifier said `own_thesis`; zero targets reached search. The proposer received 16 conditionals, 42 shared signatures and 140 catalogue entries. This proves reuse, gating and accounting; it does not prove a useful new real-corpus thesis. The disclosed fake profile clears stage routing, uses a byte/4 counter, raised local test allowances and explicit reservation accounting for historical unknown usage. Scratch fork: `/dev/shm/phi2-rereview/real-fork`. Evidence: [fork receipt](/home/dev/ara-work/reports/phi2-rereview-evidence/fork.json), [script](/home/dev/ara-work/reports/phi2-rereview-evidence/fork_probe.py), [source manifest](/home/dev/ara-work/reports/phi2-rereview-evidence/source-before.json).

**Verification and preservation.** At the exact head in `/tmp/phi2-rereview-ImBk9cg2/repo`, offline pytest completed with **1105 passed, 4 skipped / 1109 collected**, exit 0. Only after pytest exited did the complete control runner execute: **476/476 expected mutation failures and restored passes**. All **204 tracked clone files** match their pre-control hashes; the original checkout remains clean at `e7e12b4`. The four opt-in skips cover two paid-provider and two installed OCR/VL-weight tests. The green suite does not cover R1; the separate native report reproductions above do.

Commands were `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline pytest -q`, followed sequentially by `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline python tests/integration/negative_controls.py`, with temporary test data under `/dev/shm/phi2-rereview`. Evidence: [pytest receipt](/home/dev/ara-work/reports/phi2-rereview-evidence/pytest-receipt.json), [pytest transcript](/home/dev/ara-work/reports/phi2-rereview-evidence/pytest.txt), [control receipt](/home/dev/ara-work/reports/phi2-rereview-evidence/controls-receipt.json), [control transcript](/home/dev/ara-work/reports/phi2-rereview-evidence/controls.txt), [all control results](/home/dev/ara-work/reports/phi2-rereview-evidence/controls/results.json), [final preservation check](/home/dev/ara-work/reports/phi2-rereview-evidence/final-preservation.json). An initial reviewer probe used an invalid frozen-reference text; that harness error was corrected and the full matrix reran. No production fix was applied.

**Live-pilot limit.** The added `classify_target` schema changes the Codex preflight manifest from 15 to **16 cases**. Refresh the live preflight before dispatching a real fork; old 15-case receipts are insufficient. This review performed no paid calls, live schema proof, real classifier-quality evaluation, essay generation or new real-corpus closure.

**Re-review finding placement.** Only R1 is a blocking implementation defect; the other rows record fixed regressions and operational limits.

| Finding | Placement |
|---|---|
| 1. B1 mathematical/alpha regressions blocked; positive and renamed-constant controls | Prior B1 |
| 2. B2 named regressions blocked; unlisted attribution depends on model judgment | Prior B2 |
| 3. New duplicate-polarity report crash and safe repair requirement | R1 |
| 4. Real-prefix fork, source preservation, classifier calls and single accounting | Offline fork |
| 5. Full sequential tests/controls, skips, restoration and uncovered R1 | Verification and preservation |
| 6. New 16-case live schema prerequisite and unexecuted live proof | Live-pilot limit |

6 findings, 6 placed.

DONE phi2 rereview verdict=fix-first blocking=1 tests=1105/1109 negctl=pass fork_offline=ok

## Re-review R1

Reviewed `f89cd373eb3e3953bcd4ee4ad56e212ac005bcef` against `e7e12b42e3a76dfbbb6a71dbcfee2eac9f171b1d`. **Verdict: merge; R1 resolved, zero blocking findings in this narrow re-review.** No source edits, delegation or paid calls occurred.

**R1 proof.** [report.py:290](/home/dev/ara-work/xi/ara/runtime/report.py:290) now preserves event metadata explicitly, exposes the classification for existing consumers, and nests the complete receipt under `contribution`. I reran the exact saved native-graph reproductions for the two formerly failing redundant-support proofs and the necessary two-support positive control, each with both `target` and `negation` route polarity: **6/6 actual `ara report` invocations succeeded**, with HTML and JSON produced and source files unchanged.

For both redundant proofs, a negation-search route retains top-level `polarity='negation'`, while `contribution.polarity='target'` retains the local entailment-check direction. Summary JSON and detailed route JSON agree on the authoritative event polarity and target. The event sequence and graph are unchanged, and the full nested receipt equals `route_contribution`'s result field-for-field, including support IDs, reason and solver checks. Redundant proofs remain `CLOSED-single-support` and excluded by default; the positive control remains `CLOSED-derived` and selectable.

Three additional synthetic collision probes supplied receipt fields named `seq`, `target`, `polarity`, `graph`, `support_chain`, `model_summary` and `audit_results`. Every top-level field remained unchanged and every supplied receipt field survived inside `contribution`. These are explicit namespace tests, separate from the six native report reproductions. Report-time provider and engine factories were forbidden; the repository regression tests additionally regenerate fresh licensed native proofs at this head. Evidence: [independent probe results](/home/dev/ara-work/reports/phi2-r1-evidence/report-probe.json), [reproduction script](/home/dev/ara-work/reports/phi2-r1-evidence/report_probe.py), and the six retained `*-route.json` artifacts in the same evidence directory.

**Quick verification and restoration.** Focused pytest passed **66/66**, with no skips, in **14.60 seconds**. The selected files were `test_report_contribution.py`, `test_report.py`, `test_contribution_gate.py` and `test_target_triviality.py`. After pytest exited, I ran the repository's unchanged control-runner implementation with its registry filtered to tests in those four files: **34/34 expected mutation failures and restored passes**, selected from the **478-control registry**. This is scoped verification, not a fresh full-suite or all-478-controls result.

The new namespace mutation reproduced failure when flattening the receipt. The new polarity-authority mutation failed specifically because `target` replaced `negation` in the report; both restored runs passed. All **205 tracked files** in the isolated control clone match their pre-control hashes. The reviewed checkout remains clean at `f89cd37`, and the earlier review text is preserved byte-for-byte before this append. Evidence: [pytest receipt](/home/dev/ara-work/reports/phi2-r1-evidence/pytest-receipt.json), [pytest transcript](/home/dev/ara-work/reports/phi2-r1-evidence/pytest.txt), [selected controls](/home/dev/ara-work/reports/phi2-r1-evidence/selected-controls.json), [control receipt](/home/dev/ara-work/reports/phi2-r1-evidence/controls-receipt.json), [control results](/home/dev/ara-work/reports/phi2-r1-evidence/controls/results.json), [namespace failure](/home/dev/ara-work/reports/phi2-r1-evidence/controls/report_contribution_namespace-red.txt), [polarity failure](/home/dev/ara-work/reports/phi2-r1-evidence/controls/report_event_polarity_authority-red.txt), [preservation](/home/dev/ara-work/reports/phi2-r1-evidence/preservation.json).

**Scope carried forward.** This verdict clears the R1 report repair. The preceding re-review's model-dependent attribution limits and requirement for a refreshed 16-case live schema preflight still apply. No new real-corpus fork or live-provider proof is claimed by this narrow check.

**Finding placement.**

| Finding | Placement |
|---|---|
| 1. R1 resolved: successful reports, authoritative event metadata and lossless nested receipts | R1 proof |
| 2. Scoped pytest/control evidence, mutation sensitivity and exact restoration | Quick verification and restoration |
| 3. Narrow verdict; earlier semantic and live-preflight limits remain | Scope carried forward |

3 findings, 3 placed.

DONE phi2 r1 verdict=merge blocking=0 tests=66/66 negctl=pass
