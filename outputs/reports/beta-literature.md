# Beta literature intake

## Format

Reviewed `/home/dev/ara-scaffold` on `main` at `5998c90b990b843ce4da111bbddfa04f7080ca6b` on 2026-10-21. Read AGENTS.md, PLAN.md, the requested README sections, and relevant decisions (B2/B5, A8, G6, R4/TH1/TH2, and pilot allowances). No tracked files changed; no network or paid calls made.

**`--literature` accepts a readable text file, not a structured bibliography schema.** The flag is a `pathlib.Path` in `ara/runtime/cli.py:38`; the non-smoke loader is exactly `args.literature.read_text()` at line 87 (smoke override at 82). Extension is irrelevant. Python's default text encoding applies; this input is UTF-8/ASCII-compatible. Missing/unreadable/undecodable files fail through the CLI's exception path. There is no per-entry field validation, YAML parsing, BibTeX parsing, minimum entry count, source resolution, or PDF extraction on this path. Even malformed YAML could be accepted as text. ARA does not require the smoke fixture's layout.

Native flow:

- `ara/runtime/cli.py:85–107`: read text, log the entire input, construct runtime, call `prepare`.
- `ara/runtime/orchestration.py:39–47`: hand the complete string to `calls.build_t`; freeze the returned commitments before target/search work.
- `ara/runtime/calls.py:208–209`: forward literature and audience to the model-call boundary.
- `ara/runtime/calls.py:60–68`: JSON-encode literature verbatim into `INPUT_JSON`; the `build_t` JSON schema constrains the **response**, not the literature file.
- `prompts/build_t.txt:2`: instruct the model to use only supplied literature and copy source identifiers verbatim. `schemas/build_t.json:33–45` and `ara/types.py:167–170` require nonempty citations, but do not check them against manifest ids. `literature/README.md:21` therefore describes a prompt instruction, not a deterministic citation-copy guarantee.

Read the actual loader and its callers plus `tests/runtime/test_cli.py:100–111` (file input and native selection boundary), `tests/runtime/test_pilot.py:19–65` (pilot input/caps/config), and their fixture factories. These tests pass text through the runtime; they do not establish a separate literature-entry parser. No such parser exists in the inspected path.

## Conversion

**53/53 entries ingested as input text; 0 failures; 0 conversion losses.**

Output: `/home/dev/ara-scaffold/runs/inputs/epistemic-modals-literature.txt`.

Because the actual input format is plain text, conversion is a byte-identical copy of `literature/manifest.yaml` to the requested `.txt` path. This preserves every id, author string, year, title, venue, page value, filing group, URL/null, expected fulltext path, and entry order. No philosophical material, summary, or interpretation was added. No code change was necessary. The file is ignored by the repository's `runs/` rule.

- Size: 13,435 bytes.
- SHA-256, source and output: `c5d822011ffa24d2aeb687d8f3cff567a3f25c7ee80aed3a979045163182c872`.
- Independently parsed the manifest to check exactly 53 entries, 53 unique ids, nine expected fields per entry, appropriate scalar/null types, and every expected `<id>.pdf` path.
- Checked all 53 BibTeX ids and bibliographic fields against the manifest; they agree under the existing author-separator/page-range formatting. BibTeX has no extra annotation fields. Conversion uses the manifest, preserving the fields omitted by the BibTeX representation.
- Executed ARA's real `cli.main` with `--profile pilot`, the output path, and placeholder topic `P`. An injected `ModelCalls` subclass intercepts `call` before dispatch; the real `prepare`, `ModelCalls.build_t`, and `ModelCalls.render` run. Assertions check exact text in both HUMAN/run-start records and rendered input JSON, and independently count the 53 records there. No provider object is created; a socket audit guard rejects attempted network connections. The probe deliberately stops before commitment generation, and its temporary run directory is removed.

Reproducible proof script: `/home/dev/ara-work/reports/beta-literature-proof.py`.
Machine-readable receipt: `/home/dev/ara-work/reports/beta-literature-proof.json`.
Run from the checkout with `.venv/bin/python /home/dev/ara-work/reports/beta-literature-proof.py`.

Additional executed checks: `test_cli.py::test_normal_run_waits_for_human_selection`, `test_pilot.py::test_pilot_config_and_caps`, all of `test_provider.py`, `test_known_verification.py`, and `test_verification_export.py` under `tests/runtime/`: **37 passed, 2 skipped in 5.67s**. `ARA_LIVE_TEST=0` and a socket audit guard were set; the gated live tests were skipped. Used the installed environment directly, without package installation or network resolution.

This proves local text ingestion and prompt preservation only. It does not prove provider context acceptance, 53 generated commitments, successful pilot completion, citation accuracy, or reading any of the cited works. Alpha can use the output path as `--literature`; no named position has been chosen here.

## Failed/lossy entries

**Failed ingestion: none. Lossy conversions: none.** No fields or entries were dropped. The following are pre-existing source-availability/metadata gaps, not conversion failures:

- All 53 expected fulltext files are absent. The complete entry inventory below enumerates the affected ids; `fulltext/` contains only an empty `.gitkeep`.
- 50 entries have `open_access_url: null`; only `hawkesteinertthrelkeld2021`, `ninan2018`, and `hollidaymandelkern2024` supply a URL. URLs were preserved but not opened or verified.
- 13 entries have `pages: null`: `kratzer2012`, `eganweatherson2011`, `braun2012`, `macfarlane2014`, `swanson2016`, `rothschild2012`, `moss2018`, `hawkesteinertthrelkeld2021`, `yalcin2015`, `mandelkern2024`, `hollidaymandelkern2024`, `bledin2014`, `khoo2015`. Null values are retained, not filled from memory.
- `literature/README.md:11` explicitly says bibliographic details were entered from recall and have not been checked against publishers. This offline task checks internal consistency, not external correctness.

Every row below passed ingestion and is preserved losslessly. Each row also has an absent PDF. The source line is the entry's `id` line; its `pages`, `open_access_url`, and `fulltext` fields are respectively +5, +7, and +8 lines.

| Entry id | Manifest source | Pages | URL |
| --- | --- | --- | --- |
| `hacking1967` | [literature/manifest.yaml:1](/home/dev/ara-scaffold/literature/manifest.yaml:1) | present | null |
| `teller1972` | [literature/manifest.yaml:10](/home/dev/ara-scaffold/literature/manifest.yaml:10) | present | null |
| `karttunen1972` | [literature/manifest.yaml:19](/home/dev/ara-scaffold/literature/manifest.yaml:19) | present | null |
| `kratzer1977` | [literature/manifest.yaml:28](/home/dev/ara-scaffold/literature/manifest.yaml:28) | present | null |
| `kratzer1981` | [literature/manifest.yaml:37](/home/dev/ara-scaffold/literature/manifest.yaml:37) | present | null |
| `kratzer1991` | [literature/manifest.yaml:46](/home/dev/ara-scaffold/literature/manifest.yaml:46) | present | null |
| `kratzer2012` | [literature/manifest.yaml:55](/home/dev/ara-scaffold/literature/manifest.yaml:55) | null | null |
| `derose1991` | [literature/manifest.yaml:64](/home/dev/ara-scaffold/literature/manifest.yaml:64) | present | null |
| `vonfintelgillies2007` | [literature/manifest.yaml:73](/home/dev/ara-scaffold/literature/manifest.yaml:73) | present | null |
| `swanson2008` | [literature/manifest.yaml:82](/home/dev/ara-scaffold/literature/manifest.yaml:82) | present | null |
| `eganweatherson2011` | [literature/manifest.yaml:91](/home/dev/ara-scaffold/literature/manifest.yaml:91) | null | null |
| `vonfintelgillies2008` | [literature/manifest.yaml:100](/home/dev/ara-scaffold/literature/manifest.yaml:100) | present | null |
| `vonfintelgillies2011` | [literature/manifest.yaml:109](/home/dev/ara-scaffold/literature/manifest.yaml:109) | present | null |
| `hawthorne2007` | [literature/manifest.yaml:118](/home/dev/ara-scaffold/literature/manifest.yaml:118) | present | null |
| `wright2007` | [literature/manifest.yaml:127](/home/dev/ara-scaffold/literature/manifest.yaml:127) | present | null |
| `dowell2011` | [literature/manifest.yaml:136](/home/dev/ara-scaffold/literature/manifest.yaml:136) | present | null |
| `schaffer2011` | [literature/manifest.yaml:145](/home/dev/ara-scaffold/literature/manifest.yaml:145) | present | null |
| `bach2011` | [literature/manifest.yaml:154](/home/dev/ara-scaffold/literature/manifest.yaml:154) | present | null |
| `braun2012` | [literature/manifest.yaml:163](/home/dev/ara-scaffold/literature/manifest.yaml:163) | null | null |
| `dorrhawthorne2013` | [literature/manifest.yaml:172](/home/dev/ara-scaffold/literature/manifest.yaml:172) | present | null |
| `eganhawthorneweatherson2005` | [literature/manifest.yaml:181](/home/dev/ara-scaffold/literature/manifest.yaml:181) | present | null |
| `egan2007` | [literature/manifest.yaml:190](/home/dev/ara-scaffold/literature/manifest.yaml:190) | present | null |
| `stephenson2007` | [literature/manifest.yaml:199](/home/dev/ara-scaffold/literature/manifest.yaml:199) | present | null |
| `macfarlane2011` | [literature/manifest.yaml:208](/home/dev/ara-scaffold/literature/manifest.yaml:208) | present | null |
| `macfarlane2014` | [literature/manifest.yaml:217](/home/dev/ara-scaffold/literature/manifest.yaml:217) | null | null |
| `rossschroeder2013` | [literature/manifest.yaml:226](/home/dev/ara-scaffold/literature/manifest.yaml:226) | present | null |
| `yalcin2007` | [literature/manifest.yaml:235](/home/dev/ara-scaffold/literature/manifest.yaml:235) | present | null |
| `yalcin2011` | [literature/manifest.yaml:244](/home/dev/ara-scaffold/literature/manifest.yaml:244) | present | null |
| `swanson2011` | [literature/manifest.yaml:253](/home/dev/ara-scaffold/literature/manifest.yaml:253) | present | null |
| `swanson2016` | [literature/manifest.yaml:262](/home/dev/ara-scaffold/literature/manifest.yaml:262) | null | null |
| `rothschild2012` | [literature/manifest.yaml:271](/home/dev/ara-scaffold/literature/manifest.yaml:271) | null | null |
| `moss2015` | [literature/manifest.yaml:280](/home/dev/ara-scaffold/literature/manifest.yaml:280) | present | null |
| `moss2018` | [literature/manifest.yaml:289](/home/dev/ara-scaffold/literature/manifest.yaml:289) | null | null |
| `hawkesteinertthrelkeld2021` | [literature/manifest.yaml:298](/home/dev/ara-scaffold/literature/manifest.yaml:298) | null | present, unverified |
| `veltman1996` | [literature/manifest.yaml:307](/home/dev/ara-scaffold/literature/manifest.yaml:307) | present | null |
| `gsv1996` | [literature/manifest.yaml:316](/home/dev/ara-scaffold/literature/manifest.yaml:316) | present | null |
| `gillies2004` | [literature/manifest.yaml:325](/home/dev/ara-scaffold/literature/manifest.yaml:325) | present | null |
| `willer2013` | [literature/manifest.yaml:334](/home/dev/ara-scaffold/literature/manifest.yaml:334) | present | null |
| `yalcin2015` | [literature/manifest.yaml:343](/home/dev/ara-scaffold/literature/manifest.yaml:343) | null | null |
| `goldstein2019` | [literature/manifest.yaml:352](/home/dev/ara-scaffold/literature/manifest.yaml:352) | present | null |
| `ninan2018` | [literature/manifest.yaml:361](/home/dev/ara-scaffold/literature/manifest.yaml:361) | present | present, unverified |
| `mandelkern2019a` | [literature/manifest.yaml:370](/home/dev/ara-scaffold/literature/manifest.yaml:370) | present | null |
| `mandelkern2019b` | [literature/manifest.yaml:379](/home/dev/ara-scaffold/literature/manifest.yaml:379) | present | null |
| `beddorgoldstein2021` | [literature/manifest.yaml:388](/home/dev/ara-scaffold/literature/manifest.yaml:388) | present | null |
| `mandelkern2024` | [literature/manifest.yaml:397](/home/dev/ara-scaffold/literature/manifest.yaml:397) | null | null |
| `hollidaymandelkern2024` | [literature/manifest.yaml:406](/home/dev/ara-scaffold/literature/manifest.yaml:406) | null | present, unverified |
| `kolodnymacfarlane2010` | [literature/manifest.yaml:415](/home/dev/ara-scaffold/literature/manifest.yaml:415) | present | null |
| `klinedinstrothschild2012` | [literature/manifest.yaml:424](/home/dev/ara-scaffold/literature/manifest.yaml:424) | present | null |
| `bledin2014` | [literature/manifest.yaml:433](/home/dev/ara-scaffold/literature/manifest.yaml:433) | null | null |
| `vonfintelgillies2010` | [literature/manifest.yaml:442](/home/dev/ara-scaffold/literature/manifest.yaml:442) | present | null |
| `knobeyalcin2014` | [literature/manifest.yaml:451](/home/dev/ara-scaffold/literature/manifest.yaml:451) | present | null |
| `khoo2015` | [literature/manifest.yaml:460](/home/dev/ara-scaffold/literature/manifest.yaml:460) | null | null |
| `lassiter2016` | [literature/manifest.yaml:469](/home/dev/ara-scaffold/literature/manifest.yaml:469) | present | null |

## Rule check

**Disposition: issues for the brain/Joshua to resolve under the literal committed-content rule; no added argument annotations found.** Joshua's commit is unchanged.

Inspected the complete committed `literature/` inventory: `manifest.yaml:1–477`, `references.bib:1–414`, `README.md:1–21`, and the empty `fulltext/.gitkeep`. All manifest records use only the nine fields listed above. All BibTeX records use only author/title/year/howpublished plus optional pages/url. There are no abstract, summary, note, argument, premise, example, or view fields, and no appended philosophical prose.

Specific content needing a rule interpretation:

1. `AGENTS.md:3–6` prohibits any philosophical argument, premise, distinction, example, or view in committed content, without an explicit bibliographic-title exception. Some exact titles express or name views: `macfarlane2011`, title “Epistemic Modals Are Assessment-Sensitive” (`manifest.yaml:211`, `references.bib:184`); `braun2012`, “An Invariantist Theory of 'Might' Might Be Right” (`manifest.yaml:166`, `references.bib:145`); `yalcin2011`, “Nonfactualism about Epistemic Modality” (`manifest.yaml:247`, `references.bib:215`); `hawkesteinertthrelkeld2021`, “Semantic Expressivism for Epistemic Modals” (`manifest.yaml:301`, `references.bib:260`). These are bibliographic titles, not Joshua's asserted views or added annotations. Nonetheless, calling the committed tree unconditionally compliant would require assuming an exception the rule does not state. `DECISIONS.md:44–50` also directs substantive topic/literature inputs to runtime rather than committed content.
2. The `group` field is human-provided classification beyond core bibliographic identity. Position-related exact labels occur at `manifest.yaml:106–178` (`contextualism`, every ninth line), `187–232` (`relativism`), `241–304` (`expressivism`), and `313–358` (`dynamic`). `README.md:11` explicitly limits them to filing labels. They do not supply arguments or establish that each author endorses a single position. The full exact label/id inventory is in Positions below; do not silently upgrade these labels to philosophical commitments.
3. `README.md:9` supplies the selection policy: “the core statements of every position in the debate, the standard surveys, and the main data papers, 1967-2024. No work was chosen for or against any position.” This is a collection-scope/selection claim beyond bibliographic metadata, not an argument or a stated endorsement. Its completeness and neutrality have not been independently verified. Lines 11 and 15–21 are filing/operational guidance; line 21's citation-copy claim has the technical limitation described in Format.

No text naming Pancivism or Cogitio, and no reference to Joshua's own corpus, was found in these files. No such source was consulted or added to the intake. This is an inspection of `literature/`, not a provenance attestation about how its list was originally compiled. The brief authorizes reporting these issues and preserving the existing selection; it does not authorize editing/reverting Joshua's commit or deciding a repository-rule exception on his behalf.

## Positions

**Four position-related filing labels are present, exactly: `contextualism`, `relativism`, `expressivism`, `dynamic`.** There is no `position` field, dedicated position-tag field, or separately supplied exact `--named-position` statement. Do not invent one from a title or filing group. The native named-position path is distinct: `ara/runtime/calls.py:211–221` passes that string to target generation and requires one returned target with exactly that text; this task does not set it.

The manifest does contain position-related filing labels. To preserve exactly what it names without paraphrasing or implying endorsements, here is the complete `group` inventory (all nine literal values, not nine selected positions):

| Exact `group` value | Entry ids |
| --- | --- |
| `foundations` | `hacking1967`, `teller1972`, `karttunen1972`, `kratzer1977`, `kratzer1981`, `kratzer1991`, `kratzer2012`, `derose1991` |
| `survey` | `vonfintelgillies2007`, `swanson2008`, `eganweatherson2011` |
| `contextualism` | `vonfintelgillies2008`, `vonfintelgillies2011`, `hawthorne2007`, `wright2007`, `dowell2011`, `schaffer2011`, `bach2011`, `braun2012`, `dorrhawthorne2013` |
| `relativism` | `eganhawthorneweatherson2005`, `egan2007`, `stephenson2007`, `macfarlane2011`, `macfarlane2014`, `rossschroeder2013` |
| `expressivism` | `yalcin2007`, `yalcin2011`, `swanson2011`, `swanson2016`, `rothschild2012`, `moss2015`, `moss2018`, `hawkesteinertthrelkeld2021` |
| `dynamic` | `veltman1996`, `gsv1996`, `gillies2004`, `willer2013`, `yalcin2015`, `goldstein2019` |
| `recent` | `ninan2018`, `mandelkern2019a`, `mandelkern2019b`, `beddorgoldstein2021`, `mandelkern2024`, `hollidaymandelkern2024` |
| `logic` | `kolodnymacfarlane2010`, `klinedinstrothschild2012`, `bledin2014` |
| `data` | `vonfintelgillies2010`, `knobeyalcin2014`, `khoo2015`, `lassiter2016` |

The completion marker's `positions=4` counts these four distinct position-related filing labels, not four complete philosophical propositions or operator selections. `contextualism`, `relativism`, `expressivism`, and `dynamic` are retained above exactly as written, along with their ids. No broader position name is inferred from `dynamic`. There are zero explicit selectable position statements; alpha should not automatically use a filing label as `--named-position`.

## Retrieval

**ARA can invoke Anthropic's server-side web search for post-draft verification. It has no implemented manifest/PDF intake retrieval step.**

- `ara/runtime/providers.py:152–163` attaches `{"type": "web_search_20260209", "name": "web_search", "max_uses": N}` only when call kind is `search_evidence`. `build_t`, target generation, and the other call kinds receive no web tool from this code. There is no registered web-fetch tool here.
- `config.yaml:17` sets `web_search_max_uses: 5`. Pilot overlays lines 47–60 and does not override this, so pilot permits at most five searches per evidence call. Smoke overrides it to one at line 38. Pilot evidence output allowance is 64,000 tokens (line 56); classification allowance is 48,000 (line 57). `providers.py:165–177` counts the initial input and reserves a configured context window plus output/tool usage for possible search iterations; `179–190` uses streaming for these larger requests. Tool availability and a maximum do not guarantee a search is actually invoked.
- `ara/runtime/orchestration.py:82–92`: write draft → first essay audit → verification/search → cleanup → second essay audit → final draft/export. A pilot that is still awaiting human route selection has not reached this evidence stage.
- `ara/runtime/calls.py:338–387` inventories bibliography entries and double-quoted spans, calls `search_evidence` even with an empty inventory, then performs a separate schema-validated citation/originality classification using that evidence. `prompts/search_evidence.txt:2` asks for searches of draft claims and every listed item. It does not request retrieval of all 53 selected works before commitment construction.
- `calls.py:153–161` rejects bad provider stops/server-tool error blocks and extracts evidence URLs only from actual `web_search_result` blocks. Nonempty evidence text with zero URLs can still pass the evidence acquisition stage. Classification requires supported URLs for verified items/non-unverified originality; quotation checks at `362–381` require an exact whitespace-normalized excerpt match, preferring URL-bound API citations and otherwise a classifier-copied excerpt present in evidence. Source attribution remains model-assessed. Unverified items are removed at `388–399`; this is not exhaustive originality or source-truth proof.

Historical evidence inspected offline:

| Receipt | Observed retrieval | Limit |
| --- | --- | --- |
| `runs/mock-smoke/events.jsonl:65`, 2026-10-20 | `search_evidence` MODEL event has `server_tool_uses: 0` | Mock fixture execution, not live retrieval; model-name fields alone do not establish a real call. |
| `tests/fixtures/verification/responses.json:58`, `prior_statement`, 2026-10-10 23:48:11 UTC | One billed search; 10 distinct result URLs | Recorded historical software-engineering known case. |
| Same file `:610`, `real_quote`, 23:44:04 UTC | One billed search; 9 distinct result URLs | Evidence reused from an earlier call, explicitly marked in the recording. |
| Same file `:1146`, `altered_quote`, 23:44:48 UTC | One billed search; 9 distinct result URLs | Reused historical evidence. |
| Same file `:1651`, `real_citation`, 23:45:55 UTC | One billed search; 10 distinct result URLs | Reused historical evidence. |
| Same file `:2276`, `fabricated_citation`, 23:46:45 UTC | One billed search; 9 distinct result URLs | Reused historical evidence. |

The five stored evidence responses report `claude-opus-5` as serving model. `tests/runtime/test_known_verification.py:61–92` validates prompt/request hashes and replays these recorded responses through ModelCalls, cleanup and export; that replay passed here. The historical recording's ledger total is USD 3.372215, not spend incurred by beta. The historical placeholder smoke described in PLAN.md/README did not invoke web search; the later known-case receipts provide a narrower positive retrieval observation. These recordings do not establish that this epistemic-modals pilot will search, locate the selected literature, or complete. No new live retrieval was attempted.

`literature/fulltext/` is an empty storage convention described in `literature/README.md:7`. Every manifest `fulltext` path is an expected path relative to `literature/`, not content. Source search for `fulltext`, `open_access_url`, `manifest.yaml`, and `references.bib` found no matching loader/reference in `ara/`, prompts, or Python tests. The actual CLI/build-T path reads only the explicitly passed text file. Copying PDFs into that directory would not automatically extract, upload, or supply their text; the copied paths in the `.txt` input remain metadata. Likewise the three manifest URLs are not followed at intake. Consequently the current input supplies 53 bibliographic records, not the texts or arguments of 53 works, and post-draft web verification cannot retroactively ground the already frozen T in newly fetched source texts.

Handoff finding placement audit:

| Finding | Deliverable section carrying it |
| --- | --- |
| F1. Text-only loader; all 53 records preserved; offline proof stops before generation/provider acceptance | Format; Conversion |
| F2. Verbatim citation ids are instructed, not checked against manifest ids | Format |
| F3. All PDFs absent; directory/URLs have no intake retrieval wiring | Failed/lossy entries; Retrieval |
| F4. Recall-based metadata, 13 null page fields, 50 null URLs; external correctness unverified | Failed/lossy entries |
| F5. No argument annotations, but literal committed-content rule/title/group boundary needs operator interpretation | Rule check |
| F6. No explicit selectable positions; exact filing labels/id associations preserved without inference | Positions |
| F7. Web search occurs only after drafting/audit; it does not populate the initial frozen commitment table | Retrieval |
| F8. Historical search evidence exists, but no new topic/pilot retrieval or completion was tested; validation remains partial | Conversion; Retrieval |

**8 findings, 8 placed.**

Next unresolved step: the brain/Joshua resolves the committed bibliographic-content rule boundary and any exact position selection; alpha uses the ignored intake file for its separately authorized pilot and reports actual retrieval/source-grounding behavior. No tracked edits, commits, provider calls, or source downloads were made by beta.
