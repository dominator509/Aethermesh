"""Integration test: insert receipts across schema init, verify all rows survive.

EP-003 M5.
"""

# mypy: allow-untyped-defs

import contextlib
import os
import tempfile

from aethermesh.tools.audit_db import (
    SCHEMA_VERSION,
    all_for_caller,
    all_for_session,
    append,
    init,
)


class TestAuditDbRoundtrip:
    def test_insert_across_init(self) -> None:
        """Init v1, insert 10 receipts, verify all rows present."""
        fd, path = tempfile.mkstemp(suffix=".db", prefix="aep_int_")
        os.close(fd)
        try:
            init(path)

            session_hash = b"integration-session-hash"
            for i in range(10):
                append(
                    path,
                    receipt_id=f"int-rid-{i:03d}".encode(),
                    session_root_hash=session_hash,
                    message_index=i,
                    intent_header_hash=b"intent-hash",
                    body_hash=b"body-hash",
                    caller_did="did:web:org.example",
                    callee_did="did:web:peer.example",
                    policy_decision="ALLOW",
                    captoken_chain="[]",
                    discharge_refs="[]",
                    timestamp=1700000000 + i,
                    sig=b"sig",
                )

            results = all_for_session(path, session_hash)
            assert len(results) == 10
            for i, row in enumerate(results):
                assert row["message_index"] == i

            caller_results = all_for_caller(path, "did:web:org.example")
            assert len(caller_results) == 10

        finally:
            with contextlib.suppress(OSError):
                os.unlink(path)

    def test_migrate_preserves_data(self) -> None:
        """After init to v1 and inserting data, re-running migrate is idempotent."""
        fd, path = tempfile.mkstemp(suffix=".db", prefix="aep_int_")
        os.close(fd)
        try:
            init(path)

            append(
                path,
                receipt_id=b"migrate-test",
                session_root_hash=b"sh",
                message_index=0,
                intent_header_hash=b"ih",
                body_hash=b"bh",
                caller_did="did:web:example.org",
                callee_did="did:web:peer.example",
                policy_decision="ALLOW",
                captoken_chain="[]",
                discharge_refs="[]",
                timestamp=1700000000,
                sig=b"sig",
            )

            init(path)
            results = all_for_session(path, b"sh")
            assert len(results) == 1
        finally:
            with contextlib.suppress(OSError):
                os.unlink(path)

    def test_schema_version_persisted(self) -> None:
        """Schema version table is visible and correct after init."""
        fd, path = tempfile.mkstemp(suffix=".db", prefix="aep_int_")
        os.close(fd)
        try:
            init(path)
            import sqlite3

            conn = sqlite3.connect(path)
            v = conn.execute("SELECT version FROM _schema_version").fetchone()[0]
            conn.close()
            assert v == SCHEMA_VERSION
        finally:
            with contextlib.suppress(OSError):
                os.unlink(path)

    def test_all_tables_exist(self) -> None:
        """SPEC-002: three tables created on init."""
        fd, path = tempfile.mkstemp(suffix=".db", prefix="aep_int_")
        os.close(fd)
        try:
            init(path)
            import sqlite3

            conn = sqlite3.connect(path)
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
            conn.close()
            table_names = {t[0] for t in tables}
            assert "audit_receipts" in table_names
            assert "did_cache" in table_names
            assert "revocation_manifests" in table_names
        finally:
            with contextlib.suppress(OSError):
                os.unlink(path)
