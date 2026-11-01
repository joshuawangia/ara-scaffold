"""Authenticate admitted decompositions against the native model event history."""
import json

from ara.runtime.cache import canonical,digest
from ara.runtime.calls import require
from ara.runtime.providers import Response
from ara.runtime.validation import normalize_local
from ara.runtime.shared_predicates import ROOT,VERSION


def request_identity(receipt):
    return digest(canonical(dict(original=receipt['original_commitments'],symbols=receipt['original_symbols'],
        rows=receipt['provenance'],evidence=receipt['evidence'],policy=receipt['policy'])))


def verify_model_receipts(events,receipt):
    if receipt is None or receipt.get('schema_version')!=VERSION:return
    identity=request_identity(receipt);entries=receipt['catalogue'];original=receipt['original_commitments']['commitments']
    expected={}
    def add(kind,inputs,value):expected[(kind,canonical(inputs))]=value
    cat_input=dict(lifecycle_key=identity,sources=[dict(text=c['text'],source_id=receipt['provenance'][c['id']]['source_id'],
        stance=receipt['provenance'][c['id']]['stance'],evidence=receipt['evidence'][c['id']]) for c in original],policy=receipt['policy'])
    add('predicate_catalogue',cat_input,receipt['catalogue_response'])
    admitted_keys=set()
    for c,item in zip(original,receipt['items'],strict=True):
        inputs=dict(lifecycle_key=identity,source=c['text'],evidence=receipt['evidence'][c['id']],
                    stance=receipt['provenance'][c['id']]['stance'],catalogue=entries,item_key=digest(c['id']))
        if item['candidate'] is not None:add('predicate_formalize',inputs,item['candidate'])
        if item['translation'] is not None:
            back=dict(lifecycle_key=identity,item_key=digest(c['id']),formula=item['candidate']['formula'],catalogue=entries)
            add('predicate_backtranslate',back,item['translation'])
        if item['judgments']:
            judge=dict(**inputs,formula=item['candidate']['formula'],back_translation=item['translation']['text'])
            for index,value in enumerate(item['judgments']):add('predicate_fidelity',{**judge,'sample_index':index},value)
        if item['status']=='admitted':admitted_keys.add(digest(c['id']))
    found=set()
    for event in events:
        if event['label']!='MODEL' or not event['stage'].startswith('predicate_'):continue
        payload=json.loads(event['payload_json'])
        if payload.get('status')!='accepted':continue
        inputs=json.loads(event['prompt'].split('\nINPUT_JSON\n',1)[1]);inputs.pop('topic',None)
        inputs.pop('validation_feedback',None);inputs.pop('validation_history',None)
        key=(event['stage'],canonical(inputs))
        if key not in expected:
            # An admitted item cannot discard earlier accepted dissent or another
            # candidate/translation. Unresolved partial judges remain in the log.
            require(inputs.get('item_key') not in admitted_keys and event['stage']!='predicate_catalogue',
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
    if not receipt or receipt.get('schema_version')!=VERSION:return
    from ara.runtime.predicate_fork import validate_selected_origin
    validate_selected_origin(events,provenance)
    verify_model_receipts(events,receipt)
