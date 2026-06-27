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
- `tests/unit/common/test_{hashes,aead,x25519,pq_backend,canonical,did_resolver,errors}.py`
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
M1 -> M8.

## 10. Validation and Acceptance
### Acceptance Criteria
- [ ] Every SPEC-001 signature exists.
- [ ] Both PQ backends (where available) pass.
- [ ] Property tests >=100 examples each.
- [ ] Coverage >=90% lines on common/.
- [ ] `./scripts/verify.sh` exits 0.

## 11. Idempotence and Recovery
Each module single-source. Tests safe to re-run.

## 12. Progress
- [ ] M1 — Hashes + HKDF
- [ ] M2 — AEAD
- [ ] M3 — X25519
- [ ] M4 — PQ backend
- [ ] M5 — Canonical
- [ ] M6 — DID resolver
- [ ] M7 — Errors
- [ ] M8 — Coverage gate
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
- **Production-readiness impact:** Phase 1 exits.
