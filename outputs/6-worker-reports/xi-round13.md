# Xi Round 13

Implemented on `feat/run-report`, based on main `6511ff6`. Final commit: `9f07ba0a50df2802d56302134f85e4a896a23dd6`;
receipt: `runs/xi-round13/completion.json`. No live or paid calls, workers, or push.

Full offline pytest passed **1,074 tests, 4 skipped / 1,078**, in 836.09 seconds.
After pytest exited, all **463 controls** failed under mutation and passed after
restoration. All **200 pinned files** matched after both gates. The subsequent
DECISIONS edit records these results; executable inputs were not changed.

## Behavior and finding disposition

1. Target proposal receives an own-thesis policy, conditionals, shared signatures
   and the frozen catalogue. Canonical T copies, direct universal instances and
   explicit reporting language are excluded. Vocabulary and triviality share one
   correction; still-trivial candidates are removed and disclosed. Originality and
   actual multiple-source support remain model judgments, not mechanically proven.
2. Reports, route text and selection distinguish CLOSED-trivial and CLOSED-derived.
   Default/interactive selection offers derived routes; alternatives remain visible
   and require an explicit route argument. Historical graph serialization stays
   unchanged. One licensed inference does not prove novelty or independent support
   from two papers. The native smoke fixture now proves placeholder derivations.
3. `fork-from-freeze` verifies the full source chain and required anchor, a single
   freeze, bank identity, and freeze artifacts. It atomically installs the exact
   prefix and artifacts in a separate empty directory, then continues native target
   proposal and search. The fork has its own cache. Prefix usage is counted once
   and classified as imported. Source preservation is tested and demonstrated.
4. Pilot 3's previous live Codex preflight correctly refused under current code.
   A real rerun requires a current successful live preflight for its resolved
   profile. That prerequisite was not bypassed or executed in this offline task.
5. The real-data fake demo copied 6,813 prefix records, made two fake target calls,
   rejected ten deliberately trivial targets, and accepted none. Four source-file
   hashes stayed unchanged; network and paid calls were zero. This proves the fork
   and rejection on real frozen data, not useful thesis generation or real-corpus
   closure. The fake model/profile and byte/4 test counter are recorded explicitly;
   they are not provider or tokenizer measurements.

**5 findings, 5 placed**, all in Behavior and finding disposition.

## Evidence and reproduction

From `/home/dev/ara-work/xi`:

- `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked pytest -q -x`
- `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked python tests/integration/negative_controls.py`
- `uv run --offline --locked python runs/xi-round13/fork-demo.py` (choose a fresh
  output directory; the preserved successful output must not be overwritten).

Evidence in `runs/xi-round13/`: `pytest-complete.txt`, `controls.txt`, `controls/`
(all individual red/restored transcripts), `pre-gates-hashes.json`,
`restoration.json`, `fork-demo.py`, `fork-demo.json`, `fork-demo-final.txt`, and
`real-fork-final/`. Fourteen new regressions pass; new target/fork cases were
observed red before implementation. The canonical-instance normalization fix
was verified separately after the exact-copy real-data demo and is covered by
both final gates. No independent review receipt is claimed for Round 13.

An earlier full run was stopped when the disk filled. Only three failed demo
copies created by this task were removed; refusal transcripts, the successful
demo and original pilot remain. `cleanup.json` records those removals. Fifteen
recovery tests passed before the successful full-suite rerun. No product source
change was needed for disk recovery. Earlier interrupted runs are not pass receipts.
