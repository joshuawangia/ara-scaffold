# Forward gap sweep — stopped and diagnosed

No qualifying forward candidates, accepted targets, searched routes, or queue additions. The completed 20,000-consequence sweep found only Boolean packaging and two single-paper unpackings. This is a finding about the frozen formalization and bounded execution, not evidence that the literature has no substantive gaps.

Executed at clean pinned revision `f76c1b31a360ec74fc57f4c9d22c2b849eb4dcd8` in `/home/dev/ara-work/run-f76c1b3`. Brief: `/home/dev/ara-work/briefs/fwd-sweep.md`. Machine-readable report: [fwd-sweep.json](fwd-sweep.json). Detailed audit: [fwd-sweep-diagnosis.json](fwd-sweep-diagnosis.json).

## Frozen structure

Independently read the actual `runs/codex-gap-1r/frozen-t.json`, validated its catalogue and provenance, and authenticated its history through native `fork_from_freeze`. Original and copied frozen artifacts remain byte-identical to the initial hashes.

- **141/160 commitments are bare atoms**, all 141 named with their own source-paper prefix. The rest are 18 implications and one conjunction.
- **147 catalogue symbols**, all used. **Zero** symbols occur in commitments belonging to two distinct source papers.
- **Two** symbols recur when the model-alignment bridge is treated as an additional owner. These are source-to-bridge reuses, not symbols shared by two source papers. This corrects the literal “two shared across papers” description.
- Stances: 134 endorsed, 15 attacked, 10 reported, one model alignment. The 135 eligible forward premises contain 117 atoms, 17 implications and one conjunction. There are 22 source papers, 21 with endorsed premises.

The source-paper formalizations are disconnected by symbol identity; ordinary formal matching cannot infer that differently named source assertions express a shared concept.

## The sole bridge

The bridge is `schaffer2011_r2_25_n6_truth_perspectivalism -> macfarlane2014_assessment_sensitivity_framework`.

| Endpoint | Paper / physical PDF page | Stance and consequence |
| --- | --- | --- |
| Antecedent | Schaffer 2011, page 3 | `attacked`; unavailable as a global forward premise |
| Consequent | MacFarlane 2014, page 66 | `endorsed`; already a bare frozen premise from that paper |

The antecedent concerns perspective-neutral propositions whose truth varies with perspective; the consequent concerns an assessment-sensitivity framework. Their relation is a disclosed model judgment, not a source endorsement. This bridge supplies neither an admissible asserted antecedent nor a consequent outside the receiving paper’s existing closure. Exact IDs, formula and provenance are in the diagnostic JSON.

## Completed pass and bounds

| Pass | Configured depth | Consequence cap | Native instantiation-work cap | Completed outcome |
| --- | ---: | ---: | ---: | --- |
| Baseline | 2 | 500 | 180,000 | 500 consequences, 0 candidates, truncated |
| Widened | 6 | 20,000 | 7,200,000 | 20,000 consequences, 0 candidates, truncated; 493.733 seconds |
| Further continuation | 6 | 50,000 | 18,000,000 | Operator-terminated; no completed result |

The completed widening was 3× configured depth and 40× consequence/work caps. The continuation configured 100× baseline caps, but does not establish completed coverage. All 36 bank entries remained loaded. Native rule order exhausted the completed 20,000 pass within the first layer, before later rules; six configured layers were not executed. Rule decisions retain native bank licensing and deduction solver checks.

## Cross-paper symbol and premise counts

| Native rule | Retained consequences | Contain symbols owned by ≥2 source papers | Use endorsed premises from ≥2 papers |
| --- | ---: | ---: | ---: |
| Conjunction introduction | 9,180 | 8,155 | 8,020 |
| Conjunction elimination | 2 | 0 | 0 |
| Disjunction introduction | 10,818 | 9,575 | 0 |
| **Total** | **20,000** | **17,730** | **8,020** |

Thus cross-paper symbols were combined extensively: **88.65%** of retained consequences contain them. That is packaging, not substantive synthesis. Conjunction introduction bundles assertions; disjunction introduction can add another paper’s symbol without using that paper as evidence. The two eliminations unpack one paper’s conjunction. Another 135 conjunctions use the alignment bridge, whose symbols have two paper origins but which has no paper ownership. There are no retained modus-ponens, modus-tollens, syllogism, quantifier, or defeasible-scheme consequences in this pass.

The 40,002 native engine events record 20,000 retained consequences, one further disjunction license before insertion refused at the cap, and `FORWARD_CAP`. **The original engine events retain rule decisions, not each rejected formula.** To answer the symbol-count question without restarting the sweep, the audit reconstructed only these already recorded first-layer formulas from frozen ordering, native schema instantiation and known-formula deduplication, matching the entire 20,000-rule receipt sequence exactly. No solver, forward pass, candidate generation, model or route search was run during this audit. The 17,730/8,020 counts are explicitly reconstructed provenance counts; rule totals and zero surviving leads are direct native receipts.

## Stop and retained evidence

The 20,000 pass had already completed when the stop arrived. The active 50,000 continuation was terminated with SIGTERM, exit 143. All persisted receipts remain. Its 40,010 post-freeze events were checked against their chain and anchor; they include 40,000 engine events and an isolation canary, **no model target proposal and no search**. Any unflushed in-memory engine events are unavailable, so this continuation has no final candidate verdict.

- `fwd-sweep-baseline/`: completed baseline and source hashes.
- `fwd-sweep-wide/`: completed 20,000-pass summary and full engine receipts.
- `fwd-sweep-authenticated/`: authenticated frozen prefix and interrupted continuation receipts.
- `fwd-sweep-preflight/`: fresh Codex schema preflight, 20/20 passed.
- `fwd-sweep-stop.json`: termination and persisted-event audit.

The existing shared queue was left unchanged: **0 additions** by this task. No route was selected. No candidate list requires eps2 literature review. Disk remained about 19 GB free, above the required 10 GB floor. No repository source files were edited.

## Interpretation and checks

**Supported diagnosis:** this predominantly atomic, paper-isolated formalization supplies no demonstrated substantive cross-paper forward synthesis; the bounded pass spent its capacity on conjunction/disjunction packaging and single-paper unpacking. The only bridge has a restricted antecedent and an already-known consequent. Raising these bounds did not repair that representational limitation.

**Limit of the diagnosis:** “all cross-paper bank inference is impossible” is stronger than the evidence. The bank also has 23 defeasible schemes whose new conclusions need not share frozen symbol names; fresh forward synthesis does not instantiate them without previously closed route witnesses. The interrupted model-backed search never tested that possibility. Nor does a truncated first layer establish every possible deeper consequence. This report does not turn a bounded zero into a literature-absence or universal impossibility claim.

At the pinned revision, 61 focused tests passed in 210.16 seconds across per-paper synthesis, consistent novelty, novelty policy and engine conflicts (`fwd-sweep-checks.txt`). Fresh Codex schema preflight passed 20/20 with the authorized 600,000 context window. These checks establish gate/transport mechanics, not philosophical truth, faithful formalization or novelty. No full release verdict is claimed.

## Finding placement

1. Atomicity and source-symbol isolation → **Frozen structure**.
2. Bridge stance and already-known consequent → **The sole bridge**.
3. Zero leads, rule-order truncation and actual widening → **Completed pass and bounds**.
4. 17,730 cross-symbol packages versus 8,020 two-paper premise combinations → **Cross-paper symbol and premise counts**.
5. Termination, retained/incomplete evidence and unchanged queue → **Stop and retained evidence**.
6. Bounded diagnosis, defeasible-search limitation and proof scope → **Interpretation and checks**.

**6 findings, 6 placed.**

DONE fwd sweep head=f76c1b3 candidates=0 gated=0 routes=0 closed=0 queued=0 (diagnosis: paper-isolated atomic formalization yielded only packaging and single-paper unpacking; the sole bridge has an attacked antecedent and an already-known consequent).
