# ROADMAP

> **Do not implement directly from this file.** This roadmap is strategic only. Implementation happens through ExecPlans under `.agent/execplans/`.

## Phase 0 — Repository discovery and foundation
- **Purpose:** Confirm L1–L5 reference bundles; detect Python version, package manager, test harness; map drift between bundles and the consolidated `aethermesh/` package.
- **Dependencies:** none.
- **Exit:** EP-000 closed; `COMMANDS.md`, `ARCHITECTURE.md`, `ASSUMPTIONS.md` updated with verified facts.
- **Specs:** SPEC-000.
- **ExecPlans:** EP-000, EP-001.

## Phase 1 — Core domain
- **Purpose:** Consolidate `common/` primitives (hashes, HKDF, AEAD, PQ dispatch with placeholder + liboqs paths); lock canonical encoding.
- **Dependencies:** Phase 0.
- **Exit:** EP-002 closed; ≥ 90% coverage on `common/`; property-based round-trip tests for canonical encoding and AEAD.
- **Specs:** SPEC-001.
- **ExecPlans:** EP-002.

## Phase 2 — Data and persistence
- **Purpose:** SQLite-backed audit log, DID cache, revocation cache; migration discipline.
- **Dependencies:** Phase 1.
- **Exit:** EP-003 closed; reversible migrations; integration tests cover insert/select/migrate.
- **Specs:** SPEC-002.
- **ExecPlans:** EP-003.

## Phase 3 — API / service layer
- **Purpose:** Stable L3 handshake API + L4 session/IntentHeader API + `aethermesh.api` facade.
- **Dependencies:** Phases 1, 2.
- **Exit:** EP-004 closed; contract tests pass against pinned vectors.
- **Specs:** SPEC-003, SPEC-006.
- **ExecPlans:** EP-004.

## Phase 4 — Client / CLI layer
- **Purpose:** Ship `aethermesh` CLI (`demo`, `node`, `keyring`, `audit`); replace per-layer demos.
- **Dependencies:** Phase 3.
- **Exit:** EP-005 closed; CLI smoke tests pass; `NO_COLOR` honored.
- **Specs:** SPEC-004.
- **ExecPlans:** EP-005.

## Phase 5 — Auth, permissions, and security
- **Purpose:** Promote L3 attestation backends beyond SoftSign (TPM2, SEV-SNP, TDX, Apple SEP, StrongBox); finalize L5 caveat DSL; keyring runtime stub for two platforms.
- **Dependencies:** 1–4.
- **Exit:** EP-006 closed; per-backend tests pass on at least one TEE.
- **Specs:** SPEC-005.
- **ExecPlans:** EP-006.

## Phase 6 — Testing hardening
- **Purpose:** Coverage thresholds; fuzz Sphinx parser and caveat DSL; flaky test policy enforced.
- **Dependencies:** 1–5.
- **Exit:** EP-007 closed; coverage gates in CI; zero flaky tests over a 50-run main-branch sample.
- **ExecPlans:** EP-007.

## Phase 7 — Observability and operations
- **Purpose:** `structlog` JSON with redaction; OpenTelemetry counters and histograms; dashboards-as-code; per-layer runbooks.
- **Dependencies:** 1–6.
- **Exit:** EP-008 closed; sample dashboards load; redaction test passes.
- **Specs:** SPEC-007.
- **ExecPlans:** EP-008.

## Phase 8 — Deployment and release
- **Purpose:** PyPI wheel + mix-node/gateway Docker images; tag-triggered GHA build → test → publish; staging smoke; rollback drill.
- **Dependencies:** 1–7.
- **Exit:** EP-009 closed; `1.0.0-rc.1` published to TestPyPI; mix-node image runs in staging.
- **ExecPlans:** EP-009.

## Phase 9 — Production readiness
- **Purpose:** Replace every PQ placeholder with liboqs; pass two-implementation interop matrix; complete security review; publish 1.0.
- **Dependencies:** 1–8.
- **Exit:** EP-010 closed; `./scripts/production-readiness-check.sh` exits 0; ADR-0010 = Accepted.
- **Specs:** SPEC-008.
- **ExecPlans:** EP-010.

## Production-Readiness Milestone
When Phase 9 exits, tag `v1.0.0`.
