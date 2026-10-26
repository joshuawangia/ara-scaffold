"""Strict wire projection must not weaken native schema acceptance."""
import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[2]


def test_optional_null_roundtrip_and_local_constraints():
    from ara.runtime.codex_schema import strict_schema, normalize_output, VERSION
    local = {'type':'object','properties':{
        'id':{'type':'string','minLength':1},
        'rows':{'type':'array','items':{'$ref':'#/$defs/row'},'uniqueItems':True},
        'note':{'type':'string'},'nullable':{'type':['string','null']}},
        'required':['id','rows'],'additionalProperties':False,
        '$defs':{'row':{'type':'object','properties':{'p':{'const':'P'},'q':{'type':'string'}},'required':['p'],'additionalProperties':False}}}
    before=copy.deepcopy(local);wire=strict_schema(local)
    assert local==before and wire==strict_schema(local) and VERSION
    assert set(wire['required'])==set(local['properties'])
    assert 'uniqueItems' not in wire['properties']['rows']
    data={'id':'P','rows':[{'p':'P','q':None}],'note':None,'nullable':None}
    Draft202012Validator(wire).validate(data)
    restored=normalize_output(local,data)
    assert restored=={'id':'P','rows':[{'p':'P'}],'nullable':None}
    assert data['rows'][0]['q'] is None
    Draft202012Validator(local).validate(restored)
    for broken in ({**data,'id':''},{**data,'rows':data['rows']*2},{**data,'id':None}):
        with pytest.raises(ValidationError):Draft202012Validator(local).validate(normalize_output(local,broken))


def test_all_native_schemas_recursive_and_closed():
    from ara.runtime.codex_schema import strict_schema, placeholder, wire_value, normalize_output
    for path in sorted((ROOT/'schemas').glob('*.json')):
        if path.stem in ('formula','extract_paper'):continue
        local=json.loads(path.read_text());wire=strict_schema(local)
        Draft202012Validator.check_schema(wire)
        def check(node):
            if isinstance(node,dict):
                assert not set(node)&{'uniqueItems','minLength','maxLength','minItems','maxItems','pattern','format','oneOf','const','allOf','if','then','else','not','minimum'}
                if node.get('type')=='object':
                    assert node['additionalProperties'] is False
                    assert set(node['required'])==set(node['properties'])
                for key,value in node.items():
                    if key in ('properties','$defs'):
                        for child in value.values():check(child)
                    elif key not in ('enum','required'):check(value)
            elif isinstance(node,list):
                for child in node:check(child)
        check(wire)
        sample=placeholder(local);Draft202012Validator(local).validate(sample)
        encoded=wire_value(local,sample);Draft202012Validator(wire).validate(encoded)
        restored=normalize_output(local,encoded)
        Draft202012Validator(local).validate(restored)
        assert wire_value(local,restored)==encoded


def test_recursive_union_nulls_and_required_nulls_preserved():
    from ara.runtime.codex_schema import strict_schema, normalize_output
    local={'type':'object','properties':{'node':{'$ref':'#/$defs/node'}},'required':['node'],
      '$defs':{'node':{'oneOf':[
        {'type':'object','properties':{'tag':{'const':'P'},'leaf':{'type':['string','null']},'optional':{'type':'string'}},'required':['tag','leaf']},
        {'type':'object','properties':{'tag':{'const':'Q'},'child':{'$ref':'#/$defs/node'}},'required':['tag','child']}]}}}
    value={'node':{'tag':'Q','child':{'tag':'P','leaf':None,'optional':None}}}
    Draft202012Validator(strict_schema(local)).validate(value)
    assert normalize_output(local,value)=={'node':{'tag':'Q','child':{'tag':'P','leaf':None}}}


def test_unknown_properties_and_local_conditions_are_not_discarded():
    from ara.runtime.codex_schema import normalize_output
    local={'type':'object','properties':{'p':{'type':'string'}},'required':['p'],'additionalProperties':False,
           'not':{'properties':{'p':{'const':'Q'}}}}
    for value in ({'p':'P','extra':None},{'p':'Q'}):
        with pytest.raises(ValidationError):Draft202012Validator(local).validate(normalize_output(local,value))


def test_preflight_manifest_routes_and_schema_changes(tmp_path):
    import yaml
    import shutil
    from ara.runtime.codex_preflight import manifest
    config=yaml.safe_load((ROOT/'config.yaml').read_text())
    config.update(provider='mock',stages={'construction_correction':{
        'provider':'codex_cli','model':'gpt-6-luna','effort':'low'}})
    expected=manifest(config,ROOT)
    assert {c['case'] for c in expected['cases']}=={'select_t_roots_correction','build_t_batch_correction'}
    assert all(c['effort']=='low' and c['model']=='gpt-6-luna' for c in expected['cases'])
    shutil.copytree(ROOT/'schemas',tmp_path/'schemas')
    path=tmp_path/'schemas/select_t_roots.json';schema=json.loads(path.read_text())
    # A local-only constraint change still invalidates proof, even with identical wire.
    schema['properties']['roots']['maxItems']=2;path.write_text(json.dumps(schema))
    changed=manifest(config,tmp_path)
    before=next(c for c in expected['cases'] if c['kind']=='select_t_roots')
    after=next(c for c in changed['cases'] if c['kind']=='select_t_roots')
    assert before['wire_schema_hash']==after['wire_schema_hash']
    assert before['native_schema_hash']!=after['native_schema_hash']
