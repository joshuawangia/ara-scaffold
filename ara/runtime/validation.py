"""Bounded native-schema validation; disjoint tags avoid recursive branch search."""
from __future__ import annotations

import json
import math
import subprocess
import sys
import time

from jsonschema import Draft202012Validator, ValidationError, validators

DEFAULTS = {'local_validation_max_depth': 64, 'local_validation_max_nodes': 100000,
            'local_validation_timeout_seconds': 2.0}


def tagged_branches(branches):
    """A required, unique string tag proves that at most one branch can match."""
    result = {}
    for index, branch in enumerate(branches):
        if not isinstance(branch, dict) or branch.get('type') != 'object' or 'op' not in branch.get('required', []):
            return None
        tag = branch.get('properties', {}).get('op', {})
        value = tag.get('const')
        if value is None and len(tag.get('enum', [])) == 1:
            value = tag['enum'][0]
        if not isinstance(value, str) or value in result:
            return None
        result[value] = (index, branch)
    return result or None


def _tagged(keyword):
    original = Draft202012Validator.VALIDATORS[keyword]
    def validate(validator, branches, instance, schema):
        choices = tagged_branches(branches)
        if choices is None:
            yield from original(validator, branches, instance, schema)
        elif not isinstance(instance, dict) or not isinstance(instance.get('op'), str) or instance['op'] not in choices:
            yield ValidationError('expected an object with a recognized op tag')
        else:
            index, branch = choices[instance['op']]
            yield from validator.descend(instance, branch, schema_path=index)
    return validate


LinearValidator = validators.extend(Draft202012Validator,
                                    {'oneOf': _tagged('oneOf'), 'anyOf': _tagged('anyOf')})


def _limits(config):
    result = {key: (config or {}).get(key, default) for key, default in DEFAULTS.items()}
    for key, value in result.items():
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            raise ValueError(f'{key} must be finite and positive')
        if key != 'local_validation_timeout_seconds' and type(value) is not int:
            raise ValueError(f'{key} must be an integer')
    return result


def _reject(message, path=(), validator='structure'):
    raise ValidationError(message, path=path, validator=validator)


def guard_complexity(value, config=None, *, deadline=None):
    limits = _limits(config)
    deadline = deadline if deadline is not None else time.monotonic() + limits['local_validation_timeout_seconds']
    stack, count = [(value, 0)], 0
    while stack:
        item, depth = stack.pop()
        count += 1
        if count > limits['local_validation_max_nodes']:
            _reject('local_validation_max_nodes exceeded', validator='local_validation_max_nodes')
        if depth > limits['local_validation_max_depth']:
            _reject('local_validation_max_depth exceeded', validator='local_validation_max_depth')
        if time.monotonic() >= deadline:
            _reject('local_validation_timeout_seconds exceeded', validator='local_validation_timeout_seconds')
        if isinstance(item, (dict, list)):
            children = item.values() if isinstance(item, dict) else item
            if count + len(stack) + len(item) > limits['local_validation_max_nodes']:
                _reject('local_validation_max_nodes exceeded', validator='local_validation_max_nodes')
            stack.extend((child, depth + 1) for child in children)
    return limits


def _fields(value, schema, path):
    """Cheap structural constraints only; the entire native schema still follows."""
    kind = schema.get('type')
    if kind is not None and not Draft202012Validator.TYPE_CHECKER.is_type(value, kind):
        _reject(f'expected {kind}', path, 'type')
    if 'const' in schema and value != schema['const']:
        _reject('unexpected symbol/node kind', path, 'const')
    if 'enum' in schema and value not in schema['enum']:
        _reject('unknown symbol/node kind', path, 'enum')
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                _reject(f'missing required field {key}', path, 'required')
        if schema.get('additionalProperties') is False and value.keys() - schema.get('properties', {}).keys():
            _reject('unexpected formula or symbol field', path, 'additionalProperties')
        for key, child in schema.get('properties', {}).items():
            if key in value:
                _fields(value[key], child, (*path, key))
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            _reject(f'minItems: expected at least {schema["minItems"]} arguments', path, 'minItems')
        if 'maxItems' in schema and len(value) > schema['maxItems']:
            _reject(f'maxItems: expected at most {schema["maxItems"]} arguments', path, 'maxItems')
    if isinstance(value, str) and len(value) < schema.get('minLength', 0):
        _reject('empty symbol reference', path, 'minLength')


def precheck(schema, value, config=None, *, deadline=None):
    limits = guard_complexity(value, config, deadline=deadline)
    deadline = deadline if deadline is not None else time.monotonic() + limits['local_validation_timeout_seconds']
    definitions = schema.get('$defs', {})
    formula = definitions.get('formula')
    choices = tagged_branches(formula.get('oneOf', [])) if isinstance(formula, dict) else None
    stack = [(schema, value, ())]
    while stack:
        node, item, path = stack.pop()
        if time.monotonic() >= deadline:
            _reject('local_validation_timeout_seconds exceeded', path, 'local_validation_timeout_seconds')
        if not isinstance(node, dict):
            continue
        reference = node.get('$ref')
        if reference:
            if reference.startswith('#/$defs/') and reference[8:] in definitions:
                node = definitions[reference[8:]]
            else:
                continue  # Native resolver remains authoritative inside the timed child.
        if node is formula and choices:
            if not isinstance(item, dict) or not isinstance(item.get('op'), str) or item['op'] not in choices:
                _reject('expected an object with a recognized op tag', path, 'op')
            branch = choices[item['op']][1]
            _fields(item, branch, path)
            for i, child in enumerate(item.get('args', [])):
                stack.append((formula, child, (*path, 'args', i)))
            for i, term in enumerate(item.get('terms', [])):
                _fields(term, definitions['term'], (*path, 'terms', i))
            continue
        if isinstance(item, dict):
            for key, child in node.get('properties', {}).items():
                if key in item:
                    stack.append((child, item[key], (*path, key)))
        if isinstance(item, list) and 'items' in node:
            stack.extend((node['items'], child, (*path, i)) for i, child in enumerate(item))
        # The native nullable formula union: null has no AST to inspect.
        branches = node.get('anyOf', [])
        if item is not None and branches == [{'$ref': '#/$defs/formula'}, {'type': 'null'}]:
            stack.append((formula, item, path))
    return limits


def _bounded(operation, schema, value, config=None):
    limits = _limits(config)
    deadline = time.monotonic() + limits['local_validation_timeout_seconds']
    if operation == 'validate':
        precheck(schema, value, limits, deadline=deadline)
    else:
        guard_complexity(value, limits, deadline=deadline)
    request = json.dumps({'operation': operation, 'schema': schema, 'value': value})
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        _reject('local_validation_timeout_seconds exceeded', validator='local_validation_timeout_seconds')
    # A separate interpreter is safe from search threads and can be killed even
    # inside a single pathological regex/jsonschema keyword. No thread is abandoned.
    process = subprocess.Popen([sys.executable, '-m', 'ara.runtime.validation'],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        output, _ = process.communicate(request, timeout=max(.001, deadline - time.monotonic()))
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        _reject('local_validation_timeout_seconds exceeded', validator='local_validation_timeout_seconds')
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate()
    if process.returncode != 0:
        _reject('local validation worker failed', validator='local_validation_worker')
    result = json.loads(output)
    if not result['ok']:
        _reject(result['message'], result['path'], result['validator'])
    return result.get('value')


def decode_response(text):
    try:
        return json.loads(text)
    except RecursionError:
        _reject('local_validation_max_depth exceeded during JSON decoding', validator='local_validation_max_depth')


def validate_local(schema, value, config=None):
    _bounded('validate', schema, value, config)


def normalize_local(schema, value, config=None):
    return _bounded('normalize', schema, value, config)


def encode_local(schema, value):
    return _bounded('encode', schema, value)


def _main():
    request = json.load(sys.stdin)
    try:
        if request['operation'] in ('normalize', 'encode'):
            from ara.runtime.codex_schema import _map_value
            value = _map_value(request['schema'], request['value'], encode=request['operation'] == 'encode')
        else:
            LinearValidator(request['schema']).validate(request['value'])
            value = None
        result = {'ok': True, 'value': value}
    except ValidationError as exc:
        result = {'ok': False, 'message': exc.message[:1000],
                  'path': list(exc.absolute_path), 'validator': exc.validator}
    print(json.dumps(result))


if __name__ == '__main__':
    _main()
