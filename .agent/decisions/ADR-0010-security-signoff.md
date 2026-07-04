# ADR-0010 — Security Review Sign-Off

- **Status:** Proposed
- **Date:** 2026-07-04
- **Owner:** Security
- **Specs:** SPEC-008 § Gate 16

## Context
AetherMesh / AEP 1.0 requires a security review sign-off before the v1.0.0 tag can be pushed. This ADR documents the review scope, findings, and sign-off decision.

## Review Scope
- Cryptographic primitive selection and usage (hybrid PQ mandatory).
- FORBIDDEN_LOG_KEYS enforcement at log/trace emission.
- Caveat DSL fail-closed evaluation (unknown caveat → DENY).
- Attestation backend architecture (TPM2, Apple SEP, SoftSign).
- CapToken chain integrity (verify_root + verify_chain).
- Audit log redaction (body_hash only, no PII, no keys).
- Dependency audit (pip-audit passes, no High/Critical advisories).
- Input validation patterns across all public APIs.

## Findings

### Resolved
- [x] Hybrid PQ enforced at every KEM/sig path (ADR-0002).
- [x] FORBIDDEN_LOG_KEYS (18 keys) enforced at emission with CI gate.
- [x] Verifier fails closed on unknown caveat types (16 branch tests).
- [x] Audit DB file permissions restricted to 0600 on POSIX.
- [x] No secrets committed; test keys generated fresh per test.
- [x] `pip-audit` passes with zero High/Critical advisories.

### Blocking / Not Accepted for 1.0
- [ ] liboqs Python binding not integrated; EP-010 M1 is stopped until the operator installs the system `liboqs` library and matching Python binding.
- [ ] L3/L4/L5 layers are contract stubs; real protocol bodies are required before production launch claims.
- [ ] No external implementation for interop testing; the two-implementation matrix must be populated before sign-off.

### Requires Post-1.0 ADR
- [ ] Full TPM2 PCR quoting (currently subprocess-based placeholder).
- [ ] Real Apple SEP App Attest integration (currently placeholder labels).
- [ ] Rust hot paths for Sphinx hop processing (ADR-0001 deferred).

## Decision
**Proposed: Do not accept for v1.0.0 yet.** Keep ADR-0010 Proposed until the blocking items are resolved and a human security lead signs off.

## Sign-Off
- [ ] Security Lead: _______________ Date: ________
- [ ] Release Lead: _______________ Date: ________
