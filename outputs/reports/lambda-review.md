# Lambda non-author review

**Verdict: fix-first.** One BLOCKING finding (diagnostic request-content echo), one SHOULD-FIX finding (null-inventory correction recovery), and four NOTE findings. The four completed probe papers pass structural v4 validation and are reusable; `wright2007` is not. Full pytest and all 200 negative controls passed, but the new counterexamples are outside their coverage.

Subject: `/home/dev/ara-work/kappa`, `fix/extraction-acceptance`, head `f6c89063bb3d7af25570ad9ec47c3187e3a6fa9d`, base `be7468df12d4c0422d54f8ccd881d653cd92bdd4`. Read both requested briefs before reviewing implementation and the author's report. No branch edits, delegation, live requests, or paid calls. The mutation runner executed in a separate clone of this exact head. Both checkouts were clean at that head after verification. Review was performed directly, without a delegated or cross-model pass, as required by the brief.

## Findings

### F1 — BLOCKING: error-message scrubbing does not guarantee no request-content echo

**Location:** `ara/runtime/providers.py:260–269`; callers `ara/runtime/calls.py:290` and `ara/runtime/cli.py:268`.

**Failure scenario:** a provider returns a structured diagnostic such as `messages.0.content.0.text is invalid: QQQQQQQQ`, where the submitted placeholder prompt is `PPPPPPPP QQQQQQQQ RRRRRRRR`. The error helper retains `QQQQQQQQ`. Its marker expression recognizes `messages:` but not this normal dotted field path; exact whole-prompt/whole-line substitution does not remove a fragment; the message contains no JSON braces to trigger the final truncation. The CLI token-counter error path supplies no prompt at all. Arbitrary diagnostic text can therefore echo request content, despite the round-two requirement and the report's unconditional no-echo claim. This is an executed placeholder counterexample, not evidence of an actual secret leak in the paid probe.

**Fix direction:** define a conservative diagnostic contract that retains status, validated error type/request ID, and only recognized provider-generated diagnostic text; suppress unrecognized free-form message bodies rather than claiming substring redaction is complete. Add adversarial tests for dotted paths, partial/escaped echoes and token-counter failures. Preserve useful schema-compiler diagnostics through explicit parsing. Treat credential substitution as defense in depth, not a proof that arbitrary error strings contain no secrets.

### F2 — SHOULD-FIX: null inventory is normalized for validation but not for correction recovery

**Location:** `ara/runtime/calls.py:480–485`, with `merge_extraction_patch` inventory requirement at `:68` and normalization at `:57`.

**Failure scenario:** the new initial wire returns `items: null` with an invalid empty disposition. The validation boundary converts null to an empty list and rejects the disposition, correctly. Recovery then decodes the original raw response again and passes its still-null inventory to `merge_extraction_patch`, which immediately raises `candidate cannot support targeted correction`. A placeholder native extraction configured for two corrections makes only one call; an available valid next response is never requested. This is a newly exposed recovery hole in the wire shape introduced here, and can unnecessarily consume the full run's failed-paper allowance.

**Fix direction:** apply the same content-free normalization to the decoded rejected candidate before inventory merging, retaining the original MODEL receipt and normalization evidence. Test a rejected null-inventory response followed by a valid correction, including the two-attempt limit. Do not normalize malformed/ambiguous item identities into acceptance.

### F3 — NOTE: item preservation does not establish gap preservation or semantic fidelity

**Location:** `ara/runtime/calls.py:77` and `:483`; `prompts/extract_paper.txt:10`.

**Failure scenario:** an initial candidate has an out-of-bounds item plus a declared gap. A patch repairs the locator, leaves the item texts unchanged, sets `new_gaps=[]` and claims complete coverage. Native extraction accepts eight items with zero obligations in the placeholder reproduction. The merge preserves item IDs but replaces the rest of the envelope. Corrections are explicitly authorized to revise coverage metadata, and this top-level replacement predates this branch; this is therefore a disclosed limit, not a newly demonstrated contract regression. A declared gap could be legitimately corrected or improperly dismissed, and structural validation cannot distinguish them.

The probe's `veltman1996` first window also has a rejected correction where a candidate's one gap becomes zero before the next, accepted correction. The accepted first window retains no obligation from that candidate. This does **not** prove an omission in the final accepted graph: the gap may have been a false discovery or resolved by corrected content. The separate second-window sequence encounters output exhaustion and subdivision. No source-content quotation or semantic omission claim is made here.

**Fix direction:** if “nothing silently dropped” is intended to include rejected candidates' gap discoveries, introduce explicit retained gap identities and evidence-backed dismissal/resolution semantics, then include that behavior in acceptance identity and controls. Until then, describe the guarantee precisely as item-inventory preservation and accepted-obligation accounting; do not equate a passing graph validator with faithful extraction.

### F4 — NOTE: the required paid acceptance threshold remains unmet

**Location:** `/home/dev/ara-work/reports/kappa-acceptance.md:168`, “Round 2 probe outcomes and recovery”; native refusal guard `ara/runtime/calls.py:256` and publication stop `ara/runtime/extraction.py:377`.

**Failure scenario:** treating the green schema gate or tests as permission to describe the six-paper probe as successful would overstate the evidence. Four papers completed; `kolodnymacfarlane2010` ended in provider refusal and `moss2015` had no generation dispatch because its reservation exceeded the remaining cap. The requested threshold was five of six. The author states this honestly.

**Fix direction:** keep the threshold failure in the full-run decision and budget plan. No successful partial-source or 81-page stress extraction is established by this probe. Do not characterize the budget-blocked sixth paper as a model rejection or the refusal as a known policy cause.

### F5 — NOTE: v4 resume requires re-extracting wright2007

**Location:** `ara/runtime/extraction.py:26`, `:435`, `:472–476`.

**Failure scenario:** a full-run plan that assumes the prior accepted `wright2007` is reusable under v4 will understate needed extraction work. Resume uses exact acceptance identity, including version, prompt/schema hashes and effective model policy. Old compatible accounting is imported independently of graph reuse.

**Fix direction:** budget a new `wright2007` extraction. Preserve all origin logs and use the matching effective profile to reuse the four v4 probe successes. Do not relabel the old graph's acceptance identity to avoid the new call.

### F6 — NOTE: reconciliation permits continuation, not measured historical billing

**Location:** `ara/runtime/budget.py:44–60`; `ara/runtime/export.py:113`.

**Failure scenario:** an operator could mistake the opt-in reconciliation marker for measured spend or for clearance of an interrupted dispatch. The reviewed implementation correctly requires explicit `count-at-reservation`, keeps unknown receipts and their full charges, labels them upper bounds, and still refuses a missing terminal receipt. The prior unknown total remains USD0.897910; it has not become measured usage.

**Fix direction:** retain the explicit option and imported receipts in the full-run command and use accounted totals for admission. Preserve the methodology's incomplete-actual-accounting label. Do not delete reservations or treat the imported history as free.

## Coverage and evidence

Receipt, resume, accounting, pytest and sequential mutation audits are complete. Executed placeholder counterexamples are in `lambda-evidence/edge_checks.py` and `lambda-evidence/edge-checks.txt` beside this report. Candidate gap loss was downgraded to the F3 limitation after reading the explicit correction contract; it is not used to claim the accepted papers are semantically invalid.

### Normalization and patch boundaries

The only new normalizations are `items: null -> []` and empty/null optional `empty_reason -> absent`. They remove no supplied item, text, attribution, link, page locator, or substantive disposition. Original raw responses remain in MODEL receipts; normalization events name the transformation. A missing/blank disposition still fails for an empty initial range; a substantive disposition with nonempty items still fails. `extraction_defaults` fills kind-inapplicable edge defaults, but does not overwrite supplied invalid fields. The F2 recovery hole concerns re-decoding the raw value, not false acceptance by normalization.

ID merging accepts repeated unchanged items, retains omitted items, replaces named proposed items, and carries additions/changes from a rejected patch into the second attempt. Duplicate or unusable IDs refuse. Whole merged candidates are schema- and semantics-checked. Already accepted evidence supplied through reconciliation cannot be redeclared. Proposed rejected items may change during correction; that is the stated contract, not immutable-evidence mutation. The explicit loop admits initial plus at most two corrections, subject to native per-paper and enclosing budgets; generic validation retries do not multiply it. F3 limits the broader “nothing silently dropped” claim.

### Reconciliation against the imported real history

Independently executed the three Budget paths using verified imports of the probe history. Default `refuse` stopped on unknown usage. Explicit `count-at-reservation` continued at **USD19.455305**, preserving every imported event and the **USD0.897910** unknown portion; measured cost remains **USD18.557395**. Adding an unreceipted `call_start` still refused with `interrupted provider call: actual spend unknown`. No request was dispatched. Evidence: `lambda-evidence/budget_audit.py` and `lambda-evidence/budget-audit.json`.

### Native schema-preflight coverage

`ara/runtime/preflight.py:8–22` covers every response-shaping branch in `ModelCalls.response_schema`: initial, empty-candidate correction, nonempty-candidate correction, reconciliation without obligations, reconciliation with obligations. Reconciliation corrections reduce to the same latter two projected wires; page/evidence window contents and context-request continuations do not create additional schema branches. Each applicable complete grammar includes all three kind families. The explicit null empty envelope is closed and standalone.

Independently compared the five hashes in the successful live gate's existing receipts with the schemas projected from **every** probe MODEL request: all three distinct grammars actually used by the probe are included. The two additional grammars remain covered by the gate inventory. The gate uses the native extraction model/configuration and Messages endpoint, counted reservations and receipts, a placeholder prompt and one output token, with cache reads/writes disabled. It accepts `max_tokens` as grammar compilation evidence only. No new live schema test was made; service acceptance evidence is the author's retained five successful receipts, not a fresh Lambda service check.

### Probe receipts and v4 validation

Verified the probe's **450-record hash chain and anchor**, and recursively verified pinned imported ancestry. Replayed **all 11 accepted response receipts** through the current native response validator, including seeded recorded correction candidates and reconciliation windows. Canonically compared each replayed item list with its saved immutable range/reconciliation graph. All matched. Nine accepted responses belong to the four completed papers; two belong to the later refused paper and do not count as a completed paper.

Independently checked final graph IDs, source/page bounds, nonblank text/attribution, references, inference endpoint/kind constraints, obligation/resolution closure and accepted merge hashes. All four completed outcomes carry `rich-paper-acceptance-v4`:

| Paper | Items | Obligations resolved | Native resume |
| --- | ---: | ---: | --- |
| rothschild2012 | 71 | 0 | reusable |
| knobeyalcin2014 | 58 | 0 | reusable |
| macfarlane2011 | 169 | 1 | reusable |
| veltman1996 | 267 | 1 | reusable |

Total: **565 accepted items**. This is structural v4 validity, not an independent semantic fidelity judgment. No paper content is quoted in this review.

The current probe batch has **23 call-starts and 23 MODEL receipts**, measured new cost **USD11.456405**, and no unreceipted dispatch. `kolodnymacfarlane2010` has a failed outcome with no accepted-paper items; the `refusal` stop is rejected before parsing, and its usage remains charged. `moss2015` has no generation call; its failure is reservation admission. No `extraction_completed` event or completed literature artifact exists. These checks agree with the author's outcome/cost report and do not support claiming 5/6 success.

Called native `resume_papers` with both prior full26 runs and the probe, current source intake and the probe's effective configuration. It returned exactly **knobeyalcin2014, macfarlane2011, rothschild2012, veltman1996**; `wright2007` was not reused. The original ancestry stays available and imported costs are not dependent on graph reuse. Evidence: `lambda-evidence/receipt_audit.py` and `lambda-evidence/receipt-audit.json`.

### Verification execution and mutation review

Executed `uv run pytest -q` in the reviewed checkout: **495 passed, 2 skipped / 497 collected**, exit 0, **284.67 seconds**. The two opt-in paid tests were skipped. After that process completed, started `uv run python tests/integration/negative_controls.py` in `/home/dev/ara-work/lambda-control-checkout`, an exact-head shared clone with its own offline-created locked environment. The runner temporarily mutates and restores that disposable tree, leaving the reviewed branch untouched. **All 200/200 mutations failed as intended (exit 1), all restored tests passed (exit 0), and the runner exited 0.** The reviewed checkout and disposable control checkout were both clean at the requested head afterwards. Transcripts and result manifests are in `lambda-evidence/pytest.txt`, `lambda-evidence/negative-controls.txt`, `lambda-evidence/negative-control-results.json`, and `lambda-evidence/verification.json`. Individual mutant/restoration transcripts remain under the control checkout’s `runs/delta-controls/`.

Read the new mutation definitions and the targeted tests, including these twelve controls:

| Mutation | Behavior it must detect |
| --- | --- |
| expanded_extraction_schema_count | token admission counting the expanded wire |
| typed_extraction_envelope_wire | provider-compatible typed envelopes |
| empty_optional_normalization | removal/logging of content-free disposition |
| correction_second_attempt | availability of the second correction |
| correction_accumulated_inventory | retaining rejected-patch changes/additions |
| disposition_wire_separation | forbidding substantive disposition with content |
| standalone_envelope_alternatives | removing sibling object constraints beside alternatives |
| null_inventory_normalization | logged null-to-empty conversion with raw preservation |
| unknown_reconciliation_policy | opt-in continuation of unknown reservations |
| reconciled_reservation_charge | retaining their full cost |
| provider_error_receipt | emitting the allowlisted diagnostic receipt |
| schema_gate_inventory | dispatching the entire five-schema inventory |

The existing error test checks a labeled body echo and environment-secret substitution; it does not cover F1's partial dotted-path echo. The null normalization test covers a successful response, not F2's rejected-then-corrected null candidate. Green controls do not negate either independently reproduced defect.


## Finding placement and remaining limits

| Finding that changes the reader's action | Placement |
| --- | --- |
| F1: Diagnostic text can echo request fragments; the no-echo guarantee fails | Findings / F1; Verification execution and mutation review |
| F2: Rejected null inventory bypasses configured correction recovery | Findings / F2; Normalization and patch boundaries |
| F3: Proposed gap metadata can disappear; structure is not fidelity | Findings / F3; Normalization and patch boundaries; Probe receipts and v4 validation |
| F4: Paid acceptance remains 4/6; refusal and 81-page stress case did not succeed | Findings / F4; Probe receipts and v4 validation |
| F5: Reuse exactly four v4 graphs; budget a new wright2007 extraction | Findings / F5; Probe receipts and v4 validation |
| F6: Explicit reconciliation preserves unknown upper bounds and refuses interrupted dispatch | Findings / F6; Reconciliation against the imported real history |

6 findings, 6 placed

No source fixes were applied. No new service acceptance, semantic extraction-quality verdict, successful six-paper completion, or full 26-paper reliability claim is made. Repair F1/F2 and verify their targeted regressions before treating this branch as ready; retain F3–F6 in the full-run decision. If a repair changes acceptance semantics or its identity, reassess reuse rather than assuming the current four-paper result persists.

DONE lambda review verdict=fix-first blocking=1 should_fix=1 tests=495/497 negctl=pass reusable_papers=knobeyalcin2014,macfarlane2011,rothschild2012,veltman1996

## Re-review

**Verdict: merge. F1 and F2 are resolved by design and verified; no BLOCKING or SHOULD-FIX finding remains in this narrow re-review.** F3 is accurately documented and explicitly authorized for deferral. The four v4 probe successes remain reusable. This verdict applies to `0eb8592` and supersedes the original fix-first verdict above; the earlier review is retained as history.

Scope: narrow non-author re-review of F1/F2, F3 wording and continued v4 reuse at `0eb85924afeb01aac44e5bc0ca5f2714c6a99823`, against `f6c89063bb3d7af25570ad9ec47c3187e3a6fa9d`. Read `briefs/lambda-rereview.md`, `briefs/kappa-round-3.md` and the author's Round 3 report. No source changes, delegation, live provider requests or paid calls. Pytest ran in the reviewed checkout; the mutation runner followed sequentially in an exact-head disposable clone at `/home/dev/ara-work/lambda-rereview-control-checkout`.

### F1 resolved by design

`ara/runtime/providers.py:250` now treats diagnostics as a parsed contract rather than free text to scrub. HTTP error status is a real integer in 400–599, error type is enumerated, and request ID must fully match the bounded `req_` syntax. Arbitrary exception wrappers, bodies and unrecognized message strings do not flow into diagnostic output. The only retained message is the recognized schema-compiler sentence: its whole string must match, its variable tokens must be unique members of four known schema keywords, and the message is reconstructed in canonical keyword order. Prefixes, suffixes, newline additions, unknown keywords and escaped/partial echoes cannot carry arbitrary captured text through that message path. Unrecognized diagnostics explicitly say `Provider diagnostic suppressed.`

The model boundary uses this helper (`ara/runtime/calls.py:290`), as does the CLI API-error handler before console output, runtime-error recording and export (`ara/runtime/cli.py:269`). The metadata and message rules do not depend on having the original prompt, addressing the token-counter path too. The tradeoff is deliberate: unknown compiler messages are suppressed until supported by an explicit parser.

Re-executed the original placeholder dotted-path attack: the helper no longer retains its fragment, and a native model-call error receipt contains the suppression message. F1's original failure is resolved; this is not a claim that the old paid probe leaked a secret.

### F2 resolved by design

`ara/runtime/calls.py:481` applies the same existing content-free normalization to the re-decoded rejected response before `merge_extraction_patch`, and logs a `correction_candidate` normalization event. Raw MODEL receipts remain untouched. The merge still rejects ambiguous IDs; complete merged candidates still pass the existing schema and semantic checks. The initial-plus-two-corrections loop, paper allowances and enclosing budgets are unchanged.

Re-executed the original null-inventory reproduction: the initial invalid response now reaches the available valid correction and returns eight placeholder items after **two calls**, instead of terminating after one. New tests cover valid correction after one or two attempts, exhaustion at three total calls with an unused fourth response, preserved raw data, normalization events, and refusal of missing/blank/non-string/duplicate IDs. F2 is resolved without changing the accepted graph rules.

### F3 wording is accurate; deferral is authorized

`DECISIONS.md:1501` and the author's “Round 3 F3” section correctly narrow the guarantee to **item-inventory preservation across corrections and accepted-obligation accounting**. Rejected gap declarations can still disappear when a patch replaces coverage metadata; this does not prove a real accepted graph omitted evidence. The original placeholder reproduction still accepts eight items with zero obligations after the gap is removed, matching the new wording.

The round-three brief explicitly allows documenting and deferring the stronger gap-lifecycle rule when it exceeds the approximately two-hour scope. Stable pre-acceptance gap identities, evidence-backed resolution/dismissal, subdivision handling and changed schemas/reuse rules are a substantive extension; retaining this disclosed limit is consistent with that authorization. No new F3 blocker is imposed by this narrow re-review.

### Acceptance identity, wire schemas and reuse

Compared the actual probe's effective acceptance identity at the old and new commits: they are identical, including `rich-paper-acceptance-v4`, source prompt/schema hashes and effective provider/model policy. Independently projected all **nine response-shaping variants / five distinct grammars** at both revisions: every corresponding wire hash is identical. Configuration, prompts, schemas, extraction acceptance identity source and preflight source are unchanged in the diff. F1 affects diagnostics; F2 makes the existing normalization consistent on recovery, while accepted graph validation is unchanged. A live grammar gate is not needed for this delta and was not performed.

Native `resume_papers` at the new head verified the pinned probe ancestry and current source inputs and returned all four successes: **knobeyalcin2014, macfarlane2011, rothschild2012, veltman1996**, totaling **565 items**. Their stored acceptance identities exactly match the current effective identity. No provider was constructed or dispatched. Evidence: `lambda-rereview-evidence/reuse.py` and `reuse.json`. Comparison evidence is in `lambda-rereview-evidence/contracts-base.json`, `contracts-head.json` and `contracts.py` beside this report. Reproduction evidence is in `lambda-rereview-evidence/edge-checks.txt` and `edge_checks.py`.

### New mutations read

Read all nine new production-wire mutations and their owning tests:

| Mutation | Failure it exposes |
| --- | --- |
| diagnostic_suppression | arbitrary provider prose entering the receipt |
| diagnostic_status_validation | invalid or non-integer status values surviving |
| diagnostic_type_validation | unrecognized error types surviving |
| diagnostic_request_id_validation | malformed or unbounded request IDs surviving |
| diagnostic_schema_recognition | losing the recognized useful compiler diagnostic |
| diagnostic_cli_counter_boundary | native CLI token-counter exception text leaking |
| diagnostic_compiler_keywords | unknown captured keywords entering the diagnostic |
| diagnostic_compiler_full_sentence | accepting a recognized prefix with an unsafe suffix |
| rejected_candidate_normalization | null inventory terminating before correction |

These controls target the defects and parser boundaries directly, including both suppression and preservation of the specifically supported diagnostic. Independent `uv run pytest -q` completed with **515 passed, 2 skipped / 517 collected**, exit 0, in **283.36 seconds**. Only after that process completed, ran `uv run python tests/integration/negative_controls.py` in the disposable clone: **209/209 mutants failed with exit 1, every restored test passed with exit 0, and the runner exited 0**. All nine new controls are included. Both the reviewed checkout and control checkout were clean at the exact requested head after completion. Transcripts, result manifests and final metadata are in `lambda-rereview-evidence/pytest.txt`, `negative-controls.txt`, `negative-control-results.json` and `verification.json`. Individual mutant/restoration transcripts remain in the disposable checkout’s `runs/delta-controls/`.


### Retained full-run limits and finding placement

F4–F6 are unchanged: the paid probe is still **4/6**, not the required 5/6; the partial-source refusal and unattempted 81-page extraction are not successful stress-case evidence. Budget a new `wright2007` extraction rather than relabeling its older graph. Preserve/import all history and explicitly use count-at-reservation when continuing: the recorded USD19.455305 total includes USD0.897910 of unknown reservations, which remain upper bounds rather than measured billing. This re-review adds no paid usage and does not establish full-corpus semantic reliability. These are retained limits, not reopened F1/F2 defects.

| Prior finding / action-relevant result | Re-review placement |
| --- | --- |
| F1 closed; arbitrary diagnostics suppressed, recognized compiler sentence retained | F1 resolved by design; New mutations read |
| F2 closed; null-candidate correction now works within existing limits | F2 resolved by design; New mutations read |
| F3 remains a disclosed, authorized gap-preservation limitation | F3 wording is accurate; deferral is authorized |
| F4 remains: 4/6 probe and stress-case limits | Retained full-run limits and finding placement |
| F5: four v4 successes reusable; wright2007 still needs extraction | Acceptance identity, wire schemas and reuse; Retained full-run limits and finding placement |
| F6: inherited unknown reservations remain charged and labelled | Retained full-run limits and finding placement |

6 findings, 6 placed

DONE lambda rereview verdict=merge blocking=0 should_fix=0 tests=515/517 negctl=pass v4_reuse=yes
