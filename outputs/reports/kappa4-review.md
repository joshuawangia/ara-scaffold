# Kappa4 review of xi round 18

**Verdict: fix-first. Two blocking novelty bypasses reproduced through native proposal, closure and default selection. Full pytest and all 517 mutation controls pass.**

Reviewed `/home/dev/ara-work/xi`, branch `feat/run-report`, head `2c4741d481e53bac6f32f644678eef86302028a7`, against `main` at `412a4575d9b469df9a57e8fbe6e4d888ec697756`. Review performed directly, without delegation, paid calls, or source fixes.

## F1 — Blocking: connective wrappers let antecedent-only novelty become CLOSED-derived

[novelty.py:17](/home/dev/ara-work/xi/ara/runtime/novelty.py:17) descends only through leading `implies`, `forall`, and `exists`. An implication nested under `and`, `or`, or `not` is treated as a whole main claim. Its antecedent atoms then count as new main propositions at lines 60-61.

For T={P,Q}, the direct conditional `R -> (P and Q)` and a leading conditional chain are rejected. But `(R -> (P and Q)) and (S -> (P and Q))` passes all proposal gates. The native engine closes it with conjunction introduction and two conditional proofs; both scoped assumptions are unused in deriving P and Q. The policy at [route_policy.py:8](/home/dev/ara-work/xi/ara/runtime/route_policy.py:8) and [route_policy.py:35](/home/dev/ara-work/xi/ara/runtime/route_policy.py:35) counts those conditional proofs as substantive, so the result is `CLOSED-derived` and default-selectable. The two endorsed supports have two different source IDs. No fresh consequent has been established.

Z3 also proves this target equivalent to `(R or S) -> (P and Q)` (`SOLVER_UNSAT` for the equivalence), while the latter is rejected.

The equivalent disjunction `not R or (P and Q)`, explicit double negation of the conditional, and `not forall x not (R -> (P and Q))` also pass target preflight. These are executable counterexamples, not speculative paths. Evidence: `runs/kappa4-review/matrix.json`, `probes.json`, and the `conditional/` native run.

Required repair: make the new-main-assertion check robust to equivalent encodings and nested connectives; ensure a scoped proof that merely adds unused antecedents cannot qualify as the substantive link. Add regressions through proposal, closure and default selection, preserving Q from {P,P -> Q}.

## F2 — Blocking: renaming or text-only definitions can conceal an existing assertion

`novelty_check(formula, commitments)` sees only formal syntax. [target_policy.py:64](/home/dev/ara-work/xi/ara/runtime/target_policy.py:64) supplies no target text or definition bindings. [ModelCalls.propose_targets](/home/dev/ara-work/xi/ara/runtime/calls.py:945) accepts a supplied formula without checking its fidelity to the target text; the independent classifier tests assertion versus attribution, not novelty or equivalence.

Native fake-provider probes retained both `text="P", formula=R` and `text="R := (P and Q)", formula=R` for T={P,Q}. Each then closed via `sign`, with every required CQ answered using the two frozen supports, and became default-selectable `CLOSED-derived`. Returning own_thesis does not resolve whether R names a new claim: an old assertion can still be stated in one's own voice.

Boundary: a formal definition `R iff (P and Q)` included in T **is** detected and R is rejected. The failure is specifically an unbound new target symbol/definition or renamed text, not Z3's handling of an explicit formal equivalence. Text/formula fidelity was already an acknowledged representation limitation before this diff, but the requested renamed-atom/definition adversary remains able to defeat round 18's intended gate. Evidence: `runs/kappa4-review/rename/`, `definition/`, `probes.json`, and `matrix.json`.

Required repair: bind proposed new symbols to their actual assertion/definition and check reuse/equivalence before accepting their formal novelty; reject exact existing-content renames. Preserve new assertions. At minimum do not treat the current mechanical receipt as proof that this explicit adversary was excluded.

## F3 — Operational prerequisite: native real-pilot fork refuses inherited preflight

The actual `fork-from-freeze --source-run /home/dev/ara-scaffold/runs/codex-pilot-5 --provider mock` entrypoint copied the verified frozen prefix and then refused: `Codex schema preflight is missing, incomplete or stale`. The injected fake provider had not been called. A top-level provider override leaves inherited Codex construction-stage overrides present, so the preflight still applies. This is a pre-existing operational condition, not a new round-18 regression or a reason to bypass preflight. A live fork needs a current successful preflight matching its effective stage configuration.

A separate explicitly logged all-mock configuration on the verified copy completed native proposal and search. All three proposal attempts received all 169 commitments, 151 verified catalogue symbols, and the actual sign scheme. The conjunction was rejected with Boolean-recombination correction feedback; fresh R survived and closed through sign, with answered CQs and two endorsed supports from different sources. Results: one CLOSED-derived route and its OPEN negation. This is mechanical fake-provider reachability, not semantic scheme fit or useful real synthesis. It cannot turn the refused CLI entry into an accepted CLI run.

All five source artifact hashes stayed unchanged. Frozen commitments byte SHA-256: `390163f35a3b8d4604750ddd18813e938d449030006b1be0f41a20c0490944eb`; catalogue canonical hash: `43fc4b4be35ee9d5e175f067fe4cbc36c0eb4c8e97cfea13f7a47533108bd0b0`. Evidence: `runs/kappa4-review/fork-verification.json`, `pilot5-offline/`, and `fork.py`. The harness logged an explicit all-mock configuration, disabled forward expansion, and used a 2,000,000-token context allowance for the mock byte estimator. No live preflight was fabricated or bypassed; there were no paid calls.

## Completed verification

The 15-case direct probe confirms rejection of ordinary Boolean packaging, De Morgan rewrites, tautological fresh atoms, leading conditional chains, vacuous universal wrappers, alpha-renamed binders and formal aliases in T. Fresh R, F(b) from T={F(a)}, and Q from T={P,P -> Q} survive.

The native placeholder evidence confirms both blockers reach default selection. The passing owning regressions separately establish that a bare conjunction route is CLOSED-structural and excluded by default, an unreachable substantive inference cannot upgrade it, and a fresh-atom sign route stays OPEN when its CQs are unanswered. Bank licensing and CQ closure remain enforced on the native path.

Proposer guidance is concrete: it includes actual bank entries, structural/substantive IDs, good and bad placeholder plans, frozen definitions, and correction feedback. The real-T probe verified the actual catalogue hash at every proposal attempt; the guidance is not a detached placeholder-only catalogue. These parts meet the narrow brief.

Coverage is a direct, single-reviewer examination of the changed gate/route/prompt code and its native callers, bank rules, closure logic and owning tests. No sub-agent or external reviewer was used. Full pytest completed: **1195 passed, 4 skipped / 1199 collected**, exit 0, 996.01 seconds. Command: `uv run pytest -q`. The integration control runner started only after pytest exited successfully: **517/517 mutations produced the expected test failure, and all 517 restored checks passed**, exit 0. This includes all seven round-18 controls. Command: `uv run python tests/integration/negative_controls.py`.

All 223 tracked-file hashes match the pre-control snapshot, covering 49 mutated files. HEAD remains `2c4741d481e53bac6f32f644678eef86302028a7`; the working tree is clean. No source fixes or commits were made. The required controls made only temporary, restored mutations.

Evidence root: `/home/dev/ara-work/xi/runs/kappa4-review/`. It contains `pytest-full.log`, `controls-full.log`, every red/restored control log in `controls/`, `control-results.json`, `source-before.json`, `source-after.json`, `final-verification.json`, the 15-case matrix, native adversarial runs, and the real-T fork receipt. The retained harness scripts document the executed probes; rerunning them requires a fresh output directory. No live usefulness, semantic scheme fit, CQ truth, or three useful real routes is claimed.

## Finding placement

3 findings, 3 placed: F1 in the connective-wrapper section; F2 in the renaming/definition section; F3 in the native-fork prerequisite section. F1 and F2 block approval; F3 is a disclosed operational prerequisite.

DONE kappa4 verdict=fix-first blocking=2 tests=1195/1199 negctl=pass fork_offline=refused

## Re-review — Round 19, 2026-10-28

Reviewed clean head `44cced12f901ce01722d639d1ce5010ab905ddc7` on `feat/run-report`, against the previously reviewed `2c4741d481e53bac6f32f644678eef86302028a7`. Main remains `412a4575d9b469df9a57e8fbe6e4d888ec697756`. Direct review only: no delegation, source fixes or paid calls.

**Re-review verdict: fix-first, one blocking finding. Full pytest and all 531 mutation controls pass.** The earlier findings are reassessed below; the earlier gate counts apply only to Round 18.

### R1 — Blocking: decorative proof steps still upgrade irrelevant antecedents

[route_policy.py:64](/home/dev/ara-work/xi/ara/runtime/route_policy.py:64) treats any reachable assumption node below a result as evidence that the assumption was used. It follows every child of conjunction elimination, including conjuncts discarded by that rule. [route_policy.py:79](/home/dev/ara-work/xi/ara/runtime/route_policy.py:79) then qualifies any nonstructural conclusion sharing an essential atomic application with the root. This also lets a later hypothetical-syllogism step qualify a conditional whose fresh antecedent came only from unused assumptions. When the candidate step is the root, the essential-key comparison checks the same formula against itself; it does not establish that the fresh atom was concluded rather than merely assumed.

Native conditional probes use **T={P or Q, S}**, two endorsed commitments from two sources, and the same target **R -> Q**, with R explicitly bound to distinct placeholder content. Neither T nor a single commitment entails the target. R is its only essential fresh atom. All scheme CQs have explicit supported answers. A baseline also tests Q directly.

| Native proof | Current result |
| --- | --- |
| Derive Q by sign from T | Target rejected for having no essential new atom; direct engine route CLOSED-structural |
| Assume R, derive Q and S by sign independently, eliminate to Q, discharge R | CLOSED-structural, not selectable |
| Derive Q and S by sign; assume R; introduce (Q and S) and R; eliminate to Q; discharge R | **CLOSED-derived, selectable**; only conditional_proof qualifies |
| Derive R -> S using frozen S and unused R; derive S -> Q using sign; combine by hypothetical_syllogism | **CLOSED-derived, selectable**; only hypothetical_syllogism qualifies |

A matched control uses the same sign conclusion Q and S and the same elimination to Q, without inserting R into the conjunction: it is CLOSED-structural. The first decorative proof merely inserts and discards R. The second routes that irrelevant antecedent through another bank rule. Neither substantive sign inference concludes a fresh atomic proposition: Q and S are already in T's vocabulary. The underlying conclusion using existing atoms and the unadorned conditional remain structural, while the added proof packaging changes the verdict. These are native licensed, engine-closed routes, not fabricated CLOSED graphs. The target and classifier judgment stay the same across the conditional variants.

Required repair: track effective assumption dependencies through structural elimination and prevent later deductive wrappers from restoring substantive status to the same irrelevant antecedent. Regression expectations should compare the unadorned conditional, the introduction/elimination detour, and the syllogism wrapper, while retaining a sign conclusion that actually establishes a fresh proposition.

Evidence: `runs/kappa4-rereview/padded-assumption-final.json`, `syllogism-wrapper.json`, `unadorned-conditional.json`, `unadorned-matching-core.json`, `old-vocabulary-conclusion.json`, their scripts, and corresponding native run directories. An initial cyclic detour was correctly stopped by the engine; the retained counterexamples are acyclic. The final padded proof uses faithful slot texts, including all three conjuncts.

### R2 — Prior F1/F2 matrix and the model-judgment boundary

The full original 15-case formula matrix was rerun. Every previous Boolean package, conditional chain, equivalent disjunction, explicit double negation, quantifier wrapper, alpha-renamed binder and formal alias in T is rejected. Fresh R and F(b) from T={F(a)} remain eligible. The former multi-support Q target now rejects as a classical consequence, as discussed in R3.

The old native wrapped-conditional case is rejected before search; direct historical closure is CLOSED-structural and not selectable. Text P with formula R is rejected by deterministic definition reuse even with a positive classifier. Text R := (P and Q) with formula R is rejected when the required classifier returns novelty=restatement. Classifier inputs include frozen content and the bound proposed definition, and judgments are logged.

**Residual accuracy limit:** an explicitly tested false-positive classifier response (own_thesis, new_assertion, matches) still admits the definitional alias and permits CLOSED-derived closure. This is the remaining model-accuracy dependency of the newly requested hybrid policy, not a claim that the new judgment wire is absent. No paid model judgment was tested, so F2's semantic accuracy on real proposals is not established by these offline checks. Exact lexical renames have the additional deterministic protection; arbitrary definitions do not.

Evidence: `matrix.json`, `native-probes.json`, `old_wrapper/`, `old_rename/`, `old_definition/`, and `definition_false_positive/` under the re-review evidence root.

### R3 — Genuine new thesis and preserved deduction

The native genuine-R probe still passes proposal, closes through sign using two endorsed sources and answered CQs, and is default-selectable CLOSED-derived. Its fake classifier supplies distinct-content novelty/fidelity judgments; this proves mechanical reachability, not real-world originality or scheme fit.

The independent deduction probe confirms **{P,P -> Q} proves Q through licensed modus_ponens and reaches engine CLOSED**. Under the explicitly requested rule that T must not classically entail a novel target, Q is rejected from target proposal and its route is CLOSED-structural. Thus “still works” holds for deduction, not for novel-route selection; treating both as required would contradict the new admission rule. Evidence: `genuine/`, `native-probes.json`, `deduction/`, and `deduction.json`.

### R4 — Current real-T fork and preflight prerequisite

The actual CLI fork on pilot 5 again refused stale inherited Codex preflight before calling the injected fake provider. The classifier schema has changed, so a live fork needs a current successful preflight matching its effective configuration. No live preflight was fabricated or bypassed.

A separate logged all-mock target/search exercise on the verified copied freeze completed at this head. Three proposal attempts each received all 169 commitments and 151 catalogue symbols. The conjunction was rejected with deductive-closure feedback; fresh R survived, closed by sign with answered CQs and two-source support, and was CLOSED-derived. Its negation was OPEN. All five source-file hashes stayed unchanged. `fork-verification.json` records the current result, catalogue hash, dispatches and source hashes. The harness explicitly disables forward expansion and gives the mock byte estimator a 2,000,000-token context allowance. This is separate from the refused CLI entry and does not establish live semantic judgment accuracy or useful synthesis.

### R5 — Nonblocking: automatic and explicit bindings use different collision rules

With frozen atoms P and Q, a target with text R and formula P(a) receives an automatic predicate binding `{"name":"P","kind":"predicate","arity":1,"definition":"R"}`. It has no definition issues, survives proposal, and closes as selectable CLOSED-derived. Supplying that identical binding explicitly through new_symbols instead yields invalid_definition_binding and rejects the target. A fresh predicate F(a) remains accepted as the positive control.

[target_content.py:26](/home/dev/ara-work/xi/ara/runtime/target_content.py:26) checks explicit definitions against every frozen **name**; [target_content.py:33](/home/dev/ara-work/xi/ara/runtime/target_content.py:33) inserts automatic definitions after that check and compares complete name/kind/arity keys. Normalize both binding paths through one collision policy and test equivalent explicit/implicit inputs. The compiler deliberately separates atom and predicate namespaces, so this probe does not rewrite frozen atom P's meaning; it demonstrates inconsistent admission of the same proposed content and signature. This is separate from the blocking route-quality defect in R1.

Evidence: `automatic-binding-probe.json`, its script and three native run directories. This probe ran only after the full control runner exited and all source hashes were verified restored.

### Completed re-review verification

Evidence root: `/home/dev/ara-work/xi/runs/kappa4-rereview/`. Full pytest completed with **1225 passed, 4 skipped / 1229 collected**, exit 0, 1127.31 seconds, using `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked pytest -q`. The initial probe batch and pytest finished before the control runner started. The full control runner then completed: **531/531 expected mutation failures and 531/531 restored passes**, exit 0. It uses `ARA_LIVE_TEST=0 UV_OFFLINE=1 TMPDIR=/dev/shm/kappa4-rereview-tests uv run --offline --locked python tests/integration/negative_controls.py`. 

The temporary-directory choice avoids the nearly full root filesystem (416 MiB free at the checkpoint; /dev/shm had 31 GiB free). The required controls temporarily mutated 51 files; all 225 tracked-file hashes match the initial snapshot both after controls and after the final binding probe. HEAD remains `44cced12f901ce01722d639d1ce5010ab905ddc7`; the working tree is clean. No source fixes, commits, paid calls or delegation occurred. 

Full receipts are `pytest-full.log`, `controls-full.log`, `control-results.json`, every red/restored log in `controls/`, `source-before.json`, `source-after-controls.json`, `source-after.json`, and `final-verification.json`. Native probe scripts and outputs are retained alongside them; use fresh output directories to repeat those scripts. The current-head CLI fork refusal is disclosed in R4; no accepted live or fake CLI fork is claimed.

### Re-review finding placement

5 findings, 5 placed: the remaining route classification blocker in R1; old-probe resolution and model-accuracy dependency in R2; deduction/novelty behavior in R3; stale preflight and current real-T evidence in R4; automatic/explicit binding inconsistency in R5. Only R1 blocks approval.

DONE kappa4 rereview verdict=fix-first blocking=1 tests=1225/1229 negctl=pass

## Re-review R1 — Round 20, 2026-10-28

Reviewed `cb9d2c0ff2b40e511258a97eb99eb94926aa37f7` on `feat/run-report`, against Round 19 head `44cced12f901ce01722d639d1ce5010ab905ddc7`. Main remains `412a4575d9b469df9a57e8fbe6e4d888ec697756`. **Narrow verdict: merge; zero blocking findings.** R1 is resolved at this head. Review was direct and offline, with no paid calls, delegation, source fixes or commits.

### R1 resolution — the scheme itself must conclude new content

`route_policy.py:substantive_scheme_ids()` now admits only bank entries with `kind == 'defeasible'`. A reachable qualifying scheme's own conclusion must share an essential new atomic application with the target, checked against the whole freeze. Logical rules cannot supply that step. The earlier assumption-reachability heuristic is gone; target guidance uses the same bank-kind distinction.

Replayed the independent Round 19 harnesses against current production code, using fresh evidence directories, native proposal/search, licensed rules, two endorsed sources and answered scheme CQs. The conditional probes use T={P or Q,S} and target R -> Q with an explicit R binding.

| Probe | Round 20 result |
| --- | --- |
| Q by sign, using only existing atoms | Proposal rejected; direct historical engine route CLOSED-structural; not selectable |
| Unadorned R -> Q, sign concludes Q under unused R | CLOSED-structural; not selectable |
| Matching-core control: sign concludes Q and S, eliminate to Q, discharge R | CLOSED-structural; not selectable |
| Padded detour: add R to Q and S, eliminate to Q, discharge R | CLOSED-structural; not selectable |
| Hypothetical-syllogism wrapper through R -> S and S -> Q | CLOSED-structural; not selectable |
| Genuine R through sign from two frozen supports | Proposal accepted; CLOSED-derived; selectable |
| {P,P -> Q} proves Q | Licensed modus_ponens; engine CLOSED; CLOSED-structural |

All five structural proofs have empty qualifying-inference receipts. The four R1 cases plus the matching-core control therefore agree, including the two formerly selectable counterexamples. The focused regressions also verify that a genuine new sign conclusion can remain derived under a conditional wrapper, every deductive bank entry is excluded from qualifying, and an unknown scheme cannot qualify.

Evidence: `old-vocabulary-conclusion.json`, `unadorned-conditional.json`, `unadorned-matching-core.json`, `padded-assumption-final.json`, `syllogism-wrapper.json`, `native-probes.json`, `deduction.json`, and their retained harnesses/native logs under `runs/kappa4-r1/`. `verify-probes.py` asserts the observed outcomes; `probe-verification.json` records its pass.

### Prior matrix and definition-judgment boundary

All 15 formula cases were replayed. Thirteen reject: Boolean packages, De Morgan, vacuous fresh atoms, direct/chained/encoded/wrapped implications, double negation, quantifier wrappers, alpha-renamed binders, formal alias in T, and Q already entailed by {P,P -> Q}. Fresh R and F(b) from T={F(a)} remain eligible. The old native wrapped conditional is rejected at proposal and its direct historical route is structural. Exact text P/formula R is rejected by deterministic definition reuse; R := (P and Q) is rejected when the logged classifier identifies restatement.

The deliberate false-positive classifier still admits the definitional alias and permits CLOSED-derived. This reproduces the disclosed accuracy dependency of the requested deterministic-plus-model policy; it is not a newly introduced Round 20 blocker. Offline mock judgments establish the enforcement path, not semantic accuracy, faithful formalization, scheme fitness or useful synthesis. No unconditional claim that every possible definition disguise is excluded is warranted.

### Preserved deduction and binding consistency

The independent deduction probe confirms {P,P -> Q} proves Q through licensed modus_ponens. Q is intentionally rejected as a *novel target* because frozen T entails it; this does not disable deduction. Genuine R remains accepted and selectable.

The prior R5 inconsistency is resolved: automatic and explicit P(a) bindings both reject when P is already a frozen atom. Fresh automatic F(a) still proposes and closes as derived; focused tests also accept the explicit fresh binding. Both paths now use the same collision validator. Evidence: `automatic-binding-probe.json` and the parameterized binding tests.

### Verification scope and restoration

Fresh focused pytest: **125 passed / 125 collected**, no skips, exit 0, 102.71 seconds. Eight files cover nonlogical contribution, novelty, semantic judgments, contribution gates, target pools/triviality, report contribution and search alignment. The exact offline command is retained in `pytest-result.json`; output is in `pytest-focused.log`.

After every probe and pytest completed, the existing integration control runner ran a selected **67-case** manifest covering those eight test files, including all four Round 20 controls and `semantic_unused_assumption`. **67/67 expected mutation failures and 67/67 restored passes**, exit 0. The runner itself was unchanged; `run-focused-controls.py` selects its cases and invokes its native `main()`. Its manifest, results, complete output and every red/restored test log are retained in `control-manifest.json`, `control-results.json`, `controls-focused.log` and `controls/`.

All **226 tracked-file hashes** match the pre-run snapshot, including **11 temporarily mutated files**. HEAD remains pinned, the working tree is clean, and `git diff --check` passes. Restoration receipts are `source-before.json`, `source-after-controls.json` and `final-verification.json`. Temporary test data used `/dev/shm/kappa4-r1-tests` because the root filesystem is nearly full.

These are this review's **scoped** checks. Xi's separate full-suite receipt reports 1245 passed, 4 skipped / 1249 and 535 controls at this head; those counts were not independently rerun here and are not the counts in this verdict.

### Retained operational prerequisite and finding placement

The large pilot-5 fork was not repeated in this narrow pass. The prior review's native CLI refusal due to stale inherited Codex preflight remains a disclosed prerequisite: a live run needs current preflight matching its effective configuration. The earlier separate all-mock real-T exercise is historical evidence only, not current-head fork verification or live quality proof.

**5 findings, 5 placed:** R1 closure in “R1 resolution”; prior matrix and residual model-accuracy dependency in “Prior matrix and definition-judgment boundary”; deduction behavior and R5 binding repair in “Preserved deduction and binding consistency”; retained preflight prerequisite in this section. No new blocking defect was found in the requested scope.

DONE kappa4 r1 verdict=merge blocking=0 tests=125/125 negctl=pass

## Re-review round 21 — 2026-10-28

Reviewed `a272ebe7df8615a7a9a4a0215068f963171a5c3d` against `cb9d2c0ff2b40e511258a97eb99eb94926aa37f7`. **Verdict: merge; zero blocking findings in this focused review.** Work was direct and offline, without delegation or paid calls. Because a pilot was running in parallel, all probes, pytest and temporary mutations ran in `/home/dev/ara-work/kappa4-r21-checkout`, an isolated clone with its own virtual environment. The pilot's `/home/dev/ara-work/xi` source was only read.

### Attribution: required classifier rejection survives; broad lexical protection is intentionally removed

The independent native probe covers the earlier named attribution cases: argues/holds/believes that, defends, is P's view, curly-apostrophe view, according to, on P's account, holds, maintains, position, endorses and says. It also includes the prior lexical misses “P accepts Q” and “In P's opinion, Q”, plus an explicit new-symbol definition containing “P defends Q” behind target text R.

A content-sensitive fake reads the actual target and bound definitions, distinguishes reporting P's position from own-voice assertions, and returns a reason with all three classifier judgments. It is not an always-reject stub. Targets use a fresh R binding so classical novelty rejection does not conceal the classifier path. Rejection reasons and judgments are checked in the actual logs.

| Native proposal → search → selection probe | Result |
| --- | --- |
| 15 attributed texts and one attributed new-symbol definition | All 16 rejected with `own_thesis_not_established`; no selectable routes |
| “Claims about P support R” and “The account of P supports R” | Both accepted and CLOSED-derived/selectable despite lexical hits |
| Exact leading argues/holds/believes-that frames, with deliberately wrong own_thesis judgment | All three remain hard-rejected |
| “P defends R”, with deliberately wrong own_thesis judgment | Accepted and CLOSED-derived/selectable |

The last row is the requested policy's accuracy boundary, not an accidental bypass: broad text and definition hits are advisory and the classifier is authoritative. These named broad phrases no longer have the former lexical backstop, including at route display/selection. A false-positive classifier can admit an attributed thesis. The narrow hard frames retain that backstop. The tests prove enforcement of realistic fake judgments, not real classifier accuracy; pilot review should inspect actual wording, definitions and classification reasons. The owning tests additionally check catalogue evidence, `unclear` refusal, cache replay and isolated classifier inputs.

Evidence: `attribution-probes.py`, `attribution-probes.json`, `attribution-probes.log`, and the `attr-*` native directories under the evidence root.

### Novelty and derived rules: prior matrix remains intact

Replayed the full 15-case formula matrix and all nine prior independent harnesses. Thirteen formula cases reject; fresh R and F(b) from T={F(a)} remain eligible. Every old Boolean, connective and quantifier package, formal alias in T, and entailed-Q target remains rejected. The native old wrapper is structural. Exact text renames and classifier-detected definition restatements reject.

The four R1 adversaries plus the matching-core control all remain CLOSED-structural and nonselectable, with no qualifying non-logical inference. Genuine R still closes through sign with two endorsed supports and answered CQs, and is selected. {P,P -> Q} still proves Q by licensed modus_ponens, engine CLOSED, with structural rather than novel-target status. Explicit and automatic frozen-name collisions both reject; a fresh predicate remains admitted.

The deliberately false-positive definition classifier still admits the prior definitional alias. That pre-existing semantic dependency remains; Round 21 does not make formal novelty a proof of content originality. `verify-probes.py` asserts the complete expected outcome matrix, with a passing receipt in `probe-verification.json`.

### Guidance and bounded correction: licensing still decides

Five additional independent native scenarios exercise a three-candidate batch containing an unknown bank ID, an invalid conjunction deduction of fresh R, and a sign instance missing a required slot. The engine returns `UNKNOWN_BANK_ID`, `SOLVER_COUNTEREXAMPLE` and `SLOT_MISMATCH` as concrete correction feedback.

A valid corrected sign closes as derived; another invalid deduction remains OPEN; a licensed sign with unsupported CQs remains OPEN. A valid third candidate closes without asking for a second batch. An overfull four-candidate batch is rejected and only its subsequent valid correction closes. Each scenario verifies at most two batches, the actual defeasible-bank inventory in guidance, essential R evidence, and that no invalid proposal becomes a route inference. The corrected root remains the same R throughout.

Source review confirms that `_licensed_cuts` calls the existing licenser before yielding an inference. Node/depth limits, cycle checks, frozen-reference checks, premise closure, stance and CQ checks remain on the native path. Only accounted invalid proposal output triggers the new correction exception; operational failures still propagate through existing search recovery. Guidance supplies signatures and evidence, not a license.

Evidence: `guidance-probes.py`, `guidance-probes.json`, native `guidance-final-*` directories, and the affected search/licensing tests. An initial harness startup used an out-of-range validation setting and correctly refused before search; the retained final replay uses the supported maximum of three and fresh directories.

### Executed verification and limits

Fresh scoped pytest: **233 passed / 233 collected**, no skips, exit 0, 247.34 seconds. Scope: eleven owning runtime files (search guidance, contribution, search alignment/failures, non-logical contribution, novelty/semantic novelty, target pool/triviality, report contribution, calls) and the entire `tests/engine/` directory. Command and output are retained in `pytest-result.json` and `pytest-focused.log`.

All probes and pytest finished before mutations began. The existing integration runner executed **97/97 selected controls**, including all seven new Round 21 controls and the Round 20 wrapper/binding controls. The engine runner, with the review-only anchor disambiguation described below, then executed **26/26 controls**, including solver, bank, slots, conclusion, schema, scope, CQ support and limits. Every mutation caused its expected test failure, and every restoration passed: **123/123 control pairs** total. These are scoped executed checks, not a rerun of xi's separate 1,255-pass/542-control full-suite receipt.

All **227 tracked file hashes** were restored in the review clone. Its HEAD stayed pinned and its working tree stayed clean after controls. The pilot checkout also remained at the requested head with all 227 reviewed source hashes unchanged. No pilot process, source file, configuration, run artifact or provider was modified. `final-verification.json` records both checkout checks. Full logs and manifests remain under `/home/dev/ara-work/kappa4-r21-checkout/runs/kappa4-r21/`.

This pass did not repeat the large real-corpus fork, evaluate a paid model, or evaluate the parallel pilot's outcome or effective preflight. The author's exact-leaf replay is not independently repeated evidence here. Scheme fitness, CQ truth, faithful formalization, live originality and useful synthesis remain outside these offline checks.

### Pre-existing standalone engine-runner issue

The unmodified `tests/engine/negative_controls.py` completed and restored its solver and bank controls, then aborted before the slots mutation: `return result('SLOT_MISMATCH')` occurs twice, violating its unique-anchor requirement. Both occurrences and the unchanged runner already exist at base cb9d2c0. This is a nonblocking verification-tool defect, not a Round 21 licensing regression. The standalone runner needs its anchor updated before it can run unmodified.

`run-engine-controls.py` disambiguates only that mutation in its in-memory case list by including the following goal-formalization line. It invokes the existing runner and tests, then verifies restoration. No tracked file was edited permanently. The resulting 26/26 pass is an adapted-harness result; it does not claim that the unmodified standalone runner passed. The initial failure log, base comparison and exact adapted manifest are retained in `controls-focused.log`, `engine-runner-issue.json`, `engine-control-manifest.json` and `engine-controls.log`.

**5 findings, 5 placed:** attribution policy and accuracy boundary in “Attribution”; preserved prior gates and alias limitation in “Novelty and derived rules”; correction/licensing behavior in “Guidance and bounded correction”; executed scope and live/pilot limits in “Executed verification and limits”; the pre-existing standalone runner defect and workaround in “Pre-existing standalone engine-runner issue”. No new blocking defect was found.

DONE kappa4 r21 verdict=merge blocking=0 tests=233/233 negctl=pass

## Re-review round 22 — 2026-10-28

Reviewed `25e076a01bc68dc0d717ab0e9949c7674f3bfc07` against `a272ebe7df8615a7a9a4a0215068f963171a5c3d`. **Verdict: fix-first; one blocking finding.** Work was direct and offline, without delegation or paid calls. Tests and temporary mutations ran only in `/home/dev/ara-work/kappa4-r22-checkout`, an isolated clone with its own virtual environment. The parallel pilot's source, configuration and run artifacts were not modified.

### R22-F1 — Blocking: ordering the same CQ support set changes paper count and default selection

The new gate at [route_policy.py:102](/home/dev/ara-work/xi/ara/runtime/route_policy.py:102) counts paper IDs from `_logical_contribution`'s `support_ids`. That list has already discarded all but the first encountered commitment for each formula through `supports.setdefault(...)` at [route_policy.py:42](/home/dev/ara-work/xi/ara/runtime/route_policy.py:42). When the same formula has provenance from more than one paper, the selected paper depends on CQ support-list order.

Independent native reproduction freezes **t1=P from paper a, t2=Q from paper a, t3=P from paper b**. In both runs the target is the same genuine fresh R, the sign premises are exactly t1 and t2, and every CQ has the same answer and the same three supporting IDs. Both targets pass proposal; both proofs are licensed and engine CLOSED. Only the order of the CQ `supporting_t_ids` list changes:

| CQ support order | Deduplicated support IDs | Paper receipt | Classification / default selection |
| --- | --- | --- | --- |
| t1, t2, t3 | t1, t2 | a; count 1 | CLOSED-single-paper; excluded |
| t3, t1, t2 | t2, t3 | a, b; count 2 | CLOSED-derived; selected |

The two saved route graphs are **identical after sorting only the CQ supporting-ID lists**. Frozen T, provenance, formulas, premise references, CQ support sets, and all other graph fields are identical. This is not an invented paper ID or an unreachable support: paper b is cited as CQ evidence in both runs. It shows that the new gate reports different paper counts and offers different default selections for the same evidence. It can suppress a qualifying route or be changed by rearranging evidence, without changing what the proof cites.

Required repair: preserve all formula-to-commitment/paper provenance associations through logical deduplication, and apply an explicit order-independent rule for the distinct-formula/paper requirement. Arbitrarily retaining one representative source loses information. Add native regressions for reversed CQ support order and repeated formulas across papers, alongside true same-paper and duplicate-formula-only negatives. Keep formula distinctness, stance, reachability, novelty, licensing and CQ checks intact.

Evidence: `duplicate-paper-order.py`, `duplicate-paper-order.json`, both `paper-order-*-route.json` graphs, their native run directories, and `paper-order-verification.json` under the evidence root. The assertion comparing normalized graphs passed. The existing suite/control selection does not cover this provenance-collapse case.

### Paper identity: requested namespace and text-spoof probes resist inflation

Eight native proposal/search/selection cases confirm the intended ordinary behavior. Two distinct formulas from one paper remain CLOSED-single-paper when their IDs use separate range prefixes, separate salvage batches, union-item namespaces, or separate union-snapshot namespaces. The union-snapshot case uses the real `snapshot_union.unite` mapper on two conflicting bodies under one original evidence ID, then `source_provenance` to carry their unchanged paper identity into the frozen sidecar.

Misleading paper prefixes in commitment IDs, and other paper names embedded in commitment text or citation strings, also leave the count at one. A genuine two-source P/Q sign route remains CLOSED-derived/selectable; a route without a provenance sidecar remains CLOSED-contribution-unresolved. The owning tests separately cover an unreachable third-paper support and restricted source stance. Engine CLOSED is preserved. This gates default selection; explicit human `--route` selection remains available and logged. Legacy runs without paper metadata therefore require explicit selection rather than automatic writing.

Changing a sidecar source ID without updating its hash is refused. Recomputing that sidecar's hash still cannot disagree with the already logged frozen provenance: native `search_vocabulary` refuses it. Extraction validates each item against its paper source ID; salvage changes evidence IDs while retaining source ID; snapshot union changes IDs/references while retaining each item's source ID; construction copies identity from the source item rather than proposed wording.

This establishes resistance to the requested namespace/text attacks, subject to R22-F1. It counts trusted frozen source IDs, not bibliographic deduplication or independent evidence. Two separately registered IDs for the same underlying publication are not resolved by this gate; that disclosed limitation is distinct from the reproducible order-dependent count.

Evidence: `paper-probes.py`, `paper-probes.json`, `paper-probes.log`, `paper-*` native directories, and provenance/range-union tests.

### Bridges and proposal guidance: deterministic, catalogue-bound candidates

Independent bridge checks passed **40 permutations** of commitment, catalogue and provenance-row order, plus **four separate Python hash seeds**. Candidate order, content and bridge IDs were identical. Bridge IDs recompute from their canonical payloads. The expected three linked commitments form three pairs and one triple; a fourth disconnected commitment never enters a candidate despite shared text/citation bait.

Only used frozen catalogue symbols and their definition terms supply connections. Shared text/citation terms without catalogue overlap produce no bridges; common function words produce none. Same-source-only inputs, missing metadata and restricted stances produce none. A 40-commitment input yields exactly 30 pairs plus 30 triples with truncation disclosed. A changed frozen definition with a stale catalogue hash is refused at the native vocabulary boundary. Source review confirms exact frozen-vocabulary validation precedes bridge generation; proposed new target symbols are not added to the bridge catalogue.

The focused native tests verify that candidate bridges and commitment-to-paper mappings reach target, leaf and cut calls, and that bridge receipts map actual premise slots while excluding scoped hypotheses. The pool requests 30 candidates, retains at most ten in stable order, and preserves correction/survivor behavior. These are candidate leads; the engine still licenses the schemes and closes the premises/CQs. Lexical overlap is not evidence of semantic relevance or scheme suitability.

Evidence: `bridge-probes.py`, `bridge-probes.json`, `bridge-input.json`, `bridge-probes.log`, and the cross-paper/target-pool/search-guidance tests.

### Prior gates and verification scope

Replayed the full 15-case formula matrix and nine prior independent native harnesses. All expected outcomes remain: Boolean/quantifier packaging and entailed targets reject; all R1 wrapper variants remain structural; genuine R with two verified papers remains derived; licensed {P,P -> Q} proves Q while Q remains excluded as a novel target. Exact renames and classifier-detected definition restatements reject, and automatic/explicit frozen-name collisions agree. `verify-probes.py` and `probe-verification.json` record the assertions.

The prior deliberately false-positive definition classifier still admits its alias; broad attribution remains dependent on classifier accuracy under Round 21's policy. The focused attribution/semantic tests pass. No paid model accuracy, faithful formalization, semantic scheme fitness, necessary use of every CQ citation, or useful cross-paper synthesis is established here. The current pilot's outcome and effective preflight were not evaluated.

Fresh scoped pytest: **213 passed / 213 collected**, no skips, exit 0, 256.90 seconds. Fifteen files cover cross-paper policy, provenance/content construction, range union, search guidance/alignment, non-logical contribution, novelty/semantic novelty, contribution, target pool/triviality, report contribution, writer validation and native CLI replay. The exact command and output are retained in `pytest-result.json` and `pytest-focused.log`.

After all probes and pytest completed, the existing integration control runner executed **97/97 selected mutation/restoration pairs**, including all ten Round 22 controls and affected prior novelty, attribution, paper, bridge, pool and source-provenance controls. Every mutation caused a test failure and every restoration passed. The runner was unchanged; the selection manifest and every red/restored log are retained. This does not resolve R22-F1, which the selected existing tests do not cover.

All **229 tracked-file hashes** match the pre-run snapshot after controls; the clone remains clean at the requested head. The pilot checkout's 229 source hashes also match that commit and were not mutated. `git diff --check` passes. Receipts: `source-before.json`, `source-after-controls.json`, `control-manifest.json`, `control-results.json`, `controls-focused.log`, `controls/`, and `final-verification.json`. Evidence root: `/home/dev/ara-work/kappa4-r22-checkout/runs/kappa4-r22/`.

These are this review's scoped checks, not a fresh execution of xi's separately recorded 1,262-pass/552-control full run. The large real-corpus fork and the prior standalone engine runner were not repeated in this focused pass. No source fixes or commits were made.

**4 findings, 4 placed:** the blocking order-dependent paper gate in R22-F1; namespace identity resistance and bibliographic limits in “Paper identity”; deterministic bridge/pool behavior and semantic relevance limits in “Bridges and proposal guidance”; preserved gates, model dependencies and live/verification limits in “Prior gates and verification scope”. Only R22-F1 blocks approval.

DONE kappa4 r22 verdict=fix-first blocking=1 tests=213/213 negctl=pass

## Re-review round 23 — 2026-10-28

Reviewed `2ed9e21796bf55e1160bd6a22e1f0f459bb67436` against `25e076a01bc68dc0d717ab0e9949c7674f3bfc07`. **Verdict: fix-first; one new blocking finding. R22-F1 is fixed.** All probes, tests and temporary mutations ran in `/home/dev/ara-work/kappa4-r23-checkout`, an isolated clone with its own environment. No paid calls, delegation, source fixes or commits occurred. The parallel pilot was not modified or evaluated.

### R23-F1 — Blocking: an unusable exact match can displace the leaf's endorsed commitment

[search_context.py:19](/home/dev/ara-work/xi/ara/runtime/search_context.py:19) ranks exact formula matches by overlap and commitment ID, without considering their source stance. When any bridge exists, fallback seeds are disabled. [search_context.py:24](/home/dev/ara-work/xi/ara/runtime/search_context.py:24) then preserves only the first exact-match ID. That ID can be reported/attacked content even when frozen T contains an endorsed copy that can close the leaf.

The native probe freezes four commitments: `a-reported=P` with reported stance, `z-endorsed=P` with endorsed stance, and two endorsed Q commitments from other papers. Q supplies the available cross-paper bridge; only one endorsed P exists, so no P bridge supplies it. The leaf is P. All metadata passes the native frozen-catalogue/provenance validation.

| Slice | Supplied commitment rows | Mapping / native result |
| --- | --- | --- |
| Normal k=8 (also k=4,2,1) | a-reported, b-q, c-q | No visible endorsed P; mapper returns open; engine OPEN |
| Shrunk k=0 | a-reported | No visible endorsed P; mapper returns open; engine OPEN |
| Full-T reference mapper control | Includes z-endorsed | Selects z-endorsed; same native engine closes P |

The catalogue still lists z-endorsed as an evidence ID, but its commitment row and endorsed role are omitted; the identifier alone does not establish a permitted exact match. The fake mapper follows the actual projected roles: it selects only a visible, endorsed exact formula match and otherwise returns open. It does not invent cuts to compensate for omitted evidence. The normal k=8 case already fails without context pressure; a controlled counting probe reproduces the same omission at k=0. Full-T reference mapping closes the same goal with unchanged bank, freeze and provenance. This is loss of an existing usable leaf commitment, not merely omission of a potentially useful heuristic lead.

Required repair: preserve a usable endorsed exact match whenever one exists, independently of bridge selection, ID order and shrink level. Retain the stance restrictions; do not promote reported/attacked evidence to fix the omission. If indispensable leaf context cannot fit, issue the disclosed local refusal rather than silently replacing it with an unusable match. Add native regressions with earlier-ID restricted copies and later-ID endorsed copies at normal and zero bridge limits.

Evidence: `leaf-own-probe.py`, `leaf-own-probe.json`, `leaf-own-probe-final.log`, `own-leaf-final-*` native directories, and both `own-leaf-*-route.json` / `own-leaf-*-control-route.json` graph pairs under the evidence root. The reference control is explicitly an offline full-T mapper, not a paid model judgment.

### R22-F1 resolved: order-independent formula/paper matching

Replayed the original independent counterexample unchanged against this head: t1=P/a, t2=Q/a, t3=P/b, sign premises t1/t2, with CQ evidence ordered either t1,t2,t3 or t3,t1,t2. Both runs now retain all three support IDs, produce identical full contribution receipts, classify CLOSED-derived and are selectable. Their graphs still agree after sorting only CQ evidence lists.

The matching witness uses distinct formula groups and distinct paper IDs: P/t3 supplies b and Q/t2 supplies a. Logical checks retain deterministic representatives while paper matching sees every cited origin. The owning matching regressions preserve same-paper exclusion, duplicate-formula-only exclusion, stance and reachability rules. The eight prior namespace/spoofing native cases also passed again: range, salvage, union-item, actual union-snapshot and misleading ID/text/citation cases remain single-paper; true two-source support remains derived; absent provenance remains unresolved. Both sidecar-tamper refusals still hold.

Evidence: `duplicate-paper-order.py`, both graphs and native runs, `duplicate-paper-order.json`, `r22-f1-verification.json`, and `paper-probes.json`. The earlier R22 blocker is closed; R23-F1 is a separate regression in the new context slicing.

### Bounding, logging and real-source size replay

Independent checks passed 100 bridge-order permutations across k=8,4,2,1,0 and three Python hash seeds. Fixed frozen inputs produce identical slices and hashes. Bridge counts stay within k, selected commitments within the structural bound, and an endorsed exact-match positive control survives every level, including k=0. R23-F1 identifies the missing multiple-match/stance case.

A controlled native counting probe shrank 8 → 4 → 2 before its single dispatch. Each receipt records input plus output allowance, decision, selected IDs and catalogue size. The final `inputs_sha256` equals the actual dispatched input after removing the renderer's topic field. Full commitments/provenance hashes remain bound to the projection. Owning tests verify that validation feedback is recounted from full inputs and that full-T validation, licensing and stance checks remain authoritative.

Reran the author's inspected, read-only fork-4 counting harness on the pinned code with network connection attempts forbidden and a counter whose dispatch method raises. It reconstructs the native calibration state at each of eight saved requests and reproduces all original input/output counts exactly. The new map totals are **37,519–37,690** and cut totals **48,435–48,606**, including the unchanged **16,384-token output allowance**. All eight fit the configured 200,000 limit at k=8, using nine commitments and eleven catalogue entries. **ctx_max=48,606** is confirmed. All inspected source-run artifact hashes stayed unchanged.

These are calibrated admission estimates, not measured provider usage or a successful live fork. Shared-symbol ranking and zero-overlap fallback seeds remain heuristics; useful non-exact evidence may be omitted. Evidence: `slice-probes.py/json/log`, `fork4-context.py/log`, and `fork4-context/results.json` with its source hashes and per-request counting logs.

### Job-local refusals remain visible; global stops remain global

Three independent concurrent scenarios used four workers: an irreducible map refusal for one polarity, an irreducible cut refusal for one polarity, and map refusals for all six polarity jobs. In each single-failure case, five sibling results survive and only job 1 is marked failed after its bounded retry. In the all-failure case there are zero routes, six explicitly failed jobs and a partial phase—not fabricated OPEN or successful routes.

Every refused job records k=0/refused slices and search-scoped STOP events. No oversized request reaches provider dispatch. The shared budget remains unhalted and siblings are not cancelled. Published journals and exported methodology identify the same failed jobs, retry indices and partial status; missing polarity is not presented as absence of conflict. Existing tests also verify later search-port context refusals, run-wide token-cap/infrastructure stops, unknown-accounting disclosure, publication integrity and resume behavior.

Evidence: `job-local-probes.py/json/log`, `job-one-map/`, `job-one-cut/`, `job-all-map/`, and the search-failure/publication/resume tests. No failure-hiding regression was found in the executed scope.

### Executed verification and restoration

Fresh scoped pytest: **231 passed / 231 collected**, no skips, exit 0, 484.29 seconds. Sixteen owning files cover cross-paper matching, context slicing, failures, guidance, alignment, stance, model calls, prior contribution/novelty gates, target pools, report contribution, publication, parallel jobs and resume. The exact command is retained in `pytest-result.json`; output is in `pytest-focused.log`. An initial command named a nonexistent test file and exited before running tests; its command-error log is retained and excluded from these counts.

After the round 23 probes and pytest completed, the unchanged integration runner executed **125/125 selected mutation/restoration pairs**, including the three new matching controls and six context controls. Each mutation caused a test failure and each restoration passed. These existing controls do not cover R23-F1. Manifest, results and every red/restored log are retained in `control-manifest.json`, `control-results.json`, `controls-focused.log` and `controls/`.

After control restoration, replayed all nine prior independent harnesses and verified their expected outcomes (`replay-results.json`, `probe-verification.json`). The 15-case formula matrix rejects all 13 old/entailed packages and admits fresh R and F(b). All five R1/wrapper proof cases remain CLOSED-structural and nonselectable. Genuine R remains CLOSED-derived/selectable through sign; {P,P -> Q} proves Q by licensed modus_ponens while Q remains excluded as a novel target. Exact renames, classifier-detected restatements and both frozen-name collision paths reject. The deliberately false-positive definition classifier still admits its alias, preserving the previously disclosed model-accuracy limit. No new novelty or licensing bypass emerged in this replay.

All **231 tracked-file hashes** match the pre-run snapshot after controls, including **23 temporarily mutated files**. The isolated clone is clean at the reviewed head; the pilot checkout's source hashes also match that head and were not mutated. `git diff --check` passes. Evidence root: `/home/dev/ara-work/kappa4-r23-checkout/runs/kappa4-r23/`; restoration and checkout receipts are in `source-before.json`, `source-after-controls.json` and `final-verification.json`.

These are scoped checks, separate from xi's recorded full 1,276-pass/561-control run. No paid classifier accuracy, semantic independence, truthful CQ support, faithful formalization, useful synthesis, or parallel-pilot success is claimed. Prior model-dependent attribution/definition limits remain.

**5 findings, 5 placed:** new leaf-retention blocker in R23-F1; prior blocker resolution and paper-gate preservation in “R22-F1 resolved”; deterministic bounding, measurement and heuristic limits in “Bounding, logging and real-source size replay”; visible local refusals/global stops in “Job-local refusals”; executed scope and live/model limitations in “Executed verification and restoration”. Only R23-F1 blocks approval.

DONE kappa4 r23 verdict=fix-first blocking=1 tests=231/231 negctl=pass

## Re-review round 24 — 2026-10-28

Reviewed `9b9999730c32b4dd0f06ef80a075920633d1acc9` against `2ed9e21796bf55e1160bd6a22e1f0f459bb67436`. **Verdict: merge; R23-F1 is fixed, with zero blocking findings in this narrow re-review.** Work ran directly and offline in `/home/dev/ara-work/kappa4-r24-checkout`; no paid calls, delegation, source fixes or commits. The pilot checkout was not modified.

### R23-F1 resolved: every exact match survives shrinking

Replayed the original independent reproduction with the same frozen commitments: earlier-ID reported P, later-ID endorsed P, and two endorsed Q commitments supplying the available bridge. The fake mapper selects only a visible endorsed exact match. Both normal sizing and forced k=0 now close the native leaf through `z-endorsed`, agreeing with the full-T reference control. Previously both native runs stayed OPEN.

At every k in 8,4,2,1,0, both P commitments remain present, with the endorsed copy first. Projected source roles remain unchanged. Both the dispatched search_slice and logged search_context_slice identify the mandatory exact IDs. All 24 commitment-order permutations across five levels preserve that exact-match order and membership. An absent legacy provenance sidecar remains absent; it is not interpreted as endorsement. The owning pytest regressions also exercise attacked copies at normal and zero bridge limits.

Source review confirms the mandatory set is collected before bridge/fallback selection and unioned into every slice. Ordering prioritizes verified endorsed roles, then IDs; it does not change stance permissions. The only production change is in `ara/runtime/search_context.py`; frozen validation, engine licensing, novelty and paper matching are unchanged.

Evidence: `leaf-own-probe.py`, `leaf-own-probe.log`, `leaf-own-probe.json`, both native run directories, reference route graphs and `extra-checks.json` under the evidence root. This verifies premise closure, not a novel derived thesis.

### Context limits and executed verification

An additional independent irreducible-context probe keeps both exact commitments through all five attempts, logs k=0/refused, and raises a search-scoped BudgetStop. It makes zero provider dispatches and leaves the shared budget unhalted. Exact evidence is therefore exempt from shrinking, not exempt from counted admission. A large indispensable set can still refuse locally; useful non-exact evidence remains subject to heuristic selection.

Fresh focused pytest: **90/90 passed**, no skips, exit 0, 141.15 seconds. Eight files cover context slicing, stance, alignment, guidance, cross-paper policy, model calls, CLI and native CLI replay. After pytest, the unchanged integration runner executed **31/31 selected mutation/restoration pairs**, including both new exact-match controls and the existing stance, matching, bridge, context-bound and local-refusal controls. Every mutation caused an assertion/test failure and every restored case passed. Exact command, selection and transcripts are retained in `pytest-result.json`, `pytest.log`, `control-manifest.json`, `control-results.json`, `verification.log` and `controls/`.

All **231 tracked-file hashes** match before and after verification. Both the isolated clone and the pilot checkout remain clean at the reviewed commit; git diff --check passes. Receipts: `source-before.json`, `source-after-controls.json`, `final-verification.json`. Evidence root: `/home/dev/ara-work/kappa4-r24-checkout/runs/kappa4-r24/`.

This is a scoped re-review, not a fresh full-suite/full-control run or a repetition of the full historical novelty matrix and real-source fork. No paid-model accuracy, live pilot success or useful synthesis is claimed. Previously disclosed attribution/definition classifier dependencies remain.

**2 findings, 2 placed:** repaired exact-leaf omission and retained stance semantics in “R23-F1 resolved”; indispensable-context behavior, verification scope and live/model limits in “Context limits and executed verification”. No unresolved blocker remains in this scope.

DONE kappa4 r24 verdict=merge blocking=0 tests=90/90 negctl=pass

## Re-review round 25 — 2026-10-28

Reviewed `68ca9654537286c98fbd11cffb20f5f32481508b` against `9b9999730c32b4dd0f06ef80a075920633d1acc9`, including `briefs/xi-round-25-addendum.md`. **Verdict: fix-first; two blocking findings.** Review, offline probes, pytest and temporary mutations ran in `/home/dev/ara-work/kappa4-r25-checkout`. No paid calls, delegation, source fixes or commits occurred. The parallel pilot was not modified or evaluated.

### R25-F1 — Blocking: formatting a named hedge bypasses both downgrade and closure checks

[ara/engine/routes.py:14](/home/dev/ara-work/kappa4-r25-checkout/ara/engine/routes.py:14) matches literal spaces in `to some extent`, `in part` and `not fully`. Runtime downgrade and engine CQ closure both use this same predicate, so neither boundary recognizes whitespace-equivalent versions.

The native reproduction proposes fresh S over endorsed P/Q/R from three papers, licenses a sign step from P/Q, and supplies the same valid frozen R citation for its CQs. Only answer formatting changes:

| CQ answer with answered=true | Downgrade receipts | Native route / default selection |
| --- | ---: | --- |
| `To some extent, P` | 2 | OPEN; excluded |
| `To some\nextent, P` (actual newline) | 0 | CLOSED-derived; selected |
| `To some extent, P` (nonbreaking space) | 0 | CLOSED-derived; selected |

The target, inference, frozen evidence and support IDs are unchanged. These are full proposal → search → selection results, not just regex checks. The route is admitted as though the explicitly partial answers were complete. `To a limited extent, P` and `P is plausible, but the evidence is insufficient.` also close without downgrade; the whitespace-equivalent named hedge alone establishes the blocker without relying on a broad interpretation of hedge semantics.

Required repair: normalize Unicode/whitespace before applying the shared hedge policy, cover equivalent partial-answer wording conservatively, and add native regressions that cannot become selectable through either runtime or direct engine CQ handling. Preserve original answer text and supporting IDs in the disclosure. Do not weaken the evidence gate to obtain closure.

Evidence: `cq-probes.py`, `cq-probes.json`, `cq-probes.log`, and `cq-extent*`, `cq-limited`, `cq-insufficient` native run directories under the evidence root.

### R25-F2 — Blocking: stance conflicts ignore identical frozen content definitions

The addendum explicitly requires matching endorse-versus-attack conflicts on “the same formula or the same content definition.” [ara/runtime/gaps.py:65](/home/dev/ara-work/kappa4-r25-checkout/ara/runtime/gaps.py:65) instead compares canonical formulas or raw commitment text. It never consults the catalogue definitions for this comparison; definitions are used only afterward for open-problem markers.

A validated native freeze contains endorsed `a=P` from paper a, attacked `b=Q` from paper b, and endorsed `c=R` from paper b. P and Q have the **identical frozen definition S**, but different formula names and commitment texts. Detection returns zero gaps, logs no stance conflict, and sends zero gap-resolution proposal requests. A fresh F(a) candidate is retained only as a general target with no gap obligation.

Control runs changing the conflicting pair to the same formula, or to identical commitment text, each detect one stance conflict and make a gap-resolution request. Distinct definitions correctly produce no conflict. All freeze/catalogue/provenance bytes remain unchanged. This is a missed explicitly requested exact-content case, not a demand for fuzzy semantic matching or a consequence of novelty rejection.

Required repair: compare bound frozen content as well as canonical formulas, preserving logical structure, predicate arguments and polarity. Do not equate formulas merely because they share a definition term. Add native tests with distinct symbols/texts and identical frozen content, plus structurally different negatives, and verify that the resulting gap reaches proposal and retains its support obligation.

Evidence: `gap-probes.py`, `gap-probes.json`, `gap-probes-final.log`, and `gap-final-*` native directories. The earlier exploratory run used S as the target and encountered its independent definition-restatement gate; the retained final reproduction uses fresh F(a) to remove that confound.

### CQ retrieval and scheme correction: verified boundaries

The eleven independent CQ scenarios confirm that an endorsed frozen ID outside both proposal premises and the presented retrieval slice can support a CQ. Attacked/reported citations remain OPEN and unselectable; an invented ID fails native validation with `unknown CQ T id`. Ordinary `Partly`, `To some extent` and `Not fully` answers downgrade with their original text/IDs preserved. R25-F1 identifies the missing hedge variants. This verifies membership and stance, not the truth or semantic adequacy of a model's answer.

Retrieval ranking passed 100 permutations of commitment, catalogue and provenance-row order. The highest shared-symbol candidate remains first; logged input hashes match actual dispatched inputs, and total context counts include the output allowance. Owning tests exercise lexical-only definition matches, shrinking and exclusion of restricted evidence. Projection leaves full frozen hashes and full-T citation validation authoritative.

Six additional native scenarios force an initial invalid bank proposal, a corrected sign proposal with unsupported CQs, then the scheme-choice correction. Every scenario uses exactly three total proposal batches: two initial licensing attempts and one CQ-driven attempt. The correction inventory excludes the attempted sign scheme. A supported best-explanation alternative closes, retaining the original OPEN route. Unsupported, repeated, unknown, overfull and invalid-slot alternatives do not close. Proposal indices remain unique in traces. No further CQ-driven batch occurs. Evidence: `retry-probes.py/json/log`, `retry-*`, `retrieval-order.py/json` and `retrieval-order/`.

### Gap determinism, resolution obligations and unchanged gates

A placeholder inventory containing all three gap kinds passed 40 input-order permutations, including catalogue and provenance ordering. Gap records, witnesses and checks are identical; T, catalogue and provenance are unchanged. The native tests cover a three-commitment inconsistent set, same-paper exclusion, logged discovery, explicit open markers, required resolution classification, gap-first ordering, 30-target retention, and preservation of gap metadata through actual engine search and compressed trace/graph serialization. Missing gap-side support prevents default derived selection; attacked commitments do not become positive support.

The detector remains a bounded witness/lexical procedure, not a semantic or exhaustive inconsistency census. For stance conflicts, its attacked-paper support group contains that paper's endorsed commitments, not the attacked statement itself; semantic relevance still depends on proposal/classifier judgment. Whole-T novelty remains unchanged, so inconsistent T may entail every proposed thesis and prevent resolution-target admission. R25-F2 limits the stance-conflict census further.

All nine prior independent harnesses were replayed and their full expected matrix asserted. Thirteen old/entailed formula packages reject; fresh R and F(b) remain eligible. The five prior R1/wrapper proofs remain structural and nonselectable. Genuine R remains CLOSED-derived/selectable; {P,P -> Q} still proves Q by licensed modus_ponens, while Q is excluded as a novel target. Explicit/automatic frozen-name collisions and classifier-detected restatements reject. The deliberately false-positive definition classifier still admits its alias: that previously disclosed model-accuracy dependency remains. Receipts: `replay-results.json`, `probe-verification.json` and the individual native directories. No additional novelty/licensing bypass emerged in this matrix.

### Real-source replay, verification and restoration

Reran the inspected `tools/offline_gap_cq.py` on the real fork-5 freeze with network connections prohibited. All three frozen source artifacts remain unchanged and match the offline copies byte-for-byte. The native fake-provider census reproduces **12/12 CQs with retrieval leads**, **gaps_found=3** (three open-problem candidates, zero detected contradictions/stance conflicts), and **3/3 fake resolution targets retained**, from nine bounded gap-proposal calls. Every fake CQ answer is unanswered with no supporting IDs. The maximum calibrated request estimate is **36,305 input-plus-output tokens**. These are candidate leads and fake semantic judgments, not substantive resolutions or measured live usage; zero detected stance conflicts is subject to R25-F2. Receipts: `offline-census.py/log`, `fork5-census/summary.json`, `fork5-census/source-hashes.json` and its native event log.

Fresh scoped pytest: **286 passed / 286 collected**, no skips, exit 0, 413.04 seconds. Twenty files cover new CQ/gap behavior, context, stance, alignment/guidance, cross-paper policy, calls, target pools, novelty/contribution, reports, search failures, engine search/tracing/licensing, shared types and native CLI replay. Exact command/output: `pytest-result.json`, `pytest.log`.

Only after all probes and pytest exited, the unchanged integration runner executed **97/97 selected mutation/restoration pairs**, including all 18 new CQ/gap controls and the affected existing stance, context, paper, target and novelty controls. Every mutation caused its expected test failure, every restoration passed. These existing controls do not cover the two blockers above. Manifest and full transcripts: `control-manifest.json`, `control-results.json`, `controls.log`, `controls/`.

All **236 tracked-file hashes**, including **19 temporarily mutated files**, match the pre-verification snapshot. The isolated clone remains clean at the reviewed commit; git diff --check passes. At the final observation, the shared xi checkout still pointed to that commit but contained concurrent uncommitted changes. Those changes are outside this pinned review and were left untouched; the report does not claim to validate the shared working tree. The observed status and differing paths are recorded in final-verification.json. Evidence root: `/home/dev/ara-work/kappa4-r25-checkout/runs/kappa4-r25/`; checkout/restoration receipts: `source-before.json`, `source-after-controls.json`, `final-verification.json`.

These are this review's scoped checks, separate from xi's full-suite/full-control receipt. No paid-model accuracy, faithful formalization, CQ truth, semantic independence, useful synthesis or parallel-pilot success is established.

**6 findings, 6 placed:** hedge bypass in R25-F1; missing definition-based stance conflict in R25-F2; CQ integrity and bounded correction in “CQ retrieval and scheme correction”; deterministic gap behavior and resolution limits in “Gap determinism”; preserved prior gates and classifier boundary in that same section; real-source census, executed scope and restoration limits in “Real-source replay, verification and restoration”. Both R25-F1 and R25-F2 block approval.

DONE kappa4 r25 verdict=fix-first blocking=2 tests=286/286 negctl=pass

## Re-review round 26 — 2026-10-28

Reviewed `80a344892d9acd1933bf47c1b6fd8fd986bbee5b` against `68ca9654537286c98fbd11cffb20f5f32481508b`, including `briefs/xi-round-26.md` and both R25 blockers. **Verdict: merge; R25-F1 and R25-F2 are fixed, with zero blocking findings in this re-review.** The review ran directly in `/home/dev/ara-work/kappa4-r26-checkout`, with fake providers and no paid calls, delegation, production fixes or commits. The shared pilot checkout was not modified.

### R25-F1 resolved: formatted hedges cannot close the native route

Replayed the original proposal → licensed sign step → CQ → default selection reproduction. All 15 scenarios meet their expected outcomes. The ordinary supported answer still yields selectable CLOSED-derived; attacked/reported evidence stays OPEN and invented IDs fail validation. Newline and nonbreaking-space versions of “To some extent” now downgrade and stay OPEN. Limited-extent, insufficient-evidence, markdown, underscore, fullwidth Unicode and tab variants also stay OPEN and unselectable. Original answer text and supporting IDs remain available in the downgrade receipts. The same shared predicate protects runtime answers and direct engine closure.

The repair is a conservative lexical screen, not general semantic validation of an answer. Frozen T, catalogue and provenance bytes remain unchanged. Evidence: `cq-probes.py/json/log` and `cq-*` native directories under the evidence root.

### R25-F2 resolved: identical frozen definitions produce the stance obligation

The original distinct-symbol/distinct-text reproduction now finds one stance conflict when endorsed P and attacked Q have the identical frozen content definition S. It makes a gap-resolution proposal and retains fresh F(a) with the actual gap attached. Its support groups are `[['a'],['c']]`: endorsed evidence from each paper, excluding attacked `b`. Same-formula and same-text controls still find the gap; distinct definitions do not. The fake semantic classifier returns compatible in these cases, isolating the deterministic definition-matching repair. All frozen artifacts remain unchanged.

Source inspection and owning regressions verify that substitution preserves formula structure, polarity, predicate arguments and binders, and requires content-definition semantics. The broader deterministic gap inventory remains identical across 40 input-order permutations. Evidence: `gap-probes.py/json/log`, `gap-final-*`, and scoped pytest/control receipts.

### Semantic discovery: bounded model judgments, immutable inputs

An independent ranking oracle and 100 permutations of commitment/catalogue/provenance order produce the same retained pairs. Limits 0, 1, 2, 4 and 60 are respected; negative, boolean, noninteger, string and null limits refuse. Same-paper pairs and pairs with no endorsed side are excluded. The ranking remains definition-term overlap, content overlap, then IDs; selected-pair bounds do not claim exhaustive retrieval.

Native fake calls exercise all four schema outcomes. Only contradicts/in_tension create semantic gaps. The request contains just the pair, relevant definitions, verified roles and frozen hashes, with an empty global topic; the existing provider, schema validation, accounting, cache and MODEL receipts remain authoritative. A repeated discovery uses cache, with no additional provider dispatches. Every classification/gap receipt explicitly says `formal_contradiction=false`; the gap kind is semantic_conflict and reports call these semantic judgments, not formal contradictions. Restricted views identify disagreement without becoming positive support. T and all three frozen files remain byte-identical.

Invalid enums, extra output fields, empty reasons and overlong reasons are rejected and logged as unclassified; later pairs continue. Injected search-local refusal likewise skips only that pair. Injected run-wide BudgetStop and infrastructure errors propagate. Owning tests additionally exercise real counted-context refusal before dispatch. Evidence: `semantic-probes.py/json/log` and adjacent native failure directories.

On the real fork-5 freeze, the inspected offline tool independently reproduces **7,693 eligible pairs / 60 retained / 60 fake classifier calls**. Cycling the four labels yields 30 synthetic semantic gaps and one accepted fake candidate. Maximum calibrated classifier input-plus-output estimate: **6,656 tokens**. Network connections were prohibited; copied and original frozen artifacts match before/after hashes. These are plumbing and retrieval counts, not evidence of actual literature disagreements. Lexical retrieval can miss conflicts with no shared words; fake judgments establish neither classifier accuracy nor useful resolution. Evidence: `offline-census.py/log`, `fork5-census/summary.json` and `source-hashes.json`.

### Tier findings and resolution candidates are reported without claiming resolution

Three independent native paired-search runs each record one Tier 1 repair and one Tier 2 conflict. Tier 2 obligations retain actual positive/negative conclusions, route IDs and each route's endorsed support. The linked report JSON equals the native conflict projection; HTML and methodology expose the findings and their limits. No repair edits T.

A fresh S resolution candidate passes and remains explicitly `proposed_not_searched`. A candidate whose fake classifier says it does not resolve the gap, and an entailed P candidate, are both rejected within three proposal attempts. Existing target novelty, source-stance and route licensing remain authoritative. This verifies proposal integration, not automatic follow-up search or resolved conflict.

Independent generation probes reject stale tier findings after a new search boundary and candidate receipts with the wrong analyses hash. Missing/empty analyses do not assert absence of conflict. Semantic classifications are a historical receipt list, including cache replays, rather than a deduplicated current-generation conflict count; current Tier1/Tier2 counts and resolution candidates are separately generation/hash scoped. Evidence: `report-probes.py/json/log`, `tier-native-*`, `tier-report-*`, and the generation cases in `semantic-probes.json`.

### Executed verification, restoration and limits

Fresh scoped pytest: **495 passed / 495 collected**, no skips, exit 0, **856.22 seconds**. Thirty files cover the new semantic behavior, CQ/gap fixes, target and contribution gates, stance and paper policy, context, engine licensing/search/tracing, native CLI replay, reports, schema/preflight and search publication/recovery. Exact command and output: `pytest-result.json`, `pytest-files.json`, `pytest.log`.

Only after every independent probe and pytest exited, the unchanged integration runner executed **116/116 selected mutation/restoration pairs**, comprising all 19 round-26 additions and the 97 controls selected in R25. Every mutation exited 1 with a failing-test summary; every restoration exited 0 with passing tests. Transcripts were checked for actual test failures rather than collection/syntax errors. This is a selected control census, not a rerun of all 600 controls. Evidence: `control-manifest.json`, `control-results.json`, `control-transcript-verification.json`, `controls.log` and `controls/`.

All **242 tracked-file hashes**, including **22 temporarily mutated source files**, match the pre-verification snapshot. The isolated clone remains clean at the reviewed commit and git diff --check passes. At final observation, the shared xi checkout still pointed to `80a3448` but contained concurrent tracked and untracked changes. Those changes were left untouched and are outside this pinned review. Source/restoration and observed-status receipts: `source-before.json`, `source-after-probes.json`, `source-after-controls.json`, `final-verification.json`. Independent probe expectations are recorded in `probe-verification.json`.

Evidence root: `/home/dev/ara-work/kappa4-r26-checkout/runs/kappa4-r26/`. These independent checks are scoped, separate from xi's full-suite/full-control receipt. No paid-model accuracy, faithful formalization, CQ truth, useful synthesis, live preflight or parallel-pilot success is established. Whole-T novelty retains its known limitation on inconsistent T. The new classifier schema requires a refreshed live Codex preflight before live use; this review performs no live preflight.

**5 findings, 5 placed:** fixed hedge bypass in “R25-F1 resolved”; fixed definition-based stance conflict in “R25-F2 resolved”; bounded model discovery and immutable-input/accuracy limits in “Semantic discovery”; tier reporting, generation binding and unsearched resolution status in “Tier findings”; executed scope/restoration and remaining live/model limits in “Executed verification”. No unresolved blocker identified in this scope.

DONE kappa4 r26 verdict=merge blocking=0 tests=495/495 negctl=pass
