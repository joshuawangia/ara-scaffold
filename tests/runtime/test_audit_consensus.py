"""Conservative final audit evidence; all fixtures use placeholders."""
import json

import pytest

from ara.runtime.calls import EssayAuditFailed
from ara.runtime.providers import Response
from test_calls import graph, response, rig


def draft():
    return dict(title='P', body='[[node:n1]] P. Q. R.', bibliography=[])


def sample(*flagged):
    return {'labels': [dict(sentence=n, node_ids=['n1'], citation_supported=True,
        role='unsupported_claim' if n in flagged else 'argument_step') for n in (1, 2, 3)]}


def responder(provider, monkeypatch, values):
    pending = iter(values)
    seen = []
    def complete(kind, prompt, schema, maximum):
        seen.append((kind, prompt))
        return Response(response(next(pending)))
    monkeypatch.setattr(provider, 'complete', complete)
    return seen


def test_one_dissent_blocks_and_reports_sentence_agreement(rig, monkeypatch):
    from ara.runtime.essay_audit import audit_consensus
    calls, provider, log = rig
    seen = responder(provider, monkeypatch, [sample(), sample(2), sample()])
    with pytest.raises(EssayAuditFailed) as failure:
        audit_consensus(calls, graph(), draft())
    assert len(seen) == 3 and len({p for _, p in seen}) == 1
    assert failure.value.result['extra_steps'] == [2]
    receipt = json.loads(next(e['payload_json'] for e in log.read() if e['stage']=='essay_audit_consensus'))
    assert [s['extra_steps'] for s in receipt['samples']] == [[], [2], []]
    assert receipt['sentences'][1] == {'sentence':2, 'flagged_samples':[2], 'clean_samples':[1,3],
        'historical_flags':[], 'agreement':2/3}
    assert not receipt['faithful'] and receipt['unanimous_sentences']==2
    assert not list(calls.cache.path.glob('*.json'))


def test_adverse_history_and_favourable_cache_cannot_approve(rig, monkeypatch):
    from ara.runtime.essay_audit import audit_consensus
    calls, provider, log = rig
    seen = responder(provider, monkeypatch, [sample(2), sample(), sample(), sample(), sample()])
    with pytest.raises(EssayAuditFailed): calls.audit_essay(graph(), draft())
    calls.audit_essay(graph(), draft())  # Historical favourable response cache.
    assert list(calls.cache.path.glob('*.json'))
    with pytest.raises(EssayAuditFailed) as failure:
        audit_consensus(calls, graph(), draft())
    assert len(seen) == 5  # Three new transports despite the favourable cache.
    assert failure.value.result['extra_steps'] == [2]
    receipt = json.loads([e['payload_json'] for e in log.read() if e['stage']=='essay_audit_consensus'][-1])
    assert len(receipt['historical_adverse'])==1
    assert receipt['sentences'][1]['historical_flags']==['unsupported_claim']
    models=[json.loads(e['payload_json']) for e in log.read() if e['label']=='MODEL']
    assert all(not row['cache_hit'] for row in models[-3:])


def test_fresh_unanimous_gate_and_configured_sample_count(rig, monkeypatch):
    from ara.runtime.essay_audit import audit_consensus
    from ara.runtime.export import methodology
    calls, provider, log = rig
    calls.config['essay_audit_samples']=4
    seen=responder(provider, monkeypatch, [sample()]*4)
    result=audit_consensus(calls, graph(), draft())
    assert result['faithful'] and result['k']==4 and len(seen)==4
    assert result['unanimous_sentences']==3
    summary=json.loads(methodology(log.path).split('```json\n')[1].split('\n```')[0])
    assert summary['essay_audit_consensus'][-1]==result
    assert not list(calls.cache.path.glob('*.json'))


@pytest.mark.parametrize('value',[0,1,2,True,3.0,'3'])
def test_invalid_sample_count_refuses_before_dispatch(rig, monkeypatch, value):
    from ara.runtime.essay_audit import audit_consensus
    calls, provider, _=rig
    calls.config['essay_audit_samples']=value
    seen=responder(provider, monkeypatch, [])
    with pytest.raises(ValueError,match='essay_audit_samples'):
        audit_consensus(calls,graph(),draft())
    assert seen==[]


def final_responder(provider, monkeypatch, *, always_adverse=False, initial_adverse=False):
    seen=[]
    batches={}
    def complete(kind, prompt, schema, maximum):
        data=json.loads(prompt.split('\nINPUT_JSON\n')[1]);seen.append((kind,data))
        if kind=='audit_essay':
            body=' '.join(s['text'] for s in data['sentences'])
            batches[body]=batches.get(body,0)+1
            # The first audit is the pre-verification audit. Final samples then
            # disagree across different sentences, requiring their union.
            adverse = batches[body] > 1 and (always_adverse or 'Q.' in body)
            flag = 2 if batches[body]%2==0 else 3
            value=sample(flag) if adverse else sample()
            if initial_adverse and len(seen)==1: value=sample(2)
        elif kind=='revise_essay':
            value={'revisions':[dict(sentence=s['sentence'],text='S' + ' S' * (data['round'] - 1) + '.') for s in data['flagged_sentences']]}
        elif kind=='search_evidence': value='P'
        elif kind=='verify_originality_citations':
            value={'items':[], 'originality':{'assessment':'unverified','evidence_urls':[],'detail':'P'}}
        else: raise AssertionError(kind)
        return Response(response(value))
    monkeypatch.setattr(provider,'complete',complete)
    return seen


def test_native_final_union_repaired_then_reverified_and_freshly_audited(rig,monkeypatch):
    from ara.runtime.orchestration import compose
    calls,provider,log=rig
    seen=final_responder(provider,monkeypatch)
    log.record('route', graph=graph().to_dict())
    result=compose(calls,graph(),draft())
    assert result['body']=='[[node:n1]] P. S. S.'
    repair=next(data for kind,data in seen if kind=='revise_essay')
    assert {f['sentence'] for f in repair['flags']}=={2,3}
    assert [kind for kind,_ in seen].count('verify_originality_citations')==2
    assert [kind for kind,_ in seen].count('audit_essay')==7
    assert (log.path.parent/'draft.json').is_file()
    assert (log.path.parent/'export/essay.txt').is_file()
    gates=[json.loads(e['payload_json']) for e in log.read() if e['stage']=='essay_audit_consensus']
    assert [g['faithful'] for g in gates]==[False,True]
    assert len(gates[-1]['samples'])==3
    from ara.runtime.report import build_run
    report=build_run(log.path.parent)
    assert [r['payload'] for r in report['routes'][0]['audit_results']
            if r['stage']=='essay_audit_consensus']==gates


def test_failed_final_gate_cannot_export_old_success_and_repairs_are_bounded(rig,monkeypatch):
    from ara.runtime.orchestration import compose
    from ara.runtime.export import export_run
    calls,provider,log=rig
    log.record('final_draft',route_id='r1',draft=draft())
    (log.path.parent/'draft.json').write_text(json.dumps(draft()))
    export_run(log.path,log.path.parent/'export')
    seen=final_responder(provider,monkeypatch,always_adverse=True)
    with pytest.raises(EssayAuditFailed): compose(calls,graph(),draft())
    assert [kind for kind,_ in seen].count('revise_essay')==3
    assert not (log.path.parent/'draft.json').exists()
    _,essay=export_run(log.path,log.path.parent/'export')
    assert essay is None and not (log.path.parent/'export/essay.txt').exists()
    gates=[json.loads(e['payload_json']) for e in log.read() if e['stage']=='essay_audit_consensus']
    assert len(gates)==4 and all(not g['faithful'] for g in gates)


def test_incomplete_sample_blocks_and_retains_partial_receipt(rig,monkeypatch):
    from ara.runtime.essay_audit import audit_consensus
    from ara.runtime.calls import Rejected
    calls,provider,log=rig
    seen=responder(provider,monkeypatch,[sample(),{'labels':[]}])
    with pytest.raises(Rejected): audit_consensus(calls,graph(),draft())
    receipt=json.loads([e['payload_json'] for e in log.read() if e['stage']=='essay_audit_consensus'][-1])
    assert len(seen)==2 and receipt['status']=='incomplete' and receipt['failed_sample']==2
    assert len(receipt['samples'])==1 and not receipt['faithful']


def test_initial_and_final_repairs_share_three_round_limit(rig,monkeypatch):
    from ara.runtime.orchestration import compose
    calls,provider,log=rig
    seen=final_responder(provider,monkeypatch,always_adverse=True,initial_adverse=True)
    with pytest.raises(EssayAuditFailed): compose(calls,graph(),draft())
    assert [kind for kind,_ in seen].count('revise_essay')==3
    exhausted=json.loads([e['payload_json'] for e in log.read() if e['stage']=='essay_audit_revision_exhausted'][-1])
    assert exhausted['rounds']==3
    assert not (log.path.parent/'draft.json').exists()


def test_malformed_history_is_disclosed_not_counted_as_clean_sample(rig,monkeypatch):
    from ara.runtime.essay_audit import audit_consensus
    from ara.runtime.calls import Rejected
    calls,provider,log=rig
    seen=[]
    def complete(kind,prompt,schema,maximum):
        seen.append(kind)
        raw=response(sample())
        if len(seen)==1:
            raw['content'][0]['text']='```json\n'+raw['content'][0]['text']+'\n```'
        return Response(raw)
    monkeypatch.setattr(provider,'complete',complete)
    with pytest.raises(Rejected): calls.audit_essay(graph(),draft())
    result=audit_consensus(calls,graph(),draft())
    assert result['faithful'] and len(seen)==4
    assert len(result['unusable_history'])==1
    assert len(result['samples'])==3


def test_final_union_rejects_unchanged_flagged_sentences(rig,monkeypatch):
    from ara.runtime.orchestration import compose
    from ara.runtime.calls import Rejected
    calls,provider,log=rig
    final_responder(provider,monkeypatch)
    original=provider.complete
    repairs=[]
    def complete(kind,prompt,schema,maximum):
        if kind=='revise_essay':
            data=json.loads(prompt.split('\nINPUT_JSON\n')[1]);repairs.append(data)
            return Response(response({'revisions':[dict(sentence=s['sentence'],text=s['text'])
                                                  for s in data['flagged_sentences']]}))
        return original(kind,prompt,schema,maximum)
    monkeypatch.setattr(provider,'complete',complete)
    with pytest.raises(Rejected,match='flagged sentence unchanged'):
        compose(calls,graph(),draft())
    assert len(repairs)==1
    assert not any(e['stage']=='essay_audit_revision' for e in log.read())
    assert not (log.path.parent/'draft.json').exists()


def test_verification_cleanup_can_shorten_below_writer_target(rig,monkeypatch):
    from ara.runtime.orchestration import compose
    from ara.runtime.calls import word_count
    calls,provider,log=rig
    calls.config['essay_min_words']=7
    before=dict(title='P',body='[[node:n1]] P Q. "R S T."',bibliography=[])
    def complete(kind,prompt,schema,maximum):
        data=json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind=='audit_essay':
            value={'labels':[dict(sentence=s['sentence'],node_ids=['n1'],role='argument_step',citation_supported=True)
                             for s in data['sentences']]}
        elif kind=='search_evidence': value='P'
        elif kind=='verify_originality_citations':
            value={'items':[{**item,'status':'unverified','action':'remove','detail':'P','evidence_urls':[]}
                            for item in data['items']],
                   'originality':{'assessment':'unverified','evidence_urls':[],'detail':'P'}}
        else:raise AssertionError(kind)
        return Response(response(value))
    monkeypatch.setattr(provider,'complete',complete)
    result=compose(calls,graph(),before)
    assert word_count(result)<7 and 'R S T' not in result['body']
    assert (log.path.parent/'export/essay.txt').exists()
    gate=json.loads([e['payload_json'] for e in log.read() if e['stage']=='essay_audit_consensus'][-1])
    assert gate['faithful'] and len(gate['samples'])==3


def test_resumed_draft_cannot_reset_repair_allowance(rig,monkeypatch):
    from ara.runtime.orchestration import compose
    calls,provider,log=rig
    seen=final_responder(provider,monkeypatch,always_adverse=True)
    with pytest.raises(EssayAuditFailed):compose(calls,graph(),draft())
    partial=json.loads((log.path.parent/'draft.unverified.json').read_text())
    with pytest.raises(EssayAuditFailed):compose(calls,graph(),partial)
    assert [kind for kind,_ in seen].count('revise_essay')==3
    assert not (log.path.parent/'export/essay.txt').exists()


def test_final_repair_can_remain_below_writer_target(rig,monkeypatch):
    from ara.runtime.orchestration import compose
    from ara.runtime.calls import word_count
    calls,provider,log=rig
    calls.config['essay_min_words']=7
    before=dict(title='P',body='[[node:n1]] P Q. "R S T."',bibliography=[])
    repairs=[]
    def complete(kind,prompt,schema,maximum):
        data=json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind=='audit_essay':
            value={'labels':[dict(sentence=s['sentence'],node_ids=['n1'],citation_supported=True,
                role='unsupported_claim' if len(data['sentences'])==1 and 'Q' in s['text'] else 'argument_step')
                for s in data['sentences']]}
        elif kind=='revise_essay':
            repairs.append(data)
            value={'revisions':[dict(sentence=s['sentence'],text=s['text'].replace('Q','S')) for s in data['flagged_sentences']]}
        elif kind=='search_evidence':value='P'
        elif kind=='verify_originality_citations':
            value={'items':[{**item,'status':'unverified','action':'remove','detail':'P','evidence_urls':[]}
                            for item in data['items']],
                   'originality':{'assessment':'unverified','evidence_urls':[],'detail':'P'}}
        else:raise AssertionError(kind)
        return Response(response(value))
    monkeypatch.setattr(provider,'complete',complete)
    result=compose(calls,graph(),before)
    assert word_count(result)<7 and 'Q' not in result['body']
    assert len(repairs)==1 and repairs[0]['minimum_words']==0
    assert (log.path.parent/'export/essay.txt').exists()


def invalid_adverse_sample(mode):
    value = sample(2)
    if mode in ('partial', 'corrected_partial'):
        value['labels'] = value['labels'][:2]
    elif mode == 'duplicate':
        value['labels'].append(sample()['labels'][1])
    elif mode == 'unknown_node':
        value['labels'][0]['node_ids'] = ['nX']
    elif mode == 'invalid_label':
        value['labels'][0]['role'] = 'P'
    return value


@pytest.mark.parametrize('mode', ['partial', 'duplicate', 'unknown_node', 'invalid_label', 'corrected_partial'])
def test_invalid_inventory_keeps_valid_adverse_history_on_repeated_resume(rig, monkeypatch, mode):
    from ara.runtime.calls import ModelCalls, Rejected
    from ara.runtime.essay_audit import audit_consensus
    calls, provider, log = rig
    values = [invalid_adverse_sample(mode)]
    if mode == 'corrected_partial':
        calls.config['validation_attempts'] = 2
        values.insert(0, {'labels': []})
    responder(provider, monkeypatch, values + [sample()] * 9)
    with pytest.raises(Rejected):
        audit_consensus(calls, graph(), draft())
    resumed = ModelCalls(calls.config, provider, log, calls.cache, calls.root, calls.topic)
    for _ in range(2):
        with pytest.raises(EssayAuditFailed) as failure:
            audit_consensus(resumed, graph(), draft())
        result = failure.value.result
        assert result['extra_steps'] == [2]
        assert result['sentences'][1]['historical_flags'] == ['unsupported_claim']
        assert len(result['samples']) == 3 and all(s['faithful'] for s in result['samples'])
        assert any(h['extra_steps'] == [2] for h in result['historical_adverse'])
    changed = {**draft(), 'body': draft()['body'].replace('Q.', 'S.')}
    assert audit_consensus(resumed, graph(), changed)['faithful']


@pytest.mark.parametrize('mode', ['partial', 'duplicate', 'unknown_node'])
def test_native_resume_cannot_export_unchanged_draft_after_invalid_adverse_audit(rig, monkeypatch, mode):
    from ara.runtime.calls import ModelCalls, Rejected
    from ara.runtime.orchestration import compose
    calls, provider, log = rig
    log.record('route', graph=graph().to_dict())
    audits = 0
    def complete(kind, prompt, schema, maximum):
        nonlocal audits
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'audit_essay':
            audits += 1
            value = invalid_adverse_sample(mode) if audits == 2 else sample()
        elif kind == 'search_evidence':
            value = 'P'
        elif kind == 'verify_originality_citations':
            value = dict(items=[], originality=dict(assessment='unverified', detail='P', evidence_urls=[]))
        elif kind == 'revise_essay':
            # A favorable reroll must not substitute for a real repair.
            value = {'revisions': [dict(sentence=s['sentence'], text=s['text'])
                                   for s in data['flagged_sentences']]}
        else:
            raise AssertionError(kind)
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    with pytest.raises(Rejected):
        compose(calls, graph(), draft())
    resumed = ModelCalls(calls.config, provider, log, calls.cache, calls.root, calls.topic)
    with pytest.raises(Rejected):
        compose(resumed, graph(), draft())
    gate = json.loads([e['payload_json'] for e in log.read() if e['stage'] == 'essay_audit_consensus'][-1])
    assert gate['extra_steps'] == [2] and not gate['faithful']
    assert not any(e['stage'] == 'essay_audit_revision' for e in log.read())
    assert not (log.path.parent / 'draft.json').exists()
    assert not (log.path.parent / 'export/essay.txt').exists()


@pytest.mark.parametrize('adverse', [True, False])
@pytest.mark.parametrize('position', [1, 3])
def test_schema_retry_within_fresh_gate_retains_adverse_labels(rig, monkeypatch, adverse, position):
    from ara.runtime.essay_audit import audit_consensus
    calls, provider, log = rig
    calls.config['validation_attempts'] = 2
    invalid = invalid_adverse_sample('invalid_label') if adverse else sample()
    invalid['labels'][0]['role'] = 'P'
    seen = responder(provider, monkeypatch, [sample()] * (position - 1) + [invalid] + [sample()] * (4 - position))
    if adverse:
        with pytest.raises(EssayAuditFailed) as failure:
            audit_consensus(calls, graph(), draft())
        result = failure.value.result
        assert result['extra_steps'] == [2]
        assert result['sentences'][1]['historical_flags'] == ['unsupported_claim']
        assert failure.value.labels[0]['sentence'] == 2
    else:
        result = audit_consensus(calls, graph(), draft())
        assert result['faithful'] and not result['historical_adverse']
    assert len(seen) == 4
    assert len(result['samples']) == 3 and all(s['faithful'] for s in result['samples'])
    assert len(result['unusable_history']) == 1
    assert not list(calls.cache.path.glob('*.json'))
