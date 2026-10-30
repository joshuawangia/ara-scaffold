"""Proposal publication layout and bounded currency evidence; placeholders only."""
import pytest

from ara.runtime.calls import Rejected
from test_publication import paper, polished
from test_calls import rig


def scoped_value():
    value = polished(paper())
    value['markdown'] = value['markdown'].replace('2. Argument', '2. Proposal').replace(
        '4. Limits', '4. Conclusion').replace('5. Conclusion', '5. Status and method')
    return value


def test_proposal_layout_keeps_argument_and_limits_without_extra_headings():
    from ara.runtime.publication import validate_polish
    value = scoped_value()
    for heading in ('Introduction','Objections and replies','Conclusion','Status and method'):
        value['markdown'] = value['markdown'].replace(heading, 'P')
    assert validate_polish(value, paper()['body'], {'argument-map', 'source-support'}, whole=True, proposal=True)
    with pytest.raises(Rejected, match='required section'):
        validate_polish(value, paper()['body'], {'argument-map', 'source-support'}, whole=True)


def currency():
    return dict(evidence={'r:search': dict(kind='bounded_search_record', work=None),
                          'r:p': dict(kind='read_fulltext', work='p')})


def test_proposal_currency_requires_evidence_not_ritual_location():
    from ara.runtime.publication_currency import check_currency
    md = '## 1. Proposal\n\nP.\n\n## 2. Status and method\n\nQ. [lit:r:search] R. [lit:r:p]'
    check_currency(md, currency(), proposal=True)
    check_currency(md.replace('P.', 'P. [lit:r:p]'), currency(), proposal=True)
    check_currency('## 1. Proposal\n\nP. [lit:r:p]', currency(), proposal=True)
    check_currency('## 1. Proposal\n\nP.', currency(), proposal=True)
    with pytest.raises(Rejected, match='unrecorded'):
        check_currency(md.replace('r:p', 'r:q'), currency(), proposal=True)
    with pytest.raises(Rejected, match='related-work'):
        check_currency(md, currency())


def test_publication_audit_preserves_proposal_currency_boundary():
    from ara.runtime.publication_audit import publication_flags
    label = dict(sentence=1, role='source_claim', citation_supported=True, node_ids=[], publication_issue='none')
    inputs = dict(proposal={'disclosure': 'P'}, publication_context={'literature_currency': currency()},
                  sentences=[dict(sentence=1, text='P. [lit:r:search]', section='Status and method')])
    native = [dict(sentence=1, role='source_claim', reason='miscited_source_claim')]
    assert publication_flags([label], inputs, native) == []
    inputs['sentences'][0]['section'] = 'Proposal'
    assert publication_flags([label], inputs, []) == []
    inputs['sentences'][0]['section'] = 'Status and method'
    inputs.pop('proposal')
    assert any(f['reason'] == 'literature_scope' for f in publication_flags([label], inputs, []))


def test_proposal_status_note_is_not_a_structural_gate():
    from ara.runtime.publication import validate_polish
    value = scoped_value()
    value['markdown'] = value['markdown'].replace('4. Conclusion', '4. Status and method').replace(
        '5. Status and method', '5. Conclusion')
    assert validate_polish(value, paper()['body'], {'argument-map', 'source-support'}, whole=True, proposal=True)


@pytest.mark.parametrize('change', ['none', 'draft', 'route', 'flags', 'samples', 'restart'])
def test_legacy_import_needs_current_exact_k3_export(change):
    import json
    from types import SimpleNamespace
    from ara.runtime.cache import canonical, digest
    from ara.runtime.publication import verified_legacy_import
    draft = dict(title='P', body='Q', bibliography=[])
    gate = dict(audit_kind='audit_essay', status='complete', route_id='r', k=3,
                faithful=True, flags=[], draft_sha256=digest(canonical(draft)),
                samples=[dict(faithful=True, flags=[])] * 3)
    final = dict(route_id='r', draft=draft)
    if change == 'route': final['route_id'] = 'q'
    if change == 'flags': gate['flags'] = [dict(sentence=1)]
    if change == 'samples': gate['samples'] = gate['samples'][:2]
    events = [dict(stage=s, payload_json=json.dumps(p)) for s,p in [
        ('essay_composition_started', {}), ('essay_audit_consensus', gate), ('final_draft', final)]]
    if change == 'draft': draft = {**draft, 'body': 'R'}
    if change == 'restart': events.append(dict(stage='essay_composition_started', payload_json='{}'))
    assert verified_legacy_import(events, SimpleNamespace(id='r'), draft) is (change == 'none')


@pytest.mark.parametrize('exported', [True, False])
@pytest.mark.parametrize('metadata', [True, False])
def test_native_publication_imports_legacy_only_with_verified_export(rig, monkeypatch, exported, metadata):
    import json
    from ara.runtime.cache import canonical, digest
    from ara.runtime.claude_code import ClaudeCodeError
    from ara.runtime.publication import polish, paragraphs
    from ara.runtime.publication_figures import figure_data
    from ara.runtime.providers import Response
    from test_calls import response
    from test_proposal_mode import setup, DISCLOSURE
    calls, provider, log = rig
    route, _ = setup(calls, log)
    calls.config.update(token_cap=20_000_000, validation_attempts=1)
    original = paper()
    original['title'] += ' — ' + DISCLOSURE
    original['body'] = '## Abstract\n\n' + DISCLOSURE + '.\n\n' + original['body'] + '\n\n## Methodology\n\n' + DISCLOSURE + '.'
    if exported:
        log.record('essay_composition_started', route_id=route.id)
        log.record('essay_audit_consensus', audit_kind='audit_essay', status='complete', route_id=route.id,
                   k=3, faithful=True, flags=[], samples=[dict(faithful=True, flags=[])]*3,
                   draft_sha256=digest(canonical(original)))
        log.record('final_draft', route_id=route.id, draft=original)
    md = '# P — '+DISCLOSURE+'\n\n## Abstract\n\nDisclosure: '+DISCLOSURE+'. '+('P '*160)
    md += '\n\n## 1. Introduction\n\n'+('P '*300)
    md += '\n\n## 2. Source positions\n\nP P. [cite:p] Q Q. [cite:q]'
    md += '\n\n## 3. Proposal\n\n[[node:n0]] [[node:n1]] '+('P '*1800)+'.'
    md += '\n\n## 4. Objections and replies\n\n'+('Q '*700)+'.'
    md += '\n\n## 5. Conclusion\n\n**Proposal:** '+('R '*100)+'.'
    md += '\n\n## 6. Status and method\n\nP.'
    figures = figure_data(calls, route)
    placements = [dict(id=f['id'], after_paragraph=len(paragraphs(md))-1) for f in figures]
    md += ''.join('\n\n{{fig:'+f['id']+'}}' for f in figures)
    seen=[]
    def complete(kind, prompt, schema, maximum):
        data=json.loads(prompt.split('INPUT_JSON\n')[1]);seen.append((kind,data))
        if kind=='polish_essay':
            text=data['markdown'] if data['mode']=='section' else md
            if data['mode']=='whole' and not metadata:
                text=text.replace(' — '+DISCLOSURE,'').replace('Disclosure: '+DISCLOSURE+'. ','')
            value=dict(markdown=text, figure_placements=[] if data['mode']=='section' else placements,
                       change_log=[dict(paragraph=i,improvement='P') for i in range(len(paragraphs(text)))])
        elif kind=='audit_publication':
            labels=[]
            for s in data['sentences']:
                scoped=s.get('proposal_scope')
                role=('proposed_principle' if s['text'].startswith('P ') else 'argument_for_proposal') if scoped else (
                    'source_claim' if '[cite:' in s['text'] else 'framing')
                labels.append(dict(sentence=s['sentence'],role=role,node_ids=['n0','n1'] if role=='proposed_principle' else [],citation_supported=True,publication_issue='none'))
            value=dict(labels=labels)
        else: raise AssertionError(kind)
        return Response(response(value))
    monkeypatch.setattr(provider,'complete',complete)
    estimate=provider.estimate
    def estimate_call(kind,*args):
        if kind=='search_evidence':raise ClaudeCodeError('stage_requires_api_provider')
        return estimate(kind,*args)
    monkeypatch.setattr(provider,'estimate',estimate_call)
    if not exported:
        with pytest.raises(Rejected,match='proposal'):polish(calls,route,original)
        assert not seen
        return
    result,directory=polish(calls,route,original)
    assert result['polished'] and result['audit']['faithful']
    assert result['draft']['title']==('P — '+DISCLOSURE if metadata else 'P')
    assert DISCLOSURE in result['markdown'].split('## Abstract')[0]
    assert any(e['stage']=='publication_proposal_disclosure_inserted' for e in log.read()) is (not metadata)
    assert len([d for kind,d in seen if kind=='audit_publication'])==3
    assert '[cite:' not in (directory/'paper.md').read_text()
    assert result['original_sha256']==digest(canonical(original))
    assert next(json.loads(e['payload_json'])['draft'] for e in log.read() if e['stage']=='final_draft')==original


def test_codex_writer_window_stays_on_codex_audit_not_claude_polish(rig):
    import copy, json
    from types import SimpleNamespace
    from ara.runtime.codex_window import apply_context_window
    from ara.runtime.construction_stages import dispatch_settings
    from ara.runtime.publication import publication_command
    from test_calls import graph
    calls,_,log=rig
    config=copy.deepcopy(calls.config)
    config.update(provider='codex_cli',model='gpt-6-luna',model_context_window=872000,
                  model_context_margin_tokens=16384,model_context_token_bound=839232)
    log.record('run_started',config=config,topic='P')
    route=graph();log.record('route',graph=route.to_dict())
    draft_path=log.path.parent/'draft.json';draft_path.write_text(json.dumps(paper()))
    args=SimpleNamespace(command='polish',run_dir=log.path.parent,route=route.id,draft=draft_path,
                         min_words=3000,audit_provider='codex_cli',audit_model=None,unknown_usage_policy=None,
                         literature_currency=[])
    class Captured(Exception):pass
    def factory(settings,*unused,**kwargs):
        assert settings['provider']=='claude_code'
        assert apply_context_window(settings) is None
        assert settings['model_context_token_bound']<=200000
        audit=dispatch_settings(settings,'audit_publication')[2]
        assert audit['provider']=='codex_cli' and audit['model_context_window']==872000
        assert audit['model_context_token_bound']>200000
        raise Captured
    with pytest.raises(Captured):publication_command(args,log,calls.root,factory)
    assert json.loads(log.read()[0]['payload_json'])['config']==config


@pytest.mark.parametrize('issue', ['thesis_placement', 'literature_scope'])
def test_proposal_audit_does_not_promote_style_labels_to_substantive_failures(issue):
    from ara.runtime.publication_audit import publication_flags
    label=dict(sentence=1,role='source_claim',citation_supported=True,node_ids=[],publication_issue=issue)
    inputs=dict(proposal={'disclosure':'P'},publication_context={'literature_currency':currency()},
                sentences=[dict(sentence=1,text='P. [lit:r:p]',section='Proposal')])
    assert publication_flags([label],inputs,[])==[]
    label['citation_supported']=False
    assert any(f['reason']=='miscited_literature_claim' for f in publication_flags([label],inputs,[]))
    label['citation_supported']=True;inputs.pop('proposal')
    assert any(f['reason']==issue for f in publication_flags([label],inputs,[]))


def test_proposal_section_still_required():
    from ara.runtime.publication import validate_polish
    value=scoped_value();value['markdown']=value['markdown'].replace('2. Proposal','2. P')
    with pytest.raises(Rejected,match='required section'):
        validate_polish(value,paper()['body'],{'argument-map','source-support'},whole=True,proposal=True)


def test_selected_auditor_runs_native_verification_without_editor_fallback(rig,monkeypatch):
    import json
    from ara.runtime.publication import polish
    from ara.runtime.providers import MockProvider,Response
    from test_calls import response
    from test_publication import install_publication
    calls,route,_=install_publication(rig,monkeypatch)
    calls.config['stages']={'audit_publication':dict(provider='mock',model='P')}
    calls.config['pricing']['P']=calls.config['pricing'][calls.config['model']]
    backend=MockProvider({},'P');seen=[]
    def complete(kind,prompt,schema,maximum):
        seen.append(kind)
        if kind=='search_evidence':return Response(response('P',model='P'))
        if kind=='verify_originality_citations':
            data=json.loads(prompt.split('INPUT_JSON\n')[1]);assert data['items']==[]
            return Response(response(dict(items=[],originality=dict(assessment='unverified',detail='P',evidence_urls=[])),model='P'))
        return Response({**calls.provider.complete(kind,prompt,schema,maximum).raw,'model':'P'})
    monkeypatch.setattr(backend,'complete',complete)
    calls.provider_factory=lambda settings:backend
    result,_=polish(calls,route,paper())
    assert result['polished'] and result['native_citations']['status']=='pass'
    assert seen.count('audit_publication')==6
    assert 'search_evidence' in seen and 'verify_originality_citations' in seen


def test_front_matter_does_not_hide_abstract_node_markers():
    from ara.runtime.publication import validate_polish,paragraphs
    value=scoped_value()
    value['markdown']=value['markdown'].replace('## Abstract','P.\n\n## Abstract',1).replace('P '*175,'[[node:n0]] '+'P '*175,1)
    value['change_log']=[dict(paragraph=i,improvement='P') for i in range(len(paragraphs(value['markdown'])))]
    for placement in value['figure_placements']:placement['after_paragraph']+=1
    with pytest.raises(Rejected,match='abstract'):
        validate_polish(value,paper()['body'],{'argument-map','source-support'},whole=True,proposal=True)
