# ARA

ARA is a Python CLI for bank-constrained symbolic search. A model proposes steps;
the deterministic engine checks versioned bank forms, Z3 entailment, frozen
commitments and route closure. A fresh run builds and freezes one commitment
table (T); a verified fork reuses an existing freeze. Both paths propose targets,
search both polarities, and write from a selected route. Extraction,
model calls, decisions and accounting retain inspectable receipts.

The [operator-approved success criteria](docs/success-criteria.md) define an
acceptable pilot, a successful entry and the go/no-go dates.

## Install and try it offline

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/). Obtain the repository
from the operator and run commands from its root:

```sh
uv sync --locked
uv run pytest
uv run python - <<'PY'
from pathlib import Path
import yaml
config = yaml.safe_load(Path('config.yaml').read_text())
config.update(provider='mock', model='claude-opus-5', stages={}, fallbacks=[])
Path('runs').mkdir(exist_ok=True)
Path('runs/mock-config.yaml').write_text(yaml.safe_dump(config))
PY
uv run ara run --smoke --config runs/mock-config.yaml --run-dir runs/mock-smoke
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
| Estimate PDF extraction without generation | `uv run ara extract --profile extraction --manifest literature/manifest.yaml --fulltext-dir literature/fulltext --ocr off --provider mock --config runs/mock-config.yaml --estimate-only --run-dir runs/estimate` | [Extraction](docs/extraction.md) |
| Extract one PDF | `uv run ara extract --profile extraction --manifest literature/manifest.yaml --fulltext-dir literature/fulltext --paper-id p --run-dir runs/extraction` | Codex subscription login and default [OCR setup](docs/ocr.md) required; run the [schema preflight](docs/extraction.md#extraction-schema-preflight) first |
| Plan extraction ranges | `uv run ara plan-extraction --manifest literature/manifest.yaml --fulltext-dir literature/fulltext --paper-id p --ocr off --token-counter local --run-dir runs/extraction-plan` | Local estimates; generation disabled |
| Plan construction | `uv run ara plan-construction --literature runs/extraction/literature.extracted.txt --topic 'P' --profile pilot --token-counter local --run-dir runs/construction-plan` | [Construction](docs/construction.md); preserve extraction provenance |
| Construct and search | `uv run ara run --profile pilot --topic 'P' --literature runs/extraction/literature.extracted.txt --run-dir runs/pilot` | [Search](docs/search.md); pauses for route selection |
| Reuse a verified freeze | `uv run ara fork-from-freeze --source-run runs/source --run-dir runs/fork` | [Frozen forks](docs/search.md#reuse-a-verified-freeze); proposes new targets without rebuilding T |
| Resume stopped construction | `uv run ara resume-construction --run-dir runs/previous --unknown-usage-policy count-at-reservation` | Verified, unfrozen eligible run; may make paid calls |
| Resume stopped search | `uv run ara resume-search --run-dir runs/previous` | [Search recovery](docs/search.md#resume-a-stopped-search); may make paid calls |
| Select a route and write | `uv run ara select --run-dir runs/pilot` | Lists route IDs and prompts; accepts `--route ID` |
| Record feedback | `uv run ara feedback --run-dir runs/pilot --text 'P'` | Applies to the next draft, without changing frozen T |
| Export essay/methodology | `uv run ara export --run-dir runs/pilot` | [Accounting and export](docs/accounting.md); essay requires completed verification |
| Read one or more runs offline | `uv run ara report --run-dir runs/pilot --out runs/report` | Repeat `--run-dir`; [reporting](docs/reporting.md) |
| Compile extraction schemas live | `uv run ara schema-preflight --profile extraction-full --config config.yaml --run-dir runs/schema-P` | Subscription by default; API opt-in has a USD1 history-inclusive cap; [extraction](docs/extraction.md) |
| Validate Codex schemas live | `uv run ara codex-schema-preflight --config runs/codex.yaml --profile pilot --run-dir runs/codex-schemas` | Subscription calls; [providers](docs/providers.md#codex-cli) |

Target checks can exclude candidates, so a request for ten does not guarantee ten
searches. Default selection offers only `CLOSED-derived` routes; other routes
remain visible and require explicit `--route ID`. See [target checks and route
classification](docs/search.md#target-proposal-and-triviality).

`fork-from-freeze` is available at base `f89cd37`. It uses the source configuration
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
| `anthropic` (explicit API opt-in) | `ANTHROPIC_API_KEY`; official SDK, schema validation and explicit fallback accounting |
| `claude_code` | Claude Code subscription login, pinned full model ID and Git identity; fresh isolated calls with a budgeted canary |
| `codex_cli` (default) | Linux/bubblewrap, pinned CLI 0.163.0, explicit separate ChatGPT auth file and pinned model; matching schema preflight required for pilots |
| `mock` | Offline finite placeholder responses; no credentials |

The default is `codex_cli` / `gpt-6-luna` with no fallback for all stages,
including extraction and the pilot/full-extraction profiles. The isolation canary
and matching pilot schema preflight remain required. Full extraction still
requires explicit caps. The API adapter remains available through a private
configuration that explicitly selects its provider and models. Codex supports
rich extraction; external web retrieval still refuses, with no automatic API
fallback. See [providers](docs/providers.md) and [extraction](docs/extraction.md).


| Profile | Limits and use |
| --- | --- |
| Ordinary defaults | 200,000 tokens / USD10; ten candidates, depth 6, 500 search nodes |
| `--smoke` | 1,000,000 tokens / USD5; two candidates, depth 1, eight nodes, 150–300 words; automatic selection of a `CLOSED-derived` route, if available |
| `--profile pilot` | 10,000,000 tokens / USD100; ten candidates, depth 6, 500 nodes, 4,500–6,000 words; human selection |
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
