# OBSERVABILITY

## Logging Strategy
- Library: `structlog` JSON to stderr.
- Container: same JSON to stdout.
- Default level `info`; `debug` only for ExecPlan validation.

## Structured Log Fields
| Field | Type | Example |
|---|---|---|
| `ts` | RFC 3339 | `2026-06-18T15:21:33Z` |
| `level` | enum | `info` |
| `event` | string | `l4.policy.decision` |
| `layer` | enum | `L1`..`L5` |
| `session_root_hash` | 16-hex | `8abeed89e7533431` |
| `Ns` | uint | `42` |
| `msg_index` | uint | `42` |
| `capability_id` | URN | `doc.review.v1` |
| `policy_decision` | enum | `ALLOW`, `DENY_SCOPE` |
| `abort_code` | enum | `0x30` |
| `peer_attest_class` | enum | `TDX`, `SoftSign` |
| `lane` | enum | `fast`/`slow`/`slow+` |
| `node_id_prefix` | 8-hex | `4a3f12bc` |

## Forbidden Log Fields
```
FORBIDDEN_LOG_KEYS = {
  "intent_key", "message_key",
  "principal_sk", "discharger_sk", "instance_sk", "static_sk",
  "x25519_sk", "mlkem_sk", "mldsa_sk",
  "body", "body_pt", "plaintext",
  "root_key", "ck", "ck_final",
  "session_root",          # log session_root_hash
  "root_macaroon_key",
  "discharge_predicate",   # log predicate.kind only
}
```
CI gate: `tests/security/test_log_redaction.py` asserts none appear.

## Redaction Rules
- `session_root` → `session_root_hash` = first 16 hex of `SHA3-256(session_root)`.
- `discharge_predicate` → `predicate.kind` only.
- Free-form strings truncated to 256 chars; control chars escaped.

## Metrics
| Metric | Type | Labels | Description |
|---|---|---|---|
| `aep_l1_packets_total` | counter | `type`, `lane` | Sphinx packets emitted |
| `aep_l1_lane_latency_seconds` | histogram | `lane` | End-to-end latency |
| `aep_l1_sphinx_replay_rejections_total` | counter | `node_role` | Replay cache hits |
| `aep_l2_dht_records_stored_total` | gauge | `node_role` | Current STORE count |
| `aep_l2_dht_lookups_total` | counter | `result` | Lookup outcomes |
| `aep_l3_handshake_duration_seconds` | histogram | `result` | 3-msg handshake |
| `aep_l3_attestation_verifications_total` | counter | `backend`, `result` | Per-backend |
| `aep_l4_messages_total` | counter | `kind` | Frames processed |
| `aep_l4_policy_decisions_total` | counter | `decision` | One per IntentHeader |
| `aep_l4_ratchet_dh_steps_total` | counter | | DH ratchet steps |
| `aep_l5_token_verify_duration_seconds` | histogram | | Per-token verification |
| `aep_l5_discharge_issuances_total` | counter | `user_consent` | Keyring discharges |
| `aep_l5_revocation_manifest_age_seconds` | gauge | `issuer_did_hash` | Manifest age |
| `log_redaction_violation_total` | counter | | Forbidden-key insertions |

## Traces
Spans `l3.handshake`, `l4.message.send|recv`, `l5.verifier.verify`. No body or key in attributes — same redaction rules.

## Health Checks
| Endpoint | Port | Returns |
|---|---|---|
| `/healthz` | 9100 | `ok` when up |
| `/readyz` | 9100 | `ok` when directory loaded + keys present |
| `/livez` | 9100 | `ok` until liveness fails |

## Uptime Checks
External operator probes `/healthz` every 30 s. Library exposes no remote uptime endpoint.

## Dashboards
`ops/dashboards/`: `l1-transport.json`, `l3-handshake.json`, `l4-session.json`, `l5-authority.json`.

## Alerts
| Alert | Condition | Severity |
|---|---|---|
| `HandshakeFailureRate` | `aborted/total > 0.05` over 5 min | SEV-2 |
| `ReplayFlood` | `rate(replay_rejections[1m]) > 100` | SEV-2 |
| `RevocationStale` | manifest age > 2 × interval | SEV-3 |
| `LogRedactionViolation` | rate > 0 over 5 min | SEV-1 |
| `TokenVerifyP99High` | p99 verify > 5 ms | SEV-3 |
| `PolicyDenyRateSpike` | denial rate doubles vs 1 h baseline | SEV-3 |

## Service-Level Indicators
| SLI | Target |
|---|---|
| Handshake success rate (5 min) | ≥ 99.9% |
| Token verify p99 | ≤ 1 ms (5 ms ceiling) |
| Revocation manifest age | ≤ 2 × `AEP_REVOCATION_FETCH_INTERVAL_S` |
| Log redaction violations | 0 / 24 h |

## Service-Level Objectives
SLIs above sustained 30 days. Burn-rate alerts: 2% / 5% split.

## Debugging Production Issues
1. Identify alert + layer.
2. Capture `diagnose-report.json`.
3. Pull recent logs filtered by `session_root_hash`.
4. Cross-reference dashboards.
5. Open relevant runbook.

## Observability Acceptance Criteria
- New metrics declared in `aethermesh.common.metrics.REGISTRY`.
- New log events use only allowlisted fields (or add via ADR).
- CI redaction test still passes.
- Dashboards include any new operator-visible metric.
