# Flaky Test Policy

Per TESTING.md § Flaky Test Policy. Effective 2026-07-04.

## Detection
- A test that fails **2 times in a 10-run sample** (same commit, same environment) is considered **flaky**.

## Quarantine
- Mark with `@pytest.mark.quarantined` and add a `reason` kwarg: `@pytest.mark.quarantined(reason="<link to issue>")`.
- Quarantined tests are skipped in CI via `-m "not quarantined"`.
- Quarantining does **not** satisfy any ExecPlan acceptance criterion.

## Resolution Window
- Quarantined tests **must be fixed or deleted within 14 calendar days**.
- After 14 days without resolution, the test is automatically removed from the suite.

## Re-Admission
- A quarantined test may be un-quarantined after passing **10 consecutive CI runs** on the fix branch.
- The fix PR must include a root-cause analysis in the commit message.

## Reporting
- All quarantine events are logged in `DECISIONS.md` under "Flaky Test Quarantine Log."
- The log entry includes: test path, date quarantined, reason, linked issue, resolution date.

## CI Integration
- CI runs `uv run pytest -m "not quarantined"` by default.
- A separate nightly job runs `uv run pytest -m "quarantined"` and reports any unexpected passes.

## Exclusions
- Tests that depend on external services (TPM2 hardware, Apple SEP, network) are **not flaky** if the dependency is unavailable — they must use `@pytest.mark.skipif` with the appropriate condition.
- Hypothesis tests with `@settings(deadline=...)` that timeout due to CI load are **not flaky** if they pass with `--hypothesis-profile=ci`.
