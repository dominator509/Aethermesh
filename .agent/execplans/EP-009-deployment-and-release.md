# EP-009 — Deployment and Release

- **Status:** Draft  - **Owner:** Release  - **Phase:** 8  - **Specs:** SPEC-008

## 1. Purpose / Big Picture
Build artifacts (PyPI wheel + GHCR images), wire tag-triggered GHA build/test/publish, ship staging docker-compose, and execute a rollback drill.

## 2. Scope
- `Dockerfile.mix-node`, `Dockerfile.gateway`
- `ops/staging/docker-compose.yml`
- `.github/workflows/{release,staging}.yml`
- `RELEASE_NOTES.md` template, `CHANGELOG.md` baseline
- Rollback drill incident note

## 3. Non-Goals
- No production deploys (operators do that).
- No mass-distribution infrastructure beyond PyPI + GHCR.

## 4. Context and Orientation
EP-008 added observability. This plan packages the result.

## 5. Files to Read First
1. `DEPLOYMENT.md`  2. `RELEASE.md`  3. `ROLLBACK.md`  4. `ENVIRONMENT.md`

## 6. Files to Change
- `Dockerfile.mix-node`, `Dockerfile.gateway`
- `ops/staging/docker-compose.yml`
- `.github/workflows/{release,staging}.yml`
- `RELEASE_NOTES.md`, `CHANGELOG.md`
- `ops/incidents/<date>-rollback-drill.md`

## 7. Interfaces and Contracts
Per DEPLOYMENT.md and RELEASE.md.

## 8. Milestones

### M1 — Mix-node Dockerfile
- **Goal:** Multi-stage `uv`-based build.
- **Files to Read:** DEPLOYMENT.md.
- **Files to Change:** `Dockerfile.mix-node`.
- **Exact Edits Expected:** Stage 1: `python:3.11-slim` + `uv` + `uv sync --no-dev --frozen`. Stage 2: runtime with `aethermesh` installed, ENTRYPOINT `aethermesh node start --role mix-layer-1`.
- **Validation Command:** `docker build -f Dockerfile.mix-node -t aethermesh-mix-node:test .`
- **Expected Result:** exit 0; image built.
- **Recovery:** Per AGENTS § 7.

### M2 — Gateway Dockerfile
- **Goal:** Mirror mix-node with `gateway-entry`/`gateway-exit` ENTRYPOINT.
- **Files to Change:** `Dockerfile.gateway`.
- **Exact Edits Expected:** Same structure; different ENTRYPOINT.
- **Validation Command:** `docker build -f Dockerfile.gateway -t aethermesh-gateway:test .`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

### M3 — Staging docker-compose
- **Goal:** Local-runnable staging.
- **Files to Change:** `ops/staging/docker-compose.yml`.
- **Exact Edits Expected:** 3 mix nodes + 1 entry gateway + 1 exit gateway + 1 DHT node + 1 keyring stub. Health checks on 9100.
- **Validation Command:** `docker compose -f ops/staging/docker-compose.yml config`
- **Expected Result:** exit 0; compose validates.
- **Recovery:** Per AGENTS § 7.

### M4 — Release workflow
- **Goal:** Tag-triggered publish.
- **Files to Read:** RELEASE.md.
- **Files to Change:** `.github/workflows/release.yml`.
- **Exact Edits Expected:** Trigger on `push: tags: ['v*']`. Jobs: `./scripts/verify.sh`, `uv build`, `uv publish` (OIDC), `docker buildx build --push` to GHCR for both images.
- **Validation Command:** `python -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml')); print('release.yml ok')"`
- **Expected Result:** prints `release.yml ok`.
- **Recovery:** Per AGENTS § 7.

### M5 — Staging workflow
- **Goal:** Nightly staging smoke.
- **Files to Change:** `.github/workflows/staging.yml`.
- **Exact Edits Expected:** Cron `0 6 * * *`. Spin up compose, run `./scripts/smoke-test.sh`, tear down.
- **Validation Command:** `python -c "import yaml; yaml.safe_load(open('.github/workflows/staging.yml')); print('staging.yml ok')"`
- **Expected Result:** prints `staging.yml ok`.
- **Recovery:** Per AGENTS § 7.

### M6 — Rollback drill
- **Goal:** Execute and document.
- **Files to Read:** ROLLBACK.md.
- **Files to Change:** `ops/incidents/<date>-rollback-drill.md`.
- **Exact Edits Expected:** Document: bring up staging on `vX.Y.Z`, simulate failure, roll back to `vX.Y.(Z-1)` per ROLLBACK.md, verify, record timeline + postmortem.
- **Validation Command:** `[ -s ops/incidents/*-rollback-drill.md ] && echo "drill recorded"`
- **Expected Result:** prints `drill recorded`.
- **Recovery:** Per AGENTS § 7.

### M7 — RELEASE_NOTES + CHANGELOG
- **Goal:** Templates ready.
- **Files to Change:** `RELEASE_NOTES.md`, `CHANGELOG.md`.
- **Exact Edits Expected:** RELEASE_NOTES.md from RELEASE.md template. CHANGELOG.md with `## Unreleased` section.
- **Validation Command:** `[ -s RELEASE_NOTES.md ] && [ -s CHANGELOG.md ] && echo "release docs ok"`
- **Expected Result:** prints `release docs ok`.
- **Recovery:** Per AGENTS § 7.

## 9. Concrete Steps
M1 -> M7.

## 10. Validation and Acceptance
### Acceptance Criteria
- [ ] Both Dockerfiles build.
- [ ] docker-compose validates.
- [ ] release.yml + staging.yml parse as YAML.
- [ ] Rollback drill documented.
- [ ] RELEASE_NOTES.md + CHANGELOG.md exist + non-empty.
- [ ] `./scripts/verify.sh` exits 0.

## 11. Idempotence and Recovery
Dockerfiles + YAML are single-source. Re-building idempotent.

## 12. Progress
- [ ] M1 — Mix-node Dockerfile
- [ ] M2 — Gateway Dockerfile
- [ ] M3 — Staging docker-compose
- [ ] M4 — Release workflow
- [ ] M5 — Staging workflow
- [ ] M6 — Rollback drill
- [ ] M7 — RELEASE_NOTES + CHANGELOG
- [ ] Final review

## 13. Surprises & Discoveries
<filled>

## 14. Decision Log
<entries>

## 15. Outcomes & Retrospective
<Filled at completion.>
- **What landed:**
- **What changed vs plan:**
- **Remaining risks:**
- **Production-readiness impact:** Phase 8 exits.
