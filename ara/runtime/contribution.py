"""Bounded solver receipts for contribution; never an inference license."""
from collections import OrderedDict
from threading import RLock

from ara.formal import entails
from ara.runtime.cache import canonical, digest

_CACHE = OrderedDict()
_LOCK = RLock()
_CACHE_LIMIT = 8192


def formula_hash(formula):
    """Alpha-invariant structural hash; bound and free variables cannot collide."""
    def encode(f, bound=()):
        terms = [(t.kind, ('bound', bound[::-1].index(t.name))
                  if t.kind == 'variable' and t.name in bound else ('free', t.name))
                 for t in f.terms]
        nested = bound + (f.variable,) if f.op in ('forall', 'exists') else bound
        args = [encode(a, nested) for a in f.args]
        if f.op in ('and', 'or'):
            args.sort(key=canonical)
        return [f.op, f.name, terms, args]
    return digest(canonical(encode(formula.normalized())))


def clear_entailment_cache():
    with _LOCK:
        _CACHE.clear()


def cached_entails(premises, conclusion, timeout_ms=1000):
    if not 0 < timeout_ms <= 1000:
        raise ValueError('contribution timeout must be in 1..1000 ms')
    key = (tuple(formula_hash(p) for p in premises), formula_hash(conclusion), timeout_ms)
    with _LOCK:
        if key in _CACHE:
            _CACHE.move_to_end(key)
            return _CACHE[key]
        result = entails(premises, conclusion, timeout_ms)
        _CACHE[key] = result
        if len(_CACHE) > _CACHE_LIMIT:
            _CACHE.popitem(last=False)
        return result


def contribution_check(formula, commitments, timeout_ms=1000, *, both_polarities=True):
    """At most 2*(1+|T|) bounded checks, stopping on a decisive exclusion."""
    checks = []
    goals = [('target', formula)]
    if both_polarities:
        goals.append(('negation', formula.negated()))
    for polarity, goal in goals:
        for commitment in (None, *commitments.commitments):
            premises = () if commitment is None else (commitment.formula,)
            result = cached_entails(premises, goal, timeout_ms)
            row = dict(polarity=polarity, commitment_id=commitment.id if commitment else None,
                       result=result, formula_sha256=formula_hash(goal), timeout_ms=timeout_ms)
            checks.append(row)
            if result == 'SOLVER_UNSAT':
                return dict(status='trivial', reason='single_commitment_entailment' if commitment else
                            'valid_without_support', checks=checks, **{k: row[k] for k in ('polarity','commitment_id')})
    unresolved = any(c['result'] != 'SOLVER_COUNTEREXAMPLE' for c in checks)
    return dict(status='unresolved' if unresolved else 'candidate',
                reason='solver_unresolved' if unresolved else 'no_single_support', checks=checks)
