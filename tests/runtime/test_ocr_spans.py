"""Synthetic span repair contracts; no source-paper content."""
from dataclasses import replace
import json
from pathlib import Path

import pytest

from ara.runtime.ocr import OCRResult, recover_papers
from ara.runtime.extraction import PageText
from test_ocr import FakeOCR, FakeVL, flagged
from test_extraction import rig


def repair(original, result):
    from ara.runtime.ocr_spans import repair_spans
    return repair_spans(original, result)


def test_span_repair_keeps_every_clean_character():
    original = 'P,  Q\nR \ue001 S  F(x).'
    text, spans = repair(original, OCRResult(('P, Q R ∀ S F(x). LOST',), (0.99,)))
    assert text == 'P,  Q\nR ∀ S  F(x).'
    assert spans[0]['accepted'] and spans[0]['anchor_match']['unique']
    assert spans[0]['before_classes']['Co'] == 1
    assert spans[0]['after_classes']['Sm'] == 1


def test_anchor_ambiguity_refuses():
    original = 'P Q R \ue001 S F x'
    text, spans = repair(original, OCRResult(('P Q R ∀ S F x P Q R ∃ S F x',), (0.99,)))
    assert text == original and not spans[0]['accepted']
    assert spans[0]['reason'] == 'anchor_not_unique'


def test_local_low_confidence_refuses_even_when_page_mean_is_high():
    original = 'P Q R \ue001 S F x'
    result = OCRResult(('P Q R', '∀', 'S F x' + ' Z' * 100), (0.999, 0.4, 0.999))
    assert result.confidence > 0.95
    text, spans = repair(original, result)
    assert text == original and spans[0]['reason'] == 'low_confidence'


@pytest.mark.parametrize('original', ['\ue001 P Q R', 'P Q R \ufffd', 'P Q \ue001 \ue002 R S'])
def test_missing_clean_anchor_refuses(original):
    text, spans = repair(original, OCRResult(('P Q R S',), (0.99,)))
    assert text == original and all(not s['accepted'] for s in spans)


@pytest.mark.parametrize('glyph', ['\ue001', '\ufffd', '\x01'])
def test_encoding_warning_runs_are_repaired(glyph):
    text, spans = repair('P Q ' + glyph + ' R S', OCRResult(('P Q ∀ R S',), (0.99,)))
    assert text == 'P Q ∀ R S' and spans[0]['accepted']


def test_clean_page_is_unchanged_by_different_ocr():
    assert repair('P  Q\nR', OCRResult(('S',), (1.0,))) == ('P  Q\nR', [])


def test_empty_or_incomplete_insertion_refuses():
    for result in [OCRResult(('P Q R S',), (1.0,)), OCRResult(('P Q ∀ R S',), (1.0,), complete=False)]:
        text, spans = repair('P Q \ue001 R S', result)
        assert text == 'P Q \ue001 R S' and not spans[0]['accepted']


def test_two_tiers_repair_remaining_spans_without_overwriting_first(rig):
    calls, _, paper, fulltext = flagged(rig, text='P Q \ue001 R S F \ue002 x a')
    one = FakeOCR(OCRResult(('P Q ∀ R S F', '∃', 'x a'), (0.99, 0.2, 0.99)))
    two = FakeVL(OCRResult(('P Q ∃ R S F ∀ x a',), (0.99,)))
    updated = recover_papers((paper,), fulltext, calls.log, Path('unused'), engine=one, vl_engine=two)[0]
    assert updated.pages[1] == PageText(2, 'P Q ∀ R S F ∀ x a')
    assert not updated.affected_pages
    pages = [json.loads(e['payload_json']) for e in calls.log.read() if e['stage'] == 'extraction_ocr_page']
    spans = [span for page in pages for span in page['span_decisions']]
    assert sum(s['accepted'] for s in spans) == 2
    assert {s['engine'] for s in spans if s['accepted']} == {one.identity['engine'], two.identity['engine']}


def test_partial_span_success_is_retained_and_still_flagged(rig):
    calls, _, paper, fulltext = flagged(rig, text='P Q \ue001 R S F \ue002')
    updated = recover_papers((paper,), fulltext, calls.log, Path('unused'),
                            engine=FakeOCR(OCRResult(('P Q ∀ R S F ∃',), (0.99,))), use_vl=False)[0]
    assert updated.pages[1].text == 'P Q ∀ R S F \ue002'
    assert updated.affected_pages == (2,)
    assert json.loads(updated.ocr_provenance_json)[0]['selected'] == 'ocr_spans'


def test_vl_confidence_ranges_follow_inserted_tokens():
    from ara.runtime.ocr_vl import generation_result
    from test_ocr import PlaceholderTokenizer
    result = generation_result(PlaceholderTokenizer(), [1, 2, 3, 0], [0.99, 0.1, 0.99, 1.0], (0,))
    text, spans = repair('P \ue001 R', result)
    assert text == 'P \ue001 R' and spans[0]['reason'] == 'low_confidence'


def test_sparse_clean_text_is_not_replaced(rig):
    calls, _, paper, fulltext = flagged(rig, reason='sparse_image_text', text='P Q')
    updated = recover_papers((paper,), fulltext, calls.log, Path('unused'),
                            engine=FakeOCR(OCRResult(('P Q R S',), (0.999,))), use_vl=False)[0]
    assert updated.pages == paper.pages and updated.affected_pages == (2,)


def test_clean_punctuation_beside_span_is_preserved():
    text, spans = repair('P Q,  \ue001 (R S)', OCRResult(('P Q, ∀ (R S)',), (0.99,)))
    assert text == 'P Q,  ∀ (R S)' and spans[0]['accepted']


def test_encoded_math_in_tainted_run_is_not_lost():
    text, spans = repair('P Q \ue001= R S', OCRResult(('P Q ∀ R S',), (0.99,)))
    assert text == 'P Q \ue001= R S' and spans[0]['reason'] == 'encoded_symbol_loss'


@pytest.fixture
def fake_image(monkeypatch):
    import sys
    from types import SimpleNamespace
    class Image:
        width = 120
        def __init__(self, height=300): self.height = height
        def convert(self, mode): return self
        def crop(self, box): return Image(box[3] - box[1])
    monkeypatch.setitem(sys.modules, 'numpy', SimpleNamespace(
        asarray=lambda image: SimpleNamespace(mean=lambda axis: [255] * image.height)))
    return Image()


def test_vl_capped_page_retries_tiles_and_preserves_local_confidence(monkeypatch, fake_image):
    import ara.runtime.ocr_vl as module
    from test_ocr import PlaceholderTokenizer
    engine = object.__new__(module.LocalVLOCR)
    seen = []
    def recognize(image):
        seen.append(image.height)
        return module.generation_result(PlaceholderTokenizer(), [1, 2, 3, 0] if len(seen) > 1 else [1, 2],
                                        [0.99, 0.2, 0.99, 1.0] if len(seen) > 1 else [0.99, 0.99], (0,))
    monkeypatch.setattr(module, 'render_page', lambda *args: fake_image)
    engine._recognize_image = recognize
    result = engine.recognize(b'P', 2)
    assert result.complete and seen == [300, 100, 100, 100]
    assert result.text == 'P Q R\nP Q R\nP Q R'
    assert all(any(a <= offset < b and score == 0.2 for a, b, score in result.character_confidences)
               for offset in (2, 8, 14))
    receipt = json.loads(result.generation_json)
    assert not receipt['capped_attempt']['result']['complete']
    assert len(receipt['tiles']) == 3 and all(t['seconds'] >= 0 for t in receipt['tiles'])


def test_tiled_result_refuses_if_any_tile_lacks_eos(fake_image):
    from ara.runtime.ocr_vl import LocalVLOCR
    engine = object.__new__(LocalVLOCR)
    engine._recognize_image = lambda image: OCRResult(('P',), (0.99,), complete=False)
    assert not engine.recognize_tiled(fake_image).complete


def test_adjacent_tainted_spans_share_unique_outer_anchors():
    text, spans = repair('P Q \ue001R S\ue002 F x', OCRResult(('P Q [R S] F x',), (0.99,)))
    assert text == 'P Q [R S] F x' and all(s['accepted'] for s in spans)
    assert len(spans) == 2


def test_cluster_with_different_token_count_refuses():
    text, spans = repair('P Q \ue001 \ue002 F x', OCRResult(('P Q ∀ F x',), (0.99,)))
    assert text == 'P Q \ue001 \ue002 F x'
    assert all(s['reason'] == 'cluster_alignment_ambiguous' for s in spans)


def test_shorter_unique_clean_context_can_anchor():
    text, spans = repair('P Q R \ue001 S F x', OCRResult(('Q R ∀ S F',), (0.99,)))
    assert text == 'P Q R ∀ S F x' and spans[0]['accepted']


def test_tainted_span_count_is_not_changed_by_normalized_clean_whitespace():
    from ara.runtime.ocr import decision
    record = decision('P´Q R \ue001 S', OCRResult(('P Q R ∀ S',), (0.99,)))
    assert record['excluded_original_spans'] == 1


def test_vl_byte_fragments_keep_lowest_contributing_confidence():
    from ara.runtime.ocr_vl import generation_result
    class ByteTokenizer:
        all_special_ids = [0]
        def decode(self, ids, **kwargs):
            text = ''.join({0: '', 1: 'P ', 2: '\ufffd', 3: '\ufffd', 4: ' R'}[i] for i in ids)
            return text.replace('\ufffd\ufffd', '∀')
    result = generation_result(ByteTokenizer(), [1, 2, 3, 4, 0], [0.99, 0.2, 0.999, 0.99, 1.0], (0,))
    text, spans = repair('P \ue001 R', result)
    assert result.text == 'P ∀ R'
    assert text == 'P \ue001 R' and spans[0]['confidence'] == 0.2


@pytest.mark.parametrize('candidate', ['P s] R', 'P Q] R', 'P S R'])
def test_clean_characters_inside_tainted_span_cannot_change(candidate):
    original = 'P S\ue001 R'
    text, spans = repair(original, OCRResult((candidate,), (0.999,)))
    assert text == original and spans[0]['reason'] == 'clean_fragment_changed'


def test_clean_characters_inside_tainted_span_are_retained():
    text, spans = repair('P S\ue001 R', OCRResult(('P S] R',), (0.999,)))
    assert text == 'P S] R' and spans[0]['accepted']
