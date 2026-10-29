# Xi Round 24 — preserve all exact leaf evidence

Base 2ed9e21796bf55e1160bd6a22e1f0f459bb67436, branch feat/run-report,
checkout /home/dev/ara-work/xi. Offline only; no paid calls, push or delegation.

## R23-F1 repair

Every exact formula match is retained independently of bridge choice, fallback
seeds and shrink level, including k=0. Exact commitments lead the request:
verified endorsed copies first, then other copies, with ID ordering within each
group. Reported/attacked source roles remain unchanged; missing legacy roles are
not interpreted as endorsement. Both the request's search_slice and every
search_context_slice receipt list exact_match_commitment_ids.

The native regression reproduces kappa4's setup: earlier-ID restricted P,
later-ID endorsed P, and two endorsed Q commitments supplying the available
cross-paper bridge. Its fake mapper selects only a visible endorsed exact match;
it does not invent cuts to compensate for missing evidence.

All four combinations (reported/attacked, normal sizing/forced k=0) failed with
OPEN before the fix. Afterward each native engine search is CLOSED through
z-endorsed. Both exact copies remain visible, endorsed first, with their original
roles. Under the controlled counter, every 8,4,2,1,0 receipt retains both IDs.
This proves leaf closure, not a new CLOSED-derived route or novel synthesis.

The two new production-wire controls discard later exact matches or remove
stance priority. The regression must detect both. Canned map/cut fixtures were
regenerated offline for the added receipt field and commitment ordering.

## Verification

Initial red: four failures, eleven deselected, in 3.79 seconds.
Focused context suite after the fix: 15/15 passed in 11.37 seconds.
Final affected search/CLI suite: **90/90 passed**, no skips, in 114.23 seconds.
Eight files cover context slicing, stance, search alignment/guidance, cross-paper
policy, model-call boundaries, CLI and native CLI replay. The exact command is in
runs/xi-round24/verification.json; transcript: pytest.txt.
The existing integration runner passed **31/31 selected controls** covering
context, stance and cross-paper behavior, including both new controls. Every mutation
failed as expected and every restored test passed, in 197.44 seconds. All 231
pinned source hashes match after tests and controls. These are
scoped checks; this round does not claim a fresh full-suite or full-control run.

## Limits and finding placement

Exact evidence remains part of the counted request; the set may exceed the
configured context limit. In that case the existing disclosed job-local refusal
applies. Shrinking cannot discard an exact match merely to obtain admission.
No context limit, frozen codec, stance permission, engine license or novelty
policy changed. These offline tests do not establish paid-model accuracy or live
pilot completion.

2 findings, 2 placed: lost endorsed leaf evidence and its repair in R23-F1 repair;
indispensable-context and offline verification boundaries in Limits and finding
placement. No unrelated review findings are claimed fixed.

## Final revision and receipts

Committed locally as **9b9999730c32b4dd0f06ef80a075920633d1acc9**. Working tree clean; all 231 source files match
the exact tested snapshot. git diff --check passed. No push or paid calls.

Evidence directory: /home/dev/ara-work/xi/runs/xi-round24/. It contains red.txt,
focused.txt, pytest.txt, gates.txt, verification.json, control-manifest.json,
control-results.json, every selected control's red/restored transcript under
controls/, source-before.json, source-after-controls.json and
commit-verification.json.

**2 findings, 2 placed**, as inventoried above.

DONE xi round24 head=9b9999730c32b4dd0f06ef80a075920633d1acc9 tests=90/90 negctl=pass fixed=kappa4-R23-F1
