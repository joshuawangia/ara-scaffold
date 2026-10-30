import json
from pathlib import Path
from test_hypothesis_premises import freeze_h,route_reply,R
from ara.runtime.orchestration import NativeEngine
from ara.runtime.route_policy import route_contribution,selectable_routes
from ara.runtime.report import generate_report
from ara.types import Proposition


import pytest

@pytest.mark.parametrize('closed',[True,False])
def test_route_selection_summaries_disclose_hypotheses(tmp_path,monkeypatch,closed):
    from ara.types import Formula
    from test_hypothesis_premises import P,Q
    from ara.runtime.render import render_tree
    def reply(kind,data):
        if not closed and kind=='propose_cuts' and data['goal']['formula']==Formula('and',(P,Q)).to_dict():
            return dict(proposals=[])
        return route_reply(kind,data)
    calls,bank,t,meta,_=freeze_h(tmp_path/'native',monkeypatch,reply)
    result=NativeEngine(bank,calls)._engine(t).search(Proposition('r','R',R))
    route=next(r for r in result.routes if any(n.t_id=='hypothesis:h' for n in r.nodes))
    assert route.status==('CLOSED' if closed else 'OPEN')
    calls.log.record('route',graph=route.to_dict())
    generate_report([calls.log.path.parent],tmp_path/'report')
    data=json.loads((tmp_path/'report/data.json').read_text())
    summary=data['runs'][0]['routes'][0]
    route_list=json.loads((tmp_path/'report/run-0/routes.json').read_text())['routes'][0]
    detail=json.loads((tmp_path/'report'/summary['file']).read_text())
    receipt=route_contribution(route,t,meta)
    for row in (receipt,detail['contribution'],summary,route_list):
        assert row.get('conditional_on')==['hypothesis:h']
        assert 'conditional on H' in row['conclusion_status']
        assert row['hypothesis_disclosure']['conditional_on']==['hypothesis:h']
        if not closed: assert 'no completed conclusion' in row['conclusion_status']
    assert summary['classification']==('CLOSED-derived' if closed else 'OPEN')
    assert summary['selectable_by_default'] is closed
    assert 'conditional on H' in render_tree(route,t,meta).splitlines()[0]
    html=(tmp_path/'report/report.html').read_text().split('5. Routes for selection',1)[1].split('</section>',1)[0]
    assert 'conditional on H' in html
