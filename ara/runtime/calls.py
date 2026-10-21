"""The single model boundary: prompt, reserve, call, validate, log, cache."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Callable, Any

from jsonschema import Draft202012Validator, ValidationError

from ara.bank import load_bank
from ara.runtime.budget import Budget, BudgetStop, UnpricedModel
from ara.runtime.cache import Cache, cache_key, canonical
from ara.runtime.logging import EventLog, now
from ara.runtime.extraction import Paper, PaperExtraction, ExtractedItem, citation_ids
from ara.runtime.providers import Provider, Response
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

    def render(self, kind: str, inputs: dict) -> tuple[str, str]:
        template = (self.root / 'prompts' / f'{kind}.txt').read_text()
        if kind != 'search_evidence':
            # The service grammar is a compact projection. Show the model every
            # local constraint as well; the same complete prompt is logged/keyed.
            schema = json.loads((self.root / 'schemas' / f'{kind}.json').read_text())
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

    def _call_once(self, kind: str, inputs: dict, check: Callable[[dict], Any] | None = None, *, attempt: int = 1) -> Any:
        offset = len(self.log.read())
        before_tokens, before_cost = self.budget.used_tokens, self.budget.used_cost
        started = time.monotonic()
        try:
            return self._execute_once(kind, inputs, check, attempt=attempt)
        except Exception as exc:
            events = self.log.read()[offset:]
            starts = [e for e in events if e['stage'] == 'call_start']
            completed = [e for e in events if e['label'] == 'MODEL']
            if not starts or completed:
                raise
            # Any unrecorded dispatched result is incomplete. Do not serialize the
            # suspect raw response again, and replace any in-memory actual charge.
            admission = json.loads(starts[-1]['payload_json'])
            usage = TokenUsage.from_dict(admission['reserved_usage'])
            cost = self.budget.cost(usage)
            self.budget.used_tokens, self.budget.used_cost = before_tokens, before_cost
            self.budget.charge(usage, cost)
            self.log.emit(RunEvent(now(), kind, 'MODEL', self.provider.model, None,
                admission['prompt'], None, usage, float(cost), time.monotonic() - started,
                payload_json=canonical({'status': 'incomplete', 'attempt': attempt, 'reason': type(exc).__name__,
                    'cache_hit': False, 'cache_key': admission['cache_key'],
                    'accounting': 'reservation_unknown_actual'})))
            self.budget.after(kind)
            self.budget.stop('provider result incomplete; reservation charged; actual spend unknown', kind)

    def _execute_once(self, kind: str, inputs: dict, check: Callable[[dict], Any] | None = None, *, attempt: int = 1) -> Any:
        template, prompt = self.render(kind, inputs)
        schema = None if kind == 'search_evidence' else json.loads(
            (self.root / 'schemas' / f'{kind}.json').read_text())
        maximum = self.config.get(f'{kind}_max_output_tokens', self.config['max_output_tokens'])
        identity = canonical({'inputs': inputs, 'topic': self.topic, 'provider': type(self.provider).__name__,
                              'effort': self.config['effort'], 'maximum': maximum,
                              'web_max': self.config['web_search_max_uses'],
                              'formula_depth': self.config.get('formula_output_depth', 2),
                              'fallbacks': self.config.get('fallbacks', ['claude-opus-4-8'])})
        key = cache_key(kind, template, identity, self.provider.model, schema or {})
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
            if cached:
                raw = saved['raw']
                self.budget.response_cost(raw)  # Cached responses retain validated model/pricing provenance.
            else:
                estimate = self.provider.estimate(kind, prompt, schema, maximum)
                if kind == 'extract_paper' and estimate.input_tokens + maximum > self.config['model_context_token_bound']:
                    self.budget.stop('extraction context bound exceeded; no truncation', kind)
                self.budget.before(estimate, kind)
                self.log.record('call_start', kind=kind, attempt=attempt, model=self.provider.model, prompt=prompt,
                                schema=schema, reserved_usage=estimate.to_dict(), cache_key=key)
                dispatched = True
                raw = self.provider.complete(kind, prompt, schema, maximum).raw
                usage = Response(raw).usage
                require(all(type(n) is int and n >= 0 for n in usage.to_dict().values()), 'invalid usage')
                cost = self.budget.response_cost(raw)
                self.budget.charge(usage, cost)
                charged = True
            # Stop reason is checked BEFORE interpreting any content blocks.
            require(raw['stop_reason'] == 'end_turn', f'provider stop: {raw["stop_reason"]}')
            require(not any(isinstance(v, dict) and (v.get('is_error') or
                        str(v.get('type', '')).endswith('_error') or v.get('error_code'))
                        for v in walk(raw['content'])), 'server tool error')
            if schema is None:
                urls = sorted({v['url'] for v in walk(Response(raw).served_content) if isinstance(v, dict)
                               and v.get('type') == 'web_search_result' and isinstance(v.get('url'), str)})
                data = {'text': Response(raw).text(), 'urls': urls, 'content': Response(raw).served_content}
                require(bool(data['text']), 'empty evidence response')
            else:
                validating = True
                data = json.loads(Response(raw).text())
                Draft202012Validator(schema).validate(data)
            result = check(data) if check else data
        except (BudgetStop, json.JSONDecodeError):
            raise
        except Exception as exc:
            if charged and not isinstance(exc, (Rejected, ValueError, ValidationError)):
                raise
            # Provider exception messages can embed HTTP credentials. Store only
            # their class; model responses and local validation remain in full.
            reason = str(exc) if isinstance(exc, (Rejected, UnpricedModel)) else type(exc).__name__
            unknown_usage = dispatched and not charged
            if unknown_usage:
                usage, cost = estimate, self.budget.cost(estimate)
                self.budget.charge(usage, cost)
            self._event(kind, prompt, raw, usage, cost, start, cached, 'incomplete' if unknown_usage else 'rejected', reason, key, unknown_usage, attempt=attempt)
            if unknown_usage:
                self.budget.after(kind)
                self.budget.stop(f'provider accounting unavailable ({reason}); reservation charged; actual spend unknown', kind)
            self.budget.after(kind)
            if validating and not (kind == 'audit_essay' and isinstance(exc, Rejected)):
                raise InvalidOutput(reason, {'error': str(exc),
                    'rejected_response': Response(raw).text(),
                    'instruction': 'Return a new response satisfying every local schema and reference constraint.'}) from exc
            raise Rejected(reason) from exc
        self._event(kind, prompt, raw, usage, cost, start, cached, 'accepted', None, key, attempt=attempt)
        self.budget.after(kind)
        if not cached:
            self.cache.put(key, {'raw': raw})
        return result

    def _event(self, kind: str, prompt: str, raw: dict | None, usage: TokenUsage,
               cost: Any, start: float, cached: bool, status: str, reason: str | None,
               key: str, unknown_usage: bool = False, *, attempt: int = 1) -> None:
        self.log.emit(RunEvent(now(), kind, 'MODEL', self.provider.model,
                              raw.get('model') if raw else None, prompt,
                              canonical(raw) if raw is not None else None, usage, float(cost),
                              time.monotonic() - start,
                              payload_json=canonical({'status': status, 'reason': reason, 'attempt': attempt,
                                                       'cache_hit': cached, 'cache_key': key,
                                                       'requested_model': self.provider.model,
                                                       **(Response(raw).routing() if raw else {}),
                                                       'accounting': 'reservation_unknown_actual' if unknown_usage else 'actual'})))

    def extract_paper(self, paper: Paper) -> PaperExtraction:
        def check(data):
            require(data['source_id'] == paper.source_id, 'extraction source id mismatch')
            items = tuple(ExtractedItem(**item) for item in data['items'])
            for item in items:
                require(item.source_id == paper.source_id, 'extraction item source id mismatch')
                require(1 <= item.page_start <= item.page_end <= len(paper.pages), 'extraction page outside paper')
                require(bool(item.text.strip()), 'extraction text is blank')
            return PaperExtraction(paper.source_id, items)
        return self.call('extract_paper', paper.inputs(), check)

    def build_t(self, literature: str, audience: str) -> CommitmentSet:
        allowed = citation_ids(literature)
        if allowed is not None:
            require(bool(allowed), 'no extracted claims available to build T')
        def check(data):
            result = CommitmentSet.from_dict(data)
            if allowed is not None:
                require(all(c.citation in allowed for c in result.commitments), 'T citation not in extracted literature')
            return result
        return self.call('build_t', {'literature': literature, 'audience': audience}, check)

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
