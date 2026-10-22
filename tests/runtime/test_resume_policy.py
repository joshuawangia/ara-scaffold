"""Acceptance-policy binding and ancestor reuse regressions; offline P/Q only."""
import json

import pytest
import yaml

from ara.runtime.cache import Cache
from ara.runtime.calls import ModelCalls, Rejected
from ara.runtime.cli import main
from ara.runtime.extraction import HEADER, extract, literature_provenance
from ara.runtime.logging import EventLog
from ara.runtime.providers import Response
from rich_fixture import graph
from test_extraction import rig, offline, response, accounting, ROOT
from test_paper_recovery import corpus, resumed


def one_premise(provider, monkeypatch, sent):
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        sent.append(inputs['source_id'])
        value = graph(inputs['source_id'])
        value['items'] = value['items'][:1]
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)


def test_changed_acceptance_matches_fresh_extraction(rig, monkeypatch, tmp_path):
    calls, provider, papers, sent = corpus(rig, monkeypatch, failed=(), limit=0)
    one_premise(provider, monkeypatch, sent)
    extract(calls, papers[:1])
    calls.config['extraction_require_inference'] = True
    fresh = ModelCalls(calls.config, provider, EventLog(tmp_path/'fresh/events.jsonl'),
                       Cache(tmp_path/'fresh/cache'), ROOT, '')
    fresh_path = extract(fresh, papers[:1])
    assert 'inference_coverage_unverified' in fresh_path.read_text()
    sent.clear()
    _, path = resumed(calls, provider, papers[:1], tmp_path/'resumed', [calls.log.path.parent])
    assert 'inference_coverage_unverified' in path.read_text()
    assert sent == ['p']
    assert (tmp_path/'resumed/literature.extracted.txt').exists()
    assert accounting(EventLog(tmp_path/'resumed/events.jsonl'))['inherited_totals']['cost_usd'] == .00175


def test_native_cli_changed_acceptance_reextracts(rig, monkeypatch, tmp_path):
    calls, provider, _, manifest, fulltext, config = rig
    sent = []
    one_premise(provider, monkeypatch, sent)
    def factory(cfg, log, topic):
        return ModelCalls(cfg, provider, log, Cache(log.path.parent/'cache'), ROOT, topic)
    args = ['extract', '--config', str(config), '--manifest', str(manifest),
            '--fulltext-dir', str(fulltext), '--paper-id', 'p']
    source = tmp_path/'source'
    assert main([*args, '--run-dir', str(source)], calls_factory=factory) == 0
    data = yaml.safe_load(config.read_text())
    data['extraction_require_inference'] = True
    config.write_text(yaml.safe_dump(data))
    assert main([*args, '--run-dir', str(tmp_path/'fresh')], calls_factory=factory) == 0
    sent.clear()
    target = tmp_path/'resumed'
    assert main([*args, '--run-dir', str(target), '--resume-from', str(source)], calls_factory=factory) == 0
    assert sent == ['p']
    assert (target/'literature.extracted.txt').exists()


@pytest.mark.parametrize('change', ['model', 'effort', 'thinking', 'fallbacks', 'version', 'prompt', 'schema', 'legacy'])
def test_acceptance_contract_drift_reextracts(rig, monkeypatch, tmp_path, change):
    calls, provider, papers, sent = corpus(rig, monkeypatch, failed=())
    if change == 'legacy':
        import ara.runtime.extraction as extraction
        original = extraction.extraction_acceptance_identity
        monkeypatch.setattr(extraction, 'extraction_acceptance_identity', lambda *a: None)
    extract(calls, papers[:1])
    if change in ('model', 'effort', 'thinking', 'fallbacks'):
        calls.config['stages']['extraction'][change] = {
            'model': 'claude-opus-5', 'effort': 'low', 'thinking': 'disabled', 'fallbacks': ['claude-opus-4-8']}[change]
    elif change == 'legacy':
        monkeypatch.setattr(extraction, 'extraction_acceptance_identity', original)
    elif change == 'version':
        import ara.runtime.extraction as extraction
        monkeypatch.setattr(extraction, 'EXTRACTION_ACCEPTANCE_VERSION', 'changed')
    else:
        original_read = type(ROOT).read_text
        contract_path = ROOT/('prompts/extract_paper.txt' if change == 'prompt' else 'schemas/extract_paper.json')
        def changed_read(self, *args, **kwargs):
            text = original_read(self, *args, **kwargs)
            if self != contract_path: return text
            if change == 'prompt': return text+'\nP\n'
            data = json.loads(text); data['description'] = 'P'
            return json.dumps(data)
        monkeypatch.setattr(type(ROOT), 'read_text', changed_read)
    sent.clear()
    follow, path = resumed(calls, provider, papers[:1], tmp_path/'follow', [calls.log.path.parent])
    assert [i['source_id'] for _, i in sent] == ['p']
    assert float(follow.budget.used_cost) == pytest.approx(.0035)
    literature_provenance(path, path.read_text())


def test_caps_recovery_and_unrelated_stage_changes_allow_reuse(rig, monkeypatch, tmp_path):
    calls, provider, papers, sent = corpus(rig, monkeypatch, failed=())
    extract(calls, papers[:1])
    calls.config.update(cost_cap_usd=125, extraction_cost_cap_usd=125, token_cap=6000000,
                        extraction_paper_cost_cap_usd=25, extraction_paper_continuation_limit=30,
                        extraction_targeted_corrections=1, extraction_max_failed_papers=4)
    calls.config['stages']['write_essay'] = {'effort': 'low'}
    # An overridden global model is irrelevant to the effective extraction stage.
    calls.config['model'] = 'claude-sonnet-5-5'
    sent.clear()
    follow, path = resumed(calls, provider, papers[:1], tmp_path/'follow', [calls.log.path.parent])
    assert sent == []
    assert float(follow.budget.used_cost) == pytest.approx(.00175)
    literature_provenance(path, path.read_text())


def test_stopped_descendant_reuses_unreached_ancestor_success(rig, monkeypatch, tmp_path):
    calls, provider, papers, sent = corpus(rig, monkeypatch, failed=('q',), limit=0)
    extract(calls, papers[:1])
    with pytest.raises(Rejected):
        resumed(calls, provider, (papers[1], papers[0]), tmp_path/'second', [calls.log.path.parent])
    second = EventLog(tmp_path/'second/events.jsonl')
    assert accounting(second)['extraction']['failed'] == ['q']
    sent.clear()
    third, path = resumed(calls, provider, papers[:1], tmp_path/'third', [second.path.parent])
    assert sent == []
    assert float(third.budget.used_cost) == pytest.approx(.0035)
    summary = accounting(third.log)['extraction']
    assert summary['extracted'] == ['p'] and summary['failed'] == []
    assert [p['source_id'] for p in summary['failure_history']] == ['q']
    assert len(json.loads(path.read_text()[len(HEADER):])['papers']) == 1
    literature_provenance(path, path.read_text())


def test_conflicting_compatible_ancestor_successes_refuse(rig, monkeypatch, tmp_path):
    calls, provider, papers, sent = corpus(rig, monkeypatch, failed=())
    extract(calls, papers[:1])
    original = provider.complete
    def changed(*args):
        value = json.loads(original(*args).text()); value['items'][0]['text'] = 'Q'
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', changed)
    other = ModelCalls(calls.config, provider, EventLog(tmp_path/'other/events.jsonl'),
                       Cache(tmp_path/'other/cache'), ROOT, '')
    extract(other, papers[:1])
    from ara.runtime.extraction import resume_papers
    destination = EventLog(tmp_path/'destination/events.jsonl')
    with pytest.raises(ValueError, match='conflicting completed'):
        resume_papers(destination, papers[:1], [calls.log.path.parent, other.log.path.parent], calls.config, ROOT)
    assert destination.read() == []



def test_execution_rechecks_reuse_policy(rig, monkeypatch, tmp_path):
    from ara.runtime.extraction import resume_papers
    calls, provider, papers, sent = corpus(rig, monkeypatch, failed=())
    extract(calls, papers[:1])
    destination = EventLog(tmp_path/'follow/events.jsonl')
    reused = resume_papers(destination, papers[:1], [calls.log.path.parent], calls.config, ROOT)
    calls.config['extraction_require_inference'] = True
    follow = ModelCalls(calls.config, provider, destination, Cache(tmp_path/'follow/cache'), ROOT, '')
    sent.clear()
    with pytest.raises(ValueError, match='acceptance identity mismatch'):
        extract(follow, papers[:1], reused=reused)
    assert sent == []
    assert not (tmp_path/'follow/literature.extracted.txt').exists()


def test_strict_coverage_refuses_reused_partial_paper(rig, monkeypatch, tmp_path):
    from dataclasses import replace
    from ara.runtime.extraction import PageDiagnostic, resume_papers
    calls, provider, papers, sent = corpus(rig, monkeypatch, failed=())
    paper = replace(papers[0], diagnostics=(PageDiagnostic(1, 'private_use_glyphs', 1),))
    path = extract(calls, (paper,))
    assert json.loads(path.read_text()[len(HEADER):])['papers'][0]['status'] == 'partial'
    destination = EventLog(tmp_path/'follow/events.jsonl')
    reused = resume_papers(destination, (paper,), [calls.log.path.parent], calls.config, ROOT)
    follow = ModelCalls(calls.config, provider, destination, Cache(tmp_path/'follow/cache'), ROOT, '')
    sent.clear()
    with pytest.raises(ValueError, match='partial text coverage'):
        extract(follow, (paper,), missing='refuse', reused=reused)
    assert sent == []
    assert not (tmp_path/'follow/literature.extracted.txt').exists()
