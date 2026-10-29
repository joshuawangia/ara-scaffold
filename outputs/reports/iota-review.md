# Iota independent review of theta and eta

**Verdict: theta FIX-FIRST; eta FIX-FIRST.** Two blocking findings and four should-fix findings are reproduced offline. Both branch suites and mutation runners pass, but the mechanically merged suite has three failures. Fix the resume-policy and shared-T integration blockers before the paid rerun; the authors own the repairs.

Subjects: theta `b063433d56f83f058d4941c8c8a30b43ec0cf355`, eta `ec8e1870926c5fdf226abfab11e5426ac3aee5ad`, both based on `ba3a004d422467a0aed8a77be9407587d265a514`. Review-only merge: `3869e881256c754bf46c367fbd9a120cf7833e3e` in `/home/dev/ara-work/iota-integration`. I read the briefs before the author reports and reviewed the native call, extraction, provenance, construction, freeze, CLI, budget, cache and export paths. Prior review context: delta rounds 4–6. No delegation, live generation, token-count service calls, paid calls or author-branch edits. All test responses are offline placeholders.

## Theta findings

### T-B1 — BLOCKING: resume bypasses a changed extraction acceptance policy

**Locations:** `ara/runtime/extraction.py:412`, `:425`, `:436`, `:320`; CLI `ara/runtime/cli.py:135`.

The reuse predicate compares PDF, bibliographic record, page diagnostics and input hash, but receives no effective configuration or acceptance-contract version. It accepts the old graph by its recorded hash without checking it against the current extraction policy.

**Reproduction:** Extract a one-premise placeholder paper with `extraction_require_inference=false`. Resume the identical paper with that setting changed to `true`. Both the direct boundary probe and native `ara extract` probe show the difference. Fresh extraction with the new setting fails with `extraction has no stated inference`; resume publishes it as `extracted`, with zero new model calls. The PDF and manifest are unchanged. Thus an artifact produced under weaker acceptance rules silently satisfies a run that claims the stronger rules. The same absence of configuration binding warrants checking model/stage and interpretation-version changes; those additional cases are source-inspection risks, not separately executed reproductions.

**Fix direction:** Record a versioned extraction acceptance identity with each completed outcome. Compare relevant effective settings, and either revalidate the accepted graph offline under the new rules or explicitly re-extract/refuse incompatible reuse. Allow unrelated spending caps and recovery allowances to change without gratuitous re-extraction. Keep the original model/configuration receipts. Add the fresh-versus-resume policy-change regression.

Evidence: `iota-probes.py::test_resume_changed_acceptance_config` and `test_native_cli_changed_acceptance_config`, outputs `CONFIG_DRIFT` / `NATIVE_CONFIG_DRIFT` in [independent probe log](iota-probes.txt). These probes execute theta's unchanged extraction/provenance modules in the integration checkout; their source matches theta exactly.

### T-S1 — SHOULD-FIX: an interrupted resumed run hides completed ancestor papers from the next resume

**Locations:** `ara/runtime/extraction.py:436`; `ara/runtime/provenance.py:93`, `:99`.

`extraction_outcomes()` correctly selects the latest batch for publication, but it is also used as the inventory of reusable successes. Those are different responsibilities.

**Reproduction:** A completes `p`. B imports A, then attempts `q` before reaching `p`; `q` fails and B stops at its configured threshold. B retains A's verified completed `p` receipts. C resumes only from B and requests `p`: C dispatches and pays for `p` again because the latest B batch contains only the failed `q` outcome. The independent probe uses a fresh cache and records that additional dispatch. Supplying A as another `--resume-from` is a workaround, but requiring the operator to reconstruct the entire ancestor list defeats transitive completed-paper reuse.

**Fix direction:** Build a separate verified reusable-success index across the imported ancestry, bound to the current source identity and acceptance policy, with explicit conflict handling. Retain latest-batch selection for final literature and current failure disclosure. Test an intermediate stop before an inherited success would be re-emitted locally.

Evidence: `iota-probes.py::test_resume_stopped_descendant_loses_inherited_completed_paper`, output `TRANSITIVE_REUSE`.

### T-N1 — NOTE: the observed recovery and failed-evidence isolation work; resume remains whole-paper only

**Locations:** `ara/runtime/calls.py:80`, `:395`; `ara/runtime/extraction.py:342`; `ara/runtime/construction.py:154`; `ara/runtime/provenance.py:23`, `:54`.

I inspected the actual stopped run's response structure without copying source content: range 1 required correction; the later rejected response had one item, `coverage_complete=true`, no new gaps, and `context_request={pages:[], evidence_ids:[]}`. Theta's offline regression reproduces that envelope after an earlier range has already consumed a correction. Mode-specific schemas reach the prompt, token counter, provider schema and local validator; corrections preserve omitted candidate items. Initial ranges and obligation-free graph reviews cannot request context; supplied obligations have bounded, corrected context handling. Corrections remain within the paper's finite count/USD allowance.

Failed papers publish no items, are excluded from citations and construction, and appear with reasons/receipts and the configured threshold. Three failures may complete under the full-profile default; the fourth refuses publication. Global budget, unknown-spend and operational errors still stop. Original call/human receipts and costs remain present; overlapping/transitive receipt imports are deduplicated. Source/input/manifest changes cause fresh extraction. Missing or altered pinned origin data refuses; hashes do not authenticate an entirely rewritten history.

**Operating action:** preserve all origin logs and use whole-paper resume after the fixes above. The first live run completed no paper, so its paid partial range is not reusable through this feature. Structural tests do not establish semantic extraction quality or completion of all 26 PDFs within USD125.

## Eta findings

### E-B1 — BLOCKING: frozen-T verification is incompatible with theta's native extraction and resume contracts

**Locations:** `ara/runtime/frozen.py:43`, `:55`, `:121`; theta contracts at `ara/runtime/calls.py:80`, `ara/runtime/provenance.py:54`, `:73`, `:99`.

Three checks duplicate the earlier extraction contract and diverge after integration:

1. **Every ordinary theta extraction:** the verifier rebuilds a prompt using the full static extraction schema. Theta's accepted prompt contains the schema specialized for initial extraction/review/obligation mode. A valid builder is refused with `frozen T: schema/prompt version drift: extract_paper`.
2. **Resumed extraction:** theta pins `receipt_id` to the entire original prefix, while copying only deduplicated events and removing nested import markers. Eta hashes the copied block as if it were the original prefix. A valid resumed builder is refused with `frozen T: broken extraction provenance receipt`.
3. **Resumed outcome reconstruction:** eta assembles every historical `extraction_outcome`, including ancestor successes/failures and current outcomes. Theta publishes only the selected current batch. After bypassing only receipt verification in a diagnostic probe, the valid resumed builder next fails with `frozen T: broken extraction provenance`. That bypass is diagnostic evidence, not a proposed fix or a successful production import.

**Reproduction:** four native extraction → provenance import → construction/freeze fixtures: ordinary success, ordinary disclosed failure, resumed success, and resumed disclosed failure. All construct a frozen T and all fail `load_frozen` as described. The test marks the fixture builder complete to isolate extraction/construction verification; native run/select completion is separately covered by eta's integration suite.

**Fix direction:** use versioned shared schema construction and theta's pinned/transitive import verifier and current-outcome selector. Preserve rejection of changed hashes, missing origins and incompatible versions. Recognize compatible historical contracts for retained old attempts, including rejected attempts from the original run, rather than requiring every historical prompt to equal today's prompt. Add all four cases through native `ara run --from-frozen`, including a builder completed by later `ara select`. Fix all three checks together; relaxing the first check alone leaves the remaining refusals.

Evidence: parameterized `iota-probes.py::test_shared_theta_builder`; `FROM_FROZEN` and `DIAGNOSTIC_ONLY` lines in [probe output](iota-probes.txt).

### E-S1 — SHOULD-FIX: rich construction artifacts are not checked against the accepted model response

**Locations:** `ara/runtime/frozen.py:105`, `:128`, `:138`; contrast the non-rich comparison at `:146`.

The rich path proves that batch files match SYSTEM receipt hashes and merge to the frozen T. It merely checks that some accepted construction MODEL receipt exists; it does not reconstruct the batch's model-authored formulas from that receipt. The non-rich path does compare the response to T.

**Reproduction:** in an offline rich-builder fixture, change the accepted `build_t_batch` MODEL response's first formula to placeholder `S`, rebuild the fixture's outer log/anchor, and leave the batch artifact and frozen formula unchanged. `load_frozen` accepts the internally contradictory history. This follows the existing semantic-refusal tests' approach of rebuilding the outer fixture chain. It is not a claim of defeating a signature, nor a claim that hashes can authenticate a completely coherent rewritten history.

**Fix direction:** bind each accepted batch to its original call/response and deterministic normalization, including encoded formulas and targeted correction patches, then compare the reconstructed commitments to the saved batch and T. Add a rich counterpart of the existing non-rich response-disagreement test. This strengthens the requested full provenance check beyond mutually consistent SYSTEM artifacts.

Evidence: `iota-eta-probes.py::test_rich_model_response_disagrees_with_artifact`; `RICH_RECEIPT` in [eta probe output](iota-eta-probes.txt).

### E-S2 — SHOULD-FIX: a writer-only stage setting is rejected as construction drift

**Locations:** `ara/runtime/frozen.py:15`, `:19`, `:91`.

`CONSTRUCTION_KEYS` includes the entire `stages` mapping. Therefore candidate search/writer settings are not independently configurable as promised.

**Reproduction:** complete an ordinary offline builder, change only `stages.write_essay.effort` to `low`, and run the candidate with explicit caps. It refuses before provider creation with `frozen T: construction config drift`; no construction setting changed.

**Fix direction:** compare the effective settings of construction/extraction stages that matter to compatibility, with their defaults resolved, instead of the entire stage map. Permit candidate proposal/search/writing changes while preserving the inherited builder's recorded settings. Test both an allowed writer-only change and a refused construction change.

Evidence: `iota-eta-probes.py::test_writer_stage_change_refuses`, output `WRITER_CONFIG`.

### E-S3 — SHOULD-FIX: the candidate's extraction summary omits inherited failures and their policy

**Locations:** `ara/runtime/export.py:34`, `:85`, `:90`, `:97` at eta; merged theta failure fields are in the same extraction summary.

The exporter calculates `extraction` from top-level events before discovering `frozen_history_import`. It includes nested history in inherited dollar/token totals, but not in extraction outcome and coverage disclosure.

**Reproduction:** feed an extraction history with failed `q` through the native frozen-history import/export seam. The candidate summary reports `extraction.failed=[]` and `failure_policy=null`, while its inherited total includes both calls. The original failed outcome is still present deep in the verbatim nested evidence, so it has not been destroyed; the accessible structured disclosure is misleadingly empty. This is an isolated import/export test. E-B1 currently prevents the corresponding full native shared-T candidate, and no successful full candidate with failures is claimed.

**Fix direction:** expose inherited extraction outcomes, partial coverage, current failures, historical failures and the failure policy explicitly, or render clearly separated local/inherited extraction summaries. Keep those events nested for lifecycle and budget purposes; do not fix disclosure by charging inherited events as local work.

Evidence: `iota-probes.py::test_shared_failure_disclosure`, output `DISCLOSURE`.

### E-N1 — NOTE: sharing, accounting, candidate identity and later selection use the intended native lifecycle

**Locations:** `ara/runtime/cli.py:153`, `:176`, `:202`; `ara/runtime/frozen.py:79`, `:153`, `:163`; `ara/runtime/orchestration.py:43`.

The builder-complete rule is correct for the stated completed-builder contract. `awaiting_selection` alone refuses; a later successful native `ara select` produces the final draft that makes it eligible. No extra freeze is required. Original-builder-only sourcing prevents a candidate from pretending to be a new builder.

Candidate runs copy byte-identical T, start at target proposal, and refuse another construction/freeze. Fresh UUID cache identities and recorded engine seeds separate candidate cache keys; selection retains the candidate's own identity. These are engine seeds and separate requests, not provider sampling seeds or proof of statistically independent answers. Local caps exclude inherited charges; `campaign_totals` deduplicates original model receipts across the supplied log set.

**Operating action:** keep the complete campaign log set, including the builder. A candidate inherits only the prefix through freeze, so candidate-only totals omit the pilot's subsequent search/writing/selection work. Methodology identifies the shared T, builder and freeze/hash, and separates inherited/local spend; address E-S3 for source-coverage disclosure. No live provider independence, budget sufficiency, semantic quality or campaign completion has been proved by this review.

## Integration and verification

The scratch worktree started at `ba3a004`, merged theta first, then eta. Eta produced **five conflicting files**: `DECISIONS.md`, `README.md`, `ara/runtime/cli.py`, `tests/integration/negative_controls.py`, and `tests/runtime/test_extraction_round6.py`. I kept both documentation additions, combined the CLI imports and control lists, and retained eta's explicit primary-error assertion. The resulting review merge is `3869e88`; no behavioral repair was included. This is an integration exercise, not a merge into an author branch or main.

The required commands run sequentially: theta pytest → theta control runner → eta pytest → eta control runner → merged pytest. Each branch check runs on its exact committed tree in a detached scratch worktree, so mutation controls never touch an author checkout.

| Check | Result | Receipt |
|---|---|---|
| Theta `uv run pytest` | 458 passed, 2 live-provider skips; 460 collected; exit 0; 247.74s | [Full output](iota-theta-pytest.txt) |
| Theta `uv run python tests/integration/negative_controls.py` | 181/181 mutations red; 181/181 restorations green; exit 0; tracked source restoration verified | [Full output](iota-theta-controls.txt), [results](iota-theta-controls/results.json) |
| Eta full pytest | 438 passed, 2 live-provider skips; 440 collected; exit 0; 286.49s | [Full output](iota-eta-pytest.txt) |
| Eta control runner | 182/182 mutations red; 182/182 restorations green; exit 0; tracked source restoration verified | [Full output](iota-eta-controls.txt), [results](iota-eta-controls/results.json) |
| Merged full pytest | 479 passed, 3 failed, 2 live-provider skips; 484 collected; exit 1; 290.99s | [Full output](iota-merged-pytest.txt) |
| Independent integration/theta probes | 9 passed; includes deliberately asserted counterexamples, not readiness tests | [Source](iota-probes.py), [output](iota-probes.txt) |
| Independent eta probes | 2 passed; deliberately asserted counterexamples | [Source](iota-eta-probes.py), [output](iota-eta-probes.txt) |

I read the new mutation definitions and these fresh theta red/green traces (all restored green):

| Mutation | Observed injected-defect failure |
|---|---|
| `mode_specific_context_wire` | Initial/review schemas wrongly contain `context_request`; four parameter cases fail. |
| `context_validation_before_acceptance` | Unread-page/unknown-evidence requests escape the correction boundary and raise terminal `Rejected`. |
| `correction_paper_limit` | Expected paper `BudgetStop` does not occur. |
| `paper_failure_continue` | A known paper failure terminates the positive continuation/construction test. |
| `failed_evidence_exclusion` | Expected rejection of failed-status items does not occur. |
| `resume_input_binding` | Changed input dispatch is absent: `[]` instead of `['p']`. |
| `resume_receipt_dedup` | Simulated cost is 0.007 instead of 0.00525. |
| `resume_origin_checkpoint` | Truncated-log checkpoint refusal does not occur. |

Selected full traces are in [theta control receipts](iota-theta-controls/). I also read eleven new eta mutation definitions and fresh red/green traces, all restored green:

| Mutation | Observed injected-defect failure |
|---|---|
| `shared_freeze` | The explicit missing-freeze error becomes `list index out of range`. This proves the diagnostic guard, not successful acceptance without it. |
| `shared_hash` | Changed commitments reach the forbidden provider factory. |
| `shared_topic` | Different topic reaches the forbidden provider factory. |
| `shared_config` | Construction-setting drift reaches the forbidden provider factory. |
| `shared_schema` | Schema-contract drift reaches the forbidden provider factory. |
| `shared_receipts` | Missing accepted build receipts produce an index error instead of the explicit refusal. |
| `shared_cache_origin` | Missing cache origin reaches the forbidden provider factory. |
| `shared_campaign` | Simulated campaign cost becomes 60.0033 instead of 20.0033. |
| `shared_cache_identity` | Candidate cache-key sets intersect the builder/prior candidate keys. |
| `shared_local_budget` | Imported builder charges consume the candidate cap and make the expected successful run exit 2. |
| `shared_complete` | An incomplete builder reaches the forbidden provider factory. |

Selected full traces and the complete result inventory are in [eta control receipts](iota-eta-controls/). The merged suite fails exactly these three cases:

- `tests/runtime/test_shared_frozen_rich.py::test_full_rich_history_and_campaign`
- `tests/runtime/test_shared_frozen_rich.py::test_broken_rich_provenance[batch]`
- `tests/runtime/test_shared_frozen_rich.py::test_broken_rich_provenance[plan]`

All three stop at `frozen.py:56` with `schema/prompt version drift: extract_paper`, confirming E-B1. The two negative cases fail because they hit this earlier refusal instead of reaching their intended damaged-artifact checks. The merged rich path is not ready. The independent resume probes additionally expose the later import-digest and outcome-selection incompatibilities; those are not three additional full-suite failures.

Final checks: both author trees remain clean at the requested heads; the integration tree is clean at `3869e88`; `git diff --check` passes. Both mutation worktrees restored their tracked source exactly (`git diff --exit-code` exited 0). Theta's extraction/provenance/construction/paper-budget modules are unchanged in the merge, supporting attribution of the independent theta probes. The sequential verification process exited and no test/control process from this review remains running. Scratch worktrees and report receipts are retained for review. No push or main-branch merge occurred.

No live behavior is inferred from these checks. The independent probes block sockets; all model responses and charges are simulated. No real extraction, construction, search, writing, token-count service or paid rerun was performed. Earlier PDF coverage and cost-scenario limitations remain applicable; this review neither authorizes new spend nor releases prior campaign costs.

## Finding placement

| Finding that changes the next action | Section carrying it |
|---|---|
| T-B1: changed acceptance policy bypassed by reuse | Theta / T-B1 |
| T-S1: interrupted descendant loses reusable ancestor inventory | Theta / T-S1 |
| T-N1: successful recovery/isolation, retained origins, whole-paper and live-proof limits | Theta / T-N1; Integration and verification |
| E-B1: static-schema, import-digest and current-outcome integration mismatches | Eta / E-B1; Integration and verification |
| E-S1: rich model-response/artifact consistency not verified | Eta / E-S1 |
| E-S2: writer-only setting rejected | Eta / E-S2 |
| E-S3: inherited extraction failures absent from candidate summary | Eta / E-S3 |
| E-N1: native completion/sharing/accounting, seed limits and complete campaign log set | Eta / E-N1; Integration and verification |

8 findings, 8 placed.

DONE iota review theta=fix-first eta=fix-first blocking=2 should_fix=4 integration=conflicts:5 tests_merged=479/484 report=/home/dev/ara-work/reports/iota-review.md


## Re-review theta

**Verdict: merge theta; 0 blocking, 0 should-fix. T-B1 and T-S1 are resolved by design and independent verification.** Narrow re-review of `be7468df12d4c0422d54f8ccd881d653cd92bdd4` against `b063433d56f83f058d4941c8c8a30b43ec0cf355`, following `iota-rereview-theta.md` and `theta-round-3.md`. I inspected the actual diff and new mutations after reading the brief, then the author's Round 3 report. Verification runs in the detached `/home/dev/ara-work/iota-theta-rereview` checkout. No author-branch edits, delegation, live token counting, paid calls or push. Eta's rebase is outside this re-review; the earlier eta findings and integrated-run verdict are not superseded here.

### T-B1 resolved — reuse binds the current acceptance contract

**Locations:** `ara/runtime/extraction.py:25`, `:28`, `:283`, `:339`, `:381`, `:433`, `:449`; `ara/runtime/cli.py:135`.

Completed outcomes now record a versioned identity covering inference policy, provider, effective extraction model/effort/thinking/fallbacks, and prompt/schema hashes. CLI supplies the profile-applied configuration and contract root to the reusable-success index. Both index construction and the execution boundary compare the identity. Missing or incompatible identities return a source to native extraction/validation instead of treating the old graph as accepted under new rules. Strict coverage is checked before reuse, closing the related partial-source bypass.

This fixes the design, rather than only adding a special case for inference. An explicit interpretation version covers validation/normalization/mode-schema changes and must be bumped with such changes. Budget, recovery and unrelated-stage settings remain outside the identity; the tests confirm those changes preserve compatible reuse. Legacy outcomes without this identity cannot automatically supply completed-paper reuse, while their existing pinned literature and original receipts remain valid historical imports. A native cache hit may still avoid a new dispatch, but it undergoes current validation with original production receipts retained.

**Independent proof:** I reran the previous native CLI counterexample. Fresh and resumed extraction now both mark the premise-only placeholder paper failed when `extraction_require_inference` changes to true; neither publishes it as extracted. A separate same-cache probe rejects the old cached response under the new rule, records zero new charge and retains the original USD0.00175 simulated charge. The full suite also passes model/settings/version/prompt/schema/legacy drift, cap-only compatibility, execution-time recheck and strict-coverage cases.

### T-S1 resolved — verified ancestor successes remain reusable after an intermediate stop

**Locations:** `ara/runtime/provenance.py:99`, `:108`; `ara/runtime/extraction.py:449`, `:466`, `:477`.

Resume now uses a separate historical outcome inventory after verifying the pinned origin chain/imports. It filters candidates through current source and acceptance identity checks and the accepted merged-graph receipt. Conflicting compatible successes explicitly refuse before receipt import. Current-batch publication still uses `extraction_outcomes`, so adding ancestor candidates does not reintroduce old failures or duplicate papers into the published corpus.

**Independent proof:** A completes `p`; B imports A, fails on `q` before visiting `p`, and stops; C resumes only from B. C now reuses `p` with zero new calls. Its total simulated cost remains USD0.0035, retaining both original attempts exactly once. Its current corpus contains only successful `p`, while historical failed `q` remains disclosed. The completed artifact passes native literature provenance verification.

The documented API now clearly distinguishes `historical_extraction_outcomes` (candidates) from `extraction_outcomes` (current corpus), and requires effective config/root arguments for `resume_papers`. Eta can consume this contract in its own rebase; no eta repair or re-review is claimed here.

### Fresh extraction-full command and retained operating limits

**The command shape is verified offline at this head.** I ran the native CLI through profile/config validation and actual PDF intake, intercepting the injected calls factory before any provider could be constructed. Sockets were blocked. Both a fully isolated fresh command and a fresh destination importing only prior receipts reached the expected interception. Exit 2 with `PreflightCaptured` in these receipts is intentional, not a failed extraction or a generation attempt.

The inventory remains **26 PDFs / 1,379 physical pages / 82 affected pages**. The known PDF encoding/font warnings remain in the preflight log. Use the existing `--missing record-only` policy and retain partial-source disclosures. No OCR, semantic fidelity or completed 26-paper extraction is claimed.

The [reviewed config proposal](iota-theta-rereview-config.proposed.yaml) preserves the original full26 configuration, changing only the cache path to an unused location and making the full profile's default failure threshold explicit. Effective values checked at the native boundary:

| Setting | Verified value |
|---|---|
| Extraction provider/model | Anthropic / `claude-opus-5`, high effort, adaptive thinking |
| Fallbacks | Disabled |
| Enclosing and extraction USD caps | 125 / 125 |
| Token cap | 12,000,000 |
| Acceptance/recovery | Require inference; one targeted correction per response |
| Failed-paper limit | 3; exceeding it stops publication |
| Ordinary paper allowance | 24 continuations / USD15 |
| At least 300 physical pages | 48 continuations / USD30 |

For this continuing campaign, use a **new destination and cache** and carry the original stopped run's receipts so the USD125 cap includes its **USD0.818205** already spent. The native preflight confirmed **USD124.181795 remaining** after import. The original run has **zero completed papers**, so this does not reuse its partial range: all 26 papers still require extraction.

```bash
cd /home/dev/ara-work/theta
mapfile -t iota_paper_ids < /home/dev/ara-work/reports/delta-rereview4-paper-ids.txt
iota_paper_args=()
for iota_paper_id in "${iota_paper_ids[@]}"; do
  iota_paper_args+=(--paper-id "$iota_paper_id")
done
uv run ara extract \
  --config /home/dev/ara-work/reports/iota-theta-rereview-config.proposed.yaml \
  --profile extraction-full \
  --manifest /home/dev/ara-scaffold/literature/manifest.yaml \
  --fulltext-dir /home/dev/ara-scaffold/literature/fulltext \
  --missing record-only \
  --run-dir /home/dev/ara-work/theta/runs/full26-rerun-be7468d \
  --resume-from /home/dev/ara-scaffold/runs/full26-extraction \
  "${iota_paper_args[@]}"
```

[Command proposal](iota-theta-rereview-command.proposed.sh); syntax checked with `bash -n`, generation not executed. The proposed run/cache paths were absent during preflight and remain uncreated by this review. A fully isolated fresh run omits `--resume-from`; that form was also checked, but gives a USD125 new-run allowance without importing the old spend. Its campaign accounting must still include the original log. Preserve the origin log/checkpoint for the receipt-carry form.

The current head changes no extraction prompt, schema or planning inputs relative to `b063433`; no new provider token count was needed or performed. Existing cost scenarios remain scenarios. Finite caps, whole-paper-only reuse, original receipt retention and the lack of live semantic/completion proof remain T-N1 operating limits. The original paid partial range is not rescued by this change. This review checks theta's extraction readiness for the bounded experiment; it does not certify eta's shared-T path.

### Re-review verification and mutations

| Check | Result | Receipt |
|---|---|---|
| Full `uv run pytest` | 473 passed, 2 live-provider skips / 475 collected; exit 0; 294.04s | [Full output](iota-theta-rereview-pytest.txt) |
| Independent previous-counterexample/cache probes | 3 passed; 1.76s | [Source](iota-theta-rereview-probes.py), [output](iota-theta-rereview-probes.txt) |
| Native command preflights | Both reached the expected pre-provider interception; 0 provider creations/new calls | [Structured receipt](iota-theta-rereview-preflight.json), [fresh output](iota-theta-rereview-preflight.txt), [receipt-carry output](iota-theta-rereview-carry-preflight.txt) |
| Full control runner, after pytest | 188/188 mutations failed as expected; 188/188 restorations passed; exit 0 | [Full output](iota-theta-rereview-controls.txt), [results](iota-theta-rereview-controls/results.json) |

I read all seven new mutation definitions and their fresh red/green traces. Each red result was a behavioral assertion failure (pytest exit 1), followed by its corresponding restored pass (exit 0):

| Mutation | Observed failure under mutation | Trace pair |
|---|---|---|
| `resume_acceptance_policy` | Changed inference policy failed to reject the resumed paper | [red](iota-theta-rereview-controls/resume_acceptance_policy-red.txt), [green](iota-theta-rereview-controls/resume_acceptance_policy-green.txt) |
| `resume_acceptance_model` | Model drift reused the old paper with no new extraction | [red](iota-theta-rereview-controls/resume_acceptance_model-red.txt), [green](iota-theta-rereview-controls/resume_acceptance_model-green.txt) |
| `resume_acceptance_version` | Interpretation-version drift reused the old paper | [red](iota-theta-rereview-controls/resume_acceptance_version-red.txt), [green](iota-theta-rereview-controls/resume_acceptance_version-green.txt) |
| `resume_ancestor_inventory` | An interrupted descendant caused another call for the completed ancestor paper | [red](iota-theta-rereview-controls/resume_ancestor_inventory-red.txt), [green](iota-theta-rereview-controls/resume_ancestor_inventory-green.txt) |
| `resume_ancestor_conflict` | Conflicting compatible completed outcomes failed to refuse | [red](iota-theta-rereview-controls/resume_ancestor_conflict-red.txt), [green](iota-theta-rereview-controls/resume_ancestor_conflict-green.txt) |
| `resume_execution_policy` | A policy change after indexing bypassed the execution-boundary refusal | [red](iota-theta-rereview-controls/resume_execution_policy-red.txt), [green](iota-theta-rereview-controls/resume_execution_policy-green.txt) |
| `resume_strict_coverage` | Strict coverage failed to reject a reused partial paper | [red](iota-theta-rereview-controls/resume_strict_coverage-red.txt), [green](iota-theta-rereview-controls/resume_strict_coverage-green.txt) |

After the runner exited, both scratch and author checkouts remained clean at `be7468df12d4c0422d54f8ccd881d653cd92bdd4`. Unstaged and staged `git diff --exit-code`, `git diff --check`, and empty porcelain status confirmed restoration. The proposed paid run/cache paths remain absent. No live-provider result or eta integration result is implied by these offline checks.

### Re-review finding placement

| Finding/disposition affecting the next action | Placement |
|---|---|
| T-B1 resolved, identity/version duties, legacy restriction and cached revalidation | T-B1 resolved; Re-review verification and mutations |
| T-S1 resolved, ancestor inventory, conflict checks and current/history separation | T-S1 resolved; Re-review verification and mutations |
| Fresh command, original-spend carry, partial-source/whole-paper/live-proof limits and separate eta scope | Fresh extraction-full command and retained operating limits; opening scope |

3 findings, 3 placed.

DONE iota rereview theta=merge blocking=0 should_fix=0 tests=473/475 negctl=pass


## Re-review eta

**Verdict: merge eta; 0 blocking, 0 should-fix. E-B1, E-S1, E-S2 and E-S3 are resolved by design and independent verification.** Narrow re-review of eta `185a318a7fa5a46485a375ee1cb26244c2254403`, based on reviewed theta `be7468df12d4c0422d54f8ccd881d653cd92bdd4`, following `iota-rereview-eta.md` and `eta-round-2.md`. I read the repair diff, native callers and owning tests, all eight new mutation definitions and retargeted controls, then checked the author's Round 2 claims against independent evidence. Verification uses an independent detached clone at `/home/dev/ara-work/iota-eta-rereview`. No author edits, delegation, paid calls, provider token counting or push; no operations in the active paid extraction checkout or its run directories.

### E-B1 resolved — shared native contracts, pinned origins and current outcomes

**Locations:** `ara/runtime/frozen.py:46`, `:158`; `ara/runtime/response_contracts.py:9`, `:31`; `ara/runtime/calls.py:81`.

The frozen verifier now delegates imported-history verification to theta's `verify_imports`, which checks actual pinned origin prefixes and transitive imports. It reconstructs literature using theta's `extraction_outcomes`, so historical attempts remain evidence without becoming duplicate current papers. This closes both later resume failures identified in the original review.

Live prompt rendering and receipt verification share `response_contracts.py`, including mode-specific extraction schemas. New MODEL receipts record response-contract version 2. Historical accepted and rejected extraction attempts can match a pinned legacy template hash; unknown versions or changed templates refuse. I independently recomputed that hash from the original `ba3a004` prompt and schema in the review clone and checked the fixture against that historical prompt: `bfba951c2b48fc237eb2d5cf841ad9b0de8161f7f1a4f30ade2684bf1aa8c730`. Historical compatibility neither rewrites old receipts nor dispatches old schemas.

**Proof:** All four native cases pass through extraction, builder run, later builder selection, candidate `--from-frozen`, and later candidate selection/export. The full suite includes missing/changed pinned-ancestor refusals before provider creation. I reran the exact three previously failing merged-suite cases separately: `test_full_rich_history_and_campaign`, `test_broken_rich_provenance[batch]`, and `[plan]`; all pass. The independent resumed/disclosed-failure candidate also completes, with no local extraction, construction or freeze and byte-identical T.

### E-S1 resolved — accepted responses bind rich batch artifacts

**Locations:** `ara/runtime/frozen.py:72`, `:176`; `ara/runtime/construction.py:101`, `:114`, `:120`; `ara/runtime/calls.py:201`.

For each `(plan_id, batch_index)`, verification decodes the accepted MODEL response using the live decoder, applies the live correction merger when appropriate, and normalizes immutable evidence text/citations using the same helper as construction. A targeted correction must identify the actual preceding rejected candidate. The reconstructed commitments, symbols and alignments must match the saved batch. Existing artifact hashes, merge checks and frozen-table checks remain in force.

This directly closes the original internally contradictory MODEL-response/artifact counterexample. It also covers encoded formula ASTs and corrected responses, instead of comparing only the unnormalized provider text.

**Proof:** The original response/artifact contradiction now raises `construction response does not match batch`. An independent native CLI probe rebuilds a valid outer fixture chain with an inconsistent rich MODEL formula and confirms the same refusal before provider creation or destination log creation. A changed commitments file also refuses at that boundary. The full suite passes encoded and corrected receipt cases plus correction-origin disagreement refusal. All examples use placeholders.

### E-S2 resolved — compatibility excludes unrelated stage entries

**Locations:** `ara/runtime/frozen.py:18`, `:24`; `ara/runtime/providers.py:167`.

Compatibility compares relevant effective construction/extraction provider settings with runtime defaults supplied, plus the existing construction-specific configuration fields. It no longer hashes the entire `stages` map. A writer-only entry therefore does not invalidate T; effective extraction model/effort changes and construction interpretation changes still do.

This changes compatibility checking only. The current provider's stage-override implementation remains extraction-specific; accepting a `stages.write_essay` entry does not newly make that entry an operative writer override. The builder's original configuration remains verbatim in inherited history.

**Proof:** The original writer-only counterexample now succeeds through native `--from-frozen`. The full suite verifies that explicitly supplying an effective extraction default preserves compatibility, changing extraction effort changes the compatibility identity, and meaningful construction drift refuses.

### E-S3 resolved — inherited extraction disclosure without local charging

**Locations:** `ara/runtime/export.py:35`, `:63`, `:87`, `:107`.

The exporter derives extraction outcomes, partial coverage, models/usage, current failures, historical failures, stops and the failure policy from the inherited builder prefix plus local extraction evidence. The summary explicitly labels that scope. Imported history stays nested for lifecycle and budget purposes; the candidate's local charges remain its own MODEL work.

**Proof:** The independent native resumed/disclosed-failure candidate publishes successful `p`, reports current failed `q` and both historical failed attempts, and retains the maximum-three-failures policy. Simulated extraction spend is USD0.00525, inherited prefix spend USD0.00875, and local candidate spend USD0.01575. The full supplied campaign totals USD0.04025 and remains identical when the input log list is duplicated. Candidate-only aggregation is smaller because it excludes post-freeze builder work. The full suite also passes inherited partial-page diagnostics, model identity and production-lineage disclosure. The source builder files remain unchanged.

### Re-review verification and mutations

| Check | Result | Receipt |
|---|---|---|
| Full `uv run pytest` | 513 passed, 2 live-provider skips / 515 collected; exit 0; 335.20s | [Full output](iota-eta-rereview-pytest.txt) |
| Original three merged-suite failures plus independent probes | 8 passed; exit 0; 23.08s | [Probe source](iota-eta-rereview-probes.py), [output](iota-eta-rereview-probes.txt) |
| Full control runner, sequentially after pytest | 216/216 expected mutation failures; 216/216 restored passes; exit 0 | [Full output](iota-eta-rereview-controls.txt), [results](iota-eta-rereview-controls/results.json) |

I inspected all eight new mutation definitions and their fresh failure/pass traces. Each mutant exited 1, and its restored target exited 0. These are behavior checks, including valid-path regressions and the explicitly narrower correction-origin diagnostic check:

| Mutation | Observed failure under mutation | Trace pair |
|---|---|---|
| `shared_rich_response` | Removing response/artifact comparison permits the original contradictory MODEL formula. | [red](iota-eta-rereview-controls/shared_rich_response-red.txt), [green](iota-eta-rereview-controls/shared_rich_response-green.txt) |
| `shared_correction_origin` | Removing the origin check changes the expected refusal to a later batch-response mismatch; the downstream comparison still rejects this fixture. | [red](iota-eta-rereview-controls/shared_correction_origin-red.txt), [green](iota-eta-rereview-controls/shared_correction_origin-green.txt) |
| `shared_current_outcomes` | Using every historical outcome incorrectly refuses the valid resumed/disclosed-failure candidate. | [red](iota-eta-rereview-controls/shared_current_outcomes-red.txt), [green](iota-eta-rereview-controls/shared_current_outcomes-green.txt) |
| `shared_transitive_origin` | Skipping pinned-import verification lets missing and changed ancestors reach the forbidden provider-creation boundary. | [red](iota-eta-rereview-controls/shared_transitive_origin-red.txt), [green](iota-eta-rereview-controls/shared_transitive_origin-green.txt) |
| `shared_writer_settings` | Including the entire stage map again incorrectly refuses the writer-only configuration. | [red](iota-eta-rereview-controls/shared_writer_settings-red.txt), [green](iota-eta-rereview-controls/shared_writer_settings-green.txt) |
| `shared_extraction_settings` | Ignoring effective stage settings fails to distinguish changed extraction effort. | [red](iota-eta-rereview-controls/shared_extraction_settings-red.txt), [green](iota-eta-rereview-controls/shared_extraction_settings-green.txt) |
| `shared_failure_disclosure` | Ignoring inherited extraction makes the candidate report no current failed paper instead of failed `q`. | [red](iota-eta-rereview-controls/shared_failure_disclosure-red.txt), [green](iota-eta-rereview-controls/shared_failure_disclosure-green.txt) |
| `shared_legacy_attempts` | Removing the pinned legacy allowance rejects supported historical accepted/rejected attempts. | [red](iota-eta-rereview-controls/shared_legacy_attempts-red.txt), [green](iota-eta-rereview-controls/shared_legacy_attempts-green.txt) |

All control traces are archived alongside the results. The relocated full-schema control also still fails at its intended assertion and passes after restoration.

After the control runner exited, all **132 tracked files** in both review and author checkouts matched the [input fingerprints](iota-eta-rereview-files.json). Both remained clean at `185a318a7fa5a46485a375ee1cb26244c2254403`, with theta `be7468d` as their base. Staged/unstaged `git diff --exit-code`, `git diff --check` and empty porcelain status passed: [scratch receipt](iota-eta-rereview-scratch-restoration.json), [author receipt](iota-eta-rereview-author-restoration.json).

### Retained limits and next action

This re-review covers eta integrated on theta `be7468d`, including the formerly failing merged path. It does not certify any later revision or the active real-corpus extraction. No live semantic quality, statistical independence, campaign completion or budget-sufficiency claim follows from offline tests.

Keep the original completed builder and every pinned ancestor log. A native builder awaiting selection becomes eligible only after later `ara select` produces the final draft. Candidates preserve byte-identical T, reference its original freeze, start at target proposal and must not re-freeze it. Fresh cache identities and engine seeds separate candidate work; they are not provider sampling seeds.

Retain the complete campaign log set, including the builder's work after freeze. Candidates inherit only the prefix through freeze, so candidate-only totals omit the builder's later search/writing/selection. Hash chains and receipt comparisons detect changed or internally inconsistent evidence; they do not authenticate a completely coherent rewritten history or establish semantic fidelity.

### Re-review finding placement

| Finding/disposition affecting the next action | Placement |
|---|---|
| E-B1 resolved; exact historical compatibility, retained pinned ancestors and repaired theta integration | E-B1 resolved; Re-review verification and mutations; Retained limits and next action |
| E-S1 resolved; rich accepted-response/correction binding and integrity limits | E-S1 resolved; Re-review verification and mutations; Retained limits and next action |
| E-S2 resolved; effective compatibility and unchanged writer-override support | E-S2 resolved; Re-review verification and mutations |
| E-S3 resolved; inherited failure/coverage/policy disclosure and separate charges | E-S3 resolved; Re-review verification and mutations |
| Original-builder lifecycle, campaign-log completeness, cache/seed limits and offline scope | Retained limits and next action |

5 findings, 5 placed.

DONE iota rereview eta=merge blocking=0 should_fix=0 tests=513/515 negctl=pass
