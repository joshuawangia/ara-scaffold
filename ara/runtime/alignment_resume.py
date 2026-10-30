"""In-place alignment recovery from verified terminal-complete construction."""
from __future__ import annotations

import json
from types import SimpleNamespace

from ara.runtime.cache import canonical, digest
from ara.runtime.calls import require
from ara.runtime.commitment_provenance import make_commitment_provenance
from ara.runtime.construction_resume import load_construction_resume
from ara.runtime.frozen_catalogue import make_catalogue
from ara.runtime.providers import Response
from ara.runtime.symbol_alignment import (LEGACY_POLICY_VERSION, RETRIEVAL_POLICY_VERSION, POLICY_VERSION,
    _validate_judgments, _validate_unresolved, bind_judgment, candidate_inventory, legacy_candidate_pairs,
    retrieval_settings, unresolved_limit)
from ara.runtime.validation import decode_response
from ara.types import CommitmentSet


def load_alignment_resume(log, bank):
    """No provider or counter creation. Every reused output stays bound to its receipt."""
    directory=log.path.parent
    events=log.read()
    require(not any((directory/name).exists() for name in
        ('commitments.json','frozen-t.json','commitment-provenance.json')), 'alignment resume refuses an existing freeze artifact')
    return _load_alignment_resume(directory, events, bank)


def _load_alignment_resume(directory, events, bank):
    """Shared verifier for an authenticated pre-freeze prefix and its artifacts."""
    require(not any(e['stage'] in ('symbol_catalogue_frozen','commitment_provenance_frozen',
        'symbol_alignment_applied','symbol_alignment_refused') for e in events),
        'alignment resume requires unfinished alignment with no partial freeze')
    starts=[json.loads(e['payload_json']) for e in events if e['stage']=='run_started']
    require(len(starts)==1,'alignment resume requires one run configuration')
    run=starts[0]
    require(run['bank_version']==bank.bank_version,'alignment resume bank version mismatch')
    config=run['config']
    forks=[json.loads(e['payload_json']) for e in events if e['stage']=='construction_forked']
    if forks:
        config={**config,'hypothesis_premises':forks[-1]['hypotheses'],'cache_dir':forks[-1]['cache_dir']}
        run={**run,'config':config}
    log=SimpleNamespace(path=directory/'events.jsonl',read=lambda:events)
    state=load_construction_resume(SimpleNamespace(log=log,config=config),completed_only=True)
    merged=[(i,json.loads(e['payload_json'])) for i,e in enumerate(events) if e['stage']=='build_t_merged']
    require(len(merged)==1,'alignment resume requires one terminal merged receipt')
    offset,working=merged[0]
    require(working['plan_id']==state['plan_id'],'alignment resume merged plan mismatch')
    require(all(i<offset for i,e in enumerate(events) if e['stage'] in ('build_t_batch_accepted','build_t_batch_skipped')),
            'alignment resume merged receipt precedes terminal windows')
    expected={k:working[k] for k in ('plan_id','commitments','symbols','provenance')}
    require(json.loads((directory/f"working-t-{state['plan_id']}.json").read_text())==expected,
            'alignment resume working artifact mismatch')
    outcomes=list(state['completed'].values())
    commitments=CommitmentSet.from_dict({'commitments':sorted(
        [c for row in outcomes for c in row.get('commitments',[])],key=lambda c:c['id'])})
    symbols=[s for row in outcomes for s in row.get('new_symbols',[])]
    rows={id:p for row in outcomes for id,p in row.get('provenance',{}).items()}
    require(commitments.to_dict()==working['commitments'] and symbols==working['symbols'] and rows==working['provenance'],
            'alignment resume terminal merge mismatch')
    catalogue=make_catalogue(commitments,symbols)
    make_commitment_provenance(commitments,catalogue,rows)
    inventory=candidate_inventory(symbols,rows,config.get('construction_alignment_candidates',150),**retrieval_settings(config))
    candidates=inventory.pop('candidates')
    names={s['name']:s for s in symbols}
    pairs={(p['left'],p['right']):p for p in candidates}
    accepted,unresolved,rejections={},{},{}
    restored_receipts=[]
    recorded_inventory=False
    for event in events[offset+1:]:
        data=json.loads(event['payload_json'])
        if event['stage']=='symbol_alignment_candidates':
            require(data['policy_version'] in (LEGACY_POLICY_VERSION,RETRIEVAL_POLICY_VERSION,POLICY_VERSION),
                    'alignment resume unsupported candidate policy')
            original=(legacy_candidate_pairs(symbols,rows,data['limit']) if data['policy_version']==LEGACY_POLICY_VERSION
                      else candidates)
            require(data['candidates']==original==candidates and data['limit']==config.get('construction_alignment_candidates',150)
                    and data['commitments_sha256']==catalogue['commitments_sha256'] and data['catalogue_sha256']==catalogue['sha256'],
                    'alignment resume candidate receipt mismatch')
            if data['policy_version']!=LEGACY_POLICY_VERSION:
                require(data['retrieval']==inventory,'alignment resume retrieval receipt mismatch')
            recorded_inventory=True
        elif event['stage']=='judge_symbol_alignment' and event['label']=='MODEL':
            require(recorded_inventory,'alignment resume lacks candidate receipt')
            inputs=json.loads(event['prompt'].split('\nINPUT_JSON\n')[1])
            pair=(inputs['candidate']['left']['name'],inputs['candidate']['right']['name'])
            require(pair in pairs,'alignment resume accepted an unknown candidate')
            left,right=(names[n] for n in pair)
            require(inputs.get('topic')=='' and inputs['candidate']==dict(left=left,right=right,score=pairs[pair]['score'])
                and inputs['sources']=={id:rows[id] for id in sorted(set(left['evidence_ids']+right['evidence_ids']))}
                and inputs['commitments_sha256']==catalogue['commitments_sha256'] and inputs['catalogue_sha256']==catalogue['sha256'],
                'alignment resume judgment input binding mismatch')
            if data.get('status')!='accepted':
                if data.get('attempt')==1: rejections[pair]=[]
                if data.get('status')=='rejected' and event['response'] is not None and data.get('accounting')=='actual':
                    rejections.setdefault(pair,[]).append(data)
                continue
            raw=json.loads(event['response'])
            require(raw['stop_reason']=='end_turn','alignment resume incomplete accepted response')
            value=decode_response(Response(raw).text())
            version=inputs['policy_version']
            require(version in (LEGACY_POLICY_VERSION,RETRIEVAL_POLICY_VERSION,POLICY_VERSION),
                    'alignment resume unsupported judgment policy')
            if version==POLICY_VERSION:
                value=bind_judgment(value,pairs[pair])
            _validate_judgments(symbols,rows,[value])
            require((value['left'],value['right'])==pair,'alignment resume judgment changed candidate')
            require(pair not in unresolved and (pair not in accepted or accepted[pair]==value),
                    'alignment resume conflicting candidate outcomes')
            accepted[pair]=value
            restored_receipts.append(digest(canonical(event)))
        elif event['stage']=='alignment_unresolved':
            _validate_unresolved([data])
            pair=(data['left'],data['right'])
            require(recorded_inventory and pair in pairs and pair not in accepted and pair not in unresolved,
                    'alignment resume unresolved candidate mismatch')
            rejected=rejections.get(pair,[])
            require(data['attempts']==config.get('validation_attempts',1) and
                [r.get('attempt') for r in rejected]==list(range(1,data['attempts']+1)) and
                rejected[-1].get('reason')==data['reason'],
                'alignment resume unresolved outcome lacks exhausted rejected attempts')
            unresolved[pair]=data
    return dict(run=run,commitments=commitments,symbols=symbols,provenance=rows,
                candidates=candidates,judgments=[accepted[p] for p in pairs if p in accepted],
                unresolved=[unresolved[p] for p in pairs if p in unresolved],
                plan_id=state['plan_id'],completed_windows=len(outcomes),restored_receipts=restored_receipts,
                merged_receipt=digest(canonical(events[offset])),source_tail=digest(canonical(events[-1])),
                expected_source=forks[-1]['expected_source'] if forks else None)


def resume_summary(state):
    return dict(plan_id=state['plan_id'],completed_windows=state['completed_windows'],
        restored_commitments=len(state['commitments'].commitments),candidate_count=len(state['candidates']),
        accepted_judgments=len(state['judgments']),unresolved_count=len(state['unresolved']),
        unresolved_limit=unresolved_limit(state['run']['config']),
        remaining_candidates=len(state['candidates'])-len(state['judgments'])-len(state['unresolved']),
        restored_receipts=state['restored_receipts'],merged_receipt=state['merged_receipt'],source_tail=state['source_tail'],
        generation_calls=0,policy_version=POLICY_VERSION,
        note='Verified construction and candidate receipts only; no provider or token counter. Live preflight, budgets, final consistency and target/search admission remain required.')
