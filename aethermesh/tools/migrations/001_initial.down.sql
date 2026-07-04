-- 001_initial.down.sql — Drop all initial-schema tables
-- Reverse of 001_initial.up.sql

DROP TABLE IF EXISTS audit_receipts;
DROP TABLE IF EXISTS did_cache;
DROP TABLE IF EXISTS revocation_manifests;
