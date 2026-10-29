# Rho2: local OCR fallback

Implemented in `/home/dev/ara-work/rho2`, branch `feat/local-ocr`, from requested
base `50ddc056dd408e7990a177a59256e7cba2396afb`. Committed locally at
`7c988dccee16f3129463c6ab74544843e003fbc8`. The worktree is clean; no push or delegation occurred.

**All 82 affected pages were OCR'd locally: 22 met the recovery policy, 60 remain
flagged. Mean time was 6.15 seconds per affected page. This does not deliver a
guarantee of “all content.”** The remaining pages need further source repair or
review. Confidence alone is insufficient, and even accepted pages have no
semantic/formula-completeness guarantee. Existing extraction artifacts and their
seven partial statuses were not rewritten; this task made no paid provider calls.

## Native behavior and use

`ara extract` and `ara plan-extraction` now default to `--ocr local`. The fallback
runs after existing PDF diagnostics and before strict missing-policy checks,
grounding, reuse validation and model dispatch. Only diagnosed pages are OCR'd.
Healthy text remains unchanged, and citations keep one-based physical PDF pages.
Successful pages carry `selected: ocr`, engine/version, model hash, original
flags and deterministic decision metrics through input identity and published
provenance. Attempts also retain OCR output, scores and timing in native chained
logs. Rejected pages keep original text and diagnostics; `--missing refuse`
still refuses remaining affected pages. Genuine blank pages remain separately
classified. Operational errors are logged and abort explicitly.

Setup in the worktree:

```bash
uv sync --locked --extra ocr
uv run --locked --extra ocr python tools/fetch_ocr_models.py
```

Weights are already cached here under ignored `cache/ocr/`. Missing dependencies
or missing/tampered weights do not trigger a download or silent text-only fallback.
Use `--ocr-cache PATH` to select another cache. `--ocr off` explicitly selects the
old intake behavior, including when intentionally reusing historical text-only
artifacts. Changed OCR identity cannot silently reuse old extraction outcomes.
New OCR input still needs a normal extraction run to produce new argument graphs.
Existing pypdf warnings about absent optional fontTools support were observed and
remain in the ignored intake logs. This change preserves the baseline parser;
it does not claim to repair every encoding problem or detect every unread glyph.

## Engine, hardware, pins and licenses

Selected **PaddleOCR/PP-OCRv6_tiny@3.7.0**, with PaddlePaddle 3.3.1, PaddleX 3.7.2,
pypdfium2 5.14.0, Python 3.13.7, uv 0.13.5. All direct dependencies are exact;
`uv.lock` pins transitive distributions and hashes. PaddleX requires PyYAML 6.0.2,
the sole existing locked package version changed (from 6.0.3).

Hardware: 16 AMD EPYC 9554P virtual CPU cores, 62 GiB RAM (about 60 GiB available
at inspection), no detected NVIDIA GPU. Render at 200 DPI; detector longest-side
cap 4000 pixels; four CPU threads; recognition-score filter zero. MKL-DNN is
explicitly disabled because the accelerated probe failed with Paddle's
`ConvertPirAttribute2RuntimeAttribute` NotImplementedError.

Official sources checked on 2026-10-25 show the brief's versions are superseded:
PaddleOCR 3.7.0 offers PP-OCRv6; the current VLM is PaddleOCR-VL-1.6 (0.9B), and
PP-StructureV3 also exists. The official olmOCR local-inference requirements call
for a recent NVIDIA GPU with at least 12 GiB VRAM. There is no measured evidence
that it is a better fit on this CPU box; no cross-model academic accuracy
benchmark is claimed. Upstream performance tables warn that generations use
different evaluation sets.

One-page CPU probes: medium/unscaled took 66.55s; medium/1280 took 47.57s.
Tiny/1280 took 3.99s but retained only 94.68% of known word tokens, so that
configuration was rejected. Tiny/4000 took 6.16s with 100% known-token and 99.88%
character retention. The final corpus run uses tiny/4000 only. Timings were
measured on this box with tests also running, not an isolated benchmark.

PaddleOCR, PaddlePaddle, PaddleX, and both selected weight model cards are
**Apache-2.0**. pypdfium2 is Apache-2.0/BSD-3-Clause with bundled PDFium/dependency
notices. Code/weight choices and licenses are recorded in `DECISIONS.md`.

Combined model-lock SHA-256:
`400c688341313a3275a8cf2b4489636a1300d653c9ebb0cc6386259729bed208`.

Downloaded archive hashes (individual inference/config file hashes are committed
in `ara/runtime/ocr_models.json` and verified again before inference):

- Detector: `33a23c5e18d83208f9eeeccd00ed789af891786ac9255c83aeb2495b3db9ce63`.
- Recognizer: `54403af57bc53981d3dce091c6c80dfc5ae30d58495541777126a54bac450604`.

Sources:

- https://github.com/PaddlePaddle/PaddleOCR
- https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/pipeline_usage/OCR.en.md
- https://huggingface.co/PaddlePaddle/PP-OCRv6_tiny_det/tree/d3177d4e5551463292a61e27cfca2b53e7c3fe9d
- https://huggingface.co/PaddlePaddle/PP-OCRv6_tiny_rec/tree/0736086f72f666350ebcdc0c3a504eeac89cdfad
- https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6
- https://github.com/allenai/olmocr#requirements
- https://pypdfium2.readthedocs.io/en/stable/readme.html#licensing

## Recovery rule and structural results

Policy `local-ocr-v1` requires nonempty output; character-weighted recognition
confidence >= 0.95; <= 5% of characters in lines below 0.8 confidence; no
private-use/replacement/control characters; >= 98% of usable original characters;
>= 98% multiset recall of normalized Latin word tokens; and no loss of original
Unicode mathematical-symbol counts. Elapsed time is logged separately from
hashed inputs. These checks are conservative and can refuse valid alternative
hyphenation/tokenization. They cannot establish reading order, glyph meaning,
faithful mathematics, or semantic completeness.

Confidence below is the mean of each attempted page's character-weighted score,
including rejected pages. Time includes rendering/inference and decision work,
but excludes initial model loading and paper parsing.

| Paper ID | Affected / attempted | Recovered | Still flagged | Mean confidence | Seconds |
|---|---:|---:|---:|---:|---:|
| schaffer2011 | 1 | 1 | 0 | 0.9733 | 0.69 |
| braun2012 | 5 | 3 | 2 | 0.9785 | 29.83 |
| macfarlane2014 | 15 | 1 | 14 | 0.9591 | 79.38 |
| yalcin2007 | 42 | 10 | 32 | 0.9824 | 282.96 |
| yalcin2015 | 3 | 0 | 3 | 0.9589 | 14.73 |
| ninan2018 | 8 | 0 | 8 | 0.9636 | 47.67 |
| kolodnymacfarlane2010 | 8 | 7 | 1 | 0.9800 | 49.16 |
| **Total** | **82 / 82** | **22** | **60** | **0.9748** | **504.41** |

Total audit elapsed: **547.68s**. Model initialization: **1.65s**. Ten genuinely
blank controls took **28.11s** in addition to the 82 affected pages and were not
counted recovered. The exact affected-page inventory matches the prior report.
All **541 healthy pages** were unchanged, and physical page sequences and PDF
hashes matched before/after intake.

Structural audit across all 82 candidates: **33,131 original whitespace words**
versus **30,694 OCR words**; **1,441 private-use characters** in the originals
versus zero in OCR. Word totals are not truth labels. Zero bad glyphs does not
prove their meaning was recovered. Among the 60 rejected pages, reasons overlap:
49 failed known-token retention, 23 character retention, 21 mathematical-symbol
preservation, 6 mean confidence, and 5 the low-confidence-line share. Outputs
were preserved for inspection rather than admitted merely because their aggregate
confidence was high. No content quotes or paper fixtures enter tracked files.

## Offline evidence and reproduction

Final content-bearing evidence is under ignored `/home/dev/ara-work/rho2/runs/ocr-final82/`:
`events.jsonl` plus its chain checkpoint, per-paper JSON (original/recovered intake
and structural metrics), `summary.json`, and `verification.json` with artifact
hashes. The latter verifies exact 82-page coverage, 92 unique attempts including
blanks, physical numbering, healthy-page preservation, and **zero MODEL events**.

The audit ran with `unshare -Urn`; the captured namespace differs from the parent,
has no routes, and its interfaces show zero transmitted/received bytes. Receipt:
`runs/ocr-research/network-isolation.json`. Runtime additionally blocks Python
socket connections during synchronous initialization/inference and supplies
local paths/arrays only. That Python guard is not a general sandbox for arbitrary
native code or concurrent threaded callers. No PDFs were uploaded to OCR services.

Reproduce from this worktree after installing the locked extra and weights:

```bash
unshare -Urn .venv/bin/python tools/ocr_audit.py \
  --manifest /home/dev/ara-scaffold/literature/manifest.yaml \
  --fulltext-dir /home/dev/ara-scaffold/literature/fulltext \
  --run-dir runs/ocr-repeat \
  --paper-id schaffer2011 --paper-id braun2012 --paper-id yalcin2007 \
  --paper-id ninan2018 --paper-id kolodnymacfarlane2010 \
  --paper-id yalcin2015 --paper-id macfarlane2014
```

Preliminary medium/resize experiments remain in `runs/ocr-research/` and
`runs/ocr-real82/`; the interrupted medium run is not the final corpus evidence.
Research/model-card snapshots and prior work notes are in `runs/ocr-research/`.

## Verification and delivery

Final full pytest with the opt-in local model test passed **887 tests, 2 skipped**
in **541.16s** under network isolation. The two skips are pre-existing opt-in
paid-provider tests. Log: `runs/ocr-research/pytest-final.log`. All **10 OCR
production-wire controls** went red (exit 1), restored, then green (exit 0),
sequentially after pytest; receipts are in `runs/ocr-controls/`. The existing
repository runner then passed **50/50** mutations with every target restored
green (`runs/alpha-proof/negative-controls.json`). The final restored OCR/strict
intake checks passed **29/29**, including the installed local model, in 6.89s
(`runs/ocr-research/pytest-restored.log`). These test/control stages ran sequentially.

The separate base environment, without PaddleOCR installed, passed **28 tests,
1 skipped**, with networking disabled. The existing strict-policy test explicitly
selects `--ocr off` and asserts the actual `strict_incomplete_coverage` receipt,
rather than merely searching a log for the word “partial.” The symbol-loss
control uses equal-length output so character-count refusal cannot mask a broken
symbol safeguard; that target also passed after mutation restoration.

Model fetch/verification, `uv lock --check`, compileall, and `git diff --check`
passed. No dedicated lint/type-check command is configured. The inline
ce-simplify-code pass reused existing intake/logging/hash contracts and simplified
audit serialization/parsing; it did not substitute for non-author review.
Local commit: `7c988dccee16f3129463c6ab74544843e003fbc8` — `feat(runtime): recover flagged PDF pages with local OCR`.
All 14 task files are committed; no runs, weights, PDFs, or paper content are in
the commit. The committed runtime/model-lock/dependency files match the hashes
captured during the corpus audit. Final receipt: `runs/ocr-research/delivery.json`.
Non-author review follows this local delivery as the brief requests. No push.


## Finding placement

| Action-relevant finding | Deliverable section |
|---|---|
| 1. Only 22/82 pages pass; 60 require further repair/review; no all-content guarantee | Opening; Recovery rule and structural results |
| 2. Default local fallback, strict refusal, provenance and physical citations use native intake | Native behavior and use |
| 3. Installation/cache prerequisites and explicit opt-out; old extraction artifacts cannot become recovered by reuse | Native behavior and use |
| 4. Current Baidu versions, CPU hardware, tiny/full-resolution choice and lack of a demonstrated better CPU alternative | Engine, hardware, pins and licenses |
| 5. MKL-DNN failure and rejected faster detector setting; timings measured with concurrent system work | Engine, hardware, pins and licenses |
| 6. Exact dependency/model hashes and licenses; PyYAML downgrade | Engine, hardware, pins and licenses |
| 7. Threshold limits, overlapping rejection reasons, word/glyph counts, blanks and unchanged healthy pages | Recovery rule and structural results |
| 8. Native offline evidence, OS network isolation, Python-guard scope and zero paid MODEL events | Offline evidence and reproduction |
| 9. Full tests, optional paid skips, no-extra tests and restored production-wire controls; strengthened strict-policy test | Verification and delivery |
| 10. Existing parser/fontTools warnings do not establish comprehensive encoding repair | Native behavior and use |
| 11. Local commit only, clean ownership, no pushed changes, non-author review still follows | Verification and delivery |

11 findings, 11 placed.

DONE rho2 head=7c988dccee16f3129463c6ab74544843e003fbc8 engine=PaddleOCR/PP-OCRv6_tiny@3.7.0 tests=887/889 negctl=pass pages_recovered=22/82 s_per_page=6.15

## Round 2 — work record

Executing `/home/dev/ara-work/briefs/rho2-round-2.md` on the same clean branch
from `7c988dccee16f3129463c6ab74544843e003fbc8`. No delegation, push, or paid calls.
The existing regex in `ara/runtime/ocr.py:decision` extracts Latin fragments
inside damaged glyph spans; its character denominator also retains those
fragments. The revised hypothesis is to exclude tainted original spans, count
whole clean alphanumeric tokens, and retain genuinely encoded mathematical
symbols. Thresholds remain fixed. Re-evaluate the retained round-1 OCR receipts
without rerunning tier 1, report flips and regressions, and inspect flip page
renders locally without putting content in tracked files or the report.

Official PaddleOCR-VL-1.6 model card supports CPU through its Transformers example
and warns that this path performs element recognition/text spotting rather than
the full layout pipeline. Pin official revision
`c5630abae1d940eafe0697512a0325494b02ab42`; download and verify its 1.917 GB weights
plus tokenizer/config files. PyTorch CPU-only wheels avoid GPU dependencies.
Start with a rejected physical page, measure full-page generation, enforce the
same gate using actual generated-token probabilities, and reject truncation.
Run all remaining pages only if measured performance is about 120 seconds/page
or less. Initial free disk is 22 GiB. CPU benchmarking and all document inference
run in an isolated network namespace.


## Round 2

Completed on the same branch, `feat/local-ocr`, from `7c988dc`. Local commit:
`605d7d862fbb14cc32135c4c9fda4e313e316328`. This section supersedes the Round 1 acceptance counts above.

**Tier 1 recovers 13/82 pages under the revised gate; VL adds
2, for 15/82 total. 67 pages remain flagged.**
Those 67 pages still need further source repair or review. This is
threshold-based recovery, not a guarantee of all content. Existing
extraction artifacts and partial statuses were not rewritten; a normal extraction
run must consume the new intake. No paid extraction calls or push occurred.

### Metric changes and flips

The old Latin-fragment regex could count fragments on either side of a damaged
glyph as trustworthy words and could miss changes in numbers or identifiers.
Policy `local-ocr-v2` excludes entire whitespace spans containing private-use,
replacement, or invalid control glyphs before stripping LaTeX markup. It then
compares whole Unicode alphanumeric tokens, including single letters and digits,
with NFKC normalization, case folding and multiset recall. This is an explicit
alphanumeric criterion, not a dictionary claim: printable corruption that contains
no detected bad glyph can remain in the reference.

Across all 82 pages, 677 tainted spans are excluded. **0 of the prior 60 rejections
flip to accepted.** Nine prior acceptances become rejections because the old
regex missed clean-token losses: `yalcin2007` physical pages 2, 5, 9, 25, 29, 30,
31 and 42; `kolodnymacfarlane2010` page 30. These nine also received VL inference.
Among the original 60 rejections, overlapping failures under the revised metric
are 57 token retention, 23 character retention, 21 encoded mathematical-symbol
preservation, 6 mean confidence, and 5 low-confidence share. Token recall improves
on two of those pages, but their other failures remain.

The 98% character/token thresholds, 0.95 weighted-confidence floor, and 5%
low-confidence-share ceiling are unchanged. The usable-character denominator
still includes non-garbage characters inside tainted spans: removing that floor
was investigated and rejected after structural/visual inspection. Literal math
symbols still count even within tainted spans; private-use glyph identities are
not guessed. The mathematical-symbol check uses Unicode's Sm category; it does
not identify arbitrary mathematics from typography. Explicit standard LaTeX symbol spellings count as the same encoded
Unicode symbols, including Greek letters in clean-token comparison, while command names cannot stand in for missing prose.
Truncated generation and empty output are rejected. No metric was relaxed merely
to increase the recovered count.

### Native behavior and setup

Extraction and planning now default to two local tiers. Healthy pages stay on the
text layer; a tier-1 acceptance skips VL. Only rejected affected nonblank pages
reach the lazy VL engine, with the same final gate. Each attempt records tier,
engine/version, weight hash, physical page, original diagnostics, metrics and
chosen source. Native chained logs also retain output, confidence units, EOS,
generation length and elapsed time. Rejection keeps original text and diagnostics;
strict missing policy still refuses it. Operational errors log and abort.

```bash
uv sync --locked --extra ocr --extra ocr-vl
uv run --locked --extra ocr --extra ocr-vl python tools/fetch_ocr_models.py --vl
```

`--ocr-tiers 1` explicitly selects the faster single tier; `--ocr off` retains
text-only intake. Neither mode is a silent fallback. Missing/tampered weights or
missing dependencies abort explicitly. OCR provenance remains part of reuse
identity, so old extraction artifacts cannot silently acquire new recovery claims.
The cache stores weights; normal intake reruns recognition on diagnosed pages,
including before reuse checks. The ordinary audit tool supports `--tiers 1` or
`--tiers 2` (default).

### Official VL engine, pins and measured cost

The second tier is official **PaddleOCR-VL-1.6 (0.9B)**, revision
`c5630abae1d940eafe0697512a0325494b02ab42`, through its documented Transformers
CPU path. Exact dependencies are Transformers 5.20.2, PyTorch 2.14.1+cpu,
torchvision 0.29.1+cpu and pypdfium2 5.14.0. uv.lock retains distribution hashes;
`ocr_vl_model.json` pins all model/tokenizer/config files. Fifteen locked packages
were added; no previously locked package version changed in Round 2. Model weights SHA-256:
`85a479d506a11e724e7285d395c551be69f41dbc16b6342d3cacfb189aed71db`.
Combined model-lock SHA-256:
`99033588ee048347de6cf29b67a9633c173abb92ef4f5ab41eb624f16140d71a`.

Weights and PaddleOCR/Transformers code are Apache-2.0. PyTorch and torchvision
have BSD-3-Clause primary licenses; bundled distribution licenses/notices are
retained and listed in DECISIONS.md. About 19 GB remained free after installation.
No remote code is trusted, no inference download occurs, and documents remain local.

CPU configuration: eight threads, BF16, SDPA, 200 DPI, maximum 1,003,520 pixels,
greedy `OCR:` generation, KV cache, maximum 4096 new tokens and mandatory EOS.
The initial eight-thread probe took **64.91 s/page**; four threads took 81.07 s.
This met the brief's approximate 120-second threshold, so all remaining pages ran.
The audit then recorded **69 unique VL pages in
69 completed attempts**, taking **5744.37s**,
mean **83.25 s/page**. Initial model loading is
excluded, as are probes and aborted-attempt overhead. The slowest completed attempt took 415.06s; 2 pages
reached the generation cap without EOS and remained rejected. A short experiment with concurrent CPU processes increased latency;
three supplemental pages completed that way, after which remaining inference was
serialized. Their slower timings remain included. Tests and other local work also
shared the machine; this is not a dedicated-host benchmark.

VL confidence uses actual generated-token probabilities weighted by decoded
character length. It is not calibrated against PP-OCR line confidence or against
correctness. The same numeric thresholds apply to both engines, with their
confidence basis recorded. The official Transformers path performs element
recognition/text spotting, not the complete layout pipeline. Full-page use does
not establish layout, formula or reading-order fidelity. Upstream configuration
and deprecation warnings were retained; pinned model files were not altered to
silence them.

Source: https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6/tree/c5630abae1d940eafe0697512a0325494b02ab42

### Per-paper results

Tier-1 outputs are the exact saved Round 1 outputs rescored under the final gate.
VL confidence averages all attempted VL pages, including rejections. Seconds are
actual inference receipt times, not the faster final replay time.

| Paper ID | Affected | Tier 1 | VL added | Still flagged | VL attempts | VL mean confidence | VL seconds |
|---|---:|---:|---:|---:|---:|---:|---:|
| schaffer2011 | 1 | 1 | 0 | 0 | 0 | — | 0.00 |
| braun2012 | 5 | 3 | 2 | 0 | 2 | 0.9939 | 137.12 |
| macfarlane2014 | 15 | 1 | 0 | 14 | 14 | 0.9770 | 973.29 |
| yalcin2007 | 42 | 2 | 0 | 40 | 40 | 0.9877 | 3320.97 |
| yalcin2015 | 3 | 0 | 0 | 3 | 3 | 0.9892 | 559.09 |
| ninan2018 | 8 | 0 | 0 | 8 | 8 | 0.9834 | 639.87 |
| kolodnymacfarlane2010 | 8 | 6 | 0 | 2 | 2 | 0.9884 | 114.02 |
| **Total** | **82** | **13** | **2** | **67** | **69** | — | **5744.37** |

### Structural and visual evidence

There are no metric acceptance flips to spot-check. Terminal-only source/OCR
render comparisons covered a rejected character-floor candidate (`yalcin2007/6`),
a newly rejected prior acceptance (`yalcin2007/2`), and a new VL acceptance
(`braun2012/16`). The two rejected samples lose logic marks and insert margin text
inside the body. The accepted VL sample preserves body, numbered blocks, footnote
and page number, while converting corner delimiters to ordinary brackets.
The capped VL output on `yalcin2007/15` replaces the displayed logic sequence
with repeated geometric marks and omits margin/footer material despite high
confidence. These observations support conservative admission and demonstrate why passing
structural checks is not exact transcription or semantic proof. No paper quotes
or paper-derived fixtures are tracked.

Final ignored evidence: `runs/ocr-round2-final/` contains per-paper original and
recovered intake, per-attempt structural counts, summary, chained events and
`verification.json`. Verification covers all 82 physical pages, unchanged PDF
hashes/numbering, **541 unchanged healthy pages**, ten separate blank controls,
model hashes, source-code hashes and **zero MODEL events**. Word counts and
character-class counts are recorded for every attempted page.

Original inference receipts remain in `runs/ocr-final82/` (tier 1),
`runs/ocr-round2/` (the first 60 VL pages) and `runs/ocr-round2-additional/`
(the nine newly rejected pages). Final intake replays those literal outputs and
scores through production `recover_papers`, recording origin log hashes and event
indices; it does not claim another inference benchmark. This preserves completed
inference across session continuation and the final metric repair. Scripts and
research receipts are in `runs/ocr-round2-research/`. An initial final replay
incorrectly split VL text against its one aggregate score; that failed scratch
output is preserved in `runs/ocr-round2-final-failed-replay/`. The corrected final
replay preserves the VL score granularity and did not repeat inference. An early empty-generation
error was fixed to become a logged rejection; completed paper receipts were
preserved when the audit resumed.

Inference and final replay ran with `unshare -Urn`. Namespace receipts show no
routes or traffic; the synchronous Python connection guard is also active. That
Python guard alone is not a general sandbox for arbitrary native code or threaded
applications. No PDFs were sent to cloud OCR, and no paid provider calls occurred.

### Verification and local delivery

Final full pytest, with both installed local-model opt-ins and paid tests disabled:
**915 passed, 2 skipped, 1 warning in 618.47s (0:10:18)**. Log: `runs/ocr-round2-research/pytest-final.log`. The two skips are
pre-existing paid-provider opt-ins. Both installed local-model tests ran within the full suite.
The earlier full run exposed an incorrect synthetic test assumption: the actual
VL result had 0.826 confidence and 50% low-confidence character share, so refusal
was correct. The test now checks that observed rejection instead of requiring the
gate to accept it. Thresholds were not changed.

Three clean-alphanumeric cases, three Greek-equivalence cases, and the markup/span-order regression
were observed failing before their fixes. The control runner exercises **21 OCR
production-wire mutations**, each red then restored green. The repository control
runner exercises **50 mutations**, also red then restored green. These stages ran
sequentially after the full suite, in an isolated local clone whose 176 source
files matched the canonical checkout byte for byte. Imports were verified to use
the clone, and all source hashes were verified restored afterward. This kept
mutations away from the live inference process. The source manifest is
`runs/ocr-round2-research/control-source-manifest.json`. Receipts:
`runs/ocr-round2-controls/` and `runs/ocr-round2-repo-controls/negative-controls.json`.
Without either optional OCR stack installed, focused tests passed **53 tests**,
with the two local-model cases skipped (`runs/ocr-round2-research/pytest-no-extra.log`).
Lock validation, compileall and `git diff --check` pass. No dedicated lint/typecheck
command is configured. Inline simplification found no necessary refactor; it is
not a non-author review. That review remains the operator's next step as requested.

Only implementation, synthetic tests, dependency/model locks and documentation
are committed. Runs, PDFs, weights and document content remain ignored. No push.
Local commit: `605d7d862fbb14cc32135c4c9fda4e313e316328`.

### Round 2 finding placement

| Action-relevant finding | Section |
|---|---|
| 1. Clean-token definition, excluded spans, zero flips, nine stricter rejections and unchanged thresholds | Metric changes and flips |
| 2. Two-tier native path, physical citations, explicit opt-outs, weight-only caching, strict refusal and reuse identity | Native behavior and setup |
| 3. Final recovered/remaining counts and absence of an all-content guarantee | Round 2 opening; Per-paper results |
| 4. Official model/dependency pins, hashes, licenses, cache prerequisites and disk footprint | Official VL engine, pins and measured cost |
| 5. Generated-token confidence differs from line confidence; EOS, empty and truncation handling | Metric changes and flips; Official VL engine, pins and measured cost |
| 6. CPU probes, actual page timing and concurrency slowdown retained in the mean | Official VL engine, pins and measured cost |
| 7. Element-recognition backend, upstream warnings and unproved layout/formula fidelity | Official VL engine, pins and measured cost |
| 8. Literal receipt replay, origin hashes, source hashes, structural checks and unchanged healthy pages | Structural and visual evidence |
| 9. Local-only inference, namespace proof, Python-guard limits and zero paid calls | Structural and visual evidence |
| 10. Visual evidence of losses and residual typography changes even on an accepted page | Structural and visual evidence |
| 11. Initial test failure, measured rejection, final full/installed/no-extra tests and restored controls | Verification and local delivery |
| 12. Existing artifacts unchanged, local-only commit, ignored content and non-author review still due | Round 2 opening; Verification and local delivery |

12 findings, 12 placed.

DONE rho2 round2 head=605d7d862fbb14cc32135c4c9fda4e313e316328 recovered_tier1=13 recovered_vl=2 total_recovered=15/82 vl_s_per_page=83.25


## Round 3

Completed locally on `feat/local-ocr`, from `605d7d8`. Commit: `cc705c7e37ac607c1546cd8218f46bf503c99f5b`.
No push, delegation, paid extraction calls, or document uploads occurred.

**131 damaged spans are repaired; 547 remain. 9/82 pages have
no remaining diagnostics; 73 remain flagged.** “Clean” here means the
stated structural admission policy passed, not that all content or mathematics
is verified. Existing extraction artifacts were not rewritten.

### Corrected span inventory

The literal inventory is **678 damaged whitespace runs**, not the Round 2
estimate of 677. That metric subtracted a normalized clean-span count from an
unnormalized whitespace count. On `kolodnymacfarlane2010`, physical page 1,
U+00B4 acquires a leading space under NFKC, causing six damaged runs to be
reported as five. Round 3 counts original tainted runs directly; a regression
test reproduces the undercount and verifies the correction. All 678 runs are
accounted for below. The requested final `spans_repaired=131/677` field keeps
the brief's historical denominator only; the measured fraction is **131/678**.
No span was dropped to force agreement with the old total.

### Native span repair

The text layer remains the base. Exact deterministic token-sequence alignment
searches adjacent clean alphanumeric anchors from three tokens down to one on
each side. Each anchor must occur uniquely in both original and OCR streams and
appear in order. Tokens normalize with NFKC/casefold; fragments inside damaged
runs never become anchors. Adjacent damaged runs can share outer anchors only
when the interior OCR run count matches, allowing a one-to-one positional
alignment. Different cardinality refuses. All original text and whitespace
outside accepted tainted runs are preserved exactly. Literal clean fragments
inside each tainted run must also match exactly, including case and punctuation;
nonempty inserted text may occupy only the original damaged glyph runs.

Each insertion must have covering confidence >=0.95, at most 5% of non-whitespace
characters below 0.8 confidence, no bad glyphs, complete generation, and no loss
of math symbols encoded within the damaged run. Tier 1 uses covering recognition
line scores; VL uses actual generated-token probabilities mapped to character
ranges. Byte-token decoding can rewrite a preceding character, so its confidence
uses the minimum contributing score. Missing confidence coverage refuses.
These scores are not calibrated correctness probabilities.

Tier 2 tries remaining spans against original coordinates and cannot overwrite
accepted tier-1 repairs. Successful spans persist even on a still-flagged page.
Per-span logs contain engine, confidence, anchor matches, original/OCR offsets,
and before/after character classes. Native page provenance labels mixed text
`ocr_spans`; strict missing policy still refuses unresolved diagnostics. Physical
page citations and input/reuse identity remain native. Clean nonempty text with
only sparse/visual warnings is retained for inspection. Textless pages retain
the existing conservative page-OCR gate and use `ocr` provenance.

Only fully repaired glyph-warning pages lose their diagnostics. This is a
stricter claim than replacing a page whose aggregate retention passes: Round 2's
15 admitted pages and this round's 9 fully clean pages measure different
policies. The gain is preserving trustworthy text and retaining useful repairs
on incomplete pages. Unanchorable formulas and printable encoding artifacts can
remain; the detector does not claim to find all possible corruption.

### Per-paper results

| Paper ID | Affected pages | Spans | Repaired | Remaining | Pages clean | Pages flagged | Admitted mean confidence | New VL seconds |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| schaffer2011 | 1 | 0 | 0 | 0 | 1 | 0 | — | 0.00 |
| braun2012 | 5 | 24 | 3 | 21 | 0 | 5 | 0.9782 | 154.13 |
| macfarlane2014 | 15 | 111 | 0 | 111 | 0 | 15 | — | 56.42 |
| yalcin2007 | 42 | 474 | 117 | 357 | 3 | 39 | 0.9827 | 143.65 |
| yalcin2015 | 3 | 12 | 1 | 11 | 1 | 2 | 0.9908 | 105.65 |
| ninan2018 | 8 | 39 | 0 | 39 | 0 | 8 | — | 0.00 |
| kolodnymacfarlane2010 | 8 | 18 | 10 | 8 | 4 | 4 | 0.9757 | 270.20 |
| **Total** | **82** | **678** | **131** | **547** | **9** | **73** | — | **730.06** |

120 span repairs come from tier 1 and 11 from VL. Confidence averages admitted spans only; timing counts new VL attempts and tile retries only, excluding reused prior inference and initialization. The textless-page recovery is separate from span counts.

Final refusal reasons, one per remaining span: `anchor_not_unique` 490, `clean_boundary_mismatch` 13, `clean_fragment_changed` 8, `cluster_alignment_ambiguous` 8, `low_confidence` 16, `missing_anchor` 12.

### VL completion and measured time

The two prior capped pages now complete with EOS in three nonoverlapping
horizontal tiles, choosing nearby low-ink row boundaries around page thirds.
The production path retries a capped full-page result this way and logs the
capped attempt plus tile geometry, outputs, token scores and duration. All tiles
must finish; EOS alone does not establish correct formulas or layout.

| Paper / physical page | Tile retry seconds | EOS on all tiles |
|---|---:|---|
| yalcin2007 / 15 | 84.60 | Yes |
| yalcin2015 / 47 | 105.65 | Yes |

The two retries total **190.24s**, mean
**95.12s/page**. These times include rendering
and tiled inference, excluding model initialization and the already-recorded
Round 2 capped attempts. Those earlier passes took 404.61s and 415.06s;
including each retry gives 489.20s and 520.71s respectively. Fresh native intake
first tries the full page, so the retry mean is not its total worst-case latency.
9 additional pages needed VL because their earlier
whole-page acceptance had skipped it. All 9 completed with EOS in
**539.82s**, mean **59.98s/page**.
Document inference was serialized. This was not a dedicated-host benchmark.

All other results reuse literal local inference outputs and scores from prior
rounds; replay time is not reported as inference throughput. Old VL character
ranges are reconstructed from saved token IDs and their saved actual probabilities
using the pinned local tokenizer, with exact output/completion equality checked.
No fabricated page-average confidence is used for an insertion. The same pinned
models, hashes, dependencies and licenses remain in force; no new dependencies
or model downloads were needed. Approximately 19 GiB of disk remained free.

### Structural and visual spot-checks

Independent reconstruction from accepted source intervals confirms every clean
interval is unchanged. A separate subsequence check also confirms that every
original clean character inside all 131 accepted runs survives in order. All **541 healthy pages**, ten blank controls, PDF hashes
and physical numbering are preserved; the final logs contain **zero MODEL events**.
Across the 82 affected pages, whitespace-word counts are
**33131 original / 33153 repaired**;
private-use character counts are **1441 / 1009**.
Word and character totals are structural observations, not correctness labels.
Per-page counts and per-span character classes are in the ignored audit artifacts.

Terminal-only source/repaired render comparisons covered six physical pages:

- `braun2012/15`: one of two spans passes. The left damaged delimiter becomes an
  ordinary bracket; the right candidate stays flagged after the added clean-case
  guard. The original clean uppercase character is now retained. Bracket style
  is not an exact transcription of the source's corner delimiter.
- `yalcin2007/6`: two of 21 spans pass. One modal mark agrees visually with the
  source; another admitted repair turns a turnstile-like relation mark into an
  equals sign. **This is an observed recognition error among the 131 admitted
  spans**, despite unique anchors and passing confidence. The page remains
  flagged. Clean body/footnote text stays in its original extracted order;
  many glyphs and printable encoding artifacts remain unresolved.
- `yalcin2007/15`: three of seven spans pass, including numeric references.
  The displayed logic and other damaged runs remain unresolved. Tiled VL now
  completes, but that completion does not make this page clean.
- `yalcin2015/47`: none of four spans passes. The text layer's long formula block
  is badly fragmented and out of reading order, so it remains unchanged and
  flagged even though tiled OCR reaches EOS.
- `kolodnymacfarlane2010/5`: its sole damaged heading span becomes readable and
  the diagnostic clears; body and footnote text are retained. Small-cap styling
  is flattened to uppercase text, not preserved as typography.
- `yalcin2015/18`: its sole damaged calligraphic symbol becomes a LaTeX spelling
  and the diagnostic clears. The source's larger displayed formula still has
  pre-existing ordering/encoding problems outside that tainted run. **Even a
  page counted clean can therefore require source inspection.**

These checks identify limits of the requested automatic gate, not a semantic
validation of the repaired corpus. The acceptance rule was not weakened to
increase counts, and no paper-specific manual exception or guessed glyph mapping
was introduced. Do not treat the nine cleared diagnostic pages as nine verified
transcriptions. All renders and source/OCR text remain in ignored local files;
no paper passages are quoted in this report.

### Verification and local delivery

Full network-isolated pytest with both installed local-model opt-ins enabled:
**943 passed, 2 skipped, 1 warning in 550.82s (0:09:10)**. The paid-provider opt-ins remain skipped.
After that suite, **30/30 OCR production-wire controls** and then **50/50
repository controls** each failed under mutation and passed after restoration.
The three stages ran sequentially in the canonical checkout after document
inference finished. Source hashes were captured before the suite and checked
restored after both control runners. The outer shell launcher returned exit 143;
its retained child sequence completed with explicit zero-exit receipts for all
three stages. The launcher termination cause was not established. Pass claims
come from the child results and independently verified restored hashes.

The no-extra environment passed **81 tests, 2 local-model skips**. Focused
checks passed **81 tests, 2 skips** before the installed-model suite. Red-before-fix
receipts cover span admission, partial native integration, clean sparse-page
preservation, adjacent-run alignment, shorter unique anchors, and the corrected
span count. Tests also exercise ambiguous anchors, local low confidence despite
a high page mean, preserved clean characters, encoded-symbol loss, byte-token
confidence, cap retries and incomplete tiles. Lock validation, compileall and
`git diff --check` pass. No separate lint/typecheck command is configured.
The visual check exposed a clean uppercase character being changed inside a
tainted span. Three regressions failed before the exact clean-fragment guard;
the interrupted pre-fix full suite and partial replay are preserved separately
and are not final evidence. No prior inference was discarded. Span receipts are
embedded in each native page event, avoiding duplicate per-span chain writes.
Inline simplification reused span/category helpers and decoded token pieces;
it does not substitute for the operator's planned non-author review.

Evidence under `/home/dev/ara-work/rho2/runs/`:

- `ocr-round3-final/`: per-paper original/repaired intake, final per-span decisions,
  structural counts, summary, chained events and `verification.json` with source,
  origin and artifact hashes.
- `ocr-round3-capped/` and `ocr-round3-missing/`: actual new inference receipts,
  times and isolated-network namespace/route/interface records.
- `ocr-round3-research/`: reproduction scripts, terminal-only renders, red/green
  logs, `pytest-final.log`, `check-results.json`, source manifest and restoration
  receipt. `ocr-round3-controls/` contains mutation receipts; repository receipts
  are `runs/alpha-proof/negative-controls.json`.

All content stays ignored and local. Final replay also runs in `unshare -Urn`;
network receipts show no routes or traffic. The runtime Python connection guard
remains a synchronous boundary, not a general native-code sandbox. The native
audit tool can reproduce span repair on new inputs, using the setup and command
in README. Historical extraction artifacts require a new extraction run to use
these repairs. Commit is local only; non-author review remains the next step.

### Round 3 finding placement

| Action-relevant finding | Section |
|---|---|
| 1. Measured repaired/remaining spans and clean/flagged pages; no all-content guarantee | Round 3 opening; Per-paper results |
| 2. Corrected 678 inventory, cause of the old 677 count, and requested final-field interpretation | Corrected span inventory |
| 3. Unique two-sided token anchors, adjacent-run alignment, exact clean-text preservation and conservative refusals | Native span repair |
| 4. Inserted-character confidence, score mapping and calibration limits | Native span repair; VL completion and measured time |
| 5. Tier accumulation, partial diagnostics, strict refusal, native provenance/reuse and physical citations | Native span repair |
| 6. Textless-page exception, retained sparse text and remaining undetected/unalignable corruption | Native span repair |
| 7. Capped-page completion, additional VL pages, timing boundaries and saved-receipt reuse | VL completion and measured time |
| 8. Unchanged pins/licenses, no downloads and disk footprint | VL completion and measured time |
| 9. Structural preservation proof, character/word counts, exact coverage and zero MODEL events | Structural and visual spot-checks |
| 10. Terminal visual observations and residual transcription limits | Structural and visual spot-checks |
| 11. Full/no-extra/focused tests, red evidence, sequential controls, restored source and local evidence paths | Verification and local delivery |
| 12. Local isolation and guard limits, unchanged historical artifacts, local-only commit and non-author review | Verification and local delivery |

12 findings, 12 placed.

DONE rho2 round3 head=cc705c7e37ac607c1546cd8218f46bf503c99f5b spans_repaired=131/677 pages_clean=9/82 report=/home/dev/ara-work/reports/rho2-ocr.md


## Round 4

**tau2-F1 is fixed.** Local commit `9aad0132d3f78a5e18dac4f00a5e51365accbfc0` on `feat/local-ocr`, rebased onto
requested main **`7e5219a`** (`7e5219a837de0ed126c50c2dbbe8dc49036f68e9`). No push, delegation, paid calls,
credential actions, model downloads or fresh real-paper OCR inference occurred.

### Admission fix

Policy `local-ocr-v4-spans` scores only newly synthesized non-whitespace
characters corresponding to damaged glyph groups. Preserved clean fragments
contribute neither to the confidence mean nor to the low-score share. The
thresholds remain **0.95 mean confidence** and **at most 5% below 0.8**.
No aggregate threshold was raised to mask dilution.

Exact clean-fragment alignment now counts full matches, saturating at two.
Literal clean groups must match verbatim; each damaged group consumes one or
more candidate characters. Zero alignments refuses a changed clean fragment;
multiple alignments refuses ambiguous replacement boundaries. Only a unique
alignment supplies the absolute OCR ranges used for scoring. Prefix-sum dynamic
programming avoids enumerating wildcard paths. Per-span provenance records the
alignment count, synthesized ranges and confidence scope. The policy version
changes reuse identity. External token anchors, physical page numbers, strict
missing-policy refusal, partial repairs and cross-tier preservation remain intact.

The native regression attaches a low-score replacement to 30 high-score clean
characters. Replacement probabilities **0.10** and **0.94** now stay flagged,
retain the original page and publish `text_layer` rather than clearing coverage.
Their admission means are exactly the replacement scores. A **0.99** replacement
accepts even when the clean fragment has no confidence coverage. Separate tests
refuse ambiguous repeated fragments and score two separated damaged groups while
excluding the intervening clean character's low score.

### Rebase and verification

Replayed the three OCR commits from reviewed head `cc705c7` onto `7e5219a`.
**DECISIONS.md was the only conflict; both complete appended sections were kept.**
The CLI auto-merged. Exact section preservation and base ancestry were checked;
receipt: `runs/ocr-round4-research/rebase.json`.

Full offline pytest with both installed local-model tests enabled:
**987 passed, 2 skipped, 1 warning in 626.90s (0:10:26)** — **987/989**, with the two paid-provider opt-ins skipped.
Then, sequentially, **50/50 base**, **411/411 integration**, and **32/32 OCR**
production-wire mutations failed as expected and passed after restoration.
All **180 tracked-file hashes** matched the pre-suite state after every
stage, including symlink targets. The integration runner used the locked installed
environment with `UV_NO_SYNC=1` and `UV_OFFLINE=1`; all stages ran in isolated
network namespaces. No test stage overlapped a mutation runner.

The five new regression cases were observed failing before implementation.
Focused and no-extra checks each passed **86 tests, 2 installed-model skips**.
An independent exhaustive enumeration matched the alignment count and unique
ranges for **7,239** small placeholder cases. New mutation controls replace the
synthesized-only score with the old whole-span score and disable the ambiguity
refusal; both go red, then green after restoration. Existing clean-fragment and
symbol controls were updated for the new control flow. Lock validation,
compileall and `git diff --check` pass. No separate lint/typecheck is configured.

Evidence: `runs/ocr-round4-research/` contains red/focused/no-extra/full-suite logs,
source manifest, sequential gate results, alignment enumeration and final receipts.
Individual control receipts remain in `runs/alpha-proof/`, `runs/delta-controls/`
and `runs/ocr-round4-controls/`. Runs and paper content remain ignored.

### Saved-repair impact and remaining limits

Re-evaluated all **131 previously admitted Round 3 candidates**, including the
**11 VL candidates**, using their saved OCR text and actual confidence ranges.
**All 131 still pass; seven confidence values change; zero additional refusals.**
This independently agrees with tau2's observed lack of saved-corpus incidence
for F1. It is a candidate recheck, not fresh inference, a re-evaluation of earlier
rejections, or a new complete-corpus recovery count.

Round 3's **131/678 admitted spans** and **9/82 diagnostically cleared pages**
remain historical corpus results. Its observed wrong math-symbol recognition
and pre-existing formula-order/encoding problems remain unresolved. Fixing
confidence dilution does not establish correct or complete transcription.
The old extraction artifacts were not rewritten. The commit is local only;
this fixes the named review blocker without claiming a new independent review.

### Round 4 finding placement

| Action-relevant finding | Section |
|---|---|
| 1. Confidence dilution fixed; low-score refusals and high-score acceptance | Admission fix |
| 2. Exact unique clean-fragment alignment, ambiguity refusal and synthesized ranges | Admission fix |
| 3. Unchanged numeric thresholds, versioned reuse identity and preserved native behavior | Admission fix |
| 4. Requested rebase, sole conflict and both decision sections retained | Rebase and verification |
| 5. Red evidence, exact tests/controls, sequential offline gates and restored source | Rebase and verification |
| 6. Saved-candidate recheck scope, unchanged admissions and remaining recognition limits | Saved-repair impact and remaining limits |
| 7. Local-only delivery, unchanged historical artifacts and review boundary | Opening; Saved-repair impact and remaining limits |

7 findings, 7 placed.

DONE rho2 round4 head=9aad0132d3f78a5e18dac4f00a5e51365accbfc0 base=7e5219a tests=987/989 negctl=pass fixed=tau2-F1
