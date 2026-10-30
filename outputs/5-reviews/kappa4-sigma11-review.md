# Kappa4 review — sigma round 11

Reviewed `bdeaeb8444113e5c0d6d62e5ac1b494a8f0b5fee` (`fix/bounded-closure`) against `9b9999730c32b4dd0f06ef80a075920633d1acc9`. Integration target: current main `80a344892d9acd1933bf47c1b6fd8fd986bbee5b`. Brief: `/home/dev/ara-work/briefs/sigma-round-11.md`.

**Verdict: fix-first; three blocking findings. Candidate filter: too_narrow.** Native alignment/provenance and support safeguards passed the independent probes, but the current-main integration crashes on valid alignment rows, retrieval leaves credible in-budget leads unexamined, and the judge receives task context despite its isolation contract.

Review used isolated `/home/dev/ara-work/kappa4-sigma11-checkout`. No paid calls, delegation, source fixes, commits or push. Shared author/pilot checkouts were not modified. Evidence root: `/home/dev/ara-work/kappa4-sigma11-checkout/runs/kappa4-sigma11/`.

## S11-F1 — Blocking: current-main semantic discovery treats an alignment bridge as a source paper

Sigma produces a validated bridge with `kind=alignment`, `stance=model_alignment`, `source_id=null`, and no `attributed_to`, as required. Main's [semantic_conflicts.py:34](/home/dev/ara-work/kappa4-r26-checkout/ara/runtime/semantic_conflicts.py:34) admits this row whenever the other side is endorsed; its input builder then indexes `rows[tid]['attributed_to']` at line 61.

The independent interface reproduction freezes P/Q/R and a judged P→Q bridge through Sigma's native lifecycle, validates the v2 sidecar, and passes that exact vocabulary to the **unmodified, hash-checked main-80a3448 semantic detector**, running under main's own environment. It ranks six pairs, including three source/bridge pairs. After two harmless fake `unrelated` replies, it raises **`KeyError: 'attributed_to'`** before dispatching the source/bridge pair. This failure is outside the pair-local call handler, so it is not logged as an unclassified pair; it stops discovery. Merely inventing an attribution value is not a repair: bridges are model premises, not another paper, and their source_id is intentionally null.

Required repair: integrate the alignment role into main's semantic source-pair eligibility, excluding alignment bridges from source-paper comparisons or explicitly resolving their original source evidence under a separate policy. Preserve the endorsed/reported/attacked distinctions. Add a current-main native target-discovery regression over a Sigma-produced alignment freeze.

There are also **nine textual merge conflicts** from `git merge-tree --write-tree bdeaeb8 80a3448`: `DECISIONS.md`, `SOURCE_MAP.md`, `ara/runtime/calls.py`, `ara/runtime/route_policy.py`, `prompts/propose_cuts.txt`, both runtime canned JSON fixtures, `tests/integration/negative_controls.py`, and `tests/runtime/test_codex_cli.py`. CQ resolution must preserve **both** main's hedge downgrade/retrieval and Sigma's bridge-CQ exclusion. Route resolution must preserve **both** gap-side support and alignment endorsement/paper guards. Prompt guidance, cache fixtures, schema inventories and mutation anchors require combined treatment. No full resolved merge was manufactured or claimed in this review.

Evidence: `merge-tree.txt`, `merge-tree-result.json`, `native-v2/main-integration-input.json`, `main-integration-probe.py/json/log`, and `main-seam/events.jsonl`. This is an executed interface incompatibility, separate from the unresolved textual merge.

## S11-F2 — Blocking: the hard candidate cutoff is too narrow for the requested real-T pass

The number 23 alone would not establish poor recall. The independent census and inspection of excluded definitions do: [symbol_alignment.py:42](/home/dev/ara-work/kappa4-sigma11-checkout/ara/runtime/symbol_alignment.py:42) drops every score below a hard-coded 0.15 **before** applying the configurable top-N limit.

The real pilot-5 freeze contains 169 commitments, 151 eligible symbols and 22 papers. There are 10,490 signature-compatible cross-paper pairs, of which 5,036 share at least one non-stopword term. The cutoff retains only 23, using 15.3% of the default 150-candidate allowance. Raising the configured limit to 10,000 still returns the same 23. Threshold sensitivity, before the top-N cap:

| Minimum weighted cosine | Pairs retained |
| --- | ---: |
| 0.15 | 23 |
| 0.125 | 71 |
| 0.10 | 168 |
| 0.075 | 451 |

Two credible omitted leads lie **within the existing top-150 budget** when ranked by the same score:

| Omitted symbol pair | Rank / score | Why it deserves model review |
| --- | --- | --- |
| `gsv1996_n_order_content` / `vonfintelgillies2007_ic_onestep` | 132 / 0.1052158 | Both describe the same update-order asymmetry, one concretely and one schematically. |
| `schaffer2011_r2_25_n4_meaning_perspectivalism` / `willer2013_c_uniform_account` | 133 / 0.1051864 | The definitions offer competing accounts of whether perspective/information changes semantic content. |

These are **manual relevance judgments**, not asserted equivalences, entailments or contrary relations. The model must still judge them and the encoder must still apply its checks. They show why leaving 127 available candidate slots unused on this corpus is materially restrictive. The selected list also contains broad topic matches, so the cutoff is not an established semantic-precision guarantee.

Required repair: widen bounded retrieval—e.g. configurable/calibrated threshold with deterministic top-N backfill and, if useful, topic/paper diversity—while keeping the model authoritative for every alignment. Add retrieval regressions and report prefilter counts/threshold so a small candidate inventory can be diagnosed. Do not turn lexical similarity into equivalence. This review does not claim an exhaustive semantic recall measurement.

Evidence: `candidate-census.py/json/log`, `candidate-review-examples.json`, and `ranking-probes.py/json/log`. The full source definitions remain in ignored evidence, not committed fixtures.

## S11-F3 — Blocking: pair-only judgment requests inherit the task topic

The new caller at [symbol_alignment.py:146](/home/dev/ara-work/kappa4-sigma11-checkout/ara/runtime/symbol_alignment.py:146) does not override `topic`. [calls.py:292](/home/dev/ara-work/kappa4-sigma11-checkout/ara/runtime/calls.py:292) renders every request as `{'topic': self.topic, **inputs}`. Thus the production prompt contains global task context in addition to the two definitions and their source provenance, despite the brief's isolated-judgment requirement and the documented pair-only input contract.

The native probe sets the task topic to placeholder S and observes `topic='S'` in **all three actual dispatched judge requests**, including the same-content and entailment cases. This is not a guess about hidden provider context. A task topic containing a desired thesis can bias the model judgments that subsequently rewrite every affected formula. No paid-model accuracy experiment is claimed.

Required repair: explicitly neutralize task context in the alignment call, as main's semantic conflict classifier already does with `topic=''`, and add a regression that inspects the actual rendered provider request with a nonempty task topic. Preserve original definitions, source roles and frozen-input hashes.

Evidence: `native-probes.py`, `native-v2/native-probes.json` (`topic_seen`) and each `freeze-*/events.jsonl` MODEL receipt.

## Verified native boundaries

- **Model authority and originals:** unrelated judgments leave formulas and source rows unchanged. same_content alone triggers canonical rewriting; the v2 receipt preserves exact original commitments and symbols, mapping and judgments. Source text, citations and provenance rows are unchanged. Invalid candidate substitutions and extra fields stop before freeze. The native lifecycle records one freeze after alignment/provenance publication. Owning tests cover transitive rewriting, predicate signatures, quantified bridges, replay validation, fork preservation and report catalogue selection. Code constructs bridges over identical ordered argument tuples; faithful semantic correspondence remains a model judgment.
- **Consistency:** a contrary judgment over asserted P and Q is refused. Independently, source P plus a vacuous Q formula and ¬R is initially consistent; individually usable P→Q and Q→R judgments are refused as a jointly inconsistent set, retaining original T. Owning tests cover solver UNKNOWN and durable refusal reload. There is no automatic subset salvage or source-contradiction repair; already inconsistent T cannot accept a nontrivial alignment.
- **Bridge role and support:** a rehashed endorsement spoof fails replay validation. A native route using only an alignment bridge is CLOSED-single-support and nonselectable. Bridge plus one endorsed source is also insufficient; two endorsed supports from one paper remain CLOSED-single-paper. Two endorsed cross-paper sources still permit CLOSED-derived. Bridge IDs never enter paper-support matching. Using a bridge as source CQ evidence is rejected. Native outline/render/methodology paths disclose alignment judgments and alignment-premise roles. Frozen files remain unchanged throughout search.
- **Determinism and bounds:** 100 real-inventory permutations preserve the ranked list. Limits 0, 1, 5, 23, 150 and 10,000 behave as expected; invalid integer/type values refuse. This establishes deterministic bounded retrieval, not semantic adequacy; S11-F2 covers the missing recall.

Evidence: `native-probes.py/log`, `native-v2/native-probes.json` and its freeze/route directories; `ranking-probes.json`; owning pytest and control transcripts. An initial probe harness mixed main's semantic module with Sigma's older types and failed to import Gap. That harness failure is retained separately, is not a product finding, and was replaced by the version-isolated main interface probe above.

## Real-source replay and verification

Inspected and reran the author's offline real-pilot harness with network connections forbidden and outputs redirected to this review's evidence root. Both modes make 23 fake judge calls. All-unrelated retains 169 commitments / 151 symbols; a synthetic rewrite-plus-bridge run yields 170 commitments / 150 symbols / one bridge. Native freezes and persisted validators pass, and all three original source artifacts retain their hashes. These synthetic judgments prove plumbing, not valid semantic alignment, improved closure, faithful formalization or useful synthesis. As in the author's harness, accounting/context caps are generous replay-only values with mock usage, so production admission/cost is unproved. Evidence: `offline-pilot.py/log`, `real-pilot-replay/pilot5-summary.json` and both native run directories.

Fresh scoped pytest: **413 passed / 413 collected**, no skips, exit 0, **456.91 seconds**. Twenty-seven files cover alignment, construction/provider dispatch, provenance, catalogue/freeze/fork, stance and paper support, search guidance/context, contribution/novelty, writer/audit outlines, reports, schema/preflight, shared types, engine licensing and native CLI replay. Exact command/output: `pytest-files.json`, `pytest-result.json`, `pytest.log`.

Only after all probes and pytest exited, the unchanged integration runner executed **55/55 selected mutation/restoration pairs**: all 20 new alignment controls plus 35 affected existing guards. Every mutation exited 1 with failing tests, and every restoration exited 0 with passing tests. All transcripts were checked for actual failures rather than collection/syntax errors. These controls do not cover the three findings above. This is a scoped independent run, not a rerun of Sigma's full 583-control census. Manifest, results and transcripts: `control-manifest.json`, `control-results.json`, `control-transcript-verification.json`, `controls.log`, `controls/`.

All **235 tracked paths** (234 regular files plus the AGENTS.md symlink), including **16 temporarily mutated files**, match the original snapshot and committed tree. The symlink target was independently checked. The review clone remains clean and pinned to `bdeaeb8`; git diff --check passes. The shared Sigma checkout also remains clean at that head. Receipts: `source-before.json`, `source-after-probes.json`, `source-after-controls.json`, `final-verification.json`. Twelve native probe scenarios, 100 rank permutations, two real-source fake runs, and the expected integration/topic findings are summarized in `probe-verification.json`.

The new schema and provenance version require updated readers and refreshed applicable live preflight. No live preflight or paid classification was run. The existing alignment-stage failure path stops before freeze and has no dedicated construction-resume entrypoint. Main integration remains unverified beyond the explicit merge/interface checks above.

**6 findings, 6 placed:** integration blocker and nine textual conflicts in S11-F1; retrieval adequacy judgment in S11-F2; isolation failure in S11-F3; verified model/provenance/consistency/support boundaries and conservative limits in “Verified native boundaries”; synthetic real-source census and accounting/semantic limits in “Real-source replay”; executed test scope/restoration and live/integration limits in “Real-source replay and verification”. The three numbered findings block approval.

DONE kappa4 sigma11 verdict=fix-first blocking=3 tests=413/413 negctl=pass candidate_filter=too_narrow

## Re-review sigma11 + r27

Reviewed **`0a31afb92c319bd0ae38f71e51b3233050d32758`**, Xi's merge of `5557e9a` and Sigma `bdeaeb8`, including the S11 corrections and Round 27 per-paper novelty/forward/external-gap changes. Baseline context: `80a3448`; implementation brief: `/home/dev/ara-work/briefs/xi-round-27.md`; author integration receipt: `/home/dev/ara-work/reports/xi-integrate-sigma.md`.

**Verdict: fix-first; one new blocking finding (INTEG-F1). S11-F1, S11-F2 and S11-F3 are fixed on this head.** Per-paper deductive synthesis works, but packaging facts from different papers with an irrelevant atom reopens the structural-route bypass. It also contaminates forward proposals and external-gap targets.

All work ran in isolated `/home/dev/ara-work/kappa4-integ-checkout`, pinned to the requested head. Evidence root: `runs/kappa4-integ/` in that clone. No paid calls, delegation, production fixes, commits or pushes; the shared Xi/pilot checkout was not modified. Fake-provider probes explicitly refuse network access. The review applies Round 27's deliberate allowance for union entailment; ordinary cross-paper modus ponens is **not** a finding.

### INTEG-F1 — Blocking: per-paper essentiality admits padded packages as derived contributions

At [novelty.py:112](/home/dev/ara-work/kappa4-integ-checkout/ara/runtime/novelty.py:112), the Boolean-package check recognizes frozen formulas and recursively recognized connective packages. Introducing R makes that check false. At [novelty.py:137](/home/dev/ara-work/kappa4-integ-checkout/ara/runtime/novelty.py:137), R then qualifies as essential because it changes the target under either paper **considered separately**, where the other paper's already-known fact is missing. [route_policy.py:121](/home/dev/ara-work/kappa4-integ-checkout/ara/runtime/route_policy.py:121) upgrades the structurally licensed proof to CLOSED-derived.

Executed native proposal → classifier → bank licensing/search → contribution → selection reproduction, with endorsed P from paper a and Q from paper b:

| Target | Native outcome | Proof |
| --- | --- | --- |
| P ∧ Q | Proposal rejected | Correct bare-package control |
| (P ∧ Q) ∨ R | **Selectable CLOSED-derived** | Conjunction introduction, disjunction introduction |
| R → (P ∧ Q) | **Selectable CLOSED-derived** | Conditional proof with unused R assumption, conjunction introduction |
| R | Selectable CLOSED-derived | Sign scheme with both endorsed supports and answered CQs; positive control |

Both padded routes have `substantive_inferences=[]`, successful native licensing receipts, and the two genuine paper IDs. R contributes no new supported proposition; the proof only combines P and Q and adds an irrelevant wrapper. The fake classifier gives the normal positive own-thesis/new-assertion/fidelity response, intentionally isolating the deterministic novelty/route gates. This does not claim a live classifier would always accept the text. It proves those gates no longer enforce the retained padding requirement when the model approves a candidate.

The 15-case prior helper matrix confirms that direct implication, conditional chains, disjunctively encoded implications, conjunctions of padded implications, double negation and quantified negation wrappers now pass per-paper preflight with P and Q in separate papers. Bare conjunction, De Morgan packaging, tautological fresh-atom padding, vacuous universal packaging and alpha-renaming remain rejected. The formal-alias helper also reports a candidate; this is **helper-level evidence only**, not an independently established bypass of the content classifier. Genuine cross-paper deduction, a fresh atom and a fresh predicate application remain candidates.

This is reachable through the new proposer guidance too. For endorsed P(a), Q(b), R→S(c), native bounded forward mining emits **94 qualifying candidates**, including `P ∧ (Q ∨ R)` in its first 30. Its source dependencies are just P and Q, and its bank IDs are conjunction/disjunction introduction. The forward list also includes vacuous quantified copies of P and R→S combined into an equivalent frozen package. This affects useful retrieval too: in the alignment fixture P(a), Q→R(b), model bridge P→Q, genuine R ranks **35/70**, outside the `proposal_forward_candidates` first-30 slice. A final native prepare/freeze/validated-provenance→proposal replay confirms R is absent from the actual rendered proposer input; the bridge has its proper null source_id. Structural candidates crowd it out; ordinary Q from P(a), P→Q(b) still ranks first. The same weakness admits `(P ∧ Q) ∨ R` as `external:lead:pad` when an external-gap classifier positively judges resolution. Neither path repairs the flawed novelty verdict.

Existing padding tests were narrowed to one-paper bases; the R1 test additionally freezes Q in paper a. Those cases still correctly reject single-paper consequences but no longer exercise the cross-paper package regression. Repair must preserve both classes: reject irrelevant wrappers around separately known facts, while retaining `{P(a), P→Q(b)} ⊢ Q` and legitimate defeasible new theses. Do not restore the superseded whole-T-entailment prohibition. Add native selection regressions for both examples above and forward/external-gap coverage of the same boundary.

Evidence: `padding.py/json/log`, each native target directory and MODEL/engine receipts; `matrix.py/json`; `forward-probes.py/json` and `forward-padding*.jsonl`; `gap-probes.py`, `gap-probes-v2.json/log`, `gaps-v2/padded_package/events.jsonl`.

### S11-F1, S11-F2 and S11-F3 verification

- **S11-F1 fixed:** the old native freeze/bridge reproduction now reaches integrated discovery successfully. Exactly three source/source pairs are dispatched; no alignment row is passed to the source-conflict classifier. Original source attribution fields remain required. The committed merge includes both branches' changes; the nine former textual conflicts are resolved, with CQ, stance, gap and alignment guards exercised together in the affected tests and controls.
- **S11-F2 fixed for the reviewed retrieval defect:** independent real pilot-5 census returns **150 selected pairs**, from 10,490 signature-compatible cross-paper pairs and 5,036 shared-term pairs. 168 exceed the preferred 0.10 score; one deterministic diversity replacement/backfill covers the previously missing paper, yielding all **22 papers**. Both old omitted leads are selected. Twenty shuffled symbol/provenance inventories produce the identical complete result. Native persisted retrieval logs/replay are exercised by owning tests and controls. This resolves the specific hard-cutoff defect; it does not prove exhaustive semantic recall, and lexical ranking still supplies leads rather than equivalences.
- **S11-F3 fixed:** actual rendered fake-provider alignment requests have `topic=''` with the run topic set to S. Original definitions, source roles and input hashes remain present. This is measured at dispatch, not inferred from the caller signature.

Evidence: `native-probes.py`, successful `native-v3/native-probes.json`, `native-probes-v3.log`, native freeze/route events, `census.py/json/log`, owning retrieval tests and selected control transcripts. The first adapted harness retained its old callback during discovery and failed an assertion; that harness failure is retained in `native-probes.log`/`native-v2/`, superseded by the corrected callback run. It is not a product finding.

### Alignment provenance, consistency and paper ownership

All twelve prior native alignment scenarios were rerun. Unrelated judgments preserve T. same_content rewriting preserves original commitments/symbols in the receipt and original source rows. Invalid candidate substitutions/extra fields stop before freeze. Both contrary and jointly inconsistent alignment sets refuse without modifying source T. There remains one freeze. A rehashed bridge-to-endorsement spoof fails persisted provenance validation.

Bridge-only and bridge-plus-one-endorsed-source routes remain CLOSED-single-support; two endorsed supports from one paper remain CLOSED-single-paper; two endorsed cross-paper supports permit a genuinely new derived route. A bridge cannot answer a source CQ. Search leaves frozen bytes unchanged, and outlines disclose alignment premises/judgments. Directly spoofing a bridge source_id still creates neither an endorsed-paper closure group nor a paper-support match. Model judgments remain the sole authority for alignment; deterministic code does not infer an equivalence from lexical scores.

### Per-paper positives and bounded forward mining

Native owning tests verify proposal, search, selection and reporting for Q from P(a), P→Q(b), and rejection when both commitments belong to paper a. The independent fresh-R sign-scheme case remains accepted/derived. Per-paper source grouping excludes reported/attacked/alignment rows, and unresolved solver results refuse novelty.

Independent forward probes verify native bank licensing, repeat determinism, source dependency IDs, and alignment disclosure. Q appears in the cross-paper deduction case; the one-paper version yields zero candidates. For P(a), Q→R(b), and an explicitly model-judged P→Q bridge, R appears with papers a/b and a separately disclosed alignment support ID, even when the bridge's untrusted source_id is spoofed. The first-order and recorded-forward lifecycle/cache controls are covered by the owning suite. R is present in the full forward inventory, but is outside the first-30 proposer slice in this fixture (`forward-proposer-cutoff.json`). The final validated native replay confirms the actual proposer request omits R, while an independently supplied R proposal is still accepted (`cutoff-native.py/json/log`). This is a practical consequence of INTEG-F1. Forward results remain proposals subject to final gates; INTEG-F1 explains why those gates currently admit some padding.

Real pilot-5 replay was executed twice: unchanged and with the author's two explicitly fake same_content judgments through the actual prepare/freeze/provenance path. Both runs yield **zero qualifying candidates**, **500 licensed consequences**, depth 2, cap reached. The fake-aligned run selects 150 judge pairs and reduces 151 symbols to 149; source artifacts retain exact hashes and bytes. This proves plumbing and bounded enumeration, not useful synthesis, faithful equivalence, completeness, or production budget admission. The harness uses generous replay caps and mock accounting. No live semantic assessment was performed.

Evidence: `forward-probes.py/json/log`, `real-forward/summary.json`, `real-forward-aligned/summary.json`, corresponding event streams/transcripts, and `census.json` source hashes.

### External gap-file gates

Fourteen independent scenarios check the native file-to-proposal path or, for stance isolation, its loader boundary. Valid external hypotheses are logged and prioritized, bind current source IDs, preserve exact evidence/currency/search-scope/framing metadata, and leave freeze files unchanged. Spoofed papers, unknown supports, malformed evidence, and reported/model-alignment support groups refuse. A legitimate R is retained with its external gap; entailed targets, bare packages, exact attribution frames, model-judged attribution, copied definitions and model-judged restatements reject. A negative resolves_gap judgment can leave a general target with no gap attached; it does not claim a resolved gap. Native CLI/fork, outline roundtrip and missing-side support tests also pass.

The padded external target described in INTEG-F1 passes the shared novelty gate. No separate loader privilege bypass was found. Supplied literature evidence remains an AI-found claim, not an independently verified endorsement or a new frozen premise. Exact claiming/wording by a future live writer remains outside these offline tests.

Evidence: `gap-probes-v2.json/log`, `gaps-v2/`, external-gap/gap owning tests and controls. The initial gap harness omitted resolves_gap because it checked the wrong input nesting, producing only general-target fallbacks; its receipt is retained in `gap-probes.json/log`. The corrected run reads `target.gap` and establishes the external-target results above.

### Verification, restoration and limits

Fresh scoped pytest: **448/448 passed** across 31 affected files, exit 0 in 700.69 seconds; supplemental gap/CQ suite **27/27 passed**, exit 0 in 44.07 seconds. **475/475 total**, no skips. Coverage includes alignment/retrieval, construction/freeze/provenance, native proposal/search/selection/reporting, per-paper novelty and prior padding cases, source stance/paper matching, context/guidance, external/native gaps, CQ retrieval/hedges, writer/audit outlines, shared schemas/types, engine licensing and native CLI replay. Exact manifests and transcripts: `pytest-files.json`, `pytest.log`, `pytest-result.json`, `supplement-files.json`, `supplement.log`, `supplement-result.json`.

Only after pytest and every initial probe exited, the unchanged repository integration runner executed **89/89 selected mutation/restoration pairs**. Every mutation exited 1 with an actual failing test; every restored run exited 0 with passing tests. Transcript checks exclude collection failures. Selection includes all 55 prior S11 review controls plus 34 current synthesis/integration/gap/hedge controls. These controls do **not** cover INTEG-F1. This is scoped independent verification, not a rerun of the author's 1,363-collected full suite or 650-control census. Evidence: `control-manifest.json`, `control-results.json`, `control-transcript-verification.json`, `controls.log`, `controls/`.

All **252 tracked paths**, including the AGENTS symlink and **25 temporarily mutated files**, match both the initial snapshot and committed head after restoration. The review clone is clean/pinned and git diff --check passes. Final shared Xi head/status observation: `0a31afb92c319bd0ae38f71e51b3233050d32758` / `clean`; no shared files were edited by this review. `probe-verification.json` records 12 native alignment scenarios, four native padding/positive scenarios, 15 helper matrix cases, 14 gap scenarios, four repeat-checked forward scenarios, and two real-source forward replays. `source-before.json`, `source-after-probes.json`, `source-after-controls.json` and `final-verification.json` preserve restoration evidence.

After the controls exited and restoration was verified, one final native freeze→proposal follow-up checked the newly identified forward ranking cutoff (`cutoff-native.py/json/log`). No source edits or concurrent mutations were involved. No paid model call, live preflight or production pilot evaluation was run. Green existing tests and controls establish their named boundaries; they do not override the independently reproduced blocking regression.

**8 findings, 8 placed:** new padding blocker in INTEG-F1; the three former blockers individually in “S11-F1, S11-F2 and S11-F3 verification”; alignment safeguards in “Alignment provenance, consistency and paper ownership”; positive synthesis/forward behavior and real-source limits in “Per-paper positives and bounded forward mining”; file-gate results and qualifications in “External gap-file gates”; executed coverage/restoration and scope limits in “Verification, restoration and limits”. Only INTEG-F1 blocks this head.

DONE kappa4 integ verdict=fix-first blocking=1 tests=475/475 negctl=pass

## Re-review round 28

Reviewed **`1dce56efbfc97cc3ef00ea1e0f0d123841ddae51`**, base **`0a31afb92c319bd0ae38f71e51b3233050d32758`**, for the requested narrow INTEG-F1 re-review. Author receipt: `/home/dev/ara-work/reports/xi-round28.md`. The change replaces per-paper substitution checks with substitution checks against the endorsed/alignment union; other production modules are unchanged.

**Verdict: fix-first; two blocking findings.** The original disjunction/unused-conditional reproductions are fixed, and ordinary cross-paper modus ponens remains derived. However, the previously reported quantified-package variant still becomes selectable, and the new union-wide check suppresses valid deductions whenever an unrelated endorsed contradiction exists elsewhere in T.

All work used isolated `/home/dev/ara-work/kappa4-r28-checkout`, with evidence in `runs/kappa4-r28/`. No paid calls, delegation, production fixes, commits or pushes. Native probes use fake providers with network connections prohibited; pytest and controls use offline uv and `ARA_LIVE_TEST=0`. The shared Xi checkout was not modified.

### R28-F1 — Blocking: the quantified-package part of INTEG-F1 remains selectable

For endorsed **P(a)** and **Q→R(b)**, the bare target `P ∧ (Q→R)` is rejected. Adding an unused binder yields **`P ∧ ∃x(Q→R)`**, which is accepted as a target and becomes **selectable CLOSED-derived**. The same result holds through an external gap file with an affirmative content/resolution fake. Z3 verifies the two targets are equivalent with no premises.

This was part of the prior INTEG-F1 forward finding, not a requirement that the entire forward inventory must always be empty. The native proof has only **conjunction introduction** and **existential generalisation**, with the two original endorsed source IDs, no new definitions and no substantive new proposition. Both inference shapes are licensed. The existential variable occurs nowhere in its body.

At [novelty.py:118](/home/dev/ara-work/kappa4-r28-checkout/ara/runtime/novelty.py:118), `package()` only recognizes frozen hashes and connective recursion, so the quantifier hides the known conditional. The changed check at [novelty.py:145](/home/dev/ara-work/kappa4-r28-checkout/ara/runtime/novelty.py:145) then marks **Q and R** essential: substituting an atom inside a previously established conditional can change its truth under the union. That demonstrates atomic dependence of the old assertion, not a new contribution. The native content classifier is deliberately positive, as in the original deterministic-gate reproduction; no live classifier accuracy claim is made.

Forward consequences confirm the practical impact. The P(a), Q(b), R→S(c) fixture now has **66** retained forward candidates, down from 94, but still includes quantified copies of frozen compound premises. In the alignment fixture P(a), Q→R(b), model bridge P→Q, genuine R remains **35th of 70** and misses the first-30 proposer slice. A fresh native prepare/freeze/provenance→proposal replay confirms R is absent from the actual rendered request. The bridge has a null source_id; an independently proposed R still passes admission.

Required correction: reject vacuous quantifier/equivalent wrappers around combinations of already-established compound commitments at proposal, route-selection, forward and gap-target boundaries, while preserving real cross-paper deductions. Add the native two-step reproduction above; checking only the original padded disjunction/conditional is insufficient.

Evidence: `quantified-package.py/json/log`, `quantified-native/`, `quantified-gap/`, `forward-probes.py/json/log`, and `cutoff-native.py/json/log` with its validated freeze and rendered-request events.

### R28-F2 — Blocking: an unrelated contradiction disables otherwise valid synthesis

The independent positive control uses `{P(a), P→Q(b)}` and retains/selects Q as CLOSED-derived. Adding **R(c)** and **¬R(d)**, neither used by the Q proof, changes that result: Q is rejected by proposal, and its native CLOSED modus-ponens route is classified **CLOSED-structural**, with zero selectable routes. Its actual support IDs remain only `t1,t2` (P and P→Q).

The new union includes all four commitments at [novelty.py:90](/home/dev/ara-work/kappa4-r28-checkout/ara/runtime/novelty.py:90). Since that union is inconsistent, both substitution equivalences at [novelty.py:146](/home/dev/ara-work/kappa4-r28-checkout/ara/runtime/novelty.py:146) return SOLVER_UNSAT by explosion. No atom can pass; the function reports `no_essential_new_proposition`. The immutable base novelty helper, evaluated against the identical inputs, returns `candidate`. The current native proof still closes through the unchanged bank rule.

This is an unhandled consequence of the requested full-union criterion even when implemented literally: a union with no models cannot supply its required essentiality witness. Frozen cross-paper contradictions are supported inputs—the native gap detector logs the R/¬R contradiction here without changing T. The rule therefore suppresses unrelated valid work and also leaves formal-contradiction gaps unable to admit any new resolving assertion. Calling all those results structural is not an honest explanation of the obstruction.

Required correction: explicitly handle inconsistent unions and retain the intended consistent-support synthesis/conflict-resolution behavior, without allowing explosion to license unsupported claims or silently deleting/relabeling source commitments. Add a native positive regression with the unused R/¬R pair. The product policy for inconsistent literature needs resolution alongside this guard; restoring the former whole-T-entailment ban would not fix it.

Evidence: `unrelated-conflict.py/json`, `unrelated-conflict-v2.log`, and `unrelated-conflict-v2/events.jsonl`. Semantic conflict model calls are disabled in the final reproduction; the contradiction is detected deterministically. The initial harness used the wrong configuration key and left semantic fake calls enabled; its matching result is retained separately in `unrelated-conflict.log` and superseded by v2. The base comparison executes only the immutable base novelty helper, not an entire base checkout.

### Verified correction, positives and prior matrix

| Probe | Current result |
| --- | --- |
| P(a), Q(b) ⊢ proposed `(P∧Q)∨R` | Rejected; explicit native proof CLOSED-structural; nonselectable |
| P(a), Q(b) ⊢ proposed `R→(P∧Q)` | Rejected; unused-assumption proof CLOSED-structural; nonselectable |
| Bare P∧Q | Rejected and structural |
| Genuine R through sign from two endorsed papers | Accepted and selectable CLOSED-derived; CQs answered |
| P(a), P→Q(b) ⊢ Q | Accepted and selectable CLOSED-derived |
| P(a), P→Q(a) ⊢ Q | Rejected and CLOSED-single-paper |

The **15-case prior helper matrix** was rerun with provenance. All eleven direct packaging/wrapper negatives reject: bare conjunction, De Morgan form, tautological fresh-atom padding, direct implication, conditional chain, encoded implication, conjunction of padded implications, double negation, quantified negation, vacuous universal and alpha-renaming. Fresh atom, new predicate application and ordinary cross-paper deduction remain candidates. The formal-alias-in-T row remains a helper candidate, as at the base; no new end-to-end classifier bypass is claimed from that row alone. Native definition-copy and model-restatement negatives still reject.

The **14 external-gap scenarios** preserve file/provenance binding, frozen bytes, attribution and content gates. The original padded external target now rejects. A fresh R retains its external gap; a negative resolution judgment can retain only a general target without a gap. Invalid paper identities, unknown supports, malformed evidence and reported/alignment support groups refuse. R28-F1 separately establishes the remaining quantified external-target bypass.

Forward results repeat deterministically: cross-paper deduction fixture 38 candidates (Q first), same-paper fixture zero, package fixture 66, alignment fixture 70. The specific `P∧(Q∨R)` candidate from the prior finding is removed. Alignment support IDs remain separate from paper owners, including the direct spoofed-source-ID helper test. Owning tests cover union-basis receipts, both substitution polarities, solver UNKNOWN refusal, reported opposition, native proposal/selection/reporting and CLI replay.

Evidence: `padding.py/json/log`, `deduction.py/json/log`, `matrix.py/json`, `gap-probes.py`, `gap-probes-v2.json/log`, the native event directories, and `probe-verification.json`. No real-T census or live semantic evaluation was repeated in this narrow review.

### Verification, restoration and scope

Fresh scoped pytest: **186/186 passed**, no skips, across 14 affected files, exit 0 in **552.55 seconds**. The suite covers the new union-essentiality cases, per-paper synthesis, novelty/content/padding, cross-paper and stance guards, native/external gaps, report contributions, alignment retrieval, engine licensing and native CLI replay. Exact command inputs and output: `pytest-files.json`, `run-pytest.py`, `pytest.log`, `pytest-result.json`.

After all probes and pytest exited, the unchanged repository integration runner executed **27/27 selected mutation/restoration pairs**: all five new union-essentiality controls and 22 affected existing novelty, content, synthesis, stance, alignment, gap and CLI controls. Each mutation exited 1 with actual failing tests; each restoration exited 0 with passing tests. Transcript inspection excludes collection errors. Runtime: **625.98 seconds**. These controls do not cover R28-F1 or R28-F2. Manifest and receipts: `control-manifest.json`, `control-results.json`, `control-transcript-verification.json`, `controls.log`, `controls/`.

All **253 tracked paths**, including the AGENTS.md symlink and **10 temporarily mutated files**, match the original snapshot and committed head after restoration. The isolated clone remains clean/pinned; git diff --check passes. Shared Xi observation: `1dce56efbfc97cc3ef00ea1e0f0d123841ddae51`, `clean`. Snapshots and final checks: `source-before.json`, `source-after-probes.json`, `source-after-controls.json`, `final-verification.json`.

This is a narrow independent run, not a repetition of the author's full 1,375-collected suite or 655-control census. No live provider, production pilot, real-T census or semantic-originality judgment was performed. Existing green tests/controls do not negate the independently reproduced findings.

**4 findings, 4 placed:** residual package bypass and forward crowding in R28-F1; inconsistent-union regression in R28-F2; verified repairs/positive controls and matrix qualifications in “Verified correction, positives and prior matrix”; executed test scope, controls and restoration in “Verification, restoration and scope”. Both numbered findings block this head.

DONE kappa4 r28 verdict=fix-first blocking=2 tests=186/186 negctl=pass
