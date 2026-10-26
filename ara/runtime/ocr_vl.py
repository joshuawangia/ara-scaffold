"""Pinned official PaddleOCR-VL CPU second tier; no remote code or services."""
from hashlib import file_digest
from importlib.metadata import version
import json
import os
import time
from dataclasses import asdict, replace
from pathlib import Path

from ara.runtime.cache import canonical, digest
from ara.runtime.ocr import OCRResult, offline_network, render_page

VL_LOCK = Path(__file__).with_name('ocr_vl_model.json')


def verify_vl_model(cache: Path, lock: dict) -> Path:
    root = cache / 'PaddleOCR-VL-1.6'
    for filename, expected in lock['files'].items():
        try:
            with (root / filename).open('rb') as stream:
                actual = file_digest(stream, 'sha256').hexdigest()
        except FileNotFoundError as exc:
            raise ValueError('VL model missing; run tools/fetch_ocr_models.py --vl') from exc
        if actual != expected['sha256']:
            raise ValueError('VL model hash mismatch; run tools/fetch_ocr_models.py --vl')
    return root


def generation_result(tokenizer, ids: list[int], probabilities: list[float], eos_ids: tuple[int, ...]) -> OCRResult:
    if not ids or len(ids) != len(probabilities):
        raise ValueError('VL generation token/score mismatch')
    pieces = [tokenizer.decode([token], skip_special_tokens=True) for token in ids]
    units = tuple((len(piece.strip()), probability)
                  for token, piece, probability in zip(ids, pieces, probabilities)
                  if token not in tokenizer.all_special_ids)
    text = tokenizer.decode(ids, skip_special_tokens=True)
    ranges = []
    offset = 0
    if ''.join(pieces) == text:
        for piece, probability in zip(pieces, probabilities):
            if piece:
                ranges.append((offset, offset + len(piece), probability))
                offset += len(piece)
    else:
        # Byte-level tokens may rewrite the preceding replacement character.
        # Decode prefixes and assign the minimum score of all contributing tokens.
        previous, scores = '', []
        for index, probability in enumerate(probabilities):
            current = tokenizer.decode(ids[:index + 1], skip_special_tokens=True)
            common = 0
            while common < min(len(previous), len(current)) and previous[common] == current[common]:
                common += 1
            probability = min([probability] + scores[common:])
            scores[common:] = [probability] * (len(current) - common)
            previous = current
        ranges = [(i, i + 1, p) for i, p in enumerate(scores)]
    total = sum(n for n, _ in units)
    confidence = sum(n * p for n, p in units) / total if total else 0.0
    return OCRResult((text,), (confidence,), confidence_units=units, confidence_ranges=tuple(ranges),
                     complete=ids[-1] in eos_ids, confidence_basis='generated_token_probabilities',
                     generation_json=canonical(dict(token_ids=ids, token_probabilities=probabilities, generated_tokens=len(ids),
                                                    terminal_token_id=ids[-1], eos_token_ids=list(eos_ids))))


class LocalVLOCR:
    def __init__(self, cache: Path):
        lock = json.loads(VL_LOCK.read_text())
        root = verify_vl_model(cache, lock)
        for package, expected in [('torch', '2.14.1+cpu'), ('torchvision', '0.29.1+cpu'),
                                  ('transformers', '5.20.2'), ('pypdfium2', '5.14.0')]:
            if version(package) != expected:
                raise ValueError(f'VL requires {package}=={expected}; install locked ocr and ocr-vl extras')
        self.identity = dict(engine='PaddleOCR-VL', version='1.6', weights_sha256=digest(canonical(lock)),
                             model_revision=lock['revision'], backend='transformers@5.20.2/torch@2.14.1+cpu',
                             renderer='pypdfium2@5.14.0', dtype='bfloat16', cpu_threads=8, dpi=200,
                             max_pixels=1003520, max_new_tokens=4096, prompt='OCR:', use_cache=True,
                             cap_recovery='three_horizontal_whitespace_tiles')
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '1'
        os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
        with offline_network():
            import torch
            from transformers import AutoProcessor, AutoModelForImageTextToText
            torch.set_num_threads(8)
            self.model = AutoModelForImageTextToText.from_pretrained(
                root, local_files_only=True, trust_remote_code=False, dtype=torch.bfloat16,
                attn_implementation='sdpa').to('cpu').eval()
            self.processor = AutoProcessor.from_pretrained(root, local_files_only=True, trust_remote_code=False)

    def recognize(self, pdf: bytes, page: int) -> OCRResult:
        image = render_page(pdf, page)
        start = time.perf_counter()
        result = self._recognize_image(image)
        if result.complete:
            return result
        capped_seconds = time.perf_counter() - start
        tiled = self.recognize_tiled(image)
        generation = json.loads(tiled.generation_json)
        generation['capped_attempt'] = dict(seconds=capped_seconds, result=asdict(result))
        return replace(tiled, generation_json=canonical(generation))

    def recognize_tiled(self, image) -> OCRResult:
        """Retry at natural low-ink horizontal boundaries, preserving physical page."""
        import numpy as np
        ink = np.asarray(image.convert('L')).mean(axis=1)
        height = image.height
        cuts = [0]
        for fraction in (1 / 3, 2 / 3):
            center = int(height * fraction)
            radius = max(1, height // 30)
            candidates = range(max(cuts[-1] + 1, center - radius), min(height, center + radius))
            cuts.append(min(candidates, key=lambda y: (-float(ink[y]), abs(y - center), y)))
        cuts.append(height)
        results, attempts, ranges, offset = [], [], [], 0
        for top, bottom in zip(cuts, cuts[1:]):
            start = time.perf_counter()
            result = self._recognize_image(image.crop((0, top, image.width, bottom)))
            attempts.append(dict(top=top, bottom=bottom, seconds=time.perf_counter() - start,
                                 result=asdict(result)))
            ranges.extend((a + offset, b + offset, p) for a, b, p in result.character_confidences)
            offset += len(result.text) + 1
            results.append(result)
        return OCRResult(tuple(r.text for r in results), tuple(r.confidence for r in results),
                         confidence_units=tuple(u for r in results for u in r.units),
                         confidence_ranges=tuple(ranges), complete=all(r.complete for r in results),
                         confidence_basis='generated_token_probabilities',
                         generation_json=canonical(dict(mode='horizontal_tiles', tiles=attempts)))

    def _recognize_image(self, image) -> OCRResult:
        with offline_network():
            import torch
            inputs = self.processor.apply_chat_template(
                [{'role': 'user', 'content': [{'type': 'image', 'image': image}, {'type': 'text', 'text': 'OCR:'}]}],
                add_generation_prompt=True, tokenize=True, return_dict=True, return_tensors='pt',
                images_kwargs={'size': {'shortest_edge': 112896, 'longest_edge': 1003520}}).to('cpu')
            with torch.inference_mode():
                output = self.model.generate(**inputs, max_new_tokens=4096, do_sample=False, use_cache=True,
                                             return_dict_in_generate=True, output_scores=True)
            ids = output.sequences[0, inputs['input_ids'].shape[-1]:].tolist()
            probabilities = [float(torch.softmax(score[0].float(), -1)[token])
                             for score, token in zip(output.scores, ids)]
            eos = self.model.generation_config.eos_token_id
            eos_ids = (eos,) if isinstance(eos, int) else tuple(eos)
            return generation_result(self.processor.tokenizer, ids, probabilities, eos_ids)
