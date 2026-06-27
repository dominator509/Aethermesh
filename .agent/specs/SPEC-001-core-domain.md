# SPEC-001 — Core Domain

- **Status:** Draft  - **Owner:** Architecture  - **Phase:** 1  - **ExecPlans:** EP-002

## User-Visible Goal
A small, well-tested `aethermesh.common` providing cryptographic primitives, canonical encoding, and DID resolution.

## Non-Goals
Wire-format parsing (per-layer); persistence (`aethermesh.tools`).

## Terms
- **Hybrid PQ combiner:** `HKDF-SHA3-256(salt=ck, ikm=dh || ss_pq, info=<domain>)`.
- **Canonical CBOR:** RFC 8949 deterministic; reference uses sorted-key JSON.

## Required Behavior
1. `sha3_256(bytes) -> bytes` — 32 B digest.
2. `hkdf_sha3_256(ikm, salt, info, length=32) -> bytes`.
3. `aead_seal(key, nonce, plaintext, ad=b"") -> bytes`; `aead_open(...)` raises on tag mismatch.
4. `x25519_keygen() -> (sk, pk)`; `x25519_dh(sk, peer_pk) -> bytes`.
5. `hybrid_sign(sk, msg) -> bytes`; `hybrid_verify(pk, msg, sig) -> bool`.
6. `mlkem_keygen() -> MLKem768KeyPair`; `mlkem_encaps(pk) -> (ct, ss)`; `mlkem_decaps(sk, ct) -> ss`. Backend by `AEP_PQ_BACKEND`.
7. `canonical_bytes(obj) -> bytes` — deterministic.
8. `DIDResolver.register/resolve/known/bump_revocation_epoch`.

## Inputs / Outputs
Bytes in, bytes out. No state outside resolver.

## Error States
- `ValueError` for length mismatches.
- `InvalidTag` for AEAD opens.
- `KeyError` for unknown DIDs.

## Data Rules
Resolver caches per epoch; no persistence.

## Security Rules
- Hybrid PQ at every KEM/sig path.
- No log line contains key material.
- `AEP_PQ_BACKEND=placeholder` rejected at process start in production.

## Performance
- AEAD seal/open ≥ 200 MB/s/core.
- HKDF derive ≤ 50 µs per 32 B output.

## Observability
- Histogram `aep_common_aead_duration_seconds` (`op`).
- Counter `aep_common_pq_ops_total{op, backend}`.

## Required Tests
- Property-based round-trip for AEAD and canonical encoding.
- NIST vector tests for SHA3-256 and HKDF.
- Negative: `aead_open` with truncated tag raises.

## Acceptance Criteria
- `tests/unit/common/` coverage ≥ 90% lines.
- Property tests pass; NIST vectors round-trip.
