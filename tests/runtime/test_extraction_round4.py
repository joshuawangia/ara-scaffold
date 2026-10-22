"""Full-corpus boundary proofs using placeholder evidence only."""
import copy
import json

import pytest
import yaml

from ara.bank import load_bank
from ara.runtime.calls import Rejected
from ara.runtime.cli import main
from ara.runtime.extraction import Paper, PageText, HEADER
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.providers import Response
from ara.types import TokenUsage
from rich_fixture import graph, batch_response
from test_extraction import rig, offline, response, ROOT
from test_extraction_rich import rich_calls


def test_full_profile_refuses_unset_caps_before_provider(rig, capsys):
    calls, _, _, manifest, fulltext, config_path = rig
    def forbidden(*a):
        pytest.fail('provider created before profile preflight')
    code = main(['extract', '--profile', 'extraction-full', '--config', str(config_path),
                 '--manifest', str(manifest), '--fulltext-dir', str(fulltext),
                 '--run-dir', str(calls.log.path.parent / 'full')], calls_factory=forbidden)
    assert code == 2
    assert 'operator must set' in capsys.readouterr().err
    config = yaml.safe_load(config_path.read_text())
    profile = config['extraction-full']
    assert profile['stages']['extraction']['model'] == 'claude-opus-5'
    assert profile['stages']['extraction']['fallbacks'] == []
    assert profile['extraction_require_inference'] is True
    assert profile['extraction_targeted_corrections'] == 3
    assert all(profile[k] is None for k in ('token_cap', 'cost_cap_usd', 'extraction_cost_cap_usd'))


@pytest.mark.parametrize('reason', ['P', '', None, ' '])
def test_empty_range_requires_disposition_and_preserves_aggregate(rig, monkeypatch, reason):
    calls, provider, papers, *_ = rig
    calls.config['extraction_require_inference'] = True
    paper = Paper('p', papers[0].record_json, 'P', (PageText(1, 'P'), PageText(2, 'Q')))
    def estimate(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        return TokenUsage(input_tokens=200001 if len(data.get('pages', [])) == 2 and 'mode' not in data else 100)
    def complete(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        value = graph(page=2)
        if data.get('mode') == 'reconcile_ranges': value['items'] = []
        elif data['pages'][0]['page'] == 1:
            value['items'] = []
            if reason is not None: value['empty_reason'] = reason
        return Response(response(value))
    monkeypatch.setattr(provider, 'estimate', estimate)
    monkeypatch.setattr(provider, 'complete', complete)
    if reason != 'P':
        with pytest.raises(Rejected): calls.extract_paper(paper)
    else:
        result = calls.extract_paper(paper).to_dict()
        assert len(result['items']) == 8
        assert result['dispositions'] == [{'pages': [1], 'reason': 'P'}]
        saved = json.loads((calls.log.path.parent / 'p.r1-1.rich.json').read_text())
        assert saved['dispositions'] == result['dispositions']


def test_zero_roots_accounted_without_formalization(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    sent = []
    def complete(kind, prompt, schema, maximum):
        sent.append(kind)
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        return Response(response(dict(roots=[], relevance='P', omissions=[
            dict(group_id=g['group_id'], reason='Q') for g in data['selection_groups']])))
    monkeypatch.setattr(provider, 'complete', complete)
    with pytest.raises(Rejected, match='empty working T'):
        prepare_commitments(calls, load_bank(ROOT / 'bank'), path.read_text(), 'P')
    assert sent == ['select_t_roots']
    event = next(json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'build_t_batch_skipped')
    assert len(event['omitted']) == 8
    assert not any(e['stage'] == 'commitments_frozen' for e in calls.log.read())


def test_closure_preflight_before_formalization(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    calls.config['working_t_token_budget'] = 1
    sent = []
    def complete(kind, prompt, schema, maximum):
        sent.append(kind)
        return Response(response(batch_response(json.loads(prompt.split('\nINPUT_JSON\n')[1]))))
    monkeypatch.setattr(provider, 'complete', complete)
    with pytest.raises(Rejected, match='working T.*preflight'):
        calls.build_t(path.read_text(), 'P')
    assert sent == ['select_t_roots']


def test_two_rich_catalogues_share_global_capacity(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    value = json.loads(path.read_text()[len(HEADER):])
    second = json.loads(json.dumps(value['papers'][0]).replace('p:', 'q:'))
    second['source_id'] = 'q'
    for item in second['items']: item['source_id'] = 'q'
    from ara.runtime.grounding import ground_outcome
    second = ground_outcome(Paper('q', '{}', 'Q', (PageText(1, 'P Q R F(x)'),)), second, calls.log)
    value['papers'].append(second)
    calls.config.update(working_t_token_budget=10000, working_t_symbol_token_budget=19000)
    allowances = []
    original = provider.estimate
    def estimate(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'build_t_batch' and len(data.get('papers', [])) > 1:
            return TokenUsage(input_tokens=70001, output_tokens=maximum)
        return original(kind, prompt, schema, maximum)
    def complete(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        if kind == 'select_t_roots': allowances.append(data['working_token_allowance'])
        result = batch_response(data)
        if kind == 'build_t_batch':
            result['new_symbols'] = []
            result['alignments'] = []
            for item in result['commitments']:
                name = item['id'].replace(':', '_')
                item['formula'] = {'op': 'atom', 'name': name}
                result['new_symbols'].append(dict(name=name, kind='atom', arity=0,
                    definition='P ' * 500, evidence_ids=[item['id']]))
        return Response(response(result))
    monkeypatch.setattr(provider, 'estimate', estimate)
    monkeypatch.setattr(provider, 'complete', complete)
    t = prepare_commitments(calls, load_bank(ROOT / 'bank'), HEADER + json.dumps(value), 'P')
    assert len(t.commitments) == 16
    assert 0 < allowances[1] < allowances[0] < 10000
    events = calls.log.read()
    merged = next(json.loads(e['payload_json']) for e in events if e['stage'] == 'build_t_merged')
    assert len(merged['symbols']) == 16
    assert merged['input_tokens'] < 10000
    assert len(json.dumps(merged['symbols'])) > 17000
    assert sum(e['stage'] == 'build_t_capacity_preflight' for e in events) == 2
    assert sum(e['stage'] == 'commitments_frozen' for e in events) == 1


def test_catalogue_growth_preflight_precedes_formalization(rig, monkeypatch):
    calls, provider, path = rich_calls(rig, monkeypatch)
    calls.config.update(working_t_symbol_growth_tokens_per_item=256, working_t_symbol_token_budget=1000)
    with pytest.raises(Rejected, match='shared symbol token allowance preflight'):
        calls.build_t(path.read_text(), 'P')
    model = [e['stage'] for e in calls.log.read() if e['label'] == 'MODEL']
    assert model.count('select_t_roots') == 1 and 'build_t_batch' not in model


def test_full_profile_reaches_native_construction(rig, tmp_path, capsys):
    calls, _, _, _, _, config_path = rig
    literature = tmp_path/'source.txt'
    literature.write_text('P')
    arguments = ['run', '--profile', 'extraction-full', '--config', str(config_path),
                 '--topic', 'P', '--literature', str(literature), '--run-dir', str(tmp_path/'build')]
    observed = []
    def factory(config, *args):
        observed.append(config)
        raise ValueError('P')
    assert main(arguments, calls_factory=factory) == 2
    assert 'operator must set' in capsys.readouterr().err and not observed
    config = yaml.safe_load(config_path.read_text())
    config['extraction-full'].update(token_cap=1000000, cost_cap_usd=100, extraction_cost_cap_usd=100)
    config_path.write_text(yaml.safe_dump(config))
    assert main(arguments, calls_factory=factory) == 2
    assert len(observed) == 1
    assert observed[0]['working_t_symbol_token_budget'] == 32000
    assert observed[0]['construction_targeted_corrections'] == 1
    assert observed[0]['stages']['extraction']['model'] == 'claude-opus-5'
