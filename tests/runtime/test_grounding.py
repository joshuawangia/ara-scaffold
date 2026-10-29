"""Offline grounding and quarantine boundaries, using symbolic source content."""
import copy
import json
from dataclasses import replace

import pytest

from ara.runtime.extraction import HEADER, PageText, extract, citation_ids
from rich_fixture import graph
from test_extraction import rig, offline, register, accounting


def sample():
    value = graph()
    for item in value['items']:
        if item['text'] in ('P', 'Q', 'R'):
            item['text'] = f"{item['text']} {item['text']} {item['text']}"
        item['attributed_to'] = 'a'
    return value


def test_publication_quarantine_propagates_and_excludes_t(rig, monkeypatch):
    from ara.runtime.providers import Response
    from rich_fixture import batch_response
    from test_extraction import response
    calls, provider, papers, *_ = rig
    paper = replace(papers[0], pages=(PageText(1, 'P Q R F x'), PageText(2, 'S')))
    value = sample(); value['items'][0]['text'] = 'placeholder'
    register(calls, provider, paper, value)
    path = extract(calls, (paper,))
    payload = json.loads(path.read_text()[len(HEADER):])['papers'][0]
    q = {v['item_id']: v for v in payload['quarantined']}
    assert set(q) == {'p:r1-2:p', 'p:r1-2:i'}
    assert q['p:r1-2:p']['reasons'] == ['junk_placeholder_prefix']
    assert q['p:r1-2:i']['blocked_by'] == ['p:r1-2:p']
    assert len(payload['items']) == 8  # original retained inventory, never lost
    assert len(citation_ids(path.read_text())) == 6
    assert accounting(calls.log)['extraction']['grounding'][0]['quarantined'] == 2
    seen = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1]); seen.append(inputs)
        return Response(response(batch_response(inputs)))
    monkeypatch.setattr(provider, 'complete', complete)
    result = calls.build_t(path.read_text(), 'P')
    assert not {c.id for c in result.commitments} & q.keys()
    assert all(not {i['id'] for p in r['papers'] for i in p['items']} & q.keys() for r in seen)
    assert any(e['stage'] == 'extraction_item_quarantined' for e in calls.log.read())


@pytest.mark.parametrize(('text','attribution','reason'), [
    ('Placeholder P','a','junk_placeholder_prefix'), ('x','a','junk_short_text'),
    ('PQ','a','junk_short_text'), ('P P P','P P P','junk_text_equals_attribution'),
    ('... 123','a','junk_nonword'), ('S S S','a','insufficient_page_overlap'),
    ('P Q R S F X Y','a','insufficient_page_overlap'),
    ('P Q S','a','insufficient_page_overlap'),
])
def test_junk_and_page_grounding(rig, text, attribution, reason):
    calls, provider, papers, *_ = rig
    paper = replace(papers[0], pages=(PageText(1, 'P Q R'), PageText(2, 'S')))
    value = sample(); value['items'] = [dict(value['items'][0],text=text,attributed_to=attribution)]
    register(calls, provider, paper, value)
    payload = json.loads(extract(calls, (paper,)).read_text()[len(HEADER):])['papers'][0]
    assert reason in payload['quarantined'][0]['reasons']
    assert payload['grounding']['accepted_items'] == 0


def test_overlap_threshold_normalization_and_cited_pages(rig):
    calls, provider, papers, *_ = rig
    paper = replace(papers[0], pages=(PageText(1, 'P Q R'), PageText(2, 'S F')))
    value = sample(); value['items'] = [dict(value['items'][0],text='P, Q; R / S / F / X')]
    register(calls, provider, paper, value)
    payload = json.loads(extract(calls, (paper,)).read_text()[len(HEADER):])['papers'][0]
    assert payload['quarantined'] == [] # 3/6 at threshold; other page cannot contribute
    assert payload['grounding']['accepted_items'] == 1


def test_ungated_and_tampered_inventory_cannot_supply_citations(rig):
    calls, provider, papers, *_ = rig
    value = sample(); value['items'][0]['text'] = 'placeholder'
    register(calls, provider, papers[0], value)
    text = extract(calls, papers[:1]).read_text()
    data = json.loads(text[len(HEADER):])
    data['papers'][0].pop('grounding')
    with pytest.raises(ValueError, match='grounding'):
        calls.build_t(HEADER + json.dumps(data), 'P')
    data = json.loads(text[len(HEADER):]); data['papers'][0]['quarantined'] = []
    with pytest.raises(ValueError, match='grounding'):
        citation_ids(HEADER + json.dumps(data))


def test_correction_can_discard_unsupported_rejected_items(rig, monkeypatch):
    from test_extraction_acceptance import sequence
    calls, provider, papers, *_ = rig
    calls.config['extraction_targeted_corrections'] = 1
    bad = sample(); bad['items'] = [dict(bad['items'][0],page_end=99)]
    patch = {**bad, 'items': [], 'discard_items': [dict(id='p', reason='P')], 'empty_reason':'P'}
    sequence(monkeypatch, provider, [bad,patch])
    result = calls.extract_paper(papers[0])
    assert result.items == ()
    assert any(e['stage']=='extraction_candidate_discarded' for e in calls.log.read())


def test_v4_and_thin_history_revalidated_without_dispatch(rig, monkeypatch, tmp_path):
    import ara.runtime.extraction as module
    from ara.runtime.calls import ModelCalls
    from ara.runtime.cache import Cache
    from ara.runtime.extraction import resume_papers, V4_PROMPT_SHA256, V4_SCHEMA_SHA256
    from ara.runtime.logging import EventLog
    from test_extraction import ROOT
    calls, provider, papers, *_ = rig
    identity = module.extraction_acceptance_identity(calls.config, ROOT)
    previous = {**identity, 'version':'rich-paper-acceptance-v4',
                'prompt_sha256':V4_PROMPT_SHA256, 'schema_sha256':V4_SCHEMA_SHA256}
    monkeypatch.setattr(module, 'extraction_acceptance_identity', lambda *a: previous)
    papers = (replace(papers[0], pages=(PageText(1, 'P'), PageText(2, 'Q'))),)
    register(calls, provider, papers[0], sample())
    original = extract(calls, papers[:1])
    monkeypatch.setattr(module, 'extraction_acceptance_identity', lambda *a: identity)
    log = EventLog(tmp_path/'revalidate/events.jsonl')
    reused = resume_papers(log, papers[:1], [calls.log.path.parent], calls.config, ROOT, revalidate_only=True)
    def forbidden(*a,**kw): raise AssertionError('offline revalidation dispatched')
    monkeypatch.setattr(provider,'complete',forbidden)
    follow = ModelCalls(calls.config,provider,log,Cache(tmp_path/'new-cache'),ROOT,'')
    path=extract(follow,papers[:1],reused=reused,salvage_only=True)
    result=json.loads(path.read_text()[len(HEADER):])['papers'][0]
    assert result['items']==json.loads(original.read_text()[len(HEADER):])['papers'][0]['items']
    assert result['quarantined'] and result['grounding']['accepted_items']==1
    module.literature_provenance(path,path.read_text())


def test_quarantined_resolution_reopens_gap(rig):
    from ara.runtime.extraction import literature_entry
    calls,provider,papers,*_=rig
    value=sample(); value['items'][0]['text']='placeholder'
    register(calls,provider,papers[0],value)
    extract(calls,papers[:1])
    outcome=json.loads((calls.log.path.parent/'p.extraction.json').read_text())
    blocked=outcome['quarantined'][0]['item_id']
    outcome['obligations']=[dict(id='g',description='P')]
    outcome['resolutions']=[dict(obligation_id='g',evidence_ids=[blocked])]
    assert literature_entry(outcome)['open_gaps']==outcome['obligations']


def test_discard_cannot_remove_accepted_and_terminal_pruning_removes_dangling_link(rig,monkeypatch):
    from ara.runtime.calls import merge_extraction_patch,Rejected
    candidate=sample()
    with pytest.raises(Rejected,match='discard'):
        merge_extraction_patch(candidate,{**candidate,'items':[], 'discard_items':[dict(id='accepted:p',reason='P')]})
    from test_extraction_acceptance import sequence
    calls,provider,papers,*_=rig
    calls.config['extraction_targeted_corrections']=1
    candidate['items'][0]['page_end']=99
    patch={**candidate,'items':[], 'discard_items':[dict(id='p',reason='P')]}
    sequence(monkeypatch,provider,[candidate,patch])
    result = calls.extract_paper(papers[0])
    assert len(result.items) == 7  # Only the model's explicit rejected-item discard.
    assert next(i for i in result.items if i.id.endswith(':i')).premise_ids == ('p:r1-2:q',)
    repairs = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='extraction_structure_repaired']
    assert len(repairs) == 1 and repairs[0]['status'] == 'accepted'
    assert repairs[0]['removed'] == 1 and repairs[0]['total'] == 9


def test_revalidated_history_can_resume_again_without_conflict(rig,monkeypatch,tmp_path):
    from ara.runtime.extraction import resume_papers
    from ara.runtime.calls import ModelCalls
    from ara.runtime.logging import EventLog
    from ara.runtime.cache import Cache
    from test_extraction import ROOT
    calls,provider,papers,*_=rig
    register(calls,provider,papers[0],sample())
    with monkeypatch.context() as old:
        old.setattr('ara.runtime.grounding.ground_outcome', lambda paper,outcome,log: outcome)
        extract(calls,papers[:1])
    for n in range(2):
        log=EventLog(tmp_path/f'resume{n}/events.jsonl')
        reused=resume_papers(log,papers[:1],[calls.log.path.parent],calls.config,ROOT)
        calls=ModelCalls(calls.config,provider,log,Cache(tmp_path/f'cache{n}'),ROOT,'')
        def forbidden(*a,**kw): raise AssertionError('reused paper dispatched')
        monkeypatch.setattr(provider,'complete',forbidden)
        path=extract(calls,papers[:1],reused=reused,salvage_only=True)
        assert len(citation_ids(path.read_text()))==8
