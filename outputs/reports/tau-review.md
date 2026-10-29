# Tau — non-author review of bounded closure

Review subject: `/home/dev/ara-work/sigma`, branch `fix/bounded-closure`, HEAD `5009af1e053d11dac18405fe7402331134585fea`, base `1d832b24805536b46e6974ca97842cffe0458e3a`. No implementation edits, commits, delegation, push or paid generation. The requested control runner temporarily mutated production files and restored them; final verification confirms the checkout is clean at the reviewed HEAD.

**Verdict: merge. Blocking: 0. Should-fix: 0.** This is a bounded-construction review, not proof of model relevance, faithful formulas or a successful paid pilot.

## 1. Cut, attribution and disclosure

The native path is `prepare_commitments` → `construct` → model root selection → deterministic full closure/cut → fixed-inventory formalization → merge → sole freeze. `closure_budget.depth_cut` expands complete prerequisite depths and closes mandatory dependencies at every step. Incoming qualifications/distinctions and all included inference endpoints remain mandatory; an oversized mandatory root bundle contributes nothing rather than dropping its context. Code never invents evidence IDs or rewrites rich source records.

For every retained frontier item, `construction.evidence_text` prefixes `assumed_premise; support_omitted` and exact omitted direct support IDs, then preserves original attribution, attributed party, kind and text. Formalization replaces any model text/citation with that source-derived text and exact source citation. Thus an intermediate conclusion is not silently relabelled as the paper's original premise. The compact formalization request explicitly includes omitted-support edges, while complete cut/uncut inventories remain in receipts. `export.methodology` discloses each edge and the conditional-premise policy. Reuse preserves an earlier commitment unchanged, including its assumption marker; later support does not silently upgrade it.

Independent structural audit of all **5,296 real candidates** reproduced **3,593 full / 844 cut / 859 mandatory bundles too large**. Reversing item order produced identical selected IDs, omissions and depths. All retained qualifiers/endpoints, exact omitted dependency sets, attribution suffixes and marker presence passed; the source inventory remained unchanged. Evidence: `tau-evidence/cut-audit.py`, `cut-audit.json`. This census excludes exact per-window copy/request checks and semantic relevance. The native tests separately exercise frozen text, exact citation, ledger and methodology disclosure. No silent unmarked frontier commitment was found.

## 2. Budget arithmetic and downstream headroom

The actual plan has **48 windows**, not the earlier 46. With a 3,232-token wrapper, mean copied envelope rounded up to 204, and symbol/formula reservation `ceil(10471/45) = 233`, the arithmetic is:

- Working slots: `floor((80,000 - 3,232) / (204 + 233)) = 175`.
- Catalogue slots: `floor(38,400 / 233) = 164`.
- Window quota: `floor(min(175, 164) / 48) = 3`; total allocation **144 commitments**.
- Projected working envelope: `3,232 + 144 × 437 = 66,160`; projected catalogue: `144 × 233 = 33,552`.
- Batch input bound: `min(70,000, 200,000 - 64,000 - 48,000) = 70,000`.

| Quantity | Count | Bound |
|---|---:|---:|
| Largest planned initial window | 67,613 | 70,000 |
| Window + maximum formalization output + catalogue reservation | 179,613 | 200,000 |
| Projected working envelope | 66,160 | 80,000 after reserve / 100,000 configured |
| Projected catalogue | 33,552 | 38,400 after reserve / 48,000 configured |
| Per-window accepted working increment | 1,599 | 76,768 / 48, floored |
| Per-window accepted catalogue increment | 800 | 38,400 / 48 |

Actual accepted output is recounted against per-window and global guards. The working increments telescope to at most `3,232 + 48 × 1,599 = 79,984` before final merge recount; catalogue increments total at most 38,400. Copy checks include support markers. Exact formalization admission and final pre-freeze target admission remain active.

I additionally counted downstream wrappers with the free provider counter, the current full bank and placeholder goals. Target proposal's wrapper is 3,232; search-cut proposal's wrapper is 13,045. At the planned T size, these project to 66,160 and 75,973 input tokens, leaving **125,648 and 115,835 context tokens**, respectively, after their 8,192-token output allowances. Even at the accepted-increment ceiling, respective headroom is 111,824 and 102,011. Representative leaf mapping, CQ and repair envelopes also have headroom. Evidence: `tau-evidence/downstream/counts.json`, logged prompts, and `downstream-count.py`.

These downstream totals are projections, not exact requests using future generated goals/formulas. The 233 rate is an empirical reservation, not a bound on future model output. Large formulas, oversized symbols or corrections can still cause an explicit refusal; the implementation does not silently relax a guard. No deterministic budget blocker was found for this pilot configuration.

## 3. Root relevance remains model-owned

`selection_request` supplies every candidate's full closure size and conservative UTF-8 payload token bound, plus the window allocation. `construction_call(..., 'select_t_roots', ...)` obtains the relevance decision through the logged, validated model boundary. The validator checks aliases, complete omission-group coverage and nonempty reasons. Code expands/cuts the entire selected root bundle; it does not rank roots or choose substitutes. A model may choose zero roots or a bundle that cannot fit. Candidate payload byte bounds are explicitly distinguished from exact provider counts of complete requests.

## 4. Zero roots and omission accounting

Zero-root windows retain model relevance/omission reasons, emit closure/skipped receipts and make no formalization call. If roots were selected but mandatory context cannot fit, the empty reason explicitly identifies that budget condition. Every cut-away item is recorded in the closure receipt. Within its owning window, cut reasons replace preliminary selection omissions. Final accounting removes IDs accepted in any window and asserts unique omitted IDs plus accepted IDs equal the complete eligible inventory. Cross-window closure/overlap remains supported. An entirely empty T refuses before freeze.

The ledger covers eligible evidence; quarantined or unavailable source material remains governed by the existing extraction/grounding records. No missing eligible-item omission was found. Native zero-window, overlap, final inventory and single-freeze tests passed in the full suite.

## 5. Fresh real native plan

Reran the actual CLI from the reviewed checkout, using the same pilot configuration, topic, artifact and explicit `--audience ''`, stopping at the native `plan_only` boundary:

```sh
uv run ara plan-construction --profile pilot \
  --config /home/dev/ara-scaffold/runs/inputs/overnight-pilot-4-config.yaml \
  --topic 'epistemic modals' \
  --literature /home/dev/ara-scaffold/runs/overnight2-extraction/literature.extracted.txt \
  --audience '' --token-counter provider \
  --run-dir /home/dev/ara-work/reports/tau-evidence/native-plan
```

The result is **byte-for-byte identical** to `/home/dev/ara-work/reports/sigma-evidence/construction-plan.json`:

- Plan SHA-256: `4410649ff537d1b09e582dae78cb9ca1b91da0ca8b055dcdbdd9f71a53e404ef`.
- Literature SHA-256: `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`.
- **340** verified event-chain/anchor records; **zero** MODEL events, dispatch starts or recorded cost.
- Exact agreement on windows, sources/content hashes, allocation, token counts and limits.

`CountingProvider.complete` refuses generation; planning also sets spend/token caps to zero and returns before selection. This is no-generation planning with a free **networked** token-count endpoint, not a network-free tokenizer claim. Credential material was sourced into the process environment only. Evidence: `tau-evidence/native-plan/`, `real-plan-verification.json`, `verify-plan.py`.

## 6. Tests, negative controls and limits

Full `uv run pytest -q` completed first: **624 passed, 2 skipped, 626 total, 293.77 seconds**, exit 0. The skips are opt-in live tests. Planning and additional source probes also completed before starting `uv run python tests/integration/negative_controls.py`; no suite or probe runs alongside its mutations. Full runner exited 0: **280/280 mutations failed their targeted tests; 280/280 restorations passed**. Results and all 560 individual outputs are archived under `tau-evidence/controls/`. Final `git status --porcelain` is empty, HEAD remains `5009af1e053d11dac18405fe7402331134585fea`, and `git diff --check` passes. Evidence: `tau-evidence/pytest.txt`, `controls-console.txt`, `final-verification.json` and `verify-controls.py`.

Read all ten new mutations, their target assertions, and the fresh failure/restoration outputs. The failures occurred at the intended behavior checks (wrong allocation, dropped qualifier/omission/marker, missing disclosure or refusal, late request stop, or missing zero-window skip), rather than collection/import errors:

| Mutation | Behavior that must fail under mutation |
|---|---|
| `bounded_symbol_measurement` | Replacing the empirical 233 reservation with 128 |
| `bounded_global_window_division` | Giving each window the entire global slot count |
| `bounded_cut_qualification` | Dropping mandatory incoming qualifiers |
| `bounded_cut_omission_ids` | Erasing omitted-support IDs |
| `bounded_assumption_mark` | Removing the frozen-text assumption marker |
| `bounded_methodology` | Hiding omitted edges from methodology |
| `bounded_working_output` | Allowing a window to consume later working allocation |
| `bounded_symbol_output` | Allowing a window to consume later catalogue allocation |
| `bounded_exact_request_cut` | Bypassing exact formalization-request cutting |
| `bounded_zero_window` | Dispatching formalization for a zero-contribution window |

No real model relevance choice, formalization, freeze, search, route or essay was generated in this review. The structural census does not promise paper coverage or 144 accepted commitments. Formula fidelity and model compliance still require observing the authorized pilot. Optional formalization chunking remains explicitly deferred, as allowed by the brief. Existing essay instructions require conditional presentation of premises; methodology records the specific omitted-support edges. Nothing here establishes those premises independently.

## Finding placement

These six findings are review conclusions and material limits; defect counts are separately stated in the verdict.

| Finding | Placement |
|---|---|
| Deterministic cuts preserve mandatory context, source attribution/citation and explicit omitted support; structural proof is not semantic proof | §1 |
| Actual 48-window arithmetic fits; downstream headroom exists, with empirical growth and exact-output refusal limits | §2 |
| Root relevance remains a model decision; code only computes costs and cuts its selected bundle | §3 |
| Zero windows and all eligible omissions are accounted for; an empty T refuses | §4 |
| Fresh native real plan exactly reproduces sigma, with no generation; counter is free but networked | §5 |
| Full test result, control result/restoration, unexecuted live behavior and optional chunking limit | §6 |

6 findings, 6 placed.

Delivery checkpoint: all requested review work complete at clean `5009af1e053d11dac18405fe7402331134585fea`. No source fix is required by this review. The next product proof is the separately authorized paid pilot, with the model-quality and output-size limits above kept explicit. No merge or paid run was performed.

DONE tau review verdict=merge blocking=0 should_fix=0 tests=624/626 negctl=pass
