# Zeta Codex pilot

**blocked:cli-invalid-schema.** 0 frozen commitments from 0/26 papers; 0 targets; 0/20 completed searches; 0 published routes. Native exit -2. No route selected.

[Open the full-lineage report](/home/dev/ara-work/reports/overnight/codex/report.html). [Structured run audit](/home/dev/ara-scaffold/runs/codex-pilot-control/pilot-audit.json). Prior halted pilot preserved as [zeta-subagent-pilot-4.md](/home/dev/ara-work/reports/zeta-subagent-pilot-4.md).

The native process was stopped on SIGINT after repeated non-retryable `cli_invalid_schema` refusals in `select_t_roots`. Five requests failed; four windows have completed skip receipts, and the fifth was interrupted before its MODEL usage receipt. No commitments were accepted. This is a provider-stage schema blocker, not a subscription limit. The retained diagnostics suppress raw CLI text, so the exact offending schema constraint is not established. No source patch, manual retry, route-summary call or resumed pilot was attempted.

## Methodology and configuration

Extraction: imported Opus 5 results produced via the Anthropic API. Construction and search are configured to request gpt-6-luna through isolated Codex CLI calls using the ChatGPT subscription. Serving model identity is unverified; the requested model flag is not a serving receipt. No new extraction, Claude subscription call, API call, route selection or essay composition was authorized or performed by this pilot.

Search was not reached in this run.

Clean requested revision: `7e5219a837de0ed126c50c2dbbe8dc49036f68e9`. Tau2 approved the provider with no blocking provider finding; the separate OCR confidence finding is outside this run. Omega Rounds 10–12 and Tau2 were read. Their tests are reviewer evidence, not tests rerun by this pilot. The existing literature artifact remains SHA-256 `1a7a409448637bee589f9a401e7da47d8d3b867947d397ee18403996ce74b224`. New OCR repairs were not incorporated.

Config: `runs/inputs/codex-pilot-config.yaml`, copied from pilot 4 and migrated to `codex_cli` / `gpt-6-luna` with no fallback. All schema/stage routing was checked before canary execution. Auth source is exclusively `/home/dev/.config/ara/codex-home/auth.json`; no worker-home auth fallback. Local cap 100,000,000 tokens; catalogue 60,000 tokens; 233 symbol-growth tokens per item; window cap multiplier 2; search/provider concurrency 4; empty audience.

The standalone native canary passed before the pilot; native startup canaries remain logged. Generic built-in tool definitions may be visible and are disclosed; any executed tool or unknown event rejects. Skills, memory and operator instruction content must be absent. Credentials are mounted read-only per call; refresh is disabled. These checks do not establish byte-identical API context or model quality.

Visible definitions in the executed standalone canary: collaboration.followup_task, collaboration.interrupt_agent, collaboration.list_agents, collaboration.send_message, collaboration.spawn_agent, collaboration.wait_agent, functions.exec, functions.wait. Recorded tool events: 0; forbidden-term checks: 51.

The live plan contains 74 funded windows, compared with 70 in Tau2's offline review. Native allocation: 153 global slots, 148 projected commitments, 4 maximum commitments per window. This is an allocation, not a prediction of accepted output.

The first live canary measured 4323 input tokens against an initial-context estimate of 1488; native runtime overhead rose from 949 to 3974 tokens. The higher live estimate changed window partitioning. Requested caps were retained; no offline plan was substituted for live admission.

## Frozen T and construction

Freeze count 0; path `none`; SHA-256 `none`.
No frozen T exists; 0 provisional commitments remain in native batch artifacts.

| Paper | Frozen commitments |
|---|---|
| vonfintelgillies2007 | 0 |
| eganweatherson2011 | 0 |
| vonfintelgillies2011 | 0 |
| wright2007 | 0 |
| schaffer2011 | 0 |
| braun2012 | 0 |
| eganhawthorneweatherson2005 | 0 |
| egan2007 | 0 |
| macfarlane2011 | 0 |
| yalcin2007 | 0 |
| yalcin2011 | 0 |
| rothschild2012 | 0 |
| moss2015 | 0 |
| hawkesteinertthrelkeld2021 | 0 |
| veltman1996 | 0 |
| gsv1996 | 0 |
| willer2013 | 0 |
| ninan2018 | 0 |
| beddorgoldstein2021 | 0 |
| hollidaymandelkern2024 | 0 |
| kolodnymacfarlane2010 | 0 |
| knobeyalcin2014 | 0 |
| klinedinstrothschild2012 | 0 |
| bledin2014 | 0 |
| yalcin2015 | 0 |
| macfarlane2014 | 0 |

None recorded.

Window indices are zero-based. Retained closure items in a skipped window did not enter T.

| Window | Papers | Roots | Uncut | Retained | Accepted commitments | Outcome/reason |
|---|---|---|---|---|---|---|
| 0 | beddorgoldstein2021 | 0 | 0 | 0 | 0 | cli_invalid_schema |
| 1 | beddorgoldstein2021, bledin2014 | 0 | 0 | 0 | 0 | cli_invalid_schema |
| 2 | bledin2014, braun2012 | 0 | 0 | 0 | 0 | cli_invalid_schema |
| 3 | braun2012 | 0 | 0 | 0 | 0 | cli_invalid_schema |
| 4 | braun2012, egan2007 | 0 | 0 | 0 | 0 | Attempted; no completed acceptance/skip receipt before halt |
| 5 | egan2007 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 6 | egan2007, eganhawthorneweatherson2005 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 7 | eganhawthorneweatherson2005 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 8 | eganhawthorneweatherson2005, eganweatherson2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 9 | eganweatherson2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 10 | eganweatherson2011, gsv1996 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 11 | gsv1996 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 12 | gsv1996 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 13 | gsv1996, hawkesteinertthrelkeld2021 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 14 | hawkesteinertthrelkeld2021 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 15 | hawkesteinertthrelkeld2021, hollidaymandelkern2024 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 16 | hollidaymandelkern2024 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 17 | hollidaymandelkern2024 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 18 | hollidaymandelkern2024 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 19 | hollidaymandelkern2024 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 20 | hollidaymandelkern2024, klinedinstrothschild2012 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 21 | klinedinstrothschild2012 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 22 | klinedinstrothschild2012, knobeyalcin2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 23 | knobeyalcin2014, kolodnymacfarlane2010 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 24 | kolodnymacfarlane2010, macfarlane2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 25 | macfarlane2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 26 | macfarlane2011, macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 27 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 28 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 29 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 30 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 31 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 32 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 33 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 34 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 35 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 36 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 37 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 38 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 39 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 40 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 41 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 42 | macfarlane2014 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 43 | macfarlane2014, moss2015 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 44 | moss2015 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 45 | moss2015 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 46 | moss2015 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 47 | moss2015 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 48 | moss2015, ninan2018 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 49 | ninan2018 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 50 | ninan2018 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 51 | ninan2018, rothschild2012 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 52 | rothschild2012, schaffer2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 53 | schaffer2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 54 | schaffer2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 55 | schaffer2011, veltman1996 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 56 | veltman1996 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 57 | veltman1996 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 58 | veltman1996, vonfintelgillies2007 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 59 | vonfintelgillies2007 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 60 | vonfintelgillies2007 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 61 | vonfintelgillies2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 62 | vonfintelgillies2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 63 | vonfintelgillies2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 64 | vonfintelgillies2011, willer2013 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 65 | willer2013 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 66 | willer2013, wright2007 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 67 | wright2007, yalcin2007 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 68 | yalcin2007 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 69 | yalcin2007, yalcin2011 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 70 | yalcin2011, yalcin2015 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 71 | yalcin2015 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 72 | yalcin2015 | 0 | 0 | 0 | 0 | not processed before run stopped |
| 73 | yalcin2015 | 0 | 0 | 0 | 0 | not processed before run stopped |

0 frozen commitments explicitly carry support_omitted; these are assumptions at recorded frontiers, not proofs of omitted support.

None recorded.

## Targets, searches and routes

Target prose and route summaries below are model-written. Prose/formula correspondence has not been independently validated.

None recorded.

Native search phase: {"status": "not_recorded", "jobs": [], "failed_job_indices": [], "cancelled_job_indices": [], "retried_job_indices": [], "incomplete_analyses": [], "note": "Only completed searches supply routes. Missing polarity or failed analysis is not evidence of no conflicts."}

None recorded.

OPEN is not a proof. CLOSED is relative to formalized T and licensed steps. Missing polarity/paired analysis is not evidence of no conflicts. Proof depth differs from the state-ancestry depth in the native tree view.

None recorded.

## Usage, limits, refusals and timing

654,670 local recorded/reserved tokens including standalone preflight and summaries when present; 7 pilot dispatches;
7 model receipts including cache replays; 0.0 new API USD. Codex USD equivalent is **unavailable**, not measured zero.
4 unknown-usage receipts reserve 638,744 tokens already included above; their actual usage remains unknown.

Measured usage is 15,926 tokens. Standalone preflight adds 1 dispatch to the 7 native pilot dispatches.

A further 127,480 tokens are reserved by dispatched calls without MODEL settlement receipts. Including these outstanding reservations gives 782,150 conservative local tokens. They are not measured actual usage and are not silently added to the native receipt totals.

Unsettled call evidence: [{"call_id": "e2b891fb-e85c-4da4-a7ca-994d9cab01d3", "kind": "select_t_roots", "reserved_usage": {"cache_read_tokens": 0, "cache_write_tokens": 0, "input_tokens": 94712, "output_tokens": 32768, "server_tool_uses": 0}}]

Pilot-only local tokens: 649,802; imported historical tokens: 11,348,025. Imported history is reported separately from the local subscription cap.

| Stage | Receipts | Input | Output | Cache read | Cache write | Summed call seconds |
|---|---|---|---|---|---|---|
| isolation_canary | 2 | 8646 | 2412 | 0 | 0 | 46.054 |
| select_t_roots | 4 | 507672 | 131072 | 0 | 0 | 42.389 |

Standalone preflight accounting: {"calls": 1, "api_usd": "0.0", "subscription_equivalent_usd": null, "subscription_equivalent_unavailable_calls": 1, "tokens": {"input_tokens": 4325, "output_tokens": 543, "cache_read_tokens": 0, "cache_write_tokens": 0, "server_tool_uses": 0}, "summed_call_wall_seconds": 7.076334130950272, "unknown_calls": 0, "unknown_usage_reserved_tokens": 0}

Subscription-limit/watch receipts: {"subscription_equivalent_usd": null, "subscription_usd_equivalent_unavailable_calls": 6, "subscription_limit_occurrences": [], "subscription_waits": [], "subscription_wait_seconds": 0, "subscription_limit_active_since": null, "subscription_limit_elapsed_seconds": 0}

Admission begins with Anthropic-tokenizer calibration and adjusts upward from Codex usage; it is not a proven Codex token bound. Configured output allowances are admission reservations: the CLI has no hard output-token cap, so measured excess can stop the run after a response. The nominal 70k input + 64k output + 60k catalogue arithmetic does not override live admission.

None recorded.

| Timestamp | Stage | Refusal/retry/stop payload |
|---|---|---|
| 2026-10-26T03:40:01.268596+00:00 | provider_error | {"cli": {"error_category": "schema", "exit_status": 1, "failure_class": "cli_invalid_schema", "requested_model": "gpt-6-luna", "retryable": false, "served_model": null, "stderr_bytes": 193, "version": "codex-cli 0.163.0", "wall_seconds": 2.358295480022207, "warning_events": 1}, "error_type": "cli_invalid_schema", "kind": "select_t_roots", "message": "CLI diagnostic suppressed.", "provider": "codex_cli", "retryable": false} |
| 2026-10-26T03:40:04.648944+00:00 | select_t_roots | {"accounting": "reservation_unknown_actual", "attempt": 1, "auth_mode": "chatgpt", "auth_threat_model": "Linux mount/PID namespace hides operator homes; auth writes denied; refresh endpoint disabled; no credential rotation.", "auth_transport": "Per-call read-only bind of current host auth file, linked from temporary in-memory CODEX_HOME; no credential copy.", "cache_hit": false, "cache_key": "b9100625726ef37a3ee3a0079a16e990beccd51ce75ecf9470a90094caa84fee", "calibration": {"correction": "like-for-like; single-turn input versus initial, otherwise aggregate versus aggregate; run-local upward only; old observations excluded", "factors": {"build_t_batch": 0.553224, "propose_targets": 0.486932, "select_t_roots": 0.551583}, "fallback_factor": 0.553224, "observation_version": "like-for-like-v2", "runtime_overhead_current": 3974, "runtime_overhead_tokens": 949, "sha256": "7474c9e793c07eb37cc7dd59885b71ba6ab247845b91efdef6509449fe1100ea", "version": "claude-code-input-v1"}, "call_id": "108d482b-1c82-4f7a-878e-0e5b9a02642f", "cli": {"error_category": "schema", "exit_status": 1, "failure_class": "cli_invalid_schema", "requested_model": "gpt-6-luna", "retryable": false, "served_model": null, "stderr_bytes": 193, "version": "codex-cli 0.163.0", "wall_seconds": 2.358295480022207, "warning_events": 1}, "cli_version": "codex-cli 0.163.0", "concurrency": 4, "credential_output_scan": "raw and recursive decoded strings, including cache replay", "dispatch_stage": "select_t_roots", "effective_prompt_note": "Minimal task-only model instructions replace coding-agent defaults; stage developer instructions and native stage prompt retained; not API byte-identical.", "effort": "high", "fresh_cwd_and_config": true, "host_context_isolation": "Home directories and host /tmp /run hidden; fresh HOME and CODEX_HOME; project docs disabled; user config ignored.", "isolation_flags": ["--ephemeral", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check", "--json", "-s", "read-only", "-c", "approval_policy=\"never\"", "-c", "suppress_unstable_features_warning=true", "-c", "project_doc_max_bytes=0", "-c", "web_search=\"disabled\"", "-c", "mcp_servers={}", "-c", "memories.use_memories=false", "-c", "memories.generate_memories=false", "-c", "skills.bundled.enabled=false", "-c", "skills.include_instructions=false", "-c", "features.skip_host_skill_discovery=true", "-c", "tools.update_plan.enabled=false", "-c", "tools.experimental_request_user_input.enabled=false", "-c", "analytics.enabled=false", "-c", "feedback.enabled=false", "-c", "history.persistence=\"none\"", "-c", "cli_auth_credentials_store=\"file\"", "-c", "features.shell_tool=false", "-c", "features.unified_exec=false", "-c", "features.shell_snapshot=false", "-c", "features.apps=false", "-c", "features.plugins=false", "-c", "features.hooks=false", "-c", "features.memories=false", "-c", "features.goals=false", "-c", "features.multi_agent=false", "-c", "features.multi_agent_v2=false", "-c", "features.browser_use=false", "-c", "features.computer_use=false", "-c", "features.image_generation=false", "-c", "features.view_image=false", "-c", "features.skill_search=false", "-c", "features.sleep_tool=false", "-c", "features.workspace_dependencies=false"], "max_cli_turns": 1, "operator_identity_output_scan": true, "output_bound_note": "Admission reserves the configured output allowance twice; CLI has no hard output-token flag. Actual usage can stop the run after receipt.", "provider": "codex_cli", "reason": "CodexCLIError", "requested_model": "gpt-6-luna", "schema_transport": "Stage schema passed to --output-schema; local Draft202012Validator authoritative.", "served_model_policy": "CLI model event when reported; otherwise explicitly unverified, never inferred from -m.", "status": "incomplete", "subscription_cost_note": "Codex JSON reports tokens, not list-price USD; cost equivalent unavailable, never treated as measured zero.", "system_prompt": "", "thinking": "adaptive", "token_cap_policy": "local_run_usage; imported history retained separately", "token_estimate_method": "API-receipt UTF-8 calibration seed; different Codex tokenizer; upward-only like-for-like correction; no free counter", "tokenizer_note": "Seed table measured Anthropic API tokens, not the Codex tokenizer. Codex usage corrects estimates upward only.", "usd_cap_policy": "not_applicable_subscription", "visible_tool_policy": "Generic built-in definitions may be visible; visible definitions do not authorize use; any tool event rejects the response.", "web_retrieval": "disabled; search_evidence refuses"} |
| 2026-10-26T03:40:33.946049+00:00 | provider_error | {"cli": {"error_category": "schema", "exit_status": 1, "failure_class": "cli_invalid_schema", "requested_model": "gpt-6-luna", "retryable": false, "served_model": null, "stderr_bytes": 193, "version": "codex-cli 0.163.0", "wall_seconds": 1.4497012519277632, "warning_events": 1}, "error_type": "cli_invalid_schema", "kind": "select_t_roots", "message": "CLI diagnostic suppressed.", "provider": "codex_cli", "retryable": false} |
| 2026-10-26T03:40:36.856118+00:00 | select_t_roots | {"accounting": "reservation_unknown_actual", "attempt": 1, "auth_mode": "chatgpt", "auth_threat_model": "Linux mount/PID namespace hides operator homes; auth writes denied; refresh endpoint disabled; no credential rotation.", "auth_transport": "Per-call read-only bind of current host auth file, linked from temporary in-memory CODEX_HOME; no credential copy.", "cache_hit": false, "cache_key": "f4520384c31cc7149bea3e30450d58caba078125b5a4fbe5caf5958f3d7a81d8", "calibration": {"correction": "like-for-like; single-turn input versus initial, otherwise aggregate versus aggregate; run-local upward only; old observations excluded", "factors": {"build_t_batch": 0.553224, "propose_targets": 0.486932, "select_t_roots": 0.551583}, "fallback_factor": 0.553224, "observation_version": "like-for-like-v2", "runtime_overhead_current": 3974, "runtime_overhead_tokens": 949, "sha256": "7474c9e793c07eb37cc7dd59885b71ba6ab247845b91efdef6509449fe1100ea", "version": "claude-code-input-v1"}, "call_id": "270fec30-d706-4c97-8585-cded69f553e8", "cli": {"error_category": "schema", "exit_status": 1, "failure_class": "cli_invalid_schema", "requested_model": "gpt-6-luna", "retryable": false, "served_model": null, "stderr_bytes": 193, "version": "codex-cli 0.163.0", "wall_seconds": 1.4497012519277632, "warning_events": 1}, "cli_version": "codex-cli 0.163.0", "concurrency": 4, "credential_output_scan": "raw and recursive decoded strings, including cache replay", "dispatch_stage": "select_t_roots", "effective_prompt_note": "Minimal task-only model instructions replace coding-agent defaults; stage developer instructions and native stage prompt retained; not API byte-identical.", "effort": "high", "fresh_cwd_and_config": true, "host_context_isolation": "Home directories and host /tmp /run hidden; fresh HOME and CODEX_HOME; project docs disabled; user config ignored.", "isolation_flags": ["--ephemeral", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check", "--json", "-s", "read-only", "-c", "approval_policy=\"never\"", "-c", "suppress_unstable_features_warning=true", "-c", "project_doc_max_bytes=0", "-c", "web_search=\"disabled\"", "-c", "mcp_servers={}", "-c", "memories.use_memories=false", "-c", "memories.generate_memories=false", "-c", "skills.bundled.enabled=false", "-c", "skills.include_instructions=false", "-c", "features.skip_host_skill_discovery=true", "-c", "tools.update_plan.enabled=false", "-c", "tools.experimental_request_user_input.enabled=false", "-c", "analytics.enabled=false", "-c", "feedback.enabled=false", "-c", "history.persistence=\"none\"", "-c", "cli_auth_credentials_store=\"file\"", "-c", "features.shell_tool=false", "-c", "features.unified_exec=false", "-c", "features.shell_snapshot=false", "-c", "features.apps=false", "-c", "features.plugins=false", "-c", "features.hooks=false", "-c", "features.memories=false", "-c", "features.goals=false", "-c", "features.multi_agent=false", "-c", "features.multi_agent_v2=false", "-c", "features.browser_use=false", "-c", "features.computer_use=false", "-c", "features.image_generation=false", "-c", "features.view_image=false", "-c", "features.skill_search=false", "-c", "features.sleep_tool=false", "-c", "features.workspace_dependencies=false"], "max_cli_turns": 1, "operator_identity_output_scan": true, "output_bound_note": "Admission reserves the configured output allowance twice; CLI has no hard output-token flag. Actual usage can stop the run after receipt.", "provider": "codex_cli", "reason": "CodexCLIError", "requested_model": "gpt-6-luna", "schema_transport": "Stage schema passed to --output-schema; local Draft202012Validator authoritative.", "served_model_policy": "CLI model event when reported; otherwise explicitly unverified, never inferred from -m.", "status": "incomplete", "subscription_cost_note": "Codex JSON reports tokens, not list-price USD; cost equivalent unavailable, never treated as measured zero.", "system_prompt": "", "thinking": "adaptive", "token_cap_policy": "local_run_usage; imported history retained separately", "token_estimate_method": "API-receipt UTF-8 calibration seed; different Codex tokenizer; upward-only like-for-like correction; no free counter", "tokenizer_note": "Seed table measured Anthropic API tokens, not the Codex tokenizer. Codex usage corrects estimates upward only.", "usd_cap_policy": "not_applicable_subscription", "visible_tool_policy": "Generic built-in definitions may be visible; visible definitions do not authorize use; any tool event rejects the response.", "web_retrieval": "disabled; search_evidence refuses"} |
| 2026-10-26T03:41:04.811816+00:00 | provider_error | {"cli": {"error_category": "schema", "exit_status": 1, "failure_class": "cli_invalid_schema", "requested_model": "gpt-6-luna", "retryable": false, "served_model": null, "stderr_bytes": 193, "version": "codex-cli 0.163.0", "wall_seconds": 1.7624610139755532, "warning_events": 1}, "error_type": "cli_invalid_schema", "kind": "select_t_roots", "message": "CLI diagnostic suppressed.", "provider": "codex_cli", "retryable": false} |
| 2026-10-26T03:41:07.654323+00:00 | select_t_roots | {"accounting": "reservation_unknown_actual", "attempt": 1, "auth_mode": "chatgpt", "auth_threat_model": "Linux mount/PID namespace hides operator homes; auth writes denied; refresh endpoint disabled; no credential rotation.", "auth_transport": "Per-call read-only bind of current host auth file, linked from temporary in-memory CODEX_HOME; no credential copy.", "cache_hit": false, "cache_key": "46e28a822778c4763d09a74a2f7e33c83518cc3c48c41e8744d75f4bfa223a4c", "calibration": {"correction": "like-for-like; single-turn input versus initial, otherwise aggregate versus aggregate; run-local upward only; old observations excluded", "factors": {"build_t_batch": 0.553224, "propose_targets": 0.486932, "select_t_roots": 0.551583}, "fallback_factor": 0.553224, "observation_version": "like-for-like-v2", "runtime_overhead_current": 3974, "runtime_overhead_tokens": 949, "sha256": "7474c9e793c07eb37cc7dd59885b71ba6ab247845b91efdef6509449fe1100ea", "version": "claude-code-input-v1"}, "call_id": "af1ac1aa-fe9f-48a2-9168-7c992d4cd2b2", "cli": {"error_category": "schema", "exit_status": 1, "failure_class": "cli_invalid_schema", "requested_model": "gpt-6-luna", "retryable": false, "served_model": null, "stderr_bytes": 193, "version": "codex-cli 0.163.0", "wall_seconds": 1.7624610139755532, "warning_events": 1}, "cli_version": "codex-cli 0.163.0", "concurrency": 4, "credential_output_scan": "raw and recursive decoded strings, including cache replay", "dispatch_stage": "select_t_roots", "effective_prompt_note": "Minimal task-only model instructions replace coding-agent defaults; stage developer instructions and native stage prompt retained; not API byte-identical.", "effort": "high", "fresh_cwd_and_config": true, "host_context_isolation": "Home directories and host /tmp /run hidden; fresh HOME and CODEX_HOME; project docs disabled; user config ignored.", "isolation_flags": ["--ephemeral", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check", "--json", "-s", "read-only", "-c", "approval_policy=\"never\"", "-c", "suppress_unstable_features_warning=true", "-c", "project_doc_max_bytes=0", "-c", "web_search=\"disabled\"", "-c", "mcp_servers={}", "-c", "memories.use_memories=false", "-c", "memories.generate_memories=false", "-c", "skills.bundled.enabled=false", "-c", "skills.include_instructions=false", "-c", "features.skip_host_skill_discovery=true", "-c", "tools.update_plan.enabled=false", "-c", "tools.experimental_request_user_input.enabled=false", "-c", "analytics.enabled=false", "-c", "feedback.enabled=false", "-c", "history.persistence=\"none\"", "-c", "cli_auth_credentials_store=\"file\"", "-c", "features.shell_tool=false", "-c", "features.unified_exec=false", "-c", "features.shell_snapshot=false", "-c", "features.apps=false", "-c", "features.plugins=false", "-c", "features.hooks=false", "-c", "features.memories=false", "-c", "features.goals=false", "-c", "features.multi_agent=false", "-c", "features.multi_agent_v2=false", "-c", "features.browser_use=false", "-c", "features.computer_use=false", "-c", "features.image_generation=false", "-c", "features.view_image=false", "-c", "features.skill_search=false", "-c", "features.sleep_tool=false", "-c", "features.workspace_dependencies=false"], "max_cli_turns": 1, "operator_identity_output_scan": true, "output_bound_note": "Admission reserves the configured output allowance twice; CLI has no hard output-token flag. Actual usage can stop the run after receipt.", "provider": "codex_cli", "reason": "CodexCLIError", "requested_model": "gpt-6-luna", "schema_transport": "Stage schema passed to --output-schema; local Draft202012Validator authoritative.", "served_model_policy": "CLI model event when reported; otherwise explicitly unverified, never inferred from -m.", "status": "incomplete", "subscription_cost_note": "Codex JSON reports tokens, not list-price USD; cost equivalent unavailable, never treated as measured zero.", "system_prompt": "", "thinking": "adaptive", "token_cap_policy": "local_run_usage; imported history retained separately", "token_estimate_method": "API-receipt UTF-8 calibration seed; different Codex tokenizer; upward-only like-for-like correction; no free counter", "tokenizer_note": "Seed table measured Anthropic API tokens, not the Codex tokenizer. Codex usage corrects estimates upward only.", "usd_cap_policy": "not_applicable_subscription", "visible_tool_policy": "Generic built-in definitions may be visible; visible definitions do not authorize use; any tool event rejects the response.", "web_retrieval": "disabled; search_evidence refuses"} |
| 2026-10-26T03:41:34.797204+00:00 | provider_error | {"cli": {"error_category": "schema", "exit_status": 1, "failure_class": "cli_invalid_schema", "requested_model": "gpt-6-luna", "retryable": false, "served_model": null, "stderr_bytes": 193, "version": "codex-cli 0.163.0", "wall_seconds": 1.4204719919944182, "warning_events": 1}, "error_type": "cli_invalid_schema", "kind": "select_t_roots", "message": "CLI diagnostic suppressed.", "provider": "codex_cli", "retryable": false} |
| 2026-10-26T03:41:37.545326+00:00 | select_t_roots | {"accounting": "reservation_unknown_actual", "attempt": 1, "auth_mode": "chatgpt", "auth_threat_model": "Linux mount/PID namespace hides operator homes; auth writes denied; refresh endpoint disabled; no credential rotation.", "auth_transport": "Per-call read-only bind of current host auth file, linked from temporary in-memory CODEX_HOME; no credential copy.", "cache_hit": false, "cache_key": "0af3c7f6ade7e7c4378c99017fd6b37f3b59c90f6a5b9937550fc25056fb531c", "calibration": {"correction": "like-for-like; single-turn input versus initial, otherwise aggregate versus aggregate; run-local upward only; old observations excluded", "factors": {"build_t_batch": 0.553224, "propose_targets": 0.486932, "select_t_roots": 0.551583}, "fallback_factor": 0.553224, "observation_version": "like-for-like-v2", "runtime_overhead_current": 3974, "runtime_overhead_tokens": 949, "sha256": "7474c9e793c07eb37cc7dd59885b71ba6ab247845b91efdef6509449fe1100ea", "version": "claude-code-input-v1"}, "call_id": "4c76b135-3ad6-4a7c-9eba-ff1c6b9c5918", "cli": {"error_category": "schema", "exit_status": 1, "failure_class": "cli_invalid_schema", "requested_model": "gpt-6-luna", "retryable": false, "served_model": null, "stderr_bytes": 193, "version": "codex-cli 0.163.0", "wall_seconds": 1.4204719919944182, "warning_events": 1}, "cli_version": "codex-cli 0.163.0", "concurrency": 4, "credential_output_scan": "raw and recursive decoded strings, including cache replay", "dispatch_stage": "select_t_roots", "effective_prompt_note": "Minimal task-only model instructions replace coding-agent defaults; stage developer instructions and native stage prompt retained; not API byte-identical.", "effort": "high", "fresh_cwd_and_config": true, "host_context_isolation": "Home directories and host /tmp /run hidden; fresh HOME and CODEX_HOME; project docs disabled; user config ignored.", "isolation_flags": ["--ephemeral", "--ignore-user-config", "--ignore-rules", "--skip-git-repo-check", "--json", "-s", "read-only", "-c", "approval_policy=\"never\"", "-c", "suppress_unstable_features_warning=true", "-c", "project_doc_max_bytes=0", "-c", "web_search=\"disabled\"", "-c", "mcp_servers={}", "-c", "memories.use_memories=false", "-c", "memories.generate_memories=false", "-c", "skills.bundled.enabled=false", "-c", "skills.include_instructions=false", "-c", "features.skip_host_skill_discovery=true", "-c", "tools.update_plan.enabled=false", "-c", "tools.experimental_request_user_input.enabled=false", "-c", "analytics.enabled=false", "-c", "feedback.enabled=false", "-c", "history.persistence=\"none\"", "-c", "cli_auth_credentials_store=\"file\"", "-c", "features.shell_tool=false", "-c", "features.unified_exec=false", "-c", "features.shell_snapshot=false", "-c", "features.apps=false", "-c", "features.plugins=false", "-c", "features.hooks=false", "-c", "features.memories=false", "-c", "features.goals=false", "-c", "features.multi_agent=false", "-c", "features.multi_agent_v2=false", "-c", "features.browser_use=false", "-c", "features.computer_use=false", "-c", "features.image_generation=false", "-c", "features.view_image=false", "-c", "features.skill_search=false", "-c", "features.sleep_tool=false", "-c", "features.workspace_dependencies=false"], "max_cli_turns": 1, "operator_identity_output_scan": true, "output_bound_note": "Admission reserves the configured output allowance twice; CLI has no hard output-token flag. Actual usage can stop the run after receipt.", "provider": "codex_cli", "reason": "CodexCLIError", "requested_model": "gpt-6-luna", "schema_transport": "Stage schema passed to --output-schema; local Draft202012Validator authoritative.", "served_model_policy": "CLI model event when reported; otherwise explicitly unverified, never inferred from -m.", "status": "incomplete", "subscription_cost_note": "Codex JSON reports tokens, not list-price USD; cost equivalent unavailable, never treated as measured zero.", "system_prompt": "", "thinking": "adaptive", "token_cap_policy": "local_run_usage; imported history retained separately", "token_estimate_method": "API-receipt UTF-8 calibration seed; different Codex tokenizer; upward-only like-for-like correction; no free counter", "tokenizer_note": "Seed table measured Anthropic API tokens, not the Codex tokenizer. Codex usage corrects estimates upward only.", "usd_cap_policy": "not_applicable_subscription", "visible_tool_policy": "Generic built-in definitions may be visible; visible definitions do not authorize use; any tool event rejects the response.", "web_retrieval": "disabled; search_evidence refuses"} |
| 2026-10-26T03:42:06.253637+00:00 | provider_error | {"cli": {"error_category": "schema", "exit_status": 1, "failure_class": "cli_invalid_schema", "requested_model": "gpt-6-luna", "retryable": false, "served_model": null, "stderr_bytes": 193, "version": "codex-cli 0.163.0", "wall_seconds": 2.3975211440119892, "warning_events": 1}, "error_type": "cli_invalid_schema", "kind": "select_t_roots", "message": "CLI diagnostic suppressed.", "provider": "codex_cli", "retryable": false} |

| Stage interval | Seconds |
|---|---|
| startup_and_plan | 1493.10064 |
| construction_after_plan | None |
| construction_until_interruption | 184.294173 |
| target_proposal | None |
| search_publication | None |
| search_through_saved_analyses | None |
| route_summaries | None |

Native command wall time: 1730.211 seconds. Summed call time is distinct from elapsed concurrent wall time.

## Report verification and preserved history

Native ara report covers 37 inputs. Copied 27,470 files / 3,218,260,523 bytes with matching SHA-256 hashes, including all linked sidecars.
HTML: 1,069,578 bytes (1.069578 decimal MB). Opened the delivered file in Chromium 143.0.7499.4;
3,072 links/anchors checked; 0 broken links. Desktop/mobile overflow check: False.

Desktop viewport/document widths are 1440/1440 pixels; mobile widths are 390/409 pixels. The mobile document overflows by 19 pixels. Native HTML bytes were preserved; this rendering limitation is unresolved. No page errors or missing anchors were recorded.

Expanded-tree browser receipt: {"passed": true, "scope": "Historical pilot 2 evidence only; Codex pilot has no native tree preview", "current_pilot_search_details": 0, "expanded_search": "Search c94a9b5ddffe:1", "run_index": 30, "proof_nodes": 25, "state_depth": 11, "proof_depth": 5, "linked_files": [{"path": "trees/run-30-search-2.json", "bytes": 258629}, {"path": "trees/run-30-search-2.dot", "bytes": 2805}], "linked_json_opened": true, "dot_valid_header": true, "tree_keys": ["begin_seq", "version", "search_id", "target", "states", "receipts", "decisions", "complete", "authenticated", "source", "issues", "completed_routes", "nodes"], "screenshot": "/home/dev/ara-scaffold/runs/codex-pilot-control/report-expanded-historical-tree.png", "svg_available": false}

Verified 85,037 reconstructed event occurrences, 25,181 unique bodies and 770 artifact copies; input logs/anchors unchanged.

All 157 pilot-4 files matched their pre-run hashes; pilot-3 and pilot-4 handoffs and both configuration files were preserved. Source tree remains clean at 7e5219a837de0ed126c50c2dbbe8dc49036f68e9.

The halted pilot 4 remains preserved. Its native publication was interrupted; unpublished search journals are retained as artifacts, not silently merged into canonical history. Its halt-state accounting includes 1,231 Claude dispatches and 59,590,188 recorded/reserved tokens, including two calls dispatched during shutdown. Those are historical usage, not new Claude calls by this pilot. Earlier extraction gaps, quarantines, omitted material and unknown actual usage remain in prior handoffs and lineage.

## Remaining limits and next step

Before another pilot, the provider owner needs to resolve the native select_t_roots schema rejection and verify that stage through the same Codex transport. The passing canary and earlier formalise/map_leaf smoke did not exercise this construction schema. This run is preserved for diagnosis; no unreviewed provider change or replacement model was used.

Formal schema acceptance and licensed/Z3-checked steps do not establish faithful formalization or true commitments. Paper coverage is not complete extraction. Failed searches, missing summaries and unavailable paired analysis above remain unresolved. No route was selected; operator selection is a separate future instruction. The single frozen T is not rebuilt by a construction resume. No source checks or budgets were weakened to force completion.

## Finding placement

| Finding | Section |
|---|---|
| 1. Outcome, freeze and coverage | Opening; Frozen T and construction |
| 2. Revision, auth, routing, live plan/calibration difference, canary and unverified serving identity | Methodology and configuration |
| 3. Every window, skipped material and omitted support | Frozen T and construction |
| 4. Target/polarity results, route summaries and missing work | Targets, searches and routes |
| 5. Usage, unknowns, output/calibration limits, refusals and timing | Usage, limits, refusals and timing |
| 6. Full-lineage copy, browser/tree proof and rendering limitations | Report verification and preserved history |
| 7. Halted pilot 4 and historical completeness/accounting limits | Report verification and preserved history |
| 8. Semantic limits and no route selection | Remaining limits and next step |

8 findings, 8 placed.

DONE zeta codex-pilot freeze=none commitments=0 papers_in_T=0/26 targets=0 searches_ok=0/20 routes=0 status=blocked:cli-invalid-schema report=/home/dev/ara-work/reports/overnight/codex/report.html
