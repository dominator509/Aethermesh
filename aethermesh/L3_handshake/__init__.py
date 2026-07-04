"""L3 Handshake — Noise-PQ XK + mutual attestation.

SPEC-003 § L3. Stub facade — body lands in EP-006+.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aethermesh.L5_captokens import CapTokenBundle


# ---------------------------------------------------------------------------
# SessionState
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PeerAttestationSummary:
    """Summary of a peer's attestation."""

    principal_pub: bytes = b""
    platform_root: bytes = b""


@dataclass(frozen=True)
class SessionState:
    """Post-handshake session state — SPEC-003 § L3."""

    session_root: bytes
    root_key: bytes
    header_key_send: bytes
    header_key_recv: bytes
    transcript_hash: bytes
    peer_identity: PeerAttestationSummary = field(default_factory=PeerAttestationSummary)
    captoken_bundle: CapTokenBundle | None = None


# ---------------------------------------------------------------------------
# HandshakeInitiator
# ---------------------------------------------------------------------------


class HandshakeInitiator:
    """Noise-PQ XK handshake initiator — SPEC-003 § L3."""

    def __init__(
        self,
        responder_static_x25519_pub: bytes,
        responder_static_mlkem_pub: bytes,
        prologue: bytes,
        principal: bytes,
        instance: bytes,
        platform_signing_key: bytes,
        platform_root_pub: bytes,
        expected_responder_principal_pub: bytes,
        expected_responder_platform_root_pub: bytes,
        accepted_responder_backends: tuple[str, ...],
        capability_query: bytes,
    ) -> None:
        self._msg1: bytes | None = None
        self._msg2_processed = False

    def build_message_1(self) -> bytes:
        """Build and return handshake message 1."""
        return self._msg1 or b""

    def process_message_2(self, msg: bytes) -> None:
        """Process handshake message 2 from responder."""
        self._msg2_processed = True

    def build_message_3(self, captoken_bundle: object) -> bytes:
        """Build handshake message 3 with CapToken bundle."""
        return b""

    def finalize(self) -> SessionState:
        """Finalize handshake, return SessionState."""
        return SessionState(
            session_root=b"\x00" * 32,
            root_key=b"\x00" * 32,
            header_key_send=b"\x00" * 32,
            header_key_recv=b"\x00" * 32,
            transcript_hash=b"\x00" * 32,
        )


# ---------------------------------------------------------------------------
# HandshakeResponder
# ---------------------------------------------------------------------------


class HandshakeResponder:
    """Noise-PQ XK handshake responder — SPEC-003 § L3."""

    def __init__(
        self,
        static_x25519_sk: bytes,
        static_mlkem_sk: bytes,
        prologue: bytes,
        principal: bytes,
        instance: bytes,
        platform_signing_key: bytes,
        platform_root_pub: bytes,
        expected_initiator_principal_pub: bytes,
        expected_initiator_platform_root_pub: bytes,
        accepted_initiator_backends: tuple[str, ...],
    ) -> None:
        pass

    def process_message_1(self, msg: bytes) -> bytes:
        """Process msg1, return msg2."""
        return b""

    def process_message_3(self, msg: bytes) -> None:
        """Process handshake message 3."""

    def finalize(self) -> SessionState:
        """Finalize handshake."""
        return SessionState(
            session_root=b"\x00" * 32,
            root_key=b"\x00" * 32,
            header_key_send=b"\x00" * 32,
            header_key_recv=b"\x00" * 32,
            transcript_hash=b"\x00" * 32,
        )
