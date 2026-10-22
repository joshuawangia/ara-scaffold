"""Disclosed paper failures and completed-paper reuse through native boundaries."""
import json
from pathlib import Path

import pytest
import yaml

from ara.runtime.budget import BudgetStop
from ara.runtime.cache import Cache
from ara.runtime.calls import ModelCalls, Rejected
from ara.runtime.cli import main
from ara.runtime.extraction import HEADER, Paper, PageText, extract, literature_provenance, import_provenance
from ara.runtime.logging import EventLog
from ara.runtime.providers import Response
from rich_fixture import graph, batch_response
from test_extraction import rig, offline, response, accounting, ROOT


def corpus(rig, monkeypatch, failed=('q',), limit=3):
    calls, provider, *_ = rig
    calls.config.update(extraction_max_failed_papers=limit, extraction_targeted_corrections=0)
    papers = tuple(Paper(id, json.dumps({'id': id, 'title': id.upper()}), id.upper(),
                         (PageText(1, 'P Q R F(x)'),)) for id in ('p', 'q', 'r', 's', 't'))
    sent = []
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        sent.append((kind, inputs))
        if kind == 'extract_paper':
            value = graph(inputs['source_id'])
            if inputs['source_id'] in failed:
                value['source_id'] = 'invalid'
        else:
            value = batch_response(inputs)
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    return calls, provider, papers, sent


def test_failed_paper_disclosed_and_excluded_from_construction(rig, monkeypatch, tmp_path):
    calls, provider, papers, sent = corpus(rig, monkeypatch)
    path = extract(calls, papers[:3])
    data = json.loads(path.read_text()[len(HEADER):])
    assert [p['status'] for p in data['papers']] == ['extracted', 'failed', 'extracted']
    failed = data['papers'][1]
    assert failed['items'] == [] and failed['reason'] == 'InvalidOutput'
    assert failed['failure_receipt']['source_log'] == str(calls.log.path.resolve())
    assert failed['failure_receipt']['records'] > 0 and len(failed['failure_receipt']['last_hash']) == 64
    assert [i['source_id'] for k,i in sent] == ['p', 'q', 'r']
    events = literature_provenance(path, path.read_text())
    downstream_log = EventLog(tmp_path/'pilot/events.jsonl')
    import_provenance(downstream_log, events)
    downstream = ModelCalls(calls.config, provider, downstream_log, calls.cache, ROOT, 'P')
    result = downstream.build_t(path.read_text(), 'P')
    assert {c.id.split(':')[0] for c in result.commitments} == {'p', 'r'}
    assert all(p['source_id'] != 'q' for k,i in sent if k != 'extract_paper' for p in i['papers'])
    summary = accounting(downstream_log)['extraction']
    assert summary['failed'] == ['q']
    assert summary['failure_policy']['max_failed_papers'] == 3
    assert summary['failure_policy']['policy'] == 'continue-on-paper-failure'
    assert summary['failed_papers'][0]['failure_receipt'] == failed['failure_receipt']


def test_failure_threshold_stops_only_after_exceeded(rig, monkeypatch):
    calls, _, papers, sent = corpus(rig, monkeypatch, failed=('p','q','r','s'))
    with pytest.raises(Rejected):
        extract(calls, papers)
    assert [i['source_id'] for _,i in sent] == ['p','q','r','s']
    assert (calls.log.path.parent/'literature.extracted.txt').exists()
    stop = next(json.loads(e['payload_json']) for e in calls.log.read() if e['stage']=='extraction_stopped')
    assert stop['max_failed_papers'] == 3 and stop['failed_count'] == 4
    assert stop['not_attempted'] == ['t']


@pytest.mark.parametrize('failure', ['global_cap', 'unknown_spend', 'paper_cap'])
def test_only_paper_local_budget_stop_can_continue(rig, monkeypatch, failure):
    calls, provider, papers, sent = corpus(rig, monkeypatch, failed=())
    if failure == 'global_cap':
        calls.config['token_cap'] = 0
    elif failure == 'paper_cap':
        calls.config['extraction_paper_continuation_limit'] = 0
        original = provider.complete
        def incomplete(*args):
            result = original(*args)
            value = json.loads(result.text())
            if value['source_id'] == 'p':
                value.update(coverage_complete=False, new_gaps=[{'description': 'Q'}])
            return Response(response(value))
        monkeypatch.setattr(provider, 'complete', incomplete)
    else:
        def unavailable(*args):
            raise OSError('P')
        monkeypatch.setattr(provider, 'complete', unavailable)
    if failure == 'paper_cap':
        path = extract(calls, papers[:2])
        data = json.loads(path.read_text()[len(HEADER):])
        assert [p['status'] for p in data['papers']] == ['extracted','extracted']
        assert data['papers'][0]['open_gaps']
    else:
        with pytest.raises(BudgetStop):
            extract(calls, papers[:2])
        assert (calls.log.path.parent/'literature.extracted.txt').exists()
        assert not any(e['stage']=='extraction_paper_started' and json.loads(e['payload_json'])['source_id']=='q'
                       for e in calls.log.read())


@pytest.mark.parametrize('value', [-1, True, 1.5, None])
def test_invalid_failure_threshold_refuses_before_dispatch(rig, monkeypatch, value):
    calls, _, papers, sent = corpus(rig, monkeypatch, limit=value)
    with pytest.raises(ValueError, match='extraction_max_failed_papers'):
        extract(calls, papers)
    assert sent == []


def resumed(calls, provider, papers, directory, sources):
    from ara.runtime.extraction import resume_papers
    log = EventLog(directory/'events.jsonl')
    reused = resume_papers(log, papers, sources, calls.config, ROOT)
    follow = ModelCalls(calls.config, provider, log, Cache(directory/'cache'), ROOT, '')
    return follow, extract(follow, papers, reused=reused)


@pytest.mark.parametrize('stopped', [False, True])
def test_resume_reuses_completed_papers_and_retries_failed(rig, monkeypatch, tmp_path, stopped):
    calls, provider, papers, sent = corpus(rig, monkeypatch, limit=0 if stopped else 3)
    calls.config['extraction_paper_continuation_limit'] = 0
    source = calls.log.path.parent
    if stopped:
        with pytest.raises(Rejected): extract(calls, papers[:2])
    else:
        extract(calls, papers[:2])
    prior_cost = float(calls.budget.used_cost)
    sent.clear()
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        sent.append((kind, inputs))
        return Response(response(graph(inputs['source_id'])))
    monkeypatch.setattr(provider, 'complete', complete)
    follow, path = resumed(calls, provider, papers[:3], tmp_path/'follow', [source])
    assert [i['source_id'] for _,i in sent] == ['q','r']
    assert float(follow.budget.used_cost) == pytest.approx(prior_cost + .0035)
    assert len(json.loads(path.read_text()[len(HEADER):])['papers']) == 3
    literature_provenance(path, path.read_text())
    summary = accounting(follow.log)
    assert summary['extraction']['failed'] == []
    assert len(summary['extraction']['failure_history']) == 1
    assert summary['inherited_totals']['cost_usd'] == prior_cost


def test_transitive_overlapping_import_does_not_double_charge(rig, monkeypatch, tmp_path):
    calls, provider, papers, sent = corpus(rig, monkeypatch, failed=())
    extract(calls, papers[:1])
    second, _ = resumed(calls, provider, papers[:2], tmp_path/'second', [calls.log.path.parent])
    sent.clear()
    third, path = resumed(calls, provider, papers[:3], tmp_path/'third',
                           [calls.log.path.parent, second.log.path.parent, calls.log.path.parent])
    assert [i['source_id'] for _,i in sent] == ['r']
    assert float(third.budget.used_cost) == pytest.approx(.00525)
    downstream = EventLog(tmp_path/'downstream/events.jsonl')
    import_provenance(downstream, literature_provenance(path, path.read_text()))
    assert accounting(downstream)['cost_usd'] == .00525
    assert accounting(downstream)['extraction']['extracted'] == ['p','q','r']


def test_resume_origin_tamper_is_detected_transitively(rig, monkeypatch, tmp_path):
    calls, provider, papers, _ = corpus(rig, monkeypatch, failed=())
    extract(calls, papers[:1])
    second, _ = resumed(calls, provider, papers[:2], tmp_path/'second', [calls.log.path.parent])
    third, _ = resumed(calls, provider, papers[:3], tmp_path/'third', [second.log.path.parent])
    original = calls.log.path.read_text()
    calls.log.path.write_text(original.replace('"cost_usd":0.00175', '"cost_usd":0.0', 1))
    with pytest.raises(ValueError):
        resumed(calls, provider, papers[:3], tmp_path/'fourth', [third.log.path.parent])


def test_failed_status_cannot_supply_items_even_without_provenance(rig, monkeypatch):
    calls, provider, papers, sent = corpus(rig, monkeypatch, failed=())
    path = extract(calls, papers[:2])
    data = json.loads(path.read_text()[len(HEADER):])
    data['papers'][0]['status'] = 'failed'
    sent.clear()
    with pytest.raises(Rejected, match='failed'):
        calls.build_t(HEADER+json.dumps(data), 'P')
    assert sent == []



def test_exact_failure_threshold_completes(rig, monkeypatch):
    calls, _, papers, sent = corpus(rig, monkeypatch, failed=('p', 'q', 'r'))
    path = extract(calls, papers)
    assert len(sent) == 5
    assert json.loads(path.read_text()[len(HEADER):])['status'] == 'complete_with_disclosed_failures'
    assert accounting(calls.log)['extraction']['failed'] == ['p', 'q', 'r']


@pytest.mark.parametrize('change', ['pdf', 'input'])
def test_changed_source_is_extracted_again(rig, monkeypatch, tmp_path, change):
    from dataclasses import replace
    calls, provider, papers, sent = corpus(rig, monkeypatch, failed=())
    extract(calls, papers[:1])
    changed = replace(papers[0], **({'pdf_sha256': 'Q'} if change == 'pdf' else
                                  {'pages': (PageText(1, 'Q'),)}))
    sent.clear()
    follow, path = resumed(calls, provider, (changed,), tmp_path/'follow', [calls.log.path.parent])
    assert [i['source_id'] for _, i in sent] == ['p']
    assert float(follow.budget.used_cost) == pytest.approx(.0035)
    literature_provenance(path, path.read_text())


def test_inherited_cost_prevents_new_dispatch(rig, monkeypatch, tmp_path):
    calls, provider, papers, sent = corpus(rig, monkeypatch, failed=())
    extract(calls, papers[:1])
    reserve = calls.budget.cost(calls.count_request('extract_paper', papers[1].inputs()),
                                model=calls.requested_model('extract_paper'))
    calls.config['extraction_cost_cap_usd'] = float(reserve + calls.budget.used_cost / 2)
    sent.clear()
    with pytest.raises(BudgetStop, match='extraction cost cap'):
        resumed(calls, provider, papers[:2], tmp_path/'follow', [calls.log.path.parent])
    assert sent == []


@pytest.mark.parametrize('damage', ['missing', 'pin', 'truncated'])
def test_origin_damage_refuses_before_new_dispatch(rig, monkeypatch, tmp_path, damage):
    calls, provider, papers, sent = corpus(rig, monkeypatch, failed=())
    extract(calls, papers[:1])
    second, path = resumed(calls, provider, papers[:2], tmp_path/'second', [calls.log.path.parent])
    sent.clear()
    if damage == 'missing':
        calls.log.path.unlink()
    elif damage == 'truncated':
        rows = calls.log.path.read_text().splitlines(True)
        calls.log.path.write_text(''.join(rows[:-1]))
    else:
        sidecar = path.with_suffix('.provenance.json')
        data = json.loads(sidecar.read_text())
        data['last_hash'] = '0' * 64
        sidecar.write_text(json.dumps(data))
    with pytest.raises((ValueError, FileNotFoundError)):
        literature_provenance(path, path.read_text())
    assert sent == []


def test_native_cli_resume_and_pilot_import(rig, monkeypatch, tmp_path):
    from test_extraction import pdf
    calls, provider, _, manifest, fulltext, config = rig
    calls, provider, _, sent = corpus(rig, monkeypatch)
    pdf(fulltext/'q.pdf', ('Q',))
    config.write_text(yaml.safe_dump(calls.config))
    def factory(cfg, log, topic):
        return ModelCalls(cfg, provider, log, Cache(log.path.parent/'cache'), ROOT, topic)
    source, target = tmp_path/'source', tmp_path/'target'
    args = ['extract', '--config', str(config), '--manifest', str(manifest), '--fulltext-dir', str(fulltext)]
    assert main([*args, '--run-dir', str(source)], calls_factory=factory) == 0
    original = provider.complete
    def pilot_complete(kind, prompt, schema, maximum):
        if kind in ('extract_paper', 'select_t_roots', 'build_t_batch'):
            return original(kind, prompt, schema, maximum)
        values = {'propose_targets': {'targets': [{'id': 'p', 'text': 'P', 'formula': {'op': 'atom', 'name': 'P'}}]},
                  'propose_cuts': {'proposals': []}, 'map_leaf': {'t_id': 'open'}}
        return Response(response(values[kind]))
    monkeypatch.setattr(provider, 'complete', pilot_complete)
    native = tmp_path/'native-pilot'
    assert main(['run', '--config', str(config), '--topic', 'P', '--literature',
                 str(source/'literature.extracted.txt'), '--run-dir', str(native)], calls_factory=factory) == 0
    commitments = json.loads((native/'commitments.json').read_text())['commitments']
    assert commitments and all(c['citation'].startswith('p:') for c in commitments)
    assert accounting(EventLog(native/'events.jsonl'))['extraction']['failed'] == ['q']
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        sent.append((kind, inputs))
        return Response(response(graph(inputs['source_id']) if kind == 'extract_paper' else batch_response(inputs)))
    monkeypatch.setattr(provider, 'complete', complete)
    sent.clear()
    assert main([*args, '--run-dir', str(target), '--resume-from', str(source),
                 '--resume-from', str(source)], calls_factory=factory) == 0
    assert [i['source_id'] for k, i in sent] == ['q']
    artifact = target/'literature.extracted.txt'
    events = literature_provenance(artifact, artifact.read_text())
    pilot = EventLog(tmp_path/'pilot/events.jsonl')
    import_provenance(pilot, events, json.loads(artifact.with_suffix('.provenance.json').read_text()))
    built = factory(calls.config, pilot, 'P').build_t(artifact.read_text(), 'P')
    assert {c.id.split(':')[0] for c in built.commitments} == {'p', 'q'}
    assert accounting(pilot)['inherited_totals']['cost_usd'] == .00525


def test_full_profile_default_failure_threshold():
    config = yaml.safe_load((ROOT/'config.yaml').read_text())
    assert config['extraction-full']['extraction_max_failed_papers'] == 8


def test_operational_error_stops_corpus(rig, monkeypatch):
    calls, _, papers, sent = corpus(rig, monkeypatch, failed=())
    def broken(*args, **kwargs):
        raise OSError('P')
    monkeypatch.setattr(calls.provider, 'estimate', broken)
    with pytest.raises(OSError):
        extract(calls, papers[:2])
    assert sent == []
    assert (calls.log.path.parent/'literature.extracted.txt').exists()



def test_fresh_origin_checkpoint_refuses_truncated_log(rig, monkeypatch, tmp_path):
    from ara.runtime.extraction import resume_papers
    calls, _, papers, _ = corpus(rig, monkeypatch, failed=())
    extract(calls, papers[:1])
    rows = calls.log.path.read_text().splitlines(True)
    calls.log.path.write_text(''.join(rows[:-1]))
    destination = EventLog(tmp_path/'follow/events.jsonl')
    with pytest.raises(ValueError, match='checkpoint'):
        resume_papers(destination, papers[:1], [calls.log.path.parent], calls.config, ROOT)
    assert destination.read() == []


@pytest.mark.parametrize('error', [OSError, ValueError])
def test_admission_operational_error_is_not_paper_failure(rig, monkeypatch, error):
    calls, _, papers, sent = corpus(rig, monkeypatch, failed=())
    original = calls.count_request
    def broken(*args, **kwargs):
        if kwargs.get('admission'):
            raise error('P')
        return original(*args, **kwargs)
    monkeypatch.setattr(calls, 'count_request', broken)
    with pytest.raises(error):
        extract(calls, papers[:2])
    assert sent == []
    assert (calls.log.path.parent/'literature.extracted.txt').exists()



def test_completed_empty_disposition_is_reused(rig, monkeypatch, tmp_path):
    calls, provider, papers, sent = corpus(rig, monkeypatch, failed=())
    def complete(kind, prompt, schema, maximum):
        inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        sent.append(inputs['source_id'])
        return Response(response(dict(schema_version=2, source_id=inputs['source_id'],
            items=[], coverage_complete=True, new_gaps=[], empty_reason='P')))
    monkeypatch.setattr(provider, 'complete', complete)
    path = extract(calls, papers[:1])
    assert json.loads((path.parent/'p.extraction.json').read_text())['dispositions']
    sent.clear()
    follow, artifact = resumed(calls, provider, papers[:1], tmp_path/'follow', [calls.log.path.parent])
    assert sent == []
    assert float(follow.budget.used_cost) == pytest.approx(.00175)
    literature_provenance(artifact, artifact.read_text())
