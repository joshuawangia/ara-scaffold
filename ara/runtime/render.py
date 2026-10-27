"""Persist engine-owned graphs and render their structure without re-evaluating it."""
from pathlib import Path

from ara.runtime.cache import digest
from ara.types import RouteGraph
from ara.runtime.route_policy import route_classification


def render_tree(graph: RouteGraph) -> str:
    nodes = {n.id: n for n in graph.nodes}
    lines = [f'{graph.id} [{route_classification(graph)}] frontier={list(graph.frontier)}']
    def visit(node_id: str, indent: str, ancestors: frozenset[str]):
        if node_id in ancestors:
            lines.append(f'{indent}{node_id} [cycle]')
            return
        node = nodes.get(node_id)
        if node is None:
            raise ValueError(f'graph references absent node: {node_id}')
        lines.append(f'{indent}{node.id}: {node.proposition.text} [{node.kind}; T={node.t_id}]')
        for child in node.children:
            visit(child, indent + '  ', ancestors | {node_id})
    visit(graph.root_id, '', frozenset())
    return '\n'.join(lines) + '\n'


def save_route(directory: Path, graph: RouteGraph) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f'{digest(graph.id)}.json'
    path.write_text(graph.to_json() + '\n')
    path.with_suffix('.txt').write_text(render_tree(graph))
    return path
