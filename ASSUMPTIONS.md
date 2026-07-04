# ASSUMPTIONS

Each row carries a verification step. If verification fails, do not implement around it — update the relevant ExecPlan Decision Log and this file.

| # | Assumption | Reason | Risk if Wrong | How to Verify | Blocks Impl? |
|---|---|---|---|---|---|
| A1 | Python 3.11+ on host. **Verified 2026-07-03: python=3.14.4 (Windows, `python` not `python3`), uv=0.11.25.** | Reference uses 3.11 syntax / `tomllib` | Build fails | `python3 --version` ≥ 3.11 | Yes (EP-001) |
| A2 | `uv` is the package manager. **Verified 2026-07-03: uv=0.11.25.** | Fast, lockfile-native | Scripts fail | `command -v uv` | Yes |
| A3 | `liboqs` available via `oqs` Python | Required to swap PQ placeholders for prod | Cannot reach production readiness | `uv add oqs && python -c "import oqs"` | Blocks EP-010 |
| A4 | QUIC stack (`aioquic` or `quiche`) available | L1 needs RFC 9221 DATAGRAM | L1 stays in-process simulation | `uv add aioquic` + DATAGRAM check | Blocks EP-009 |
| A5 | MLS library with extension hooks available | L4 group mode needs AEP extensions | Group mode remains a sketch | Confirm `LeafNode` + `GroupContext` extension APIs | Blocks group-mode features in EP-004 |
| A6 | SQLite ≥ 3.35 | Local audit, DID cache, revocation cache | Persistence layer fails | `sqlite3 --version` ≥ 3.35 | Yes (EP-003) |
| A7 | GitHub Actions for CI. **Verified 2026-07-03: no `.github/workflows/` present; repo lives on GitHub (github.com/Dominator509/Aethermesh).** | OSS conventions | `.github/workflows/` wasted if elsewhere | Repo lives on GitHub | Yes (EP-009) |
| A8 | Docker available for mix-node packaging | Standard for self-hosted | Mix-node ops doc unusable | `docker --version` | Blocks EP-009 |
| A9 | TEE optional in dev, required in prod | Reference impl supports SoftSign fallback | Cannot verify real attestation in dev | `python -m aethermesh.L3.attestation.discover` | Blocks EP-010 |
| A10 | Hybrid PQ mandatory; PQ-only forbidden | Defense in depth | Catastrophic if a primitive falls | Code review every KEM/sig call | Yes — protocol invariant |
| A11 | No telemetry leaves library / mix-node code | Vendor neutrality + privacy | Trust loss | Grep for `requests.post`, `httpx.post`, `urllib` to non-localhost; CI enforces | Yes (EP-007) |
| A12 | **REFUTED 2026-07-03: no `bundles/`, `aethermesh/`, `pyproject.toml`, or `tests/` exist on disk. Repo is blueprint-only (88 tracked files, all agent/docs/scripts). Bundles/code to be created starting EP-001.** | ~~They were demoed end-to-end~~ | ~~Re-implementing wastes time~~ A12 assumption was premature; repo starts from this blueprint. | Each `python -m code` succeeds at HEAD — currently N/A | Yes (EP-000) |
| A13 | All identifiers de-identified (`did:web:example.org`, `agent-a`) | Avoid leaking real-world context | Identifiability risk | CI grep for known real DIDs / hostnames | Yes (EP-007) |
| A14 | Prod requires `AEP_PQ_BACKEND=liboqs`; `placeholder` rejected | Placeholder is demo aid only | Catastrophic if placeholder runs in prod | Runtime config check | Blocks EP-010 |
| A15 | Constant-rate cover (~80 kbit/s active) acceptable to operators | Required for metadata privacy | Operators refuse the load | Survey ≥ 3 operators; document in DECISIONS.md | Blocks EP-009 |
