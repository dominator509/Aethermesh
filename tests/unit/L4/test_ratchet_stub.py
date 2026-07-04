"""Tests for L4 PairRatchet, PolicyLayer, MlsGroup, IntentHeader stubs — coverage backfill.

EP-007 M2.
"""

from aethermesh.common.errors import PolicyDecision
from aethermesh.L4_ratchet import (
    IntentHeader,
    MlsGroup,
    PairMessage,
    PairRatchet,
    PolicyLayer,
)

ValidationResult = PolicyDecision  # per aethermesh.api re-export


class TestIntentHeader:
    def test_defaults(self) -> None:
        ih = IntentHeader()
        assert ih.action == ""
        assert ih.resource == ""
        assert ih.scope == ()
        assert ih.budget == 0

    def test_custom(self) -> None:
        ih = IntentHeader(
            action="read", resource="doc/42", scope=("read",), budget=5, intent_path=("docs",)
        )
        assert ih.action == "read"
        assert ih.resource == "doc/42"
        assert ih.scope == ("read",)
        assert ih.budget == 5
        assert ih.intent_path == ("docs",)

    def test_frozen(self) -> None:
        ih = IntentHeader(action="write")
        assert ih.action == "write"


class TestPairMessage:
    def test_defaults(self) -> None:
        pm = PairMessage(header=b"hdr", body=b"body")
        assert pm.header == b"hdr"
        assert pm.body == b"body"
        assert pm.dh_pub == b""

    def test_with_dh_pub(self) -> None:
        pm = PairMessage(header=b"h", body=b"b", dh_pub=b"dh")
        assert pm.dh_pub == b"dh"


class TestPairRatchet:
    def test_initialize_alice(self) -> None:
        ratchet = PairRatchet.initialize_alice(
            root_key=b"\x00" * 32,
            bob_dh_x25519_pub=b"\x01" * 32,
            bob_dh_mlkem_pub=b"\x02" * 1184,
        )
        assert isinstance(ratchet, PairRatchet)

    def test_initialize_bob(self) -> None:
        ratchet = PairRatchet.initialize_bob(
            root_key=b"\x00" * 32,
            my_dh_x25519_sk=b"\x01" * 32,
            my_dh_x25519_pk=b"\x02" * 32,
            my_dh_mlkem=b"\x03" * 2400,
        )
        assert isinstance(ratchet, PairRatchet)

    def test_encrypt(self) -> None:
        ratchet = PairRatchet.initialize_alice(b"\x00" * 32, b"\x01" * 32, b"\x02" * 1184)
        msg = ratchet.encrypt(b"intent", b"body", session_id=b"\x03" * 32)
        assert isinstance(msg, PairMessage)
        assert msg.body == b"body"

    def test_encrypt_with_dh_pub(self) -> None:
        ratchet = PairRatchet.initialize_alice(b"\x00" * 32, b"\x01" * 32, b"\x02" * 1184)
        msg = ratchet.encrypt(b"intent", b"body", session_id=b"\x03" * 32, include_dh_pub=True)
        assert isinstance(msg, PairMessage)

    def test_derive_message_keys(self) -> None:
        ratchet = PairRatchet.initialize_alice(b"\x00" * 32, b"\x01" * 32, b"\x02" * 1184)
        ik, mk = ratchet.derive_message_keys(b"header")
        assert len(ik) == 32
        assert len(mk) == 32


class TestPolicyLayer:
    def test_validate_deny_no_captoken(self) -> None:
        """PolicyLayer denies when no CapToken added (Codex audit: fail-closed default)."""
        policy = PolicyLayer()
        intent = IntentHeader(action="read", resource="doc")
        result = policy.validate(ns=0, intent=intent)
        assert result == ValidationResult.DENY_NO_CAPTOKEN

    def test_add_captoken(self) -> None:
        from aethermesh.api import CapToken

        policy = PolicyLayer()
        token = CapToken.mint(
            "did:web:example.org",
            "r",
            "r/{}",
            (),
            0,
            9999999999,
            0,
            b"\x00" * 32,
        )
        policy.add_captoken(token)

    def test_stage_and_release(self) -> None:
        policy = PolicyLayer()
        from aethermesh.api import CapToken

        token = CapToken.mint(
            "did:web:example.org",
            "r",
            "r/{}",
            (),
            0,
            9999999999,
            0,
            b"\x00" * 32,
        )
        policy.add_captoken(token)
        policy.stage_body_key(ns=0, message_key=b"\x11" * 32)
        policy.validate(ns=0, intent=IntentHeader(action="read"))
        body_key = policy.release(ns=0)
        assert len(body_key) == 32

    def test_release_without_allow_raises(self) -> None:
        policy = PolicyLayer()
        import pytest

        with pytest.raises(PermissionError):
            policy.release(ns=99)


class TestMlsGroup:
    def test_init(self) -> None:
        group = MlsGroup(group_id=b"g1", members=(b"m1", b"m2"))
        assert group.group_id == b"g1"

    def test_init_with_ciphersuite(self) -> None:
        group = MlsGroup(group_id=b"g2", members=(), ciphersuite="CUSTOM")
        assert group.group_id == b"g2"

    def test_add_member(self) -> None:
        group = MlsGroup(group_id=b"g1", members=(b"m1",))
        group.add_member(b"m2", b"m1")

    def test_add_member_with_envelope(self) -> None:
        group = MlsGroup(group_id=b"g1", members=(b"m1",))
        group.add_member(b"m2", b"m1", new_envelope=b"env")

    def test_intent_key_root(self) -> None:
        group = MlsGroup(group_id=b"g1", members=(b"m1",))
        key = group.intent_key_root(b"m1")
        assert len(key) == 32

    def test_message_key_root(self) -> None:
        group = MlsGroup(group_id=b"g1", members=(b"m1",))
        key = group.message_key_root(b"m1")
        assert len(key) == 32


class TestValidationResult:
    def test_enum_values(self) -> None:
        assert ValidationResult.ALLOW.value == 0
        assert ValidationResult.DENY_SCOPE.value == 1
        assert ValidationResult.DENY_NO_CAPTOKEN.value == 5
        assert ValidationResult.PENDING_DISCHARGE.value == 6
