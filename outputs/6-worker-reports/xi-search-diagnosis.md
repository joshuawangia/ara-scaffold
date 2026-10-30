**Xi Round 11 — offline search diagnosis**

The primary failure is loss of formula identity across the search interfaces. All 10 positive targets received a proposal whose conclusion text exactly matched the goal, yet independently formalizing that text changed its formula. Every positive route therefore stopped at its root with `CONCLUSION_MISMATCH`. Across the 20 completed jobs, 16 of 22 proposals were discarded for this reason. Increasing depth or node caps would not address this failure.

There is a second representation barrier: all 10 targets have **zero symbol overlap** with frozen T, and all 14 formalized premise occurrences also have zero overlap. T contains 166 distinct, standalone atoms, one per commitment, with no predicates, constants, connectives, or shared signatures. The targets are related to the literature in ordinary language, but their formal representations are disconnected.

This is diagnosis only. No source/config changes, model calls, provider creation, push, or new paid activity were performed. The completed integration/F2 revision remains `4c1c76f` on `feat/run-report`. Its earlier test gates were not repeated for this read-only analysis.

**Evidence and counting boundary**

Primary input: `/home/dev/ara-scaffold/runs/codex-pilot-2/`. Supporting report: `/home/dev/ara-work/reports/overnight/codex2-final/`, pilot `run-39` (display Run 40). The main chain has 7,713 records, ending at hash `6c647d499be75d4464d0041781372150ab71327aac4e85ea9709d604dde2f3c6`, timestamp `2026-10-26T14:33:48.759206+00:00`, matching the report snapshot. The main chain and anchor, all 21 nonempty journal chains and anchors, their main-log publication hashes and exact copied event sequences, and 20 sealed sidecar hashes and trace semantics were verified. `commitments.json` equals the logged frozen/merged inventory. The report records code revision `c8194b5`; the inspected search/licensing/call/construction source has no changes between that revision and Xi's current head.

Final-job counts use original batch `820e18fd2bf74627b10e7f9031b34778`, except job 7, which uses recovery batch `0efc95b1922a4487836b14e6687e99d2`. The original job-7 journal is retained separately as interrupted history. The report's 21st trace is unsealed; its contents were not used to infer completed search structure. Repeated publication markers do not count as repeated execution. Model-written route summaries were not used as causal proof.

Frozen T has 166 commitments from **24 represented paper IDs**. `build_t_merged.source_ids` has 26 IDs, including two with no retained commitments (`rothschild2012`, `kolodnymacfarlane2010`); it must not be used as the retained-paper count.

Machine-readable evidence is in [xi-search-diagnosis-evidence](xi-search-diagnosis-evidence/): `metrics.json` contains per-job paths, main publication sequence references, sidecar receipts, proposals, decisions, graphs, mapper candidates, and conclusion comparisons. `inputs.json` pins the 65 consulted primary files. `solver-check.json` contains the offline entailment checks. Analysis scripts and intermediate verified extracts are included for reproduction.

**Ranked causes and smallest proposed changes**

1. **Goal/conclusion formula drift — observed direct cause; highest priority.** Of 22 proposals, 16 (72.7%) failed `CONCLUSION_MISMATCH`: all 10 positive roots plus 6 descendant proposals. All 22 conclusion texts exactly equal their corresponding goal text; 15 of the 16 mismatches even have disjoint goal/conclusion symbol sets. This is not primarily a proposer paraphrasing error. Targets arrive with formulas from `propose_targets`; `Licenser.formalise` preserves those, but `Licenser.check` creates a new unformalized `Proposition('conclusion', text)`. `ModelCalls.formalise` receives only that proposition, with no goal formula, T, or symbol catalogue. It produces a fresh representation, which fails canonical equality. See `ara/engine/licensing.py:39`, `:55`, `ara/runtime/calls.py:912`, `:930`, and `prompts/formalise.txt:1`.

   A useful contrasting observation is already in the run: all four admitted root proposals are negation jobs, whose goal text is serialized AST (`ara/types.py:152`). Those four conclusions retain the goal formula. Two other negation proposals also retain it and proceed to solver rejection. This supports the representation diagnosis without an additional model experiment. For example, job 0 journal seq 11 proposes the exact target text; seq 16 formalizes it into a predicate with two constants instead of the supplied atom; seq 17 rejects it.

   Smallest fix to evaluate first: when conclusion text exactly equals the current goal text, bind the conclusion to the existing goal proposition/formula instead of re-formalizing it. Prefer an explicit current-goal reference in the proposal contract. Do not overwrite a different-text conclusion or relax canonical equality. Regression home: `tests/engine/test_licensing.py` plus `tests/runtime/test_calls.py`; use placeholder text with a deliberately inconsistent formalizer, and ensure mismatching text/formula still fails. This would remove the observed early identity rejection, but does **not** by itself establish premise licensing or route closure.

2. **Frozen-T/search symbol contract is disconnected — observed closure barrier.** Each target is a fresh atom absent from T's 166 signatures; its negation adds no symbols. All 14 formalized premise occurrences are likewise disjoint from T. `map_leaf` returned a valid non-open commitment ID 14 times out of 25 calls, but none of these candidates passed formula equality. Four more T IDs were supplied directly in admitted proposal premises, also with no closure. There were 29 `NOT_IN_COMMITMENTS` decisions and zero `FROZEN_COMMITMENT` decisions. Construction enforces symbol declarations and reuse evidence (`ara/runtime/construction.py:519`), while target proposal and formalization do not carry this contract (`ara/runtime/calls.py:912`, `:930`). Terminus correctly requires the cited T formula to equal the leaf (`ara/engine/terminus.py:5`). A mapper suggestion is not a license.

   The frozen formulas also flatten all 166 commitments to distinct atoms: no encoded implication, conjunction, quantifier, or predicate remains to connect them deductively. An offline call to the production entailment function, using all frozen formulas against each of the 20 root goals, returned `SOLVER_COUNTEREXAMPLE` 20/20 times. The all-T-atoms-true assignment leaves every fresh target atom unconstrained. This proves lack of classical entailment for these encodings; it does not prove lack of semantic relevance or impossibility of every bank-licensed defeasible route.

   Smallest coherent next fix: carry the immutable T symbol catalogue and goal/slot bindings through target and premise formalization; include catalogue identity in cache inputs. Reuse a frozen formula only for an explicit, validated commitment reference with matching evidence text, or after an auditable alignment step. A paraphrase or shared subject alone is insufficient. Reject or explicitly diagnose disconnected target vocabulary before a costly search. Preserve meaningful connective/relational structure during future T construction where supported by evidence; do not turn every author-attributed claim into a freely interchangeable unqualified proposition. Keep the present freeze immutable. Tests belong in `tests/runtime/test_calls.py`, `tests/runtime/test_construction_stages.py`, and `tests/engine/test_search.py`, with placeholder catalogues and negative controls for wrong attribution/reference.

3. **One proposal batch per leaf amplifies the representation failures — observed termination mechanism.** The 29 proposer invocations returned exactly one proposal 22 times and an empty list 7 times; there were no alternative proposals in any batch. The engine expands a leaf once, and blocks it with `NO_ADMITTED_PROPOSAL` when the batch produces no licensed child (`ara/engine/search.py:136`, `:201`). All 25 blocked leaves stopped for that reason. Sixteen jobs terminated after a single root expansion: 10 conclusion mismatches, 5 empty proposal batches, and 1 solver counterexample. The other four jobs each admitted just one inference, then blocked their remaining leaves.

   After fixing identity and T alignment, consider one bounded correction attempt carrying the actual rejection reason, and/or requesting a small diverse proposal batch. A correction needs distinct feedback/cache input, an explicit attempt budget, and a recorded terminal reason. An empty proposal may be appropriate; do not force invented support. Test in `tests/engine/test_search.py` and `tests/runtime/test_search_failures.py`. No evidence supports increasing depth/node limits first: every job had depth cap 6 and node cap 500, reached depth 0 or 1, created only 1–4 nodes, and ended `truncated=false`; zero depth/node-cap, cycle, or timeout decisions occurred. Maximum node use was 4/500 (0.8%). Forward-pass depth 2 is downstream analysis, not a remedy for rejected cuts (`ara/engine/conflicts.py:47`).

4. **Some proposed deductions do not instantiate an entailing sequent — observed smaller cause.** Two proposals reached the solver and received `SOLVER_COUNTEREXAMPLE`: negated target6 at the root, and negated target7 at a descendant. Both use `modus_tollens`; their conclusion formalizations match the respective goals, so these are distinct from the 16 conclusion mismatches. Independently formalized slots do not supply a sequent that entails the conclusion. Keep solver rejection and bank-shape checking (`ara/engine/licensing.py:60`, `:80`). The smallest improvement is to formalize a proposal's slot substitutions together in the same vocabulary, with explicit shared metavariable bindings, and feed the concrete rejection back into the bounded correction path. Regression home: `tests/engine/test_licensing.py`; valid placeholder modus tollens must pass, mismatched slot substitutions must fail. The recorded data does not establish that a faithful re-encoding of either rejected argument would be valid.

5. **Proposal T-reference hygiene is weaker than mapper validation — latent failure exposed by inspection.** Across 59 premise slots in the 22 proposals, 23 claim a non-open T reference; **5 of those 23 are absent from frozen T**, spread across three proposals (jobs 6, 15, 18). Four are citation strings supplied where commitment IDs are required; one names an absent item. All three affected proposals were already rejected for conclusion mismatch, so these bad IDs did not cause the observed early root failures. All four direct T references actually reached by admitted inferences are valid IDs, and still fail formula equality as described above. `map_leaf` checks membership (`ara/runtime/calls.py:934`), but `propose_cuts` currently only constructs `Proposal` objects (`:924`). Add membership validation and targeted correction at that runtime boundary, preserving the engine's independent closure checks. Test in `tests/runtime/test_calls.py` with unknown IDs and citation-vs-ID confusion. Fixing only cause 1 would expose these additional failures.

**Per-job measurements**

Job indices are zero-based. `+` means target, `−` means negation. `M/F/P/C` are MODEL receipts for `map_leaf/formalise/propose_cuts/answer_cq`; cache replay is included. `Reject` counts engine proposal prunes, while `Val` counts schema/output rejection receipts. `CM` = `CONCLUSION_MISMATCH`; `SC` = `SOLVER_COUNTEREXAMPLE`. Every route is OPEN, every terminal block reason is `NO_ADMITTED_PROPOSAL`, and no job is truncated. `Depth` is proof-node depth, not report state-ancestry depth.

| Job | Target | Nodes created / expanded | Depth | M/F/P/C | Proposals / admitted | Reject | Val | Terminal blocks |
|---:|---|---:|---:|---|---:|---|---:|---:|
| 0 | target1 + | 1 / 1 | 0 | 1/1/1/0 | 1 / 0 | 1 CM | 0 | 1 |
| 1 | target1 − | 1 / 1 | 0 | 1/0/1/0 | 0 / 0 | 0 | 0 | 1 |
| 2 | target2 + | 1 / 1 | 0 | 1/1/1/0 | 1 / 0 | 1 CM | 0 | 1 |
| 3 | target2 − | 1 / 1 | 0 | 1/0/1/0 | 0 / 0 | 0 | 0 | 1 |
| 4 | target3 + | 1 / 1 | 0 | 1/1/1/0 | 1 / 0 | 1 CM | 0 | 1 |
| 5 | target3 − | 1 / 1 | 0 | 1/0/1/0 | 0 / 0 | 0 | 0 | 1 |
| 6 | target4 + | 1 / 1 | 0 | 1/1/1/0 | 1 / 0 | 1 CM | 0 | 1 |
| 7 | target4 − | 3 / 3 | 1 | 2/4/3/2 | 2 / 1 | 1 CM | 0 | 2 |
| 8 | target5 + | 1 / 1 | 0 | 1/1/1/0 | 1 / 0 | 1 CM | 0 | 1 |
| 9 | target5 − | 1 / 1 | 0 | 1/0/1/0 | 0 / 0 | 0 | 0 | 1 |
| 10 | target6 + | 1 / 1 | 0 | 1/1/1/0 | 1 / 0 | 1 CM | 0 | 1 |
| 11 | target6 − | 1 / 1 | 0 | 1/3/1/0 | 1 / 0 | 1 SC | 0 | 1 |
| 12 | target7 + | 1 / 1 | 0 | 1/1/1/0 | 1 / 0 | 1 CM | 0 | 1 |
| 13 | target7 − | 4 / 3 | 1 | 3/7/3/0 | 2 / 1 | 1 SC | 0 | 2 |
| 14 | target8 + | 1 / 1 | 0 | 1/1/1/0 | 1 / 0 | 1 CM | 0 | 1 |
| 15 | target8 − | 4 / 4 | 1 | 2/7/4/2 | 4 / 1 | 3 CM | 0 | 3 |
| 16 | target9 + | 1 / 1 | 0 | 1/1/1/0 | 1 / 0 | 1 CM | 0 | 1 |
| 17 | target9 − | 3 / 3 | 1 | 2/5/3/2 | 3 / 1 | 2 CM | 0 | 2 |
| 18 | target10 + | 1 / 1 | 0 | 1/1/1/0 | 1 / 0 | 1 CM | 0 | 1 |
| 19 | target10 − | 1 / 1 | 0 | 1/0/1/0 | 0 / 0 | 0 | 0 | 1 |

Totals: **30 nodes created, 29 expansions, 22 proposals, 4 admitted inferences, 18 proposal rejections, 25 terminal blocks, 20 OPEN routes, 0 closed T leaves**. One scoped assumption accounts for the created node that is not expanded. The four inferences are: target4− `verbal_classification`, target7− `reductio_ad_absurdum`, target8− `negative_consequences`, target9− `commitment`. Their proof-node counts are 3, 4, 4, 3. Three routes cite T in CQ answers (6 `CQ_SUPPORTED` decisions); CQ evidence does not close their open premises. Thus “no T” should be qualified as no closed T leaves for these four routes; the 16 single-root routes contain no inference or CQ evidence.

| Call kind | Accepted MODEL receipts | Cache replay | Actual dispatches in final-job journals |
|---|---:|---:|---:|
| map_leaf | 25 | 2 | 23 |
| formalise | 36 | 3 | 33 |
| propose_cuts | 29 | 3 | 26 |
| answer_cq | 6 | 2 | 4 |
| Total | 96 | 10 | 86 |

The recovered job 7 has 11 accepted receipts, 10 replayed from cache and one newly dispatched formalization. The other 19 final jobs have no replayed receipts. All 96 final-job outputs passed runtime validation. The 18 engine prunes are therefore **not** schema rejections. Goal formulas were already supplied by target proposal; there are no extra per-job root-formalization calls hidden in these counts.

**Per-target symbol alignment and content relevance**

Metric: `overlap(target) = |S(target) ∩ S(T)| / |S(target)|`, where a signature is `(name, kind, arity)` for atoms/predicates and `(name, constant, 0)` for constants. Logical operators and bound-variable names are excluded. Every target has exactly one atom and no predicates or constants; T has 166 atom signatures and zero predicates/constants. Name-only overlap is also zero. The mean across the 10 targets is **0.000 (0%)**; the same mean applies across both polarities. This is signature identity, not substring similarity.

| Target | Atom signature name | Shared / total | Overlap |
|---|---|---:|---:|
| target1 | `epistemic_modal_semantics_tracks_information` | 0 / 1 | 0% |
| target2 | `assessment_sensitivity_epistemic_modals` | 0 / 1 | 0% |
| target3 | `worldly_information_safety` | 0 / 1 | 0% |
| target4 | `epistemic_contradictions_genuine` | 0 / 1 | 0% |
| target5 | `classical_inference_epistemic_levels` | 0 / 1 | 0% |
| target6 | `dynamic_information_update_epistemic_modals` | 0 / 1 | 0% |
| target7 | `epistemic_modal_assertion_pragmatics` | 0 / 1 | 0% |
| target8 | `probability_measure_semantics_epistemic_vocabulary` | 0 / 1 | 0% |
| target9 | `ways_of_thinking_de_re_epistemic_modals` | 0 / 1 | 0% |
| target10 | `epistemic_modals_contextual_group_underspecification` | 0 / 1 | 0% |

The evidence does **not** support “the targets are off-topic” as the main explanation. Every positive root mapper selected a real T candidate (10/10). Inspection of those texts finds thematic links for all ten, with especially close formulations for targets 2, 3, 5, 8, 9, and 10. Examples by reference, without claiming formal equivalence:

| Target | Related frozen commitment | What the comparison supports |
|---|---|---|
| 2 | `macfarlane2014:r103-113-refine:n7` | Same distinction being targeted; separate formula names |
| 3 | `beddorgoldstein2021:r1-23:c_info_sensitive_safety` | Closely corresponding condition; target atom not the T atom |
| 5 | `hollidaymandelkern2024:r1-17:d_epistemic_levels` | Same within/across-level contrast; distinct encodings |
| 8 | `moss2015:union:item:moss2015:salvage:3870505846b36fcb:moss2015:r1-10:n_thesis` | Same proposed representational approach; attribution and qualifications still matter |
| 9 | `ninan2018:r23-45:n58` | Same dependence described in target; provenance includes omitted support |
| 10 | `vonfintelgillies2011:union:item:vonfintelgillies2011:salvage:102d49a275b6d08b:vonfintelgillies2011:r1-11:a_both_readings` | Same underspecification issue; provenance includes omitted support |

The mapper also suggested the same T ID for both polarities of target5, reinforcing why a model-selected ID cannot establish identity or closure. The weakest step would be to equate nearby prose automatically. The right diagnostic distinction is: the content supplies relevant candidates, but the logged formal encoding and admitted steps do not connect them into a proof. Whole-T counterexamples constrain classical entailment only; defeasible bank routes require their own valid premises and CQs.

**Historical validation failure and limits of the diagnosis**

Finding 6: the original job 7 was interrupted and has no sealed completed trace. Its journal has 12 `call_start` and 12 `response_received` events but only 11 MODEL receipts: 10 accepted and 1 rejected formalization (seq 61, followed by `validation_retry` at seq 62). The rejected response contains malformed connective arities; the journal records `ValidationError`, without a detailed schema path. The next response was received but had no terminal MODEL receipt in that journal. This history explains the need for recovery, not the sparsity of the 20 final routes. Across both the final-job journals and this interrupted journal, there are 98 actual dispatches, 106 accepted MODEL receipts including 10 cache replays, 1 rejected receipt, and 1 received response without a terminal MODEL receipt in its original journal. These are execution counts, not a new cost/accounting reconciliation. Historical unsealed/unknown-usage gaps remain visible in the supporting report. Do not treat the failed attempt as a 21st completed search or infer its graph from an unsealed file.

There is no completed-job evidence of budget STOP, context refusal, validation exhaustion, solver timeout, node cap, or depth cap removing these steps. Requested model identity is `gpt-6-luna` via Codex CLI; serving identity is marked unverified in the recorded responses. No model-quality comparison or claim that a different model would solve the problem is established by this offline analysis. Proposed fixes and regression tests above were not implemented or executed.

**Secondary source-quality observation**

Finding 7: two inspected commitment texts (the target8 and target10 references above) retain serialization-like trailing fragments. This is a source-text fidelity concern to inspect against the extracted records before future construction; it is not evidence that the formula identity failures were caused by those fragments. The diagnostic count is two observed examples, not an exhaustive text-quality audit. Preserve immutable evidence and trace any future cleanup to its source rather than silently editing frozen T. No cleanup was made here.

**Verification and handoff**

Executed offline: main/journal chain and anchor verification; exact publication event comparison; 20 sidecar hash and semantic validations; frozen artifact comparison; per-job receipt/graph counts; per-target/per-premise signature overlap; canonical goal/conclusion comparisons; and 20 production-solver entailment probes. Final verification: **65/65 pinned primary files are unchanged**, the repository is clean at `4c1c76fe34d00666d9fc2535b2f2d2eba380ab46`, and the frozen artifact matches both logged inventories; see `xi-search-diagnosis-evidence/final-verification.json`. This report does not claim a new pytest/control-runner result; Round 10 already completed those gates at `4c1c76f` (1033 passed, 4 skipped / 1037; 434/434 controls restored green).

7 findings, 7 placed: ranked causes 1–5 above; historical validation and evidence limits in finding 6; secondary source-text fidelity in finding 7. The recommended first change is exact-goal formula binding, followed by the T/search symbol contract, before any search-budget experiment.
