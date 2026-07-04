# Mix Node Runbook

## Purpose
Operational runbook for AetherMesh L1 mix nodes.

## Prerequisites
- VM provisioned with `aethermesh-mix-node` container image.
- `node_sk` + `node_pq_sk` generated (see DEPLOYMENT.md).
- Node ID registered with directory authority.

## Startup
```sh
docker run --rm -d --name aethermesh-mix-1 \
  --env-file /etc/aethermesh/mix.env \
  -v /var/lib/aethermesh:/var/lib/aethermesh \
  -p 4040:4040/udp \
  ghcr.io/<org>/aethermesh-mix-node:X.Y.Z
```

## Health Check
```sh
curl http://localhost:9100/healthz
# expected: ok
curl http://localhost:9100/metrics | grep aep_l1_packets_total
# expected: rising
```

## Common Issues

### Replay cache hit rate > 1%
- **Symptom:** `aep_l1_sphinx_replay_rejections_total` rising
- **Diagnosis:** DoS replays or clock skew
- **Action:** Inspect upstream peers; run `ntpd -q` to resync

### Mix key rotation lag (> 5 min)
- **Symptom:** Stale key material in directory
- **Action:** `aethermesh node refresh-directory`

### Cover traffic stalled
- **Symptom:** `aep_l1_packets_total` flat
- **Action:** Check gateway connection + rate config (`AEP_COVER_RATE_PPS_ACTIVE`)

### Audit DB locked
- **Symptom:** `database is locked` in logs
- **Action:** Stop duplicate writer; use systemd `BindsTo` for single-writer guarantee

## Diagnostics
```sh
aethermesh node diagnose --out diagnose-report.json
```

## Escalation
| Severity | Response |
|---|---|
| SEV-1 | Page immediately: release lead + security |
| SEV-2 | Page within 15 min: on-call operator |
| SEV-3 | Page within 1 h |
| SEV-4 | Next business day |
