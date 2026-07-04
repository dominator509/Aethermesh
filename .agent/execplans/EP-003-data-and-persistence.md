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
- `ENVIRONMENT.md` (register `AEP_AUDIT_RETENTION_DAYS`)

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
M1 -> M6. All executed 2026-07-03.

## 10. Validation and Acceptance
### Acceptance Criteria
- [x] All SPEC-002 tables created. (audit_receipts, did_cache, revocation_manifests + indexes)
- [x] Forward + backward migrations round-trip. (`migrate(..., target=0)` drops v1 tables and returns schema version to 0)
- [x] Coverage on `audit_db` >=85% lines. (98%, 123 stmts)
- [x] `./scripts/verify.sh` exits 0. (lint→format→typecheck→unit(165 passed, 1 skipped)→integration(5)→e2e(1)→build→security→audit→smoke: all ok)

## 11. Idempotence and Recovery
Migrations idempotent. Tests use temp paths. Backward migration path is covered by a v1→v0 test.

## 12. Progress
- [x] M1 — Schema v1 (3 tables + 2 indexes per SPEC-002; WAL mode; init() creates DB)
- [x] M2 — Migrate (CLI: `python -m aethermesh.tools.audit_db migrate --path --check`; idempotent forward)
- [x] M3 — Insert + query (append, all_for_session, all_for_caller; IntegrityError on dup)
- [x] M4 — Backup (VACUUM INTO atomic backup; 1 test)
- [x] M5 — Integration (4 tests: insert across init, migrate preserves data, schema persisted, tables exist)
- [x] M6 — Retention (prune with configurable days; invalid and <30 values rejected)
- [x] Final review

## 13. Surprises & Discoveries
1. **`sqlite3.Connection.execute().fetchone()[0]` returns `Any`**: Required `# type: ignore[no-any-return]` on `_current_version`. Standard sqlite3 typing issue.
2. **`dict[str, object]` incompatible with `**` unpacking**: Pytest `**r` unpacking into typed function params fails strict mypy. Used `# type: ignore[arg-type]` + `# mypy: allow-untyped-defs` in test files.
3. **SIM105 everywhere**: ruff flags `try: os.unlink(); except OSError: pass` (test cleanup). Replaced with `contextlib.suppress(OSError)` across all test files.
4. **`# pragma: no cover` needed for 3 paths**: `FileNotFoundError` (migration file missing), `_current_version` null safety, and `_cli()`. `_cli()` is validated by subprocess.
5. **Retention env var was missing from ENVIRONMENT.md**: `AEP_AUDIT_RETENTION_DAYS` is specified by SPEC-002, so audit registered it in the environment table.
6. **Future schema guard needed**: `init()` now refuses to start against a DB whose `_schema_version` is newer than this code supports.
7. **Windows cannot prove POSIX 0600**: The code applies mode `0600` on POSIX; Windows relies on ACLs, so the mode assertion is skipped there.

## 14. Decision Log
| # | Context | Decision | Alternatives | Consequences |
|---|---|---|---|---|
| D1 | Backward migration path uncovered | `# pragma: no cover` — Phase 2 never migrates down | Add test that migrates down — rejected: complex, requires creating v2+ first | Backward SQL present and valid but untested |
| D2 | Test files use `**r` dict unpacking | `# mypy: allow-untyped-defs` + `# type: ignore[arg-type]` | Use TypedDict for receipt — rejected: over-engineering for test code | Clean tests, mypy strict-passing on source |
| D3 | `_cli()` not captured by coverage (subprocess) | `# pragma: no cover`; tested via `subprocess.run` | Call `_cli()` directly — rejected: `_cli()` is private and uses argparse with real args | CLI path validated via integration test |
| D4 | cache_db.py stub | Created minimal docstring stub per EP-003 Files to Change | Full cache implementation — rejected: cache queries belong in EP-007 (DHT integration) | File present, no coverage impact |
| D5 | `/tmp/` paths on Windows | Git Bash resolves `/tmp/` to its own temp; Windows `tempfile.mkstemp` used in tests | Use `C:\tmp` — rejected: tests should be OS-portable | Works on Windows Git Bash and Linux |
| D6 | SPEC-002 names `AEP_AUDIT_RETENTION_DAYS` but ENVIRONMENT.md lacked it | Register the env var and make invalid values fail closed | Silently default invalid values to 90 — rejected: masks config errors | Retention config is discoverable and invalid values raise `ValueError` |
| D7 | SPEC-002 requires schema mismatch refusal and reversible migrations | `init()` rejects future schema versions; unit test exercises v1→v0 down migration | Leave down migration pragma-excluded — rejected: acceptance asks for round-trip | Migration evidence now covers both directions |

## 15. Outcomes & Retrospective
- **What landed:** Complete persistence layer: `audit_db.py` (init, migrate, append, query, backup, prune), migrations (001_initial.up/down.sql), `init_audit_db.py` CLI, `cache_db.py` stub. 23 unit + 4 integration tests for tools (26 passed, 1 Windows POSIX-mode skip). 98% coverage on audit_db. All verify.sh gates pass (165 unit passed, 1 skipped + 5 integration + 1 e2e).
- **What changed vs plan:** `migrate` unused import fixed in integration tests. `contextlib.suppress` pattern adopted project-wide for test cleanup. `AEP_AUDIT_RETENTION_DAYS` added to `ENVIRONMENT.md`. `init()` now rejects future schemas. `# mypy: allow-untyped-defs` added to test files with `**` unpacking patterns.
- **Remaining risks:** Retention pruning relies on env var `AEP_AUDIT_RETENTION_DAYS` — default 90 days, invalid and <30 values tested. `cache_db.py` is a stub awaiting EP-007. Windows file privacy depends on ACLs rather than enforceable POSIX `0600` bits.
- **Production-readiness impact:** Phase 2 exits. EP-004 (API/service layer) is unblocked. Persistence boundaries respected — all DB access in `aethermesh.tools.*`, no protocol-core module opens a file handle.
