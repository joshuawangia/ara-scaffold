# Eta: shared frozen T

Implemented and committed locally on `feat/shared-frozen-t` at `ec8e1870926c5fdf226abfab11e5426ac3aee5ad`.
Parent: requested `ba3a004`. Checkout: `/home/dev/ara-work/eta`.
The pilot working tree and its runs were not modified. No paid calls, delegation,
or push occurred. Non-author review remains with the caller.

## Design

`ara run --from-frozen <builder-dir>` uses the existing run lifecycle and starts
at target proposal. It requires explicit `--cost-cap-usd` and `--token-cap`, and
accepts the existing topic/profile/configuration flags. Construction is skipped;
the new run references the original freeze and stores byte-identical T without
another freeze event. The ordinary search, selection, writing and export paths
remain in use, including completion through a later `ara select`.

The source is read without creating locks or writing files. Verification covers
the full log chain and checkpoint, exactly one freeze, canonical T/file hash,
construction configuration and schema contracts, original model/cache receipts,
extraction import digests and reconstructed literature, and rich construction
plans, batch artifacts and merge agreement. Invalid sources refuse before provider
creation. An imported run cannot construct or freeze T again.

Original chain rows and rich artifacts are nested in `frozen_history_import`,
with original labels, timestamps and charges preserved. Nesting prevents old
lifecycle events from becoming candidate events and keeps inherited charges out
of local budgets. Methodology names the builder, original freeze hash, T hash,
inherited/local totals, and candidate identity. `campaign_totals(log_paths)`
deduplicates original MODEL receipts across extraction, builder and candidate
logs; the caller supplies the complete campaign log set.

Each candidate receives a fresh UUID response-cache identity and random engine
seed, both recorded in effective configuration and cache keys. Candidate prompts
receive the shared T, not the builder's searches, writing or feedback. Within-run
cache replay and later selection retain that candidate's identity. The seed
controls engine tie-breaking; it is not a provider sampling seed. Separate requests
do not guarantee distinct answers or statistical independence.

## Decisions and limits

- Use the original completed builder, not another candidate. A run still awaiting
  selection is incomplete; a successful later selection/final draft completes it.
- Construction model/settings must match. Search/writer controls and local caps
  may differ. Both new-run caps are explicit; inherited costs consume neither.
- The `ba3a004` pilot format is supported using embedded canonical T, logged
  schemas and a committed legacy type/bank/schema manifest. New freezes record
  the hash and manifest directly. Legacy compatibility applies only when the
  manifest field is absent; recorded empty/null manifests refuse.
- Missing origins, broken receipts, changed hashes, topic differences, and
  relevant configuration/schema drift refuse explicitly. Hashes establish
  recorded integrity, not authenticity against a complete history rewrite or
  semantic fidelity of model-generated commitments.

Implementation is in the native CLI/orchestration/call/export modules and the
new `ara/runtime/frozen.py`. The legacy manifest is packaged as runtime data.
README and DECISIONS document usage and policy. The structured handoff lists all
13 changed files: [result JSON](/home/dev/ara-work/reports/eta-shared-frozen-t-result.json).

## Executed proof

Final commands ran sequentially on the tree now committed at `ec8e1870926c5fdf226abfab11e5426ac3aee5ad`:

| Check | Result | Receipt |
| --- | --- | --- |
| `uv run pytest` | 438 passed, 2 intentional live-provider skips, 0 failures; 300.44s | [Full log](/home/dev/ara-work/reports/eta-pytest.txt) |
| `uv run python tests/integration/negative_controls.py` | 182/182 defects detected; 182/182 restorations passed | [Full log](/home/dev/ara-work/reports/eta-negctl.txt), [case results](/home/dev/ara-work/reports/eta-negctl-results.json) |
| Restoration and commit checks | All 13 owned files match their verified fingerprints in the committed tree; no extra changed paths; clean worktree; requested parent | [Fingerprints](/home/dev/ara-work/reports/eta-pre-controls-files.json) |
| `git diff --check` | Passed | Executed before commit |

Tests use placeholders and offline transports. Native smoke candidates exercise
proposal, real engine search, writing/audits and export. Additional tests cover
later selection, legacy freezes, every requested refusal category, source
immutability, no re-freeze, distinct seeds/cache keys, local-cap exclusion and
campaign deduplication. Rich fixtures exercise extraction/construction receipts,
including tampered plan, batch and extraction provenance. Per-control red/green
logs remain under `/home/dev/ara-work/eta/runs/delta-controls/`.

The first native candidate test failed before implementation because the flags
were absent. Empty/null manifest cases also failed before their correction.
Full-suite verification found and corrected export compatibility with minimal
historical `run_started` records lacking configuration; its existing log-only
regeneration test now passes.

The mandatory controls also exposed a pre-existing test weakness: the broad
`match='paper'` assertion matched Python 3.15 JSON exception notes after an
admission guard was disabled. The existing paper-limit test now checks the
primary admission error, so serialization failure cannot substitute for validation.
No extraction production behavior changed. All 32 owning tests passed, and both
finite-limit mutations were subsequently detected and restored. These repairs
were followed by the final full sequential run above. Historical attempts and
red-first evidence are retained in [work notes](/home/dev/ara-work/reports/eta-shared-frozen-t-work-notes.md).

## Gaps

The running paid pilot and live provider behavior were not exercised. Legacy
compatibility and candidate independence have offline proof only. Non-author
review is pending; this is a verified local implementation handoff, not a release
verdict. The requested work is complete, with no implementation blocker remaining.

## Findings placement

| Finding affecting the caller's action | Placement |
| --- | --- |
| 1. Original completed builder, compatible configuration, full receipts and explicit caps are required. | Decisions and limits |
| 2. Legacy and minimal-log compatibility have bounded support; absent differs from empty/null, and live pilot compatibility is unexercised. | Decisions and limits; Executed proof; Gaps |
| 3. Cache/session separation and engine seeds do not establish provider sampling or statistical independence; within-run replay remains. | Design |
| 4. Inherited charges are separate; campaign totals require deduplicating an explicit complete log set. | Design |
| 5. Hash/provenance checks do not prove authenticity against full rewriting or semantic fidelity. | Decisions and limits |
| 6. Paid/live validation and non-author review remain outside this handoff; no push/release is claimed. | Gaps |
| 7. A pre-existing extraction-limit assertion was strengthened to make the required controls meaningful; review that test-only scope addition. | Executed proof |

7 findings, 7 placed.

DONE eta shared-t head=ec8e1870926c5fdf226abfab11e5426ac3aee5ad tests=438/440 negctl=pass report=/home/dev/ara-work/reports/eta-shared-frozen-t.md

## Round 2

Fixed **E-B1, E-S1, E-S2 and E-S3** on `feat/shared-frozen-t`. The final local
head is `185a318a7fa5a46485a375ee1cb26244c2254403`, based on theta
`be7468df12d4c0422d54f8ccd881d653cd92bdd4` as instructed. This section supersedes
the round-1 integration/readiness claims; the original receipts remain historical
proof of that earlier tree.

### Integration and behavior

First rebased onto theta's then-current `b063433`, preserving both sides of five
conflicts. After the operator supplied `be7468d`, committed the verified fixes and
rebased both eta commits onto it. The second rebase required combined README,
DECISIONS and control-list additions; runtime changes merged automatically.
The resulting eta commits are `5f46ea4` and `185a318`. Theta's acceptance-policy
and ancestor-success fixes are included. Eta retains the round-1 primary-error
assertion that prevents Python 3.15 exception notes from masking invalid-limit
admission defects. No push occurred.

- **E-B1:** `frozen.py` now calls theta's `verify_imports` and
  `extraction_outcomes`. Pinned/transitive origins are verified against their
  actual original prefixes, while literature reconstruction uses the current
  published batch. Live rendering and frozen receipt verification share
  `response_contracts.py`; new MODEL receipts record contract version 2. The
  exact `ba3a004` extraction prompt/schema digest admits compatible original
  accepted and rejected attempts. Unknown versions, changed prompts, changed
  hashes and missing/changed ancestors refuse. Historical receipts are preserved,
  not rewritten or redispatched under an old schema.
- **E-S1:** rich batch verification reconstructs commitments from accepted MODEL
  responses using the same encoded-formula decoder, correction merger and
  immutable-evidence normalization as live construction. Targeted patches bind
  to their original rejected response. Reconstructed commitments, symbols and
  alignments must match the saved batch; existing batch hashes, merge and frozen-T
  checks remain. Contradictory responses and altered correction origins refuse.
- **E-S2:** compatibility compares effective construction/extraction settings with
  defaults resolved, instead of comparing the entire `stages` map. Writer-only
  entries are allowed; relevant extraction and construction drift still refuses.
  This changes compatibility checking, not which provider stage overrides the
  runtime supports. Original builder settings remain verbatim in inherited history.
- **E-S3:** methodology includes inherited extraction outcomes, partial coverage,
  current failures, historical failures, failure policy, models and extraction
  usage in an explicitly labelled scope. Events stay nested: inherited spend is
  excluded from local totals, lifecycle and candidate caps.

### Executed proof

All final verification runs are offline and sequential on the committed tree
above. The full suite completed before starting the full mutation runner.

| Check | Result | Receipt |
| --- | --- | --- |
| Targeted integration after final rebase | 33 passed; theta acceptance/ancestry, native candidates and rich receipts | [Targeted log](eta-round2-rebased-targeted.txt) |
| Final `uv run pytest` | 513 passed, 2 live-provider skips / 515; 361.91s | [Full pytest log](eta-round2-final-pytest.txt) |
| Final `uv run python tests/integration/negative_controls.py` | 216/216 defects detected; 216/216 restorations passed | [Full control log](eta-round2-final-negctl.txt), [results](eta-round2-final-negctl-results.json) |
| Final restoration/committed-tree comparison | All 132 tracked files match input fingerprints; clean committed tree; `git diff --check` passed | [Input fingerprints](eta-round2-final-files.json) |

The four native cases are ordinary success, ordinary disclosed failure, resumed
success and resumed disclosed failure. Each uses native `ara run`, completes the
builder through later `ara select`, starts a candidate with `--from-frozen`, and
completes that candidate through selection/writing/audits/export. They verify
byte-identical T, immutable builder files, no local extraction/construction/freeze,
local/inherited charges and current/historical failure policy disclosure. Partial
coverage disclosure and historical accepted/rejected prompt compatibility have
additional focused import/export and receipt-boundary tests. Rich fixtures cover
encoded formulas, accepted correction patches, response/artifact disagreement and
changed correction candidates. All three merged-suite failures named by iota are
green in the final suite.

New mutation controls cover rich-response consistency, correction origins, current
outcome selection, pinned ancestors, writer-only settings, effective extraction
settings, inherited failures and historical prompt support. Existing controls were
retargeted when their production helpers moved; their expected injected failures
and restored passes remain required. Theta's new acceptance/ancestry controls are
included in the final runner. Per-case red/green outputs are preserved in
[final control receipts](eta-round2-final-controls/) and
`/home/dev/ara-work/eta/runs/delta-controls/`.

Earlier round-2 evidence is retained separately: [red regressions](eta-round2-red.txt),
[35 targeted controls](eta-round2-controls-targeted.txt), and the first full
[498/500 suite](eta-round2-pytest.txt) followed by
[209/209 controls](eta-round2-negctl.txt), all before the final theta rebase.
The final-base receipts above are the delivery evidence.

### Limits and operating requirements

Use the original completed builder with the same topic, compatible construction
settings, unchanged table and complete provenance; retain every pinned ancestor
log. Candidate caps are explicit. Preserve the complete campaign log set,
including builder work after freeze: a candidate-only set omits that later work.
Cache identities and engine seeds separate candidate searches but do not prove
provider sampling independence or statistical independence. Hash checks do not
authenticate a completely rewritten history or prove semantic fidelity.

No paid calls, real-provider generation/count service, source-checkout changes,
push or release occurred. Live quality, full-corpus budget sufficiency and campaign
completion remain unproved. Non-author review belongs to the caller. This handoff
is bound to the instructed theta `be7468d`; any further theta changes require a
new integration check.

### Round-2 finding placement

| Finding affecting the next action | Placement |
| --- | --- |
| E-B1: native contracts, supported historical receipts and required pinned origins | Integration and behavior / E-B1; Executed proof; Limits and operating requirements |
| E-S1: accepted rich responses and correction origins must agree with artifacts | Integration and behavior / E-S1; Executed proof |
| E-S2: writer entries are compatible; meaningful construction/extraction drift still refuses; no new provider overrides | Integration and behavior / E-S2 |
| E-S3: inherited coverage/failure disclosure includes policy without local charging | Integration and behavior / E-S3; Executed proof |
| Exact theta base, merged-suite repair, combined conflicts and retained primary-error assertion | Integration and behavior; Executed proof |
| Original-builder, campaign-log, cache/seed and integrity limits carry forward | Limits and operating requirements |
| Offline proof only; further theta changes and non-author/live review remain caller concerns | Executed proof; Limits and operating requirements |

14 findings, 14 placed: seven retained round-1 findings in their original
sections, and seven round-2 findings in the table above.

DONE eta round2 head=185a318a7fa5a46485a375ee1cb26244c2254403 base=be7468df12d4c0422d54f8ccd881d653cd92bdd4 tests=513/515 negctl=pass fixed=E-B1,E-S1,E-S2,E-S3
