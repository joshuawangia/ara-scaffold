"""Conservative request admission and actual usage accounting with clean stops."""
from __future__ import annotations

from decimal import Decimal
import json

from ara.runtime.cache import canonical
from ara.runtime.logging import EventLog
from ara.types import TokenUsage
from ara.runtime.providers import Response


class UnpricedModel(ValueError):
    pass


class BudgetStop(RuntimeError):
    pass


def tokens(usage: TokenUsage) -> int:
    return usage.input_tokens + usage.output_tokens + usage.cache_read_tokens + usage.cache_write_tokens


class Budget:
    def __init__(self, config: dict, log: EventLog):
        self.config, self.log = config, log
        self.rates = config['pricing'][config['model']]
        for rates in config['pricing'].values():
            for name, value in rates.items():
                if name.endswith('_usd') and (not Decimal(str(value)).is_finite() or Decimal(str(value)) < 0):
                    raise ValueError('pricing must be finite and nonnegative')
        if not Decimal(str(config['cost_cap_usd'])).is_finite() or config['cost_cap_usd'] < 0:
            raise ValueError('cost cap must be finite and nonnegative')
        extraction_cap = Decimal(str(config.get('extraction_cost_cap_usd', config['cost_cap_usd'])))
        if not extraction_cap.is_finite() or extraction_cap < 0:
            raise ValueError('extraction cost cap must be finite and nonnegative')
        if type(config['token_cap']) is not int or config['token_cap'] < 0:
            raise ValueError('token cap must be a nonnegative integer')
        self.used_tokens = sum(tokens(TokenUsage.from_dict(e['usage'])) for e in log.read())
        self.used_cost = sum((Decimal(str(e['cost_usd'])) for e in log.read()), Decimal(0))
        if any(json.loads(e['payload_json']).get('accounting') == 'reservation_unknown_actual' for e in log.read()):
            self.stop('prior provider spend is unknown; start a reconciled new run', 'resume')
        starts = sum(e['stage'] == 'call_start' for e in log.read())
        finishes = sum(e['label'] == 'MODEL' and not json.loads(e['payload_json']).get('cache_hit')
                       for e in log.read())
        if starts > finishes:
            self.stop('interrupted provider call: actual spend unknown', 'resume')

    def cost(self, usage: TokenUsage, raw_usage: dict | None = None, model: str | None = None) -> Decimal:
        model = model or self.config['model']
        r = self.config['pricing'].get(model)
        if r is None or not {'input_per_million_usd', 'output_per_million_usd'} <= r.keys():
            raise UnpricedModel(f'unpriced served model: {model}')
        creation = (raw_usage or {}).get('cache_creation') or {}
        hour = creation.get('ephemeral_1h_input_tokens', 0)
        minute = creation.get('ephemeral_5m_input_tokens', 0)
        # Unknown cache TTL is charged at the more expensive rate.
        unknown = max(0, usage.cache_write_tokens - hour - minute)
        pairs = [(usage.input_tokens, 'input_per_million_usd'),
                 (usage.output_tokens, 'output_per_million_usd'),
                 (usage.cache_read_tokens, 'cache_read_per_million_usd'),
                 (minute, 'cache_write_5m_per_million_usd'),
                 (hour + unknown, 'cache_write_1h_per_million_usd')]
        for n, key in pairs:
            if n and key not in r:
                raise UnpricedModel(f'unpriced usage for served model {model}: {key}')
        result = sum((Decimal(n) * Decimal(str(r[k])) / 1000000 for n, k in pairs if n), Decimal(0))
        # Web search is a service charge, independent of the serving model.
        return result + Decimal(usage.server_tool_uses) * Decimal(str(self.rates['web_search_per_thousand_usd'])) / 1000

    def response_cost(self, raw: dict) -> Decimal:
        served_model = raw['model']
        # Validate the served model even for a zero-token refusal or cache entry.
        self.cost(TokenUsage(), model=served_model)
        iterations = raw['usage'].get('iterations') or []
        if not iterations:
            return self.cost(Response(raw).usage, raw['usage'], model=served_model)
        result = Decimal(0)
        fallback = Response(raw).routing()['fallback_used']
        for iteration in iterations:
            if iteration['type'] not in ('message', 'fallback_message'):
                raise ValueError('unsupported provider usage iteration')
            if fallback and not iteration.get('model'):
                raise UnpricedModel('missing model in fallback usage iteration')
            model = iteration.get('model') or served_model
            result += self.cost(Response.usage_fields(iteration), iteration, model=model)
        tools = Response(raw).usage.server_tool_uses
        return result + self.cost(TokenUsage(server_tool_uses=tools), model=served_model)

    def stop(self, reason: str, stage: str) -> None:
        state = {'reason': reason, 'stage': stage, 'tokens': self.used_tokens,
                 'cost_usd': float(self.used_cost), 'status': 'STOPPED'}
        self.log.record(stage, 'STOP', **{k: v for k, v in state.items() if k != 'stage'})
        (self.log.path.parent / 'partial.json').write_text(canonical(state))
        raise BudgetStop(reason)

    def extraction_cost(self) -> Decimal:
        return sum((Decimal(str(e['cost_usd'])) for e in self.log.read()
                    if e['stage'] == 'extract_paper' and e['label'] == 'MODEL'), Decimal(0))

    def before(self, usage: TokenUsage, stage: str, model: str | None = None) -> None:
        if stage == 'extract_paper' and self.extraction_cost() + self.cost(usage, model=model) > Decimal(str(
                self.config.get('extraction_cost_cap_usd', self.config['cost_cap_usd']))):
            self.stop('extraction cost cap: request reservation exceeds remaining cost', stage)
        if self.used_tokens + tokens(usage) > self.config['token_cap']:
            self.stop('token cap: request reservation exceeds remaining tokens', stage)
        if self.used_cost + self.cost(usage, model=model) > Decimal(str(self.config['cost_cap_usd'])):
            self.stop('cost cap: request reservation exceeds remaining cost', stage)

    def charge(self, usage: TokenUsage, cost: Decimal) -> None:
        self.used_tokens += tokens(usage)
        self.used_cost += cost

    def after(self, stage: str) -> None:
        if stage == 'extract_paper' and self.extraction_cost() > Decimal(str(
                self.config.get('extraction_cost_cap_usd', self.config['cost_cap_usd']))):
            self.stop('extraction cost cap exceeded by actual usage', stage)
        if self.used_tokens > self.config['token_cap']:
            self.stop('token cap exceeded by actual usage', stage)
        if self.used_cost > Decimal(str(self.config['cost_cap_usd'])):
            self.stop('cost cap exceeded by actual usage', stage)
