# Documentation index

Start with the [project README](../README.md) for setup and command examples. Each
guide owns one concern; link to it instead of copying its procedure.

| Guide | Owns |
| --- | --- |
| [Success criteria](success-criteria.md) | Operator-approved acceptable-pilot requirements, entry requirements and go/no-go dates |
| [Extraction](extraction.md) | PDF intake, range evidence, corrections, grounding, provenance, reuse and schema preflight |
| [Construction](construction.md) | Working T, capacity planning, window allocation, resume and frozen vocabulary |
| [Search](search.md) | Target gates, route classification, frozen forks, pilot search, selection, writing and resume |
| [Providers and isolation](providers.md) | API/CLI setup, stage dispatch, isolation, retry policies and Codex schema gate |
| [Accounting](accounting.md) | Logs, budgets, measured/reserved/inherited usage, calibration and export |
| [OCR](ocr.md) | Optional local models, installation, span repair, audit and limits |
| [Proposal admission](proposal-admission.md) | Verified paper-owned OPEN targets, free admission plans and capacity gates |
| [Audit carry-over](audit-carryover.md) | Verified sentence reuse, meaning checks and persistent adverse history |
| [Publication](publication.md) | Isolated polish, deterministic figures, PDF rendering and verification status |
| [Reporting](reporting.md) | Offline reader, linked evidence, trace verification and report limits |
| [Verification](verification.md) | Check commands, evidence standards and historical live receipts |

## Agent context layers

[CLAUDE.md](../CLAUDE.md) owns repository rules; `AGENTS.md` is its symlink.
[SOURCE_MAP.md](../SOURCE_MAP.md) owns navigation. This directory owns operating
guides. [PLAN.md](../PLAN.md) owns current work status and gaps.
[DECISIONS.md](../DECISIONS.md) is append-only historical reasoning, with
supersession links. None is a substitute for reading the relevant source and
tests.

For claims about current behavior, check CLI registration and runtime bodies, then
owning tests, then these guides. Requirements and operator decisions still define
intended behavior; code absence does not cancel them. Historical test counts and
live receipts apply to their recorded revision, not automatically to the current
tree. New observations belong in a dated handoff or decision entry.

Load local context only when entering a scope. Missing child context inherits the
root; do not create duplicate instruction files for every module. New scoped
instructions need a distinct responsibility. Keep generated run evidence in
ignored directories and report its location without copying source content here.
