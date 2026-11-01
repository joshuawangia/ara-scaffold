"""Small verified source selections, without copying unrelated historical journals."""
from copy import deepcopy
from pathlib import Path

from ara.runtime.cache import canonical, digest
from ara.runtime.calls import require
from ara.runtime.construction_fork import inspect_construction_fork
from ara.runtime.extraction import save_immutable
from ara.runtime.shared_predicates import policy, symbols_for
from ara.runtime.vocabulary_consolidation import evidence_items
from ara.types import CommitmentSet


def inspect_selection(source,destination,bank,selection):
    require(isinstance(selection,dict) and set(selection)=={'commitment_ids','max_unresolved','failure_streak'},
            'invalid shared predicate selection fields')
    ids=selection['commitment_ids']
    require(isinstance(ids,list) and 1<=len(ids)<=64 and all(isinstance(i,str) for i in ids) and len(ids)==len(set(ids)),
            'invalid selected commitment inventory')
    # Reuse the native verification of completed construction, frozen source
    # provenance, alignment receipts, source anchor and exact prefix. No write.
    plan=inspect_construction_fork(source,destination,bank,[],consolidation={
        'construction_consolidate_vocabulary':True,'consolidation_batch_size':64})
    state=plan['state'];available={c.id:c for c in state['commitments'].commitments}
    require(set(ids)<=set(available),'selected source commitment unavailable')
    t=CommitmentSet(tuple(available[id] for id in sorted(ids)))
    rows={c.id:deepcopy(state['provenance'][c.id]) for c in t.commitments}
    symbols=symbols_for(t,state['symbols'],[])
    evidence={id:item for id,item in evidence_items(state['run']['literature'],state['provenance']).items() if id in rows}
    require(all(row.get('source_id') for row in rows.values()),'selection includes non-source commitments')
    config={**state['run']['config'],'cache_dir':str(Path(destination).absolute()/'cache'),
            'construction_consolidate_vocabulary':False,'construction_shared_predicates':True,'hypothesis_premises':[],
            'shared_predicates_version':'shared-predicate-formalization-v3',
            'shared_predicates_max_unresolved':selection['max_unresolved'],
            'shared_predicates_failure_streak':selection['failure_streak']}
    policy(config)
    payload=dict(schema_version='shared-predicate-source-selection-v1',source_run=str(Path(source).resolve()),
        source_tail=plan['receipt']['source_tail'],source_prefix_sha256=plan['receipt']['prefix_sha256'],
        source_artifacts=plan['receipt']['artifacts'],selection=selection,commitments=t.to_dict(),symbols=symbols,
        provenance=rows,evidence=evidence,bank_version=bank.bank_version,
        note='New selected lifecycle; original source receipts verified natively, not copied or re-accounted. No extraction or model generation.')
    receipt={**payload,'sha256':digest(canonical(payload))}
    run={**state['run'],'config':config,'literature':'Verified accepted source selection; full evidence in shared_predicate_source receipt.'}
    return dict(receipt=receipt,run=run,commitments=t,symbols=symbols,rows=rows,evidence=evidence)


def initialize(plan,destination):
    from ara.runtime.logging import EventLog
    from ara.runtime.construction_fork import separate_destination
    separate_destination(plan['receipt']['source_run'],destination)
    log=EventLog(Path(destination)/'events.jsonl')
    log.record('run_started',**plan['run'])
    log.record('shared_predicate_source',**plan['receipt'])
    save_immutable(Path(destination)/'shared-predicate-source.json',canonical(plan['receipt']))
    log.record('build_t_merged',commitments=plan['commitments'].to_dict(),symbols=plan['symbols'],provenance=plan['rows'],
               note='Verified selected accepted source formulas, before shared-predicate formalization.')
    return log


def validate_selected_origin(events,provenance):
    """The compact source-selection receipt must bind the frozen re-formalization."""
    import json
    receipt=provenance.get('consolidation') if provenance else None
    if not receipt or receipt.get('schema_version') not in ('shared-predicate-formalization-v1','shared-predicate-formalization-v2','shared-predicate-formalization-v3'):return
    origins=[json.loads(e['payload_json']) for e in events if e['stage']=='shared_predicate_source']
    if not origins:
        merges=[json.loads(e['payload_json']) for e in events if e['stage']=='build_t_merged']
        require(len(merges)==1 and merges[0]['commitments']==receipt['original_commitments'] and
                merges[0]['symbols']==receipt['original_symbols'] and merges[0]['provenance']==receipt['provenance'],
                'shared predicate freeze requires a bound construction origin')
        return
    require(len(origins)==1,'shared predicate freeze requires one selected-source receipt')
    origin=origins[0]
    require(origin.get('sha256')==digest(canonical({k:v for k,v in origin.items() if k!='sha256'})),
            'selected-source receipt hash mismatch')
    require(origin['commitments']==receipt['original_commitments'] and origin['symbols']==receipt['original_symbols']
            and origin['provenance']==receipt['provenance'] and origin['evidence']==receipt['evidence'],
            'shared predicate selected-source binding mismatch')
    import tempfile
    from ara.bank import load_bank
    from ara.runtime.shared_predicates import ROOT
    with tempfile.TemporaryDirectory(prefix='ara-shared-source-verify-') as temporary:
        checked=inspect_selection(origin['source_run'],Path(temporary),load_bank(ROOT/'bank'),origin['selection'])
    require(checked['receipt']==origin,'retained shared predicate source changed')
