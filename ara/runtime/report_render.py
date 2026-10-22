"""Self-contained HTML, Markdown twin, JSON receipts and Graphviz exports."""
from __future__ import annotations

import base64
from html import escape
import json
from pathlib import Path
import shutil
import subprocess


def pretty(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)


def pre(value):
    return '<pre>' + escape(pretty(value)) + '</pre>'


def details(title, body, opened=False):
    return '<details' + (' open' if opened else '') + '><summary>' + escape(str(title)) + '</summary>' + body + '</details>'


def fenced(value):
    text = pretty(value)
    fence = '```'
    while fence in text:
        fence += '`'
    return fence + 'json\n' + text + '\n' + fence + '\n'


def node_title(node, depth):
    rule = (node.get('proposal') or {}).get('bank_id')
    return f"{node['id']} · depth {depth} · {node['kind']} · T={node.get('t_id', 'open')}" + (
        f' · {rule}' if rule else '') + ': ' + node['proposition']['text']


def route_html(graph):
    nodes = {n['id']: n for n in graph['nodes']}
    def visit(nid, depth=0, ancestors=frozenset()):
        if nid in ancestors:
            return '<p>Cycle reference: ' + escape(nid) + '</p>'
        if nid not in nodes:
            return '<p>Missing node: ' + escape(nid) + '</p>'
        node = nodes[nid]
        return details(node_title(node, depth), pre(node) + ''.join(
            visit(child, depth + 1, ancestors | {nid}) for child in node.get('children', [])), depth < 1)
    reachable = set()
    stack = [graph['root_id']]
    while stack:
        nid = stack.pop()
        if nid in reachable or nid not in nodes:
            continue
        reachable.add(nid)
        stack.extend(nodes[nid].get('children', []))
    return visit(graph['root_id']) + ''.join(details('Unreachable recorded node ' + nid, pre(node))
                                            for nid, node in nodes.items() if nid not in reachable)


def route_dot(graph):
    nodes = {n['id']: f'n{i}' for i, n in enumerate(graph['nodes'])}
    depths = {graph['root_id']: 0}
    by_id = {n['id']: n for n in graph['nodes']}
    queue = [graph['root_id']]
    for nid in queue:
        for child in by_id.get(nid, {}).get('children', []):
            if child not in depths:
                depths[child] = depths[nid] + 1
                queue.append(child)
    lines = ['digraph route {', 'rankdir=TB;', 'node [shape=box];']
    for node in graph['nodes']:
        label = node_title(node, depths.get(node['id'], 'unreachable'))
        lines.append(f'{nodes[node["id"]]} [label={json.dumps(label, ensure_ascii=False)}];')
        for child in node.get('children', []):
            if child in nodes:
                rule = (node.get('proposal') or {}).get('bank_id', 'step')
                lines.append(f'{nodes[node["id"]]} -> {nodes[child]} [label={json.dumps(rule, ensure_ascii=False)}];')
    return '\n'.join(lines + ['}']) + '\n'


def trace_dot(trace):
    ids = {s['state_id']: f's{i}' for i, s in enumerate(trace['states'])}
    lines = ['digraph search {', 'rankdir=TB;', 'node [shape=box];']
    for state in trace['states']:
        label = f"state {state['state_id']}\n{state['transition']}\n{state.get('reason', '')}"
        lines.append(f'{ids[state["state_id"]]} [label={json.dumps(label, ensure_ascii=False)}];')
        parent = state['parent_state_id']
        if parent in ids:
            step = state.get('bank_id') or state.get('reason') or state['transition']
            lines.append(f'{ids[parent]} -> {ids[state["state_id"]]} [label={json.dumps(step, ensure_ascii=False)}];')
    for index, receipt in enumerate(trace['receipts']):
        p = receipt['payload']
        if p['action'] in ('prune', 'complete') and p.get('state_id') in ids:
            lines.append(f'p{index} [label={json.dumps(p["reason"], ensure_ascii=False)},shape=ellipse];')
            lines.append(f'{ids[p["state_id"]]} -> p{index};')
    return '\n'.join(lines + ['}']) + '\n'


def trace_html(trace):
    children = {}
    for state in trace['states']:
        children.setdefault(state['parent_state_id'], []).append(state)
    def visit(state, ancestors=frozenset()):
        sid = state['state_id']
        if sid in ancestors:
            return '<p>Cycle in recorded state ancestry.</p>'
        receipts = [r for r in trace['receipts'] if r['payload'].get('state_id') == sid and r['payload']['action'] != 'state']
        decisions = [r for r in trace['decisions'] if r['context'].get('state_id') == sid]
        title = f"State {sid} ← {state['parent_state_id']} · {state['transition']} · {state.get('bank_id') or state.get('reason', '')}"
        body = pre({k: v for k, v in state.items() if k != 'graph'})
        body += route_html(state['graph']) + details('Branch receipts and decisions', pre(receipts + decisions))
        body += ''.join(visit(child, ancestors | {sid}) for child in children.get(sid, []))
        return details(title, body, state['parent_state_id'] is None)
    return ''.join(visit(state) for state in children.get(None, []))


def graph_export(source, stem, destination, graphviz):
    dot_path = destination / 'trees' / (stem + '.dot')
    dot_path.parent.mkdir(exist_ok=True)
    dot_path.write_text(source)
    result = dict(dot=str(dot_path.relative_to(destination)), svg=None, status='DOT only: dot unavailable locally')
    image = ''
    if graphviz:
        try:
            completed = subprocess.run([graphviz, '-Tsvg'], input=source, text=True,
                                       capture_output=True, timeout=30, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            result['status'] = 'DOT retained; SVG rendering failed: ' + str(exc)
        else:
            if completed.returncode:
                result['status'] = 'DOT retained; SVG rendering failed: ' + completed.stderr
            else:
                svg = completed.stdout
                dot_path.with_suffix('.svg').write_text(svg)
                result.update(svg=str(dot_path.with_suffix('.svg').relative_to(destination)), status='DOT and SVG rendered locally')
                image = '<img alt="Recorded graph" src="data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode() + '">'
    return result, image


CSS = '''
:root {color-scheme:light; font-family:system-ui,sans-serif; color:#172630; background:#f4f6f7}
body {max-width:1200px; margin:auto; padding:2rem} h1,h2,h3 {line-height:1.2}
section {background:white; padding:1.4rem; margin:1.2rem 0; border-radius:8px}
a {color:#075e89} nav a {margin-right:1rem} summary {cursor:pointer; font-weight:600; padding:.5rem}
details {border-left:3px solid #9eb8c6; margin:.6rem 0; padding-left:.7rem}
pre {white-space:pre-wrap; overflow-wrap:anywhere; background:#f5f7f8; padding:.8rem; font-size:.85rem}
table {border-collapse:collapse; width:100%} td,th {text-align:left; padding:.6rem; border-bottom:1px solid #ddd}
img {max-width:100%; height:auto} .gap {border-left:4px solid #b16b00; padding:.6rem; background:#fff6e6}
@media print {body {background:white; padding:0} section {break-inside:auto}}
'''


def render(report, destination: Path):
    graphviz = shutil.which('dot')
    html = ['<!doctype html><html lang="en"><meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; img-src data:; style-src \'unsafe-inline\'">',
            '<title>ARA full-run report</title><style>' + CSS + '</style><body><h1>ARA full-run report</h1>',
            '<p>Offline snapshot of verified receipts. No model calls.</p>']
    md = ['# ARA full-run report\n\nOffline snapshot of verified receipts. No model calls.\n']
    def section(title, value, anchor, custom=''):
        html.append('<section id="' + anchor + '"><h2>' + escape(title) + '</h2>' + custom + details('Recorded data', pre(value)) + '</section>')
        md.append('## ' + title + '\n\n' + fenced(value))
    html.append('<nav>' + ''.join(f'<a href="#run-{i}">Run {i+1}</a>' for i in range(len(report['runs']))) + '</nav>')
    section('Combined accounting', dict(aggregation_note=report['aggregation_note'], **report['accounting']), 'combined')
    exported_runs = []
    for index, run in enumerate(report['runs']):
        prefix = f'run-{index}'
        html.append('<h2 id="' + prefix + '">' + escape(run['directory']) + '</h2>')
        md.append('# Run: ' + run['directory'] + '\n')
        # Failure or missing-data notices are visible before opening any details.
        html.extend('<p class="gap">' + escape(g) + '</p>' for g in run['gaps'])
        section('1. Run identity', run['identity'], prefix + '-identity')
        ex = run['extraction']
        table = '<table><thead><tr><th>Paper</th><th>Status</th><th>Pages</th><th>Items</th><th>Measured USD</th><th>Reserved unknown USD</th></tr></thead><tbody>'
        for paper in ex['papers']:
            outcome = paper['outcome'] or {}
            cells = [paper['source_id'], paper['status'], outcome.get('pages', 'unknown'),
                     sum(paper['item_counts_by_kind'].values()), paper['accounting']['measured']['cost_usd'],
                     paper['accounting']['unknown_at_reservation']['cost_usd']]
            table += '<tr>' + ''.join('<td>' + escape(str(v)) + '</td>' for v in cells) + '</tr>'
        table += '</tbody></table>'
        table += ''.join(details(p['source_id'] + ' · ' + p['status'], pre(p)) for p in ex['papers'])
        section('2. Extraction per paper and corpus exclusions', ex, prefix + '-extraction', table)
        section('3. Construction and frozen commitments', run['construction'], prefix + '-construction')
        trees = []
        body = ''
        for ti, trace in enumerate(run['search']['traces']):
            export, svg = graph_export(trace_dot(trace), f'{prefix}-search-{ti}', destination, graphviz)
            trees.append(dict(kind='search', begin_seq=trace['begin_seq'], **export))
            body += details(f"Search {trace['target']['id']} · {trace['search_id']} · {'complete' if trace['complete'] else 'interrupted'}", trace_html(trace) + svg)
        for ri, route in enumerate(run['routes']):
            graph = route['graph']
            export, svg = graph_export(route_dot(graph), f'{prefix}-route-{ri}', destination, graphviz)
            trees.append(dict(kind='route', route_id=graph['id'], seq=route['seq'], **export))
            body += details(f"{route['target']} / {route['polarity']} · {graph['id']} [{graph['status']}]", route_html(graph) + svg)
        if not body:
            body = '<p>No recorded search trees or routes.</p>'
        run['tree_exports'] = trees
        for tree in trees:
            if tree['svg'] is None:
                run['gaps'].append(tree['status'] + ': ' + tree['dot'])
        section('4. Search-tree tracing', dict(**run['search'], tree_exports=trees), prefix + '-search', body)
        cards = ''.join(details(r['graph']['id'] + ' · ' + r['graph']['status'],
                               '<p>' + escape(str(r['model_summary']) if r['model_summary'] else 'Model-written summary not recorded.') + '</p>'
                               + pre(r['support_chain']) + details('Recorded audit results', pre(r['audit_results'])))
                        for r in run['routes'])
        section('5. Routes for selection', dict(routes=run['routes'], unassigned_audits=run['unassigned_audits'],
                note='A null summary means no recorded model-written summary. Unassigned audits cannot certify a particular route.'), prefix + '-routes', cards)
        section('6. Accounting', run['accounting'], prefix + '-accounting')
        section('7. Human actions log', run['human_actions'], prefix + '-human')
        section('8. Gaps and limits', dict(gaps=run['gaps'], failure_receipts=run['failure_receipts'],
                                         limit_receipts=run['limit_receipts']), prefix + '-gaps',
                ''.join('<p class="gap">' + escape(g) + '</p>' for g in run['gaps']))
        section('Run artifacts (not independently authenticated)', run['artifacts'], prefix + '-artifacts')
        raw_file = prefix + '-events.json'
        artifact_file = prefix + '-artifacts.json'
        (destination / raw_file).write_text(pretty(run['records']) + '\n')
        (destination / artifact_file).write_text(pretty(run['artifacts']) + '\n')
        html.append(details('Full verified event receipts (prompts, responses and usage)', pre(run['records'])))
        md.append('## Full verified event receipts\n\n' + fenced(run['records']))
        exported_runs.append({**{k: v for k, v in run.items() if k not in ('records', 'artifacts')},
                              'events_file': raw_file, 'artifacts_file': artifact_file})
    (destination / 'data.json').write_text(pretty({**report, 'runs': exported_runs}) + '\n')
    (destination / 'report.html').write_text('\n'.join(html) + '</body></html>\n')
    (destination / 'report.md').write_text('\n'.join(md))
