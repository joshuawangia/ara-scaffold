import copy
import json
import re

import pytest

from ara.runtime.calls import Rejected
from test_calls import rig, response
from test_sectioned_writer import seed_sources
from ara.runtime.providers import Response


def paper():
    body = '\n\n'.join(f'## {i}. {h}\n\n[[node:n{(i-1)%2}]] ' + 'P ' * 900 + ' [cite:p] [cite:q]'
                         for i, h in enumerate(['Introduction', 'Argument', 'Objections and replies', 'Limits', 'Conclusion'], 1))
    return dict(title='P', body=body, bibliography=[dict(id=t, text='a (2000). P. Q. PDF p. 1.', url=None) for t in ['p', 'q']])


def publication_nodes(text):
    return [node for tid,node in [('p','n0'),('q','n1')] if '[cite:'+tid+']' in text]


def publication_role(text):
    return 'argument_step' if publication_nodes(text) else 'framing'


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


def install_publication(rig, monkeypatch, adverse=0, repair_bad=False, *, web_absent=False):
    from ara.runtime.publication import paragraphs
    from ara.runtime.claude_code import ClaudeCodeError
    calls,provider,log = rig
    route=seed_sources(calls,log,local_pages='P P P Q Q Q R R R')
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
                from ara.runtime.publication_audit import document_blocks
                blocks=document_blocks(md)
                spans=[(blocks[s['location']['block_index']]['start']+s['location']['start'],
                        blocks[s['location']['block_index']]['start']+s['location']['end'])
                       for s in data['flagged_sentences']]
                for start,end in sorted(spans,reverse=True):
                    md=md[:start]+re.sub(r'\bP\b',('Q '*data['repair_round']).strip(),md[start:end],count=1)+md[end:]
                if repair_bad: md=md.replace('P '*175,'Q '*175,1)
                out=dict(markdown=md,figure_placements=[dict(id=x,after_paragraph=5) for x in ['argument-map','source-support']],
                         change_log=[dict(paragraph=i,improvement='P') for i in range(len(paragraphs(md)))])
        elif kind in ('audit_essay', 'audit_publication'):
            audit_count+=1
            out={'labels':[dict(sentence=s['sentence'],node_ids=publication_nodes(s['text']),
                role='unsupported_claim' if audit_count<=adverse*3 and '[cite:p]' in s['text'] else publication_role(s['text']),
                citation_supported=True,publication_issue='none') for s in data['sentences']]}
        elif kind=='search_evidence':
            if not web_absent:
                raise ClaudeCodeError('stage_requires_api_provider')
            out='P'
        elif kind=='verify_originality_citations' and web_absent:
            out=dict(items=[{**item,'status':'unverified','action':'remove','detail':'P','evidence_urls':[]}
                            for item in data['items']],
                     originality=dict(assessment='unverified',detail='P',evidence_urls=[]))
        else: raise AssertionError(kind)
        return Response(response(out))
    monkeypatch.setattr(provider,'complete',complete)
    estimate = provider.estimate
    def subscription_estimate(kind, prompt, schema, maximum):
        if kind == 'search_evidence' and not web_absent:
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
    assert '[cite:' not in (directory/'paper.md').read_text()
    assert result['citation_receipt']['p']['raw_citation']=='p:pdf:1#p'
    assert '[[node:' not in (directory/'paper.md').read_text()
    assert '[[node:' in result['draft']['body']
    assert load_publication(calls.log.path.parent)[0]==result
    assert not any(e['stage']=='final_draft' for e in calls.log.read())
    events=[e for e in calls.log.read() if e['label']=='MODEL']
    assert len([e for e in events if e['stage']=='polish_essay'])==6
    assert all(e['prompt'] and e['response'] for e in events if e['stage']=='polish_essay')
    assert any(e['stage']=='search_evidence' and json.loads(e['payload_json'])['status']=='rejected' for e in events)


@pytest.mark.parametrize('adverse,expected',[(1,True),(2,True),(3,True),(4,False)])
def test_three_targeted_repairs_then_audit_or_exact_fallback(rig,monkeypatch,adverse,expected):
    from ara.runtime.publication import polish
    calls,route,seen=install_publication(rig,monkeypatch,adverse)
    result,_=polish(calls,route,paper())
    assert result['polished'] is expected
    rounds=min(adverse,3)
    assert sum(k=='audit_publication' for k,_ in seen)==3*(rounds+1)
    repairs=[d for k,d in seen if k=='polish_essay' and d['mode']=='repair']
    assert len(repairs)==result['repair_rounds']==rounds
    assert [d['repair_round'] for d in repairs]==list(range(1,rounds+1))
    for repair in repairs:
        assert repair['flagged_sentences']
        assert all(s['sentence']>0 and s['reasons']==['unsupported_claim'] for s in repair['flagged_sentences'])
        assert repair['audit_failures']==repair['audit']['flags']
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


@pytest.mark.parametrize('audit_provider', ['claude_code', 'codex_cli'])
@pytest.mark.parametrize('configured,override,expected',[(None,None,3000),(3600,None,3600),(3600,3200,3200)])
def test_publication_cli_pins_provider_and_runs_offline_followups(rig,monkeypatch,configured,override,expected,audit_provider):
    from ara.runtime.cli import main
    from ara.runtime.publication import MODEL
    calls,route,seen=install_publication(rig,monkeypatch)
    log=calls.log
    if audit_provider=='codex_cli':
        calls.config['pricing']['gpt-6-luna']=calls.config['pricing'][calls.config['model']]
    if configured is not None: calls.config['publication_min_words']=configured
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
    def factory(config,newlog,topic,*,imported_draft=None):
        settings.append(config)
        calls.log=newlog
        calls.config=config
        if audit_provider=='codex_cli':
            from ara.runtime.providers import MockProvider
            def audit_factory(settings):
                backend=MockProvider({},settings['model'])
                def complete(kind,prompt,schema,maximum):
                    raw=calls.provider.complete(kind,prompt,schema,maximum).raw
                    return Response({**raw,'model':settings['model']})
                backend.complete=complete
                return backend
            calls.provider_factory=audit_factory
        calls.screen_imported_draft(imported_draft, kind='audit_publication')
        return calls
    args=['--run-dir',str(replacement.path.parent)]
    extra=[] if override is None else ['--min-words',str(override)]
    extra+=['--audit-provider',audit_provider]
    if audit_provider=='codex_cli':extra+=['--audit-model','gpt-6-luna']
    assert main(['polish',*args,'--route',route.id,*extra],calls_factory=factory)==2
    assert settings[0]['publication_min_words']==settings[0]['essay_min_words']==expected
    inputs=[d for k,d in seen if k=='polish_essay']
    assert all(d['minimum_words']==expected and d['maximum_words']==6000 for d in inputs)
    assert all(d['source_evidence']['allowed_bibliography'] for k,d in seen if k=='audit_publication')
    assert settings[0]['provider']=='claude_code' and settings[0]['model']==MODEL
    if audit_provider=='codex_cli':
        assert settings[0]['stages']['audit_publication']['provider']=='codex_cli'
        assert settings[0]['stages']['audit_publication']['model']=='gpt-6-luna'
        audits=[json.loads(e['payload_json']) for e in replacement.read() if e['stage']=='audit_publication']
        assert audits[-1]['requested_model']=='gpt-6-luna'
    else:assert settings[0]['stages']=={}
    assert main(['figures',*args],calls_factory=lambda *a: pytest.fail('offline command opened provider'))==0
    assert main(['render-pdf',*args],calls_factory=lambda *a: pytest.fail('offline command opened provider'))==0
    completed=[json.loads(e['payload_json']) for e in replacement.read() if e['stage']=='publication_pdf']
    assert completed[-1]['figures']==2 and completed[-1]['native_citations']=='blocked'
    methodology=(replacement.path.parent/'export/methodology.md').read_text()
    assert 'polish_essay' in methodology
    policy=[json.loads(e['payload_json']) for e in replacement.read() if e['stage']=='publication_length_policy'][-1]
    assert policy['minimum_words']==expected and policy['maximum_words']==6000
    assert 'not a competition minimum' in policy['minimum_basis']
    summary=json.loads(methodology.split('```json\n',1)[1].split('\n```',1)[0])
    assert summary['publication']['publication_length_policy'][-1]==policy


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
    text=render_references(dict(body='P',bibliography=[dict(id='t',text='p:pdf:1#t',url=None)]),evidence,records,receipt={'t':dict(source_id='p')})
    assert 'a; b (2000). P. Q. pp. 1-2.' in text and '[t]' not in text
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


def test_polish_can_merge_redundant_paragraphs_without_losing_support():
    from ara.runtime.publication import validate_polish, paragraphs
    original='[[node:n0]] P [cite:p]\n\n[[node:n1]] Q [cite:q]'
    value=dict(markdown='[[node:n0]] P [cite:p] [[node:n1]] Q [cite:q]',figure_placements=[],change_log=[dict(paragraph=0,improvement='P')])
    assert validate_polish(value,original,set())


def test_reading_citations_use_authors_and_provenance_pages():
    from ara.runtime.publication_references import reading_copy, render_references
    evidence=dict(supporting_commitments=[dict(commitment=dict(id='t',citation='p:pdf:2-3#t'),provenance=dict(source_id='p',page_start=2,page_end=3))])
    records={'p':dict(record=dict(id='p',authors='a, P; b, Q',year=2000,title='P',venue='Q',version_details='internal:q'),pdf_sha256='abc')}
    text,receipt=reading_copy('P [cite:t]',evidence,records,None)
    assert text=='P (a & b 2000, PDF pp. 2–3)'
    assert receipt['t']['raw_citation']=='p:pdf:2-3#t'
    assert receipt['t']['source_id']=='p' and receipt['t']['pdf_sha256']=='abc'
    assert receipt['t']['bibliography']['version_details']=='internal:q'
    assert 'internal:q' not in render_references({},evidence,records,receipt=receipt)
    with pytest.raises(Rejected,match='citation'):
        reading_copy('P [cite:q]',evidence,records,None)


def currency_record():
    return dict(task='p',created_at='2000',coverage='P',verification=dict(tracked_files_unchanged=True,existing_26_pdfs_unchanged=True),
        evidence_register=dict(e=dict(work='p',year=2000,pdf_pages=[1,2],section='1',kind='read_fulltext_passages',claim='P'),
                               m=dict(work='q',year=2000,section='P',kind='metadata_abstract_only',claim='Q')),
        records=[dict(id='p',authors=['a'],title='P',year=2000)],thesis_currency=[],linking_claims={},query_catalog=[])


def test_currency_input_is_logged_and_bound_to_exact_record(rig,tmp_path):
    from ara.runtime.publication_currency import load_currency
    from hashlib import sha256
    calls,_,log=rig; path=tmp_path/'p.json';raw=json.dumps(currency_record(),indent=2);path.write_text(raw)
    value=load_currency([path],log)
    assert value['records'][0]['sha256']==sha256(raw.encode()).hexdigest()
    assert value['evidence']['p:e']['location']=='PDF pp. 1, 2; §1'
    assert 'p:m' not in value['evidence']
    assert value['excluded_metadata'][0]['work']=='q'
    event=[e for e in log.read() if e['stage']=='publication_currency_input'][-1]
    assert event['label']=='HUMAN' and json.loads(event['payload_json'])['text']==raw
    path.write_text('{}')
    assert value['evidence']['p:e']['claim']=='P'
    with pytest.raises(Rejected,match='currency'):
        load_currency([path],log)


@pytest.mark.parametrize('adverse', [False, True])
def test_post_polish_audit_receives_currency_and_original_draft(rig,monkeypatch,tmp_path,adverse):
    from ara.runtime.publication import polish
    from ara.runtime.publication_currency import load_currency
    calls,route,seen=install_publication(rig,monkeypatch)
    path=tmp_path/'p.json';path.write_text(json.dumps(currency_record()));currency=load_currency([path],calls.log)
    provider=calls.provider;old=provider.complete
    def complete(kind,prompt,schema,maximum):
        data=json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind=='polish_essay' and data['mode']=='whole':
            out=polished(paper());out['markdown']=out['markdown'].replace('## 5. Conclusion','## 5. Related work and scope of the novelty claim\n\nP [lit:p:e] [lit:p:search]\n\n## 6. Conclusion')
            from ara.runtime.publication import paragraphs
            out['change_log']=[dict(paragraph=i,improvement='P') for i in range(len(paragraphs(out['markdown'])))]
            for f in out['figure_placements']:f['after_paragraph']=len(paragraphs(out['markdown']))-1
            return Response(response(out))
        if kind=='audit_publication':
            assert data['publication_context']['literature_currency']==currency
            assert data['publication_context']['original_draft']==paper()
            return Response(response(dict(labels=[dict(sentence=s['sentence'],node_ids=[] if '[lit:' in s['text'] else publication_nodes(s['text']),
                role=('unsupported_claim' if adverse else 'source_claim') if '[lit:' in s['text'] else publication_role(s['text']),
                citation_supported=True,publication_issue='none') for s in data['sentences']])))
        return old(kind,prompt,schema,maximum)
    monkeypatch.setattr(provider,'complete',complete)
    result,directory=polish(calls,route,paper(),currency=currency)
    assert result['polished'] is (not adverse) and result['literature_currency']==currency
    text=(directory/'paper.md').read_text();assert '[lit:' not in text
    if adverse:
        assert result['draft']==paper()
        assert 'Literature-currency record' not in text
    else:assert 'Related work and scope of the novelty claim' in text
    audits=[e for e in calls.log.read() if e['stage']=='audit_publication' and e['label']=='MODEL']
    assert audits and 'literature_currency' in audits[-1]['prompt']


def test_currency_refuses_failed_verification(rig,tmp_path):
    from ara.runtime.publication_currency import load_currency
    calls,_,log=rig;path=tmp_path/'p.json'
    path.write_text(json.dumps(dict(task='p',handoff_verification=dict(verified_at='2000',errors=['P']))))
    with pytest.raises(Rejected,match='verification'):
        load_currency([path],log)


def test_literature_claims_cannot_escape_the_related_work_section():
    from ara.runtime.publication_currency import check_currency
    currency=dict(evidence={'p:e':dict(kind='read_fulltext',work='p'),'p:search':dict(kind='bounded_search_record',work=None)})
    good='## 1. Related work and scope of the novelty claim\n\nP [lit:p:e] [lit:p:search]\n\n## 2. Conclusion\n\nQ'
    check_currency(good,currency)
    check_currency(good.replace('Related work and scope of the novelty claim','Related Work and Scope of the Novelty Claim'),currency)
    for bad in [good+' [lit:p:e]',good.replace('[lit:p:e]','[lit:q:e]'),good.replace('P [lit:p:e]','[[node:n0]] P [lit:p:e]')]:
        with pytest.raises(Rejected):check_currency(bad,currency)


def test_reading_copy_deduplicates_same_page_but_retains_both_ids():
    from ara.runtime.publication_references import reading_copy
    evidence=dict(supporting_commitments=[dict(commitment=dict(id=id,citation='p:pdf:2#'+id),provenance=dict(source_id='p',page_start=2,page_end=2)) for id in ('t','u')])
    records={'p':dict(record=dict(authors=['a'],year=2000),pdf_sha256='abc')}
    text,receipt=reading_copy('P. [[node:n0]] [cite:t] [[node:n1]] [cite:u]',evidence,records,None)
    assert text=='P (a 2000, PDF p. 2).'
    assert set(receipt)=={'t','u'}
    assert receipt['t']['raw_citation']!=receipt['u']['raw_citation']


@pytest.mark.parametrize('words,expected', [(2990,True),(2900,False),(5990,False)])
def test_publication_word_bounds_use_rendered_citations(rig,monkeypatch,words,expected):
    from ara.runtime.publication import polish, NODE, FIGURE
    calls,route,_=install_publication(rig,monkeypatch)
    provider=calls.provider; old=provider.complete
    def complete(kind,prompt,schema,maximum):
        data=json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind=='polish_essay' and data['mode']=='whole':
            out=polished(paper())
            out['markdown']=out['markdown'].replace('P '*900,'P '*570)
            count=len(NODE.sub('',FIGURE.sub('',out['markdown'])).split())
            out['markdown']=out['markdown'].replace('P '*570,'P '*(570+words-count),1)
            return Response(response(out))
        return old(kind,prompt,schema,maximum)
    monkeypatch.setattr(provider,'complete',complete)
    result,_=polish(calls,route,paper())
    assert result['polished'] is expected
    if expected:
        assert result['audit_words']==words < 3000 <= result['words'] <= 6000
    else:
        assert 'word count' in result['polish_failure']


@pytest.mark.parametrize('role',['framing','exposition','signpost','objection','reply'])
def test_publication_typed_framing_is_not_a_false_positive(rig,monkeypatch,role):
    from ara.runtime.publication import polish
    calls,route,_=install_publication(rig,monkeypatch)
    complete=calls.provider.complete
    def classify(kind,prompt,schema,maximum):
        raw=complete(kind,prompt,schema,maximum)
        if kind=='audit_publication':
            value=json.loads(raw.text()); value['labels'][0].update(role=role,node_ids=[])
            return Response(response(value))
        return raw
    monkeypatch.setattr(calls.provider,'complete',classify)
    result,_=polish(calls,route,paper())
    assert result['polished'] and result['repair_rounds']==0
    assert all(sample['role_counts'][role]>=1 for sample in result['audit']['samples'])


def test_publication_issue_reaches_targeted_repair(rig,monkeypatch):
    from ara.runtime.publication import polish
    calls,route,seen=install_publication(rig,monkeypatch)
    complete=calls.provider.complete; audits=0
    def classify(kind,prompt,schema,maximum):
        nonlocal audits
        raw=complete(kind,prompt,schema,maximum)
        if kind=='audit_publication':
            audits+=1;value=json.loads(raw.text())
            if audits==1:
                data=json.loads(prompt.split('\nINPUT_JSON\n')[1])
                n=next(s['sentence'] for s in data['sentences'] if not s['text'].startswith('#'))
                next(l for l in value['labels'] if l['sentence']==n)['publication_issue']='thesis_placement'
            return Response(response(value))
        return raw
    monkeypatch.setattr(calls.provider,'complete',classify)
    result,_=polish(calls,route,paper())
    assert result['polished'] and result['repair_rounds']==1
    repair=next(d for k,d in seen if k=='polish_essay' and d['mode']=='repair')
    assert repair['flagged_sentences'][0]['reasons']==['thesis_placement']


def test_publication_literature_sentence_scope_and_typed_support(rig,monkeypatch):
    from ara.runtime.calls import EssayAuditFailed
    calls,route,_=install_publication(rig,monkeypatch)
    currency={'evidence':{'p:e':{'kind':'read_fulltext','work':'p'}}}
    calls.config['essay_min_words']=3000
    context=dict(original_draft=paper(),literature_currency=currency)
    draft=dict(title='P',body='## 1. Related work and scope of the novelty claim\n\nP. [lit:p:e]\n\n## 2. Argument\n\n[[node:n0]] [[node:n1]] Q. [cite:p] [cite:q]',bibliography=paper()['bibliography'])
    def complete(kind,prompt,schema,maximum):
        data=json.loads(prompt.split('\nINPUT_JSON\n')[1])
        return Response(response(dict(labels=[dict(sentence=s['sentence'],role='source_claim' if '[lit:' in s['text'] else publication_role(s['text']),
            node_ids=[] if '[lit:' in s['text'] else publication_nodes(s['text']),citation_supported=True,publication_issue='none') for s in data['sentences']])))
    monkeypatch.setattr(calls.provider,'complete',complete)
    inputs=calls.audit_inputs(route,draft,publication_context=context)
    assert inputs['source_evidence']['allowed_bibliography']
    sentence=next(s for s in inputs['sentences'] if '[lit:' in s['text'])
    assert sentence['text']=='P. [lit:p:e]'
    assert sentence['section']=='Related work and scope of the novelty claim'
    assert calls.audit_essay(route,draft,publication_context=context)['faithful']
    titled={**draft,'body':draft['body'].replace('Related work and scope of the novelty claim','Related Work and Scope of the Novelty Claim')}
    assert calls.audit_essay(route,titled,publication_context=context)['faithful']
    for changed,reason in [(draft['body'].replace('Related work and scope of the novelty claim','Introduction'),'literature_scope'),(draft['body'].replace('[lit:p:e]','[lit:p:z]'),'miscited_literature_claim')]:
        with pytest.raises(EssayAuditFailed) as exc:calls.audit_essay(route,{**draft,'body':changed},publication_context=context)
        assert reason in [f['reason'] for f in exc.value.result['flags']]


@pytest.mark.parametrize('minimum,words,passed',[(3000,3000,True),(3000,2999,False),(3500,3200,False),(3200,3200,True),(3000,6000,True),(3000,6001,False)])
def test_configurable_publication_minimum_and_fixed_maximum(minimum,words,passed):
    from ara.runtime.publication import validate_polish,NODE,FIGURE
    draft=paper();value=polished(draft)
    value['markdown']=value['markdown'].replace('P '*900,'P '*570)
    current=len(NODE.sub('',FIGURE.sub('',value['markdown'])).split())
    value['markdown']=value['markdown'].replace('P '*570,'P '*(570+words-current),1)
    if passed:
        assert validate_polish(value,draft['body'],{'argument-map','source-support'},whole=True,minimum_words=minimum)==value
    else:
        with pytest.raises(Rejected,match='word count'):
            validate_polish(value,draft['body'],{'argument-map','source-support'},whole=True,minimum_words=minimum)


@pytest.mark.parametrize('minimum',[0,6001,True,3000.5])
def test_invalid_publication_floor_refuses_before_calls(rig,monkeypatch,minimum):
    from ara.runtime.publication import polish
    calls,route,seen=install_publication(rig,monkeypatch)
    calls.config['publication_min_words']=minimum
    with pytest.raises(Rejected,match='publication minimum'):
        polish(calls,route,paper())
    assert seen==[]
