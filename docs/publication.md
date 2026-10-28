# Publication

[Documentation index](README.md)

Publication starts from an existing draft and route; it does not search, alter T,
or license new moves. Generated artifacts remain under the ignored run directory.

```sh
uv run ara polish --run-dir runs/example --route ROUTE_ID
uv run ara figures --run-dir runs/example
uv run ara render-pdf --run-dir runs/example
```

`polish` reads `draft.json` when present, otherwise `draft.unverified.json`.
`--draft PATH` explicitly selects a saved draft. The route must exist in the run;
when omitted, the latest HUMAN selection or the sole available route is used.
Use `--unknown-usage-policy count-at-reservation` only when intentionally accepting
prior unknown usage at its reservation, as in other native resume commands.

The publication provider is pinned to isolated `claude_code` / `claude-opus-5-5`.
This command authorizes that provider for publication only; pilot routing stays
unchanged. The existing canary, forbidden-context scan, identity/credential scan,
cache, schema validation, budget and append-only receipts apply. It opens one
logical call per section and one whole-paper call. Transport retries retain their
native bounded policy; publication validation does not silently regenerate a
section. A complete adverse audit permits one targeted repair, then a full audit.
Remaining failure retains the original draft and explicitly records fallback.

The structured response contains Markdown, figure placements and a paragraph
change log. The whole paper requires a 150–200-word abstract, consecutive numbered
sections and 4,500–6,000 words excluding references and internal node markers.
Paragraph order, exact citation sequences and node-marker sequences are checked.
The reading Markdown removes internal node markers; the annotated Markdown
and native audit draft remain in publication.json. References retain exact T citations and
join bibliographic records from logged extraction inputs only when source IDs
and PDF hashes match. Conflicting records refuse. Full metadata is omitted when
no matching logged record exists; no checkout manifest supplies a replacement.
Recorded bibliography metadata is not independently verified. Native audit checks source support and
route fidelity. These are model assessments, not a semantic equivalence proof.

The native citation/originality path is attempted on accepted polish. Its external
retrieval step is unavailable through the isolated subscription provider: this is
recorded as **blocked**, returns exit 2, and does not call an API fallback. Local
citation membership is a separate check, not a replacement for external source
verification. A Markdown/PDF artifact can therefore exist with incomplete
verification. Inspect `publication.json` and methodology before treating it as a
verified paper. Publication never emits `final_draft` or changes the native essay
export. `figures` and `render-pdf` return success for their own artifact checks,
not a research-quality or submission verdict.

Artifacts live in `publication/<content-id>/`: `paper.md`, `publication.json`,
`figures/manifest.json`, SVGs, `paper.html`, `paper.pdf` and `pdf-checks.json`.
`publication/latest.json` binds the result digest; downstream commands refuse a
changed Markdown/result or route, and refuse an earlier artifact after an incomplete
later polish attempt. Figure hashes bind embedded SVG bytes. All attempts and
model versions remain in the event-derived methodology.

Figures use deterministic Python SVG layout, no AI images or external dot binary.
They show route edges/schemes/CQ status, frozen page citations and source stance.
A gap panel appears only for an open route frontier and shows its recorded
inference path. Source extraction defects are not argument gaps; no resolution
is inferred from them.

Rendering uses locked Markdown/Playwright/PDF libraries and the local Chromium
headless shell at
`~/.cache/ms-playwright/chromium_headless_shell-1200/chrome-headless-shell-linux64/chrome-headless-shell`.
HTML from Markdown is escaped, SVG is restricted to static elements, and browser
network requests are blocked. Print checks record page count, embedded fonts,
figure inventory/captions, HTML horizontal overflow and PDF glyph bounds. These
checks complement visual inspection; they cannot establish research quality.
