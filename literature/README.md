# Literature: epistemic modals

53 works. Groups: foundations 8, survey 3, contextualism 9, relativism 6, expressivism 8, dynamic 6, recent 6, logic 3, data 4.

- `manifest.yaml`: one record per work (id, authors, year, title, venue, pages, group, link, expected full-text path).
- `references.bib`: the same records as BibTeX.
- `fulltext/`: empty. Each PDF goes here named `<id>.pdf`.

Selection rule: the core statements of every position in the debate, the standard surveys, and the main data papers, 1967-2024. No work was chosen for or against any position.

`group` is a filing label only. `pages` is null where the range was not confirmed. Bibliographic details were entered from recall and have not been checked against publishers.

## Use with ara

Pass one of these files as the run-time literature, e.g.

```
uv run ara run --profile pilot --topic "<topic>" --literature literature/manifest.yaml --run-dir runs/epistemic-modals
```

`manifest.yaml` carries ids that `build_t` copies verbatim into citations; `references.bib` is the same set as BibTeX.
