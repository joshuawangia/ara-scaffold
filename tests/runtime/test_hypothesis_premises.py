"""Disclosed hypotheses are premises, never sources or source-paper credit."""
from dataclasses import replace
import json
import pytest
from ara.types import Commitment, CommitmentSet, Formula
from test_cross_paper import frozen_metadata

P, Q, R = (Formula('atom', name=n) for n in ('P','Q','R'))
H = Formula('implies', (Formula('and', (P,Q)), R))


def configured(formula=H):
    return dict(id='hypothesis:h', text='(P and Q) implies R', formula=formula.to_dict(),
        rationale='P Q R', proposer='operator', linked_gap='g', linked_target='r',
        new_symbols=[dict(name='R',kind='atom',arity=0,definition='R')])


def sources():
    t = CommitmentSet((Commitment('p','P','a:1',P),Commitment('q','Q','b:1',Q)))
    catalogue, provenance = frozen_metadata(t, ('a','b'))
    return t, catalogue['symbol_catalogue'], provenance


def test_hypothesis_never_supplies_paper_credit():
    from ara.runtime.bridges import paper_support
    receipt = paper_support([dict(formula_hash='p',support_ids=['p']),dict(formula_hash='h',support_ids=['h'])],
        dict(commitments={'p':dict(stance='endorsed',source_id='a'),
                          'h':dict(kind='hypothesis',stance='proposed',source_id=None)}))
    assert receipt['status'] == 'verified'
    assert receipt['paper_count'] == 1
    assert 'h' not in receipt['commitment_papers']
    assert not receipt['cross_paper_supported']


def test_native_freeze_binds_hypotheses_and_one_freeze(tmp_path, monkeypatch):
    from test_search_alignment import rig, ROOT
    from ara.bank import load_bank
    from ara.runtime.orchestration import prepare_commitments
    from ara.runtime.search_alignment import catalogue_inputs
    t, catalogue, provenance = sources()
    calls, _ = rig(tmp_path, lambda kind, data: pytest.fail(kind))
    (tmp_path/'frozen-t.json').unlink()  # rig supplies an unrelated search freeze.
    calls.config['hypothesis_premises'] = [configured()]
    calls.config['construction_alignment_candidates'] = 0
    calls.log.record('build_t_merged', commitments=t.to_dict(), symbols=catalogue['symbols'], provenance=provenance['commitments'])
    monkeypatch.setattr(calls, 'build_t', lambda *_: t)
    frozen = prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    assert frozen.get('hypothesis:h').formula == H
    metadata = catalogue_inputs(calls.log.path.parent,frozen)
    row = metadata['commitment_provenance']['commitments']['hypothesis:h']
    assert row['kind']=='hypothesis' and row['stance']=='proposed' and row['source_id'] is None
    assert metadata['hypothesis_disclosure']['hypotheses'][0]['id']=='hypothesis:h'
    assert sum(e['stage']=='commitments_frozen' for e in calls.log.read())==1
    assert any(e['stage']=='hypotheses_admitted' for e in calls.log.read())
    from ara.runtime.commitment_provenance import validate_commitment_provenance
    from ara.runtime.cache import canonical,digest
    bad=json.loads(canonical(metadata['commitment_provenance']))
    bad['commitments']['hypothesis:h']['source_id']='a'
    bad['sha256']=digest(canonical({k:v for k,v in bad.items() if k!='sha256'}))
    full=json.loads((calls.log.path.parent/'frozen-t.json').read_text())['symbol_catalogue']
    with pytest.raises(ValueError,match='hypothes'):
        validate_commitment_provenance(bad,frozen,full)


def test_hypothesis_padding_cannot_pass_novelty():
    from ara.runtime.novelty import novelty_check
    t, _, meta=sources()
    t=CommitmentSet(t.commitments+(Commitment('h','R','hypothesis:h',R),))
    meta['commitments']['h']=dict(kind='hypothesis',stance='proposed',source_id=None)
    receipt=novelty_check(R,t,meta,support_ids=('p','q','h'))
    assert receipt['status']=='rejected'
    assert receipt['reason']=='hypothesis_padding'


def test_hypothesis_can_link_two_genuine_papers():
    from ara.runtime.novelty import novelty_check
    t, _, meta=sources()
    t=CommitmentSet(t.commitments+(Commitment('h','(P and Q) implies R','hypothesis:h',H),))
    meta['commitments']['h']=dict(kind='hypothesis',stance='proposed',source_id=None)
    receipt=novelty_check(R,t,meta,support_ids=('p','q','h'))
    assert receipt['status']=='candidate'
    assert receipt['conditional_on']==['h']


def freeze_h(tmp_path, monkeypatch, reply, entry=None):
    from test_search_alignment import rig, ROOT
    from ara.bank import load_bank
    from ara.runtime.orchestration import prepare_commitments
    from ara.runtime.search_alignment import catalogue_inputs
    t, catalogue, provenance=sources()
    calls, requests=rig(tmp_path,reply)
    (tmp_path/'frozen-t.json').unlink()
    calls.config.update(hypothesis_premises=[entry or configured()],construction_alignment_candidates=0,
        node_cap=40,forward_pass_depth=0,semantic_conflict_pair_limit=0,essay_min_words=0)
    calls.log.record('build_t_merged', commitments=t.to_dict(),symbols=catalogue['symbols'],provenance=provenance['commitments'])
    monkeypatch.setattr(calls,'build_t',lambda *_:t)
    bank=load_bank(ROOT/'bank')
    frozen=prepare_commitments(calls,bank,'P','P')
    return calls,bank,frozen,catalogue_inputs(tmp_path,frozen)['commitment_provenance'],requests


def route_reply(kind,data):
    if kind=='map_leaf':
        return dict(t_id=next((c['id'] for c in data['commitments']['commitments'] if c['formula']==data['leaf']['formula']),'open'))
    if kind=='propose_cuts':
        if data['goal']['formula']==R.to_dict():
            bank,slots='modus_ponens',[('conditional','(P and Q) implies R','hypothesis:h'),('antecedent','P and Q','open')]
        elif data['goal']['formula']==Formula('and',(P,Q)).to_dict():
            bank,slots='conjunction_introduction',[('left','P','p'),('right','Q','q')]
        else:return dict(proposals=[])
        return dict(proposals=[dict(bank_id=bank,conclusion_text=data['goal']['text'],conclusion_ref='current_goal',
            premises=[dict(slot=s,text=t,t_id=id,scope_id=None) for s,t,id in slots])])
    if kind=='formalise_slots':
        return dict(slots=[dict(slot=b['slot'],formula=b['formula'] or Formula('and',(P,Q)).to_dict()) for b in data['slot_bindings']])
    pytest.fail(kind)


def test_native_conditional_route_requires_two_real_papers(tmp_path,monkeypatch):
    from ara.types import Proposition
    from ara.runtime.orchestration import NativeEngine
    from ara.runtime.route_policy import route_contribution,selectable_routes
    from ara.runtime.synthesis import forward_candidates
    from ara.runtime.writing import source_context
    calls,bank,t,meta,_=freeze_h(tmp_path,monkeypatch,route_reply)
    result=NativeEngine(bank,calls)._engine(t).search(Proposition('r','R',R))
    selected=selectable_routes(result.routes,t,meta)
    assert selected
    route=selected[0]
    receipt=route_contribution(route,t,meta)
    assert receipt['classification']=='CLOSED-derived'
    assert receipt['conclusion_status']=='conditional on H'
    assert receipt['conditional_on']==['hypothesis:h']
    assert receipt['paper_support']['paper_ids']==['a','b']
    assert receipt['endorsed_support_ids']==['p','q']
    assert not receipt['stance_crossings']
    outline=calls.essay_outline(route)
    assert any(r['role']=='hypothesis_premise' for r in outline['source_roles'])
    evidence=source_context(calls,route)
    assert {b['id'] for b in evidence['allowed_bibliography']}=={'p','q'}
    assert evidence['hypothesis_disclosure']['conditional_on']==['hypothesis:h']
    from ara.runtime.semantic_conflicts import rank_pairs
    # H must not enter a source-pair candidate or attribution lookup.
    vocabulary=calls.search_vocabulary(t)
    pairs=rank_pairs(t,vocabulary['symbol_catalogue'],meta,10)['pairs']
    assert all('hypothesis:h' not in pair['commitment_ids'] for pair in pairs)
    from ara.runtime.report import construction
    from ara.runtime.logging import read_log
    assert construction(read_log(calls.log.path),{})['hypotheses']
    from ara.runtime.export import methodology
    assert 'hypothesis:h' in methodology(calls.log.path)


@pytest.mark.parametrize('mode',['undisclosed','attributed','mixed','valid'])
def test_hypothesis_export_and_typed_audit(tmp_path,monkeypatch,mode):
    from ara.runtime.orchestration import NativeEngine
    from ara.runtime.route_policy import selectable_routes
    from ara.types import Proposition
    from ara.runtime.essay_audit import audit_result
    from ara.runtime.export import export_run
    calls,bank,t,meta,_=freeze_h(tmp_path,monkeypatch,route_reply)
    route=selectable_routes(NativeEngine(bank,calls)._engine(t).search(Proposition('r','R',R)).routes,t,meta)[0]
    calls.log.record('route',graph=route.to_dict())
    body=[];labels=[]
    for i,node in enumerate(route.nodes,1):
        hypothesis=node.t_id=='hypothesis:h'
        text=('This paper proposes (P and Q) implies R' if mode in ('valid','mixed') else
              'a argues that (P and Q) implies R' if mode=='attributed' else '(P and Q) implies R') if hypothesis else 'P Q'
        body.append(f'[[node:{node.id}]] {text}.')
        labels.append(dict(sentence=i,node_ids=[node.id],role='proposed_principle' if hypothesis else 'argument_step',citation_supported=True))
    body.append("\nThis paper's conclusion is conditional on H (hypothesis:h).")
    labels.append(dict(sentence=len(body),node_ids=[],role='framing',citation_supported=True))
    draft=dict(title='P',body='\n'.join(body),bibliography=[])
    inputs=calls.audit_inputs(route,draft)
    # Source claims intentionally lack citations here; isolate H flags from those failures.
    if mode=='mixed':
        hypothesis_label=next(label for label in labels if label['role']=='proposed_principle')
        hypothesis_label['node_ids'].append(next(n.id for n in route.nodes if n.t_id=='p'))
    verdict=audit_result(route,draft,inputs,dict(labels=labels))
    assert bool([f for f in verdict['flags'] if 'hypothesis' in f['reason']]) == (mode!='valid')
    calls.log.record('final_draft',route_id=route.id,draft=draft)
    if mode in ('undisclosed','attributed'):
        with pytest.raises(ValueError,match='hypothesis disclosure'):
            export_run(calls.log.path,tmp_path/'export')
        assert not (tmp_path/'export/essay.txt').exists()
    else:
        from ara.runtime.hypotheses import validate_disclosure
        validate_disclosure(calls.log.read(),route,draft)
        template=calls.render('write_essay',calls.essay_inputs(route))[1]
        assert 'Conditional on H' in template and 'proposed_principle' in template


@pytest.mark.parametrize('change',['inconsistent','missing_symbol','attribution','duplicate','legacy'])
def test_hypothesis_refuses_before_freeze(tmp_path,monkeypatch,change):
    entry=configured()
    if change=='inconsistent':entry.update(formula=P.negated().to_dict(),new_symbols=[])
    elif change=='missing_symbol':entry['new_symbols']=[]
    elif change=='attribution':entry['text']='a argues that R'
    elif change=='duplicate':entry['id']='p'
    if change=='legacy':
        from test_search_alignment import rig,ROOT
        from ara.bank import load_bank
        from ara.runtime.orchestration import prepare_commitments
        calls,_=rig(tmp_path,lambda *_:None)
        calls.config['hypothesis_premises']=[entry]
        monkeypatch.setattr(calls,'build_t',lambda *_:sources()[0])
        with pytest.raises(ValueError,match='hypothesis'):
            prepare_commitments(calls,load_bank(ROOT/'bank'),'P','P')
    else:
        with pytest.raises(ValueError):freeze_h(tmp_path,monkeypatch,route_reply,entry)
    assert not (tmp_path/'commitments.json').exists()
    if change!='legacy':
        assert not (tmp_path/'frozen-t.json').exists()


def test_hypothesis_formalization_uses_logged_normal_gate(tmp_path,monkeypatch):
    entry=configured();entry.pop('formula');entry['formalization_request']='(P and Q) implies R'
    def reply(kind,data):
        assert kind=='formalise'
        assert data['formalization_request']==entry['formalization_request']
        assert {s['name'] for s in data['symbol_catalogue']}=={'P','Q'}
        assert data['new_symbols'][0]['name']=='R'
        return dict(formula=H.to_dict())
    calls,_,t,meta,requests=freeze_h(tmp_path,monkeypatch,reply,entry)
    assert t.get('hypothesis:h').formula==H
    assert [k for k,_ in requests]==['formalise']
    assert any(e['stage']=='formalise' and e['label']=='MODEL' for e in calls.log.read())


def test_hypothesis_is_not_cq_or_bibliography_evidence(tmp_path,monkeypatch):
    from ara.types import CriticalQuestion,Proposal,PremiseFill
    from ara.runtime.calls import Rejected
    def reply(kind,data):
        assert kind=='answer_cq'
        return dict(cq_id=data['question']['id'],answered=True,answer='P Q',supporting_t_ids=['hypothesis:h'])
    calls,bank,t,_,_=freeze_h(tmp_path,monkeypatch,reply)
    entry=next(e for e in bank.entries if e.critical_questions)
    proposal=Proposal(entry.id,tuple(PremiseFill(s.id,'P','p') for s in entry.premise_slots),'R')
    with pytest.raises(Rejected,match='source CQ evidence'):
        calls.answer_cq(entry.critical_questions[0],proposal,t)
    from ara.runtime.citations import local_verdicts
    draft=dict(title='P',body='P [cite:hypothesis:h]',bibliography=[dict(id='hypothesis:h',text='P',url=None)])
    with pytest.raises(Rejected,match='source citation'):
        local_verdicts(calls,draft,[])


def test_hypothesis_native_writer_audit_export_and_figures(tmp_path,monkeypatch):
    from test_calls import ROOT
    from test_search_alignment import rig,raw
    from test_delivery_alignment_citations import aligned_sources
    from ara.runtime.providers import Response
    from ara.runtime.orchestration import NativeEngine,compose
    from ara.runtime.route_policy import selectable_routes
    from ara.runtime.writing import source_context
    from ara.types import Proposition
    calls,_=rig(tmp_path,lambda *_:None)
    (tmp_path/'frozen-t.json').unlink()
    calls.config['hypothesis_premises']=[configured()]
    _,frozen,_=aligned_sources(calls,calls.provider,calls.log,monkeypatch)
    meta=calls.search_vocabulary(frozen)['commitment_provenance']
    def dispatch(kind,prompt,*_):
        data=json.loads(prompt.split('INPUT_JSON\n')[1])
        return Response(raw(route_reply(kind,data)))
    monkeypatch.setattr(calls.provider,'complete',dispatch)
    from ara.bank import load_bank
    bank=load_bank(ROOT/'bank')
    route=selectable_routes(NativeEngine(bank,calls)._engine(frozen).search(Proposition('r','R',R)).routes,frozen,meta)[0]
    calls.log.record('route',graph=route.to_dict())
    evidence=source_context(calls,route)
    body=[];labels=[]
    for i,node in enumerate(route.nodes,1):
        hypothesis=node.t_id=='hypothesis:h'
        text='This paper proposes (P and Q) implies R' if hypothesis else node.proposition.text+' P'
        citation=' [cite:'+node.t_id+']' if node.t_id in ('p','q') else ''
        body.append(f'[[node:{node.id}]] {text}.{citation}')
        labels.append(dict(sentence=i,node_ids=[node.id],role='proposed_principle' if hypothesis else 'argument_step',citation_supported=True))
    body.append("\nThis paper's conclusion is conditional on H (hypothesis:h).");labels.append(dict(sentence=len(body),node_ids=[],role='framing',citation_supported=True))
    draft=dict(title='P',body='\n'.join(body),bibliography=evidence['allowed_bibliography'])
    seen=[]
    def complete(kind,prompt,*_):
        seen.append(kind)
        if kind=='write_essay':value=draft
        elif kind=='audit_essay':value=dict(labels=labels)
        elif kind=='search_evidence':value='P'
        else:
            assert kind=='verify_originality_citations'
            value=dict(items=[],originality=dict(assessment='unverified',detail='P',evidence_urls=[]))
        return Response(raw(value))
    monkeypatch.setattr(calls.provider,'complete',complete)
    assert compose(calls,route)==draft
    assert 'write_essay' in seen and seen.count('audit_essay')>=3
    essay=(tmp_path/'export/essay.txt').read_text()
    assert 'conditional on H (hypothesis:h)' in essay and 'This paper proposes' in essay
    assert 'Proposed hypothesis:' not in '\n'.join(b['text'] for b in draft['bibliography'])
    from ara.runtime.publication_figures import generate_figures
    manifest=generate_figures(calls,route,tmp_path/'figures')
    assert all('Proposed hypothesis' in (tmp_path/'figures'/e['file']).read_text() for e in manifest)
    # A later malformed final draft must not inherit the earlier clean export.
    from ara.runtime.export import export_run
    undisclosed={**draft,'body':draft['body'].replace('This paper proposes ','').replace("This paper's conclusion is conditional on H (hypothesis:h).",'')}
    calls.log.record('final_draft',route_id=route.id,draft=undisclosed)
    with pytest.raises(ValueError,match='hypothesis disclosure'):
        export_run(calls.log.path,tmp_path/'export')
    assert not (tmp_path/'export/essay.txt').exists()


def test_hypothesis_fork_preserves_exact_frozen_authority(tmp_path,monkeypatch):
    from ara.runtime.freeze_fork import fork_from_freeze
    from ara.runtime.search_alignment import catalogue_inputs
    src=tmp_path/'source';src.mkdir()
    calls,bank,t,meta,_=freeze_h(src,monkeypatch,route_reply)
    # A native run configuration is required for prefix verification.
    # Event ordering is irrelevant to this fixture's zero-provider freeze, but
    # the run event must be inside the copied prefix.
    from ara.runtime.logging import EventLog
    events=calls.log.read()
    log=EventLog(tmp_path/'native/events.jsonl')
    log.record('run_started',config=calls.config,topic='P',audience='P',literature='P',bank_version=bank.bank_version)
    from ara.types import RunEvent
    for event in events:log.emit(RunEvent.from_dict(event))
    for name in ('commitments.json','frozen-t.json','commitment-provenance.json'):
        (log.path.parent/name).write_bytes((src/name).read_bytes())
    before={p.name:p.read_bytes() for p in log.path.parent.iterdir() if p.is_file()}
    _,_,forked=fork_from_freeze(log.path.parent,tmp_path/'fork',bank)
    assert forked==t
    assert catalogue_inputs(tmp_path/'fork',t)['commitment_provenance']==meta
    assert {p.name:p.read_bytes() for p in log.path.parent.iterdir() if p.is_file()}==before


def test_hypothesis_publication_refuses_qualifier_loss(tmp_path,monkeypatch):
    from ara.runtime.orchestration import NativeEngine
    from ara.runtime.route_policy import selectable_routes
    from ara.runtime.publication import publish
    from ara.types import Proposition
    calls,bank,t,meta,_=freeze_h(tmp_path,monkeypatch,route_reply)
    route=selectable_routes(NativeEngine(bank,calls)._engine(t).search(Proposition('r','R',R)).routes,t,meta)[0]
    calls.log.record('route',graph=route.to_dict())
    with pytest.raises(ValueError,match='hypothesis disclosure'):
        publish(calls.log,dict(route_id=route.id,markdown='# P\n\nP Q.',draft=dict(bibliography=[]),
            polished=True,audit={},local_citations=[],native_citations=[],words=3,bibliographic_records={},
            repair_rounds=0,accepted_repair_rounds=0,word_limits={},repair_validation_attempts=0))
    assert not (tmp_path/'publication/latest.json').exists()


def test_hypothesis_extension_keeps_legacy_alignment_validation():
    from ara.runtime.commitment_provenance import validate_commitment_provenance
    from ara.runtime.cache import canonical, digest
    t, catalogue, provenance = sources()
    provenance.update(schema_version='commitment-provenance-v2', alignment=None)
    provenance['sha256'] = digest(canonical({k:v for k,v in provenance.items() if k!='sha256'}))
    with pytest.raises(ValueError):
        validate_commitment_provenance(provenance, t, catalogue)
