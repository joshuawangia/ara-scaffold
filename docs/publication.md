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
section. A complete adverse typed audit permits up to three targeted repair rounds,
each followed by the shared conservative audit gate on the current title, headings and body. Every round receives exact flagged sentence numbers,
text, typed roles and reason categories; only their owning blocks may change. Title/heading edits require a flag on that specific block; duplicate sentence text elsewhere grants no permission. Field offsets identify the flagged occurrence and its paragraph/block index. Unflagged blocks and separators are compared byte-for-byte.
Each numbered repair round permits two structural-validation attempts: the initial
proposal and one bounded retry. Invalid output receives the exact validator failure,
rendered before/after word counts, floor/ceiling and the sections that shrank. The
retry uses the same pre-repair candidate, flagged occurrences and round number.
Only flagged sentence spans may change, including within an allowed paragraph;
all intervening spans remain byte-identical. The editor must preserve length and
support without padding. A second invalid response ends the attempt honestly.
These retries never reset or increase the three-round semantic repair limit
(at most six repair proposals). Transport retries keep their existing policy.
Attempted and accepted repair counts and the structural-attempt bound are recorded
separately; rejected responses and validation retries remain in the event log.
Remaining failure retains the original draft and explicitly records fallback.

Publication admission uses the pinned Opus 5.5 native 1,000,000-token window,
verified against [Claude Code model configuration](https://code.claude.com/docs/en/model-config#extended-context)
and the [model catalogue](https://platform.claude.com/docs/en/models/overview).
No `[1m]` suffix is required for this model. The bound is the window minus the
provider's doubled output allowance and a positive `publication_context_margin_tokens`
(default 16,384). At the default 24,576 output setting the bound is 934,464;
native admission additionally counts request output inside that conservative bound.
This operator-authorized publication policy replaces the historical generic 200,000
bound, not the provider window or its isolation. `publication_context_policy` and
configuration receipts disclose the calculation. The separately selected Codex
auditor retains its own configured bound/window. Full source evidence and fresh
k>=3 adverse-history audits remain unchanged; requests that still exceed admission
refuse without truncation. The policy is an admission estimate, not a serving-token
measurement or a guarantee that a provider will accept a particular request.

The audit after citation verification shares the same three-round repair loop.
A late flag receives the same occurrence-bound repair permissions and fresh audit
requirements as an earlier flag. It cannot be outvoted by clean samples. Restarting
an interrupted publication recovers its last accepted repair from the append-only
log for the same route and original-draft hash; it screens that draft through the
effective providers before logging or dispatch, revalidates it, and resumes at the
next unused round. It does not rerun section or whole-paper editing. The ledger
rejects consumed-round restarts, exhausted budgets, excess structural attempts and
unfinished repair outputs rather than replenishing retries. A completed third-round
refusal stands; retain the verified pre-polish export as the fallback deliverable.

The structured response contains Markdown, figure placements and a paragraph
change log. The whole paper requires a 150–200-word abstract, consecutive numbered
sections and, by default, 3,000–6,000 reading words excluding references and internal
node markers. The minimum is an ARA publication profile setting, not a competition
rule. Prefer a tight complete paper over padding. The 6,000-word ceiling is fixed.
Set `publication_min_words` in the run configuration or use `ara polish --min-words N`
to override it for a publication attempt (integer 1–6,000). The CLI override wins;
older runs without this setting default to 3,000. This does not change the writer's
separate `essay_min_words` profile. All sections and repairs receive the effective
bounds; `publication_length_policy` records the minimum, maximum, counting basis
and editorial preference in the event-derived methodology and publication receipt.
Source evidence remains mandatory for publication audits at any word minimum.
Distinct citation and route-node inventories are checked; the publication audit checks substantive preservation after editorial restructuring.
The reading Markdown removes internal node markers; the annotated Markdown
and native audit draft remain in publication.json. References retain exact T citations and
join bibliographic records from logged extraction inputs only when source IDs
and PDF hashes match. Conflicting records refuse. Full metadata is omitted when
no matching logged record exists; no checkout manifest supplies a replacement.
Recorded bibliography metadata is not independently verified. Native audit checks source support and
route fidelity. These are model assessments, not a semantic equivalence proof.

The native citation/originality path is attempted on accepted polish through the
explicitly selected audit provider. Codex supports its native web verification;
without that selection, Claude cannot perform the retrieval step. That case is
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

## Literature positioning and editorial quality

Repeat `--literature-currency PATH` to import the initial literature-currency JSON
record and its focused followup. Each input is retained verbatim as a HUMAN event
with its SHA-256 and verification receipt. Page/section-linked read evidence,
route-specific assessments, search scope and access gaps are passed to the
polisher. Metadata-only records are excluded from substantive evidence. These
inputs do not alter frozen T, route licensing or figure support.

The optional numbered “Related work and scope of the novelty claim” section uses
separate `[lit:ID]` citations. All such citations must resolve to the logged record
and stay in that section; the section cannot acquire route-node markers. Heading
capitalization is stylistic and is compared case-insensitively by both scope checks. The
publication audit uses nu4's shared conservative gate: at least three fresh
samples (`essay_audit_samples`, minimum/default 3), the union of all flags and
unresolved adverse history for the exact audit input, and unanimous acceptance.
Favourable cached samples cannot replace a fresh call. A changed candidate receives
another full gate; an unchanged repair cannot erase prior dissent. Each receipt
identifies `audit_publication`, each sample, history and the derived verdict.
Incomplete samples fail closed. This decision rule does not guarantee semantic
truth or stable classifications. It uses native sentence-label and coverage checks with a
publication-specific prompt. Source claims, argument steps, presentation, objections
and replies have distinct roles; framing alone does not fail or satisfy route
coverage. Unsupported substance, miscitation and unmapped argument steps still
fail. Publication-specific reasons also identify misplaced literature positioning,
misplaced thesis restatements, unsupported elaboration and material changes to the
original draft. It receives the original draft and exactly the same
currency evidence. Unsupported attribution, general novelty claims, loss of
substantive limits and misuse of another proposal's search result are adverse
labels. Only bounded absence within the stated 2018–2026 search and recorded
partial anticipation are permitted. Input verification is an imported receipt,
not a new independent literature search.

Polishing can merge or remove redundant paragraphs while retaining the distinct
citation and route-node inventories. The change log follows output paragraphs;
claim-level preservation is checked by the audit, not inferred from marker
counts. Prompts call for a clear thesis, signposted argument, CQ-grounded
objections, concise limits and removal of repetitive hedging. Literature positioning
belongs only in related work; thesis statements belong only in the abstract,
introduction and conclusion. Repairs may not elaborate beyond route nodes and
answered CQs. These instructions also govern each targeted repair. Word bounds apply
to the rendered reading text before acceptance, excluding references and internal
markers. The shorter raw citation IDs in the audit copy do not impose a second
minimum. Both counts remain in the receipt.

Reading Markdown, PDF and figures use deterministic author–year citations with
physical PDF pages from provenance. Printed-page offsets are never guessed.
Bibliographic records come from hash-bound extraction inputs or the explicitly
logged currency record; missing metadata is labelled as unavailable. Raw citation
IDs and exact locators remain in `publication.json` and `citation-receipt.json`,
not the reading bibliography. The audit runs on annotated text before this
mechanical display conversion.

Whole-paper publication defaults to a 900-second isolated CLI timeout because
long structured editing output can exceed the provider's ordinary 300-second
default. An explicitly configured timeout still wins; pilot defaults and bounded
transport retries are unchanged. Exhausted timeouts retain their unknown-usage
receipts and cannot become an audited publication success.

Adjacent citations to the same work and physical page display once while retaining
each evidence ID in the receipt. Citation groups move before sentence-ending
punctuation. Equal display labels for distinct works are not collapsed.

Reading conversion removes internal node markers before citation deduplication
and punctuation placement. A retained original fallback lists only references it
actually cites; an imported currency record stays in logs when unused.

Free-form import/version notes remain in the citation receipt, not the reading
bibliography. The related-work prose and audit still receive these notes so that
substantive version and access limits are preserved.

## Imported drafts and separately selected audits

Imported drafts use the same `ModelCalls.screen_imported_draft` as writer resume.
The complete object, including unexpected fields, is screened by the publication
provider and any separately selected audit provider before schema diagnostics,
provider preflight, content-bearing logs, dispatch or fallback publication.
Direct `polish` calls repeat that screen before any publication effect.

Use `--audit-provider codex_cli` to retain Opus for all editing calls and run
`audit_publication` through the isolated Codex adapter. `--audit-model` selects its
pin; absent that override, the recorded writer model is used and must be a GPT
model. Without the flag the existing pinned Claude audit remains available.
Provider scopes share the same budget, append-only log and cache boundary, with
provider/model/settings included in cache identity. Each provider performs its
own isolation preflight. The explicitly selected audit provider also performs native citation/originality
verification, sharing the original log, cache and budget. Without a separate
audit provider, unavailable external retrieval remains explicitly blocked. It does not change pilot routing or claim stable model judgments.
The live receipt distinguishes schema/transport proof from the semantic verdict.

## Frozen citations and malformed audit history

Publication uses the writer's retained-page citation verification before external
search. References from exported drafts keep their canonical bibliography and raw
T locators in the citation receipt. An empty web result cannot remove references
verified against frozen commitments, retained pages and their recorded hashes.
Missing local evidence refuses verification; it is not evidence for deleting a
citation. External quotations and originality still follow the native retrieval
path and may remain blocked under the publication provider.

Valid adverse labels from incomplete, duplicate or otherwise malformed historical
audits remain binding. Publication-specific issues use the same flag calculation
for complete samples and partial-history recovery, including current titles,
headings and literature positioning. Such a receipt supplies adverse evidence
only, never a clean verdict. Validation-feedback retries do not change which
unchanged audit input the history belongs to. Every cited sentence is checked for
citation support regardless of its typed role; restated source premises require
their frozen evidence citations even when labelled as argument steps.

The conservative gate also reads rejected responses produced by schema retries
within its fresh samples before deciding. A valid adverse label in a malformed
response remains binding even when the corrected response is clean. Invalid
responses never count as clean samples; the gate still requires at least three
complete fresh samples. Receipts distinguish recovered adverse evidence from
those sample verdicts.

## Proposal publications

An explicitly authorized OPEN proposal retains its title-page label (in the title
or front matter) and one abstract
disclosure sentence. Its bridge is stated and defended in a clearly headed
Proposal section as the paper's argued principle, not a source claim. Every
source report must be cited and faithful, and unsupported substance cannot be
presented as established. Native proposal validation owns that contract.

Natural prose needs no sentence prefixes, paragraph ownership cues, repeated
disclaimers or mandatory status-note placement. Source discussion is allowed
inside Proposal when its citations support it and it remains distinct from the
bridge. A short Status and method note is an editorial option. Proposal currency
citations must resolve to their logged evidence; bounded-search qualifications,
read status, page/section limits and source fidelity still apply wherever cited.
The ordinary route layout and related-work rules remain unchanged.

Publication receives the native proposal/audit metadata and retains fresh k≥3
samples, union of substantive flags and adverse history. Proposal-only placement
labels are advisory; source/currency support, unsupported substance, route
coverage and original-draft fidelity still fail when violated. The raw labels
remain in the audit receipts. A clean gate is a model assessment, not proof of
semantic truth.

Only the current exact accepted export with a matching clean complete k≥3 writer
gate may use the legacy disclosure format on import. Final text and every repair
use the current native validator; the retained original export is not rewritten.
The writer's Codex-only context window stays on the separately selected Codex
auditor. The Claude editor uses the repository context-admission bound, preserving
any smaller inherited bound. The source run configuration remains unchanged.

The initial whole-paper output receives deterministic proposal metadata through
the shared insertion helper before strict validation and the fresh audit. The
model's original citation/node/figure inventories and indices are validated
first; only metadata-related paragraph/figure indices are recomputed. A receipt
binds the before/after values and retains the original model change log. Repairs
still validate strictly and cannot use insertion to alter unflagged spans.
