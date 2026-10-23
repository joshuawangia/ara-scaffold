"""Construction dispatch chooses a provider/model without sharing mutable routing state."""
import json
import pytest
import yaml
from decimal import Decimal

from ara.bank import load_bank
from ara.runtime import cli
from ara.runtime.cache import canonical
from ara.runtime.orchestration import prepare_commitments
from ara.runtime.providers import Response
from test_construction_shares import windows, payloads
from test_extraction import rig, ROOT


@pytest.mark.parametrize('profile', [False, True])
def test_native_construction_routes_selection_formalization_and_correction(rig, monkeypatch, tmp_path, profile):
    calls, provider, literature, sent = windows(rig, monkeypatch)
    trace = []
    estimate, complete = provider.estimate, provider.complete
    class Backend:
        def __init__(self, config):
            self.model, self.kind = config['model'], config['provider']
        def estimate(self, kind, prompt, schema, maximum):
            trace.append(('count', self.kind, self.model, kind))
            return estimate(kind, prompt, schema, maximum)
        def complete(self, kind, prompt, schema, maximum):
            trace.append(('generate', self.kind, self.model, kind))
            inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
            raw = complete(kind, prompt, schema, maximum).raw
            if kind == 'select_t_roots' and inputs['batch_index'] == 0 and inputs.get('mode') != 'targeted_correction':
                value = json.loads(raw['content'][0]['text']); value['relevance'] = ''
                raw['content'][0]['text'] = canonical(value)
            return Response({**raw, 'model': self.model})
    monkeypatch.setattr(cli, 'AnthropicProvider', Backend)
    monkeypatch.setattr(cli, 'MockProvider', lambda path, model: Backend({'provider':'mock','model':model}))
    config = {**calls.config, 'stages': {
        'select_t_roots': {'provider':'anthropic','model':'Q'},
        'build_t_batch': {'provider':'mock','model':'R'},
        'construction_correction': {'provider':'anthropic','model':'S'}},
        'pricing': {**calls.config['pricing'], **{model: calls.config['pricing'][calls.config['model']] for model in ('Q','R','S')}}}
    if profile:
        config['pilot'] = {'stages': {'extraction': {'model': calls.config['model']}}}
        path = tmp_path/'stages.yaml'; path.write_text(yaml.safe_dump(config))
        created = []
        def factory(config, log, topic):
            result = cli.make_calls(config, log, topic, ROOT)
            monkeypatch.setattr(result, 'propose_targets', lambda *args: ())
            created.append(result)
            return result
        assert cli.main(['run', '--config', str(path), '--profile', 'pilot', '--topic', calls.topic,
                         '--literature', str(calls.log.path.parent/'literature.extracted.txt'),
                         '--audience', '', '--run-dir', str(tmp_path/'routed')], calls_factory=factory) == 0
        routed = created[0]
        assert len(payloads(routed, 'build_t_batch_accepted')) == 3
    else:
        routed = cli.make_calls(config, calls.log, calls.topic, ROOT)
        result = prepare_commitments(routed, load_bank(ROOT/'bank'), literature, '')
        assert len(result.commitments) == 3
    generated = [entry[1:] for entry in trace if entry[0] == 'generate']
    assert generated[:3] == [('anthropic','Q','select_t_roots'),('anthropic','S','select_t_roots'),('mock','R','build_t_batch')]
    for backend, model, kind in generated:
        assert ('count', backend, model, kind) in trace
    selection = next(inputs for kind,inputs in sent if kind=='select_t_roots' and inputs['batch_index']==1)
    selection = {key:value for key,value in selection.items() if key != 'topic'}
    before = sum(entry[0]=='generate' for entry in trace)
    routed.call('select_t_roots', selection)
    assert sum(entry[0]=='generate' for entry in trace) == before
    routed.config['stages']['select_t_roots']['provider'] = 'mock'
    routed.call('select_t_roots', selection)
    assert sum(entry[0]=='generate' for entry in trace) == before + 1
    assert trace[-1] == ('generate','mock','Q','select_t_roots')
    receipts = [e for e in routed.log.read() if e['label']=='MODEL' and e['stage'] in ('select_t_roots','build_t_batch')]
    assert [e['model_id'] for e in receipts[:3]] == ['Q','S','R']
    assert routed.provider.model == calls.config['model']
    assert routed.config['model'] == config['model']
    assert routed.budget.used_cost == sum(Decimal(str(e['cost_usd'])) for e in routed.log.read())
    plan = payloads(routed,'build_t_plan')[0]['plan']
    assert plan['construction_stages']['select_t_roots']['model'] == 'Q'
    assert plan['construction_stages']['build_t_batch_correction']['model'] == 'S'
    from ara.runtime.export import methodology
    summary = json.loads(methodology(routed.log.path).split('```json\n')[1].split('\n```')[0])
    dispatches = summary['construction']['stage_dispatches']
    assert any(d['stage']=='construction_correction' and d['requested_model']=='S' and d['provider']=='anthropic'
               for d in dispatches)
