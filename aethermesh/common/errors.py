"""Error taxonomies and cross-layer translations.

SPEC-006 — Per-Layer Taxonomies and Cross-Layer Translation.
"""

from enum import IntEnum

# ====================================================================
# L3 — AbortCode (SPEC-006 § L3)
# ====================================================================


class AbortCode(IntEnum):
    BAD_VERSION = 0x10
    UNKNOWN_SUITE = 0x11
    DECRYPT_FAILED = 0x20
    BAD_TRANSCRIPT = 0x21
    ATTESTATION_INVALID = 0x30
    ATTESTATION_REVOKED = 0x31
    ATTESTATION_STALE = 0x32
    ATTESTATION_PLATFORM_UNACCEPTABLE = 0x33
    POLICY_DENIED = 0x40
    POLICY_REJECTED = 0x41
    DISCHARGE_MISSING = 0x42
    DISCHARGE_INVALID = 0x43
    CAPTOKEN_MALFORMED = 0x50
    CAPTOKEN_CAVEAT_VIOLATION = 0x51
    REPLAY_DETECTED = 0xF0
    INTERNAL_ERROR = 0xFF


class HandshakeAbort(Exception):  # noqa: N818
    """Raised by L3 handshake on abort. Name per SPEC-006 § L3."""

    def __init__(self, code: AbortCode, message: str = "") -> None:
        self.code = code
        self.message = message
        super().__init__(f"[{code.name}] {message}")


# ====================================================================
# L4 wire codes (SPEC-006 § L4 wire codes)
# ====================================================================


class L4WireCode(IntEnum):
    BAD_HEADER = 0x10
    UNKNOWN_DH_PUB = 0x11
    SKIP_LIMIT_EXCEEDED = 0x12
    REPLAY = 0x13
    BAD_INTENT_AEAD = 0x20
    INTENT_CANONICAL_VIOLATION = 0x21
    CAPABILITY_UNKNOWN = 0x22
    CAPABILITY_ROOT_MISMATCH = 0x23
    SCOPE_VIOLATION = 0x24
    BUDGET_EXCEEDED = 0x25
    CAPTOKEN_MISSING_OR_REVOKED = 0x26
    INTENT_PATH_INVALID = 0x27
    EXPIRED = 0x28
    BODY_AEAD_FAILED = 0x40
    MLS_COMMIT_INVALID = 0x50
    MEMBER_ATTESTATION_INVALID = 0x51
    CAP_ENVELOPE_MISMATCH = 0x52
    EPOCH_OUTDATED = 0x53


# ====================================================================
# L4 PolicyDecision (SPEC-006 § L4 policy)
# ====================================================================


class PolicyDecision(IntEnum):
    ALLOW = 0
    DENY_SCOPE = 1
    DENY_BUDGET = 2
    DENY_EXPIRED = 3
    DENY_UNKNOWN_CAP = 4
    DENY_NO_CAPTOKEN = 5
    PENDING_DISCHARGE = 6
    DENY_SCHEMA_MISMATCH = 7
    DENY_INTENT_PATH = 8


# ====================================================================
# L5 VerificationDecision (SPEC-006 § L5)
# ====================================================================


class VerificationDecision(IntEnum):
    ALLOW = 0
    DENY_ISSUER_SIG = 1
    DENY_CHAIN = 2
    DENY_REVOKED_EPOCH = 3
    DENY_REVOKED_CTID = 4
    DENY_UNKNOWN_CAVEAT = 5
    DENY_TIME = 6
    DENY_ACTION = 7
    DENY_SCOPE = 8
    DENY_BUDGET = 9
    DENY_RATE = 10
    DENY_SESSION_BINDING = 11
    DENY_INSTANCE_BINDING = 12
    DENY_ATTESTATION_BINDING = 13
    DENY_PRINCIPAL_BINDING = 14
    DENY_LANE = 15
    DENY_INTENT_PATH = 16
    DENY_POSTURE = 17
    DENY_GEO = 18
    PENDING_DISCHARGE = 19
    DENY_DISCHARGE_INVALID = 20


# ====================================================================
# Cross-layer TRANSLATIONS (SPEC-006 § Cross-Layer Translation)
# ====================================================================

# Map (source_layer, source_code) → (target_layer, target_decision)
# Each entry: (L3_AbortCode, L4_WireCode, L4_PolicyDecision, L5_VerificationDecision)
TRANSLATIONS: dict[tuple[str, int], tuple[str, int]] = {
    # L3 → L4
    ("L3", AbortCode.REPLAY_DETECTED): ("L4", L4WireCode.REPLAY),
    ("L3", AbortCode.POLICY_DENIED): ("L4", PolicyDecision.DENY_SCOPE),
    ("L3", AbortCode.POLICY_REJECTED): ("L4", PolicyDecision.DENY_SCOPE),
    ("L3", AbortCode.CAPTOKEN_MALFORMED): ("L4", PolicyDecision.DENY_NO_CAPTOKEN),
    ("L3", AbortCode.CAPTOKEN_CAVEAT_VIOLATION): ("L4", PolicyDecision.DENY_SCOPE),
    ("L3", AbortCode.DISCHARGE_MISSING): ("L4", PolicyDecision.PENDING_DISCHARGE),
    ("L3", AbortCode.DISCHARGE_INVALID): ("L5", VerificationDecision.DENY_DISCHARGE_INVALID),
    # L4 → L5
    ("L4", PolicyDecision.DENY_SCOPE): ("L5", VerificationDecision.DENY_SCOPE),
    ("L4", PolicyDecision.DENY_BUDGET): ("L5", VerificationDecision.DENY_BUDGET),
    ("L4", PolicyDecision.DENY_EXPIRED): ("L5", VerificationDecision.DENY_TIME),
    ("L4", PolicyDecision.DENY_NO_CAPTOKEN): ("L5", VerificationDecision.DENY_ISSUER_SIG),
    ("L4", PolicyDecision.PENDING_DISCHARGE): ("L5", VerificationDecision.PENDING_DISCHARGE),
    # L5 → L4
    ("L5", VerificationDecision.DENY_REVOKED_EPOCH): ("L4", L4WireCode.CAPTOKEN_MISSING_OR_REVOKED),
    ("L5", VerificationDecision.DENY_REVOKED_CTID): ("L4", L4WireCode.CAPTOKEN_MISSING_OR_REVOKED),
    ("L5", VerificationDecision.DENY_SCOPE): ("L4", L4WireCode.SCOPE_VIOLATION),
    ("L5", VerificationDecision.DENY_BUDGET): ("L4", L4WireCode.BUDGET_EXCEEDED),
    ("L5", VerificationDecision.PENDING_DISCHARGE): ("L4", PolicyDecision.PENDING_DISCHARGE),
}


def translate_error(source_layer: str, source_code: int) -> tuple[str, int]:
    """Translate an error code from *source_layer* to the receiving layer's taxonomy.

    Returns (target_layer, target_code).

    Raises:
        KeyError: If no translation is defined for this (layer, code) pair.
    """
    key = (source_layer, source_code)
    if key not in TRANSLATIONS:
        raise KeyError(f"No translation for ({source_layer}, 0x{source_code:02X})")
    return TRANSLATIONS[key]
