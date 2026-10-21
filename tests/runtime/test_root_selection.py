"""Compact complete selection and stage admission with placeholder evidence."""
import copy
import json

import pytest
from ara.bank import load_bank
from ara.runtime.calls import Rejected
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.providers import Response
from ara.runtime.budget import BudgetStop
from ara.types import TokenUsage
from rich_fixture import batch_response
from test_extraction import rig, offline, response, ROOT
from test_extraction_rich import rich_calls


def choose(inputs):
    root = next(i['root_id'] for p in inputs['papers'] for i in p['items'] if i['id'].endswith(':f'))
    return {'roots': [root], 'relevance': 'P', 'omissions': [
        {'group_id': g['group_id'], 'reason': 'Q'} for g in inputs['selection_groups'] if set(g['root_ids']) - {root}]}


def test_compact_selection_expands_before_closure_and_freezes(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    sent = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1]); sent.append((kind, inputs, maximum))
        if kind == 'select_t_roots':
            assert maximum == 16384
            return Response(response(choose(inputs)))
        assert len(inputs['closure']['roots']) == 1 and inputs['closure']['roots'][0].endswith(':f')
        assert len(inputs['closure']['inventory']) == 8
        return Response(response(batch_response(inputs)))
    monkeypatch.setattr(provider, 'complete', complete)
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), path.read_text(), 'P')
    assert len(result.commitments) == 8
    events = calls.log.read()
    assert sum(e['stage'] == 'commitments_frozen' for e in events) == 1
    inventory = next(json.loads(e['payload_json']) for e in events if e['stage'] == 'build_t_selection_inventory')
    assert set(inventory['root_ids'].values()) == {c.id for c in result.commitments}
    assert sum(len(g['root_ids']) for g in inventory['groups']) == 8


@pytest.mark.parametrize('bad', ['missing_group', 'unknown_group', 'duplicate_group', 'unknown_root'])
def test_bad_selection_never_freezes(rig, monkeypatch, bad):
    calls, provider, path = rich_calls(rig, monkeypatch)
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind != 'select_t_roots': return Response(response(batch_response(inputs)))
        value = choose(inputs)
        if bad == 'missing_group': value['omissions'].pop(0)
        if bad == 'unknown_group': value['omissions'][0]['group_id'] = 'unknown'
        if bad == 'duplicate_group': value['omissions'].append(value['omissions'][0])
        if bad == 'unknown_root': value['roots'] = ['unknown']
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    with pytest.raises(Rejected): prepare_commitments(calls, load_bank(ROOT/'bank'), path.read_text(), 'P')
    assert not any(e['stage'] == 'commitments_frozen' for e in calls.log.read())


def test_root_allowance_is_counted_before_dispatch_and_cache(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    original = provider.estimate
    seen = []
    def estimate(kind, prompt, schema, maximum):
        if kind == 'select_t_roots':
            seen.append(maximum)
            return TokenUsage(input_tokens=190000, output_tokens=maximum)
        return original(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'estimate', estimate)
    before = provider.calls
    with pytest.raises(BudgetStop, match='context bound'): calls.build_t(path.read_text(), 'P')
    assert seen == [16384] and provider.calls == before


def test_stage_allowance_partitions_root_cache(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    calls.build_t(path.read_text(), 'P'); before = provider.calls
    calls.build_t(path.read_text(), 'P'); assert provider.calls == before
    calls.config['select_t_roots_max_output_tokens'] = 18000
    calls.build_t(path.read_text(), 'P')
    assert provider.calls == before + 1


def test_grouped_omissions_bound_response_without_losing_items():
    from ara.runtime.construction import selection_inventory
    items = {}
    for n in range(176):
        id = f'p:r1-2:p{n:03}'
        items[id] = dict(id=id, source_id='p', kind='premise', attribution='author_claim', attributed_to='P')
    aliases, groups = selection_inventory(items)
    assert len(groups) == 1 and set(aliases.values()) == set(items)
    assert set(groups[0]['root_ids']) == set(aliases)
    compact = {'roots': ['r1'], 'relevance': 'P', 'omissions': [{'group_id': 'g1', 'reason': 'Q'}]}
    old = {'roots': [next(iter(items))], 'relevance': 'P', 'omissions': [{'evidence_ids': list(items)[1:], 'reason': 'Q'}]}
    assert len(json.dumps(compact)) < len(json.dumps(old)) / 10
    assert selection_inventory(dict(reversed(list(items.items())))) == (aliases, groups)


@pytest.mark.parametrize('stage', ['select_t_roots', 'build_t_batch'])
@pytest.mark.parametrize('patch', ['valid', 'unchanged', 'invalid'])
def test_targeted_stage_correction_preserves_inventory(rig, monkeypatch, stage, patch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    calls.config.update(construction_targeted_corrections=1, validation_attempts=3)
    counts = {}; originals = {}
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        counts[kind] = counts.get(kind, 0) + 1
        good = choose(inputs) if kind == 'select_t_roots' else batch_response(inputs)
        if kind != stage: return Response(response(good))
        if counts[kind] == 1:
            originals[kind] = copy.deepcopy(good)
            if kind == 'select_t_roots': good['omissions'].pop(0)
            else: good['commitments'][0]['formula'] = {'op':'atom', 'name':'unknown'}
            return Response(response(good))
        assert inputs['mode'] == 'targeted_correction' and inputs['candidate'] and inputs['validation_error']
        good = originals[kind]
        if kind == 'select_t_roots':
            correction = {**good, 'omissions': good['omissions'][:1]}
            if patch == 'unchanged': correction['omissions'] += good['omissions'][1:2]
            if patch == 'invalid': correction['omissions'][0]['reason'] = ' '
        else:
            correction = {'commitments':good['commitments'][:1], 'new_symbols':[], 'alignments':[]}
            if patch == 'unchanged': correction['commitments'] += good['commitments'][1:2]
            if patch == 'invalid': correction['commitments'][0]['formula'] = {'op':'atom','name':'unknown2'}
            for item in correction['commitments']: item['formula'] = json.dumps(item['formula'])
        return Response(response(correction))
    monkeypatch.setattr(provider, 'complete', complete)
    if patch == 'valid':
        result = prepare_commitments(calls, load_bank(ROOT/'bank'), path.read_text(), 'P')
        assert len(result.commitments) == 8
        assert sum(e['stage'] == 'commitments_frozen' for e in calls.log.read()) == 1
    else:
        with pytest.raises(Rejected): prepare_commitments(calls, load_bank(ROOT/'bank'), path.read_text(), 'P')
        assert not any(e['stage'] == 'commitments_frozen' for e in calls.log.read())
    assert counts[stage] == 2
    events = [e for e in calls.log.read() if e['stage']==stage and e['label']=='MODEL']
    assert len(events)==2 and all(e['cost_usd']>0 for e in events)
    assert json.loads(events[0]['payload_json'])['status']=='rejected'


def test_root_reservation_uses_own_output_allowance(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    calls.config['cost_cap_usd'] = .3  # Fits 8192 output tokens, not 16384.
    monkeypatch.setattr(provider, 'estimate', lambda kind, prompt, schema, maximum: TokenUsage(input_tokens=100, output_tokens=maximum))
    before = provider.calls
    with pytest.raises(BudgetStop): calls.build_t(path.read_text(), 'P')
    assert provider.calls == before
    assert not any(e['stage'] == 'build_t_closure' for e in calls.log.read())


def test_targeted_correction_recounts_context(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    calls.config['construction_targeted_corrections'] = 1
    original = provider.estimate
    sent = []
    def estimate(kind, prompt, schema, maximum):
        if json.loads(prompt.split('\nINPUT_JSON\n')[1]).get('mode') == 'targeted_correction':
            return TokenUsage(input_tokens=200001, output_tokens=maximum)
        return original(kind, prompt, schema, maximum)
    def complete(kind, prompt, schema, maximum):
        sent.append(kind)
        value = choose(json.loads(prompt.split('\nINPUT_JSON\n')[1])); value['omissions'].pop(0)
        return Response(response(value))
    monkeypatch.setattr(provider, 'estimate', estimate)
    monkeypatch.setattr(provider, 'complete', complete)
    with pytest.raises(BudgetStop, match='context bound'): calls.build_t(path.read_text(), 'P')
    assert sent == ['select_t_roots']
    assert not any(e['stage'] == 'commitments_frozen' for e in calls.log.read())


def test_group_omission_excludes_selected_member(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'select_t_roots':
            root = next(i['root_id'] for p in inputs['papers'] for i in p['items'] if i['id'].endswith(':p'))
            value = {'roots':[root], 'relevance':'P', 'omissions':[
                {'group_id':g['group_id'],'reason':'Q'} for g in inputs['selection_groups']]}
        else: value = batch_response(inputs)
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), path.read_text(), 'P')
    assert len(result.commitments)==1 and result.commitments[0].id.endswith(':p')
    closure = next(json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='build_t_closure')
    assert len(closure['omitted'])==7
    assert result.commitments[0].id not in {o['evidence_id'] for o in closure['omitted']}
