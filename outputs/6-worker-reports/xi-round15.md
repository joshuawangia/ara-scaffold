# Xi Round 15 — phi2 R1

Checkout `/home/dev/ara-work/xi`, branch `feat/run-report`, base
`e7e12b42e3a76dfbbb6a71dbcfee2eac9f171b1d`. Completed at `f89cd373eb3e3953bcd4ee4ad56e212ac005bcef`.
No paid calls, push, or delegation.

## Field ownership

`route_details` now keeps event metadata authoritative and nests the complete
contribution receipt under `contribution`. `classification` remains at the top
level for existing report summaries and selection disclosure. A route can
therefore retain `polarity='negation'` while its nested solver receipt records
`polarity='target'`. No contribution fields are expanded over route fields.
This fixes both the duplicate-key crash and the silent-overwrite alternative.
Contribution checks, licensing, and default selection policy are unchanged.

## Native report regression

The parametrized regression constructs licensed native closures for both
phi2 redundant-support examples, plus the necessary two-support positive
control. These are saved-route/report cases; they deliberately bypass target
admission, which still rejects the redundant targets.

The real report CLI must emit HTML and JSON for all three cases, preserve the
source files byte-for-byte, retain the event's negation polarity in the report
summary and route detail, and preserve the entire nested contribution receipt.
The two redundant routes remain `CLOSED-single-support` and are not offered by
default; the positive control remains `CLOSED-derived`. Report-time provider
and engine factories are forbidden.

Before the fix, both redundant cases reproduced the report failure; the
positive case failed the new nested-receipt contract. After the fix, all
36 focused report/contribution tests passed. Two production-wire controls
reintroduced the flat expansion and the silent polarity replacement; both
failed the regression and restored green. Evidence is under
`/home/dev/ara-work/xi/runs/xi-round15/`: `red.txt`, `focused.txt`,
`focused-controls.txt`, `focused-control-results.json`, and
`focused-restoration.json`.

## Final verification and limits

Full offline pytest passed: **1,108 passed, four skipped / 1,112 collected**
in 764.06 seconds (`pytest-full.txt`). All 205 pinned source hashes matched
afterward (`source-before.json`, `pytest-verification.json`). The four configured
skips cover live known-case/provider tests and optional local OCR/VL tests.
All **478 controls passed**, sequentially after pytest: each mutation returned
pytest exit 1 and each restored test returned exit 0. All 205 source hashes
matched after the runner, including its 47 mutable source files. Evidence:
`controls-full.txt`, `full-control-results.json`, `controls/`,
`source-after-controls.json`, and `final-verification.json` in the same task
evidence directory. `git diff --check` passed. Committed locally as `f89cd373eb3e3953bcd4ee4ad56e212ac005bcef`. The worktree is clean; the committed tree
matches all 205 verified source hashes (resolving committed symlinks). Nothing
was pushed.
The task uses placeholder inputs and fake providers. No live classifier,
paid-provider, or real-corpus synthesis result is claimed.

| Finding affecting review or use | Placement |
| --- | --- |
| Duplicate-polarity crash and authoritative event/nested receipt contract | Field ownership |
| Both native reproductions, positive control, read-only CLI proof, mutation coverage | Native report regression |
| Full-gate evidence, source restoration, local commit, and offline limits | Final verification and limits |

3 findings, 3 placed.

DONE xi round15 head=f89cd373eb3e3953bcd4ee4ad56e212ac005bcef tests=1108/1112 negctl=pass fixed=phi2-R1
