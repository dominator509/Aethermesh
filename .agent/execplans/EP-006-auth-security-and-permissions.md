# EP-006 — Auth, Security, and Permissions

- **Status:** Draft  - **Owner:** Security  - **Phase:** 5  - **Specs:** SPEC-005

## 1. Purpose / Big Picture
Promote L3 attestation beyond SoftSign to TPM2 + Apple SEP, finalize L5 caveat DSL, ship minimal keyring service stub.

## 2. Scope
- `aethermesh/L3_handshake/attestation/backends/{tpm2,apple_sep}.py`
- `aethermesh/L5_captokens/caveats.py` (missing caveats only)
- `aethermesh/tools/keyring_serve.py`
- Per-backend tests + verifier branch coverage tests.

## 3. Non-Goals
- No SEV-SNP, TDX, StrongBox. No real TEE provisioning. No web-based keyring.

## 4. Context and Orientation
Bundles ship SoftSign. EP-006 adds two real backends gated by host capability (skipped if absent).

## 5. Files to Read First
1. `SPEC-005-auth-and-permissions.md`  2. `bundles/aethermesh_L3/code/attestation.py`  3. `bundles/aethermesh_L5/code/{caveat_types,caveats,verifier}.py`  4. `SECURITY.md` Cryptographic Rules

## 6. Files to Change
- `aethermesh/L3_handshake/attestation/backends/{__init__,tpm2,apple_sep}.py`
- `aethermesh/L5_captokens/caveats.py` (additions only)
- `aethermesh/tools/keyring_serve.py`
- `tests/unit/L3/attestation/test_{tpm2,apple_sep}.py`
- `tests/unit/L5/verifier/test_branch_coverage.py`
- `tests/integration/keyring/test_unix_socket.py`

## 7. Interfaces and Contracts
Per SPEC-005 § Attestation Backends + Caveat DSL + Keyring IPC.

## 8. Milestones

### M1 — TPM2 backend skeleton
- **Goal:** `build_quote` + `verify_quote` with SPEC-005 shape.
- **Files to Read:** SPEC-005, bundle `attestation.py`.
- **Files to Change:** `backends/tpm2.py`, `tests/unit/L3/attestation/test_tpm2.py`.
- **Exact Edits Expected:** `build_quote(...)` calls `tpm2-tools` via subprocess if present, else clearly-labeled placeholder. Test skips if `command -v tpm2_pcrread` missing.
- **Validation Command:** `uv run pytest tests/unit/L3/attestation/test_tpm2.py -q`
- **Expected Result:** exit 0 (may skip on hosts without TPM2 tools).
- **Recovery:** Per AGENTS § 7.

### M2 — Apple SEP backend
- **Goal:** Same shape, App Attest + DeviceCheck (mocked outside macOS).
- **Files to Change:** `backends/apple_sep.py`, `tests/unit/L3/attestation/test_apple_sep.py`.
- **Exact Edits Expected:** Same interface; `@pytest.mark.skipif(sys.platform != "darwin", ...)`.
- **Validation Command:** `uv run pytest tests/unit/L3/attestation/test_apple_sep.py -q`
- **Expected Result:** exit 0 (skips on non-macOS).
- **Recovery:** Per AGENTS § 7.

### M3 — Caveat DSL gap analysis
- **Goal:** Every SPEC-005 caveat type implemented.
- **Files to Read:** SPEC-005 § Caveat DSL, bundle `caveats.py`, `verifier.py`.
- **Files to Change:** `caveats.py` (only if gaps); `verifier.py` (only if gaps).
- **Exact Edits Expected:** Add missing caveat constructors and `_eval_caveat` branches. Record gap list in Surprises.
- **Validation Command:** `uv run pytest tests/unit/L5/verifier/ -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

### M4 — Verifier branch coverage
- **Goal:** >=70% branch coverage on `verifier.py`.
- **Files to Change:** `tests/unit/L5/verifier/test_branch_coverage.py`.
- **Exact Edits Expected:** Tests for every fail-closed branch (each DENY_*, PENDING_DISCHARGE, unknown caveat).
- **Validation Command:** `uv run pytest tests/unit/L5/verifier/ --cov=aethermesh.L5_captokens.verifier --cov-branch --cov-fail-under-branch=70 -q`
- **Expected Result:** exit 0; branch coverage >=70%.
- **Recovery:** Per AGENTS § 7.

### M5 — Keyring service stub
- **Goal:** Unix socket per SPEC-005.
- **Files to Read:** SPEC-005 § Keyring IPC.
- **Files to Change:** `aethermesh/tools/keyring_serve.py`, `tests/integration/keyring/test_unix_socket.py`.
- **Exact Edits Expected:** Binds to `$AEP_KEYRING_SOCKET`, reads length-prefixed CBOR `discharge_request`/`mint_request`, responds with signed `Discharge`/`CapToken`. Tests use temp socket path.
- **Validation Command:** `uv run pytest tests/integration/keyring/ -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

## 9. Concrete Steps
M1 -> M5.

## 10. Validation and Acceptance
### Acceptance Criteria
- [ ] TPM2 + Apple SEP backends exist (skip-safe outside hosts).
- [ ] Every SPEC-005 caveat type implemented and tested.
- [ ] Verifier branch coverage >=70%.
- [ ] Keyring IPC roundtrip passes.
- [ ] `./scripts/verify.sh` exits 0.

## 11. Idempotence and Recovery
Each backend module + caveat independent.

## 12. Progress
- [ ] M1 — TPM2 backend
- [ ] M2 — Apple SEP backend
- [ ] M3 — Caveat DSL gap
- [ ] M4 — Branch coverage
- [ ] M5 — Keyring stub
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
- **Production-readiness impact:** Phase 5 exits.
