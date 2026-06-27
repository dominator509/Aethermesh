# ROLLBACK

## Rollback Triggers
Any one is enough.
- Interop matrix break detected post-release.
- New CVE in a runtime dep that the released code path uses.
- A platform attestation root revoked upstream.
- Performance regression > 20% on p95 of any SLI in first 72 h.
- Log redaction violation observed in production (SEV-1).
- Mix node refuses to start in prod due to `AEP_PQ_BACKEND` regression.

## Rollback Decision Owner
Release lead. Fallback: security lead, then on-call.

## Rollback Types
| Type | Path |
|---|---|
| Library | PyPI yank + pin in operator env files |
| Image | GHCR revert + redeploy previous tag |
| Config | Revert `directory.json` to previous epoch authority |
| Feature flag | Toggle `AEP_DEFAULT_LANE` or `AEP_REVOCATION_FETCH_INTERVAL_S` |
| Database | Backward migration via `aethermesh.tools.audit_db` |

## Application Rollback (Library)
1. Release lead declares rollback.
2. `uv publish --yank` on PyPI for `vX.Y.Z`.
3. Notify operators; pin `aethermesh==X.Y.(Z-1)`.
4. Confirm operators rolled back (image redeploy below).

## Application Rollback (Image)
```sh
docker stop aethermesh-mix-1
docker pull ghcr.io/<org>/aethermesh-mix-node:X.Y.(Z-1)
docker run --rm -d --name aethermesh-mix-1 \
  --env-file /etc/aethermesh/mix.env \
  -v /var/lib/aethermesh:/var/lib/aethermesh \
  -p 4040:4040/udp \
  ghcr.io/<org>/aethermesh-mix-node:X.Y.(Z-1)
```

## Database Rollback
```sh
docker exec aethermesh-mix-1 \
  python -m aethermesh.tools.audit_db migrate --to X --path /var/lib/aethermesh/audit.db
```
Backward migrations exist for last two `SCHEMA_VERSION`s. Older → restore from backup.

## Config Rollback
```sh
cp /etc/aethermesh/directory.previous.json /etc/aethermesh/directory.json
docker restart aethermesh-mix-1
```

## Feature Flag Rollback
Edit `/etc/aethermesh/mix.env`, e.g. `AEP_DEFAULT_LANE=slow`; `docker restart`.

## Verification After Rollback
1. `curl -sf http://localhost:9100/healthz` → `ok`.
2. `aep_l3_handshake_duration_seconds{result="success"}` rate ≥ pre-incident baseline within 10 min.
3. Zero `log_redaction_violation_total` increment over 10 min.
4. `./scripts/smoke-test.sh` returns 0.

## Communication
- **At decision:** ops channel: "Rolling back vX.Y.Z to vX.Y.(Z-1). Reason: <one line>."
- **At completion:** "Rollback complete. All affected nodes on vX.Y.(Z-1)."
- **Within 24 h:** postmortem draft circulated.

## Postmortem Template
```
# Postmortem: <incident>
## Summary
## Timeline
## Impact
## Root cause
## Trigger
## Contributing factors
## Detection
## Resolution
## What went well
## What went poorly
## Action items (owner, due date)
```
