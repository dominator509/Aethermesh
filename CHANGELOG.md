# Changelog

All notable changes to AetherMesh will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Core cryptographic library (`aethermesh.common`)
- L3/L4/L5 API facade stubs (`aethermesh.api`)
- CLI with 12 subcommands (`aethermesh.cli`)
- TPM2 and Apple SEP attestation backends
- Caveat DSL with 18 caveat types and fail-closed verifier
- Keyring IPC service
- Hypothesis fuzz targets
- Structured JSON logging with FORBIDDEN_LOG_KEYS
- Metrics REGISTRY (14 metrics)
- Health endpoints on port 9100
- Grafana dashboards and Prometheus alert rules
- Role runbooks (mix-node, gateway, dht-node, keyring)
- Flaky test policy and quarantine harness
- Interop test scaffolding
- Docker images for mix-node and gateway
- Staging docker-compose environment
- CI/CD workflows (CI, release, staging)

[Unreleased]: https://github.com/dominator509/Aethermesh/tree/main
