# Zeta fork pilot 3

Operator confirmed kappa4 approved revision a272ebe with 0 blocking findings and it is merged to main.

**awaiting-selection.** 3 targets; 6/6 searches; 2 CLOSED-derived, 0 CLOSED-structural, 4 OPEN. No route selected.

[Native full-lineage report](/home/dev/ara-work/reports/overnight/fork3/report.html) · [Model-written summaries and review notes](/home/dev/ara-work/reports/overnight/fork3/route-summaries.html) · [Full audit](/home/dev/ara-work/reports/overnight/fork3/fork-audit.json).


## Acceptable pilot — approved criteria 1–4

Overall verdict: **FAIL**. All four criteria are required.

| Criterion | PASS/FAIL | Numbers |
|---|---|---|
| 1. Clean run | PASS | awaiting_selection=True; searches 6/6; new MODEL receipts 69; unsettled 0; unknown usage 0; Claude/non-Codex calls 0; new API USD 0.0 |
| 2. Coverage | PASS | 22/26 papers; page-cited 169/169; stance-labelled 169/169 |
| 3. Real routes | FAIL | CLOSED-derived 2; mechanical cross-paper qualifiers 0; substantively qualifying 0 (required >=3) |
| 4. Readable output | PASS | model-written summaries 6/6; report opened; page errors 0; missing anchors 0; HTML 1.277620 MB |

Criterion 4 evaluates summary coverage and rendering; substantive accuracy limits are disclosed in the summary review. Native labels do not independently establish useful synthesis, source truth, faithful formalization or literature originality. The Successful entry criteria (essay, audits, methodology and submission) were not attempted.


## Execution and source preservation

Clean detached revision `a272ebe7df8615a7a9a4a0215068f963171a5c3d` in `/home/dev/ara-work/run-a272ebe`. Fresh live 16-case Codex schema preflight, then standalone canary, then native fork-from-freeze with the fresh proof override. The CLI forks and immediately continues targets/search, so preflights preceded it. No native source edits, commits, new construction or second freeze. Pilot 5 source files and the named prior handoffs match their pre-run hashes. Previous handoff remains `zeta-fork2.md`; `zeta-codex-pilot-5.md` is also preserved.

Same native configuration: codex_cli requesting gpt-6-luna through separate ChatGPT authentication; 100M local token cap, 60k catalogue, construction multiplier 2, concurrency 4, empty audience and no fallbacks. Only the fresh schema-proof path and native fork cache differ. Serving model identity is unverified; requested identity is not serving proof. Historical extraction and construction are retained as imported usage, not new calls.

| Freeze measure | Value |
|---|---|
| Commitments | 169 |
| Papers | 22/26 |
| Page cited | 169 |
| Stance labels | 169 |
| Stance distribution | {'endorsed': 150, 'attacked': 13, 'reported': 6} |
| Copied prefix records | 7092 |
| Prefix SHA-256 | ebc06323f56c53cf184a187fea12843558df3da750ab1454e7bb3cec1e03ecc1 |
| Frozen commitments with omitted source support | 22 |

Coverage does not prove extraction completeness or faithful paraphrase. Pilot 5 construction omissions and lexical-validator limitations remain inherited; the fork did not repair T. Endorsed means asserted by the source author, not independently true. Reported/attacked material is not an admissible global premise or CQ source.


## Targets and novelty gates

Candidate-attempt dispositions: {"kept": 3}. 3 candidate-attempt pairs across 3 proposal calls. Full definitions, essential-atom substitutions, solver timeouts and all rejection receipts remain in fork-audit.json and the native report.

| Attempt | Requested pool | Received pool | Underfilled | Disposition |
|---|---|---|---|---|
| 1 | 20 | 1 | True | passed |
| 2 | 20 | 1 | True | passed |
| 3 | 20 | 1 | True | passed |

### Attempt 1 — information-sensitive-epistemic-semantics

An adequate semantics of epistemic modals must make modal evaluation sensitive to information states, not only to worlds.

| Gate | Verdict |
|---|---|
| Pool | kept |
| Own thesis | own_thesis |
| Semantic novelty / fidelity | new_assertion / matches |
| Classifier reason | The target states a requirement in its own voice. Its text matches the supplied atomic definition, and the requirement is not merely a restatement of an existing frozen commitment. |
| Contribution | candidate: no_single_support |
| Whole-T novelty | candidate: essential_new_assertion |
| Essential new propositions | [{'args': [], 'name': 'epistemic_semantics_requires_information_state_sensitivity', 'op': 'atom', 'terms': [], 'variable': None}] |
| Rejection reasons | [] |
| Fresh definitions | [] |

### Attempt 2 — order-sensitivity-diagnostic

Order sensitivity in epistemic-modal discourse is a diagnostic constraint on an adequate semantics of those modals.

| Gate | Verdict |
|---|---|
| Pool | kept |
| Own thesis | own_thesis |
| Semantic novelty / fidelity | new_assertion / matches |
| Classifier reason | The target directly asserts the same proposition as its rendered content. The frozen entries discuss order effects but do not state that order sensitivity is a diagnostic constraint on adequate epistemic-modal semantics. |
| Contribution | candidate: no_single_support |
| Whole-T novelty | candidate: essential_new_assertion |
| Essential new propositions | [{'args': [], 'name': 'epistemic_modal_order_sensitivity_is_a_diagnostic_constraint', 'op': 'atom', 'terms': [], 'variable': None}] |
| Rejection reasons | [] |
| Fresh definitions | [] |

### Attempt 3 — static-semantics-order-limit

A static possible-worlds semantics that treats sentence sequences as conjunctions cannot explain order-sensitive epistemic-modal discourse.

| Gate | Verdict |
|---|---|
| Pool | kept |
| Own thesis | own_thesis |
| Semantic novelty / fidelity | new_assertion / matches |
| Classifier reason | The target asserts its claim directly, and the atomic formula is bound to the same text. It synthesizes the frozen claims about static conjunction semantics and order-sensitive discourse into an explanatory conclusion. |
| Contribution | candidate: no_single_support |
| Whole-T novelty | candidate: essential_new_assertion |
| Essential new propositions | [{'args': [], 'name': 'static_conjunction_semantics_cannot_explain_order_sensitive_epistemic_modal_discourse', 'op': 'atom', 'terms': [], 'variable': None}] |
| Rejection reasons | [] |
| Fresh definitions | [] |

**Attribution-screen review:** All 3 candidates were retained, one from each of 3 underfilled requests for 20. All 3 own-thesis classifications report own_thesis/new_assertion/matches; deterministic contribution and essential-atom novelty gates passed. One lexical advisory hit (states in information states) was logged for the first target, which the classifier accepted. No exact report-frame or lexical exclusion occurred. This directly exercises advisory-hit acceptance on an own-voice use of states.

| Attempt | Target | Matched content words |
|---|---|---|
| 1 | information-sensitive-epistemic-semantics | ['states'] |
| 2 | order-sensitivity-diagnostic | [] |
| 3 | static-semantics-order-limit | [] |

Substantive novelty limit: the static-semantics target repeats the no-order-asymmetry criticism explicitly developed in von Fintel and Gillies2007, PDF pages 25–26. Its fresh atom and own-thesis classification are not evidence of a novel literature contribution. The 2 closed routes likewise establish no qualifying cross-paper new thesis; see their individual reviews.


## Searches and routes

| Category | Count |
|---|---|
| CLOSED-derived | 2 |
| CLOSED-structural | 0 |
| CLOSED-single-support | 0 |
| CLOSED-attributed-report | 0 |
| CLOSED-contribution-unresolved | 0 |
| CLOSED-stance-crossing | 0 |
| OPEN | 4 |

| Target | Polarity | Nodes | Depth | Proposals | Complete/authenticated | Prunes |
|---|---|---|---|---|---|---|
| information-sensitive-epistemic-semantics | target | 3 | 1 | 1 | True/True | {} |
| information-sensitive-epistemic-semantics | negation | 3 | 1 | 1 | True/True | {} |
| order-sensitivity-diagnostic | target | 3 | 1 | 1 | True/True | {} |
| order-sensitivity-diagnostic | negation | 1 | 0 | 0 | True/True | {} |
| static-semantics-order-limit | target | 3 | 1 | 1 | True/True | {} |
| static-semantics-order-limit | negation | 3 | 1 | 1 | True/True | {} |

| Route | Target/polarity | Category | Used commitments | Papers | Qualified schemes | Novelty | Stance crossings |
|---|---|---|---|---|---|---|---|
| 9a35a6febc9d:r0 | information-sensitive-epistemic-semantics / target | CLOSED-derived | ['gsv1996:r18-35:n_order', 'gsv1996:r18-35:n_seq_conj'] | ['gsv1996'] | [{'node_id': 'n0', 'bank_id': 'sign'}] | essential_new_assertion | [] |
| 14deb2a30da4:r0 | information-sensitive-epistemic-semantics / negation | OPEN | ['macfarlane2011:r1-22:main_concl', 'yalcin2007:r1-22:c1'] | ['macfarlane2011', 'yalcin2007'] | [] | None | [] |
| edd5e3e69fbe:r0 | order-sensitivity-diagnostic / target | CLOSED-derived | ['gsv1996:r18-35:n_order', 'gsv1996:r18-35:n_seq_conj'] | ['gsv1996'] | [{'node_id': 'n0', 'bank_id': 'sign'}] | essential_new_assertion | [] |
| 66bacb38c304:r0 | order-sensitivity-diagnostic / negation | OPEN | [] | [] | [] | None | [] |
| 42a72010f361:r0 | static-semantics-order-limit / target | OPEN | ['gsv1996:r18-35:n_order', 'gsv1996:r18-35:n_qual_more_than', 'vonfintelgillies2007:union:item:vonfintelgillies2007:r25-32-refine:ic_onestep', 'vonfintelgillies2007:union:item:vonfintelgillies2007:salvage:4ff47650edc001ab:vonfintelgillies2007:r25-32-refine:av_static'] | ['gsv1996', 'vonfintelgillies2007'] | [] | None | [{'commitment_id': 'vonfintelgillies2007:union:item:vonfintelgillies2007:salvage:4ff47650edc001ab:vonfintelgillies2007:r25-32-refine:av_static', 'stance': 'attacked', 'role': 'cq_evidence'}] |
| 61c78dfec51e:r0 | static-semantics-order-limit / negation | OPEN | ['gsv1996:r18-35:n_order', 'vonfintelgillies2007:union:item:vonfintelgillies2007:salvage:4ff47650edc001ab:vonfintelgillies2007:r25-32-refine:av_static'] | ['gsv1996', 'vonfintelgillies2007'] | [] | None | [{'commitment_id': 'vonfintelgillies2007:union:item:vonfintelgillies2007:salvage:4ff47650edc001ab:vonfintelgillies2007:r25-32-refine:av_static', 'stance': 'attacked', 'role': 'cq_evidence'}] |

Used commitments include reachable premises and CQ evidence. Distinct-support qualification deduplicates formulas; merely counting IDs can overstate independence. OPEN is a bounded search result, not proof of impossibility. Current-head report classifications can differ from original historical labels because the report applies the current contribution policy.


## Paired conflicts and forward analysis

One Tier 1 conflict groups opposite static-semantics conclusions under the same premise formulas. Both graphs remain OPEN. The repair response proposes narrowing the positive claim, but its bank_id is vonfintelgillies2007, a paper identifier absent from the versioned bank; its premise slot names are also not sign slots. This is a schema-accepted model suggestion retained in the analysis receipt, not an engine-licensed repair, changed route, or resolved conflict. No repair proposal was applied. The two closed routes each have 138 forward consequences and no truncation; this deterministic analysis added no model spend, apart from the separate logged conflict-repair call.

Tier 1 conflicts: 1; Tier 2 conflicts: 0; forward consequences: 276. Full paired-analysis receipts are preserved in the native report and conflict-review.json.


## Substantive review of CLOSED-derived routes

Read all 6 authenticated terminal trace graphs, the 7 referenced frozen commitments and stance/provenance records, the sign scheme with its 2 CQs, and original PDF pages 18/20 of GSV1996 plus 25/26 of von Fintel and Gillies 2007. The 2 CLOSED-derived graphs share 2 supports from 1 paper; neither meets criterion 3. Native closure/atomic novelty is separated from supported new philosophical contribution. All six terminal trace graph hashes and classifications were checked against the final published native routes and match.

| Route | Mechanical qualification | Distinct supports / papers | Qualified schemes | Criterion 3 review |
|---|---|---|---|---|
| 9a35a6febc9d:r0 | False | 2 / 1 | [{'node_id': 'n0', 'bank_id': 'sign'}] | FAIL: FAIL. Mechanically CLOSED-derived: one licensed sign inference concludes the essential fresh atom; two distinct endorsed commitments and both CQ answers come from GSV1996, PDF page 18. It therefore has only 1 paper, below the required 2. The source demonstrates a particular dynamic account and an order-sensitive example; that does not establish the universal necessity asserted for every adequate epistemic-modal semantics. CQ1 itself disclaims universality. The sign_relation is a description of that account, rather than an independently established link to the universal requirement. GSV1996 page 20 also limits the treatment, while page 18 makes the order example conditional on intervening information/different speakers. Source premise n_order has omitted support inf1. Native atomic novelty passes, but a supported novel thesis is not established. |
| edd5e3e69fbe:r0 | False | 2 / 1 | [{'node_id': 'n0', 'bank_id': 'sign'}] | FAIL: FAIL. Mechanically CLOSED-derived: one licensed sign inference concludes the essential fresh atom; the same two distinct endorsed GSV1996 commitments and the same paper support both CQs. Only 1 paper is used, below the required 2. Treating the order contrast as a diagnostic is a reasonable methodological inference, but the route reuses the paper's existing explanatory example and account; it supplies no independent novelty comparison or cross-paper synthesis. CQ answers explicitly do not establish that the dynamic account is uniquely required or decisive for every semantic theory. GSV1996 PDF page 18 already presents order sensitivity as the phenomenon the semantics explains, and qualifies the example by discourse setting. n_order carries omitted support inf1. The route can show native defeasible closure without establishing a qualifying new contribution. |


## Open-route evidence and support fit

Route `14deb2a30da4:r0`: Negation of information-state-sensitivity target remains OPEN.

| Finding |
|---|
| Both open premise leaves formalize to the same negated atom as the root; they provide no independent derivation. |
| Both critical questions are unanswered. The first cites endorsed MacFarlane2011 and Yalcin2007 positions as counterpressure, not as proof of this negation. |
| Two papers mentioned in unanswered CQs do not turn this open graph into a qualifying supported route. |

Route `66bacb38c304:r0`: Negation of order-sensitivity-diagnostic remains an unexpanded OPEN leaf.

| Finding |
|---|
| No inference or supporting commitment is established; an empty proposal/correction outcome is bounded failure to find a route, not a refutation. |

Route `42a72010f361:r0`: Static-semantics target remains OPEN despite a licensed sign attempt.

| Finding |
|---|
| Its static-conjunction premise references an attacked-view commitment from von Fintel and Gillies 2007 PDF page 25. It remains open instead of being accepted as an endorsed global premise. |
| CQ2 is marked answered=true but cites the attacked-view commitment; the stance restriction prevents this from establishing closure. The target 3 polarity pair uses the same problematic material. |
| The source already explains the no-asymmetry prediction on PDF pages 25–26, so the target's native new-atom verdict does not establish a new literature contribution. |

Route `61c78dfec51e:r0`: Negation of static-semantics target remains OPEN, with a polarity error in its support.

| Finding |
|---|
| The sign proposal targets the negation, but both CQ answers argue that static conjunction semantics cannot explain order sensitivity: they support the positive target rather than its negation. |
| The static-view premise is attacked and remains open; CQ evidence also cites it. Native OPEN withholds closure, but the model's affirmative CQ flags are not substantively reliable. |


## Model-written summaries and review

Read all six model-written summaries against the final published graphs, the seven referenced frozen commitments and provenance records, the sign scheme, and original source pages. The summaries generally preserve closure status and source limitations. The last summary correctly recognizes its CQ/conclusion polarity mismatch but misstates which nodes remain on the frontier. Original model text is retained; notes below clarify formal status, stance and criterion 3 limits.

| Route | Model-written summary | Review note |
|---|---|---|
| 9a35a6febc9d:r0 | Target polarity: positive. The recorded inference uses GSV’s endorsed commitments that conjunction updates sequentially and “might” tests consistency (n_seq_conj), and that the order of raining/not-raining information affects consistency (n_order), to support information-state-sensitive modal evaluation. The graph is CLOSED relative to these formalized commitments and its licensed inference, not proof that the commitments or formalization are true; the contribution remains a candidate, with solver checks reporting counterexamples to deductive closure. The source text for n_order lists omitted support gsv1996:r18-35:inf1, which is not supplied here, so that premise’s explanatory support is incomplete. | Both distinct supports are from GSV1996 (one paper), so criterion 3 fails. The counterexamples reported by the novelty checks show that T does not classically entail the fresh target atom; they do not invalidate the licensed defeasible sign step. The stronger claim that every adequate semantics must be information-state-sensitive remains substantively unestablished; see the route review. |
| 14deb2a30da4:r0 | This OPEN, negation-polarity route targets the denial that an adequate epistemic-modal semantics must be information-state-sensitive. Its inference proposes that truth conditions can be information-state-independent and that epistemic modal claims can be evaluated by them, but both premises remain open; no recorded step establishes the denial. Frozen commitments offer competing considerations, not support for those premises: MacFarlane’s endorsed author claim allows truth to vary with contexts of use and assessment, while Yalcin’s endorsed author claim distinguishes world and information coordinates and relates incoherence to joint acceptability relative to one information state. MacFarlane’s provenance lists an omitted supporting inference, so the supplied conclusion relies on support not included here. These are reported author claims, not independently verified. The route remains open. | MacFarlane and Yalcin are labelled endorsed in frozen provenance. The phrase reported author claims in this summary describes attribution, not the reported stance category. Both premise leaves repeat the root negation at formula level and remain open. |
| edd5e3e69fbe:r0 | Positive route to the target: order sensitivity is a diagnostic constraint on an adequate epistemic-modal semantics. Its inference combines the endorsed claims that conjunction updates information sequentially and “might” tests consistency, and that reversing the order of the rain statements changes whether the discourse is consistent. The supporting commitment about the order contrast lists omitted support gsv1996:r18-35:inf1, which is not represented in this route. The graph is CLOSED relative to its supplied commitments and licensed steps; this does not establish their truth or faithful formalization. It supports a diagnostic constraint, not that this account is uniquely correct or decisive for every semantic theory. | Both distinct supports are from the same GSV1996 paper, and they duplicate the support set of the other closed route. The graph is mechanically CLOSED-derived, but neither cross-paper qualification nor a new literature contribution is established. The diagnostic inference remains a candidate interpretation of the source example. |
| 66bacb38c304:r0 | This OPEN route targets the negation of the proposed diagnostic claim that order sensitivity in epistemic-modal discourse constrains adequate semantics. Its sole recorded step is a leaf stating that negation; no supporting steps, frozen commitments, or support provenance are supplied. The route remains open and does not establish the negation. |  |
| 42a72010f361:r0 | Target-polarity route, OPEN. Its inference combines the conditional attacked-view assumption that static conjunction semantics assigns the same intersection condition to both sentence orders with the reported contrast that “might be raining” followed by “not raining” is acceptable, but the reverse order is inconsistent. This supports the target that such a static account cannot explain order-sensitive epistemic-modal discourse. The reported contrast is attributed to Groenendijk, Stokhof and Veltman as endorsed, but its provenance lists omitted support gsv1996:r18-35:inf1; that omitted support is not supplied here. A further endorsed commitment qualifies that the paper’s modal semantics does not exhaust “might,” while treating consistency testing as essential for epistemic modality. The recorded CQ support also reports a dynamic system’s order asymmetry. The route remains OPEN relative to the supplied commitments and licensed steps; the conditional static assumption is an attacked view, not an endorsed premise, and the route does not establish its truth or faithful formalization. | The summary's supports-the-target wording is conditional on the attacked static-view assumption. That record is not an admissible endorsed global premise or CQ source here; the root and static-view leaf remain open. The source itself already explains the no-asymmetry objection on PDF pages 25–26. |
| 61c78dfec51e:r0 | Polarity is negation: the recorded conclusion formally negates the proposed target. The inference pairs a static-conjunction account—which predicts the same truth conditions for both sentence orders—with an attributed report that discourse behavior differs by order. The graph’s CQ answers say this mismatch supports the claim that the account cannot explain the behavior, although the recorded conclusion has opposite polarity. The static account is an attacked view, not an endorsed premise; the order-sensitivity report is attributed to Groenendijk, Stokhof and Veltman as endorsed. That report omits support gsv1996:r18-35:inf1, so its use assumes that omitted support. The route is OPEN: both supporting leaves remain on the frontier, so it is not closed relative to the supplied commitments and licensed steps. | The summary correctly identifies that the CQ answers favor the positive target while the graph concludes its negation. Its statement that both supporting leaves remain on the frontier is inaccurate: frontier is n0 (root) and n1 (attacked static-view premise); n2 (endorsed order observation) is closed. The separate Tier 1 repair suggestion was not licensed or applied. |


## Usage, human actions and stops

| Scope | MODEL receipts | Tokens | API USD | Unknown usage |
|---|---|---|---|---|
| New fork including summaries | 50 | 3013057 | 0.0 | 0 |
| Fresh schema/canary | 19 | 91387 | 0.0 | 0 |
| New task total | 69 | 3104444 | 0.0 | 0 |
| Inherited prefix | 447 | 16204728 | 110.395145 | 2 |

Subscription dollar equivalent is unavailable; zero new API spend is not zero subscription cost. Native exit timing: {"phase": "fork", "exit_code": 0, "started_epoch": 1793167317.0566452, "ended_epoch": 1793170933.2048843, "wall_seconds": 3616.148239850998}. Summed model wall time differs from elapsed wall time. 0 resume receipts, 0 subscription-limit events, 0 unsettled calls. The two-hour persistent usage-limit watchdog was retained.

| Time | Human action | Recorded input |
|---|---|---|
| 2026-10-28T06:00:15.955531+00:00 | codex-schema-preflight | ["codex-schema-preflight", "--config", "/home/dev/ara-scaffold/runs/inputs/codex-fork-3-config.yaml", "--run-dir", "/home/dev/ara-scaffold/runs/codex-fork-3-schema-preflight"] |
| 2026-10-28T06:01:45.480161+00:00 | isolation-preflight | Native standalone canary required by /home/dev/ara-work/briefs/zeta-fork-pilot-3.md; no API and no route selection. |
| 2026-10-28T06:02:22.896986+00:00 | fork-from-freeze | ["fork-from-freeze", "--source-run", "/home/dev/ara-scaffold/runs/codex-pilot-5", "--run-dir", "/home/dev/ara-scaffold/runs/codex-fork-3", "--codex-schema-preflight-log", "/home/dev/ara-scaffold/runs/codex-fork-3-schema-preflight/events.jsonl"] |
| 2026-10-28T07:02:47.581369+00:00 | operator-success-criteria | Fork pilot 3 brief and approved success criteria; full verbatim input retained in native HUMAN receipt and fork-audit.json. |
| 2026-10-28T07:02:57.228277+00:00 | operator-review-approval | Note (same task): kappa4 approved xi r21 (a272ebe) with 0 blocking; it is now merged to main. Fork pilot 3 results are not provisional — drop that label in your handoff. |
| 2026-10-28T07:03:12.339380+00:00 | route-summary-reporting | Fork pilot 3 brief and approved success criteria; full verbatim input retained in native HUMAN receipt and fork-audit.json. |

| Time | Stage | Status/reason |
|---|---|---|

Offline continuation after operator-reported capacity error: {"timestamp": "2026-10-28T07:24:42.498477+00:00", "label": "HUMAN", "stage": "offline-report-continuation", "text": "Same task: capacity error. Continue fork pilot 3 from where you stopped.", "action": "Reused existing offline report PID3360676 and finisher; no pilot restart, no native log mutation and no further model calls.", "model_work_finished_at": "2026-10-28T07:09:01.837688+00:00"}


## Report verification and limitations

Native report: 58 lineage inputs; 139,978 event occurrences reconstructed from 41,385 unique event bodies; 1,607 artifact copies and 4,331 links checked. Logs and anchors unchanged. Delivered 45,352 native files / 4,692,640,032 bytes with matching hashes, including all sidecars. HTML 1,277,620 bytes (1.277620 decimal MB), opened in Chromium 143.0.7499.4; 0 page errors and 0 missing anchors. Desktop 1440/1440 pixels; mobile 390/409 pixels (viewport/document).

The native browser layout check is FAIL solely because the mobile document overflows its viewport by 19 pixels. Desktop rendering, anchors and page-error checks pass; criterion 4 passes for rendering and summary coverage, with this layout limitation disclosed.

7692 copied freeze-prefix occurrences are incorrectly displayed as original_in across the fork inputs; import-origin-overlay.json identifies them. Accounting deduplicates event bodies and separates inherited usage. Raw native report bytes are preserved.

tree-browser-check.json: {"passed": true, "scope": "Current Fork pilot 3 authenticated trace", "current_pilot_search_details": 12, "expanded_search": "Search 9a35a6febc9d:0", "run_index": 57, "proof_nodes": 3, "state_depth": 1, "proof_depth": 1, "linked_files": [{"path": "trees/run-57-search-0.json", "bytes": 21136}, {"path": "trees/run-57-search-0.dot", "bytes": 192}], "linked_json_opened": true, "dot_valid_header": true, "tree_keys": ["begin_seq", "version", "search_id", "target", "states", "receipts", "decisions", "complete", "authenticated", "source", "issues", "completed_routes", "nodes"], "screenshot": "/home/dev/ara-scaffold/runs/codex-fork-3-control/report-expanded-current-tree.png", "svg_available": false}

companion-browser-check.json: {"passed": true, "articles": 6, "errors": [], "missing": [], "desktop": {"width": 1440, "scrollWidth": 1440}, "mobile": {"width": 390, "scrollWidth": 390}, "browser": "143.0.7499.4"}

Verified duplicate cleanup: {"source": "/home/dev/ara-scaffold/runs/codex-fork-2-report", "preserved_delivery": "/home/dev/ara-work/reports/overnight/fork2", "file_count": 44093, "bytes": 4577580575, "all_hashes_matched_before_removal": true, "scope": "Only duplicate generated report; native runs, control evidence and delivery preserved"}

Verified duplicate cleanup: {"files": [{"path": "/home/dev/ara-scaffold/runs/overnight2-report/report.html", "preserved": "/home/dev/ara-work/reports/overnight/report-part2.html", "bytes": 1773973093, "sha256": "eab7e8d32bcd9c5c1761078f18ed625fbd15a1fe61ebe6139449997d48d1c34f"}, {"path": "/home/dev/ara-scaffold/runs/overnight2-report/report.md", "preserved": "/home/dev/ara-work/reports/overnight/report-part2.md", "bytes": 1294519053, "sha256": "b52c950c614982f14c77f1a458b24e9492bebc9f50ff4791f4252f1608a82a16"}, {"path": "/home/dev/ara-scaffold/runs/overnight2-report/data.json", "preserved": "/home/dev/ara-work/reports/overnight/report-part2.json", "bytes": 294547609, "sha256": "a8dc1250da31153f8bd24b917621266072752866f58dc5d8665e38f2a9e4e2bf"}], "bytes": 3363039755, "all_hashes_matched_before_removal": true, "scope": "Only three duplicate generated report indexes; native runs, delivered indexes and all sidecars preserved"}


## Finding placement and next step

| Finding | Placement |
|---|---|
| 1 | Final state and no selection — Opening |
| 2 | Revision, configuration, preflight and model-identity limit — Execution and source preservation |
| 3 | Inherited coverage, citations, stance and omissions — Execution and source preservation |
| 4 | All target gate verdicts and novelty evidence — Targets and novelty gates |
| 5 | Search completeness, categories and support — Searches and routes |
| 6 | Substantive scheme and main-thesis fitness — Substantive review of CLOSED-derived routes |
| 7 | Summary coverage and accuracy — Model-written summaries and review |
| 8 | Usage, human inputs, refusals and recovery — Usage, human actions and stops |
| 9 | Copy integrity, rendering and display limits — Report verification and limitations |
| 10 | Fork provenance display mislabelling — Report verification and limitations |
| 11 | Source/handoff preservation and disk reclamation — Execution and source preservation; Report verification and limitations |
| 12 | Approved criteria verdicts — Acceptable pilot — approved criteria 1–4 |
| 13 | Open-route substantive evidence and support fit — Open-route evidence and support fit |
| 14 | Confirmed code review and merge status — Opening |
| 15 | Paired conflict, unlicensed repair suggestion and forward analysis — Paired conflicts and forward analysis |

15 findings, 15 placed.

No route selection, essay or additional pilot was started.

DONE zeta fork3 targets=3 derived_closed=2 structural_closed=0 open=4 criteria=P,P,F,P status=awaiting-selection report=/home/dev/ara-work/reports/overnight/fork3/report.html
