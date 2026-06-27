# EP-008 — Observability and Operations

- **Status:** Draft  - **Owner:** Observability  - **Phase:** 7  - **Specs:** SPEC-007

## 1. Purpose / Big Picture
Wire `structlog` + OpenTelemetry. Implement FORBIDDEN_LOG_KEYS rejection at emission. Add health endpoints, metrics REGISTRY, dashboards-as-code, alert rules, and per-role runbooks.

## 2. Scope
- `aethermesh/common/{logging,metrics,tracing}.py`
- `aethermesh/tools/health.py` (HTTP on 9100)
- `ops/dashboards/{l1-transport,l3-handshake,l4-session,l5-authority}.json`
- `ops/alerts/aethermesh.rules.yml`
- `ops/runbooks/{mix-node,gateway,dht-node,keyring}.md`
- `tests/security/test_log_redaction.py`

## 3. Non-Goals
- No external dashboards hosted by library.
- No cross-host log aggregation.

## 4. Context and Orientation
EP-002 produced `aethermesh.common`. This plan adds the logging + metrics scaffolding the rest of the codebase uses.

## 5. Files to Read First
1. `SPEC-007-observability.md`  2. `OBSERVABILITY.md`  3. `SECURITY.md` § Logging Redaction Rules  4. `OPERATIONS.md`

## 6. Files to Change
- `aethermesh/common/{logging,metrics,tracing}.py`
- `aethermesh/tools/health.py`
- `ops/dashboards/*.json`, `ops/alerts/aethermesh.rules.yml`, `ops/runbooks/*.md`
- `tests/security/test_log_redaction.py`
- `tests/integration/test_metrics_registry.py`
- `tests/e2e/test_health_endpoints.py`

## 7. Interfaces and Contracts
Per SPEC-007 + OBSERVABILITY.md.

## 8. Milestones

### M1 — Logging + FORBIDDEN_LOG_KEYS
- **Goal:** `aethermesh.common.logging.logger` rejects forbidden keys.
- **Files to Read:** OBSERVABILITY.md FORBIDDEN_LOG_KEYS.
- **Files to Change:** `aethermesh/common/logging.py`, `tests/security/test_log_redaction.py`.
- **Exact Edits Expected:** `structlog` configured with JSON renderer + custom processor rejecting forbidden keys (raises in tests, increments `log_redaction_violation_total` in prod). Test runs an end-to-end flow with all 5 layers and asserts none of the forbidden keys appear in `caplog`.
- **Validation Command:** `uv run pytest tests/security/test_log_redaction.py -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

### M2 — Metrics REGISTRY
- **Goal:** Every SPEC-007 metric declared.
- **Files to Read:** OBSERVABILITY.md Metrics section.
- **Files to Change:** `aethermesh/common/metrics.py`, `tests/integration/test_metrics_registry.py`.
- **Exact Edits Expected:** `REGISTRY = {...}` lists every metric (name, type, labels) per OBSERVABILITY.md. `counter(name, labels)` and `histogram(name, labels)` wrappers using OpenTelemetry or Prometheus client.
- **Validation Command:** `uv run pytest tests/integration/test_metrics_registry.py -q`
- **Expected Result:** exit 0; every metric in OBSERVABILITY.md registered.
- **Recovery:** Per AGENTS § 7.

### M3 — Tracing
- **Goal:** OTel spans `l3.handshake`, `l4.message.send/recv`, `l5.verifier.verify`.
- **Files to Change:** `aethermesh/common/tracing.py`.
- **Exact Edits Expected:** Lazy OTel exporter setup based on `AEP_OTEL_ENDPOINT`. Same redaction rules as logging.
- **Validation Command:** `uv run python -c "from aethermesh.common.tracing import tracer; print('tracing ok')"`
- **Expected Result:** prints `tracing ok`.
- **Recovery:** Per AGENTS § 7.

### M4 — Health endpoints
- **Goal:** `/healthz`, `/readyz`, `/livez`, `/metrics` on port 9100.
- **Files to Read:** SPEC-007 Health.
- **Files to Change:** `aethermesh/tools/health.py`, `tests/e2e/test_health_endpoints.py`.
- **Exact Edits Expected:** stdlib `http.server`. `/healthz` returns `ok` after 5s startup. `/readyz` checks directory loaded + keys present. `/metrics` returns Prometheus exposition.
- **Validation Command:** `uv run pytest tests/e2e/test_health_endpoints.py -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

### M5 — Dashboards
- **Goal:** 4 Grafana JSON files.
- **Files to Change:** `ops/dashboards/{l1-transport,l3-handshake,l4-session,l5-authority}.json`.
- **Exact Edits Expected:** Minimal valid Grafana panel JSON with panels for each metric category.
- **Validation Command:** `for d in ops/dashboards/*.json; do python -m json.tool < "$d" > /dev/null && echo "$d ok" || exit 1; done`
- **Expected Result:** each prints `ok`.
- **Recovery:** Per AGENTS § 7.

### M6 — Alert rules
- **Goal:** Prometheus rules for every alert in OBSERVABILITY.md.
- **Files to Change:** `ops/alerts/aethermesh.rules.yml`.
- **Exact Edits Expected:** YAML with one rule per alert (HandshakeFailureRate, ReplayFlood, RevocationStale, LogRedactionViolation, TokenVerifyP99High, PolicyDenyRateSpike).
- **Validation Command:** `python -c "import yaml; yaml.safe_load(open('ops/alerts/aethermesh.rules.yml')); print('rules ok')"`
- **Expected Result:** prints `rules ok`.
- **Recovery:** Per AGENTS § 7.

### M7 — Runbooks
- **Goal:** 4 role runbooks.
- **Files to Read:** OPERATIONS.md runbooks.
- **Files to Change:** `ops/runbooks/{mix-node,gateway,dht-node,keyring}.md`.
- **Exact Edits Expected:** Each follows `.agent/templates/runbook-template.md` and mirrors OPERATIONS.md content.
- **Validation Command:** `for f in ops/runbooks/*.md; do [ -s "$f" ] || exit 1; done; echo "runbooks ok"`
- **Expected Result:** prints `runbooks ok`.
- **Recovery:** Per AGENTS § 7.

## 9. Concrete Steps
M1 -> M7.

## 10. Validation and Acceptance
### Acceptance Criteria
- [ ] `tests/security/test_log_redaction.py` passes.
- [ ] Every SPEC-007 metric registered.
- [ ] Health endpoints return `ok` after startup.
- [ ] Dashboards parse as Grafana JSON.
- [ ] Alert rules parse as Prometheus YAML.
- [ ] All 4 runbooks exist and non-empty.
- [ ] `./scripts/verify.sh` exits 0.

## 11. Idempotence and Recovery
JSON/YAML files single-source. Re-running tests safe.

## 12. Progress
- [ ] M1 — Logging + FORBIDDEN_LOG_KEYS
- [ ] M2 — Metrics REGISTRY
- [ ] M3 — Tracing
- [ ] M4 — Health endpoints
- [ ] M5 — Dashboards
- [ ] M6 — Alert rules
- [ ] M7 — Runbooks
- [ ] Final review

## 13. Surprises & Discoveries
<filled>

## 14. Decision Log
<entries>

## 15. Outcomes & Retrospective
<Filled at completion.>
- **What landed:**
- **What changed vs plan:**
- **Remaining risks:**
- **Production-readiness impact:** Phase 7 exits.
