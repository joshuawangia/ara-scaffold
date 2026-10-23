"""Measured estimates, upward-only learning, and scarce-window allocation."""
import json
import math
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ara.runtime.cache import canonical
from ara.runtime.closure_budget import budget_plan
from ara.types import Proposition
from test_claude_code import cli


def test_calibration_reproduces_quantiles_and_measured_overhead():
    from ara.runtime.claude_estimation import TABLE
    factors = TABLE['factors']
    for kind, row in factors.items():
        ratios = sorted(s['tokens']/s['bytes'] for s in TABLE['api_samples'] if s['kind']==kind)
        assert row['samples'] == len(ratios)
        assert row['p99'] == ratios[math.ceil(.99*len(ratios))-1]
        assert row['factor'] == math.ceil(row['p99']*1.05*1e6)/1e6
        assert all('prompt' not in s for s in TABLE['api_samples'])
    for sample in TABLE['cli_samples']:
        factor = factors.get(sample['kind'], {'factor':TABLE['fallback_factor']})['factor']
        assert math.ceil(sample['bytes']*factor)+TABLE['runtime_overhead_tokens'] >= sample['tokens']


def test_provider_uses_calibration_and_keeps_two_turn_reservation(cli):
    from ara.runtime.claude_estimation import TABLE
    make, _, _, _ = cli
    calls, _ = make()
    kind, inputs, maximum = 'select_t_roots', {'papers':[]}, 16384
    prompt = calls.render(kind, inputs)[1]
    size = len((prompt + calls.provider.system_for(kind) + canonical(calls.response_schema(kind,inputs))).encode())
    count = calls.count_request(kind, inputs)
    initial = math.ceil(size * TABLE['factors'][kind]['factor']) + TABLE['runtime_overhead_tokens']
    assert count.initial_input_tokens == initial
    assert count.reservation.input_tokens == 2*initial+maximum
    assert count.reservation.output_tokens == 2*maximum


def test_live_usage_tightens_later_calls_without_invalidating_cache(cli):
    make, _, _, binary = cli
    binary.write_text(binary.read_text().replace("result={'type':'result'", "if not canary: usage['input_tokens']=30000\nresult={'type':'result'"))
    calls, log = make()
    inputs = {'proposition':Proposition('p','P').to_dict()}
    before = calls.count_request('formalise', inputs).initial_input_tokens
    calls.formalise(Proposition('p','P'))
    after = calls.count_request('formalise', inputs).initial_input_tokens
    assert before < 30005 <= after
    observations = [json.loads(e['payload_json']) for e in log.read() if e['stage']=='provider_estimate_observation']
    observed = observations[-1]
    assert observed['underestimated'] is True
    assert observed['actual_input_tokens'] == 30005
    assert observed['factor_after'] > observed['factor_before']
    assert calls.formalise(Proposition('p','P')).name == 'P'
    assert len([e for e in log.read() if e['stage']=='provider_estimate_observation']) == len(observations)
    reopened, _ = make()
    assert reopened.count_request('formalise', inputs).initial_input_tokens == after
    # Smaller later receipts never loosen the factor, including concurrent updates.
    provider = calls.provider
    estimate = provider.estimate('formalise', 'P', {}, 32)
    with ThreadPoolExecutor(4) as pool:
        results = list(pool.map(lambda n: provider.observe('formalise','P',{},estimate,{'usage':{'input_tokens':n,'output_tokens':1}}), [1,2,3,4]))
    assert all(r['factor_after'] >= observed['factor_after'] for r in results)


def test_scarce_slots_fund_first_windows_without_exceeding_capacity(cli):
    _, _, config, _ = cli
    config.update(working_t_token_budget=10000, working_t_symbol_token_budget=900,
                  working_t_symbol_growth_tokens_per_item=233, construction_window_cap_multiplier=2)
    plan = budget_plan(config, 5, 200, 1000, 70000)
    assert plan['global_commitment_slots'] == 3
    assert plan['window_initial_commitments'] == [1,1,1,0,0]
    assert plan['window_commitment_caps'] == [2,2,2,0,0]
    assert plan['projected_t_commitments'] == 3
    assert plan['funded_windows'] == 3
    assert plan['allocation_rule'] == 'one_slot_in_plan_order_when_capacity_below_window_count'


def test_correction_provider_reuses_run_calibration(cli, tmp_path):
    import pytest
    from ara.runtime.cli import make_calls
    from ara.runtime.calls import Rejected
    from ara.runtime.construction import construction_call
    from ara.runtime.logging import EventLog
    _, set_mode, config, binary = cli
    config.update(cache_dir=str(tmp_path/'shared-cache'), stages={
        'select_t_roots': {'effort':'low'}, 'construction_correction': {'effort':'high'}})
    binary.write_text(binary.read_text().replace("result={'type':'result'", "if not canary: usage['input_tokens']=30000\nresult={'type':'result'"))
    log = EventLog(tmp_path/'shared/events.jsonl')
    calls = make_calls(config, log, 'P')
    set_mode('construction_correction_rate')
    def check(data):
        raise Rejected('P')
    with pytest.raises(Rejected, match='cli_usage_limit'):
        construction_call(calls,'select_t_roots',{'papers':[]},check,{'select_t_roots':1})
    rows=[json.loads(e['payload_json']) for e in log.read() if e['stage']=='provider_estimate_observation']
    rows=[r for r in rows if r['kind']=='select_t_roots']
    assert len(rows)==4 and rows[0]['underestimated']
    assert all(r['factor_before']>=rows[0]['factor_after'] for r in rows[1:])
    assert all(r['estimated_initial_input_tokens']>=30005 for r in rows[1:])
