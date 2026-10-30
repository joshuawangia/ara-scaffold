# ARA outputs (temporary — delete from the repo before making it public again)

Snapshot of competition outputs. The repo is private; this folder is meant to be removed later.
Nothing here is a submission verdict. Route selection is the operator's.

## Status at a glance

| Item | File | Status |
| --- | --- | --- |
| Metapaper v5 (43 pp, 10 figures; unified under ARA base concepts; root cause: paper-isolated atomic T; §Credits) | `metapaper/metapaper.pdf` | Rendered; anonymity grep clean; marks pending work as pending |
| Route-1 paper, polished (3,471 words, 9 pp) | `papers/pi3-quality3.pdf` | Typed post-polish audit passed after 1 repair (single-sample audit, pre k=3 gate) |
| Route-1 paper, unpolished fallback (5,065 words, 12 pp) | `papers/pi3-quality4.pdf` | Polish failed (repair below 3,000 floor); fallback kept |
| Route-1 paper, first publication | `papers/pi3-publication.pdf` | Earlier version (4,743 words) |
| Route essays, round 5 (4,710 / 4,613 words) | `essays/round5/` | Native exports; final audit passed only by cache replay of a non-deterministic audit |
| Route essays, round 6 | `essays/round6/*-NO-CITATIONS.txt` | k=3 audit passed, but verification stripped every citation — not usable as-is (round 7 fixing) |
| Early drafts | `essays/drafts/` | Unverified |
| **B/2 proposal paper** (verified original, 3,168 w) | `candidates/gap1pu-B-2-proposal/paper.pdf` | ARA-proposed thesis; bridge argued. k=3 audit [0,0,0]; Opus polish refused, not used |
| **T2 proposal paper** (verified original, 3,427 w) | `candidates/gap1pu-C-T2-iff-proposal/paper.pdf` | eps2-proposed thesis (tested in ARA); bridge argued. k=3 audit [0,0,0]; polish refused |
| B/1, A/3 proposal papers | `candidates/gap1pu-B-1-proposal`, `gap1pu-A-3-proposal` | Refused: substantive audit flags after 3 repairs |
| ARA-derived (CLOSED) route paper | — | None yet: search pending packing fix (xi) and vocabulary consolidation (sigma) |

## Reports

- `reports/handoffs/gap1-handoff.md` — gap pilot 1: construction done, stopped at alignment.
- `reports/handoffs/gap1r-handoff.md` — recovery: frozen T (160), stopped at L3 target admission.
- `reports/handoffs/gap1f-handoff.md` — provider-window check (272k default, 872k max).
- `reports/eps2-L3.md`, `reports/eps2-bridge-literature.md` — literature currency (2018–2026) and L3 verdict.
- `reports/kappa4-*.md` — non-author reviews; `reports/*-round*.md` — worker reports.
- `success-criteria.md` — approved pilot and entry criteria.

Not included (too large for git): event-derived methodology for pi3 quality3/4 (~400 MB each) at
`/home/dev/ara-work/reports/papers/pi3-quality{3,4}-methodology.md`, run directories, evidence trees.

## Candidates (all routes drafted; operator selects)

`candidates/<id>/` holds each candidate's paper.pdf, paper.md and status.json (stage, words, citations,
audit flags, refusal reason). `gap-T2-analysis` is an analysis of ARA output, not an ARA-derived route.
