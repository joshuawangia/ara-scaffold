"""Cross-source alignment: placeholder definitions through the native freeze."""
from copy import deepcopy
import json

import pytest

from ara.types import Commitment, CommitmentSet, Formula, Term
from ara.runtime.cache import canonical, digest
from ara.runtime.commitment_provenance import source_provenance, make_commitment_provenance
from ara.runtime.frozen_catalogue import make_catalogue
from test_extraction import rig, ROOT, response


def fixture(negative=False, predicate=False):
    symbols, commitments, rows = [], [], {}
    for name, source in [('P', 'a'), ('Q', 'b'), ('R', 'c')]:
        formula = Formula('predicate', name=name, terms=(Term('constant', 'a'),)) if predicate else Formula('atom', name=name)
        if negative and name == 'Q': formula = formula.negated()
        commitments.append(Commitment(name, 'P Q', source + ':1', formula))
        symbols.append(dict(name=name, kind='predicate' if predicate else 'atom', arity=int(predicate), definition='P Q', evidence_ids=[name]))
        rows[name] = source_provenance(dict(id=name, source_id=source, attributed_to=source,
            page_start=1, page_end=1, attribution='author_claim', kind='premise', text='P Q'), [source])
    if predicate: symbols.append(dict(name='a',kind='constant',arity=0,definition='a',evidence_ids=['P','Q','R']))
    return CommitmentSet(tuple(commitments)), symbols, rows


def judgment(left='P', right='Q', relation='same_content'):
    return dict(left=left, right=right, relation=relation, reason='P Q')


def test_candidates_are_bounded_cross_source_content_pairs():
    from ara.runtime.symbol_alignment import candidate_pairs
    t, symbols, rows = fixture()
    pairs = candidate_pairs(symbols, rows)
    assert [(p['left'], p['right']) for p in pairs] == [('P','Q'),('P','R'),('Q','R')]
    assert len(candidate_pairs(symbols, rows, limit=1)) == 1
    rows['Q']['source_id'] = 'a'
    assert ('P','Q') not in [(p['left'],p['right']) for p in candidate_pairs(symbols, rows)]
    symbols[2]['definition'] = 'S'
    assert candidate_pairs(symbols, rows) == []
    for invalid in (-1, True, '1'):
        with pytest.raises(ValueError): candidate_pairs(symbols, rows, limit=invalid)


def test_same_content_rewrites_transitively_and_keeps_originals():
    from ara.runtime.symbol_alignment import apply_judgments
    t, symbols, rows = fixture(predicate=True)
    original = deepcopy((t.to_dict(), symbols, rows))
    aligned, catalogue, provenance, mapping = apply_judgments(t, symbols, rows,
        [judgment(), judgment('Q','R')])
    assert mapping == {'P':'P','Q':'P','R':'P','a':'a'}
    assert {c.formula.name for c in aligned.commitments} == {'P'}
    assert next(s for s in catalogue if s['name']=='P')['evidence_ids'] == ['P','Q','R']
    assert provenance == rows
    assert (t.to_dict(), symbols, rows) == original
    assert [c.citation for c in aligned.commitments] == [c.citation for c in t.commitments]


@pytest.mark.parametrize('relation', ['entails_left_right','entails_right_left','contrary'])
def test_bridges_are_explicit_quantified_model_alignment(relation):
    from ara.runtime.symbol_alignment import apply_judgments
    t, symbols, rows = fixture(predicate=True)
    # Make all source formulas vacuous so any bridge remains consistent.
    t = CommitmentSet(tuple(Commitment(c.id,c.text,c.citation,Formula('implies',(c.formula,c.formula))) for c in t.commitments))
    result, catalogue, provenance, _ = apply_judgments(t,symbols,rows,[judgment(relation=relation)])
    bridge = result.commitments[-1]
    assert bridge.id.startswith('alignment:') and bridge.formula.op == 'forall'
    row = provenance[bridge.id]
    assert row['stance'] == 'model_alignment' and row['kind'] == 'alignment' and row['source_id'] is None
    assert row['source_ids'] == ['a','b'] and row['evidence_ids'] == ['P','Q']
    assert row['definitions'] == symbols[:2]
    assert 'a:1' in bridge.citation and 'b:1' in bridge.citation
    from ara.formal import entails
    p, q = [c.formula.args[0] for c in t.commitments[:2]]
    conclusion = Formula('not',(Formula('and',(p,q)),)) if relation=='contrary' else Formula('implies',(p,q) if relation=='entails_left_right' else (q,p))
    assert entails((bridge.formula,), conclusion, 1000) == 'SOLVER_UNSAT'


def test_alignment_refuses_inconsistent_set_type_errors_and_duplicates():
    from ara.runtime.symbol_alignment import apply_judgments
    t, symbols, rows = fixture(negative=True)
    with pytest.raises(ValueError, match='consistency'): apply_judgments(t,symbols,rows,[judgment()])
    with pytest.raises(ValueError, match='duplicate'): apply_judgments(t,symbols,rows,[judgment(),judgment()])
    symbols[1].update(kind='predicate',arity=1)
    with pytest.raises(ValueError): apply_judgments(t,symbols,rows,[judgment()])


def configure_judge(rig, monkeypatch, relation='entails_left_right'):
    calls = rig[0]
    from ara.runtime.providers import Response
    requests = []
    def complete(kind,prompt,schema,maximum):
        assert kind=='judge_symbol_alignment'
        inputs=json.loads(prompt.split('\nINPUT_JSON\n')[1]); requests.append(inputs)
        pair=inputs['candidate']
        return Response(response(judgment(pair['left']['name'],pair['right']['name'],relation)))
    monkeypatch.setattr(calls.provider,'complete',complete)
    return calls,requests


def test_native_freeze_persists_alignment_receipt_and_validates_replay(rig, monkeypatch):
    from ara.bank import load_bank
    from ara.runtime.orchestration import prepare_commitments
    from ara.runtime.commitment_provenance import load_commitment_provenance, validate_commitment_provenance
    calls,requests=configure_judge(rig,monkeypatch)
    t,symbols,rows=fixture()
    monkeypatch.setattr(calls,'build_t',lambda *_:t)
    calls.log.record('run_started',config=calls.config,topic='P',audience='P',literature='P',bank_version=load_bank(ROOT/'bank').bank_version)
    calls.log.record('build_t_merged',commitments=t.to_dict(),symbols=symbols,provenance=rows)
    result=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert len(requests)==3 and len(result.commitments)==6
    directory=calls.log.path.parent
    catalogue=json.loads((directory/'frozen-t.json').read_text())['symbol_catalogue']
    meta=load_commitment_provenance(directory,result,catalogue)
    assert meta['schema_version']=='commitment-provenance-v2'
    assert meta['alignment']['original_commitments']==t.to_dict()
    assert meta['alignment']['original_symbols']==symbols
    assert meta['alignment']['status']=='accepted'
    events=calls.log.read(); stages=[e['stage'] for e in events]
    assert stages.index('symbol_alignment_applied') < stages.index('commitment_provenance_frozen') < stages.index('commitments_frozen')
    assert len([e for e in events if e['stage']=='judge_symbol_alignment' and e['label']=='MODEL'])==3
    assert all('commitments_sha256' in r and 'catalogue_sha256' in r for r in requests)
    from ara.runtime.freeze_fork import fork_from_freeze
    destination=directory.parent/'fork'
    _,_,forked=fork_from_freeze(directory,destination,load_bank(ROOT/'bank'))
    assert forked==result
    assert (destination/'commitment-provenance.json').read_bytes()==(directory/'commitment-provenance.json').read_bytes()
    for change in ('mapping','formula','stance'):
        altered=deepcopy(meta)
        if change=='mapping': altered['alignment']['mapping']['Q']='P'
        elif change=='formula': altered['alignment']['original_commitments']['commitments'][0]['formula']['name']='S'
        else: altered['commitments'][result.commitments[-1].id]['stance']='endorsed'
        altered['sha256']=digest(canonical({k:v for k,v in altered.items() if k!='sha256'}))
        with pytest.raises(ValueError): validate_commitment_provenance(altered,result,catalogue)


def test_refused_alignment_is_logged_and_preserves_original_T(rig,monkeypatch):
    from ara.runtime.symbol_alignment import align_symbols
    calls,requests=configure_judge(rig,monkeypatch,'same_content')
    t,symbols,rows=fixture(negative=True)
    result,catalogue,provenance,receipt=align_symbols(calls,t,symbols,rows)
    assert result==t and catalogue==symbols and provenance==rows
    assert receipt['status']=='refused' and 'consistency' in receipt['refusal_reason']
    assert any(e['stage']=='symbol_alignment_refused' for e in calls.log.read())
    make_commitment_provenance(result,make_catalogue(result,catalogue),provenance,alignment=receipt)


def test_alignment_uses_construction_provider_even_on_retry():
    from ara.runtime.providers import stage_settings
    from ara.runtime.construction_stages import dispatch_settings
    config=dict(provider='anthropic',model='P',effort='high',stages={
        'build_t_batch':dict(provider='codex_cli',model='Q'),
        'judge_symbol_alignment':dict(provider='anthropic',model='R'),
        'construction_correction':dict(provider='anthropic',model='S')})
    assert stage_settings(config,'judge_symbol_alignment')['model']=='Q'
    for correction in (False,True):
        assert dispatch_settings(config,'judge_symbol_alignment',correction=correction)[2]['model']=='Q'


def test_solver_unknown_refuses_alignment(rig,monkeypatch):
    import ara.formal
    from ara.runtime.symbol_alignment import align_symbols
    calls,_=configure_judge(rig,monkeypatch)
    monkeypatch.setattr(ara.formal,'entails',lambda *a:'SOLVER_UNKNOWN')
    t,symbols,rows=fixture()
    result,_,_,receipt=align_symbols(calls,t,symbols,rows)
    assert result==t and receipt['status']=='refused'


@pytest.mark.parametrize('endorsed_count', [1,2])
def test_native_search_alignment_is_disclosed_and_needs_two_endorsed_sources(rig,monkeypatch,endorsed_count):
    from ara.bank import load_bank
    from ara.runtime.orchestration import prepare_commitments, NativeEngine, search_all
    from ara.runtime.providers import Response
    from ara.runtime.route_policy import route_contribution
    from ara.types import Proposition
    calls,requests=configure_judge(rig,monkeypatch)
    t,symbols,rows=fixture()
    calls.config.update(construction_alignment_candidates=1,depth_cap=2,node_cap=30,forward_pass_depth=1)
    monkeypatch.setattr(calls,'build_t',lambda *_:t)
    calls.log.record('build_t_merged',commitments=t.to_dict(),symbols=symbols,provenance=rows)
    bank=load_bank(ROOT/'bank')
    result=prepare_commitments(calls,bank,'P','P')
    bridge=result.commitments[-1]
    def complete(kind,prompt,*args):
        inputs=json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind=='map_leaf': data=dict(t_id='open')
        elif kind=='propose_cuts':
            if inputs['goal']['formula']!=Formula('atom',name='S').to_dict(): data=dict(proposals=[])
            else:
                assert inputs['commitment_roles'][bridge.id]['stance']=='model_alignment'
                data=dict(proposals=[dict(bank_id='sign',conclusion_text='S',conclusion_ref='current_goal',
                    premises=[dict(slot=slot,text=c.text,t_id=c.id,scope_id=None) for slot,c in
                        zip(('sign_relation','observed_sign'),(bridge,result.commitments[0]))])])
        elif kind=='formalise_slots': data=dict(slots=[dict(slot=b['slot'],formula=b['formula']) for b in inputs['slot_bindings']])
        elif kind=='answer_cq': data=dict(cq_id=inputs['question']['id'],answered=True,answer='P R',supporting_t_ids=['P','R'] if endorsed_count==2 else ['P'])
        elif kind=='tier1_repair': data=dict(action='unresolved',detail='P',proposals=[])
        else: raise AssertionError(kind)
        return Response(response(data))
    monkeypatch.setattr(calls.provider,'complete',complete)
    engine=NativeEngine(bank,calls)
    assert bridge in engine._engine(result).commitments.commitments
    routes=search_all(calls,engine,result,(Proposition('s','S',Formula('atom',name='S')),))
    closed=next(r for r in routes if r.status=='CLOSED')
    meta=calls.search_vocabulary(result)['commitment_provenance']
    receipt=route_contribution(closed,result,meta)
    assert receipt['classification']==('CLOSED-derived' if endorsed_count==2 else 'CLOSED-single-support')
    assert receipt['alignment_support_ids']==[bridge.id]
    assert receipt['stance_crossings']==[]
    assert bridge.id not in {w['commitment_id'] for w in receipt['paper_support']['matching']}
    assert len(receipt['endorsed_support_ids'])==endorsed_count
    outline=calls.essay_outline(closed)
    assert any(row['stance']=='model_alignment' and row['role']=='alignment_premise' for row in outline['source_roles'])
    assert outline['alignment_disclosure']['judgments']
    from ara.runtime.render import render_tree
    assert 'model_alignment' in render_tree(closed,result,meta)
    from ara.runtime.export import export_run
    export_run(calls.log.path,calls.log.path.parent/'export')
    assert 'model_alignment' in (calls.log.path.parent/'export'/'methodology.md').read_text()


def test_unrelated_and_zero_limit_never_invent_alignment(rig,monkeypatch):
    from ara.runtime.symbol_alignment import align_symbols
    calls,requests=configure_judge(rig,monkeypatch,'unrelated')
    t,symbols,rows=fixture()
    result,_,provenance,receipt=align_symbols(calls,t,symbols,rows)
    assert result==t and provenance==rows and receipt['mapping']=={s['name']:s['name'] for s in symbols}
    calls.config['construction_alignment_candidates']=0
    result,_,_,receipt=align_symbols(calls,t,symbols,rows)
    assert result==t and receipt is None and len(requests)==3


def test_alignment_bridge_cannot_be_source_cq_evidence(rig,monkeypatch):
    from ara.bank import load_bank
    from ara.runtime.orchestration import prepare_commitments
    from ara.runtime.calls import Rejected
    from ara.runtime.providers import Response
    from ara.types import Proposal, PremiseFill
    calls,_=configure_judge(rig,monkeypatch)
    t,symbols,rows=fixture()
    monkeypatch.setattr(calls,'build_t',lambda *_:t)
    calls.log.record('build_t_merged',commitments=t.to_dict(),symbols=symbols,provenance=rows)
    bank=load_bank(ROOT/'bank')
    result=prepare_commitments(calls,bank,'P','P')
    question=bank.get('sign').critical_questions[0]
    monkeypatch.setattr(calls.provider,'complete',lambda *a:Response(response(dict(cq_id=question.id,
        answered=True,answer='P Q',supporting_t_ids=[result.commitments[-1].id]))))
    with pytest.raises(Rejected,match='alignment premises'):
        calls.answer_cq(question,Proposal('sign',(PremiseFill('observed_sign','P','P'), PremiseFill('sign_relation','Q','Q')),'S'),result)


def test_canonical_freeze_report_uses_final_catalogue_and_retains_unframe_history(rig,monkeypatch):
    from ara.bank import load_bank
    from ara.runtime.orchestration import prepare_commitments
    from ara.runtime.report import build_run
    calls,_=configure_judge(rig,monkeypatch,'same_content')
    t,symbols,rows=fixture()
    rows['Q']['definition_unframes']=[dict(kind='symbol',name='Q',author='b',original_definition='b claims that P Q',definition='P Q')]
    monkeypatch.setattr(calls,'build_t',lambda *_:t)
    calls.log.record('build_t_merged',commitments=t.to_dict(),symbols=symbols,provenance=rows)
    result=prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert {c.formula.name for c in result.commitments}=={'P'}
    report=build_run(calls.log.path.parent)
    assert report['construction']['symbol_count']==1
    assert report['construction']['commitment_provenance']['commitments']['Q']['definition_unframes']==rows['Q']['definition_unframes']
    assert report['construction']['commitment_provenance']['alignment']['original_symbols']==symbols


def test_predicate_arity_and_symbol_type_are_not_interchangeable():
    from ara.runtime.symbol_alignment import candidate_pairs,apply_judgments
    t,symbols,rows=fixture()
    q=Formula('predicate',name='Q',terms=(Term('constant','a'),))
    t=CommitmentSet((t.commitments[0],Commitment('Q','P Q','b:1',q),t.commitments[2]))
    symbols[1].update(kind='predicate',arity=1)
    symbols.append(dict(name='a',kind='constant',arity=0,definition='a',evidence_ids=['Q']))
    assert [(p['left'],p['right']) for p in candidate_pairs(symbols,rows)]==[('P','R')]
    with pytest.raises(ValueError,match='signature'): apply_judgments(t,symbols,rows,[judgment(relation='unrelated')])


def test_recorded_solver_refusal_remains_loadable_when_solver_later_resolves(rig,monkeypatch):
    from ara.runtime.symbol_alignment import align_symbols
    import ara.formal
    calls,_=configure_judge(rig,monkeypatch)
    t,symbols,rows=fixture()
    with monkeypatch.context() as patch:
        patch.setattr(ara.formal,'entails',lambda *a:'SOLVER_UNKNOWN')
        result,final_symbols,final_rows,receipt=align_symbols(calls,t,symbols,rows)
    assert receipt['status']=='refused'
    stored=make_commitment_provenance(result,make_catalogue(result,final_symbols),final_rows,alignment=receipt)
    assert stored['alignment']['status']=='refused' and result==t
