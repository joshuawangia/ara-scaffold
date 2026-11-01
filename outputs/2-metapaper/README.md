# ARA methods paper v8

Open **metapaper.pdf**: 23 pages, comprising a one-page executive summary, 20 pages of main text and a two-page appendix. This edition is written for a human reader interested in how ARA generates philosophical targets, arguments and papers. An executive summary introduces the method; sections 1–8 follow source construction, gap detection, licensed search, hypothesis premises, writing, the safety–retraction example, human direction and outputs. A short appendix supplies evidence pointers, central references and all 43 worker names plus the orchestrator.

The paper replaces the earlier incident chronology with an explanation of the method. The audited T2 and B/2 originals, the rendered gap analysis and the proposed conditional derivation retain distinct statuses. Earlier editions preserve the full incident record and route atlas.

**metapaper.md** is the editable manuscript. **data.json** contains source hashes, the evidence scope, numerical inputs, figure specifications and the internal finding-placement record. **verification.json** records executed checks and the final artifact manifest. **preview-*.png** provides page contact sheets.

Regenerate diagrams with `python make_figures.py`; the script uses only the Python standard library and fixed SVG geometry. Render with `python render_pdf.py` in an environment containing markdown-it-py, Playwright, pypdf, pypdfium2 and Pillow, plus the local Chromium build selected in the script. Browser networking is blocked. SVG bytes are deterministic; PDF bytes are not claimed deterministic.

This edition makes no new ARA generation or polish calls and does not alter the delivered candidate papers. Its rendering and evidence checks are separate from the native audits of those papers. No external publication or delegation was performed.

Section 8 includes the accepted consolidation prefix of 22 batches / 181 commitments. The additional operator-requested shared-predicate measurement had not been supplied at rendering and is explicitly pending. No value or completed replacement freeze is inferred.
