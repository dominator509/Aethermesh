# SPEC-008 — Production Readiness

- **Status:** Draft  - **Owner:** Release  - **Phase:** 9  - **ExecPlans:** EP-010

## User-Visible Goal
A single observable gate signals the project is ready to publish 1.0.

## Non-Goals
Subjective quality assessments.

## Required Behavior
`./scripts/production-readiness-check.sh` runs every gate below and exits 0 iff all pass.

## Gates (each machine-observable)
1. `./scripts/verify.sh` exits 0.
2. `AEP_PQ_BACKEND=placeholder uv run python -m aethermesh.tools.smoke --prod` exits non-zero with clear message.
3. `AEP_PQ_BACKEND=liboqs uv run python -m aethermesh.tools.smoke --prod` exits 0.
4. `uv run pytest tests/interop --slow -q` exits 0.
5. `uv run pytest tests/perf --benchmark-only --benchmark-json=tests/perf/results/baseline.json` exits 0, writes the JSON artifact, and the benchmark assertions enforce the documented budgets.
6. `uv run pytest tests/security -q` exits 0.
7. `uv run pip-audit` exits 0.
8. `./scripts/dependency-audit.sh` exits 0.
9. `tests/security/test_log_redaction.py` exits 0.
10. `aethermesh node health` exits 0 against a freshly started node.
11. `git grep -nE "TODO|FIXME" aethermesh/L1_sphinx aethermesh/L2_dht aethermesh/L3_handshake aethermesh/L4_ratchet aethermesh/L5_captokens` returns no matches.
12. `aethermesh.tools.audit_db migrate --check` exits 0.
13. `ops/dashboards/*.json` parse as valid Grafana JSON.
14. `ops/alerts/aethermesh.rules.yml` parses with `promtool check rules`.
15. `RELEASE_NOTES.md` is non-empty.
16. ADR-0010 status is `Accepted` in `DECISIONS.md`.

## Inputs / Outputs
Inputs: clean repo at candidate release commit. Outputs: exit code + per-gate summary on stdout.

## Error States
Any gate failure prints `production readiness: FAIL — <gate name>` and exits non-zero.

## Security Rules
Script never reads/writes outside repo root and audit-DB fixture directory.

## Required Tests
- `tests/e2e/test_production_readiness_script.py` invokes script against fixture repo where every gate is manipulable.

## Acceptance Criteria
- Tagged release commit makes script exit 0.
- Test that flips any gate makes script exit non-zero with expected gate name.
