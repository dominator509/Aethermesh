# SPEC-007 — Observability

- **Status:** Draft  - **Owner:** Observability  - **Phase:** 7  - **ExecPlans:** EP-008

## User-Visible Goal
Operators can observe protocol health without ever seeing message content or key material.

## Non-Goals
Long-term content retention; cross-host log aggregation prescribed by library.

## Required Behavior

### Logging
Per OBSERVABILITY.md. Single `structlog` logger via `aethermesh.common.logging.logger`. Allowlist + FORBIDDEN_LOG_KEYS denylist enforced at emission.

### Metrics
Per OBSERVABILITY.md. Emitted via `aethermesh.common.metrics` wrappers. Registered in `aethermesh.common.metrics.REGISTRY`.

### Traces
OpenTelemetry; spans `l3.handshake`, `l4.message.send/recv`, `l5.verifier.verify`. Same redaction rules.

### Health
`/healthz`, `/readyz`, `/livez` on port 9100. `aethermesh node health` returns same content.

### Dashboards
`ops/dashboards/`: `l1-transport.json`, `l3-handshake.json`, `l4-session.json`, `l5-authority.json`.

### Alerts
`ops/alerts/aethermesh.rules.yml`: Prometheus rules for every alert.

## SLIs
- Handshake success rate (5 min) ≥ 99.9%.
- Token verify p99 ≤ 1 ms (5 ms ceiling).
- Revocation manifest age ≤ 2 × `AEP_REVOCATION_FETCH_INTERVAL_S`.
- Log redaction violations: 0 / 24 h.

## SLOs
SLIs above sustained 30 days.

## Error States
- Forbidden log key insertion increments `log_redaction_violation_total` and (in tests) raises.
- OTLP exporter failure logged as `event=otel.export.failed` without re-emitting payload.

## Security Rules
No body content. No key material. See FORBIDDEN_LOG_KEYS.

## Required Tests
- `tests/security/test_log_redaction.py`: end-to-end under `caplog`; assert no forbidden keys.
- `tests/integration/test_metrics_registry.py`: every metric registered.
- `tests/e2e/test_health_endpoints.py`: `/healthz` and `/readyz` reachable.

## Acceptance Criteria
- Redaction test passes.
- Metrics registry test passes.
- Health endpoints return `ok`.
