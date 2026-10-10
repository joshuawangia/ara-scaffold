# Verification recordings

`cases.json` specifies the five known software-engineering cases, independent
expected verdicts, and exact source provenance. `responses.json` contains real
provider responses, prompts, complete request objects and SHA-256 hashes,
requested/served models, capture dates, usage and costs. No response text is
synthesized for the primary replay tests. The adverse-classifier test explicitly
changes only the altered quotation's verdict to exercise the local exact check.

Run offline with:

```sh
uv run pytest -q tests/runtime/test_known_verification.py tests/runtime/test_verification_export.py
uv run python tests/runtime/theta_negative_controls.py
```

The live test skips unless `ARA_LIVE_TEST=1`. Source credentials into the shell
without printing them, then run:

```sh
ARA_LIVE_TEST=1 uv run pytest -q -s tests/runtime/test_known_verification.py::test_live_known_cases
```

Receipts are written under ignored `runs/theta-verification-*`. The test-local
USD4 cap covers its whole event ledger. To resume that same ledger and reuse
already paid evidence, set `ARA_VERIFICATION_RUN` to that run directory. This
does not reset its spend. A fully cached run cannot count as a live-test pass.
Do not blindly rerun a fresh ledger without accounting for prior live spend.

Review a new recording before replacing `responses.json`; do not change the
independent expected outcomes to match a changed model response. Web retrieval
and source attribution can drift. The committed fixtures are historical evidence,
not a guarantee that future calls will produce identical text or source choices.
The export assertions exercise verification/cleanup/export; the existing native
CLI tests separately cover the writer and route-audit lifecycle.
