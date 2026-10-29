# Rho3 independent integration review

**Verdict: Sigma merge; Xi merge; 0 blocking findings.** No actionable code defect found in the source review, offline end-to-end exercises or complete validation run. This is a non-author, single-reviewer verification; no delegation, external review, paid calls or push occurred.

## Reviewed and merged revisions

| Role | Revision |
|---|---|
| Requested base | `b48d56f97286199cbd144fc441b2d92837bfdda9` |
| Sigma round 10 | `5fcd2b1a3dd76e15b565731f078aea7f2f74d536` |
| Xi round 17 | `fffb7c3cd1526d048ffda302fc877559eba5a2a5` |
| Committed integration merge | `7c7bdc839fa96c7eece54bd93d3961055162bf27` |

Scratch clone: `/home/dev/ara-work/rho3-integration`, branch `review/rho3`.
Sigma was merged onto the requested base first (`7835a53`), followed by Xi.
The only conflicts were the expected additive `DECISIONS.md` and
`tests/integration/negative_controls.py` conflicts; both sides were retained.
Every non-conflicting changed file matches its author revision exactly. The merged
runner contains all **510 unique controls**. See [merge-audit.json](rho3-evidence/merge-audit.json).
Author branches were not edited. This scratch merge is the deliverable integration,
not a push or a merge into the main checkout.

## Sigma: corrections, feedback and content provenance

Reviewed the construction lifecycle, transport/schema/admission boundary, resume,
source provenance, freeze and owning regressions against the round-10 brief.

- `construction.py:346` allocates a fresh allowance for each window, separately for
  `select_t_roots` and `build_t_batch`. The default is **2**. Corrections remain
  counted through native transport and admission. The second patch sees the first
  patch's accumulated candidate; invalid patches retain the active validation reason.
- Feedback names all offending commitment IDs and symbol names, with matched
  attribution phrases and the content-only-restatement instruction.
- `commitment_provenance.py:39` matches only a complete leading, source-known
  speaker/author plus `argues that`, `holds that`, or `claims that`, case-sensitively.
  Unknown speakers, nonleading/quoted/negated/conditional frames and missing `that`
  are not mechanically removed. A copied candidate prevents progressive peeling
  of nested frames across corrections. The remainder passes the same validator again.
- Each rewrite has a `definition_unframed` event and original-definition/author
  history in the hash-bound provenance. Source text, citations and stance survive.
  The independent native runs below verified those fields against extracted evidence.
  Rejected rewrite events can remain in the log without contributing frozen content.

**Pilot migration:** an old saved explicit limit of `1` remains `1`; set
`construction_targeted_corrections: 2` in the actual new run configuration. Plan
v12 binds the correction policy, so an old plan cannot silently resume with new
semantics. Completed or terminal refused windows do not replenish on resume.
The separate existing structure correction and transport retries are outside the
targeted-correction count. Existing request/run budgets still govern dispatch.
Deploy the updated provenance reader with construction: it accepts old sidecars,
but old strict readers cannot accept the new optional unframing history.

The lexical attribution screen is unchanged. It can still reject legitimate
content containing its trigger words; additional corrections do not prove faithful
paraphrase or semantic preservation. No unlogged rewrite was found.

## Xi: novel theses, rejection reasons and retained pool

Reviewed target proposal/classification, contribution checks, search callers,
licensing, route publication and the changed fixtures against the round-17 brief.

The proposer receives the actual versioned bank, slots and critical questions,
with placeholder examples of deduction, defeasible support and the conditional
consequent trap. The contract requires a new main proposition, rather than padding
an existing commitment with antecedents. Concrete rejection feedback includes the
candidate, checked polarity, full entailing commitment, explanation and applicable
conditional-consequent warning. Own-thesis failures carry the classifier reason.

An ordinary attempt requests **20** candidates and retains at most
`min(target_candidates, 10)`. There are at most **three proposal attempts** (two
corrections). Passing targets survive in stable attempt/response order. Retained
IDs and canonical structural formulas are deduplicated. Rejected, duplicate,
retained and surplus candidates are logged individually. Short pools are explicitly
underfilled; empty/oversized responses are invalid. Named positions remain one
exact-text candidate. These rules do not guarantee semantic diversity, originality,
a full pool, or useful live theses.

The no-support/single-support checks on both polarities, solver-unresolved exclusion,
attribution/own-thesis requirements, stance restrictions and derived-route policy
remain in force. Engine code, contribution code, route policy, bank and target
schema are byte-identical to the base. Vocabulary mismatch now remains advisory
without the former forced retry; at the base it was already not a final exclusion.
A fresh atom can therefore reach native search without replacing it merely to
share vocabulary with T. This is not an inference license: native bank and CQ
checks still decide closure.

## Independent native end-to-end evidence

[Independent harness](rho3-evidence/native_e2e.py) imports production modules only,
not test helpers, and substitutes only the provider response port. It creates a
placeholder PDF, uses native extraction and verified literature import, then calls
`cli.main(run)` through construction, one freeze, target gates, native engine search,
route publication and export. There is no handcrafted frozen sidecar or route,
engine replacement, or patched gate. Network connections and generation outside
the scripted provider are forbidden.

Frozen content T contains **P and Q endorsed, S reported, and F attacked**. The
fresh target is **R**, absent from T. Each exact 20-item pool contains R and 19
trivial P candidates; R is retained and the other 19 are rejected. Eight exact
commitment/symbol frames are removed with retained originals. Bibliographic authors
are unavailable in this fixture's extracted artifact and remain unavailable;
attributed speakers and rewrite authors are retained, not inferred.

| Independent run | Native result |
|---|---|
| Two endorsed supports P/Q, both sign CQs answered | **CLOSED-derived**, support IDs `p:r1-1:p`, `p:r1-1:q` |
| Same supports, unanswered CQs | **OPEN** |
| Reported S substituted as a global premise | **OPEN** |

The positive root uses the actual `sign` bank entry. `cq1` and `cq2` are both
answered with the two endorsed frozen IDs. Provenance is verified and there is no
stance crossing. Z3 returns `SOLVER_COUNTEREXAMPLE` for `{P,Q} |= R`: classical
entailment is not required for the licensed defeasible closure. Thus **mechanical
nontrivial defeasible reachability is real**, including the content/stance lifecycle.
It does not prove the truth of CQ answers, semantic scheme fit, useful real-literature
synthesis, or originality; those model outputs are scripted in this offline proof.

Artifacts: [receipt.json](/home/dev/ara-work/rho3-integration/runs/rho3-native-e2e/receipt.json),
[native report](/home/dev/ara-work/rho3-integration/runs/rho3-native-e2e/report/report.html),
[console](rho3-evidence/native-e2e.txt), and
[field-preservation checks](rho3-evidence/native-e2e-validation.json).
The native offline report rendered all three run lineages successfully.

## Real-literature plan and expected coverage

The reviewed Sigma counting/census harness was rerun against the committed merged
source, with separate outputs and generation/network disabled. It used pilot 4's
real extracted literature and configuration, changing the correction limit to 2,
with the native Codex estimator and pre-plan calibration. Input log
`/home/dev/ara-scaffold/runs/codex-pilot-4/events.jsonl` retained SHA-256
`508f17d6a366a1dfec7f33171c4f0ff2a5c5682407b557f1e88f22ab23f353e5`.

| Merged planning result | Value |
|---|---|
| Papers / funded windows | 26 / 74 |
| Maximum estimated window input | 67,326 of 70,000 |
| Initial commitments / cap per window | 2 / 4 |
| Projected allocation | 148 commitments |
| Projected working / symbol tokens | 78,745 / 34,484 |
| Correction policy | 2 per window per call type; up to 296 targeted corrections |

Xi's longer target prompt raises the planning wrapper from Sigma's 8,334 to 8,889
estimated tokens and reduces available global commitment slots from 151 to 150;
all 74 windows remain funded, with the same 148-commitment initial allocation.
These are allocation/counting estimates, not accepted commitments or exact tokenizer bounds.

The recorded-response census reproduces **35 attribution-rejected responses across
34 windows**, with **zero exact frames eligible for automatic unframing** and zero
responses thereby clearing the definition gate. Historical correction events total
two across the two call types. Earlier windows no longer exhaust later windows'
allowance, but improved coverage depends on successful model corrections and all
remaining gates. The old result remains **64 commitments from 12/26 papers**;
this review did not regenerate that corpus or claim recovered coverage.

An additional offline count on the historical 64-commitment T estimates the old
full target prompt at 57,876 input tokens and the merged prompt at 72,220; both
fit the 200,000-token bound including the 16,384-token context output allowance.
Expanded T and correction payloads still require runtime admission; this is not
proof that every future target request will fit.

Evidence: [plan summary](rho3-evidence/real-plan-summary.json),
[full plan](rho3-evidence/real-plan.json), [definition census](rho3-evidence/definition-census.json),
[replan script](rho3-evidence/offline_plan.py), and
[target envelope](rho3-evidence/target-envelope.json).

## Verification and remaining limits

Executed on committed integration `7c7bdc839fa96c7eece54bd93d3961055162bf27`:

| Check | Result |
|---|---|
| `uv sync --locked --offline` | Passed using the committed lockfile |
| `uv run --offline pytest -q` | **1,179 passed, 4 skipped / 1,183 total**, 988.89 seconds |
| `uv run --offline python tests/integration/negative_controls.py` | **510/510 passed**, 2,482.03 seconds; every mutation exit 1, every restored test exit 0 |
| Source restoration | All **220 tracked file contents** match before/after hashes; integration worktree clean |
| Author checkouts | Sigma and Xi remain at their requested heads and branches, both clean |
| Original pilot log | SHA-256 still matches after all checks |
| `git diff b48d56f HEAD --check` | Passed |

The full suite finished before the control runner began. All independent planning
and native proof runs finished before source mutation began. The four default
skips are the opt-in live-provider/installed-OCR checks; no live evidence is inferred.
No failing hook or gate was bypassed, and no source fix was needed after the merge.

Receipts: [pytest output](rho3-evidence/pytest.txt),
[control console](rho3-evidence/negctl.txt), [all control results](rho3-evidence/controls-results.json),
[per-control red/green logs](/home/dev/ara-work/rho3-integration/runs/delta-controls),
[source hashes before](rho3-evidence/source-before.json),
[source hashes after](rho3-evidence/source-after.json), and
[final verification](rho3-evidence/final-verification.json).

No paid provider call, live pilot, route selection or essay composition was performed.
The full suite and production-wire controls are regression evidence; the independent
native runs establish mechanical integration. None establishes real source truth,
faithful live formalization or improved pilot-5 paper coverage. No blocker was found
that requires editing either author branch before integration.

## Finding placement

| Action-changing observation | Deliverable section |
|---|---|
| Exact reviewed/merged scope and additive conflict resolution | Reviewed and merged revisions |
| Per-window corrections, old-config migration, resume identity, unframing/provenance and lexical limits | Sigma: corrections, feedback and content provenance |
| Novel-thesis contract, retained pool, concrete reasons, unchanged gates and advisory vocabulary | Xi: novel theses, rejection reasons and retained pool |
| Native defeasible closure, CQ/stance negatives and semantic limits | Independent native end-to-end evidence |
| Real plan remains funded, but none of the historical rejects is automatically repaired; live coverage and future context remain unproved | Real-literature plan and expected coverage |
| Exact executed suite/control receipts, restored source, skips and preserved author trees | Verification and remaining limits |
| No paid/live run, selection, writing or main-branch publication | Reviewed and merged revisions; Verification and remaining limits |

7 findings, 7 placed.

DONE rho3 sigma=merge xi=merge blocking=0 merge_sha=7c7bdc839fa96c7eece54bd93d3961055162bf27 merged_tests=1179/1183 negctl=pass e2e_defeasible=yes
