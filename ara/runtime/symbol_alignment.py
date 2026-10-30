"""Bounded model judgments over cross-source vocabulary before the sole freeze."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from heapq import nsmallest
from itertools import combinations
import math
import re

from ara.runtime.cache import canonical, digest
from ara.runtime.frozen_catalogue import make_catalogue
from ara.types import Commitment, CommitmentSet, Formula, Term

LEGACY_POLICY_VERSION = 'cross-source-symbol-alignment-v1'
RETRIEVAL_POLICY_VERSION = 'cross-source-symbol-alignment-v2'
POLICY_VERSION = 'cross-source-symbol-alignment-v3'
CONSISTENCY_REFUSAL = 'alignment consistency not established (unsat or unknown)'
RELATIONS = {'same_content', 'entails_left_right', 'entails_right_left', 'contrary', 'unrelated'}
_STOP = frozenset('a an the and or not of to in on for from with by as at is are be that this it its'.split())


def retrieval_settings(config):
    minimum_score=config.get('construction_alignment_min_score',0.10)
    diversity=config.get('construction_alignment_paper_diversity',True)
    if type(minimum_score) not in (int,float) or not math.isfinite(minimum_score) or not 0 <= minimum_score <= 1:
        raise ValueError('construction_alignment_min_score must be a finite number from 0 to 1')
    if type(diversity) is not bool:
        raise ValueError('construction_alignment_paper_diversity must be boolean')
    from ara.runtime.shared_vocabulary import vocabulary_policy
    vocabulary_policy(config)
    top_k=config.get('construction_alignment_top_k',0)
    return dict(minimum_score=minimum_score,paper_diversity=diversity,
                **({'per_symbol_top_k':top_k} if top_k else {}))


def _rank(pair):
    return -pair['score'],pair['left'],pair['right']


def _scored_pairs(symbols, provenance, stats, *, include_zero=False):
    eligible = sorted((s for s in symbols if s['kind'] in ('atom','predicate')), key=lambda s:s['name'])
    terms = {s['name']: set(re.findall(r"\b[^\W\d_][\w'-]*\b",s['definition'].casefold())) - _STOP for s in eligible}
    frequencies = {}
    for values in terms.values():
        for term in values: frequencies[term] = frequencies.get(term,0) + 1
    weights = {term: 1 + math.log((1+len(eligible))/(1+frequency)) for term,frequency in frequencies.items()}
    papers = {s['name']: {provenance[id]['source_id'] for id in s['evidence_ids']} for s in eligible}
    stats.update(eligible_symbols=len(eligible),signature_compatible_pairs=0,lexical_overlap_pairs=0)
    for left,right in combinations(eligible,2):
        a,b = left['name'],right['name']
        if ((left['kind'],left['arity']) != (right['kind'],right['arity']) or
                not papers[a] or not papers[b] or None in papers[a] | papers[b] or papers[a] & papers[b]):
            continue
        stats['signature_compatible_pairs'] += 1
        common = terms[a] & terms[b]
        if not common and not include_zero: continue
        stats['lexical_overlap_pairs'] += int(bool(common))
        norm = math.sqrt(sum(weights[t]**2 for t in terms[a]) * sum(weights[t]**2 for t in terms[b]))
        score = sum(weights[t]**2 for t in common) / norm if norm else 0.0
        yield dict(left=a,right=b,score=round(score,8)),papers[a]|papers[b],score


def legacy_candidate_pairs(symbols, provenance, limit=150):
    """Replay the original hard cutoff exactly for persisted policy-v1 receipts."""
    if type(limit) is not int or limit < 0:
        raise ValueError('construction_alignment_candidates must be a nonnegative integer')
    return nsmallest(limit,(pair for pair,_,score in _scored_pairs(symbols,provenance,{}) if score>=0.15),key=_rank)


def candidate_inventory(symbols, provenance, limit=150, *, minimum_score=0.10, paper_diversity=True, per_symbol_top_k=0):
    """Bound model calls, backfill lexical leads, and retain source-paper coverage."""
    if type(limit) is not int or limit < 0:
        raise ValueError('construction_alignment_candidates must be a nonnegative integer')
    settings=retrieval_settings(dict(construction_alignment_min_score=minimum_score,
                                    construction_alignment_paper_diversity=paper_diversity,
                                    construction_alignment_top_k=per_symbol_top_k))
    if per_symbol_top_k:
        return _wide_inventory(symbols, provenance, limit, settings)
    stats=dict(**settings,above_threshold_pairs=0,diversity_additions=0)
    best_by_paper={}
    def scored():
        for pair,papers,score in _scored_pairs(symbols,provenance,stats):
            stats['above_threshold_pairs'] += int(score>=minimum_score)
            for paper in papers:
                current=best_by_paper.get(paper)
                if current is None or _rank(pair)<_rank(current):
                    best_by_paper[paper]=pair
            yield pair
    selected=nsmallest(max(1,limit),scored(),key=_rank)[:limit]
    symbol_papers={s['name']:{provenance[id]['source_id'] for id in s['evidence_ids']} for s in symbols}
    def coverage(pairs):
        return {paper for pair in pairs for name in (pair['left'],pair['right']) for paper in symbol_papers[name]}
    if paper_diversity:
        for paper in sorted(best_by_paper):
            covered=coverage(selected)
            if paper in covered: continue
            candidate=best_by_paper[paper]
            for index in range(len(selected)-1,-1,-1):
                replacement=selected[:index]+selected[index+1:]+[candidate]
                if covered <= coverage(replacement):
                    selected=sorted(replacement,key=_rank)
                    stats['diversity_additions'] += 1
                    break
    stats.update(backfilled_pairs=sum(p['score']<minimum_score for p in selected),
                 eligible_papers=sorted(best_by_paper),covered_papers=sorted(coverage(selected)),
                 selected_pairs=len(selected),limit=limit,
                 ranking='weighted_cosine_then_names; backfill_shared_terms; preserve_and_extend_paper_coverage')
    return dict(candidates=selected,**stats)


def _wide_inventory(symbols, provenance, limit, settings):
    """Per-symbol retrieval from all compatible pairs, including zero word overlap.

    Weighted lexical similarity ranks candidates; only the model judges semantics.
    Round-robin rank allocation prevents one dense cluster consuming the whole cap.
    Retained memory is bounded by symbols times min(top_k, global call limit).
    """
    top_k = settings['per_symbol_top_k']
    stats = dict(**settings, above_threshold_pairs=0)
    neighbours = {}
    width = min(top_k, limit)
    for pair, papers, score in _scored_pairs(symbols, provenance, stats, include_zero=True):
        stats['above_threshold_pairs'] += int(score >= settings['minimum_score'])
        for name in (pair['left'], pair['right']):
            neighbours[name] = nsmallest(width, neighbours.get(name, []) + [pair], key=_rank)
    ranked = {}
    for name in sorted(neighbours):
        for rank, pair in enumerate(neighbours[name]):
            key = (pair['left'], pair['right'])
            previous = ranked.get(key)
            if previous is None or rank < previous[0]:
                ranked[key] = (rank, pair)
    pool = sorted(ranked.values(), key=lambda item: (item[0], *_rank(item[1])))
    selected = sorted([pair for _, pair in pool[:limit]], key=_rank)
    symbol_papers = {s['name']: {provenance[id]['source_id'] for id in s['evidence_ids']} for s in symbols}
    covered = sorted({name for p in selected for name in (p['left'], p['right'])})
    stats.update(selected_pairs=len(selected), limit=limit,
        top_k_pool_pairs=len(pool), truncated=len(pool)>limit or (width<top_k and stats['signature_compatible_pairs']>limit),
        zero_overlap_pairs=sum(p['score']==0 for p in selected),
        backfilled_pairs=sum(p['score']<settings['minimum_score'] for p in selected),
        eligible_symbols_with_pairs=len(neighbours), covered_symbols=covered,
        covered_papers=sorted({paper for name in covered for paper in symbol_papers[name]}),
        ranking='per_symbol_top_k; rank_rounds_then_weighted_cosine_then_names; zero_overlap_eligible')
    return dict(candidates=selected, **stats)


def candidate_pairs(symbols, provenance, limit=150, **settings):
    return candidate_inventory(symbols,provenance,limit,**settings)['candidates']


def _validate_judgments(symbols, rows, judgments):
    names = {s['name']:s for s in symbols}
    seen = set()
    for row in judgments:
        if (not isinstance(row,dict) or set(row)!={'left','right','relation','reason'} or
                not all(isinstance(v,str) and v.strip() for v in row.values()) or
                row['relation'] not in RELATIONS or row['left'] not in names or row['right'] not in names):
            raise ValueError('invalid alignment judgment')
        left,right = names[row['left']],names[row['right']]
        pair = tuple(sorted((row['left'],row['right'])))
        if pair in seen or pair[0]==pair[1]: raise ValueError('duplicate alignment pair')
        seen.add(pair)
        if (left['kind'] not in ('atom','predicate') or
                (left['kind'],left['arity']) != (right['kind'],right['arity'])):
            raise ValueError('alignment signature mismatch')
        sources = [{rows[id]['source_id'] for id in s['evidence_ids']} for s in (left,right)]
        if not all(sources) or sources[0] & sources[1] or None in sources[0] | sources[1]:
            raise ValueError('alignment requires distinct source definitions')


def _consistent(commitments):
    from ara.formal import entails
    # Entailing a contradiction is exactly inconsistency; UNKNOWN also refuses.
    p=Formula('atom',name='alignment_consistency_probe')
    contradiction=Formula('and',(p,p.negated()))
    return entails(tuple(c.formula for c in commitments.commitments),contradiction,5000)=='SOLVER_COUNTEREXAMPLE'


def _rewrite(formula,mapping):
    return replace(formula, name=mapping[formula.name] if formula.op in ('atom','predicate') else formula.name,
                   args=tuple(_rewrite(a,mapping) for a in formula.args))


def apply_judgments(commitments, symbols, provenance, judgments):
    """Apply the complete set transactionally; no inferred or partial alignments."""
    make_catalogue(commitments,symbols)
    _validate_judgments(symbols,provenance,judgments)
    mapping={s['name']:s['name'] for s in symbols}
    def root(name):
        while mapping[name]!=name: name=mapping[name]
        return name
    for j in judgments:
        if j['relation']=='same_content':
            a,b=sorted((root(j['left']),root(j['right'])))
            mapping[b]=a
    mapping={name:root(name) for name in mapping}
    rewritten=[replace(c,formula=_rewrite(c.formula,mapping)) for c in commitments.commitments]
    names={s['name']:s for s in symbols}
    catalogue=[]
    for name in sorted(set(mapping.values())):
        evidence=sorted({id for old,s in names.items() if mapping[old]==name for id in s['evidence_ids']})
        catalogue.append({**names[name],'evidence_ids':evidence})
    rows=deepcopy(provenance)
    formulas={c.formula.canonical() for c in rewritten}
    for j in judgments:
        if j['relation'] in ('same_content','unrelated'): continue
        left,right=names[j['left']],names[j['right']]
        variables=[Term('variable',f'x{i}') for i in range(left['arity'])]
        a,b=[Formula(s['kind'],name=mapping[s['name']],terms=tuple(variables)) for s in (left,right)]
        formula=(Formula('not',(Formula('and',(a,b)),)) if j['relation']=='contrary' else
                 Formula('implies',(a,b) if j['relation']=='entails_left_right' else (b,a)))
        for variable in reversed(variables): formula=Formula('forall',(formula,),variable=variable.name)
        if formula.canonical() in formulas: raise ValueError('duplicate alignment formula')
        formulas.add(formula.canonical())
        id='alignment:'+digest(canonical(j))
        if id in rows: raise ValueError('duplicate alignment id')
        evidence=sorted(set(left['evidence_ids']+right['evidence_ids']))
        citation='; '.join(f"{s['name']} [{s['definition']}]: " + ', '.join(commitments.get(e).citation for e in s['evidence_ids']) for s in (left,right))
        text=f"{j['relation']}: {left['definition']} ; {right['definition']}"
        rewritten.append(Commitment(id,text,citation,formula))
        rows[id]=dict(kind='alignment',stance='model_alignment',source_id=None,
                      source_ids=sorted({provenance[e]['source_id'] for e in evidence}),evidence_ids=evidence,
                      definitions=deepcopy([left,right]),judgment=dict(j))
    result=CommitmentSet(tuple(rewritten))
    if any(j['relation']!='unrelated' for j in judgments) and not _consistent(result):
        raise ValueError(CONSISTENCY_REFUSAL)
    make_catalogue(result,catalogue)
    return result,catalogue,rows,mapping


def unresolved_limit(config):
    limit=config.get('construction_alignment_max_unresolved',5)
    if type(limit) is not int or limit < 0:
        raise ValueError('construction_alignment_max_unresolved must be a nonnegative integer')
    return limit


def bind_judgment(value, candidate):
    """The response owns only the relation/reason; candidate identity is runtime data."""
    from ara.runtime.calls import require
    require(isinstance(value,dict) and set(value)=={'relation','reason'},
            'alignment response must contain only relation and reason')
    require(value['relation'] in RELATIONS and isinstance(value['reason'],str) and
            0 < len(value['reason'].strip()) <= 1000, 'invalid alignment verdict')
    return dict(left=candidate['left'],right=candidate['right'],**value)


def _validate_unresolved(rows):
    if not isinstance(rows,list): raise ValueError('invalid alignment unresolved inventory')
    for row in rows:
        if (not isinstance(row,dict) or set(row)!={'left','right','status','reason','attempts'} or
                row['status']!='alignment_unresolved' or
                not all(isinstance(row[k],str) and row[k].strip() for k in ('left','right','reason')) or
                type(row['attempts']) is not int or not 1 <= row['attempts'] <= 3):
            raise ValueError('invalid alignment unresolved outcome')


def align_symbols(calls, commitments, symbols, provenance):
    from ara.runtime.calls import InvalidOutput, require
    limit=calls.config.get('construction_alignment_candidates',150)
    max_unresolved=unresolved_limit(calls.config)
    catalogue=make_catalogue(commitments,symbols)
    from ara.runtime.commitment_provenance import make_commitment_provenance
    make_commitment_provenance(commitments,catalogue,provenance)
    inventory=candidate_inventory(symbols,provenance,limit,**retrieval_settings(calls.config))
    candidates=inventory['candidates']
    retrieval={k:v for k,v in inventory.items() if k!='candidates'}
    restored=getattr(calls,'alignment_resume',None)
    if restored is not None:
        require(candidates==restored['candidates'], 'alignment resume candidate inventory changed')
    calls.log.record('symbol_alignment_candidates',policy_version=POLICY_VERSION,limit=limit,
                     candidates=candidates,retrieval=retrieval,unresolved_limit=max_unresolved,
                     commitments_sha256=catalogue['commitments_sha256'],catalogue_sha256=catalogue['sha256'])
    if not candidates: return commitments,symbols,provenance,None
    names={s['name']:s for s in symbols}
    previous={(j['left'],j['right']):j for j in restored['judgments']} if restored else {}
    pending={(j['left'],j['right']):j for j in restored['unresolved']} if restored else {}
    judgments,unresolved=[],[]
    for candidate in candidates:
        left,right=names[candidate['left']],names[candidate['right']]
        pair=(candidate['left'],candidate['right'])
        if pair in previous:
            judgments.append(previous[pair])
        elif pair in pending:
            unresolved.append(pending[pair])
        else:
            def check(value):
                bound=bind_judgment(value,candidate)
                _validate_judgments(symbols,provenance,[bound])
                return bound
            try:
                value=calls.call('judge_symbol_alignment',dict(topic='',policy_version=POLICY_VERSION,
                    candidate=dict(left=left,right=right,score=candidate['score']),
                    sources={id:provenance[id] for id in sorted(set(left['evidence_ids']+right['evidence_ids']))},
                    commitments_sha256=catalogue['commitments_sha256'],catalogue_sha256=catalogue['sha256']),check)
            except InvalidOutput as exc:
                outcome=dict(left=pair[0],right=pair[1],status='alignment_unresolved',
                             reason=str(exc),attempts=calls.config.get('validation_attempts',1))
                unresolved.append(outcome)
                calls.log.record('alignment_unresolved',**outcome)
            else:
                judgments.append(value)
        if len(unresolved)>max_unresolved:
            calls.log.record('symbol_alignment_incomplete',status='unresolved_limit_exceeded',
                unresolved=unresolved,unresolved_count=len(unresolved),unresolved_limit=max_unresolved,
                accepted_count=len(judgments),candidate_count=len(candidates))
            require(False,'alignment unresolved limit exceeded; no freeze')
    receipt=dict(policy_version=POLICY_VERSION,candidate_limit=limit,candidates=candidates,judgments=judgments,retrieval=retrieval,
                 unresolved=unresolved,unresolved_limit=max_unresolved,
                 original_commitments=commitments.to_dict(),original_symbols=deepcopy(symbols),
                 status='accepted',refusal_reason=None,mapping={s['name']:s['name'] for s in symbols})
    try:
        result,catalogue,rows,mapping=apply_judgments(commitments,symbols,provenance,judgments)
    except ValueError as exc:
        receipt.update(status='refused',refusal_reason=str(exc))
        calls.log.record('symbol_alignment_refused',**receipt)
        return commitments,symbols,provenance,receipt
    receipt['mapping']=mapping
    if calls.config.get('construction_shared_vocabulary') or calls.config.get('construction_alignment_top_k',0):
        from ara.runtime.shared_vocabulary import vocabulary_metrics
        calls.log.record('alignment_vocabulary_metrics',
            before=vocabulary_metrics(commitments,symbols,provenance),
            after=vocabulary_metrics(result,catalogue,rows))
    calls.log.record('symbol_alignment_applied',**receipt)
    return result,catalogue,rows,receipt


def validate_alignment(receipt, commitments, symbols, rows):
    """Replay persisted judgments against original T; no model calls on load."""
    fields={'policy_version','candidate_limit','candidates','judgments','original_commitments','original_symbols',
            'status','refusal_reason','mapping'}
    if not isinstance(receipt,dict):
        raise ValueError('invalid alignment receipt')
    version=receipt.get('policy_version')
    if version in (RETRIEVAL_POLICY_VERSION,POLICY_VERSION):
        fields=fields|{'retrieval'}
    if version==POLICY_VERSION:
        fields=fields|{'unresolved','unresolved_limit'}
    if set(receipt)!=fields or version not in (LEGACY_POLICY_VERSION,RETRIEVAL_POLICY_VERSION,POLICY_VERSION):
        raise ValueError('invalid alignment receipt')
    original=CommitmentSet.from_dict(receipt['original_commitments'])
    source_rows={c.id:rows[c.id] for c in original.commitments}
    original_symbols=receipt['original_symbols']
    if version==LEGACY_POLICY_VERSION:
        candidates=legacy_candidate_pairs(original_symbols,source_rows,receipt['candidate_limit'])
    else:
        retrieval=receipt['retrieval']
        if not isinstance(retrieval,dict) or not {'minimum_score','paper_diversity'} <= retrieval.keys():
            raise ValueError('invalid alignment retrieval policy')
        inventory=candidate_inventory(original_symbols,source_rows,receipt['candidate_limit'],
            minimum_score=retrieval['minimum_score'],paper_diversity=retrieval['paper_diversity'],
            per_symbol_top_k=retrieval.get('per_symbol_top_k',0))
        candidates=inventory.pop('candidates')
        if retrieval!=inventory:
            raise ValueError('alignment retrieval replay mismatch')
    unresolved=receipt.get('unresolved',[])
    _validate_unresolved(unresolved)
    if version==POLICY_VERSION and len(unresolved)>unresolved_limit(
            {'construction_alignment_max_unresolved':receipt['unresolved_limit']}):
        raise ValueError('alignment unresolved limit exceeded')
    if not candidates or receipt['candidates']!=candidates:
        raise ValueError('alignment candidate inventory mismatch')
    pairs=[(c['left'],c['right']) for c in candidates]
    accepted=[(j['left'],j['right']) for j in receipt['judgments']]
    missing=[(j['left'],j['right']) for j in unresolved]
    if (len(accepted)+len(missing)!=len(pairs) or set(accepted)&set(missing) or
            accepted!=[p for p in pairs if p not in missing] or missing!=[p for p in pairs if p not in accepted]):
        raise ValueError('alignment judgment inventory mismatch')
    _validate_judgments(original_symbols,source_rows,receipt['judgments'])
    if receipt['status']=='refused' and receipt['refusal_reason']==CONSISTENCY_REFUSAL:
        # A recorded refusal grants no alignment and must survive solver timing changes.
        expected,expected_symbols,expected_rows=original,original_symbols,source_rows
        mapping={s['name']:s['name'] for s in original_symbols}
    else:
        try:
            expected,expected_symbols,expected_rows,mapping=apply_judgments(original,original_symbols,source_rows,receipt['judgments'])
        except ValueError as exc:
            if receipt['status']!='refused' or receipt['refusal_reason']!=str(exc):
                raise ValueError('alignment refusal replay mismatch') from exc
            expected,expected_symbols,expected_rows=original,original_symbols,source_rows
            mapping={s['name']:s['name'] for s in original_symbols}
        else:
            if receipt['status']!='accepted' or receipt['refusal_reason'] is not None:
                raise ValueError('alignment acceptance replay mismatch')
    if (expected!=commitments or make_catalogue(expected,expected_symbols)!=make_catalogue(commitments,symbols) or
            expected_rows!=rows or receipt['mapping']!=mapping):
        raise ValueError('alignment replay mismatch')
    return original,original_symbols


def alignment_disclosure(provenance):
    receipt=provenance.get('alignment') if provenance else None
    if receipt is None:
        return dict(status='unavailable', judgments=[], mapping={})
    return dict(status=receipt['status'],refusal_reason=receipt['refusal_reason'],
                judgments=receipt['judgments'],unresolved=receipt.get('unresolved',[]),
                unresolved_count=len(receipt.get('unresolved',[])),
                mapping={a:b for a,b in receipt['mapping'].items() if a!=b},
                note='Model alignment judgments are not source endorsements. Bridges belong to no single paper; at least two endorsed source supports remain required.')
