# SECURITY

## Security Goals
1. Confidentiality of message bodies against any party except the two endpoints, with quantum resilience.
2. Metadata privacy against a global passive observer.
3. Mutual authentication of code, config, and principal.
4. Fine-grained, session-bound, revocable authority for every action.
5. Audit without disclosure.

## Threat Model Summary
| Adversary | Defeated by |
|---|---|
| Passive network observer | L1 Sphinx + constant-rate cover |
| Active mix | Stratified topology, replay tags, loop cover |
| Key-only impostor | L3 mutual attestation (code + config + principal) |
| Prompt-injected clone | L3 `config_measurement` mismatch |
| Cross-vendor session replay | L3 `cert_chain` + L5 `bound_to_session` |
| Stolen CapToken | L5 `bound_to_session`, `bound_to_instance` caveats |
| Harvest-now-decrypt-later | Hybrid PQ throughout L3 + L4 |
| Endpoint compromise (post-hoc) | L4 forward secrecy + PCS at next ratchet |
| Subpoena of relay | L1 nothing-to-log; L2 epoch erasure |
| Subpoena of vendor cloud | L4 content E2EE; L5 capability split |
| DHT eclipse | Kademlia k-bucket diversity + 3 disjoint paths |
| Sybil | Directory-issued node ID certs |

## Cryptographic Rules
- Hybrid PQ **mandatory** at every KEM and signature.
- Approved deps: `cryptography`, `oqs` (liboqs), stdlib `hashlib` / `hmac`.
- Approved primitives: SHA3-256, HKDF-SHA3-256, X25519, ChaCha20-Poly1305, Ed25519, ML-KEM-768 (FIPS 203), ML-DSA-65 (FIPS 204), BLAKE3 (preferred) or HMAC-SHA3-256 fallback.
- Forbidden: SHA-1 anywhere; AES-CBC; static IVs.

## Authentication / Authorization Rules
- Endpoint identity = DID + attestation quote. Key alone insufficient.
- Authentication mutual; both sides attest first.
- Principal binding = hybrid sig over `(instance_pubkey || runtime_measurement || config_measurement || not_after)`.
- Verifier fails **closed** on: unknown caveat types, mismatched `bound_to_session` / `bound_to_instance`, stale `revocation_epoch`, expired `time.before`, missing / expired / mismatched discharge.

## Input Validation Rules
- Bytes from outside the process parsed once per layer.
- Length checks, then structural, then semantic.
- Typed errors; no generic exceptions across layer boundaries.

## Output Encoding Rules
- Canonical CBOR (RFC 8949 deterministic). Reference uses sorted-key JSON as stand-in.

## Secret Management Rules
- No private keys committed. Test keys generated fresh per test.
- Runtime keys in `*_sk` fields excluded from `__repr__` and structured logs.
- Keyring service holds principal + discharger keys; never enters agent runtime address space.

## Dependency Security Rules
- `uv run pip-audit` in CI on every PR.
- Runtime-dep CVE blocks release unless code path provably unreachable (documented in DECISIONS.md).
- Adding any crypto dep requires ADR.

## Logging Redaction Rules
`aethermesh.common.logging` rejects these keys at emission:
```
FORBIDDEN_LOG_KEYS = {
  "intent_key", "message_key",
  "principal_sk", "discharger_sk", "instance_sk", "static_sk",
  "x25519_sk", "mlkem_sk", "mldsa_sk",
  "body", "body_pt", "plaintext",
  "root_key", "ck", "ck_final",
  "session_root",          # log session_root_hash (SHA3-256) instead
  "root_macaroon_key",
  "discharge_predicate",   # log predicate.kind only
}
```
CI gate: `tests/security/test_log_redaction.py` asserts none appear in a sample end-to-end flow under `caplog`.

## Data Protection Rules
- Audit log stores `body_hash` only.
- Transparency log stores `receipt_id` hashes only.
- DID caches store public keys only.
- Revocation registry caches signed manifests verbatim.

## Production Data Rules
See AGENTS.md § 13.

## Safe Migration Rules
- Audit DB: `SCHEMA_VERSION` + `MIGRATIONS[N]` with forward + backward SQL.
- Dropping a column requires ADR.
- No migration runs in CI outside fixture paths.

## API Security Rules
- Public APIs accept bytes / immutable types where possible.
- Typed error codes per layer's taxonomy.
- Rate limiting is the embedder's responsibility; L1 gateways apply per-source-IP token bucket.

## Rate Limiting
- L1 mix: per-source-IP token bucket (operator-configured).
- L2 DHT STORE: per-key PoW.
- L5 keyring: max 5 discharges / session / minute by default.

## File Upload Rules
Not applicable.

## Security Checklist (Crypto-Touching PRs)
- [ ] No new crypto primitive without ADR.
- [ ] Hybrid PQ at every new call site.
- [ ] `./scripts/security-check.sh` passes.
- [ ] `./scripts/dependency-audit.sh` passes.
- [ ] Failure-mode test added (replay / scope / discharge / revocation).
- [ ] No new log record contains a forbidden key.
- [ ] No new vector file lacks `TEST_ONLY` label.

## STOP Conditions for Security-Sensitive Actions
STOP and request explicit permission for:
- Rotating a principal or discharger key.
- Publishing a `RevocationManifest`.
- Updating any platform attestation root.
- Changing `FORBIDDEN_LOG_KEYS`.
- Introducing a new cryptographic primitive.
- Relaxing any caveat-fail-closed behavior.
- Lowering any coverage threshold or test gate.
- Setting `AEP_PQ_BACKEND` to anything other than `liboqs` in a production-targeted config.
