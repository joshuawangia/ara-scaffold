"""Bind short, call-local references; never repair model formulas or definitions."""
from copy import deepcopy
from dataclasses import replace

from ara.runtime.cache import canonical, digest
from ara.runtime.calls import Rejected
from ara.runtime.construction import formula_symbols
from ara.types import Formula

VERSION = 'vocabulary-consolidation-v3'
BINDING_V2 = 'vocabulary-consolidation-v2'
BOUND_VERSIONS = (BINDING_V2, VERSION)
LEGACY = 'vocabulary-consolidation-v1'


class BindingMismatch(Rejected):
    def __init__(self, message, **constraints):
        self.reference_constraints = constraints
        super().__init__(message + ': ' + canonical(constraints))


def rewrite_handles(formula, mapping):
    """Rename declared symbols, including constants; bound variables stay local."""
    return replace(formula,
        name=mapping[formula.name] if formula.op in ('atom','predicate') else formula.name,
        terms=tuple(replace(t, name=mapping[t.name]) if t.kind=='constant' else t for t in formula.terms),
        args=tuple(rewrite_handles(a,mapping) for a in formula.args))


def catalogue_handles(symbols):
    return [dict(handle=f's{i}', kind=s['kind'], arity=s['arity'], definition=s['definition'])
            for i, s in enumerate(symbols)]


def bind_response(data, inputs, original, prior, symbols):
    """Resolve positional slots and declared handles, deriving all actual use IDs."""
    if inputs.get('binding_version') not in BOUND_VERSIONS:
        return data, symbols, None
    slots=inputs['accepted_commitments']['commitments']
    if len(data['formulas']) != len(slots):
        raise BindingMismatch('consolidation formula slot count mismatch',
                              expected_formula_count=len(slots), received_formula_count=len(data['formulas']))
    existing={f's{i}':s for i,s in enumerate(symbols)}
    fresh={f'n{i}':s for i,s in enumerate(data['new_symbols'])}
    declared={**existing, **fresh}
    formulas=[Formula.from_dict(value) for value in data['formulas']]
    used=set(); mismatches=[]
    for slot,formula in enumerate(formulas):
        for handle,kind,arity in formula_symbols(formula):
            used.add(handle)
            if handle in declared and (kind,arity)!=(declared[handle]['kind'],declared[handle]['arity']):
                mismatches.append(dict(slot=slot,handle=handle,expected_kind=declared[handle]['kind'],
                    expected_arity=declared[handle]['arity'],received_kind=kind,received_arity=arity))
    unknown=sorted(used-set(declared)); unused=sorted(set(fresh)-used)
    if unknown or unused or mismatches:
        raise BindingMismatch('consolidation formula handle mismatch',unknown_formula_handles=unknown,
            unused_new_handles=unused,signature_mismatches=mismatches,
            allowed_existing_handles=sorted(existing),allowed_new_handles=sorted(fresh))
    expected=sorted(used & set(existing)); supplied=[r['handle'] for r in data['reuse']]
    duplicates=sorted({h for h in supplied if supplied.count(h)>1})
    if sorted(supplied)!=expected or duplicates or any(not r['reason'].strip() for r in data['reuse']):
        raise BindingMismatch('consolidation reuse handle mismatch',expected_reuse_handles=expected,
            received_reuse_handles=supplied,missing_reuse_handles=sorted(set(expected)-set(supplied)),
            extra_reuse_handles=sorted(set(supplied)-set(expected)),duplicate_reuse_handles=duplicates,
            blank_reason_handles=[r['handle'] for r in data['reuse'] if not r['reason'].strip()])
    mapping={h:s['name'] for h,s in existing.items()}
    mapping.update({h:f"V{inputs['batch_index']}_{i}" for i,h in enumerate(fresh)})
    originals={c.id:c for c in original.commitments}
    commitments=[replace(originals[slot['id']],formula=rewrite_handles(formula,mapping))
                 for slot,formula in zip(slots,formulas)]
    all_uses={}
    for c in (*prior.commitments,*commitments):
        for name,_,_ in formula_symbols(c.formula):all_uses.setdefault(name,set()).add(c.id)
    bound_symbols=[{**deepcopy(s),'evidence_ids':sorted(all_uses[s['name']])} for s in symbols]
    new_symbols=[dict(name=mapping[h],**deepcopy(s),evidence_ids=sorted(all_uses[mapping[h]]))
                 for h,s in fresh.items()]
    result=dict(commitments=[dict(id=c.id,definition=c.text,formula=c.formula.to_dict()) for c in commitments],
                new_symbols=new_symbols,
                alignments=[dict(name=mapping[r['handle']],reason=r['reason']) for r in data['reuse']])
    bindings=dict(slots=[s['id'] for s in slots],
        catalogue={h:dict(name=s['name'],key=digest(canonical(s))) for h,s in existing.items()},
        introduced={h:mapping[h] for h in fresh},
        evidence_ids={name:sorted(ids) for name,ids in sorted(all_uses.items())},
        reuse=[dict(handle=r['handle'],name=mapping[r['handle']],
                    catalogue_key=digest(canonical(existing[r['handle']])),reason=r['reason']) for r in data['reuse']])
    return result,bound_symbols,bindings


def screen_new_definitions(symbols):
    """Precisely screen fresh declarations; report matches without rewriting text."""
    from ara.runtime.commitment_provenance import (
        PRECISE_SCREEN, content_definition, _definition_screen_text, _PRECISE_ATTRIBUTION)
    issues=[]
    for slot,symbol in enumerate(symbols):
        text=symbol['definition']
        if content_definition(text,screen=PRECISE_SCREEN):continue
        normalized=_definition_screen_text(text)
        views=[('raw',text)]
        if normalized is not None and normalized!=text:views.append(('screening_view',normalized))
        matches=[dict(view=view,match=m.group(),span=list(m.span()))
                 for view,value in views for m in _PRECISE_ATTRIBUTION.finditer(value)]
        reason=('attribution_frame' if matches else 'unsupported_markup' if normalized is None else 'no_textual_content')
        issues.append(dict(declaration_slot=slot,handle=f'n{slot}',name=symbol['name'],
            definition=text,screen=PRECISE_SCREEN,reason=reason,matched_frames=matches))
    if issues:
        raise BindingMismatch('consolidation symbol is not content',definition_issues=issues)
