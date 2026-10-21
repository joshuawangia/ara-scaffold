"""The single model boundary: prompt, reserve, call, validate, log, cache."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from dataclasses import replace
from typing import Callable, Any

from jsonschema import Draft202012Validator, ValidationError

from ara.bank import load_bank
from ara.runtime.budget import Budget, BudgetStop, UnpricedModel
from ara.runtime.cache import Cache, cache_key, canonical, digest
from ara.runtime.logging import EventLog, now
from ara.runtime.extraction import Paper, PaperExtraction, ExtractedItem, citation_ids, save_immutable, extraction_range_plan, record_new_obligations
from ara.runtime.providers import Provider, Response, stage_settings
from ara.types import (BankEntry, CommitmentSet, CQAnswer, CriticalQuestion, Formula,
                       PremiseFill, Proposal, Proposition, RouteGraph, RunEvent,
                       Tier1Repair, TokenUsage)


class Rejected(ValueError):
    pass


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
    merged = {**patch, 'items': [updates.pop(id, item) for id, item in old.items()]}
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


class ModelCalls:
    def __init__(self, config: dict, provider: Provider, log: EventLog, cache: Cache,
                 root: Path, topic: str):
        self.config, self.provider, self.log, self.cache = config, provider, log, cache
        self.root, self.topic = Path(root), topic
        self.budget = Budget(config, log)
        self._paper_budget = None

    def requested_model(self, kind: str) -> str:
        return self.provider.model_for(kind) if hasattr(self.provider, 'model_for') else self.provider.model

    def response_schema(self, kind: str, inputs: dict) -> dict | None:
        if kind == 'search_evidence':
            return None
        schema = json.loads((self.root / 'schemas' / f'{kind}.json').read_text())
        if kind == 'extract_paper':
            mode = inputs.get('original_mode') if inputs.get('mode') == 'targeted_correction' else inputs.get('mode')
            reconciliation = mode == 'reconcile_ranges'
            if not reconciliation or not inputs.get('obligations'):
                for field in ('context_request', 'pending_obligation_ids', 'resolutions'):
                    del schema['properties'][field]
            if reconciliation:
                del schema['properties']['empty_reason']
            elif inputs.get('mode') == 'targeted_correction':
                # Patch items may be empty while the resulting graph is nonempty.
                if inputs.get('candidate', {}).get('items'):
                    schema['properties']['empty_reason'] = {'type': 'null'}
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
        template = (self.root / 'prompts' / f'{kind}.txt').read_text()
        if kind != 'search_evidence':
            # The service grammar is a compact projection. Show the model every
            # local constraint as well; the same complete prompt is logged/keyed.
            schema = self.response_schema(kind, inputs)
            template += '\nLOCAL_RESPONSE_SCHEMA (all constraints are mandatory)\n' + canonical(schema)
        # JSON input is data, never interpreted as a format template.
        return template, template + '\nINPUT_JSON\n' + canonical({'topic': self.topic, **inputs})

    def call(self, kind: str, inputs: dict, check: Callable[[dict], Any] | None = None) -> Any:
        attempts = self.config.get('validation_attempts', 1)
        if type(attempts) is not int or not 1 <= attempts <= 3:
            raise ValueError('validation_attempts must be between 1 and 3')
        if kind == 'write_essay':
            attempts = 4
        request_inputs = inputs
        for attempt in range(attempts):
            try:
                return self._call_once(kind, request_inputs, check, attempt=attempt + 1)
            except InvalidOutput as exc:
                if attempt + 1 == attempts:
                    raise
                self.log.record('validation_retry', kind=kind, next_attempt=attempt + 2,
                                reason=str(exc))
                if kind != 'write_essay':
                    request_inputs = {**inputs, 'validation_feedback': exc.feedback}
        raise AssertionError('unreachable')

    def _call_once(self, kind: str, inputs: dict, check: Callable[[dict], Any] | None = None, *, attempt: int = 1, schema_smoke: bool = False) -> Any:
        offset = len(self.log.read())
        before_tokens, before_cost = self.budget.used_tokens, self.budget.used_cost
        started = time.monotonic()
        try:
            return self._execute_once(kind, inputs, check, attempt=attempt, schema_smoke=schema_smoke)
        except Exception as exc:
            events = self.log.read()[offset:]
            starts = [e for e in events if e['stage'] == 'call_start']
            completed = [e for e in events if e['label'] == 'MODEL']
            if not starts or completed:
                raise
            received = [json.loads(e['payload_json']) for e in events if e['stage'] == 'response_received']
            if received:
                receipt = received[-1]
                self._event(kind, json.loads(starts[-1]['payload_json'])['prompt'], receipt['raw_response'],
                            TokenUsage.from_dict(receipt['measured_usage']), receipt['measured_cost_usd'],
                            started, False, 'rejected', type(exc).__name__, receipt['cache_key'], attempt=attempt)
                self.budget.stop('post-response failure; measured usage retained', kind)
            # Any unrecorded dispatched result is incomplete. Do not serialize the
            # suspect raw response again, and replace any in-memory actual charge.
            admission = json.loads(starts[-1]['payload_json'])
            usage = TokenUsage.from_dict(admission['reserved_usage'])
            cost = self.budget.cost(usage, model=self.requested_model(kind))
            self.budget.used_tokens, self.budget.used_cost = before_tokens, before_cost
            self.budget.charge(usage, cost)
            self.log.emit(RunEvent(now(), kind, 'MODEL', self.requested_model(kind), None,
                admission['prompt'], None, usage, float(cost), time.monotonic() - started,
                payload_json=canonical({'status': 'incomplete', 'attempt': attempt, 'reason': type(exc).__name__,
                    'cache_hit': False, 'cache_key': admission['cache_key'],
                    'accounting': 'reservation_unknown_actual',
                    **({'source_id': self._paper_budget.source_id} if kind == 'extract_paper' and self._paper_budget else {})})))
            self.budget.after(kind)
            self.budget.stop('provider result incomplete; reservation charged; actual spend unknown', kind)

    def _execute_once(self, kind: str, inputs: dict, check: Callable[[dict], Any] | None = None, *, attempt: int = 1, schema_smoke: bool = False) -> Any:
        template, prompt = self.render(kind, inputs)
        schema = self.response_schema(kind, inputs)
        maximum = self.config.get(f'{kind}_max_output_tokens', self.config['max_output_tokens'])
        if kind == 'build_t_batch':
            maximum = self.config['extracted_build_t_max_output_tokens']
        identity = canonical({'inputs': inputs, 'topic': self.topic, 'provider': type(self.provider).__name__,
                              'effort': stage_settings(self.config, kind)['effort'], 'maximum': maximum,
                              'thinking': stage_settings(self.config, kind).get('thinking', 'adaptive'),
                              'web_max': self.config['web_search_max_uses'],
                              'formula_depth': self.config.get('formula_output_depth', 2),
                              'fallbacks': stage_settings(self.config, kind).get('fallbacks', ['claude-opus-4-8'])})
        if schema_smoke:
            prompt = 'P. Return a JSON object matching the response schema.'
            maximum = 1
        key = cache_key(kind, template, identity, self.requested_model(kind), schema or {})
        saved = None
        if not schema_smoke:
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
                estimate = self.count_request(kind, inputs, maximum=maximum, admission=True)
            if not cached:
                self.budget.before(estimate, kind, model=self.requested_model(kind))
            if kind == 'extract_paper' and self._paper_budget is not None:
                self._paper_budget.before(estimate, cached=cached)
            if cached:
                raw = saved['raw']
                self.budget.response_cost(raw)  # Cached responses retain validated model/pricing provenance.
            else:
                self.log.record('call_start', kind=kind, attempt=attempt, model=self.requested_model(kind), prompt=prompt,
                                schema=schema, reserved_usage=estimate.to_dict(), cache_key=key)
                dispatched = True
                raw = self.provider.complete(kind, prompt, schema, maximum).raw
                usage = Response(raw).usage
                require(all(type(n) is int and n >= 0 for n in usage.to_dict().values()), 'invalid usage')
                cost = self.budget.response_cost(raw)
                self.budget.charge(usage, cost)
                charged = True
                # Durable before parsing or follow-up token-counter/network validation.
                self.log.record('response_received', kind=kind, cache_key=key,
                                requested_model=self.requested_model(kind), raw_response=raw,
                                measured_usage=usage.to_dict(), measured_cost_usd=float(cost))
            # Stop reason is checked BEFORE interpreting any content blocks.
            if schema_smoke:
                require(raw['stop_reason'] in ('end_turn', 'max_tokens'), f'provider stop: {raw["stop_reason"]}')
            else:
                require(raw['stop_reason'] == 'end_turn', f'provider stop: {raw["stop_reason"]}')
            require(not any(isinstance(v, dict) and (v.get('is_error') or
                        str(v.get('type', '')).endswith('_error') or v.get('error_code'))
                        for v in walk(raw['content'])), 'server tool error')
            if schema_smoke:
                data = {'grammar_accepted': True}
            elif schema is None:
                urls = sorted({v['url'] for v in walk(Response(raw).served_content) if isinstance(v, dict)
                               and v.get('type') == 'web_search_result' and isinstance(v.get('url'), str)})
                data = {'text': Response(raw).text(), 'urls': urls, 'content': Response(raw).served_content}
                require(bool(data['text']), 'empty evidence response')
            else:
                validating = True
                data = json.loads(Response(raw).text())
                if kind == 'build_t_batch' and isinstance(data, dict) and isinstance(data.get('commitments'), list):
                    for item in data['commitments']:
                        if isinstance(item, dict) and isinstance(item.get('formula'), str):
                            try:
                                item['formula'] = json.loads(item['formula'])
                            except json.JSONDecodeError as exc:
                                raise Rejected('invalid encoded formula JSON') from exc
                if kind == 'extract_paper' and isinstance(data, dict):
                    changes = normalize_extraction(data)
                    if changes:
                        self.log.record('extraction_normalized', cache_key=key, changes=changes,
                                        source_id=inputs.get('source_id'), attempt=attempt)
                    extraction_defaults(data)
                Draft202012Validator(schema).validate(data)
            result = check(data) if check else data
        except Exception as exc:
            if not charged and isinstance(exc, BudgetStop):
                raise
            if not validating:
                from ara.runtime.providers import provider_error_evidence
                self.log.record('provider_error', kind=kind, **provider_error_evidence(exc, prompt))
            # Provider exception messages can embed HTTP credentials. Store only
            # their class; model responses and local validation remain in full.
            reason = str(exc) if isinstance(exc, (Rejected, UnpricedModel)) else type(exc).__name__
            if kind == 'extract_paper' and isinstance(exc, ValidationError):
                reason = f'ValidationError at /{"/".join(map(str, exc.absolute_path))}: {exc.validator} constraint failed'
                if exc.context:
                    reason += '; ' + '; '.join(
                        f'/{"/".join(map(str, error.absolute_path))}: {error.validator}'
                        for error in exc.context)
            unknown_usage = dispatched and not charged
            if unknown_usage:
                usage, cost = estimate, self.budget.cost(estimate, model=self.requested_model(kind))
                self.budget.charge(usage, cost)
            self._event(kind, prompt, raw, usage, cost, start, cached, 'incomplete' if unknown_usage else 'rejected', reason, key, unknown_usage, attempt=attempt)
            if unknown_usage:
                self.budget.after(kind)
                self.budget.stop(f'provider accounting unavailable ({reason}); reservation charged; actual spend unknown', kind)
            self._after(kind)
            if not isinstance(exc, (Rejected, ValueError, ValidationError)):
                self.log.record('validation_failed', kind=kind, reason=type(exc).__name__, cache_key=key)
                raise
            if validating and not (kind == 'audit_essay' and isinstance(exc, Rejected)):
                raise InvalidOutput(reason, {'error': reason if kind == 'extract_paper' else str(exc),
                    'rejected_response': Response(raw).text(),
                    'instruction': 'Return a new response satisfying every local schema and reference constraint.'}) from exc
            if not isinstance(exc, Rejected):
                raise
            raise Rejected(reason) from exc
        self._event(kind, prompt, raw, usage, cost, start, cached, 'accepted', None, key, attempt=attempt)
        self._after(kind)
        if not cached and not schema_smoke:
            self.cache.put(key, {'raw': raw})
        return result

    def _after(self, kind):
        self.budget.after(kind)
        if kind == 'extract_paper' and self._paper_budget is not None:
            self._paper_budget.after()

    def _event(self, kind: str, prompt: str, raw: dict | None, usage: TokenUsage,
               cost: Any, start: float, cached: bool, status: str, reason: str | None,
               key: str, unknown_usage: bool = False, *, attempt: int = 1) -> None:
        self.log.emit(RunEvent(now(), kind, 'MODEL', self.requested_model(kind),
                              raw.get('model') if raw else None, prompt,
                              canonical(raw) if raw is not None else None, usage, float(cost),
                              time.monotonic() - start,
                              payload_json=canonical({'status': status, 'reason': reason, 'attempt': attempt,
                                                       'cache_hit': cached, 'cache_key': key,
                                                       'requested_model': self.requested_model(kind),
                                                       'effort': stage_settings(self.config, kind)['effort'],
                                                       'thinking': stage_settings(self.config, kind).get('thinking', 'adaptive'),
                                                       **(Response(raw).routing() if raw else {}),
                                                       'accounting': 'reservation_unknown_actual' if unknown_usage else 'actual',
                                                       **({'source_id': self._paper_budget.source_id} if kind == 'extract_paper' and self._paper_budget else {})})))

    def count_request(self, kind: str, inputs: dict, *, maximum: int | None = None,
                      admission: bool = False) -> TokenUsage:
        if maximum is None:
            maximum = self.config.get(f'{kind}_max_output_tokens', self.config['max_output_tokens'])
            if kind == 'build_t_batch':
                maximum = self.config['extracted_build_t_max_output_tokens']
        prompt = self.render(kind, inputs)[1]
        schema = self.response_schema(kind, inputs)
        estimate = self.provider.estimate(kind, prompt, schema, maximum)
        # The search reservation includes future tool iterations. Admission concerns
        # the counted initial context; each iteration is separately bounded by the service.
        initial = estimate.input_tokens - (self.config['model_context_token_bound'] * estimate.server_tool_uses
                                           if kind == 'search_evidence' else 0)
        fits = initial + maximum <= self.config['model_context_token_bound']
        self.log.record('context_admission' if admission else 'context_plan', kind=kind,
                        input_tokens=initial, output_tokens=maximum, limit=self.config['model_context_token_bound'],
                        decision='fits' if fits else 'refused', prompt=prompt)
        if admission and not fits:
            self.budget.stop(f'{kind} context bound exceeded by counted request; no truncation', kind,
                             scope='paper' if kind == 'extract_paper' else 'run')
        return estimate

    def extract_paper(self, paper: Paper) -> PaperExtraction:
        from ara.runtime.extraction_budget import PaperAllowance
        require(self._paper_budget is None, 'nested paper extraction')
        allowance = self._paper_budget = PaperAllowance(self, paper)
        try:
            return self._extract_paper(paper)
        except BudgetStop as exc:
            if not allowance.stopped:
                allowance.stop(str(exc), scope=exc.scope)
            raise
        finally:
            self._paper_budget = None

    def _extraction_response(self, paper, inputs, pages, prefix, existing=(),
                             allow_incomplete=False, validate_context=None):
        corrections = self.config.get('extraction_targeted_corrections')
        if corrections is not None and (type(corrections) is not int or corrections not in (0, 1, 2)):
            raise ValueError('extraction_targeted_corrections must be 0, 1 or 2')
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
                            item.inference_origin == 'paper_stated', 'invalid stated inference')
                else:
                    require(not item.premise_ids and item.conclusion_id is None and
                            not item.qualification_ids and item.inference_origin is None, 'node contains inference fields')
                require(not item.applies_to or item.kind in ('distinction', 'qualification'), 'invalid qualification relation')
            by_id = {item.id: item for item in (*existing, *items)}
            if self.config.get('extraction_require_inference', False) and (
                    inputs.get('mode') != 'reconcile_ranges' and not data['new_gaps'] and
                    len(pages) == len(paper.readable_pages)):
                require(any(item.kind == 'inference' for item in by_id.values()), 'extraction has no stated inference')
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
            return PaperExtraction(paper.source_id, converted, resolutions_json=canonical(ledger),
                                   dispositions_json=canonical(dispositions)), data['new_gaps'], request
        if corrections is None:
            return self.call('extract_paper', inputs, check)
        candidate = None
        request = inputs
        for correction in range(corrections + 1):
            def corrected(patch):
                merged = merge_extraction_patch(candidate, patch)
                extraction_defaults(merged)
                schema = self.response_schema('extract_paper', inputs)
                Draft202012Validator(schema).validate(merged)
                return check(merged)
            try:
                return self._call_once('extract_paper', request,
                                       check if correction == 0 else corrected, attempt=correction + 1)
            except InvalidOutput as exc:
                if correction == corrections:
                    raise
                try:
                    rejected = json.loads(exc.feedback['rejected_response'])
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

    def _extract_paper(self, paper: Paper) -> PaperExtraction:
        ranges: list[PaperExtraction] = []
        def run(inputs, pages, prefix, existing=(), allow_incomplete=False, validate_context=None):
            return self._extraction_response(paper, inputs, pages, prefix, existing,
                                             allow_incomplete, validate_context)

        unresolved = []
        def segment(pages):
            inputs = {**paper.inputs(), 'pages': [dict(page=p.page, text=p.text) for p in pages]}
            prefix = f'r{pages[0].page}-{pages[-1].page}'
            self.log.record('extraction_range', source_id=paper.source_id, prefix=prefix,
                            pages=[p.page for p in pages], input_hash=digest(canonical(inputs)))
            try:
                result, new_gaps, _ = run(inputs, pages, prefix, allow_incomplete=True)
            except Rejected as exc:
                if not any(reason in str(exc) for reason in ('provider stop: max_tokens', 'extraction coverage incomplete')) or len(pages) == 1:
                    raise
                self.log.record('extraction_range_split', source_id=paper.source_id, prefix=prefix, reason=str(exc))
                mid = len(pages) // 2
                segment(pages[:mid]); segment(pages[mid:])
                return
            obligations = record_new_obligations(self.log, paper.source_id, prefix, 1,
                                                 [p.page for p in pages], new_gaps)
            result = replace(result, obligations_json=canonical(obligations))
            ranges.append(result)
            unresolved.extend(obligations)
            save_immutable(self.log.path.parent / f'{paper.source_id}.{prefix}.rich.json', canonical(result.to_dict()))
        for pages, _ in extraction_range_plan(self, paper):
            segment(pages)
        from ara.runtime.reconciliation import reconcile
        items, unresolved, resolutions = reconcile(self, paper, ranges, run)
        resolutions_json = canonical(resolutions)
        require(len({item.id for item in items}) == len(items), 'duplicate merged extraction id')
        if (len(ranges) > 1 or unresolved) and self.config.get('extraction_require_inference', False):
            require(any(item.kind == 'inference' for item in items), 'extraction has no stated inference')
        result = PaperExtraction(paper.source_id, items, obligations_json=canonical(unresolved),
                                 resolutions_json=resolutions_json, dispositions_json=canonical([
                                     d for r in ranges for d in json.loads(r.dispositions_json)]))
        self.log.record('extraction_graph_merged', source_id=paper.source_id, ranges=len(ranges),
                        items=len(items), graph_hash=digest(canonical(result.to_dict())))
        return result

    def build_t(self, literature: str, audience: str) -> CommitmentSet:
        allowed = citation_ids(literature)
        if allowed is not None:
            require(bool(allowed), 'no extracted claims available to build T')
            from ara.runtime.construction import construct
            return construct(self, literature, audience)
        return self.call('build_t', {'literature': literature, 'audience': audience}, CommitmentSet.from_dict)

    def propose_targets(self, commitments: CommitmentSet, count: int = 10,
                        named_position: str | None = None) -> tuple[Proposition, ...]:
        def check(data):
            targets = tuple(Proposition.from_dict(p) for p in data['targets'])
            require(len(targets) == (1 if named_position is not None else count), 'wrong target count')
            require(len({p.id for p in targets}) == len(targets), 'duplicate target id')
            if named_position is not None:
                require(targets[0].text == named_position, 'named position was changed')
            return targets
        return self.call('propose_targets', {'commitments': commitments.to_dict(), 'count': count,
                                            'named_position': named_position}, check)

    def propose_cuts(self, goal: Proposition, commitments: CommitmentSet,
                     bank: tuple[BankEntry, ...]) -> tuple[Proposal, ...]:
        return self.call('propose_cuts', {'goal': goal.to_dict(), 'commitments': commitments.to_dict(),
                         'bank': [b.to_dict() for b in bank]},
                         lambda d: tuple(Proposal.from_dict(p) for p in d['proposals']))

    def formalise(self, proposition: Proposition) -> Formula:
        return self.call('formalise', {'proposition': proposition.to_dict()},
                         lambda d: Formula.from_dict(d['formula']))

    def map_leaf(self, leaf: Proposition, commitments: CommitmentSet) -> str:
        def check(data):
            require(data['t_id'] == 'open' or commitments.get(data['t_id']) is not None, 'unknown T id')
            return data['t_id']
        return self.call('map_leaf', {'leaf': leaf.to_dict(), 'commitments': commitments.to_dict()}, check)

    def answer_cq(self, question: CriticalQuestion, proposal: Proposal,
                  commitments: CommitmentSet) -> CQAnswer:
        def check(data):
            answer = CQAnswer.from_dict(data)
            require(answer.cq_id == question.id, 'wrong CQ id')
            require(all(commitments.get(t) is not None for t in answer.supporting_t_ids), 'unknown CQ T id')
            return answer
        return self.call('answer_cq', {'question': question.to_dict(), 'proposal': proposal.to_dict(),
                                      'commitments': commitments.to_dict()}, check)

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
        return {'nodes': [{'id': n.id, 'text': n.proposition.text} for n in route.nodes],
                'links': links}

    def essay_inputs(self, route: RouteGraph) -> dict:
        return {'outline': self.essay_outline(route), 'word_limit': min(6000, self.config['essay_word_limit']),
                'minimum_words': self.config['essay_min_words'],
                'feedback': [json.loads(e['payload_json'])['text'] for e in self.log.read()
                             if e['label'] == 'HUMAN' and e['stage'] == 'feedback']}

    def write_essay(self, route: RouteGraph) -> dict:
        def check(data):
            require(word_count(data) <= min(6000, self.config['essay_word_limit']), 'essay word limit exceeded')
            require(len({b['id'] for b in data['bibliography']}) == len(data['bibliography']), 'duplicate citation id')
            markers = set(re.findall(r'\[\[node:([^\]]+)\]\]', data['body']))
            require(markers == {node.id for node in route.nodes}, 'essay writer: node marker coverage mismatch')
            body = re.sub(r'\[\[node:[^\]]+\]\]|\[cite:[^\]]+\]', '', data['body'])
            text_tokens = [token for token in body.split() if any(char.isalnum() for char in token)]
            require(len(text_tokens) >= 2, 'essay writer: body needs at least two text tokens')
            require(word_count(data) >= self.config['essay_min_words'],
                    'essay writer: minimum words not reached')
            return data
        return self.call('write_essay', self.essay_inputs(route), check)

    def audit_inputs(self, route: RouteGraph, draft: dict) -> dict:
        body = re.sub(r'\[\[node:[^\]]+\]\]', '', draft['body'])
        parts = [part.strip() for part in re.split(r'(?<=[.!?])\s+|\n+', body) if part.strip()]
        return {'sentences': [{'sentence': i, 'text': text} for i, text in enumerate(parts, 1)],
                'outline': self.essay_outline(route)}

    def audit_essay(self, route: RouteGraph, draft: dict) -> dict:
        inputs = self.audit_inputs(route, draft)
        def check(data):
            ids = {n.id for n in route.nodes}
            expected = {s['sentence'] for s in inputs['sentences']}
            labels = data['labels']
            numbers = [item['sentence'] for item in labels]
            if len(numbers) != len(set(numbers)) or set(numbers) != expected:
                require(not any(item['asserts_premise_or_inference_not_in_outline'] for item in labels),
                        'essay audit failed')
                # An incomplete non-adverse inventory supplies no audit verdict.
                # Correct its shape through the normal bounded validation policy;
                # a complete adverse audit remains final below.
                raise ValidationError('essay audit: sentence inventory mismatch')
            covered = {node for item in labels for node in item['node_ids']}
            require(covered <= ids, 'essay audit: unknown node id')
            missing = ids - covered
            extra = [item['sentence'] for item in labels if item['asserts_premise_or_inference_not_in_outline']]
            markers = set(re.findall(r'\[\[node:([^\]]+)\]\]', draft['body']))
            result = {'covered_node_ids': sorted(covered), 'missing_node_ids': sorted(missing),
                      'extra_steps': extra,
                      'faithful': not missing and not extra and markers == ids}
            self.log.record('essay_audit', **result)
            require(result['faithful'], 'essay audit failed')
            return result
        return self.call('audit_essay', inputs, check)

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
        items = self.verification_items(draft)
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
        cleaned = json.loads(canonical(draft))
        removed = []
        for item in result['items']:
            if item['status'] == 'unverified':
                removed.append(item['id'])
                cleaned['body'] = cleaned['body'].replace(item['text'], '')
                if item['kind'] == 'citation':
                    cleaned['bibliography'] = [b for b in cleaned['bibliography'] if b['id'] != item['id']]
                    cleaned['body'] = cleaned['body'].replace(f'[cite:{item["id"]}]', '')
                else:
                    cleaned['body'] = cleaned['body'].replace('""', '').replace('“”', '')
        self.log.record('verification_cleanup', removed_ids=removed, draft=cleaned, verification=result)
        return cleaned, result
