"""Publication review regressions; only placeholders and disposable sentinels."""
import json
import re
import shutil

import pytest

from ara.runtime.claude_code import ClaudeCodeError
from ara.runtime.cli import main
from ara.runtime.logging import EventLog
from ara.runtime.providers import Response
from ara.types import RunEvent
from test_calls import rig, response
from test_claude_code import cli
from test_publication import install_publication, paper, polished
from test_sectioned_writer import seed_sources


@pytest.mark.parametrize('field', ['body', 'title', 'bibliography', 'unexpected'])
@pytest.mark.parametrize('sensitive', ['sentinel@example.invalid', 'offline-token'])
def test_publication_import_screen_before_effects(cli, field, sensitive, capsys):
    make, set_mode, config, binary = cli
    calls, log = make()
    config.update(token_cap=20_000_000, cache_dir=str(log.path.parent/'cache'))
    route = seed_sources(calls, log)
    target = EventLog(log.path.parent/'publication-run/events.jsonl')
    for e in log.read():
        if e['stage'] == 'run_started':
            payload=json.loads(e['payload_json']); payload.update(config=config, topic='P')
            e={**e, 'payload_json':json.dumps(payload)}
        target.emit(RunEvent.from_dict(e))
    for name in ('frozen-t.json', 'commitment-provenance.json'):
        shutil.copyfile(log.path.parent/name, target.path.parent/name)
    target.record('route', graph=route.to_dict())
    draft=paper()
    if field=='body': draft['body']=sensitive+' '+draft['body']
    elif field=='bibliography': draft['bibliography'][0]['text']=sensitive
    else: draft[field]=sensitive
    with pytest.raises(ClaudeCodeError): calls.provider.scan_output(draft)
    source=log.path.parent/'import.json';source.write_text(json.dumps(draft))
    trace=binary.with_suffix('.trace'); before=trace.read_bytes()
    set_mode('exit')
    assert main(['polish','--run-dir',str(target.path.parent),'--draft',str(source),'--route',route.id])==2
    output=capsys.readouterr()
    assert sensitive not in output.out+output.err
    assert ('operator_identity_in_output' if '@' in sensitive else 'credential_in_cli_output') in output.err
    assert trace.read_bytes()==before, 'import screening must precede even the provider canary'
    for path in target.path.parent.rglob('*'):
        if path.is_file(): assert sensitive.encode() not in path.read_bytes(),path
    assert not (target.path.parent/'publication/latest.json').exists()


def boundary_provider(rig, monkeypatch, mode):
    from ara.runtime.publication import paragraphs
    calls,route,_=install_publication(rig,monkeypatch)
    calls.config['validation_attempts']=1
    original=calls.provider.complete;requests=[]
    def complete(kind,prompt,schema,maximum):
        data=json.loads(prompt.split('\nINPUT_JSON\n')[1]);requests.append((kind,data))
        if kind=='polish_essay' and data['mode']=='whole':
            value=polished(paper())
            if mode in ('duplicate','duplicate_allowed'):
                value['markdown']=value['markdown'].replace('[[node:n0]] ', '[[node:n0]] P. ',1).replace('[[node:n1]] ', '[[node:n1]] P. ',1)
            elif mode in ('flagged_title','title_stays_bad'):
                value['markdown']=value['markdown'].replace('# P\n','# R\n',1)
            elif mode=='flagged_heading':
                value['markdown']=value['markdown'].replace('## 2. Argument','## 2. Argument R',1)
            else:
                value['markdown']=value['markdown'].replace('[[node:n0]] ','[[node:n0]] R. ',1)
            return Response(response(value))
        if kind=='polish_essay' and data['mode']=='repair':
            md=data['markdown']
            if mode=='move_title':md=md.replace('R.','P.').replace('# P\n','# R\n',1)
            elif mode=='move_heading':md=md.replace('R.','P.').replace('## 2. Argument','## 2. Argument R',1)
            elif mode in ('duplicate','duplicate_allowed'):
                md=md.replace('[[node:n0]] P.','[[node:n0]] P. [cite:p]',1)
                if mode=='duplicate':md=md.replace('[[node:n1]] P.','[[node:n1]] Q.',1)
            elif mode=='flagged_title':md=md.replace('# R\n','# P\n',1)
            elif mode=='flagged_heading':md=md.replace('## 2. Argument R','## 2. Argument',1)
            value=dict(markdown=md,figure_placements=[dict(id=x,after_paragraph=5) for x in ['argument-map','source-support']],change_log=[dict(paragraph=i,improvement='P') for i in range(len(paragraphs(md)))])
            return Response(response(value))
        if kind=='audit_publication':
            labels=[]
            for s in data['sentences']:
                unsupported=bool(re.search(r'\bR\b',s['text']))
                source=mode in ('duplicate','duplicate_allowed') and s['section']=='Introduction' and s['text']=='P.'
                labels.append(dict(sentence=s['sentence'],role='unsupported_claim' if unsupported else 'source_claim' if source else 'argument_step',node_ids=['n0','n1'],citation_supported=not source,publication_issue='unsupported_elaboration' if unsupported else 'none'))
            return Response(response(dict(labels=labels)))
        return original(kind,prompt,schema,maximum)
    monkeypatch.setattr(calls.provider,'complete',complete)
    return calls,route,requests


@pytest.mark.parametrize('mode', ['move_title','move_heading'])
def test_repair_cannot_edit_unflagged_title_or_heading(rig,monkeypatch,mode):
    from ara.runtime.publication import polish
    calls,route,requests=boundary_provider(rig,monkeypatch,mode)
    result,_=polish(calls,route,paper())
    assert not result['polished']
    assert result['accepted_repair_rounds']==0
    assert result['draft']==paper()
    assert 'unflagged' in result['polish_failure']


@pytest.mark.parametrize('mode', ['flagged_title','flagged_heading'])
def test_flagged_structure_can_be_repaired_and_reaudited(rig,monkeypatch,mode):
    from ara.runtime.publication import polish
    calls,route,requests=boundary_provider(rig,monkeypatch,mode)
    result,_=polish(calls,route,paper())
    assert result['polished'] and result['repair_rounds']==1
    audits=[v for k,v in requests if k=='audit_publication']
    assert len(audits)==6
    assert any(re.search(r'\bR\b',s['text']) for s in audits[0]['sentences'])
    assert not any(re.search(r'\bR\b',s['text']) for s in audits[-1]['sentences'])


def test_current_title_still_unsupported_after_repairs_fails(rig,monkeypatch):
    from ara.runtime.publication import polish
    calls,route,requests=boundary_provider(rig,monkeypatch,'title_stays_bad')
    result,_=polish(calls,route,paper())
    assert not result['polished'] and result['repair_rounds']==3
    assert result['draft']==paper()


@pytest.mark.parametrize('mode,accepted', [('duplicate',False),('duplicate_allowed',True)])
def test_duplicate_sentence_repair_uses_only_flagged_occurrence(rig,monkeypatch,mode,accepted):
    from ara.runtime.publication import polish
    calls,route,requests=boundary_provider(rig,monkeypatch,mode)
    result,_=polish(calls,route,paper())
    repair=next(v for k,v in requests if k=='polish_essay' and v['mode']=='repair')
    assert repair['allowed_paragraphs']==[1]
    flagged=repair['flagged_sentences']
    assert len(flagged)==1 and flagged[0]['location']['paragraph_index']==1
    assert flagged[0]['location']['start'] < flagged[0]['location']['end']
    assert result['polished'] is accepted
    if not accepted:assert result['accepted_repair_rounds']==0


def test_changed_publication_title_cannot_reuse_audit_cache(rig,monkeypatch):
    from ara.runtime.calls import EssayAuditFailed
    calls,route,requests=boundary_provider(rig,monkeypatch,'flagged_title')
    draft=paper();context=dict(original_draft=draft,literature_currency=None)
    assert calls.audit_essay(route,draft,publication_context=context)['faithful']
    with pytest.raises(EssayAuditFailed):
        calls.audit_essay(route,{**draft,'title':'R'},publication_context=context)
    assert len([1 for k,_ in requests if k=='audit_publication'])==2


def test_publication_audit_dispatch_uses_effective_provider(rig,monkeypatch):
    from ara.runtime.providers import MockProvider
    calls,route,_=install_publication(rig,monkeypatch)
    calls.config['stages']={'audit_publication':{'provider':'mock','model':'P'}}
    calls.config['pricing']['P']=calls.config['pricing'][calls.config['model']]
    audited=[]
    auditor=MockProvider({},'P')
    def complete(kind,prompt,schema,maximum):
        assert kind=='audit_publication'
        audited.append(kind)
        data=json.loads(prompt.split('\nINPUT_JSON\n')[1])
        return Response(response({'labels':[dict(sentence=s['sentence'],role='argument_step',node_ids=['n0','n1'],citation_supported=True,publication_issue='none') for s in data['sentences']]},model='P'))
    monkeypatch.setattr(auditor,'complete',complete)
    calls.provider_factory=lambda settings: auditor
    calls.audit_essay(route,paper(),publication_context=dict(original_draft=paper(),literature_currency=None))
    assert audited==['audit_publication']
    scoped=calls._for_construction_stage('audit_publication',{})
    assert scoped.budget is calls.budget and scoped.log is calls.log


def test_import_screen_includes_effective_audit_provider(rig,monkeypatch):
    from ara.runtime.publication import polish
    from ara.runtime.providers import MockProvider
    calls,route,_=install_publication(rig,monkeypatch)
    calls.config['stages']={'audit_publication':{'provider':'mock','model':'P'}}
    auditor=MockProvider({},'P')
    def scan(value):
        if value['title']=='P': raise ClaudeCodeError('operator_identity_in_output')
    monkeypatch.setattr(auditor,'scan_output',scan,raising=False)
    calls.provider_factory=lambda settings: auditor
    before=calls.log.path.read_bytes()
    with pytest.raises(ClaudeCodeError,match='operator_identity_in_output'):
        polish(calls,route,paper())
    assert calls.log.path.read_bytes()==before
    assert not (calls.log.path.parent/'publication/latest.json').exists()
