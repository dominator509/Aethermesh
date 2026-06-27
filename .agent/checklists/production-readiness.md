# Checklist — Production Readiness

Before tagging `vX.Y.Z`:

- [ ] **Functional:** 5 demos exit 0; every outcome covered by ≥ 1 E2E test; non-goals excluded.
- [ ] **Tests:** lint/format/typecheck/unit/integration/e2e/property/interop/perf/security all pass; coverage thresholds met.
- [ ] **Security:** `security-check.sh` + `dependency-audit.sh` pass; placeholder PQ rejected in prod; FORBIDDEN_LOG_KEYS enforced; ADR-0010 Accepted.
- [ ] **Privacy:** no PII; transparency log hashes only; audit retention documented.
- [ ] **Performance:** all PROJECT_BRIEF budgets met; no > 10% regression.
- [ ] **Accessibility (CLI):** `NO_COLOR=1` honored; plain-text defaults; no color-as-sole-state.
- [ ] **Observability:** every metric + alert emitted/declared; dashboards parse; redaction test passes.
- [ ] **Deployment:** PyPI + GHCR credentials rehearsed; staging smoke exit 0; multi-arch verified.
- [ ] **Rollback:** drill executed; backward migrations exercised; previous images on GHCR.
- [ ] **Backups:** audit DB backup/restore tested; WAL confirmed.
- [ ] **Docs:** README/CHANGELOG/RELEASE_NOTES current; every SPEC and ADR exists.
- [ ] **Support:** incident response reviewed; SLIs/SLOs agreed; escalation in OPERATIONS.md.
