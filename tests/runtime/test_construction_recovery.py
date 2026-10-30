"""Bounded recovery retains only independently validated source commitments."""
import json

import pytest

from ara.bank import load_bank
from ara.runtime.calls import Rejected
from ara.runtime.construction import construct
from ara.runtime.extraction import HEADER, extract
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.providers import Response
from ara.types import TokenUsage
from rich_fixture import batch_response, graph
from test_extraction import rig, register, response, ROOT


def records(calls, stage):
    return [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == stage]


def setup(rig, monkeypatch, *, full=False):
    calls, provider, papers, *_ = rig
    value = graph()
    if not full:
        value['items'] = value['items'][:3]
    register(calls, provider, papers[0], value)
    path = extract(calls, (papers[0],))
    sent = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1]); sent.append((kind, inputs))
        return Response(response(batch_response(inputs)))
    monkeypatch.setattr(provider, 'complete', complete)
    calls.config.update(construction_targeted_corrections=1, construction_alignment_candidates=0)
    return calls, provider, path.read_text(), sent


def freeze(calls, literature):
    return prepare_commitments(calls, load_bank(ROOT/'bank'), literature, 'P')


@pytest.mark.parametrize('damage', ['definition', 'formula', 'schema', 'schema_field', 'symbol', 'page', 'stance', 'inconsistent'])
def test_partial_accepts_valid_rows_after_repairs_and_freezes_once(rig, monkeypatch, damage):
    calls, provider, literature, sent = setup(rig, monkeypatch)
    calls.config['construction_partial_acceptance'] = True
    if damage in ('page', 'stance'):
        data = json.loads(literature[len(HEADER):])
        bad = data['papers'][0]['items'][1]
        if damage == 'page': bad['page_start'] = True
        else: bad['kind'] = 'reported_view'
        from ara.runtime.grounding import ground_outcome
        data['papers'][0] = ground_outcome(rig[2][0], data['papers'][0], calls.log)
        literature = HEADER + json.dumps(data)
    complete = provider.complete
    def respond(kind, prompt, schema, maximum):
        out = complete(kind, prompt, schema, maximum)
        value = json.loads(out.text())
        if kind == 'build_t_batch':
            row = next(c for c in value['commitments'] if c['id'].endswith(':q'))
            if damage == 'definition': row['definition'] = 'According to b, Q'
            if damage == 'formula': row['formula'] = dict(op='atom', name='S')
            if damage == 'schema': row['formula'] = dict(op='not', args=[])
            if damage == 'schema_field': row['extra'] = 'P'
            if damage == 'symbol':
                next(s for s in value['new_symbols'] if s['name'] == 'Q')['definition'] = 'According to b, Q'
            if damage == 'inconsistent':
                row['formula'] = dict(op='and', args=[dict(op='atom', name='Q'), dict(op='not', args=[dict(op='atom', name='Q')])])
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', respond)
    result = freeze(calls, literature)
    assert {c.id.rsplit(':', 1)[1] for c in result.commitments} == {'p', 'r'}
    assert len([1 for k, _ in sent if k == 'build_t_batch']) == 2
    partial = records(calls, 'construction_partial_acceptance')
    assert len(partial) == 1 and len(partial[0]['dropped']) == 1
    assert partial[0]['dropped'][0]['evidence_id'].endswith(':q') and partial[0]['dropped'][0]['reason']
    assert records(calls, 'build_t_batch_accepted')[0]['status'] == 'partial'
    assert not records(calls, 'build_t_batch_skipped')
    assert len(records(calls, 'commitments_frozen')) == 1
    artifact = json.loads((calls.log.path.parent/'frozen-t.json').read_text())
    assert {s['name'] for s in artifact['symbol_catalogue']['symbols']} == {'P', 'R'}


def test_partial_dropped_support_drops_transitive_dependants(rig, monkeypatch):
    calls, provider, literature, _ = setup(rig, monkeypatch, full=True)
    calls.config['construction_partial_acceptance'] = True
    complete = provider.complete
    def respond(kind, prompt, schema, maximum):
        value = json.loads(complete(kind, prompt, schema, maximum).text())
        if kind == 'build_t_batch':
            next(c for c in value['commitments'] if c['id'].endswith(':p'))['definition'] = 'According to b, P'
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', respond)
    result = freeze(calls, literature)
    kept = {c.id.rsplit(':', 1)[1] for c in result.commitments}
    assert kept == {'q', 'd', 'qual'}
    dropped = records(calls, 'construction_partial_acceptance')[0]['dropped']
    assert any(d['evidence_id'].endswith(':f') and 'depend' in d['reason'] for d in dropped)
    assert all(not row['omitted_support_ids'] for row in records(calls, 'commitment_provenance_frozen')[0]['commitments'].values())


@pytest.mark.parametrize('failure', ['output', 'context'])
def test_failed_window_splits_once_and_uses_shared_catalogue(rig, monkeypatch, failure):
    calls, provider, literature, sent = setup(rig, monkeypatch)
    calls.config['construction_split_retry'] = True
    complete, estimate = provider.complete, provider.estimate
    def respond(kind, prompt, schema, maximum):
        value = json.loads(complete(kind, prompt, schema, maximum).text())
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if failure == 'output' and kind == 'build_t_batch' and inputs['batch_index'] == 0:
            for c in value['commitments']: c['definition'] = 'According to b, P'
        return Response(response(value))
    def count(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if failure == 'context' and kind == 'select_t_roots' and inputs.get('plan_id') and inputs['batch_index'] == 0:
            return TokenUsage(input_tokens=300000, output_tokens=maximum)
        return estimate(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'complete', respond)
    monkeypatch.setattr(provider, 'estimate', count)
    result = freeze(calls, literature)
    assert len(result.commitments) == 3
    split = records(calls, 'construction_split_retry')
    assert len(split) == 1 and split[0]['children'] == [1, 2]
    plan = records(calls, 'build_t_plan')[0]['plan']
    assert len(plan['batches']) == 3
    assert [len(i['papers'][0]['items']) for k, i in sent if k == 'select_t_roots' and i['batch_index'] != 0] == [1, 2]
    assert any(i['shared_symbols'] for k, i in sent if k == 'build_t_batch' and i['batch_index'] == 2)
    assert len(records(calls, 'commitments_frozen')) == 1


def test_failed_split_children_never_split_recursively(rig, monkeypatch):
    calls, provider, literature, sent = setup(rig, monkeypatch)
    calls.config['construction_split_retry'] = True
    complete = provider.complete
    def respond(kind, prompt, schema, maximum):
        value = json.loads(complete(kind, prompt, schema, maximum).text())
        if kind == 'build_t_batch':
            for c in value['commitments']: c['definition'] = 'According to b, P'
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', respond)
    with pytest.raises(Rejected, match='empty working T'): freeze(calls, literature)
    assert len(records(calls, 'construction_split_retry')) == 1
    assert len([1 for k, _ in sent if k == 'select_t_roots']) == 3
    assert not records(calls, 'commitments_frozen')


@pytest.mark.parametrize('text', ['P holds', 'P and Q hold', 'P states are Q', 'P maintains Q'])
def test_precise_screen_survives_freeze_and_sidecar_validation(rig, monkeypatch, text):
    from ara.runtime.commitment_provenance import load_commitment_provenance
    calls, provider, literature, _ = setup(rig, monkeypatch)
    calls.config['construction_precise_attribution'] = True
    complete = provider.complete
    def respond(kind, prompt, schema, maximum):
        value = json.loads(complete(kind, prompt, schema, maximum).text())
        if kind == 'build_t_batch':
            value['commitments'][0]['definition'] = text
            value['new_symbols'][0]['definition'] = text
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', respond)
    result = freeze(calls, literature)
    assert len(result.commitments) == 3 and text in {c.text for c in result.commitments}
    catalogue = json.loads((calls.log.path.parent/'frozen-t.json').read_text())['symbol_catalogue']
    provenance = load_commitment_provenance(calls.log.path.parent, result, catalogue)
    assert all(p['definition_screen'] == 'attribution-frames-v1' for p in provenance['commitments'].values())


@pytest.mark.parametrize('text', ['b argues that P', 'b holds that P', 'b states that P', 'According to b, P', "b's view is P"])
def test_precise_screen_keeps_explicit_attribution_hard(text):
    from ara.runtime.commitment_provenance import content_definition
    assert not content_definition(text, screen='attribution-frames-v1')


def test_disabled_flags_preserve_plan_and_legacy_screen(rig, monkeypatch):
    from ara.runtime.commitment_provenance import content_definition
    calls, _, literature, _ = setup(rig, monkeypatch)
    for flag in ('construction_partial_acceptance', 'construction_split_retry', 'construction_precise_attribution'):
        calls.config.pop(flag, None)
    before = construct(calls, literature, 'P', plan_only=True)
    calls.config.update(construction_partial_acceptance=False, construction_split_retry=False, construction_precise_attribution=False)
    assert construct(calls, literature, 'P', plan_only=True) == before
    assert not content_definition('P holds')


@pytest.mark.parametrize('flag', ['construction_partial_acceptance', 'construction_split_retry', 'construction_precise_attribution'])
def test_invalid_recovery_flags_refuse_before_planning(rig, monkeypatch, flag):
    calls, _, literature, _ = setup(rig, monkeypatch)
    calls.config[flag] = 'true'
    with pytest.raises(ValueError, match='boolean'): construct(calls, literature, 'P', plan_only=True)
    assert not records(calls, 'build_t_plan')


def test_successful_parent_leaves_children_inactive_and_receipts_resumable(rig, monkeypatch):
    from ara.runtime.alignment_resume import load_alignment_resume
    calls, _, literature, sent = setup(rig, monkeypatch)
    calls.config.update(construction_split_retry=True, construction_precise_attribution=True)
    calls.log.record('run_started', config=calls.config, topic=calls.topic, literature=literature,
                     audience='P', bank_version=load_bank(ROOT/'bank').bank_version)
    result = calls.build_t(literature, 'P')
    assert len(result.commitments) == 3 and len(sent) == 2
    assert not records(calls, 'construction_split_retry')
    skipped = records(calls, 'build_t_batch_skipped')
    assert len(skipped) == 2 and all(r['status'] == 'inactive_retry' and r['omitted'] == [] for r in skipped)
    restored = load_alignment_resume(calls.log, load_bank(ROOT/'bank'))
    assert restored['commitments'] == result and restored['completed_windows'] == 3


@pytest.mark.parametrize('terminal', [1, 2])
def test_split_resume_retains_verified_child_before_terminal_refusal(rig, monkeypatch, tmp_path, terminal):
    import httpx2 as httpx
    from anthropic import APIStatusError
    from ara.runtime import providers
    from ara.runtime.budget import BudgetStop
    from ara.runtime.cache import Cache
    from ara.runtime.calls import ModelCalls
    calls, provider, literature, _ = setup(rig, monkeypatch)
    calls.config['construction_split_retry'] = True
    complete = provider.complete
    def respond(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if inputs['batch_index'] == terminal and kind == 'select_t_roots':
            raise APIStatusError('P', response=httpx.Response(400, request=httpx.Request('POST', 'https://example.invalid'),
                headers={'request-id': 'req_P'}), body={'error': {'type': 'invalid_request_error', 'message': 'P'}})
        value = json.loads(complete(kind, prompt, schema, maximum).text())
        if inputs['batch_index'] == 0 and kind == 'build_t_batch':
            for row in value['commitments']: row['definition'] = 'According to b, P'
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', respond)
    with monkeypatch.context() as old:
        old.setattr(providers, 'terminal_request_refusal', lambda exc: False)
        with pytest.raises(BudgetStop): freeze(calls, literature)
    assert not records(calls, 'commitments_frozen')
    resumed = ModelCalls({**calls.config, 'unknown_usage_policy': 'count-at-reservation'}, provider,
                         calls.log, Cache(tmp_path/'resume-cache'), ROOT, calls.topic)
    resumed.construction_resume = True
    result = freeze(resumed, literature)
    assert {c.id.rsplit(':', 1)[1] for c in result.commitments} == ({'p'} if terminal == 2 else {'q', 'r'})
    assert len(records(calls, 'construction_split_retry')) == 1
    assert len(records(calls, 'commitments_frozen')) == 1


@pytest.mark.parametrize('damage', ['unknown_binding', 'conflict', 'structure'])
def test_partial_cannot_promote_bad_binding_conflict_or_flat_inference(rig, monkeypatch, damage):
    calls, provider, literature, _ = setup(rig, monkeypatch, full=damage == 'structure')
    calls.config['construction_partial_acceptance'] = True
    complete = provider.complete
    def respond(kind, prompt, schema, maximum):
        value = json.loads(complete(kind, prompt, schema, maximum).text())
        if kind == 'build_t_batch':
            if damage == 'unknown_binding':
                next(s for s in value['new_symbols'] if s['name'] == 'Q')['evidence_ids'].append('missing')
            elif damage == 'conflict':
                next(c for c in value['commitments'] if c['id'].endswith(':q'))['formula'] = dict(op='not', args=[dict(op='atom', name='P')])
            else:
                for c in value['commitments']:
                    if c['id'].endswith((':i', ':j')): c['formula'] = dict(op='atom', name='F')
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', respond)
    result = freeze(calls, literature)
    ids = {c.id.rsplit(':', 1)[1] for c in result.commitments}
    assert ids == ({'p', 'q', 'd', 'qual'} if damage == 'structure' else {'p', 'r'})
    assert records(calls, 'construction_partial_acceptance')


def test_precise_sidecar_policy_cannot_be_removed_or_forged(rig, monkeypatch):
    from copy import deepcopy
    from ara.runtime.cache import canonical, digest
    from ara.runtime.commitment_provenance import validate_commitment_provenance
    calls, provider, literature, _ = setup(rig, monkeypatch)
    calls.config['construction_precise_attribution'] = True
    complete = provider.complete
    def respond(kind, prompt, schema, maximum):
        value = json.loads(complete(kind, prompt, schema, maximum).text())
        if kind == 'build_t_batch': value['commitments'][0]['definition'] = 'P holds'
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', respond)
    result = freeze(calls, literature)
    source = records(calls, 'commitment_provenance_frozen')[0]
    catalogue = json.loads((calls.log.path.parent/'frozen-t.json').read_text())['symbol_catalogue']
    assert source['schema_version'] == 'commitment-provenance-v3'
    for damage in ('remove', 'unknown', 'legacy'):
        data = deepcopy(source)
        if damage == 'legacy': data['schema_version'] = 'commitment-provenance-v2'
        else:
            for row in data['commitments'].values():
                if damage == 'remove': row.pop('definition_screen')
                else: row['definition_screen'] = 'unknown'
        data['sha256'] = digest(canonical({k: v for k, v in data.items() if k != 'sha256'}))
        with pytest.raises(ValueError): validate_commitment_provenance(data, result, catalogue)


@pytest.mark.parametrize('drop_binding', [False, True])
def test_partial_symbol_binding_uses_valid_later_row_without_inventing_evidence(rig, monkeypatch, drop_binding):
    calls, provider, literature, _ = setup(rig, monkeypatch)
    calls.config['construction_partial_acceptance'] = True
    complete = provider.complete
    def respond(kind, prompt, schema, maximum):
        value = json.loads(complete(kind, prompt, schema, maximum).text())
        if kind == 'build_t_batch':
            p, q, r = value['commitments']
            p['formula'] = r['formula'] = dict(op='atom', name='P')
            if drop_binding: r['definition'] = 'According to b, P'
            else: q['definition'] = 'According to b, Q'
            value['new_symbols'] = [dict(name='P', kind='atom', arity=0, definition='P', evidence_ids=[r['id']]),
                                    dict(name='Q', kind='atom', arity=0, definition='Q', evidence_ids=[q['id']])]
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', respond)
    result = freeze(calls, literature)
    assert {c.id.rsplit(':', 1)[1] for c in result.commitments} == ({'q'} if drop_binding else {'p', 'r'})
    if drop_binding:
        assert any(d['evidence_id'].endswith(':p') and 'symbol evidence' in d['reason']
                   for d in records(calls, 'construction_partial_acceptance')[0]['dropped'])


def test_split_children_are_counted_before_selection(rig, monkeypatch):
    calls, provider, literature, sent = setup(rig, monkeypatch)
    calls.config['construction_split_retry'] = True
    complete, estimate = provider.complete, provider.estimate
    def respond(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        value = json.loads(complete(kind, prompt, schema, maximum).text())
        if kind == 'build_t_batch' and inputs['batch_index'] == 0:
            for c in value['commitments']: c['definition'] = 'According to b, P'
        return Response(response(value))
    def count(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'select_t_roots' and sum(len(p['items']) for p in inputs['papers']) == 1:
            return TokenUsage(input_tokens=70001, output_tokens=maximum)
        return estimate(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'complete', respond)
    monkeypatch.setattr(provider, 'estimate', count)
    result = freeze(calls, literature)
    assert {c.id.rsplit(':', 1)[1] for c in result.commitments} == {'q', 'r'}
    assert not any(i['batch_index'] == 1 for _, i in sent)
    assert any(r['index'] == 1 and 'input bound' in r['reason'] for r in records(calls, 'build_t_batch_skipped'))


def test_global_exhaustion_never_activates_split(rig, monkeypatch):
    calls, _, literature, sent = setup(rig, monkeypatch)
    calls.config.update(construction_split_retry=True, working_t_token_budget=1)
    with pytest.raises(Rejected, match='empty working T'): freeze(calls, literature)
    assert not sent and not records(calls, 'construction_split_retry')
    assert [r['status'] for r in records(calls, 'build_t_batch_skipped')] == ['skipped', 'inactive_retry', 'inactive_retry']


def test_unknown_consistency_never_accepts_partial(rig, monkeypatch):
    from ara.runtime import symbol_alignment
    calls, _, literature, _ = setup(rig, monkeypatch)
    calls.config['construction_partial_acceptance'] = True
    monkeypatch.setattr(symbol_alignment, '_consistent', lambda _: False)
    with pytest.raises(Rejected, match='empty working T'): freeze(calls, literature)
    assert not records(calls, 'construction_partial_acceptance')
    assert not records(calls, 'commitments_frozen')


def test_recovery_flags_cannot_change_in_a_stage(rig, monkeypatch):
    calls, _, literature, _ = setup(rig, monkeypatch)
    calls.config['stages'] = {'build_t_batch': {'construction_partial_acceptance': True}}
    with pytest.raises(ValueError, match='run-level only'): construct(calls, literature, 'P', plan_only=True)
    assert not records(calls, 'build_t_plan')


def test_recovery_methodology_and_precise_fork_preserve_receipts(rig, monkeypatch, tmp_path):
    from ara.runtime.export import methodology
    from ara.runtime.freeze_fork import fork_from_freeze
    calls, provider, literature, sent = setup(rig, monkeypatch)
    calls.config.update(construction_partial_acceptance=True, construction_split_retry=True,
                        construction_precise_attribution=True)
    calls.log.record('run_started', config=calls.config, topic=calls.topic, literature=literature,
                     audience='P', bank_version=load_bank(ROOT/'bank').bank_version)
    complete = provider.complete
    def respond(kind, prompt, schema, maximum):
        value = json.loads(complete(kind, prompt, schema, maximum).text())
        if kind == 'build_t_batch':
            value['commitments'][0]['definition'] = 'P holds'
            value['commitments'][1]['definition'] = 'According to b, Q'
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', respond)
    result = freeze(calls, literature)
    assert len(result.commitments) == 2 and not records(calls, 'construction_split_retry')
    assert len([1 for k, _ in sent if k == 'select_t_roots']) == 1
    summary = json.loads(methodology(calls.log.path).split('```json\n')[1].split('\n```')[0])
    assert summary['construction']['partial_acceptances'] == records(calls, 'construction_partial_acceptance')
    assert summary['construction']['split_retries'] == []
    dst = tmp_path/'fork'
    _, _, frozen = fork_from_freeze(calls.log.path.parent, dst, load_bank(ROOT/'bank'))
    assert frozen == result
    assert (dst/'commitment-provenance.json').read_bytes() == (calls.log.path.parent/'commitment-provenance.json').read_bytes()


def test_recovery_does_not_bypass_response_complexity(rig, monkeypatch):
    calls, provider, literature, _ = setup(rig, monkeypatch)
    calls.config.update(construction_partial_acceptance=True, local_validation_max_nodes=1000)
    complete = provider.complete
    def respond(kind, prompt, schema, maximum):
        value = json.loads(complete(kind, prompt, schema, maximum).text())
        if kind == 'build_t_batch': value['alignments'] = [dict(name='S'+str(i), reason='P') for i in range(500)]
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', respond)
    with pytest.raises(Rejected, match='complexity refused'): freeze(calls, literature)
    assert not records(calls, 'commitments_frozen')
