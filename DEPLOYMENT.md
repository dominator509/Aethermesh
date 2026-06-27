# DEPLOYMENT

## Deployment Environments
| Env | Purpose | Hosting | AEP_PQ_BACKEND | Attestation |
|---|---|---|---|---|
| dev | Local laptop | direct Python | `placeholder` allowed | `SoftSign` |
| staging | Pre-prod soak | docker-compose | `liboqs` | `SoftSign` + TPM2 if available |
| prod | Live mesh | per-operator infra | `liboqs` (enforced) | TEE-only |

## Deployment Architecture
```
GitHub release --PyPI--> aethermesh wheel
                |
                +--GHCR--> aethermesh-mix-node, aethermesh-gateway images
                                |
                                +--docker pull--> operator infra
```

## Build Artifact
- Library: `aethermesh-X.Y.Z-py3-none-any.whl` + `.tar.gz` on PyPI.
- Mix node: `ghcr.io/<org>/aethermesh-mix-node:X.Y.Z` (multi-arch).
- Gateway: `ghcr.io/<org>/aethermesh-gateway:X.Y.Z` (multi-arch).
- CLI in wheel; `aethermesh` console script.

## Release Flow
1. Merge to `main`; CI green.
2. Tag `vX.Y.Z` (or `vX.Y.Z-rc.N`).
3. GHA: `./scripts/verify.sh` → `uv build` → sign wheel → publish PyPI (or TestPyPI for `-rc.N`) → build + push Docker images.
4. Staging operators pull new image; smoke runs.
5. Production operators promote after 72 h burn-in.

## Deployment Steps (Mix Node, staging)
```sh
docker pull ghcr.io/<org>/aethermesh-mix-node:X.Y.Z
# /etc/aethermesh/mix.env:
AEP_NODE_ROLE=mix-layer-1
AEP_NODE_ID_HEX=<32 hex chars>
AEP_NODE_SK_PATH=/run/secrets/node_sk
AEP_NODE_PQ_SK_PATH=/run/secrets/node_pq_sk
AEP_PQ_BACKEND=liboqs
AEP_OTEL_ENDPOINT=http://otel-collector:4317

docker run --rm -d --name aethermesh-mix-1 \
  --env-file /etc/aethermesh/mix.env \
  -v /var/lib/aethermesh:/var/lib/aethermesh \
  -p 4040:4040/udp \
  ghcr.io/<org>/aethermesh-mix-node:X.Y.Z
```

## Deployment Steps (Gateway)
Same image, `AEP_NODE_ROLE=gateway-entry` or `gateway-exit`.

## Migration Steps
```sh
docker exec aethermesh-mix-1 \
  python -m aethermesh.tools.audit_db migrate --path /var/lib/aethermesh/audit.db
```
Idempotent; backward migrations exist for last two versions.

## Rollback Steps
See ROLLBACK.md.

## Post-Deploy Smoke Tests
```sh
docker exec aethermesh-mix-1 \
  python -m aethermesh.tools.smoke --target self --lane fast --timeout 5
# expected: smoke test: ok
curl -sf http://localhost:9100/metrics | grep -q aep_l1_packets_total
```

## Required Approvals
- Library release: 2 reviewers, ≥1 `protocol-owner`.
- Mix-node / gateway release: 1 reviewer.
- Protocol-affecting change: 2 reviewers + ADR.

## Deployment STOP Conditions
Pipeline refuses to publish if:
- `AEP_PQ_BACKEND=placeholder` in prod env file.
- Attestation roots in `aethermesh/L3_handshake/attestation/roots/` changed without ADR.
- `pip-audit` reports unmitigated High / Critical advisory.
- `./scripts/production-readiness-check.sh` did not pass in the release commit.
- `RELEASE_NOTES.md` missing or empty.

## Production Verification (within 60 min)
1. `aep_l3_handshake_duration_seconds{result="success"}` p95 ≤ 550 ms.
2. `aep_l4_policy_decisions_total{decision="ALLOW"}` rate matches previous release ±5%.
3. Zero `aep_l5_token_verify_duration_seconds` > 5 ms.
4. `aep_l5_revocation_manifest_age_seconds` < `AEP_REVOCATION_FETCH_INTERVAL_S * 2`.
