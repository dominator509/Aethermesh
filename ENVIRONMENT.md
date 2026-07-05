# ENVIRONMENT

## Required Tools
| Tool | Min Version | Purpose |
|---|---|---|
| Python | 3.11 | Runtime |
| `uv` | 0.4 | Package manager |
| `git` | 2.30 | Source control |
| `sqlite3` | 3.35 | Local audit DB |
| `libsodium` | 1.0.18 | Used by `cryptography` |
| `liboqs` | 0.10.0 | Required for `AEP_PQ_BACKEND=liboqs` |
| `promtool` | 2.2.1 | Prometheus alert rule validation for Gate 14 |
| `docker` | 24 | Mix-node / gateway packaging (EP-009) |
| `make` | 4 | Optional convenience runner |

## Package Manager
- `uv` canonical. Lockfile `uv.lock` (never hand-edited).
- `pyproject.toml` carries PEP 621 metadata + tool config.
- Runtime PQ binding is `liboqs-python`, pinned to the upstream Git tag `0.12.0`.
- Dev extras include `pytest-benchmark` for `uv run pytest tests/perf --benchmark-only`.

## Environment Variables
| Name | Required? | Env | Example | Secret? | Description | Validation |
|---|---|---|---|---|---|---|
| `AEP_LOG_LEVEL` | optional | all | `info` | no | `debug`/`info`/`warning`/`error` | one of 4 |
| `AEP_AUDIT_DB_PATH` | optional | all | `./audit.db` | no | SQLite path for local audit | parent dir writable |
| `AEP_AUDIT_RETENTION_DAYS` | optional | all | `90` | no | Audit receipt retention window in days | integer ≥ 30 |
| `AEP_DIRECTORY_URL` | required for prod | prod | `https://directory.example.org/epoch.json` | no | Directory bootstrap | https only in prod |
| `AEP_KEYRING_SOCKET` | required for end-agent | dev/prod | `/run/aethermesh/keyring.sock` | no | Unix socket to keyring | path is a socket |
| `AEP_PQ_BACKEND` | required | all | `liboqs` | no | `placeholder` (dev only) or `liboqs` (prod) | prod refuses `placeholder` |
| `AEP_DEFAULT_LANE` | optional | all | `fast` | no | `fast` / `slow` / `slow+` | one of 3 |
| `AEP_OTEL_ENDPOINT` | optional | prod | `http://otel-collector:4317` | no | OTLP gRPC | URL format |
| `AEP_NODE_ROLE` | required for mix-node | prod | `mix-layer-1` | no | Role label | regex `^(mix-layer-[123]|gateway-(entry|exit)|dht-node)$` |
| `AEP_NODE_ID_HEX` | required for mix-node | prod | `4a3f...` | no | 32 hex chars | exactly 32 hex |
| `AEP_REVOCATION_FETCH_INTERVAL_S` | optional | prod | `300` | no | Manifest poll interval | int ≥ 60 |
| `AEP_COVER_RATE_PPS_ACTIVE` | optional | all | `5` | no | Active cover rate | 1–10 |
| `AEP_COVER_RATE_PPS_IDLE` | optional | all | `1` | no | Idle cover rate | 0.5–5 |

Any new variable must be added here first.

## Secrets
Library ships no secrets. Operators provide:
- Mix-node X25519 SK (`AEP_NODE_SK_PATH`).
- Mix-node ML-KEM-768 SK (`AEP_NODE_PQ_SK_PATH`).
- Keyring principal + discharger hybrid SKs (TEE-held; never read by protocol code).

## Local Development Setup
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone <repo>
cd aethermesh
uv sync --all-extras --dev
./scripts/preflight.sh
uv run python -m aethermesh.demos.layer1
```

## Local Database Setup
```sh
uv run python -m aethermesh.tools.init_audit_db --path ./audit.db
```

## Test Environment Setup
```sh
./scripts/test-unit.sh
AEP_AUDIT_DB_PATH=$(mktemp) uv run pytest tests/integration -q
```

## Staging Environment Setup
- 3 mix nodes, 1 entry gateway, 1 exit gateway, 1 DHT node, 1 keyring stub (SoftSign).
- `AEP_PQ_BACKEND=liboqs`.

## Production Environment Setup
- ≥ 30 mix nodes across ≥ 3 operators per layer.
- Gateways operated by ≥ 3 vendors. DHT nodes by ≥ 5 operators.
- Keyrings use platform TEEs only.
- `AEP_PQ_BACKEND=liboqs` enforced.

## Configuration Validation
`aethermesh.common.config.load()` validates each variable at process start; failure prints offender and exits non-zero.

## Environment Parity Rules
- Same code path / library version / primitives across dev/staging/prod.
- Only attestation backends and cover-rate params may differ.

## Troubleshooting
| Symptom | Fix |
|---|---|
| `ImportError: oqs` | Install `liboqs`; or `AEP_PQ_BACKEND=placeholder` (dev only). |
| `pytest: error: unrecognized arguments: --benchmark-only` | `uv sync --all-extras --dev` to install `pytest-benchmark`. |
| `production readiness: FAIL — promtool not installed` | Install Prometheus or add `promtool` to `PATH`; verify with `promtool check rules ops/alerts/aethermesh.rules.yml`. |
| `Permission denied: /run/aethermesh/keyring.sock` | Run keyring or use `AEP_KEYRING_SOCKET=/tmp/aethermesh-test.sock` (dev). |
| Mix node refuses to start in prod | Check `AEP_PQ_BACKEND`; placeholder rejected. |
| Audit DB locked | Two writers; serialize via systemd. |
| Constant cover overloads test bandwidth | Set `AEP_COVER_RATE_PPS_ACTIVE=1` (dev only). |
