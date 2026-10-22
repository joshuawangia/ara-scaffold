"""Offline placeholder cap-scale search benchmark using the actual native writer.

Run from the repository root. All output goes to a new ignored runs/ directory.
The baseline engine is loaded read-only from the specified Git revision.
"""
from dataclasses import replace
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import types

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tests/engine')]
from test_search import Scripted, table, proposal, prop, P, Q, R
from ara.bank import load_bank
from ara.engine.search import Engine, EngineConfig
from ara.runtime.logging import EventLog, read_log
from ara.runtime.search_traces import SearchTraceFiles
from ara.types import Formula


class Dynamic(Scripted):
    def __init__(self, bank, width, padding, rule, log=None):
        super().__init__()
        self.entry = bank.get(rule)
        self.width, self.padding, self.log = width, padding, log

    def propose_cuts(self, goal, commitments, entries):
        self.goals.append(goal.formula.canonical())
        cuts = []
        for atom in (P, Q, R)[:self.width]:
            child = Formula('and', (goal.formula, atom))
            cut = proposal(self.entry.id, goal.formula, **{slot.id: child for slot in self.entry.premise_slots})
            cuts.append(replace(cut, premises=tuple(replace(p, text=p.text + ' ' * self.padding) for p in cut.premises)))
        return tuple(cuts)

    def emit(self, event):
        super().emit(event)
        if self.log is not None:
            self.log.emit(event)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--base', default='0eb8592')
    parser.add_argument('--scenarios', nargs='+', type=int, choices=range(5), default=list(range(5)))
    args = parser.parse_args()
    out = args.out.resolve()
    if not out.is_relative_to(ROOT / 'runs'):
        parser.error('--out must be a new directory under runs/')
    out.mkdir(parents=True, exist_ok=False)
    baseline = types.ModuleType('ara.engine.trace_benchmark_baseline')
    sys.modules[baseline.__name__] = baseline
    exec(subprocess.check_output(['git', 'show', f'{args.base}:ara/engine/search.py'], cwd=ROOT, text=True), baseline.__dict__)
    bank = load_bank(ROOT / 'bank')
    results = []
    scenarios = [(1, 0, 'sign'), (1, 1000, 'sign'), (3, 0, 'sign'), (3, 1000, 'sign'), (1, 0, 'expert_opinion')]
    for index in args.scenarios:
        width, padding, rule = scenarios[index]
        runs = []
        for traced in (False, True):
            log = EventLog(out / str(index) / ('traced' if traced else 'baseline') / 'events.jsonl')
            ports = Dynamic(bank, width, padding, rule, log)
            cls, config = (Engine, EngineConfig) if traced else (baseline.Engine, baseline.EngineConfig)
            kwargs = dict(traces=SearchTraceFiles(log)) if traced else {}
            engine = cls(bank, table(), ports, ports, ports, ports, ports, ports,
                         config(depth_cap=6, node_cap=500), **kwargs)
            start = time.perf_counter()
            result = engine.search(prop(P))
            elapsed = time.perf_counter() - start
            runs.append((result, ports, elapsed, log))
            print(json.dumps(dict(scenario=index, traced=traced, seconds=elapsed, nodes=result.nodes_created)), flush=True)
        old, new = runs
        assert old[0].to_json() == new[0].to_json()
        assert old[1].goals == new[1].goals
        assert [e.decision for e in old[1].events] == [e.decision for e in new[1].events]
        seals = [r for r in read_log(new[3].path) if r['event']['stage'] == 'search_trace_receipt']
        assert len(seals) == 1
        sidecar_bytes = sum(p.stat().st_size for p in (new[3].path.parent / 'search-traces').glob('*.jsonl'))
        # Exact file size difference includes the chained seal and checkpoint increment.
        chain_increment = sum(p.stat().st_size for p in (new[3].path, new[3].anchor)) - sum(p.stat().st_size for p in (old[3].path, old[3].anchor))
        row = dict(width=width, padding=padding, rule=rule, nodes=new[0].nodes_created, routes=len(new[0].routes),
                   baseline_seconds=old[2], traced_seconds=new[2], overhead_pct=100 * (new[2] / old[2] - 1),
                   sidecar_bytes=sidecar_bytes, chain_increment_bytes=chain_increment,
                   pilot_trace_mb=20 * (sidecar_bytes + chain_increment) / 1e6,
                   equal_results_goals_decisions=True)
        results.append(row)
        (out / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
        print(json.dumps(row), flush=True)


if __name__ == '__main__':
    main()
