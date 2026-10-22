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
    pieces, visited = [], set()
    stack = [('node', graph['root_id'], 0)]
    while stack:
        action, nid, depth = stack.pop()
        if action == 'close':
            pieces.append('</details>')
            continue
        if nid in visited or nid not in nodes:
            pieces.append('<p>Repeated or missing node reference: ' + escape(nid) + '</p>')
            continue
        visited.add(nid)
        node = nodes[nid]
        pieces.append('<details' + (' open' if depth == 0 else '') + '><summary>' +
                      escape(node_title(node, depth)) + '</summary>' + pre(node))
        stack.append(('close', nid, depth))
        stack.extend(('node', child, depth + 1) for child in reversed(node.get('children', [])))
    pieces.extend(details('Unreachable recorded node ' + nid, pre(node)) for nid, node in nodes.items() if nid not in visited)
    return ''.join(pieces)


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
    states = [s for s in trace['states'] if type(s.get('state_id')) is int]
    ids = {s['state_id']: f's{i}' for i, s in enumerate(states)}
    lines = ['digraph search {', 'rankdir=TB;', 'node [shape=box];']
    for state in states:
        label = f"state {state['state_id']}\n{state.get('transition')}\n{state.get('reason', '')}"
        lines.append(f'{ids[state["state_id"]]} [label={json.dumps(label, ensure_ascii=False)}];')
        parent = state.get('parent_state_id')
        if type(parent) is int and parent in ids:
            step = state.get('bank_id') or state.get('reason') or state.get('transition', 'unknown')
            lines.append(f'{ids[parent]} -> {ids[state["state_id"]]} [label={json.dumps(step, ensure_ascii=False)}];')
    for index, receipt in enumerate(trace['receipts']):
        p = receipt['payload']
        if p.get('action') in ('prune', 'complete') and type(p.get('state_id')) is int and p['state_id'] in ids:
            lines.append(f'p{index} [label={json.dumps(p.get("reason", "missing reason"), ensure_ascii=False)},shape=ellipse];')
            lines.append(f'{ids[p["state_id"]]} -> p{index};')
    return '\n'.join(lines + ['}']) + '\n'


def trace_html(trace, anchor_prefix='trace'):
    """One collapsible block per state with explicit links; no recursive history."""
    from collections import defaultdict
    receipts, decisions, children = defaultdict(list), defaultdict(list), defaultdict(list)
    for receipt in trace['receipts']:
        state = receipt['payload'].get('state_id')
        if type(state) is int and receipt['payload'].get('action') != 'state':
            receipts[state].append(receipt)
    for decision in trace['decisions']:
        state = decision['context'].get('state_id')
        if type(state) is int:
            decisions[state].append(decision)
    for state in trace['states']:
        parent = state.get('parent_state_id')
        if type(parent) is int:
            children[parent].append(state.get('state_id'))
    def link(sid):
        return '<a href="#' + anchor_prefix + '-state-' + escape(str(sid), quote=True) + '">' + escape(str(sid)) + '</a>'
    pieces = ['<p>State history is shown in recorded order. Parent and child links retain ancestry without deeply nesting the page.</p>']
    for index, state in enumerate(trace['states']):
        sid, parent = state.get('state_id'), state.get('parent_state_id')
        title = f"State {sid} ← {parent} · {state.get('transition')} · {state.get('bank_id') or state.get('reason', '')}"
        pieces.append('<div id="' + anchor_prefix + '-state-' + escape(str(sid), quote=True) + '">')
        body = '<p>Parent: ' + (link(parent) if parent is not None else 'root') + '</p>'
        if type(sid) is int:
            body += '<p>Children: ' + ', '.join(link(child) for child in children[sid]) + '</p>'
        body += pre({k: v for k, v in state.items() if k != 'graph'})
        if type(sid) is int:
            for receipt in receipts[sid]:
                terminal = receipt['payload'].get('graph')
                if terminal and not trace.get('issues'):
                    body += route_html(terminal)
            body += details('Branch receipts and decisions', pre(receipts[sid] + decisions[sid]))
        pieces.append(details(title, body, index == 0) + '</div>')
    if trace.get('issues'):
        pieces.append(details('Trace gaps and retained receipts', pre(dict(issues=trace['issues'], receipts=trace['receipts']))))
    return ''.join(pieces)


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
        table = '<table><thead><tr><th>Paper</th><th>Status</th><th>Pages</th><th>Items</th><th>Measured USD</th><th>Reserved unknown USD</th><th>Unclassified USD</th></tr></thead><tbody>'
        for paper in ex['papers']:
            outcome = paper['outcome'] or {}
            cells = [paper['source_id'], paper['status'], outcome.get('pages', 'unknown'),
                     sum(paper['item_counts_by_kind'].values()), paper['accounting']['measured']['cost_usd'],
                     paper['accounting']['unknown_at_reservation']['cost_usd'], paper['accounting']['unclassified']['cost_usd']]
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
            target = trace['target']
            target_id = target.get('id', '(unknown)') if isinstance(target, dict) else '(invalid target)'
            status = 'complete' if trace['complete'] else 'partial'
            body += details(f"Search {target_id} · {trace['search_id']} · {status}",
                            trace_html(trace, f'{prefix}-search-{ti}') + svg)
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
