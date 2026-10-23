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
        else:
            self.provider = AnthropicProvider(config) if counter == 'provider' else None
        if hasattr(self.provider, 'initial_context_tokens'):
            self.initial_context_tokens = self.provider.initial_context_tokens
            self.context_output_tokens = self.provider.context_output_tokens
        self.estimate_method = getattr(self.provider, 'estimate_method',
                                       'provider_count_tokens' if self.provider else 'local_estimate_utf8_bytes_div_4')

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
