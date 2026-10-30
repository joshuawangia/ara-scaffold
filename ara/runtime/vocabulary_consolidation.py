"""Opt-in re-formalization of accepted content; never a source-premise rewrite."""
from copy import deepcopy
from dataclasses import replace
import json
import re

from ara.runtime.cache import canonical, digest
from ara.runtime.calls import require
from ara.runtime.construction import formula_symbols
from ara.runtime.extraction import HEADER, save_immutable
from ara.runtime.frozen_catalogue import make_catalogue
from ara.runtime.shared_vocabulary import vocabulary_metrics
from ara.types import CommitmentSet, Formula

VERSION = 'vocabulary-consolidation-v1'
CONFIG_KEYS = {'construction_consolidate_vocabulary', 'consolidation_batch_size',
               'construction_alignment_candidates', 'construction_alignment_top_k',
               'construction_alignment_min_score', 'construction_alignment_paper_diversity',
               'construction_alignment_max_unresolved'}


def policy(config):
    enabled = config.get('construction_consolidate_vocabulary', False)
    require(type(enabled) is bool, 'construction_consolidate_vocabulary must be boolean')
    size = config.get('consolidation_batch_size', 16)
    require(type(size) is int and 1 <= size <= 64, 'consolidation_batch_size must be between 1 and 64')
    require(not any(isinstance(v, dict) and any(k in v for k in
        ('construction_consolidate_vocabulary','consolidation_batch_size')) for v in config.get('stages',{}).values()),
        'consolidation settings are run-level only')
    return dict(version=VERSION, batch_size=size, grouping='lexical-overlap-cross-source-first-v1') if enabled else None


def config_override(value):
    require(isinstance(value,dict) and set(value)<=CONFIG_KEYS, 'invalid consolidation config fields')
    require(policy(value) is not None, 'consolidation config must explicitly enable consolidation')
    from ara.runtime.symbol_alignment import retrieval_settings, unresolved_limit
    retrieval_settings(value);unresolved_limit(value)
    require(type(value.get('construction_alignment_candidates',150)) is int and
            value.get('construction_alignment_candidates',150)>=0, 'invalid alignment candidate limit')
    return deepcopy(value)


def evidence_items(literature, rows):
    if isinstance(literature,dict):
        require(set(literature)==set(rows), 'consolidation evidence inventory mismatch')
        return literature
    if literature.startswith(HEADER):
        papers=json.loads(literature[len(HEADER):])['papers']
        items={i['id']:i for p in papers for i in p['items']}
        require(set(rows)<=set(items), 'consolidation source evidence unavailable')
        return {id:items[id] for id in sorted(rows)}
    # Legacy plain-text construction has provenance but no extraction graph.
    return {id:dict(id=id,kind=r['source_kind'],premise_ids=[],conclusion_id=None,
                    qualification_ids=[],applies_to=[]) for id,r in rows.items()}


def make_plan(commitments, symbols, rows, config, literature):
    settings=policy(config)
    require(settings is not None, 'consolidation is not enabled')
    make_catalogue(commitments,symbols)
    ids={c.id for c in commitments.commitments}
    require(ids==set(rows) and all(r.get('source_id') for r in rows.values()),
            'consolidation requires accepted source commitments only')
    items=evidence_items(literature,rows)
    # Keep accepted inference endpoints/qualifications together. No formula or
    # semantic equivalence is inferred by lexical scheduling.
    groups={id:{id} for id in ids}
    for id in sorted(ids):
        item=items[id]
        linked=({*item.get('premise_ids',[]),item.get('conclusion_id'),
                 *item.get('qualification_ids',[]),*item.get('applies_to',[])} & ids)
        for other in sorted(linked):
            joined=groups[id]|groups[other]
            for member in joined:groups[member]=joined
    units=sorted({tuple(sorted(g)) for g in groups.values()})
    require(all(len(u)<=settings['batch_size'] for u in units),
            'consolidation dependency component exceeds batch size; raise bound or refuse, never cut it')
    by_id={c.id:c for c in commitments.commitments}
    words={id:set(re.findall(r'\w+',c.text.casefold())) for id,c in by_id.items()}
    batches=[]
    while units:
        selected=list(units.pop(0))
        while units:
            room=settings['batch_size']-len(selected)
            eligible=[u for u in units if len(u)<=room]
            if not eligible:break
            terms=set().union(*(words[id] for id in selected))
            sources={rows[id]['source_id'] for id in selected}
            def rank(unit):
                tokens=set().union(*(words[id] for id in unit))
                cross=bool({rows[id]['source_id'] for id in unit}-sources)
                score=len(tokens & terms)/max(1,len(tokens | terms))
                return (-int(cross),-score,unit)
            chosen=min(eligible,key=rank);units.remove(chosen);selected.extend(chosen)
        batches.append(sorted(selected))
    payload=dict(policy=settings,original_commitments_sha256=digest(canonical(commitments.to_dict())),
        original_catalogue_sha256=make_catalogue(commitments,symbols)['sha256'],
        provenance_sha256=digest(canonical(rows)),evidence_sha256=digest(canonical(items)),
        batches=batches,before=vocabulary_metrics(commitments,symbols,rows),after=None,generation_calls=0,
        note='Deterministic lexical topic scheduling only; no new formulas or semantic judgments in plan-only mode.')
    return {**payload,'plan_id':digest(canonical(payload))}


def batch_inputs(plan, index, original, original_symbols, rows, current, symbols, items):
    ids=set(plan['batches'][index])
    return dict(mode='vocabulary_consolidation',consolidation_plan_id=plan['plan_id'],batch_index=index,
        accepted_commitments=CommitmentSet(tuple(c for c in original.commitments if c.id in ids)).to_dict(),
        original_catalogue=original_symbols,source_provenance={id:rows[id] for id in sorted(ids)},
        source_evidence=[items[id] for id in sorted(ids)],
        existing_commitments=current.to_dict()['commitments'],shared_symbols=symbols,
        commitments_sha256=plan['original_commitments_sha256'],provenance_sha256=plan['provenance_sha256'])


def validate_batch(data, inputs, original, prior, symbols, rows):
    """The normal formula/catalogue/stance gates, with stricter immutable text."""
    from ara.runtime.commitment_provenance import content_definition, PRECISE_SCREEN
    from ara.runtime.symbol_alignment import _consistent
    expected={c['id']:c for c in inputs['accepted_commitments']['commitments']}
    ids=[c['id'] for c in data['commitments']]
    require(len(ids)==len(set(ids)) and set(ids)==set(expected), 'consolidation inventory mismatch')
    require(all(c['definition']==expected[c['id']]['text'] for c in data['commitments']),
            'consolidation changed accepted text')
    originals={c.id:c for c in original.commitments}
    fresh=CommitmentSet(tuple(replace(originals[c['id']],formula=Formula.from_dict(c['formula'])) for c in data['commitments']))
    combined=CommitmentSet(tuple(sorted((*prior.commitments,*fresh.commitments),key=lambda c:c.id)))
    new=data['new_symbols'];catalogue=symbols+new
    require(len({s['name'] for s in catalogue})==len(catalogue), 'consolidation duplicate symbol')
    used={}
    for c in fresh.commitments:
        for name,kind,arity in formula_symbols(c.formula):used.setdefault(name,set()).add(c.id)
    old_names={s['name'] for s in symbols}
    require({a['name'] for a in data['alignments']}==set(used)&old_names and
            len(data['alignments'])==len({a['name'] for a in data['alignments']}) and
            all(a['reason'].strip() for a in data['alignments']), 'consolidation reuse judgment mismatch')
    for s in new:
        require(s['name'] in used and set(s['evidence_ids'])==used[s['name']],
                'consolidation symbol evidence must bind its actual accepted uses')
        screen=PRECISE_SCREEN if all(rows[id].get('definition_screen')==PRECISE_SCREEN for id in s['evidence_ids']) else None
        require(content_definition(s['definition'],screen=screen), 'consolidation symbol is not content')
    make_catalogue(combined,catalogue)  # Exact signature inventory and locally bound variables.
    require(all(_consistent(CommitmentSet((c,))) for c in fresh.commitments) and
            _consistent(CommitmentSet(tuple(c for c in combined.commitments if rows[c.id]['stance']=='endorsed'))),
            'consolidation consistency not established (unsat or unknown)')
    from ara.runtime.construction_structure import structure_gate
    items={i['id']:i for i in inputs['source_evidence']}
    metrics=structure_gate(fresh,prior,items)
    # Faithful atoms are allowed; an asserted conditional must reuse its endpoints.
    require(not any(i['reason']!='inference_requires_conditional' for i in metrics['issues']),
            'consolidation conditional endpoint mismatch')
    return combined,catalogue,metrics


def validate_receipt(receipt, final, symbols, rows):
    """Replay every formalization; return original T/catalogue for source history checks."""
    from ara.runtime.validation import validate_local
    from pathlib import Path
    fields={'schema_version','plan','original_commitments','original_symbols','provenance',
            'evidence','batches','commitments','symbols','before','after','sha256'}
    require(isinstance(receipt,dict) and set(receipt)==fields and receipt['schema_version']==VERSION,
            'invalid consolidation receipt')
    require(receipt['sha256']==digest(canonical({k:v for k,v in receipt.items() if k!='sha256'})),
            'consolidation receipt hash mismatch')
    original=CommitmentSet.from_dict(receipt['original_commitments']);source_rows=receipt['provenance']
    config=dict(construction_consolidate_vocabulary=True,consolidation_batch_size=receipt['plan']['policy']['batch_size'])
    plan=make_plan(original,receipt['original_symbols'],source_rows,config,receipt['evidence'])
    require(plan==receipt['plan'], 'consolidation plan mismatch')
    require({id:rows[id] for id in source_rows}==source_rows, 'consolidation changed source provenance')
    from ara.runtime.commitment_provenance import make_commitment_provenance
    make_commitment_provenance(original,make_catalogue(original,receipt['original_symbols']),source_rows)
    current=CommitmentSet(());catalogue=[];items=evidence_items(receipt['evidence'],source_rows)
    schema=json.loads((Path(__file__).resolve().parents[2]/'schemas/build_t_batch.json').read_text())
    require(len(receipt['batches'])==len(plan['batches']), 'consolidation missing batch')
    for index,batch in enumerate(receipt['batches']):
        inputs=batch_inputs(plan,index,original,receipt['original_symbols'],source_rows,current,catalogue,items)
        require(set(batch)=={'index','input_sha256','response','structure'} and batch['index']==index and
                batch['input_sha256']==digest(canonical(inputs)), 'consolidation batch input mismatch')
        validate_local(schema,batch['response'])
        current,catalogue,structure=validate_batch(batch['response'],inputs,original,current,catalogue,source_rows)
        require(structure==batch['structure'], 'consolidation structure receipt mismatch')
    require(current==final and receipt['commitments']==final.to_dict() and receipt['symbols']==catalogue and
            make_catalogue(final,symbols)==make_catalogue(current,catalogue), 'consolidation output mismatch')
    require(receipt['before']==plan['before'] and receipt['after']==vocabulary_metrics(current,catalogue,source_rows),
            'consolidation metric mismatch')
    return original,receipt['original_symbols']


def restored_receipt(events, original, symbols, rows, config, literature):
    applied=[json.loads(e['payload_json']) for e in events if e['stage']=='vocabulary_consolidated']
    require(len(applied)<=1, 'duplicate consolidation receipt')
    if not applied:return None
    receipt=applied[0];final=CommitmentSet.from_dict(receipt['commitments'])
    before,before_symbols=validate_receipt(receipt,final,receipt['symbols'],rows)
    require(before==original and before_symbols==symbols and receipt['plan']==make_plan(original,symbols,rows,config,literature),
            'consolidation restored source mismatch')
    return receipt


def consolidate(calls, original, original_symbols, rows, literature):
    if policy(calls.config) is None:return original,original_symbols,rows,None
    events=calls.log.read()
    restored=restored_receipt(events,original,original_symbols,rows,calls.config,literature)
    if restored:return CommitmentSet.from_dict(restored['commitments']),restored['symbols'],rows,restored
    plan=make_plan(original,original_symbols,rows,calls.config,literature)
    calls.log.record('vocabulary_consolidation_plan',**plan)
    current=CommitmentSet(());symbols=[];batches=[];items=evidence_items(literature,rows)
    for index in range(len(plan['batches'])):
        inputs=batch_inputs(plan,index,original,original_symbols,rows,current,symbols,items)
        calls.count_request('build_t_batch',inputs,admission=True)
        def check(data):
            result,catalogue,structure=validate_batch(data,inputs,original,current,symbols,rows)
            measured=calls.count_request('propose_targets',dict(commitments=result.to_dict(),count=calls.config['target_candidates'],named_position=None),admission=True)
            require(measured.initial_input_tokens<=calls.config['working_t_token_budget'] and measured.initial_input_tokens+measured.context_output_tokens<=calls.config['model_context_token_bound'],
                    'consolidation working T capacity exceeded')
            baseline=calls.count_request('build_t_batch',{**inputs,'accepted_commitments':{'commitments':[]},'original_catalogue':[],'shared_symbols':[]})
            counted=calls.count_request('build_t_batch',{**inputs,'accepted_commitments':{'commitments':[]},'original_catalogue':[],'shared_symbols':catalogue})
            require(counted.initial_input_tokens-baseline.initial_input_tokens<=calls.config['working_t_symbol_token_budget'],
                    'consolidation catalogue capacity exceeded')
            return result,catalogue,structure,deepcopy(data)
        current,symbols,structure,data=calls.call('build_t_batch',inputs,check)
        batch=dict(index=index,input_sha256=digest(canonical(inputs)),response=data,structure=structure)
        batches.append(batch)
        calls.log.record('vocabulary_consolidation_batch',plan_id=plan['plan_id'],**batch,
            note='Predicate reuse and formula interpretation are model judgments; accepted source content is unchanged.')
    payload=dict(schema_version=VERSION,plan=plan,original_commitments=original.to_dict(),original_symbols=original_symbols,
        provenance=rows,evidence=items,batches=batches,commitments=current.to_dict(),symbols=symbols,
        before=plan['before'],after=vocabulary_metrics(current,symbols,rows))
    receipt={**payload,'sha256':digest(canonical(payload))}
    validate_receipt(receipt,current,symbols,rows)
    save_immutable(calls.log.path.parent/'vocabulary-consolidation.json',canonical(receipt))
    calls.log.record('vocabulary_consolidated',**receipt)
    return current,symbols,rows,receipt
