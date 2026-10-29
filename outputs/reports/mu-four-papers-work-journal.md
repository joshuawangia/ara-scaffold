# Mu: four-paper acceptance

Work in progress. Base `0eb85924afeb01aac44e5bc0ca5f2714c6a99823`; isolated branch `fix/four-paper-acceptance`, checkout `/home/dev/ara-work/mu`. Original checkout, runs and cache are read-only. No delegation or push.

## Diagnosis and intended change

Observed native receipts in full26-rerun and full26-v4a, including raw requests, responses, physical page inputs, corrections and immutable range artifacts. Content stays in ignored runs, never tracked files.

- `vonfintelgillies2007`: reversed physical page endpoints in the model output reach the page-bounds check. Earlier recovery also encountered inconsistent coverage flags. Ordering endpoints is content-free; it does not justify moving citations to other pages.
- `eganweatherson2011`: Pass A starts with one placeholder qualification, then one placeholder distinction, then 63 distinctions/qualifications without inference edges. This is not a reconstructed-origin rejection. Earlier attempt has both genuine inference-bearing ranges and proposition-only ranges. Do not convert kinds or invent links deterministically.
- `vonfintelgillies2011`: Pass A emits 87 proposition/view items, including 41 intermediate conclusions, but no inference edges; corrections remain non-inference placeholder items. Earlier attempt similarly emits 110 non-inference items. No reconstructed-origin inference was emitted. Prompt and provider wire must allow honest reconstruction, and absence requires an explicit disposition.
- `schaffer2011`: terminal patch contains two identical items with the same local ID. Retain both under stable distinct IDs, preserve references to the first identical occurrence, and refuse genuinely ambiguous references to distinct duplicate items with specific correction feedback. Earlier errors include an inference qualification with the wrong kind.

Responsible path: `providers.structured_schema` exposes restricted inference origin; `calls._call_once` normalizes wire values, validates schema and logs; `_extraction_response` enforces graph/link/page checks and patch merging; `_extract_paper` assembles ranges through `reconciliation.reconcile`; `extraction.resume_papers` pins source and acceptance identity and verifies graph receipts. V4 identity equality currently blocks all schema/prompt changes. V5 must explicitly recognize the reviewed v4 contract and revalidate graphs offline without rewriting original receipts.

Target: page-linked, attributed source argument structure, supported reconstructed links disclosed by origin, paper-level inference coverage or explicit absence, bounded specific corrections, no dropped items. Neither page bounds nor graph validity proves semantic fidelity. Literal placeholders and substantive model omissions cannot be repaired by renaming or by relaxing structure.

## Evidence in progress

Compared locked pypdf 6.21.1 with separately pinned pdfminer.six 20250506, without changing production dependencies. Raw per-page text and statistics are in `runs/mu-control/`. Inspected prose order, headings, footnotes and hyphenation. No two-column interleaving observed in inspected source pages. Pdfminer loses word spacing across the 2007 PDF; pypdf remains more usable. No demonstrated causal text failure warrants replacing the extractor. Source font artifacts and a diagnosed unread first page in Schaffer remain disclosed; no OCR or silent text replacement.

Replay harness needed explicit exclusion of imported schema-preflight MODEL receipts and responses with no provider body. Original harness otherwise crashes on absent INPUT_JSON. Replays cover the original two attempts and Pass A with transitive Kappa history; deduplication remains by full receipt identity. The exact base is archived under ignored `runs/mu-baseline-code`; only the replay harness compatibility fix is copied there. Early incomplete replay directories are diagnostics, not results.

Next: finish regressions, offline v4 revalidation and exact before/after replay; full pytest then control runner sequentially; live schema preflight <= USD0.25; four-paper extraction <= USD10 new using native read-only ancestry import; local commit and final report.

## Implemented changes

V5 permits `reconstructed` origins in both local and provider schema; retains disclosed `no_inference_reason` as page-scoped graph dispositions; checks inference across the paper, with a counted whole-paper review when range responses provide neither links nor an exhaustive absence disposition. No range-level link quota. Existing obligations still traverse native reconciliation. A paper-level review exceeding context capacity refuses without truncation.

Reversed endpoints are sorted before validation and logged with old/new values. Repeated identical correction items receive stable suffixes without item deletion; references continue to the first identical occurrence. Referenced distinct duplicates refuse as ambiguous rather than guessing. Three corrections are enabled in the full profile, retaining native accounting and specific validation feedback.

V4 migration is explicit, pinned to the reviewed predecessor prompt/schema and unchanged source/profile, with offline schema/link/attribution/page/citation/obligation revalidation. Old immutable outcomes remain v4; a separate `extraction_acceptance_revalidated` receipt records the v5 check. No relabeling or new model call.

## Offline replay

Exact-base replay: 59 unique paper responses; 3 accepted, 17 normalized, 30 needing correction, 2 subdivision, 7 terminal. V5 with three corrections: 3 accepted, 20 normalized, 33 needing correction, 2 subdivision, 1 terminal. Thus immediate response acceptance improves 20/59 to 23/59. Remaining terminal is a provider refusal in the inherited Kappa partial-source case. Twelve non-paper/no-body receipts are explicitly listed as excluded (11 schema gates, one missing provider body). Accepted historical responses remain accepted or normalized.

The added immediate acceptances are the two reversed-page responses in the earlier introduction extraction and the reversed-page Pass A response for the 2007 paper. The duplicate patch now proceeds past ID handling but still needs a model correction for its qualification-kind error; this is not fabricated success. Replay validates responses independently and does not establish paper completion, source fidelity, or successful continuation. Evidence: `runs/mu-baseline-code/runs/replay/summary.json`, `runs/mu-replay-after/summary.json`.

## V4 reuse

Executed socket-blocked native `resume_papers` against Pass A alone, verifying its transitive ancestry and accepted graph hashes. All five v4 papers survived offline v5 revalidation: rothschild2012 71 items, knobeyalcin2014 58, macfarlane2011 169, veltman1996 267, wright2007 105; **670 items total, five migration receipts, zero provider calls**. Original identity and outcomes remain unchanged. Evidence: `runs/mu-v4-reuse/events.jsonl`, `runs/mu-control/v4-reuse.json`. This includes the newest Pass A acceptance, not merely older probe graphs.

The alternative extractor comparison has a dedicated ignored reproducibility lock at `runs/mu-textcheck/uv.lock`; production `uv.lock` is unchanged. Median per-page word overlap with pypdf is 0.998 for the introduction, 0.971 for the 2011 paper and 0.990 for Schaffer. The 2007 paper's 0.053 reflects pdfminer concatenating words, not pypdf losing paragraphs: 16/32 page strings are identical after removing whitespace. Other differences include ligature/font encodings and proof/header artifacts. These metrics and inspected source passages are diagnostic evidence, not a semantic completeness score.

## Verification

Full pytest on the final production code: **532 passed, 2 skipped / 534 collected**, exit 0, 318.29 seconds. Evidence `runs/mu-control/pytest-final.txt`. Earlier interrupted/targeted transcripts remain diagnostic only. During the negative-control audit the absent-disposition regression was strengthened to assert no extra dispatch after rejection; its mutation/restoration proof is part of the control runner.

Socket-blocked live preflight confirmed native inherited accounting **USD26.872865**, aggregate/extraction cap **USD36.872865**, exactly **USD10 new allowance**, three corrections and four selected paper IDs; no provider constructed. The live schema gate will be separately bounded by USD0.25 and imported into the same USD10 allowance, making the combined cap stricter than the two separate requested ceilings. Existing unknown-usage reservations remain counted and disclosed. Evidence `runs/mu-control/preflight.json`.

Control repair: the first full control attempt stopped at an obsolete reversed-range test node (pytest exit 4, not a successful negative control). The anchor now tests the new repair case and its still-rejected out-of-bounds citation. Eleven affected controls were then executed successfully (all mutants exit 1, all restorations exit 0), including stable duplicate IDs, ambiguity refusal, third correction, disposition requirement and v4 graph revalidation. Full runner restarted; `runs/mu-control/negative-controls-final.txt` is the authoritative pending transcript. No production change occurred after the passing full pytest.

Locked extractor replay verified exactly the same saved page text on all 125 pages for both pypdf and pdfminer; `runs/mu-control/locked-text-verification.json`. The first pypdf environment and production source hashes remain unchanged.

Current checkpoint: final production code tested, local commit pending, full controls running; no paid calls yet. Live gate/extraction launcher and exact caps prepared at `runs/mu-control/launch.py` and `live-config.yaml`. Next execute gate only after full controls pass, then four-paper native extraction using the prepared launcher and documented environment credential file; inspect outputs, record costs/outcomes, commit locally and finish finding placement.

## Content-quality limitation in reused history

A separate read-only inventory found literal placeholder-prefixed text in **six items across three already accepted v4 graphs**: wright2007 (1), macfarlane2011 (1), veltman1996 (4). The other two reusable graphs had no such prefix matches. These are existing outputs, preserved rather than repaired or rewritten. This materially limits any claim that reusable/structurally valid means faithful or complete. The check is a literal-prefix screen, not an exhaustive semantic audit. No new extraction of these five papers is authorized by this four-paper budget. The live four-paper results must be inspected separately for this failure pattern.

Final controls: **216/216 mutations detected (exit 1), all restored tests passed (exit 0), runner exit 0**, sequentially after full pytest. The final 18 v5 regressions also passed after restoration, including the strengthened no-extra-dispatch assertion. Two full-suite skips are opt-in paid tests. Locally committed as `c42bbc95c866f4c87cdf698d2456a21844017239`; tracked status clean. No push. Native live grammar gate started at this head with the prepared USD0.25 cap; extraction awaits its result.

## Live progress checkpoint (not final outcomes)

At commit c42bbc95c866f4c87cdf698d2456a21844017239 the native schema gate passed 5/5 in 26.361 seconds for **USD0.046880**. The four-paper run imports Pass A plus this gate read-only, with no push or source edits. Its aggregate cap is unchanged.

The 2007 paper failed after seven new responses, costing **USD2.545590**. Its two initial ranges each yielded one literal placeholder item, accepted structurally before the paper-level inference check. Reconciliation correctly detected the missing argument inventory and opened two obligations. A subsequent response had root source ID `x`; corrections then tried to redeclare the immutable placeholder evidence. Three corrections exhausted without a valid graph. This is a new live failure path, not the original reversed-page failure. It shows that structural relaxation does not repair bad accepted range content. No completed paper is claimed.

The introduction is currently receiving correction for absent inference nodes and absent explicit no-inference disposition. Total accounted extraction spend at this checkpoint is USD3.020820 plus the gate. Native paid execution remains active under the cap. If a useful allowance remains after all four, a counted whole-paper request for the 2007 paper could avoid accepting a range before paper-level validation; no such additional request has yet been dispatched.

The introduction completed on its fourth response (initial plus three corrections): **125 items, 26 paper-stated inference nodes, zero literal placeholder-prefix items**, new paper spend USD1.632025. Kinds: 49 premises, 23 intermediate conclusions, 26 inferences, 4 qualifications, 19 reported views, 2 attacked views, 2 distinctions. Five spot-checked citations (local IDs n1, p5, inf11, p21, r16; physical pages 1, 3, 8, 13, 19) were supported by the cited source passages with the reported/attacked attribution preserved. This is a sample, not an exhaustive fidelity or completeness audit. The 2011 paper is now running.

Concurrent-history discovery: zeta is continuing in `/home/dev/ara-scaffold/runs/full26-v4a2`, beyond the earlier report snapshot. It has newly accepted eganhawthorneweatherson2005 (213 items) and yalcin2007 (210 items). Native offline v5 reuse validation is running against that current chain, with no provider and no source writes. The same literal-prefix screen finds 4 and 2 placeholder items respectively, so the known v4 quality inventory is now **12 such items across five of seven completed graphs**. Do not report only the earlier five-paper snapshot as all current reuse evidence.

The active paid run's second paper is accepted (125 items); the third encountered output exhaustion, subdivided, and is correcting blank attribution. No change to paid caps, code, schemas, or existing outcomes has been made. A new full pytest run on the exact committed test tree is also running read-only (no mutation controls during live generation); this covers the strengthened assertion added before the successful control run.

Updated verification: exact committed-tree pytest completed with **532 passed, 2 skipped in 276.07 seconds**, `runs/mu-control/pytest-committed-head.txt`. The successful 216-control sequence preceded all paid calls; no mutation runner was used during live generation. The seven-paper concurrent-history native reuse check completed: **1,093 items, seven v5 revalidation receipts, zero provider calls**, `runs/mu-control/v4-current-reuse.json` and `runs/mu-v4-current-reuse/events.jsonl`. Its two added graphs are the current zeta acceptances listed above.

The 2011 paper's first accepted range has 84 items/15 inferences and one literal placeholder. Its second range currently has one placeholder item; reconciliation has opened obligations rather than publishing completion. Accounted new extraction spend reached USD6.385620. Structural acceptance of placeholder-only ranges remains a demonstrated limitation under the requested strict relaxation; a new content-quality rejection rule would be a distinct tightening, so it has not been silently introduced.

The third paper's obligation continuation twice failed the exact obligation inventory check and is using correction 2. Accounted new extraction spend is USD7.443895 plus the USD0.046880 gate. The run still has only the introduction completed. The native per-request maximum reservation may stop later work before all remaining dollars are consumed; no cap increase or silent ledger bypass is permitted. The proposed whole-paper follow-up remains conditional on a usable remaining allowance after the authorized four-paper run, and has not been dispatched.

Further raw-response diagnosis: the 2011 obligation requests supplied one exact obligation ID. The first rejected continuation omitted both `resolutions` and `pending_obligation_ids` while returning a context request; later corrections again omitted both ledger fields. The source graph and obligation inventory therefore cannot be marked complete. This is an observed producer/validator mismatch, not missing PDF text. The final correction is now in flight at USD8.039050 extraction spend plus the gate; the combined remaining allowance is below USD2, so the contemplated extra whole-paper run is unlikely to be admissible.
