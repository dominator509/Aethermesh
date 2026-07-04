"""L4 Session — PQ Double Ratchet + MLS group + policy layer.

SPEC-003 § L4. Stub facade — body lands in EP-006+.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from aethermesh.common.errors import PolicyDecision as ValidationResult

if TYPE_CHECKING:
    from aethermesh.L5_captokens import CapToken


# ---------------------------------------------------------------------------
# IntentHeader
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IntentHeader:
    """Intent header for policy validation — SPEC-003 § L4."""

    action: str = ""
    resource: str = ""
    scope: tuple[str, ...] = ()
    budget: int = 0
    intent_path: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# PairRatchet
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PairMessage:
    """A single message in the PairRatchet protocol."""

    header: bytes
    body: bytes
    dh_pub: bytes = b""


class PairRatchet:
    """PQ Double Ratchet pairwise session — SPEC-003 § L4."""

    def __init__(self) -> None:
        self._initialized = False

    @classmethod
    def initialize_alice(
        cls,
        root_key: bytes,
        bob_dh_x25519_pub: bytes,
        bob_dh_mlkem_pub: bytes,
    ) -> PairRatchet:
        """Initialize as Alice (sender of first message)."""
        return cls()

    @classmethod
    def initialize_bob(
        cls,
        root_key: bytes,
        my_dh_x25519_sk: bytes,
        my_dh_x25519_pk: bytes,
        my_dh_mlkem: bytes,
    ) -> PairRatchet:
        """Initialize as Bob (receiver of first message)."""
        return cls()

    def encrypt(
        self,
        intent_header_bytes: bytes,
        body_bytes: bytes,
        session_id: bytes,
        include_dh_pub: bool = False,
    ) -> PairMessage:
        """Encrypt a message."""
        return PairMessage(header=b"", body=body_bytes)

    def derive_message_keys(self, header: bytes) -> tuple[bytes, bytes]:
        """Derive intent_key and message_key from header."""
        return (b"\x00" * 32, b"\x00" * 32)


# ---------------------------------------------------------------------------
# PolicyLayer
# ---------------------------------------------------------------------------


class PolicyLayer:
    """Policy layer for intent/message key split — SPEC-003 § L4."""

    def __init__(self) -> None:
        self._captokens: list[CapToken] = []
        self._staged: dict[int, bytes] = {}
        self._last_result: ValidationResult | None = None

    def add_captoken(self, info: CapToken) -> None:
        """Register a CapToken for validation."""
        self._captokens.append(info)

    def stage_body_key(self, ns: int, message_key: bytes) -> None:
        """Stage a body key under sequence number *ns*."""
        self._staged[ns] = message_key

    def validate(self, ns: int, intent: IntentHeader) -> ValidationResult:
        """Validate intent against captokens."""
        self._last_result = (
            ValidationResult.ALLOW if self._captokens else ValidationResult.DENY_NO_CAPTOKEN
        )
        return self._last_result

    def release(self, ns: int) -> bytes:
        """Release body key for sequence *ns*. Raises PermissionError if not ALLOW."""
        if self._last_result != ValidationResult.ALLOW:
            raise PermissionError(f"cannot release ns={ns}: {self._last_result}")
        return self._staged.get(ns, b"\x00" * 32)


# ---------------------------------------------------------------------------
# MlsGroup
# ---------------------------------------------------------------------------


class MlsGroup:
    """MLS PQ group session — SPEC-003 § L4."""

    def __init__(
        self,
        group_id: bytes,
        members: tuple[bytes, ...],
        ciphersuite: str = "MLS_PQ_X25519_MLKEM768_AES256GCM_SHA3_256",
    ) -> None:
        self.group_id = group_id

    def add_member(
        self,
        member: bytes,
        committer_id: bytes,
        new_envelope: bytes | None = None,
    ) -> None:
        """Add a member to the group."""

    def intent_key_root(self, sender_id: bytes) -> bytes:
        """Return intent key root for *sender_id*."""
        return b"\x00" * 32

    def message_key_root(self, sender_id: bytes) -> bytes:
        """Return message key root for *sender_id*."""
        return b"\x00" * 32
