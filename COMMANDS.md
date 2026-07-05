# COMMANDS.md — Allowed Commands

Coding agents must not invent commands. If a command is missing or stale, **update this file first** with evidence from the repository (`pyproject.toml`, `uv.lock`, `Makefile`) before using it.

## Working Directory Rule
All commands run from the repo root. If unsure: `cd $(git rev-parse --show-toplevel)`.

## Package Manager Rule
`uv` ≥ 0.4. Do not use `pip install` directly. Install (one-time):
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Subsequent commands must not pipe to shell.

## Canonical Commands
| Purpose | Command | Expected Success Output |
|---|---|---|
| Install / sync deps | `uv sync --all-extras --dev` | exit 0; lockfile up to date |
| Preflight | `./scripts/preflight.sh` | `preflight: ok` |
| Lint | `uv run ruff check .` | no errors |
| Format check | `uv run ruff format --check .` | `X files already formatted` |
| Format apply | `uv run ruff format .` | `X files reformatted` |
| Typecheck | `uv run mypy aethermesh tests` | `Success: no issues found` |
| Unit tests | `uv run pytest tests/unit -q` | exit 0; `N passed` |
| Integration tests | `uv run pytest tests/integration -q` | exit 0; `N passed` |
| Interop / E2E (slow) | `uv run pytest tests/interop -q --slow` | exit 0 |
| E2E (CLI) | `uv run pytest tests/e2e -q` | exit 0 |
| Property tests | `uv run pytest tests/property -q` | exit 0 |
| Performance | `uv run pytest tests/perf --benchmark-only --benchmark-json=tests/perf/results/baseline.json` | budgets met + JSON written |
| Build wheel + sdist | `uv build` | `dist/aethermesh-X.Y.Z*.{whl,tar.gz}` |
| Security check | `uv run bandit -r aethermesh -ll -q` | `No issues identified.` |
| Dependency audit | `uv run pip-audit` | `No known vulnerabilities found` |
| Smoke test | `uv run python -m aethermesh.tools.smoke` | `smoke test: ok` |
| Full verification | `./scripts/verify.sh` | `verify: ok` |
| Production readiness | `./scripts/production-readiness-check.sh` | `production readiness: ok` |
| Per-layer demo | `uv run python -m aethermesh.demos.layerN` (N=1..5) | `=== DONE ===` |
| Init audit DB | `uv run python -m aethermesh.tools.init_audit_db --path ./audit.db` | `audit db initialized at ./audit.db` |
| Bootstrap directory | `uv run python -m aethermesh.tools.bootstrap_directory --out ./directory.json` | `directory bootstrapped` |
| Audit DB migrate | `uv run python -m aethermesh.tools.audit_db migrate --path ./audit.db` | `audit db at schema vN` |
| Coverage report | `uv run pytest --cov=aethermesh --cov-report=term-missing` | `TOTAL ≥ 85%` |
| L5 verifier branch coverage | `uv run pytest tests/unit/L5/verifier/ --cov=aethermesh.L5_captokens.verifier --cov-branch --cov-fail-under=70 -q` | exit 0; `TOTAL ≥ 70%` |

## Forbidden Commands
- `pip install ...` (use `uv add` and `uv sync`).
- `curl ... | sh` outside the one-time `uv` install.
- `rm -rf` of any directory outside `./build`, `./dist`, `./.pytest_cache`.
- `sudo` (never required).
- `git push --force` to any branch except the agent's working branch.
- `python setup.py ...` (PEP 621 only).
- Any HTTP request to hostnames other than `127.0.0.1` / `localhost` or fixture files.
- Publishing a `RevocationManifest` from CI.
- Running mix-node code against the live community directory from CI.

## Recovery Instructions
| Problem | Recovery |
|---|---|
| `uv: command not found` | Install per top of file; re-source shell. |
| `ModuleNotFoundError: aethermesh` | `uv sync`. |
| `uv sync` fails on `oqs` build | Confirm `liboqs` installed; fall back to `AEP_PQ_BACKEND=placeholder` for dev only. |
| `mypy` stub errors | `uv run mypy --install-types --non-interactive`. |
| `pytest fixture not found` | Confirm `tests/conftest.py` present and importable. |
| Coverage below threshold | Add missing tests required by active ExecPlan. |
| Interop test fails | Inspect `tests/interop/results/INTEROP_REPORT.md`; never patch protocol to make a test pass. |

## Updating This File
If a needed command is genuinely missing, the agent must:
1. Confirm the tool is in `pyproject.toml` (or `uv add` it).
2. Confirm the invocation works locally.
3. Add the row above with exact command + expected output.
4. Record in active ExecPlan Decision Log.
