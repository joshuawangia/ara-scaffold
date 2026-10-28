"""Bounded HTML overview with linked, lossless evidence files."""
from __future__ import annotations

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


def node_title(node, depth):
    rule = (node.get('proposal') or {}).get('bank_id')
    return f"{node['id']} · depth {depth} · {node['kind']} · T={node.get('t_id', 'open')}" + (
        f' · {rule}' if rule else '') + ': ' + node['proposition']['text']


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


def graph_export(source, stem, destination, graphviz):
    dot_path = destination / 'trees' / (stem + '.dot')
    dot_path.parent.mkdir(exist_ok=True)
    dot_path.write_text(source)
    result = dict(dot=str(dot_path.relative_to(destination)), svg=None, status='DOT only: dot unavailable locally')
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
    return result


CSS = '''
:root {color-scheme:light; font-family:system-ui,sans-serif; color:#172630; background:#f4f6f7}
body {max-width:1264px; width:100%; box-sizing:border-box; margin:auto; padding:2rem} h1,h2,h3 {line-height:1.2}
section {background:white; padding:1.4rem; margin:1.2rem 0; border-radius:8px}
h2,p,a {overflow-wrap:anywhere} a {color:#075e89} nav a {margin-right:1rem} summary {cursor:pointer; font-weight:600; padding:.5rem}
details {border-left:3px solid #9eb8c6; margin:.6rem 0; padding-left:.7rem}
pre {white-space:pre-wrap; overflow-wrap:anywhere; background:#f5f7f8; padding:.8rem; font-size:.85rem}
.table-scroll {max-width:100%; overflow-x:auto} table {border-collapse:collapse; width:100%; min-width:640px} td,th {text-align:left; padding:.6rem; border-bottom:1px solid #ddd}
img {max-width:100%; height:auto} .gap {border-left:4px solid #b16b00; padding:.6rem; background:#fff6e6}
@media (max-width:600px) {body {padding:1rem} section {padding:1rem}}
@media print {body {background:white; padding:0} section {break-inside:auto}}
'''


# Decimal byte budgets include escaped UTF-8 markup, not source character counts.
HTML_BYTES = 12_000_000
SECTION_BYTES = 64_000
TREE_LEVELS = 3
TREE_NODES = 60


def short(value, limit=240):
    text = str(value)
    return text if len(text) <= limit else text[:limit] + '… [see linked file]'


def preview(value, depth=0):
    if isinstance(value, str):
        return short(value, 500)
    if isinstance(value, (list, dict)) and depth >= 5:
        return f'[{len(value)} entries; see linked file]'
    if isinstance(value, dict):
        items = list(value.items())
        result = {short(k): preview(v, depth + 1) for k, v in items[:30]}
        if len(items) > 30:
            result['…'] = f'{len(items) - 30} more fields; see linked file'
        return result
    if isinstance(value, list):
        result = [preview(v, depth + 1) for v in value[:20]]
        if len(value) > 20:
            result.append(f'{len(value) - 20} more entries; see linked file')
        return result
    return value


def link(path, title='see file'):
    return '<a href="' + escape(path, quote=True) + '">' + escape(title) + '</a>'


def table(headers, rows):
    # Complete table chunks keep overflow notices outside valid, closed markup.
    heading = '<thead><tr>' + ''.join('<th>' + escape(h) + '</th>' for h in headers) + '</tr></thead>'
    chunk = []
    def block():
        return '<div class="table-scroll"><table>' + heading + '<tbody>' + ''.join(chunk) + '</tbody></table></div>'
    for row in rows:
        chunk.append('<tr>' + ''.join('<td>' + cell + '</td>' for cell in row) + '</tr>')
        if len(chunk) == 8:
            yield block()
            chunk = []
    if chunk:
        yield block()


def tree_summary(tree, kind):
    if kind == 'search':
        states = tree['states']
        depths = {}
        for state in states:
            sid, parent = state.get('state_id'), state.get('parent_state_id')
            if type(sid) is int and (parent is None or type(parent) is int and parent in depths):
                depths[sid] = 0 if parent is None else depths[parent] + 1
        rows = [(s.get('state_id'), s.get('parent_state_id'), depths.get(s.get('state_id')),
                 s.get('transition'), s.get('reason') or s.get('bank_id')) for s in states
                if type(s.get('state_id')) is int]
        summary = dict(nodes=len(states), edges=sum(type(s.get('parent_state_id')) is int for s in states),
                       depth=max(depths.values(), default=0), outcome='complete' if tree['complete'] else 'partial',
                       proof_nodes=len(tree.get('nodes', [])), completed_routes=len(tree.get('completed_routes', [])),
                       route_outcomes=[r.get('reason') for r in tree.get('completed_routes', [])],
                       note='Node/edge/depth counts describe state ancestry; proof nodes are counted separately.', issues=tree['issues'])
    else:
        nodes = {n['id']: n for n in tree['nodes']}
        depths, queue = {tree['root_id']: 0}, [tree['root_id']]
        for nid in queue:
            for child in nodes.get(nid, {}).get('children', []):
                if child not in depths:
                    depths[child] = depths[nid] + 1
                    queue.append(child)
        rows = [(n['id'], ', '.join(n.get('children', [])), depths.get(n['id']), n['kind'], n['proposition']['text']) for n in tree['nodes']]
        summary = dict(nodes=len(nodes), edges=sum(len(n.get('children', [])) for n in nodes.values()),
                       depth=max(depths.values(), default=0), outcome=tree['status'])
    visible = [r for r in rows if r[2] is not None and r[2] < TREE_LEVELS][:TREE_NODES]
    summary.update(preview_levels=TREE_LEVELS, preview_nodes=len(visible), omitted_nodes=len(rows)-len(visible))
    return summary, visible


class Page:
    def __init__(self, destination, run_count):
        self.destination = destination
        self.parts = ['<!doctype html><html lang="en"><meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'">',
            '<title>ARA full-run report</title><style>' + CSS + '</style><body>',
            '<h1>ARA full-run report</h1><p>Offline verified snapshot. No model calls. '
            'This overview contains bounded previews; full evidence is in linked sibling files.</p>',
            '<p>' + link('data.json', 'All runs and files') + ' · ' + link('events/index.json', 'Unique events and imported-by references') + '</p>']
        self.size = sum(len(s.encode()) for s in self.parts)
        self.budget = min(SECTION_BYTES, max(1000, (HTML_BYTES - self.size - 1000) // (run_count * 10 + 4)))
        self.md = ['# ARA full-run report\n\nBounded overview; [all runs and evidence](data.json).\n']
        self.truncated = []

    def section(self, title, anchor, filename, fragments):
        header = '<section id="' + anchor + '"><h2>' + escape(short(title)) + '</h2>'
        notice = '<p>Full data: ' + link(filename, 'see file ' + filename) + '</p>'
        warning = '<p class="gap">HTML view truncated; ' + link(filename, 'see file ' + filename) + '.</p>'
        allowance = min(self.budget, HTML_BYTES - self.size - 1000)
        if allowance < len((header + notice + warning).encode()) + 20:
            self.truncated.append(anchor)
            return  # The root manifest link still reaches every exported section.
        body, used, cut = [], len((header + notice + warning + '</section>').encode()), False
        for fragment in fragments:
            size = len(fragment.encode())
            if used + size > allowance:
                cut = True
                break
            body.append(fragment)
            used += size
        # Each fragment is a complete element; section truncation never cuts tags.
        text = header + notice + ''.join(body) + (warning if cut else '') + '</section>'
        self.parts.append(text)
        self.size += len(text.encode())
        if cut:
            self.truncated.append(anchor)
        self.md.append('## ' + short(title) + '\n\n[Full data](' + filename + ')\n\n' +
                       ('HTML view truncated.\n' if cut else ''))

    def finish(self):
        if self.truncated:
            self.parts.append('<p class="gap">Some HTML views were truncated. ' + link('data.json', 'see file data.json for every run and section') + '.</p>')
        self.parts.append('</body></html>\n')
        text = '\n'.join(self.parts)
        assert len(text.encode()) < 15_000_000, 'HTML budget invariant failed'
        (self.destination/'report.html').write_text(text)
        (self.destination/'report.md').write_text('\n'.join(self.md))


def render(report, destination: Path):
    from ara.runtime.report_files import EvidenceFiles, write_json
    files = EvidenceFiles(destination)
    page = Page(destination, len(report['runs']))
    graphviz = shutil.which('dot')
    exported = []
    page.section('Run overview', 'runs', 'data.json', table(
        ['Run', 'Records', 'Measured USD', 'Reserved unknown USD'],
        ([link(f'#run-{i}-identity', short(r['directory'])), str(len(r['records'])),
          str(r['accounting']['measured']['cost_usd']), str(r['accounting']['unknown_at_reservation']['cost_usd'])]
         for i, r in enumerate(report['runs']))))
    account_file = files.write('accounting.json', report['accounting'])
    combined = {k: v for k, v in report['accounting'].items() if k not in ('timeline', 'unresolved_dispatches', 'unfinalized_measured_responses')}
    page.section('Combined accounting', 'combined', account_file,
                 [*table(['Classification', 'USD', 'Model receipts'],
                         ([escape(name), str(combined[key]['cost_usd']), str(combined[key]['model_calls'])]
                          for name, key in [('Measured', 'measured'), ('Reserved; actual unknown', 'unknown_at_reservation'),
                                            ('Unclassified', 'unclassified'), ('Budget accounted', 'budget_accounted')])),
                  '<p>' + escape(report['aggregation_note']) + '</p>',
                  details('Accounting breakdown', pre(preview(combined)))])
    for index, run in enumerate(report['runs']):
        prefix = f'run-{index}'
        events_file = files.records(run, prefix)
        artifacts_file, artifact_entries = files.artifacts(run, prefix)
        sections = {}
        def section(name, title, full, summary, fragments=None):
            filename = files.write(f'{prefix}/{name}.json', files.projection(full, run))
            sections[name] = filename
            page.section(title, prefix + '-' + name, filename,
                         fragments if fragments is not None else [pre(preview(summary))])
            return filename
        identity = {k: v for k, v in run['identity'].items() if k not in ('configuration_receipts', 'lineage')}
        section('identity', f'Run {index + 1}: {run["directory"]}', run['identity'], identity)
        papers = []
        for pi, paper in enumerate(run['extraction']['papers']):
            filename = files.write(f'{prefix}/papers/paper-{pi}.json', files.projection(paper, run))
            outcome = paper['outcome'] or {}
            papers.append(dict(source_id=paper['source_id'], status=paper['status'], pages=outcome.get('pages'),
                               item_counts_by_kind=paper['item_counts_by_kind'], accounting=paper['accounting'], file=filename))
        extraction = {**{k:v for k,v in run['extraction'].items() if k not in ('papers','stops')}, 'papers': papers}
        def paper_rows():
            yield from table(['Paper', 'Status', 'Pages', 'Items', 'Measured USD', 'Reserved unknown USD', 'Evidence'],
                ([escape(short(v)) for v in (p['source_id'], p['status'], p['pages'], sum(p['item_counts_by_kind'].values()),
                    p['accounting']['measured']['cost_usd'], p['accounting']['unknown_at_reservation']['cost_usd'])] +
                 [link(p['file'], 'Paper items and history')] for p in papers))
            yield pre(preview(extraction))
        section('extraction', '2. Extraction per paper and corpus exclusions', {**extraction, 'stops':run['extraction']['stops']}, extraction, paper_rows())
        built = {k:v for k,v in run['construction'].items() if k not in ('commitments','symbol_catalogue','events')}
        built['commitment_count'] = len(run['construction']['commitments'])
        built['file'] = section('construction', '3. Construction and frozen commitments', run['construction'], built)
        trees, trace_summaries, route_summaries, tree_blocks = [], [], [], []
        for ti, trace in enumerate(run['search']['traces']):
            trace_file = f'trees/{prefix}-search-{ti}.json'
            write_json(destination / trace_file, trace)
            export = graph_export(trace_dot(trace), f'{prefix}-search-{ti}', destination, graphviz)
            summary, rows = tree_summary(trace, 'search')
            trees.append(dict(kind='search', begin_seq=trace['begin_seq'], file=trace_file, **summary, **export))
            trace_summaries.append(dict(search_id=trace['search_id'], complete=trace['complete'], file=trace_file, **summary))
            tree_blocks.append(tree_block('Search ' + short(trace['search_id']), summary, rows, trace_file, export))
        for ri, route in enumerate(run['routes']):
            graph = route['graph']
            filename = files.write(f'trees/{prefix}-route-{ri}.json', route)
            export = graph_export(route_dot(graph), f'{prefix}-route-{ri}', destination, graphviz)
            summary, rows = tree_summary(graph, 'route')
            trees.append(dict(kind='route', route_id=graph['id'], seq=route['seq'], file=filename, **summary, **export))
            route_summaries.append(dict(classification=route['classification'], selectable_by_default=route['classification']=='CLOSED-derived', route_id=graph['id'], target=route['target'], polarity=route['polarity'], model_summary=preview(route['model_summary']), file=filename, **summary))
            tree_blocks.append(tree_block('Route ' + short(graph['id']), summary, rows, filename, export))
        for tree in trees:
            if tree['svg'] is None:
                run['gaps'].append(tree['status'] + ': ' + tree['dot'])
        search = {**{k:v for k,v in run['search'].items() if k != 'traces'}, 'traces': trace_summaries, 'tree_exports':trees}
        search_file = section('search', '4. Search-tree tracing', search, search,
                             tree_blocks or ['<p>No recorded search trees or routes.</p>'])
        conflict_summary = {k:v for k,v in run['conflicts'].items() if k not in ('tier1','tier2','semantic_classifications','resolution_candidates')}
        conflict_summary['resolution_candidate_count'] = len(run['conflicts']['resolution_candidates'])
        conflict_summary['file'] = section('conflicts', 'Tier 1 repairs and Tier 2 conflicts', run['conflicts'], conflict_summary)
        section('routes', '5. Routes for selection', dict(routes=route_summaries, unassigned_audits=run['unassigned_audits']), route_summaries)
        account = {k:v for k,v in run['accounting'].items() if k not in ('timeline','unresolved_dispatches','unfinalized_measured_responses')}
        account['file'] = section('accounting', '6. Accounting', run['accounting'], account)
        section('human', '7. Human actions log', run['human_actions'], run['human_actions'])
        gaps = dict(gaps=run['gaps'], failure_receipts=run['failure_receipts'], limit_receipts=run['limit_receipts'])
        section('gaps', '8. Gaps and limits', gaps, gaps)
        page.md.append(f'Gaps: {short("; ".join(run["gaps"]), 4000)}\n')
        sections['artifacts'] = artifacts_file
        page.section('Run artifacts (not independently authenticated)', prefix+'-artifacts', artifacts_file,
                     ('<p>'+escape(short(a['path']))+' · '+(link(a['file']) if a.get('file') else escape(a.get('status','')) )+'</p>' for a in artifact_entries))
        exported.append(dict(run_id=prefix, directory=run['directory'], identity=identity, extraction=extraction, construction=built,
                             search=dict(traces=trace_summaries,file=search_file), conflicts=conflict_summary, routes=route_summaries,
                             accounting=account, gaps=run['gaps'], tree_exports=trees, sections=sections,
                             events_file=events_file, artifacts_file=artifacts_file))
    event_index = files.write('events/index.json', list(files.events.values()))
    page.section('Original event inventory · Imported by', 'events', event_index,
                 ('<p>'+link(e['file'], short(e['stage']))+' · '+escape(short(e['timestamp']))+
                  ' · Original in: '+', '.join(link('#'+r+'-identity', r) for r in e['original_in'])+' · Imported by: '+', '.join(link('#'+r+'-identity', r) for r in e['imported_by'])+'</p>' for e in files.events.values()))
    files.write('data.json', dict(format_version=2, runs=exported, accounting=combined, accounting_file=account_file,
                                 events_index=event_index, aggregation_note=report['aggregation_note'],
                                 html_truncated_sections=page.truncated))
    page.finish()


def tree_block(title, summary, rows, filename, export):
    body = pre(preview(summary)) + '<p>' + link(filename, 'Full tree JSON') + ' · ' + link(export['dot'], 'Full DOT')
    if export['svg']:
        body += ' · ' + link(export['svg'], 'Full SVG')
    body += '</p><p>First ' + str(TREE_LEVELS) + ' levels; at most ' + str(TREE_NODES) + ' nodes. Remaining nodes are in the linked files.</p>'
    body += ''.join('<p>' + ' · '.join(escape(short(v)) for v in row) + '</p>' for row in rows)
    return details(title, body)
