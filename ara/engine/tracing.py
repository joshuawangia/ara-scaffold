"""Versioned trace deltas and interned references, independent of persistence."""
from __future__ import annotations

import hashlib
import json

from ara.ports import SearchTraceSink


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def identity(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


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

    def __call__(self, action, **data):
        if self.sink is None:
            return
        if action == 'begin':
            target = data.pop('target')
            formula = target.formula.to_dict()
            self.sink.record('begin', version=2, **data, target=dict(id=target.id,
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
            proposal = data.pop('proposal')
            value = dict(bank_id=proposal.bank_id,
                         conclusion_text_id=self.define('text', proposal.conclusion_text),
                         premises=[dict(slot=p.slot, text_id=self.define('text', p.text),
                                        t_id=p.t_id, scope_id=p.scope_id) for p in proposal.premises])
            data['proposal_id'] = self.define('proposal', value)
        elif action == 'complete':
            data['graph'] = data['graph'].to_dict()
            data['status'] = 'route'
        elif action == 'prune':
            data['status'] = 'pruned'
        self.sink.record(action, **data)
