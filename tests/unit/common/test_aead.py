"""Tests for aethermesh.common.aead — SPEC-001 § Required Behavior item 3."""

import pytest
from cryptography.exceptions import InvalidTag

from aethermesh.common.aead import AeadOpenError, aead_open, aead_seal

KEY = bytes(range(32))
NONCE = bytes(range(12))


class TestAeadSeal:
    def test_seal_returns_bytes(self) -> None:
        ct = aead_seal(KEY, NONCE, b"hello")
        assert isinstance(ct, bytes)

    def test_seal_appends_tag(self) -> None:
        ct = aead_seal(KEY, NONCE, b"hello")
        # Ciphertext = plaintext + 16-byte tag
        assert len(ct) == len(b"hello") + 16

    def test_empty_plaintext(self) -> None:
        ct = aead_seal(KEY, NONCE, b"")
        assert len(ct) == 16  # just the tag

    def test_seal_with_associated_data(self) -> None:
        ct = aead_seal(KEY, NONCE, b"data", ad=b"auth-data")
        assert len(ct) == len(b"data") + 16

    def test_seal_different_nonce_different_output(self) -> None:
        n1 = bytes(12)
        n2 = bytes([1] * 12)
        ct1 = aead_seal(KEY, n1, b"msg")
        ct2 = aead_seal(KEY, n2, b"msg")
        assert ct1 != ct2

    def test_seal_different_key_different_output(self) -> None:
        k1 = bytes(range(32))
        k2 = bytes([255 - b for b in k1])
        ct1 = aead_seal(k1, NONCE, b"msg")
        ct2 = aead_seal(k2, NONCE, b"msg")
        assert ct1 != ct2

    def test_bad_key_length(self) -> None:
        with pytest.raises(ValueError, match="key must be 32"):
            aead_seal(b"short", NONCE, b"msg")

    def test_bad_nonce_length(self) -> None:
        with pytest.raises(ValueError, match="nonce must be 12"):
            aead_seal(KEY, b"short", b"msg")


class TestAeadOpen:
    def test_roundtrip(self) -> None:
        for msg in [b"", b"a", b"hello world", bytes(range(256))]:
            ct = aead_seal(KEY, NONCE, msg)
            pt = aead_open(KEY, NONCE, ct)
            assert pt == msg

    def test_roundtrip_with_ad(self) -> None:
        ct = aead_seal(KEY, NONCE, b"secret", ad=b"header")
        pt = aead_open(KEY, NONCE, ct, ad=b"header")
        assert pt == b"secret"

    def test_wrong_ad_raises(self) -> None:
        ct = aead_seal(KEY, NONCE, b"secret", ad=b"correct")
        with pytest.raises(AeadOpenError):
            aead_open(KEY, NONCE, ct, ad=b"wrong")

    def test_wrong_key_raises(self) -> None:
        ct = aead_seal(KEY, NONCE, b"data")
        wrong_key = bytes([255 - b for b in KEY])
        with pytest.raises(AeadOpenError):
            aead_open(wrong_key, NONCE, ct)

    def test_wrong_nonce_raises(self) -> None:
        ct = aead_seal(KEY, NONCE, b"data")
        wrong_nonce = bytes([255 - b for b in NONCE])
        with pytest.raises(AeadOpenError):
            aead_open(KEY, wrong_nonce, ct)

    def test_corrupted_ciphertext_raises(self) -> None:
        ct = aead_seal(KEY, NONCE, b"data")
        corrupted = ct[:-1] + bytes([ct[-1] ^ 0xFF])
        with pytest.raises(AeadOpenError):
            aead_open(KEY, NONCE, corrupted)

    def test_corrupted_ciphertext_raises_invalid_tag(self) -> None:
        ct = aead_seal(KEY, NONCE, b"data")
        corrupted = ct[:-1] + bytes([ct[-1] ^ 0xFF])
        with pytest.raises(InvalidTag):
            aead_open(KEY, NONCE, corrupted)

    def test_truncated_ciphertext_raises(self) -> None:
        with pytest.raises(ValueError, match="ciphertext too short"):
            aead_open(KEY, NONCE, b"short")

    def test_bad_key_length(self) -> None:
        ct = aead_seal(KEY, NONCE, b"msg")
        with pytest.raises(ValueError, match="key must be 32"):
            aead_open(b"bad", NONCE, ct)

    def test_bad_nonce_length(self) -> None:
        ct = aead_seal(KEY, NONCE, b"msg")
        with pytest.raises(ValueError, match="nonce must be 12"):
            aead_open(KEY, b"bad_nonce__", ct)

    def test_tag_only_ciphertext(self) -> None:
        """Ciphertext exactly 16 bytes (just tag, zero plaintext)."""
        ct = aead_seal(KEY, NONCE, b"")
        pt = aead_open(KEY, NONCE, ct)
        assert pt == b""

    def test_large_message_roundtrip(self) -> None:
        msg = bytes(range(256)) * 8  # 2048 bytes (max Sphinx packet size)
        ct = aead_seal(KEY, NONCE, msg)
        pt = aead_open(KEY, NONCE, ct)
        assert pt == msg
