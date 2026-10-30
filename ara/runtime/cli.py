"""Human entrypoints. Every accepted input is a verbatim timestamped HUMAN event."""
from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path
from typing import Callable

import yaml

from ara.bank import load_bank
from ara.runtime.budget import BudgetStop
from ara.runtime.cache import Cache
from ara.runtime.calls import ModelCalls
from ara.runtime.export import export_run
from ara.runtime.extraction import extract, load_papers, MissingExtractionLineage, resume_papers, validate_failure_limit
from ara.runtime.logging import EventLog, now
from ara.runtime.orchestration import compose, native_engine, prepare, search_all
from ara.runtime.search_publication import search_status
from ara.runtime.providers import AnthropicProvider, MockProvider
from ara.types import RouteGraph
from ara.runtime.route_policy import route_display_status, selectable_routes, frozen_from_events, provenance_from_events

ROOT = Path(__file__).resolve().parents[2]


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='ara')
    sub = p.add_subparsers(dest='command', required=True)
    run = sub.add_parser('run')
    run.add_argument('--config', type=Path, default=ROOT / 'config.yaml')
    run.add_argument('--run-dir', type=Path)
    profile = run.add_mutually_exclusive_group()
    profile.add_argument('--smoke', action='store_true')
    profile.add_argument('--profile', choices=('pilot', 'extraction-full'))
    run.add_argument('--provider', choices=('anthropic', 'mock', 'claude_code', 'codex_cli'))
    run.add_argument('--topic')
    run.add_argument('--literature', type=Path)
    run.add_argument('--audience', default='runtime audience')
    run.add_argument('--named-position')
    run.add_argument('--gap-file', type=Path)
    run.add_argument('--route')
    run.add_argument('--model-context-window', type=int)
    run.add_argument('--context-margin-tokens', type=int)
    fork = sub.add_parser('fork-from-freeze', help='verify and fork a frozen prefix; continue with current target proposal')
    fork.add_argument('--source-run', type=Path, required=True)
    fork.add_argument('--run-dir', type=Path, required=True)
    fork.add_argument('--gap-file', type=Path)
    fork.add_argument('--model-context-window', type=int)
    fork.add_argument('--context-margin-tokens', type=int)
    fork.add_argument('--provider', choices=('anthropic','mock','claude_code','codex_cli'))
    fork.add_argument('--codex-schema-preflight-log', type=Path)
    fork.add_argument('--unknown-usage-policy', choices=('refuse','count-at-reservation'))
    resume = sub.add_parser('resume-construction', help='continue a verified stopped construction in its existing directory')
    resume.add_argument('--run-dir', type=Path, required=True)
    resume.add_argument('--codex-schema-preflight-log', type=Path)
    resume.add_argument('--unknown-usage-policy', choices=('count-at-reservation',), required=True)
    resume.add_argument('--plan-only', action='store_true', help='free counts and verified restoration only; no generation')
    resume.add_argument('--output-dir', type=Path, help='separate empty directory for count-only resume receipts')
    alignment = sub.add_parser('resume-alignment', help='continue unfinished alignment from verified completed construction')
    alignment.add_argument('--run-dir', type=Path, required=True)
    alignment.add_argument('--plan-only', action='store_true', help='verify restoration only; no provider or counter')
    alignment.add_argument('--output-dir', type=Path, help='separate empty directory for free resume receipts')
    alignment.add_argument('--codex-schema-preflight-log', type=Path)
    alignment.add_argument('--unknown-usage-policy', choices=('refuse','count-at-reservation'))
    search_resume = sub.add_parser('resume-search', help='publish verified search journals and continue unfinished jobs')
    search_resume.add_argument('--run-dir', type=Path, required=True)
    search_resume.add_argument('--stop-before-dispatch', action='store_true',
                               help='recover publication/accounting and print the remaining jobs; no provider creation')
    search_resume.add_argument('--codex-schema-preflight-log', type=Path)
    search_resume.add_argument('--unknown-usage-policy', choices=('refuse', 'count-at-reservation'))
    extraction = sub.add_parser('extract')
    extraction.add_argument('--config', type=Path, default=ROOT / 'config.yaml')
    extraction.add_argument('--manifest', type=Path, required=True)
    extraction.add_argument('--fulltext-dir', type=Path, required=True)
    extraction.add_argument('--run-dir', type=Path, required=True)
    extraction.add_argument('--provider', choices=('anthropic', 'mock', 'claude_code', 'codex_cli'))
    extraction.add_argument('--paper-id', action='append', default=[])
    extraction.add_argument('--ocr', choices=('local', 'off'), default='local', help='local OCR fallback on diagnosed pages (default: local)')
    extraction.add_argument('--ocr-tiers', type=int, choices=(1, 2), default=2, help='2 adds local VL fallback after tier-1 rejection')
    extraction.add_argument('--ocr-cache', type=Path, default=Path('cache/ocr'))
    extraction.add_argument('--missing', choices=('record-only', 'refuse'), default='record-only')
    extraction.add_argument('--estimate-only', action='store_true')
    extraction.add_argument('--salvage-only', action='store_true', help='Publish verified accepted ranges without model calls')
    extraction.add_argument('--exclude-paper', action='append', default=[], metavar='ID=REASON')
    extraction.add_argument('--resume-from', type=Path, action='append', default=[])
    extraction.add_argument('--profile', choices=('extraction', 'extraction-full'))
    extraction.add_argument('--unknown-usage-policy', choices=('refuse', 'count-at-reservation'), default='refuse')
    gate = sub.add_parser('schema-preflight')
    gate.add_argument('--config', type=Path, default=ROOT / 'config.yaml')
    gate.add_argument('--run-dir', type=Path, required=True)
    gate.add_argument('--profile', choices=('extraction', 'extraction-full'), default='extraction-full')
    gate.add_argument('--cost-cap-usd', type=float, default=1.0)
    gate.add_argument('--resume-from', type=Path, action='append', default=[])
    gate.add_argument('--unknown-usage-policy', choices=('refuse', 'count-at-reservation'), default='refuse')
    codex_gate = sub.add_parser('codex-schema-preflight')
    codex_gate.add_argument('--config', type=Path, default=ROOT / 'config.yaml')
    codex_gate.add_argument('--run-dir', type=Path, required=True)
    codex_gate.add_argument('--profile', choices=('pilot', 'extraction-full'))
    plan = sub.add_parser('plan-extraction')
    plan.add_argument('--config', type=Path, default=ROOT / 'config.yaml')
    plan.add_argument('--ocr', choices=('local', 'off'), default='local')
    plan.add_argument('--ocr-tiers', type=int, choices=(1, 2), default=2)
    plan.add_argument('--ocr-cache', type=Path, default=Path('cache/ocr'))
    plan.add_argument('--manifest', type=Path, required=True)
    plan.add_argument('--fulltext-dir', type=Path, required=True)
    plan.add_argument('--run-dir', type=Path, required=True)
    plan.add_argument('--paper-id', action='append', default=[])
    plan.add_argument('--profile', choices=('extraction', 'extraction-full'), default='extraction-full')
    plan.add_argument('--token-counter', choices=('local', 'provider'), default='local')
    construction = sub.add_parser('plan-construction', help='count native construction allocation; generation disabled')
    construction.add_argument('--config', type=Path, default=ROOT / 'config.yaml')
    construction.add_argument('--literature', type=Path, required=True)
    construction.add_argument('--topic', required=True)
    construction.add_argument('--audience', default='')
    construction.add_argument('--run-dir', type=Path, required=True)
    construction.add_argument('--profile', choices=('pilot', 'extraction-full'), default='pilot')
    construction.add_argument('--token-counter', choices=('local', 'provider'), default='local')
    target_plan = sub.add_parser('plan-target-request', help='recount a recorded full target request; no generation')
    target_plan.add_argument('--run-dir', type=Path, required=True)
    target_plan.add_argument('--out', type=Path, required=True)
    target_plan.add_argument('--gap-id')
    target_plan.add_argument('--context-token-bound', type=int)
    target_plan.add_argument('--model-context-window', type=int)
    target_plan.add_argument('--context-margin-tokens', type=int)
    target_plan.add_argument('--counter', choices=('provider', 'local'), default='provider')
    report = sub.add_parser('report', help='render verified run receipts offline; no model calls')
    report.add_argument('--run-dir', type=Path, action='append', required=True)
    report.add_argument('--out', type=Path, required=True)
    for command in ('polish', 'figures', 'render-pdf'):
        cmd = sub.add_parser(command)
        cmd.add_argument('--run-dir', type=Path, required=True)
        if command == 'polish':
            cmd.add_argument('--route')
            cmd.add_argument('--draft', type=Path)
            cmd.add_argument('--audit-provider', choices=('claude_code', 'codex_cli'), default='claude_code')
            cmd.add_argument('--audit-model', help='audit model; defaults to the run writer model for Codex')
            cmd.add_argument('--min-words', type=int, help='ARA publication floor; defaults to publication_min_words in the run config or 3000')
            cmd.add_argument('--literature-currency', type=Path, action='append', default=[])
            cmd.add_argument('--unknown-usage-policy', choices=('refuse', 'count-at-reservation'))
    for command in ('select', 'feedback', 'export'):
        cmd = sub.add_parser(command)
        cmd.add_argument('--run-dir', type=Path, required=True)
        if command == 'select':
            cmd.add_argument('--route')
            cmd.add_argument('--draft', type=Path, help='audit an existing unverified draft without generating a new essay')
            cmd.add_argument('--codex-schema-preflight-log', type=Path)
            cmd.add_argument('--unknown-usage-policy', choices=('refuse', 'count-at-reservation'))
        if command == 'feedback':
            cmd.add_argument('--text')
        if command == 'export':
            cmd.add_argument('--output', type=Path)
            cmd.add_argument('--redact', action='append', default=[])
    for cmd in sub.choices.values():
        cmd.add_argument('--human-minutes', type=float, default=0)
    return p


def make_provider(config: dict, root: Path = ROOT):
    if config['provider'] == 'anthropic':
        provider = AnthropicProvider(config)
    elif config['provider'] == 'claude_code':
        from ara.runtime.claude_code import ClaudeCodeProvider
        provider = ClaudeCodeProvider(config)
    elif config['provider'] == 'codex_cli':
        from ara.runtime.codex_cli import CodexCLIProvider
        provider = CodexCLIProvider(config)
    elif config['provider'] == 'mock':
        provider = MockProvider(Path(config.get('mock_responses', root / 'tests/fixtures/runtime/native-canned.json')), config['model'])
    else:
        raise ValueError(f'unknown provider: {config["provider"]}')
    return provider


def make_calls(config: dict, log: EventLog, topic: str, root: Path = ROOT, *, imported_draft=None) -> ModelCalls:
    from ara.runtime.codex_window import apply_context_window
    decision = apply_context_window(config)
    if decision is not None:
        log.record('operator_context_window', **decision)
    return ModelCalls(config, make_provider(config, root), log, Cache(Path(config['cache_dir'])), root, topic,
                      provider_factory=lambda settings: make_provider(settings, root), imported_draft=imported_draft)


def configure_window(config, args):
    from ara.runtime.codex_window import apply_context_window
    if args.model_context_window is not None:
        config['model_context_window'] = args.model_context_window
    if args.context_margin_tokens is not None:
        if args.model_context_window is None and config.get('model_context_window') is None:
            raise ValueError('context margin requires model_context_window')
        config['model_context_margin_tokens'] = args.context_margin_tokens
    return apply_context_window(config)


def apply_profile(config, name):
    profile = config[name]
    stages = {**config.get('stages', {}), **profile.get('stages', {})}
    config.update(profile)
    config['stages'] = stages


def validate_profile_caps(config: dict, profile: str | None) -> None:
    if profile != 'extraction-full':
        return
    missing_caps = [key for key in ('token_cap', 'cost_cap_usd', 'extraction_cost_cap_usd')
                    if config.get(key) is None]
    if missing_caps:
        raise ValueError('operator must set extraction-full caps: ' + ', '.join(missing_caps))


def disclose_search(log):
    status = search_status(log.read())
    if status['status'] == 'partial':
        print(f"Partial search: {len(status['failed_job_indices'])} jobs failed; "
              f"{len(status['incomplete_analyses'])} target analyses incomplete. "
              "Completed routes remain selectable; see methodology for missing work and accounting.",
              file=sys.stderr)
    return status


def main(argv: list[str] | None = None, *, engine_factory: Callable = native_engine,
         calls_factory: Callable = make_calls) -> int:
    raw_args = list(sys.argv[1:] if argv is None else argv)
    args = parser().parse_args(raw_args)
    log = None
    started = time.monotonic()
    human_elapsed = 0.0
    try:
        if args.command == 'plan-target-request':
            from ara.runtime.planning import plan_recorded_target
            report = plan_recorded_target(args.run_dir, args.out, ROOT, gap_id=args.gap_id,
                                          bound=args.context_token_bound, counter=args.counter,
                                          window=args.model_context_window, margin=args.context_margin_tokens)
            print(json.dumps(report, sort_keys=True))
            return 0
        if args.command == 'fork-from-freeze':
            from ara.runtime.freeze_fork import fork_from_freeze
            bank = load_bank(ROOT / 'bank')
            log, run, commitments = fork_from_freeze(args.source_run, args.run_dir, bank)
            config = {**run['config'], 'cache_dir': str(args.run_dir.resolve() / 'cache')}
            if args.gap_file is not None:
                config['gap_file'] = str(args.gap_file.resolve())
            if args.provider is not None:
                config['provider'] = args.provider
            if args.unknown_usage_policy is not None:
                config['unknown_usage_policy'] = args.unknown_usage_policy
            if args.codex_schema_preflight_log is not None:
                config['codex_cli'] = {**config.get('codex_cli', {}), 'schema_preflight_log': str(args.codex_schema_preflight_log)}
            configure_window(config, args)
            log.record('freeze_fork_configuration', config=config)
            log.human('fork-from-freeze', json.dumps(raw_args), reported_minutes=args.human_minutes)
            from ara.runtime.codex_preflight import require_codex_preflight
            require_codex_preflight(config, ROOT)
            calls = calls_factory(config, log, run['topic'])
            targets = calls.propose_targets(commitments, config['target_candidates'])
            log.record('candidates', candidates=[t.to_dict() for t in targets])
            routes = search_all(calls, native_engine(bank,calls), commitments, targets)
            log.record('awaiting_selection', route_ids=[r.id for r in routes], search=disclose_search(log),
                       selectable_route_ids=[r.id for r in selectable_routes(routes, commitments, provenance_from_events(log.read(), commitments))])
            log.record('run_finished', state='awaiting_selection')
            export_run(log.path,args.run_dir/'export')
            print(str(args.run_dir))
            return 0
        if args.command == 'resume-search':
            from ara.runtime.search_resume import load_search_resume, publish_search_resume, search_resume_lock
            if not (args.run_dir / 'events.jsonl').is_file():
                raise ValueError('search run log does not exist')
            with search_resume_lock(args.run_dir):
                source_log = EventLog(args.run_dir / 'events.jsonl')
                bank = load_bank(ROOT / 'bank')
                state = load_search_resume(source_log, bank, ROOT)
                # Verify every input before any canonical append or provider creation.
                log = source_log
                publish_search_resume(log, state)
                log.human('resume-search', json.dumps(raw_args), reported_minutes=args.human_minutes)
                log.record('search_resume_plan', **state.summary())
                if args.stop_before_dispatch or state.already_finished:
                    print(json.dumps(state.summary()))
                    return 0
                config = dict(state.run['config'])
                if args.unknown_usage_policy is not None:
                    config['unknown_usage_policy'] = args.unknown_usage_policy
                if args.codex_schema_preflight_log is not None:
                    config['codex_cli'] = {**config.get('codex_cli', {}),
                        'schema_preflight_log': str(args.codex_schema_preflight_log)}
                from ara.runtime.codex_preflight import require_codex_preflight
                require_codex_preflight(config, ROOT)
                calls = calls_factory(config, log, state.run['topic'])
                engine = engine_factory(bank, calls)
                from ara.runtime.orchestration import NativeEngine
                if not isinstance(engine, NativeEngine):
                    raise ValueError('search resume requires the native engine')
                routes = search_all(calls, engine, state.commitments, state.targets, restored=state.restored)
                log.record('awaiting_selection', route_ids=[r.id for r in routes], search=disclose_search(log))
                log.record('run_finished', state='awaiting_selection')
                print(str(args.run_dir))
                return 0
        if args.command == 'resume-alignment':
            from ara.runtime.alignment_resume import load_alignment_resume, resume_summary
            from ara.runtime.construction_resume import construction_resume_lock
            from ara.runtime.extraction import save_immutable
            from ara.runtime.cache import canonical
            if not (args.run_dir / 'events.jsonl').is_file():
                raise ValueError('alignment run log does not exist')
            if args.plan_only:
                if (args.output_dir is None or args.output_dir.resolve().is_relative_to(args.run_dir.resolve()) or
                        args.run_dir.resolve().is_relative_to(args.output_dir.resolve())):
                    raise ValueError('plan-only alignment resume requires a separate --output-dir')
                if args.output_dir.exists() and any(args.output_dir.iterdir()):
                    raise ValueError('plan-only output directory must be empty')
            elif args.output_dir is not None:
                raise ValueError('--output-dir requires --plan-only')
            with construction_resume_lock(args.run_dir):
                source_log=EventLog(args.run_dir / 'events.jsonl')
                bank=load_bank(ROOT / 'bank')
                state=load_alignment_resume(source_log,bank)
                summary=resume_summary(state)
                if args.plan_only:
                    log=EventLog(args.output_dir / 'events.jsonl')
                    log.human('resume-alignment-plan',json.dumps(raw_args),reported_minutes=args.human_minutes)
                    log.record('alignment_resume_plan',**summary)
                    save_immutable(args.output_dir / 'alignment-resume-plan.json',canonical(summary))
                    print(json.dumps(summary))
                    return 0
                run=state['run']
                config=dict(run['config'])
                if args.unknown_usage_policy is not None:
                    config['unknown_usage_policy']=args.unknown_usage_policy
                if args.codex_schema_preflight_log is not None:
                    config['codex_cli']={**config.get('codex_cli',{}),
                        'schema_preflight_log':str(args.codex_schema_preflight_log)}
                from ara.runtime.codex_preflight import require_codex_preflight
                require_codex_preflight(config,ROOT)
                log=source_log
                log.human('resume-alignment',json.dumps(raw_args),reported_minutes=args.human_minutes)
                log.record('alignment_resumed',**summary,config=config)
                calls=calls_factory(config,log,run['topic'])
                calls.alignment_resume=state
                human=next((json.loads(e['payload_json']) for e in log.read() if e['stage']=='run' and e['label']=='HUMAN'),{})
                commitments,targets=prepare(calls,bank,run['literature'],run['audience'],human.get('named_position'))
                routes=search_all(calls,engine_factory(bank,calls),commitments,targets)
                log.record('awaiting_selection',route_ids=[r.id for r in routes],search=disclose_search(log))
                log.record('run_finished',state='awaiting_selection')
                print(str(args.run_dir))
                return 0
        if args.command == 'resume-construction':
            if not (args.run_dir / 'events.jsonl').is_file():
                raise ValueError('construction run log does not exist')
            if args.plan_only:
                if args.output_dir is None or args.output_dir.resolve().is_relative_to(args.run_dir.resolve()):
                    raise ValueError('plan-only resume requires a separate --output-dir')
                if args.output_dir.exists() and any(args.output_dir.iterdir()):
                    raise ValueError('plan-only output directory must be empty')
            elif args.output_dir is not None:
                raise ValueError('--output-dir requires --plan-only')
            from ara.runtime.construction_resume import construction_resume_lock
            with construction_resume_lock(args.run_dir):
                source_log = EventLog(args.run_dir / 'events.jsonl')
                events = source_log.read()
                starts = [json.loads(e['payload_json']) for e in events if e['stage'] == 'run_started']
                if len(starts) != 1:
                    raise ValueError('construction resume requires one run configuration')
                run = starts[0]
                bank = load_bank(ROOT / 'bank')
                if bank.bank_version != run['bank_version']:
                    raise ValueError('construction resume bank version mismatch')
                config = {**run['config'], 'unknown_usage_policy': args.unknown_usage_policy}
                if args.codex_schema_preflight_log is not None:
                    config['codex_cli'] = {**config.get('codex_cli', {}),
                        'schema_preflight_log': str(args.codex_schema_preflight_log)}
                if args.plan_only:
                    from ara.runtime.planning import plan_construction_resume
                    log = EventLog(args.output_dir / 'events.jsonl')
                    log.human('resume-construction-plan', json.dumps(raw_args), reported_minutes=args.human_minutes)
                    result = plan_construction_resume(config, log, source_log, ROOT, run)
                    print(json.dumps(result))
                    return 0
                from ara.runtime.codex_preflight import require_codex_preflight
                require_codex_preflight(config, ROOT)
                log = source_log
                calls = calls_factory(config, log, run['topic'])
                calls.construction_resume = True
                log.human('resume-construction', json.dumps(raw_args), reported_minutes=args.human_minutes)
                human = next((json.loads(e['payload_json']) for e in events if e['stage'] == 'run' and e['label'] == 'HUMAN'), {})
                commitments, targets = prepare(calls, bank, run['literature'], run['audience'], human.get('named_position'))
                routes = search_all(calls, engine_factory(bank, calls), commitments, targets)
                log.record('awaiting_selection', route_ids=[r.id for r in routes], search=disclose_search(log))
                log.record('run_finished', state='awaiting_selection')
                print(str(args.run_dir))
                return 0
        if args.command == 'report':
            from ara.runtime.report import generate_report
            print(str(generate_report(args.run_dir, args.out)))
            return 0
        if args.command == 'codex-schema-preflight':
            from ara.runtime.codex_preflight import codex_schema_preflight
            config = yaml.safe_load(args.config.read_text())
            if args.profile:
                apply_profile(config, args.profile)
            if args.run_dir.exists() and any(args.run_dir.iterdir()):
                raise ValueError('Codex schema preflight destination must be empty')
            log = EventLog(args.run_dir / 'events.jsonl')
            log.human('codex-schema-preflight', json.dumps(raw_args), reported_minutes=args.human_minutes)
            log.record('codex_schema_preflight_config', config=config)
            result = codex_schema_preflight(calls_factory(config, log, 'P'))
            print(json.dumps(result))
            return 0 if result['passed'] else 2
        if args.command == 'schema-preflight':
            from ara.runtime.preflight import schema_preflight
            from ara.runtime.provenance import checkpoint, read_checkpoint, import_receipts
            if not 0 <= args.cost_cap_usd <= 1:
                raise ValueError('schema preflight cap must be between zero and USD1')
            config = yaml.safe_load(args.config.read_text())
            apply_profile(config, args.profile)
            config.update(cost_cap_usd=args.cost_cap_usd, extraction_cost_cap_usd=args.cost_cap_usd,
                          unknown_usage_policy=args.unknown_usage_policy)
            if args.run_dir.exists() and any(args.run_dir.iterdir()):
                raise ValueError('schema preflight destination must be empty')
            log = EventLog(args.run_dir / 'events.jsonl')
            log.human('schema-preflight', json.dumps(raw_args), argv=raw_args,
                      reported_minutes=args.human_minutes)
            log.record('schema_preflight_config', config=config)
            for source in args.resume_from:
                origin = checkpoint(source / 'events.jsonl')
                import_receipts(log, read_checkpoint(origin), origin)
            calls = calls_factory(config, log, 'P')
            print(json.dumps(schema_preflight(calls)))
            return 0
        if args.command == 'plan-construction':
            from ara.runtime.planning import plan_construction
            config = yaml.safe_load(args.config.read_text())
            apply_profile(config, args.profile)
            if args.run_dir.exists() and any(args.run_dir.iterdir()):
                raise ValueError('new planning directory must be empty')
            log = EventLog(args.run_dir / 'events.jsonl')
            log.human('plan-construction', json.dumps(raw_args), argv=raw_args, reported_minutes=args.human_minutes)
            report = plan_construction(config, log, args.literature.read_text(), ROOT, args.topic,
                                       args.audience, args.token_counter)
            print(json.dumps(report))
            return 0
        if args.command == 'plan-extraction':
            from ara.runtime.planning import plan_extraction
            config = yaml.safe_load(args.config.read_text())
            apply_profile(config, args.profile)
            if args.run_dir.exists() and any(args.run_dir.iterdir()):
                raise ValueError('new planning directory must be empty')
            log = EventLog(args.run_dir / 'events.jsonl')
            log.human('plan-extraction', json.dumps(raw_args), argv=raw_args, reported_minutes=args.human_minutes)
            log.record('extraction_planning_started', config=config, counter=args.token_counter)
            papers = load_papers(args.manifest, args.fulltext_dir, tuple(args.paper_id))
            log.record('extraction_ocr_policy', mode=args.ocr, tiers=args.ocr_tiers)
            if args.ocr == 'local':
                from ara.runtime.ocr import recover_papers
                papers = recover_papers(papers, args.fulltext_dir, log, args.ocr_cache, use_vl=args.ocr_tiers == 2)
            report = plan_extraction(config, log, papers, ROOT, args.token_counter)
            return 2 if report['totals']['refused'] else 0
        if args.command == 'extract':
            config = yaml.safe_load(args.config.read_text())
            if args.profile:
                apply_profile(config, args.profile)
            validate_profile_caps(config, args.profile)
            config['unknown_usage_policy'] = args.unknown_usage_policy
            config.setdefault('validation_attempts', 3)
            validate_failure_limit(config)
            if args.provider:
                config['provider'] = args.provider
            if args.run_dir.exists() and any(args.run_dir.iterdir()):
                raise ValueError('extraction destination must be empty; use --resume-from with a new run directory')
            log = EventLog(args.run_dir / 'events.jsonl')
            log.human('extract', json.dumps(raw_args, ensure_ascii=False), argv=raw_args,
                      manifest=args.manifest.read_text(), reported_minutes=args.human_minutes)
            log.record('extraction_started', config=config, manifest=str(args.manifest.resolve()),
                       fulltext_dir=str(args.fulltext_dir.resolve()), selected=args.paper_id,
                       missing_policy=args.missing, estimate_only=args.estimate_only,
                       tools=['pypdf', 'Anthropic Messages API', 'jsonschema'])
            excluded = {}
            for value in args.exclude_paper:
                source, sep, reason = value.partition('=')
                if not sep or not source or not reason.strip():
                    raise ValueError('--exclude-paper requires ID=REASON')
                excluded[source] = reason
            selected = tuple(dict.fromkeys([*args.paper_id, *excluded])) if args.paper_id else ()
            papers = load_papers(args.manifest, args.fulltext_dir, selected)
            log.record('extraction_ocr_policy', mode=args.ocr, tiers=args.ocr_tiers)
            if args.ocr == 'local':
                from ara.runtime.ocr import recover_papers
                papers = recover_papers(papers, args.fulltext_dir, log, args.ocr_cache, use_vl=args.ocr_tiers == 2)
            if not set(excluded) <= {p.source_id for p in papers}:
                raise ValueError('excluded paper is absent from manifest')
            reused = resume_papers(log, papers, args.resume_from, config, ROOT, revalidate_only=args.salvage_only) if args.resume_from and not args.estimate_only else {}
            if args.salvage_only:
                from ara.runtime.salvage import OfflineExtractionProvider
                calls = ModelCalls(config, OfflineExtractionProvider(config), log, Cache(Path(config['cache_dir'])), ROOT, '')
            else:
                calls = calls_factory(config, log, '')
            path = extract(calls, papers, missing=args.missing, estimate_only=args.estimate_only, reused=reused,
                           salvage_only=args.salvage_only, excluded=excluded)
            if path:
                print(str(path))
            return 0
        if args.command == 'run':
            config = yaml.safe_load(args.config.read_text())
            selected_profile = 'smoke' if args.smoke else args.profile
            if selected_profile:
                apply_profile(config, selected_profile)
            validate_profile_caps(config, selected_profile)
            if args.smoke:
                topic = args.topic if args.topic is not None else 'P Q'
                literature = args.literature.read_text() if args.literature else (
                    ROOT / 'tests/fixtures/runtime/smoke-literature.txt').read_text()
            else:
                if args.topic is None or args.literature is None:
                    raise ValueError('run requires --topic and --literature, or --smoke')
                topic, literature = args.topic, args.literature.read_text()
            if args.gap_file is not None:
                config['gap_file'] = str(args.gap_file.resolve())
            if args.provider is not None:
                config['provider'] = args.provider
            configure_window(config, args)
            from ara.runtime.codex_preflight import require_codex_preflight
            require_codex_preflight(config, ROOT)
            directory = args.run_dir or Path(config['runs_dir']) / uuid.uuid4().hex
            if directory.exists() and any(directory.iterdir()):
                raise ValueError('new run directory must be empty; use select/feedback/export to resume')
            log = EventLog(directory / 'events.jsonl')
            try:
                from ara.runtime.verification import import_literature
                provenance = import_literature(log, args.literature, literature,
                    Path(config['cache_dir']) / 'lineage-verification') if args.literature else ()
            except MissingExtractionLineage as exc:
                log.record('extraction_lineage_missing', reason=str(exc))
                raise
            log.human('run', args.topic if args.topic is not None else json.dumps(raw_args, ensure_ascii=False),
                      argv=raw_args, topic=args.topic,
                      literature=literature if args.literature is not None and not provenance else None,
                      named_position=args.named_position, reported_minutes=args.human_minutes)
            bank = load_bank(ROOT / 'bank')
            log.record('run_started', config=config, topic=topic, literature=literature, audience=args.audience,
                       literature_source='model_extraction' if provenance else ('human_file' if args.literature is not None else 'smoke_fixture'),
                       bank_version=bank.bank_version,
                       architecture='L: versioned bank; T: frozen commitments; H: model cut proposer; '
                       'deterministic engine: licensing, search, conflicts; runtime: effects',
                       tools=['Anthropic Messages API', 'web_search_20260209', 'Z3', 'jsonschema'])
            calls = calls_factory(config, log, topic)
            engine = engine_factory(bank, calls)
            commitments, targets = prepare(calls, bank, literature, args.audience, args.named_position)
            routes = search_all(calls, engine, commitments, targets)
            search_info = disclose_search(log)
            route_id = args.route
            if route_id:
                log.human('select', route_id, source='run --route')
            elif args.smoke:
                route_id = next((r.id for r in selectable_routes(routes, commitments, provenance_from_events(log.read(), commitments))), None)
                log.record('selection', route_id=route_id, policy='smoke: first CLOSED-derived route only')
            if route_id:
                chosen = next((r for r in routes if r.id == route_id), None)
                if chosen is None:
                    raise ValueError('unknown route id')
                compose(calls, chosen)
            else:
                log.record('awaiting_selection', route_ids=[r.id for r in routes], search=search_info)
            log.record('run_finished', state='complete' if route_id else 'awaiting_selection')
            export_run(log.path, directory / 'export')
            print(str(directory))
            return 0
        if not (args.run_dir / 'events.jsonl').is_file():
            raise ValueError('run log does not exist')
        log = EventLog(args.run_dir / 'events.jsonl')
        log.human(args.command + '_command', json.dumps(raw_args, ensure_ascii=False),
                  argv=raw_args, reported_minutes=args.human_minutes)
        if args.command in ('polish', 'figures', 'render-pdf'):
            from ara.runtime.publication import publication_command
            return publication_command(args, log, ROOT, calls_factory)
        if args.command == 'feedback':
            start = time.monotonic()
            text = args.text if args.text is not None else input('Feedback: ')
            elapsed = time.monotonic() - start if args.text is None else 0
            human_elapsed += elapsed
            log.human('feedback', text, elapsed_seconds=elapsed)
            return 0
        if args.command == 'export':
            report, essay = export_run(log.path, args.output or args.run_dir / 'export', tuple(args.redact))
            print(str(report))
            if essay:
                print(str(essay))
            return 0
        events = log.read()
        commitments = frozen_from_events(events)
        routes = [RouteGraph.from_dict(json.loads(e['payload_json'])['graph'])
                  for e in events if e['stage'] == 'route']
        for route in routes:
            print(f'{route.id} [{route_display_status(route, commitments, provenance_from_events(events, commitments))}]' +
                  (' selectable' if route in selectable_routes(routes, commitments, provenance_from_events(log.read(), commitments)) else ' disclosed; explicit --route required'))
        offered = selectable_routes(routes, commitments, provenance_from_events(log.read(), commitments))
        if args.route is None and not offered:
            print('No CLOSED-derived routes available for selection.')
            return 0
        start = time.monotonic()
        route_id = args.route if args.route is not None else input('Route id: ')
        elapsed = time.monotonic() - start if args.route is None else 0
        human_elapsed += elapsed
        log.human('select', route_id, elapsed_seconds=elapsed)
        chosen = next((r for r in (routes if args.route is not None else offered) if r.id == route_id), None)
        if chosen is None:
            raise ValueError('unknown route id')
        from ara.runtime.freeze_fork import effective_run
        run = effective_run(events)
        selection_config = dict(run['config'])
        if args.codex_schema_preflight_log is not None:
            selection_config['codex_cli'] = {**selection_config.get('codex_cli', {}),
                'schema_preflight_log': str(args.codex_schema_preflight_log)}
        if args.unknown_usage_policy is not None:
            selection_config['unknown_usage_policy'] = args.unknown_usage_policy
        from ara.runtime.codex_preflight import require_codex_preflight
        require_codex_preflight(selection_config, ROOT)
        calls = calls_factory(selection_config, log, run['topic'])
        draft = json.loads(args.draft.read_text()) if args.draft is not None else None
        compose(calls, chosen, draft)
        return 0
    except Exception as exc:
        from anthropic import APIError
        if isinstance(exc, APIError):
            from ara.runtime.providers import provider_error_evidence
            evidence = provider_error_evidence(exc)
            if log is not None:
                log.record('provider_error', **evidence)
            exc = RuntimeError(json.dumps(evidence))
        if log is not None:
            if not isinstance(exc, BudgetStop):
                log.record('runtime_error', error_type=type(exc).__name__, message=str(exc))
            # Methodology and partial graphs survive even a clean budget stop.
            export_run(log.path, log.path.parent / 'export', strict=False)
        print(f'ara: {exc}', file=sys.stderr)
        return 2
    finally:
        if log is not None:
            log.record('command_timing', command=args.command,
                       machine_elapsed_seconds=max(0.0, time.monotonic() - started - human_elapsed))
            # Refresh after timing so exports include the completed command.
            if args.command != 'feedback':
                destination = (args.output if args.command == 'export' else None) or log.path.parent / 'export'
                redactions = tuple(args.redact) if args.command == 'export' else ()
                export_run(log.path, destination, redactions, strict=False)


if __name__ == '__main__':
    raise SystemExit(main())
