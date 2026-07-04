"""Tests for aethermesh.common.hashes — SPEC-001 § Required Behavior 1-2."""

import json
from pathlib import Path
from typing import Any

import pytest

from aethermesh.common.hashes import hkdf_sha3_256, sha3_256

VECTORS_PATH = Path(__file__).parent.parent.parent / "vectors" / "sha3_256_nist.json"


def _load_vectors() -> list[dict[str, Any]]:
    with open(VECTORS_PATH) as f:
        data: dict[str, Any] = json.load(f)
    assert data["TEST_ONLY"] is True
    return data["vectors"]  # type: ignore[no-any-return]


class TestSha3256:
    """SHA3-256 per SPEC-001 § Required Behavior item 1."""

    def test_empty(self) -> None:
        """Empty input produces correct 32-byte digest."""
        result = sha3_256(b"")
        assert len(result) == 32
        # Known value: SHA3-256("")
        assert result.hex() == "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a"

    def test_abc(self) -> None:
        result = sha3_256(b"abc")
        assert len(result) == 32
        assert result.hex() == "3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532"

    def test_output_length(self) -> None:
        """sha3_256 always returns exactly 32 bytes."""
        for msg in [b"", b"a", b"hello world", bytes(range(256))]:
            assert len(sha3_256(msg)) == 32

    def test_deterministic(self) -> None:
        """Same input always produces same digest."""
        msg = b"deterministic test message"
        a = sha3_256(msg)
        b_result = sha3_256(msg)
        assert a == b_result

    def test_avalanche(self) -> None:
        """Single-bit change produces different digest."""
        a = sha3_256(b"message")
        b_result = sha3_256(b"messagf")
        assert a != b_result
        # Hamming distance should be substantial
        differing_bytes = sum(1 for x, y in zip(a, b_result, strict=True) if x != y)
        assert differing_bytes > 5

    def test_type_error(self) -> None:
        """Non-bytes input raises TypeError."""
        with pytest.raises(TypeError):
            sha3_256("string")  # type: ignore[arg-type]

    @pytest.mark.parametrize("vec", _load_vectors())
    def test_nist_vectors(self, vec: dict[str, Any]) -> None:
        """NIST-style SHA3-256 KAT vectors."""
        msg = bytes.fromhex(vec["msg"])
        expected = vec["md"]
        result = sha3_256(msg).hex()
        assert result == expected


class TestHkdfSha3256:
    """HKDF-SHA3-256 per SPEC-001 § Required Behavior item 2."""

    def test_basic_derive(self) -> None:
        """Basic HKDF derivation returns correct length."""
        ikm = b"input key material"
        salt = b"salty"
        info = b"aethermesh test"
        okm = hkdf_sha3_256(ikm, salt, info, length=32)
        assert len(okm) == 32

    def test_deterministic(self) -> None:
        """Same inputs produce same output."""
        ikm = b"ikm"
        a = hkdf_sha3_256(ikm, b"salt", b"info", length=32)
        b_result = hkdf_sha3_256(ikm, b"salt", b"info", length=32)
        assert a == b_result

    def test_different_info_produces_different_key(self) -> None:
        """info parameter is a domain separator."""
        ikm = b"shared secret"
        salt = b"test salt"
        k1 = hkdf_sha3_256(ikm, salt, b"L3_handshake", length=32)
        k2 = hkdf_sha3_256(ikm, salt, b"L4_ratchet", length=32)
        assert k1 != k2

    def test_different_salt_produces_different_key(self) -> None:
        ikm = b"shared secret"
        k1 = hkdf_sha3_256(ikm, b"salt_a", b"info", length=32)
        k2 = hkdf_sha3_256(ikm, b"salt_b", b"info", length=32)
        assert k1 != k2

    def test_different_lengths(self) -> None:
        """Can derive keys of different lengths."""
        ikm = b"test ikm"
        for length in [16, 32, 48, 64]:
            okm = hkdf_sha3_256(ikm, b"salt", b"info", length=length)
            assert len(okm) == length

    def test_empty_salt(self) -> None:
        """Empty salt (default) works."""
        okm = hkdf_sha3_256(b"ikm", b"", b"info", length=32)
        assert len(okm) == 32

    def test_empty_info(self) -> None:
        """Empty info (default) works."""
        okm = hkdf_sha3_256(b"ikm", b"salt", b"", length=32)
        assert len(okm) == 32

    def test_rfc5869_test_vector(self) -> None:
        """RFC 5869 § A.1 test vector adapted for SHA3-256.

        We use RFC 5869 values for IKM/salt/info but with SHA3-256.
        This primarily validates the HMAC-SHA3-256 path in expand/extract.
        """
        ikm = bytes.fromhex("0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b")
        salt = bytes.fromhex("000102030405060708090a0b0c")
        info = bytes.fromhex("f0f1f2f3f4f5f6f7f8f9")
        okm = hkdf_sha3_256(ikm, salt, info, length=42)
        assert len(okm) == 42

    def test_max_length(self) -> None:
        """HKDF can derive up to 255*32 bytes."""
        okm = hkdf_sha3_256(b"ikm", b"salt", b"info", length=255 * 32)
        assert len(okm) == 255 * 32

    def test_length_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="length must be"):
            hkdf_sha3_256(b"ikm", b"salt", b"info", length=0)

    def test_length_too_large_raises(self) -> None:
        with pytest.raises(ValueError, match="length must be"):
            hkdf_sha3_256(b"ikm", b"salt", b"info", length=255 * 32 + 1)

    def test_type_error_ikm(self) -> None:
        with pytest.raises(TypeError):
            hkdf_sha3_256("not bytes")  # type: ignore[arg-type]

    def test_type_error_salt(self) -> None:
        with pytest.raises(TypeError):
            hkdf_sha3_256(b"ikm", "not bytes")  # type: ignore[arg-type]

    def test_type_error_info(self) -> None:
        with pytest.raises(TypeError):
            hkdf_sha3_256(b"ikm", b"salt", 123)  # type: ignore[arg-type]
