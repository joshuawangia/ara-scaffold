# ARA outputs (temporary — delete from the repo before making it public again)

Snapshot of competition outputs. The repo is private; this folder is meant to be removed later.
Nothing here is a submission verdict. Route selection is the operator's.

## Status at a glance

| Item | File | Status |
| --- | --- | --- |
| Metapaper v3 (methodology, 26 pp, 8 deterministic figures; honest novelty status) | `metapaper/metapaper.pdf` | Rendered; anonymity grep clean; marks pending work as pending |
| Route-1 paper, polished (3,471 words, 9 pp) | `papers/pi3-quality3.pdf` | Typed post-polish audit passed after 1 repair (single-sample audit, pre k=3 gate) |
| Route-1 paper, unpolished fallback (5,065 words, 12 pp) | `papers/pi3-quality4.pdf` | Polish failed (repair below 3,000 floor); fallback kept |
| Route-1 paper, first publication | `papers/pi3-publication.pdf` | Earlier version (4,743 words) |
| Route essays, round 5 (4,710 / 4,613 words) | `essays/round5/` | Native exports; final audit passed only by cache replay of a non-deterministic audit |
| Route essays, round 6 | `essays/round6/*-NO-CITATIONS.txt` | k=3 audit passed, but verification stripped every citation — not usable as-is (round 7 fixing) |
| Early drafts | `essays/drafts/` | Unverified |
| L3 gap paper | — | Not yet produced: gap search running from the gap1r freeze |

## Reports

- `reports/handoffs/gap1-handoff.md` — gap pilot 1: construction done, stopped at alignment.
- `reports/handoffs/gap1r-handoff.md` — recovery: frozen T (160), stopped at L3 target admission.
- `reports/handoffs/gap1f-handoff.md` — provider-window check (272k default, 872k max).
- `reports/eps2-L3.md`, `reports/eps2-bridge-literature.md` — literature currency (2018–2026) and L3 verdict.
- `reports/kappa4-*.md` — non-author reviews; `reports/*-round*.md` — worker reports.
- `success-criteria.md` — approved pilot and entry criteria.

Not included (too large for git): event-derived methodology for pi3 quality3/4 (~400 MB each) at
`/home/dev/ara-work/reports/papers/pi3-quality{3,4}-methodology.md`, run directories, evidence trees.
