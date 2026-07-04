# Keyring Service Runbook

## Purpose
Operational runbook for AetherMesh keyring service.

## Prerequisites
- Runs only inside platform TEE (SEP / StrongBox / TPM2).
- Refuses to serve if `AEP_PQ_BACKEND=placeholder`.
- Unix socket at `$AEP_KEYRING_SOCKET`.

## Startup
```sh
AEP_PQ_BACKEND=liboqs \
AEP_KEYRING_SOCKET=/run/aethermesh/keyring.sock \
  aethermesh keyring serve --socket /run/aethermesh/keyring.sock
```

## Health Check
The keyring does not expose HTTP. Health is confirmed by:
```sh
curl http://localhost:9100/readyz
# expects "ok" when keyring socket is present and accessible
```

## Common Issues

### Permission denied on socket
- **Symptom:** `Permission denied: /run/aethermesh/keyring.sock`
- **Action:** Verify socket directory permissions; use `AEP_KEYRING_SOCKET=/tmp/aethermesh-test.sock` for dev

### AEP_PQ_BACKEND=placeholder rejected
- **Symptom:** Keyring refuses to start
- **Action:** Install `liboqs` and set `AEP_PQ_BACKEND=liboqs`

### Audit DB user-owned
- Audit log is user-owned; never read by operator tooling without explicit permission per AGENTS.md § 13.

## Security Notes
- No private keys ever appear in logs.
- Discharge issuance logged as `aep_l5_discharge_issuances_total` with `user_consent` label only.
- Rotation of principal/discharger keys requires AGENTS.md STOP acknowledgment.

## Diagnostics
```sh
aethermesh node diagnose --out diagnose-report.json
```

## Escalation
Same as mix-node runbook.
