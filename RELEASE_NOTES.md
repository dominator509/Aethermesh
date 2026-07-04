## v0.1.0.dev0 — Unreleased

### Added
- `aethermesh.common`: cryptographic primitives (SHA3-256, HKDF, AEAD, X25519, PQ-KEM/DSA), canonical encoding, DID resolver, error taxonomies (EP-002).
- L3 handshake stubs: HandshakeInitiator, HandshakeResponder, SessionState (EP-004).
- L4 session stubs: PairRatchet, PolicyLayer, MlsGroup, IntentHeader (EP-004).
- L5 authority stubs: CapToken, Caveat, CapTokenVerifier, Discharge, KeyringService, AuditLog (EP-004).
- `aethermesh.api` facade: unified import point for all public symbols (EP-004).
- `aethermesh.cli`: console script with demo, node, keyring, audit, tools subcommands (EP-005).
- L3 attestation backends: TPM2 and Apple SEP with skip-safe placeholder fallbacks (EP-006).
- Caveat DSL: 18 caveat types with EvaluationContext and fail-closed verifier (EP-006).
- Keyring IPC: Unix socket service with discharge/mint request dispatch (EP-006).
- Hypothesis fuzz targets: Sphinx packet parser, caveat DSL verifier (EP-007).
- Flaky test policy: `.github/FLAKY_POLICY.md` with 14-day quarantine window (EP-007).
- Structured JSON logging with FORBIDDEN_LOG_KEYS enforcement (18 forbidden keys) (EP-008).
- Metrics REGISTRY: 14 counters/gauges/histograms per OBSERVABILITY.md (EP-008).
- Health endpoints: `/healthz`, `/readyz`, `/livez`, `/metrics` on port 9100 (EP-008).
- Grafana dashboards: L1 transport, L3 handshake, L4 session, L5 authority (EP-008).
- Prometheus alert rules: 6 alerts per OBSERVABILITY.md (EP-008).
- Role runbooks: mix-node, gateway, dht-node, keyring (EP-008).

### Changed
- EP-001: Foundation established with `pyproject.toml`, package stubs, CI baseline.
- EP-003: SQLite persistence layer with migrations, backup, retention pruning.

### Security
- Hybrid PQ mandatory at every KEM/sig path (placeholder + liboqs dispatch).
- Log redaction enforced at emission (raises in strict/test mode, drops + increments counter in prod).
- Verifier fails closed on unknown caveat types.
- Audit DB file permissions restricted to 0600 on POSIX.

### Known Limitations
- All L3/L4/L5 implementations are contract stubs; real protocol bodies land in future releases.
- TPM2 attestation backend calls `tpm2_pcrread` subprocess but does not do full PCR quoting.
- Apple SEP backend uses placeholder labels, not real App Attest APIs.
- Keyring IPC uses length-prefixed JSON (CBOR pending dependency approval).
- Unix domain sockets not available on Windows — keyring tests skip on win32.
