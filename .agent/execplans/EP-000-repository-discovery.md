# EP-000 — Repository Discovery

- **Status:** Draft  - **Owner:** Architecture  - **Phase:** 0  - **Specs:** SPEC-000

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
M1 -> M6 in order.

## 10. Validation and Acceptance
### Acceptance Criteria
- [ ] All 5 bundle demos exit 0.
- [ ] `ASSUMPTIONS.md` A1, A2, A7, A12 have verification notes.
- [ ] `ARCHITECTURE.md` Repository Map reflects actual state.
- [ ] `COMMANDS.md` updated if needed.
- [ ] First failing gate of `./scripts/verify.sh` recorded in Surprises (EP-001 will fix).

## 11. Idempotence and Recovery
Every step is read-only or appends notes. Re-running re-confirms; previous notes not deleted.

## 12. Progress
- [ ] M1 — Inventory
- [ ] M2 — Bundles run
- [ ] M3 — Package manager + Python
- [ ] M4 — CI configuration
- [ ] M5 — Drift mapping
- [ ] M6 — Missing commands
- [ ] Final review

## 13. Surprises & Discoveries
<filled as work proceeds>

## 14. Decision Log
<entries>

## 15. Outcomes & Retrospective
<Filled at completion.>
- **What landed:**
- **What changed vs plan:**
- **Remaining risks:**
- **Production-readiness impact:** Phase 0 exits; EP-001 unblocked.
