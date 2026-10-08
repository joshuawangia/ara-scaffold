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
    run.add_argument('--smoke', action='store_true')
    run.add_argument('--topic')
    run.add_argument('--literature', type=Path)
    run.add_argument('--audience', default='runtime audience')
    run.add_argument('--named-position')
    run.add_argument('--route')
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
        provider = MockProvider(Path(config['mock_responses']), config['model'])
    else:
        raise ValueError(f'unknown provider: {config["provider"]}')
    return ModelCalls(config, provider, log, Cache(Path(config['cache_dir'])), root, topic)


def main(argv: list[str] | None = None, *, engine_factory: Callable = native_engine,
         calls_factory: Callable = make_calls) -> int:
    raw_args = list(sys.argv[1:] if argv is None else argv)
    args = parser().parse_args(raw_args)
    log = None
    try:
        if args.command == 'run':
            config = yaml.safe_load(args.config.read_text())
            if args.smoke:
                config.update(config['smoke'])
                topic = args.topic if args.topic is not None else 'P Q'
                literature = args.literature.read_text() if args.literature else (
                    ROOT / 'tests/fixtures/runtime/smoke-literature.txt').read_text()
            else:
                if args.topic is None or args.literature is None:
                    raise ValueError('run requires --topic and --literature, or --smoke')
                topic, literature = args.topic, args.literature.read_text()
            directory = args.run_dir or Path(config['runs_dir']) / uuid.uuid4().hex
            if directory.exists() and any(directory.iterdir()):
                raise ValueError('new run directory must be empty; use select/feedback/export to resume')
            log = EventLog(directory / 'events.jsonl')
            log.human('run', topic, argv=raw_args, literature=literature, audience=args.audience,
                      named_position=args.named_position, reported_minutes=args.human_minutes)
            bank = load_bank(ROOT / 'bank')
            log.record('run_started', config=config, topic=topic, bank_version=bank.bank_version,
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
        log = EventLog(args.run_dir / 'events.jsonl')
        log.human(args.command + '_command', json.dumps(raw_args, ensure_ascii=False),
                  argv=raw_args, reported_minutes=args.human_minutes)
        if args.command == 'feedback':
            start = time.monotonic()
            text = args.text if args.text is not None else input('Feedback: ')
            elapsed = time.monotonic() - start if args.text is None else 0
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
        log.human('select', route_id, elapsed_seconds=elapsed)
        chosen = next((r for r in routes if r.id == route_id), None)
        if chosen is None:
            raise ValueError('unknown route id')
        run = next(json.loads(e['payload_json']) for e in events if e['stage'] == 'run_started')
        calls = calls_factory(run['config'], log, run['topic'])
        compose(calls, chosen)
        return 0
    except Exception as exc:
        if log is not None:
            if not isinstance(exc, BudgetStop):
                log.record('runtime_error', error_type=type(exc).__name__, message=str(exc))
            # Methodology and partial graphs survive even a clean budget stop.
            export_run(log.path, log.path.parent / 'export')
        print(f'ara: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
