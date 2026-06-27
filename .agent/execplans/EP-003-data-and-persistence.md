# EP-003 — Data and Persistence

- **Status:** Draft  - **Owner:** Data  - **Phase:** 2  - **Specs:** SPEC-002

## 1. Purpose / Big Picture
Implement `aethermesh.tools.audit_db` and `aethermesh.tools.cache_db`. All persistence in `aethermesh.tools.*`; no protocol-core module opens a file handle.

## 2. Scope
- `aethermesh/tools/{__init__,audit_db,cache_db,init_audit_db}.py`
- `aethermesh/tools/migrations/001_initial.{up,down}.sql`
- Integration tests.

## 3. Non-Goals
- No remote DB. No ORMs. No persistence in protocol-core.

## 4. Context and Orientation
EP-002 produced `aethermesh.common`. This plan adds the only persistence: local audit + DID/revocation cache.

## 5. Files to Read First
1. `AGENTS.md`  2. `SPEC-002-data-model.md`  3. `ENVIRONMENT.md`  4. `ARCHITECTURE.md` Persistence Boundaries  5. `bundles/aethermesh_L5/code/audit.py`

## 6. Files to Change
- `aethermesh/tools/{__init__,audit_db,cache_db,init_audit_db}.py`
- `aethermesh/tools/migrations/001_initial.{up,down}.sql`
- `tests/unit/tools/test_audit_db.py`
- `tests/integration/tools/test_audit_db_roundtrip.py`

## 7. Interfaces and Contracts
Per SPEC-002 Tables + Retention + Migrations.

## 8. Milestones

### M1 — Schema v1
- **Goal:** SQLite file with three tables + indexes per SPEC-002.
- **Files to Read:** SPEC-002.
- **Files to Change:** `migrations/001_initial.up.sql`, `001_initial.down.sql`, `audit_db.py`.
- **Exact Edits Expected:** `SCHEMA_VERSION = 1`. `MIGRATIONS = {1: (up_sql, down_sql)}`. `init(path)` opens WAL, runs migrations.
- **Validation Command:** `uv run python -c "from aethermesh.tools.audit_db import init; init('/tmp/test.db'); print('ok')"`
- **Expected Result:** prints `ok`.
- **Recovery:** Per AGENTS § 7.

### M2 — Migrate command
- **Goal:** `migrate --to N` idempotent.
- **Files to Change:** `audit_db.py`.
- **Exact Edits Expected:** `migrate(path, target=None)`. CLI: `python -m aethermesh.tools.audit_db migrate --path X --to N`. `--check` verifies current <= latest.
- **Validation Command:** `uv run python -m aethermesh.tools.audit_db migrate --path /tmp/test.db --check`
- **Expected Result:** exit 0; `audit db at schema v1`.
- **Recovery:** Per AGENTS § 7.

### M3 — Insert + query
- **Goal:** `append(receipt)`, `all_for_session(hash)`, `all_for_caller(did)`.
- **Files to Change:** `audit_db.py`, `tests/unit/tools/test_audit_db.py`.
- **Exact Edits Expected:** Parametrized SQL. Dup `receipt_id` raises `IntegrityError`.
- **Validation Command:** `uv run pytest tests/unit/tools/test_audit_db.py -q`
- **Expected Result:** exit 0; >=6 cases.
- **Recovery:** Per AGENTS § 7.

### M4 — Backup via VACUUM INTO
- **Goal:** Atomic backup.
- **Files to Read:** OPERATIONS.md Backup section.
- **Files to Change:** `audit_db.py`.
- **Exact Edits Expected:** `backup(src, dst)` runs `VACUUM INTO ?`.
- **Validation Command:** `uv run pytest tests/unit/tools/test_audit_db.py::test_backup_atomic -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

### M5 — Integration roundtrip
- **Goal:** Insert + read across migrations.
- **Files to Change:** `tests/integration/tools/test_audit_db_roundtrip.py`.
- **Exact Edits Expected:** Init v1, insert 10 receipts, migrate v0->v1, assert all rows equal.
- **Validation Command:** `uv run pytest tests/integration/tools/test_audit_db_roundtrip.py -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

### M6 — Retention enforcement
- **Goal:** `prune(now=None)` deletes old receipts.
- **Files to Read:** SPEC-002 Retention.
- **Files to Change:** `audit_db.py`, test file.
- **Exact Edits Expected:** Remove rows where `timestamp < now - retention_s`. `<30` raises ValueError.
- **Validation Command:** `uv run pytest tests/unit/tools/test_audit_db.py::test_prune -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

## 9. Concrete Steps
M1 -> M6.

## 10. Validation and Acceptance
### Acceptance Criteria
- [ ] All SPEC-002 tables created.
- [ ] Forward + backward migrations round-trip.
- [ ] Coverage on `audit_db` >=85% lines.
- [ ] `./scripts/verify.sh` exits 0.

## 11. Idempotence and Recovery
Migrations idempotent. Tests use temp paths.

## 12. Progress
- [ ] M1 — Schema v1
- [ ] M2 — Migrate
- [ ] M3 — Insert + query
- [ ] M4 — Backup
- [ ] M5 — Integration
- [ ] M6 — Retention
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
- **Production-readiness impact:** Phase 2 exits.
