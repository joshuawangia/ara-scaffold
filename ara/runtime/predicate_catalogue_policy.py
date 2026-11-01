"""Small provisional catalogues gain authority only after shared source coverage."""
from copy import deepcopy
import re

from ara.runtime.cache import canonical,digest
from ara.runtime.calls import require
from ara.runtime.predicate_coverage import V3,coverage

CAPACITY={'sorts':12,'predicates':24}
MIN_PAPERS=2


def capacity_feedback(data):
    data=data if isinstance(data,dict) else {}
    counts={k:len(data[k]) if isinstance(data.get(k),list) else None for k in CAPACITY}
    sorts=[s for s in data.get('sorts',[]) if isinstance(s,dict)] if isinstance(data.get('sorts'),list) else []
    names={s['name'] for s in sorts if isinstance(s.get('name'),str)}
    dependencies=set()
    for p in data.get('predicates',[]) if isinstance(data.get('predicates'),list) else []:
        for r in p.get('roles',[]) if isinstance(p,dict) and isinstance(p.get('roles'),list) else []:
            if isinstance(r,dict) and isinstance(r.get('sort'),str):dependencies.add(r['sort'])
    stop={'the','a','an','of','at','to','in','and','or','with','as','for','by','on','is','that'}
    tokens=lambda s:set(re.findall(r'\w+',str(s.get('gloss','')).casefold()))-stop
    overlaps=[]
    for i,left in enumerate(sorts):
        for right in sorts[i+1:]:
            shared=sorted(tokens(left)&tokens(right))
            if shared:overlaps.append(dict(sorts=[left.get('name'),right.get('name')],shared_gloss_terms=shared))
    overlaps=sorted(overlaps,key=lambda r:(-len(r['shared_gloss_terms']),canonical(r)))[:6]
    message='; '.join(f'{k}: {counts[k]}; merge to <={limit}' for k,limit in CAPACITY.items())
    message+='; these sorts overlap (lexical candidates only): '+canonical(overlaps)
    return dict(counts=counts,limits=CAPACITY,dependency_sort_count=len(dependencies),
                dangling_sorts=sorted(dependencies-names),overlap_candidates=overlaps,message=message,
                instruction='No provisional entries are protected. Return a coherent bounded catalogue; count all role dependencies. '
                            'Overlap suggestions are not equivalence or permission to lose distinctions. Do not truncate or invent reuse.')


def vocabulary_key(data):
    from ara.runtime.commitment_provenance import _definition_screen_text
    def visible(text):return ' '.join(_definition_screen_text(text).split())
    # Local sort labels are aliases, not new meanings. Ordered role semantics stay explicit.
    sorts={s['name']:visible(s['gloss']) for s in data['sorts']}
    predicates=[dict(gloss=visible(p['gloss']),roles=[dict(role=visible(r['role']),sort=sorts[r['sort']])
                 for r in p['roles']]) for p in data['predicates']]
    return digest(canonical(dict(sorts=sorted(set(sorts.values())),predicates=sorted(predicates,key=canonical))))


def draft(data,history=()):
    from ara.runtime.shared_predicates import catalogue
    feedback=capacity_feedback(data)
    require(all(n is None or n<=CAPACITY[k] for k,n in feedback['counts'].items()),feedback['message'])
    entries=catalogue(data,version=V3)
    require(vocabulary_key(data) not in {vocabulary_key(p) for p in history},
            'unchanged provisional vocabulary cannot reroll coverage')
    return entries


def assess(data,check,sources):
    entries=draft(data)
    coverage(check,entries,len(sources))
    require(all(isinstance(s.get('source_id'),str) and s['source_id'] for s in sources),'coverage requires source provenance')
    uses={e['handle']:set() for e in entries}
    by_handle={e['handle']:e for e in entries}
    sorts={e['roles'][0]['sort']:e['handle'] for e in entries if e['kind']=='sort'}
    for source,row in zip(sources,check['coverage'],strict=True):
        for handle in row['handles']:
            uses[handle].add(source['source_id'])
            for role in by_handle[handle]['roles']:uses[sorts[role['sort']]].add(source['source_id'])
    deficient=[dict(handle=e['handle'],kind=e['kind'],gloss=e['gloss'],source_papers=sorted(uses[e['handle']]))
               for e in entries if len(uses[e['handle']])<MIN_PAPERS]
    return dict(accepted=all(r['covered'] for r in check['coverage']) and not deficient,
                missing_slots=[i for i,r in enumerate(check['coverage']) if not r['covered']],
                insufficient_shared_use=deficient,minimum_source_papers=MIN_PAPERS,
                source_use_by_handle={h:sorted(papers) for h,papers in uses.items()})


def catalogue_inputs(base,history,checks):
    result={**base,'policy_version':V3,'catalogue_capacity':CAPACITY,'minimum_source_papers':MIN_PAPERS}
    if history:result.update(mode='provisional_revision',revision=len(history),draft_catalogue=history[-1],
                            coverage_feedback={**assess(history[-1],checks[-1],base['sources']),
                                               'coverage':deepcopy(checks[-1])})
    return result


def coverage_inputs(base,data,revision):
    return dict(lifecycle_key=base['lifecycle_key'],policy_version=V3,sources=base['sources'],
                catalogue=draft(data),revision=revision,minimum_source_papers=MIN_PAPERS)


def protection(base,data,check,revision):
    result=assess(data,check,base['sources'])
    require(result['accepted'],'catalogue protection requires complete shared coverage')
    return dict(lifecycle_key=base['lifecycle_key'],revision=revision,
                catalogue_sha256=digest(canonical(data)),coverage_sha256=digest(canonical(check)),
                source_use_by_handle=result['source_use_by_handle'])


def prepare(calls,base):
    history=[];checks=[]
    for revision in range(3):
        entries,data=calls.call('predicate_catalogue',catalogue_inputs(base,history,checks),
                               lambda d:(draft(d,history),deepcopy(d)))
        history.append(data)
        check=calls.call('predicate_coverage',coverage_inputs(base,data,revision),
                         lambda d:coverage(d,entries,len(base['sources'])))
        checks.append(check)
        assessment=assess(data,check,base['sources'])
        calls.log.record('shared_predicate_coverage',revision=revision,catalogue=data,coverage=check,
                         assessment=assessment,note='Provisional model coverage; authority requires complete cross-paper use.')
        if assessment['accepted']:
            calls.log.record('shared_predicate_catalogue_protected',**protection(base,data,check,revision))
            return entries,data,history,checks
    raise ValueError('provisional catalogue lacks complete shared coverage after bounded revisions')


def replay(history,checks,sources):
    require(1<=len(history)<=3 and len(history)==len(checks),'invalid provisional catalogue history')
    for i,(data,check) in enumerate(zip(history,checks,strict=True)):
        draft(data,history[:i])
        assessment=assess(data,check,sources)
        require(assessment['accepted']==(i==len(history)-1),'invalid catalogue protection/coverage history')


def verify_protection(events,base,history,checks):
    expected=protection(base,history[-1],checks[-1],len(history)-1)
    import json
    found=[(i,json.loads(e['payload_json'])) for i,e in enumerate(events) if e['stage']=='shared_predicate_catalogue_protected']
    require(len(found)==1 and found[0][1]==expected,'catalogue protection receipt mismatch')
    position=found[0][0]
    from ara.runtime.predicate_receipts import model_inputs
    def accepted_positions(kind,inputs):
        return [i for i,e in enumerate(events) if e['stage']==kind and e['label']=='MODEL' and
                json.loads(e['payload_json']).get('status')=='accepted' and model_inputs(e)==inputs]
    previous=-1
    for revision,(data,check) in enumerate(zip(history,checks,strict=True)):
        cat=accepted_positions('predicate_catalogue',catalogue_inputs(base,history[:revision],checks[:revision]))
        cov=accepted_positions('predicate_coverage',coverage_inputs(base,data,revision))
        require(len(cat)==len(cov)==1,'catalogue protection requires unique accepted responses')
        require(previous<cat[0]<cov[0],'catalogue/coverage order mismatch')
        previous=cov[0]
    cover=[i for i,e in enumerate(events) if e['stage']=='predicate_coverage' and e['label']=='MODEL']
    formal=[i for i,e in enumerate(events) if (e['stage']=='predicate_formalize' and e['label']=='MODEL') or
            (e['stage']=='call_start' and json.loads(e['payload_json']).get('kind')=='predicate_formalize')]
    require(bool(cover) and max(cover)<position and (not formal or position<min(formal)),
            'catalogue protection order mismatch')
