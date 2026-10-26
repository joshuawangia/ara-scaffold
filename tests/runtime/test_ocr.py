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
        self.result = result or OCRResult(('P Q ∀ R F(x)',), (0.99,))
        self.seen = []

    def recognize(self, raw, page):
        self.seen.append(page)
        return self.result


def flagged(rig, reason='private_use_glyphs', text='P Q \ue001 R F(x)'):
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
    assert recovered.pages[1] == PageText(2, 'P Q ∀ R F(x)')
    assert recovered.affected_pages == ()
    register(calls, provider, recovered, {**VALUE, 'items': [{**ITEM, 'page_start': 2, 'page_end': 2}]})
    path = extract(calls, (recovered,), missing='refuse')
    assert 'p:pdf:2#' in path.read_text()
    outcome = json.loads(next(e['payload_json'] for e in calls.log.read() if e['stage'] == 'extraction_outcome'))
    assert outcome['status'] == 'extracted'
    provenance = literature_entry(outcome)['ocr_provenance'][0]
    assert provenance['selected'] == 'ocr_spans' and provenance['engine'] == ENGINE
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
    recovered = recover_papers((paper,), fulltext, calls.log, Path('unused'), engine=engine, vl_engine=FakeOCR(engine.result))[0]
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
    import ara.runtime.ocr_vl as vl_module
    monkeypatch.setattr(vl_module, 'LocalVLOCR', lambda cache: FakeOCR(engine.result))
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


@pytest.mark.parametrize('glyph', ['\ue001', '\ufffd', '\x01'])
def test_damaged_spans_do_not_create_trusted_word_fragments(glyph):
    result = decision('PP' + glyph + 'QQ RR', OCRResult(('SSSS RR',), (0.99,)))
    assert result['retained_token_share'] == 1.0
    assert result['clean_original_tokens'] == 1
    assert result['excluded_original_spans'] == 1
    assert result['recovered']


def test_clean_word_loss_still_refuses_after_damaged_span_exclusion():
    result = decision('PP\ue001QQ RR', OCRResult(('SSSS TT',), (0.99,)))
    assert result['retained_token_share'] == 0.0
    assert not result['recovered']


def test_character_floor_is_not_removed_with_untrusted_words():
    result = decision('PP\ue001QQ RR', OCRResult(('RR',), (0.99,)))
    assert result['retained_token_share'] == 1.0
    assert result['character_ratio'] < 0.98
    assert not result['recovered']


def test_literal_math_inside_damaged_span_remains_required():
    result = decision('P\ue001=Q', OCRResult(('P R Q',), (0.99,)))
    assert result['missing_math_symbols'] == 1
    assert not result['recovered']


@pytest.mark.parametrize('original,rendered', [('P ∀ Q', r'P \forall Q'),
                                             ('P ⊭ Q', r'P \not\models Q')])
def test_standard_latex_is_an_encoding_of_the_same_math_symbol(original, rendered):
    assert decision(original, OCRResult((rendered,), (0.99,)))['recovered']


def test_unknown_latex_cannot_supply_a_required_math_symbol():
    assert not decision('P ∀ Q', OCRResult((r'P \unknown Q',), (0.99,)))['recovered']


class FakeVL(FakeOCR):
    identity = dict(engine='PaddleOCR-VL', version='1.6', weights_sha256='b' * 64)


def test_second_tier_recovers_only_rejected_physical_page(rig):
    calls, provider, paper, fulltext = flagged(rig)
    tiny = FakeOCR(OCRResult(('P',), (0.4,)))
    vl = FakeVL()
    updated = recover_papers((paper,), fulltext, calls.log, Path('unused'), engine=tiny, vl_engine=vl)[0]
    assert tiny.seen == vl.seen == [2]
    assert updated.pages[0] is paper.pages[0]
    assert updated.pages[1] == PageText(2, 'P Q ∀ R F(x)')
    assert not updated.affected_pages
    register(calls, provider, updated, {**VALUE, 'items': [{**ITEM, 'page_start': 2, 'page_end': 2}]})
    path = extract(calls, (updated,), missing='refuse')
    assert 'p:pdf:2#' in path.read_text()
    records = json.loads(updated.ocr_provenance_json)
    assert [(r['tier'], r['engine'], r['recovered']) for r in records] == [
        (1, ENGINE, False), (2, 'PaddleOCR-VL', True)]
    assert records[-1]['weights_sha256'] == 'b' * 64
    assert 'seconds' not in records[-1]


def test_second_tier_is_skipped_after_tier1_acceptance(rig):
    calls, _, paper, fulltext = flagged(rig)
    vl = FakeVL()
    updated = recover_papers((paper,), fulltext, calls.log, Path('unused'), engine=FakeOCR(), vl_engine=vl)[0]
    assert vl.seen == []
    assert len(json.loads(updated.ocr_provenance_json)) == 1


def test_second_tier_uses_same_gate_and_keeps_rejected_text(rig):
    calls, provider, paper, fulltext = flagged(rig)
    low = OCRResult(('P Q ∀ R F(x)',), (0.94,))
    updated = recover_papers((paper,), fulltext, calls.log, Path('unused'), engine=FakeOCR(low), vl_engine=FakeVL(low))[0]
    assert updated.affected_pages == (2,) and updated.pages == paper.pages
    assert not any(r['recovered'] for r in json.loads(updated.ocr_provenance_json))
    with pytest.raises(ValueError, match='partial text coverage'):
        extract(calls, (updated,), missing='refuse')
    assert provider.calls == 0


def test_second_tier_operational_failure_is_not_swallowed(rig):
    calls, _, paper, fulltext = flagged(rig)
    class BrokenVL(FakeVL):
        def recognize(self, *args): raise RuntimeError('P')
    with pytest.raises(ValueError, match='local OCR failed'):
        recover_papers((paper,), fulltext, calls.log, Path('unused'),
                       engine=FakeOCR(OCRResult(('P',), (0.1,))), vl_engine=BrokenVL())
    assert calls.log.read()[-1]['stage'] == 'extraction_ocr_error'


def test_explicit_tier1_only_does_not_initialize_vl(rig, monkeypatch):
    import ara.runtime.ocr_vl as module
    calls, _, paper, fulltext = flagged(rig)
    def forbidden(*args):raise AssertionError('VL is disabled')
    monkeypatch.setattr(module, 'LocalVLOCR', forbidden)
    updated = recover_papers((paper,), fulltext, calls.log, Path('unused'),
                             engine=FakeOCR(OCRResult(('P',), (0.2,))), use_vl=False)[0]
    assert updated.affected_pages == (2,)


class PlaceholderTokenizer:
    all_special_ids = [0]
    def decode(self, ids, **kwargs):
        return ''.join({0:'', 1:'P', 2:' Q', 3:' R'}[i] for i in ids)


def test_vl_generation_records_actual_probabilities_and_eos():
    from ara.runtime.ocr_vl import generation_result
    result = generation_result(PlaceholderTokenizer(), [1, 2, 0], [0.99, 0.2, 1.0], (0,))
    assert result.complete and result.text == 'P Q'
    assert result.confidence < 0.95 and result.low_confidence_share > 0.05
    assert result.confidence_basis == 'generated_token_probabilities'
    assert not decision('P Q', result)['recovered']
    assert json.loads(result.generation_json)['terminal_token_id'] == 0


def test_vl_truncation_is_not_recovery_even_with_high_confidence():
    from ara.runtime.ocr_vl import generation_result
    result = generation_result(PlaceholderTokenizer(), [1, 2], [0.999, 0.999], (0,))
    assert result.confidence > 0.95
    assert not decision('P Q', result)['recovered']


def test_vl_weight_hash_rejects_tampering(tmp_path):
    from ara.runtime.ocr_vl import verify_vl_model
    lock = {'files': {'P.bin': {'sha256': sha256(b'P').hexdigest()}}}
    root = tmp_path / 'PaddleOCR-VL-1.6'
    with pytest.raises(ValueError, match='VL model missing'):verify_vl_model(tmp_path, lock)
    root.mkdir();(root/'P.bin').write_bytes(b'P')
    assert verify_vl_model(tmp_path, lock) == root
    (root/'P.bin').write_bytes(b'Q')
    with pytest.raises(ValueError, match='hash mismatch'):verify_vl_model(tmp_path, lock)


@pytest.mark.skipif(os.environ.get('ARA_TEST_LOCAL_VL') != '1', reason='opt-in installed VL weights')
def test_local_vl_synthetic_image_pdf(tmp_path):
    from PIL import Image, ImageDraw
    from ara.runtime.ocr_vl import LocalVLOCR
    image = Image.new('RGB', (700, 700), 'white')
    ImageDraw.Draw(image).text((80, 80), 'P Q R S F(x)', fill='black', font_size=36)
    image.save(tmp_path/'p.pdf', 'PDF', resolution=150)
    result = LocalVLOCR(Path(os.environ.get('ARA_OCR_CACHE', 'cache/ocr'))).recognize((tmp_path/'p.pdf').read_bytes(), 1)
    assert result.complete
    assert all(c in result.text for c in 'PQRS')
    assert result.confidence < 0.95 and result.low_confidence_share > 0.05
    assert not decision('', result)['recovered']



def test_empty_vl_response_is_unrecovered_not_an_operational_error():
    from ara.runtime.ocr_vl import generation_result
    result = generation_result(PlaceholderTokenizer(), [0], [0.99], (0,))
    assert result.complete and result.text == ''
    assert result.confidence == 0.0
    assert not decision('P Q', result)['recovered']



def test_cli_tier1_only_reaches_strict_policy_without_vl(rig, monkeypatch, tmp_path):
    from ara.runtime.cli import main
    import ara.runtime.ocr as module
    import ara.runtime.ocr_vl as vl_module
    from pypdf._page import PageObject
    calls, provider, _, manifest, fulltext, config = rig
    monkeypatch.setattr(PageObject, 'extract_text', lambda *a, **kw: 'P\ue001')
    monkeypatch.setattr(module, 'LocalOCR', lambda cache: FakeOCR(OCRResult(('P',), (0.2,))))
    def forbidden(*args):raise AssertionError('VL must not initialize')
    monkeypatch.setattr(vl_module, 'LocalVLOCR', forbidden)
    def factory(config, log, topic):
        calls.log = log
        return calls
    assert main(['extract', '--manifest', str(manifest), '--fulltext-dir', str(fulltext),
                 '--config', str(config), '--run-dir', str(tmp_path/'tier1-cli'),
                 '--missing', 'refuse', '--ocr-tiers', '1'], calls_factory=factory) == 2
    outcomes = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'extraction_outcome']
    assert outcomes[-1]['reason'] == 'strict_incomplete_coverage'
    assert provider.calls == 0



def test_latex_control_words_cannot_replace_missing_prose_tokens():
    result = decision('PP', OCRResult((r'\PP',), (0.99,)))
    assert result['retained_token_share'] == 0.0
    assert not result['recovered']


@pytest.mark.parametrize('original,rendered', [('P1 Q', 'P2 Q'), ('P Q', 'P R'), ('P 12', 'P 34')])
def test_clean_alphanumeric_tokens_are_not_reduced_to_latin_fragments(original, rendered):
    result = decision(original, OCRResult((rendered,), (0.999,)))
    assert result['retained_token_share'] < 0.98
    assert not result['recovered']


def test_latex_markup_does_not_hide_a_damaged_original_span():
    result = decision('\\begin{P\ue001}QQ RR', OCRResult(('SSSSSSSSSSSSSSSS RR',), (0.99,)))
    assert result['clean_original_tokens'] == 1
    assert result['retained_token_share'] == 1.0
    assert result['recovered']


@pytest.mark.parametrize('original,rendered', [('P φ Q', r'P \phi Q'), ('P α Q', r'P \alpha Q'),
                                             ('P Γ Q', r'P \Gamma Q')])
def test_standard_latex_greek_preserves_clean_alphanumeric_symbols(original, rendered):
    result = decision(original, OCRResult((rendered,), (0.99,)))
    assert result['retained_token_share'] == 1.0
    assert result['recovered']
