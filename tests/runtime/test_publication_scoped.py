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
    assert validate_polish(value, paper()['body'], {'argument-map', 'source-support'}, whole=True, proposal=True)
    with pytest.raises(Rejected, match='required section'):
        validate_polish(value, paper()['body'], {'argument-map', 'source-support'}, whole=True)


def currency():
    return dict(evidence={'r:search': dict(kind='bounded_search_record', work=None),
                          'r:p': dict(kind='read_fulltext', work='p')})


def test_proposal_currency_is_confined_to_status_note():
    from ara.runtime.publication_currency import check_currency
    md = '## 1. Proposal\n\nP.\n\n## 2. Status and method\n\nQ. [lit:r:search] R. [lit:r:p]'
    check_currency(md, currency(), proposal=True)
    with pytest.raises(Rejected, match='only'):
        check_currency(md.replace('P.', 'P. [lit:r:p]'), currency(), proposal=True)
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
    assert any(f['reason'] == 'literature_scope' for f in publication_flags([label], inputs, []))
    inputs['sentences'][0]['section'] = 'Status and method'
    inputs.pop('proposal')
    assert any(f['reason'] == 'literature_scope' for f in publication_flags([label], inputs, []))


def test_proposal_status_note_must_be_last():
    from ara.runtime.publication import validate_polish
    value = scoped_value()
    value['markdown'] = value['markdown'].replace('4. Conclusion', '4. Status and method').replace(
        '5. Status and method', '5. Conclusion')
    with pytest.raises(Rejected, match='last'):
        validate_polish(value, paper()['body'], {'argument-map', 'source-support'}, whole=True, proposal=True)


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
def test_native_publication_imports_legacy_only_with_verified_export(rig, monkeypatch, exported):
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
    md = '# P\n\n## Abstract\n\nDisclosure: '+DISCLOSURE+'. '+('P '*160)
    md += '\n\n## 1. Introduction\n\n'+('P '*300)
    md += '\n\n## 2. Source positions\n\nP P. [cite:p] Q Q. [cite:q]'
    md += '\n\n## 3. Proposal\n\n[[node:n0]] [[node:n1]] '+('P '*1800)+'.'
    md += '\n\n## 4. Objections and replies\n\n'+('Q '*700)+'.'
    md += '\n\n## 5. Conclusion\n\n**Proposal:** '+('R '*100)+'.'
    md += '\n\n## 6. Status and method\n\nDisclosure: '+DISCLOSURE+'.'
    figures = figure_data(calls, route)
    placements = [dict(id=f['id'], after_paragraph=len(paragraphs(md))-1) for f in figures]
    md += ''.join('\n\n{{fig:'+f['id']+'}}' for f in figures)
    seen=[]
    def complete(kind, prompt, schema, maximum):
        data=json.loads(prompt.split('INPUT_JSON\n')[1]);seen.append((kind,data))
        if kind=='polish_essay':
            text=data['markdown'] if data['mode']=='section' else md
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
        with pytest.raises(Rejected,match='title'):polish(calls,route,original)
        assert not seen
        return
    result,directory=polish(calls,route,original)
    assert result['polished'] and result['audit']['faithful']
    assert result['draft']['title']=='P' and 'Status and method' in result['markdown']
    assert len([d for kind,d in seen if kind=='audit_publication'])==3
    assert '[cite:' not in (directory/'paper.md').read_text()
    assert result['original_sha256']==digest(canonical(original))
    assert next(json.loads(e['payload_json'])['draft'] for e in log.read() if e['stage']=='final_draft')==original
