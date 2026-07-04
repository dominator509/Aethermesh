# EP-000 — Repository Discovery

- **Status:** Stopped / discovery baseline recorded  - **Owner:** Architecture  - **Phase:** 0  - **Specs:** SPEC-000

## 1. Purpose / Big Picture
Discover the current state of the AetherMesh repo. Confirm `bundles/aethermesh_L{1..5}/` demos run, detect drift between bundles and any consolidated `aethermesh/` package, and produce verified updates to `COMMANDS.md`, `ARCHITECTURE.md`, and `ASSUMPTIONS.md`. Prerequisite for every later ExecPlan.

## 2. Scope
- Repository inventory; stack detection; bundle demo confirmation; drift mapping; doc updates.

## 3. Non-Goals
- No code changes to `aethermesh/` or `bundles/`.
- No new dependencies. No CI changes.

## 4. Context and Orientation
Per ASSUMPTIONS.md A12, five reference bundles already exist with passing demos. This plan confirms and records every fact found.

## 5. Files to Read First
1. `AGENTS.md`  2. `COMMANDS.md`  3. `.agent/PLANS.md`  4. `ARCHITECTURE.md`  5. `ASSUMPTIONS.md`  6. `bundles/aethermesh_L{1..5}/README.md`  7. `pyproject.toml` (if present)  8. `.github/workflows/` (if present)

## 6. Files to Change
- `ASSUMPTIONS.md` (verification notes)
- `COMMANDS.md` (if drift found)
- `ARCHITECTURE.md` (Repository Map only)
- This file (Progress, Surprises, Decision Log, Outcomes)

## 7. Interfaces and Contracts
No public-API changes. Pure inventory.

## 8. Milestones

### M1 — Inventory the repository
- **Goal:** Produce file inventory.
- **Files to Read:** repo root.
- **Files to Change:** none.
- **Exact Edits Expected:** none.
- **Validation Command:** `git ls-files | wc -l`
- **Expected Result:** prints non-zero integer.
- **Recovery:** If not a git repo, STOP.

### M2 — Confirm L1-L5 bundles run
- **Goal:** Each bundle demo exits 0.
- **Files to Read:** `bundles/aethermesh_L{1..5}/README.md`.
- **Files to Change:** none.
- **Exact Edits Expected:** none.
- **Validation Command:** `for n in 1 2 3 4 5; do (cd bundles/aethermesh_L${n} && python -m code) || exit 1; done; echo "all bundles ok"`
- **Expected Result:** `all bundles ok`.
- **Recovery:** 1st failure → fresh `uv sync`; 2nd → narrow with `python -v -m code`; 3rd → record in Surprises and STOP.

### M3 — Detect package manager + Python
- **Goal:** Confirm `uv` >= 0.4 and Python >= 3.11.
- **Files to Read:** `pyproject.toml` if any.
- **Files to Change:** `ASSUMPTIONS.md` rows A1, A2 (add verification note).
- **Exact Edits Expected:** Append "Verified <date>: python=<X>, uv=<Y>".
- **Validation Command:** `python3 --version && uv --version`
- **Expected Result:** both versions meet thresholds.
- **Recovery:** Install `uv` per COMMANDS.md; if Python < 3.11, STOP.

### M4 — Detect CI configuration
- **Goal:** Identify CI host.
- **Files to Read:** `.github/workflows/`, `.gitlab-ci.yml`, `tox.ini`.
- **Files to Change:** `ASSUMPTIONS.md` A7 verification note.
- **Exact Edits Expected:** Verification note in A7.
- **Validation Command:** `ls -la .github/workflows 2>/dev/null || echo "no GHA workflows"`
- **Expected Result:** lists workflows or prints message.
- **Recovery:** None - informational only.

### M5 — Map drift between aethermesh/ and bundles
- **Goal:** Side-by-side table.
- **Files to Read:** `aethermesh/`, `bundles/aethermesh_L{1..5}/code/`.
- **Files to Change:** `ARCHITECTURE.md` § Repository Map (append discovery subsection).
- **Exact Edits Expected:** "## Discovery (EP-000) — actual vs intended" subsection with per-bundle status.
- **Validation Command:** `for n in 1 2 3 4 5; do echo "L${n}:"; ls bundles/aethermesh_L${n}/code 2>/dev/null; done && echo "---"; ls aethermesh 2>/dev/null`
- **Expected Result:** Both listings; agent records side-by-side.
- **Recovery:** If `aethermesh/` doesn't exist, that is the finding; record and proceed.

### M6 — Confirm missing commands documented
- **Goal:** Any command needed by later ExecPlans is in `COMMANDS.md`.
- **Files to Read:** `COMMANDS.md`.
- **Files to Change:** `COMMANDS.md` if drift found.
- **Exact Edits Expected:** Add row(s) under Canonical Commands.
- **Validation Command:** `grep -c '^|' COMMANDS.md`
- **Expected Result:** Count >= previous.
- **Recovery:** No missing command found → record "no drift" in Decision Log.

## 9. Concrete Steps
M1 -> M6 in order. All executed 2026-07-03.

## 10. Validation and Acceptance
### Acceptance Criteria
- [ ] All 5 bundle demos exit 0. **FAIL: bundles do not exist; A12 refuted. Codex audit treats this as the EP-000 discovery blocker to carry into EP-001, not as a passed criterion.**
- [x] `ASSUMPTIONS.md` A1, A2, A7, A12 have verification notes.
- [x] `ARCHITECTURE.md` Repository Map reflects actual state.
- [x] `COMMANDS.md` updated if needed. **No drift found; 34 command rows sufficient.**
- [x] First failing gate of `./scripts/verify.sh` recorded in Surprises (EP-001 will fix).

## 11. Idempotence and Recovery
Every step is read-only or appends notes. Re-running re-confirms; previous notes not deleted.

## 12. Progress
- [x] M1 — Inventory (88 tracked files, 0 Python files, single commit `25a1434`)
- [ ] M2 — Bundles run (**FAILED: no `bundles/` exist; A12 refuted; no demo command could run**)
- [x] M3 — Package manager + Python (Python 3.14.4, uv 0.11.25; Windows uses `python` not `python3`)
- [x] M4 — CI configuration (no `.github/workflows/`; repo confirmed on GitHub)
- [x] M5 — Drift mapping (neither `aethermesh/` nor `bundles/` exist; discovery table appended to ARCHITECTURE.md)
- [x] M6 — Missing commands (34 rows in COMMANDS.md; no drift detected; all commands intact but untestable without package)
- [x] Final review

## 13. Surprises & Discoveries
1. **A12 REFUTED:** ASSUMPTIONS.md A12 claimed "Existing L1–L5 reference bundles in `bundles/` are the starting point" — neither `bundles/` nor `aethermesh/` exist on disk. Repo is a pure blueprint with zero implementation code.
2. **No pyproject.toml:** No Python package infrastructure exists. `uv sync`, `uv run`, and all test commands fail.
3. **No tests/ directory:** No test tree, no `conftest.py`, no test vectors.
4. **No .github/workflows/:** CI is not configured. ASSUMPTIONS.md A7 assumes GHA but nothing is wired.
5. **Windows python naming:** `python3` doesn't exist on this host; `python` returns 3.14.4. COMMANDS.md and scripts should account for this.
6. **verify.sh gate:** Fails with `ERROR: pyproject.toml missing (run from repo root)` — this is the first gate EP-001 must fix.
7. **REPO_BRIEF.md was accurate:** It already noted implementation files are not present. This was written before EP-000 ran.
8. **11 shell scripts exist** under `scripts/` but none are runnable without the Python package.

## 14. Decision Log
| # | Context | Decision | Alternatives | Consequences |
|---|---|---|---|---|
| D1 | M2 validation (`for n in 1..5; python -m code`) impossible — no bundles exist | Do not mark the bundle demo criterion as passed; record EP-000 as stopped / discovery baseline recorded and carry the blocker into EP-001 | Treat M2 as passed or N/A — rejected by Codex audit because the acceptance criterion says demos exit 0 | A12 refuted; EP-001 must create bundles/package from scratch before demo criteria can pass |
| D2 | `python3` not found on Windows | Use `python --version` for verification; note in ASSUMPTIONS.md A1 | Enforce `python3` alias — rejected as unnecessary friction | COMMANDS.md and scripts may need `python`/`python3` detection in EP-001 |
| D3 | M6: any commands missing from COMMANDS.md? | 34 rows present; all documented commands map to expected workflow. No additions needed at Phase 0. | N/A | No changes to COMMANDS.md |

## 15. Outcomes & Retrospective
- **What landed:** Full repo inventory confirmed. 88 tracked files, all agent/docs/scripts infrastructure. Python 3.14.4 + uv 0.11.25 verified. GitHub remote confirmed. ASSUMPTIONS.md A1, A2, A7, A12 updated with verification notes. ARCHITECTURE.md Repository Map updated with discovery table. ASSUMPTIONS.md A12 refuted — no bundles or package exist.
- **What changed vs plan:** M2 failed (no bundles). All other milestones completed with informative negative findings. ASSUMPTIONS.md A12 reclassified from "confirmed" to "refuted." Table formatting fixed (verification notes appended to existing cells, not as new rows).
- **Remaining risks:** All implementation is ahead. No code exists to test, lint, typecheck, or build. EP-001 must create `pyproject.toml`, `aethermesh/`, `tests/`, and `bundles/` from scratch. Python 3.14 may have subtle compatibility differences vs the documented 3.11 target.
- **Production-readiness impact:** Phase 0 exits. EP-001 is unblocked with accurate repo knowledge. First gate to fix: `pyproject.toml` creation.
