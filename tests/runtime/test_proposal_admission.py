"""Paper-owned targets use frozen evidence without invented search or inference."""
from pathlib import Path
from types import SimpleNamespace
import json

import pytest

from ara.bank import load_bank
from ara.runtime.cache import canonical, digest
from ara.runtime.logging import EventLog, read_log
from test_calls import rig, ROOT
from test_sectioned_writer import seed_sources


def prepared(rig):
    calls,_,log=rig
    seed_sources(calls,log,local_pages='P P P Q Q Q R R R')
    events=log.read()
    bank=load_bank(ROOT/'bank')
    # Build a normal, fully bound source lifecycle from the placeholder receipts.
    source=log.path.parent.parent/'source'
    target=EventLog(source/'events.jsonl')
    from ara.types import RunEvent
    for event in events:
        value=json.loads(event['payload_json'])
        if event['stage']=='run_started':
            value.update(config={**calls.config,'provider':'mock'},topic='P',bank_version=bank.bank_version)
        if event['stage']=='commitments_frozen':
            value['bank_version']=bank.bank_version
            (source/'commitments.json').write_text(canonical(value['commitments']))
        target.emit(RunEvent.from_dict({**event,'payload_json':canonical(value)}))
    for name in ('frozen-t.json','commitment-provenance.json'):
        (source/name).write_bytes((log.path.parent/name).read_bytes())
    rows=read_log(target.path)
    freeze=next(r for r in rows if r['event']['stage']=='commitments_frozen')
    request=dict(candidate_id='candidate-P', source_freeze_hash=freeze['hash'],
        proposal=dict(target_text='R',thesis_origin='eps2',dossier_mapping='P',missing_premise='Q; no formalization or search.',
                      frozen_evidence_ids=['p','q'],local_sources=[],minimum_words=3000),
        grounding_files=[])
    return source,request


def invoke(source,destination,request,monkeypatch,*,plan=False):
    from ara.runtime.cli import main
    packet=destination.parent/'packet.json';packet.write_text(canonical(request))
    monkeypatch.setattr('ara.runtime.proposal_admission.shutil.disk_usage',lambda p:SimpleNamespace(free=100_000_000_000))
    args=['admit-proposal','--source-run',str(source),'--run-dir',str(destination),'--packet',str(packet)]
    if plan:args+=['--plan-only']
    return main(args,calls_factory=lambda *a,**kw:pytest.fail('admission must not create ModelCalls'))


def test_native_admission_keeps_sources_and_adds_only_unformalized_open_target(rig,monkeypatch,tmp_path):
    from ara.runtime.proposal import from_events
    from ara.runtime.route_policy import frozen_from_events,route_classification
    from ara.types import RouteGraph
    source,request=prepared(rig);before={p.name:p.read_bytes() for p in source.iterdir() if p.is_file()}
    destination=tmp_path/'candidate'
    assert invoke(source,destination,request,monkeypatch)==0
    events=EventLog(destination/'events.jsonl').read()
    graphs=[json.loads(e['payload_json']) for e in events if e['stage']=='route']
    assert len(graphs)==1 and graphs[0]['authority']=='paper_owned_target_not_search_result'
    route=RouteGraph.from_dict(graphs[0]['graph'])
    assert route.status=='OPEN' and len(route.nodes)==1 and route.frontier==(route.root_id,)
    assert route.nodes[0].proposition.formula is None
    assert route.nodes[0].t_id=='open' and not route.nodes[0].children and route.nodes[0].proposal is None
    assert route_classification(route,frozen_from_events(events))=='OPEN'
    assert from_events(events,route.id)['packet']['target_text']=='R'
    assert from_events(events,route.id)['disclosure'].startswith('eps2-proposed')
    assert sum(e['stage']=='commitments_frozen' for e in events)==1
    assert not any(e['stage'] in ('formalise','search_started','engine_decision') for e in events)
    assert {p.name:p.read_bytes() for p in source.iterdir() if p.is_file()}==before
    # Native writer/audit gets source evidence, not route premises or H authority.
    calls=rig[0];calls.log=EventLog(destination/'events.jsonl')
    from ara.runtime.writing import source_context
    context=source_context(calls,route)
    assert context['supporting_commitments']==[]
    assert len(context['proposal_source_evidence'])==2
    assert calls.essay_outline(route)['links']==[]
    assert 'hypothesis_disclosure' not in calls.essay_outline(route)


def test_native_plan_validates_without_copy_or_model(rig,monkeypatch,tmp_path,capsys):
    source,request=prepared(rig);destination=tmp_path/'candidate'
    assert invoke(source,destination,request,monkeypatch,plan=True)==0
    assert not destination.exists()
    plan=json.loads(capsys.readouterr().out)
    assert plan['status']=='ready' and plan['inferences']==0 and plan['new_freeze'] is False


@pytest.mark.parametrize('defect',['freeze','evidence','packet_route','floor','identity'])
def test_admission_refuses_before_copy_or_model(rig,monkeypatch,tmp_path,defect):
    from ara.runtime.cli import main
    source,request=prepared(rig);destination=tmp_path/'candidate'
    if defect=='freeze':request['source_freeze_hash']='0'*64
    if defect=='evidence':request['proposal']['frozen_evidence_ids']=['missing']
    if defect=='packet_route':request['proposal']['route_id']='invented'
    from ara.runtime import proposal_admission
    monkeypatch.setattr(proposal_admission.shutil,'disk_usage',lambda p:SimpleNamespace(free=1 if defect=='floor' else 100_000_000_000))
    if defect=='identity':
        def scan(*a,**kw):raise ValueError('operator_identity_in_output')
        monkeypatch.setattr(proposal_admission,'screen_request',scan)
    packet=tmp_path/'input.json';packet.write_text(canonical(request))
    assert main(['admit-proposal','--source-run',str(source),'--run-dir',str(destination),'--packet',str(packet)],
                calls_factory=lambda *a,**kw:pytest.fail('provider dispatch'))!=0
    assert not destination.exists()


def test_selection_capacity_refusal_writes_no_log_or_export(rig,monkeypatch,tmp_path):
    from ara.runtime.cli import main
    from ara.runtime import proposal_admission
    source,request=prepared(rig);destination=tmp_path/'candidate'
    assert invoke(source,destination,request,monkeypatch)==0
    before={str(p.relative_to(destination)):p.read_bytes() for p in destination.rglob('*') if p.is_file()}
    monkeypatch.setattr(proposal_admission.shutil,'disk_usage',lambda p:SimpleNamespace(free=1))
    assert main(['select','--run-dir',str(destination)],calls_factory=lambda *a:pytest.fail('dispatch'))==2
    assert {str(p.relative_to(destination)):p.read_bytes() for p in destination.rglob('*') if p.is_file()}==before


def test_queue_promotion_requires_bound_native_admission(rig,monkeypatch,tmp_path,capsys):
    from hashlib import sha256
    from ara.runtime.proposal_admission import promote_queue_entry
    source,request=prepared(rig);destination=tmp_path/'candidate'
    grounding=tmp_path/'grounding.json';grounding.write_text('{"target":"R"}')
    request['grounding_files']=[dict(path=str(grounding),sha256=sha256(grounding.read_bytes()).hexdigest())]
    entry=dict(id='candidate-P',status='OPEN-proposal-pending',route_id=None,run_dir=str(source),
               grounding_packet=str(grounding),dispatch_hold='awaiting_native_grounding_admission')
    assert invoke(source,destination,request,monkeypatch)==0
    from ara.runtime.cli import main
    queued=tmp_path/'entry.json';queued.write_text(canonical(entry))
    capsys.readouterr()
    assert main(['promote-proposal','--entry',str(queued),'--run-dir',str(destination)],
                calls_factory=lambda *a:pytest.fail('promotion must not dispatch'))==0
    admitted=json.loads(capsys.readouterr().out)
    assert admitted['status']=='OPEN-proposal' and admitted['reuse_admitted_run'] is True
    assert admitted['run_dir']==str(destination) and admitted['source_run']==str(source)
    assert admitted['dispatch_hold'] is None
    with pytest.raises(ValueError):promote_queue_entry({**entry,'id':'candidate-Q'},destination)
    grounding.write_text('{"target":"S"}')
    with pytest.raises(ValueError,match='grounding binding'):promote_queue_entry(entry,destination)


def test_grounding_file_change_refuses_before_copy(rig,monkeypatch,tmp_path):
    source,request=prepared(rig)
    grounding=tmp_path/'grounding';grounding.write_text('P')
    request['grounding_files']=[dict(path=str(grounding),sha256='0'*64)]
    assert invoke(source,tmp_path/'candidate',request,monkeypatch)==2
    assert not (tmp_path/'candidate').exists()


def test_native_output_screen_runs_before_admission_records(rig,monkeypatch,tmp_path):
    from ara.runtime import proposal_admission
    source,request=prepared(rig)
    class Provider:
        def scan_output(self,value):
            assert value['request']['proposal']['target_text']=='R'
            raise ValueError('operator_identity_in_output')
    monkeypatch.setattr('ara.runtime.cli.make_provider',lambda *a:Provider())
    assert invoke(source,tmp_path/'candidate',request,monkeypatch)==2
    assert not (tmp_path/'candidate').exists()


@pytest.mark.parametrize('adverse',[False,True])
def test_admitted_target_reaches_native_k3_with_source_citations(rig,monkeypatch,tmp_path,adverse):
    from ara.runtime.essay_audit import audit_consensus
    from ara.runtime.calls import EssayAuditFailed
    from ara.runtime.providers import Response
    from ara.runtime.proposal import from_events,insert_disclosure
    from ara.runtime.citations import check_coverage
    from ara.types import RouteGraph
    from test_calls import response
    source,request=prepared(rig);destination=tmp_path/'candidate'
    assert invoke(source,destination,request,monkeypatch)==0
    calls,provider,_=rig;calls.log=EventLog(destination/'events.jsonl')
    events=calls.log.read()
    route=RouteGraph.from_dict(next(json.loads(e['payload_json'])['graph'] for e in events if e['stage']=='route'))
    from ara.runtime.writing import source_context
    draft=insert_disclosure(from_events(events,route.id),dict(title='P',body='Abstract\nP.\nProposal\n[[node:proposal-root]] R.\nP P P. [cite:p]\nQ Q Q. [cite:q]',bibliography=source_context(calls,route)['allowed_bibliography']))
    count=0
    def complete(kind,prompt,schema,maximum):
        nonlocal count
        assert kind=='audit_essay';count+=1
        inputs=json.loads(prompt.split('\nINPUT_JSON\n')[1])
        rows=[]
        for s in inputs['sentences']:
            root=s['text']=='R.'
            rows.append(dict(sentence=s['sentence'],node_ids=['proposal-root'] if root else [],
                role=('unsupported_claim' if adverse and count==2 else 'proposed_principle') if root else
                     ('source_claim' if '[cite:' in s['text'] else 'framing'),citation_supported=True))
        return Response(response(dict(labels=rows)))
    monkeypatch.setattr(provider,'complete',complete)
    if adverse:
        with pytest.raises(EssayAuditFailed):audit_consensus(calls,route,draft)
    else:
        assert audit_consensus(calls,route,draft)['faithful']
        check_coverage(calls.log.read(),route,draft)
    assert count==3


def test_root_reserve_is_checked_even_when_code_and_run_are_in_shm(monkeypatch):
    from ara.runtime.proposal_admission import capacity
    monkeypatch.setattr('ara.runtime.proposal_admission.shutil.disk_usage',
        lambda path:SimpleNamespace(free=5_999_999_999 if str(path)=='/' else 100_000_000_000))
    assert not capacity('/dev/shm/target','/dev/shm/code',100)['fits']


def test_admission_exports_methodology_but_no_essay(rig,monkeypatch,tmp_path):
    from ara.runtime.export import export_run
    source,request=prepared(rig);destination=tmp_path/'candidate'
    assert invoke(source,destination,request,monkeypatch)==0
    report,essay=export_run(destination/'events.jsonl',destination/'export')
    assert report.exists() and essay is None
    assert not (destination/'export/essay.txt').exists()
    assert 'paper_owned_proposal_not_frozen_T_or_engine_license' in report.read_text()
