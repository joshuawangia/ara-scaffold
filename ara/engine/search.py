"""Bounded best-first AND/OR route search over validated synchronous ports."""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import heapq
from contextlib import nullcontext
import random
from typing import Mapping, TYPE_CHECKING

from ara.bank import Bank
from ara.ports import CQAnswerer, CutProposer, EventSink, Formaliser, LeafMapper, Tier1Repairer, SearchTraceFactory
from ara.types import CommitmentSet, ProofScope, Proposal, Proposition, Record, RouteGraph, RouteNode
from ara.engine.licensing import Licenser, License, emit
from ara.engine.routes import cq_supported, dialectical_cost, finish, independent_count
from ara.engine.terminus import check_terminus, is_terminus
from ara.engine.tracing import TraceRecorder

if TYPE_CHECKING:
    from ara.engine.conflicts import AnalysisResult


@dataclass(frozen=True)
class EngineConfig(Record):
    depth_cap: int = 6
    node_cap: int = 500
    seed: int = 0
    forward_pass_depth: int = 2
    solver_timeout_ms: int = 1000

    def __post_init__(self):
        super().__post_init__()
        if self.depth_cap < 0 or self.node_cap < 1 or self.forward_pass_depth < 0 or self.solver_timeout_ms < 1:
            raise ValueError('invalid engine bounds')

    @classmethod
    def from_mapping(cls, config: Mapping) -> EngineConfig:
        return cls(**{k: config[k] for k in cls.__dataclass_fields__ if k in config})


@dataclass(frozen=True)
class SearchResult(Record):
    target: Proposition
    routes: tuple[RouteGraph, ...]
    independent_closed_routes: int
    nodes_created: int
    truncated: bool


@dataclass
class _State:
    graph: RouteGraph
    depths: dict[str, int]
    contexts: dict[str, tuple[tuple[str, Proposition], ...]]
    ancestors: dict[str, tuple[str, ...]]
    blocked: frozenset[str] = frozenset()


class Engine:
    def __init__(self, bank: Bank, commitments: CommitmentSet, proposer: CutProposer,
                 formaliser: Formaliser, leaf_mapper: LeafMapper, cq_answerer: CQAnswerer,
                 repairer: Tier1Repairer, sink: EventSink, config: EngineConfig | None = None,
                 traces: SearchTraceFactory | None = None):
        self.bank, self.commitments, self.proposer = bank, commitments, proposer
        self.formaliser, self.leaf_mapper, self.cq_answerer = formaliser, leaf_mapper, cq_answerer
        self.repairer, self.sink, self.config = repairer, sink, config or EngineConfig()
        self.licenser = Licenser(bank, formaliser, sink, self.config.solver_timeout_ms, commitments)
        self._licenses: list[tuple[Proposal, License]] = []
        self._search_serial = 0
        self.traces = traces

    def _leaf(self, node_id: str, p: Proposition, t_id: str, context) -> RouteNode:
        p = replace(p, id=node_id)
        for scope_id, assumption in reversed(context):
            if p.formula.canonical() == assumption.formula.canonical():
                emit(self.sink, 'licensed', 'SCOPED_ASSUMPTION', node_id=node_id)
                return RouteNode(node_id, p, 'assumption', scope_id=scope_id)
        if t_id == 'open':
            t_id = self.leaf_mapper.map_leaf(p, self.commitments)
        closed = check_terminus(p, t_id, self.commitments, self.sink, node_id)
        return RouteNode(node_id, p, 'leaf', t_id=t_id if closed else 'open',
                         scope_id=context[-1][0] if context else None)

    def search(self, target: Proposition) -> SearchResult:
        target = self.licenser.formalise(target)
        prefix = hashlib.sha256(target.formula.canonical().encode()).hexdigest()[:12]
        search_id = f'{prefix}:{self._search_serial}'
        self._search_serial += 1

        context = self.traces.open_search(search_id) if self.traces else nullcontext(None)
        with context as sink:
            return self._search(target, prefix, search_id, TraceRecorder(sink))

    def _search(self, target, prefix, search_id, trace):
        trace('begin', search_id=search_id, target=target, config=self.config.to_dict(),
              bank_version=self.bank.bank_version)
        root = self._leaf('n0', target, 'open', ())
        trace('node', node=root, parent_node_id=None, depth=0)
        graph = RouteGraph(prefix, root.id, (root,))
        queue, completed = [], []
        rng = random.Random(self.config.seed)
        serial, created, truncated = 0, 1, False

        def push(state: _State, parent=None, action="root", **edge):
            nonlocal serial
            trace('state', state_id=serial, parent_state_id=parent, transition=action,
                  status='blocked' if action == 'block' else 'open', **edge)
            cost = dialectical_cost(state.graph.nodes, self.commitments)
            heapq.heappush(queue, (float('inf') if cost is None else cost, rng.random(), serial, state))
            serial += 1

        push(_State(graph, {'n0': 0}, {'n0': ()}, {'n0': ()}))
        while queue:
            _, _, state_id, state = heapq.heappop(queue)
            trace('visit', state_id=state_id)
            candidates = [n for n in state.graph.nodes if n.kind == 'leaf' and n.id not in state.blocked
                          and not is_terminus(n.proposition, n.t_id, self.commitments)]
            if not candidates:
                completed.append(finish(replace(state.graph, id=f'{prefix}:r{len(completed)}'), self.commitments, self.bank))
                trace('complete', state_id=state_id, graph=completed[-1],
                      reason='ROUTE_' + completed[-1].status)
                continue
            node = candidates[0]
            if state.depths[node.id] >= self.config.depth_cap or created >= self.config.node_cap:
                reason = 'DEPTH_CAP' if state.depths[node.id] >= self.config.depth_cap else 'NODE_CAP'
                emit(self.sink, 'discarded', reason, node_id=node.id)
                truncated = True
                push(replace(state, blocked=state.blocked | {node.id}), state_id, 'block',
                     node_id=node.id, reason=reason)
                continue
            if node.proposition.formula.canonical() in state.ancestors[node.id]:
                emit(self.sink, 'discarded', 'CYCLE', node_id=node.id)
                push(replace(state, blocked=state.blocked | {node.id}), state_id, 'block',
                     node_id=node.id, reason='CYCLE')
                continue
            trace('expand', state_id=state_id, node_id=node.id, depth=state.depths[node.id])
            proposals = self.proposer.propose_cuts(node.proposition, self.commitments, self.bank.entries)
            produced, seen = False, set()
            for proposal_index, proposal in enumerate(proposals):
                trace('proposal', state_id=state_id, node_id=node.id,
                      proposal_index=proposal_index, proposal=proposal)
                if proposal.to_json() in seen:
                    emit(self.sink, 'discarded', 'DUPLICATE_PROPOSAL', bank_id=proposal.bank_id, node_id=node.id)
                    trace('prune', state_id=state_id, node_id=node.id, proposal_index=proposal_index,
                          reason='DUPLICATE_PROPOSAL')
                    continue
                seen.add(proposal.to_json())
                license = self.licenser.check(proposal, node.proposition, node.id)
                if not license.licensed:
                    trace('prune', state_id=state_id, node_id=node.id, proposal_index=proposal_index,
                          reason=license.decision.reason_code)
                    continue
                self._licenses.append((proposal, license))
                if created + len(license.premises) > self.config.node_cap:
                    truncated = True
                    emit(self.sink, 'discarded', 'NODE_CAP', bank_id=proposal.bank_id, node_id=node.id)
                    trace('prune', state_id=state_id, node_id=node.id, proposal_index=proposal_index,
                          reason='NODE_CAP')
                    continue
                entry = license.entry
                fills = {p.slot: p for p in proposal.premises}
                new_ids = {p.id: f'n{created + i}' for i, p in enumerate(license.premises)}
                created += len(new_ids)
                contexts = dict(state.contexts)
                depths, ancestors = dict(state.depths), dict(state.ancestors)
                scopes = list(state.graph.scopes)
                slot_context = {p.id: state.contexts[node.id] for p in license.premises}
                if entry.formula_schema:
                    props = {p.id: p for p in license.premises}
                    for scope in entry.formula_schema.scopes:
                        scope_id = f'{node.id}:{scope.id}:{new_ids[scope.assumption_slot]}'
                        assumption = props[scope.assumption_slot]
                        for slot in (scope.assumption_slot, *scope.result_slots):
                            slot_context[slot] += ((scope_id, assumption),)
                        scopes.append(ProofScope(scope_id, new_ids[scope.assumption_slot],
                                                 tuple(new_ids[s] for s in scope.result_slots), node.id))
                children = []
                for p in license.premises:
                    nid, context = new_ids[p.id], slot_context[p.id]
                    children.append(self._leaf(nid, p, fills[p.id].t_id, context))
                    contexts[nid] = context
                    depths[nid] = state.depths[node.id] + 1
                    trace('node', node=children[-1], parent_node_id=node.id, depth=depths[nid])
                    ancestors[nid] = state.ancestors[node.id] + (node.proposition.formula.canonical(),)
                answers = tuple(self.cq_answerer.answer_cq(q, proposal, self.commitments)
                                for q in entry.critical_questions)
                for q, answer in zip(entry.critical_questions, answers):
                    supported = cq_supported(answer, q.id, self.commitments)
                    emit(self.sink, 'licensed' if supported else 'discarded',
                         'CQ_SUPPORTED' if supported else 'CQ_UNSUPPORTED', bank_id=entry.id, node_id=node.id)
                inference = replace(node, kind='inference', t_id='open', proposal=proposal,
                                    children=tuple(c.id for c in children), cq_answers=answers)
                nodes = tuple(inference if n.id == node.id else n for n in state.graph.nodes) + tuple(children)
                push(_State(replace(state.graph, nodes=nodes, scopes=tuple(scopes)), depths, contexts, ancestors, state.blocked),
                     state_id, 'inference', node_id=node.id, proposal_index=proposal_index, bank_id=entry.id,
                     children=[c.id for c in children], commitment_ids=sorted({c.t_id for c in children if c.t_id != 'open'} |
                         {tid for a in answers for tid in a.supporting_t_ids}),
                     cq_answers=[a.to_dict() for a in answers],
                     scopes=[s.to_dict() for s in scopes[len(state.graph.scopes):]])
                produced = True
            if not produced:
                push(replace(state, blocked=state.blocked | {node.id}), state_id, 'block',
                     node_id=node.id, reason='NO_ADMITTED_PROPOSAL')
        routes = tuple(completed)
        for route in routes:
            emit(self.sink, 'licensed' if route.status == 'CLOSED' else 'discarded',
                 f'ROUTE_{route.status}', node_id=route.root_id)
        trace('end', routes=[r.id for r in routes], nodes_created=created, truncated=truncated)
        return SearchResult(target, routes, independent_count(routes, self.commitments), created, truncated)

    def analyse(self, target: Proposition) -> AnalysisResult:
        from ara.engine.conflicts import analyse
        return analyse(self, target)
