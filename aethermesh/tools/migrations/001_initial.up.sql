-- 001_initial.up.sql — Create audit_receipts, did_cache, revocation_manifests
-- SPEC-002 Tables; EP-003 M1

CREATE TABLE IF NOT EXISTS audit_receipts (
    receipt_id        BLOB PRIMARY KEY NOT NULL,
    session_root_hash BLOB NOT NULL,
    message_index     INTEGER NOT NULL,
    intent_header_hash BLOB NOT NULL,
    body_hash         BLOB NOT NULL,
    caller_did        TEXT NOT NULL,
    callee_did        TEXT NOT NULL,
    policy_decision   TEXT NOT NULL,
    captoken_chain    TEXT NOT NULL,
    discharge_refs    TEXT NOT NULL,
    timestamp         INTEGER NOT NULL,
    sig               BLOB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_session ON audit_receipts(session_root_hash);
CREATE INDEX IF NOT EXISTS idx_caller  ON audit_receipts(caller_did);

CREATE TABLE IF NOT EXISTS did_cache (
    did              TEXT PRIMARY KEY NOT NULL,
    pubkey_bundle    BLOB NOT NULL,
    revocation_epoch INTEGER NOT NULL,
    fetched_at       INTEGER NOT NULL,
    expires_at       INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS revocation_manifests (
    issuer_did       TEXT PRIMARY KEY NOT NULL,
    revocation_epoch INTEGER NOT NULL,
    manifest_bytes   BLOB NOT NULL,
    fetched_at       INTEGER NOT NULL,
    not_after        INTEGER NOT NULL
);
