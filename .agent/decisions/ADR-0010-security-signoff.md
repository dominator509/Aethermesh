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
- [x] `liboqs` local integration validated: `AEP_PQ_BACKEND=liboqs ./scripts/verify.sh` and `uv run python -m aethermesh.tools.smoke --prod` pass on the current Windows environment.
- [x] FORBIDDEN_LOG_KEYS (18 keys) enforced at emission with CI gate.
- [x] Verifier fails closed on unknown caveat types (16 branch tests).
- [x] Audit DB file permissions restricted to 0600 on POSIX.
- [x] No secrets committed; test keys generated fresh per test.
- [x] `pip-audit` passes with zero High/Critical advisories.

### Blocking / Not Accepted for 1.0
- [ ] `tests/interop/external/` is absent, so the required two-implementation interop matrix is not available.
- [ ] `tests/perf/` now records `tests/perf/results/baseline.json`, but L1/L3/L4 still benchmark placeholder or stub-level surfaces and no reference-VM perf sign-off is recorded.
- [ ] L3/L4/L5 layers are contract stubs; real protocol bodies are required before production launch claims.
- [ ] Human security lead sign-off is still missing; ADR-0010 cannot move to Accepted without it.

### Requires Post-1.0 ADR
- [ ] Full TPM2 PCR quoting (currently subprocess-based placeholder).
- [ ] Real Apple SEP App Attest integration (currently placeholder labels).
- [ ] Rust hot paths for Sphinx hop processing (ADR-0001 deferred).

## Decision
**Proposed: Do not accept for v1.0.0 yet.** Keep ADR-0010 Proposed until the blocking items are resolved, the performance gate has real evidence, and a human security lead signs off.

## Sign-Off
- [ ] Security Lead: _______________ Date: ________
- [ ] Release Lead: _______________ Date: ________
