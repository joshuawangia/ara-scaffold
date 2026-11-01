"""Complete positional catalogue coverage and append-only definition corrections."""
from copy import deepcopy
import json
import re
from jsonschema import ValidationError

from ara.runtime.calls import require
from ara.runtime.cache import canonical
from ara.runtime.validation import validate_local

V2='shared-predicate-formalization-v2'
# Glosses describe relations. Bare relation verbs are not attribution evidence.
# Preserve the exact named report-frame boundary, including formatted text.
_REPORT_FRAME=re.compile(r"\b(?:[A-Z][\w’'-]*|[ab])(?:\s+[A-Z][\w’'-]*){0,3}\s+"
    r"(?i:argues?|claims?|holds?|maintains?|states?|reports?|asserts?|believes?|says?|thinks?|contends?|suggests?|proposes?|defends?|endorses?)"
    r"(?:[^\w.!?。！？]|_)+(?i:that)(?=[\W_]|$)")


def catalogue_definition(text):
    from ara.runtime.commitment_provenance import _definition_screen_text
    if not isinstance(text,str) or not text.strip():return False
    view=_definition_screen_text(text)
    return view is not None and bool(view.strip()) and not _REPORT_FRAME.search(view)


def preserved_entries(data):
    """Protect individually valid entries even if another entry/field was rejected."""
    from ara.runtime.shared_predicates import ROOT
    schema=json.loads((ROOT/'schemas/predicate_catalogue.json').read_text())
    result=dict(sorts=[],predicates=[])
    if not isinstance(data,dict):return result
    for field in result:
        values=data.get(field,[])
        if not isinstance(values,list):continue
        for row in values:
            try:
                validate_local(schema['properties'][field]['items'],row)
                require(catalogue_definition(row['gloss']),'invalid definition')
                if field=='sorts':
                    require(row['name'] not in {s['name'] for s in result['sorts']},'duplicate sort')
                else:
                    names={s['name'] for s in result['sorts']}
                    require(all(r['sort'] in names for r in row['roles']),'unknown role sort')
                    require(len({r['role'] for r in row['roles']})==len(row['roles']),'duplicate role')
                    require(catalogue_definition(row['gloss']+' [roles: '+', '.join(r['role']+':'+r['sort'] for r in row['roles'])+']'),'invalid role definition')
                if row not in result[field]:result[field].append(deepcopy(row))
            except (ValueError,ValidationError):continue
    return result


def merge_preserved(prior,data):
    result=deepcopy(prior or dict(sorts=[],predicates=[]))
    fresh=preserved_entries(data)
    for field in result:
        for row in fresh[field]:
            if row not in result[field]:result[field].append(row)
    return result


def check_preserved(data,preserved):
    for field,values in (preserved or {}).items():
        require(all(row in data.get(field,[]) for row in values),
                'catalogue correction must preserve valid entries: '+canonical(preserved))


def check_extension(data,prior):
    check_preserved(data,prior)
    for field in ('sorts','predicates'):
        require(data[field][:len(prior[field])]==prior[field],
                'catalogue extension must preserve published order and handles')


def coverage(data,entries,count):
    from ara.runtime.shared_predicates import schema_check
    schema_check('predicate_coverage',data)
    require(len(data['coverage'])==count,'coverage slot count mismatch')
    handles={e['handle'] for e in entries if e['kind']=='relation'}
    for index,row in enumerate(data['coverage']):
        require(bool(row['reason'].strip()),f'coverage slot {index} requires a reason')
        require(set(row['handles'])<=handles and len(row['handles'])==len(set(row['handles'])),
                f'coverage slot {index} has unknown or duplicate content handles')
        require(row['covered']==(bool(row['handles']) and not row['missing']),
                f'coverage slot {index} has inconsistent missing components')
    return deepcopy(data)


def catalogue_inputs(base,history,checks):
    if not history:return {**base,'policy_version':V2}
    return {**base,'policy_version':V2,'mode':'coverage_patch','revision':len(history),
            'preserve_catalogue':history[-1],'coverage_feedback':checks[-1]}


def coverage_inputs(base,data,revision):
    from ara.runtime.shared_predicates import catalogue
    return dict(lifecycle_key=base['lifecycle_key'],policy_version=V2,sources=base['sources'],
                catalogue=catalogue(data,version=V2),revision=revision)


def prepare(calls,base):
    from ara.runtime.shared_predicates import catalogue
    history=[];checks=[]
    for revision in range(3):
        inputs=catalogue_inputs(base,history,checks)
        def validate(data):
            entries=catalogue(data,version=V2)
            if history:check_extension(data,history[-1])
            return entries,deepcopy(data)
        entries,data=calls.call('predicate_catalogue',inputs,validate)
        history.append(data)
        cov_inputs=coverage_inputs(base,data,revision)
        checked=calls.call('predicate_coverage',cov_inputs,
                           lambda d:coverage(d,entries,len(base['sources'])))
        checks.append(checked)
        calls.log.record('shared_predicate_coverage',revision=revision,catalogue=data,coverage=checked,
                         note='Model coverage judgment for every selected sentence; not independent semantic certification.')
        if all(row['covered'] for row in checked['coverage']):return entries,data,history,checks
    raise ValueError('catalogue coverage incomplete after bounded extensions')


def replay(history,checks,count):
    from ara.runtime.shared_predicates import catalogue
    require(1<=len(history)<=3 and len(history)==len(checks),'invalid catalogue coverage history')
    for index,(data,check) in enumerate(zip(history,checks,strict=True)):
        entries=catalogue(data,version=V2)
        coverage(check,entries,count)
        if index:
            check_extension(data,history[index-1])
            require(not all(r['covered'] for r in checks[index-1]['coverage']),'unnecessary catalogue revision')
    require(all(r['covered'] for r in checks[-1]['coverage']),'catalogue coverage incomplete')


def response_schema(kind,schema,inputs):
    """One effective grammar for native calls and live schema preflight."""
    if kind=='predicate_formalize' and inputs.get('policy_version')==V2:
        schema['properties']['mode']={'enum':['decompose']}
        schema['properties']['formula']={'$ref':'#/$defs/formula'}
    if kind=='predicate_coverage' and inputs.get('sources'):
        schema['properties']['coverage'].update(minItems=len(inputs['sources']),maxItems=len(inputs['sources']))
    if kind=='predicate_formalize' and inputs.get('catalogue'):
        branch=next(b for b in schema['$defs']['formula']['oneOf'] if b['properties']['op'].get('const')=='predicate')
        branch['properties']['name']={'type':'string','enum':[e['handle'] for e in inputs['catalogue']]}
    return schema
