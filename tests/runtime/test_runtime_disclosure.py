"""The route status is runtime-owned, not a model-authored paragraph."""
from dataclasses import replace
import json

import pytest

from ara.runtime.hypotheses import insert_runtime_disclosure, validate_disclosure
from ara.runtime.orchestration import NativeEngine
from ara.runtime.route_policy import selectable_routes
from ara.types import Proposition
from test_hypothesis_premises import freeze_h, route_reply, R


def prepared(tmp_path, monkeypatch):
    calls, bank, t, meta, _ = freeze_h(tmp_path, monkeypatch, route_reply)
    route = selectable_routes(NativeEngine(bank,calls)._engine(t).search(Proposition('r','R',R)).routes,t,meta)[0]
    calls.log.record('route', graph=route.to_dict())
    lines = [f'[[node:{n.id}]] ' + ('This paper proposes (P and Q) implies R.'
             if n.t_id == 'hypothesis:h' else 'P Q.') for n in route.nodes]
    authored = dict(title='P',body='\n'.join(lines),bibliography=[])
    draft = insert_runtime_disclosure(calls,route,authored)
    return calls, route, authored, draft


@pytest.mark.parametrize('change', ['missing', 'preceded', 'altered', 'duplicate'])
def test_runtime_disclosure_is_fixed_before_authored_text(tmp_path, monkeypatch, change):
    calls, route, authored, draft = prepared(tmp_path, monkeypatch)
    validate_disclosure(calls.log.read(),route,draft)
    body = dict(missing=authored['body'], preceded='Not:\n\n'+draft['body'],
                altered=draft['body'].replace('conditional on H (hypothesis:h)', 'conditional on H (hypothesis:other)'),
                duplicate=draft['body']+'\n\n'+draft['body'])[change]
    changed={**draft,'body':body}
    with pytest.raises(ValueError, match='hypothesis disclosure'):
        calls.validate_essay(route,changed,minimum_words=0)
    from ara.runtime.export import export_run
    calls.log.record('final_draft',route_id=route.id,draft=changed)
    with pytest.raises(ValueError, match='hypothesis disclosure'):
        export_run(calls.log.path,tmp_path/'export')


def test_runtime_disclosure_needs_route_bound_insertion(tmp_path, monkeypatch):
    calls, route, authored, draft = prepared(tmp_path,monkeypatch)
    events=calls.log.read()
    validate_disclosure(events,route,draft)
    without=[e for e in events if e['stage']!='hypothesis_disclosure_inserted']
    with pytest.raises(ValueError,match='insertion receipt'):
        validate_disclosure(without,route,draft)
    changed=replace(route,id='different-route')
    with pytest.raises(ValueError,match='insertion receipt'):
        validate_disclosure(events,changed,draft)
    # Recorded author bytes and the fixed block are independently inspectable.
    from ara.runtime.cache import digest
    row=next(json.loads(e['payload_json']) for e in events if e['stage']=='hypothesis_disclosure_inserted')
    assert row['authored_body_sha256']==digest(authored['body'])
    assert row['block_sha256']==digest(row['block'])
    assert draft['body']==row['block']+authored['body']


@pytest.mark.parametrize('status', ['Not Conditional on H.', 'The result is 𝐮𝐧𝐜𝐨𝐧𝐝𝐢𝐭𝐢𝐨𝐧𝐚𝐥.'])
def test_runtime_authored_status_is_reserved(tmp_path,monkeypatch,status):
    calls,route,authored,_=prepared(tmp_path,monkeypatch)
    with pytest.raises(ValueError,match='hypothesis disclosure'):
        calls.validate_essay(route,{**authored,'body':authored['body']+'\n\n'+status},
                             minimum_words=0,authored=True)
