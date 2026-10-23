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
from ara.runtime.providers import AnthropicProvider, MockProvider
from ara.types import RouteGraph

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
    run.add_argument('--provider', choices=('anthropic', 'mock'))
    run.add_argument('--topic')
    run.add_argument('--literature', type=Path)
    run.add_argument('--audience', default='runtime audience')
    run.add_argument('--named-position')
    run.add_argument('--route')
    resume = sub.add_parser('resume-construction', help='continue a verified stopped construction in its existing directory')
    resume.add_argument('--run-dir', type=Path, required=True)
    resume.add_argument('--unknown-usage-policy', choices=('count-at-reservation',), required=True)
    resume.add_argument('--plan-only', action='store_true', help='free counts and verified restoration only; no generation')
    resume.add_argument('--output-dir', type=Path, help='separate empty directory for count-only resume receipts')
    extraction = sub.add_parser('extract')
    extraction.add_argument('--config', type=Path, default=ROOT / 'config.yaml')
    extraction.add_argument('--manifest', type=Path, required=True)
    extraction.add_argument('--fulltext-dir', type=Path, required=True)
    extraction.add_argument('--run-dir', type=Path, required=True)
    extraction.add_argument('--provider', choices=('anthropic', 'mock'))
    extraction.add_argument('--paper-id', action='append', default=[])
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
    plan = sub.add_parser('plan-extraction')
    plan.add_argument('--config', type=Path, default=ROOT / 'config.yaml')
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
    report = sub.add_parser('report', help='render verified run receipts offline; no model calls')
    report.add_argument('--run-dir', type=Path, action='append', required=True)
    report.add_argument('--out', type=Path, required=True)
    for command in ('select', 'feedback', 'export'):
        cmd = sub.add_parser(command)
        cmd.add_argument('--run-dir', type=Path, required=True)
        if command == 'select':
            cmd.add_argument('--route')
        if command == 'feedback':
            cmd.add_argument('--text')
        if command == 'export':
            cmd.add_argument('--output', type=Path)
            cmd.add_argument('--redact', action='append', default=[])
    for cmd in sub.choices.values():
        cmd.add_argument('--human-minutes', type=float, default=0)
    return p


def make_calls(config: dict, log: EventLog, topic: str, root: Path = ROOT) -> ModelCalls:
    if config['provider'] == 'anthropic':
        provider = AnthropicProvider(config)
    elif config['provider'] == 'mock':
        provider = MockProvider(Path(config.get('mock_responses', root / 'tests/fixtures/runtime/native-canned.json')), config['model'])
    else:
        raise ValueError(f'unknown provider: {config["provider"]}')
    return ModelCalls(config, provider, log, Cache(Path(config['cache_dir'])), root, topic)


def validate_profile_caps(config: dict, profile: str | None) -> None:
    if profile != 'extraction-full':
        return
    missing_caps = [key for key in ('token_cap', 'cost_cap_usd', 'extraction_cost_cap_usd')
                    if config.get(key) is None]
    if missing_caps:
        raise ValueError('operator must set extraction-full caps: ' + ', '.join(missing_caps))


def main(argv: list[str] | None = None, *, engine_factory: Callable = native_engine,
         calls_factory: Callable = make_calls) -> int:
    raw_args = list(sys.argv[1:] if argv is None else argv)
    args = parser().parse_args(raw_args)
    log = None
    started = time.monotonic()
    human_elapsed = 0.0
    try:
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
                if args.plan_only:
                    from ara.runtime.planning import plan_construction_resume
                    log = EventLog(args.output_dir / 'events.jsonl')
                    log.human('resume-construction-plan', json.dumps(raw_args), reported_minutes=args.human_minutes)
                    result = plan_construction_resume(config, log, source_log, ROOT, run)
                    print(json.dumps(result))
                    return 0
                log = source_log
                calls = calls_factory(config, log, run['topic'])
                calls.construction_resume = True
                log.human('resume-construction', json.dumps(raw_args), reported_minutes=args.human_minutes)
                human = next((json.loads(e['payload_json']) for e in events if e['stage'] == 'run' and e['label'] == 'HUMAN'), {})
                commitments, targets = prepare(calls, bank, run['literature'], run['audience'], human.get('named_position'))
                routes = search_all(calls, engine_factory(bank, calls), commitments, targets)
                log.record('awaiting_selection', route_ids=[r.id for r in routes])
                log.record('run_finished', state='awaiting_selection')
                print(str(args.run_dir))
                return 0
        if args.command == 'report':
            from ara.runtime.report import generate_report
            print(str(generate_report(args.run_dir, args.out)))
            return 0
        if args.command == 'schema-preflight':
            from ara.runtime.preflight import schema_preflight
            from ara.runtime.provenance import checkpoint, read_checkpoint, import_receipts
            if not 0 <= args.cost_cap_usd <= 1:
                raise ValueError('schema preflight cap must be between zero and USD1')
            config = yaml.safe_load(args.config.read_text())
            config.update(config[args.profile])
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
            config.update(config[args.profile])
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
            config.update(config[args.profile])
            if args.run_dir.exists() and any(args.run_dir.iterdir()):
                raise ValueError('new planning directory must be empty')
            log = EventLog(args.run_dir / 'events.jsonl')
            log.human('plan-extraction', json.dumps(raw_args), argv=raw_args, reported_minutes=args.human_minutes)
            log.record('extraction_planning_started', config=config, counter=args.token_counter)
            papers = load_papers(args.manifest, args.fulltext_dir, tuple(args.paper_id))
            report = plan_extraction(config, log, papers, ROOT, args.token_counter)
            return 2 if report['totals']['refused'] else 0
        if args.command == 'extract':
            config = yaml.safe_load(args.config.read_text())
            if args.profile:
                config.update(config[args.profile])
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
                config.update(config[selected_profile])
            validate_profile_caps(config, selected_profile)
            if args.smoke:
                topic = args.topic if args.topic is not None else 'P Q'
                literature = args.literature.read_text() if args.literature else (
                    ROOT / 'tests/fixtures/runtime/smoke-literature.txt').read_text()
            else:
                if args.topic is None or args.literature is None:
                    raise ValueError('run requires --topic and --literature, or --smoke')
                topic, literature = args.topic, args.literature.read_text()
            if args.provider is not None:
                config['provider'] = args.provider
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
            route_id = args.route
            if route_id:
                log.human('select', route_id, source='run --route')
            elif args.smoke:
                route_id = next((r.id for r in routes if r.status == 'CLOSED'), routes[0].id if routes else None)
                log.record('selection', route_id=route_id, policy='smoke: first CLOSED route, otherwise first OPEN')
            if route_id:
                chosen = next((r for r in routes if r.id == route_id), None)
                if chosen is None:
                    raise ValueError('unknown route id')
                compose(calls, chosen)
            else:
                log.record('awaiting_selection', route_ids=[r.id for r in routes])
            log.record('run_finished', state='complete' if route_id else 'awaiting_selection')
            export_run(log.path, directory / 'export')
            print(str(directory))
            return 0
        if not (args.run_dir / 'events.jsonl').is_file():
            raise ValueError('run log does not exist')
        log = EventLog(args.run_dir / 'events.jsonl')
        log.human(args.command + '_command', json.dumps(raw_args, ensure_ascii=False),
                  argv=raw_args, reported_minutes=args.human_minutes)
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
        routes = [RouteGraph.from_dict(json.loads(e['payload_json'])['graph'])
                  for e in events if e['stage'] == 'route']
        for route in routes:
            print(f'{route.id} [{route.status}]')
        start = time.monotonic()
        route_id = args.route if args.route is not None else input('Route id: ')
        elapsed = time.monotonic() - start if args.route is None else 0
        human_elapsed += elapsed
        log.human('select', route_id, elapsed_seconds=elapsed)
        chosen = next((r for r in routes if r.id == route_id), None)
        if chosen is None:
            raise ValueError('unknown route id')
        run = next(json.loads(e['payload_json']) for e in events if e['stage'] == 'run_started')
        calls = calls_factory(run['config'], log, run['topic'])
        compose(calls, chosen)
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
            export_run(log.path, log.path.parent / 'export')
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
                export_run(log.path, destination, redactions)


if __name__ == '__main__':
    raise SystemExit(main())
