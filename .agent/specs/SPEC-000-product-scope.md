# SPEC-000 — Product Scope

- **Status:** Draft  - **Owner:** Product  - **Phase:** 0  - **ExecPlans:** EP-000, EP-001

## User-Visible Goal
Two AI agents anywhere on the public internet can find each other anonymously by capability + endorsement, authenticate with mutual attestation, exchange ratcheted post-quantum-secure messages, and have every action gated by precisely-scoped CapTokens.

## Non-Goals
Not a human messenger; not an LLM serving protocol; not a TLS replacement; not a global agent search; not a custodial key store; not a blockchain.

## Terms
- **AEP** — Agent Exchange Protocol.
- **CapToken** — macaroon-style authorization token (L5).
- **session_root** — `SHA3-256(ck_final)` from L3.

## Required Behavior
1. L1: 2 KB fixed-size Sphinx over q-mix QUIC; constant cover.
2. L2: capability-hashed Kademlia DHT with bucket-PIR over L1.
3. L3: Noise-PQ XK with mutual attestation; produces `session_root`.
4. L4: PQ Double Ratchet (pair) + MLS (group); intent/message key split.
5. L5: CapTokens with signed verification_seed; in-band discharges; audit receipts.

## Inputs / Outputs
- Inputs: peer DID, capability schema id, request scope.
- Outputs: per-action ALLOW / DENY; AuditReceipt instances.

## Error States
Per-layer abort codes / decisions (SPEC-006).

## Data Rules
No PII anywhere. See SPEC-002.

## Security Rules
Hybrid PQ throughout. See SECURITY.md.

## Accessibility
N/A. CLI honors `NO_COLOR=1`.

## Performance
See PROJECT_BRIEF.md budgets.

## Observability
See SPEC-007.

## Required Tests
- Five layer demos exit 0.
- Two-impl interop matrix passes for ≥ 1 scenario per layer.

## Acceptance Criteria
- `uv run python -m aethermesh.demos.layer{1..5}` exit 0.
- `./scripts/verify.sh` returns `verify: ok`.
