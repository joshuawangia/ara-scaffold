# Eta shared frozen T — working record

Base: ba3a004; branch feat/shared-frozen-t; checkout /home/dev/ara-work/eta.
Brief: /home/dev/ara-work/briefs/eta-shared-frozen-t.md. Direct native execution;
no delegation, paid provider calls, push, or pilot working-tree/run writes.

## Design and causal account

At the base, CLI run always calls prepare -> prepare_commitments -> build_t ->
commitments_frozen -> propose_targets. Extraction imports re-emit original events
and consume the builder budget. Cache keys omit candidate identity. Existing
native mock smoke/replay and extraction rich tests establish those behaviors.

The implementation adds verified --from-frozen intake to that entrypoint, splits
prepare_targets from construction, and nests verified original chain rows through
freeze in a frozen_history_import event. Local consumers see only candidate
lifecycle events; original labels remain inside the inherited snapshot. Methodology
summarizes inherited/local totals; campaign_totals deduplicates canonical MODEL
receipts across builders, extraction logs, candidates and repeated inputs.

A fresh UUID cache identity and engine seed go into candidate effective config
and model cache keys. Prompt inputs do not include inherited search/writer history.
Source verification is read-only and precedes provider creation. Construction
receipts include schema prompts, original cache origins, extraction import digest
and reconstructed literature, rich plan/batch hashes and merge/T agreement.

## Decisions and limits

Legacy pilot freeze compatibility uses canonical embedded T and logged schemas,
plus a pinned baseline type/bank/schema manifest. New freezes record explicit hash
and manifest. The source must have a completed native lifecycle (including a successful later
select after awaiting_selection);
candidates must reference the original builder. Both caps are explicit CLI inputs.
Construction model/config remains fixed; search/writer controls and caps may differ.
The seed controls engine tie-breaking, not provider sampling. Cache isolation and
stateless prompts are proven; statistical independence and differing answers are
not promised. Hash chains are integrity checks, not signatures against full rewrite.

## Verification in progress

Test-first native candidate proof failed because --from-frozen and cap flags were
unrecognized (expected baseline failure). Focused green receipts before final
polish: 8 CLI/native tests; 17 candidate/refusal/accounting tests; 4 rich provenance
tests. The source snapshots stayed byte-identical in candidate tests. The original
blanket no-cache-hit assertion was corrected: within-candidate replay is permitted;
cross-candidate cache keys must be disjoint. Full required suite and mutation
controls are next, sequentially. Final revision and counts pending.

## Handoff gaps

No live pilot or paid call tested; only offline placeholders. Non-author review is
owned by the caller and remains pending. No release or shipping verdict is claimed.


## Final verification checkpoint

Initial full suite was intentionally interrupted after 161 passing tests / 218.14s
to fix legacy completion through later select. This is not a green full-suite claim.
The affected lifecycle/refusal/rich-provenance rerun passed 18 tests / 35.98s.
All 181 mutation locations were checked for an exact unique production match.
Final full pytest followed by the integration negative controls is running
sequentially on the stable tree. No source edits during that run.

Full run found one exporter compatibility failure: minimal historical run_started
records have no config. Candidate identity export now checks for that optional
field. Receipt: 435 passed, 2 intentional live skips, 1 failure / 283.63s. The
existing log-only regeneration test is the regression proof; targeted rerun and
final sequential verification follow. No negative controls started after failure.


## Findings placement for handoff

1. Candidate operation requires the original completed builder, compatible
   construction config, full source receipts/artifacts, and explicit local caps —
   placed in **Decisions and limits**, and README's shared-frozen usage section.
2. Legacy pilot support is verified offline against embedded T/logged schemas and
   a pinned baseline; the live pilot itself is unexamined — placed in **Decisions
   and limits** and **Handoff gaps**.
3. Independence means disjoint runtime response cache identities, fresh engine
   seeds and stateless requests; within-run replay is retained and statistical
   independence/provider sampling control is not claimed — placed in **Design and
   causal account** and **Decisions and limits**.
4. Inherited history is nested and charged separately; campaign consumers must
   use receipt deduplication across their explicit log set — placed in **Design
   and causal account**.
5. Log hashes/checkpoints detect integrity changes but cannot authenticate a fully
   rewritten history — placed in **Decisions and limits**.
6. Offline proof does not replace paid/live validation or the caller's non-author
   review; no push or release verdict is included — placed in **Handoff gaps**.

6 findings, 6 placed.

Execution route: native, inline Codex; no external implementation binding/model
request, run controller, delegation or fallback. Task brief owns the finishing
contract: local commit and report, standalone shipping skipped. There were no
pre-existing changes in this new worktree. Verification still pending final suite
and full negative-control results; do not treat this working record as DONE.


## Executed final-suite receipt

`uv run pytest`: 436 passed, 2 intentional live-provider skips, 0 failures in
282.86 seconds, CPython 3.15.0. Log: /home/dev/ara-work/reports/eta-pytest.txt.
The exporter repair's targeted rerun passed 17 tests in 8.52 seconds.
The required integration mutation command started only after full pytest exited
zero; 75 controls have completed with red=1/restored=0. The corpus-capacity
control is running. Final mutation verdict, restoration check, commit and DONE
line remain pending. Current committed revision is still ba3a004 plus the 12
owned uncommitted paths in eta-pre-controls-files.json.


## Required-control repair

The first full mutation run stopped at paper_count_finite: red=0/restored=0
after 159 detected defects. This existing control's broad pytest match='paper'
accepted a later JSON nonfinite-value error: CPython 3.15 adds the dictionary
key in exception notes, which pytest includes when matching. A local plain-json
probe confirmed the exact note. Strengthened the existing invalid-paper-limit
test to require the primary admission error message, not a secondary storage
error. No extraction production code changed. All 32 owning tests passed in
4.95s; targeted finite-count and finite-cost mutations now give red=1/restored=0.
The full shared-feature mutation subset is being completed before final full
pytest then all integration controls are run again sequentially.

7. Required verification includes a strengthened pre-existing extraction-limit
   test, outside the feature's production path; review its error assertion change
   alongside the new feature — placed in **Required-control repair**.

Updated handoff inventory: 7 findings, 7 placed. Earlier counts and incomplete
verification checkpoints above are historical working notes, not final verdicts.


## Manifest-presence correction

Final inspection found that a recorded empty/null contract selected the legacy
manifest via truthiness. Two new native refusal tests failed before the fix.
Legacy compatibility now applies only when the field is absent; recorded empty
or null manifests refuse before provider creation. The new empty-manifest
production mutation is included in the full runner (182 controls total). This
is part of finding 2's legacy compatibility boundary. Final full-suite counts
will include these two additional cases. The prior in-progress full run was
interrupted to apply this correction before the final verification checkpoint.


## Final tree verification (latest checkpoint)

Full `uv run pytest` is green on the final implementation and all 13 owned
paths: 438 passed, 2 intentional live-provider skips, 0 failures / 300.44s.
The additional manifest-presence control gave red=1/restored=0 before this run.
All 182 integration controls now run sequentially after that full-suite pass.
No source edits are planned; next steps are the final mutation verdict, exact
restoration check against eta-pre-controls-files.json, local commit, and report.

Final revision: ec8e1870926c5fdf226abfab11e5426ac3aee5ad. All 182 controls passed and all files restored. Commit matches verified content; worktree clean. Final deliverable is eta-shared-frozen-t.md.

## Round 2 in progress
- Brief: eta-round-2.md; review iota-review.md E-B1/E-S1/E-S2/E-S3.
- Rebased ec8e187 onto theta b063433d56f83f058d4941c8c8a30b43ec0cf355; replayed eta commit is 9db2ce5. Five conflicts resolved preserving theta/eta docs, CLI, controls and eta primary-error assertion.
- Native provenance verifier/current-outcome selector reused. Response schema/render template moved to shared response_contracts.py, version=2; exact ba3a004 extraction template+schema digest is historical compatibility only.
- Construction decoder, correction merge, evidence normalization shared by live execution and audit. Frozen verification reconstructs accepted commitments/symbols/alignments; correction candidate must match original rejected MODEL response.
- Config compares effective relevant stage settings/defaults; writer-only map entries allowed. Extraction disclosure includes nested history without flattening local budget events.
- Red: eta-round2-red.txt, 6 failed/21 passed (original merged three, response test masked by same prompt refusal, writer and effective-default regressions).
- Green targeted: eta-round2-targeted.txt 43 passed; native matrix eta-round2-native.txt 6 passed; rich/legacy suite eta-round2-rich.txt 52 passed.
- Added partial coverage disclosure test after those runs; pending full verification.
- Currently running targeted controls, session 48451, eta-round2-controls-targeted.txt. DO NOT edit source or run tests during controls. 209 anchors verified beforehand. Full pytest then full controls still required; no paid calls/push.
- No final-theta instruction received yet; base remains b063433. Re-rebase only when instructed by operator/brain.
- Full stable-tree verification: eta-round2-pytest.txt = 498 passed, 2 skipped / 500, 334.87s. No paid/provider tests enabled.
- Targeted controls: 35/35 red,35/35 restored green; eta-round2-controls-targeted-results.json retained.
- Full 209 controls now running sequentially after full pytest, session 97166, eta-round2-negctl.txt; source snapshot eta-round2-verified-files.json matches full-suite input. Do not edit production files during this run. At last check 75/209 completed, all red/restored green.
- Still needs final control completion/restoration check, local commit on feat/shared-frozen-t (owned paths only), Round2 report append and result JSON. Final requested line includes exact base b063433d56f83f058d4941c8c8a30b43ec0cf355 unless instructed otherwise. No final-theta rebase instruction yet.
- Operator instructed rebase onto theta be7468d (T-B1/T-S1 fixed) during initial full controls. Waited for completion/restoration: 209/209 red/restored green. Original base evidence remains in eta-round2-pytest.txt and eta-round2-negctl*.json/txt.
- Committed local fixes as 5acc7f3, then rebased both eta commits onto be7468df12d4c0422d54f8ccd881d653cd92bdd4. Docs/control-list conflicts preserved both additions. Current clean HEAD is 185a318 (full SHA obtainable via git); earlier eta replay is 5f46ea4.
- Rebased targeted tests: 33 passed in 41.35s (eta-round2-rebased-targeted.txt). 216 mutation anchors verified.
- Final full pytest running as session 28551; log eta-round2-final-pytest.txt, 515 collected, currently long capacity test. Snapshot eta-round2-final-files.json. After full pytest must run full controls sequentially again, then verify committed bytes/restoration and append Round 2 report + final result JSON. No paid calls/no push. Final DONE base must be be7468df12d4c0422d54f8ccd881d653cd92bdd4.
- Final pytest passed 513/515 (2 live skips), 361.91s. Final full controls now running session 37803, eta-round2-final-negctl.txt, 216 cases. Source snapshot remains unchanged. Prepared eta-round2-report-draft.md with pending control/restoration placeholders; replace only after actual success, append to main report, add exact final DONE line. Head 185a318a7fa5a46485a375ee1cb26244c2254403, base be7468df12d4c0422d54f8ccd881d653cd92bdd4. No more implementation changes are currently required.

- FINAL: DONE eta round2 head=185a318a7fa5a46485a375ee1cb26244c2254403 base=be7468df12d4c0422d54f8ccd881d653cd92bdd4 tests=513/515 negctl=pass fixed=E-B1,E-S1,E-S2,E-S3
- Final full controls 216/216 detected and restored; all 132 tracked file fingerprints match, worktree clean, diff-check passed. Main report Round 2 appended; full control traces copied to eta-round2-final-controls. Non-author review belongs to caller; no unresolved implementation work. No paid calls/push.
