# SPEC-003 — API Contracts

- **Status:** Draft  - **Owner:** Architecture  - **Phase:** 3  - **ExecPlans:** EP-004

## User-Visible Goal
Stable public APIs for L3, L4, L5 through `aethermesh.api`.

## Non-Goals
HTTP/gRPC services; public exposure of internal helpers.

## Required Behavior

### L3 — Handshake
```
HandshakeInitiator(responder_static_x25519_pub, responder_static_mlkem_pub,
                   prologue, principal, instance, platform_signing_key,
                   platform_root_pub, expected_responder_principal_pub,
                   expected_responder_platform_root_pub,
                   accepted_responder_backends, capability_query)
  .build_message_1() -> bytes
  .process_message_2(bytes) -> None
  .build_message_3(captoken_bundle) -> bytes
  .finalize() -> SessionState

HandshakeResponder(static, prologue, principal, instance, ...) — symmetrical

SessionState(session_root: bytes32, root_key: bytes32,
             header_key_send: bytes32, header_key_recv: bytes32,
             transcript_hash: bytes32, peer_identity: PeerAttestationSummary,
             captoken_bundle: CapTokenBundle | None)
```

### L4 — Session
```
PairRatchet.initialize_alice(root_key, bob_dh_x25519_pub, bob_dh_mlkem_pub)
PairRatchet.initialize_bob(root_key, my_dh_x25519_sk, my_dh_x25519_pk, my_dh_mlkem)
PairRatchet.encrypt(intent_header_bytes, body_bytes, session_id, include_dh_pub=False) -> PairMessage
PairRatchet.derive_message_keys(header, ...) -> (intent_key, message_key)

PolicyLayer.add_captoken(info)
PolicyLayer.stage_body_key(ns, message_key)
PolicyLayer.validate(ns, intent: IntentHeader) -> ValidationResult
PolicyLayer.release(ns) -> bytes32  # raises PermissionError if not ALLOW

MlsGroup(group_id, members, ...)
MlsGroup.add_member(member, committer_id, new_envelope=None)
MlsGroup.intent_key_root(sender_id) -> bytes
MlsGroup.message_key_root(sender_id) -> bytes
```

### L5 — Authority
```
CapToken.mint(issuer, root_resource, resource_template, schema_pins,
              not_before, not_after, revocation_epoch, issuer_sk) -> CapToken
CapToken.attenuate(new_caveat: Caveat) -> CapToken
CapToken.verify_root(resolver) -> bool
CapToken.verify_chain() -> bool

CapTokenVerifier(did_resolver, revocation_registry, schema_registry=None)
  .verify(token, request, discharges=None, ledger=None) -> VerificationResult

KeyringService.create(principal_did, discharger_did, resolver=None)
KeyringService.mint_root_captoken(...) -> CapToken
KeyringService.issue_discharge(caveat, session_root, user_consent, lifetime_s=300) -> Discharge | None

AuditLog.append(receipt: AuditReceipt)
AuditLog.all_for_session(session_root_hash) -> list[AuditReceipt]
```

### Facade
```
from aethermesh.api import (
  HandshakeInitiator, HandshakeResponder, SessionState,
  PairRatchet, PolicyLayer, IntentHeader, MlsGroup,
  CapToken, Caveat, CapTokenVerifier, Discharge, KeyringService, AuditLog,
)
```

## Error States
- L3: `HandshakeAbort(code: AbortCode, message: str)`.
- L4: `PolicyLayer.release(ns)` raises `PermissionError` if not ALLOW.
- L5: `verify()` returns `VerificationResult(decision, reason, ...)`.

## Security Rules
- Public APIs accept bytes/immutable types.
- No public API leaks `intent_key`, `message_key`, or any FORBIDDEN_LOG_KEYS.

## Required Tests
- Contract tests in `tests/contracts/` pin public symbols.
- Vector-based round-trip L3 → L4 → L5.

## Acceptance Criteria
- Removing any public symbol fails `tests/contracts/`.
- All five layer demos use only `aethermesh.api` imports.
