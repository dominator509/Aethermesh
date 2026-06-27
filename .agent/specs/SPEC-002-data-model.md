# SPEC-002 — Data Model

- **Status:** Draft  - **Owner:** Data  - **Phase:** 2  - **ExecPlans:** EP-003

## User-Visible Goal
Local SQLite audit log + DID cache + revocation cache, reversibly migrateable, never stores PII.

## Non-Goals
Relational model for the protocol; cross-host DB.

## Terms
- **receipt_id:** `SHA3-256(canonical(AuditReceipt))`.
- **schema_version:** integer, owned by `aethermesh.tools.audit_db`.

## Required Behavior
### Tables
```
audit_receipts (
  receipt_id BLOB PK, session_root_hash BLOB NOT NULL,
  message_index INTEGER NOT NULL, intent_header_hash BLOB NOT NULL,
  body_hash BLOB NOT NULL, caller_did TEXT NOT NULL, callee_did TEXT NOT NULL,
  policy_decision TEXT NOT NULL, captoken_chain TEXT NOT NULL,
  discharge_refs TEXT NOT NULL, timestamp INTEGER NOT NULL, sig BLOB NOT NULL
);
CREATE INDEX idx_session ON audit_receipts(session_root_hash);
CREATE INDEX idx_caller  ON audit_receipts(caller_did);

did_cache (
  did TEXT PK, pubkey_bundle BLOB NOT NULL, revocation_epoch INTEGER NOT NULL,
  fetched_at INTEGER NOT NULL, expires_at INTEGER NOT NULL
);

revocation_manifests (
  issuer_did TEXT PK, revocation_epoch INTEGER NOT NULL,
  manifest_bytes BLOB NOT NULL, fetched_at INTEGER NOT NULL, not_after INTEGER NOT NULL
);
```

### Retention
- `audit_receipts`: default 90 days; configurable via `AEP_AUDIT_RETENTION_DAYS` (≥ 30 enforced).
- `did_cache`: TTL ≤ 1 epoch (3600 s).
- `revocation_manifests`: until superseded.

### Migrations
`MIGRATIONS[N]` with forward + backward SQL. `aethermesh.tools.audit_db migrate --to N` applies idempotently.

## Inputs / Outputs
- Append: `AuditReceipt` → row.
- Query: by `session_root_hash` or `caller_did`.

## Error States
- `IntegrityError` on duplicate `receipt_id`.
- Schema mismatch → process refuses to start.

## Data Rules
- No body bytes anywhere.
- No FORBIDDEN_LOG_KEYS field ever written.
- No PII.

## Security Rules
- Audit DB file mode 0600.
- WAL files in same directory.

## Performance
- 1k inserts/s/core.
- p99 query by `session_root_hash` ≤ 5 ms.

## Required Tests
- Forward + backward migration round-trip for every `SCHEMA_VERSION`.
- Insert/query under `tests/integration/tools/`.
- Negative: duplicate insert rejected.

## Acceptance Criteria
- `aethermesh.tools.audit_db migrate --check` returns 0 against previous-schema fixture.
- Coverage on `aethermesh.tools.audit_db` ≥ 85% lines.
