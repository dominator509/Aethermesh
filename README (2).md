# AetherMesh / AEP — Blueprint Pack (Pass 2 of 2: ExecPlans)

This is **Pass 2** of the AetherMesh / AEP blueprint pack. It contains all 11 ExecPlans (EP-000 through EP-010). Use it together with `aethermesh_blueprint_pass1.zip`.

## What's in Pass 2
| ExecPlan | Phase | Purpose |
|---|---|---|
| EP-000-repository-discovery.md | 0 | Discover repo state, confirm L1-L5 bundles run, map drift |
| EP-001-foundation.md | 0 | Establish pyproject.toml, uv sync, ruff/mypy, pytest harness, CI |
| EP-002-core-domain.md | 1 | Consolidate `aethermesh.common` primitives + PQ backend dispatch |
| EP-003-data-and-persistence.md | 2 | SQLite audit_db with reversible migrations |
| EP-004-api-or-service-layer.md | 3 | `aethermesh.api` facade + contract tests |
| EP-005-user-interface-or-client.md | 4 | `aethermesh` CLI (demo/node/keyring/audit/tools) |
| EP-006-auth-security-and-permissions.md | 5 | TPM2 + Apple SEP attestation; caveat DSL; keyring stub |
| EP-007-testing-hardening.md | 6 | Coverage gates; Sphinx + caveat fuzz; flaky policy; interop scaffolding |
| EP-008-observability-and-operations.md | 7 | structlog + OTel; FORBIDDEN_LOG_KEYS; health endpoints; dashboards; alerts; runbooks |
| EP-009-deployment-and-release.md | 8 | Dockerfiles; staging compose; release workflow; rollback drill |
| EP-010-production-readiness.md | 9 | liboqs swap; interop matrix; security review (ADR-0010); v1.0.0 |

## How to use Pass 2 alongside Pass 1

1. Unzip both archives at the repo root:
   ```sh
   unzip aethermesh_blueprint_pass1.zip
   unzip aethermesh_blueprint_pass2.zip
   # Merge into repo root (each pack's directory tree maps 1:1):
   cp -r aethermesh_blueprint/. /path/to/your/repo/
   cp -r aethermesh_blueprint_pass2/.agent/execplans /path/to/your/repo/.agent/
   ```

2. Read `AGENTS.md` (Pass 1) in full.

3. Run preflight:
   ```sh
   ./scripts/preflight.sh
   # expected: preflight: ok
   ```

4. Start with the first ExecPlan in strict order:
   - **EP-000** (mandatory for existing partially-built repos per ASSUMPTIONS.md A12).
   - Then EP-001, EP-002, ..., EP-010 in numeric order.
   - Each ExecPlan is self-contained per `.agent/PLANS.md`.
   - Do not skip steps. Do not implement from `ROADMAP.md` directly.

5. Use the generic invocation prompt from Pass 1's `README.md` section "How to Use This Blueprint Pack" § 4 to drive a lower-tier coding LLM through each plan.

## Sequencing rules

- One active ExecPlan at a time.
- Complete milestones in order; validate each.
- Update Progress, Surprises & Discoveries, and Decision Log as you work.
- Do not start the next ExecPlan until the current one's Outcomes & Retrospective is filled and `./scripts/verify.sh` returns `verify: ok`.

## Note on EP-010

EP-010 is the production launch gate. Its M5 (security review + ADR-0010 Accepted) and M8 (v1.0.0 tag after 72h burn-in) are explicit STOP conditions for anything destructive. The coding agent must request explicit user permission before executing them.

## License

MIT.
