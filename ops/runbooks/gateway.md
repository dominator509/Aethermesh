# Gateway Runbook

## Purpose
Operational runbook for AetherMesh entry/exit gateways.

## Prerequisites
- Same as mix-node, with `AEP_NODE_ROLE=gateway-entry` or `gateway-exit`.
- Public UDP port reachable.
- Local PQ KEM keypair rotated per epoch (3600 s).

## Startup
```sh
docker run --rm -d --name aethermesh-gateway-1 \
  --env-file /etc/aethermesh/gateway.env \
  -v /var/lib/aethermesh:/var/lib/aethermesh \
  -p 4040:4040/udp \
  ghcr.io/<org>/aethermesh-gateway:X.Y.Z
```

## Health Check
```sh
curl http://localhost:9100/healthz
curl http://localhost:9100/metrics | grep aep_l1_packets_total
```

## Key Rotation
```sh
# Every epoch (3600 s):
docker exec aethermesh-gateway-1 \
  python -m aethermesh.tools.gen_node_keys --rotate
```

## Common Issues

### Public UDP unreachable
- Confirm firewall allows port 4040/udp.
- Verify with external probe: `nc -u <gateway-ip> 4040 < /dev/null`

### PQ KEM rotation missed
- **Symptom:** `aep_l3_handshake_duration_seconds{result="aborted"}` rising
- **Action:** Force rotation via `aethermesh node refresh-directory`

## Diagnostics
```sh
aethermesh node diagnose --out diagnose-report.json
```

## Escalation
Same as mix-node runbook.
