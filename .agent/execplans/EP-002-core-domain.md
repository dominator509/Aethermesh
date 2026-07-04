# EP-002 — Core Domain

- **Status:** Draft  - **Owner:** Architecture  - **Phase:** 1  - **Specs:** SPEC-001, SPEC-006

## 1. Purpose / Big Picture
Consolidate cryptographic + canonical-encoding primitives from `bundles/aethermesh_L{1..5}/code/crypto_primitives.py` into `aethermesh.common`. Implement `pq_backend` dispatch (placeholder + liboqs). Reach >=90% line coverage on `aethermesh/common/`.

## 2. Scope
- `aethermesh/common/{__init__,hashes,aead,x25519,pq_backend,canonical,did_resolver,errors,constants}.py`
- Matching `tests/unit/common/` test files.

## 3. Non-Goals
- No layer code (L1-L5).
- No persistence.
- No new deps beyond `cryptography` (+ optional `oqs`).

## 4. Context and Orientation
Each bundle has its own `crypto_primitives.py` with small drift. This plan creates single source of truth.

## 5. Files to Read First
1. `AGENTS.md`  2. `.agent/specs/SPEC-001-core-domain.md`  3. `bundles/aethermesh_L1/code/crypto_primitives.py`  4. `bundles/aethermesh_L5/code/crypto_primitives.py`  5. `bundles/aethermesh_L5/code/canonical.py`  6. `ARCHITECTURE.md` Dependency Rules

## 6. Files to Change
- `aethermesh/common/{__init__,hashes,aead,x25519,pq_backend,canonical,did_resolver,errors,constants}.py`
- `tests/unit/common/test_{hashes,aead,x25519,pq_backend,canonical,did_resolver,errors,constants}.py`
- `tests/property/test_aead_roundtrip.py`, `tests/property/test_canonical_roundtrip.py`
- `tests/vectors/sha3_256_nist.json` (TEST_ONLY label)

## 7. Interfaces and Contracts
Per SPEC-001 § Required Behavior — every signature must exist.

## 8. Milestones

### M1 — Hashes + HKDF
- **Goal:** `sha3_256` + `hkdf_sha3_256` with NIST coverage.
- **Files to Read:** bundle `crypto_primitives.py`, SPEC-001.
- **Files to Change:** `aethermesh/common/hashes.py`, `tests/unit/common/test_hashes.py`, `tests/vectors/sha3_256_nist.json`.
- **Exact Edits Expected:** Type-annotated implementations. Vector test loads JSON, asserts each digest.
- **Validation Command:** `uv run pytest tests/unit/common/test_hashes.py -q`
- **Expected Result:** exit 0; >=5 NIST KAT vectors pass.
- **Recovery:** Per AGENTS § 7.

### M2 — AEAD
- **Goal:** `aead_seal`/`aead_open` ChaCha20-Poly1305.
- **Files to Read:** bundle `crypto_primitives.py`.
- **Files to Change:** `aethermesh/common/aead.py`, `tests/unit/common/test_aead.py`, `tests/property/test_aead_roundtrip.py`.
- **Exact Edits Expected:** Wrappers over `cryptography.hazmat.primitives.ciphers.aead.ChaCha20Poly1305`. Open raises on tag mismatch. Property test: roundtrip for arbitrary bytes <=2048.
- **Validation Command:** `uv run pytest tests/unit/common/test_aead.py tests/property/test_aead_roundtrip.py -q`
- **Expected Result:** exit 0; property test >=100 examples.
- **Recovery:** Per AGENTS § 7.

### M3 — X25519
- **Goal:** `x25519_keygen`/`x25519_dh`.
- **Files to Change:** `aethermesh/common/x25519.py`, `tests/unit/common/test_x25519.py`.
- **Exact Edits Expected:** Wrappers over `cryptography` lib. Round-trip A<->B shared secret test.
- **Validation Command:** `uv run pytest tests/unit/common/test_x25519.py -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

### M4 — PQ backend dispatch
- **Goal:** `mlkem_*` / `mldsa_*` with placeholder + liboqs paths.
- **Files to Read:** bundle `crypto_primitives.py`, `ENVIRONMENT.md`.
- **Files to Change:** `aethermesh/common/pq_backend.py`, `tests/unit/common/test_pq_backend.py`.
- **Exact Edits Expected:** `BACKEND = os.environ.get("AEP_PQ_BACKEND", "placeholder")`. Placeholder uses in-tree impls with correct byte sizes (1184/1088 ML-KEM); liboqs dispatches to `oqs` package. Size constants match SPEC.
- **Validation Command:** `AEP_PQ_BACKEND=placeholder uv run pytest tests/unit/common/test_pq_backend.py -q`
- **Expected Result:** exit 0.
- **Recovery:** If `oqs` missing, skip with `pytest.importorskip`; record in Decision Log.

### M5 — Canonical encoding
- **Goal:** Deterministic JSON stand-in for CBOR.
- **Files to Change:** `aethermesh/common/canonical.py`, `tests/unit/common/test_canonical.py`, `tests/property/test_canonical_roundtrip.py`.
- **Exact Edits Expected:** Sort keys, bytes->hex default. Property test on round-trip.
- **Validation Command:** `uv run pytest tests/unit/common/test_canonical.py tests/property/test_canonical_roundtrip.py -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

### M6 — DID resolver
- **Goal:** In-memory `DIDResolver`.
- **Files to Change:** `aethermesh/common/did_resolver.py`, `tests/unit/common/test_did_resolver.py`.
- **Exact Edits Expected:** `register`/`resolve`/`known`/`bump_revocation_epoch`. Tests: hit, miss (KeyError), epoch bump.
- **Validation Command:** `uv run pytest tests/unit/common/test_did_resolver.py -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

### M7 — Errors + translations
- **Goal:** `aethermesh.common.errors` with per-layer enums + TRANSLATIONS.
- **Files to Read:** SPEC-006.
- **Files to Change:** `aethermesh/common/errors.py`, `tests/unit/common/test_errors.py`.
- **Exact Edits Expected:** Re-export `AbortCode`, `PolicyDecision`, `VerificationDecision`. `TRANSLATIONS` cross-layer mapping.
- **Validation Command:** `uv run pytest tests/unit/common/test_errors.py -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

### M8 — Coverage gate
- **Goal:** >=90% line coverage on `aethermesh/common/`.
- **Files to Change:** add edge tests where missed.
- **Validation Command:** `uv run pytest tests/unit/common/ tests/property/ --cov=aethermesh.common --cov-report=term-missing --cov-fail-under=90 -q`
- **Expected Result:** exit 0; `TOTAL >=90%`.
- **Recovery:** Per AGENTS § 7.

## 9. Concrete Steps
M1 -> M8. All executed 2026-07-03.

## 10. Validation and Acceptance
### Acceptance Criteria
- [x] Every SPEC-001 signature exists. (sha3_256, hkdf_sha3_256, aead_seal/open, x25519_keygen/dh, mlkem_*, mldsa_*, hybrid_sign/verify, canonical_bytes/from_bytes, DIDResolver)
- [x] Placeholder PQ backend passes. liboqs path is present but skipped in this Windows/Python 3.13 environment because `oqs` is not installed (Decision Log D7).
- [x] Property tests >=100 examples each. (AEAD: 200×4=800; Canonical: 200×3=600)
- [x] Coverage >=90% lines on common/. (99%, 363 stmts)
- [x] `./scripts/verify.sh` exits 0. (lint→format→typecheck→unit→integration→e2e→build→security→audit→smoke: all ok)

## 11. Idempotence and Recovery
Each module single-source. Tests safe to re-run. liboqs paths excluded from coverage baseline via `# pragma: no cover`.

## 12. Progress
- [x] M1 — Hashes + HKDF (sha3_256, hkdf_sha3_256; 28 tests incl. 8 NIST KAT vectors)
- [x] M2 — AEAD (aead_seal/open via ChaCha20Poly1305; 20 unit + 4 property = 24 tests)
- [x] M3 — X25519 (x25519_keygen/dh; 9 tests incl. RFC 7748 §6.1 vector)
- [x] M4 — PQ backend (mlkem_*/mldsa_* + hybrid; 21 tests; placeholder fully covered, liboqs pragma-excluded)
- [x] M5 — Canonical (canonical_bytes/from_bytes; 23 unit + 3 property = 26 tests)
- [x] M6 — DID resolver (register/resolve/known/bump_revocation_epoch; 14 tests)
- [x] M7 — Errors (AbortCode/L4WireCode/PolicyDecision/VerificationDecision/TRANSLATIONS; 15 tests)
- [x] M8 — Coverage gate (99% — 149 tests total, 363 stmts, 2 missed lines)
- [x] Final review

## 13. Surprises & Discoveries
1. **No bundle code to consolidate**: EP-002 references `bundles/aethermesh_L{1..5}/code/crypto_primitives.py` — EP-000 confirmed these don't exist. All modules implemented from SPEC-001 directly.
2. **ML-KEM/DSA placeholder key sizes**: SK size calculation initially wrong (sk = seed + pk without padding to full PQ size). Fixed by adding zero-padding to reach FIPS 203/204 sizes.
3. **liboqs branch coverage**: ~40% of pq_backend.py unreachable without `oqs` package. Marked liboqs paths with `# pragma: no cover` to keep coverage baseline honest.
4. **Ruff/mypy strictness**: 20+ lint issues on first verify run — unused imports, line length, import ordering, N818 (HandshakeAbort naming per SPEC-006), B028 (warnings.warn stacklevel), C401 (set comprehensions), B905 (zip strict). All fixed.
5. **Property test `assert False`**: Ruff B011 flags `assert False` in except-blocks (optimized out with `python -O`). Replaced with `raise AssertionError()`.
6. **Real common test surface**: EP-001 had 1 placeholder unit test; EP-002 adds full common coverage across hashes, AEAD, X25519, PQ, canonical, DID resolver, errors, constants, and property tests.
7. **Python 3.13.13 in venv**: `uv sync` resolved to CPython 3.13.13, not host's 3.14.4. Both satisfy >=3.11.
8. **Canonical bytes marker collision**: Audit found strings starting with `0x` decoded as bytes. Added a one-character escape for user strings that would collide with the bytes marker.

## 14. Decision Log
| # | Context | Decision | Alternatives | Consequences |
|---|---|---|---|---|
| D1 | No bundles exist to consolidate from | Implement all modules from SPEC-001 directly | Create dummy bundles first — rejected: adds files not needed for the final package | Clean implementation without bundle artifacts |
| D2 | Placeholder PQ uses X25519 KEM + Ed25519 sigs padded to FIPS sizes | Use `cryptography` library's X25519/Ed25519 with zero-padding to ML-KEM-768 / ML-DSA-65 byte sizes | Implement simplified lattice-based KEM — rejected: excessive for placeholder | Placeholder is functional for testing, not cryptographically PQ |
| D3 | Canonical encoding: JSON with hex-encoded bytes | Sorted-key JSON, bytes as `0x<hex>` strings | CBOR — rejected: no cbor2 dependency yet; JSON is simpler for Phase 1 | Compatible with SPEC-001 interim JSON approach |
| D4 | 21 liboqs-only statements uncovered | Mark with `# pragma: no cover` | Install oqs for CI coverage — rejected: liboqs not available on all platforms | Honest coverage baseline; liboqs path tested when available |
| D5 | N818 HandshakeAbort naming | Add `# noqa: N818` — name is per SPEC-006 § L3 | Rename to HandshakeAbortError — rejected: SPEC takes priority over lint | SPEC-006 compliance maintained |
| D6 | test_constants.py not in original EP-002 Files to Change | Created to reach 90% coverage (constants.py was at 0%) | Move constants to another module — rejected: constants.py is listed in Files to Change and deserves its own test | 1 extra test file; coverage jumped from 86% to 95% |
| D7 | liboqs backend untestable in this environment | Mark liboqs paths `# pragma: no cover`; tests use `AEP_PQ_BACKEND=placeholder` | Install oqs — rejected: oqs wheel not available for Windows Python 3.13 | Placeholder backend passes locally; liboqs is deferred until oqs is available |
| D8 | Audit found canonical `0x` string/bytes ambiguity | Escape user strings beginning with `0x` or `\` while keeping bytes encoded as `0x<hex>` | Switch to a fully tagged JSON structure — rejected: larger wire change than needed for EP-002 | Property round-trip covers hex-like strings without changing byte marker semantics |

## 15. Outcomes & Retrospective
- **What landed:** Complete `aethermesh.common` implementation: 8 source modules (hashes, AEAD, X25519, PQ backend, canonical, DID resolver, errors, constants), NIST SHA3-256 vectors, RFC 7748 test vector, property-based AEAD + canonical roundtrip tests. Common/property coverage gate: 149 tests, 99% line coverage. All verify.sh gates pass.
- **What changed vs plan:** No bundle consolidation (bundles don't exist). `test_constants.py` added for coverage and recorded in Files to Change. liboqs paths pragma-excluded. SPEC-001 implemented from scratch. `HandshakeAbort` kept per SPEC naming (with noqa). Audit added canonical string escaping for `0x` collisions and made `AeadOpenError` subclass `InvalidTag`.
- **Remaining risks:** liboqs path untested on this platform (oqs wheel not available for Windows CPython 3.13). PQ placeholder uses classical crypto with PQ-sized padding — cryptographically sound building blocks but not actual post-quantum. Python 3.13 vs 3.11 compatibility not yet tested on CI (GHA uses ubuntu-latest Python 3.11).
- **Production-readiness impact:** Phase 1 exits. `aethermesh.common` is ready for layer consumption. EP-003 (data/persistence) and EP-004 (API layer) are unblocked. All SPEC-001 signatures exist and are tested.
