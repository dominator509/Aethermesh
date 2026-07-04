# ARCHITECTURE

## Purpose
Defines repository boundaries, invariants, and concrete import rules for the AetherMesh / AEP repo.

## System Overview
```
+---------------------------------------------+
| L5 Authority (CapTokens, discharges, audit) |
+---------------------------------------------+
| L4 Session (PQ Double Ratchet + MLS group)  |
+---------------------------------------------+
| L3 Handshake (Noise-PQ XK + attestation)    |
+---------------------------------------------+
| L2 Discovery (Capability-hashed DHT)        |
+---------------------------------------------+
| L1 Transport (Sphinx over q-mix QUIC)       |
+---------------------------------------------+
| common (crypto primitives, DIDs, canonical) |
+---------------------------------------------+
```

## Repository Map (Intended)
```
aethermesh/
  common/   L1_sphinx/   L2_dht/   L3_handshake/   L4_ratchet/   L5_captokens/
  demos/    tools/       api/
tests/
  unit/L{1..5}/  integration/  interop/  property/  vectors/  perf/  e2e/  security/
.agent/   scripts/   bundles/   ops/
```

## Discovery (EP-000) — actual vs intended (2026-07-03)

| Path | Intended | Actual | Status |
|---|---|---|---|
| `aethermesh/` | 7 subpackages | Absent | To be created EP-001 |
| `tests/` | 9 subdirectories | Absent | To be created EP-001 |
| `bundles/` | 5 reference bundles (L1-L5) | Absent | To be created EP-001 |
| `pyproject.toml` | Present with deps | Absent | To be created EP-001 |
| `.github/workflows/` | GHA CI | Absent | To be created EP-009 |
| `.agent/` | Specs, ExecPlans, templates | Present (40 files) | OK |
| `scripts/` | Shell wrappers (11 scripts) | Present | OK — untested without `aethermesh/` |
| `*.md` (authority docs) | AGENTS, ARCHITECTURE, COMMANDS, etc. | Present (18 docs) | OK |
| Python | ≥ 3.11 | 3.14.4 | OK |
| uv | ≥ 0.4 | 0.11.25 | OK |
| Git | Single commit | `25a1434` Initial blueprint import | OK |
| Remote | GitHub | `github.com/dominator509/Aethermesh.git` | OK |

**Verdict:** Repo is a planning/agent blueprint with zero implementation code. EP-001 must bootstrap `pyproject.toml`, `aethermesh/`, `tests/`, and `bundles/` from scratch.

## Layer Responsibilities
| Layer | Responsibility | Key Public API |
|---|---|---|
| common | Hashes, HKDF, X25519, AEAD, PQ KEM/sig dispatch, canonical, DID resolver | `sha3_256`, `hkdf_sha3_256`, `mlkem_*`, `mldsa_*`, `canonical_bytes`, `DIDResolver` |
| L1_sphinx | 2 KB Sphinx, hop processing, q-mix QUIC, cover, lanes, directory, gateways | `SphinxPacket.build`, `MixNode.process`, `PathSelector.select`, `CoverScheduler` |
| L2_dht | Capability descriptors, Kademlia, bucket-PIR, intro blocks, revocation, endorsement bulletins | `CapabilityDescriptor`, `KademliaNode`, `DHTClient.lookup`, `SphinxIntroBlock` |
| L3_handshake | Noise-PQ XK, attestation quotes, principal binding, `session_root` | `HandshakeInitiator`, `HandshakeResponder`, `AttestationQuote`, `SessionState` |
| L4_ratchet | PQ Double Ratchet, MLS PQ ciphersuite + extensions, intent/message key split, policy | `PairRatchet`, `MlsGroup`, `PolicyLayer`, `IntentHeader` |
| L5_captokens | CapTokens (signed verification_seed), caveats, discharges, revocation, audit, keyring | `CapToken`, `Caveat`, `Discharge`, `CapTokenVerifier`, `KeyringService`, `AuditLog` |

## Dependency Rules (Enforced by `import-linter` in CI)
- `common` may not import any layer.
- `L1_sphinx` may import `common` only.
- `L2_dht` may import `common` and `L1_sphinx` only.
- `L3_handshake` may import `common`, `L1_sphinx`, `L2_dht` only.
- `L4_ratchet` may import `common`, `L1_sphinx`, `L3_handshake` only. It does **not** import `L2_dht`.
- `L5_captokens` may import `common` only. L4 consumes L5 via `aethermesh.L4_ratchet.policy_layer`.
- `demos/` and `tools/` may import any layer.
- `tests/unit/LX/` may import only `aethermesh.common` and `aethermesh.LX_*`.

## Runtime Flow
```
agent_a wants peer doc review
  -> L5: mint/attenuate CapToken with bound_to_session pending
  -> L2: lookup CapabilityDescriptor -> SphinxIntroBlock
  -> L1: Sphinx packet to intro point (fast lane)
  -> L3: 3-msg handshake; session_root = SHA3-256(ck_final); transmit CapToken bundle in msg 3
  -> L4: per-msg symmetric chain; intent_key to policy, message_key sealed;
         policy validates IntentHeader against CapTokens; on ALLOW, message_key released to model
  -> L5: AuditReceipt emitted with hash-only fields
```

## Data Flow
- Keys flow downward only at boundary: L3 hands `(root_key, session_root)` to L4 once at finalization.
- Encrypted messages flow through L1 unchanged.
- CapTokens ride L3 msg 3 and reside in L4 session store thereafter.
- Audit receipts emit from L4 policy to L5 `AuditLog`; only `receipt_id` hashes leave the process.

## State Management Rules
- Session state in `L4_ratchet.PairRatchet` (pair) or `MlsGroup` (group). No global session registry.
- Revocation state in `L5_captokens.RevocationRegistry`, lazily hydrated.
- Replay caches per-node + per-session; TTL in `common.constants`.

## Persistence Boundaries
- SQLite allowed only in `aethermesh.tools.audit_db` and `aethermesh.tools.cache_db`.
- No protocol-core module opens a file handle. Library default is in-memory.

## External Integration Boundaries
| External | Boundary Module | Responsibility |
|---|---|---|
| `oqs` (liboqs) | `common.pq_backend` | ML-KEM-768, ML-DSA-65 ops |
| QUIC (`aioquic`/`quiche`) | `L1_sphinx.qmix_quic` | One Sphinx per DATAGRAM |
| MLS library | `L4_ratchet.mls_group` | TreeKEM + Commit + AEP extensions |
| TEE attestors | `L3_handshake.attestation.backends.*` | Hardware quotes |
| Sigstore Rekor | `L5_captokens.transparency_log` | Submit `receipt_id` only |

## Security Boundaries
- Policy layer separate process from model layer in prod; IPC contract in SPEC-005.
- Keyring service reached only via Unix socket at `AEP_KEYRING_SOCKET`.
- Mix nodes never see plaintext bodies; verified by L1 test feeding known random plaintexts.

## Validation Boundaries
- One parser per layer per wire format.
- Caveat evaluation only in `L5_captokens.verifier`.
- Attestation verification only in `L3_handshake.attestation`.

## Error Handling Boundaries
- L3: `L3_handshake.aborts.AbortCode`.
- L4: `L4_ratchet.policy_layer.PolicyDecision` + L4 wire codes.
- L5: `L5_captokens.verifier.VerificationDecision`.
- Cross-layer errors translate to receiving layer's taxonomy; no internal exception types leak.

## Observability Boundaries
- One logger via `common.logging.logger`. Metrics via `common.metrics.counter()/histogram()`.

## Architectural Invariants
1. `session_root` threads L3 → L4 → L5.
2. Policy layer never holds `message_key` simultaneously with `intent_key`; OS process boundary enforces in production.
3. Hybrid PQ mandatory at every cryptographic step.
4. 2048-byte fixed Sphinx packets are the only thing on L1 wire.
5. `capability_root` = `SHA3-256(canonical(schema_json))`.
6. Replay caches are 2-epoch deep; never disabled.

## Forbidden Changes
- Removing intent/message key split at L4.
- L1 importing any higher layer.
- Global session registry.
- Centralized server in any code path.
- Replacing hybrid PQ with classical-only or PQ-only.
- Policy layer calling model layer without `release(Ns)` handoff.
- Persisting plaintext message bodies anywhere.
- Logging any FORBIDDEN_LOG_KEYS value.

## How to Add a New Feature
1. Open or write the relevant SPEC.
2. Create an ExecPlan from `.agent/templates/execplan-template.md`.
3. Confirm dependency rules.
4. Add tests under matching `tests/unit/LX/`.
5. Implement smallest milestone; validate; tick; continue.
6. Update ARCHITECTURE.md, DECISIONS.md, and touched SPECs in the same commit.

## How to Add a New Dependency
1. Confirm no existing dep suffices.
2. `uv add <pkg>`; commit lockfile.
3. Add ADR.
4. Update ENVIRONMENT.md if a system package is required.
5. Run `./scripts/security-check.sh` and `./scripts/dependency-audit.sh`.

## How to Modify a Data Schema
1. Bump `aethermesh.tools.audit_db.SCHEMA_VERSION`.
2. Add `MIGRATIONS[N]` with forward + backward SQL.
3. Update SPEC-002.
4. Update `tests/unit/tools/test_audit_db.py`.

## How to Add a New Integration
See External Integration Boundaries. Add module + ADR + feature flag in `common.constants` + integration test exercising old and new paths.

## Architecture Review Checklist
- [ ] No new import violates dependency rules.
- [ ] No new module in a directory lacking an ADR.
- [ ] No new persistence outside `aethermesh.tools.*`.
- [ ] No new external HTTP destination outside allowed integration modules.
- [ ] No new logger instantiation outside `common.logging`.
- [ ] Test coverage added for the new boundary.
- [ ] Updated SPEC and ADR in the same commit.
