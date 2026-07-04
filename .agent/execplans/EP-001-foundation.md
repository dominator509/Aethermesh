# EP-001 — Foundation

- **Status:** Complete / Codex-audited  - **Owner:** DX  - **Phase:** 0  - **Specs:** SPEC-000

## 1. Purpose / Big Picture
Establish `pyproject.toml`, `uv` sync, `ruff` + `mypy` strict, `pytest` harness, baseline GHA CI, and a runnable `./scripts/verify.sh`.

## 2. Scope
- `pyproject.toml`, `uv.lock`, `.github/workflows/ci.yml`, `tests/conftest.py`, package stub.

## 3. Non-Goals
- No protocol code. No new deps beyond ruff/mypy/pytest/hypothesis/pip-audit/bandit/cryptography.

## 4. Context and Orientation
EP-000 confirmed `uv` and Python. This plan creates the build envelope.

## 5. Files to Read First
1. `AGENTS.md`  2. `COMMANDS.md`  3. `.agent/PLANS.md`  4. `ARCHITECTURE.md` Repository Map  5. `ENVIRONMENT.md`  6. existing `pyproject.toml` if any  7. existing `.github/workflows/` if any

## 6. Files to Change
- `.gitignore` (create/edit)
- `pyproject.toml` (create/edit)
- `uv.lock` (generated)
- `.github/workflows/ci.yml` (create)
- `tests/__init__.py`
- `tests/conftest.py`
- `tests/unit/__init__.py`
- `tests/unit/test_placeholder.py`
- `tests/integration/__init__.py`
- `tests/integration/test_placeholder.py`
- `tests/e2e/__init__.py`
- `tests/e2e/test_placeholder.py`
- `tests/property/__init__.py`
- `tests/security/__init__.py`
- `tests/security/test_smoke.py`
- `aethermesh/__init__.py` (`__version__ = "0.1.0.dev0"`)
- `aethermesh/cli/__init__.py` (stub)
- `aethermesh/common/__init__.py` (stub)
- `aethermesh/tools/__init__.py` (stub)
- `aethermesh/tools/smoke.py` (baseline smoke gate)
- `README.md` baseline

## 7. Interfaces and Contracts
`pyproject.toml` declares `requires-python = ">=3.11"` and `[project.scripts] aethermesh = "aethermesh.cli:main"`. CLI body lands in EP-005; here stub raises `NotImplementedError`.

## 8. Milestones

### M1 — Create pyproject.toml
- **Goal:** Metadata + tool configs.
- **Files to Read:** `ENVIRONMENT.md`, `TESTING.md`.
- **Files to Change:** `pyproject.toml`.
- **Exact Edits Expected:** `[project]` (name=aethermesh, version=0.1.0.dev0, license=MIT, requires-python=">=3.11", deps=["cryptography"]), `[project.optional-dependencies] dev = [ruff, mypy, pytest, pytest-cov, hypothesis, bandit, pip-audit]`, `[project.scripts] aethermesh = "aethermesh.cli:main"`, `[tool.ruff]` line-length=100, `[tool.mypy]` strict=true, `[tool.pytest.ini_options] testpaths=["tests"]`, `[tool.coverage.run] source=["aethermesh"]`.
- **Validation Command:** `uv sync --all-extras --dev`
- **Expected Result:** exit 0; `uv.lock` created.
- **Recovery:** Per AGENTS § 7.

### M2 — aethermesh package stub
- **Goal:** Package importable.
- **Files to Read:** none.
- **Files to Change:** `aethermesh/__init__.py`, `aethermesh/cli/__init__.py`.
- **Exact Edits Expected:** `aethermesh/__init__.py`: `__version__ = "0.1.0.dev0"`. `aethermesh/cli/__init__.py`: `def main() -> int: raise NotImplementedError("EP-005 implements the CLI")`.
- **Validation Command:** `uv run python -c "import aethermesh; print(aethermesh.__version__)"`
- **Expected Result:** prints `0.1.0.dev0`.
- **Recovery:** Per AGENTS § 7.

### M3 — Wire ruff + mypy
- **Goal:** Pass on empty repo.
- **Files to Read:** `pyproject.toml`.
- **Files to Change:** none if M1 complete.
- **Exact Edits Expected:** none, verify only.
- **Validation Command:** `uv run ruff check . && uv run ruff format --check . && uv run mypy aethermesh tests`
- **Expected Result:** all exit 0.
- **Recovery:** 1st → format with ruff; 2nd → `mypy --install-types --non-interactive`; 3rd → STOP.

### M4 — Pytest harness
- **Goal:** Empty pytest succeeds.
- **Files to Read:** `TESTING.md`.
- **Files to Change:** `tests/conftest.py`, test dir `__init__.py` files.
- **Exact Edits Expected:** `conftest.py` adds a no-op session fixture. Empty `__init__.py` per test dir.
- **Validation Command:** `uv run pytest -q`
- **Expected Result:** exit 0; `no tests ran`.
- **Recovery:** Per AGENTS § 7.

### M5 — Baseline CI
- **Goal:** GHA workflow runs preflight + verify.
- **Files to Read:** `DEPLOYMENT.md`, `COMMANDS.md`.
- **Files to Change:** `.github/workflows/ci.yml`.
- **Exact Edits Expected:** One job: checkout, install `uv`, run `uv sync --all-extras --dev`, run `./scripts/verify.sh`. Trigger on push + pull_request.
- **Validation Command:** `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('ci.yml ok')"`
- **Expected Result:** `ci.yml ok`.
- **Recovery:** YAML lint; minimize; STOP.

### M6 — verify.sh exits 0
- **Goal:** Full verify on empty repo.
- **Files to Read:** `scripts/*.sh`.
- **Files to Change:** add `tests/security/test_smoke.py` with `def test_smoke(): assert True`.
- **Exact Edits Expected:** minimal passing test so `security-check.sh` doesn't fail on empty dir.
- **Validation Command:** `./scripts/verify.sh`
- **Expected Result:** `verify: ok`.
- **Recovery:** Anti-fixation per step.

## 9. Concrete Steps
M1 -> M6. All executed 2026-07-03.

## 10. Validation and Acceptance
### Acceptance Criteria
- [x] `uv sync` completes. (49 packages, aethermesh 0.1.0.dev0 installed)
- [x] `uv run python -c "import aethermesh"` works. (prints `0.1.0.dev0`)
- [x] `./scripts/verify.sh` exits 0 with `verify: ok`. (full chain passes: preflight→lint→format→typecheck→unit→integration→e2e→build→security→audit→smoke)
- [x] `.github/workflows/ci.yml` parses as YAML. (`ci.yml ok`)
- [x] Full changed-file set matches Files to Change. Codex audit used `git status --short --untracked-files=all` because `git diff --name-only` omits untracked files before staging; tracked diff is `.agent/execplans/EP-001-foundation.md` and `README.md`.

## 11. Idempotence and Recovery
`uv sync` idempotent. Empty `__init__.py` files idempotent. CI workflow single-source.

## 12. Progress
- [x] M1 — pyproject.toml (created, uv sync exits 0, uv.lock generated)
- [x] M2 — Package stub (aethermesh/__init__.py, aethermesh/cli/__init__.py, + additional stubs for tools/smoke/ common)
- [x] M3 — ruff + mypy (ruff: 0 errors, format: 16 files already formatted, mypy: no issues in 16 source files)
- [x] M4 — pytest harness (tests/ with conftest.py + __init__.py per dir + 4 placeholder tests; all pass)
- [x] M5 — Baseline CI (.github/workflows/ci.yml created, YAML validates)
- [x] M6 — verify.sh (full chain: preflight: ok → verify: ok)
- [x] Final review

## 13. Surprises & Discoveries
1. **uv not on bash PATH when PowerShell spawns bash**: Shell scripts work directly in Git Bash but fail when PowerShell invokes bash (PATH not inherited). All script validation runs via Bash tool. CI uses ubuntu-latest where this won't apply.
2. **pytest exit 5 on empty test dirs**: Pytest returns exit code 5 when no tests are collected (`set -e` propagates this). Required adding placeholder test files to unit/, integration/, and e2e/ directories — not just __init__.py.
3. **hatchling needs package directory to build**: `uv sync` fails when pyproject.toml exists but aethermesh/ directory doesn't. M1 and M2 have a hidden dependency — package stubs must exist before `uv sync` can succeed.
4. **uv-managed Python is 3.13.13** while host `python` is 3.14.4. Both satisfy the >=3.11 requirement.
5. **aethermesh/tools/smoke.py needed immediately**: smoke-test.sh requires `python -m aethermesh.tools.smoke` in verify.sh chain. This module was not in EP-001's original file list but is required for M6 to pass.
6. **bandit passes on empty package**: `bandit -r aethermesh` exits 0 with no findings on the stub package. No false positives.
7. **Generated caches polluted status under Codex sandbox**: Git could not read the user-level ignore file, so Codex added repo-local `.gitignore` coverage for Python caches, build outputs, local Claude state, and local Obsidian plugins.

## 14. Decision Log
| # | Context | Decision | Alternatives | Consequences |
|---|---|---|---|---|
| D1 | pytest exit 5 ("no tests ran") breaks test scripts | Add minimal `test_placeholder.py` (assert True) to unit/, integration/, e2e/ dirs | Skip test scripts in verify.sh until later — rejected: verify.sh is the acceptance gate | 3 placeholder test files created; body lands in EP-002+ |
| D2 | smoke-test.sh needs `aethermesh.tools.smoke` module | Create `aethermesh/tools/__init__.py` + `aethermesh/tools/smoke.py` with `main()` that prints "smoke test: ok" | Remove smoke-test.sh from verify.sh — rejected: the full chain must pass per Acceptance Criteria | 2 extra files beyond original EP scope; body lands in EP-002+ |
| D3 | bandit needs `aethermesh/` source directory to scan | `aethermesh/` package already exists from M2; bandit scans the stub package successfully | N/A | No additional changes needed |
| D4 | hatchling needs `[tool.hatch.build.targets.wheel]` or a package dir | Create aethermesh/ directory first (M2 before re-running M1 validation) | Add explicit wheel config — rejected: simpler to create the package dir which is needed anyway | M1-M2 order reversed in practice; M1 validation can't pass without M2 files |
| D5 | `aethermesh/common/__init__.py` not in original EP-001 Files to Change | Created proactively as all layer stubs will need it; empty docstring only; Codex audit added it to Files to Change | Defer to EP-002 — rejected because the foundation mypy/package baseline benefits from the stub | 1 extra file from original plan; no protocol code |
| D6 | Generated Python caches and local Claude/Obsidian state appeared in `git status` | Add `.gitignore` during Codex audit and add it to Files to Change | Leave status noisy — rejected because EP handoffs depend on clean file-scope evidence | Repo-local ignore now protects cache/build/local-tool state |

## 15. Outcomes & Retrospective
- **What landed:** Complete foundation: `.gitignore`, `pyproject.toml` with 49 resolved packages, `uv.lock`, `aethermesh/` package (5 modules: __init__, cli, tools, tools.smoke, common), `tests/` tree (7 dirs, 4 tests, conftest.py), `.github/workflows/ci.yml`, updated README.md. All 11 verify.sh gates pass — `verify: ok`.
- **What changed vs plan:** Extra files beyond the original Files to Change were added to the plan during Codex audit (`.gitignore`, tools stubs, common stub, tests/__init__.py, placeholder tests, tests/security/test_smoke.py). All were required for full verify-chain or clean handoff evidence. M1+M2 ordering reversed (package needed before sync). README.md rewritten (was blueprint unpack guide, now project README).
- **Remaining risks:** Python 3.13.13 in venv vs host Python 3.14.4 — minor version drift from documented 3.11 target. GHA CI untested (workflow created but not pushed/run). `pip-audit` skips aethermesh (expected: not on PyPI). Bandit scan is trivial on stub package — will surface real issues when protocol code lands in EP-002.
- **Production-readiness impact:** Phase 0 exits. EP-002 (core domain) is fully unblocked. Every CI gate has a passing baseline. `./scripts/verify.sh` exits 0 with `verify: ok`.
