# Zeta overnight full pass — part 7 stopped during token counting

**The native resume exited 2 before any paid dispatch, with HTTP 400 `invalid_request_error` during its initial plan recount. New part 7 spend is USD0.000000.** It did not reach `construction_resumed`, window 18, or any restored-batch event. The earlier seven accepted batches and **140 provisional commitments remain intact**, but there is still no final ledger, merge, freeze, targets, search, route or `awaiting_selection` state. No route was selected.

**Xi is not merged into local or fetched remote `main`; both remain `e5e40cb99a5e827be8c054feb171d400346a700e`.** Per the part 7 brief, the new final report was not generated with the old renderer. `/home/dev/ara-scaffold/runs/overnight-report-final/` and `/home/dev/ara-work/reports/overnight/final/` are absent. The existing `/home/dev/ara-work/reports/overnight/report.html` is the preserved **part 6** report and excludes the five new resume events. The DONE line points to that last generated report, not a newly generated part 7 report. This written handoff and the part 7 controls contain the current result.

Cumulative accounted totals are unchanged: **Zeta overnight USD70.402330**, **whole-night Mu + Zeta USD81.751115**, **overall campaign USD133.630090**. Three earlier unknown reservations totalling USD1.844820 remain unknown; no new reservation was added. The corpus is unchanged: **26 nonempty graphs, 5,659 items, 363 quarantined, 5,296 eligible, 57 open gaps, zero exclusions**. Nineteen graphs are natively `extracted`, seven `partial`; counts do not prove semantic completeness.

## Part 7 execution and exact stop

Executed from clean `main` at `e5e40cb99a5e827be8c054feb171d400346a700e`:

```sh
uv run ara resume-construction --run-dir /home/dev/ara-scaffold/runs/overnight6-pilot --unknown-usage-policy count-at-reservation
```

The CLI used the stored configuration, literature, topic and explicitly empty audience under its exclusive resume lock. Credentials were supplied only through the launch environment. No configuration, source, prompt, extraction artifact or cap was changed; no worker was spawned and no commit or push occurred.

Exactly five events were appended:

| UTC on 2026-10-23 | Event | Result |
|---|---|---|
| 09:04:32.116354 | `unknown_usage_reconciled` | Existing three reservations, USD1.844820, retained under count-at-reservation |
| 09:04:41.010250 | HUMAN `resume-construction` | Authorized native command |
| 09:05:05.747382 | `provider_error` | HTTP 400, `invalid_request_error`, request `req_011CgJuF9SbuoBv9JiiSAnyo` |
| 09:05:08.962052 | `runtime_error` | Native sanitized provider diagnostic propagated as RuntimeError |
| 09:05:21.716310 | `command_timing` | 69.119521711 seconds machine elapsed |

The diagnostic message is **“Provider diagnostic suppressed.”** It does not identify the underlying complaint. This is a token-counter failure before the first successful `context_plan` receipt: no `call_start`, response, MODEL receipt, `construction_resumed` or restored-batch event was added. Source inspection places the first provider count at `count_request('build_t_batch', inputs)` in construction partition planning; the native error receipt itself does not record request kind, prompt, size or count. That source-path inference is not a measured token-count receipt. No malformed-request, prompt-size, service-capacity or credential diagnosis is claimed.

The new window-refusal policy handles receipted generation failures at reservation. This failure occurred earlier, during provider counting, so no charge/reservation existed to turn into an accounted window skip. The native operational exception propagated and the command exited 2. It is not logged as an overload/capacity error; the brief requires other stops to be recorded, so no retry or provider probe followed.

## Preservation and scope of resume proof

Before execution, copied the original log, anchor and root artifacts to `runs/overnight7-control/part6-snapshot/`, with a SHA-256 manifest. After the failed resume:

- The original **279,466,310-byte / 5,190-row** log is an exact byte prefix of the current log, SHA-256 `c44b443a82130252cebc15dcb2ac34058f9c3c6c2a1180dd53f1fa5780fad3b3`, matching Phi's reviewed source.
- All **18 original plan and batch artifacts** are byte-identical to the snapshot.
- The native event chain, anchor and available transitive extraction origins verify with zero gaps.
- All **seven accepted batches / 140 provisional commitments** are preserved, with zero new accepted batches, generation dispatches or MODEL receipts.
- Native accounted cost is unchanged at **USD130.112615**. No unclassified receipt, unresolved dispatch or unfinalized measured response exists.

Phi's reviewed offline replay restored the 17 completed windows, skipped terminal window 17, and reached window 18 with the same plan ID and zero generation or added cost. Its 24.1-minute startup is an observed offline timing, not a guarantee that live startup will reach restoration. This live attempt stopped after 69.12 seconds at the first counter request. **The offline restoration proof remains valid as offline evidence; this attempt does not establish live restoration or downstream success.**

Sigma round 4 reports 669 passed / 2 skipped and 300 mutation/restoration controls. Phi independently reviewed Sigma `e5e40cb` with Xi `3350ef1`, merged them in scratch at `c5d04ee`, and reports **672 passed, 2 skipped of 674**, then **305 mutations failed their targeted tests and 305 restorations passed**. Phi's verdict is merge for both, zero blocking. Those tests/replay are the reviewers' executed offline evidence, not checks rerun by this operational pass. The opt-in live checks remained skipped.

Sigma's offline reconstruction of the earlier window 17 request found no demonstrated malformed or oversized application request. A mock SDK stream reproduced `APIStatusError(status_code=200)`, consistent with an opaque streamed provider rejection and explaining the earlier null HTTP status. The original suppressed complaint remains unrecoverable. That finding does not diagnose this new, explicitly HTTP 400 counter failure.

## Part 7 budget handling

Resume reads the stored native cap **USD245.395145** and has **no CLI cap override**. At launch, native accounted cost was USD130.112615, leaving **USD115.282530**. No cap increase was needed to allow the brief's USD115, and no stored receipt/configuration was edited.

The new allowance is slightly stricter than that remaining native capacity. External process supervision was prepared to stop conservatively at USD99 finalized new spend, retaining USD16 for an in-flight request; the largest configured request reservation is at most USD15.33 under the initial 200,000-token context, five web uses, 64,000 output tokens per iteration and stored prices. This is a process-stop buffer, not a native budget override. **The guard never triggered:** there were no new paid calls or charges.

| Scope | Accounted USD |
|---|---:|
| Part 7 measured | 0.000000 |
| Part 7 new unknown reservation | 0.000000 |
| Zeta cumulative overnight | 70.402330 |
| Whole-night Mu + Zeta | 81.751115 |
| Native current-run ledger, including inherited history | 130.112615 |
| Separate earlier pilot offset | 3.517475 |
| Overall campaign measured | 131.785270 |
| Overall campaign unknown reservations | 1.844820 |
| Overall campaign accounted | 133.630090 |

The whole-night maximum with all USD115 would have been USD196.751115, below USD200. All USD115 remains unused. The native 30-million-token cap and 233/48,000 construction settings remain unchanged. Cumulative overall accounting still has 316 measured and 3 unknown MODEL receipts; no prior accepted call was repaid. The DONE line's `new_usd` remains Zeta's cumulative overnight accounted total, not this zero-spend attempt.

## Xi integration and report status

After the pilot exited, fetched `origin` and checked both local and remote main. Both point to Sigma `e5e40cb`; Xi's readable-report work has not been integrated there. No feature-branch merge, conflict resolution or source change was performed. The brief explicitly says to report non-integration if Xi is not merged, so no old-renderer report was generated and no nonexistent final-report link is claimed.

Phi's independent audit of Xi's existing real output found a 2,453,319-byte HTML overview, 7,994 files / 1,052,011,317 bytes, full event/occurrence/artifact retention, valid links, and desktop/mobile Chromium rendering. That is reviewed output from another directory and revision, not a newly generated deliverable from this run. Xi requires the whole sibling-file directory to accompany the HTML. Those review results do not prove a current final report or real completed search-tree rendering; neither exists from this pilot.

The preserved part 6 report has 57 files / 9,107,028,227 bytes with all copied hashes verified, including 12 historical core backups through `report-part5.*`. Its 3.70 GB HTML crashed Chromium twice; only complete-file static anchors and an exact search-section excerpt were verified. That limitation remains attached to the old report. The requested new `overnight/final/` directory remains absent.

Current controls: `/home/dev/ara-scaffold/runs/overnight7-control/`, including `resume-command.json`, `admission-check.json`, snapshot/manifest, resume console/status/exit code, `resume-verification.json`, `xi-integration-check.json`, `final-verification.json` and work notes. The prior written handoff is preserved as `zeta-full26-part6.md`. The original part 6 controls and native report remain intact. No paid process is active.

## Carried-forward extraction and part 6 evidence

The sections below preserve the unchanged corpus and completed part 6 evidence. Their execution, cost, source revision, copy and browser claims refer to **part 6**, not a new part 7 report. Current part 7 status is stated above. In particular, the native report described below does not include the five new resume events.

### Extraction inventory

All 26 supplied PDFs have native nonempty graphs: 19 extracted and 7 partial. The exclusion roster is empty. Counts do not establish semantic completeness.

| Paper ID | Status | Items | Quarantined | Eligible | Open gaps |
|---|---|---:|---:|---:|---:|
| vonfintelgillies2007 | extracted | 136 | 27 | 109 | 6 |
| eganweatherson2011 | extracted | 125 | 10 | 115 | 0 |
| vonfintelgillies2011 | extracted | 147 | 13 | 134 | 4 |
| wright2007 | extracted | 105 | 17 | 88 | 0 |
| schaffer2011 | partial | 194 | 21 | 173 | 5 |
| braun2012 | partial | 119 | 38 | 81 | 6 |
| eganhawthorneweatherson2005 | extracted | 213 | 14 | 199 | 0 |
| egan2007 | extracted | 158 | 12 | 146 | 2 |
| macfarlane2011 | extracted | 169 | 17 | 152 | 0 |
| yalcin2007 | partial | 210 | 10 | 200 | 2 |
| yalcin2011 | extracted | 87 | 24 | 63 | 3 |
| rothschild2012 | extracted | 71 | 1 | 70 | 0 |
| moss2015 | extracted | 241 | 13 | 228 | 9 |
| hawkesteinertthrelkeld2021 | extracted | 227 | 5 | 222 | 0 |
| veltman1996 | extracted | 267 | 31 | 236 | 0 |
| gsv1996 | extracted | 259 | 11 | 248 | 1 |
| willer2013 | extracted | 169 | 1 | 168 | 0 |
| ninan2018 | partial | 180 | 15 | 165 | 2 |
| beddorgoldstein2021 | extracted | 123 | 16 | 107 | 0 |
| hollidaymandelkern2024 | extracted | 382 | 7 | 375 | 5 |
| kolodnymacfarlane2010 | partial | 84 | 13 | 71 | 1 |
| knobeyalcin2014 | extracted | 58 | 1 | 57 | 0 |
| klinedinstrothschild2012 | extracted | 198 | 2 | 196 | 0 |
| bledin2014 | extracted | 116 | 3 | 113 | 1 |
| yalcin2015 | partial | 224 | 7 | 217 | 3 |
| macfarlane2014 | partial | 1397 | 34 | 1363 | 7 |
| **Total** | **26 graphs** | **5659** | **363** | **5296** | **57** |

### Item counts by kind

Counts include quarantined items. P=premise, C=conclusion, IC=intermediate conclusion, I=inference, RV=reported view, AV=attacked view, D=distinction, Q=qualification.

| Paper ID | P | C | IC | I | RV | AV | D | Q |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| vonfintelgillies2007 | 47 | 8 | 34 | 14 | 10 | 10 | 3 | 10 |
| eganweatherson2011 | 49 | 0 | 23 | 26 | 19 | 2 | 2 | 4 |
| vonfintelgillies2011 | 53 | 3 | 29 | 30 | 7 | 10 | 1 | 14 |
| wright2007 | 38 | 2 | 21 | 21 | 12 | 2 | 1 | 8 |
| schaffer2011 | 73 | 3 | 31 | 33 | 10 | 13 | 7 | 24 |
| braun2012 | 29 | 1 | 32 | 21 | 6 | 10 | 2 | 18 |
| eganhawthorneweatherson2005 | 47 | 1 | 23 | 39 | 8 | 6 | 71 | 18 |
| egan2007 | 52 | 5 | 27 | 35 | 7 | 7 | 8 | 17 |
| macfarlane2011 | 61 | 2 | 34 | 37 | 14 | 4 | 6 | 11 |
| yalcin2007 | 49 | 2 | 37 | 38 | 8 | 4 | 3 | 69 |
| yalcin2011 | 23 | 2 | 35 | 0 | 6 | 4 | 5 | 12 |
| rothschild2012 | 28 | 2 | 10 | 13 | 6 | 6 | 0 | 6 |
| moss2015 | 86 | 4 | 56 | 54 | 15 | 4 | 3 | 19 |
| hawkesteinertthrelkeld2021 | 86 | 4 | 50 | 48 | 17 | 6 | 2 | 14 |
| veltman1996 | 99 | 12 | 57 | 66 | 5 | 4 | 6 | 18 |
| gsv1996 | 101 | 26 | 44 | 64 | 6 | 1 | 4 | 13 |
| willer2013 | 57 | 5 | 35 | 39 | 12 | 9 | 4 | 8 |
| ninan2018 | 65 | 9 | 41 | 35 | 12 | 0 | 4 | 14 |
| beddorgoldstein2021 | 49 | 5 | 40 | 9 | 8 | 6 | 0 | 6 |
| hollidaymandelkern2024 | 148 | 38 | 50 | 87 | 17 | 9 | 5 | 28 |
| kolodnymacfarlane2010 | 28 | 1 | 18 | 17 | 6 | 7 | 1 | 6 |
| knobeyalcin2014 | 15 | 4 | 6 | 12 | 7 | 3 | 3 | 8 |
| klinedinstrothschild2012 | 67 | 5 | 35 | 39 | 14 | 6 | 4 | 28 |
| bledin2014 | 42 | 7 | 16 | 23 | 9 | 6 | 5 | 8 |
| yalcin2015 | 66 | 10 | 51 | 50 | 14 | 6 | 3 | 24 |
| macfarlane2014 | 464 | 55 | 229 | 247 | 115 | 96 | 98 | 93 |

### Part 2 extraction cost, tokens, and time

Only the four remaining papers incurred new extraction charges. All 22 earlier graphs were reused. Costs include accepted and rejected responses; model seconds sum call wall times, and paper elapsed seconds include local processing. All new cache and server-tool usage is zero.

| Paper ID | New USD | Input tokens | Output tokens | Receipts | Model seconds | Paper elapsed seconds |
|---|---:|---:|---:|---:|---:|---:|
| klinedinstrothschild2012 | 4.661000 | 333720 | 119696 | 12 | 1333.4 | 1428.8 |
| bledin2014 | 2.332290 | 224633 | 48365 | 6 | 587.4 | 647.7 |
| yalcin2015 | 2.853850 | 278320 | 58490 | 6 | 649.8 | 721.8 |
| macfarlane2014 | 18.894005 | 1228606 | 510039 | 49 | 5849.8 | 6393.6 |

### Publication, retention, and prerequisite-context fix

The authoritative corpus is `/home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt`. Native extraction and publication exited 0 on clean main `9d4ec86595f7c46d5ba6d6f9747d86d50533246a`. All 26 PDFs were present. The 22 earlier graphs were reused before the four remaining papers; the book ran last. Yalcin 2015 received exactly the one newly authorized paper retry. Native bounded range refinements and targeted corrections are included in the accounting; no failed-paper retry loop was launched.

The artifact audit verified transitive native provenance, every compatible original snapshot and its item bodies/reference mapping, citations, acceptance identities, recomputed grounding, dependency quarantine, gap resolution, and agreement with native methodology. The prior Round 3 artifact still verifies. Mu's union publication resolves the earlier non-monotonic identity blocker. The additional 51 retained namespace identities preserve historical/remapped evidence; they are not 51 newly extracted claims. The earlier failed publication remains in the full report as diagnostic history. Its failure is superseded by this successful publication, not erased.

The original part 2 publication proceeded under the operator's corpus-specific Pi-B1 exception. Its final inventory used `/home/dev/ara-work/reports/pi-evidence/native_context_inventory.py` and found **741 shared items, zero prerequisite-context mismatches**. That result and artifact are unchanged. **The general Pi-B1 defect is now fixed in part 3's code**, according to Rho's independent review of `1d832b24805536b46e6974ca97842cffe0458e3a`. Rho rebuilt all six real unions in both orders and compared 2,146 original-root prerequisite closures without mismatch. This structural preservation evidence is distinct from a semantic audit. The pilot consumes the same published artifact; it does not republish or re-extract the corpus.

Evidence: `runs/overnight2-control/audit-summary.json`, `audit-console.log`, `historical-artifact-verification.json`, `final-context-check/native-context-inventory.json`, and the two adaptation-provenance JSON files. The earlier preflight established native reuse compatibility and exact equality of all 3,724 prior items while intercepting history copying; the actual extraction subsequently performed the full native import. No full-copy claim is made for that probe.

### Coverage, quarantine, and limits

The corpus retains **363 quarantined items: 312 direct and 51 dependency quarantines**. Those items remain auditable and are excluded from eligible source evidence; the audit found no eligible dependency pointing into the quarantined set. There are **57 snapshot-scoped open gaps**: 46 inherited plus 1 in Bledin, 3 in Yalcin 2015, and 7 in the book. Klinedinst–Rothschild adds none. Historical snapshot-scoped gaps can differ from the earlier diagnostic inventory's deduplicated-looking counts; the native artifact is authoritative.

Lexical grounding is not entailment, faithful attribution, completeness, or a semantic quality audit. It can exclude supported paraphrases and admit unsupported text that overlaps source vocabulary. Partial-source diagnostics, thin-range dispositions, rejected model responses, reopened gaps, and failed reconciliation remain visible in native evidence. Yalcin 2011 has no eligible inference items; its explicit unverified-inference limitation remains. PDF parsing logged missing optional fontTools support for some CFF encodings. No OCR, parser substitution, or semantic completeness review was performed.

The published union preserves **19 `thin_range` disposition records across 8 sources**. These are snapshot-retained records, some overlapping or repeated, not 19 independently missing source ranges. Other retained attempts can also record that a thin range was filled. These disclosures must not be collapsed into a completeness claim.

| Paper ID | Retained thin-range page spans |
|---|---|
| vonfintelgillies2007 | 17–24, 17–32 |
| vonfintelgillies2011 | 12–23 |
| braun2012 | 1–26, 1–13 |
| yalcin2011 | 20–28, 29–38, 20–38, 29–38 |
| moss2015 | 51–60, 41–60, 41–50, 51–60 |
| beddorgoldstein2021 | 24–35 |
| klinedinstrothschild2012 | 13–25 |
| macfarlane2014 | 160–170, 291–301, 336–346, 347–358 |

Von Fintel–Gillies 2007 retains an inference-disposition conflict: a no-explicit-structure disposition overlaps accepted paper-stated inference evidence. Beddor–Goldstein retains its failed reconciliation and thin pages 24–35; Holliday–Mandelkern retains its earlier reconciliation context refusal. Beddor–Goldstein and the book each retain a no-explicit-inferential-structure disposition whose reason is the literal placeholder marker. Those reasons do not substantiate absence of inferential structure. They are preserved limitations, not semantic proof. The final disposition inventory is `runs/overnight2-control/disposition-summary.json`.

The book retains **1,397 items, 34 quarantined, and 7 open gaps**, with native status `partial`. It reached its configured 48 continuations after 49 charged attempts, spending **USD18.894005**. The next continuation was refused before dispatch. Best-effort reconciliation was separately refused before dispatch: **701,471 input tokens + 32,000 output allowance = 733,471**, above the **200,000** context bound. Native processing retained the accepted range graph and published it. Neither receipt exhausted the dollar or campaign token budget. Per the operator's correction, these limits did not trigger SIGINT or an unauthorized retry. Reconciliation is not presented as successfully completed.

Extraction used **11,348,025 budget-accounted campaign tokens** against the unchanged 12,000,000 cap. New part 2 extraction used 2,065,279 input and 736,590 output tokens, with zero cache/server-tool usage. All **73 fresh dispatches** have finalized measured receipts, with zero pending calls, unfinalized responses, new unknown reservations, or unclassified charges. All fresh extraction receipts name Opus 5; no fallback was used. Extraction elapsed time was about 208.5 minutes, including approximately 46 minutes of ancestry import; recorded fresh model-call time totals 8,420.3 seconds.

The existing six-grammar gate was not repeated: no prompt/schema change invalidated it. Its result establishes wire compilation, not substantive source fidelity. No tracked code edits, source tests, config changes beyond the explicit part 5 configuration and cap, delegation, commit, or push were performed for this operational continuation.

#### Partial-source physical page diagnostics

These pages carry native unread/encoding diagnostics. Full reasons remain in the event report; no OCR or source repair is claimed.

| Paper ID | PDF pages | Affected physical pages |
|---|---:|---|

| schaffer2011 | 49 | 1 |

| braun2012 | 52 | 15–16, 23–24, 36 |

| yalcin2007 | 44 | 1–25, 27–40, 42–44 |

| ninan2018 | 45 | 13–14, 17–18, 24, 28, 44–45 |

| kolodnymacfarlane2010 | 31 | 1, 4–6, 8–9, 30–31 |

| yalcin2015 | 54 | 18, 46–47 |

| macfarlane2014 | 358 | 60, 165–166, 174, 177, 179, 219–220, 229, 233–234, 240, 278–279, 284 |




### Reviewed construction and corrected symbol basis

Part 6 runs clean main **1411e91c70a6537422dbfece6f6ed1301b90e748**. Sigma rounds 2/3 change construction to soft window shares and admission against recounted remaining global capacity. Upsilon's independent narrow B1 re-review says **merge, zero blocking**. Both report **646 passed, 2 skipped of 648**, followed sequentially by **293 mutations failing their targeted tests and 293 restorations passing**. The skips are opt-in live checks. Those are their executed offline checks, not tests rerun for this operational pass or proof of live semantic quality.

Round 2 allowed actual-output borrowing but still used local shares to veto closure admission. Upsilon reproduced starvation after an early accepted output crossed the planning headroom target. Round 3 removes those local admission vetoes. Model selection still receives recomputed shares as guidance. Global working and catalogue capacity, exact initial/correction/downstream request contexts, campaign accounting and spend/token caps remain hard. Window-level selection/formalization refusals are logged and skipped; rejected symbols and commitments cannot enter accepted state. Genuine global construction exhaustion omits the remaining windows and passes accepted work to the existing single freeze. An empty T and operational/campaign failures still abort.

Construction v8 preserves the deepest complete prerequisite layer that fits the recounted global and exact-request bounds. Mandatory incoming qualifications/distinctions and included inference endpoints remain. Cut-frontier text carries **`assumed_premise; support_omitted`** plus the exact omitted direct-support IDs, attributed text and citation. Original rich evidence stays immutable. Uncut/cut inventories, skipped windows and omissions remain logged. Reuse retains the earlier assumption marker even if later windows add support. These are conditional working premises; no source inference becomes an engine license. Formula fidelity, relevance and symbol alignment require semantic judgment beyond these structural checks. Formalization chunking remains deferred.

**Correction: the part 4 brief's 70–90 catalogue tokens per item rationale was wrong.** Gamma round 3c has 89 symbols for 45 commitments. Exact paired counts, differing only in catalogue, are 20,563 empty and 31,034 populated: **10,471 / 45 = 232.69**, rounded to **233**. The old 128 reservation was not a verified 1.4× margin. Historical evidence is `runs/overnight4-control/reservation-rationale-check.json`.

The literal part 3 configuration had 256 growth / 32,000 catalogue, giving 96 initial slots. Part 5's native count-only baseline verified that result with 340 chain/anchor records and zero generation. The operator explicitly authorized **233 / 48,000** to match Sigma's reviewed 144-slot plan. Part 6 retains that approved config byte for byte, including a 100,000 working budget, 200,000 model context, 30,000,000 token cap, and native USD245.395145 cap. Initial allocation is guidance, not a promise or hard upper limit on actual accepted commitments. Sigma round 2's 67,631 maximum input count is historical; round 3 changed the prompt and this pilot counts its own requests.

The audience is explicitly empty (`--audience ''`); no named position, smoke mode, fallback or route selection is authorized. The historical part 2 pilot used the literal CLI default; parts 3 onward corrected it. Source title/author metadata was already absent in the original records and was not discarded by projection.

### Live construction, cuts and window outcomes

The live plan has **48 windows, three soft slots per window and 144 initial allocated slots**, a 204-token copied-envelope estimate, a 233-token growth reservation, a 3,232-token wrapper and 20% planning headroom. Projected working/catalogue use is 66,160 / 33,552 tokens. The largest initial input is **67,688**, below 70,000; plus 64,000 reserved output and 48,000 catalogue is **179,688**, below 200,000. The fresh count is 75 tokens above part 5 and 57 above Sigma round 2; the allocation is unchanged. Plan ID: `0c05ea4383c09b28bb865ce44c3eb2dbfb8efde6b49c16888989215a1efe2581`.

All seven accepted batches log borrowing beyond their soft shares. Window 0 retains five commitments against its three-slot initial target and borrows 2,603 working / 2,070 catalogue tokens. Later accepted batches retain 17, 12, 24, 76, three and three new commitments. This executes the repaired global-admission path on real evidence; it does not validate the semantic formulas or alignment decisions.

The final structural audit verifies every accepted artifact hash, exact attributed text/citation, mandatory qualifier and endpoint context, and exact omitted-support edges. Seven provisional commitments carry seven explicit omitted-support edges. Native methodology names every one. Accepted cuts are window 5 (89 uncut to 76 retained, depth 2, three edges), window 10 (79 to three, depth 0, two edges) and window 11 (26 to three, depth 0, two edges). Window 2 reuses 11 prior commitments unchanged, adding 12 from its 23-item closure. All 32 dispatch catalogues exactly match the symbols from earlier accepted batches, including after nine rejected responses; no rejected symbol leaks forward. The accepted catalogue contains 377 symbols. All 11 reused prior commitment bodies match exactly. No rejected commitment enters accepted batch state. There is no final selected/omitted ledger or frozen-text proof because the operational stop precedes merge/freeze.

The accepted commitments span eight sources:

| Source ID | Provisional commitments |
|---|---:|
| beddorgoldstein2021 | 3 |
| bledin2014 | 7 |
| braun2012 | 26 |
| egan2007 | 22 |
| eganhawthorneweatherson2005 | 68 |
| eganweatherson2011 | 8 |
| hawkesteinertthrelkeld2021 | 1 |
| hollidaymandelkern2024 | 5 |

Window numbers below are zero-based. “Retained” includes reused items; “new accepted” counts only accepted new items. Charges include selection, formalization and corrections; the final row is an unknown reservation, not measured spend. A dash means no validated closure was produced.

| Window | Roots | Uncut | Retained | New accepted | Outcome | Accounted USD |
|---:|---:|---:|---:|---:|---|---:|
| 0 | 4 | 5 | 5 | 5 | accepted | 0.811395 |
| 1 | 3 | 17 | 17 | 17 | accepted | 1.107180 |
| 2 | 2 | 23 | 23 | 12 | accepted | 1.294420 |
| 3 | 3 | 24 | 24 | 24 | accepted | 1.070520 |
| 4 | 2 | 117 | 70 | 0 | provider stop: max_tokens | 2.443530 |
| 5 | 2 | 89 | 76 | 76 | accepted | 1.881915 |
| 6 | 10 | 31 | 13 | 0 | construction correction repeats unchanged item | 1.889650 |
| 7 | 6 | 40 | 9 | 0 | invalid encoded formula JSON | 0.966955 |
| 8 | 4 | 30 | 0 | 0 | mandatory root context cannot fit remaining capacity/request bound | 0.525300 |
| 9 | 2 | 54 | 10 | 0 | shared symbol token allowance exceeded | 1.055350 |
| 10 | 2 | 79 | 3 | 3 | accepted | 1.097095 |
| 11 | 2 | 26 | 3 | 3 | accepted | 0.902615 |
| 12 | 3 | 40 | 0 | 0 | mandatory root context cannot fit remaining capacity/request bound | 0.687030 |
| 13 | — | — | — | 0 | working T evidence inventory mismatch | 0.661410 |
| 14 | 3 | 59 | 0 | 0 | mandatory root context cannot fit remaining capacity/request bound | 0.713405 |
| 15 | 1 | 85 | 2 | 0 | shared symbol token allowance exceeded | 1.041785 |
| 16 | — | — | — | 0 | working T evidence inventory mismatch | 0.621005 |
| 17 | — | — | — | 0 | STOP: provider accounting unavailable; unknown reservation | 0.946910 |

Windows 18–47 were not reached. Window 4's formalization alone cost USD1.890890 and stopped at `max_tokens` (64,000 output tokens); native skip continued the run. Window 6 first exceeded the global catalogue allowance; its correction repeated an unchanged item and was rejected. Windows 9 and 15 also exceeded global catalogue capacity. Window 7 had invalid encoded formula JSON. Windows 8, 12 and 14 retained no mandatory bundle that fit. Windows 13 and 16 failed the root evidence-inventory check.

`construction_targeted_corrections=1` is **one correction per call type across the entire construction**, not one per window. The root-selection correction was consumed successfully on window 2; the formalization correction was consumed unsuccessfully on window 6. Later refusals were skipped without replenishing that allowance. Raw rejected responses and all their charges remain in the native receipts.

### Exact terminal boundary and restart recovery

Window 17, containing source `macfarlane2014`, dispatched `select_t_roots` at **2026-10-23 07:08:14.096283 UTC**. At **07:08:58.200426 UTC**, the provider diagnostic recorded `invalid_request_error`, HTTP status `null`, request ID `req_011CgJkLXVWBuPojPU69m6qe`. Diagnostic free text is intentionally suppressed by the native provider boundary; the underlying request complaint cannot be inferred. No measured response followed. At **07:09:04.333693 UTC**, native accounting stopped with:

`provider accounting unavailable (APIStatusError); reservation charged; actual spend unknown`

The reservation is **107,462 input + 16,384 output tokens**, USD0.946910. It remains classified unknown. The stop recorded native accounted cost **USD130.112615** and **13,997,703 tokens**, below USD245.395145 and 30,000,000. The final construction recount was **68,499 working / 47,062 catalogue tokens**, leaving **31,501 / 938**. No global-construction exhaustion event occurred. The runtime correctly aborted this operational/accounting failure instead of freezing provisional work. No service-capacity recovery was attempted because this is not logged as an overload/capacity error; the brief requires other terminal stops to be recorded and left stopped.

The assistant daemon restarted at about 05:56 UTC. The original supervisor died, but the native pilot survived as the same process and continued its in-flight call. Monitoring was attached to that existing process; there was no pilot relaunch or duplicate dispatch. Consequently the original OS exit code is unavailable and is **not claimed** as 0 or 2. Native STOP, `command_timing`, completed exports and subsequent process disappearance establish the terminal result. Logged machine elapsed time is **5,800.282240 seconds**. No paid pilot process remains active.

### Accounting and limits

Native imports and overall campaign accounting differ: the artifact imports USD110.395145; prior pilots 3–5 add USD3.517475 outside that artifact. Part 6's native cap USD245.395145 therefore permits USD135 new, corresponding to an overall campaign ceiling USD248.912620. The whole-night baseline USD62.033645 plus USD135 would be USD197.033645, below USD200. These caps and the 30-million native token cap were unchanged.

| Scope | Accounted USD |
|---|---:|
| Pre-night campaign | 51.878975 |
| Mu new overnight | 11.348785 |
| Zeta part 1 | 18.426240 |
| Zeta part 2 extraction | 28.741145 |
| Zeta part 2 pilot | 0.000000 |
| Zeta part 3 pilot | 0.535735 |
| Zeta part 4 pilot | 0.916415 |
| Zeta part 5 pilot | 2.065325 |
| Zeta part 6 measured | 18.770560 |
| Zeta part 6 unknown reservation | 0.946910 |
| **Zeta cumulative overnight** | **70.402330** |
| **Whole-night new, Mu + Zeta** | **81.751115** |
| Overall campaign measured | 131.785270 |
| Overall campaign unknown reservations | 1.844820 |
| **Overall campaign accounted** | **133.630090** |

The DONE line's `new_usd=70.402330` is **Zeta's cumulative accounted overnight spend**, including the new unknown reservation. Part 6 leaves **USD115.282530** of its new allowance unused. Three unknown reservations remain: two historical USD0.897910 plus the new USD0.946910. They are not relabelled measured usage.

Part 6 has **31 measured MODEL receipts and one unknown reservation**, from 32 dispatches, with no cache replay or fallback. The 31 measured calls total **2,218,762 input + 307,070 output tokens**, zero cache/server-tool usage, and **3,819.05 model seconds**. The unknown call separately reserves 123,846 tokens and logs 50.36 seconds. Accounted new tokens are 2,649,678; overall campaign accounted tokens, including separate prior pilots, are 14,498,226. There are **zero unclassified receipts, unresolved dispatches or unfinalized measured responses**. An unknown finalized reservation is still an accounting limitation, even when no dispatch remains unresolved.

| Stage | Measured calls | Measured USD | Input tokens | Output tokens |
|---|---:|---:|---:|---:|
| Root selection | 18 | 10.144755 | 1,595,536 | 86,683 |
| Formalization, including rejected outputs | 13 | 8.625805 | 623,226 | 220,387 |

All measured model IDs/versions are Opus 5. The unknown call records the requested Opus 5 model; served model/version are unverified. Full-lineage accounting deduplicates inherited receipts instead of summing per-run totals; it contains 316 measured and three unknown MODEL receipts.

### Native report, search evidence, rendering and copy

`ara report` exited **0** over **27 real run directories**: all prior 26 inputs plus this pilot. Recursive origin enumeration found no referenced extraction origin outside those inputs. The part 5 count-only planner remains a separately identified zero-generation configuration control, not an extraction ancestor. Native reporting verifies chains and available pinned origins before publication.

The part 6 search projection matches its sidecar inventory: **zero sidecars, traces, search-start/finish receipts or route graphs**. The rendered section explicitly states “No recorded search trees or routes.” The section exists, but the requested populated search-tree evidence is absent because construction stopped before freeze. No search result was reconstructed or fabricated.

**Full browser rendering failed.** Chromium crashed while loading the **3,703,537,195-byte HTML** on two attempts: the default attempt after 33.546 seconds and a retry with a 16 GiB JavaScript heap after 26.520 seconds. No full-page screenshot or successful full-document rendering is claimed. This is a practical usability limitation of the delivered monolithic report, not a successful browser check.

Static inspection of the complete file verified **244 sections** and every required anchor for all 27 runs, with zero missing anchors. An exact byte-for-byte excerpt of the last run's search section rendered successfully in Chromium **143.0.7499.4** and its screenshot was inspected. It states “No recorded search trees or routes.” This excerpt proves only that disclosure renders in isolation; it does not substitute for full-page rendering. The full native HTML, Markdown, JSON and support files remain unchanged. The concise written report at `/home/dev/ara-work/reports/zeta-full26.md` is the readable handoff; full raw evidence remains in the native outputs. Failed attempts, static check and excerpt evidence are preserved under part 6 controls.

All **57 generated files**, totalling **9,107,028,227 bytes**, were copied to `/home/dev/ara-work/reports/overnight/` and individually SHA-256 verified, including all support/event/artifact files. No unexpected stale files remain. Twelve historical core backups are preserved and hash-match their source reports: HTML/Markdown/JSON for `report-part2` through `report-part5`; each JSON backup is its prior `data.json`. The new HTML is **3,703,537,195 bytes**, retaining full receipts and repeated lineage views.

Chains verify against recorded checkpoints; rewriting both chain and checkpoint is outside that guarantee. Raw artifacts are separately labelled unless matched to receipts; search sidecars require native seals. Historical missing code revisions/source IDs, unknown usage, and missing original title/author metadata remain explicit. The new run's revision is recorded in controls and this handoff. No full release, semantic completeness or philosophical-success claim follows from these structural checks.

| Delivered file | Bytes | SHA-256 |
|---|---:|---|
| `report.html` | 3703537195 | `a6ca832d138af03abc1b39f4839472c76b135b1778bfa19620d0a3ffe4dba5df` |
| `report.md` | 2673308570 | `d4627ddfc3de38fd18988832e89bf5092c2c9f134b45de7c58c1fb1f6d79499d` |
| `data.json` | 612847862 | `2f9a526dcb4e0551f5f965ef2862148510dfbc404cbd5fbe4801377f683c233b` |

Authoritative extraction: `/home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt`, SHA-256 `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`. Native pilot/report: `runs/overnight6-pilot/` and `runs/overnight6-report/`. Approved configuration: `runs/overnight6-control/config.yaml`, byte-identical to part 5. At the part 6 checkpoint, source was clean at `1411e91c70a6537422dbfece6f6ed1301b90e748`.

Controls under `/home/dev/ara-scaffold/runs/overnight6-control/` include admission/config/backup receipts, live plan, pilot summary, final construction, symbol-lineage and window audits, terminal diagnostics/boundary, process-end record, report-origin check, native-report check, browser/copy receipts, final verification and work notes. The previous written report is preserved as `zeta-full26-part5.md`; previous run controls and extraction/context audits remain intact. Generated config and control scripts are ignored; no tracked source edits, delegation, commit, push or route selection occurred.


## Finding placement

| Action-relevant finding | Deliverable placement |
|---|---|
| 1. Live resume exited 2 on HTTP 400 counter rejection before paid dispatch/restoration; no capacity retry | Part 7 execution and exact stop |
| 2. Original log prefix and 18 plan/batch artifacts preserved; 140 prior provisional commitments not repaid | Preservation and scope of resume proof |
| 3. Phi offline restoration and 24-minute startup are not live completion; exact reviewer tests/limits | Preservation and scope of resume proof |
| 4. New counter receipt suppresses complaint and lacks request kind/count; source-path inference is distinguished | Part 7 execution and exact stop |
| 5. Stored cap has no override and slightly exceeds stricter USD115 allowance; conservative unused supervision buffer | Part 7 budget handling |
| 6. Xi absent from local/remote main; final report/destination absent; DONE links only prior part 6 report | Opening; Xi integration and report status |
| 7. Zero new spend; unchanged Zeta/night/campaign totals and three unknowns; no unresolved calls | Part 7 budget handling |
| 8. No ledger/merge/freeze/targets/search/routes/awaiting-selection; 140 remain provisional; no route chosen | Opening; Preservation and scope of resume proof |
| 9. Unchanged 26 nonempty graphs, per-paper/kind counts, seven partial sources, no completeness claim | Opening; Extraction inventory; Item counts by kind |
| 10. Original snapshot/identity retention, publication history and Pi-B1 context repair | Publication, retention, and prerequisite-context fix |
| 11. Quarantines, dependencies, gaps, missing inference, thin-range overlap/conflict and placeholder reasons | Coverage, quarantine, and limits |
| 12. Book continuation/reconciliation limits, retained ranges, parser/unread-page diagnostics and no OCR | Coverage, quarantine, and limits; Partial-source physical page diagnostics |
| 13. Wrong 70–90 estimate corrected to 233; literal part 3 config differed and operator approved 233/48,000 | Reviewed construction and corrected symbol basis |
| 14. Round 3 global admission, live soft-share borrowing, 140 provisional commitments/eight sources, 7 omitted-support edges | Live construction, cuts and window outcomes |
| 15. Ten earlier native skips with exact causes/costs; correction allowance shared per call type | Live construction, cuts and window outcomes |
| 16. Original window 17 opaque rejection and unknown charge; Sigma diagnosis does not explain new counter 400 | Preservation and scope of resume proof; Exact terminal boundary and restart recovery |
| 17. Part 6 daemon restart killed supervisor only; original OS exit unavailable, unlike part 7 exit 2 | Exact terminal boundary and restart recovery; Part 7 execution and exact stop |
| 18. Prior 27-input native report/copies/backups retained; inherited deduplication and trust/revision/metadata gaps | Native report, search evidence, rendering and copy |
| 19. Old 3.70 GB HTML browser failures; Xi's reviewed readable output is not this task's final deliverable | Xi integration and report status; Native report, search evidence, rendering and copy |
| 20. Stored source/config/artifact unchanged; no source edits/delegation/push/route selection; durable current receipts | Part 7 execution and exact stop; Xi integration and report status |

20 findings, 20 placed.

DONE zeta overnight extracted=26/26 excluded=0 quarantined=363 items=5659 freeze=none commitments=0 targets=0 routes=0 new_usd=70.402330 status=blocked:resume-token-counter-invalid-request report=/home/dev/ara-work/reports/overnight/report.html
