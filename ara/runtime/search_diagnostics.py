"""Sanitized evidence from the actual packed requests in durable search journals."""
from collections import Counter, defaultdict
import json

from ara.runtime.cache import canonical, digest
from ara.runtime.providers import Response
from ara.runtime.search_alignment import symbols
from ara.types import Formula


class SearchPaused(RuntimeError):
    """An intentional search checkpoint, resumable through the native journals."""


def accepted_inferences(journal):
    return sum((event.get('decision') or {}).get('reason_code') == 'BANK_LICENSED' and
               (event.get('decision') or {}).get('status') == 'licensed' for event in journal.read())


# Never copy free-form validator/provider messages or engine details into summaries.
REJECTION_CODES = frozenset('''UNKNOWN_BANK_ID SLOT_MISMATCH CONCLUSION_REFERENCE_MISMATCH
CONCLUSION_MISMATCH INVALID_SCOPE SCHEMA_MISMATCH SOLVER_SAT SOLVER_UNKNOWN
STANCE_CROSSING INVALID_PROPOSAL_BATCH DUPLICATE_PROPOSAL PROPOSAL_CORRECTION
CQ_SCHEME_CORRECTION CQ_REPEATED_SCHEME CYCLE NODE_CAP NOT_IN_COMMITMENTS OPPOSED_COMMITMENT
DEPTH_CAP TIER1_CONFLICT TIER2_CONFLICT'''.split())


def response_summary(event):
    data = json.loads(event['payload_json'])
    status = data.get('status')
    outcome = status if status in ('accepted', 'rejected', 'incomplete') else 'unknown'
    if status == 'accepted' and event['stage'] in ('map_leaf', 'propose_cuts'):
        response = json.loads(Response(json.loads(event['response'])).text())
        if event['stage'] == 'propose_cuts':
            outcome = 'accepted_proposals' if response['proposals'] else 'accepted_empty_proposals'
        else:
            outcome = 'accepted_open_leaf' if response['t_id'] == 'open' else 'accepted_frozen_reference'
    reason = None
    if status == 'rejected':
        raw_reason = data.get('reason') or ''
        reason = ('schema_validation_rejected' if raw_reason.startswith('ValidationError') else
                  'unknown_frozen_reference' if raw_reason == 'unknown T id' else
                  'model_output_rejected')
    elif status == 'incomplete':
        reason = 'model_response_incomplete'
    return dict(kind=event['stage'], outcome=outcome, attempt=data.get('attempt'),
                cache_hit=bool(data.get('cache_hit')), rejection_reason=reason)


def packed_request(event, basis):
    inputs = json.loads(event['prompt'].split('\nINPUT_JSON\n', 1)[1])
    rows = {c['id']: c for c in inputs.get('commitments', {}).get('commitments', [])}
    present = sorted(set(basis) & rows.keys())
    papers = {tid: row.get('source_id') for tid, row in (inputs.get('commitment_roles') or {}).items()}
    papers.update(inputs.get('commitment_papers', {}))
    shared = defaultdict(dict)
    for tid in present:
        paper = papers.get(tid)
        if paper:
            for signature in symbols(Formula.from_dict(rows[tid]['formula'])):
                shared[signature][tid] = paper
    overlap = [dict(name=name, kind=kind, arity=arity,
                    commitment_ids=sorted(members), paper_ids=sorted(set(members.values())))
               for (name, kind, arity), members in sorted(shared.items())
               if len(set(members.values())) >= 2]
    return dict(**response_summary(event), request_sha256=digest(event['prompt']),
                premise_payload='packed_commitments' if 'commitments' in inputs else 'no_commitments_payload',
                basis_ids=list(basis), present_basis_ids=present,
                missing_basis_ids=sorted(set(basis) - rows.keys()),
                basis_present=(set(basis) <= rows.keys()) if basis and 'commitments' in inputs else None,
                cross_paper_shared_symbols=overlap,
                paper_evidence='available' if basis and all(papers.get(tid) for tid in basis) else 'unavailable_or_partial')


def job_diagnostic(journal, goal, index, status, *, restored_inferences=0):
    events = journal.read()
    requests, responses, reasons = [], [], Counter()
    accepted = restored_inferences
    for event in events:
        decision = event.get('decision') or {}
        accepted += decision.get('status') == 'licensed' and decision.get('reason_code') == 'BANK_LICENSED'
        if decision.get('status') == 'discarded':
            code = decision.get('reason_code')
            reasons[code if code in REJECTION_CODES else 'OTHER_ENGINE_REJECTION'] += 1
        if event['label'] == 'MODEL':
            responses.append(response_summary(event))
            if event['stage'] in ('map_leaf', 'propose_cuts', 'formalise_slots'):
                requests.append(packed_request(event, goal.basis_commitment_ids))
        if event['stage'] == 'search_job_failed':
            reasons['JOB_FAILED'] += 1
        if event['stage'] == 'search_context_slice':
            if json.loads(event['payload_json']).get('decision') == 'refused':
                reasons['PACKED_CONTEXT_REFUSED'] += 1
    return dict(job_index=index, target_id=goal.id, status=status,
                accepted_inferences=accepted, requests=requests, model_responses=responses,
                request_evidence='recorded' if requests else 'restored_previous_batch' if status == 'restored' else 'not_dispatched_or_no_model_request',
                rejection_reasons=dict(sorted(reasons.items())))


def write_pause(log, publication, jobs, results, attempts, restored, completed, threshold):
    rows = [job_diagnostic(publication.journals[i], goal, i,
                'restored' if i in restored else 'completed' if results[i] is not None else
                'failed' if attempts[i] else 'cancelled',
                restored_inferences=len(engine._licenses) if i in restored else 0)
            for i, (engine, goal) in enumerate(jobs)]
    path = f'search-diagnostics/{publication.batch_id}.json'
    receipt = dict(version=1, batch_id=publication.batch_id, threshold=threshold,
                   completed_jobs=completed, accepted_inferences=sum(r['accepted_inferences'] for r in rows),
                   receipt_path=path, jobs=rows,
                   note='Formal shared symbols do not prove semantic alignment. Accepted model output is not an accepted inference. Resume starts a fresh completion window for unfinished jobs.')
    destination = log.path.parent / path
    destination.parent.mkdir(exist_ok=True)
    with destination.open('x') as stream:
        stream.write(canonical(receipt) + '\n')
    log.record('search_zero_inference_pause', **receipt)
    return SearchPaused(f'Search paused after {completed} completed jobs with zero accepted inferences; inspect {path}, then resume-search explicitly.')
