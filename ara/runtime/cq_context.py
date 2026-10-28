"""Counted CQ retrieval over the full frozen inventory; relevance is not support."""
import re
from string import Formatter
from ara.runtime.bridges import _STOP_WORDS
from ara.runtime.cache import canonical, digest
from ara.runtime.search_alignment import symbols
from ara.types import CommitmentSet


def rank_cq(inputs):
    commitments = CommitmentSet.from_dict(inputs['commitments'])
    proposal = inputs['proposal']
    fills = {p['slot']: p['text'] for p in proposal['premises']}
    fills['conclusion'] = proposal['conclusion_text']
    template = inputs['question']['template']
    question = template.format_map(fills)
    words = set(re.findall(r'\w+', question.casefold())) - _STOP_WORDS
    names = set(re.findall(r'\w+', question))
    query_symbols = set()
    for _, slot, _, _ in Formatter().parse(template):
        for fill in proposal['premises']:
            c = commitments.get(fill['t_id'])
            if slot == fill['slot'] and c:
                query_symbols.update(symbols(c.formula))
    catalogue = inputs.get('symbol_catalogue') or []
    query_symbols.update((s['name'],s['kind'],s['arity']) for s in catalogue if s['name'] in names)
    definitions = {(s['name'],s['kind'],s['arity']): s['definition'] for s in catalogue}
    provenance = inputs.get('commitment_provenance')
    rows = provenance['commitments'] if provenance else {}
    ranked = []
    for c in commitments.commitments:
        if provenance is not None and rows[c.id]['stance'] != 'endorsed':
            continue
        sigs = set(symbols(c.formula))
        shared = len(sigs & query_symbols)
        content = c.text + ' ' + ' '.join(definitions.get(s,'') for s in sigs)
        lexical = len(words & (set(re.findall(r'\w+',content.casefold())) - _STOP_WORDS))
        if shared or lexical:
            ranked.append(dict(commitment_id=c.id, shared_symbols=shared, content_overlap=lexical))
    ranked.sort(key=lambda r: (-r['shared_symbols'], -r['content_overlap'], r['commitment_id']))
    return question, ranked


def fit_cq_request(calls, inputs):
    question, ranked = rank_cq(inputs)
    commitments = CommitmentSet.from_dict(inputs['commitments'])
    provenance = inputs.get('commitment_provenance')
    for limit in (16, 8, 4, 2, 1, 0):
        candidates = ranked[:limit]
        selected = [commitments.get(r['commitment_id']) for r in candidates]
        ids = {c.id for c in selected}
        referenced = set(s for c in selected for s in symbols(c.formula))
        data = {k:v for k,v in inputs.items() if k not in (
            'commitment_provenance','candidate_bridges','commitment_papers','bridge_policy')}
        data.update(commitments=CommitmentSet(tuple(selected)).to_dict(),
            commitments_scope='ranked_cq_slice_of_full_frozen_T', instantiated_question=question,
            symbol_catalogue=[s for s in inputs.get('symbol_catalogue') or []
                              if (s['name'],s['kind'],s['arity']) in referenced],
            commitment_roles={tid: {k:provenance['commitments'][tid][k] for k in
                ('stance','source_id','omitted_support_ids')} for tid in sorted(ids)} if provenance else None,
            cq_retrieval=dict(version='cq-retrieval-v1', limit=limit, candidates=candidates,
                total_candidates=len(ranked), total_commitments=len(commitments.commitments),
                stance='endorsed_only' if provenance else 'unavailable_legacy',
                ranking='shared_symbols_then_content_overlap_then_id',
                instruction='Candidates are leads, not proof. Cite any valid frozen T id; do not infer missing links.'))
        count = calls.count_request('answer_cq', data)
        total = count.initial_input_tokens + count.context_output_tokens
        fits = total <= calls.config['model_context_token_bound']
        calls.log.record('cq_context_slice', cq_id=inputs['question']['id'], bank_id=inputs['proposal']['bank_id'],
            limit=limit, candidates=candidates, total_candidates=len(ranked),
            input_tokens=count.initial_input_tokens, output_tokens=count.context_output_tokens,
            total_tokens=total, decision='fits' if fits else 'shrink' if limit else 'refused',
            inputs_sha256=digest(canonical(data)), commitments_sha256=inputs['commitments_sha256'])
        if fits:
            return data
    calls.count_request('answer_cq', data, admission=True)
    return data
