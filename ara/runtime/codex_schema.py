"""Versioned OpenAI-strict wire projection; native Draft 2020-12 stays authoritative."""
from copy import deepcopy

from ara.runtime.validation import LinearValidator, normalize_local, encode_local, validate_local, tagged_branches

VERSION = 'ara-openai-strict-v2'
# Constraints outside this vocabulary remain in the native schema and prompt.
WIRE_KEYS = frozenset(('type', 'enum', 'description', '$ref'))


def strict_schema(schema):
    def project(node):
        if not isinstance(node, dict):
            raise ValueError('Codex schema must use explicit typed schemas')
        result = {k:deepcopy(v) for k,v in node.items() if k in WIRE_KEYS}
        if '$ref' in result and not result['$ref'].startswith('#/'):
            raise ValueError('Codex schema references must be local')
        if 'const' in node:
            value = node['const']
            result['enum'] = [value]
            result.setdefault('type', ('null' if value is None else 'boolean' if isinstance(value,bool)
                                      else 'string' if isinstance(value,str) else 'number'))
        for key in ('$defs', 'properties'):
            if key in node:
                result[key] = {name:project(child) for name,child in node[key].items()}
        alternatives = node.get('oneOf', node.get('anyOf'))
        # Object-level alternatives refine the native fields; retaining them as
        # partial wire objects is invalid strict schema. Keep these rules local.
        if alternatives is not None and 'properties' not in node:
            result['anyOf'] = [project(child) for child in alternatives]
        if node.get('type') == 'object' or 'properties' in node:
            result['type'] = 'object'
            properties = result.setdefault('properties', {})
            required = set(node.get('required', []))
            for name, child in list(properties.items()):
                if name not in required:
                    properties[name] = {'anyOf':[child, {'type':'null'}]}
            result['required'] = list(properties)
            result['additionalProperties'] = False
        if node.get('type') == 'array':
            # Native maxItems=0 means the only valid local value is []. The wire
            # still requires items; any generated null item fails native maxItems.
            result['items'] = project(node['items']) if 'items' in node else {'type':'null'}
        return result
    return project(schema)


def _resolve(schema, root):
    while '$ref' in schema:
        pointer = schema['$ref']
        if not pointer.startswith('#/'):
            raise ValueError('Codex schema references must be local')
        schema = root
        for part in pointer[2:].split('/'):
            schema = schema[part.replace('~1','/').replace('~0','~')]
    return schema


def _map_value(schema, value, *, encode):
    root = schema
    local_validator = LinearValidator(root)
    wire_validator = LinearValidator(strict_schema(root))
    def visit(node, item, tagged_valid=False):
        node = _resolve(node, root)
        branches = node.get('oneOf', node.get('anyOf'))
        if branches and 'properties' not in node:
            choices = tagged_branches(branches)
            if choices:
                selected = choices.get(item.get('op')) if isinstance(item, dict) and isinstance(item.get('op'), str) else None
                if selected is None:
                    return deepcopy(item)
                branch = selected[1]
                validator = local_validator if encode else wire_validator
                if tagged_valid or validator.evolve(schema=branch if encode else strict_schema(branch)).is_valid(item):
                    return visit(branch, item, tagged_valid=True)
                return deepcopy(item)
            validator = local_validator if encode else wire_validator
            for branch in branches:
                candidate = branch if encode else strict_schema(branch)
                if validator.evolve(schema=candidate).is_valid(item):
                    return visit(branch, item)
            # Preserve malformed data for authoritative local rejection.
            return deepcopy(item)
        if isinstance(item, dict) and (node.get('type')=='object' or 'properties' in node):
            result = {name:deepcopy(child) for name,child in item.items() if name not in node.get('properties', {})}
            required = set(node.get('required', []))
            for name, child in node.get('properties', {}).items():
                if name not in item:
                    if encode and name not in required:
                        result[name] = None
                    continue
                if (not encode and item[name] is None and name not in required
                        and not local_validator.evolve(schema=child).is_valid(None)):
                    continue
                else:
                    result[name] = visit(child, item[name], tagged_valid)
            return result
        if isinstance(item, list) and 'items' in node:
            return [visit(node['items'], child, tagged_valid) for child in item]
        return deepcopy(item)
    return visit(schema, value)


def normalize_output(schema, value, config=None):
    """Remove only wire-added null sentinels; preserve native nulls and bad fields."""
    return normalize_local(schema, value, config)


def wire_value(schema, value):
    """Represent optional omissions as null for deterministic preflight examples."""
    return encode_local(schema, value)


def placeholder(schema):
    """Small placeholder-only witness for native stage schemas, checked locally."""
    def sample(node):
        node = _resolve(node, schema)
        if 'const' in node:
            return node['const']
        if 'enum' in node:
            return node['enum'][0]
        branches = node.get('oneOf', node.get('anyOf'))
        if branches and 'properties' not in node:
            return sample(branches[0])
        kind = node.get('type')
        if isinstance(kind,list):
            kind = 'null' if 'null' in kind else kind[0]
        if kind == 'object':
            return {name:sample(node['properties'][name]) for name in node.get('required',[])}
        if kind == 'array':
            return [sample(node['items']) for _ in range(node.get('minItems',0))]
        if kind == 'string':
            return 'P' * max(1,node.get('minLength',1))
        if kind in ('integer','number'):
            return max(0,node.get('minimum',0))
        if kind == 'boolean':
            return False
        if kind == 'null':
            return None
        raise ValueError('No placeholder for untyped Codex schema')
    value = sample(schema)
    # The extraction initial envelope requires a disposition for empty items.
    if schema.get('title') == 'extract_paper_v2' and 'empty_reason' in schema.get('properties', {}):
        value['empty_reason'] = 'P'
    validate_local(schema, value)
    return value
