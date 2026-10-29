"""Placeholder-only fixtures for runtime orchestration, never a production engine."""
import json
from pathlib import Path
from ara.bank import load_bank

from ara.runtime.cache import canonical
from ara.runtime.calls import ModelCalls
from ara.runtime.providers import mock_key
from ara.types import (Commitment, CommitmentSet, Formula, Proposition, RouteGraph,
                       RouteNode, EngineDecision, RunEvent, Proposal, PremiseFill, CQAnswer, Term)

ROOT = Path(__file__).resolve().parents[2]
P, Q, R, S = (Formula('atom', name=n) for n in ('P','Q','R','S'))
T = CommitmentSet((Commitment('t1','R','placeholder:1',R), Commitment('t2','S','placeholder:2',S),
    Commitment('t3','F(a)','placeholder:3',Formula('predicate',name='F',terms=(Term('constant','a'),))),
    Commitment('t4','F(b)','placeholder:4',Formula('predicate',name='F',terms=(Term('constant','b'),)))))
TARGETS = (Proposition('p', 'P', Formula('atom', name='P')), Proposition('q', 'Q', Formula('atom', name='Q')))
DRAFT = {'title': 'P', 'body': '[[node:n:p]][[node:n:p:c]][[node:n:p:a]] ' + ' '.join(['P'] * 150), 'bibliography': []}


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
        return (fixture_route(target),)

    def conflicts(self, routes, commitments):
        # This is just a fixture result. Real conflict correctness belongs to engine tests.
        return {'tier1': [], 'tier2': [], 'independent_closed': 2, 'forward': []}


def fixture_route(target):
    root='n:'+target.id
    if target.id not in ('p','q'):
        return RouteGraph('route:'+target.id,root,(RouteNode(root,target,'leaf','open'),),'OPEN',(root,))
    antecedent,conditional=(T.commitments[i] for i in ((0,2) if target.id=='p' else (1,3)))
    proposal=Proposal('sign',(PremiseFill('sign_relation',conditional.text,conditional.id),
        PremiseFill('observed_sign',antecedent.text,antecedent.id)),target.text,conclusion_ref='current_goal')
    return RouteGraph('route:'+target.id,root,(
        RouteNode(root,target,'inference',proposal=proposal,children=(root+':c',root+':a'),
            cq_answers=tuple(CQAnswer(q.id,'P',True,(conditional.id,antecedent.id)) for q in load_bank(ROOT/'bank').get('sign').critical_questions)),
        RouteNode(root+':c',Proposition('c',conditional.text,conditional.formula),'leaf',conditional.id),
        RouteNode(root+':a',Proposition('a',antecedent.text,antecedent.formula),'leaf',antecedent.id)),'CLOSED')


def canned(config):
    """Produce exact hash keys from an explicit finite request inventory."""
    calls = object.__new__(ModelCalls)
    from types import SimpleNamespace
    calls.log = SimpleNamespace(read=lambda: [])
    calls.root, calls.topic, calls.config = ROOT, 'P Q', config
    result = {}
    def add(kind, inputs, output, content=None):
        if kind in ('map_leaf', 'propose_cuts'):
            from ara.runtime.search_context import leaf_slice
            inputs = leaf_slice(inputs, 8)
        prompt = calls.render(kind, inputs)[1]
        result[mock_key(kind, prompt)] = {
            'model': config['model'], 'stop_reason': 'end_turn',
            'content': content or [{'type': 'text', 'text': canonical(output)}],
            'usage': {'input_tokens': 5, 'output_tokens': 3}}
    add('build_t', {'literature': (ROOT / 'tests/fixtures/runtime/smoke-literature.txt').read_text(),
                    'audience': 'runtime audience'}, T.to_dict())
    from ara.runtime.search_alignment import catalogue_inputs, search_guidance
    from ara.runtime.target_policy import target_context, classifier_inputs
    vocabulary = catalogue_inputs(ROOT / 'tests/fixtures/runtime', T)
    add('propose_targets', {'commitments': T.to_dict(), 'count': 30, 'keep_count': 2, 'attempt': 1, 'attempt_budget': 3, 'named_position': None, 'forward_candidates': [], **vocabulary, **target_context(T, load_bank(ROOT / 'bank'))},
        {'targets': [t.to_dict() for t in TARGETS]})
    from ara.types import negate_proposition
    for target in TARGETS:
        add('classify_target', classifier_inputs(target, vocabulary, T),
            dict(novelty='new_assertion',fidelity='matches',classification='own_thesis', reason='P'))
        for goal in (target, negate_proposition(target)):
            add('map_leaf', dict(leaf=goal.to_dict(), commitments=T.to_dict(), **vocabulary, **search_guidance(goal,T,load_bank(ROOT/'bank').entries)),
                {'t_id': 'open'})
            add('propose_cuts', {'goal': goal.to_dict(), 'commitments': T.to_dict(), 'bank': [],
                'proposal_limit': 3, 'attempt_budget': 2, 'attempt':1, 'rejection_feedback':[], **vocabulary, **search_guidance(goal,T,())}, {'proposals': []})
    route = fixture_route(TARGETS[0])
    add('write_essay', {'outline': calls.essay_outline(route), 'word_limit': 300, 'minimum_words': 150, 'feedback': []}, DRAFT)
    add('audit_essay', calls.audit_inputs(route, DRAFT),
        {'labels': [{'sentence': 1, 'node_ids': ['n:p', 'n:p:c', 'n:p:a'], 'role': 'argument_step', 'citation_supported': True}]})
    content = [{'type': 'text', 'text': 'P'}]
    add('search_evidence', {'draft': DRAFT, 'items': []}, {}, content)
    add('verify_originality_citations', {'draft': DRAFT, 'items': [],
        'evidence': {'text': 'P', 'urls': [], 'content': content}},
        {'originality': {'assessment': 'unverified', 'evidence_urls': [], 'detail': 'P'}, 'items': []})
    return result
