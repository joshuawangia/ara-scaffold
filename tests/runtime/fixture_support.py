"""Placeholder-only fixtures for runtime orchestration, never a production engine."""
import json
from pathlib import Path

from ara.runtime.cache import canonical
from ara.runtime.calls import ModelCalls
from ara.runtime.providers import mock_key
from ara.types import (Commitment, CommitmentSet, Formula, Proposition, RouteGraph,
                       RouteNode, EngineDecision, RunEvent)

ROOT = Path(__file__).resolve().parents[2]
T = CommitmentSet((Commitment('t1', 'P', 'placeholder:1', Formula('atom', name='P')),
                   Commitment('t2', 'Q', 'placeholder:2', Formula('atom', name='Q'))))
TARGETS = (Proposition('p', 'P', Formula('atom', name='P')), Proposition('q', 'Q', Formula('atom', name='Q')))
DRAFT = {'title': 'P', 'body': '[[node:n:p]] ' + ' '.join(['P'] * 150), 'bibliography': []}


class FakeEngine:
    def __init__(self, calls):
        self.calls = calls
        self.goals = []

    def analyse(self, target, commitments):
        from ara.engine import AnalysisResult
        from ara.engine.search import SearchResult
        from ara.types import negate_proposition
        results = []
        for goal in (target, negate_proposition(target)):
            routes = self.search(goal, commitments)
            results.append(SearchResult(goal, routes, sum(r.status == 'CLOSED' for r in routes), 1, False))
        return AnalysisResult(*results, (), (), ())

    def search(self, target, commitments):
        self.goals.append(target)
        t_id = self.calls.map_leaf(target, commitments)
        self.calls.propose_cuts(target, commitments, ())
        self.calls.log.emit(RunEvent('2026-10-08T00:00:00+00:00', 'license', 'ENGINE',
                                    decision=EngineDecision('discarded', 'test_decision', 'P')))
        closed = t_id != 'open'
        return (RouteGraph('route:' + target.id, 'n:' + target.id,
                           (RouteNode('n:' + target.id, target, 'leaf', t_id),),
                           'CLOSED' if closed else 'OPEN', () if closed else ('n:' + target.id,)),)

    def conflicts(self, routes, commitments):
        # This is just a fixture result. Real conflict correctness belongs to engine tests.
        return {'tier1': [], 'tier2': [], 'independent_closed': 2, 'forward': []}


def canned(config):
    """Produce exact hash keys from an explicit finite request inventory."""
    calls = object.__new__(ModelCalls)
    calls.root, calls.topic, calls.config = ROOT, 'P Q', config
    result = {}
    def add(kind, inputs, output, content=None):
        prompt = calls.render(kind, inputs)[1]
        result[mock_key(kind, prompt)] = {
            'model': config['model'], 'stop_reason': 'end_turn',
            'content': content or [{'type': 'text', 'text': canonical(output)}],
            'usage': {'input_tokens': 5, 'output_tokens': 3}}
    add('build_t', {'literature': (ROOT / 'tests/fixtures/runtime/smoke-literature.txt').read_text(),
                    'audience': 'runtime audience'}, T.to_dict())
    from ara.runtime.search_alignment import catalogue_inputs
    vocabulary = catalogue_inputs(ROOT / 'tests/fixtures/runtime', T)
    add('propose_targets', {'commitments': T.to_dict(), 'count': 2, 'named_position': None, **vocabulary},
        {'targets': [t.to_dict() for t in TARGETS]})
    from ara.types import negate_proposition
    for target in TARGETS:
        for goal in (target, negate_proposition(target)):
            add('map_leaf', {'leaf': goal.to_dict(), 'commitments': T.to_dict()},
                {'t_id': {'p': 't1', 'q': 't2'}.get(goal.id, 'open')})
            add('propose_cuts', {'goal': goal.to_dict(), 'commitments': T.to_dict(), 'bank': [],
                'proposal_limit': 3, 'attempt_budget': 1, **vocabulary}, {'proposals': []})
    route = RouteGraph('route:p', 'n:p', (RouteNode('n:p', TARGETS[0], 'leaf', 't1'),), 'CLOSED')
    add('write_essay', {'outline': calls.essay_outline(route), 'word_limit': 300, 'minimum_words': 150, 'feedback': []}, DRAFT)
    add('audit_essay', calls.audit_inputs(route, DRAFT),
        {'labels': [{'sentence': 1, 'node_ids': ['n:p'], 'asserts_premise_or_inference_not_in_outline': False}]})
    content = [{'type': 'text', 'text': 'P'}]
    add('search_evidence', {'draft': DRAFT, 'items': []}, {}, content)
    add('verify_originality_citations', {'draft': DRAFT, 'items': [],
        'evidence': {'text': 'P', 'urls': [], 'content': content}},
        {'originality': {'assessment': 'unverified', 'evidence_urls': [], 'detail': 'P'}, 'items': []})
    return result
