"""Offline subprocess proof of the production CLI, ports, engine and exports."""
import json
import os
from pathlib import Path
import subprocess
import sys

import yaml

from ara.runtime.export import methodology
from ara.runtime.logging import EventLog
from ara.runtime.render import render_tree
from ara.types import CommitmentSet, RouteGraph

ROOT = Path(__file__).resolve().parents[2]


def test_native_mock_smoke_and_replay(tmp_path):
    config = yaml.safe_load((ROOT / 'config.yaml').read_text())
    config['cache_dir'] = str(tmp_path / 'cache')
    config_path = tmp_path / 'config.yaml'
    config_path.write_text(yaml.safe_dump(config))
    env = {k: v for k, v in os.environ.items() if k != 'ANTHROPIC_API_KEY'}
    def cli(*args):
        result = subprocess.run([sys.executable, '-m', 'ara.runtime.cli', *args],
                                cwd=ROOT, env=env, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
    run = tmp_path / 'smoke'
    cli('run', '--smoke', '--provider', 'mock', '--config', str(config_path), '--run-dir', str(run))
    files = sorted((run / 'routes').glob('*.json'))
    assert len(files) == 4
    graphs = [RouteGraph.from_json(p.read_text()) for p in files]
    commitments = CommitmentSet.from_json((run / 'commitments.json').read_text())
    assert sum(g.status == 'CLOSED' for g in graphs) == 2
    for path, graph in zip(files, graphs):
        assert path.with_suffix('.txt').read_text() == render_tree(graph, commitments)
        for node in graph.nodes:
            if graph.status == 'CLOSED' and node.kind == 'leaf':
                assert commitments.get(node.t_id).formula.canonical() == node.proposition.formula.canonical()
            elif graph.status != 'CLOSED':
                assert node.id in graph.frontier
    events = EventLog(run / 'events.jsonl').read()
    findings = json.loads(next(e['payload_json'] for e in events if e['stage'] == 'conflicts_and_robustness'))
    assert len(findings['findings']['analyses']) == 2
    for analysis in findings['findings']['analyses']:
        from ara.types import Formula
        positive = Formula.from_dict(analysis['target']['target']['formula'])
        negative = Formula.from_dict(analysis['negated']['target']['formula'])
        assert negative.canonical() == positive.negated().canonical()
        assert analysis['target']['independent_closed_routes'] == 1
        assert analysis['negated']['independent_closed_routes'] == 0
        assert analysis['forward'] and analysis['forward'][0]['consequences']
    assert any(e['decision'] and e['decision']['reason_code'] == 'BANK_LICENSED' for e in events)
    assert not (run / 'draft.json').exists()
    assert any(e['stage'] == 'awaiting_selection' for e in events)
    selected = next(g.id for g in graphs if g.nodes[0].proposition.text == 'P')
    cli('select', '--run-dir', str(run), '--route', selected)
    draft = json.loads((run / 'draft.json').read_text())
    assert draft['body'] == '[[node:n0]][[node:n1]][[node:n2]] ' + ' '.join(['P'] * 150)
    cli('export', '--run-dir', str(run), '--output', str(run / 'explicit-export'))
    assert (run / 'explicit-export/essay.txt').read_text() == 'P\n\n' + ' '.join(['P'] * 150) + '\n'
    assert (run / 'explicit-export/methodology.md').read_text() == methodology(run / 'events.jsonl')
    cli('feedback', '--run-dir', str(run), '--text', 'P')
    selected = next(g.id for g in graphs if g.nodes[0].proposition.text == 'P')
    cli('select', '--run-dir', str(run), '--route', selected)
    events = EventLog(run / 'events.jsonl').read()
    assert any(e['stage'] == 'feedback' and json.loads(e['payload_json'])['text'] == 'P' for e in events)
    assert json.loads((run / 'draft.json').read_text())['body'] == '[[node:n0]][[node:n1]][[node:n2]] ' + ' '.join(['P'] * 150)
    replay = tmp_path / 'replay'
    cli('run', '--smoke', '--provider', 'mock', '--config', str(config_path), '--run-dir', str(replay))
    assert [p.read_bytes() for p in files] == [p.read_bytes() for p in sorted((replay / 'routes').glob('*.json'))]
    models = [e for e in EventLog(replay / 'events.jsonl').read() if e['label'] == 'MODEL']
    assert models and all(json.loads(e['payload_json'])['cache_hit'] for e in models)
    assert all(e['cost_usd'] == 0 for e in models)
