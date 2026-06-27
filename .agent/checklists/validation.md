# Checklist — Validation

- [ ] `uv run ruff check .` — lint passes.
- [ ] `uv run ruff format --check .` — format check passes.
- [ ] `uv run mypy aethermesh tests` — typecheck passes.
- [ ] `uv run pytest tests/unit -q` — unit tests pass.
- [ ] `uv run pytest tests/integration -q` — integration tests pass.
- [ ] `uv run pytest tests/property -q` — property tests pass.
- [ ] `uv run pytest tests/e2e -q` — E2E tests pass.
- [ ] `uv build` — build succeeds.
- [ ] `./scripts/security-check.sh` — security check passes.
- [ ] `./scripts/dependency-audit.sh` — audit passes.
- [ ] `./scripts/smoke-test.sh` — smoke passes.
- [ ] `./scripts/verify.sh` — full verify exits 0 with `verify: ok`.
