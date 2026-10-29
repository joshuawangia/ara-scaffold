# From literature to audited drafts: how ARA was built, run, and corrected

*An anonymised methodology report • Version 3 • correspondence checkpoint: 29 October 2026, 20:41:14 UTC*

## Abstract

ARA combines language-model proposals with a deterministic, bank-constrained argument engine. This report reconstructs its development and use from correspondence, run receipts, pilot reports, and source-linked reviews. The scaffold was **designed and directed by a human, and built largely by AI coding agents under that direction**. A selected bibliography yielded a smaller accessible corpus, rich extraction records, and frozen working commitments. Models proposed targets and inference steps; the engine checked licenses and searched both polarities. Iteration repaired extraction loss, construction limits, provider isolation, trivial closure, vocabulary mismatch, and short or unsupported writing. A later gap pilot correctly refused altered identifiers at alignment candidate 36/150. Recovery reused finished construction, froze 160 commitments with no unresolved alignments, then refused the first L3 target request at admission. Offline context packing fit the configured bound; the packed/unpacked fork comparison remains pending. Formal success repeatedly exceeded substantive success: closed routes could restate sources, package conjunctions, or depend on only one paper. Later literature checks narrowed an apparent gap to a partially anticipated connection whose exact derivation was not found within the stated search scope. Later sampled audits exposed nondeterminism, and two native exports lost all citations. No substantive novel contribution is established so far; a qualifying cross-paper pilot, citation repair, and L3 novelty dossier remain pending. Costs, tokens, human decisions, and missing accounting are reported separately rather than inferred from successful execution.

## 1. Scope, authorship, and evidence

The human chose the research area, supplied the initial literature collection, directed the scaffold, approved budgets and provider changes, set acceptance criteria, and selected routes and subsequent research priorities. Coding agents investigated, implemented, tested, reviewed, and operated the scaffold. Generation inside ARA occurred through separately isolated provider calls. These are different roles: evidence that an ARA call excluded host context does not establish that development workers lacked that context. The operating rule prohibited the human from supplying original philosophical arguments, premises, distinctions, or a personal view. This report documents the recorded actions; it does not independently certify competition compliance. [R1–R3]

The correspondence snapshot contains **29 timestamped entries recording human actions**, including approvals reported indirectly by the coordinating agent. Appendix A lists every such entry. The brief also records earlier human design and bibliography preparation without timestamps. Those activities are disclosed, but no time is invented for them. Native event labels such as `HUMAN` mark command/input boundaries; workers also used those boundaries. They are therefore not a count of distinct human interventions or human labor. [R1, R2]

Evidence is versioned. At the original report’s checkpoint, the observed main revision was `80a3448`; the principal numerical ledger is the frozen fork-6 report, whose last local event is on 28 October. Later writer, publication, literature, and local-branch reports are explicitly identified as supplements. Version 2 preserved gap pilot 1 at `0a31afb` and the round-4 typed-audit table. Version 3 adds recovery at `4cefe35`, the offline context-packing plans at `c99c6b3`, writer rounds 5–6, and four independent reviews. Three later human-action entries extend Appendix A to 29. Findings and closures are tied to their reviewed heads; no global integrated-head verdict is inferred. We do not splice their successful stages into a fictional completed run. In particular, the later acquisition of **54 PDFs** did not retroactively enlarge the frozen evidence used by the reported pilots. [R4–R8]

Every figure has its numerical input and source pointers in `data.json` and `figures/manifest.json`. The data also contains source-file hashes, the anonymised correspondence snapshot, model-receipt accounting components, prompt hashes, and gate dispositions. The companion `prompts.md` supplies recorded instruction variants without reproducing source-paper passages. Raw logs retain full prompts and responses in the private evidence workspace; they are not anonymously publishable by default.

## 2. What ARA is

ARA separates **L**, the versioned bank of permitted move forms; **T**, the working table of source-linked commitments; and **H**, model-proposed cuts or hypotheses. A model is not allowed to create a license by asserting that a step is plausible. A step must instantiate an existing bank entry. Deductive entries require both shape checks and Z3 entailment. Defeasible entries require the relevant scheme and its critical questions; a failed or unsupported critical question leaves an obligation open. [R3]

Rich extraction records are immutable source evidence. A construction lifecycle selects a bounded working subset, formalizes it, records source stance and omitted support, and then freezes T. Search uses that freeze. A verified fork copies the frozen prefix and provenance, proposes new targets, and uses a separate cache. It reuses premises, not statistical independence. Reported or attacked source positions are not silently converted into endorsed premises. [R3, R4]

{{fig:architecture}}

For each target, ARA searches both the target and its negation. The engine records proposed, licensed, discarded, and unresolved moves. A closed route means the engine’s formal obligations were met under that version’s policy. It does not establish that a source was faithfully translated, its premises are true, the result is new to the literature, or its prose is good philosophy.

Originality was pursued through several independent checks: avoiding direct restatement of T, testing single-support entailment and tautologies, classifying whether the target states an own thesis, checking the relation between its text and formal definition, requiring distinct source supports, and later comparing with retrieved literature. The gate design changed substantially. Its defects are part of the method’s history, not evidence of an invariant guarantee. [R9–R11]

## 3. The pipeline actually run

### 3.1 Literature and extraction

The initial bibliography contained **53 works**, dated **1967–2024**. Only **four** were from **2020 onward**, and none was later than **2024**. The first acquisition pass obtained **26 PDFs**, leaving **27** originals requiring access elsewhere. The accessible subset covered **1996–2024**, with **three** works from **2020 onward**. Intake accepted all bibliographic entries, but bibliographic intake was not full-text extraction. [R2, R5]

The first small-summary design was rejected because a **four-item, 400-character** cap could not preserve argument structure. Rich extraction instead retained page-linked premises, intermediate conclusions, inferences, distinctions, qualifications, and reported or attacked positions. The complete original-corpus pass produced **5,659 items** in **26 nonempty graphs**. Of those items, **363** were quarantined: **312 directly** and **51 because of dependencies**. **5,296** remained eligible. **Nineteen** graphs were classified as extracted and **seven** as partial; **57** snapshot-scoped extraction gaps remained. These gaps concern source processing and must not be confused with open research problems. [R1, R12]

The later acquisition and currency audit added **28 full texts**: **25 modern selections** and **three** missing originals. The local collection therefore reached **54 PDFs**. The modern search recorded **44 candidates**; **19** modern selections and **24** originals remained unavailable, yielding **43 acquisition requests**. Access failure is a limit on the review, not evidence that a problem is open. Newly obtained texts were not part of the frozen pilot evidence at the supplement’s checkpoint. [R5]

### 3.2 Construction, search, and route selection

Construction reduced eligible source material to a bounded T. The reused pilot-5 freeze contained **169 commitments from 22 papers**, including **16 conditionals** and **151 distinct symbol signatures**. Its stance inventory was **150 endorsed, six reported, and 13 attacked** commitments. Aggregate symbol reuse initially looked encouraging, but **zero** exact symbol signatures crossed paper boundaries. That distinction explains why a large source inventory could still offer little cross-paper inference. [R6]

{{fig:funnel}}

Pilot 5 retained **seven targets**, completed **14 polarity searches**, and published **14 routes**. Four received the then-current `CLOSED-derived` label, but substantive review found only conjunction packaging. Later forks reused its freeze. Fork 3 retained **three targets**, completed **six searches**, and obtained **two derived closed routes** plus **four open routes**. Both closed routes used the same single source paper. The operator subsequently selected those available derived routes for writing while also requesting a real literature-gap investigation. [R1, R6, R9]

Fork 6 pursued gap-driven targets. It searched **ten targets**, **six** labelled gap-resolution, and completed **20 polarity searches**. All **20** routes were open; **18** were bare unresolved roots. Of **nine** critical-question calls, **two** returned supported and **seven** unsupported. Thus retrieval of relevant T material did not establish the connecting premises. One additional target passed its pool but was omitted by the outer target cap. The request to build all passing routes was not fully achieved. [R4]

### 3.3 Writing, audit, verification, and polish

The initial whole-essay writer produced **eight attempts** across the selected routes, all below the then-configured **4,500-word** minimum; their range was **1,590–4,376 words**. No audit was reached. A sectioned writer then used an outline with section budgets, deterministic assembly, and targeted expansion. Its first length-successful draft reached **4,642 words**, but failed audit on **four sentences**. A repaired **4,604-word** draft passed a subsequent native audit, then stopped before external evidence retrieval. [R1, R7]

Later evidence changes the interpretation of that pass. A new binary audit flagged **101** sentences in the same previously accepted draft. Typed auditing distinguished source claims, argument steps, framing, objections, and unsupported claims. In the later recorded comparison, route 1 began with **75/245** flags and route 2 with **25/245**. Repairs yielded **4,714-word** and **4,619-word** drafts with zero flags in their final pre-verification audits. Both native runs nevertheless stopped at `search_evidence` with `cli_tool_event`. An isolated web diagnostic succeeded, but neither native lifecycle produced accepted retrieval evidence, citation/originality classification, the final audit, or an essay export. **Verified native exports remained zero at the round-4 checkpoint.** [R7]

**Table 1. Round-4 typed pre-verification audit, reproduced from the writer’s receipt.** “Audit passed” does not mean that retrieval, citation/originality verification, or export passed. [R7]

| Route / stage | Native words | Flags / sentences | Outcome |
| --- | ---: | ---: | --- |
| Route 1 imported draft | 4,604 | 75/245 | Revision required |
| Route 1 accepted repair 1 | 4,714 | 0/245 | Pre-verification audit passed |
| Route 2 imported draft | 4,638 | 25/245 | Revision required |
| Route 2 accepted repair 1 | 4,525 | 74/244 | Revision required |
| Route 2 accepted repair 2 | 4,619 | 0/244 | Pre-verification audit passed |

The increase from **25 to 74 flags** on route 2 shows why these labels should not be read as a stable quality score. Native word counts include machine markers. Excluding both node and citation markers, the final drafts contain **4,578** and **4,498 words** respectively; route 2 is two words below the then-configured **4,500-word** floor under that stricter count. Neither round-4 draft was a verified export. Nu4 r5 was pending at the version-2 checkpoint; its later completion and round-6 limitations are reported below. This historical table is unchanged. [R7, R17, R20]

A separate publication branch polished the preserved earlier route-1 draft through isolated Claude Opus calls. It produced a **4,743-word**, **12-page** PDF with **two deterministic figures**. Its native audit covered all route nodes and its exact T-citation membership check passed. External verification remained blocked on that branch. This polished artifact is evidence of successful prose and rendering work on one selected route; it is not the L3 gap paper and is not proof of a verified competition entry. [R8]

### 3.3.1 Later writer rounds: unstable audits and citation-free exports

Round 5 (`0368a17`) identified the refused event as `item.completed → web_search → action.type=other` and permitted that exact native web event only in `search_evidence`. Both routes then completed native export with originality labelled `possible_overlap`. That label is not a novelty pass. After quotation cleanup, route 1 received **44 flags**, then **zero** on a byte-identical cleaned-input prompt without a text repair. Route 2 changed from **eight to six flags** before substantive repair. Final audits could replay an accepted cache sample without reconciling the adverse verdict. These observations show audit nondeterminism, not measured error rates or evidence that the clean sample was correct. [R20, R22]

Round 6 (`d9ac619`) introduced a **k=3 union gate**: fresh requests bypass the response cache, and any current or valid prior same-prompt adverse flag remains binding. It is neither majority voting nor a claim of statistically independent samples. Repairs address the union and return through verification and fresh audit. The exact final-stage batches were: [R20]

| Route / batch | Flags per sample | Prior adverse | Union | Unanimous / sentences | Verdict |
| --- | --- | ---: | ---: | --- | --- |
| 1 / 1 | 0, 0, 36 | 44 | 47 | 209/245 | reject |
| 1 / 2 | 41, 52, 42 | none | 53 | 234/246 | reject |
| 1 / 3 | 0, 0, 0 | none | 0 | 245/245 | accept |
| 2 / 1 | 30, 0, 0 | none | 30 | 214/244 | reject |
| 2 / 2 | 2, 0, 5 | none | 6 | 238/244 | reject |
| 2 / 3 | 1, 15, 1 | none | 15 | 230/244 | reject |
| 2 / 4 | 0, 0, 0 | none | 0 | 244/244 | accept |

Unanimity counts agreement in binary votes; unanimous adverse votes still reject. Route 1 used **10 actual fresh audit calls** for **nine valid final-batch samples**; route 2 used **13 calls** for **12 samples**. Initial audits and bounded schema correction explain the difference. The first route-1 batch retained the earlier 44-flag result despite two clean samples. Complete valid adverse history therefore worked; the incomplete-history loophole later found by review remains pending repair (§4.8). [R20, R23]

Both round-6 lifecycles exported, but **each final bibliography had zero entries and each body had zero citation markers**. Native word counts were **5,387 / 4,413**, or **5,336 / 4,385** without machine markers. Both originality verdicts remained `possible_overlap`. External verification had removed the local source citations; subsequent clean audits did not restore them. These are native exports, not submission-ready essays or proof of source fidelity. Route 1 ran before a later cleanup-length/resume-budget correction; route 2 used the corrected source. The report preserves that source-version distinction rather than claiming both ran at the final committed head. [R20]

**Citation repair is pending in R7.** The requested fix verifies frozen-T references against local full text and page evidence first, uses web search as supplementary evidence, and refuses an export whose source claims lack citation coverage. It also must preserve valid adverse evidence from incomplete audit inventories. Publication's separate default floor is **3,000 words**, distinct from the historical writer construction target of **4,500** and the **6,000-word** ceiling. Native counters and marker-free counts must not be interchanged. [R20, R22, R23]

### 3.4 Gap pilot 1: completed construction, then an alignment stop

The fresh gap pilot ran at detached revision `0a31afb`. It completed **74 construction windows: 53 accepted and 21 skipped**, retaining **159 working commitments from 22 of 26 papers**. These were pre-alignment artifacts. **There was no frozen T**, so the frozen-coverage criterion was not met even though the working set represented enough papers numerically. The supervisor exited with status **2** at **13:36:58 UTC on 29 October**, after **16,340.66 seconds**. [R16]

Alignment stopped at candidate **36 of 150**. It had accepted **35 judgments**: **34 unrelated** and **one right-to-left entailment**. The next candidate received **three invalid replies**, each changing the immutable symbol-ID fragment `r27_39` to `r27-39`. The responses called the relation unrelated, but their changed reference violated the exact-reference contract. **The validator correctly refused them.** The model text was not silently normalized and the working set was not promoted into a freeze. No bridges or canonical rewrites were applied; the final consistency phase was never reached. [R16]

The free `resume-construction --plan-only` check also refused: “construction resume requires a terminal window refusal.” Construction had already finished, and that revision had no alignment-resume entrypoint. Starting a new run with retained cache was the documented alternative; it would replay construction and could make new calls. That alternative was not executed as an in-place recovery. **Targets, forward synthesis, routes, writing, and an L3 resolution were never reached.** A rendering pass over an empty route inventory is not evidence of route-summary quality. [R16]

Coverage and semantic limits survived the completed construction stage. Skipped windows included capacity/empty-closure losses, a no-root selection, lexical attribution false positives, and provenance/schema refusals. The sole accepted entailment judgment was disputed on source review and involved an attacked description, not an endorsed safety–retraction bridge. Several original L3 anchors did not survive construction; a surviving retraction-related statement could not silently replace the full retraction rule. Four conflict inputs also lacked bindings because their required source contributed no commitment. These were qualified draft inputs, never admitted frozen gaps. [R16]

Independent review of this exact revision also retained blocking **INTEG-F1**: irrelevant fresh-atom wrappers could package existing cross-paper facts and receive a native derived label. This defect was independent of the earlier identifier stop. The pilot generated no target or route on which to test it; an empty padding-review inventory does not clear the defect. L3 therefore remains partially anticipated, with no resolution established by this pilot. [R16]

### 3.5 Gap1r: recovery reached freeze, then target admission stopped

At `4cefe35`, recovery restored all **74 construction windows**, **159 source commitments**, and **35 accepted legacy judgments**. It completed **115 pending pairs** without replaying construction: **150/150 accepted judgments**, comprising **149 unrelated** and **one right-to-left entailment**, with **zero unresolved**. Applying the one model-alignment bridge produced **frozen T = 160 (159 source + 1 bridge)** across **22/26 papers**, with no canonical rewrites. This is executed continuation evidence, not merely a repair brief. The source inventory retained **134 endorsed, 10 reported, and 15 attacked** commitments. The inherited bridge remains semantically disputed; accepting its receipt did not establish a safety–retraction inference. [R18]

The actual frozen union was satisfiable, so the inconsistent-union failure R28-F2 did **not** occur in this pilot. Six external gaps bound successfully. A new semantic pass classified **60 pairs: 35 compatible, 22 unrelated, three in tension**. Together with three source-level open-problem records, the three tensions and six external records produced **12 hypotheses**. These are not twelve established open problems. Source review found stance reversal in one supposed tension, distinct consequence notions conflated in another, and historically open questions treated as current. Four other comparisons remained unbound because their source supplied no commitment. Missing L3 rule anchors persisted. [R18]

Forward synthesis reached its **depth-2 / 500-consequence cap**, reported truncation, and returned **two leads**. Both were conjunction packaging, with **zero substantive contributions**, despite the native `per_paper_new_assertion` label. Neither supplied a retraction premise. A cited warning against an inference also had an incomplete page span and a misleading positive formula; the frozen record was not silently repaired. These are observed forward-lead false positives, not executed target-admission or selectable-route results. [R18]

The first L3 target request was then refused **before dispatch**: **311,785 estimated input + 16,384 output allowance = 328,169**, against a **200,000** bound. Thus “312k > 200k” describes the input estimate alone; admission counted the larger total. **No target call, target, route, selection, or L3 resolution occurred.** A prior readiness check estimated only **51,998 input tokens** and did not represent the full target request. The full prompt was **627,750 UTF-8 bytes**, including **332,316 bytes** of provenance. The stopped request incurred no generation spend. Recovery's supervisor elapsed time was **13,773.98 seconds**, ending with status **2**. [R18]

## 4. Iteration: failures, fixes, and mistakes

{{fig:iterations}}

### 4.1 Extraction structure and source retention

The small-summary cap was a design mistake against the stated aim of preserving arguments. Rich extraction removed that cap, but strict output contracts then rejected useful material. A cheaper Sonnet extraction produced malformed inference structure; a subsequent retry reduced a partial paper to **nine items**, compared with **108** from the Opus extraction. The cheaper path did not pass the richness test. The first complete-corpus attempts also stopped on reversed page ranges, missing inference dispositions, duplicate correction IDs, and reconciliation failures. [R1]

The repairs separated deterministic wire repair from invented source content, added bounded corrections, allowed disclosed reconstruction or a no-inference disposition, and retained accepted ranges through best-effort reconciliation. Shape validation alone had admitted placeholder-like junk: a later grounding pass quarantined **245 of 2,333** items in an intermediate corpus. Union publication repaired source loss across resumed snapshots. The final quarantine inventory remained visible rather than being deleted to improve a success count. [R1, R12]

OCR was tried on **82 affected pages**. Successive diagnostics reported **22** recovered pages under the first metric, then **15** under revised whole-page rules. Span-level repair recovered **131 of 677** damaged spans, with only **nine of 82** pages clean. These are different metrics, not a monotone improvement curve. Review found confidence dilution and required a further fix. OCR availability did not establish complete source recovery. [R1]

### 4.2 Construction capacity

The first rich build dropped **40 dependencies**, so no freeze was accepted. Later construction could not fit whole-paper provenance into a window: one singleton input was approximately **86,000 tokens** against a **70,000-token** batch limit. Filtering metadata to the selected window repaired that particular cause, but further refusals exposed the absence of a global plan. [R1]

The coordinator then justified a lower symbol-growth allowance using a claimed **70–90 tokens per commitment**. That claim was wrong. The pilot worker corrected the observed symbol cost to approximately **233 tokens per commitment**. The report retains the error and its correction. Bounded closure, disclosed support cuts, global working/catalogue budgets, and soft per-window shares replaced successive cap increases. An intermediate run had stopped at **802 tokens against an 800-token share**, despite remaining global capacity; the corrected policy allowed borrowing within the global bound. [R1]

### 4.3 Providers, credit, and isolation

API construction stopped with opaque request failures, then a count-endpoint diagnostic identified insufficient credit. The earlier request failure was suspected to have the same cause, but that retrospective attribution was not proven. A subscription route was then implemented. Its first strict isolation probe failed because built-in context, hooks, and identity-related material remained. The revised contract excluded operator content and customizations while disclosing unavoidable vendor context. Output and decoded-string scans, fresh sessions, bounded retries, and canaries were reviewed repeatedly. [R1, R13]

Subscription capacity was also misestimated. A calibration comparison of aggregate usage with initial context inflated a factor from **0.553 to 1.424**, leaving **58 of 70** windows skipped in the first Claude pilot. Like-for-like accounting and a local rather than inherited token cap repaired the comparison. A later **401** after host authentication refresh exposed stale in-memory credentials; per-call credential reads and one bounded re-read retry addressed it. These repairs did not prove that future provider behavior would remain stable. [R1, R13]

### 4.4 Structure, cross-paper vocabulary, and triviality

A resumed Codex pilot completed **20 searches** but returned only open routes. Diagnosis found **16 of 22** proposed steps with conclusion mismatch, a T of **166 standalone atoms**, and no target-symbol overlap. Structured source inferences, frozen-catalogue guidance, goal binding, joint slot formalization, and reference checks repaired concrete causes of empty search. The next pilot obtained closed routes, but they were depth-zero restatements of individual commitments. [R1, R10]

Own-thesis classification then became entangled with attribution: content definitions saying that an author held a claim made the classifier reject useful own-voice targets as reports. Content-only definitions plus separate stance/provenance repaired that representation. A subsequent lexical filter still rejected ordinary words such as “claims” or “states” in substantive content. Fork 2’s review identified **eight lexical-only exclusions**. The lexical screen became advisory; exact report frames remained hard failures. [R9]

The whole-T novelty gate was another substantive design error. Requiring that the union of T not entail a target prevents deductive synthesis across papers, even when no single paper entails it. The corrected local policy allows union entailment and tests each paper’s endorsed closure separately, while retaining anti-padding, stance, fidelity, and support checks. The placeholder regression combines P from one paper with P → Q from another and derives Q. This demonstrates the corrected mechanism, not a real literature result. The final bounded real-freeze census, at depth **two** and a **500-consequence cap**, found **zero qualifying candidates**. An earlier six-candidate census was superseded after a packaging defect was fixed. Cross-paper symbol alignment was still a separate integration boundary. [R11]

### 4.5 Writing and audit

Repeated whole-draft retries did not supply actionable length feedback. Section budgets and append-only expansion preserved accepted material while filling deficits. Citation splitting, identity screening on resumed drafts, and revision-marker handling also required repair. Typed auditing improved the distinction between exposition and unsupported argument, but audit judgments varied markedly across runs. A zero-flag model judgment is evidence about that invocation, not an independent semantic proof. The retained adverse judgments and the final retrieval failures remain part of the record. [R7]

### 4.6 Coordination and reporting

The coordinating agent acknowledged an idle period from **12:33:41 to 16:49:21 UTC on 28 October**, or **4 hours 15 minutes 40 seconds**. It waited for a go/no-go decision instead of starting an already available alternative in parallel. Earlier, its instruction to stop at “any cap” caused a worker to interrupt an extraction pass after a best-effort reconciliation refusal; that was a briefing error, not evidence that the corpus could not be processed. [R1]

Reporting itself needed repair. A **3.7 GB** HTML report crashed Chromium; a later sidecar-based report was approximately **2.45 MB**. Fork 6’s native report rendered on desktop but retained **19 pixels** of mobile overflow. Its event-origin index also mislabelled **15,663** inherited-prefix occurrences; a separate overlay corrected attribution without altering native report bytes. The main accounting deduplicates receipts, so imported lineage must not be summed as new spend. These defects concern the original run reports; this metapaper has its own rendering checks. [R1, R4]

### 4.7 Alignment design lesson and completed recovery

The identifier validator was right to refuse gap1's altered reference. The avoidable design error was asking a model to echo an immutable ID, letting one item's bounded failure abort the run, and offering no continuation from finished construction. Sigma r12 moved identity binding into the host-owned candidate record, requested relation/reason only, recorded per-item unresolved outcomes under a declared threshold, and added alignment continuation. Gap1r exercised that continuation with zero unresolved outcomes. Recovery preserves stage receipts; it does not certify the semantics of the retained bridge. [R17, R18, R21]

Sigma r12 and nu4 r5 were pending in version 2 and have results in version 3. Current pending work is the A/B fork comparison, R7 citation/adverse-history repairs, sigma r14's stage-window and integration-control repairs, and the L3 novelty dossier. A requested fix or an uncommitted diagnostic is not credited as a completed result. [R19–R25]

### 4.8 Independent review findings ledger

The ledger records findings at the reviewed head and later evidence of closure. Passing scoped tests did not imply that no blockers remained. All cited reviewer reproductions were offline; synthetic identity/credential sentinels were used, with no claim of a real disclosure. [R21–R24]

| Finding | Reproduced failure | Disposition at this checkpoint |
| --- | --- | --- |
| **S12-F1 (P2)** | Old integration fixture echoed left/right IDs; new schema correctly refused. Combined tests 52/53. | Closed in Xi 0c4d472; s13 owning regression confirms. [R21] |
| **NP-F1 (P1)** | Imported publication drafts reached logs/fallback before sensitive-content screening; synthetic offline probes. | Closed for publication at Pi a6a2f9b; r2 independently reproduced refusal before effects. [R22, R23] |
| **NP-F2 (P2)** | Repaired current title was absent from audit input and cache identity. | Closed for publication at Pi a6a2f9b; r2 confirms title coverage and invalidation. [R22, R23] |
| **NP-F3 (P2)** | Substring matching authorized edits to a duplicate unflagged occurrence. | Closed at Pi a6a2f9b; r2 confirms occurrence-bound permission. [R22, R23] |
| **R2-F1 (P1)** | Invalid/incomplete audit history discarded valid adverse labels; three clean samples exported unchanged text with zero repairs. | Pending R7: preserve valid flags or unresolved blocking obligation. [R23] |
| **R2-F2 (P1)** | Exact frozen-local citations were sent to external verification; unverified deleted bibliography 2→0 and markers 2→0. | Pending R7: local-source verification and final citation coverage refusal. [R23] |
| **S13-F2 (P1)** | Stage window 272000 with run window 872000 admitted 587839 using run bound 839232, above effective stage bound 239232. | Pending sigma r14; run-level-only workaround is not closure. [R24] |
| **S13-F1 (P2)** | Merged full-T mutation anchor missing: 680/681 resolve despite 59/59 combined tests. | Pending integration repair; in-memory adapted control diagnostic is not an applied fix. [R24] |

The s12 review passed **233/233** Sigma tests and **44 controls**, but the combined fixture failed (**52/53**); three additive merge conflicts also needed resolution. The later Xi `0c4d472` integration and s13 review close S12-F1. No production identity-binding or resume bypass was reproduced in s12. [R21, R24]

The np review passed **373/374 collected tests** with one paid-provider skip and **62 scoped controls**, yet independent probes found NP-F1–F3. It also recorded audit instability (NP-N1), distinct publication/writer length policies (NP-N2), and limited offline/semantic evidence (NP-N3). The r2 review passed **429/430 collected tests**, one paid-provider skip, and **82 controls**. It independently closed the three Pi publication findings at `a6a2f9b`, while retaining two Nu4 blockers at `d9ac619`. Closure of those Pi defects does not establish successful polish, source fidelity, or a stable semantic audit. [R22, R23]

R2-F1 is narrower than failure of the whole union design: complete adverse history remains binding. A partial inventory, duplicate sentence, or unknown node can instead make the entire historical response unusable, dropping its valid adverse flag. Three clean samples then export the unchanged draft with **zero repairs**. Refusing the first malformed call is insufficient if resume discards the obligation it discovered. [R23]

The s13 review passed **410/410 scoped tests** across Sigma and a synthetic combined tree, plus **13 scoped controls**. Its runtime reproduction nonetheless dispatched **555,071 input + 32,768 output = 587,839** tokens to a fake provider using a **272,000** stage window, because admission retained the run's **839,232** bound. The effective stage bound was **239,232**. Clearing the stage override also reproduced the configuration split; a uniform run-level window refused correctly. The workaround is to use a run-level window only while the repair remains pending. The merged full-T mutation anchor also remained broken: an adapted in-memory diagnostic went red/green, but that adaptation was not an applied closure. No live service acceptance is inferred from these offline checks. [R24]

## 5. Gates, rejection, and candidate selection

The operator-approved acceptable pilot required a clean native selection boundary, source coverage of at least **20 of 26 papers**, at least **three** genuinely derived routes, and readable summaries/reporting. Each qualifying route had to state a novel own thesis, avoid single-commitment entailment, use at least **two distinct supports from two papers**, respect stance, and contain a licensed inference. Pilot 5 met the clean-run, coverage, and rendering requirements but failed the substantive-route requirement. A native label alone did not satisfy the criterion. [R1, R6]

{{fig:gates}}

The chart counts candidate-attempt incidences under the recorded gate reason. Reasons can overlap. In fork 1, an attribution screen and the own-thesis classifier could both reject a candidate; adding the columns would overcount rejected candidates. Later pool receipts record an explicit retained/rejected disposition. The figure preserves this difference rather than treating all generations as a controlled, identical experiment. Exact rows and event hashes are in the data supplement.

The gates caught several real defects: single-premise restatements, unused-antecedent conditionals, Boolean packaging, renamed assertions, ornamental proof steps, and unsupported gap-resolution labels. They also created false positives and exclusions: attribution vocabulary, an order-dependent paper count, stance-blind support slicing, a duplicate target identifier, and the outer target cap. Passing all gates was necessary under a given policy but never sufficient for literature novelty. [R4, R9–R11]

{{fig:routes}}

The operator selected the two available fork-3 derived routes only after their single-paper limitation was reported. Those routes supplied writing experiments. The later L3 priority was a separate research direction, not a retroactive claim that the selected routes had already resolved that gap. No successful cross-paper pilot is established by the evidence covered here.

## 6. Gap discovery and the literature currency check

The initial gap detector found **three source-level open-problem flags**. It did not establish that those problems were still open in the current literature. The follow-up checked the source context, later literature, and proposed resolution theses. Its verdict was **one addressed, two partially addressed, and zero certified still open**. [R4, R5]

| Flag | What the system treated as unresolved | What the currency check found |
| --- | --- | --- |
| G1 | Whether disagreement motivates a relativist account and where the effect belongs | Later theories and experiments address the comparison. Remaining disagreement does not certify an untouched problem. |
| G2 | Nested probability and the interpretation of a particular reply pattern | Later formal/pragmatic models and experiments address the mechanism. The exact remaining scope was only partially settled by the accessible material. |
| G3 | An older absence-of-model or absence-of-diagnostic claim | MacFarlane’s later models and fixed-use/retraction diagnostics address that claim. Relevant works were already in the original accessible corpus. |

L3 emerged from the failed search for connecting premises and a targeted bridge-literature investigation: could worldly-information safety support an assessment-sensitive retraction obligation? The initial acquisition report classified the link as unknown. The deeper check revised it to **partial**. The safety anchor already discusses retraction and assessor information; Dinges’s later work connects estimates of epistemic qualities, including safety, to retraction while allowing a rival semantic interpretation. These are substantive anticipations. The accessible texts did not establish the specific safety-to-retraction derivation sought by ARA. [R5]

The focused search covered **2018–2026** and retrieved indexed first-generation citation sets, including **11** works citing the safety anchor, **116** citing the earlier assessment-sensitive account, and **449** citing the later book. Those counts describe retrieved index records, not papers all read in full. The index omitted an actual book citation found in a read PDF, demonstrating that absence from a citation graph is unreliable negative evidence. Two especially relevant modern comparisons remained inaccessible. [R5]

A separate live semantic-conflict pass classified **60 pairs**: **three contradictory**, **seven in tension**, **35 compatible**, and **15 unrelated**. Source/currency review of the ten flagged pairs yielded **nine partial** and **one unknown**, with none certified still open. L3 was omitted by that bounded top-pair retrieval and was investigated separately. The operator approved the restrained framing **“not found within stated search scope, partially anticipated.”** That framing is retained here. It is not a claim that ARA resolved L3 or established priority. [R1, R14]

## 7. Models, prompts, providers, and isolation

| Role in the recorded work | Model / version evidence | Limit |
| --- | --- | --- |
| API extraction and early construction | Receipts identify `claude-opus-5`; early cheaper-model experiments requested `claude-sonnet-5-5` | API ledger scope below excludes some early experiments. No underlying weight revision beyond reported identifiers is available. |
| Subscription construction/search | `claude-opus-5-5`, Claude Code `2.1.306` | Vendor runtime context remains; effective prompts differ from direct API prompts. |
| Codex pilots and writing | Requested `gpt-6-luna`, `codex-cli 0.163.0` | Serving identity was recorded as `unverified` when omitted by CLI output. A requested pin is not a serving receipt. |
| Publication-only polish | `claude-opus-5-5`, Claude Code `2.1.306` | Separately authorized polish, not authorization to resume Claude pilots. |
| Scaffold coding, orchestration, this report | Agent roles recorded in briefs/correspondence | A complete per-worker model/version and token ledger is unavailable in the supplied sources. No exact model identity is inferred from a role name. |

The API-to-Claude switch followed the credit failure and the human request for an agent route. The Claude-to-Codex switch followed the operator’s clarification that “chat” meant ChatGPT/Codex; the active Claude pilot was halted. Later, the operator explicitly prohibited further API credit use and authorized ordinary agent calls by default, with Claude Opus reserved for the requested final polish. These were human choices, not automatic provider fallback. [R1, R13]

The Claude canary and review established the recorded configuration’s suppression of operator customizations and identity output. They did not establish absence of vendor built-ins or byte-identical API context. Subsequent reviews caught escaped-output leakage and unsafe diagnostic text; allowlisted diagnostics replaced free-text retention. Codex used fresh processes, temporary configuration, isolated host homes/process state, disabled project instructions, skills, memory, and external tools, plus a context canary. Generic built-in tool definitions could still be visible; actual tool events rejected the response. Strict-schema projection required its own preflight. Isolation evidence is specific to the tested transport/version and threat model, not proof against all contamination. It does not erase pretrained model knowledge or establish that every generated idea came only from the supplied papers. [R13]

The later web-evidence transport deliberately differed from the earlier tool-free transport. Round 4 rejected an unidentified native event; round 5 diagnosed the specific web-search event and narrowly permitted it for `search_evidence`. Subsequent native exports are recorded in §3.3.1, together with their citation loss. That repair did not authorize other tool events. [R7, R20]

### 7.1 Context window: client configuration, request size, and pending forks

Gap1f was **not launched**. Inspection of the pinned `codex-cli 0.163.0` metadata for requested `gpt-6-luna` found a **272,000 default** and **872,000 maximum** context window. These are client metadata, not verified serving capacity or a served-model identity. The old isolated adapter ignored user configuration and did not pass `model_context_window`. Raising ARA's admission limit alone therefore did not enable the larger provider window. The operator authorized loosening the limit at **19:09:07 UTC**. [R1, R19]

Sigma r13 (`c99c6b3`) added explicit window forwarding, including the canary, and gap-scoped target packing. Its **one-hop** plan retained **three full and 157 compact commitments**, **all IDs/formulas**, **147 symbols**, and **11/150 alignment judgments**, explicitly recording the other judgments as projected. Full frozen T remains authoritative for the downstream gates. The packed prompt measured **204,567 bytes**; its **122,108-token** total is an offline admission estimate, not measured service usage or a fork result. [R19]

| Saved request / configuration | Input estimate | Output allowance | Total / bound | Evidence |
| --- | ---: | ---: | --- | --- |
| Historical unpacked L3 | 311,785 | 16,384 | 328,169 / 200,000 | Refused before dispatch |
| Packed; original bound | 105,724 | 16,384 | 122,108 / 200,000 | Offline plan fits |
| Packed; explicit 272k window | 105,724 | 16,384 | 122,108 / 239,232 | Offline plan fits |
| Unpacked current template; 872k window | 312,084 | 16,384 | 328,468 / 839,232 | Offline plan fits |
| Packed; explicit 872k window | 105,724 | 16,384 | 122,108 / 839,232 | Offline plan fits |

The current unpacked template is **299 tokens** larger than the historically refused one. The derived bound subtracts twice the configured **8,192-token** target output allowance and a **16,384-token** margin from the selected window; admission also includes the request's output reservation. These conservative estimates are not additive field-token measurements. Offline forwarding tests do not establish live larger-window acceptance, and the per-stage mismatch in S13-F2 prevents a blanket correctness claim. [R19, R24]

{{fig:context-admission}}

The requested comparison forks are **A: packed with hops=2** and **B: unpacked with a raised run-level window (600,000 proposed)**. Their target counts, routes, substantive contributions, L3 verdicts, and quality comparison are **pending**. A's actual full-row count is also pending: the three-full/157-compact, 122,108-token result above belongs to the **one-hop offline plan**, not fork A. [R19]

### 7.2 Prompt disclosure

Stage prompts are topic-neutral templates combined at runtime with source text, the frozen catalogue, target/route state, explicit schemas, and correction feedback. Full prompt and response receipts were retained. Worker briefs separately specified implementation tasks, budgets, permitted providers, stop conditions, and expected evidence. They directed scaffold development; they were not all passed verbatim to philosophical generation calls. [R2, R3, R15]

Representative recorded instructions included:

- Extraction: “Preserve the paper’s argument structure” and “Do not reduce this to a fixed number of central claims.”
- Construction: a selected source inference must become a content conditional using the exact endpoint formulas, rather than a new standalone atom.
- Target proposal: assert a thesis in the system’s own voice; preserve frozen meanings; do not invent support to fill the requested pool.
- Search: instantiate the supplied bank and answer critical questions from available evidence. The engine retains licensing authority.
- Writing: compose from the selected route and source context, preserve citations and node coverage, and meet explicit length bounds.
- Publication: improve presentation without adding claims, preserve citation/marker sequences, then run the native audit again.

The quoted extraction sentences are short instruction excerpts, not literature quotations. The other entries are functional descriptions. `prompts.md` supplies the exact recorded instruction prefixes and their digests, including successive variants. Current source templates alone would be insufficient to reproduce earlier runs because gates, correction messages, schemas, effective provider instructions, and runtime inputs changed. Exact raw prompts remain privately recoverable through the event hashes. [R15]

## 8. Time, tokens, and cost

### 8.1 Accounting boundary

The principal ledger is `reports/overnight/fork6/accounting.json`. Its report covers **67 lineage runs** and deduplicates identical event receipts across copied prefixes and imports. We reaggregated its MODEL receipts by provider and stage and checked equality with its measured, unknown-at-reservation, and token totals. Per-run totals must not be added: many include the same extraction and freeze history. [R4]

This is a measured lineage subtotal, **not total campaign cost**. It excludes some early smoke/development work, later writer/publication branches, coding and review-agent conversations, the orchestration conversation, and production of this metapaper. The early smoke receipt separately reports **$7.059330**. The initial development record also retained unknown usage reservations. No reconciled global invoice or subscription fee allocation is present, so no all-in dollar total is asserted. [R1, R4]

{{fig:api-cost}}

The ledger contains **4,534 measured MODEL receipts** and **12 unknown-at-reservation receipts**. MODEL receipts include cache replays and validation/preflight work; these counts are not unique uncached generation calls. Recorded measured usage totals **113,530,631 tokens**, including the separate cache components. Unknown usage contributes **1,700,600 reserved tokens**, not measured consumption. API measured USD is **$131.785270**; the **$1.844820** unknown reservation makes the budget-accounted sum **$133.630090**. A failed response with no usage receipt does not become measured because it was budgeted. [R4]

| Provider scope | Input | Output | Cache read | Cache write | Unknown reserved tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
| Anthropic API | 11,314,239 | 3,008,563 | 0 | 0 | 175,424 |
| Claude Code subscription | 4,012 | 1,972,083 | 5,762,812 | 49,414,935 | 661,810 |
| Codex CLI subscription | 39,728,717 | 1,087,909 | 1,228,160 | 0 | 863,366 |
| Legacy: provider absent | 8,373 | 828 | 0 | 0 | 0 |

{{fig:subscription-tokens}}

A small legacy receipt requests `gpt-6-luna` but lacks an explicit provider field. Its **9,201 measured tokens** remain separately unattributed instead of being silently assigned to an API or subscription provider. Subscription list-price equivalents, where available, are not API payments. The data retains every native stage and token component; the figure groups stages only for readability.

### 8.2 Separate supplements and missing totals

The writer’s round-2 repair/audit supplement records **143,996 input**, **5,888 cache-read**, and **35,228 output tokens** across **eight actual responses**, all requesting Codex. These numbers exclude its preflight and earlier writing attempts. The publication receipt records **155,926 input**, **49,281 cache-read**, **208,242 cache-write**, and **183,617 output tokens**. Its **37 MODEL receipts** include cache replay; **19 dispatches** produced **18 measured responses** and one timeout with unknown usage retained at reservation. Thus its token aggregate is mixed measured/reserved, not wholly measured. These supplements are not added to the lineage subtotal. [R7, R8]

Gap pilot 1 has a separate local ledger: **242 fresh Codex calls**, comprising **221 main-run calls**, **20 schema-preflight calls**, and **one standalone canary**. Measured fresh usage is **4,769,322 input + 235,926 output + 266,752 cache-read = 5,272,000 tokens**; cache writes and server-tool uses are zero. New API spend is **$0**, while subscription dollar-equivalent is unavailable. Requested model identity remains `gpt-6-luna`; served identities are unverified. The pilot report’s inherited extraction charges are not new spend and are not added again to the fork-6 ledger. Its free recovery inspection made no new model calls. [R16]

Gap1r adds **197 fresh Codex calls**: **177 main-run calls** (two canaries, 115 alignment, 60 semantic classification) and **20 preflight calls**. Its measured components are **724,135 input + 36,474 output + 279,680 cache-read = 1,040,289 tokens**, with **$0 new API spend**. Together gap1 and gap1r used **439 calls / 6,312,289 measured token components**. Inherited extraction charges must not be added again. Gap1f and sigma r13's offline plans made no new generation calls. The enlarged-window A/B runs remain pending, and this report does not manufacture an R5–R6 global token total from their audit-call counts. [R18–R20]

Summed measured model wall time in the lineage is **99,802.960 seconds**, approximately **27.723 hours**; unknown-at-reservation receipts add **747.604 seconds** of recorded wall time. Calls can overlap, so neither sum is elapsed campaign duration or human labor. The correspondence span is **8 days, 20 hours, 39 minutes, 11 seconds**. No complete operator-reported labor duration is available. Zero-minute fields on worker-generated command receipts cannot establish zero human effort. [R1, R4]

## 9. Novelty status and limits

### 9.1 Honest novelty status

**Zero substantive novel contributions have been established so far in the evidence covered here.** This is an evidence status, not a theorem that the architecture can never produce one. Earlier closed routes restated sources, packaged conjunctions, or relied on a single paper. Gap1r's two forward leads again packaged existing commitments; the pilot reached no model target or route. The formal novelty gate is weaker than philosophical novelty: passing a per-paper entailment or own-thesis check does not establish an informative argument, faithful premises, priority in modern literature, or resolution of an acknowledged problem. [R6, R9–R11, R18]

L3 remains partially anticipated and unresolved. The **L3 novelty dossier is pending**. Its brief asks for explicit candidate theses and their closest **2018–2026** sources, with bounded verdicts of anticipated, partially anticipated, or not found within the stated search scope. Comparing only with the **26-paper input corpus** (22 papers represented in gap1r’s frozen T) cannot establish modern-literature novelty. Neither an offline request that fits nor the operator's larger-window authorization is evidence that a new thesis was produced. The A/B fork results and any subsequent literature assessment must be reported separately when available. [R19, R25]

### 9.2 What remains unproven

1. **No qualifying cross-paper pilot.** Recovery meets frozen coverage numerically, with 160 commitments and zero unresolved alignments, but stops before target dispatch. Source stance, missing anchors, and disputed bridge semantics remain. The actual freeze was SAT; the padding false positives were observed. Later Xi integration is not a retrospective rerun of that pilot. [R18, R24]
2. **Native exports exist, but source fidelity is not established.** R6 exported two essays with no bibliography entries or citation markers. Audit disagreement persists; k=3 catches more adverse samples but does not guarantee correct judgments. Incomplete adverse history can be dropped on resume. Citation coverage and adverse-history repairs remain pending. [R20, R23]
3. **Context and integration fixes are bounded.** Client metadata and offline packing/forwarding are established. Live larger-window acceptance and fork quality are pending; stage-window admission and the combined full-T control need repair. [R19, R24]
4. **Formal and semantic correctness differ.** Licenses, citations, hashes, SAT checks and typed labels do not prove true premises, faithful translation or reliable audit judgments. The literature review is access-limited and nonexhaustive. [R5, R18]
5. **Isolation and identity are bounded.** Specific canaries and guards passed; vendor instructions and some generic tool definitions remained. Codex serving identity remained unverified. Development-agent context is a separate boundary. [R13, R19]
6. **Accounting and human actions are record-bounded.** The principal ledger is a deduplicated lineage subtotal. Development, orchestration, subscription costs and human labor are incomplete. Appendix A is complete for the frozen correspondence prefix, not unlogged activity. [R1, R4]
7. **Selection/report losses and intake ambiguity remain disclosed.** A target cap, duplicate ID, native report overflow and origin-label defects had consequences (§§3.2, 4.6). Bibliographic titles and human filing labels raised a literal committed-content-rule issue. No added argument annotations were found, but corpus completeness and neutrality were not independently verified. [R2, R4]
8. **Privacy status changed.** The earlier visibility API action failed with HTTP 403. The later **20:04:19 UTC** entry records the repository as private, verified via API, and outputs copied/pushed. The old failure is retained as history, not a current privacy verdict. This report is delivered locally and separately scanned for identity. [R1]

## Appendix A. Complete recorded human-action entries

Timestamps are UTC. Entries are grouped exactly by correspondence record; one entry may contain several instructions or actions. H01–H03 are indirect reports of operator actions. Summaries remove identity and credential locations while preserving the decision. The corresponding anonymised record text and original line number are in `data.json`.

| ID / UTC timestamp | Recorded human action |
| --- | --- |
| H01 · 2026-10-21 00:02:03 | Approved the initial coding workers and spending: five smoke runs capped at $5 each and one pilot capped at $100. This approval is reported by the coordinator. |
| H02 · 2026-10-21 00:12:18 | Chose per-paper logged extraction; the existing pilot was held pending that capability. |
| H03 · 2026-10-21 00:48:04 | Asked the team to collect PDFs; the operational brief restricted collection to lawful open access. |
| H04 · 2026-10-21 02:03:18 | Chose rich extraction rather than the compressed-summary option and said they were obtaining remaining papers. |
| H05 · 2026-10-21 03:38:41 | Approved one additional build-T attempt by increasing its cap from $4 to $6. |
| H06 · 2026-10-21 03:40:20 | Directed extraction to use a cheaper model and asked the team to get through to the pilot. |
| H07 · 2026-10-21 18:21:02 | Pulled and pushed the main branch to the remote repository. |
| H08 · 2026-10-21 18:25:51 | Approved an approximately $600–700 all-in budget, a shared frozen T across candidates, and the start of extraction/pilot work. |
| H09 · 2026-10-22 03:32:13 | Asked for immediate repair of the four-paper failure policy; requested looser workable restrictions and OCR if needed. |
| H10 · 2026-10-22 05:33:48 | Requested a full overnight pass, a $200 cap, and a detailed morning report with search-tree traces; authorized workers and method iteration. The coordinator interpreted the cap as new spend within the earlier campaign budget. |
| H11 · 2026-10-23 13:17:07 | Requested an agent/connector route, a fresh T rebuild, parallel work, and iteration until an acceptable pilot. |
| H12 · 2026-10-24 15:28:25 | Clarified that “use chat” meant ChatGPT/Codex and prohibited Claude-subscription pilots. The active pilot was halted. |
| H13 · 2026-10-25 22:26:45 | Requested integration of the new open-source Baidu OCR family in parallel for future content recovery. |
| H14 · 2026-10-25 22:53:20 | Completed a separate ChatGPT/Codex login. No credential value or identifying location is reproduced. |
| H15 · 2026-10-27 02:06:18 | Requested plain-language documentation and repository organization using an existing internal methodology; the resulting assignment was documentation-only. |
| H16 · 2026-10-27 15:15:37 | Saved a repository access token. The coordinator then pushed and started periodic pushes; no credential value is reproduced. |
| H17 · 2026-10-27 15:38:31 | Approved the complete pilot and entry criteria, including 20/26-paper coverage, three qualifying derived routes, a 4,500–6,000-word audited essay, an anonymised methodology, and the October 31 AoE deadline. Set October 29/30 checkpoints. |
| H18 · 2026-10-28 16:52:30 | Directed “Write C,” asked for at least one resolvable literature gap, and asked to build all routes. The coordinator recorded selection of all available CLOSED-derived routes for writing. |
| H19 · 2026-10-28 20:59:16 | Requested a Claude Opus final pass producing professional papers, visualizations, Markdown, then PDF. |
| H20 · 2026-10-28 21:02:01 | Questioned the lack of novel conclusions; requested bridge-paper discovery/ingestion, creative investigation, consideration of architectural changes, and examination of contradictions. |
| H21 · 2026-10-28 21:03:17 | Required explicit disclosure of missing modern literature, acquisition of that literature, and accurate claims about open questions. |
| H22 · 2026-10-28 21:03:45 | Directed the team to obtain the full texts and put them in the full-text collection. |
| H23 · 2026-10-28 21:06:14 | Requested maximum parallelization of the ongoing work. |
| H24 · 2026-10-28 21:14:27 | Prohibited further credit-based API work and authorized normal agent calls as the default; the coordinator retained Claude only for the separately requested Opus polish. |
| H25 · 2026-10-29 06:17:05 | Gave GO for the safety–retraction gap paper and this visual metapaper; approved “not found within stated search scope, partially anticipated,” directed best effort from available sources, and requested an output repository. |
| H26 · 2026-10-29 06:20:26 | Asked to make the scaffold repository private and place outputs in a folder for later deletion. The visibility API request was refused with HTTP 403 for insufficient administration permission; that action did not change visibility; H28 records the later successful change. |
| H27 · 2026-10-29 19:09:07 | Authorized loosening the token limit. The later adapter change forwards an explicit provider window; raising native admission alone was insufficient. |
| H28 · 2026-10-29 20:04:19 | Reported the repository private; the coordinator verified visibility through the API, copied outputs, and pushed them. This supersedes the earlier failed privacy request. |
| H29 · 2026-10-29 20:41:14 | Questioned idle completed agents and context limits, and asked whether the work was pursuing real novelty. The coordinator requested an L3 novelty dossier, delivery integration, and this report revision. |

**Earlier human actions without a timestamp in this log.** The human designed and directed the scaffold, chose the topic, and supplied/committed the initial bibliography and filing labels. The intake review found no added argument annotations, but flagged an unresolved literal-rule tension: bibliographic titles and human-provided grouping labels can name positions despite the repository’s blanket prohibition on committed philosophical content. Four position-related filing labels were not four selected theses. The collection’s claimed completeness and neutrality were not independently verified. No selection policy is promoted here into proof that the corpus was balanced. [R2]

## Appendix B. Evidence register and reproducibility

The following local source identifiers are intentionally free of operator identity. `data.json/sources` records their SHA-256 digests at collection. Later source changes do not alter this snapshot’s claims. Model receipt entries carry original event-content hashes and prompt hashes. For chart data, consult `data.json/figures` or `figures/manifest.json`; for exact instructions, consult `prompts.md` and `prompts.json`.

| ID | Primary sources and responsibility |
| --- | --- |
| R1 | `correspondence/log.txt`, frozen through 2026-10-29 20:41:14 UTC: decisions, iterations, human actions, and timing. |
| R2 | `briefs/beta-literature.md`, `reports/beta-literature.md`, `reports/epsilon-pdfs.md`: supplied bibliography, intake scope, rule issues, initial access. |
| R3 | Scaffold `CLAUDE.md`, `PLAN.md`, `SOURCE_MAP.md`, `DECISIONS.md`, and `docs/`: architecture, boundaries, lifecycle, policies and their limitations. |
| R4 | `reports/overnight/fork6/{data,accounting}.json`, its content-addressed event sidecars, and `reports/zeta-fork6.md`: deduplicated accounting, gap/search outcomes and report defects. |
| R5 | `reports/eps2-bridge-literature.md`, `eps2-L3.md`, `eps2-methodology-supplement.md` and their JSON twins: initial sweep, focused currency check, cumulative coverage. |
| R6 | `reports/zeta-codex-pilot-5.md` and `reports/overnight/codex5/`: frozen structure, stance, symbol reuse, targets and routes. |
| R7 | `reports/nu4-writer.md`, round-2 and round-4 native receipts, plus `zeta-writing-test.md` and `zeta-writing-route2.md`: length repair, audit variation, blocked retrieval and export. |
| R8 | `reports/pi3-publication.md` and `pi3/runs/pi3-proof/live-result.json`: preserved input, polish, native audit, usage and rendering evidence. |
| R9 | `reports/zeta-fork1.md` through `zeta-fork6.md`, native target-gate receipts and `kappa4-review.md`: rejection mechanisms, counterexamples, false positives and substantive route review. |
| R10 | `reports/zeta-codex-pilot-2-resumed.md`, `zeta-codex-pilot-3.md`, `xi-search-diagnosis.md`: atomic T, conclusion mismatch and trivial closure. |
| R11 | `briefs/xi-round-27.md`, `reports/xi-round27.md`: per-paper novelty correction, superseded census and final bounded zero-candidate census. |
| R12 | `reports/zeta-full26-part7.md`, `gamma-extraction.md`, `mu-four-papers.md`, `sigma-bounded-closure.md`: extraction inventory, quarantine, retention and construction repairs. |
| R13 | `reports/omega-subagent-provider.md`, provider review reports and scaffold `docs/providers.md`: API/CLI versions, isolation scope, calibration and diagnostics. |
| R14 | `reports/zeta-conflicts.md`: bounded semantic-conflict pass and source/currency review. |
| R15 | `briefs/` and run MODEL receipts; exact instruction variants in the prompt supplement: task direction, stage instructions, correction history and prompt identities. The instruction supplement remains the version-1 inspected scope. |
| R16 | `reports/overnight/gap1/handoff.md`, `reports/zeta-gap1.md`, `pilot-exit.json`, `final-local-accounting.json`, and the preserved integration review: failed alignment, construction inventory, source limits, timing and fresh usage. |
| R17 | `briefs/sigma-round-12.md` and `briefs/nu4-round-5.md`: historical repair requests, pending at v2; later results are in R18 and R20. |
| R18 | `reports/overnight/gap1r/handoff.md`, `reports/zeta-gap1r.md`, `reports/overnight/gap1r/final-local-accounting.json`, `reports/overnight/gap1r/pilot-exit.json`: Gap1r recovery, frozen inventory, source/padding review, admission refusal, timing and fresh accounting. |
| R19 | `reports/overnight/gap1f/handoff.md`, `reports/sigma-round13.md`, `briefs/zeta-gap-fork2.md`: Gap1f client-window inspection, sigma r13 offline plans/window plumbing, pending packed/unpacked fork brief. |
| R20 | `reports/nu4-writer.md`, `briefs/nu4-round-7.md`: Nu4 R5–R6 native exports, audit dissent and union batches, citation loss; R7 repair brief remains pending. |
| R21 | `reports/kappa4-sigma12-review.md`: Kappa4 s12: ID-free response and recovery review, integration fixture blocker. |
| R22 | `reports/kappa4-nu4pi3-review.md`: Kappa4 np: publication screening/title/occurrence blockers, audit and length-policy notes. |
| R23 | `reports/kappa4-r2-review.md`: Kappa4 r2: Pi closure evidence, incomplete adverse-history and citation-stripping blockers. |
| R24 | `reports/kappa4-sigma13-review.md`: Kappa4 s13: stage-window admission mismatch, merged mutation-anchor failure, S12-F1 closure. |
| R25 | `briefs/eps2-L3-novelty.md`: L3 novelty-dossier brief; requested modern-literature assessment, results pending. |

This document was assembled from existing evidence without new ARA provider calls. Its authoring-agent usage is outside the supplied accounting. Charts were generated deterministically with matplotlib, using serif type, greyscale, and one accent color. Markdown was rendered through local Chromium because the available `ara render-pdf` CLI accepts a native publication run rather than an arbitrary methodology document. Rendering checks cover embedded fonts, figure inventory, captions, page bounds, and horizontal overflow. `verification.json` records the executed checks and artifact hashes.

**Finding placement.** Each material finding is placed in the report as follows.

| Finding | Report section |
| --- | --- |
| 1. No substantive novel contribution or qualifying pilot | 5, 9.1 |
| 2. Historical R4 audit counts versus marker-free words | 3.3 |
| 3. Gap1 correct ID refusal and missing continuation | 3.4, 4.7 |
| 4. Recovery and zero unresolved do not certify bridge semantics | 3.5, 9.2 |
| 5. Source stance, citation spans, omissions and incomplete L3 anchors | 3.4–3.5 |
| 6. SAT freeze excludes R28-F2 here; observed padding remains | 3.5, 9.1 |
| 7. Full target request refused despite smaller readiness check | 3.5, 7.1 |
| 8. Pinned window metadata and omitted adapter forwarding | 7.1 |
| 9. Offline one-hop packing is not pending two-hop fork A | 7.1 |
| 10. Audit nondeterminism and k=3 union limits | 3.3.1 |
| 11. Native exports lost all citations; R7 pending | 3.3.1, 9.2 |
| 12. Incomplete adverse history can allow unchanged export | 4.8 |
| 13. L3 partial anticipation, access limits and pending novelty dossier | 6, 9.1 |
| 14. Isolation and unverified serving identity | 7, 9.2 |
| 15. Accounting and human record limits | 1, 8, 9.2, Appendix A |
| 16. Target and native report losses | 3.2, 4.6, 9.2 |
| 17. Privacy failure superseded by later verified status | 9.2, Appendix A |
| 18. Intake ambiguity and unverified collection neutrality | 9.2, Appendix A |
| 19. S12-F1 fixture failure closed at later integrated head | 4.8 |
| 20. NP-F1 imported publication screening closed for publication | 4.8 |
| 21. NP-F2 title audit/cache omission closed for publication | 4.8 |
| 22. NP-F3 duplicate occurrence permission closed for publication | 4.8 |
| 23. S13-F2 stage-window over-admission pending repair | 4.8, 7.1 |
| 24. S13-F1 merged mutation control still pending repair | 4.8 |
| 25. Green scoped tests did not exclude review blockers | 4.8 |
| 26. Separate length policies and source versions | 3.3.1, 4.8 |

**26 findings, 26 placed.**
