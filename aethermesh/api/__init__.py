"""AetherMesh public API facade — SPEC-003.

All stable public symbols re-exported from a single import point.
Layers L3/L4/L5 are stub facades; bodies land in EP-006+ (EP-004 Decision Log D1).
"""

from aethermesh.common.errors import PolicyDecision as ValidationResult
from aethermesh.common.errors import VerificationDecision
from aethermesh.L3_handshake import (
    HandshakeInitiator,
    HandshakeResponder,
    PeerAttestationSummary,
    SessionState,
)
from aethermesh.L4_ratchet import (
    IntentHeader,
    MlsGroup,
    PairMessage,
    PairRatchet,
    PolicyLayer,
)
from aethermesh.L5_captokens import (
    AuditLog,
    AuditReceipt,
    CapToken,
    CapTokenVerifier,
    Caveat,
    Discharge,
    KeyringService,
    VerificationResult,
)

__all__ = [
    # L3
    "HandshakeInitiator",
    "HandshakeResponder",
    "SessionState",
    "PeerAttestationSummary",
    # L4
    "PairRatchet",
    "PairMessage",
    "PolicyLayer",
    "IntentHeader",
    "MlsGroup",
    "ValidationResult",
    # L5
    "CapToken",
    "Caveat",
    "CapTokenVerifier",
    "VerificationResult",
    "VerificationDecision",
    "Discharge",
    "KeyringService",
    "AuditLog",
    "AuditReceipt",
]
