"""Placeholder-only offline OCR fallback and native extraction controls."""
from dataclasses import replace
from hashlib import sha256
import json
import os
from pathlib import Path
import socket

import pytest

from ara.runtime.cache import canonical
from ara.runtime.extraction import PageDiagnostic, PageText, extract, load_papers, literature_entry, validate_reused_paper
from ara.runtime.ocr import (OCRResult, decision, recover_papers, verify_models, offline_network,
                             LocalOCR, ENGINE, VERSION)
from test_extraction import rig, register, VALUE, ITEM, pdf


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError('network forbidden')
    monkeypatch.setattr(socket.socket, 'connect', refuse)
    monkeypatch.setattr(socket.socket, 'connect_ex', refuse)


class FakeOCR:
    identity = dict(engine=ENGINE, version=VERSION, weights_sha256='a' * 64)

    def __init__(self, result=None):
        self.result = result or OCRResult(('P Q R F(x)',), (0.99,))
        self.seen = []

    def recognize(self, raw, page):
        self.seen.append(page)
        return self.result


def flagged(rig, reason='private_use_glyphs', text='P Q R F(x)\ue001'):
    calls, provider, papers, manifest, fulltext, _ = rig
    paper = replace(papers[0], pages=(papers[0].pages[0], PageText(2, text)),
                    diagnostics=(PageDiagnostic(2, reason, len(text)),))
    return calls, provider, paper, fulltext


def test_recovery_preserves_healthy_page_and_physical_citations(rig):
    calls, provider, paper, fulltext = flagged(rig)
    engine = FakeOCR()
    recovered = recover_papers((paper,), fulltext, calls.log, Path('unused'), engine=engine)[0]
    assert engine.seen == [2]
    assert recovered.pages[0] is paper.pages[0]
    assert recovered.pages[1] == PageText(2, 'P Q R F(x)')
    assert recovered.affected_pages == ()
    register(calls, provider, recovered, {**VALUE, 'items': [{**ITEM, 'page_start': 2, 'page_end': 2}]})
    path = extract(calls, (recovered,), missing='refuse')
    assert 'p:pdf:2#' in path.read_text()
    outcome = json.loads(next(e['payload_json'] for e in calls.log.read() if e['stage'] == 'extraction_outcome'))
    assert outcome['status'] == 'extracted'
    provenance = literature_entry(outcome)['ocr_provenance'][0]
    assert provenance['selected'] == 'ocr' and provenance['engine'] == ENGINE
    assert provenance['version'] == VERSION and provenance['weights_sha256'] == 'a' * 64
    assert provenance['original_diagnostics'][0]['reason'] == 'private_use_glyphs'
    assert 'seconds' not in recovered.inputs()['ocr_provenance'][0]
    with pytest.raises(ValueError, match='OCR provenance'):
        validate_reused_paper(recovered, {k:v for k,v in outcome.items() if k != 'ocr_provenance'}, outcome['acceptance_identity'])


@pytest.mark.parametrize('reason,text', [('private_use_glyphs','P\ue001'), ('sparse_image_text',''),
                                        ('nontext_visual_content',''), ('encoding_warning','P\ufffd')])
def test_low_confidence_stays_partial_and_strict_refuses(rig, reason, text):
    calls, provider, paper, fulltext = flagged(rig, reason, text)
    engine = FakeOCR(OCRResult(('P Q R',), (0.4,)))
    recovered = recover_papers((paper,), fulltext, calls.log, Path('unused'), engine=engine)[0]
    assert recovered.affected_pages == (2,)
    assert recovered.pages == paper.pages
    assert json.loads(recovered.ocr_provenance_json)[0]['selected'] == 'text_layer'
    with pytest.raises(ValueError, match='partial text coverage'):
        extract(calls, (recovered,), missing='refuse')
    assert provider.calls == 0


@pytest.mark.parametrize('original,lines,scores', [
    ('P', ('P',), (0.94,)), ('P Q R S', ('P',), (0.99,)),
    ('F(x) = P', ('F(x) Q P',), (0.99,)), ('P', ('P\ue001',), (0.99,)),
    ('P', ('P\ufffd',), (0.99,)), ('P', (), ()),
    ('placeholder retained', ('placeholder different',), (0.99,)),
    ('P', ('P'*90,'Q'*10), (1.0,0.79)),
])
def test_rejects_uncertain_or_lossy_ocr(original, lines, scores):
    assert not decision(original, OCRResult(lines, scores))['recovered']


@pytest.mark.parametrize('scores', [(float('nan'),), (float('inf'),), (-0.1,), (1.01,), ()])
def test_malformed_confidence_refused(scores):
    with pytest.raises(ValueError):
        OCRResult(('P',), scores)


def test_healthy_only_never_initializes_ocr(rig, monkeypatch):
    import ara.runtime.ocr as module
    calls, _, papers, _, fulltext, _ = rig
    def fail(*args): raise AssertionError('OCR must stay lazy')
    monkeypatch.setattr(module, 'LocalOCR', fail)
    assert recover_papers(papers, fulltext, calls.log, Path('unused')) == papers


def test_operational_error_is_logged_and_not_swallowed(rig):
    calls, _, paper, fulltext = flagged(rig)
    class Broken(FakeOCR):
        def recognize(self, *args): raise RuntimeError('P')
    with pytest.raises(ValueError, match='local OCR failed'):
        recover_papers((paper,), fulltext, calls.log, Path('unused'), engine=Broken())
    events = calls.log.read()
    assert events[-1]['stage'] == 'extraction_ocr_error'
    assert not any(e['stage'] == 'extraction_ocr_page' for e in events)


def test_pdf_changed_after_intake_refused(rig):
    calls, _, paper, fulltext = flagged(rig)
    (fulltext / 'p.pdf').write_bytes(b'P')
    engine = FakeOCR()
    with pytest.raises(ValueError, match='local OCR failed'):
        recover_papers((paper,), fulltext, calls.log, Path('unused'), engine=engine)
    assert engine.seen == []


def test_hash_verification_rejects_missing_and_tampered_weights(tmp_path):
    lock = {'P': {'files': {'P.bin': sha256(b'P').hexdigest()}}}
    with pytest.raises(ValueError, match='hash mismatch'): verify_models(tmp_path, lock)
    (tmp_path / 'P.bin').write_bytes(b'P')
    verify_models(tmp_path, lock)
    (tmp_path / 'P.bin').write_bytes(b'Q')
    with pytest.raises(ValueError, match='hash mismatch'): verify_models(tmp_path, lock)


def test_network_guard_denies_connections_and_restores():
    original = socket.socket.connect
    with offline_network():
        with socket.socket() as connection:
            with pytest.raises(RuntimeError, match='network access forbidden'):
                connection.connect(('127.0.0.1', 1))
    assert socket.socket.connect is original


def test_cli_defaults_to_local_before_provider_and_strict_policy(rig, monkeypatch, tmp_path):
    from ara.runtime.cli import main
    import ara.runtime.ocr as module
    from pypdf._page import PageObject
    calls, provider, _, manifest, fulltext, config = rig
    monkeypatch.setattr(PageObject, 'extract_text', lambda *a, **kw: 'P\ue001')
    engine = FakeOCR(OCRResult(('P',), (0.2,)))
    monkeypatch.setattr(module, 'LocalOCR', lambda cache: engine)
    def factory(config, log, topic):
        calls.log = log
        return calls
    assert main(['extract', '--manifest', str(manifest), '--fulltext-dir', str(fulltext),
                 '--config', str(config), '--run-dir', str(tmp_path/'cli'), '--missing', 'refuse'],
                calls_factory=factory) == 2
    assert engine.seen == [1, 2] and provider.calls == 0
    assert any(e['stage'] == 'extraction_ocr_page' for e in calls.log.read())


@pytest.mark.skipif(os.environ.get('ARA_TEST_LOCAL_OCR') != '1', reason='opt-in installed local weights')
def test_local_ocr_synthetic_raster_pdf(tmp_path):
    from PIL import Image, ImageDraw
    from ara.runtime.logging import EventLog
    image = Image.new('RGB', (1000, 1000), 'white')
    ImageDraw.Draw(image).text((80, 80), 'P Q R S F(x)', fill='black', font_size=36)
    image.save(tmp_path/'p.pdf', 'PDF', resolution=100)
    manifest = tmp_path/'manifest.yaml'
    manifest.write_text('- id: p\n  fulltext: fulltext/p.pdf\n')
    papers = load_papers(manifest, tmp_path)
    assert papers[0].affected_pages == (1,)
    log = EventLog(tmp_path/'run/events.jsonl')
    recovered = recover_papers(papers, tmp_path, log, Path(os.environ.get('ARA_OCR_CACHE', 'cache/ocr')))
    assert recovered[0].affected_pages == ()
    assert all(c in recovered[0].pages[0].text for c in 'PQRS')
    assert json.loads(recovered[0].ocr_provenance_json)[0]['selected'] == 'ocr'


def test_genuinely_blank_page_keeps_native_classification(rig):
    calls, _, paper, fulltext = flagged(rig, 'blank_page', '')
    recovered = recover_papers((paper,), fulltext, calls.log, Path('unused'), engine=FakeOCR(OCRResult((), ())))[0]
    assert recovered.affected_pages == ()
    assert recovered.diagnostics == paper.diagnostics
    assert not json.loads(recovered.ocr_provenance_json)[0]['recovered']


def test_high_confidence_cannot_hide_small_readable_text_loss():
    original = ' '.join(['placeholder'] * 100)
    result = OCRResult((' '.join(['placeholder'] * 97),), (0.999,))
    assert not decision(original, result)['recovered']
