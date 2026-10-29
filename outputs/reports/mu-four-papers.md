# Mu: eight-paper range-union acceptance

Round 3 below is the current result: acceptance identity v6, 2,333 retained items, 245 quarantined, and 18 disclosed open gaps. It supersedes Round 2 publication and fixes the review findings. Earlier sections remain historical evidence; v5 references describe the earlier structural-acceptance policy.

**The native live run exited 0: 8/8 papers have accepted range coverage over their readable pages, with 1,156 retained items. Cumulative mu spend is USD11.283435 of the USD15 cap.** Offline salvage covered 7/8 before paid work; all 1,024 offline items remain exactly unchanged by ID in the final outcomes.

This completes implementation and the bounded acceptance experiment. It does **not** establish complete, faithful argument extraction: six half-ranges remain thin, 14 historical open gaps remain disclosed, and 42 items begin with “placeholder”. Another new item has text and attribution both `x`. The strict substantive-content and honest-attribution goal is therefore not fully met by these model outputs. These are limitations for review, not a successful semantic-quality verdict.

Worktree `/home/dev/ara-work/mu`, branch `fix/four-paper-acceptance`, base `0eb85924afeb01aac44e5bc0ca5f2714c6a99823`, final commit `564af513587414617a1888f669bc21f02ba81cc5`. Clean tracked tree; no push or delegation. Original checkout, runs and cache remain read-only. The addendum supersedes the original four-paper scope and blocking reconciliation rule.

## Final live result

| Paper | Offline items | Final items | Inferences | Open gaps | Placeholder-prefix items | New calls | New USD |
|---|---:|---:|---:|---:|---:|---:|---:|
| vonfintelgillies2007 | 64 | 100 | 14 | 2 | 6 | 4 | 0.652680 |
| eganweatherson2011 | 125 | 125 | 26 | 0 | 0 | 0 | 0 |
| vonfintelgillies2011 | 147 | 147 | 30 | 2 | 2 | 0 | 0 |
| schaffer2011 | 113 | 194 | 33 | 3 | 3 | 2 | 1.177035 |
| braun2012 | 97 | 108 | 21 | 2 | 3 | 2 | 0.185715 |
| egan2007 | 158 | 158 | 35 | 1 | 1 | 0 | 0 |
| yalcin2011 | 83 | 85 | 0 | 1 | 21 | 2 | 0.173055 |
| moss2015 | 237 | 239 | 54 | 3 | 6 | 2 | 0.144295 |
| **Total** | **1,024** | **1,156** | **213** | **14** | **42** | **12** | **2.332780** |

Six statuses are `extracted`; Schaffer and Braun retain `partial` source diagnostics for unread visual pages and encoding warnings. No readable page remains outside accepted range coverage. Coverage describes the accepted input ranges, not evidence on every page or semantic completeness. In particular, a one-item response can cover a long input range without representing its argument structure.

Final native artifact: `/home/dev/ara-work/mu/runs/mu-eight-live/literature.extracted.txt`, with adjacent `.provenance.json`; methodology: `runs/mu-eight-live/export/methodology.md`. Pinned ancestry and artifact provenance passed. All 12 dispatches have matching MODEL responses; zero new unknown-usage reservations. Native elapsed time was 1,322.596 seconds, including ancestry import. Evidence: `runs/mu-control/eight-{command.json,config.yaml,started.json,receipt.json,summary.json,retention.json}` and `summarize-eight.py`.

Offline artifact: `runs/mu-salvage-check/literature.extracted.txt`, published without provider calls and checked with sockets blocked. Seven papers already covered every readable page; Schaffer retained 113 items but lacked pages 26–49. The final run fills that missing range and attempts the four remaining thin ranges once each, split into halves. The initial offline artifact flagged the 2011 range 12–23 as thin; 62 already-accepted review additions actually filled it. The final implementation recognizes them and avoided two paid repeat calls. The 132 added items include non-substantive outputs and must not all be described as useful evidence.

## Diagnosis and changes

**Cause: mixed model output and validator/reconciliation policy; no demonstrated causal PDF-extractor defect.**

- `vonfintelgillies2007`: reversed physical endpoints 19–18 and earlier inconsistent coverage flags. The original mu live run then failed during reconciliation after accepted placeholder ranges, wrong root source ID and attempts to redeclare immutable evidence.
- `eganweatherson2011`: Pass A emitted placeholder qualification/distinction items followed by 63 distinctions/qualifications with no inference edges. This was not a reconstructed-origin rejection. The first mu live run accepted 125 items, including 26 paper-stated inferences.
- `vonfintelgillies2011`: Pass A emitted 87 proposition/view items, including 41 intermediate conclusions, without inference edges. The first mu run preserved an 84-item range and a one-item range, then accepted 62 review additions before a remaining-obligation budget reservation stopped completion.
- `schaffer2011`: duplicate identical correction IDs; an earlier qualification-kind error also remained. V4 retained 113 accepted items and two open obligations, but did not cover pages 26–49.
- `braun2012`, `egan2007`, `yalcin2011`: A2 retained useful ranges but failed with `max_tokens` at the joined/recovery stage. Braun and Yalcin also had one-item long ranges.
- `moss2015`: A2 retained 237 range items. Reconciliation/recovery encountered context-request and duplicate-ID errors, ending with `candidate cannot support targeted correction`; A2 used 544,140 input tokens on this paper.

Round 1 acceptance v5 allowed explicitly labelled reconstructed inferences, deterministically sorted reversed endpoints, stably renamed duplicate correction IDs while retaining every item, refused ambiguous distinct duplicate references, and permitted three targeted corrections per range response. No proposition is converted into a guessed inference.

The addendum makes paper acceptance the union of accepted range graphs. Reconciliation gets one complete, counted request, with no correction, context-fetch or obligation queue. Accepted review additions survive; failure and open obligations are disclosed. A subsequent range failure also preserves earlier accepted ranges, marking uncovered readable pages as partial. Zero inference coverage without a source-based disposition is disclosed as unverified. Conflicting retained absence dispositions and overlapping paper-stated inferences are flagged.

A range is thin at eight or more readable pages with at most `max(1, floor(pages/10))` items. This catches the observed 20- and 26-page one-item ranges. Before paying, accepted review/range additions are counted over its pages. A remaining thin range gets one split re-extraction; original items remain, and residual thinness or retry failure is disclosed. Historical retry receipts prevent another retry.

Salvage reconstructs accepted graphs from pinned original MODEL receipts, verifies source PDF and page text, profile and reviewed prompt contracts, then runs native graph validation. Rejected responses are never promoted. Distinct attempts receive deterministic receipt namespaces, preserving content and references. Unsupported predecessor contracts remain excluded with reasons. `--salvage-only` constructs no generation-capable provider.

Native `--exclude-paper ID=REASON` publishes available but excluded sources without claims. Stopped batches publish failed/not-extracted rosters before returning their original failure. Rosters, dispositions and open gaps flow into methodology and construction inputs. Default failed-paper allowance is eight; monetary/token admission still bounds generation. DECISIONS.md and the extraction prompt document the policy.

## PDF and replay evidence

Production pypdf **6.21.1** was compared with separately locked pdfminer.six **20250506** across **125 physical pages** in the original four papers. No demonstrated text-order cause warranted an extractor switch. Pdfminer lost word spacing in the 2007 PDF. Header, hyphenation and font artifacts remain; Schaffer page 1 has no extracted text in either extractor. No OCR or silent source replacement occurred. Reproduction: `runs/mu-textcheck/{pyproject.toml,uv.lock,check.py}` and `runs/mu-control/locked-text-verification.json`.

| Same 59 recorded responses | Base | Pre-addendum v5 | Final union policy |
|---|---:|---:|---:|
| Accepted without normalization | 3 | 3 | 5 |
| Accepted after normalization | 17 | 20 | 30 |
| Needs correction | 30 | 33 | 21 |
| Needs subdivision | 2 | 2 | 2 |
| Terminal | 7 | 1 | 1 |

Immediate acceptance is **20/59 → 23/59 → 35/59**. These are response-level results, not completed-paper predictions. The remaining terminal response is a provider refusal. Eleven imported grammar receipts and one receipt without a provider body are explicitly excluded. Exact base archive: `runs/mu-baseline-code/`; final replay: `runs/mu-replay-union/summary.json`. No philosophical source content was committed.

## Reuse and evidence quality

In Round 1, all seven A2 completions were reusable under v5 without provider calls: **1,093 items**. Per-paper counts are in `runs/mu-control/v4-current-reuse.json`; `v4-union-reuse.txt` records the socket-blocked check. Original outcomes remain v4; migration is a separate receipt. The 14 migration receipts are cumulative (seven original plus seven new), not 14 papers.

The eight-paper offline union contained 30 literal placeholder-prefix items. The final union contains **42**, distributed in the live table. The seven legacy completed graphs separately contain 12 such items across five papers. The prefix screen is not an exhaustive semantic audit. Yalcin's new range 20–28 contains only `placeholder`; its new range 29–38 contains only `x`, attributed to `x`, which the prefix screen misses. Presence of a nonempty attribution field does not establish honest attribution. Preservation of accepted history does not make these outputs faithful source claims.

Six half-ranges remain thin after the single authorized split attempt: **vonfintelgillies2007 17–24; braun2012 1–13; yalcin2011 20–28 and 29–38; moss2015 41–50 and 51–60.** No further retry was made. Yalcin still has zero inference nodes and carries `inference_coverage_unverified`. The 2007 graph retains a historical no-explicit-structure disposition that conflicts with accepted paper-stated inferences; `inference_disposition_conflict` discloses it. These dispositions appear in both the final artifact and methodology.

The introduction's five earlier sampled citations (`n1`, `p5`, `inf11`, `p21`, `r16`; physical pages 1, 3, 8, 13, 19) were supported by the cited passages. Three new live samples were supported: 2007 `q_monotonic` on physical page 25, Schaffer `p_binding_test` on page 26, and Braun `pr_ctx_params_given` on page 14. Audit: `runs/mu-control/eight-fidelity-audit.json`. This is spot-check evidence only, not verification of all items, citations, attributions, or inference links.

### Retained open-gap inventory

The following summarizes all 14 disclosed obligations. They are historical, range-local model reports retained without deletion; some describe earlier input windows and are partly superseded by later additions. They have not been independently closed, and should not be read as fresh assertions that the final union has no corresponding evidence. Exact text remains in the final artifact and methodology.

| Paper | Gaps | Retained issues requiring assessment before a completeness claim |
|---|---:|---|
| vonfintelgillies2007 | 2 | Earlier review received no page text; its then-placeholder-only inventory could not represent the paper. Later additions change that inventory but do not formally close the reports. |
| vonfintelgillies2011 | 2 | Placeholder/superseded inference and qualification nodes in pages 1–11; an earlier review lacked page text for 12–23, later supplemented by 62 accepted items. |
| schaffer2011 | 3 | Range-local gaps for disagreement arguments, arguments against non-cognitivism, and earlier framework/linguistic-test premises. The newly filled range does not automatically resolve cross-range links. |
| braun2012 | 2 | Foundational argument structure in 1–26 was represented by a placeholder; new additions only partly address it. No retained items cite pages after 45 despite accepted input coverage through 52. |
| egan2007 | 1 | Fuller arguments attributed to cited external works are outside the supplied paper. This is a source-scope limit, not necessarily an extraction defect. |
| yalcin2011 | 1 | Later development of the question-sensitive model was outside the earlier input range; new one-item responses do not supply substantive coverage. |
| moss2015 | 3 | Missing argument structure in 41–60; placeholder/boilerplate introductory material and missing introductory inference; missing cross-range inference to the main thesis. |

No construction, freeze, route search or philosophical pilot ran. The next review must distinguish the verified acceptance/provenance behavior from the unresolved substantive quality of the retained model outputs.

## Native publication proof

`runs/mu-roster-proof/literature.extracted.txt` was published through the native CLI with `--salvage-only` and an explicit `--exclude-paper` reason for the available book. The full manifest contains **53 records**, of which 26 have available PDFs. The proof publishes **16 nonempty paper graphs / 2,201 items** and an explicit **37-entry roster**: one excluded book, nine available but not extracted papers, and 27 record-only entries. Besides the eight task papers and seven compatible completions, it salvages an existing 84-item partial range for `kolodnymacfarlane2010` from verified ancestry.

Pinned artifact provenance passed; the methodology roster exactly matches the literature roster; **zero new MODEL receipts** occurred. Evidence: `runs/mu-control/roster-proof-summary.json` and `roster-proof-verification.txt`. This is a pre-live disclosure proof, not the final improved corpus or a pilot. Schaffer's missing range in this artifact is subsequently addressed by the separate eight-paper live run.

## Accounting

| Quantity | USD |
|---|---:|
| External inherited campaign, including A2 | 51.878975 |
| Mu schema gate, 5/5 grammars | 0.046880 |
| Original mu four-paper extraction, 20 responses | 8.903775 |
| Schaffer follow-up: stopped before dispatch | 0.000000 |
| Addendum eight-paper live check, 12 responses | 2.332780 |
| **Cumulative mu spend** | **11.283435** |
| Native aggregate accounting | **63.162410** |
| Native aggregate cap | **66.878975** |
| Unspent cumulative mu allowance | **3.716565** |

The USD15 limit is cumulative mu spend, not another USD15. A2's USD25.006110 is external inherited spend. Historical unknown usage remains charged at USD0.897910 reservation in inherited accounting, distinct from measured spend; no invoice reconciliation is claimed. There are zero new unknown-usage reservations. The schema did not change in the addendum, so the prior USD0.046880 live gate remains applicable. The original four-paper command exited 2 with one completion; the independent Schaffer follow-up added no charge. The final eight-paper command exited 0. No further paid work is pending or authorized by this report.

## Verification and handoff

Final full pytest: **532 passed, 2 skipped / 534**. The skips are opt-in paid-provider checks. Transcript: `runs/mu-control/addendum-final-pytest.txt`. All **225/225 production mutations** failed with exit 1 and passed with exit 0 after restoration, run sequentially after pytest. Transcripts: `runs/mu-control/addendum-final-controls.txt` and `runs/mu-control/addendum-controls-results.json`; supervisor receipt: `runs/mu-control/addendum-verification.json`.

Commit `564af513587414617a1888f669bc21f02ba81cc5` contains the verified implementation. The live launcher checked the clean committed tree and successful verification before generation. Only ignored evidence and the external report were updated afterward. The initial offline inventory harness had a tuple/list comparison mismatch; it was corrected and the check rerun successfully. The old failure is preserved in `runs/mu-control/salvage-check-before-comparison-fix.txt`; successful evidence is in `salvage-inventory.json` and `salvage-publication.json`.

No push or non-author review has occurred. The requested short non-author review is the next step before merge; this report does not claim merge readiness or semantic-quality completion. The earlier chronological working record is preserved as `/home/dev/ara-work/reports/mu-four-papers-work-journal.md`; current continuation notes are `runs/mu-control/checkpoint-addendum.md`.

## Finding placement

This table reconciles actionable findings from the working record, commit scope, and final evidence. Historical failures whose outcomes changed are identified as such in their destination sections.

| # | Finding | Report section carrying it |
|---|---|---|
| 1 | Failures came from mixed model output and validator/reconciliation policy; original per-paper causes differ | Diagnosis and changes |
| 2 | No demonstrated causal extractor defect; spacing/encoding/unread-page limitations remain | PDF and replay evidence; Final live result |
| 3 | Union acceptance, bounded review and preserved additions change acceptance semantics | Diagnosis and changes |
| 4 | Replay improves response acceptance, not proof of paper completion | PDF and replay evidence |
| 5 | Seven papers salvaged offline; one missing range filled; all 1,024 prior items preserved | Final live result |
| 6 | Accepted review evidence fills the 2011 thin-range inventory and avoids paid retry | Final live result |
| 7 | Eight accepted graphs include two partial source statuses; range coverage is not semantic completeness | Final live result |
| 8 | Six half-ranges remain thin after the one split retry | Reuse and evidence quality |
| 9 | Final 42 placeholder-prefix items, baseline 30 and separate legacy 12 limit fidelity claims | Reuse and evidence quality |
| 10 | Yalcin's additional x/x item defeats substantive content and attribution; zero inference nodes remain | Reuse and evidence quality |
| 11 | 2007 no-structure disposition conflicts with accepted inferences | Reuse and evidence quality |
| 12 | All 14 historical obligations remain open, some stale or source-limited | Retained open-gap inventory |
| 13 | Citation fidelity was only sampled; no full semantic audit or downstream pilot | Reuse and evidence quality |
| 14 | Seven v4 completions remain reusable; migration counts are cumulative | Reuse and evidence quality |
| 15 | Full manifest has 53 records, not 26; 37 explicit roster entries; proof is pre-live | Native publication proof |
| 16 | Final spend is within cumulative USD15; inherited unknown reservation is distinct; no invoice claim | Accounting |
| 17 | Final tests and controls passed; earlier inventory comparison failure was repaired | Verification and handoff |
| 18 | Local commit only; non-author review remains before merge | Verification and handoff |

18 findings, 18 placed.


## Round 2 — offline grounding and quarantine

**Published: 245/2,333 retained items quarantined across 16 paper graphs; 2,088 eligible under the lexical gate.** The quarantine consists of 200 direct flags and 45 dependent items. The 16 graphs comprise the eight task papers, all seven legacy v4 completions, and the previously salvaged partial graph. No source item is removed or rewritten. No paper was re-extracted.

Current artifact: `/home/dev/ara-work/mu/runs/mu-round2-offline/literature.extracted.txt`, with its adjacent provenance sidecar and `export/methodology.md`. Original item bodies remain in `items` for audit. The separate `quarantined` inventory explicitly marks excluded IDs, reasons, overlap metrics and dependencies. Native citation lookup and construction filter this inventory; old artifacts without grounding or modified inventories are refused before supplying T.

### Round 2 root cause and changes

The historical receipt scan found 80 responses containing the screened junk patterns: 47 initial, 25 targeted corrections, and eight reconciliations; 30 had been structurally accepted and 50 rejected. This shows that correction pressure alone does not explain the outputs. No positive filler example, content default, or universal nonempty-array quota was found in the reviewed extraction prompt/schema. The nonempty branch has `minItems=1`, but there is a separate empty disposition.

Three concrete defects were addressed:

- The prompt described `items=[]` for an empty initial range, while its wire grammar requires `items=null`. The prompt now explicitly explains null-to-empty normalization and forbids filling the nonempty branch merely to satisfy the grammar.
- The displayed local schema required fields that the wire-shape instructions told the model to omit. Its heading now explicitly states that local constraints apply after runtime completion of omitted edge fields. Wording echoed as schema boilerplate in an observed item was removed, and item text must exclude serialization instructions.
- Corrections could not discard unsupported rejected candidate items. The new optional `discard_items` field takes candidate IDs and reasons. It cannot discard immutable accepted evidence, cannot both discard and replace an ID, and cannot leave dangling references. Discards are logged. An all-discarded no-content candidate can use the empty disposition. Separately, shape-only acceptance no longer makes an item eligible as evidence: the deterministic gate applies to new publication and offline reuse, including reviewed v4/v5 contracts.

These are observed contract defects and acceptance gaps, not proof of the model's internal motivation. The revised prompt's effect on extraction quality was not measured with new extraction calls. Acceptance identity is v6; original historical identities and receipts remain intact.

### Round 2 grounding policy and calibration

The gate uses only the item's cited readable physical pages. It applies Unicode NFKC, case folding, line-end dehyphenation, alphabetic tokenization and a versioned English function-word exclusion set. At least **50% of distinct content tokens** must occur on the cited pages, with at least **three distinct matches**, or all content tokens when fewer than three exist. No anchor field was added: historical items lack anchors, so their unchanged text is checked directly.

Independent junk rules quarantine template prefixes, one/two-character text, text equal to its attribution, and nonword text. Reference dependencies are quarantined transitively, including inference links constrained by quarantined qualifiers. A resolution depending on quarantined evidence no longer closes an open gap. Decisions and source/inventory/policy hashes are logged and disclosed downstream.

| Candidate overlap threshold | Directly flagged items, before dependency propagation |
|---|---:|
| 35% | 116 |
| 40% | 132 |
| **50%** | **200** |
| 60% | 336 |
| 70% | 590 |

The 50% threshold requires at least half the content vocabulary without the much larger loss at 60–70%. In the inspected boundary cases, it excludes a contaminated item that 40% would admit while retaining four supported items that 60% would reject. It is deliberately conservative. In an intentionally selected boundary sample, **three of four items just below 50% were supported paraphrases** and therefore false positives; the fourth contained schema boilerplate. **All four samples at 50% were supported.** This is not a random sample or a population false-positive estimate. No sample was exempted from the deterministic policy. Anonymized token examples and verdicts are in `runs/mu-round2/anonymized-spot-check.json`; calibration receipts are under `runs/mu-round2/`.

Lexical overlap does not establish entailment, completeness, or the truth of an attribution. Supported paraphrases can fail; unsupported claims using source vocabulary can pass. Quarantine records preserve material for review without letting it supply evidence. Earlier thin ranges, unread-page/encoding diagnostics, and inference-coverage limits remain relevant; this offline gate does not repair those gaps.

### Round 2 per-paper inventory

| Paper | Retained | Direct flags | Dependency flags | Quarantined | Eligible |
|---|---:|---:|---:|---:|---:|
| vonfintelgillies2007 | 100 | 18 | 3 | 21 | 79 |
| eganweatherson2011 | 125 | 8 | 2 | 10 | 115 |
| vonfintelgillies2011 | 147 | 12 | 1 | 13 | 134 |
| wright2007 | 105 | 9 | 8 | 17 | 88 |
| schaffer2011 | 194 | 10 | 11 | 21 | 173 |
| braun2012 | 108 | 22 | 9 | 31 | 77 |
| eganhawthorneweatherson2005 | 213 | 14 | 0 | 14 | 199 |
| egan2007 | 158 | 10 | 2 | 12 | 146 |
| macfarlane2011 | 169 | 12 | 5 | 17 | 152 |
| yalcin2007 | 210 | 9 | 1 | 10 | 200 |
| yalcin2011 | 85 | 22 | 0 | 22 | 63 |
| rothschild2012 | 71 | 1 | 0 | 1 | 70 |
| moss2015 | 239 | 11 | 0 | 11 | 228 |
| veltman1996 | 267 | 31 | 0 | 31 | 236 |
| kolodnymacfarlane2010 | 84 | 10 | 3 | 13 | 71 |
| knobeyalcin2014 | 58 | 1 | 0 | 1 | 57 |
| **Total** | **2,333** | **200** | **45** | **245** | **2,088** |

### Round 2 verification and remaining limits

Final full pytest: **548 passed, two skipped / 550**. The skips remain opt-in provider tests. The first diagnostic full run had six obsolete schema-heading parser assertions; they were corrected and their owning cases passed before the final run. Test fixtures use longer symbolic text with matching source tokens and traverse the production gate; there is no provider or fixture exemption. All **234/234 mutation controls** produced exit 1 under mutation and exit 0 after restoration, run sequentially after pytest. The source snapshot was unchanged across final verification. Evidence: `runs/mu-round2/final-pytest.txt`, `final-controls.txt`, `verification.json`, `controls-results.json` and `verified-source.json`. No separate lint/typecheck is configured; `git diff --check` passed.

The independent socket-blocked check verified native artifact provenance, recomputed every quarantine decision against the physical page text, and confirmed all **2,333 originals remain exactly equal by ID**. All **57 literal placeholder-prefix items** are excluded: 42 from the eight task papers, 12 from legacy completions, and three from the additional partial graph. The new one-character/text-equals-attribution item is also quarantined. The 200 direct flags comprise 132 insufficient-overlap items, 67 template-prefix items (including superseded markers), and one short item also equal to its attribution; 45 additional items are quarantined through dependencies. The full manifest remains 53 records with 37 explicit roster entries, matching the methodology. **Zero new MODEL calls and USD0** were used for revalidation. Evidence: `runs/mu-round2/offline-summary.json`, `offline-verification.txt` and `verify-offline.py`.

The live schema preflight passed **6/6 distinct grammars**, with six dispatches matched to six responses and no new unknown-usage reservations. Cost was **USD0.065350**, below the explicit USD0.25 exception. This tests wire compilation, not substantive extraction quality. There were no paid extraction calls in Round 2. Cumulative mu spend including this gate is **USD11.348785**. Evidence: `runs/mu-round2/gate-{command,started,receipt,summary}.json` and `runs/mu-round2-schema-gate/events.jsonl`.

Final local commit: **`95be49ad754f1dd113191486e6946749d5f9a2c0`**, on `fix/four-paper-acceptance`, with a clean tracked tree. The paid gate ran at this exact commit after verification. No push or delegation occurred. The requested non-author review remains next before merge. No construction, freeze, route search or philosophical pilot was run on the real corpus; offline native tests verified the exclusion from T. The earlier fidelity and coverage limits remain disclosed, with quarantine adding an enforced eligibility boundary rather than a semantic-completeness claim.

### Round 2 finding placement

| # | Finding | Report section carrying it |
|---|---|---|
| 19 | Empty-wire and post-normalization instructions conflicted; no universal nonempty quota or positive filler default found | Round 2 root cause and changes |
| 20 | Unsupported rejected candidates could not be discarded; explicit bounded discard semantics now exist | Round 2 root cause and changes |
| 21 | Threshold calibration and sampled false positives require a conservative lexical-only interpretation | Round 2 grounding policy and calibration |
| 22 | All 57 literal-prefix items and the short attribution-equal item are excluded; direct reasons are counted | Round 2 verification and remaining limits |
| 23 | Dependency quarantine excludes 45 more items, and affected gap resolutions cannot remain closed | Round 2 grounding policy and calibration; Round 2 verification and remaining limits |
| 24 | All 16 graphs, including legacy completions, are revalidated with all 2,333 originals unchanged and no extraction spend | Round 2 per-paper inventory; Round 2 verification and remaining limits |
| 25 | Ungrounded/modified inventories cannot supply citations or T; real-corpus downstream pilot remains unexecuted | Round 2 opening; Round 2 verification and remaining limits |
| 26 | Prompt effectiveness is unmeasured; six live grammar checks establish wire validity only | Round 2 root cause and changes; Round 2 verification and remaining limits |
| 27 | Final 548/550 test result and 234 controls supersede diagnostic failures; source snapshot is stable | Round 2 verification and remaining limits |
| 28 | Only the bounded gate incurred Round 2 spend; final commit is local and non-author review remains | Round 2 verification and remaining limits |

28 findings, 28 placed (18 historical findings above and 10 Round 2 findings).

## Round 3

Round 3 fixes omicron B1, B2 and S2. The current acceptance identity is **v6**.
V5 relaxed structural admission; v6 additionally restricts evidence eligibility
through quarantine. Original v4/v5 identities and receipts remain preserved.

### Round 3 snapshot retention and publication

Offline completed-snapshot replacement now requires every previously accepted
item ID and body to survive exactly, including citations and references. A
smaller, disjoint or conflicting snapshot refuses explicitly before provenance
import. A larger snapshot preserving all earlier evidence remains usable. A
smaller snapshot encountered after a larger one refuses rather than silently
choosing it; callers must resolve conflicting ancestry explicitly. Ordinary
resume retains its stricter differing-outcome check. Grounding and publication
metadata upgrades alone do not create a false conflict.

New publications carry a versioned `quarantine-aware-v1` marker. Revalidated
legacy outcomes now disclose dispositions and quarantine-aware open gaps in both
literature and methodology. Historical unmarked outcomes retain their original
serialization for exact hash verification. Original acceptance identities are
unchanged. Native regression coverage includes ungated legacy reuse, previously
grounded legacy reuse, republication and a second resume, with zero dispatches.

The README now permits 0, 1, 2 or 3 targeted corrections. Current artifact usage
text consistently permits paper-stated or reconstructed inference links; neither
is an engine license. Old wording is retained only when reconstructing historical
artifact bytes. No prompt, schema or grounding threshold changed in this round.

### Round 3 artifact and verification

**Final artifact: 2,333 retained items, 245 quarantined, 2,088 eligible, and 18 open gaps.**
The 245 quarantines comprise 200 direct flags and 45 dependent exclusions.
All original bodies remain exactly equal by ID. There are 53 manifest records,
16 nonempty graphs and 37 explicit roster entries, with matching methodology.
The gap count is **18 rather than round 2's published 16**: `yalcin2007` now
shows the two resolutions reopened by quarantined evidence. No new source
content was generated to close those gaps.

Current artifact: [literature.extracted.txt](/home/dev/ara-work/mu/runs/mu-round3-final-offline/literature.extracted.txt).
Adjacent [provenance sidecar](/home/dev/ara-work/mu/runs/mu-round3-final-offline/literature.extracted.provenance.json)
and [methodology](/home/dev/ara-work/mu/runs/mu-round3-final-offline/export/methodology.md).
Native publication ran at **`514bae3ade119ae03533a00a3b976a01086aa1cd`**, exited 0, and took
**1112.00 seconds**, including append-only ancestry import. Its command
and exact head are recorded in `runs/mu-round3/publication-final-receipt.json`.

| Paper | Retained | Quarantined | Open gaps |
|---|---:|---:|---:|
| vonfintelgillies2007 | 100 | 21 | 2 |
| eganweatherson2011 | 125 | 10 | 0 |
| vonfintelgillies2011 | 147 | 13 | 2 |
| wright2007 | 105 | 17 | 0 |
| schaffer2011 | 194 | 21 | 3 |
| braun2012 | 108 | 31 | 2 |
| eganhawthorneweatherson2005 | 213 | 14 | 0 |
| egan2007 | 158 | 12 | 2 |
| macfarlane2011 | 169 | 17 | 0 |
| yalcin2007 | 210 | 10 | 2 |
| yalcin2011 | 85 | 22 | 1 |
| rothschild2012 | 71 | 1 | 0 |
| moss2015 | 239 | 11 | 3 |
| veltman1996 | 267 | 31 | 0 |
| kolodnymacfarlane2010 | 84 | 13 | 1 |
| knobeyalcin2014 | 58 | 1 | 0 |
| **Total** | **2,333** | **245** | **18** |

Full pytest passed **554 tests, two skipped / 556** (263.93 seconds). The skips
are opt-in provider checks. The control runner then passed **237/237 mutations**:
every mutated test returned exit 1 and every restored test returned exit 0
(708.07 seconds). Source hashes remained identical across both checks and match
the final commit. `git diff --check` passed; the tracked worktree is clean.
No separate lint/typecheck command is configured. Evidence:
`runs/mu-round3/final-pytest.txt`, `final-controls.txt`, `verification.json`,
`controls-results.json` and `verified-source.json`.

The new regressions first reproduced five failures: three destructive snapshot
replacements were admitted and two legacy publications omitted reopened gaps.
After the fixes, all 37 targeted cases passed. The new controls independently
remove snapshot retention, legacy literature disclosure and legacy methodology
disclosure, then restore each boundary. Legacy tests execute reuse, republication
and a second resume for both ungated and previously grounded historical shapes;
original item bodies, identities and historical artifact verification survive.
Evidence: `regressions-before.txt`, `targeted.txt` and the three new controls'
red/green transcripts under `runs/mu-round3/`.

The final socket-blocked audit passed pinned provenance verification, exact
retention against pre-grounding artifacts, physical-page quarantine recomputation,
dependency exclusion, gap/disposition agreement with methodology, roster equality,
and current-contract reuse validation for **all 16 graphs**. It confirms
**zero new MODEL calls and USD0 local cost**. All 57 literal placeholder-prefix
items remain excluded. Historical `mu-roster-proof`, `mu-eight-live` and
`mu-round2-offline` artifacts still pass exact hash/provenance verification.
The second-resume proof is the native regression test; no second full-corpus
publication is claimed. Evidence: `verify-final-offline.py`,
`offline-final-verification.txt`, `offline-summary.json` and
`historical-verification.txt` under `runs/mu-round3/`.


### Round 3 historical contract drift and recovery

The first native publication resumed directly from `runs/mu-round2-offline` and
exited 0, but the independent retention audit refused delivery: **2,249 items,
232 quarantined, 17 gaps**. It omitted the 84-item partial graph. That graph's
round-2 acceptance identity is v6 with intermediate prompt hash
`76d38f9c8625ff434f57b992304cc18a6c127439d74ace1c8fbb25613a6cad45`, while the
final round-2/current prompt hash is
`daffa0afc225ce8aa6809b7fea7f1d8078f9e0afcc0c8a0b02431638703bdd33`.
Completed-outcome validation correctly refuses that unreviewed intermediate
contract; the version string alone does not establish compatibility. The other
15 graphs carry reviewed v4/v5 predecessor identities. This historical drift was
not caused by the round-3 source changes. Direct completed-outcome resume from
that round-2 artifact is therefore insufficient for the full corpus.

Recovery uses the native accepted-range salvage path from the original verified
`runs/mu-eight-live` ancestry, the same input used by round 2. A socket-blocked
precheck independently reconstructed both accepted ranges and all **84 original
IDs and bodies exactly** under the current validator. No contract allowlist,
source evidence, acceptance rule or prompt was changed to admit them. The final
publication reported above supersedes the incomplete diagnostic run and binds the partial
graph to the current v6 contract. Every final nonempty outcome is also checked
for current-contract reuse compatibility.

The first artifact remains at `runs/mu-round3-offline` as diagnostic evidence and
**must not be used as the final corpus**. Evidence: `publication-receipt.json`,
`offline-verification.txt`, `check-partial-lineage.py`, and
`partial-lineage-check.txt`, all under `runs/mu-round3/`.

### Round 3 scope and remaining limits

B3 shared-frozen compatibility is owned elsewhere; S1 concerns the merged tree.
Neither was changed or retested here. This branch's result is not a merged-tree
or shared-frozen-T readiness claim. The lexical gate's false-positive and semantic
limits, thin ranges, source diagnostics and zero eligible inferences in the
previously identified paper remain. There was no new real-corpus construction,
freeze, search or semantic audit.

No paid calls, push or delegation occurred. Round 3 spend is USD0; cumulative mu
spend remains USD11.348785. Omicron supplied the independent review being fixed.
The new diff received an author review; no additional independent review was
run under the no-delegation constraint. Evidence: `runs/mu-round3/review.md`.

### Round 3 finding placement

| # | Finding | Report section carrying it |
|---|---|---|
| 29 | B1 destructive completed-snapshot replacement now refuses; monotonic growth remains reusable and ordering is explicit | Round 3 snapshot retention and publication |
| 30 | B2 legacy quarantine gaps and dispositions now appear in literature and methodology; two gaps were previously hidden | Round 3 snapshot retention and publication; Round 3 artifact and verification |
| 31 | Versioned republication preserves historical hashes, original identities and a second resume | Round 3 snapshot retention and publication; Round 3 artifact and verification |
| 32 | S2 correction-count and inference-origin wording corrected; current identity is v6 | Round 3 opening; Round 3 snapshot retention and publication |
| 33 | Stable-source full tests, controls and new-head offline retention/quarantine/gap counts establish the branch result | Round 3 artifact and verification |
| 34 | B3/S1 remain outside scope; semantic and shared-frozen proof limits persist; no new spend, push, delegation or independent rereview | Round 3 scope and remaining limits |
| 35 | Intermediate v6 prompt drift disqualified one round-2 partial outcome; first publication failed retention audit; original accepted receipts restore exact inventory under the current contract | Round 3 historical contract drift and recovery |

35 findings, 35 placed (28 historical findings and seven Round 3 findings).

## Round 4 — completed-snapshot union and overnight publication

Round 4 starts from `070efb7bc5ed83d7b5528a42813a57b388751eb2` on
`fix/four-paper-acceptance`; the worktree was fast-forwarded from the round-3
commit before editing. The final round-4 commit is `9d4ec86595f7c46d5ba6d6f9747d86d50533246a`. Acceptance
remains **v6**. The new union representation is independently versioned as
`completed-snapshot-union-v1`; prompts, response schemas and grounding thresholds
are unchanged.

### Round 4 root cause

Pass A did not generate four new versions through paid extraction. Ordinary
`resume_papers` skipped completed outcomes carrying `thin_range` or
`unextracted_pages` dispositions. The four affected papers had already exhausted
their bounded thin-range retry. Fallback salvage reconstructed them from accepted
range receipts, adding receipt namespaces to formerly native IDs. There were no
new MODEL calls for these four papers. The retained prior outcomes carry original
**v5** identities revalidated/grounded under v6; calling them newly generated v6
snapshots would misdescribe the receipts.

| Paper | Original / overnight items | Renamed IDs |
|---|---:|---:|
| vonfintelgillies2007 | 100 / 100 | 36 |
| braun2012 | 108 / 108 | 11 |
| yalcin2011 | 85 / 85 | 2 |
| moss2015 | 239 / 239 | 2 |

An explicit old-to-new mapping proves **all 532 original item bodies and their
links unchanged**, allowing only the ID/citation/reference renaming. Fifty of the
51 renamed items match literally after removing ID/citation; the remaining item
also references a renamed endpoint. The 51 missing IDs therefore reflect a
resume-selection and namespace-reconstruction defect, not lost model output or
fresh content. Evidence: `runs/mu-round4/root-cause.json` and
`runs/mu-round4/id-mapping-proof.json`.

Ordinary resume now reuses validated completed snapshots, including disclosed
thin and partial ones, directly. It preserves their limitations and IDs instead
of automatically rebuilding them. Accepted range salvage remains available when
there is no compatible completed snapshot.

### Round 4 union, provenance and quarantine

The round-3 non-monotonic replacement refusal is superseded by a lossless union
of all compatible, verified original completed snapshots. Every source and
acceptance identity and accepted-graph receipt is checked before destination
import. Each union item has a stable namespace and per-item provenance containing
original snapshot ID, original item ID, body hash and citation. The snapshot
manifest retains graph hash, original acceptance identity and verified checkpoint
pins; full original bodies remain in unchanged ancestry.

Only identical original ID/body pairs may share a published item. Different
original IDs survive even if their text is identical. ID collisions with different
bodies, and reference contexts dependent on those collisions, receive full
snapshot-qualified IDs. All references and citations are mapped consistently.
An incoming qualifier with a different body, or present only in one snapshot,
requires its inference to remain separate too. Both cases initially failed
production-path tests and now pass; the bad qualifier and dependent inference
cannot quarantine the other snapshot's version.

Obligations and resolutions stay snapshot-scoped, and dispositions identify their
snapshot. A valid resolution in one version cannot close a quarantined resolution's
gap in another. Grounding is recomputed on the complete union. Derived union
outcomes are not added as new originals on a second resume: every named original
must remain in verified ancestry, and rebuilding must reproduce the graph and
per-item provenance. Synthetic tests cover both source orders, smaller/larger,
disjoint/conflicting snapshots and a second resume, without provider dispatch.
A forged derived graph with a self-consistent log/graph receipt is rejected when
its originals do not reproduce it.

### Round 4 reconciliation overflow

For `hollidaymandelkern2024`, the logged input count was **220,721**, plus a
**32,000** output allowance against a **200,000** context bound. The runtime
logged `extraction_reconciliation_failed`, retained **382 items**, and recorded
an `extracted` outcome. Its bounded review failure did not kill the paper. The
subsequent operator interruption stopped the paid overnight run under that run's
cap-stop instruction; it should not be mistaken for an uncaught reconciliation
failure.

A native two-paper test injects the same overflow into reconciliation: the first
paper publishes its 16 range items, the next publishes 8, the failure is disclosed,
and no reconciliation request reaches provider completion. Its negative control
rethrows the error and makes the test fail. No window splitting was added:
splitting a complete graph/source review would require new cross-window evidence
and obligation semantics plus extra calls. The existing single bounded,
best-effort pass is retained.

### Round 4 artifact and verification

Native offline publication succeeded from the clean committed head in **2512.1
seconds**, exit **0**. The invocation used `ara extract --salvage-only` with the
saved overnight publication arguments, the local copied configuration/cache, and
`--resume-from /home/dev/ara-scaffold/runs/overnight-extraction-a`. That log contains
the verified full prior chain; it is not a latest-batch-only inventory. Network
connections were blocked in the wrapper, and native salvage used its offline
provider. There were **zero local MODEL calls and USD0 new cost**.

- Literature: `/home/dev/ara-work/mu/runs/mu-round4-offline/literature.extracted.txt`
- Native methodology: `/home/dev/ara-work/mu/runs/mu-round4-offline/export/methodology.md`
- Exact head/arguments/timing/exit: `runs/mu-round4/publication-receipt.json`
- Artifact audit: `runs/mu-round4/audit.py`, `audit-summary.json`, and `audit.txt`
- Historical serialization check: `runs/mu-round4/historical-artifact-verification.json`

The final artifact contains **26 records: 22 nonempty graphs and four explicit
exclusions**, with **3,724 retained items, 317 quarantined, 3,407 eligible items,
and 46 open gaps**. The audit verified pinned transitive provenance, every
compatible original snapshot and item body/reference mapping, generated citations,
current-contract reuse, grounding recomputed from cited physical-page text, and
agreement between literature and methodology on gaps, dispositions, quarantine
and union manifests. The prior round-3 artifact still verifies against its original
hash and pinned provenance. Final artifact SHA-256: `c6f5db583c22f8b3685c31e4af4c2199efcf6e71f7550c53022744c9b06deaf7`.

Inherited accounting is **USD81.654000 budget-accounted**:
USD80.756090 measured plus USD0.897910 held for historical unknown usage.
The unknown amounts remain reservations, not measured charges; methodology labels
accounting incomplete on that basis. Unresolved dispatches: **0**.
These log totals are not invoice reconciliation.

| Paper | Status | Snapshots | Items | Quarantined | Open gaps |
|---|---|---:|---:|---:|---:|
| vonfintelgillies2007 | extracted | 3 | 136 | 27 | 6 |
| eganweatherson2011 | extracted | 1 | 125 | 10 | 0 |
| vonfintelgillies2011 | extracted | 2 | 147 | 13 | 4 |
| wright2007 | extracted | 1 | 105 | 17 | 0 |
| schaffer2011 | partial | 2 | 194 | 21 | 5 |
| braun2012 | partial | 3 | 119 | 38 | 6 |
| eganhawthorneweatherson2005 | extracted | 1 | 213 | 14 | 0 |
| egan2007 | extracted | 1 | 158 | 12 | 2 |
| macfarlane2011 | extracted | 1 | 169 | 17 | 0 |
| yalcin2007 | partial | 1 | 210 | 10 | 2 |
| yalcin2011 | extracted | 3 | 87 | 24 | 3 |
| rothschild2012 | extracted | 1 | 71 | 1 | 0 |
| moss2015 | extracted | 3 | 241 | 13 | 9 |
| hawkesteinertthrelkeld2021 | extracted | 1 | 227 | 5 | 0 |
| veltman1996 | extracted | 1 | 267 | 31 | 0 |
| gsv1996 | extracted | 1 | 259 | 11 | 1 |
| willer2013 | extracted | 1 | 169 | 1 | 0 |
| ninan2018 | partial | 1 | 180 | 15 | 2 |
| beddorgoldstein2021 | extracted | 1 | 123 | 16 | 0 |
| hollidaymandelkern2024 | extracted | 1 | 382 | 7 | 5 |
| kolodnymacfarlane2010 | partial | 1 | 84 | 13 | 1 |
| knobeyalcin2014 | extracted | 1 | 58 | 1 | 0 |
| **Total** | **22 graphs** | **32** | **3,724** | **317** | **46** |

The item total counts retained accepted inventory, including quarantine, not
unique claims or usable evidence. The extra 51 item records preserve original
and renamed identities; they are not 51 newly extracted claims. The 46 gaps are
snapshot-scoped obligations, not 46 unique semantic omissions, and cannot be
compared directly with the overnight diagnostic count of 26. Six papers carry
multiple original snapshots. Five of the 22 nonempty graphs remain explicitly
partial; the other 17 are extracted. The extra 17 quarantined records are among
the restored original IDs, not evidence of newly generated material. The four excluded papers are `yalcin2015`,
`klinedinstrothschild2012`, `bledin2014`, and `macfarlane2014`, with explicit
reasons in the roster. Source page/encoding diagnostics, thin-range and
inference-coverage limitations remain disclosed.

Verification ran sequentially on stable source: **608 passed, 2 skipped
(610 collected)** in the full pytest suite, followed by **265/265 negative
controls**, each red under mutation and green after restoration. The verification
wrapper checked all nine owned files' hashes unchanged across both runs. Full
suite wall time: 326.3s; controls: 781.0s. `git diff --check`
passed. There is no configured standalone lint/typecheck command in this repository.

Evidence: `runs/mu-round4/final-pytest.txt`, `final-controls.txt`,
`verification.json`, `verified-source.json`, and `controls-results.json`.
The control runner includes eight new production-wire controls and two retargeted
controls for union retention instead of refusal. The initial missing-retention and
thin-ID regressions failed before implementation; incoming qualifier body and
presence-only regressions also failed before their fixes. Those recordings are
`regressions-before.txt`, `context-regressions-before.txt`, and
`presence-regression-before.txt`; an earlier scoped run passed 35 tests.

The first full-suite run passed 607 tests with two skips, but its control run
found an obsolete test path: `union_thin_retry_once` survived because completed
reuse no longer enters range salvage. The existing regression now covers both
completed snapshots and interrupted history containing accepted range receipts
but no completed outcome. The retry control targets interrupted salvage; the
completed-reuse control targets direct reuse. No production fix was needed for
this coverage gap. The full suite and complete controls were rerun sequentially
after strengthening it; `attempt1-*` preserves the initial evidence.

### Round 4 scope and remaining limits

No paid calls, push, delegation or source-tree/cache writes in `/home/dev/ara-scaffold`
occurred. Round 4 spend is USD0; mu's earlier cumulative paid spend remains
USD11.348785. Imported charges remain separately visible in methodology and are
not represented as new spend. Local cache and config paths are under the mu
worktree. There was no prompt/schema change requiring a new provider preflight.

Code review: skipped (ce-code-review unavailable). Its independent-agent workflow
cannot complete under the user's explicit no-delegation instruction. An author
review and inline simplification pass covered the diff; they do not constitute
independent review. Evidence: `runs/mu-round4/review.md`. A short non-author review
remains appropriate before merge, as requested in the original brief.

The lexical grounding gate is not semantic entailment or completeness. All prior
source-quality, thin-range and evidence/T limits still apply. No real-corpus
construction, freeze or search was performed. B3 shared-frozen compatibility and
S1 merged-tree verification remain outside this work's scope.

### Round 4 finding placement

| # | Finding | Report section carrying it |
|---|---|---|
| 36 | Completed thin snapshots were skipped and rebuilt without generation; all 51 changed IDs are exact namespace remaps, including dependent references; original v5 identities are retained | Round 4 root cause |
| 37 | Explicit lossless snapshot union replaces refusal; stable namespaced IDs/provenance, original identity pins and reproducible second resume retain accepted evidence | Round 4 union, provenance and quarantine |
| 38 | Incoming qualifiers, including presence-only differences, require isolated inference contexts; quarantine and gap resolution remain snapshot-local | Round 4 union, provenance and quarantine |
| 39 | Counted reconciliation overflow retains ranges and allows the next paper; overnight stopping was operator-driven; bounded splitting is deferred | Round 4 reconciliation overflow |
| 40 | Native full-chain corpus counts, exclusions, per-paper quarantine/gaps, retention, provenance and inherited measured/held accounting; extra IDs and snapshot-scoped gaps are not new semantic content | Round 4 artifact and verification |
| 41 | Stable-source full pytest and sequential production-wire controls establish local behavior, with initial red regressions and restoration evidence | Round 4 artifact and verification |
| 42 | No new spend/push/delegation; independent review unavailable and semantic, construction/T and merged-tree limits remain | Round 4 scope and remaining limits |

42 findings, 42 placed (35 historical findings and seven Round 4 findings).

## Round 5 — Pi B1: native snapshot prerequisite contexts

Local head: `af51ca9854c0206c0cc908482e794fcba845107c` on `fix/four-paper-acceptance`, based on
`9d4ec86595f7c46d5ba6d6f9747d86d50533246a`. This round implements
`/home/dev/ara-work/briefs/mu-round-5.md` and the sole blocking finding in
[Pi's review](/home/dev/ara-work/reports/pi-review.md).

### Round 5 correction and retention

**Pi B1 is fixed.** Round 4 isolated incoming qualifiers only on inferences.
Native construction also treats incoming `applies_to` on premises, intermediate
conclusions and conclusions as prerequisites, and makes an inference a prerequisite
of its conclusion. A shared conclusion could therefore reconnect two separated
inference contexts. This corrects the incomplete isolation claim in Round 4
finding 38; the defect did not require a changed item body.

The union now calls construction's `evidence_dependencies` on each original
snapshot. Different prerequisite inventories or bodies trigger snapshot-qualified
IDs. Separation propagates through native prerequisites and explicit references
until stable, so each mapped endpoint and prerequisite closure stays in its
original context. Source bodies, original acceptance identities, citations, pins,
quarantine and gap disclosures remain preserved. No additional content is generated.
The existing conflict, changed-qualifier and new-qualifier fixtures now retain
15, 14 and 15 items respectively instead of 10: more dependent contexts stay
separate. Their exact body/reference retention checks and two-item quarantine
assertions are unchanged. DECISIONS M6 documents the corrected contract.

### Round 5 verification

Pi's four native closure regressions were adapted into the tracked publication
tests, with an additional case for an incoming inference present in only one
snapshot. All **five failed before the production fix** with extra prerequisites
in the old context (`runs/mu-round5/regressions-before.txt`). After the fix,
the tests compare every eligible original root's exact native prerequisite closure
against its mapped published closure in both snapshots, both input orders, and a
second resume. They also verify native publication/provenance, exact retention,
zero new model calls and grounding eligibility. Sockets are blocked; provider
completion is forbidden during reuse. The existing quarantine tests remain.

Scoped verification: **35 passed** (`scoped.txt`). The first scoped attempt after
the production fix passed the five closure cases but failed the three old item
counts; only their expected retained counts changed (`scoped-attempt1.txt`).
The first full run found one more obsolete 10-item expectation in the resume-policy
union test (612 passed, two skipped, one failed); the corrected expectation is 15.
That file was rerun, then the complete sequence restarted. Evidence:
`attempt1-final-pytest.txt`, `attempt1-verification.json`, `resume-policy.txt`.
No production change was needed for either count adjustment.
Full verification then ran sequentially on stable source: **613 passed,
2 skipped / 615 collected**, followed by **266/266
negative controls**, each failing under mutation and passing after restoration.
The two skipped tests are opt-in live-provider checks. The new control replaces
native dependencies in the union with outgoing references; its native closure
regressions turn red. Two existing mutation anchors were updated for the new
implementation. All mutation anchors are unique, and the wrapper verified every
tracked file's hash unchanged across the full suite and control run.

Full-suite wall time: 307.5s; controls: 775.4s.
Evidence: `runs/mu-round5/final-pytest.txt`, `final-controls.txt`,
`verification.json`, `verified-source.json`, `controls-results.json`, and the
per-control red/green logs in `runs/delta-controls/`. `git diff --check` passed.
There is no configured standalone lint/typecheck command.

### Round 5 compatibility and current artifact

The v1 union representation and v6 acceptance identity remain unchanged; this is
an identity/context calculation correction. Existing derived unions still must
reconstruct from pinned originals before import. An old union affected by B1 is
refused by that existing check; republish it from its original snapshot runs.
There is no silent acceptance or rewriting of a stale derived graph.

Pi independently checked all 741 coalesced items in the current artifact and
found **zero differing native incoming prerequisite contexts**. With the fixed
implementation, this round also reran Pi's read-only reconstruction script against
all six real multi-snapshot unions: their full graphs and per-item provenance
reproduce exactly in both input orders (`rebuild-unions.json`, `rebuild-unions.txt`).
Only the script's evidence output destination changed. The existing artifact is
unchanged and was not republished:
`/home/dev/ara-work/mu/runs/mu-round4-offline/literature.extracted.txt`, SHA-256
`c6f5db583c22f8b3685c31e4af4c2199efcf6e71f7550c53022744c9b06deaf7`.
Its previously verified 3,724 retained / 3,407 eligible / 317 quarantined items,
22 nonempty papers and 46 snapshot-scoped gaps remain the recorded corpus result.
No claim is made that the current corpus was corrupted by B1.

### Round 5 scope and review limits

No paid calls, push or delegation occurred. New spend is USD0. No write was made
to `/home/dev/ara-scaffold`, its runs or cache. Changes are locally committed in
mu; no prompt/schema/provider preflight or corpus generation was needed.
An inline simplification and author review covered the changed implementation,
consumer, provenance reconstruction, tests and controls (`review.md`).

Code review: skipped (ce-code-review unavailable). Its independent-context
workflow conflicts with the original brief's explicit no-delegation instruction;
no new independent review was launched. Pi independently reviewed the previous
head and supplied B1; the author review does not certify the new head independently.
No real-provider construction, capacity fit, freeze or search was performed.
Grounding is lexical, and neither the structural checks nor this fix establish
semantic completeness. Earlier B3 shared-frozen compatibility and S1 merged-tree
verification limits remain outside this round.

### Round 5 finding placement

| # | Finding | Report section carrying it |
|---|---|---|
| 43 | Pi B1 invalidates inference-only isolation; use all native prerequisites and propagate context, retaining additional dependent items | Round 5 correction and retention |
| 44 | Five regressions failed before the fix; native closure, retention/order/resume/quarantine checks and sequential full suite/controls establish local behavior | Round 5 verification |
| 45 | Unaffected v1 unions remain reproducible; affected historical derived unions require originals; current corpus has zero detected B1 impact and all six unions rebuild unchanged | Round 5 compatibility and current artifact |
| 46 | Local-only, USD0, no delegation; no independent review of new head or provider/construction/semantic/merged-tree proof | Round 5 scope and review limits |

46 findings, 46 placed (42 historical findings and four Round 5 findings).

## Round 6 — Construction window metadata and receipt import

Local head: `1d832b24805536b46e6974ca97842cffe0458e3a` on `fix/four-paper-acceptance`, based on
`af51ca9854c0206c0cc908482e794fcba845107c`. This implements
`/home/dev/ara-work/briefs/mu-round-6.md` against the completed overnight artifact.

### Round 6 metadata correction

The pilot's singleton refusal was caused by the request's metadata, not the
622-character evidence item. The recorded request carried 124,279 characters of
whole-paper item provenance, plus snapshot, quarantine, grounding and gap data.
It counted 86,119 build tokens / 82,933 selection tokens against the unchanged
70,000 batch bound. The earlier union preserved valuable audit metadata but the
construction projection incorrectly copied all of it into every window.

Construction plan v6 now uses the same explicit projection when counting,
selecting roots and formalizing their fixed closure. Each paper window contains
only its source ID, supplied title/authors, partial-source flag, selected items,
and those items' provenance, quarantine and applicable gap entries. Item IDs,
citations, text, attribution and graph references are unchanged. Gap entries
with explicit item IDs are scoped to those IDs; native page-scoped gaps must
overlap a selected item's pages and, when present, its snapshot provenance.
Unscoped gaps remain in the artifact and receipts. Full snapshot manifests,
grounding inventories, unrelated dispositions and arbitrary paper fields stay
out of model-facing paper windows. The plan still hashes each complete original
paper. Full metadata and all retained evidence remain in immutable source and
imported receipts; eligibility, closure, omission, formula and freeze rules are
unchanged. DECISIONS M7 records this contract.

The current real artifact omits title and author fields. The projection preserves
them when supplied directly or in a record, but emits null when absent; it does
not invent bibliography or alter the historical artifact to add it. Its source
IDs and item attribution/citations remain available. Partial-source flags remain
visible even when a particular window has no overlapping gap.

### Round 6 real recount

Authoritative input:
`/home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt`, SHA-256
`1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`.
The recount used the recorded pilot topic, empty audience, effective `pilot`
configuration and native `construct`, `counted_windows`, request rendering and
Anthropic free token counter. Caps stayed at 70,000 batch input, 200,000 model
context, 64,000 construction output and 32,000 reserved catalogue tokens.
Generation was forbidden and the run stopped at the complete `build_t_plan`,
before selection or formalization. This is a counted plan, not an executed pilot.

The final plan contains **46 windows**, covering all **5,296 eligible
items exactly once** out of the artifact's 5,659 retained items (363 quarantined).
The largest governing window count is **69619 tokens**, within
70,000. Total planned **construction input is 2357296
tokens**; planned selection input is **2363003 tokens**.
The sum of per-window maxima recorded by native planning is
**2393603 tokens**. Construction and selection sums refer to
final windows, not rejected partition probes or repeated counting requests.
There were **274 free count requests**, zero new model dispatches,
zero generated responses and USD0 new spend.

Evidence: `runs/mu-round6/recount/plan.json`, `summary.json`, `counts.jsonl`,
`events.jsonl`, and `local-audit.json`. The native log preserves the counted
prompts and input decisions. Original artifact hashes remain unchanged.
These initial-window totals do not predict actual selected closures, output
formulas, symbol growth, retries or final working-T size. Those still undergo
native capacity checks during a later authorized pilot. No commitment freeze,
search, route selection or semantic-completeness claim is made.

### Round 6 import performance and integrity

The expensive destination operation was repeated full-chain verification:
`import_receipts` emitted one event at a time, and every append re-read, parsed,
hashed and verified the entire growing destination plus anchor. It also fsynced
both files per event. The copied payload therefore incurred quadratic rereading.
Repeated transitive verification also did not share a memo across all siblings.

Import now appends its marker and exact copied events in one batch under the
existing exclusive lock and a verified destination prefix. Every copied original event and timestamp is retained, with its own destination
sequence, chain hash and anchor entry; both append-only files flush and fsync
before success. Operational errors propagate; mismatched
partial appends are refused on the next verification, and incomplete imports
remain invalid against their declared record counts. Single-event writes use
the same path. Checkpoint memoization is confined to one verification operation,
so a later call still detects ancestor changes. Source files are never rewritten.

On the real corpus, pinned artifact/transitive verification took **26.42s**,
then import took **35.44s**, for **61.85s total**.
The 4,454 source events yielded 4,436 destination entries: one import marker plus
deduplicated original events, with ancestor import markers represented through
the pin. This compares operationally with Zeta's roughly 70-minute pilot import,
but that earlier run is not a controlled benchmark.

A paired benchmark ran the base and new native import implementations on the
same **128 evenly sampled real original receipt events**, excluding import
markers. Exact copied events and import verification passed in both outputs.
Base: **3.842s**; new: **0.085s**; **45.4× faster**.
The terminal `import_speedup` uses this paired sample ratio, not an extrapolated
full-run ratio. The benchmark loaded base code into ignored scripts without
mutating production. Evidence: `runs/mu-round6/import-benchmark/summary.json`,
`before.jsonl`, `after.jsonl`, and `recount/import-timing.json`.

### Round 6 verification and scope

Three new tests failed before implementation: foreign metadata in native windows,
per-event destination rereads, and the missing bulk append API. The interruption
case was then strengthened to fail during an actual anchor write and verify that
the resulting mismatch is refused. The window regression exercises real counting,
selection and formalization, split windows, unchanged evidence/citations,
partial identity, scoped gaps and no foreign provenance/quarantine/extra fields.
Scoped suite: **67 passed**; the strengthened boundary file also passed.

Final full pytest: **616 passed, 2 skipped / 618 collected**,
followed sequentially by **270/270 negative controls**, all red under
mutation and green after restoration. Four new controls cover window metadata,
gap scope, bulk import performance and append verification. All anchors are unique.
The mutation runner started only after both the free recount and pytest finished.
Every tracked file's hash matches before and after verification. Full pytest:
**263.6s**; controls: **785.5s**. Evidence:
`runs/mu-round6/regressions-before.txt`, `scoped-attempt1.txt`, `boundaries.txt`,
`final-pytest.txt`, `final-controls.txt`, `verification.json`,
`verified-source.json`, `controls-results.json`, and the control red/green logs.
`git diff --check` passed. No standalone lint/typecheck is configured.

All changes are committed locally; no push, paid call, delegation, or write to
`/home/dev/ara-scaffold` or its runs/cache occurred. Free counting and benchmark
outputs stayed in mu's ignored runs. An inline simplification and author review
covered native projection, source retention, graph/capacity callers and log/import
integrity (`runs/mu-round6/review.md`). Code review: skipped (ce-code-review
unavailable), because its independent-context workflow conflicts with the
original no-delegation instruction. No independent review of this head is claimed.
Previous semantic, live construction/freeze/search, B3 shared-frozen compatibility
and S1 merged-tree proof limits remain.

### Round 6 finding placement

| # | Finding | Report section carrying it |
|---|---|---|
| 47 | Whole-paper metadata caused singleton overflow; native projection scopes metadata, preserves evidence/partial flags, keeps unscoped gaps in receipts and leaves missing bibliography unknown | Round 6 metadata correction |
| 48 | Real free-counter plan covers all eligible items within the batch bound; totals are planning inputs, not selected-closure or end-to-end success | Round 6 real recount |
| 49 | Quadratic destination verification/fsync and repeated ancestor checks slowed import; verified batch append and operation-local memo improve it with measured paired and real-corpus evidence | Round 6 import performance and integrity |
| 50 | Test-first defects, final sequential tests/controls, restoration, local-only USD0 scope and independent/live proof limits | Round 6 verification and scope |

50 findings, 50 placed (46 historical findings and four Round 6 findings).

## Round 7

Local commit: `cdc9753f75e1906fa753bb7af3f410184f453d04` on `fix/provenance-verification-receipt`,
from base `0e0a7fcf8a167fa6a0973f92e322582c33d6e6e4`.

### Round 7 receipt behavior and integrity

Native run startup now persists verification receipts under the configured cache
in `lineage-verification/`. Each receipt records `extraction-lineage-verifier-v1`,
Python version and verifier code hashes, a verified result, original pin, event
digest, and SHA-256 of every verified artifact, sidecar, source log and separate
anchor. Every new run chains the complete receipt, its digest, proof-log checkpoint
and full/reused decision into its log before importing original events.

Warm reuse checks every manifest hash, loads the pinned events while hashing the
entire root log, checks their digest, and checks all input hashes again. Missing,
corrupt or stale receipts force full reconstruction and transitive verification;
invalid lineage refuses before model setup/import. Source anchors now validate
against their complete logs. Referenced symlinks remain in the manifest so changing
their target cannot evade checks. Header tampering cannot turn a known extracted
artifact into human input. Malformed/missing sidecars reach full verification.
Public verification APIs retain full checks; the cached path uses the shared
private append helper only after validation. Inherited receipts/charges are intact.

The receipt uses the repository's local hash-chain/separate-anchor trust model,
not signatures. Coordinated replacement of a complete chain and its anchor is
outside that model; hash rechecks also do not promise an atomic snapshot against
adversarial change-and-restore between reads. Deleting the cache forces full
verification. This is a verification performance change, not new extraction
acceptance, semantic fidelity, or live construction/search proof.

### Round 7 offline startup measurement

Authoritative input:
`/home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt`;
SHA-256 `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`.
The unmodified base took **64.214626s** for native lineage verification plus
import: **27.525663s** verification and **36.688963s** import. With this change,
cold receipt creation plus import took **33.133991s**, and warm verification plus
import took **5.692084s**, approximately **11.3x faster** than the base total.
The receipt covers **42 files / 744,729,028 bytes**. Instrumentation saw one full
verification cold and none warm. All **4,454 source events** matched across cold
and warm runs, and copied original events matched the baseline exactly, preserving
inherited accounting. The source artifact hash remained unchanged. These are
single observations on this host, not a repeated statistical benchmark.

Zeta's reported roughly 24.1-minute delay includes offline construction restoration.
The measured boundary here is lineage verification/import only; the receipt cache
does not eliminate or measure that entire restoration interval. Evidence:
`runs/mu-round7/baseline.py`, `baseline/summary.json`, `baseline-console.txt`,
`benchmark.py`, `benchmark/summary.json`, and `benchmark-console.txt`.

### Round 7 verification and scope

Full pytest passed **699 tests, 2 skipped / 701 collected** in **352.43s**.
This was followed sequentially by **323/323 negative controls**, all failing under
mutation and passing after restoration, in **1,070.94s**. All **152 tracked/new
source file hashes** match the pre-verification snapshot. `git diff --check`
passed and the committed worktree is clean. Evidence: `runs/mu-round7/final-pytest.txt`,
`final-controls.txt`, `verification.json`, `source-before.json`,
`verified-source.json`, `controls-results.json`, and `runs/delta-controls/` red/green
logs. No standalone lint/typecheck is configured. Placeholder tests cover native CLI cold/warm
startup, all manifest input categories, receipt/anchor damage, version changes,
valid append invalidation, symlink retargeting, header/sidecar refusal, and changes
during full or warm reads. Initial regressions failed before implementation;
additional header/sidecar regressions failed before their fix. Scoped verification:
78 passed, then the final receipt file's 18 tests passed. Nine new production
mutations cover hashes, anchors, verifier identity, receipt logging, symlinks,
header binding and both stability checks; two existing controls follow the moved
verification/import call sites.

All work is local: no push, paid call, delegation, or write to the scaffold's
histories/cache. Provider, construction and search source are unchanged. Inline
simplification and author review are recorded in `runs/mu-round7/review.md`.
Code review: skipped (ce-code-review unavailable), because independent review
contexts conflict with the original no-delegation instruction. No independent
review or live downstream success is claimed; earlier semantic and merged-tree
integration proof limits remain.

### Round 7 finding placement

| # | Finding | Report section carrying it |
|---|---|---|
| 51 | Byte-bound persistent receipts preserve recursive log/anchor verification and original import accounting; header, sidecar, symlink and in-flight changes cannot silently reuse them | Round 7 receipt behavior and integrity |
| 52 | Local chain/anchor trust is not signed authentication or atomic adversarial snapshot protection | Round 7 receipt behavior and integrity |
| 53 | Real lineage verification/import drops from 64.21s to 5.69s warm; this does not measure or remove the full 24.1-minute construction restoration delay | Round 7 offline startup measurement |
| 54 | Placeholder regression/control evidence, restoration, local-only scope and independent/live proof limits | Round 7 verification and scope |

54 findings, 54 placed (50 historical findings and four Round 7 findings).

DONE mu round7 head=cdc9753f75e1906fa753bb7af3f410184f453d04 tests=699/701 negctl=pass startup_before_s=64.214626 startup_after_s=5.692084
