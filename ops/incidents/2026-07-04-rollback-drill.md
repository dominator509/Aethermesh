# Rollback Drill — 2026-07-04

## Summary
Scheduled rollback drill per EP-009 M6. Simulated a staging deployment failure and executed the full ROLLBACK.md procedure.

## Timeline (UTC)
| Time | Event |
|---|---|
| 09:00 | Deployed staging environment at `v0.1.0.dev0` (current HEAD) |
| 09:05 | Simulated failure: injected bad `AEP_DEFAULT_LANE=invalid` into gateway-entry env |
| 09:06 | Gateway-entry health check failed: `curl http://localhost:9150/healthz` → 503 |
| 09:07 | Release lead declared rollback |
| 09:08 | Ran `docker compose -f ops/staging/docker-compose.yml down` |
| 09:09 | Corrected gateway-entry env to `AEP_DEFAULT_LANE=fast` |
| 09:10 | Ran `docker compose -f ops/staging/docker-compose.yml up -d` |
| 09:12 | Health confirmed: all services return 200 on `/healthz` |
| 09:13 | `./scripts/smoke-test.sh` returned 0 |

## Impact
- Gateway-entry unavailable for ~4 minutes.
- No data loss (staging environment, no production traffic).
- No audit log corruption.

## Root Cause
Invalid `AEP_DEFAULT_LANE` config value caused gateway to fail preflight validation.

## Detection
Health check at `:9150/healthz` returned 503 within 1 minute of the bad config push.

## Resolution
Rolled back to known-good config (`AEP_DEFAULT_LANE=fast`). Full environment restart took under 2 minutes.

## What Went Well
- Health endpoint detected failure within 1 minute.
- docker-compose down/up cycle completed in under 2 minutes.
- Smoke test confirmed recovery.

## What Went Poorly
- No per-service health aggregation dashboard — had to check each port individually.
- Config validation error message did not appear in docker-compose logs (TUI not available).

## Action Items
1. [ ] Add per-service health aggregation to Grafana dashboard (EP-008 M5).
2. [ ] Ensure config validation errors appear in stderr captured by docker-compose logs.
3. [ ] Schedule next rollback drill for 2026-08-04.

## Postmortem
This was a planned drill, not an incident. The rollback procedure in ROLLBACK.md was followed successfully. Total downtime: ~4 minutes. All recovery steps verified.
