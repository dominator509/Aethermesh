"""Integration roundtrip: mint CapToken, L3 handshake, L4 message, L5 verify.

EP-004 M5. Test data is deterministic and test-only.
"""

from aethermesh.api import (
    AuditLog,
    AuditReceipt,
    CapToken,
    CapTokenVerifier,
    Caveat,
    Discharge,
    HandshakeInitiator,
    HandshakeResponder,
    IntentHeader,
    KeyringService,
    PairRatchet,
    PolicyLayer,
    SessionState,
)
from aethermesh.common.did_resolver import DIDResolver

# Deterministic test material — TEST_ONLY
ALICE_PRINCIPAL = b"alice-principal-32-bytes!!!"  # 32 bytes
BOB_PRINCIPAL = b"bob-principal-32-bytes!!!!!"
X25519_PUB = bytes(range(32))
MLKEM_PUB = bytes(i % 256 for i in range(1184))
PROLOGUE = b"AetherMesh v0.1 test prologue"


class TestL3L4L5Roundtrip:
    def test_full_roundtrip(self) -> None:
        """L3 handshake → L4 ratchet → L5 verify with CapToken."""
        # ── L5: Mint CapToken ──
        token = CapToken.mint(
            issuer="did:web:example.org",
            root_resource="doc-review",
            resource_template="doc-review/{doc_id}",
            schema_pins=(),
            not_before=0,
            not_after=9999999999,
            revocation_epoch=0,
            issuer_sk=b"\x00" * 32,
        )

        # ── L3: Handshake ──
        initiator = HandshakeInitiator(
            responder_static_x25519_pub=X25519_PUB,
            responder_static_mlkem_pub=MLKEM_PUB,
            prologue=PROLOGUE,
            principal=ALICE_PRINCIPAL,
            instance=b"instance-a",
            platform_signing_key=b"\x00" * 32,
            platform_root_pub=b"\x00" * 32,
            expected_responder_principal_pub=BOB_PRINCIPAL,
            expected_responder_platform_root_pub=b"\x00" * 32,
            accepted_responder_backends=("softsign",),
            capability_query=b"doc-review",
        )

        msg1 = initiator.build_message_1()

        responder = HandshakeResponder(
            static_x25519_sk=b"\x00" * 32,
            static_mlkem_sk=b"\x00" * 2400,
            prologue=PROLOGUE,
            principal=BOB_PRINCIPAL,
            instance=b"instance-b",
            platform_signing_key=b"\x00" * 32,
            platform_root_pub=b"\x00" * 32,
            expected_initiator_principal_pub=ALICE_PRINCIPAL,
            expected_initiator_platform_root_pub=b"\x00" * 32,
            accepted_initiator_backends=("softsign",),
        )

        msg2 = responder.process_message_1(msg1)
        initiator.process_message_2(msg2)
        msg3 = initiator.build_message_3(captoken_bundle=[token])
        responder.process_message_3(msg3)

        alice_session = initiator.finalize()
        bob_session = responder.finalize()

        assert isinstance(alice_session, SessionState)
        assert isinstance(bob_session, SessionState)
        assert len(alice_session.session_root) == 32
        assert len(bob_session.session_root) == 32

        # ── L4: Pairwise Ratchet ──
        _alice = PairRatchet.initialize_alice(
            root_key=alice_session.root_key,
            bob_dh_x25519_pub=X25519_PUB,
            bob_dh_mlkem_pub=MLKEM_PUB,
        )

        _bob = PairRatchet.initialize_bob(
            root_key=bob_session.root_key,
            my_dh_x25519_sk=b"\x00" * 32,
            my_dh_x25519_pk=X25519_PUB,
            my_dh_mlkem=b"\x00" * 2400,
        )

        intent = IntentHeader(
            action="read",
            resource="doc-review/42",
            scope=("read",),
            budget=1,
            intent_path=("doc-review",),
        )

        # ── L4: Policy Layer ──
        policy = PolicyLayer()
        policy.add_captoken(token)
        policy.stage_body_key(ns=0, message_key=b"\x11" * 32)
        result = policy.validate(ns=0, intent=intent)

        from aethermesh.api import ValidationResult

        assert result == ValidationResult.ALLOW

        # ── L4: Release body key ──
        body_key = policy.release(ns=0)
        assert body_key == b"\x11" * 32

        # ── L5: Verify token ──
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b'{"key":"test-pubkey"}')

        verifier = CapTokenVerifier(
            did_resolver=resolver,
            revocation_registry=object(),
        )

        from aethermesh.api import VerificationDecision

        vresult = verifier.verify(token, request=intent)
        assert vresult.decision == VerificationDecision.ALLOW

        # ── L5: Audit ──
        audit = AuditLog()
        receipt = AuditReceipt(
            receipt_id=b"\x00" * 32,
            session_root_hash=alice_session.session_root,
            message_index=0,
            intent_header_hash=b"\x00" * 32,
            body_hash=b"\x00" * 32,
            caller_did="did:web:example.org",
            callee_did="did:web:peer.example",
            policy_decision="ALLOW",
            captoken_chain="[]",
            discharge_refs="[]",
            timestamp=1700000000,
            sig=b"\x00" * 64,
        )
        audit.append(receipt)

    def test_keyring_mint_and_discharge(self) -> None:
        """Keyring mints root CapToken and issues discharge."""
        ks = KeyringService.create(
            principal_did="did:web:example.org",
            discharger_did="did:web:org.example",
        )

        token = ks.mint_root_captoken(
            resource="api",
            template="api/{method}",
            not_before=0,
            not_after=9999999999,
            revocation_epoch=0,
        )

        assert isinstance(token, CapToken)

        caveat = Caveat("time", "2026-01-01", discharge_required=True)
        discharge = ks.issue_discharge(
            caveat,
            session_root=b"\x00" * 32,
            user_consent=True,
            lifetime_s=300,
        )
        assert isinstance(discharge, Discharge)

        # No consent → no discharge
        no_discharge = ks.issue_discharge(
            caveat,
            session_root=b"\x00" * 32,
            user_consent=False,
        )
        assert no_discharge is None

    def test_policy_denies_without_captoken(self) -> None:
        """PolicyLayer denies when no CapToken is added."""
        policy = PolicyLayer()
        intent = IntentHeader(action="write", resource="secret", scope=("write",))
        result = policy.validate(ns=1, intent=intent)
        from aethermesh.api import ValidationResult

        assert result == ValidationResult.DENY_NO_CAPTOKEN
        try:
            policy.release(ns=1)
            raise AssertionError("release should fail when policy is not ALLOW")
        except PermissionError:
            pass
