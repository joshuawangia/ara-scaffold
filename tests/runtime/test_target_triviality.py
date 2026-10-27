"""Placeholder target contribution and selection boundaries."""
import json
from dataclasses import replace

from ara.types import Commitment, CommitmentSet, Formula, Proposition, RouteGraph, RouteNode, Proposal, PremiseFill
from test_search_alignment import P, Q, R, T, GOAL, rig, own_thesis


def test_trivial_target_correction_and_exhaustion(tmp_path):
    def reply(kind, inputs):
        assert kind == 'propose_targets'
        assert inputs['target_policy']['minimum_support_commitments'] == 2
        assert inputs['conditionals'][0]['id'] == 't2'
        return {'targets': [GOAL.to_dict() if 'triviality_feedback' in inputs else Proposition('p', 'P', P).to_dict()]}
    calls, requests = rig(tmp_path, own_thesis(reply))
    assert calls.propose_targets(T, 1) == (GOAL,)
    assert len(requests) == 4
    assert requests[-2][1]['triviality_feedback']['rejected'][0]['reason'] == 'single_commitment_entailment'
    calls, requests = rig(tmp_path/'bad', own_thesis(lambda *_: {'targets': [Proposition('p', 'P', P).to_dict()]}))
    assert calls.propose_targets(T, 1) == ()
    assert len(requests) == 4
    receipts = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='target_triviality_preflight']
    assert len(receipts) == 3
    assert receipts[-1]['status'] == 'rejected_after_two_corrections'


def test_single_commitment_instance_and_attribution():
    from ara.runtime.target_policy import trivial_targets
    from ara.types import Term
    body = Formula('predicate', name='F', terms=(Term('variable','x'),))
    frozen = Formula('forall', (body,), variable='x')
    t = CommitmentSet((Commitment('t', 'P', 'placeholder:1', frozen),))
    instance = Formula('predicate', name='F', terms=(Term('constant','a'),))
    assert trivial_targets((Proposition('p','F(a)',instance),),t)[0]['reason']=='single_commitment_entailment'
    assert trivial_targets((Proposition('p','P argues that Q',Q),),T)[0]['reason']=='attributed_report'
    assert trivial_targets((GOAL,),T)==[]


def test_derived_classification_and_default_selection():
    from ara.runtime.route_policy import route_classification, selectable_routes
    trivial = RouteGraph('t','n',(RouteNode('n',Proposition('p','P',P),'leaf','t1'),),'CLOSED')
    proposal = Proposal('modus_ponens',(PremiseFill('conditional','P -> Q','t2'),PremiseFill('antecedent','P','t1')),'Q')
    derived = RouteGraph('d','n',(RouteNode('n',GOAL,'inference',proposal=proposal,children=('a','b')),
        RouteNode('a',Proposition('a','P -> Q',T.commitments[1].formula),'leaf','t2'),
        RouteNode('b',Proposition('b','P',P),'leaf','t1')),'CLOSED')
    opened = replace(trivial,id='o',status='OPEN',frontier=('n',))
    assert route_classification(trivial)=='CLOSED-single-support'
    assert route_classification(derived)=='CLOSED-derived'
    assert selectable_routes((trivial,derived,opened))==(derived,)
    from ara.runtime.render import render_tree
    assert 'CLOSED-single-support' in render_tree(trivial)
    from ara.runtime.report import route_details
    row={'seq':0,'event':{'payload_json':json.dumps({'graph':trivial.to_dict()})}}
    assert route_details(row,{})['classification']=='CLOSED-contribution-unresolved'


def test_default_cli_lists_but_does_not_offer_trivial(tmp_path,monkeypatch,capsys):
    from ara.runtime.cli import main
    from ara.runtime.logging import EventLog
    log=EventLog(tmp_path/'events.jsonl')
    graph=RouteGraph('t','n',(RouteNode('n',Proposition('p','P',P),'leaf','t1'),),'CLOSED')
    log.record('route',graph=graph.to_dict())
    monkeypatch.setattr('builtins.input',lambda *_: (_ for _ in ()).throw(AssertionError('trivial offered')))
    assert main(['select','--run-dir',str(tmp_path)],calls_factory=lambda *_: (_ for _ in ()).throw(AssertionError('provider')))==0
    assert 'CLOSED-single-support' in capsys.readouterr().out
    assert not any(e['stage']=='select' for e in log.read())


def test_single_premise_entailment_preserves_bindings():
    from ara.runtime.contribution import cached_entails
    direct_instance = lambda p, v: cached_entails((p,), v) == 'SOLVER_UNSAT'
    from ara.types import Term
    x,y=Term('variable','x'),Term('variable','y')
    a,b=Term('constant','a'),Term('constant','b')
    pred=lambda *ts: Formula('predicate',name='F',terms=ts)
    assert not direct_instance(Formula('forall',(pred(x,x),),variable='x'),pred(a,b))
    quantified=Formula('forall',(Formula('forall',(pred(x,y),),variable='y'),),variable='x')
    assert direct_instance(quantified,Formula('forall',(pred(a,y),),variable='y'))
    assert direct_instance(quantified,Formula('forall',(pred(y,y),),variable='y'))


def test_direct_instance_uses_canonical_normalization():
    from ara.runtime.contribution import cached_entails
    direct_instance = lambda p, v: cached_entails((p,), v) == 'SOLVER_UNSAT'
    from ara.types import Term
    body=Formula('predicate',name='F',terms=(Term('variable','x'),))
    pattern=Formula('forall',(Formula('not',(Formula('not',(body,)),)),),variable='x')
    value=Formula('predicate',name='F',terms=(Term('constant','a'),))
    assert direct_instance(pattern,value)
