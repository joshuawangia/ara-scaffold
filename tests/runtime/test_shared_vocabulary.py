"""Opt-in common vocabulary and bounded cross-source retrieval, placeholders only."""
from copy import deepcopy
import json
import pytest

from ara.runtime.symbol_alignment import candidate_inventory, retrieval_settings, align_symbols
from ara.runtime.commitment_provenance import make_commitment_provenance, validate_commitment_provenance
from ara.runtime.frozen_catalogue import make_catalogue
from test_extraction import rig, ROOT
from test_symbol_alignment import fixture, configure_judge
from test_construction_recovery import setup, records


def test_shared_policy_is_counted_keyed_and_plan_bound(rig, monkeypatch):
    from ara.runtime.construction import construct
    calls, _, literature, sent = setup(rig, monkeypatch)
    legacy = calls.render('build_t_batch', {})
    calls.config['construction_shared_vocabulary'] = True
    enabled = calls.render('build_t_batch', {})
    assert 'Prefer source-prefixed names.' not in enabled[0]
    assert 'SHARED VOCABULARY CONTRACT' in enabled[0]
    assert 'same meaning and signature' in enabled[0]
    assert legacy != enabled
    construct(calls, literature, 'P')
    plan = records(calls, 'build_t_plan')[0]['plan']
    assert plan['shared_vocabulary_policy']['version'] == 'shared-vocabulary-v1'
    assert all(i['plan']['shared_vocabulary_policy'] == plan['shared_vocabulary_policy'] for _, i in sent)
    assert records(calls, 'construction_vocabulary_metrics')[0]['metrics']['commitments'] == 3
    calls.config['construction_shared_vocabulary'] = False
    assert calls.render('build_t_batch', {}) == legacy


@pytest.mark.parametrize('key,value', [('construction_shared_vocabulary', 'yes'),
    ('construction_alignment_top_k', True), ('construction_alignment_top_k', -1),
    ('construction_alignment_top_k', 1.5)])
def test_vocabulary_settings_refuse_invalid_and_stage_overrides(rig, key, value):
    calls = rig[0]
    from ara.runtime.shared_vocabulary import vocabulary_policy
    calls.config[key] = value
    with pytest.raises(ValueError): vocabulary_policy(calls.config)
    calls.config.pop(key)
    calls.config.setdefault('stages', {})['build_t_batch'] = {key: True}
    with pytest.raises(ValueError, match='run-level'): vocabulary_policy(calls.config)


def test_wide_retrieval_includes_zero_overlap_with_per_symbol_coverage():
    symbols = [dict(name=n, kind='atom', arity=0, definition=n, evidence_ids=[n]) for n in 'PQRS']
    rows = {n: dict(source_id=n) for n in 'PQRS'}
    assert candidate_inventory(symbols, rows)['candidates'] == []
    result = candidate_inventory(symbols, rows, 6, per_symbol_top_k=3)
    assert len(result['candidates']) == 6 and result['zero_overlap_pairs'] == 6
    assert result['covered_symbols'] == list('PQRS')
    assert result == candidate_inventory(symbols[::-1], rows, 6, per_symbol_top_k=3)
    limited = candidate_inventory(symbols, rows, 2, per_symbol_top_k=1)
    assert len(limited['candidates']) == 2 and limited['truncated']
    rows['Q']['source_id'] = 'P'
    pairs = candidate_inventory(symbols, rows, 10, per_symbol_top_k=3)['candidates']
    assert not any(p['left']=='P' and p['right']=='Q' for p in pairs)


def test_wide_native_alignment_replays_and_refuses_policy_tampering(rig, monkeypatch):
    calls, requests = configure_judge(rig, monkeypatch, 'same_content')
    calls.config['construction_alignment_top_k'] = 2
    t, symbols, rows = fixture()
    for s in symbols: s['definition'] = s['name']
    result, final_symbols, final_rows, receipt = align_symbols(calls, t, symbols, rows)
    assert len(requests) == 3
    assert len(final_symbols) == 1
    assert receipt['retrieval']['per_symbol_top_k'] == 2
    catalogue = make_catalogue(result, final_symbols)
    meta = make_commitment_provenance(result, catalogue, final_rows, alignment=receipt)
    assert validate_commitment_provenance(meta, result, catalogue) == meta
    from ara.runtime.export import methodology
    report = json.loads(methodology(calls.log.path).split('```json\n')[1].split('\n```')[0])
    metrics = report['construction']['alignment_vocabulary_metrics'][0]
    assert metrics['before']['shared_symbols'] == 0 and metrics['after']['shared_symbols'] == 1
    bad = deepcopy(meta)
    bad['alignment']['retrieval']['per_symbol_top_k'] = 1
    from ara.runtime.cache import canonical, digest
    bad['sha256'] = digest(canonical({k:v for k,v in bad.items() if k!='sha256'}))
    with pytest.raises(ValueError, match='retrieval'): validate_commitment_provenance(bad, result, catalogue)


def test_metrics_count_actual_source_uses_and_cross_paper_modus_ponens():
    from ara.runtime.shared_vocabulary import vocabulary_metrics
    from ara.types import Commitment, CommitmentSet, Formula
    p,q = [Formula('atom', name=n) for n in 'PQ']
    t = CommitmentSet((Commitment('a:p','P','a:1',p),
        Commitment('b:i','P Q','b:1',Formula('implies',(p,q)))))
    symbols = [dict(name=n, kind='atom', arity=0, definition=n, evidence_ids=[id])
               for n,id in [('P','a:p'),('Q','b:i')]]
    rows = {'a:p':dict(source_id='a',stance='endorsed'), 'b:i':dict(source_id='b',stance='endorsed')}
    metrics = vocabulary_metrics(t, symbols, rows)
    assert metrics['bare_atoms'] == 1 and metrics['bare_atom_fraction'] == .5
    assert metrics['shared_symbols'] == 1
    assert metrics['cross_paper_modus_ponens_candidates'] == 1
    rows['a:p']['stance'] = 'reported'
    assert vocabulary_metrics(t, symbols, rows)['cross_paper_modus_ponens_candidates'] == 0


def test_wide_resume_uses_recorded_inventory(rig, monkeypatch):
    from ara.bank import load_bank
    from ara.runtime.alignment_resume import load_alignment_resume
    from ara.runtime.budget import BudgetStop
    from test_alignment_resume import completed
    calls = rig[0]
    calls.config.update(construction_alignment_top_k=1, construction_alignment_candidates=2)
    t, symbols, rows = completed(calls)
    def fail(*args): raise RuntimeError('P')
    monkeypatch.setattr(calls.provider, 'complete', fail)
    with pytest.raises(BudgetStop): align_symbols(calls, t, symbols, rows)
    restored = load_alignment_resume(calls.log, load_bank(ROOT/'bank'))
    assert len(restored['candidates']) == 2
    assert restored['run']['config']['construction_alignment_top_k'] == 1


def test_shared_predicate_reuse_passes_native_freeze_and_licensed_mp(rig, monkeypatch):
    from dataclasses import replace
    from ara.bank import load_bank
    from ara.runtime.extraction import extract
    from ara.runtime.orchestration import prepare_commitments
    from ara.runtime.providers import Response
    from ara.runtime.frozen_catalogue import validate_frozen_artifact
    from ara.runtime.commitment_provenance import load_commitment_provenance
    from ara.formal import entails
    from ara.engine.matching import matches_schema
    from ara.types import Formula, Term
    from test_extraction import register, response
    from rich_fixture import graph, batch_response
    calls, provider, papers, *_ = rig
    second = replace(papers[0], source_id='q', record_json=json.dumps(dict(id='q',title='Q')))
    for paper in (papers[0], second):
        value = graph(paper.source_id); value['items'] = value['items'][:1]
        register(calls, provider, paper, value)
    literature = extract(calls, (papers[0], second)).read_text()
    calls.config.update(construction_shared_vocabulary=True, construction_alignment_candidates=0)
    p = Formula('predicate', name='F', terms=(Term('constant','a'),))
    q = Formula('predicate', name='G', terms=(Term('constant','a'),))
    requests = []
    estimate = provider.estimate
    def count(kind, prompt, schema, maximum):
        from ara.types import TokenUsage
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'select_t_roots' and len(inputs.get('papers', [])) > 1:
            return TokenUsage(input_tokens=70001, output_tokens=maximum)
        return estimate(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'estimate', count)
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind != 'build_t_batch': return Response(response(batch_response(inputs)))
        requests.append(inputs)
        item = inputs['papers'][0]['items'][0]
        prior = bool(inputs['shared_symbols'])
        formula = Formula('implies',(p,q)) if prior else p
        new = [('G','predicate',1)] if prior else [('F','predicate',1),('a','constant',0)]
        return Response(response(dict(commitments=[dict(id=item['id'],definition='P Q',formula=formula.to_dict())],
            new_symbols=[dict(name=n,kind=k,arity=a,definition=n,evidence_ids=[item['id']]) for n,k,a in new],
            alignments=[dict(name=n,reason='P') for n in ('F','a')] if prior else [])))
    monkeypatch.setattr(provider, 'complete', complete)
    bank = load_bank(ROOT/'bank')
    t = prepare_commitments(calls, bank, literature, 'P')
    assert len(requests)==2 and {s['name'] for s in requests[1]['shared_symbols']}=={'F','a'}
    catalogue = validate_frozen_artifact(json.loads((calls.log.path.parent/'frozen-t.json').read_text()),t)
    meta = load_commitment_provenance(calls.log.path.parent,t,catalogue)
    from ara.runtime.shared_vocabulary import vocabulary_metrics
    metrics = vocabulary_metrics(t,catalogue['symbols'],meta['commitments'])
    assert metrics['shared_predicates']==1 and metrics['cross_paper_modus_ponens_candidates']==1
    conditional = next(c.formula for c in t.commitments if c.formula.op=='implies')
    assert matches_schema(bank.get('modus_ponens').formula_schema,{'conditional':conditional,'antecedent':p},q)
    assert entails(tuple(c.formula for c in t.commitments),q,1000)=='SOLVER_UNSAT'
    from ara.engine.licensing import Licenser
    from ara.engine.forward import _CanonicalFormaliser
    from ara.types import Proposal, PremiseFill, Proposition
    proposal = Proposal('modus_ponens', (PremiseFill('conditional',conditional.to_json()),
        PremiseFill('antecedent',p.to_json())), q.to_json())
    assert Licenser(bank,_CanonicalFormaliser(),calls.log).check(proposal,Proposition('Q','Q',q)).licensed
    assert len(records(calls,'commitments_frozen'))==1
