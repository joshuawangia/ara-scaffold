# Zeta fork pilot 5 — awaiting selection, provisional

Native completion succeeded: **6 targets, 12/12 searches, 12 OPEN routes**. No route was selected. The acceptable-pilot verdict is **FAIL** because there are **0 CLOSED-derived routes**, against at least 3 required.

[Native full-lineage report](/home/dev/ara-work/reports/overnight/fork5/report.html) · [Annotated model-written summaries](/home/dev/ara-work/reports/overnight/fork5/route-summaries.html) · [Full audit](/home/dev/ara-work/reports/overnight/fork5/fork-audit.json).


## Acceptable pilot criteria

| Criterion | PASS/FAIL | Numbers |
|---|---|---|
| 1. Clean run | PASS | awaiting_selection=True; searches 12/12; MODEL receipts 96; unsettled 0; unknown usage 0; Claude/non-Codex 0; new API USD 0 |
| 2. Coverage | PASS | 22/26 papers; page-cited 169/169; stance-labelled 169/169 (150 endorsed, 13 attacked, 6 reported) |
| 3. Real routes | FAIL | CLOSED-derived 0 (required>=3); qualifying cross-paper closed proofs 0; substantive CLOSED-derived reviews 0 applicable |
| 4. Readable output | PASS | Model-written summaries 12/12; HTML opens; page errors 0; missing anchors 0; 1.383398 MB; semantic summary qualifications below |

Criterion 4 evaluates summary coverage and rendering. It does not erase the semantic inaccuracies and qualifications recorded below. There are no CLOSED-derived graphs to review item by item for criterion 3. All 12 OPEN graphs were reviewed for the proposed scheme, support roles, polarity and unresolved obligations. The successful-entry essay, audits and submission were not attempted.

## Execution and review status

**Provisional:** xi r23 `2ed9e21796bf55e1160bd6a22e1f0f459bb67436`; kappa4 review confirmation has not been supplied by the operator. Earlier r21 approval does not approve r23. Clean detached checkout `/home/dev/ara-work/run-2ed9e21`; no repository source edits or additional worker contexts.

Fresh live Codex schema preflight 16/16, standalone canary, then native fork with its own isolation canary. The reporting summary helper also ran its native canary. Same effective pilot 5 configuration apart from the fork cache and fresh schema-proof path: requested `gpt-6-luna`, Codex CLI, effort high, search concurrency 4, context bound 200,000, 100M local-token cap, empty audience and no fallbacks. No Claude or API calls, route selection, new construction or second freeze.

Pilot 5 source run `/home/dev/ara-scaffold/runs/codex-pilot-5` remains byte-for-byte preserved across its 167 files. The fork prefix and frozen artifacts match it. Frozen T has 169 commitments from 22 papers; every commitment carries a physical-page citation and stance label. The preserved previous handoff is `/home/dev/ara-work/reports/zeta-fork4.md`.

## Target gates

Proposal batches contained 5, 1, 1 candidates against a requested pool 30; 6 were kept against the keep limit 10. Every candidate passed 340 target/negation tautology and single-support solver checks (all returned counterexamples), whole-T closure admission and essential-new-atom checks with 1 essential fresh atom. All used new, disconnected vocabulary (advisory). Formal candidate admission is not proof of faithful formalization or philosophical originality. The own-thesis/content classifier made the final semantic distinction.

| Target | Own thesis | Fidelity | Semantic novelty | Formal novelty | Final |
|---|---|---|---|---|---|
| target_1 | own_thesis | matches | new_assertion | essential_new_assertion | KEPT |
| target_2 | own_thesis | matches | new_assertion | essential_new_assertion | KEPT |
| target_3 | own_thesis | matches | new_assertion | essential_new_assertion | KEPT |
| target_4 | own_thesis | matches | new_assertion | essential_new_assertion | KEPT |
| target_5 | own_thesis | matches | new_assertion | essential_new_assertion | KEPT |
| target_6 | own_thesis | matches | restatement | essential_new_assertion | REJECTED |
| target_7 | own_thesis | matches | new_assertion | essential_new_assertion | KEPT |

**target_1** — An adequate semantics of epistemic modals must preserve information-sensitive Safety for probabilistic knowledge while also satisfying the stated assertibility constraints for modal connectives.

Classifier: The target asserts a combined adequacy requirement in its own voice. Frozen content discusses the safety and assertibility constraints separately, but not their joint requirement; the rendered definition matches the target text.

**target_2** — Assessment-sensitive accounts of epistemic modals should preserve worldly-information safety across nearby worlds.

Classifier: The target directly asserts a normative claim in its own voice. Its text matches the bound atomic definition, and the claim that assessment-sensitive accounts should preserve worldly-information safety is not merely a restatement of a frozen commitment.

**target_3** — A semantic model of epistemic modals should represent world-specific worldly information separately from information about the topic situation.

Classifier: The target directly proposes a semantic-model requirement. Its text matches the rendered atom; the explicit separation of world-specific worldly information from topic-situation information adds content beyond the frozen commitments.

**target_4** — A probabilistic semantics for epistemic modals should evaluate high-credence claims against the worldly information relevant at nearby worlds, not solely against probability measures.

Classifier: The target directly recommends how a probabilistic semantics should evaluate claims; “claims” does not report anyone’s position. Its text matches the rendered atom and binding. Although frozen content discusses nearby-world credence and worldly information, it does not state this recommendation’s contrast with evaluation solely against probability measures.

**target_5** — Adequate assertability conditions for probabilistic epistemic claims should track both the question under consideration and worldly information at nearby worlds.

Classifier: The target asserts in its own voice that assertability conditions should track both question and nearby-world information, combining constraints not stated together in frozen_content. The supplied atom is bound to that exact proposition; “claims” refers to the subject matter, not a source report.

**target_6** — Epistemic modal inference should distinguish failure of consequence from impossibility of joint truth: some classically invalid inferences fail because their premises cannot be jointly accepted by one information state.

Classifier: The target asserts its own methodological claim, and its text matches the bound atom. It restates the frozen claim that incoherence can arise from failure of joint acceptability relative to one information state, not impossibility of joint truth.

**target_7** — A compositional account of epistemic-modal discourse should represent question-sensitive assertability independently from the information-parameter shifts caused by non-truth-tabular connectives.

Classifier: The target states a recommendation in its own voice. Its text matches the rendered definition, and it adds the claim that question-sensitive assertability should be represented independently of connective-driven information shifts.

Five lexical hits (`accounts`, `claims` twice, `state`, `account`) were advisory; 0 lexical-only exclusions. Target 6 was rejected for semantic restatement despite its fresh atom and own-thesis form. No exact leading report frame was rejected.

## Guidance and context bounds

All 3 exact native proposal prompts matched the prepared catalogue bridge context and paper map. The 60 bridges (30 pairs,30 triples) cover 21 commitments / 7 papers; all 60 include Beddor–Goldstein 2021 and the generic term `about`; 0 use shared catalogue symbols. This concentration limits the diversity of the supplied leads. It is not evidence that the concentration caused a particular result.

R23 produced 36 counted leaf-context slices: 12 `map_leaf` and 24 `propose_cuts`. All fit at the first 8-bridge level; 0 further shrinks or refusals. Maximum counted input 31,934 plus 16,384 output allowance = **48,318**, below the unchanged 200,000 context bound. Across those slices, the guidance included 9 commitments from 5 papers. Full T and its provenance remained validation authority; a slice is not the entire frozen evidence set. These counts use the configured calibrated admission estimator, not a free exact Codex tokenizer. They are scoped to leaf/cut guidance, not every model stage.

There were 24 cut calls (one initial batch and one correction per search), 5 proposal_bridge receipts and 5 bank-licensed candidate steps. The proposals identify cross-paper slots, but the required critical questions remain open. R23’s context handling was exercised successfully; its order-independent CLOSED-derived matching rule was not exercised on a closed graph in this pilot.

## Routes and substantive review

| Category | Count |
|---|---|
| CLOSED-derived | 0 |
| CLOSED-structural | 0 |
| CLOSED-single-paper | 0 |
| OPEN | 12 |
| Other classifications | 0 |

All 12 terminal traces are sealed, authenticated, complete and match the published native graph hashes. They contain 24 proof nodes in total, maximum depth 1, and 0 truncated searches. Seven routes have one unresolved root and no licensed proposal. Five have a root scheme with frozen premise leaves; all 12 retain frontier `n0`. The five schemes are 3 sign and 2 best_explanation; these are candidate steps with unresolved CQs, not closed proofs.

| Target/polarity | Route | Scheme | Distinct commitments / papers | Open obligations |
|---|---|---|---|---|
| target_1 | 871f4c4b293a:r0 | sign | 2 / 2 | cq1, cq2 |
| not:target_1 | 9f1f7264a75b:r0 | none | 0 / 0 | unsupported root |
| target_2 | 3f141dbb2b92:r0 | none | 0 / 0 | unsupported root |
| not:target_2 | 71e709181088:r0 | none | 0 / 0 | unsupported root |
| target_3 | 1cc540b50577:r0 | none | 0 / 0 | unsupported root |
| not:target_3 | 675c22724e64:r0 | none | 0 / 0 | unsupported root |
| target_4 | d471addaa75c:r0 | best_explanation | 3 / 3 | cq1, cq2 |
| not:target_4 | 40fdf6e31af6:r0 | none | 0 / 0 | unsupported root |
| target_5 | 9805e3aa0cfa:r0 | sign | 2 / 2 | cq1, cq2 |
| not:target_5 | 9d3c169681bc:r0 | best_explanation | 3 / 3 | cq1, cq2 |
| target_7 | 476424c8082d:r0 | sign | 2 / 2 | cq1, cq2 |
| not:target_7 | 935637cda889:r0 | none | 0 / 0 | unsupported root |

**target_1 / 871f4c4b293a:r0** — The sign premises concern avoiding two difficulties for modal knowledge and satisfying a different set of assertibility constraints. Both CQs correctly leave the unproved compatibility/link to a single jointly adequate semantics open. Beddor–Goldstein has one omitted support ID.

**target_4 / d471addaa75c:r0** — The abduction premise labelled explanation is the Hawke–Steinert-Threlkeld semantic expressivism, not a demonstrated explanation of Beddor–Goldstein’s relevant-alternatives difficulties. cq1/cq2 remain false. cq3 is recorded true even though its prose says only partly and denies a comprehensive alternatives examination; treat that support as qualified, not adequate comparison proof.

**target_5 / 9805e3aa0cfa:r0** — Moss supports question-sensitive assertability, and Beddor–Goldstein discusses the defended theory avoiding two difficulties. Neither supplies a connection from those claims to nearby-world worldly-information requirements for assertability. Both CQs remain false.

**not:target_5 / 9d3c169681bc:r0** — The abduction does not show that modal-knowledge theory explains question-sensitive assertability, beats the alternative, or establishes the negation of the joint requirement. cq1/cq2 remain false. cq3 is recorded true although the answer says only partially and denies systematic alternatives review.

**target_7 / 476424c8082d:r0** — The sign premises from Beddor–Goldstein and Hawke–Steinert-Threlkeld do not establish independent representation of question-sensitive assertability and connective-driven parameter shifts. Both CQs remain false.

All 6 paired analyses completed, with 0 Tier 1 findings, 0 Tier 2 findings and 0 forward results. Those bounded results do not establish global consistency, truth or search exhaustion.

## Critical-question review

The native receipts contain 12 CQ answers: 10 unsupported and 2 supported. Both supported answers are `cq3` of best_explanation, on target 4 and not:target_5. The bank asks whether plausible alternatives were adequately examined. The responses are marked `answered=true`, but say **“Partly”** or **“Only partially”**, and explicitly deny comprehensive/systematic examination. They establish at most a qualified component; they do not independently establish that the alternatives were adequately evaluated. Each route still has cq1/cq2 false, so this discrepancy did not produce a CLOSED route.

The sign routes do not establish that the observed sign is reliable or that the supplied relation supports the new conclusion. The best-explanation routes do not show explanatory fit or superiority to alternatives. Native bank licensing should be read together with those open obligations.

## Source and summary review

Reviewed all12 authenticated terminal graphs and model summaries, the 4 referenced frozen commitments and stance/provenance records, the sign/best_explanation bank entries, and original PDF pages Beddor–Goldstein 41, Hawke–Steinert-Threlkeld 19, MacFarlane 195 (printed 181), Moss 17 (5:17). All 4 referenced commitments are endorsed by their source authors; that does not independently verify their truth. Pypdf emitted mathematical-font encoding warnings; this review concerns the readable prose passages, not exact mathematical notation or full-paper verification.

**beddorgoldstein2021 PDF41** — PDF41 confirms the two relevant-alternatives difficulties and the source’s claim that its theory avoids them. The frozen commitment explicitly omits supporting link_raTwoDifficulties. It does not connect this claim to HST assertibility or Moss question sensitivity.

**hawkesteinertthrelkeld2021 PDF19** — PDF19 announces the positive semantic-expressivist proposal and its partial truth-value interpretation function with conservative modal/connective interaction. It does not establish joint satisfaction of Beddor–Goldstein safety conditions.

**macfarlane2014 PDF195** — PDF195 (printed181) criticizes contextualist knowledge-attribution predictions about truth, disagreement and retraction. It is not a comparative evaluation of the proposed probabilistic semantics against all relevant alternatives.

**moss2015 PDF17** — PDF17 (5:17) motivates question-sensitive assertability for a probabilistic conditional. It supports that limited component, without adding nearby-world/worldly-information requirements.

The source passages support the component claims without establishing the proposed cross-paper relationships. Beddor–Goldstein’s frozen provenance lists omitted support `beddorgoldstein2021:r36-47-refine:link_raTwoDifficulties`; it is absent from these route proofs. This is an evidence-transfer gap, not a finding that the paper has no argument.

**Summary corrections:** not:target_3 strengthens denial of a requirement into an opposite prohibition. Its formula is NOT(the model should represent the information types separately), not a requirement that it should avoid doing so. The not:target_5 and target_7 summaries’ cross-paper-support language must also be qualified: their graphs contain verified premises from 3 and 2 papers, respectively; what they lack is a qualifying CLOSED-derived proof. Raw model summaries remain unchanged below and in the native log.

### 871f4c4b293a:r0 — target_1 / target

Target polarity: supports the claim that an adequate epistemic-modal semantics must combine information-sensitive Safety for probabilistic knowledge with the stated assertibility constraints. The recorded steps cite Beddor and Goldstein’s endorsed claim that their defended theory avoids two relevant-alternatives difficulties, and Hawke and Steinert-Threlkeld’s endorsed claim that their semantic expressivism meets the assertibility constraints. These are separate source claims; the steps do not establish that one semantics meets both requirements. The route is OPEN: its connection remains unproved and both recorded critical questions are unanswered. The first commitment’s source text omits support ID beddorgoldstein2021:r36-47-refine:link_raTwoDifficulties; this is an omitted-support assumption, not supplied evidence. Endorsement reports the authors’ stance, not independent verification.

Review note: The omitted-support ID describes evidence not carried into this frozen route. It does not mean the original paper lacks the argument. Both critical questions remain unsupported.
### 9f1f7264a75b:r0 — target_1 / negation

This OPEN route takes the negation of target_1: that an adequate epistemic-modal semantics must preserve information-sensitive Safety for probabilistic knowledge and satisfy the stated assertibility constraints. Its only recorded node is an unsupported negation leaf; there are no steps or frozen commitments supporting it. The route remains open, and no omitted-support assumptions are specified.

Review note: The description preserves the OPEN status and absence of supporting steps.
### 3f141dbb2b92:r0 — target_2 / target

This OPEN route targets the claim that assessment-sensitive accounts of epistemic modals should preserve worldly-information safety across nearby worlds (target polarity). Its graph contains only the target as an unsupported leaf, with no recorded steps or frozen commitments. Support is absent (zero papers against a two-paper minimum), so the route remains open; the target is not established.

Review note: The description preserves the OPEN status and absence of supporting steps.
### 71e709181088:r0 — target_2 / negation

The target is that assessment-sensitive accounts of epistemic modals preserve worldly-information safety across nearby worlds. This route has negation polarity: its sole recorded node is the negation of that target. There are no recorded supporting steps, CQ answers, or frozen commitments, so no commitment-based support is established. The route is OPEN; the target’s negation remains unresolved. No omitted-support assumption is supplied.

Review note: The description preserves the OPEN status and absence of supporting steps.
### 1cc540b50577:r0 — target_3 / target

This OPEN route has target polarity: a semantic model of epistemic modals should represent world-specific worldly information separately from information about the topic situation. Its only recorded step is the target itself, left open; no supporting steps or frozen commitments are supplied or used. No omitted-support assumptions are reported.

Review note: The description preserves the OPEN status and absence of supporting steps.
### 675c22724e64:r0 — target_3 / negation

This OPEN route targets the negation of target_3: that a semantic model of epistemic modals should not represent world-specific worldly information separately from information about the topic situation. Its graph contains only an unresolved leaf asserting that negation; there are no recorded supporting steps or frozen commitments. The route remains open, with no supplied support papers or commitment text, so it does not establish the negated target.

Review note: Negation-scope correction: the formal target is NOT(the model should represent the information types separately). It denies the requirement; it does not assert that models should NOT represent them separately. The model summary states that stronger prohibition. No support was established for either reading.
### d471addaa75c:r0 — target_4 / target

OPEN; target polarity. The best-explanation step proposes that epistemic-modals semantics assess high-credence claims using worldly information at nearby worlds, not probability measures alone. Its recorded commitments report difficulties for relevant-alternatives theory, describe a semantic-expressivist proposal, and criticize contextualist predictions; they do not establish the proposed probabilistic account or compare it with alternatives. The Beddor–Goldstein commitment is endorsed by its authors but lists an omitted support link (beddorgoldstein2021:r36-47-refine:link_raTwoDifficulties), so its support is not present here. The alternatives question is only partly answered; the expressivism-versus-relevant-alternatives and comparative-explanatory questions remain unanswered. The target remains open.

Review note: The route contains premises from three verified papers. CQ3 is marked answered=true, but its text says only partly and does not establish comprehensive alternatives review. Other CQs remain false. Omitted support refers to the frozen route evidence, not absence of an argument in the source paper.
### 40fdf6e31af6:r0 — target_4 / negation

This route has negation polarity toward target_4: it opposes the claim that probabilistic semantics for epistemic modals should assess high-credence claims using worldly information at nearby worlds, rather than probability measures alone. The graph contains only an open leaf and no recorded supporting steps or frozen commitments. The route remains open; no source stance or omitted-support assumption is supplied.

Review note: The description preserves the OPEN status and absence of supporting steps.
### 9805e3aa0cfa:r0 — target_5 / target

Target polarity: positive. The recorded inference combines Moss’s endorsed claim that assertability varies with the question under consideration, which supports the question-sensitive part, with Beddor and Goldstein’s endorsed claim that their modal-knowledge account avoids two difficulties for relevant-alternatives theory. The latter does not establish that assertability should track worldly information at nearby worlds; that support question remains unanswered. Its provenance lists omitted support (link_raTwoDifficulties), so that claim’s underlying support is not supplied here. The route is OPEN, with the inference unresolved; its commitments are not independently verified.

Review note: The route contains premises from two verified papers. Both CQs remain false. The omitted Beddor–Goldstein support is absent from the frozen route evidence; no claim is made that the original paper lacks that support.
### 9d3c169681bc:r0 — target_5 / negation

OPEN; target polarity is negation: the route attempts to support that adequate assertability conditions need not track both the question and worldly information at nearby worlds. Its recorded best-explanation step uses Moss’s endorsed claim that assertability varies with the question, Beddor and Goldstein’s endorsed claim that their defended theory avoids two difficulties for relevant-alternatives theory, and MacFarlane’s endorsed criticism of contextualism. These commitments are reported author claims, not independently verified; the graph does not show how they establish the negated target. The Beddor–Goldstein commitment omits the support link `beddorgoldstein2021:r36-47-refine:link_raTwoDifficulties`, so its use assumes that omitted support. The root remains the frontier: the explanation’s fit to question sensitivity and superiority to alternatives are unanswered; examination of alternatives is only partial. No qualifying cross-paper support is recorded.

Review note: The graph has premises from three verified papers; no qualifying cross-paper support means no CLOSED-derived proof, not absence of cross-paper premises. CQ3 is marked true while its answer says only partially. Both other CQs remain false. The omitted support is a frozen-route evidence gap.
### 476424c8082d:r0 — target_7 / target

OPEN; polarity is target. The route proposes that compositional epistemic-modal semantics represent question-sensitive assertability independently of information-parameter shifts from non-truth-tabular connectives. Its recorded commitments say that a semantic expressivism uses a partial interpretation from information situations to truth values (allowing acceptance, rejection, or neutrality), is logically conservative, and has non-classical behavior from connective–modal interaction. These author-endorsed claims do not establish the proposed independence. The other endorsed commitment says the defended modal-knowledge account avoids two difficulties for relevant-alternatives theory, but is not a direct argument for the target; its supporting text omits a linking support item. Endorsement reports the authors’ stance, not independent verification. The route remains open: its listed critical questions are unanswered, and the contribution has no verified cross-paper support.

Review note: The graph has premises from two verified papers. The summary’s no verified cross-paper support should be read as no qualifying CLOSED-derived proof; the source-paper identities of its premises are verified. Both CQs remain false. Omitted support concerns frozen evidence, not an absence of source argument.
### 935637cda889:r0 — target_7 / negation

This OPEN route targets the negation of target_7: it opposes the claim that a compositional account of epistemic-modal discourse should represent question-sensitive assertability independently of information-parameter shifts from non-truth-tabular connectives. Its graph contains only an unexpanded negation leaf, with no recorded supporting steps or frozen commitments. The route remains open; the supplied data gives no further support or blocker.

Review note: The description preserves the OPEN status and absence of supporting steps.

## Usage and provenance

| Scope | Calls | Input | Output | Cache read | Total tokens | API USD |
|---|---|---|---|---|---|---|
| Fresh preflights | 19 | 86330 | 4814 | 0 | 91144 | 0.0 |
| Fork plus summary reporting | 77 | 2479178 | 33584 | 33792 | 2546554 | 0.0 |
| Total new work | 96 | 2565508 | 38398 | 33792 | 2637698 | 0.0 |

The 77 fork/reporting calls comprise 2 isolation canaries, 3 target proposals, 7 classifiers, 12 leaf maps, 24 cut proposals, 5 slot formalizations, 12 CQ answers and 12 route summaries. All 96 new calls have actual accounting; unsettled 0, unknown usage 0, Claude/non-Codex 0, fallbacks 0. Subscription USD equivalent is unavailable. The requested model pin does not verify serving identity; serving identity remains unverified.

Native command elapsed 1,280.815 seconds; summary stage 522.984 seconds; summed model-call wall time 1,121.136 seconds. These measure different scopes and are not human labor estimates. Native HUMAN receipts log schema preflight, standalone canary, fork-from-freeze, the verbatim brief/success criteria and route-summary reporting. Operator-reported minutes are 0; unmeasured human time is not invented. Review/reporting work is documented in external control notes.

| Native HUMAN action | UTC timestamp |
|---|---|
| codex-schema-preflight | 2026-10-28T11:35:36.500230+00:00 |
| isolation-preflight | 2026-10-28T11:37:09.107542+00:00 |
| fork-from-freeze | 2026-10-28T11:37:54.697601+00:00 |
| operator-success-criteria | 2026-10-28T11:59:08.160949+00:00 |
| route-summary-reporting | 2026-10-28T11:59:23.650980+00:00 |

Historical extraction/API and Claude receipts are preserved in the full lineage. The zero API/Claude claim concerns this fork and its fresh preflights/report summaries. Combined report accounting remains $131.785270 measured plus $1.844820 unknown/reserved = $133.630090 budget-accounted; these are historical charges, not new pilot5 spend.

## Report verification

`ara report` completed over 64 runs. Native HTML: **1,383,398 bytes / 1.383398 decimal MB**. The independent copy contains 46,816 native report files / 4,851,657,729 bytes, including HTML, Markdown, data.json and all linked events, per-run sections, artifacts and tree sidecars. All SHA-256 hashes matched; generated staging files were reclaimed only after each delivered copy was verified. Native logs and previous delivered reports were preserved.

The audit reconstructed 155,224 event occurrences from 42,447 unique bodies, verified 1,787 artifact copies and checked 4,587 HTML links. Broken links 0, missing anchors 0; all 64 input logs/anchors unchanged.

Chromium 143.0.7499.4 opened the delivered file. Page errors 0; desktop 1440px / scroll width1440px. Mobile 390px / scroll width409px: **19px horizontal overflow**. Strict browser layout verdict: FAIL. Criterion 4 passes coverage/rendering; a fully responsive layout is not claimed. Native report bytes remain unchanged.

The native event index still mislabels **13,006 copied freeze-prefix occurrences** as original_in instead of imported_by. `import-origin-overlay.json` records the correction; accounting remains deduplicated.

Before this run, 15,912 byte-identical generated report staging files were reclaimed after comparison with delivered fork4, freeing 2,064,455,954 bytes; 76 unmatched staging files were retained. Those old generated staging directories are partial. Use the preserved delivered report bundles. This run’s new staging copy is likewise retired after verified delivery.

The companion route-summaries.html preserves each original model summary and places the source/polarity/CQ qualifications beside it. Audit JSON, browser receipts/screenshots, source-page excerpts, target and bridge reviews, trace/route verification and summary review are delivered alongside the native report.
Companion browser check PASS: 12 articles; desktop 1440/1440 px and mobile 390/390 px; 0 page errors; polarity/provenance corrections visible. Native current-run search details expanded successfully. The bounded overview truncates some route previews; complete graph evidence remains in linked JSON/DOT.


## Findings placement

1. R23 review confirmation remains pending; results provisional — **Execution and review status**.
2. Zero CLOSED-derived routes versus at least three required — **Acceptable pilot criteria**.
3. Pool underfilled at six retained out of ten; one semantic-restatement rejection despite formal novelty — **Target gates**.
4. Bridge pool concentrates on about and Beddor-Goldstein; slices expose nine commitments from five papers — **Guidance and context bounds**.
5. Five licensed scheme steps remain open; seven routes have no licensed proposal — **Routes and substantive review**.
6. Two CQ3 receipts marked supported describe only partial alternatives review — **Critical-question review**.
7. One frozen commitment omits a support link; this is not a claim that the original paper lacks an argument — **Source and summary review**.
8. Component source claims do not establish the proposed cross-paper relationships — **Source and summary review**.
9. Serving identity is unverified despite requested model pin — **Usage and provenance**.
10. Historical API/Claude usage in full lineage is separate from new Codex-only pilot usage — **Usage and provenance**.
11. Generated staging duplicates were reclaimed after exact hash checks; use delivered report bundles — **Report verification**.
12. Negated target_3 summary strengthens not-required into should-not; raw text must be read with the explicit scope correction — **Source and summary review**.
13. Two summaries say cross-paper support is absent or unverified although their graphs contain verified premises from two/three papers; they lack a qualifying closed proof — **Source and summary review**.
14. Source-page review covers readable prose; mathematical-font encoding warnings prevent a claim of exact notation verification — **Source and summary review**.
15. Native event index labels 13,006 copied prefix occurrences as original; use the origin overlay — **Report verification**.
16. Mobile layout overflows by 19px; rendering passes but strict responsive-layout check fails — **Report verification**.

**16 findings, 16 placed.**

## Continuation boundary

The native run is at awaiting_selection, but no route meets the acceptable-pilot route requirement. No route was selected, and no essay or submission was started. Next work requires the operator’s direction; this pass does not alter T, the configuration, source stance or the original model responses.

DONE zeta fork5 targets=6 derived_closed=0 structural_closed=0 open=12 criteria=P,P,F,P status=awaiting-selection report=/home/dev/ara-work/reports/overnight/fork5/report.html
