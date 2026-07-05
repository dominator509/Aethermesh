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
- `pyproject.toml` (pin `liboqs-python`, allow direct references, add benchmark dev dep)
- `uv.lock`
- `ENVIRONMENT.md`
- `tests/conftest.py`
- `tests/unit/common/test_pq_backend.py`
- `tests/interop/results/INTEROP_REPORT.md`
- `tests/perf/__init__.py`
- `tests/perf/conftest.py`
- `tests/perf/helpers.py`
- `tests/perf/test_l1_fast_lane.py`
- `tests/perf/test_l3_handshake.py`
- `tests/perf/test_l4_non_dh_step.py`
- `tests/perf/test_l5_captoken_verify.py`
- `tests/perf/results/README.md`
- `tests/perf/results/baseline.json`
- `scripts/production-readiness-check.sh`
- `.agent/decisions/ADR-0010-security-signoff.md`
- `.agent/specs/SPEC-008-production-readiness.md`
- `DECISIONS.md` (ADR-0010 -> Accepted)
- `README.md`
- `REPO_BRIEF.md`
- `RELEASE_NOTES.md` (1.0.0 entry)
- `CHANGELOG.md` (1.0.0 entry)

## 7. Interfaces and Contracts
Per SPEC-008 § Gates.

## 8. Milestones

### M1 — Install liboqs
- **Goal:** `oqs` package available.
- **Files to Read:** `ENVIRONMENT.md`.
- **Files to Change:** `pyproject.toml`, `uv.lock`, `ENVIRONMENT.md`.
- **Exact Edits Expected:** Pin `liboqs-python` from the upstream Git tag, allow direct references in Hatch metadata, and confirm that `liboqs` is reachable via system install or upstream auto-build.
- **Validation Command:** `uv pip show liboqs-python && AEP_PQ_BACKEND=liboqs uv run python -m aethermesh.tools.smoke --prod`
- **Expected Result:** `liboqs-python` shown as installed; `smoke test: ok`.
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
- **Files to Change:** `tests/conftest.py`, `tests/interop/results/INTEROP_REPORT.md`.
- **Exact Edits Expected:** Record matrix: per layer x per scenario pass/fail against pinned reference impl in `tests/interop/external/`.
- **Validation Command:** `AEP_PQ_BACKEND=liboqs uv run pytest tests/interop --slow -q`
- **Expected Result:** exit 0; INTEROP_REPORT.md updated.
- **Recovery:** Per AGENTS § 7. Interop failures are protocol bugs; do not patch tests to make them pass.

### M4 — Performance baseline
- **Goal:** Budgets met on reference VM; results recorded.
- **Files to Read:** PROJECT_BRIEF.md budgets.
- **Files to Change:** `tests/perf/__init__.py`, `tests/perf/conftest.py`, `tests/perf/helpers.py`, `tests/perf/test_l1_fast_lane.py`, `tests/perf/test_l3_handshake.py`, `tests/perf/test_l4_non_dh_step.py`, `tests/perf/test_l5_captoken_verify.py`, `tests/perf/results/README.md`, `tests/perf/results/baseline.json`, `scripts/production-readiness-check.sh`, `COMMANDS.md`, `.agent/specs/SPEC-008-production-readiness.md`.
- **Exact Edits Expected:** Add repo-local benchmark modules for the current L1/L3/L4/L5 callable surfaces, wire the canonical JSON output path, and record p95 + p99 per category.
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
- **Files to Change:** `scripts/production-readiness-check.sh`.
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
- [x] `AEP_PQ_BACKEND=liboqs ./scripts/verify.sh` exits 0.
- [ ] Interop matrix passes. **BLOCKED — `uv run pytest tests/interop --slow -q` now passes, but only the scaffold vector test runs and `tests/interop/external/` is absent.**
- [ ] Performance budgets met. **LOCAL PASS — `uv run pytest tests/perf --benchmark-only --benchmark-json=tests/perf/results/baseline.json` exits 0 and records results, but production perf sign-off remains blocked because L1/L3/L4 still exercise placeholder or stub-level surfaces and no reference VM evidence is recorded.**
- [ ] ADR-0010 = Accepted in DECISIONS.md. **BLOCKED — requires human security lead sign-off (AGENTS.md STOP condition).**
- [ ] `./scripts/production-readiness-check.sh` exits 0. **BLOCKED — now reaches Gate 16 and stops because ADR-0010 is not marked `Accepted` in `DECISIONS.md`.**
- [ ] v1.0.0 tag pushed. **BLOCKED — all preceding gates must pass.**

## 11. Idempotence and Recovery
Tags are not idempotent — once pushed, v1.0.0 cannot be un-tagged without harm. The RC step is the rehearsal.

## 12. Progress
- [x] M1 — Install liboqs (`liboqs-python` pinned from upstream Git tag `0.12.0`; local `AEP_PQ_BACKEND=liboqs` smoke passes)
- [x] M2 — Full suite with liboqs (`AEP_PQ_BACKEND=liboqs ./scripts/verify.sh` returns `verify: ok`)
- [ ] M3 — Interop matrix (**BLOCKED: exact command passes, but only `tests/interop/test_vectors_scaffold.py` runs; `tests/interop/external/` is missing**)
- [ ] M4 — Performance baseline (**LOCAL PASS: repo-local perf suite exists, writes `tests/perf/results/baseline.json`, and current-machine budgets pass; production sign-off still needs reference VM evidence and real layer implementations**)
- [ ] M5 — Security review + ADR-0010 (draft ADR document written at `.agent/decisions/ADR-0010-security-signoff.md`; status remains **Proposed** and not accepted)
- [ ] M6 — production-readiness-check.sh (**BLOCKED: Gate 16 fails because ADR-0010 is still `Proposed`**)
- [ ] M7 — v1.0.0-rc.1 (**BLOCKED: requires M6 all-gates-pass**)
- [ ] M8 — v1.0.0 final (**BLOCKED: requires M7 + 72h burn-in**)
- [x] Final review

## 13. Surprises & Discoveries
1. **`oqs` does not expose `__version__`**: the literal M1 validation command from the original plan is stale for the actual binding API. Validation was recorded via `uv pip show liboqs-python`, successful `smoke --prod`, and successful `AEP_PQ_BACKEND=liboqs ./scripts/verify.sh`.
2. **The runtime PQ binding is not available from PyPI**: `liboqs-python==0.12.0` had to be pinned from the upstream Git tag, and Hatch needed `allow-direct-references = true` for editable builds.
3. **The repo documented `pytest --slow` without implementing it**: `tests/conftest.py` registered the `slow` marker but not the `--slow` option, so the interop command failed until the repo-local pytest hook was added.
4. **The repo documented `--benchmark-only` without the plugin**: `pytest-benchmark` was missing from dev dependencies; after adding it, the real blocker became visible.
5. **Performance infrastructure now exists, but it is still scaffold-scoped**: `tests/perf/` now records `tests/perf/results/baseline.json`, but L1/L3/L4 still benchmark placeholder or stub-level surfaces and the reference benchmark VM has not been recorded.
6. **Interop is scaffold-only**: the exact command now exits 0, but only `tests/interop/test_vectors_scaffold.py` runs and `tests/interop/external/` is absent.
7. **ADR-0010 draft is not sign-off**: `.agent/decisions/ADR-0010-security-signoff.md` remains a draft blocker record; `DECISIONS.md` is still Proposed and no human security lead sign-off is recorded.
8. **Gate 12 was a harness defect, not a product defect**: the readiness script needed a disposable audit DB fixture path; after adding one, the script advances to the later gates.
9. **Gate 14 was an operator-tooling dependency, not a rule defect**: once `promtool` was installed, `promtool check rules ops/alerts/aethermesh.rules.yml` passed with `SUCCESS: 6 rules found`.

## 14. Decision Log
| # | Context | Decision | Alternatives | Consequences |
|---|---|---|---|---|
| D1 | Initial EP-010 state had no working liboqs Python binding | Record the blocker first, then resolve it by pinning `liboqs-python` to the upstream Git tag and syncing a real local install | Treat `AEP_PQ_BACKEND=liboqs` as sufficient — rejected: it would false-green Gate 3 | Placeholder PQ backend remained dev-only until the real binding path was wired in; M1 now passes locally |
| D2 | Smoke `--prod` previously checked only the environment value | Require the actual liboqs Python API in `--prod` smoke mode | Accept any non-placeholder value — rejected: false production-readiness signal | Gate 3 only passes when the real liboqs API is available |
| D3 | ADR-0010 requires human security review | Keep ADR-0010 Proposed; draft blocker findings only | Mark ADR Accepted — rejected: AGENTS.md STOP condition | Security sign-off remains an explicit launch blocker |
| D4 | `liboqs-python` 0.12.0 is not available from the package index used by `uv add` | Pin the runtime dependency to the upstream Git tag and allow direct references in Hatch metadata | Keep an untracked manual `uv pip install` only — rejected: not reproducible | `uv sync` now recreates the liboqs binding, but requires GitHub access during dependency resolution |
| D5 | `uv run pytest tests/interop --slow -q` was a documented command but the repo did not implement `--slow` | Add a repo-local pytest option in `tests/conftest.py` that enables tests marked `slow` | Change docs/commands to `-m slow` only — rejected: more drift across repo docs | Interop command surface now matches `COMMANDS.md`, `TESTING.md`, and `PRODUCTION_READINESS.md` |
| D6 | `uv run pytest tests/perf --benchmark-only` was a documented command but `pytest-benchmark` was missing | Add `pytest-benchmark` as a dev dependency | Leave the command broken — rejected: hides the real EP-010 blocker | Performance validation now fails for the real reason: there is no `tests/perf/` suite or baseline path |
| D7 | EP-010 still lacked any benchmark suite after the harness dependency landed | Add small repo-local perf benchmarks for the callable L1/L3/L4/L5 surfaces that actually exist in this checkout and record `tests/perf/results/baseline.json` | Create empty perf artifacts to appease the command — rejected: false production signal | Gate 5 now exercises real repo-local callable surfaces, but production perf claims still need reference hardware and non-stub layer bodies |
| D8 | Gate 5 used `--benchmark-compare-fail` without any valid compare source while the active ExecPlan required a JSON baseline artifact | Align Gate 5 with the ExecPlan by wiring `--benchmark-json=tests/perf/results/baseline.json` and relying on benchmark assertions for local budget enforcement | Keep the invalid compare flag — rejected: it aborts before any benchmark evidence is written | The readiness harness now records durable local perf evidence; release-to-release regression strategy still needs a real reference baseline source |
| D9 | The next production-readiness blocker surfaced immediately after Gate 5 was fixed | Patch Gate 12 to run `audit_db migrate --check` against a disposable repo-local schema-v0 fixture and rerun the full script | Keep the miswired command and stop at Gate 12 — rejected: stale blocker record and no proof of repair | Gate 12 now passes; the next real blocker is missing `promtool` at Gate 14 |
| D10 | Gate 14 failed on missing operator tooling, but the alert rules themselves had not been validated yet | Install Prometheus `promtool` via Chocolatey, run `promtool check rules ops/alerts/aethermesh.rules.yml`, and rerun the full readiness script | Change Gate 14 to a weaker parser-only check — rejected: SPEC-008 requires `promtool check rules` | Gate 14 now passes locally; the next real blocker is ADR-0010 remaining `Proposed` at Gate 16 |

## 15. Outcomes & Retrospective
- **What landed:** `liboqs-python` is now pinned and reproducible via `uv sync`; `AEP_PQ_BACKEND=liboqs ./scripts/verify.sh` returns `verify: ok`; the repo-local `--slow` interop flag and `pytest-benchmark` harness now match the documented commands; `tests/perf/` now exists, writes `tests/perf/results/baseline.json`, and Gate 5 in `./scripts/production-readiness-check.sh` now records the JSON artifact instead of aborting on an invalid compare flag.
- **What changed vs plan:** M1 and M2 completed locally. M3 only reached the scaffold vector test because no second implementation exists in-repo. M4 now has a local benchmark suite and baseline artifact, but it still lacks reference-VM evidence and non-stub layer bodies for production sign-off. M5 remains blocked by required human sign-off. M6 now passes Gates 12 and 14 and reaches Gate 16, where it stops because ADR-0010 is still `Proposed`. M7-M8 were not attempted.
- **Remaining risks:** real L1/L2/L3/L4/L5 protocol implementations, external interop partner coverage, reference benchmark hardware, human security lead sign-off, and the 72h burn-in window remain launch blockers.
- **Production-readiness impact:** EP-010 is **still partial**. AetherMesh / AEP is still NOT production-ready per SPEC-008. The liboqs-backed local baseline, repo-local perf harness, and Gates 12 and 14 are now green, but production launch remains blocked by scaffold-only interop, scaffold-scoped perf evidence, and human security approval.
