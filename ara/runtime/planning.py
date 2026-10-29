"""Unpaid range and capacity planning; this provider cannot generate responses."""
import copy
import json
from math import ceil

from ara.runtime.cache import Cache, canonical
from ara.runtime.calls import ModelCalls
from ara.runtime.extraction import extraction_range_plan, save_immutable
from ara.runtime.providers import AnthropicProvider, stage_settings
from ara.types import TokenUsage


class CountingProvider:
    def __init__(self, config, counter):
        self.config = config
        self.model = config['model']
        if counter == 'provider' and config.get('provider') == 'claude_code':
            from ara.runtime.claude_code import ClaudeCodeProvider
            self.provider = ClaudeCodeProvider(config)
        elif counter == 'provider' and config.get('provider') == 'codex_cli':
            from ara.runtime.codex_cli import CodexCLIProvider
            self.provider = CodexCLIProvider(config)
        else:
            self.provider = AnthropicProvider(config) if counter == 'provider' else None
        if hasattr(self.provider, 'initial_context_tokens'):
            self.initial_context_tokens = self.provider.initial_context_tokens
            self.context_output_tokens = self.provider.context_output_tokens
        self.estimate_method = getattr(self.provider, 'estimate_method',
                                       'provider_count_tokens' if self.provider else 'local_estimate_utf8_bytes_div_4')

    def metadata(self, kind):
        return self.provider.metadata(kind) if hasattr(self.provider, 'metadata') else {}

    def model_for(self, kind):
        return stage_settings(self.config, kind)['model']

    def estimate(self, kind, prompt, schema, maximum):
        if self.provider is not None:
            return self.provider.estimate(kind, prompt, schema, maximum)
        return TokenUsage(input_tokens=ceil(len((prompt + canonical(schema or {})).encode()) / 4),
                          output_tokens=maximum)

    def complete(self, *args, **kwargs):
        raise RuntimeError('planning forbids generation')


def plan_extraction(config, log, papers, root, counter):
    from ara.runtime.budget import BudgetStop
    caps = {key: config.get(key) for key in ('token_cap', 'cost_cap_usd', 'extraction_cost_cap_usd')}
    settings = copy.deepcopy(config)
    # Zero caps plus a count-only provider make accidental generation impossible.
    settings.update(token_cap=0, cost_cap_usd=0, extraction_cost_cap_usd=0)
    calls = ModelCalls(settings, CountingProvider(settings, counter), log,
                       Cache(log.path.parent / 'planning-cache'), root, '')
    model = calls.requested_model('extract_paper')
    rates = settings['pricing'][model]
    output_rate = settings.get('extraction_planned_output_tokens_per_page', 1200)
    graph_rate = settings.get('planning_graph_tokens_per_page', 1270)
    batch_overhead = settings.get('planning_batch_overhead_tokens', 8000)
    source_bound = min(settings['build_t_batch_input_tokens'], settings['model_context_token_bound'] -
                       settings['extracted_build_t_max_output_tokens'] - settings['working_t_symbol_token_budget'])
    graph_allowance = source_bound - batch_overhead
    if output_rate <= 0 or graph_rate <= 0 or graph_allowance <= 0:
        raise ValueError('invalid planning density or batch allowance')
    report = dict(counter=calls.provider.estimate_method,
                  model=model, operator_caps=caps, generation_ready=False, dispatches=0,
                  output_tokens_per_readable_page=output_rate, graph_tokens_per_readable_page=graph_rate,
                  batch_overhead_estimate=batch_overhead, input_rate_usd_per_million=rates['input_per_million_usd'],
                  output_rate_usd_per_million=rates['output_per_million_usd'],
                  limits=dict(context=settings['model_context_token_bound'], source_batch=source_bound,
                              working=settings['working_t_token_budget'], symbols=settings['working_t_symbol_token_budget']),
                  papers=[],
                  note='Input ranges use the runtime counter and planner. Output density and construction windows are scenarios. '
                       'Costs exclude reconciliation, retries and corrections; actual graphs, closures and symbol growth are unknown. '
                       'Fits means readable initial extraction ranges fit context, not full-run or semantic acceptance. '
                       'Generation requires operator caps and normal runtime admission.')
    for paper in papers:
        row = dict(source_id=paper.source_id, pdf_sha256=paper.pdf_sha256, pages=len(paper.pages),
                   readable_pages=len(paper.readable_pages), unread_pages=len(paper.unread_pages),
                   affected_pages=len(set(paper.affected_pages)), characters=sum(len(p.text) for p in paper.pages),
                   ranges=[], admission='refuses', reason=paper.unavailable,
                   input_tokens=0, estimated_output_tokens=0, output_allowance=0,
                   estimated_usd=0, initial_reservation_usd=0,
                   estimated_graph_tokens=len(paper.readable_pages) * graph_rate,
                   estimated_selection_windows=ceil(len(paper.readable_pages) * graph_rate / graph_allowance))
        if not paper.unavailable and paper.readable_pages:
            try:
                ranges = extraction_range_plan(calls, paper)
                row['ranges'] = [dict(pages=[p.page for p in pages], input_tokens=usage.input_tokens,
                                      output_allowance=settings['extract_paper_max_output_tokens'])
                                 for pages, usage in ranges]
                row.update(admission='fits', input_tokens=sum(u.input_tokens for _, u in ranges),
                           estimated_output_tokens=len(paper.readable_pages) * output_rate,
                           output_allowance=len(ranges) * settings['extract_paper_max_output_tokens'])
                row['estimated_usd'] = round((row['input_tokens'] * rates['input_per_million_usd'] +
                                             row['estimated_output_tokens'] * rates['output_per_million_usd']) / 1e6, 6)
                row['initial_reservation_usd'] = round((row['input_tokens'] * rates['input_per_million_usd'] +
                                                      row['output_allowance'] * rates['output_per_million_usd']) / 1e6, 6)
            except BudgetStop as exc:
                row['reason'] = str(exc)
        elif not row['reason']:
            row['reason'] = 'no readable pages'
        report['papers'].append(row)
        log.record('extraction_paper_plan', **row)
        print(canonical(row), flush=True)
    fields = ('pages', 'readable_pages', 'unread_pages', 'affected_pages', 'characters', 'input_tokens',
              'estimated_output_tokens', 'output_allowance', 'estimated_usd', 'initial_reservation_usd',
              'estimated_graph_tokens', 'estimated_selection_windows')
    totals = {key: round(sum(row[key] for row in report['papers']), 6) for key in fields}
    totals.update(papers=len(papers), ranges=sum(len(row['ranges']) for row in report['papers']),
                  refused=[row['source_id'] for row in report['papers'] if row['admission'] != 'fits'])
    report['totals'] = totals
    save_immutable(log.path.parent / 'extraction-plan.json', canonical(report))
    log.record('extraction_plan_complete', **report)
    print(canonical(dict(counter=report['counter'], totals=totals)), flush=True)
    return report


def plan_construction(config, log, literature, root, topic, audience, counter):
    """The native global construction plan, with generation disabled in two ways."""
    from ara.runtime.construction import construct
    settings = copy.deepcopy(config)
    settings.update(token_cap=0, cost_cap_usd=0, extraction_cost_cap_usd=0)
    calls = ModelCalls(settings, CountingProvider(settings, counter), log,
                       Cache(log.path.parent / 'planning-cache'), root, topic,
                       provider_factory=lambda stage: CountingProvider(stage, counter))
    plan = construct(calls, literature, audience, plan_only=True)
    largest = max((b['input_tokens'] for b in plan['batches'] if b['input_tokens'] is not None), default=0)
    report = dict(plan=plan, counter=calls.provider.estimate_method,
                  uncounted_windows=[b['index'] for b in plan['batches'] if b['input_tokens'] is None],
                  generation_calls=0, audience=audience, max_request_tokens=largest,
                  context_reserved_tokens=largest + settings['extracted_build_t_max_output_tokens'] + settings['working_t_symbol_token_budget'],
                  limits=dict(batch=plan['budget']['batch_input_bound'], context=settings['model_context_token_bound'],
                              working=settings['working_t_token_budget'], symbols=settings['working_t_symbol_token_budget']),
                  note='Native selection windows and global allocation only. No model relevance or formulas are predicted. '
                       'Closure payload sizes are conservative UTF-8 bounds. Exact chosen formalization and search requests are rechecked live.')
    save_immutable(log.path.parent / 'construction-plan.json', canonical(report))
    log.record('construction_plan_complete', **report)
    return report


def plan_construction_resume(config, log, source_log, root, run):
    from types import SimpleNamespace
    from ara.runtime.construction import construct
    from ara.runtime.construction_resume import load_construction_resume
    state = load_construction_resume(SimpleNamespace(log=source_log, config=config))
    settings = {**config, 'token_cap': 0, 'cost_cap_usd': 0, 'extraction_cost_cap_usd': 0}
    calls = ModelCalls(settings, CountingProvider(settings, 'provider'), log,
                       Cache(log.path.parent / 'planning-cache'), root, run['topic'],
                       provider_factory=lambda stage: CountingProvider(stage, 'provider'))
    result = construct(calls, run['literature'], run['audience'], plan_only=True, resume_state=state)
    refusals = [json.loads(e['payload_json']) for e in log.read() if e['stage'] == 'token_count_refused']
    report = dict(**result, counter=calls.provider.estimate_method, generation_calls=0, new_cost_usd=0,
                  all_counts_passed=not refusals, counter_refusals=refusals,
                  source_run=str(source_log.path.parent))
    save_immutable(log.path.parent / 'construction-resume-plan.json', canonical(report))
    log.record('construction_resume_plan_complete', **report)
    return report


def plan_recorded_target(source, destination, root, *, gap_id=None, bound=None, counter='provider', window=None, margin=None):
    """Replay one authenticated full target request through native prompt admission.

    Uses the recorded gap, leads and feedback verbatim; never re-runs discovery.
    Source artifacts and chained freeze receipts must agree. Output is separate.
    """
    from pathlib import Path
    from ara.bank import load_bank
    from ara.runtime.cache import digest
    from ara.runtime.freeze_fork import effective_run
    from ara.runtime.logging import EventLog, read_log, LogTampered
    from ara.runtime.search_alignment import catalogue_inputs
    from ara.runtime.search_context import fit_target_request
    from ara.types import CommitmentSet
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if destination.is_relative_to(source) or source.is_relative_to(destination):
        raise ValueError('target plan output must be separate from source')
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('target plan output must be empty')
    if bound is not None and (type(bound) is not int or bound <= 0):
        raise ValueError('context bound must be a positive integer')
    rows = read_log(source/'events.jsonl')
    if (source/'events.anchor').read_text().splitlines() != [r['hash'] for r in rows]:
        raise LogTampered('target plan source anchor mismatch')
    events = [r['event'] for r in rows]
    freezes = [json.loads(e['payload_json']) for e in events if e['stage']=='commitments_frozen']
    if len(freezes) != 1:
        raise ValueError('target plan requires one freeze')
    commitments = CommitmentSet.from_dict(freezes[0]['commitments'])
    if CommitmentSet.from_json((source/'commitments.json').read_text()) != commitments:
        raise ValueError('target plan frozen commitments mismatch')
    vocabulary = catalogue_inputs(source, commitments)
    catalogue = json.loads((source/'frozen-t.json').read_text())['symbol_catalogue'] if vocabulary['symbol_catalogue'] is not None else None
    for stage, expected in (('symbol_catalogue_frozen', catalogue),
                            ('commitment_provenance_frozen', vocabulary['commitment_provenance'])):
        receipts = [json.loads(e['payload_json']) for e in events if e['stage']==stage]
        if receipts != ([expected] if expected is not None else []):
            raise ValueError('target plan frozen receipt mismatch: ' + stage)
    bank = load_bank(root/'bank')
    if freezes[0]['bank_version'] != bank.bank_version:
        raise ValueError('target plan bank version mismatch')
    selected = None
    for index, event in enumerate(events):
        if event['stage'] != 'context_admission':
            continue
        row = json.loads(event['payload_json'])
        if row.get('kind') != 'propose_targets':
            continue
        inputs = json.loads(row['prompt'].split('\nINPUT_JSON\n', 1)[1])
        if (inputs.get('commitments') == commitments.to_dict() and 'bank' in inputs
                and 'target_slice' not in inputs and
                (gap_id is None or inputs.get('resolution_gap', {}).get('id') == gap_id)):
            selected = index, row, inputs
    if selected is None:
        raise ValueError('no recorded full assembled target request matches; capacity counts are not target plans')
    index, recorded, inputs = selected
    if any(inputs.get(key) != value for key,value in vocabulary.items()):
        raise ValueError('recorded target vocabulary differs from frozen artifacts')
    if inputs['bank'] != [b.to_dict() for b in bank.entries]:
        raise ValueError('recorded target bank differs from current bank')
    run = effective_run(events[:index+1])
    settings = run['config']
    for event in events[:index+1]:
        if event['stage'] in ('alignment_resumed', 'freeze_fork_configuration'):
            settings = json.loads(event['payload_json'])['config']
    settings = {**settings, 'token_cap': 0, 'cost_cap_usd': 0, 'extraction_cost_cap_usd': 0,
                'model_context_token_bound': recorded['limit'] if bound is None else bound}
    from ara.runtime.codex_window import apply_context_window
    if window is not None:
        settings['model_context_window'] = window
    if margin is not None:
        settings['model_context_margin_tokens'] = margin
    window_decision = apply_context_window(settings)
    if bound is not None and window_decision is not None and bound != settings['model_context_token_bound']:
        raise ValueError('context bound conflicts with configured provider window')
    provider = CountingProvider(settings, counter)
    if counter == 'provider' and settings.get('provider') not in ('codex_cli', 'claude_code'):
        raise ValueError('recorded target free plan requires a local counter or subscription estimate')
    if hasattr(provider.provider, 'calibration_state'):
        provider.provider.calibration_state.restore(events[:index+1])
    log = EventLog(destination/'events.jsonl')
    if window_decision is not None:
        log.record('operator_context_window', **window_decision)
    topic = inputs.pop('topic')
    calls = ModelCalls(settings, provider, log, Cache(destination/'planning-cache'), root, topic)
    log.record('target_plan_source', source_run=str(source), source_tail=rows[-1]['hash'],
               request_event_hash=rows[index]['hash'], counter=provider.estimate_method,
               commitments_sha256=vocabulary['commitments_sha256'],
               provenance_sha256=vocabulary['provenance_sha256'],
               note='Exact recorded gap, leads and feedback; no discovery or generation.')
    original = calls.count_request('propose_targets', inputs, purpose='unpacked_recorded_target_with_current_template')
    data = fit_target_request(calls, inputs)
    packed = calls.count_request('propose_targets', data, admission=True)
    def counts(input_tokens, output_tokens):
        total = input_tokens + output_tokens
        return dict(input_tokens=input_tokens, output_tokens=output_tokens, total_tokens=total,
                    fits_recorded_bound=total <= recorded['limit'],
                    fits_configured_bound=total <= settings['model_context_token_bound'])
    report = dict(generation_calls=0, new_cost_usd=0, decision='fits',
        counter=provider.estimate_method, calibration=provider.metadata('propose_targets').get('calibration'),
        bounds=dict(recorded=recorded['limit'], configured=settings['model_context_token_bound']),
        context_window_decision=window_decision,
        recorded_request=counts(recorded['input_tokens'], recorded['output_tokens']),
        unpacked_current_template=counts(original.initial_input_tokens, original.context_output_tokens),
        packed=counts(packed.initial_input_tokens, packed.context_output_tokens),
        inputs_sha256=digest(canonical(data)), source_request_event_hash=rows[index]['hash'],
        projection=data['target_slice'],
        note='Admission estimate, not tokenizer proof or semantic readiness. Configured bound must not exceed the effective provider window. No target generation, routes or selection.')
    save_immutable(destination/'target-request.json', canonical(data))
    save_immutable(destination/'target-plan.json', canonical(report))
    log.record('target_plan_complete', **report)
    return report
