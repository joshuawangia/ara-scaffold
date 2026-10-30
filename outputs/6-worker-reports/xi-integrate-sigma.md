# Xi integration of Sigma round 11

Local merge `0a31afb92c319bd0ae38f71e51b3233050d32758` in
`/home/dev/ara-work/xi`, branch `feat/run-report`, from `5557e9a` plus
Sigma `bdeaeb8444113e5c0d6d62e5ac1b494a8f0b5fee`. No push or paid calls. Final revision and gates are recorded below.

## Integrated behavior

Both branches' policies survive the merge: construction aligns symbols before
freeze and persists replayable v2 provenance; Xi retains per-paper novelty,
forward leads, gap targets, strict CQ answers and conflict feedback. Alignment
bridges are disclosed global premises, never source CQ evidence or paper owners.
Only endorsed source commitments enter per-paper closure or supply source support.
The matching requirement still needs two distinct support formulas assignable to
two papers. The new forward path admits alignment premises and reports their IDs
separately; semantic conflict pairing excludes their non-source metadata.

A placeholder regression uses P from a, Q→R from b, and a model-alignment P→Q
bridge. The native forward pass proposes R, with a and b as its two papers and the
bridge disclosed separately. Q from one endorsed source plus the bridge does not
qualify. A forged bridge source_id still cannot enter endorsed-paper closure.

The additive conflicts in DECISIONS, source map, calls, route policy, prompts and
controls retain both changes. Codex preflight now requires all 18 cases. The
finite canned responses were rekeyed for combined request shapes without changing
any of their 41 response payloads. Sigma's CQ test now supplies actual sign slots
so Xi's instantiated-question retrieval reaches the intended rejection check.

## Offline real-T census and limits

`tools/offline_forward_synthesis.py --source /home/dev/ara-scaffold/runs/codex-fork-5
--out runs/xi-integrate-sigma/fork5-aligned-final --fake-alignments
runs/xi-integrate-sigma/fake-alignments.json` uses an explicitly fake provider
through native prepare/freeze, persisted catalogue and provenance validation.
Network connections are refused. Original source artifact hashes and byte copies
remain unchanged. Generous replay caps and mock accounting are disclosed; this
is not proof of production budget admission.

The real freeze has 169 commitments and 22 endorsed papers. The **final v2**
retrieval selects **150 pairs**, covering all22 papers, from10,490 signature-compatible
cross-paper pairs and5,036 pairs with shared lexical terms.168 score at least0.10.
One deterministic diversity replacement adds the missing paper; one selected pair
is below the preferred threshold. The review's two excluded leads are now ranked
132 and133 within the150 selected pairs. Exact counts/settings/rows are in
`runs/xi-integrate-sigma/real-retrieval.json` and the persisted alignment receipt.

Two fake same_content judgments exercise the overlapping assessment-sensitive
modal descriptions and the concretely/schematically stated update-order asymmetry.
Native freeze accepts them, reducing151 symbols to149; the other148 judgments are
fake unrelated responses. Full definitions are not identical: these are disclosed
test assumptions, not established semantic equivalences or a claim that the
complete theories say the same thing.

Final result: **0 qualifying forward candidates**,500 licensed consequences,
depth2, cap reached. The prior unaligned census was also0 at the same bound.
Persistence, retrieval and forward input wiring are exercised; improved real
synthesis, exhaustive absence, faithful formalization and useful philosophical
novelty remain unproved. The positive placeholder bridge regression is separate
from this real-T zero result.

Final command uses `--out runs/xi-integrate-sigma/fork5-v2-aligned` and
`--fake-alignments runs/xi-integrate-sigma/fake-alignments-v2.json`. Receipts:
`fork5-v2-aligned/summary.json`, `aligned/events.jsonl`, and `offline-v2.txt`.
The earlier23-pair run in `fork5-aligned-final` predates the review correction and
is superseded. The earlier `offline.txt` records an unpriced mock identity failure;
the corrected harness uses the existing MockProvider accounting identity with an
explicit fake-run receipt. No real provider was called.

## Kappa4 S11 blockers

- **S11-F1 fixed:** native v2 freeze→discovery regression dispatches only the three
  actual source/source pairs, excluding every bridge. No attributed_to fallback
  or invented paper identity is added.
- **S11-F2 fixed:** configurable preferred score0.10, bounded top-N shared-term
  backfill, deterministic paper diversity, logged and replay-validated retrieval
  statistics. Threshold and diversity settings bind construction plan v14 and
  alignment policy v2. Legacy policy-v1 receipts replay their original hard0.15
  cutoff. Broader retrieval never invents same_content or entailment judgments.
- **S11-F3 fixed:** the actual rendered judge request explicitly contains `topic=''`,
  even when the run topic is nonempty. Original definitions, source roles and
  freeze hashes remain available. The neutral-topic regression failed before the
  fix and passed afterward.

## External headline gap file

The prior Round27 follow-through is implemented as `gap_file` configuration and
`--gap-file` on both `run` and `fork-from-freeze`. `external-gaps-v1` records are
AI-found hypotheses; priority0 is first, followed by other external and native
gaps. Exact file content, SHA-256, current freeze hashes and ordered gap IDs are
logged. Evidence, currency verdict, search scope and qualified claim framing
persist with the target/route and writer/auditor outline. Every support group must
bind endorsed commitments from its corresponding paper; external literature
citations are advisory evidence and do not become frozen premises.

Ready input: `/home/dev/ara-work/reports/eps2-L3-gap.json`. It contains eps2's L3,
its full-text evidence and partial currency verdict, rival explanation, access and
indexing limitations, and five bound endorsed commitments from Beddor–Goldstein
and MacFarlane2014. Its exact framing is: **“not found within the stated 2018–2026
search scope; partially anticipated by Mighty Knowledge and Dinges 2021.”**
This remains a research lead, not a certified open problem or an already derived
link. Native loading against the real freeze is recorded at
`runs/xi-integrate-sigma/external-gap/`. The native placeholder CLI fork regression
proves it seeds proposal first without modifying the source freeze. Real research
content stays outside committed files. `gap_file=yes`.

## Verification

Full pytest passed on the committed merge: **1359 passed,4 skipped /1363 collected**,
exit0 in1994.28s. All 252 pinned repository paths matched afterward. The complete
650-control runner passed: every mutation caused an actual test failure, every
restoration passed, and all 252 committed paths matched after restoration. The
checkout is clean. Both gates exited 0; control runtime was 4,987.05 seconds.
Final receipt: `runs/xi-integrate-sigma/delivery.json`; full transcripts and
restored hashes are retained beside it. The final affected
suite136 passed, all4 retrieval/isolation tests passed, and all52 selected
mutation/restoration pairs passed with actual failing tests and green restorations.
Initial affected suite123 passed; native external-gap suite8
passed; CLI/finite-fixture suite25 passed. Initial merge suite53 passed/one failure
was the malformed CQ fixture described above. Expected red regressions and failed
fixture rekey attempts remain under `runs/xi-integrate-sigma/`.

Author-side diff/caller inspection and inline simplification checks found no
additional refactor worth adding. No independent agent review was run: the
operator restriction on new worker/hidden-agent contexts applies. Code review:
skipped (ce-code-review unavailable). The attempted skill outcome is retained in
`review-attempt.json`; no independent-review receipt is claimed. No separate
lint/typecheck command is configured.

## Findings placement

1. Combined policy, bridge ownership and two-source requirements → Integrated behavior.
2. Native bridge-enabled placeholder candidate and one-source negative → Integrated behavior.
3. Real-T zero count, cap and fake-equivalence limitation → Offline real-T census and limits.
4. Source preservation and mock-accounting limits → Offline real-T census and limits.
5. L3 input, evidence, currency and required claim framing → External headline gap file.
6. Verification failures/repairs, gate status and unavailable independent review → Verification.
7. All three blocking review findings, calibrated retrieval and topic isolation → Kappa4 S11 blockers.

**7 findings, 7 placed.**

DONE xi integrate-sigma head=0a31afb92c319bd0ae38f71e51b3233050d32758 tests=1359/1363 negctl=pass forward_candidates_with_alignment=0 fixed=S11-F1,S11-F2,S11-F3 alignment_candidates_real=150
