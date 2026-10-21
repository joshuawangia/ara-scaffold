"""Round-three recovery boundaries, with placeholder graphs only."""
import copy
import json
from decimal import Decimal
from types import SimpleNamespace

import pytest

from test_extraction import rig, offline, response, accounting, ROOT
from rich_fixture import graph
from ara.runtime.providers import Response, AnthropicProvider
from ara.runtime.calls import Rejected
from ara.runtime.extraction import Paper, PageText, extract
from ara.types import TokenUsage


def test_directional_closure_shared_premise_and_qualifier():
    from ara.runtime.construction import prerequisite_closure
    value = graph()['items']
    # P -> Q and P -> R share a qualifier. Choosing Q must not select R.
    items = {i['id']: i for i in value if i['id'] in ('p', 'q', 'r', 'i', 'j', 'qual')}
    items['i'].update(premise_ids=['p'], conclusion_id='q', qualification_ids=['qual'])
    items['j'].update(premise_ids=['p'], conclusion_id='r', qualification_ids=['qual'])
    items['qual']['applies_to'] = ['q', 'r']
    assert prerequisite_closure(items, ['q']) == {'p', 'q', 'i', 'qual'}
    assert prerequisite_closure(items, ['p']) == {'p'}
    assert prerequisite_closure(items, ['i']) == {'p', 'q', 'i', 'qual'}
    assert prerequisite_closure(items, ['qual']) == {'qual'}
    with pytest.raises(Rejected, match='root'):
        prerequisite_closure(items, ['unknown'])


@pytest.mark.parametrize('resolve', [False, True, 'unknown'])
def test_unresolved_obligations_require_evidence(rig, monkeypatch, resolve):
    calls, provider, papers, *_ = rig
    paper = Paper('p', papers[0].record_json, 'P', (PageText(1, 'P'), PageText(2, 'Q')))
    seen = []
    def estimate(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        large = data.get('mode') != 'reconcile_ranges' and len(data.get('pages', [])) > 1
        return TokenUsage(input_tokens=200001 if large else 100, output_tokens=maximum)
    def complete(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1]); seen.append(data)
        value = graph()
        value['items'] = []
        if data.get('mode') != 'reconcile_ranges':
            page = data['pages'][0]['page']
            value['items'] = [graph(page=page)['items'][0 if page == 1 else 1]]
            if page == 1:
                value.update(coverage_complete=False, unresolved_references=['Q'])
        elif resolve:
            assert [p['text'] for p in data['pages']] == ['P', 'Q']
            obligation = data['obligations'][0]
            assert obligation['range'] == 'r1-1' and obligation['pages'] == [1]
            # Add a genuine cross-range link and qualifier with exact old endpoints.
            i = graph()['items'][6]
            i.update(id='i', premise_ids=['p:r1-1:p'], conclusion_id='p:r2-2:q', qualification_ids=['qual'])
            qual = graph()['items'][5]
            qual.update(id='qual', applies_to=['i'])
            value['items'] = [i, qual]
            value['resolutions'] = [{'obligation_id': obligation['id'], 'evidence_ids': ['unknown'] if resolve == 'unknown' else ['p:r2-2:q', 'i', 'qual']}]
        return Response(response(value))
    monkeypatch.setattr(provider, 'estimate', estimate)
    monkeypatch.setattr(provider, 'complete', complete)
    if not resolve or resolve == 'unknown':
        with pytest.raises(Rejected, match='obligation'):
            extract(calls, (paper,))
        assert not (calls.log.path.parent / 'literature.extracted.txt').exists()
    else:
        result = calls.extract_paper(paper)
        data = result.to_dict()
        assert len(data['items']) == 4
        assert len(data['obligations']) == len(data['resolutions']) == 1
        assert set(data['resolutions'][0]['evidence_ids']) == {'p:r2-2:q', 'p:joined:i', 'p:joined:qual'}
        assert any(e['stage'] == 'extraction_obligations_resolved' for e in calls.log.read())


def test_measured_response_survives_followup_count_failure(rig, monkeypatch):
    calls, provider, *_ = rig
    raw = response({'formula': {'op': 'atom', 'name': 'P'}})
    monkeypatch.setattr(provider, 'complete', lambda *a: Response(raw))
    def check(data):
        # The known response is already durable before any fallible validation.
        received = [e for e in calls.log.read() if e['stage'] == 'response_received']
        assert len(received) == 1
        raise OSError('P')
    with pytest.raises(OSError):
        calls.call('formalise', {'proposition': 'P'}, check)
    model = [e for e in calls.log.read() if e['label'] == 'MODEL']
    assert len(model) == 1 and json.loads(model[0]['response']) == raw
    assert model[0]['usage']['input_tokens'] == 100 and model[0]['usage']['output_tokens'] == 50
    assert model[0]['cost_usd'] == .00175
    assert json.loads(model[0]['payload_json'])['accounting'] == 'actual'
    assert json.loads(model[0]['payload_json'])['status'] == 'rejected'
    assert calls.budget.used_cost == Decimal('0.00175')
    assert not list(calls.cache.path.glob('*.json'))
    assert not any(e['stage'] == 'commitments_frozen' for e in calls.log.read())


def test_stage_model_wire_cache_and_receipts(rig):
    calls, _, papers, *_ = rig
    from ara.runtime.calls import ModelCalls
    from ara.runtime.cache import Cache
    sent = []
    class Stream:
        def __init__(self, request): self.request = request
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def get_final_message(self):
            raw = response(graph())
            raw['model'] = self.request['model']
            return SimpleNamespace(to_dict=lambda mode: raw)
    def stream(**request):
        sent.append(request)
        return Stream(request)
    client = SimpleNamespace(messages=SimpleNamespace(count_tokens=lambda **kw: SimpleNamespace(input_tokens=100)),
                             beta=SimpleNamespace(messages=SimpleNamespace(stream=stream)))
    calls.config['cost_cap_usd'] = .321  # Fits a Sonnet reservation, not an Opus reservation.
    provider = AnthropicProvider(calls.config, client)
    calls = ModelCalls(calls.config, provider, calls.log, calls.cache, ROOT, 'P')
    calls.extract_paper(papers[0])
    assert sent[-1]['model'] == 'claude-sonnet-5-5' and 'fallbacks' not in sent[-1]
    assert provider.request('build_t', 'P', None, 100)['model'] == 'claude-opus-5'
    calls.extract_paper(papers[0])
    assert len(sent) == 1
    calls.config['cost_cap_usd'] = 2
    calls.config['stages']['extraction']['model'] = 'claude-opus-5'
    calls.extract_paper(papers[0])
    assert len(sent) == 2
    model = [e for e in calls.log.read() if e['label'] == 'MODEL']
    assert model[0]['model_id'] == model[0]['model_version'] == 'claude-sonnet-5-5'
    assert model[0]['cost_usd'] == .0007
    report = accounting(calls.log)
    assert 'claude-sonnet-5-5' in report['extraction']['models']


def test_accounting_separates_reservations(rig, monkeypatch):
    calls, provider, *_ = rig
    from ara.runtime.budget import BudgetStop
    monkeypatch.setattr(provider, 'complete', lambda *a: (_ for _ in ()).throw(OSError('P')))
    with pytest.raises(BudgetStop): calls.call('formalise', {'proposition': 'P'})
    report = accounting(calls.log)
    assert report['measured_usage']['cost_usd'] == 0
    assert report['unknown_usage_reservations']['cost_usd'] > 0
    assert report['budget_accounted']['cost_usd'] == report['unknown_usage_reservations']['cost_usd']
    assert report['local_totals']['measured_usage']['tokens']['input_tokens'] == 0


@pytest.mark.parametrize('corrupt', ['closure', 'attribution', 'citation'])
def test_fixed_inventory_boundary_has_no_freeze(rig, monkeypatch, corrupt):
    from dataclasses import replace
    import ara.runtime.construction as construction
    from ara.runtime.orchestration import prepare_commitments
    from ara.bank import load_bank
    from ara.types import CommitmentSet
    from test_extraction_rich import rich_calls
    from rich_fixture import batch_response
    calls, provider, path = rich_calls(rig, monkeypatch)
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        value = batch_response(inputs)
        if kind == 'select_t_roots':
            root = next(i['root_id'] for p in inputs['papers'] for i in p['items'] if i['id'].endswith(':f'))
            value['omissions'] = [dict(group_id=g['group_id'], reason='Q') for g in inputs['selection_groups'] if set(g['root_ids']) - {root}]
            value['roots'] = [root]
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    if corrupt == 'closure':
        monkeypatch.setattr(construction, 'prerequisite_closure', lambda items, roots: set(roots))
        message = 'drops premise/link/qualification'
    else:
        original = CommitmentSet.from_dict
        def corrupted(data):
            t = original(data)
            field = {'text': 'Q'} if corrupt == 'attribution' else {'citation': 'q:pdf:1'}
            return CommitmentSet((replace(t.commitments[0], **field), *t.commitments[1:]))
        monkeypatch.setattr(CommitmentSet, 'from_dict', corrupted)
        message = 'changed evidence or attribution' if corrupt == 'attribution' else 'citation not in extracted'
    with pytest.raises(Rejected, match=message):
        prepare_commitments(calls, load_bank(ROOT / 'bank'), path.read_text(), 'P')
    assert not any(e['stage'] == 'commitments_frozen' for e in calls.log.read())
    assert not (calls.log.path.parent / 'commitments.json').exists()


def test_build_count_failure_preserves_measured_raw_receipt(rig, monkeypatch):
    from test_extraction_rich import rich_calls
    from ara.runtime.orchestration import prepare_commitments
    from ara.bank import load_bank
    calls, provider, path = rich_calls(rig, monkeypatch)
    original = provider.estimate
    def estimate(kind, *a):
        if kind == 'propose_targets' and any(e['stage'] == 'response_received' and json.loads(e['payload_json'])['kind'] == 'build_t_batch' for e in calls.log.read()): raise OSError('P')
        return original(kind, *a)
    monkeypatch.setattr(provider, 'estimate', estimate)
    with pytest.raises(OSError):
        prepare_commitments(calls, load_bank(ROOT / 'bank'), path.read_text(), 'P')
    e = [e for e in calls.log.read() if e['label'] == 'MODEL'][-1]
    assert e['stage'] == 'build_t_batch' and e['response'] is not None
    assert e['usage']['input_tokens'] == 100 and e['usage']['output_tokens'] == 50
    assert e['cost_usd'] == .00175 and json.loads(e['payload_json'])['accounting'] == 'actual'
    assert not any(e['stage'] == 'commitments_frozen' for e in calls.log.read())


def test_extraction_wire_has_unambiguous_nodes(rig, monkeypatch):
    from ara.runtime.providers import structured_schema
    from jsonschema import Draft202012Validator, ValidationError
    schema = json.loads((ROOT / 'schemas/extract_paper.json').read_text())
    wire = structured_schema(schema)
    value = graph()
    for item in value['items']:
        if item['kind'] != 'inference':
            for key in ('premise_ids', 'conclusion_id', 'qualification_ids', 'inference_origin'): del item[key]
    for item in value['items']:
        if item['kind'] not in ('distinction', 'qualification'): del item['applies_to']
    Draft202012Validator(wire).validate(value)
    invalid_relation = copy.deepcopy(value)
    invalid_relation['items'][0]['applies_to'] = ['q']
    with pytest.raises(ValidationError): Draft202012Validator(wire).validate(invalid_relation)
    invalid = copy.deepcopy(value)
    invalid['items'][0]['inference_origin'] = 'paper_stated'
    with pytest.raises(ValidationError): Draft202012Validator(wire).validate(invalid)
    calls, provider, papers, *_ = rig
    monkeypatch.setattr(provider, 'complete', lambda *a: Response(response(value)))
    result = calls.extract_paper(papers[0])
    assert len(result.items) == 8 and result.items[0].inference_origin is None


@pytest.mark.parametrize('failure', ['parse', 'logging'])
def test_known_usage_survives_parsing_or_terminal_log_failure(rig, monkeypatch, failure):
    from ara.runtime.budget import BudgetStop
    calls, provider, *_ = rig
    raw = response({'formula': {'op': 'atom', 'name': 'P'}})
    if failure == 'parse':
        raw['content'][0]['text'] = '{'
        error = Rejected
    else:
        emit = calls.log.emit
        def fail_once(event):
            if event.label == 'MODEL':
                monkeypatch.setattr(calls.log, 'emit', emit)
                raise OSError('P')
            emit(event)
        monkeypatch.setattr(calls.log, 'emit', fail_once)
        error = BudgetStop
    monkeypatch.setattr(provider, 'complete', lambda *a: Response(raw))
    with pytest.raises(error): calls.call('formalise', {'proposition': 'P'})
    events = [e for e in calls.log.read() if e['label'] == 'MODEL']
    assert len(events) == 1
    assert events[0]['cost_usd'] == .00175 and events[0]['usage']['output_tokens'] == 50
    assert json.loads(events[0]['response']) == raw
    assert json.loads(events[0]['payload_json'])['accounting'] == 'actual'
    assert not list(calls.cache.path.glob('*.json'))
