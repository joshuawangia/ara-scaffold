import copy
import json

import pytest

from ara.runtime.calls import Rejected
from test_calls import rig, response
from test_sectioned_writer import seed_sources
from ara.runtime.providers import Response


def paper():
    body = '\n\n'.join(f'## {i}. {h}\n\n[[node:n{(i-1)%2}]] ' + 'P ' * 900 + ' [cite:p] [cite:q]'
                         for i, h in enumerate(['Introduction', 'Argument', 'Objections and replies', 'Limits', 'Conclusion'], 1))
    return dict(title='P', body=body, bibliography=[dict(id=t, text='p:pdf:1#'+t, url=None) for t in ['p', 'q']])


def polished(draft):
    from ara.runtime.publication import paragraphs
    md = '# P\n\n## Abstract\n\n' + 'P ' * 175 + '\n\n' + draft['body']
    md += '\n\n{{fig:argument-map}}\n\n{{fig:source-support}}'
    return dict(markdown=md, figure_placements=[dict(id=x, after_paragraph=5) for x in ['argument-map','source-support']],
                change_log=[dict(paragraph=i, improvement='P') for i in range(len(paragraphs(md)))])


def test_publication_constraints():
    from ara.runtime.publication import validate_polish
    draft = paper()
    value = polished(draft)
    assert validate_polish(value, draft['body'], {'argument-map','source-support'}, whole=True) == value
    for change, match in [('citation','citation'), ('length','word'), ('log','paragraph'), ('figure','figure'), ('missing_figure','figure'), ('abstract','abstract')]:
        bad = copy.deepcopy(value)
        if change == 'citation': bad['markdown'] = bad['markdown'].replace('[cite:p]', '[cite:z]', 1)
        if change == 'length': bad['markdown'] = bad['markdown'].replace('P '*900, 'P '*2900, 1)
        if change == 'log': bad['change_log'] = []
        if change == 'figure': bad['figure_placements'][0]['id'] = '../P'
        if change == 'missing_figure':
            bad['markdown'] = bad['markdown'].replace('{{fig:argument-map}}', '')
            bad['figure_placements'] = bad['figure_placements'][1:]
        if change == 'abstract': bad['markdown'] = bad['markdown'].replace('P '*175, 'P ', 1)
        with pytest.raises(Rejected, match=match):
            validate_polish(bad, draft['body'], {'argument-map','source-support'}, whole=True)


def test_figures_are_deterministic_source_linked(rig, tmp_path):
    from ara.runtime.publication_figures import generate_figures
    calls, _, log = rig
    route = seed_sources(calls, log)
    first = generate_figures(calls, route, tmp_path/'a')
    second = generate_figures(calls, route, tmp_path/'b')
    assert [x['id'] for x in first] == ['argument-map','source-support']
    for a,b in zip(first,second):
        assert (tmp_path/'a'/a['file']).read_bytes() == (tmp_path/'b'/b['file']).read_bytes()
    support = (tmp_path/'a'/'source-support.svg').read_text()
    assert 'p:pdf:1#p' in support and 'endorsed' in support and 'n0' in support
    assert '<svg' in support and '<script' not in support


def test_html_embeds_only_declared_figures_and_escapes(tmp_path):
    from ara.runtime.publication_pdf import paper_html
    (tmp_path/'argument-map.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>P</text></svg>')
    manifest=[dict(id='argument-map',file='argument-map.svg',caption='P < Q')]
    html = paper_html('# P\n\n<script>P</script>\n\n{{fig:argument-map}}',manifest,tmp_path)
    assert '<figcaption>Figure 1.' in html and '<svg ' in html
    assert '<script>P</script>' not in html and 'P &lt; Q' in html
    with pytest.raises(ValueError,match='figure'):
        paper_html('# P\n\n{{fig:missing}}',manifest,tmp_path)


def install_publication(rig, monkeypatch, adverse=0, repair_bad=False):
    from ara.runtime.publication import paragraphs
    from ara.runtime.claude_code import ClaudeCodeError
    calls,provider,log = rig
    route=seed_sources(calls,log)
    calls.config.update(essay_min_words=4500,token_cap=20_000_000)
    seen=[]
    audit_count=0
    def complete(kind,prompt,schema,maximum):
        nonlocal audit_count
        data=json.loads(prompt.split('\nINPUT_JSON\n')[1]);seen.append((kind,data))
        if kind=='polish_essay':
            if data['mode']=='section':
                md=data['markdown']
                out=dict(markdown=md,figure_placements=[],change_log=[dict(paragraph=i,improvement='P') for i in range(len(paragraphs(md)))])
            elif data['mode']=='whole':
                out=polished(paper())
            else:
                md=data['markdown']
                if repair_bad: md=md.replace('P '*175,'Q '*175,1)
                out=dict(markdown=md,figure_placements=[dict(id=x,after_paragraph=5) for x in ['argument-map','source-support']],
                         change_log=[dict(paragraph=i,improvement='P') for i in range(len(paragraphs(md)))])
        elif kind=='audit_essay':
            audit_count+=1
            out={'labels':[dict(sentence=s['sentence'],node_ids=['n0','n1'],
                asserts_premise_or_inference_not_in_outline=audit_count<=adverse and '[cite:p]' in s['text']) for s in data['sentences']]}
        elif kind=='search_evidence':
            raise ClaudeCodeError('stage_requires_api_provider')
        else: raise AssertionError(kind)
        return Response(response(out))
    monkeypatch.setattr(provider,'complete',complete)
    estimate = provider.estimate
    def subscription_estimate(kind, prompt, schema, maximum):
        if kind == 'search_evidence':
            raise ClaudeCodeError('stage_requires_api_provider')
        return estimate(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'estimate', subscription_estimate)
    return calls,route,seen


def test_native_polish_logs_sections_and_blocks_unavailable_verification(rig,monkeypatch):
    from ara.runtime.publication import polish,load_publication
    calls,route,seen=install_publication(rig,monkeypatch)
    result,directory=polish(calls,route,paper())
    assert result['polished'] and result['audit']['faithful']
    assert result['native_citations']['status']=='blocked'
    assert [d['mode'] for k,d in seen if k=='polish_essay']==['section']*5+['whole']
    assert (directory/'paper.md').read_text().endswith('p:pdf:1#q\n')
    assert '[[node:' not in (directory/'paper.md').read_text()
    assert '[[node:' in result['draft']['body']
    assert load_publication(calls.log.path.parent)[0]==result
    assert not any(e['stage']=='final_draft' for e in calls.log.read())
    events=[e for e in calls.log.read() if e['label']=='MODEL']
    assert len([e for e in events if e['stage']=='polish_essay'])==6
    assert all(e['prompt'] and e['response'] for e in events if e['stage']=='polish_essay')
    assert any(e['stage']=='search_evidence' and json.loads(e['payload_json'])['status']=='rejected' for e in events)


@pytest.mark.parametrize('adverse,expected',[(1,True),(2,False)])
def test_one_targeted_repair_then_audit_or_exact_fallback(rig,monkeypatch,adverse,expected):
    from ara.runtime.publication import polish
    calls,route,seen=install_publication(rig,monkeypatch,adverse)
    result,_=polish(calls,route,paper())
    assert result['polished'] is expected
    assert sum(k=='audit_essay' for k,_ in seen)==2
    assert sum(k=='polish_essay' and d['mode']=='repair' for k,d in seen)==1
    if not expected:
        assert result['draft']==paper() and result['native_citations']['status']=='not_run'


def test_repair_cannot_change_unflagged_abstract(rig,monkeypatch):
    from ara.runtime.publication import polish
    calls,route,_=install_publication(rig,monkeypatch,1,True)
    result,_=polish(calls,route,paper())
    assert not result['polished'] and 'unflagged' in result['polish_failure']


def test_pdf_native_browser_offline(tmp_path):
    from ara.runtime.publication_figures import _svg
    from ara.runtime.publication_pdf import render_pdf
    from pathlib import Path
    chromium=Path.home()/'.cache/ms-playwright/chromium_headless_shell-1200/chrome-headless-shell-linux64/chrome-headless-shell'
    if not chromium.exists(): pytest.skip('local Chromium unavailable')
    (tmp_path/'argument-map.svg').write_text(_svg('P',[('p','P')]))
    manifest=[dict(id='argument-map',file='argument-map.svg',caption='P')]
    result=render_pdf('# P\n\n## 1. P\n\nP '*1+'\n\n{{fig:argument-map}}',manifest,tmp_path,tmp_path/'paper.pdf')
    assert result['pages']>=1 and result['figures']==1 and all(result['embedded_fonts'].values())
    assert result['horizontal_overflow']==[]


def test_publication_cli_pins_provider_and_runs_offline_followups(rig,monkeypatch):
    from ara.runtime.cli import main
    from ara.runtime.publication import MODEL
    calls,route,seen=install_publication(rig,monkeypatch)
    log=calls.log
    # Seed the ordinary run metadata through its existing event format.
    original_read=log.read
    def metadata():
        events=original_read()
        for e in events:
            if e['stage']=='run_started':
                d=json.loads(e['payload_json']);d.update(config=calls.config,topic='P')
                e['payload_json']=json.dumps(d)
        return events
    # CLI constructs a fresh EventLog; use a real log with complete native metadata.
    from ara.runtime.logging import EventLog
    replacement=EventLog(log.path.parent/'complete'/'events.jsonl')
    from ara.types import RunEvent
    replacement.emit_many(RunEvent.from_dict(e) for e in metadata())
    import shutil
    for name in ('frozen-t.json','commitment-provenance.json'):
        shutil.copyfile(log.path.parent/name,replacement.path.parent/name)
    calls.log=replacement
    replacement.record('route',graph=route.to_dict())
    (replacement.path.parent/'draft.unverified.json').write_text(json.dumps(paper()))
    settings=[]
    def factory(config,newlog,topic):
        settings.append(config)
        calls.log=newlog
        return calls
    args=['--run-dir',str(replacement.path.parent)]
    assert main(['polish',*args,'--route',route.id],calls_factory=factory)==2
    assert settings[0]['provider']=='claude_code' and settings[0]['model']==MODEL and settings[0]['stages']=={}
    assert main(['figures',*args],calls_factory=lambda *a: pytest.fail('offline command opened provider'))==0
    assert main(['render-pdf',*args],calls_factory=lambda *a: pytest.fail('offline command opened provider'))==0
    completed=[json.loads(e['payload_json']) for e in replacement.read() if e['stage']=='publication_pdf']
    assert completed[-1]['figures']==2 and completed[-1]['native_citations']=='blocked'
    assert 'polish_essay' in (replacement.path.parent/'export/methodology.md').read_text()


def test_gap_figure_uses_route_frontier_not_source_extraction_gaps(rig, tmp_path):
    from dataclasses import replace
    from ara.runtime.publication_figures import generate_figures
    calls, _, log = rig
    route = seed_sources(calls,log)
    opened = replace(route,status='OPEN',frontier=('n0',))
    manifest = generate_figures(calls,opened,tmp_path)
    assert [f['id'] for f in manifest] == ['argument-map','source-support','gap']
    svg = (tmp_path/'gap.svg').read_text()
    assert 'n0' in svg and 'Open commitment' in svg
    assert 'source extraction' not in svg.lower()


def test_new_failed_attempt_cannot_render_previous_publication(rig,monkeypatch):
    from ara.runtime.publication import polish,load_publication
    calls,route,_=install_publication(rig,monkeypatch)
    polish(calls,route,paper())
    calls.log.record('publication_configuration',draft_sha256='P')
    with pytest.raises(Rejected,match='incomplete'):
        load_publication(calls.log.path.parent)


def test_references_use_logged_metadata_bound_to_source_pdf(rig):
    from ara.runtime.publication_references import bibliography_records, render_references
    from ara.runtime.extraction import HEADER
    from ara.runtime.cache import canonical
    calls,_,log=rig
    record=dict(id='p',authors='a; b',year=2000,title='P',venue='Q',pages='1-2')
    evidence=dict(supporting_commitments=[dict(commitment=dict(id='t',citation='p:pdf:1#t'),provenance=dict(source_id='p'))])
    log.record('run_started',literature=HEADER+canonical(dict(papers=[dict(source_id='p',pdf_sha256='abc')])))
    log.record('extract_paper', status='P')
    from ara.types import RunEvent
    from ara.runtime.logging import now
    prompt='P\nINPUT_JSON\n'+canonical(dict(source_id='p',pdf_sha256='abc',record=record))
    log.emit(RunEvent(now(),'extract_paper','MODEL',prompt=prompt))
    records=bibliography_records(log,evidence)
    text=render_references(dict(bibliography=[dict(id='t',text='p:pdf:1#t',url=None)]),evidence,records)
    assert 'a; b (2000). P. Q. pp. 1-2.' in text and '[t] p:pdf:1#t' in text
    assert records['p']['record']==record and records['p']['pdf_sha256']=='abc'
    assert records['p']['verification']=='not_independently_verified'
    # A later record for a different PDF cannot replace this source's identity.
    other='P\nINPUT_JSON\n'+canonical(dict(source_id='p',pdf_sha256='other',record={**record,'title':'R'}))
    log.emit(RunEvent(now(),'extract_paper','MODEL',prompt=other))
    assert bibliography_records(log,evidence)==records
    # Conflicting metadata for the identical source refuses, rather than guessing.
    conflict='P\nINPUT_JSON\n'+canonical(dict(source_id='p',pdf_sha256='abc',record={**record,'title':'R'}))
    log.emit(RunEvent(now(),'extract_paper','MODEL',prompt=conflict))
    with pytest.raises(Rejected,match='conflicting bibliography'):
        bibliography_records(log,evidence)
