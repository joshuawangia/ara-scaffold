"""New review gaps survive the single review pass; no obligation queue."""
import json

import pytest

from ara.runtime.providers import Response
from rich_fixture import graph
from test_extraction import rig, offline, response


@pytest.mark.parametrize('description', ['R', 'Q'])
@pytest.mark.parametrize('resolve_original', [False, True])
def test_new_gap_survives_original_resolution(rig, monkeypatch, resolve_original, description):
    calls, provider, papers, *_ = rig
    seen = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1]); seen.append(inputs)
        value = graph()
        value.update(coverage_complete=False, new_gaps=[{'description': description}])
        if len(seen) == 2:
            value['items'] = []
            oid = inputs['obligations'][0]['id']
            if resolve_original:
                value['resolutions'] = [dict(obligation_id=oid, evidence_ids=['p:r1-2:p'])]
            else:
                value['pending_obligation_ids'] = [oid]
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    result = calls.extract_paper(papers[0]).to_dict()
    assert len(seen) == 2 and len(result['items']) == 8
    assert len(result['obligations']) == 2 and len(result['resolutions']) == int(resolve_original)
    assert [o['description'] for o in result['obligations']] == [description, description]
    assert len({o['id'] for o in result['obligations']}) == 2
    models = [e for e in calls.log.read() if e['label'] == 'MODEL']
    assert len(models) == 2 and all(json.loads(e['payload_json'])['status'] == 'accepted' for e in models)
    assert all(e['cost_usd'] == .00175 for e in models)
    assert (calls.log.path.parent/'p.joined.rich.json').exists()
