"""Stateless transports. Credentials never enter requests, cache keys, or events."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from ara.runtime.cache import canonical, digest
from ara.types import TokenUsage


class MissingResponse(RuntimeError):
    pass


@dataclass(frozen=True)
class Response:
    raw: dict

    @staticmethod
    def usage_fields(usage: dict) -> TokenUsage:
        tool = usage.get('server_tool_use') or {}
        return TokenUsage(usage.get('input_tokens', 0), usage.get('output_tokens', 0),
                          usage.get('cache_read_input_tokens') or 0,
                          usage.get('cache_creation_input_tokens') or 0,
                          tool.get('web_search_requests', 0))

    @property
    def usage(self) -> TokenUsage:
        usage = self.raw['usage']
        iterations = usage.get('iterations') or []
        if not iterations:
            return self.usage_fields(usage)
        if any(i['type'] not in ('message', 'fallback_message') for i in iterations):
            raise ValueError('unsupported provider usage iteration')
        parts = [self.usage_fields(i) for i in iterations]
        totals = {key: sum(p.to_dict()[key] for p in parts)
                  for key in ('input_tokens', 'output_tokens', 'cache_read_tokens', 'cache_write_tokens')}
        return TokenUsage(**totals, server_tool_uses=self.usage_fields(usage).server_tool_uses)

    @property
    def served_content(self) -> list[dict]:
        content = self.raw['content']
        boundary = max((i for i, block in enumerate(content) if block['type'] == 'fallback'), default=-1)
        return content[boundary + 1:]

    def text(self) -> str:
        return '\n'.join(b['text'] for b in self.served_content if b['type'] == 'text')

    def routing(self) -> dict:
        blocks = [b for b in self.raw['content'] if b['type'] == 'fallback']
        iterations = self.raw['usage'].get('iterations') or []
        return {'served_model': self.raw['model'], 'fallback_blocks': blocks,
                'fallback_iterations': [i for i in iterations if i['type'] == 'fallback_message'],
                'fallback_used': bool(blocks) or any(i['type'] == 'fallback_message' for i in iterations)}


def mock_key(kind: str, prompt: str) -> str:
    return f'{kind}:{digest(prompt)}'


class Provider(Protocol):
    model: str
    def estimate(self, kind: str, prompt: str, schema: dict | None, maximum: int) -> TokenUsage: ...
    def complete(self, kind: str, prompt: str, schema: dict | None, maximum: int) -> Response: ...


class MockProvider:
    def __init__(self, responses: dict | Path, model: str = 'claude-opus-5'):
        self.responses = json.loads(responses.read_text()) if isinstance(responses, Path) else responses
        self.model = model
        self.calls = 0

    def estimate(self, kind: str, prompt: str, schema: dict | None, maximum: int) -> TokenUsage:
        return TokenUsage(input_tokens=len(prompt.encode()), output_tokens=maximum)

    def complete(self, kind: str, prompt: str, schema: dict | None, maximum: int) -> Response:
        self.calls += 1
        key = mock_key(kind, prompt)
        if key not in self.responses:
            raise MissingResponse(f'missing canned response: {key}')
        return Response(json.loads(canonical(self.responses[key])))


def structured_schema(schema: dict, depth: int = 2) -> dict:
    """Project unsupported constraints; local validation remains authoritative.

    Formula recursion becomes an acyclic chain of definitions with a finite depth.
    At depth zero only atoms and predicates are generated. No schema is weakened
    at the runtime acceptance boundary.
    """
    original = json.loads(canonical(schema))
    definitions = original.get('$defs', {})
    formula = definitions.pop('formula', None)
    if formula:
        # Two AST families avoid the per-operator grammar explosion while
        # keeping compound arguments nonempty (minItems=1 is SDK-supported).
        operators = [branch['properties']['op']['const'] for branch in formula['oneOf']]
        for level in range(depth + 1):
            leaf = {
                'type': 'object', 'additionalProperties': False,
                'properties': {
                    'op': {'type': 'string', 'enum': ['atom', 'predicate']},
                    'args': {'type': 'array', 'items': {'type': 'null'}},
                    'name': {'type': 'string'},
                    'terms': {'type': 'array', 'items': {'$ref': '#/$defs/term'}},
                    'variable': {'type': 'null'},
                },
                'required': ['op', 'args', 'name', 'terms', 'variable'],
            }
            node = leaf
            if level:
                compound = json.loads(canonical(leaf))
                compound['properties'].update({
                    'op': {'type': 'string', 'enum': [op for op in operators if op not in ('atom', 'predicate')]},
                    'args': {'type': 'array', 'minItems': 1, 'items': {'$ref': f'#/$defs/formula_{level - 1}'}},
                    'name': {'type': 'null'}, 'variable': {'type': ['string', 'null']},
                })
                node = {'anyOf': [leaf, compound]}
            definitions[f'formula_{level}'] = node
        original = json.loads(canonical(original).replace('"#/$defs/formula"', f'"#/$defs/formula_{depth}"'))
    unsupported = {'$schema', 'minimum', 'maximum', 'minLength', 'maxLength', 'minItems',
                   'maxItems', 'uniqueItems', 'if', 'then', 'else', 'allOf', 'not'}
    def project(value: Any) -> Any:
        if isinstance(value, list):
            return [project(v) for v in value]
        if not isinstance(value, dict):
            return value
        result = {('anyOf' if k == 'oneOf' else k): project(v)
                  for k, v in value.items() if k not in unsupported}
        if 'minItems' in value:
            result['minItems'] = min(1, value['minItems'])
        if result.get('type') == 'array' and 'items' not in result:
            result['items'] = {'type': 'null'}
        return result
    return project(original)


class AnthropicProvider:
    def __init__(self, config: dict, client: Any = None):
        if client is None:
            from anthropic import Anthropic
            # SDK retries can otherwise create unlogged, unreserved billable calls.
            client = Anthropic(max_retries=0)
        self.client, self.config, self.model = client, config, config['model']
        if config.get('fallbacks', 'default') not in ('default', 'off'):
            raise ValueError('fallbacks must be default or off')

    def request(self, kind: str, prompt: str, schema: dict | None, maximum: int) -> dict:
        output = {'effort': self.config['effort']}
        if schema is not None:
            output['format'] = {'type': 'json_schema', 'schema': structured_schema(
                schema, self.config.get('formula_output_depth', 2))}
        request = {'model': self.model, 'max_tokens': maximum,
                   'thinking': {'type': 'adaptive'}, 'output_config': output,
                   'messages': [{'role': 'user', 'content': prompt}]}
        if kind == 'search_evidence':
            request['tools'] = [{'type': 'web_search_20260209', 'name': 'web_search',
                                 'max_uses': self.config['web_search_max_uses'] }]
        return request

    def estimate(self, kind: str, prompt: str, schema: dict | None, maximum: int) -> TokenUsage:
        request = self.request(kind, prompt, schema, maximum)
        count_request = {k: v for k, v in request.items() if k not in ('max_tokens', 'output_config')}
        # Include the schema bytes conservatively when count_tokens cannot accept format.
        count_request['messages'] = [{'role': 'user', 'content': prompt + canonical(schema or {})}]
        count = self.client.messages.count_tokens(**count_request).input_tokens
        searches = self.config['web_search_max_uses'] if kind == 'search_evidence' else 0
        # A server search may repeatedly consume a full context window. Reserve
        # the configured model input ceiling for every possible server iteration.
        if searches:
            count = max(count, self.config['model_context_token_bound']) * (searches + 1)
        return TokenUsage(input_tokens=count, output_tokens=maximum * (searches + 1),
                          server_tool_uses=searches)

    def complete(self, kind: str, prompt: str, schema: dict | None, maximum: int) -> Response:
        request = self.request(kind, prompt, schema, maximum)
        if self.config.get('fallbacks', 'default') == 'default':
            request.update(betas=['server-side-fallback-2026-07-01'], fallbacks='default')
        raw = self.client.beta.messages.create(**request)
        return Response(raw.to_dict())
