"""Competition writing through the real logged boundary, with placeholder replies."""
import json

import pytest

from ara.runtime.calls import Rejected, word_count
from ara.runtime.providers import Response
from test_calls import response, rig
from test_writer_validation import route


def plan():
    return {'title': 'P', 'sections': [
        {'id': f's{i}', 'heading': 'P', 'purpose': 'P', 'word_budget': 1000,
         'node_ids': ['n0', 'n1']} for i in range(5)]}


def section(words, token='P'):
    return {'title': 'P', 'body': '[[node:n0]] [[node:n1]] ' + (token + ' ') * (words - 3),
            'bibliography': []}


def install(calls, provider, monkeypatch, sizes, revision_size=1000):
    calls.config['essay_min_words'] = 4500
    calls.config['token_cap'] = 10_000_000
    seen = []
    def complete(kind, prompt, schema, maximum):
        data = json.loads(prompt.split('\nINPUT_JSON\n')[1])
        seen.append((kind, data))
        if kind == 'outline_essay':
            result = plan()
        else:
            assert kind == 'write_essay' and data['mode'] in ('section', 'expand', 'condense')
            index = int(data['section']['id'][1:])
            result = section(sizes[index] if data['mode'] == 'section' else revision_size, ['P', 'Q', 'R', 'S', 'F(x)'][index])
        return Response(response(result))
    monkeypatch.setattr(provider, 'complete', complete)
    return seen


def test_section_assembly_preserves_order_and_logged_context(rig, monkeypatch):
    calls, provider, log = rig
    seen = install(calls, provider, monkeypatch, [1000] * 5)
    draft = calls.write_essay(route())
    assert word_count(draft) == 5001
    assert draft['body'] == '\n\n'.join('P\n\n' + section(1000, token)['body'] for token in ['P', 'Q', 'R', 'S', 'F(x)'])
    assert len(seen) == 6
    assert [len(data['previous_sections']) for _, data in seen[1:]] == list(range(5))
    assert all(data['section_plan'] == plan() for _, data in seen[1:])
    assert all(data['outline'] == calls.essay_outline(route()) for _, data in seen)
    assert len([e for e in log.read() if e['label'] == 'MODEL']) == 6
    assert any(e['stage'] == 'essay_section_plan' for e in log.read())


def test_expansion_targets_largest_deficit_and_keeps_accepted_sections(rig, monkeypatch):
    calls, provider, log = rig
    seen = install(calls, provider, monkeypatch, [1000, 200, 1000, 1000, 1000])
    draft = calls.write_essay(route())
    assert word_count(draft) == 5200
    bodies = ['P\n\n' + section(1000, token)['body'] for token in ['P', 'Q', 'R', 'S', 'F(x)']]
    bodies[1] = 'P\n\n' + section(200, 'Q')['body'] + '\n\n' + section(1000, 'Q')['body']
    assert draft['body'] == '\n\n'.join(bodies)
    revisions = [data for _, data in seen if data.get('mode') == 'expand']
    assert len(revisions) == 1 and revisions[0]['section']['id'] == 's1'
    assert revisions[0]['current_section'] == section(200, 'Q')
    assert revisions[0]['measured_words'] == 200
    assert revisions[0]['total_words'] == 4201
    assert len([data for _, data in seen if data.get('mode') == 'section']) == 5
    assert any(e['stage'] == 'essay_length_revision' for e in log.read())


def test_condensation_keeps_other_sections(rig, monkeypatch):
    calls, provider, _ = rig
    seen = install(calls, provider, monkeypatch, [1700, 1000, 1200, 1200, 1200])
    draft = calls.write_essay(route())
    assert word_count(draft) == 5601
    revisions = [data for _, data in seen if data.get('mode') == 'condense']
    assert len(revisions) == 1 and revisions[0]['section']['id'] == 's0'


def test_small_additions_exhaust_three_rounds_without_regeneration(rig, monkeypatch):
    calls, provider, log = rig
    seen = install(calls, provider, monkeypatch, [200] * 5, revision_size=5)
    with pytest.raises(Rejected, match='minimum words'):
        calls.write_essay(route())
    revisions = [data for _, data in seen if data.get('mode') == 'expand']
    assert len(revisions) == 15 and {r['round'] for r in revisions} == {1, 2, 3}
    assert not any(e['stage'] in ('essay_audit', 'final_draft') for e in log.read())


def test_outline_budget_rejected_before_sections(rig, monkeypatch):
    calls, provider, log = rig
    calls.config['essay_min_words'] = 4500
    bad = plan()
    for s in bad['sections']:
        s['word_budget'] = 800
    monkeypatch.setattr(provider, 'complete', lambda *args: Response(response(bad)))
    with pytest.raises(Rejected, match='section budgets'):
        calls.write_essay(route())
    assert all(e['stage'] == 'outline_essay' for e in log.read() if e['label'] == 'MODEL')


def seed_sources(calls, log, *, local_pages=None, local_hash=None):
    from dataclasses import replace
    from ara.runtime.cache import canonical
    from ara.runtime.extraction import HEADER
    from ara.runtime.grounding import POLICY, receipt_hash
    from ara.runtime.frozen_catalogue import frozen_artifact
    from ara.runtime.commitment_provenance import make_commitment_provenance, source_provenance
    from ara.types import Commitment, CommitmentSet, Formula
    from rich_fixture import graph
    items = graph()['items']
    for i in items:
        i['citation'] = 'p:pdf:1#' + i['id']
    paper = dict(source_id='p', status='partial', items=items, quarantined=[],
                 open_gaps=[dict(description='Q', pages=[1])], resolutions=[])
    paper['grounding'] = dict(policy=POLICY, source_text_sha256='P',
        inventory_sha256=receipt_hash(items, [], 'P'))
    if local_pages is not None:
        from ara.runtime.cache import digest
        paper['pdf_sha256'] = 'a' * 64
        page_hash = local_hash or digest(canonical({1: local_pages}))
        paper['grounding'].update(source_text_sha256=page_hash,
                                 inventory_sha256=receipt_hash(items, [], page_hash))
    commitments = CommitmentSet(tuple(Commitment(i['id'], i['text'], i['citation'], Formula('atom', name=n))
                                     for i, n in zip(items[:2], ['P', 'Q'])))
    artifact = frozen_artifact(commitments, [dict(name=n, kind='atom', arity=0, definition=n,
        evidence_ids=[i['id']]) for i, n in zip(items[:2], ['P', 'Q'])])
    provenance = make_commitment_provenance(commitments, artifact['symbol_catalogue'],
        {i['id']: source_provenance(i, ['a'], ['i']) for i in items[:2]})
    directory = log.path.parent
    (directory / 'frozen-t.json').write_text(canonical(artifact))
    (directory / 'commitment-provenance.json').write_text(canonical(provenance))
    log.record('run_started', literature=HEADER + canonical(dict(papers=[paper])))
    if local_pages is not None:
        from ara.types import RunEvent
        from ara.runtime.logging import now
        record = dict(id='p', authors='a', year=2000, title='P', venue='Q', open_access_url=None)
        inputs = dict(source_id='p', pdf_sha256='a' * 64, record=record,
                      pages=[dict(page=1, text=local_pages)])
        log.emit(RunEvent(now(), 'extract_paper', 'MODEL', prompt='INPUT_JSON\n' + canonical(inputs),
            payload_json=canonical(dict(source_id='p', status='accepted', cache_hit=False, cache_key='P'))))
    log.record('symbol_catalogue_frozen', **artifact['symbol_catalogue'])
    log.record('commitment_provenance_frozen', **provenance)
    log.record('commitments_frozen', commitments=commitments.to_dict())
    r = route()
    return replace(r, nodes=tuple(replace(n, t_id=tid) for n, tid in zip(r.nodes, ['p', 'q'])))


def test_exact_evidence_context_and_citations_reach_writer_and_audit(rig, monkeypatch):
    from ara.runtime.writing import source_context
    calls, provider, log = rig
    r = seed_sources(calls, log)
    seen = install(calls, provider, monkeypatch, [1000] * 5)
    complete = provider.complete
    def cite(kind, prompt, schema, maximum):
        raw = complete(kind, prompt, schema, maximum)
        if kind == 'write_essay':
            draft = json.loads(raw.text())
            draft['body'] += ' [cite:p] [cite:q]'
            draft['bibliography'] = [dict(id=tid, text='p:pdf:1#' + tid, url=None) for tid in ['p', 'q']]
            return Response(response(draft))
        return raw
    monkeypatch.setattr(provider, 'complete', cite)
    draft = calls.write_essay(r)
    evidence = source_context(calls, r)
    assert seen[0][1]['source_evidence'] == evidence
    assert all(data['source_evidence'] == evidence for _, data in seen)
    assert calls.audit_inputs(r, draft)['source_evidence'] == evidence
    assert len(draft['bibliography']) == 2
    first = evidence['supporting_commitments'][0]
    assert first['commitment']['citation'] == 'p:pdf:1#p'
    assert first['provenance']['source_text'] == 'P P P'
    assert first['provenance']['attributed_to'] == 'a'
    assert first['provenance']['page_start'] == first['provenance']['page_end'] == 1
    assert evidence['disclosed_limits']['omitted_support_ids'] == ['i']
    assert all(len(p['items']) == 6 and p['omitted_item_count'] == 1 for p in evidence['paper_context'])
    assert all(p['open_gaps'] == [dict(description='Q', pages=[1])] for p in evidence['paper_context'])
    assert any(i['id'] == 'i' for i in evidence['paper_context'][0]['items'])


@pytest.mark.parametrize('bad', ['unknown', 'citation_text', 'missing'])
def test_section_cannot_invent_or_drop_source_citations(rig, monkeypatch, bad):
    calls, provider, log = rig
    r = seed_sources(calls, log)
    install(calls, provider, monkeypatch, [1000] * 5)
    complete = provider.complete
    def invalid(kind, prompt, schema, maximum):
        raw = complete(kind, prompt, schema, maximum)
        if kind == 'write_essay':
            draft = json.loads(raw.text())
            if bad != 'missing':
                ids = ['p', 'q', 'z'] if bad == 'unknown' else ['p', 'q']
                draft['body'] += ''.join(f' [cite:{tid}]' for tid in ids)
                draft['bibliography'] = [dict(id=tid, text='p:pdf:1#' + tid, url=None) for tid in ids]
                if bad == 'citation_text':
                    draft['bibliography'][0]['text'] = 'Q'
            return Response(response(draft))
        return raw
    monkeypatch.setattr(provider, 'complete', invalid)
    with pytest.raises(Rejected, match='citation'):
        calls.write_essay(r)
    assert not any(e['stage'] == 'essay_assembled' for e in log.read())


def test_sectioned_compose_still_stops_at_adverse_audit(rig, monkeypatch):
    from ara.runtime.orchestration import compose
    calls, provider, log = rig
    install(calls, provider, monkeypatch, [1000] * 5)
    complete = provider.complete
    def adverse(kind, prompt, schema, maximum):
        if kind == 'revise_essay':
            inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
            return Response(response({'revisions': [dict(sentence=s['sentence'], text=s['text'])
                                                   for s in inputs['flagged_sentences']]}))
        if kind == 'audit_essay':
            inputs = json.loads(prompt.split('\nINPUT_JSON\n')[1])
            return Response(response({'labels': [dict(sentence=s['sentence'], node_ids=['n0', 'n1'],
                role='unsupported_claim', citation_supported=True) for s in inputs['sentences']]}))
        return complete(kind, prompt, schema, maximum)
    monkeypatch.setattr(provider, 'complete', adverse)
    with pytest.raises(Rejected, match='audit failed'):
        compose(calls, route())
    assert (log.path.parent / 'draft.unverified.json').exists()
    assert not (log.path.parent / 'draft.json').exists()
    assert any(e['stage'] == 'essay_audit' for e in log.read())
    assert not any(e['stage'] in ('search_evidence', 'final_draft') for e in log.read())


@pytest.mark.parametrize('kind', ['outline_essay', 'revise_essay'])
def test_outline_uses_writing_stage_configuration(kind):
    from ara.runtime.providers import stage_settings
    assert stage_settings({'model': 'P', 'stages': {'writing': {'model': 'Q'}, 'search': {'model': 'R'}}},
                          kind)['model'] == 'Q'
