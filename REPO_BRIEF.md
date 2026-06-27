# REPO_BRIEF - AetherMesh / AEP

## Purpose
AetherMesh / AEP is a reference implementation blueprint for a vendor-neutral Agent Exchange Protocol. The intended production system has five layers: L1 Sphinx mixnet, L2 capability-hashed DHT, L3 Noise-PQ XK with mutual attestation, L4 PQ Double Ratchet plus MLS, and L5 macaroon-style CapTokens.

## Stack
- Current checkout shape: blueprint/control-plane docs, `.agent` specs and ExecPlans, shell scripts, and Obsidian vault config.
- Intended runtime stack from project docs: Python 3.11+, `uv`, `ruff`, `mypy`, `pytest`, `bandit`, `pip-audit`, SQLite tooling, liboqs-backed PQ crypto, and protocol modules under `aethermesh/`.
- Source package, tests, bundles, `pyproject.toml`, and `uv.lock` are not present in this directory as of this brief.

## Important Entrypoints
- Agent guardrails: `AGENTS.md`.
- Command authority: `COMMANDS.md`.
- Active first ExecPlan: `.agent/execplans/EP-000-repository-discovery.md`.
- ExecPlan rules: `.agent/PLANS.md` and `.agent/EXECUTION_RULES.md`.
- Architecture map: `ARCHITECTURE.md`.
- Production gates: `PRODUCTION_READINESS.md` and `.agent/specs/SPEC-008-production-readiness.md`.
- Existing project brief: `PROJECT_BRIEF.md`.

## Commands
Run commands from the repo root and follow `COMMANDS.md`; do not invent replacements.

| Purpose | Command |
|---|---|
| Preflight | `./scripts/preflight.sh` |
| Install/sync | `uv sync --all-extras --dev` |
| Lint | `uv run ruff check .` |
| Format check | `uv run ruff format --check .` |
| Typecheck | `uv run mypy aethermesh tests` |
| Unit tests | `uv run pytest tests/unit -q` |
| Integration tests | `uv run pytest tests/integration -q` |
| E2E tests | `uv run pytest tests/e2e -q` |
| Build | `uv build` |
| Security check | `uv run bandit -r aethermesh -ll -q` |
| Dependency audit | `uv run pip-audit` |
| Smoke | `uv run python -m aethermesh.tools.smoke` |
| Full verify | `./scripts/verify.sh` |

Note: `scripts/preflight.sh` currently requires `pyproject.toml`, so this blueprint-only checkout is expected to fail that gate until implementation files are added.

## Important Directories
- `.agent/execplans/` - EP-000 through EP-010 milestone plans.
- `.agent/specs/` - SPEC-000 through SPEC-008.
- `.agent/prompts/` - continuation, debugging, execution, and final-review prompts.
- `.agent/checklists/` - readiness, validation, release, rollback, and incident checklists.
- `.agent/templates/` - ADR, ExecPlan, runbook, spec, and test templates.
- `.obsidian/` - existing Obsidian vault configuration.
- `scripts/` - documented shell wrappers for gates.
- Intended but not currently present: `aethermesh/`, `tests/`, `bundles/`, `ops/`, `.github/workflows/`.

## Safety Notes
- Do not weaken `AGENTS.md`; it is the primary repo-local guardrail after current user instruction.
- Do not implement from `ROADMAP.md` directly; use the active ExecPlan.
- Do not add dependencies without checking `pyproject.toml` and recording the decision.
- Do not read or write `/var/lib/aethermesh/` or `~/.aethermesh/` without explicit permission.
- Never commit secrets, private keys, attestation signing keys, discharger keys, or production audit logs.
- Replacing PQ placeholders with liboqs requires ADR plus explicit STOP acknowledgement.

## Current Unknowns / TODO
- Confirm whether the actual implementation checkout lives elsewhere or has not yet been unpacked.
- Run EP-000 once this directory is a Git worktree and implementation files exist.
- Confirm package metadata, CI, test tree, and bundle demo locations when present.
