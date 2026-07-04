"""SQLite audit log + DID cache + revocation cache.

SPEC-002 — Local persistence. All DB access lives in aethermesh.tools.*.
No protocol-core module opens a file handle (ARCHITECTURE.md § Persistence Boundaries).

EP-003 M1–M6.
"""

import os
import sqlite3
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Schema metadata
# ---------------------------------------------------------------------------

SCHEMA_VERSION = 1

_MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def _load_migration(version: int, direction: str) -> str:
    path = _MIGRATIONS_DIR / f"{version:03d}_initial.{direction}.sql"
    if not path.exists():  # pragma: no cover
        raise FileNotFoundError(f"Migration not found: {path}")
    return path.read_text(encoding="utf-8")


MIGRATIONS: dict[int, tuple[str, str]] = {
    1: (_load_migration(1, "up"), _load_migration(1, "down")),
}

# ---------------------------------------------------------------------------
# Retention
# ---------------------------------------------------------------------------

DEFAULT_RETENTION_SECONDS = 90 * 86400  # 90 days
MIN_RETENTION_SECONDS = 30 * 86400  # 30 days minimum


def _retention_seconds() -> int:
    days_str = os.environ.get("AEP_AUDIT_RETENTION_DAYS", "90")
    try:
        days = int(days_str)
    except ValueError:
        raise ValueError("AEP_AUDIT_RETENTION_DAYS must be an integer") from None
    if days < 30:
        raise ValueError(f"AEP_AUDIT_RETENTION_DAYS must be >= 30, got {days}")
    return days * 86400


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------


def init(path: str) -> None:
    """Create or open audit DB at *path*, run pending migrations."""
    conn = _connect(path)
    try:
        _ensure_schema_version_table(conn)
        current = _current_version(conn)
        if current > SCHEMA_VERSION:
            raise RuntimeError(f"Schema version {current} > supported v{SCHEMA_VERSION}")
        if current < SCHEMA_VERSION:
            _migrate_forward(conn, current, SCHEMA_VERSION)
    finally:
        conn.close()


def _connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    _restrict_file_permissions(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _restrict_file_permissions(path: str) -> None:
    """Set audit DB mode to 0600 on POSIX hosts.

    Windows file privacy is governed by ACLs, not POSIX mode bits.
    """
    if os.name != "nt" and path not in (":memory:", ""):
        os.chmod(path, 0o600)


def _ensure_schema_version_table(conn: sqlite3.Connection) -> None:
    conn.execute("CREATE TABLE IF NOT EXISTS _schema_version (version INTEGER PRIMARY KEY)")
    conn.commit()
    cur = conn.execute("SELECT COUNT(*) FROM _schema_version")
    if cur.fetchone()[0] == 0:
        conn.execute("INSERT INTO _schema_version (version) VALUES (0)")
        conn.commit()


def _current_version(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT version FROM _schema_version").fetchone()
    if row is None:  # pragma: no cover
        return 0
    return row[0]  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# Migrate
# ---------------------------------------------------------------------------


def migrate(path: str, target: int | None = None, check: bool = False) -> None:
    """Apply or verify migrations.

    Args:
        path: Database file path.
        target: Target schema version (default: latest).
        check: If True, only verify current version; don't apply migrations.
    """
    if target is None:
        target = SCHEMA_VERSION

    conn = _connect(path)
    try:
        _ensure_schema_version_table(conn)
        current = _current_version(conn)

        if check:
            if current > target:
                raise RuntimeError(f"Schema version {current} > target {target}")
            if current < target:
                print(f"audit db at schema v{current} (behind target v{target})")
            else:
                print(f"audit db at schema v{current}")
            return

        if current < target:
            _migrate_forward(conn, current, target)
        elif current > target:  # pragma: no cover
            _migrate_backward(conn, current, target)

        print(f"audit db at schema v{_current_version(conn)}")
    finally:
        conn.close()


def _migrate_forward(conn: sqlite3.Connection, from_version: int, to_version: int) -> None:
    for v in range(from_version + 1, to_version + 1):
        if v not in MIGRATIONS:
            raise RuntimeError(f"No migration for version {v}")
        up_sql, _ = MIGRATIONS[v]
        conn.executescript(up_sql)
        conn.execute("UPDATE _schema_version SET version = ?", (v,))
        conn.commit()


def _migrate_backward(conn: sqlite3.Connection, from_version: int, to_version: int) -> None:
    for v in range(from_version, to_version, -1):
        if v not in MIGRATIONS:
            raise RuntimeError(f"No migration for version {v}")
        _, down_sql = MIGRATIONS[v]
        conn.executescript(down_sql)
        conn.execute("UPDATE _schema_version SET version = ?", (v - 1,))
        conn.commit()


# ---------------------------------------------------------------------------
# Insert + query (M3)
# ---------------------------------------------------------------------------


def append(
    path: str,
    receipt_id: bytes,
    session_root_hash: bytes,
    message_index: int,
    intent_header_hash: bytes,
    body_hash: bytes,
    caller_did: str,
    callee_did: str,
    policy_decision: str,
    captoken_chain: str,
    discharge_refs: str,
    timestamp: int,
    sig: bytes,
) -> None:
    """Insert an audit receipt. Raises sqlite3.IntegrityError on duplicate receipt_id."""
    conn = _connect(path)
    try:
        conn.execute(
            """INSERT INTO audit_receipts (
                receipt_id, session_root_hash, message_index, intent_header_hash,
                body_hash, caller_did, callee_did, policy_decision,
                captoken_chain, discharge_refs, timestamp, sig
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                receipt_id,
                session_root_hash,
                message_index,
                intent_header_hash,
                body_hash,
                caller_did,
                callee_did,
                policy_decision,
                captoken_chain,
                discharge_refs,
                timestamp,
                sig,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def all_for_session(path: str, session_root_hash: bytes) -> list[dict[str, object]]:
    """Return all receipts for a given session_root_hash."""
    conn = _connect(path)
    try:
        rows = conn.execute(
            "SELECT * FROM audit_receipts WHERE session_root_hash = ? ORDER BY message_index",
            (session_root_hash,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def all_for_caller(path: str, caller_did: str) -> list[dict[str, object]]:
    """Return all receipts for a given caller DID."""
    conn = _connect(path)
    try:
        rows = conn.execute(
            "SELECT * FROM audit_receipts WHERE caller_did = ? ORDER BY timestamp",
            (caller_did,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        conn.close()


def _row_to_dict(row: tuple[object, ...]) -> dict[str, object]:
    cols = [
        "receipt_id",
        "session_root_hash",
        "message_index",
        "intent_header_hash",
        "body_hash",
        "caller_did",
        "callee_did",
        "policy_decision",
        "captoken_chain",
        "discharge_refs",
        "timestamp",
        "sig",
    ]
    return dict(zip(cols, row, strict=True))


# ---------------------------------------------------------------------------
# Backup (M4)
# ---------------------------------------------------------------------------


def backup(src: str, dst: str) -> None:
    """Create an atomic backup of *src* to *dst* via VACUUM INTO."""
    conn = _connect(src)
    try:
        conn.execute("VACUUM INTO ?", (dst,))
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Retention (M6)
# ---------------------------------------------------------------------------


def prune(path: str, now: float | None = None) -> int:
    """Delete audit_receipts older than retention period.

    Args:
        path: Database path.
        now: Current unix timestamp (default: time.time()).

    Returns:
        Number of rows deleted.

    Raises:
        ValueError: If retention period is < minimum.
    """
    retention = _retention_seconds()
    if retention < MIN_RETENTION_SECONDS:
        raise ValueError(
            f"Retention must be >= {MIN_RETENTION_SECONDS}s ({MIN_RETENTION_SECONDS // 86400} days)"
        )

    if now is None:
        now = time.time()

    cutoff = int(now) - retention
    conn = _connect(path)
    try:
        cur = conn.execute("DELETE FROM audit_receipts WHERE timestamp < ?", (cutoff,))
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CLI entry point: python -m aethermesh.tools.audit_db migrate --path X
# ---------------------------------------------------------------------------


def _cli() -> None:  # pragma: no cover
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="AetherMesh audit database management")
    sub = parser.add_subparsers(dest="command")

    migrate_p = sub.add_parser("migrate", help="Run database migrations")
    migrate_p.add_argument("--path", required=True, help="Path to SQLite database")
    migrate_p.add_argument("--to", type=int, default=None, help="Target schema version")
    migrate_p.add_argument("--check", action="store_true", help="Only check current version")

    args = parser.parse_args()
    if args.command == "migrate":
        migrate(args.path, target=args.to, check=args.check)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    _cli()
