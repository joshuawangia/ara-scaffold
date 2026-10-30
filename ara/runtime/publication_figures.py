"""Deterministic SVG layout from frozen route/evidence; no model or dot process."""
from __future__ import annotations

from html import escape
from pathlib import Path
import textwrap

from ara.runtime.cache import canonical, digest
from ara.runtime.writing import source_context

ACCENT = '#345b70'


def _svg(title, rows, links=()):
    """A top-to-bottom route layout, wrapping every label instead of clipping it."""
    width, y = 900, 65
    boxes = []
    positions = {}
    for key, label in rows:
        lines = [line for part in label.split('\n') for line in textwrap.wrap(part, 88, break_long_words=True)]
        height = max(70, 28 + 22 * len(lines))
        positions[key] = (y, height)
        boxes.append(f'<g><rect x="65" y="{y}" width="770" height="{height}" rx="4" fill="#fafafa" stroke="{ACCENT}"/>')
        for i, line in enumerate(lines):
            boxes.append(f'<text x="85" y="{y+28+i*22}">{escape(line)}</text>')
        boxes.append('</g>')
        y += height + 45
    edges = []
    for index, (source, target) in enumerate(links):
        sy, sh = positions[source]
        ty, th = positions[target]
        lane = 16 + index % 5 * 8
        edges.append(f'<path d="M65 {sy+sh/2} H{lane} V{ty+th/2} H62" fill="none" stroke="{ACCENT}" marker-end="url(#arrow)"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {y}" role="img">'
            f'<title>{escape(title)}</title><defs><marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6" fill="{ACCENT}"/></marker></defs>'
            '<style>text { font-family: "Liberation Serif", "Times New Roman", serif; font-size: 18px; fill: #222; }</style>'
            f'<rect width="100%" height="100%" fill="white"/><text x="65" y="32" font-weight="bold">{escape(title)}</text>'
            + ''.join(edges + boxes) + '</svg>\n')


def figure_data(calls, route, citation_receipt=None):
    evidence = source_context(calls, route)
    supports = {s['commitment']['id']: s for s in evidence['supporting_commitments']}
    outline = calls.essay_outline(route)
    schemes = {link['conclusion']: link['scheme'] for link in outline['links']}
    rows, edges, support_rows = [], [], []
    for node in route.nodes:
        source = supports.get(node.t_id)
        label = f'{node.id} — {node.kind}' + ('; conclusion' if node.id == route.root_id else '')
        label += '\n' + node.proposition.text
        if node.id in schemes:
            label += '\nScheme: ' + schemes[node.id]
        if node.cq_answers:
            label += '\nCQ: ' + '; '.join(a.cq_id + (' answered' if a.answered else ' open') for a in node.cq_answers)
        elif node.kind == 'inference':
            label += '\nCQ: no answers recorded'
        if source:
            p = source['provenance']
            if p and p.get('stance') == 'model_alignment':
                label += '\nModel alignment judgment (not source endorsement)'
            else:
                label += '\nSource: ' + (citation_receipt[node.t_id]['display'] if citation_receipt else (p['source_id'] if p else 'unavailable') + '; ' + source['commitment']['citation'])
        rows.append((node.id, label))
        edges.extend((child, node.id) for child in node.children)
    for role in outline.get('source_roles', []):
        source = supports[role['evidence_id']]
        p = source['provenance']
        if p.get('stance') == 'model_alignment':
            support_rows.append((str(len(support_rows)), role['node_id'] +
                ' ← Model alignment judgment (not source endorsement)\n' +
                source['commitment']['text'] + '; definition evidence: ' + ', '.join(p['evidence_ids'])))
            continue
        citation = citation_receipt[role['evidence_id']]['display'] if citation_receipt else source['commitment']['citation']
        support_rows.append((str(len(support_rows)), f"{role['node_id']} ← {citation}\nStance: {p['stance']}; attributed to {p['attributed_to']}; role: {role['role']}"))
    if not support_rows:
        support_rows = [('none', 'Source provenance unavailable; no source support inferred.')]
    result = [dict(id='argument-map', caption='Route premises, inference schemes and conclusion. Arrows follow premise-to-conclusion links; CQ labels report recorded answers.', rows=rows, links=edges),
              dict(id='source-support', caption='Frozen source support by route node, page citation, attribution and stance. Recorded support is not independent verification.', rows=support_rows, links=[])]
    if route.frontier:
        gap_rows = [(id, ('Open commitment: ' if id in route.frontier else '') + label)
                    for id, label in rows]
        result.append(dict(id='gap', caption='Open commitments in the route and their recorded inference path to the conclusion. The conclusion remains conditional on these commitments; the diagram asserts no resolution.', rows=gap_rows, links=edges))
    return result


def generate_figures(calls, route, directory: Path, citation_receipt=None):
    directory.mkdir(parents=True, exist_ok=True)
    manifest = []
    for item in figure_data(calls, route, citation_receipt):
        svg = _svg(item['id'].replace('-', ' ').title(), item['rows'], item['links'])
        name = item['id'] + '.svg'
        (directory / name).write_text(svg)
        manifest.append(dict(id=item['id'], file=name, caption=item['caption'], sha256=digest(svg)))
    (directory / 'manifest.json').write_text(canonical(manifest))
    return manifest
