# DECISIONS — Architecture Decision Log

## Decision Table
| ADR | Status | Date | Owner | Title |
|---|---|---|---|---|
| ADR-0001 | Accepted | 2026-06-18 | Architecture | Python 3.11+ reference; Rust hot paths deferred |
| ADR-0002 | Accepted | 2026-06-18 | Security | Hybrid PQ only (X25519+ML-KEM-768, Ed25519+ML-DSA-65) |
| ADR-0003 | Accepted | 2026-06-18 | DX | Use `uv` as package manager |
| ADR-0004 | Accepted | 2026-06-18 | Privacy | Cover traffic at 5 pkt/s active, 1 pkt/s idle |
| ADR-0005 | Accepted | 2026-06-18 | Privacy | Bucket-PIR default 12-bit prefix |
| ADR-0006 | Accepted | 2026-06-18 | Authority | Signed `verification_seed` for CapToken public-key issuance |
| ADR-0007 | Proposed | TBD | Ops | Mix nodes ship as Docker images on GHCR |
| ADR-0008 | Proposed | TBD | Security | Prod refuses to start unless `AEP_PQ_BACKEND=liboqs` |
| ADR-0009 | Proposed | TBD | Observability | structlog JSON + OpenTelemetry; no PII; no body content |
| ADR-0010 | Proposed | TBD | Security | Security review sign-off (gates 1.0) |

## ADR Index
Each ADR follows `.agent/templates/adr-template.md`. ADR files live in `.agent/decisions/`.

## Initial ADRs

### ADR-0001 — Python 3.11+ reference; Rust hot paths deferred
- **Context:** Reference bundles are Python 3.12 in the sandbox; future Rust core for Sphinx hop processing and path selection has been discussed for throughput.
- **Decision:** Pure Python (3.11+) for 1.0. Rust hot paths post-1.0 with own ADR.
- **Alternatives:** Pure Rust with Python bindings (rejected: doubles surface area before 1.0).
- **Consequences:** L1 throughput AEAD-bound; benchmarks validate on commodity VMs.
- **Status:** Accepted.

### ADR-0002 — Hybrid PQ only
- **Context:** Defend against both classical (ECDLP) and future quantum break.
- **Decision:** Every KEM passes `dh_x || ss_pq` to HKDF; every signature is hybrid. PQ-only and classical-only forbidden.
- **Alternatives:** PQ-only after 2030 (rejected: harvest risk); classical-only (rejected: harvest now decrypt later).
- **Consequences:** ~6.5 KB handshake; resilience against either single primitive falling.
- **Status:** Accepted.

### ADR-0003 — Use `uv` as package manager
- **Context:** Faster installs, native lockfile, PEP 621 integration.
- **Decision:** `uv` mandatory; `pip install` forbidden per COMMANDS.md.
- **Alternatives:** poetry, pdm, raw pip+venv (rejected).
- **Consequences:** `uv` is a preflight prerequisite.
- **Status:** Accepted.

### ADR-0004 — Constant-rate cover at 5 pkt/s active, 1 pkt/s idle
- **Context:** Cover load is the central cost of L1 metadata privacy.
- **Decision:** Active = 5 pkt/s; idle = 1 pkt/s. Adjustments require ADR.
- **Alternatives:** 10 pkt/s (hostile to mobile); 1 pkt/s active (reveals state).
- **Consequences:** Mobile idle profile required.
- **Status:** Accepted.

### ADR-0005 — Bucket-PIR with default 12-bit prefix
- **Context:** Final-hop DHT node would otherwise learn the exact key.
- **Decision:** Default `bucket_bits = 12`; tunable [8..16] per query.
- **Alternatives:** Full PIR (too expensive); no PIR (leaks).
- **Consequences:** Last-hop traffic grows by O(bucket size); ~64 KB cap.
- **Status:** Accepted.

### ADR-0006 — Signed `verification_seed` for CapToken public-key issuance
- **Context:** Stock macaroons need shared root key; cross-vendor needs public-key issuance.
- **Decision:** `verification_seed = HKDF(salt=ctid, ikm=root_resource || schema_pins || revocation_epoch, info="aep/captoken/vseed/v1", L=32)`. Included in signed root block; used as HMAC chain starting tag.
- **Alternatives:** Per-verifier shared secrets; bearer JWTs (no attenuation).
- **Consequences:** Verifiers check issuer sig then walk chain forward. Root key never leaves the keyring.
- **Status:** Accepted.

## Rules for Adding New Decisions
1. Open `.agent/decisions/ADR-NNNN-short-title.md` from template.
2. Add a row to the Decision Table.
3. Reference the ADR in the ExecPlan Decision Log that motivated it.
4. New ADRs start **Proposed**; owner moves to **Accepted** after review.
