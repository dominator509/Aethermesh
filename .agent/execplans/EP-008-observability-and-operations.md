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
- `.agent/decisions/ADR-0011-ops-directory-for-observability-artifacts.md`
- `DECISIONS.md`
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
- [x] `tests/security/test_log_redaction.py` passes. (10 tests: strict mode raises, non-strict drops, all 18 keys tested, safe logging, tracing redaction, truncation)
- [x] Every SPEC-007 metric registered. (14 metrics matching OBSERVABILITY.md)
- [x] Health endpoints return `ok`. (6 E2E tests: healthz/readyz/livez/metrics/404)
- [x] Dashboards parse as Grafana JSON. (4 dashboard files, all valid JSON)
- [x] Alert rules parse as Prometheus YAML. (rules ok)
- [x] All 4 runbooks exist and non-empty. (mix-node, gateway, dht-node, keyring)
- [x] `./scripts/verify.sh` exits 0. (lint→format→typecheck→unit(299)→integration(17)→e2e(36)→security(11)→build→audit→smoke: all ok)

## 11. Idempotence and Recovery
JSON/YAML files single-source. Tests re-running safe. Metrics REGISTRY loaded at import time.

## 12. Progress
- [x] M1 — Logging + FORBIDDEN_LOG_KEYS (structlog-style JSON logger, 18 forbidden keys enforced at emission, 10 redaction/tracing tests)
- [x] M2 — Metrics REGISTRY (14 counters/gauges/histograms per OBSERVABILITY.md, thread-safe, 9 integration tests)
- [x] M3 — Tracing (OTel stub tracer with span management, lazy endpoint config)
- [x] M4 — Health endpoints (/healthz, /readyz, /livez, /metrics on port 9100, stdlib http.server, 6 E2E tests)
- [x] M5 — Dashboards (4 Grafana JSON files: L1 transport, L3 handshake, L4 session, L5 authority)
- [x] M6 — Alert rules (6 Prometheus rules: HandshakeFailureRate, ReplayFlood, RevocationStale, LogRedactionViolation, TokenVerifyP99High, PolicyDenyRateSpike)
- [x] M7 — Runbooks (4 role runbooks: mix-node, gateway, dht-node, keyring)
- [x] Final review

## 13. Surprises & Discoveries
1. **No structlog dependency**: Implemented custom JSON logger with identical API shape. Avoids adding a new dependency per AGENTS.md § 8.
2. **Module-level int import snapshot**: `_redaction_violation_count` imported by the test captured the int value at import time. Fixed by importing the module (`import aethermesh.common.logging as logmod`) and accessing via `logmod._redaction_violation_count`.
3. **E741 variable naming**: ruff flags single-letter variable `l` (ambiguous with `1`). Renamed to `log` across all redaction tests.
4. **Health server for E2E tests**: Used a separate thread with non-default port (19100). Tests verify healthz during grace period (503) and after startup (200).
5. **Codex audit backfill**: Additional unit tests for CLI modules and tools appeared during EP-008 execution (test_cli_units.py, test_keyring_serve.py, test_tool_entrypoints.py) — these were added by the Codex audit of EP-007 and are now passing. Unit test count went from 248 to 299.
6. **Codex audit found two redaction gaps**: Logging violations incremented a local int but not the metrics registry, and tracing accepted forbidden attributes. Both now increment `log_redaction_violation_total`; tracing raises on forbidden attributes.
7. **`ops/` is a new top-level directory**: AGENTS.md requires an ADR for new top-level directories, so ADR-0011 records the EP-008 `ops/` layout.

## 14. Decision Log
| # | Context | Decision | Alternatives | Consequences |
|---|---|---|---|---|
| D1 | No structlog in dependencies | Implement custom JSON logger matching structlog API | Add structlog dep — rejected: AGENTS.md § 8 requires Decision Log + pyproject.toml evidence | 130-line custom logger; no new dependency |
| D2 | No OpenTelemetry SDK in dependencies | Implement stub tracer with same API shape (start_span, span context manager, set_attribute, end) | Add OTel SDK dep — rejected: SDK is heavy, tracing is optional per SPEC-007 | 55-line stub; production wires to real OTel when available |
| D3 | Metrics storage: in-process dicts | Thread-safe Counter/Gauge/Histogram with Lock | Use prometheus_client — rejected: no new deps per AGENTS.md § 8 | 200-line metrics module; works for single-process, multi-threaded |
| D4 | Health endpoints: stdlib http.server | `http.server` on port 9100 in background thread | Use aiohttp/Flask — rejected: no new deps | 80-line health module; sufficient for operator health checks |
| D5 | `ops/` is a new top-level directory | Add ADR-0011 and keep observability artifacts under `ops/{dashboards,alerts,runbooks}` | Put machine-consumed ops artifacts under docs — rejected: blurs runtime/operator ownership | Satisfies AGENTS.md top-level-directory guardrail |
| D6 | SPEC-007 says traces use same redaction rules as logging | Reject forbidden trace attributes and increment `log_redaction_violation_total` | Allow traces and rely on caller discipline — rejected: violates SPEC-007 | Tracing is fail-closed for forbidden attributes |

## 15. Outcomes & Retrospective
- **What landed:** Complete observability stack: structured JSON logging with FORBIDDEN_LOG_KEYS enforcement, 14-metric REGISTRY (counters/gauges/histograms), OTel tracing stub, 4 health endpoints, 4 Grafana dashboards, 6 Prometheus alert rules, 4 role runbooks. 3 new source modules + 1 health tool + 17 ops files. 10 redaction/tracing tests + 9 metrics integration tests + 6 health E2E tests. 363 verify-phase tests pass.
- **What changed vs plan:** No structlog/OTel deps — custom implementations matching API shapes. Codex audit added backend CLI/tools unit tests. Redaction test had int-import-snapshot bug (fixed with module-level access).
- **Remaining risks:** Tracing is a stub — real OTel exporter not wired. Health server is basic stdlib — no TLS, no request limiting. Metrics are in-process only — no remote push gateway. Dashboards are minimal Grafana JSON — need real deployment to validate panels.
- **Production-readiness impact:** Phase 7 exits. EP-009 (deployment/release) is unblocked. Logging redaction enforced at emission with CI gate. All OBSERVABILITY.md metrics declared and tested. Health endpoints operational.
