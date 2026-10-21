"""Native shared-T candidates over ordinary and transitive extraction histories."""
import json
import pytest
import yaml

from test_extraction import rig, offline, response, accounting, pdf, ROOT
from test_paper_recovery import corpus
from ara.runtime.cache import Cache
from ara.runtime.calls import ModelCalls
from ara.runtime.cli import main
from ara.runtime.logging import EventLog
from ara.runtime.providers import Response


@pytest.fixture
def native_builder(rig, monkeypatch, tmp_path):
    calls, provider, _, manifest, fulltext, config = rig
    def build(resume=False, failed=False):
        calls, provider, _, sent = corpus(rig, monkeypatch, failed=('q',) if failed else ())
        calls.config.update(essay_min_words=2, essay_word_limit=300, depth_cap=1, node_cap=8,
                            forward_pass_depth=0)
        config.write_text(yaml.safe_dump(calls.config))
        pdf(fulltext / 'q.pdf', ('Q',))
        def factory(cfg, log, topic):
            return ModelCalls(cfg, provider, log, Cache(log.path.parent / 'cache'), ROOT, topic)
        args = ['extract', '--config', str(config), '--manifest', str(manifest), '--fulltext-dir', str(fulltext)]
        source = tmp_path / 'extraction'
        assert main([*args, '--run-dir', str(source)], calls_factory=factory) == 0
        if resume:
            target = tmp_path / 'resumed'
            assert main([*args, '--run-dir', str(target), '--resume-from', str(source)], calls_factory=factory) == 0
            source = target
        original = provider.complete
        def complete(kind, prompt, schema, maximum):
            if kind in ('extract_paper', 'select_t_roots', 'build_t_batch'):
                return original(kind, prompt, schema, maximum)
            inputs = json.loads(prompt.rsplit('\nINPUT_JSON\n', 1)[1])
            if kind == 'write_essay':
                value = {'title': 'P', 'body': 'P Q ' + ' '.join('[[node:' + n['id'] + ']]' for n in inputs['outline']['nodes']), 'bibliography': []}
            elif kind == 'audit_essay':
                value = {'labels': [dict(sentence=s['sentence'], node_ids=[n['id'] for n in inputs['outline']['nodes']], asserts_premise_or_inference_not_in_outline=False) for s in inputs['sentences']]}
            else:
                value = {'propose_targets': {'targets': [{'id': 'p', 'text': 'P', 'formula': {'op': 'atom', 'name': 'P'}}]},
                         'propose_cuts': {'proposals': []}, 'map_leaf': {'t_id': 'open'},
                         'search_evidence': 'P', 'verify_originality_citations': {'originality': {'assessment': 'unverified', 'evidence_urls': [], 'detail': 'P'}, 'items': []}}[kind]
            return Response(response(value))
        monkeypatch.setattr(provider, 'complete', complete)
        builder = tmp_path / 'builder'
        assert main(['run', '--config', str(config), '--topic', 'P Q', '--literature',
                     str(source / 'literature.extracted.txt'), '--run-dir', str(builder)], calls_factory=factory) == 0
        log = EventLog(builder / 'events.jsonl')
        assert not any(e['stage'] == 'final_draft' for e in log.read())
        route = next(json.loads(e['payload_json'])['graph']['id'] for e in log.read() if e['stage'] == 'route')
        assert main(['select', '--run-dir', str(builder), '--route', route], calls_factory=factory) == 0
        return builder, config, factory
    return build


@pytest.mark.parametrize('resume,failed', [(False, False), (False, True), (True, False), (True, True)])
def test_native_shared_theta_builder(native_builder, tmp_path, resume, failed):
    builder, config, factory = native_builder(resume, failed)
    before = {p.name: p.read_bytes() for p in builder.iterdir() if p.is_file()}
    candidate = tmp_path / 'candidate'
    assert main(['run', '--config', str(config), '--topic', 'P Q', '--from-frozen', str(builder),
                 '--run-dir', str(candidate), '--cost-cap-usd', '2', '--token-cap', '1000000'], calls_factory=factory) == 0
    log = EventLog(candidate / 'events.jsonl')
    route = next(json.loads(e['payload_json'])['graph']['id'] for e in log.read() if e['stage'] == 'route')
    assert main(['select', '--run-dir', str(candidate), '--route', route], calls_factory=factory) == 0
    summary = accounting(log)
    assert summary['extraction']['failed'] == (['q'] if failed else [])
    assert len(summary['extraction']['failure_history']) == (2 if resume else 1) * int(failed)
    assert summary['extraction']['failure_policy']['max_failed_papers'] == 3
    assert summary['extraction']['failure_policy']['policy'] == 'continue-on-paper-failure'
    assert summary['extraction']['extracted'] == (['p'] if failed else ['p', 'q'])
    assert summary['local_totals']['cost_usd'] == summary['cost_usd'] > 0
    assert summary['inherited_totals']['cost_usd'] > 0
    assert any(e['stage'] == 'final_draft' for e in log.read())
    assert not any(e['stage'] in ('extract_paper', 'build_t_batch', 'commitments_frozen') for e in log.read())
    assert (candidate / 'commitments.json').read_bytes() == (builder / 'commitments.json').read_bytes()
    assert before == {p.name: p.read_bytes() for p in builder.iterdir() if p.is_file()}


@pytest.mark.parametrize('damage', ['missing', 'changed'])
def test_native_shared_requires_pinned_ancestors(native_builder, tmp_path, damage, capsys):
    builder, config, factory = native_builder(True, True)
    origin = tmp_path / 'extraction/events.jsonl'
    if damage == 'missing':
        origin.unlink()
    else:
        origin.write_text(origin.read_text().replace('P', 'S', 1))
    def forbidden(*args):
        pytest.fail('broken provenance reached provider')
    assert main(['run', '--config', str(config), '--topic', 'P Q', '--from-frozen', str(builder),
                 '--run-dir', str(tmp_path / 'refused'), '--cost-cap-usd', '2', '--token-cap', '1000000'], calls_factory=forbidden) == 2
    assert 'broken extraction provenance receipt' in capsys.readouterr().err


@pytest.mark.parametrize('damage', [None, 'prompt', 'version'])
def test_retained_legacy_accepted_and_rejected_attempts(rig, monkeypatch, damage):
    from ara.runtime.extraction import extract
    from ara.runtime.frozen import verify_receipts
    from ara.runtime.cache import canonical
    calls, _, papers, _ = corpus(rig, monkeypatch, failed=('q',))
    extract(calls, papers[:2])
    events = calls.log.read()
    template = (ROOT / 'tests/fixtures/runtime/legacy-extract-prompt.txt').read_text()
    template += '\nLOCAL_RESPONSE_SCHEMA (all constraints are mandatory)\n' + canonical(json.loads((ROOT / 'schemas/extract_paper.json').read_text()))
    statuses = set()
    for e in events:
        if e['label'] == 'MODEL':
            p = json.loads(e['payload_json'])
            statuses.add(p['status'])
            p.pop('response_contract_version')
            if damage == 'version': p['response_contract_version'] = 999
            e['payload_json'] = canonical(p)
            inputs = e['prompt'].rsplit('\nINPUT_JSON\n', 1)[1]
            e['prompt'] = template + ('P' if damage == 'prompt' else '') + '\nINPUT_JSON\n' + inputs
    assert statuses == {'accepted', 'rejected'}
    if damage:
        with pytest.raises(ValueError, match='schema/prompt version drift'):
            verify_receipts(events, ROOT)
    else:
        verify_receipts(events, ROOT)


def test_inherited_partial_coverage(rig):
    from test_extraction import register
    from test_extraction_fix1 import add_image
    from ara.runtime.extraction import load_papers, extract
    from ara.runtime.frozen import import_frozen
    from ara.runtime.logging import read_log
    calls, provider, _, manifest, fulltext, _ = rig
    pdf(fulltext / 'p.pdf', ('P', ''))
    add_image(fulltext / 'p.pdf', 1)
    paper = load_papers(manifest, fulltext, ('p',))[0]
    register(calls, provider, paper)
    extract(calls, (paper,))
    log = EventLog(calls.log.path.parent.parent / 'partial-candidate/events.jsonl')
    import_frozen(log, dict(builder_run='P', freeze_hash='Q', commitments_sha256='R',
        commitments={'commitments': []}, records=read_log(calls.log.path), artifacts={}))
    summary = accounting(log)
    inherited = summary['extraction']
    assert inherited['partial'] == [{'source_id': 'p', 'affected_pages': [2],
        'page_diagnostics': [{'page': 2, 'reason': 'sparse_image_text', 'text_chars': 0}]}]
    assert inherited['models'] == ['claude-opus-5']
    assert inherited['production_lineage_complete']
    assert summary['cost_usd'] == summary['local_totals']['cost_usd'] == 0
    assert summary['inherited_totals']['cost_usd'] > 0
