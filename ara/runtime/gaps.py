"""Deterministic frozen-content gaps; witnesses, not an exhaustive semantic census."""
from itertools import combinations
import re
from ara.runtime.cache import canonical, digest
from ara.runtime.search_alignment import symbols
from ara.runtime.contribution import cached_entails
from ara.types import Gap, Formula

_OPEN = re.compile(r'\b(unresolved|unsolved|is open|problem remains|jury is out|open (?:problem|question|issue)|remains? (?:unknown|unclear|open)|not yet (?:known|resolved|solved))\b', re.I)


def detect_gaps(commitments, catalogue, provenance):
    if provenance is None or catalogue is None:
        return dict(gaps=(), status='unavailable_legacy', checks=(), set_search='unavailable')
    rows = provenance['commitments']
    inventory = sorted(commitments.commitments,key=lambda c:c.id)
    endorsed = [c for c in inventory if rows[c.id]['stance']=='endorsed']
    signatures = {c.id:set(symbols(c.formula)) for c in inventory}
    gaps, checks = {}, []
    def add(kind, members):
        ids = tuple(sorted(c.id for c in members))
        papers = tuple(sorted({rows[tid]['source_id'] for tid in ids}))
        if kind != 'open_problem' and len(papers)<2:
            return
        if kind=='stance_conflict':
            groups=tuple(tuple(c.id for c in endorsed if rows[c.id]['source_id']==paper
                and (c.id in ids or any(rows[tid]['stance']=='attacked' and rows[tid]['source_id']==paper for tid in ids)))
                for paper in papers)
        else:
            groups=tuple(tuple(tid for tid in ids if rows[tid]['source_id']==paper) for paper in papers)
        payload=dict(kind=kind,commitment_ids=ids,paper_ids=papers,support_groups=groups)
        gap=Gap('gap:'+digest(canonical(payload)),**payload)
        gaps[gap.id]=gap
    def unsat(members):
        if not members: return False
        atom=members[0].formula
        false=Formula('and',(atom,atom.negated()))
        verdict=cached_entails(tuple(c.formula for c in members),false,1000)
        checks.append(dict(commitment_ids=[c.id for c in members],solver_result=verdict))
        return verdict=='SOLVER_UNSAT'
    for a,b in combinations(endorsed,2):
        if rows[a.id]['source_id']!=rows[b.id]['source_id'] and signatures[a.id]&signatures[b.id] and unsat((a,b)):
            add('contradiction',(a,b))
    # One deletion-minimal joint witness per shared-symbol component catches
    # multi-premise inconsistency even when no pair contradicts. No exhaustive MUS claim.
    pending=list(endorsed)
    while pending:
        component=[pending.pop(0)]
        used=set(signatures[component[0].id])
        while True:
            linked=[c for c in pending if used&signatures[c.id]]
            if not linked: break
            component.extend(linked)
            used.update(s for c in linked for s in signatures[c.id])
            pending=[c for c in pending if c not in linked]
        if len(component)>2 and unsat(component):
            core=component[:]
            for c in component:
                remainder=[v for v in core if v.id!=c.id]
                if unsat(remainder): core=remainder
            add('contradiction',core)
    for a in endorsed:
        for b in inventory:
            if rows[b.id]['stance']=='attacked' and rows[a.id]['source_id']!=rows[b.id]['source_id']:
                if a.formula.canonical()==b.formula.canonical() or a.text==b.text:
                    add('stance_conflict',(a,b))
        definitions=[s['definition'] for s in catalogue
                     if (s['name'],s['kind'],s['arity']) in signatures[a.id]]
        if any(_OPEN.search(text) for text in (a.text,*definitions)):
            add('open_problem',(a,))
    return dict(gaps=tuple(sorted(gaps.values(),key=lambda g:(g.kind,g.commitment_ids))),
                status='verified_frozen_candidates',checks=tuple(checks),
                set_search='all_shared_symbol_cross_paper_pairs_plus_one_minimal_witness_per_component')


def resolution_support(gap, support_ids, provenance):
    rows=provenance['commitments'] if provenance else {}
    eligible={tid for tid in support_ids if rows.get(tid,{}).get('stance')=='endorsed'}
    witnesses=[sorted(eligible & set(group)) for group in gap.support_groups]
    return dict(gap=gap.to_dict(), supported=bool(witnesses) and all(witnesses),
                group_witnesses=witnesses, reason='endorsed_support_required_from_each_gap_side')
