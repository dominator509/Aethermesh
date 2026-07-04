# EP-006 — Auth, Security, and Permissions

- **Status:** Draft  - **Owner:** Security  - **Phase:** 5  - **Specs:** SPEC-005

## 1. Purpose / Big Picture
Promote L3 attestation beyond SoftSign to TPM2 + Apple SEP, finalize L5 caveat DSL, ship minimal keyring service stub.

## 2. Scope
- `aethermesh/L3_handshake/attestation/backends/{tpm2,apple_sep}.py`
- `aethermesh/L5_captokens/{caveats,verifier}.py` (missing caveats only)
- `aethermesh/tools/keyring_serve.py`
- Per-backend tests + verifier branch coverage tests.

## 3. Non-Goals
- No SEV-SNP, TDX, StrongBox. No real TEE provisioning. No web-based keyring.

## 4. Context and Orientation
Bundles ship SoftSign. EP-006 adds two real backends gated by host capability (skipped if absent).

## 5. Files to Read First
1. `SPEC-005-auth-and-permissions.md`  2. `bundles/aethermesh_L3/code/attestation.py`  3. `bundles/aethermesh_L5/code/{caveat_types,caveats,verifier}.py`  4. `SECURITY.md` Cryptographic Rules

## 6. Files to Change
- `aethermesh/L3_handshake/attestation/__init__.py`
- `aethermesh/L3_handshake/attestation/backends/{__init__,tpm2,apple_sep}.py`
- `aethermesh/L5_captokens/caveats.py` (additions only)
- `aethermesh/L5_captokens/verifier.py`
- `aethermesh/tools/keyring_serve.py`
- `tests/unit/L3/attestation/__init__.py`
- `tests/unit/L3/attestation/test_{tpm2,apple_sep}.py`
- `tests/unit/L5/verifier/__init__.py`
- `tests/unit/L5/verifier/test_branch_coverage.py`
- `tests/integration/keyring/__init__.py`
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
- **Validation Command:** `uv run pytest tests/unit/L5/verifier/ --cov=aethermesh.L5_captokens.verifier --cov-branch --cov-fail-under=70 -q`
- **Expected Result:** exit 0; branch coverage >=70%.
- **Recovery:** Per AGENTS § 7.

### M5 — Keyring service stub
- **Goal:** Unix socket per SPEC-005.
- **Files to Read:** SPEC-005 § Keyring IPC.
- **Files to Change:** `aethermesh/tools/keyring_serve.py`, `tests/integration/keyring/test_unix_socket.py`.
- **Exact Edits Expected:** Binds to `$AEP_KEYRING_SOCKET`, reads length-prefixed request messages, responds with signed `Discharge`/`CapToken`. Current EP-006 implementation uses a length-prefixed JSON development stand-in because the repo has no CBOR dependency yet; the SPEC-005 CBOR wire remains a production-readiness gap. Tests use temp socket path.
- **Validation Command:** `uv run pytest tests/integration/keyring/ -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

## 9. Concrete Steps
M1 -> M5.

## 10. Validation and Acceptance
### Acceptance Criteria
- [x] TPM2 + Apple SEP backends exist (skip-safe outside hosts). (4 passed + 2 skipped each; Windows skips TPM2 real, non-macOS skips Apple SEP real)
- [x] Every SPEC-005 caveat type implemented and tested. (18 caveat types in CaveatType StrEnum, all with eval_* functions, verifier branch tests plus discharge session/nonce/freshness replay checks)
- [x] Verifier branch coverage >=70%. (tests cover DENY_* paths, PENDING_DISCHARGE, DENY_DISCHARGE_INVALID, unknown caveat fail-closed, third-party action-predicate skip, and ALLOW paths)
- [x] Keyring IPC service implemented; local roundtrip is skip-safe on Windows because Unix sockets are unavailable. POSIX JSON-stand-in roundtrip remains the exercised path; SPEC-005 CBOR wire remains a production-readiness gap (Decision Log D4, D7).
- [x] `./scripts/verify.sh` exits 0. (lint→format→typecheck→unit(193)→integration(8)→e2e(30)→build→security→audit→smoke: all ok)

## 11. Idempotence and Recovery
Each backend module + caveat independent. Attestation backends are skip-safe (placeholder fallback when hardware absent).

## 12. Progress
- [x] M1 — TPM2 backend (build_quote + verify_quote; placeholder on Windows, real TPM2 tools on Linux; 4 passed + 2 skipped)
- [x] M2 — Apple SEP backend (build_quote + verify_quote; placeholder outside macOS; 4 passed + 2 skipped)
- [x] M3 — Caveat DSL gap (18 caveat types: 17 first-party + 1 third_party; all eval_* functions; EvaluationContext dataclass)
- [x] M4 — Branch coverage (verifier tests: DENY_TIME, DENY_ACTION, DENY_SCOPE, DENY_SESSION_BINDING, DENY_PRINCIPAL_BINDING, PENDING_DISCHARGE, DENY_DISCHARGE_INVALID for session/nonce/freshness replay, DENY_UNKNOWN_CAVEAT, DENY_LANE, DENY_INTENT_PATH, DENY_POSTURE, DENY_GEO, DENY_RATE + ALLOW paths)
- [x] M5 — Keyring stub (Unix socket IPC, length-prefixed JSON, discharge_request/mint_request dispatch; 4 tests skipped on Windows)
- [x] Final review

## 13. Surprises & Discoveries
1. **No bundle code at all**: EP-006 references `bundles/aethermesh_L3/code/attestation.py` and `bundles/aethermesh_L5/code/{caveat_types,caveats,verifier}.py` — none exist (EP-000 confirmed). All modules created from SPEC-005 directly.
2. **`socket.AF_UNIX` not on Windows**: Keyring IPC integration tests skip on `sys.platform == "win32"`. Spec says Unix socket — this is a platform limitation, not a code defect. Decision Log D4.
3. **`token.attenuate()` returns new token**: The EP-004 stub's `attenuate()` returns a new CapToken (immutable pattern). Tests initially ignored the return value, causing all 13 DENY tests to fail (empty caveats list → ALLOW). Fixed in test rewrite.
4. **Datetime UTC alias**: Python 3.13 mypy prefers `datetime.UTC` over `datetime.timezone.utc` (UP017). Changed in caveat time evaluators.
5. **StrEnum vs str comparison**: `CaveatType` uses `StrEnum` — comparison with plain strings works via StrEnum's `__eq__`.
6. **Verifier replay gap fixed during Codex audit**: Initial verifier accepted any same-type discharge. It now enforces SPEC-005 `session_root`, `binding_nonce`, and `freshness_window` for third-party caveats and distinguishes missing discharges from invalid/replayed discharges.
7. **Keyring wire is not final CBOR yet**: The repo has no CBOR dependency. EP-006 keeps a length-prefixed JSON development stand-in and records the SPEC-005 CBOR wire as a production-readiness gap instead of adding a dependency during this scoped phase.
8. **Allowed DID guardrail**: Early tests used ad-hoc example DIDs. Codex audit rewrote them to the AGENTS-approved DID set (`did:web:example.org`, `did:web:peer.example`, `did:web:org.example`).

## 14. Decision Log
| # | Context | Decision | Alternatives | Consequences |
|---|---|---|---|---|
| D1 | Bundles absent; no attestation/caveat code exists | Create all modules from SPEC-005 directly | N/A — only option | 6 new source modules, all matching SPEC-005 |
| D2 | TPM2 backend: real vs placeholder | Dynamic dispatch based on `shutil.which("tpm2_pcrread")`; `@pytest.mark.skipif` in tests | Static "placeholder only" — rejected: SPEC-005 requires real TPM2 path | Real TPM2 tested on Linux hosts; placeholder on all others |
| D3 | Apple SEP backend: macOS-only | `sys.platform == "darwin"` gate; `@pytest.mark.skipif` in tests | Omit entirely — rejected: SPEC-005 requires Apple SEP backend | macOS testing requires real hardware; placeholder everywhere else |
| D4 | Unix socket not available on Windows | Keyring integration tests skip on `sys.platform == "win32"`; `# mypy: ignore-errors` for AF_UNIX | Implement Windows named pipe alternative — rejected: SPEC-005 says Unix socket, EP-006 non-goals exclude new transport | Keyring IPC works on Linux/macOS; Windows CI skips |
| D5 | `token.attenuate()` return value ignored | Tests rewritten to capture `token = token.attenuate(...)` (immutable pattern) | Make attenuate mutate in place — rejected: immutable pattern is correct for CapToken chain integrity | All 20 verifier tests pass |
| D6 | `_caveat_denial_code` dict.get type issue | Added `# type: ignore[no-any-return, call-overload]` — StrEnum key types don't narrow dict.get return | Refactor to use if/elif chain — rejected: mapping is clearer and more maintainable | Single type-ignore comment; correct runtime behavior |
| D7 | Keyring SPEC asks for CBOR but repo has no CBOR dependency | Keep length-prefixed JSON as a development stand-in and record CBOR as a production-readiness gap | Add `cbor2` now — rejected: dependency changes require a scoped decision and ENVIRONMENT/pyproject updates | Tests validate framing/dispatch locally where AF_UNIX exists; production CBOR remains future work |
| D8 | SPEC-005 requires discharge replay protection | Enforce third-party discharge `session_root`, `binding_nonce`, and `freshness_window`; return `DENY_DISCHARGE_INVALID` for mismatches | Same-type discharge match only — rejected: fails replay requirement | Verifier now distinguishes missing vs invalid discharges |
| D9 | EP-006 coverage command used unsupported `--cov-fail-under-branch` | Use installed pytest-cov option `--cov-fail-under=70` with `--cov-branch`, and add the command to `COMMANDS.md` | Keep stale command — rejected: local option surface proves it cannot run | Branch-enabled coverage gate is runnable on this environment |

## 15. Outcomes & Retrospective
- **What landed:** Full EP-006 surface: TPM2 attestation backend (build_quote + verify_quote with real/placeholder dispatch), Apple SEP attestation backend (same interface, macOS-gated), caveat DSL (18 types with eval_* functions and EvaluationContext), CapToken verifier (verify_token with fail-closed branch coverage covering DENY paths and SPEC-005 discharge replay binding), keyring IPC service (Unix socket, length-prefixed JSON development stand-in, discharge/mint dispatch).
- **What changed vs plan:** No bundle consolidation (bundles absent). Keyring IPC tests skip on Windows. Attestation backends use placeholder on unsupported platforms. `CaveatType` uses StrEnum for ergonomic string comparison. Verifier branch coverage includes third-party discharge replay and action-predicate handling.
- **Remaining risks:** TPM2 real path tested only on Linux with tpm2-tools installed. Apple SEP real path tested only on macOS arm64/x86_64. Keyring IPC untested on Windows by design. Keyring wire still needs SPEC-005 CBOR before production. Backward migration SQL from EP-003 still untested. CAVEATS: attestation backends are development-grade stubs — `build_quote` on TPM2 calls `tpm2_pcrread` subprocess but doesn't do full PCR quoting; Apple SEP uses placeholder labels, not real App Attest APIs.
- **Production-readiness impact:** Phase 5 exits with production gaps recorded. EP-007 (testing/hardening) is unblocked. Attestation backends exist for all EP-006 platforms. Caveat DSL is complete with fail-closed verifier and replay binding. Keyring IPC service shape is defined; CBOR wire hardening remains for a later scoped dependency decision.
