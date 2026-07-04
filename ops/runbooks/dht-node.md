# DHT Node Runbook

## Purpose
Operational runbook for AetherMesh L2 DHT nodes.

## Prerequisites
- Bootstrap routing table from ≥ 3 peers.
- `AEP_REVOCATION_FETCH_INTERVAL_S` ≤ 300 s.

## Startup
```sh
docker run --rm -d --name aethermesh-dht-1 \
  --env-file /etc/aethermesh/dht.env \
  -v /var/lib/aethermesh:/var/lib/aethermesh \
  ghcr.io/<org>/aethermesh-dht-node:X.Y.Z
```

## Health Check
```sh
curl http://localhost:9100/healthz
curl http://localhost:9100/metrics | grep aep_l2_dht_records_stored_total
# expected: non-zero within 10 min of startup
```

## Common Issues

### DHT eclipse suspected
- **Symptom:** All `find_node` responses converge to a small set
- **Action:** `export AEP_DHT_BOOTSTRAP_OVERRIDE=<known-good-peer>`; report to directory authority

### STORE count zero
- **Symptom:** `aep_l2_dht_records_stored_total` = 0 after 10 min
- **Action:** Verify ≥ 3 bootstrap peers are reachable; check network connectivity

### Revocation manifest stale
- **Symptom:** `aep_l5_revocation_manifest_age_seconds` > 600
- **Action:** Verify `AEP_REVOCATION_FETCH_INTERVAL_S` is set; check directory URL reachability

## Diagnostics
```sh
aethermesh node diagnose --out diagnose-report.json
```

## Escalation
Same as mix-node runbook.
