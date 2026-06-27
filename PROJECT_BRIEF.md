# PROJECT_BRIEF — AetherMesh / AEP

## Project Name
AetherMesh / AEP (Agent Exchange Protocol).

## Problem Statement
AI agents have no vendor-neutral way to communicate across the public internet without (a) a central server seeing the social graph, (b) a shared vendor account, or (c) bearer tokens with no fine-grained authority. Existing E2EE messengers leak metadata; existing capability systems (UCAN, macaroons) lack session binding and PQ resilience; existing PQ handshakes (TLS 1.3 hybrid) do not bind code, configuration, and principal into a single attested transcript.

## Target Users
1. AI agent runtime authors (vendor SDKs + self-hosted).
2. Keyring service authors (Apple SEP, Android StrongBox, TPM2 Linux).
3. Mix node / gateway operators (vendor + community).
4. Security researchers.

## Primary User Outcomes
1. Find a peer agent anonymously by capability + endorsement.
2. Establish a hybrid PQ session with mutual remote attestation of code, config, and principal.
3. Exchange ratcheted messages whose intent is policy-checked before the body key is released to the model layer.
4. Authorize actions with macaroon CapTokens that are session-bound and require fresh user discharges for write-class operations.
5. Audit every action without revealing content.

## Business Goals
- Ship a vendor-neutral 1.0 with two independent implementations passing interop.
- License MIT.
- No telemetry leaves library or mix nodes.
- Backward compatibility within AEP-1.x; breaking changes require major bump.

## Technical Goals
- Hybrid PQ throughout: X25519 + ML-KEM-768 (FIPS 203); Ed25519 + ML-DSA-65 (FIPS 204). Never PQ-only.
- L1 fast-lane p95 ≤ 300 ms.
- L3 handshake ≤ 550 ms over fast lane.
- L4 non-DH-step messages ≥ 200k msg/s/core.
- L5 CapToken verify ≤ 300 µs.
- Cover traffic ≤ 80 kbit/s active, ≤ 16 kbit/s idle.
- Coverage ≥ 85% lines / ≥ 70% branches per layer.

## Out-of-Scope (Non-Goals)
- Not a human messenger.
- Not an LLM serving protocol.
- Not a TLS replacement.
- Not a global agent search engine.
- Not a blockchain.
- Not a custodial key store.

## Success Metrics
- Two-impl interop matrix: 100% pass on spec-defined test vectors.
- Coverage ≥ 85% lines / ≥ 70% branches.
- Performance budgets above met on the reference benchmark VM.
- Zero secrets in `git log -p` repository-wide.
- All 5 layer demos exit 0 on a clean checkout post `uv sync`.
- `./scripts/production-readiness-check.sh` exits 0.

## Production Readiness Definition
Headline gates:
1. EP-000..EP-010 closed with Outcomes & Retrospective complete.
2. `./scripts/verify.sh` exits 0.
3. `./scripts/production-readiness-check.sh` exits 0.
4. Two independent implementations exchanged traffic across all five layers (recorded in `tests/interop/results/INTEROP_REPORT.md`).
5. Real ML-KEM-768 and ML-DSA-65 via liboqs replace every placeholder; `AEP_PQ_BACKEND=liboqs` enforced in prod.
6. Security review sign-off recorded as ADR-0010 = Accepted.
