# Literature inputs

The manifest contains 53 bibliographic records dated 1967–2024. Its nine filing
groups contain 8, 3, 9, 6, 8, 6, 6, 3 and 4 records. Group labels organize files;
they do not establish source quality or evidential support. The collection was
selected to cover primary positions, surveys and data papers without selecting
for or against a position. Bibliographic details were entered from recall and
have not been checked against publishers; `pages` is null when unconfirmed.

- `manifest.yaml` records IDs, authors, year, title, venue, pages, group, link and
  expected PDF path.
- `references.bib` contains the same records as BibTeX.
- `fulltext/` holds local, ignored PDFs named `<id>.pdf`. Its contents depend on
  the checkout; Git does not supply the PDFs.

Bibliographic records are not extracted source evidence. Put the listed PDFs in
`fulltext/`, follow [extraction](../docs/extraction.md), then pass the resulting
`literature.extracted.txt` and its preserved provenance to `ara run`. The generic
`--literature` option also reads ordinary text, but passing a manifest alone does
not read its PDFs or establish page-linked support.

Keep substantive source text and generated outputs out of tracked files. Use
placeholder topics in committed examples, as required by [CLAUDE.md](../CLAUDE.md).
