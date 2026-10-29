"""Codex transport must preserve native range extraction and local constraints."""
import json
from dataclasses import replace

import pytest
from jsonschema import Draft202012Validator, ValidationError

from test_codex_cli import codex, ROOT
from ara.runtime.cli import make_calls
from ara.runtime.logging import EventLog
from ara.runtime.extraction import Paper, PageText, extraction_range_plan
from ara.runtime.codex_schema import strict_schema, normalize_output, wire_value

VARIANTS = [dict(mode='initial'), dict(mode='reconcile_ranges'),
            dict(mode='reconcile_ranges',obligations=[{'id':'P'}])]
VARIANTS += [{**v,'mode':'targeted_correction','original_mode':v['mode'],'candidate':{'items':items}}
             for v in list(VARIANTS) for items in ([],[{'id':'P'}])]


@pytest.mark.parametrize('inputs',VARIANTS)
def test_all_extraction_mode_wires(codex,inputs):
    config,auth,write,tmp=codex
    calls=make_calls(config,EventLog(tmp/'events.jsonl'),'P')
    local=calls.response_schema('extract_paper',inputs);wire=strict_schema(local)
    assert 'anyOf' not in wire  # OpenAI strict requires a root object.
    assert wire['additionalProperties'] is False
    assert set(wire['required'])==set(wire['properties'])
    from rich_fixture import graph
    value=graph()
    if inputs['mode']=='targeted_correction':value['discard_items']=[{'id':'q','reason':'P'}]
    encoded=wire_value(local,value)
    Draft202012Validator(wire).validate(encoded)
    restored=normalize_output(local,encoded)
    assert restored['items']==value['items'] and 'no_inference_reason' not in restored
    Draft202012Validator(local).validate(restored)
    invalid={**restored,'items':[{**restored['items'][0],'page_start':0}]}
    with pytest.raises(ValidationError):Draft202012Validator(local).validate(invalid)
    if inputs['mode']=='initial':
        with pytest.raises(ValidationError):Draft202012Validator(local).validate({**restored,'items':[]})


def test_native_extraction_and_targeted_correction(codex):
    config,auth,write,tmp=codex
    config.update(extraction_targeted_corrections=1,validation_attempts=1,token_cap=2000000,
                  extraction_require_inference=True)
    write('extract:correction');log=EventLog(tmp/'events.jsonl');calls=make_calls(config,log,'P')
    paper=Paper('p','{}','P',(PageText(1,'P Q R F(x)'),))
    result=calls.extract_paper(paper)
    assert len(result.items)==8 and sum(i.kind=='inference' for i in result.items)==2
    events=log.read();rows=[e for e in events if e['label']=='MODEL' and e['stage']=='extract_paper']
    assert any(json.loads(e['payload_json'])['status']=='rejected' for e in rows)
    assert any('targeted_correction' in e['prompt'] for e in rows)
    assert all(json.loads(e['payload_json'])['provider']=='codex_cli' and e['cost_usd']==0 for e in rows)
    assert all(e['usage']['input_tokens']>0 for e in rows)
    assert any(e['stage']=='extraction_graph_merged' for e in events)
    assert all('offline-access' not in e['payload_json'] for e in events)


def test_counted_ranges_include_cli_output_bound_without_truncation(codex):
    config,auth,write,tmp=codex
    config.update(extract_paper_max_output_tokens=1000,token_cap=2000000)
    calls=make_calls(config,EventLog(tmp/'events.jsonl'),'P')
    paper=Paper('p','{}','P',tuple(PageText(i,'P '*4000) for i in range(1,5)))
    full=calls.count_request('extract_paper',paper.inputs())
    calls.config['model_context_token_bound']=full.initial_input_tokens+1000
    plan=extraction_range_plan(calls,paper)
    assert len(plan)>1
    assert [p for pages,_ in plan for p in pages]==list(paper.pages)
    for pages,_ in plan:
        count=calls.count_request('extract_paper',replace(paper,pages=pages).inputs(),admission=True)
        assert count.initial_input_tokens+count.context_output_tokens<=calls.config['model_context_token_bound']
    assert not any(e['stage']=='call_start' and json.loads(e['payload_json'])['kind']=='extract_paper' for e in calls.log.read())


def test_codex_extraction_preflight_uses_strict_wires(codex):
    from ara.runtime.preflight import schema_preflight
    config,auth,write,tmp=codex;write('preflight')
    calls=make_calls(config,EventLog(tmp/'events.jsonl'),'P')
    result=schema_preflight(calls)
    assert result['passed'] and result['distinct_schemas']>=4
    rows=[e for e in calls.log.read() if e['label']=='MODEL' and e['stage']=='extract_paper']
    assert len(rows)==result['distinct_schemas']
    started=next(json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='schema_preflight_started')
    from ara.runtime.cache import canonical, digest
    assert [w['schema_id'] for w in started['wires']]==[json.loads(e['payload_json'])['cli']['wire_schema_hash'] for e in rows]
    assert all(w['schema_id']==digest(canonical(w['wire'])) for w in started['wires'])
    assert all(json.loads(e['payload_json'])['status']=='accepted' for e in rows)


def test_native_multirange_and_reconciliation(codex):
    config,auth,write,tmp=codex
    config.update(extract_paper_max_output_tokens=1000,extraction_planned_output_tokens_per_page=1000,
                  token_cap=2000000)
    write('extract:ok');calls=make_calls(config,EventLog(tmp/'events.jsonl'),'P')
    paper=Paper('p','{}','P',(PageText(1,'P Q R F(x)'),PageText(2,'P Q R F(x)')))
    result=calls.extract_paper(paper)
    assert len(result.items)==16 and {i.page_start for i in result.items}=={1,2}
    rows=[e for e in calls.log.read() if e['label']=='MODEL' and e['stage']=='extract_paper']
    requests=[json.loads(e['prompt'].split('INPUT_JSON\n')[1]) for e in rows]
    initial=[r for r in requests if r.get('mode')!='reconcile_ranges']
    assert [p for r in initial for p in r['pages']]==[{'page':p.page,'text':p.text} for p in paper.pages]
    assert len(requests)==3 and requests[-1]['mode']=='reconcile_ranges'
    assert len(requests[-1]['ranges'][0]['items'])==16
    assert all(json.loads(e['payload_json'])['status']=='accepted' for e in rows)


def test_extraction_single_page_overflow_refuses_before_dispatch(codex):
    from ara.runtime.budget import BudgetStop
    config,auth,write,tmp=codex
    calls=make_calls(config,EventLog(tmp/'events.jsonl'),'P')
    config['model_context_token_bound']=1
    paper=Paper('p','{}','P',(PageText(1,'P Q R F(x)'),))
    with pytest.raises(BudgetStop,match='single page cannot fit'):calls.extract_paper(paper)
    assert not any(e['stage']=='extract_paper' and e['label']=='MODEL' for e in calls.log.read())


def test_codex_extraction_reuse_identity_pins_projection(codex):
    from ara.runtime.extraction import extraction_acceptance_identity
    from ara.runtime.codex_schema import VERSION
    config,*_=codex
    assert extraction_acceptance_identity(config,ROOT)['schema_transform']==VERSION
    assert 'schema_transform' not in extraction_acceptance_identity({**config,'provider':'mock'},ROOT)


def test_codex_accepted_ranges_can_be_salvaged_offline(codex):
    from ara.runtime.extraction import extract
    from ara.runtime.salvage import accepted_ranges
    config,auth,write,tmp=codex
    config.update(token_cap=2000000,extraction_targeted_corrections=1)
    write('extract:correction');calls=make_calls(config,EventLog(tmp/'events.jsonl'),'P')
    paper=Paper('p','{"id":"p"}','P',(PageText(1,'P Q R F(x)'),))
    extract(calls,(paper,))
    replay=EventLog(tmp/'replay/events.jsonl')
    result=accepted_ranges(calls.log.read(),(paper,),config,ROOT,replay)
    assert len(result['p'])==1 and len(result['p'][0]['result'].items)==8
    assert not any(e['label']=='MODEL' for e in replay.read())


@pytest.mark.parametrize('failed_patch', [False, True])
def test_codex_duplicate_initial_wire_recovers_and_replays(codex, failed_patch):
    from ara.runtime.extraction import extract
    from ara.runtime.salvage import accepted_ranges
    config,auth,write,tmp=codex
    config.update(token_cap=2000000)
    write('extract:duplicate:retry' if failed_patch else 'extract:duplicate')
    calls=make_calls(config,EventLog(tmp/'events.jsonl'),'P')
    paper=Paper('p','{"id":"p"}','P',(PageText(1,'P Q R F(x)'),))
    extract(calls,(paper,))
    rows=[e for e in calls.log.read() if e['label']=='MODEL' and e['stage']=='extract_paper']
    assert [json.loads(e['payload_json'])['status'] for e in rows]==['rejected']*(2 if failed_patch else 1)+['accepted']
    request=json.loads(rows[1]['prompt'].split('INPUT_JSON\n')[1])
    assert request['required_reference_updates']==['i']
    assert len(request['candidate']['items'])==9
    replay=EventLog(tmp/'replay/events.jsonl')
    result=accepted_ranges(calls.log.read(),(paper,),config,ROOT,replay)
    assert len(result['p'][0]['result'].items)==9
    assert not any(e['label']=='MODEL' for e in replay.read())
