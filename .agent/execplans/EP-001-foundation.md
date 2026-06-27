# EP-001 — Foundation

- **Status:** Draft  - **Owner:** DX  - **Phase:** 0  - **Specs:** SPEC-000

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
- `pyproject.toml` (create/edit)
- `uv.lock` (generated)
- `.github/workflows/ci.yml` (create)
- `tests/conftest.py`
- `tests/{unit,integration,e2e,property,security}/__init__.py`
- `aethermesh/__init__.py` (`__version__ = "0.1.0.dev0"`)
- `aethermesh/cli/__init__.py` (stub)
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
M1 -> M6.

## 10. Validation and Acceptance
### Acceptance Criteria
- [ ] `uv sync` completes.
- [ ] `uv run python -c "import aethermesh"` works.
- [ ] `./scripts/verify.sh` exits 0 with `verify: ok`.
- [ ] `.github/workflows/ci.yml` parses as YAML.
- [ ] `git diff --name-only` matches Files to Change.

## 11. Idempotence and Recovery
`uv sync` idempotent. Empty `__init__.py` files idempotent. CI workflow single-source.

## 12. Progress
- [ ] M1 — pyproject.toml
- [ ] M2 — Package stub
- [ ] M3 — ruff + mypy
- [ ] M4 — pytest harness
- [ ] M5 — Baseline CI
- [ ] M6 — verify.sh
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
- **Production-readiness impact:** Phase 0 exits; EP-002+ unblocked.
