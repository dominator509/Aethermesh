# TESTING

## Test Pyramid
Unit ~70% / Integration ~20% / E2E ~7% / Interop ~3%.

## Unit Test Rules
- `tests/unit/L{1..5}/` mirroring layer layout.
- Every branching public function gets a test.
- No mocking of crypto primitives. Inject fixed key material via existing constructors for determinism.
- Use `hypothesis` for serialize→deserialize, encrypt→decrypt, attenuate→verify-chain.
- Coverage: ≥ 85% lines per layer; ≥ 70% branches on `L5_captokens.verifier` DSL.

## Integration Test Rules
- `tests/integration/`; compose L1+L2+L3+L4+L5 in-process via `aethermesh.L1_sphinx.testing` simulator.
- No real network sockets. ≤ 2 s wall-clock each on the reference VM.

## E2E / Acceptance Test Rules
- `tests/e2e/`; drive `aethermesh` CLI via `subprocess`.
- Assert exit 0 + documented success marker (`=== DONE ===`, `verify: ok`).

## Interop Test Rules
- `tests/interop/`; two implementations exchange wire traffic against vectors in `tests/vectors/`.
- Marker `@pytest.mark.slow`.
- Failures are protocol bugs. Do not modify wire format to make tests pass without SPEC change + ADR.

## Contract Test Rules
- Every public API change → contract test in `tests/contracts/` pinning signature + semantics.
- Removing / renaming a public symbol requires one minor release of deprecation.

## Smoke Test Rules
- `aethermesh.tools.smoke`; ≤ 5 s; exit 0 on clean install.
- Validates per-layer demos; CapToken mint+verify round-trip; intent/message key split releases body key only on ALLOW.

## Regression Test Rules
- Every fixed bug ships with a test that fails before, passes after. File: `test_regression_<issue>.py`.

## Performance Test Rules
- `tests/perf/`; `@pytest.mark.perf`. Targets from `PROJECT_BRIEF.md`.
- Regression > 10% from previous tagged release fails CI.

## Accessibility Test Rules (CLI only)
- CLI honors `NO_COLOR=1`; plain text default; color not sole state indicator.
- CI: `NO_COLOR=1 uv run aethermesh demo --check`.

## Security Test Rules
- Replay rejection: every L1 mix test includes a duplicate packet ⇒ reject.
- Scope subset: every L5 test includes scope violation ⇒ `DENY_SCOPE`.
- Revocation epoch fail-closed: every L5 test includes stale epoch ⇒ `DENY_REVOKED_EPOCH`.
- Unknown caveat fail-closed: every L5 test includes malformed caveat ⇒ `DENY_UNKNOWN_CAVEAT`.

## Test Data Rules
- `tests/vectors/` per-vector README; all labeled `TEST_ONLY`. No real DIDs / keys / attestation chains.

## Mocking Rules
- Allowed: mocking attestation backend (fixed quote) in `tests/conftest.py`.
- Forbidden: mocking AEAD, HKDF, X25519, ML-KEM, ML-DSA, any signature. No monkey-patching `aethermesh.common.*` in unit tests.

## Fixture Rules
- Shared in `tests/conftest.py`; per-scope in `tests/<scope>/conftest.py`. No network access.

## Required Tests Per Feature
1. Unit tests for new behavior.
2. ≥ 1 regression / failure-mode test.
3. Update relevant contract test if public API changed.
4. Smoke step in `aethermesh.tools.smoke` if user-observable.

## Validation Matrix
| Type | Command | Merge | Release |
|---|---|---|---|
| Lint | `uv run ruff check .` | yes | yes |
| Format | `uv run ruff format --check .` | yes | yes |
| Typecheck | `uv run mypy aethermesh tests` | yes | yes |
| Unit | `uv run pytest tests/unit` | yes | yes |
| Integration | `uv run pytest tests/integration` | yes | yes |
| E2E | `uv run pytest tests/e2e` | yes | yes |
| Property | `uv run pytest tests/property` | yes | yes |
| Performance | `uv run pytest tests/perf --benchmark-only` | no | yes (baseline) |
| Interop | `uv run pytest tests/interop --slow` | nightly | yes |
| Security | `./scripts/security-check.sh` | yes | yes |
| Audit | `./scripts/dependency-audit.sh` | yes | yes |
| Smoke | `./scripts/smoke-test.sh` | yes | yes |
| Full verify | `./scripts/verify.sh` | yes | yes |

## Flaky Test Policy
- 2 spurious fails in 10-run sample ⇒ `@pytest.mark.skip(reason="quarantined: <link>")` + open issue.
- Quarantined tests must be fixed or deleted within 14 days.
- Quarantining does not satisfy any ExecPlan acceptance criterion.

## Definition of Test Done
- Required tests from ExecPlan exist and pass.
- Coverage thresholds met on touched modules.
- No quarantined tests added by this milestone.
- ExecPlan's validation command returned its expected result.
