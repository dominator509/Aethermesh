"""Tests for aethermesh.tools.audit_db — SPEC-002 insert/query/backup/retention.

EP-003 M3, M4, M6.
"""

# mypy: allow-untyped-defs

import contextlib
import io
import os
import sqlite3
import subprocess
import sys
import tempfile
import time

import pytest

from aethermesh.tools.audit_db import (
    SCHEMA_VERSION,
    all_for_caller,
    all_for_session,
    append,
    backup,
    init,
    migrate,
    prune,
)


@pytest.fixture
def tmpdb():
    fd, path = tempfile.mkstemp(suffix=".db", prefix="aep_test_")
    os.close(fd)
    init(path)
    yield path
    with contextlib.suppress(OSError):
        os.unlink(path)


def _receipt(
    receipt_id: bytes = b"rid-001",
    session_root_hash: bytes = b"session-hash-001",
    message_index: int = 1,
    caller_did: str = "did:web:example.org",
    callee_did: str = "did:web:peer.example",
    timestamp: int = 1700000000,
) -> dict[str, object]:
    return {
        "receipt_id": receipt_id,
        "session_root_hash": session_root_hash,
        "message_index": message_index,
        "intent_header_hash": b"intent-hash",
        "body_hash": b"body-hash",
        "caller_did": caller_did,
        "callee_did": callee_did,
        "policy_decision": "ALLOW",
        "captoken_chain": "[]",
        "discharge_refs": "[]",
        "timestamp": timestamp,
        "sig": b"sig-bytes",
    }


class TestInsert:
    def test_append_single(self, tmpdb: str) -> None:
        r = _receipt()
        append(tmpdb, **r)  # type: ignore[arg-type]

    def test_append_duplicate_rejects(self, tmpdb: str) -> None:
        r = _receipt()
        append(tmpdb, **r)  # type: ignore[arg-type]
        with pytest.raises(sqlite3.IntegrityError):
            append(tmpdb, **r)  # type: ignore[arg-type]

    def test_append_multiple(self, tmpdb: str) -> None:
        for i in range(5):
            r = _receipt(
                receipt_id=f"rid-{i:03d}".encode(),
                message_index=i,
            )
            append(tmpdb, **r)  # type: ignore[arg-type]


class TestQuery:
    def test_all_for_session(self, tmpdb: str) -> None:
        sh = b"session-xyz"
        for i in range(3):
            r = _receipt(
                receipt_id=f"rid-{i:03d}".encode(),
                session_root_hash=sh,
                message_index=i,
            )
            append(tmpdb, **r)  # type: ignore[arg-type]

        results = all_for_session(tmpdb, sh)
        assert len(results) == 3
        assert [row["message_index"] for row in results] == [0, 1, 2]

    def test_all_for_session_empty(self, tmpdb: str) -> None:
        results = all_for_session(tmpdb, b"nonexistent")
        assert results == []

    def test_all_for_caller(self, tmpdb: str) -> None:
        for i in range(3):
            r = _receipt(
                receipt_id=f"rid-{i:03d}".encode(),
                caller_did="did:web:org.example",
                timestamp=1700000000 + i,
            )
            append(tmpdb, **r)  # type: ignore[arg-type]

        results = all_for_caller(tmpdb, "did:web:org.example")
        assert len(results) == 3

    def test_all_for_caller_empty(self, tmpdb: str) -> None:
        results = all_for_caller(tmpdb, "did:web:org.example")
        assert results == []

    def test_schema_version_after_init(self, tmpdb: str) -> None:
        conn = sqlite3.connect(tmpdb)
        v = conn.execute("SELECT version FROM _schema_version").fetchone()[0]
        conn.close()
        assert v == SCHEMA_VERSION

    def test_file_mode_0600_on_posix(self, tmpdb: str) -> None:
        if os.name == "nt":
            pytest.skip("Windows uses ACLs, not POSIX mode bits")
        assert (os.stat(tmpdb).st_mode & 0o777) == 0o600


class TestMigrate:
    def test_migrate_check_fresh(self, tmpdb: str) -> None:
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            migrate(tmpdb, check=True)
        assert "audit db at schema v1" in f.getvalue()

    def test_migrate_to_current_idempotent(self, tmpdb: str) -> None:
        migrate(tmpdb, target=SCHEMA_VERSION)
        migrate(tmpdb, target=SCHEMA_VERSION)

    def test_migrate_backward_to_zero(self, tmpdb: str) -> None:
        migrate(tmpdb, target=0)
        conn = sqlite3.connect(tmpdb)
        try:
            version = conn.execute("SELECT version FROM _schema_version").fetchone()[0]
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
        finally:
            conn.close()
        assert version == 0
        assert "audit_receipts" not in tables
        assert "did_cache" not in tables
        assert "revocation_manifests" not in tables

    def test_migrate_check_behind(self) -> None:
        fd, path = tempfile.mkstemp(suffix=".db", prefix="aep_test_")
        os.close(fd)
        try:
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                migrate(path, check=True)
            assert "behind" in f.getvalue()
        finally:
            with contextlib.suppress(OSError):
                os.unlink(path)


class TestBackup:
    def test_backup_atomic(self, tmpdb: str) -> None:
        r = _receipt()
        append(tmpdb, **r)  # type: ignore[arg-type]

        fd, dst = tempfile.mkstemp(suffix=".db", prefix="aep_backup_")
        os.close(fd)
        try:
            backup(tmpdb, dst)
            results = all_for_session(dst, b"session-hash-001")
            assert len(results) == 1
        finally:
            with contextlib.suppress(OSError):
                os.unlink(dst)


class TestPrune:
    def test_prune_deletes_old(self, tmpdb: str) -> None:
        old_time = int(time.time()) - 100 * 86400
        r = _receipt(receipt_id=b"old-receipt", timestamp=old_time)
        append(tmpdb, **r)  # type: ignore[arg-type]
        count = prune(tmpdb)
        assert count == 1
        results = all_for_session(tmpdb, b"session-hash-001")
        assert results == []

    def test_prune_keeps_recent(self, tmpdb: str) -> None:
        recent_time = int(time.time()) - 10 * 86400
        r = _receipt(receipt_id=b"recent-receipt", timestamp=recent_time)
        append(tmpdb, **r)  # type: ignore[arg-type]
        count = prune(tmpdb)
        assert count == 0
        results = all_for_session(tmpdb, b"session-hash-001")
        assert len(results) == 1

    def test_prune_empty(self, tmpdb: str) -> None:
        count = prune(tmpdb)
        assert count == 0


class TestEdgeCases:
    def test_migrate_check_version_ahead_raises(self, tmpdb: str) -> None:
        with pytest.raises(RuntimeError, match="> target"):
            migrate(tmpdb, target=0, check=True)

    def test_cli_migrate_module(self) -> None:
        fd, path = tempfile.mkstemp(suffix=".db", prefix="aep_cli_")
        os.close(fd)
        try:
            init(path)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "aethermesh.tools.audit_db",
                    "migrate",
                    "--path",
                    path,
                    "--check",
                ],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            assert "audit db at schema v1" in result.stdout
        finally:
            with contextlib.suppress(OSError):
                os.unlink(path)

    def test_prune_retention_below_min_raises(self, tmpdb: str) -> None:
        old = os.environ.get("AEP_AUDIT_RETENTION_DAYS")
        os.environ["AEP_AUDIT_RETENTION_DAYS"] = "10"
        try:
            with pytest.raises(ValueError, match=">= 30"):
                prune(tmpdb)
        finally:
            if old is not None:
                os.environ["AEP_AUDIT_RETENTION_DAYS"] = old
            else:
                del os.environ["AEP_AUDIT_RETENTION_DAYS"]

    def test_prune_retention_non_integer_raises(self, tmpdb: str) -> None:
        old = os.environ.get("AEP_AUDIT_RETENTION_DAYS")
        os.environ["AEP_AUDIT_RETENTION_DAYS"] = "ninety"
        try:
            with pytest.raises(ValueError, match="must be an integer"):
                prune(tmpdb)
        finally:
            if old is not None:
                os.environ["AEP_AUDIT_RETENTION_DAYS"] = old
            else:
                del os.environ["AEP_AUDIT_RETENTION_DAYS"]

    def test_init_future_schema_refuses_to_start(self, tmpdb: str) -> None:
        conn = sqlite3.connect(tmpdb)
        conn.execute("UPDATE _schema_version SET version = ?", (SCHEMA_VERSION + 1,))
        conn.commit()
        conn.close()
        with pytest.raises(RuntimeError, match="supported"):
            init(tmpdb)

    def test_init_migration_missing_raises(self) -> None:
        fd, path = tempfile.mkstemp(suffix=".db", prefix="aep_edge_")
        os.close(fd)
        try:
            init(path)
            with pytest.raises(RuntimeError, match="No migration for version"):
                migrate(path, target=99)
        finally:
            with contextlib.suppress(OSError):
                os.unlink(path)
