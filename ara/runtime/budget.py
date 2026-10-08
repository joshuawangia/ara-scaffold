"""Conservative request admission and actual usage accounting with clean stops."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from ara.runtime.cache import canonical
from ara.runtime.logging import EventLog
from ara.types import TokenUsage


class BudgetStop(RuntimeError):
    pass


def tokens(usage: TokenUsage) -> int:
    return usage.input_tokens + usage.output_tokens + usage.cache_read_tokens + usage.cache_write_tokens


class Budget:
    def __init__(self, config: dict, log: EventLog):
        self.config, self.log = config, log
        self.rates = config['pricing'][config['model']]
        self.used_tokens = sum(tokens(TokenUsage.from_dict(e['usage'])) for e in log.read())
        self.used_cost = sum((Decimal(str(e['cost_usd'])) for e in log.read()), Decimal(0))

    def cost(self, usage: TokenUsage, raw_usage: dict | None = None) -> Decimal:
        r = self.rates
        creation = (raw_usage or {}).get('cache_creation') or {}
        hour = creation.get('ephemeral_1h_input_tokens', 0)
        minute = creation.get('ephemeral_5m_input_tokens', usage.cache_write_tokens - hour)
        # Unknown cache TTL is charged at the more expensive rate.
        unknown = max(0, usage.cache_write_tokens - hour - minute)
        pairs = [(usage.input_tokens, 'input_per_million_usd'),
                 (usage.output_tokens, 'output_per_million_usd'),
                 (usage.cache_read_tokens, 'cache_read_per_million_usd'),
                 (minute, 'cache_write_5m_per_million_usd'),
                 (hour + unknown, 'cache_write_1h_per_million_usd')]
        result = sum((Decimal(n) * Decimal(str(r[k])) / 1000000 for n, k in pairs), Decimal(0))
        return result + Decimal(usage.server_tool_uses) * Decimal(str(r['web_search_per_thousand_usd'])) / 1000

    def stop(self, reason: str, stage: str) -> None:
        state = {'reason': reason, 'stage': stage, 'tokens': self.used_tokens,
                 'cost_usd': float(self.used_cost), 'status': 'STOPPED'}
        self.log.record(stage, 'STOP', **{k: v for k, v in state.items() if k != 'stage'})
        (self.log.path.parent / 'partial.json').write_text(canonical(state))
        raise BudgetStop(reason)

    def before(self, usage: TokenUsage, stage: str) -> None:
        if self.used_tokens + tokens(usage) > self.config['token_cap']:
            self.stop('token cap: request reservation exceeds remaining tokens', stage)
        if self.used_cost + self.cost(usage) > Decimal(str(self.config['cost_cap_usd'])):
            self.stop('cost cap: request reservation exceeds remaining cost', stage)

    def charge(self, usage: TokenUsage, cost: Decimal) -> None:
        self.used_tokens += tokens(usage)
        self.used_cost += cost

    def after(self, stage: str) -> None:
        if self.used_tokens > self.config['token_cap']:
            self.stop('token cap exceeded by actual usage', stage)
        if self.used_cost > Decimal(str(self.config['cost_cap_usd'])):
            self.stop('cost cap exceeded by actual usage', stage)
