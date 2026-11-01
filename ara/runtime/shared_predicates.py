"""Catalogue-first, independently judged decompositions of immutable source content."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import json

from ara.runtime.cache import canonical, digest
from ara.runtime.calls import require, InvalidOutput
from ara.runtime.construction import formula_symbols
from ara.runtime.extraction import save_immutable
from ara.runtime.frozen_catalogue import make_catalogue
from ara.runtime.shared_vocabulary import vocabulary_metrics
from ara.runtime.symbol_alignment import _consistent
from ara.runtime.validation import validate_local
from ara.types import CommitmentSet, Formula

VERSION = 'shared-predicate-formalization-v1'
from ara.runtime.predicate_coverage import V2,V3,MANDATORY
VERSIONS=(VERSION,V2,V3)
KINDS = ('predicate_catalogue','predicate_coverage','predicate_formalize','predicate_backtranslate','predicate_fidelity')
ROOT = Path(__file__).resolve().parents[2]


def policy(config):
    enabled=config.get('construction_shared_predicates',False)
    require(type(enabled) is bool,'construction_shared_predicates must be boolean')
    if not enabled:return None
    require(not config.get('construction_consolidate_vocabulary') and not config.get('hypothesis_premises'),
            'shared predicates require a separate source-only lifecycle')
    limit=config.get('shared_predicates_max_unresolved',3)
    streak=config.get('shared_predicates_failure_streak',5)
    require(type(limit) is int and 0<=limit<=64,'invalid shared predicate unresolved limit')
    require(type(streak) is int and 1<=streak<=64,'invalid shared predicate failure streak')
    require(not any(any(k.startswith('shared_predicates_') or k=='construction_shared_predicates' for k in stage)
                    for stage in config.get('stages',{}).values() if isinstance(stage,dict)),
            'shared predicate policy is run-level only')
    version=config.get('shared_predicates_version',V3)
    require(version in VERSIONS,'unknown shared predicate policy version')
    result=dict(version=version,max_unresolved=limit,failure_streak=streak,judges=3,
                types='explicit-unary-guards-v1',failure='retain-original',alignment='disabled')
    if version==V3:
        from ara.runtime.predicate_catalogue_policy import CAPACITY,MIN_PAPERS
        result.update(catalogue_capacity=deepcopy(CAPACITY),minimum_source_papers=MIN_PAPERS,
                      catalogue_protection='after-complete-shared-coverage')
    return result


def schema_check(kind,data):
    validate_local(json.loads((ROOT/f'schemas/{kind}.json').read_text()),data)


def catalogue(data,*,version=VERSION):
    """Key proposed meanings, not model-supplied IDs. No lexical semantic merge."""
    from ara.runtime.commitment_provenance import content_definition, PRECISE_SCREEN
    from ara.runtime.predicate_coverage import catalogue_definition
    def definition_ok(text):
        return catalogue_definition(text) if version in MANDATORY else content_definition(text,screen=PRECISE_SCREEN)
    schema_check('predicate_catalogue',data)
    sorts=data['sorts'];names=[s['name'] for s in sorts]
    require(len(set(names))==len(names),'duplicate sort name')
    result=[]
    for i,s in enumerate(sorts):
        require(definition_ok(s['gloss']),'sort gloss report frame or unsupported formatting')
        result.append(dict(handle=f't{i}',name='SPT_'+digest(canonical(s))[:24],kind='sort',
                           gloss=s['gloss'],roles=[dict(role='member',sort=s['name'])]))
    for i,p in enumerate(data['predicates']):
        require(definition_ok(p['gloss']),'predicate gloss report frame or unsupported formatting')
        require(all(r['sort'] in names for r in p['roles']),'unknown role sort')
        require(len({r['role'] for r in p['roles']})==len(p['roles']),'duplicate argument role')
        full_definition=p['gloss']+' [roles: '+', '.join(r['role']+':'+r['sort'] for r in p['roles'])+']'
        require(definition_ok(full_definition),'predicate role report frame or unsupported formatting')
        key=dict(gloss=p['gloss'],roles=p['roles'])
        result.append(dict(handle=f'p{i}',name='SPP_'+digest(canonical(key))[:24],kind='relation',**p))
    require(len({s['name'] for s in result})==len(result),'duplicate catalogue meaning key')
    return result


def typed_formula(value,entries):
    """Validate guarded one-sorted FOL, then bind handles without changing structure."""
    f=Formula.from_dict(value);by_handle={s['handle']:s for s in entries}
    used_relations=set()
    def visit(node,env):
        require(node.op!='atom','private atoms forbidden; propose a structured formula')
        if node.op=='predicate':
            require(node.name in by_handle,'unknown predicate handle: '+str(node.name))
            entry=by_handle[node.name]
            require(len(node.terms)==len(entry['roles']),'predicate arity mismatch: '+node.name)
            for term,role in zip(node.terms,entry['roles'],strict=True):
                require(term.kind=='variable' and term.name in env,'only bound variable terms are supported')
                require(env[term.name]==role['sort'],'argument sort mismatch: '+node.name+'/'+role['role'])
            if entry['kind']=='relation':used_relations.add(entry['handle'])
        if node.op in ('forall','exists'):
            require(node.variable not in env,'shadowed variable')
            body=node.args[0]
            shape='implies' if node.op=='forall' else 'and'
            require(body.op==shape,'quantifier requires explicit sort guard')
            guard=body.args[0]
            require(guard.op=='predicate' and guard.name in by_handle and by_handle[guard.name]['kind']=='sort'
                    and len(guard.terms)==1 and guard.terms[0].kind=='variable' and guard.terms[0].name==node.variable,
                    'quantifier requires leading unary sort guard')
            env={**env,node.variable:by_handle[guard.name]['roles'][0]['sort']}
        for child in node.args:visit(child,env)
    visit(f,{})
    require(bool(used_relations),'decomposition must use a content predicate')
    def bind(node):
        return replace(node,name=by_handle[node.name]['name'] if node.op=='predicate' else node.name,
                       args=tuple(bind(a) for a in node.args))
    return bind(f)


def candidate(data,entries,*,version=VERSION):
    schema_check('predicate_formalize',data)
    require(bool(data['reason'].strip()),'formalization requires a reason')
    if version in MANDATORY:require(data['mode']=='decompose' and data['formula'] is not None,'structured proposal mandatory')
    if data['mode']=='retain':
        require(data['formula'] is None,'retain response must not supply a formula')
        return None
    require(data['formula'] is not None,'decomposition requires a formula')
    return typed_formula(data['formula'],entries)


def fidelity(judgments):
    require(len(judgments)==3,'three fidelity judgments required')
    for j in judgments:schema_check('predicate_fidelity',j)
    return all(j['equivalent'] and j['preserves_scope'] and j['no_additions'] and j['reason'].strip() for j in judgments)


def symbols_for(t,original_symbols,entries):
    definitions={s['name']:s for s in original_symbols}
    for e in entries:
        roles=', '.join(r['role']+':'+r['sort'] for r in e['roles'])
        definitions[e['name']]=dict(name=e['name'],kind='predicate',arity=len(e['roles']),
            definition=e['gloss']+' [roles: '+roles+']')
    uses={}
    for c in t.commitments:
        for name,kind,arity in formula_symbols(c.formula):uses.setdefault(name,set()).add(c.id)
    result=[{**definitions[name],'evidence_ids':sorted(ids)} for name,ids in sorted(uses.items())]
    make_catalogue(t,result)
    return result


def metrics(t,symbols,rows,entries,items,*,version=VERSION):
    result=vocabulary_metrics(t,symbols,rows)
    from collections import defaultdict
    uses=defaultdict(set);all_uses=defaultdict(set)
    admitted_ids={i['id'] for i in items if i['status']=='admitted'}
    content={e['name'] for e in entries if e['kind']=='relation'}
    for c in t.commitments:
        for name,_,_ in formula_symbols(c.formula):
            if rows[c.id].get('source_id'):
                all_uses[name].add(rows[c.id]['source_id'])
                if c.id in admitted_ids and rows[c.id]['stance']=='endorsed':uses[name].add(rows[c.id]['source_id'])
    accepted=sum(i['status']=='admitted' for i in items)
    result.update(shared_content_predicates=sum(len(uses[n])>=2 for n in content),
                  shared_content_predicates_all_stances=sum(len(all_uses[n])>=2 for n in content),
                  shared_content_scope='admitted decompositions in endorsed SOURCE papers only; all-stance actual uses separate',
                  admitted=accepted,unresolved=len(items)-accepted,
                  faithful_fraction=accepted/len(items) if items else 0,
                  fidelity_scope='unanimous three model judgments; not independent semantic certification',
                  atomic_cost=sum(c.formula.op=='atom' for c in t.commitments))
    if version in MANDATORY:
        judged=sum(len(i['judgments'])==3 for i in items)
        result.update(proposed=sum(i['candidate'] is not None for i in items),judged=judged,
                      current_judgments_passed=sum(fidelity(i['judgments']) for i in items if len(i['judgments'])==3),
                      judged_fraction=judged/len(items) if items else 0)
    return result


def admit_item(original,current,rows,entries,item,*,version=VERSION):
    """Replay structural, fidelity and full endorsed-set gates for one source item."""
    require(set(item)=={'id','status','candidate','translation','judgments','reason'},'invalid predicate item fields')
    require(item['id']==original.id and item['status'] in ('admitted','unresolved') and item['reason'].strip(),
            'invalid predicate item identity/status')
    f=candidate(item['candidate'],entries,version=version) if item['candidate'] is not None else None
    if item['translation'] is not None:schema_check('predicate_backtranslate',item['translation'])
    for judgment in item['judgments']:schema_check('predicate_fidelity',judgment)
    require(len(item['judgments']) in (0,3),'incomplete fidelity record')
    if version in MANDATORY:
        require(f is not None and item['translation'] is not None and len(item['judgments'])==3,
                'mandatory proposal and complete fidelity measurement required')
    if item['status']=='unresolved':
        if version in MANDATORY:
            require(item['reason'] in ('adverse_fidelity','adverse_fidelity_history','shared predicate consistency not established'),
                    'unresolved proposal requires a fidelity or consistency rejection')
            if item['reason']=='adverse_fidelity':require(not fidelity(item['judgments']),'unresolved fidelity mismatch')
            if item['reason']=='adverse_fidelity_history':require(fidelity(item['judgments']),'unresolved history mismatch')
            if item['reason']=='shared predicate consistency not established':
                proposed=CommitmentSet(tuple(replace(c,formula=f) if c.id==original.id else c for c in current.commitments))
                require(not (_consistent(CommitmentSet((replace(original,formula=f),))) and
                    _consistent(CommitmentSet(tuple(c for c in proposed.commitments if rows[c.id]['stance']=='endorsed')))),
                    'unresolved consistency mismatch')
        return current
    require(f is not None and item['translation'] is not None and item['translation']['text'].strip(),
            'admission requires candidate and blind translation')
    require(fidelity(item['judgments']),'adverse fidelity judgment')
    updated=CommitmentSet(tuple(replace(c,formula=f) if c.id==original.id else c for c in current.commitments))
    require(_consistent(CommitmentSet((replace(original,formula=f),))) and
            _consistent(CommitmentSet(tuple(c for c in updated.commitments if rows[c.id]['stance']=='endorsed'))),
            'shared predicate consistency not established')
    return updated


def validate_receipt(receipt,final,symbols,rows):
    fields={'schema_version','policy','original_commitments','original_symbols','provenance','evidence',
            'catalogue_response','catalogue','items','commitments','symbols','before','after','sha256'}
    version=receipt.get('schema_version') if isinstance(receipt,dict) else None
    if version in MANDATORY:fields|={'catalogue_history','coverage_history'}
    require(isinstance(receipt,dict) and set(receipt)==fields and version in VERSIONS,
            'invalid shared predicate receipt')
    require(receipt['sha256']==digest(canonical({k:v for k,v in receipt.items() if k!='sha256'})),
            'shared predicate receipt hash mismatch')
    p=receipt['policy'];config=dict(construction_shared_predicates=True,shared_predicates_version=version,
        shared_predicates_max_unresolved=p['max_unresolved'],shared_predicates_failure_streak=p['failure_streak'])
    require(p==policy(config),'shared predicate policy mismatch')
    original=CommitmentSet.from_dict(receipt['original_commitments']);entries=catalogue(receipt['catalogue_response'],version=version)
    if version in MANDATORY:
        if version==V3:
            from ara.runtime.predicate_catalogue_policy import replay
            replay(receipt['catalogue_history'],receipt['coverage_history'],[rows[c.id] for c in original.commitments])
        else:
            from ara.runtime.predicate_coverage import replay
            replay(receipt['catalogue_history'],receipt['coverage_history'],len(original.commitments))
        require(receipt['catalogue_history'][-1]==receipt['catalogue_response'],'coverage final catalogue mismatch')
    require(entries==receipt['catalogue'] and rows==receipt['provenance'],'shared predicate catalogue/provenance mismatch')
    require(set(receipt['evidence'])=={c.id for c in original.commitments},'shared predicate evidence mismatch')
    from ara.runtime.commitment_provenance import make_commitment_provenance
    make_commitment_provenance(original,make_catalogue(original,receipt['original_symbols']),rows)
    require(len(receipt['items'])==len(original.commitments),'shared predicate item count mismatch')
    current=original;unresolved=streak=0
    for c,item in zip(original.commitments,receipt['items'],strict=True):
        current=admit_item(c,current,rows,entries,item,version=version)
        if item['status']=='unresolved':unresolved+=1;streak+=1
        else:streak=0
        require(unresolved<=p['max_unresolved'] and streak<p['failure_streak'],'shared predicate failure threshold exceeded')
    expected=symbols_for(current,receipt['original_symbols'],entries)
    require(current==final and final.to_dict()==receipt['commitments'] and expected==receipt['symbols'] and
            make_catalogue(final,symbols)==make_catalogue(final,expected),'shared predicate output mismatch')
    require(receipt['before']==vocabulary_metrics(original,receipt['original_symbols'],rows) and
            receipt['after']==metrics(final,expected,rows,entries,receipt['items'],version=version),'shared predicate metrics mismatch')
    return original,receipt['original_symbols']


def formalize(calls,original,original_symbols,rows,literature):
    p=policy(calls.config);require(p is not None,'shared predicates not enabled')
    version=p['version']
    require(len(original.commitments)<=64 and all(r.get('source_id') for r in rows.values()),
            'shared predicates require a bounded source-only selection')
    from ara.runtime.vocabulary_consolidation import evidence_items
    evidence=evidence_items(literature,rows)
    identity=digest(canonical(dict(original=original.to_dict(),symbols=original_symbols,rows=rows,evidence=evidence,policy=p)))
    cat_input=dict(lifecycle_key=identity,sources=[dict(text=c.text,source_id=rows[c.id]['source_id'],
                   stance=rows[c.id]['stance'],evidence=evidence[c.id]) for c in original.commitments],policy=p)
    history=checks=None
    if version in MANDATORY:
        if version==V3:
            from ara.runtime.predicate_catalogue_policy import prepare
        else:
            from ara.runtime.predicate_coverage import prepare
        entries,cat_response,history,checks=prepare(calls,cat_input)
    else:
        entries,cat_response=calls.call('predicate_catalogue',cat_input,lambda d:(catalogue(d),deepcopy(d)))
    calls.log.record('shared_predicate_catalogue',lifecycle_key=identity,entries=entries,response=cat_response,
                     note='Proposed cross-source meanings and deduplication are model judgments, not established equivalences.')
    current=original;items=[];unresolved=streak=0
    require(_consistent(CommitmentSet(tuple(c for c in original.commitments if rows[c.id]['stance']=='endorsed'))),
            'selected original endorsed theory is inconsistent or unknown')
    for c in original.commitments:
        inputs=dict(lifecycle_key=identity,source=c.text,evidence=evidence[c.id],stance=rows[c.id]['stance'],
                    catalogue=entries,item_key=digest(c.id))
        if version in MANDATORY:inputs['policy_version']=version
        item=dict(id=c.id,status='unresolved',candidate=None,translation=None,judgments=[],reason='')
        try:
            _,d=calls.call('predicate_formalize',inputs,lambda d:(candidate(d,entries,version=version),deepcopy(d)))
            item['candidate']=d
            if d['mode']=='retain':item['reason']='model_retained_original: '+d['reason']
            else:
                # No source sentence/evidence is supplied to the blind back-translator.
                back=dict(lifecycle_key=identity,item_key=digest(c.id),formula=d['formula'],catalogue=entries)
                item['translation']=calls.call('predicate_backtranslate',back)
                judge=dict(**inputs,formula=d['formula'],back_translation=item['translation']['text'])
                item['judgments']=[calls.call('predicate_fidelity',{**judge,'sample_index':i}) for i in range(3)]
                from ara.runtime.predicate_receipts import fidelity_adverse_history
                if not fidelity(item['judgments']):item['reason']='adverse_fidelity'
                elif fidelity_adverse_history(calls.log.read(),judge):item['reason']='adverse_fidelity_history'
                else:
                    item.update(status='admitted',reason='unanimous_fidelity')
                    try:current=admit_item(c,current,rows,entries,item,version=version)
                    except ValueError as exc:item.update(status='unresolved',reason=str(exc))
        except InvalidOutput as exc:
            if version in MANDATORY:raise  # No unmeasured atom fallback under mandatory proposals.
            # Invalid model output is item-local; budget/provider failures remain fatal.
            item.update(status='unresolved',reason='validation_exhausted: '+str(exc))
            if len(item['judgments']) not in (0,3):item['judgments']=[]
        items.append(item)
        stage='shared_predicate_admitted' if item['status']=='admitted' else 'consolidation_unresolved'
        calls.log.record(stage,lifecycle_key=identity,**item,
                         note='Unresolved means the exact original formula is retained; it is not a successful decomposition.')
        if item['status']=='unresolved':unresolved+=1;streak+=1
        else:streak=0
        if version==V3 and (unresolved>p['max_unresolved'] or streak>=p['failure_streak']):
            calls.log.record('shared_predicate_diagnostic_pause',unresolved=unresolved,processed=len(items),
                             selected=len(original.commitments),unattempted=len(original.commitments)-len(items),
                             admitted=len(items)-unresolved,policy=p,note='Stop and diagnose before any freeze or further formalization.')
        require(unresolved<=p['max_unresolved'] and streak<p['failure_streak'],'shared predicate failure threshold exceeded')
    symbols=symbols_for(current,original_symbols,entries)
    payload=dict(schema_version=version,policy=p,original_commitments=original.to_dict(),original_symbols=original_symbols,
        provenance=rows,evidence=evidence,catalogue_response=cat_response,catalogue=entries,items=items,
        commitments=current.to_dict(),symbols=symbols,before=vocabulary_metrics(original,original_symbols,rows),
        after=metrics(current,symbols,rows,entries,items,version=version))
    if version in MANDATORY:payload.update(catalogue_history=history,coverage_history=checks)
    receipt={**payload,'sha256':digest(canonical(payload))}
    validate_receipt(receipt,current,symbols,rows)
    save_immutable(calls.log.path.parent/'shared-predicates.json',canonical(receipt))
    calls.log.record('shared_predicates_finished',**receipt)
    return current,symbols,rows,receipt
