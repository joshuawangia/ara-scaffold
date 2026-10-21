"""Paper-local admission, sharing the model boundary's measured accounting."""
from decimal import Decimal, InvalidOperation
import json


def _count(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(f'{name} must be a finite nonnegative integer')
    return value


def _dollars(value, name):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f'{name} must be finite and nonnegative') from None
    if not result.is_finite() or result < 0:
        raise ValueError(f'{name} must be finite and nonnegative')
    return result


class PaperAllowance:
    def __init__(self, calls, paper):
        self.calls, self.source_id = calls, paper.source_id
        config = calls.config
        self.continuation_limit = _count(config.get('extraction_paper_continuation_limit', 24),
                                         'extraction_paper_continuation_limit')
        self.cost_cap = _dollars(config.get('extraction_paper_cost_cap_usd', 15),
                                 'extraction_paper_cost_cap_usd')
        large = config.get('extraction_large_paper_limits')
        if large is not None:
            if not isinstance(large, dict) or set(large) != {'min_pages', 'continuation_limit', 'cost_cap_usd'}:
                raise ValueError('extraction_large_paper_limits requires min_pages, continuation_limit, cost_cap_usd')
            threshold = _count(large['min_pages'], 'large paper min_pages')
            count = _count(large['continuation_limit'], 'large paper continuation_limit')
            cost = _dollars(large['cost_cap_usd'], 'large paper cost_cap_usd')
            if len(paper.pages) >= threshold:
                self.continuation_limit, self.cost_cap = count, cost
        events = calls.log.read()
        self.attempts = sum(e['stage'] == 'extraction_paper_attempt' and
                            json.loads(e['payload_json'])['source_id'] == self.source_id for e in events)
        self.prior_cost = sum((Decimal(str(e['cost_usd'])) for e in events
                               if e['label'] == 'MODEL' and e['stage'] == 'extract_paper' and
                               json.loads(e['payload_json']).get('source_id') == self.source_id), Decimal(0))
        self.start_cost = calls.budget.used_cost
        self.stopped = False
        calls.log.record('extraction_paper_allowance', **self.state(), physical_pages=len(paper.pages))

    @property
    def spent(self):
        return self.prior_cost + self.calls.budget.used_cost - self.start_cost

    def state(self):
        return dict(source_id=self.source_id, paper_attempts=self.attempts,
                    paper_continuations=max(0, self.attempts - 1),
                    paper_continuation_limit=self.continuation_limit,
                    paper_cost_usd=float(self.spent), paper_cost_cap_usd=float(self.cost_cap))

    def stop(self, reason):
        pending = set()
        for event in self.calls.log.read():
            data = json.loads(event['payload_json'])
            if data.get('source_id') != self.source_id:
                continue
            if event['stage'] == 'extraction_obligation_discovered':
                pending.add(data['obligation']['id'])
            elif event['stage'] == 'extraction_obligation_resolved':
                pending.difference_update(r['obligation_id'] for r in data['resolutions'])
        pending = sorted(pending)
        self.stopped = True
        self.calls.budget.stop(f'{reason}; paper {self.source_id}; pending IDs {pending}',
                               'extract_paper', **self.state(), pending_obligation_ids=pending)

    def before(self, estimate, *, cached):
        if self.attempts > self.continuation_limit:
            self.stop('paper continuation limit reached before dispatch')
        reserve = Decimal(0) if cached else self.calls.budget.cost(
            estimate, model=self.calls.requested_model('extract_paper'))
        if self.spent + reserve > self.cost_cap:
            self.stop('paper cost cap: request reservation exceeds remaining cost')
        self.attempts += 1
        self.calls.log.record('extraction_paper_attempt', **self.state(),
                              reserved_cost_usd=float(reserve), cache_hit=cached)

    def after(self):
        if self.spent > self.cost_cap:
            self.stop('paper cost cap exceeded by actual usage')
