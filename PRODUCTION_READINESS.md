# PRODUCTION_READINESS

## Definition
Production-ready when every gate below is met, `./scripts/production-readiness-check.sh` exits 0, and ADR-0010 (security sign-off) is `Accepted`.

## Functional Readiness
- [ ] All 5 layer demos: `uv run python -m aethermesh.demos.layer{1..5}` exit 0.
- [ ] Every core user outcome in PROJECT_BRIEF.md exercised by ≥ 1 E2E test.
- [ ] All non-goals remain excluded.
- [ ] No open issue tagged `release-blocker`.
- [ ] No `TODO`/`FIXME` in `aethermesh/L*/` paths.

## Test Readiness
- [ ] `uv run ruff check .` passes.
- [ ] `uv run ruff format --check .` passes.
- [ ] `uv run mypy aethermesh tests` passes.
- [ ] `uv run pytest tests/unit` passes; coverage ≥ 85% lines / ≥ 70% branches per layer.
- [ ] `uv run pytest tests/integration` passes.
- [ ] `uv run pytest tests/property` passes.
- [ ] `uv run pytest tests/e2e` passes.
- [ ] `uv run pytest tests/interop --slow` passes.
- [ ] `uv run pytest tests/perf --benchmark-only` meets PROJECT_BRIEF budgets.
- [ ] `tests/security/test_log_redaction.py` passes.
- [ ] Zero quarantined tests added this release.

## Security Readiness
- [ ] `./scripts/security-check.sh` passes.
- [ ] `./scripts/dependency-audit.sh`: zero unmitigated High / Critical.
- [ ] `AEP_PQ_BACKEND=placeholder` rejected by runtime in prod mode.
- [ ] No new crypto primitive without ADR.
- [ ] All FORBIDDEN_LOG_KEYS enforced at insertion (CI gate).
- [ ] Threat model in SECURITY.md reviewed.
- [ ] ADR-0010 (security sign-off) Accepted.

## Privacy Readiness
- [ ] No PII in any code path.
- [ ] DHT records carry no PII.
- [ ] Transparency log entries only `receipt_id` hashes.
- [ ] Audit retention policy documented in OPERATIONS.md.
- [ ] Discharge ledger biometric-gated on device side.

## Performance Readiness
- [ ] L1 fast-lane p95 ≤ 300 ms.
- [ ] L3 handshake ≤ 550 ms.
- [ ] L4 non-DH-step ≥ 200k msg/s/core.
- [ ] L5 token verify p99 ≤ 300 µs.
- [ ] Cover-rate within `AEP_COVER_RATE_PPS_ACTIVE` ±5%.
- [ ] No regression > 10% vs previous tag.

## Accessibility Readiness (CLI only)
- [ ] `NO_COLOR=1` honored.
- [ ] Plain-text default in every `--help`.
- [ ] No subcommand uses color as sole state indicator.

## Observability Readiness
- [ ] Every metric in OBSERVABILITY.md emitted.
- [ ] Every alert has a Prometheus rule under `ops/alerts/`.
- [ ] Dashboards in `ops/dashboards/` load.
- [ ] `/healthz`, `/readyz`, `/metrics` reachable on every role.
- [ ] CI redaction test passes.

## Deployment Readiness
- [ ] PyPI credentials valid; TestPyPI rehearsal done.
- [ ] GHCR push credentials valid; image rehearsal done.
- [ ] Docker images run on linux/amd64 and linux/arm64.
- [ ] DEPLOYMENT.md steps executed in staging this cycle.
- [ ] `./scripts/smoke-test.sh` returns 0 against staging.

## Rollback Readiness
- [ ] Rollback drill executed this cycle.
- [ ] Backward migrations for audit DB exercised.
- [ ] Previous release images still on GHCR.
- [ ] Rollback decision-owner documented.

## Data Readiness
- [ ] Audit DB backup/restore tested.
- [ ] SQLite WAL mode confirmed.
- [ ] `aethermesh.tools.audit_db migrate --check` passes against previous-schema fixture.

## Documentation Readiness
- [ ] `README.md` reflects current install + quick-start.
- [ ] Every public API has docstring.
- [ ] Every SPEC and ADR referenced in ROADMAP exists.
- [ ] `CHANGELOG.md` has this release's entry.
- [ ] `RELEASE_NOTES.md` exists for this release.

## Support Readiness
- [ ] Incident response checklist reviewed.
- [ ] SLIs / SLOs agreed by release lead.
- [ ] Escalation documented in OPERATIONS.md.

## Final Launch Gate
When every box ticked AND `./scripts/production-readiness-check.sh` returns `production readiness: ok`, release lead tags `vX.Y.Z`.

## Condensed Checklist
- [ ] Functional / Test / Security / Privacy / Performance / Accessibility / Observability / Deployment / Rollback / Data / Documentation / Support
- [ ] ADR-0010 Accepted
- [ ] `./scripts/production-readiness-check.sh` exits 0
