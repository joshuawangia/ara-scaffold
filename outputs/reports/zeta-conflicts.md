# zeta: live semantic-conflict detection

**60/60 candidate pairs classified: 3 `contradicts`, 7 `in_tension`, 35 `compatible`, 15 `unrelated`; 0 unclassified.** Source-reviewed status of the 10 flagged pairs: 0 `still_open`, 0 `addressed_by`, 9 `partial`, 1 `unknown`. **L3 is separately `unknown` and was omitted by the top 60 retrieval.**

Execution completed with exit 0 in 48.4 minutes, using the native classifier at `80a3448`. Original pilot-5 files, copied historical log prefix and frozen T were verified unchanged. Frozen T contains 169 commitments from 22 papers. No search, target proposal, selection, or writing stage was started.

## Scope and interpretation

xi round 26 at `80a344892d9acd1933bf47c1b6fd8fd986bbee5b` was approved by kappa4 with **0 blocking findings** and merged to main, as confirmed by the operator on 2026-10-29. The live conflict-detection results are **not provisional**. This code-review approval does not change the source-review qualifications or literature-status judgments below.

The classifier was the pinned native `ModelCalls.discover_gaps` path, which combines deterministic gap checks with `semantic_conflicts.classify_pairs`. No target proposal, argument search, route selection, or writing was invoked. The mandatory Codex isolation canary preceded classification. The full pilot schema-preflight suite was not invoked: it dispatches unrelated model stages. Direct `discover_gaps` does not require that CLI entry gate; each classifier response still passes the native strict wire schema and local validation. No code, prompt, or schema was modified.

Pairs are selected by descending overlap in frozen catalogue-definition terms, then lexical overlap, then IDs. Cross-paper pairs require at least one endorsed commitment. Native selection took 60 of 7,693 eligible pairs (0.78%); this is neither an exhaustive census nor a random sample. Formula-private names do not establish semantic compatibility. Every raw label below is a fallible semantic judgment, **not** a formal contradiction or an addition to T. Exact IDs and frozen stances are preserved; source-informed qualifications are separate from raw output.

Modern-status labels concern what the checked literature supports about the flagged issue. `addressed_by` means identifiable work addresses the historical mechanism/problem, not that a theory won; `partial` means relevant treatment without resolution of the full comparison; `unknown` means the exact relationship/current status is not established; `still_open` requires affirmative evidence of a current unresolved problem. Lack of a bridge or inaccessible full text is not enough for `still_open`. eps2's `partially_addressed` maps to the brief's `partial`.

All page numbers are physical PDF pages. The relevant original-source passages and selected modern passages were extracted locally; PDF hashes and the extracted-page inventory are retained in `source-page-manifest.json`. A page being extracted is not itself proof that its whole contents were reviewed: each entry below names the passages actually used. eps2's literature search is bounded and its modern additions have not been imported into frozen T. This task performs a source review against those existing materials, not a new literature search.

## Every flagged pair

### Pair 14 — `contradicts`; modern status `partial`

**A. `egan2007:salvage:dec68a6bbc12fd01:egan2007:r1-19:n_relativist_might`**

Paper: Egan, Andy (2007), *Epistemic Modals, Relativism and Assertion* (`egan2007`). Frozen stance: **endorsed**; attributed to: Andy Egan (author). Frozen citation: `egan2007:pdf:12#egan2007:salvage:dec68a6bbc12fd01:egan2007:r1-19:n_relativist_might`.

Frozen content: “It might be the case that P” is true relative to a centered world <w,t,i> iff it is compatible with everything within i’s epistemic reach at t in w that P; the semantic value of “Bond might be in Zurich” is the corresponding set of <w,t,i> triples.

**B. `yalcin2007:r23-33:rv_diagonal`**

Paper: Yalcin, Seth (2007), *Epistemic Modals* (`yalcin2007`). Frozen stance: **attacked**; attributed to: the diagonal view of epistemic modal content (akin to Egan 2007), considered and ultimately rejected by Yalcin. Frozen citation: `yalcin2007:pdf:27#yalcin2007:r23-33:rv_diagonal`.

Frozen content: For an unembedded epistemic modal sentence φ, its informational content is the diagonal proposition λc.⟦φ⟧^{c,s_c,w_c} determined by the two-dimensional matrix: a set of centered worlds true at a centered world just in case φ is compatible with the information available at that centered world.

**Raw classifier reason:**

> Egan endorses a centered-world compatibility account of epistemic-modal content. Yalcin’s passage attributes and rejects the diagonal view, described in closely matching terms as compatibility with available information at a centered world. The opposed stances concern substantially the same view.

**Source check:** Supported as a disagreement between endorsed and rejected accounts, with a qualification about identity. Egan2007 PDF12 states the centered-world epistemic-reach account; PDF13 distinguishes it from a possible-worlds/group account and explains how conversational sources enlarge epistemic reach. Yalcin2007 PDF27 presents the diagonal account and explicitly calls it akin to Egan2007 in footnote25. PDF28–30 contrasts it with the informational view and argues for the latter. The frozen attacked stance is therefore supported by the surrounding discussion, although the cited PDF27 alone presents the view rather than the rejection. The theories are close enough for a substantive disagreement, but epistemic reach and a context-supplied information state are not automatically identical. This is not a formal inconsistency in T. Yalcin PDF31 also notes that a suitably redefined diagonal can technically collapse into the informational view, at the cost of abandoning Reflexivity. Thus the opposition is not an impossibility theorem about every diagonal construction.

**Modern status:** `partial`. eps2 G1 and L5 are partial. Yalcin2018 PDF2–3 distinguishes illocutionary force from conversational update, while Beddor–Egan2018 PDF39–41 tests assessment-QUD effects and discusses relativist, cloudy contextualist and dynamic implementations. These works address the content/force and assessment motivations without resolving the exact Egan/diagonal versus informational comparison. No current-open certification follows.

Checked page extracts: egan2007: [PDF12](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/egan2007-pdf12.txt), [PDF13](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/egan2007-pdf13.txt); yalcin2007: [PDF27](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/yalcin2007-pdf27.txt), [PDF28](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/yalcin2007-pdf28.txt), [PDF29](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/yalcin2007-pdf29.txt), [PDF30](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/yalcin2007-pdf30.txt), [PDF31](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/yalcin2007-pdf31.txt); yalcin2018force: [PDF2](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/yalcin2018force-pdf2.txt), [PDF3](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/yalcin2018force-pdf3.txt); beddoregan2018: [PDF39](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf39.txt), [PDF40](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf40.txt), [PDF41](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf41.txt).

### Pair 17 — `in_tension`; modern status `partial`

**A. `hawkesteinertthrelkeld2021:r10-19-refine:inf_to_positive`**

Paper: Hawke, Peter; Steinert-Threlkeld, Shane (2021), *Semantic Expressivism for Epistemic Modals* (`hawkesteinertthrelkeld2021`). Frozen stance: **endorsed**; attributed to: Hawke and Steinert-Threlkeld. Frozen citation: `hawkesteinertthrelkeld2021:pdf:17-19#hawkesteinertthrelkeld2021:r10-19-refine:inf_to_positive`.

Frozen content: If the classic merely pragmatic frameworks miss the assertibility constraints, then a semantic expressivism is developed whose interpretation function maps information situations to truth-values and satisfies those constraints.

**B. `macfarlane2014:r247-268:relativist_proposal`**

Paper: MacFarlane, John (2014), *Assessment Sensitivity: Relative Truth and Its Applications* (`macfarlane2014`). Frozen stance: **endorsed**; attributed to: MacFarlane. Frozen citation: `macfarlane2014:pdf:268#macfarlane2014:r247-268:relativist_proposal`.

Frozen content: Epistemic modals are assessment-sensitive: their truth depends on what the assessor knows and varies with the context of assessment, so they have no absolute truth values, resist capture in standard truth-conditional frameworks, and undermine the motivation for expressivism.

**Raw classifier reason:**

> Both are endorsed. MacFarlane says assessment sensitivity undermines expressivism, while Hawke and Steinert-Threlkeld endorse a semantic expressivism. Their situation-indexed truth values could accommodate variability, so this is a tension rather than a direct contradiction.

**Source check:** Supported as a methodological tension, not a direct contradiction. Hawke–Steinert-Threlkeld2021 PDF17–19 rejects specific merely pragmatic treatments for missing assertibility constraints and develops a partial information-state semantics meeting them. MacFarlane2014 PDF268 argues that assessment sensitivity restores a broadly truth-conditional option and thereby undermines an anti-contextualist motivation for expressivism. This does not show that his account meets the later paper’s particular constraints, nor does the conditional expressivist proposal deny all assessment-sensitive truth conditions. The classifier’s suggestion that situation-indexed truth values could accommodate variability is a possibility, not an integration proved in these pages.

**Modern status:** `partial`. eps2 L1 and L5 record partial treatment. Hawke2023 PDF7–11 develops a related acceptance semantics for modal knowledge and documents its own logical tradeoffs; Yalcin2018 PDF2–3 separates force and conversational update. Beddor–Egan2018 PDF39–43 discusses rival ways to explain assessment-QUD effects. These support comparison, not a winning or unified architecture. Rudin2024 and Hawke2024expressivists are relevant abstract-only leads in eps2 and cannot supply missing full-text proof.

Checked page extracts: hawkesteinertthrelkeld2021: [PDF17](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawkesteinertthrelkeld2021-pdf17.txt), [PDF18](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawkesteinertthrelkeld2021-pdf18.txt), [PDF19](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawkesteinertthrelkeld2021-pdf19.txt); macfarlane2014: [PDF268](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/macfarlane2014-pdf268.txt); hawke2023acceptance: [PDF7](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawke2023acceptance-pdf7.txt), [PDF8](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawke2023acceptance-pdf8.txt), [PDF9](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawke2023acceptance-pdf9.txt), [PDF10](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawke2023acceptance-pdf10.txt), [PDF11](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawke2023acceptance-pdf11.txt); yalcin2018force: [PDF2](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/yalcin2018force-pdf2.txt), [PDF3](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/yalcin2018force-pdf3.txt); beddoregan2018: [PDF39](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf39.txt), [PDF40](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf40.txt), [PDF41](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf41.txt), [PDF42](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf42.txt), [PDF43](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf43.txt).

### Pair 20 — `in_tension`; modern status `partial`

**A. `macfarlane2014:r247-268:relativist_proposal`**

Paper: MacFarlane, John (2014), *Assessment Sensitivity: Relative Truth and Its Applications* (`macfarlane2014`). Frozen stance: **endorsed**; attributed to: MacFarlane. Frozen citation: `macfarlane2014:pdf:268#macfarlane2014:r247-268:relativist_proposal`.

Frozen content: Epistemic modals are assessment-sensitive: their truth depends on what the assessor knows and varies with the context of assessment, so they have no absolute truth values, resist capture in standard truth-conditional frameworks, and undermine the motivation for expressivism.

**B. `vonfintelgillies2011:union:item:vonfintelgillies2011:salvage:eccdcb12d37ac9c1:vonfintelgillies2011:joined2:r12-23:c_overall`**

Paper: von Fintel, Kai; Gillies, Anthony S. (2011), *'Might' Made Right* (`vonfintelgillies2011`). Frozen stance: **endorsed**; attributed to: von Fintel and Gillies. Frozen citation: `vonfintelgillies2011:pdf:22#vonfintelgillies2011:union:item:vonfintelgillies2011:salvage:eccdcb12d37ac9c1:vonfintelgillies2011:joined2:r12-23:c_overall`.

Frozen content: BEMs have clear advantages over currently fashionable relativist approaches: they require no innovations in the semantics of epistemic modals, use a standard context-dependent semantics, and their strange properties derive from their indeterminacy being used by design to achieve spectacular results.

**Raw classifier reason:**

> Both claims are endorsed. MacFarlane’s claim favors assessment-sensitive relativism and says standard truth-conditional frameworks resist capturing it; von Fintel and Gillies praise BEMs’ standard context-dependent semantics over relativist approaches. These are competing approaches, but the BEM claim does not directly deny MacFarlane’s account.

**Source check:** Supported as competition between endorsed approaches. MacFarlane2014 PDF268 proposes assessment-dependent modal truth and argues for its explanatory advantages. Von Fintel–Gillies2011 PDF2,12,22 instead preserves standard context-dependent semantic values and locates the distinctive behavior in indeterminacy plus pragmatics. PDF22 explicitly claims advantages over fashionable rivals. The classifier is right to preserve the difference between a rival positive program and a literal negation of every claim in the other program.

**Modern status:** `partial`. eps2 G1 and L6: Beddor–Egan2018 PDF39–43 directly distinguishes fixed-use assessment variation from use-context variation. It supports flexible relativism against standard contextualism, but also develops QUD-sensitive cloudy contextualism and an update-semantic alternative. Ball2020 PDF1–2 proposes temporal externalism as another explanation of disagreement/retraction. These address the comparison without settling it; the exact pair is partial, not certified still open.

Checked page extracts: macfarlane2014: [PDF268](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/macfarlane2014-pdf268.txt); vonfintelgillies2011: [PDF2](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/vonfintelgillies2011-pdf2.txt), [PDF12](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/vonfintelgillies2011-pdf12.txt), [PDF22](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/vonfintelgillies2011-pdf22.txt); beddoregan2018: [PDF39](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf39.txt), [PDF40](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf40.txt), [PDF41](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf41.txt), [PDF42](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf42.txt), [PDF43](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf43.txt); ball2020relativism: [PDF1](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/ball2020relativism-pdf1.txt), [PDF2](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/ball2020relativism-pdf2.txt).

### Pair 30 — `in_tension`; modern status `partial`

**A. `vonfintelgillies2011:union:item:vonfintelgillies2011:salvage:eccdcb12d37ac9c1:vonfintelgillies2011:joined2:r12-23:p_travel`**

Paper: von Fintel, Kai; Gillies, Anthony S. (2011), *'Might' Made Right* (`vonfintelgillies2011`). Frozen stance: **endorsed**; attributed to: von Fintel and Gillies. Frozen citation: `vonfintelgillies2011:pdf:12#vonfintelgillies2011:union:item:vonfintelgillies2011:salvage:eccdcb12d37ac9c1:vonfintelgillies2011:joined2:r12-23:p_travel`.

Frozen content: If the facts up to t allow groups G1, G2, ... as resolutions of the contextual parameter, delimiting a cloud C of contexts, then an utterance of might(B)(φ) with respect to C at t puts into play the set of propositions P such that for some c in C, the semantic value of might(B)(φ) at c is P; a proposition put into play is available for denial and uptake.

**B. `willer2013:r21-40:inf_contextualism`**

Paper: Willer, Malte (2013), *Dynamics of Epistemic Modality* (`willer2013`). Frozen stance: **endorsed**; attributed to: Willer. Frozen citation: `willer2013:pdf:33-34#willer2013:r21-40:inf_contextualism`.

Frozen content: Because the ambiguity hypothesis fails standard tests such as the contradiction test, and because no principle predicts that all readings become legitimate objects of acceptance or denial, the contextualist floating-propositions response is dubious for at least two reasons.

**Raw classifier reason:**

> Both are endorsed: von Fintel and Gillies say an utterance can put the propositions from a cloud of contexts into play for denial and uptake; Willer argues the contextualist floating-propositions response is dubious, since no principle predicts that all readings enter discourse as objects of acceptance or denial. This challenges the rationale for the proposal, though it does not directly deny this specific mechanism.

**Source check:** Supported, and the source identifies a direct critical connection. Von Fintel–Gillies2011 PDF12 gives Travel: the utterance puts propositions from admissible contexts into play for denial and uptake. Willer2013 PDF33–34 explicitly cites von Fintel–Gillies2011 (footnote33) and challenges the floating-propositions response on ambiguity-test and discourse-principle grounds. This is a reasoned objection to an endorsed mechanism, rather than proof that the conditional Travel formulation is logically false.

**Modern status:** `partial`. eps2 G1/L6: Beddor–Egan2018 PDF40–42 revisits cloudy contextualism. PDF41 supplies a QUD-Sensitive Appraisal Norm, and PDF42 footnote29 explicitly derives it from a more general principle for underspecified or ambiguous utterances. That is relevant progress on the demand for a non-ad-hoc pragmatic principle, but it does not in the passages checked settle Willer’s separate claim that the ambiguity hypothesis lacks independent support, nor establish that all readings legitimately enter discourse. Thus partial, with an identifiable response component rather than a certified untouched open problem.

Checked page extracts: vonfintelgillies2011: [PDF12](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/vonfintelgillies2011-pdf12.txt); willer2013: [PDF33](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/willer2013-pdf33.txt), [PDF34](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/willer2013-pdf34.txt); beddoregan2018: [PDF40](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf40.txt), [PDF41](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf41.txt), [PDF42](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf42.txt).

### Pair 34 — `in_tension`; modern status `partial`

**A. `hawkesteinertthrelkeld2021:r10-19-refine:inf_to_positive`**

Paper: Hawke, Peter; Steinert-Threlkeld, Shane (2021), *Semantic Expressivism for Epistemic Modals* (`hawkesteinertthrelkeld2021`). Frozen stance: **endorsed**; attributed to: Hawke and Steinert-Threlkeld. Frozen citation: `hawkesteinertthrelkeld2021:pdf:17-19#hawkesteinertthrelkeld2021:r10-19-refine:inf_to_positive`.

Frozen content: If the classic merely pragmatic frameworks miss the assertibility constraints, then a semantic expressivism is developed whose interpretation function maps information situations to truth-values and satisfies those constraints.

**B. `willer2013:r1-20:c_uniform_account`**

Paper: Willer, Malte (2013), *Dynamics of Epistemic Modality* (`willer2013`). Frozen stance: **endorsed**; attributed to: Willer. Frozen citation: `willer2013:pdf:14#willer2013:r1-20:c_uniform_account`.

Frozen content: Variation in what is known has a pragmatic but no semantic effect on epistemic modals: it leads to variation in assessment of epistemic-modality judgments, not communicated content. This view is possible because the semantics assigns no truth conditions to such sentences but characterizes content through effects on information available to interlocutors.

**Raw classifier reason:**

> Both are endorsed accounts of epistemic modals. Hawke and Steinert-Threlkeld’s proposal gives sentences a partial truth-value interpretation, while Willer says such sentences have no truth conditions and that knowledge variation affects assessment only pragmatically. This is a tension, though their accounts may differ in scope or notion of content.

**Source check:** A qualified methodological tension is supported. Hawke–Steinert-Threlkeld2021 PDF17–19 distinguishes semantic expressivism from pragmatic expressivism and explicitly criticizes update semantics before giving its partial interpretation function. Willer2013 PDF14 describes content by effects on information states and assigns variation in assessment to pragmatics. However, Hawke’s values 1/0 at an information state are explained as acceptance/rejection; they must not be equated without argument with ordinary truth conditions at worlds. The disagreement concerns compositional value types and constraints, not a simple truth/no-truth contradiction.

**Modern status:** `partial`. eps2 L5/L7 are partial. Willer2023propositionalism PDF1–2 explicitly defends dynamic analyses against dynamic propositionalism; it is continuing comparative work, not a resolution of this exact pair. Yalcin2018 PDF2–3 separates force and update roles. Hawke2023 PDF8–10 provides a related bilateral acceptance semantics with explicit knowledge clauses, but does not establish equivalence to Willer’s account. These sources clarify alternatives without settling the full comparison.

Checked page extracts: hawkesteinertthrelkeld2021: [PDF17](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawkesteinertthrelkeld2021-pdf17.txt), [PDF18](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawkesteinertthrelkeld2021-pdf18.txt), [PDF19](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawkesteinertthrelkeld2021-pdf19.txt); willer2013: [PDF14](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/willer2013-pdf14.txt); willer2023propositionalism: [PDF1](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/willer2023propositionalism-pdf1.txt), [PDF2](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/willer2023propositionalism-pdf2.txt); yalcin2018force: [PDF2](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/yalcin2018force-pdf2.txt), [PDF3](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/yalcin2018force-pdf3.txt); hawke2023acceptance: [PDF8](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawke2023acceptance-pdf8.txt), [PDF9](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawke2023acceptance-pdf9.txt), [PDF10](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawke2023acceptance-pdf10.txt).

### Pair 35 — `in_tension`; modern status `unknown`

**A. `hawkesteinertthrelkeld2021:r10-19-refine:inf_to_positive`**

Paper: Hawke, Peter; Steinert-Threlkeld, Shane (2021), *Semantic Expressivism for Epistemic Modals* (`hawkesteinertthrelkeld2021`). Frozen stance: **endorsed**; attributed to: Hawke and Steinert-Threlkeld. Frozen citation: `hawkesteinertthrelkeld2021:pdf:17-19#hawkesteinertthrelkeld2021:r10-19-refine:inf_to_positive`.

Frozen content: If the classic merely pragmatic frameworks miss the assertibility constraints, then a semantic expressivism is developed whose interpretation function maps information situations to truth-values and satisfies those constraints.

**B. `yalcin2007:joined4:yalcin2007:xr2:inf_domain_to_prob`**

Paper: Yalcin, Seth (2007), *Epistemic Modals* (`yalcin2007`). Frozen stance: **endorsed**; attributed to: Seth Yalcin. Frozen citation: `yalcin2007:pdf:11-33#yalcin2007:joined4:yalcin2007:xr2:inf_domain_to_prob`.

Frozen content: The probabilistic proposal upgrades the earlier domain semantics by replacing the set-of-worlds value of the information parameter with a probability space, because probability operators generate the same epistemic contradictions as epistemic possibility and necessity modals.

**Raw classifier reason:**

> Hawke and Steinert-Threlkeld endorse a semantic alternative and reject domain semantics supplemented with boolean disjunction as missing their constraints. Yalcin endorses a probabilistic upgrade to earlier domain semantics, but the definition does not say it uses that supplementation or fails those constraints. The views may overlap, requiring that distinction; they do not directly contradict.

**Source check:** The precise conflict is not established. Hawke–Steinert-Threlkeld2021 PDF17–19 targets domain semantics supplemented with Boolean disjunction and a specified update semantics. Yalcin2007 PDF33 proposes changing the information parameter to a probability space and explicitly describes the construction as one path among alternatives. The broad frozen citation spans PDF11–33, but the probability-upgrade passage is PDF33. The criticism of the specified domain system cannot simply be transferred to every probabilistic extension without checking its disjunction, acceptance and consequence clauses. The classifier itself acknowledges this missing step.

**Modern status:** `unknown`. eps2 L4/L7 and G2 identify relevant partial work, including Herbstritt–Franke2019 PDF5–6 on a conservative compositional model for nested probabilistic beliefs and Hawke2023 PDF7–11 on acceptance/knowledge. Neither checked passage establishes that the precise probabilistic extension inherits or avoids the constraints criticized in Hawke–Steinert-Threlkeld2021. Its exact tension/current resolution is therefore unknown, not certified still open.

Checked page extracts: hawkesteinertthrelkeld2021: [PDF17](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawkesteinertthrelkeld2021-pdf17.txt), [PDF18](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawkesteinertthrelkeld2021-pdf18.txt), [PDF19](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawkesteinertthrelkeld2021-pdf19.txt); yalcin2007: [PDF33](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/yalcin2007-pdf33.txt); herbstrittfranke2019: [PDF5](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/herbstrittfranke2019-pdf5.txt), [PDF6](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/herbstrittfranke2019-pdf6.txt); hawke2023acceptance: [PDF7](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawke2023acceptance-pdf7.txt), [PDF8](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawke2023acceptance-pdf8.txt), [PDF9](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawke2023acceptance-pdf9.txt), [PDF10](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawke2023acceptance-pdf10.txt), [PDF11](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hawke2023acceptance-pdf11.txt).

### Pair 42 — `contradicts`; modern status `partial`

**A. `macfarlane2011:r1-22:main_concl`**

Paper: MacFarlane, John (2011), *Epistemic Modals Are Assessment-Sensitive* (`macfarlane2011`). Frozen stance: **endorsed**; attributed to: MacFarlane. Frozen citation: `macfarlane2011:pdf:3-22#macfarlane2011:r1-22:main_concl`.

Frozen content: Epistemic modals are assessment-sensitive: a viable truth-conditional semantics for them is available once truth is allowed to vary with the context of assessment as well as the context of use; this semantics meets the objections to contextualism and undermines the motivation for abandoning truth-conditional semantics in favor of force-modifier or expressivist theories.

**B. `willer2013:r1-20:c_uniform_account`**

Paper: Willer, Malte (2013), *Dynamics of Epistemic Modality* (`willer2013`). Frozen stance: **endorsed**; attributed to: Willer. Frozen citation: `willer2013:pdf:14#willer2013:r1-20:c_uniform_account`.

Frozen content: Variation in what is known has a pragmatic but no semantic effect on epistemic modals: it leads to variation in assessment of epistemic-modality judgments, not communicated content. This view is possible because the semantics assigns no truth conditions to such sentences but characterizes content through effects on information available to interlocutors.

**Raw classifier reason:**

> MacFarlane endorses a truth-conditional semantics for epistemic modals, while Willer endorses an account that assigns them no truth conditions and treats variation as pragmatic. They directly disagree about whether these sentences have truth conditions.

**Source check:** Supported as incompatible semantic proposals for the same expressions. MacFarlane2011 PDF20–22 distinguishes contexts of use/assessment and gives epistemic-modal truth values relative to the assessor; PDF21 explicitly denies absolute truth values while retaining assessment-relative ones. Willer2013 PDF14 explicitly says the semantics does not ascribe truth conditions and makes information differences pragmatic determinants of assessment rather than changes in what is said. The classifier’s direct disagreement is about these kinds of semantic theory, not an absolute-versus-relative truth equivocation or a solver contradiction.

**Modern status:** `partial`. eps2 G1/L5/L6: Beddor–Egan2018 PDF39–43 provides assessment-QUD experiments but explicitly allows both flexible relativist and dynamic implementations; PDF43 sketches an update-semantic account yielding the same truth-appraisal predictions. Ball2020 PDF1–2 supplies a further metasemantic competitor; Willer2023propositionalism PDF1–2 continues the dynamic/propositional comparison. The data and mechanisms are addressed, but they do not uniquely select between the theories. Status partial.

Checked page extracts: macfarlane2011: [PDF20](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/macfarlane2011-pdf20.txt), [PDF21](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/macfarlane2011-pdf21.txt), [PDF22](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/macfarlane2011-pdf22.txt); willer2013: [PDF14](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/willer2013-pdf14.txt); beddoregan2018: [PDF39](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf39.txt), [PDF40](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf40.txt), [PDF41](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf41.txt), [PDF42](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf42.txt), [PDF43](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf43.txt); ball2020relativism: [PDF1](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/ball2020relativism-pdf1.txt), [PDF2](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/ball2020relativism-pdf2.txt); willer2023propositionalism: [PDF1](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/willer2023propositionalism-pdf1.txt), [PDF2](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/willer2023propositionalism-pdf2.txt).

### Pair 46 — `contradicts`; modern status `partial`

**A. `macfarlane2014:r247-268:relativist_proposal`**

Paper: MacFarlane, John (2014), *Assessment Sensitivity: Relative Truth and Its Applications* (`macfarlane2014`). Frozen stance: **endorsed**; attributed to: MacFarlane. Frozen citation: `macfarlane2014:pdf:268#macfarlane2014:r247-268:relativist_proposal`.

Frozen content: Epistemic modals are assessment-sensitive: their truth depends on what the assessor knows and varies with the context of assessment, so they have no absolute truth values, resist capture in standard truth-conditional frameworks, and undermine the motivation for expressivism.

**B. `willer2013:r1-20:c_uniform_account`**

Paper: Willer, Malte (2013), *Dynamics of Epistemic Modality* (`willer2013`). Frozen stance: **endorsed**; attributed to: Willer. Frozen citation: `willer2013:pdf:14#willer2013:r1-20:c_uniform_account`.

Frozen content: Variation in what is known has a pragmatic but no semantic effect on epistemic modals: it leads to variation in assessment of epistemic-modality judgments, not communicated content. This view is possible because the semantics assigns no truth conditions to such sentences but characterizes content through effects on information available to interlocutors.

**Raw classifier reason:**

> Both definitions are endorsed. MacFarlane says epistemic modals’ truth varies with the assessor; Willer says changes in what is known have no semantic effect and change only pragmatic assessment, not communicated content. These are opposing accounts of that variation.

**Source check:** Supported as the same broad semantic opposition as pair42, now using MacFarlane2014 PDF268 and Willer2013 PDF14. MacFarlane attributes variation to assessment-relative truth; Willer assigns it to pragmatic assessment in a semantics of information-state effects without truth conditions. One qualification matters: assessment-sensitive truth does not itself require the communicated content to change. Both accounts can preserve what was said while explaining assessment differently. The raw reason must not be read as showing that MacFarlane changes content whenever the assessor changes.

**Modern status:** `partial`. eps2 G1/L5/L6: Beddor–Egan2018 PDF39–43 develops assessment-QUD diagnostics alongside cloudy-contextualist and dynamic alternatives; PDF43 explicitly sketches matching truth-appraisal predictions in an update setting. Ball2020 PDF1–2 adds a metasemantic alternative, and Willer2023propositionalism PDF1–2 continues comparison of dynamic and propositional approaches. These are partial treatments, not consensus or proof of equivalence. This pair overlaps the dispute in pair42 and is not counted as a distinct independent discovery.

Checked page extracts: macfarlane2014: [PDF268](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/macfarlane2014-pdf268.txt); willer2013: [PDF14](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/willer2013-pdf14.txt); beddoregan2018: [PDF39](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf39.txt), [PDF40](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf40.txt), [PDF41](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf41.txt), [PDF42](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf42.txt), [PDF43](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf43.txt); ball2020relativism: [PDF1](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/ball2020relativism-pdf1.txt), [PDF2](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/ball2020relativism-pdf2.txt); willer2023propositionalism: [PDF1](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/willer2023propositionalism-pdf1.txt), [PDF2](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/willer2023propositionalism-pdf2.txt).

### Pair 49 — `in_tension`; modern status `partial`

**A. `moss2015:union:item:moss2015:salvage:3870505846b36fcb:moss2015:r1-10:n_thesis`**

Paper: Moss, Sarah (2015), *On the Semantics and Pragmatics of Epistemic Vocabulary* (`moss2015`). Frozen stance: **endorsed**; attributed to: Sarah Moss. Frozen citation: `moss2015:pdf:1-2#moss2015:union:item:moss2015:salvage:3870505846b36fcb:moss2015:r1-10:n_thesis`.

Frozen content: A semantics that assigns sets of probability measures, rather than sets of worlds, as sentential semantic values for epistemic expressions (possibility and necessity modals, indicative conditionals) should be adopted: what it lacks in conservatism it makes up for in strength.

**B. `vonfintelgillies2011:union:item:vonfintelgillies2011:salvage:eccdcb12d37ac9c1:vonfintelgillies2011:joined2:r12-23:p_two_implementations`**

Paper: von Fintel, Kai; Gillies, Anthony S. (2011), *'Might' Made Right* (`vonfintelgillies2011`). Frozen stance: **endorsed**; attributed to: von Fintel and Gillies. Frozen citation: `vonfintelgillies2011:pdf:12#vonfintelgillies2011:union:item:vonfintelgillies2011:salvage:eccdcb12d37ac9c1:vonfintelgillies2011:joined2:r12-23:p_two_implementations`.

Frozen content: Two ways of making the cloud-of-contexts intuition precise differ in how labor is divided between semantics and pragmatics: (i) constructions such as bems can have sets of propositions rather than propositions as semantic values, assigned relative to sets of admissible contexts rather than single contexts; or (ii) ordinary semantic values can be assigned at determinate contexts while a richer pragmatics does the explanatory work. Option (ii) affords a better view of the landmark properties of bems.

**Raw classifier reason:**

> Both sources endorse their claims. Moss favors sets of probability measures as semantic values for epistemic expressions; von Fintel and Gillies prefer determinate-context values with richer pragmatics for bems over sets of propositions. Their emphasis on semantics versus pragmatics is in tension, but the different value types and scope leave room to distinguish them.

**Source check:** Supported only as a qualified rivalry of architectures. Moss2015 PDF1–2 advocates sets of probability measures for a range including modals and indicative conditionals, motivated by nested and disjoined epistemic vocabulary. Von Fintel–Gillies2011 PDF12 compares ways to implement a cloud of contexts for bare epistemic modals and opts for normal values at determinate contexts plus richer pragmatics. Their alternative sets of propositions are not Moss’s sets of probability measures. Neither passage alone demonstrates that every probabilistic compositional semantics conflicts with a cloud-based pragmatic account.

**Modern status:** `partial`. eps2 G2/L4/L5: Herbstritt–Franke2019 PDF5–6 supplies a conservative possible-worlds analysis for nested probabilistic beliefs; footnote2 on PDF5 says its experimental application is practically equivalent to Moss’s analysis. Beddor–Egan2018 PDF40–43 develops QUD-sensitive cloudy-contextualist and dynamic alternatives for assessment effects. These are concrete partial comparisons and mechanisms, not proof that the original full theories are equivalent or that one supersedes the other.

Checked page extracts: moss2015: [PDF1](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/moss2015-pdf1.txt), [PDF2](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/moss2015-pdf2.txt); vonfintelgillies2011: [PDF12](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/vonfintelgillies2011-pdf12.txt); herbstrittfranke2019: [PDF5](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/herbstrittfranke2019-pdf5.txt), [PDF6](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/herbstrittfranke2019-pdf6.txt); beddoregan2018: [PDF40](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf40.txt), [PDF41](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf41.txt), [PDF42](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf42.txt), [PDF43](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/beddoregan2018-pdf43.txt).

### Pair 58 — `in_tension`; modern status `partial`

**A. `hollidaymandelkern2024:r1-17:c_abstract_program`**

Paper: Holliday, Wesley H.; Mandelkern, Matthew (2024), *The Orthologic of Epistemic Modals* (`hollidaymandelkern2024`). Frozen stance: **endorsed**; attributed to: Holliday and Mandelkern. Frozen citation: `hollidaymandelkern2024:pdf:1#hollidaymandelkern2024:r1-17:c_abstract_program`.

Frozen content: A semantics and logic for epistemic modals makes epistemic contradictions genuine contradictions and invalidates distributivity and disjunctive syllogism while otherwise preserving classical laws; it begins with an algebraic semantics based on ortholattices rather than Boolean algebras, then gives a possibility semantics based on partial possibilities related by compatibility; both semantics yield the same consequence relation, which is axiomatized.

**B. `moss2015:union:item:moss2015:salvage:3870505846b36fcb:moss2015:r1-10:n_thesis`**

Paper: Moss, Sarah (2015), *On the Semantics and Pragmatics of Epistemic Vocabulary* (`moss2015`). Frozen stance: **endorsed**; attributed to: Sarah Moss. Frozen citation: `moss2015:pdf:1-2#moss2015:union:item:moss2015:salvage:3870505846b36fcb:moss2015:r1-10:n_thesis`.

Frozen content: A semantics that assigns sets of probability measures, rather than sets of worlds, as sentential semantic values for epistemic expressions (possibility and necessity modals, indicative conditionals) should be adopted: what it lacks in conservatism it makes up for in strength.

**Raw classifier reason:**

> Both commitments are endorsed. Moss recommends sets of probability measures as semantic values for epistemic expressions, while Holliday and Mandelkern develop ortholattice and partial-possibility semantics for epistemic modals. These are potentially competing accounts, but neither commitment rules out the other, so their scope or relationship would need clarification.

**Source check:** The two frozen abstract-level commitments alone show different positive programs, not incompatibility. Reading beyond them supplies a concrete qualified comparison: Holliday–Mandelkern2024 PDF20 discusses Moss’s nested-modality motivation and offers its own treatment without collapse; PDF50 footnote30 excludes a systematic review of probabilistic approaches. PDF55 nevertheless explicitly identifies a prima facie problem for Moss-style contents: ordinary probability measures do not directly measure sets of probability measures, complicating discourse about the probability of a modal claim. It cites attempted solutions, not a settled refutation. PDF57 lists a model of credences on epistemic-modal propositions among its own further tasks. Moss2015 PDF1–2 states the broader probabilistic program including conditionals and nested vocabulary. Thus there are real comparison points, but the classifier’s general rivalry is broader than any demonstrated contradiction.

**Modern status:** `partial`. eps2 G2/L4/L7 identifies partial modern treatment of nesting, probability and embedding. Herbstritt–Franke2019 PDF5–6 gives a conservative nested-belief semantics and notes practical equivalence to Moss for its experimental setting; that does not by itself solve Holliday–Mandelkern’s PDF55 problem about probabilities of sentential contents. Mandelkern2025dynamic PDF16–17 clarifies embedding/order desiderata but does not settle this full probabilistic-versus-possibility comparison. The 2024 paper’s cited solution leads and future-work statements are not a certified still-open verdict in 2026. Status partial.

Checked page extracts: hollidaymandelkern2024: [PDF1](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hollidaymandelkern2024-pdf1.txt), [PDF20](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hollidaymandelkern2024-pdf20.txt), [PDF50](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hollidaymandelkern2024-pdf50.txt), [PDF55](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hollidaymandelkern2024-pdf55.txt), [PDF57](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/hollidaymandelkern2024-pdf57.txt); moss2015: [PDF1](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/moss2015-pdf1.txt), [PDF2](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/moss2015-pdf2.txt); herbstrittfranke2019: [PDF5](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/herbstrittfranke2019-pdf5.txt), [PDF6](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/herbstrittfranke2019-pdf6.txt); mandelkern2025dynamic: [PDF16](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/mandelkern2025dynamic-pdf16.txt), [PDF17](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-pages/mandelkern2025dynamic-pdf17.txt).

## L3: safety and assessment-sensitive retraction — `unknown`

This run does **not** directly classify L3. The top 60 use 16 of the 22 papers represented in frozen T and contain no Beddor–Goldstein2021 commitments. The first eligible pair involving that paper is rank 64: `beddorgoldstein2021:r1-23:c_info_sensitive_safety` with `egan2007:salvage:dec68a6bbc12fd01:egan2007:r1-19:n_relativist_might`. The safety condition paired with MacFarlane's retraction illustration `macfarlane2014:r114-135:n30` ranks 7058; paired with his norms qualification `macfarlane2014:r114-135:q6` it ranks 7059. All these positions come from an offline run of the same native ranking, not extra classifier calls. See `l3-coverage.json` in the control directory. Absence from the selected pairs is a retrieval omission, not a compatibility verdict.

The source check establishes separate components:

- Beddor and Goldstein, *Mighty Knowledge* (2021), physical PDF23 §5.3.3, derives information-sensitive safety: at a nearby world where credence in A is high, A's worldly probability must also be high. Belief reports undergo flavor shift; the condition concerns modal knowledge, not a speaker's later obligation to withdraw a speech act. Frozen anchors include `beddorgoldstein2021:r1-23:c_info_sensitive_safety` (PDF5–15) and `beddorgoldstein2021:r1-23:ic_derive_safety` (PDF23), both **endorsed**. PDF41's relevant-alternatives difficulty and footnote41 concern Safety and language fragments; they do not state a retraction bridge.
- MacFarlane, *Assessment Sensitivity* (2014), physical PDF122 (=printed 108), states the Retraction Rule: hold the original use context fixed and evaluate truth from the later assessment context. PDF123–124 illustrates the difference with taste; PDF128 allows the Reflexive Knowledge Rule as an alternative assertion norm. This alternative does not identify that norm with Beddor–Goldstein's safety semantics. Frozen anchors `macfarlane2014:r114-135:n30` and `macfarlane2014:r114-135:q6` are **endorsed**.
- MacFarlane, *Epistemic Modals* (2011), physical PDF20–22 §§5.1–5.3, supplies the epistemic-modal application: Sally learns that Joe is not in Boston and should retract her earlier might-claim. PDF22 explicitly makes later acquired knowledge relevant, rather than the mere existence of accessible but unacquired information. This is a substantive comparison point with worldly-information accounts, not by itself a contradiction: modal assertion/retraction and knowledge of a modal are different explananda.
- Hawke, *An Acceptance Semantics for Stable Modal Knowledge* (2023), physical PDF7–11, develops stable acceptance under accessible refinements and worldly information. PDF8 distinguishes constraints on ordinary might-claims from constraints on knowledge ascriptions and chooses the latter. PDF9–11 defines the semantics and proves its logical properties. These pages provide a bridge component but no derivation of the specified probabilistic safety-to-retraction connection.

This agrees with eps2's “Linking claims and CQs,” L3: **unknown; no read source licenses the required linking claim**. The full texts of *Modal Knowledge for Expressivists* (2024) and *Stable acceptance for mighty knowledge* (2024) remain unavailable in eps2's audit. The former's abstract mentions a safety comparison, which establishes relevance only. The 2023 extended abstract cannot substitute for either 2024 paper. Beddor–Egan2018 PDF39–43 and Ball2020 PDF1–2 supply alternative assessment/retraction explanations; they do not prove this specific unification. No source reviewed here certifies that L3 remains an open problem as of 2026, so it is not counted `still_open`.

## Deterministic gap flags

The native deterministic checks are reported separately from semantic labels. Their returned counters are:

```json
{
  "status": "verified_frozen_candidates",
  "formal_contradictions": 0,
  "stance_conflicts": 0,
  "open_problem_flags": 3,
  "solver_checks": 16,
  "solver_results": {
    "SOLVER_COUNTEREXAMPLE": 16
  },
  "set_search": "all_shared_symbol_cross_paper_pairs_plus_one_minimal_witness_per_component"
}
```

- `gap:e7d1b6e20262d0d61eb4135799c7ca8a2649dd6792003a9fb794e9bd9060a7a4` — `open_problem`; commitments: `eganweatherson2011:r1-21:ic13`.
- `gap:9aedd7e6790f860ed0f9b052b9e15584e5d8f75f6d87bfcbb4fdd6dc2a3addd8` — `open_problem`; commitments: `moss2015:union:item:moss2015:salvage:e986b46e97e98057:moss2015:r11-20:p11_dialogue`.
- `gap:3736a732a2fab2d0b8b16dc4e93118889a3a932f3b6788223cc717608d9d12b6` — `open_problem`; commitments: `wright2007:r1-22:n63`.

eps2’s “Gap currency” treats the Egan–Weatherson motivation/location question as `partial`, Moss’s nested-probability/answerhood question as `partial`, and Wright’s historical lack-of-a-clear-model claim as `addressed_by` MacFarlane and later experiments. These lexical flags are not three newly certified open problems. None is counted as a semantic conflict or as `still_open` here.

## Execution, integrity, and usage

- Pinned checkout: `/home/dev/ara-work/run-80a3448`; full revision `80a344892d9acd1933bf47c1b6fd8fd986bbee5b`; clean before and after.
- Original: `/home/dev/ara-scaffold/runs/codex-pilot-5`. Independent working copy: `/home/dev/ara-scaffold/runs/codex-conflicts-live`. All 167 original files matched the saved SHA-256 manifest after execution; no added or missing original files. Copying used separate inodes, not hardlinks.
- Preserved imported prefix: 8743 records / 402,455,115 bytes. Appended interval: 381 records. Final log chain and anchor verified; `commitments.json`, `frozen-t.json`, and `commitment-provenance.json` unchanged.
- Cache storage was relocated to the working copy before provider construction. Historical configuration and log records were not rewritten. Effective runtime configuration and authorization were appended to the copied log.
- New model receipts: 61, all `codex_cli`, requested `gpt-6-luna`, high effort; 60 classifier calls plus one mandatory isolation canary. Zero Claude/API calls, zero cache replays, zero provider fallbacks. Accounting categories: `{'actual': 61}`.
- Local usage including canary: 221,127 input + 16,892 output + 105,984 cache-read + 0 cache-write tokens = 344,003 tokens; 0 server-tool uses.
- Usage by stage: `{"classify_conflict": {"cache_read_tokens": 105984, "cache_write_tokens": 0, "input_tokens": 216806, "output_tokens": 15431, "server_tool_uses": 0}, "isolation_canary": {"cache_read_tokens": 0, "cache_write_tokens": 0, "input_tokens": 4321, "output_tokens": 1461, "server_tool_uses": 0}}`.
- Subscription dollar equivalent is unavailable. The log’s numeric $0 is not measured free usage or an API price estimate. Served model/version is unverified by the CLI; the requested model is recorded, not promoted into a verified served identity.
- The copied history includes older reservation-accounted usage; the runtime logged its reconciliation. That inherited history is excluded from the new-usage totals above.
- The isolation canary passed. The native adapter used read-only authentication transport; no credentials were copied into the run or report. No tracked code changes or philosophical content were committed.

## Evidence and coverage

- [All 60 raw pair results](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/pairs.json), [ranking](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/ranking.json), [source-informed reviews](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/reviews.json), [source-page manifest](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-page-manifest.json).
- [Final audit](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/final-audit.json), [copy verification](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/copy-verification.json), [original manifest](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/source-manifest.json), [exit receipt](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/classify-exit.json), [native detection result](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/detection.json).
- [L3 ranking audit](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/l3-coverage.json), [control notes](/home/dev/ara-scaffold/runs/codex-conflicts-live-control/work-notes.md), [eps2 literature review](/home/dev/ara-work/reports/eps2-bridge-literature.md).
- Native run log: `/home/dev/ara-scaffold/runs/codex-conflicts-live/events.jsonl`. Report/control artifacts remain outside tracked source.

Counts describe individual candidate pairs, not distinct philosophical disputes: several pairs can restate the same disagreement. Compatible/unrelated labels are not source-reviewed certificates for whole theories; this report checks every positive conflict/tension and the special L3 lead. Modern access gaps and the bounded eps2 sweep preclude an exhaustive 2026 literature verdict.

## Findings placement

| Finding | Where reported |
| --- | --- |
| F1. Approved code/review status and direct-call schema scope | Scope and interpretation |
| F2. Only 60/7,693 eligible pairs, 16/22 papers; pair counts are not dispute counts | Scope and interpretation; Evidence and coverage |
| F3. L3 omitted by retrieval and its linking claim remains unknown | L3 |
| F4. Semantic labels are fallible; no formal contradiction or modern-open certification follows from a label | Scope and interpretation; every pair’s Source check and Modern status |
| F5. Subscription price equivalent and served version unavailable; inherited usage excluded | Execution, integrity, and usage |
| F6. Three historical lexical flags have later treatments and are not new open problems | Deterministic gap flags |
| F7. Pair 14: raw `contradicts` with source qualifications; status `partial` | Every flagged pair, Pair 14 |
| F8. Pair 17: raw `in_tension` with source qualifications; status `partial` | Every flagged pair, Pair 17 |
| F9. Pair 20: raw `in_tension` with source qualifications; status `partial` | Every flagged pair, Pair 20 |
| F10. Pair 30: raw `in_tension` with source qualifications; status `partial` | Every flagged pair, Pair 30 |
| F11. Pair 34: raw `in_tension` with source qualifications; status `partial` | Every flagged pair, Pair 34 |
| F12. Pair 35: raw `in_tension` with source qualifications; status `unknown` | Every flagged pair, Pair 35 |
| F13. Pair 42: raw `contradicts` with source qualifications; status `partial` | Every flagged pair, Pair 42 |
| F14. Pair 46: raw `contradicts` with source qualifications; status `partial` | Every flagged pair, Pair 46 |
| F15. Pair 49: raw `in_tension` with source qualifications; status `partial` | Every flagged pair, Pair 49 |
| F16. Pair 58: raw `in_tension` with source qualifications; status `partial` | Every flagged pair, Pair 58 |

**16 findings, 16 placed.**
