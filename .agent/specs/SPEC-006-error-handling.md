# SPEC-006 — Error Handling

- **Status:** Draft  - **Owner:** Architecture  - **Phase:** 3, 5

## User-Visible Goal
Predictable, taxonomized errors per layer; no internal exception leaks across boundaries.

## Per-Layer Taxonomies

### L3 — `AbortCode`
```
0x10 BAD_VERSION    0x11 UNKNOWN_SUITE
0x20 DECRYPT_FAILED 0x21 BAD_TRANSCRIPT
0x30 ATTESTATION_INVALID  0x31 ATTESTATION_REVOKED
0x32 ATTESTATION_STALE    0x33 ATTESTATION_PLATFORM_UNACCEPTABLE
0x40 POLICY_DENIED  0x41 POLICY_REJECTED
0x42 DISCHARGE_MISSING  0x43 DISCHARGE_INVALID
0x50 CAPTOKEN_MALFORMED  0x51 CAPTOKEN_CAVEAT_VIOLATION
0xF0 REPLAY_DETECTED  0xFF INTERNAL_ERROR
```
Raised as `HandshakeAbort(code, message)`.

### L4 wire codes
```
L4.10 bad_header             L4.11 unknown_dh_pub
L4.12 skip_limit_exceeded    L4.13 replay
L4.20 bad_intent_aead        L4.21 intent_canonical_violation
L4.22 capability_unknown     L4.23 capability_root_mismatch
L4.24 scope_violation        L4.25 budget_exceeded
L4.26 captoken_missing_or_revoked
L4.27 intent_path_invalid    L4.28 expired
L4.40 body_aead_failed
L4.50 mls_commit_invalid     L4.51 member_attestation_invalid
L4.52 cap_envelope_mismatch  L4.53 epoch_outdated
```

### L4 policy
`PolicyDecision`: `ALLOW`, `DENY_SCOPE`, `DENY_BUDGET`, `DENY_EXPIRED`, `DENY_UNKNOWN_CAP`, `DENY_NO_CAPTOKEN`, `PENDING_DISCHARGE`, `DENY_SCHEMA_MISMATCH`, `DENY_INTENT_PATH`.

### L5
`VerificationDecision`: `ALLOW`, `DENY_ISSUER_SIG`, `DENY_CHAIN`, `DENY_REVOKED_EPOCH`, `DENY_REVOKED_CTID`, `DENY_UNKNOWN_CAVEAT`, `DENY_TIME`, `DENY_ACTION`, `DENY_SCOPE`, `DENY_BUDGET`, `DENY_RATE`, `DENY_SESSION_BINDING`, `DENY_INSTANCE_BINDING`, `DENY_ATTESTATION_BINDING`, `DENY_PRINCIPAL_BINDING`, `DENY_LANE`, `DENY_INTENT_PATH`, `DENY_POSTURE`, `DENY_GEO`, `PENDING_DISCHARGE`, `DENY_DISCHARGE_INVALID`.

## Cross-Layer Translation
- Errors crossing a boundary translate to the receiving layer's taxonomy.
- No internal exception type (e.g., `ValueError`) leaks across boundaries.
- Translation map in `aethermesh.common.errors.TRANSLATIONS`.

## User-Facing Messages
- CLI: `aethermesh: <subcommand>: <one-line message>` to stderr.
- Logs: `event=<layer>.<topic>.<outcome>` with `abort_code` / `policy_decision` fields.

## Logging Behavior
- No FORBIDDEN_LOG_KEYS fields ever logged.
- Error reasons may include short strings; never raw bytes.

## Retry Behavior
- L1 mixnet: no auto-retry; lost packets are lost (DATAGRAM semantics).
- L4 application: caller decides; library does not retry.
- L5 discharge: caller may retry after presenting a new discharge.

## Failure States
Each layer documents decisions for: missing input, malformed input, expired input, replay, scope mismatch, budget exhaustion, unknown caveat.

## Required Tests
- One test per error code per layer asserting exact code is raised/returned.
- One translation test per cross-layer pair (L1↔L4, L3↔L4, L4↔L5).

## Acceptance Criteria
- `tests/unit/common/test_errors.py` confirms every taxonomy entry has ≥ 1 raising/returning call site.
- `tests/security/test_log_redaction.py` passes.
