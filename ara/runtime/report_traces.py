"""Authenticate sidecars and validate trace semantics before claiming completeness."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path

from ara.runtime.cache import canonical, digest
from ara.runtime.logging import LogTampered
from ara.types import RouteGraph


def new_trace(begin_seq, data, authenticated=True, source=None):
    return dict(begin_seq=begin_seq, version=data.get('version'), search_id=data.get('search_id'),
                target=data.get('target') or {'id': '(unknown)'}, states=[], receipts=[], decisions=[],
                complete=False, authenticated=authenticated, source=source, issues=[])


def expand_graph(graph, reference):
    """Resolve an explicitly complete graph; never infer missing state history."""
    def proposal(ref):
        if ref is None:
            return None
        value = reference('proposal', ref)
        return dict(bank_id=value['bank_id'], conclusion_text=reference('text', value['conclusion_text_id']),
                    premises=[dict(slot=p['slot'], text=reference('text', p['text_id']),
                                   t_id=p['t_id'], scope_id=p['scope_id']) for p in value['premises']])
    nodes = []
    for node in graph['nodes']:
        p = node['proposition']
        nodes.append({**{k: v for k, v in node.items() if k != 'proposal_id'},
                      'proposition': dict(id=p['id'], text=reference('text', p['text_id']),
                                          formula=reference('formula', p['formula_id'])),
                      'proposal': proposal(node['proposal_id'])})
    return {**graph, 'nodes': nodes}


def validate_trace(trace):
    rows = [r['payload'] for r in trace['receipts']]
    issues = trace['issues']
    def issue(text):
        if text not in issues:
            issues.append(text)
    version = trace['version']
    if not isinstance(trace['target'], dict) or not isinstance(trace['target'].get('id'), str):
        issue('invalid target inventory')
    if version not in (1, 2):
        issue('unsupported trace version: ' + repr(version))
    if not rows or rows[0].get('action') != 'begin' or sum(r.get('action') == 'begin' for r in rows) != 1:
        issue('missing or duplicate begin receipt')
    ends = [r for r in rows if r.get('action') == 'end']
    if len(ends) != 1 or rows[-1].get('action') != 'end':
        issue('missing, duplicate or misplaced end receipt')
    if version == 1 and any(r.get('version') != 1 or r.get('search_id') != trace['search_id'] for r in rows):
        issue('inconsistent legacy trace identity/version')
    states, roots = {}, []
    for state in trace['states']:
        sid = state.get('state_id')
        if type(sid) is not int or sid < 0:
            issue('invalid state ID')
            continue
        if sid in states:
            issue('duplicate state ID')
        parent = state.get('parent_state_id')
        if parent is None:
            roots.append(sid)
        elif type(parent) is not int or parent not in states:
            issue('state parent absent, cyclic or not recorded before child')
        states[sid] = state
        if (parent is None) != (state.get('transition') == 'root'):
            issue('root transition differs from parent inventory')
        if state.get('transition') not in ('root', 'block', 'inference'):
            issue('unknown state transition')
        if state.get('transition') == 'block' and not state.get('reason'):
            issue('blocked state lacks reason')
    if roots != [0] or not states:
        issue('root state inventory must contain exactly state 0')
    definitions = {}
    if version == 2:
        for row in rows:
            action = row.get('action')
            if action == 'definition':
                key = (row.get('kind'), row.get('ref'))
                if any(not isinstance(v, str) for v in key):
                    issue('invalid definition reference')
                    continue
                if key in definitions or row['ref'] != digest(canonical(row.get('value'))):
                    issue('duplicate or invalid content-addressed definition')
                definitions[key] = row.get('value')
    def reference(kind, ref):
        if not isinstance(ref, str) or (kind, ref) not in definitions:
            issue('unresolved ' + kind + ' reference')
            return None
        return definitions[kind, ref]

    terminals = [r for r in rows if r.get('action') == 'complete']
    if version == 2:
        expanded = []
        for row in terminals:
            try:
                if row.get('graph_encoding') != 'references-v1':
                    raise ValueError('unsupported terminal graph encoding')
                expanded.append({**row, 'graph': expand_graph(row['graph'], reference)})
            except (KeyError, TypeError, ValueError, AttributeError):
                issue('invalid terminal graph fields or references')
                expanded.append(row)
        terminals = expanded
    trace['completed_routes'] = terminals
    terminal_states = [r.get('state_id') for r in terminals]
    if any(type(s) is not int for s in terminal_states):
        issue('invalid completion state ID')
    else:
        parents = {s.get('parent_state_id') for s in states.values() if type(s.get('parent_state_id')) is int}
        if len(set(terminal_states)) != len(terminal_states) or set(terminal_states) != set(states) - parents:
            issue('terminal state completion coverage mismatch')
    graphs = []
    for row in terminals:
        graph = row.get('graph')
        if not isinstance(graph, dict) or not isinstance(graph.get('nodes'), list):
            issue('completion lacks a full route graph')
            continue
        graphs.append(graph)
        try:
            RouteGraph.from_dict(graph)
        except (TypeError, ValueError):
            issue('invalid terminal graph fields')
            continue
        nodes = graph['nodes']
        ids = [n.get('id') for n in nodes if isinstance(n, dict)]
        if (len(ids) != len(nodes) or any(not isinstance(n, str) for n in ids) or
                len(set(ids)) != len(ids) or graph.get('root_id') not in ids):
            issue('invalid terminal graph node/root inventory')
            continue
        if any(c not in ids for n in nodes for c in n.get('children', [])):
            issue('terminal graph references an absent child')
        by_id = {n['id']: n for n in nodes}
        pending, visited = [graph['root_id']], set()
        while pending:
            nid = pending.pop()
            if nid in visited:
                issue('terminal graph has repeated or cyclic ancestry')
                continue
            visited.add(nid)
            pending.extend(by_id.get(nid, {}).get('children', []))
        if visited != set(ids):
            issue('terminal graph contains unreachable nodes')
        if row.get('reason') != 'ROUTE_' + str(graph.get('status')):
            issue('terminal graph status and completion reason differ')
    route_ids = [g.get('id') for g in graphs]
    if any(not isinstance(r, str) for r in route_ids):
        issue('invalid terminal route ID')
    elif len(set(route_ids)) != len(route_ids):
        issue('duplicate terminal route ID')
    if len(ends) == 1 and Counter(ends[0].get('routes', [])) != Counter(route_ids):
        issue('declared routes differ from completed routes')

    if version == 2:
        nodes, proposals = {}, {}
        for row in rows:
            action = row.get('action')
            if action == 'state' and row.get('status') != ('blocked' if row.get('transition') == 'block' else 'open'):
                issue('state status differs from transition')
            if action == 'complete' and row.get('status') != 'route':
                issue('completion lacks route status')
            if action == 'prune' and row.get('status') != 'pruned':
                issue('prune lacks pruned status')
            if action not in ('begin', 'definition', 'node', 'proposal', 'state', 'visit', 'expand', 'prune', 'complete', 'end'):
                issue('unsupported trace action')
            if action == 'node':
                nid = row.get('node_id')
                if not isinstance(nid, str) or nid in nodes:
                    issue('duplicate or invalid proof node ID')
                    continue
                parent = row.get('parent_node_id')
                if parent is None:
                    if nid != 'n0' or row.get('depth') != 0:
                        issue('invalid proof root')
                elif (parent not in nodes or type(row.get('depth')) is not int or
                      row['depth'] != nodes[parent]['depth'] + 1):
                    issue('proof node parent/depth mismatch')
                nodes[nid] = row
            elif action == 'proposal':
                key = (row.get('state_id'), row.get('proposal_index'))
                if any(type(k) is not int for k in key) or key in proposals:
                    issue('duplicate or invalid proposal identity')
                else:
                    proposals[key] = row
        for node in nodes.values():
            reference('formula', node.get('formula_id'))
            reference('text', node.get('text_id'))
        for (kind, _), value in definitions.items():
            if kind == 'proposal':
                if not isinstance(value, dict):
                    issue('invalid proposal definition')
                    continue
                reference('text', value.get('conclusion_text_id'))
                for premise in value.get('premises', []):
                    reference('text', premise.get('text_id'))
        for row in rows:
            action = row.get('action')
            if action in ('visit', 'expand', 'proposal', 'prune') and row.get('state_id') not in states:
                issue('transition references an absent state')
            if action in ('expand', 'proposal', 'prune') and row.get('node_id') not in nodes:
                issue('transition references an absent proof node')
            if action == 'proposal':
                reference('proposal', row.get('proposal_id'))
            if action == 'prune' and ((row.get('state_id'), row.get('proposal_index')) not in proposals or not row.get('reason')):
                issue('prune lacks a recorded proposal or reason')
        for state in states.values():
            if state.get('transition') != 'root' and state.get('node_id') not in nodes:
                issue('state delta references an absent proof node')
            if state.get('transition') == 'inference':
                candidate = proposals.get((state.get('parent_state_id'), state.get('proposal_index')))
                if candidate is None or state.get('node_id') not in nodes or any(n not in nodes for n in state.get('children', [])):
                    issue('inference delta lacks its proposal or proof nodes')
                elif (reference('proposal', candidate.get('proposal_id')) or {}).get('bank_id') != state.get('bank_id'):
                    issue('inference delta rule differs from proposal')
        if 'n0' not in nodes or sum(n.get('parent_node_id') is None for n in nodes.values()) != 1:
            issue('proof root inventory mismatch')
        if len(ends) == 1 and ends[0].get('nodes_created') != len(nodes):
            issue('created proof node inventory mismatch')
        target = trace['target']
        if isinstance(target, dict) and nodes.get('n0', {}).get('formula_id') != target.get('formula_id'):
            issue('proof root differs from target formula')
        if isinstance(target, dict):
            trace['target'] = dict(id=target.get('id', '(unknown)'),
                                   text=reference('text', target.get('text_id')),
                                   formula=reference('formula', target.get('formula_id')))
        trace['nodes'] = list(nodes.values())
        # Compare each completed graph with its explicit state path, without
        # reconstructing or storing full intermediate graphs.
        for row in terminals:
            sid, path, visited = row.get('state_id'), [], set()
            while type(sid) is int and sid in states and sid not in visited:
                visited.add(sid)
                path.append(states[sid])
                sid = states[sid].get('parent_state_id')
            expected = {'n0'}
            inferences = {}
            for state in reversed(path):
                if state.get('transition') == 'inference':
                    if state.get('node_id') not in expected:
                        issue('inference expands a node outside its state branch')
                    expected.update(state.get('children', []))
                    inferences[state.get('node_id')] = state
            graph = row.get('graph', {})
            if graph.get('root_id') != 'n0':
                issue('terminal graph root differs from proof root')
            if expected != {n.get('id') for n in graph.get('nodes', [])}:
                issue('terminal graph differs from its recorded delta path')
            for node in graph.get('nodes', []):
                recorded = nodes.get(node.get('id'), {})
                if (node.get('proposition', {}).get('formula') != reference('formula', recorded.get('formula_id')) or
                        node.get('proposition', {}).get('text') != reference('text', recorded.get('text_id'))):
                    issue('terminal proposition differs from its node definition')
                inference = inferences.get(node.get('id'))
                if inference is not None:
                    if (node.get('kind') != 'inference' or node.get('children') != inference.get('children') or
                            node.get('cq_answers') != inference.get('cq_answers') or
                            (node.get('proposal') or {}).get('bank_id') != inference.get('bank_id')):
                        issue('terminal inference differs from its delta')
                elif node.get('kind') != recorded.get('kind') or node.get('t_id') != recorded.get('t_id'):
                    issue('terminal leaf differs from its node definition')
    if not trace['authenticated']:
        issue('sidecar has no verified chained seal')
    trace['complete'] = not issues


def read_sidecar(directory, receipt):
    relative = Path(receipt['path'])
    if relative.is_absolute() or len(relative.parts) != 2 or relative.parts[0] != 'search-traces' or relative.suffix != '.jsonl':
        raise ValueError('invalid search sidecar path')
    candidates = [directory / relative]
    if receipt.get('source_log'):
        candidates.append(Path(receipt['source_log']).parent / relative)
    for path in candidates:
        if path.exists():
            if path.is_symlink() or path.parent.is_symlink():
                raise ValueError('search sidecar symlink refused')
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != receipt['sha256']:
                raise LogTampered('search sidecar hash mismatch: ' + str(path))
            lines = raw.splitlines(keepends=True)
            if len(lines) != receipt['line_count'] or any(not line.endswith(b'\n') for line in lines):
                raise LogTampered('search sidecar line count/termination mismatch: ' + str(path))
            rows = [json.loads(line) for line in lines]
            if any(not isinstance(r, dict) or r.get('seq') != i for i, r in enumerate(rows)):
                raise ValueError('invalid search sidecar sequence')
            return rows, path
    return None, candidates[0]


def collect_traces(records, directory, compact):
    traces, active, context, unassigned = [], None, {}, []
    for row in records:
        event = row['event']
        data = json.loads(event['payload_json'])
        if event['stage'] == 'search_trace':
            if data.get('action') == 'begin':
                active = new_trace(row['seq'], data)
                traces.append(active)
                context = {}
            if active is None or data.get('search_id') != active['search_id']:
                unassigned.append(compact(row))
                continue
            active['receipts'].append(compact(row))
            if data.get('action') in ('visit', 'expand', 'proposal'):
                context = {k: data[k] for k in ('state_id', 'node_id', 'proposal_index') if k in data}
            if data.get('action') == 'complete':
                context = {}
            if data.get('action') == 'state':
                active['states'].append(data)
            if data.get('action') == 'end':
                active = None
        elif event['label'] == 'ENGINE' and active is not None:
            active['decisions'].append(dict(**compact(row), context=dict(context)))
    claimed = set()
    for row in records:
        if row['event']['stage'] != 'search_trace_receipt':
            continue
        seal = json.loads(row['event']['payload_json'])
        rows, path = read_sidecar(directory, seal)
        claimed.add((directory / seal['path']).resolve())
        trace = new_trace(row['seq'], rows[0] if rows else dict(version=seal.get('version'), search_id=seal.get('search_id')),
                          authenticated=rows is not None, source=seal)
        if rows is None:
            trace['issues'].append('sealed sidecar unavailable: ' + str(path))
        elif rows:
            if seal.get('version') != 2 or rows[0].get('search_id') != seal.get('search_id'):
                trace['issues'].append('sidecar seal identity/version mismatch')
            trace['receipts'] = [dict(seq=r['seq'], stage='search_trace', label='SYSTEM', payload=r) for r in rows]
            trace['states'] = [r for r in rows if r.get('action') == 'state']
        traces.append(trace)
    for path in sorted((directory / 'search-traces').glob('*.jsonl')):
        if path.resolve() not in claimed:
            trace = new_trace(None, {'search_id': path.stem}, authenticated=False, source={'path': str(path.relative_to(directory))})
            trace['issues'].append('unclosed sidecar: no chained hash receipt; content not interpreted')
            traces.append(trace)
    for trace in traces:
        try:
            validate_trace(trace)
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            trace['issues'].append('invalid trace fields: ' + str(exc))
            trace['complete'] = False
    return dict(traces=traces, unassigned_trace_receipts=unassigned,
                logged_searches=[compact(r) for r in records if r['event']['stage'] in
                                 ('candidates', 'analysis_started', 'search_started', 'search_finished')],
                engine_decisions=[compact(r) for r in records if r['event']['label'] == 'ENGINE'],
                conflicts_and_robustness=[compact(r) for r in records if r['event']['stage'] == 'conflicts_and_robustness'])
