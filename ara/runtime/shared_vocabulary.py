"""Opt-in construction guidance and descriptive vocabulary diagnostics."""
from collections import defaultdict


SHARED_CONTRACT = '''
SHARED VOCABULARY CONTRACT (shared-vocabulary-v1):
Use the growing run-level shared_symbols catalogue as the semantic starting point.
Before introducing a symbol, compare the source-supported relation and its argument
roles with existing definitions. Reuse only the same meaning and signature; record
that semantic judgment in alignments. Prefer content-level predicate/constant names
independent of source IDs. Source identity and endorsement belong in provenance.
When supported, factor claims into predicates with explicit arguments, shared terms,
quantifiers and logical connectives. Reuse shared subformulas in conditionals so a
premise from another source can instantiate the same relation. Preserve scope,
argument order, qualifications, context indices and distinctions; similar wording
alone never licenses reuse. Do not encode a relational claim as one per-source
atom merely to avoid using structure. If evidence does not justify structure, keep
a faithful atom; never invent structure or equivalence to improve reuse metrics.
New definitions must specify argument roles and evidence_ids. Do not populate a
speculative starter ontology or rewrite previously accepted definitions. This
contract replaces the default source-prefixed naming preference only.
'''


def vocabulary_policy(config):
    enabled = config.get('construction_shared_vocabulary', False)
    top_k = config.get('construction_alignment_top_k', 0)
    if type(enabled) is not bool:
        raise ValueError('construction_shared_vocabulary must be boolean')
    if type(top_k) is not int or top_k < 0:
        raise ValueError('construction_alignment_top_k must be a nonnegative integer')
    keys = ('construction_shared_vocabulary', 'construction_alignment_top_k')
    if any(isinstance(s, dict) and any(k in s for k in keys) for s in config.get('stages', {}).values()):
        raise ValueError('shared vocabulary settings are run-level only')
    return dict(version='shared-vocabulary-v1') if enabled else None


def vocabulary_metrics(commitments, symbols, provenance):
    """Count actual formula uses; catalogue evidence bindings alone miss later reuse.

    MP is a narrow structural opportunity count, not a licensed route or a complete
    bank sweep. Only source-endorsed rows seed its two premise slots.
    """
    from ara.runtime.construction import formula_symbols
    uses = defaultdict(set)
    contextual_uses = defaultdict(set)
    endorsed = defaultdict(set)
    for c in commitments.commitments:
        row = provenance[c.id]
        source = row.get('source_id')
        for name, _, _ in formula_symbols(c.formula):
            contextual_uses[name].update([source] if source is not None else row.get('source_ids', []))
        if source is not None:
            for name, _, _ in formula_symbols(c.formula):
                uses[name].add(source)
            if row.get('stance') == 'endorsed':
                endorsed[c.formula.canonical()].add(source)
    mp = 0
    for c in commitments.commitments:
        row = provenance[c.id]
        if c.formula.op != 'implies' or row.get('stance') != 'endorsed' or row.get('source_id') is None:
            continue
        mp += sum(source != row['source_id'] for source in endorsed[c.formula.args[0].canonical()])
    count = len(commitments.commitments)
    atoms = sum(c.formula.op == 'atom' for c in commitments.commitments)
    return dict(commitments=count, bare_atoms=atoms, bare_atom_fraction=atoms/count if count else 0,
                symbols=len(symbols), shared_symbols=sum(len(sources) >= 2 for sources in uses.values()),
                shared_symbols_including_alignment_context=sum(len(sources) >= 2 for sources in contextual_uses.values()),
                shared_predicates=sum(s['kind'] == 'predicate' and len(uses[s['name']]) >= 2 for s in symbols),
                cross_paper_modus_ponens_candidates=mp,
                metric_scope='actual source formula uses; endorsed exact antecedent MP only; not licensed routes')
