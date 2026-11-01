"""Bounded native bank instances over actual endorsed source formula supports."""
from collections import defaultdict
from ara.engine.forward import _instances, _Budget, _WorkLimit, _CanonicalFormaliser, _PACKAGING_RULES
from ara.engine.licensing import Licenser
from ara.types import PremiseFill, Proposal, Proposition


def bank_instances(t,rows,bank,sink,*,work_per_rule=500):
    if type(work_per_rule) is not int or work_per_rule<1:raise ValueError('invalid bank metric work limit')
    source_uses=defaultdict(set);known={}
    for c in t.commitments:
        r=rows[c.id]
        if r.get('source_id') is not None and r.get('stance')=='endorsed':
            key=c.formula.canonical();known[key]=c.formula;source_uses[key].add(r['source_id'])
    checker=Licenser(bank,_CanonicalFormaliser(),sink,timeout_ms=1000)
    coverage=[];instances=[];seen=set()
    for entry in bank.entries:
        schema=entry.formula_schema
        if entry.id in _PACKAGING_RULES:mode='excluded_packaging'
        elif schema is None or schema.scopes:mode='requires_witness'
        elif len(schema.premises)<2:mode='not_cross_source_single_step'
        else:mode='enumerated'
        row=dict(bank_id=entry.id,mode=mode,work_limit=work_per_rule,work_used=0,truncated=False,licensed=0)
        if mode=='enumerated':
            budget=_Budget(work_per_rule)
            try:
                for fills,conclusion in _instances(schema,tuple(known.values()),budget):
                    sources=set().union(*(source_uses[f.canonical()] for f in fills.values()))
                    if len(sources)<2:continue
                    key=(entry.id,tuple(sorted((k,v.canonical()) for k,v in fills.items())),conclusion.canonical())
                    if key in seen:continue
                    seen.add(key)
                    proposal=Proposal(entry.id,tuple(PremiseFill(s.id,fills[s.id].canonical()) for s in entry.premise_slots),conclusion.canonical())
                    licensed=checker.check(proposal,Proposition('metric',conclusion.canonical(),conclusion))
                    if licensed.licensed:
                        row['licensed']+=1
                        instances.append(dict(bank_id=entry.id,premises={k:v.to_dict() for k,v in fills.items()},
                                              conclusion=conclusion.to_dict(),source_papers=sorted(sources)))
            except _WorkLimit:row['truncated']=True
            row['work_used']=work_per_rule-budget.remaining
        coverage.append(row)
    return dict(cross_paper_applicable_bank_instances=len(instances),instances=instances,coverage=coverage,
                truncated=any(r['truncated'] for r in coverage),
                scope='One-step native bank matching and licensing on endorsed source formulas; no Boolean packaging, no generated premises, no search; truncated coverage is not absence.')
