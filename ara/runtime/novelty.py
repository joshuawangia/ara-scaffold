"""Per-paper novelty with bounded solver receipts; conservative legacy fallback."""
from dataclasses import replace
from ara.runtime.cache import canonical
from ara.runtime.contribution import cached_entails
from ara.runtime.novelty_basis import consistent_basis, boolean_package
from ara.types import Formula, CommitmentSet


def application_key(formula, bound=()):
    # Local bound-variable identity ignores unused surrounding binders while
    # preserving repeated-versus-distinct variables and free/constant identity.
    variables = {}
    terms = []
    for term in formula.terms:
        if term.kind == 'variable' and term.name in bound:
            identity = ('bound', variables.setdefault(term.name, len(variables)))
        else:
            identity = ('free', term.name)
        terms.append((term.kind, identity))
    return canonical([formula.op, formula.name, terms])


def atomic_applications(formula, bound=()):
    if formula.op in ('atom', 'predicate'):
        yield application_key(formula, bound), formula
    nested = bound + (formula.variable,) if formula.op in ('forall', 'exists') else bound
    for child in formula.args:
        yield from atomic_applications(child, nested)


def cofactor(formula, key, truth, bound=()):
    if formula.op in ('atom', 'predicate') and application_key(formula, bound) == key:
        # The shared AST has no truth constants. These are exactly top/bottom.
        return Formula('or' if truth else 'and', (formula, formula.negated()))
    nested = bound + (formula.variable,) if formula.op in ('forall', 'exists') else bound
    return replace(formula, args=tuple(cofactor(a, key, truth, nested) for a in formula.args))


def novelty_check(formula, commitments, provenance=None, *, support_ids=None, basis_ids=()):
    if provenance is not None:
        return per_paper_novelty(formula, commitments, provenance, support_ids=support_ids, basis_ids=basis_ids)
    premises = tuple(c.formula for c in commitments.commitments)
    checks = []
    base = dict(basis_commitment_ids=[c.id for c in commitments.commitments], checks=checks)
    result = cached_entails(premises, formula, 1000)
    checks.append(dict(scope='deductive_closure', solver_result=result, timeout_ms=1000))
    if result == 'SOLVER_UNSAT':
        return dict(**base, status='rejected', reason='deductive_closure', solver_result=result,
                    explanation='All of frozen T classically entails this target. Connective or quantifier wrappers do not create a new assertion.')
    if result != 'SOLVER_COUNTEREXAMPLE':
        return dict(**base, status='unresolved', reason='novelty_unresolved',
                    explanation='Bounded deductive-closure checking did not establish novelty.')
    existing = {key for c in commitments.commitments for key, _ in atomic_applications(c.formula)}
    candidates = {key:atom for key, atom in atomic_applications(formula) if key not in existing}
    essential = []
    for key, atom in candidates.items():
        changed = False
        for truth in (True, False):
            result = cached_entails(premises, Formula('iff', (formula, cofactor(formula, key, truth))), 1000)
            checks.append(dict(scope='essential_atom', application_key=key, substituted_truth=truth,
                               solver_result=result, timeout_ms=1000))
            if result not in ('SOLVER_UNSAT', 'SOLVER_COUNTEREXAMPLE'):
                return dict(**base, status='unresolved', reason='novelty_unresolved',
                            explanation='Bounded essential-atom checking was unresolved; novelty cannot be admitted.')
            changed |= result == 'SOLVER_COUNTEREXAMPLE'
        if changed:
            essential.append((key, atom))
    if not essential:
        return dict(**base, status='rejected', reason='no_essential_new_proposition',
                    explanation='No new atomic application changes the target truth under T when replaced by true or false; vacuous or renamed bound variables do not count.')
    return dict(**base, status='candidate', reason='essential_new_assertion',
                essential_application_keys=[key for key, _ in essential],
                essential_new_propositions=[atom.to_dict() for _, atom in essential])


def endorsed_papers(commitments, provenance):
    """Verified source ownership only; model alignments never invent a paper."""
    groups = {}
    rows = provenance['commitments']
    for c in commitments.commitments:
        row = rows.get(c.id, {})
        if row.get('stance') == 'endorsed' and row.get('source_id'):
            groups.setdefault(row['source_id'], []).append(c)
    return {paper: tuple(sorted(group, key=lambda c:c.id)) for paper, group in sorted(groups.items())}


def per_paper_novelty(formula, commitments, provenance, *, support_ids=None, basis_ids=()):
    groups = endorsed_papers(commitments, provenance)
    selection = consistent_basis(commitments, provenance,
        basis_ids if support_ids is None else support_ids, exact=support_ids is not None)
    union = tuple(commitments.get(tid) for tid in selection['selected_commitment_ids'])
    union_premises = tuple(c.formula for c in union)
    from ara.runtime.hypotheses import hypothesis_ids
    conditional = [c for c in union if c.id in hypothesis_ids(provenance)]
    checks = []
    base = dict(basis='per_paper_endorsed_closure',
        basis_commitment_ids=[c.id for group in groups.values() for c in group],
        union_basis_commitment_ids=[c.id for c in union], consistent_basis=selection, checks=checks)
    if conditional:
        base['conditional_on'] = [c.id for c in conditional]
    def check(premises, goal, scope, paper=None, **details):
        result = cached_entails(premises, goal, 1000)
        checks.append(dict(scope=scope, paper_id=paper, solver_result=result, timeout_ms=1000, **details))
        return result
    def result(status, reason, explanation, **details):
        return dict(**base, status=status, reason=reason, explanation=explanation, **details)
    if selection['status'] != 'consistent':
        return result('rejected' if selection['status'] == 'conflict' else 'unresolved', selection['reason'],
            'The asserted basis must be satisfiable. Conflicting premises are resolution obligations, not a license for arbitrary targets.')
    tautology = check((), formula, 'tautology')
    if tautology == 'SOLVER_UNSAT':
        return result('rejected','valid_without_support','The target is true without source support.')
    if tautology != 'SOLVER_COUNTEREXAMPLE' or not groups:
        return result('unresolved','novelty_unresolved','No verified per-paper novelty verdict is available.')
    # A paper with internal contradictions must not entail everything by explosion.
    # Preserve any required supports it owns, and disclose its consistent projection.
    premises = {}
    base['paper_bases'] = {}
    required = set(selection['required_commitment_ids'])
    for paper, members in groups.items():
        paper_basis = consistent_basis(CommitmentSet(members), None, required & {c.id for c in members})
        base['paper_bases'][paper] = paper_basis
        if paper_basis['status'] != 'consistent':
            return result('unresolved','novelty_unresolved','A bounded per-paper consistency check was unresolved.')
        premises[paper] = tuple(commitments.get(tid).formula for tid in paper_basis['selected_commitment_ids'])
    for paper, basis in premises.items():
        verdict = check(basis + tuple(c.formula for c in conditional), formula, 'per_paper_closure', paper)
        if verdict == 'SOLVER_UNSAT':
            return result('rejected','hypothesis_padding' if conditional else 'single_paper_closure',
                'One paper already entails the target; wrappers or unused antecedents do not add a synthesis.',
                paper_id=paper, entailing_commitment_ids=[c.id for c in groups[paper]])
        if verdict != 'SOLVER_COUNTEREXAMPLE':
            return result('unresolved','novelty_unresolved','A bounded per-paper closure check was unresolved.')
    package_check = boolean_package(formula, union)
    base['boolean_package'] = package_check
    if package_check['solver_result'] == 'SOLVER_UNSAT':
        return result('rejected','no_essential_new_proposition',
            'The target is equivalent to a Boolean combination of basis formulas, without assuming those formulas true.')
    if package_check['solver_result'] != 'SOLVER_COUNTEREXAMPLE':
        return result('unresolved','novelty_unresolved','Bounded Boolean-package equivalence was unresolved.')
    essential = []
    for key, atom in sorted(dict(atomic_applications(formula)).items()):
        # An atom may occur in a conditional in T without being a consequence
        # of any individual paper. Mere conjunctions of separately known facts
        # have no new essential assertion.
        known = False
        for paper, basis in premises.items():
            for goal in (atom, atom.negated()):
                verdict = check(basis, goal, 'per_paper_atom_closure', paper, application_key=key)
                if verdict == 'SOLVER_UNSAT':
                    known = True
                    break
                if verdict != 'SOLVER_COUNTEREXAMPLE':
                    return result('unresolved','novelty_unresolved','An atomic closure check was unresolved.')
            if known:
                break
        if known:
            continue
        changed = False
        # Use only the consistent selected basis; unrelated contradictions in T
        # must neither suppress a contribution nor license one by explosion.
        for truth in (True, False):
            verdict = check(union_premises, Formula('iff',(formula,cofactor(formula,key,truth))),
                'essential_atom_union',application_key=key,substituted_truth=truth)
            if verdict not in ('SOLVER_UNSAT','SOLVER_COUNTEREXAMPLE'):
                return result('unresolved','novelty_unresolved','A union essential-atom check was unresolved.')
            changed |= verdict == 'SOLVER_COUNTEREXAMPLE'
        if changed:
            essential.append((key,atom))
    if not essential:
        return result('rejected','no_essential_new_proposition',
            'No atomic assertion outside every individual paper closure changes target truth under the selected consistent support basis.')
    return result('candidate','per_paper_new_assertion',
        'No individual endorsed paper entails this target, and an assertion remains essential under the selected consistent support basis. Union entailment is allowed.',
        essential_application_keys=[key for key,_ in essential],
        essential_new_propositions=[atom.to_dict() for _,atom in essential])
