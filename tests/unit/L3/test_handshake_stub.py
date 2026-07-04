"""Tests for L3 HandshakeInitiator, HandshakeResponder, SessionState — coverage backfill.

EP-007 M2.
"""

from aethermesh.L3_handshake import (
    HandshakeInitiator,
    HandshakeResponder,
    PeerAttestationSummary,
    SessionState,
)


class TestPeerAttestationSummary:
    def test_defaults(self) -> None:
        pas = PeerAttestationSummary()
        assert pas.principal_pub == b""
        assert pas.platform_root == b""

    def test_custom(self) -> None:
        pas = PeerAttestationSummary(principal_pub=b"pk", platform_root=b"root")
        assert pas.principal_pub == b"pk"
        assert pas.platform_root == b"root"


class TestSessionState:
    def test_defaults(self) -> None:
        ss = SessionState(
            session_root=b"\x00" * 32,
            root_key=b"\x01" * 32,
            header_key_send=b"\x02" * 32,
            header_key_recv=b"\x03" * 32,
            transcript_hash=b"\x04" * 32,
        )
        assert len(ss.session_root) == 32
        assert len(ss.root_key) == 32
        assert ss.captoken_bundle is None

    def test_with_peer_identity(self) -> None:
        ss = SessionState(
            session_root=b"\x00" * 32,
            root_key=b"\x01" * 32,
            header_key_send=b"\x02" * 32,
            header_key_recv=b"\x03" * 32,
            transcript_hash=b"\x04" * 32,
            peer_identity=PeerAttestationSummary(principal_pub=b"peer"),
        )
        assert ss.peer_identity.principal_pub == b"peer"

    def test_with_captoken_bundle(self) -> None:
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
        ss = SessionState(
            session_root=b"\x00" * 32,
            root_key=b"\x01" * 32,
            header_key_send=b"\x02" * 32,
            header_key_recv=b"\x03" * 32,
            transcript_hash=b"\x04" * 32,
            captoken_bundle=[token],
        )
        assert ss.captoken_bundle is not None
        assert len(ss.captoken_bundle) == 1


class TestHandshakeInitiator:
    def _make_initiator(self) -> HandshakeInitiator:
        return HandshakeInitiator(
            responder_static_x25519_pub=b"\x00" * 32,
            responder_static_mlkem_pub=b"\x00" * 1184,
            prologue=b"test",
            principal=b"principal-32-bytes!!!!!!",
            instance=b"instance",
            platform_signing_key=b"\x00" * 32,
            platform_root_pub=b"\x00" * 32,
            expected_responder_principal_pub=b"responder-principal-32",
            expected_responder_platform_root_pub=b"\x00" * 32,
            accepted_responder_backends=("softsign",),
            capability_query=b"test-query",
        )

    def test_build_message_1(self) -> None:
        initiator = self._make_initiator()
        msg1 = initiator.build_message_1()
        assert isinstance(msg1, bytes)

    def test_process_message_2(self) -> None:
        initiator = self._make_initiator()
        initiator.process_message_2(b"fake-msg2")

    def test_build_message_3(self) -> None:
        initiator = self._make_initiator()
        initiator.process_message_2(b"msg2")
        msg3 = initiator.build_message_3(captoken_bundle=[])
        assert isinstance(msg3, bytes)

    def test_finalize(self) -> None:
        initiator = self._make_initiator()
        state = initiator.finalize()
        assert isinstance(state, SessionState)
        assert len(state.session_root) == 32
        assert len(state.root_key) == 32


class TestHandshakeResponder:
    def _make_responder(self) -> HandshakeResponder:
        return HandshakeResponder(
            static_x25519_sk=b"\x00" * 32,
            static_mlkem_sk=b"\x00" * 2400,
            prologue=b"test",
            principal=b"responder-principal-32",
            instance=b"instance-b",
            platform_signing_key=b"\x00" * 32,
            platform_root_pub=b"\x00" * 32,
            expected_initiator_principal_pub=b"principal-32-bytes!!!!!!",
            expected_initiator_platform_root_pub=b"\x00" * 32,
            accepted_initiator_backends=("softsign",),
        )

    def test_process_message_1(self) -> None:
        responder = self._make_responder()
        msg2 = responder.process_message_1(b"msg1")
        assert isinstance(msg2, bytes)

    def test_process_message_3(self) -> None:
        responder = self._make_responder()
        responder.process_message_1(b"msg1")
        responder.process_message_3(b"msg3")

    def test_finalize(self) -> None:
        responder = self._make_responder()
        responder.process_message_1(b"msg1")
        responder.process_message_3(b"msg3")
        state = responder.finalize()
        assert isinstance(state, SessionState)
