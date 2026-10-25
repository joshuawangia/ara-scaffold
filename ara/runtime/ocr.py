"""Local, hash-verified PaddleOCR fallback. No downloads during intake."""
from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
from importlib.metadata import version
import json
import math
import os
from pathlib import Path
import re
import socket
import time
from typing import Protocol
import unicodedata

from ara.runtime.cache import canonical, digest

POLICY = 'local-ocr-v1'
ENGINE = 'PaddleOCR/PP-OCRv6_tiny'
VERSION = '3.7.0'
LOCK = Path(__file__).with_name('ocr_models.json')


@dataclass(frozen=True)
class OCRResult:
    lines: tuple[str, ...]
    scores: tuple[float, ...]

    def __post_init__(self):
        if len(self.lines) != len(self.scores) or any(not isinstance(s, str) for s in self.lines):
            raise ValueError('invalid OCR line/score shape')
        if any(not math.isfinite(s) or not 0 <= s <= 1 for s in self.scores):
            raise ValueError('invalid OCR confidence')

    @property
    def text(self):
        return '\n'.join(self.lines)

    @property
    def confidence(self):
        total = sum(len(s.strip()) for s in self.lines)
        return sum(len(s.strip()) * c for s, c in zip(self.lines, self.scores)) / total if total else 0.0


class OCREngine(Protocol):
    identity: dict

    def recognize(self, pdf: bytes, page: int) -> OCRResult: ...


def bad_character(c: str) -> bool:
    return unicodedata.category(c) == 'Co' or c == '\ufffd' or (
        unicodedata.category(c) == 'Cc' and c not in '\n\r\t')


def decision(original: str, result: OCRResult) -> dict:
    """Conservative page-level admission, not a semantic completeness verdict."""
    text = result.text
    old = ''.join(c for c in original if not c.isspace() and not bad_character(c))
    new = ''.join(c for c in text if not c.isspace())
    tokens = lambda s: Counter(re.findall(r'[a-zA-Z]{2,}', unicodedata.normalize('NFKC', s).lower()))
    before, after = tokens(original), tokens(text)
    recall = sum((before & after).values()) / sum(before.values()) if before else 1.0
    symbols = lambda s: Counter(c for c in s if unicodedata.category(c) == 'Sm')
    missing_symbols = sum((symbols(original) - symbols(text)).values())
    low_chars = sum(len(s.strip()) for s, c in zip(result.lines, result.scores) if c < 0.8)
    total_chars = sum(len(s.strip()) for s in result.lines)
    low_share = low_chars / total_chars if total_chars else 1.0
    length_ratio = len(new) / len(old) if old else 1.0
    recovered = (bool(new) and result.confidence >= 0.95 and low_share <= 0.05
                 and not any(bad_character(c) for c in text)
                 and length_ratio >= 0.98 and recall >= 0.98 and missing_symbols == 0)
    return dict(policy=POLICY, recovered=recovered, selected='ocr' if recovered else 'text_layer',
                confidence=result.confidence, low_confidence_char_share=low_share,
                retained_token_share=recall, character_ratio=length_ratio,
                missing_math_symbols=missing_symbols,
                original_text_sha256=digest(original), ocr_text_sha256=digest(text))


@contextmanager
def offline_network():
    """Deny Python network connections around this synchronous local OCR boundary."""
    def refuse(*args, **kwargs):
        raise RuntimeError('network access forbidden during local OCR')
    connect, connect_ex = socket.socket.connect, socket.socket.connect_ex
    create = socket.create_connection
    socket.socket.connect = socket.socket.connect_ex = socket.create_connection = refuse
    try:
        yield
    finally:
        socket.socket.connect, socket.socket.connect_ex = connect, connect_ex
        socket.create_connection = create


def verify_models(cache: Path, lock: dict) -> None:
    for model in lock.values():
        for filename, expected in model['files'].items():
            path = cache / filename
            if not path.is_file() or sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError('OCR model missing or hash mismatch; run tools/fetch_ocr_models.py')


class LocalOCR:
    def __init__(self, cache: Path):
        lock = json.loads(LOCK.read_text())
        verify_models(cache, lock)
        for package, expected in [('paddleocr', VERSION), ('paddlepaddle', '3.3.1'),
                                  ('paddlex', '3.7.2'), ('pypdfium2', '5.14.0')]:
            if version(package) != expected:
                raise ValueError(f'OCR requires {package}=={expected}; use uv sync --locked --extra ocr')
        self.identity = dict(engine=ENGINE, version=VERSION, weights_sha256=digest(canonical(lock)),
                             renderer='pypdfium2@5.14.0', dpi=200, cpu_threads=4,
                             detection_max_side=4000, mkldnn=False)
        os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
        os.environ['HF_HUB_OFFLINE'] = '1'
        with offline_network():
            from paddleocr import PaddleOCR
            self.pipeline = PaddleOCR(
                text_detection_model_name='PP-OCRv6_tiny_det',
                text_detection_model_dir=str(cache / 'PP-OCRv6_tiny_det_infer'),
                text_recognition_model_name='PP-OCRv6_tiny_rec',
                text_recognition_model_dir=str(cache / 'PP-OCRv6_tiny_rec_infer'),
                use_doc_orientation_classify=False, use_doc_unwarping=False,
                use_textline_orientation=False, device='cpu', cpu_threads=4,
                enable_mkldnn=False, text_rec_score_thresh=0.0,
                text_det_limit_side_len=4000, text_det_limit_type='max',
            )

    def recognize(self, pdf: bytes, page: int) -> OCRResult:
        with offline_network():
            import numpy as np
            import pypdfium2 as pdfium
            with pdfium.PdfDocument(pdf) as document:
                physical = document[page - 1]
                try:
                    bitmap = physical.render(scale=200 / 72)
                    try:
                        pixels = np.array(bitmap.to_pil().convert('RGB'))[:, :, ::-1].copy()
                    finally:
                        bitmap.close()
                finally:
                    physical.close()
            rows = list(self.pipeline.predict(pixels))
        if len(rows) != 1:
            raise ValueError('OCR must return exactly one physical page')
        return OCRResult(tuple(rows[0]['rec_texts']), tuple(float(s) for s in rows[0]['rec_scores']))


def recover_papers(papers, fulltext_dir: Path, log, cache: Path, *, engine: OCREngine | None = None):
    """Recover diagnosed pages before strict policy, grounding and reuse validation."""
    from ara.runtime.extraction import PageText
    recovered_papers = []
    for paper in papers:
        if paper.unavailable not in (None, 'no_readable_text'):
            recovered_papers.append(paper)
            continue
        candidates = {d.page for d in paper.diagnostics}
        if not candidates:
            recovered_papers.append(paper)
            continue
        try:
            if engine is None:
                engine = LocalOCR(cache)
            raw = (fulltext_dir / f'{paper.source_id}.pdf').read_bytes()
            if sha256(raw).hexdigest() != paper.pdf_sha256:
                raise ValueError('PDF changed after text intake')
            pages, records = [], []
            diagnostics = list(paper.diagnostics)
            for page in paper.pages:
                if page.page not in candidates:
                    pages.append(page)
                    continue
                start = time.perf_counter()
                result = engine.recognize(raw, page.page)
                record = dict(page=page.page, **engine.identity, **decision(page.text, result),
                              original_diagnostics=[asdict(d) for d in paper.diagnostics if d.page == page.page])
                log.record('extraction_ocr_page', source_id=paper.source_id, **record,
                           seconds=time.perf_counter() - start, text=result.text,
                           line_confidences=list(result.scores))
                records.append(record)
                if record['recovered']:
                    pages.append(PageText(page.page, result.text))
                    diagnostics = [d for d in diagnostics if d.page != page.page]
                else:
                    pages.append(page)
            updated = replace(paper, pages=tuple(pages), diagnostics=tuple(diagnostics),
                              ocr_provenance_json=canonical(records), unavailable=None)
            if not updated.readable_pages and not updated.affected_pages:
                updated = replace(updated, unavailable='no_readable_text')
            recovered_papers.append(updated)
        except Exception as exc:
            log.record('extraction_ocr_error', source_id=paper.source_id, error=type(exc).__name__)
            raise ValueError(f'{paper.source_id}: local OCR failed ({type(exc).__name__}); check locked dependencies and model cache') from exc
    return tuple(recovered_papers)
