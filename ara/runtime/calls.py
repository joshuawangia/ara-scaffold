"""The single model boundary: prompt, reserve, call, validate, log, cache."""
from __future__ import annotations

import json
import re
import time
from threading import Lock, RLock
import threading
import uuid
from pathlib import Path
from dataclasses import dataclass, replace
from typing import Callable, Any

from jsonschema import ValidationError
from ara.runtime.validation import decode_response, guard_complexity, validate_local

from ara.bank import load_bank
from ara.ports import InvalidProposalBatch
from ara.runtime.budget import Budget, BudgetStop, UnpricedModel
from ara.runtime.cache import Cache, cache_key, canonical, digest
from ara.runtime.logging import EventLog, now
from ara.runtime.extraction import Paper, PaperExtraction, ExtractedItem, citation_ids, save_immutable, extraction_range_plan, record_new_obligations
from ara.runtime.providers import Provider, Response, stage_settings
from ara.types import (BankEntry, CommitmentSet, CQAnswer, CriticalQuestion, Formula,
                       PremiseFill, Proposal, Proposition, RouteGraph, RunEvent,
                       Tier1Repair, TokenUsage)


@dataclass(frozen=True)
class RequestCount:
    """Context sizing is distinct from cumulative transport/accounting usage."""
    initial_input_tokens: int
    context_output_tokens: int
    reservation: TokenUsage


class Rejected(ValueError):
    pass


class EssayAuditFailed(Rejected):
    """A complete adverse audit, with the exact evidence and labels retained."""
    def __init__(self, result, inputs, labels):
        super().__init__('essay audit failed')
        self.result, self.inputs, self.labels = result, inputs, labels


class RejectedCutBatch(Rejected, InvalidProposalBatch):
    pass


class CountRequestRefused(RuntimeError):
    """A free counter request received a terminal provider request rejection."""


class InvalidOutput(Rejected):
    """A fully accounted model response failed local validation."""
    def __init__(self, reason: str, feedback: dict):
        super().__init__(reason)
        self.feedback = feedback


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise Rejected(reason)


def extraction_defaults(data: dict) -> dict:
    """Fill only omitted empty structural fields; never repair model relations."""
    for item in data.get('items', []):
        if not isinstance(item, dict):
            continue
        if item.get('kind') not in ('distinction', 'qualification'):
            item.setdefault('applies_to', [])
        if item.get('kind') != 'inference':
            for field, empty in (('premise_ids', []), ('conclusion_id', None),
                                 ('qualification_ids', []), ('inference_origin', None)):
                item.setdefault(field, empty)
    return data


def normalize_extraction(data: dict) -> list[dict]:
    """Normalize content-free wire values; retain every item and disposition."""
    changes = []
    if 'items' in data and data['items'] is None:
        data['items'] = []
        changes.append({'path': '/items', 'operation': 'null_empty_inventory_to_array'})
    if 'empty_reason' in data and data['empty_reason'] in ('', None):
        del data['empty_reason']
        changes.append({'path': '/empty_reason', 'operation': 'remove_empty_optional'})
    for index, item in enumerate(data.get('items', [])):
        if not isinstance(item, dict):
            continue
        start, end = item.get('page_start'), item.get('page_end')
        if type(start) is int and type(end) is int and start > end:
            item['page_start'], item['page_end'] = end, start
            changes.append({'path': f'/items/{index}', 'operation': 'order_page_range',
                            'before': [start, end], 'after': [end, start]})
    return changes


def normalize_patch_ids(patch: dict, candidate: dict) -> list[dict]:
    """Preserve duplicate items; never guess the referent of a distinct duplicate."""
    items = patch.get('items')
    if not isinstance(items, list) or not all(isinstance(i, dict) for i in items):
        return []
    prior = candidate.get('items', [])
    prior = prior if isinstance(prior, list) else []
    all_items = items + prior
    if not all(isinstance(i, dict) and isinstance(i.get('id'), str) for i in all_items):
        return []  # Schema/inventory validation supplies the specific feedback.
    occupied = {i['id'] for i in all_items}
    patch_ids = {i['id'] for i in items}
    previous = {i['id']: i for i in prior}
    referenced = set()
    for item in all_items:
        for field in ('premise_ids', 'qualification_ids', 'applies_to', 'evidence_ids'):
            if isinstance(item.get(field), list):
                referenced.update(r for r in item[field] if isinstance(r, str))
        if isinstance(item.get('conclusion_id'), str):
            referenced.add(item['conclusion_id'])
    resolutions = patch.get('resolutions', [])
    if isinstance(resolutions, list):
        for resolution in resolutions:
            if isinstance(resolution, dict) and isinstance(resolution.get('evidence_ids'), list):
                referenced.update(r for r in resolution['evidence_ids'] if isinstance(r, str))
    first, changes = {}, []
    for index, item in enumerate(items):
        old = item.get('id')
        if not isinstance(old, str) or not old:
            continue
        if old not in first:
            first[old] = item
            continue
        require(old not in referenced or item == first[old],
                f'ambiguous duplicate correction id {old}; give each distinct item a unique id and explicit references')
        serial = 2
        fresh = f'{old}__duplicate_{serial}'
        while fresh in occupied:
            normalized = extraction_defaults({'items': [{**item, 'id': fresh}]})['items'][0]
            if fresh not in patch_ids and fresh in previous and previous[fresh] == normalized:
                break  # Replaying the same failed patch retains the same ID.
            serial += 1
            fresh = f'{old}__duplicate_{serial}'
        item['id'] = fresh
        occupied.add(fresh)
        patch_ids.add(fresh)
        changes.append({'path': f'/items/{index}/id', 'operation': 'rename_duplicate_id',
                        'before': old, 'after': fresh, 'references': 'first_occurrence'})
    return changes


def merge_extraction_patch(candidate: dict, patch: dict) -> dict:
    """A patch replaces named items, preserves omitted items, and adds new IDs."""
    def inventory(data):
        require(isinstance(data, dict) and isinstance(data.get('items'), list),
                'candidate cannot support targeted correction')
        require(all(isinstance(item, dict) and isinstance(item.get('id'), str) and item['id']
                    for item in data['items']), 'ambiguous correction inventory')
        ids = [item['id'] for item in data['items']]
        require(len(ids) == len(set(ids)), 'duplicate correction id')
        return {item['id']: item for item in data['items']}
    old, updates = inventory(candidate), inventory(patch)
    discarded = patch.get('discard_items', [])
    ids = [d['id'] for d in discarded]
    require(len(ids) == len(set(ids)) and set(ids) <= old.keys() and not set(ids) & updates.keys() and
            all(d['reason'].strip() for d in discarded), 'invalid rejected-candidate discard')
    merged = {k: v for k, v in patch.items() if k != 'discard_items'}
    merged['items'] = [updates.pop(id, item) for id, item in old.items() if id not in ids]
    merged['items'].extend(updates.values())
    return merged


def word_count(draft: dict) -> int:
    # Count every whitespace-delimited token in title and body, including markers.
    return len(re.findall(r'\S+', draft['title'] + '\n' + draft['body']))


def walk(value: Any):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def extraction_failure_reason(exc):
    return f'{type(exc).__name__}: {exc}' if isinstance(exc, (Rejected, BudgetStop)) else type(exc).__name__


class ModelCalls:
    def __init__(self, config: dict, provider: Provider, log: EventLog, cache: Cache,
                 root: Path, topic: str, *, provider_factory=None, imported_draft=None):
        self.config, self.provider, self.log, self.cache = config, provider, log, cache
        self.root, self.topic = Path(root), topic
        self._paper_budget = None
        self.construction_resume = False
        self._key_lock = Lock()
        self._key_locks = {}
        self.provider_factory = provider_factory
        self._stage_providers = {}
        self._calibration_state = None
        if hasattr(provider, 'calibration_state'):
            from ara.runtime.claude_estimation import CalibrationState
            self._calibration_state = CalibrationState()
            self._calibration_state.restore(self.log.read())
            provider.calibration_state = self._calibration_state
        self._stage_provider_lock = RLock()
        self._reservations = threading.local()
        if imported_draft is not None:
            self.screen_imported_draft(imported_draft, kind='audit_publication')
        self.budget = Budget(config, log)
        self._ensure_provider_ready(force=True)

    def screen_imported_draft(self, draft, *, kind='audit_essay'):
        """One input screen shared by resumed writing and publication."""
        providers = [self.provider, self._for_construction_stage(kind, {}).provider]
        for provider in {id(p): p for p in providers}.values():
            if hasattr(provider, 'scan_output'):
                provider.scan_output(draft)

    def _subscription(self):
        return getattr(self.provider, 'provider_kind', None) in ('claude_code', 'codex_cli')

    def _ensure_provider_ready(self, *, force=False):
        with self._stage_provider_lock:
            if self._subscription() and (force or not self.provider.ready):
                self.call('isolation_canary', {})
                self.provider.ready = True

    def _for_construction_stage(self, kind, inputs, *, attempt=1):
        from copy import copy
        from ara.runtime.construction_stages import dispatch_settings
        if hasattr(self, '_dispatch_stage'):
            return self
        stage, overrides, settings = dispatch_settings(self.config, kind,
            correction=attempt > 1 or inputs.get('mode') == 'targeted_correction')
        if not overrides:
            return self
        require(self.provider_factory is not None, 'construction stage overrides require a provider factory')
        key = canonical(settings)
        with self._stage_provider_lock:
            if key not in self._stage_providers:
                self._stage_providers[key] = self.provider_factory(settings)
                stage_provider = self._stage_providers[key]
                if hasattr(stage_provider, 'calibration_state'):
                    if self._calibration_state is None:
                        self._calibration_state = stage_provider.calibration_state
                        self._calibration_state.restore(self.log.read())
                    stage_provider.calibration_state = self._calibration_state
        scoped = copy(self)
        scoped.config, scoped.provider = settings, self._stage_providers[key]
        scoped._dispatch_stage = stage
        scoped._dispatch_identity = digest(canonical({'provider': settings['provider'], 'overrides': overrides,
                                                     'options': settings.get(settings['provider'], {})}))
        return scoped

    def requested_model(self, kind: str) -> str:
        return self.provider.model_for(kind) if hasattr(self.provider, 'model_for') else self.provider.model

    def response_schema(self, kind: str, inputs: dict) -> dict | None:
        if kind == 'isolation_canary':
            from ara.runtime.claude_code import CANARY_SCHEMA
            return CANARY_SCHEMA
        if kind == 'search_evidence':
            return None
        schema = json.loads((self.root / 'schemas' / f'{kind}.json').read_text())
        if kind == 'extract_paper':
            if inputs.get('mode') != 'targeted_correction':
                del schema['properties']['discard_items']
            mode = inputs.get('original_mode') if inputs.get('mode') == 'targeted_correction' else inputs.get('mode')
            reconciliation = mode == 'reconcile_ranges'
            if not reconciliation or not inputs.get('obligations'):
                for field in ('context_request', 'pending_obligation_ids', 'resolutions'):
                    del schema['properties'][field]
            if reconciliation:
                del schema['properties']['empty_reason']
            elif inputs.get('mode') == 'targeted_correction':
                # Explicit discards may remove all rejected candidate items.
                pass
            else:
                # The provider projection preserves these disjoint alternatives.
                # Empty arrays are represented without unsupported maxItems=0.
                schema['oneOf'] = [
                    {'properties': {'items': {'minItems': 1}, 'empty_reason': {'type': 'null'}}},
                    {'properties': {'items': {'items': {'type': 'null'}},
                                    'empty_reason': {'type': 'string', 'minLength': 1}},
                     'required': ['empty_reason']},
                ]
        return schema

    def render(self, kind: str, inputs: dict) -> tuple[str, str]:
        if kind == 'isolation_canary':
            from ara.runtime.claude_code import CANARY_PROMPT
            prompt = getattr(self.provider, 'canary_prompt', CANARY_PROMPT)
            return prompt, prompt
        template = (self.root / 'prompts' / f'{kind}.txt').read_text()
        if kind != 'search_evidence':
            # The service grammar is a compact projection. Show the model every
            # local constraint as well; the same complete prompt is logged/keyed.
            schema = self.response_schema(kind, inputs)
            note = ('constraints apply after runtime completion of omitted edge fields; follow WIRE SHAPE, never put field instructions in text'
                    if kind == 'extract_paper' else 'all constraints are mandatory')
            template += f'\nLOCAL_RESPONSE_SCHEMA ({note})\n' + canonical(schema)
        # JSON input is data, never interpreted as a format template.
        return template, template + '\nINPUT_JSON\n' + canonical({'topic': self.topic, **inputs})

    def call(self, kind: str, inputs: dict, check: Callable[[dict], Any] | None = None, *, fresh: bool = False, validation_attempts: int | None = None) -> Any:
        attempts = self.config.get('validation_attempts', 1) if validation_attempts is None else validation_attempts
        if type(attempts) is not int or not 1 <= attempts <= 3:
            raise ValueError('validation_attempts must be between 1 and 3')
        whole_essay = kind == 'write_essay' and 'mode' not in inputs
        if whole_essay:
            attempts = 4
        request_inputs = inputs
        for attempt in range(attempts):
            try:
                return self._transport_call(kind, request_inputs, check, attempt=attempt + 1, fresh=fresh)
            except InvalidOutput as exc:
                if attempt + 1 == attempts:
                    raise
                self.log.record('validation_retry', kind=kind, next_attempt=attempt + 2,
                                reason=str(exc))
                if not whole_essay:
                    request_inputs = {**inputs, 'validation_feedback': exc.feedback}
        raise AssertionError('unreachable')

    def _transport_call(self, kind, inputs, check, *, attempt, fresh=False):
        from ara.runtime.claude_code import ClaudeCodeError
        provider = self._for_construction_stage(kind, inputs, attempt=attempt).provider
        unclassified_retries = 0
        auth_retries = 0
        for retry in range(getattr(provider, 'retries', 0) + 1):
            try:
                return self._call_once(kind, inputs, check, attempt=attempt, fresh=fresh)
            except ClaudeCodeError as exc:
                unclassified = exc.code == 'cli_exit_error' and exc.receipt.get('exit_status') == 1
                auth = exc.code == 'cli_auth_error'
                if (not exc.retryable or retry == provider.retries
                        or (unclassified and unclassified_retries >= 1) or (auth and auth_retries >= 1)):
                    raise Rejected(exc.code) from None
                if unclassified:
                    unclassified_retries += 1
                if auth:
                    auth_retries += 1
                delay = min(30, provider.backoff * 2 ** retry)
                event = 'auth_refresh_retry' if auth else ('unclassified_exit_retry' if unclassified else 'provider_retry')
                self.log.record(event, kind=kind, next_attempt=retry + 2,
                                delay_seconds=delay, reason=exc.code)
                time.sleep(delay)
        raise AssertionError('unreachable')

    def _call_once(self, kind: str, inputs: dict, check: Callable[[dict], Any] | None = None, *, attempt: int = 1, schema_smoke: bool = False, fresh: bool = False) -> Any:
        scoped = self._for_construction_stage(kind, inputs, attempt=attempt)
        if scoped is not self:
            return scoped._call_once(kind, inputs, check, attempt=attempt, schema_smoke=schema_smoke, fresh=fresh)
        if kind != 'isolation_canary':
            self._ensure_provider_ready()
        if not schema_smoke and kind in ('map_leaf', 'propose_cuts') and 'commitments' in inputs:
            from ara.runtime.search_context import fit_leaf_request
            inputs = fit_leaf_request(self, kind, inputs)
        if not schema_smoke and kind == 'answer_cq' and 'commitments' in inputs:
            from ara.runtime.cq_context import fit_cq_request
            inputs = fit_cq_request(self, inputs)
        if not schema_smoke and kind == 'propose_targets' and 'commitments' in inputs:
            from ara.runtime.search_context import fit_target_request
            inputs = fit_target_request(self, inputs)
        # Same-request single flight prevents duplicate dispatch and partial cache reads.
        key = digest(canonical([kind, inputs, schema_smoke]))
        with self._key_lock:
            lock = self._key_locks.setdefault(key, RLock())
        with lock:
            return self._call_reserved(kind, inputs, check, attempt=attempt, schema_smoke=schema_smoke, fresh=fresh)

    def _call_reserved(self, kind, inputs, check, *, attempt, schema_smoke, fresh=False):
        state = {}
        started = time.monotonic()
        previous_call_id = getattr(self._reservations, 'call_id', None)
        self._reservations.call_id = str(uuid.uuid4())
        try:
            return self._execute_once(kind, inputs, check, attempt=attempt,
                                      schema_smoke=schema_smoke, state=state, fresh=fresh)
        except Exception as exc:
            admission = state.get('admission')
            if admission is None or state.get('completed'):
                raise
            receipt = state.get('receipt')
            if receipt:
                self._event(kind, admission['prompt'], receipt['raw_response'],
                            TokenUsage.from_dict(receipt['measured_usage']), receipt['measured_cost_usd'],
                            started, False, 'rejected', type(exc).__name__, receipt['cache_key'], attempt=attempt)
                self.budget.stop('post-response failure; measured usage retained', kind)
            usage = TokenUsage.from_dict(admission['reserved_usage'])
            cost = self.budget.cost(usage, model=self.requested_model(kind), subscription=self._subscription())
            self.budget.settle(state['reservation'], usage, cost)
            self.log.emit(RunEvent(now(), kind, 'MODEL', self.requested_model(kind), None,
                admission['prompt'], None, usage, float(cost), time.monotonic() - started,
                payload_json=canonical({'status': 'incomplete', 'attempt': attempt, 'reason': type(exc).__name__,
                    'cache_hit': False, 'cache_key': admission['cache_key'],
                    'accounting': 'reservation_unknown_actual', 'call_id': self._reservations.call_id,
                    **({'source_id': self._paper_budget.source_id} if kind == 'extract_paper' and self._paper_budget else {})})))
            self.budget.after(kind, subscription=self._subscription())
            self.budget.stop('provider result incomplete; reservation charged; actual spend unknown', kind)
        finally:
            self.budget.release(state.get('reservation'))
            self._reservations.call_id = previous_call_id

    def _execute_once(self, kind: str, inputs: dict, check: Callable[[dict], Any] | None = None, *, attempt: int = 1, schema_smoke: bool = False, state: dict, fresh: bool = False) -> Any:
        template, prompt = self.render(kind, inputs)
        schema = self.response_schema(kind, inputs)
        maximum = self.config.get(f'{kind}_max_output_tokens', self.config['max_output_tokens'])
        if kind == 'build_t_batch':
            maximum = self.config['extracted_build_t_max_output_tokens']
        if kind == 'isolation_canary':
            maximum = 4096
        identity = canonical({'inputs': inputs, 'topic': self.topic, 'provider': type(self.provider).__name__,
                              **({'dispatch_stage': self._dispatch_stage, 'dispatch_settings': self._dispatch_identity}
                                 if hasattr(self, '_dispatch_stage') else {}),
                              'effort': stage_settings(self.config, kind)['effort'], 'maximum': maximum,
                              'thinking': stage_settings(self.config, kind).get('thinking', 'adaptive'),
                              'web_max': self.config['web_search_max_uses'],
                              'formula_depth': self.config.get('formula_output_depth', 2),
                              'fallbacks': stage_settings(self.config, kind).get('fallbacks', ['claude-opus-4-8']),
                              **({'system_prompt': stage_settings(self.config, kind)['system_prompt']}
                                 if stage_settings(self.config, kind).get('system_prompt') else {}),
                              **({'provider_metadata': self.provider.metadata(kind)} if hasattr(self.provider, 'metadata') else {})})
        if schema_smoke:
            prompt = 'P. Return a JSON object matching the response schema.'
            maximum = 1
            if self.config.get('provider') == 'codex_cli':
                from ara.runtime.codex_schema import placeholder, wire_value
                prompt = 'Return exactly this placeholder JSON, without using tools:\n' + canonical(wire_value(schema, placeholder(schema)))
                maximum = 4096
        key = cache_key(kind, template, identity, self.requested_model(kind), schema or {})
        saved = None
        if not fresh and not schema_smoke and kind != 'isolation_canary':
            saved = self.cache.get(key)
        start = time.monotonic()
        raw = None
        usage, cost = TokenUsage(), self.budget.cost(TokenUsage())
        cached = saved is not None
        dispatched = False
        validating = False
        charged = False
        estimate = TokenUsage()
        try:
            if schema_smoke:
                estimate = self.provider.estimate(kind, prompt, schema, maximum)
            else:
                estimate = self.count_request(kind, inputs, maximum=maximum, admission=True).reservation
            if not cached:
                state['reservation'] = self.budget.reserve(estimate, kind, model=self.requested_model(kind), subscription=self._subscription())
            if kind == 'extract_paper' and self._paper_budget is not None:
                self._paper_budget.before(estimate, cached=cached)
            if cached:
                if hasattr(self.provider, 'scan_output'):
                    from ara.runtime.claude_code import ClaudeCodeError
                    try:
                        self.provider.scan_output(saved['raw'])
                    except ClaudeCodeError:
                        self.cache.discard(key)
                        raise
                raw = saved['raw']
                self.budget.response_cost(raw)  # Cached responses retain validated model/pricing provenance.
            else:
                self.log.record('call_start', kind=kind, attempt=attempt, model=self.requested_model(kind), prompt=prompt,
                                schema=schema, reserved_usage=estimate.to_dict(), cache_key=key, call_id=self._reservations.call_id,
                                **(self.provider.metadata(kind) if hasattr(self.provider, 'metadata') else {}))
                state['admission'] = dict(prompt=prompt, reserved_usage=estimate.to_dict(), cache_key=key)
                dispatched = True
                raw = self.provider.complete(kind, prompt, schema, maximum).raw
                usage = Response(raw).usage
                require(all(type(n) is int and n >= 0 for n in usage.to_dict().values()), 'invalid usage')
                cost = self.budget.response_cost(raw)
                # Keep the reservation until the measured receipt is durable.
                # Parsing and follow-up validation happen only after accounting.
                self._receive(state, kind, key, raw, usage, cost)
                charged = True
                if hasattr(self.provider, 'observe'):
                    self.log.record('provider_estimate_observation', kind=kind, call_id=self._reservations.call_id,
                                    **self.provider.observe(kind, prompt, schema, estimate, raw))
            # Stop reason is checked BEFORE interpreting any content blocks.
            if schema_smoke and self.config.get('provider') != 'codex_cli':
                require(raw['stop_reason'] in ('end_turn', 'max_tokens'), f'provider stop: {raw["stop_reason"]}')
            else:
                require(raw['stop_reason'] == 'end_turn', f'provider stop: {raw["stop_reason"]}')
            require(not any(isinstance(v, dict) and (v.get('is_error') or
                        str(v.get('type', '')).endswith('_error') or v.get('error_code'))
                        for v in walk(raw['content'])), 'server tool error')
            if schema_smoke and self.config.get('provider') != 'codex_cli':
                data = {'grammar_accepted': True}
            elif schema is None:
                urls = sorted({v['url'] for v in walk(Response(raw).served_content) if isinstance(v, dict)
                               and v.get('type') == 'web_search_result' and isinstance(v.get('url'), str)})
                data = {'text': Response(raw).text(), 'urls': urls, 'content': Response(raw).served_content}
                require(bool(data['text']), 'empty evidence response')
            else:
                validating = True
                data = decode_response(Response(raw).text())
                guard_complexity(data, self.config)
                if hasattr(self.provider, 'normalize_output'):
                    data = self.provider.normalize_output(schema, data)
                if kind == 'build_t_batch' and isinstance(data, dict) and isinstance(data.get('commitments'), list):
                    for item in data['commitments']:
                        if isinstance(item, dict) and isinstance(item.get('formula'), str):
                            try:
                                item['formula'] = decode_response(item['formula'])
                            except json.JSONDecodeError as exc:
                                raise Rejected('invalid encoded formula JSON') from exc
                if kind == 'extract_paper' and isinstance(data, dict):
                    changes = normalize_extraction(data)
                    if inputs.get('mode') == 'targeted_correction':
                        changes += normalize_patch_ids(data, inputs['candidate'])
                    if changes:
                        self.log.record('extraction_normalized', cache_key=key, changes=changes,
                                        source_id=inputs.get('source_id'), attempt=attempt)
                    extraction_defaults(data)
                validate_local(schema, data, self.config)
            result = check(data) if check else data
        except Exception as exc:
            if isinstance(exc, CountRequestRefused) and not dispatched:
                raise
            if not charged and isinstance(exc, BudgetStop):
                raise
            from ara.runtime.claude_code import ClaudeCodeError
            if isinstance(exc, ClaudeCodeError) and exc.response is not None and not charged:
                raw = exc.response
                usage = Response(raw).usage
                cost = self.budget.response_cost(raw)
                self._receive(state, kind, key, raw, usage, cost)
                charged = True
                if hasattr(self.provider, 'observe'):
                    self.log.record('provider_estimate_observation', kind=kind, call_id=self._reservations.call_id,
                                    **self.provider.observe(kind, prompt, schema, estimate, raw))
            if not validating:
                from ara.runtime.providers import provider_error_evidence
                self.log.record('provider_error', kind=kind, **provider_error_evidence(exc, prompt))
            # Provider exception messages can embed HTTP credentials. Store only
            # their class; model responses and local validation remain in full.
            reason = str(exc) if isinstance(exc, (Rejected, UnpricedModel)) else type(exc).__name__
            if isinstance(exc, ValidationError):
                reason = (f'ValidationError at /{"/".join(map(str, exc.absolute_path))}: {exc.validator} constraint failed'
                          if isinstance(exc.validator, str) else exc.message)
                if exc.context:
                    reason += '; ' + '; '.join(
                        f'/{"/".join(map(str, error.absolute_path))}: {error.validator}'
                        for error in exc.context)
            unknown_usage = dispatched and not charged
            if unknown_usage:
                usage, cost = estimate, self.budget.cost(estimate, model=self.requested_model(kind), subscription=self._subscription())
                self.budget.settle(state['reservation'], usage, cost)
            self._event(kind, prompt, raw, usage, cost, start, cached, 'incomplete' if unknown_usage else 'rejected', reason, key, unknown_usage, attempt=attempt, error_receipt=getattr(exc, 'receipt', None))
            state['completed'] = True
            if isinstance(exc, ClaudeCodeError):
                self.budget.after(kind, subscription=self._subscription())
                raise
            if unknown_usage:
                self.budget.after(kind, subscription=self._subscription())
                from ara.runtime.providers import terminal_request_refusal
                if kind in ('select_t_roots', 'build_t_batch') and terminal_request_refusal(exc):
                    self.log.record('construction_provider_refusal', kind=kind, cache_key=key,
                                    policy='count-at-reservation', terminal=True,
                                    evidence=provider_error_evidence(exc),
                                    note='Terminal provider rejection; actual usage unknown; reservation retained.')
                    raise Rejected('terminal provider request refusal; unknown usage counted at reservation') from exc
                self.budget.stop(f'provider accounting unavailable ({reason}); reservation charged; actual spend unknown', kind)
            self._after(kind)
            if not isinstance(exc, (Rejected, ValueError, ValidationError)):
                self.log.record('validation_failed', kind=kind, reason=type(exc).__name__, cache_key=key)
                raise
            if validating and not (kind in ('audit_essay', 'audit_publication') and isinstance(exc, Rejected)):
                raise InvalidOutput(reason, {'error': reason if isinstance(exc, ValidationError) or kind == 'extract_paper' else str(exc),
                    'rejected_response': Response(raw).text(),
                    'instruction': 'Return a new response satisfying every local schema and reference constraint.'}) from exc
            if not isinstance(exc, Rejected):
                raise
            if isinstance(exc, EssayAuditFailed):
                raise
            raise Rejected(reason) from exc
        self._event(kind, prompt, raw, usage, cost, start, cached, 'accepted', None, key, attempt=attempt)
        state['completed'] = True
        self._after(kind)
        if not fresh and not cached and not schema_smoke and kind != 'isolation_canary':
            self.cache.put(key, {'raw': raw})
        return result

    def _receive(self, state, kind, key, raw, usage, cost):
        self.log.record('response_received', kind=kind, cache_key=key,
                        requested_model=self.requested_model(kind), raw_response=raw,
                        call_id=self._reservations.call_id,
                        measured_usage=usage.to_dict(), measured_cost_usd=float(cost))
        self.budget.settle(state['reservation'], usage, cost)
        state['receipt'] = dict(raw_response=raw, measured_usage=usage.to_dict(),
                                measured_cost_usd=float(cost), cache_key=key)

    def _after(self, kind):
        self.budget.after(kind, subscription=self._subscription())
        if kind == 'extract_paper' and self._paper_budget is not None:
            self._paper_budget.after()

    def _event(self, kind: str, prompt: str, raw: dict | None, usage: TokenUsage,
               cost: Any, start: float, cached: bool, status: str, reason: str | None,
               key: str, unknown_usage: bool = False, *, attempt: int = 1, error_receipt: dict | None = None) -> None:
        self.log.emit(RunEvent(now(), kind, 'MODEL', self.requested_model(kind),
                              raw.get('model') if raw else None, prompt,
                              canonical(raw) if raw is not None else None, usage, float(cost),
                              time.monotonic() - start,
                              payload_json=canonical({'status': status, 'reason': reason, 'attempt': attempt,
                                                       'cache_hit': cached, 'cache_key': key,
                                                       'call_id': self._reservations.call_id,
                                                       'requested_model': self.requested_model(kind),
                                                       'provider': self.config.get('provider'),
                                                       'dispatch_stage': getattr(self, '_dispatch_stage', kind),
                                                       **(self.provider.metadata(kind) if hasattr(self.provider, 'metadata') else {}),
                                                       **({k: raw[k] for k in ('cli', 'subscription_usage', 'isolation') if k in raw} if raw else {}),
                                                       **({'cli': error_receipt} if error_receipt else {}),
                                                       'effort': stage_settings(self.config, kind)['effort'],
                                                       'thinking': stage_settings(self.config, kind).get('thinking', 'adaptive'),
                                                       **(Response(raw).routing() if raw else {}),
                                                       'accounting': 'reservation_unknown_actual' if unknown_usage else 'actual',
                                                       **({'source_id': self._paper_budget.source_id} if kind == 'extract_paper' and self._paper_budget else {})})))

    def count_request(self, kind: str, inputs: dict, *, maximum: int | None = None,
                      admission: bool = False, purpose: str | None = None) -> RequestCount:
        if purpose is None:
            purpose = ('commitments_only_capacity_not_target_readiness'
                       if kind == 'propose_targets' and 'bank' not in inputs else 'assembled_request')
        scoped = self._for_construction_stage(kind, inputs)
        if scoped is not self:
            return scoped.count_request(kind, inputs, maximum=maximum, admission=admission, purpose=purpose)
        if maximum is None:
            maximum = self.config.get(f'{kind}_max_output_tokens', self.config['max_output_tokens'])
            if kind == 'build_t_batch':
                maximum = self.config['extracted_build_t_max_output_tokens']
        if kind == 'isolation_canary':
            maximum = 4096
        prompt = self.render(kind, inputs)[1]
        schema = self.response_schema(kind, inputs)
        try:
            estimate = self.provider.estimate(kind, prompt, schema, maximum)
        except Exception as exc:
            from ara.runtime.providers import terminal_request_refusal, provider_error_evidence
            if terminal_request_refusal(exc):
                self.log.record('token_count_refused', kind=kind, request_hash=digest(prompt),
                                cost_usd=0, evidence=provider_error_evidence(exc))
                raise CountRequestRefused('terminal token-count request refusal; no charge or dispatch') from exc
            self.log.record('token_count_failed', kind=kind, request_hash=digest(prompt),
                            cost_usd=0, evidence=provider_error_evidence(exc))
            if isinstance(exc, ValueError):
                # Counter failures during output validation are operational, not model errors.
                raise RuntimeError('token counting failed') from exc
            raise
        # The search reservation includes future tool iterations. Admission concerns
        # the counted initial context; each iteration is separately bounded by the service.
        initial = estimate.input_tokens - (self.config['model_context_token_bound'] * estimate.server_tool_uses
                                           if kind == 'search_evidence' else 0)
        if hasattr(self.provider, 'initial_context_tokens'):
            initial = self.provider.initial_context_tokens(estimate)
        context_output = self.provider.context_output_tokens(maximum) if hasattr(self.provider, 'context_output_tokens') else maximum
        fits = initial + context_output <= self.config['model_context_token_bound']
        self.log.record('context_admission' if admission else 'context_plan', kind=kind, purpose=purpose,
                        model=self.requested_model(kind), provider=self.config.get('provider'),
                        dispatch_stage=getattr(self, '_dispatch_stage', kind),
                        input_tokens=initial, output_tokens=context_output, reserved_usage=estimate.to_dict(),
                        limit=self.config['model_context_token_bound'],
                        decision='fits' if fits else 'refused', prompt=prompt,
                        token_count_method=getattr(self.provider, 'estimate_method', 'provider_count'),
                        calibration=self.provider.metadata(kind).get('calibration') if hasattr(self.provider, 'metadata') else None)
        if admission and not fits:
            from ara.runtime.search_context import SEARCH_STAGES
            self.budget.stop(f'{kind} context bound exceeded by counted request; no truncation', kind,
                             scope=('paper' if kind == 'extract_paper' else
                                    'window' if kind in ('select_t_roots', 'build_t_batch') else
                                    'search' if kind in SEARCH_STAGES or
                                    (kind == 'formalise' and 'commitments_sha256' in inputs) else 'run'))
        return RequestCount(initial, context_output, estimate)

    def extract_paper(self, paper: Paper, *, salvaged=(), salvage_only=False) -> PaperExtraction:
        from ara.runtime.extraction_budget import PaperAllowance
        require(self._paper_budget is None, 'nested paper extraction')
        allowance = self._paper_budget = PaperAllowance(self, paper)
        try:
            return self._extract_paper(paper, salvaged=salvaged, salvage_only=salvage_only)
        except BudgetStop as exc:
            if not allowance.stopped:
                allowance.stop(str(exc), scope=exc.scope)
            raise
        finally:
            self._paper_budget = None

    def _extraction_response(self, paper, inputs, pages, prefix, existing=(),
                             allow_incomplete=False, validate_context=None, single_pass=False, recorded_data=None):
        corrections = self.config.get('extraction_targeted_corrections')
        if corrections is not None and (type(corrections) is not int or corrections not in (0, 1, 2, 3)):
            raise ValueError('extraction_targeted_corrections must be 0, 1, 2 or 3')
        known = {item.id for item in existing}
        def check(data):
            require(data['source_id'] == paper.source_id, 'extraction source id mismatch')
            require(bool(data['items']) or inputs.get('mode') == 'reconcile_ranges' or
                    (bool(data.get('empty_reason', '').strip()) and data['coverage_complete'] and
                     not data['new_gaps']), 'empty extraction requires complete no-argument disposition')
            require(not data.get('empty_reason') or not data['items'], 'nonempty extraction has empty disposition')
            pending_ids = data.get('pending_obligation_ids', [])
            incomplete = bool(pending_ids or data['new_gaps'])
            require(data['coverage_complete'] or (allow_incomplete and incomplete), 'extraction coverage incomplete')
            require(not data['coverage_complete'] or not incomplete, 'unresolved obligation status mismatch')
            require(all(gap['description'].strip() for gap in data['new_gaps']), 'blank new gap')
            items = tuple(ExtractedItem(**item) for item in data['items'])
            ids = [item.id for item in items]
            require(len(ids) == len(set(ids)), 'duplicate extraction id')
            require(not set(ids) & known, 'extraction redeclares immutable evidence')
            mapping = {id: f'{paper.source_id}:{prefix}:{id}' for id in ids}
            available = set(ids) | known
            for item in items:
                require(item.source_id == paper.source_id, 'extraction item source id mismatch')
                require(1 <= item.page_start <= item.page_end <= len(paper.pages),
                        f'extraction page outside paper: {item.id} cites {item.page_start}-{item.page_end}; '
                        f'valid physical bounds 1-{len(paper.pages)}')
                require(bool(item.text.strip()) and bool(item.attributed_to.strip()), 'extraction text is blank')
                readable = {page.page for page in pages}
                require(item.page_start in readable and item.page_end in readable and
                        not any(item.page_start <= page <= item.page_end for page in paper.unread_pages),
                        'extraction cites unread page')
                refs = (*item.premise_ids, *item.qualification_ids, *item.applies_to,
                        *((item.conclusion_id,) if item.conclusion_id else ()))
                require(set(refs) <= available, 'extraction link has unknown endpoint')
                if item.kind == 'inference':
                    require(bool(item.premise_ids) and bool(item.conclusion_id) and
                            item.inference_origin in ('paper_stated', 'reconstructed'), 'invalid stated inference')
                else:
                    require(not item.premise_ids and item.conclusion_id is None and
                            not item.qualification_ids and item.inference_origin is None, 'node contains inference fields')
                require(not item.applies_to or item.kind in ('distinction', 'qualification'), 'invalid qualification relation')
            by_id = {item.id: item for item in (*existing, *items)}
            if data.get('no_inference_reason') is not None:
                require(bool(data['no_inference_reason'].strip()), 'blank no-inference disposition')
                require(not any(i.kind == 'inference' for i in by_id.values()),
                        'no-inference disposition conflicts with inference evidence')
            for item in items:
                if item.kind == 'inference':
                    require(all(by_id[id].kind != 'inference' for id in (*item.premise_ids, item.conclusion_id)),
                            'inference endpoint must be a proposition')
                    require(all(by_id[id].kind in ('distinction', 'qualification') for id in item.qualification_ids),
                            'inference qualification has wrong kind')
            def mapped(id):
                return mapping.get(id, id)
            converted = tuple(replace(item, id=mapped(item.id),
                premise_ids=tuple(map(mapped, item.premise_ids)),
                conclusion_id=mapped(item.conclusion_id) if item.conclusion_id else None,
                qualification_ids=tuple(map(mapped, item.qualification_ids)),
                applies_to=tuple(map(mapped, item.applies_to))) for item in items)
            obligations = inputs.get('obligations', [])
            resolutions = data.get('resolutions', [])
            resolved_ids = [r['obligation_id'] for r in resolutions]
            require(len(resolved_ids) == len(set(resolved_ids)) and
                    len(pending_ids) == len(set(pending_ids)) and not set(pending_ids) & set(resolved_ids) and
                    set(resolved_ids) | set(pending_ids) == {o['id'] for o in obligations}, 'unresolved obligation inventory')
            request = data.get('context_request', {})
            require(not request or (inputs.get('mode') == 'reconcile_ranges' and bool(pending_ids)),
                    'context request requires a pending obligation')
            if request:
                require(bool(request['pages'] or request['evidence_ids']), 'unresolved obligation empty context request')
                if validate_context is not None:
                    validate_context(request)
            require(all(r['evidence_ids'] and set(r['evidence_ids']) <= available for r in resolutions),
                    'obligation resolution lacks accepted evidence')
            ledger = [{**r, 'evidence_ids': [mapped(id) for id in r['evidence_ids']]} for r in resolutions]
            dispositions = ([dict(pages=[p.page for p in pages], reason=data['empty_reason'])]
                            if data.get('empty_reason') else [])
            if data.get('no_inference_reason'):
                dispositions.append(dict(pages=[p.page for p in pages],
                                         kind='no_explicit_inferential_structure',
                                         reason=data['no_inference_reason']))
            return PaperExtraction(paper.source_id, converted, resolutions_json=canonical(ledger),
                                   dispositions_json=canonical(dispositions)), data['new_gaps'], request
        if recorded_data is not None:
            validate_local(self.response_schema('extract_paper', inputs), recorded_data, self.config)
            return check(recorded_data)
        if single_pass:
            return self._call_once('extract_paper', inputs, check)
        if corrections is None:
            return self.call('extract_paper', inputs, check)
        candidate = None
        request = inputs
        for correction in range(corrections + 1):
            def corrected(patch):
                merged = merge_extraction_patch(candidate, patch)
                extraction_defaults(merged)
                schema = self.response_schema('extract_paper', inputs)
                validate_local(schema, merged, self.config)
                result = check(merged)
                for discarded in patch.get('discard_items', []):
                    self.log.record('extraction_candidate_discarded', source_id=paper.source_id,
                                    candidate_hash=digest(canonical(candidate)), **discarded)
                return result
            try:
                return self._call_once('extract_paper', request,
                                       check if correction == 0 else corrected, attempt=correction + 1)
            except InvalidOutput as exc:
                if correction == corrections:
                    raise
                try:
                    rejected = json.loads(exc.feedback['rejected_response'])
                    if isinstance(rejected, dict):
                        changes = normalize_extraction(rejected)
                        if candidate is not None:
                            changes += normalize_patch_ids(rejected, candidate)
                        if changes:
                            self.log.record('extraction_normalized', phase='correction_candidate',
                                            source_id=paper.source_id, attempt=correction + 1,
                                            changes=changes)
                    # Keep changes/additions from a failed patch visible to the
                    # next correction; never restart from a truncated inventory.
                    candidate = merge_extraction_patch(candidate or rejected, rejected)
                except (ValueError, KeyError, TypeError) as error:
                    raise Rejected('candidate cannot support targeted correction') from error
                request = {**inputs, 'mode': 'targeted_correction',
                           'original_mode': inputs.get('mode'), 'candidate': candidate,
                           'validation_error': exc.feedback['error'],
                           'valid_page_bounds': {'paper_start': 1, 'paper_end': len(paper.pages),
                                                 'readable_pages': [p.page for p in pages]}}
                self.log.record('extraction_targeted_correction', source_id=paper.source_id,
                                candidate_hash=digest(canonical(candidate)), reason=exc.feedback['error'],
                                correction=correction + 1, correction_limit=corrections,
                                valid_page_bounds=request['valid_page_bounds'])
        raise AssertionError('unreachable')

    def _extract_paper(self, paper: Paper, *, salvaged=(), salvage_only=False) -> PaperExtraction:
        from ara.runtime.salvage import is_thin
        ranges = [entry['result'] for entry in salvaged]
        dispositions = []
        covered = {p for entry in salvaged for p in entry['pages']}
        def run(inputs, pages, prefix, existing=(), allow_incomplete=False, validate_context=None, single_pass=False):
            return self._extraction_response(paper, inputs, pages, prefix, existing,
                                             allow_incomplete, validate_context, single_pass)

        def segment(pages, *, refinement=False):
            inputs = {**paper.inputs(), 'pages': [dict(page=p.page, text=p.text) for p in pages]}
            prefix = f'r{pages[0].page}-{pages[-1].page}' + ('-refine' if refinement else '')
            self.log.record('extraction_range', source_id=paper.source_id, prefix=prefix,
                            pages=[p.page for p in pages], input_hash=digest(canonical(inputs)))
            try:
                result, new_gaps, _ = run(inputs, pages, prefix, allow_incomplete=True)
            except Rejected as exc:
                if not any(reason in str(exc) for reason in ('provider stop: max_tokens', 'extraction coverage incomplete')) or len(pages) == 1:
                    raise
                self.log.record('extraction_range_split', source_id=paper.source_id, prefix=prefix, reason=str(exc))
                mid = len(pages) // 2
                segment(pages[:mid], refinement=refinement); segment(pages[mid:], refinement=refinement)
                return
            obligations = record_new_obligations(self.log, paper.source_id, prefix, 1,
                                                 [p.page for p in pages], new_gaps)
            result = replace(result, obligations_json=canonical(obligations))
            ranges.append(result)
            covered.update(p.page for p in pages)
            save_immutable(self.log.path.parent / f'{paper.source_id}.{prefix}.rich.json', canonical(result.to_dict()))
            if is_thin(pages, result.items):
                if not refinement:
                    refine(pages)
                else:
                    dispositions.append(dict(kind='thin_range', pages=[p.page for p in pages],
                                             items=len(result.items), reason='Still thin after one split re-extraction.'))

        def refine(pages):
            self.log.record('extraction_thin_retry', source_id=paper.source_id, pages=[p.page for p in pages])
            mid = len(pages) // 2
            for half in (pages[:mid], pages[mid:]):
                try:
                    segment(half, refinement=True)
                except Exception as exc:
                    dispositions.append(dict(kind='thin_range', pages=[p.page for p in half],
                                             reason=f'Re-extraction failed; accepted evidence retained: {extraction_failure_reason(exc)}'))

        pending_thin = []
        for entry in salvaged:
            ids = entry['pages']
            pages = tuple(p for p in paper.readable_pages if p.page in ids)
            if is_thin(pages, entry['result'].items):
                # A richer accepted snapshot may already cover this same range.
                richer = {p for other in salvaged if not is_thin(other['pages'], other['result'].items)
                          for p in other['pages']}
                supported = [i for other in salvaged for i in other['result'].items
                             if i.page_start in ids and i.page_end in ids]
                if not is_thin(pages, supported):
                    dispositions.append(dict(kind='thin_range_filled_by_accepted_evidence', pages=ids,
                        reason='Accepted evidence from other ranges or review already exceeds the thin-range threshold.'))
                elif not set(ids) <= richer:
                    if entry.get('refined'):
                        dispositions.append(dict(kind='thin_range', pages=ids, reason='Still thin after the historical split re-extraction attempt.'))
                    else:
                        pending_thin.append(pages)
        if salvage_only:
            dispositions.extend(dict(kind='thin_range', pages=[p.page for p in pages],
                                     reason='Offline salvage; one split re-extraction remains due.') for pages in pending_thin)
        else:
            seen = set()
            for pages in pending_thin:
                key = tuple(p.page for p in pages)
                if key not in seen:
                    refine(pages)
                    seen.add(key)
        missing = tuple(p for p in paper.readable_pages if p.page not in covered)
        if missing and not salvage_only:
            try:
                for pages, _ in extraction_range_plan(self, replace(paper, pages=missing)):
                    segment(pages)
            except Exception as exc:
                if not ranges:
                    raise
                dispositions.append(dict(kind='range_extraction_failed', reason=f'{extraction_failure_reason(exc)}'))
        missing_ids = [p.page for p in paper.readable_pages if p.page not in covered]
        if missing_ids:
            dispositions.append(dict(kind='unextracted_pages', pages=missing_ids,
                                     reason='No accepted range covers these readable pages.'))
        if salvage_only or salvaged:
            items = tuple(i for r in ranges for i in r.items)
            unresolved = [o for r in ranges for o in json.loads(r.obligations_json)]
            resolutions = [v for r in ranges for v in json.loads(r.resolutions_json)]
            dispositions.append(dict(kind='reconciliation_not_repeated', reason='Accepted historical review output retained; offline salvage does not repeat review.'))
        else:
            from ara.runtime.reconciliation import reconcile
            items, unresolved, resolutions, review_dispositions = reconcile(self, paper, ranges, run)
            dispositions.extend(review_dispositions)
        require(len({item.id for item in items}) == len(items), 'duplicate merged extraction id')
        dispositions.extend(d for r in ranges for d in json.loads(r.dispositions_json))
        if self.config.get('extraction_require_inference', False) and not any(i.kind == 'inference' for i in items):
            dispositions.append(dict(kind='inference_coverage_unverified',
                                     reason='Accepted range union contains no inference nodes; no completeness claim.'))
        if any(d.get('kind') == 'no_explicit_inferential_structure' and any(
                i.kind == 'inference' and i.inference_origin == 'paper_stated' and
                any(i.page_start <= page <= i.page_end for page in d['pages']) for i in items)
                for d in dispositions):
            dispositions.append(dict(kind='inference_disposition_conflict',
                reason='Retained attempts disagree: a no-explicit-structure disposition overlaps accepted paper-stated inference evidence.'))
        result = PaperExtraction(paper.source_id, items, obligations_json=canonical(unresolved),
                                 resolutions_json=canonical(resolutions), dispositions_json=canonical(dispositions))
        self.log.record('extraction_graph_merged', source_id=paper.source_id, ranges=len(ranges),
                        items=len(items), graph_hash=digest(canonical(result.to_dict())))
        return result

    def build_t(self, literature: str, audience: str) -> CommitmentSet:
        allowed = citation_ids(literature)
        if allowed is not None:
            require(bool(allowed), 'no extracted claims available to build T')
            from ara.runtime.construction import construct
            return construct(self, literature, audience)
        require(not self.config.get('construction_gap_anchors') and not self.config.get('construction_context_limits'),
                'construction gap anchors and context limits require rich extracted literature')
        return self.call('build_t', {'literature': literature, 'audience': audience}, CommitmentSet.from_dict)

    def search_vocabulary(self, commitments):
        from ara.runtime.search_alignment import catalogue_inputs
        vocabulary = catalogue_inputs(self.log.path.parent, commitments)
        events = self.log.read()
        if any(e['stage'] == 'commitments_frozen' for e in events):
            from ara.runtime.route_policy import provenance_from_events
            require(vocabulary['commitment_provenance'] == provenance_from_events(events, commitments),
                    'search commitment provenance receipt mismatch')
        return vocabulary

    def discover_gaps(self, commitments):
        from ara.runtime.gaps import detect_gaps
        from ara.runtime.semantic_conflicts import classify_pairs
        vocabulary = self.search_vocabulary(commitments)
        from ara.runtime.external_gaps import load_external_gaps
        external = load_external_gaps(self, commitments, vocabulary)
        detection = detect_gaps(commitments, vocabulary['symbol_catalogue'], vocabulary['commitment_provenance'])
        from ara.runtime.conflict_feedback import support_conflict_gaps
        support_gaps = support_conflict_gaps(self.log.read(), commitments, vocabulary['commitment_provenance'])
        return {**detection, 'gaps': external + detection['gaps'] + support_gaps + classify_pairs(self, commitments, vocabulary)}

    def propose_targets(self, commitments: CommitmentSet, count: int = 30,
                        named_position: str | None = None) -> tuple[Proposition, ...]:
        require(type(count) is int and count > 0, 'target count must be positive')
        vocabulary = self.search_vocabulary(commitments)
        detection = self.discover_gaps(commitments)
        self.log.record('gaps_detected', **{k:v for k,v in detection.items() if k != 'gaps'},
                        gaps=[g.to_dict() for g in detection['gaps']],
                        commitments_sha256=vocabulary['commitments_sha256'],
                        provenance_sha256=vocabulary['provenance_sha256'])
        if named_position is not None or not detection['gaps']:
            return self._propose_target_pool(commitments, count, named_position)
        kept = list(self.propose_gap_targets(commitments, detection['gaps'], count))
        formulas = {t.formula.canonical() for t in kept}
        if len(kept) < min(count,30):
            for target in self._propose_target_pool(commitments, min(count,30)):
                key = target.formula.canonical()
                if len(kept) < min(count,30) and key not in formulas and target.id not in {t.id for t in kept}:
                    kept.append(target)
                    formulas.add(key)
        self.log.record('gap_target_pool_finished', keep_limit=min(count,30),
                        kept=[t.to_dict() for t in kept], gaps_considered=len(detection['gaps']))
        return tuple(kept)

    def propose_gap_targets(self, commitments, gaps, count=30):
        require(type(count) is int and count > 0, 'target count must be positive')
        kept, formulas = [], set()
        for gap in gaps:
            candidates = self._propose_target_pool(commitments, min(count,30), resolution_gap=gap)
            for target in candidates:
                key = target.formula.canonical()
                if len(kept) < min(count,30) and key not in formulas:
                    kept.append(target)
                    formulas.add(key)
        return tuple(kept)

    def _propose_target_pool(self, commitments, count, named_position=None, *, resolution_gap=None):
        from ara.runtime.search_alignment import symbols
        vocabulary = self.search_vocabulary(commitments)
        from ara.runtime.target_policy import target_context, trivial_targets, classifier_inputs
        from ara.runtime.contribution import formula_hash
        require(type(count) is int and count > 0, 'target count must be positive')
        keep_count = 1 if named_position is not None else min(count, 30)
        pool_count = 1 if named_position is not None else 30
        def check(data):
            targets = tuple(Proposition.from_dict(p) for p in data['targets'])
            require(1 <= len(targets) <= pool_count, 'target pool outside requested bounds')
            require(len({p.id for p in targets}) == len(targets), 'duplicate target id')
            if named_position is not None:
                require(targets[0].text == named_position, 'named position was changed')
            return targets
        inputs = dict(commitments=commitments.to_dict(), count=pool_count, keep_count=keep_count,
                      attempt=1, attempt_budget=3, named_position=named_position,
                      **vocabulary, **target_context(commitments, load_bank(self.root / 'bank')))
        from ara.runtime.synthesis import proposal_forward_candidates
        inputs['forward_candidates'] = proposal_forward_candidates(self, commitments, vocabulary)
        target_bases = {Formula.from_dict(c['formula']).canonical(): tuple(c['support_ids']) for c in inputs['forward_candidates']}
        if resolution_gap is not None:
            inputs.update(resolution_gap=resolution_gap.to_dict(),
                resolution_instruction='Propose a new resolving thesis: a distinction, restriction or bridge addressing this gap. Support it by bank schemes using endorsed T from every support group. Empty groups mean no admissible evidence. All novelty and stance gates still apply. External AI findings are hypotheses, not source endorsements. Preserve their search scope, currency verdict, evidence qualifications and exact claim_framing; never claim exhaustive absence.')
        frozen = set().union(*(set(symbols(c.formula)) for c in commitments.commitments))
        kept, kept_ids, kept_formulas = [], set(), set()
        for attempt in range(3):
            targets = self.call('propose_targets', inputs, check)
            if resolution_gap is not None:
                targets = tuple(replace(p, id=resolution_gap.id + ':' + p.id, gap=resolution_gap) for p in targets)
            targets = tuple(p if p.formula else replace(p, formula=self.formalise(p, commitments=commitments))
                            for p in targets)
            disconnected = [p.id for p in targets if not set(symbols(p.formula)) & frozen]
            self.log.record('target_vocabulary_preflight', attempt=attempt + 1, attempt_budget=3,
                            disconnected=disconnected, catalogue_sha256=vocabulary['catalogue_sha256'],
                            catalogue_status=vocabulary['catalogue_status'],
                            status='disconnected' if disconnected else 'aligned',
                            note='New thesis vocabulary is advisory, not a rejection; native bank licensing and CQ support decide reachability.')
            receipts = []
            rejected = trivial_targets(targets, commitments, vocabulary['symbol_catalogue'], receipts,
                                       vocabulary['commitment_provenance'], target_bases)
            for receipt in receipts:
                self.log.record('target_contribution_preflight', attempt=attempt + 1, **receipt)
            for target in targets:
                content = classifier_inputs(target, vocabulary, commitments)
                self.log.record('target_lexical_attribution', target_id=target.id, attempt=attempt + 1,
                                hits=content['lexical_attribution_hits'], policy='advisory')
                for issue in content['definition_issues']:
                    rejected.append(dict(target_id=target.id, target=target.to_dict(), **issue,
                                         explanation='Proposed content must bind a fresh assertion, not rename frozen content.'))
                classification = self.call('classify_target', content, lambda d: d)
                self.log.record('target_own_thesis_classification', target_id=target.id,
                                attempt=attempt + 1, **classification)
                if target.gap is not None and classification.get('resolves_gap') is not True:
                    rejected.append(dict(target_id=target.id, target=target.to_dict(),
                        reason='gap_resolution_not_established', explanation=classification['reason']))
                if classification['novelty'] != 'new_assertion' or classification['fidelity'] != 'matches':
                    rejected.append(dict(target_id=target.id, target=target.to_dict(), reason='target_content_not_established',
                                         novelty=classification['novelty'], fidelity=classification['fidelity'],
                                         explanation=classification['reason']))
                if classification['classification'] != 'own_thesis':
                    rejected.append(dict(target_id=target.id, target=target.to_dict(), reason='own_thesis_not_established',
                                         classification=classification['classification'], explanation=classification['reason']))
            for index, target in enumerate(targets):
                reasons = [r for r in rejected if r['target_id'] == target.id]
                key = formula_hash(target.formula)
                if reasons:
                    disposition = 'rejected'
                elif target.id in kept_ids or key in kept_formulas:
                    disposition = 'duplicate'
                    rejected.append(dict(target_id=target.id, target=target.to_dict(), reason='duplicate_retained_target',
                                         explanation='Use a distinct ID and formula; this target was already retained.'))
                elif len(kept) >= keep_count:
                    disposition = 'over_limit'
                else:
                    disposition = 'kept'
                    kept.append(target)
                    kept_ids.add(target.id)
                    kept_formulas.add(key)
                self.log.record('target_pool_candidate', attempt=attempt + 1, index=index,
                                target=target.to_dict(), disposition=disposition,
                                reasons=[r for r in rejected if r['target_id'] == target.id])
            self.log.record('target_triviality_preflight', attempt=attempt + 1, attempt_budget=3,
                            rejected=rejected, status=('rejected_after_two_corrections' if attempt == 2 else 'correction_required')
                            if rejected else 'passed',
                            requested_pool=pool_count, received_pool=len(targets), underfilled=len(targets) < pool_count,
                            note='Bounded solver contribution and isolated own-thesis classification; semantic originality and text/formula fidelity remain unproved.')
            if len(kept) >= keep_count:
                break
            inputs = {**inputs, 'attempt': attempt + 2, 'retained_targets': [p.to_dict() for p in kept],
                'triviality_feedback': dict(rejected=rejected, previous_targets=[p.to_dict() for p in targets],
                    instruction='Propose new main claims needing at least two frozen supports through supplied bank schemes. Repair the concrete witness, not just the wording; do not repeat retained targets.')}
        self.log.record('target_pool_finished', attempts=attempt + 1, attempt_budget=3,
                        requested_pool=pool_count, keep_limit=keep_count, kept=[p.to_dict() for p in kept])
        return tuple(kept)

    def propose_cuts(self, goal: Proposition, commitments: CommitmentSet,
                     bank: tuple[BankEntry, ...], *, feedback: tuple[dict, ...] = ()) -> tuple[Proposal, ...]:
        from ara.runtime.search_alignment import slot_bindings, search_guidance
        from ara.runtime.bridges import proposal_bridge
        vocabulary = self.search_vocabulary(commitments)
        def check(data):
            proposals = tuple(Proposal.from_dict(p) for p in data['proposals'])
            require(len(proposals) <= 3, 'proposal batch exceeds three candidates')
            require(len({p.to_json() for p in proposals}) == len(proposals), 'duplicate proposal in batch')
            for proposal in proposals:
                slot_bindings(proposal, commitments)
                require(proposal.conclusion_text == goal.text,
                        'current-goal reference text mismatch')
            # Exact existing text is an identity binding, never a semantic similarity decision.
            return tuple(replace(p, conclusion_ref='current_goal') for p in proposals)
        inputs = dict(goal=goal.to_dict(), commitments=commitments.to_dict(),
                      bank=[b.to_dict() for b in bank], proposal_limit=3, attempt_budget=2,
                      attempt=2 if feedback else 1, rejection_feedback=list(feedback),
                      **vocabulary, **search_guidance(goal, commitments, bank, vocabulary['commitment_provenance']))
        try:
            proposals = self._transport_call('propose_cuts', inputs, check, attempt=inputs['attempt'])
        except InvalidOutput as exc:
            raise RejectedCutBatch(str(exc)) from exc
        for index,proposal in enumerate(proposals):
            self.log.record('proposal_bridge', goal_id=goal.id, attempt=inputs['attempt'], proposal_index=index,
                            **proposal_bridge(proposal,vocabulary))
        return proposals

    def formalise(self, proposition: Proposition, *, commitments=None) -> Formula:
        inputs = {'proposition': proposition.to_dict()}
        if commitments is not None:
            inputs.update(self.search_vocabulary(commitments))
            inputs['vocabulary_instruction'] = 'Reuse catalogue definitions and signatures; preserve the proposition meaning.'
        return self.call('formalise', inputs, lambda d: Formula.from_dict(d['formula']))

    def formalise_slots(self, proposal, goal, entry, commitments):
        from ara.runtime.search_alignment import slot_bindings, validate_slots, metavariable_bindings
        bindings = slot_bindings(proposal, commitments)
        vocabulary = self.search_vocabulary(commitments)
        inputs = dict(proposal=proposal.to_dict(), goal=goal.to_dict(), bank_entry=entry.to_dict(),
                      slot_bindings=bindings,
                      shared_metavariables=metavariable_bindings(entry, goal, bindings),
                      **vocabulary)
        return self.call('formalise_slots', inputs,
                         lambda d: validate_slots(d, proposal, entry, bindings, vocabulary['symbol_catalogue']))

    def map_leaf(self, leaf: Proposition, commitments: CommitmentSet) -> str:
        def check(data):
            require(data['t_id'] == 'open' or commitments.get(data['t_id']) is not None, 'unknown T id')
            return data['t_id']
        from ara.runtime.search_alignment import search_guidance
        vocabulary = self.search_vocabulary(commitments)
        return self.call('map_leaf', dict(leaf=leaf.to_dict(), commitments=commitments.to_dict(),
                         **vocabulary,
                         **search_guidance(leaf, commitments, load_bank(self.root / 'bank').entries, vocabulary['commitment_provenance'])), check)

    def answer_cq(self, question: CriticalQuestion, proposal: Proposal,
                  commitments: CommitmentSet) -> CQAnswer:
        vocabulary = self.search_vocabulary(commitments)
        provenance = vocabulary['commitment_provenance']
        def check(data):
            answer = CQAnswer.from_dict(data)
            require(answer.cq_id == question.id, 'wrong CQ id')
            require(all(commitments.get(t) is not None for t in answer.supporting_t_ids), 'unknown CQ T id')
            from ara.engine.routes import partial_cq
            if answer.answered and partial_cq(answer.answer):
                self.log.record('cq_answer_downgraded', bank_id=proposal.bank_id,
                                original=answer.to_dict(), reason='partial_answer_is_not_yes')
                answer = replace(answer, answered=False)
            require(provenance is None or all(provenance['commitments'][t]['stance'] != 'model_alignment'
                    for t in answer.supporting_t_ids), 'alignment premises cannot substitute for source CQ evidence')
            return answer
        return self.call('answer_cq', dict(question=question.to_dict(), proposal=proposal.to_dict(),
                                      commitments=commitments.to_dict(), **vocabulary), check)

    def repair_tier1(self, premises: tuple[PremiseFill, ...], conclusions: tuple[Proposition, ...],
                     commitments: CommitmentSet) -> Tier1Repair:
        return self.call('tier1_repair', {'premises': [p.to_dict() for p in premises],
                         'conclusions': [p.to_dict() for p in conclusions],
                         'commitments': commitments.to_dict()}, Tier1Repair.from_dict)

    def essay_outline(self, route: RouteGraph) -> dict:
        """Project essay content, retaining ids only as references and markers."""
        bank = load_bank(self.root / 'bank')
        links = []
        for node in route.nodes:
            if node.kind != 'inference':
                continue
            require(node.proposal is not None, 'outline inference has no proposal')
            entry = bank.get(node.proposal.bank_id)
            require(entry is not None, 'outline inference has unknown bank entry')
            fills = {p.slot: p.text for p in node.proposal.premises}
            fills[entry.conclusion_slot.id] = node.proposition.text
            questions = {q.id: q.template for q in entry.critical_questions}
            answered = []
            for answer in node.cq_answers:
                if answer.answered and answer.answer.strip():
                    require(answer.cq_id in questions, 'outline answer has unknown question')
                    answered.append({'question': questions[answer.cq_id].format_map(fills),
                                     'answer': answer.answer})
            link = {'premises': list(node.children), 'conclusion': node.id,
                    'scheme': entry.name, 'answered_questions': answered}
            # Assumption discharge is part of the argument, unlike scope ids.
            scopes = [scope for scope in route.scopes if scope.discharged_by == node.id]
            if scopes:
                link['assumptions'] = [scope.assumption_node_id for scope in scopes]
                link['scoped_results'] = [n for scope in scopes for n in scope.result_node_ids]
            links.append(link)
        outline = {'nodes': [{'id': n.id, 'text': n.proposition.text} for n in route.nodes],
                   'links': links}
        root_gap = next(n.proposition.gap for n in route.nodes if n.id == route.root_id)
        if root_gap is not None:
            outline['gap_resolution'] = root_gap.to_dict()
        from ara.runtime.route_policy import frozen_from_events
        frozen = frozen_from_events(self.log.read())
        provenance = self.search_vocabulary(frozen)['commitment_provenance'] if frozen is not None else None
        if provenance is not None:
            roles = []
            for node in route.nodes:
                uses = [(node.t_id, 'global_premise')] if node.kind == 'leaf' and node.t_id != 'open' else []
                uses += [(tid, 'cq_evidence') for a in node.cq_answers for tid in a.supporting_t_ids]
                if node.kind == 'assumption' and node.proposition.formula is not None:
                    uses += [(c.id, 'scoped_hypothesis') for c in frozen.commitments
                             if c.formula.canonical() == node.proposition.formula.canonical()]
                for tid, role in sorted(set(uses)):
                    source = provenance['commitments'].get(tid)
                    require(source is not None, 'outline source role missing frozen commitment')
                    roles.append(dict(node_id=node.id, evidence_id=tid,
                                      role='alignment_premise' if source['stance']=='model_alignment' and role=='global_premise' else role,
                                      stance=source['stance'], attributed_to=source.get('attributed_to'),
                                      source_id=source['source_id']))
            outline['source_roles'] = roles
            if 'alignment' in provenance:
                from ara.runtime.symbol_alignment import alignment_disclosure
                outline['alignment_disclosure'] = alignment_disclosure(provenance)
        return outline

    def essay_inputs(self, route: RouteGraph) -> dict:
        from ara.runtime.proposal import from_events
        proposal = from_events(self.log.read(), route.id)
        return {**({'proposal': proposal} if proposal else {}), 'outline': self.essay_outline(route), 'word_limit': min(6000, self.config['essay_word_limit']),
                'minimum_words': self.config['essay_min_words'],
                'feedback': [json.loads(e['payload_json'])['text'] for e in self.log.read()
                             if e['label'] == 'HUMAN' and e['stage'] == 'feedback']}

    def validate_essay(self, route: RouteGraph, data: dict, *, minimum_words: int | None = None) -> dict:
        validate_local(self.response_schema('write_essay', {}), data, self.config)
        from ara.runtime.proposal import from_events, validate_disclosure
        validate_disclosure(from_events(self.log.read(), route.id), data)
        require(word_count(data) <= min(6000, self.config['essay_word_limit']), 'essay word limit exceeded')
        require(len({b['id'] for b in data['bibliography']}) == len(data['bibliography']), 'duplicate citation id')
        markers = set(re.findall(r'\[\[node:([^\]]+)\]\]', data['body']))
        require(markers == {node.id for node in route.nodes}, 'essay writer: node marker coverage mismatch')
        body = re.sub(r'\[\[node:[^\]]+\]\]|\[cite:[^\]]+\]', '', data['body'])
        text_tokens = [token for token in body.split() if any(char.isalnum() for char in token)]
        require(len(text_tokens) >= 2, 'essay writer: body needs at least two text tokens')
        minimum = self.config['essay_min_words'] if minimum_words is None else minimum_words
        require(word_count(data) >= minimum,
                'essay writer: minimum words not reached')
        return data

    def write_essay(self, route: RouteGraph) -> dict:
        def check(data):
            from ara.runtime.proposal import retain_disclosure
            data = retain_disclosure(self, route, data, phase='composition')
            return self.validate_essay(route, data)
        if self.config['essay_min_words'] >= 4500 or 'proposal' in self.essay_inputs(route):
            from ara.runtime.writing import sectioned_essay
            return sectioned_essay(self, route, self.essay_inputs(route), check)
        return self.call('write_essay', self.essay_inputs(route), check)

    def audit_inputs(self, route: RouteGraph, draft: dict, *, publication_context=None) -> dict:
        from ara.runtime.essay_audit import sentence_spans, NODE
        spans = sentence_spans(draft['body'], literature=publication_context is not None)
        parts = [NODE.sub('', draft['body'][start:end]).strip() for start, end in spans]
        inputs = {'sentences': [{'sentence': i, 'text': text} for i, text in enumerate(parts, 1)],
                  'outline': self.essay_outline(route),
                  'root_conclusion': {'node_id': route.root_id,
                                      'text': next(n.proposition.text for n in route.nodes if n.id == route.root_id)}}
        from ara.runtime.proposal import from_events, validate_disclosure
        proposal = from_events(self.log.read(), route.id)
        if proposal:
            validate_disclosure(proposal, draft)
            inputs['proposal'] = proposal
        if proposal or publication_context is not None or self.config['essay_min_words'] >= 4500 or any(
                e['stage'] == 'commitment_provenance_frozen' for e in self.log.read()):
            from ara.runtime.writing import source_context
            inputs['source_evidence'] = source_context(self, route)
        if publication_context is not None:
            from ara.runtime.publication_audit import sentence_sections
            inputs['publication_context'] = publication_context
            for sentence, section, (start, end) in zip(inputs['sentences'], sentence_sections(draft['body'], spans), spans):
                sentence.update(section=section, field='body', start=start, end=end)
            inputs['sentences'].append(dict(sentence=len(spans)+1, text=draft['title'],
                section='Title', field='title', start=0, end=len(draft['title'])))
        if proposal and publication_context is None:
            inputs['sentences'].append(dict(sentence=len(spans)+1, text=draft['title']))
        return inputs

    def audit_essay(self, route: RouteGraph, draft: dict, *, publication_context=None, fresh=False) -> dict:
        from ara.runtime.essay_audit import audit_result
        inputs = self.audit_inputs(route, draft, publication_context=publication_context)
        kind = 'audit_publication' if publication_context is not None else 'audit_essay'
        def check(data):
            result = audit_result(route, draft, inputs, data)
            self.log.record('essay_audit', route_id=route.id,
                            prompt_sha256=digest(self.render(kind, inputs)[1]), **result)
            if not result['faithful']:
                raise EssayAuditFailed(result, inputs, data['labels'])
            return result
        return self.call(kind, inputs, check, fresh=fresh)


    def search_evidence(self, draft: dict, items: list[dict]) -> dict:
        return self.call('search_evidence', {'draft': draft, 'items': items})

    @staticmethod
    def verification_items(draft: dict) -> list[dict]:
        items = [{'id': b['id'], 'kind': 'citation', 'text': b['text']} for b in draft['bibliography']]
        quotations = re.findall(r'"([^"\n]+)"|“([^”]+)”', draft['body'])
        items.extend({'id': f'quote:{i}', 'kind': 'quotation', 'text': a or b}
                     for i, (a, b) in enumerate(quotations))
        require(len({i['id'] for i in items}) == len(items), 'duplicate verification id')
        return items

    def verify_originality_citations(self, draft: dict) -> tuple[dict, dict]:
        from ara.runtime.citations import local_verdicts
        all_items = self.verification_items(draft)
        local = local_verdicts(self, draft, all_items)
        items = [item for item in all_items if item['id'] not in local]
        evidence = self.search_evidence(draft, items)
        def check(data):
            expected = {i['id']: i for i in items}
            require(len(data['items']) == len(items) and {i['id'] for i in data['items']} == set(expected),
                    'verification omitted or invented items')
            for item in data['items']:
                require(all(item[k] == expected[item['id']][k] for k in ('kind', 'text')), 'verification changed item')
                require(set(item['evidence_urls']) <= set(evidence['urls']), 'unsupported verification URL')
                if item['status'] == 'verified':
                    require(bool(item['evidence_urls']), 'verified without evidence')
                    if item['kind'] == 'quotation':
                        # Prefer URL-bound API excerpts. Some transports return
                        # empty citation arrays; then the classifier must extract
                        # a passage from the search evidence. Attribution remains
                        # model-assessed; wording is checked locally, never fuzzy.
                        quote = ' '.join(item['text'].split())
                        excerpts = [v['cited_text'] for v in walk(evidence['content'])
                                    if isinstance(v, dict) and
                                    v.get('type') == 'web_search_result_location' and
                                    v.get('url') in item['evidence_urls'] and
                                    isinstance(v.get('cited_text'), str)]
                        if not excerpts:
                            extracted = item.get('source_excerpt')
                            if extracted and ' '.join(extracted.split()) in ' '.join(evidence['text'].split()):
                                excerpts = [extracted]
                        exact = any(re.search(r'(?<!\w)' + re.escape(quote) + r'(?!\w)',
                                              ' '.join(text.split())) for text in excerpts)
                        if not exact:
                            item.update(status='unverified', action='remove',
                                        detail='No exact quotation in the cited source excerpts.')
            originality = data['originality']
            require(set(originality['evidence_urls']) <= set(evidence['urls']), 'unsupported originality URL')
            require(originality['assessment'] == 'unverified' or bool(originality['evidence_urls']),
                    'originality requires search evidence')
            return data
        result = self.call('verify_originality_citations', {'draft': draft, 'items': items, 'evidence': evidence}, check)
        remote = {item['id']: item for item in result['items']}
        result = {**result, 'items': [local[item['id']] if item['id'] in local else remote[item['id']]
                                     for item in all_items]}
        cleaned = json.loads(canonical(draft))
        removed = []
        removal_reasons = []
        for item in result['items']:
            if item['status'] == 'unverified':
                removed.append(item['id'])
                removal_reasons.append(dict(id=item['id'], reason=item.get('removal_reason', item['detail']),
                                            basis=item.get('verification_basis', 'web_evidence')))
                cleaned['body'] = cleaned['body'].replace(item['text'], '')
                if item['kind'] == 'citation':
                    cleaned['bibliography'] = [b for b in cleaned['bibliography'] if b['id'] != item['id']]
                    cleaned['body'] = cleaned['body'].replace(f'[cite:{item["id"]}]', '')
                else:
                    cleaned['body'] = cleaned['body'].replace('""', '').replace('“”', '')
            elif item.get('verification_basis') == 'local_frozen_T' and item['kind'] == 'citation':
                cleaned['bibliography'] = [item['local_evidence']['bibliography'] if b['id'] == item['id'] else b
                                           for b in cleaned['bibliography']]
        self.log.record('verification_cleanup', removed_ids=removed, removal_reasons=removal_reasons,
                        draft=cleaned, verification=result)
        return cleaned, result
