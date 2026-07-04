"""Contract tests: every SPEC-003 public symbol is importable and signature-pinned.

EP-004 M3.
"""

import inspect
from collections.abc import Callable
from dataclasses import fields

import aethermesh.api as api
from aethermesh.common.errors import PolicyDecision, VerificationDecision

# SPEC-003 required facade symbols.
REQUIRED_SYMBOLS = [
    "HandshakeInitiator",
    "HandshakeResponder",
    "SessionState",
    "PairRatchet",
    "PolicyLayer",
    "IntentHeader",
    "MlsGroup",
    "CapToken",
    "Caveat",
    "CapTokenVerifier",
    "Discharge",
    "KeyringService",
    "AuditLog",
]


def _parameter_names(callable_object: Callable[..., object]) -> list[str]:
    return list(inspect.signature(callable_object).parameters)


class TestApiSurface:
    def test_all_symbols_importable(self) -> None:
        """Every SPEC-003 symbol is importable from aethermesh.api."""
        for name in REQUIRED_SYMBOLS:
            obj = getattr(api, name, None)
            assert obj is not None, f"{name} not found in aethermesh.api"

    def test_all_symbols_in_all(self) -> None:
        """Every SPEC-003 facade symbol is in __all__."""
        for name in REQUIRED_SYMBOLS:
            assert name in api.__all__, f"{name} not in __all__"

    def test_decision_aliases_use_shared_taxonomy(self) -> None:
        assert api.ValidationResult is PolicyDecision
        assert api.VerificationDecision is VerificationDecision


class TestHandshakeInitiator:
    def test_init_signature(self) -> None:
        assert _parameter_names(api.HandshakeInitiator.__init__) == [
            "self",
            "responder_static_x25519_pub",
            "responder_static_mlkem_pub",
            "prologue",
            "principal",
            "instance",
            "platform_signing_key",
            "platform_root_pub",
            "expected_responder_principal_pub",
            "expected_responder_platform_root_pub",
            "accepted_responder_backends",
            "capability_query",
        ]

    def test_methods(self) -> None:
        assert _parameter_names(api.HandshakeInitiator.build_message_1) == ["self"]
        assert _parameter_names(api.HandshakeInitiator.process_message_2) == ["self", "msg"]
        assert _parameter_names(api.HandshakeInitiator.build_message_3) == [
            "self",
            "captoken_bundle",
        ]
        assert _parameter_names(api.HandshakeInitiator.finalize) == ["self"]


class TestHandshakeResponder:
    def test_init_signature(self) -> None:
        assert _parameter_names(api.HandshakeResponder.__init__) == [
            "self",
            "static_x25519_sk",
            "static_mlkem_sk",
            "prologue",
            "principal",
            "instance",
            "platform_signing_key",
            "platform_root_pub",
            "expected_initiator_principal_pub",
            "expected_initiator_platform_root_pub",
            "accepted_initiator_backends",
        ]

    def test_methods(self) -> None:
        assert _parameter_names(api.HandshakeResponder.process_message_1) == ["self", "msg"]
        assert _parameter_names(api.HandshakeResponder.process_message_3) == ["self", "msg"]
        assert _parameter_names(api.HandshakeResponder.finalize) == ["self"]


class TestSessionState:
    def test_fields(self) -> None:
        field_names = {f.name for f in fields(api.SessionState)}
        assert field_names == {
            "session_root",
            "root_key",
            "header_key_send",
            "header_key_recv",
            "transcript_hash",
            "peer_identity",
            "captoken_bundle",
        }


class TestPairRatchet:
    def test_classmethods(self) -> None:
        assert _parameter_names(api.PairRatchet.initialize_alice) == [
            "root_key",
            "bob_dh_x25519_pub",
            "bob_dh_mlkem_pub",
        ]
        assert _parameter_names(api.PairRatchet.initialize_bob) == [
            "root_key",
            "my_dh_x25519_sk",
            "my_dh_x25519_pk",
            "my_dh_mlkem",
        ]

    def test_methods(self) -> None:
        assert _parameter_names(api.PairRatchet.encrypt) == [
            "self",
            "intent_header_bytes",
            "body_bytes",
            "session_id",
            "include_dh_pub",
        ]
        assert _parameter_names(api.PairRatchet.derive_message_keys) == ["self", "header"]


class TestPolicyLayer:
    def test_methods(self) -> None:
        assert _parameter_names(api.PolicyLayer.add_captoken) == ["self", "info"]
        assert _parameter_names(api.PolicyLayer.stage_body_key) == [
            "self",
            "ns",
            "message_key",
        ]
        assert _parameter_names(api.PolicyLayer.validate) == ["self", "ns", "intent"]
        assert _parameter_names(api.PolicyLayer.release) == ["self", "ns"]


class TestMlsGroup:
    def test_init_signature(self) -> None:
        assert _parameter_names(api.MlsGroup.__init__) == [
            "self",
            "group_id",
            "members",
            "ciphersuite",
        ]

    def test_methods(self) -> None:
        assert _parameter_names(api.MlsGroup.add_member) == [
            "self",
            "member",
            "committer_id",
            "new_envelope",
        ]
        assert _parameter_names(api.MlsGroup.intent_key_root) == ["self", "sender_id"]
        assert _parameter_names(api.MlsGroup.message_key_root) == ["self", "sender_id"]


class TestCapToken:
    def test_mint_signature(self) -> None:
        assert _parameter_names(api.CapToken.mint) == [
            "issuer",
            "root_resource",
            "resource_template",
            "schema_pins",
            "not_before",
            "not_after",
            "revocation_epoch",
            "issuer_sk",
        ]

    def test_methods(self) -> None:
        assert _parameter_names(api.CapToken.attenuate) == ["self", "new_caveat"]
        assert _parameter_names(api.CapToken.verify_root) == ["self", "resolver"]
        assert _parameter_names(api.CapToken.verify_chain) == ["self"]

    def test_attenuate_returns_new_token(self) -> None:
        token = api.CapToken.mint(
            issuer="did:web:example.org",
            root_resource="api",
            resource_template="api/{method}",
            schema_pins=(),
            not_before=0,
            not_after=1,
            revocation_epoch=0,
            issuer_sk=b"\x00" * 32,
        )
        attenuated = token.attenuate(api.Caveat("scope", "read"))
        assert attenuated is not token
        assert token.caveats == []
        assert len(attenuated.caveats) == 1


class TestCaveat:
    def test_init_signature_and_fields(self) -> None:
        assert _parameter_names(api.Caveat.__init__) == [
            "self",
            "caveat_type",
            "value",
            "discharge_required",
        ]
        c = api.Caveat("time", "2026-01-01")
        assert c.caveat_type == "time"
        assert c.value == "2026-01-01"


class TestCapTokenVerifier:
    def test_verify_signature(self) -> None:
        assert _parameter_names(api.CapTokenVerifier.verify) == [
            "self",
            "token",
            "request",
            "discharges",
            "ledger",
        ]


class TestDischarge:
    def test_init_signature_and_fields(self) -> None:
        assert _parameter_names(api.Discharge.__init__) == [
            "self",
            "caveat_type",
            "session_root",
            "discharger_did",
        ]
        d = api.Discharge("time", b"\x00" * 32, "did:web:org.example")
        assert d.caveat_type == "time"


class TestKeyringService:
    def test_create_classmethod(self) -> None:
        assert _parameter_names(api.KeyringService.create) == [
            "principal_did",
            "discharger_did",
            "resolver",
        ]

    def test_methods(self) -> None:
        assert _parameter_names(api.KeyringService.mint_root_captoken) == [
            "self",
            "resource",
            "template",
            "schema_pins",
            "not_before",
            "not_after",
            "revocation_epoch",
        ]
        assert _parameter_names(api.KeyringService.issue_discharge) == [
            "self",
            "caveat",
            "session_root",
            "user_consent",
            "lifetime_s",
        ]


class TestAuditLog:
    def test_methods(self) -> None:
        assert _parameter_names(api.AuditLog.append) == ["self", "receipt"]
        assert _parameter_names(api.AuditLog.all_for_session) == [
            "self",
            "session_root_hash",
        ]
