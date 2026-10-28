"""Versioned trace deltas and interned references, independent of persistence."""
from __future__ import annotations

import hashlib
import json

from ara.ports import SearchTraceSink


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def identity(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


def proposition_metadata(proposition):
    return {k:v for k,v in proposition.to_dict().items() if k not in ('text', 'formula')}


class TraceRecorder:
    def __init__(self, sink: SearchTraceSink | None):
        self.sink = sink
        self.known = set()

    def define(self, kind, value):
        ref = identity(value)
        if (kind, ref) not in self.known:
            self.known.add((kind, ref))
            self.sink.record('definition', kind=kind, ref=ref, value=value)
        return ref

    def proposal_ref(self, proposal):
        value = dict(bank_id=proposal.bank_id,
                     conclusion_text_id=self.define('text', proposal.conclusion_text),
                     premises=[dict(slot=p.slot, text_id=self.define('text', p.text),
                                    t_id=p.t_id, scope_id=p.scope_id) for p in proposal.premises])
        if proposal.conclusion_ref is not None:
            value['conclusion_ref'] = proposal.conclusion_ref
        return self.define('proposal', value)

    def graph(self, graph):
        result = graph.to_dict()
        for node, encoded_node in zip(graph.nodes, result['nodes']):
            encoded_node['proposition'] = dict(**proposition_metadata(node.proposition),
                formula_id=self.define('formula', node.proposition.formula.to_dict()),
                text_id=self.define('text', node.proposition.text))
            del encoded_node['proposal']
            encoded_node['proposal_id'] = self.proposal_ref(node.proposal) if node.proposal else None
        return result

    def __call__(self, action, **data):
        if self.sink is None:
            return
        if action == 'begin':
            target = data.pop('target')
            formula = target.formula.to_dict()
            self.sink.record('begin', version=2, **data, target=dict(**proposition_metadata(target),
                             formula_id=identity(formula), text_id=identity(target.text)))
            self.define('formula', formula)
            self.define('text', target.text)
            return
        if action == 'node':
            node = data.pop('node')
            data.update(node_id=node.id, kind=node.kind, t_id=node.t_id, scope_id=node.scope_id,
                        formula_id=self.define('formula', node.proposition.formula.to_dict()),
                        text_id=self.define('text', node.proposition.text),
                        status='closed' if node.t_id != 'open' or node.kind == 'assumption' else 'open')
        elif action == 'proposal':
            data['proposal_id'] = self.proposal_ref(data.pop('proposal'))
        elif action == 'complete':
            data['graph'] = self.graph(data['graph'])
            data['graph_encoding'] = 'references-v1'
            data['status'] = 'route'
        elif action == 'prune':
            data['status'] = 'pruned'
        self.sink.record(action, **data)
