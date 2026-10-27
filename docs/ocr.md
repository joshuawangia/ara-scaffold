# Local OCR

[Documentation index](README.md) · [Project README](../README.md)

`ara extract` and `ara plan-extraction` default to `--ocr local`: only pages with
glyph/encoding, visual-only, sparse-image, or empty-text diagnostics are rendered
locally. Healthy text-layer pages are unchanged. Install the pinned CPU stack and
download the hash-pinned public weights once:

```bash
uv sync --locked --extra ocr --extra ocr-vl
uv run --locked --extra ocr --extra ocr-vl python tools/fetch_ocr_models.py --vl
```

Python is pinned in `.python-version`; use that interpreter for the OCR extra.
Weights live in ignored `cache/ocr/`; override with `--ocr-cache PATH` on the
extraction/planning commands (or `--cache PATH` on the download/audit tools).
Intake never downloads weights or uses a cloud OCR endpoint. Missing dependencies,
missing/corrupt models, and inference failures abort explicitly. `--ocr off`
selects the previous text-only behavior, useful when reusing historical artifacts.
OCR changes the hashed input identity, so old extraction outcomes cannot be
silently reused as OCR-derived evidence.

Tier 1 uses PaddleOCR 3.7.0 with Baidu PP-OCRv6 tiny models on CPU. Remaining
flagged spans then use official PaddleOCR-VL-1.6 (0.9B), pinned to revision
`c5630abae1d940eafe0697512a0325494b02ab42`, with Transformers and CPU-only
PyTorch. VL loads lazily. `--ocr-tiers 1` explicitly disables it (only the `ocr`
extra and tier-1 weights are then required).

Policy `local-ocr-v4-spans` preserves the text layer and replaces only damaged
whitespace runs containing private-use, replacement, or invalid control glyphs.
Deterministic sequence alignment requires unique clean alphanumeric anchors on
both sides in both texts, searching adjacent anchor lengths from three tokens down
to one. Adjacent damaged runs share outer anchors and require a one-to-one run
alignment; differing run counts refuse. Original clean text, punctuation and
whitespace remain byte-for-byte unchanged. Literal clean fragments inside a
damaged run must also survive exactly and in order, with nonempty replacement text
at each damaged glyph run; otherwise the proposed repair refuses. Accepted tier-1
repairs are retained while tier 2 attempts the remaining spans using the original
coordinates.

Exact clean-fragment alignment must also be unique within the candidate span.
Repeated clean fragments that admit multiple glyph-group boundaries refuse. Only
newly synthesized non-whitespace characters at damaged glyph groups enter the
confidence mean and low-score share; preserved clean characters cannot dilute
either metric. Their absolute OCR ranges and alignment count are logged. Each
inserted span needs confidence >= 0.95, at most 5% of synthesized characters in
confidence units below 0.8, complete generation, no bad glyphs, and no loss of
mathematical symbols encoded inside the original damaged span. Tier 1 uses the
covering recognition-line scores. VL maps actual generated-token probabilities to
decoded character ranges, conservatively combining byte-token scores where
decoding rewrites a character. Neither confidence source is a calibrated
correctness probability. Ambiguous/missing anchors, unmapped scores, empty
insertions and incomplete generation remain flagged. Clean nonempty text with only
a visual/sparse diagnostic is retained for inspection; textless pages still use
the conservative whole-page OCR gate.

Per-span logs include engine, confidence, anchor matches, character offsets and
before/after character classes. Page provenance uses `selected: ocr_spans` for
mixed text, or `ocr` for textless-page recovery. Only fully repaired pages lose
their glyph diagnostics; partial repairs retain warnings and strict refusal.
Citations retain physical page numbers. The audit reports repaired/remaining spans
and clean/flagged pages. These checks do not establish exact typography, formula
fidelity, reading order or semantic completeness.

VL generation capped without EOS retries three horizontal tiles, choosing nearby
low-ink row boundaries. All tiles must finish with EOS. The full capped attempt,
each tile's geometry, output, scores and duration remain logged. Tiling can cut
layout elements; completion alone never certifies recovery.

Offline default tests use fakes. To exercise installed weights on a generated
placeholder raster PDF without networking:

```bash
ARA_TEST_LOCAL_OCR=1 ARA_TEST_LOCAL_VL=1 unshare -Urn .venv/bin/python -m pytest -q tests/runtime/test_ocr.py
```

`unshare -Urn` is a Linux validation command; the normal runtime also blocks
Python connections around synchronous OCR. A CPU-only audit makes no extraction
provider calls and writes content only under ignored `runs/`:

```bash
unshare -Urn .venv/bin/python tools/ocr_audit.py \
  --manifest literature/manifest.yaml --fulltext-dir literature/fulltext \
  --run-dir runs/ocr-audit
```

Use repeated `--paper-id` to audit a subset, or `--tiers 1` for tier 1 only. The
audit records per-paper recovery, remaining flags, mean confidence, timing, word
counts and character classes; empty-page controls are separate from affected-page
totals. Run production-wire controls only after pytest has finished, with no other
test/mutation runner:

```bash
uv run --locked --extra ocr --extra ocr-vl pytest -q
uv run --locked --extra ocr --extra ocr-vl python tools/ocr_negative_controls.py
uv run --locked --extra ocr --extra ocr-vl python tools/negative_controls.py
```

