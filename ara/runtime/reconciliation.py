"""One best-effort review; accepted range evidence always survives."""
from dataclasses import asdict
import json

from ara.runtime.cache import canonical, digest
from ara.runtime.extraction import PaperExtraction, save_immutable, record_new_obligations


def reconcile(calls, paper, ranges, run):
    from ara.runtime.calls import extraction_failure_reason
    items = tuple(item for result in ranges for item in result.items)
    obligations = [o for result in ranges for o in json.loads(result.obligations_json)]
    resolutions = [r for result in ranges for r in json.loads(result.resolutions_json)]
    dispositions = []
    if len(ranges) == 1 and not obligations:
        return items, obligations, resolutions, dispositions
    resolved = {r['obligation_id'] for r in resolutions}
    pending = [o for o in obligations if o['id'] not in resolved]
    inputs = dict(mode='reconcile_ranges', source_id=paper.source_id, pdf_sha256=paper.pdf_sha256,
                  evidence_page_ids=[p.page for p in paper.readable_pages],
                  ranges=[PaperExtraction(paper.source_id, items).to_dict()], obligations=pending,
                  pages=[asdict(p) for p in paper.readable_pages])
    def validate_context(request):
        from ara.runtime.calls import require
        require(set(request['pages']) <= set(inputs['evidence_page_ids']), 'reconciliation requests unread page')
        require(set(request['evidence_ids']) <= {i.id for i in items}, 'reconciliation requests unknown evidence')

    try:
        # Admit the complete graph and source, or disclose the refusal. There is
        # no truncation, correction chain, traversal or follow-up context request.
        calls.count_request('extract_paper', inputs, admission=True)
        calls.log.record('extraction_reconciliation_window', source_id=paper.source_id,
                         prefix='joined', page_ids=inputs['evidence_page_ids'],
                         evidence_ids=[i.id for i in items], obligation_ids=[o['id'] for o in pending],
                         input_hash=digest(canonical(inputs)))
        result, gaps, request = run(inputs, paper.readable_pages, 'joined', existing=items,
                                    allow_incomplete=True, single_pass=True, validate_context=validate_context)
        new = record_new_obligations(calls.log, paper.source_id, 'joined', 1,
                                     inputs['evidence_page_ids'], gaps)
        obligations.extend(new)
        items += result.items
        resolutions.extend(json.loads(result.resolutions_json))
        dispositions.extend(json.loads(result.dispositions_json))
        snapshot = PaperExtraction(paper.source_id, result.items, obligations_json=canonical(pending + new),
                                   resolutions_json=result.resolutions_json,
                                   dispositions_json=result.dispositions_json)
        save_immutable(calls.log.path.parent / f'{paper.source_id}.joined.rich.json', canonical(snapshot.to_dict()))
        if request:
            dispositions.append(dict(kind='context_request_unfulfilled', request=request,
                                     reason='One reconciliation pass; additional context was not fetched.'))
    except Exception as exc:
        dispositions.append(dict(kind='reconciliation_failed', reason=extraction_failure_reason(exc)))
        calls.log.record('extraction_reconciliation_failed', source_id=paper.source_id,
                         reason=extraction_failure_reason(exc), retained_items=len(items))
    calls.log.record('extraction_obligations_resolved', source_id=paper.source_id,
                     obligations=obligations, resolutions=resolutions,
                     open_ids=[o['id'] for o in obligations if o['id'] not in {r['obligation_id'] for r in resolutions}])
    return items, obligations, resolutions, dispositions
