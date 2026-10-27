"""Display and selection policy; the engine's historical CLOSED codec is unchanged."""


def route_classification(route):
    if route.status != 'CLOSED':
        return route.status
    nodes = {n.id:n for n in route.nodes}
    pending, seen = [route.root_id], set()
    while pending:
        id = pending.pop()
        if id in seen:
            continue
        seen.add(id)
        node = nodes[id]
        if node.kind == 'inference' and node.proposal is not None:
            return 'CLOSED-derived'
        pending.extend(node.children)
    return 'CLOSED-trivial'


def selectable_routes(routes):
    return tuple(r for r in routes if route_classification(r) == 'CLOSED-derived')
