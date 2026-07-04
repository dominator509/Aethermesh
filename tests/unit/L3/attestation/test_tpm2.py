"""Tests for TPM2 attestation backend — EP-006 M1."""

import os
import shutil

import pytest

from aethermesh.L3_handshake.attestation.backends.tpm2 import (
    BACKEND_CODE,
    build_quote,
    verify_quote,
)

TEST_RUNTIME = b"\x00" * 32
TEST_CONFIG = b"\x11" * 32
TEST_PUBKEY = bytes(range(32))
TEST_SIGNING_KEY = b"\x22" * 32
TEST_NONCE = b"\x33" * 16
TEST_NOT_AFTER = 9999999999


@pytest.mark.skipif(
    os.name == "nt" or shutil.which("tpm2_pcrread") is None,
    reason="TPM2 tools not available on this host",
)
class TestTpm2Real:
    def test_build_quote_real(self) -> None:
        quote = build_quote(
            TEST_RUNTIME,
            TEST_CONFIG,
            TEST_PUBKEY,
            TEST_SIGNING_KEY,
            TEST_NOT_AFTER,
            TEST_NONCE,
        )
        assert quote.backend_code == BACKEND_CODE
        assert len(quote.hardware_quote) >= 32
        assert not quote.hardware_quote.startswith(b"TPM2_PLACEHOLDER")

    def test_verify_quote_real(self) -> None:
        quote = build_quote(
            TEST_RUNTIME,
            TEST_CONFIG,
            TEST_PUBKEY,
            TEST_SIGNING_KEY,
            TEST_NOT_AFTER,
            TEST_NONCE,
        )
        assert verify_quote(quote, TEST_NONCE) is True


class TestTpm2Placeholder:
    def test_build_quote_placeholder(self) -> None:
        """Placeholder quote builds on hosts without TPM2."""
        quote = build_quote(
            TEST_RUNTIME,
            TEST_CONFIG,
            TEST_PUBKEY,
            TEST_SIGNING_KEY,
            TEST_NOT_AFTER,
            TEST_NONCE,
        )
        assert quote.backend_code == BACKEND_CODE
        assert isinstance(quote.runtime_measurement, bytes)

    def test_verify_placeholder(self) -> None:
        quote = build_quote(
            TEST_RUNTIME,
            TEST_CONFIG,
            TEST_PUBKEY,
            TEST_SIGNING_KEY,
            TEST_NOT_AFTER,
            TEST_NONCE,
        )
        assert verify_quote(quote, TEST_NONCE) is True

    def test_verify_wrong_nonce(self) -> None:
        quote = build_quote(
            TEST_RUNTIME,
            TEST_CONFIG,
            TEST_PUBKEY,
            TEST_SIGNING_KEY,
            TEST_NOT_AFTER,
            TEST_NONCE,
        )
        assert verify_quote(quote, b"wrong-nonce-16!!") is False

    def test_verify_wrong_backend_code(self) -> None:
        quote = build_quote(
            TEST_RUNTIME,
            TEST_CONFIG,
            TEST_PUBKEY,
            TEST_SIGNING_KEY,
            TEST_NOT_AFTER,
            TEST_NONCE,
        )
        # Mutate backend_code (dataclass is frozen, make new one)
        from aethermesh.L3_handshake.attestation import AttestationQuote

        bad = AttestationQuote(
            runtime_measurement=quote.runtime_measurement,
            config_measurement=quote.config_measurement,
            instance_pubkey=quote.instance_pubkey,
            principal_binding=quote.principal_binding,
            not_after=quote.not_after,
            freshness_nonce=quote.freshness_nonce,
            hardware_quote=quote.hardware_quote,
            backend_code=99,
        )
        assert verify_quote(bad, TEST_NONCE) is False
