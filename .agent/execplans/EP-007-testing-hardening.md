# EP-007 — Testing Hardening

- **Status:** Draft  - **Owner:** QA  - **Phase:** 6  - **Specs:** SPEC-006, TESTING.md

## 1. Purpose / Big Picture
Reach coverage thresholds (>=85% line per layer, >=70% branch on L5 verifier DSL). Fuzz Sphinx packet parser + caveat DSL with `hypothesis`. Define flaky-test policy + quarantine harness. Assemble interop test scaffolding.

## 2. Scope
- Backfill unit tests.
- Hypothesis fuzz targets.
- Flaky test policy file.
- Interop scaffolding.

## 3. Non-Goals
- No new features. No new protocol layers. No performance benchmarks (EP-010).

## 4. Context and Orientation
EP-002..EP-006 added code with passing tests but uneven coverage. This plan closes gaps and adds fuzz + interop scaffolding.

## 5. Files to Read First
1. `TESTING.md`  2. `bundles/aethermesh_L1/code/sphinx_packet.py`  3. `bundles/aethermesh_L5/code/{caveats,verifier}.py`  4. existing `tests/` tree

## 6. Files to Change
- `tests/property/test_sphinx_fuzz.py`
- `tests/property/test_caveat_fuzz.py`
- `tests/interop/conftest.py`
- `.github/FLAKY_POLICY.md`
- backfill tests in `tests/unit/L{1..5}/` as needed.

## 7. Interfaces and Contracts
None new. Pure test additions.

## 8. Milestones

### M1 — Coverage audit per layer
- **Goal:** Identify gaps.
- **Files to Read:** existing coverage report.
- **Files to Change:** none.
- **Exact Edits Expected:** none; record gaps in Surprises.
- **Validation Command:** `uv run pytest tests/unit --cov=aethermesh --cov-report=term-missing -q`
- **Expected Result:** report shows per-layer percentages.
- **Recovery:** Per AGENTS § 7.

### M2 — Backfill unit tests to >=85% line
- **Goal:** Each layer reaches threshold.
- **Files to Change:** new test files under `tests/unit/L{N}/test_*.py`.
- **Exact Edits Expected:** Tests targeting uncovered branches.
- **Validation Command:** `uv run pytest tests/unit --cov=aethermesh --cov-report=term --cov-fail-under=85 -q`
- **Expected Result:** exit 0; `TOTAL >=85%`.
- **Recovery:** Per AGENTS § 7.

### M3 — Sphinx fuzz target
- **Goal:** `hypothesis` generates random byte strings; `SphinxPacket.from_wire` either accepts or raises typed error — never crashes.
- **Files to Read:** `bundles/aethermesh_L1/code/sphinx_packet.py`.
- **Files to Change:** `tests/property/test_sphinx_fuzz.py`.
- **Exact Edits Expected:** Strategy generating `binary(min_size=0, max_size=2100)`. Assert: either decodes or raises `(ValueError, OverflowError)`.
- **Validation Command:** `uv run pytest tests/property/test_sphinx_fuzz.py -q`
- **Expected Result:** exit 0; >=200 examples.
- **Recovery:** Per AGENTS § 7.

### M4 — Caveat DSL fuzz target
- **Goal:** Random CBOR-like caveat dicts; `Caveat.from_dict` either parses or returns `DENY_UNKNOWN_CAVEAT` (no crash).
- **Files to Read:** `bundles/aethermesh_L5/code/caveats.py`.
- **Files to Change:** `tests/property/test_caveat_fuzz.py`.
- **Exact Edits Expected:** Strategy generating dicts with random `type` ints; assert no uncaught exception escapes the verifier.
- **Validation Command:** `uv run pytest tests/property/test_caveat_fuzz.py -q`
- **Expected Result:** exit 0; >=200 examples.
- **Recovery:** Per AGENTS § 7.

### M5 — Flaky test policy file
- **Goal:** Quarantine harness with auto-issue.
- **Files to Change:** `.github/FLAKY_POLICY.md`, `tests/conftest.py`.
- **Exact Edits Expected:** Policy file from `TESTING.md` § Flaky Test Policy. Conftest adds marker `quarantined`. 14-day timeout convention documented.
- **Validation Command:** `uv run pytest -m "not quarantined" -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

### M6 — Interop scaffolding
- **Goal:** `tests/interop/conftest.py` loads pinned vectors.
- **Files to Read:** `tests/vectors/`.
- **Files to Change:** `tests/interop/{__init__,conftest}.py`, `tests/interop/results/INTEROP_REPORT.md`.
- **Exact Edits Expected:** Fixture loading vectors from `tests/vectors/`. INTEROP_REPORT.md template. `pytest.mark.slow` setup.
- **Validation Command:** `uv run pytest tests/interop --collect-only -q`
- **Expected Result:** collects tests; no errors.
- **Recovery:** Per AGENTS § 7.

## 9. Concrete Steps
M1 -> M6.

## 10. Validation and Acceptance
### Acceptance Criteria
- [ ] Each layer >=85% line coverage.
- [ ] Verifier branch coverage >=70% (from EP-006).
- [ ] Both fuzz targets run >=200 examples without uncaught exceptions.
- [ ] Flaky policy file exists.
- [ ] Interop scaffolding collects.
- [ ] `./scripts/verify.sh` exits 0.

## 11. Idempotence and Recovery
Tests are idempotent; hypothesis examples deterministic with seed.

## 12. Progress
- [ ] M1 — Coverage audit
- [ ] M2 — Backfill
- [ ] M3 — Sphinx fuzz
- [ ] M4 — Caveat fuzz
- [ ] M5 — Flaky policy
- [ ] M6 — Interop scaffolding
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
- **Production-readiness impact:** Phase 6 exits.
