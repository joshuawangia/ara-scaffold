"""Content and source stance remain distinct across the native freeze boundary."""
import json

import pytest

from ara.bank import load_bank
from ara.runtime.cache import canonical, digest
from ara.runtime.calls import Rejected
from ara.runtime.extraction import extract
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.providers import Response
from ara.types import CommitmentSet
from rich_fixture import graph, batch_response
from test_extraction import rig, register, response, pdf, ROOT


def setup(rig, monkeypatch, bad=None, repair=True):
    calls, provider, papers, _, fulltext, _ = rig
    # Re-read paper after placing exact placeholder source text on the page.
    from ara.runtime.extraction import load_papers
    pdf(fulltext / 'p.pdf', ('a argues P P P; b reports Q Q Q; b attacks R R R',))
    papers = load_papers(rig[3], fulltext)
    value = graph()
    value['items'] = value['items'][:3]
    for item, attribution, name in zip(value['items'], ('author_claim','reported_view','attacked_view'), ('P','Q','R')):
        item.update(attribution=attribution, attributed_to='a' if name=='P' else 'b',
                    text={'P':'a argues P P P','Q':'b reports Q Q Q','R':'b attacks R R R'}[name])
    register(calls, provider, papers[0], value)
    path = extract(calls, (papers[0],))
    calls.config['construction_targeted_corrections'] = 1
    sent=[]
    def complete(kind, prompt, schema, maximum):
        inputs=json.loads(prompt.split('\nINPUT_JSON\n')[1]); sent.append(inputs)
        if kind=='select_t_roots':return Response(response(batch_response(inputs)))
        items=[i for p in inputs['papers'] for i in p['items']]
        data=dict(commitments=[dict(id=i['id'],definition=n,formula=dict(op='atom',name=n)) for i,n in zip(items,('P','Q','R'))],
                  new_symbols=[dict(name=n,kind='atom',arity=0,definition=n,evidence_ids=[i['id']]) for i,n in zip(items,('P','Q','R'))],alignments=[])
        field='new_symbols' if bad=='symbol' else 'commitments'
        if bad and (not repair or inputs.get('mode')!='targeted_correction'):
            data[field][0]['definition']='According to a, P'
        if inputs.get('mode')=='targeted_correction':
            data={key: ([data[key][0]] if key==field else []) for key in data}
        return Response(response(data))
    monkeypatch.setattr(provider,'complete',complete)
    return calls,path,sent


def freeze(calls,path):
    return prepare_commitments(calls,load_bank(ROOT/'bank'),path.read_text(),'P')


@pytest.mark.parametrize('authors_supplied',[False,True])
def test_content_stance_and_exact_evidence_survive_freeze(rig,monkeypatch,authors_supplied):
    calls,path,sent=setup(rig,monkeypatch)
    if authors_supplied:
        from ara.runtime.extraction import HEADER
        data=json.loads(path.read_text()[len(HEADER):])
        data['papers'][0]['authors']=['a']
        path=path.parent/'literature-with-authors.txt'
        path.write_text(HEADER+canonical(data))
    original=path.read_bytes()
    result=freeze(calls,path)
    assert {c.text for c in result.commitments}=={'P','Q','R'}
    from ara.runtime.commitment_provenance import load_commitment_provenance
    directory=calls.log.path.parent
    catalogue=json.loads((directory/'frozen-t.json').read_text())['symbol_catalogue']
    metadata=load_commitment_provenance(directory,result,catalogue)
    assert metadata['definition_semantics']=='content'
    assert metadata['commitments_sha256']==digest(canonical(result.to_dict()))
    assert metadata['catalogue_sha256']==catalogue['sha256']
    rows={c.text:metadata['commitments'][c.id] for c in result.commitments}
    assert {key:r['stance'] for key,r in rows.items()}=={'P':'endorsed','Q':'reported','R':'attacked'}
    assert rows['P']['source_text']=='a argues P P P'
    assert rows['Q']['attributed_to']=='b' and rows['R']['attribution']=='attacked_view'
    assert rows['Q']['source_authors']==(['a'] if authors_supplied else [])
    assert all(r['page_start']==r['page_end']==1 and r['source_id']=='p' for r in rows.values())
    assert path.read_bytes()==original
    assert CommitmentSet.from_json((directory/'commitments.json').read_text())==result
    assert all(set(c.to_dict())=={'id','text','citation','formula'} for c in result.commitments)
    assert all(c.citation=='p:pdf:1#'+c.id for c in result.commitments)
    events=calls.log.read()
    receipt=next(json.loads(e['payload_json']) for e in events if e['stage']=='commitment_provenance_frozen')
    assert receipt==metadata
    stages=[e['stage'] for e in events]
    assert stages.index('commitment_provenance_frozen') < stages.index('commitments_frozen')


@pytest.mark.parametrize('bad',['symbol','commitment'])
def test_attributed_definition_gets_logged_targeted_correction(rig,monkeypatch,bad):
    calls,path,sent=setup(rig,monkeypatch,bad)
    result=freeze(calls,path)
    assert {c.text for c in result.commitments}=={'P','Q','R'}
    corrections=[json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='construction_targeted_correction']
    assert len(corrections)==1 and 'content definition' in corrections[0]['reason']
    assert len([s for s in sent if s.get('mode')=='targeted_correction'])==1


@pytest.mark.parametrize('bad',['symbol','commitment'])
def test_uncorrected_attribution_cannot_freeze(rig,monkeypatch,bad):
    calls,path,_=setup(rig,monkeypatch,bad,repair=False)
    with pytest.raises(Rejected):freeze(calls,path)
    assert not (calls.log.path.parent/'commitments.json').exists()


@pytest.mark.parametrize('field',['stance','source_text','catalogue_sha256','commitments_sha256'])
def test_provenance_tampering_refuses(rig,monkeypatch,field):
    calls,path,_=setup(rig,monkeypatch)
    result=freeze(calls,path)
    from ara.runtime.commitment_provenance import validate_commitment_provenance
    directory=calls.log.path.parent
    value=json.loads((directory/'commitment-provenance.json').read_text())
    catalogue=json.loads((directory/'frozen-t.json').read_text())['symbol_catalogue']
    if field.endswith('sha256'):value[field]='0'*64
    else:next(iter(value['commitments'].values()))[field]='attacked' if field=='stance' else 'Q'
    with pytest.raises(ValueError):validate_commitment_provenance(value,result,catalogue)


def test_legacy_metadata_is_unknown_without_codec_changes(tmp_path):
    from ara.runtime.commitment_provenance import load_commitment_provenance
    original={'commitments':[dict(id='p',text='a argues P',citation='p:pdf:1',formula={'op':'atom','name':'P','args':[],'terms':[],'variable':None})]}
    # Establish canonical legacy bytes, without adding default provenance fields.
    t=CommitmentSet.from_dict(original)
    encoded=t.to_dict()
    assert set(encoded['commitments'][0])=={'id','text','citation','formula'}
    assert load_commitment_provenance(tmp_path,t,None) is None


def test_exact_frames_unframed_without_model_correction(rig, monkeypatch):
    calls, path, sent = setup(rig, monkeypatch)
    calls.config['construction_targeted_corrections'] = 0
    complete = calls.provider.complete
    def framed(kind, prompt, schema, maximum):
        raw = complete(kind, prompt, schema, maximum)
        if kind != 'build_t_batch':
            return raw
        data = json.loads(raw.text())
        for field in ('commitments', 'new_symbols'):
            for entry, author, name in zip(data[field], ('a', 'b', 'b'), ('P', 'Q', 'R')):
                entry['definition'] = f'{author} argues that {name}'
        return Response(response(data))
    monkeypatch.setattr(calls.provider, 'complete', framed)
    result = freeze(calls, path)
    assert {c.text for c in result.commitments} == {'P', 'Q', 'R'}
    metadata = json.loads((calls.log.path.parent/'commitment-provenance.json').read_text())
    for c in result.commitments:
        row = metadata['commitments'][c.id]
        assert len(row['definition_unframes']) == 2
        assert {r['kind'] for r in row['definition_unframes']} == {'commitment', 'symbol'}
        assert all(r['original_definition'] == f"{row['attributed_to']} argues that {c.text}" for r in row['definition_unframes'])
        assert row['source_text'] != c.text
    assert {r['stance'] for r in metadata['commitments'].values()} == {'endorsed', 'reported', 'attacked'}
    events = calls.log.read()
    assert sum(e['stage'] == 'definition_unframed' for e in events) == 6
    assert not any(e['stage'] == 'construction_targeted_correction' for e in events)


@pytest.mark.parametrize('definition', ['Not a argues that P', 'If a argues that P, Q',
    'According to a, P', 'z argues that P', 'a argues P', '"a argues that P"'])
def test_nonexact_frames_require_model_correction(rig, monkeypatch, definition):
    calls, path, sent = setup(rig, monkeypatch)
    calls.config['construction_targeted_corrections'] = 0
    complete = calls.provider.complete
    def framed(kind, prompt, schema, maximum):
        raw = complete(kind, prompt, schema, maximum)
        if kind == 'build_t_batch':
            data = json.loads(raw.text()); data['commitments'][0]['definition'] = definition
            return Response(response(data))
        return raw
    monkeypatch.setattr(calls.provider, 'complete', framed)
    with pytest.raises(Rejected): freeze(calls, path)
    assert not any(e['stage'] == 'definition_unframed' for e in calls.log.read())


def test_feedback_names_all_offenders_and_unframed_remainder_is_rechecked(rig, monkeypatch):
    calls, path, sent = setup(rig, monkeypatch)
    calls.config['construction_targeted_corrections'] = 0
    complete = calls.provider.complete
    def framed(kind, prompt, schema, maximum):
        raw = complete(kind, prompt, schema, maximum)
        if kind == 'build_t_batch':
            data = json.loads(raw.text())
            data['commitments'][0]['definition'] = 'a argues that b holds that P'
            data['commitments'][1]['definition'] = 'According to b, Q'
            data['new_symbols'][0]['definition'] = 'a claims P'
            return Response(response(data))
        return raw
    monkeypatch.setattr(calls.provider, 'complete', framed)
    with pytest.raises(Rejected) as error: freeze(calls, path)
    for text in ('p:r1-1:p', 'p:r1-1:q', 'holds', 'According to', 'claims', 'symbol', 'content-only'):
        assert text in str(error.value)
    assert any(e['stage'] == 'definition_unframed' for e in calls.log.read())


def test_second_correction_keeps_first_patch_and_supplies_specific_feedback(rig, monkeypatch):
    calls, path, sent = setup(rig, monkeypatch)
    calls.config['construction_targeted_corrections'] = 2
    complete = calls.provider.complete
    requests = []
    def respond(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind != 'build_t_batch': return complete(kind, prompt, schema, maximum)
        requests.append(inputs)
        if len(requests) == 1:
            data = json.loads(complete(kind, prompt, schema, maximum).text())
            data['commitments'][0]['definition'] = 'a argues P'
            data['commitments'][1]['definition'] = 'b holds Q'
        else:
            index = len(requests) - 2
            assert 'content-only' in inputs['validation_error']
            assert ('argues' if index == 0 else 'holds') in inputs['validation_error']
            entry = {**inputs['candidate']['commitments'][index], 'definition': ('P', 'Q')[index]}
            data = dict(commitments=[entry], new_symbols=[], alignments=[])
        return Response(response(data))
    monkeypatch.setattr(calls.provider, 'complete', respond)
    result = freeze(calls, path)
    assert len(requests) == 3 and {c.text for c in result.commitments} == {'P', 'Q', 'R'}
    assert requests[2]['candidate']['commitments'][0]['definition'] == 'P'
    assert len(requests[2]['candidate']['new_symbols']) == 3


def test_unframing_does_not_peel_nested_frames_across_corrections(rig, monkeypatch):
    calls, path, sent = setup(rig, monkeypatch)
    calls.config['construction_targeted_corrections'] = 2
    complete = calls.provider.complete
    count = 0
    def respond(kind, prompt, schema, maximum):
        nonlocal count
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind != 'build_t_batch': return complete(kind, prompt, schema, maximum)
        count += 1
        if count == 1:
            data = json.loads(complete(kind, prompt, schema, maximum).text())
            for entry, definition in zip(data['commitments'],
                    ('a argues that a holds that P', 'b holds Q', 'b holds R')):
                entry['definition'] = definition
        else:
            index = count - 1
            entry = {**inputs['candidate']['commitments'][index], 'definition': ('P', 'Q', 'R')[index]}
            data = dict(commitments=[entry], new_symbols=[], alignments=[])
        return Response(response(data))
    monkeypatch.setattr(calls.provider, 'complete', respond)
    with pytest.raises(Rejected): freeze(calls, path)
    assert count == 3
    assert not (calls.log.path.parent/'commitments.json').exists()


def test_invalid_patch_keeps_active_definition_feedback(rig, monkeypatch):
    calls, path, sent = setup(rig, monkeypatch, bad='commitment')
    calls.config['construction_targeted_corrections'] = 2
    complete = calls.provider.complete
    count = 0
    def respond(kind, prompt, schema, maximum):
        nonlocal count
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind != 'build_t_batch': return complete(kind, prompt, schema, maximum)
        count += 1
        if count == 1: return complete(kind, prompt, schema, maximum)
        entry = dict(inputs['candidate']['commitments'][0])
        if count == 3:
            for text in ('According to', entry['id'], 'content-only', 'repeats unchanged'):
                assert text in inputs['validation_error']
            entry['definition'] = 'P'
        return Response(response(dict(commitments=[entry], new_symbols=[], alignments=[])))
    monkeypatch.setattr(calls.provider, 'complete', respond)
    assert len(freeze(calls, path).commitments) == 3
    assert count == 3
