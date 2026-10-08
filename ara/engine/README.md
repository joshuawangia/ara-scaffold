# Engine integration

Use the existing bank loader and frozen shared contracts. No changes to
`ara/types.py` or `ara/ports.py` are required.

```python
from ara.engine import Engine, EngineConfig

engine = Engine(
    bank=bank, commitments=commitments,
    proposer=cut_proposer, formaliser=formaliser,
    leaf_mapper=leaf_mapper, cq_answerer=cq_answerer,
    repairer=tier1_repairer, sink=event_sink,
    config=EngineConfig.from_mapping(config),
)
analysis = engine.analyse(target)
# analysis.target.routes and analysis.negated.routes contain RouteGraph values.
# Each RouteGraph retains the scaffold's to_json()/from_json() contract.
serialized = analysis.to_json()
```

`Engine.search(target)` performs one bounded search. `Engine.analyse(target)`
performs that search and the identical search of its canonical negation, runs
forward passes for closed routes, and requests Tier 1 repairs. Use `analyse`
for the complete runtime workflow. The result is immutable and round-trips with
`AnalysisResult.from_json`. The two SearchResults include their targets, routes,
independent closed-route counts, nodes_created, and truncated flags. `forward`
contains route-associated consequences (formula, bank id, premises, depth and
flagged), plus truncation flags. Tier 2 records opposing route ids and the first
flagged consequence, or null when neither bounded forward pass finds one.

EngineConfig consumes depth_cap, node_cap, seed, forward_pass_depth, and
solver_timeout_ms. The last key is optional with a 1000 ms default; the scaffold's
config file has no timeout key. Runtime can provide it without modifying the
shared types. Invalid nonpositive timeout/node caps and negative depths fail.

Every proposal is licensed by bank identity, exact filled slots, canonical goal,
scope and (for deductions) solver entailment plus schema matching. Ports may
raise their logged rejection/budget errors; engine calls propagate them. Forward
instantiations use engine-owned ASTs, with no Formaliser or provider calls.
Decision events carry real timestamps; timestamps are absent from graphs and
analysis JSON, preserving byte-identical replay with identical port outputs.

A CLOSED route has every external leaf in frozen T with both a matching id and
canonical formula, all scoped assumptions properly introduced/discharged by the
constructed proof tree, and every CQ answered with nonempty text and existing T
support ids. CQ nodes with missing support remain in the OPEN frontier alongside
unclosed leaves. CQ truth or faithful text formalisation is not mechanically
established by these structural/evidence checks.

Cost is the inference count plus one per unresolved external leaf, zero for T
leaves or local assumptions, and infinite (JSON null) when T contains an external
leaf's canonical negation. Best-first uses that lower-bound cost and seeded
random tie breaks. Each search's global node allocation and path depth are
bounded; cycles are pruned. A T terminus is not expanded further. Counts refer to
discovered closed routes, not all possible proofs. Independence is the exact
maximum number with pairwise disjoint canonical external premise sets, including
CQ support; repeated T ids/formula aliases cannot inflate it.

Forward deduction uses observed subformulas for unbound formula variables and
observed constants for quantifier instances (the bank substitution constant for
vacuous/no-observed-constant cases). Defeasible forms have no formula schema from
which to invent a conclusion; forward replay uses their licensed, CQ-supported
instances in the discovered closed graphs. Scoped exports use the verified
subproof's external dependencies and height. Internal assumptions never become
forward premises. Each layer reads the previous layer's snapshot. The node cap
also caps new forward consequences; an instantiation-work cap of
node_cap × bank-entry-count × 10 prevents combinatorial enumeration from hanging.
Both caps produce FORWARD_CAP and truncated=true, never a completeness claim.

Tier 1 compares canonical premise sets of discovered licensed steps, including
forward deductions, and the full external support of closed routes (including
CQ evidence and scoped exports). Contradictory conclusions mark the set and call the repair
port once per canonical pair. Scope-local assumptions are excluded from global
conflict grouping. Repair proposals are returned for review; they do not mutate
frozen T or become licensed automatically. Tier 2 pairs CLOSED target/negation
routes and records the first flag in positive-forward then negative-forward
order. No flagged consequence is represented explicitly by null.
