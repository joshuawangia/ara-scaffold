# Upsilon2 — non-author review and integration

**Recommend merge for Sigma and Xi; zero blocking defects found.** The resolved scratch merge passed 1,060 tests (four opt-in skips) and all 450 production-wire controls. Fresh structured T closes a native placeholder route and replays offline; the flat negative remains open. The offline Codex plan completed on the real literature. A real rerun still needs a fresh live schema preflight.

## Scope and integration

Reviewed Sigma `2452ecbabdc02ead31dd86bb4e23e90bc17ded5d` against `c32d429`, and Xi `119488f47d9933d18636daadd9283c9c8e87957d` against `4c1c76f`. Both author checkouts were clean and were left unchanged. I performed the review myself, without delegation, paid calls, push, or live-provider execution.

Scratch clone: `/home/dev/ara-work/upsilon2-integration`. Started at requested main/base `4c1c76f`, fast-forwarded Xi, then merged Sigma. Result: `6511ff6cb2bb5d88c5abedc1f20b715a03324d0f`, with the two requested review heads as parents.

**F1 — Integration requires three explicit conflict resolutions (nonblocking once resolved).**

| Conflict | Resolution applied only in scratch |
| --- | --- |
| `DECISIONS.md` | Preserve Xi's Round 10/12 and Sigma's S8 documentation. |
| `ara/runtime/frozen_catalogue.py` | Keep the shared contract and Sigma's additional dictionary type guard. |
| `tests/integration/negative_controls.py` | Preserve both control lists, including all 12 Xi and all four Sigma additions. |

The merge is therefore reported as `conflicts`, even after successful resolution. No production behavior was changed beyond those branch contents. An initial mechanical resolution damaged the documentation/control-list text; AST validation caught it, and a fresh three-way merge with line-wise marker removal corrected it before the control runner. The runtime and pytest files were unchanged by that correction.

## Requirement review

| Requirement | Assessment and code boundary |
| --- | --- |
| Sigma inference conditionals | `construction_structure.py:31` identifies selected inference evidence, requires conditionals, and checks exact selected endpoint formulas as conjuncts. Production construction obtains model-authored formulas and citations from the fixed rich-source inventory. |
| Shared vocabulary and model judgment | `construction.py:508` validates declarations, signatures, reuse alignment reasons and evidence; definitions and actual bindings remain logged. The prompt requires source-supported relational encoding. Code does not invent semantic equivalence. |
| Structure gate and one correction | `construction.py:551` records initial metrics, makes one complete replacement request with item-specific issues, then records the outcome. The attempt is distinct from schema-validation patches and still uses transport, stage routing, budget, schema, provenance and capacity checks. |
| Flatness | A still-atomic inference batch can be retained only with the failed gate and `flat_after_one_correction` disclosure. A nonflat endpoint violation refuses the batch. Methodology exports the gates/outcomes; no padding or forced invented structure. |
| Frozen catalogue | `orchestration.py:95` writes `frozen-t.json` before the single freeze. `frozen_catalogue.py` binds exact T, exact signatures, definitions/evidence and canonical SHA-256. Legacy `commitments.json` remains unchanged. |
| Xi goal binding | `licensing.py:57` binds `current_goal` only for exact text, retains canonical equality, and leaves historical unreferenced proposals on their previous interpretation path. Different text cannot borrow the goal formula. |
| Catalogue-aware search | Targets, catalogue-aware standalone formalization and joint slots receive symbols plus catalogue/T hashes in request/cache inputs. Present corrupt metadata refuses; missing metadata is explicitly marked `unavailable_legacy`. |
| Disconnected preflight | `calls.py:929` records exact-signature overlap and retries target proposal once with the previous targets and catalogue feedback. A second disconnected result remains disclosed; it is not silently declared reachable or replaced by fiat. |
| Bounded alternatives/correction | Xi takes the brief's **batch alternative**: one batch of up to three distinct candidates per expanded leaf. It does not add a new engine-rejection correction loop. Runtime validation retries separately carry specific rejection feedback and remain bounded by configuration. |
| Joint slots | `search_alignment.py:46` and `calls.py:970` co-formalize the sequent with goal, bank, exact T bindings and up to eight candidate metavariable substitutions. Frozen formula equality and known symbol signatures are checked. Solver entailment, bank shape, scope checks and terminus equality remain independent. |
| T references | `slot_bindings` rejects unknown IDs and text differing from the attributed frozen text. Joint formalization cannot change a bound formula. Runtime correction tests exercise unknown ID, wrong text and changed goal text. |
| Native closure and replay | The independent integrated probe below exercises constructed T, single freeze, target proposal, concurrent paired search, route publication and offline resume. It closes through the conditionals rather than taking the already-frozen final conclusion as a leaf. |

No confirmed merge-blocking source defect has been retained. This is a single non-author review using the code-review skill's correctness and requirement checks; its delegation/external-peer workflow was overridden by the explicit brief. No independent additional reviewer is claimed.

## Independent end-to-end proof

Reproduce from the scratch root:

```sh
uv run --offline --locked python /home/dev/ara-work/reports/upsilon2-evidence/e2e.py
```

The script expects a fresh `runs/upsilon2-e2e` directory; preserve the existing evidence and choose another output directory for a rerun.

A fake provider supplies a rich placeholder graph through native extraction and Sigma construction. T freezes eight commitments, including two conditionals with shared predicates/constants. Xi proposes `F(a)` and searches both polarities through `prepare` and `search_all` with concurrency 2. Its positive route is **CLOSED**, with seven nodes: three bank-licensed inferences and four exact T leaves (`p`, `q`, `i`, `j`). Neither the intermediate nor final conclusion is used as a frozen leaf. Each joint formalization receives the verified catalogue. Offline resume restores both jobs and rechecks the licenses with no provider.

The complementary `flat-e2e.py` probe uses the same native path with flat formulas. It gets exactly one structure correction, retains explicit flatness, and produces **OPEN/OPEN**, with no admitted inference. Thus the identity fix does not manufacture closure from a flat encoding.

Receipts: [e2e.json](upsilon2-evidence/e2e.json), [flat-e2e.json](upsilon2-evidence/flat-e2e.json), reproducible scripts and transcripts in [upsilon2-evidence](upsilon2-evidence/). Native immutable artifacts and search journals remain in the scratch clone's `runs/upsilon2-e2e/run` and `runs/upsilon2-flat-e2e/run`.

## Offline Codex plan and rerun prerequisites

The planner uses the **resolved config, topic, audience and exact literature recorded by codex-pilot-2**, retaining `provider=codex_cli`, requested model `gpt-6-luna`. Literature SHA-256: `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`. It calls native `plan_construction` with `counter=local`, zero generation budgets and a count-only provider; socket connections are disabled. No Codex process or paid provider is created.

Executed result: plan `rich-working-t-v10`; **31 windows, zero uncounted windows, zero generation calls**. Local maximum request estimate: 66,389 tokens; with output/catalogue reservations: 190,389 against context bound 200,000. Each window starts with six commitment slots and cap 12; projected total 186. The projected count is allocation arithmetic, not a prediction of selected source items, inferred formulas, actual provider token counts or successful closure. The local byte/4 counter explains why its partition need not equal the earlier pilot's provider-specific partition. Receipt and script: [plan.json](upsilon2-evidence/plan.json), [plan.py](upsilon2-evidence/plan.py).

**F2 — Refresh the Codex schema preflight before a real rerun (operational prerequisite, not a source defect).** I executed `require_codex_preflight` offline using that pilot's recorded configuration against the merged tree. It refused with `Codex schema preflight is missing, incomplete or stale`. The expected manifest now includes `formalise_slots` and changed construction/proposal schemas. Run a fresh live preflight for the actual resolved rerun profile, then point it at that successful log; do not reuse the old receipt. Live preflight was outside this no-paid review. See [preflight.json](upsilon2-evidence/preflight.json).

**F3 — Keep the proof claim bounded (coverage limitation).** These results establish that the native construction/search interfaces can now close a structured placeholder route, and that flattening does not get false closure. They do not establish faithful real-literature formalization, useful relevance selection, live Codex schema acceptance, real-model performance, or any real-corpus closed route. The structure gate measures syntax and exact formula connections; symbol reuse can include shared constants and is not semantic evidence. A second disconnected target remains searchable with a disclosed warning. Inspect the new run's structure/flatness, catalogue and target-preflight receipts before describing a real pilot as successful. The old frozen 166-atom T remains unchanged; this proof concerns fresh construction.

## Verification and placement

Full pytest: **1,060 passed, 4 skipped / 1,064**, exit 0, 889.92 seconds. The skips are two opt-in paid-provider tests and two opt-in local OCR/VL-weight tests. Command: `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked pytest -q`. Full control runner: **450/450 expected mutation failures, 450/450 restored passes**, exit 0, started only after pytest exited. Command: `ARA_LIVE_TEST=0 UV_OFFLINE=1 uv run --offline --locked python tests/integration/negative_controls.py`.

All **195 tracked-file hashes** match the pre-control manifest, the scratch working tree is clean, and both author checkouts remain clean at the requested heads. No source edits followed verification. I inspected the failures from all 16 new controls: goal re-formalization and independent slot interpretation lose closure; reference, slot, endpoint and catalogue guards cease refusing their invalid inputs when disabled; missing catalogue/metavariable/batch context fails the fake-provider/request assertions; removing reference trace data breaks offline replay. The latter request assertions surface through expected runtime error wrapping, not through a live provider. These are contract/behavior controls, not evidence of model quality.

Full transcripts: [pytest.txt](upsilon2-evidence/pytest.txt), [controls.txt](upsilon2-evidence/controls.txt). All 900 individual red/restored transcripts and the result registry are archived under [controls](upsilon2-evidence/controls/). New-control failure excerpts: [new-control-failures.json](upsilon2-evidence/new-control-failures.json). Consolidated exact-head, hash, branch, test, end-to-end and planning receipt: [final-verification.json](upsilon2-evidence/final-verification.json).

3 findings, 3 placed: F1 in Scope and integration; F2 in Offline Codex plan and rerun prerequisites; F3 in that same section's coverage limitation. No retained blocking code defect; both branches are recommended for merge with the recorded conflict resolutions. The live preflight and real-corpus semantic/closure limits remain explicit prerequisites and limits, not failed source gates.

DONE upsilon2 sigma=merge xi=merge blocking=0 integration=conflicts:DECISIONS.md,ara/runtime/frozen_catalogue.py,tests/integration/negative_controls.py merged_tests=1060/1064 e2e_closure=yes
