
## Round 4

Subject: `feat/paper-extraction`, final HEAD **be8c2c2ee2adaf491a8a31bb38640d40e287cebc**. Starting revision
`1b152d9c78c9c30851b48d106359cb796bcedc61`. Read Delta's entire Re-review round 3.
Implemented D3-S1/S2/S3, then D3-B2/B1, then the unpaid 26-PDF plan. No paid
generation, push, pilot, worker or subagent. Status: **awaiting-review**.

Local commits: `851022f` (policy, empty stages and global capacity), `783e8b4`
(bounded graph/obligation windows), and `be8c2c2ee2adaf491a8a31bb38640d40e287cebc` (unpaid planner and final
native-profile, prior-context and remaining-allowance refinements).

### Policy and capacity changes

- **D3-S1:** `extraction-full` explicitly selects `claude-opus-5` at the extraction
  stage, with no fallback, aggregate nonzero-inference acceptance, and one targeted
  correction per paper. The model remains editable in one stage line. Enclosing
  token/cost caps and extraction cost cap are `null`; generation refuses before
  provider creation until the operator fills all three. Historical profiles retain
  their earlier defaults, including their extraction model and optional policies.
  Native `ara run --profile extraction-full` accepts the same profile and preflights
  its caps, so catalogue size and construction corrections reach the actual build.
- **D3-S2:** an empty readable range needs a complete, obligation-free model-authored
  reason, persisted with physical page IDs. This cannot erase pending references or
  bypass aggregate inference acceptance. A zero-root window must account for every
  omission group, skips formalization and participates in the lifecycle. Overall
  empty T still refuses; a large source can have empty windows and a successful T.
- **D3-S3:** working capacity is cumulative and measured against actual accepted T;
  unused capacity carries forward and each root-selection request receives that
  same measured remaining allowance. Before formalization the runtime counts the exact
  source-copy payload in a minimal formula envelope, the catalogue and the remaining
  global capacity. Full profile uses a configurable 256-token/selected-item catalogue
  growth reservation and a 32k catalogue limit. Historical profiles use zero growth
  reservation; actual catalogue growth remains checked. These are planning bounds,
  not predictions of formulas or semantic reuse. The two-rich-batch proof accepts
  16 distinct named symbols near a 19k catalogue limit and 16 commitments under a
  10k working limit. Capacity refusals retain logged roots/closures for explicit
  revised selection; there is no automatic budget-driven root reselection.
- **D3-B2:** a shared counted partitioner windows within a large source. Selection
  sees bounded evidence; closure uses the full immutable graph. Exact IDs already
  formalized are reused, with prior formulas and supporting source evidence supplied
  to later formalization. Every counted formalization inventory is fixed, and an
  oversized required closure refuses before dispatch rather than losing support.
  Final selected/omitted accounting covers the whole graph; one merge and freeze.
- **D3-B1:** reconciliation never reconstructs one unbounded whole-paper request.
  No-obligation review traverses bounded graph windows; discovered gaps receive
  stable IDs. Each obligation traverses counted original-page/evidence windows,
  accounting for itself as resolved or pending on every turn. Models can request
  complete next page/evidence sets; unknown/unread IDs, oversized required sets,
  request cycles or the 16-request default limit refuse without discarding context.
  Pending ledgers and accepted range/window artifacts survive refusal. A resolved
  ledger cannot coexist with an unexplained remaining reference. Runtime validates
  inventory and provenance; semantic adequacy remains a source-review judgment.

### Executed proof and review limits

- Final `uv run pytest -q`: **373 passed, 2 skipped, 375 collected (257.15s)**, log `runs/gamma-round4/pytest-final.txt`.
- Final complete control runner: **154/154 red, all 154 restored green, exit 0**, run only after pytest ended;
  results and actual red/restored traces are in `runs/gamma-round4/controls/`.
- New tests first failed against the old paths. Offline proof includes a 98-item
  single source larger than one context, 8 selected items plus 90 accounted
  omissions, cross-window prerequisites and one freeze; overlapping closures reuse
  prior formulas/support without duplicate evidence. A six-page source exceeding
  one context resolves a cross-window obligation after explicitly requesting pages
  1 and 6. Its unresolved variant refuses. A graph-only union larger than context
  traverses bounded review windows without omission. Oversized selected closures
  and catalogue growth refuse before formalization. Fixtures contain placeholders.
- Initial full-suite attempts exposed the historical low-density growth-reservation
  mismatch and a refusal-message regression; targeted repairs passed. Manual source
  inspection found the missing prior-context payload, added before the final suite.
  The final diff audit also corrected root selection to receive the measured
  remaining budget; its two-rich-batch regression first failed on the stale full
  allowance, then passed. Earlier failed test receipts remain in `runs/gamma-round4/`. Mutation-anchor
  audit caught a control-script quoting error and relocated anchors before execution.
- Inline simplification removed duplicated selection rendering and obsolete
  proportional/all-paper packing. No lint/typecheck command is configured.
  **Code review: skipped (ce-code-review unavailable)** — its independent delegated
  review workflow conflicts with the explicit solo restriction. No completed CE
  independent-review receipt is claimed; this handoff is for Delta's next review.
  [ce-code-review SKILL.md](/home/dev/.codex/plugins/cache/compound-engineering-plugin/compound-engineering/3.31.0/skills/ce-code-review/SKILL.md)
  requires “Dispatch the selected local reviewers as one concurrent batch”; that
  delegated workflow was not available under the solo constraint.
  Manual diff inspection covered runtime callers, prompts, schemas, immutable
  artifacts and the source/citation boundary, not real-model semantic fidelity.

### 26-paper unpaid plan

Read the 26 available PDFs under `/home/dev/ara-scaffold/literature/fulltext/`, using
its manifest. The manifest has 53 records; the other 27 missing files were not part
of this requested 26-PDF size check. Native command: `ara plan-extraction --profile
extraction-full --token-counter provider`, with those 26 explicit `--paper-id` values,
the manifest/fulltext paths above, and `--run-dir runs/gamma-round4/plan26`.
The exact argv, PDF hashes, configuration and full counted prompts are retained in
that ignored run directory; the report below contains identifiers and numbers only.

Verified free counting from the official token-counting documentation before API
use: “Token counting is **free to use**”. Receipt:
`runs/gamma-round4/free-count-verification.json`; source document:
`runs/gamma-round4/token-counting-docs.txt`. The numeric plan audit records **106
count requests, zero generation dispatches, zero MODEL events and USD0.000000**.
The planning provider cannot generate and its internal generation caps are zero.

**26/26 initial readable-range plans fit**: 1,379 physical pages, 1,368 readable
pages, 66 ranges, **1,592,920 provider-counted initial input tokens**. Maximum
initial range: **34,808 input + 32,000 output = 66,808**, below 200,000 context.
Execution and planning share the range planner; full profile also splits using a
1,200-output-token/readable-page scenario (prior bounded sample: about 1,150,
including thinking). Actual exhaustion can still require a smaller range.

The table's input counts are provider counts including the runtime's conservative
schema overhead. Selection windows are estimates from 1,270 graph tokens/readable
page, a 70k source batch and 8k wrapper allowance. Actual graphs, root inventories,
closures and catalogues do not exist for this corpus yet, so construction admission
remains conditional; these 38 estimated selection windows are not measured batches.
`fits` means initial readable extraction ranges fit, not full semantic coverage,
spend authorization, or an accepted extraction/build/pilot chain.

Costs use Opus **USD5/M input, USD25/M output**. “Initial” uses counted input plus
1,200 estimated output tokens/readable page. “With review” adds an explicitly
estimated no-obligation graph-review pass: binary windows with 160k graph capacity,
8k wrapper input and 8,192 output/window. This is the final-line cost scenario;
actual obligation scans, context requests, retries, targeted corrections and all
construction/pilot costs are additional and unmeasured.

| Source ID | Pages/readable | Initial ranges | Counted input | Est. selection windows | Admission | Initial USD | With review USD |
|---|---:|---:|---:|---:|---|---:|---:|
| vonfintelgillies2007 | 32/32 | 2 | 37,075 | 1 | fits | 1.145375 | 1.593375 |
| eganweatherson2011 | 21/21 | 1 | 24,309 | 1 | fits | 0.751545 | 0.751545 |
| vonfintelgillies2011 | 23/23 | 1 | 31,204 | 1 | fits | 0.846020 | 0.846020 |
| wright2007 | 22/22 | 1 | 25,987 | 1 | fits | 0.789935 | 0.789935 |
| schaffer2011 | 49/48 | 2 | 59,170 | 1 | fits | 1.735850 | 2.285450 |
| braun2012 | 52/52 | 2 | 45,408 | 2 | fits | 1.787040 | 2.362040 |
| eganhawthorneweatherson2005 | 48/48 | 2 | 48,903 | 1 | fits | 1.684515 | 2.234115 |
| egan2007 | 39/39 | 2 | 34,223 | 1 | fits | 1.341115 | 1.833565 |
| macfarlane2011 | 44/44 | 2 | 46,825 | 1 | fits | 1.554125 | 2.078325 |
| macfarlane2014 | 358/349 | 16 | 377,551 | 8 | fits | 12.357755 | 15.553105 |
| yalcin2007 | 44/44 | 2 | 56,914 | 1 | fits | 1.604570 | 2.128770 |
| yalcin2011 | 38/38 | 2 | 52,170 | 1 | fits | 1.400850 | 1.886950 |
| rothschild2012 | 13/13 | 1 | 17,337 | 1 | fits | 0.476685 | 0.476685 |
| moss2015 | 81/81 | 4 | 85,761 | 2 | fits | 2.858805 | 3.617955 |
| hawkesteinertthrelkeld2021 | 38/38 | 2 | 63,759 | 1 | fits | 1.458795 | 1.944895 |
| veltman1996 | 44/44 | 2 | 46,036 | 1 | fits | 1.550180 | 2.074380 |
| gsv1996 | 35/35 | 2 | 43,974 | 1 | fits | 1.269870 | 1.736920 |
| willer2013 | 40/40 | 2 | 51,914 | 1 | fits | 1.459570 | 1.958370 |
| yalcin2015 | 54/53 | 3 | 68,135 | 2 | fits | 1.930675 | 2.512025 |
| ninan2018 | 45/45 | 2 | 57,472 | 1 | fits | 1.637360 | 2.167910 |
| beddorgoldstein2021 | 47/47 | 2 | 49,346 | 1 | fits | 1.656730 | 2.199980 |
| hollidaymandelkern2024 | 70/70 | 4 | 111,982 | 2 | fits | 2.659910 | 3.349210 |
| kolodnymacfarlane2010 | 31/31 | 2 | 36,836 | 1 | fits | 1.114180 | 1.555830 |
| klinedinstrothschild2012 | 50/50 | 2 | 47,878 | 2 | fits | 1.739390 | 2.301690 |
| bledin2014 | 40/40 | 2 | 50,312 | 1 | fits | 1.451560 | 1.950360 |
| knobeyalcin2014 | 21/21 | 1 | 22,439 | 1 | fits | 0.742195 | 0.742195 |
| **Total** | **1379/1368** | **66** | **1,592,920** | **38 estimated** | **26 fit** | **49.004600** | **62.931600** |

Physical page ranges follow. Commas within one range identify gaps in readable page
numbers; semicolons separate model requests. Exact page arrays and per-range input
counts are in `runs/gamma-round4/plan26/extraction-plan.json`.

| Source ID | Planned physical page ranges |
|---|---|
| vonfintelgillies2007 | 1-16; 17-32 |
| eganweatherson2011 | 1-21 |
| vonfintelgillies2011 | 1-23 |
| wright2007 | 1-22 |
| schaffer2011 | 2-25; 26-49 |
| braun2012 | 1-26; 27-52 |
| eganhawthorneweatherson2005 | 1-24; 25-48 |
| egan2007 | 1-19; 20-39 |
| macfarlane2011 | 1-22; 23-44 |
| macfarlane2014 | 1,3-7,9-13,15-24; 25-39,41,43-48; 49-70; 71-92; 93-113; 114-135; 136-151,153,155-159; 160-181; 182-202; 203-224; 225-246; 247-268; 269-290; 291-312; 313-333,335; 336-349,351-358 |
| yalcin2007 | 1-22; 23-44 |
| yalcin2011 | 1-19; 20-38 |
| rothschild2012 | 1-13 |
| moss2015 | 1-20; 21-40; 41-60; 61-81 |
| hawkesteinertthrelkeld2021 | 1-19; 20-38 |
| veltman1996 | 1-22; 23-44 |
| gsv1996 | 1-17; 18-35 |
| willer2013 | 1-20; 21-40 |
| yalcin2015 | 1-26; 27-39; 40-53 |
| ninan2018 | 1-22; 23-45 |
| beddorgoldstein2021 | 1-23; 24-47 |
| hollidaymandelkern2024 | 1-17; 18-35; 36-52; 53-70 |
| kolodnymacfarlane2010 | 1-15; 16-31 |
| klinedinstrothschild2012 | 1-25; 26-50 |
| bledin2014 | 1-20; 21-40 |
| knobeyalcin2014 | 1-21 |

### Cost, coverage and remaining gates

The primary **USD62.931600** extraction scenario includes 24 estimated graph-review
windows, with no unresolved-obligation work. Initial calls alone reserve 2,112,000
output tokens at 32k/range: **USD60.764600**, compared with their expected-output
scenario USD49.004600. Reserving full output also for the estimated review windows
would give **USD88.976400**. These are scenarios, not upper bounds: real obligations,
context retrieval, corrections and retries can add calls. Even the initial scenario
exceeds the historical USD30 profile. Including the review scenario gives
5,233,488 input-plus-output tokens; its full-output reservation scenario gives
6,275,280, also above the historical 6M token cap. Review tokens are estimates,
not provider counts. The operator must set the null caps; none
were raised here. Numeric derivation: `runs/gamma-round4/plan26-cost-scenarios.json`.

Seven sources have **82 affected physical pages**: `schaffer2011` 1 (unread),
`braun2012` 5, `macfarlane2014` 15, `yalcin2007` 42, `yalcin2015` 3,
`ninan2018` 8 and `kolodnymacfarlane2010` 8. The other 81 affected pages have retained
encoding warnings. Ten blank pages plus the one unread page explain the 11-page
difference between physical and readable totals. Strict missing/coverage policy
still refuses partial sources; planning fit does not override it. pypdf warnings
are retained under `runs/gamma-round4/plan26-stderr.txt`; this is not OCR or proof of
correct text order/glyph interpretation. No source argument content is reproduced.

**D3-N1 remains a disclosed limit:** targeted patches cannot delete rejected entries,
repair truncated/malformed inventories, or guarantee successful recovery. Live
construction patch success and the new window protocol's live wire acceptance and semantic
quality remain unproved this unpaid round. **D3-N2 remains separate:** no native
frozen-T resume path or downstream live pilot was added/executed. Passing a frozen
commitments file as literature is still not an authorized continuation path.

The accepted round-3c 45-item freeze is untouched; SHA256 remains
`25a7ec8c35d393b230738e6008467d70926697db6bed1f91c72b5edcd39cb3a4`.
No earlier failed receipts or unknown reservations were released. Campaign totals
remain **USD5.461870 measured + USD3.934240 held unknown = USD9.396110 accounted**;
build campaign remains **USD5.433360 of USD6**. This round adds USD0.000000 paid
usage. No full corpus extraction, construction or pilot success is claimed.

### Findings placement

| Finding | Deliverable placement |
|---|---|
| D3-S1: full-run stage/policy and unset caps | Policy and capacity changes; Cost, coverage and remaining gates |
| D3-S2: legitimate empty ranges/windows | Policy and capacity changes; Executed proof and review limits |
| D3-S3: global working/catalogue capacity and prediction limits | Policy and capacity changes; 26-paper unpaid plan |
| D3-B2: single-source windows/full closure/prior context/oversized closure | Policy and capacity changes; Executed proof and review limits |
| D3-B1: bounded review/obligations/context requests and safe refusals | Policy and capacity changes; Executed proof and review limits |
| D3-N1: patch deletion/truncation/live semantic limits | Cost, coverage and remaining gates |
| D3-N2: frozen-T continuation/pilot gate | Cost, coverage and remaining gates |
| Corpus scope, missing 27 files, unread/glyph-warning coverage | 26-paper unpaid plan; Cost, coverage and remaining gates |
| Cost scenarios, omitted work, no cap authority, retained campaign reservations | 26-paper unpaid plan; Cost, coverage and remaining gates |
| Free endpoint verification and zero generation/spend | 26-paper unpaid plan; Cost, coverage and remaining gates |
| Executed verification, repaired regressions and independent-review gap | Executed proof and review limits |

**11 findings, 11 placed.**

DONE gamma round4 head=be8c2c2ee2adaf491a8a31bb38640d40e287cebc tests=373/375 negctl=pass fixed=D3-S1,D3-S2,D3-S3,D3-B2,D3-B1 plan26=fits est26_opus_usd=62.931600 status=awaiting-review
