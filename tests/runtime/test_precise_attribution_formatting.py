"""Report frames remain excluded when emphasis or punctuation separates words."""
import json
from dataclasses import replace

import pytest

from ara.runtime.calls import Rejected
from ara.runtime.providers import Response
from ara.runtime.commitment_provenance import content_definition, PRECISE_SCREEN
from test_construction_recovery import setup, freeze
from test_extraction import rig, response

FRAMES = ['b holds **that** P', 'b states *that* P', 'b maintains: that P',
          'b holds _that_ P', 'b states `that` P', 'b maintains — that P',
          'b holds, that P', 'b maintains; that P',
          'b holds <em>that</em> P', 'b states <strong>that</strong> P',
          'b maintains &quot;that&quot; P', 'b h&#111;lds <em>th&#97;t</em> P',
          'b h**olds** th**at** P', 'b holds<br>that P',
          'b holds &lt;em&gt;that&lt;/em&gt; P', 'b <holds> that P',
          '![b h**olds** th**at** P](https://example.invalid/p.png)',
          'b ![h**olds**](https://example.invalid/p.png) th**at** P',
          '![b ![h**olds**](P) th**at** P](Q)',
          'b <img alt="h&#111;lds" src="P"> that P']


@pytest.mark.parametrize('text', FRAMES)
def test_formatted_report_frame_never_freezes(rig, monkeypatch, text):
    calls, provider, literature, _ = setup(rig, monkeypatch)
    calls.config.update(construction_precise_attribution=True, construction_targeted_corrections=0)
    complete = provider.complete
    def respond(kind, prompt, schema, maximum):
        value = json.loads(complete(kind, prompt, schema, maximum).text())
        if kind == 'build_t_batch':
            for row in value['commitments'] + value['new_symbols']:
                row['definition'] = text
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', respond)
    with pytest.raises(Rejected, match='content definition'):
        freeze(calls, literature)
    assert not (calls.log.path.parent/'commitments.json').exists()


@pytest.mark.parametrize('text', FRAMES)
def test_formatted_report_frame_rejected_when_loading_metadata(text):
    from ara.runtime.commitment_provenance import make_commitment_provenance, validate_commitment_provenance
    from ara.runtime.frozen_catalogue import make_catalogue
    from ara.runtime.cache import canonical, digest
    from ara.types import CommitmentSet
    from test_symbol_alignment import fixture
    t, symbols, rows = fixture()
    for row in rows.values(): row['definition_screen'] = PRECISE_SCREEN
    meta = make_commitment_provenance(t, make_catalogue(t,symbols), rows)
    changed = CommitmentSet(tuple(replace(c,text=text) for c in t.commitments))
    changed_symbols = [dict(s,definition=text) for s in symbols]
    catalogue = make_catalogue(changed, changed_symbols)
    meta.update(commitments_sha256=catalogue['commitments_sha256'],catalogue_sha256=catalogue['sha256'])
    meta['sha256'] = digest(canonical({k:v for k,v in meta.items() if k!='sha256'}))
    with pytest.raises(ValueError, match='content definition'):
        validate_commitment_provenance(meta,changed,catalogue)


@pytest.mark.parametrize('text', ['P holds', 'P and Q hold', 'P states are Q',
    'P maintains Q', 'P holds. That Q holds is R.',
    'P <em>holds</em>', 'P <span>states</span> are Q',
    'P &lt; Q', 'P holds.<br>That Q holds is R.'])
def test_ordinary_state_predication_stays_content(text):
    assert content_definition(text,screen=PRECISE_SCREEN)


def test_markup_screen_never_rewrites_accepted_definitions_or_source(rig, monkeypatch):
    from ara.runtime.extraction import HEADER
    from ara.runtime.commitment_provenance import load_commitment_provenance
    calls, provider, literature, _ = setup(rig, monkeypatch)
    calls.config['construction_precise_attribution'] = True
    source = {i['id']:i['text'] for p in json.loads(literature[len(HEADER):])['papers'] for i in p['items']}
    definition = 'P <em>holds</em>'
    complete = provider.complete
    def respond(kind, prompt, schema, maximum):
        value = json.loads(complete(kind, prompt, schema, maximum).text())
        if kind == 'build_t_batch':
            for row in value['commitments'] + value['new_symbols']:
                row['definition'] = definition
        return Response(response(value))
    monkeypatch.setattr(provider, 'complete', respond)
    result = freeze(calls, literature)
    catalogue = json.loads((calls.log.path.parent/'frozen-t.json').read_text())['symbol_catalogue']
    metadata = load_commitment_provenance(calls.log.path.parent,result,catalogue)
    assert all(c.text == definition for c in result.commitments)
    assert all(s['definition'] == definition for s in catalogue['symbols'])
    assert all(row['source_text'] == source[id] for id,row in metadata['commitments'].items())


@pytest.mark.parametrize('text', ['![P](https://example.invalid/p.png)',
    '<img alt="P" src="https://example.invalid/p.png">',
    '![P][a]\n\n[a]: https://example.invalid/p.png', '![P ![Q](R)](S)'])
def test_images_have_explicit_content_boundary_reason(text):
    from ara.runtime.commitment_provenance import definition_issues
    assert not content_definition(text,screen=PRECISE_SCREEN)
    issues = definition_issues(dict(commitments=[dict(id='P',definition=text)],new_symbols=[]),screen=PRECISE_SCREEN)
    assert issues[0]['reason'] == 'image markup is not supported in content definitions'
