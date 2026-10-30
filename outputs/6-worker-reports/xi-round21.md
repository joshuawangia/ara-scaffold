# Xi Round 21 — advisory attribution and new-atom scheme reachability

Base `cb9d2c0ff2b40e511258a97eb99eb94926aa37f7`, branch `feat/run-report`,
checkout `/home/dev/ara-work/xi`. Offline only, no paid calls, push or delegation.
Evidence: `runs/xi-round21/`.

## Attribution policy

Broad lexical matches in target text, proposed definitions and used catalogue
names/definitions are logged as `target_lexical_attribution` and included in the
isolated classifier's cache-keyed input. Its own-thesis judgment is authoritative,
except exact leading proper-name + argues/holds/believes that report frames.
Route display retains only that narrow lexical veto. Construction's shared
lexicon is unchanged. Phi2's named report phrases receive strong-evidence prompt
guidance and are rejected through fake attributed_report judgments in regression
coverage. Own-voice uses of claims about and account reach native closure and
selection with a positive classifier. No paid classifier accuracy is claimed.

## Native scheme guidance and correction

Map_leaf and propose_cuts receive essential-new-proposition evidence, frozen
catalogue metadata and actual non-logical scheme signatures with CQs. Mapping
still returns only a T id or open; cut proposals supply the schemes. The engine
licenses up to three candidates per batch and requests one correction only when
none is licensed, with actual rejected instances and engine codes. Empty batches
receive NO_PROPOSALS; accounted validation failures supply their concrete reason.
The two-batch budget is independent of validation_attempts. Operational failures
still propagate. A licensed alternative needs no further batch, and ordinary
premise/CQ, cycle, depth and node checks remain authoritative.

## Real-leaf replay and limits

The exact pilot-2 target9 open leaf n1 from route b7259361c81f:r0 was replayed as a
fresh search root using all 169 commitments and 151 verified catalogue symbols.
Three deliberately invalid bank IDs produced UNKNOWN_BANK_ID feedback; one
corrected sign instance concluded its exact atom, with two endorsed supports
from two papers and fake supported CQ answers. Native result: CLOSED-derived;
its negation stayed OPEN. All nine source artifact hashes match. Sockets were
blocked. Receipt: `real-leaf-receipt.json`; native report:
`real-leaf-verified-report/report.html`; run: `real-leaf-verified/`; harness: `replay_leaf.py`.

This is an exact-leaf rehearsal, not a resumed/repaired historical graph. The
historical leaf repeats its ancestor formula and remains cycle-pruned there.
Suitable model output must propose the fitting new-atom scheme before that
cycle. The supplied fake sign and CQ output proves mechanical admission, not
semantic scheme fitness, truthful support, useful synthesis or originality.
The existing model-accuracy dependency for arbitrary aliases remains. Live use
needs current effective configuration/preflight; no live run was attempted.

The first replay reached closure but its report destination was incorrectly
inside its input run, and the report guard refused. That harness-only error is
retained in `replay-leaf.txt`. The corrected fresh run uses a sibling report
folder; `replay-leaf-final.txt` records success. Source artifacts were untouched.

## Arbitrary-atom scheme inventory

The current bank has 23 non-logical entries. Every one is kind=defeasible,
with a free conclusion slot and no deductive formula schema. The native licenser
therefore permits an arbitrary atomic goal when the exact conclusion reference,
required slots and scope constraints are satisfied. This is a syntactic ability;
T must actually supply semantically appropriate premises, all CQs need supported
answers, and stance/novelty/contribution gates still apply. It does not mean each
scheme fits this corpus or this leaf. Deductive entries may sometimes conclude
an atom but cannot license a genuinely new one from classical T alone, nor supply
the non-logical qualifying step for CLOSED-derived.

| Bank ID | Required premise slots | Critical questions (bank templates) |
|---|---|---|
| `expert_opinion` | `expertise`, `assertion`, `domain_match` | cq1: Is {expertise} credible in the domain specified by {domain_match}?<br>cq2: Does {domain_match} cover {assertion}?<br>cq3: Does {assertion} support {conclusion}?<br>cq4: Is the source of {assertion} trustworthy?<br>cq5: Is {assertion} consistent with other expert assessments of {domain_match}?<br>cq6: Is {assertion} based on evidence within {domain_match}? |
| `position_to_know` | `access`, `assertion`, `reliability` | cq1: Is the source of {assertion} in the position specified by {access}?<br>cq2: Is the source of {assertion} trustworthy according to {reliability}?<br>cq3: Was {assertion} actually asserted? |
| `witness_testimony` | `observation`, `testimony`, `reliability` | cq1: Is {testimony} internally consistent?<br>cq2: Is {testimony} consistent with {observation}?<br>cq3: Is the source of {testimony} reliable according to {reliability}?<br>cq4: Is {testimony} consistent with other evidence concerning {observation}? |
| `popular_opinion` | `acceptance`, `population`, `relevance` | cq1: Is {acceptance} established for {population}?<br>cq2: Does {relevance} support {conclusion}? |
| `analogy` | `source_case`, `similarity`, `transfer` | cq1: Are there relevant differences that undermine {similarity}?<br>cq2: Is {source_case} established?<br>cq3: Does {similarity} justify {transfer}?<br>cq4: Is there a counteranalogy to {transfer}? |
| `cause_to_effect` | `causal_rule`, `cause`, `conditions` | cq1: Are {conditions} satisfied?<br>cq2: Does {causal_rule} connect {cause} to {conclusion}?<br>cq3: Do intervening factors defeat {causal_rule} under {conditions}? |
| `correlation_to_cause` | `correlation`, `direction`, `alternatives` | cq1: Is {correlation} established?<br>cq2: Is {direction} justified?<br>cq3: Have common-cause and reverse-direction possibilities in {alternatives} been addressed? |
| `sign` | `sign_relation`, `observed_sign` | cq1: Is {observed_sign} reliable?<br>cq2: Does {sign_relation} support {conclusion}? |
| `established_rule` | `rule`, `applicability`, `exceptions` | cq1: Does {applicability} satisfy {rule}?<br>cq2: Do {exceptions} defeat {conclusion}? |
| `verbal_classification` | `criteria`, `properties` | cq1: Are {criteria} appropriate?<br>cq2: Do {properties} satisfy {criteria}? |
| `practical_reasoning` | `goal`, `means`, `alternatives` | cq1: Is {goal} achievable?<br>cq2: Are {means} necessary or sufficient for {goal}?<br>cq3: Are {alternatives} preferable to {means}?<br>cq4: Do adverse consequences of {means} defeat {conclusion}? |
| `positive_consequences` | `action`, `consequences`, `valuation` | cq1: Does {action} produce {consequences}?<br>cq2: Does {valuation} support {conclusion}? |
| `negative_consequences` | `action`, `consequences`, `valuation` | cq1: Does {action} produce {consequences}?<br>cq2: Does {valuation} support {conclusion}? |
| `commitment` | `commitment`, `implication` | cq1: Is {commitment} established?<br>cq2: Does {implication} connect {commitment} to {conclusion}? |
| `inconsistent_commitment` | `first_commitment`, `second_commitment`, `incompatibility` | cq1: Are {first_commitment} and {second_commitment} established?<br>cq2: Does {incompatibility} support {conclusion}? |
| `precedent` | `prior_case`, `similarity`, `applicable_rule` | cq1: Does {similarity} justify applying {applicable_rule}?<br>cq2: Is {prior_case} relevant to {conclusion}? |
| `best_explanation` | `observations`, `explanation`, `alternatives` | cq1: Does {explanation} account for {observations}?<br>cq2: Does {explanation} account for {observations} better than {alternatives}?<br>cq3: Have plausible {alternatives} been adequately examined? |
| `example` | `instance`, `representativeness`, `generalisation` | cq1: Does {instance} support {generalisation}?<br>cq2: Is {representativeness} adequate for {conclusion}? |
| `slippery_slope` | `initial_step`, `transition_chain`, `endpoint` | cq1: Does {initial_step} initiate {transition_chain}?<br>cq2: Is each transition in {transition_chain} supported?<br>cq3: Can {transition_chain} be stopped before {endpoint}?<br>cq4: Does {endpoint} support {conclusion}? |
| `ad_hominem_direct` | `credibility_attribute`, `relevance`, `assertion` | cq1: Is {credibility_attribute} established?<br>cq2: Does {relevance} connect {credibility_attribute} to {assertion}? |
| `ad_hominem_circumstantial` | `circumstances`, `commitment`, `inconsistency` | cq1: Are {circumstances} established?<br>cq2: Does {inconsistency} concern {commitment}?<br>cq3: Does {inconsistency} support {conclusion}? |
| `ad_hominem_tu_quoque` | `conduct`, `assertion`, `inconsistency` | cq1: Are {conduct} and {assertion} established?<br>cq2: Does {inconsistency} support {conclusion}? |
| `bias` | `bias_evidence`, `assertion`, `relevance` | cq1: Is {bias_evidence} established?<br>cq2: Does {relevance} connect {bias_evidence} to {assertion}? |

## Verification

Before implementation, all six new guidance/advisory regressions failed
(`red.txt`). Initial focused tests passed 39/39. The broader owning run passed
143 tests and exposed one legacy formula=None call; guidance now records
unformalised_goal instead of dereferencing it. The repaired focused run passed
55/55 (`focused-final.txt`). Canned/native fixtures were regenerated offline
using `runs/xi-round19/rekey.py`. Final counts follow after sequential gates.

## Finding placement

5 findings, 5 placed: lexical policy change in Attribution policy; native bounded
correction in Native scheme guidance; exact-leaf/cycle limitation, semantic/model
accuracy limits, and live prerequisites in Real-leaf replay and limits. The scheme
inventory is the requested structural capability report, not a suitability claim.

Final focused verification: **41 passed**, including native CLI canned replay
(`last-focused.txt`). **15/15** focused mutation/restoration controls passed,
with all five touched source hashes restored (`focused-controls.txt`,
`focused-control-results.json`). The final real-leaf rehearsal was repeated
after behavior-preserving simplification in a fresh directory.

Recovery/parallel verification passed 41 tests and identified two stale call-count
assertions (sequential/concurrent variants). The expected successful empty-leaf
calls now include their one correction batch; provider failure retries, recovery
ordering and partial-result assertions are unchanged. Evidence: `recovery-check.txt`.

The repaired recovery variants passed **2/2**, and all **5/5** owning
mutation/restoration controls passed with source hashes restored
(`recovery-fixed.txt`, `recovery-controls.txt`). Full sequential verification
now pins the final 227-file source snapshot.

The first full pytest passed **1,255 tests, four skipped / 1,259 collected**.
The sequential control run stopped at control 452: target_instance_guard had
accidentally been retargeted to the leading-attribution test, which cannot detect
the single-commitment-entailment mutation. All 227 pinned source hashes were
restored. The selector now points back to its existing quantified-instance test;
that control is red under mutation and green after restoration. The remaining
controls are being checked before repeating the final sequential gates. Original
receipts are preserved under `first-gates/`; no product behavior changed in this
repair.

The repaired selector and all subsequent controls passed **91/91**, including
all seven new Round 21 controls (`remaining-controls.txt`). Final full pytest
then passed **1,255 / 1,259 collected, four skipped**, in 1,002.63 seconds.
All 227 pinned source hashes matched after pytest. The full 542-control runner
is executing sequentially after it (`gates.txt`, `pytest-full.txt`).

## Final sequential gates

**1,255 passed, four skipped / 1,259 collected**; **542/542 controls passed**
(all mutations red, all restorations green). The full control runner completed
after the final full pytest, on the corrected tree. All **227 pinned files**
match their pre-test hashes, including all **51 mutated production files**.
`git diff --check` passed. Receipts: `final-verification.json`,
`source-before.json`, `source-after-controls.json`, `full-control-results.json`,
`pytest-full.txt`, `controls-full.txt`, and the individual red/green logs in
`controls/`. Zero paid calls; no push.

Committed locally as **`a272ebe7df8615a7a9a4a0215068f963171a5c3d`** on `feat/run-report`.
The working tree is clean, and all 227 committed file contents match the exact
hashes pinned before the final sequential gates (the AGENTS.md symlink resolves
to the committed CLAUDE.md). Receipt: `commit-verification.json`.

**5 findings, 5 placed**, with placement recorded above. Semantic fitness, live
classifier accuracy, historical-graph repair, and live-run readiness remain
outside this offline verification; see Real-leaf replay and limits.
