"""Bounded graph review and explicit obligation continuation over immutable evidence."""
from collections import deque
from dataclasses import asdict, replace
import json

from ara.runtime.cache import canonical, digest
from ara.runtime.extraction import PaperExtraction, save_immutable, record_new_obligations
from ara.runtime.windows import counted_windows


def reconcile(calls, paper, ranges, run):
    from ara.runtime.calls import require
    items = tuple(item for result in ranges for item in result.items)
    obligations = [o for result in ranges for o in json.loads(result.obligations_json)]
    resolutions = []
    queue = deque(obligations)
    if len(ranges) == 1 and not obligations:
        return items, obligations, resolutions
    pages = {p.page: p for p in paper.readable_pages}
    limit = calls.config['model_context_token_bound'] - calls.config['extract_paper_max_output_tokens']
    max_requests = calls.config.get('reconciliation_context_requests', 16)
    require(type(max_requests) is int and max_requests >= 0, 'invalid reconciliation context request limit')
    turn = 0

    def inputs_for(page_ids, obligation=None, evidence_ids=(), requested=False):
        known = {item.id: item for item in items}
        require(set(page_ids) <= set(pages), 'reconciliation requests unread page')
        require(set(evidence_ids) <= set(known), 'reconciliation requests unknown evidence')
        selected = tuple(item for item in items if item.id in evidence_ids or
                         any(item.page_start <= p <= item.page_end for p in page_ids))
        inputs = dict(mode='reconcile_ranges', source_id=paper.source_id, pdf_sha256=paper.pdf_sha256,
                      evidence_page_ids=list(page_ids),
                      ranges=[PaperExtraction(paper.source_id, selected).to_dict()],
                      obligations=[obligation] if obligation else [],
                      pages=[asdict(pages[p]) for p in page_ids] if obligation or requested else [])
        return inputs, selected

    def windows_for(obligation=None):
        def count(ids):
            return calls.count_request('extract_paper', inputs_for(ids, obligation)[0]).input_tokens
        return counted_windows(tuple(pages), count, limit, lambda: calls.budget.stop(
            'reconciliation indivisible evidence window exceeds context; obligations retained', 'extract_paper'))

    def execute(ids, obligation=None, evidence_ids=(), requested=False):
        nonlocal items, turn
        inputs, selected = inputs_for(ids, obligation, evidence_ids, requested)
        calls.count_request('extract_paper', inputs, admission=True)
        prefix = 'joined' if turn == 0 else f'joined{turn + 1}'
        turn += 1
        calls.log.record('extraction_reconciliation_window', source_id=paper.source_id,
                         prefix=prefix, page_ids=list(ids), evidence_ids=[i.id for i in selected],
                         obligation_ids=[o['id'] for o in inputs['obligations']], input_hash=digest(canonical(inputs)))
        result, new_gaps, request = run(inputs, tuple(pages[p] for p in ids), prefix,
                                       existing=selected, allow_incomplete=True)
        new_obligations = record_new_obligations(calls.log, paper.source_id, prefix, turn, ids, new_gaps)
        obligations.extend(new_obligations)
        queue.extend(new_obligations)
        items += result.items
        result = replace(result, obligations_json=canonical(inputs['obligations'] + new_obligations))
        save_immutable(calls.log.path.parent / f'{paper.source_id}.{prefix}.rich.json', canonical(result.to_dict()))
        return result, request

    # When the initial ranges declared no missing references, review every graph
    # window once. Newly found gaps become stable obligations, never a discarded note.
    if not obligations:
        for ids in windows_for():
            execute(ids)

    while queue:
        obligation = queue.popleft()
        resolved = False
        requests = set()
        for initial in windows_for(obligation):
            ids, evidence_ids, requested = initial, (), False
            while True:
                result, request = execute(ids, obligation, evidence_ids, requested)
                ledger = json.loads(result.resolutions_json)
                if ledger:
                    resolutions.extend(ledger)
                    calls.log.record('extraction_obligation_resolved', source_id=paper.source_id,
                                     resolutions=ledger)
                    resolved = True
                    break
                if not request:
                    break
                key = canonical(request)
                require(key not in requests and len(requests) < max_requests,
                        'unresolved obligation context request cycle or limit')
                requests.add(key)
                ids = tuple(sorted(request['pages']))
                evidence_ids = tuple(request['evidence_ids'])
                require(bool(ids) or bool(evidence_ids), 'unresolved obligation empty context request')
                # Evidence requests carry their actual source pages too. The full
                # requested set is admitted or refused; it is never silently trimmed.
                ids = tuple(sorted(set(ids) | {p for item in items if item.id in evidence_ids
                    for p in pages if item.page_start <= p <= item.page_end}))
                requested = True
            if resolved:
                break
        require(resolved, 'unresolved obligation inventory after all evidence windows')
    require({r['obligation_id'] for r in resolutions} == {o['id'] for o in obligations},
            'unresolved obligation inventory at merge')
    save_immutable(calls.log.path.parent / f'{paper.source_id}.obligations.json', canonical(obligations))
    calls.log.record('extraction_obligations_resolved', source_id=paper.source_id,
                     obligations=obligations, resolutions=resolutions)
    return items, obligations, resolutions
