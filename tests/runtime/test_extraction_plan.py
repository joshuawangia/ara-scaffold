"""Unpaid planner covers actual page ranges without a generation surface."""
import json
from pathlib import Path

from ara.runtime.cli import main
from test_extraction import rig, offline, ROOT


def test_plan_cli_with_unset_caps_reads_pdfs_and_never_generates(rig, tmp_path, capsys):
    calls, provider, papers, manifest, fulltext, config = rig
    directory = tmp_path/'plan'
    def forbidden(*a):
        raise AssertionError('generation calls factory must never be used')
    result = main(['plan-extraction', '--config', str(config), '--manifest', str(manifest),
                   '--fulltext-dir', str(fulltext), '--paper-id', 'p', '--run-dir', str(directory),
                   '--token-counter', 'local'], calls_factory=forbidden)
    assert result == 0
    plan = json.loads((directory/'extraction-plan.json').read_text())
    assert plan['counter'] == 'local_estimate_utf8_bytes_div_4'
    assert plan['generation_ready'] is False and plan['dispatches'] == 0
    assert plan['model'] == 'claude-opus-5'
    assert plan['papers'][0]['admission'] == 'fits'
    assert plan['papers'][0]['ranges'][0]['pages'] == [1,2]
    assert plan['papers'][0]['estimated_usd'] > 0
    assert plan['totals']['papers'] == 1
    assert all(plan['operator_caps'][k] is None for k in plan['operator_caps'])
    output = capsys.readouterr().out
    assert '"text"' not in output and '"record"' not in output
    from ara.runtime.logging import read_log
    events = [r['event'] for r in read_log(directory/'events.jsonl')]
    assert not any(e['label'] == 'MODEL' or e['stage'] == 'call_start' for e in events)


def test_provider_plan_uses_count_boundary_only(rig, tmp_path, monkeypatch):
    from ara.runtime import planning
    from ara.types import TokenUsage
    calls, _, _, manifest, fulltext, config = rig
    counted = []
    class Counter:
        def __init__(self, settings):
            assert settings['stages']['extraction']['model'] == 'claude-opus-5'
        def estimate(self, kind, prompt, schema, maximum):
            counted.append(kind)
            return TokenUsage(input_tokens=100, output_tokens=maximum)
        def complete(self, *a):
            raise AssertionError('no paid generation')
    monkeypatch.setattr(planning, 'AnthropicProvider', Counter)
    directory = tmp_path/'plan'
    result = main(['plan-extraction', '--config', str(config), '--manifest', str(manifest),
                   '--fulltext-dir', str(fulltext), '--paper-id', 'p', '--run-dir', str(directory),
                   '--token-counter', 'provider'])
    assert result == 0 and counted and set(counted) == {'extract_paper'}
    plan = json.loads((directory/'extraction-plan.json').read_text())
    assert plan['papers'][0]['input_tokens'] == 100
    assert plan['counter'] == 'provider_count_tokens'
    assert plan['papers'][0]['estimated_usd'] == .0605


def test_planned_ranges_use_output_density_and_keep_every_page(rig):
    from ara.runtime.extraction import Paper, PageText, extraction_range_plan
    calls, _, papers, *_ = rig
    calls.config['extraction_planned_output_tokens_per_page'] = 16000
    paper = Paper('p', papers[0].record_json, 'P', tuple(PageText(n, 'P') for n in range(1,21)))
    ranges = extraction_range_plan(calls, paper)
    assert [p.page for pages, _ in ranges for p in pages] == list(range(1,21))
    assert len(ranges) >= 10 and all(len(pages) <= 2 for pages, _ in ranges)
