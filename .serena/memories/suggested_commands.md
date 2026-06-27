# Suggested Commands

- RTK rule applies: prefix shell commands with `rtk`; PowerShell builtins are acceptable for simple local reads.
- Repo command authority is `COMMANDS.md`; update it with evidence before using a missing command.
- Canonical gates from repo root: `./scripts/preflight.sh`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy aethermesh tests`, `uv run pytest tests/unit -q`, `uv run pytest tests/integration -q`, `uv run pytest tests/e2e -q`, `uv build`, `uv run bandit -r aethermesh -ll -q`, `uv run pip-audit`, `uv run python -m aethermesh.tools.smoke`, `./scripts/verify.sh`.
- Current checkout is not a Git worktree at onboarding time; `rtk git status --short` fails with `fatal: not a git repository` until real repo metadata exists.
- `scripts/preflight.sh` requires `pyproject.toml` and executable script bits; in this Windows blueprint checkout it is expected to fail before implementation unpacking/Unix perms are resolved.