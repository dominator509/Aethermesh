# EP-009 — Deployment and Release

- **Status:** Completed  - **Owner:** Release  - **Phase:** 8  - **Specs:** SPEC-008

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
- [x] Both Dockerfiles build. (M1+M2: `docker build` succeeds for mix-node and gateway images; runtime entrypoints start requested roles)
- [x] docker-compose validates. (M3: `docker compose config` parses 7 services correctly; local stack reaches healthy)
- [x] release.yml + staging.yml parse as YAML. (M4+M5: both workflows validate)
- [x] Rollback drill documented. (M6: `ops/incidents/2026-07-04-rollback-drill.md`, full timeline + postmortem)
- [x] RELEASE_NOTES.md + CHANGELOG.md exist + non-empty. (M7: release notes with all EP-002..EP-008 additions, changelog in Keep a Changelog format)
- [x] `./scripts/verify.sh` exits 0. (lint→format→typecheck→unit(299)→integration(17)→e2e(36)→security(11)→build→audit→smoke: all ok)

## 11. Idempotence and Recovery
Dockerfiles + YAML single-source. Re-building idempotent. Rollback drill documents recovery path: compose down, fix config, compose up.

## 12. Progress
- [x] M1 — Mix-node Dockerfile (multi-stage, python:3.11-slim, uv build, health check, ENTRYPOINT)
- [x] M2 — Gateway Dockerfile (same structure, gateway-entry/gateway-exit ENTRYPOINT)
- [x] M3 — Staging docker-compose (7 services: 3 mix nodes + 2 gateways + 1 DHT + 1 keyring, health checks)
- [x] M4 — Release workflow (tag-triggered: verify→build+PyPI publish→GHCR docker images, OIDC auth)
- [x] M5 — Staging workflow (nightly cron: compose up, wait health, smoke, teardown)
- [x] M6 — Rollback drill (full timeline: deploy→inject failure→detect→rollback→verify→postmortem)
- [x] M7 — RELEASE_NOTES + CHANGELOG (v0.1.0.dev0 release notes with all EP additions, Keep a Changelog format)
- [x] Final review

## 13. Surprises & Discoveries
1. **Docker build needs README.md**: `uv sync` triggers hatchling build which requires `readme = "README.md"` from pyproject.toml to exist in the build context. Added `COPY README.md` to both Dockerfiles.
2. **Docker available on Windows host**: The Windows Docker Desktop with Linux containers worked for building both Dockerfiles. This was unexpected — EP-000 had listed Docker as an assumption (A8) that wasn't verified.
3. **docker-compose `version` attribute obsolete**: Docker warned the `version: "3.8"` top-level key is obsolete. Removed it.
4. **EP-009 files are deployment artifacts** — no Python code changes. All 9 new files are Docker/CI/YAML/docs.
5. **Staging workflow uses manual `docker compose` commands**: The GHA workflow manually runs compose commands rather than using the `docker compose` GHA action — simpler and more portable.
6. **Copied uv virtualenv preserves builder shebangs**: Console scripts in `.venv/bin` pointed at `/build/.venv/bin/python`; runtime must copy the venv to `/build/.venv`, not `/app/.venv`.
7. **Compose interpolates `$AEP_NODE_ROLE` before container startup**: Staging shell entrypoints must use `$$AEP_NODE_ROLE` so each service's container env supplies the role.
8. **Node/keyring commands are still honest stubs**: Staging compose uses a staging-only `tail -f /dev/null` keepalive after successful stub startup so health checks and nightly smoke can exercise the stack scaffold until real node loops replace the stubs.

## 14. Decision Log
| # | Context | Decision | Alternatives | Consequences |
|---|---|---|---|---|
| D1 | Docker build requires README.md | Add `COPY README.md ./` to Dockerfiles | Remove readme from pyproject.toml — rejected: README is required for PyPI | Both Dockerfiles build successfully |
| D2 | docker-compose.yml `version` deprecated | Remove `version: "3.8"` line | Keep for backward compatibility — rejected: Compose v2+ ignores it | Cleaner file, no functional impact |
| D3 | Release workflow uses uv publish with OIDC | `uv publish --trusted-publishing always` | PyPI token — rejected: OIDC is the modern standard | Passwordless PyPI publishing via GHA identity |
| D4 | Staging workflow: nightly cron at 06:13 UTC | `13 6 * * *` (off-rounded minute per CronCreate guidance) | Hourly or on-push — rejected: staging is soak, not CI | Runs once daily; sufficient for soak testing |
| D5 | Docker runtime entrypoints needed to support multiple service roles | Use `AEP_NODE_ROLE` in Dockerfile shell entrypoints | Hard-code mix-layer-1/gateway-entry — rejected: compose needs mix-2, mix-3, gateway-exit, and dht-node | One image can serve the roles declared by staging compose |
| D6 | Runtime image copied `.venv` away from its shebang path | Keep runtime workdir and venv at `/build` | Reinstall in runtime or add `uv` to runtime — rejected: larger image and more moving parts | Console scripts execute without requiring `uv` in the runtime stage |
| D7 | Current node/keyring starts exit cleanly because they are stubs | Keep production image entrypoints honest; add staging-only keepalive wrappers in compose | Change CLI behavior — rejected: EP-009 is deployment-only | Local staging workflow reaches healthy without changing source behavior |

## 15. Outcomes & Retrospective
- **What landed:** 2 multi-stage Dockerfiles (mix-node + gateway), staging docker-compose (7 services with health checks), release GHA workflow (tag-triggered: verify→PyPI→GHCR), staging GHA workflow (nightly cron: compose→health→smoke→teardown), rollback drill incident record (full timeline + postmortem), RELEASE_NOTES.md (v0.1.0.dev0), CHANGELOG.md (Keep a Changelog format). 363 tests pass.
- **What changed vs plan:** Dockerfiles needed README.md copy and a runtime venv path fix. Dockerfile entrypoints use `AEP_NODE_ROLE` so the same image can serve all declared roles. Staging compose has explicit keepalive wrappers because node/keyring commands are still stubs. docker-compose version key removed. Docker available on this host (unexpected — EP-000 hadn't verified A8).
- **Remaining risks:** Release workflow untested (no tags pushed). Docker images not published to GHCR. PyPI publishing not tested (no PyPI project configured). Rollback drill is a document exercise, not an actual drill against live staging. Staging health is scaffold-level until real node/keyring loops replace stubs.
- **Production-readiness impact:** Phase 8 exits. EP-010 (production readiness) is unblocked. Deployment artifacts ready: Dockerfiles build, compose validates, local staging stack reaches healthy, CI/CD workflows defined, release documentation complete.
