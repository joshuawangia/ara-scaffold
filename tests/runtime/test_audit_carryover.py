"""Verified sentence carry-over uses native audit receipts, never fuzzy verdicts."""
import copy
import json
from itertools import chain, repeat

import pytest

from ara.runtime.calls import EssayAuditFailed
from ara.runtime.essay_audit import audit_consensus
from ara.runtime.providers import Response
from test_calls import response, rig
from test_sectioned_writer import seed_sources


def setup_source(rig, monkeypatch, *, first='This paper argues that P, Q, and R.', votes=('equivalent',)*3, vary_source_roles=False, source_shape_retry=False):
    calls, provider, log = rig
    route = seed_sources(calls, log)
    calls.config.update(essay_min_words=4500, token_cap=20_000_000, validation_attempts=2 if source_shape_retry else 1)
    source = dict(title='S', body='[[node:n0]] '+first+' [cite:p]\n[[node:n1]] We argue that Q. [cite:q]',
                  bibliography=[dict(id=t, text='a (2000). P. Q. PDF p. 1.', url=None) for t in ('p','q')])
    from ara.runtime.writing import source_context
    source['bibliography']=source_context(calls,route)['allowed_bibliography']
    seen=[]
    state=dict(adverse=False, votes=chain(votes, repeat('equivalent')))
    def complete(kind, prompt, schema, maximum):
        inputs=json.loads(prompt.split('\nINPUT_JSON\n')[1]);seen.append((kind,inputs))
        if kind=='audit_meaning':
            vote=next(state['votes'])
            value=dict(pairs=[dict(sentence=p['sentence'], source_sentence=p['source_sentence'], verdict=vote, reason='P') for p in inputs['pairs']])
        else:
            labels=[]
            for s in inputs['sentences']:
                nodes=['n0'] if '[cite:p]' in s['text'] else ['n1'] if '[cite:q]' in s['text'] else []
                adverse=state['adverse'] and s.get('field')!='title' and not s['text'].startswith('##')
                labels.append(dict(sentence=s['sentence'], node_ids=nodes,
                    role='unsupported_claim' if adverse else ('source_claim' if vary_source_roles and len(seen)==2 else 'argument_step') if nodes else 'framing',
                    citation_supported=not adverse,
                    **({'publication_issue':'unsupported_elaboration' if adverse else 'none'} if kind=='audit_publication' else {})))
            value=dict(labels=labels[:-1] if source_shape_retry and len(seen)==2 else labels)
        return Response(response(value))
    monkeypatch.setattr(provider,'complete',complete)
    audit_consensus(calls,route,source)
    log.record('final_draft',route_id=route.id,draft=source)
    state['adverse']=True
    return calls,route,source,state,seen


def revised(source, first='P, Q and R.'):
    return {**source,'body':'[[node:n0]] '+first+' [cite:p]\n[[node:n1]] Q. [cite:q]'}


def run(calls,route,source,draft):
    return audit_consensus(calls,route,draft,publication_context=dict(original_draft=source,literature_currency=None))


def test_prefix_only_inherits_verified_role_and_keeps_raw_dissent(rig,monkeypatch):
    calls,route,source,_,seen=setup_source(rig,monkeypatch)
    result=run(calls,route,source,revised(source))
    assert result['faithful'] and result['flags']==[]
    assert len(result['verified_sentence_carryover']['sentences'])==2
    assert {s['method'] for s in result['verified_sentence_carryover']['sentences']}=={'prefix_only'}
    assert all(s['label']['role']=='argument_step' for s in result['verified_sentence_carryover']['sentences'])
    assert [k for k,_ in seen].count('audit_publication')==3
    assert not any(k=='audit_meaning' for k,_ in seen)
    raw=[e for e in calls.log.read() if e['stage']=='audit_publication' and e['label']=='MODEL']
    assert all('unsupported_claim' in e['response'] for e in raw)


@pytest.mark.parametrize('text', ['P, Q and S.', 'Not P, Q and R.', 'According to a, P, Q and R.'])
def test_substantive_or_attribution_change_retains_dissent(rig,monkeypatch,text):
    calls,route,source,_,seen=setup_source(rig,monkeypatch,votes=('equivalent','different','equivalent'))
    with pytest.raises(EssayAuditFailed) as exc:
        run(calls,route,source,revised(source,text))
    assert 1 in exc.value.result['extra_steps']
    assert 2 not in exc.value.result['extra_steps']
    assert [k for k,_ in seen].count('audit_meaning')==3


def test_meaning_equivalent_rewording_inherits_after_three_votes(rig,monkeypatch):
    calls,route,source,_,seen=setup_source(rig,monkeypatch)
    result=run(calls,route,source,revised(source,'P together with Q and R.'))
    assert result['faithful']
    rows=result['verified_sentence_carryover']['sentences']
    assert rows[0]['method']=='meaning_preserved'
    assert [v['verdict'] for v in rows[0]['votes']]==['equivalent']*3
    assert [k for k,_ in seen].count('audit_meaning')==3


@pytest.mark.parametrize('change', ['citation','bibliography','no_final','wrong_source','adverse_gate'])
def test_unverified_or_recited_text_cannot_inherit(rig,monkeypatch,change):
    calls,route,source,_,_=setup_source(rig,monkeypatch,votes=('different',)*3)
    draft=revised(source)
    if change=='citation':draft['body']=draft['body'].replace('[cite:p]','[cite:q]',1)
    if change=='bibliography':draft['bibliography']=[{**b,'text':'R'} for b in source['bibliography']]
    if change=='no_final':calls.log.record('essay_composition_started',route_id=route.id)
    if change=='wrong_source':source={**source,'title':'R'}
    if change=='adverse_gate':
        calls.log.record('essay_audit_consensus',audit_kind='audit_essay',route_id=route.id,faithful=False)
        calls.log.record('final_draft',route_id=route.id,draft=source)
    with pytest.raises(EssayAuditFailed):run(calls,route,source,draft)


def test_prior_nonprefix_adverse_history_is_not_erased(rig,monkeypatch):
    calls,route,source,state,_=setup_source(rig,monkeypatch,votes=('different',)*3)
    draft=revised(source,'P, Q and S.')
    # A pre-adjustment model receipt has no derived carry-over metadata.
    inputs=calls.audit_inputs(route,draft,publication_context=dict(original_draft=source,literature_currency=None))
    inputs.pop('verified_sentence_carryover',None)
    from ara.runtime.essay_audit import audit_result
    calls.call('audit_publication',inputs,lambda data:audit_result(route,draft,inputs,data),fresh=True)
    state['adverse']=False
    with pytest.raises(EssayAuditFailed) as exc:run(calls,route,source,draft)
    assert exc.value.result['extra_steps']==[1]
    assert exc.value.result['historical_adverse']


def test_meaning_dissent_survives_resume_without_reroll(rig,monkeypatch):
    calls,route,source,state,seen=setup_source(rig,monkeypatch,votes=('equivalent','uncertain','equivalent'))
    draft=revised(source,'P together with Q and R.')
    with pytest.raises(EssayAuditFailed):run(calls,route,source,draft)
    state['adverse']=False
    with pytest.raises(EssayAuditFailed):run(calls,route,source,draft)
    assert [k for k,_ in seen].count('audit_meaning')==3


def test_scope_broadening_requires_meaning_and_retains_dissent(rig,monkeypatch):
    calls,route,source,_,seen=setup_source(rig,monkeypatch,
        first='This paper argues that these P satisfy Q.',votes=('equivalent','different','equivalent'))
    with pytest.raises(EssayAuditFailed) as exc:
        run(calls,route,source,revised(source,'The P closest to R satisfy Q.'))
    assert 1 in exc.value.result['extra_steps']
    decisions=exc.value.result['verified_sentence_carryover']['meaning_checks']
    assert decisions[0]['outcome']=='normal_audit'
    assert [v['verdict'] for v in decisions[0]['votes']]==['equivalent','different','equivalent']


def test_new_unaligned_sentence_is_audited_normally(rig,monkeypatch):
    calls,route,source,_,seen=setup_source(rig,monkeypatch)
    draft=revised(source);draft['body']+='\nS.'
    with pytest.raises(EssayAuditFailed) as exc:run(calls,route,source,draft)
    assert exc.value.result['extra_steps']==[3]
    assert not any(k=='audit_meaning' for k,_ in seen)


@pytest.mark.parametrize('shape',['missing','duplicate','unknown_node'])
def test_carryover_does_not_validate_malformed_current_inventory(rig,monkeypatch,shape):
    from ara.runtime.calls import Rejected
    calls,route,source,_,_=setup_source(rig,monkeypatch)
    def malformed(kind,prompt,schema,maximum):
        inputs=json.loads(prompt.split('\nINPUT_JSON\n')[1])
        labels=[dict(sentence=s['sentence'],node_ids=[] if s.get('field')=='title' else ['n0','n1'],
                     role='framing' if s.get('field')=='title' else 'argument_step',citation_supported=True,
                     publication_issue='none') for s in inputs['sentences']]
        if shape=='missing':labels=labels[:-1]
        if shape=='duplicate':labels[-1]=labels[0]
        if shape=='unknown_node':labels[0]['node_ids']=['unknown']
        return Response(response(dict(labels=labels)))
    monkeypatch.setattr(calls.provider,'complete',malformed)
    with pytest.raises(Rejected):run(calls,route,source,revised(source))


def test_malformed_meaning_retry_retains_valid_adverse_vote(rig,monkeypatch):
    calls,route,source,_,_=setup_source(rig,monkeypatch)
    original=calls.provider.complete
    assert calls.config.get('validation_attempts',1)==1
    count=0
    def complete(kind,prompt,schema,maximum):
        nonlocal count
        if kind!='audit_meaning':return original(kind,prompt,schema,maximum)
        count+=1
        inputs=json.loads(prompt.split('\nINPUT_JSON\n')[1]);p=inputs['pairs'][0]
        rows=[dict(sentence=p['sentence'],source_sentence=p['source_sentence'],verdict='different' if count==1 else 'equivalent',reason='P')]
        if count==1:rows*=2
        return Response(response(dict(pairs=rows)))
    monkeypatch.setattr(calls.provider,'complete',complete)
    with pytest.raises(EssayAuditFailed) as exc:run(calls,route,source,revised(source,'P together with Q and R.'))
    assert count==4
    decision=exc.value.result['verified_sentence_carryover']['meaning_checks'][0]
    assert not decision['inherited'] and decision['historical_adverse']


def test_alignment_exposes_exact_source_occurrence_with_markers(rig,monkeypatch):
    from ara.runtime.audit_carryover import aligned_pairs,verified_source_rows
    calls,route,source,_,_=setup_source(rig,monkeypatch)
    draft=revised(source)
    inputs=calls.audit_inputs(route,draft,publication_context=dict(original_draft=source))
    verified=verified_source_rows(calls,route,draft,inputs)
    pair=aligned_pairs(verified,inputs,draft)[0]
    assert pair['raw_source_text']==source['body'][pair['source_start']:pair['source_end']]
    assert '[[node:n0]]' in pair['raw_source_text']
    assert '[[node:' not in pair['source_text']


@pytest.mark.parametrize('resume', [False, True])
def test_missing_meaning_inventory_keeps_all_51_adverse_votes(rig, monkeypatch, resume):
    from ara.runtime.audit_carryover import aligned_pairs, verified_source_rows
    from ara.runtime.calls import InvalidOutput
    from jsonschema import ValidationError

    first=' [cite:p]\n'.join(f'This paper argues that P{i:03d}, Q, and R.' for i in range(101))
    calls,route,source,_,_=setup_source(rig,monkeypatch,first=first)
    # Leave room for the all-inherited mutation: it must fail on lost adverse
    # votes, not incidentally hit the mock context ceiling.
    calls.config['model_context_token_bound']=2_000_000
    draft={**source, 'body': source['body'].replace('This paper argues that ', '').replace(', Q, and R.', ' together with Q and R.').replace('We argue that ', '')}
    inputs=calls.audit_inputs(route,draft,publication_context=dict(original_draft=source,literature_currency=None))
    bound=verified_source_rows(calls,route,draft,inputs)
    pairs=[p for p in aligned_pairs(bound,inputs,draft) if p['method']=='meaning_check']
    assert len(pairs)==101
    missing={pairs[i]['sentence'] for i in (35,61,63)}
    returned=[p for p in pairs if p['sentence'] not in missing]
    adverse={p['sentence'] for p in returned[:51]}
    original=calls.provider.complete
    requests=[]
    def complete(kind,prompt,schema,maximum):
        if kind!='audit_meaning':return original(kind,prompt,schema,maximum)
        request=json.loads(prompt.split('\nINPUT_JSON\n')[1]);requests.append(request)
        selected=returned if len(requests)==1 else request['pairs']
        rows=[dict(sentence=p['sentence'],source_sentence=p['source_sentence'],
                   verdict='different' if len(requests)==1 and p['sentence'] in adverse else 'equivalent',reason='P') for p in selected]
        return Response(response(dict(pairs=rows)))
    monkeypatch.setattr(calls.provider,'complete',complete)
    if resume:
        request=dict(source_sha256=bound['source_sha256'],gate_sha256=bound['gate_sha256'],pairs=pairs,
                     outline=inputs['outline'],proposal=inputs.get('proposal'))
        def reject(data):raise ValidationError('meaning check pair inventory mismatch')
        with pytest.raises(InvalidOutput):calls.call('audit_meaning',request,reject,fresh=True)
    with pytest.raises(EssayAuditFailed) as exc:run(calls,route,source,draft)
    assert calls.config.get('validation_attempts',1)==1
    assert len(requests)==4
    decisions=exc.value.result['verified_sentence_carryover']['meaning_checks']
    assert len(decisions)==101
    assert {p['sentence'] for p in decisions if not p['inherited']}==adverse
    assert {p['sentence'] for p in decisions if p['historical_adverse']}==adverse
    assert set(exc.value.result['extra_steps'])==adverse
    assert all([v['verdict'] for v in p['votes']]==['equivalent']*3 for p in decisions)
    if not resume:
        feedback=json.dumps(requests[1]['validation_feedback'])
        assert 'missing=' in feedback and 'extra=[]' in feedback and 'duplicates=[]' in feedback
        for p in pairs:
            if p['sentence'] in missing:assert str([p['sentence'],p['source_sentence']]) in feedback
    with pytest.raises(EssayAuditFailed):run(calls,route,source,draft)
    assert len(requests)==4  # Persisted decisions cannot be rerolled.


def test_meaning_shape_retry_stops_after_one_correction(rig,monkeypatch):
    from ara.runtime.calls import InvalidOutput
    calls,route,source,_,seen=setup_source(rig,monkeypatch)
    original=calls.provider.complete
    requests=[]
    def complete(kind,prompt,schema,maximum):
        if kind!='audit_meaning':return original(kind,prompt,schema,maximum)
        inputs=json.loads(prompt.split('\nINPUT_JSON\n')[1]);requests.append(inputs)
        return Response(response(dict(pairs=[])))
    monkeypatch.setattr(calls.provider,'complete',complete)
    with pytest.raises(InvalidOutput,match='meaning check pair inventory mismatch'):
        run(calls,route,source,revised(source,'P together with Q and R.'))
    assert len(requests)==2
    assert 'validation_feedback' not in requests[0]
    assert 'validation_feedback' in requests[1]
    assert not any(k=='audit_publication' for k,_ in seen)
    assert not any(e['stage']=='sentence_meaning_consensus' for e in calls.log.read())


def test_prefix_removal_allows_only_sentence_initial_capitalization(rig, monkeypatch):
    calls, route, source, _, seen = setup_source(rig, monkeypatch, first='This paper argues that p entails Q.')
    draft = revised(source, 'P entails Q.')
    inputs = calls.audit_inputs(route, draft, publication_context=dict(original_draft=source))
    rows = inputs['verified_sentence_carryover']['sentences']
    assert {r['sentence'] for r in rows if r['method']=='prefix_only'} == {1, 2}
    assert len(seen) == 3  # Source receipts only; no meaning or publication call.


@pytest.mark.parametrize('text', ['P entails q.', 'P does not entail Q.', 'P entails R.'])
def test_prefix_capitalization_does_not_hide_other_word_changes(rig, monkeypatch, text):
    calls, route, source, _, seen = setup_source(rig, monkeypatch, first='This paper argues that p entails Q.')
    inputs = calls.audit_inputs(route, revised(source,text), publication_context=dict(original_draft=source))
    assert 1 not in {r['sentence'] for r in inputs['verified_sentence_carryover']['sentences']}
    assert len(seen) == 3
