# Kappa extraction acceptance robustness

> Latest result: Round 3 fixes Lambda F1/F2 with offline verification and no paid calls. F3 is explicitly deferred; the prior paid acceptance threshold remains failed at 4/6. Earlier sections are retained as history.

**Live acceptance target not met: 0/6 papers accepted.** The first native probe stopped on a provider `BadRequestError` before returning an extraction response; five papers were not attempted. USD0.886705 is retained as an **unknown-usage reservation**, not a measured charge. No retry, accounting reset, or second paid run occurred.

Probe revision: `c6f9e0553172b198de161d5d2828c6218c0b31a0`. Final delivery revision: `c07a1530cae79496811cce81f935dd15e882a468` (offline wire-schema correction, fully verified locally). Both commits are local only; the worktree is clean. Branch `fix/extraction-acceptance`, isolated checkout `/home/dev/ara-work/kappa`, base `be7468df12d4c0422d54f8ccd881d653cd92bdd4`. The primary checkout remains clean at the requested base. No push or non-author review has occurred.

## Behavior and preservation

Native extraction and reconciliation share one response-validation boundary. Full extraction now permits two targeted corrections per response (configurable 0/1/2), with ordinary paper continuation/cost and enclosing campaign admission on every call. Patches retain omitted items, accept unchanged items, and preserve changes/additions from a rejected first patch for the next correction. Ambiguous inventories still refuse. Correction feedback names the failed constraint and valid physical paper/window pages.

The initial-range wire separates nonempty content from empty-range dispositions. Nonempty-candidate corrections cannot declare a substantive empty disposition. Existing mode- and kind-specific wire restrictions remain. Only an empty/null optional disposition is normalized away, with a dedicated event and the original raw response retained. Blank attribution, invalid source citations/endpoints, unsupported inference structure, inconsistent coverage and unresolved obligations remain errors. Acceptance identity is v3, so prior graphs are not silently reused under a changed contract; historical charges remain importable.

Implementation rationale is in `DECISIONS.md`, section “Kappa: extraction response acceptance and bounded correction.”

## Offline replay

The harness `tools/replay_extraction.py` reads ignored logs, forbids socket connections, and uses the same native schema, merge and semantic-validation path. It verifies PDF hashes and page text against recorded requests, then replays each original source window and candidate independently and deduplicates identical copied ancestor receipts. It does not predict new model corrections, execute the complete obligation/context traversal, or prove completed-paper coverage or semantic fidelity. Replay’s local counters and accounting receipts are synthetic offline artifacts, not new charges.

Sources: `/home/dev/ara-scaffold/runs/full26-extraction/events.jsonl` and `/home/dev/ara-scaffold/runs/full26-rerun/events.jsonl`. There are **18 unique MODEL responses**, of which **3 were historically accepted**.

| Outcome | Before | After |
|---|---:|---:|
| Accepted directly | 3 | 3 |
| Accepted after content-free normalization | 0 | 3 |
| Requires a new targeted correction | 9 | 11 |
| Requires native output-limit subdivision | 1 | 1 |
| Terminal under the replayed recovery allowance | 5 | 0 |
| Total | 18 | 18 |

Thus acceptance without a new provider response rises from **3/18 to 6/18**. Of the 15 historically rejected responses, three become acceptable after normalization, eleven still require a new correction, and one requires subdivision. None of those eleven is counted as accepted. Removing the unchanged-item rejection exposes missing inference links in that recorded patch; the semantic guard still rejects it.

Authoritative evidence: `runs/kappa-replay/baseline-final/summary.json` and `runs/kappa-replay/after-v3/summary.json`, with per-response receipts in their adjacent directories. Earlier `before` and `baseline` directories are harness-development artifacts, superseded by the deduplicated baseline.

### Per-response results

Event numbers are zero-based positions in the verified origin log. Copied ancestor events are omitted. “Correction” means a new response is required, not acceptance.

| Origin/event | Paper | Mode | Before | After | Remaining error or action |
|---|---|---|---|---|---|
| full26-extraction/14 | vonfintelgillies2007 | range | correction | normalized | optional empty disposition removed |
| full26-extraction/20 | vonfintelgillies2007 | targeted_correction | accepted | accepted | — |
| full26-extraction/26 | vonfintelgillies2007 | range | correction | correction | ValidationError at /: additionalProperties constraint failed |
| full26-rerun/46 | vonfintelgillies2007 | range | correction | correction | ValidationError at /items/0/attributed_to: minLength constraint failed |
| full26-rerun/52 | vonfintelgillies2007 | targeted_correction | terminal | correction | unresolved obligation status mismatch |
| full26-rerun/63 | eganweatherson2011 | range | correction | correction | extraction has no stated inference |
| full26-rerun/69 | eganweatherson2011 | targeted_correction | subdivision | subdivision | provider stop: max_tokens |
| full26-rerun/76 | eganweatherson2011 | range | correction | normalized | optional empty disposition removed |
| full26-rerun/82 | eganweatherson2011 | targeted_correction | accepted | accepted | — |
| full26-rerun/89 | eganweatherson2011 | range | correction | correction | extraction page outside paper |
| full26-rerun/95 | eganweatherson2011 | targeted_correction | terminal | correction | extraction page outside paper |
| full26-rerun/106 | vonfintelgillies2011 | range | correction | correction | extraction has no stated inference |
| full26-rerun/112 | vonfintelgillies2011 | targeted_correction | terminal | correction | extraction has no stated inference |
| full26-rerun/123 | wright2007 | range | accepted | accepted | — |
| full26-rerun/137 | schaffer2011 | range | correction | normalized | optional empty disposition removed |
| full26-rerun/143 | schaffer2011 | targeted_correction | terminal | correction | extraction coverage incomplete |
| full26-rerun/150 | schaffer2011 | range | correction | correction | unresolved obligation status mismatch |
| full26-rerun/156 | schaffer2011 | targeted_correction | terminal | correction | ValidationError at /empty_reason: type constraint failed |

## Probe selection and cap

Among the 21 not-yet-attempted papers, sort by physical page count then ID. Select positions 1 and 2, central neighbors 10 and 11 (both 44 pages), and the two explicitly requested stress sources. Selection and original source hashes are preserved in `runs/kappa-control/probe-selection.json`. A private manifest preserves the exact original records in the table’s execution order.

| Paper | Selection | Physical pages | Probe outcome | Corrections used | New accounted USD |
|---|---|---:|---|---:|---:|
| rothschild2012 | shortest | 13 | failed before provider response | 0 | 0.886705 unknown reservation |
| knobeyalcin2014 | second shortest | 21 | not attempted | 0 | 0 |
| macfarlane2011 | central neighbor | 44 | not attempted | 0 | 0 |
| veltman1996 | central neighbor | 44 | not attempted | 0 | 0 |
| kolodnymacfarlane2010 | specified partial source | 31 | not attempted | 0 | 0 |
| moss2015 | specified multi-range source | 81 | not attempted | 0 | 0 |

USD7.055050 of historical campaign charges was imported exactly once through both prior run directories. The brief does not explicitly distinguish incremental from campaign spend. An optional clarification was requested, but execution uses the conservative authorized intersection: **USD12 total campaign cap**, leaving **USD4.944950 for new calls**. No increased cap is inferred from silence. Native offline preflight verified the complete ancestry, exactly USD7.055050 imported once, no live provider construction and zero generation calls. The native paid probe ran from the committed, clean worktree and exited 2 after 17.550 seconds. Its stop was caused by unknown provider accounting, not exhaustion of the USD12 cap. The probe used the native `ara extract --profile extraction-full` lifecycle and wrote to `runs/kappa-probe`. The startup estimate was USD6.785070 for these six sources, excluding recovery, and flagged that the batch exceeded the USD4.944950 remaining under the selected campaign cap. This is an estimate, not a completed-corpus price; the observed stop was the provider/accounting failure before that cap was exhausted.

## Provider rejection, accounting, and offline follow-up

The first new `call_start` ended with `BadRequestError`, no `response_received` and no raw provider response. The runtime logged an incomplete MODEL receipt and retained the full USD0.886705 admission reservation. The detailed provider error body and request ID were not retained, so the precise service-side rejection reason cannot be proven from this run.

| Accounting quantity | USD |
|---|---:|
| Inherited measured/accounted charges | 7.055050 |
| New measured charges available in receipts | 0.000000 |
| New reservation held for unknown actual usage | 0.886705 |
| Campaign accounted total | 7.941755 |

Zero new measured charges means **no actual-usage receipt was received**, not that the request was free. There are no unrecorded outstanding dispatches: the attempted call has a terminal unknown-usage receipt. All 180 probe-log events and their anchor were verified. No completed paper, literature bundle, or pilot artifact was published. In the final DONE line, `probe_usd=0.886705` denotes accounted exposure, entirely unknown reservation; it is not a billing reconciliation.

Offline investigation reproduced an SDK schema-conversion failure on the new constraint-only envelope branches. The provider documentation requires closed objects, and the SDK requires typed/composite branches. The follow-up expands each alternative into a complete typed, closed object while retaining common root constraints, types the version field, and uses an explicit nullable union. A regression also checks that the empty alternative cannot accept null array items. Admission now counts the expanded extraction wire schema, rather than hiding its larger envelope behind the shorter local constraints. The observed SDK incompatibility is consistent with the live failure; the missing provider error body prevents an exact causal verdict.

The corrected schema passes offline SDK transformation and placeholder acceptance tests. **No live request has exercised this follow-up.** An executed offline native CLI resume included both ancestors and the failed probe. With sockets blocked, it refused with `prior provider spend is unknown; start a reconciled new run`, exit 2, and zero new dispatches. Every call-start and MODEL receipt matched the copied original probe history exactly. The native `Budget` constructor refuses prior receipts marked `reservation_unknown_actual`; the retained reservation was not deleted, relabelled, or bypassed. Further paid probing requires reconciliation of this receipt before a new native run. Raising the cap alone does not remove that blocker.

Reference consulted offline after the failure: https://platform.claude.com/docs/en/build-with-claude/structured-outputs (saved under `runs/kappa-control/structured-outputs-docs.*`). No extra model call was used for diagnosis.

## Verification

**Before the probe at `c6f9e05`:** full `uv run pytest -q` passed with 486 passed and 2 opt-in paid tests skipped (488 collected), followed sequentially by `uv run python tests/integration/negative_controls.py`: all 192/192 mutations failed as intended and passed after restoration. Both command exits were 0. Evidence is archived in `runs/kappa-control/*preprobe*`.

The response-boundary extraction first preserved 48 existing tests. New/updated behavior tests first failed (10 failed, 12 passed), then passed. Broader testing caught feedback-format changes leaking into other model stages; the change was narrowed to extraction. Two control maintenance issues were fixed rather than bypassed: the new schema made the old missing-disposition mutation redundant, so its test now uses a whitespace-only reason; an extracted function changed the indentation of another mutation anchor. The complete runner passed after both updates.

**Post-probe follow-up:** the SDK schema test and expanded-wire counting test each failed before their fixes. The SDK/acceptance set then passed 70 tests with one opt-in paid test skipped; the final targeted acceptance/planning/provider set passed 48 with one skipped. **Final full pytest on the corrected code passed: 488 passed, 2 skipped (490 collected), 252.76 seconds.** **The complete 194/194 control runner then passed (every mutation red=1, restored=0), exit 0, in 587.59 seconds.** A green final result will not be presented as a successful live probe.


## Evidence and handoff

All paths below are relative to `/home/dev/ara-work/kappa`; real data remains gitignored.

- `runs/kappa-control/verification.json`, `pytest-final.txt`, `negative-controls-final.txt`, and `runs/delta-controls/results.json`: final 488/490 pytest result (two opt-in paid skips) and 194/194 control results. The `*preprobe*` files preserve the separate checks that preceded the paid attempt.
- `runs/kappa-replay/baseline-final/summary.json` and `runs/kappa-replay/after-v3/summary.json`: deduplicated per-response baseline and final replay, with adjacent offline receipts.
- `runs/kappa-control/probe-command.json`, `probe-config.yaml`, `probe-manifest.yaml`, `probe-selection.json`, and `source-pin-check.json`: exact native invocation, selected unchanged source records, budget configuration and six original PDF hashes.
- `runs/kappa-probe/events.jsonl`, `events.anchor`, and `export/methodology.md`; `runs/kappa-control/probe-summary.json`, `probe-status.json`, and `probe-console.txt`: authoritative failed-probe execution, accounting and timing.
- `runs/kappa-control/preflight.json` and `unknown-resume.json`, plus their logs: offline ancestry/counting preflight and executed refusal to resume unknown spend without another dispatch.
- `runs/kappa-control/sdk-schema-red.txt`, `sdk-schema-green.txt`, `wire-counter-red.txt`, and `wire-final-targeted.txt`: red-before-fix and restored targeted evidence for the post-probe correction.

The non-author review should assess the final code at the delivery revision while treating the live acceptance criterion as **unmet**. Next unresolved step: obtain/reconcile the failed request’s usage evidence through an auditable path, review the wire correction, then decide on a native live follow-up with all prior charges retained. The final code has no live service acceptance receipt.

## Remaining gaps and finding placement

Non-author review follows local delivery. Replay demonstrates response acceptance, not faithful extraction of entire papers. Partial source diagnostics and original PDF/font limitations remain visible. **The paid success criterion of at least 5/6 accepted was not met: 0/6.** Neither the specified partial source nor the 81-page multi-range source received a live request. The final wire fix remains unexercised by the service, and unknown-usage accounting blocks another native paid run.

| Finding | Placement |
|---|---|
| F1: Contract/recovery changes retain semantic guards and inventory | Behavior and preservation |
| F2: Replay acceptance improves only to 6/18; eleven responses still need a model correction | Offline replay |
| F3: Unchanged-item rejection previously masked missing inference links | Offline replay |
| F4: Replay does not prove whole-paper completion or fidelity | Offline replay; Remaining gaps and finding placement |
| F5: Acceptance v3 invalidates prior graph reuse while retaining charges | Behavior and preservation |
| F6: Probe selection includes partial and multi-range sources | Probe selection and cap |
| F7: Prior spend, conservative cap interpretation, and startup estimate exceeding remaining headroom | Probe selection and cap |
| F8: Broader verification caught feedback effects and stale mutation targets; none was bypassed | Verification |
| F9: Probe rejected before a response; five sources unattempted and reservation remains unknown | Provider rejection, accounting, and offline follow-up; Probe selection and cap |
| F10: Expanded wire is counted and passes SDK checks but has no live proof; native resume refusal is executed | Provider rejection, accounting, and offline follow-up; Remaining gaps and finding placement |

10 findings, 10 placed

DONE kappa head=c07a1530cae79496811cce81f935dd15e882a468 tests=488/490 negctl=pass replay_before=3/18 replay_after=6/18 probe=0/6 probe_usd=0.886705 report=/home/dev/ara-work/reports/kappa-acceptance.md


## Round 2

**The schema gate passed, but the probe acceptance target was not met: 4/6 accepted, below the required 5/6.** The native probe measured USD11.456405 of new usage-priced cost. The partial-source paper ended with provider `stop_reason: refusal`; the 81-page source was refused at budget admission before any generation request. No budget increase, accounting reset, or further paid probe occurred.

Final local revision: `f6c89063bb3d7af25570ad9ec47c3187e3a6fa9d` on `fix/extraction-acceptance`. Two round-two commits: `7597b6b` (native reconciliation, diagnostics, preflight) and `f6c8906` (service-compatible standalone envelopes). Nothing was pushed.

### Round 2 implementation

`extract` and `schema-preflight` now expose `--unknown-usage-policy count-at-reservation`. The default still refuses unknown accounting. Explicit reconciliation appends a marker containing the original receipt hashes and upper-bound total; original receipts retain their timestamps, charges, and `reservation_unknown_actual` status. An interrupted dispatch without a receipt still refuses continuation. Native pinned, transitive imports deduplicate ancestry before charging it.

Provider error receipts allowlist sanitized HTTP status, error type, message, and request ID. Exception/request objects and body echoes are not serialized into those diagnostics. This also covers native CLI token-counter API errors. The first live gate demonstrated the diagnostic path against an actual HTTP 400.

Initial extraction wire alternatives now stand alone. The empty branch uses an explicit null inventory; the native boundary logs the content-free conversion to an empty list and preserves the raw response. Local schema, attribution, citation, inference, immutable-evidence, inventory, and obligation checks remain enforced. Reusable acceptance identity is `rich-paper-acceptance-v4`; graph format remains v2.

### Round 2 schema gate

The native command `ara schema-preflight` uses the extraction stage's model and endpoint, a placeholder-only prompt, one output token, native reservations and receipts, and no cache reuse or cache population. It enumerates five distinct projected grammars: initial extraction; correction of an empty candidate; correction of a nonempty candidate; reconciliation without obligations; reconciliation with obligations. Reconciliation corrections share those latter wires. Every applicable complete grammar includes the three kind families, so the service compiles all alternatives. This proves live grammar acceptance, not valid complete generated graphs or paper quality.

Attempt 1 at `7597b6b` failed on its first schema:

- HTTP 400, `invalid_request_error`.
- Message: `output_config.format.schema: For 'anyOf', 'additionalProperties, properties, required, type' is not supported`.
- Request ID: `req_011CgGFCB35vXJ1CPSNm3EmR`.
- Unknown usage reservation: **USD0.011205**, preserved and imported into attempt 2.

The correction removed intersecting sibling object constraints and used the explicit null empty inventory. Offline SDK transformation alone had not detected the service restriction. After offline regressions, full pytest, and the complete control runner passed, attempt 2 at the final revision passed **5/5 schemas**. Across both attempts there were **6 generation requests**, **USD0.045940 measured usage-priced cost**, and **USD0.011205 unknown usage, counted at reservation**: **USD0.057145 aggregate accounted**, below the USD1 gate cap. No outstanding gate calls remain.

Evidence: `runs/kappa-round2-gate/`, `runs/kappa-round2-gate2/`, and `runs/kappa-round2-control/gate{,2}-{status,summary}.json`. The second gate imports the first receipt chain; its historical 400 is not a rejection of the corrected schema.

### Round 2 probe outcomes and recovery

The exact original six-paper manifest and order were retained. All six native intake hashes match the original inventory, checked in `source-pins-round2.json`. The native `ara extract --profile extraction-full` run used Opus 5 with fallbacks disabled and preserved the normal lifecycle. It ran from the clean final commit, exited 2 after **3181.690 seconds**, and produced **23 generation receipts**, all with measured usage, and **10 targeted corrections**. No new probe usage is unknown.

| Paper | Pages | Final outcome | Accepted items | Calls | Targeted corrections | New measured USD |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| rothschild2012 | 13 | accepted | 71 | 1 | 0 | 0.467270 |
| knobeyalcin2014 | 21 | accepted | 58 | 2 | 1 | 0.590040 |
| macfarlane2011 | 44 | accepted | 169 | 6 | 3 | 3.322955 |
| veltman1996 | 44 | accepted | 267 | 10 | 5 | 5.202470 |
| kolodnymacfarlane2010 | 31 | refusal | 0 | 4 | 1 | 1.873670 |
| moss2015 | 81 | budget-blocked before dispatch | 0 | 0 | 0 | 0.000000 |

The four accepted papers contain **565 accepted evidence items** in native merged-graph receipts. Accepted responses from the fifth paper are not counted as an accepted paper. Failed candidates are not promoted into the accepted inventory.

Recovery was useful but expensive. The second paper's missing stated inference was corrected. The third required an initial obligation-status correction and two reconciliation inventory corrections. The fourth required coverage/obligation and qualification-kind corrections, hit `max_tokens` during correction, then completed through native range subdivision and reconciliation. The fifth corrected an item source-ID mismatch but failed during later reconciliation. Correction counts are totals per paper; the configured limit remains two corrections per response.

The fifth paper, the specified partial-source case, retained its eight affected-page diagnostics (all 31 pages readable). Its last response reported `stop_reason: refusal`, with 57,496 input tokens and 28,304 output tokens, including 9,862 thinking tokens. The text ended in repetitive punctuation; no specific policy explanation or underlying cause is established. The native stop-reason guard rejected it before parsing. Raw evidence is retained under the ignored run directory; no claim is made that this partial-source case succeeded.

### Round 2 accounting and budget stop

The round-two brief explicitly authorized **USD12 new probe spend**. Native offline preflight blocked network access and verified **USD7.998900 inherited exactly once**, including all old runs, the round-one failed probe, and both gate attempts. The effective campaign and extraction caps were therefore **USD19.998900**.

| Quantity | USD |
| --- | ---: |
| Pre-round-two inherited accounted cost | 7.941755 |
| Both schema-gate attempts, accounted | 0.057145 |
| Inherited total at probe start | 7.998900 |
| New probe measured usage-priced cost | 11.456405 |
| Campaign accounted total | 19.455305 |
| Campaign measured usage-priced total | 18.557395 |
| Preserved campaign unknown reservations | 0.897910 |
| Remaining probe allowance | 0.543595 |
| Sixth paper's first required reservation | 0.906080 |

The sixth paper entered native intake but had **zero generation calls**: its USD0.906080 reservation exceeded the remaining USD0.543595. The runtime recorded a budget failure and stopped the batch; this is not a model acceptance failure on that paper. No complete `literature.extracted.txt` corpus artifact was published. The four accepted graphs, failed outcomes, raw responses, partial state, and methodology remain available in the run receipts/export. Do not treat the run as a completed six-paper corpus.

The USD0.897910 unknown total is the old USD0.886705 reservation plus the first gate's USD0.011205 reservation. These are **unknown usage, counted at reservation**, labelled upper bounds, never measured usage. Methodology correctly remains incomplete for actual historical spend. Measured costs are calculated from usage at configured rates, not a provider invoice. Combined new round-two accounting, gate plus probe, is USD11.513550; no cap was raised.

### Round 2 verification and evidence

At the final source revision, sequentially before the successful paid gate and probe:

- `uv run pytest -q`: **495 passed, 2 skipped / 497 collected**, 253.69 seconds of pytest execution.
- `uv run python tests/integration/negative_controls.py`: **200/200** mutations red, all restored green; 624.03 seconds for the runner. Controls cover reservation continuation and full charging, error receipts, schema inventory, standalone envelopes, and null normalization, alongside the existing semantic guards.
- Targeted envelope/context/preflight regressions: **37 passed**. Relevant wire/normalization tests were observed failing before the correction.
- Earlier verification exposed two mutation anchors affected by refactoring; these were restored before the complete green run. A pre-existing test that assumed root object properties was updated to check every standalone alternative. Earlier transcripts remain separate from final results.
- Final probe integrity: **450 hash-chain records**, matching anchor, verified transitive pinned imports, **zero outstanding dispatches**, and all six source pins matched. Native preflight independently confirmed the exact inherited total with zero generation calls and blocked networking.

Primary receipts are under `/home/dev/ara-work/kappa/runs/kappa-round2-control/`: `verification.json`, `pytest-final.txt`, `negative-controls-final.txt`, `negative-control-results.json`, `gate2-summary.json`, `preflight.json`, `probe-command.json`, `probe-status.json`, `probe-summary.json`, `final-integrity.json`, and `source-pins-round2.json`. The run itself is `runs/kappa-round2-probe/`; methodology is in its `export/`. Exact commands and effective configs are retained in those ignored artifacts. Earlier replay evidence remains the round-one replay; it was not rerun or presented as new round-two evidence.

### Round 2 delivery limits and finding placement

The requested accounting, diagnostics, and repeatable native schema gate are implemented and locally committed. The grammar gate passed. **The paid acceptance threshold failed**, the partial-source case remains unsuccessful, and the 81-page source received no generation request. Recovery still consumes substantial tokens and money; this run does not establish full-corpus reliability or an economical six-paper completion. No semantic guard was relaxed to improve the count. Further paid work is outside the remaining usable reservation budget for this profile and was not attempted.

The worktree is clean at `f6c89063bb3d7af25570ad9ec47c3187e3a6fa9d`. `/home/dev/ara-scaffold` remains clean at `be7468df12d4c0422d54f8ccd881d653cd92bdd4`. No push or delegation occurred. The brief's separate non-author review remains to be performed.

| Finding that changes the reader's action | Deliverable section |
| --- | --- |
| Explicit conservative continuation works; historical usage is still unknown | Round 2 implementation; Round 2 accounting and budget stop |
| SDK transformation missed a live service restriction; standalone alternatives fixed it | Round 2 schema gate |
| Null inventory normalization is content-free, logged, and changes acceptance identity | Round 2 implementation |
| Five live grammars passed within the aggregate gate cap; this is not extraction-quality proof | Round 2 schema gate |
| Acceptance threshold failed at 4/6 | Round 2 probe outcomes and recovery; Round 2 delivery limits and finding placement |
| Ten corrections and subdivision recovered papers but consumed substantial budget | Round 2 probe outcomes and recovery |
| Partial-source paper failed on a provider-reported refusal; cause not established | Round 2 probe outcomes and recovery |
| Sixth source had zero generation calls; budget stop prevented corpus publication | Round 2 accounting and budget stop |
| Full tests/controls passed with two skips; receipts and source pins verified | Round 2 verification and evidence |
| No full-corpus verdict, no push, and separate non-author review still pending | Round 2 delivery limits and finding placement |

10 findings, 10 placed

DONE kappa round2 head=f6c89063bb3d7af25570ad9ec47c3187e3a6fa9d tests=495/497 negctl=pass schema_gate=pass gate_usd=0.057145 probe=4/6 probe_usd=11.456405 report=/home/dev/ara-work/reports/kappa-acceptance.md


## Round 3

Local revision `0eb85924afeb01aac44e5bc0ca5f2714c6a99823` on `fix/extraction-acceptance`, based on round-two
`f6c89063bb3d7af25570ad9ec47c3187e3a6fa9d`. **F1 and F2 are fixed.** F3 is deferred
under the brief's approximately two-hour clause, with the guarantee narrowed
below and in `DECISIONS.md`. No push, delegation, live API call or new spend
occurred. The wire schemas are unchanged: `schema_gate=not-needed`.

### Round 3 F1: conservative diagnostics

Provider diagnostics no longer depend on substring scrubbing or knowledge of the
prompt. Arbitrary free-form messages, including dotted-path, partial and escaped
request echoes, produce `Provider diagnostic suppressed.` This applies at the
model-call boundary and to native CLI token-counter errors before console output,
runtime-error recording or export. HTTP status must be an integer in 400–599;
error type must belong to the provider-type enumeration; request IDs must match
bounded alphanumeric `req_` syntax. Invalid metadata becomes null.

The full-string parser recognizes only the schema compiler's `anyOf` sibling
constraint diagnostic. Its variable tokens are allowlisted schema keywords and
the output sentence is reconstructed canonically. This preserves the useful
round-two compiler diagnostic without retaining arbitrary captured text. Other
compiler diagnostics are intentionally suppressed until explicitly supported.
The round-two unconditional no-echo claim based on substring scrubbing is
superseded by this narrower, tested contract.

### Round 3 F2: normalized correction candidates

Decoded rejected responses now use the same content-free normalization as initial
validation before the item-ID merge. An invalid null inventory can reach a valid
correction instead of terminating after one call. Tests cover success after one
or two corrections and refusal after initial plus two unsuccessful corrections;
an unused valid fourth response is never dispatched. Raw MODEL responses remain
unchanged, and correction-candidate normalization has its own phase/attempt/change
event. Empty, non-string and duplicate item IDs still refuse without requesting a
repair that might silently assign identities. Existing paper allowance, budget,
semantic validation and accepted-evidence immutability tests remain in force.

### Round 3 F3: precise guarantee and deferred work

The guarantee is **item-inventory preservation across corrections and
accepted-obligation accounting**. It does not preserve rejected candidates' gap
declarations and does not prove semantic fidelity. A correction may replace
coverage metadata and `new_gaps`, allowing a rejected gap to disappear without an
explicit evidence-backed disposition. Lambda's placeholder reproduction establishes
this limitation; it does not establish an omission in any accepted real graph.

A complete fix needs stable gap identities before acceptance, explicit resolution
and dismissal evidence rules, integration with subdivision and failed ranges,
changed prompts/schemas, acceptance-identity/reuse reassessment and controls.
I estimate that exceeds this round's approximately two-hour scope. The brief
explicitly permits documenting this limit and leaving behavior unchanged; that
option was taken. Simply unioning descriptions would not support evidence-backed
dismissal of false discoveries.

### Round 3 verification, schema identity and delivery

- Regression proof before implementation: **16 failed, 25 passed**, exposing
  request-echo/metadata failures and premature null-candidate termination.
- Final targeted diagnostic/acceptance suite: **41 passed**. CLI coverage uses the
  native `AnthropicProvider.estimate` token counter with an offline failing SDK
  client and checks console, log and export files for the adversarial fragment.
- `uv run pytest -q`: **515 passed, 2 skipped / 517 collected**; verification wrapper
  elapsed 305.57 seconds. The two opt-in paid tests stayed skipped.
- Only after pytest finished, `uv run python tests/integration/negative_controls.py`:
  **209/209** mutations exited 1, all restored tests exited 0; wrapper elapsed
  729.68 seconds. Nine new controls cover suppression,
  status/type/request-ID validation, recognized compiler messages, keyword and
  full-sentence parsing, native CLI errors, and rejected-candidate normalization.
- Offline comparison against the round-two source evaluated **nine response-shaping
  variants / five distinct wire schemas**, all identical. Prompts, schema files,
  configuration and extraction acceptance identity source are unchanged. No live
  schema preflight was needed or performed.

Acceptance remains `rich-paper-acceptance-v4`: diagnostics do not change graph
acceptance, and the recovery fix applies the existing v4 normalization consistently
without changing the accepted graph rules. Lambda independently verified four v4
successes as reusable: `rothschild2012`, `knobeyalcin2014`, `macfarlane2011`, and
`veltman1996` (565 items total). Their acceptance-identity inputs remain unchanged;
this round did not rerun paid extraction or claim a new semantic quality review.

Receipts: `/home/dev/ara-work/kappa/runs/kappa-round3-control/`, including
`targeted-red.txt`, `targeted-green.txt`, `offline-check.json`, `verification.json`,
`pytest-final.txt`, `negative-controls-final.txt`, and `negative-control-results.json`.
Per-control mutant/restored transcripts are under `runs/delta-controls/`.
The final checkout is clean at the revision above. `/home/dev/ara-scaffold` remains
clean at `be7468df12d4c0422d54f8ccd881d653cd92bdd4`. This is local implementation and
verification; the caller owns any subsequent independent review and publication.

### Round 3 F4–F6: full-run limits and budget requirements

- **F4:** The paid probe still completed **4/6**, below the required **5/6**. The
  partial-source case ended in provider `refusal`; its underlying cause remains
  unestablished. The 81-page source had zero generation calls because the first
  reservation exceeded the remaining budget. Neither stress case has a successful
  extraction established by this probe, and no completed corpus artifact exists.
  The green offline checks do not turn this into a successful paid acceptance run.
- **F5:** A future full run must budget a **new `wright2007` extraction**. Do not
  relabel its older graph to v4. Reuse the four compatible v4 successes only with
  their matching effective model/profile and intact origin receipts.
- **F6:** Campaign accounted total remains **USD19.455305**, consisting of
  **USD18.557395** measured usage-priced cost and **USD0.897910** unknown reservations.
  This round adds **USD0**. Future continuation must preserve/import history and
  use explicit `--unknown-usage-policy count-at-reservation`; unknown receipts stay
  upper bounds, not measured billing, and methodology stays incomplete for actual
  historical usage. Unreceipted dispatches still refuse. No allowance was reset.

### Round 3 finding placement

| Finding that changes the reader's action | Deliverable section |
| --- | --- |
| F1 fixed: conservative diagnostic contract; unknown compiler messages suppressed | Round 3 F1; Round 3 verification |
| F2 fixed: normalized null-candidate recovery remains bounded and logged | Round 3 F2; Round 3 verification |
| F3 deferred: rejected gaps can disappear; structure is not semantic fidelity | Round 3 F3 |
| F4 remains: paid threshold 4/6 failed; stress cases and corpus completion unproven | Round 3 F4–F6 |
| F5: budget a new wright2007; retain exact v4 acceptance identity for reuse | Round 3 F4–F6; Round 3 verification |
| F6: keep unknown reservations charged and labelled; interrupted dispatch still refuses | Round 3 F4–F6 |

6 findings, 6 placed

DONE kappa round3 head=0eb85924afeb01aac44e5bc0ca5f2714c6a99823 tests=515/517 negctl=pass fixed=F1,F2 schema_gate=not-needed
