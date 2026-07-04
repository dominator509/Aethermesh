# EP-010 — Production Readiness

- **Status:** Stopped  - **Owner:** Release + Security  - **Phase:** 9  - **Specs:** SPEC-008

## 1. Purpose / Big Picture
Swap placeholder PQ to liboqs, pass two-implementation interop matrix, complete security review (ADR-0010 = Accepted), run `./scripts/production-readiness-check.sh`, tag v1.0.0.

## 2. Scope
- liboqs swap-in.
- Interop matrix results.
- Performance benchmark baseline.
- ADR-0010.
- v1.0.0-rc.1 then v1.0.0 tags.

## 3. Non-Goals
- No new features.
- No new attestation backends beyond what EP-006 produced.

## 4. Context and Orientation
EP-008 added observability. EP-009 added release infra. This plan flips production switches and executes the launch gate.

## 5. Files to Read First
1. `PRODUCTION_READINESS.md`  2. `SPEC-008-production-readiness.md`  3. `DECISIONS.md` (ADR-0010 row)  4. `SECURITY.md`

## 6. Files to Change
- `pyproject.toml` (add `oqs` dep)
- `tests/interop/results/INTEROP_REPORT.md`
- `tests/perf/results/baseline.json`
- `.agent/decisions/ADR-0010-security-signoff.md`
- `DECISIONS.md` (ADR-0010 -> Accepted)
- `RELEASE_NOTES.md` (1.0.0 entry)
- `CHANGELOG.md` (1.0.0 entry)

## 7. Interfaces and Contracts
Per SPEC-008 § Gates.

## 8. Milestones

### M1 — Install liboqs
- **Goal:** `oqs` package available.
- **Files to Read:** `ENVIRONMENT.md`.
- **Files to Change:** `pyproject.toml` (add `oqs` to deps).
- **Exact Edits Expected:** `uv add oqs`. Confirm `liboqs` system package installed (operator task; document in note).
- **Validation Command:** `uv run python -c "import oqs; print(oqs.__version__)"`
- **Expected Result:** prints version.
- **Recovery:** If liboqs system package missing → STOP and request operator install.

### M2 — Full suite with liboqs
- **Goal:** Every test passes with real PQ.
- **Files to Change:** none.
- **Exact Edits Expected:** none.
- **Validation Command:** `AEP_PQ_BACKEND=liboqs ./scripts/verify.sh`
- **Expected Result:** `verify: ok`.
- **Recovery:** Per AGENTS § 7.

### M3 — Interop matrix
- **Goal:** Two-implementation interop passes.
- **Files to Read:** `tests/interop/conftest.py` (from EP-007).
- **Files to Change:** `tests/interop/results/INTEROP_REPORT.md`.
- **Exact Edits Expected:** Record matrix: per layer x per scenario pass/fail against pinned reference impl in `tests/interop/external/`.
- **Validation Command:** `AEP_PQ_BACKEND=liboqs uv run pytest tests/interop --slow -q`
- **Expected Result:** exit 0; INTEROP_REPORT.md updated.
- **Recovery:** Per AGENTS § 7. Interop failures are protocol bugs; do not patch tests to make them pass.

### M4 — Performance baseline
- **Goal:** Budgets met on reference VM; results recorded.
- **Files to Read:** PROJECT_BRIEF.md budgets.
- **Files to Change:** `tests/perf/results/baseline.json`.
- **Exact Edits Expected:** Run benchmarks; record p95 + p99 per category.
- **Validation Command:** `uv run pytest tests/perf --benchmark-only --benchmark-json=tests/perf/results/baseline.json`
- **Expected Result:** budgets met (L1 p95 <=300ms, L3 <=550ms, L4 >=200k msg/s/core, L5 verify p99 <=300us).
- **Recovery:** Per AGENTS § 7.

### M5 — Security review + ADR-0010
- **Goal:** Security lead signs off; ADR-0010 -> Accepted.
- **Files to Read:** SECURITY.md threat model, all SPECs.
- **Files to Change:** `.agent/decisions/ADR-0010-security-signoff.md`, `DECISIONS.md`.
- **Exact Edits Expected:** New ADR with security review findings. Update `DECISIONS.md` table row for ADR-0010 to `Accepted`.
- **Validation Command:** `grep -q "^| ADR-0010 | Accepted" DECISIONS.md && echo "ADR-0010 accepted"`
- **Expected Result:** prints `ADR-0010 accepted`.
- **Recovery:** This requires a human sign-off — if security lead not available, STOP condition (legal/security judgement).

### M6 — production-readiness-check.sh
- **Goal:** Script exits 0.
- **Files to Change:** none (script from Pass 1).
- **Exact Edits Expected:** none.
- **Validation Command:** `./scripts/production-readiness-check.sh`
- **Expected Result:** `production readiness: ok`.
- **Recovery:** Per failing gate, anti-fixation. Each gate failure indicates which other milestone is incomplete.

### M7 — v1.0.0-rc.1
- **Goal:** RC published to TestPyPI.
- **Files to Change:** `pyproject.toml` (version=`1.0.0-rc.1`), `aethermesh/__init__.py`, `RELEASE_NOTES.md`, `CHANGELOG.md`.
- **Exact Edits Expected:** Version bump; RC entry in changelog; release-notes section.
- **Validation Command:** `git tag v1.0.0-rc.1 && git push origin v1.0.0-rc.1 && sleep 60 && curl -sf https://test.pypi.org/pypi/aethermesh/1.0.0rc1/json | head -1`
- **Expected Result:** TestPyPI shows RC wheel.
- **Recovery:** Per AGENTS § 7. STOP if PyPI/GHCR credentials missing.

### M8 — v1.0.0 final
- **Goal:** Final tag after 72h burn-in on staging.
- **Files to Change:** `pyproject.toml` (version=`1.0.0`), `aethermesh/__init__.py`.
- **Exact Edits Expected:** Version bump; final changelog entry.
- **Validation Command:** `git tag v1.0.0 && git push origin v1.0.0`
- **Expected Result:** tag pushed; GHA release workflow publishes to PyPI + GHCR.
- **Recovery:** 72h burn-in is non-negotiable. If any SEV-1/SEV-2 in the window, STOP and abort release per ROLLBACK.md.

## 9. Concrete Steps
M1 -> M8 in strict order. Do not skip M5 or M6.

## 10. Validation and Acceptance
### Acceptance Criteria
- [ ] `AEP_PQ_BACKEND=liboqs ./scripts/verify.sh` exits 0. **BLOCKED — STOP: liboqs Python binding not available.**
- [ ] Interop matrix passes. **NOT REACHED — blocked by M1.**
- [ ] Performance budgets met. **NOT REACHED — blocked by M1.**
- [ ] ADR-0010 = Accepted in DECISIONS.md. **BLOCKED — requires human security lead sign-off (AGENTS.md STOP condition).**
- [ ] `./scripts/production-readiness-check.sh` exits 0. **BLOCKED — stops at Gate 3 because liboqs binding is unavailable.**
- [ ] v1.0.0 tag pushed. **BLOCKED — all preceding gates must pass.**

## 11. Idempotence and Recovery
Tags are not idempotent — once pushed, v1.0.0 cannot be un-tagged without harm. The RC step is the rehearsal.

## 12. Progress
- [ ] M1 — Install liboqs (**STOP: no valid `oqs`/liboqs Python binding is importable in this environment. Requires operator-installed system `liboqs` C library plus matching Python binding.**)
- [ ] M2 — Full suite with liboqs (**BLOCKED by M1**)
- [ ] M3 — Interop matrix (**NOT REACHED: blocked by M1**)
- [ ] M4 — Performance baseline (**NOT REACHED: blocked by M1**)
- [ ] M5 — Security review + ADR-0010 (draft ADR document written at `.agent/decisions/ADR-0010-security-signoff.md`; status remains **Proposed** and not accepted)
- [ ] M6 — production-readiness-check.sh (**BLOCKED: Gate 3 fails because liboqs binding is unavailable**)
- [ ] M7 — v1.0.0-rc.1 (**BLOCKED: requires M6 all-gates-pass**)
- [ ] M8 — v1.0.0 final (**BLOCKED: requires M7 + 72h burn-in**)
- [x] Final review

## 13. Surprises & Discoveries
1. **liboqs binding unavailable locally**: `uv run python -c m=__import__('oqs')` fails with `ModuleNotFoundError: No module named 'oqs'`. EP-010 M1 is a STOP condition until the operator installs system `liboqs` plus the matching Python binding.
2. **Smoke `--prod` gate now fails honestly**: Updated `aethermesh.tools.smoke` to reject `AEP_PQ_BACKEND=placeholder` and to reject `AEP_PQ_BACKEND=liboqs` when the actual `oqs.KeyEncapsulation`/`oqs.Signature` binding API is unavailable.
3. **Production readiness check stops at Gate 3**: Gate 1 (`verify.sh`) and Gate 2 (placeholder rejected) pass; Gate 3 fails because liboqs is unavailable. Later gates were not treated as passed.
4. **ADR-0010 draft is not sign-off**: `.agent/decisions/ADR-0010-security-signoff.md` exists as a draft blocker record, but `DECISIONS.md` remains Proposed and no human security sign-off is recorded.

## 14. Decision Log
| # | Context | Decision | Alternatives | Consequences |
|---|---|---|---|---|
| D1 | liboqs Python binding not available | STOP — record as infrastructure blocker. Operator must install system `liboqs` plus the matching Python binding | Treat `AEP_PQ_BACKEND=liboqs` as sufficient — rejected: it would false-green Gate 3 | Placeholder PQ backend remains dev-only; production readiness cannot pass |
| D2 | Smoke `--prod` previously checked only the environment value | Require the actual liboqs Python API in `--prod` smoke mode | Accept any non-placeholder value — rejected: false production-readiness signal | Gate 3 now fails honestly until liboqs is installed |
| D3 | ADR-0010 requires human security review | Keep ADR-0010 Proposed; draft blocker findings only | Mark ADR Accepted — rejected: AGENTS.md STOP condition | Security sign-off remains an explicit launch blocker |

## 15. Outcomes & Retrospective
- **What landed:** Smoke `--prod` now rejects placeholder and missing/nonconforming liboqs bindings; ADR-0010 draft records blockers but remains Proposed.
- **What changed vs plan:** M1 stopped immediately because no valid liboqs Python binding is importable. M5/M6 were not completed; only a draft ADR and an honest smoke gate were produced. M7-M8 were not attempted.
- **Remaining risks:** liboqs system library + correct Python binding must be operator-installed. v1.0.0 cannot be tagged until all 16 production readiness gates pass. Real protocol implementations, external interop partner, human security lead sign-off, promtool, and production hardware remain launch blockers.
- **Production-readiness impact:** EP-010 is **stopped at M1**. AetherMesh / AEP is NOT production-ready per SPEC-008. The blueprint/dev-phase infrastructure remains verified, but production launch requires operator-installed liboqs, real layer implementations replacing stubs, external implementation for interop, security lead sign-off, and production hardware for performance baselines.
