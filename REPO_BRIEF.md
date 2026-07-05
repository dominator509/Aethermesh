# REPO_BRIEF - AetherMesh / AEP

## Purpose
AetherMesh / AEP is a pre-production reference implementation and readiness harness for a vendor-neutral Agent Exchange Protocol. The intended production system has five layers: L1 Sphinx mixnet, L2 capability-hashed DHT, L3 Noise-PQ XK with mutual attestation, L4 PQ Double Ratchet plus MLS, and L5 macaroon-style CapTokens.

## Current Status
- Version: `0.1.0.dev0`.
- Development baseline: `AEP_PQ_BACKEND=liboqs ./scripts/verify.sh` passes.
- Production readiness: interop is scaffold-only; the perf suite now records `tests/perf/results/baseline.json`, Gates 12 and 14 now pass locally, and reference-VM perf sign-off plus ADR-0010 human sign-off still block launch.
- ADR-0010 remains Proposed; no v1.0.0 tag or external publishing until all production-readiness gates pass.
- Several layer bodies remain stubs/scaffolds; do not describe this repo as production-ready.

## Stack
- Python 3.11+, `uv`, `ruff`, `mypy`, `pytest`, `bandit`, `pip-audit`.
- Runtime package under `aethermesh/`; tests under `tests/`.
- SQLite audit/cache DB tooling under `aethermesh/tools/`.
- Docker packaging via `Dockerfile.mix-node`, `Dockerfile.gateway`, and `ops/staging/docker-compose.yml`.
- Intended production PQ backend: system `liboqs` plus Python `oqs` wrapper exposing `KeyEncapsulation` and `Signature`.
- `liboqs-python` is pinned from the upstream Git tag `0.12.0` in `pyproject.toml` / `uv.lock`.

## Important Entrypoints
- Agent guardrails: `AGENTS.md`.
- Claude/DeepSeek instructions: `CLAUDE.md`.
- Command authority: `COMMANDS.md`.
- Architecture map: `ARCHITECTURE.md`.
- Current production blocker record: `.agent/execplans/EP-010-production-readiness.md`.
- Production gates: `PRODUCTION_READINESS.md` and `.agent/specs/SPEC-008-production-readiness.md`.
- README for human setup: `README.md`.

## Commands
Run from repo root and follow `COMMANDS.md`; do not invent replacements.

| Purpose | Command |
|---|---|
| Sync deps | `uv sync --all-extras --dev` |
| Preflight | `./scripts/preflight.sh` |
| Full verify | `./scripts/verify.sh` |
| Production readiness | `./scripts/production-readiness-check.sh` |
| Unit tests | `uv run pytest tests/unit -q` |
| Integration tests | `uv run pytest tests/integration -q` |
| E2E tests | `uv run pytest tests/e2e -q` |
| Security check | `./scripts/security-check.sh` |
| Dependency audit | `./scripts/dependency-audit.sh` |
| Build | `uv build` |
| Smoke | `uv run python -m aethermesh.tools.smoke` |

Windows note: use Git Bash or `sh.exe scripts/<name>.sh` when plain PowerShell cannot run shell scripts.

## Important Directories
- `aethermesh/common/` - hashes, AEAD, canonical encoding, DIDs, PQ backend, logging, metrics.
- `aethermesh/L3_handshake/` - handshake and attestation scaffolding.
- `aethermesh/L4_ratchet/` - ratchet/session scaffolding.
- `aethermesh/L5_captokens/` - caveats and verifier.
- `aethermesh/cli/` - `aethermesh` CLI.
- `aethermesh/tools/` - smoke, health, keyring, audit/cache DB, migrations.
- `tests/` - unit, integration, e2e, property, security, interop scaffolding.
- `ops/` - dashboards, alerts, runbooks, staging compose, incidents.
- `.agent/` - ExecPlans, specs, ADRs, templates, prompts, checklists.
- `.github/workflows/` - CI, release, and staging workflows.

## Safety Notes
- Do not weaken `AGENTS.md`; it is the primary repo-local guardrail after current user instruction.
- Do not implement from `ROADMAP.md` directly; use the active ExecPlan.
- Do not add dependencies without checking `pyproject.toml` and recording the decision.
- Never commit secrets, private keys, attestation signing keys, discharger keys, or production audit logs.
- Do not read/write/delete `/var/lib/aethermesh/` or `~/.aethermesh/` without explicit permission.
- Replacing PQ placeholders with liboqs requires ADR plus explicit STOP acknowledgement.
- Do not mark ADR-0010 Accepted, push release tags, publish to PyPI/GHCR, or claim production readiness without the required human/operator gates.

## Current Unknowns / TODO
- Real layer implementations must replace remaining stubs before interop/perf claims.
- `tests/interop/external/` is absent, so the required two-implementation matrix is not available yet.
- `tests/perf/` now exists and records `tests/perf/results/baseline.json`, but L1/L3/L4 still benchmark placeholder or stub-level surfaces and no reference benchmark VM evidence is recorded yet.
- Performance reference environment and external implementation partner are still needed.
- ADR-0010 is still `Proposed`, so Gate 16 is now the first failing production-readiness gate.
