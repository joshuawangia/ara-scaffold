"""Alignment judgments remain distinct from locally verified source citations."""
import json

import pytest

from ara.runtime.cache import canonical, digest
from ara.runtime.providers import Response
from ara.types import Commitment, CommitmentSet, Formula, PremiseFill, Proposal, Proposition, RouteGraph, RouteNode, RunEvent
from test_calls import rig, response, ROOT


def aligned_sources(calls, provider, log, monkeypatch):
    from ara.bank import load_bank
    from ara.runtime.commitment_provenance import source_provenance
    from ara.runtime.extraction import HEADER
    from ara.runtime.grounding import POLICY, receipt_hash
    from ara.runtime.logging import now
    from ara.runtime.orchestration import prepare_commitments
    from rich_fixture import graph

    calls.config.update(provider='mock', stages={}, essay_min_words=0,
                        construction_alignment_candidates=1, token_cap=1000000)
    papers, rows, commitments, symbols, extraction_inputs = [], {}, [], [], []
    for index, (tid, name) in enumerate((('p', 'P'), ('q', 'Q'))):
        item = graph(tid)['items'][index]
        item['citation'] = tid + ':pdf:1#' + tid
        pages = {1: item['text']}
        page_hash = digest(canonical(pages))
        pdf_hash = ('a' if tid == 'p' else 'b') * 64
        papers.append(dict(source_id=tid, status='partial', items=[item], quarantined=[],
            open_gaps=[], resolutions=[], pdf_sha256=pdf_hash,
            grounding=dict(policy=POLICY, source_text_sha256=page_hash,
                           inventory_sha256=receipt_hash([item], [], page_hash))))
        rows[tid] = source_provenance(item, [tid], ['i'] if tid == 'q' else ())
        commitments.append(Commitment(tid, name, item['citation'], Formula('atom', name=name)))
        symbols.append(dict(name=name, kind='atom', arity=0, definition='P Q', evidence_ids=[tid]))
        extraction_inputs.append(dict(source_id=tid, pdf_sha256=pdf_hash,
            record=dict(id=tid, authors=tid, year=2000, title=name, venue='P', open_access_url=None),
            pages=[dict(page=1, text=item['text'])]))
    original = CommitmentSet(tuple(commitments))
    log.record('run_started', config=calls.config, topic='P', audience='P',
               literature=HEADER + canonical(dict(papers=papers)))
    for inputs in extraction_inputs:
        log.emit(RunEvent(now(), 'extract_paper', 'MODEL', prompt='\nINPUT_JSON\n' + canonical(inputs),
            payload_json=canonical(dict(source_id=inputs['source_id'], status='accepted', cache_hit=False, cache_key='P'))))
    log.record('build_t_merged', commitments=original.to_dict(), symbols=symbols, provenance=rows)
    monkeypatch.setattr(calls, 'build_t', lambda *_: original)
    def judge(kind, *_):
        assert kind == 'judge_symbol_alignment'
        return Response(response(dict(relation='entails_left_right', reason='P Q')))
    monkeypatch.setattr(provider, 'complete', judge)
    frozen = prepare_commitments(calls, load_bank(ROOT / 'bank'), 'P', 'P')
    bridge = frozen.commitments[-1]
    assert bridge.id.startswith('alignment:')
    route = RouteGraph('aligned', 'nq', (
        RouteNode('nq', Proposition('target', 'Q', Formula('atom', name='Q')), 'inference',
            proposal=Proposal('modus_ponens', (
                PremiseFill('conditional', bridge.text, bridge.id),
                PremiseFill('antecedent', 'P', 'p')), 'Q', conclusion_ref='current_goal'),
            children=('nb', 'np')),
        RouteNode('np', Proposition('p', 'P', frozen.get('p').formula), 'leaf', 'p'),
        RouteNode('nb', Proposition('bridge', bridge.text, bridge.formula), 'leaf', bridge.id)), 'CLOSED')
    log.record('route', graph=route.to_dict())
    return route, frozen, bridge


def test_native_alignment_composition_preserves_source_citations_and_disclosure(rig, monkeypatch):
    from ara.runtime.orchestration import compose
    from ara.runtime.writing import source_context
    calls, provider, log = rig
    route, frozen, bridge = aligned_sources(calls, provider, log, monkeypatch)
    paths = [log.path.parent / name for name in ('commitments.json', 'frozen-t.json', 'commitment-provenance.json')]
    before = {p.name: p.read_bytes() for p in paths}
    evidence = source_context(calls, route)
    assert {b['id'] for b in evidence['allowed_bibliography']} == {'p', 'q'}
    assert {s['commitment']['id'] for s in evidence['supporting_commitments']} == {'p', bridge.id}
    extra = evidence['alignment_source_evidence']
    assert [s['commitment']['id'] for s in extra] == ['q']
    assert extra[0]['provenance']['source_text'] == 'Q Q Q'
    assert extra[0]['authority'] == 'definition_evidence_not_additional_premise'
    assert evidence['disclosed_limits']['omitted_support_ids'] == ['i']
    draft = dict(title='P', body='[[node:np]] P P P. [cite:p]\n'
                 '[[node:nb]] Model judgment P implies Q. [cite:q]\n[[node:nq]] Q Q Q.',
                 bibliography=evidence['allowed_bibliography'])
    seen = []
    def complete(kind, prompt, *_):
        inputs = json.loads(prompt.split('INPUT_JSON\n')[1]); seen.append(kind)
        if kind == 'audit_essay':
            assert inputs['outline']['alignment_disclosure']['judgments']
            assert inputs['source_evidence']['alignment_source_evidence'] == extra
            assert any(r['role'] == 'alignment_premise' for r in inputs['outline']['source_roles'])
            assert len(inputs['sentences']) == 3
            value = dict(labels=[dict(sentence=s['sentence'], role='argument_step', node_ids=[node], citation_supported=True)
                                 for node, s in zip(('np', 'nb', 'nq'), inputs['sentences'])])
        elif kind == 'search_evidence':
            assert inputs['items'] == []
            value = 'P'
        else:
            assert kind == 'verify_originality_citations' and inputs['items'] == []
            value = dict(items=[], originality=dict(assessment='unverified', detail='P', evidence_urls=[]))
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    result = compose(calls, route, draft)
    assert result == draft and seen.count('audit_essay') == 4
    assert {p.name: p.read_bytes() for p in paths} == before
    essay = (log.path.parent / 'export/essay.txt').read_text()
    assert 'PDF p. 1' in essay and bridge.id not in essay
    receipts = [json.loads(e['payload_json']) for e in log.read() if e['stage'] == 'local_citation_verification']
    assert {r['item_id'] for r in receipts if r['status'] == 'verified'} == {'p', 'q'}


def test_alignment_definition_source_coverage_and_bridge_citation_refuse(rig, monkeypatch):
    from ara.runtime.calls import Rejected
    from ara.runtime.citations import check_coverage
    from ara.runtime.writing import source_context
    calls, provider, log = rig
    route, _, bridge = aligned_sources(calls, provider, log, monkeypatch)
    entries = source_context(calls, route)['allowed_bibliography']
    draft = dict(title='P', body='P P P. [cite:p]', bibliography=[e for e in entries if e['id'] == 'p'])
    with pytest.raises(ValueError, match='citation coverage'):
        check_coverage(log.read(), route, draft)
    draft = dict(title='P', body='P Q. [cite:' + bridge.id + ']',
                 bibliography=[dict(id=bridge.id, text=bridge.citation, url=None)])
    seen = []
    monkeypatch.setattr(provider, 'complete', lambda *a: seen.append(a))
    with pytest.raises(Rejected, match='alignment.*source citation'):
        calls.verify_originality_citations(draft)
    assert seen == []


def test_sectioned_alignment_writer_cites_definition_sources(rig, monkeypatch):
    from ara.runtime.calls import word_count
    calls, provider, log = rig
    route, _, bridge = aligned_sources(calls, provider, log, monkeypatch)
    calls.config.update(essay_min_words=4500, token_cap=10_000_000)
    def complete(kind, prompt, *_):
        inputs = json.loads(prompt.split('INPUT_JSON\n')[1])
        assert inputs['source_evidence']['alignment_source_evidence'][0]['commitment']['id'] == 'q'
        if kind == 'outline_essay':
            value = dict(title='P', sections=[dict(id=f's{i}', heading='P', purpose='P',
                word_budget=1000, node_ids=['np', 'nb', 'nq']) for i in range(5)])
        else:
            assert kind == 'write_essay'
            value = dict(title='P', body='[[node:np]] [[node:nb]] [[node:nq]] ' + 'P ' * 1000 +
                '[cite:p] [cite:q]', bibliography=inputs['source_evidence']['allowed_bibliography'])
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', complete)
    draft = calls.write_essay(route)
    assert 4500 <= word_count(draft) <= 6000
    assert {b['id'] for b in draft['bibliography']} == {'p', 'q'}
    assert bridge.id not in draft['body']


@pytest.mark.parametrize('render', ['reading', 'figures', 'figures_with_receipts'])
def test_alignment_publication_preserves_definition_citations_and_judgment_role(rig, monkeypatch, tmp_path, render):
    from ara.runtime.writing import source_context
    from ara.runtime.publication_references import bibliography_records, reading_copy
    from ara.runtime.publication_figures import generate_figures
    calls, provider, log = rig
    route, _, bridge = aligned_sources(calls, provider, log, monkeypatch)
    evidence = source_context(calls, route)
    if render == 'reading':
        records = bibliography_records(log, evidence)
        text, receipt = reading_copy('P [cite:p] Q [cite:q]', evidence, records, None)
        assert set(records) == set(receipt) == {'p', 'q'}
        assert text == 'P (p 2000, PDF p. 1) Q (q 2000, PDF p. 1)'
        from ara.runtime.calls import Rejected
        with pytest.raises(Rejected, match='reading citation lacks T provenance'):
            reading_copy('P [cite:' + bridge.id + ']', evidence, records, None)
    else:
        receipts = {id: dict(display=id + ' 2000, PDF p. 1') for id in ('p', 'q')}
        manifest = generate_figures(calls, route, tmp_path, receipts if render.endswith('receipts') else None)
        assert len(manifest) == 2
        for entry in manifest:
            svg = (tmp_path / entry['file']).read_text()
            assert 'Model alignment judgment' in svg
            assert 'not source endorsement' in svg
            assert 'Source: None' not in svg
