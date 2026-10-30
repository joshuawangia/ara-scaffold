"""Operator anchors stay inside native construction and counted admission."""
import copy
import json

import pytest

from ara.bank import load_bank
from ara.runtime.calls import Rejected
from ara.runtime.construction import construct
from ara.runtime.extraction import HEADER, Paper, PageText
from ara.runtime.grounding import ground_outcome
from ara.runtime.logging import EventLog
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.planning import plan_construction
from ara.runtime.providers import Response
from rich_fixture import batch_response
from test_extraction import rig, response, ROOT
from test_extraction_rich import rich_calls


def records(calls, stage):
    return [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == stage]


def select(inputs, ids):
    roots = [i['root_id'] for p in inputs['papers'] for i in p['items'] if i['id'] in ids]
    return dict(roots=roots, relevance='P', omissions=[dict(group_id=g['group_id'], reason='Q')
        for g in inputs['selection_groups'] if set(g['root_ids']) - set(roots)])


def test_anchor_window_closes_full_graph_before_one_freeze(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    original = path.read_bytes()
    evidence = json.loads(path.read_text()[len(HEADER):])['papers'][0]['items']
    root = next(i['id'] for i in evidence if i['id'].endswith(':f'))
    calls.config['construction_gap_anchors'] = [dict(gap_id='P', source_id='p', root_ids=[root])]
    sent = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1]); sent.append((kind, inputs))
        value = select(inputs, {root} if inputs.get('gap_anchor') else set()) if kind == 'select_t_roots' else batch_response(inputs)
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), path.read_text(), 'P')
    assert {c.id for c in result.commitments} == {i['id'] for i in evidence}
    assert path.read_bytes() == original
    plan = records(calls, 'build_t_plan')[0]['plan']
    assert len(plan['batches']) == 2 and plan['batches'][0]['gap_anchor']['gap_id'] == 'P'
    assert 'gap_anchor' not in plan['batches'][1]
    selected = next(i for k, i in sent if k == 'select_t_roots')
    assert selected['gap_anchor']['required_root_ids'] == ['r1']
    formal = next(i for k, i in sent if k == 'build_t_batch')
    assert set(formal['closure']['full_inventory']) == {i['id'] for i in evidence}
    assert formal['closure']['support_omitted'] == {}
    assert len(records(calls, 'construction_gap_anchor_window')) == 1
    assert len(records(calls, 'commitments_frozen')) == 1


@pytest.mark.parametrize('anchor', [None, {}, [dict(gap_id='P', source_id='p')],
    [dict(gap_id='P', source_id='missing', root_ids=['P'])],
    [dict(gap_id='P', source_id='p', root_ids=['missing'])],
    [dict(gap_id='P', source_id='p', page_ranges=[[2, 1]])],
    [dict(gap_id='P', source_id='p', page_ranges=[[True, 1]])],
    [dict(gap_id='P', source_id='p', page_ranges=[[99, 100]])],
    [dict(gap_id='P', source_id='p', page_ranges=[[1, 1]], formula='P')]])
def test_invalid_anchors_refuse_before_construction_count(rig, monkeypatch, anchor):
    calls, provider, path = rich_calls(rig, monkeypatch)
    calls.config['construction_gap_anchors'] = anchor
    before = len(records(calls, 'context_plan'))
    with pytest.raises((ValueError, Rejected), match='anchor'):
        construct(calls, path.read_text(), 'P', plan_only=True)
    assert len(records(calls, 'context_plan')) == before
    assert not records(calls, 'build_t_plan')


def test_overlapping_page_anchors_keep_one_final_omission_per_item(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    calls.config['construction_gap_anchors'] = [dict(gap_id=g, source_id='p', page_ranges=[[1, 1]]) for g in ('P', 'Q')]
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        value = select(inputs, {i['id'] for p in inputs['papers'] for i in p['items'] if i['id'].endswith(':p')}) if kind == 'select_t_roots' else batch_response(inputs)
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), path.read_text(), 'P')
    assert len(result.commitments) == 1
    assert len(records(calls, 'construction_gap_anchor_window')) == 2
    omitted = records(calls, 'build_t_evidence_accounted')[0]['omitted']
    assert len(omitted) == len({o['evidence_id'] for o in omitted}) == 7


@pytest.mark.parametrize('damage', ['root', 'symbol'])
def test_anchor_cannot_bypass_selection_or_formalization(rig, monkeypatch, damage):
    calls, provider, path = rich_calls(rig, monkeypatch)
    root = json.loads(path.read_text()[len(HEADER):])['papers'][0]['items'][0]['id']
    calls.config.update(construction_gap_anchors=[dict(gap_id='P', source_id='p', root_ids=[root])],
                        construction_targeted_corrections=0)
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'select_t_roots':
            value = select(inputs, {root} if inputs.get('gap_anchor') and damage == 'symbol' else set())
        else:
            value = batch_response(inputs); value['new_symbols'] = []
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    with pytest.raises(Rejected, match='empty working T'):
        prepare_commitments(calls, load_bank(ROOT/'bank'), path.read_text(), 'P')
    skipped = records(calls, 'build_t_batch_skipped')
    assert any(('required anchor root' if damage == 'root' else 'undeclared formula symbol') in s.get('reason', '') for s in skipped)
    assert not records(calls, 'commitments_frozen')


def test_anchor_stance_and_source_text_survive_native_freeze(rig, monkeypatch):
    from test_content_provenance import setup, freeze
    calls, path, _ = setup(rig, monkeypatch)
    calls.config['construction_gap_anchors'] = [dict(gap_id='P', source_id='p', page_ranges=[[1, 1]])]
    result = freeze(calls, path)
    rows = records(calls, 'commitment_provenance_frozen')[0]['commitments']
    assert {r['stance'] for r in rows.values()} == {'endorsed', 'reported', 'attacked'}
    assert len(result.commitments) == 3 and len(records(calls, 'construction_gap_anchor_window')) == 1


@pytest.mark.parametrize('window,bound,batch', [(272000, 239232, 139348), (600000, 567232, 340339)])
def test_context_limits_plan_from_effective_run_window_without_generation(rig, monkeypatch, tmp_path, window, bound, batch):
    calls, _, path = rich_calls(rig, monkeypatch)
    config = {**calls.config, 'provider': 'codex_cli', 'model': 'gpt-6-luna', 'model_context_window': window,
              'construction_context_limits': dict(build_t_batch_input_tokens=.6, working_t_token_budget=.65,
                                                  working_t_symbol_token_budget=.15)}
    report = plan_construction(config, EventLog(tmp_path/'plan/events.jsonl'), path.read_text(), ROOT, 'P', '', 'local')
    assert report['limits']['context'] == bound
    assert report['limits']['working'] == int(bound * .65)
    assert report['limits']['symbols'] == int(bound * .15)
    # The smaller run still reserves 64000 output plus 35884 catalogue tokens.
    assert report['limits']['batch'] == batch
    assert report['plan']['context_limits']['origin'] == 'operator_run_config'
    assert report['generation_calls'] == 0 and config['working_t_token_budget'] == 100000


@pytest.mark.parametrize('limits', [None, [], {'unknown': .5}, {'working_t_token_budget': True},
    {'working_t_token_budget': 0}, {'working_t_token_budget': 1.1}, {'working_t_token_budget': float('nan')}])
def test_invalid_context_limits_refuse_before_construction(rig, monkeypatch, limits):
    calls, _, path = rich_calls(rig, monkeypatch)
    calls.config['construction_context_limits'] = limits
    with pytest.raises((ValueError, Rejected), match='construction context'):
        construct(calls, path.read_text(), '', plan_only=True)
    assert not records(calls, 'build_t_plan')


@pytest.mark.parametrize('raised', [False, True])
def test_window_derived_limits_admit_previously_oversized_source_without_truncation(rig, monkeypatch, raised):
    calls, provider, path = rich_calls(rig, monkeypatch)
    data = json.loads(path.read_text()[len(HEADER):]); paper = data['papers'][0]
    paper['items'] = [copy.deepcopy(paper['items'][0])]
    paper['items'][0]['text'] = 'P ' * 40000
    data['papers'][0] = ground_outcome(Paper('p', '{}', 'P', (PageText(1, 'P P P'),)), paper, calls.log)
    calls.config.update(model_context_token_bound=400000, token_cap=10000000)
    if raised:
        calls.config['construction_context_limits'] = dict(build_t_batch_input_tokens=.6,
            working_t_token_budget=.65, working_t_symbol_token_budget=.15)
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        value = batch_response(inputs)
        if kind == 'build_t_batch':
            for c in value['commitments']: c['definition'] = 'P'
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    literature = HEADER + json.dumps(data)
    if not raised:
        with pytest.raises(Rejected, match='empty working T'):
            prepare_commitments(calls, load_bank(ROOT/'bank'), literature, 'P')
        assert records(calls, 'build_t_batch_skipped')
    else:
        result = prepare_commitments(calls, load_bank(ROOT/'bank'), literature, 'P')
        assert len(result.commitments) == 1
        row = records(calls, 'commitment_provenance_frozen')[0]['commitments'][result.commitments[0].id]
        assert row['source_text'] == 'P ' * 40000
        assert records(calls, 'operator_construction_limits')[0]['effective']['build_t_batch_input_tokens'] == 240000
        assert len(records(calls, 'commitments_frozen')) == 1


def test_anchor_plan_cli_discloses_limits_without_generation(rig, monkeypatch, tmp_path):
    import yaml
    from ara.runtime.cli import main
    calls, _, path = rich_calls(rig, monkeypatch)
    config = {**calls.config, 'provider': 'codex_cli', 'model': 'gpt-6-luna', 'model_context_window': 600000,
        'construction_gap_anchors': [dict(gap_id='P', source_id='p', page_ranges=[[1, 1]])],
        'construction_context_limits': dict(build_t_batch_input_tokens=.6, working_t_token_budget=.65,
                                            working_t_symbol_token_budget=.15)}
    config_path = tmp_path/'anchors.yaml'; config_path.write_text(yaml.safe_dump(config))
    output = tmp_path/'cli-plan'
    assert main(['plan-construction', '--config', str(config_path), '--literature', str(path), '--topic', 'P',
                 '--run-dir', str(output), '--token-counter', 'local']) == 0
    report = json.loads((output/'construction-plan.json').read_text())
    assert report['limits'] == dict(batch=340339, context=567232, working=368700, symbols=85084)
    assert report['plan']['batches'][0]['gap_anchor']['page_ranges'] == [[1, 1]]
    assert len(report['plan']['batches']) == 2 and report['generation_calls'] == 0
    assert not any(e['label'] == 'MODEL' for e in EventLog(output/'events.jsonl').read())


def test_disabled_options_preserve_plan_identity_and_anchor_change_partitions_it(rig, monkeypatch):
    from ara.runtime.cache import canonical, digest
    calls, _, path = rich_calls(rig, monkeypatch)
    first = construct(calls, path.read_text(), 'P', plan_only=True)
    calls.config.update(construction_context_limits={}, construction_gap_anchors=[])
    second = construct(calls, path.read_text(), 'P', plan_only=True)
    assert first == second
    assert 'context_limits' not in first and 'gap_anchors' not in first
    calls.config['construction_gap_anchors'] = [dict(gap_id='P', source_id='p', page_ranges=[[1, 1]])]
    third = construct(calls, path.read_text(), 'P', plan_only=True)
    assert digest(canonical(third)) != digest(canonical(first))


def test_anchor_cannot_restore_quarantined_evidence(rig, monkeypatch):
    calls, _, path = rich_calls(rig, monkeypatch)
    data = json.loads(path.read_text()[len(HEADER):]); paper = data['papers'][0]
    root = paper['items'][0]['id']
    paper['items'][0]['text'] = 'dummy P P P'
    data['papers'][0] = ground_outcome(Paper('p', '{}', 'P', (PageText(1, 'P Q R F(x)'),)), paper, calls.log)
    calls.config['construction_gap_anchors'] = [dict(gap_id='P', source_id='p', root_ids=[root])]
    with pytest.raises(ValueError, match='anchor roots.*grounded'):
        construct(calls, HEADER + json.dumps(data), 'P', plan_only=True)
    assert not records(calls, 'build_t_plan')


def test_anchor_and_limits_are_disclosed_in_methodology(rig, monkeypatch):
    from ara.runtime.export import methodology
    calls, _, path = rich_calls(rig, monkeypatch)
    calls.config.update(construction_gap_anchors=[dict(gap_id='P', source_id='p', page_ranges=[[1, 1]])],
                        construction_context_limits={'working_t_token_budget': .5})
    prepare_commitments(calls, load_bank(ROOT/'bank'), path.read_text(), 'P')
    summary = json.loads(methodology(calls.log.path).split('```json\n')[1].split('\n```')[0])
    assert summary['construction']['gap_anchor_windows'] == records(calls, 'construction_gap_anchor_window')
    assert summary['construction']['context_limits'] == records(calls, 'operator_construction_limits')
    assert len(summary['construction']['gap_anchor_windows']) == len(summary['construction']['context_limits']) == 1


def test_extra_anchor_windows_are_counted_split_and_reuse_exact_ids(rig, monkeypatch):
    from test_construction_shares import windows
    calls, _, literature, sent = windows(rig, monkeypatch)
    ids = [i['id'] for i in json.loads(literature[len(HEADER):])['papers'][0]['items']]
    calls.config['construction_gap_anchors'] = [dict(gap_id='P', source_id='p', root_ids=ids)]
    result = prepare_commitments(calls, load_bank(ROOT/'bank'), literature, 'P')
    plan = records(calls, 'build_t_plan')[0]['plan']
    assert len(plan['batches']) == 6
    assert all(b['input_tokens'] <= 70000 for b in plan['batches'])
    selections = [i for kind, i in sent if kind == 'select_t_roots']
    assert len(selections) == 6
    assert all(i['gap_anchor']['required_root_ids'] == ['r1'] for i in selections[:3])
    assert all('gap_anchor' not in i for i in selections[3:])
    assert {c.id for c in result.commitments} == set(ids)
    assert sum(kind == 'build_t_batch' for kind, _ in sent) == 3


def test_context_derived_construction_cannot_overrun_smaller_stage_window(rig, monkeypatch):
    from ara.runtime.providers import MockProvider
    calls, _, path = rich_calls(rig, monkeypatch)
    data = json.loads(path.read_text()[len(HEADER):]); paper = data['papers'][0]
    paper['items'] = [copy.deepcopy(paper['items'][0])]
    paper['items'][0]['text'] = 'P ' * 125000
    data['papers'][0] = ground_outcome(Paper('p', '{}', 'P', (PageText(1, 'P P P'),)), paper, calls.log)
    calls.config.update(provider='codex_cli', model='gpt-6-luna', model_context_window=600000,
        construction_context_limits=dict(build_t_batch_input_tokens=.6, working_t_token_budget=.65,
                                         working_t_symbol_token_budget=.15),
        stages={'select_t_roots': {'model_context_window': 272000}})
    # Offline counting backend; isolated wire/canary behavior is tested in test_codex_cli.
    from ara.runtime.budget import Budget
    calls.budget = Budget(calls.config, calls.log)
    calls.provider_factory = lambda settings: MockProvider({})
    with pytest.raises(Rejected, match='empty working T'):
        prepare_commitments(calls, load_bank(ROOT/'bank'), HEADER + json.dumps(data), 'P')
    admissions = [r for r in records(calls, 'context_admission') if r['kind'] == 'select_t_roots']
    assert admissions and admissions[-1]['limit'] == 239232 and admissions[-1]['decision'] == 'refused'
    assert records(calls, 'build_t_plan')[0]['plan']['budget']['batch_input_bound'] == 340339
    assert calls._stage_providers and all(p.calls == 0 for p in calls._stage_providers.values())
    assert not records(calls, 'commitments_frozen')
