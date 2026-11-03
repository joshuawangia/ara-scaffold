# ARA

ARA is a Python CLI for bank-constrained symbolic search. A model proposes steps;
the deterministic engine checks versioned bank forms, Z3 entailment, frozen
commitments and route closure. A fresh run builds and freezes one commitment
table (T); a verified fork reuses an existing freeze. Both paths propose targets,
search both polarities, and write from a selected route. Extraction,
model calls, decisions and accounting retain inspectable receipts.

The [operator-approved success criteria](docs/success-criteria.md) define an
acceptable pilot, a successful entry and the go/no-go dates.

## Pipeline end to end

1. **Extract and inspect sources.** PDF intake retains page-linked evidence,
   accepted ranges, rejected material and provenance. Plan locally before
   generation; extraction quality still requires source inspection.
2. **Construct and freeze T.** Counted construction produces commitments and a
   symbol catalogue. Optional consolidation and alignment precede one freeze.
   Explicit proposed H premises are admitted before that freeze and retain their
   proposed status; structural checks do not prove faithful formalization.
3. **Propose targets and search.** Target gates use the verified frozen inputs.
   The engine searches both polarities and licenses steps against the versioned
   bank. Packed requests retain the declared target basis. By default, ten
   completed jobs with no accepted inference pause search with a diagnostic
   receipt; explicit resume retains sealed jobs.
4. **Choose the paper's claim.** Ordinary selection offers `CLOSED-derived`
   routes. An explicitly owned OPEN proposal uses a disclosed proposal packet.
   `admit-proposal` can admit an unformalized paper-owned target from a verified
   freeze without search, inferred edges, H admission or a new freeze. Related
   evidence is not represented as derived support.
5. **Write and check.** Native writing, source citations, typed sentence audits
   and conservative multi-sample consensus govern the draft. H-dependent writing
   retains runtime conditional disclosure. OPEN proposals retain paper ownership;
   accepted sentence carry-over never erases adverse history or repair budgets.
6. **Publish and export.** Optional polish, bounded occurrence repairs, figures
   and PDF rendering retain the native verification gates. Export and offline
   reports distinguish accepted results, partial work, refusals and costs.

Each stage writes append-only receipts. A verified fork preserves its source
artifacts and starts a separate lifecycle; resume continues the recorded one.
Read the [operating guides](docs/README.md) before live calls. Offline tests,
model judgments and symbolic validity establish different kinds of evidence.

## Install and try it offline

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/). Obtain the repository
from the operator and run commands from its root:

```sh
uv sync --locked
uv run pytest
uv run ara run --smoke --provider mock --run-dir runs/mock-smoke
uv run ara export --run-dir runs/mock-smoke
```

Mock responses cover the shipped placeholder smoke and feedback example. Other
inputs fail explicitly. Mock costs are simulated; no provider is called. The
legacy smoke fixture has no verified paper identities, so it awaits explicit
selection before writing: `uv run ara select --run-dir runs/mock-smoke --route ID`
using an ID from the recorded routes. It does not demonstrate cross-paper success.
The [verification guide](docs/verification.md) explains offline checks, negative
controls, opt-in tests and historical live receipts.

## Commands

Use a fresh empty destination for new runs, extraction, planning and reports.
Resume and selection commands use an existing run. Examples use placeholder
inputs; supply substantive topic and literature only at runtime. `p` means a
manifest paper ID. Full command options are available through `uv run ara --help`
and `uv run ara COMMAND --help`.

| Task | Command | Details |
| --- | --- | --- |
| Estimate PDF extraction without generation | `uv run ara extract --profile extraction --manifest /path/to/manifest.yaml --fulltext-dir /path/to/fulltext --ocr off --provider mock --estimate-only --run-dir runs/estimate` | [Extraction](docs/extraction.md) |
| Extract one PDF | `uv run ara extract --profile extraction --manifest /path/to/manifest.yaml --fulltext-dir /path/to/fulltext --paper-id p --run-dir runs/extraction` | API credential and default [OCR setup](docs/ocr.md) required |
| Plan extraction ranges | `uv run ara plan-extraction --manifest /path/to/manifest.yaml --fulltext-dir /path/to/fulltext --paper-id p --ocr off --token-counter local --run-dir runs/extraction-plan` | Local estimates; generation disabled |
| Plan construction | `uv run ara plan-construction --literature runs/extraction/literature.extracted.txt --topic 'P' --profile pilot --token-counter local --run-dir runs/construction-plan` | [Construction](docs/construction.md); preserve extraction provenance |
| Construct and search | `uv run ara run --profile pilot --topic 'P' --literature runs/extraction/literature.extracted.txt --run-dir runs/pilot` | [Search](docs/search.md); pauses for route selection |
| Reuse a verified freeze | `uv run ara fork-from-freeze --source-run runs/source --run-dir runs/fork` | [Frozen forks](docs/search.md#reuse-a-verified-freeze); proposes new targets without rebuilding T |
| Reuse completed construction with proposed H | `uv run ara resume-alignment --source-run runs/source --run-dir runs/h-fork --hypotheses-file runs/h.json --plan-only --output-dir runs/h-plan` | Free verified reuse plan; [H lifecycle](docs/construction.md#new-hypothesis-lifecycle-from-completed-construction) |
| Admit a paper-owned OPEN target | `uv run ara admit-proposal --source-run runs/source --run-dir runs/proposal --packet runs/proposal-request.json --plan-only` | No-copy, no-generation [admission plan](docs/proposal-admission.md); remove `--plan-only` only for actual admission |
| Resume stopped construction | `uv run ara resume-construction --run-dir runs/previous --unknown-usage-policy count-at-reservation` | Verified, unfrozen eligible run; may make paid calls |
| Resume stopped search | `uv run ara resume-search --run-dir runs/previous` | [Search recovery](docs/search.md#resume-a-stopped-search); may make paid calls |
| Select a route and write | `uv run ara select --run-dir runs/pilot` | Lists route IDs and prompts; accepts `--route ID` |
| Record feedback | `uv run ara feedback --run-dir runs/pilot --text 'P'` | Applies to the next draft, without changing frozen T |
| Export essay/methodology | `uv run ara export --run-dir runs/pilot` | [Accounting and export](docs/accounting.md); essay requires completed verification |
| Polish an existing draft | `uv run ara polish --run-dir runs/pilot --route ID` | [Publication](docs/publication.md); explicit provider and verification policy |
| Render publication artifacts | `uv run ara figures --run-dir runs/pilot` then `uv run ara render-pdf --run-dir runs/pilot` | Uses the recorded publication result |
| Read one or more runs offline | `uv run ara report --run-dir runs/pilot --out runs/report` | Repeat `--run-dir`; [reporting](docs/reporting.md) |
| Compile extraction schemas live | `uv run ara schema-preflight --profile extraction-full --config config.yaml --run-dir runs/schema-P` | Paid, USD1 history-inclusive cap; [extraction](docs/extraction.md) |
| Validate Codex schemas live | `uv run ara codex-schema-preflight --config runs/codex.yaml --profile pilot --run-dir runs/codex-schemas` | Subscription calls; [providers](docs/providers.md#codex-cli) |

Target checks can exclude candidates. The default target limit is 30;
each retained target has two polarity jobs. Default selection offers only `CLOSED-derived` routes; other routes
remain visible and require explicit `--route ID`. See [target checks and route
classification](docs/search.md#target-proposal-and-triviality).

`fork-from-freeze` uses the source configuration
with explicit provider/preflight/unknown-usage overrides and a separate cache.
`run --from-frozen` is not a supported alias. Forking may make paid calls.

`resume-construction --plan-only --output-dir runs/resume-plan` verifies restoration
and counts the next request without generation or source-run writes. The provider
counter can require network/account access. `resume-search --stop-before-dispatch`
creates no provider but **appends recovery receipts** to the source run; use a copy
when preserving an audit input. See the corresponding guides before either command.

## Providers and configuration

[config.yaml](config.yaml) contains defaults, pricing assumptions, stage overrides
and profiles. Pass `--config PATH` on commands that accept it. Resumes use their
stored configuration. Put private configuration under ignored `runs/` and keep
API keys in the environment.

| Provider | Setup and scope |
| --- | --- |
| `anthropic` (default API) | `ANTHROPIC_API_KEY`; official SDK, schema validation and explicit fallback accounting |
| `claude_code` | Claude Code subscription login, pinned full model ID and Git identity; fresh isolated calls with a budgeted canary |
| `codex_cli` | Linux/bubblewrap, pinned CLI 0.163.0, explicit separate ChatGPT auth file and pinned model; matching schema preflight required for pilots |
| `mock` | Offline finite placeholder responses; no credentials |

The API default is `claude-opus-5` with explicit `claude-opus-4-8` fallback.
Ordinary extraction uses `claude-sonnet-5-5` without fallback; `extraction-full`
uses Opus without fallback. Construction overrides can select providers/models;
search and writing overrides select model settings within the run's provider.
Both subscription transports refuse PDF extraction; extract separately with the
API. Codex permits web retrieval only for `search_evidence`; Claude Code refuses
that stage. Stage settings do not create an automatic API fallback. A requested Codex model is not verified serving
identity. Read [providers and isolation](docs/providers.md) before paid work.

| Profile | Limits and use |
| --- | --- |
| Ordinary defaults | 200,000 tokens / USD10; 30 candidates, depth 6, 500 search nodes |
| `--smoke` | 1,000,000 tokens / USD5; two candidates, depth 1, eight nodes, 150–300 words; automatic selection of a `CLOSED-derived` route, if available |
| `--profile pilot` | 10,000,000 tokens / USD100; 30 candidates, depth 6, 500 nodes, 4,500–6,000 words; human selection |
| `--profile extraction` | 6,000,000 tokens / USD30 enclosing and extraction caps |
| `--profile extraction-full` | Generation disabled until token, run USD and extraction USD caps are set; also accepted by `run` for construction settings |

Profiles are command-specific; `--smoke` and `--profile` cannot be combined.
Caps are ceilings, not forecasts or completion guarantees. Subscription calls use
local token admission; USD caps apply to API calls. [Accounting](docs/accounting.md)
separates measured usage, unknown reservations and inherited charges. Default local
OCR needs optional dependencies and pinned weights; `--ocr off` selects text-only
intake and changes source identity.

## Documentation and repository rules

[docs/README.md](docs/README.md) routes operational detail by concern.
[SOURCE_MAP.md](SOURCE_MAP.md) maps modules, entry points and tests.
[PLAN.md](PLAN.md) separates implemented behavior from deferred work.
[DECISIONS.md](DECISIONS.md) preserves the indexed decision history.

[CLAUDE.md](CLAUDE.md) is the canonical working agreement; `AGENTS.md` links to it.
Tracked examples and ordinary fixtures use placeholders. The authorized
software-engineering verification recordings are the sole fixture exception.
Keep substantive inputs, generated outputs, logs and credentials out of commits.
Model translation, attribution, OCR and audits have explicit limits; passing
schemas and offline tests do not establish source fidelity or exhaustive search.
