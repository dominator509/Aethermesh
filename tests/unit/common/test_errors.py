"""Tests for aethermesh.common.errors — SPEC-006 per-layer taxonomies."""

import pytest

from aethermesh.common.errors import (
    TRANSLATIONS,
    AbortCode,
    HandshakeAbort,
    L4WireCode,
    PolicyDecision,
    VerificationDecision,
    translate_error,
)


class TestAbortCode:
    """L3 AbortCode per SPEC-006 § L3."""

    def test_all_codes_unique(self) -> None:
        values = list(AbortCode)
        assert len(values) == len({v.value for v in values})

    def test_handshake_abort_raises(self) -> None:
        exc = HandshakeAbort(AbortCode.REPLAY_DETECTED, "duplicate packet")
        assert exc.code == AbortCode.REPLAY_DETECTED
        assert "REPLAY_DETECTED" in str(exc)
        assert "duplicate packet" in str(exc)

    def test_handshake_abort_is_exception(self) -> None:
        with pytest.raises(HandshakeAbort):
            raise HandshakeAbort(AbortCode.INTERNAL_ERROR)

    def test_all_16_abort_codes_present(self) -> None:
        expected = {
            "BAD_VERSION",
            "UNKNOWN_SUITE",
            "DECRYPT_FAILED",
            "BAD_TRANSCRIPT",
            "ATTESTATION_INVALID",
            "ATTESTATION_REVOKED",
            "ATTESTATION_STALE",
            "ATTESTATION_PLATFORM_UNACCEPTABLE",
            "POLICY_DENIED",
            "POLICY_REJECTED",
            "DISCHARGE_MISSING",
            "DISCHARGE_INVALID",
            "CAPTOKEN_MALFORMED",
            "CAPTOKEN_CAVEAT_VIOLATION",
            "REPLAY_DETECTED",
            "INTERNAL_ERROR",
        }
        actual = {v.name for v in AbortCode}
        assert actual == expected


class TestL4WireCode:
    """L4 wire codes per SPEC-006 § L4 wire codes."""

    def test_all_codes_unique(self) -> None:
        values = list(L4WireCode)
        assert len(values) == len({v.value for v in values})

    def test_all_18_wire_codes_present(self) -> None:
        expected = {
            "BAD_HEADER",
            "UNKNOWN_DH_PUB",
            "SKIP_LIMIT_EXCEEDED",
            "REPLAY",
            "BAD_INTENT_AEAD",
            "INTENT_CANONICAL_VIOLATION",
            "CAPABILITY_UNKNOWN",
            "CAPABILITY_ROOT_MISMATCH",
            "SCOPE_VIOLATION",
            "BUDGET_EXCEEDED",
            "CAPTOKEN_MISSING_OR_REVOKED",
            "INTENT_PATH_INVALID",
            "EXPIRED",
            "BODY_AEAD_FAILED",
            "MLS_COMMIT_INVALID",
            "MEMBER_ATTESTATION_INVALID",
            "CAP_ENVELOPE_MISMATCH",
            "EPOCH_OUTDATED",
        }
        actual = {v.name for v in L4WireCode}
        assert actual == expected


class TestPolicyDecision:
    """L4 policy decisions per SPEC-006 § L4 policy."""

    def test_all_codes_unique(self) -> None:
        values = list(PolicyDecision)
        assert len(values) == len({v.value for v in values})

    def test_all_9_policy_decisions_present(self) -> None:
        expected = {
            "ALLOW",
            "DENY_SCOPE",
            "DENY_BUDGET",
            "DENY_EXPIRED",
            "DENY_UNKNOWN_CAP",
            "DENY_NO_CAPTOKEN",
            "PENDING_DISCHARGE",
            "DENY_SCHEMA_MISMATCH",
            "DENY_INTENT_PATH",
        }
        actual = {v.name for v in PolicyDecision}
        assert actual == expected


class TestVerificationDecision:
    """L5 verification decisions per SPEC-006 § L5."""

    def test_all_codes_unique(self) -> None:
        values = list(VerificationDecision)
        assert len(values) == len({v.value for v in values})

    def test_all_21_verification_decisions_present(self) -> None:
        expected = {
            "ALLOW",
            "DENY_ISSUER_SIG",
            "DENY_CHAIN",
            "DENY_REVOKED_EPOCH",
            "DENY_REVOKED_CTID",
            "DENY_UNKNOWN_CAVEAT",
            "DENY_TIME",
            "DENY_ACTION",
            "DENY_SCOPE",
            "DENY_BUDGET",
            "DENY_RATE",
            "DENY_SESSION_BINDING",
            "DENY_INSTANCE_BINDING",
            "DENY_ATTESTATION_BINDING",
            "DENY_PRINCIPAL_BINDING",
            "DENY_LANE",
            "DENY_INTENT_PATH",
            "DENY_POSTURE",
            "DENY_GEO",
            "PENDING_DISCHARGE",
            "DENY_DISCHARGE_INVALID",
        }
        actual = {v.name for v in VerificationDecision}
        assert actual == expected


class TestTranslations:
    """Cross-layer TRANSLATIONS per SPEC-006 § Cross-Layer Translation."""

    def test_translate_l3_replay_to_l4(self) -> None:
        target_layer, target_code = translate_error("L3", AbortCode.REPLAY_DETECTED)
        assert target_layer == "L4"
        assert target_code == L4WireCode.REPLAY

    def test_translate_l4_deny_scope_to_l5(self) -> None:
        target_layer, target_code = translate_error("L4", PolicyDecision.DENY_SCOPE)
        assert target_layer == "L5"
        assert target_code == VerificationDecision.DENY_SCOPE

    def test_translate_l5_revoked_epoch_to_l4(self) -> None:
        target_layer, target_code = translate_error("L5", VerificationDecision.DENY_REVOKED_EPOCH)
        assert target_layer == "L4"
        assert target_code == L4WireCode.CAPTOKEN_MISSING_OR_REVOKED

    def test_unknown_translation_raises_keyerror(self) -> None:
        with pytest.raises(KeyError, match="No translation"):
            translate_error("L1", 0xFFFF)

    def test_all_translations_valid(self) -> None:
        """Every entry in TRANSLATIONS is a valid (layer, code) pair."""
        valid_layers = {"L3", "L4", "L5"}
        for (src_layer, src_code), (tgt_layer, tgt_code) in TRANSLATIONS.items():
            assert src_layer in valid_layers
            assert tgt_layer in valid_layers
            assert isinstance(src_code, int)
            assert isinstance(tgt_code, int)
