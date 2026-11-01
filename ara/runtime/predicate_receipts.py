"""Authenticate admitted decompositions against the native model event history."""
import json

from ara.runtime.cache import canonical,digest
from ara.runtime.calls import require
from ara.runtime.providers import Response
from ara.runtime.validation import normalize_local
from ara.runtime.shared_predicates import ROOT,VERSIONS
from ara.runtime.predicate_coverage import V2


def model_inputs(event):
    inputs=json.loads(event['prompt'].split('\nINPUT_JSON\n',1)[1])
    for field in ('topic','validation_feedback','validation_history'):inputs.pop(field,None)
    return inputs


def adverse_fields(event):
    try:
        raw=json.loads(Response(json.loads(event['response'])).text())
    except (ValueError,TypeError,KeyError):
        return []
    if not isinstance(raw,dict):return []
    return [field for field in ('equivalent','preserves_scope','no_additions') if raw.get(field) is False]


def fidelity_adverse_history(events,inputs):
    expected={canonical({**inputs,'sample_index':i}) for i in range(3)}
    return any(e['label']=='MODEL' and e['stage']=='predicate_fidelity' and
               canonical(model_inputs(e)) in expected and adverse_fields(e) for e in events)


def request_identity(receipt):
    return digest(canonical(dict(original=receipt['original_commitments'],symbols=receipt['original_symbols'],
        rows=receipt['provenance'],evidence=receipt['evidence'],policy=receipt['policy'])))


def verify_model_receipts(events,receipt):
    if receipt is None or receipt.get('schema_version') not in VERSIONS:return
    identity=request_identity(receipt);entries=receipt['catalogue'];original=receipt['original_commitments']['commitments']
    expected={}
    def add(kind,inputs,value):expected[(kind,canonical(inputs))]=value
    cat_input=dict(lifecycle_key=identity,sources=[dict(text=c['text'],source_id=receipt['provenance'][c['id']]['source_id'],
        stance=receipt['provenance'][c['id']]['stance'],evidence=receipt['evidence'][c['id']]) for c in original],policy=receipt['policy'])
    if receipt['schema_version']==V2:
        from ara.runtime.predicate_coverage import catalogue_inputs,coverage_inputs
        for index,(data,check) in enumerate(zip(receipt['catalogue_history'],receipt['coverage_history'],strict=True)):
            add('predicate_catalogue',catalogue_inputs(cat_input,receipt['catalogue_history'][:index],receipt['coverage_history'][:index]),data)
            add('predicate_coverage',coverage_inputs(cat_input,data,index),check)
    else:add('predicate_catalogue',cat_input,receipt['catalogue_response'])
    admitted_keys=set()
    for c,item in zip(original,receipt['items'],strict=True):
        inputs=dict(lifecycle_key=identity,source=c['text'],evidence=receipt['evidence'][c['id']],
                    stance=receipt['provenance'][c['id']]['stance'],catalogue=entries,item_key=digest(c['id']))
        if receipt['schema_version']==V2:inputs['policy_version']=V2
        if item['candidate'] is not None:add('predicate_formalize',inputs,item['candidate'])
        if item['translation'] is not None:
            back=dict(lifecycle_key=identity,item_key=digest(c['id']),formula=item['candidate']['formula'],catalogue=entries)
            add('predicate_backtranslate',back,item['translation'])
        if item['judgments']:
            judge=dict(**inputs,formula=item['candidate']['formula'],back_translation=item['translation']['text'])
            for index,value in enumerate(item['judgments']):add('predicate_fidelity',{**judge,'sample_index':index},value)
            if receipt['schema_version']==V2 and item['reason']=='adverse_fidelity_history':
                require(fidelity_adverse_history(events,judge),'unresolved history lacks adverse judgment')
        if item['status']=='admitted':admitted_keys.add(digest(c['id']))
    found=set();protected={}
    for event in events:
        if event['label']!='MODEL' or not event['stage'].startswith('predicate_'):continue
        payload=json.loads(event['payload_json'])
        inputs=model_inputs(event)
        key=(event['stage'],canonical(inputs))
        if event['stage']=='predicate_fidelity' and key in expected and inputs.get('item_key') in admitted_keys:
            require(not adverse_fields(event),'adverse fidelity history forbids admission')
        if receipt['schema_version']==V2 and event['stage']=='predicate_catalogue':
            from ara.runtime.predicate_coverage import merge_preserved,check_preserved
            try:raw=json.loads(Response(json.loads(event['response'])).text())
            except (ValueError,TypeError,KeyError):raw=None
            if payload.get('status')=='accepted':check_preserved(raw,protected.get(key))
            protected[key]=merge_preserved(protected.get(key),raw)
        if payload.get('status')!='accepted':continue
        if key not in expected:
            # An admitted item cannot discard earlier accepted dissent or another
            # candidate/translation. Unresolved partial judges remain in the log.
            require(inputs.get('item_key') not in admitted_keys and event['stage'] not in ('predicate_catalogue','predicate_coverage'),
                    'unbound prior predicate response or fidelity dissent')
            continue
        require(key not in found,'duplicate predicate model receipt')
        schema=json.loads((ROOT/f"schemas/{event['stage']}.json").read_text())
        raw=json.loads(Response(json.loads(event['response'])).text())
        normalized=normalize_local(schema,raw)
        require(normalized==expected[key],'predicate model response/receipt mismatch')
        found.add(key)
    require(found==set(expected),'missing authenticated predicate model response')


def verify_runtime(events,provenance):
    receipt=provenance.get('consolidation') if provenance else None
    if not receipt or receipt.get('schema_version') not in VERSIONS:return
    from ara.runtime.predicate_fork import validate_selected_origin
    validate_selected_origin(events,provenance)
    verify_model_receipts(events,receipt)
