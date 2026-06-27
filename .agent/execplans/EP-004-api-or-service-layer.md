# EP-004 — API / Service Layer

- **Status:** Draft  - **Owner:** Architecture  - **Phase:** 3  - **Specs:** SPEC-003, SPEC-006

## 1. Purpose / Big Picture
Promote L3/L4/L5 public APIs into a stable `aethermesh.api` facade. Add contract tests pinning every public symbol so accidental breakage fails CI.

## 2. Scope
- `aethermesh/api/__init__.py`
- `tests/contracts/test_api_surface.py`
- `tests/integration/test_l3_l4_l5_roundtrip.py`
- SPEC-003 updates if drift discovered.

## 3. Non-Goals
- No new public APIs. No HTTP/gRPC services. No CLI (EP-005).

## 4. Context and Orientation
Layers live in `bundles/aethermesh_L{1..5}/code/`. Facade imports from there; full layer move is a later ExecPlan.

## 5. Files to Read First
1. `AGENTS.md`  2. `SPEC-003-api-contracts.md`  3. `ARCHITECTURE.md` Layer Responsibilities  4. `bundles/aethermesh_L3/code/handshake.py`  5. `bundles/aethermesh_L4/code/{pair_ratchet,policy_layer}.py`  6. `bundles/aethermesh_L5/code/{captoken,verifier,keyring}.py`

## 6. Files to Change
- `aethermesh/api/__init__.py`
- `tests/contracts/__init__.py`, `tests/contracts/test_api_surface.py`
- `tests/integration/test_l3_l4_l5_roundtrip.py`
- `SPEC-003-api-contracts.md` only if drift requires.

## 7. Interfaces and Contracts
Per SPEC-003 § Required Behavior — every name listed importable from `aethermesh.api`.

## 8. Milestones

### M1 — Audit bundle public APIs
- **Goal:** Confirm signatures match SPEC-003.
- **Files to Read:** all SPEC-003 modules.
- **Files to Change:** `tests/contracts/test_api_surface.py` (scaffolding).
- **Exact Edits Expected:** File with `def test_audit_complete(): ...`.
- **Validation Command:** `uv run pytest tests/contracts/test_api_surface.py -q`
- **Expected Result:** exit 0; 1 test passes.
- **Recovery:** Per AGENTS § 7.

### M2 — Write the facade
- **Goal:** All SPEC-003 imports succeed.
- **Files to Read:** SPEC-003.
- **Files to Change:** `aethermesh/api/__init__.py`.
- **Exact Edits Expected:** Import + re-export. If a target path doesn't exist, record in Decision Log; don't invent.
- **Validation Command:** `uv run python -c "from aethermesh.api import HandshakeInitiator, HandshakeResponder, SessionState, PairRatchet, PolicyLayer, IntentHeader, MlsGroup, CapToken, Caveat, CapTokenVerifier, Discharge, KeyringService, AuditLog; print('api ok')"`
- **Expected Result:** prints `api ok`.
- **Recovery:** 1st check path; 2nd `-v`; 3rd STOP.

### M3 — Contract tests
- **Goal:** Assert every public signature.
- **Files to Change:** `tests/contracts/test_api_surface.py`.
- **Exact Edits Expected:** `inspect.signature` to assert parameter list per SPEC-003. One test per symbol.
- **Validation Command:** `uv run pytest tests/contracts/test_api_surface.py -q`
- **Expected Result:** exit 0; >=13 tests pass.
- **Recovery:** Per AGENTS § 7.

### M4 — SPEC reconciliation
- **Goal:** Update SPEC-003 with ADR if reality differs.
- **Files to Change:** `SPEC-003-api-contracts.md`, `DECISIONS.md`.
- **Exact Edits Expected:** Match actual signatures only where tests failed. New ADR if architectural.
- **Validation Command:** `uv run pytest tests/contracts/ -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

### M5 — L3->L4->L5 integration roundtrip
- **Goal:** Mint CapToken, run L3 handshake, send L4 message, L5 verifier ALLOWs.
- **Files to Read:** all SPEC-003 modules.
- **Files to Change:** `tests/integration/test_l3_l4_l5_roundtrip.py`.
- **Exact Edits Expected:** Full flow with deterministic test material. Asserts `policy.validate` returns `ALLOW` and `policy.release(ns)` succeeds.
- **Validation Command:** `uv run pytest tests/integration/test_l3_l4_l5_roundtrip.py -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

## 9. Concrete Steps
M1 -> M5.

## 10. Validation and Acceptance
### Acceptance Criteria
- [ ] `from aethermesh.api import *` succeeds for all SPEC-003 symbols.
- [ ] Removing any public symbol fails contract tests.
- [ ] Integration roundtrip passes.
- [ ] `./scripts/verify.sh` exits 0.

## 11. Idempotence and Recovery
Facade is single module; re-importing idempotent.

## 12. Progress
- [ ] M1 — Audit
- [ ] M2 — Facade
- [ ] M3 — Contract tests
- [ ] M4 — SPEC reconciliation
- [ ] M5 — Integration roundtrip
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
- **Production-readiness impact:** Phase 3 exits.
