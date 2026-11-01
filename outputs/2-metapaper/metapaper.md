# Philosophy as search over licensed arguments

*The ARA method, with a safety–retraction case study · Version 8*

## Executive summary

ARA generates philosophical targets, searches for arguments for and against them, and turns suitable candidates into papers whose claims can be traced to sources or explicitly proposed premises. Its method separates a bank of licensed argument moves (**L**), a frozen theory of source commitments (**T**), and a workspace of hypotheses and targets (**H**). Language models suggest the content. The runtime controls which moves enter an argument and records what remains to be defended.

The distinctive contribution is the connection between these stages. Source stance and page provenance survive formalization. Novelty is tested against each paper separately, so combining premises can yield a new consequence without treating a conjunction of familiar claims as a thesis. A proposed bridge can enter as a disclosed hypothesis; a paper must then distinguish what follows conditionally from why that hypothesis should be accepted. Typed sentence audits, repeated audit samples and local citation checks carry the distinction into prose.

The safety–retraction case produced two audited proposal papers and a rendered gap analysis. The exact biconditional connecting safety failure to obligatory retraction was not found in a bounded literature search. Its proposal paper states and argues for the missing normative bridge and a separate assumption needed for the converse. The sources did not mechanically establish the biconditional. This is a concrete output of the method: a research question becomes an inspectable proposal with identifiable premises, objections and citation trails.

## Abstract

ARA is a method for generating philosophy through search over licensed arguments. It extracts source commitments with stance and page provenance, assembles and freezes a theory, proposes targets, and searches for both a thesis and its negation using a bank of argument schemes. Solver checks govern deductive steps; defeasible schemes carry explicit critical questions. Backward gap detection identifies missing connections and unresolved tensions, while forward search asks what commitments from different papers jointly support. Novelty is assessed relative to individual papers, with separate controls against repackaging and a further comparison with the wider literature. When a new bridge is needed, ARA can record it as a proposed premise and preserve the conditional character of any resulting argument. Proposal mode instead supports a paper that argues for that bridge. Writing is grounded in the route and sources, then checked through typed sentence audits, conservative repeated sampling, local citation verification and controlled editing. A worked example follows the relation between worldly-information safety and assessment-sensitive retraction through literature comparison, target search and two delivered proposal papers. The method produces inspectable philosophical proposals and exposes the assumptions needed to develop them. The principal open problem is faithful shared formalization across papers: source coverage and fluent prose alone do not supply an executable connection.

## 1. The idea: philosophy as search over licensed moves

A philosophical paper often draws its force from a small number of transitions: an observation supports an explanation; a counterexample challenges a generalization; two claims together imply a consequence; an objection exposes a condition that the argument has not met. ARA makes these transitions explicit. A language model may suggest a thesis or a promising line of reasoning. To enter the recorded argument, a step must fit an available argument scheme and satisfy the checks attached to that scheme. The resulting object records the claim, its support and any outstanding obligation. [E1]

The method divides responsibility among three components. **L** is the bank of licensed moves. It states the forms of reasoning that a search may use. **T** is the source theory: accepted formal commitments, each linked to a paper, a passage and a stance. **H** is the workspace of proposed targets, intermediate claims and, where explicitly admitted, hypothesis premises. A target is something to investigate. An admitted hypothesis premise is something temporarily assumed. The system records the difference, because proposing a conclusion does not authorize using it as a premise.

This division gives language models substantial creative work. They select relevant passages, propose formalizations, identify similarities, suggest theses and attempt arguments. It also limits what their fluency can establish. A model's explanation that a step is plausible does not itself license the step. The runtime checks the supplied structure against L, the available source commitments and the relevant obligations. An accepted transition therefore has a recorded basis that can be examined independently of the prose used to recommend it.

{{fig:architecture}}

### 1.1 Deduction and defeasible reasoning

For a deductive move, ARA checks both the argument's form and the entailment of its conclusion from its stated premises. Z3 supplies the solver check for the supported formal language. The bank adds the requirement that the step instantiate a permitted move. This matters because a solver answer by itself does not explain which part of the argument is doing the work. The route retains the premises and the named move, so a reader can inspect the inference as well as its formal verdict. [E1]

Many philosophical arguments are defeasible. Evidence may count in favor of an explanation without entailing it; a sign may support a conclusion while admitting another explanation. Such steps carry critical questions. A sign argument, for example, needs more than the observation of a putative sign: relevant questions about its connection to the conclusion and alternative explanations remain part of the route. ARA records answers and support where they are available. An unanswered required question remains an obligation.

The status **CLOSED** means that a route met the formal obligations imposed by its recorded scheme and system revision. **OPEN** means that some obligation remains. An OPEN route can contain a useful licensed step and still fall short of a completed argument. These statuses concern the recorded argument. Whether its premises are true, its source translations faithful, or its conclusion philosophically valuable requires further judgment.

### 1.2 What the method makes available to a reader

The output is an argument that can be challenged at several precise points. A reader can ask whether a passage supports a premise, whether the author endorsed it, whether the formal translation preserves its scope, whether the chosen scheme applies, or whether a critical question has been answered. A proposed bridge is visible at the place where it enters. Disagreement can therefore identify a premise or transition instead of relying on an overall impression of a convincing essay.

This structure is particularly useful for synthesis across papers. Each paper may provide part of an argument without stating the combined conclusion. ARA preserves which source contributes which part, then searches for an admissible connection. The new work may be a jointly supported consequence, an intermediate lemma, or a bridge that still needs an independent defense. The paper produced at the end must retain that distinction.

The contribution of the present implementation is an enforced connection between source evidence, argument search and writing. It makes the status of a philosophical claim travel with that claim into the finished paper. The case study below shows what this permits in practice, including a proposal whose missing normative assumption can be stated and discussed clearly. Comparative priority over every other research system is not established by this study.

## 2. Building a source theory from papers

### 2.1 Extract arguments with their source context

ARA begins with full texts and a bibliography selected for the research task. Extraction records premises, conclusions, inference structure, qualifications and source locations. The aim is to retain material from which an argument can be reconstructed. A sentence stating an objection, a premise supporting the author's conclusion and a view quoted for criticism cannot all become premises with the same authority. [E2]

Each extracted item therefore retains provenance. The record identifies its paper and passage, together with the context needed to interpret it. Page references let a later reader return to the source. Dependencies link a conclusion to the premises or qualifications on which it relies. Material that fails grounding or validation is kept apart from eligible evidence rather than silently promoted into the theory.

The distinction between extraction and construction is useful. Extraction can preserve a rich range of claims from a paper. Construction selects and formalizes the commitments relevant to a particular investigation. An extracted claim is not automatically an accepted premise, and an acquired PDF does not automatically enter an existing theory. This gives the experiment a definite evidential scope.

### 2.2 Windows keep the relevant dependencies together

A construction request operates over a window of grounded evidence and its dependencies. The window gives the model enough context to propose formulas and explain their source basis, within the request's capacity. The accepted output records the formula, its symbols, the source passage and the stance. The runtime checks this output against the permitted formula language and the evidence supplied to that request.

Window boundaries matter because a philosophical claim can depend on a definition or restriction elsewhere in the paper. A conclusion detached from its qualification may express a stronger thesis than the source defends. Dependency-aware construction seeks to carry those supporting items into the same request. When the necessary material cannot be admitted, the omission remains recorded. The resulting theory can then be assessed as a selection from the literature rather than mistaken for a complete transcription of it.

Immutable identity belongs to the runtime. The model can return a judgment or a local reference to an item; code binds that answer to the existing source record. This keeps the identity of a passage stable through construction and later use. It also lets completed work be reused without asking a model to reproduce identifiers or reinterpret evidence that has already been accepted. The methodological benefit is continuity of reference: the premise discussed during writing remains the premise inspected during construction.

### 2.3 Stance changes how a premise may be used

ARA distinguishes **endorsed**, **reported** and **attacked** commitments. An endorsed commitment is presented as part of the source author's own position. A reported commitment describes another view without attributing endorsement to the reporting author. An attacked commitment is a position the source challenges. These labels preserve a basic philosophical distinction that ordinary citation can conceal: a page containing a proposition need not support that proposition.

Stance also affects synthesis. A claim drawn from one paper's objection cannot be counted as that paper's endorsed contribution to a joint argument. A report of a rival position can help formulate a conflict or an objection, while retaining its reported status. The system thus separates relevance to a discussion from authority as an endorsed premise.

Source wording and attribution are stored separately from the formal content. A formula should express the proposition under investigation; its provenance should explain who advances or rejects it. Keeping these responsibilities separate makes it possible to reason about the proposition without turning every target into a statement that an author said something. The source connection remains available when the paper must attribute the claim.

### 2.4 Alignment proposes connections across papers

Different authors can discuss the same relation using different vocabulary, or use similar words for different relations. Alignment compares candidate commitments across papers and records a semantic judgment, such as a directional entailment, incompatibility or lack of a relevant connection. A useful alignment must respect the direction and scope of the claims. Similar terminology alone does not establish equivalence.

An alignment judgment is model-generated evidence about a proposed connection. It does not make either source endorse a new claim. ARA retains the judgment's origin and subjects any admitted formal bridge to the relevant consistency checks. This keeps the contribution of the original papers distinct from the model's interpretation of their relationship.

The distinction becomes especially important when papers divide a subject differently. One source may analyze knowledge, another the truth of an assertion, and a third an obligation to withdraw it. A vocabulary alignment that erases those differences would conceal the very philosophical question being investigated. The safety–retraction example requires the relation among these concepts to be argued, not settled by a shared label.

### 2.5 Freeze once, then preserve the experiment's premises

After construction and alignment, ARA freezes T for that lifecycle. The freeze fixes the accepted formulas and their provenance. Search forks can then investigate different targets or use different request configurations against the same source theory. A result remains attributable to what that particular experiment knew. Newly acquired papers do not retroactively strengthen it. [E2]

{{fig:lifecycle}}

A change to the theory belongs to a new lifecycle. Consolidation, for example, re-formalizes already accepted source content using a shared catalogue while retaining the original text, source identifiers, stance and provenance. It records old and proposed formulas, performs new alignment and creates a new freeze. Hypothesis admission likewise occurs before the freeze of its own lifecycle. The prior theory remains available for comparison.

This makes philosophical disagreements about formalization inspectable. One can compare two theories built from the same passages and ask what changed in their formulas, rather than attributing a new result to additional literature that was never acquired. The method preserves both the historical experiment and the interpretation being tested next.

## 3. Finding where philosophy is missing

### 3.1 Backward investigation starts from an obligation

A backward investigation begins with a question that the current evidence does not settle. The starting point may be a conflict between source claims, a tension between endorsed positions, an explicit open problem, or an attempted argument whose next step lacks support. The investigation asks what would connect the available premises to the target and whether the literature already supplies that connection. [E3]

Conflicts must be interpreted before they become research questions. Two sentences may concern different agents, times, senses of a term or levels of explanation. An author may report a claim in order to reject it. Stance and provenance help distinguish a disagreement among endorsed positions from a contrast that a source has already explained. Formal inconsistency and philosophical disagreement are also different findings: an inconsistent union cannot be used to derive arbitrary novelty.

An explicit open-problem statement is a lead with a date. Its author may have written before a later solution, qualification or reformulation. ARA therefore pairs source-level gap detection with a literature-currency check. That check examines later work and nearby formulations, records what was accessible, and states how closely the proposed question matches the literature. It can turn a broad apparent gap into a more precise missing premise.

For the safety–retraction investigation, the useful question was not simply whether safety and retraction had ever been discussed together. They had. The remaining task concerned a particular normative connection: whether failure of a specified safety condition obliges the original speaker to retract the same earlier assertion, with its context of use fixed. The backward procedure made the demanded connection more exact.

### 3.2 Forward investigation asks what follows jointly

Forward search begins with accepted premises and asks which consequences the licensed bank can construct. Its philosophical interest lies in a consequence that requires contributions from different papers while being absent from any single paper's endorsed theory. ARA therefore measures source-relative novelty against papers separately. It permits the combined theory to entail a candidate. [E1, E4]

A small schematic example explains the policy. Suppose paper A supplies P, while paper B supplies the conditional P → Q. Neither paper's accepted commitments alone entail Q, but their union does. A licensed application of modus ponens can make Q a candidate for synthesis. This example illustrates the gate's logic; it is not a result attributed to the safety–retraction corpus.

For each source paper i, let Eᵢ denote its accepted endorsed commitments, interpreted under the supported closure rules. A candidate for deductive synthesis must survive the individual-paper tests: Eᵢ must not already entail it. The union may entail it, and a route must still supply the licensed argument. This avoids excluding the very joint consequences that cross-paper reasoning seeks.

The policy also rejects simple repackaging. If two sources supply P and Q, merely naming P ∧ Q as a new thesis does not demonstrate a substantive connection. The implementation applies anti-padding and support checks alongside the per-paper comparison. Consistency checks prevent an inconsistent endorsed union from becoming an unrestricted source of consequences. These controls define a source-relative candidate; they do not determine its importance to philosophy.

{{fig:gaps}}

### 3.3 A gap description and a target play different roles

A gap description states what the investigation lacks. A target states a proposition for which an argument will be sought. The difference helps control scope. “How are safety and retraction related?” invites several answers. A target claiming sufficiency makes one demand; a biconditional adds a separate demand for necessity. A negative target may expose a counterexample or show why an attractive bridge needs restriction.

The target record includes its formulation and proposed source basis. Targets generated by ARA remain distinguishable from hypotheses supplied by a literature analyst or human direction. Their origins matter when reporting what the search discovered. Supplying a well-defined external target can be a useful test without converting that formulation into an ARA-generated discovery.

The procedure can also reveal a mismatch between a promising sentence and the available formal theory. An English target may name relations that the accepted formulas do not expose. A meaningful search needs shared formal structure connecting its premises and conclusion. Larger search bounds cannot supply the internal relations hidden inside an opaque proposition. This is the methodological problem addressed by consolidation (§8).

### 3.4 Formal novelty and literature novelty are separate questions

A target can be new relative to the selected theory and familiar in the wider literature. It can also be absent from the retrieved literature while resting on a mistaken translation or an undefended premise. ARA keeps these evaluations separate. The formal tests concern source theories and routes. The literature comparison concerns the proposed thesis as a philosophical claim, including its nearest precedents and rivals.

The literature dossier uses three bounded verdicts. **Anticipated** means that an accessible source already develops the relevant view. **Partially anticipated** identifies components that are already present and the proposed addition that remains unestablished. **Not found within scope** means that the search and inspected texts did not locate support for the exact formulation. The last verdict is useful for directing work, but it establishes neither truth nor priority.

A good comparison states the target precisely enough that a nearby result cannot silently replace it. A condition on knowledge differs from a condition on truth; permission to retract differs from an obligation to retract. When a proposed thesis changes one of these terms, its relation to the literature must be reassessed. The nine-thesis comparison in §6 shows how this supports research rather than reducing novelty to a keyword search.

## 4. Generating theses and constructing arguments

### 4.1 Search both a thesis and its negation

For each admitted target, ARA searches the positive and negative polarities. The two searches ask for arguments supporting the proposition and its negation under the available theory and licensed moves. Searching both makes counterargument part of the research procedure instead of leaving it entirely to the later essay writer. [E4]

Neither an unsuccessful positive search nor an unsuccessful negative search settles the issue. An OPEN positive route is not a proof of the negation, and two OPEN routes do not establish independence in a mathematical sense. They show what this bounded search left unresolved. Their value lies in the explicit obligations and any accepted intermediate structure they contain.

The search uses source commitments, proposed intermediate claims and argument schemes to extend routes. An intermediate claim can divide a difficult target into smaller obligations. Each extension must preserve the connection between its premises, conclusion and licensed move. The system records what was accepted, so the final route can be distinguished from suggestions that a model made but the runtime did not admit.

### 4.2 Routes expose the structure of an argument

A route is presented as an argument tree rooted at the target. Its children identify premises or subclaims required to support the parent. Source leaves point back to T. Other leaves may be unresolved subclaims. A defeasible node carries its critical questions as explicit obligations. This representation makes both the progress and the incompleteness of an argument visible.

One recorded comparative route illustrates the distinction. It joined Egan's response to a communicative objection with MacFarlane's criticism of Solipsistic Contextualism's treatment of genuine disputes through a sign scheme. The route contained one accepted inference and two source leaves. One critical question was supported; another remained unsupported. The route therefore stayed OPEN. It had an inspectable argument structure even though it did not establish its comparative conclusion. [E4]

{{fig:route}}

A writer can discuss such a partial argument if its status is preserved. The paper must explain the supported transition and the unresolved question, rather than presenting the conclusion as established. This is one way the system can produce useful philosophical material before an entire route closes. The partial sign route is distinct from the safety–retraction proposal developed in §6.

### 4.3 Keep source authority separate from model-visible context

A search request may need a compact selection from a large frozen theory. ARA packs model-visible material while retaining the full theory for licensing, stance and novelty checks. The selection must include the target's declared source basis and the relevant formal neighborhood. A compact index naming a premise does not replace the premise's formula and source content. [E2, E4]

This arrangement separates two responsibilities. Retrieval decides what evidence the proposing model sees at that step. Validation decides whether the proposed move is admissible against the authoritative theory. Reducing a request therefore need not weaken the gate, but it can still deprive the model of a useful premise unless basis coverage is protected.

The recorded full-basis replay retained complete target bases in all 46 map requests and 92 cut requests examined. This is evidence that the request construction preserves those declared premises. It does not establish that a model will discover a useful argument from them. The philosophical payoff is a better-defined test: an empty proposal is more informative when the model actually saw the evidence on which the target was based.

### 4.4 Admit a new idea as a disclosed premise

Some gaps require a bridge principle that the sources do not supply. ARA provides a specific place for that proposal. An H premise carries its origin, rationale and linked target, with stance recorded as proposed. It enters a new construction-reuse lifecycle before that lifecycle freezes. Formula and consistency checks still apply. The runtime gives H no source-paper credit. [E5]

The resulting claim has the form: given the source commitments and the disclosed hypothesis, this conclusion follows through the recorded licensed moves. The hypothesis remains a philosophical commitment to be defended. It does not become an endorsed source claim because the solver accepts a consequence from it.

This is especially useful when the missing work is normative. A source may explain the conditions under which a belief is safe; another may state a rule governing retraction. A proposal can connect those concepts, but the connection must be identified as new. The derivation then shows what the proposal would support, while the paper assesses why a reader should accept it.

{{fig:hypothesis}}

The design also guards against trivial conditional success. Assuming the target itself and adding irrelevant source material would create a formally easy route without substantive synthesis. H cannot count as a second source paper, and a qualifying cross-paper route must still make genuine use of source premises. Affirmative conditional disclosure is produced by the runtime, so a writer cannot omit the hypothesis on which the conclusion depends.

### 4.5 Proposal mode makes the bridge itself the subject

A proposed bridge can merit a paper before a conditional route has been licensed. Proposal mode supports that task. It requires a clear origin label, an explicit statement and defense of the bridge, faithful attributed source claims, and no presentation of the proposed thesis as an established result. Objections and replies may develop the proposal in ordinary philosophical prose. [E5, E6]

This permits two related outputs. A conditional-derivation paper explains a licensed route from T plus disclosed H, and separately defends H. A proposal paper argues for H or a target bridge without claiming that such a route has been obtained. Their status is carried through drafting and verification. The distinction lets the system pursue new ideas while remaining precise about where those ideas enter the argument.

## 5. From a route to a paper

### 5.1 Draft around the argument and its evidence

The writing stage receives the route, source evidence and the permissions associated with the candidate's mode. It develops an outline with section budgets, then writes and assembles the sections. A route-based paper should explain the target, introduce its premises, present its licensed steps and discuss remaining obligations. A proposal paper should state its bridge, defend it and consider objections while preserving the difference between source claims and new reasoning. [E6]

This organization lets prose do work that a formula cannot. It can explain why a premise is interesting, distinguish a claim from a nearby rival, motivate a definition and make a critical question intelligible. Such exposition remains accountable to the route's status. Elaborating an OPEN argument does not close it, and improving the style of a proposal does not convert its bridge into a source theorem.

The all-candidates pipeline automates entry into this process for eligible candidates. A CLOSED route can enter writing, as can an OPEN route with an accepted inference under the relevant policy. Selected root-only hypotheses can enter through the separately authorized proposal mode. The queue records which path a candidate uses, allowing drafting to proceed across the available candidates while the human retains final submission selection.

### 5.2 Audit sentences according to what they claim

A sentence reporting a source claim needs different support from a sentence posing an objection. ARA therefore uses a typed audit. It distinguishes source claims, argument steps, proposed principles, reasons offered for a proposal, framing, objections and replies. The auditor asks whether a sentence satisfies the requirements of its role. [E6]

A source claim must be faithful to the cited passage and its scope. A route step must match the recorded argument. A proposed principle must retain its proposed status. Exposition can explain the argument without pretending to be an extra licensed inference. This makes the audit compatible with a readable philosophical paper: every sentence does not need to repeat a formula or carry the same kind of citation.

The audit also checks coverage. A paper should not omit an awkward node or add an unsupported transition between two source claims. Node and citation markers connect prose to the underlying record during verification. The final presentation can use ordinary references while retaining the machine-readable evidence needed to inspect those connections.

### 5.3 Use repeated judgments conservatively

Model judgments about prose vary. ARA uses three fresh audit samples and takes the union of valid adverse findings, together with relevant adverse history. A clean sample cannot erase a still-applicable objection from another sample. Revision addresses the union and returns through the required checks. [E6]

This policy is conservative about unresolved disagreement. It does not interpret three calls as three statistically independent experts or turn a zero-flag result into a probability that the paper is correct. Its purpose is operational: a favorable rerun should not let an unsupported sentence survive without a reasoned repair or a justified change in its status.

Repair is tied to the sentence and its evidence. A local edit may correct a quotation, narrow a claim or remove an unsupported elaboration. The revised draft is then checked under the same responsibilities. This preserves a useful relation between the audit's objection and the writer's response, instead of treating a new whole-paper draft as if its history had disappeared.

### 5.4 Verify citations against the local source

Citation verification checks more than the existence of a bibliographic item. The local PDF must match the claimed source; the location must identify the relevant passage; a quotation must match the source text; and the cited passage must support the attributed claim. Physical PDF pages and printed page numbers may differ, so a reproducible locator must state which it uses. [E6, E7]

This is a separate responsibility from sentence auditing. A fluent source summary can cite the wrong passage. A correctly located quotation can still be used to support a stronger claim than the source makes. The pipeline therefore retains both checks rather than treating either as a substitute for the other.

The finished paper's references also carry result status. A dossier's “not found” verdict is evidence about a literature search, not a premise proving the proposed thesis. A model-generated bridge is not a source endorsement. These distinctions are as important to a trustworthy citation trail as the formatting of the bibliography.

### 5.5 Improve style without changing the argument's authority

Editing operates on a verified source draft. Exact source identity, evidence, outline and citation markers bind any carried-over verdict. Limited normalization can preserve an already checked sentence through changes in typography or redundant prefixes. A substantive wording change needs a new judgment about whether its meaning has changed. [E8]

For aligned edits outside that limited normalization, the recorded method uses three fresh meaning judgments. Only unanimous equivalence permits the sentence to inherit the source verdict. A changed or uncertain sentence returns to ordinary typed audit; valid adverse history remains relevant. This lets a paper become more readable without assuming that a stylistic instruction guarantees semantic preservation.

{{fig:publication}}

A delivery decision thus concerns a particular text and its evidence. An accepted original can remain the delivered paper when a later polished version is not accepted. The verified originals discussed below are the actual outputs of that policy. Their audit and citation trails belong to those texts, not to every subsequent attempt to rewrite them.

## 6. Worked example: safety and the obligation to retract

### 6.1 Define the question before seeking the connection

Consider an earlier assertion of “might p.” A later context supplies a new standpoint from which the assertion is assessed. The safety–retraction investigation asks whether failure of the original belief's worldly-information safety, evaluated at that later assessment, obliges the original speaker to retract the same assertion. The context of use fixes the original assertion under discussion; the context of assessment supplies the later standpoint. Holding use fixed keeps the question about that assertion rather than a new utterance with a different content.

This formulation distinguishes several possible outcomes. The speaker may lose knowledge, the earlier assertion may be judged untrue, another participant may reject it, or the original speaker may be required to retract it. Those outcomes are not interchangeable. The investigation concerns a proposed connection between a condition on belief and a normative requirement concerning an assertion.

The project called this missing connection L3. The label identifies a research question, not a bank license or a result. The method took it through source selection, literature comparison, explicit candidate formulation, polarity search and proposal writing. The resulting paper makes the missing bridge a subject for philosophical assessment. [E3, E7]

### 6.2 Identify what each source actually contributes

Beddor and Goldstein's *Mighty Knowledge* (2021) supplies the safety side. Their account treats information-sensitive safety as a condition on modal knowledge. Each possible world determines a body of worldly information relevant to knowing epistemic-modal claims. Safety evaluates the belief across nearby worlds where it is held, using the information associated with those worlds. A later assessor’s disagreement alone is not a test of that condition. The dossier also found discussion of retraction and assessor information in the paper. This is substantial prior engagement with the issue; it does not identify safety failure with the falsity of an earlier bare might-assertion.

MacFarlane's *Assessment Sensitivity* (2014, printed pp. 108–109; PDF pp. 122–123 in the inspected copy) supplies the Retraction Rule. It gives a sufficient trigger for required retraction when an assertion is not true as used at its original context and assessed from the later context. The rule therefore provides a two-context normative structure. It does not say that any failure of safety meets its antecedent, or that its stated trigger is the only possible ground of a retraction obligation.

Hawke's *Stable acceptance for mighty knowledge* (2024) develops an alternative treatment of modal knowledge and considers when available evidence supports denying a knowledge attribution. That helps distinguish a current denial of knowledge from an obligation to retract a particular earlier assertion. In *Modal Knowledge for Expressivists* (2024), Hawke examines a safety variant that removes a truth conjunct. The variant makes it especially important to keep safety and truth distinct. Its countermodels concern the specified knowledge account; they do not themselves establish a retraction norm.

Rudin's *Asserting epistemic modals* (online 2024; issue 2025) reports that willingness to reject modal claims can diverge from judgments that they are false. This bears on how responses to modal assertions should be interpreted. Another participant's rejection, however, does not by itself establish the original speaker's retrospective obligation to retract.

Dinges's *Knowledge and Asymmetric Loss* (2021) develops a further rival explanation. Changes in loss functions can affect estimates of epistemic qualities and willingness to stand by a knowledge claim. The discussion expressly extends to estimates of safety or reliability. It offers a way to understand retraction-related judgments without requiring relativism. Applying that explanation to bare might-assertions or to a normative obligation would require additional argument. [E3]

Together these sources make the question sharper. The safety account supplies a condition relevant to knowledge; the Retraction Rule supplies a sufficient normative trigger; the neighboring literature identifies competing mechanisms and distinctions. The missing philosophical work is the connection among them. Citing all the sources establishes an evidential starting point, not that connection.

### 6.3 Compare candidate theses with the literature

The literature analyst formulated nine candidate resolutions and compared them with retrieved and inspected work. The search covered 2018 through 29 October 2026, with MacFarlane's 2014 book included as an earlier anchor. It used content queries, citation links and focused source reading. Ranking limits, incomplete indexing and access gaps bound the result. The nine formulations were analyst-generated comparison targets, rather than nine discoveries attributed to the native search. [E3]

| Candidate | Question or proposed connection | Literature verdict |
| --- | --- | --- |
| T1 | Safety failure is sufficient for obligatory retraction. | Partially anticipated |
| T2 | Safety failure is necessary and sufficient for obligatory retraction. | Not found within scope |
| T3 | Asymmetric loss explains retraction without relativism. | Anticipated |
| T4 | Stable acceptance guides withdrawal. | Partially anticipated |
| T5 | Worldly information is selected relative to assessment. | Partially anticipated |
| T6 | Flexible truth assessment accompanies current-context retraction. | Anticipated |
| T7 | Speech-act effects explain withdrawal. | Anticipated |
| T8 | Later responses help determine earlier content. | Anticipated |
| T9 | Fragmented or topic-sensitive knowledge supports a retraction norm. | Partially anticipated |

Four candidates were anticipated, four partially anticipated and one not found within scope. T2 was the exact not-found formulation. Its sufficiency direction remained closest to partially anticipated T1. The stronger biconditional's search verdict cannot remove the precedents for that direction.

The comparison therefore supplied two things: a precise target worth investigating and a map of what an argument must acknowledge. T2 must preserve the distinction between safety and truth, address the difference between rejection and retraction, and justify the necessity direction separately. A paper that simply renamed familiar components would not satisfy those demands.

### 6.4 Turn the question into targets and inspect both routes

The exact T2 target concerned the same earlier might-assertion and fixed use context: obligatory retraction at a later assessment occurs if and only if the original belief fails worldly-information safety as evaluated there. The literature analyst, eps2, supplied this formulation for testing in ARA. ARA had also generated nearby targets, including B/2, but those differed in their subject or normative force. Their origins remain distinct. [E4]

ARA tested the exact biconditional and its two directions. The positive and negative routes for all three stayed OPEN without an accepted inference. For the exact biconditional, the recorded positive route was a single open root, as was its negation. The English formulation was richer than its whole-claim atomic encoding. These records show an uncompleted derivation under that theory and search, not a counterexample to T2.

{{fig:worked-example}}

A separate combined design asks what would be required to use the retained safety source and Retraction Rule in a conditional argument. A sufficient-direction hypothesis would connect the specified safety failure to the Retraction Rule's antecedent for the same assertion and contexts. The source rule would then have a distinct role in reaching the obligation. A second hypothesis would address necessity by defending an exhaustiveness condition on the relevant grounds for obligatory retraction. It would have to support the conclusion that no such obligation arises within the target scope while safety is preserved. Simply assuming the desired converse would leave that philosophical work undone. This design keeps the two directions and their assumptions separate. [E5]

The conditional design had not become a licensed route at the retained checkpoint. No H premise had been admitted and no combined freeze or derivation had been completed. Its diagram is a plan for the argument, with proposed dependencies marked as such. A faithful shared formalization is needed before the system can test whether these premises support the intended conclusion through its licensed moves.

### 6.5 Make the bridge an argued proposal

The delivered exact-T2 paper took the proposal path. It stated a normative bridge: later-assessed failure of the original belief's worldly-information safety counts as a defect warranting an obligation on the original speaker to retract that assertion. The paper then treated the converse as requiring a separate exhaustiveness assumption: within the proposed norm, no independent ground imposes that obligation while safety is preserved. [E7]

These are identifiable philosophical commitments. The sufficient direction asks why this kind of epistemic defect should require disavowal of an assertoric commitment. The necessary direction asks why the proposed criterion exhausts the relevant grounds for obligation. The paper's objections and replies examine that second demand. A sufficient trigger does not become a necessary trigger by reversing the conditional.

The sources constrain the discussion without doing all its work. MacFarlane's allowance that one may retract something still thought true distinguishes permissibility from obligation; it does not by itself refute the narrower biconditional about required retraction. Rudin's distinction between rejection and falsity cautions against using one response as a proxy for another. Hawke's safety variant cautions against building truth silently into a safety condition. These distinctions specify what the proposed bridge has to explain.

The proposal is defended conditionally, rather than reported as a theorem already extracted from those sources. Its origin label states that it is an eps2-proposed thesis tested in ARA and that the bridge is argued, not mechanically derived. The original text passed a complete three-sample native audit with no flags and was delivered as an eight-page paper with local citation evidence. The reading count was 3,427 words including the delivery note and excluding references. Later editing attempts do not replace the authority of that accepted original.

B/2 produced a related seven-page proposal paper. Its central criterion concerns warranted retraction of a specified epistemic-modal knowledge claim: the proposed warrant requires failure of the relevant safety condition, and disagreement alone is insufficient. This differs from exact T2's biconditional about the original speaker's obligation to retract a bare might-assertion. B/2 also passed its original three-sample audit and was delivered with its own citation trail, at 3,168 reading words on the same counting basis. The two papers are related proposals, not duplicate proofs of T2.

### 6.6 What the complete example shows

The investigation moved from a broad missing connection to a set of precise thesis alternatives, then to two papers whose proposed additions can be identified. Literature comparison constrained what could be presented as new. Search preserved the absence of a licensed derivation. Proposal mode allowed the philosophical work to continue as an explicit argument for a bridge. Verification attached the delivered prose to particular sources and audit records.

The resulting papers give a reader concrete claims to assess. One can challenge the normative bridge, the exhaustiveness assumption, the scope of the knowledge claim or the interpretation of a cited passage. The gap analysis gives a complementary account of the missing connections and search outcomes. It is a rendered analysis of the research record, with a different verification scope from the two native audited proposals. This end-to-end separation is the method's practical achievement.

## 7. Organizing the work under human direction

The scaffold was designed and directed by a human and built largely by AI coding agents under that direction. The human selected the topic and initial bibliography, approved resource and provider choices, set acceptance criteria and research priorities, and retained final submission selection. Those decisions determine what kind of research the system is attempting; they are part of the method rather than invisible background. [E10]

Specialized workers handled literature acquisition, extraction, construction, search, writing, publication and reporting. Written briefs defined their tasks and the evidence each handoff had to supply. Independent reviewers examined implementation claims and proposed changes separately from the workers who produced them. A shared record connected decisions, source snapshots and outputs across these roles.

The recorded roster credits 43 workers plus one orchestrator. These are agent identifiers, not human names; exact serving-model versions were not recorded for every development worker. Runtime generation and publication models have separate receipts. The appendix groups the workers by their recorded responsibilities without implying that a harness name identifies a particular serving model.

The orchestration also separates production from selection. The all-candidates queue can draft eligible routes and authorized proposals automatically. The human can then compare actual papers, their origins and their verification status rather than choosing only from target descriptions.

## 8. What it produced and what remains open

ARA generated new philosophy papers end to end, taking source literature through target formulation, argument development, writing and manuscript verification. The delivered exact-T2 and B/2 proposal papers have audited citation trails and complete three-sample native audits. T2 develops the safety–retraction biconditional; B/2 argues for a related necessity condition on warranted retraction. A rendered, source-checked gap analysis supplies a third manuscript explaining the research question and its missing connections. Together they demonstrate a working literature-to-paper method. [E7]

The all-candidates pipeline automatically drafts every eligible candidate, including authorized proposals. It connects search directly to manuscript production while preserving each candidate's origin, argument status and evidence. Scale is compute-bound in the number of candidate investigations and drafting passes the system can execute: additional search and writing compute expands that capacity, with the same verification requirements applied to every output. The human director retains final submission selection.

Consolidation extends the method toward shared formal vocabulary. It re-formalizes accepted source content against a common catalogue while preserving source text, stance and provenance, then aligns the revised formulas before a new freeze. The recorded run accepted 22 batches containing 181 commitments from 22 source papers. Fwd's completed census checks actual symbol use in those accepted formulas, rather than treating a catalogue entry or repeated local handle as cross-paper reuse (`reports/vocab-after-r20.md`, measured 1 November 2026). [E9]

The remaining limits are specific. These papers defend proposals; no substantive novel cross-paper CLOSED derivation is established, and a literature verdict of “not found” remains bounded. Fwd measured **zero shared predicates and zero symbols shared across source papers** in the accepted consolidation subset, which remained unfrozen: formal paper isolation is not yet solved there. More compute increases research and drafting capacity, while the number of verified papers still depends on the candidates meeting the argument and manuscript checks.

## Appendix. Sources and credits

### A. Evidence and scope

This methods paper reorganizes the research evidence retained in v7, through 30 October 2026. The source register below points to that record and its primary evidence. It is not a live progress report. The associated `data.json` records source hashes, numerical inputs, candidate identities and figure specifications; earlier editions preserve the incident chronology and full route atlas. No new ARA research run was conducted for this edition.

| Pointer | Evidence used in this paper |
| --- | --- |
| E1 | V7 §§1 and 4.1–4.2: L/T/H architecture, bank licensing, solver checks, defeasible obligations and per-paper novelty; underlying scaffold documentation and recorded search policy. |
| E2 | V7 §§2–3: extraction, stance, provenance, alignment, freeze lifecycles and full-basis request construction; construction and packing receipts. |
| E3 | `reports/eps2-L3-novelty.md`: nine-thesis comparison, source passages, acquisition and bounded search scope. Its hash matches the v7 snapshot. |
| E4 | V7 §§4.3–5.3 and route atlas: actual targets, polarity routes and the partial sign argument. `data.json` retains the exact-T2 target and both route records. |
| E5 | V7 §6: hypothesis-premise policy, proposal mode and the combined safety–retraction design; source-bound conditional status and the uncompleted combined route. |
| E6 | V7 §§7.1–7.5 and 7.7: sectioned writing, typed audit, repeated-sample union, candidate queue and local citation verification. |
| E7 | `reports/candidates/pi3-original-delivery.md`; the B/2 and exact-T2 candidates' `paper.md`, `paper.pdf` and `pi3/verified-original-render.json`; gap-analysis artifacts. Original texts and audit gates are distinguished from later editing attempts. |
| E8 | V7 §§7.6 and 7.8: source-bound sentence carry-over, unanimous meaning comparison and the status of revised texts. |
| E9 | V7 §§2.3, 2.6–2.7 and 5.3: counts of atomic commitments and shared symbols, the consolidation lifecycle and the retained search outcomes. |
| E10 | V7 §§8.4 and appendices B–C: human direction, worker credits and recorded decisions. Agent identifiers below are not human names. |

The gap analysis is `reports/candidates/gap-T2-analysis/paper.pdf`. The audited proposals are `reports/candidates/gap1pu-B-2-proposal/paper.pdf` and `reports/candidates/gap1pu-C-T2-iff-proposal/paper.pdf`. Relative paths begin at the research workspace. Their distinct verification scopes are stated in §§6 and 8. Verification of this methods paper covers source consistency, deterministic figures, rendering and anonymity; it is separate from the native audits of the proposal papers.

### B. Works central to the example

Beddor, Bob, and Simon Goldstein. 2021. “Mighty Knowledge.” *Journal of Philosophy* 118(5): 229–269.

Dinges, Alexander. 2021. “Knowledge and Asymmetric Loss.” See the page-checked source passages in E3, especially §4.3.1 and footnote 10.

Hawke, Peter. 2024. “Stable acceptance for mighty knowledge.” *Philosophical Studies*. https://doi.org/10.1007/s11098-024-02103-z.

Hawke, Peter. 2024. “Modal Knowledge for Expressivists.” *Journal of Philosophical Logic*. https://doi.org/10.1007/s10992-024-09759-2.

MacFarlane, John. 2014. *Assessment Sensitivity: Relative Truth and Its Applications*. Oxford University Press.

Rudin, Deniz. 2025 [online 2024]. “Asserting epistemic modals.” *Linguistics and Philosophy* 48: 43–88. https://doi.org/10.1007/s10988-024-09423-7.

### C. Credits by recorded responsibility

The human director designed and directed the scaffold and retained final research and submission decisions. The orchestrator coordinated briefs, assignments and handoffs. The recorded development roster contains 43 workers, all attributed to Codex harnesses; the orchestrator used Claude. Exact per-worker serving-model versions are unrecorded. Roles below summarize contributions across the retained campaign, not current assignments.

| Responsibility | Worker names |
| --- | --- |
| Literature intake, acquisition and comparison | beta, epsilon, eps2 |
| Extraction, grounding and OCR | gamma, kappa, mu, rho2 |
| Source-theory construction and freeze reuse | eta, sigma |
| Resumable execution, argument search and integration | theta, xi, xi2, fwd |
| Live pilots, forks and research runs | alpha, zeta |
| Provider isolation and runtime transport | omega |
| Writing, audit and publication | nu4, pi3 |
| Documentation and methodology | omicron3, meta |
| Evidence retention and workspace operations | janitor |
| Extraction and evidence review | delta, lambda, omicron, pi, rho |
| Construction and lifecycle review | iota, tau, upsilon, phi, chi |
| Transport, resume and OCR review | psi, kappa2, lambda2, tau2 |
| Search, stance and integration review | upsilon2, phi2, kappa3, rho3 |
| Report and documentation review | nu, chi2 |
| Cross-cutting independent review | kappa4, kappa5 |

