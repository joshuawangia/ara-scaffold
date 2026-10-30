"""Native quotation failures use occurrence-bound publication repair budgets."""
import json
import pytest
from ara.runtime.providers import Response
from ara.runtime.calls import Rejected
from test_calls import rig, response
from test_publication import install_publication, paper, polished


def test_quotation_failure_targets_its_exact_occurrence():
    from ara.runtime.publication_verification import quotation_flags
    body='P "Q". R "Q".'
    inputs=dict(sentences=[dict(sentence=1,field='body',start=0,end=6),
                           dict(sentence=2,field='body',start=7,end=len(body))])
    failed=[dict(id='quote:1',kind='quotation',text='Q',status='unverified')]
    assert quotation_flags(dict(body=body),inputs,failed)==[
        dict(sentence=2,role='source_claim',reason='unverified_quotation')]
    with pytest.raises(Rejected):
        quotation_flags(dict(body=body),inputs,[dict(failed[0],text='R')])
    with pytest.raises(Rejected):
        quotation_flags(dict(body=body),inputs,[dict(failed[0],id='quote:8')])


@pytest.mark.parametrize('unchanged,substantive',[(False,False),(True,False),(False,True)])
def test_native_quote_failure_gets_bounded_repair_without_accepting_cleanup(rig,monkeypatch,unchanged,substantive):
    from ara.runtime.publication import polish
    calls,route,_=install_publication(rig,monkeypatch)
    from ara.types import RunEvent
    from ara.runtime.logging import now
    metadata=next(e for e in calls.log.read() if e['stage']=='extract_paper')
    calls.log.emit(RunEvent(now(),'extract_paper','MODEL',
        prompt='P\n'+metadata['prompt'],payload_json=metadata['payload_json']))
    original=calls.provider.complete;repairs=[];audits=[]
    title='R' if substantive else 'P'
    def complete(kind,prompt,schema,maximum):
        data=json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind=='polish_essay' and data['mode']=='whole':
            value=polished(paper());value['markdown']=value['markdown'].replace('[[node:n0]] ', '[[node:n0]] "'+title+'" ',1)
            return Response(response(value))
        if kind=='polish_essay' and data['mode']=='repair':
            repairs.append(data)
            md=data['markdown'] if unchanged else data['markdown'].replace('"'+title+'"','*'+title+'*',1)
            return Response(response(dict(polished(paper()),markdown=md)))
        if kind=='audit_publication':audits.append(data)
        return original(kind,prompt,schema,maximum)
    def verify(draft):
        if '"'+title+'"' in draft['body']:
            return dict(draft,body=draft['body'].replace('"'+title+'"','S')),dict(items=[dict(id='quote:0',kind='quotation',text=title,status='unverified',detail='P')])
        return draft,dict(items=[dict(status='verified')])
    monkeypatch.setattr(calls.provider,'complete',complete)
    monkeypatch.setattr(calls,'verify_originality_citations',verify)
    result,_=polish(calls,route,paper())
    if substantive:
        assert not repairs and not result['polished'] and result['draft']==paper()
        return
    assert [r['repair_round'] for r in repairs]==([1,1] if unchanged else [1])
    assert repairs[0]['flagged_sentences'][0]['reasons']==['unverified_quotation']
    assert not result['polished'] if unchanged else result['polished']
    if unchanged:assert result['draft']==paper()
    else:
        assert '*P*' in result['draft']['body'] and '"P"' not in result['draft']['body']
        assert result['native_citations']['status']=='pass' and len(audits)==9
        assert result['draft']['bibliography']==paper()['bibliography']


def test_format_repair_preserves_title_wording_and_other_occurrences():
    from ara.runtime.publication_verification import title_format_body
    draft=dict(body='P "Q". R “Q”.')
    failed=[dict(id='quote:1',kind='quotation',text='Q',status='unverified')]
    assert title_format_body(draft,failed,{'Q'})=='P "Q". R *Q*.'
    with pytest.raises(Rejected,match='logged work title'):
        title_format_body(draft,failed,{'R'})
